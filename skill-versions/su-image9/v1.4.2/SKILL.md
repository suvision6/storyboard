---
name: su-image9
description: Image2 9 宫格/3x3 黑白分镜提示词独立技能。用于把参考图、资产图、俯视图、站位图、尾帧、剧本文字、文字版分镜、Markdown/Excel 表格、局部镜号或表格截图转写为 Image2/gpt-image-2 可复制提示词。默认生成 wide horizontal 16:9 canvas containing a clean 3x3 storyboard grid，9 个宫格全部为 horizontal 16:9 storyboard frames。保留 9 格容量，同时使用不可覆盖的 SYSTEM_STYLE_LAYER 锁定黑白石墨铅笔生产分镜风格，并吸收 7 格版的第 1 格主平面锚定、固定物屏幕投影、车辆局部坐标、座位-车窗邻接、车内摄影机占位、车内外同侧窗口、画内文字禁令、后处理脚本派生中文标注和生图验收规则。不得修改 su-fenjingskill-zh 主表、Prompt 列、Storyboard 列、Excel 或校验脚本。
---

# Image2 9 宫格分镜提示词独立技能

## 版本

<!-- skill-version: 1.4.2 -->

`su-image9` 是 3x3 九宫格黑白分镜提示词独立入口。它保留九宫格横版容量，但补入 `su-image7` 中更强的空间、车辆、反打、无字生图和后处理中文标注规则，并用 `SYSTEM_STYLE_LAYER` 把风格从普通 prompt 片段提升为不可覆盖的系统层。不要转用 `su-image2-storyboard-grid-zh`。

1.3.0 强化语义规划层：九宫格在格式正确之前，必须先通过空间连续、Panel 1 主锚定、逐格去重、具体轴线、逐 Panel 车辆坐标和语义失败校验。格式硬词通过不等于可生图；任何语义闸门失败都必须停止，不得输出正式 `Image2 可复制提示词`。

1.4.0 强化系统风格层：九宫格在内容正确之前，必须先锁定黑白石墨铅笔生产分镜媒介、线条、排线、灰度、纸面颗粒和 batch 一致性。正式提示词必须分为 `SYSTEM_STYLE_LAYER`、`SCENE_LAYER`、`CAMERA_RULE_LAYER`、`PANEL_LAYER P01-P09` 和 `NEGATIVE_CONSTRAINTS`；Panel 层只写内容，不得重新定义风格。

1.4.1 强化 Panel 数据锁定层和标注/PDF 后处理层：每个 Panel 必须显式继承 `shot_data.json` 的镜头三要素、可见对象、禁显对象、人物锚点和屏幕轴线；标注版/PDF 不得把原始九宫格硬切成 9 个小图后重复画框，不得用 PIL 默认 JPEG PDF 导出导致线条压缩伪影。

1.4.2 修复 1.4.1 生图退化：第 1 格主平面锚定优先级高于逐字机位匹配；若来源首镜是特写、近景、过肩或反应镜头，必须把该来源镜头顺延到 P02-P09，并把 P01 改写为空间全景锚定。新增的 Panel 数据硬字段必须保留，但最终 Image2 生图块必须压缩，避免把完整可见性表、长禁显清单和重复轴线整段塞入每格导致脏线、噪点和深色堆叠。

## 核心边界

- 不修改 `su-fenjingskill-zh`，不回写主表，不改变镜号、场景、原剧本段落、镜头时长、运镜主画面、备注、Prompt 列或 Storyboard 列。
- 默认只输出 Markdown 提示词文件；只有用户明确要求“生图、批量生成、按 Markdown 生成图片、输出 ZIP”时才进入生图流程。
- 最终 `Image2 可复制提示词` 使用英文主导；中文分析表只服务于空间、连续性和取舍锁定。
- Image2 prompt block must be image-only and text-free；生图层禁止任何画内文字，最终提示词必须保留 `no text inside the image`，不得包含页眉、镜号、三要素、annotation layer、after generation labels、`C序号` 或任何让模型画字的指令。
- 标注交付层只允许后处理脚本添加中文文字：生图完成后，由脚本读取 `shot_data.json`，在图片外部排版层添加页眉和每格 `C序号｜视角｜景别｜运镜` 标签；这些文字不得由 Image2 直接生成、猜写、翻译、混写或改写。
- Image2 生成层永远无字；所有中文页眉、镜号范围、`C序号` 和三要素标注，只能由后处理脚本基于 `shot_data.json` 在图外标签区派生添加。
- 三要素标注必须先按 `shot_data.json` 的计划值生成，再对照生成图的实际构图、景别和原分镜剧情核对；若构图不符，必须标记为“构图不符，需重生/人工确认”，不得用假标签迁就错误画面。
- 如果读取 `su-fenjingskill-zh` 交付物，优先用主表前 6 列、`shot_data.json`、`continuity_logs`、`continuity_updates`、`visible_characters`、`visible_props`；Prompt 列只能作为镜头摘要辅助，不能作为主输入或唯一输入。
- `SYSTEM_STYLE_LAYER` 是固定全局层，不是可选段落。参考图、场景描述、角色动作、镜头语言、用户补充说明或 Panel 内容都不得覆盖、削弱或替换这一层。
- 风格规则不得分散写入 P01-P09。Panel 层只能写主体、动作、构图、景别、空间继承和状态变化，不得把某一格改成漫画、插画、电影剧照、CG、概念图或渲染图。

## SYSTEM_STYLE_LAYER｜系统风格层

`SYSTEM_STYLE_LAYER` 是 `su-image9` 的最高优先级视觉层。它定义整张九宫格和整个 batch 的统一绘画媒介、线条、灰度、材质和渲染禁令。正式 `Image2 可复制提示词` 必须先输出 `SYSTEM_STYLE_LAYER`，再输出场景、镜头和 Panel 内容。

固定风格模块必须完整进入最终提示词：

