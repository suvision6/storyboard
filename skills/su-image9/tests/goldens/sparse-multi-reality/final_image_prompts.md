# PAGE-01

DELIVERABLE:
@CANON(HARD_PHRASES)

SYSTEM_STYLE_LAYER:
@CANON(SYSTEM_STYLE_LAYER)

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
C001: source camera 平视, 双人中景, 固定镜头; Composition: （A在门口，B在桌边，两人相对。）; Camera motion idea: 固定镜头; Visible action state: A和B站在门口，A握着钥匙。

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
@CANON(GEOMETRY_BLUEPRINT)
Source-defined fixed geometry for this page: 门; 桌子.

VEHICLE_AND_AXIS_LOCKS:
Preserve registered eyelines, facing, side-axis relationships, and screen-left/screen-right continuity.
Do not introduce unregistered transport objects or alter any registered object state.

OBJECT_VISIBILITY_AND_BOUNDARIES:
Draw only these visible registered props when their source panel calls for them: 钥匙.
Offscreen voices and characters remain outside the frame unless that source panel lists them as visible.

PANEL_LAYER:
PANEL-1: Draw 平视, 双人中景, 固定镜头. Composition: （A在门口，B在桌边，两人相对。）; Camera motion idea: 固定镜头; Visible action state: A和B站在门口，A握着钥匙。 Visible characters: A、B. Offscreen characters must remain outside the frame: none. Visible registered props: 钥匙. Distance/position stage: none. Do not add another action phase, character, prop, emotion result, or spatial fact.
PANEL-2: Draw same-axis wider composition derived from 平视, 双人中景, 固定镜头. Use a wider composition on the established side of the axis, revealing only registered geometry. Preserve the source state exactly: Composition: （A在门口，B在桌边，两人相对。）; Camera motion idea: 固定镜头; Visible action state: A和B站在门口，A握着钥匙。 Visible characters: A、B. Offscreen characters must remain outside the frame: none. Visible registered props: 钥匙. Distance/position stage: none. Do not add another action phase, character, prop, emotion result, or spatial fact.
PANEL-3: Draw same-axis tighter composition derived from 平视, 双人中景, 固定镜头. Use a tighter composition on the same axis without advancing the action or emotional result. Preserve the source state exactly: Composition: （A在门口，B在桌边，两人相对。）; Camera motion idea: 固定镜头; Visible action state: A和B站在门口，A握着钥匙。 Visible characters: A、B. Offscreen characters must remain outside the frame: none. Visible registered props: 钥匙. Distance/position stage: none. Do not add another action phase, character, prop, emotion result, or spatial fact.
PANEL-4: Draw same-side three-quarter view derived from 平视, 双人中景, 固定镜头. Use a three-quarter view from the established side of the axis while preserving eyelines and positions. Preserve the source state exactly: Composition: （A在门口，B在桌边，两人相对。）; Camera motion idea: 固定镜头; Visible action state: A和B站在门口，A握着钥匙。 Visible characters: A、B. Offscreen characters must remain outside the frame: none. Visible registered props: 钥匙. Distance/position stage: none. Do not add another action phase, character, prop, emotion result, or spatial fact.
PANEL-5: Draw same-side profile view derived from 平视, 双人中景, 固定镜头. Use a profile view from the established side of the axis without reversing screen direction. Preserve the source state exactly: Composition: （A在门口，B在桌边，两人相对。）; Camera motion idea: 固定镜头; Visible action state: A和B站在门口，A握着钥匙。 Visible characters: A、B. Offscreen characters must remain outside the frame: none. Visible registered props: 钥匙. Distance/position stage: none. Do not add another action phase, character, prop, emotion result, or spatial fact.
PANEL-6: Draw same-side high angle derived from 平视, 双人中景, 固定镜头. Use a restrained high angle from the established side, preserving the identical action state and geometry. Preserve the source state exactly: Composition: （A在门口，B在桌边，两人相对。）; Camera motion idea: 固定镜头; Visible action state: A和B站在门口，A握着钥匙。 Visible characters: A、B. Offscreen characters must remain outside the frame: none. Visible registered props: 钥匙. Distance/position stage: none. Do not add another action phase, character, prop, emotion result, or spatial fact.
PANEL-7: Draw same-side low angle derived from 平视, 双人中景, 固定镜头. Use a restrained low angle from the established side, preserving the identical action state and geometry. Preserve the source state exactly: Composition: （A在门口，B在桌边，两人相对。）; Camera motion idea: 固定镜头; Visible action state: A和B站在门口，A握着钥匙。 Visible characters: A、B. Offscreen characters must remain outside the frame: none. Visible registered props: 钥匙. Distance/position stage: none. Do not add another action phase, character, prop, emotion result, or spatial fact.
PANEL-8: Draw same-side over-shoulder view derived from 平视, 双人中景, 固定镜头. Use an over-shoulder view only between the already visible characters; preserve eyelines and screen sides. Preserve the source state exactly: Composition: （A在门口，B在桌边，两人相对。）; Camera motion idea: 固定镜头; Visible action state: A和B站在门口，A握着钥匙。 Visible characters: A、B. Offscreen characters must remain outside the frame: none. Visible registered props: 钥匙. Distance/position stage: none. Do not add another action phase, character, prop, emotion result, or spatial fact.
PANEL-9: Draw registered-prop insert derived from 平视, 双人中景, 固定镜头. Use an insert of an already visible registered prop without changing its owner, position, state, or action stage. Preserve the source state exactly: Composition: （A在门口，B在桌边，两人相对。）; Camera motion idea: 固定镜头; Visible action state: A和B站在门口，A握着钥匙。 Visible characters: A、B. Offscreen characters must remain outside the frame: none. Visible registered props: 钥匙. Distance/position stage: none. Do not add another action phase, character, prop, emotion result, or spatial fact.

