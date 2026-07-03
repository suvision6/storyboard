#!/usr/bin/env python3
"""Static preflight validator for su-image9 final_image_prompts.md.

This validator checks structural prompt failures that are easy to miss when a
page is within the target character range but semantically unsafe for image
generation.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


REQUIRED_PAGE_LAYERS = [
    "DELIVERABLE:",
    "SYSTEM_STYLE_LAYER:",
    "PROFILE_SOURCE_AND_PRECEDENCE:",
    "PROJECT_VISUAL_PROFILE:",
    "SCENE_LAYER:",
    "CAMERA_RULE_LAYER:",
    "CONTINUITY_LAYER:",
    "PANEL_1_MASTER_SPATIAL_LAYOUT_ANCHOR:",
    "FIXED_OBJECT_SCREEN_PROJECTION:",
    "PANEL_INHERITANCE_MAP:",
    "AXIS_AND_SHOULDER_LOCKS:",
    "OBJECT_VISIBILITY_AND_BOUNDARIES:",
    "PANEL_DIFFERENCE_TASKS:",
    "PANEL_LAYER P01-P09:",
    "NEGATIVE_CONSTRAINTS:",
]

PANEL_FIELDS = [
    "SOURCE SHOT:",
    "MUST MATCH SHOT_DATA CAMERA TAG:",
    "VISIBLE ONLY:",
    "MUST NOT SHOW:",
    "CHARACTER ANCHORS:",
    "SCREEN POSITION / AXIS LOCK:",
    "CONTENT:",
]

CHARACTER_ALIASES = {
    "林晓彤": "LX",
    "沈夜": "SY",
    "顾成": "GC",
    "顾城": "GC",
    "林晓杰": "LXJ",
    "金黑雾体": "GOLD_BLACK_MIST",
}

RELATION_TAG_MARKERS = ("过肩", "双人", "reverse", "ots", "over-shoulder")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def split_pages(prompt_text: str) -> dict[str, str]:
    pages: dict[str, str] = {}
    for block in re.split(r"\n---\n\n", prompt_text.strip()):
        first = block.splitlines()[0] if block.splitlines() else ""
        match = re.match(r"#\s*(P\d+)", first)
        if match:
            pages[match.group(1)] = block
    return pages


def parse_prompt_panels(page_text: str) -> dict[str, dict[str, str]]:
    if "PANEL_LAYER P01-P09:" not in page_text:
        return {}
    panel_text = page_text.split("PANEL_LAYER P01-P09:", 1)[1]
    panel_text = panel_text.split("NEGATIVE_CONSTRAINTS:", 1)[0]
    panels: dict[str, dict[str, str]] = {}
    pattern = re.compile(r"\n?(P\d\d):\n([\s\S]*?)(?=\nP\d\d:\n|\Z)")
    for match in pattern.finditer(panel_text.strip() + "\n"):
        panel_id = match.group(1)
        body = match.group(2)
        fields: dict[str, str] = {}
        for field in PANEL_FIELDS:
            field_pattern = re.compile(
                re.escape(field) + r"\s*([\s\S]*?)(?=\n(?:"
                + "|".join(re.escape(f) for f in PANEL_FIELDS)
                + r")|\Z)"
            )
            field_match = field_pattern.search(body)
            fields[field] = field_match.group(1).strip() if field_match else ""
        anchor_match = re.search(r"ANCHOR_VISIBLE_ALLOWED:\s*([^\n]+)", body)
        if anchor_match:
            fields["ANCHOR_VISIBLE_ALLOWED:"] = anchor_match.group(1).strip()
        panels[panel_id] = fields
    return panels


def extract_chars(visible_text: str) -> set[str]:
    text = visible_text.replace("Characters:", "chars=")
    if "chars=" not in text:
        return set()
    part = text.split("chars=", 1)[1].split(";", 1)[0].split(".", 1)[0]
    return {token.strip() for token in re.split(r"[,/]", part) if token.strip() and token.strip() != "none"}


def extract_props(visible_text: str) -> set[str]:
    text = visible_text.replace("Props/effects:", "props=")
    if "props=" not in text:
        return set()
    part = text.split("props=", 1)[1].split(";", 1)[0].split(".", 1)[0]
    return {token.strip() for token in re.split(r"[,/]", part) if token.strip() and token.strip() != "none"}


def mentioned_character_codes(content: str) -> set[str]:
    return {code for name, code in CHARACTER_ALIASES.items() if name in content}


def add_issue(issues: list[dict[str, str]], code: str, where: str, detail: str) -> None:
    issues.append({"code": code, "where": where, "detail": detail})


def validate(
    shot_data: dict[str, Any],
    panel_plan: dict[str, Any],
    final_prompts: str,
) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    pages = split_pages(final_prompts)

    continuity_logs = shot_data.get("continuity_logs") or []
    if continuity_logs and "CONTINUITY_LAYER:" not in final_prompts:
        add_issue(
            issues,
            "missing_continuity_layer",
            "final_image_prompts.md",
            "shot_data has continuity_logs but final prompt has no CONTINUITY_LAYER.",
        )

    for log in continuity_logs:
        fixed_objects = [str(x) for x in log.get("fixed_objects", [])]
        if fixed_objects and not any(obj in final_prompts for obj in fixed_objects):
            add_issue(
                issues,
                "continuity_fixed_objects_absent",
                str(log.get("scene", "unknown scene")),
                "None of the fixed_objects appear in final prompt: " + ", ".join(fixed_objects),
            )

    for page_id, page_text in pages.items():
        length = len(page_text)
        if length < 7000 or length > 11000:
            add_issue(
                issues,
                "page_length_outside_target",
                page_id,
                f"Page is {length} characters; target is 7,000-11,000.",
            )
        if length > 12000:
            add_issue(
                issues,
                "page_length_hard_stop",
                page_id,
                f"Page is {length} characters; over 12,000 hard stop.",
            )
        for layer in REQUIRED_PAGE_LAYERS:
            if layer not in page_text:
                add_issue(issues, "missing_required_layer", page_id, f"Missing {layer}")

        prompt_panels = parse_prompt_panels(page_text)
        if len(prompt_panels) != 9:
            add_issue(issues, "wrong_panel_count", page_id, f"Found {len(prompt_panels)} panels.")

        for panel_id, fields in prompt_panels.items():
            where = f"{page_id}/{panel_id}"
            for field in PANEL_FIELDS:
                if not fields.get(field):
                    add_issue(issues, "missing_panel_field", where, f"Missing or empty {field}")

            visible = fields.get("VISIBLE ONLY:", "")
            must_not = fields.get("MUST NOT SHOW:", "")
            anchors = fields.get("CHARACTER ANCHORS:", "")
            content = fields.get("CONTENT:", "")
            axis = fields.get("SCREEN POSITION / AXIS LOCK:", "")
            anchor_visible = fields.get("ANCHOR_VISIBLE_ALLOWED:", "")

            allowed_chars = extract_chars(visible)
            anchor_allowed_chars = extract_chars("chars=" + anchor_visible)
            mentioned = mentioned_character_codes(content)
            missing_mentions = mentioned - allowed_chars - anchor_allowed_chars
            if missing_mentions:
                add_issue(
                    issues,
                    "content_visible_conflict",
                    where,
                    "CONTENT mentions characters not allowed by VISIBLE ONLY/ANCHOR_VISIBLE_ALLOWED: "
                    + ", ".join(sorted(missing_mentions)),
                )

            props = extract_props(visible)
            if "MIST/VFX" in props or "MIST/VFX" in content or "MIST/VFX" in anchors:
                add_issue(
                    issues,
                    "ambiguous_mist_token",
                    where,
                    "Use precise GREY_LXJ_MIST / GOLD_BLACK_MIST / LIGHT_DUST / BRACELET_PULSE tokens, not MIST/VFX.",
                )

            if "MIST/VFX" in props and "no MIST" in must_not:
                add_issue(
                    issues,
                    "visible_must_not_conflict",
                    where,
                    "VISIBLE ONLY allows MIST/VFX but MUST NOT SHOW forbids MIST.",
                )

            gc_visible = "GC" in allowed_chars or "GC" in anchors
            staff_visible = "STAFF" in props or "STAFF" in visible
            staff_invited = "sole staff owner" in anchors or "staff owner" in anchors
            staff_forbidden = "no STAFF" in must_not or "no staff" in must_not.lower()
            if gc_visible and staff_invited and not staff_visible and not staff_forbidden:
                add_issue(
                    issues,
                    "prop_anchor_invites_absent_staff",
                    where,
                    "GC is visible without STAFF, but CHARACTER ANCHORS invite staff ownership and MUST NOT SHOW does not forbid staff visibility.",
                )

            relation_like = any(marker in fields.get("MUST MATCH SHOT_DATA CAMERA TAG:", "").lower() for marker in RELATION_TAG_MARKERS)
            relation_like = relation_like or any(marker in fields.get("MUST MATCH SHOT_DATA CAMERA TAG:", "") for marker in ("过肩", "双人"))
            has_shoulder_lock = any(token in axis.lower() for token in ("shoulder", "foreground", "background"))
            has_shoulder_lock = has_shoulder_lock or any(token in axis for token in ("肩", "前景", "后景"))
            if relation_like and not has_shoulder_lock:
                add_issue(
                    issues,
                    "relation_shot_missing_shoulder_lock",
                    where,
                    "Relationship/OTS/two-shot panel lacks shoulder or foreground/background lock.",
                )

    for page in panel_plan.get("pages", []):
        page_id = str(page.get("page", "unknown"))
        by_source: dict[str, list[dict[str, Any]]] = {}
        for panel in page.get("panels", []):
            by_source.setdefault(str(panel.get("source_shot")), []).append(panel)
        for source, panels in by_source.items():
            if len(panels) <= 1:
                continue
            content_values = {
                str(panel.get("content_source_sanitized", "")).strip()
                for panel in panels
            }
            task_values = {
                str(panel.get("difference_task") or panel.get("phase") or "").strip()
                for panel in panels
            }
            has_split_or_anchor = any(
                str(panel.get("role")) in {"split", "anchor_override"} for panel in panels
            )
            if has_split_or_anchor and len(content_values) <= 1 and len(task_values) <= 1:
                add_issue(
                    issues,
                    "duplicate_split_without_distinct_task",
                    f"{page_id}/source {source}",
                    "Repeated source shot has no distinct content or difference task.",
                )

    return {
        "ok": not issues,
        "issue_count": len(issues),
        "issues": issues,
        "page_count": len(pages),
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Validate su-image9 final prompts before image generation.")
    parser.add_argument("--shot-data", required=True, type=Path)
    parser.add_argument("--panel-plan", required=True, type=Path)
    parser.add_argument("--final-prompts", required=True, type=Path)
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args(argv)

    shot_data = load_json(args.shot_data)
    panel_plan = load_json(args.panel_plan)
    final_prompts = args.final_prompts.read_text(encoding="utf-8")

    result = validate(shot_data, panel_plan, final_prompts)
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.json_output:
        args.json_output.write_text(output + "\n", encoding="utf-8")
    print(output)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
