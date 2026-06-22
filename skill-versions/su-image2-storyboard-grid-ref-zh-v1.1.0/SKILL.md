---
name: su-image2-storyboard-grid-ref-zh
version: "1.1.0"
description: 有参考图、资产图、俯视图、站位图、尾帧、角色图、道具图或图片编号时使用。将参考资产和文字剧情转写为适用于 Image2/gpt-image-2 的 3x3 九宫格黑白分镜提示词 Markdown；先做资产/空间一致性审查，冲突或用途不清时直接任务失败并列出冲突点。最终 Image2 可复制提示词使用英文主导。必须锁定对视轴线、反打肩位和银幕左右关系，防止反打越轴。不得修改 su-fenjingskill-zh 主表、Prompt 列、Storyboard 列、Excel 或校验脚本。
---

# Image2 九宫格分镜提示词｜参考图版

## 版本

<!-- skill-version: 1.1.0 -->

用于有参考图或美术资产的 Image2 九宫格黑白分镜提示词任务。参考图版的第一目标是稳定资产用途、空间布局、角色身份、道具归属和机位约束。

1.1.0 强化正反打和过肩镜头：凡出现两人对视、对话、反打、过肩、反应近景或关系近景，必须锁定对视轴线、反打肩位和银幕左右关系。

## 核心边界

- 只读取用户提供的参考图、资产说明、主表、文字分镜或剧情文本。
- 不修改 `su-fenjingskill-zh`。
- 不回写主表，不改变镜号、原剧本段落、镜头时长、运镜主画面、备注、Prompt 列或故事板列。
- 默认输出 Markdown 提示词文件；没有明确生图要求时不生成 PNG/ZIP。
- 参考图只转写成具体可生成控制信息，不在最终提示词中写“如图所示”“严格参考图片”“根据图片”。

## 先决失败规则

在生成任何正式 Markdown 提示词之前，先做资产/空间一致性审查。以下情况必须失败并停止：

- 图片用途不清或资产编号无法匹配。
- 俯视图/站位图与透视参考图发生空间冲突。
- 用户文字与参考图中的门、窗、床、桌、角色站位、机位、道具归属发生冲突。
- 多张参考图之间无法判断主次，且会影响空间布局、人物身份或道具归属。

失败时只输出以下结构，不生成正式提示词、不生成 `Image2 可复制提示词`、不生成 PNG/ZIP：

```markdown
任务失败：参考资产冲突

冲突点列表：
| 编号 | 冲突对象 | 用户文字/资产 A | 参考图/资产 B | 冲突原因 |
|---|---|---|---|---|
| 1 | ... | ... | ... | ... |

会影响的输出部分：
- ...

请用户修改/确认的具体内容：
- ...
```

如果用户本轮已经明确指定冲突裁决方式，例如“以俯视图为准，透视图只参考装修风格”，按用户裁决执行，不视为冲突。

## 资产优先级

按以下顺序解释资产；不得静默改写优先级：

1. 用户本轮明确裁决和用途说明。
2. 俯视平面图、简笔平面图、站位图。
3. 机位图、机位箭头、镜头方向说明。
4. 场景透视参考图、概念图、剧照式场景图。
5. 角色图、道具图、美术风格图。
6. 文字剧情、文字分镜、主表内容。

参考图必须转写为具体控制：

- 角色图：外貌、服装、体态、身份识别点。
- 俯视图/站位图：世界坐标、所靠墙面、朝向、人物站位、移动路线、机位位置和镜头方向。
- 场景图：空间结构、门窗、通道、家具、纵深、边界、环境基调。
- 道具图：形态、尺寸、材质、功能、被触碰或使用方式。
- 尾帧：上一段结束时的位置、朝向、距离和空间关系。

## 工作流

