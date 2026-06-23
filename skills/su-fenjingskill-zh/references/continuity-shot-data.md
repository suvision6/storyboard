# Continuity And Shot Data Contract

在拆分 Beat 前完整读取本文件。它定义连续性台账、事实覆盖、`shot_data` 结构和确定性校验接口。当前合同为稳定 7 列主表，不包含关键帧列。

## 连续性台账

为每个场景创建一项 `continuity_logs`，只保存该场景的初始状态：

- `scene`：必须与镜头场景完全一致。
- `first_shot_anchor_type`：场景首镜锚定类型，只允许 `space`、`multi_character`、`both`、`single_continuation`、`subjective`。
- `spatial_axis`：主轴线、人物相对方向和越轴限制。
- `fixed_objects`：固定物名称、位置和状态。
- `characters`：角色名称、初始位置、朝向和状态。
- `props`：道具名称、位置、归属和状态。
- `sound_sources`：画内、画外声源及其空间来源。
- `reality_layer`：现实、回忆、梦境、灵魂或主观视角。

台账不是不可变快照。后续镜头只能通过 `continuity_updates` 追加有证据的迁移，不得覆盖历史或让状态无镜头依据地跳变。

### 场景首镜锚定类型

- `space`：山林、道路、高速、山坳、神殿大厅、洞窟入口、广场、走廊等需要先建立地形、方向和固定物的场景。
- `multi_character`：同一场景首段出现 2 人及以上可见互动，包括室外群戏、室内多人对话、多人行动、多人对峙。
- `both`：同时需要空间锚定和多人站位锚定。
- `single_continuation`：单人独处、上一场已建立空间后的近距离情绪承接，或多人并非本场主要互动的承接镜。
- `subjective`：虚空、幻境、记忆、抽象主观场域。

类型为 `space`、`multi_character`、`both` 时，本场第一镜必须使用全景类景别：`大远景`、`大全景`、`全景`、`中全景`。多人场景首镜或前两镜必须覆盖人物站位事实，不允许先进入特写、道具特写或单人反应。类型为 `single_continuation` 或 `subjective` 时，首镜可以不是全景类，但仍必须交代空间边界、固定物方向或主观视觉锚点。

## Beat 与事实

1. 按可表演节拍分配连续唯一的 `B001` 格式 Beat ID。
2. 为每个必须拍到的事实分配 `{Beat ID}-F{两位序号}`，例如 `B003-F02`。
3. 事实类型只使用：`character`、`action`、`dialogue`、`prop`、`space`、`position`、`emotion`、`sound`、`reality`。
4. 一个镜头可以覆盖一个或多个连续 Beat；一个 Beat 可以由多个镜头共同完成。
5. `dialogue` 事实的 `text` 只写需要逐字保留的对白原文，不含角色名前缀或说明。
6. 每个事实 ID 必须至少出现在一个镜头的 `covered_fact_ids` 中，且该镜头必须绑定事实所属 Beat。
7. 不得用“已隐含”或“观众能理解”替代可拍事实。无法视觉化的事实必须在备注说明处理方式。

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
- 新场景重新建立初始状态，不继承其他场景的位置；跨场景保持角色身份、服装和道具归属等剧情连续性。
- 最小合理补足不得作为剧情状态迁移证据。无法从原文建立迁移时，保留旧状态并报告歧义。

## shot_data 结构

保存 UTF-8 JSON，顶层结构固定：

```json
{
  "metadata": {
    "skill_name": "su-fenjingskill-zh",
    "version": "2.3.0",
    "title": "片名或集名",
    "reference_status": {
      "continuity-shot-data": "loaded | missing",
      "camera-language": "loaded | missing",
      "seedance-prompt-rules": "loaded | missing"
    }
  },
  "continuity_logs": [],
  "beats": [],
  "shots": [],
  "validation_report": {
    "status": "PASS | WARN | FAIL",
    "warnings": [],
    "errors": []
  }
}
```

`continuity_logs` 示例：

```json
{
  "scene": "1 室外山林 日 外",
  "first_shot_anchor_type": "both",
  "spatial_axis": "山路由画面左下通向右上，三人沿山路向岭上行进。",
  "fixed_objects": ["山路", "密林", "裂缝入口"],
  "characters": ["A在画面左前，B在中间，C在右后，三人面向岭上。"],
  "props": [],
  "sound_sources": [],
  "reality_layer": "现实"
}
```

Beat 结构：

```json
{
  "beat_id": "B001",
  "scene": "场景编号 场景名",
  "source_text": "原文",
  "dramatic_function": "本 Beat 的叙事功能",
  "facts": [
    {"fact_id": "B001-F01", "type": "action", "text": "必须拍到的事实"}
  ]
}
```

Shot 结构：

```json
{
  "shot_no": 1,
  "scene": "场景编号 场景名",
  "beat_ids": ["B001"],
  "covered_fact_ids": ["B001-F01"],
  "source_paragraph": "原剧本段落",
  "duration_seconds": 3,
  "duration_breakdown": {
    "sync_action_seconds": 2,
    "sync_dialogue_seconds": 0,
    "non_sync_action_seconds": 0,
    "emotional_pause_seconds": 1
  },
  "long_take": {"classification": "not_applicable", "reason": "镜头不超过10秒"},
  "camera_main_image": "[视角, 景别, 运镜]\n【机位逻辑】...",
  "notes": "备注",
  "prompt": "精简五字段 Prompt，由 build 脚本派生",
  "visible_characters": [],
  "offscreen_characters": [],
  "visible_props": [],
  "continuity_updates": []
}
```

- `keyframe` 字段已移除，任何镜头包含 `keyframe` 都是失败项。
- `old_shot_no`、`PASS_INTERNAL`、`运镜修正`、`【镜内变化】` 属于过程痕迹，不得进入交付数据。
- `visible_characters`、`offscreen_characters` 不得重叠。
- Prompt 中画外人物只允许出现在含该角色名和“画外声”的同一行。

## 校验状态

- `PASS`：结构、覆盖、连续性、时长、Prompt、Markdown 和 Excel 一致。
- `WARN`：引用缺失或合理补足已标注，但不影响交付使用。
- `FAIL`：结构错误、表头不符、Beat/事实遗漏、时长错误、连续性断裂、可见性错误、Prompt 合同错误，或 JSON/Markdown/Excel 任意内容不一致。

## 交付映射

交付脚本按以下顺序生成 7 列：

1. `shot_no`
2. `scene`
3. `beat_ids + source_paragraph`
4. `duration_seconds`
5. `camera_main_image`
6. `notes`
7. `prompt`

Markdown、Excel 和 JSON 必须来自同一数据源。不得手动编辑 Markdown 或 Excel 来绕过 JSON 校验。