```text
SYSTEM_STYLE_LAYER:
This entire generation must follow a single unified storyboard production style.

STYLE ANCHOR:
Treat this as a single cohesive storyboard drawn by one graphite storyboard artist in a single production session. For batch generation, all outputs must match the same storyboard artist, same production session, same medium, same stroke weight, same shading density, and same unfinished storyboard look.

MEDIUM:
Monochrome graphite storyboard / pencil pre-visualization drawing only. Hand-drawn pencil / graphite sketch only. Production storyboard sheet. Animatic frame design. Non-painting, non-rendered, non-illustration.

LINE RULE:
Thin graphite linework only. Visible sketch strokes allowed. Construction lines allowed. Rough drafting lines allowed. No inked comic outlines. No polished clean manga line art.

SHADING RULE:
Light hatching only. Mid-gray tonal range. Controlled medium contrast only. No pure black fill blocks. No heavy ink fill. No painterly shading. No soft airbrush gradients.

TEXTURE RULE:
Paper-like sketch texture. Slightly rough graphite grain. High-frequency pencil texture. Unfinished production drawing aesthetic.

RENDERING RULE:
No digital painting, no photorealism, no CGI, no cinematic lighting, no bloom, no HDR lighting, no volumetric god rays, no depth-of-field blur, no airbrush gradients, no rendered concept art look.

CONSISTENCY RULE:
All 9 panels must share identical drawing style, graphite medium, stroke weight, shading density, texture grain, tonal range, and rendering restraint. No stylistic variation between panels is allowed.
```

参考图只能提供角色、空间、道具、车辆或构图依据，不能覆盖 `SYSTEM_STYLE_LAYER`。如果参考图是彩色、写实、厚涂、漫画、照片、AI 渲染或 CG，只继承内容信息，不继承视觉风格。如果用户明确要求“保持参考图风格”，且该风格与石墨铅笔分镜冲突，必须提示冲突并要求确认，不得静默覆盖系统风格层。

## SKLL 分层输出架构

正式提示词必须按层级组织，不得把风格、场景和 Panel 内容混写成一段无层级 prompt。

固定层级：

1. `SYSTEM_STYLE_LAYER`
   - 只负责媒介、笔触、灰度、材质、渲染禁令和 batch 风格一致性。
   - 不写具体剧情动作，不写单格镜头内容，不被后续层覆盖。
2. `SCENE_LAYER`
   - 负责场景位置、空间边界、固定几何、门窗家具、道路、洞穴、车厢等不可漂移锚点。
   - 负责人物、车辆、道具、灵异对象的初始位置和允许位移。
   - 负责 Panel 1 主平面锚定与 Panels 2-9 继承关系。
   - 不重新定义绘画风格。
3. `CAMERA_RULE_LAYER`
   - 负责机位编号、摄影机朝向、对视轴线、反打肩位、车辆内摄影机占位、`screen left/right` 投影。
   - 不重新定义绘画风格，不新增剧情事实。
4. `PANEL_LAYER P01-P09`
    - 每个 Panel 只写主体、动作阶段、景别、观察角度、构图任务、空间继承、对象状态变化和信息增量。
   - 每个 Panel 必须显式写入 `MUST MATCH SHOT_DATA CAMERA TAG`、`VISIBLE ONLY`、`MUST NOT SHOW`、`CHARACTER ANCHORS`、`SCREEN POSITION / AXIS LOCK` 和 `CONTENT`。
   - 正式 Image2 生图块必须使用压缩写法：字段名保留，字段内容只保留对绘图必要的信息；完整长表放在中文分析区，不得在每格重复长禁显清单、完整来源段落或整段轴线。
   - Panel 层不得只写泛化镜头词，如 `wide shot`、`storm center`、`reaction shot`、`same layout`；必须绑定来源镜头编号和 `camera_main_image` 方括号里的三要素。
   - 不允许写新的风格词，不允许用每格重复风格词的方式制造风格漂移。
5. `NEGATIVE_CONSTRAINTS`
   - 汇总几何、无字、无色彩、无渲染、无漫画页、无插画化等禁令。

## Panel 数据硬锁层

当输入来自 `su-fenjingskill-zh` 主表、`shot_data.json`、Markdown/Excel 分镜表或任何已锁定镜号范围时，`PANEL_LAYER P01-P09` 必须逐格使用以下固定结构。缺一项即视为语义规划失败，不得输出正式 `Image2 可复制提示词`：

```text
P0X:
SOURCE SHOT: shot N 或 shot N-M 的主镜头编号；P01 若被重写为空间锚定，则写 page anchor synthesized from shot range N-M, source shot N moved to P02.
MUST MATCH SHOT_DATA CAMERA TAG: [视角, 景别, 运镜] copied exactly from shot_data.json camera_main_image；P01 anchor override 时同时写 DRAWN CAMERA TAG: master wide/full spatial anchor.
VISIBLE ONLY: only the characters / props / spatial anchors visible in the source shot or explicitly allowed by the page anchor.
MUST NOT SHOW: all offscreen characters, props, future objects, alternate locations, subtitles, labels, readable symbols, and any character not listed for this Panel.
CHARACTER ANCHORS: identity, silhouette, costume continuity, prop ownership, state, and forbidden swaps for every visible recurring character.
SCREEN POSITION / AXIS LOCK: screen left/right, A/B axis endpoints, camera side, over-shoulder shoulder side, and any allowed crop or push-in.
CONTENT: subject, action phase, composition task, spatial inheritance, object state change, and result.
```

- `MUST MATCH SHOT_DATA CAMERA TAG` 必须直接来自 `shot_data.json` 的 `camera_main_image` 开头方括号，不得根据生成图、用户口头描述或 Prompt 列重写。唯一例外是 P01 主平面锚定：当来源首镜是特写、近景、过肩或局部反应时，P01 必须记录来源三要素用于追溯，但实际绘制使用 `DRAWN CAMERA TAG: master wide/full spatial anchor`；来源首镜顺延到 P02-P09 并保持原三要素。
- 来源节点少于 9 个而拆分阶段时，每个拆分 Panel 仍必须指向一个来源镜头，并写清该格继承的同一三要素；除 P01 anchor override 外，不得把特写改成全景、把高角度俯拍改成平视、把低角度仰拍改成普通宽景。
- 多镜头合并 Panel 默认使用来源范围首镜头三要素；若该格明确指定主镜头，则以该主镜头三要素为准，并在中文 `九格取舍表` 说明。
- `VISIBLE ONLY` 不等于“可以把同场人物都画进来”。若 `visible_characters` 只有两人，其余角色必须写入 `MUST NOT SHOW`，不得作为远景小人、背影、阴影、倒影、轮廓或背景站位出现。P01 anchor override 的 `VISIBLE ONLY` 按本页锚定关系写入已出现且允许用于建立空间的角色/道具；不得沿用来源特写的单人可见性把空间锚点人物排除掉。
- `MUST NOT SHOW` 必须包括：不在本格 `visible_characters` 的角色、不在本格 `visible_props` 的道具、未出现的怪物形态、未来状态、回忆空间、手术室空间、字幕、页眉、镜号、倒计时数字、心电图可读文字。
- 关系镜头、过肩、反打和双人中景必须写具体肩位和屏幕左右；不得只写 `do not cross the axis`。

