---
name: su-image2-storyboard-grid-ref-zh
version: "1.5.1"
description: "有参考图、资产图、俯视图、站位图、尾帧、角色图、道具图或图片编号时使用。将参考资产和文字剧情转写为适用于 Image2/gpt-image-2 的 7 格 2:3 竖版跨栏锚定黑白分镜提示词 Markdown；读取 su-fenjingskill-zh 主分镜时，必须优先继承 SU Image Batch Context 和主表/台账摘要，Prompt 列只能作为镜头摘要辅助，不能作为主输入或唯一输入；先做资产/空间一致性审查，冲突或用途不清时直接任务失败并列出冲突点。最终 Image2 可复制提示词使用英文主导。默认生成 7-panel vertical 2:3 storyboard sheet：整体画布为 vertical 2:3，第 1 格为顶部全宽 horizontal 16:9 主平面锚定格，下方 6 格为 2-column by 3-row grid，7 个宫格全部为 horizontal 16:9 storyboard frames。必须服从俯视图/站位图/场景参考图的空间布局，锁定门窗家具几何、车辆舵向与座位、车辆局部坐标、座位-车窗邻接、车内摄影机占位、车内外同侧窗口关系、固定物屏幕投影、对视轴线、反打肩位和银幕左右关系。不得修改 su-fenjingskill-zh 主表、Prompt 列、Storyboard 列、Excel 或校验脚本。"
---

# Image2 7 格分镜提示词｜参考图版

## 版本

<!-- skill-version: 1.5.1 -->

用于有参考图或美术资产的 Image2 7 格 2:3 竖版黑白分镜提示词任务。参考图版的第一目标是稳定资产用途、空间布局、角色身份、道具归属、门窗家具几何和机位约束。

1.5.1 增加 SU VISION Workflow v1.1 的主分镜继承规则：读取 `su-fenjingskill-zh` 交付物时，优先读取 `SU Image Batch Context` 和主表/台账摘要，不建立另一套主连续性台账。Prompt 列只能辅助理解每镜可见动作、景别、时长和七格取舍，不得替代主表、台账、站位、迁移、道具或空间轴线。参考图若与主表/台账摘要冲突，按参考资产冲突处理，除非用户明确指定裁决方式。

1.5.0 强化单格比例与车辆内景物理可拍性：整体故事板继续为 `vertical 2:3 canvas`，但 7 个宫格全部必须是 `horizontal 16:9 storyboard frames`；第 1 格为顶部全宽 16:9 跨栏锚定格，约占整张画布 35%-38% 高度。同时新增座位-车窗邻接与车内摄影机占位规则，防止车内镜头为了构图把人物移出原座位。

1.4.0 强化车辆局部坐标：本项目车辆默认左舵；出现车内外连续关系、下车、车窗框中框、后排反打或车内外对话时，必须明示左舵/右舵，锁定 `vehicle left/right/front/rear`、座位、下车侧、窗口侧和 `screen left/right` 投影，不得让 Image2 自行推断。有参考图时，车辆舵向、座位、下车侧、车窗侧与文字冲突会触发参考资产冲突失败合同。

1.3.0 默认改为 7 格 2:3 竖版跨栏锚定：第 1 格横向跨满宽作为主平面锚定格；下方 6 格按 `2-column by 3-row grid` 推进剧情。后续格只能从第 1 格裁切、推进、反打、俯拍或侧拍，不得重新布景。有俯视图、站位图或场景参考图时，第 1 格必须优先服从该空间参考；冲突时触发参考资产冲突失败合同。

## 核心边界

- 只读取用户提供的参考图、资产说明、主表、文字分镜或剧情文本。
- 不修改 `su-fenjingskill-zh`。
- 不回写主表，不改变镜号、原剧本段落、镜头时长、运镜主画面、备注、Prompt 列或 Storyboard 列。
- 默认输出 Markdown 提示词文件；没有明确生图要求时不生成 PNG/ZIP。
- 参考图只转写成具体可生成控制信息，不在最终提示词中写“如图所示”“严格参考图片”“根据图片”。
- 只有角色/道具参考图而没有空间参考时，不从角色/道具图臆造空间；第 1 格按文字推演主平面锚定。
- 不建立或维护另一套主连续性台账；只把 `su-fenjing` 台账摘要转译成局部图像连续性锁定表。
- 不得只读取 `su-fenjing` 的 Prompt 列生成正式生图提示词。
- 5 格暂不作为默认规则。

