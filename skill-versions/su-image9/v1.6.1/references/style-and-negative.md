# su-image9 Style And Negative Reference

Use this file when generating `final_image_prompts.md` or when the user asks to generate images.

## STYLE_LOCK

Use this compact wording once per page. It must be identical across pages in one batch.

```text
STYLE_LOCK:
Unified black-and-white director blocking sketch. Same clean pencil line width, same light gray density, low-detail faces, simple costume silhouettes, sparse structural environment. Prioritize composition, camera viewpoint, character placement, floor plane, object positions, action phase, and continuity over beauty, texture, atmosphere, or face matching. Not a polished illustration, not manga, not photoreal.
```

## CANVAS_LOCK

Use this compact wording once per page.

```text
CANVAS_LOCK:
One wide horizontal 16:9 canvas. Exact clean 3x3 storyboard grid, nine equal horizontal 16:9 panels, straight borders and gutters. No text or labels inside the image. P01 establishes the master space; P02-P09 inherit it unless a source shot changes state.
```

## NEGATIVE_LOCK

Keep this compact. Do not repeat negatives inside every panel. It must be identical across pages in one batch.

```text
NEGATIVE_LOCK:
No text, labels, captions, panel numbers, shot numbers, subtitles, arrows, UI, monitor graphics, logos, watermarks, Chinese or English writing. No photorealism, realistic skin, portrait rendering, cinematic lighting, color, CGI, 3D render, painting, polished illustration, manga/comic layout, collage, poster, heavy texture, dense environment rendering, mixed panel sizes.
```

Do not write countdown, numeric countdown, bpm, HR, ECG, monitor UI, or readable numerals in the final prompt. If the story has a countdown or heartbeat, convert it before final prompt into non-readable rhythm marks or omit it from the image layer.

## Abstract Heartbeat Rule

ECG-like, heartbeat, pulse, or rhythm marks are allowed only as non-readable abstract visual rhythm. They must not become monitor UI, a data grid, readable numbers, `bpm`, `HR`, labels, device interface, or screen text.
