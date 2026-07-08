#!/usr/bin/env python3
"""Derive a su-image9 v2.0.2 prompt package from locked shot_data.json."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

VERSION = "2.0.2"
CANON_VERSION = "2.0.2"
MIN_SEMANTIC_PAGE_SIZE = 5

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

POSITIVE_ANCHOR = {"master", "establishing", "wide", "full", "全景", "大全景", "大远景"}
NEGATIVE_ANCHOR = {"close", "close-up", "medium", "over-shoulder", "ots", "insert", "pov", "reaction", "black", "特写", "近景", "中景", "过肩", "反应", "黑场"}
BAD_PAGE_START_LAYERS = {"memory", "surgery", "black"}
LAYER_BRIDGE_TERMS = {
    "记忆层": "memory",
    "年幼": "memory",
    "回忆": "memory",
    "手术": "surgery",
    "无影灯": "surgery",
    "心电": "surgery",
    "除颤": "surgery",
    "黑屏": "black",
    "切黑": "black",
    "平线长鸣": "black",
    "动作全部变慢": "final_slow",
    "沈夜消失": "final_slow",
    "独自站": "final_slow",
    "倒计时": "final_slow",
}


def camera_tag(shot: dict[str, Any]) -> str:
    match = re.match(r"\[([^\]]+)\]", str(shot.get("camera_main_image", "")))
    return match.group(1).strip() if match else ""


def normalize_tag_tokens(tag: str) -> set[str]:
    lower = tag.lower()
    tokens = set(re.findall(r"[a-z]+(?:-[a-z]+)?|[\u4e00-\u9fff]+", lower))
    if "close" in tokens and "up" in tokens:
        tokens.add("close-up")
    if "over" in tokens and "shoulder" in tokens:
        tokens.add("over-shoulder")
    return tokens


def prompt_field(prompt: str, label: str) -> str:
    match = re.search(rf"{label}：(.+?)(?:\n|$)", prompt)
    return match.group(1).strip() if match else ""


def clean_text(text: str) -> str:
    text = re.sub(r"△", "", text)
    text = re.sub(r"【[^】]*】", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def visible_names(items: list[str]) -> str:
    return "、".join(items) if items else "无"


def prop_names(items: list[str]) -> str:
    return "、".join(items) if items else "none"


def scene_logs(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["scene_id"]: item for item in data.get("continuity_logs", []) if isinstance(item, dict) and item.get("scene_id")}


def page_chunks(shots: list[dict[str, Any]], page_size: int) -> list[list[dict[str, Any]]]:
    pages: list[list[dict[str, Any]]] = []
    start = 0
    while start < len(shots):
        max_end = min(start + page_size, len(shots))
        cut = None
        for index in range(start + 1, max_end):
            if index - start < MIN_SEMANTIC_PAGE_SIZE:
                continue
            if len(shots) - index < MIN_SEMANTIC_PAGE_SIZE:
                continue
            if should_split_before(shots[index - 1], shots[index]):
                cut = index
                break
        if cut is None:
            cut = max_end
            if (
                max_end < len(shots)
                and max_end - start > MIN_SEMANTIC_PAGE_SIZE
                and is_bad_page_start(shots[max_end])
                and not is_bad_page_start(shots[max_end - 1])
            ):
                cut = max_end - 1
        if cut <= start:
            cut = max_end
        pages.append(shots[start:cut])
        start = cut
    return pages


def layer_key(shot: dict[str, Any]) -> str:
    text = " ".join(
        [
            str(shot.get("scene", "")),
            str(shot.get("shot_type", "")),
            str(shot.get("camera_main_image", "")),
            str(shot.get("source_paragraph", "")),
            str(shot.get("prompt", "")),
        ]
    )
    for term, key in LAYER_BRIDGE_TERMS.items():
        if term in text:
            return key
    return "current"


def is_bad_page_start(shot: dict[str, Any]) -> bool:
    return layer_key(shot) in BAD_PAGE_START_LAYERS


def scene_location_key(shot: dict[str, Any]) -> str:
    scene = str(shot.get("scene", ""))
    scene = re.sub(r"^\s*\d+\s*-\s*\d+\s*", "", scene)
    scene = scene.replace("同", "")
    scene = scene.replace("日", "").replace("夜", "").replace("内", "").replace("外", "")
    scene = re.sub(r"\s+", "", scene)
    return scene


def is_allowed_cross_scene_bridge(previous: dict[str, Any], current: dict[str, Any]) -> bool:
    if layer_key(previous) != "current" or layer_key(current) != "current":
        return False
    if scene_location_key(previous) != scene_location_key(current):
        return False
    return str(current.get("shot_type", "")).strip() == "master"


def should_split_before(previous: dict[str, Any], current: dict[str, Any]) -> bool:
    if layer_key(previous) != layer_key(current) and layer_key(current) in BAD_PAGE_START_LAYERS:
        return True
    if str(previous.get("scene_id", "")) != str(current.get("scene_id", "")):
        return not is_allowed_cross_scene_bridge(previous, current)
    return False


def shot_text(shot: dict[str, Any]) -> str:
    return " ".join(
        [
            str(shot.get("camera_main_image", "")),
            str(shot.get("source_paragraph", "")),
            str(shot.get("prompt", "")),
        ]
    ).lower()


def has_distance_endpoint(shot: dict[str, Any]) -> bool:
    text = shot_text(shot)
    return any(term.lower() in text for term in DISTANCE_ENDPOINT_TERMS)


def distance_locks(chunk: list[dict[str, Any]]) -> list[str]:
    locks = ["none" for _ in chunk]
    for index in range(1, len(chunk)):
        if not has_distance_endpoint(chunk[index]):
            continue
        current_panel = index + 1
        current_shot = chunk[index]["shot_no"]
        locks[index - 1] = (
            f"pre-approach: 后续 PANEL-{current_panel}/C{current_shot} 才到达靠近或停步终点；"
            "本格保持位移前距离，人物之间保留可见空地和空间纵深，不得提前画成终点状态。"
        )
        locks[index] = (
            f"endpoint-arrival: 本格按 C{current_shot} 执行靠近或停步终点；"
            "该距离终点不得提前出现在前序 Panel。"
        )
    return locks


def shot_summary(shot: dict[str, Any]) -> str:
    prompt = str(shot.get("prompt", ""))
    content = prompt_field(prompt, "画面内容")
    composition = prompt_field(prompt, "构图")
    camera = prompt_field(prompt, "运镜手法")
    if not content:
        content = str(shot.get("source_paragraph", ""))
    parts = []
    if composition:
        parts.append(f"构图：{clean_text(composition)}")
    if camera:
        parts.append(f"运镜：{clean_text(camera)}")
    if content:
        parts.append(f"画面：{clean_text(content)}")
    return "；".join(parts) or f"镜头 C{shot.get('shot_no')} 的可见动作阶段"


def drawn_camera_tag(shot: dict[str, Any], panel_index: int, sparse: bool = False) -> str:
    tag = camera_tag(shot)
    if sparse:
        return f"sparse-page continuation derived from source camera tag: {tag}"
    if panel_index == 1:
        tokens = normalize_tag_tokens(tag)
        if tokens & NEGATIVE_ANCHOR:
            return f"master wide/full spatial anchor rewritten inside source shot {shot.get('shot_no')} from source camera tag: {tag}"
        return f"master wide/full spatial anchor derived from source camera tag: {tag}"
    return f"drawn camera follows source camera tag: {tag}"


def floor_axis(shot: dict[str, Any], log: dict[str, Any] | None, panel_index: int) -> str:
    axis = str(log.get("spatial_axis", "")) if log else ""
    if panel_index == 1:
        return f"Panel 1 anchors the page axis without changing source order: {axis or shot.get('scene', '')}"
    return f"Keep the same scene axis and screen-side relationships from Panel 1; source scene: {shot.get('scene', '')}"


def panel_plan_item(shot: dict[str, Any], panel_index: int, log: dict[str, Any] | None, distance_lock: str, sparse: bool = False) -> dict[str, Any]:
    return {
        "panel": f"PANEL-{panel_index}",
        "source_shot": int(shot["shot_no"]),
        "shot_data_camera_tag": camera_tag(shot),
        "drawn_camera_tag": drawn_camera_tag(shot, panel_index, sparse),
        "visible_only": f"visible characters: {visible_names(shot.get('visible_characters', []))}; visible props: {prop_names(shot.get('visible_props', []))}",
        "action_composition": shot_summary(shot)[:900],
        "floor_axis_delta": floor_axis(shot, log, panel_index),
        "prop_state": prop_names(shot.get("visible_props", [])),
        "distance_stage_lock": distance_lock,
    }


def page_title(page_no: int, chunk: list[dict[str, Any]]) -> str:
    scenes: list[str] = []
    for shot in chunk:
        scene = str(shot.get("scene", ""))
        if scene and scene not in scenes:
            scenes.append(scene)
    return f"PAGE-{page_no:02d} 镜头{chunk[0]['shot_no']}-{chunk[-1]['shot_no']}｜{' / '.join(scenes) or '未命名场景'}"


def page_scene_ids(chunk: list[dict[str, Any]]) -> list[str]:
    result: list[str] = []
    for shot in chunk:
        scene_id = str(shot.get("scene_id", ""))
        if scene_id and scene_id not in result:
            result.append(scene_id)
    return result


def page_layer_keys(chunk: list[dict[str, Any]]) -> list[str]:
    result: list[str] = []
    for shot in chunk:
        key = layer_key(shot)
        if key not in result:
            result.append(key)
    return result


def page_bridge_policy(chunk: list[dict[str, Any]]) -> str:
    scene_ids = page_scene_ids(chunk)
    layers = page_layer_keys(chunk)
    parts = ["scene_layer_aware_strict_source_order"]
    if len(scene_ids) > 1:
        parts.append("intentional_cross_scene_bridge")
    if len(layers) > 1:
        parts.append("intentional_layer_bridge")
    return "+".join(parts)


def page_split_reason(chunk: list[dict[str, Any]], page_size: int) -> str:
    if len(chunk) < page_size:
        return "semantic_split_to_protect_page_anchor_or_scene_layer_boundary"
    if len(page_scene_ids(chunk)) > 1 or len(page_layer_keys(chunk)) > 1:
        return "same_page_bridge_declared_by_page_split_policy"
    return "max_page_size_reached"


def page_scene_layer(chunk: list[dict[str, Any]], logs: dict[str, dict[str, Any]]) -> str:
    scene_ids: list[str] = []
    for shot in chunk:
        scene_id = str(shot.get("scene_id", ""))
        if scene_id and scene_id not in scene_ids:
            scene_ids.append(scene_id)
    lines = [
        "Build a single grayscale graphite storyboard sheet from the locked shot_data source.",
        "Translate all colored supernatural effects into distinct graphite tonal contrast only; do not add actual color.",
    ]
    for scene_id in scene_ids:
        log = logs.get(scene_id, {})
        fixed = "; ".join(
            f"{item.get('name')} at {item.get('position')} with state {item.get('state')}"
            for item in log.get("fixed_objects", [])
            if isinstance(item, dict)
        )
        chars = "; ".join(
            f"{item.get('name')} at {item.get('position')}, facing {item.get('facing')}, state {item.get('state', 'normal')}"
            for item in log.get("characters", [])
            if isinstance(item, dict)
        )
        lines.append(f"{scene_id} {log.get('scene', '')}: {log.get('spatial_axis', '')}")
        if fixed:
            lines.append(f"Fixed geometry: {fixed}.")
        if chars:
            lines.append(f"Character placement: {chars}.")
    if not scene_ids:
        lines.append("No continuity log is available; derive only from visible shot_data facts.")
    return "\n".join(lines)


def page_camera_layer(chunk: list[dict[str, Any]]) -> str:
    lines = [
        "Maintain one consistent screen geography inside this page. Panel 1 establishes the page layout while keeping the first source shot in the first panel.",
        "Do not reorder later source shots into Panel 1 for anchor convenience.",
        "Relationship shots must preserve eyeline direction, shoulder-side logic, and screen-left/screen-right placement from the source camera notes.",
    ]
    for shot in chunk:
        tag = camera_tag(shot)
        logic = clean_text(str(shot.get("camera_main_image", "")).replace(f"[{tag}]", "", 1))
        lines.append(f"Shot {shot['shot_no']} camera tag {tag}: {logic}")
    return "\n".join(lines)


def page_continuity_layer(chunk: list[dict[str, Any]], sparse: bool) -> str:
    lines = [
        "Use only the characters, props, locations, and action states present in the source shots for this page.",
        "Preserve source-shot order exactly; Panel 1 cannot borrow a later shot as the page anchor.",
        "If a later panel contains an approach or stopping-distance endpoint, earlier panels must keep the pre-approach spacing.",
        "No visible Chinese dialogue, countdown digits, monitor text, subtitles, shot numbers, labels, or arrows may appear inside any panel.",
    ]
    if sparse:
        lines.append("This is a sparse final page: continuation panels repeat only the final transition state without adding new story facts.")
    return "\n".join(lines)


def page_layout_layer(chunk: list[dict[str, Any]], sparse: bool) -> str:
    lines = [
        f"This page uses source shots {chunk[0]['shot_no']}-{chunk[-1]['shot_no']} from the locked shot_data source.",
        "Each panel keeps source-shot order; Panel 1 uses the first source shot in this page range.",
        "Panel 1 may be rewritten as a wider spatial anchor only inside the first source shot's facts.",
    ]
    if sparse:
        lines.append("Panels after the last source event are quiet continuation beats with no new plot, props, or readable screen information.")
    return "\n".join(lines)


def panel_anchor(chunk: list[dict[str, Any]], logs: dict[str, dict[str, Any]]) -> str:
    shot = chunk[0]
    log = logs.get(str(shot.get("scene_id", "")), {})
    return (
        f"Panel 1 anchors {shot.get('scene', '')} using source shot C{shot.get('shot_no')} only. "
        f"{log.get('spatial_axis', '')} "
        "Show enough floor, wall, ceiling, and character placement to make later panels inherit the same layout without moving a later source shot into Panel 1."
    )


def geometry_lock(chunk: list[dict[str, Any]], logs: dict[str, dict[str, Any]]) -> str:
    names: list[str] = []
    for shot in chunk:
        log = logs.get(str(shot.get("scene_id", "")), {})
        for fixed in log.get("fixed_objects", []):
            label = fixed.get("name") if isinstance(fixed, dict) else None
            if label and label not in names:
                names.append(label)
    fixed_text = "、".join(names) if names else "地下空间固定岩壁、地面、雾体位置"
    return f"Lock fixed geometry for {fixed_text}. Keep cave walls, floor fractures, mist-core position, and fixed boundaries consistent within each scene segment."


def object_boundaries(chunk: list[dict[str, Any]]) -> str:
    props: list[str] = []
    for shot in chunk:
        for prop in shot.get("visible_props", []):
            if prop not in props:
                props.append(prop)
    prop_text = "、".join(props) if props else "no concrete handheld props"
    return f"Visible object boundary: {prop_text}. Offscreen voices remain offscreen; do not draw their speakers unless listed as visible in the source shot."


def visual_sentence(shot: dict[str, Any], panel_index: int, distance_lock: str, is_continuation: bool = False) -> str:
    chars = visible_names(shot.get("visible_characters", []))
    props = prop_names(shot.get("visible_props", []))
    if is_continuation:
        return (
            f"PANEL-{panel_index}: A quiet continuation holds the same final transition state, with visible characters {chars} "
            f"and visible props {props}; the composition stays silent, sparse, text-free, and does not add a new story fact."
        )
    tag = camera_tag(shot)
    prompt = str(shot.get("prompt", ""))
    composition = clean_text(prompt_field(prompt, "构图")) or "the stated source composition"
    movement = clean_text(prompt_field(prompt, "运镜手法")) or "a fixed camera"
    content = clean_text(prompt_field(prompt, "画面内容") or str(shot.get("source_paragraph", ""))) or f"source shot C{shot.get('shot_no')} action"
    distance_sentence = ""
    if distance_lock != "none":
        distance_sentence = f" Distance stage lock: {distance_lock}"
    return (
        f"PANEL-{panel_index}: Use a {tag} view; show {composition} with visible characters {chars} and visible props {props}; "
        f"{content}; keep the motion idea of {movement} inside the panel without changing the strict panel frame.{distance_sentence}"
    )


def page_prompt(page_no: int, chunk: list[dict[str, Any]], logs: dict[str, dict[str, Any]], sparse: bool) -> str:
    locks = distance_locks(chunk)
    padded = list(chunk)
    padded_locks = list(locks)
    while len(padded) < 9:
        padded.append(chunk[-1])
        padded_locks.append("none")
    lines = [
        f"# {page_title(page_no, chunk)}",
        "",
        "DELIVERABLE:",
        "@CANON(HARD_PHRASES)",
        "@CANON(GEOMETRY_BLUEPRINT)",
        "",
        "SYSTEM_STYLE_LAYER:",
        "@CANON(SYSTEM_STYLE_LAYER)",
        "",
        "SCENE_LAYER:",
        page_scene_layer(chunk, logs),
        "",
        "CAMERA_RULE_LAYER:",
        page_camera_layer(chunk),
        "",
        "CONTINUITY_LAYER:",
        page_continuity_layer(chunk, sparse),
        "",
        "TEXT_DERIVED_LAYOUT:",
        page_layout_layer(chunk, sparse),
        "",
        "PANEL_1_MASTER_SPATIAL_LAYOUT_ANCHOR:",
        panel_anchor(chunk, logs),
        "",
        "DOOR_WINDOW_FURNITURE_GEOMETRY_LOCK:",
        geometry_lock(chunk, logs),
        "",
        "VEHICLE_AND_AXIS_LOCKS:",
        "No vehicle appears on this page. Preserve character eyelines, side-axis relationships, shoulder positions, and screen-left/screen-right continuity instead.",
        "",
        "OBJECT_VISIBILITY_AND_BOUNDARIES:",
        object_boundaries(chunk),
        "",
        "PANEL_LAYER PANEL-1 to PANEL-9:",
    ]
    for index, shot in enumerate(padded, 1):
        lines.append(visual_sentence(shot, index, padded_locks[index - 1], index > len(chunk)))
    lines.extend(["", "NEGATIVE_CONSTRAINTS:", "@CANON(NEGATIVE_CONSTRAINTS)", ""])
    return "\n".join(lines)


def analysis_doc(data: dict[str, Any], pages: list[list[dict[str, Any]]], out_dir: Path) -> str:
    lines = [
        "# su-image9 v2.0.2 分析与锁定",
        "",
        "## 来源范围",
        "",
        f"- 镜头数：{len(data.get('shots', []))}",
        "- 派生策略：严格保持源镜头顺序；按场景/叙事层级感知分页，不再固定每 9 镜头硬切。",
        "- 距离阶段：相邻镜头出现靠近/停步终点时，前序 Panel 写入 distance_stage_lock。",
        "",
        "## 分页方案",
        "",
        "| 页面 | 源镜头 | scene_id | layer | sparse_page | split_reason |",
        "|---|---:|---|---|---|---|",
    ]
    for page_no, chunk in enumerate(pages, 1):
        lines.append(
            f"| PAGE-{page_no:02d} | {chunk[0]['shot_no']}-{chunk[-1]['shot_no']} | "
            f"{'/'.join(page_scene_ids(chunk)) or 'unknown'} | {'/'.join(page_layer_keys(chunk))} | "
            f"{str(len(chunk) < 9).lower()} | {page_split_reason(chunk, 9)} |"
        )
    lines.extend(
        [
            "",
            "## 产物",
            "",
            f"- panel_plan.json：{out_dir / 'panel_plan.json'}",
            f"- page-map.json：{out_dir / 'page-map.json'}",
            f"- final_image_prompts.md：{out_dir / 'final_image_prompts.md'}",
            f"- final_image_prompts.compiled.md：{out_dir / 'final_image_prompts.compiled.md'}",
            f"- validation_report.json：{out_dir / 'validation_report.json'}",
        ]
    )
    return "\n".join(lines) + "\n"


def build_panel_plan(data: dict[str, Any], pages: list[list[dict[str, Any]]]) -> dict[str, Any]:
    logs = scene_logs(data)
    plan_pages: list[dict[str, Any]] = []
    for page_no, chunk in enumerate(pages, 1):
        locks = distance_locks(chunk)
        padded = list(chunk)
        padded_locks = list(locks)
        while len(padded) < 9:
            padded.append(chunk[-1])
            padded_locks.append("none")
        page = {
            "page": f"PAGE-{page_no:02d}",
            "sparse_page": len(chunk) < 9,
            "source_shot_range": f"{chunk[0]['shot_no']}-{chunk[-1]['shot_no']}",
            "sequence_order_policy": "strict_source_order_no_anchor_reorder",
            "page_split_policy": page_bridge_policy(chunk),
            "source_scene_ids": page_scene_ids(chunk),
            "source_layer_keys": page_layer_keys(chunk),
            "split_reason": page_split_reason(chunk, 9),
            "anchor_decision": "deterministic_source_order",
            "panels": [],
        }
        for panel_index, shot in enumerate(padded, 1):
            page["panels"].append(
                panel_plan_item(
                    shot,
                    panel_index,
                    logs.get(str(shot.get("scene_id", ""))),
                    padded_locks[panel_index - 1],
                    sparse=panel_index > len(chunk),
                )
            )
        plan_pages.append(page)
    return {
        "skill": "su-image9",
        "version": VERSION,
        "canon_version": CANON_VERSION,
        "reference_binding_status": "prompt_only",
        "forbidden_prompt_tokens_extra": [],
        "source_precheck_status": data.get("validation_report", {}).get("status"),
        "pages": plan_pages,
    }


def build_page_map(pages: list[list[dict[str, Any]]]) -> dict[str, Any]:
    mapped_pages: list[dict[str, Any]] = []
    for page_no, chunk in enumerate(pages, 1):
        padded = list(chunk)
        while len(padded) < 9:
            padded.append(chunk[-1])
        mapped_pages.append(
            {
                "page_no": page_no,
                "layout": "9",
                "source": f"PAGE-{page_no:02d}.png",
                "header": f"{chunk[0].get('scene', '')}｜镜头{chunk[0]['shot_no']:03d}-{chunk[-1]['shot_no']:03d}",
                "source_shot_range": f"{chunk[0]['shot_no']}-{chunk[-1]['shot_no']}",
                "sparse_page": len(chunk) < 9,
                "page_split_policy": page_bridge_policy(chunk),
                "split_reason": page_split_reason(chunk, 9),
                "panels": [
                    {
                        "panel_no": panel_index,
                        "shot_nos": [int(shot["shot_no"])],
                        "label_shot_no": int(shot["shot_no"]),
                    }
                    for panel_index, shot in enumerate(padded, 1)
                ],
            }
        )
    return {
        "skill": "su-image9",
        "version": VERSION,
        "canon_version": CANON_VERSION,
        "page_split_policy": "scene_layer_aware_strict_source_order",
        "pages": mapped_pages,
    }


def run_validator(args: argparse.Namespace, out_dir: Path, shot_data_path: Path) -> int:
    cmd = [
        sys.executable,
        str(args.validator),
        "--mode",
        "full",
        "--canon",
        str(args.canon),
        "--panel-plan",
        str(out_dir / "panel_plan.json"),
        "--final-prompts",
        str(out_dir / "final_image_prompts.md"),
        "--shot-data",
        str(shot_data_path),
        "--report",
        str(out_dir / "validation_report.json"),
        "--out",
        str(out_dir / "final_image_prompts.compiled.md"),
    ]
    result = subprocess.run(cmd, text=True)
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Derive su-image9 v2.0.2 prompt package from shot_data.json.")
    parser.add_argument("--shot-data", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--canon", type=Path, default=Path(__file__).parents[1] / "references" / "canon-locks.md")
    parser.add_argument("--validator", type=Path, default=Path(__file__).with_name("validate_su_image9_prompt.py"))
    parser.add_argument("--page-size", type=int, default=9)
    parser.add_argument("--skip-validate", action="store_true")
    args = parser.parse_args()

    data = json.loads(args.shot_data.read_text(encoding="utf-8-sig"))
    shots = data.get("shots", [])
    if not isinstance(shots, list) or not shots:
        raise SystemExit("shot_data.json must contain a non-empty shots array")
    pages = page_chunks(shots, args.page_size)
    logs = scene_logs(data)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    panel_plan = build_panel_plan(data, pages)
    page_map = build_page_map(pages)
    prompts = "\n\n".join(page_prompt(page_no, chunk, logs, len(chunk) < args.page_size) for page_no, chunk in enumerate(pages, 1))

    (args.out_dir / "panel_plan.json").write_text(json.dumps(panel_plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (args.out_dir / "page-map.json").write_text(json.dumps(page_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (args.out_dir / "final_image_prompts.md").write_text(prompts + "\n", encoding="utf-8")
    (args.out_dir / "分析与锁定.md").write_text(analysis_doc(data, pages, args.out_dir), encoding="utf-8")

    if args.skip_validate:
        return 0
    return run_validator(args, args.out_dir, args.shot_data)


if __name__ == "__main__":
    raise SystemExit(main())