## 连续性继承输入

当输入来自 `su-fenjingskill-zh` 已验收分镜表时，先读取当前批次的 `SU Image Batch Context`：

```text
主分镜版本
场景名
镜号范围
对应主表行
对应 continuity_logs 场景摘要
当前镜号范围涉及的 continuity_updates
visible_characters
visible_props
固定物、门窗、道路、车辆、道具摘要
允许位移与禁止漂移
参考图用途说明
```

输入优先级固定为：

1. `shot_data.json` 中的 `continuity_logs`、`continuity_updates`、`shots`、`visible_characters`、`visible_props`
2. 主表前 6 列和已确认参考资产控制信息
3. Prompt 列，仅作摘要辅助

将 `su-fenjing` 台账摘要转译为本 skill 的 `空间概念`、`第1格跨栏主平面锚定表`、`前序7格布局继承表`、`对象可见性表`、`对视轴线与反打锁定表`。如果参考图与主表/台账摘要在人物站位、门窗家具、车辆侧别、道具归属或运动路径上冲突，必须触发参考资产冲突失败合同，不得静默改写主连续性。

## 先决失败规则

在生成任何正式 Markdown 提示词之前，先做资产/空间一致性审查。以下情况必须失败并停止：

- 图片用途不清或资产编号无法匹配。
- 俯视图/站位图与透视参考图发生空间冲突。
- 用户文字与参考图中的门、窗、床、桌、角色站位、机位、道具归属发生冲突。
- 参考图与用户文字对第 1 格跨栏主平面锚定、门窗家具几何、人物站位、人物起点或运动路径发生冲突。
- 参考图与用户文字对车辆舵向、驾驶座/副驾/后排左右座位、下车侧、车窗侧、车内外同侧窗口关系发生冲突。
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
4. 建立空间概念：场景边界、方向锁定、摄影机轴线、初始坐标、允许位移、禁止漂移。
5. 建立第 1 格跨栏主平面锚定；有俯视图、站位图或场景参考图时，优先服从参考图空间。
6. 输出门窗家具几何锁定、车辆舵向与座位锁定、车辆局部坐标与屏幕投影、车辆座位-车窗邻接、车内摄影机占位、车内外同侧窗口关系、固定物屏幕投影、前序 7 格布局继承、门槛边界、对象足迹、机位编号、对视轴线与反打锁定、摄影机朝向、对象可见性等表格。
7. 从来源镜头或剧情中选取 7 个可见画面节点，写入 `七格取舍表`。
8. 生成英文主导的 `Image2 可复制提示词`。
9. 输出前自检版式、资产用途、第 1 格跨栏锚定、门窗家具几何继承、反打轴线、对象可见性和仿真词清洗。

## 7 格版式规则

- 整体画布必须为竖版 `2:3`。
- 每个宫格都必须是横向 `16:9` 分镜画幅；整体画布不能改成横向 16:9。
- 第 1 格必须横向跨满宽，位于画面上方，是 horizontal 16:9 主平面锚定格，占整张画面约 35%-38% 高度。
- 第 1 格必须是主平面锚定格，不是普通剧情格；它只建立可公开空间、固定物、人物起点和运动路径。
- 第 2-7 格位于第 1 格下方，固定排列为 `2-column by 3-row grid`，每格同样必须是 horizontal 16:9 storyboard frame。
- 第 2-7 格只推进剧情，必须从第 1 格裁切、推进、反打、俯拍或侧拍，不得重新布景。
- 有俯视图、站位图或场景图时，第 1 格跨栏锚定必须服从空间参考。

## 第 1 格跨栏主平面锚定规则

