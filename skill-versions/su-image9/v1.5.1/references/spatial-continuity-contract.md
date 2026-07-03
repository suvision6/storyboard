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

`continuity_logs` are not optional summaries. They are the main source for fixed objects, scene axes, starting positions, facing directions, reality layers, and prop states.

## Final Prompt Mandatory Layers

`final_image_prompts.md` must keep these compact layers per page:

```text
CONTINUITY_LAYER:
Scene continuity from shot_data continuity_logs / continuity_updates. Include fixed objects, character starting positions, facing, prop states, reality layer, and inherited/diverged states.

PANEL_1_MASTER_SPATIAL_LAYOUT_ANCHOR:
P01 drawn layout, fixed anchors, allowed hidden objects, character/object start positions, and what Panels 2-9 inherit.

FIXED_OBJECT_SCREEN_PROJECTION:
For each fixed object, state screen position or "cropped/offscreen but unchanged"; never move it to a new side.

PANEL_INHERITANCE_MAP:
P02-P09 inherit which P01 anchors, what may be cropped, what cannot be redrawn, and what source state changes.

AXIS_AND_SHOULDER_LOCKS:
A end, B end, camera side, forbidden side, screen left/right, shoulder side for OTS/reverse shots, foreground/background.

PANEL_DIFFERENCE_TASKS:
One unique visual task for each panel. Split panels must show distinct action phase, state, reaction, object change, or result.
```

## P01 Anchor Override

If the first source shot is a close-up, reaction, over-shoulder, insert, black frame, or local prop shot:

- P01 must be rewritten as a master spatial anchor.
- Keep source shot ID for traceability.
- Add `DRAWN CAMERA TAG: master wide/full spatial anchor`.
- Source close-up/action moves to P02-P09.
- P01 must use `ANCHOR_VISIBLE_ALLOWED`, not the source shot's original single-person `VISIBLE ONLY`.

Failure examples:

- P01 content establishes LX and LXJ, but `VISIBLE ONLY` permits only LXJ.
- P01 says master cave layout but has the source close-up camera as the only drawn camera.
- P01 introduces a character/prop not yet revealed by the page range.

## Fixed Objects And Screen Projection

For every page, list fixed anchors from continuity or source:

- cave entrance / fissure / platform edge
- room walls / doors / windows / furniture
- road / vehicle / seat-window relation
- cave floor / central void / ceiling / mist core position

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

- establishing position
- action start
- contact / impact / crossing
- reaction
- prop state change
- VFX phase
- result / aftermath

Do not repeat the same source shot with the same content text. If distinct visual tasks cannot fill 9 panels, change the page range instead of hard-filling.

## Naming Rules

Use precise effect tokens:

- `GREY_LXJ_MIST`: grey-white mist attached to Lin Xiaojie's dissolving body.
- `GOLD_BLACK_MIST`: hostile gold-black mist body/core/tendrils/bats/vortex.
- `LIGHT_DUST`: grey-white or red light particles after dissolution.
- `BRACELET_PULSE`: non-readable bracelet pulse/crack/light state.
- `WHITE_LIGHT`: operating-room-like white light or abstract white light.

Do not use `MIST/VFX` as a catch-all. It causes grey character mist and hostile mist core to collide with `MUST NOT SHOW`.

## Prop Ownership Without Prop Invitation

Prop ownership is not permission to draw the prop in every panel.

- If `visible_props` includes `STAFF`, write `STAFF visible with/near GC only`.
- If GC is visible but `STAFF` is not visible, write `no STAFF visible in this panel`.
- If `visible_props` includes `BRACELET`, write `BRACELET on LX/fallen from LX only`.
- If LX is visible but bracelet is not a visual focus, keep bracelet as costume continuity but do not invite readable UI or countdown.
