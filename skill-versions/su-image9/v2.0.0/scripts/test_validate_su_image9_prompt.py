#!/usr/bin/env python3
"""Regression tests for su-image9 v2.0.0 validator/compiler."""

from __future__ import annotations

import json
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
                "camera_main_image": f"[{tag}]\nsource camera text",
                "visible_characters": ["LX"],
                "visible_props": ["BRACELET"],
            }
        )
    return {"shots": shots, "continuity_logs": []}


def panel_plan(
    first_tag: str = "master wide full",
    drawn_first: str = "master wide/full spatial anchor",
    *,
    human_confirmed: bool = False,
    prop_override: str | None = None,
) -> dict:
    panels = []
    for index in range(1, 10):
        source_tag = first_tag if index == 1 else f"medium side view {index}"
        panels.append(
            {
                "panel": f"PANEL-{index}",
                "source_shot": index,
                "shot_data_camera_tag": source_tag,
                "drawn_camera_tag": drawn_first if index == 1 else f"medium side view {index}",
                "visible_only": "LX and BRACELET only",
                "action_composition": f"LX advances through a distinct storyboard beat {index}",
                "floor_axis_delta": f"upper cliff platform remains the floor; axis stays from LX to platform edge {index}",
                "prop_state": prop_override if prop_override is not None and index == 2 else f"BRACELET remains on LX wrist phase {index}",
            }
        )
    page = {
        "page": "PAGE-01",
        "sparse_page": False,
        "panels": panels,
    }
    if human_confirmed:
        page["anchor_decision"] = "human_confirmed"
    return {
        "skill": "su-image9",
        "version": "2.0.0",
        "canon_version": "2.0.0",
        "reference_binding_status": "prompt_only",
        "forbidden_prompt_tokens_extra": [],
        "pages": [page],
    }


def panel_sentence(index: int, extra: str = "") -> str:
    return (
        f"PANEL-{index}: Medium storyboard view of LX on the same upper cliff platform established in Panel 1; "
        f"the camera observes a distinct action phase {index} while the bracelet stays visible on LX wrist; "
        f"the platform edge remains in the same background zone and no new room or object is introduced. {extra}"
    )


def valid_prompt(*, extra_scene: str = "", extra_panel: str = "", missing_layer: str | None = None) -> str:
    layers = {
        "DELIVERABLE": "@CANON(HARD_PHRASES)\n@CANON(GEOMETRY_BLUEPRINT)",
        "SYSTEM_STYLE_LAYER": "@CANON(SYSTEM_STYLE_LAYER)",
        "SCENE_LAYER": f"The page takes place on one upper cliff platform with a fixed platform edge, fissure entrance, and empty background. {extra_scene}",
        "CAMERA_RULE_LAYER": "Camera stays on the same side of the LX to platform edge axis; screen left and screen right remain locked across reverse views.",
        "CONTINUITY_LAYER": "All panels inherit the upper cliff platform, the fixed platform edge, the fissure entrance, and LX wrist bracelet state.",
        "TEXT_DERIVED_LAYOUT": "No reference image is bound; all layout facts are derived from text and panel_plan.json.",
        "PANEL_1_MASTER_SPATIAL_LAYOUT_ANCHOR": "Panel 1 establishes the whole platform, LX start position, platform edge, fissure entrance, and empty space for later crop-ins.",
        "DOOR_WINDOW_FURNITURE_GEOMETRY_LOCK": "This exterior page has no doors, windows, or furniture; fixed terrain geometry remains the platform and fissure entrance.",
        "VEHICLE_AND_AXIS_LOCKS": "No vehicle appears on this page; the relationship axis stays between LX and the platform edge.",
        "OBJECT_VISIBILITY_AND_BOUNDARIES": "Only LX and the bracelet appear; offscreen objects must remain offscreen and cannot appear as shadows or silhouettes.",
        "PANEL_LAYER PANEL-1 to PANEL-9": "\n".join(panel_sentence(index, extra_panel if index == 3 else "") for index in range(1, 10)),
        "NEGATIVE_CONSTRAINTS": "@CANON(NEGATIVE_CONSTRAINTS)",
    }
    if missing_layer:
        layers.pop(missing_layer)
    rendered = ["# PAGE-01"]
    for key, value in layers.items():
        rendered.append(f"{key}:\n{value}")
    return "\n\n".join(rendered) + "\n"