### 最终生图块压缩规则

1.4.1 的新增字段用于防止漂移，但不得把分析层整表搬进 Image2 生图块。正式 `Image2 可复制提示词` 必须满足：

- 单页最终生图块目标长度为 7,000-11,000 个英文/中文字符；超过 12,000 字符必须先压缩，不得直接生图。
- `SYSTEM_STYLE_LAYER`、`GEOMETRY_BLUEPRINT` 和 `NEGATIVE_CONSTRAINTS` 只写一次，不得在每个 Panel 复述风格禁令。
- `MUST NOT SHOW` 每格只列本格最关键的禁显角色、禁显道具和禁显空间；通用禁令如文字、字幕、页眉、镜号、水印、CG、彩色、厚涂统一放入 `NEGATIVE_CONSTRAINTS`。
- `CHARACTER ANCHORS` 每格只写可见角色的短锚点，例如 `Lin Xiaotong: bracelet owner, female silhouette, right-side continuity, no staff/no brow mark`；完整角色外观与道具锚点表只放在中文分析区。
- `SCREEN POSITION / AXIS LOCK` 每格只写本格银幕左右、肩位、前后层级和是否允许裁切；不得把同一长轴线文本复制到每个可见角色后。
- `CONTENT` 只能是一到两句可画内容，不得粘贴完整 `camera_main_image` 段落、对白原文或大段来源说明。
- 如果最终生图块因新增硬字段导致线条变脏、噪点变多、深色堆叠或模型开始画伪文字，必须优先压缩 Panel 层，而不是削弱 `SYSTEM_STYLE_LAYER`。

## 人物连续锚点

人物连续页必须输出 `角色外观与道具锚点表`，并在每个相关 Panel 的 `CHARACTER ANCHORS` 中复述本格可见人物锚点。以下为本项目默认锚点；若 `shot_data.json` 或用户当前指令给出更具体锚点，以来源为准，但不得静默互换身份：

| 角色 | 身份锚点 | 轮廓/服装锚点 | 道具/状态锚点 | 位置锚点 | 禁止互换 |
|---|---|---|---|---|---|
| 林晓彤 | 年轻中国女性，手环持有者 | 与沈夜、顾成区分的女性轮廓；服装和发型在同一页内连续 | 手环归她所有；可出现泪痕、抬手、挡雾等来源动作 | 战斗队形右侧，或按来源移动到沈夜身前、空腔中心 | 不能持长棍，不能带沈夜额间神印，不能被画成沈夜或顾成 |
| 沈夜 | 男性同伴 | 与林晓彤区分的男性轮廓；同页服装连续 | 胸口旧伤、赤光/额间神印相关状态；后期可消散 | 战斗队形左侧；牺牲段可位于林晓彤对面 | 不能持手环，不能持顾成长棍，不能被画成女性角色 |
| 顾成 | 男性同伴，长棍持有者 | 与沈夜区分的男性轮廓；更靠中前或倒地低位 | 长棍归他所有；可出现长棍断裂、倒地、撑棍 | 战斗队形中前；受击后倒地位置保持连续 | 不能持手环，不能带沈夜额间神印，不能被画成沈夜或林晓彤 |

- 当某格不应出现某角色时，必须在 `MUST NOT SHOW` 中显式写入该角色名。
- 角色外观锚点只用于身份和连续性，不得引入彩色服装、照片质感、CG 质感或漫画风格。
- 如果同一页中无法用文字锚点防止人物互换，应拆页或请求补参考图；不得硬生成。

## 输入分流

### 参考图输入

当输入包含场景参考图、角色图、道具图、俯视图、平面图、站位图、机位图、尾帧、上一镜输出图、图片编号、资产路径或图片附件时，按参考图流程执行。

参考图流程必须先做资产/空间一致性审查。以下情况必须输出 `任务失败：参考资产冲突` 并停止：

- 图片用途不清或资产编号无法匹配。
- 俯视图/站位图与透视参考图发生空间冲突。
- 用户文字与参考图中的门、窗、床、桌、车、角色站位、机位、道具归属发生冲突。
- 参考图与主表/台账摘要在人物站位、门窗家具、车辆侧别、道具归属或运动路径上冲突。
- 多张参考图之间无法判断主次，且会影响空间布局、人物身份或道具归属。

参考图必须转写成具体控制信息，不在最终提示词中写“如图所示”“严格参考图片”“根据图片”。只有角色/道具参考图而没有空间参考时，不从角色/道具图臆造空间；第 1 格按文字推演主平面锚定。

参考图转写必须分离内容与风格：

- `内容可继承`：角色身份、服装轮廓、道具形状、空间结构、门窗家具、车辆位置、机位关系。
- `风格不可继承`：色彩、照片质感、电影光效、CG 渲染、厚涂笔触、漫画线稿、AI 精修质感。
- 参考图若是风格参考而非内容参考，且与 `SYSTEM_STYLE_LAYER` 冲突，必须输出 `任务失败：参考风格冲突` 或请求用户确认是否改变技能目标。
- 最终提示词不得写 `copy the style of the reference image`、`match the reference style` 或同义句。

### 纯文字输入

当输入只有剧本文字、纯剧情段落、文字版分镜、Markdown/Excel 表格内容、表格截图转写内容、局部镜号或镜号范围时，按纯文字流程执行。

纯文字流程不得要求用户补参考图；不得为了画面丰富新增角色、新道具、新建筑、新动作结果或新对白。如果输入中出现参考图或资产线索，切换到参考图流程。

若纯文字中包含“电影感、赛博、厚涂、日漫、写实、照片级、CG、概念图”等风格词，默认只作为剧情氛围或来源描述理解，不改变 `SYSTEM_STYLE_LAYER`。如果用户明确要求改变默认石墨铅笔生产分镜风格，必须视为与 `su-image9` 默认合同冲突，并先要求确认。

## 9 宫格版式规则

