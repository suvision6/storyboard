---
name: su-image2-storyboard-grid-text-zh
version: "1.5.0"
description: "无参考图时使用。根据剧本文字、纯剧情段落、文字版分镜、Markdown/Excel 表格、局部镜号或表格截图转写内容，推演适用于 Image2/gpt-image-2 的 7 格 2:3 竖版跨栏锚定分镜提示词 Markdown。分析表使用中文，最终 Image2 可复制提示词使用英文主导。默认生成 7-panel vertical 2:3 storyboard sheet：整体画布为 vertical 2:3，第 1 格为顶部全宽 horizontal 16:9 主平面锚定格，下方 6 格为 2-column by 3-row grid，7 个宫格全部为 horizontal 16:9 storyboard frames。必须锁定门窗家具几何、车辆舵向与座位、车辆局部坐标、座位-车窗邻接、车内摄影机占位、车内外同侧窗口关系、固定物屏幕投影、对视轴线、反打肩位和银幕左右关系。不得新增剧情事实，不要求补参考图，不修改 su-fenjingskill-zh 主表、Prompt 列、Storyboard 列、Excel 或校验脚本。"
---

# Image2 7 格分镜提示词｜纯文字版

## 版本

<!-- skill-version: 1.5.0 -->

用于无参考图、只依靠文字来源生成 Image2 7 格 2:3 竖版黑白分镜提示词。文字来源可以是剧本文字、文字版分镜、主表内容、Markdown/Excel 表格、表格截图转写内容或局部镜号范围。

1.5.0 强化单格比例与车辆内景物理可拍性：整体故事板继续为 `vertical 2:3 canvas`，但 7 个宫格全部必须是 `horizontal 16:9 storyboard frames`；第 1 格为顶部全宽 16:9 跨栏锚定格，约占整张画布 35%-38% 高度。同时新增座位-车窗邻接与车内摄影机占位规则，防止车内镜头为了构图把人物移出原座位。

1.4.0 强化车辆局部坐标：本项目车辆默认左舵；出现车内外连续关系、下车、车窗框中框、后排反打或车内外对话时，必须明示左舵/右舵，锁定 `vehicle left/right/front/rear`、座位、下车侧、窗口侧和 `screen left/right` 投影，不得让 Image2 自行推断。

1.3.0 默认改为 7 格 2:3 竖版跨栏锚定：第 1 格横向跨满宽作为主平面锚定格；下方 6 格按 `2-column by 3-row grid` 推进剧情。后续格只能从第 1 格裁切、推进、反打、俯拍或侧拍，不得重新布景。5 格暂不作为默认规则。

## 核心边界

- 不使用参考图规则，不输出资产控制表。
- 不要求用户补参考图。
- 不修改 `su-fenjingskill-zh`。
- 不回写主表，不改变镜号、原剧本段落、镜头时长、运镜主画面、备注、Prompt 列或 Storyboard 列。
- 默认输出 Markdown 提示词文件；没有明确生图要求时不生成 PNG/ZIP。
- 只从文字事实推演 7 格；不得为了画面丰富新增角色、新道具、新建筑、新动作结果或新对白。
- 第 1 格跨栏主平面锚定优先级高于原始镜头景别，但低于“不新增剧情事实”和“不提前揭示隐藏对象”。
- 若输入出现参考图、资产路径、角色图、场景图、俯视图、站位图、尾帧或图片编号，停止使用本 skill，改用 `../su-image2-storyboard-grid-ref-zh/SKILL.md`。

## 工作流

1. 完整阅读全部文字来源，不截取局部句子直接规划 7 格。
2. 判断来源类型：主表、文字分镜、表格转写或纯剧情。
3. 建立空间概念：场景边界、方向锁定、摄影机轴线、初始坐标、允许位移、禁止漂移。
4. 建立第 1 格跨栏主平面锚定：无论原始第一节点是否为近景/特写，都先用跨栏大画幅锁定可公开空间、固定物、人物起点和运动路径。
5. 输出必填表格：空间概念、第 1 格跨栏主平面锚定、门窗家具几何锁定、车辆舵向与座位锁定、车辆局部坐标与屏幕投影、车辆座位-车窗邻接、车内摄影机占位、车内外同侧窗口关系、固定物屏幕投影、前序 7 格布局继承、对象足迹、机位编号、对视轴线与反打锁定、摄影机朝向、对象可见性、七格取舍。
6. 从来源镜头或剧情中选取 7 个可见节点，写入 `七格取舍表`。
7. 生成英文主导的 `Image2 可复制提示词`。
8. 输出前自检版式、画内文字禁令、固定物几何继承、反打轴线、对象可见性和仿真词清洗。

