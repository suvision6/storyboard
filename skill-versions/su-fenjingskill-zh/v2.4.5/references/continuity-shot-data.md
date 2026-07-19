# Continuity And Shot Data Contract

<!-- for skill-version: 2.4.5 / rule-revision: 2.4.5-director-shot-integrity-guard-2026-07-18 -->

在拆分 Beat 前完整读取本文件。它只定义连续性台账、Beat/事实、状态迁移、`shot_data` JSON 结构和确定性校验接口；主流程、人工门禁、7 列表、运镜与 Prompt 规则分别以 `SKILL.md`、`camera-language.md`、`hybrid-shot-audit.md`、`seedance-prompt-rules.md` 为准。当前合同为稳定 7 列主表，不包含关键帧列。

## 连续性台账

为每个场景创建一项 `continuity_logs`，只保存该场景初始状态和跨场继承关系：

- `scene_id`：机器匹配键，格式为 `S[0-9]{2,}`，必须唯一；数字部分只用 ASCII `0-9`，当前合同不额外禁止 `S00` 或超过两位。JSON 内一切场景引用使用该字段。
- `scene`：展示名，用于 Markdown/Excel 场景列，例如 `1 室外山林 日 外`。
- `first_shot_anchor_type`：只允许 `space | multi_character | both | single_continuation | subjective`。
- `spatial_axis`：供人阅读的主轴线、人物相对方向、入口/出口、越轴限制。
- `spatial_axes`：2.4.5 机器轴线数组。每项含唯一 `axis_id: AX[0-9]{2,}`、`axis_type: eyeline | movement | action | spatial`、非空 `endpoint_a` / `endpoint_b`、`side_a_anchor` / `side_b_anchor`；两端点不得相同。`multi_character | both` 至少一项。
- `fixed_objects`：固定物名称、位置和状态。
- `characters`：角色名称、初始位置、朝向和状态。
- `props`：道具名称、位置、归属和状态。
- `sound_sources`：以 `SS[0-9]{2,}` 稳定 ID 为键的对象；数字部分只用 ASCII `0-9`，当前合同不额外禁止 `SS00` 或超过两位。每项必须含非空 `name`、`visibility`、`position`、`state`，其中 `visibility` 仅允许 `onscreen | offscreen`。
- `reality_layer`：现实、回忆、梦境、灵魂、主观视角等现实层级。
- `inherits_from`：同空间跨场继承的父场景 `scene_id`，无继承时为空字符串。
- `inherited_states`：从父场景继承的 RFC 6901 JSON Pointer 列表。
- `diverged_states`：从父场景发散或重置的 RFC 6901 JSON Pointer 列表。

凡会被 `continuity_update` 修改、或其子字段会被跨场继承的 character / prop / fixed_object，必须使用可定位的结构化条目（对象映射，或含稳定 `name` / `entity` 的对象数组）；自由文本字符串只能用于不会迁移的展示说明。2.4.3 的 update 若无法在当前场景初态中定位实体及字段，直接 FAIL；历史版本保持原只读语义。

继承规则：显式 `inherits_from` 高于默认重置；未列入 `inherited_states` 的字段按新场景重置。新写值必须以 `/` 开头并按 RFC 6901 使用 `~0` 表示 `~`、`~1` 表示 `/`，例如 `/characters`、`/sound_sources/SS01/position`。旧顶层裸字段（如 `characters`）仅作兼容，等价于 `/characters`；包含 `.` 的点号路径不是合法 pointer。裸字段与 pointer 规范化后不得重复；`inherited_states` 与 `diverged_states` 之间同一路径或祖先/子路径都视为冲突。每条 inherited 路径必须在父场景终态与子场景初态同时存在且值相等；每条 diverged 路径也必须在父、子两侧存在，但它表示“不承担继承等值义务”，父子当前值允许偶然相同。台账不是不可变快照，后续镜头只能通过 `continuity_updates` 追加有事实证据的迁移，不得覆盖历史或让状态无镜头依据地跳变。

### 场景首镜锚定类型

