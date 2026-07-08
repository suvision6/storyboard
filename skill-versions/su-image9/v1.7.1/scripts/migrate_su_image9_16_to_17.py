#!/usr/bin/env python3
"""Migrate su-image9 1.6.x prompt artifacts toward the 1.7.1 contract."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

CANON_MARKERS = {
    "STYLE_LOCK": "@CANON(STYLE_LOCK)",
    "CANVAS_LOCK": "@CANON(CANVAS_LOCK)",
    "REFERENCE_LOCK": "@CANON(REFERENCE_LOCK)",
    "NEGATIVE_LOCK": "@CANON(NEGATIVE_LOCK)",
}
CANON_BUILTIN_TOKENS = {
    "red", "reddish", "crimson", "scarlet", "ruby", "blood-red", "gold", "golden",
    "gilded", "blue", "azure", "cyan", "navy", "green", "emerald", "yellow",
    "amber", "purple", "violet", "pink", "magenta", "orange", "brown", "colorful",
    "multicolored", "vivid colors", "saturated colors", "portrait likeness", "exact face",
    "photoreal", "photorealistic", "hyperrealistic", "ultra detailed", "highly detailed",
    "intricate", "8k", "4k", "masterpiece", "cinematic", "studio lighting", "skin texture",
    "film grain",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def migrate_page_name(value: str) -> tuple[str, bool]:
    match = re.fullmatch(r"P(\d{2})", value.strip())
    if match:
        return f"PAGE-{match.group(1)}", True
    return value, False


def migrate_panel_name(value: str) -> tuple[str, bool]:
    text = value.strip()
    match = re.fullmatch(r"P0?(\d+)", text)
    if match:
        return f"PANEL-{int(match.group(1))}", True
    return text, False


def migrate_plan(plan: dict[str, Any]) -> tuple[dict[str, Any], list[str], list[str]]:
    changed: list[str] = []
    ambiguous: list[str] = []
    plan = json.loads(json.dumps(plan, ensure_ascii=False))
    plan["version"] = "1.7.1"
    if "forbidden_prompt_tokens" in plan:
        raw = plan.pop("forbidden_prompt_tokens") or []
        if not isinstance(raw, list):
            raw = [raw]
        extra = [str(item) for item in raw if str(item).lower() not in CANON_BUILTIN_TOKENS]
        plan["forbidden_prompt_tokens_extra"] = extra
        changed.append("forbidden_prompt_tokens -> forbidden_prompt_tokens_extra")
    for page_index, page in enumerate(plan.get("pages", []) or [], start=1):
        if isinstance(page, dict):
            if page.get("page"):
                new_name, did = migrate_page_name(str(page["page"]))
                if did:
                    changed.append(f"page {page['page']} -> {new_name}")
                    page["page"] = new_name
            for panel_index, panel in enumerate(page.get("panels", []) or [], start=1):
                if not isinstance(panel, dict):
                    continue
                raw_panel = panel.get("panel") or panel.get("panel_id")
                if raw_panel:
                    new_panel, did = migrate_panel_name(str(raw_panel))
                    if did:
                        changed.append(f"panel {raw_panel} -> {new_panel}")
                    panel["panel"] = new_panel
                    panel.pop("panel_id", None)
                else:
                    panel["panel"] = f"PANEL-{panel_index}"
                    ambiguous.append(f"page {page_index} panel {panel_index}: missing panel id, inferred PANEL-{panel_index}")
                if not panel.get("drawn_camera_tag"):
                    panel["drawn_camera_tag"] = panel.get("source_camera_tag", "")
                    changed.append(f"{page.get('page', page_index)} {panel['panel']}: added drawn_camera_tag from source_camera_tag")
    return plan, changed, ambiguous


def replace_lock_blocks(text: str, changed: list[str]) -> str:
    for block, marker in CANON_MARKERS.items():
        pattern = re.compile(rf"(?ms)^({block}:)\s*\n(.*?)(?=^\n?(?:STYLE_LOCK|CANVAS_LOCK|REFERENCE_LOCK|CONTINUITY_LOCK|PANEL_TASKS|NEGATIVE_LOCK):|\Z)")
        def repl(match: re.Match[str]) -> str:
            changed.append(f"{block} replaced with {marker}")
            return f"{block}:\n{marker}\n\n"
        text = pattern.sub(repl, text)
    text = re.sub(r"(?m)^#\s+P(\d{2})\b", r"# PAGE-\1", text)
    text = re.sub(r"(?m)^P0?(\d+):\s*$", lambda m: f"PANEL-{int(m.group(1))}:", text)
    text = text.replace("PANEL_TASKS P01-P09:", "PANEL_TASKS P01-P09:")
    return text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Migrate su-image9 1.6.x panel plan and final prompts to 1.7.1 naming/canon markers.")
    parser.add_argument("--panel-plan", required=True)
    parser.add_argument("--final-prompts", required=True)
    parser.add_argument("--out-dir", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    changed: list[str] = []
    prompt_text = Path(args.final_prompts).read_text(encoding="utf-8")
    plan, plan_changed, ambiguous = migrate_plan(load_json(Path(args.panel_plan)))
    changed.extend(plan_changed)
    migrated_prompt = replace_lock_blocks(prompt_text, changed)
    dump_json(out_dir / "panel_plan.json", plan)
    (out_dir / "final_image_prompts.md").write_text(migrated_prompt, encoding="utf-8")
    report = {
        "version": "1.7.1",
        "changed": changed,
        "manual_review": ambiguous,
        "note": "Migration does not grant validation exemptions; rerun validate_su_image9_prompt.py before use.",
    }
    dump_json(out_dir / "migration_report.json", report)
    return 1 if ambiguous else 0


if __name__ == "__main__":
    raise SystemExit(main())
