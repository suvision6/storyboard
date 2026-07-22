---
name: su-image9
description: Image2/gpt-image-2 9 宫格 3x3 黑白石墨铅笔分镜提示词独立技能。用于从已验证的 shot_data.json 派生 panel_plan、page-map 和自然语言 PANEL_LAYER，并生成严格几何、统一石墨风格、保持源镜顺序与剧情事实的九格提示词。v2.0.3 采用失败封闭合同：SKILL 内联锁块、canon-locks.md 和 validator 快照必须严格一致；缺失工具、text-only、不可锚定首镜、跨场/跨层或 sparse 冲突只能输出 REVIEW_REQUIRED，禁止正式生图。不得修改 su-fenjingskill-zh 主表、Prompt 列、Storyboard 列、Excel 或校验脚本。
---

# Image2 9 宫格黑白分镜提示词技能（融合版）

## 版本

<!-- skill-version: 2.0.3 -->
<!-- fusion-base: 1.4.0 (generation layer) + 1.7.3 (governance layer) -->
<!-- canon-version: 2.0.3 -->

`su-image9` 是独立的 3x3 九宫格黑白分镜提示词入口。不转用 `su-image2-storyboard-grid-zh`，不修改 `su-fenjingskill-zh` 及其主表、Prompt 列、Storyboard 列、Excel、校验脚本。

**2.0.3 稳定原则**：保留 1.4.0 的生成层锁块与 2.0.x 双轨结构，但治理层改为失败封闭。正式发布必须同时具备 `shot_data.json`、canon、validator 和严格一致的三份锁块；任何依赖缺失、合同冲突或事实无法证明时，宁可返回 `REVIEW_REQUIRED` / `CONTRACT_FAIL`，不得错误放行。2.0.3 不承诺自动标注、PDF 或 ZIP。

---

## 设计总纲（冲突时按序优先）

1. **P-IMAGE（最高）**：生成层合同（第一部分 GEN 全部条款）不可被治理层、预算、词表、校验器或任何流程规则削弱、压缩、外置或替换。图像模型只能看到最终文本，最终文本的完整性优先于一切流程正确性。
2. **P-FAIL-CLOSED**：`canon`、validator、`shot_data` 或必要 reference 缺失时，只能生成诊断材料并设置 `release_ready=false`；不得把内联自查当作机器门禁的等价替代。
3. **P-MACHINE**：可量化判定优先下沉 validator；固定文本优先由 validator 编译注入而非模型手抄。但 validator 只能做加法校验（查缺、查漂移、查冲突），不得做减法裁剪（删冗余、砍长度、剔重复）。
4. **P-HUMAN**：权衡和不可逆成本由人工确认；但人工确认不得把结构错误、事实缺失或 2.0.3 明确阻断的合同冲突改成 `release_ready=true`。
5. **P-STATE**：状态迁移以落盘文件为凭证。`panel_plan.json` 必须显式保存 `release_ready` 与 `review_required_reasons`；每条 reason 固定为 `{code, page, message}`，禁止只写不可定位的自由文本。SC 自查只提供诊断证据，不能作为发布凭证。

---

## 一页速查卡（先读这里）

```text
双层架构：
  生成层合同（GEN）＝ 1.4.0 的图像接口，写死在本文档，不可侵犯。
  治理层（GOV）＝ 2.0.3 失败封闭门禁，依赖缺失即阻断发布。

两条通道：
  快速通道：单页 + 无 review 原因 + 无参考图冲突 → 规划 → 机器门禁 → 直接出 prompt，不停。
  完整通道：多页 batch / 存在 warn / 参考图待绑定 → 走 HC-1 确认后继续。

两种校验模式：
  validator 在场 → G0 结构门禁 + G1 事实门禁 + canon 编译 → 生图只用 compiled 文件。
  validator 或 canon 缺失 → SC 诊断模式：可输出内联锁块与自查表，但必须 REVIEW_REQUIRED，禁止生图。

三条铁律：
  ① 最终生图文本出现任何 "@CANON(" 字面量 ＝ 硬性失败，无条件。
  ② PANEL_LAYER 必须是自然语言视觉描述；校验器话术禁止入 prompt。
  ③ 字符预算只有下限（硬块在场性），上限只 warn 永不 fail；冗余强化是特性不是缺陷。

无条件保留的人工规则：
  HC-3 重试耗尽三选一 ｜ REVIEW_REQUIRED 不得因人工确认直接变成发布通过

生图前目检顺序（无论哪种模式都执行）：
  16:9 画布 → 3x3 九格 → 9 格同宽同高 16:9 → 无画内文字 → 石墨铅笔质感
  → 无 CG/电影光/漫画页 → Panel 1 锚定 → 固定物继承 → 车辆坐标 → 轴线 → 可见性
```

---

## 核心边界

- 不修改 `su-fenjingskill-zh`，不回写主表，不改变镜号、场景、原剧本段落、镜头时长、运镜主画面、备注、Prompt 列或 Storyboard 列。
- 默认从 `shot_data.json` 输出完整 prompt 包；只有 `release_ready=true` 且用户明确要求生图时才进入生图链路。
- 原始图：`wide horizontal 16:9 canvas`，`clean 3x3 storyboard grid`，9 个宫格全部为 `horizontal 16:9 storyboard frame`。
- 最终 `Image2 可复制提示词` 使用英文主导；中文分析表只服务于空间、连续性、取舍和自查凭证。
- 生图层永远无字；中文页眉、镜号、`C序号`、三要素标注属于可选外部后处理，不是 2.0.3 正式交付承诺。
- 参考图只继承角色身份轮廓、发型轮廓、服装剪影、道具形状与归属、空间结构、车辆位置、机位关系；不继承照片质感、精修脸、色彩、光效、厚涂、漫画线稿或 AI 渲染风格。
- 如果读取 `su-fenjingskill-zh` 交付物，优先用主表前 6 列、`shot_data.json`、`continuity_logs`、`continuity_updates`、`visible_characters`、`visible_props`；Prompt 列只能作为镜头摘要辅助。