- `space`：山林、道路、高速、山坳、大厅、洞窟入口、广场、走廊等需要先建立地形、方向和固定物的场景。
- `multi_character`：同一场景首段出现 2 人及以上可见互动，包括室外群戏、室内多人对话、多人行动、多人对峙。
- `both`：同时需要空间锚定和多人站位锚定。
- `single_continuation`：单人独处、上一场已建立空间后的近距离情绪承接，或多人并非本场主要互动的承接镜。
- `subjective`：虚空、幻境、记忆、抽象主观场域。

类型为 `space`、`multi_character`、`both` 时，本场第一镜必须使用全景类景别：`大远景`、`大全景`、`全景`、`中全景`。`multi_character`、`both` 的首镜还必须让 `visible_characters` 至少包含 2 个不同角色、覆盖当前镜头的 `position` fact，并在 `【场景首镜站位】` 中完整交代所有可见互动角色的基础位置、朝向、距离与主要视线关系；第二镜只能补充遮挡、前后景或细微关系，不得补交基础站位。类型为 `single_continuation` 或 `subjective` 时，首镜可以不是全景类，但仍必须保留 `【场景首镜站位】` 标签，内容可写空间边界、固定物方向或主观视觉锚点。

## Beat 与事实

### 2.4.3 源文锁定

`shot_data` 必须包含顶层 `script_lock`：

```json
{
  "status": "locked",
  "approved_script_path": "outputs/YYYY-MM-DD/docs/<片名>.approved_script.txt",
  "locked_text": "人类确认后的完整剧本文本",
  "locked_text_hash": "sha256(normalized_locked_text)",
  "approved_corrections": [
    {"from": "原始文本", "to": "批准后文本", "reason": "人工批准原因"}
  ]
}
```

`approved_script_path` 必须是相对 `--workspace-root` 的 UTF-8/UTF-8 BOM 普通文件路径；解析后的真实路径不得逃出工作区。校验器必须实际读取该文件，路径字符串本身不构成凭证。读取时仅移除开头 BOM，并将 CRLF/CR 统一为 LF；结果必须与 `locked_text` 全文一致。拆分 Beat 前、Gate A 前、Gate B 前和 Gate C 前必须复核：标题行、全部场景头、全部人物行和正文行均在 `locked_text` 中；不得只锁表格段落、摘要段落或局部正文。

2.4.3 的 `locked_text_hash` 对上述规范化全文直接计算 SHA-256，不删除其他空白；2.4.1/2.4.2 旧数据按各自旧算法只读校验。`locked_text` 是唯一源文；Beat 与 Shot 不得手写摘要。每个 `beats[*].source_text` 与 `shots[*].source_paragraph` 必须通过 `source_span` 或 `source_spans` 指向规范化文本的 0-based Unicode code point 左闭右开区间：

```json
{"start": 0, "end": 18, "text_hash": "可选，span 文本的同规则 hash"}
```

`start` 与 `end` 只能是真正 JSON 整数，不接受布尔值、字符串或小数。`source_span` 与 `source_spans` 互斥；多段非连续原文使用 `source_spans`，必须按 `start` 严格升序、无重叠、无重复，并按顺序用 LF 拼接。校验器从 `locked_text[start:end]` 回切文本并与 `source_text` / `source_paragraph` 逐字对比；任何摘要、删字、改词、换序或缺少区间均为 FAIL。

