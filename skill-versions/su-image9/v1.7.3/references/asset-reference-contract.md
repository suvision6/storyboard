# su-image9 Asset Reference Contract

<!-- ref-version: 1.7.3 -->

Use this file whenever the task includes reference images, asset images, image numbers, prop references, character turnarounds, or tail frames.

## Reference Purpose

Reference images are asset anchors, not rendering targets.

They may provide only:

- Identity silhouette: age impression, face outline, body proportion, role identity.
- Hairstyle silhouette: length, outline, major shape.
- Costume silhouette: clothing layers, collar shape, jacket/coat/shirt/pants outline, key readable contrast.
- Prop shape: approximate shape, scale, material impression in black-and-white sketch.
- Prop ownership: who may carry or wear the prop.
- Continuity guard: prevent character/prop swaps across panels and pages.

They must not provide:

- Photographic likeness pressure.
- Portrait-level detail.
- Skin rendering.
- Studio lighting.
- Color grading.
- High-detail fabric texture.
- CGI, painting, manga, AI polish, or finished illustration style.
- Permission to make the drawing more detailed than a director blocking sketch.

## Prompt Wording

Use canon markers in `final_image_prompts.md`; do not copy lock text from this file:

```text
REFERENCE_LOCK:
@CANON(REFERENCE_LOCK)

REFERENCE_LOCK for text-only flows:
@CANON(REFERENCE_LOCK_TEXT_ONLY)
```

## Short Character Anchors

Panel anchors must stay short and visible-only:

```text
LX: long hair silhouette, white blouse + loose jeans silhouette, bracelet owner, simplified face, screen right.
SY: dark long coat + black turtleneck silhouette, no staff.
GC: suit + tie + short beard silhouette, STAFF owner only when STAFF visible.
LXJ: young, black leather jacket + white shirt silhouette, may be semi-transparent.
```

Do not write `highly detailed`, `portrait likeness`, `photoreal reference`, `exact face`, `copy reference lighting`, 真人相似, 精修脸, 照片质感, or equivalent phrases in final image prompts.
