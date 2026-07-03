---
name: su-image9
description: Image2 9 宫格/3x3 导演草图式 blocking 分镜提示词独立技能。用于把参考图、资产图、俯视图、站位图、尾帧、剧本文字、文字版分镜、Markdown/Excel 表格、局部镜号或表格截图转写为 Image2/gpt-image-2 可复制提示词。默认生成 wide horizontal 16:9 canvas containing a clean 3x3 storyboard grid，9 个宫格全部为 horizontal 16:9 storyboard frames。1.6.0 将默认风格改为黑色铅笔导演草图，优先锁定构图、人物站位、连续性台账、摄影机视角、地面层级、物理合理性和道具时间状态；参考图只作为身份、发型轮廓、服装剪影、道具形状与归属锚点，不用于提高画面精细度。不得修改 su-fenjingskill-zh 主表、Prompt 列、Storyboard 列、Excel 或校验脚本。
---

# Image2 9 宫格导演草图分镜提示词

## 版本

<!-- skill-version: 1.6.0 -->

`su-image9` 是独立的 3x3 分镜提示词入口。它不转用 `su-image2-storyboard-grid-zh`，不修改 `su-fenjingskill-zh`，不回写主表、Prompt 列、Storyboard 列、Excel 或校验脚本。

1.6.0 的方向是导演草图式 blocking：先让空间、站位、轴线、构图、动作阶段和物理状态稳定，再考虑人物识别。不要把参考图、风格词或环境细节写成精修图、照片图或概念图。

## 必读 References

按任务读取，不把长规则堆进主文件：

- `references/style-and-negative.md`：`DIRECTOR_BLOCKING_SKETCH_LAYER`、严格 3x3 几何和通用负面约束。
- `references/asset-reference-contract.md`：参考图资产锚点合同，只锁外形、服装、道具，不提高精细度。
- `references/spatial-continuity-contract.md`：continuity、P01、固定物、地面层级、禁站区、构图锁、split 差异和道具时间状态。
- `references/output-templates.md`：`分析与锁定.md`、`final_image_prompts.md`、`panel_plan.json` 的 1.6.0 模板。
- `references/validation-checklists.md`：语义、跨字段、prompt、生图、标注/PDF 验收清单。

有 `shot_data.json`、已锁定镜号、参考图、要求生图/ZIP/PDF/标注图时，必须读取对应 reference。生图前必须运行 `scripts/validate_su_image9_prompt.py`。

## 核心边界

- 默认只输出 Markdown 提示词；只有用户明确要求“生图、批量生成、按 prompt 输出图片、ZIP”时才进入生图。
- 原始生图必须是 16:9 横版 3x3 九宫格，9 个 panel 都是 horizontal 16:9。
- 生图层永远无字：不得有页眉、镜号、三要素、字幕、倒计时数字、bpm、HR、监护仪 UI、标签、箭头或水印。
- 标注、页眉、`C序号｜视角｜景别｜运镜` 只能由后处理脚本加在图外标签区。
- 参考图只继承身份轮廓、发型轮廓、服装剪影、道具形状和归属；不得继承照片质感、皮肤细节、棚拍光、彩色、CG、厚涂、漫画或精修程度。
- 当前工具若无法真实绑定参考图，只能输出文字提示词或标注“未绑定参考图，人物映射风险高”；不得交付为正式参考图版生图。

## 稳定执行流程

1. **输入审查**
   - 判断是参考图/资产流程还是纯文字流程。
   - 若有角色图、道具图、场景图、站位图、尾帧或图片编号，先做资产用途和冲突审查。
   - 参考图未真实绑定但用户要求正式参考图版生图时，必须停止。

2. **来源读取**
   - 有 `shot_data.json` 时必须读取 `shots`、`continuity_logs`、`continuity_updates`、`visible_characters`、`visible_props`、`offscreen_characters` 和 `camera_main_image`。
   - `continuity_logs` 是空间、站位、固定物、地面层级、轴线和道具状态的优先来源；不得只用 Prompt 列或自然语言摘要替代。
   - 若 continuity 与用户本轮明确说明冲突，按用户本轮优先；冲突仍无法解决时停止。

3. **语义规划闸门**
   - 分页按连续空间、关系轴线、动作阶段、地面层级、道具状态和现实层切；不得只按镜头数量均衡切。
   - 每页必须有可继承的主空间锚点。跨空间、现实/幻境层级断裂、可站立面改变时必须拆页或明确过渡。
   - P01 必须是主空间锚定。若来源首镜是特写、近景、过肩、反应镜头、局部道具或黑场，P01 改写为空间锚定，来源镜头顺延到 P02-P09。
   - 同源 split 必须改变机位、景别、主体、空间关系、动作阶段、道具状态或前后层级；情绪微差异不算有效拆格。

4. **分析与锁定稿**
   - 完整档案和长表放入 `分析与锁定.md`：资产审查、profile、continuity、P01 锚定、固定物投影、地面层级、禁站区、panel 继承、轴线肩位、构图差异、道具时间状态、逐 panel 可见性和去重检查。
   - 该文件可详细；它不是生图输入。

