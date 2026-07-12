---
name: su-fenjingskill-zh
description: 剧情片导演分镜系统（人工门禁稳定版）。将完整剧本，或在完整已锁定剧本中指定的分场/剧情段落，转换为稳定 7 列电影分镜表，独立完成导演拆镜、Beat 与原文事实追踪、连续性台账、动态时长、精简视频 Prompt、shot_data JSON、Markdown、Excel 和完整交付校验；按需在长输入分批及 Beat 锁定、主表锁定、交付签发设置 Gate 0/A/B/C 强制人工审核，审核通过前不得进入下一阶段。
---

# 剧情片导演分镜系统

<!-- skill-version: 2.4.3 -->

当前版本：2.4.3。
当前规则修订：`2.4.3-contract-integrity-p2-2026-07-12`。

---

## 0.0 执行入口自检

执行完整剧本分镜时，必须以本 `SKILL.md` 所在目录作为技能根目录，并从该目录解析 `VERSION`、`references/` 与 `scripts/`。如果存在同名全局技能、其他项目副本或旧版缓存技能，只能作为只读参考，不得作为当前任务规则出处。禁止把用户名、盘符或项目绝对路径写入执行入口。

开始拆镜前必须确认三项：

1. 技能根目录下 `VERSION` 为 `2.4.3`。
2. `SKILL.md` 当前规则修订为 `2.4.3-contract-integrity-p2-2026-07-12`。
3. 实际使用的 `storyboard_delivery.py` 与 `validate_storyboard.js` 均来自该技能根目录的 `scripts/`。

任一项无法确认时，停止生成并说明风险；不得用同名旧版技能继续交付。

---

## 0. 版本与兼容（唯一版本规则出处）

本文件其余部分的所有规则均指 2.4.3 本版规则。`build` 只允许生成 2.4.3 数据；旧版本仅允许 `validate` 只读校验。缺失、未知、未来版本或与版本不匹配的 `rule_revision` 一律 FAIL，不得按最近版本猜测执行。旧数据兼容只按下表处理：

| metadata.version | 处理方式 |
| --- | --- |
| 2.3.2 / 2.3.3 | 只读兼容：不检查审计字段、切点字段、人工门禁。 |
| 2.3.4 / 2.3.5 / 2.3.6 | 只读兼容：按各自 `rule_revision` 校验，不要求 `human_reviews`。 |
| 2.4.0 | 只读兼容：人工门禁稳定版；不强制 `script_lock`。 |
| 2.4.1 | 只读兼容：源文锁定版；强制 `script_lock` 与 `source_span` 回切校验，不强制 `approved_script_path`。 |
| 2.4.2 | 只读兼容：外部源文凭证版；沿用该版本的源文指纹算法，不得用于新建交付。 |
| 2.4.3 | 本版全部规则生效；强制技能相对入口、真实源文文件、规范化全文 hash、内容绑定人工门禁与最终签发。 |

### 受保护审计字段统一清单

Prompt 派生阶段及一切后置阶段禁止修改以下字段：

`metadata.project_lexicon`、`beat_order`、`shot_type`、`split_reason`、`insert_priority`、`long_take_support`、`cut_priority`、`cut_reasons`、`cut_group`、`cut_category`、`cut_moment_id`、`inherits_from`、`inherited_states`、`diverged_states`、`continuity_updates`、`covered_fact_ids`、`beat_ids`、`duration_seconds`、`duration_breakdown`、`long_take`、`script_lock`、`source_span`、`source_spans`。

`human_reviews` 与 `metadata.revision_log` 是程序性只追加日志：工作流禁止修改或删除既有记录，只能追加合法的更高轮次记录。校验器只验证当前 JSON 快照中的结构、顺序、连续 round、最新状态与内容 hash；它不能仅凭同一可编辑文件证明历史记录从未被原地改写，也不认证 `reviewer` 身份。需要不可抵赖性时，必须由版本历史、外部签名或真正只追加存储提供锚点。

---

## 1. 角色与优先级

以剧情片导演、DOP 和分镜师的执行视角工作。默认视觉原则为**克制、精密、信息增量**。

**输出稳定性优先于表达丰富性**：同一剧本重复执行应产出结构一致的结果。判断存疑时选择更保守的方案并提交人工门禁裁决，不得自行发挥。

规则发生张力时按以下顺序仲裁：

0. **诚实优先**：不得伪称已读取文件、已运行脚本或已通过校验。
1. 不遗漏、不改写原文事实和对白。
2. 保持空间、角色、道具、声音和现实层级连续。
3. 按可表演 Beat 合并动作与反应。
4. 按时长公式估算镜头时长。
5. 镜头数量、节奏压缩和 Prompt 表达。
6. **拆合冲突仲裁**：`must_isolate` 拆分要求 **高于** 相邻镜头信息增量合并要求。因必拆产生的低增量相邻镜组，备注写 `[必拆相邻]`，信息增量校验对该镜组豁免，并自动进入 Gate B 人工复核清单。

禁止编造原文没有的情节、角色、道具、空间、情绪转折或过渡镜头。最小合理补足只允许处理空间轴线、朝向、画面左右关系等制作信息，必须在备注写 `[合理补足]`，不得补写剧情事实。

---

## 2. 必读资源与读取凭证

按以下产出阶段读取：

- 拆分 Beat 前：`references/continuity-shot-data.md`
- 主表锁定前：`references/hybrid-shot-audit.md`
- Gate A 批准后：`references/camera-language.md`
- Gate B 批准后：`references/seedance-prompt-rules.md`
- 可选：`references/project-notes.md` 只承载项目层字面词与偏好，位阶低于本文件；需要其词表时复制到 `metadata.project_lexicon`，不得让项目文件改写通用规则。文件缺失不影响通用流程。

