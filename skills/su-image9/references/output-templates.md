# su-image9 Output Templates

Use this file when creating deliverables. In v1.6.1 the analysis draft may be detailed; `final_image_prompts.md` must be a short image-generation input, not a copied audit document.

Required outputs:

- `分析与锁定.md`
- `panel_plan.json`
- `final_image_prompts.md`
- `generation_manifest.json` only when images are generated

## 分析与锁定.md Template

```markdown
# SU-IMAGE9｜分析与锁定

## 基本信息

| 项目 | 内容 |
|---|---|
| 技能 | su-image9 |
| 版本 | 1.6.1 |
| 来源 | shot_data / script / user text |
| 输出 | 分析稿 + panel_plan.json + final_image_prompts.md |
| 是否生图 | 否 / 是 |
| 参考图绑定状态 | bound / prompt_only / not_bound |

## 资产与用途审查

| 资产 | 对象 | 只继承 | 禁止继承 | 冲突 |
|---|---|---|---|---|
| Image # | 角色/道具 | 轮廓、服装剪影、道具归属 | 照片质感、精修脸、真人相似、色彩风格 | 无 / 说明 |

## 空间与连续性锁定

| Page | 来源镜号 | 主空间 | 固定锚点 | 地面/禁站区 | 轴线 | P01 处理 |
|---|---|---|---|---|---|---|
| P01 | 001-009 | ... | ... | ... | A=..., B=... | source / anchor_override |

## 逐格事实计划

| Page | Panel | Source | Source camera tag | Drawn camera tag | Visible only | Floor/axis delta | Prop state |
|---|---|---:|---|---|---|---|---|
| P01 | P01 | 001 | ... | ... | chars=...; props=... | ... | ... |

## 输出前失败检查

| 项目 | 结果 | 说明 |
|---|---|---|
| P01 锚定真实成立 | 通过/失败 | ... |
| 无占位句 | 通过/失败 | ... |
| final prompt 字符预算 | 通过/失败 | ... |
| 参考图绑定状态 | 通过/失败 | ... |
```

## panel_plan.json Template

`panel_plan.json` is the validator's fact source. Do not leave generic placeholders.

```json
{
  "skill": "su-image9",
  "version": "1.6.1",
  "source": "path-or-description",
  "reference_binding_status": "bound | prompt_only | not_bound",
  "forbidden_prompt_tokens": [
    "page A/B",
    "foreground/background/shoulder locked",
    "as applicable",
    "allowed positions",
    "fixed objects",
    "source action phase",
    "source camera tag",
    "countdown",
    "数字",
    "bpm",
    "HR",
    "ECG",
    "red",
    "gold"
  ],
  "reference_assets": [
    {
      "image": "Image #1",
      "object": "LX",
      "purpose": "identity silhouette, hairstyle silhouette, costume silhouette, prop ownership"
    }
  ],
  "pages": [
    {
      "page": "P01",
      "title": "short page title",
      "shots": [1, 2, 3, 4, 5, 6, 7, 8, 9],
      "space": "scene name",
      "fixed_anchors": ["specific entrance", "specific platform edge", "specific wall"],
      "floor_plane_lock": "named walkable surface",
      "forbidden_standing_zones": ["specific drop", "specific wall face", "specific core interior"],
      "axis_endpoint_a": "specific A-end object/person/side",
      "axis_endpoint_b": "specific B-end object/person/side",
      "camera_side": "specific allowed camera side",
      "screen_left_right_lock": "screen left=...; screen right=...",
      "panels": [
        {
          "panel": "P01",
          "source_shot": 1,
          "source_camera_tag": "exact tag from shot_data camera_main_image brackets",
          "drawn_camera_tag": "same as source camera tag OR master wide/full spatial anchor",
          "p01_anchor_override": false,
          "anchor_visible_allowed": {
            "characters": [],
            "props": []
          },
          "visible_characters": ["LX"],
          "visible_props": ["BRACELET"],
          "action_composition": "drawable action and composition only",
          "floor_axis_delta": "floor=...; A=...; B=...; camera side=...; screen left=...; screen right=...; foreground=...; background=...",
          "prop_temporal_state": "BRACELET on LX wrist / none / STAFF held by GC",
          "screen_left_right_lock": "screen left=...; screen right=...",
          "axis_endpoint_a": "specific A end",
          "axis_endpoint_b": "specific B end",
          "floor_plane": "specific walkable surface",
          "forbidden_standing_zone": "specific forbidden zones"
        }
      ]
    }
  ]
}
```

