---
name: su-image9
description: 从 su-fenjingskill-zh 2.4.2 的已锁定 shot_data.json 派生 Image2 3x3 黑白石墨电影分镜提示词、九格原图与外围标注 PNG。以 panel_plan.json 为唯一机器事实源，严格保持源镜顺序、原构图、场景、现实层、人物、道具和连续性；不修改导演主表。
---

# su-image9

## 版本

`2.1.0`

这是独立的九宫格黑白石墨分镜技能。
它读取导演主流程已经锁定的结构化镜头数据。
它不拆剧本、不改镜头、不回写主表。

## 何时触发

以下任务使用本 Skill：

- 从合规 `shot_data.json` 生成 3x3 九格提示词包。
- 为 Image2 / gpt-image-2 准备黑白石墨分镜页。
- 生成或复核 `panel_plan.json` 与 `page-map.json`。
- 对无字九格 PNG 添加外围页眉和格号图例。
- 检查九格页是否忠实继承源镜事实与连续性。

以下任务不使用本 Skill：

- 剧本拆 Beat、拆镜或修改导演镜头设计。
- 修改 `su-fenjingskill-zh` 主表、Prompt、关键帧或 Excel。
- 彩色概念图、写实剧照、漫画页或其他视觉风格。
- text-only 交付。

非黑白石墨请求直接报告超出技能范围。
不要进入“确认后改风格”的分支。

## 权威优先级

冲突时依次执行：

1. 用户当前明确指令，但不得改写已锁定剧情事实。
2. `shot_data.json` 的源镜、Beat、事实和连续性。
3. `panel_plan.json` 的当前批次机器事实。
4. `references/canon-locks.md` 的视觉与几何锁。
5. 已绑定参考资产中未被用户修改的身份或几何信息。

`panel_plan.json` 是本 Skill 唯一机器事实源。
Prompt、page-map、分析摘要和标注 manifest 都从它派生。
禁止分别手改多个交付物以追求表面一致。

## 输入门禁

正式入口只接受：

- `metadata.skill_name == "su-fenjingskill-zh"`。
- `metadata.version == "2.4.2"`。
- `script_lock.status == "locked"`。
- 上游 Gate A、Gate B、Gate C 均已有 `approved` 记录，其中 Gate C 是进入图像阶段的最终签发。
- 上游 `validation_report.status` 为 `PASS`。
- `validation_report.source_json_hash` 与当前源文件一致。

上游 `WARN` 必须逐条存在 `warn_resolutions`。
非白名单 WARN 只能由 `human` 处置。
处置摘要写入 `panel_plan.source.warning_digest`。
源文件或 WARN 集合变化后，旧批准立即失效。

`FAIL`、`NOT_RUN`、缺 Gate、缺哈希或缺处置均停止。

不提供 SC 自查替代正式机器门禁。

## 正式流程

### 1. 锁定来源

读取 `shot_data.json`，记录：

- 文件 SHA-256。
- 规范化内容哈希。
- 上游 Skill 版本。
- 上游校验状态。
- WARN 摘要。

任何后续产物必须引用同一来源摘要。

### 2. 绑定参考资产

参考资产状态只有：

- `none`：未提供参考资产。
- `bound`：已绑定到明确角色、道具、空间或 Panel。

提供了参考图却无法明确绑定时，返回 `F-ASSET`。
资产只约束身份、形状、归属和固定几何。
资产不得覆盖源镜动作、人物可见性、现实层或导演构图。

详见 `references/asset-reference-contract.md`。

### 3. 严格分页

一页只允许：

- 一个 `scene_id`。
- 一个 `reality_layer`。
- 最多九个源镜头。

场景或现实层变化必须换页。
不支持 cross-scene bridge。
不支持 cross-layer bridge。

黑场或纯声音 transition 只能结束已有页面。

它不能成为派生角度的来源。

无法合法归属时返回 `F-PAGE-ANCHOR`。

### 4. 保留源镜

每个源镜头先生成一个 `panel_kind=source` 的格子。

Panel 1 永远对应本页第一个源镜头。
Panel 1 保留该源镜原始 camera tag 和导演构图。
禁止为了建立空间而自动改宽、换角度或借用后序镜头。

页面另设 `spatial_anchor_panel`。
它指向第一个具有可靠空间依据的 source Panel。
该 Panel 可以不是 Panel 1。

空间锚点判定只依赖结构化空间信息。

不得用“回忆、手术、黑场”等关键词代替结构判断。

### 5. 补足九格

不足九格时只可生成 `panel_kind=derived_angle`。

派生格必须紧邻其 source Panel。

镜号序列必须非递减。

候选角度按以下顺序选择：

1. 同轴更宽或更紧构图。
2. 同侧三分之四角度。
3. 同侧侧面角度。
4. 已知空间内的高机位或低机位。
5. 双人过肩角度。
6. 已有可见道具插入。

过肩只用于至少两名可见角色。

道具插入只用于已登记的可见道具。

派生格只能改变机位角度、景别和构图重心。

以下内容必须与来源格完全相同：

