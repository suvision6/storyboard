#!/usr/bin/env python3
"""Tests for the stable 7-column storyboard delivery contract."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from openpyxl import load_workbook

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import storyboard_delivery as delivery


def valid_data() -> dict:
    return {
        "metadata": {
            "skill_name": "su-fenjingskill-zh",
            "version": "2.3.0",
            "title": "稳定化样片",
            "reference_status": {
                "continuity-shot-data": "loaded",
                "camera-language": "loaded",
                "seedance-prompt-rules": "loaded",
            },
        },
        "continuity_logs": [
            {
                "scene": "1 室内 日 内",
                "first_shot_anchor_type": "single_continuation",
                "spatial_axis": "A在门口，B在桌边。",
                "fixed_objects": [],
                "characters": [],
                "props": [],
                "sound_sources": [],
                "reality_layer": "现实",
            }
        ],
        "beats": [
            {
                "beat_id": "B001",
                "scene": "1 室内 日 内",
                "source_text": "A站在门口。",
                "facts": [{"fact_id": "B001-F01", "type": "position", "text": "A站在门口。"}],
            },
            {
                "beat_id": "B002",
                "scene": "1 室内 日 内",
                "source_text": "A走到桌边。",
                "facts": [{"fact_id": "B002-F01", "type": "position", "text": "A走到桌边。"}],
            },
            {
                "beat_id": "B003",
                "scene": "1 室内 日 内",
                "source_text": "A说：到了。",
                "facts": [{"fact_id": "B003-F01", "type": "dialogue", "text": "到了。"}],
            },
        ],
        "shots": [
            {
                "shot_no": 1,
                "scene": "1 室内 日 内",
                "beat_ids": ["B001"],
                "covered_fact_ids": ["B001-F01"],
                "source_paragraph": "A站在门口。",
                "duration_seconds": 2,
                "duration_breakdown": {
                    "sync_action_seconds": 1,
                    "sync_dialogue_seconds": 0,
                    "non_sync_action_seconds": 0,
                    "emotional_pause_seconds": 1,
                },
                "camera_main_image": "[平视, 中景, 固定镜头]\n【机位逻辑】摄影机在桌边看向门口。\n【场景首镜站位】（A站在门口，面向桌边。）\nA站在门口，手扶门框。",
                "notes": "建立初始站位。",
                "prompt": "",
                "visible_characters": ["A"],
                "offscreen_characters": [],
                "visible_props": [],
                "continuity_updates": [],
            },
            {
                "shot_no": 2,
                "scene": "1 室内 日 内",
                "beat_ids": ["B002", "B003"],
                "covered_fact_ids": ["B002-F01", "B003-F01"],
                "source_paragraph": "A走到桌边。A说：到了。",
                "duration_seconds": 3,
                "duration_breakdown": {
                    "sync_action_seconds": 2,
                    "sync_dialogue_seconds": 1,
                    "non_sync_action_seconds": 0,
                    "emotional_pause_seconds": 1,
                },
                "camera_main_image": "[侧面平视, 中景, 横移跟拍]\n【机位逻辑】摄影机沿桌边横移，跟住A的脚步。\n【站位位移】A从门口走到桌边，面向B的位置。\nA在桌边停下，说：“到了。”",
                "notes": "A完成位置迁移。",
                "prompt": "",
                "visible_characters": ["A"],
                "offscreen_characters": [],
                "visible_props": [],
                "continuity_updates": [
                    {
                        "entity_type": "character",
                        "entity": "A",
                        "field": "position",
                        "from": "门口",
                        "to": "桌边",
                        "evidence_fact_ids": ["B002-F01"],
                    }
                ],
            },
        ],
        "validation_report": {"status": "PASS", "warnings": [], "errors": []},
    }


class DeliveryContractTests(unittest.TestCase):
    def test_build_writes_7_column_markdown_and_excel(self) -> None:
        with tempfile.TemporaryDirectory() as root_name:
            root = Path(root_name)
            data_path = root / "sample.shot_data.json"
            md_path = root / "sample.md"
            xlsx_path = root / "sample.xlsx"
            data_path.write_text(json.dumps(valid_data(), ensure_ascii=False), encoding="utf-8")

            rc = delivery.main(["build", "--data", str(data_path), "--markdown", str(md_path), "--excel", str(xlsx_path)])
            self.assertEqual(0, rc)

            built = json.loads(data_path.read_text(encoding="utf-8"))
            self.assertEqual("PASS", built["validation_report"]["status"])
            self.assertNotIn("keyframe", built["shots"][0])
            self.assertEqual(delivery.derive_prompt(built["shots"][0]), built["shots"][0]["prompt"])

            markdown = md_path.read_text(encoding="utf-8")
            self.assertIn("| 镜号 | 场景 | 原剧本段落 | 镜头时长(秒) | 运镜+主画面描述(含台词) | 备注 | Prompt |", markdown)
            self.assertNotIn("关键帧", markdown)
            self.assertNotIn("【镜内变化】", markdown)

            workbook = load_workbook(xlsx_path, read_only=True)
            try:
                self.assertEqual(["分镜表"], workbook.sheetnames)
                sheet = workbook["分镜表"]
                self.assertEqual(3, sheet.max_row)
                self.assertEqual(7, sheet.max_column)
            finally:
                workbook.close()

    def test_validate_wrapper_passes_built_files(self) -> None:
        with tempfile.TemporaryDirectory() as root_name:
            root = Path(root_name)
            data_path = root / "sample.shot_data.json"
            md_path = root / "sample.md"
            xlsx_path = root / "sample.xlsx"
            data_path.write_text(json.dumps(valid_data(), ensure_ascii=False), encoding="utf-8")
            self.assertEqual(0, delivery.main(["build", "--data", str(data_path), "--markdown", str(md_path), "--excel", str(xlsx_path)]))

            process = subprocess.run(
                [
                    "node",
                    str(SCRIPT_DIR / "validate_storyboard.js"),
                    "--python",
                    sys.executable,
                    "--data",
                    str(data_path),
                    "--markdown",
                    str(md_path),
                    "--excel",
                    str(xlsx_path),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, process.returncode, process.stderr + process.stdout)

    def test_keyframe_field_is_rejected(self) -> None:
        data = valid_data()
        data["shots"][0]["keyframe"] = "场景：旧关键帧"
        delivery.derive_prompts(data)
        result = delivery.validate_data(data, strict_status=True)
        self.assertTrue(any("keyframe" in item for item in result.errors))

    def test_pass_internal_status_is_rejected(self) -> None:
        data = valid_data()
        data["validation_report"]["status"] = "PASS_INTERNAL"
        delivery.derive_prompts(data)
        result = delivery.validate_data(data, strict_status=True)
        self.assertTrue(any("PASS / WARN / FAIL" in item for item in result.errors))

    def test_station_move_requires_continuity_update(self) -> None:
        data = valid_data()
        data["shots"][1]["continuity_updates"] = []
        delivery.derive_prompts(data)
        result = delivery.validate_data(data, strict_status=True)
        self.assertTrue(any("continuity_updates 为空" in item for item in result.errors))

    def test_position_update_requires_station_move(self) -> None:
        data = valid_data()
        data["shots"][1]["camera_main_image"] = data["shots"][1]["camera_main_image"].replace("【站位位移】", "")
        delivery.derive_prompts(data)
        result = delivery.validate_data(data, strict_status=True)
        self.assertTrue(any("缺少【站位位移】" in item for item in result.errors))

    def test_prompt_internal_label_is_rejected(self) -> None:
        data = valid_data()
        delivery.derive_prompts(data)
        data["shots"][0]["prompt"] += "\n【镜内变化】污染"
        result = delivery.validate_data(data, strict_status=True)
        self.assertTrue(any("Prompt" in item and "内部" in item for item in result.errors))

    def test_dialogue_duration_cannot_be_underestimated(self) -> None:
        data = valid_data()
        data["shots"][1]["camera_main_image"] = "[平视, 中景, 固定镜头]\n【机位逻辑】摄影机拍A站在桌边。\nA说：“这句话很长很长不能压到一秒。”"
        data["shots"][1]["duration_seconds"] = 1
        data["shots"][1]["duration_breakdown"]["sync_action_seconds"] = 1
        data["shots"][1]["duration_breakdown"]["sync_dialogue_seconds"] = 1
        data["shots"][1]["duration_breakdown"]["emotional_pause_seconds"] = 0
        data["shots"][1]["continuity_updates"] = []
        delivery.derive_prompts(data)
        result = delivery.validate_data(data, strict_status=True)
        self.assertTrue(any("对白时长过短" in item for item in result.errors))

    def test_outdoor_multi_character_panorama_first_shot_passes(self) -> None:
        data = valid_data()
        data["continuity_logs"][0]["first_shot_anchor_type"] = "both"
        data["continuity_logs"][0]["spatial_axis"] = "A在画面左侧，B在画面右侧，两人沿山路面向远处。"
        data["shots"][0]["camera_main_image"] = (
            "[微俯视, 大全景, 固定镜头]\n"
            "【机位逻辑】摄影机在山路上方俯看两人和远处入口。\n"
            "【场景首镜站位】（A在画面左侧，B在画面右侧，两人相距三米，面向远处入口。）\n"
            "A和B站在山路上，远处入口被雾压住。"
        )
        data["shots"][0]["visible_characters"] = ["A", "B"]
        delivery.derive_prompts(data)
        result = delivery.validate_data(data, strict_status=True)
        self.assertFalse(result.errors, result.errors)

    def test_indoor_multi_character_full_shot_first_shot_passes(self) -> None:
        data = valid_data()
        data["continuity_logs"][0]["first_shot_anchor_type"] = "multi_character"
        data["continuity_logs"][0]["spatial_axis"] = "A在画面左侧门口，B在画面右侧桌边，两人隔桌对视。"
        data["shots"][0]["camera_main_image"] = (
            "[平视, 全景, 固定镜头]\n"
            "【机位逻辑】摄影机在房间侧墙拍到门、桌和两人的左右关系。\n"
            "【场景首镜站位】（A在画面左侧门口，面向右侧桌边；B在画面右侧桌边，面向A，两人隔桌对视。）\n"
            "A扶着门框，B站在桌边。"
        )
        data["shots"][0]["visible_characters"] = ["A", "B"]
        delivery.derive_prompts(data)
        result = delivery.validate_data(data, strict_status=True)
        self.assertFalse(result.errors, result.errors)

    def test_multi_character_first_shot_medium_close_fails(self) -> None:
        data = valid_data()
        data["continuity_logs"][0]["first_shot_anchor_type"] = "multi_character"
        data["shots"][0]["camera_main_image"] = (
            "[平视, 中近景, 固定镜头]\n"
            "【机位逻辑】摄影机拍两人上半身。\n"
            "【场景首镜站位】（A在左，B在右，两人面向彼此。）\n"
            "A和B看着对方。"
        )
        data["shots"][0]["visible_characters"] = ["A", "B"]
        delivery.derive_prompts(data)
        result = delivery.validate_data(data, strict_status=True)
        self.assertTrue(any("景别必须为大远景/大全景/全景/中全景" in item for item in result.errors))

    def test_single_continuation_medium_first_shot_passes(self) -> None:
        data = valid_data()
        data["continuity_logs"][0]["first_shot_anchor_type"] = "single_continuation"
        data["shots"][0]["camera_main_image"] = (
            "[平视, 中景, 固定镜头]\n"
            "【机位逻辑】摄影机在岩壁前拍A的半身和身后空间边界。\n"
            "【场景首镜站位】（A靠在岩壁前，面向画面右侧微光。）\n"
            "A靠在岩壁上，抬头看向右侧微光。"
        )
        data["shots"][0]["visible_characters"] = ["A"]
        delivery.derive_prompts(data)
        result = delivery.validate_data(data, strict_status=True)
        self.assertFalse(result.errors, result.errors)

    def test_extreme_wide_steadicam_fails(self) -> None:
        data = valid_data()
        data["shots"][0]["camera_main_image"] = (
            "[微俯视, 大全景, 斯坦尼康平稳跟随]\n"
            "【机位逻辑】摄影机拍到山路全貌和人物位置。\n"
            "【场景首镜站位】（A站在画面左侧，面向远处。）\n"
            "A站在山路上。"
        )
        delivery.derive_prompts(data)
        result = delivery.validate_data(data, strict_status=True)
        self.assertTrue(any("大远景/大全景不得使用斯坦尼康" in item for item in result.errors))

    def test_extreme_wide_crane_passes(self) -> None:
        data = valid_data()
        data["continuity_logs"][0]["first_shot_anchor_type"] = "both"
        data["continuity_logs"][0]["spatial_axis"] = "A在画面左侧，B在画面右侧，两人面向远处入口。"
        data["shots"][0]["camera_main_image"] = (
            "[微俯视, 大全景, 伸缩摇臂缓慢下降]\n"
            "【机位逻辑】摄影机从林冠上方下降，拍到山路、入口和两人左右关系。\n"
            "【场景首镜站位】（A在画面左侧，B在画面右侧，两人相距三米，面向远处入口。）\n"
            "A和B站在山路上。"
        )
        data["shots"][0]["visible_characters"] = ["A", "B"]
        delivery.derive_prompts(data)
        result = delivery.validate_data(data, strict_status=True)
        self.assertFalse(result.errors, result.errors)

    def test_aerial_large_landscape_passes(self) -> None:
        data = valid_data()
        data["continuity_logs"][0]["first_shot_anchor_type"] = "space"
        data["shots"][0]["camera_main_image"] = (
            "[高角度俯拍, 大远景, 航拍缓慢推进]\n"
            "【机位逻辑】摄影机从高速公路上方推进，拍到道路纵深和远处雾区。\n"
            "【场景首镜站位】（道路由画面左下延伸至右上，A处在远处路肩，面向雾区。）\n"
            "浓雾压过高速公路。"
        )
        delivery.derive_prompts(data)
        result = delivery.validate_data(data, strict_status=True)
        self.assertFalse(result.errors, result.errors)

    def test_steadicam_medium_follow_passes(self) -> None:
        data = valid_data()
        data["shots"][0]["camera_main_image"] = (
            "[平视, 中景, 斯坦尼康跟随]\n"
            "【机位逻辑】摄影机在地面跟随A从门口走向桌边。\n"
            "【场景首镜站位】（A站在门口，面向桌边。）\n"
            "A从门口向桌边走去。"
        )
        delivery.derive_prompts(data)
        result = delivery.validate_data(data, strict_status=True)
        self.assertFalse(result.errors, result.errors)

    def test_aerial_medium_close_fails(self) -> None:
        data = valid_data()
        data["shots"][0]["camera_main_image"] = (
            "[平视, 中近景, 航拍缓慢推进]\n"
            "【机位逻辑】摄影机贴近A的上半身推进。\n"
            "【场景首镜站位】（A站在门口，面向桌边。）\n"
            "A看向桌边。"
        )
        delivery.derive_prompts(data)
        result = delivery.validate_data(data, strict_status=True)
        self.assertTrue(any("航拍必须服务于大范围空间" in item for item in result.errors))


if __name__ == "__main__":
    unittest.main()