---

# 第一部分：生成层合同（GEN，不可侵犯）

本部分全部条款为最高优先级。治理层、预算规则、词表扫描、人工确认、任何 references 文件都不得覆盖、削弱、压缩或外置本部分内容。

## GEN-1 SYSTEM_STYLE_LAYER 内联权威副本

以下固定风格模块必须**完整**进入每一页最终提示词。canon-locks.md、本文内联副本与 validator 快照必须逐块一致；任一缺失或不一致均不得以另一副本覆盖后放行。

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

- GEN-1a：`SYSTEM_STYLE_LAYER` 必须位于 `PANEL_LAYER` 之前；缺失或后置视为生成层合同违约，停止输出。
- GEN-1b：参考图、场景描述、用户风格词均不得覆盖本层。用户明确要求改变石墨铅笔风格时，视为与技能默认合同冲突，必须先提示冲突并要求确认，不得静默覆盖。

## GEN-2 Strict panel geometry blueprint 内联权威副本

以下几何硬约束句必须完整进入每一页最终提示词，**禁止任何形式的精简、合并或"意思到了"式改写**：

```text
Strict panel geometry blueprint, mandatory before drawing:
Treat the final canvas as a clean wide horizontal 16:9 layout.
Draw exactly nine separate straight rectangular panel frames with visible gutters.
Arrange the 9 panels in a clean 3x3 storyboard grid: three equal columns and three equal rows.
All 9 panels must have the same width, the same height, the same 16:9 aspect ratio, and aligned edges.
Each panel frame must remain a flat horizontal 16:9 rectangle.
Do not let any panel become square, vertical, tall, narrow, compressed, stretched, trapezoid, diagonal, rounded, or irregular.
Keep gutters and margins as empty separating space. If a close-up needs more room, use empty background or negative space inside that panel; never change the panel shape or aspect ratio.
Do not create 3:2, 4:3, A4, square, vertical, mixed-size, manga, comic, collage, or poster layouts.
Do not create a manga page, comic page, dynamic collage, masonry grid, mixed panel sizes, tilted frames, perspective-distorted frames, overlapping panels, or a poster composition.
The content inside a panel may crop or zoom, but the panel frame itself must remain a flat horizontal 16:9 rectangle.
Geometry correctness does not replace the SYSTEM_STYLE_LAYER. The 3x3 grid must remain geometrically strict while all panel contents remain in the same monochrome graphite storyboard production style.
```

## GEN-3 NEGATIVE_CONSTRAINTS 内联权威副本

每一页最终提示词的 `NEGATIVE_CONSTRAINTS` 必须完整包含：

```text
No photorealism, no film still look, no realistic skin texture, no cinematic lighting, no cinematic grading, no HDR lighting, no bloom, no volumetric god rays, no depth-of-field blur, no CGI, no 3D render, no digital painting, no digital illustration look, no rendered concept art, no polished illustration, no watercolor, no oil painting, no painterly shading, no soft airbrush gradients, no anime rendering, no manga page, no comic page layout, no inked comic outlines, no clean manga line art, no dynamic collage, no masonry grid, no poster composition, no color, no pure black fill blocks, no heavy ink fill, no text inside the image, no labels, no subtitles, no arrows, no watermarks, no square panels, no vertical panels, no tall panels, no narrow panels, no mixed-size panels.
```

解释性豁免：`No pure black fill blocks` 不禁止铅笔线、宫格边框和 gutter；`No manga page / comic page layout` 同时是风格禁令和版式禁令；`No anime rendering` 不禁止低细节铅笔分镜脸。

## GEN-4 硬词清单（在场性下限）

每一页最终提示词必须包含以下硬词句（这是字符预算唯一的**硬性下限**定义）：

- `Generate one wide horizontal 16:9 canvas containing a clean 3x3 storyboard grid.`
- `Each of the 9 panels must also be a horizontal 16:9 storyboard frame.`
- `Panel 1 is the master spatial layout anchor for the entire 3x3 grid.`
- `All Panels 2-9 must be derived from the same Panel 1 layout.`
- `Do not redesign the room, exterior location, furniture footprint, terrain, road, doorway, vehicle position, or object positions in later panels.`
- `Do not generate any text, labels, captions, panel numbers, scene headers, shot numbers, subtitles, arrows, or watermarks inside the image.`
- GEN-1 风格块全文、GEN-2 几何蓝图全文、GEN-3 负面约束全文。

## GEN-5 最终提示词 12 层结构

最终 `Image2 可复制提示词` 按以下顺序组织，不得混写成无层级 prompt：

1. `DELIVERABLE`
2. `SYSTEM_STYLE_LAYER`（GEN-1 全文）
3. `SCENE_LAYER`
4. `CAMERA_RULE_LAYER`
5. `CONTINUITY_LAYER`
6. `REFERENCE_USAGE` 或 `TEXT_DERIVED_LAYOUT`
7. `PANEL_1_MASTER_SPATIAL_LAYOUT_ANCHOR`
8. `DOOR_WINDOW_FURNITURE_GEOMETRY_LOCK`
9. `VEHICLE_AND_AXIS_LOCKS`
10. `OBJECT_VISIBILITY_AND_BOUNDARIES`
11. `PANEL_LAYER PANEL-1 to PANEL-9`
12. `NEGATIVE_CONSTRAINTS`（GEN-3 全文）

结构规则：

