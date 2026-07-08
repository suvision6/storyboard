# su-image9 Output Templates

<!-- ref-version: 1.7.3 -->

Required outputs：`分析与锁定.md`、`panel_plan.json`、`final_image_prompts.md`（手写稿）、**`final_image_prompts.compiled.md`（validator 编译产物，生图唯一输入）**、`generation_manifest.json`（仅生图）。

## 分析与锁定.md Template

```markdown
# SU-IMAGE9｜分析与锁定

## 基本信息

| 项目 | 内容 |
|---|---|
| 技能 / 版本 | su-image9 / 1.7.3 |
| canon-version | 1.7.1 |
| 来源 | shot_data / script / user text |
| batch_id | F-xxxxxxxx xxxxxxxx 或 T-xxxxxxxxxxxxxxxx |
| 是否生图 | 否 / 是 |
| 参考图绑定状态 | bound / prompt_only / not_bound |
| validator 模式 | full / text-only |

## 资产与用途审查

| 资产 | 对象 | 只继承 | 禁止继承 | 冲突 |
|---|---|---|---|---|
| Image # | 角色/道具 | 轮廓、剪影、归属 | 照片质感、精修脸、色彩 | 无 / 说明 |

## 空间与连续性锁定

| Page | 来源镜号 | 主空间 | 固定锚点 | 地面/禁站区 | 轴线 | PANEL-1 处理 |
|---|---|---|---|---|---|---|
| PAGE-01 | 001-009 | ... | ... | ... | A=..., B=... | source / anchor_override / ⚠️待人工裁定（理由） |

## 逐格事实计划

| Page | Panel | Source | Source camera tag | Drawn camera tag | Visible only | Floor/axis delta | Prop state |
|---|---|---:|---|---|---|---|---|
| PAGE-01 | PANEL-1 | 001 | ... | ... | chars=...; props=... | ... | ... |

## ⚠️ 降级声明（HC-1 必审，置顶红旗）

| 降级项 | 适用页/格 | 理由 |
|---|---|---|
| sparse_page / 镜头不足策略 / not_bound raw_generation / 旧命名沿用 / 锚定判定不确定 | ... | ... |

## HC-1 提交表

| 项目 | 内容 |
|---|---|
| ⚠️ 降级声明 | 上表汇总（无则"无"） |
| 分页方案 | 各 PAGE 镜号范围与切分依据 |
| 每页 PANEL-1 处理 | source / override + 理由 |
| split 拆格 | 同源格与差异维度 |
| 参考图绑定状态 | 状态 + 可用生图模式 |
| 预计交付物 | prompt 包 / 生图 / 标注 / PDF / ZIP |
```

## panel_plan.json Template

```json
{
  "skill": "su-image9",
  "version": "1.7.3",
  "canon_version": "1.7.1",
  "source": "path-or-description",
  "reference_binding_status": "bound | prompt_only | not_bound",
  "forbidden_prompt_tokens_extra": ["仅追加；无法删减 canon 内置表"],
  "reference_assets": [
    { "image": "Image #1", "object": "LX",
      "purpose": "identity silhouette, hairstyle silhouette, costume silhouette, prop ownership" }
  ],
  "pages": [
    {
      "page": "PAGE-01",
      "title": "short page title",
      "shots": [1,2,3,4,5,6,7,8,9],
      "sparse_page": false,
      "space": "scene name",
      "fixed_anchors": ["specific entrance", "specific platform edge", "specific wall"],
      "floor_plane_lock": "named walkable surface",
      "forbidden_standing_zones": ["specific drop", "specific wall face"],
      "axis_endpoint_a": "specific A-end",
      "axis_endpoint_b": "specific B-end",
      "camera_side": "specific allowed side",
      "screen_left_right_lock": "screen left=...; screen right=...",
      "panels": [
        {
          "panel": "PANEL-1",
          "source_shot": 1,
          "source_camera_tag": "exact tag from shot_data brackets",
          "drawn_camera_tag": "same as source OR master wide/full spatial anchor",
          "anchor_override": true,
          "anchor_visible_allowed": { "characters": [], "props": [] },
          "visible_characters": ["LX"],
          "visible_props": ["BRACELET"],
          "vfx_state": ["none | body-state vapor effect | dissolving particles | environment effect"],
          "action_composition": "drawable action and composition only",
          "floor_axis_delta": "floor=...; A=...; B=...; camera side=...; screen left=...; screen right=...; foreground=...; background=...",
          "prop_temporal_state": "BRACELET non-readable pulse on LX wrist / no physical prop; no handheld object; vfx/body-state only if present",
          "floor_plane": "specific walkable surface",
          "forbidden_standing_zone": "specific forbidden zones"
        }
      ]
    }
  ]
}
```

