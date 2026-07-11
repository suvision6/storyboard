# su-image9 Canon Locks

<!-- ref-version: 2.0.3 -->
<!-- canon-version: 2.0.3 -->

本文件是 `su-image9` v2.0.3 的 canon 编译源。2.0.3 暂时保留本文件、`SKILL.md` 内联锁块和 validator 出厂快照三份兼容副本；三者必须严格一致，不设最终仲裁者，不允许自动修复。本版未改动四个锁块正文，只升级 canon-version 以标记失败封闭门禁。

## 编译规则

- 本文件必须且只能定义 `SYSTEM_STYLE_LAYER`、`GEOMETRY_BLUEPRINT`、`HARD_PHRASES`、`NEGATIVE_CONSTRAINTS` 四个唯一锁块；缺版本、截断、缺块、重复块、未知块或逐块正文漂移均为合同失败。
- `final_image_prompts.md` 只可使用上述四个 `@CANON(NAME)` 标记；validator 必须在 `final_image_prompts.compiled.md` 中展开。
- 最终可生图文本中出现任何 `@CANON(` 字面量，均为硬性失败。
- validator 只能做加法校验：查缺、查漂移、查冲突；不得删冗余、砍长度、剔除重复强化句、重排或以 canon 原文静默覆盖手写漂移。
- 修改任一 canon 块、核心生图合同、派生规则或门禁行为时，必须同步更新 `SKILL.md` 内联副本并升 `canon-version`。

## 锁文本

### canon:SYSTEM_STYLE_LAYER

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

### canon:GEOMETRY_BLUEPRINT

```text
Strict panel geometry blueprint, mandatory before drawing:
Treat the final canvas as a clean wide horizontal 16:9 layout.
Draw exactly nine separate straight rectangular panel frames with visible gutters.
Arrange the 9 panels in a clean 3x3 storyboard grid: three equal columns and three equal rows.
All 9 panels must have the same width, the same height, the same 16:9 aspect ratio, and aligned edges.
Each panel frame must remain a flat horizontal 16:9 rectangle.
Do not let any panel become square, vertical, tall, narrow, compressed, stretched, trapezoid, diagonal, rounded, or irregular.
Keep gutters and margins as empty separating space. If a close-up needs more room, use empty background or negative space inside that panel; never change the panel shape or aspect ratio.
Do not create 3:2, 4:3, A4, square, vertical, mixed-size, manga, comic, collage, or poster layouts.
Do not create a manga page, comic page, dynamic collage, masonry grid, mixed panel sizes, tilted frames, perspective-distorted frames, overlapping panels, or a poster composition.
The content inside a panel may crop or zoom, but the panel frame itself must remain a flat horizontal 16:9 rectangle.
Geometry correctness does not replace the SYSTEM_STYLE_LAYER. The 3x3 grid must remain geometrically strict while all panel contents remain in the same monochrome graphite storyboard production style.
```

### canon:HARD_PHRASES

```text
Generate one wide horizontal 16:9 canvas containing a clean 3x3 storyboard grid.
Each of the 9 panels must also be a horizontal 16:9 storyboard frame.
Panel 1 is the master spatial layout anchor for the entire 3x3 grid.
All Panels 2-9 must be derived from the same Panel 1 layout.
Do not redesign the room, exterior location, furniture footprint, terrain, road, doorway, vehicle position, or object positions in later panels.
Do not generate any text, labels, captions, panel numbers, scene headers, shot numbers, subtitles, arrows, or watermarks inside the image.
```

### canon:NEGATIVE_CONSTRAINTS

```text
NEGATIVE_CONSTRAINTS:
No photorealism, no film still look, no realistic skin texture, no cinematic lighting, no cinematic grading, no HDR lighting, no bloom, no volumetric god rays, no depth-of-field blur, no CGI, no 3D render, no digital painting, no digital illustration look, no rendered concept art, no polished illustration, no watercolor, no oil painting, no painterly shading, no soft airbrush gradients, no anime rendering, no manga page, no comic page layout, no inked comic outlines, no clean manga line art, no dynamic collage, no masonry grid, no poster composition, no color, no pure black fill blocks, no heavy ink fill, no text inside the image, no labels, no subtitles, no arrows, no watermarks, no square panels, no vertical panels, no tall panels, no narrow panels, no mixed-size panels.
```

## 封闭硬禁词扩展

`forbidden_prompt_tokens_extra` 只能追加，不能删减 canon 内置硬禁。v2.0.3 必须扫描所有动态层，四个 canon 锁块本身不参与扫描。
