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
This page is bound to source shots C001, C002.
The structured panel plan is the only machine fact source; this Prompt must not override it.
Reference asset state: none.

SCENE_LAYER:
Scene S01; reality layer: 现实.
Source scene heading: 1 城市街道 日 外.
Registered spatial axis: A与B保持同侧关系，A从起点移向终点，摄影机不跨轴。.
Registered fixed geometry: 道路边线; 路灯.
Registered character placement: A: position 路边, facing B; B: position 车头一侧, facing A.

CAMERA_RULE_LAYER:
Preserve every source shot camera tag and source order; a derived angle may change only angle, shot size, or composition emphasis.
C001: source camera 平视, 双人中景, 固定镜头; Composition: （A在路边轿车驾驶门外，B在车头一侧，两人同处轴线一侧。）; Camera motion idea: 固定镜头; Visible action state: A和B站在路边轿车旁，A握着车钥匙。
C002: source camera 侧面平视, 双人中景, 横移跟拍; Composition: 可见主体：A、B；可见道具：轿车、车钥匙。; Camera motion idea: 横移跟拍; Visible action state: A到达驾驶门边仍握着车钥匙，B说：“出发。”

CONTINUITY_LAYER:
Visible character boundary: A、B.
Visible prop boundary: 轿车、车钥匙.
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
Source-defined fixed geometry for this page: 道路边线; 路灯.

VEHICLE_AND_AXIS_LOCKS:
Preserve registered eyelines, facing, side-axis relationships, and screen-left/screen-right continuity.
Registered vehicles or transport objects: 轿车. Preserve their registered positions and states only.

OBJECT_VISIBILITY_AND_BOUNDARIES:
Draw only these visible registered props when their source panel calls for them: 轿车、车钥匙.
Offscreen voices and characters remain outside the frame unless that source panel lists them as visible.