1. 完整阅读全部输入：文字、镜号范围、表格、截图文字、图片说明和资产路径。
2. 建立 `资产控制` 表；每张图或资产编号都要写清用途、类型、控制内容、状态和备注。
3. 执行先决失败规则；如失败，按固定失败格式输出并停止。
4. 建立空间概念：场景边界、方向锚定、摄影机轴线、初始坐标、允许位移、禁止漂移。
5. 对室内、建筑、门槛、对象足迹、机位、对视轴线与反打、可见性进行表格锁定。
6. 从来源镜头或剧情中选取九个可见画面节点，写入 `九格取舍表`。
7. 生成英文主导的 `Image2 可复制提示词`。
8. 静默自检比例、风格、文字禁令、资产用途、空间连续性和仿真词清洗。

## 对视轴线与反打锁定规则

当九格内出现两人对视、对话、正反打、过肩、反应近景或关系近景时，必须先锁定对视轴线。

- 必须写清谁在轴线 A 端、谁在轴线 B 端、摄影机允许停在哪一侧、禁止跨到哪一侧。
- 必须锁定银幕左右关系，例如“林晓彤保持 screen left，母亲保持 screen right”。反打时只能裁切、换景别或换焦点，不得左右互换。
- 过肩和反打必须指定肩位，例如“从母亲左肩后反打林晓彤”或“从母亲右肩后反打林晓彤”。不得只写“过肩”“反打”“over the shoulder”或“reverse angle”。
- 一旦某格建立了对视轴线，后续同一组人物关系镜头必须继承同一轴线侧和银幕左右，除非来源文字、参考图或站位图明确交代人物绕行、换位或摄影机越轴。
- 如果来源只写“反打”但没有肩位，生成 Markdown 时必须根据上一格空间关系主动选择一个合理肩位并锁死；不能把肩位留给 Image2 决定。
- 反打格的英文 Panel 描述必须同时包含：同侧轴线、具体肩位、screen left/screen right、`Do not cross the axis or swap screen sides.`。

## Markdown 文件结构

默认按场景、镜号范围或剧情段组织：

```markdown
# Image2 九宫格分镜提示词｜项目名或场次名

## 场景/镜号/剧情段

来源：...

资产控制：
| 文件或编号 | 我识别为 | 类型 | 控制内容 | 状态 | 备注 |
|---|---|---|---|---|---|
| ... | ... | 场景图/角色图/道具图/俯视图/站位图/尾帧 | ... | 已匹配 | ... |

俯视平面图锚定表：
| 对象/区域 | 平面图标记或识别点 | 世界坐标/所靠墙面 | 朝向/开口方向 | 与其他对象关系 | 约束 |
|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... |

空间概念：
- 场景边界：...
- 方向锚定：...
- 摄影机轴线：...
- 初始坐标：...
- 允许位移：...
- 禁止漂移：...

主体空间朝向表：
| 建筑/空间结构 | 初始朝向锚点 | 识别点左右关系 | 机位切换对应可见面 | 禁止错乱 |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |

室内平面布局表：
| 空间/家具/陈设 | 固定参照物 | 世界坐标/所靠墙面 | 与其他对象关系 | 可见格投影 | 禁止漂移 |
|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... |

前序宫格布局继承表：
| 格 | 继承自 | 必须继承的空间锚点 | 本格新增/变化 | 本格可裁掉 | 禁止重建 |
|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... |

门槛边界表：
| 边界 | 外侧/近侧 | 内侧/远侧 | 对象所在侧 | 允许跨越 | 禁止错乱 |
|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... |

对象足迹与朝向表：
| 对象 | 世界坐标锚点 | 占地足迹 | 固定朝向 | 可见格投影 | 禁止变化 |
|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... |

机位编号表：
| 机位 | 平面图位置 | 镜头朝向 | 服务格 | 应见背景 | 禁止背景 | 继承说明 |
|---|---|---|---|---|---|---|
| A | ... | ... | ... | ... | ... | ... |

对视轴线与反打锁定表：
| 格 | 关系轴线 | 摄影机所在轴线侧 | 过肩/反打肩位 | 银幕左右关系 | 禁止跨轴 |
|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... |

摄影机朝向表：
| 格 | 摄影机位置 | 镜头朝向 | 主体朝向 | 背景应见 | 背景禁见 |
|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... |

对象可见性表：
| 对象 | 可见格 | 画外格 | 锁定说明 |
|---|---|---|---|
| ... | ... | ... | ... |

九格取舍表：
| 格 | 来源镜头 | 保留画面事实 | 取舍理由 |
|---|---|---|---|
| 1 | ... | ... | ... |

Image2 可复制提示词：
...
```

