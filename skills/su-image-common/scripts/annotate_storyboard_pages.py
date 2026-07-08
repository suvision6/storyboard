#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from PIL import Image, ImageDraw, ImageFont


TRIAD_RE = re.compile(r"^\s*\[([^\]]+)\]")
DEFAULT_FONT_CANDIDATES = (
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
)


@dataclass
class PanelSpec:
    panel_no: int
    shot_nos: List[int]
    box: Optional[Tuple[int, int, int, int]] = None


@dataclass
class PageSpec:
    page_no: int
    layout: str
    source: str
    panels: List[PanelSpec]
    header: Optional[str] = None
    status: str = "delivered"
    reason: str = ""


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def dump_json(path: Path, data: dict) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Add Chinese header and panel labels to text-free storyboard pages."
    )
    parser.add_argument("--data", required=True, help="Path to shot_data.json")
    parser.add_argument("--page-map", required=True, help="Path to page map json")
    parser.add_argument("--pages", required=True, help="Directory containing source PNG pages")
    parser.add_argument("--output", required=True, help="Directory for annotated PNG pages")
    parser.add_argument("--font-path", help="Optional font file path for Chinese text")
    parser.add_argument("--font-size", type=int, default=28)
    parser.add_argument("--header-height", type=int, default=78)
    parser.add_argument("--label-height", type=int, default=62)
    parser.add_argument("--header-padding-x", type=int, default=28)
    parser.add_argument("--text-color", default="#111111")
    parser.add_argument("--background-color", default="#FFFFFF")
    return parser.parse_args()


def normalize_layout(value: str) -> str:
    text = str(value).strip().lower()
    if text in {"7", "su-image7", "image7"}:
        return "7"
    if text in {"9", "su-image9", "image9"}:
        return "9"
    raise ValueError(f"Unsupported layout: {value}")


def expected_panels(layout: str) -> int:
    return 7 if layout == "7" else 9


def row_panel_groups(layout: str) -> List[List[int]]:
    if layout == "7":
        return [[1], [2, 3], [4, 5], [6, 7]]
    return [[1, 2, 3], [4, 5, 6], [7, 8, 9]]


def parse_box(raw: object) -> Tuple[int, int, int, int]:
    if isinstance(raw, dict):
        x = int(raw["x"])
        y = int(raw["y"])
        width = int(raw["width"])
        height = int(raw["height"])
    elif isinstance(raw, Sequence) and len(raw) == 4:
        x = int(raw[0])
        y = int(raw[1])
        width = int(raw[2])
        height = int(raw[3])
    else:
        raise ValueError(f"Invalid box payload: {raw!r}")
    return (x, y, x + width, y + height)


def load_page_specs(page_map: dict) -> List[PageSpec]:
    pages = page_map.get("pages")
    if not isinstance(pages, list) or not pages:
        raise ValueError("page_map.pages must be a non-empty array.")
    result: List[PageSpec] = []
    for item in pages:
        if not isinstance(item, dict):
            raise ValueError("Each page_map.pages item must be an object.")
        layout = normalize_layout(item.get("layout"))
        panels_raw = item.get("panels")
        if not isinstance(panels_raw, list) or not panels_raw:
            raise ValueError("Each page_map page must include non-empty panels.")
        panels: List[PanelSpec] = []
        for raw_panel in panels_raw:
            if not isinstance(raw_panel, dict):
                raise ValueError("Each panel must be an object.")
            shot_nos_raw = raw_panel.get("shot_nos")
            if shot_nos_raw is None and raw_panel.get("shot_no") is not None:
                shot_nos_raw = [raw_panel["shot_no"]]
            if not isinstance(shot_nos_raw, list) or not shot_nos_raw:
                raise ValueError("Each panel must include shot_nos.")
            box = parse_box(raw_panel["box"]) if "box" in raw_panel else None
            panels.append(
                PanelSpec(
                    panel_no=int(raw_panel["panel_no"]),
                    shot_nos=[int(value) for value in shot_nos_raw],
                    box=box,
                )
            )
        result.append(
            PageSpec(
                page_no=int(item["page_no"]),
                layout=layout,
                source=str(item["source"]),
                panels=panels,
                header=item.get("header"),
                status=str(item.get("status", "delivered")),
                reason=str(item.get("reason", "")),
            )
        )
    return result


