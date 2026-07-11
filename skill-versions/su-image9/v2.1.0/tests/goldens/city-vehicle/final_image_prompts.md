# PAGE-01

DELIVERABLE:
@CANON(HARD_PHRASES)

SYSTEM_STYLE_LAYER:
@CANON(SYSTEM_STYLE_LAYER)

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
@CANON(GEOMETRY_BLUEPRINT)
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
@CANON(NEGATIVE_CONSTRAINTS)
