#!/usr/bin/env python3
"""Regression tests for su-image9 v1.7.2 validator/compiler."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).with_name("validate_su_image9_prompt.py")
CANON_PATH = Path(__file__).parents[1] / "references" / "canon-locks.md"
PYTHON = Path(sys.executable)


def shot_data(first_tag: str = "master wide full") -> dict:
    shots = []
    for index in range(1, 10):
        tag = first_tag if index == 1 else f"medium side view {index}"
        shots.append(
            {
                "shot_no": index,
                "scene": "14-1 ???? ? ?",
                "camera_main_image": f"[{tag}]\nsource camera text",
                "visible_characters": ["LX"],
                "visible_props": ["BRACELET"],
            }
        )
    return {"shots": shots, "continuity_logs": []}


def panel_plan(first_tag: str = "master wide full", drawn_first: str = "master wide/full spatial anchor", *, sparse: bool = False, human_confirmed: bool = False) -> dict:
    panels = []
    for index in range(1, 10):
        source_tag = first_tag if index == 1 else f"medium side view {index}"
        panels.append(
            {
                "panel": f"PANEL-{index}",
                "source_shot": index,
                "source_camera_tag": source_tag,
                "drawn_camera_tag": drawn_first if index == 1 else f"medium side view {index}",
                "p01_anchor_override": index == 1,
                "visible_characters": ["LX"],
                "visible_props": ["BRACELET"],
                "prop_temporal_state": "BRACELET on LX wrist",
                "axis_endpoint_a": "LX side",
                "axis_endpoint_b": "platform edge",
                "floor_plane": "upper cliff platform",
            }
        )
    page = {
        "page": "PAGE-01",
        "sparse_page": sparse,
        "fixed_anchors": ["platform edge", "fissure entrance"],
        "axis_endpoint_a": "LX side",
        "axis_endpoint_b": "platform edge",
        "floor_plane_lock": "upper cliff platform",
        "panels": panels,
    }
    if human_confirmed:
        page["anchor_decision"] = "human_confirmed"
    return {
        "skill": "su-image9",
        "version": "1.7.2",
        "reference_binding_status": "prompt_only",
        "forbidden_prompt_tokens_extra": [],
        "pages": [page],
    }


def valid_prompt(
    *,
    first_tag: str = "master wide full",
    drawn_first: str = "master wide/full spatial anchor",
    extra_continuity: str = "",
    extra_action: str = "",
    missing_drawn: bool = False,
    duplicate_triad: bool = False,
    hand_style: str | None = None,
    floor_zero: bool = False,
    visible_override: str | None = None,
    prop_override: str | None = None,
) -> str:
    style = "@CANON(STYLE_LOCK)" if hand_style is None else hand_style
    panels = []
    for index in range(1, 10):
        source_tag = first_tag if index == 1 else f"medium side view {index}"
        drawn = drawn_first if index == 1 else f"medium side view {index}"
        action = f"LX action {index} at platform edge. {extra_action}"
        floor = "unrelated empty zone" if floor_zero else f"upper cliff platform; LX side to platform edge {index}."
        prop = f"BRACELET phase {index}."
        visible = "LX and BRACELET only."
        if duplicate_triad and index in {4, 5}:
            action = "LX repeats identical blocking near the platform edge."
            floor = "upper cliff platform; axis from LX side to platform edge."
            prop = "BRACELET unchanged."
        if visible_override is not None and index == 2:
            visible = visible_override
        if prop_override is not None and index == 2:
            prop = prop_override
        drawn_line = "" if missing_drawn and index == 4 else f"DRAWN CAMERA TAG: {drawn}\n"
        panels.append(
            f"""PANEL-{index}:
SOURCE SHOT: {index}
MUST MATCH SHOT_DATA CAMERA TAG: {source_tag}
{drawn_line}VISIBLE ONLY: {visible}
ACTION / COMPOSITION: {action}
FLOOR / AXIS DELTA: {floor}
PROP STATE: {prop}
"""
        )
    return f"""# PAGE-01

STYLE_LOCK:
{style}

CANVAS_LOCK:
@CANON(CANVAS_LOCK)

