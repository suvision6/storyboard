# Continuity And Shot Data Contract

在拆分 Beat 前完整读取本文件。它定义连续性台账、事实覆盖、`shot_data` 结构和确定性校验接口。

## Contents

- 连续性台账
- Beat 与事实
- 状态迁移
- shot_data 结构
- 校验状态
- 交付映射

## 连续性台账

为每个场景创建一项 `continuity_logs`，只保存该场景的初始状态：

- `scene`：必须与镜头场景完全一致。
- `spatial_axis`：主轴线、人物相对方向和越轴限制。
- `fixed_objects`：固定物名称、位置和状态。
- `characters`：角色名称、初始位置、朝向和状态。
- `props`：道具名称、位置、归属和状态。
- `sound_sources`：画内、画外声源及其空间来源。
- `reality_layer`：现实、回忆、梦境、灵魂或主观视角。

台账不是不可变快照。后续镜头只能通过 `continuity_updates` 追加有证据的迁移，不得覆盖历史或让状态无镜头依据地跳变。

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
- 运镜主画面出现 `【站位位移】` 时，当前镜头必须登记人物位置或朝向迁移。
- 新场景重新建立初始状态，不继承其他场景的位置；跨场景保持角色身份、服装和道具归属等剧情连续性。
- 最小合理补足不得作为剧情状态迁移证据。无法从原文建立迁移时，保留旧状态并报告歧义。

## shot_data 结构

保存 UTF-8 JSON，顶层结构固定：

```json
{
  "metadata": {
    "skill_name": "su-fenjingskill-zh",
    "version": "2.2.0",
    "title": "片名或集名",
    "reference_status": {
      "camera_language": "loaded | missing",
      "seedance_prompt_rules": "loaded | missing"
    }
  },
  "continuity_logs": [],
  "beats": [],
  "shots": [],
  "validation_report": {
    "status": "PASS | WARN | FAIL",
    "reference_missing": [],
    "warnings": [],
    "errors": []
  }
}
```

Beat 结构：

```json
{
  "beat_id": "B001",
  "scene": "13-1 赤狐岭迷雾深林 日 外",
  "source_text": "原文，不改写对白",
  "dramatic_function": "本节拍的信息或情绪功能",
  "facts": [
    {"fact_id": "B001-F01", "type": "action", "text": "必须拍到的原文事实"}
  ]
}
```

镜头结构：

```json
{
  "shot_no": 1,
  "scene": "13-1 赤狐岭迷雾深林 日 外",
  "beat_ids": ["B001"],
  "covered_fact_ids": ["B001-F01"],
  "source_paragraph": "不含 Beat 前缀的原剧本段落",
  "duration_seconds": 7,
  "duration_breakdown": {
    "sync_action_seconds": 4,
    "sync_dialogue_seconds": 0,
    "non_sync_action_seconds": 0,
    "emotional_pause_seconds": 3
  },
  "long_take": {"classification": "not_applicable", "reason": "镜头不超过10秒"},
  "camera_main_image": "三元组、机位逻辑、站位和画面",
  "notes": "备注",
  "prompt": "Seedance 五字段",
  "keyframe": "关键帧七字段",
  "visible_characters": [],
  "offscreen_characters": [],
  "visible_props": [],
  "continuity_updates": []
}
```

## 字段规则

- `metadata.version` 必须为 `2.2.0`；两个 reference 状态只能为 `loaded` 或 `missing`。
- `duration_seconds` 必须等于四项时长公式结果向上取整后的整数。
- `long_take.classification` 只允许 `continuous_performance`、`emotional_climax`、`not_applicable`。
- 超过 10 秒且分类为前两项时必须写 `[长镜头]`；分类为 `not_applicable` 时必须填写具体理由。
- `visible_characters`、`offscreen_characters` 不得重叠；关键帧不得出现画外人物。
- Prompt 中画外人物只允许出现在含该角色名和“画外声”的同一行。
- `validation_report` 由交付脚本更新，不要手工伪造 PASS。

## 校验状态

- `FAIL`：结构错误、表头不符、Beat/事实遗漏、时长错误、连续性断裂、可见性错误、Prompt/关键帧合同错误，或 JSON、Markdown、Excel 任意内容不一致。
- `WARN`：reference 缺失，或备注包含已明确说明的 `[合理补足]`。
- `PASS`：不存在错误或警告。

reference 缺失时允许使用主 Skill 内置最低规则继续，但必须记录具体文件并输出 `WARN`；不得声称已加载。

## 交付映射

交付脚本按以下映射生成 8 列：

1. `shot_no`
2. `scene`
3. 由 `beat_ids` 前缀和 `source_paragraph` 合成
4. `duration_seconds`
5. `camera_main_image`
6. `notes`
7. `prompt`
8. `keyframe`

Markdown 用 `<br>` 表示单元格内换行；Excel 使用真实换行。校验时统一换行和空白后逐格比较。Excel 只建立 `分镜表` Sheet，不添加连续性、报告或隐藏数据 Sheet。