## 7 格版式规则

- 整体画布必须为竖版 `2:3`。
- 每个宫格都必须是横向 `16:9` 分镜画幅；整体画布不能改成横向 16:9。
- 第 1 格必须横向跨满宽，位于画面上方，是 horizontal 16:9 主平面锚定格，占整张画面约 35%-38% 高度。
- 第 1 格必须是主平面锚定格，不是普通剧情格；它只建立可公开空间、固定物、人物起点和运动路径。
- 第 2-7 格位于第 1 格下方，固定排列为 `2-column by 3-row grid`，每格同样必须是 horizontal 16:9 storyboard frame。
- 第 2-7 格只推进剧情，必须从第 1 格裁切、推进、反打、俯拍或侧拍，不得重新布景。
- 不得在最终提示词中要求横版总画布、等权七格、普通拼贴或未跨栏的第 1 格。

## 第 1 格跨栏主平面锚定规则

- 所有内景、外景、院落、走廊、房间、道路、车厢等连续 7 格，第 1 格必须优先建立主平面锚定。
- 即使原始剧情第一节点是特写、近景或反应镜头，也要把第 1 格改写为全景、大全景、俯视全景或主观全景锚定格。
- 第 1 格不得新增剧情事实，不得新增角色、道具、建筑、车辆、动物或对白。
- 尚未在剧情中出现的人物、道具、车辆、动物或灵异对象不得提前画出。
- 第 1 格只允许锚定未来出现对象所在的空位置、门口、房间中央、道路尽头、桌面空位等可公开空间区域。
- 后续 2-7 格只能从第 1 格建立的空间、家具、地形、门窗、道路、人物起点和运动路径中裁切、推进、反打、俯拍或侧拍。
- 后续近景如果裁掉家具、地形、门窗或道路，背景应保持简化或来自第 1 格局部；不得补画新家具、新门窗、新街道或新房间。

## 门窗家具几何锁定规则

- 每个门必须锁定：所在墙面、屏幕区域、铰链侧、把手侧、开合方向、门内侧/外侧可见面。
- 每个窗必须锁定：所在墙面、窗框方向、可见内/外侧、是否可作为光源。
- 每件关键家具必须锁定：所靠墙面、屏幕区域、正面/侧面朝向、与门窗和人物路径的关系。
- 后续格若固定物可见，必须继承第 1 格几何；若不可见，只能裁掉或简化背景，不能重画成另一套门窗家具。
- 门口近景、门把手特写、反打背景、俯拍全景必须继承同一扇门的铰链侧、把手侧和开合方向，不得镜像。

## 车辆舵向与局部坐标锁定规则

只要 7 格内出现车辆、下车、车内外连续关系、车窗框中框、后排反打、车内外对话或透过车窗看人，就必须先锁定车辆局部坐标。

- 本项目车辆默认左舵；若文字明确右舵，则以文字为准，并在表格和英文提示词中明示。
- 每个车辆场景必须同时区分 `vehicle left/right/front/rear` 和 `screen left/right`，禁止把车辆左右直接等同为画面左右。
- 左舵车固定推演：驾驶座 = `vehicle front-left`，副驾 = `vehicle front-right`，右后排 = `vehicle rear-right`，副驾下车后人物位于 `vehicle-right exterior side`。
- 如果角色从副驾下车，必须锁定其下车侧、车门侧、车窗侧和后续窗外位置；后续车内镜头只能透过同一侧车窗看到该角色。
- 车内镜头必须写清摄影机所在座位/车内区域、镜头朝向哪一侧车窗、窗外应继承第 1 格的哪部分外景锚点。
- 类似 12-1 的左舵车场景应锁为：车辆投影在画左，乘客侧/车辆右侧朝画右，林晓彤位于画右；沈夜坐右后排，后续车内镜头透过同一侧右后窗看到窗外的林晓彤。
- 若车辆舵向、座位、下车侧或车窗侧无法从文字推演，也必须按项目默认左舵显式声明，不能留给 Image2 自行决定。
- 生图或复核时，只要车外人物下车侧与车内窗口侧不一致、车内镜头看向错误车窗、后排左右座位与舵向不一致，判定失败。

### 车辆座位-车窗邻接规则

