#!/usr/bin/env python3
"""Focused regression tests for the su-image9 1.6.1 validator."""

from __future__ import annotations

import unittest

from validate_su_image9_prompt import validate


STYLE = (
    "Unified black-and-white director blocking sketch. Same clean pencil line width, "
    "same light gray density, low-detail faces, simple costume silhouettes, sparse structural environment. "
    "Not a polished illustration, not manga, not photoreal."
)

NEGATIVE = (
    "No text, labels, captions, panel numbers, shot numbers, subtitles, arrows, UI, monitor graphics, "
    "logos, watermarks, Chinese or English writing. No photorealism, realistic skin, portrait rendering, "
    "cinematic lighting, color, CGI, 3D render, painting, polished illustration, manga/comic layout, "
    "collage, poster, heavy texture, dense environment rendering, mixed panel sizes."
)


def shot_data() -> dict:
    shots = []
    for index in range(1, 10):
        camera = "平视, 特写, 固定镜头" if index == 1 else "侧面平视, 中景, 固定镜头"
        shots.append(
            {
                "shot_no": index,
                "scene": "14-1 地下岩台 日 内",
                "camera_main_image": f"[{camera}]\n【机位逻辑】source camera.",
                "visible_characters": ["林晓彤"] if index != 1 else ["林晓杰"],
                "visible_props": ["手环"] if index != 1 else [],
            }
        )
    return {"shots": shots, "continuity_logs": []}


def panel_plan(prompt_only: bool = False, anchor_single_only: bool = False) -> dict:
    panels = []
    for index in range(1, 10):
        panel_id = f"P{index:02d}"
        is_anchor = index == 1
        panels.append(
            {
                "panel": panel_id,
                "source_shot": index,
                "source_camera_tag": "平视, 特写, 固定镜头" if index == 1 else "侧面平视, 中景, 固定镜头",
                "drawn_camera_tag": "master wide/full spatial anchor" if is_anchor else "侧面平视, 中景, 固定镜头",
                "p01_anchor_override": is_anchor,
                "anchor_visible_allowed": {
                    "characters": ["LXJ"] if anchor_single_only else ["LX", "LXJ"],
                    "props": [] if anchor_single_only else ["BRACELET"],
                },
                "visible_characters": ["LXJ"] if index == 1 else ["LX"],
                "visible_props": [] if index == 1 else ["BRACELET"],
                "action_composition": "specific drawable action",
                "floor_axis_delta": "specific concrete floor and axis",
                "prop_temporal_state": "none" if index == 1 else "BRACELET worn on LX wrist",
                "screen_left_right_lock": "screen left=LX; screen right=LXJ",
                "axis_endpoint_a": "LX side",
                "axis_endpoint_b": "LXJ side",
                "floor_plane": "upper cliff platform",
                "forbidden_standing_zone": "lower void",
            }
        )
    return {
        "skill": "su-image9",
        "version": "1.6.1",
        "reference_binding_status": "prompt_only" if prompt_only else "bound",
        "forbidden_prompt_tokens": ["page A/B", "as applicable", "allowed positions"],
        "pages": [
            {
                "page": "P01",
                "title": "test page",
                "shots": list(range(1, 10)),
                "space": "14-1 地下岩台 日 内",
                "fixed_anchors": ["fissure entrance", "platform edge"],
                "floor_plane_lock": "upper cliff platform",
                "forbidden_standing_zones": ["lower void"],
                "axis_endpoint_a": "LX side",
                "axis_endpoint_b": "LXJ side",
                "camera_side": "LX side",
                "screen_left_right_lock": "screen left=LX; screen right=LXJ",
                "panels": panels,
            }
        ],
    }


