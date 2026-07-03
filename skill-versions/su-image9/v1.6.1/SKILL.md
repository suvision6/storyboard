---
name: su-image9
description: Image2/gpt-image-2 9 宫格 3x3 黑白导演 blocking 草图提示词独立技能。v1.6.1 使用“长分析、短生图、强门禁”：分析稿和 panel_plan 可以完整，final_image_prompts.md 必须是 2,500-4,500 字符/页的 6 块短生图稿；validator 必须逐格比对 shot_data.json、panel_plan.json 和 final prompt。参考图只作为身份轮廓、发型轮廓、服装剪影、道具形状与归属锚点，不作为照片质感、精修脸或风格目标。不得修改 su-fenjingskill-zh 主表、Prompt 列、Storyboard 列、Excel 或校验脚本。
---

# Image2 9 宫格导演 blocking 草图提示词

## 版本

<!-- skill-version: 1.6.1 -->

`su-image9` 是独立的 3x3 分镜提示词入口。它不转用 `su-image2-storyboard-grid-zh`，不修改 `su-fenjingskill-zh`，不回写主表、Prompt 列、Storyboard 列、Excel 或校验脚本。

1.6.1 的核心修复是：分析可以长，生图必须短；门禁验事实，不验字段名；不允许手写二次压缩。保留 1.4.0 的统一风格层、1.4.2 的 P01 主空间锚定优先级、1.5.x/1.6.0 的分析稿与结构化计划分离方向；废弃 1.4.1 式逐格重复堆规则的 prompt 膨胀方向。

## 必读 References

按任务读取，不能把 reference 长规则照搬进 final prompt：

- `references/style-and-negative.md`：`STYLE_LOCK`、`CANVAS_LOCK`、`NEGATIVE_LOCK` 的短文本。
- `references/asset-reference-contract.md`：参考图资产锚点合同，只锁外形、服装、道具归属，不提高精细度。
- `references/spatial-continuity-contract.md`：P01、地面、禁站区、具体轴线、split 与道具时间状态如何进入 `panel_plan.json` 和短 panel 任务。
- `references/output-templates.md`：`分析与锁定.md`、`final_image_prompts.md`、`panel_plan.json`、`generation_manifest.json` 的 1.6.1 模板。
- `references/validation-checklists.md`：语义、事实门禁、生图和标注/PDF 验收清单。

有 `shot_data.json`、已锁定镜号、参考图、要求生图/ZIP/PDF/标注图时，必须读取对应 reference。生图前必须运行 `scripts/validate_su_image9_prompt.py`。

## 核心边界

- 默认只输出 prompt 包；只有用户明确要求“生图、批量生成、按 prompt 输出图片、ZIP”时才进入生图。
- 原始生图必须是 wide horizontal 16:9 canvas，clean 3x3 grid，9 个 panel 都是 horizontal 16:9 storyboard frame。
- 生图层永远无字：不得有页眉、镜号、三要素、字幕、倒计时数字、bpm、HR、ECG、监护仪 UI、标签、箭头或水印。
- 标注、页眉、`C序号｜视角｜景别｜运镜` 只能由后处理脚本加在图外标签区。
- 参考图只继承身份轮廓、发型轮廓、服装剪影、道具形状和归属；不得继承照片质感、皮肤细节、棚拍光、彩色、CG、厚涂、漫画、精修程度或真人脸相似。
- `reference_binding_status=prompt_only` 时，不得进入正式参考图生图流程；只能输出 prompt 包或明确标注“未绑定参考图，人物映射风险高”。

## 稳定执行流程

1. **输入审查**
   - 判断是参考图/资产流程还是纯文字流程。
   - 若有角色图、道具图、场景图、站位图、尾帧或图片编号，先做资产用途和冲突审查。
   - 若用户要求正式参考图版生图，必须确认参考图已真实绑定；否则停止。

2. **来源读取**
   - 有 `shot_data.json` 时必须读取 `shots`、`continuity_logs`、`continuity_updates`、`visible_characters`、`visible_props`、`offscreen_characters` 和 `camera_main_image`。
   - `continuity_logs` 是空间、固定物、站位、地面层级、轴线、现实层和道具状态的优先来源；不得只用 Prompt 列或自然语言摘要替代。

3. **语义规划闸门**
   - 分页按连续空间、关系轴线、动作阶段、地面层级、道具状态和现实层切；不得只按镜头数量均衡切。
   - P01 必须是主空间锚定。若来源首镜是特写、近景、过肩、反应镜头、局部道具或黑场，P01 改写为空间锚定，来源镜头事实保留在 `SOURCE SHOT` 和 `MUST MATCH SHOT_DATA CAMERA TAG`。
   - P01 anchor override 的可见性必须服务空间锚定，不能继承来源特写的单人 `VISIBLE ONLY`。
   - 同源 split 必须改变机位、景别、主体、空间关系、动作阶段、道具状态或前后层级；情绪微差异不算有效拆格。

4. **分析与锁定稿**
   - 完整审查、人物/道具 profile、continuity、固定物投影、P01 锚定、轴线、split 差异、逐格可见性和失败原因放入 `分析与锁定.md`。
   - 该文件可以长；它不是生图输入。

