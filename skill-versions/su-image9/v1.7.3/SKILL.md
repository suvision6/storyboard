---
name: su-image9
description: Image2/gpt-image-2 9 宫格 3x3 黑白导演 blocking 草图提示词独立技能。v1.7.3 采用"长分析、短生图、三级门禁、人工确认、canon 编译注入"：锁文本以 @CANON 标记引用，由 validator 编译展开为 final_image_prompts.compiled.md，生图只允许使用编译产物；validator 无条件双模式运行且内置出厂快照守卫 canon；PAGE/PANEL 命名分离；关键状态迁移必须经人工确认（HC-1 规划确认、HC-2 生图放行、HC-3 收敛裁决），模糊或授权性回复不推进。参考图只作为身份轮廓、发型轮廓、服装剪影、道具形状与归属锚点。v1.7.3 同步 references 版本、清除旧 P01/P02-P09 示意和旧锁文本全文示意，不改变 validator/schema 行为。不得修改 su-fenjingskill-zh 主表、Prompt 列、Storyboard 列、Excel 或校验脚本。
---

# Image2 9 宫格导演 blocking 草图提示词

## 版本

<!-- skill-version: 1.7.3 -->

`su-image9` 是独立的 3x3 分镜提示词入口，不转用 `su-image2-storyboard-grid-zh`，不修改 `su-fenjingskill-zh` 及其主表、Prompt 列、Storyboard 列、Excel、校验脚本。

**1.7.3 相对 1.7.2 的文档同步补丁**（对应 v1.8.0 提案 OPT-15，先行发布）：

- references 统一标记为 `ref-version: 1.7.3`，`canon-locks.md` 保持 `canon-version: 1.7.1`（锁文本未变）。
- `spatial-continuity-contract.md` 删除旧 `v1.6.1` 表述，`P01/P01-P09` 全部改为 `PANEL-1/PANEL-1 to PANEL-9`。
- `style-and-negative.md` 与 `asset-reference-contract.md` 不再复制锁文本全文，改为 `@CANON(NAME)` 引用示意，避免与 `canon-locks.md` 漂移。
- 本补丁不启用 1.8.0 的 schema、validator、图像验收、glossary、条带/格级生成等新 contract；这些仍需完整实现和回归后另行升版。

**1.7.1 相对 1.7.0 的修复**（对应复审补丁 P1-P9）：

- P1：canon 块改为 `@CANON(NAME)` 标记引用 + validator 编译注入；手抄全文仍容忍（自动修正并记 `canon_autofixed`）；生图一律使用 `final_image_prompts.compiled.md`。
- P2：注水检测改为"内容字段值重复"判定，字段骨架与 canon 块不计入。
- P3：batch_id 双模式定义（`F-` / `T-` 前缀），text-only 不再无定义。
- P4：新增 R-HC-0b，模糊与授权性回复不得推进状态。
- P5：新增缺页交付规则（HC-3 部分页终止后的 page-map/PDF/ZIP 处置）。
- P6/P7：实体交集分词粒度、锚定判定关键词集写死；判定不确定一律转 warn 交人工。
- P8：validator 内置 canon 出厂快照，canon 变更必须显式带版本升级。
- P9：新增一页速查卡。

## 一页速查卡（先读这里）

```text
状态机：S0→S1来源锁定→S2规划→[HC-1]→S3出prompt→[G0+G1机器门禁+编译]→S4
        →[HC-2放行]→S5生图→S6验收(最多2次重生)→[耗尽则HC-3]→S7后处理→S8交付
仅 prompt 包任务：S4 交付编译产物即结束。

何时查什么：
  写锁文本/查禁词       → canon-locks.md（唯一权威；prompt 里只写 @CANON 标记）
  参考图任务            → asset-reference-contract.md（R-BIND 矩阵）
  空间/轴线/拆格        → spatial-continuity-contract.md
  写四类产出物          → output-templates.md
  自检与门禁条目        → validation-checklists.md
  生图前                → 必跑 validate_su_image9_prompt.py（full 或 text-only）

三个人工确认点：
  HC-1 规划定稿后（降级项必列）｜HC-2 生图前（warn 必列）｜HC-3 重试耗尽时（三选一）
用户回复只认：确认 / 修改：<意见> / 终止。其余（含"你看着办"）一律停住重问。

生图只用 final_image_prompts.compiled.md，绝不用手写原文。
```

## 设计原则（冲突时按序优先）

1. **P-SAFE**：门禁配置不可被校验对象自身定义或削弱。
2. **P-MACHINE**：可量化判定下沉 validator；固定文本由 validator 注入而非模型手抄。
3. **P-HUMAN**：权衡、降级、不可逆成本的决策必须经人工确认；判定不确定时机器转 warn 交人工，不静默二选一。
4. **P-STATE**：状态迁移必须有落盘凭证；无凭证迁移非法。