- 整体画布必须是 `wide horizontal 16:9 canvas`。
- 输出固定为 `clean 3x3 storyboard grid`，不得改成 7 格、竖版 2:3、正方形拼贴或不规则多格。
- 9 个宫格全部必须是 `horizontal 16:9 storyboard frame`，不得画成正方形、竖图或等比例混乱的小格。
- 原始 Image2 生图画布不得使用 `3:2`、`4:3` 或横版 A4；这些比例只允许作为脚本后处理审阅版或 PDF 版式。
- Panel 1 是 3x3 网格内的主平面锚定格，不跨栏；Panels 2-9 从 Panel 1 推进剧情。
- Panels 2-9 只能从 Panel 1 裁切、推进、反打、俯拍、侧拍或换焦点，不得重新布景。
- 九宫格版式稳定不等于风格稳定；几何正确后仍必须通过 `SYSTEM_STYLE_LAYER` 风格校验。
- 9 个 Panel 的边框、gutter、线条密度、灰度密度必须统一。
- Close-up 或特写只能在 Panel 内裁切内容，不允许通过加粗线条、重黑块、电影光效或高反差渲染来强调。

## 语义规划闸门

生成正式 Markdown 之前，必须先完成语义规划闸门。以下任一条件失败时，输出 `任务失败：su-image9 语义规划失败`，列出失败项，并停止；不得生成 `Image2 可复制提示词`，不得进入生图。

- 分页必须按连续空间、人物关系轴线、车辆内外连续关系、幻境/现实层级切段；不得只按镜头数量均衡切段。
- 同一页九宫格只能有一个可继承的主空间锚点。若来源发生明确转场、切回、进入另一空间、记忆层级切换或车内外关系断裂，必须拆成新页，除非 Panel 1 能同时建立这些层级的从属关系。
- Panel 1 必须是空间主锚定，不得直接使用特写、极近特写、单人近景、主观局部、中景反应或道具特写作为 Panel 1。
- 如果来源第一镜不是空间锚定，必须在不新增剧情事实的前提下改写 Panel 1：只建立已公开空间、固定物、角色起点、车辆位置、道路方向、门窗家具、层级关系和未来对象的空位。
- 每个 Panel 必须有唯一的主体、动作阶段、构图任务和对象状态；不得为了凑满 9 格直接复用同一来源镜头或同一句画面描述。
- 对话、对视、过肩、反打、保护、追击、车内外互看、旁观层观看事故等关系镜头，必须先输出具体轴线，不得只写泛化的 `do not cross the axis`。
- 车辆页必须逐 Panel 写清车辆局部坐标、座位、车窗侧、摄影机占位、车内外同侧关系和 `screen left/right` 投影，不得只写通用左舵规则。
- 任一 Panel 缺少 `SOURCE SHOT`、`MUST MATCH SHOT_DATA CAMERA TAG`、`VISIBLE ONLY`、`MUST NOT SHOW`、`CHARACTER ANCHORS`、`SCREEN POSITION / AXIS LOCK` 或 `CONTENT` 时，必须输出 `任务失败：su-image9 语义规划失败`。
- 任一 Panel 的 `MUST MATCH SHOT_DATA CAMERA TAG` 与来源 `shot_data.json` 的方括号三要素不一致，或未能追溯到来源镜头编号时，必须停止。
- 任一 Panel 的 `VISIBLE ONLY` 包含来源中不可见角色/道具，或 `MUST NOT SHOW` 遗漏同场但本格不可见的关键角色时，必须停止。
- 人物连续页缺少 `角色外观与道具锚点表`，或林晓彤、沈夜、顾成等连续人物没有在 Panel 内写入 `CHARACTER ANCHORS` 时，必须停止。
- 任一连续人物的身份、轮廓、服装、道具归属、状态或屏幕位置与来源相互错置，例如林晓彤持长棍、沈夜持手环、顾成带沈夜神印，必须停止。
- 若任务包含标注版或 PDF 派生计划，计划中出现九宫格硬切、单格重复画框、标签压入画内、PIL 默认 JPEG PDF 或 `/DCTDecode` 单一 JPEG 滤镜时，必须停止并改用后处理规则。
- 必须存在完整 `SYSTEM_STYLE_LAYER`，且必须位于 `PANEL_LAYER P01-P09` 之前；缺失或后置都视为语义规划失败。
- P01-P09 不得包含独立风格定义，例如 `cinematic lighting`、`anime rendering`、`digital painting`、`photorealistic`、`concept art`、`watercolor`、`oil painting`、`CGI render`。
- 同一页中不得把不同 Panel 规划为不同绘画媒介、不同线条密度、不同灰度密度或不同渲染方式。
- 多页 batch 必须声明同一分镜师、同一生产场次、同一媒介、同一笔触和同一灰度密度。
- 参考图风格与系统风格冲突时，必须剥离参考图风格；无法剥离时输出 `任务失败：参考风格冲突`。
- 负面约束必须覆盖写实、电影光、HDR、体积光、CG、数字绘画、厚涂、水彩、油画、日漫渲染、漫画页、概念图、气刷渐变和画内文字。

语义失败格式：

```markdown
任务失败：su-image9 语义规划失败

失败项：
| 编号 | 类型 | 位置 | 原因 | 修复要求 |
|---|---|---|---|---|
| 1 | ... | ... | ... | ... |

不生成正式 Image2 提示词。
```

### Strict panel geometry blueprint

英文最终提示词必须携带这一组几何硬约束，避免九宫格变成方格、竖窄格、混合尺寸小格或不规则漫画拼贴：

- `Strict panel geometry blueprint, mandatory before drawing:`
- `Treat the final canvas as a clean wide horizontal 16:9 layout.`
- `Draw exactly nine separate straight rectangular panel frames with visible gutters.`
- `Arrange the 9 panels in a clean 3x3 storyboard grid: three equal columns and three equal rows.`
- `All 9 panels must have the same width, the same height, the same 16:9 aspect ratio, and aligned edges.`
- `Each panel frame must remain a flat horizontal 16:9 rectangle.`
- `Do not let any panel become square, vertical, tall, narrow, compressed, stretched, trapezoid, diagonal, rounded, or irregular.`
- `Keep gutters and margins as empty separating space. If a close-up needs more room, use empty background or negative space inside that panel; never change the panel shape or aspect ratio.`
- `Do not create 3:2, 4:3, A4, square, vertical, mixed-size, manga, comic, collage, or poster layouts.`
- `Do not create a manga page, comic page, dynamic collage, masonry grid, mixed panel sizes, tilted frames, perspective-distorted frames, overlapping panels, or a poster composition.`
- `The content inside a panel may crop or zoom, but the panel frame itself must remain a flat horizontal 16:9 rectangle.`
- `Geometry correctness does not replace the SYSTEM_STYLE_LAYER. The 3x3 grid must remain geometrically strict while all panel contents remain in the same monochrome graphite storyboard production style.`

