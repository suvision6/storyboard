# su-image9 Style And Negative Reference

<!-- ref-version: 1.7.3 -->

Use this file when generating `final_image_prompts.md` or when the user asks to generate images.

## Canon Lock Usage

`canon-locks.md` is the only authority for lock text. In `final_image_prompts.md`, write marker references only; the validator compiles them into `final_image_prompts.compiled.md`.

```text
STYLE_LOCK:
@CANON(STYLE_LOCK)

CANVAS_LOCK:
@CANON(CANVAS_LOCK)

REFERENCE_LOCK:
@CANON(REFERENCE_LOCK)
or, for text-only flows:
@CANON(REFERENCE_LOCK_TEXT_ONLY)

NEGATIVE_LOCK:
@CANON(NEGATIVE_LOCK)
```

Keep the lock markers identical across pages in one batch. Do not repeat negative terms inside every panel; panel fields should carry only drawable action, composition, floor/axis, visible-only, and prop-state facts.

Do not write countdown, numeric countdown, bpm, HR, ECG, monitor UI, or readable numerals in the final prompt. If the story has a countdown or heartbeat, convert it before final prompt into non-readable rhythm marks or omit it from the image layer.

## Abstract Heartbeat Rule

ECG-like, heartbeat, pulse, or rhythm marks are allowed only as non-readable abstract visual rhythm. They must not become monitor UI, a data grid, readable numbers, `bpm`, `HR`, labels, device interface, or screen text.