- `SCENE_LAYER` 负责空间边界、固定几何、门窗家具、道路、车厢等不可漂移锚点，及人物/车辆/道具初始位置与允许位移；不重新定义风格。
- `CAMERA_RULE_LAYER` 负责机位编号、摄影机朝向、对视轴线、反打肩位、车内摄影机占位、`screen left/right` 投影；不重新定义风格，不新增剧情事实。
- `PANEL_LAYER` 不得出现任何新的风格定义（`cinematic lighting`、`anime rendering`、`digital painting`、`photorealistic`、`concept art`、`watercolor`、`oil painting`、`CGI render` 等命中即失败）。
- 如需在 Panel 提醒风格，只允许写 `Panel style inherits SYSTEM_STYLE_LAYER exactly.`，默认不建议每格重复。

## GEN-6 Panel 双轨制（融合核心）

**机器轨（panel_plan.json）**：每格保留短字段结构，仅供规划与事实比对，**永不进入生图文本**：

```text
PANEL-n:
  source_shot:
  shot_data_camera_tag:
  drawn_camera_tag:
  visible_only:
  action_composition:
  floor_axis_delta:
  prop_state:
  distance_stage_lock:
```

**生图轨（PANEL_LAYER）**：每格必须写成**自然语言视觉描述句**，覆盖：主体、动作阶段、景别、观察角度、构图任务、空间继承来源（继承 Panel 1 哪部分）、角色朝向与距离、互动对象、情绪的可见表达方式、道具位置/归属/状态变化、动作结果、信息增量。示例形态（非锁文本）：

```text
PANEL-3: Medium shot from the vehicle rear-left area toward the boy seated at vehicle rear-right; the right rear window beside him shows the same foggy mountain road established in Panel 1; his hands grip the seat edge; camera does not occupy his seat; screen left shows the mother's shoulder in soft foreground.
```

- GEN-6a：生图轨每格必须是完整句子，不得是 `key=value` 电报体。
- GEN-6b：`props=yes/no/true/false/present/absent` 等布尔压缩禁止出现在两条轨中；道具只能写具体物名或 none（机器轨），生图轨用自然语言描述道具在画面中的位置与状态。
- GEN-6c：位移距离锁。相邻来源镜头出现"走上前、靠近、退后、停在两步远、贴近、扑上去、跪到面前"等位移终点时，前序 Panel 必须在 `distance_stage_lock` 和生图轨中明确保持位移前距离、可见空地或空间纵深；后序 Panel 才能画出终点状态。禁止把后序距离终点提前画入前序 Panel。

## GEN-7 校验器话术入 prompt 禁令

以下类型文本**禁止**出现在最终生图文本中：

- `MUST MATCH SHOT_DATA CAMERA TAG`、`SOURCE SHOT:`、字段骨架名。
- `no physical prop; no handheld object; vfx/body-state only if present.` 等面向校验器的元语句（其语义由 DOM-6 在规划层执行）。
- 任何 `@CANON(` 字面量（见 GOV-1，无条件硬性失败）。
- 页眉、镜号、`C序号`、三要素、annotation layer、after generation labels 或任何让模型画字的指令。
- `copy the style of the reference image`、`match the reference style`、"如图所示""严格参考图片"及同义句。

## GEN-8 无字生图与可选后处理分离

- 原始生图保持无字；`no text inside the image` 必须保留在负面约束中。
- 若项目另有已验证的标注工具，可在图外添加中文 `场次/场景｜镜头编号范围` 与 `C序号｜视角｜景别｜运镜`；2.0.3 本身不保证标注脚本存在，也不把标注结果计入 `release_ready`。
- `C序号` 必须使用该 Panel 的真实来源镜号（`panel.shot_nos[0]` / `source_shot`），不得按页内格号重置为 C1-C9。
- `视角｜景别｜运镜` 计划值只从 `shot_data.json` 的 `camera_main_image` 开头方括号读取；不得翻译、猜写、概括或混用中英文。
- 多镜头合并 Panel 默认使用来源范围首镜头三要素；提示词明确指定主镜头时以主镜头为准。
- 后处理前必须逐格核对生成图实际构图与 JSON 三要素、原分镜剧情、Panel 顺序、动作阶段和距离阶段；不符时**不得用假标签迁就错误画面**，该格标记 `构图不符，需重生/人工确认`。
- 标签区位于宫格外部排版层，不得压缩、遮挡、裁切或覆盖任何 16:9 宫格内容；不得对宫格内图像加色、加调色、加锐化、加阴影 UI、加漫画边框。
- 使用外部标注工具时必须优先检测实际 3x3 宫格边框；检测失败只能显式报告，不得静默裁切或错位。
- 2.0.3 不承诺 PDF、ZIP 或其他分发版式；原始无字 16:9 九宫格始终是唯一图像母版。

---

# 第二部分：领域规则层（DOM，内联，不外置）

本部分知识必须留在 SKILL 正文；references 只保存模板与细化合同。必要 reference 缺失时按 P-FAIL-CLOSED 阻断发布。

## DOM-1 Panel 1 主平面锚定

- 每页 `PANEL-1` 必须是该页主空间锚定，不得直接使用特写、极近特写、单人近景、主观局部、中景反应或道具特写。
- `PANEL-1` 必须保留本页来源范围的首个源镜头编号。时间顺序优先于锚点便利；不得为了获得更宽的空间锚定而把后续镜头提前到第一格。
- 来源第一镜不是可直接使用的空间锚定时，不得把近景/特写静默改成宽镜，也不得重排后续镜头。2.0.3 必须设置 `release_ready=false`，在 `review_required_reasons` 写入 `R-FIRST-SHOT-ANCHOR` 并返回 `REVIEW_REQUIRED`。
- 尚未在剧情中出现的人物、道具、车辆、动物或灵异对象不得提前画出；只能锚定其未来出现的空位置。
- 后续近景裁掉家具、地形、门窗或道路时，背景保持简化或来自 Panel 1 局部；不得补画新家具、新门窗、新街道或新房间。
- Panels 2-9 只能从 Panel 1 裁切、推进、反打、俯拍、侧拍或换焦点，不得重新布景。