**读取凭证**：每个已读文件必须在 `metadata.reference_status` 登记 `loaded | missing`，并在 `metadata.reference_proof` 摘录该文件首个标题行原文作为凭证。缺失文件写 `missing` 并在备注登记 `[reference missing]`，按内置最低规则降级执行；不得伪称已读取。

**2.4.3 源文锁定**：开始拆分 Beat 前，必须先生成顶层 `script_lock`，锁定人类确认后的完整剧本文本。`approved_script_path` 必须是工作区内可读 UTF-8/UTF-8 BOM 普通文件的相对路径；解析后的真实路径不得逃出工作区。读取时仅移除开头 BOM，并将 CRLF/CR 统一为 LF；规范化结果必须与 `locked_text` 全文一致。`locked_text_hash` 对该规范化全文直接计算 SHA-256，不删除其他空白。2.4.1/2.4.2 旧数据仍按其原指纹算法只读校验。

`locked_text` 是唯一可引用源文；如用户批准错字修正，修正后的文本进入 `locked_text`，原始修正意见进入 `script_lock.approved_corrections`。所有 `beats[*].source_text` 与 `shots[*].source_paragraph` 必须通过 `source_span` 或 `source_spans` 指向规范化 `locked_text` 的 0-based Unicode code point 左闭右开区间。`start`/`end` 只能是真正 JSON 整数，不接受布尔值、字符串或小数。两种 span 字段互斥；多 span 必须按 `start` 严格升序、无重叠、无重复，并按顺序用 LF 拼接。任何摘要、改写、删字、换词、换序或未登记来源区间均为 FAIL。

**源文锁定预检**：开始拆分 Beat 前必须保存批准后源文凭证文件，例如 `outputs/YYYY-MM-DD/docs/<片名>.approved_script.txt`，并由校验器实际读取和全文比对；路径字符串本身不构成凭证。Gate A、Gate B 和 Gate C 前均需复核标题、全部场景头、全部人物行和正文行没有从 `locked_text` 中遗漏。若发现 `locked_text` 只包含表格段落、摘要段落或局部正文，立即回到输入检查阶段，不得继续生成。

**对白保真**：同镜 `source_paragraph` 与 `dialogue` facts 构成允许对白集合。`camera_main_image` 与 Prompt 中每段中文或英文引号内对白必须逐字命中该集合；只允许引号样式不同，不得修改引号内字符。仅原文明确标注 VO、画外声或等价信息时，才可作为画外声。

**产出顺序门禁**：镜头、焦段、构图和运镜等摄影术语不得出现在 Gate A 批准前的台账、Beat 或事实中。用于 `space` / `position` anchor fact 的空间轴线、人物朝向和画面左右关系属于连续性制作信息，不属于摄影设计。Gate A 批准后 Beat 层冻结；摄影阶段发现 Beat 问题必须走驳回回流，不得静默回改。

---

## 3. 人工审核门禁总则

四道门禁，逐道**停机等待人工裁决**：

| 门禁 | 时机 | 审核包内容 | 批准后冻结对象 |
| --- | --- | --- | --- |
| **Gate 0**（仅长输入） | 输入检查后 | 分批计划 `batch_plan`：每批场景、预计镜头量、跨批连续性依赖 | 分批边界 |
| **Gate A** | Beat 与事实生成后 | 台账摘要、Beat/事实全表、`must_isolate` 清单、密度 WARN、保真 WARN | 台账、Beat、事实、切点标记 |
| **Gate B** | 导演主表前 6 列完成后 | 6 列主表、审计字段摘要、仲裁清单（`[必拆相邻]` / `[反转动机]` / 长镜复核 / `[安全镜]` 申请）、时长分布 | 前 6 列 + 全部受保护审计字段 |
| **Gate C** | 校验运行后 | 校验报告、WARN 处置表、三文件清单；`NOT_RUN` 时的降级说明 | 交付物整体 |

执行规则：

1. 到达门禁时**必须停止生成**，输出审核包并明确请求裁决；不得代替人工写"通过"。
2. 人工回复批准（如 `GATE_A APPROVED`）后方可继续；驳回时只修改被驳回项，重新提交同一门禁。
3. 每次裁决登记入 `human_reviews`：

```json
{
  "gate": "GATE_0 | GATE_A | GATE_B | GATE_C",
  "round": 1,
  "status": "approved | rejected",
  "reviewer": "人工标识",
  "notes": "审核意见原文摘录",
  "reviewed_hash": "该 Gate 审核范围的 64 位 SHA-256",
  "batch_id": "BT01；单批任务与 Gate 0/C 省略",
  "approved_items": ["shot:12:safety", "shot:13:axis-reversal", "shot:14:required-adjacent"]
}
```