5. **最终生图压缩稿**
   - `final_image_prompts.md` 是唯一允许用于 Image2 的正式输入；不得临场手写二次压缩 prompt 直接生图。
   - 每页目标 5,000-9,000 字符；任一页超过 12,000 字符必须停止并压缩。
   - 必须保留以下短层级，不能删：
     `DIRECTOR_BLOCKING_SKETCH_LAYER`、`ASSET_REFERENCE_LOCK`、`PROJECT_VISUAL_PROFILE`、`SCENE_LAYER`、`CAMERA_RULE_LAYER`、`CONTINUITY_LAYER`、`PANEL_1_MASTER_SPATIAL_LAYOUT_ANCHOR`、`FIXED_OBJECT_SCREEN_PROJECTION`、`FLOOR_PLANE_LOCK`、`ELEVATION_AND_DEPTH_LOCK`、`CAMERA_COMPOSITION_LOCK`、`PANEL_INHERITANCE_MAP`、`AXIS_AND_SHOULDER_LOCKS`、`OBJECT_VISIBILITY_AND_BOUNDARIES`、`SPLIT_COMPOSITION_DIFFERENCE_LOCK`、`PROP_TEMPORAL_PHASE_LOCK`、`PANEL_LAYER P01-P09`、`NEGATIVE_CONSTRAINTS`。
   - 色彩功能词进入 final prompt 前必须转为黑白草图词：红光=浅灰强光/亮脉冲，金黑雾=深灰暗雾/黑线团，不直接写彩色诱导词。

6. **生图前 validator**
   - 对有 `shot_data.json` 和 `panel_plan.json` 的正式稿，必须运行：
     `python skills/su-image9/scripts/validate_su_image9_prompt.py --shot-data <shot_data.json> --panel-plan <panel_plan.json> --final-prompts <final_image_prompts.md>`
   - 任一失败项存在，不得生图。

7. **生图与验收**
   - 只有用户明确要求生图才执行。
   - 原始无字图必须保留。任何图不通过九宫格、无字、导演草图风格、人物/道具、P01、地面层级、禁站区、可见性、轴线、构图差异或道具时间状态检查时，标记不合格并收紧 prompt，最多连续重生两次。

## Panel 硬字段

每个 panel 必须保留字段名：

```text
SOURCE SHOT:
MUST MATCH SHOT_DATA CAMERA TAG:
VISIBLE ONLY:
MUST NOT SHOW:
CHARACTER ANCHORS:
SCREEN POSITION / AXIS LOCK:
FLOOR / DEPTH LOCK:
CONTENT:
```

硬规则：

- `MUST MATCH SHOT_DATA CAMERA TAG` 必须来自 `camera_main_image` 开头方括号。P01 anchor override 时同时写来源 tag 和 `DRAWN CAMERA TAG: master wide/full spatial anchor`。
- P01 anchor override 不得沿用来源特写的单人 `VISIBLE ONLY`；必须单独写 `ANCHOR_VISIBLE_ALLOWED`。
- `VISIBLE ONLY` 不等于同场人物都可见。本格不可见角色不得作为远景小人、背影、阴影、倒影、轮廓或背景站位出现。
- `FLOOR / DEPTH LOCK` 必须说明人物脚底所在可站立面、不可站立区、上下层级和 foreground/lower screen 是否只是画面位置。
- 对话、过肩、反打、双人中景必须写 A/B 端、摄影机侧、screen left/right、肩位、前后层级和允许裁切。

## 人物、道具和防漂移

- 同页多名相似男性必须显式防串：顾成=西服/领带/短须，沈夜=深色长风衣/黑高领，林晓杰=黑皮衣/白衬衫/年轻/可半透明。
- 长棍只属于顾成，但只有 `visible_props=STAFF` 时才允许长棍；顾成可见但本格无 STAFF 时必须写 `no STAFF visible in this panel`。
- 手环只属于林晓彤。只允许裂痕、光点、不可读抽象脉冲；不得有倒计时数字、bpm、HR、监护仪 UI、网格数据、屏幕文字。
- 手环状态必须互斥：戴在手上、正在脱落、半空、落地、化灰不能在同一 panel 并存。
- 不得把不同雾体压成 `MIST/VFX`。必须区分 `GREY_LXJ_MIST`、`DARK_HOSTILE_MIST`、`LIGHT_DUST`、`BRACELET_PULSE`、`WHITE_LIGHT` 等来源状态。

## 输出合同

每个正式提示词任务至少输出：

1. `分析与锁定.md`
2. `final_image_prompts.md`
3. `panel_plan.json`

`panel_plan.json` 必须记录来源镜头、P01 override、floor plane、forbidden standing zone、camera composition、split composition delta、prop temporal state、可见性和逐格差异，供 validator 追踪。

## 失败条件

任一项失败，输出 `任务失败：su-image9 语义规划失败` 并停止：

- 未读取可用的 `continuity_logs` / `continuity_updates`。
- P01 非空间锚定，或 P01 anchor override 与可见性冲突。
- final prompt 缺少任一必需短层级。
- 缺少地面层级、禁站区、构图锁或道具时间状态。
- `VISIBLE ONLY`、`MUST NOT SHOW`、`CONTENT`、`CHARACTER ANCHORS` 互相打架。
- 同源 split 只有情绪微差异，没有可见构图差异。
- 关系镜头没有肩位、摄影机侧或具体 screen left/right。
- 道具归属诱导错误，例如无 STAFF 的顾成格仍邀请画长棍。
- 不同雾体、光尘或手环脉冲混用同一模糊 token。
- final prompt 出现精修参考、照片级参考、彩色光效诱导或参考图提高精细度的写法。
- `final_image_prompts.md` 任一页超过 12,000 字符。
- 生图前 validator 失败。

失败格式：

```text
任务失败：su-image9 语义规划失败
- 失败项：
- 依据：
- 建议下一步：
```