- 所有内景、外景、院落、走廊、房间、道路、车厢等连续 7 格，第 1 格必须优先建立主平面锚定。
- 即使原始剧情第一节点是特写、近景或反应镜头，也要把第 1 格改写为全景、大全景、俯视全景或主观全景锚定格。
- 第 1 格不得新增剧情事实，不得新增角色、道具、建筑、车辆、动物或对白。
- 尚未在剧情中出现的人物、道具、车辆、动物或灵异对象不得提前画出。
- 第 1 格只允许锚定未来出现对象所在的空位置、门口、房间中央、道路尽头、桌面空位等可公开空间区域。
- 后续 2-7 格只能从第 1 格建立的空间、家具、地形、门窗、道路、人物起点和运动路径中裁切、推进、反打、俯拍或侧拍。
- 后续近景如果裁掉家具、地形、门窗或道路，背景应保持简化或来自第 1 格局部；不得补画新家具、新门窗、新街道或新房间。
- 如果参考图与文字对第 1 格跨栏主平面锚定、门窗家具几何或人物站位发生冲突，输出 `任务失败：参考资产冲突` 并停止。

## 门窗家具几何锁定规则

- 每个门必须锁定：所在墙面、屏幕区域、铰链侧、把手侧、开合方向、门内侧/外侧可见面。
- 每个窗必须锁定：所在墙面、窗框方向、可见内/外侧、是否可作为光源。
- 每件关键家具必须锁定：所靠墙面、屏幕区域、正面/侧面朝向、与门窗和人物路径的关系。
- 后续格若固定物可见，必须继承第 1 格几何；若不可见，只能裁掉或简化背景，不能重画成另一套门窗家具。
- 门口近景、门把手特写、反打背景、俯拍全景必须继承同一扇门的铰链侧、把手侧和开合方向，不得镜像。

## 车辆舵向与局部坐标锁定规则

只要 7 格内出现车辆、下车、车内外连续关系、车窗框中框、后排反打、车内外对话或透过车窗看人，就必须先锁定车辆局部坐标。

- 本项目车辆默认左舵；若文字或参考图明确右舵，则以明确来源为准，并在表格和英文提示词中明示。
- 每个车辆场景必须同时区分 `vehicle left/right/front/rear` 和 `screen left/right`，禁止把车辆左右直接等同为画面左右。
- 左舵车固定推演：驾驶座 = `vehicle front-left`，副驾 = `vehicle front-right`，右后排 = `vehicle rear-right`，副驾下车后人物位于 `vehicle-right exterior side`。
- 如果角色从副驾下车，必须锁定其下车侧、车门侧、车窗侧和后续窗外位置；后续车内镜头只能透过同一侧车窗看到该角色。
- 车内镜头必须写清摄影机所在座位/车内区域、镜头朝向哪一侧车窗、窗外应继承第 1 格的哪部分外景锚点。
- 类似 12-1 的左舵车场景应锁为：车辆投影在画左，乘客侧/车辆右侧朝画右，林晓彤位于画右；沈夜坐右后排，后续车内镜头透过同一侧右后窗看到窗外的林晓彤。
- 若参考图与文字对车辆舵向、座位、下车侧或车窗侧冲突，输出 `任务失败：参考资产冲突` 并停止。
- 生图或复核时，只要车外人物下车侧与车内窗口侧不一致、车内镜头看向错误车窗、后排左右座位与舵向不一致，判定失败。

### 车辆座位-车窗邻接规则

- 车辆内景必须锁定每个被拍座位相邻的车门/车窗；座位不能为了露出窗户或适配构图而漂移。
- `vehicle rear-right seat is directly adjacent to the vehicle-right rear door/window.`
- 若沈夜在 `vehicle rear-right`，他必须贴近 `vehicle-right rear door/window` 内侧；不得把他移到 `vehicle rear-left` 或后排中座。
- 车内摄影机不能占掉被拍人物的座位。若被拍人物在 `vehicle rear-right`，摄影机应在 `vehicle rear-left or rear-center-left`，斜拍向 `vehicle rear-right` 和他身旁的右后窗。
- 车内镜头若要同时看到沈夜和窗外林晓彤，必须采用斜向构图：沈夜保持右后排且贴近右后窗，林晓彤位于同一右后窗外；不得为了完整展示窗户而把沈夜挪到画面另一侧。
- 若参考图与文字对座位-车窗邻接或摄影机占位发生冲突，按参考资产冲突处理，除非用户明确指定裁决方式。

## 对视轴线与反打锁定规则

当 7 格内出现两人对视、对话、正反打、过肩、反应近景或关系近景时，必须先锁定对视轴线。