4. `human_reviews` 在工作流中只允许追加；校验器按当前快照检查。同一 Gate/批次的 `round` 必须从 1 开始连续加 1；只认最高轮次，最新 `rejected` 会立即撤销旧 `approved`。各 Gate/批次的最新有效记录必须按 Gate 0 → A → B → C 出现在追加序列中；任一上游 Gate 新增 round 后，旧的下游批准失效，必须追加更高 round 重新批准。分批任务 Gate A/B 必须覆盖每个批次，Gate C 只审核最终合并结果且晚于全部批次最新 Gate B。本检查不提供历史不可篡改证明，可信边界见第 2 节。
5. 每条审核必须绑定脚本确定性计算的 `reviewed_hash`：Gate 0 覆盖版本、标题、`metadata.project_lexicon`、source lock 与 batch plan；Gate A 覆盖 project lexicon、source lock、对应台账、Beat、Facts 与切点；Gate B 再覆盖 project lexicon、最终镜号、前 6 列、连续性更新与受保护审计字段；Gate C 覆盖最终 7 列、WARN 处置与最终内容 hash。`human_reviews`、`revision_log`、`validation_report` 不进入上述内容 hash，避免追加审核记录导致 hash 自毁。
6. 2.4.3 每条审核记录都必须显式写 `approved_items`；只有 Gate B 可写非空数组，Gate 0/A/C 必须写 `[]`。`[安全镜]`、`[反转动机]`、`[必拆相邻]` 例外必须通过该字段精确绑定镜号与类型，token 固定为 `shot:<shot_no>:safety`、`shot:<shot_no>:axis-reversal`、`shot:<shot_no>:required-adjacent`；泛化批准无效。
7. **冻结与回流**：已批准数据冻结。后续阶段发现冻结数据有错，必须声明"申请回流至 Gate X"并说明理由，经人工同意后修改并重新过该门禁；`metadata.revision_log` 追加 `{round, trigger, summary}`。
8. 2.4.3 预签发强制检查 Gate A/B（分批时含 Gate 0）及其审核 hash；最终签发额外要求 Gate C 最新轮次为 `approved` 且 hash 匹配。`NOT_RUN` 交付必须在 Gate C 明确记录 `accepted_without_validation`。

长输入的 `batch_plan` 结构固定为：

```json
{"batches":[{"batch_id":"BT01","scene_ids":["S01","S02"],"expected_shot_count":20,"depends_on":[]}]}
```

`batch_id` 必须唯一；每个场景只属于一个批次；`depends_on` 只能引用既有批次且不得成环。所有 Beat/Shot 必须归属已登记场景与批次。单批任务使用 `null`；空对象或空 `batches` 不是合法长输入计划，也不能触发 Gate 0 豁免。

**修复迭代合法性**：因校验 FAIL 或人工驳回而合并、拆分、重设镜头属于合法修复，须记入 `revision_log`。被禁止的是无审计的自发批量后处理。交付数据不得含 `old_shot_no`、`PASS_INTERNAL`、`运镜修正`、`【镜内变化】` 等过程痕迹；`revision_log` 是唯一合法过程记录。

---

## 4. 工作流

1. **检查输入与环境**：确认剧本正文、场景、角色、空间、关键道具和对白；正文缺失即停止。登记 `reference_status` 与 `script_status`。2.4.3 必须实际读取工作区内 `approved_script_path` 并写入 `script_lock`。可选 `metadata.project_lexicon` 是对象，只允许 `prop_terms | space_terms | vfx_terms | reality_terms | sound_terms`；可省略无词项的 key，每个已出现的值必须是非空数组，词项须非空、无首尾空白、无 Unicode 控制/格式/代理字符且同一 key 内唯一。词项只按普通字面子串匹配；正则元字符允许出现但会被转义，不得用来扩大命中范围。需要项目词时从低位阶 `project-notes.md` 明确复制，禁止通用规则硬编码。
2. **分批（仅长输入）**：输入超过单场或预计单次输出无法完整承载时，先按固定 schema 产出非空 `batch_plan.batches`，过 **Gate 0**。逐批生成分片 `shot_data`，批间连续性依赖显式登记。单次输出必须停在完整场景边界，**禁止输出截断的 JSON**；最后覆盖全部批次并重新进行全局连续性与三文件校验。
3. **建立连续性台账**：每场分配机器键 `scene_id`（S01、S02…），显示名仅用于展示；JSON 内一切场景引用只用 `scene_id`。按场景锁定空间轴线、固定物、角色初始站位、道具状态、声音来源、现实层级，填写 `first_shot_anchor_type`。
   - 跨场继承：显式 `inherits_from` **优先于**默认重置；`inherited_states` / `diverged_states` 新写值必须是 RFC 6901 JSON Pointer（含 `~0` / `~1` 转义）。裸字段与其 `/<字段名>` 形式规范化后不得重复；两类列表之间同一路径及祖先/子路径均冲突。`inherited_states` 的每条路径必须同时存在于父、子场景且值逐项相等；`diverged_states` 的每条路径也必须在父、子场景同时存在。旧顶层裸字段仅作兼容，等价于 `/<字段名>`；不得用点号伪装嵌套路径。
   - `sound_sources` 固定为 `SSxx` 键对象，值含非空 `name`、`visibility`、`position`、`state`；`visibility` 仅 `onscreen | offscreen`。声源首次被听见前也要在当前场景台账登记，可用 `state: "silent"` 或等义初态；出现 `new_sound_source` 时，当前镜头必须覆盖 `sound` fact，并用 `entity_type: "sound_source"`、已登记的 `entity: "SSxx"` 和该 fact 作为证据登记状态变化。