## 后处理中文标注层

后处理中文标注层是生图后的外部排版步骤，不属于 Image2 生图内容，严禁写入 `Image2 可复制提示词` 代码块。需要分发给同事、导演或制片审阅时，默认同时规划一版标注图：

- 原始生图保持无字；不得在 Image2 提示词里要求生成中文、镜号、场次、字幕、箭头文字或说明文字。
- 标注版在整张图最左上方页眉写中文：`场次/场景｜镜头编号范围`，例如 `13-1 赤狐岭迷雾深林 日 外｜镜头001-009`。
- 标注版在每个单独宫格下方的外部标签区写中文：`C序号｜视角｜景别｜运镜`，例如 `C1｜微俯视｜大全景｜伸缩摇臂缓慢下降`。
- `视角｜景别｜运镜` 的计划值必须只从 `shot_data.json` 的 `camera_main_image` 开头方括号读取；不得翻译成英文，不得根据画面猜写，不得用模型自行概括，不得混用中英文。
- 多镜头合并 Panel 默认使用来源范围首镜头三要素；若生成提示词明确指定主镜头，则以该主镜头三要素为准。
- 后处理前必须做图片构图核对：逐格检查生成图的实际视角、景别、运镜表达是否大体符合对应 JSON 三要素和原分镜剧情。
- 若图片与 JSON 三要素或原分镜剧情明显不符，不允许把标签改成看似匹配的假三要素；该格必须标记为 `构图不符，需重生/人工确认`，优先重生该段或该页。
- 标签区必须位于宫格外部排版层，不得压缩、遮挡、裁切或覆盖任何 16:9 宫格内容。
- 标注版可由脚本扩展为 `3:2` 横版审阅图或 A4 横版 PDF；这些比例只属于分发版式，不改变原始无字 16:9 九宫格。
- 若生成 PDF、图册、PPT 或网页索引，优先使用标注版；若要继续二次生图或修图，保留无字原图。
- 后处理中文标注层不得改变原始图的石墨铅笔分镜质感。标注版只增加外部文字排版，不得对宫格内图像加色、加电影调色、加锐化特效、加阴影 UI、加漫画边框。
- 若标注版用于 PDF、PPT 或网页索引，也必须保留“原始无字石墨铅笔分镜图”为母版。

### 标注/PDF 排版派生规则

标注版和 PDF 属于生图后的外部排版层。生成标注版或 PDF 时必须遵守：

- 原始生图不得被九宫格硬切成 9 个独立小图后再重画边框；不得把原始宫格线、裁切线、后处理边框叠成三层线。
- 标注版优先采用整图加外部页眉和标签带；若必须重排，优先整行裁切，不按单格裁切。
- 标签只能放在宫格外部标签带，不得覆盖、压缩、遮挡或重采样任何 16:9 宫格内容。
- 标注版不得在每格上重复画外框；如需辅助线，只允许使用极细横向行分隔线或图外标签带分隔线。
- 若需要自动定位宫格边界，优先用图像灰度投影、边线检测或人工确认的真实宫格线；不得默认用 `width / 3`、`height / 3` 的小数硬切作为唯一方案。
- PDF 必须使用无 JPEG 压缩或低损嵌图流程，优先 `reportlab + PNG/FlateDecode`；不得使用 PIL 默认 `Image.save(..., PDF)` 导致 `/DCTDecode` JPEG 压缩。
- PDF 输出后必须用 `pypdf` 检查页数、图片 XObject 尺寸和滤镜；若滤镜是单一 `/DCTDecode`，必须视为 PDF 派生失败并改用无损/低损流程。
- PDF 输出后必须用 Poppler `pdftoppm` 或等效工具渲染抽查页，确认线条没有混乱、标签没有裁切、图像没有被压缩出明显伪影。

## 第 1 格主平面锚定

- 所有内景、外景、院落、走廊、房间、道路、车厢等连续九宫格，Panel 1 必须优先建立主平面锚定。
- 即使原始第一节点是特写、近景或反应镜头，也要把 Panel 1 改写为全景、大全景、俯视全景或主观全景锚定格。
- P01 主平面锚定高于 `MUST MATCH SHOT_DATA CAMERA TAG` 的绘制优先级。来源首镜的三要素必须记录，但不得让 `[特写]`、`[中近景]`、`[过肩]` 或 `[局部]` 把 P01 变成非锚定格。
- 当来源首镜不是全景锚定时，P01 必须写 `SOURCE SHOT: page anchor synthesized from shot range N-M; source shot N moved to P02`，P02 承接原 shot N 并逐字匹配其三要素。
- P01 的 `VISIBLE ONLY` 必须服务空间锚定：允许显示本页已出现且需要建立银幕左右关系的角色、道具和空间锚点；禁止因为来源首镜是单人特写而把其他锚定角色写进 `MUST NOT SHOW`。
- Panel 1 不得新增剧情事实，不得新增角色、道具、建筑、车辆、动物或对白。
- 尚未在剧情中出现的人物、道具、车辆、动物或灵异对象不得提前画出；只能锚定其未来出现的空位置、门口、房间中央、道路尽头、桌面空位等可公开空间。
- 后续近景如果裁掉家具、地形、门窗或道路，背景应保持简化或来自 Panel 1 局部；不得补画新家具、新门窗、新街道或新房间。
- Panel 1 的英文描述必须写明：空间边界、主方向、固定锚点、角色或车辆初始位置、允许隐藏对象、后续继承方式、禁止重建内容。
- 若 Panel 1 来源于重写锚定而非原镜头本身，必须在中文 `九格取舍表` 中标注 `重写为空间锚定`，并说明没有新增剧情事实。

## 固定物与空间锁定

9 宫格必须吸收 7 格版的固定物约束。按任务实际场景输出这些中文表格：