1. Beat ID 使用 canonical 格式：数值后缀必须大于 0，1–999 固定写三位（`B001`…`B999`），1000 起不加前导零（`B1000`、`B1001`……）。Beat ID 一经创建永久稳定；新增 Beat 只取尚未使用且大于现有最大数值后缀的 ID，不得因插入、删除或重排复用空号或重编号。`B000`、`B0001` 等非 canonical 写法一律 FAIL。
2. 每个 Beat 必须有 `beat_order`。它是 canonical 正十进制字符串：值必须大于 0，禁止符号、指数、前导零和无意义尾零（合法如 `1`、`1.5`、`0.25`；非法如 `0`、`01`、`1.0`、`.5`、`1e2`）。用任意精度 `Decimal` 比较，禁止二进制浮点；初建可用 `1, 2, ...`，插到首项前取 `first_order / 2`，插到相邻 Beat 间取两者 Decimal 中点，追加取末项加 1，再输出 canonical 字符串。`beats` 数组必须按其数值严格递增。
3. 为每个必须拍到的事实分配 `{Beat ID}-F{两位序号}`，例如 `B003-F02`；事实 ID 必须全局唯一、绑定所属 Beat，`fact.text` 必须是非空字符串。
4. 事实类型只使用：`character`、`action`、`dialogue`、`prop`、`space`、`position`、`emotion`、`sound`、`reality`。
5. 一个镜头可以覆盖一个或多个 Beat；一个 Beat 可以由多个镜头共同完成。
6. `dialogue` 事实的 `text` 只写需要逐字保留的对白原文，不含角色名前缀或说明；另含 `speaker`（本场角色）、`addressees`（本场角色数组，可空）、`delivery: onscreen | offscreen | vo`。
7. `fact.text` 必须使用原文词汇或其直接指称，禁止写入视觉化翻译；情绪视觉化只允许出现在运镜主画面列。
8. `space_anchor_fact` / `blocking_anchor_fact` 是职责名称，不是新增字段或 fact type；分别用现有 `type: "space"` / `type: "position"` 表达。它们可记录空间轴线、朝向、画面左右关系等制作补足，但必须标为 `[合理补足]`，不得写镜头、焦段、构图、运镜等摄影设计，也不得新增剧情事实。
9. 每个事实 ID 必须至少出现在一个镜头的 `covered_fact_ids` 中，且该镜头必须绑定事实所属 Beat。
10. 不得用“已隐含”或“观众能理解”替代可拍事实。无法视觉化的事实必须在备注说明处理方式；不得机械一 Beat 一镜或机械多 Beat 一镜。

多 Beat 显示以 `beats` 的 Decimal order 排序位置为准：只有 order 数组位置连续且 ID 数值逐一加 1 时可缩写 `B001-B003`；其他多 Beat 用 `+` 显式列举。`+` 本身不表示非连续；只有所选 Beat 之间存在未覆盖的 order 位置时，才必须写 `[非连续Beat]` 加原因，不能只按 ID 数字是否连续判断。

### 对白保真

同镜 `source_paragraph` 与 `type == "dialogue"` 的 facts 共同构成允许对白集合。`camera_main_image` 与 Prompt 中每段中文或英文引号内对白必须逐字命中该集合；只允许引号样式不同，不得修改、截断或重排引号内字符。仅原文明确标注 VO、画外声，或明确人物不在场且只闻其声时，才可登记为画外声。

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
- `cut_group`：兼容字段，2.4.3 不参与门禁判断。
- `cut_category`：只用于统计与审计，不作为 `must_isolate` 合并门禁。
- `cut_moment_id`：标记同一不可拆瞬间。
- 默认 `must_isolate`：真相首次落地、宿主/替身/惩罚/起源解释、VFX 不可逆变化、首次 VO/画外声源、现实层切换、重大情绪反转。
- 同镜合并多个 `must_isolate` 事实的唯一条件：同 Beat、同 `cut_moment_id`，且镜头备注写 `[不可拆说明]`。
- 单场 `must_isolate` Beat 占比超过 50% 时只触发 WARN，唯一处置路径是 Gate A 人工逐条裁决 `keep` 或降级；模型不得自行降级。

## 状态迁移

每条迁移包含：

```json
{
  "entity_type": "character | prop | fixed_object | sound_source | reality_layer",
  "entity": "实体名称；sound_source 使用 SSxx；reality_layer 使用空字符串",
  "field": "position | facing | state | owner | visibility | value | presence",
  "from": "迁移前状态",
  "to": "迁移后状态",
  "evidence_fact_ids": ["B002-F01"]
}
```

