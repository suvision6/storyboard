# su-image9 Style And Negative Reference

Use this file when generating `final_image_prompts.md` or when the user asks to generate images.

## SYSTEM_STYLE_LAYER

```text
SYSTEM_STYLE_LAYER:
This entire generation must follow a single unified storyboard production style.

STYLE ANCHOR:
Treat this as a single cohesive storyboard drawn by one graphite storyboard artist in a single production session. For batch generation, all outputs must match the same storyboard artist, same production session, same medium, same stroke weight, same shading density, and same unfinished storyboard look.

MEDIUM:
Monochrome graphite storyboard / pencil pre-visualization drawing only. Hand-drawn pencil / graphite sketch only. Production storyboard sheet. Animatic frame design. Non-painting, non-rendered, non-illustration.

LINE RULE:
Thin graphite linework only. Visible sketch strokes allowed. Construction lines allowed. Rough drafting lines allowed. No inked comic outlines. No polished clean manga line art.

SHADING RULE:
Light hatching only. Mid-gray tonal range. Controlled medium contrast only. No pure black fill blocks. No heavy ink fill. No painterly shading. No soft airbrush gradients.

TEXTURE RULE:
Paper-like sketch texture. Slightly rough graphite grain. High-frequency pencil texture. Unfinished production drawing aesthetic.

RENDERING RULE:
No digital painting, no photorealism, no CGI, no cinematic lighting, no bloom, no HDR lighting, no volumetric god rays, no depth-of-field blur, no airbrush gradients, no rendered concept art look.

CONSISTENCY RULE:
All 9 panels must share identical drawing style, graphite medium, stroke weight, shading density, texture grain, tonal range, and rendering restraint. No stylistic variation between panels is allowed.
```

## Strict Panel Geometry

Include this once per Image2 page:

```text
Generate one wide horizontal 16:9 canvas containing a clean 3x3 storyboard grid.
Draw exactly nine separate straight rectangular panel frames with visible gutters.
Arrange the 9 panels in a clean 3x3 storyboard grid: three equal columns and three equal rows.
All 9 panels must have the same width, the same height, the same 16:9 aspect ratio, and aligned edges.
Each of the 9 panels must also be a horizontal 16:9 storyboard frame.
Do not let any panel become square, vertical, tall, narrow, compressed, stretched, trapezoid, diagonal, rounded, or irregular.
Do not create 3:2, 4:3, A4, square, vertical, mixed-size, manga, comic, collage, or poster layouts.
Panel 1 is the master spatial layout anchor for the entire 3x3 grid.
All Panels 2-9 must be derived from the same Panel 1 layout.
Do not redesign the room, exterior location, furniture footprint, terrain, road, doorway, vehicle position, or object positions in later panels.
```

## NEGATIVE_CONSTRAINTS

Keep this compact. Do not repeat long negatives inside every panel.

```text
NEGATIVE_CONSTRAINTS:
No text inside the image. No labels, captions, panel numbers, scene headers, shot numbers, subtitles, arrows, UI, readable countdown digits, ECG monitor data, bpm, HR, watermarks, logos, or Chinese/English writing inside the image.
No photorealism, realistic skin rendering, cinematic lighting, cinematic grading, HDR, bloom, volumetric light, depth-of-field blur, CGI, 3D render, digital painting, polished illustration, manga page, comic page, dynamic collage, poster composition, color, pure black fill blocks, heavy ink fill, or mixed panel sizes.
Reference images provide identity, costume silhouette, prop shape, and spatial facts only; they do not change the graphite storyboard style.
```

## Abstract Heartbeat Rule

ECG-like, heartbeat, pulse, or rhythm marks are allowed only as non-readable abstract visual rhythm. They must not become monitor UI, a data grid, readable numbers, `bpm`, `HR`, labels, device interface, or screen text.
