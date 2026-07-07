---
name: su-fenjingskill-zh
description: 剧情片导演分镜系统（人工门禁稳定版）。将完整剧本、分场或剧情段落转换为稳定 7 列电影分镜表，独立完成导演拆镜、Beat 与原文事实追踪、连续性台账、动态时长、精简视频 Prompt、shot_data JSON、Markdown、Excel 和完整交付校验；在 Beat 锁定、主表锁定、交付签发三处设强制人工审核门禁，审核通过前不得进入下一阶段。
---

# 剧情片导演分镜系统

<!-- skill-version: 2.4.2 -->

当前版本：2.4.2。
当前规则修订：`2.4.2-source-lock-entry-guard-2026-07-07`。

---

## 0.0 执行入口自检

在本项目执行完整剧本分镜时，必须使用项目内技能入口 `C:\Users\EDY\Documents\引魂师\skills\su-fenjingskill-zh`。如果存在同名全局技能或旧版缓存技能，只能作为只读参考，不得作为当前任务规则出处。

开始拆镜前必须确认三项：

1. `skills/su-fenjingskill-zh/VERSION` 为 `2.4.2`。
2. `SKILL.md` 当前规则修订为 `2.4.2-source-lock-entry-guard-2026-07-07`。
3. 实际使用的 `storyboard_delivery.py` 与 `validate_storyboard.js` 均来自项目内 `skills/su-fenjingskill-zh/scripts/`。

任一项无法确认时，停止生成并说明风险；不得用同名旧版技能继续交付。

---

## 0. 版本与兼容（唯一版本规则出处）

本文件其余部分的所有规则均指 2.4.2 本版规则，全文不再使用"2.3.4 修订版""2.3.6 起"等散点版本指代。旧数据兼容只按下表处理：

| metadata.version | 处理方式 |
| --- | --- |
| 2.3.2 / 2.3.3 | 只读兼容：不检查审计字段、切点字段、人工门禁。 |
| 2.3.4 / 2.3.5 / 2.3.6 | 只读兼容：按各自 `rule_revision` 校验，不要求 `human_reviews`。 |
| 2.4.0 | 只读兼容：人工门禁稳定版；不强制 `script_lock`。 |
| 2.4.1 | 只读兼容：源文锁定版；强制 `script_lock` 与 `source_span` 回切校验，不强制 `approved_script_path`。 |
| 2.4.2 | 本版全部规则生效；`rule_revision` 缺失或不匹配视为 FAIL；强制项目内技能入口自检、`approved_script_path` 外部源文凭证、`script_lock` 源文锁定与 `source_span` 回切校验。 |

### 受保护审计字段统一清单

Prompt 派生阶段及一切后置阶段禁止修改以下字段：

`shot_type`、`split_reason`、`insert_priority`、`long_take_support`、`cut_priority`、`cut_reasons`、`cut_group`、`cut_category`、`cut_moment_id`、`inherits_from`、`inherited_states`、`diverged_states`、`continuity_updates`、`covered_fact_ids`、`beat_ids`、`duration_seconds`、`duration_breakdown`、`long_take`、`human_reviews`、`script_lock`、`source_span`、`source_spans`。

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

禁止编造原文没有的情节、角色、道具、空间、情绪转折或过渡镜头。最小合理补足只允许处理轴线、朝向、机位侧等制作信息，必须在备注写 `[合理补足]`，不得补写剧情事实。

---

## 2. 必读资源与读取凭证

按以下产出阶段读取：

- 拆分 Beat 前：`references/continuity-shot-data.md`
- 主表锁定前：`references/hybrid-shot-audit.md`
- Gate A 批准后：`references/camera-language.md`
- Gate B 批准后：`references/seedance-prompt-rules.md`
- 可选：`references/project-notes.md`（项目层偏好，规则位阶低于本文件，冲突时以本文件为准）

**读取凭证**：每个已读文件必须在 `metadata.reference_status` 登记 `loaded | missing`，并在 `metadata.reference_proof` 摘录该文件首个标题行原文作为凭证。缺失文件写 `missing` 并在备注登记 `[reference missing]`，按内置最低规则降级执行；不得伪称已读取。