- `entity_type` 与 `field` 只能使用上表枚举；除 `reality_layer` 的 `entity` 固定为空字符串外，其余实体名必须非空。`entity_type`、`entity`、`field`、`from`、`to` 都必须是无首尾空白的原生字符串，`from` / `to` 不得为空。
- `from` 必须等于该实体当前状态，`to` 不得与 `from` 相同。
- 证据事实必须由当前镜头覆盖；`sound_source` 的每条迁移还必须至少命中一个 `type: "sound"` 的当前镜头事实。
- 人物 `position` 或 `facing` 迁移时，运镜主画面必须出现 `【站位位移】`。
- 运镜主画面出现 `【站位位移】` 时，当前镜头必须登记对应位置或朝向迁移。
- 声源 `position`、`visibility` 或 `state` 变化时，必须以 `entity_type: "sound_source"`、当前场景台账已登记的 `entity: "SSxx"` 登记；`from`/`to` 必须是无首尾空白的非空字符串，并对应该声源对象当前字段值。首次被听见的声源可先以 `state: "silent"` 或等义初态登记；凡镜头或 fact 使用 `new_sound_source`，该镜必须覆盖 `sound` fact，并让对应 sound_source update 的 `evidence_fact_ids` 命中该 fact。
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
| 声源位置 / 可见性 / 状态变化 | 是 | 否 |

校验器逐镜推进当前状态；`continuity_update.from` 必须等于上一状态，`to` 才会成为下一状态。

## shot_data 结构

保存 UTF-8 JSON，顶层结构固定。下列 JSON 是字段位置示意，不是可直接通过校验的完整样例；`|` 分隔内容表示任选其一，`continuity_logs`、`beats`、`shots` 等必需数组不得按示意留空：

```json
{
  "metadata": {
    "skill_name": "su-fenjingskill-zh",
    "version": "2.4.5",
    "rule_revision": "2.4.5-director-shot-integrity-guard-2026-07-18",
    "title": "片名或集名",
    "project_lexicon": {
      "prop_terms": ["项目道具词"], "space_terms": ["项目场景词"], "vfx_terms": ["项目特效词"], "reality_terms": ["项目层级词"], "sound_terms": ["项目声源词"]
    },
    "reference_status": {
      "continuity-shot-data": "loaded | missing",
      "hybrid-shot-audit": "loaded | missing",
      "camera-language": "loaded | missing",
      "seedance-prompt-rules": "loaded | missing",
      "project-notes": "loaded"
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
    "approved_script_path": "outputs/YYYY-MM-DD/docs/<片名>.approved_script.txt",
    "locked_text": "人类确认后的完整剧本文本",
    "locked_text_hash": "sha256",
    "approved_corrections": []
  },
  "batch_plan": null,
  "human_reviews": [],
  "warn_resolutions": [],
  "continuity_logs": [],
  "beats": [],
  "performance_chains": [],
  "directorial_constraints": [],
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
  "spatial_axes": [
    {"axis_id":"AX01","axis_type":"movement","endpoint_a":"山脚","endpoint_b":"岭上","side_a_anchor":"山路左侧林缘","side_b_anchor":"山路右侧崖边"}
  ],
  "fixed_objects": ["山路", "密林", "裂缝入口"],
  "characters": [
    {"name": "A", "position": "画面左前", "facing": "岭上"},
    {"name": "B", "position": "画面中间", "facing": "岭上"},
    {"name": "C", "position": "画面右后", "facing": "岭上"}
  ],
  "props": [],
  "sound_sources": {
    "SS01": {"name": "山门钟声", "visibility": "offscreen", "position": "山门外", "state": "持续"}
  },
  "reality_layer": "现实",
  "inherits_from": "",
  "inherited_states": [],
  "diverged_states": []
}
```

`inherits_from` 为空时，两类 pointer 列表必须为空。跨场字段片段：`{"scene_id":"S02","inherits_from":"S01","inherited_states":["/sound_sources/SS01/state"],"diverged_states":["/characters"]}`；其中 S02 初态的 `/sound_sources/SS01/state` 必须逐类型等于 S01 全部镜头推进后的终态，而不是 S01 的开场初态。

### batch_plan 结构

单批任务使用 `null`。长输入使用非空结构：

