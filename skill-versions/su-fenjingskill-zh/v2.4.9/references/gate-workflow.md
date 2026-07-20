# Gate 状态机与回流合同

<!-- for skill-version: 2.4.9 / rule-revision: 2.4.9-gate-state-contract-2026-07-21 -->

本文件是 2.4.9 的 Gate schema、批次依赖、逐镜例外、hash、失效传播、Prompt 回流和签发规则的唯一规范源。`SKILL.md` 只负责阶段路由；字段 schema 仍以 `continuity-shot-data.md` 为准。

## 目录

- [Gate 顺序](#1-gate-顺序)
- [审核记录](#2-human_reviews)
- [批次 DAG](#3-批次-dag)
- [Hash 作用域](#4-reviewed_hash-作用域)
- [Gate B 逐镜例外](#5-gate-b-逐镜例外)
- [失效与回流](#6-失效与回流)
- [Prompt 超长](#7-prompt-超长)
- [Gate C 与签发](#8-gate-c-与四文件签发)

## 1. Gate 顺序

非分批任务：

```text
Gate A → Gate B → 派生 Prompt → WARN 处置 → Gate C
```

分批任务：

```text
Gate 0
  → 依赖批次 Gate B
  → 目标批次 Gate A
  → 目标批次 Gate B
  → 全部批次完成
  → 派生 Prompt
  → WARN 处置
  → Gate C
```

任何 Gate 到达时必须停机等待人工裁决；模型不得自行写入 approved。

## 2. human_reviews

每条记录程序性 append-only：

```json
{
  "gate": "GATE_0 | GATE_A | GATE_B | GATE_C",
  "round": 1,
  "status": "approved | rejected",
  "reviewer": "人工标识",
  "notes": "审核意见",
  "reviewed_hash": "64位小写SHA-256",
  "batch_id": "仅分批 Gate A/B 使用",
  "approved_items": []
}
```

- 同一 Gate/批次的 round 从 1 连续增加，只认最新记录。
- 最新 rejected 撤销旧 approved。
- Gate 0/C 不写 `batch_id`；分批 Gate A/B 必须写。
- Gate 0/A/C 的 `approved_items` 必须为空。
- Gate B rejected 的 `approved_items` 必须为空。
- Gate B approved 只能填写审核包中真实存在的精确逐镜 token。

Gate 0/A/C 不另设机器生成的 `review-package` 文件：代理提交当前阶段摘要、冻结范围和 `review-hash` 输出后即停机；人工裁决按上面的 `human_reviews` schema 追加。Gate B 使用正式 `review-package` 命令生成逐镜审核包。任何阶段都不得由代理自行追加 `status: approved`。

## 3. 批次 DAG

`batch_plan.batches[*].depends_on` 是执行顺序的唯一来源；数组位置只用于稳定展示，不代表完成前缀。

- Gate A(B) 要求 Gate 0 有效，且 B 的每个直接依赖批次 Gate B 有效。
- Gate B(B) 要求自身 Gate A 有效，且每个直接依赖批次 Gate B 仍有效。
- 阶段预检读取“目标批次 + 全部传递依赖”，排除所有无关批次。
- 跨批 `direct_handoff` 的来源批次必须位于目标批次的依赖闭包。
- 跨批 `inherits_from` 的父场景批次必须位于目标批次的传递依赖闭包，且父批 Gate B 当前有效；阶段预检保留依赖批已批准镜头，只清空目标批镜头层。
- Gate C 要求所有批次 Gate B 有效。

## 4. reviewed_hash 作用域

- Gate 0：版本、规则修订、标题、脚本锁、项目词表和 batch plan 的 `batch_id`、`scene_ids`、`depends_on`；可选 `expected_shot_count` 不进入 hash。
- Gate A：目标批次台账、Beat、Facts、表演链、Gate-A 约束，以及依赖批次 Gate-B 内容 hash 摘要。
- Gate B：Gate A 范围、目标批次前 6 列和受保护审计字段、Gate-B 约束，以及依赖摘要；不含 Prompt。
- Gate C：最终内容 hash，包含第 7 列和 `warn_resolutions`。

继承实际值的 Gate A 派生槽与 Gate B 冻结时点只以 `continuity-shot-data.md` 的“阶段所有权与字段生命周期”为准；占位符只存在于 hash payload，不写入交付 JSON。

`human_reviews`、`metadata.revision_log`、`validation_report` 不进入内容 hash。迁移数据中的旧版 reference 读取状态、标题摘录和脚本可用性凭证字段仅作为已弃用字段忽略，也不进入 2.4.9 内容 hash。

`directorial_constraints` 只进入实际影响批次：

- `same_shot` / `same_beat` 由 `fact_ids` 所属场景确定；
- `forbid_literal` 由 `scene_ids` / `shot_nos` 确定；
- `direct_handoff` 归属 `to_scene_id` 的目标批次；
- `freeze_gate: GATE_A` 进入 Gate A/B；`freeze_gate: GATE_B` 只进入 Gate B。

## 5. Gate B 逐镜例外

Gate B 审核包允许以下结构正确的候选以 pending WARN 出现：

| 类型 | 必需标记 | token |
| --- | --- | --- |
| 无事实安全镜 | `[安全镜]` | `shot:<n>:safety` |
| 有意跳切 | `[跳切说明]` | `shot:<n>:jump-cut` |
| 有意越轴 | `[越轴说明]` | `shot:<n>:axis-cross` |
| 纵深推拉反转 | `[反转动机]` + 理由 | `shot:<n>:axis-reversal` |
| 表演链拆分 | `[动作链拆分]` + `chain_breaks` | `shot:<n>:performance-chain-break` |
| 原文跨度复用 | `[原文复用]` + `source_reuse` | `shot:<n>:source-reuse` |

pending 不是批准：

- `review-package` 只把标记、结构和边界全部正确的候选降为 WARN。
- 结构错误、标记缺失、镜号或边界不匹配仍然 FAIL。
- 普通 validate、build、Gate C 和 final-signoff 必须命中最新有效 Gate B 的精确 token。
- `[人工批准]` 文字没有审批效力；2.4.9 安全镜在审核前不要求该文字。

## 6. 失效与回流

历史记录不删除；以下变化通过 hash 和审核顺序使下游批准失效：

- Gate 0 新 round：全部 Gate A/B/C 失效。
- 某批 Gate A 新 round：本批 Gate B、所有依赖后代 Gate A/B、Gate C 失效。
- 某批 Gate B 新 round：所有依赖后代 Gate A/B、Gate C 失效。
- 仅 Prompt 或 `warn_resolutions` 改变：Gate C 失效，Gate B 不变。

冻结字段需要修改时，先记录回流原因，再修改并追加目标 Gate 的新 round；不得原地改写历史审核。

## 7. Prompt 超长

Prompt 只在全部所需 Gate B 有效后派生。单镜超过 800 字符是 Gate C 前的人工 WARN：

- 保留：`warn_resolutions` 使用 `resolved_by: human`，`resolution: keep | accepted_without_change`，由 Gate C 绑定最终 Prompt。
- 拆镜：不得批准当前 Gate C；回流所属批次 Gate B，审核修改后的前 6 列，再重新派生 Prompt。
- `resolution: revise` 不能关闭仍存在的超长 WARN。
- `auto_whitelist` 不得处理 Prompt 超长。
- 禁止通过删改或截断原文对白降低长度。

## 8. Gate C 与四文件签发

2.4.9 的校验状态只有 `PASS | WARN | FAIL`：

- `PASS`：无错误且无 WARN。
- `WARN`：无错误，但存在必须处置的风险；仍可进入 Gate C 审核。
- `FAIL`：结构、冻结、内容或四文件一致性错误，禁止签发。

每条 WARN 使用稳定 `warn_id`，处置对象固定为：

```json
{
  "warn_id": "W-十二位小写十六进制",
  "resolution": "keep | revise | accepted_without_change",
  "resolved_by": "human | auto_whitelist",
  "note": "非空处置说明"
}
```

`keep` 表示人工确认风险成立但有意保留当前创作选择；`accepted_without_change` 表示人工确认该诊断不需要改动内容；`revise` 表示仍须修改，不能关闭仍存在的 WARN。`auto_whitelist` 只允许校验器明示的程序性白名单，Prompt 超长与节奏 WARN 必须由 `human` 处置。

未运行或未完成最终严格校验时保持未签发，不生成降级可交付状态。Gate C 审核最终内容 hash、JSON/Markdown/Excel/独立 validation report 四个计划文件名、预签发校验结果及全部 WARN 处置；`reviewed_hash` 绑定最终内容，不声称逐字节哈希四个文件。只有无 FAIL、所有 WARN 已合法关闭、全部所需 Gate B 有效且 Gate C 最新 approved 的 `reviewed_hash` 命中最终内容 hash，才允许执行 `build --final-signoff` 和 `validate --final-signoff`。最终四文件的字节级同源性由这两个命令的原子生成与严格比对负责。

四文件必须来自同一 `shot_data`，在临时文件中全部生成并自检成功后原子替换；任何一步失败均不得部分覆盖正式交付物。
