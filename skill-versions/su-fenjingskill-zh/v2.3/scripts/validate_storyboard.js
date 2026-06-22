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

const defaultMovementTerms = ["固定", "推进", "缓慢推进"];

const requiredCutPointCategories = [
  {
    name: "发言权转移",
    patterns: [/[\u4e00-\u9fa5A-Za-z0-9·]{1,8}[：:]/g],
    countMatches: true,
  },
  {
    name: "问答关系变化",
    patterns: [/问|回答|回应|反问|你们不会|是不是|为什么|什么|吗|？|\?/],
  },
  {
    name: "角色明显反应",
    patterns: [/一怔|脸色|眼眶|嘴唇|冷笑|大笑|慌|痛苦|不可思议|回头|低头|抬头|摇头|点头|踉跄|绷|僵|停住/],
  },
  {
    name: "道具状态变化",
    patterns: [/手环|短棍|长棍|磁卡|刷卡器|魂钉|裂痕|项链|绿灯|显示|亮起|暗下|恢复|变长|延伸|变成|熄灭/],
  },
  {
    name: "攻击发起命中结果",
    patterns: [/抬手|挥|扑|冲|拽|拦|扫|斩|震|炸|击|挡|断裂|碎裂|灰飞烟灭|跳入/],
  },
  {
    name: "空间方向改变",
    patterns: [/东侧|西侧|南侧|中央|高台|祭池边|走向|走到|冲向|转身|回到|两侧|不同方向|分头/],
  },
  {
    name: "层级切换",
    patterns: [/切回|切——|梦境|现实|闪回|脑海|灵魂|亡魂|残魂|画外声|VO/],
  },
  {
    name: "阵法状态变化",
    patterns: [/阵眼|破阵|续阵|阵破|符文|祭池|锁魂柱|柱身|黑纹|管道|雾气|龙卷|漩涡|回收|膨胀/],
  },
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

function hasLongShotReason(note) {
  return String(note || "").includes("[保留理由]");
}

function hasUncuttableExplanation(note) {
  return String(note || "").includes("[不可拆说明]");
}

function findRequiredCutPointCategories(textValue) {
  const value = String(textValue || "");
  const found = [];
  for (const category of requiredCutPointCategories) {
    if (category.countMatches) {
      const count = category.patterns
        .map((pattern) => [...value.matchAll(pattern)].length)
        .reduce((sum, item) => sum + item, 0);
      if (count >= 2) found.push(category.name);
      continue;
    }
    if (category.patterns.some((pattern) => pattern.test(value))) {
      found.push(category.name);
    }
  }
  return found;
}

function findUnsupportedScriptMarkers(textValue) {
  const value = String(textValue || "");
  return unsupportedScriptMarkers.filter((marker) => value.includes(marker));
}

function parseTriad(line) {
  const match = String(line || "").match(/^\[([^,\]]+),\s*([^,\]]+),\s*([^\]]+)\]$/);
  if (!match) return null;
  return {
    raw: `[${match[1].trim()}, ${match[2].trim()}, ${match[3].trim()}]`,
    angle: match[1].trim(),
    shotSize: match[2].trim(),
    movement: match[3].trim(),
  };
}

function extractSpeakers(textValue) {
  const value = String(textValue || "").replace(/<br\s*\/?>/gi, "\n");
  const matches = [...value.matchAll(/(?:^|\n|[。；;，,])\s*([\u4e00-\u9fa5A-Za-z0-9·]{1,8})[：:]/g)];
  const forbiddenLabels = new Set(["时间", "景别", "构图", "运镜手法", "画面内容", "场景", "主体", "画面", "风格", "禁止"]);
  return matches
    .map((match) => match[1].trim())
    .filter((name) => name && !forbiddenLabels.has(name));
}

