---
name: su-image9
description: Image2 9 宫格/3x3 黑白分镜提示词独立技能。用于把参考图、资产图、俯视图、站位图、尾帧、剧本文字、文字版分镜、Markdown/Excel 表格、局部镜号或表格截图转写为 Image2/gpt-image-2 可复制提示词。默认生成 wide horizontal 16:9 canvas containing a clean 3x3 storyboard grid，9 个宫格全部为 horizontal 16:9 storyboard frames。1.5.1 恢复稳定流程：强制读取 continuity、P01 主锚定、固定物投影、panel 继承、轴线肩位、逐格差异、跨字段 validator；继续保留 final_image_prompts.md 压缩稿和参考图真实绑定门槛。不得修改 su-fenjingskill-zh 主表、Prompt 列、Storyboard 列、Excel 或校验脚本。
---

# Image2 9 宫格分镜提示词独立技能

## 版本

<!-- skill-version: 1.5.1 -->

`su-image9` 是独立的 3x3 黑白石墨分镜提示词入口。它不转用 `su-image2-storyboard-grid-zh`，不修改 `su-fenjingskill-zh`，不回写主表、Prompt 列、Storyboard 列、Excel 或校验脚本。

1.5.1 修复 1.5.0 的退化：压缩稿仍必须存在，但不得压掉连续性台账、P01 空间锚定、固定物投影、panel 继承、轴线肩位和逐格差异任务。长度合格不代表语义合格；validator 未通过不得生图。

## 必读 References

按任务读取，不把长规则堆进主文件：

- `references/style-and-negative.md`：完整 `SYSTEM_STYLE_LAYER`、通用 `NEGATIVE_CONSTRAINTS`、严格 3x3 几何硬词。
- `references/spatial-continuity-contract.md`：continuity、P01 anchor、固定物投影、panel 继承、轴线肩位、split 去重和命名规则。
- `references/output-templates.md`：`分析与锁定.md`、`final_image_prompts.md`、`panel_plan.json` 的 1.5.1 模板。
- `references/validation-checklists.md`：语义、跨字段、prompt、生图、标注/PDF 验收清单。

有 `shot_data.json`、已锁定镜号、参考图、要求生图/ZIP/PDF/标注图时，必须读取对应 reference。生图前还必须运行 `scripts/validate_su_image9_prompt.py`。

## 核心边界

- 默认只输出 Markdown 提示词；只有用户明确要求“生图、批量生成、按 prompt 输出图片、ZIP”时才进入生图。
- 每张原始图必须是 wide horizontal 16:9 canvas containing a clean 3x3 storyboard grid；9 个 panel 全部为 horizontal 16:9。
- Image2 生图层永远无字：不得生成页眉、镜号、三要素、`C序号`、字幕、倒计时数字、bpm、HR、监护仪 UI、标签、箭头或水印。
- 标注、页眉、`C序号｜视角｜景别｜运镜` 只能由后处理脚本加在图外标签区。
- 参考图只继承身份、服装轮廓、发型轮廓、道具形状、道具归属、空间事实；不得继承照片、彩色、棚拍光、写实皮肤、CG、厚涂、漫画或 AI 渲染风格。
- 当前工具若无法真实绑定参考图，只能输出文字提示词或标注“未绑定参考图，人物映射风险高”；不得交付为正式参考图版生图。

## 稳定执行流程

1. **输入审查**
   - 判断是参考图/资产流程还是纯文字流程。
   - 若有角色图、道具图、场景图、站位图、尾帧或图片编号，先做资产用途和冲突审查。
   - 参考图未真实绑定但用户要求正式参考图版生图时，必须停止。

2. **来源读取**
   - 有 `shot_data.json` 时必须读取 `shots`、`continuity_logs`、`continuity_updates`、`visible_characters`、`visible_props` 和 `camera_main_image`。
   - `continuity_logs` 是空间、站位、固定物和轴线的优先来源；不得只用 Prompt 列或自然语言摘要替代。
   - 若 continuity 与用户本轮明确说明冲突，按用户本轮优先；冲突仍无法解决时停止。

3. **语义规划闸门**
   - 分页按连续空间、关系轴线、动作阶段、道具状态和情绪转折，不得只按镜头数量均衡切。
   - 每页必须有一个可继承的主空间锚点；跨空间、现实/幻境层级断裂时必须拆页。
   - Panel 1 必须是主平面锚定。若来源首镜是特写、近景、过肩或反应镜头，P01 改写为空间锚定，来源镜头顺延到 P02-P09。
   - 不得硬凑 9 格。同源 split 必须拆成不同动作阶段、道具状态、反应、空间关系或结果；同源同句重复直接失败。

4. **分析与锁定稿**
   - 完整档案和长表放入 `分析与锁定.md`：资产审查、profile、continuity、P01 锚定、固定物屏幕投影、panel 继承、轴线肩位、逐格差异、逐 panel 可见性、九格取舍、去重检查。
   - 该文件可详细；它不是生图输入。