NEGATIVE_CONSTRAINTS:
@CANON(NEGATIVE_CONSTRAINTS)

# PAGE-02

DELIVERABLE:
@CANON(HARD_PHRASES)

SYSTEM_STYLE_LAYER:
@CANON(SYSTEM_STYLE_LAYER)

SOURCE_BINDING_LAYER:
This page is bound to source shots C002.
The structured panel plan is the only machine fact source; this Prompt must not override it.
Reference asset state: none.

SCENE_LAYER:
Scene S01; reality layer: 回忆.
Source scene heading: 1 会客室 日 内.
Registered spatial axis: A与B保持同侧关系，A从起点移向终点，摄影机不跨轴。.
Registered fixed geometry: 门; 桌子.
Registered character placement: A: position 门口, facing B; B: position 桌边, facing A.

CAMERA_RULE_LAYER:
Preserve every source shot camera tag and source order; a derived angle may change only angle, shot size, or composition emphasis.
C002: source camera 同侧三分之四, 双人中景, 轻微横移; Composition: 可见主体：A、B；可见道具：钥匙。; Camera motion idea: 轻微横移; Visible action state: A到达桌边仍握着钥匙，B说：“到了。”

CONTINUITY_LAYER:
Visible character boundary: A、B.
Visible prop boundary: 钥匙.
Derived panels inherit the exact Beat, fact, action phase, emotional result, and continuity-state hash of their source panel.
Position and facing transitions follow only continuity_updates; never infer a distance endpoint from action keywords.

PAGE_SPATIAL_ANCHOR:
Use PANEL-1 / C002 as this page's declared spatial anchor.
Panel 1 still preserves its original director-approved source camera and composition; do not widen or redesign it to manufacture an anchor.
All angles remain on the registered side of the axis and may reveal only registered geometry.

FIXED_GEOMETRY_LOCK:
@CANON(GEOMETRY_BLUEPRINT)
Source-defined fixed geometry for this page: 门; 桌子.

VEHICLE_AND_AXIS_LOCKS:
Preserve registered eyelines, facing, side-axis relationships, and screen-left/screen-right continuity.
Do not introduce unregistered transport objects or alter any registered object state.

OBJECT_VISIBILITY_AND_BOUNDARIES:
Draw only these visible registered props when their source panel calls for them: 钥匙.
Offscreen voices and characters remain outside the frame unless that source panel lists them as visible.

