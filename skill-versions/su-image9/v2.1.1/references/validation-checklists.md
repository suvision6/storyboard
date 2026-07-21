# 校验、状态与验收合同

<!-- ref-version: 2.1.1 -->

## 状态

- `0 PASS`：全部合同通过，可设置 `release_ready=true`。
- `1 REVIEW_REQUIRED`：可修复的分页、锚点、资产或授权问题。
- `2 CONTRACT_FAIL`：结构损坏、事实漂移、canon 错误或产物不一致。
- `3 TOOL_ERROR`：运行时、字体、图像解码或写盘故障。

退出码非 0 时必须 `release_ready=false`。

review reason 固定为 `{code, page, message}`。

## 输入门禁

必须检查：

- 上游 Skill 必须为 `su-fenjingskill-zh`；上游 `metadata.version` 与 `metadata.rule_revision` 必须是非空字符串，但不与任何固定版本比较，并必须原样写入 source provenance。
- `script_lock.status=locked`。
- 上游 Gate A、Gate B、Gate C 均已批准，Gate C 为最终签发。
- source hash 与当前文件一致。
- 上游 PASS，或所有 WARN 已按合同处置。
- `script_lock.locked_text_hash` 与 `validation_report.source_json_hash` 必须匹配已实现的上游哈希范围；不能仅凭“64 位字符串”放行。
- shot_no 为唯一、严格递增的正整数。
- 每个 shot 的 scene_id 已登记到 continuity_logs。

## Canon Gate

`canon-locks.md` 是唯一人工源。

必须且只能存在四个唯一块：

- `HARD_PHRASES`
- `GEOMETRY_BLUEPRINT`
- `SYSTEM_STYLE_LAYER`
- `NEGATIVE_CONSTRAINTS`

缺版本、缺块、重复块、未知块、截断或哈希漂移均为 CONTRACT_FAIL。

compiled Prompt 不得残留 `@CANON(`。

## Plan Gate

检查 `panel_plan.json`：

- 顶层、Page 与 Panel 字段完整且类型正确。
- 页面从 PAGE-01 连续递增。
- 每页只有一个 scene_id 和 reality_layer。
- 每个源镜头恰有一个 source Panel。
- `spatial_anchor_panel` 指向本页合法 source Panel。
- source Panel 保留来源 camera tag 和构图。
- derived Panel 紧邻来源、后缀唯一且 `fact_delta=none`。
- Beat、事实、人物、道具和连续性状态与来源完全一致。
- source_shot 顺序非递减。
- 不存在跨场/跨层页面、重复末镜或事实补写。

## 确定性一致性

validator 必须从同一 `shot_data.json` 重建：

- 完整 `panel_plan.json`。
- 完整 `page-map.json`。
- 全部动态 Prompt 层。
- 每格 PANEL 自然语言文本。

归一化后任一差异均为 CONTRACT_FAIL。

`panel_plan.json` 是唯一机器事实源；其他成果不得自行计算不同标签或镜号。

## Prompt Gate

必须检查：

- 十二层各出现一次并严格按顺序。
- PAGE 与 PANEL ID 精确、唯一、连续。
- 每页恰有 PANEL-1 至 PANEL-9。
- PANEL 文本无字段骨架、key=value 或校验器话术。
- 除 canon 块外不得重新定义风格。
- 不得新增普通中英文人物、道具、动作或空间事实。
- 画内禁止文字、字幕、格号、水印和箭头。

## 失败状态

2.1.1 不再使用 bridge 或“首镜改宽后人工放行”语义。场景和现实层变化直接拆页。

以下稳定失败码不得生图：

- `F-PAGE-ANCHOR`：当前页没有合法空间锚点。
- `F-SPARSE-COVERAGE`：无法形成足够的零事实增量派生角度。
- `F-ASSET`：参考资产无法绑定或身份/几何冲突无法裁决。
- `F-LEGACY-REGENERATE`：旧包必须从原始 shot_data 重新生成。

上游 WARN 未完成合同处置时保持 REVIEW_REQUIRED；完成处置后记录为 `WARN_ACCEPTED`。text-only 已从正式接口删除。

## PNG 标注验收

标注器必须：

- 拒绝旧版本、`release_ready=false` 或 source file SHA-256 已失效的 page-map。
- 从 page-map 直接读取 `display_label`。
- 正确保留 `C005-A` 等派生标签。
- 优先检测真实 3x3 边框。
- fallback 时记录 warning。
- 使用经验证支持中文的字体。
- 找不到可靠字体时返回 TOOL_ERROR。
- 将原始九格作为完整像素块一次性粘贴。
- 只在顶部和底部外围扩展画布。
- 不缩放、裁切、覆盖或切割重排原图。
- 缺页引用返回 CONTRACT_FAIL。
- 任一页失败时不保留其他页的半成品 PNG。
- 只产生 PNG 与 `annotation_manifest.json`。

## 图像目检

真实出图按以下项评分：

- 16:9 总画布与严格 3x3 九格。
- 九格同宽同高、边框和 gutter 稳定。
- 黑白石墨铅笔质感一致。
- 无 CG、电影光、漫画页或彩色渲染。
- 源镜顺序、构图和动作阶段正确。
- 空间锚点、轴线、距离和固定物连续。
- 车辆、道具和画外对象没有偷画或漂移。
- 画内无任何可读文字。

单页最多重试两次；耗尽后必须报告失败项，不得自行接受缺陷。
