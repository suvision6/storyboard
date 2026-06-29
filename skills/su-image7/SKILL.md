---
name: su-image7
description: Image2 7 格/宫格黑白分镜提示词独立技能。用于把参考图、资产图、俯视图、站位图、尾帧、剧本文字、文字版分镜、Markdown/Excel 表格、局部镜号或表格截图转写为 Image2/gpt-image-2 可复制提示词。默认生成 7-panel vertical 9:16 storyboard sheet，推荐尺寸 1536 x 2736：第 1 格为顶部全宽 horizontal 16:9 主平面锚定格，下方 6 格为 2-column by 3-row grid，7 个宫格全部为 horizontal 16:9 storyboard frames；Image2 只生成无字原图，中文页眉和每格三要素由后处理脚本添加。必须锁定空间、固定物、车辆局部坐标、座位-车窗邻接、车内摄影机占位、车内外同侧窗口、对视轴线、反打肩位和银幕左右关系。不得修改 su-fenjingskill-zh 主表、Prompt 列、Storyboard 列、Excel 或校验脚本。
---

# Image2 7 格分镜提示词独立技能

## 版本

<!-- skill-version: 1.2.0 -->

`su-image7` 是 7 格 9:16 竖版跨栏锚定分镜提示词独立入口，默认无字生图尺寸为 `1536 x 2736`。不要再转用 `su-image2-storyboard-grid-zh`；本技能内部完成参考图版/纯文字版分流。

## 核心边界

- 不修改 `su-fenjingskill-zh`，不回写主表，不改变镜号、场景、原剧本段落、镜头时长、运镜主画面、备注、Prompt 列或 Storyboard 列。
- 默认只输出 Markdown 提示词文件；只有用户明确要求“生图、批量生成、按 Markdown 生成图片、输出 ZIP”时才进入生图流程。
- 最终 `Image2 可复制提示词` 使用英文主导；中文分析表只服务于空间、连续性和取舍锁定。
- Image2 prompt block must be image-only and text-free；生图层禁止任何画内文字，最终提示词必须保留 `no text inside the image`，不得包含页眉、镜号、三要素、annotation layer、after generation labels 或任何让模型画字的指令。
- 标注交付层只允许后处理脚本添加中文文字：生图完成后，由脚本读取 `shot_data.json`，在图片外部排版层添加页眉和每格 `C序号｜视角｜景别｜运镜` 标签；这些文字不得由 Image2 直接生成、猜写、翻译或改写。
- 如果读取 `su-fenjingskill-zh` 交付物，优先用主表前 6 列、`shot_data.json`、`continuity_logs`、`continuity_updates`、`visible_characters`、`visible_props`；Prompt 列只能作为镜头摘要辅助，不能作为主输入或唯一输入。

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

### 纯文字输入

当输入只有剧本文字、纯剧情段落、文字版分镜、Markdown/Excel 表格内容、表格截图转写内容、局部镜号或镜号范围时，按纯文字流程执行。

纯文字流程不得要求用户补参考图；不得为了画面丰富新增角色、新道具、新建筑、新动作结果或新对白。如果输入中出现参考图或资产线索，切换到参考图流程。

## 7 格版式规则

- 整体画布必须为 `vertical 9:16 canvas`，推荐无字原图尺寸固定为 `1536 x 2736`。
- 每个宫格都必须是 `horizontal 16:9 storyboard frame`；整体画布不能改成横向 16:9。
- Panel 1 必须是顶部全宽 horizontal 16:9 主平面锚定格，约占整张画布 35%-38% 高度。
- Panels 2-7 位于 Panel 1 下方，固定排列为 `2-column by 3-row grid`。
- Panels 2-7 只能从 Panel 1 裁切、推进、反打、俯拍或侧拍，不得重新布景。
- su-image7 不再使用 `vertical 2:3 canvas`、`1024 x 1536` 或 `1536 x 2304` 作为默认最终画布；这些比例只允许用于旧产物回看，不得作为新提示词默认值。

### Strict panel geometry blueprint

英文最终提示词必须携带这一组几何硬约束，避免后续宫格变成方格、竖窄格或不规则漫画拼贴：