PANEL_LAYER:
PANEL-1: Draw 同侧三分之四, 双人中景, 轻微横移. Composition: 可见主体：A、B；可见道具：钥匙。; Camera motion idea: 轻微横移; Visible action state: A到达桌边仍握着钥匙，B说：“到了。” Visible characters: A、B. Offscreen characters must remain outside the frame: none. Visible registered props: 钥匙. Distance/position stage: endpoint-transition: A.position 门口 -> 桌边 (evidence: B002-F01). Do not add another action phase, character, prop, emotion result, or spatial fact.
PANEL-2: Draw same-axis wider composition derived from 同侧三分之四, 双人中景, 轻微横移. Use a wider composition on the established side of the axis, revealing only registered geometry. Preserve the source state exactly: Composition: 可见主体：A、B；可见道具：钥匙。; Camera motion idea: 轻微横移; Visible action state: A到达桌边仍握着钥匙，B说：“到了。” Visible characters: A、B. Offscreen characters must remain outside the frame: none. Visible registered props: 钥匙. Distance/position stage: endpoint-transition: A.position 门口 -> 桌边 (evidence: B002-F01). Do not add another action phase, character, prop, emotion result, or spatial fact.
PANEL-3: Draw same-axis tighter composition derived from 同侧三分之四, 双人中景, 轻微横移. Use a tighter composition on the same axis without advancing the action or emotional result. Preserve the source state exactly: Composition: 可见主体：A、B；可见道具：钥匙。; Camera motion idea: 轻微横移; Visible action state: A到达桌边仍握着钥匙，B说：“到了。” Visible characters: A、B. Offscreen characters must remain outside the frame: none. Visible registered props: 钥匙. Distance/position stage: endpoint-transition: A.position 门口 -> 桌边 (evidence: B002-F01). Do not add another action phase, character, prop, emotion result, or spatial fact.
PANEL-4: Draw same-side three-quarter view derived from 同侧三分之四, 双人中景, 轻微横移. Use a three-quarter view from the established side of the axis while preserving eyelines and positions. Preserve the source state exactly: Composition: 可见主体：A、B；可见道具：钥匙。; Camera motion idea: 轻微横移; Visible action state: A到达桌边仍握着钥匙，B说：“到了。” Visible characters: A、B. Offscreen characters must remain outside the frame: none. Visible registered props: 钥匙. Distance/position stage: endpoint-transition: A.position 门口 -> 桌边 (evidence: B002-F01). Do not add another action phase, character, prop, emotion result, or spatial fact.
PANEL-5: Draw same-side profile view derived from 同侧三分之四, 双人中景, 轻微横移. Use a profile view from the established side of the axis without reversing screen direction. Preserve the source state exactly: Composition: 可见主体：A、B；可见道具：钥匙。; Camera motion idea: 轻微横移; Visible action state: A到达桌边仍握着钥匙，B说：“到了。” Visible characters: A、B. Offscreen characters must remain outside the frame: none. Visible registered props: 钥匙. Distance/position stage: endpoint-transition: A.position 门口 -> 桌边 (evidence: B002-F01). Do not add another action phase, character, prop, emotion result, or spatial fact.
PANEL-6: Draw same-side high angle derived from 同侧三分之四, 双人中景, 轻微横移. Use a restrained high angle from the established side, preserving the identical action state and geometry. Preserve the source state exactly: Composition: 可见主体：A、B；可见道具：钥匙。; Camera motion idea: 轻微横移; Visible action state: A到达桌边仍握着钥匙，B说：“到了。” Visible characters: A、B. Offscreen characters must remain outside the frame: none. Visible registered props: 钥匙. Distance/position stage: endpoint-transition: A.position 门口 -> 桌边 (evidence: B002-F01). Do not add another action phase, character, prop, emotion result, or spatial fact.
PANEL-7: Draw same-side low angle derived from 同侧三分之四, 双人中景, 轻微横移. Use a restrained low angle from the established side, preserving the identical action state and geometry. Preserve the source state exactly: Composition: 可见主体：A、B；可见道具：钥匙。; Camera motion idea: 轻微横移; Visible action state: A到达桌边仍握着钥匙，B说：“到了。” Visible characters: A、B. Offscreen characters must remain outside the frame: none. Visible registered props: 钥匙. Distance/position stage: endpoint-transition: A.position 门口 -> 桌边 (evidence: B002-F01). Do not add another action phase, character, prop, emotion result, or spatial fact.
PANEL-8: Draw same-side over-shoulder view derived from 同侧三分之四, 双人中景, 轻微横移. Use an over-shoulder view only between the already visible characters; preserve eyelines and screen sides. Preserve the source state exactly: Composition: 可见主体：A、B；可见道具：钥匙。; Camera motion idea: 轻微横移; Visible action state: A到达桌边仍握着钥匙，B说：“到了。” Visible characters: A、B. Offscreen characters must remain outside the frame: none. Visible registered props: 钥匙. Distance/position stage: endpoint-transition: A.position 门口 -> 桌边 (evidence: B002-F01). Do not add another action phase, character, prop, emotion result, or spatial fact.
PANEL-9: Draw registered-prop insert derived from 同侧三分之四, 双人中景, 轻微横移. Use an insert of an already visible registered prop without changing its owner, position, state, or action stage. Preserve the source state exactly: Composition: 可见主体：A、B；可见道具：钥匙。; Camera motion idea: 轻微横移; Visible action state: A到达桌边仍握着钥匙，B说：“到了。” Visible characters: A、B. Offscreen characters must remain outside the frame: none. Visible registered props: 钥匙. Distance/position stage: endpoint-transition: A.position 门口 -> 桌边 (evidence: B002-F01). Do not add another action phase, character, prop, emotion result, or spatial fact.

NEGATIVE_CONSTRAINTS:
@CANON(NEGATIVE_CONSTRAINTS)