- 必须写清谁在轴线 A 端、谁在轴线 B 端、摄影机允许停在哪一侧、禁止跨到哪一侧。
- 必须锁定银幕左右关系，例如“林晓彤保持 screen left，母亲保持 screen right”。反打时只能裁切、换景别或换焦点，不得左右互换。
- 过肩和反打必须指定肩位，例如“从母亲左肩后反打林晓彤”或“从母亲右肩后反打林晓彤”。不得只写“过肩”“反打”“over the shoulder”或“reverse angle”。
- 如果来源只写“反打”但没有肩位，生成 Markdown 时必须根据上一格空间关系主动选择一个合理肩位并锁死；不能把肩位留给 Image2 决定。
- 反打格的英文 Panel 描述必须同时包含：同侧轴线、具体肩位、`screen left/screen right`、`Do not cross the axis or swap screen sides.`

## Markdown 文件结构

默认按场景、镜号范围或剧情段组织：

```markdown
# Image2 7 格分镜提示词｜项目名或场次名

## 场景/镜号/剧情段
来源：...

资产控制：
| 文件或编号 | 我识别为 | 类型 | 控制内容 | 状态 | 备注 |
|---|---|---|---|---|---|
| ... | ... | 场景图/角色图/道具图/俯视图/站位图/尾帧 | ... | 已匹配 | ... |

俯视平面图锁定表：
| 对象/区域 | 平面图标记或识别点 | 世界坐标/所靠墙面 | 朝向/开口方向 | 与其他对象关系 | 约束 |
|---|---|---|---|---|---|

第1格跨栏主平面锚定表：
| 空间类型 | 第1格锚定景别 | 必须建立的固定锚点 | 允许隐藏/暂不出现对象 | 后续继承规则 | 禁止提前揭示或重建 |
|---|---|---|---|---|---|

门窗家具几何锁定表：
| 固定物 | 所在墙面/区域 | 第1格屏幕区域 | 几何朝向/可见面 | 铰链/把手/开合或正侧面 | 后续可见格 | 禁止漂移 |
|---|---|---|---|---|---|---|

固定物屏幕投影表：
| 格 | 门/入口投影 | 床/大件家具投影 | 桌/梳妆台/镜子投影 | 关键道具投影 | 背景处理 | 禁止重画 |
|---|---|---|---|---|---|---|

车辆舵向与座位锁定表：
| 车辆默认舵向 | 驾驶座 | 副驾 | 后排左座 | 后排右座 | 角色座位/下车侧 | 来源依据 |
|---|---|---|---|---|---|---|

车辆局部坐标与屏幕投影表：
| 格 | vehicle front/rear | vehicle left/right | screen left/right 投影 | 可见车侧 | 禁止镜像 |
|---|---|---|---|---|---|

车内外同侧窗口关系表：
| 格 | 车内人物座位 | 车窗侧 | 窗外人物位置 | 摄影机位置 | 镜头朝向 | 必须继承的外景锚点 |
|---|---|---|---|---|---|---|

车辆座位-车窗邻接表：
| 车辆舵向 | 座位 | 相邻车门/车窗 | 角色 | 是否允许离开该座位 | 禁止漂移 |
|---|---|---|---|---|---|

车内摄影机占位表：
| 格 | 摄影机占用位置 | 被拍人物座位 | 镜头朝向 | 可见车窗 | 禁止占位冲突 |
|---|---|---|---|---|---|

空间概念：
- 场景边界：...
- 方向锁定：...
- 摄影机轴线：...
- 初始坐标：...
- 允许位移：...
- 禁止漂移：...

前序7格布局继承表：
| 格 | 继承自 | 必须继承的空间锚点 | 本格新增/变化 | 本格可裁掉 | 禁止重建 |
|---|---|---|---|---|---|

门槛边界表：
| 边界 | 外侧/近侧 | 内侧/远侧 | 对象所在侧 | 允许跨越 | 禁止错乱 |
|---|---|---|---|---|---|

对象足迹与朝向表：
| 对象 | 世界坐标锚点 | 占地足迹 | 固定朝向 | 可见格投影 | 禁止变化 |
|---|---|---|---|---|---|

机位编号表：
| 机位 | 平面图位置 | 镜头朝向 | 服务格 | 应见背景 | 禁止背景 | 继承说明 |
|---|---|---|---|---|---|---|

对视轴线与反打锁定表：
| 格 | 关系轴线 | 摄影机所在轴线侧 | 过肩/反打肩位 | 银幕左右关系 | 禁止跨轴 |
|---|---|---|---|---|---|

摄影机朝向表：
| 格 | 摄影机位置 | 镜头朝向 | 主体朝向 | 背景应见 | 背景禁见 |
|---|---|---|---|---|---|

对象可见性表：
| 对象 | 可见格 | 画外格 | 锁定说明 |
|---|---|---|---|

七格取舍表：
| 格 | 来源镜头 | 保留画面事实 | 取舍理由 |
|---|---|---|---|

Image2 可复制提示词：
...
```

