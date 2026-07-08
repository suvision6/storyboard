# su-image9 Output Templates

<!-- ref-version: 2.0.0 -->

Required prompt outputs: `分析与锁定.md`、`panel_plan.json`、`final_image_prompts.md`、`final_image_prompts.compiled.md`。生图链路另产 `generation_manifest.json`、`page-map.json`、`pages/`。

## panel_plan.json Template

```json
{
  "skill": "su-image9",
  "version": "2.0.0",
  "canon_version": "2.0.0",
  "reference_binding_status": "bound | prompt_only | not_bound",
  "forbidden_prompt_tokens_extra": [],
  "pages": [
    {
      "page": "PAGE-01",
      "sparse_page": false,
      "anchor_decision": "human_confirmed | omitted when deterministic",
      "panels": [
        {
          "panel": "PANEL-1",
          "source_shot": 1,
          "shot_data_camera_tag": "exact tag from shot_data brackets",
          "drawn_camera_tag": "master wide/full spatial anchor",
          "visible_only": "specific visible characters and concrete props or none",
          "action_composition": "machine-track drawable action summary",
          "floor_axis_delta": "specific floor, axis endpoints, camera side, screen sides",
          "prop_state": "concrete prop state or none"
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
  "version": "2.0.0",
  "canon_version": "2.0.0",
  "batch_id": "F-xxxxxxxxxxxxxxxx | T-xxxxxxxxxxxxxxxx | S-xxxxxxxxxxxxxxxx",
  "prompt_source": "path/to/final_image_prompts.compiled.md",
  "hc_confirmations": [],
  "images": [
    {
      "page": "PAGE-01",
      "attempts": [
        {
          "attempt_no": 1,
          "prompt_sha256": "sha256-of-compiled-page-text",
          "canon_autofixed": false,
          "result": "pass | fail",
          "failed_items": []
        }
      ],
      "acceptance_status": "pass | accepted_with_defects | fail_converge"
    }
  ]
}
```