4. **拆分 Beat 与事实**：先生成本场空间锚定事实与站位锚定事实，再按场景目标、动作/台词关系、空间变化、道具变化和现实层级拆分可表演 Beat。`space_anchor_fact` / `blocking_anchor_fact` 是职责名称，不是新增 JSON 字段或 fact type：分别用现有 `type: "space"` / `type: "position"` 表达，并填写既有切点字段。
   - Beat ID 一经创建永久稳定；当前 canonical 格式为 `B001`…`B999`，1000 起写 `B1000`、`B1001`……，禁止 `B000` 和多余前导零。新增 ID 只取尚未使用且大于现有最大数值后缀的编号，不复用空号。叙事顺序只由 `beat_order` 决定：它是 canonical 正十进制字符串，以 `Decimal` 比较；插在首项前取 `first_order / 2`，插在相邻项间取两者中点，追加取末项加 1；`beats` 数组必须按 order 严格递增。
   - `fact.text` 必须使用原文词汇或其直接指称，**禁止写入视觉化翻译**；情绪视觉化只发生在运镜主画面列。保真 WARN 只比对 fact 层，`[合理补足]` 内容不计。
   - 每个事实填写 `cut_priority`（`normal | recommended | must_isolate`）、`cut_category`、`cut_moment_id`。`cut_reasons` 在 `recommended` 与 `must_isolate` 时必须非空，`normal` 时可为空数组。`cut_group` 仅为兼容保留，不参与任何门禁判断。
   - 默认 `must_isolate`：真相首次落地、宿主/替身/惩罚/起源解释、VFX 不可逆变化、首次 VO/画外声源、现实层切换、重大情绪反转。
   - **密度指标**：含 ≥1 个 `must_isolate` 事实的 Beat 计为 must_isolate Beat；单场占比 >50% 触发 WARN，唯一处置路径是 Gate A 人工逐条裁决 `keep` 或降级，**模型不得自行降级**。
5. **【Gate A：Beat 锁定审核】** 提交审核包，停机等待。批准后 Beat 层冻结。
6. **生成段落主骨架**：按可表演段落组织主镜、动作链、对白段和空间推进。不得机械一 Beat 一镜（防碎切），也不得机械多 Beat 压缩（事实覆盖完整不等于分镜有效覆盖）。
7. **执行插镜审计**：按 `hybrid-shot-audit.md` 逐项审计道具状态变化、VFX 不可逆变化、真相首次出现、首次声源、现实层切换和重大情绪反转，填写 `shot_type`、`split_reason`、`insert_priority`、`long_take_support`。
   - **每个镜头必须覆盖至少一个事实 ID**。`transition`、`safety` 镜必须绑定空间/声音/现实层事实；确无事实可绑时禁止生成。剪辑确需无事实安全镜时，只能在 Gate B 由人工批准添加，备注写 `[安全镜][人工批准]`。
   - 多个 `must_isolate` 事实同镜合并的**唯一条件**：同 Beat + 同 `cut_moment_id`，且备注写 `[不可拆说明]`。`cut_category` 仅用于统计审计，不作为合并门禁。
   - 原文现场对白不得改写为画外声；仅原文明确 VO、画外声或等价标注（人物明确不在场且原文写明只闻其声）时可按画外声处理。
8. **锁定导演主表前 6 列并自检**：
   - 每个事实 ID 被至少一个绑定相应 Beat 的镜头覆盖。
   - 连续性逐镜推进：`continuity_update.from` 必须等于上一状态，`to` 才成为下一状态。
   - 相邻镜头信息增量检查；`[必拆相邻]` 镜组豁免（仲裁顺序第 6 条）。
   - 同场相邻**纵深推拉方向反转**默认禁止；确有叙事动机时备注写 `[反转动机]` 加一句话理由，校验降为 WARN 并列入 Gate B 复核。机器 token `axis-reversal` 仅为历史兼容名称，本规则不是 180 度越轴，空间轴线仍按 `spatial_axis` 独立校验。
   - 在 Gate B 前确定从 1 开始连续的最终镜号；Gate B 批准后禁止重排镜号。
9. **【Gate B：主表锁定审核】** 提交含 Gate B 内容 hash 的审核包，停机等待。批准后前 6 列与审计字段冻结。
10. **派生 Prompt**：只派生第 7 列，不得触碰受保护审计字段清单中的任何字段；发现主表问题走回流申请，不得在 Prompt 层静默修表。
11. **预签发构建**：用普通 `build` 从唯一 `shot_data` 派生 Prompt、Markdown、Excel 和报告；四份文件先写同目录临时文件并全部自检成功后再原子替换，任一步失败都不得回写输入 JSON 或覆盖既有正式文件。`<片名>` 仅允许中英文、数字、下划线、连字符，其余字符替换为下划线。
12. **运行预签发校验**：脚本重新计算结构、Gate/WARN 审计和内容 hash，不信任数据内已有 PASS。严格校验要求 `source_json_hash` 是脚本生成的 64 位小写十六进制 SHA-256，并与当前内容一致。
13. **【Gate C：交付签发审核】** 提交校验报告、WARN 处置表、最终三文件清单与 Gate C 内容 hash，停机等待签发。
    - 每条 WARN 必须在 `warn_resolutions` 有条目 `{warn_id, resolution, resolved_by, note}`。
    - 仅白名单 WARN（reference missing、`[合理补足]`、节奏健康参考）允许 `resolved_by: "auto_whitelist"`；其余一律 `resolved_by: "human"`。
    - `resolution: "revise"` 只记录历史修订；若当前 WARN 仍存在则未解决。仍存在的 WARN 只能由合法的 `keep` 或 `accepted_without_change` 关闭。
14. **最终签发构建与只读复核**：追加 hash 匹配的 Gate C `approved` 后执行 `build --final-signoff`，再执行 `validate --final-signoff`。两步均不得重排镜号或改变已审核内容。

仅当三份正式产物已由合法 builder 生成、但最终校验环境暂不可用时，才允许 `NOT_RUN`：`source_json_hash` 必须为空，Gate C 必须明确接受 `accepted_without_validation`，且任何摘要不得把它称为 PASS。builder 缺失时不得生成或声称完成新交付。

