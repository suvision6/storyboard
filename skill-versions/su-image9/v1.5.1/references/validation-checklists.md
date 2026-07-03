# su-image9 Validation Checklists

Use this file before delivering prompts, before image generation, and after images are generated.

## Semantic Validation

Stop with `任务失败：su-image9 语义规划失败` if any item fails.

- Source range is clear and traceable.
- If `shot_data.json` has `continuity_logs` or `continuity_updates`, they are read and reflected in `CONTINUITY_LAYER`.
- Page does not cross incompatible spaces unless a source transition explicitly requires it.
- Panel 1 is a master spatial anchor; close-up/reaction/over-shoulder first shots use anchor override.
- P01 anchor override has `DRAWN CAMERA TAG` and `ANCHOR_VISIBLE_ALLOWED`.
- P01 anchor visible objects do not conflict with its content.
- Every panel has `SOURCE SHOT`, `MUST MATCH SHOT_DATA CAMERA TAG`, `VISIBLE ONLY`, `MUST NOT SHOW`, `CHARACTER ANCHORS`, `SCREEN POSITION / AXIS LOCK`, and `CONTENT`.
- `MUST MATCH SHOT_DATA CAMERA TAG` matches the source bracketed camera tag, except P01 override also states the drawn anchor camera.
- `VISIBLE ONLY`, `MUST NOT SHOW`, `CHARACTER ANCHORS`, and `CONTENT` do not contradict each other.
- `VISIBLE ONLY` does not include source-invisible characters or props unless P01 anchor explicitly permits them.
- `MUST NOT SHOW` includes key offscreen characters, wrong props, future states, alternate spaces, readable text/UI, and page-specific high-risk errors.
- Similar characters include anti-swap short anchors.
- Relationship shots include A/B endpoints, camera side, forbidden side, screen left/right, foreground/background, and shoulder side when applicable.
- Vehicle shots include vehicle local coordinates, seat-window adjacency, camera occupancy, and same-side window relation.
- Split panels have unique visual tasks; same source shot with same content is a failure.

## Cross-Field Failure Checks

These are hard failures even when all fields exist:

- `CONTENT` mentions a character that is not allowed by `VISIBLE ONLY` and is not an explicit P01 anchor-visible object.
- `VISIBLE ONLY` allows a prop/effect while `MUST NOT SHOW` forbids the same prop/effect.
- `CHARACTER ANCHORS` invites a prop that is absent from `visible_props`; example: GC visible without STAFF but anchor says only "sole staff owner" and no `no STAFF visible`.
- `MIST/VFX` or another catch-all token merges different source states such as grey Lin Xiaojie mist and hostile gold-black mist.
- A relationship panel has `过肩`, `双人`, `reverse`, `OTS`, or equivalent camera tag but no shoulder/foreground/background lock.
- `SCREEN POSITION / AXIS LOCK` is identical across most panels and fails to describe panel-specific crop, shoulder, or layer differences.
- A page uses source repetition to fill 9 panels but `PANEL_DIFFERENCE_TASKS` does not provide a distinct drawable task for each repeated source.

## Reference Asset Validation

- Reference assets are mapped to explicit characters/props.
- Content and style are separated.
- If image generation cannot bind image references, the output is not called formal reference-image generation.
- If a prop belongs to one character, every panel either shows that prop with the owner or explicitly forbids mis-ownership / visibility.
- If references conflict with user instruction, project docs, continuity, or `shot_data`, stop and list the conflict.

## final_image_prompts.md Validation

- File exists before image generation.
- Every page is 7,000-11,000 characters.
- Any page over 12,000 characters stops the workflow.
- `SYSTEM_STYLE_LAYER` appears before `PANEL_LAYER`.
- `PROJECT_VISUAL_PROFILE` appears once per page before `PANEL_LAYER`.
- Required 1.5.1 layers appear before `PANEL_LAYER`: `CONTINUITY_LAYER`, `PANEL_1_MASTER_SPATIAL_LAYOUT_ANCHOR`, `FIXED_OBJECT_SCREEN_PROJECTION`, `PANEL_INHERITANCE_MAP`, `AXIS_AND_SHOULDER_LOCKS`, `PANEL_DIFFERENCE_TASKS`.
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
5. Monochrome graphite storyboard / pencil pre-visualization only.
6. Same artist, stroke weight, hatching, tonal range, and paper grain across all panels.
7. Panel 1 establishes the master space.
8. Later panels inherit Panel 1 geometry and fixed objects.
9. Character identity, hair, clothing, and prop ownership match `PROJECT_VISUAL_PROFILE`.
10. Similar male characters do not swap clothing, props, or roles.
11. Visible-only boundaries are respected.
12. Axis, screen left/right, shoulder side, foreground/background are not crossed.
13. Split panels are visually distinct when repeated sources are used.
14. Vehicle local coordinate rules pass where applicable.

If any item fails, mark the page as not deliverable, tighten `final_image_prompts.md`, and regenerate at most twice.

## Annotated Image / PDF Validation

Annotation belongs outside the generated image:

- Original no-text 16:9 image remains preserved.
- Chinese header and `C序号｜视角｜景别｜运镜` labels are added by post-processing only.
- Labels do not cover, compress, crop, or redraw panel content.
- Do not hard-cut the source grid into nine small images and redraw duplicate panel frames unless manual boundary validation requires it.
- PDF uses lossless or low-loss embedding; avoid default JPEG-only PDF output.
- Render-check PDF pages before delivery.