## DOM-2 锚定判定关键词集（继承 1.7.3 R-ANCHOR-2）

对页首格来源 tag 分词后判定：

- 正集：{master, establishing, wide, full, 全景, 大全景, 大远景}
- 负集：{close, close-up, medium, over-shoulder, OTS, insert, POV, reaction, black, 特写, 近景, 中景, 过肩, 反应, 黑场}
- 仅含正集 → 可直用；含负集、两者皆含或两者皆不含 → `REVIEW_REQUIRED`。不得把关键词不确定、首镜空间不足或 camera tag 冲突降为可豁免 warn。

## DOM-3 固定物与空间锁定

按任务实际场景输出中文表格：`空间概念`、`第1格主平面锚定表`、`门窗家具几何锁定表`、`固定物屏幕投影表`（不可见时写"裁掉/画外"，不能写成新位置）、`前序9格布局继承表`、`对象足迹与朝向表`、`机位编号表`、`摄影机朝向表`、`对象可见性表`、`逐格差异表`、`风格继承检查表`。

- 不适用的表允许一行写"本页不适用"，但 `风格继承检查表`、`逐格差异表`、`九格去重检查表` 不得省略。
- 画外对象不得以阴影、倒影、小黑点或背景轮廓出现。

`风格继承检查表` 表头固定为：

| 页码 | Panel 范围 | SYSTEM_STYLE_LAYER 是否存在 | Panel 是否只写内容 | 是否有冲突风格词 | 处理 |
|---|---|---|---|---|---|

## DOM-4 车辆局部坐标与车内物理规则

只要出现车辆、下车、车内外连续关系、车窗框中框、后排反打、车内外对话或透过车窗看人，即强制生效：

- 默认左舵；来源明确右舵则以来源为准并中英文双明示。
- 必须区分 `vehicle left/right/front/rear` 和 `screen left/right`；禁止把车辆左右直接等同为画面左右。
- 左舵固定推演：驾驶座 = `vehicle front-left`，副驾 = `vehicle front-right`，右后排 = `vehicle rear-right`，副驾下车后人物位于 `vehicle-right exterior side`；此后车内镜头只能透过同侧车窗看到该角色。
- `vehicle rear-right seat is directly adjacent to the vehicle-right rear door/window.`
- 拍摄 `vehicle rear-right` 人物时，摄影机应在 `vehicle rear-left or rear-center-left`，斜拍向右后窗；摄影机不能占掉被拍人物座位。
- 车辆页每个相关 Panel 的生图轨描述必须包含具体坐标句，覆盖：`vehicle-local position`、`camera occupancy`、`view direction`、`visible window/side`、`screen projection`。
- 车外事故、车头、车轮、车窗、车内人物等连续关系必须继承同一辆车和同一事故方向，不得在不同 Panel 重置车辆朝向。
- 来源未明确后排左右座位时，锁定为 `same rear bench, adjacent rear-row positions`，明确摄影机不占用后排人物位置。

必填车辆中文表：`车辆舵向与座位锁定表`、`车辆局部坐标与屏幕投影表`、`车辆座位-车窗邻接表`、`车内摄影机占位表`、`车内外同侧窗口关系表`、`逐Panel车辆坐标表`。

## DOM-5 对视轴线与反打锁定

出现两人对视、对话、正反打、过肩、反应近景、关系近景、旁观层观看事故、角色隔车窗互看时强制生效：

- 输出 `对视轴线与反打锁定表`：谁在轴线 A 端、谁在 B 端、摄影机允许侧、禁止跨越侧。表中**不得只写原则句**，必须至少包含一个具体人物/对象名、一组 A/B 端、一个摄影机侧和一组 `screen left/screen right`。
- 锁定 `screen left/right`；反打只能裁切、换景别或换焦点，不得左右互换。
- 过肩和反打必须指定具体肩位，不得只写"过肩""反打""over the shoulder""reverse angle"。
- 生图轨描述必须包含同侧轴线、具体肩位、`screen left/screen right` 和 `Do not cross the axis or swap screen sides.`

## DOM-6 道具与 VFX 语义卫生（1.7.3 R-PROP 改写为内容指引）

- 雾气、光点、光、能量余波、霜层、灰烬、黑雾核心、雾体、触须、消散粒子属于 VFX/身体状态/环境效果，**在规划层不作为 physical props、不触发道具归属**；在生图轨中作为环境/氛围描述自然写入画面句子。
- 机器轨 `prop_state` 只能写具体物名或 none；生图轨用自然语言写道具在画面中的位置、归属与状态变化。
- 任何压缩需求（预算、篇幅）都不得改变语义：不得删减事实、不得把 VFX 改写成道具、不得把具体道具泛化为布尔值；若不可避免，停下走人工确认。
- 场景、固定物、人物、车辆、道具和 VFX 只能来自 `shot_data` 或已绑定参考资产；禁止写入通用洞穴、岩壁、地裂、雾核、家具、门窗、车辆或“本页无车辆”等无来源默认事实。
- `fixed_objects` 与 `characters` 无论采用字符串数组还是对象数组，都必须先规范化为非空事实项；布尔值、`yes/no`、未知对象类型不得冒充实体。

## DOM-7 九格取舍与去重