- 车辆内景必须锁定每个被拍座位相邻的车门/车窗；座位不能为了露出窗户或适配构图而漂移。
- `vehicle rear-right seat is directly adjacent to the vehicle-right rear door/window.`
- 若沈夜在 `vehicle rear-right`，他必须贴近 `vehicle-right rear door/window` 内侧；不得把他移到 `vehicle rear-left` 或后排中座。
- 车内摄影机不能占掉被拍人物的座位。若被拍人物在 `vehicle rear-right`，摄影机应在 `vehicle rear-left or rear-center-left`，斜拍向 `vehicle rear-right` 和他身旁的右后窗。
- 车内镜头若要同时看到沈夜和窗外林晓彤，必须采用斜向构图：沈夜保持右后排且贴近右后窗，林晓彤位于同一右后窗外；不得为了完整展示窗户而把沈夜挪到画面另一侧。

## 对视轴线与反打锁定规则

当 7 格内出现两人对视、对话、正反打、过肩、反应近景或关系近景时，必须先锁定对视轴线。

- 必须写清谁在轴线 A 端、谁在轴线 B 端、摄影机允许停在哪一侧、禁止跨到哪一侧。
- 必须锁定银幕左右关系，例如“林晓彤保持 screen left，母亲保持 screen right”。反打时只能裁切、换景别或换焦点，不得左右互换。
- 过肩和反打必须指定肩位，例如“从母亲左肩后反打林晓彤”或“从母亲右肩后反打林晓彤”。不得只写“过肩”“反打”“over the shoulder”或“reverse angle”。
- 一旦某格建立了对视轴线，后续同一组人物关系镜头必须继承同一轴线侧和银幕左右，除非来源文字明确交代人物绕行、换位或摄影机越轴。
- 反打格的英文 Panel 描述必须同时包含：同侧轴线、具体肩位、`screen left/screen right`、`Do not cross the axis or swap screen sides.`

## 必填表格

按任务实际场景输出以下表格。表格只写在 Markdown 中，不要求生成到图片里。

### 空间概念

```markdown
空间概念：
- 场景边界：...
- 方向锁定：...
- 摄影机轴线：...
- 初始坐标：...
- 允许位移：...
- 禁止漂移：...
```

### 第1格跨栏主平面锚定表

所有连续 7 格必须输出。第 1 格是跨栏主平面锚定格，不等同于剧情第一特写。

```markdown
| 空间类型 | 第1格锚定景别 | 必须建立的固定锚点 | 允许隐藏/暂不出现对象 | 后续继承规则 | 禁止提前揭示或重建 |
|---|---|---|---|---|---|
```

### 门窗家具几何锁定表

存在门、窗、床、桌、梳妆台、镜子、车门、院门、道路入口等固定物时必须输出。

```markdown
| 固定物 | 所在墙面/区域 | 第1格屏幕区域 | 几何朝向/可见面 | 铰链/把手/开合或正侧面 | 后续可见格 | 禁止漂移 |
|---|---|---|---|---|---|---|
```

### 固定物屏幕投影表

所有有固定空间锚点的 7 格都必须输出。固定物不可见时写“裁掉”，不能写成新位置。

```markdown
| 格 | 门/入口投影 | 床/大件家具投影 | 桌/梳妆台/镜子投影 | 关键道具投影 | 背景处理 | 禁止重画 |
|---|---|---|---|---|---|---|
```

### 车辆舵向与座位锁定表

存在车辆、下车、车内镜头、车窗框中框或车内外连续关系时必须输出。

```markdown
| 车辆默认舵向 | 驾驶座 | 副驾 | 后排左座 | 后排右座 | 角色座位/下车侧 | 来源依据 |
|---|---|---|---|---|---|---|
```

### 车辆局部坐标与屏幕投影表

存在车辆时必须输出。必须同时写车辆坐标和屏幕投影，禁止混用。

```markdown
| 格 | vehicle front/rear | vehicle left/right | screen left/right 投影 | 可见车侧 | 禁止镜像 |
|---|---|---|---|---|---|
```

### 车内外同侧窗口关系表

存在车窗、车内外对话、后排反打或透过车窗看人时必须输出。

```markdown
| 格 | 车内人物座位 | 车窗侧 | 窗外人物位置 | 摄影机位置 | 镜头朝向 | 必须继承的外景锚点 |
|---|---|---|---|---|---|---|
```

### 车辆座位-车窗邻接表

存在车内人物、车内镜头、车窗框中框或后排反打时必须输出。

