# su-image9 Spatial Continuity Contract

<!-- ref-version: 2.0.3 -->

## Source Reads

可用时优先读取 `shot_data.json` 的 `shots[].camera_main_image`、`visible_characters`、`offscreen_characters`、`visible_props`、`continuity_updates` 与顶层 `continuity_logs`。`su-fenjingskill-zh` 的 Prompt 列只能作为镜头摘要辅助，不得作为唯一输入。

场景、固定物、角色、车辆、道具和 VFX 必须有上述字段或已绑定参考资产依据。禁止通用洞穴、岩壁、地裂、雾核、家具、门窗、车辆和“本页无车辆”等无来源默认值。字符串数组与对象数组先规范化；布尔值和未知对象类型不得充当实体。

## Prompt Shape

正式提示词每页固定为 12 层：

```text
DELIVERABLE:
SYSTEM_STYLE_LAYER:
SCENE_LAYER:
CAMERA_RULE_LAYER:
CONTINUITY_LAYER:
REFERENCE_USAGE 或 TEXT_DERIVED_LAYOUT:
PANEL_1_MASTER_SPATIAL_LAYOUT_ANCHOR:
DOOR_WINDOW_FURNITURE_GEOMETRY_LOCK:
VEHICLE_AND_AXIS_LOCKS:
OBJECT_VISIBILITY_AND_BOUNDARIES:
PANEL_LAYER PANEL-1 to PANEL-9:
NEGATIVE_CONSTRAINTS:
```

`panel_plan.json` 是机器轨；`PANEL_LAYER` 是生图轨。机器轨短字段不得直充生图文本。

## Panel 1 Anchor

- `PANEL-1` 必须是该页主空间锚定。
- `PANEL-1` 必须保留本页来源范围首镜号；不得为了锚定便利把后续镜头提前。
- 来源第一镜为特写、近景、过肩、反应、插入、POV、黑场或其他不可证明的空间锚定时，不得改宽、不得重排。设置 `release_ready=false`，记录 `R-FIRST-SHOT-ANCHOR` 并返回 `REVIEW_REQUIRED`。
- 后续 Panels 2-9 只能从 Panel 1 裁切、推进、反打、俯拍、侧拍或换焦点，不得重新布景。

## Vehicle And Axis

- 车辆页必须区分 `vehicle left/right/front/rear` 与 `screen left/right`。
- 左舵默认：驾驶座为 `vehicle front-left`，副驾为 `vehicle front-right`，右后排为 `vehicle rear-right`。
- 关系镜头必须写具体轴线 A/B 端、摄影机允许侧、肩位和 `screen left/right`，不得只写原则句。

## De-Duplication

每页必须有 9 个不同视觉任务。2.0.3 不再通过推测动作阶段或重复末镜补足来源不足；需要补格的 sparse 页设置 `release_ready=false`，记录 `R-SPARSE-UNIQUENESS` 并返回 `REVIEW_REQUIRED`。

## Scene And Layer Aware Pagination

正式派生脚本必须按连续空间、人物关系轴线、车辆内外连续关系和叙事层级切页，不得固定每 9 镜头硬切。可发布页只能有一个 `scene_id` 和一个现实/叙事层级；回忆、手术现实或黑屏镜头可以在结构化空间成立时独立开页。任何跨场或跨层页都设置 `release_ready=false`，记录 `R-CROSS-SCENE` / `R-CROSS-LAYER` 并返回 `REVIEW_REQUIRED`，旧 bridge 声明不得豁免。

## Distance Stage Lock

相邻镜头存在靠近、退后、两步远、贴近、扑上去、跪到面前等位移终点时，前序 Panel 必须保持位移前距离和可见空间纵深，后序 Panel 才能画终点状态。该锁定写入 `panel_plan.json` 的 `distance_stage_lock`，并同步进入对应 `PANEL_LAYER` 自然语言描述。