```json
{
  "batches": [
    {"batch_id": "BT01", "scene_ids": ["S01", "S02"], "expected_shot_count": 20, "depends_on": []}
  ]
}
```

`batch_id` 格式为 `BT[0-9]{2,}`，数字部分只用 ASCII `0-9`，当前合同不额外禁止 `BT00` 或超过两位，且必须唯一；每个场景只能属于一个批次；`expected_shot_count` 必须是正整数，但只用于容量规划，不是拆镜目标或验收阈值；`depends_on` 只能引用已存在批次且依赖图无环。所有 Beat 与 Shot 必须归属已登记场景及批次。空对象或空 `batches` 不是合法长输入计划，也不能用来绕过 Gate 0。

### Beat 结构

以下 Beat 与 Shot JSON 继续是字段结构示意；完整可校验数据还必须满足源文回切、切点字段、Gate、Prompt 派生和全局引用合同。

```json
{
  "beat_id": "B001",
  "beat_order": "1",
  "scene_id": "S01",
  "scene": "1 室外山林 日 外",
  "source_text": "原文",
  "source_span": {"start": 0, "end": 2, "text_hash": "可选"},
  "dramatic_function": "本 Beat 的叙事功能",
  "facts": [
    {"fact_id": "B001-F01", "type": "action", "text": "A抬手指向山门", "performers": ["A"], "cut_priority": "normal", "cut_reasons": [], "cut_group": "B001-action", "cut_category": "action", "cut_moment_id": "B001-action-moment"}
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
  "camera_geometry": {
    "axis_id": "AX01 | null",
    "axis_side": "side_a | side_b | on_axis | not_applicable",
    "camera_position": "可复核的相对机位位置",
    "camera_facing": "toward_end_a | toward_end_b | along_a_to_b | along_b_to_a | across_axis | subjective | overhead | not_applicable",
    "angle_delta_from_previous": "scene_start | same | minor | substantial | axis_cross | not_comparable",
    "primary_subjects": ["角色或主体"],
    "pov_character": null,
    "screen_directions": [{"entity":"A","kind":"facing | eyeline | movement","direction":"screen_left | screen_right | toward_camera | away_camera | neutral"}]
  },
  "performance_cues": [{"character":"A","channel":"gaze_face | breath_voice | posture_hand | stillness","description":"逐字存在于 camera_main_image 的表演描述","evidence_fact_ids":["B001-F01"]}],
  "action_progressions": [{"entity":"A","evidence_fact_ids":["B001-F01"],"start":"逐字起点","process":"逐字过程","end":"逐字终点"}],
  "environment_cues": [{"kind":"sound | light | contact","basis":"fact | inevitable_action","description":"逐字存在于 camera_main_image 的环境反馈","evidence_fact_ids":["B001-F01"]}],
  "chain_breaks": [{"chain_id":"PC001","after_step":1,"reason":"must_isolate | reality_shift | time_jump | spatial_discontinuity | intentional_editorial_emphasis"}],
  "continuity_updates": [],
  "shot_type": "master | action | dialogue | reaction | insert | transition | vfx_anchor | safety",
  "split_reason": ["spatial_anchor | performance_continuity | new_information | prop_state_change | new_vfx_state | new_sound_source | reality_layer_shift | causal_reveal | emotional_turn | continuity_migration"],
  "insert_priority": "none | recommended | must_have",
  "long_take_support": []
}
```

`camera_geometry` 是 2.4.5 的相邻镜头机器事实。`axis_id` 为 null 时 `axis_side` 必须是 `not_applicable`；绑定 AXxx 时不得是 `not_applicable`。本场首镜 `angle_delta_from_previous=scene_start`，其他镜头不得使用该值；同轴相邻 `same | minor` 代表没有达到等价 30 度机位变化，改变景别不能替代改机位。`primary_subjects` 中的人物必须在本镜可见或为 POV，非人物主体必须是本场已登记 props/fixed_objects 且出现在 `visible_props` 或主画面；两镜有共同可见人物、共同主体，或同轴且 `camera_position` 未改变时不得写 `not_comparable`。`substantial` 必须伴随不同 `camera_position`。主观三元组必须填写本场角色 `pov_character`，非主观镜必须为 null。屏幕方向反转必须由后镜 position/facing update 支撑。