```markdown
| 车辆舵向 | 座位 | 相邻车门/车窗 | 角色 | 是否允许离开该座位 | 禁止漂移 |
|---|---|---|---|---|---|
```

### 车内摄影机占位表

存在车内镜头时必须输出。摄影机占用位置不得与被拍人物座位冲突。

```markdown
| 格 | 摄影机占用位置 | 被拍人物座位 | 镜头朝向 | 可见车窗 | 禁止占位冲突 |
|---|---|---|---|---|---|
```

### 前序7格布局继承表

每个后续格必须写清继承第 1 格哪些锚点、哪些只允许裁切、哪些不得重画。

```markdown
| 格 | 继承自 | 必须继承的空间锚点 | 本格新增/变化 | 本格可裁掉 | 禁止重建 |
|---|---|---|---|---|---|
```

### 对象足迹与朝向表

```markdown
| 对象 | 世界坐标锚点 | 占地足迹 | 固定朝向 | 可见格投影 | 禁止变化 |
|---|---|---|---|---|---|
```

### 机位编号表

每格只能绑定一个主机位。

```markdown
| 机位 | 平面图位置 | 镜头朝向 | 服务格 | 应见背景 | 禁止背景 | 继承说明 |
|---|---|---|---|---|---|---|
```

### 对视轴线与反打锁定表

只要存在对话、对视、反打、过肩、双人关系近景或反应近景，就必须输出。

```markdown
| 格 | 关系轴线 | 摄影机所在轴线侧 | 过肩/反打肩位 | 银幕左右关系 | 禁止跨轴 |
|---|---|---|---|---|---|
```

### 摄影机朝向表

```markdown
| 格 | 摄影机位置 | 镜头朝向 | 主体朝向 | 背景应见 | 背景禁见 |
|---|---|---|---|---|---|
```

### 对象可见性表

```markdown
| 对象 | 可见格 | 画外格 | 锁定说明 |
|---|---|---|---|
```

画外对象不得以远景、背景、小黑点、倒影、阴影或类似轮廓出现。同一对象同一格不能同时可见又画外。

### 七格取舍表

来自分镜表、截图或长剧情时必须输出。

```markdown
| 格 | 来源镜头 | 保留画面事实 | 取舍理由 |
|---|---|---|---|
```

## 7 格取舍规则

- 有主表时，按用户指定场景、镜号范围或若干镜头生成，不重新拆主表，不改变镜号含义。
- 来源节点少于 7 个时，用同一镜头内的可见阶段、景别、角度、关键反应或道具细节补足。
- 来源节点多于 7 个时，只保留最关键的 7 个视觉节点，不删改主表事实。
- 第 1 格固定为跨栏主平面锚定格；下方第 2-7 格按剧情推进。
- 第 2-7 格通常压缩为：触发变化、反应、关键人物/对象出现、同侧反打、关系推进/信息揭示、收束动作。按来源事实调整，不新增剧情。
- 每格必须写清主体、动作、景别、观察角度、构图、空间关系、角色朝向、距离、互动对象、情绪可见方式、道具位置/归属/变化和动作结果。

## 英文最终提示词结构

最终 `Image2 可复制提示词` 使用英文主导，按以下顺序组织：

1. Deliverable
2. Style
3. Global continuity rules
4. Text-derived layout
5. Panel 1 full-width master spatial anchor
6. Door/window/furniture geometry lock
7. Vehicle handedness and local coordinate lock
8. Seat-window adjacency and interior camera occupancy lock
9. Camera map
10. Eyeline axis and reverse-shot lock
11. Object visibility and boundaries
12. Panel 1-7
13. Negative constraints

必须包含这些硬词：

- `Generate one vertical 2:3 canvas containing a clean 7-panel storyboard sheet.`
- `Each of the 7 panels must be a horizontal 16:9 storyboard frame.`
- `Panel 1 is a full-width master spatial layout anchor across the top.`
- `Panels 2-7 are arranged below Panel 1 in a clean 2-column by 3-row grid.`
- `All Panels 2-7 must be derived from the same Panel 1 layout.`
- `Do not make the overall canvas horizontal 16:9; only the individual panels are horizontal 16:9 frames.`
- `rough black-and-white pencil storyboard sketch`
- `low-detail faces`
- `light gray shading only`

推荐骨架：

