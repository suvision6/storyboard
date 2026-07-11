#!/usr/bin/env python3
"""Stability regressions for the su-image9 v2.0.3 derivation path."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import derive_su_image9_prompt_package as derive

DERIVE_PATH = Path(__file__).with_name("derive_su_image9_prompt_package.py")
MIGRATE_PATH = Path(__file__).with_name("migrate_su_image9_16_to_17.py")
PYTHON = Path(sys.executable)


def make_data(count: int = 9, *, first_tag: str = "平视, 全景, 固定镜头") -> dict:
    shots = []
    for index in range(1, count + 1):
        tag = first_tag if index == 1 else "平视, 中景, 固定镜头"
        shots.append(
            {
                "shot_no": index,
                "scene_id": "S01",
                "scene": "1 外滩 日 外",
                "beat_ids": [f"B{index:03d}"],
                "covered_fact_ids": [f"B{index:03d}-F01"],
                "source_paragraph": f"人物完成动作阶段 {index}",
                "camera_main_image": f"[{tag}]\n原镜头构图 {index}",
                "prompt": f"画面内容：人物完成动作阶段 {index}\n构图：保持原镜头构图 {index}\n运镜手法：固定镜头",
                "visible_characters": ["林晓"],
                "offscreen_characters": [],
                "visible_props": [],
                "continuity_updates": [],
                "shot_type": "master" if index == 1 else "action",
            }
        )
    return {
        "metadata": {"skill_name": "su-fenjingskill-zh", "version": "2.4.2"},
        "script_lock": {"status": "locked"},
        "continuity_logs": [
            {
                "scene_id": "S01",
                "scene": "1 外滩 日 外",
                "spatial_axis": "江岸从画面左侧延伸至右侧",
                "reality_layer": "现实",
                "fixed_objects": ["外滩路面", {"name": "路灯", "position": "画面右侧", "state": "亮"}],
                "characters": ["林晓站在画面左侧", {"name": "周明", "position": "画外", "facing": "向左"}],
            }
        ],
        "shots": shots,
        "validation_report": {"status": "PASS"},
    }


class Derive203StabilityTests(unittest.TestCase):
    def run_derive(self, data: dict, *extra: str, skip_validate: bool = False):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        source = root / "shot_data.json"
        output = root / "package"
        source.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        command = [
            str(PYTHON),
            str(DERIVE_PATH),
            "--shot-data",
            str(source),
            "--out-dir",
            str(output),
            *extra,
        ]
        if skip_validate:
            command.append("--skip-validate")
        result = subprocess.run(
            command,
            text=True,
            capture_output=True,
        )
        return temp, output, result

    def test_general_scene_has_no_cave_mist_or_vehicle_absence_facts(self) -> None:
        temp, output, result = self.run_derive(make_data())
        with temp:
            report_text = (output / "validation_report.json").read_text(encoding="utf-8") if (output / "validation_report.json").exists() else ""
            self.assertEqual(result.returncode, 0, result.stderr + report_text)
            prompt = (output / "final_image_prompts.md").read_text(encoding="utf-8")
            for forbidden in ("洞穴", "地裂", "雾核", "mist-core", "cave walls", "floor fractures", "No vehicle appears"):
                self.assertNotIn(forbidden, prompt)
            self.assertIn("外滩路面", prompt)
            self.assertIn("路灯: position 画面右侧, state 亮", prompt)
            self.assertIn("林晓站在画面左侧", prompt)
            self.assertIn("周明: position 画外, facing 向左", prompt)
            self.assertTrue((output / "final_image_prompts.compiled.md").exists())
            report = json.loads((output / "validation_report.json").read_text(encoding="utf-8"))
            self.assertTrue(report["release_ready"])
            self.assertEqual(Path(report["compiled_path"]), (output / "final_image_prompts.compiled.md").resolve())
            self.assertTrue(Path(report["compiled_path"]).is_file())
            plan = json.loads((output / "panel_plan.json").read_text(encoding="utf-8"))
            page_map = json.loads((output / "page-map.json").read_text(encoding="utf-8"))
            self.assertTrue(plan["release_ready"])
            self.assertTrue(page_map["release_ready"])
            self.assertTrue(page_map["pages"][0]["release_ready"])
            self.assertEqual(page_map["review_required_reasons"], [])
            self.assertEqual(page_map["pages"][0]["review_required_reasons"], [])

    def test_skip_validate_is_rejected_without_prompt_artifacts(self) -> None:
        temp, output, result = self.run_derive(make_data(), skip_validate=True)
        with temp:
            self.assertEqual(result.returncode, 2)
            report = json.loads((output / "validation_report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "CONTRACT_FAIL")
            self.assertFalse(report["release_ready"])
            self.assertFalse((output / "panel_plan.json").exists())
            self.assertFalse((output / "page-map.json").exists())
            self.assertFalse((output / "final_image_prompts.md").exists())
            self.assertFalse((output / "final_image_prompts.compiled.md").exists())

    def test_missing_validator_is_review_required_without_partial_package(self) -> None:
        temp, output, result = self.run_derive(
            make_data(),
            "--validator",
            str(Path(tempfile.gettempdir()) / "missing-su-image9-validator.py"),
        )
        with temp:
            self.assertEqual(result.returncode, 1)
            report = json.loads((output / "validation_report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "REVIEW_REQUIRED")
            self.assertFalse(report["release_ready"])
            self.assertEqual(report["review_required_reasons"][0]["code"], "R-VALIDATOR-MISSING")
            self.assertFalse((output / "panel_plan.json").exists())
            self.assertFalse((output / "page-map.json").exists())
            self.assertFalse((output / "final_image_prompts.md").exists())
            self.assertFalse((output / "final_image_prompts.compiled.md").exists())

    def test_missing_canon_is_review_required_without_partial_package(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "shot_data.json"
            output = root / "package"
            missing_canon = root / "missing-canon-locks.md"
            source.write_text(json.dumps(make_data(), ensure_ascii=False, indent=2), encoding="utf-8")
            result = subprocess.run(
                [
                    str(PYTHON),
                    str(DERIVE_PATH),
                    "--shot-data",
                    str(source),
                    "--out-dir",
                    str(output),
                    "--canon",
                    str(missing_canon),
                ],
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 1)
            report = json.loads((output / "validation_report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "REVIEW_REQUIRED")
            self.assertFalse(report["release_ready"])
            self.assertEqual(report["review_required_reasons"][0]["code"], "R-CANON-MISSING")
            self.assertFalse((output / "panel_plan.json").exists())
            self.assertFalse((output / "page-map.json").exists())
            self.assertFalse((output / "final_image_prompts.md").exists())
            self.assertFalse((output / "final_image_prompts.compiled.md").exists())

    def test_vehicle_is_emitted_only_when_registered(self) -> None:
        data = make_data()
        data["shots"][0]["visible_props"] = ["汽车"]
        temp, output, result = self.run_derive(data)
        with temp:
            report_text = (output / "validation_report.json").read_text(encoding="utf-8") if (output / "validation_report.json").exists() else ""
            self.assertEqual(result.returncode, 0, result.stderr + report_text)
            prompt = (output / "final_image_prompts.md").read_text(encoding="utf-8")
            self.assertIn("Source-defined vehicles or transport objects: 汽车", prompt)

    def test_scene_location_parser_preserves_location_characters(self) -> None:
        cases = {
            "1 外滩 日 外": "外滩",
            "2 夜店 夜 内": "夜店",
            "3 内蒙古 日 外": "内蒙古",
            "14-4 同 地下空腔 日 内": "地下空腔",
        }
        for scene, expected in cases.items():
            with self.subTest(scene=scene):
                self.assertEqual(derive.scene_location_key({"scene": scene}), expected)

    def test_page_size_rejects_zero_negative_and_non_nine(self) -> None:
        for page_size in ("0", "-1", "8", "10"):
            temp, output, result = self.run_derive(make_data(), "--page-size", page_size)
            with temp, self.subTest(page_size=page_size):
                self.assertEqual(result.returncode, 2)
                self.assertFalse(output.exists())

    def test_upstream_fail_and_not_run_are_contract_failures(self) -> None:
        for status in ("FAIL", "NOT_RUN"):
            data = make_data()
            data["validation_report"]["status"] = status
            temp, output, result = self.run_derive(data)
            with temp, self.subTest(status=status):
                self.assertEqual(result.returncode, 2)
                report = json.loads((output / "validation_report.json").read_text(encoding="utf-8"))
                self.assertEqual(report["status"], "CONTRACT_FAIL")
                self.assertFalse((output / "final_image_prompts.md").exists())

    def test_empty_continuity_logs_are_contract_failure(self) -> None:
        data = make_data()
        data["continuity_logs"] = []
        temp, output, result = self.run_derive(data)
        with temp:
            self.assertEqual(result.returncode, 2)
            report = json.loads((output / "validation_report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "CONTRACT_FAIL")
            self.assertTrue(any("continuity_logs must contain" in error for error in report["errors"]))
            self.assertTrue(any("S01 is not registered" in error for error in report["errors"]))
            self.assertFalse((output / "panel_plan.json").exists())
            self.assertFalse((output / "page-map.json").exists())
            self.assertFalse((output / "final_image_prompts.md").exists())
            self.assertFalse((output / "final_image_prompts.compiled.md").exists())

    def test_close_first_shot_requires_review_without_rewrite(self) -> None:
        data = make_data(first_tag="平视, 特写, 固定镜头")
        temp, output, result = self.run_derive(data)
        with temp:
            self.assertEqual(result.returncode, 1)
            report = json.loads((output / "validation_report.json").read_text(encoding="utf-8"))
            self.assertIn("R-FIRST-SHOT-ANCHOR", {item["code"] for item in report["review_required_reasons"]})
            self.assertFalse((output / "panel_plan.json").exists())

    def test_non_empty_output_directory_is_rejected_without_overwriting_release(self) -> None:
        data = make_data()
        temp, output, first = self.run_derive(data)
        with temp:
            self.assertEqual(first.returncode, 0, first.stderr)
            protected_paths = [
                output / "panel_plan.json",
                output / "page-map.json",
                output / "final_image_prompts.compiled.md",
                output / "validation_report.json",
            ]
            before = {path.name: path.read_bytes() for path in protected_paths}
            data["shots"][0]["camera_main_image"] = "[平视, 特写, 固定镜头]\n原镜头特写"
            source = output.parent / "shot_data.json"
            source.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            second = subprocess.run(
                [
                    str(PYTHON),
                    str(DERIVE_PATH),
                    "--shot-data",
                    str(source),
                    "--out-dir",
                    str(output),
                ],
                text=True,
                capture_output=True,
            )
            self.assertEqual(second.returncode, 2)
            self.assertIn("must be absent or empty", second.stderr)
            self.assertEqual(before, {path.name: path.read_bytes() for path in protected_paths})

    def test_page_map_release_state_is_synchronized_at_top_and_page(self) -> None:
        data = make_data()
        pages = derive.page_chunks(data["shots"], 9, derive.scene_logs(data))
        panel_plan = derive.build_panel_plan(data, pages)
        page_map = derive.build_page_map(pages)
        self.assertFalse(panel_plan["release_ready"])
        self.assertFalse(page_map["release_ready"])
        self.assertFalse(page_map["pages"][0]["release_ready"])
        self.assertEqual(page_map["review_required_reasons"][0]["code"], "R-PENDING-VALIDATION")
        self.assertEqual(page_map["pages"][0]["review_required_reasons"][0]["code"], "R-PENDING-VALIDATION")
        derive.set_release_state(panel_plan, page_map, ready=True, reasons=[])
        self.assertTrue(panel_plan["release_ready"])
        self.assertTrue(page_map["release_ready"])
        self.assertTrue(page_map["pages"][0]["release_ready"])
        self.assertEqual(page_map["review_required_reasons"], [])
        self.assertEqual(page_map["pages"][0]["review_required_reasons"], [])

    def test_sparse_page_requires_review_instead_of_repeating_last_shot(self) -> None:
        temp, output, result = self.run_derive(make_data(8))
        with temp:
            self.assertEqual(result.returncode, 1)
            report = json.loads((output / "validation_report.json").read_text(encoding="utf-8"))
            self.assertIn("R-SPARSE-UNIQUENESS", {item["code"] for item in report["review_required_reasons"]})
            self.assertFalse((output / "page-map.json").exists())

    def test_scene_and_reality_boundaries_are_split_not_bridged(self) -> None:
        data = make_data(18)
        data["continuity_logs"].append(
            {
                "scene_id": "S02",
                "scene": "2 夜店 夜 内",
                "reality_layer": "第二现实层",
                "fixed_objects": ["吧台"],
                "characters": ["林晓站在吧台前"],
            }
        )
        for shot in data["shots"][9:]:
            shot["scene_id"] = "S02"
            shot["scene"] = "2 夜店 夜 内"
            shot["reality_layer"] = "第二现实层"
        data["shots"][9]["shot_type"] = "master"
        data["shots"][9]["camera_main_image"] = "[平视, 全景, 固定镜头]\n第二现实层的原始建立镜头"
        temp, output, result = self.run_derive(data)
        with temp:
            report_text = (output / "validation_report.json").read_text(encoding="utf-8") if (output / "validation_report.json").exists() else ""
            self.assertEqual(result.returncode, 0, result.stderr + report_text)
            plan = json.loads((output / "panel_plan.json").read_text(encoding="utf-8"))
            self.assertEqual([page["source_scene_ids"] for page in plan["pages"]], [["S01"], ["S02"]])
            self.assertEqual([page["source_layer_keys"] for page in plan["pages"]], [["现实"], ["第二现实层"]])
            self.assertNotIn("intentional_", json.dumps(plan, ensure_ascii=False))

    def test_plan_contains_explicit_source_fact_arrays(self) -> None:
        temp, output, result = self.run_derive(make_data())
        with temp:
            self.assertEqual(result.returncode, 0, result.stderr)
            plan = json.loads((output / "panel_plan.json").read_text(encoding="utf-8"))
            panel = plan["pages"][0]["panels"][0]
            self.assertEqual(panel["beat_ids"], ["B001"])
            self.assertEqual(panel["covered_fact_ids"], ["B001-F01"])
            self.assertEqual(panel["visible_characters"], ["林晓"])
            self.assertEqual(panel["offscreen_characters"], [])
            self.assertEqual(panel["visible_props"], [])
            self.assertIn("visible_only", panel)
            self.assertIn("prop_state", panel)

    def test_legacy_detector_never_creates_migrated_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan_path = root / "panel_plan.json"
            prompt_path = root / "final.md"
            output = root / "migrated"
            plan_path.write_text(json.dumps({"skill": "su-image9", "version": "2.0.2"}), encoding="utf-8")
            prompt_path.write_text("# PAGE-01\n@CANON(HARD_PHRASES)\n@CANON(GEOMETRY_BLUEPRINT)\n", encoding="utf-8")
            result = subprocess.run(
                [
                    str(PYTHON),
                    str(MIGRATE_PATH),
                    "--panel-plan",
                    str(plan_path),
                    "--final-prompts",
                    str(prompt_path),
                    "--out-dir",
                    str(output),
                ],
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 1, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["status"], "F-LEGACY-REGENERATE")
            self.assertEqual(report["detected_version"], "2.0.2")
            self.assertFalse(output.exists())

    def test_unreleased_210_is_not_treated_as_current(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan_path = root / "panel_plan.json"
            prompt_path = root / "final.md"
            output = root / "migrated"
            plan_path.write_text(json.dumps({"skill": "su-image9", "version": "2.1.0"}), encoding="utf-8")
            prompt_path.write_text("# PAGE-01\n@CANON(HARD_PHRASES)\n@CANON(GEOMETRY_BLUEPRINT)\n", encoding="utf-8")
            result = subprocess.run(
                [
                    str(PYTHON),
                    str(MIGRATE_PATH),
                    "--panel-plan",
                    str(plan_path),
                    "--final-prompts",
                    str(prompt_path),
                    "--out-dir",
                    str(output),
                ],
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 1, result.stderr)
            report = json.loads(result.stdout)
            self.assertNotEqual(report["status"], "CURRENT_NO_MIGRATION_REQUIRED")
            self.assertEqual(report["status"], "F-LEGACY-REGENERATE")
            self.assertEqual(report["detected_version"], "2.1.0")
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
