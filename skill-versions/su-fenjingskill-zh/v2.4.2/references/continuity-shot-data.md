# Continuity And Shot Data Contract

<!-- for skill-version: 2.4.2 / rule-revision: 2.4.2-source-lock-entry-guard-2026-07-07 -->

在拆分 Beat 前完整读取本文件。它只定义连续性台账、Beat/事实、状态迁移、`shot_data` JSON 结构和确定性校验接口；主流程、人工门禁、7 列表、运镜与 Prompt 规则分别以 `SKILL.md`、`camera-language.md`、`hybrid-shot-audit.md`、`seedance-prompt-rules.md` 为准。当前合同为稳定 7 列主表，不包含关键帧列。

## 连续性台账

为每个场景创建一项 `continuity_logs`，只保存该场景初始状态和跨场继承关系：

- `scene_id`：机器匹配键，格式建议 `S01`、`S02`，必须唯一；JSON 内一切场景引用使用该字段。
- `scene`：展示名，用于 Markdown/Excel 场景列，例如 `1 室外山林 日 外`。
- `first_shot_anchor_type`：只允许 `space | multi_character | both | single_continuation | subjective`。
- `spatial_axis`：主轴线、人物相对方向、入口/出口、越轴限制。
- `fixed_objects`：固定物名称、位置和状态。
- `characters`：角色名称、初始位置、朝向和状态。
- `props`：道具名称、位置、归属和状态。
- `sound_sources`：画内、画外声源及其空间来源。
- `reality_layer`：现实、回忆、梦境、灵魂、主观视角等现实层级。
- `inherits_from`：同空间跨场继承的父场景 `scene_id`，无继承时为空字符串。
- `inherited_states`：从父场景继承的字段路径列表。
- `diverged_states`：从父场景发散或重置的字段路径列表。

继承规则：显式 `inherits_from` 高于默认重置；未列入 `inherited_states` 的字段按新场景重置；同一字段不得同时出现在 `inherited_states` 与 `diverged_states`。台账不是不可变快照，后续镜头只能通过 `continuity_updates` 追加有证据的迁移，不得覆盖历史或让状态无镜头依据地跳变。

### 场景首镜锚定类型

- `space`：山林、道路、高速、山坳、神殿大厅、洞窟入口、广场、走廊等需要先建立地形、方向和固定物的场景。
- `multi_character`：同一场景首段出现 2 人及以上可见互动，包括室外群戏、室内多人对话、多人行动、多人对峙。
- `both`：同时需要空间锚定和多人站位锚定。
- `single_continuation`：单人独处、上一场已建立空间后的近距离情绪承接，或多人并非本场主要互动的承接镜。
- `subjective`：虚空、幻境、记忆、抽象主观场域。

类型为 `space`、`multi_character`、`both` 时，本场第一镜必须使用全景类景别：`大远景`、`大全景`、`全景`、`中全景`。多人场景首镜或前两镜必须覆盖人物站位事实，不允许先进入特写、道具特写或单人反应。类型为 `single_continuation` 或 `subjective` 时，首镜可以不是全景类，但仍必须交代空间边界、固定物方向或主观视觉锚点。

## Beat 与事实

### 2.4.2 源文锁定

`shot_data` 必须包含顶层 `script_lock`：

```json
{
  "status": "locked",
  "approved_script_path": "outputs/YYYY-MM-DD/docs/<片名>.approved_script.txt",
  "locked_text": "人类确认后的完整剧本文本",
  "locked_text_hash": "sha256(script_fragment_fingerprint(locked_text))",
  "approved_corrections": [
    {"from": "原始文本", "to": "批准后文本", "reason": "人工批准原因"}
  ]
}
```

`approved_script_path` 指向外部可读的批准后源文凭证文件，文件全文必须与 `locked_text` 一致。拆分 Beat 前、Gate A 前、Gate B 前和 Gate C 前必须复核：标题行、全部场景头、全部人物行和正文行均在 `locked_text` 中；不得只锁表格段落、摘要段落或局部正文。

`script_fragment_fingerprint` 的规则是去除全部空白后计算 SHA-256。`locked_text` 是唯一源文；Beat 与 Shot 不得手写摘要。每个 `beats[*].source_text` 与 `shots[*].source_paragraph` 必须通过 `source_span` 或 `source_spans` 指向 `locked_text` 的 0-based 字符区间：