```text
Generate one vertical 2:3 canvas containing a clean 7-panel storyboard sheet. Each of the 7 panels must be a horizontal 16:9 storyboard frame. Panel 1 is a full-width master spatial layout anchor across the top, occupying about 35-38 percent of the canvas height. Panels 2-7 are arranged below Panel 1 in a clean 2-column by 3-row grid, and each lower panel is also a horizontal 16:9 storyboard frame. Do not make the overall canvas horizontal 16:9; only the individual panels are horizontal 16:9 frames. Use rough black-and-white pencil storyboard sketch style, director thumbnail boards, simple linework, light gray shading only, low-detail faces, clear camera angles, clear object positions, and clear character blocking.

The 7 panels are one continuous visual sequence. Preserve the same world coordinates, fixed-object geometry, door/window/furniture footprint, object ownership, character identity, and movement path unless the source text explicitly states movement.

Text-derived layout:
- Space boundary: ...
- Direction anchor: ...
- Initial object positions: ...
- Allowed movement: ...
- Forbidden drift: ...

Panel 1 full-width master spatial anchor:
- Panel 1 is a full-width master spatial layout anchor across the top.
- Panel 1 establishes all source-supported visible space, fixed objects, character starting positions, and movement paths.
- All Panels 2-7 must be derived from the same Panel 1 layout.
- Do not reveal characters, props, vehicles, animals, or supernatural figures before the source text introduces them.

Door/window/furniture geometry lock:
- Door/entrance: wall or region..., screen area..., hinge side..., handle side..., swing/open direction..., visible interior/exterior face...
- Key furniture: wall or region..., screen area..., front/side orientation..., relation to door and movement path...
- If a fixed object is not visible in a later panel, crop it out or simplify the background. Do not redraw it in a new place.

Vehicle handedness and local coordinate lock:
- For this project, use a left-hand-drive sedan unless the source text explicitly states a right-hand-drive vehicle.
- Vehicle-local coordinates are independent from screen left and screen right.
- Driver seat is vehicle front-left, front passenger seat is vehicle front-right, rear-left seat is vehicle rear-left, and rear-right seat is vehicle rear-right.
- If a character exits from the front passenger seat, that character exits to the vehicle-right exterior side. Keep the same side for later window views.
- For vehicle interior shots, state the exact seat or interior camera position, the exact window side, and the exterior anchor visible through that window.
- Example for scene 12-1: Shen Ye sits in vehicle rear-right, Lin Xiaotong exits to the vehicle-right passenger side, and the interior shot looks toward the same vehicle-right passenger-side rear window. Do not mirror the car, do not move her to the opposite side, and do not swap vehicle-left with vehicle-right.

Seat-window adjacency and interior camera occupancy lock:
- vehicle rear-right seat is directly adjacent to the vehicle-right rear door/window.
- A character seated in vehicle rear-right must remain directly adjacent to the vehicle-right rear door/window and must not be moved to vehicle rear-left or the center seat for composition.
- Camera is at vehicle rear-left or rear-center-left, looking diagonally toward Shen Ye in vehicle rear-right and the vehicle-right rear window. Shen Ye must remain directly adjacent to the vehicle-right rear door/window. Do not place him in vehicle rear-left or center seat. Lin Xiaotong is outside that same vehicle-right rear window.

Camera map:
- Camera A: fixed position..., lens direction..., used by Panel 1.
- Camera B: cropped/pushed-in/reverse/high-angle/side-angle view derived from Panel 1..., used by Panel...

Eyeline axis and reverse-shot lock:
- Establish the eyeline axis between [Character A] at [world position] and [Character B] at [world position].
- Keep [Character A] on screen left and [Character B] on screen right throughout this relationship beat.
- For reverse shots, stay on the same side of the eyeline axis and specify the exact shoulder side. Do not cross the axis or swap screen sides.

Object visibility and boundaries:
- [Object]: visible only in Panels..., completely off-screen in Panels...
- [Door/boundary]: [object/person] may cross only in Panel...

Panel 1: full-width master spatial layout anchor...
Panel 2: derived from Panel 1...
Panel 3: derived from Panel 1... If Panel 3 is inside a sedan, the camera is at vehicle rear-left or rear-center-left, looking diagonally toward Shen Ye in vehicle rear-right and the vehicle-right rear window. Shen Ye must remain directly adjacent to the vehicle-right rear door/window. Do not place him in vehicle rear-left or center seat. Lin Xiaotong is outside that same vehicle-right rear window. Do not mirror the car, do not move her to the opposite side, and do not swap vehicle-left with vehicle-right.
Panel 4: derived from Panel 1...
Panel 5: derived from Panel 1...
Panel 6: derived from Panel 1...
Panel 7: derived from Panel 1...

No photorealism, no film still look, no realistic skin texture, no cinematic lighting, no polished illustration, no manga page, no poster composition, no color, no text inside the image, no labels, no subtitles, no arrows, no watermarks.
```

