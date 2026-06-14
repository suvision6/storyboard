#!/usr/bin/env node

const fs = require("fs");

const file = process.argv[2];
if (!file) {
  console.error("Usage: node skills/su-fenjingskill-zh/scripts/validate_storyboard.js <storyboard.md>");
  process.exit(2);
}

const text = fs.readFileSync(file, "utf8");
const lines = text.split(/\r?\n/);
const tableLines = lines.filter((line) => /^\|\s*/.test(line));

const forbidden = [
  "令人叹为观止",
  "令人惊叹",
  "令人着迷",
  "精心打造",
  "匠心独运",
  "独具匠心",
  "视觉盛宴",
  "光影交响",
  "完美呈现",
  "极致体验",
  "引人入胜",
  "震撼人心",
  "巧妙融合",
  "仿佛",
  "犹如",
  "宛如",
  "好似",
];

const movementTerms = [
  "固定",
  "推进",
  "推轨",
  "拉远",
  "拉出",
  "横摇",
  "纵摇",
  "摇臂",
  "跟拍",
  "跟随",
  "环绕",
  "手持",
  "甩镜头",
  "升降",
  "变焦",
];

const unsupportedScriptMarkers = [
  "承上镜动作",
  "承上镜",
  "补充镜头",
  "新增镜头",
  "新增过渡",
  "无原文依据",
  "非原文",
  "原文未写",
  "自行添加",
  "自行补充",
  "为了过渡",
  "建议保留此镜",
];

function splitRow(line) {
  return line
    .replace(/^\|/, "")
    .replace(/\|$/, "")
    .split("|")
    .map((cell) => cell.trim());
}

function isSeparator(cells) {
  return cells.every((cell) => /^:?-{3,}:?$/.test(cell));
}

function cellLines(textValue) {
  return textValue
    .replace(/<br\s*\/?>/gi, "\n")
    .split(/\n/)
    .map((line) => line.trim())
    .filter(Boolean);
}

function firstLineStarting(textValue, prefix) {
  return cellLines(textValue).find((line) => line.startsWith(prefix));
}

function indexOfField(textValue, field) {
  return textValue.indexOf(field);
}

function normalizeOriginal(textValue) {
  return String(textValue || "")
    .replace(/<br\s*\/?>/gi, "")
    .replace(/\s+/g, "")
    .replace(/[。；;，,：:、]/g, "")
    .trim();
}

function hasLowInformationReaction(textValue) {
  const value = String(textValue || "").replace(/<br\s*\/?>/gi, "");
  const weakTerms = ["沉默", "看着", "望着", "停住", "没有出声", "保持不动", "静止"];
  const infoTerms = [
    "眼眶",
    "眼泪",
    "嘴唇",
    "发抖",
    "回头",
    "转身",
    "走",
    "拿",
    "放",
    "关",
    "推",
    "光",
    "手环",
    "裂痕",
    "相册",
    "照片",
    "梳子",
    "门",
    "车",
    "鸟",
    "光柱",
    "路牌",
  ];
  return weakTerms.some((term) => value.includes(term)) && !infoTerms.some((term) => value.includes(term));
}

function parseExplicitHiddenItems(cameraLines) {
  const textValue = cameraLines.join("\n");
  const matches = [...textValue.matchAll(/(?:不入画|画外|画面外)[:：]([^。\n；;]+)/g)];
  return matches
    .flatMap((match) => match[1].split(/[、,，\/\s]+/))
    .map((item) => item.trim())
    .filter((item) => item && !/^(无|没有|空|暂无)$/.test(item));
}

