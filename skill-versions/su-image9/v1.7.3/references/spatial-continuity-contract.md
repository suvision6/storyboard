# su-image9 Spatial Continuity Contract

<!-- ref-version: 1.7.3 -->

Use this file when a task has `shot_data.json`, locked shot numbers, reference assets, relationship shots, or any image generation request.

## Required Source Reads

When available, read and use:

- `shots[].camera_main_image`
- `shots[].visible_characters`
- `shots[].offscreen_characters`
- `shots[].visible_props`
- `shots[].continuity_updates`
- top-level `continuity_logs`

`continuity_logs` are the main source for fixed anchors, floor planes, starting positions, facing directions, axes, reality layers, and prop states.

## Where Spatial Data Belongs

Detailed spatial reasoning belongs in `分析与锁定.md` and `panel_plan.json`. `final_image_prompts.md` only receives the compact facts needed to draw the page.

Do not copy old 1.6.0 spatial layers into final prompt. The final prompt must use:

```text
CONTINUITY_LOCK:
Space=[specific]. Fixed anchors=[specific names]. Floor=[specific walkable surface]. Forbidden=[specific zones]. Axis A=[specific], B=[specific], camera side=[specific], screen left=[specific], screen right=[specific]. Props=[ownership and state constraints].

PANEL_TASKS PANEL-1 to PANEL-9:
FLOOR / AXIS DELTA: floor=...; A=...; B=...; camera side=...; screen left=...; screen right=...; foreground=...; background=...; shoulder=if needed.
```

## PANEL-1 Anchor Override

If the first source shot is a close-up, reaction, over-shoulder, insert, black frame, or local prop shot:

- PANEL-1 must be rewritten as a master spatial anchor.
- Keep source shot ID for traceability.
- Keep the source camera tag in `MUST MATCH SHOT_DATA CAMERA TAG`.
- Add `DRAWN CAMERA TAG: master wide/full spatial anchor`.
- PANEL-1 must use `anchor_visible_allowed` from `panel_plan.json`, not the source shot's original single-person `VISIBLE ONLY`.
- PANEL-1 must identify specific floor/surface, fixed anchors, character/object start positions or allowed empty positions, and forbidden standing zones.

## Floor, Elevation, And Forbidden Standing Zones

Every page with terrain, ledges, platforms, stairs, pits, cave voids, roads, vehicles, beds, or floors must state:

- The named floor plane or surface where feet, knees, bodies, or props can physically rest.
- Forbidden standing zones such as below cliff, inside void, beyond ledge edge, inside mist core, air column, ceiling, wall face, unreachable background.
- Whether `screen lower` means foreground framing or a physically lower elevation.
- Whether a character may cross from one plane to another in this page.

For a cliff/platform page: all visible human feet stay on the same upper platform unless the source explicitly shows a fall or descent; the lower void/cliff face is not a walking surface.

## Fixed Anchors

List fixed anchors from continuity or source: cave entrance, fissure, platform edge, floor, central void, ceiling, core, doorway, wall, furniture, road, vehicle, seat-window relation.

Each panel must inherit the anchor:

- Visible: state its specific screen position.
- Cropped: state it is offscreen while original position remains unchanged.
- Not applicable: state why it is outside the page space.

Do not replace fixed-anchor inheritance with vague wording such as `same cave layout`, `fixed objects`, or `as applicable`.

## Axis And Shoulder Locks

Relationship shots require concrete blocking:

- A endpoint and B endpoint.
- Camera allowed side and forbidden side.
- screen left and screen right.
- Foreground and background.
- Shoulder side for over-shoulder and reverse shots.
- Crop or push-in limits.

`do not cross the axis` alone is not valid.

## Split And Difference Rules

When fewer than 9 source shots are available, split only source-visible information:

- Establishing position.
- Action start.
- Contact / impact / crossing.
- Reaction.
- Prop state change.
- VFX phase.
- Result / aftermath.

Do not repeat the same source shot with the same camera scale, subject, screen area, and content text. If distinct visual tasks cannot fill 9 panels, change the page range instead of hard-filling.

## Prop Temporal State

A prop can have only one physical phase in a panel:

- Bracelet: on wrist, cracking on wrist, non-readable pulse, detaching, falling in air, lying on ground, turning to ash, offscreen.
- Staff: held by GC, inserted into ground, pale line glow, dim, cracked, broken near GC, offscreen.
- Mist/core: distant mass, tendril extension, surrounding pressure, dissolving particles, offscreen.

Do not draw a hand on the ground and a fallen bracelet on the ground in the same panel unless the source explicitly shows the hand still reaching above it with clear depth separation.

## Naming Rules

Use precise black-and-white effect tokens:

- `GREY_LXJ_MIST`: pale gray mist attached to Lin Xiaojie's dissolving body.
- `DARK_HOSTILE_MIST`: dark gray hostile mist body/core/tendrils/vortex.
- `LIGHT_DUST`: pale gray particles after dissolution.
- `BRACELET_PULSE`: non-readable bracelet pulse/crack/rhythm state.
- `WHITE_LIGHT`: pale operating-room-like light or abstract white light.

Do not use `MIST/VFX` as a catch-all. Do not write red/gold color terms in final image prompts; translate them to light/dark pencil functions.
