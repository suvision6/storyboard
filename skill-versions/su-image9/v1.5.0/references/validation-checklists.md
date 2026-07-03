# su-image9 Validation Checklists

Use this file before delivering prompts, before generating images, and after images are generated.

## Semantic Validation

Stop with `任务失败：su-image9 语义规划失败` if any item fails.

- Source range is clear and traceable.
- Page does not cross incompatible spaces unless a source transition explicitly requires it.
- Panel 1 is a master spatial anchor; if source first shot is close-up/reaction/over-shoulder, P01 anchor override is recorded.
- Every panel has `SOURCE SHOT`, `MUST MATCH SHOT_DATA CAMERA TAG`, `VISIBLE ONLY`, `MUST NOT SHOW`, `CHARACTER ANCHORS`, `SCREEN POSITION / AXIS LOCK`, and `CONTENT`.
- `MUST MATCH SHOT_DATA CAMERA TAG` matches the source bracketed camera tag.
- `VISIBLE ONLY` does not include source-invisible characters or props.
- `MUST NOT SHOW` includes key offscreen characters, wrong props, future states, alternate spaces, and page-specific high-risk errors.
- Relationship shots include concrete A/B endpoints, camera side, screen left/right, and shoulder side when applicable.
- Vehicle shots include vehicle local coordinates, seat-window adjacency, camera occupancy, and same-side window relation.
- Similar characters include anti-swap short anchors.

## Reference Asset Validation

- Reference assets are mapped to explicit characters/props.
- Content and style are separated.
- If image generation tool cannot bind image references, the output is not called a formal reference-image generation.
- If a prop belongs to one character, every panel either shows that owner or explicitly forbids mis-ownership.
- If references conflict with user instruction, project docs, or `shot_data`, stop and list the conflict.

## final_image_prompts.md Validation

- File exists before image generation.
- Every page is 7,000-11,000 characters.
- Any page over 12,000 characters stops the workflow.
- `PROJECT_VISUAL_PROFILE` appears once per page before `PANEL_LAYER`.
- `SYSTEM_STYLE_LAYER` appears before `PANEL_LAYER`.
- `OBJECT_VISIBILITY_AND_BOUNDARIES` is a page summary, not a duplicate per-panel table.
- Panel `CHARACTER ANCHORS` are short anchors, not full profile copies.
- Panel `SCREEN POSITION / AXIS LOCK` is panel-specific, not a repeated page-long axis.
- General no-text/style/geometry negatives are not repeated inside every panel.

## Raw Image Validation

Inspect generated images in this order:

1. Wide horizontal 16:9 canvas.
2. Strict 3x3 grid.
3. Nine equal panel frames, each horizontal 16:9.
4. No panel numbers, text, subtitles, labels, arrows, UI, readable digits, watermarks, or monitor data.
5. Monochrome graphite storyboard / pencil pre-visualization only.
6. Same artist, stroke weight, hatching, tonal range, and paper grain across all panels.
7. Panel 1 establishes the master space.
8. Later panels inherit Panel 1 geometry.
9. Character identity, hair, clothing, and prop ownership match `PROJECT_VISUAL_PROFILE`.
10. Similar male characters do not swap clothing, props, or roles.
11. Visible-only boundaries are respected.
12. Axis and screen left/right are not crossed.
13. Vehicle local coordinate rules pass where applicable.

If any item fails, mark the page as not deliverable, tighten `final_image_prompts.md`, and regenerate at most twice.

## Annotated Image / PDF Validation

Annotation belongs outside the generated image:

- Original no-text 16:9 image remains preserved.
- Chinese header and `C序号｜视角｜景别｜运镜` labels are added by post-processing only.
- Labels do not cover, compress, or crop panel content.
- Do not hard-cut the source grid into nine small images and redraw duplicate panel frames unless manual boundary validation requires it.
- PDF uses lossless or low-loss embedding; avoid default JPEG-only PDF output.
- Render-check PDF pages before delivery.