`俯视平面图锚定表` 仅在有俯视图、平面图、站位图或机位图时输出。`室内平面布局表` 仅在室内或半封闭空间时输出。`对视轴线与反打锁定表` 在存在对话、对视、反打、过肩、双人关系近景或反应近景时必须输出。其他锁定表只要来源中存在对应对象或边界，就必须输出。

## 九格规则

- 九格只能保留来源镜头或剧情中可追溯的画面事实。
- 来源镜头少于九个时，用同一镜头内的可见阶段、景别、角度、反应、道具细节补足。
- 来源镜头多于九个时，保留最能表达空间关系、动作推进、道具变化、情绪转折和收尾状态的九个节点。
- 不新增角色、道具、建筑重点、动作结果或对白。
- 每格必须绑定一个主机位编号。
- 每格必须写清主体、动作、景别、观察角度、构图、朝向、距离、道具归属、情绪可见方式和动作结果。
- 反打、过肩和关系近景必须写清对视轴线侧、具体肩位和银幕左右关系；不得把轴线交给 Image2 自行判断。

## 英文最终提示词结构

最终 `Image2 可复制提示词` 使用英文主导，按以下顺序组织：

1. Deliverable。
2. Style。
3. Global continuity rules。
4. Reference usage。
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

The 9 panels are one continuous visual sequence. Preserve the same world coordinates, camera axis, furniture footprint, object ownership, door/window/wall positions, character identity, and movement path unless the source explicitly states movement. Camera changes may crop or reproject objects, but must not move, mirror, duplicate, or swap fixed objects.

Reference usage:
- Reference Image 1: use only for [room layout / building layout / prop shape / character outfit / blocking].
- Reference Image 2: use only for [character identity / outfit / body type].
Do not copy color, polished rendering, photographic lighting, or decorative finish unless explicitly requested. Convert all references into a rough black-and-white storyboard sketch.

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

## 生图追加规则

只有用户明确要求“生图、批量生成、按 Markdown 生成图片、按文件内提示词生成宫格图、输出 ZIP”时才生图。

生图时：

- 读取 Markdown 内每段 `Image2 可复制提示词`。
- 每段生成一张独立 3x3 九宫格 PNG。
- PNG 放入 `pages/`，与 `prompts.md` 一起打包 ZIP。
- 交付前必须打开 PNG 目检。
- 若格数、比例、黑白草图风格、资产一致性、空间连续性、对象可见性、画内文字、反打越轴、人物左右互换、过肩方向不明任一失败，收紧提示词并重生一次；最多连续重生两次。

## 输出前自检

- 是否先完成资产/空间一致性审查。
- 是否没有触发先决失败规则。
- 是否有 `资产控制`，并且每张参考图都有明确用途。
- 是否把参考图转写成具体控制信息，没有写“如图所示”。
- 是否输出必要的空间、平面、继承、门槛、足迹、机位、摄影机、可见性和取舍表。
- 存在对话、对视、反打、过肩或关系近景时，是否输出 `对视轴线与反打锁定表`。
- 每个反打格是否写明具体肩位，而不是只写“反打”“过肩”“reverse angle”或“over the shoulder”。
- 相邻关系格是否保持同一组人物的 `screen left` / `screen right` 连续。
- 英文 Panel 描述是否继承了中文表中的轴线侧、肩位和禁止跨轴要求。
- 是否最终提示词为英文主导。
- 是否包含整体 16:9、每格 16:9、3x3、黑白铅笔分镜硬词。
- 是否没有新增来源外角色、道具、剧情或对白。
- 是否没有画内文字。
- 是否没有把仿真导向词写成正向要求。
