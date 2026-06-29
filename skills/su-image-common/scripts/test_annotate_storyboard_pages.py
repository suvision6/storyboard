#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw


SCRIPT_PATH = Path(__file__).with_name("annotate_storyboard_pages.py")
PYTHON = Path("/Users/suvision/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3")


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


if __name__ == "__main__":
    unittest.main()
