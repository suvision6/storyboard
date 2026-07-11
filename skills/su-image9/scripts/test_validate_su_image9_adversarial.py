#!/usr/bin/env python3
"""Adversarial regression tests for the su-image9 v2.0.3 validator."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import derive_su_image9_prompt_package as derive
from test_validate_su_image9_prompt import shot_data

SCRIPT_PATH = Path(__file__).with_name("validate_su_image9_prompt.py")
CANON_PATH = Path(__file__).parents[1] / "references" / "canon-locks.md"


def strict_fixture() -> tuple[dict, dict]:
    shots = shot_data()
    shots.update(
        {
            "metadata": {"skill_name": "su-fenjingskill-zh", "version": "2.4.2"},
            "script_lock": {"status": "locked"},
            "validation_report": {"status": "PASS"},
        }
    )
    shots["continuity_logs"] = [
        {
            "scene_id": "S01",
            "scene": "1 山崖平台 日 外",
            "reality_layer": "现实",
            "spatial_axis": "LX位于画面左侧，平台边缘位于画面右侧",
            "fixed_objects": [{"name": "平台边缘", "position": "画面右侧", "state": "固定"}],
            "characters": [{"name": "LX", "position": "画面左侧", "facing": "向右", "state": "正常"}],
        }
    ]
    for index, shot in enumerate(shots["shots"], 1):
        shot.update(
            {
                "scene_id": "S01",
                "scene": "1 山崖平台 日 外",
                "source_paragraph": f"LX advances through storyboard action {index}",
                "prompt": (
                    f"画面内容：LX advances through storyboard action {index}\n"
                    f"构图：LX remains on the upper cliff platform phase {index}\n"
                    "运镜手法：fixed camera"
                ),
                "beat_ids": [f"B{index:03d}"],
                "covered_fact_ids": [f"B{index:03d}-F01"],
                "offscreen_characters": [],
                "continuity_updates": [],
            }
        )
    logs = derive.scene_logs(shots)
    plan = derive.build_panel_plan(shots, derive.page_chunks(shots["shots"], 9, logs))
    plan["release_ready"] = True
    plan["review_required_reasons"] = []
    return plan, shots


def render_prompt(shots: dict) -> str:
    logs = derive.scene_logs(shots)
    chunks = derive.page_chunks(shots["shots"], 9, logs)
    return "\n\n".join(derive.page_prompt(page_no, chunk, logs, sparse=len(chunk) < 9) for page_no, chunk in enumerate(chunks, 1))


def valid_prompt(*, extra_scene: str = "", extra_panel: str = "", missing_layer: str | None = None) -> str:
    _, shots = strict_fixture()
    prompt = render_prompt(shots)
    if extra_scene:
        prompt = prompt.replace("SCENE_LAYER:\n", f"SCENE_LAYER:\n{extra_scene}\n", 1)
    if extra_panel:
        prompt = prompt.replace("\nPANEL-4:", f" {extra_panel}\nPANEL-4:", 1)
    if missing_layer:
        headings = [
            "DELIVERABLE", "SYSTEM_STYLE_LAYER", "SCENE_LAYER", "CAMERA_RULE_LAYER", "CONTINUITY_LAYER",
            "TEXT_DERIVED_LAYOUT", "PANEL_1_MASTER_SPATIAL_LAYOUT_ANCHOR", "DOOR_WINDOW_FURNITURE_GEOMETRY_LOCK",
            "VEHICLE_AND_AXIS_LOCKS", "OBJECT_VISIBILITY_AND_BOUNDARIES", "PANEL_LAYER PANEL-1 to PANEL-9", "NEGATIVE_CONSTRAINTS",
        ]
        if missing_layer in headings:
            index = headings.index(missing_layer)
            next_heading = headings[index + 1] if index + 1 < len(headings) else None
            pattern = rf"(?ms)^{re.escape(missing_layer)}:\n.*?(?=^{re.escape(next_heading)}:\n)" if next_heading else rf"(?ms)^{re.escape(missing_layer)}:\n.*$"
            prompt = re.sub(pattern, "", prompt)
    return prompt


class Validator203AdversarialTests(unittest.TestCase):
    def run_case(
        self,
        prompt: str,
        plan: object,
        shots: object,
        *,
        mode: str = "full",
        canon_text: str | None = None,
        missing_canon: bool = False,
        plan_json: str | None = None,
        shot_json: str | None = None,
    ) -> tuple[int, dict, str]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan_path = root / "panel_plan.json"
            prompt_path = root / "final_image_prompts.md"
            shot_path = root / "shot_data.json"
            canon_path = root / "missing-canon.md" if missing_canon else root / "canon-locks.md"
            report_path = root / "validation_report.json"
            out_path = root / "compiled.md"
            plan_path.write_text(plan_json if plan_json is not None else json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
            prompt_path.write_text(prompt, encoding="utf-8")
            shot_path.write_text(shot_json if shot_json is not None else json.dumps(shots, ensure_ascii=False, indent=2), encoding="utf-8")
            if not missing_canon:
                canon_path.write_text(canon_text if canon_text is not None else CANON_PATH.read_text(encoding="utf-8"), encoding="utf-8")
            cmd = [
                sys.executable,
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
                cmd.extend(["--shot-data", str(shot_path)])
            result = subprocess.run(cmd, text=True, capture_output=True)
            report = json.loads(report_path.read_text(encoding="utf-8"))
            compiled = out_path.read_text(encoding="utf-8") if out_path.exists() else ""
            return result.returncode, report, compiled

    @staticmethod
    def checks(report: dict) -> set[str]:
        return {
            finding["check"]
            for page in report.get("pages", [])
            for finding in page.get("findings", [])
        }

    def test_strict_fixture_passes(self) -> None:
        plan, shots = strict_fixture()
        code, report, _ = self.run_case(render_prompt(shots), plan, shots)
        self.assertEqual(code, 0, report)
        self.assertTrue(report["release_ready"])

    def test_reversed_prompt_panels_fail(self) -> None:
        plan, shots = strict_fixture()
        prompt = valid_prompt()
        ordered_items = [
            derive.visual_sentence(shot, index, str(plan["pages"][0]["panels"][index - 1]["distance_stage_lock"]))
            for index, shot in enumerate(shots["shots"], 1)
        ]
        ordered = "\n".join(ordered_items)
        reversed_panels = "\n".join(reversed(ordered_items))
        code, report, _ = self.run_case(prompt.replace(ordered, reversed_panels), plan, shots)
        self.assertEqual(code, 2, report)
        self.assertIn("G0-06", self.checks(report))

    def test_fake_panel_id_has_no_positional_fallback(self) -> None:
        plan, shots = strict_fixture()
        plan["pages"][0]["panels"][0]["panel"] = "BANANA"
        code, report, _ = self.run_case(valid_prompt(), plan, shots)
        self.assertEqual(code, 2, report)
        self.assertIn("G1-01", self.checks(report))

    def test_missing_source_shots_fail_global_coverage(self) -> None:
        plan, shots = strict_fixture()
        for number in range(10, 19):
            shots["shots"].append(
                {
                    **shots["shots"][-1],
                    "shot_no": number,
                    "beat_ids": [f"B{number:03d}"],
                    "covered_fact_ids": [f"B{number:03d}-F01"],
                }
            )
        code, report, _ = self.run_case(valid_prompt(), plan, shots)
        self.assertEqual(code, 2, report)
        self.assertIn("G1-15", self.checks(report))

    def test_wrong_facts_entities_and_boolean_compression_fail(self) -> None:
        plan, shots = strict_fixture()
        panel = plan["pages"][0]["panels"][2]
        panel["beat_ids"] = ["B999"]
        panel["covered_fact_ids"] = ["B999-F01"]
        panel["visible_characters"] = ["OTHER"]
        panel["visible_props"] = True
        code, report, _ = self.run_case(valid_prompt(), plan, shots)
        self.assertEqual(code, 2, report)
        self.assertTrue({"G0-09", "G1-05"}.issubset(self.checks(report)), report)

    def test_dynamic_layer_and_extra_forbidden_tokens_are_scanned(self) -> None:
        plan, shots = strict_fixture()
        plan["forbidden_prompt_tokens_extra"] = ["neon noir"]
        prompt = valid_prompt(extra_scene="Use neon noir accents in this location.")
        code, report, _ = self.run_case(prompt, plan, shots)
        self.assertEqual(code, 2, report)
        self.assertIn("G0-08", self.checks(report))

    def test_layer_reorder_duplicate_and_unknown_fail_without_rewrite(self) -> None:
        plan, shots = strict_fixture()
        prompt = valid_prompt()
        prompt = prompt.replace("SCENE_LAYER:\n", "UNKNOWN_DYNAMIC_LAYER:\nInjected facts.\n\nSCENE_LAYER:\n", 1)
        prompt = prompt.replace("CAMERA_RULE_LAYER:\n", "SCENE_LAYER:\nDuplicate scene.\n\nCAMERA_RULE_LAYER:\n", 1)
        code, report, compiled = self.run_case(prompt, plan, shots)
        self.assertEqual(code, 2, report)
        self.assertIn("G0-12", self.checks(report))
        self.assertIn("UNKNOWN_DYNAMIC_LAYER", compiled)
        self.assertIn("Duplicate scene", compiled)

    def test_all_canon_corruptions_fail_closed(self) -> None:
        plan, shots = strict_fixture()
        original = CANON_PATH.read_text(encoding="utf-8")
        corruptions = {
            "truncated": "<!-- canon-version: 2.0.3 -->\n",
            "wrong_version": original.replace("canon-version: 2.0.3", "canon-version: 9.9.9"),
            "duplicate": original + "\n### canon:HARD_PHRASES\n\n```text\nduplicate\n```\n",
            "unknown": original + "\n### canon:INJECTED\n\n```text\ninjected\n```\n",
            "tampered": original.replace("Generate one wide horizontal", "Generate one altered wide horizontal", 1),
        }
        for name, canon_text in corruptions.items():
            with self.subTest(name=name):
                code, report, _ = self.run_case(valid_prompt(), plan, shots, canon_text=canon_text)
                self.assertEqual(code, 2, report)
                self.assertIn("G0-00", self.checks(report))
        code, report, _ = self.run_case(valid_prompt(), plan, shots, missing_canon=True)
        self.assertEqual(code, 2, report)
        self.assertIn("G0-00", self.checks(report))

    def test_prompt_canon_drift_is_not_autofixed(self) -> None:
        plan, shots = strict_fixture()
        prompt = valid_prompt().replace("@CANON(SYSTEM_STYLE_LAYER)", "CUSTOM SYSTEM DRIFT")
        code, report, compiled = self.run_case(prompt, plan, shots)
        self.assertEqual(code, 2, report)
        self.assertIn("G0-02", self.checks(report))
        self.assertIn("CUSTOM SYSTEM DRIFT", compiled)
        self.assertFalse(report["pages"][0]["canon_autofixed"])

    def test_legacy_plan_is_review_only_and_never_release_ready(self) -> None:
        plan, shots = strict_fixture()
        plan.update({"version": "2.0.2", "canon_version": "2.0.2", "release_ready": False})
        code, report, _ = self.run_case(valid_prompt(), plan, shots)
        self.assertEqual(code, 1, report)
        self.assertEqual(report["status"], "REVIEW_REQUIRED")
        self.assertEqual(report["exit_code"], 1)
        self.assertFalse(report["release_ready"])

        plan["release_ready"] = True
        code, report, _ = self.run_case(valid_prompt(), plan, shots)
        self.assertEqual(code, 2, report)
        self.assertFalse(report["release_ready"])

    def test_camera_and_continuity_tampering_or_omission_fail(self) -> None:
        mutations = {
            "shot_data_camera_tag": lambda panel, shot: panel.__setitem__("shot_data_camera_tag", "wrong camera"),
            "source_camera_tag": lambda panel, shot: panel.__setitem__("source_camera_tag", "wrong camera"),
            "drawn_camera_tag": lambda panel, shot: panel.__setitem__("drawn_camera_tag", "invented overhead camera"),
            "continuity_updates": lambda panel, shot: panel.__setitem__("continuity_updates", [{"entity": "LX", "field": "position", "to": "invented"}]),
            "missing_source_camera_tag": lambda panel, shot: panel.pop("source_camera_tag"),
            "missing_continuity_updates": lambda panel, shot: panel.pop("continuity_updates"),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                plan, shots = strict_fixture()
                shots["shots"][0]["continuity_updates"] = [{"entity": "LX", "field": "position", "from": "A", "to": "B"}]
                plan["pages"][0]["panels"][0]["continuity_updates"] = list(shots["shots"][0]["continuity_updates"])
                mutate(plan["pages"][0]["panels"][0], shots["shots"][0])
                code, report, _ = self.run_case(valid_prompt(), plan, shots)
                self.assertEqual(code, 2, report)
                self.assertTrue(self.checks(report) & {"G1-04", "G1-07"}, report)

    def test_page_preamble_and_zero_padded_panel_id_fail_without_data_loss(self) -> None:
        plan, shots = strict_fixture()
        prompt = "UNTRUSTED PREFIX\n\n" + valid_prompt().replace("PANEL-1:", "PANEL-01:", 1)
        code, report, compiled = self.run_case(prompt, plan, shots)
        self.assertEqual(code, 2, report)
        self.assertTrue({"G0-11", "G0-06"}.issubset(self.checks(report)), report)
        self.assertIn("UNTRUSTED PREFIX", compiled)
        self.assertIn("PANEL-01", compiled)

    def test_bridge_exemptions_are_always_rejected(self) -> None:
        for bridge in ("intentional_cross_scene_bridge", "intentional_layer_bridge"):
            with self.subTest(bridge=bridge):
                plan, shots = strict_fixture()
                plan["pages"][0]["page_split_policy"] = "scene_layer_aware_strict_source_order+" + bridge
                code, report, _ = self.run_case(valid_prompt(), plan, shots)
                self.assertEqual(code, 1, report)
                expected_code = "R-CROSS-SCENE" if bridge == "intentional_cross_scene_bridge" else "R-CROSS-LAYER"
                self.assertIn(expected_code, self.checks(report))
                self.assertFalse(report["release_ready"])
                self.assertTrue(report["review_required_reasons"], report)
                self.assertEqual(set(report["review_required_reasons"][0]), {"code", "page", "message"})

    def test_memory_keyword_can_open_structurally_consistent_page(self) -> None:
        plan, shots = strict_fixture()
        plan["pages"][0]["page_split_policy"] = "strict_single_scene_single_reality_layer"
        for shot in shots["shots"]:
            tag = shot["camera_main_image"].split("]", 1)[0] + "]"
            shot["camera_main_image"] = tag + "\n回忆层中的同一连续动作"
        code, report, _ = self.run_case(render_prompt(shots), plan, shots)
        self.assertEqual(code, 0, report)

    def test_fractional_source_shot_never_truncates_to_integer(self) -> None:
        plan, shots = strict_fixture()
        plan["pages"][0]["panels"][0]["source_shot"] = 1.9
        code, report, _ = self.run_case(valid_prompt(), plan, shots)
        self.assertEqual(code, 2, report)
        self.assertIn("G1-03", self.checks(report))

    def test_source_shot_numbers_require_unique_increasing_json_integers(self) -> None:
        mutations = {
            "float": lambda shots: shots["shots"][0].__setitem__("shot_no", 1.9),
            "string": lambda shots: shots["shots"][0].__setitem__("shot_no", "1"),
            "duplicate": lambda shots: shots["shots"][1].__setitem__("shot_no", 1),
            "reordered": lambda shots: shots["shots"].__setitem__(slice(0, 2), [shots["shots"][1], shots["shots"][0]]),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                plan, shots = strict_fixture()
                mutate(shots)
                code, report, _ = self.run_case(valid_prompt(), plan, shots)
                self.assertEqual(code, 2, report)
                self.assertIn("G1-03", self.checks(report))

    def test_deterministic_rebuild_rejects_machine_and_page_drift(self) -> None:
        mutations = {
            "visible_only": lambda plan: plan["pages"][0]["panels"][0].__setitem__("visible_only", "COMPLETELY WRONG"),
            "action_composition": lambda plan: plan["pages"][0]["panels"][0].__setitem__("action_composition", "COMPLETELY WRONG"),
            "floor_axis_delta": lambda plan: plan["pages"][0]["panels"][0].__setitem__("floor_axis_delta", "COMPLETELY WRONG"),
            "prop_state": lambda plan: plan["pages"][0]["panels"][0].__setitem__("prop_state", "COMPLETELY WRONG"),
            "source_scene_ids": lambda plan: plan["pages"][0].__setitem__("source_scene_ids", ["WRONG"]),
            "source_layer_keys": lambda plan: plan["pages"][0].__setitem__("source_layer_keys", ["WRONG"]),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                plan, shots = strict_fixture()
                mutate(plan)
                code, report, _ = self.run_case(valid_prompt(), plan, shots)
                self.assertEqual(code, 2, report)
                self.assertIn("G1-17", self.checks(report))

    def test_sparse_and_first_shot_anchor_are_structured_review_states(self) -> None:
        plan, shots = strict_fixture()
        shots["shots"] = shots["shots"][:4]
        logs = derive.scene_logs(shots)
        plan = derive.build_panel_plan(shots, derive.page_chunks(shots["shots"], 9, logs))
        plan.update({"release_ready": True, "review_required_reasons": []})
        code, report, _ = self.run_case(render_prompt(shots), plan, shots)
        self.assertEqual(code, 1, report)
        self.assertEqual(report["review_required_reasons"][0]["code"], "R-SPARSE-UNIQUENESS")

        plan, shots = strict_fixture()
        shots["shots"][0]["camera_main_image"] = "[close-up]\n原镜头构图 1"
        logs = derive.scene_logs(shots)
        plan = derive.build_panel_plan(shots, derive.page_chunks(shots["shots"], 9, logs))
        plan.update({"release_ready": True, "review_required_reasons": []})
        code, report, _ = self.run_case(render_prompt(shots), plan, shots)
        self.assertEqual(code, 1, report)
        self.assertEqual(report["review_required_reasons"][0]["code"], "R-FIRST-SHOT-ANCHOR")

    def test_undeclared_prompt_person_and_prop_fail(self) -> None:
        for addition in (
            "NEW_PERSON enters holding NEW_PROP.",
            "A stranger enters holding a knife.",
            "陌生男人拿刀进入。",
        ):
            with self.subTest(addition=addition):
                plan, shots = strict_fixture()
                prompt = valid_prompt(extra_panel=addition)
                code, report, _ = self.run_case(prompt, plan, shots)
                self.assertEqual(code, 2, report)
                self.assertIn("G1-18", self.checks(report))

    def test_direct_validator_enforces_upstream_shot_data_contract(self) -> None:
        for missing in ("metadata", "script_lock", "validation_report"):
            with self.subTest(missing=missing):
                plan, shots = strict_fixture()
                shots.pop(missing)
                code, report, _ = self.run_case(valid_prompt(), plan, shots)
                self.assertEqual(code, 2, report)
                self.assertIn("G1-00", self.checks(report))
        plan, shots = strict_fixture()
        shots["shots"][0].pop("scene_id")
        code, report, _ = self.run_case(valid_prompt(), plan, shots)
        self.assertEqual(code, 2, report)
        self.assertIn("G1-00", self.checks(report))

    def test_invalid_json_and_root_types_are_contract_failures(self) -> None:
        plan, shots = strict_fixture()
        cases = [
            {"plan_json": "{not-json", "shot_json": None},
            {"plan_json": "[]", "shot_json": None},
            {"plan_json": None, "shot_json": "[]"},
        ]
        for case in cases:
            with self.subTest(case=case):
                code, report, _ = self.run_case(valid_prompt(), plan, shots, **case)
                self.assertEqual(code, 2, report)
                self.assertEqual(report["status"], "CONTRACT_FAIL")
                self.assertEqual(report["exit_code"], 2)
                self.assertFalse(report["release_ready"])

    def test_text_only_v203_never_release_ready(self) -> None:
        plan, shots = strict_fixture()
        plan["release_ready"] = False
        plan["review_required_reasons"] = [{"code": "R-TEXT-ONLY", "page": "GLOBAL", "message": "deprecated compatibility mode"}]
        code, report, _ = self.run_case(valid_prompt(), plan, shots, mode="text-only")
        self.assertEqual(code, 1, report)
        self.assertFalse(report["release_ready"])
        self.assertEqual(report["status"], "REVIEW_REQUIRED")
        self.assertIn("R-TEXT-ONLY-DEPRECATED", self.checks(report))
        self.assertEqual(report["review_required_reasons"][0]["code"], "R-TEXT-ONLY-DEPRECATED")

    def test_review_reasons_require_structured_objects(self) -> None:
        plan, shots = strict_fixture()
        plan["release_ready"] = False
        plan["review_required_reasons"] = ["unstructured"]
        code, report, _ = self.run_case(valid_prompt(), plan, shots)
        self.assertEqual(code, 2, report)
        self.assertIn("G0-13", self.checks(report))


if __name__ == "__main__":
    unittest.main()