- 有主表时按用户指定镜号范围生成，不重新拆主表，不改变镜号含义。
- 禁止为了空间锚定静默重排镜头。页首镜头不适合锚定时按 `R-FIRST-SHOT-ANCHOR` 阻断，不得把 C23/C50/C56 等后段镜头提前为该页 `PANEL-1`。
- 来源节点少于 9 个且必须补格时，2.0.3 不再通过重复末镜或推测动作阶段凑满；设置 `release_ready=false`，写入 `R-SPARSE-UNIQUENESS` 并返回 `REVIEW_REQUIRED`。
- 来源节点多于 9 个：每页最多容纳 9 个源镜头，按同一 `scene_id`、同一现实层和严格源顺序继续分页；任何源镜头都不得因取舍被丢弃。
- 每页输出 `九格去重检查表`：Panel、来源镜头、是否重复、唯一视觉任务、与前后 Panel 的差异。
- 每页输出或落盘 `source_shot_range` 与 `sequence_order_policy`。可发布页的原生 `source_shot` 必须严格递增且完整覆盖来源范围；不得通过重复末镜伪装完整九格。
- 无法在不重复、不新增事实前提下得到 9 个不同画面时，必须重新分页，不得硬凑。
- 分页必须按连续空间、人物关系轴线、车辆内外连续关系和叙事层级切段；可发布页只能包含一个 `scene_id` 和一个现实/叙事层级。
- 正式派生脚本必须执行 `strict_single_scene_single_reality_layer`：每页最多 9 镜，同场同层内顺序分页。回忆、手术现实、黑屏或其他层级镜头可以各自在结构化空间成立时开新页，但不得与其他层级共页。
- 同一页跨 `scene_id` 或跨叙事层级时，即使旧 plan 声明了 bridge，也必须设置 `release_ready=false`，写入 `R-CROSS-SCENE` 或 `R-CROSS-LAYER` 并返回 `REVIEW_REQUIRED`。

---

# 第三部分：输入分流

## 参考图输入（含 R-BIND 矩阵）

输入包含场景参考图、角色图、道具图、俯视图、站位图、机位图、尾帧、上一镜输出图、资产路径或图片附件时执行。

**资产/空间一致性审查**，以下情况输出 `任务失败：参考资产冲突（F-ASSET）` 并停止：图片用途不清或资产编号无法匹配；俯视图与透视图空间冲突；用户文字与参考图在门窗家具、站位、机位、道具归属上冲突；参考图与主表/台账摘要冲突；多图无法判断主次且影响布局/身份/归属。

**内容与风格分离**：

- 可继承：角色身份、服装轮廓、发型轮廓、道具形状、空间结构、门窗家具、车辆位置、机位关系。
- 不可继承：色彩、照片质感、电影光效、CG 渲染、厚涂笔触、漫画线稿、AI 精修质感。
- 风格参考与 GEN-1 冲突且无法剥离时，输出 `任务失败：参考风格冲突（F-ASSET）` 或请求用户确认是否改变技能目标。

**绑定矩阵**：`bound` 全流程可用；`prompt_only` 仅 prompt 交付；`not_bound` 可 raw_generation 但须在规划确认时声明 + 标记 `reference_risk: unbound` + 交付警告；`formal_reference_image` 必须 bound；矩阵外组合 = F-GATE。

参考图必须转写成具体控制信息；只有角色/道具参考而没有空间参考时，不从角色/道具图臆造空间，Panel 1 按文字推演锚定。

## 纯文字输入

只有剧本文字、文字版分镜、Markdown/Excel 表格内容、表格截图转写、局部镜号或镜号范围时执行。

- 不要求用户补参考图；不为画面丰富新增角色、道具、建筑、动作结果或对白。
- 文字中的"电影感、赛博、厚涂、日漫、写实、CG"等词默认只作为剧情氛围理解，不改变 GEN-1；用户明确要求改风格时先确认冲突。
- 出现参考图或资产线索时切换到参考图流程。

---

# 第四部分：治理层（GOV，失败封闭）

## GOV-1 canon 严格编译

- GOV-1a：`SKILL.md` 内联锁块、`references/canon-locks.md` 与 validator 出厂快照是 2.0.3 的三份兼容副本，四块名称、逐块正文和 `canon-version` 必须严格一致。任一副本存在但缺版本、截断、缺块、重复块、未知块或逐块哈希漂移，均为 `CONTRACT_FAIL`。
- GOV-1b：`final_image_prompts.md` 可写白名单 `@CANON(NAME)` 标记，由 validator 展开为 `final_image_prompts.compiled.md`。白名单仅含 `HARD_PHRASES`、`GEOMETRY_BLUEPRINT`、`SYSTEM_STYLE_LAYER`、`NEGATIVE_CONSTRAINTS`。
- GOV-1c（铁律）：**最终可生图文本中出现任何 `@CANON(` 字面量 = 无条件硬性失败**，任何模式下都不得放行。
- GOV-1d：关闭 `canon_autofixed`。validator 只报告差异，不得整块替换、重排、裁剪或静默修复后放行。canon 或 validator 缺失时可输出 SC 诊断材料，但必须 `release_ready=false` 并返回 `REVIEW_REQUIRED`。

## GOV-2 机器门禁与诊断模式

**模式 A：机器门禁（validator 在场）**

从 `shot_data.json` 生成 prompt 包时，优先使用正式派生脚本：

```bash
python skills/su-image9/scripts/derive_su_image9_prompt_package.py \
  --shot-data shot_data.json --out-dir path/to/su-image9_package
```

该脚本必须产出 `分析与锁定.md`、`panel_plan.json`、`page-map.json`、`final_image_prompts.md`、`final_image_prompts.compiled.md`、`validation_report.json`，并严格保持来源镜头顺序。`panel_plan.json` 必须含 `release_ready` 与 `review_required_reasons`。临时派生脚本不得绕过 v2.0.3 的顺序锁、距离阶段锁与场景/层级感知分页。