- `空间概念`：场景边界、方向锁定、摄影机轴线、初始坐标、允许位移、禁止漂移。
- `第1格主平面锚定表`：空间类型、锚定景别、固定锚点、允许隐藏对象、后续继承规则、禁止提前揭示或重建。
- `门窗家具几何锁定表`：门的墙面、铰链侧、把手侧、开合方向；窗的墙面、内外侧和光源；家具的墙面、屏幕区域、正/侧面朝向和路径关系。
- `固定物屏幕投影表`：每格中门、床、桌、梳妆台、镜子、车门、道路入口等固定物的屏幕投影；不可见时写“裁掉/画外”，不能写成新位置。
- `前序9格布局继承表`：Panels 2-9 逐格写清继承 Panel 1 哪些锚点、哪些只允许裁切、哪些不得重画。
- `对象足迹与朝向表`、`机位编号表`、`摄影机朝向表`、`对象可见性表` 按对象和镜头关系输出。
- `角色外观与道具锚点表`：连续人物的身份、轮廓、服装、道具归属、状态、屏幕位置和禁止互换规则。
- `逐Panel可见性排除表`：每格列出 `VISIBLE ONLY` 与 `MUST NOT SHOW`，防止同场但本格不可见角色漂入画面。
- `逐格差异表`：每个 Panel 必须写清与其他 Panel 不同的主体、动作阶段、景别/角度、对象状态和信息增量，防止重复分格。
- `风格继承检查表`：逐页确认 `SYSTEM_STYLE_LAYER` 是否存在、Panel 是否只写内容、是否有冲突风格词、冲突如何处理。这张表只写在 Markdown 分析区，不得写入图片。

`风格继承检查表` 表头固定为：

| 页码 | Panel 范围 | SYSTEM_STYLE_LAYER 是否存在 | Panel 是否只写内容 | 是否有冲突风格词 | 处理 |
|---|---|---|---|---|---|

## 车辆局部坐标与车内物理规则

这是从 7 格版补入 9 宫格的强制升级。只要九宫格内出现车辆、下车、车内外连续关系、车窗框中框、后排反打、车内外对话或透过车窗看人，就必须输出车辆锁定表。

- 本项目车辆默认左舵；若文字或已确认参考图明确右舵，则以来源为准，并在中文表格和英文提示词中明示。
- 必须同时区分 `vehicle left/right/front/rear` 和 `screen left/right`；禁止把车辆左右直接等同为画面左右。
- 左舵车固定推演：驾驶座 = `vehicle front-left`，副驾 = `vehicle front-right`，右后排 = `vehicle rear-right`，副驾下车后人物位于 `vehicle-right exterior side`。
- 如果角色从副驾下车，后续车内镜头只能透过同一侧车窗看到该角色。
- `vehicle rear-right seat is directly adjacent to the vehicle-right rear door/window.`
- 若被拍人物在 `vehicle rear-right`，摄影机应在 `vehicle rear-left or rear-center-left`，斜拍向 `vehicle rear-right` 和他身旁的右后窗；摄影机不能占掉被拍人物座位。
- 车内镜头必须写清摄影机所在座位/区域、镜头朝向哪侧车窗、窗外继承 Panel 1 的哪部分外景锚点。
- 车辆页的每个相关 Panel 描述都必须包含具体坐标句，格式应覆盖：`vehicle-local position`、`camera occupancy`、`view direction`、`visible window/side`、`screen projection`。
- 车外事故、车头、车轮、车窗、车内父亲、车内后排母子、车内恶念、眉心入体等连续关系，必须继承同一辆车和同一事故方向，不得在不同 Panel 中重置车辆朝向。
- 如果来源没有明确后排左右座位，不得擅自把角色固定到错误一侧；可以锁定为 `same rear bench, adjacent rear-row positions`，但必须明确摄影机不占用后排人物位置，并保持同一后排区域。

必填车辆表：

- `车辆舵向与座位锁定表`
- `车辆局部坐标与屏幕投影表`
- `车辆座位-车窗邻接表`
- `车内摄影机占位表`
- `车内外同侧窗口关系表`
- `逐Panel车辆坐标表`

## 对视轴线与反打锁定

当出现两人对视、对话、正反打、过肩、反应近景或关系近景时，必须先输出 `对视轴线与反打锁定表`。

- 写清谁在轴线 A 端、谁在轴线 B 端、摄影机允许停在哪一侧、禁止跨到哪一侧。
- 锁定 `screen left` / `screen right`；反打时只能裁切、换景别或换焦点，不得左右互换。
- 过肩和反打必须指定肩位，不得只写“过肩”“反打”“over the shoulder”或“reverse angle”。
- 英文 Panel 描述必须包含同侧轴线、具体肩位、`screen left/screen right` 和 `Do not cross the axis or swap screen sides.`
- 旁观层观看事故、角色观看黑雾、角色隔车窗/车内外关系，也必须视为轴线关系。必须写清观察者端、被观察事件端、摄影机所在侧和禁止互换的屏幕方向。
- `对视轴线与反打锁定表` 中不得只写原则句。必须至少包含一个具体人物/对象名、一个 A/B 端、一个摄影机侧和一组 `screen left/screen right`。

## 九格取舍

- 有主表时，按用户指定场景、镜号范围或若干镜头生成，不重新拆主表，不改变镜号含义。
- 来源节点少于 9 个时，用同一镜头内的可见阶段、景别、角度、关键反应或道具细节补足。
- 来源节点多于 9 个时，只保留最能表达空间关系、动作推进、道具变化、情绪转折和收尾状态的 9 个节点。
- Panel 1 固定服务主平面锚定；Panels 2-9 承接剧情推进。
- 每格必须写清主体、动作、景别、观察角度、构图、空间关系、角色朝向、距离、互动对象、情绪可见方式、道具位置/归属/变化和动作结果。
- 来源节点少于 9 个时，补足格必须来自来源可追溯的不同阶段；同一来源镜头若被拆分，必须拆成 `建立位置`、`动作开始`、`动作结果`、`反应`、`道具状态变化` 等不同画面，不得复用相同镜头描述。
- 每页必须输出 `九格去重检查表`：Panel、来源镜头、是否重复、唯一视觉任务、与前后 Panel 的差异。
- 若某页无法在不重复、不新增事实的前提下得到 9 个不同画面，必须缩小或扩大来源范围重新分页；不得硬凑。
- 九格取舍只决定剧情节点和构图任务，不决定风格。
- 来源节点少于 9 个时，补足格只能拆分动作阶段、道具状态、反应、空间关系，不能靠改变画风制造差异。
- 来源节点多于 9 个时，删减标准仍是空间、动作、道具、情绪、收尾，不得为了风格多样性选择节点。
- `逐格差异表` 必须说明“视觉任务差异”，但不得写成“风格差异”。

## 语义输出前校验

输出正式提示词前必须逐页校验：

