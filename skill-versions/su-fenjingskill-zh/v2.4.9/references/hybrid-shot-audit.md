# 混合拆镜审计规则

<!-- for skill-version: 2.4.9 / rule-revision: 2.4.9-gate-state-contract-2026-07-21 -->

在 Gate A 批准后、导演主表锁定（Gate B 提交）前阅读本文件。它用来保留段落主骨架和镜内推进，同时保证关键信息插镜、反应镜、道具特写和 VFX 锚点不被段落长镜糊掉。Markdown/Excel 主表仍然只导出稳定 7 列；本文件新增的审计字段只进入 `shot_data.json`。

本文件所有规则均指 2.4.9。事实级切点字段的结构定义以 `continuity-shot-data.md` 为唯一出处，本文件只规定审计与拆合判断。项目专有字面词只在显式复制到 `metadata.project_lexicon` 后参与当前数据校验。

## 目录

- [总原则](#总原则)
- [事实级切点审计](#事实级切点审计要点)
- [镜头分类字段](#shot_type)
- [必须审计的节点](#必须审计的节点)
- [长镜支撑](#长镜支撑)
- [节奏参考](#节奏参考)

## 总原则

- 先生成段落主骨架，再执行插镜审计；不得先机械拆成一拍一镜再后处理合并。
- 情绪可以合并，因果不能糊；动作可以合并，关键信息不能糊；对白可以合并，真相落点不能糊。
- `不得机械一 Beat 一镜` 只防止碎切，不允许反向变成多 Beat 压缩。事实 ID 覆盖完整不等于分镜有效覆盖。
- 镜头数量、短镜比例、长镜比例和 cut/min 只作为健康参考，只能 WARN，不能 FAIL。
- 插镜必须来自原文事实、可见道具变化、可听声源、VFX 状态变化或明确情绪反转；不得编造剧情补镜。
- **拆合冲突仲裁**：`must_isolate` 高于普通合并建议，但不能绕过机位几何与表演链规则。若必拆后形成同轴 `same | minor` 相邻镜，必须重设为 `substantial` 等价机位变化；只有明确有意跳切才走 `gate-workflow.md` 的 pending jump-cut 路径。
- 同场相邻镜头**默认禁止纵深推拉方向反转**：推进类运动后不得直接接拉出/拉远类运动，反向组合亦同。它不是 180 度越轴；确有叙事动机时仍使用兼容标注 `[反转动机]` 与机器 token `axis-reversal`，经 Gate B 复核；无标注即 FAIL。

## 事实级切点审计要点

切点字段（`cut_priority`、`cut_reasons`、`cut_category`、`cut_moment_id`、兼容字段 `cut_group`）在 Beat 阶段填写并经 Gate A 冻结。本阶段只做审计与拆合执行，不得回改切点标记；发现标记错误必须申请回流至 Gate A。

- **合并唯一条件**：多个 `must_isolate` 事实同镜合并，必须**同 Beat + 同 `cut_moment_id`**，且镜头备注写 `[不可拆说明]`。
- `cut_category` **仅用于统计与审计**，不作为合并门禁；只因同 category 或同 `cut_group` 不得合并。
- 同一物理瞬间同时发生的多个事实（例如 VFX 撞击与瞳孔变化）应在 Beat 阶段共用同一 `cut_moment_id`；若审计时发现同瞬间事实被拆在不同 moment 导致无法合并，走 Gate A 回流修正，不得在镜头层自行变通。
- `cut_priority=recommended` 与 `insert_priority=recommended` 都只是审计提示，不得把已登记的同一人物动作→反应→台词 `performance_chain` 自动切开。动作链拆分必须走 `chain_breaks` 与 Gate B 精确例外。
- **密度指标**：含 ≥1 个 `must_isolate` 事实的 Beat 计为 must_isolate Beat；单场占比 >50% 触发 WARN。唯一处置路径是 Gate A 人工逐条裁决 `keep` 或降级，**模型不得自行降级**，也不得为规避该 WARN 在审计阶段偷改标记。

默认 `must_isolate` 的通用类型（项目实例词见可选 `project-notes.md`，文件本身不自动生效）：

- 真相首次落地：身份、因果、幕后操控、起源解释第一次让观众获得信息。
- VFX 不可逆变化：状态从一种形态进入另一种形态且不可回退。
- 首次声源或声源转折：首次 VO、首次画外声源、声源方向改变。
- 现实层切换：现实、幻境、记忆、主观视角等层级之间的进入与退出。
- 重大情绪反转：关系或心理的明确转折，不只是表情补充。

## 保留必拆切点检测

以下必拆切点必须保留，并作为 `cut_priority` 与过度压缩校验的来源：

- 发言权转移。
- 问答关系变化。
- 角色明显反应。
- 道具状态变化。
- 攻击/命中/结果。
- 空间方向改变。
- 层级/声音来源变化（现实层词与声音来源词共用一个类别，同一段命中两者也只计一个切点类别）。
- 阵法/VFX 状态变化。

9 秒及以上镜头包含两个及以上必拆切点时，默认 FAIL；切点是否相同**以 `cut_moment_id` 判断**。只有备注明确 `[长镜头]`、`[保留理由]`（12 秒及以上另加 `[不可拆说明]`），且镜内不含多个**不同 `cut_moment_id`** 的 `must_isolate` 切点时才可保留。

## shot_type

每个镜头必须填写 `shot_type`：

| 值 | 定义 |
| --- | --- |
| `master` | 空间建立、首镜站位或场面调度主镜。 |
| `action` | 连续动作链或物理事件推进。 |
| `dialogue` | 主要承载对白与关系变化。 |
| `reaction` | 重大真相、声源或事件后的情绪反应。 |
| `insert` | 道具、手部、伤口、屏幕、空间细节等信息插镜。 |
| `transition` | 场景、现实层、空间方向或时间层级转换。 |
| `vfx_anchor` | VFX 不可逆状态变化或因果落点。 |
| `safety` | 为剪辑、节奏、VFX 或声音预留的后期安全镜。 |

**`transition` 与 `safety` 的事实绑定规则**：

- 两类镜头必须绑定空间、声音或现实层事实（`covered_fact_ids` 非空）；确无事实可绑时**禁止生成**。
- 剪辑确需无事实安全镜时，备注写 `[安全镜]`，按 `gate-workflow.md` 进入 Gate B pending；普通校验和签发仍要求精确人工批准。
- 校验器只对上述精确绑定的镜头豁免"每镜必须覆盖 ≥1 事实"检查；泛化批准或无有效批准记录的 `[安全镜]` 标注视为 FAIL。

## split_reason

每个镜头必须填写非空 `split_reason`，可多选：

- `spatial_anchor`：建立空间、轴线、入口、出口、人物初始站位。
- `performance_continuity`：保持表演连续性、对白完整性或段落情绪推进。
- `new_information`：出现新的可拍信息，观众必须看见或听见。
- `prop_state_change`：道具位置、归属、亮灭、破损、显隐或功能状态改变。
- `new_vfx_state`：VFX 从无到有、从弱到强、颜色/形态/边界发生不可逆变化。
- `new_sound_source`：首次出现 VO、画外声、环境声源、震动或声源方向改变。
- `reality_layer_shift`：现实、幻境、记忆、主观视角等层级切换。
- `causal_reveal`：真相、因果关系、幕后操控或关键身份首次落地。
- `emotional_turn`：人物情绪或关系发生明确反转，不只是表情补充。
- `continuity_migration`：人物、道具、朝向、现实层或空间状态发生连续性迁移。

## insert_priority

每个镜头必须填写 `insert_priority`：

- `none`：段落主镜或连续动作镜，不需要独立插镜。
- `recommended`：建议保留为独立镜或在镜内明确插镜意识，便于剪辑识别。
- `must_have`：真相、VFX、道具状态、现实层或声源因果点必须独立成镜或在镜内被清楚强调。

## 必须审计的节点

以下节点必须逐项确认是否需要独立镜，或在主镜内以明确构图、运动、景别变化形成插镜意识，并用 `shot_type`、`split_reason`、`insert_priority` 标记：

- 道具状态变化：亮起、暗下、断裂、归属变化、位置变化、被看见或被遮挡。
- VFX 不可逆变化：从一种状态进入另一种状态。
- 真相首次出现：因果解释、身份揭示、记忆真相、操控关系第一次让观众获得信息。
- 现实层切换：各层级之间的进入与退出。
- 声源首次出现或转折：首次 VO、画外声方向变化、震动来源。
- 重大情绪反转：关系或心理转折。

**短反应镜检查**：若 `shot_type == "reaction"`、`insert_priority == "none"`、`duration_seconds <= 3`，且与相邻镜头同场、无新的空间/道具/声音/位置/现实层事实，校验器触发 `merge_candidate` WARN（写入 `validation_report`，经 `warn_resolutions` 处置，**不写入备注**）。对白后同人物短表情反应仍按硬规则 FAIL，必须合并进同一镜。

**情绪表演 Gate B 摘要**：审核包由脚本从 emotion facts、`performance_cues`、`environment_cues` 和 `continuity_updates` 自动派生，不要求另写逐镜摘要。它只供人工审核，不创建新字段，也不用情绪密度反向主导拆镜。

## 长镜支撑

`duration_breakdown` 是唯一机器时长事实，备注中的自然语言时长估算可选。`duration_seconds > 10` 的镜头必须填写至少两项 `long_take_support`，且 `long_take.classification` 不得为 `not_applicable`：

- `shot_size_change`
- `character_blocking`
- `foreground_background_change`
- `sound_source_change`
- `vfx_state_change`
- `emotional_turn`
- `spatial_progression`

超过 10 秒的镜头不能只靠一句"氛围延长"成立。

附加门禁：

- 9-11 秒镜头必须在备注写 `[长镜头]` 和 `[保留理由]`。
- 12 秒及以上镜头必须在备注写 `[长镜头]`、`[保留理由]` 和 `[不可拆说明]`。
- `insert`、`reaction`、`vfx_anchor` 超过 5 秒，必须写 `[保留理由]` 且至少两项有效 `long_take_support`。
- `dialogue` 或 `master` 镜承载多个关键切点（不同 `cut_moment_id`），或承载 8 秒以上关键切点，必须重拆。
- 所有触发以上门禁的镜头自动列入 Gate B 审核包的长镜复核清单。

## 节奏参考

以下指标写入 `validation_report.hybrid_audit` 与 `director_integrity_audit.rhythm`，聚合越界永远只允许 WARN，不允许 FAIL；它们不在自动白名单，必须由人工在 `warn_resolutions` 处置。局部结构错误仍按本文件对应条款独立 FAIL：

- 短镜：`duration_seconds <= 3`，全片参考比例 10%-18%。
- 长镜：`duration_seconds >= 6`，全片参考比例 40%-55%。
- `cut/min` 全片参考 10.5-12.5。
- 10 秒以上镜头参考 3-5 个，局部强戏可以超出，需要人工判断。

低 cut/min、低短镜比例提示压缩风险；高 cut/min、高短镜比例提示碎切；长镜比例低于 40% 或高于 55% 均提示节奏偏离。不得为了让参考指标好看而机械增删镜头；任何因指标调整的拆合都必须能解释为画面信息或情绪节奏需要，并记入 `revision_log`。

## 项目层倾向

项目专有字面词已迁入可选 `references/project-notes.md`，位阶低于本文件与 `SKILL.md`。需要启用时，显式复制安全字面词到 `metadata.project_lexicon`；本文件与通用校验规则不得硬编码角色、道具、场景或 VFX 项目词。