PANEL_LAYER:
PANEL-1: Draw 平视, 双人中景, 固定镜头. Composition: （A在路边轿车驾驶门外，B在车头一侧，两人同处轴线一侧。）; Camera motion idea: 固定镜头; Visible action state: A和B站在路边轿车旁，A握着车钥匙。 Visible characters: A、B. Offscreen characters must remain outside the frame: none. Visible registered props: 轿车、车钥匙. Distance/position stage: pre-transition: keep A.position at 路边 before C002. Do not add another action phase, character, prop, emotion result, or spatial fact.
PANEL-2: Draw same-axis wider composition derived from 平视, 双人中景, 固定镜头. Use a wider composition on the established side of the axis, revealing only registered geometry. Preserve the source state exactly: Composition: （A在路边轿车驾驶门外，B在车头一侧，两人同处轴线一侧。）; Camera motion idea: 固定镜头; Visible action state: A和B站在路边轿车旁，A握着车钥匙。 Visible characters: A、B. Offscreen characters must remain outside the frame: none. Visible registered props: 轿车、车钥匙. Distance/position stage: pre-transition: keep A.position at 路边 before C002. Do not add another action phase, character, prop, emotion result, or spatial fact.
PANEL-3: Draw same-axis tighter composition derived from 平视, 双人中景, 固定镜头. Use a tighter composition on the same axis without advancing the action or emotional result. Preserve the source state exactly: Composition: （A在路边轿车驾驶门外，B在车头一侧，两人同处轴线一侧。）; Camera motion idea: 固定镜头; Visible action state: A和B站在路边轿车旁，A握着车钥匙。 Visible characters: A、B. Offscreen characters must remain outside the frame: none. Visible registered props: 轿车、车钥匙. Distance/position stage: pre-transition: keep A.position at 路边 before C002. Do not add another action phase, character, prop, emotion result, or spatial fact.
PANEL-4: Draw same-side three-quarter view derived from 平视, 双人中景, 固定镜头. Use a three-quarter view from the established side of the axis while preserving eyelines and positions. Preserve the source state exactly: Composition: （A在路边轿车驾驶门外，B在车头一侧，两人同处轴线一侧。）; Camera motion idea: 固定镜头; Visible action state: A和B站在路边轿车旁，A握着车钥匙。 Visible characters: A、B. Offscreen characters must remain outside the frame: none. Visible registered props: 轿车、车钥匙. Distance/position stage: pre-transition: keep A.position at 路边 before C002. Do not add another action phase, character, prop, emotion result, or spatial fact.
PANEL-5: Draw same-side profile view derived from 平视, 双人中景, 固定镜头. Use a profile view from the established side of the axis without reversing screen direction. Preserve the source state exactly: Composition: （A在路边轿车驾驶门外，B在车头一侧，两人同处轴线一侧。）; Camera motion idea: 固定镜头; Visible action state: A和B站在路边轿车旁，A握着车钥匙。 Visible characters: A、B. Offscreen characters must remain outside the frame: none. Visible registered props: 轿车、车钥匙. Distance/position stage: pre-transition: keep A.position at 路边 before C002. Do not add another action phase, character, prop, emotion result, or spatial fact.
PANEL-6: Draw 侧面平视, 双人中景, 横移跟拍. Composition: 可见主体：A、B；可见道具：轿车、车钥匙。; Camera motion idea: 横移跟拍; Visible action state: A到达驾驶门边仍握着车钥匙，B说：“出发。” Visible characters: A、B. Offscreen characters must remain outside the frame: none. Visible registered props: 轿车、车钥匙. Distance/position stage: endpoint-transition: A.position 路边 -> 驾驶门边 (evidence: B002-F01). Do not add another action phase, character, prop, emotion result, or spatial fact.
PANEL-7: Draw same-axis wider composition derived from 侧面平视, 双人中景, 横移跟拍. Use a wider composition on the established side of the axis, revealing only registered geometry. Preserve the source state exactly: Composition: 可见主体：A、B；可见道具：轿车、车钥匙。; Camera motion idea: 横移跟拍; Visible action state: A到达驾驶门边仍握着车钥匙，B说：“出发。” Visible characters: A、B. Offscreen characters must remain outside the frame: none. Visible registered props: 轿车、车钥匙. Distance/position stage: endpoint-transition: A.position 路边 -> 驾驶门边 (evidence: B002-F01). Do not add another action phase, character, prop, emotion result, or spatial fact.
PANEL-8: Draw same-axis tighter composition derived from 侧面平视, 双人中景, 横移跟拍. Use a tighter composition on the same axis without advancing the action or emotional result. Preserve the source state exactly: Composition: 可见主体：A、B；可见道具：轿车、车钥匙。; Camera motion idea: 横移跟拍; Visible action state: A到达驾驶门边仍握着车钥匙，B说：“出发。” Visible characters: A、B. Offscreen characters must remain outside the frame: none. Visible registered props: 轿车、车钥匙. Distance/position stage: endpoint-transition: A.position 路边 -> 驾驶门边 (evidence: B002-F01). Do not add another action phase, character, prop, emotion result, or spatial fact.
PANEL-9: Draw same-side three-quarter view derived from 侧面平视, 双人中景, 横移跟拍. Use a three-quarter view from the established side of the axis while preserving eyelines and positions. Preserve the source state exactly: Composition: 可见主体：A、B；可见道具：轿车、车钥匙。; Camera motion idea: 横移跟拍; Visible action state: A到达驾驶门边仍握着车钥匙，B说：“出发。” Visible characters: A、B. Offscreen characters must remain outside the frame: none. Visible registered props: 轿车、车钥匙. Distance/position stage: endpoint-transition: A.position 路边 -> 驾驶门边 (evidence: B002-F01). Do not add another action phase, character, prop, emotion result, or spatial fact.

NEGATIVE_CONSTRAINTS:
NEGATIVE_CONSTRAINTS:
No photorealism, no film still look, no realistic skin texture, no cinematic lighting, no cinematic grading, no HDR lighting, no bloom, no volumetric god rays, no depth-of-field blur, no CGI, no 3D render, no digital painting, no digital illustration look, no rendered concept art, no polished illustration, no watercolor, no oil painting, no painterly shading, no soft airbrush gradients, no anime rendering, no manga page, no comic page layout, no inked comic outlines, no clean manga line art, no dynamic collage, no masonry grid, no poster composition, no color, no pure black fill blocks, no heavy ink fill, no text inside the image, no labels, no subtitles, no arrows, no watermarks, no square panels, no vertical panels, no tall panels, no narrow panels, no mixed-size panels.
