#!/usr/bin/env python3
"""Validator/compiler for su-image9 v2.0.1 final prompts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

CANON_VERSION = "2.0.1"

SYSTEM_STYLE_LAYER = """SYSTEM_STYLE_LAYER:
This entire generation must follow a single unified storyboard production style.

STYLE ANCHOR:
Treat this as a single cohesive storyboard drawn by one graphite storyboard artist in a single production session. For batch generation, all outputs must match the same storyboard artist, same production session, same medium, same stroke weight, same shading density, and same unfinished storyboard look.

MEDIUM:
Monochrome graphite storyboard / pencil pre-visualization drawing only. Hand-drawn pencil / graphite sketch only. Production storyboard sheet. Animatic frame design. Non-painting, non-rendered, non-illustration.

LINE RULE:
Thin graphite linework only. Visible sketch strokes allowed. Construction lines allowed. Rough drafting lines allowed. No inked comic outlines. No polished clean manga line art.

SHADING RULE:
Light hatching only. Mid-gray tonal range. Controlled medium contrast only. No pure black fill blocks. No heavy ink fill. No painterly shading. No soft airbrush gradients.

TEXTURE RULE:
Paper-like sketch texture. Slightly rough graphite grain. High-frequency pencil texture. Unfinished production drawing aesthetic.

RENDERING RULE:
No digital painting, no photorealism, no CGI, no cinematic lighting, no bloom, no HDR lighting, no volumetric god rays, no depth-of-field blur, no airbrush gradients, no rendered concept art look.

