# PAGE-01

DELIVERABLE:
Generate one wide horizontal 16:9 canvas containing a clean 3x3 storyboard grid.
Each of the 9 panels must also be a horizontal 16:9 storyboard frame.
Use the declared PAGE_SPATIAL_ANCHOR for spatial continuity across the entire 3x3 grid.
Preserve source-shot order and every source shot's original camera composition.
Do not redesign the room, exterior location, furniture footprint, terrain, road, doorway, vehicle position, or object positions in later panels.
Do not generate any text, labels, captions, panel numbers, scene headers, shot numbers, subtitles, arrows, or watermarks inside the image.

SYSTEM_STYLE_LAYER:
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

SOURCE_BINDING_LAYER:
This page is bound to source shots C001.
The structured panel plan is the only machine fact source; this Prompt must not override it.
Reference asset state: none.

SCENE_LAYER:
Scene S01; reality layer: 现实.
Source scene heading: 1 会客室 日 内.
Registered spatial axis: A与B保持同侧关系，A从起点移向终点，摄影机不跨轴。.
Registered fixed geometry: 门; 桌子.
Registered character placement: A: position 门口, facing B; B: position 桌边, facing A.

CAMERA_RULE_LAYER:
Preserve every source shot camera tag and source order; a derived angle may change only angle, shot size, or composition emphasis.
C001: source camera 同侧三分之四, 双人中景, 轻微横移; Composition: （A在门口，B在桌边，两人相对。）; Camera motion idea: 轻微横移; Visible action state: A握着钥匙走到B面前，B说：“到了。”

CONTINUITY_LAYER:
Visible character boundary: A、B.
Visible prop boundary: 钥匙.
Derived panels inherit the exact Beat, fact, action phase, emotional result, and continuity-state hash of their source panel.
Position and facing transitions follow only continuity_updates; never infer a distance endpoint from action keywords.

PAGE_SPATIAL_ANCHOR:
Use PANEL-1 / C001 as this page's declared spatial anchor.
Panel 1 still preserves its original director-approved source camera and composition; do not widen or redesign it to manufacture an anchor.
All angles remain on the registered side of the axis and may reveal only registered geometry.

FIXED_GEOMETRY_LOCK:
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
Source-defined fixed geometry for this page: 门; 桌子.

VEHICLE_AND_AXIS_LOCKS:
Preserve registered eyelines, facing, side-axis relationships, and screen-left/screen-right continuity.
Do not introduce unregistered transport objects or alter any registered object state.

OBJECT_VISIBILITY_AND_BOUNDARIES:
Draw only these visible registered props when their source panel calls for them: 钥匙.
Offscreen voices and characters remain outside the frame unless that source panel lists them as visible.

