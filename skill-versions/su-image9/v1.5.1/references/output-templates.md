# su-image9 Output Templates

Use this file when creating deliverables. The analysis draft may be detailed; `final_image_prompts.md` must be compressed but still carry the spatial hard layers.

## Required Files

- `分析与锁定.md`
- `final_image_prompts.md`
- `panel_plan.json` when source shots are traceable

Generated images belong under `outputs/YYYY-MM-DD/images/` only after validator passes and the user explicitly requests image generation.

## 分析与锁定.md Template

```markdown
# SU-IMAGE9｜分析与锁定

## 基本信息

| 项目 | 内容 |
|---|---|
| 技能 | su-image9 |
| 版本 | 1.5.1 |
| 来源 | shot_data / continuity_logs / references / text |
| 输出 | 分析稿 + final_image_prompts.md + panel_plan.json |
| 是否生图 | 是/否 |
| 参考图绑定状态 | bound / not bound / prompt-only |

## 参考资产与来源优先级

| 资产 | 对象 | 用途 | 冲突状态 |
|---|---|---|---|

## PROJECT_VISUAL_PROFILE

| 对象 | 身份/轮廓 | 道具归属 | 状态变化 | 禁止互换 |
|---|---|---|---|---|

## CONTINUITY_LAYER 草案

| 页 | 来源场景 | 固定物 | 起点/朝向 | 道具状态 | 现实层 |
|---|---|---|---|---|---|

## P01 主锚定表

| Page | P01 类型 | 来源镜号 | DRAWN CAMERA TAG | ANCHOR_VISIBLE_ALLOWED | 不可新增 |
|---|---|---:|---|---|---|

## 固定物屏幕投影表

| Page | Panel | 固定物 | 屏幕投影/裁切 | 禁止漂移 |
|---|---:|---|---|---|

## Panel 继承与逐格差异表

| Page | Panel | 来源镜号 | 继承 P01 哪些锚点 | 唯一视觉任务 | split 是否不同 |
|---|---:|---:|---|---|---|

## 轴线与肩位表

| Page | Panel | A端 | B端 | 摄影机侧 | screen left/right | 肩位/前后层级 |
|---|---:|---|---|---|---|---|

## 逐Panel可见性排除表

| Page | Panel | VISIBLE ONLY | MUST NOT SHOW | 跨字段风险 |
|---|---:|---|---|---|

## 输出前校验

| 项目 | 结果 | 说明 |
|---|---|---|
```

## panel_plan.json Minimum Shape

```json
{
  "skill": "su-image9",
  "version": "1.5.1",
  "source": "shot_data path",
  "reference_binding_status": "bound | not_bound | prompt_only",
  "pages": [
    {
      "page": "P01",
      "title": "page title",
      "shots": [1, 2, 3],
      "space": "page space",
      "axis": "page axis",
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
          "axis_lock": ""
        }
      ]
    }
  ]
}
```

## final_image_prompts.md Template

Each page must be 7,000-11,000 characters. Stop if any page exceeds 12,000 characters.

```text
DELIVERABLE:
Generate one wide horizontal 16:9 canvas containing a clean 3x3 storyboard grid. Image-only, no text inside the image.

SYSTEM_STYLE_LAYER:
[compact style layer from references/style-and-negative.md]

STRICT_3X3_GEOMETRY:
[compact geometry hard words from references/style-and-negative.md]

PROFILE_SOURCE_AND_PRECEDENCE:
Current profile derived from: user instruction / reference assets / project docs / shot_data continuity / inference.
Conflict status:
Reference binding status:

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

PANEL_INHERITANCE_MAP:
How P02-P09 inherit P01 anchors; what may crop; what cannot move.

AXIS_AND_SHOULDER_LOCKS:
Concrete relation axes and shoulder/foreground/background locks.

OBJECT_VISIBILITY_AND_BOUNDARIES:
Page-level summary plus global no-drift boundaries. Do not replace per-panel VISIBLE ONLY.

PANEL_DIFFERENCE_TASKS:
P01: unique task
...
P09: unique task

PANEL_LAYER P01-P09:

P01:
SOURCE SHOT:
MUST MATCH SHOT_DATA CAMERA TAG:
VISIBLE ONLY:
MUST NOT SHOW:
CHARACTER ANCHORS:
SCREEN POSITION / AXIS LOCK:
CONTENT:

[Repeat P02-P09.]

NEGATIVE_CONSTRAINTS:
[compact negative constraints from references/style-and-negative.md]
```

## Compression Rules

- Keep full profiles, long continuity tables, and long checklists in `分析与锁定.md`.
- Keep the mandatory continuity and spatial layers in `final_image_prompts.md`, but write them compactly.
- Panel `CHARACTER ANCHORS` use short visible-character anchors only.
- If a prop is not visible in a panel, the anchor must not invite it.
- Panel `SCREEN POSITION / AXIS LOCK` must be panel-specific, not a repeated page-long axis.
- `CONTENT` must be drawable action/composition only, not dialogue text or long source paragraphs.