5. **结构化计划**
   - `panel_plan.json` 是 validator 的事实源，必须记录 root `reference_binding_status`、`forbidden_prompt_tokens`，以及每格 `source_camera_tag`、`drawn_camera_tag`、`p01_anchor_override`、`anchor_visible_allowed`、`screen_left_right_lock`、`axis_endpoint_a/b`、`visible_characters`、`visible_props`、`prop_temporal_state`、地面和禁站区。

6. **最终短生图稿**
   - `final_image_prompts.md` 是唯一允许用于 Image2 的正式输入；不得临场手写二次压缩 prompt 直接生图。
   - 每页目标 2,500-4,500 字符；超过 5,000 字符必须停止。
   - 每页只保留 6 块，且顺序固定：`STYLE_LOCK`、`CANVAS_LOCK`、`REFERENCE_LOCK`、`CONTINUITY_LOCK`、`PANEL_TASKS P01-P09`、`NEGATIVE_LOCK`。
   - 禁止旧 1.6.0 多层审查块进入 final prompt：`PROJECT_VISUAL_PROFILE`、`SCENE_LAYER`、`CAMERA_RULE_LAYER`、`FIXED_OBJECT_SCREEN_PROJECTION`、`ELEVATION_AND_DEPTH_LOCK`、`CAMERA_COMPOSITION_LOCK`、`OBJECT_VISIBILITY_AND_BOUNDARIES`、`SPLIT_COMPOSITION_DIFFERENCE_LOCK`、`PROP_TEMPORAL_PHASE_LOCK` 等只能留在分析稿或 `panel_plan.json`。
   - 禁止占位句：`page A/B`、`foreground/background/shoulder locked`、`as applicable`、`allowed positions`、`fixed objects`、`source action phase`、`source camera tag`。
   - 色彩功能词进入 final prompt 前必须转为黑白草图词：红光/赤光=light gray pulse，金黑雾=dark mist mass，金色纹路=pale line glow；不得直接写红、金、gold、red。
   - 倒计时、数字、bpm、HR、ECG、监护仪 UI、readable digits 不得进入 final prompt；手环只能写 non-readable pulse/crack/rhythm mark。

7. **生图前 validator**
   - 对有 `shot_data.json` 和 `panel_plan.json` 的正式稿，必须运行：
     `python skills/su-image9/scripts/validate_su_image9_prompt.py --shot-data <shot_data.json> --panel-plan <panel_plan.json> --final-prompts <final_image_prompts.md>`
   - 进入生图时还必须提供或生成 `generation_manifest.json`，记录是否原文使用 prompt、是否真实绑定参考图、每页图片路径和风格一致性验收。
   - 任一失败项存在，不得生图。

8. **生图与验收**
   - 原始无字图必须保留。
   - 多页或 P01-P04 连续生图必须使用完全相同的 `STYLE_LOCK` 和 `NEGATIVE_LOCK`。
   - 若工具支持风格参考图，先生成 style calibration sheet；若不支持，至少不得逐页改写风格块。
   - 任一图不通过九宫格、无字、统一黑白导演草图、低细节脸、人物/道具归属、P01、地面层级、禁站区、可见性、轴线、split 差异或道具时间状态检查时，标记不合格并收紧 prompt，最多连续重生两次。

## Panel 短字段

每个 panel 在 `PANEL_TASKS P01-P09` 中必须保留字段名：

```text
SOURCE SHOT:
MUST MATCH SHOT_DATA CAMERA TAG:
DRAWN CAMERA TAG:        # 仅 P01 anchor override 必填
VISIBLE ONLY:
ACTION / COMPOSITION:
FLOOR / AXIS DELTA:
PROP STATE:
```

硬规则：

- `SOURCE SHOT` 必须和 `panel_plan.json` 的 `source_shot` 一致。
- `MUST MATCH SHOT_DATA CAMERA TAG` 必须和 `shot_data.json` 中对应镜头 `camera_main_image` 的开头方括号完全一致。
- P01 anchor override 仍要保留来源 camera tag，同时单独写 `DRAWN CAMERA TAG: master wide/full spatial anchor`。
- `VISIBLE ONLY` 必须和 `panel_plan.json` 对齐；P01 anchor override 使用 `anchor_visible_allowed`，不得沿用来源特写的单人可见性。
- `FLOOR / AXIS DELTA` 必须具体写 A/B 端、camera side、screen left/right、foreground/background；关系镜头必须写 shoulder。
- `PROP STATE` 必须和本格 visible props 对齐，且手环、长棍、雾体等时间状态互斥。

## 失败条件

任一项失败，输出 `任务失败：su-image9 语义规划失败` 并停止：

- 未读取可用的 `continuity_logs` / `continuity_updates`。
- `final_image_prompts.md` 缺少 6 块之一、出现旧 1.6.0 审查层、任一页超过 5,000 字符。
- 生成前没有通过 `validate_su_image9_prompt.py`。
- P01 非空间锚定，或 P01 anchor override 沿用来源特写的单人可见性。
- `SOURCE SHOT`、camera tag、可见人物、可见道具、道具状态与 `shot_data.json` / `panel_plan.json` 不一致。
- 轴线、地面、禁站区、split 差异或道具状态是占位句。
- `reference_binding_status=prompt_only` 却进入正式参考图生图。
- final prompt 出现倒计时、可读数字、UI、红/金色彩词、照片级参考、真人脸相似或精修参考。
- 生图使用的不是 final prompt 原文，或没有 `generation_manifest.json`。

失败格式：

```text
任务失败：su-image9 语义规划失败
- 失败项：
- 依据：
- 建议下一步：
```