## 必读 References

- `references/canon-locks.md`：锁文本、T1/T2/T3 词表、占位句表的**唯一权威源**。
- `references/asset-reference-contract.md`：参考图合同 + R-BIND 矩阵。
- `references/spatial-continuity-contract.md`：空间连续性合同。
- `references/output-templates.md`：1.7.3 产出物模板。
- `references/validation-checklists.md`：三级门禁清单。
- `skills/su-image-common/references/page-map-schema.md`：page-map 结构。

## 核心边界

- 默认只输出 prompt 包；用户明确要求生图/批量/ZIP 时才进生图链路。
- 原始图：wide horizontal 16:9 canvas，clean 3x3 grid，9 格均为 horizontal 16:9。
- 生图层永远无字；标注只能由后处理脚本加在图外。
- 参考图只继承轮廓、剪影、道具形状与归属；不继承照片质感、精修脸、色彩、光。

## 命名规范（R-NAME）

- R-NAME-1：页 = `PAGE-01`…；格 = `PANEL-1`…`PANEL-9`。禁止 P01 双关。
- R-NAME-2：全部产出物遵守，validator 对旧命名判 F-GATE。
- R-NAME-3：存量文件先经迁移脚本（文件 F）处理，或在 HC-1 声明沿用并确认（不推荐）。

## 状态机（R-STATE）

```text
S0 INIT → S1 SOURCE_LOCKED（凭证：来源清单+绑定状态）
→ S2 PLANNED（凭证：分析与锁定.md + panel_plan.json）
→ [HC-1] → S3 PROMPTED（凭证：final_image_prompts.md 手写稿）
→ [G0+G1+编译]（凭证：validation_report.json + final_image_prompts.compiled.md）
→ S4 VALIDATED
→ [HC-2] → S5 GENERATING（只用 compiled 文件）
→ S6 ACCEPTANCE（fail→收紧→回 G0+G1 重编译→重生；单页最多 2 次重生）
→ [HC-3 仅耗尽时] → S7 POSTPROCESS（page-map + 标注脚本）
→ S8 DELIVERED（凭证：generation_manifest.json）
```

- R-STATE-1：不得跳态；凭证必须是**落盘文件路径 + 关键字段摘录**，不接受口头声明。
- R-STATE-2：任何回退须重走后续全部门禁，旧凭证作废。
- R-STATE-3：prompt 包任务在 S4 交付 compiled 文件后结束。

## 人工确认点

- **R-HC-0**：每个 HC 按固定格式提交摘要，等待回复；未回复停在原状态。合法回复仅三种：`确认` / `修改：<意见>` / `终止`。
- **R-HC-0b（新）**：非三种合法回复（含"嗯""行吧""随便""你看着办"等模糊或授权性回复）一律**不推进**，输出"请明确回复：确认 / 修改：<意见> / 终止"。授权性回复（"你看着办"）明确判为非法——模型不得代行裁决。连续 2 次非法回复后，模型可给出推荐选项及理由，但仍须用户显式`确认`。
- 提交摘要格式要求：**降级项与 warn 项置顶并以 ⚠️ 标记**；无降级无 warn 时摘要 ≤10 行。

### HC-1 规划确认（必选，S2→S3）
提交六项表：分页方案 / 每页 PANEL-1 处理 / split 拆格 / 降级声明 / 绑定状态与可用模式 / 预计交付物。
- R-HC-1a：降级项（sparse_page、镜头不足策略、not_bound raw_generation、旧命名沿用、**锚定判定不确定项**）未列出并确认，后续使用即 F-GATE。
- R-HC-1b：用户`修改`后必须更新 panel_plan 并重提。

### HC-2 生图放行（生图链路必选，S4→S5）
提交：validator 报告摘要（每页字符数、`canon_autofixed` 页、全部 warn 逐条）/ generation_mode × binding_status 及 R-BIND 依据 / batch_id 与 canon 快照状态。
- R-HC-2a：warn 经确认即放行，记入 manifest.waived_warnings。
- R-HC-2b：T3 白名单外词汇未经放行不得进入生图。

### HC-3 收敛裁决（重试耗尽触发）
提交：失败清单（IMG 编号）+ 最后一版原始图 + 已尝试收紧措施。用户三选一：`接受缺陷交付`（页标 `accepted_with_defects` 入 S7）/ `回退规划`（回 S2 重走全链）/ `终止`（该页 F-CONVERGE，其余页按 R-MAP-4 缺页规则继续）。模型不得代答、不得自行第 3 次重试。

### HC-4 交付确认（可选，默认关闭）
用户任务开始时声明启用；启用后 S7→S8 前提交标注抽检图。

## 三级门禁

### G0 结构门禁（无条件双模式）

