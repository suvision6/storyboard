# su-image9 Spatial Continuity Contract

<!-- ref-version: 2.0.1 -->

## Source Reads

可用时优先读取 `shot_data.json` 的 `shots[].camera_main_image`、`visible_characters`、`offscreen_characters`、`visible_props`、`continuity_updates` 与顶层 `continuity_logs`。`su-fenjingskill-zh` 的 Prompt 列只能作为镜头摘要辅助，不得作为唯一输入。

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
- 来源第一镜为特写、近景、过肩、反应、插入、POV 或黑场时，保留来源镜号，但改写为 `drawn_camera_tag: master wide/full spatial anchor`，只在首镜事实内扩展空间。
- 后续 Panels 2-9 只能从 Panel 1 裁切、推进、反打、俯拍、侧拍或换焦点，不得重新布景。

## Vehicle And Axis

- 车辆页必须区分 `vehicle left/right/front/rear` 与 `screen left/right`。
- 左舵默认：驾驶座为 `vehicle front-left`，副驾为 `vehicle front-right`，右后排为 `vehicle rear-right`。
- 关系镜头必须写具体轴线 A/B 端、摄影机允许侧、肩位和 `screen left/right`，不得只写原则句。

## De-Duplication

每页必须有 9 个不同视觉任务。来源节点不足时只能从已公开事实中补足动作阶段、位置建立、结果、反应或道具状态变化；无法补足时重新分页，不得硬凑。

## Distance Stage Lock

相邻镜头存在靠近、退后、两步远、贴近、扑上去、跪到面前等位移终点时，前序 Panel 必须保持位移前距离和可见空间纵深，后序 Panel 才能画终点状态。该锁定写入 `panel_plan.json` 的 `distance_stage_lock`，并同步进入对应 `PANEL_LAYER` 自然语言描述。