class Validator200Tests(unittest.TestCase):
    def run_case(
        self,
        prompt: str,
        plan: dict | None = None,
        shots: dict | None = None,
        *,
        mode: str = "full",
        canon_text: str | None = None,
    ):
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
            canon_path.write_text(canon_text if canon_text is not None else CANON_PATH.read_text(encoding="utf-8"), encoding="utf-8")
            cmd = [
                str(PYTHON),
                str(SCRIPT_PATH),
                "--mode",
                mode,
                "--canon",
                str(canon_path),
                "--panel-plan",
                str(plan_path),
                "--final-prompts",
                str(prompt_path),
                "--report",
                str(report_path),
                "--out",
                str(out_path),
            ]
            if mode == "full":
                shot_path.write_text(json.dumps(shots or shot_data(), ensure_ascii=False, indent=2), encoding="utf-8")
                cmd.extend(["--shot-data", str(shot_path)])
            result = subprocess.run(cmd, text=True, capture_output=True)
            report = json.loads(report_path.read_text(encoding="utf-8"))
            compiled = out_path.read_text(encoding="utf-8") if out_path.exists() else ""
            return result.returncode, report, compiled, result

    def checks(self, report: dict) -> set[str]:
        found = set()
        for page in report.get("pages", []):
            for finding in page.get("findings", []):
                found.add(finding["check"])
        return found

    def test_valid_v2_prompt_passes_and_expands_canon(self) -> None:
        code, report, compiled, _ = self.run_case(valid_prompt())
        self.assertEqual(code, 0, report)
        self.assertIn("This entire generation must follow a single unified storyboard production style.", compiled)
        self.assertIn("Strict panel geometry blueprint, mandatory before drawing:", compiled)
        self.assertNotIn("@CANON(", compiled)

    def test_unknown_canon_marker_leak_fails(self) -> None:
        code, report, compiled, _ = self.run_case(valid_prompt(extra_scene="@CANON(UNEXPANDED)"))
        self.assertEqual(code, 2, report)
        self.assertIn("G0-03", self.checks(report))
        self.assertIn("@CANON(UNEXPANDED)", compiled)

    def test_missing_required_layer_fails(self) -> None:
        code, report, _, _ = self.run_case(valid_prompt(missing_layer="CAMERA_RULE_LAYER"))
        self.assertEqual(code, 2, report)
        self.assertIn("G0-01", self.checks(report))

    def test_panel_layer_field_skeleton_fails(self) -> None:
        code, report, _, _ = self.run_case(valid_prompt(extra_panel="SOURCE SHOT: 3"))
        self.assertEqual(code, 2, report)
        self.assertIn("G0-07", self.checks(report))

    def test_budget_upper_bound_warns_without_fail(self) -> None:
        filler = " neutral storyboard continuity phrase" * 360
        code, report, _, _ = self.run_case(valid_prompt(extra_scene=filler))
        self.assertEqual(code, 1, report)
        self.assertEqual(report["summary"]["fail"], 0, report)
        self.assertIn("G0-05", self.checks(report))

    def test_old_panel_tasks_structure_fails(self) -> None:
        old_prompt = """# PAGE-01

STYLE_LOCK:
@CANON(STYLE_LOCK)

PANEL_TASKS PANEL-1 to PANEL-9:
PANEL-1:
SOURCE SHOT: 1

NEGATIVE_LOCK:
@CANON(NEGATIVE_LOCK)
"""
        code, report, _, _ = self.run_case(old_prompt, mode="text-only")
        self.assertEqual(code, 2, report)
        self.assertIn("G0-10", self.checks(report))

    def test_boolean_props_in_plan_fails(self) -> None:
        code, report, _, _ = self.run_case(valid_prompt(), plan=panel_plan(prop_override="props=yes"))
        self.assertEqual(code, 2, report)
        self.assertIn("G0-09", self.checks(report))

    def test_forbidden_style_term_in_panel_fails(self) -> None:
        code, report, _, _ = self.run_case(valid_prompt(extra_panel="Use cinematic lighting on LX face."))
        self.assertEqual(code, 2, report)
        self.assertIn("G0-08", self.checks(report))

    def test_text_only_keeps_t_batch_prefix(self) -> None:
        code, report, _, _ = self.run_case(valid_prompt(), mode="text-only")
        self.assertEqual(code, 0, report)
        self.assertTrue(report["batch_id"].startswith("T-"), report)

    def test_uncertain_anchor_requires_human_confirmation(self) -> None:
        plan = panel_plan(first_tag="wide close-up", drawn_first="master wide/full spatial anchor")
        code, report, _, _ = self.run_case(valid_prompt(), plan=plan, shots=shot_data(first_tag="wide close-up"))
        self.assertEqual(code, 2, report)
        self.assertIn("G1-11", self.checks(report))


if __name__ == "__main__":
    unittest.main()
