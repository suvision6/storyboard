# su-image9 Validation Checklists

<!-- ref-version: 1.7.1 -->

## G0 结构门禁（无条件，两模式）

| # | 检查项 | 级别 |
|---|---|---|
| G0-00 | canon 出厂快照校验：锁文本 sha 与内置快照一致；不一致且 canon-version 未升级 → fail；已升级需 `--accept-canon-change` | fail |
| G0-01 | 6 块齐全且顺序固定 | fail |
| G0-02 | canon 编译：@CANON 标记展开；手写全文比对，不一致自动替换并记 `canon_autofixed=true` | warn 备注 |
| G0-03 | 同 batch 各页编译后锁块 sha 互相一致 | fail |
| G0-04 | 字符预算（**编译后**文本）：[2500,4500] pass；(4500,5000] warn；>5000 fail；<2500 fail（sparse_page 确认后 1800） | 按档 |
| G0-05 | **内容字段值重复检测（1.7.1 重写）**：① 同页任意两格的（ACTION+FLOOR+PROP）三元组归一化后完全相同 → fail（重复格）；② 单字段值内句子重复率 >50% → warn。字段名骨架与 canon 块不计入 | 按档 |
| G0-06 | T1 内容禁令（预剔除 non-readable；结构性数字豁免） | fail |
| G0-07 | T2 封闭黑名单（canon ∪ extra；词界+词形/子串+例外） | fail |
| G0-08 | T3 白名单外风格词 | warn → HC-2 |
| G0-09 | 占位句黑名单 | fail |
| G0-10 | 实体交集（分词粒度按 R-PLACE-2 写死：英文去停用词后 ≥3 字符内容词词界命中；中文整串子串） | fail |
| G0-11 | PAGE/PANEL 命名合规 | fail |
| G0-12 | 每格 7 字段齐全含 DRAWN CAMERA TAG；无 CONTENT | fail |
| G0-13 | 无旧 1.6.0 审查层（九个 LAYER/LOCK 名单同 1.7.0） | fail |
| G0-14 | 物理道具语义守卫：`VISIBLE ONLY` 禁止 `props=yes/no/true/false/present/absent`；VFX/身体状态/环境效果不得写入 physical props；`PROP STATE` 禁止裸 `owned` / `ownership unchanged`，无实体道具必须写 no physical prop / no handheld object | fail |

## G1 事实门禁（full 模式）

G1-01 至 G1-10、G1-12、G1-13 同 1.7.0（SOURCE SHOT / camera tag / 每格 drawn tag / override 可见性 / FLOOR 完整性 / 道具归属互斥 / 拆格差异 / continuity 读取）。

**G1-11（1.7.1 重写）**：页首格锚定判定按关键词集——正集 {master, establishing, wide, full, 全景, 大远景}；负集 {close, close-up, medium, over-shoulder, OTS, insert, POV, reaction, black, 特写, 近景, 中景, 过肩, 反应, 黑场}。仅正 → 可直用；含负 → 必须 override，未 override 判 fail；**皆含或皆不含 → warn，要求该项已出现在 HC-1 降级声明中，否则 fail**。

## G2 人工门禁

- HC-1：六项表齐全，⚠️ 降级项置顶（含锚定不确定项）；合法回复推进，非法回复（含授权性回复）停住重问（R-HC-0b）。
- HC-2：字符数 / canon_autofixed 页 / 全部 warn 逐条 / R-BIND 依据 / batch_id 与快照状态；确认 = warn 放行入 manifest。
- HC-3：失败清单 + 最后原图 + 收紧记录；三选一；模型不得代答。

## 原始图验收（IMG-01 至 IMG-15）

同 1.7.0（16:9 画布 / 3x3 / 九等格 / 无字 / 黑白草图 / 跨页一致 / PANEL-1 主空间 / 继承 / 身份归属 / 不换装 / visible-only / 落脚面 / 轴线 / 拆格可辨 / 道具互斥）。失败流程：收紧 → **重跑 G0+G1 重编译** → 重生 → attempts 记录 → 2 次耗尽 → HC-3。

## manifest 校验

同 1.7.0，另加：`prompt_source` 指向 compiled 文件；每 attempt 记 `canon_autofixed`；`fail_converge` 页有对应 page-map `not_delivered` 条目。

## 标注 / PDF / 缺页校验

- 原始无字图保留；标签仅图外；不遮挡不裁剪。
- 网格偏差 ≤1.5% 短边；超标显式 box 重跑。
- **缺页（R-MAP-4）**：page-map 有 `not_delivered` 条目；标注与 PDF 跳过且不重排页码；交付说明置顶缺页清单。
- PDF 无损/低损嵌入，交付前渲染核对。

## 失败输出格式

同 1.7.0（五类代码 + 规则编号引用）。