**2.4.2 源文锁定**：开始拆分 Beat 前，必须先生成顶层 `script_lock`，锁定人类确认后的完整剧本文本。`script_lock.locked_text` 是唯一可引用源文；如用户批准错字修正，修正后的文本进入 `locked_text`，原始修正意见进入 `script_lock.approved_corrections`。`script_lock.locked_text_hash` 使用去除空白后的 `locked_text` 计算 SHA-256。所有 `beats[*].source_text` 与 `shots[*].source_paragraph` 必须通过 `source_span` 或 `source_spans` 指向 `locked_text` 的 0-based 字符区间，校验器会按区间回切文本；任何摘要、改写、删字、换词或未登记来源区间均为 FAIL。

**源文锁定预检**：开始拆分 Beat 前必须同时保存一份外部可读的批准后源文凭证文件，例如 `outputs/YYYY-MM-DD/docs/<片名>.approved_script.txt`。`script_lock.locked_text` 必须与该文件全文一致；Gate A、Gate B 和 Gate C 前均需复核标题、全部场景头、全部人物行和正文行没有从 `locked_text` 中遗漏。若发现 `locked_text` 只包含表格段落、摘要段落或局部正文，立即回到输入检查阶段，不得继续生成。

**产出顺序门禁**：摄影术语不得出现在 Gate A 批准前的任何产出物（台账、Beat、事实）中。Gate A 批准后 Beat 层冻结；摄影阶段发现 Beat 问题必须走驳回回流，不得静默回改。

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
  "notes": "审核意见原文摘录"
}
```

4. **冻结与回流**：已批准数据冻结。后续阶段发现冻结数据有错，必须声明"申请回流至 Gate X"并说明理由，经人工同意后修改并重新过该门禁；`metadata.revision_log` 追加 `{round, trigger, summary}`。
5. `metadata.version == "2.4.0"`、`"2.4.1"` 或 `"2.4.2"` 时，预签发校验强制检查 Gate A/B 均有 `approved` 记录（存在 `batch_plan` 时还须 Gate 0）；最终签发校验额外要求 Gate C `approved`。`NOT_RUN` 交付必须在 Gate C 显式记录 `accepted_without_validation`。`2.4.1+` 额外要求 `script_lock` 与源文区间校验通过；`2.4.2` 额外要求 `approved_script_path` 外部源文凭证。

**修复迭代合法性**：因校验 FAIL 或人工驳回而合并、拆分、重设镜头属于合法修复，须记入 `revision_log`。被禁止的是无审计的自发批量后处理。交付数据不得含 `old_shot_no`、`PASS_INTERNAL`、`运镜修正`、`【镜内变化】` 等过程痕迹；`revision_log` 是唯一合法过程记录。

---

## 4. 工作流

1. **检查输入与环境**：确认剧本正文、场景、角色、空间、关键道具和对白；正文缺失即停止。登记 `reference_status` 与 `script_status`（`storyboard_delivery.py`、`validate_storyboard.js` 各标 `available | missing`）。2.4.1 起必须先写入 `script_lock`，并在后续 Beat/Shot 中只用 `source_span(s)` 从锁定剧本回切原文，不得手写摘要代替原文；2.4.2 起必须同步保存并登记 `approved_script_path`。
2. **分批（仅长输入）**：输入超过单场或预计单次输出无法完整承载时，先产出 `batch_plan`，过 **Gate 0**。逐批生成分片 `shot_data`，批间连续性依赖显式登记。单次输出必须停在完整场景边界，**禁止输出截断的 JSON**；最后合并分片并整体校验。
3. **建立连续性台账**：每场分配机器键 `scene_id`（S01、S02…），显示名仅用于展示；JSON 内一切场景引用只用 `scene_id`。按场景锁定空间轴线、固定物、角色初始站位、道具状态、声音来源、现实层级，填写 `first_shot_anchor_type`。
   - 跨场继承：显式 `inherits_from` **优先于**默认重置；未列入 `inherited_states` 的字段一律按新场景重置；同一字段不得同时出现在 `inherited_states` 与 `diverged_states`。
4. **拆分 Beat 与事实**：先生成本场 `space_anchor_fact` 与 `blocking_anchor_fact`，再按场景目标、动作/台词关系、空间变化、道具变化和现实层级拆分可表演 Beat。
   - Beat ID 唯一且单调递增即可，**允许空号**；修改时禁止重编号既有 ID，新增用空号插入。
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
   - 同场相邻轴向反转默认禁止；确有叙事动机时备注写 `[反转动机]` 加一句话理由，校验降为 WARN 并列入 Gate B 复核清单。
9. **【Gate B：主表锁定审核】** 提交审核包，停机等待。批准后前 6 列与审计字段冻结。
10. **派生 Prompt**：只派生第 7 列，不得触碰受保护审计字段清单中的任何字段；发现主表问题走回流申请，不得在 Prompt 层静默修表。
11. **保存单一数据源**：先写 `<片名>.shot_data.json`，再用脚本从该 JSON 同时生成 `<片名>.md` 和 `<片名>.xlsx`，不得分别手写三份内容。`<片名>` 仅允许中英文、数字、下划线、连字符，其余字符替换为下划线。
12. **运行校验**：
    - 脚本可用：执行 JSON/Markdown/Excel 三方校验，hash 由脚本计算写入。
    - 脚本或环境缺失：`validation_report.status = "NOT_RUN"`，hash 字段留空字符串，**禁止手写 hash、禁止自称 PASS**。`NOT_RUN` 交付必须在 Gate C 由人工显式记录 `accepted_without_validation`。
13. **【Gate C：交付签发审核】** 提交校验报告与 WARN 处置表，停机等待签发。
    - 每条 WARN 必须在 `warn_resolutions` 有条目 `{warn_id, resolution, resolved_by, note}`。
    - 仅白名单 WARN（reference missing、`[合理补足]`、节奏健康参考）允许 `resolved_by: "auto_whitelist"`；其余一律 `resolved_by: "human"`。

---

## 5. 7 列合同

固定列顺序：

| 镜号 | 场景 | 原剧本段落 | 镜头时长(秒) | 运镜+主画面描述(含台词) | 备注 | Prompt |
| --- | --- | --- | --- | --- | --- | --- |

- 镜号：从 1 开始连续纯数字；最终镜号由脚本在交付时统一重排一次。
- 场景列写显示名（`场景编号 场景名`）；`scene_id` 只存在于 JSON。每个新场景首镜必须在运镜列写 `【场景首镜站位】`。
- 场景首镜必须服从 `first_shot_anchor_type`：`space` / `multi_character` / `both` 的首镜必须使用 `大远景 / 大全景 / 全景 / 中全景`，优先建立地形方向、固定物、人物左右关系、朝向和距离。
- 原剧本段落以 Beat ID 开头：单 Beat 写 `B001～原文`；连续多 Beat 写 `B001-B003～原文`；非连续 Beat 用 `+`，且备注写 `[非连续Beat]` 加原因。2.4.1 起该列的“原文”必须由 `shots[*].source_span(s)` 从 `script_lock.locked_text` 回切生成，不得摘要、概括或删改。
- 不得使用"承上镜动作""补充镜头""新增过渡"等占位文字替代原文。
- 主表不含关键帧列；`shot_data.shots[*].keyframe` 字段不得出现。
- 全部审计字段只存在于 JSON，不进入 Markdown/Excel 7 列。
- 不得机械一 Beat 一镜；同样不得机械多 Beat 一镜：一个镜头覆盖 3 个及以上 Beat 且包含关键切点时视为过度压缩，必须重拆。

---

## 6. 镜头时长

```text
镜头时长 = max(同步动作, 同步台词) + 非同步动作 + 情绪留白
```

- **取整规则**：各分项先向上取整为非负整数，`duration_seconds` 必须精确等于分项之和。
- 正常中文对白约 3-4 字/秒；迟疑、悲伤或压低声音约 2 字/秒。估算存疑时取较长值，并在 Gate B 审核包中说明。
- 超过 6 秒：备注写 `[时长估算] 同步动作X秒 + 同步台词X秒 + 非同步动作X秒 + 情绪留白X秒`。
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
- 多人场景进入正反打、特写、道具特写或单人反应前，必须先用全景类镜头交代人物左右关系、朝向、距离和主要对视轴线。
- `single_continuation` / `subjective` 可不用全景类首镜，但必须用 `【场景首镜站位】` 或视觉锚点说明人物/空间边界。
- 全景必须承载空间、人物或行动信息；不得为满足规则添加无剧情事实的空镜。

### 7.2 每格固定结构

```text
[视角/高度, 景别/特殊视角, 摄影机运动方式]
【机位逻辑】摄影机的空间位置、朝向和画面控制意图。
【场景首镜站位】仅场景首镜出现：所有出场角色的位置和朝向。
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
- 同场相邻镜头**默认禁止轴向反转**：推进类运动后不得直接接拉出/拉远类运动，反向组合同样禁止。确有叙事动机（如推进揭示后拉出暴露空间代价）时，备注写 `[反转动机]` 加一句话理由，校验降为 WARN 并进入 Gate B 复核清单。

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

