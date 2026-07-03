# su-image9 Validation Checklists

Use this file before delivering prompts, before image generation, and after images are generated.

## Semantic Validation

Stop with `任务失败：su-image9 语义规划失败` if any item fails.

- Source range is clear and traceable.
- If `shot_data.json` has `continuity_logs` or `continuity_updates`, they are read and reflected in `分析与锁定.md` and `panel_plan.json`.
- Reference assets are treated as identity/costume/prop anchors only, not detail, face, or style targets.
- Page does not cross incompatible spaces, floor planes, or reality layers unless a source transition explicitly requires it.
- P01 is a master spatial anchor; close-up/reaction/over-shoulder/insert/black first shots use anchor override.
- P01 anchor override has source camera tag, `DRAWN CAMERA TAG`, anchor-visible characters/props, allowed standing surface, forbidden standing zones, and specific fixed anchors.
- Every panel in `panel_plan.json` has source shot, source camera tag, drawn camera tag, visible characters, visible props, floor/axis delta, and prop temporal state.
- Split panels have unique visual composition tasks; same source shot with only emotional difference is a failure.
- Prop temporal states are mutually exclusive within each panel.

## Final Prompt Validation

Hard failures:

- Any page is over 5,000 characters.
- Any page is outside the 2,500-4,500 target range.
- Any page lacks one of the six required blocks: `STYLE_LOCK`, `CANVAS_LOCK`, `REFERENCE_LOCK`, `CONTINUITY_LOCK`, `PANEL_TASKS P01-P09`, `NEGATIVE_LOCK`.
- Any old 1.6.0 audit layer appears in `final_image_prompts.md`.
- `STYLE_LOCK` or `NEGATIVE_LOCK` differs across pages in the same batch.
- Prompt text contains placeholders: `page A/B`, `foreground/background/shoulder locked`, `as applicable`, `allowed positions`, `fixed objects`, `source action phase`, `source camera tag`.
- Prompt text contains countdown/digit/UI terms: countdown, numeric countdown, `数字`, bpm, HR, ECG, monitor UI, readable digits, 监护仪, 心跳仪.
- Prompt text contains color or detail pressure: 红光, 赤光, 金黑, 金色, red, gold, portrait likeness, exact face, photoreal reference, 精修脸, 真人相似, 照片质感.

## Fact Gate Against shot_data / panel_plan

`scripts/validate_su_image9_prompt.py` must reject:

- `SOURCE SHOT` differs from `panel_plan.json`.
- `MUST MATCH SHOT_DATA CAMERA TAG` differs from `panel_plan.json` or the bracket tag in `shot_data.json`.
- Non-anchor `VISIBLE ONLY` differs from `panel_plan.json` / `shot_data.json`.
- P01 anchor override uses source close-up single-person visibility instead of `anchor_visible_allowed`.
- P01 anchor override lacks `DRAWN CAMERA TAG: master wide/full spatial anchor`.
- `ACTION / COMPOSITION` for P01 anchor does not describe floor/surface/forbidden zones/start positions.
- `FLOOR / AXIS DELTA` does not contain A endpoint, B endpoint, camera side, screen left, screen right, foreground, and background.
- Relationship shots lack shoulder side or concrete foreground/background.
- Visible props/effects are absent from `PROP STATE`.
- STAFF appears with a non-GC character unless it is an explicit prop-only insert.
- BRACELET appears with a non-LX character unless it is an explicit prop-only insert.

## Reference Asset Gate

- Reference assets are mapped to explicit characters/props.
- Content and style are separated.
- If image generation cannot bind image references, the output is not called formal reference-image generation.
- `reference_binding_status=prompt_only` may deliver prompts but may not enter `formal_reference_image` generation.
- If references conflict with user instruction, project docs, continuity, or `shot_data`, stop and list the conflict.

## Raw Image Validation

Inspect generated images in this order:

1. Wide horizontal 16:9 canvas.
2. Strict 3x3 grid.
3. Nine equal panel frames, each horizontal 16:9.
4. No panel numbers, text, subtitles, labels, arrows, UI, readable numerals, watermarks, monitor data, or writing.
5. Clean black-pencil director blocking sketch only.
6. Same line width, same gray density, same low-detail faces, and same sketch density across pages.
7. Panel 1 establishes the master space, floor plane, fixed anchors, and forbidden zones.
8. Later panels inherit Panel 1 geometry and fixed objects unless the source state changes.
9. Character identity, hair, clothing, and prop ownership match `panel_plan.json`.
10. Similar male characters do not swap clothing, props, or roles.
11. Visible-only boundaries are respected.
12. Feet/knees/fallen bodies/props rest on allowed surfaces only.
13. Axis, screen left/right, shoulder side, foreground/background are not crossed.
14. Split panels are visually distinct when repeated sources are used.
15. Bracelet/staff/mist states are physically plausible and mutually exclusive.

If any item fails, mark the page as not deliverable, tighten `final_image_prompts.md`, and regenerate at most twice.

## generation_manifest.json Validation

- Manifest exists for every generated image batch.
- `prompt_used_verbatim=true` for each image.
- `prompt_sha256` matches the exact final prompt page text when present.
- `formal_reference_image` requires `reference_binding_status=bound`.
- `style_consistency_passed=true` is recorded for each image before delivery.

## Annotated Image / PDF Validation

Annotation belongs outside the generated image:

- Original no-text 16:9 image remains preserved.
- Chinese header and `C序号｜视角｜景别｜运镜` labels are added by post-processing only.
- Labels do not cover, compress, crop, or redraw panel content.
- PDF uses lossless or low-loss embedding; avoid default JPEG-only PDF output.
- Render-check PDF pages before delivery.
