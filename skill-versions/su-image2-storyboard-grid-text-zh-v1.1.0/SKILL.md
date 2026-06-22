---
name: su-image2-storyboard-grid-text-zh
version: "1.1.0"
description: 无参考图时使用。根据剧本文字、纯剧情段落、文字版分镜、Markdown/Excel 表格、局部镜号或表格截图转写内容，推演适用于 Image2/gpt-image-2 的 3x3 九宫格黑白分镜提示词 Markdown。分析表使用中文，最终 Image2 可复制提示词使用英文主导。必须锁定对视轴线、反打肩位和银幕左右关系，防止反打越轴。不得新增剧情事实，不要求补参考图，不修改 su-fenjingskill-zh 主表、Prompt 列、Storyboard 列、Excel 或校验脚本。
---

# Image2 九宫格分镜提示词｜纯文字版

## 版本

<!-- skill-version: 1.1.0 -->

用于无参考图、只依靠文字来源生成 Image2 九宫格黑白分镜提示词。文字来源可以是剧本文字、文字版分镜、主表内容、Markdown/Excel 表格、表格截图转写内容或局部镜号范围。

1.1.0 强化正反打和过肩镜头：凡出现两人对视、对话、反打、过肩、反应近景或关系近景，必须锁定对视轴线、反打肩位和银幕左右关系。

## 核心边界

- 不使用参考图规则，不输出 `资产控制`。
- 不要求用户补参考图。
- 不修改 `su-fenjingskill-zh`。
- 不回写主表，不改变镜号、原剧本段落、镜头时长、运镜主画面、备注、Prompt 列或故事板列。
- 默认输出 Markdown 提示词文件；没有明确生图要求时不生成 PNG/ZIP。
- 只从文字事实推演九格；不得为了画面丰富新增角色、新道具、新建筑、新动作结果或新对白。

如果输入中出现参考图、资产路径、角色图、场景图、俯视图、站位图、尾帧或图片编号，停止使用本 skill，改用 `../su-image2-storyboard-grid-ref-zh/SKILL.md`。

## 输入处理

按以下优先级解释文字来源：

1. 用户本轮明确要求。
2. `su-fenjingskill-zh` 主表中的镜号、场景、原剧本段落、运镜主画面、备注、Prompt、故事板列。
3. 用户提供的文字版分镜或 Markdown/Excel 表格内容。
4. 表格截图或 Excel 截图中的可见文字，需要先人工转写成结构化来源。
5. 纯剧情文本。

表格截图输入时，先识别并保留：场景号、镜头顺序、主体、动作、景别、机位、运镜、站位、空间关系、关键物体、道具归属和明确对白/动作结果。截图模糊到无法判断镜头顺序、人物归属或关键空间关系时，说明缺口并停止，不生成正式提示词。

## 工作流

1. 完整阅读全部文字来源，不截取局部句子直接规划九格。
2. 判断来源类型：主表/文字分镜/表格转写/纯剧情。
3. 建立空间概念：场景边界、方向锚定、摄影机轴线、初始坐标、允许位移、禁止漂移。
4. 建立必要锁定表：主体空间朝向、室内平面布局、前序继承、门槛边界、对象足迹、机位编号、对视轴线与反打锁定、摄影机朝向、对象可见性。
5. 从来源镜头或剧情中选取九个可见节点，写入 `九格取舍表`。
6. 生成英文主导的 `Image2 可复制提示词`。
7. 静默自检比例、风格、文字禁令、空间连续性、对象可见性和仿真词清洗。

## 空间锁定规则

- 角色、动物、车辆、道具和家具都必须以初始坐标为锚点。
- 只有文字来源明确交代位移时，才允许位置变化；必须写清起点、路径、终点。
- 后续宫格没有被文字来源提到的人、动物、车辆、道具严禁乱入。
- 同一对象不得在相邻格无理由换边、消失、出现、改变归属或改变运动方向。
- 室内场景必须先建立平面布局：门、窗、墙、床、桌、沙发、梳妆台、柜体、通道、关键道具。
- 第一个室内全景或主观全景必须承担平面建立功能。
- 近景、特写、反打、俯拍和主观视角只能从已建立平面推导，不能每格重新布置。
- 特写只能裁切空间，不能暗示家具换位；必须写清“同一家具局部”或“同一台面局部”。

## 对视轴线与反打锁定规则

当九格内出现两人对视、对话、正反打、过肩、反应近景或关系近景时，必须先锁定对视轴线。