REFERENCE_LOCK:
@CANON(REFERENCE_LOCK_TEXT_ONLY)

CONTINUITY_LOCK:
The upper cliff platform contains the platform edge and fissure entrance. Axis runs from LX side to platform edge. {extra_continuity}

PANEL_TASKS P01-P09:

{''.join(panels)}
NEGATIVE_LOCK:
@CANON(NEGATIVE_LOCK)
"""


class Validator171Tests(unittest.TestCase):
    def run_case(self, prompt: str, plan: dict | None = None, shots: dict | None = None, *, mode: str = "full", canon_text: str | None = None):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan_path = root / "panel_plan.json"
            prompt_path = root / "final_image_prompts.md"
            shot_path = root / "shot_data.json"
            canon_path = root / "canon-locks.md"
            report_path = root / "validation_report.json"
            out_path = root / "final_image_prompts.compiled.md"
            plan_path.write_text(json.dumps(plan or panel_plan(), ensure_ascii=False, indent=2), encoding="utf-8")
            prompt_path.write_text(prompt, encoding="utf-8")
            if shots is not None:
                shot_path.write_text(json.dumps(shots, ensure_ascii=False, indent=2), encoding="utf-8")
            canon_path.write_text(canon_text if canon_text is not None else CANON_PATH.read_text(encoding="utf-8"), encoding="utf-8")
            cmd = [str(PYTHON), str(SCRIPT_PATH), "--mode", mode, "--canon", str(canon_path), "--panel-plan", str(plan_path), "--final-prompts", str(prompt_path), "--report", str(report_path), "--out", str(out_path)]
            if mode == "full":
                shot_path.write_text(json.dumps(shots or shot_data(), ensure_ascii=False, indent=2), encoding="utf-8")
                cmd.extend(["--shot-data", str(shot_path)])
            result = subprocess.run(cmd, text=True, capture_output=True)
            report = json.loads(report_path.read_text(encoding="utf-8"))
            compiled = out_path.read_text(encoding="utf-8") if out_path.exists() else ""
            return result.returncode, report, compiled

    def checks(self, report: dict) -> set[str]:
        found = set()
        for page in report.get("pages", []):
            for finding in page.get("findings", []):
                found.add(finding["check"])
        return found

    def test_t01_4700_codepoints_warn(self) -> None:
        filler = " neutral blocking beat" * 18
        code, report, _ = self.run_case(valid_prompt(extra_continuity=filler), plan=panel_plan(), shots=shot_data())
        self.assertEqual(code, 1, report)
        self.assertIn("G0-04", self.checks(report))

    def test_t02_extra_cannot_clear_red(self) -> None:
        plan = panel_plan()
        plan["forbidden_prompt_tokens_extra"] = []
        code, report, _ = self.run_case(valid_prompt(extra_action="red pulse"), plan=plan, shots=shot_data())
        self.assertEqual(code, 2, report)
        self.assertIn("G0-07", self.checks(report))

    def test_t03_centered_composition_not_red_false_positive(self) -> None:
        code, report, _ = self.run_case(valid_prompt(extra_action="centered composition"), plan=panel_plan(), shots=shot_data())
        self.assertNotIn("G0-07", self.checks(report))

    def test_t04_crimson_glow_fails(self) -> None:
        code, report, _ = self.run_case(valid_prompt(extra_action="crimson glow"), plan=panel_plan(), shots=shot_data())
        self.assertEqual(code, 2, report)
        self.assertIn("G0-07", self.checks(report))

    def test_t05_non_readable_pulse_allowed(self) -> None:
        code, report, _ = self.run_case(valid_prompt(extra_action="non-readable pulse"), plan=panel_plan(), shots=shot_data())
        self.assertNotIn("G0-06", self.checks(report))

    def test_t06_text_only_runs_g0_without_shot_data(self) -> None:
        code, report, _ = self.run_case(valid_prompt(), plan=panel_plan(), shots=None, mode="text-only")
        self.assertIn(code, {0, 1}, report)
        self.assertTrue(report["batch_id"].startswith("T-"))

    def test_t07_closeup_without_override_fails(self) -> None:
        plan = panel_plan(first_tag="close-up", drawn_first="close-up")
        code, report, _ = self.run_case(valid_prompt(first_tag="close-up", drawn_first="close-up"), plan=plan, shots=shot_data(first_tag="close-up"))
        self.assertEqual(code, 2, report)
        self.assertIn("G1-11", self.checks(report))

    def test_t08_missing_drawn_camera_tag_fails(self) -> None:
        code, report, _ = self.run_case(valid_prompt(missing_drawn=True), plan=panel_plan(), shots=shot_data())
        self.assertEqual(code, 2, report)
        self.assertIn("G0-12", self.checks(report))

    def test_t09_handwritten_canon_autofixed(self) -> None:
        bad_style = "STYLE_LOCK:\nUnified black-and-white director blocking sketch"
        code, report, compiled = self.run_case(valid_prompt(hand_style=bad_style), plan=panel_plan(), shots=shot_data())
        self.assertIn(code, {1, 2}, report)
        self.assertTrue(report["pages"][0]["canon_autofixed"])
        self.assertIn("Prioritize composition", compiled)

    def test_t10_zero_entity_intersection_fails(self) -> None:
        code, report, _ = self.run_case(valid_prompt(floor_zero=True), plan=panel_plan(), shots=shot_data())
        self.assertEqual(code, 2, report)
        self.assertIn("G0-10", self.checks(report))

    def test_t11_canon_marker_expands(self) -> None:
        code, report, compiled = self.run_case(valid_prompt(), plan=panel_plan(), shots=shot_data())
        self.assertIn("Unified black-and-white director blocking sketch", compiled)
        self.assertNotIn("@CANON(STYLE_LOCK)", compiled)

    def test_t12_duplicate_content_triad_fails_without_template_false_positive(self) -> None:
        code, report, _ = self.run_case(valid_prompt(duplicate_triad=True), plan=panel_plan(), shots=shot_data())
        self.assertEqual(code, 2, report)
        self.assertIn("G0-05", self.checks(report))

    def test_t13_text_only_batch_id_prefix(self) -> None:
        code, report, _ = self.run_case(valid_prompt(), plan=panel_plan(), shots=None, mode="text-only")
        self.assertTrue(report["batch_id"].startswith("T-"), report)

    def test_t14_tampered_canon_same_version_fails(self) -> None:
        tampered = CANON_PATH.read_text(encoding="utf-8").replace("Not a polished illustration", "Not a polished image")
        code, report, _ = self.run_case(valid_prompt(), plan=panel_plan(), shots=shot_data(), canon_text=tampered)
        self.assertEqual(code, 2, report)
        self.assertEqual(report["canon_snapshot_status"], "TAMPERED")
        self.assertIn("G0-00", self.checks(report))

    def test_t15_wide_closeup_uncertain_requires_human_confirmation(self) -> None:
        plan = panel_plan(first_tag="wide close-up", drawn_first="master wide/full spatial anchor")
        code, report, _ = self.run_case(valid_prompt(first_tag="wide close-up"), plan=plan, shots=shot_data(first_tag="wide close-up"))
        self.assertEqual(code, 2, report)
        self.assertIn("G1-11", self.checks(report))

    def test_t16_props_yes_fails(self) -> None:
        code, report, _ = self.run_case(valid_prompt(visible_override="chars=LX; props=yes."), plan=panel_plan(), shots=shot_data())
        self.assertEqual(code, 2, report)
        self.assertIn("G0-14", self.checks(report))

    def test_t17_bare_owned_prop_state_fails(self) -> None:
        code, report, _ = self.run_case(valid_prompt(prop_override="owned; non-readable; p2."), plan=panel_plan(), shots=shot_data())
        self.assertEqual(code, 2, report)
        self.assertIn("G0-14", self.checks(report))

    def test_t18_vfx_visible_prop_fails(self) -> None:
        code, report, _ = self.run_case(valid_prompt(visible_override="chars=LX; props=灰白色雾气."), plan=panel_plan(), shots=shot_data())
        self.assertEqual(code, 2, report)
        self.assertIn("G0-14", self.checks(report))


if __name__ == "__main__":
    unittest.main()
