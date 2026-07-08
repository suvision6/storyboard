#!/usr/bin/env python3
"""Validator/compiler for su-image9 v1.7.1 final prompts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import string
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

CANON_VERSION = "1.7.1"
CANON_BLOCKS = [
    "STYLE_LOCK",
    "CANVAS_LOCK",
    "REFERENCE_LOCK",
    "REFERENCE_LOCK_TEXT_ONLY",
    "NEGATIVE_LOCK",
]
REQUIRED_PAGE_BLOCKS = [
    "STYLE_LOCK",
    "CANVAS_LOCK",
    "REFERENCE_LOCK",
    "CONTINUITY_LOCK",
    "PANEL_TASKS",
    "NEGATIVE_LOCK",
]
PANEL_FIELDS = [
    "SOURCE SHOT",
    "MUST MATCH SHOT_DATA CAMERA TAG",
    "DRAWN CAMERA TAG",
    "VISIBLE ONLY",
    "ACTION / COMPOSITION",
    "FLOOR / AXIS DELTA",
    "PROP STATE",
]
CONTENT_FIELDS = {"ACTION / COMPOSITION", "PROP STATE", "FLOOR / AXIS DELTA"}
PLACEHOLDER_PHRASES = {
    "page A/B",
    "foreground/background/shoulder locked",
    "as applicable",
    "allowed positions",
    "fixed objects",
    "source action phase",
    "source camera tag",
}
T1_PATTERNS = [
    r"\bcountdown\b",
    r"\bnumeric countdown\b",
    r"\bbpm\b",
    r"\bhr\b",
    r"\becg\b",
    r"\bmonitor\b",
    r"\bscreen text\b",
    r"\breadable\b",
    r"\bdigits\b",
    r"\bnumerals\b",
    r"\btimer\b",
    r"\bclock face with numbers\b",
    r"\u5012\u8ba1\u65f6",
    r"\u76d1\u62a4\u4eea",
    r"\u5fc3\u8df3\u4eea",
    r"\u8bfb\u6570",
    r"\u5c4f\u5e55\u6587\u5b57",
]
T2_WORDS = {
    "red", "reddish", "crimson", "scarlet", "ruby", "blood-red",
    "gold", "golden", "gilded", "blue", "azure", "cyan", "navy",
    "green", "emerald", "jade-green", "yellow", "amber", "purple",
    "violet", "pink", "magenta", "orange", "brown", "colorful",
    "multicolored", "saturated", "photoreal", "photorealistic",
    "hyperrealistic", "portrait", "likeness", "masterpiece", "cinematic",
    "studio", "lighting", "skin", "texture", "film", "grain",
}
T2_CHINESE = [
    "\u7ea2", "\u8d64", "\u6731\u7ea2", "\u91d1\u8272", "\u91d1\u9ed1",
    "\u84dd", "\u7eff", "\u9ec4", "\u7d2b", "\u7c89", "\u6a59", "\u68d5",
    "\u5f69\u8272", "\u4e03\u5f69", "\u7cbe\u4fee",
    "\u771f\u4eba\u76f8\u4f3c", "\u7167\u7247\u8d28\u611f", "\u7167\u7247\u7ea7",
]
T3_WHITELIST = {
    "sketch", "sketchy", "blocking", "storyboard", "simplified", "structural",
    "sparse", "clean", "rough", "loose", "minimal", "flat", "schematic",
    "pencil", "line", "linework", "outline", "silhouette", "low-detail",
    "black-and-white", "monochrome", "gray", "grey", "pale", "dark", "light",
    "wide", "tight", "shallow", "deep",
}
T3_PROBE = {"atmospheric", "dramatic", "beautiful", "elegant", "moody", "cinematic"}
POSITIVE_ANCHOR = {"master", "establishing", "wide", "full", "\u5168\u666f", "\u5927\u8fdc\u666f"}
NEGATIVE_ANCHOR = {
    "close", "close-up", "medium", "over-shoulder", "ots", "insert", "pov",
    "reaction", "black", "\u7279\u5199", "\u8fd1\u666f", "\u4e2d\u666f",
    "\u8fc7\u80a9", "\u53cd\u5e94", "\u9ed1\u573a",
}
STOPWORDS = {"a", "an", "the", "of", "to", "in", "on", "at", "by", "for", "with", "from", "and", "or", "specific", "named"}
BOOLEAN_PROP_VALUES = {"yes", "no", "true", "false", "present", "absent"}
BARE_PROP_OWNERSHIP_PATTERNS = [
    r"^\s*owned\b",
    r"\bownership unchanged\b",
    r"\bsource ownership unchanged\b",
]
VFX_PROP_TOKENS = [
    "\u7070\u767d\u8272\u96fe\u6c14",
    "\u7070\u767d\u8272\u5149\u70b9",
    "\u7070\u767d\u8272\u5149\u5c18",
    "\u91d1\u9ed1\u96fe\u4f53",
    "\u91d1\u9ed1\u8272\u89e6\u987b",
    "\u9f99\u5377\u98ce\u96fe\u4f53",
    "\u8d64\u5149",
    "\u8d64\u8272\u5149\u70b9",
    "\u8d64\u8272\u5149\u6d77",
    "\u8d64\u8272\u6b8b\u5149",
    "\u767d\u5149",
    "\u80fd\u91cf\u4f59\u6ce2",
    "\u971c\u5c42",
    "\u7070\u70ec",
    "\u900f\u660e\u5149\u5899",
    "\u96fe\u8760\u8760",
    "\u9ed1\u96fe",
    "\u9ed1\u96fe\u6838\u5fc3",
]
VFX_STATE_MARKERS = {
    "vfx-state",
    "body-state",
    "environment effect",
    "vfx/body-state",
    "vapor effect",
    "particle effect",
}

EXPECTED_CANON_TEXTS = {
    "STYLE_LOCK": """STYLE_LOCK:\nUnified black-and-white director blocking sketch. Same clean pencil line width, same light gray density, low-detail faces, simple costume silhouettes, sparse structural environment. Prioritize composition, camera viewpoint, character placement, floor plane, object positions, action phase, and continuity over beauty, texture, atmosphere, or face matching. Not a polished illustration, not manga, not photoreal.""",
    "CANVAS_LOCK": """CANVAS_LOCK:\nOne wide horizontal 16:9 canvas. Exact clean 3x3 storyboard grid, nine equal horizontal 16:9 panels, straight borders and gutters. No text or labels inside the image. PANEL-1 establishes the master space; PANEL-2 to PANEL-9 inherit it unless a source shot changes state.""",
    "REFERENCE_LOCK": """REFERENCE_LOCK:\nReference images only lock identity silhouette, hairstyle silhouette, costume silhouette, prop shape, and prop ownership. Draw all characters as simplified director blocking sketch figures, not portrait renderings. Do not copy photo texture, skin detail, lighting, color, refinement level, or face matching.""",
    "REFERENCE_LOCK_TEXT_ONLY": """REFERENCE_LOCK:\nNo reference images are bound. Character identity, hairstyle, costume silhouette, and prop ownership are text-defined only, as stated in panel tasks. Draw all characters as simplified director blocking sketch figures. Do not invent photographic likeness, skin detail, lighting style, or color for any character.""",
    "NEGATIVE_LOCK": """NEGATIVE_LOCK:\nNo text, labels, captions, panel numbers, shot numbers, subtitles, arrows, UI, monitor graphics, logos, watermarks, Chinese or English writing. No photorealism, realistic skin, portrait rendering, cinematic lighting, color, CGI, 3D render, painting, polished illustration, manga/comic layout, collage, poster, heavy texture, dense environment rendering, mixed panel sizes.""",
}
FACTORY_HASHES = {name: hashlib.sha256(text.encode("utf-8")).hexdigest() for name, text in EXPECTED_CANON_TEXTS.items()}


@dataclass
class Finding:
    check: str
    severity: str
    field: str
    token: str = ""
    context: str = ""


@dataclass
class Panel:
    name: str
    fields: dict[str, str]


@dataclass
class Page:
    name: str
    text: str
    blocks: dict[str, str]
    panels: list[Panel]
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


def normalize_for_compare(text: str) -> str:
    return re.sub(r"\s+", " ", nfc(text)).strip()


def issue(check: str, severity: str, field: str, token: str = "", context: str = "") -> Finding:
    return Finding(check, severity, field, token, context[:240])


def extract_canon(path: Path | None) -> tuple[str, dict[str, str], dict[str, str]]:
    if path is None:
        return CANON_VERSION, EXPECTED_CANON_TEXTS.copy(), FACTORY_HASHES.copy()
    text = path.read_text(encoding="utf-8")
    version_match = re.search(r"<!--\s*canon-version:\s*([^\s]+)\s*-->", text)
    version = version_match.group(1) if version_match else "unknown"
    blocks: dict[str, str] = {}
    for match in re.finditer(r"(?ms)^###\s+canon:([A-Z_]+)\s*\n\s*```text\s*\n(.*?)\n```", text):
        name = match.group(1).strip()
        body = nfc(match.group(2))
        blocks[name] = body
    # Store with headers because prompts include block headings.
    result = {}
    for name, body in blocks.items():
        result[name] = body if body.startswith(name.replace("_TEXT_ONLY", "") + ":") else body
    hashes = {name: sha256_text(value) for name, value in result.items()}
    return version, result, hashes


def split_pages(text: str) -> list[Page]:
    text = nfc(text)
    matches = list(re.finditer(r"(?m)^#\s+(PAGE-\d{2}|P\d{2})\b.*$", text))
    if not matches:
        return [Page("PAGE-01", text, {}, [])]
    pages: list[Page] = []
    for idx, match in enumerate(matches):
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        raw_name = match.group(1)
        name = raw_name if raw_name.startswith("PAGE-") else f"PAGE-{raw_name[1:]}"
        pages.append(Page(name, text[match.end():end].strip(), {}, []))
    return pages


def parse_blocks(page: Page) -> None:
    headers = list(re.finditer(r"(?m)^(STYLE_LOCK|CANVAS_LOCK|REFERENCE_LOCK|CONTINUITY_LOCK|PANEL_TASKS(?:\s+P\d{2}-P\d{2})?|NEGATIVE_LOCK):\s*$", page.text))
    blocks: dict[str, str] = {}
    for idx, header in enumerate(headers):
        raw_name = header.group(1)
        name = "PANEL_TASKS" if raw_name.startswith("PANEL_TASKS") else raw_name
        end = headers[idx + 1].start() if idx + 1 < len(headers) else len(page.text)
        blocks[name] = page.text[header.end():end].strip()
    page.blocks = blocks


def parse_panels(page: Page) -> None:
    block = page.blocks.get("PANEL_TASKS", "")
    matches = list(re.finditer(r"(?m)^(PANEL-(\d+)|P(\d{2})):\s*$", block))
    panels: list[Panel] = []
    for idx, match in enumerate(matches):
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(block)
        raw_no = match.group(2) or str(int(match.group(3)))
        name = f"PANEL-{int(raw_no)}"
        body = block[match.end():end].strip()
        fields: dict[str, str] = {}
        field_matches = list(re.finditer(r"(?m)^(SOURCE SHOT|MUST MATCH SHOT_DATA CAMERA TAG|DRAWN CAMERA TAG|VISIBLE ONLY|ACTION / COMPOSITION|FLOOR / AXIS DELTA|PROP STATE):\s*(.*)$", body))
        for fidx, fmatch in enumerate(field_matches):
            fend = field_matches[fidx + 1].start() if fidx + 1 < len(field_matches) else len(body)
            first = fmatch.group(2).strip()
            rest = body[fmatch.end():fend].strip()
            fields[fmatch.group(1)] = (first + ("\n" + rest if rest else "")).strip()
        panels.append(Panel(name, fields))
    page.panels = panels


def render_page(page: Page) -> str:
    order = ["STYLE_LOCK", "CANVAS_LOCK", "REFERENCE_LOCK", "CONTINUITY_LOCK", "PANEL_TASKS", "NEGATIVE_LOCK"]
    parts = [f"# {page.name}"]
    for name in order:
        if name in page.blocks:
            suffix = " P01-P09" if name == "PANEL_TASKS" else ""
            parts.append(f"{name}{suffix}:\n{page.blocks[name]}")
    return "\n\n".join(parts).strip()


def compile_pages(pages: list[Page], canon_blocks: dict[str, str], strict: bool) -> str:
    for page in pages:
        parse_blocks(page)
        for required in REQUIRED_PAGE_BLOCKS:
            if required not in page.blocks:
                page.findings.append(issue("G0-12", "fail", page.name, required, "required block missing"))
        for block_name in ["STYLE_LOCK", "CANVAS_LOCK", "REFERENCE_LOCK", "NEGATIVE_LOCK"]:
            if block_name not in page.blocks:
                continue
            value = nfc(page.blocks[block_name])
            marker = re.fullmatch(r"@CANON\(([A-Z_]+)\)", value)
            if marker:
                canon_name = marker.group(1)
                if canon_name not in canon_blocks:
                    page.findings.append(issue("G0-02", "fail", f"{page.name}/{block_name}", canon_name, "unknown canon marker"))
                    continue
                page.blocks[block_name] = canon_blocks[canon_name]
                continue
            expected_name = "REFERENCE_LOCK_TEXT_ONLY" if "No reference images are bound" in value else block_name
            expected = canon_blocks.get(expected_name) or canon_blocks.get(block_name)
            if expected and normalize_for_compare(value) != normalize_for_compare(expected):
                if strict:
                    page.findings.append(issue("G0-02", "fail", f"{page.name}/{block_name}", block_name, "canon block differs under --strict-canon"))
                else:
                    page.blocks[block_name] = expected
                    page.canon_autofixed = True
                    page.findings.append(issue("G0-02", "warn", f"{page.name}/{block_name}", block_name, "canon_autofixed=true"))
        parse_panels(page)
    return "\n\n".join(render_page(page) for page in pages).strip() + "\n"


def codepoint_len(text: str) -> int:
    return len(nfc(text))


def normalized_sentence(text: str) -> str:
    text = re.sub(r"\s+", " ", text.lower()).strip()
    return text.rstrip(".;? ")


def sentence_repeat_warn(value: str) -> bool:
    parts = [normalized_sentence(p) for p in re.split(r"[.;?]", value) if normalized_sentence(p)]
    if len(parts) < 2:
        return False
    repeats = len(parts) - len(set(parts))
    return repeats / len(parts) > 0.5


def scan_tokens(text: str, page: Page, field: str) -> None:
    protected = text.replace("non-readable", "")
    lower = protected.lower()
    for pattern in T1_PATTERNS:
        if re.search(pattern, lower, re.I):
            page.findings.append(issue("G0-06", "fail", field, pattern, text))
    cleaned = lower.replace("metal", "")
    words = set(re.findall(r"[a-z][a-z-]*", cleaned))
    for word in sorted(words & T2_WORDS):
        page.findings.append(issue("G0-07", "fail", field, word, text))
    for token in T2_CHINESE:
        if token in protected:
            page.findings.append(issue("G0-07", "fail", field, token, text))
    for token in sorted(words & T3_PROBE):
        if token not in T3_WHITELIST:
            page.findings.append(issue("G0-08", "warn", field, token, text))
    for phrase in PLACEHOLDER_PHRASES:
        if phrase.lower() in lower:
            page.findings.append(issue("G0-09", "fail", field, phrase, text))


def visible_props_value(visible_only: str) -> str:
    match = re.search(r"\bprops\s*=\s*([^.;\n]+)", visible_only, re.I)
    return match.group(1).strip() if match else ""


def scan_prop_semantics(panel: Panel, page: Page) -> None:
    visible = panel.fields.get("VISIBLE ONLY", "")
    prop_state = panel.fields.get("PROP STATE", "")
    props_value = visible_props_value(visible)
    props_lower = props_value.lower()
    if props_lower in BOOLEAN_PROP_VALUES:
        page.findings.append(
            issue(
                "G0-14",
                "fail",
                f"{page.name}/{panel.name}/VISIBLE ONLY",
                f"props={props_value}",
                "ambiguous boolean prop value is not allowed; use props=none or concrete physical props",
            )
        )
    for token in VFX_PROP_TOKENS:
        if token and token in props_value:
            page.findings.append(
                issue(
                    "G0-14",
                    "fail",
                    f"{page.name}/{panel.name}/VISIBLE ONLY",
                    token,
                    "VFX/body-state/environment effect must not be listed as a physical prop",
                )
            )
    normalized_prop_state = prop_state.lower().strip()
    for pattern in BARE_PROP_OWNERSHIP_PATTERNS:
        if re.search(pattern, normalized_prop_state):
            page.findings.append(
                issue(
                    "G0-14",
                    "fail",
                    f"{page.name}/{panel.name}/PROP STATE",
                    pattern,
                    "bare ownership wording is not allowed; name a concrete physical prop or state no physical prop",
                )
            )
    marker_present = any(marker in normalized_prop_state for marker in VFX_STATE_MARKERS)
    for token in VFX_PROP_TOKENS:
        if token and token in prop_state and not marker_present:
            page.findings.append(
                issue(
                    "G0-14",
                    "fail",
                    f"{page.name}/{panel.name}/PROP STATE",
                    token,
                    "VFX/body-state/environment effect must be explicitly classified, not treated as prop ownership",
                )
            )


def entity_terms(value: Any) -> set[str]:
    raw: list[str] = []
    if value is None:
        return set()
    if isinstance(value, list):
        raw.extend(str(v) for v in value)
    else:
        raw.append(str(value))
    terms: set[str] = set()
    for item in raw:
        if re.search(r"[\u4e00-\u9fff]", item):
            cleaned = item.strip()
            if cleaned:
                terms.add(cleaned.lower())
        for word in re.findall(r"[A-Za-z][A-Za-z0-9_-]*", item.lower()):
            if len(word) >= 3 and word not in STOPWORDS:
                terms.add(word)
    return terms


def text_has_entity(text: str, terms: set[str]) -> bool:
    lower = text.lower()
    for term in terms:
        if re.search(r"[\u4e00-\u9fff]", term):
            if term in lower:
                return True
        elif re.search(rf"\b{re.escape(term)}\b", lower):
            return True
    return False


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


def panel_plan_for(page_plan: dict[str, Any], panel: Panel) -> dict[str, Any]:
    panels = page_plan.get("panels")
    if not isinstance(panels, list):
        return {}
    target = int(panel.name.split("-")[1])
    for item in panels:
        raw = str(item.get("panel", item.get("panel_id", "")))
        m = re.search(r"(\d+)", raw)
        if m and int(m.group(1)) == target:
            return item
    return panels[target - 1] if target - 1 < len(panels) else {}


def shot_index(shot_data: dict[str, Any] | None) -> dict[int, dict[str, Any]]:
    result = {}
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


def validate_g0(pages: list[Page], compiled_text: str, panel_plan: dict[str, Any]) -> None:
    for page in pages:
        page_text = render_page(page)
        page.char_count = codepoint_len(page_text)
        if page.char_count > 5000:
            page.budget_status = "fail"
            page.findings.append(issue("G0-04", "fail", page.name, str(page.char_count), "page exceeds 5000 codepoints"))
        elif page.char_count > 4500:
            page.budget_status = "warn"
            page.findings.append(issue("G0-04", "warn", page.name, str(page.char_count), "page exceeds 4500 codepoints"))
        else:
            pplan = page_plan_for(page, panel_plan)
            lower_bound = 1800 if pplan.get("sparse_page") else 2500
            if page.char_count < lower_bound:
                page.budget_status = "fail"
                page.findings.append(issue("G0-04", "fail", page.name, str(page.char_count), "page below budget lower bound"))
            else:
                page.budget_status = "pass"
        if re.search(r"\bP\d{2}:\s*$", page.blocks.get("PANEL_TASKS", ""), re.M):
            page.findings.append(issue("G0-11", "fail", page.name, "Pxx", "old panel naming is not allowed"))
        if re.search(r"^#\s+P\d{2}\b", page.text, re.M):
            page.findings.append(issue("G0-11", "fail", page.name, "Pxx", "old page naming is not allowed"))
        if len(page.panels) != 9:
            page.findings.append(issue("G0-12", "fail", page.name, str(len(page.panels)), "page must contain nine panels"))
        triples: dict[tuple[str, str, str], str] = {}
        for panel in page.panels:
            for field_name in PANEL_FIELDS:
                if not panel.fields.get(field_name):
                    page.findings.append(issue("G0-12", "fail", f"{page.name}/{panel.name}", field_name, "required field missing"))
            for field_name, value in panel.fields.items():
                if field_name in CONTENT_FIELDS:
                    scan_tokens(value, page, f"{page.name}/{panel.name}/{field_name}")
                    if sentence_repeat_warn(value):
                        page.findings.append(issue("G0-05", "warn", f"{page.name}/{panel.name}/{field_name}", "repeated sentences", value))
            scan_prop_semantics(panel, page)
            triad = tuple(normalized_sentence(panel.fields.get(name, "")) for name in ["ACTION / COMPOSITION", "FLOOR / AXIS DELTA", "PROP STATE"])
            if all(triad):
                if triad in triples:
                    page.findings.append(issue("G0-05", "fail", f"{page.name}/{panel.name}", triples[triad], "same content triad repeated"))
                else:
                    triples[triad] = panel.name
        scan_tokens(page.blocks.get("CONTINUITY_LOCK", ""), page, f"{page.name}/CONTINUITY_LOCK")
        pplan = page_plan_for(page, panel_plan)
        entities = set()
        for key in ["fixed_anchors", "axis_endpoint_a", "axis_endpoint_b", "floor_plane_lock", "floor_plane"]:
            entities |= entity_terms(pplan.get(key))
        if entities:
            if not text_has_entity(page.blocks.get("CONTINUITY_LOCK", ""), entities):
                page.findings.append(issue("G0-10", "fail", f"{page.name}/CONTINUITY_LOCK", "entity_intersection", "zero intersection with panel_plan entities"))
            for panel in page.panels:
                if not text_has_entity(panel.fields.get("FLOOR / AXIS DELTA", ""), entities):
                    page.findings.append(issue("G0-10", "fail", f"{page.name}/{panel.name}/FLOOR / AXIS DELTA", "entity_intersection", "zero intersection with panel_plan entities"))


def validate_g1(pages: list[Page], panel_plan: dict[str, Any], shot_data: dict[str, Any] | None, mode: str) -> None:
    if mode == "full" and not shot_data:
        pages[0].findings.append(issue("G1-00", "fail", "shot_data", "missing", "full mode requires --shot-data"))
        return
    if mode != "full":
        return
    shots = shot_index(shot_data)
    for page in pages:
        pplan = page_plan_for(page, panel_plan)
        for panel in page.panels:
            pp = panel_plan_for(pplan, panel)
            source_raw = panel.fields.get("SOURCE SHOT", "")
            m = re.search(r"\d+", source_raw)
            source_no = int(m.group(0)) if m else None
            if source_no is None or source_no not in shots:
                page.findings.append(issue("G1-01", "fail", f"{page.name}/{panel.name}/SOURCE SHOT", source_raw, "source shot not found"))
                continue
            if pp.get("source_shot") is not None and int(pp.get("source_shot")) != source_no:
                page.findings.append(issue("G1-01", "fail", f"{page.name}/{panel.name}/SOURCE SHOT", source_raw, "source shot differs from panel_plan"))
            shot_tag = camera_tag_from_shot(shots[source_no])
            must_tag = panel.fields.get("MUST MATCH SHOT_DATA CAMERA TAG", "")
            plan_tag = str(pp.get("source_camera_tag", ""))
            if shot_tag and normalize_for_compare(must_tag) != normalize_for_compare(shot_tag):
                page.findings.append(issue("G1-02", "fail", f"{page.name}/{panel.name}/MUST MATCH SHOT_DATA CAMERA TAG", must_tag, f"expected {shot_tag}"))
            if plan_tag and normalize_for_compare(must_tag) != normalize_for_compare(plan_tag):
                page.findings.append(issue("G1-03", "fail", f"{page.name}/{panel.name}/MUST MATCH_SHOT_DATA CAMERA TAG", must_tag, f"expected panel_plan {plan_tag}"))
            drawn = panel.fields.get("DRAWN CAMERA TAG", "")
            if pp.get("drawn_camera_tag") and normalize_for_compare(drawn) != normalize_for_compare(str(pp.get("drawn_camera_tag"))):
                page.findings.append(issue("G1-04", "fail", f"{page.name}/{panel.name}/DRAWN CAMERA TAG", drawn, f"expected {pp.get('drawn_camera_tag')}"))
        if page.panels:
            first = page.panels[0]
            first_plan = panel_plan_for(pplan, first)
            tag = str(first_plan.get("source_camera_tag") or first.fields.get("MUST MATCH SHOT_DATA CAMERA TAG", ""))
            tokens = normalize_tag_tokens(tag)
            pos = bool(tokens & POSITIVE_ANCHOR)
            neg = bool(tokens & NEGATIVE_ANCHOR)
            drawn = first.fields.get("DRAWN CAMERA TAG", "")
            override = "master wide/full spatial anchor" in drawn.lower()
            if neg and not override:
                page.findings.append(issue("G1-11", "fail", f"{page.name}/{first.name}/DRAWN CAMERA TAG", tag, "negative anchor tag requires override"))
            if (pos and neg) or (not pos and not neg):
                page.findings.append(issue("G1-11", "warn", f"{page.name}/{first.name}", tag, "anchor decision uncertain; HC-1 required"))
                if pplan.get("anchor_decision") != "human_confirmed":
                    page.findings.append(issue("G1-11", "fail", f"{page.name}/{first.name}", tag, "panel_plan missing anchor_decision=human_confirmed"))


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
    for name in CANON_BLOCKS:
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
    parser = argparse.ArgumentParser(description="Compile and validate su-image9 v1.7.1 prompts.")
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