- 必须写清谁在轴线 A 端、谁在轴线 B 端、摄影机允许停在哪一侧、禁止跨到哪一侧。
- 必须锁定银幕左右关系，例如“林晓彤保持 screen left，母亲保持 screen right”。反打时只能裁切、换景别或换焦点，不得左右互换。
- 过肩和反打必须指定肩位，例如“从母亲左肩后反打林晓彤”或“从母亲右肩后反打林晓彤”。不得只写“过肩”“反打”“over the shoulder”或“reverse angle”。
- 一旦某格建立了对视轴线，后续同一组人物关系镜头必须继承同一轴线侧和银幕左右，除非来源文字明确交代人物绕行、换位或摄影机越轴。
- 如果来源文字只写“反打”但没有肩位，生成 Markdown 时必须根据上一格空间关系主动选择一个合理肩位并锁死；不能把肩位留给 Image2 决定。
- 反打格的英文 Panel 描述必须同时包含：同侧轴线、具体肩位、screen left/screen right、`Do not cross the axis or swap screen sides.`。

## 必填表格

按任务实际场景输出以下表格。表格只写在 Markdown 中，不要求生成到图片里。

### 空间概念

```markdown
空间概念：
- 场景边界：...
- 方向锚定：...
- 摄影机轴线：...
- 初始坐标：...
- 允许位移：...
- 禁止漂移：...
```

### 主体空间朝向表

用于建筑、院门、走廊、房间、楼梯、洞口、车厢等固定空间结构。

```markdown
| 建筑/空间结构 | 初始朝向锚点 | 识别点左右关系 | 机位切换对应可见面 | 禁止错乱 |
|---|---|---|---|---|
```

室内戏可把此表转译为房间、门、窗、走廊、墙面朝向，不必强行写外立面。

### 室内平面布局表

室内、房间、车厢、教室、书房、卧室、病房、客厅、办公室、店铺必须输出。

```markdown
| 空间/家具/陈设 | 固定参照物 | 世界坐标/所靠墙面 | 与其他对象关系 | 可见格投影 | 禁止漂移 |
|---|---|---|---|---|---|
```

### 前序宫格布局继承表

同一场景连续九宫格必须输出。

```markdown
| 格 | 继承自 | 必须继承的空间锚点 | 本格新增/变化 | 本格可裁掉 | 禁止重建 |
|---|---|---|---|---|---|
```

### 门槛边界表

存在门、院门、车门、房门、走廊入口、桥、台阶、洞口、道路边线等边界时必须输出。

```markdown
| 边界 | 外侧/近侧 | 内侧/远侧 | 对象所在侧 | 允许跨越 | 禁止错乱 |
|---|---|---|---|---|---|
```

### 对象足迹与朝向表

同一对象在两个以上格可见时必须输出。

```markdown
| 对象 | 世界坐标锚点 | 占地足迹 | 固定朝向 | 可见格投影 | 禁止变化 |
|---|---|---|---|---|---|
```

### 机位编号表

同一场景连续九宫格且需要稳定空间时必须输出；每格只能绑定一个主机位。

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

写法要求：

- `关系轴线` 必须写清 A 端人物、B 端人物和轴线方向，例如“林晓彤门口端 A 到母亲房间中央端 B”。
- `摄影机所在轴线侧` 必须写清摄影机在轴线同一侧的世界位置，例如“床侧同侧”“门口东侧同侧”，不能只写“正面”或“反打”。
- `过肩/反打肩位` 必须写具体肩位；非过肩格可写“无，正面同侧机位”。
- `银幕左右关系` 必须写 `screen left` / `screen right`，并说明反打是否保持或裁切该关系。
- `禁止跨轴` 必须明确“不得越过对视轴到另一侧、不得交换人物银幕左右、不得把前景肩位换肩”。

### 摄影机朝向表

来自分镜表、截图或剧情文本时必须输出。

```markdown
| 格 | 摄影机位置 | 镜头朝向 | 主体朝向 | 背景应见 | 背景禁见 |
|---|---|---|---|---|---|
```

### 对象可见性表

来自分镜表、截图或剧情文本时必须输出。

```markdown
| 对象 | 可见格 | 画外格 | 锁定说明 |
|---|---|---|---|
```

画外对象不得以远景、背景、小黑点、倒影、阴影或类似轮廓出现。同一对象同一格不能同时可见又画外。

### 九格取舍表

来自分镜表、截图或长剧情时必须输出。

```markdown
| 格 | 来源镜头 | 保留画面事实 | 取舍理由 |
|---|---|---|---|
```

## 九格规则

- 有主表时，按用户指定场景、镜号范围或若干镜头生成，不重新拆主表，不改变镜号含义。
- 主表镜头少于九个时，用同一镜头内的可见阶段、景别、角度、关键反应或道具细节补足。
- 主表镜头多于九个时，只保留最关键的九个视觉节点，不删改主表事实。
- 只有纯剧情时，从文本推演九个可见画面节点；节点不足时用同一剧情状态的不同景别、角度、构图、角色反应、道具细节或空间观察方式补足。
- 每格必须写清主体、动作、景别、观察角度、构图、空间关系、角色朝向、距离、互动对象、情绪可见方式、道具位置/归属/变化和动作结果。