顶层结构在 `continuity-shot-data.md` 基础上新增：

```json
{
  "metadata": {
    "version": "2.4.2",
    "rule_revision": "2.4.2-source-lock-entry-guard-2026-07-07",
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

- `continuity_logs[*].scene_id` 为机器匹配键；`shots[*].scene_id` 必须与之对应。
- 每个镜头 `covered_fact_ids` 非空。
- `duration_breakdown` 各分项为非负整数，之和等于 `duration_seconds`。
- `visible_characters` 与 `offscreen_characters` 不得重叠。
- 任何镜头包含 `keyframe` 字段都是失败项。

---

## 11. 生成与校验

先调用 `codex_app__load_workspace_dependencies` 获取 bundled Python 路径；脚本需要 `openpyxl`。

```powershell
& <bundled-python> skills/su-fenjingskill-zh/scripts/storyboard_delivery.py build --data <片名>.shot_data.json --markdown <片名>.md --excel <片名>.xlsx --report <片名>.validation_report.json
node skills/su-fenjingskill-zh/scripts/validate_storyboard.js --python <bundled-python> --data <片名>.shot_data.json --markdown <片名>.md --excel <片名>.xlsx --report <片名>.validation_report.json
```

校验状态：

- `PASS`：结构、覆盖、连续性、时长、Prompt、三文件一致，且 Gate 记录完整。
- `WARN`：全部 WARN 均有 `warn_resolutions` 处置记录后方可交付。
- `FAIL`：禁止交付，必须修正后重跑。
- `NOT_RUN`：脚本或环境缺失时的唯一合法状态；hash 留空，禁止伪造；须 Gate C 人工显式接受。

2.4.2 数据的校验器额外强制检查：`approved_script_path` 外部源文凭证、`script_lock` 源文锁定与 `source_span(s)` 回切比对、`human_reviews` 完整性（预签发 Gate A/B，最终签发追加 Gate C）、每镜 ≥1 事实覆盖、分项时长求和、备注标注封闭清单、`warn_resolutions` 完整性、`NOT_RUN` 时 hash 为空、`must_isolate` 合并条件（同 Beat + 同 `cut_moment_id`）、轴向反转标注、跨场继承字段一致性。2.4.0 旧数据只读兼容，不补查 `script_lock`；2.4.1 旧数据只读兼容，不补查 `approved_script_path`。

---

## 12. 交付验收

- 三个同名文件齐全且来自同一 `shot_data`。
- Gate A / B / C 均有 `approved` 记录（长输入含 Gate 0）。
- Beat 与事实 ID 唯一、单调、完整覆盖；每镜覆盖 ≥1 事实；原文对白引号内未改字。
- 连续性状态机逐镜推进无漂移；触发表六类变化登记完整；跨场继承字段合法。
- 时长求和、长镜分类、长镜支撑项、切点字段全部合法。
- `must_isolate` 事实无非法合并；`[必拆相邻]`、`[反转动机]`、`[安全镜]` 均经 Gate B 复核。
- 所有 WARN 有处置记录；`NOT_RUN` 有人工接受记录。
- 运镜结构、场景首镜站位、Prompt 五字段完整；构图字段无对白、声音、动作链。
- Markdown 与 Excel 的表头、行数、镜号和逐格内容一致。
- 主表不含关键帧列、不含封闭清单外标注、不含过程痕迹；`revision_log` 为唯一过程记录。

---

## 附录 A：reference 文件配套修订要求

本文件生效前，必须同步修订以下引用文件：

**continuity-shot-data.md**
1. 增加 `scene_id` 字段，JSON 内引用一律用 scene_id。
2. 迁移触发表替换为本文件 7.3 节的六行版（含被动位移、朝向变化）。
3. 写入继承优先级：显式 `inherits_from` > 默认重置；未列字段一律重置。
4. `cut_reasons` 条款改为："`recommended` 与 `must_isolate` 时必须非空；`normal` 时可为空数组"。
5. 写入 `fact.text` 字面化规则（禁止视觉化翻译进 fact 层）。
6. Beat 编号改为"唯一单调、允许空号、禁止重编既有 ID"。
7. 顶层 JSON 补 `human_reviews`、`warn_resolutions`、`revision_log`、`script_status`、`reference_proof`、`batch_plan`。
8. `validation_report.status` 增加 `NOT_RUN`。
9. `long_take.classification` 枚举成文；分项时长求和规则成文。
10. "每镜必须覆盖 ≥1 事实"写入合同。

**camera-language.md**
1. 轴向反转节增加 `[反转动机]` 逃生标注（WARN + Gate B 复核）。
2. 相邻信息增量节增加 `[必拆相邻]` 豁免。
3. 增加仲裁顺序引用：must_isolate 拆分 > 信息增量合并。

**hybrid-shot-audit.md**
1. `must_isolate` 合并条件改为"同 Beat + 同 `cut_moment_id`"；`cut_category` 降为统计审计用途。
2. 密度 WARN 补度量定义（含 ≥1 个 must_isolate 事实的 Beat）与"仅人工可降级"。
3. **整节删除"第 13 集倾向"**，内容迁往 `project-notes.md`。
4. `long_take_support` 阈值表述去版本化（>10 秒一律适用）。
5. 增加 `safety` / `transition` 绑定事实与 `[安全镜][人工批准]` 规则。

**seedance-prompt-rules.md**
1. 跨景别镜头 `景别` 字段写 `起始景别→结束景别`。
2. 增加 800 字符 WARN 与"禁止截断台词"。
3. 对白保真只比对引号内内容。
4. "禁止修改字段"改为引用本文件第 0 节的受保护审计字段统一清单。

**新增 project-notes.md（可选，项目层）**
承接原第 13 集角色名、VO 清单、剧集倾向等项目私有内容；文件头注明"位阶低于 skill 层，冲突以 SKILL.md 为准"。

---

## 附录 B：本版修复映射（速查）

| 修复项 | 对应旧版漏洞 |
| --- | --- |
| 合并条件改同 moment + `[必拆相邻]` 豁免 + 仲裁第 6 条 | 拆/合规则死锁 |
| 版本兼容表集中 + long_take_support 去版本化 + 受保护字段统一清单 | 版本作用域矛盾 |
| 触发表补被动位移与朝向 | 连续性触发遗漏 |
| 每镜必覆盖事实 + `[安全镜][人工批准]` | 空镜后门 |
| `[反转动机]` 逃生标注 | 轴向反转无豁免 |
| `revision_log` 合法化修复迭代 | 修复与后处理禁令冲突 |
| 密度指标定义 + 仅人工降级 | WARN 度量未定义 |
| `fact.text` 字面化 | 保真 WARN 系统性误报 |
| `NOT_RUN` 协议 + 禁伪造 hash + 诚实优先条款 | 伪造校验激励 |
| Gate 0 分批协议 + 禁截断 JSON | 长剧本截断风险 |
| project-notes.md 剥离 | 项目内容泄漏 |
| scene_id + Beat 空号制 | 标识符脆弱性 |
| 文件名清洗 | 命令注入面 |
| 800 字符 WARN + 禁截断台词 | 下游截断风险 |