5. **最终生图压缩稿**
   - `final_image_prompts.md` 是唯一允许用于 Image2 的正式输入。
   - 每页目标 7,000-11,000 字符；任一页超过 12,000 字符必须停止并压缩。
   - 必须保留以下短层级，不能删：
     `SYSTEM_STYLE_LAYER`、`PROFILE_SOURCE_AND_PRECEDENCE`、`PROJECT_VISUAL_PROFILE`、`SCENE_LAYER`、`CAMERA_RULE_LAYER`、`CONTINUITY_LAYER`、`PANEL_1_MASTER_SPATIAL_LAYOUT_ANCHOR`、`FIXED_OBJECT_SCREEN_PROJECTION`、`PANEL_INHERITANCE_MAP`、`AXIS_AND_SHOULDER_LOCKS`、`OBJECT_VISIBILITY_AND_BOUNDARIES`、`PANEL_DIFFERENCE_TASKS`、`PANEL_LAYER P01-P09`、`NEGATIVE_CONSTRAINTS`。

6. **生图前 validator**
   - 对有 `shot_data.json` 和 `panel_plan.json` 的正式稿，必须运行：
     `python skills/su-image9/scripts/validate_su_image9_prompt.py --shot-data <shot_data.json> --panel-plan <panel_plan.json> --final-prompts <final_image_prompts.md>`
   - 任一失败项存在，不得生图。

7. **生图与验收**
   - 只有用户明确要求生图才执行。
   - 原始无字图必须保留。任何图不通过几何、无字、风格、人物/道具、P01、可见性、轴线检查时，标记不合格并收紧 prompt，最多连续重生两次。

## Profile 合同

`PROJECT_VISUAL_PROFILE` 位于 `SYSTEM_STYLE_LAYER` 之后、`SCENE_LAYER` 之前。它只锁当前任务的题材时代、服装体系、人物外观、道具归属和禁漂移方向，不得写成技能全局默认。

来源优先级：

1. 用户本轮明确说明。
2. 参考图、角色资产、道具资产、场景资产。
3. 项目文档、角色设定、连续性资料。
4. `shot_data.json`、`continuity_logs`、`continuity_updates`、主表连续性。
5. 模型基于剧情的弱推断。

完整人物/道具档案只放 `分析与锁定.md`；`final_image_prompts.md` 每页只写一次压缩 profile；Panel 内只写可见角色短锚点。

## Panel 硬字段

每个 panel 必须保留字段名：

```text
SOURCE SHOT:
MUST MATCH SHOT_DATA CAMERA TAG:
VISIBLE ONLY:
MUST NOT SHOW:
CHARACTER ANCHORS:
SCREEN POSITION / AXIS LOCK:
CONTENT:
```

硬规则：

- `MUST MATCH SHOT_DATA CAMERA TAG` 必须来自 `camera_main_image` 开头方括号。P01 anchor override 时同时写来源 tag 和 `DRAWN CAMERA TAG: master wide/full spatial anchor`。
- P01 anchor override 不得沿用来源特写的单人 `VISIBLE ONLY`。必须单独写 `ANCHOR_VISIBLE_ALLOWED`，只允许已出现且用于建立空间的角色/道具。
- `VISIBLE ONLY` 不等于同场人物都可见。本格不可见角色不得作为远景小人、背影、阴影、倒影、轮廓或背景站位出现。
- `VISIBLE ONLY`、`MUST NOT SHOW`、`CHARACTER ANCHORS`、`CONTENT` 不得互相冲突。
- 对话、过肩、反打、双人中景必须写 A/B 端、摄影机侧、screen left/right、肩位、前后层级和允许裁切。

## 人物、道具、命名防漂移

- 同页多名相似男性必须显式防串：顾成=西服/领带/短须，沈夜=深色长风衣/黑高领，林晓杰=黑皮衣/白衬衫/年轻/可半透明。
- 长棍只属于顾成，但不能把“长棍唯一主人”写成每格都画长棍。只有 `visible_props=STAFF` 时才允许长棍；顾成可见但本格无 STAFF 时必须写 `no STAFF visible in this panel`。
- 手环只属于林晓彤。只允许裂痕、光点、不可读抽象脉冲；不得有倒计时数字、bpm、HR、监护仪 UI、网格数据、屏幕文字。
- 不得把不同雾体压成 `MIST/VFX`。必须区分 `GREY_LXJ_MIST`、`GOLD_BLACK_MIST`、`LIGHT_DUST`、`BRACELET_PULSE`、`WHITE_LIGHT` 等来源状态。
- 道具或 VFX 的时代/风格例外不得反向改变人物服装、发型或场景时代。

## 输出合同

每个正式提示词任务至少输出：

1. `分析与锁定.md`
2. `final_image_prompts.md`

建议同时输出 `panel_plan.json`，供 validator 追踪来源镜头、P01 override、split phase、可见性和逐格差异。

## 失败条件

任一项失败，输出 `任务失败：su-image9 语义规划失败` 并停止：

- 未读取可用的 `continuity_logs` / `continuity_updates`。
- P01 非空间锚定，或 P01 anchor override 与可见性冲突。
- final prompt 缺少任一必需短层级。
- `VISIBLE ONLY`、`MUST NOT SHOW`、`CONTENT`、`CHARACTER ANCHORS` 互相打架。
- 同源 split 没有不同视觉任务。
- 关系镜头没有肩位、摄影机侧或具体 screen left/right。
- 道具归属诱导错误，例如无 STAFF 的顾成格仍邀请画长棍。
- 灰白雾气、金黑雾体、光尘、手环脉冲混用同一模糊 token。
- `final_image_prompts.md` 任一页超过 12,000 字符。
- 生图前 validator 失败。

失败格式：

```text
任务失败：su-image9 语义规划失败
- 失败项：
- 依据：
- 建议下一步：
```