- `Strict panel geometry blueprint, mandatory before drawing:`
- `Treat the final canvas as a clean vertical 9:16 layout, equivalent to 1536 x 2736 layout units.`
- `Draw exactly seven separate straight rectangular panel frames with visible gutters.`
- `Panel 1: one full-width horizontal 16:9 rectangle across the top, occupying the full usable panel width.`
- `Panels 2-7: six identical lower horizontal 16:9 rectangles arranged below Panel 1 in two equal columns and three equal rows.`
- `Panels 2-7 must all have the same width, the same height, the same 16:9 aspect ratio, and aligned edges.`
- `Do not let any lower panel become square, vertical, tall, narrow, compressed, stretched, trapezoid, diagonal, rounded, or irregular.`
- `Keep gutters and margins as empty separating space. If a close-up needs more room, use empty background or negative space inside that panel; never change the panel shape or aspect ratio.`
- `Do not create a manga page, comic page, dynamic collage, masonry grid, mixed panel sizes, tilted frames, perspective-distorted frames, overlapping panels, or a poster composition.`
- `The content inside a panel may crop or zoom, but the panel frame itself must remain a flat horizontal 16:9 rectangle.`

## 标注交付层（annotation layer）

标注交付层是生图后的外部排版步骤，不属于 Image2 生图内容，严禁写入 `Image2 可复制提示词` 代码块。需要分发给同事、导演或制片审阅时，默认同时规划一版标注图：

- 原始生图保持无字；不得在 Image2 提示词里要求生成中文、镜号、场次、字幕、箭头文字或说明文字。
- 标注版在整张图最左上方页眉写中文：`场次/场景｜镜头编号范围`，例如 `13-1 赤狐岭迷雾深林 日 外｜镜头001-010`。
- 标注版在每个单独宫格下方的外部标签区写中文：`C序号｜视角｜景别｜运镜`，例如 `C1｜微俯视｜大全景｜伸缩摇臂缓慢下降`。
- `视角｜景别｜运镜` 必须只从 `shot_data.json` 的 `camera_main_image` 开头方括号读取；不得翻译成英文，不得根据画面猜写，不得用模型自行概括。
- 多镜头合并 Panel 默认使用来源范围首镜头三要素；若用户明确指定主镜头，则以用户指定主镜头为准。
- 标签区必须位于宫格外部排版层，不得压缩、遮挡、裁切或覆盖任何 16:9 宫格内容。
- 若生成 PDF、图册、PPT 或网页索引，优先使用标注版；若要继续二次生图或修图，保留无字原图。

## page-map 产出要求

后处理脚本不得猜测宫格与镜头关系。只要进入生图或标注交付，就必须同时产出 `page-map.json`。

- `page-map.json` 是标注后处理脚本的强制输入文件。
- 结构说明见 `skills/su-image-common/references/page-map-schema.md`。
- 每一页必须声明：
  - `page_no`
  - `layout`
  - `source`
  - `panels`
- 7 格页的 `panels` 必须完整覆盖 `1..7`，不得缺格。
- 每个 `panel_no` 必须明确对应 `shot_nos`；如果一个 Panel 合并多个镜头，数组首镜头就是默认三要素标签来源。
- 如果实际生图宫格几何与默认版式推导不一致，必须在 `page-map.json` 里显式写 `box`，禁止让脚本靠目测猜位置。
- 没有 `page-map.json`，不得声称可以安全生成标注版。

最小示例：

```json
{
  "pages": [
    {
      "page_no": 1,
      "layout": "7",
      "source": "page-001.png",
      "panels": [
        { "panel_no": 1, "shot_nos": [1] },
        { "panel_no": 2, "shot_nos": [2, 3] },
        { "panel_no": 3, "shot_nos": [4] },
        { "panel_no": 4, "shot_nos": [5] },
        { "panel_no": 5, "shot_nos": [6] },
        { "panel_no": 6, "shot_nos": [7] },
        { "panel_no": 7, "shot_nos": [8] }
      ]
    }
  ]
}
```

## 后处理脚本调用

后处理脚本固定使用：

`skills/su-image-common/scripts/annotate_storyboard_pages.py`

推荐调用方式：

```bash
<bundled-python> skills/su-image-common/scripts/annotate_storyboard_pages.py \
  --data <片名>.shot_data.json \
  --page-map page-map.json \
  --pages pages \
  --output annotated-pages
```

执行约束：