---

## 5. 7 列合同

固定列顺序：

| 镜号 | 场景 | 原剧本段落 | 镜头时长(秒) | 运镜+主画面描述(含台词) | 备注 | Prompt |
| --- | --- | --- | --- | --- | --- | --- |

- 镜号：从 1 开始连续纯数字；必须在 Gate B 前确定，Gate B 批准后不得重排。
- 场景列写显示名（`场景编号 场景名`）；`scene_id` 只存在于 JSON。每个新场景首镜必须在运镜列写 `【场景首镜站位】`。
- 场景首镜必须服从 `first_shot_anchor_type`：`space` / `multi_character` / `both` 的首镜必须使用全景类景别；`multi_character` / `both` 还必须让 `visible_characters` 至少包含 2 个不同角色、覆盖当前镜头的 `position` fact，并在 `【场景首镜站位】` 中完成所有可见互动角色的基础站位、朝向、距离与主要视线关系。第二镜只能补充细节，不得补交基础站位。
- 原剧本段落以 Beat ID 开头，`shots[*].beat_ids` 必须按 `beat_order` 严格递增。单 Beat 写 `B001～原文`；仅当所选 Beat 的 order 数组位置连续且 ID 数值也逐一加 1 时可缩写 `B001-B003`，其他多 Beat 一律用 `+` 显式列举。`+` 本身不表示非连续；只有所选 Beat 在 order 数组中存在位置缺口时，才必须写 `[非连续Beat]` 加原因。原文只由 `source_span(s)` 回切，不得摘要或删改。
- 不得使用"承上镜动作""补充镜头""新增过渡"等占位文字替代原文。
- 主表不含关键帧列；`shot_data.shots[*].keyframe` 字段不得出现。
- 全部审计字段只存在于 JSON，不进入 Markdown/Excel 7 列。
- 不得机械一 Beat 一镜；同样不得机械多 Beat 一镜：一个镜头覆盖 3 个及以上 Beat 且包含关键切点时视为过度压缩，必须重拆。

---

## 6. 镜头时长

```text
镜头时长 = max(同步动作, 同步台词) + 非同步动作 + 情绪留白
```

- **唯一公式**：同步动作与同步对白并行发生，先取两者较大值，再加非同步动作与情绪留白；不得把四项直接相加。估算阶段如产生小数，必须在写入 JSON 前向上取整；JSON 与 validator 只接受非负整数，不接收小数后代为取整。`duration_seconds` 必须精确等于 `max(sync_action_seconds, sync_dialogue_seconds) + non_sync_action_seconds + emotional_pause_seconds`。
- 正常中文对白约 3-4 字/秒；迟疑、悲伤或压低声音约 2 字/秒。估算存疑时取较长值，并在 Gate B 审核包中说明。
- 超过 6 秒：备注可列 `[时长估算] 同步动作X秒；同步台词X秒；非同步动作X秒；情绪留白X秒`，并明确“前两项取 max 后再加后两项”的结果。
- 9-11 秒：备注写 `[长镜头]` 和 `[保留理由]`。
- 超过 10 秒：**一律**填至少两项 `long_take_support`，并填 `long_take.classification`，枚举：`not_applicable | dialogue_long | action_long | spatial_long | emotional_long`。
- 12 秒及以上：另加 `[不可拆说明]`。
- `insert`、`reaction`、`vfx_anchor` 超过 5 秒：必须写 `[保留理由]` 且至少两项有效 `long_take_support`。
- 不得为了统计好看强行压缩长对白或连续动作。

---

## 7. 运镜与主画面

### 7.1 场景首镜锚定

`first_shot_anchor_type` 取值：`space | multi_character | both | single_continuation | subjective`（定义见 `continuity-shot-data.md`）。

- `space` / `multi_character` / `both` 首镜必须是全景类景别；室外大场景优先 `微俯视大全景` 或 `平视大全景`；室内多人对话优先 `平视全景` 或 `微俯视全景`。
- 多人场景首镜必须完整交代所有可见互动角色的基础站位、朝向、距离和主要对视轴线；`multi_character` / `both` 的 `visible_characters` 至少 2 人，且首镜必须覆盖 `position` fact。第二镜只能补充遮挡、前后景或细微关系，不得把基础站位拆到第二镜。
- `single_continuation` / `subjective` 可不用全景类首镜，但仍必须保留 `【场景首镜站位】` 标签；标签内容可写人物位置、空间边界、固定物方向或主观视觉锚点。
- 全景必须承载空间、人物或行动信息；不得为满足规则添加无剧情事实的空镜。

### 7.2 每格固定结构

```text
[视角/高度, 景别/特殊视角, 摄影机运动方式]
【机位逻辑】摄影机的空间位置、朝向和画面控制意图。
【场景首镜站位】仅场景首镜出现：所有可见互动角色的位置、朝向、距离和主要视线关系；无可见互动角色时写空间或主观视觉锚点。
【站位位移】仅人物位置或朝向变化时出现。
可见动作、表情、道具互动和原样对白。
```

- 第一行只能是完整三元组，第二行必须以 `【机位逻辑】` 开头。
- 只写摄影机可拍到的事实；情绪必须翻译为眼神、嘴唇、手指、呼吸、姿态和停顿。
- 台词原样嵌入动作尾端，明确说话者和对象。
- `斯坦尼康` 只用于地面人物持续位移，不得用于 `大远景`、`大全景`、超大户外空间、建筑或地貌建立。`航拍` 用于超大范围空间关系，搭配大远景/大全景/全景及俯拍类视角。
- 三元组不得混写远景类和近景/特写类；需要景别跨度时必须使用 `光学变焦`、`急推`、`急拉`、`推轨推进/拉出`、`伸缩摇臂` 等可完成跨度的运镜，并在备注写 `[景别跨度]` 理由。

