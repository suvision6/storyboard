# su-image9 Validation Checklists

<!-- ref-version: 2.0.2 -->

## G0 Structure Gate

| # | 检查项 | 级别 |
|---|---|---|
| G0-00 | canon 出厂快照校验；锁文本变更未升 `canon-version` 或未显式接受 | fail |
| G0-01 | 12 层齐全且顺序正确；`REFERENCE_USAGE` 与 `TEXT_DERIVED_LAYOUT` 二选一 | fail |
| G0-02 | canon 编译展开；手写锁块不一致时自动替换并记 `canon_autofixed=true` | warn |
| G0-03 | compiled 文本无任何 `@CANON(` 字面量泄漏 | fail |
| G0-04 | GEN-4 硬词清单、GEN-1、GEN-2、GEN-3 全文在场 | fail |
| G0-05 | 单页 >12000 Unicode 码点只 warn，不 fail | warn |
| G0-06 | `PANEL_LAYER` 有 9 个 `PANEL-1` 至 `PANEL-9` 自然语言视觉描述 | fail |
| G0-07 | `PANEL_LAYER` 禁止字段骨架、校验器话术、key=value 电报体 | fail |
| G0-08 | `PANEL_LAYER` 与 `CONTINUITY_LAYER` 禁止独立风格定义词 | fail |
| G0-09 | `props=yes/no/true/false/present/absent` 禁止出现在 panel_plan 或生图文本 | fail |
| G0-10 | PAGE/PANEL 命名合规；旧 `P01`/`PANEL_TASKS` 生图结构不允许 | fail |

## G1 Fact Gate

full 模式逐格比对 `shot_data.json`、`panel_plan.json` 和 compiled prompt：

- `source_shot` 必须命中 `shot_data.shots[].shot_no`。
- `shot_data_camera_tag` 必须等于 `camera_main_image` 开头方括号三要素。
- `drawn_camera_tag` 必填。
- `panel_plan.json` 每格必须含 v2.0.2 固定机器轨字段，包括 `distance_stage_lock`。
- 页首锚定判定不确定时转 warn，并要求 `anchor_decision: human_confirmed` 或正式派生脚本写入的 `deterministic_source_order`。
- `G1-12`：每页 `PANEL-1.source_shot` 必须等于 `source_shot_range` 起点或本页最小源镜号；`source_shot` 顺序必须非递减，非 sparse 页不得重复源镜头。
- `G1-13`：相邻镜头出现靠近、退后、两步远、贴近、扑上去、跪到面前等位移终点时，前序 Panel 必须通过 `distance_stage_lock` 与生图轨明确保持位移前距离。
- `G1-14`：每页必须含 `page_split_policy: scene_layer_aware_strict_source_order`；回忆层、手术现实层、黑屏不得作为页首；跨 `scene_id` 必须声明 `intentional_cross_scene_bridge`，跨叙事层级必须声明 `intentional_layer_bridge`。

## SC Self Check

validator 缺失时，中文分析区必须输出 `SC 自查表`。任一项失败，修正后重查；不得带失败项输出正式提示词。

## Image Acceptance

原始图按 IMG-01 至 IMG-12 目检：16:9、3x3、九格同宽同高、无画内文字、石墨铅笔质感、无 CG/电影光/漫画页、Panel 1 锚定、Panel 顺序正确、动作阶段正确、距离阶段正确、固定物继承、车辆坐标、反打轴线、画外对象不偷画。

标注版检查：每格 C 号来自真实来源镜号而非页内格号；标注脚本优先使用实际宫格检测，fallback 必须写入 manifest warning；标签区不得覆盖、裁切或压缩任何宫格内容。