有可见人物时 `performance_cues` 必须 1–3 项，无可见人物时为空；人物必须在本镜可见集合中，描述逐字存在于主画面且事实证据为本镜覆盖子集。Cue evidence 只能是 action/emotion/dialogue/position：action/emotion 的 cue.character 必须属于 performers，dialogue 必须等于 speaker，position 必须由 fact.text 明确点名；space/prop/sound/reality 不能单独为人物表演取证。每个已覆盖 action/emotion fact 的 `performers` 必须映射到本镜可见、画外或 POV 集合；可见 performer 必须有引用该 fact 的 cue。存在 continuity update，或 split reason 含 `prop_state_change | new_vfx_state | continuity_migration` 时，`action_progressions` 非空并逐字写出起点、过程、终点。主画面让声音、光线或接触承担信息时，`environment_cues` 非空且只能来自 fact 或已有动作的不可避免反馈。以上三个字段与 `chain_breaks` 即使为空也必须显式为数组。

相邻镜头若使用完全相同的 `source_span(s)`，默认 FAIL。结构性不可合并时，后镜可加：

```json
{"source_reuse":{"from_shot_no":1,"reason":"simultaneous_must_isolate | single_sentence_multi_action | source_line_indivisible"}}
```

同时备注 `[原文复用]` 并由 Gate B 精确批准 `shot:<n>:source-reuse`，才降为人工 WARN。

### Performance chain 与导演约束

同一人物连续动作、反应和台词默认是一个不可机械切开的表演单元：

```json
{
  "chain_id":"PC001",
  "scene_id":"S01",
  "character":"A",
  "steps":[
    {"role":"action","fact_ids":["B001-F01"]},
    {"role":"reaction","fact_ids":["B001-F02"]},
    {"role":"dialogue","fact_ids":["B001-F03"]}
  ]
}
```

`chain_id` 全局唯一且符合 `PC[0-9]{3,}`；至少两个步骤，步骤 facts 均属于同场。Action/emotion fact 必须显式含非空 `performers[]`；纯物体/环境变化改用 prop/space/sound/reality。链中 dialogue 的 `speaker`、action/emotion 的 `performers` 必须与 `chain.character` 一致。整条链的所有事实默认至少共同落在一个镜头；仅让每对相邻步骤分别重叠、却没有一镜承载整链，仍视为拆镜。确需拆分时，每个经批准的 boundary 必须把整链划分为内部可共同覆盖的连续段，后段首镜登记 `chain_breaks`、备注 `[动作链拆分]`，并经 Gate B 批准 `shot:<n>:performance-chain-break`；`recommended`、`insert_priority` 或方便剪辑本身不是拆分理由。

为防止通过省略 `performance_chains` 绕过，校验器会按 Beat 顺序扫描连续 action/emotion/dialogue facts：dialogue 使用 `speaker`，action/emotion 使用结构化 `performers`；恰好一名表演者时自动归属。相邻两项属于同一角色却没有共同镜头时，必须已有覆盖二者的 chain；否则直接 FAIL。多人共同动作必须由 Gate A 人工建立 chain 或 directorial constraint，不能靠模糊文本猜测。

人工审核形成的持续约束使用：

```json
{
  "constraint_id":"DC001",
  "type":"same_shot | same_beat | forbid_literal | direct_handoff",
  "freeze_gate":"GATE_A | GATE_B",
  "origin":{"gate":"GATE_A | GATE_B","round":1},
  "fact_ids":["B001-F01","B001-F02"]
}
```

- `same_shot`：`fact_ids` 至少两项，必须共同落在一镜。
- `same_beat`：`fact_ids` 至少两项且所属 Beat 相同。
- `forbid_literal`：写 `literal`，并至少给 `scene_ids` 或 `shot_nos` 范围；禁止字面元素不得出现在主画面、Prompt 或 `visible_props`。
- `direct_handoff`：写有效 `from_fact_id`、`to_scene_id`、`forbidden_literal`；目标场首镜不得再次出现被禁止的过渡元素。

