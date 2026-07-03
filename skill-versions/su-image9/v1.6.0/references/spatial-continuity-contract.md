# su-image9 Spatial Continuity Contract

Use this file when a task has `shot_data.json`, locked shot numbers, reference assets, relationship shots, or any image generation request.

## Required Source Reads

When available, read and use:

- `shots[].camera_main_image`
- `shots[].visible_characters`
- `shots[].offscreen_characters`
- `shots[].visible_props`
- `shots[].continuity_updates`
- top-level `continuity_logs`

`continuity_logs` are the main source for fixed objects, floor planes, starting positions, facing directions, axes, reality layers, and prop states.

## Mandatory Final Prompt Layers

`final_image_prompts.md` must keep these compact page layers:

```text
CONTINUITY_LAYER:
Fixed objects, character start positions, facing, prop states, reality layer, inherited/diverged states from continuity_logs and continuity_updates.

PANEL_1_MASTER_SPATIAL_LAYOUT_ANCHOR:
P01 drawn layout, fixed anchors, allowed hidden objects, character/object start positions, visible standing surfaces, and what Panels 2-9 inherit.

FIXED_OBJECT_SCREEN_PROJECTION:
For each fixed object, state screen position or "cropped/offscreen but unchanged"; never move it to a new side.

FLOOR_PLANE_LOCK:
Name the allowed standing surface, who stands/kneels/falls on it, and every forbidden standing zone.

ELEVATION_AND_DEPTH_LOCK:
Separate screen lower/foreground from physically lower level, cliff below, void, pit, upper platform, background, and foreground.

CAMERA_COMPOSITION_LOCK:
For each panel, state camera height, camera direction, subject scale, dominant screen area, and foreground/background relation.

PANEL_INHERITANCE_MAP:
P02-P09 inherit which P01 anchors, what may crop, what cannot move, and what source state changes.

AXIS_AND_SHOULDER_LOCKS:
A end, B end, camera side, forbidden side, screen left/right, shoulder side for OTS/reverse shots, foreground/background.

SPLIT_COMPOSITION_DIFFERENCE_LOCK:
Repeated source shots must differ by camera, scale, subject, spatial relation, action phase, prop state, or depth layer. Emotion-only difference fails.

PROP_TEMPORAL_PHASE_LOCK:
Each prop/effect has one physical state per panel: worn, held, inserted, cracked, falling, on ground, ash, pulse, offscreen, etc.
```

## P01 Anchor Override

If the first source shot is a close-up, reaction, over-shoulder, insert, black frame, or local prop shot:

- P01 must be rewritten as a master spatial anchor.
- Keep source shot ID for traceability.
- Add `DRAWN CAMERA TAG: master wide/full spatial anchor`.
- Source close-up/action moves to P02-P09.
- P01 must use `ANCHOR_VISIBLE_ALLOWED`, not the source shot's original single-person `VISIBLE ONLY`.
- P01 must identify allowed standing surfaces and forbidden standing zones.

## Floor, Elevation, And Forbidden Standing Zones

Every page with terrain, ledges, platforms, stairs, pits, cave voids, roads, vehicles, beds, or floors must state:

- The named floor plane or surface where feet, knees, bodies, or props can physically rest.
- Forbidden standing zones such as below cliff, inside void, beyond ledge edge, inside mist core, air column, ceiling, wall face, unreachable background.
- Whether `screen lower` means foreground framing or a physically lower elevation.
- Whether a character may cross from one plane to another in this page.

For a cliff/platform page, write: all visible human feet stay on the same upper platform unless the source explicitly shows a fall or descent; the lower void/cliff face is not a walking surface.

## Fixed Objects And Screen Projection

List fixed anchors from continuity or source: cave entrance, fissure, platform edge, floor, central void, ceiling, core, doorway, wall, furniture, road, vehicle, seat-window relation.

Each panel must inherit the anchor:

- Visible: state its screen position.
- Cropped: write `cropped/offscreen, original position unchanged`.
- Not applicable: write why it is outside the page space.

Do not replace fixed-object inheritance with a vague sentence like "same cave layout".

## Axis And Shoulder Locks

Relationship shots require concrete blocking:

- A end and B end.
- Camera allowed side and forbidden side.
- screen left/right.
- Foreground/background.
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

- Bracelet: on wrist, cracking on wrist, pulsing abstractly, detaching, falling in air, lying on ground, turning to ash, offscreen.
- Staff: held by GC, inserted into ground, glowing, dim, cracked, broken near GC, offscreen.
- Mist/core: distant mass, tendril extension, surrounding pressure, dissolving particles, offscreen.

Do not draw a hand on the ground and a fallen bracelet on the ground in the same panel unless the source explicitly shows the hand still reaching above it with clear depth separation.

## Naming Rules

Use precise black-and-white effect tokens:

- `GREY_LXJ_MIST`: pale gray mist attached to Lin Xiaojie's dissolving body.
- `DARK_HOSTILE_MIST`: dark gray hostile mist body/core/tendrils/vortex.
- `LIGHT_DUST`: pale gray particles after dissolution.
- `BRACELET_PULSE`: non-readable bracelet pulse/crack/light state.
- `WHITE_LIGHT`: pale operating-room-like light or abstract white light.

Do not use `MIST/VFX` as a catch-all. Do not write red/gold color terms in final image prompts; translate them to light/dark graphite functions.
