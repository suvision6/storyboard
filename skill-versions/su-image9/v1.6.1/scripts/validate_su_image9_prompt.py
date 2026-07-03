#!/usr/bin/env python3
"""Fact validator for su-image9 1.6.1 final prompts.

The validator intentionally rejects prompt-shaped text that only contains
required headings. It compares each page and panel against panel_plan.json and
shot_data.json, then applies prompt-budget and image-generation gate checks.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


REQUIRED_PAGE_BLOCKS = [
    "STYLE_LOCK:",
    "CANVAS_LOCK:",
    "REFERENCE_LOCK:",
    "CONTINUITY_LOCK:",
    "PANEL_TASKS P01-P09:",
    "NEGATIVE_LOCK:",
]

OLD_16_LAYER_TOKENS = (
    "DIRECTOR_BLOCKING_SKETCH_LAYER:",
    "PROJECT_VISUAL_PROFILE:",
    "SCENE_LAYER:",
    "CAMERA_RULE_LAYER:",
    "PANEL_1_MASTER_SPATIAL_LAYOUT_ANCHOR:",
    "FIXED_OBJECT_SCREEN_PROJECTION:",
    "ELEVATION_AND_DEPTH_LOCK:",
    "CAMERA_COMPOSITION_LOCK:",
    "OBJECT_VISIBILITY_AND_BOUNDARIES:",
    "SPLIT_COMPOSITION_DIFFERENCE_LOCK:",
    "PROP_TEMPORAL_PHASE_LOCK:",
    "PANEL_LAYER P01-P09:",
)

PANEL_FIELDS = [
    "SOURCE SHOT:",
    "MUST MATCH SHOT_DATA CAMERA TAG:",
    "VISIBLE ONLY:",
    "ACTION / COMPOSITION:",
    "FLOOR / AXIS DELTA:",
    "PROP STATE:",
]

PANEL_PLAN_REQUIRED_FIELDS = [
    "source_shot",
    "source_camera_tag",
    "drawn_camera_tag",
    "p01_anchor_override",
    "visible_characters",
    "visible_props",
    "prop_temporal_state",
    "screen_left_right_lock",
    "axis_endpoint_a",
    "axis_endpoint_b",
    "floor_plane",
    "forbidden_standing_zone",
]

ROOT_PLAN_REQUIRED_FIELDS = [
    "reference_binding_status",
    "forbidden_prompt_tokens",
]

PLACEHOLDER_TOKENS = (
    "page A/B",
    "foreground/background/shoulder locked",
    "as applicable",
    "allowed positions",
    "fixed objects",
    "source action phase",
    "source camera tag",
)

COUNTDOWN_OR_UI_PATTERNS = (
    r"\bcountdown\b",
    r"abstract\s+countdown",
    r"数字\s*[0-9一二三四五六七八九十]",
    r"\bbpm\b",
    r"\bHR\b",
    r"\bECG\b",
    r"monitor\s+UI",
    r"readable\s+digits",
    r"监护仪",
    r"心跳仪",
)

COLOR_LEAK_PATTERNS = (
    r"红光",
    r"红色",
    r"赤光",
    r"赤色",
    r"金黑",
    r"金色",
    r"\bred\b",
    r"\bgold\b",
    r"\bgolden\b",
    r"gold-black",
)

DETAIL_PRESSURE_PATTERNS = (
    r"high detail",
    r"highly detailed",
    r"portrait likeness",
    r"photoreal reference",
    r"photographic likeness",
    r"exact face",
    r"detailed portrait",
    r"copy reference lighting",
    r"精修脸",
    r"真人相似",
    r"照片质感",
)

RELATION_CAMERA_MARKERS = ("过肩", "双人", "reverse", "OTS", "over-shoulder")

CHARACTER_CODES = {
    "林晓彤": "LX",
    "沈夜": "SY",
    "顾成": "GC",
    "顾城": "GC",
    "林晓杰": "LXJ",
    "金黑雾体": "DARK_HOSTILE_MIST",
    "LX": "LX",
    "SY": "SY",
    "GC": "GC",
    "LXJ": "LXJ",
    "DARK_HOSTILE_MIST": "DARK_HOSTILE_MIST",
}

PROP_CODES = {
    "手环": "BRACELET",
    "长棍": "STAFF",
    "倒计时": "BRACELET_PULSE",
    "灰白色雾气": "GREY_LXJ_MIST",
    "灰白色光点": "LIGHT_DUST",
    "灰白色光尘": "LIGHT_DUST",
    "灰白色残光": "LIGHT_DUST",
    "能量余波": "BRACELET_PULSE",
    "金黑雾体": "DARK_HOSTILE_MIST",
    "金黑色触须": "DARK_HOSTILE_MIST_TENDRIL",
    "黑雾核心": "DARK_HOSTILE_CORE",
    "黑雾": "DARK_HOSTILE_MIST",
    "雾蝙蝠": "DARK_HOSTILE_BATS",
    "龙卷风雾体": "DARK_HOSTILE_WALL",
    "赤光": "SY_LIGHT_DUST",
    "赤色光点": "SY_LIGHT_DUST",
    "赤色光海": "SY_LIGHT_DUST_FLOW",
    "赤色残光": "SY_LIGHT_DUST",
    "金色纹路": "STAFF_DIM_LINE",
    "白光": "WHITE_LIGHT",
    "神印": "SY_MARK",
    "霜层": "FROST_LAYER",
    "碎石": "ROCK_DEBRIS",
    "岩石裂缝": "ROCK_CRACK",
    "透明光墙": "DEFENSE_WALL",
    "亡魂轮廓": "HOSTILE_SOUL_OUTLINES",
    "气劲": "FORCE_WAVE",
    "旧伤": "OLD_WOUND",
    "灰烬": "ASH_DUST",
    "岩壁": "ROCK_WALL",
    "STAFF": "STAFF",
    "BRACELET": "BRACELET",
    "GREY_LXJ_MIST": "GREY_LXJ_MIST",
    "LIGHT_DUST": "LIGHT_DUST",
    "BRACELET_PULSE": "BRACELET_PULSE",
    "DARK_HOSTILE_MIST": "DARK_HOSTILE_MIST",
    "DARK_HOSTILE_MIST_TENDRIL": "DARK_HOSTILE_MIST_TENDRIL",
    "DARK_HOSTILE_CORE": "DARK_HOSTILE_CORE",
    "WHITE_LIGHT": "WHITE_LIGHT",
}

BRACELET_PHASES = {
    "worn": ("bracelet on wrist", "on LX wrist", "worn", "戴在手上", "手环佩戴", "手环在手腕"),
    "detaching": ("detaching", "separating", "脱落中", "正在脱落", "分离"),
    "falling": ("bracelet falling", "bracelet midair", "bracelet in air", "手环半空", "手环下落"),
    "ground": ("bracelet on ground", "fallen bracelet", "手环落地", "手环在地面"),
    "ash": ("bracelet ash", "bracelet ashes", "手环化灰", "手环灰烬"),
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def add_issue(issues: list[dict[str, str]], code: str, where: str, detail: str) -> None:
    issues.append({"code": code, "where": where, "detail": detail})


def normalize_set(values: Any, mapping: dict[str, str]) -> set[str]:
    if values in (None, "", []):
        return set()
    if isinstance(values, str):
        raw_values = [v.strip() for v in re.split(r"[,/;，、]", values)]
    else:
        raw_values = [str(v).strip() for v in values]
    result: set[str] = set()
    for value in raw_values:
        if not value or value.lower() == "none":
            continue
        result.add(mapping.get(value, value))
    return result


def camera_tag_from_shot(shot: dict[str, Any]) -> str:
    text = str(shot.get("camera_main_image", ""))
    match = re.match(r"\[([^\]]+)\]", text.strip())
    return match.group(1).strip() if match else ""


def split_pages(prompt_text: str) -> dict[str, str]:
    matches = list(re.finditer(r"(?m)^#\s*(P\d{2})\b.*$", prompt_text))
    pages: dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(prompt_text)
        pages[match.group(1)] = prompt_text[start:end].strip()
    return pages


def block_content(page_text: str, block_name: str) -> str:
    pattern = re.compile(
        re.escape(block_name) + r"\s*([\s\S]*?)(?=\n(?:"
        + "|".join(re.escape(name) for name in REQUIRED_PAGE_BLOCKS if name != block_name)
        + r")|\Z)"
    )
    match = pattern.search(page_text)
    return match.group(1).strip() if match else ""


def parse_prompt_panels(page_text: str) -> dict[str, dict[str, str]]:
    task_text = block_content(page_text, "PANEL_TASKS P01-P09:")
    panels: dict[str, dict[str, str]] = {}
    pattern = re.compile(r"(?m)^(P\d{2}):\s*$")
    matches = list(pattern.finditer(task_text))
    for index, match in enumerate(matches):
        panel_id = match.group(1)
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(task_text)
        body = task_text[start:end]
        fields: dict[str, str] = {}
        all_fields = PANEL_FIELDS + ["DRAWN CAMERA TAG:", "ANCHOR_VISIBLE_ALLOWED:"]
        for field in all_fields:
            field_pattern = re.compile(
                re.escape(field) + r"\s*([\s\S]*?)(?=\n(?:"
                + "|".join(re.escape(item) for item in all_fields)
                + r")|\Z)"
            )
            field_match = field_pattern.search(body)
            fields[field] = field_match.group(1).strip() if field_match else ""
        panels[panel_id] = fields
    return panels


def parse_int(text: str) -> int | None:
    match = re.search(r"\d+", text)
    return int(match.group(0)) if match else None


def extract_visible(visible_text: str, key: str, mapping: dict[str, str]) -> set[str]:
    variants = {
        "chars": ("chars", "characters", "char"),
        "props": ("props", "prop", "effects"),
    }[key]
    for variant in variants:
        match = re.search(rf"\b{variant}\s*=\s*([^.;\n]+)", visible_text, flags=re.IGNORECASE)
        if match:
            return normalize_set(match.group(1), mapping)
    return set()


def anchor_allowed_set(value: Any, key: str, mapping: dict[str, str]) -> set[str]:
    if isinstance(value, dict):
        return normalize_set(value.get(key) or value.get(f"{key}s"), mapping)
    if isinstance(value, list):
        return normalize_set(value, mapping)
    return normalize_set(value, mapping)


def text_has_pattern(text: str, patterns: tuple[str, ...]) -> str | None:
    for pattern in patterns:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return pattern
    return None


def bracelet_phases(text: str) -> set[str]:
    lower = text.lower()
    phases = set()
    for phase, tokens in BRACELET_PHASES.items():
        if any(token.lower() in lower for token in tokens):
            phases.add(phase)
    return phases


def has_concrete_axis(text: str) -> bool:
    required_patterns = (
        r"\bA\s*=",
        r"\bB\s*=",
        r"camera\s+side\s*=",
        r"screen\s+left\s*=",
        r"screen\s+right\s*=",
    )
    if not all(re.search(pattern, text, flags=re.IGNORECASE) for pattern in required_patterns):
        return False
    has_depth = (
        re.search(r"foreground\s*=", text, flags=re.IGNORECASE)
        and re.search(r"background\s*=", text, flags=re.IGNORECASE)
    )
    has_cn_depth = "前景" in text and "后景" in text
    return bool(has_depth or has_cn_depth)


def relation_camera(camera_tag: str) -> bool:
    lower = camera_tag.lower()
    return any(marker.lower() in lower for marker in RELATION_CAMERA_MARKERS)


def prompt_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_generation_manifest(
    issues: list[dict[str, str]],
    panel_plan: dict[str, Any],
    pages: dict[str, str],
    manifest: dict[str, Any] | None,
) -> None:
    if not manifest:
        return
    mode = str(manifest.get("generation_mode", "")).lower()
    formal_reference = bool(manifest.get("formal_reference_generation")) or mode in {
        "formal_reference_image",
        "formal_reference_generation",
    }
    binding = str(manifest.get("reference_binding_status") or panel_plan.get("reference_binding_status") or "")
    if formal_reference and binding != "bound":
        add_issue(
            issues,
            "formal_reference_generation_without_bound_refs",
            "generation_manifest.json",
            f"Formal reference-image generation requires bound references; current status is {binding!r}.",
        )
    for item in manifest.get("images", []):
        page_id = str(item.get("page", "unknown"))
        if item.get("prompt_used_verbatim") is not True:
            add_issue(
                issues,
                "prompt_not_used_verbatim",
                f"generation_manifest.json/{page_id}",
                "Image generation must use the exact final_image_prompts.md page text without manual compression.",
            )
        expected_hash = prompt_hash(pages.get(page_id, ""))
        supplied_hash = str(item.get("prompt_sha256", ""))
        if supplied_hash and supplied_hash != expected_hash:
            add_issue(
                issues,
                "prompt_hash_mismatch",
                f"generation_manifest.json/{page_id}",
                "prompt_sha256 does not match the final prompt page text.",
            )
        if "style_consistency_passed" not in item:
            add_issue(
                issues,
                "missing_style_consistency_gate",
                f"generation_manifest.json/{page_id}",
                "Generated images must record style_consistency_passed.",
            )
        elif item.get("style_consistency_passed") is not True:
            add_issue(
                issues,
                "style_consistency_failed",
                f"generation_manifest.json/{page_id}",
                "Style consistency gate did not pass.",
            )


def validate(
    shot_data: dict[str, Any],
    panel_plan: dict[str, Any],
    final_prompts: str,
    generation_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    pages = split_pages(final_prompts)

    for field in ROOT_PLAN_REQUIRED_FIELDS:
        if panel_plan.get(field) in (None, "", []):
            add_issue(issues, "missing_panel_plan_root_field", "panel_plan.json", f"Missing {field}.")

    for token in OLD_16_LAYER_TOKENS:
        if token in final_prompts:
            add_issue(
                issues,
                "old_1_6_layer_in_final_prompt",
                "final_image_prompts.md",
                f"Old 1.6.0 layer is not allowed in v1.6.1 final prompt: {token}",
            )

    for token in PLACEHOLDER_TOKENS:
        if token.lower() in final_prompts.lower():
            add_issue(
                issues,
                "placeholder_prompt_text",
                "final_image_prompts.md",
                f"Placeholder text is forbidden in final prompt: {token}",
            )

    pattern = text_has_pattern(final_prompts, COUNTDOWN_OR_UI_PATTERNS)
    if pattern:
        add_issue(
            issues,
            "countdown_or_ui_token_in_final_prompt",
            "final_image_prompts.md",
            f"Countdown/UI/readable digit token is forbidden: {pattern}",
        )

    pattern = text_has_pattern(final_prompts, COLOR_LEAK_PATTERNS)
    if pattern:
        add_issue(
            issues,
            "color_function_word_leak",
            "final_image_prompts.md",
            f"Color term must be converted to black-and-white sketch function: {pattern}",
        )

    pattern = text_has_pattern(final_prompts, DETAIL_PRESSURE_PATTERNS)
    if pattern:
        add_issue(
            issues,
            "reference_detail_pressure",
            "final_image_prompts.md",
            f"Reference/detail pressure is forbidden: {pattern}",
        )

    for token in panel_plan.get("forbidden_prompt_tokens") or []:
        token_text = str(token)
        if token_text and token_text.lower() in final_prompts.lower():
            add_issue(
                issues,
                "panel_plan_forbidden_token_present",
                "final_image_prompts.md",
                f"panel_plan forbidden_prompt_tokens contains a token present in final prompt: {token_text}",
            )

    style_locks = {block_content(page, "STYLE_LOCK:") for page in pages.values()}
    negative_locks = {block_content(page, "NEGATIVE_LOCK:") for page in pages.values()}
    if len(style_locks) > 1:
        add_issue(issues, "style_lock_not_identical", "final_image_prompts.md", "STYLE_LOCK differs across pages.")
    if len(negative_locks) > 1:
        add_issue(issues, "negative_lock_not_identical", "final_image_prompts.md", "NEGATIVE_LOCK differs across pages.")

    shot_by_no = {int(shot.get("shot_no")): shot for shot in shot_data.get("shots", []) if shot.get("shot_no") is not None}
    plan_pages = {str(page.get("page")): page for page in panel_plan.get("pages", [])}

    for page_id, page_text in pages.items():
        if len(page_text) < 2500:
            add_issue(issues, "page_length_below_target", page_id, f"Page is {len(page_text)} chars; target is 2,500-4,500.")
        if len(page_text) > 4500:
            add_issue(issues, "page_length_above_target", page_id, f"Page is {len(page_text)} chars; target is 2,500-4,500.")
        if len(page_text) > 5000:
            add_issue(issues, "page_length_hard_stop", page_id, f"Page is {len(page_text)} chars; over 5,000 hard stop.")
        for block in REQUIRED_PAGE_BLOCKS:
            if not block_content(page_text, block):
                add_issue(issues, "missing_required_block", page_id, f"Missing or empty {block}")

        plan_page = plan_pages.get(page_id)
        if not plan_page:
            add_issue(issues, "page_missing_from_panel_plan", page_id, "Page is absent from panel_plan.json.")
            continue

        prompt_panels = parse_prompt_panels(page_text)
        if len(prompt_panels) != 9:
            add_issue(issues, "wrong_panel_count", page_id, f"Found {len(prompt_panels)} panels; expected 9.")

        plan_panels = {str(panel.get("panel")): panel for panel in plan_page.get("panels", [])}
        for panel_id in [f"P{i:02d}" for i in range(1, 10)]:
            where = f"{page_id}/{panel_id}"
            prompt_panel = prompt_panels.get(panel_id)
            plan_panel = plan_panels.get(panel_id)
            if not prompt_panel:
                add_issue(issues, "missing_prompt_panel", where, "Panel is missing from final prompt.")
                continue
            if not plan_panel:
                add_issue(issues, "missing_panel_plan_panel", where, "Panel is missing from panel_plan.json.")
                continue

            for field in PANEL_PLAN_REQUIRED_FIELDS:
                value = plan_panel.get(field)
                empty_list_allowed = field in {"visible_characters", "visible_props"}
                if field not in plan_panel or value in (None, "") or (value == [] and not empty_list_allowed):
                    add_issue(issues, "missing_panel_plan_panel_field", where, f"Missing {field}.")

            for field in PANEL_FIELDS:
                if not prompt_panel.get(field):
                    add_issue(issues, "missing_prompt_panel_field", where, f"Missing or empty {field}")

            prompt_source = parse_int(prompt_panel.get("SOURCE SHOT:", ""))
            plan_source = int(plan_panel.get("source_shot", -1))
            if prompt_source != plan_source:
                add_issue(issues, "source_shot_mismatch", where, f"Prompt source {prompt_source} != panel_plan source {plan_source}.")

            shot = shot_by_no.get(plan_source)
            source_camera = str(plan_panel.get("source_camera_tag") or "").strip()
            if shot:
                shot_camera = camera_tag_from_shot(shot)
                if source_camera != shot_camera:
                    add_issue(
                        issues,
                        "panel_plan_camera_tag_mismatch_shot_data",
                        where,
                        f"panel_plan source_camera_tag {source_camera!r} != shot_data {shot_camera!r}.",
                    )
                shot_chars = normalize_set(shot.get("visible_characters"), CHARACTER_CODES)
                plan_chars = normalize_set(plan_panel.get("visible_characters"), CHARACTER_CODES)
                if not bool(plan_panel.get("p01_anchor_override")) and plan_chars != shot_chars:
                    add_issue(
                        issues,
                        "panel_plan_visible_characters_mismatch_shot_data",
                        where,
                        f"panel_plan chars {sorted(plan_chars)} != shot_data chars {sorted(shot_chars)}.",
                    )
                shot_props = normalize_set(shot.get("visible_props"), PROP_CODES)
                plan_props = normalize_set(plan_panel.get("visible_props"), PROP_CODES)
                if not bool(plan_panel.get("p01_anchor_override")) and plan_props != shot_props:
                    add_issue(
                        issues,
                        "panel_plan_visible_props_mismatch_shot_data",
                        where,
                        f"panel_plan props {sorted(plan_props)} != shot_data props {sorted(shot_props)}.",
                    )

            prompt_camera = str(prompt_panel.get("MUST MATCH SHOT_DATA CAMERA TAG:", "")).strip()
            if prompt_camera != source_camera:
                add_issue(
                    issues,
                    "prompt_camera_tag_mismatch_panel_plan",
                    where,
                    f"Prompt camera tag {prompt_camera!r} != panel_plan source_camera_tag {source_camera!r}.",
                )

            is_anchor = bool(plan_panel.get("p01_anchor_override"))
            drawn_camera_prompt = str(prompt_panel.get("DRAWN CAMERA TAG:", "")).strip()
            drawn_camera_plan = str(plan_panel.get("drawn_camera_tag") or "").strip()
            if is_anchor:
                if panel_id != "P01":
                    add_issue(issues, "anchor_override_not_p01", where, "Only P01 may use anchor override.")
                if not drawn_camera_prompt:
                    add_issue(issues, "p01_anchor_missing_drawn_camera_tag", where, "Anchor override requires DRAWN CAMERA TAG.")
                elif drawn_camera_prompt != drawn_camera_plan:
                    add_issue(
                        issues,
                        "drawn_camera_tag_mismatch",
                        where,
                        f"Prompt drawn tag {drawn_camera_prompt!r} != panel_plan {drawn_camera_plan!r}.",
                    )
            elif drawn_camera_prompt and drawn_camera_prompt != source_camera:
                add_issue(issues, "unexpected_drawn_camera_tag", where, "Non-anchor panels must not invent a different DRAWN CAMERA TAG.")

            prompt_chars = extract_visible(prompt_panel.get("VISIBLE ONLY:", ""), "chars", CHARACTER_CODES)
            prompt_props = extract_visible(prompt_panel.get("VISIBLE ONLY:", ""), "props", PROP_CODES)
            if is_anchor:
                allowed = plan_panel.get("anchor_visible_allowed")
                expected_chars = anchor_allowed_set(allowed, "characters", CHARACTER_CODES)
                expected_props = anchor_allowed_set(allowed, "props", PROP_CODES)
                if not expected_chars and not expected_props:
                    add_issue(issues, "p01_anchor_missing_anchor_visible_allowed", where, "Anchor override requires anchor_visible_allowed.")
                if expected_chars and prompt_chars != expected_chars:
                    add_issue(
                        issues,
                        "p01_anchor_visible_only_not_anchor_allowed",
                        where,
                        f"P01 anchor VISIBLE ONLY chars {sorted(prompt_chars)} != anchor_visible_allowed {sorted(expected_chars)}.",
                    )
                if expected_props and prompt_props != expected_props:
                    add_issue(
                        issues,
                        "p01_anchor_props_not_anchor_allowed",
                        where,
                        f"P01 anchor VISIBLE ONLY props {sorted(prompt_props)} != anchor_visible_allowed {sorted(expected_props)}.",
                    )
            else:
                expected_chars = normalize_set(plan_panel.get("visible_characters"), CHARACTER_CODES)
                expected_props = normalize_set(plan_panel.get("visible_props"), PROP_CODES)
                if prompt_chars != expected_chars:
                    add_issue(
                        issues,
                        "prompt_visible_characters_mismatch_panel_plan",
                        where,
                        f"Prompt chars {sorted(prompt_chars)} != panel_plan chars {sorted(expected_chars)}.",
                    )
                if prompt_props != expected_props:
                    add_issue(
                        issues,
                        "prompt_visible_props_mismatch_panel_plan",
                        where,
                        f"Prompt props {sorted(prompt_props)} != panel_plan props {sorted(expected_props)}.",
                    )

            action = prompt_panel.get("ACTION / COMPOSITION:", "")
            floor_axis = prompt_panel.get("FLOOR / AXIS DELTA:", "")
            prop_state = prompt_panel.get("PROP STATE:", "")
            if is_anchor:
                anchor_terms = ("floor", "surface", "forbidden", "start", "initial", "empty position", "可站立", "禁站", "起点", "空位")
                if not any(term.lower() in action.lower() for term in anchor_terms):
                    add_issue(
                        issues,
                        "p01_anchor_action_not_spatial",
                        where,
                        "Anchor ACTION / COMPOSITION must describe floor/surface/forbidden zones/start positions.",
                    )

            if not has_concrete_axis(floor_axis):
                add_issue(
                    issues,
                    "axis_lock_not_concrete",
                    where,
                    "FLOOR / AXIS DELTA must contain A=, B=, camera side=, screen left=, screen right=, foreground=, and background=.",
                )

            if relation_camera(source_camera) and not re.search(r"shoulder\s*=", floor_axis, flags=re.IGNORECASE) and "肩" not in floor_axis:
                add_issue(
                    issues,
                    "relation_shot_missing_shoulder_lock",
                    where,
                    "Relationship/OTS/two-shot panel requires shoulder= or a concrete shoulder-side note.",
                )

            state_phases = bracelet_phases(prop_state + "\n" + action)
            if len(state_phases) > 1:
                add_issue(
                    issues,
                    "bracelet_temporal_phase_conflict",
                    where,
                    "Bracelet has multiple physical phases in one panel: " + ", ".join(sorted(state_phases)),
                )

            for prop in prompt_props:
                if prop not in prop_state and prop_state.lower() != "none":
                    add_issue(
                        issues,
                        "visible_prop_missing_from_prop_state",
                        where,
                        f"Visible prop/effect {prop} is absent from PROP STATE.",
                    )

            if "STAFF" in prompt_props and prompt_chars and "GC" not in prompt_chars:
                add_issue(issues, "staff_without_owner", where, "STAFF can only appear with GC or as an explicit prop-only insert.")
            if "BRACELET" in prompt_props and prompt_chars and "LX" not in prompt_chars:
                add_issue(issues, "bracelet_without_owner", where, "BRACELET can only appear with LX or as an explicit prop-only insert.")

    validate_generation_manifest(issues, panel_plan, pages, generation_manifest)

    return {
        "ok": not issues,
        "issue_count": len(issues),
        "issues": issues,
        "page_count": len(pages),
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Validate su-image9 1.6.1 final prompts before image generation.")
    parser.add_argument("--shot-data", required=True, type=Path)
    parser.add_argument("--panel-plan", required=True, type=Path)
    parser.add_argument("--final-prompts", required=True, type=Path)
    parser.add_argument("--generation-manifest", type=Path)
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args(argv)

    shot_data = load_json(args.shot_data)
    panel_plan = load_json(args.panel_plan)
    final_prompts = args.final_prompts.read_text(encoding="utf-8")
    generation_manifest = load_json(args.generation_manifest) if args.generation_manifest else None

    result = validate(shot_data, panel_plan, final_prompts, generation_manifest)
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.json_output:
        args.json_output.write_text(output + "\n", encoding="utf-8")
    print(output)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