## final_image_prompts.md Template（手写稿，1.7.3 标记制）

```text
# PAGE-01 short page title

STYLE_LOCK:
@CANON(STYLE_LOCK)

CANVAS_LOCK:
@CANON(CANVAS_LOCK)

REFERENCE_LOCK:
@CANON(REFERENCE_LOCK)
（无参考图流程改用 @CANON(REFERENCE_LOCK_TEXT_ONLY)）

CONTINUITY_LOCK:
Space=[specific]. Fixed anchors=[specific names]. Floor=[specific walkable surface]. Forbidden=[specific zones]. Axis A=[specific], B=[specific], camera side=[specific], screen left=[specific], screen right=[specific]. Props=[ownership and state constraints].

PANEL_TASKS PANEL-1 to PANEL-9:

PANEL-1:
SOURCE SHOT: 1
MUST MATCH SHOT_DATA CAMERA TAG: exact source tag
DRAWN CAMERA TAG: master wide/full spatial anchor
VISIBLE ONLY: chars=LX,SY; props=BRACELET.
ACTION / COMPOSITION: drawable composition with specific floor, fixed anchors, start positions, and forbidden zones.
FLOOR / AXIS DELTA: floor=specific; A=specific; B=specific; camera side=specific; screen left=specific; screen right=specific; foreground=specific; background=specific; shoulder=if relationship shot.
PROP STATE: BRACELET non-readable pulse on LX wrist.

[PANEL-2 至 PANEL-9 同一字段集，DRAWN CAMERA TAG 每格必写。]

NEGATIVE_LOCK:
@CANON(NEGATIVE_LOCK)
```

规则：手写 canon 全文被容忍（validator 自动修正并记 warn）；字符预算以**编译后**文本计；禁止旧 1.6.0 层、占位句、`CONTENT` 字段。

道具规则：`VISIBLE ONLY` 中 `props=` 只能写 `none` 或具体物理道具名，禁止 `props=yes/no/true/false/present/absent`；雾气、光点、光、能量余波、霜层、灰烬等 VFX / 身体状态 / 环境效果不得作为 physical props。无实体道具时 `PROP STATE` 必须明确写 `no physical prop; no handheld object; vfx/body-state only if present.`，禁止裸 `owned` / `ownership unchanged`。

## generation_manifest.json Template

```json
{
  "skill": "su-image9",
  "version": "1.7.3",
  "canon_version": "1.7.1",
  "batch_id": "F-xxxxxxxxxxxxxxxx | T-xxxxxxxxxxxxxxxx",
  "generation_mode": "prompt_only | raw_generation | formal_reference_image",
  "reference_binding_status": "bound | prompt_only | not_bound",
  "reference_risk": "none | unbound",
  "prompt_source": "path/to/final_image_prompts.compiled.md",
  "hc_confirmations": [
    { "checkpoint": "HC-1 | HC-2 | HC-3 | HC-4",
      "decision": "确认 | 修改后确认 | 接受缺陷交付 | 回退规划 | 终止",
      "user_reply_summary": "用户原话摘要",
      "waived_warnings": [],
      "round": 1 }
  ],
  "images": [
    {
      "page": "PAGE-01",
      "attempts": [
        { "attempt_no": 1,
          "prompt_sha256": "sha256-of-compiled-page-text",
          "prompt_used_verbatim": true,
          "canon_autofixed": false,
          "result": "pass | fail",
          "failed_items": [] }
      ],
      "raw_image_path": "path/to/raw/no-text/image.png",
      "reference_images_bound": true,
      "style_consistency_passed": true,
      "acceptance_status": "pass | accepted_with_defects | fail_converge"
    }
  ]
}
```

规则：`prompt_source` 必须指向 compiled 文件；`prompt_sha256` = 当次 compiled 页文本；attempts 上限 3；`accepted_with_defects` 须有 HC-3 记录；`fail_converge` 页按 R-MAP-4 处理。

## page-map.json 缺页字段（R-MAP-4）

```json
{ "page_no": 3, "status": "not_delivered", "reason": "F-CONVERGE (HC-3: 终止)", "layout": "3x3", "panels": [] }
```

正常页无 `status` 字段（默认 delivered）；缺页不重排其余页码。