```bash
python skills/su-image9/scripts/validate_su_image9_prompt.py \
  --mode full|text-only --canon references/canon-locks.md \
  --panel-plan panel_plan.json --final-prompts final_image_prompts.md \
  [--shot-data shot_data.json] --report validation_report.json \
  --out final_image_prompts.compiled.md
```

- G0 结构门禁：三份 canon 严格一致、12 层唯一且按顺序出现、硬词在场、`@CANON` 无泄漏、PAGE 连续唯一、每页 `PANEL-1` 至 `PANEL-9` 恰好一次且按序、未知层/重复层/错序层全部失败。compiler 不得用字典覆盖、固定重排或静默裁剪修正输入。
- G1 事实门禁（full 模式）：逐格比对 shot_data ↔ panel_plan ↔ compiled prompt。所有来源镜头必须完整覆盖且只能有一个原生 Panel；严格比对 `beat_ids`、`covered_fact_ids`、camera tag、可见/画外角色、可见道具、连续性依据、来源顺序、轴线与距离阶段。找不到 PAGE/PANEL ID 必须失败，禁止按数组位置或第一项回退。
- `forbidden_prompt_tokens_extra` 必须扫描全部动态层；布尔值、`yes/no`、错误对象类型不得冒充角色、道具或状态。
- **validator 只做加法校验**：禁止实现任何删冗余、砍长度、剔除重复强化句的逻辑。

**模式 B：SC 诊断（validator 或 canon 缺失）**

在中文分析区输出 `SC 自查表` 作为落盘凭证，逐项打勾并给出证据位置：

| 编号 | 检查项 | 结果 | 证据位置 |
|---|---|---|---|
| SC-01 | GEN-1 风格块全文在场且位于 Panel 前 | | |
| SC-02 | GEN-2 几何蓝图全文在场 | | |
| SC-03 | GEN-3 负面约束全文在场 | | |
| SC-04 | GEN-4 硬词句逐条在场 | | |
| SC-05 | 无 `@CANON(` 字面量泄漏 | | |
| SC-06 | PANEL 层为自然语言、无风格词、无校验器话术 | | |
| SC-07 | Panel 1 原镜头本身可作为主平面锚定；否则已记录 REVIEW_REQUIRED | | |
| SC-08 | 九格无重复视觉任务（去重表已出） | | |
| SC-09 | 关系镜头有具体轴线、肩位、screen left/right | | |
| SC-10 | 车辆页逐 Panel 坐标/座位/窗侧/占位齐全 | | |
| SC-11 | 无画内文字要求、无 C序号/页眉入 prompt | | |
| SC-12 | 参考图只继承内容未继承风格 | | |
| SC-13 | 多页 batch 锁块逐字一致 | | |
| SC-14 | `PANEL-1` 保留本页来源范围首镜号，无锚点重排 | | |
| SC-15 | 相邻位移终点已写 `distance_stage_lock`，前序格未提前画终点 | | |

SC 表只能帮助定位错误。无论自查结果如何，都必须设置 `release_ready=false`、记录 `R-VALIDATOR-MISSING` 或 `R-CANON-MISSING` 并返回 `REVIEW_REQUIRED`；不得生图或声明正式发布通过。

## GOV-3 字符预算（只设下限）

- GOV-3a：**下限 = GEN-4 硬词清单与三个锁块全文在场**。这是唯一硬性预算要求。
- GOV-3b：上限仅提醒：单页编译后全文 >12000 Unicode 码点时 warn 一次，提示检查是否有无信息量的复读；**永不 fail，永不强制删减**。
- GOV-3c：几何句、风格句、轴线句、坐标句的正向重复视为设计特性；删除反注水 fail 机制。
- GOV-3d：任何为压缩而删减事实、改写语义的行为按 DOM-6 停下走人工确认。

## GOV-4 词表（动态层硬禁 + 可选 warn）

- 硬禁（两种模式都执行）：任一动态层出现独立风格定义词（`cinematic lighting`、`anime rendering`、`digital painting`、`photorealistic`、`concept art`、`watercolor`、`oil painting`、`CGI render` 及封闭黑名单扩展 `forbidden_prompt_tokens_extra`，只增不减）→ fail。
- 扫描范围为除四个 canon 锁块外的全部动态层；不得只扫 `CONTINUITY_LAYER` 与 `PANEL_LAYER`。
- 白名单外风格词 warn 转人工：仅 validator 在场时启用；SC 模式下由 SC-06 覆盖。
- **删除对内容字段的通用 T1 扫描**：不得因词表把有用的描述性词汇逼出提示词。

## GOV-5 人工确认点（不得覆盖硬门禁）

**通道判定**：单页 + 机器门禁可用 + 无 review 原因 + 无参考图冲突 + 非生图链路 → 快速通道；否则走完整通道或直接阻断。

- **HC-1 规划确认（条件必选）**：多页 batch、资产绑定风险或可豁免 warn 时触发。提交分页方案、每页 PANEL-1、拆格方案、warn、绑定状态与预计交付物。`review_required_reasons` 非空时只能报告，不能通过 HC-1 放行。
- **HC-2 生图放行（生图链路必选）**：只接受机器门禁报告中 `release_ready=true` 的包；提交校验摘要、全部可豁免 warn、生成模式、绑定依据与 batch 状态。SC 诊断、text-only 或 review 包不得进入 HC-2。
- **HC-3 收敛裁决（重试耗尽触发，无条件保留）**：提交失败清单 + 最后一版原始图 + 已尝试收紧措施。用户三选一：`接受缺陷交付`（页标 `accepted_with_defects`）/ `回退规划`（重走全链）/ `终止`（该页 F-CONVERGE，其余页按 GOV-9 缺页规则继续）。模型不得代答、不得自行第 3 次重试。
- **模糊回复不推进（无条件保留）**：HC 点只认 `确认` / `修改：<意见>` / `终止`。模糊回复（"嗯""行吧""随便"）和授权性回复（"你看着办"）一律不推进，输出"请明确回复：确认 / 修改：<意见> / 终止"。连续 2 次非法回复后可给推荐选项及理由，仍须用户显式 `确认`。
- 提交摘要格式：降级项与 warn 项置顶 ⚠️；无降级无 warn 时摘要 ≤10 行。

