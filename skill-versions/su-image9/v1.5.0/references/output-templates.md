# su-image9 Output Templates

Use this file when creating deliverables. The analysis draft may be detailed; the final image prompt must be compressed and auditable.

## Required Files

For every formal prompt delivery:

- `分析与锁定.md`
- `final_image_prompts.md`

Optional:

- `panel_plan.json`
- generated images under `outputs/YYYY-MM-DD/images/`
- annotated review images/PDF only after original no-text images pass review

## 分析与锁定.md Template

```markdown
# SU-IMAGE9｜分析与锁定

## 基本信息

| 项目 | 内容 |
|---|---|
| 技能 | su-image9 |
| 版本 | 1.5.0 |
| 来源 | shot_data / markdown / references |
| 输出 | 分析稿 + final_image_prompts.md |
| 是否生图 | 是/否 |

## 参考资产与来源优先级

| 资产 | 对象 | 用途 | 冲突状态 |
|---|---|---|---|

## PROJECT_VISUAL_PROFILE

| 对象 | 身份/轮廓 | 道具归属 | 状态变化 | 禁止互换 |
|---|---|---|---|---|

## 空间与轴线

| 页 | 空间锚点 | A端 | B端 | 摄影机允许侧 | screen left/right |
|---|---|---|---|---|---|

## 九格取舍表

| Page | Panel | 来源镜号 | 三要素 | 可见对象 | 视觉任务 | 取舍理由 |
|---|---:|---:|---|---|---|---|

## 逐Panel可见性排除表

| Page | Panel | VISIBLE ONLY | MUST NOT SHOW | 风险 |
|---|---:|---|---|---|

## 输出前校验

| 项目 | 结果 | 说明 |
|---|---|---|
```

## final_image_prompts.md Template

Each page must be 7,000-11,000 characters. Stop if any page exceeds 12,000 characters.

```text
DELIVERABLE:
Generate one wide horizontal 16:9 canvas containing a clean 3x3 storyboard grid. Image-only, no text inside the image.

SYSTEM_STYLE_LAYER:
[Insert compact style layer from references/style-and-negative.md]

PROFILE_SOURCE_AND_PRECEDENCE:
Current profile derived from: user instruction / reference assets / project docs / shot_data continuity / inference.
Conflict status: no conflict.
Reference binding status: bound / not bound. If not bound, state mapping risk.

PROJECT_VISUAL_PROFILE:
PROJECT ERA / GENRE:
COSTUME SYSTEM:
CHARACTER PROFILE LOCKS: one compact line per recurring character.
PROP PROFILE LOCKS: one compact line per recurring prop.
DRIFT GUARD:

SCENE_LAYER:
Page-level space, fixed geometry, Panel 1 inheritance, allowed movement, forbidden redesign.

CAMERA_RULE_LAYER:
Page-level axis. Include A end, B end, camera side, screen left/right. Do not rely only on "do not cross axis".

OBJECT_VISIBILITY_AND_BOUNDARIES:
Page-level summary only. Do not duplicate every panel's full VISIBLE ONLY / MUST NOT SHOW table.

PANEL_LAYER P01-P09:

P01:
SOURCE SHOT:
MUST MATCH SHOT_DATA CAMERA TAG:
VISIBLE ONLY:
MUST NOT SHOW:
CHARACTER ANCHORS:
SCREEN POSITION / AXIS LOCK:
CONTENT:

[Repeat P02-P09 with short fields.]

NEGATIVE_CONSTRAINTS:
[Insert compact negative constraints from references/style-and-negative.md]
```

## Compression Rules

- Full character and prop profiles live in `分析与锁定.md`; `final_image_prompts.md` uses compact profile once per page.
- Panel `CHARACTER ANCHORS` use short codes and anti-swap clauses.
- Panel `SCREEN POSITION / AXIS LOCK` writes only panel-specific left/right, shoulder side, foreground/background, crop, or push-in.
- Panel `MUST NOT SHOW` lists only the most dangerous forbidden objects for that panel.
- General no-text, no-UI, style, geometry, and rendering negatives live only in `NEGATIVE_CONSTRAINTS`.
- Dialogue is converted to facial expression, posture, eyeline, and action. Do not paste dialogue text into image prompts.