## 英文最终提示词结构

最终 `Image2 可复制提示词` 使用英文主导，按以下顺序组织：

1. Deliverable。
2. Style。
3. Global continuity rules。
4. Text-derived layout。
5. Camera map。
6. Eyeline axis and reverse-shot lock。
7. Object visibility and boundaries。
8. Panel 1-9。
9. Negative constraints。

必须包含这些硬词：

- `Generate one wide horizontal 16:9 canvas containing a clean 3x3 storyboard grid.`
- `Each of the 9 panels must also be a horizontal 16:9 storyboard frame.`
- `rough black-and-white pencil storyboard sketch`
- `low-detail faces`
- `light gray shading only`

推荐骨架：

```text
Generate one wide horizontal 16:9 canvas containing a clean 3x3 storyboard grid. Each of the 9 panels must also be a horizontal 16:9 storyboard frame, not square, not vertical. Use rough black-and-white pencil storyboard sketch style, director thumbnail boards, simple linework, light gray shading only, low-detail faces, clear camera angles, clear room layout, clear object positions, and clear character blocking. Layout and spatial readability are the priority.

The 9 panels are one continuous visual sequence. Preserve the same world coordinates, camera axis, furniture footprint, object ownership, door/window/wall positions, character identity, and movement path unless the source text explicitly states movement. Camera changes may crop or reproject objects, but must not move, mirror, duplicate, or swap fixed objects.

Text-derived layout:
- Space boundary: ...
- Direction anchor: ...
- Initial object positions: ...
- Allowed movement: ...
- Forbidden drift: ...

Camera map:
- Camera A: fixed position..., lens direction..., used by Panels...
- Camera B: fixed position..., lens direction..., used by Panels...

Eyeline axis and reverse-shot lock:
- Establish the eyeline axis between [Character A] at [world position] and [Character B] at [world position].
- Keep [Character A] on screen left and [Character B] on screen right throughout this relationship beat.
- For reverse shots, stay on the same side of the eyeline axis. Specify the exact shoulder position, such as: Shoot over the mother's left shoulder toward Lin Xiaotong. Keep Lin Xiaotong on screen left and the mother foreground shoulder on screen right. Do not cross the axis or swap screen sides.
- Never write only "reverse angle", "over the shoulder", or "relationship close shot" unless the same sentence also states the shoulder side and screen-left/screen-right relationship.

Object visibility and boundaries:
- [Object]: visible only in Panels..., completely off-screen in Panels...
- [Door/boundary]: [object/person] may cross only in Panel...

Panel 1: ...
Panel 2: ...
Panel 3: ...
Panel 4: ...
Panel 5: ...
Panel 6: ...
Panel 7: ...
Panel 8: ...
Panel 9: ...

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

同时禁止要求正方形画布、竖版画布、单张方形拼贴、照片级写实或彩色电影感。

## 画内文字禁令

默认禁止任何画内文字，不要要求 Image2 在图里生成镜号、格号、角色名、台词、字幕、旁白、说明文字、方位标注、箭头文字或水印。Markdown 中的 `Panel 1` 到 `Panel 9` 只用于阅读和复制，不是画面内容。

## 生图追加规则

只有用户明确要求“生图、批量生成、按 Markdown 生成图片、按文件内提示词生成宫格图、输出 ZIP”时才生图。

生图时：

- 读取 Markdown 内每段 `Image2 可复制提示词`。
- 每段生成一张独立 3x3 九宫格 PNG。
- PNG 放入 `pages/`，与 `prompts.md` 一起打包 ZIP。
- 交付前必须打开 PNG 目检。
- 若格数、比例、黑白草图风格、空间连续性、对象可见性、画内文字、反打越轴、人物左右互换、过肩方向不明任一失败，收紧提示词并重生一次；最多连续重生两次。

## 输出前自检

- 是否没有参考图输入；若有，是否已改用参考图版。
- 是否完整阅读全部文字来源。
- 是否没有新增来源外角色、道具、剧情或对白。
- 是否输出必要的空间、平面、继承、门槛、足迹、机位、摄影机、可见性和取舍表。
- 存在对话、对视、反打、过肩或关系近景时，是否输出 `对视轴线与反打锁定表`。
- 每个反打格是否写明具体肩位，而不是只写“反打”“过肩”“reverse angle”或“over the shoulder”。
- 相邻关系格是否保持同一组人物的 `screen left` / `screen right` 连续。
- 英文 Panel 描述是否继承了中文表中的轴线侧、肩位和禁止跨轴要求。
- 是否最终提示词为英文主导。
- 是否包含整体 16:9、每格 16:9、3x3、黑白铅笔分镜硬词。
- 是否没有画内文字。
- 是否没有把仿真导向词写成正向要求。