两类顶层数组都进入 Gate A/B review hash，生成后不得静默删除或改写。

关键约束：

- `continuity_logs`、`beats`、`shots` 必须是非空数组；`continuity_logs[*].scene_id` 必须唯一；`shots[*].scene_id` 与 `beats[*].scene_id` 必须匹配已登记场景。
- 可选 `metadata.project_lexicon` 必须是对象且只允许五个固定 key；无词项的 key 可省略，每个已出现的值必须是非空、无首尾空白、无 Unicode 控制/格式/代理字符、同一 key 内无重复的字面词数组。正则元字符允许出现但一律转义后按普通子串匹配，不得扩大命中范围；词表随 Gate 0/A/B hash 冻结。不启用项目词时省略整个字段；未使用 `project-notes.md` 时也从 `reference_status` 省略该可选键。
- Beat ID 与 Fact ID 必须唯一；Fact ID 格式为 `<Beat ID>-F[0-9]{2}`，数字部分只用 ASCII `0-9`，当前合同不额外禁止 `F00`。Beat ID 永久稳定，新增只取未用更大号；`beats` 与每个 `shots[*].beat_ids` 都必须按 canonical `beat_order` 的 Decimal 值严格递增。Shot 引用的 Beat、Fact、Scene 必须存在、归属一致且处于同一场景。
- 每个镜头 `covered_fact_ids` 非空；唯一例外是 `shot_type == "safety"`、备注含 `[安全镜][人工批准]`，且 Gate B 明确批准无事实安全镜。
- `transition` 与 `safety` 镜默认也必须绑定空间、声音或现实层事实；无事实安全镜只能由 Gate B `approved_items` 以 `shot:<镜号>:safety` 精确批准。
- `duration_breakdown` 各分项与 `duration_seconds` 只接受 JSON 整数，拒绝布尔值、小数、字符串数字、NaN 与 Infinity；总时长必须大于 0，且精确等于 `max(sync_action_seconds, sync_dialogue_seconds) + non_sync_action_seconds + emotional_pause_seconds`。
- 超过 10 秒的镜头必须至少两项 `long_take_support`，且 `long_take.classification` 不得为 `not_applicable`。
- `visible_characters` 与 `offscreen_characters` 每项必须是无首尾空白的非空字符串，同一数组内不得重复，两数组不得重叠；`multi_character` / `both` 首镜的可见角色还必须在台账可识别角色和 `【场景首镜站位】` 中逐一出现。
- 主画面非对白区域出现的本场角色必须映射到 visible/offscreen/POV；onscreen dialogue speaker 必须可见，offscreen/vo speaker 必须在画外集合，addressees 必须可见、画外或 POV。
- offscreen/vo dialogue fact 不得单独成镜；当前镜必须同时覆盖至少一个非 dialogue fact，给声音提供可见动作、反应、空间或其他画面事实支撑。
- `continuity_updates[*].evidence_fact_ids` 必须由当前镜头覆盖；迁移只能追加，禁止覆盖历史或无镜跳变。继承/发散使用 RFC 6901 pointer：规范化重复 FAIL，两类列表之间同路径及祖先/子路径冲突；inherited 路径须在父场景终态与子场景初态存在且值相等，diverged 路径须在父、子两侧存在；`inherits_from` 不得自指或成环。`sound_sources` 必须是 SSxx 键对象，声源变化必须使用已登记 SSxx 的 `sound_source` update；`new_sound_source` 还必须由当前镜头覆盖的 sound fact 取证。
- 备注中所有方括号标签必须属于 `SKILL.md` 的封闭清单；非连续 Beat 必须使用 `+` 并注明 `[非连续Beat]` 原因。
- 任何镜头包含 `keyframe` 字段都是失败项。
- `old_shot_no`、`PASS_INTERNAL`、`运镜修正`、`【镜内变化】` 属于过程痕迹，不得进入交付数据；`revision_log` 是唯一合法过程记录。

