# su-image9 Validation Checklists

Use this file before delivering prompts, before image generation, and after images are generated.

## Semantic Validation

Stop with `任务失败：su-image9 语义规划失败` if any item fails.

- Source range is clear and traceable.
- If `shot_data.json` has `continuity_logs` or `continuity_updates`, they are read and reflected in `CONTINUITY_LAYER`.
- Reference assets are treated as identity/costume/prop anchors only, not detail or style targets.
- Page does not cross incompatible spaces, floor planes, or reality layers unless a source transition explicitly requires it.
- Panel 1 is a master spatial anchor; close-up/reaction/over-shoulder first shots use anchor override.
- P01 anchor override has `DRAWN CAMERA TAG`, `ANCHOR_VISIBLE_ALLOWED`, allowed standing surface, and forbidden standing zones.
- Every panel has `SOURCE SHOT`, `MUST MATCH SHOT_DATA CAMERA TAG`, `VISIBLE ONLY`, `MUST NOT SHOW`, `CHARACTER ANCHORS`, `SCREEN POSITION / AXIS LOCK`, `FLOOR / DEPTH LOCK`, and `CONTENT`.
- `VISIBLE ONLY`, `MUST NOT SHOW`, `CHARACTER ANCHORS`, `FLOOR / DEPTH LOCK`, and `CONTENT` do not contradict each other.
- Similar characters include anti-swap short anchors.
- Relationship shots include A/B endpoints, camera side, forbidden side, screen left/right, foreground/background, and shoulder side when applicable.
- Split panels have unique visual composition tasks; same source shot with only emotional difference is a failure.
- Prop temporal states are mutually exclusive within each panel.

## Cross-Field Failure Checks

These are hard failures even when all fields exist:

- `CONTENT` mentions a character that is not allowed by `VISIBLE ONLY` and is not an explicit P01 anchor-visible object.
- `VISIBLE ONLY` allows a prop/effect while `MUST NOT SHOW` forbids the same prop/effect.
- `CHARACTER ANCHORS` invites a prop that is absent from `visible_props`; example: GC visible without STAFF but anchor says only "staff owner" and no `no STAFF visible`.
- `MIST/VFX` or another catch-all token merges different source states such as grey Lin Xiaojie mist and hostile dark mist.
- A relationship panel has `过肩`, `双人`, `reverse`, `OTS`, or equivalent camera tag but no shoulder/foreground/background lock.
- `SCREEN POSITION / AXIS LOCK` or `FLOOR / DEPTH LOCK` is identical across most panels and fails to describe panel-specific crop, shoulder, level, or layer differences.
- A page uses source repetition to fill 9 panels but `SPLIT_COMPOSITION_DIFFERENCE_LOCK` does not provide a distinct camera/scale/subject/depth/action/prop delta.
- A character stands in a forbidden zone such as below cliff, void, wall face, ceiling, or core unless source explicitly requires it.
- Bracelet states such as on wrist, falling, on ground, and ash appear in the same panel.
- Final prompt contains color leakage such as red light, gold-black mist, 红光, 金黑, or 金色.
- Final prompt contains detail pressure such as high detail, portrait likeness, photoreal reference, exact face, detailed portrait, or copy reference lighting.

## Reference Asset Validation

- Reference assets are mapped to explicit characters/props.
- Content and style are separated.
- If image generation cannot bind image references, the output is not called formal reference-image generation.
- If a prop belongs to one character, every panel either shows that prop with the owner or explicitly forbids mis-ownership / visibility.
- If references conflict with user instruction, project docs, continuity, or `shot_data`, stop and list the conflict.

## final_image_prompts.md Validation

- File exists before image generation.
- Every page target is 5,000-9,000 characters.
- Any page over 12,000 characters stops the workflow.
- `DIRECTOR_BLOCKING_SKETCH_LAYER` appears before `PANEL_LAYER`.
- `ASSET_REFERENCE_LOCK` and `PROJECT_VISUAL_PROFILE` appear once per page before `PANEL_LAYER`.
- Required 1.6.0 layers appear before `PANEL_LAYER`: `CONTINUITY_LAYER`, `PANEL_1_MASTER_SPATIAL_LAYOUT_ANCHOR`, `FIXED_OBJECT_SCREEN_PROJECTION`, `FLOOR_PLANE_LOCK`, `ELEVATION_AND_DEPTH_LOCK`, `CAMERA_COMPOSITION_LOCK`, `PANEL_INHERITANCE_MAP`, `AXIS_AND_SHOULDER_LOCKS`, `SPLIT_COMPOSITION_DIFFERENCE_LOCK`, `PROP_TEMPORAL_PHASE_LOCK`.
- `OBJECT_VISIBILITY_AND_BOUNDARIES` is present but does not replace per-panel `VISIBLE ONLY`.
- Panel `CHARACTER ANCHORS` are short anchors, not full profile copies.
- General no-text/style/geometry negatives are not repeated inside every panel.
- Run `scripts/validate_su_image9_prompt.py` when `shot_data.json` and `panel_plan.json` are available.

## Raw Image Validation

Inspect generated images in this order:

1. Wide horizontal 16:9 canvas.
2. Strict 3x3 grid.
3. Nine equal panel frames, each horizontal 16:9.
4. No panel numbers, text, subtitles, labels, arrows, UI, readable digits, watermarks, or monitor data.
5. Clean black-pencil director blocking sketch only.
6. Panel 1 establishes the master space, floor plane, fixed anchors, and forbidden zones.
7. Later panels inherit Panel 1 geometry and fixed objects.
8. Character identity, hair, clothing, and prop ownership match `PROJECT_VISUAL_PROFILE`.
9. Similar male characters do not swap clothing, props, or roles.
10. Visible-only boundaries are respected.
11. Feet/knees/fallen bodies/props rest on allowed surfaces only.
12. Axis, screen left/right, shoulder side, foreground/background are not crossed.
13. Split panels are visually distinct when repeated sources are used.
14. Bracelet/staff/mist states are physically plausible and mutually exclusive.

If any item fails, mark the page as not deliverable, tighten `final_image_prompts.md`, and regenerate at most twice.

## Annotated Image / PDF Validation

Annotation belongs outside the generated image:

- Original no-text 16:9 image remains preserved.
- Chinese header and `C序号｜视角｜景别｜运镜` labels are added by post-processing only.
- Labels do not cover, compress, crop, or redraw panel content.
- Do not hard-cut the source grid into nine small images and redraw duplicate panel frames unless manual boundary validation requires it.
- PDF uses lossless or low-loss embedding; avoid default JPEG-only PDF output.
- Render-check PDF pages before delivery.