```json
{"start": 0, "end": 18, "text_hash": "可选，span 文本的同规则 hash"}
```

校验器会从 `locked_text[start:end]` 回切文本并与 `source_text` / `source_paragraph` 对比；任何摘要、删字、改词、换序或缺少区间均为 FAIL。多段非连续原文使用 `source_spans`，按数组顺序用换行拼接。

1. Beat ID 使用 `B001` 格式，必须唯一、单调递增，允许空号；修改时禁止重编号既有 ID，新增 Beat 使用空号或更大的新号。
2. 为每个必须拍到的事实分配 `{Beat ID}-F{两位序号}`，例如 `B003-F02`；事实 ID 必须绑定所属 Beat。
3. 事实类型只使用：`character`、`action`、`dialogue`、`prop`、`space`、`position`、`emotion`、`sound`、`reality`。
4. 一个镜头可以覆盖一个或多个 Beat；一个 Beat 可以由多个镜头共同完成。
5. `dialogue` 事实的 `text` 只写需要逐字保留的对白原文，不含角色名前缀或说明。
6. `fact.text` 必须使用原文词汇或其直接指称，禁止写入视觉化翻译；情绪视觉化只允许出现在运镜主画面列。
7. `space_anchor_fact` 与 `blocking_anchor_fact` 可记录轴线、朝向、机位侧等制作补足，但必须标为 `[合理补足]` 的制作信息，不得新增剧情事实。
8. 每个事实 ID 必须至少出现在一个镜头的 `covered_fact_ids` 中，且该镜头必须绑定事实所属 Beat。
9. 不得用“已隐含”或“观众能理解”替代可拍事实。无法视觉化的事实必须在备注说明处理方式。
10. 不得机械一 Beat 一镜，也不得机械多 Beat 一镜；事实覆盖完整不等于分镜有效覆盖。

### 事实级切点字段

每个 fact 必须包含：

```json
{
  "fact_id": "B001-F01",
  "type": "action",
  "text": "必须拍到的事实",
  "cut_priority": "normal | recommended | must_isolate",
  "cut_reasons": ["causal_reveal"],
  "cut_group": "B001-causal-reveal",
  "cut_category": "space | prop | action | emotion | sound | reality | dialogue | vfx | character",
  "cut_moment_id": "B001-vfx-impact"
}
```

- `cut_priority`：`normal` 表示可随表演合并；`recommended` 表示建议独立或在镜内清楚突出；`must_isolate` 表示默认必须独立成镜。
- `cut_reasons`：复用 `shot.split_reason` 枚举；`recommended` 与 `must_isolate` 时必须非空，`normal` 时可为空数组。
- `cut_group`：兼容字段，2.4.2 不参与门禁判断。
- `cut_category`：只用于统计与审计，不作为 `must_isolate` 合并门禁。
- `cut_moment_id`：标记同一不可拆瞬间。
- 默认 `must_isolate`：真相首次落地、宿主/替身/惩罚/起源解释、VFX 不可逆变化、首次 VO/画外声源、现实层切换、重大情绪反转。
- 同镜合并多个 `must_isolate` 事实的唯一条件：同 Beat、同 `cut_moment_id`，且镜头备注写 `[不可拆说明]`。
- 单场 `must_isolate` Beat 占比超过 50% 时只触发 WARN，唯一处置路径是 Gate A 人工逐条裁决 `keep` 或降级；模型不得自行降级。

## 状态迁移

每条迁移包含：

```json
{
  "entity_type": "character | prop | fixed_object | reality_layer",
  "entity": "实体名称；reality_layer 使用空字符串",
  "field": "position | facing | state | owner | value",
  "from": "迁移前状态",
  "to": "迁移后状态",
  "evidence_fact_ids": ["B002-F01"]
}
```