- `scene_id` 与 `reality_layer`。
- Beat 与事实 ID。
- 可见和画外角色。
- 可见道具及其状态。
- 动作阶段与情绪结果。
- 连续性状态哈希。

派生格 `fact_delta` 必须为 `none`。
显示标签使用 `C005-A`、`C005-B`。
机器来源仍保存 `source_shot: 5`。

无法获得足够合法角度时返回 `F-SPARSE-COVERAGE`。

不得重复末镜、补写动作或虚构剧情来凑满九格。

分页与派生细节见 `references/spatial-continuity-contract.md`。

### 6. 建立 panel_plan

顶层必须包含：

- `skill`、`version`、`schema_version`。
- `source`、`canon`、`reference_bindings`。
- `pages` 与 `release_ready`。

Page 必须包含：

- `page`、`scene_id`、`reality_layer`。
- `page_mode`、`spatial_anchor_panel`。
- `source_shot_nos`、`completion_mode`、`panels`。

Panel 必须包含：

- `panel`、`panel_kind`、`source_shot`。
- `variant_suffix`、`display_label`。
- `source_camera_tag`、`drawn_camera_tag`。
- `beat_ids`、`covered_fact_ids`。
- `visible_characters`、`offscreen_characters`、`visible_props`。
- `continuity_state_hash`、`composition_task`。
- `distance_stage_lock`、`fact_delta`。

source Panel 使用：

- `variant_suffix: null`。
- `fact_delta: source`。

derived Panel 使用：

- 非空 `variant_suffix`。
- `fact_delta: none`。

完整结构见 `references/output-templates.md`。

### 7. 渲染 Prompt

最终层顺序固定为：

1. `DELIVERABLE`
2. `SYSTEM_STYLE_LAYER`
3. `SOURCE_BINDING_LAYER`
4. `SCENE_LAYER`
5. `CAMERA_RULE_LAYER`
6. `CONTINUITY_LAYER`
7. `PAGE_SPATIAL_ANCHOR`
8. `FIXED_GEOMETRY_LOCK`
9. `VEHICLE_AND_AXIS_LOCKS`
10. `OBJECT_VISIBILITY_AND_BOUNDARIES`
11. `PANEL_LAYER`
12. `NEGATIVE_CONSTRAINTS`

四个固定锁只从 `references/canon-locks.md` 编译。
PANEL 文本由 `panel_plan.json` 确定性渲染。
validator 必须从同一源数据重建并逐格比较。

任意手改或新增剧情事实均失败。

画内禁止文字、格号、字幕、水印和箭头。

### 8. 校验与授权

退出码固定：

- `0`：PASS。
- `1`：REVIEW_REQUIRED。
- `2`：CONTRACT_FAIL。
- `3`：TOOL_ERROR。

只有 `0` 可以对应 `release_ready=true`。

自然语言中的明确同意、修改或终止均有效。

用户已明确授权生图时，不重复要求固定字面回复。

单页最多重试两次。

重试耗尽后报告具体失败项和最后产物。

不得自行接受缺陷。

验证合同见 `references/validation-checklists.md`。

## 固定交付

Prompt 包固定包含六项：

1. `分析与锁定.md`
2. `panel_plan.json`
3. `page-map.json`
4. `final_image_prompts.md`
5. `final_image_prompts.compiled.md`
6. `validation_report.json`

正式图像阶段只增加：

- 原始无字九格 PNG。
- 外围标注 PNG。
- `annotation_manifest.json`。

不生成 text-only 或固定成果之外的打包文件。

## PNG 外围标注

调用：

```text
python scripts/annotate_storyboard_pages.py --data <shot_data.json> --page-map <page-map.json> --pages <pages_dir> --output <output_dir> [--font-path <font>]
```

标签只读取 `page-map.json` 的 `display_label`；标注前必须核对 page-map 为 2.1、`release_ready=true`，且其 source file SHA-256 与当前 `shot_data.json` 文件一致。

优先检测真实 3x3 边框。

检测失败时使用 canonical boxes，并在 manifest 写 warning。

无可靠中文字体时返回 TOOL_ERROR。

原始九格作为完整像素块一次性粘贴。

只允许在画布顶部和底部外围增加标签区。

禁止缩放、裁切、覆盖或在宫格行间插入标签带。

## Reference 路由

- 固定锁文本：`references/canon-locks.md`
- 分页、锚点和连续性：`references/spatial-continuity-contract.md`
- 参考资产绑定：`references/asset-reference-contract.md`
- Schema、交付和 CLI：`references/output-templates.md`
- 状态、失败和验收：`references/validation-checklists.md`

只读取当前步骤需要的 reference。

禁止把 reference 全文重新复制回本文件。

## 不可变边界

- 不修改 `su-fenjingskill-zh`。
- 不回写导演主表。
- 不让摄影术语反向改变源镜事实。
- 不让参考图改变剧情。
- 不让 derived Panel 产生事实增量。
- 不让 Prompt 成为新的机器事实源。
- 不以人工确认放行结构错误或事实篡改。
- 不在依赖缺失时伪装成正式可发布结果。