- Panel 1 是否为主平面锚定，且不是特写/近景/局部反应；若来源首镜不是全景，是否已把来源首镜顺延到 P02-P09。
- Panels 1-9 是否没有重复来源镜头的相同画面任务。
- 本页是否只有一个可继承主空间，或已明确主空间与从属层级关系。
- 关系镜头是否有具体轴线、肩位和 `screen left/right`。
- 车辆镜头是否有逐 Panel 车辆坐标、座位、窗侧和摄影机占位。
- 对象可见性是否没有让画外对象以阴影、倒影、小黑点或背景轮廓出现。
- 每个 Panel 是否都有 `SOURCE SHOT`，且来源镜头能在 `shot_data.json` 或主表中追溯。
- 每个 Panel 是否逐字写入 `MUST MATCH SHOT_DATA CAMERA TAG`、`VISIBLE ONLY`、`MUST NOT SHOW`、`CHARACTER ANCHORS`、`SCREEN POSITION / AXIS LOCK` 和 `CONTENT`，且字段内容已按最终生图块压缩规则精简。
- `MUST MATCH SHOT_DATA CAMERA TAG` 是否与 `camera_main_image` 方括号三要素一致；P01 anchor override 是否同时记录来源三要素和实际绘制全景锚定，不得把高角度俯拍、低角度仰拍、平视、过肩、特写、中景、全景或运镜词无说明改写成泛化词。
- `VISIBLE ONLY` 与 `MUST NOT SHOW` 是否按每格可见性排除，不允许本格不可见角色、道具、未来状态或其他空间漂入画面；P01 anchor override 不得把本页空间锚定所需角色误列为禁显。
- 人物连续页是否输出 `角色外观与道具锚点表`，并在 Panel 内锁定林晓彤、沈夜、顾成的轮廓、服装、道具归属、状态和屏幕位置。
- Image2 代码块是否不包含后处理中文标注、`C序号`、页眉、镜号或任何画内文字要求。
- 是否存在完整 `SYSTEM_STYLE_LAYER`，且在 `PANEL_LAYER P01-P09` 之前。
- P01-P09 是否只写内容、动作、构图、空间继承和状态变化，没有重新定义风格。
- 单页最终 Image2 生图块是否控制在 7,000-11,000 字符目标区间；若超过 12,000 字符，必须先压缩再生图。
- 是否已输出 `风格继承检查表`，且没有未处理的冲突风格词。
- 多页 batch 是否锁定同一分镜师、同一生产场次、同一媒介、同一笔触、同一灰度密度。
- 参考图是否只继承内容信息，没有继承彩色、写实、CG、厚涂、漫画或 AI 渲染风格。
- 若本轮同时规划标注图或 PDF，是否明确禁止九宫格硬切、重复画框、标签遮挡画面、PIL 默认 JPEG PDF 和单一 `/DCTDecode`。
- PDF 派生是否要求 `reportlab + PNG/FlateDecode` 或等效无损/低损流程，并要求 `pypdf` 滤镜检查和渲染抽查。

任一校验失败，必须按 `任务失败：su-image9 语义规划失败` 输出，不得生成正式提示词。

## 英文最终提示词结构

最终 `Image2 可复制提示词` 按以下顺序组织：

1. `DELIVERABLE`
2. `SYSTEM_STYLE_LAYER`
3. `SCENE_LAYER`
4. `CAMERA_RULE_LAYER`
5. `CONTINUITY_LAYER`
6. `REFERENCE_USAGE` 或 `TEXT_DERIVED_LAYOUT`
7. `PANEL_1_MASTER_SPATIAL_LAYOUT_ANCHOR`
8. `DOOR_WINDOW_FURNITURE_GEOMETRY_LOCK`
9. `VEHICLE_AND_AXIS_LOCKS`
10. `OBJECT_VISIBILITY_AND_BOUNDARIES`
11. `PANEL_LAYER P01-P09`
12. `NEGATIVE_CONSTRAINTS`

结构规则：

- `SYSTEM_STYLE_LAYER` 必须出现在 `PANEL_LAYER P01-P09` 之前。
- `PANEL_LAYER P01-P09` 不得出现新的风格定义。
- `OBJECT_VISIBILITY_AND_BOUNDARIES` 必须按 Panel 汇总 `VISIBLE ONLY` 和 `MUST NOT SHOW`，并列出本页不可漂入画面的角色、道具和空间层级；完整长表只属于分析区。
- `PANEL_LAYER P01-P09` 必须逐格使用固定块：`SOURCE SHOT`、`MUST MATCH SHOT_DATA CAMERA TAG`、`VISIBLE ONLY`、`MUST NOT SHOW`、`CHARACTER ANCHORS`、`SCREEN POSITION / AXIS LOCK`、`CONTENT`；正式生图块中每个字段必须是短句或短列表。
- 以上字段名必须保留英文大写硬词，不得翻译、缩写、合并或改成自然段。
- 如果必须在 Panel 中提醒风格，只允许写 `Panel style inherits SYSTEM_STYLE_LAYER exactly.`，但默认不建议每格重复。
- `NEGATIVE_CONSTRAINTS` 必须同时包含几何禁令、文字禁令、风格跑偏禁令和渲染禁令。

必须包含硬词：

- `Generate one wide horizontal 16:9 canvas containing a clean 3x3 storyboard grid.`
- `SOURCE SHOT:`
- `MUST MATCH SHOT_DATA CAMERA TAG:`
- `VISIBLE ONLY:`
- `MUST NOT SHOW:`
- `CHARACTER ANCHORS:`
- `SCREEN POSITION / AXIS LOCK:`
- `CONTENT:`
- `Each of the 9 panels must also be a horizontal 16:9 storyboard frame.`
- `Panel 1 is the master spatial layout anchor for the entire 3x3 grid.`
- `P01 anchor override: source camera tag is logged, drawn camera is master wide/full spatial anchor.`
- `All Panels 2-9 must be derived from the same Panel 1 layout.`
- `Do not redesign the room, exterior location, furniture footprint, terrain, road, doorway, vehicle position, or object positions in later panels.`
- `Strict panel geometry blueprint, mandatory before drawing:`
- `Arrange the 9 panels in a clean 3x3 storyboard grid: three equal columns and three equal rows.`
- `All 9 panels must have the same width, the same height, the same 16:9 aspect ratio, and aligned edges.`
- `Do not let any panel become square, vertical, tall, narrow, compressed, stretched, trapezoid, diagonal, rounded, or irregular.`
- `Do not create 3:2, 4:3, A4, square, vertical, mixed-size, manga, comic, collage, or poster layouts.`
- `Do not generate any text, labels, captions, panel numbers, scene headers, shot numbers, subtitles, arrows, or watermarks inside the image.`
- `This entire generation must follow a single unified storyboard production style.`
- `Monochrome graphite storyboard / pencil pre-visualization drawing only.`
- `Hand-drawn pencil / graphite sketch only.`
- `Production storyboard sheet.`
- `Animatic frame design.`
- `Non-painting, non-rendered, non-illustration.`
- `Thin graphite linework only.`
- `Visible sketch strokes allowed.`
- `Construction lines allowed.`
- `Light hatching only.`
- `Mid-gray tonal range.`
- `Controlled medium contrast only.`
- `No pure black fill blocks.`
- `Paper-like sketch texture.`
- `Slightly rough graphite grain.`
- `All 9 panels must share identical drawing style, graphite medium, stroke weight, shading density, texture grain, tonal range, and rendering restraint.`
- `Treat this as a single cohesive storyboard drawn by one graphite storyboard artist in a single production session.`
- `For batch generation, all outputs must match the same storyboard artist, same production session, same medium, same stroke weight, same shading density, and same unfinished storyboard look.`

