# su-image9 Output Templates

<!-- ref-version: 2.0.3 -->

Required prompt outputs: `分析与锁定.md`、`panel_plan.json`、`page-map.json`、`final_image_prompts.md`、`final_image_prompts.compiled.md`、`validation_report.json`。只有 `release_ready=true` 的生图链路另产 `generation_manifest.json` 与 `pages/`。2.0.3 不承诺 PDF、ZIP 或自动标注产物。

状态与进程退出码必须一致：`0=PASS`、`1=REVIEW_REQUIRED`、`2=CONTRACT_FAIL`、`3=TOOL_ERROR`。退出码非 0 时 `release_ready` 必须为 `false`；`review_required_reasons` 是 `{code, page, message}` 对象数组，不接受裸字符串。稳定原因码包括 `R-UPSTREAM-WARN`、`R-CROSS-SCENE`、`R-CROSS-LAYER`、`R-SPARSE-UNIQUENESS`、`R-FIRST-SHOT-ANCHOR`、`R-TEXT-ONLY-DEPRECATED`、`R-VALIDATOR-MISSING` 和 `R-CANON-MISSING`。text-only、缺 validator/canon、不可锚定首镜、跨场/跨层页和 unresolved sparse 页均不得产生可发布 batch。

## panel_plan.json Template

```json
{
  "skill": "su-image9",
  "version": "2.0.3",
  "canon_version": "2.0.3",
  "release_ready": true,
  "review_required_reasons": [],
  "reference_binding_status": "bound | prompt_only | not_bound",
  "forbidden_prompt_tokens_extra": [],
  "pages": [
    {
      "page": "PAGE-01",
      "sparse_page": false,
      "source_shot_range": "1-9",
      "sequence_order_policy": "strict_source_order_no_anchor_reorder",
      "page_split_policy": "strict_single_scene_single_reality_layer",
      "source_scene_ids": ["S01"],
      "source_layer_keys": ["current"],
      "split_reason": "max_page_size_reached | scene_reality_boundary_or_end_of_source",
      "anchor_decision": "deterministic_source_order | review_required",
      "panels": [
        {
          "panel": "PANEL-1",
          "source_shot": 1,
          "beat_ids": ["B001"],
          "covered_fact_ids": ["F001"],
          "shot_data_camera_tag": "exact tag from shot_data brackets",
          "source_camera_tag": "exact tag from shot_data brackets",
          "drawn_camera_tag": "drawn camera follows source camera tag: <exact source tag>",
          "visible_characters": ["角色名"],
          "offscreen_characters": [],
          "visible_props": ["来源明确的道具"],
          "continuity_updates": [],
          "visible_only": "specific visible characters and concrete props or none",
          "action_composition": "machine-track drawable action summary",
          "floor_axis_delta": "specific floor, axis endpoints, camera side, screen sides",
          "prop_state": "concrete prop state or none",
          "distance_stage_lock": "none | pre-approach/end-state lock for adjacent movement endpoint"
        }
      ]
    }
  ]
}
```

## page-map.json Template

```json
{
  "skill": "su-image9",
  "version": "2.0.3",
  "canon_version": "2.0.3",
  "release_ready": true,
  "review_required_reasons": [],
  "page_split_policy": "strict_single_scene_single_reality_layer",
  "pages": [
    {
      "page_no": 1,
      "layout": "9",
      "source": "PAGE-01.png",
      "header": "场景｜镜头001-009",
      "source_shot_range": "1-9",
      "sparse_page": false,
      "page_split_policy": "strict_single_scene_single_reality_layer",
      "split_reason": "max_page_size_reached",
      "panels": [
        {
          "panel_no": 1,
          "shot_nos": [1],
          "label_shot_no": 1
        }
      ]
    }
  ]
}
```

## final_image_prompts.md Template

```markdown
# PAGE-01 short title

DELIVERABLE:
@CANON(HARD_PHRASES)
@CANON(GEOMETRY_BLUEPRINT)

SYSTEM_STYLE_LAYER:
@CANON(SYSTEM_STYLE_LAYER)

SCENE_LAYER:
...

CAMERA_RULE_LAYER:
...

CONTINUITY_LAYER:
...

TEXT_DERIVED_LAYOUT:
...

PANEL_1_MASTER_SPATIAL_LAYOUT_ANCHOR:
...

DOOR_WINDOW_FURNITURE_GEOMETRY_LOCK:
...

VEHICLE_AND_AXIS_LOCKS:
...

OBJECT_VISIBILITY_AND_BOUNDARIES:
...

PANEL_LAYER PANEL-1 to PANEL-9:
PANEL-1: Natural-language visual description sentence...
PANEL-2: Natural-language visual description sentence...
PANEL-3: Natural-language visual description sentence...
PANEL-4: Natural-language visual description sentence...
PANEL-5: Natural-language visual description sentence...
PANEL-6: Natural-language visual description sentence...
PANEL-7: Natural-language visual description sentence...
PANEL-8: Natural-language visual description sentence...
PANEL-9: Natural-language visual description sentence...

NEGATIVE_CONSTRAINTS:
@CANON(NEGATIVE_CONSTRAINTS)
```

## generation_manifest.json Template

```json
{
  "skill": "su-image9",
  "version": "2.0.3",
  "canon_version": "2.0.3",
  "release_ready": true,
  "review_required_reasons": [],
  "batch_id": "F-xxxxxxxxxxxxxxxx",
  "prompt_source": "path/to/final_image_prompts.compiled.md",
  "hc_confirmations": [],
  "images": [
    {
      "page": "PAGE-01",
      "attempts": [
        {
          "attempt_no": 1,
          "prompt_sha256": "sha256-of-compiled-page-text",
          "result": "pass | fail",
          "failed_items": []
        }
      ],
      "acceptance_status": "pass | accepted_with_defects | fail_converge"
    }
  ]
}
```
