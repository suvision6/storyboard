---
name: su-image9
description: Image2 9 宫格/3x3 黑白分镜提示词独立技能。用于把参考图、资产图、俯视图、站位图、尾帧、剧本文字、文字版分镜、Markdown/Excel 表格、局部镜号或表格截图转写为 Image2/gpt-image-2 可复制提示词。默认生成 wide horizontal 16:9 canvas containing a clean 3x3 storyboard grid，9 个宫格全部为 horizontal 16:9 storyboard frames。1.5.0 起强制区分“分析与锁定稿”和“final_image_prompts.md 最终生图压缩稿”，防止超长 prompt、人物/道具串位、轴线漂移和未绑定参考图冒充参考图生图。不得修改 su-fenjingskill-zh 主表、Prompt 列、Storyboard 列、Excel 或校验脚本。
---

# Image2 9 宫格分镜提示词独立技能

## 版本

<!-- skill-version: 1.5.0 -->

`su-image9` 是 3x3 九宫格黑白石墨分镜提示词独立入口。它不转用 `su-image2-storyboard-grid-zh`，不修改 `su-fenjingskill-zh`，不回写主表、Prompt 列、Storyboard 列、Excel 或校验脚本。

1.5.0 重构目标：保留必要规则，删除重复规则，强制生成可审计的最终生图压缩稿。正式生图前必须存在 `final_image_prompts.md`；不得临场手写压缩 prompt 直接生图。

## 必读 References

按任务需要读取以下文件，避免把长规则全部塞入主上下文：

- `references/style-and-negative.md`：完整 `SYSTEM_STYLE_LAYER`、通用 `NEGATIVE_CONSTRAINTS`、3x3 几何硬词。
- `references/output-templates.md`：`分析与锁定.md` 与 `final_image_prompts.md` 模板。
- `references/validation-checklists.md`：语义、风格、生图、标注/PDF 验收清单。

当用户要求生图、ZIP、PDF、标注图、批量生成，或输出最终可复制 prompt 时，必须读取对应 reference。

## 核心边界

- 只生成独立的 3x3 九宫格提示词或基于这些提示词的图片交付；不改变主分镜合同。
- 每张原始 Image2 图必须是 wide horizontal 16:9 canvas containing a clean 3x3 storyboard grid，9 个 panel 全部为 horizontal 16:9。
- 默认只输出 Markdown 提示词文件；只有用户明确要求“生图、批量生成、按 Markdown 生成图片、输出 ZIP”时才进入生图流程。
- Image2 生成层永远无字：不得让模型生成页眉、镜号、三要素、`C序号`、字幕、倒计时数字、bpm、HR、监护仪 UI、标签、箭头或水印。
- 标注、页眉、`C序号｜视角｜景别｜运镜` 只能由后处理脚本在图外标签区添加，不能写进 Image2 生图块。
- 参考图只继承角色身份、服装轮廓、发型轮廓、道具形状、道具归属、空间事实；不得继承照片、彩色、棚拍光、写实皮肤、CG、厚涂、漫画或 AI 渲染风格。
- 如果当前工具无法把参考图作为真实图像输入绑定，只能生成文字提示词或明确标注“未绑定参考图，人物映射风险高”；不得交付为正式参考图版生图。

## 输入分流

### 参考图/资产输入

出现角色图、道具图、场景图、俯视图、站位图、机位图、尾帧、上一镜输出图、图片编号或资产路径时，按参考图流程执行：

1. 先做资产/空间一致性审查。
2. 生成 `PROFILE_SOURCE_AND_PRECEDENCE` 和 `PROJECT_VISUAL_PROFILE`。
3. 把参考图转写为可执行内容锁：身份、服装、发型、道具、站位、空间事实。
4. 剥离参考图风格，只继承内容。

以下情况必须停止并输出失败原因：图文空间冲突、道具归属冲突、同名角色多套不可兼容服装、参考图风格无法剥离、参考图未真实绑定但用户要求正式参考图版生图。

### 纯文字输入

只有剧本文字、文字版分镜、Markdown/Excel 表格、局部镜号或表格截图时，按纯文字流程执行。不得因为无图而要求用户补图；不得新增来源没有的人物、道具、空间、动作结果或对白。