`俯视平面图锁定表` 仅在有俯视图、平面图、站位图或机位图时输出。`车辆舵向与座位锁定表`、`车辆局部坐标与屏幕投影表`、`车辆座位-车窗邻接表`、`车内摄影机占位表`、`车内外同侧窗口关系表` 在存在车辆、下车、车内镜头、车窗框中框或车内外连续关系时必须输出。`对视轴线与反打锁定表` 在存在对话、对视、反打、过肩、双人关系近景或反应近景时必须输出。其他锁定表只要来源中存在对应对象或边界，就必须输出。

## 7 格取舍规则

- 7 格只能保留来源镜头或剧情中可追溯的画面事实。
- 来源镜头少于 7 个时，用同一镜头内的可见阶段、景别、角度、反应、道具细节补足。
- 来源镜头多于 7 个时，保留最能表达空间关系、动作推进、道具变化、情绪转折和收尾状态的 7 个节点。
- 第 1 格固定为跨栏主平面锚定格；第 2-7 格承接剧情推进。
- 不新增角色、道具、建筑重点、动作结果或对白。
- 每格必须绑定一个主机位编号。
- 每格必须写清主体、动作、景别、观察角度、构图、朝向、距离、道具归属、情绪可见方式和动作结果。
- 反打、过肩和关系近景必须写清对视轴线侧、具体肩位和银幕左右关系；不得把轴线交给 Image2 自行判断。

## 英文最终提示词结构

最终 `Image2 可复制提示词` 使用英文主导，按以下顺序组织：

1. Deliverable
2. Style
3. Global continuity rules
4. Reference usage
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

The 7 panels are one continuous visual sequence. Preserve the same world coordinates, fixed-object geometry, door/window/furniture footprint, object ownership, character identity, and movement path unless the source text or approved reference explicitly states movement.

Reference usage:
- Reference Image 1: use only for [room layout / building layout / doorway geometry / blocking].
- Reference Image 2: use only for [character identity / outfit / body type].
- Reference Image 3: use only for [prop shape / scale / ownership].
Do not copy color, polished rendering, photographic lighting, or decorative finish unless explicitly requested. Convert all references into a rough black-and-white storyboard sketch.

Panel 1 full-width master spatial anchor:
- Panel 1 is a full-width master spatial layout anchor across the top.
- Panel 1 establishes all source-supported and approved-reference visible space, fixed objects, character starting positions, and movement paths.
- All Panels 2-7 must be derived from the same Panel 1 layout.
- If a floor plan, blocking diagram, or scene reference controls space, Panel 1 must follow that spatial reference.
- Do not reveal characters, props, vehicles, animals, or supernatural figures before the source text introduces them.

Door/window/furniture geometry lock:
- Door/entrance: wall or region..., screen area..., hinge side..., handle side..., swing/open direction..., visible interior/exterior face...
- Key furniture: wall or region..., screen area..., front/side orientation..., relation to door and movement path...
- If a fixed object is not visible in a later panel, crop it out or simplify the background. Do not redraw it in a new place.

Vehicle handedness and local coordinate lock:
- For this project, use a left-hand-drive sedan unless the source text or approved reference explicitly states a right-hand-drive vehicle.
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
- For reverse shots, stay on the same side of the eyeline axis. Specify the exact shoulder position, such as: Shoot over the mother's left shoulder toward Lin Xiaotong. Keep Lin Xiaotong on screen left and the mother foreground shoulder on screen right. Do not cross the axis or swap screen sides.
- Never write only "reverse angle", "over the shoulder", or "relationship close shot" unless the same sentence also states the shoulder side and screen-left/screen-right relationship.

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

