---
name: su-fenjingskill-zh
description: 剧情片导演分镜系统（人工门禁稳定版）。把完整剧本，或完整锁定剧本中明确指定的分场/剧情段落，转换为稳定 7 列电影分镜表；负责锁源、Beat 与事实、连续性、导演拆镜、动态时长、五字段视频 Prompt、JSON/Markdown/Excel/validation report 四文件交付，并在 Gate 0/A/B/C 设置人工停机。
---

# 剧情片导演分镜系统

<!-- skill-version: 2.4.9 -->

当前版本：2.4.9。
当前规则修订：`2.4.9-gate-state-contract-2026-07-21`。

## 1. 活动包与执行入口

以本 `SKILL.md` 所在目录为唯一技能根目录，从这里解析 `VERSION`、`references/` 和 `scripts/storyboard_delivery.py`。同名全局副本、项目副本、缓存和旧版快照只能只读参考，不能混入当前任务。

任何当前版 CLI 命令开始前，`storyboard_delivery.py` 都会直接检查：

- `VERSION` 必须是 `2.4.9`；
- 本文件、正式 Python 入口和五份必需 reference 的版本、规则修订一致；
- 必需 reference 与正式 Python 入口实际存在。

`references/project-notes.md` 完全可选；缺失不警告。当前版不把运行环境读取声明写进分镜 JSON，也不依赖 Node。`validate_storyboard.js` 仅保留为历史版本兼容包装器，不是 2.4.9 正式入口。

## 2. 输入、边界与不变量

输入必须是完整剧本，或完整已锁定剧本中明确指定的分场/剧情段落。只有梗概、零散台词或未经锁定的扩写稿时停止，不得猜补成正式分镜。

关键不变量：

1. 原文先锁定，后续只做镜头分配；对白、事件因果、人物关系和现实层级不得改写。
2. 主表固定 7 列：`镜号｜场景｜原剧本段落｜镜头时长(秒)｜运镜+主画面描述(含台词)｜备注｜Prompt`。
3. Prompt 固定五字段身份：`时间｜景别｜构图｜运镜手法｜画面内容`，只能在 Gate B 有效批准后确定性派生。
4. Gate 数量固定为 Gate 0/A/B/C。代理不得自动批准、代替用户批准、伪造 hash、校验结果或签发状态。
5. `shot_data.json` 是结构化机器事实源；Markdown 与 Excel 是同一 7 列视图，validation report 是正式校验证据。
6. `camera_geometry`、`performance_cues`、`action_progressions`、`environment_cues`、`performance_chains`、`directorial_constraints` 属于质量守卫。只有相关事实触发时才要求非空；无适用事实时允许显式空数组，不得编造内容填字段。
7. `duration_breakdown` 是时长的唯一机器事实；备注中的自然语言时长说明可写可不写。

## 3. 规则优先级

发生冲突时按以下顺序执行：

1. 用户对当前任务的最新明确指令；
2. 本 `SKILL.md` 的不变量、人工停机和阶段路由；
3. 当前阶段唯一权威 reference；
4. `project-notes.md` 中被人工选中并复制进 `metadata.project_lexicon` 的项目词；
5. 一般电影语言建议。

低位规则不得覆盖高位规则。发现高位冻结内容错误时申请回流，不得在下游静默修补。

## 4. Reference 路由

每份细则只承担一种职责，开始相应阶段前必须完整读取：

| 阶段 | 必读文件 | 唯一职责 |
| --- | --- | --- |
| 锁源、连续性、Beat/事实、JSON | [continuity-shot-data.md](references/continuity-shot-data.md) | schema、source span、状态迁移、继承和字段生命周期 |
| Gate、分批、hash、WARN、回流、签发 | [gate-workflow.md](references/gate-workflow.md) | Gate 记录、`depends_on` DAG、冻结/失效和四文件签发 |
| Gate A 后拆合与时长审计 | [hybrid-shot-audit.md](references/hybrid-shot-audit.md) | `must_isolate`、拆合、长镜和节奏审计 |
| Gate A 后摄影与表演创作 | [camera-language.md](references/camera-language.md) | 首镜、机位、构图、运镜与可拍表演 |
| Gate B 后 Prompt 派生 | [seedance-prompt-rules.md](references/seedance-prompt-rules.md) | 五字段 Prompt |
| 确有项目词表需要时 | [project-notes.md](references/project-notes.md) | 可选项目字面词；不参与通用合同 |

主文件不重复 reference 中的字段枚举、阈值、例外 schema 或命令参数。

## 5. 总状态机

```text
输入与锁源 → 可选 Gate 0 → 事实层 → Gate A
→ 镜头层 → Gate B → Prompt/交付 → Gate C
```

- 长输入需要分批时先提交 Gate 0；单批任务跳过 Gate 0。
- 每个 Gate 都是人工停机点：输出该阶段审核材料后立即停止，等待用户明确批准或驳回；Gate 0/A/C 提交阶段摘要与 `review-hash`，Gate B 使用 `review-package`。
- 只有最新轮次状态、审核 hash、批次和依赖均有效，批准才生效。
- 上游冻结内容一旦改变，下游审核自动失效；必须按 [gate-workflow.md](references/gate-workflow.md) 回流。
- 分批任务以 `depends_on` 为真实执行 DAG，不以列表顺序冒充依赖。
- 用户只批准当前明确 Gate 与轮次；“确认”不自动批准后续 Gate。

## 6. 工作流

### 6.1 锁源与可选 Gate 0