## Profile 合同

`PROJECT_VISUAL_PROFILE` 是项目级内容锁定层，必须位于 `SYSTEM_STYLE_LAYER` 之后、`SCENE_LAYER` 之前。它只写当前任务的题材时代、服装体系、角色外观、道具归属和禁漂移方向，不得写成技能全局默认。

来源优先级固定：

1. 用户本轮明确说明。
2. 参考图、角色资产、道具资产、场景资产。
3. 项目文档、角色设定、连续性资料。
4. `shot_data.json`、`continuity_logs`、`continuity_updates` 和主表连续性。
5. 模型基于剧情的弱推断。

Profile 必须包含：

- `PROJECT ERA / GENRE`
- `COSTUME SYSTEM`
- `CHARACTER PROFILE LOCKS`
- `PROP PROFILE LOCKS`
- `DRIFT GUARD`

人物档案和道具档案的完整表只放在 `分析与锁定.md`。`final_image_prompts.md` 中每页只写一次压缩 profile。Panel 内只能使用短锚点。

## 九格分页与 Panel 规则

- 每页固定 9 个 panel。来源镜头多于 9 个时按空间、动作、道具、情绪、收尾取舍；来源镜头少于 9 个时只能拆分来源镜头内的动作阶段、道具状态、反应、空间关系，不得新增剧情事实。
- Panel 1 必须是主平面锚定。若来源首镜是特写、近景、过肩或反应镜头，P01 必须改写为空间全景锚定，并记录来源首镜顺延到 P02-P09。
- 后续 panel 只能继承、裁切、推进、反打、俯拍或侧拍 P01 空间，不得重新布置房间、洞窟、道路、车辆、门窗、家具或固定物位置。
- 每个 panel 必须保留固定字段名：`SOURCE SHOT`、`MUST MATCH SHOT_DATA CAMERA TAG`、`VISIBLE ONLY`、`MUST NOT SHOW`、`CHARACTER ANCHORS`、`SCREEN POSITION / AXIS LOCK`、`CONTENT`。
- `MUST MATCH SHOT_DATA CAMERA TAG` 必须来自 `shot_data.json` 的 `camera_main_image` 开头方括号。P01 anchor override 时同时记录来源三要素和实际绘制全景锚定。
- `VISIBLE ONLY` 不等于同场人物都可见；本格不可见角色不得作为远景小人、背影、阴影、倒影、轮廓或背景站位出现。

## 短锚点与防串规则

`CHARACTER ANCHORS` 每格只写可见角色短锚点，不重复完整 profile。格式示例：

```text
LX: white blouse, light jeans, bracelet owner, screen right; not Shen Ye/Gu Cheng.
SY: dark trench coat, black turtleneck, screen left; no staff, not Gu Cheng suit.
GC: beige suit, tie, stubble, staff owner; not Shen Ye trench coat.
LXJ: black leather jacket, white shirt, young, translucent if source says; not Shen Ye/Gu Cheng.
```

同页多名相似男性时必须显式防串：

- 顾成：西服、衬衫、领带、短须、长棍唯一持有者；不得变沈夜风衣。
- 沈夜：深色长风衣、黑高领；不得持长棍，不得穿顾成西服。
- 林晓杰：黑皮衣、白衬衫、年轻、可半透明；不得变沈夜风衣或顾成西服。

道具短锚点必须写归属者。长棍只属于顾成；手环只属于林晓彤。若道具本身具有另一时代或风格，只能作为道具例外，不得把人物服装、发型或场景整体带向该道具的时代/风格。

手环页只允许裂痕、脉冲、不可读抽象节奏线或光点；不得有倒计时数字、bpm、HR、监护仪 UI、网格数据、屏幕文字。

## 轴线与空间锁定

关系镜头、对话、正反打、过肩、反应近景、车内外关系、人物看雾体或事件，都必须先在分析稿中写具体轴线：

- A 端、B 端。
- 摄影机允许侧和禁止侧。
- screen left/right。
- 过肩肩位、前后层级、允许裁切。