### 7.3 连续性迁移触发表

| 变化类型 | continuity_update | 【站位位移】 |
| --- | --- | --- |
| 人物主动移动到新位置 | 是 | 是 |
| 人物被动位移（被拖走、击飞、摔倒等） | 是 | 是 |
| 人物朝向变化（位置不变） | 是 | 是 |
| 摄影机切换主体/景别，人物未动 | 否 | 否 |
| 新人物入场 / 人物退场 | 是 | 是 |
| 道具状态变化 | 是 | 否 |

- 出现 `【站位位移】` 但无对应 `continuity_updates` 是失败项；有位置/朝向迁移但画面没写 `【站位位移】` 也是失败项。

### 7.4 相邻镜头规则

- 同场相邻镜头必须有明确画面信息增量；无站位/朝向迁移、同一可见主体、视角族相同、景别相近且运镜只是固定或轻微运动时，必须合并或重设镜头。
- **豁免**：因 `must_isolate` 必拆产生的低增量相邻镜组，备注写 `[必拆相邻]`，豁免合并要求并进入 Gate B 复核清单。
- 同场相邻镜头**默认禁止纵深推拉方向反转**：推进后不得直接接拉出/拉远，反向组合亦同。确有叙事动机时备注写 `[反转动机]` 并进入 Gate B 复核。历史机器 token 保留 `axis-reversal`；本规则不等于 180 度越轴。

---

## 8. 备注标注封闭清单

备注记录情绪阶段、道具状态、声音来源、特效、节奏点、合理补足、时长拆算和连续性结论。允许的标注**仅限**：

`[合理补足]`、`[时长估算]`、`[长镜头]`、`[保留理由]`、`[不可拆说明]`、`[景别跨度]`、`[非连续Beat]`、`[必拆相邻]`、`[反转动机]`、`[安全镜]`、`[人工批准]`、`[声音]`、`[reference missing]`

清单外的标注视为过程痕迹，FAIL。

- 声源可见写 `[声音]：画内声...`；声源不可见写 `[声音]：画外声...`，不得描写画外人物的动作、表情或站位。

---

## 9. Prompt

Prompt 是后置派生列，每镜只能使用五字段：

```text
时间：0秒-X秒
景别：基础景别或特殊视角
构图：可见主体、同框角色和道具的位置关系
运镜手法：真实摄影运动
画面内容：可见动作、表情、道具互动、画内/画外声和原样对白
```

- 跨景别镜头的 `景别` 字段写 `起始景别→结束景别`。
- `构图` 只写主体、位置和道具关系；对白、声音、动作链、情绪反应只进 `画面内容`。引号不闭合或字段串位视为 FAIL。
- **对白保真校验只比对引号内内容**；嵌入句式与引号标点不计入"改字"。
- 单镜 Prompt 总长超过 800 字符触发 WARN，进 Gate B 决定是否拆镜；**禁止以截断台词方式规避**。
- Prompt 不得包含内部标签（`【机位逻辑】`、`【站位位移】`、`【场景首镜站位】` 等）、关键帧内容、生图风格词、审稿意见。
- Prompt 只能忠实派生自已锁定主表、`visible_characters`、`visible_props` 和已登记画外声；发现主表问题必须走回流申请。

---

## 10. shot_data 结构（本版新增/变更字段）

顶层结构在 `continuity-shot-data.md` 基础上新增。下列 JSON 只展示字段位置和候选值，不是可直接通过校验的完整样例；`|` 分隔内容表示任选其一，必需数组不得按示意留空：

```json
{
  "metadata": {
    "version": "2.4.3",
    "rule_revision": "2.4.3-contract-integrity-p2-2026-07-12",
    "project_lexicon": {"prop_terms": ["项目道具词"], "space_terms": ["项目场景词"], "vfx_terms": ["项目特效词"], "reality_terms": ["项目层级词"], "sound_terms": ["项目声源词"]},
    "reference_status": {},
    "reference_proof": {},
    "script_status": {
      "storyboard_delivery.py": "available | missing",
      "validate_storyboard.js": "available | missing"
    },
    "revision_log": []
  },
  "script_lock": {
    "status": "locked",
    "approved_script_path": "工作区内相对路径",
    "locked_text": "人类确认后的完整剧本文本",
    "locked_text_hash": "sha256",
    "approved_corrections": []
  },
  "batch_plan": null,
  "human_reviews": [],
  "warn_resolutions": [],
  "continuity_logs": [],
  "beats": [],
  "shots": [],
  "validation_report": {
    "status": "PASS | WARN | FAIL | NOT_RUN",
    "warnings": [],
    "errors": [],
    "source_json_hash": "由脚本计算；NOT_RUN 时为空字符串"
  }
}
```

关键约束：

