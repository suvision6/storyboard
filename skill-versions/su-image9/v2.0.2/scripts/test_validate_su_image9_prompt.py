#!/usr/bin/env python3
"""Regression tests for su-image9 v2.0.2 validator/compiler."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).with_name("validate_su_image9_prompt.py")
DERIVE_PATH = Path(__file__).with_name("derive_su_image9_prompt_package.py")
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


def distance_shot_data() -> dict:
    data = shot_data()
    data["shots"][1]["camera_main_image"] = "[medium side view 2]\nLX walks forward and stops two steps away from the other character."
    data["shots"][1]["source_paragraph"] = "LX walks forward and stops two steps away from the other character."
    data["shots"][1]["prompt"] = "画面内容：LX walks forward and stops two steps away from the other character."
    return data


def panel_plan(
    first_tag: str = "master wide full",
    drawn_first: str = "master wide/full spatial anchor",
    *,
    human_confirmed: bool = False,
    prop_override: str | None = None,
    distance_lock: str = "none",
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
                "distance_stage_lock": distance_lock,
            }
        )
    page = {
        "page": "PAGE-01",
        "sparse_page": False,
        "source_shot_range": "1-9",
        "sequence_order_policy": "strict_source_order_no_anchor_reorder",
        "page_split_policy": "scene_layer_aware_strict_source_order",
        "panels": panels,
    }
    if human_confirmed:
        page["anchor_decision"] = "human_confirmed"
    return {
        "skill": "su-image9",
        "version": "2.0.2",
        "canon_version": "2.0.2",
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


class Validator201Tests(unittest.TestCase):
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

    def test_reordered_panel_one_source_fails(self) -> None:
        plan = panel_plan()
        plan["pages"][0]["panels"][0]["source_shot"] = 3
        plan["pages"][0]["panels"][0]["shot_data_camera_tag"] = "medium side view 3"
        plan["pages"][0]["panels"][1]["source_shot"] = 1
        plan["pages"][0]["panels"][1]["shot_data_camera_tag"] = "master wide full"
        code, report, _, _ = self.run_case(valid_prompt(), plan=plan)
        self.assertEqual(code, 2, report)
        self.assertIn("G1-12", self.checks(report))

    def test_distance_stage_lock_required_before_later_endpoint(self) -> None:
        code, report, _, _ = self.run_case(valid_prompt(), shots=distance_shot_data())
        self.assertEqual(code, 2, report)
        self.assertIn("G1-13", self.checks(report))

    def test_distance_stage_lock_allows_later_endpoint(self) -> None:
        plan = panel_plan()
        plan["pages"][0]["panels"][0]["distance_stage_lock"] = "pre-approach: keeps distance with visible empty floor before the two-step stop in Panel 2"
        prompt = valid_prompt(extra_panel="") .replace(
            "the camera observes a distinct action phase 1 while the bracelet stays visible on LX wrist;",
            "the camera observes a distinct action phase 1 while LX is not yet close and visible empty floor remains before the two-step stop;",
        )
        code, report, _, _ = self.run_case(prompt, plan=plan, shots=distance_shot_data())
        self.assertEqual(code, 0, report)

    def test_bad_layer_cannot_open_page(self) -> None:
        plan = panel_plan(first_tag="master wide full")
        shots = shot_data(first_tag="master wide full")
        shots["shots"][0]["shot_type"] = "transition"
        shots["shots"][0]["camera_main_image"] = "[master wide full]\n画面进入短暂记忆层，年幼角色出现。"
        code, report, _, _ = self.run_case(valid_prompt(), plan=plan, shots=shots)
        self.assertEqual(code, 2, report)
        self.assertIn("G1-14", self.checks(report))

    def test_cross_scene_bridge_requires_policy(self) -> None:
        plan = panel_plan()
        shots = shot_data()
        for shot in shots["shots"][:5]:
            shot["scene_id"] = "S01"
            shot["scene"] = "14-2 地下空腔 日 内"
        for shot in shots["shots"][5:]:
            shot["scene_id"] = "S02"
            shot["scene"] = "14-3 地下空腔 日 内"
        code, report, _, _ = self.run_case(valid_prompt(), plan=plan, shots=shots)
        self.assertEqual(code, 2, report)
        self.assertIn("G1-14", self.checks(report))
        plan["pages"][0]["page_split_policy"] = "scene_layer_aware_strict_source_order+intentional_cross_scene_bridge"
        code, report, _, _ = self.run_case(valid_prompt(), plan=plan, shots=shots)
        self.assertEqual(code, 0, report)

    def test_derive_script_preserves_source_order(self) -> None:
        data = shot_data()
        for index in range(10, 19):
            data["shots"].append(
                {
                    "shot_no": index,
                    "scene_id": "S02",
                    "scene": "test scene two",
                    "camera_main_image": f"[master wide full {index}]\nsource camera text",
                    "source_paragraph": f"source beat {index}",
                    "prompt": f"画面内容：source beat {index}",
                    "visible_characters": ["LX"],
                    "visible_props": [],
                }
            )
        for shot in data["shots"]:
            shot.setdefault("scene_id", "S01")
            shot.setdefault("scene", "test scene one")
            shot.setdefault("source_paragraph", f"source beat {shot['shot_no']}")
            shot.setdefault("prompt", f"画面内容：source beat {shot['shot_no']}")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shot_path = root / "shot_data.json"
            out_dir = root / "package"
            shot_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            result = subprocess.run(
                [
                    str(PYTHON),
                    str(DERIVE_PATH),
                    "--shot-data",
                    str(shot_path),
                    "--out-dir",
                    str(out_dir),
                    "--canon",
                    str(CANON_PATH),
                    "--validator",
                    str(SCRIPT_PATH),
                ],
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            plan = json.loads((out_dir / "panel_plan.json").read_text(encoding="utf-8"))
            self.assertEqual(plan["pages"][0]["panels"][0]["source_shot"], 1)
            self.assertEqual(plan["pages"][1]["panels"][0]["source_shot"], 10)

    def test_derive_script_uses_scene_layer_aware_pagination(self) -> None:
        shots = []
        for index in range(1, 59):
            scene_id = "S01"
            scene = "14-1 地下通道 日 内"
            shot_type = "dialogue"
            camera = "[平视, 中景, 固定镜头]\nsource camera text"
            if index == 1:
                shot_type = "master"
                camera = "[微俯视, 全景, 固定镜头]\nsource camera text"
            if index == 9:
                shot_type = "insert"
                camera = "[微俯视, 特写, 固定镜头]\n当前场景手部接触。"
            if index == 10:
                shot_type = "transition"
                camera = "[平视, 中景, 固定镜头]\n画面进入短暂记忆层，年幼林晓杰出现。"
            if index >= 17:
                scene_id = "S02"
                scene = "14-2 地下空腔 日 内"
            if index >= 23:
                scene_id = "S03"
                scene = "14-3 地下空腔 日 内"
            if index == 17 or index == 23:
                shot_type = "master"
                camera = "[微俯视, 全景, 固定镜头]\n同一地下空腔当前层空间建立。"
            if index >= 51:
                scene_id = "S04"
                scene = "14-4 同 地下空腔 日 内"
            if index == 51:
                shot_type = "master"
                camera = "[平视, 中景, 固定镜头]\n周围动作全部变慢，沈夜消失，林晓彤独自站在空腔中央，倒计时开始。"
            shots.append(
                {
                    "shot_no": index,
                    "scene_id": scene_id,
                    "scene": scene,
                    "shot_type": shot_type,
                    "camera_main_image": camera,
                    "source_paragraph": f"source beat {index}",
                    "prompt": f"画面内容：source beat {index}",
                    "visible_characters": ["LX"],
                    "visible_props": [],
                }
            )
        data = {"shots": shots, "continuity_logs": []}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shot_path = root / "shot_data.json"
            out_dir = root / "package"
            shot_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            result = subprocess.run(
                [
                    str(PYTHON),
                    str(DERIVE_PATH),
                    "--shot-data",
                    str(shot_path),
                    "--out-dir",
                    str(out_dir),
                    "--canon",
                    str(CANON_PATH),
                    "--validator",
                    str(SCRIPT_PATH),
                ],
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            plan = json.loads((out_dir / "panel_plan.json").read_text(encoding="utf-8"))
            ranges = [page["source_shot_range"] for page in plan["pages"]]
            self.assertEqual(ranges, ["1-8", "9-16", "17-25", "26-34", "35-43", "44-50", "51-58"])
            page_map = json.loads((out_dir / "page-map.json").read_text(encoding="utf-8"))
            self.assertEqual(page_map["pages"][1]["panels"][0]["shot_nos"], [9])
            self.assertEqual(page_map["pages"][5]["source_shot_range"], "44-50")


if __name__ == "__main__":
    unittest.main()
