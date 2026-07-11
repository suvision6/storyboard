#!/usr/bin/env python3
"""Fail-closed validator/compiler for su-image9 v2.0.3 final prompts."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

CANON_VERSION = "2.0.3"

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
CANON_NAMES = frozenset(EXPECTED_CANON_TEXTS)
CANON_INTERNAL_HEADINGS = {
    "STYLE ANCHOR",
    "MEDIUM",
    "LINE RULE",
    "SHADING RULE",
    "TEXTURE RULE",
    "RENDERING RULE",
    "CONSISTENCY RULE",
}
STRICT_FACT_FIELDS = (
    "beat_ids",
    "covered_fact_ids",
    "visible_characters",
    "offscreen_characters",
    "visible_props",
)
BOOLEAN_LIKE = {"yes", "no", "true", "false", "present", "absent", "error"}
POSITIVE_ANCHOR = {"master", "establishing", "wide", "full", "全景", "大全景", "大远景"}
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
class LayerEntry:
    raw_name: str
    name: str
    body: str


@dataclass
class Page:
    name: str
    text: str
    explicit_heading: bool = True
    preamble: str = ""
    layer_entries: list[LayerEntry] = field(default_factory=list)
    layers: dict[str, str] = field(default_factory=dict)
    layer_headings: dict[str, str] = field(default_factory=dict)
    panels: list[PanelText] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    canon_autofixed: bool = False
    char_count: int = 0
    budget_status: str = "pass"


class ContractInputError(ValueError):
    """Raised when serialized inputs violate the public data contract."""


def load_deriver_contract() -> Any:
    path = Path(__file__).with_name("derive_su_image9_prompt_package.py")
    spec = importlib.util.spec_from_file_location("_su_image9_deriver_contract", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load deterministic deriver contract from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


def extract_canon(path: Path | None) -> tuple[str, dict[str, str], dict[str, str], list[Finding]]:
    findings: list[Finding] = []
    if path is None or not path.exists():
        findings.append(issue("G0-00", "fail", "canon", "missing", "canon file is required; built-in fallback is disabled"))
        return "unknown", {}, {}, findings
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        findings.append(issue("G0-00", "fail", "canon", "unreadable", str(exc)))
        return "unknown", {}, {}, findings

    version_matches = re.findall(r"<!--\s*canon-version:\s*([^\s]+)\s*-->", text)
    version = version_matches[0] if len(version_matches) == 1 else "unknown"
    if len(version_matches) != 1:
        findings.append(issue("G0-00", "fail", "canon/version", str(len(version_matches)), "canon must declare exactly one canon-version"))
    elif version != CANON_VERSION:
        findings.append(issue("G0-00", "fail", "canon/version", version, f"expected canon-version {CANON_VERSION}"))

    headings = re.findall(r"(?m)^###\s+canon:([^\s]+)\s*$", text)
    counts: dict[str, int] = {}
    for name in headings:
        counts[name] = counts.get(name, 0) + 1
    for name, count in counts.items():
        if name not in CANON_NAMES:
            findings.append(issue("G0-00", "fail", f"canon:{name}", "unknown", "only the four canonical block names are allowed"))
        if count != 1:
            findings.append(issue("G0-00", "fail", f"canon:{name}", str(count), "canon block heading must be unique"))

    parsed: dict[str, list[str]] = {}
    block_pattern = r"(?ms)^###\s+canon:([^\s]+)\s*\n\s*```text\s*\n(.*?)\n```"
    for match in re.finditer(block_pattern, text):
        parsed.setdefault(match.group(1), []).append(nfc(match.group(2)))

    blocks: dict[str, str] = {}
    for name in sorted(CANON_NAMES):
        values = parsed.get(name, [])
        if counts.get(name, 0) != 1 or len(values) != 1:
            findings.append(issue("G0-00", "fail", f"canon:{name}", "missing_or_malformed", "canon block must contain exactly one fenced text payload"))
            continue
        blocks[name] = values[0]
    hashes = {name: sha256_text(value) for name, value in blocks.items()}
    return version, blocks, hashes, findings


def extract_skill_inline_canon(path: Path) -> tuple[str, dict[str, str], list[Finding]]:
    findings: list[Finding] = []
    if not path.exists():
        findings.append(issue("G0-00", "fail", "SKILL.md", "missing", "inline canon authority cannot be compared"))
        return "unknown", {}, findings
    text = path.read_text(encoding="utf-8")
    skill_versions = re.findall(r"<!--\s*skill-version:\s*([^\s]+)\s*-->", text)
    canon_versions = re.findall(r"<!--\s*canon-version:\s*([^\s]+)\s*-->", text)
    version = skill_versions[0] if len(skill_versions) == 1 else "unknown"
    if skill_versions != [CANON_VERSION]:
        findings.append(issue("G0-00", "fail", "SKILL.md/skill-version", json.dumps(skill_versions), f"exactly one skill-version {CANON_VERSION} is required"))
    if canon_versions != [CANON_VERSION]:
        findings.append(issue("G0-00", "fail", "SKILL.md/canon-version", json.dumps(canon_versions), f"exactly one canon-version {CANON_VERSION} is required"))
    for section in ("GEN-1", "GEN-2", "GEN-3", "GEN-4"):
        count = len(re.findall(rf"(?m)^##\s+{re.escape(section)}\b", text))
        if count != 1:
            findings.append(issue("G0-00", "fail", f"SKILL.md/{section}", str(count), "inline canon section must occur exactly once"))

    def fenced_after(section: str) -> str | None:
        match = re.search(rf"(?ms)^##\s+{section}.*?^```text\s*\n(.*?)\n```", text)
        return nfc(match.group(1)) if match else None

    blocks: dict[str, str] = {}
    system = fenced_after(r"GEN-1\b")
    geometry = fenced_after(r"GEN-2\b")
    negative = fenced_after(r"GEN-3\b")
    if system is not None:
        blocks["SYSTEM_STYLE_LAYER"] = system
    if geometry is not None:
        blocks["GEOMETRY_BLUEPRINT"] = geometry
    if negative is not None:
        blocks["NEGATIVE_CONSTRAINTS"] = "NEGATIVE_CONSTRAINTS:\n" + negative.removeprefix("NEGATIVE_CONSTRAINTS:\n")

    hard_section = re.search(r"(?ms)^##\s+GEN-4\b.*?\n(.*?)(?=^##\s+GEN-5\b)", text)
    if hard_section:
        hard_lines = re.findall(r"(?m)^-\s+`([^`]+)`\s*$", hard_section.group(1))
        if hard_lines == HARD_PHRASES.splitlines():
            blocks["HARD_PHRASES"] = nfc("\n".join(hard_lines))
        else:
            findings.append(issue("G0-00", "fail", "SKILL.md:HARD_PHRASES", str(len(hard_lines)), "GEN-4 hard phrases must match the exact six-line snapshot with no extras"))

    for name in sorted(CANON_NAMES):
        if name not in blocks:
            findings.append(issue("G0-00", "fail", f"SKILL.md:{name}", "missing", "inline canon block cannot be parsed"))
    return version, blocks, findings


def split_pages(text: str) -> list[Page]:
    text = nfc(text)
    matches = list(re.finditer(r"(?m)^#\s+(PAGE-\d{2})\b.*$", text))
    if not matches:
        page = Page("PAGE-01", text, explicit_heading=False)
        page.findings.append(issue("G0-11", "fail", "final_prompts", "missing_page_heading", "prompt must begin with an explicit # PAGE-01 heading"))
        return [page]
    pages: list[Page] = []
    document_preamble = text[: matches[0].start()].strip()
    for idx, match in enumerate(matches):
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        body = text[match.end():end].strip()
        if idx == 0 and document_preamble:
            body = document_preamble + "\n\n" + body
        pages.append(Page(match.group(1), body))
    if document_preamble:
        pages[0].findings.append(issue("G0-11", "fail", "final_prompts/preamble", "unexpected_text", "text before the first PAGE heading is forbidden and has been preserved for diagnosis"))
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
    entries: list[LayerEntry] = []
    page.preamble = page.text[: headers[0].start()].strip() if headers else page.text.strip()
    if page.preamble:
        page.findings.append(issue("G0-12", "fail", page.name, "preamble", "content before the first required layer is not allowed"))
    for idx, header in enumerate(headers):
        raw = header.group(1)
        name = normalize_layer_name(raw)
        end = headers[idx + 1].start() if idx + 1 < len(headers) else len(page.text)
        body = page.text[header.end():end].strip()
        entries.append(LayerEntry(raw, name, body))
        if name in layers:
            page.findings.append(issue("G0-12", "fail", f"{page.name}/{raw}", "duplicate", "duplicate layer headings are forbidden"))
        else:
            layers[name] = body
            layer_headings[name] = raw
    actual_order = [entry.name for entry in entries]
    if actual_order != LAYER_ORDER:
        page.findings.append(
            issue(
                "G0-12",
                "fail",
                f"{page.name}/layer_order",
                ",".join(actual_order),
                "layers must appear exactly once in the required order; compiler will not reorder them",
            )
        )

    known_header_spans = {(match.start(), match.end()) for match in headers}
    candidate_pattern = r"(?m)^([A-Z][A-Z0-9_ /-]{2,}):\s*$"
    for candidate in re.finditer(candidate_pattern, page.text):
        if (candidate.start(), candidate.end()) in known_header_spans:
            continue
        raw = candidate.group(1).strip()
        if raw in CANON_INTERNAL_HEADINGS or re.fullmatch(r"PANEL-[1-9]", raw):
            continue
        if not re.search(r"(?:LAYER|LOCK|LAYOUT|ANCHOR|CONSTRAINTS|DELIVERABLE)$", raw):
            continue
        page.findings.append(issue("G0-12", "fail", f"{page.name}/{raw}", "unknown_layer", "unknown top-level layer-like heading is forbidden"))
    page.layer_entries = entries
    page.layers = layers
    page.layer_headings = layer_headings


def parse_panel_layer(page: Page) -> None:
    panel_layer = page.layers.get("PANEL_LAYER", "")
    panels: list[PanelText] = []
    matches = list(re.finditer(r"(?ms)^PANEL-(\d+):\s*(.*?)(?=^PANEL-\d+:\s*|\Z)", panel_layer))
    for match in matches:
        panels.append(PanelText(f"PANEL-{match.group(1)}", match.group(2).strip()))
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
    if page.preamble:
        parts.append(page.preamble)
    for entry in page.layer_entries:
        parts.append(f"{entry.raw_name}:\n{entry.body}")
    return "\n\n".join(parts).strip()


def compile_pages(pages: list[Page], canon_blocks: dict[str, str]) -> str:
    for page in pages:
        parse_layers(page)
        for required in LAYER_ORDER:
            if required == "REFERENCE_OR_TEXT":
                if required not in page.layers:
                    page.findings.append(issue("G0-01", "fail", page.name, "REFERENCE_USAGE or TEXT_DERIVED_LAYOUT", "required layer missing"))
                continue
            if required not in page.layers:
                page.findings.append(issue("G0-01", "fail", page.name, required, "required layer missing"))
        first_values: dict[str, str] = {}
        for entry in page.layer_entries:
            entry.body = replace_canon_markers(page, entry.name, entry.body, canon_blocks)
            first_values.setdefault(entry.name, entry.body)
        page.layers = first_values
        for name in ["SYSTEM_STYLE_LAYER", "NEGATIVE_CONSTRAINTS"]:
            if name not in page.layers:
                continue
            expected = canon_blocks.get(name)
            actual_full = canonical_layer_text(name, page.layers[name])
            if expected is None or normalize_for_compare(actual_full) != normalize_for_compare(expected):
                page.findings.append(issue("G0-02", "fail", f"{page.name}/{name}", name, "canon block differs; automatic repair is disabled"))
        parse_panel_layer(page)
    return "\n\n".join(render_page(page) for page in pages).strip() + "\n"


def codepoint_len(text: str) -> int:
    return len(nfc(text))


def compiled_page_text(page: Page) -> str:
    return render_page(page)


def require_text(page: Page, text: str, source: str, check: str = "G0-04") -> None:
    page_text = compiled_page_text(page)
    if normalize_for_compare(text) not in normalize_for_compare(page_text):
        page.findings.append(issue(check, "fail", f"{page.name}/{source}", "missing", "required v2.0.3 generation-layer text missing"))


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


def scan_forbidden_style(text: str, page: Page, field: str, extra_tokens: list[str] | None = None) -> None:
    lower = text.lower()
    for token in [*FORBIDDEN_STYLE_TOKENS, *(extra_tokens or [])]:
        if token in lower:
            page.findings.append(issue("G0-08", "fail", field, token, "forbidden independent style definition"))


def dynamic_layer_body(name: str, body: str) -> str:
    if name in {"SYSTEM_STYLE_LAYER", "NEGATIVE_CONSTRAINTS"}:
        return ""
    cleaned = body
    for canonical in (HARD_PHRASES, GEOMETRY_BLUEPRINT):
        cleaned = cleaned.replace(canonical, "")
        cleaned = cleaned.replace(strip_own_heading(name, canonical), "")
    return cleaned


def scan_panel_text(page: Page, extra_tokens: list[str] | None = None) -> None:
    if len(page.panels) != 9:
        page.findings.append(issue("G0-06", "fail", page.name, str(len(page.panels)), "PANEL_LAYER must contain exactly 9 panels"))
    expected_names = [f"PANEL-{index}" for index in range(1, 10)]
    actual_names = [panel.name for panel in page.panels]
    if actual_names != expected_names:
        page.findings.append(issue("G0-06", "fail", page.name, ",".join(actual_names), "panels must be unique and ordered exactly PANEL-1 through PANEL-9"))
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
        scan_forbidden_style(text, page, field, extra_tokens)


def plan_pages(panel_plan: dict[str, Any]) -> list[dict[str, Any]]:
    pages = panel_plan.get("pages")
    return pages if isinstance(pages, list) else []


def page_plan_for(page: Page, panel_plan: dict[str, Any]) -> dict[str, Any]:
    pages = plan_pages(panel_plan)
    for item in pages:
        if isinstance(item, dict) and item.get("page") == page.name:
            return item
    return {}


def panel_plan_items(page_plan: dict[str, Any]) -> list[dict[str, Any]]:
    panels = page_plan.get("panels")
    return panels if isinstance(panels, list) else []


def panel_plan_for(page_plan: dict[str, Any], index: int) -> dict[str, Any]:
    panels = panel_plan_items(page_plan)
    for item in panels:
        if isinstance(item, dict) and item.get("panel", item.get("panel_id")) == f"PANEL-{index}":
            return item
    return {}


def scan_plan_booleans(value: Any, path: str, findings: list[Finding]) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            key_name = str(key)
            semantic = key_name in {*STRICT_FACT_FIELDS, "visible_only", "prop_state"}
            if semantic and isinstance(nested, bool):
                findings.append(issue("G0-09", "fail", f"{path}.{key_name}" if path else key_name, str(nested), "boolean values cannot stand in for factual entities or states"))
            if semantic and isinstance(nested, str) and nested.strip().lower() in BOOLEAN_LIKE:
                findings.append(issue("G0-09", "fail", f"{path}.{key_name}" if path else key_name, nested, "boolean/error shorthand cannot stand in for factual entities or states"))
            scan_plan_booleans(nested, f"{path}.{key}" if path else str(key), findings)
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            scan_plan_booleans(nested, f"{path}[{index}]", findings)
    elif isinstance(value, str):
        if re.search(r"\bprops\s*=\s*(yes|no|true|false|present|absent)\b", value, re.I):
            findings.append(issue("G0-09", "fail", path, "props boolean", "boolean prop compression is forbidden in panel_plan"))


def shot_index(shot_data: dict[str, Any] | None, findings: list[Finding] | None = None) -> dict[int, dict[str, Any]]:
    result: dict[int, dict[str, Any]] = {}
    if not shot_data:
        return result
    shots = shot_data.get("shots", [])
    if not isinstance(shots, list):
        if findings is not None:
            findings.append(issue("G1-03", "fail", "shot_data.shots", type(shots).__name__, "shots must be an array"))
        return result
    for index, shot in enumerate(shots):
        if not isinstance(shot, dict):
            if findings is not None:
                findings.append(issue("G1-03", "fail", f"shot_data.shots[{index}]", type(shot).__name__, "shot must be an object"))
            continue
        raw = shot.get("shot_no")
        if isinstance(raw, bool) or not isinstance(raw, int) or raw <= 0:
            if findings is not None:
                findings.append(issue("G1-03", "fail", f"shot_data.shots[{index}].shot_no", raw, "shot_no must be a positive JSON integer"))
            continue
        number = raw
        if number in result:
            if findings is not None:
                findings.append(issue("G1-03", "fail", f"shot_data.shots[{index}].shot_no", number, "duplicate source shot number"))
            continue
        result[number] = shot
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


def unique_in_order(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if value and value not in result:
            result.append(value)
    return result


def validate_page_split_policy(page: Page, pplan: dict[str, Any], source_numbers: list[int], shots: dict[int, dict[str, Any]]) -> None:
    policy = str(pplan.get("page_split_policy", "")).strip()
    if not policy:
        page.findings.append(issue("G1-14", "fail", f"{page.name}/page_split_policy", "missing", "v2.0.3 requires scene/layer-aware page split policy"))
        return
    supported_policy = "scene_layer_aware_strict_source_order" in policy or policy == "strict_single_scene_single_reality_layer"
    if not supported_policy:
        page.findings.append(issue("G1-14", "fail", f"{page.name}/page_split_policy", policy, "page split policy must enforce scene/layer boundaries and preserve source order"))
    unique_sources: list[int] = []
    for source_no in source_numbers:
        if source_no not in unique_sources:
            unique_sources.append(source_no)
    source_shots = [shots[number] for number in unique_sources if number in shots]
    if not source_shots:
        return


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


def extra_forbidden_tokens(panel_plan: dict[str, Any], findings: list[Finding]) -> list[str]:
    raw = panel_plan.get("forbidden_prompt_tokens_extra", [])
    if not isinstance(raw, list):
        findings.append(issue("G0-08", "fail", "panel_plan.forbidden_prompt_tokens_extra", type(raw).__name__, "extra forbidden tokens must be an array of strings"))
        return []
    result: list[str] = []
    for index, item in enumerate(raw):
        if not isinstance(item, str) or not item.strip():
            findings.append(issue("G0-08", "fail", f"panel_plan.forbidden_prompt_tokens_extra[{index}]", type(item).__name__, "token must be a non-empty string"))
            continue
        token = item.strip().lower()
        if token not in result:
            result.append(token)
    return result


def validate_prompt_plan_structure(pages: list[Page], panel_plan: dict[str, Any], findings: list[Finding]) -> None:
    prompt_names = [page.name for page in pages]
    expected_prompt_names = [f"PAGE-{index:02d}" for index in range(1, len(pages) + 1)]
    if prompt_names != expected_prompt_names:
        findings.append(issue("G0-11", "fail", "final_prompts/pages", ",".join(prompt_names), "prompt page IDs must be unique, ordered, and continuous from PAGE-01"))

    raw_plan_pages = panel_plan.get("pages")
    if not isinstance(raw_plan_pages, list):
        findings.append(issue("G0-11", "fail", "panel_plan.pages", type(raw_plan_pages).__name__, "panel_plan.pages must be an array"))
        return
    plan_names: list[str] = []
    for index, item in enumerate(raw_plan_pages, 1):
        if not isinstance(item, dict):
            findings.append(issue("G0-11", "fail", f"panel_plan.pages[{index - 1}]", type(item).__name__, "page plan must be an object"))
            plan_names.append("")
            continue
        raw_name = item.get("page")
        plan_names.append(raw_name if isinstance(raw_name, str) else "")
        panels = item.get("panels")
        if not isinstance(panels, list):
            findings.append(issue("G1-01", "fail", f"panel_plan.pages[{index - 1}].panels", type(panels).__name__, "panels must be an array"))
            continue
        actual_panel_names = [
            panel.get("panel", panel.get("panel_id")) if isinstance(panel, dict) else None
            for panel in panels
        ]
        expected_panel_names = [f"PANEL-{panel_index}" for panel_index in range(1, 10)]
        if actual_panel_names != expected_panel_names:
            findings.append(
                issue(
                    "G1-01",
                    "fail",
                    f"panel_plan/{raw_name or index}/panels",
                    ",".join(str(name) for name in actual_panel_names),
                    "panel plan IDs must be unique and ordered exactly PANEL-1 through PANEL-9",
                )
            )
    if plan_names != expected_prompt_names or plan_names != prompt_names:
        findings.append(issue("G0-11", "fail", "prompt_vs_panel_plan/pages", f"prompt={prompt_names}; plan={plan_names}", "prompt and panel_plan pages must match one-to-one in exact order"))


def validate_release_contract(panel_plan: dict[str, Any], mode: str, findings: list[Finding]) -> None:
    if panel_plan.get("skill") != "su-image9":
        findings.append(issue("G0-13", "fail", "panel_plan.skill", panel_plan.get("skill"), "expected su-image9"))
    version = str(panel_plan.get("version", ""))
    if mode == "text-only":
        if panel_plan.get("release_ready") is True:
            findings.append(issue("G0-13", "fail", "panel_plan.release_ready", "true", "text-only mode is deprecated and can never be release-ready"))
        else:
            findings.append(issue("R-TEXT-ONLY-DEPRECATED", "warn", "PACKAGE/mode", "text-only", "text-only compatibility mode always requires review"))
        if version != CANON_VERSION:
            findings.append(issue("G0-13", "warn", "panel_plan.version", version or "missing", "legacy or unknown plan is review-only; regenerate as v2.0.3"))
        return
    if version != CANON_VERSION:
        if panel_plan.get("release_ready") is True:
            findings.append(issue("G0-13", "fail", "panel_plan.release_ready", "true", f"legacy or unknown plan version {version or 'missing'} cannot be release-ready"))
        else:
            findings.append(issue("G0-13", "warn", "panel_plan.version", version or "missing", "legacy or unknown plan is review-only; regenerate as v2.0.3"))
        return
    if panel_plan.get("canon_version") != CANON_VERSION:
        findings.append(issue("G0-13", "fail", "panel_plan.canon_version", panel_plan.get("canon_version"), f"expected {CANON_VERSION}"))
    ready = panel_plan.get("release_ready")
    reasons = panel_plan.get("review_required_reasons", [])
    if not isinstance(ready, bool):
        findings.append(issue("G0-13", "fail", "panel_plan.release_ready", type(ready).__name__, "v2.0.3 full plans require a boolean release_ready"))
        return
    reasons_valid = isinstance(reasons, list)
    if reasons_valid:
        for item in reasons:
            if not isinstance(item, dict) or any(not isinstance(item.get(key), str) or not item.get(key, "").strip() for key in ("code", "page", "message")):
                reasons_valid = False
                break
    if not reasons_valid:
        findings.append(issue("G0-13", "fail", "panel_plan.review_required_reasons", type(reasons).__name__, "review reasons must be objects with non-empty code, page, and message"))
        return
    if ready and reasons:
        findings.append(issue("G0-13", "fail", "panel_plan.release_ready", "true", "release_ready conflicts with non-empty review_required_reasons"))
    elif not ready:
        severity = "warn" if reasons else "fail"
        findings.append(issue("G0-13", severity, "panel_plan.release_ready", "false", "release is blocked" if reasons else "release_ready=false requires at least one review reason"))


def validate_g0(pages: list[Page], compiled_text: str, panel_plan: dict[str, Any]) -> None:
    global_plan_findings: list[Finding] = []
    scan_plan_booleans(panel_plan, "panel_plan", global_plan_findings)
    extras = extra_forbidden_tokens(panel_plan, global_plan_findings)
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
            page.findings.append(issue("G0-10", "fail", page.name, "v1.7.3 structure", "old PANEL_TASKS/canon-lock structure is not allowed for v2.0.3 final prompts"))
        if re.search(r"\bP\d{2}\b", page.text):
            page.findings.append(issue("G0-10", "fail", page.name, "Pxx", "old P01-style naming is not allowed"))
        validate_layer_presence(page)
        for entry in page.layer_entries:
            body = dynamic_layer_body(entry.name, entry.body)
            if body:
                scan_forbidden_style(body, page, f"{page.name}/{entry.raw_name}", extras)
        scan_panel_text(page, extras)
        page.findings.extend(global_plan_findings)


def normalized_string_list(value: Any, page: Page, field: str) -> list[str] | None:
    if not isinstance(value, list):
        page.findings.append(issue("G1-05", "fail", field, type(value).__name__, "fact field must be an array of strings"))
        return None
    result: list[str] = []
    for index, item in enumerate(value):
        if isinstance(item, bool) or not isinstance(item, str) or not item.strip():
            page.findings.append(issue("G1-05", "fail", f"{field}[{index}]", type(item).__name__, "fact items must be non-empty strings, never booleans or objects"))
            continue
        clean = nfc(item)
        if clean in result:
            page.findings.append(issue("G1-05", "fail", field, clean, "duplicate fact/entity value"))
            continue
        result.append(clean)
    return result


def legacy_visible_lists(panel: dict[str, Any]) -> tuple[list[str] | None, list[str] | None]:
    raw = panel.get("visible_only")
    if not isinstance(raw, str):
        return None, None
    chars_match = re.search(r"visible\s+characters\s*:\s*(.*?)(?:;|$)", raw, re.I)
    props_match = re.search(r"visible\s+props\s*:\s*(.*?)(?:;|$)", raw, re.I)

    def split(match: re.Match[str] | None) -> list[str] | None:
        if not match:
            return None
        value = match.group(1).strip()
        if not value or value.lower() in {"none", "no visible characters", "no visible props"}:
            return []
        return [item.strip() for item in re.split(r"[,，、/]", value) if item.strip()]

    return split(chars_match), split(props_match)


def compare_fact_field(
    page: Page,
    panel: dict[str, Any],
    shot: dict[str, Any],
    field_name: str,
    field_path: str,
    *,
    require_explicit: bool,
) -> list[str]:
    if field_name not in shot:
        return []
    expected = normalized_string_list(shot.get(field_name), page, f"shot_data/{field_path}/{field_name}")
    if expected is None:
        return []
    actual_raw = panel.get(field_name)
    actual: list[str] | None = None
    if actual_raw is not None:
        actual = normalized_string_list(actual_raw, page, f"panel_plan/{field_path}/{field_name}")
    elif not require_explicit and field_name in {"visible_characters", "visible_props"}:
        legacy_chars, legacy_props = legacy_visible_lists(panel)
        actual = legacy_chars if field_name == "visible_characters" else legacy_props
        if actual is None:
            legacy_text = " ".join(str(panel.get(key, "")) for key in ("visible_only", "prop_state"))
            folded = normalize_for_compare(legacy_text).casefold()
            if not expected or all(normalize_for_compare(item).casefold() in folded for item in expected):
                actual = list(expected)
    elif not require_explicit and not expected:
        actual = []
    if actual is None:
        page.findings.append(issue("G1-05", "fail", f"panel_plan/{field_path}/{field_name}", "missing", "source fact field must be represented explicitly in panel_plan"))
        return expected
    if [item.casefold() for item in actual] != [item.casefold() for item in expected]:
        page.findings.append(issue("G1-05", "fail", f"panel_plan/{field_path}/{field_name}", json.dumps(actual, ensure_ascii=False), f"expected {json.dumps(expected, ensure_ascii=False)}"))
    return expected


def normalized_continuity_updates(value: Any, page: Page, field: str) -> list[dict[str, Any]] | None:
    if not isinstance(value, list):
        page.findings.append(issue("G1-07", "fail", field, type(value).__name__, "continuity_updates must be an array of objects"))
        return None
    result: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            page.findings.append(issue("G1-07", "fail", f"{field}[{index}]", type(item).__name__, "continuity update must be an object"))
            continue
        result.append(item)
    return result


def compare_continuity_updates(page: Page, panel: dict[str, Any], shot: dict[str, Any], field_path: str, require_explicit: bool) -> None:
    if "continuity_updates" not in shot:
        if require_explicit:
            page.findings.append(issue("G1-07", "fail", f"shot_data/{field_path}/continuity_updates", "missing", "v2.0.3 source shot must declare continuity_updates"))
        return
    expected = normalized_continuity_updates(shot.get("continuity_updates"), page, f"shot_data/{field_path}/continuity_updates")
    if "continuity_updates" not in panel:
        if require_explicit or expected:
            page.findings.append(issue("G1-07", "fail", f"panel_plan/{field_path}/continuity_updates", "missing", "panel must preserve source continuity_updates"))
        return
    actual = normalized_continuity_updates(panel.get("continuity_updates"), page, f"panel_plan/{field_path}/continuity_updates")
    if expected is not None and actual is not None:
        expected_text = json.dumps(expected, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        actual_text = json.dumps(actual, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        if actual_text != expected_text:
            page.findings.append(issue("G1-07", "fail", f"panel_plan/{field_path}/continuity_updates", actual_text, f"expected {expected_text}"))


def drawn_camera_matches_source(drawn: Any, source_tag: str) -> bool:
    if not isinstance(drawn, str) or not drawn.strip():
        return False
    normalized_drawn = normalize_for_compare(drawn)
    normalized_source = normalize_for_compare(source_tag)
    if normalized_drawn == normalized_source:
        return True
    prefix = "drawn camera follows source camera tag:"
    if normalized_drawn.casefold().startswith(prefix):
        return normalize_for_compare(normalized_drawn[len(prefix):]) == normalized_source
    return False


def reality_layer_from_source(shot: dict[str, Any], logs: dict[str, dict[str, Any]]) -> str:
    direct = str(shot.get("reality_layer", "")).strip()
    if direct:
        return direct
    inherited = str(logs.get(str(shot.get("scene_id", "")), {}).get("reality_layer", "")).strip()
    return inherited or "unspecified"


def validate_shot_data_contract(shot_data: Any, page: Page) -> bool:
    if not isinstance(shot_data, dict):
        page.findings.append(issue("G1-00", "fail", "shot_data", type(shot_data).__name__, "shot_data root must be an object"))
        return False
    metadata = shot_data.get("metadata")
    if not isinstance(metadata, dict):
        page.findings.append(issue("G1-00", "fail", "shot_data.metadata", type(metadata).__name__, "metadata must be an object"))
    else:
        if metadata.get("skill_name") != "su-fenjingskill-zh":
            page.findings.append(issue("G1-00", "fail", "shot_data.metadata.skill_name", metadata.get("skill_name"), "expected su-fenjingskill-zh"))
        if metadata.get("version") != "2.4.2":
            page.findings.append(issue("G1-00", "fail", "shot_data.metadata.version", metadata.get("version"), "v2.0.3 accepts only su-fenjingskill-zh 2.4.2 shot_data"))
    script_lock = shot_data.get("script_lock")
    if not isinstance(script_lock, dict) or script_lock.get("status") != "locked":
        page.findings.append(issue("G1-00", "fail", "shot_data.script_lock.status", script_lock.get("status") if isinstance(script_lock, dict) else type(script_lock).__name__, "script lock must be locked"))
    upstream = shot_data.get("validation_report")
    if not isinstance(upstream, dict):
        page.findings.append(issue("G1-00", "fail", "shot_data.validation_report", type(upstream).__name__, "validation_report must be an object"))
    else:
        status = str(upstream.get("status", "")).upper()
        if status not in {"PASS", "WARN"}:
            page.findings.append(issue("G1-00", "fail", "shot_data.validation_report.status", status or "missing", "upstream status must be PASS or WARN"))
        elif status == "WARN":
            page.findings.append(issue("G1-00", "warn", "shot_data.validation_report.status", status, "upstream WARN remains review-only"))
    shots = shot_data.get("shots")
    raw_logs = shot_data.get("continuity_logs")
    registered_scene_ids: set[str] = set()
    if not isinstance(raw_logs, list):
        page.findings.append(issue("G1-00", "fail", "shot_data.continuity_logs", type(raw_logs).__name__, "continuity_logs must be an array"))
    else:
        for index, log in enumerate(raw_logs):
            scene_id = log.get("scene_id") if isinstance(log, dict) else None
            if not isinstance(scene_id, str) or not scene_id.strip():
                page.findings.append(issue("G1-00", "fail", f"shot_data.continuity_logs[{index}].scene_id", scene_id, "continuity log scene_id must be a non-empty string"))
                continue
            if scene_id in registered_scene_ids:
                page.findings.append(issue("G1-00", "fail", f"shot_data.continuity_logs[{index}].scene_id", scene_id, "continuity log scene_id must be unique"))
            registered_scene_ids.add(scene_id)
    if not isinstance(shots, list) or not shots:
        page.findings.append(issue("G1-00", "fail", "shot_data.shots", type(shots).__name__, "shots must be a non-empty array"))
    else:
        shot_numbers: list[int] = []
        for index, shot in enumerate(shots):
            if not isinstance(shot, dict):
                continue
            shot_no = shot.get("shot_no")
            if isinstance(shot_no, bool) or not isinstance(shot_no, int) or shot_no <= 0:
                page.findings.append(issue("G1-03", "fail", f"shot_data.shots[{index}].shot_no", shot_no, "shot_no must be a positive JSON integer"))
            else:
                shot_numbers.append(shot_no)
            scene_id = shot.get("scene_id")
            if not isinstance(scene_id, str) or not scene_id.strip():
                page.findings.append(issue("G1-00", "fail", f"shot_data.shots[{index}].scene_id", scene_id, "scene_id must be a non-empty string"))
            elif scene_id not in registered_scene_ids:
                page.findings.append(issue("G1-00", "fail", f"shot_data.shots[{index}].scene_id", scene_id, "shot scene_id must be registered in continuity_logs"))
        if len(shot_numbers) != len(set(shot_numbers)):
            page.findings.append(issue("G1-03", "fail", "shot_data.shots/shot_no", ",".join(map(str, shot_numbers)), "shot_no values must be unique"))
        if shot_numbers != sorted(shot_numbers):
            page.findings.append(issue("G1-03", "fail", "shot_data.shots/shot_no", ",".join(map(str, shot_numbers)), "shot_no values must be strictly increasing"))
    return True


def validate_g1(pages: list[Page], panel_plan: dict[str, Any], shot_data: dict[str, Any] | None, mode: str) -> None:
    if mode == "full" and shot_data is None:
        pages[0].findings.append(issue("G1-00", "fail", "shot_data", "missing", "full mode requires --shot-data"))
        return
    if mode != "full":
        return
    if not validate_shot_data_contract(shot_data, pages[0]):
        return
    source_findings: list[Finding] = []
    shots = shot_index(shot_data, source_findings)
    if pages:
        pages[0].findings.extend(source_findings)
    plan_version = str(panel_plan.get("version", ""))
    require_explicit_facts = plan_version == CANON_VERSION
    native_sources: list[int] = []
    all_source_occurrences: list[int] = []
    for page in pages:
        pplan = page_plan_for(page, panel_plan)
        panels = panel_plan_items(pplan)
        source_numbers: list[int] = []
        page_native_seen: set[int] = set()
        prompt_panels = {panel.name: panel.text for panel in page.panels}
        if not pplan:
            page.findings.append(issue("G1-01", "fail", f"{page.name}/panel_plan", "missing", "exact page ID not found; positional fallback is disabled"))
        if len(panels) != 9:
            page.findings.append(issue("G1-01", "fail", f"{page.name}/panel_plan", str(len(panels)), "panel_plan page must contain 9 panels"))
        for index in range(1, 10):
            pp = panel_plan_for(pplan, index)
            if not pp:
                page.findings.append(issue("G1-01", "fail", f"{page.name}/PANEL-{index}", "missing", "panel_plan panel missing"))
                continue
            for field_name in MACHINE_PANEL_FIELDS:
                if pp.get(field_name) in {None, ""}:
                    page.findings.append(issue("G1-02", "fail", f"{page.name}/PANEL-{index}/{field_name}", "missing", "required v2.0.3 machine-track field missing"))
            if require_explicit_facts:
                for field_name in STRICT_FACT_FIELDS:
                    if field_name not in pp:
                        page.findings.append(issue("G1-05", "fail", f"{page.name}/PANEL-{index}/{field_name}", "missing", "v2.0.3 panels require explicit fact arrays"))
                for field_name in ("source_camera_tag", "continuity_updates"):
                    if field_name not in pp:
                        page.findings.append(issue("G1-07", "fail", f"{page.name}/PANEL-{index}/{field_name}", "missing", "v2.0.3 panel field is required"))
            source_raw = pp.get("source_shot")
            if isinstance(source_raw, bool) or not isinstance(source_raw, int) or source_raw <= 0:
                page.findings.append(issue("G1-03", "fail", f"{page.name}/PANEL-{index}/source_shot", source_raw, "source_shot must be a positive JSON integer"))
                continue
            source_no = source_raw
            source_numbers.append(source_no)
            all_source_occurrences.append(source_no)
            panel_kind = pp.get("panel_kind")
            if panel_kind is not None and panel_kind not in {"source", "derived_angle", "continuation"}:
                page.findings.append(issue("G1-06", "fail", f"{page.name}/PANEL-{index}/panel_kind", panel_kind, "unknown panel_kind"))
            is_native = panel_kind == "source" if panel_kind is not None else source_no not in page_native_seen
            if is_native:
                native_sources.append(source_no)
                page_native_seen.add(source_no)
            if source_no not in shots:
                page.findings.append(issue("G1-03", "fail", f"{page.name}/PANEL-{index}/source_shot", source_no, "source shot not found in shot_data"))
                continue
            shot_tag = camera_tag_from_shot(shots[source_no])
            plan_tag_raw = pp.get("shot_data_camera_tag")
            plan_tag = plan_tag_raw if isinstance(plan_tag_raw, str) else ""
            if normalize_for_compare(shot_tag) != normalize_for_compare(plan_tag):
                page.findings.append(issue("G1-04", "fail", f"{page.name}/PANEL-{index}/shot_data_camera_tag", plan_tag, f"expected {shot_tag}"))
            source_tag_raw = pp.get("source_camera_tag")
            if require_explicit_facts or source_tag_raw is not None:
                if not isinstance(source_tag_raw, str) or normalize_for_compare(source_tag_raw) != normalize_for_compare(shot_tag):
                    page.findings.append(issue("G1-04", "fail", f"{page.name}/PANEL-{index}/source_camera_tag", source_tag_raw, f"expected {shot_tag}"))
            if require_explicit_facts and is_native and not drawn_camera_matches_source(pp.get("drawn_camera_tag"), shot_tag):
                page.findings.append(issue("G1-04", "fail", f"{page.name}/PANEL-{index}/drawn_camera_tag", pp.get("drawn_camera_tag"), "source panel camera must exactly preserve its source camera tag"))
            shot = shots[source_no]
            fact_path = f"{page.name}/PANEL-{index}"
            visible_characters = compare_fact_field(page, pp, shot, "visible_characters", fact_path, require_explicit=require_explicit_facts)
            visible_props = compare_fact_field(page, pp, shot, "visible_props", fact_path, require_explicit=require_explicit_facts)
            compare_fact_field(page, pp, shot, "offscreen_characters", fact_path, require_explicit=require_explicit_facts)
            compare_fact_field(page, pp, shot, "beat_ids", fact_path, require_explicit=require_explicit_facts)
            compare_fact_field(page, pp, shot, "covered_fact_ids", fact_path, require_explicit=require_explicit_facts)
            compare_continuity_updates(page, pp, shot, fact_path, require_explicit_facts)
            panel_text = prompt_panels.get(f"PANEL-{index}", "")
            panel_text_folded = normalize_for_compare(panel_text).casefold()
            if require_explicit_facts:
                for entity in [*visible_characters, *visible_props]:
                    if normalize_for_compare(entity).casefold() not in panel_text_folded:
                        page.findings.append(issue("G1-05", "fail", f"{page.name}/PANEL-{index}", entity, "visible source entity/prop is missing from PANEL text"))
                allowed_identifiers = {
                    normalize_for_compare(item).casefold()
                    for field_name in ("visible_characters", "offscreen_characters", "visible_props")
                    for item in (pp.get(field_name) if isinstance(pp.get(field_name), list) else [])
                    if isinstance(item, str)
                }
                camera_identifiers = {"pov", "ots", "ecu", "cu", "mcu", "ms", "ws", "ews"}
                for token in re.findall(r"\b[A-Z][A-Z0-9_]{2,}\b", panel_text):
                    if token.casefold() not in allowed_identifiers and token.casefold() not in camera_identifiers:
                        page.findings.append(issue("G1-08", "fail", f"{page.name}/PANEL-{index}", token, "PANEL text contains an undeclared identifier that may introduce a new person or prop"))
        validate_page_split_policy(page, pplan, source_numbers, shots)
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
        if plan_version != CANON_VERSION:
            first = panel_plan_for(pplan, 1)
            tag = str(first.get("shot_data_camera_tag", ""))
            tokens = normalize_tag_tokens(tag)
            pos = bool(tokens & POSITIVE_ANCHOR)
            neg = bool(tokens & NEGATIVE_ANCHOR)
            drawn = str(first.get("drawn_camera_tag", ""))
            override = "master wide/full spatial anchor" in drawn.lower()
            if neg and not override:
                page.findings.append(issue("G1-11", "fail", f"{page.name}/PANEL-1/drawn_camera_tag", tag, "legacy negative anchor tag lacks its legacy spatial override"))
            if (pos and neg) or (not pos and not neg):
                page.findings.append(issue("G1-11", "warn", f"{page.name}/PANEL-1", tag, "legacy anchor decision uncertain; regeneration is required"))

    if pages:
        expected_sources = list(shots)
        missing = [number for number in expected_sources if number not in all_source_occurrences]
        unexpected = [number for number in all_source_occurrences if number not in shots]
        if missing:
            pages[0].findings.append(issue("G1-15", "fail", "panel_plan/source_coverage", ",".join(map(str, missing)), "every shot_data source shot must be covered"))
        if unexpected:
            pages[0].findings.append(issue("G1-15", "fail", "panel_plan/source_coverage", ",".join(map(str, unexpected)), "panel_plan contains unknown source shots"))
        duplicate_native = sorted({number for number in native_sources if native_sources.count(number) > 1})
        if duplicate_native:
            pages[0].findings.append(issue("G1-15", "fail", "panel_plan/native_sources", ",".join(map(str, duplicate_native)), "each source shot must have exactly one native panel"))
        if native_sources != expected_sources:
            pages[0].findings.append(issue("G1-15", "fail", "panel_plan/native_source_order", ",".join(map(str, native_sources)), f"expected exact source order {','.join(map(str, expected_sources))}"))


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


def finding_to_review_reason(finding: Finding) -> dict[str, str]:
    field = finding.field or "PACKAGE"
    prefix = field.split("/", 1)[0]
    page = prefix if re.fullmatch(r"PAGE-\d{2}", prefix) else "PACKAGE"
    return {"code": finding.check, "page": page, "message": finding.context or finding.token or "Review required."}


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


def split_review_findings(panel_plan: dict[str, Any], shot_data: dict[str, Any] | None) -> list[Finding]:
    if not isinstance(shot_data, dict):
        return []
    source_shots = {
        shot.get("shot_no"): shot
        for shot in shot_data.get("shots", [])
        if isinstance(shot, dict) and isinstance(shot.get("shot_no"), int) and not isinstance(shot.get("shot_no"), bool)
    }
    logs = {
        str(item.get("scene_id")): item
        for item in shot_data.get("continuity_logs", [])
        if isinstance(item, dict) and item.get("scene_id")
    }
    findings: list[Finding] = []
    seen: set[tuple[str, str]] = set()
    for page in plan_pages(panel_plan):
        if not isinstance(page, dict):
            continue
        page_name = str(page.get("page", "UNKNOWN"))
        policy = str(page.get("page_split_policy", ""))
        numbers = unique_in_order(
            [
                str(panel.get("source_shot"))
                for panel in panel_plan_items(page)
                if isinstance(panel, dict) and isinstance(panel.get("source_shot"), int) and not isinstance(panel.get("source_shot"), bool)
            ]
        )
        shots = [source_shots.get(int(number)) for number in numbers if int(number) in source_shots]
        scene_ids = unique_in_order([str(shot.get("scene_id", "")) for shot in shots if isinstance(shot, dict)])
        layers = unique_in_order([reality_layer_from_source(shot, logs) for shot in shots if isinstance(shot, dict)])
        if len(scene_ids) > 1 or "intentional_cross_scene_bridge" in policy:
            key = (page_name, "R-CROSS-SCENE")
            if key not in seen:
                findings.append(issue("R-CROSS-SCENE", "warn", f"{page_name}/page_split_policy", policy, "page must be split at the scene boundary before release"))
                seen.add(key)
        if len(layers) > 1 or "intentional_layer_bridge" in policy:
            key = (page_name, "R-CROSS-LAYER")
            if key not in seen:
                findings.append(issue("R-CROSS-LAYER", "warn", f"{page_name}/page_split_policy", policy, "page must be split at the reality-layer boundary before release"))
                seen.add(key)
        if bool(page.get("sparse_page")) or len(numbers) < 9:
            key = (page_name, "R-SPARSE-UNIQUENESS")
            if key not in seen:
                findings.append(issue("R-SPARSE-UNIQUENESS", "warn", f"{page_name}/sparse_page", str(page.get("sparse_page")), "sparse page requires a new unique-angle plan before release"))
                seen.add(key)
        if shots:
            first_tag = camera_tag_from_shot(shots[0])
            if normalize_tag_tokens(first_tag) & NEGATIVE_ANCHOR:
                key = (page_name, "R-FIRST-SHOT-ANCHOR")
                if key not in seen:
                    findings.append(issue("R-FIRST-SHOT-ANCHOR", "warn", f"{page_name}/PANEL-1", first_tag, "first source shot is not a reliable spatial anchor and requires review without camera rewrite"))
                    seen.add(key)
    return findings


def validate_deriver_parity(
    panel_plan: dict[str, Any],
    final_prompts: str,
    shot_data: dict[str, Any] | None,
    mode: str,
    findings: list[Finding],
) -> None:
    if (
        mode != "full"
        or panel_plan.get("version") != CANON_VERSION
        or panel_plan.get("release_ready") is not True
        or not isinstance(shot_data, dict)
    ):
        return
    try:
        deriver = load_deriver_contract()
        logs = deriver.scene_logs(shot_data)
        chunks = deriver.page_chunks(shot_data.get("shots", []), 9, logs)
        expected_plan = deriver.build_panel_plan(shot_data, chunks)
        expected_plan["release_ready"] = panel_plan.get("release_ready")
        expected_plan["review_required_reasons"] = panel_plan.get("review_required_reasons")
        if isinstance(panel_plan.get("forbidden_prompt_tokens_extra"), list):
            expected_plan["forbidden_prompt_tokens_extra"] = panel_plan["forbidden_prompt_tokens_extra"]
        expected_prompts = "\n\n".join(
            deriver.page_prompt(page_no, chunk, logs, sparse=False)
            for page_no, chunk in enumerate(chunks, 1)
        )
    except Exception as exc:
        findings.append(issue("G1-17", "fail", "deriver_contract", type(exc).__name__, f"cannot rebuild deterministic v2.0.3 package: {exc}"))
        return

    actual_plan_text = json.dumps(panel_plan, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    expected_plan_text = json.dumps(expected_plan, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    if actual_plan_text != expected_plan_text:
        findings.append(issue("G1-17", "fail", "panel_plan", sha256_text(actual_plan_text), f"deterministic plan mismatch; expected sha256 {sha256_text(expected_plan_text)}"))
    if nfc(final_prompts) != nfc(expected_prompts):
        findings.append(issue("G1-18", "fail", "final_prompts", sha256_text(final_prompts), f"deterministic prompt mismatch; expected sha256 {sha256_text(expected_prompts)}"))


def validate(
    panel_plan: dict[str, Any],
    final_prompts: str,
    *,
    mode: str = "full",
    shot_data: dict[str, Any] | None = None,
    canon_path: Path | None = None,
    panel_plan_path: Path | None = None,
    shot_data_path: Path | None = None,
    compiled_path: str = "final_image_prompts.compiled.md",
) -> dict[str, Any]:
    canon_version, canon_blocks, canon_hashes, canon_findings = extract_canon(canon_path)
    skill_path = Path(__file__).resolve().parents[1] / "SKILL.md"
    _, skill_blocks, skill_findings = extract_skill_inline_canon(skill_path)
    pages = split_pages(final_prompts)
    global_findings: list[Finding] = [*canon_findings, *skill_findings]
    validate_prompt_plan_structure(pages, panel_plan, global_findings)
    validate_release_contract(panel_plan, mode, global_findings)
    split_findings = split_review_findings(panel_plan, shot_data)
    global_findings.extend(split_findings)
    if not split_findings:
        validate_deriver_parity(panel_plan, final_prompts, shot_data, mode, global_findings)
    snapshot_status = "match"
    for name in EXPECTED_CANON_TEXTS:
        expected = FACTORY_HASHES.get(name)
        actual = canon_hashes.get(name)
        if actual != expected:
            snapshot_status = "TAMPERED"
            global_findings.append(issue("G0-00", "fail", f"canon:{name}", actual or "missing", "canon hash differs; acceptance bypass is disabled"))
        inline = skill_blocks.get(name)
        if inline is None or sha256_text(inline) != expected:
            snapshot_status = "TAMPERED"
            global_findings.append(issue("G0-00", "fail", f"SKILL.md:{name}", sha256_text(inline) if inline else "missing", "SKILL inline canon differs from validator snapshot"))
        if actual is not None and inline is not None and sha256_text(inline) != actual:
            snapshot_status = "TAMPERED"
            global_findings.append(issue("G0-00", "fail", f"canon_vs_SKILL:{name}", actual, "canon file and SKILL inline authority differ"))
    compiled = compile_pages(pages, canon_blocks)
    if pages and global_findings:
        pages[0].findings[:0] = global_findings
    validate_g0(pages, compiled, panel_plan)
    validate_g1(pages, panel_plan, shot_data, mode)
    summary = summarize(pages)
    exit_code = validation_exit_code(summary)
    status = "CONTRACT_FAIL" if exit_code == 2 else "REVIEW_REQUIRED" if exit_code == 1 else "PASS"
    computed_release_ready = (
        mode == "full"
        and str(panel_plan.get("version", "")) == CANON_VERSION
        and panel_plan.get("release_ready") is True
        and exit_code == 0
    )
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
        "status": status,
        "canon_version": canon_version,
        "canon_snapshot_status": snapshot_status,
        "canon_hashes": canon_hashes,
        "batch_id": batch_id,
        "compiled_path": compiled_path,
        "compiled_text": compiled,
        "pages": report_pages,
        "summary": summary,
        "release_ready": computed_release_ready,
        "review_required_reasons": [finding_to_review_reason(finding) for page in pages for finding in page.findings if finding.severity == "warn" and finding.check.startswith("R-")],
        "hc2_adjudication_queue": hc2_queue,
        "exit_code": exit_code,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compile and validate su-image9 v2.0.3 prompts.")
    parser.add_argument("--mode", choices=["full", "text-only"], required=True)
    parser.add_argument("--canon", required=True)
    parser.add_argument("--panel-plan", required=True)
    parser.add_argument("--final-prompts", required=True)
    parser.add_argument("--shot-data")
    parser.add_argument("--report", required=True)
    parser.add_argument("--out", required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.mode == "full" and not args.shot_data:
        Path(args.report).write_text(json.dumps({"status": "CONTRACT_FAIL", "exit_code": 2, "release_ready": False, "summary": {"fail": 1, "warn": 0}, "error": "full mode requires --shot-data"}, ensure_ascii=False, indent=2), encoding="utf-8")
        return 2
    try:
        panel_plan_path = Path(args.panel_plan)
        shot_data_path = Path(args.shot_data) if args.shot_data else None
        panel_plan = load_json(panel_plan_path)
        shot_data = load_json(shot_data_path) if shot_data_path else None
        if not isinstance(panel_plan, dict):
            raise ContractInputError("panel_plan root must be a JSON object")
        if args.mode == "full" and not isinstance(shot_data, dict):
            raise ContractInputError("shot_data root must be a JSON object")
        prompt_text = Path(args.final_prompts).read_text(encoding="utf-8")
        result = validate(
            panel_plan,
            prompt_text,
            mode=args.mode,
            shot_data=shot_data,
            canon_path=Path(args.canon),
            panel_plan_path=panel_plan_path,
            shot_data_path=shot_data_path,
            compiled_path=args.out,
        )
        Path(args.out).write_text(result["compiled_text"], encoding="utf-8")
        report = {key: value for key, value in result.items() if key != "compiled_text"}
        Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return int(result["exit_code"])
    except (json.JSONDecodeError, ContractInputError) as exc:
        payload = {"status": "CONTRACT_FAIL", "exit_code": 2, "release_ready": False, "summary": {"fail": 1, "warn": 0}, "error": str(exc)}
        Path(args.report).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return 2
    except Exception as exc:
        payload = {"status": "TOOL_ERROR", "exit_code": 3, "release_ready": False, "summary": {"fail": 1, "warn": 0}, "error": str(exc)}
        Path(args.report).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