```bash
python skills/su-image9/scripts/validate_su_image9_prompt.py \
  --mode full|text-only --canon references/canon-locks.md \
  --panel-plan panel_plan.json --final-prompts final_image_prompts.md \
  [--shot-data shot_data.json] --report validation_report.json \
  --out final_image_prompts.compiled.md
```

- **R-G0-1**：生图前必跑，两模式必居其一；"没有 shot_data"不是免检理由。
- **R-G0-2（canon 编译，取代旧 sha256 零容忍）**：四个锁块推荐写 `@CANON(NAME)` 标记，由 validator 展开为 canon 原文；若手写全文，validator 比对——一致则通过，不一致则**用 canon 原文替换并记 `canon_autofixed=true`（warn 备注，不判 fail）**。编译产物 `final_image_prompts.compiled.md` 是唯一可用于生图的文本。
- **R-G0-3（canon 快照守卫）**：validator 内置 canon 各锁块出厂 sha256 快照。运行时 canon 文件锁文本与快照不符：若 canon-version 头未升级 → 直接 fail（canon 被篡改）；已升级 → 需显式 `--accept-canon-change` 方可继续，并将新旧 hash 写入报告。
- **R-G0-4**：其余检查项（字符预算、注水、T1/T2/T3、占位句、实体交集、命名、字段齐全）以 checklist G0-04 至 G0-13 为准，**全部以编译后文本为计算对象**。

### G1 事实门禁（full 模式）
逐格比对 shot_data ↔ panel_plan ↔ compiled prompt：SOURCE SHOT / camera tag / 每格 DRAWN CAMERA TAG / VISIBLE ONLY / FLOOR AXIS 完整性 / PROP 互斥 / 道具归属 / 锚定触发合规 / 拆格差异 / continuity 已读取。条目见 checklist G1-01 至 G1-13。

### G2 人工门禁
即 HC-1/2/3/(4)。

## 字符预算（R-BUDGET）

- R-BUDGET-1：口径 = **编译后文本**（标记已展开）NFC 归一化 Unicode 码点数，含字段名与换行。
- R-BUDGET-2：`[2500,4500]` pass；`(4500,5000]` warn；`>5000` fail。
- R-BUDGET-3：`<2500` fail；`sparse_page: true` 经 HC-1 确认后下限 1800。
- R-BUDGET-4：禁注水；判定见 checklist G0-05（内容字段值重复，字段骨架与 canon 块不计入）。
- R-BUDGET-5（校准任务，上线前执行一次）：用真实 shot_data 编译 3 页实测基线字符数；若固定块+骨架基线 >2200，将 pass 区间整体上调并升 skill patch 版本。

## 禁令三层（R-TOKEN）

以 canon-locks.md 为唯一词表源。要点：canon 四块 hash 校验、**不参与**词汇扫描；扫描仅作用于 CONTINUITY_LOCK 与 PANEL_TASKS；T1 限内容字段且预剔除 `non-readable`、结构性数字豁免；T2 封闭黑名单 = canon 内置 ∪ `forbidden_prompt_tokens_extra`（只增不减）；T3 白名单外风格词 warn → HC-2。

## 占位句（R-PLACE）

- R-PLACE-1：canon 占位句黑名单命中即 fail。
- R-PLACE-2：CONTINUITY_LOCK 与 FLOOR/AXIS DELTA 必须与 panel_plan 具名实体有交集。分词粒度（写死）：英文实体短语去停用词（冠词、介词及 `specific/named`）后，任一**长度 ≥3 的内容词**词界命中即算；中文实体按整串子串命中。任一页/格零交集 → fail。

## 锚定与拆格（R-ANCHOR / R-SPLIT）

- R-ANCHOR-1：每页 PANEL-1 = 该页主空间锚定。
- R-ANCHOR-2（关键词集判定，取代窄正则）：对页首格来源 tag 分词后判定——
  - 正集：{master, establishing, wide, full, 全景, 大远景}
  - 负集：{close, close-up, medium, over-shoulder, OTS, insert, POV, reaction, black, 特写, 近景, 中景, 过肩, 反应, 黑场}
  - 仅含正集 → 可直用；含负集 → 必须 override；**两者皆含或皆不含 → warn，列入 HC-1 降级声明由人工裁定**，机器不得静默二选一。
- R-ANCHOR-3：override 保留 SOURCE SHOT 与来源 tag，另写 `DRAWN CAMERA TAG: master wide/full spatial anchor`，可见性用 `anchor_visible_allowed`。
- R-ANCHOR-4：**每格**必写 DRAWN CAMERA TAG，G1 逐格比对。
- R-SPLIT-1/2/3：同 1.7.0（差异维度至少一项；白名单拆分；总镜头 <5 时 HC-1 提替代方案，否则 F-PLAN）。

## 参考图绑定（R-BIND）