- 必须使用 `shot_data.json` 和 `page-map.json`，不得省略其一。
- `annotated-pages/` 中输出的是中文标注版 PNG。
- 脚本同时输出 `annotated-pages/manifest.json`，用于核对页眉和每格标签来源。
- 如果脚本报出 `camera_main_image` 三要素缺失、镜头号不存在、panel 覆盖不完整或布局不支持，必须视为交付失败，先修数据再重跑。

## 第 1 格跨栏主平面锚定

- 所有内景、外景、院落、走廊、房间、道路、车厢等连续 7 格，Panel 1 必须优先建立主平面锚定。
- 即使原始第一节点是特写、近景或反应镜头，也要把 Panel 1 改写为全景、大全景、俯视全景或主观全景锚定格。
- Panel 1 不得新增剧情事实，不得新增角色、道具、建筑、车辆、动物或对白。
- 尚未在剧情中出现的人物、道具、车辆、动物或灵异对象不得提前画出；只能锚定其未来出现的空位置、门口、房间中央、道路尽头、桌面空位等可公开空间。
- 后续近景如果裁掉家具、地形、门窗或道路，背景应保持简化或来自 Panel 1 局部；不得补画新家具、新门窗、新街道或新房间。

## 固定物与空间锁定

必须按任务实际场景输出这些中文表格：

- `空间概念`：场景边界、方向锁定、摄影机轴线、初始坐标、允许位移、禁止漂移。
- `第1格跨栏主平面锚定表`：空间类型、锚定景别、固定锚点、允许隐藏对象、后续继承规则、禁止提前揭示或重建。
- `门窗家具几何锁定表`：门的墙面、铰链侧、把手侧、开合方向；窗的墙面、内外侧和光源；家具的墙面、屏幕区域、正/侧面朝向和路径关系。
- `固定物屏幕投影表`：每格中门、床、桌、梳妆台、镜子、车门、道路入口等固定物的屏幕投影；不可见时写“裁掉/画外”，不能写成新位置。
- `前序7格布局继承表`：Panels 2-7 逐格写清继承 Panel 1 哪些锚点、哪些只允许裁切、哪些不得重画。
- `对象足迹与朝向表`、`机位编号表`、`摄影机朝向表`、`对象可见性表` 按对象和镜头关系输出。

## 车辆局部坐标与车内物理规则

只要 7 格内出现车辆、下车、车内外连续关系、车窗框中框、后排反打、车内外对话或透过车窗看人，就必须输出车辆锁定表。

- 本项目车辆默认左舵；若文字或已确认参考图明确右舵，则以来源为准，并在中文表格和英文提示词中明示。
- 必须同时区分 `vehicle left/right/front/rear` 和 `screen left/right`；禁止把车辆左右直接等同为画面左右。
- 左舵车固定推演：驾驶座 = `vehicle front-left`，副驾 = `vehicle front-right`，右后排 = `vehicle rear-right`，副驾下车后人物位于 `vehicle-right exterior side`。
- 如果角色从副驾下车，后续车内镜头只能透过同一侧车窗看到该角色。
- `vehicle rear-right seat is directly adjacent to the vehicle-right rear door/window.`
- 若被拍人物在 `vehicle rear-right`，摄影机应在 `vehicle rear-left or rear-center-left`，斜拍向 `vehicle rear-right` 和他身旁的右后窗；摄影机不能占掉被拍人物座位。
- 车内镜头必须写清摄影机所在座位/区域、镜头朝向哪侧车窗、窗外继承 Panel 1 的哪部分外景锚点。

必填车辆表：

- `车辆舵向与座位锁定表`
- `车辆局部坐标与屏幕投影表`
- `车辆座位-车窗邻接表`
- `车内摄影机占位表`
- `车内外同侧窗口关系表`

## 对视轴线与反打锁定

当出现两人对视、对话、正反打、过肩、反应近景或关系近景时，必须先输出 `对视轴线与反打锁定表`。

- 写清谁在轴线 A 端、谁在轴线 B 端、摄影机允许停在哪一侧、禁止跨到哪一侧。
- 锁定 `screen left` / `screen right`；反打时只能裁切、换景别或换焦点，不得左右互换。
- 过肩和反打必须指定肩位，不得只写“过肩”“反打”“over the shoulder”或“reverse angle”。
- 英文 Panel 描述必须包含同侧轴线、具体肩位、`screen left/screen right` 和 `Do not cross the axis or swap screen sides.`