## GOV-6 状态机与退出码

```text
模式 A（validator 在场）：
S0 → S1 来源锁定 → S2 规划 → [HC-1 条件触发] → S3 出手写稿
→ [G0+G1+编译] → S4 VALIDATED → [HC-2] → S5 生图（只用 compiled）
→ S6 验收（fail→收紧→重跑 G0+G1 重编译→重生；单页最多 2 次）
→ [HC-3 仅耗尽] → S7 后处理 → S8 交付（manifest）

模式 B（SC 诊断）：
规划 → 草稿提示词 + SC 自查表 → REVIEW_REQUIRED；流程终止，不进入生图、验收或正式交付
```

- 退出码固定：`0=PASS`、`1=REVIEW_REQUIRED`、`2=CONTRACT_FAIL`、`3=TOOL_ERROR`。只有退出码 0 可以对应 `release_ready=true`。
- 不得跳态；模式 A 凭证 = 落盘文件路径 + 关键字段摘录；模式 B 凭证 = 诊断材料且永不等于发布凭证。
- 任何回退须重走后续全部校验，旧凭证作废。
- 仅 prompt 包任务在校验通过交付后结束。

## GOV-7 重试与收敛

- 验收 fail → 收紧提示词 → 重跑当前模式全部校验 → 用新文本重生。跳过重校验 = F-GATE。
- manifest 每页 `attempts[]`：`{attempt_no, prompt_sha256, result, failed_items}`；2.0.3 不允许 `canon_autofixed=true`。
- 单页最多 2 次重生；耗尽触发 HC-3。

## GOV-8 Batch

- 模式 A：`batch_id = "F-" + sha256(shot_data)[:8] + sha256(panel_plan)[:8]`。`text-only` 在 2.0.3 已弃用：兼容入口可输出诊断，但必须 `release_ready=false`、记录 `R-TEXT-ONLY-DEPRECATED` 并返回 `REVIEW_REQUIRED`。模式 B 只用于诊断，不分配可发布 batch。
- 同 batch 各页锁块以**锁文本逐字相等**为一致标准（模式 A 比 sha，模式 B 比对文本）。
- 多页任务所有页必须使用完全相同的 SYSTEM_STYLE_LAYER；场景切换只改 SCENE_LAYER。现实/幻境差异只允许通过构图、对象透明度、空间关系表达，不得改成彩色、CG、电影光、厚涂、漫画或高反差。
- 风格参考图支持时先出 style calibration sheet；不支持时不得逐页改风格块。

## GOV-9 page-map 与可选后处理

- prompt 包和生图链路必须产出 `page-map.json`；9 格页 panels 覆盖 1..9。2.0.3 不承诺 PDF、ZIP 或自动标注交付。
- 正式派生脚本生成的 page-map 必须记录每格真实 `shot_nos`、`label_shot_no`、页面标题、`source_shot_range`、`sparse_page`、`page_split_policy` 和 `split_reason`。
- 若项目另行提供已验证的外部后处理工具，网格几何偏差 > 画幅短边 1.5% 时必须报错，不得目测修正后静默交付。
- 缺页规则：HC-3 后存在 F-CONVERGE 页时，page-map 保留条目并标 `"status": "not_delivered"`；其余页码不得重排；交付说明置顶列出缺页及原因，manifest 记录 `acceptance_status: fail_converge`。

## GOV-10 失败分类

F-PLAN（规划失败）/ F-GATE（合同或门禁失败）/ F-CONVERGE（收敛失败）/ F-ASSET（资产冲突）/ F-ABORT（用户终止）。需要人工或后续版本处理但无结构破坏时使用 `REVIEW_REQUIRED`，并列出稳定原因码。统一格式：

```text
任务失败：su-image9 <类别名称>（<代码>）
- 失败项：
- 违反规则：<GEN-x / DOM-x / GOV-x / SC-xx / IMG-xx>
- 依据：
- 建议下一步：
```

---

# 第五部分：产出物与验收

## 命名规范

- 页 = `PAGE-01`…；格 = `PANEL-1`…`PANEL-9`；禁止 P01 双关。旧包仅由迁移检测器识别并返回重新派生要求，不在原地修改历史文件。

