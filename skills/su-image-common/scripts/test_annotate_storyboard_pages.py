#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw


SCRIPT_PATH = Path(__file__).with_name("annotate_storyboard_pages.py")
PYTHON = Path(sys.executable)


class AnnotateStoryboardPagesTest(unittest.TestCase):
    def test_generate_manifest_and_png(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pages_dir = root / "pages"
            output_dir = root / "annotated-pages"
            pages_dir.mkdir()

            image = Image.new("RGB", (1536, 2736), "white")
            draw = ImageDraw.Draw(image)
            draw.rectangle((90, 110, 1446, 873), outline="black", width=4)
            image.save(pages_dir / "page-001.png")

            data = {
                "shots": [
                    {
                        "shot_no": 1,
                        "scene": "13-1 赤狐岭迷雾深林 日 外",
                        "camera_main_image": "[微俯视, 大全景, 伸缩摇臂缓慢下降]\n【机位逻辑】...",
                    }
                ]
            }
            page_map = {
                "pages": [
                    {
                        "page_no": 1,
                        "layout": "7",
                        "source": "page-001.png",
                        "panels": [
                            {"panel_no": 1, "shot_nos": [1]},
                            {"panel_no": 2, "shot_nos": [1]},
                            {"panel_no": 3, "shot_nos": [1]},
                            {"panel_no": 4, "shot_nos": [1]},
                            {"panel_no": 5, "shot_nos": [1]},
                            {"panel_no": 6, "shot_nos": [1]},
                            {"panel_no": 7, "shot_nos": [1]},
                        ],
                    }
                ]
            }
            data_path = root / "sample.shot_data.json"
            page_map_path = root / "page-map.json"
            data_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            page_map_path.write_text(json.dumps(page_map, ensure_ascii=False, indent=2), encoding="utf-8")

            subprocess.run(
                [
                    str(PYTHON),
                    str(SCRIPT_PATH),
                    "--data",
                    str(data_path),
                    "--page-map",
                    str(page_map_path),
                    "--pages",
                    str(pages_dir),
                    "--output",
                    str(output_dir),
                ],
                check=True,
            )

            annotated = output_dir / "page-001.png"
            manifest = output_dir / "manifest.json"
            self.assertTrue(annotated.exists())
            self.assertTrue(manifest.exists())

            with Image.open(annotated) as output_image:
                self.assertEqual(output_image.size[0], 1536)
                self.assertGreater(output_image.size[1], 2736)

            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(payload["pages"][0]["header"], "13-1 赤狐岭迷雾深林 日 外｜镜头001-001")
            self.assertIn("C1｜微俯视｜大全景｜伸缩摇臂缓慢下降", payload["pages"][0]["panel_labels"]["1"])
            self.assertEqual(payload["skipped_pages"], [])

    def test_skips_not_delivered_page_without_renumbering(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pages_dir = root / "pages"
            output_dir = root / "annotated-pages"
            pages_dir.mkdir()

            image = Image.new("RGB", (1536, 2736), "white")
            image.save(pages_dir / "page-001.png")
            image.save(pages_dir / "page-003.png")

            data = {
                "shots": [
                    {
                        "shot_no": 1,
                        "scene": "13-1 赤狐岭迷雾深林 日 外",
                        "camera_main_image": "[微俯视, 大全景, 伸缩摇臂缓慢下降]\n【机位逻辑】...",
                    }
                ]
            }
            delivered_panels = [{"panel_no": index, "shot_nos": [1]} for index in range(1, 10)]
            page_map = {
                "pages": [
                    {"page_no": 1, "layout": "9", "source": "page-001.png", "panels": delivered_panels},
                    {
                        "page_no": 2,
                        "layout": "9",
                        "source": "page-002.png",
                        "status": "not_delivered",
                        "reason": "F-CONVERGE",
                        "panels": delivered_panels,
                    },
                    {"page_no": 3, "layout": "9", "source": "page-003.png", "panels": delivered_panels},
                ]
            }
            data_path = root / "sample.shot_data.json"
            page_map_path = root / "page-map.json"
            data_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            page_map_path.write_text(json.dumps(page_map, ensure_ascii=False, indent=2), encoding="utf-8")

            subprocess.run(
                [
                    str(PYTHON),
                    str(SCRIPT_PATH),
                    "--data",
                    str(data_path),
                    "--page-map",
                    str(page_map_path),
                    "--pages",
                    str(pages_dir),
                    "--output",
                    str(output_dir),
                ],
                check=True,
            )

            self.assertTrue((output_dir / "page-001.png").exists())
            self.assertFalse((output_dir / "page-002.png").exists())
            self.assertTrue((output_dir / "page-003.png").exists())
            payload = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual([page["page_no"] for page in payload["pages"]], [1, 3])
            self.assertEqual(payload["skipped_pages"], [{"page_no": 2, "reason": "F-CONVERGE"}])

    def test_labels_use_source_shot_numbers_and_detect_grid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pages_dir = root / "pages"
            output_dir = root / "annotated-pages"
            pages_dir.mkdir()

            image = Image.new("RGB", (900, 600), "white")
            draw = ImageDraw.Draw(image)
            panel_width = 260
            panel_height = 146
            gutter_x = 30
            gutter_y = 30
            start_x = 20
            start_y = 20
            for row in range(3):
                for col in range(3):
                    left = start_x + col * (panel_width + gutter_x)
                    top = start_y + row * (panel_height + gutter_y)
                    draw.rectangle((left, top, left + panel_width, top + panel_height), outline="black", width=4)
            image.save(pages_dir / "PAGE-02.png")

            data = {
                "shots": [
                    {
                        "shot_no": shot_no,
                        "scene": "14-1 地下通道 日 内",
                        "camera_main_image": "[平视, 中景, 固定镜头]\n【机位逻辑】...",
                    }
                    for shot_no in range(10, 19)
                ]
            }
            page_map = {
                "pages": [
                    {
                        "page_no": 2,
                        "layout": "9",
                        "source": "PAGE-02.png",
                        "panels": [
                            {"panel_no": panel_no, "shot_nos": [shot_no]}
                            for panel_no, shot_no in enumerate(range(10, 19), 1)
                        ],
                    }
                ]
            }
            data_path = root / "sample.shot_data.json"
            page_map_path = root / "page-map.json"
            data_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            page_map_path.write_text(json.dumps(page_map, ensure_ascii=False, indent=2), encoding="utf-8")

            subprocess.run(
                [
                    str(PYTHON),
                    str(SCRIPT_PATH),
                    "--data",
                    str(data_path),
                    "--page-map",
                    str(page_map_path),
                    "--pages",
                    str(pages_dir),
                    "--output",
                    str(output_dir),
                ],
                check=True,
            )

            payload = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
            page = payload["pages"][0]
            self.assertTrue(page["panel_labels"]["1"].startswith("C10｜"))
            self.assertTrue(page["panel_labels"]["9"].startswith("C18｜"))
            self.assertEqual(page["box_detection"], "detected_image_grid")
            self.assertEqual(page["warnings"], [])


if __name__ == "__main__":
    unittest.main()