- `from` 必须等于该实体当前状态，`to` 不得与 `from` 相同。
- 证据事实必须由当前镜头覆盖。
- 人物 `position` 或 `facing` 迁移时，运镜主画面必须出现 `【站位位移】`。
- 运镜主画面出现 `【站位位移】` 时，当前镜头必须登记对应位置或朝向迁移。
- 新场景默认重新建立初始状态；跨场继承只能通过 `inherits_from`、`inherited_states`、`diverged_states` 显式登记。
- 最小合理补足不得作为剧情状态迁移证据。无法从原文建立迁移时，保留旧状态并报告歧义。

迁移触发表固定如下：

| 变化类型 | continuity_update | 【站位位移】 |
| --- | --- | --- |
| 人物主动移动到新位置 | 是 | 是 |
| 人物被动位移（被拖走、击飞、摔倒等） | 是 | 是 |
| 人物朝向变化（位置不变） | 是 | 是 |
| 摄影机切换主体/景别，人物未动 | 否 | 否 |
| 新人物入场 / 人物退场 | 是 | 是 |
| 道具状态变化 | 是 | 否 |

校验器逐镜推进当前状态；`continuity_update.from` 必须等于上一状态，`to` 才会成为下一状态。

## shot_data 结构

保存 UTF-8 JSON，顶层结构固定：

```json
{
  "metadata": {
    "skill_name": "su-fenjingskill-zh",
    "version": "2.4.2",
    "rule_revision": "2.4.2-source-lock-entry-guard-2026-07-07",
    "title": "片名或集名",
    "reference_status": {
      "continuity-shot-data": "loaded | missing",
      "hybrid-shot-audit": "loaded | missing",
      "camera-language": "loaded | missing",
      "seedance-prompt-rules": "loaded | missing"
    },
    "reference_proof": {},
    "script_status": {
      "storyboard_delivery.py": "available | missing",
      "validate_storyboard.js": "available | missing"
    },
    "revision_log": []
  },
  "script_lock": {
    "status": "locked",
    "locked_text": "人类确认后的完整剧本文本",
    "locked_text_hash": "sha256",
    "approved_corrections": []
  },
  "batch_plan": null,
  "human_reviews": [],
  "warn_resolutions": [],
  "continuity_logs": [],
  "beats": [],
  "shots": [],
  "validation_report": {
    "status": "PASS | WARN | FAIL | NOT_RUN",
    "warnings": [],
    "errors": [],
    "source_json_hash": "由脚本计算；NOT_RUN 时为空字符串"
  }
}
```

### continuity_logs 示例

```json
{
  "scene_id": "S01",
  "scene": "1 室外山林 日 外",
  "first_shot_anchor_type": "both",
  "spatial_axis": "山路由画面左下通向右上，三人沿山路向岭上行进。",
  "fixed_objects": ["山路", "密林", "裂缝入口"],
  "characters": ["A在画面左前，B在中间，C在右后，三人面向岭上。"],
  "props": [],
  "sound_sources": [],
  "reality_layer": "现实",
  "inherits_from": "",
  "inherited_states": [],
  "diverged_states": []
}
```

### Beat 结构

```json
{
  "beat_id": "B001",
  "scene_id": "S01",
  "scene": "1 室外山林 日 外",
  "source_text": "原文",
  "source_span": {"start": 0, "end": 2, "text_hash": "可选"},
  "dramatic_function": "本 Beat 的叙事功能",
  "facts": [
    {"fact_id": "B001-F01", "type": "action", "text": "必须拍到的事实"}
  ]
}
```

### Shot 结构

```json
{
  "shot_no": 1,
  "scene_id": "S01",
  "scene": "1 室外山林 日 外",
  "beat_ids": ["B001"],
  "covered_fact_ids": ["B001-F01"],
  "source_paragraph": "原剧本段落",
  "source_span": {"start": 0, "end": 5, "text_hash": "可选"},
  "duration_seconds": 3,
  "duration_breakdown": {
    "sync_action_seconds": 2,
    "sync_dialogue_seconds": 0,
    "non_sync_action_seconds": 0,
    "emotional_pause_seconds": 1
  },
  "long_take": {"classification": "not_applicable | dialogue_long | action_long | spatial_long | emotional_long", "reason": "镜头不超过10秒"},
  "camera_main_image": "[视角, 景别, 运镜]\n【机位逻辑】...",
  "notes": "备注",
  "prompt": "精简五字段 Prompt，由 build 脚本派生",
  "visible_characters": [],
  "offscreen_characters": [],
  "visible_props": [],
  "continuity_updates": [],
  "shot_type": "master | action | dialogue | reaction | insert | transition | vfx_anchor | safety",
  "split_reason": ["spatial_anchor | performance_continuity | new_information | prop_state_change | new_vfx_state | new_sound_source | reality_layer_shift | causal_reveal | emotional_turn | continuity_migration"],
  "insert_priority": "none | recommended | must_have",
  "long_take_support": []
}
```