`final_image_prompts.md` 中页级写完整轴线；Panel 内只写本格 screen left/right、肩位、前后层级和裁切差异。不得每格复制整段长轴线，也不得只写 `do not cross the axis`。

车辆页必须写车辆局部坐标：`vehicle left/right/front/rear`、座位-车窗邻接、摄影机占位、车内外同侧窗口关系。没有车辆时写“本页无车辆”，不要复制车辆规则。

## 输出合同

每个任务至少输出：

1. `分析与锁定.md`
2. `final_image_prompts.md`

如需数据追踪，可额外输出 `panel_plan.json`。如需生图，图片放入 `outputs/YYYY-MM-DD/images/`，原始无字图必须保留。

### 分析与锁定.md

可写完整信息，包含来源范围、资产审查、profile、角色/道具锚点表、空间概念、P01 锚定、固定物屏幕投影、轴线表、车辆表、逐 panel 可见性、九格取舍、去重检查、风格继承检查。

### final_image_prompts.md

这是唯一允许用于 Image2 生图的正式输入。每页必须：

- 目标长度 7,000-11,000 字符。
- 超过 12,000 字符必须停止并压缩，不得生图。
- 包含 `SYSTEM_STYLE_LAYER`、`PROFILE_SOURCE_AND_PRECEDENCE`、`PROJECT_VISUAL_PROFILE`、`SCENE_LAYER`、`CAMERA_RULE_LAYER`、`PANEL_LAYER P01-P09`、`NEGATIVE_CONSTRAINTS`。
- `PROJECT_VISUAL_PROFILE` 每页只写一次。
- `OBJECT_VISIBILITY_AND_BOUNDARIES` 只保留页级摘要，不和 Panel 字段逐字重复。
- `MUST NOT SHOW` 每格只列本格关键禁显对象；通用文字/UI/字幕/风格禁令放入 `NEGATIVE_CONSTRAINTS`。
- `SCREEN POSITION / AXIS LOCK` 每格只写本格差异。
- `CONTENT` 只能写可画内容，不粘贴对白原文、完整剧本段落或长分析。

## 生图前硬门槛

只有用户明确要求生图或 ZIP 时才生图。生图前必须满足：

- 已存在 `final_image_prompts.md`，且每页 7,000-11,000 字符；任一页超过 12,000 字符则停止。
- 参考图版必须真实绑定参考图输入；否则只能作为文字提示词或标注高风险样张，不得交付为正式参考图版生图。
- 每页已通过语义验收和风格验收。
- 人物/道具归属、screen left/right、Panel 1 主锚定、可见性、无字、3x3 几何均已检查。
- 不允许临场手写、口头压缩或聊天窗口临时拼接 prompt 直接生图。

任一失败，输出 `任务失败：su-image9 语义规划失败` 或具体失败类型，列出失败项并停止。

## 生图后验收

原始图按以下顺序目检，任一失败必须标记不合格并收紧压缩稿后重生，最多连续重生两次：

1. wide horizontal 16:9，严格 3x3，9 格同宽同高，每格 horizontal 16:9。
2. 无画内文字、数字、字幕、标签、UI、水印。
3. 整体为同一黑白石墨铅笔生产分镜风格。
4. 人物服装、发型、道具归属匹配 profile；相似男性不串位。
5. Panel 1 主平面锚定成立，后续空间继承成立。
6. `VISIBLE ONLY` 无多画角色，`MUST NOT SHOW` 无误入画面。
7. 轴线、screen left/right、过肩肩位不越轴。
8. 车辆页检查局部坐标、座位-车窗邻接、摄影机占位。

标注图、PDF 或图册验收细则见 `references/validation-checklists.md`。

## 失败输出格式

当无法继续时，输出：

```text
任务失败：su-image9 语义规划失败
- 失败项：
- 依据：
- 建议下一步：
```

常见失败项：参考资产冲突、参考图未真实绑定、profile 来源冲突、Panel 1 非锚定、轴线泛化、人物/道具串位风险无法用短锚点控制、最终生图块超过 12,000 字符、缺少 `final_image_prompts.md`。
