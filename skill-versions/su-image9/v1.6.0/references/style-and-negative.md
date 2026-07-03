# su-image9 Style And Negative Reference

Use this file when generating `final_image_prompts.md` or when the user asks to generate images.

## DIRECTOR_BLOCKING_SKETCH_LAYER

```text
DIRECTOR_BLOCKING_SKETCH_LAYER:
Draw as a director blocking sketch for production alignment, not a finished illustration.
Use black pencil line drawing, clean readable strokes, sparse construction lines, low detail faces, simple costume silhouettes, light gray shadow blocks only.
Prioritize composition, camera viewpoint, character placement, floor plane, object positions, action phase, and continuity over beauty, texture, atmosphere, or portrait likeness.
Environment is structural only: floor, edge, doorway/fissure, wall, ceiling, core, fixed object silhouettes. No dense cave texture or decorative rendering.
Do not use photorealism, skin rendering, cinematic lighting, concept art, CGI, manga rendering, painted shading, heavy graphite texture, paper grain emphasis, or polished illustration.
All 9 panels must look like the same clean black-pencil blocking pass with the same low-detail drawing density.
```

## Strict Panel Geometry

Include this once per Image2 page:

```text
Generate one wide horizontal 16:9 canvas containing a clean 3x3 storyboard grid.
Draw exactly nine separate straight rectangular panel frames with visible gutters.
Arrange the 9 panels in three equal columns and three equal rows.
All 9 panels must have equal size, aligned edges, and horizontal 16:9 storyboard framing.
Do not create square, vertical, mixed-size, manga, comic, collage, poster, A4, or irregular layouts.
Panel 1 is the master spatial layout anchor. Panels 2-9 must inherit Panel 1's fixed space and object positions unless the source continuity states a change.
```

## NEGATIVE_CONSTRAINTS

Keep this compact. Do not repeat long negatives inside every panel.

```text
NEGATIVE_CONSTRAINTS:
No text inside the image. No labels, captions, panel numbers, scene headers, shot numbers, subtitles, arrows, UI, readable countdown digits, ECG data, bpm, HR, watermarks, logos, or Chinese/English writing.
No photorealism, realistic skin, portrait rendering, cinematic lighting, color, HDR, bloom, volumetric rays, depth blur, CGI, 3D render, digital painting, polished illustration, manga page, comic page, dynamic collage, poster composition, heavy texture, heavy ink fill, or mixed panel sizes.
Reference images provide identity silhouette, hairstyle silhouette, costume silhouette, prop shape, and prop ownership only; they never increase detail level or override the director blocking sketch style.
```

## Abstract Heartbeat Rule

ECG-like, heartbeat, pulse, or rhythm marks are allowed only as non-readable abstract visual rhythm. They must not become monitor UI, a data grid, readable numbers, `bpm`, `HR`, labels, device interface, or screen text.