function hasDialogue(textValue) {
  const value = String(textValue || "");
  return /["“][^"”]{2,}["”]/.test(value) || extractSpeakers(value).length > 0;
}

function hasDistanceAndOrientation(textValue) {
  const value = String(textValue || "");
  const hasDistance = /相距|距离|半步|一步|两步|三步|四步|五步|\d+\s*米|[一二三四五六七八九十]+米/.test(value);
  const hasOrientation = /面向|朝向|看向|背对|侧身|正对|转向|视线/.test(value);
  return hasDistance && hasOrientation;
}

function isSingleCloseShot(shotSize) {
  const value = String(shotSize || "");
  if (/双人|三人|群像|全景|远景|大远景/.test(value)) return false;
  return /单人|纯净|带关系|近景|中近景|中特写|特写/.test(value);
}

function indicatesPositionChange(textValue) {
  return /走到|走向|靠近|后退|退到|冲到|来到|绕到|穿过|进入|离开|站到|移到|跨到/.test(String(textValue || ""));
}

function getSceneStats(map, scene) {
  if (!map.has(scene)) {
    map.set(scene, {
      shots: 0,
      eyeLevel: 0,
      defaultMovement: 0,
      triadCounts: new Map(),
      movementCounts: new Map(),
      speakers: new Set(),
      hasDialogue: false,
      soloCloseShots: 0,
      totalDuration: 0,
      range7to8: 0,
      range9to11: 0,
      range12plus: 0,
    });
  }
  return map.get(scene);
}

function incrementCount(map, key) {
  map.set(key, (map.get(key) || 0) + 1);
}

function mostCommonShare(map, total) {
  if (!total) return null;
  let best = null;
  for (const [name, count] of map.entries()) {
    if (!best || count > best.count) best = { name, count };
  }
  if (!best) return null;
  return { ...best, share: best.count / total };
}

const headerIndex = tableLines.findIndex((line) => {
  const cells = splitRow(line);
  return cells.length === 8 && cells[0] === "镜号" && cells[6] === "Prompt";
});

const errors = [];
const warnings = [];
const infoMessages = [];

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
  let previousScene = "";
  let previousTriadRaw = "";
  let previousTriadShotRaw = "";
  const sceneStats = new Map();
  const durationStats = {
    shots: 0,
    total: 0,
    range7to8: 0,
    range9to11: 0,
    range12plus: 0,
  };

  for (const line of dataLines) {
    const cells = splitRow(line);
    const [shotRaw, scene, original, durationRaw, camera, note, prompt, storyboard] = cells;
    const shot = Number(shotRaw);
    const duration = Number(durationRaw);
    const stats = getSceneStats(sceneStats, scene);

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
      durationStats.shots += 1;
      durationStats.total += duration;
      stats.totalDuration += duration;
      if (duration >= 7 && duration <= 8) {
        durationStats.range7to8 += 1;
        stats.range7to8 += 1;
      }
      if (duration >= 9 && duration <= 11) {
        durationStats.range9to11 += 1;
        stats.range9to11 += 1;
      }
      if (duration >= 12) {
        durationStats.range12plus += 1;
        stats.range12plus += 1;
      }
      if (duration > 6 && !hasDurationEstimate(note)) {
        errors.push(`镜号${shotRaw}：超过6秒的镜头必须在备注写 [时长估算] 动作X秒 + 台词X秒 + 情绪留白X秒。`);
      }
      if (duration >= 9 && duration <= 11 && (!note.includes("[长镜头]") || !hasLongShotReason(note))) {
        errors.push(`镜号${shotRaw}：9-11秒高风险长镜头必须拆分，若保留必须在备注写 [长镜头] 和 [保留理由]。`);
      }
      if (
        duration >= 12 &&
        (!note.includes("[长镜头]") || !hasLongShotReason(note) || !hasUncuttableExplanation(note))
      ) {
        errors.push(`镜号${shotRaw}：12秒及以上默认不合格；若保留必须在备注写 [长镜头]、[保留理由] 和 [不可拆说明]。`);
      }
      if (duration >= 9) {
        const cutPoints = findRequiredCutPointCategories(`${original}\n${camera}`);
        if (cutPoints.length >= 2) {
          warnings.push(`镜号${shotRaw}：${duration}秒长镜头包含多个必须拆出的切点（${cutPoints.join("、")}），请优先重新拆分。`);
        }
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

    const triad = parseTriad(cameraLines[0] || "");
    stats.shots += 1;
    if (triad) {
      incrementCount(stats.triadCounts, triad.raw);
      incrementCount(stats.movementCounts, triad.movement);
      if (/^平视$|平视/.test(triad.angle)) stats.eyeLevel += 1;
      if (defaultMovementTerms.some((term) => triad.movement.includes(term))) stats.defaultMovement += 1;
      if (isSingleCloseShot(triad.shotSize)) stats.soloCloseShots += 1;
      if (previousScene === scene && previousTriadRaw === triad.raw) {
        warnings.push(`镜号${previousTriadShotRaw}-${shotRaw}：相邻镜头使用同一三元组 ${triad.raw}，请确认不是机械重复。`);
      }
    }
    if (/双人/.test(camera) && !hasDistanceAndOrientation(camera)) {
      warnings.push(`镜号${shotRaw}：双人同框疑似缺少距离或朝向描述，应写清两人的空间距离、朝向和画面关系。`);
    }
    if (indicatesPositionChange(`${original}\n${camera}`) && !camera.includes("【站位位移】")) {
      warnings.push(`镜号${shotRaw}：检测到角色位置变化，但运镜列未写【站位位移】，请确认行动路线是否连续。`);
    }
    for (const speaker of extractSpeakers(original)) stats.speakers.add(speaker);
    stats.hasDialogue ||= hasDialogue(original);
    previousScene = scene;
    previousTriadRaw = triad ? triad.raw : "";
    previousTriadShotRaw = shotRaw;

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
  if (durationStats.shots) {
    const avg = (durationStats.total / durationStats.shots).toFixed(2);
    infoMessages.push(
      `时长统计：镜头${durationStats.shots}个，平均${avg}秒，7-8秒${durationStats.range7to8}个，9-11秒${durationStats.range9to11}个，12秒及以上${durationStats.range12plus}个。`
    );
  }
  for (const [scene, stats] of sceneStats.entries()) {
    if (stats.shots) {
      const sceneAvg = (stats.totalDuration / stats.shots).toFixed(2);
      infoMessages.push(
        `场景${scene}：平均${sceneAvg}秒，7-8秒${stats.range7to8}个，9-11秒${stats.range9to11}个，12秒及以上${stats.range12plus}个。`
      );
    }
    if (stats.shots >= 4) {
      const triadDominance = mostCommonShare(stats.triadCounts, stats.shots);
      const movementDominance = mostCommonShare(stats.movementCounts, stats.shots);
      if (triadDominance && triadDominance.share >= 0.5) {
        warnings.push(`场景${scene}：三元组 ${triadDominance.name} 出现 ${triadDominance.count}/${stats.shots}，镜头设计可能过于重复。`);
      }
      if (movementDominance && movementDominance.share >= 0.55) {
        warnings.push(`场景${scene}：运镜 ${movementDominance.name} 出现 ${movementDominance.count}/${stats.shots}，请确认不是固定/推进默认化。`);
      }
      if (stats.eyeLevel / stats.shots >= 0.65) {
        warnings.push(`场景${scene}：平视镜头占比 ${stats.eyeLevel}/${stats.shots}，请确认角度选择都有信息增量。`);
      }
      if (stats.defaultMovement / stats.shots >= 0.65) {
        warnings.push(`场景${scene}：固定/推进类运镜占比 ${stats.defaultMovement}/${stats.shots}，请确认没有机械堆叠。`);
      }
    }
    if (stats.hasDialogue && stats.speakers.size >= 3 && stats.soloCloseShots < stats.speakers.size) {
      warnings.push(`场景${scene}：多人对话检测到 ${stats.speakers.size} 个发言角色，但单人近景/中近景约 ${stats.soloCloseShots} 个，请确认关键角色都有独立反应镜头。`);
    }
  }
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

if (infoMessages.length) {
  console.log("STATS:");
  for (const message of infoMessages) console.log(`- ${message}`);
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