## final_image_prompts.md Template

Each page must be 2,500-4,500 characters. Hard stop above 5,000 characters. Only the following six blocks are allowed as page-level blocks.

```text
# P01 short page title

STYLE_LOCK:
Unified black-and-white director blocking sketch. Same clean pencil line width, same light gray density, low-detail faces, simple costume silhouettes, sparse structural environment. Not a polished illustration, not manga, not photoreal.

CANVAS_LOCK:
One wide horizontal 16:9 canvas. Exact clean 3x3 storyboard grid, nine equal horizontal 16:9 panels, straight borders and gutters. No text or labels inside the image. P01 establishes the master space; P02-P09 inherit it unless a source shot changes state.

REFERENCE_LOCK:
Reference images only lock identity silhouette, hairstyle silhouette, costume silhouette, prop shape, and prop ownership. Do not copy photo texture, skin detail, lighting, color, refinement level, or face matching.

CONTINUITY_LOCK:
Space=[specific]. Fixed anchors=[specific names]. Floor=[specific walkable surface]. Forbidden=[specific zones]. Axis A=[specific], B=[specific], camera side=[specific], screen left=[specific], screen right=[specific]. Props=[ownership and state constraints].

PANEL_TASKS P01-P09:

P01:
SOURCE SHOT: 1
MUST MATCH SHOT_DATA CAMERA TAG: exact source tag
DRAWN CAMERA TAG: master wide/full spatial anchor
VISIBLE ONLY: chars=LX,SY; props=BRACELET.
ACTION / COMPOSITION: drawable composition with specific floor, fixed anchors, start positions, and forbidden zones.
FLOOR / AXIS DELTA: floor=specific surface; A=specific end; B=specific end; camera side=specific side; screen left=specific; screen right=specific; foreground=specific; background=specific; shoulder=if relationship shot.
PROP STATE: BRACELET non-readable pulse on LX wrist.

P02:
SOURCE SHOT: 2
MUST MATCH SHOT_DATA CAMERA TAG: exact source tag
VISIBLE ONLY: chars=...; props=...
ACTION / COMPOSITION: drawable action and composition only.
FLOOR / AXIS DELTA: floor=...; A=...; B=...; camera side=...; screen left=...; screen right=...; foreground=...; background=...
PROP STATE: none.

[P03-P09 use the same short field set.]

NEGATIVE_LOCK:
No text, labels, captions, panel numbers, shot numbers, subtitles, arrows, UI, monitor graphics, logos, watermarks, Chinese or English writing. No photorealism, realistic skin, portrait rendering, cinematic lighting, color, CGI, 3D render, painting, polished illustration, manga/comic layout, collage, poster, heavy texture, dense environment rendering, mixed panel sizes.
```

Rules:

- `STYLE_LOCK` and `NEGATIVE_LOCK` must be identical across pages in a batch.
- Do not write the old 1.6.0 layers in `final_image_prompts.md`.
- Do not write placeholder text such as `page A/B`, `as applicable`, `allowed positions`, `fixed objects`, or `source action phase`.
- Do not write countdown, numeric countdown, bpm, HR, ECG, monitor UI, readable digits, red, gold, portrait likeness, exact face, or photoreal reference.
- `CONTENT` is not a v1.6.1 field; use `ACTION / COMPOSITION`.

## generation_manifest.json Template

Required only when images are generated.

```json
{
  "skill": "su-image9",
  "version": "1.6.1",
  "generation_mode": "prompt_only | raw_generation | formal_reference_image",
  "reference_binding_status": "bound | prompt_only | not_bound",
  "prompt_source": "path/to/final_image_prompts.md",
  "images": [
    {
      "page": "P01",
      "prompt_used_verbatim": true,
      "prompt_sha256": "sha256-of-the-exact-page-text",
      "reference_images_bound": true,
      "raw_image_path": "path/to/raw/no-text/image.png",
      "style_consistency_passed": true,
      "acceptance_status": "pass | fail | needs_regeneration"
    }
  ]
}
```

Rules:

- `formal_reference_image` requires `reference_binding_status=bound`.
- `prompt_used_verbatim` must be true for every generated image.
- `style_consistency_passed` must be recorded for every generated image.