def valid_prompt(extra: str = "", camera_override: str | None = None, generic_axis: bool = False, anchor_single_only: bool = False) -> str:
    panel_blocks = []
    for index in range(1, 10):
        panel_id = f"P{index:02d}"
        source_camera = "平视, 特写, 固定镜头" if index == 1 else "侧面平视, 中景, 固定镜头"
        if camera_override and index == 2:
            source_camera = camera_override
        drawn = "\nDRAWN CAMERA TAG: master wide/full spatial anchor" if index == 1 else ""
        visible = "chars=LXJ; props=none." if anchor_single_only and index == 1 else (
            "chars=LX,LXJ; props=BRACELET." if index == 1 else "chars=LX; props=BRACELET."
        )
        action = (
            "floor upper cliff platform, visible fissure entrance, platform edge, forbidden lower void, "
            "start positions for LX and LXJ, sparse blocking composition with simple silhouettes and clear spacing. "
            "The drawing uses structural background only and enough empty space to maintain one clean storyboard sketch style."
            if index == 1
            else "LX performs a clear source action on the upper cliff platform with readable blocking, simple silhouette, inherited platform edge, and a distinct camera crop from the master anchor."
        )
        axis = (
            "page A/B; foreground/background/shoulder locked."
            if generic_axis
            else "floor=upper cliff platform; A=LX side; B=LXJ side; camera side=LX side; screen left=LX; screen right=LXJ; foreground=LX side rock; background=LXJ edge."
        )
        prop_state = "none" if anchor_single_only and index == 1 else "BRACELET worn on LX wrist"
        panel_blocks.append(
            f"""{panel_id}:
SOURCE SHOT: {index}
MUST MATCH SHOT_DATA CAMERA TAG: {source_camera}{drawn}
VISIBLE ONLY: {visible}
ACTION / COMPOSITION: {action}
FLOOR / AXIS DELTA: {axis}
PROP STATE: {prop_state}
"""
        )
    return f"""# P01 test page

STYLE_LOCK:
{STYLE}

CANVAS_LOCK:
One wide horizontal 16:9 canvas. Exact clean 3x3 storyboard grid, nine equal horizontal 16:9 panels, straight borders and gutters. No text or labels inside the image. P01 establishes the master space; P02-P09 inherit it unless a source shot changes state.

REFERENCE_LOCK:
Reference images only lock identity silhouette, hairstyle silhouette, costume silhouette, prop shape, and prop ownership. Do not copy photo texture, skin detail, lighting, color, refinement level, or face matching.

CONTINUITY_LOCK:
Space=14-1 cliff platform. Fixed anchors=fissure entrance, platform edge. Floor=upper cliff platform. Forbidden=lower void. Axis A=LX side, B=LXJ side, camera side=LX side, screen left=LX, screen right=LXJ. Props=BRACELET only LX.

PANEL_TASKS P01-P09:

{chr(10).join(panel_blocks)}
NEGATIVE_LOCK:
{NEGATIVE}
{extra}
"""


class ValidatorRegressionTests(unittest.TestCase):
    def assert_has_issue(self, result: dict, code: str) -> None:
        codes = {issue["code"] for issue in result["issues"]}
        self.assertIn(code, codes, result)

    def test_rejects_camera_tag_mismatch(self) -> None:
        result = validate(shot_data(), panel_plan(), valid_prompt(camera_override="错误机位, 特写, 固定镜头"))
        self.assert_has_issue(result, "prompt_camera_tag_mismatch_panel_plan")

    def test_rejects_p01_anchor_with_single_closeup_visibility(self) -> None:
        result = validate(shot_data(), panel_plan(anchor_single_only=False), valid_prompt(anchor_single_only=True))
        self.assert_has_issue(result, "p01_anchor_visible_only_not_anchor_allowed")

    def test_rejects_placeholder_axis_text(self) -> None:
        result = validate(shot_data(), panel_plan(), valid_prompt(generic_axis=True))
        self.assert_has_issue(result, "placeholder_prompt_text")
        self.assert_has_issue(result, "axis_lock_not_concrete")

    def test_rejects_formal_reference_generation_without_bound_refs(self) -> None:
        manifest = {
            "generation_mode": "formal_reference_image",
            "reference_binding_status": "prompt_only",
            "images": [{"page": "P01", "prompt_used_verbatim": True, "style_consistency_passed": True}],
        }
        result = validate(shot_data(), panel_plan(prompt_only=True), valid_prompt(), manifest)
        self.assert_has_issue(result, "formal_reference_generation_without_bound_refs")

    def test_rejects_countdown_and_monitor_tokens(self) -> None:
        result = validate(shot_data(), panel_plan(), valid_prompt(extra="abstract countdown pulse 数字4 bpm HR ECG"))
        self.assert_has_issue(result, "countdown_or_ui_token_in_final_prompt")


if __name__ == "__main__":
    unittest.main()