CONSISTENCY RULE:
All 9 panels must share identical drawing style, graphite medium, stroke weight, shading density, texture grain, tonal range, and rendering restraint. No stylistic variation between panels is allowed."""

GEOMETRY_BLUEPRINT = """Strict panel geometry blueprint, mandatory before drawing:
Treat the final canvas as a clean wide horizontal 16:9 layout.
Draw exactly nine separate straight rectangular panel frames with visible gutters.
Arrange the 9 panels in a clean 3x3 storyboard grid: three equal columns and three equal rows.
All 9 panels must have the same width, the same height, the same 16:9 aspect ratio, and aligned edges.
Each panel frame must remain a flat horizontal 16:9 rectangle.
Do not let any panel become square, vertical, tall, narrow, compressed, stretched, trapezoid, diagonal, rounded, or irregular.
Keep gutters and margins as empty separating space. If a close-up needs more room, use empty background or negative space inside that panel; never change the panel shape or aspect ratio.
Do not create 3:2, 4:3, A4, square, vertical, mixed-size, manga, comic, collage, or poster layouts.
Do not create a manga page, comic page, dynamic collage, masonry grid, mixed panel sizes, tilted frames, perspective-distorted frames, overlapping panels, or a poster composition.
The content inside a panel may crop or zoom, but the panel frame itself must remain a flat horizontal 16:9 rectangle.
Geometry correctness does not replace the SYSTEM_STYLE_LAYER. The 3x3 grid must remain geometrically strict while all panel contents remain in the same monochrome graphite storyboard production style."""

HARD_PHRASES = """Generate one wide horizontal 16:9 canvas containing a clean 3x3 storyboard grid.
Each of the 9 panels must also be a horizontal 16:9 storyboard frame.
Panel 1 is the master spatial layout anchor for the entire 3x3 grid.
All Panels 2-9 must be derived from the same Panel 1 layout.
Do not redesign the room, exterior location, furniture footprint, terrain, road, doorway, vehicle position, or object positions in later panels.
Do not generate any text, labels, captions, panel numbers, scene headers, shot numbers, subtitles, arrows, or watermarks inside the image."""

NEGATIVE_CONSTRAINTS = """NEGATIVE_CONSTRAINTS:
No photorealism, no film still look, no realistic skin texture, no cinematic lighting, no cinematic grading, no HDR lighting, no bloom, no volumetric god rays, no depth-of-field blur, no CGI, no 3D render, no digital painting, no digital illustration look, no rendered concept art, no polished illustration, no watercolor, no oil painting, no painterly shading, no soft airbrush gradients, no anime rendering, no manga page, no comic page layout, no inked comic outlines, no clean manga line art, no dynamic collage, no masonry grid, no poster composition, no color, no pure black fill blocks, no heavy ink fill, no text inside the image, no labels, no subtitles, no arrows, no watermarks, no square panels, no vertical panels, no tall panels, no narrow panels, no mixed-size panels."""

EXPECTED_CANON_TEXTS = {
    "SYSTEM_STYLE_LAYER": SYSTEM_STYLE_LAYER,
    "GEOMETRY_BLUEPRINT": GEOMETRY_BLUEPRINT,
    "HARD_PHRASES": HARD_PHRASES,
    "NEGATIVE_CONSTRAINTS": NEGATIVE_CONSTRAINTS,
}
FACTORY_HASHES = {name: hashlib.sha256(text.encode("utf-8")).hexdigest() for name, text in EXPECTED_CANON_TEXTS.items()}

LAYER_ORDER = [
    "DELIVERABLE",
    "SYSTEM_STYLE_LAYER",
    "SCENE_LAYER",
    "CAMERA_RULE_LAYER",
    "CONTINUITY_LAYER",
    "REFERENCE_OR_TEXT",
    "PANEL_1_MASTER_SPATIAL_LAYOUT_ANCHOR",
    "DOOR_WINDOW_FURNITURE_GEOMETRY_LOCK",
    "VEHICLE_AND_AXIS_LOCKS",
    "OBJECT_VISIBILITY_AND_BOUNDARIES",
    "PANEL_LAYER",
    "NEGATIVE_CONSTRAINTS",
]
LAYER_HEADINGS = {
    "DELIVERABLE",
    "SYSTEM_STYLE_LAYER",
    "SCENE_LAYER",
    "CAMERA_RULE_LAYER",
    "CONTINUITY_LAYER",
    "REFERENCE_USAGE",
    "TEXT_DERIVED_LAYOUT",
    "PANEL_1_MASTER_SPATIAL_LAYOUT_ANCHOR",
    "DOOR_WINDOW_FURNITURE_GEOMETRY_LOCK",
    "VEHICLE_AND_AXIS_LOCKS",
    "OBJECT_VISIBILITY_AND_BOUNDARIES",
    "PANEL_LAYER PANEL-1 to PANEL-9",
    "NEGATIVE_CONSTRAINTS",
}
RENDER_HEADINGS = {
    "REFERENCE_USAGE": "REFERENCE_USAGE",
    "TEXT_DERIVED_LAYOUT": "TEXT_DERIVED_LAYOUT",
    "PANEL_LAYER": "PANEL_LAYER PANEL-1 to PANEL-9",
}
MACHINE_PANEL_FIELDS = [
    "source_shot",
    "shot_data_camera_tag",
    "drawn_camera_tag",
    "visible_only",
    "action_composition",
    "floor_axis_delta",
    "prop_state",
    "distance_stage_lock",
]
FIELD_SKELETON_PATTERNS = [
    r"\bSOURCE SHOT\b",
    r"\bMUST MATCH SHOT_DATA CAMERA TAG\b",
    r"\bDRAWN CAMERA TAG\b",
    r"\bVISIBLE ONLY\b",
    r"\bACTION / COMPOSITION\b",
    r"\bFLOOR / AXIS DELTA\b",
    r"\bPROP STATE\b",
    r"\bPANEL_TASKS\b",
    r"\bSTYLE_LOCK\b",
    r"\bCANVAS_LOCK\b",
    r"\bNEGATIVE_LOCK\b",
]
FORBIDDEN_STYLE_TOKENS = [
    "cinematic lighting",
    "anime rendering",
    "digital painting",
    "photorealistic",
    "photorealism",
    "concept art",
    "watercolor",
    "oil painting",
    "cgi render",
    "3d render",
]
POSITIVE_ANCHOR = {"master", "establishing", "wide", "full", "全景", "大远景"}
NEGATIVE_ANCHOR = {"close", "close-up", "medium", "over-shoulder", "ots", "insert", "pov", "reaction", "black", "特写", "近景", "中景", "过肩", "反应", "黑场"}
DISTANCE_ENDPOINT_TERMS = [
    "两步远",
    "一步远",
    "走上前",
    "上前",
    "靠近",
    "贴近",
    "退后",
    "扑上去",
    "跪到",
    "跪在",
    "走到",
    "停在",
    "steps away",
    "two steps",
    "walks forward",
    "moves closer",
    "approaches",
    "stops near",
    "kneels before",
    "rushes toward",
]
PRE_DISTANCE_LOCK_TERMS = [
    "未靠近",
    "尚未靠近",
    "保持距离",
    "位移前",
    "前序距离",
    "可见空地",
    "通道纵深",
    "不要提前",
    "属于后序",
    "pre-approach",
    "not yet",
    "before the approach",
    "keeps distance",
    "visible empty",
    "empty floor",
    "do not place",
    "belongs to panel",
]


@dataclass
class Finding:
    check: str
    severity: str
    field: str
    token: str = ""
    context: str = ""


@dataclass
class PanelText:
    name: str
    text: str


@dataclass
class Page:
    name: str
    text: str
    layers: dict[str, str] = field(default_factory=dict)
    layer_headings: dict[str, str] = field(default_factory=dict)
    panels: list[PanelText] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    canon_autofixed: bool = False
    char_count: int = 0
    budget_status: str = "pass"


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text).replace("\r\n", "\n").strip()


def sha256_text(text: str) -> str:
    return hashlib.sha256(nfc(text).encode("utf-8")).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def issue(check: str, severity: str, field: str, token: str = "", context: str = "") -> Finding:
    return Finding(check, severity, field, str(token), str(context)[:260])


def normalize_for_compare(text: str) -> str:
    return re.sub(r"\s+", " ", nfc(text)).strip()


def strip_own_heading(name: str, body: str) -> str:
    body = nfc(body)
    heading = RENDER_HEADINGS.get(name, name)
    if body == heading + ":":
        return ""
    if body.startswith(heading + ":\n"):
        return body.split("\n", 1)[1].strip()
    return body


def canonical_layer_text(name: str, body: str) -> str:
    heading = RENDER_HEADINGS.get(name, name)
    clean_body = strip_own_heading(name, body)
    return f"{heading}:\n{clean_body}".strip()


def extract_canon(path: Path | None) -> tuple[str, dict[str, str], dict[str, str]]:
    if path is None or not path.exists():
        return CANON_VERSION, EXPECTED_CANON_TEXTS.copy(), FACTORY_HASHES.copy()
    text = path.read_text(encoding="utf-8")
    version_match = re.search(r"<!--\s*canon-version:\s*([^\s]+)\s*-->", text)
    version = version_match.group(1) if version_match else "unknown"
    blocks: dict[str, str] = {}
    for match in re.finditer(r"(?ms)^###\s+canon:([A-Z_]+)\s*\n\s*```text\s*\n(.*?)\n```", text):
        blocks[match.group(1).strip()] = nfc(match.group(2))
    for name, expected in EXPECTED_CANON_TEXTS.items():
        blocks.setdefault(name, expected)
    hashes = {name: sha256_text(value) for name, value in blocks.items()}
    return version, blocks, hashes


def split_pages(text: str) -> list[Page]:
    text = nfc(text)
    matches = list(re.finditer(r"(?m)^#\s+(PAGE-\d{2})\b.*$", text))
    if not matches:
        return [Page("PAGE-01", text)]
    pages: list[Page] = []
    for idx, match in enumerate(matches):
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        pages.append(Page(match.group(1), text[match.end():end].strip()))
    return pages


def normalize_layer_name(raw: str) -> str:
    if raw == "PANEL_LAYER PANEL-1 to PANEL-9":
        return "PANEL_LAYER"
    if raw in {"REFERENCE_USAGE", "TEXT_DERIVED_LAYOUT"}:
        return "REFERENCE_OR_TEXT"
    return raw


def parse_layers(page: Page) -> None:
    heading_alt = "|".join(re.escape(item) for item in sorted(LAYER_HEADINGS, key=len, reverse=True))
    headers = list(re.finditer(rf"(?m)^({heading_alt}):\s*$", page.text))
    layers: dict[str, str] = {}
    layer_headings: dict[str, str] = {}
    for idx, header in enumerate(headers):
        raw = header.group(1)
        name = normalize_layer_name(raw)
        end = headers[idx + 1].start() if idx + 1 < len(headers) else len(page.text)
        layers[name] = page.text[header.end():end].strip()
        layer_headings[name] = raw
    page.layers = layers
    page.layer_headings = layer_headings


def parse_panel_layer(page: Page) -> None:
    panel_layer = page.layers.get("PANEL_LAYER", "")
    panels: list[PanelText] = []
    matches = list(re.finditer(r"(?ms)^PANEL-(\d+):\s*(.*?)(?=^PANEL-\d+:\s*|\Z)", panel_layer))
    for match in matches:
        panels.append(PanelText(f"PANEL-{int(match.group(1))}", match.group(2).strip()))
    page.panels = panels


def replace_canon_markers(page: Page, layer_name: str, body: str, canon_blocks: dict[str, str]) -> str:
    def repl(match: re.Match[str]) -> str:
        canon_name = match.group(1)
        if canon_name not in canon_blocks:
            page.findings.append(issue("G0-02", "fail", f"{page.name}/{layer_name}", canon_name, "unknown canon marker"))
            return match.group(0)
        replacement = canon_blocks[canon_name]
        if canon_name == layer_name:
            return strip_own_heading(layer_name, replacement)
        return replacement

    return re.sub(r"@CANON\(([A-Z_]+)\)", repl, body)


def render_page(page: Page) -> str:
    parts = [f"# {page.name}"]
    for name in LAYER_ORDER:
        if name == "REFERENCE_OR_TEXT":
            if name in page.layers:
                heading = page.layer_headings.get(name, "TEXT_DERIVED_LAYOUT")
                parts.append(f"{heading}:\n{page.layers[name]}")
            continue
        if name in page.layers:
            heading = RENDER_HEADINGS.get(name, name)
            parts.append(f"{heading}:\n{page.layers[name]}")
    return "\n\n".join(parts).strip()


def compile_pages(pages: list[Page], canon_blocks: dict[str, str], strict_canon: bool) -> str:
    for page in pages:
        parse_layers(page)
        for required in LAYER_ORDER:
            if required == "REFERENCE_OR_TEXT":
                if required not in page.layers:
                    page.findings.append(issue("G0-01", "fail", page.name, "REFERENCE_USAGE or TEXT_DERIVED_LAYOUT", "required layer missing"))
                continue
            if required not in page.layers:
                page.findings.append(issue("G0-01", "fail", page.name, required, "required layer missing"))
        for name, body in list(page.layers.items()):
            page.layers[name] = replace_canon_markers(page, name, body, canon_blocks)
        for name in ["SYSTEM_STYLE_LAYER", "NEGATIVE_CONSTRAINTS"]:
            if name not in page.layers:
                continue
            expected = canon_blocks.get(name, EXPECTED_CANON_TEXTS[name])
            actual_full = canonical_layer_text(name, page.layers[name])
            if normalize_for_compare(actual_full) != normalize_for_compare(expected):
                if strict_canon:
                    page.findings.append(issue("G0-02", "fail", f"{page.name}/{name}", name, "canon block differs under --strict-canon"))
                else:
                    page.layers[name] = strip_own_heading(name, expected)
                    page.canon_autofixed = True
                    page.findings.append(issue("G0-02", "warn", f"{page.name}/{name}", name, "canon_autofixed=true"))
        parse_panel_layer(page)
    return "\n\n".join(render_page(page) for page in pages).strip() + "\n"


def codepoint_len(text: str) -> int:
    return len(nfc(text))


def compiled_page_text(page: Page) -> str:
    return render_page(page)


def require_text(page: Page, text: str, source: str, check: str = "G0-04") -> None:
    page_text = compiled_page_text(page)
    if normalize_for_compare(text) not in normalize_for_compare(page_text):
        page.findings.append(issue(check, "fail", f"{page.name}/{source}", "missing", "required v2.0.1 generation-layer text missing"))


def validate_layer_presence(page: Page) -> None:
    for line in HARD_PHRASES.splitlines():
        require_text(page, line, "HARD_PHRASES")
    for line in GEOMETRY_BLUEPRINT.splitlines():
        require_text(page, line, "GEOMETRY_BLUEPRINT")
    require_text(page, SYSTEM_STYLE_LAYER, "SYSTEM_STYLE_LAYER")
    require_text(page, NEGATIVE_CONSTRAINTS, "NEGATIVE_CONSTRAINTS")
    system_pos = compiled_page_text(page).find("SYSTEM_STYLE_LAYER:")
    panel_pos = compiled_page_text(page).find("PANEL_LAYER PANEL-1 to PANEL-9:")
    if system_pos == -1 or panel_pos == -1 or system_pos > panel_pos:
        page.findings.append(issue("G0-04", "fail", page.name, "SYSTEM_STYLE_LAYER", "style layer must appear before PANEL_LAYER"))


def scan_forbidden_style(text: str, page: Page, field: str) -> None:
    lower = text.lower()
    for token in FORBIDDEN_STYLE_TOKENS:
        if token in lower:
            page.findings.append(issue("G0-08", "fail", field, token, "forbidden independent style definition"))


def scan_panel_text(page: Page) -> None:
    if len(page.panels) != 9:
        page.findings.append(issue("G0-06", "fail", page.name, str(len(page.panels)), "PANEL_LAYER must contain exactly 9 panels"))
    seen = {panel.name for panel in page.panels}
    for index in range(1, 10):
        if f"PANEL-{index}" not in seen:
            page.findings.append(issue("G0-06", "fail", page.name, f"PANEL-{index}", "panel missing"))
    for panel in page.panels:
        text = panel.text.strip()
        field = f"{page.name}/{panel.name}"
        if len(re.findall(r"[A-Za-z\u4e00-\u9fff]+", text)) < 6:
            page.findings.append(issue("G0-06", "fail", field, "too_short", "panel must be a natural-language visual description"))
        for pattern in FIELD_SKELETON_PATTERNS:
            if re.search(pattern, text, re.I):
                page.findings.append(issue("G0-07", "fail", field, pattern, "validator or machine-track wording leaked into PANEL_LAYER"))
        if re.search(r"\b[A-Za-z][A-Za-z0-9_-]*\s*=\s*[^.;,\n]+", text):
            page.findings.append(issue("G0-07", "fail", field, "key=value", "PANEL_LAYER must not use telegraphic key=value fields"))
        if re.search(r"\bprops\s*=\s*(yes|no|true|false|present|absent)\b", text, re.I):
            page.findings.append(issue("G0-09", "fail", field, "props boolean", "boolean prop compression is forbidden"))
        scan_forbidden_style(text, page, field)


def plan_pages(panel_plan: dict[str, Any]) -> list[dict[str, Any]]:
    pages = panel_plan.get("pages")
    return pages if isinstance(pages, list) else []


def page_plan_for(page: Page, panel_plan: dict[str, Any]) -> dict[str, Any]:
    target_num = int(re.search(r"(\d+)", page.name).group(1)) if re.search(r"(\d+)", page.name) else 1
    pages = plan_pages(panel_plan)
    if not pages:
        return {}
    for item in pages:
        raw = str(item.get("page", ""))
        m = re.search(r"(\d+)", raw)
        if m and int(m.group(1)) == target_num:
            return item
    return pages[target_num - 1] if target_num - 1 < len(pages) else pages[0]


def panel_plan_items(page_plan: dict[str, Any]) -> list[dict[str, Any]]:
    panels = page_plan.get("panels")
    return panels if isinstance(panels, list) else []


def panel_plan_for(page_plan: dict[str, Any], index: int) -> dict[str, Any]:
    panels = panel_plan_items(page_plan)
    for item in panels:
        raw = str(item.get("panel", item.get("panel_id", "")))
        m = re.search(r"(\d+)", raw)
        if m and int(m.group(1)) == index:
            return item
    return panels[index - 1] if index - 1 < len(panels) else {}


def scan_plan_booleans(value: Any, path: str, findings: list[Finding]) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            scan_plan_booleans(nested, f"{path}.{key}" if path else str(key), findings)
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            scan_plan_booleans(nested, f"{path}[{index}]", findings)
    elif isinstance(value, str):
        if re.search(r"\bprops\s*=\s*(yes|no|true|false|present|absent)\b", value, re.I):
            findings.append(issue("G0-09", "fail", path, "props boolean", "boolean prop compression is forbidden in panel_plan"))


def shot_index(shot_data: dict[str, Any] | None) -> dict[int, dict[str, Any]]:
    result: dict[int, dict[str, Any]] = {}
    if not shot_data:
        return result
    for shot in shot_data.get("shots", []):
        if isinstance(shot, dict) and shot.get("shot_no") is not None:
            result[int(shot["shot_no"])] = shot
    return result


def camera_tag_from_shot(shot: dict[str, Any]) -> str:
    text = str(shot.get("camera_main_image", "")).strip()
    match = re.match(r"\[([^\]]+)\]", text)
    return match.group(1).strip() if match else ""


def normalize_tag_tokens(tag: str) -> set[str]:
    lower = tag.lower()
    tokens = set(re.findall(r"[a-z]+(?:-[a-z]+)?|[\u4e00-\u9fff]+", lower))
    if "close" in tokens and "up" in tokens:
        tokens.add("close-up")
    if "over" in tokens and "shoulder" in tokens:
        tokens.add("over-shoulder")
    return tokens


def source_range_start(page_plan: dict[str, Any], source_numbers: list[int]) -> int | None:
    raw = str(page_plan.get("source_shot_range", "")).strip()
    match = re.match(r"^\s*(\d+)\s*(?:-|–|—|至|到)\s*(\d+)\s*$", raw)
    if match:
        return int(match.group(1))
    return min(source_numbers) if source_numbers else None


def shot_search_text(shot: dict[str, Any]) -> str:
    parts = [
        str(shot.get("camera_main_image", "")),
        str(shot.get("source_paragraph", "")),
        str(shot.get("prompt", "")),
    ]
    return " ".join(parts).lower()


def text_has_any(text: str, terms: list[str]) -> bool:
    lower = text.lower()
    return any(term.lower() in lower for term in terms)


def has_distance_endpoint(shot: dict[str, Any]) -> bool:
    return text_has_any(shot_search_text(shot), DISTANCE_ENDPOINT_TERMS)


def has_pre_distance_lock(panel_plan_item: dict[str, Any], panel_text: str) -> bool:
    text = " ".join(
        [
            str(panel_plan_item.get("distance_stage_lock", "")),
            str(panel_plan_item.get("action_composition", "")),
            panel_text,
        ]
    )
    return text_has_any(text, PRE_DISTANCE_LOCK_TERMS)


def validate_g0(pages: list[Page], compiled_text: str, panel_plan: dict[str, Any]) -> None:
    global_plan_findings: list[Finding] = []
    scan_plan_booleans(panel_plan, "panel_plan", global_plan_findings)
    for page in pages:
        page.char_count = codepoint_len(compiled_page_text(page))
        if page.char_count > 12000:
            page.budget_status = "warn"
            page.findings.append(issue("G0-05", "warn", page.name, str(page.char_count), "page exceeds 12000 codepoints; warn only"))
        else:
            page.budget_status = "pass"
        if "@CANON(" in compiled_page_text(page):
            page.findings.append(issue("G0-03", "fail", page.name, "@CANON(", "canon marker leaked into compiled text"))
        if re.search(r"(?m)^(STYLE_LOCK|CANVAS_LOCK|REFERENCE_LOCK|PANEL_TASKS|NEGATIVE_LOCK):", page.text):
            page.findings.append(issue("G0-10", "fail", page.name, "v1.7.3 structure", "old PANEL_TASKS/canon-lock structure is not allowed for v2.0.1 final prompts"))
        if re.search(r"\bP\d{2}\b", page.text):
            page.findings.append(issue("G0-10", "fail", page.name, "Pxx", "old P01-style naming is not allowed"))
        validate_layer_presence(page)
        scan_forbidden_style(page.layers.get("CONTINUITY_LAYER", ""), page, f"{page.name}/CONTINUITY_LAYER")
        scan_panel_text(page)
        page.findings.extend(global_plan_findings)


def validate_g1(pages: list[Page], panel_plan: dict[str, Any], shot_data: dict[str, Any] | None, mode: str) -> None:
    if mode == "full" and not shot_data:
        pages[0].findings.append(issue("G1-00", "fail", "shot_data", "missing", "full mode requires --shot-data"))
        return
    if mode != "full":
        return
    shots = shot_index(shot_data)
    for page in pages:
        pplan = page_plan_for(page, panel_plan)
        panels = panel_plan_items(pplan)
        source_numbers: list[int] = []
        if len(panels) != 9:
            page.findings.append(issue("G1-01", "fail", f"{page.name}/panel_plan", str(len(panels)), "panel_plan page must contain 9 panels"))
        for index in range(1, 10):
            pp = panel_plan_for(pplan, index)
            if not pp:
                page.findings.append(issue("G1-01", "fail", f"{page.name}/PANEL-{index}", "missing", "panel_plan panel missing"))
                continue
            for field_name in MACHINE_PANEL_FIELDS:
                if pp.get(field_name) in {None, ""}:
                    page.findings.append(issue("G1-02", "fail", f"{page.name}/PANEL-{index}/{field_name}", "missing", "required v2.0.1 machine-track field missing"))
            source_raw = pp.get("source_shot")
            try:
                source_no = int(source_raw)
            except (TypeError, ValueError):
                page.findings.append(issue("G1-03", "fail", f"{page.name}/PANEL-{index}/source_shot", source_raw, "source_shot must be an integer"))
                continue
            source_numbers.append(source_no)
            if source_no not in shots:
                page.findings.append(issue("G1-03", "fail", f"{page.name}/PANEL-{index}/source_shot", source_no, "source shot not found in shot_data"))
                continue
            shot_tag = camera_tag_from_shot(shots[source_no])
            plan_tag = str(pp.get("shot_data_camera_tag", ""))
            if shot_tag and normalize_for_compare(shot_tag) != normalize_for_compare(plan_tag):
                page.findings.append(issue("G1-04", "fail", f"{page.name}/PANEL-{index}/shot_data_camera_tag", plan_tag, f"expected {shot_tag}"))
        range_start = source_range_start(pplan, source_numbers)
        if source_numbers and range_start is not None and source_numbers[0] != range_start:
            page.findings.append(
                issue(
                    "G1-12",
                    "fail",
                    f"{page.name}/PANEL-1/source_shot",
                    str(source_numbers[0]),
                    f"PANEL-1 must keep source range start {range_start}; do not reorder later shots into the anchor slot",
                )
            )
        if source_numbers and source_numbers != sorted(source_numbers):
            page.findings.append(
                issue(
                    "G1-12",
                    "fail",
                    f"{page.name}/panel_sequence",
                    ",".join(str(item) for item in source_numbers),
                    "source_shot order must remain nondecreasing; sparse continuation may repeat only after its source event",
                )
            )
        if not bool(pplan.get("sparse_page")) and len(set(source_numbers)) != len(source_numbers):
            page.findings.append(
                issue(
                    "G1-12",
                    "fail",
                    f"{page.name}/panel_sequence",
                    ",".join(str(item) for item in source_numbers),
                    "non-sparse pages must not duplicate source shots to fill panels",
                )
            )
        for index in range(2, 10):
            current_plan = panel_plan_for(pplan, index)
            previous_plan = panel_plan_for(pplan, index - 1)
            try:
                current_source = int(current_plan.get("source_shot"))
                previous_source = int(previous_plan.get("source_shot"))
            except (TypeError, ValueError):
                continue
            if current_source <= previous_source or current_source not in shots:
                continue
            if not has_distance_endpoint(shots[current_source]):
                continue
            previous_text = page.panels[index - 2].text if index - 2 < len(page.panels) else ""
            if not has_pre_distance_lock(previous_plan, previous_text):
                page.findings.append(
                    issue(
                        "G1-13",
                        "fail",
                        f"{page.name}/PANEL-{index - 1}/distance_stage_lock",
                        str(previous_plan.get("distance_stage_lock", "")),
                        f"source shot {current_source} defines a later distance/approach endpoint; previous panel must explicitly keep pre-approach spacing",
                    )
                )
        first = panel_plan_for(pplan, 1)
        tag = str(first.get("shot_data_camera_tag", ""))
        tokens = normalize_tag_tokens(tag)
        pos = bool(tokens & POSITIVE_ANCHOR)
        neg = bool(tokens & NEGATIVE_ANCHOR)
        drawn = str(first.get("drawn_camera_tag", ""))
        override = "master wide/full spatial anchor" in drawn.lower()
        if neg and not override:
            page.findings.append(issue("G1-11", "fail", f"{page.name}/PANEL-1/drawn_camera_tag", tag, "negative anchor tag requires master spatial override"))
        if (pos and neg) or (not pos and not neg):
            page.findings.append(issue("G1-11", "warn", f"{page.name}/PANEL-1", tag, "anchor decision uncertain; HC-1 required"))
            if pplan.get("anchor_decision") not in {"human_confirmed", "deterministic_source_order"}:
                page.findings.append(issue("G1-11", "fail", f"{page.name}/PANEL-1", tag, "panel_plan missing anchor_decision=human_confirmed or deterministic_source_order"))


def summarize(pages: list[Page]) -> dict[str, int]:
    fail = warn = 0
    for page in pages:
        for finding in page.findings:
            if finding.severity == "fail":
                fail += 1
            elif finding.severity == "warn":
                warn += 1
    return {"fail": fail, "warn": warn, "pass_checks": 0}


def findings_to_dict(findings: list[Finding]) -> list[dict[str, str]]:
    return [finding.__dict__ for finding in findings]


def validation_exit_code(summary: dict[str, int]) -> int:
    if summary["fail"]:
        return 2
    if summary["warn"]:
        return 1
    return 0


def compute_batch_id(mode: str, panel_plan_path: Path | None, panel_plan: dict[str, Any], shot_data_path: Path | None, shot_data: dict[str, Any] | None) -> str:
    plan_bytes = panel_plan_path.read_bytes() if panel_plan_path else json.dumps(panel_plan, sort_keys=True, ensure_ascii=False).encode("utf-8")
    plan_hash = hashlib.sha256(plan_bytes).hexdigest()
    if mode == "full":
        shot_bytes = shot_data_path.read_bytes() if shot_data_path else json.dumps(shot_data or {}, sort_keys=True, ensure_ascii=False).encode("utf-8")
        return "F-" + hashlib.sha256(shot_bytes).hexdigest()[:8] + plan_hash[:8]
    return "T-" + plan_hash[:16]


def validate(
    panel_plan: dict[str, Any],
    final_prompts: str,
    *,
    mode: str = "full",
    shot_data: dict[str, Any] | None = None,
    canon_path: Path | None = None,
    strict_canon: bool = False,
    accept_canon_change: bool = False,
    panel_plan_path: Path | None = None,
    shot_data_path: Path | None = None,
    compiled_path: str = "final_image_prompts.compiled.md",
) -> dict[str, Any]:
    canon_version, canon_blocks, canon_hashes = extract_canon(canon_path)
    pages = split_pages(final_prompts)
    global_findings: list[Finding] = []
    snapshot_status = "match"
    for name in EXPECTED_CANON_TEXTS:
        expected = FACTORY_HASHES.get(name)
        actual = canon_hashes.get(name)
        if actual != expected:
            if canon_version == CANON_VERSION:
                snapshot_status = "TAMPERED"
                global_findings.append(issue("G0-00", "fail", f"canon:{name}", actual or "missing", "canon hash differs without canon-version upgrade"))
            elif accept_canon_change:
                snapshot_status = "changed_accepted"
            else:
                snapshot_status = "changed_unaccepted"
                global_findings.append(issue("G0-00", "fail", f"canon:{name}", actual or "missing", "canon changed; rerun with --accept-canon-change"))
    compiled = compile_pages(pages, canon_blocks, strict_canon)
    if pages and global_findings:
        pages[0].findings[:0] = global_findings
    validate_g0(pages, compiled, panel_plan)
    validate_g1(pages, panel_plan, shot_data, mode)
    summary = summarize(pages)
    batch_id = compute_batch_id(mode, panel_plan_path, panel_plan, shot_data_path, shot_data)
    report_pages = []
    hc2_queue = []
    for page in pages:
        page_findings = findings_to_dict(page.findings)
        report_pages.append(
            {
                "page": page.name,
                "char_count": page.char_count,
                "budget_status": page.budget_status,
                "canon_autofixed": page.canon_autofixed,
                "findings": page_findings,
            }
        )
        for finding in page.findings:
            if finding.severity == "warn":
                hc2_queue.append(finding.__dict__)
    return {
        "mode": mode,
        "canon_version": canon_version,
        "canon_snapshot_status": snapshot_status,
        "batch_id": batch_id,
        "compiled_path": compiled_path,
        "compiled_text": compiled,
        "pages": report_pages,
        "summary": summary,
        "hc2_adjudication_queue": hc2_queue,
        "exit_code": validation_exit_code(summary),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compile and validate su-image9 v2.0.1 prompts.")
    parser.add_argument("--mode", choices=["full", "text-only"], required=True)
    parser.add_argument("--canon", required=True)
    parser.add_argument("--panel-plan", required=True)
    parser.add_argument("--final-prompts", required=True)
    parser.add_argument("--shot-data")
    parser.add_argument("--report", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--strict-canon", action="store_true")
    parser.add_argument("--accept-canon-change", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.mode == "full" and not args.shot_data:
        Path(args.report).write_text(json.dumps({"summary": {"fail": 1, "warn": 0}, "error": "full mode requires --shot-data"}, ensure_ascii=False, indent=2), encoding="utf-8")
        return 2
    try:
        panel_plan_path = Path(args.panel_plan)
        shot_data_path = Path(args.shot_data) if args.shot_data else None
        panel_plan = load_json(panel_plan_path)
        shot_data = load_json(shot_data_path) if shot_data_path else None
        prompt_text = Path(args.final_prompts).read_text(encoding="utf-8")
        result = validate(
            panel_plan,
            prompt_text,
            mode=args.mode,
            shot_data=shot_data,
            canon_path=Path(args.canon),
            strict_canon=args.strict_canon,
            accept_canon_change=args.accept_canon_change,
            panel_plan_path=panel_plan_path,
            shot_data_path=shot_data_path,
            compiled_path=args.out,
        )
        Path(args.out).write_text(result["compiled_text"], encoding="utf-8")
        report = {key: value for key, value in result.items() if key not in {"compiled_text", "exit_code"}}
        Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return int(result["exit_code"])
    except Exception as exc:
        payload = {"summary": {"fail": 1, "warn": 0}, "error": str(exc)}
        Path(args.report).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