def select_font(font_path: Optional[str], font_size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [font_path] if font_path else []
    candidates.extend(DEFAULT_FONT_CANDIDATES)
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return ImageFont.truetype(candidate, font_size)
    return ImageFont.load_default()


def parse_triad(camera_main_image: str) -> Tuple[str, str, str]:
    match = TRIAD_RE.search(camera_main_image or "")
    if not match:
        raise ValueError(f"camera_main_image triad missing: {camera_main_image!r}")
    parts = [part.strip() for part in match.group(1).split(",")]
    if len(parts) != 3 or not all(parts):
        raise ValueError(f"camera_main_image triad invalid: {camera_main_image!r}")
    return (parts[0], parts[1], parts[2])


def build_shot_index(data: dict) -> Dict[int, dict]:
    shots = data.get("shots")
    if not isinstance(shots, list):
        raise ValueError("shot_data.json must contain shots array.")
    index: Dict[int, dict] = {}
    for shot in shots:
        if isinstance(shot, dict) and shot.get("shot_no") is not None:
            index[int(shot["shot_no"])] = shot
    return index


def derive_header(page: PageSpec, shot_index: Dict[int, dict]) -> str:
    if page.header:
        return page.header
    shot_nos = sorted({shot_no for panel in page.panels for shot_no in panel.shot_nos})
    first = shot_index[shot_nos[0]]
    scene = str(first.get("scene", "")).strip() or "未命名场景"
    return f"{scene}｜镜头{shot_nos[0]:03d}-{shot_nos[-1]:03d}"


def derive_panel_label(panel: PanelSpec, shot_index: Dict[int, dict]) -> str:
    shot = shot_index[panel.shot_nos[0]]
    angle, shot_size, movement = parse_triad(str(shot.get("camera_main_image", "")))
    return f"C{panel.shot_nos[0]}｜{angle}｜{shot_size}｜{movement}"


def canonical_boxes(layout: str, width: int, height: int) -> Dict[int, Tuple[int, int, int, int]]:
    if layout == "7":
        margin_x = round(width * 0.055)
        top_margin = round(height * 0.045)
        gutter_x = round(width * 0.03)
        gutter_y = round(height * 0.028)
        usable_width = width - margin_x * 2
        panel1_height = round(usable_width * 9 / 16)
        lower_width = (usable_width - gutter_x) // 2
        lower_height = round(lower_width * 9 / 16)
        boxes: Dict[int, Tuple[int, int, int, int]] = {
            1: (margin_x, top_margin, margin_x + usable_width, top_margin + panel1_height)
        }
        for row_index, (left_panel, right_panel) in enumerate(((2, 3), (4, 5), (6, 7)), start=0):
            y = top_margin + panel1_height + gutter_y + row_index * (lower_height + gutter_y)
            left_x = margin_x
            right_x = margin_x + lower_width + gutter_x
            boxes[left_panel] = (left_x, y, left_x + lower_width, y + lower_height)
            boxes[right_panel] = (right_x, y, right_x + lower_width, y + lower_height)
        return boxes
    margin_x = round(width * 0.045)
    margin_y = round(height * 0.06)
    gutter_x = round(width * 0.022)
    gutter_y = round(height * 0.03)
    usable_width = width - margin_x * 2 - gutter_x * 2
    panel_width = usable_width // 3
    panel_height = round(panel_width * 9 / 16)
    boxes = {}
    panel_no = 1
    for row in range(3):
        y = margin_y + row * (panel_height + gutter_y)
        for col in range(3):
            x = margin_x + col * (panel_width + gutter_x)
            boxes[panel_no] = (x, y, x + panel_width, y + panel_height)
            panel_no += 1
    return boxes


def cluster_positions(positions: List[int]) -> List[int]:
    if not positions:
        return []
    clusters: List[List[int]] = [[positions[0]]]
    for position in positions[1:]:
        if position <= clusters[-1][-1] + 2:
            clusters[-1].append(position)
        else:
            clusters.append([position])
    return [round(sum(cluster) / len(cluster)) for cluster in clusters]


def dark_line_positions(image: Image.Image, axis: str) -> List[int]:
    grayscale = image.convert("L")
    width, height = grayscale.size
    pixels = grayscale.load()
    positions: List[int] = []
    threshold = 72
    min_fraction = 0.12
    if axis == "x":
        for x in range(width):
            dark = sum(1 for y in range(height) if pixels[x, y] < threshold)
            if dark / height >= min_fraction:
                positions.append(x)
        return cluster_positions(positions)
    for y in range(height):
        dark = sum(1 for x in range(width) if pixels[x, y] < threshold)
        if dark / width >= min_fraction:
            positions.append(y)
    return cluster_positions(positions)


def select_grid_lines(lines: List[int], expected: int, min_gap: int) -> List[int]:
    filtered: List[int] = []
    for line in lines:
        if not filtered or line - filtered[-1] >= min_gap:
            filtered.append(line)
        elif abs(line - filtered[-1]) <= min_gap:
            filtered[-1] = round((filtered[-1] + line) / 2)
    if len(filtered) < expected:
        return []
    if len(filtered) == expected:
        return filtered
    best: List[int] = []
    best_span = -1
    for start in range(0, len(filtered) - expected + 1):
        candidate = filtered[start : start + expected]
        span = candidate[-1] - candidate[0]
        if span > best_span:
            best = candidate
            best_span = span
    return best


def detect_nine_panel_boxes(image: Image.Image) -> Tuple[Optional[Dict[int, Tuple[int, int, int, int]]], List[str]]:
    width, height = image.size
    x_lines = select_grid_lines(dark_line_positions(image, "x"), 6, max(4, round(width * 0.006)))
    y_lines = select_grid_lines(dark_line_positions(image, "y"), 6, max(4, round(height * 0.006)))
    warnings: List[str] = []
    if len(x_lines) != 6 or len(y_lines) != 6:
        warnings.append("actual_grid_detection_failed; canonical_boxes_used")
        return None, warnings
    boxes: Dict[int, Tuple[int, int, int, int]] = {}
    panel_no = 1
    for row in range(3):
        top = y_lines[row * 2]
        bottom = y_lines[row * 2 + 1]
        for col in range(3):
            left = x_lines[col * 2]
            right = x_lines[col * 2 + 1]
            if right <= left or bottom <= top:
                warnings.append("actual_grid_detection_invalid_geometry; canonical_boxes_used")
                return None, warnings
            boxes[panel_no] = (left, top, right, bottom)
            panel_no += 1
    return boxes, warnings


def resolve_panel_boxes(page: PageSpec, image: Image.Image) -> Tuple[Dict[int, Tuple[int, int, int, int]], str, List[str]]:
    width, height = image.size
    explicit_boxes = {panel.panel_no: panel.box for panel in page.panels if panel.box is not None}
    if len(explicit_boxes) == len(page.panels):
        return {panel.panel_no: panel.box for panel in page.panels if panel.box is not None}, "explicit_page_map_boxes", []
    if page.layout == "9":
        detected, warnings = detect_nine_panel_boxes(image)
        if detected:
            return detected, "detected_image_grid", warnings
        default_boxes = canonical_boxes(page.layout, width, height)
        return default_boxes, "canonical_fallback", warnings
    default_boxes = canonical_boxes(page.layout, width, height)
    return default_boxes, "canonical_layout", ["actual_grid_detection_not_supported_for_layout_7; canonical_boxes_used"]


def validate_panels(page: PageSpec) -> None:
    expected = expected_panels(page.layout)
    panel_nos = sorted(panel.panel_no for panel in page.panels)
    if panel_nos != list(range(1, expected + 1)):
        raise ValueError(
            f"Page {page.page_no} panels must be exactly 1..{expected}; got {panel_nos}."
        )


def measure_centered_text(draw: ImageDraw.ImageDraw, box: Tuple[int, int, int, int], text: str, font: ImageFont.ImageFont) -> Tuple[float, float]:
    left, top, right, bottom = box
    text_box = draw.textbbox((0, 0), text, font=font)
    text_width = text_box[2] - text_box[0]
    text_height = text_box[3] - text_box[1]
    x = left + (right - left - text_width) / 2
    y = top + (bottom - top - text_height) / 2
    return x, y


def render_page(
    page: PageSpec,
    source_path: Path,
    output_path: Path,
    shot_index: Dict[int, dict],
    font: ImageFont.ImageFont,
    header_height: int,
    label_height: int,
    header_padding_x: int,
    text_color: str,
    background_color: str,
) -> dict:
    validate_panels(page)
    image = Image.open(source_path).convert("RGB")
    width, height = image.size
    panel_boxes, box_detection, warnings = resolve_panel_boxes(page, image)
    rows = row_panel_groups(page.layout)
    row_tops = [min(panel_boxes[panel_no][1] for panel_no in row) for row in rows]
    row_bottoms = [max(panel_boxes[panel_no][3] for panel_no in row) for row in rows]

    new_height = height + header_height + label_height * len(rows)
    canvas = Image.new("RGB", (width, new_height), background_color)
    draw = ImageDraw.Draw(canvas)

    header_text = derive_header(page, shot_index)
    current_src_y = 0
    current_dst_y = header_height
    adjusted_boxes: Dict[int, Tuple[int, int, int, int]] = {}
    label_bands: Dict[int, Tuple[int, int, int, int]] = {}

    for row_index, row in enumerate(rows):
        row_top = row_tops[row_index]
        row_bottom = row_bottoms[row_index]
        if row_top > current_src_y:
            strip = image.crop((0, current_src_y, width, row_top))
            canvas.paste(strip, (0, current_dst_y))
            current_dst_y += row_top - current_src_y
        strip = image.crop((0, row_top, width, row_bottom))
        canvas.paste(strip, (0, current_dst_y))
        delta_y = current_dst_y - row_top
        for panel_no in row:
            left, top, right, bottom = panel_boxes[panel_no]
            adjusted_boxes[panel_no] = (left, top + delta_y, right, bottom + delta_y)
        label_bands[row_index] = (0, current_dst_y + (row_bottom - row_top), width, current_dst_y + (row_bottom - row_top) + label_height)
        current_dst_y += (row_bottom - row_top) + label_height
        current_src_y = row_bottom
    if current_src_y < height:
        strip = image.crop((0, current_src_y, width, height))
        canvas.paste(strip, (0, current_dst_y))

    draw.rectangle((0, 0, width, header_height), fill=background_color)
    header_x, header_y = measure_centered_text(
        draw,
        (header_padding_x, 0, width - header_padding_x, header_height),
        header_text,
        font,
    )
    draw.text((header_x, header_y), header_text, fill=text_color, font=font)

    for row_index, row in enumerate(rows):
        label_band = label_bands[row_index]
        for panel_no in row:
            label = derive_panel_label(next(panel for panel in page.panels if panel.panel_no == panel_no), shot_index)
            left, _, right, _ = adjusted_boxes[panel_no]
            x, y = measure_centered_text(draw, (left, label_band[1], right, label_band[3]), label, font)
            draw.text((x, y), label, fill=text_color, font=font)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path)
    return {
        "page_no": page.page_no,
        "layout": page.layout,
        "source": str(source_path),
        "output": str(output_path),
        "header": header_text,
        "box_detection": box_detection,
        "warnings": warnings,
        "panel_labels": {str(panel.panel_no): derive_panel_label(panel, shot_index) for panel in page.panels},
    }