关键约束：

- `continuity_logs[*].scene_id` 必须唯一；`shots[*].scene_id` 与 `beats[*].scene_id` 必须匹配已登记场景。
- 每个镜头 `covered_fact_ids` 非空；唯一例外是 `shot_type == "safety"`、备注含 `[安全镜][人工批准]`，且 Gate B 明确批准无事实安全镜。
- `transition` 与 `safety` 镜默认也必须绑定空间、声音或现实层事实；无事实安全镜只能走上述人工批准例外。
- `duration_breakdown` 各分项为非负整数，`duration_seconds` 必须精确等于 `max(sync_action_seconds, sync_dialogue_seconds) + non_sync_action_seconds + emotional_pause_seconds`。
- 超过 10 秒的镜头必须至少两项 `long_take_support`，且 `long_take.classification` 不得为 `not_applicable`。
- `visible_characters` 与 `offscreen_characters` 不得重叠。
- 任何镜头包含 `keyframe` 字段都是失败项。
- `old_shot_no`、`PASS_INTERNAL`、`运镜修正`、`【镜内变化】` 属于过程痕迹，不得进入交付数据；`revision_log` 是唯一合法过程记录。

## 人工审核记录

每条 `human_reviews` 使用：

```json
{
  "gate": "GATE_0 | GATE_A | GATE_B | GATE_C",
  "round": 1,
  "status": "approved | rejected",
  "reviewer": "人工标识",
  "notes": "审核意见原文摘录"
}
```

2.4.2 预签发校验要求 Gate A / Gate B 均有 `approved` 记录；存在 `batch_plan` 时还要求 Gate 0。最终签发校验额外要求 Gate C `approved`。`NOT_RUN` 交付必须在 Gate C 记录 `accepted_without_validation`。2.4.2 还要求 `approved_script_path`、`script_lock` 与所有 Beat/Shot 源文区间校验通过。

## WARN 处置记录

每条 `warn_resolutions` 使用：

```json
{
  "warn_id": "稳定 WARN ID",
  "resolution": "keep | revise | accepted_without_change",
  "resolved_by": "human | auto_whitelist",
  "note": "处置说明"
}
```

每条 WARN 必须有处置记录。白名单 WARN 仅包括 reference missing、`[合理补足]`、节奏健康参考，可用 `auto_whitelist`；其他 WARN 必须由 `human` 处置。

## 校验状态

- `PASS`：结构、覆盖、连续性、时长、Prompt、Markdown 和 Excel 一致，且必需 Gate 记录完整。
- `WARN`：结构可交付但存在 WARN；所有 WARN 均有 `warn_resolutions` 后方可交付。
- `FAIL`：结构错误、表头不符、Beat/事实遗漏、时长错误、连续性断裂、可见性错误、Prompt 合同错误，或 JSON/Markdown/Excel 任意内容不一致。
- `NOT_RUN`：脚本或环境缺失时的唯一合法状态；`source_json_hash` 必须为空字符串，禁止伪造；须 Gate C 人工显式接受。

## 交付映射

交付脚本按以下顺序生成 7 列：

1. `shot_no`
2. `scene`
3. `beat_ids + source_paragraph`
4. `duration_seconds`
5. `camera_main_image`
6. `notes`
7. `prompt`

审计字段只存在于 JSON，不进入 Markdown/Excel 主表。Excel 可增加 `校验摘要` Sheet，Markdown 可附校验摘要，独立 `validation_report.json` 必须与 `shot_data.validation_report` 一致；这些都不得改变主表 7 列。Markdown、Excel 和 JSON 必须来自同一数据源，不得手动编辑 Markdown 或 Excel 来绕过 JSON 校验。