## 人工审核记录

每条 `human_reviews` 使用；`approved_items` 必须显式存在，非 Gate B 时写空数组：

```json
{
  "gate": "GATE_0 | GATE_A | GATE_B | GATE_C",
  "round": 1,
  "status": "approved | rejected",
  "reviewer": "人工标识",
  "notes": "审核意见原文摘录",
  "reviewed_hash": "该 Gate 审核范围的 64 位 SHA-256",
  "batch_id": "BT01；单批任务与 Gate 0/C 省略",
  "approved_items": ["shot:12:jump-cut", "shot:13:axis-cross", "shot:14:performance-chain-break", "shot:15:source-reuse"]
}
```

`human_reviews` 按工作流约定实行程序性 append-only：禁止修改或删除既有记录，只能追加。校验器只能检查当前快照中的顺序、连续 round、最新状态与 `reviewed_hash`，不能证明同一可编辑文件的历史记录从未被原地改写，也不能认证 `reviewer` 身份。同一 Gate/批次的 `round` 必须从 1 开始连续加 1，只认最高轮次；最新 `rejected` 会撤销旧 `approved`。Gate 顺序必须合法。分批任务 Gate A/B 必须带 `batch_id` 并覆盖所有批次；Gate 0/C 不带批次。

Gate 0/A/B 使用各阶段 hash；Gate C `reviewed_hash` 必须等于 `canonical_data_hash`。hash 范围与算法以 `SKILL.md` 为准。旧 token 为 `safety | axis-reversal | required-adjacent`；2.4.5 新 token 为 `jump-cut | axis-cross | performance-chain-break | source-reuse`，一律使用 `shot:<shot_no>:<token>` 且与对应标注和结构化字段同时成立，泛化批准无效。预签发要求 Gate A/B（分批时含 Gate 0）最新轮次批准且 hash 匹配；`--final-signoff` 额外要求 Gate C 最新轮次批准且 hash 匹配。

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

每条 WARN 必须有处置记录。2.4.5 白名单 WARN 仅包括 reference missing、`[合理补足]`，可用 `auto_whitelist`；节奏越界、跳切、越轴、动作链拆分、原文复用及其他 WARN 必须由 `human` 处置。

`resolution: "revise"` 只记录历史修订；若当前 WARN 仍存在，则仍未解决。仍存在的 WARN 只有合法的 `keep` 或 `accepted_without_change` 才能关闭。

## 校验状态

- `PASS`：结构、覆盖、连续性、时长、Prompt、Markdown 和 Excel 一致，且必需 Gate 记录与审核 hash 完整。
- `WARN`：结构可交付但存在 WARN；所有 WARN 均有 `warn_resolutions` 后方可交付。
- `FAIL`：结构错误、表头不符、Beat/事实遗漏、时长错误、连续性断裂、可见性错误、Prompt 合同错误，或 JSON/Markdown/Excel 任意内容不一致。
- `NOT_RUN`：仅在合法 builder 已生成三份正式产物、但最终校验环境暂不可用时使用；`source_json_hash` 必须为空字符串，Gate C 必须明确接受 `accepted_without_validation`，任何摘要不得称为 PASS。builder 缺失时不得生成新交付。

strict validate 必须重算 status、warnings、errors、计数、Gate/WARN 审计和 `canonical_data_hash`，不得信任数据内已有 PASS。`source_json_hash` 必须是与当前内容相符的 64 位小写十六进制 SHA-256；canonical 输入排除 `validation_report`、`human_reviews`、`metadata.revision_log`，但包含 `warn_resolutions`。

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

2.4.5 的 build/validate 必须传 `--workspace-root` 与 `--report`；2.4.4 及更早版本只读 validate。build 将 JSON、Markdown、Excel、report 全部写入同目录临时文件，四份生成并自检成功后再原子替换；任一步失败都保留既有正式文件，不回写输入 JSON。Markdown/Excel 必须使用同一 canonical 单元格格式化规则，保证换行、字面量 `<br>`、数值和以 `= + - @` 开头的文本可逆且不被当作公式。