- `continuity_logs`、`beats`、`shots` 必须是非空数组。Scene 为 `S[0-9]{2,}`，Batch 为 `BT[0-9]{2,}`，Sound Source 为 `SS[0-9]{2,}`，Fact 为 `<Beat ID>-F[0-9]{2}`；编号数位只用 ASCII `0-9`，因此既不额外禁止 `00`，也不额外禁止超过两位。Scene、Beat、Fact、Batch ID 在各自合同范围内唯一；Sound Source ID 在单场 `sound_sources` 内唯一，继承场景用同键对应同一声源。`fact.text` 必须非空。Beat ID 永久稳定，`beats` 按 canonical `beat_order` 的 Decimal 值严格递增。
- `shots[*]` 引用的 Scene、Beat、Fact 必须存在、归属一致且与当前场景匹配；`continuity_updates[*].evidence_fact_ids` 必须由当前镜头覆盖。
- 每个镜头 `covered_fact_ids` 非空；无事实安全镜只能由 Gate B `approved_items` 精确批准。
- `duration_breakdown` 各分项为非负整数，并按第 6 节公式得到 `duration_seconds`。
- `visible_characters` 与 `offscreen_characters` 必须是无重复、无首尾空白的非空字符串项数组，且不得重叠；`multi_character` / `both` 首镜还要与台账角色及 `【场景首镜站位】` 逐一对应。
- `inherited_states` / `diverged_states` 使用 RFC 6901 pointer；`sound_sources` 使用 `SSxx` 键对象。每条声源迁移都使用 `entity_type: "sound_source"`，`from` / `to` 是无首尾空白的非空字符串，且证据必须命中当前镜头覆盖的 `sound` fact。
- `source_span` 与 `source_spans` 互斥；多 span 严格升序、无重叠、无重复。
- 备注内所有方括号标签必须属于第 8 节封闭清单；非连续 Beat 必须使用 `+` 且注明 `[非连续Beat]` 原因。
- 任何镜头包含 `keyframe` 字段都是失败项。

---

## 11. 生成与校验

优先调用 `codex_app__load_workspace_dependencies` 获取 bundled Python 路径；脚本需要 `openpyxl`。若当前工具面未提供该入口，只能使用运行环境已明确提供且实际可启动的 bundled Python，不得回退到用户名或项目绝对路径硬编码。

2.4.3 的 `build` 与 `validate` 都必须显式传入 `--workspace-root` 和 `--report`；旧版本只能执行只读 `validate`。每次提交 Gate 审核前，先用只读 `review-hash` 生成当前审核范围的 hash；该命令不修改文件，也不代表内容已通过校验：

```powershell
& <bundled-python> <skill-root>/scripts/storyboard_delivery.py review-hash --data <片名>.shot_data.json --gate GATE_A
& <bundled-python> <skill-root>/scripts/storyboard_delivery.py review-hash --data <片名>.shot_data.json --gate GATE_B
& <bundled-python> <skill-root>/scripts/storyboard_delivery.py review-hash --data <片名>.shot_data.json --gate GATE_C
```

分批任务另按 `GATE_0`（无 `--batch-id`）→每批 `GATE_A/GATE_B --batch-id BTxx`→全局 `GATE_C`（无 `--batch-id`）计算；单批 Gate A/B 省略 `--batch-id`。预签发与最终签发命令分别为：

```powershell
& <bundled-python> <skill-root>/scripts/storyboard_delivery.py build --workspace-root <workspace-root> --data <片名>.shot_data.json --markdown <片名>.md --excel <片名>.xlsx --report <片名>.validation_report.json
node <skill-root>/scripts/validate_storyboard.js --python <bundled-python> --workspace-root <workspace-root> --data <片名>.shot_data.json --markdown <片名>.md --excel <片名>.xlsx --report <片名>.validation_report.json

& <bundled-python> <skill-root>/scripts/storyboard_delivery.py build --final-signoff --workspace-root <workspace-root> --data <片名>.shot_data.json --markdown <片名>.md --excel <片名>.xlsx --report <片名>.validation_report.json
node <skill-root>/scripts/validate_storyboard.js --final-signoff --python <bundled-python> --workspace-root <workspace-root> --data <片名>.shot_data.json --markdown <片名>.md --excel <片名>.xlsx --report <片名>.validation_report.json
```

校验状态：

- `PASS`：结构、覆盖、连续性、时长、Prompt、三文件一致，且 Gate 记录完整。
- `WARN`：全部 WARN 均有 `warn_resolutions` 处置记录后方可交付。
- `FAIL`：禁止交付，必须修正后重跑。
- `NOT_RUN`：仅用于合法 builder 已生成三份正式产物、但最终校验环境暂不可用的降级状态；hash 留空，禁止伪造，须 Gate C 人工显式接受。builder 缺失时禁止生成新交付。

2.4.3 校验器额外强制检查：真实源文与 span、对白、ID/引用、Beat order、RFC 6901 继承、声源对象与迁移、最新 Gate/hash、project lexicon 冻结、事实覆盖、时长公式、封闭标签、WARN、NOT_RUN、must_isolate、纵深推拉方向反转及跨场连续性。`source_json_hash` 等于 `canonical_data_hash`：排除 `validation_report`、`human_reviews`、`metadata.revision_log`，包含 `warn_resolutions`；Gate C `reviewed_hash` 必须等于该 hash。strict validate 重算真实结果，不接受陈旧或自称 PASS 的报告。

四份输出必须先在同目录临时文件中完成生成与自检，再原子替换正式文件。任何结构、解析、依赖、权限或损坏文件错误都必须返回结构化 FAIL，不得泄露 traceback，也不得在 FAIL 时回写输入 JSON。

---

## 12. 交付验收