function spokenCharCount(textValue) {
  const matches = [...String(textValue || "").matchAll(/["“]([^"”]+)["”]/g)];
  return matches
    .map((match) => match[1].replace(/\s+/g, ""))
    .reduce((sum, value) => sum + value.length, 0);
}

function hasDurationEstimate(note) {
  const value = String(note || "");
  return (
    value.includes("[时长估算]") &&
    /动作\s*\d+(?:\.\d+)?\s*秒/.test(value) &&
    /台词\s*\d+(?:\.\d+)?\s*秒/.test(value) &&
    /情绪留白\s*\d+(?:\.\d+)?\s*秒/.test(value)
  );
}

function findUnsupportedScriptMarkers(textValue) {
  const value = String(textValue || "");
  return unsupportedScriptMarkers.filter((marker) => value.includes(marker));
}

const headerIndex = tableLines.findIndex((line) => {
  const cells = splitRow(line);
  return cells.length === 8 && cells[0] === "镜号" && cells[6] === "Prompt";
});

const errors = [];
const warnings = [];

if (headerIndex === -1) {
  errors.push("未找到 8 列分镜表表头。");
} else {
  const dataLines = tableLines.slice(headerIndex + 1).filter((line) => {
    const cells = splitRow(line);
    return cells.length === 8 && !isSeparator(cells) && /^\d+$/.test(cells[0]);
  });

  let expectedShot = 1;
  const sceneFirstSeen = new Set();
  let hook = false;
  let conflict = false;
  let surprise = false;
  let cliffhanger = false;
  let previousOriginal = "";
  let previousShotRaw = "";

  for (const line of dataLines) {
    const cells = splitRow(line);
    const [shotRaw, scene, original, durationRaw, camera, note, prompt, storyboard] = cells;
    const shot = Number(shotRaw);
    const duration = Number(durationRaw);

    if (shot !== expectedShot) {
      errors.push(`镜号不连续：期望 ${expectedShot}，实际 ${shotRaw}。`);
      expectedShot = shot + 1;
    } else {
      expectedShot += 1;
    }

    if (!scene) errors.push(`镜号${shotRaw}：场景为空。`);
    if (!original) errors.push(`镜号${shotRaw}：原剧本段落为空。`);
    const unsupportedMarkers = findUnsupportedScriptMarkers(`${original}\n${camera}\n${note}\n${prompt}\n${storyboard}`);
    if (unsupportedMarkers.length) {
      errors.push(`镜号${shotRaw}：疑似加入无原文依据内容或用非原文占位替代原文：${unsupportedMarkers.join("、")}。`);
    }

    const normalizedOriginal = normalizeOriginal(original);
    if (normalizedOriginal && normalizedOriginal === previousOriginal && !note.includes("重复原文必要")) {
      errors.push(`镜号${previousShotRaw}-${shotRaw}：连续重复同一原剧本段落，疑似把同一 beat 机械拆碎。若确有必要，请在备注写 [重复原文必要]。`);
    }
    previousOriginal = normalizedOriginal;
    previousShotRaw = shotRaw;

    if (!Number.isFinite(duration) || duration <= 0) {
      errors.push(`镜号${shotRaw}：镜头时长不是正数。`);
    } else {
      if (duration > 6 && !hasDurationEstimate(note)) {
        errors.push(`镜号${shotRaw}：超过6秒的镜头必须在备注写 [时长估算] 动作X秒 + 台词X秒 + 情绪留白X秒。`);
      }
      if (duration > 10 && !note.includes("[长镜头]")) {
        errors.push(`镜号${shotRaw}：超过10秒的镜头必须在备注写 [长镜头]。`);
      }
      const chars = spokenCharCount(`${original}\n${camera}`);
      const minDialogueSeconds = chars / 6;
      if (chars >= 12 && duration < Math.ceil(minDialogueSeconds)) {
        warnings.push(`镜号${shotRaw}：台词约${chars}字但时长${duration}秒，可能低于急促语速估算。`);
      }
    }

    const cameraLines = cellLines(camera);
    const triadPattern = /^\[[^,\]]+,\s*[^,\]]+,\s*[^\]]+\]$/;
    if (!cameraLines.length || !triadPattern.test(cameraLines[0])) {
      errors.push(`镜号${shotRaw}：运镜列第一行必须单独是 [角度, 景别, 运镜] 三元组。`);
    }
    if (cameraLines.length < 2) {
      errors.push(`镜号${shotRaw}：运镜列缺少三元组之后的机位逻辑。`);
    }

    const cameraLogicLine = cameraLines[1] || "";
    if (!cameraLogicLine.startsWith("【机位逻辑】")) {
      errors.push(`镜号${shotRaw}：运镜列第二行必须以【机位逻辑】开头。`);
    }

    const explicitHiddenItems = parseExplicitHiddenItems(cameraLines);

    if (!sceneFirstSeen.has(scene)) {
      sceneFirstSeen.add(scene);
      if (!cameraLines.slice(1).join("\n").includes("【场景首镜站位】")) {
        errors.push(`镜号${shotRaw}：场景首镜缺少【场景首镜站位】。`);
      }
    }

    for (const field of ["时间：", "景别：", "构图：", "运镜手法：", "画面内容："]) {
      if (!prompt.includes(field)) {
        errors.push(`镜号${shotRaw}：Prompt 缺少 ${field}`);
      }
    }

    const shotSizeLine = firstLineStarting(prompt, "景别：");
    if (shotSizeLine) {
      const value = shotSizeLine.replace(/^景别：/, "");
      if (/[，,]/.test(value) || movementTerms.some((term) => value.includes(term))) {
        errors.push(`镜号${shotRaw}：Prompt 景别疑似混入构图或运镜：${shotSizeLine}`);
      }
    }

    const timeMatches = [...prompt.matchAll(/时间：\s*(\d+)秒\s*-\s*(\d+)秒/g)];
    if (!timeMatches.length) {
      errors.push(`镜号${shotRaw}：Prompt 时间格式不可解析。`);
    }
    for (const match of timeMatches) {
      const start = Number(match[1]);
      const end = Number(match[2]);
      if (end <= start) errors.push(`镜号${shotRaw}：Prompt 时间倒退或为0。`);
      if (end - start > 15) errors.push(`镜号${shotRaw}：Prompt 单片段超过15秒。`);
    }

    const storyboardText = cellLines(storyboard).join("\n");
    if (!storyboardText || /待补|同上|参考前/.test(storyboardText)) {
      errors.push(`镜号${shotRaw}：故事板列为空或不可执行。`);
    }
    if (storyboardText.includes("AI生图提示词")) {
      errors.push(`镜号${shotRaw}：故事板列不得使用 AI生图提示词 标题。`);
    }
    const storyboardFields = ["场景：", "主体：", "画面：", "构图/景别：", "光影/色调：", "风格：", "禁止："];
    for (const field of storyboardFields) {
      if (!storyboardText.includes(field)) {
        errors.push(`镜号${shotRaw}：故事板列缺少 ${field}`);
      }
    }
    for (let i = 1; i < storyboardFields.length; i += 1) {
      const previous = indexOfField(storyboardText, storyboardFields[i - 1]);
      const current = indexOfField(storyboardText, storyboardFields[i]);
      if (previous !== -1 && current !== -1 && current < previous) {
        errors.push(`镜号${shotRaw}：故事板列字段顺序错误，${storyboardFields[i]} 不应早于 ${storyboardFields[i - 1]}。`);
      }
    }
    if (!storyboardText.includes("严格杜绝低分辨率，模糊，光影错位，比例不合理，杜绝任何cg游戏感")) {
      errors.push(`镜号${shotRaw}：故事板列禁止项缺少低分辨率/模糊/cg游戏感禁令。`);
    }
    if (/宫格图|站位图|九宫格|六宫格|四宫格|表后详稿|→\s*场景/.test(storyboardText)) {
      errors.push(`镜号${shotRaw}：故事板列疑似仍使用旧场景级宫格/站位图格式。`);
    }
    if (hasLowInformationReaction(original) && hasLowInformationReaction(camera)) {
      warnings.push(`镜号${shotRaw}：疑似低信息空反应镜，请确认是否应与前后动作/台词合并。`);
    }

    for (const item of explicitHiddenItems) {
      if (prompt.includes(item)) {
        errors.push(`镜号${shotRaw}：Prompt 写入了明确标为不入画/画外的内容：${item}`);
      }
      if (storyboardText.includes(item)) {
        errors.push(`镜号${shotRaw}：故事板列写入了明确标为不入画/画外的内容：${item}`);
      }
    }

    hook ||= note.includes("前5秒钩子");
    conflict ||= note.includes("前60秒冲突");
    surprise ||= note.includes("前120秒超预期");
    cliffhanger ||= note.includes("结尾15秒悬念点");
  }

  if (dataLines.length === 0) errors.push("没有找到镜头数据行。");
  if (!hook) warnings.push("未检测到 [前5秒钩子] 标记。");
  if (!conflict) warnings.push("未检测到 [前60秒冲突] 标记。");
  if (!surprise) warnings.push("未检测到 [前120秒超预期] 标记。");
  if (!cliffhanger) warnings.push("未检测到 [结尾15秒悬念点] 标记。");
}

for (const word of forbidden) {
  if (text.includes(word)) {
    errors.push(`检测到禁用表达：${word}`);
  }
}

if (warnings.length) {
  console.log("WARNINGS:");
  for (const warning of warnings) console.log(`- ${warning}`);
}

if (errors.length) {
  console.error("ERRORS:");
  for (const error of errors) console.error(`- ${error}`);
  process.exit(1);
}

console.log("OK: storyboard validation passed.");