## 生图追加规则

只有用户明确要求“生图、批量生成、按 Markdown 生成图片、按文件内提示词生成分镜图、输出 ZIP”时才生图。

生图时：

- 读取 Markdown 内每段 `Image2 可复制提示词`。
- 每段生成一张独立 7 格 2:3 PNG。
- PNG 放入 `pages/`，与 `prompts.md` 一起打包 ZIP。
- 交付前必须打开 PNG 目检。
- 目检顺序固定为：整体 2:3、7 格版式、每格 16:9、第 1 格跨栏、无画内文字、固定物几何继承、车辆局部坐标、座位-车窗邻接、车内摄影机占位、反打轴线、对象可见性。
- 若整体比例、格数、版式、任一宫格不是 horizontal 16:9、第 1 格跨栏、黑白草图风格、资产一致性、门方向/把手/铰链漂移、家具/地形/门窗/道路重排、近景补出新背景、左舵/右舵未明示、座位与车辆舵向不一致、车外人物下车侧与车内窗户侧不一致、车内镜头看向错误车窗、沈夜未贴近右后门/右后窗、摄影机占掉沈夜座位、人物被挪到后排左座/中座、`vehicle left/right` 被当成 `screen left/right` 镜像、反打越轴、人物左右互换、对象可见性、画内文字任一失败，收紧提示词并重生一次；最多连续重生两次。

## 输出前自检

- 是否先完成资产/空间一致性审查。
- 是否没有触发先决失败规则。
- 输入来自 `su-fenjingskill-zh` 时，是否已读取 `SU Image Batch Context` 或明确标注降级执行。
- 是否没有把 Prompt 列当成主输入或唯一输入。
- 是否没有建立另一套主连续性台账。
- 是否有 `资产控制`，并且每张参考图都有明确用途。
- 是否把参考图转写成具体控制信息，没有写“如图所示”。
- 是否输出 `第1格跨栏主平面锚定表`，并确认第 1 格优先服从俯视图/站位图/场景图等空间参考。
- 是否输出 `门窗家具几何锁定表` 和 `固定物屏幕投影表`。
- 存在车辆、下车、车内镜头或车窗框中框时，是否输出 `车辆舵向与座位锁定表`、`车辆局部坐标与屏幕投影表` 和 `车内外同侧窗口关系表`。
- 存在车内人物、车内镜头或后排反打时，是否输出 `车辆座位-车窗邻接表` 和 `车内摄影机占位表`。
- 是否确认每个宫格都是 horizontal 16:9，且整体画布仍为 vertical 2:3。
- 是否明示左舵/右舵，并区分 `vehicle left/right/front/rear` 与 `screen left/right`。
- 车外人物下车侧、车内人物座位、车窗侧和后续窗外位置是否保持同一车辆侧。
- 后排人物是否保持与对应车窗/车门邻接；摄影机是否没有占掉被拍人物座位。
- 如果只有角色/道具参考图，是否未从角色/道具图臆造空间，而是按文字推演第 1 格跨栏主平面锚定。
- 第 1 格是否只建立可公开空间，不提前揭示后续才出现的人物、道具、车辆、动物或灵异对象。
- 前序继承表是否逐格写清第 2-7 格继承第 1 格哪些锚点、哪些只允许裁切、哪些不得重画。
- 英文最终提示词是否包含 `vertical 2:3 canvas`、`7-panel storyboard sheet`、`Each of the 7 panels must be a horizontal 16:9 storyboard frame`、`full-width master spatial layout anchor`、`2-column by 3-row grid`。
- 存在对话、对视、反打、过肩或关系近景时，是否输出 `对视轴线与反打锁定表`。
- 每个反打格是否写明具体肩位，而不是只写“反打”“过肩”“reverse angle”或“over the shoulder”。
- 相邻关系格是否保持同一组人物的 `screen left` / `screen right` 连续。
- 英文 Panel 描述是否继承了中文表中的轴线侧、肩位和禁止跨轴要求。
- 是否最终提示词为英文主导。
- 是否没有旧版式硬词。
- 是否没有新增来源外角色、道具、剧情或对白。
- 是否没有画内文字。
- 是否没有把仿真导向词写成正向要求。