- 三个同名文件齐全且来自同一 `shot_data`。
- Gate A / B / C 均有 `approved` 记录（长输入含 Gate 0）。
- Beat/Fact ID 唯一且永久稳定，Beat order 严格递增并完整覆盖；每镜覆盖 ≥1 事实；原文对白引号内未改字。
- 连续性状态机逐镜推进无漂移；RFC 6901 继承、SSxx 声源与迁移登记合法。
- max 时长公式、长镜分类、长镜支撑项、切点字段全部合法。
- `must_isolate` 事实无非法合并；纵深推拉方向反转的 `[反转动机]`、`[必拆相邻]`、`[安全镜]` 均经 Gate B 复核。
- 所有 WARN 有处置记录；`NOT_RUN` 有人工接受记录。
- 运镜结构、场景首镜站位、Prompt 五字段完整；构图字段无对白、声音、动作链。
- Markdown 与 Excel 的表头、行数、镜号和逐格内容一致。
- 主表不含关键帧列、不含封闭清单外标注、不含过程痕迹；`revision_log` 为唯一过程记录。

---

## 附录 A：reference 文件配套修订要求

本文件生效前，必须同步修订以下引用文件：

**continuity-shot-data.md**
1. 增加 `scene_id` 字段，JSON 内引用一律用 scene_id。
2. 迁移触发表替换为本文件 7.3 节的固定版（含被动位移、朝向变化与声源变化）。
3. 写入继承优先级与 RFC 6901 pointer；旧顶层裸字段按 `/<字段名>` 兼容。
4. `cut_reasons` 条款改为："`recommended` 与 `must_isolate` 时必须非空；`normal` 时可为空数组"。
5. 写入 `fact.text` 字面化规则（禁止视觉化翻译进 fact 层）。
6. Beat ID 永久稳定；新增只取未用更大号，叙事排序与中点插入只使用 Decimal `beat_order`。
7. 顶层 JSON 补 `human_reviews`、`warn_resolutions`、`revision_log`、`script_status`、`reference_proof`、`batch_plan`。
8. `validation_report.status` 增加 `NOT_RUN`。
9. `long_take.classification` 枚举成文；时长明确为同步两项取 max 后加非同步动作与留白。
10. "每镜必须覆盖 ≥1 事实"写入合同。

**camera-language.md**
1. 纵深推拉方向反转节保留 `[反转动机]`（WARN + Gate B），并声明它不是 180 度越轴。
2. 相邻信息增量节增加 `[必拆相邻]` 豁免。
3. 增加仲裁顺序引用：must_isolate 拆分 > 信息增量合并。

**hybrid-shot-audit.md**
1. `must_isolate` 合并条件改为"同 Beat + 同 `cut_moment_id`"；`cut_category` 降为统计审计用途。
2. 密度 WARN 补度量定义（含 ≥1 个 must_isolate 事实的 Beat）与"仅人工可降级"。
3. 项目词库已迁入低位阶 `project-notes.md`；运行时只从 `metadata.project_lexicon` 读取安全字面词。
4. `long_take_support` 阈值表述去版本化（>10 秒一律适用）。
5. 增加 `safety` / `transition` 绑定事实与 `[安全镜][人工批准]` 规则。

**seedance-prompt-rules.md**
1. 跨景别镜头 `景别` 字段写 `起始景别→结束景别`。
2. 增加 800 字符 WARN 与"禁止截断台词"。
3. 对白保真只比对引号内内容。
4. "禁止修改字段"改为引用本文件第 0 节的受保护审计字段统一清单。

**project-notes.md（已迁移）**
该可选文件承接现有项目字面词与项目偏好，位阶低于 Skill；需要启用时显式复制安全字面词到 `metadata.project_lexicon`，文件内容本身不自动生效。

---

## 附录 B：本版修复映射（速查）

| 修复项 | 对应旧版漏洞 |
| --- | --- |
| 真实读取 `approved_script_path` + BOM/换行规范化 + 精确 span | 假源文凭证与 Windows span 漂移 |
| 版本 profile + 仅当前版 build + 未知版本拒绝 | 版本降级与 fail-open |
| 最新轮次裁决 + 阶段 hash + Gate C canonical hash | 历史批准绕过与签发 hash 自毁 |
| 非空结构、ID/引用/类型完整性 | 空台账、空事实与悬空引用漏检 |
| strict 报告重算 + WARN 当前态处置 | 伪造 PASS、陈旧报告与 `revise` 假关闭 |
| `--workspace-root` + 原子四文件 + `--final-signoff` | 路径漂移、半套产物与漏签发 |
| 合并条件改同 moment + `[必拆相邻]` 豁免 + 仲裁第 6 条 | 拆/合规则死锁 |
| 版本兼容表集中 + long_take_support 去版本化 + 受保护字段统一清单 | 版本作用域矛盾 |
| 触发表补被动位移与朝向 | 连续性触发遗漏 |
| 每镜必覆盖事实 + `[安全镜][人工批准]` | 空镜后门 |
| 纵深推拉方向反转 + `[反转动机]`，与 180 度越轴分离 | 运镜方向与空间轴线概念混淆 |
| `revision_log` 合法化修复迭代 | 修复与后处理禁令冲突 |
| 密度指标定义 + 仅人工降级 | WARN 度量未定义 |
| `fact.text` 字面化 | 保真 WARN 系统性误报 |
| `NOT_RUN` 协议 + 禁伪造 hash + 诚实优先条款 | 伪造校验激励 |
| Gate 0 分批协议 + 禁截断 JSON | 长剧本截断风险 |
| project-notes.md + `metadata.project_lexicon` 已迁移 | 项目内容泄漏到通用校验器 |
| scene_id + 永久 Beat ID + Decimal beat_order | 标识符重编与插入死锁 |
| 文件名清洗 | 命令注入面 |
| 800 字符 WARN + 禁截断台词 | 下游截断风险 |