1. 检查输入是否满足完整性边界。
2. 完整读取 [continuity-shot-data.md](references/continuity-shot-data.md) 和 [gate-workflow.md](references/gate-workflow.md)。
3. 建立 `script_lock`、场景 ID 与必要项目词表；逐字锁定对白。
4. 长输入建立 `batch_plan`。`batch_id`、`scene_ids`、`depends_on` 必填；`expected_shot_count` 仅是可选正整数容量提示，不参与 Gate 0 hash、拆镜目标或验收。
5. 提交 Gate 0 阶段摘要、冻结范围与 `review-hash` 后停止。批准后锁定剧本、词表、分批范围与依赖图。

### 6.2 事实层与 Gate A

1. 逐场建立连续性台账、Beat、facts、source span 和必要的继承意图。
2. 确保每一条事实可追溯至锁定原文；对白保持逐字一致。
3. 只生成事实层字段，不提前生成镜头、Prompt 或正式交付物。
4. 提交 Gate A 阶段摘要、冻结范围与 `review-hash` 后停止。批准后冻结该批事实层和 Gate A 约束。

### 6.3 镜头层与 Gate B

1. 确认 Gate A 仍有效；再完整读取 [hybrid-shot-audit.md](references/hybrid-shot-audit.md) 和 [camera-language.md](references/camera-language.md)。
2. 完成前 6 列、时长事实、连续性更新及被事实触发的导演审计结构。
3. 同批继承的实际值在 Gate B 由父场终态派生并冻结；跨批继承只允许来自 `depends_on` 闭包内且 Gate B 有效的父批。
4. Gate B 审核包中的情绪与表演摘要由事实、表演提示、环境提示和连续性更新自动派生，不要求另写一份人工摘要。
5. 合法逐镜例外可作为 pending 进入 Gate B 审核包；普通校验仍要求用户精确批准。
6. 用正式 `review-package` 提交 Gate B 审核包并停止。批准后冻结镜头层、审计字段与前 6 列。

### 6.4 Prompt、校验与 Gate C

1. 确认所有相关 Gate B 仍有效；完整读取 [seedance-prompt-rules.md](references/seedance-prompt-rules.md)。
2. 由已锁定字段确定性派生五字段 Prompt，不得借 Prompt 修改上游内容。
3. 运行正式 Python build 和严格 validate，生成 JSON、Markdown、Excel、validation report 四文件原子包。
4. 所有 WARN 必须按 [gate-workflow.md](references/gate-workflow.md) 写出处置；非程序性白名单 WARN 必须由人工选择 `keep`、`revise` 或 `accepted_without_change`。`revise` 表示问题仍未解决，不能签发。
5. 未完成最终校验时保持未签发。只有真实校验为 PASS，或全部 WARN 已合法处置且无 FAIL，并且 Gate C 最新批准 hash 匹配，才可最终签发。
6. 提交 Gate C 最终内容 hash、四文件名清单、预签发校验结果与 WARN 处置后停止；用户批准后再执行 `--final-signoff`。不得把“文件已生成”描述成“已签发”。

## 7. 冻结与回流

- Gate 0 冻结锁源、项目词和分批 DAG。
- Gate A 冻结事实层、继承意图和 Gate A 导演约束。
- Gate B 冻结前 6 列、镜头审计结构、同批继承派生值与 Gate B 约束。
- Gate C 冻结最终内容 hash 与签发决策；四文件字节级同源性由批准后的原子 build 和严格 validate 签发。

回流原则：

- 锁源、词表或分批 DAG 改动：回 Gate 0；单批锁源改动从 Gate A 重新开始。
- Beat、facts、source span、继承意图或 Gate A 约束改动：回 Gate A。
- 镜号、前 6 列、时长事实、连续性更新或导演审计字段改动：回所属批次 Gate B。
- Prompt 过长若保留，用 Gate C 前 WARN 处置；若拆镜，回所属批次 Gate B。
- Prompt 纯派生错误可重新派生；若根因在冻结字段，按根因回流。
- 四文件或 validation report 不一致：重新 build/validate，再提交 Gate C。

具体 hash 作用域、失效传播和 pending 条件只以 [gate-workflow.md](references/gate-workflow.md) 为准。

## 8. 正式命令

2.4.9 唯一正式入口：

```text
python <skill-root>/scripts/storyboard_delivery.py <command> ...
```

命令名称保持稳定：

- `review-hash`：执行对应阶段前置校验并输出审核 hash；
- `review-package`：生成 Gate B 审核包；
- `build`：派生 Prompt 并原子生成四文件；
- `validate`：严格比对四文件；
- `build --final-signoff` / `validate --final-signoff`：要求 Gate C 有效后签发。

参数以 `python .../storyboard_delivery.py <command> --help` 为准。当前 build/validate 必须显式提供 workspace root、JSON、Markdown、Excel 和 validation report 路径。

## 9. 交付验收

最终签发必须同时满足：

- 7 列主表与五字段 Prompt 合同不变；
- 锁定原文、source span、对白和事实覆盖通过；
- Gate 0/A/B/C 的当前必需审核均有效，且没有自动批准；
- 结构化导演审计、连续性、继承、时长、拆合和 Prompt 校验通过；
- 所有 WARN 已合法处置，状态仅为 PASS 或 WARN，且无 FAIL；
- JSON、Markdown、Excel、validation report 来自同一次原子 build，并通过严格一致性校验；
- validation report 与真实校验结果一致，未伪造 hash 或状态。

历史 `2.4.3–2.4.8` 数据只能按版本 profile 和不可变快照只读验证；不得用旧语义生成 2.4.9 交付，也不得修改历史快照。
