#!/usr/bin/env python3

import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import storyboard_delivery as delivery


def keyframe(scene, subject, image):
    return (
        f"场景：{scene}；\n"
        f"主体：{subject}；\n"
        f"画面：{image}；\n"
        "构图/景别：克制的单帧关系构图；\n"
        "光影/色调：低饱和冷灰光；\n"
        "风格：电影感、真实质感、分镜关键帧；\n"
        "禁止：多格漫画、拼贴、字幕、对白文字、水印、摄像机设备、场记板、额外角色、额外道具。"
        "严格杜绝低分辨率，模糊，光影错位，比例不合理，杜绝任何cg游戏感"
    )


def valid_data():
    scene_one = "13-1 赤狐岭迷雾深林 日 外"
    scene_two = "13-2 赤狐岭白雾空地 日 外"
    return {
        "metadata": {
            "skill_name": "su-fenjingskill-zh",
            "version": "2.2.0",
            "title": "引魂师片段测试",
            "reference_status": {
                "camera_language": "loaded",
                "seedance_prompt_rules": "loaded",
            },
        },
        "continuity_logs": [
            {
                "scene": scene_one,
                "spatial_axis": "沿小径纵深轴，三人保持前后关系。",
                "fixed_objects": [
                    {"name": "密林小径", "position": "场景中央", "state": "碎石与枯叶覆盖"}
                ],
                "characters": [
                    {"name": "林晓彤", "position": "小径左前", "facing": "山里", "state": "行进"},
                    {"name": "沈夜", "position": "右后半步", "facing": "山里", "state": "行进"},
                    {"name": "顾成", "position": "队尾", "facing": "山里", "state": "行进"},
                ],
                "props": [
                    {
                        "name": "手环",
                        "position": "林晓彤左腕",
                        "owner": "林晓彤",
                        "state": "微光",
                    }
                ],
                "sound_sources": [],
                "reality_layer": "现实",
            },
            {
                "scene": scene_two,
                "spatial_axis": "三人面向白雾中心，保持同侧轴线。",
                "fixed_objects": [
                    {"name": "白雾空地", "position": "场景中央", "state": "白雾缓慢散开"}
                ],
                "characters": [
                    {"name": "林晓彤", "position": "空地左侧", "facing": "雾心", "state": "戒备"},
                    {"name": "沈夜", "position": "空地中央", "facing": "雾心", "state": "观察"},
                    {"name": "顾成", "position": "空地右侧", "facing": "雾心", "state": "戒备"},
                ],
                "props": [
                    {
                        "name": "手环",
                        "position": "林晓彤左腕",
                        "owner": "林晓彤",
                        "state": "变亮",
                    }
                ],
                "sound_sources": [],
                "reality_layer": "现实",
            },
        ],
        "beats": [
            {
                "beat_id": "B001",
                "scene": scene_one,
                "source_text": "三人穿过密林，雾在树与树之间一层层飘散。",
                "dramatic_function": "建立空间与队形。",
                "facts": [
                    {"fact_id": "B001-F01", "type": "action", "text": "三人穿过密林"},
                    {"fact_id": "B001-F02", "type": "space", "text": "雾在树与树之间一层层飘散"},
                ],
            },
            {
                "beat_id": "B002",
                "scene": scene_one,
                "source_text": "林晓彤手环上那丝金色随每一步深入变亮。",
                "dramatic_function": "道具状态升级。",
                "facts": [
                    {"fact_id": "B002-F01", "type": "prop", "text": "手环金色随深入变亮"}
                ],
            },
            {
                "beat_id": "B003",
                "scene": scene_two,
                "source_text": "沈夜：进这片林子，它就已经盯着我们了。",
                "dramatic_function": "明确威胁。",
                "facts": [
                    {
                        "fact_id": "B003-F01",
                        "type": "dialogue",
                        "text": "进这片林子，它就已经盯着我们了。",
                    }
                ],
            },
        ],
        "shots": [
            {
                "shot_no": 1,
                "scene": scene_one,
                "beat_ids": ["B001"],
                "covered_fact_ids": ["B001-F01", "B001-F02"],
                "source_paragraph": "三人穿过密林，雾在树与树之间一层层飘散。",
                "duration_seconds": 7,
                "duration_breakdown": {
                    "sync_action_seconds": 4,
                    "sync_dialogue_seconds": 0,
                    "non_sync_action_seconds": 0,
                    "emotional_pause_seconds": 3,
                },
                "long_take": {
                    "classification": "not_applicable",
                    "reason": "镜头不超过10秒",
                },
                "camera_main_image": (
                    "[微俯视, 全景, 缓慢推进]\n"
                    "【机位逻辑】摄影机在小径前方略高处朝三人后退，保留雾层纵深。\n"
                    "【场景首镜站位】（林晓彤：小径左前，面向山里；沈夜：右后半步，面向山里；"
                    "顾成：队尾，面向山里。）\n"
                    "三人踩过碎石和枯叶进入密林，雾在树与树之间一层层飘散。"
                ),
                "notes": (
                    "[时长估算] 同步动作4秒 + 同步台词0秒 + 非同步动作0秒 + 情绪留白3秒"
                ),
                "prompt": (
                    "时间：0秒-7秒\n"
                    "景别：微俯视全景\n"
                    "构图：林晓彤、沈夜、顾成沿小径前后排列。\n"
                    "运镜手法：缓慢推进\n"
                    "画面内容：林晓彤、沈夜、顾成穿过密林，雾在树间分层飘散。"
                ),
                "keyframe": keyframe(
                    scene_one,
                    "林晓彤、沈夜、顾成",
                    "三人沿密林小径前行，树间雾层清晰",
                ),
                "visible_characters": ["林晓彤", "沈夜", "顾成"],
                "offscreen_characters": [],
                "visible_props": [],
                "continuity_updates": [],
            },
            {
                "shot_no": 2,
                "scene": scene_one,
                "beat_ids": ["B002"],
                "covered_fact_ids": ["B002-F01"],
                "source_paragraph": "林晓彤手环上那丝金色随每一步深入变亮。",
                "duration_seconds": 5,
                "duration_breakdown": {
                    "sync_action_seconds": 5,
                    "sync_dialogue_seconds": 0,
                    "non_sync_action_seconds": 0,
                    "emotional_pause_seconds": 0,
                },
                "long_take": {
                    "classification": "not_applicable",
                    "reason": "镜头不超过10秒",
                },
                "camera_main_image": (
                    "[平视, 手腕特写, 跟拍]\n"
                    "【机位逻辑】摄影机贴近林晓彤左腕随步伐移动。\n"
                    "手环里的金色随每一步深入逐次变亮。"
                ),
                "notes": "手环状态由微光变为变亮。",
                "prompt": (
                    "时间：0秒-5秒\n"
                    "景别：平视特写\n"
                    "构图：林晓彤左腕和手环居中。\n"
                    "运镜手法：跟拍\n"
                    "画面内容：林晓彤继续行走，手环里的金色逐次变亮。"
                ),
                "keyframe": keyframe(
                    scene_one,
                    "林晓彤左腕和手环",
                    "手环金色亮度增强，枯叶地面作为背景",
                ),
                "visible_characters": ["林晓彤"],
                "offscreen_characters": [],
                "visible_props": ["手环"],
                "continuity_updates": [
                    {
                        "entity_type": "prop",
                        "entity": "手环",
                        "field": "state",
                        "from": "微光",
                        "to": "变亮",
                        "evidence_fact_ids": ["B002-F01"],
                    }
                ],
            },
            {
                "shot_no": 3,
                "scene": scene_two,
                "beat_ids": ["B003"],
                "covered_fact_ids": ["B003-F01"],
                "source_paragraph": "沈夜：进这片林子，它就已经盯着我们了。",
                "duration_seconds": 6,
                "duration_breakdown": {
                    "sync_action_seconds": 2,
                    "sync_dialogue_seconds": 4,
                    "non_sync_action_seconds": 0,
                    "emotional_pause_seconds": 2,
                },
                "long_take": {
                    "classification": "not_applicable",
                    "reason": "镜头不超过10秒",
                },
                "camera_main_image": (
                    "[平视, 三人中景, 固定镜头]\n"
                    "【机位逻辑】摄影机在三人正前方，保持威胁方向和视线轴。\n"
                    "【场景首镜站位】（林晓彤：空地左侧，面向雾心；沈夜：空地中央，面向雾心；"
                    "顾成：空地右侧，面向雾心。）\n"
                    "沈夜扫视白雾，对林晓彤和顾成说：\"进这片林子，它就已经盯着我们了。\""
                ),
                "notes": "沈夜明确白雾已经锁定三人。",
                "prompt": (
                    "时间：0秒-6秒\n"
                    "景别：平视中景\n"
                    "构图：沈夜居中，林晓彤和顾成分处两侧。\n"
                    "运镜手法：固定锁机\n"
                    "画面内容：沈夜扫视白雾，对林晓彤和顾成说：\"进这片林子，它就已经盯着我们了。\""
                ),
                "keyframe": keyframe(
                    scene_two,
                    "林晓彤、沈夜、顾成",
                    "沈夜居中观察白雾，另外两人分处两侧戒备",
                ),
                "visible_characters": ["林晓彤", "沈夜", "顾成"],
                "offscreen_characters": [],
                "visible_props": [],
                "continuity_updates": [],
            },
        ],
        "validation_report": {
            "status": "FAIL",
            "reference_missing": [],
            "warnings": [],
            "errors": ["尚未运行"],
        },
    }