PANEL_LAYER:
PANEL-1: Draw 同侧三分之四, 双人中景, 轻微横移. Composition: （A在门口，B在桌边，两人相对。）; Camera motion idea: 轻微横移; Visible action state: A握着钥匙走到B面前，B说：“到了。” Visible characters: A、B. Offscreen characters must remain outside the frame: none. Visible registered props: 钥匙. Distance/position stage: endpoint-transition: A.position 门口 -> 桌边 (evidence: B002-F01). Do not add another action phase, character, prop, emotion result, or spatial fact.
PANEL-2: Draw same-axis wider composition derived from 同侧三分之四, 双人中景, 轻微横移. Use a wider composition on the established side of the axis, revealing only registered geometry. Preserve the source state exactly: Composition: （A在门口，B在桌边，两人相对。）; Camera motion idea: 轻微横移; Visible action state: A握着钥匙走到B面前，B说：“到了。” Visible characters: A、B. Offscreen characters must remain outside the frame: none. Visible registered props: 钥匙. Distance/position stage: endpoint-transition: A.position 门口 -> 桌边 (evidence: B002-F01). Do not add another action phase, character, prop, emotion result, or spatial fact.
PANEL-3: Draw same-axis tighter composition derived from 同侧三分之四, 双人中景, 轻微横移. Use a tighter composition on the same axis without advancing the action or emotional result. Preserve the source state exactly: Composition: （A在门口，B在桌边，两人相对。）; Camera motion idea: 轻微横移; Visible action state: A握着钥匙走到B面前，B说：“到了。” Visible characters: A、B. Offscreen characters must remain outside the frame: none. Visible registered props: 钥匙. Distance/position stage: endpoint-transition: A.position 门口 -> 桌边 (evidence: B002-F01). Do not add another action phase, character, prop, emotion result, or spatial fact.
PANEL-4: Draw same-side three-quarter view derived from 同侧三分之四, 双人中景, 轻微横移. Use a three-quarter view from the established side of the axis while preserving eyelines and positions. Preserve the source state exactly: Composition: （A在门口，B在桌边，两人相对。）; Camera motion idea: 轻微横移; Visible action state: A握着钥匙走到B面前，B说：“到了。” Visible characters: A、B. Offscreen characters must remain outside the frame: none. Visible registered props: 钥匙. Distance/position stage: endpoint-transition: A.position 门口 -> 桌边 (evidence: B002-F01). Do not add another action phase, character, prop, emotion result, or spatial fact.
PANEL-5: Draw same-side profile view derived from 同侧三分之四, 双人中景, 轻微横移. Use a profile view from the established side of the axis without reversing screen direction. Preserve the source state exactly: Composition: （A在门口，B在桌边，两人相对。）; Camera motion idea: 轻微横移; Visible action state: A握着钥匙走到B面前，B说：“到了。” Visible characters: A、B. Offscreen characters must remain outside the frame: none. Visible registered props: 钥匙. Distance/position stage: endpoint-transition: A.position 门口 -> 桌边 (evidence: B002-F01). Do not add another action phase, character, prop, emotion result, or spatial fact.
PANEL-6: Draw same-side high angle derived from 同侧三分之四, 双人中景, 轻微横移. Use a restrained high angle from the established side, preserving the identical action state and geometry. Preserve the source state exactly: Composition: （A在门口，B在桌边，两人相对。）; Camera motion idea: 轻微横移; Visible action state: A握着钥匙走到B面前，B说：“到了。” Visible characters: A、B. Offscreen characters must remain outside the frame: none. Visible registered props: 钥匙. Distance/position stage: endpoint-transition: A.position 门口 -> 桌边 (evidence: B002-F01). Do not add another action phase, character, prop, emotion result, or spatial fact.
PANEL-7: Draw same-side low angle derived from 同侧三分之四, 双人中景, 轻微横移. Use a restrained low angle from the established side, preserving the identical action state and geometry. Preserve the source state exactly: Composition: （A在门口，B在桌边，两人相对。）; Camera motion idea: 轻微横移; Visible action state: A握着钥匙走到B面前，B说：“到了。” Visible characters: A、B. Offscreen characters must remain outside the frame: none. Visible registered props: 钥匙. Distance/position stage: endpoint-transition: A.position 门口 -> 桌边 (evidence: B002-F01). Do not add another action phase, character, prop, emotion result, or spatial fact.
PANEL-8: Draw same-side over-shoulder view derived from 同侧三分之四, 双人中景, 轻微横移. Use an over-shoulder view only between the already visible characters; preserve eyelines and screen sides. Preserve the source state exactly: Composition: （A在门口，B在桌边，两人相对。）; Camera motion idea: 轻微横移; Visible action state: A握着钥匙走到B面前，B说：“到了。” Visible characters: A、B. Offscreen characters must remain outside the frame: none. Visible registered props: 钥匙. Distance/position stage: endpoint-transition: A.position 门口 -> 桌边 (evidence: B002-F01). Do not add another action phase, character, prop, emotion result, or spatial fact.
PANEL-9: Draw registered-prop insert derived from 同侧三分之四, 双人中景, 轻微横移. Use an insert of an already visible registered prop without changing its owner, position, state, or action stage. Preserve the source state exactly: Composition: （A在门口，B在桌边，两人相对。）; Camera motion idea: 轻微横移; Visible action state: A握着钥匙走到B面前，B说：“到了。” Visible characters: A、B. Offscreen characters must remain outside the frame: none. Visible registered props: 钥匙. Distance/position stage: endpoint-transition: A.position 门口 -> 桌边 (evidence: B002-F01). Do not add another action phase, character, prop, emotion result, or spatial fact.

NEGATIVE_CONSTRAINTS:
NEGATIVE_CONSTRAINTS:
No photorealism, no film still look, no realistic skin texture, no cinematic lighting, no cinematic grading, no HDR lighting, no bloom, no volumetric god rays, no depth-of-field blur, no CGI, no 3D render, no digital painting, no digital illustration look, no rendered concept art, no polished illustration, no watercolor, no oil painting, no painterly shading, no soft airbrush gradients, no anime rendering, no manga page, no comic page layout, no inked comic outlines, no clean manga line art, no dynamic collage, no masonry grid, no poster composition, no color, no pure black fill blocks, no heavy ink fill, no text inside the image, no labels, no subtitles, no arrows, no watermarks, no square panels, no vertical panels, no tall panels, no narrow panels, no mixed-size panels.