矩阵同 1.7.0（见 asset-reference-contract.md）：bound 全开；prompt_only 仅 prompt 交付；not_bound 可 raw_generation 但须 HC-1 声明 + `reference_risk: unbound` + 交付警告；`formal_reference_image` 必须 bound；矩阵外 F-GATE。纯文字流程 REFERENCE_LOCK 用 `@CANON(REFERENCE_LOCK_TEXT_ONLY)`。

## Panel 短字段

```text
PANEL-n:
SOURCE SHOT:
MUST MATCH SHOT_DATA CAMERA TAG:
DRAWN CAMERA TAG:
VISIBLE ONLY:
ACTION / COMPOSITION:
FLOOR / AXIS DELTA:
PROP STATE:
```

`CONTENT` 不是合法字段。

## 道具与 VFX 状态（R-PROP）

- R-PROP-1：`VISIBLE ONLY` 的 `props=` 只能写 `none` 或具体物理道具名；禁止 `props=yes/no/true/false/present/absent` 这类布尔压缩。
- R-PROP-2：雾气、光点、光、能量余波、霜层、灰烬、黑雾核心、雾体、触须、消散粒子等属于 VFX / 身体状态 / 环境效果，不得作为 physical props，不得触发道具归属。
- R-PROP-3：无实体道具时 `PROP STATE` 必须写明 `no physical prop; no handheld object; vfx/body-state only if present.`；禁止裸写 `owned`、`ownership unchanged` 或同义归属压缩。
- R-PROP-4：字符预算压缩不得改变语义。若为了预算需要删减事实、把 VFX 改写成道具、或把具体道具泛化为布尔值，必须停在 HC-1/HC-2 重新提交人工确认。

## 重试与收敛（R-RETRY）

- R-RETRY-1：验收 fail → 收紧手写稿 → **重跑 G0+G1 并重编译** → 用新 compiled 文本重生。跳过重校验 = F-GATE。
- R-RETRY-2：manifest 每页 `attempts[]`：`{attempt_no, prompt_sha256(=compiled 页文本), canon_autofixed, result, failed_items}`。
- R-RETRY-3：单页最多 2 次重生；耗尽触发 HC-3。

## Batch（R-BATCH）

- R-BATCH-1：full 模式 `batch_id = "F-" + sha256(shot_data)[:8] + sha256(panel_plan)[:8]`；**text-only 模式 `batch_id = "T-" + sha256(panel_plan)[:16]`**。由 validator 计算并写入报告与 manifest。
- R-BATCH-2：同 batch 各页锁块以**锁文本 sha 相等**为一致标准（canon-version 字符串仅作变更管理，锁文本未变的版本升级不影响已开 batch）。
- R-BATCH-3：风格参考图支持时先出 style calibration sheet；不支持时不得逐页改风格块。

## page-map、缺页与后处理（R-MAP）

- R-MAP-1：生图/标注/PDF/ZIP 交付必产 page-map.json；9 格页 panels 覆盖 1..9。
- R-MAP-2：网格几何偏差 > 画幅短边 1.5% → 脚本报错，显式写 box 后重跑；禁止目测。
- R-MAP-3：后处理固定调用 `annotate_storyboard_pages.py`（参数同 1.7.0）；脚本任何报错 = F-ASSET。
- **R-MAP-4（缺页规则，新）**：HC-3 后存在 F-CONVERGE 页时——page-map 保留该 page 条目并标 `"status": "not_delivered"`；标注脚本与 PDF 跳过该页、**不重排其余页码**；交付说明必须置顶列出缺页清单及原因；manifest 该页 `acceptance_status: fail_converge`。

## 失败分类（R-FAIL）

F-PLAN / F-GATE / F-CONVERGE / F-ASSET / F-ABORT，定义同 1.7.0。统一格式：

```text
任务失败：su-image9 <类别名称>（<代码>）
- 失败项：
- 违反规则：<G0-xx / G1-xx / IMG-xx / R-xxx>
- 依据：
- 建议下一步：
```

## 迁移

- 1.7.2 → 1.7.3：文档同步补丁；更新 references 命名与 canon 引用示意即可，validator/schema/产出物结构不变。
- 1.7.0 → 1.7.1：规则层升级，产出物结构兼容；旧 `final_image_prompts.md` 重跑 validator 即可获得 compiled 产物。
- 1.6.1 → 1.7.1：运行迁移脚本（文件 F）完成命名改写与锁块替换为 @CANON 标记；`forbidden_prompt_tokens` 自动降级为 `forbidden_prompt_tokens_extra`。

## 上线准入（硬标准）

1. 两个脚本按文件 E/F 规格落地；2. 回归 T01-T15 全绿；3. R-BUDGET-5 校准完成。三项未齐前，本规则文本不视为已生效。