def main() -> int:
    args = parse_args()
    data_path = Path(args.data).resolve()
    page_map_path = Path(args.page_map).resolve()
    pages_dir = Path(args.pages).resolve()
    output_dir = Path(args.output).resolve()

    shot_index = build_shot_index(load_json(data_path))
    page_specs = load_page_specs(load_json(page_map_path))
    font = select_font(args.font_path, args.font_size)

    manifest = {"pages": [], "skipped_pages": []}
    for page in page_specs:
        if page.status == "not_delivered":
            manifest["skipped_pages"].append(
                {
                    "page_no": page.page_no,
                    "reason": page.reason or "not_delivered",
                }
            )
            continue
        for panel in page.panels:
            for shot_no in panel.shot_nos:
                if shot_no not in shot_index:
                    raise ValueError(f"Shot {shot_no} referenced by page {page.page_no} not found in shot_data.")
        source_path = Path(page.source)
        if not source_path.is_absolute():
            source_path = pages_dir / source_path
        output_path = output_dir / source_path.name
        manifest["pages"].append(
            render_page(
                page=page,
                source_path=source_path,
                output_path=output_path,
                shot_index=shot_index,
                font=font,
                header_height=args.header_height,
                label_height=args.label_height,
                header_padding_x=args.header_padding_x,
                text_color=args.text_color,
                background_color=args.background_color,
            )
        )
    dump_json(output_dir / "manifest.json", manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