否定约束固定包含：`No photorealism, no film still look, no realistic skin texture, no cinematic lighting, no cinematic grading, no HDR lighting, no bloom, no volumetric god rays, no depth-of-field blur, no CGI, no 3D render, no digital painting, no digital illustration look, no rendered concept art, no polished illustration, no watercolor, no oil painting, no painterly shading, no soft airbrush gradients, no anime rendering, no manga page, no comic page layout, no inked comic outlines, no clean manga line art, no dynamic collage, no masonry grid, no poster composition, no color, no pure black fill blocks, no heavy ink fill, no text inside the image, no labels, no subtitles, no arrows, no watermarks, no square panels, no vertical panels, no tall panels, no narrow panels, no mixed-size panels.`

`No pure black fill blocks` 不禁止铅笔线、宫格边框和 gutter。`No manga page / comic page layout` 同时是风格禁令和版式禁令。`No anime rendering` 不禁止低细节人物脸；人物仍允许低细节铅笔分镜脸。

## 正式 Markdown 输出骨架

每一页九宫格 Markdown 必须按以下骨架输出，除非任务失败：

```markdown
# Image2 9 宫格分镜提示词｜项目名或场次名

## 中文分析区

### 来源范围

### 九格取舍表

### 空间概念

### 第1格主平面锚定表

### 门窗家具几何锁定表

### 固定物屏幕投影表

### 前序9格布局继承表

### 角色外观与道具锚点表

### 逐Panel可见性排除表

### 对视轴线与反打锁定表

### 车辆锁定表

### 九格去重检查表

### 风格继承检查表
| 页码 | Panel 范围 | SYSTEM_STYLE_LAYER 是否存在 | Panel 是否只写内容 | 是否有冲突风格词 | 处理 |
|---|---|---|---|---|---|

## Image2 可复制提示词

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

PANEL_LAYER P01-P09:

NEGATIVE_CONSTRAINTS:
```

若某页没有车辆、对视反打或参考图，对应中文表格可以写“本页不适用”，但不得删除 `SYSTEM_STYLE_LAYER`、`风格继承检查表`、`PANEL_LAYER P01-P09` 或 `NEGATIVE_CONSTRAINTS`。

## 生图与验收

只有用户明确要求生图或 ZIP 时才生图。每段提示词生成一张独立 3x3 九宫格 PNG，PNG 放入 `pages/`，与 `prompts.md` 打包 ZIP。

原始生图目检顺序固定为：整体横版 16:9、不得是 3:2/4:3/横版 A4、3x3 九格、9 格同宽同高、每格 16:9、无方格/竖窄格/混合尺寸宫格、无画内文字、整体为 monochrome graphite storyboard、像 hand-drawn pencil / graphite sketch、无数字厚涂、无 CG、无电影光、无漫画页、无日漫渲染、9 格同一 stroke weight、9 格同一 shading density、9 格同一 mid-gray tonal range、Panel 1 主平面锚定、每格人物身份正确、`VISIBLE ONLY` 无多画角色、`MUST NOT SHOW` 无误入画面、镜头三要素匹配 `MUST MATCH SHOT_DATA CAMERA TAG`、固定物几何继承、车辆局部坐标、座位-车窗邻接、车内摄影机占位、车内外同侧窗口、反打轴线、屏幕左右不越轴、对象可见性。任一失败，收紧提示词并重生一次；最多连续重生两次。

标注版验收顺序固定为：原始 16:9 宫格比例未改变、中文页眉 `场次/场景｜镜头编号范围` 存在、每个宫格下方 `C序号｜视角｜景别｜运镜` 三要素存在、三要素逐项来自 `shot_data.json`、生成图构图与原分镜剧情大体一致、构图不符处已标记为需重生/人工确认、文字清晰、标签区不遮挡宫格、不压缩宫格、不裁切宫格、不改变宫格边框、不把原始图九宫格硬切成 9 个独立小图、不在每格上重复画框、不出现原图线、裁切线、后处理线三层叠加。

PDF 验收顺序固定为：页数与标注图数量一致、每页图像尺寸正确、标签未被裁切、线条未混乱、无明显 JPEG 压缩伪影、`pypdf` 检查图片 XObject 滤镜不是单一 `/DCTDecode`、优先为 PNG/FlateDecode 或等效无损/低损嵌图、Poppler 渲染抽查页面通过。若 PDF 由 PIL 默认 PDF 导出导致 JPEG 压缩，必须视为失败并重做。

多页九宫格、批量生成、按镜号范围生成多个 Markdown prompt 或 ZIP 时，所有页必须使用完全相同的 `SYSTEM_STYLE_LAYER`。场景切换只能改变 `SCENE_LAYER`，不得改变媒介、线条、灰度、颗粒、渲染密度或分镜师手感。现实/幻境差异只允许通过构图、对象透明度、空间关系表达，不得改成彩色、CG、电影光、厚涂、漫画或高反差风格。批量验收必须检查多页是否像同一位分镜师同一生产场次画出。

生图前还必须完成语义验收和风格验收：重复格、Panel 1 非锚定、跨空间混页、泛化轴线、车辆坐标缺失、缺少 `SYSTEM_STYLE_LAYER`、Panel 层覆盖风格、参考风格冲突、batch 风格未锁定、渲染禁令不足任一存在时，不得生图。