## 最终提示词清洗

以下词不得作为正向风格、画面质量或摄影质感要求出现；只允许在固定否定句中用于排除：

- `realistic cinematic framing`
- `photorealistic`
- `film still`
- `real skin texture`
- `highly detailed face`
- `cinematic lighting`
- `realistic photography`
- `photo-real`
- `beautiful portrait`

同时禁止要求横版总画布、等权七格、普通拼贴、照片级写实或彩色电影感。

## 画内文字禁令

默认禁止任何画内文字，不要要求 Image2 在图里生成格号、角色名、台词、字幕、旁白、说明文字、方位标注、箭头文字或水印。Markdown 中的 `Panel 1` 到 `Panel 7` 只用于阅读和复制，不是画面内容。

## 生图追加规则

只有用户明确要求“生图、批量生成、按 Markdown 生成图片、按文件内提示词生成分镜图、输出 ZIP”时才生图。

生图时：

- 读取 Markdown 内每段 `Image2 可复制提示词`。
- 每段生成一张独立 7 格 2:3 PNG。
- PNG 放入 `pages/`，与 `prompts.md` 一起打包 ZIP。
- 交付前必须打开 PNG 目检。
- 目检顺序固定为：整体 2:3、7 格版式、每格 16:9、第 1 格跨栏、无画内文字、固定物几何继承、车辆局部坐标、座位-车窗邻接、车内摄影机占位、反打轴线、对象可见性。
- 若整体比例、格数、版式、任一宫格不是 horizontal 16:9、第 1 格跨栏、黑白草图风格、画内文字、门方向/把手/铰链漂移、家具/地形/门窗/道路重排、近景补出新背景、左舵/右舵未明示、座位与车辆舵向不一致、车外人物下车侧与车内窗户侧不一致、车内镜头看向错误车窗、沈夜未贴近右后门/右后窗、摄影机占掉沈夜座位、人物被挪到后排左座/中座、`vehicle left/right` 被当成 `screen left/right` 镜像、反打越轴、人物左右互换、对象可见性任一失败，收紧提示词并重生一次；最多连续重生两次。

## 输出前自检

- 是否没有参考图输入；若有，是否已改用参考图版。
- 是否完整阅读全部文字来源。
- 是否没有新增来源外角色、道具、剧情或对白。
- 是否输出 `第1格跨栏主平面锚定表`，并确认第 1 格是全宽跨栏大锚定格。
- 是否输出 `门窗家具几何锁定表` 和 `固定物屏幕投影表`。
- 存在车辆、下车、车内镜头或车窗框中框时，是否输出 `车辆舵向与座位锁定表`、`车辆局部坐标与屏幕投影表` 和 `车内外同侧窗口关系表`。
- 存在车内人物、车内镜头或后排反打时，是否输出 `车辆座位-车窗邻接表` 和 `车内摄影机占位表`。
- 是否确认每个宫格都是 horizontal 16:9，且整体画布仍为 vertical 2:3。
- 是否明示左舵/右舵，并区分 `vehicle left/right/front/rear` 与 `screen left/right`。
- 车外人物下车侧、车内人物座位、车窗侧和后续窗外位置是否保持同一车辆侧。
- 后排人物是否保持与对应车窗/车门邻接；摄影机是否没有占掉被拍人物座位。
- 第 1 格是否只建立可公开空间，不提前揭示后续才出现的人物、道具、车辆、动物或灵异对象。
- 前序继承表是否逐格写清第 2-7 格继承第 1 格哪些锚点、哪些只允许裁切、哪些不得重画。
- 英文最终提示词是否包含 `vertical 2:3 canvas`、`7-panel storyboard sheet`、`Each of the 7 panels must be a horizontal 16:9 storyboard frame`、`full-width master spatial layout anchor`、`2-column by 3-row grid`。
- 是否没有旧版式硬词。
- 存在对话、对视、反打、过肩或关系近景时，是否输出 `对视轴线与反打锁定表`。
- 是否最终提示词为英文主导。
- 是否没有画内文字。
- 是否没有把仿真导向词写成正向要求。
