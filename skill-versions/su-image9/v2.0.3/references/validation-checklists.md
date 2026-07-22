# su-image9 Validation Checklists

<!-- ref-version: 2.0.3 -->

## G0 Structure Gate

| # | 检查项 | 级别 |
|---|---|---|
| G0-00 | SKILL 内联锁块、canon 文件、validator 快照的版本、四块名称、逐块正文和哈希严格一致 | fail |
| G0-01 | 12 层各出现一次且按定义顺序排列；重复、错序、未知层或 `REFERENCE_USAGE` / `TEXT_DERIVED_LAYOUT` 非二选一 | fail |
| G0-02 | canon 缺版本、截断、缺块、重复块、未知块或手写锁块漂移；禁止自动替换 | fail |
| G0-03 | compiled 文本无任何 `@CANON(` 字面量泄漏 | fail |
| G0-04 | GEN-4 硬词清单、GEN-1、GEN-2、GEN-3 全文在场 | fail |
| G0-05 | 单页 >12000 Unicode 码点只 warn，不 fail | warn |
| G0-06 | 每页恰有按序且唯一的 `PANEL-1` 至 `PANEL-9` 自然语言视觉描述 | fail |
| G0-07 | `PANEL_LAYER` 禁止字段骨架、校验器话术、key=value 电报体 | fail |
| G0-08 | 除四个 canon 锁块外的全部动态层禁止独立风格定义词 | fail |
| G0-09 | `props=yes/no/true/false/present/absent` 禁止出现在 panel_plan 或生图文本 | fail |
| G0-10 | PAGE/PANEL 命名合规；旧 `P01`/`PANEL_TASKS` 生图结构不允许 | fail |
| G0-11 | Prompt 页与 plan 页数量、页号和顺序完全一致；PAGE 从 01 连续递增且唯一 | fail |
| G0-12 | `forbidden_prompt_tokens_extra` 扫描全部动态层，四个 canon 锁块除外 | fail |
| G0-13 | compiler 不得用覆盖、重排、裁剪或位置回退静默修复输入 | fail |

## G1 Fact Gate

full 模式逐格比对 `shot_data.json`、`panel_plan.json` 和 compiled prompt：

- `source_shot` 必须命中 `shot_data.shots[].shot_no`。
- `shot_data_camera_tag` 必须等于 `camera_main_image` 开头方括号三要素。
- `drawn_camera_tag` 必填。
- `panel_plan.json` 每格必须含 v2.0.3 固定机器轨字段，包括 `distance_stage_lock`；顶层必须含 `release_ready` 与 `review_required_reasons`。
- 所有源镜头必须完整覆盖且只能有一个原生 Panel；找不到 PAGE/PANEL ID 必须失败，禁止按位置或第一项回退。
- 逐格严格比对 `beat_ids`、`covered_fact_ids`、camera tag、可见/画外角色、可见道具、连续性依据、来源顺序、轴线和距离阶段。
- 布尔值、`yes/no` 与未知对象类型不得充当角色、道具或状态。
- 页首锚定判定不确定或首镜为近景/特写等不可直接锚定镜头时返回 `REVIEW_REQUIRED`，不得自动改宽或以人工确认放行。
- `G1-12`：每页 `PANEL-1.source_shot` 必须等于 `source_shot_range` 起点或本页最小源镜号；`source_shot` 顺序必须非递减，非 sparse 页不得重复源镜头。
- `G1-13`：相邻镜头出现靠近、退后、两步远、贴近、扑上去、跪到面前等位移终点时，前序 Panel 必须通过 `distance_stage_lock` 与生图轨明确保持位移前距离。
- `G1-14`：每页必须含 `page_split_policy: strict_single_scene_single_reality_layer`，且只能有一个 `scene_id` 和一个现实/叙事层级；跨场或跨层返回 `REVIEW_REQUIRED`，旧 bridge 声明不得豁免。
- `G1-17`：`release_ready=true` 的 2.0.3 包必须能由正式 deriver 从同一 `shot_data` 重建出完全一致的 `panel_plan.json`；任何页字段、机器字段或事实字段手改均 fail。
- `G1-18`：`release_ready=true` 的 2.0.3 包必须能由正式 deriver 重建出完全一致的动态层和 PANEL 文本；任何手改、普通中英文新增人物/道具或剧情事实均 fail。
- `G1-15`：需要补格的 sparse 页返回 `REVIEW_REQUIRED`；不得重复末镜或推测动作阶段后标记可发布。

## SC Self Check

validator 或 canon 缺失时，中文分析区可输出 `SC 自查表` 作为诊断材料，但必须 `release_ready=false` 并返回 `REVIEW_REQUIRED`。SC 永远不能替代机器门禁或进入生图链路。

退出码固定：`0=PASS`、`1=REVIEW_REQUIRED`、`2=CONTRACT_FAIL`、`3=TOOL_ERROR`。只有退出码 0 可以对应 `release_ready=true`。text-only 兼容入口必须返回 1 并记录 `R-TEXT-ONLY-DEPRECATED`。

## Image Acceptance

原始图按 IMG-01 至 IMG-12 目检：16:9、3x3、九格同宽同高、无画内文字、石墨铅笔质感、无 CG/电影光/漫画页、Panel 1 锚定、Panel 顺序正确、动作阶段正确、距离阶段正确、固定物继承、车辆坐标、反打轴线、画外对象不偷画。

如项目另行使用已验证的外部标注工具，每格 C 号必须来自真实来源镜号；标签区不得覆盖、裁切或压缩宫格。2.0.3 不把自动标注、PDF 或 ZIP 纳入正式交付门禁。