## 七格取舍

- 有主表时，按用户指定场景、镜号范围或若干镜头生成，不重新拆主表，不改变镜号含义。
- 来源节点少于 7 个时，用同一镜头内的可见阶段、景别、角度、关键反应或道具细节补足。
- 来源节点多于 7 个时，只保留最能表达空间关系、动作推进、道具变化、情绪转折和收尾状态的 7 个节点。
- Panel 1 固定服务主平面锚定；Panels 2-7 承接剧情推进。
- 每格必须写清主体、动作、景别、观察角度、构图、空间关系、角色朝向、距离、互动对象、情绪可见方式、道具位置/归属/变化和动作结果。

## 英文最终提示词结构

最终 `Image2 可复制提示词` 按以下顺序组织：

1. Deliverable
2. Style
3. Global continuity rules
4. Reference usage 或 Text-derived layout
5. Panel 1 full-width master spatial anchor
6. Door/window/furniture geometry lock
7. Vehicle handedness and local coordinate lock
8. Seat-window adjacency and interior camera occupancy lock
9. Camera map
10. Eyeline axis and reverse-shot lock
11. Object visibility and boundaries
12. Panel 1-7
13. Negative constraints

必须包含硬词：

- `Generate one vertical 9:16 canvas, equivalent to 1536 x 2736, containing a clean 7-panel storyboard sheet.`
- `Each of the 7 panels must be a horizontal 16:9 storyboard frame.`
- `Panel 1 is a full-width master spatial layout anchor across the top.`
- `Panels 2-7 are arranged below Panel 1 in a clean 2-column by 3-row grid.`
- `All Panels 2-7 must be derived from the same Panel 1 layout.`
- `Do not make the overall canvas horizontal 16:9; only the individual panels are horizontal 16:9 frames.`
- `Do not generate any text, labels, captions, panel numbers, scene headers, shot numbers, subtitles, arrows, or watermarks inside the image.`
- `Strict panel geometry blueprint, mandatory before drawing:`
- `Treat the final canvas as a clean vertical 9:16 layout, equivalent to 1536 x 2736 layout units.`
- `Panels 2-7: six identical lower horizontal 16:9 rectangles arranged below Panel 1 in two equal columns and three equal rows.`
- `Do not let any lower panel become square, vertical, tall, narrow, compressed, stretched, trapezoid, diagonal, rounded, or irregular.`
- `rough black-and-white pencil storyboard sketch`
- `low-detail faces`
- `light gray shading only`

否定约束固定包含：`No photorealism, no film still look, no realistic skin texture, no cinematic lighting, no polished illustration, no manga page, no comic page layout, no dynamic collage, no masonry grid, no poster composition, no color, no text inside the image, no labels, no subtitles, no arrows, no watermarks, no square panels, no vertical panels, no tall panels, no narrow panels, no mixed-size lower panels.`

## 生图与验收

只有用户明确要求生图或 ZIP 时才生图。每段提示词生成一张独立 7 格 9:16 无字 PNG，推荐尺寸 `1536 x 2736`，PNG 放入 `pages/`，与 `prompts.md`、`page-map.json` 一起作为后处理输入。

若需要标注交付版，必须在无字原图生成完成后执行后处理脚本，并产出：

- `pages/*.png`
- `page-map.json`
- `annotated-pages/*.png`
- `annotated-pages/manifest.json`

原始生图目检顺序固定为：整体 9:16、推荐尺寸 `1536 x 2736`、7 格版式、每格 16:9、Panel 1 跨栏、Panels 2-7 同宽同高且均为 16:9、无方格/竖窄格/混合尺寸宫格、无画内文字、固定物几何继承、车辆局部坐标、座位-车窗邻接、车内摄影机占位、车内外同侧窗口、反打轴线、对象可见性。任一失败，收紧提示词并重生一次；最多连续重生两次。

标注版验收顺序固定为：原始 16:9 宫格比例未改变、中文页眉 `场次/场景｜镜头编号范围` 存在、每个宫格下方 `C序号｜视角｜景别｜运镜` 三要素存在、三要素逐项来自 `shot_data.json`、文字清晰、标签区不遮挡宫格、不压缩宫格、不改变宫格边框。
