# su-image9 Output Templates

Use this file when creating deliverables. The analysis draft may be detailed; `final_image_prompts.md` must be compressed but still carry the spatial and physical hard locks.

## Required Files

- `分析与锁定.md`
- `final_image_prompts.md`
- `panel_plan.json`

Generated images belong under `outputs/YYYY-MM-DD/images/` only after validator passes and the user explicitly requests image generation.

## 分析与锁定.md Template

```markdown
# SU-IMAGE9｜分析与锁定

## 基本信息

| 项目 | 内容 |
|---|---|
| 技能 | su-image9 |
| 版本 | 1.6.0 |
| 来源 | shot_data / continuity_logs / references / text |
| 输出 | 分析稿 + final_image_prompts.md + panel_plan.json |
| 是否生图 | 是/否 |
| 参考图绑定状态 | bound / not_bound / prompt_only |

## 参考资产锚点

| 资产 | 对象 | 只继承 | 禁止继承 | 冲突状态 |
|---|---|---|---|---|

## PROJECT_VISUAL_PROFILE

| 对象 | 身份/轮廓 | 服装剪影 | 道具归属 | 状态变化 | 禁止互换 |
|---|---|---|---|---|---|

## CONTINUITY_LAYER 草案

| 页 | 来源场景 | 固定物 | 起点/朝向 | 地面层级 | 道具状态 | 现实层 |
|---|---|---|---|---|---|---|

## P01 主锚定表

| Page | P01 类型 | 来源镜号 | DRAWN CAMERA TAG | ANCHOR_VISIBLE_ALLOWED | 可站立面 | 禁站区 |
|---|---|---:|---|---|---|---|

## 固定物与地面投影表

| Page | Panel | 固定物/地面 | 屏幕投影/裁切 | 禁止漂移 |
|---|---:|---|---|---|

## Panel 继承与构图差异表

| Page | Panel | 来源镜号 | 继承 P01 哪些锚点 | camera/scale/subject/depth 差异 | split 是否有效 |
|---|---:|---:|---|---|---|

## 轴线、肩位、构图表

| Page | Panel | A端 | B端 | 摄影机侧 | screen left/right | 肩位/前后层级 | 主体画面区域 |
|---|---:|---|---|---|---|---|---|

## 道具时间状态表

| Page | Panel | STAFF | BRACELET | MIST/LIGHT | 互斥检查 |
|---|---:|---|---|---|---|

## 输出前校验

| 项目 | 结果 | 说明 |
|---|---|---|
```

## panel_plan.json Minimum Shape

```json
{
  "skill": "su-image9",
  "version": "1.6.0",
  "source": "shot_data path",
  "reference_binding_status": "bound | not_bound | prompt_only",
  "pages": [
    {
      "page": "P01",
      "title": "page title",
      "shots": [1, 2, 3],
      "space": "page space",
      "axis": "page axis",
      "floor_plane_lock": "allowed standing surface",
      "forbidden_standing_zones": ["void", "below cliff"],
      "camera_composition_lock": "page camera and composition rule",
      "panels": [
        {
          "panel": "P01",
          "source_shot": 1,
          "role": "source | anchor_override | split",
          "phase": "primary / distinct split task",
          "camera_tag": "copied shot tag",
          "visible_characters": [],
          "visible_props": [],
          "content_source_sanitized": "",
          "difference_task": "",
          "axis_lock": "",
          "floor_plane": "",
          "forbidden_standing_zone": "",
          "camera_composition": "",
          "split_composition_delta": "",
          "prop_temporal_state": ""
        }
      ]
    }
  ]
}
```

## final_image_prompts.md Template

Each page target is 5,000-9,000 characters. Stop if any page exceeds 12,000 characters.

```text
# P01 Page Title

DELIVERABLE:
Generate one wide horizontal 16:9 canvas containing a clean 3x3 storyboard grid. Image-only, no text inside the image.

DIRECTOR_BLOCKING_SKETCH_LAYER:
[compact layer from references/style-and-negative.md]

STRICT_3X3_GEOMETRY:
[compact geometry hard words from references/style-and-negative.md]

ASSET_REFERENCE_LOCK:
Reference images are used only for identity silhouette, hairstyle silhouette, costume silhouette, prop shape, and prop ownership. Draw simplified director blocking sketch figures, not portrait renderings.

PROJECT_VISUAL_PROFILE:
PROJECT ERA / GENRE:
COSTUME SYSTEM:
CHARACTER PROFILE LOCKS:
PROP PROFILE LOCKS:
DRIFT GUARD:

SCENE_LAYER:
Page-level space and fixed geometry.

CAMERA_RULE_LAYER:
Page-level camera axis with A end, B end, camera side, forbidden side, screen left/right.

CONTINUITY_LAYER:
Fixed objects, continuity log positions, facing, prop state, reality layer, inherited/diverged states.

PANEL_1_MASTER_SPATIAL_LAYOUT_ANCHOR:
P01 source / override status. If override, include DRAWN CAMERA TAG and ANCHOR_VISIBLE_ALLOWED.

FIXED_OBJECT_SCREEN_PROJECTION:
Compact per-page/per-panel projection summary. Cropped fixed objects stay in original position.

FLOOR_PLANE_LOCK:
Allowed standing surface and forbidden standing zones.

ELEVATION_AND_DEPTH_LOCK:
Define upper/lower physical levels and distinguish screen lower/foreground from lower elevation.

CAMERA_COMPOSITION_LOCK:
Panel camera heights, directions, subject scales, dominant screen areas, and foreground/background.

PANEL_INHERITANCE_MAP:
How P02-P09 inherit P01 anchors; what may crop; what cannot move.

AXIS_AND_SHOULDER_LOCKS:
Concrete relation axes and shoulder/foreground/background locks.

OBJECT_VISIBILITY_AND_BOUNDARIES:
Page-level summary plus global no-drift boundaries. Do not replace per-panel VISIBLE ONLY.

SPLIT_COMPOSITION_DIFFERENCE_LOCK:
P01: unique composition task
...
P09: unique composition task

PROP_TEMPORAL_PHASE_LOCK:
One physical state per prop/effect per panel.

PANEL_LAYER P01-P09:

P01:
SOURCE SHOT:
MUST MATCH SHOT_DATA CAMERA TAG:
VISIBLE ONLY:
MUST NOT SHOW:
CHARACTER ANCHORS:
SCREEN POSITION / AXIS LOCK:
FLOOR / DEPTH LOCK:
CONTENT:

[Repeat P02-P09.]

NEGATIVE_CONSTRAINTS:
[compact negative constraints from references/style-and-negative.md]
```

## Compression Rules

- Keep full profiles, long continuity tables, and long checklists in `分析与锁定.md`.
- Keep mandatory spatial layers in `final_image_prompts.md`, but write them compactly.
- Panel `CHARACTER ANCHORS` use short visible-character anchors only.
- If a prop is not visible in a panel, the anchor must not invite it.
- Panel `SCREEN POSITION / AXIS LOCK` and `FLOOR / DEPTH LOCK` must be panel-specific, not repeated page text.
- `CONTENT` must be drawable action/composition only, not dialogue text or long source paragraphs.
- Do not write color function words directly; translate them to light/dark sketch values before final prompt.