class DeliveryTests(unittest.TestCase):
    def test_valid_data_passes(self):
        result = delivery.validate_data(valid_data())
        self.assertEqual([], result.errors)
        self.assertEqual("PASS", result.status)

    def test_missing_fact_fails(self):
        data = valid_data()
        data["shots"][1]["covered_fact_ids"] = []
        result = delivery.validate_data(data)
        self.assertTrue(any("原文事实未覆盖" in item for item in result.errors))

    def test_beat_gap_fails(self):
        data = valid_data()
        data["beats"][1]["beat_id"] = "B004"
        result = delivery.validate_data(data)
        self.assertTrue(any("Beat ID 不连续" in item for item in result.errors))

    def test_continuity_drift_fails(self):
        data = valid_data()
        data["shots"][1]["continuity_updates"][0]["from"] = "熄灭"
        result = delivery.validate_data(data)
        self.assertTrue(any("连续性迁移起点错误" in item for item in result.errors))

    def test_duration_formula_fails(self):
        data = valid_data()
        data["shots"][0]["duration_seconds"] = 6
        result = delivery.validate_data(data)
        self.assertTrue(any("时长应为" in item for item in result.errors))

    def test_positive_subtitle_fails(self):
        data = valid_data()
        data["shots"][0]["keyframe"] = data["shots"][0]["keyframe"].replace(
            "画面：", "画面：带字幕的"
        )
        result = delivery.validate_data(data)
        self.assertTrue(any("只能出现在关键帧禁止字段" in item for item in result.errors))

    def test_reference_missing_warns(self):
        data = valid_data()
        data["metadata"]["reference_status"]["camera_language"] = "missing"
        result = delivery.validate_data(data)
        self.assertEqual([], result.errors)
        self.assertEqual("WARN", result.status)
        report = delivery.report_from(result, data["metadata"])
        self.assertEqual(["camera-language.md"], report["reference_missing"])

    def test_prompt_over_15_seconds_requires_segments(self):
        data = valid_data()
        shot = data["shots"][0]
        shot["duration_seconds"] = 16
        shot["duration_breakdown"]["sync_action_seconds"] = 13
        shot["duration_breakdown"]["emotional_pause_seconds"] = 3
        shot["notes"] = (
            "[时长估算] 同步动作13秒 + 同步台词0秒 + 非同步动作0秒 + 情绪留白3秒"
        )
        shot["long_take"] = {
            "classification": "not_applicable",
            "reason": "镜头由多个视频片段组合",
        }
        shot["prompt"] = shot["prompt"].replace("0秒-7秒", "0秒-16秒")
        result = delivery.validate_data(data)
        self.assertTrue(any("超过15秒的 Prompt" in item for item in result.errors))

    def test_segmented_prompt_passes(self):
        data = valid_data()
        shot = data["shots"][0]
        shot["duration_seconds"] = 16
        shot["duration_breakdown"]["sync_action_seconds"] = 13
        shot["duration_breakdown"]["emotional_pause_seconds"] = 3
        shot["notes"] = (
            "[时长估算] 同步动作13秒 + 同步台词0秒 + 非同步动作0秒 + 情绪留白3秒"
        )
        shot["long_take"] = {
            "classification": "not_applicable",
            "reason": "镜头由两个视频片段组合",
        }
        shot["prompt"] = (
            "片段A\n"
            "时间：0秒-10秒\n"
            "景别：微俯视全景\n"
            "构图：林晓彤、沈夜、顾成沿小径前后排列。\n"
            "运镜手法：缓慢推进\n"
            "画面内容：林晓彤、沈夜、顾成进入密林，雾在树间分层飘散。\n"
            "片段B\n"
            "时间：0秒-6秒\n"
            "景别：平视中景\n"
            "构图：三人继续沿小径前行。\n"
            "运镜手法：跟拍\n"
            "画面内容：林晓彤、沈夜、顾成继续深入密林。"
        )
        result = delivery.validate_data(data)
        self.assertEqual([], result.errors)

    def test_long_take_marker_required(self):
        data = valid_data()
        shot = data["shots"][0]
        shot["duration_seconds"] = 11
        shot["duration_breakdown"]["sync_action_seconds"] = 8
        shot["notes"] = (
            "[时长估算] 同步动作8秒 + 同步台词0秒 + 非同步动作0秒 + 情绪留白3秒"
        )
        shot["long_take"] = {
            "classification": "continuous_performance",
            "reason": "三人连续进入密林",
        }
        shot["prompt"] = shot["prompt"].replace("0秒-7秒", "0秒-11秒")
        result = delivery.validate_data(data)
        self.assertTrue(any("必须标记 [长镜头]" in item for item in result.errors))

    def test_position_update_requires_marker(self):
        data = valid_data()
        data["shots"][0]["continuity_updates"] = [
            {
                "entity_type": "character",
                "entity": "林晓彤",
                "field": "position",
                "from": "小径左前",
                "to": "树旁",
                "evidence_fact_ids": ["B001-F01"],
            }
        ]
        result = delivery.validate_data(data)
        self.assertTrue(any("必须写【站位位移】" in item for item in result.errors))

    def test_build_and_validate_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data_path = root / "sample.shot_data.json"
            md_path = root / "sample.md"
            xlsx_path = root / "sample.xlsx"
            data_path.write_text(
                json.dumps(valid_data(), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            build = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_DIR / "storyboard_delivery.py"),
                    "build",
                    "--data",
                    str(data_path),
                    "--markdown",
                    str(md_path),
                    "--excel",
                    str(xlsx_path),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, build.returncode, build.stdout + build.stderr)
            validate = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_DIR / "storyboard_delivery.py"),
                    "validate",
                    "--data",
                    str(data_path),
                    "--markdown",
                    str(md_path),
                    "--excel",
                    str(xlsx_path),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, validate.returncode, validate.stdout + validate.stderr)
            self.assertIn("| 关键帧 |", md_path.read_text(encoding="utf-8"))
            _, load_workbook, _, _, _, _ = delivery.openpyxl_modules()
            workbook = load_workbook(xlsx_path)
            self.assertEqual(["分镜表"], workbook.sheetnames)
            self.assertEqual("A2", workbook["分镜表"].freeze_panes)
            self.assertEqual(delivery.HEADERS, [cell.value for cell in workbook["分镜表"][1]])
            self.assertEqual(108, workbook["分镜表"].row_dimensions[2].height)
            workbook.close()

    def test_node_wrapper(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("node is not available")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data_path, md_path, xlsx_path = (
                root / "sample.shot_data.json",
                root / "sample.md",
                root / "sample.xlsx",
            )
            data_path.write_text(json.dumps(valid_data(), ensure_ascii=False), encoding="utf-8")
            self.assertEqual(
                0,
                delivery.run_build(
                    type("Args", (), {"data": data_path, "markdown": md_path, "excel": xlsx_path})()
                ),
            )
            validate = subprocess.run(
                [
                    node,
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
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, validate.returncode, validate.stdout + validate.stderr)

    def test_old_column_name_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data_path, md_path, xlsx_path = (
                root / "sample.shot_data.json",
                root / "sample.md",
                root / "sample.xlsx",
            )
            data_path.write_text(json.dumps(valid_data(), ensure_ascii=False), encoding="utf-8")
            code = delivery.run_build(
                type("Args", (), {"data": data_path, "markdown": md_path, "excel": xlsx_path})()
            )
            self.assertEqual(0, code)
            md_path.write_text(
                md_path.read_text(encoding="utf-8").replace("| 关键帧 |", "| 故事板 |", 1),
                encoding="utf-8",
            )
            result = delivery.validate_data(delivery.load_json(data_path))
            delivery.compare_artifacts(delivery.load_json(data_path), md_path, xlsx_path, result)
            self.assertTrue(any("旧列名" in item for item in result.errors))

    def test_markdown_cell_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data_path, md_path, xlsx_path = (
                root / "sample.shot_data.json",
                root / "sample.md",
                root / "sample.xlsx",
            )
            data_path.write_text(json.dumps(valid_data(), ensure_ascii=False), encoding="utf-8")
            self.assertEqual(
                0,
                delivery.run_build(
                    type("Args", (), {"data": data_path, "markdown": md_path, "excel": xlsx_path})()
                ),
            )
            md_path.write_text(
                md_path.read_text(encoding="utf-8").replace(
                    "三人踩过碎石和枯叶进入密林",
                    "错误改写",
                    1,
                ),
                encoding="utf-8",
            )
            result = delivery.validate_data(delivery.load_json(data_path))
            delivery.compare_artifacts(delivery.load_json(data_path), md_path, xlsx_path, result)
            self.assertTrue(any("Markdown 第1行第5列" in item for item in result.errors))

    def test_excel_mismatch_and_corruption_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data_path, md_path, xlsx_path = (
                root / "sample.shot_data.json",
                root / "sample.md",
                root / "sample.xlsx",
            )
            data_path.write_text(json.dumps(valid_data(), ensure_ascii=False), encoding="utf-8")
            code = delivery.run_build(
                type("Args", (), {"data": data_path, "markdown": md_path, "excel": xlsx_path})()
            )
            self.assertEqual(0, code)
            _, load_workbook, _, _, _, _ = delivery.openpyxl_modules()
            workbook = load_workbook(xlsx_path)
            workbook["分镜表"]["B2"] = "错误场景"
            workbook.save(xlsx_path)
            result = delivery.validate_data(delivery.load_json(data_path))
            delivery.compare_artifacts(delivery.load_json(data_path), md_path, xlsx_path, result)
            self.assertTrue(any("Excel 第1行第2列" in item for item in result.errors))

            xlsx_path.write_bytes(b"not an xlsx")
            result = delivery.validate_data(delivery.load_json(data_path))
            delivery.compare_artifacts(delivery.load_json(data_path), md_path, xlsx_path, result)
            self.assertTrue(any("Excel 无法读取" in item for item in result.errors))


if __name__ == "__main__":
    unittest.main()