## 正式 Markdown 输出骨架

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
### 对视轴线与反打锁定表
### 车辆锁定表
### 九格去重检查表
### 风格继承检查表
### SC 自查表（模式 B 必出；模式 A 写"由 validator 报告替代"并附报告路径）
### 发布状态（release_ready / review_required_reasons）

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
PANEL_LAYER PANEL-1 to PANEL-9:
NEGATIVE_CONSTRAINTS:
```

无车辆、无对视反打、无参考图的页，对应表可写"本页不适用"，但不得删除 `SYSTEM_STYLE_LAYER`、`风格继承检查表`、`九格去重检查表`、`PANEL_LAYER`、`NEGATIVE_CONSTRAINTS`、`SC 自查表/validator 报告引用`。

## 生图与验收（IMG 目检顺序，两种模式统一执行）

只有 `release_ready=true` 的每段 compiled 提示词才能生成一张独立 3x3 九宫格 PNG；2.0.3 不自动打包 ZIP。

原始图目检顺序固定：

1. IMG-01 整体横版 16:9；不得是 3:2 / 4:3 / 横版 A4
2. IMG-02 3x3 九格；9 格同宽同高；每格 16:9
3. IMG-03 无方格 / 竖窄格 / 混合尺寸 / 倾斜 / 重叠宫格
4. IMG-04 无画内文字、标签、箭头、水印
5. IMG-05 整体为 monochrome graphite storyboard，像 hand-drawn pencil / graphite sketch
6. IMG-06 无数字厚涂、无 CG、无电影光、无漫画页、无日漫渲染、无彩色
7. IMG-07 9 格同一 stroke weight、同一 shading density、同一 mid-gray tonal range
8. IMG-08 Panel 1 为主平面锚定
9. IMG-09 固定物几何继承正确、无重新布景
10. IMG-10 车辆局部坐标、座位-车窗邻接、车内摄影机占位、车内外同侧窗口正确
11. IMG-11 反打轴线未跨越、screen left/right 未互换
12. IMG-12 画外对象未以阴影/倒影/黑点/轮廓出现

任一失败 → 收紧提示词并按 GOV-7 重生；单页最多 2 次，耗尽触发 HC-3。

若另行执行外部标注，其验收要求仍为：原始 16:9 宫格比例与像素内容不变，标签来自 `shot_data.json`，标签区不遮挡、不裁切、不压缩宫格。该可选产物不属于 2.0.3 release gate。

批量验收：多页必须像同一位分镜师同一生产场次画出。

---

# 第六部分：迁移与回归

## 从 1.4.0 迁移

- 生成层零迁移成本：锁块、硬词、领域表全部保留且措辞不变。
- 新增：PAGE/PANEL 命名、panel_plan.json 机器轨、SC 诊断表、条件 HC 点、重试上限与 HC-3。SC 只作诊断，不是发布门禁。

## 从 1.7.x 迁移

- `@CANON` 标记继续可用（validator 在场时）；validator 或 canon 缺失场景只能走 GOV-1d 诊断，不得发布。
- 删除：字符预算 hard fail 区间、反注水 fail、T1 内容扫描、Panel 短字段直充生图文本、"上线准入未齐则规则不生效"条款（由 P-FALLBACK 取代）。
- `final_image_prompts.md` 重跑 validator 获得 compiled 产物；Panel 短字段迁入 panel_plan.json，生图轨按 GEN-6 重写为自然语言。旧迁移脚本只检测 1.6/1.7/2.0.2 包并要求从原始 `shot_data` 重新派生，不再写入或半迁移旧包。
- `forbidden_prompt_tokens` 沿用为 `forbidden_prompt_tokens_extra`（只增不减）。

## 回归标准（最高验收，取代流程指标）

1. **出图对照基线**：固定 3 组代表性剧本（含车辆页、对视反打页、sparse 冲突诊断页），以 1.4.0 提示词产出的图为基线；仅对 `release_ready=true` 的 v2.0.3 包生图，且 IMG-01 至 IMG-12 逐项**不劣于**基线，方可视为合入成功。
2. validator 回归（T 系列）仅作为工具正确性验证，**不得替代出图对照**。
3. 任何后续版本对锁块、硬词、Panel 写法、预算、词表的修改，必须重跑出图对照；治理层新特性若导致任一 IMG 项劣化，特性回退，版本不予发布。
4. canon-locks.md、本文档内联副本与 validator 快照任何一方变更，其余两方必须同步，并升 canon-version；不同步 = F-GATE。

---

## 附：本版本相对两个来源版本的取舍总账

| 机制 | 来源 | 处置 |
|---|---|---|
| SYSTEM_STYLE_LAYER 全文内联 | 1.4.0 | 保留，定为 GEN-1 权威副本 |
| 几何蓝图 12 句 | 1.4.0 | 保留，禁止精简（GEN-2） |
| 负面约束大列表 | 1.4.0 | 保留（GEN-3） |
| 硬词清单 | 1.4.0 | 保留，定义为预算唯一下限（GEN-4） |
| 车辆/轴线/锚定/去重领域规则 | 1.4.0 | 回迁正文（DOM 层） |
| 目检顺序清单 | 1.4.0 | 保留并编号 IMG-01~12 |
| 荣誉制自查 | 1.4.0 | 保留为落盘 SC 诊断表，不具发布效力 |
| canon 编译 autofix | 1.7.x | 删除；三份兼容副本必须严格一致（GOV-1） |
| @CANON 无兜底 | 1.7.x | 缺依赖只允许诊断，不允许发布（GOV-1d） |
| 字符预算硬 fail + 反注水 | 1.7.x | 去除，改为下限硬/上限 warn（GOV-3） |
| Panel 短字段直充 prompt | 1.7.x | 去除，改双轨制（GEN-6） |
| 校验器话术入 prompt | 1.7.x | 去除（GEN-7） |
| T1 内容词扫描 | 1.7.x | 去除，仅留封闭黑名单（GOV-4） |
| "规则未生效"自我作废条款 | 1.7.x | 去除，由 P-FAIL-CLOSED 取代 |
| G1 事实门禁 | 1.7.x | 保留（模式 A） |
| HC-1/2/3 + 模糊不推进 | 1.7.x | 保留，HC-1/2 改条件触发，HC-3 与模糊规则无条件 |
| 锚定判定不确定转 warn | 1.7.x | 收紧为 REVIEW_REQUIRED（DOM-2） |
| R-PROP 语义卫生 | 1.7.x | 保留语义，改写为内容指引（DOM-6） |
| PAGE/PANEL 命名、重试、page-map、缺页、manifest、batch_id、失败分类、速查卡、R-BIND | 1.7.x | 保留 |
