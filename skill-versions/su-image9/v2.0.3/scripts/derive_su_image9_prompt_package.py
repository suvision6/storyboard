#!/usr/bin/env python3
"""Derive a fail-closed su-image9 v2.0.3 prompt package from shot_data.json."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

VERSION = "2.0.3"
CANON_VERSION = "2.0.3"
PAGE_SIZE = 9

EXIT_PASS = 0
EXIT_REVIEW_REQUIRED = 1
EXIT_CONTRACT_FAIL = 2
EXIT_TOOL_ERROR = 3

PENDING_VALIDATION_REASON = {
    "code": "R-PENDING-VALIDATION",
    "page": "PACKAGE",
    "message": "The prompt package has not completed full validator sign-off.",
}

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
NEGATIVE_ANCHOR = {
    "close", "close-up", "medium", "over-shoulder", "ots", "insert", "pov", "reaction", "black",
    "特写", "近景", "中景", "过肩", "反应", "黑场",
}


def normalized_text_list(value: Any) -> list[str]:
    """Return non-empty strings without accepting booleans or scalar coercion."""
    if not isinstance(value, list):
        return []
    result: list[str] = []
    for item in value:
        if isinstance(item, str):
            text = item.strip()
        elif isinstance(item, dict):
            text = str(item.get("name", "")).strip()
        else:
            continue
        if text and text not in result:
            result.append(text)
    return result


def continuity_description(item: Any, *, character: bool = False) -> str:
    if isinstance(item, str):
        return item.strip()
    if not isinstance(item, dict):
        return ""
    name = str(item.get("name", "")).strip()
    if not name:
        return ""
    details: list[str] = []
    position = str(item.get("position", "")).strip()
    facing = str(item.get("facing", "")).strip()
    state = str(item.get("state", "")).strip()
    if position:
        details.append(f"position {position}")
    if character and facing:
        details.append(f"facing {facing}")
    if state:
        details.append(f"state {state}")
    return f"{name}: {', '.join(details)}" if details else name


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


def visible_names(items: Any) -> str:
    names = normalized_text_list(items)
    return "、".join(names) if names else "无"


def prop_names(items: Any) -> str:
    names = normalized_text_list(items)
    return "、".join(names) if names else "none"


def scene_logs(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(item["scene_id"]): item
        for item in data.get("continuity_logs", [])
        if isinstance(item, dict) and item.get("scene_id")
    }


def reality_layer(shot: dict[str, Any], logs: dict[str, dict[str, Any]] | None = None) -> str:
    direct = str(shot.get("reality_layer", "")).strip()
    if direct:
        return direct
    if logs:
        log = logs.get(str(shot.get("scene_id", "")), {})
        inherited = str(log.get("reality_layer", "")).strip()
        if inherited:
            return inherited
    return "unspecified"


def page_chunks(
    shots: list[dict[str, Any]],
    page_size: int,
    logs: dict[str, dict[str, Any]] | None = None,
) -> list[list[dict[str, Any]]]:
    if page_size != PAGE_SIZE:
        raise ValueError(f"page_size must be exactly {PAGE_SIZE}")
    pages: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    current_key: tuple[str, str] | None = None
    for shot in shots:
        key = (str(shot.get("scene_id", "")), reality_layer(shot, logs))
        if current and (key != current_key or len(current) == PAGE_SIZE):
            pages.append(current)
            current = []
        current.append(shot)
        current_key = key
    if current:
        pages.append(current)
    return pages


def scene_location_key(shot: dict[str, Any]) -> str:
    scene = str(shot.get("scene", ""))
    scene = re.sub(r"^\s*(?:场次\s*)?\d+(?:\s*[-._]\s*\d+)*\s*", "", scene)
    scene = re.sub(r"^同\s+", "", scene)
    scene = re.sub(r"(?:\s+(?:日|夜|晨|昏|内|外)){1,4}\s*$", "", scene)
    return re.sub(r"\s+", " ", scene).strip()


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
    return f"drawn camera follows source camera tag: {tag}"


def floor_axis(shot: dict[str, Any], log: dict[str, Any] | None, panel_index: int) -> str:
    axis = str(log.get("spatial_axis", "")) if log else ""
    if panel_index == 1:
        return f"Panel 1 anchors the page axis without changing source order: {axis or shot.get('scene', '')}"
    return f"Keep the same scene axis and screen-side relationships from Panel 1; source scene: {shot.get('scene', '')}"


def panel_plan_item(shot: dict[str, Any], panel_index: int, log: dict[str, Any] | None, distance_lock: str, sparse: bool = False) -> dict[str, Any]:
    visible_characters = normalized_text_list(shot.get("visible_characters", []))
    offscreen_characters = normalized_text_list(shot.get("offscreen_characters", []))
    visible_props = normalized_text_list(shot.get("visible_props", []))
    tag = camera_tag(shot)
    return {
        "panel": f"PANEL-{panel_index}",
        "source_shot": int(shot["shot_no"]),
        "shot_data_camera_tag": tag,
        "source_camera_tag": tag,
        "drawn_camera_tag": drawn_camera_tag(shot, panel_index, sparse),
        "beat_ids": normalized_text_list(shot.get("beat_ids", [])),
        "covered_fact_ids": normalized_text_list(shot.get("covered_fact_ids", [])),
        "visible_characters": visible_characters,
        "offscreen_characters": offscreen_characters,
        "visible_props": visible_props,
        "continuity_updates": shot.get("continuity_updates", []) if isinstance(shot.get("continuity_updates", []), list) else [],
        "visible_only": f"visible characters: {visible_names(visible_characters)}; visible props: {prop_names(visible_props)}",
        "action_composition": shot_summary(shot)[:900],
        "floor_axis_delta": floor_axis(shot, log, panel_index),
        "prop_state": prop_names(visible_props),
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


def page_layer_keys(chunk: list[dict[str, Any]], logs: dict[str, dict[str, Any]] | None = None) -> list[str]:
    result: list[str] = []
    for shot in chunk:
        key = reality_layer(shot, logs)
        if key not in result:
            result.append(key)
    return result


def page_bridge_policy(chunk: list[dict[str, Any]]) -> str:
    return "strict_single_scene_single_reality_layer"


def page_split_reason(chunk: list[dict[str, Any]], page_size: int) -> str:
    if len(chunk) < page_size:
        return "scene_reality_boundary_or_end_of_source"
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
            description
            for item in log.get("fixed_objects", [])
            if (description := continuity_description(item))
        )
        chars = "; ".join(
            description
            for item in log.get("characters", [])
            if (description := continuity_description(item, character=True))
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
        "Maintain one consistent screen geography inside this page. Panel 1 preserves the first source shot's original camera tag and composition.",
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
        "Panel 1 preserves the first source shot's camera tag and visible facts without widening or redesigning it.",
    ]
    if sparse:
        lines.append("Panels after the last source event are quiet continuation beats with no new plot, props, or readable screen information.")
    return "\n".join(lines)


def panel_anchor(chunk: list[dict[str, Any]], logs: dict[str, dict[str, Any]]) -> str:
    shot = chunk[0]
    log = logs.get(str(shot.get("scene_id", "")), {})
    return (
        f"Panel 1 preserves {shot.get('scene', '')} using source shot C{shot.get('shot_no')} only. "
        f"{log.get('spatial_axis', '')} "
        "Keep its original camera tag, visible character list, visible props, and composition; do not borrow facts from a later source shot."
    )


def geometry_lock(chunk: list[dict[str, Any]], logs: dict[str, dict[str, Any]]) -> str:
    names: list[str] = []
    for shot in chunk:
        log = logs.get(str(shot.get("scene_id", "")), {})
        for fixed in log.get("fixed_objects", []):
            label = continuity_description(fixed)
            if label and label not in names:
                names.append(label)
    if names:
        return f"Lock only the source-defined fixed geometry: {'; '.join(names)}. Preserve those positions and states across the page."
    return "No fixed geometry is registered for this page. Do not invent doors, windows, furniture, terrain, boundaries, or effects."


VEHICLE_TERMS = (
    "车", "汽车", "轿车", "卡车", "货车", "摩托", "自行车", "巴士", "公交", "列车", "火车",
)
ENGLISH_VEHICLE_TERMS = ("vehicle", "car", "truck", "motorcycle", "bicycle", "bus", "train")


def is_vehicle_name(value: str) -> bool:
    if any(term in value for term in VEHICLE_TERMS):
        return True
    return any(re.search(rf"\b{re.escape(term)}s?\b", value, flags=re.IGNORECASE) for term in ENGLISH_VEHICLE_TERMS)


def source_vehicle_facts(chunk: list[dict[str, Any]], logs: dict[str, dict[str, Any]]) -> list[str]:
    candidates: list[str] = []
    for shot in chunk:
        candidates.extend(normalized_text_list(shot.get("visible_props", [])))
        log = logs.get(str(shot.get("scene_id", "")), {})
        candidates.extend(normalized_text_list(log.get("fixed_objects", [])))
    return [item for item in dict.fromkeys(candidates) if is_vehicle_name(item)]


def vehicle_axis_layer(chunk: list[dict[str, Any]], logs: dict[str, dict[str, Any]]) -> str:
    vehicles = source_vehicle_facts(chunk, logs)
    lines = ["Preserve source-defined character eyelines, side-axis relationships, and screen-left/screen-right continuity."]
    if vehicles:
        lines.append(f"Source-defined vehicles or transport objects: {'、'.join(vehicles)}. Preserve only their registered positions and states.")
    else:
        lines.append("Do not introduce any object that is absent from the source facts.")
    return " ".join(lines)


def object_boundaries(chunk: list[dict[str, Any]]) -> str:
    props: list[str] = []
    for shot in chunk:
        for prop in normalized_text_list(shot.get("visible_props", [])):
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
        vehicle_axis_layer(chunk, logs),
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
        "# su-image9 v2.0.3 分析与锁定",
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
            f"{'/'.join(page_scene_ids(chunk)) or 'unknown'} | {'/'.join(page_layer_keys(chunk, scene_logs(data)))} | "
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
            "source_layer_keys": page_layer_keys(chunk, logs),
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
        "release_ready": False,
        "review_required_reasons": [dict(PENDING_VALIDATION_REASON)],
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
                "release_ready": False,
                "review_required_reasons": [dict(PENDING_VALIDATION_REASON)],
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
        "page_split_policy": "strict_single_scene_single_reality_layer",
        "release_ready": False,
        "review_required_reasons": [dict(PENDING_VALIDATION_REASON)],
        "pages": mapped_pages,
    }


def validate_shot_data(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["shot_data root must be a JSON object"]
    metadata = data.get("metadata")
    if not isinstance(metadata, dict):
        errors.append("metadata must be an object")
    else:
        if metadata.get("skill_name") != "su-fenjingskill-zh":
            errors.append('metadata.skill_name must be "su-fenjingskill-zh"')
        if not isinstance(metadata.get("version"), str) or not metadata.get("version", "").strip():
            errors.append("metadata.version must be a non-empty string")

    script_lock = data.get("script_lock")
    if not isinstance(script_lock, dict) or script_lock.get("status") != "locked":
        errors.append('script_lock.status must be "locked"')

    report = data.get("validation_report")
    if not isinstance(report, dict):
        errors.append("validation_report must be an object")
    else:
        status = str(report.get("status", "")).upper()
        if status in {"FAIL", "NOT_RUN"}:
            errors.append(f"upstream validation_report.status {status} cannot be used for image derivation")
        elif status not in {"PASS", "WARN"}:
            errors.append("validation_report.status must be PASS or WARN")

    logs = data.get("continuity_logs")
    if not isinstance(logs, list):
        errors.append("continuity_logs must be an array")
        logs = []
    elif not logs:
        errors.append("continuity_logs must contain at least one registered scene")
    registered_scene_ids: set[str] = set()
    for index, log in enumerate(logs, 1):
        if not isinstance(log, dict):
            errors.append(f"continuity_logs[{index}] must be an object")
            continue
        scene_id = str(log.get("scene_id", "")).strip()
        if not scene_id:
            errors.append(f"continuity_logs[{index}].scene_id must be non-empty")
        elif scene_id in registered_scene_ids:
            errors.append(f"continuity_logs scene_id {scene_id} is duplicated")
        else:
            registered_scene_ids.add(scene_id)
        for field in ("fixed_objects", "characters"):
            items = log.get(field, [])
            if not isinstance(items, list):
                errors.append(f"continuity_logs[{index}].{field} must be an array")
                continue
            for item_index, item in enumerate(items, 1):
                if isinstance(item, str) and item.strip():
                    continue
                if isinstance(item, dict) and str(item.get("name", "")).strip():
                    continue
                errors.append(
                    f"continuity_logs[{index}].{field}[{item_index}] must be a non-empty string or named object"
                )

    shots = data.get("shots")
    if not isinstance(shots, list) or not shots:
        errors.append("shots must be a non-empty array")
        return errors
    seen_shot_nos: set[int] = set()
    previous_shot_no = 0
    for index, shot in enumerate(shots, 1):
        if not isinstance(shot, dict):
            errors.append(f"shots[{index}] must be an object")
            continue
        shot_no = shot.get("shot_no")
        if isinstance(shot_no, bool) or not isinstance(shot_no, int) or shot_no <= 0:
            errors.append(f"shots[{index}].shot_no must be a positive integer")
        else:
            if shot_no in seen_shot_nos:
                errors.append(f"shot_no {shot_no} is duplicated")
            if shot_no <= previous_shot_no:
                errors.append("shots must be in strictly increasing shot_no order")
            seen_shot_nos.add(shot_no)
            previous_shot_no = shot_no
        scene_id = str(shot.get("scene_id", "")).strip()
        if not scene_id:
            errors.append(f"shots[{index}].scene_id must be non-empty")
        elif scene_id not in registered_scene_ids:
            errors.append(f"shots[{index}].scene_id {scene_id} is not registered in continuity_logs")
        if not camera_tag(shot):
            errors.append(f"shots[{index}].camera_main_image must start with a non-empty [camera tag]")
        for field in (
            "beat_ids",
            "covered_fact_ids",
            "visible_characters",
            "offscreen_characters",
            "visible_props",
            "continuity_updates",
        ):
            if not isinstance(shot.get(field), list):
                errors.append(f"shots[{index}].{field} must be an array")
    return errors


def has_spatial_anchor(shot: dict[str, Any]) -> bool:
    tokens = normalize_tag_tokens(camera_tag(shot))
    if tokens & NEGATIVE_ANCHOR:
        return False
    if str(shot.get("shot_type", "")).strip() == "master":
        return True
    return bool(tokens & POSITIVE_ANCHOR)


def review_required_reasons(
    data: dict[str, Any],
    pages: list[list[dict[str, Any]]],
) -> list[dict[str, str]]:
    logs = scene_logs(data)
    reasons: list[dict[str, str]] = []
    if str(data.get("validation_report", {}).get("status", "")).upper() == "WARN":
        reasons.append(
            {
                "code": "R-UPSTREAM-WARN",
                "page": "SOURCE",
                "message": "Upstream WARN requires human review before a v2.0.3 image package can be released.",
            }
        )
    for page_no, chunk in enumerate(pages, 1):
        page = f"PAGE-{page_no:02d}"
        if len(page_scene_ids(chunk)) != 1:
            reasons.append(
                {"code": "R-CROSS-SCENE", "page": page, "message": "A page cannot bridge multiple scene_id values."}
            )
        if len(page_layer_keys(chunk, logs)) != 1:
            reasons.append(
                {"code": "R-CROSS-LAYER", "page": page, "message": "A page cannot bridge multiple reality layers."}
            )
        if len(chunk) < PAGE_SIZE:
            reasons.append(
                {
                    "code": "R-SPARSE-UNIQUENESS",
                    "page": page,
                    "message": "Fewer than nine source shots cannot prove nine unique visual tasks in v2.0.3.",
                }
            )
        if chunk and not has_spatial_anchor(chunk[0]):
            reasons.append(
                {
                    "code": "R-FIRST-SHOT-ANCHOR",
                    "page": page,
                    "message": "The first source shot is not a declared master/wide/full spatial anchor and may not be rewritten.",
                }
            )
    return reasons


def write_status_report(
    out_dir: Path,
    status: str,
    *,
    errors: list[str] | None = None,
    review_reasons: list[dict[str, str]] | None = None,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "skill": "su-image9",
        "version": VERSION,
        "status": status,
        "exit_code": {
            "PASS": EXIT_PASS,
            "REVIEW_REQUIRED": EXIT_REVIEW_REQUIRED,
            "CONTRACT_FAIL": EXIT_CONTRACT_FAIL,
            "TOOL_ERROR": EXIT_TOOL_ERROR,
        }.get(status, EXIT_TOOL_ERROR),
        "release_ready": False,
        "errors": errors or [],
        "review_required_reasons": review_reasons or [],
    }
    (out_dir / "validation_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def set_release_state(
    panel_plan: dict[str, Any],
    page_map: dict[str, Any],
    *,
    ready: bool,
    reasons: list[dict[str, str]],
) -> None:
    panel_plan["release_ready"] = ready
    panel_plan["review_required_reasons"] = [dict(item) for item in reasons]
    page_map["release_ready"] = ready
    page_map["review_required_reasons"] = [dict(item) for item in reasons]
    for page in page_map.get("pages", []):
        if not isinstance(page, dict):
            continue
        page["release_ready"] = ready
        page["review_required_reasons"] = [dict(item) for item in reasons]


def write_release_manifests(out_dir: Path, panel_plan: dict[str, Any], page_map: dict[str, Any]) -> None:
    (out_dir / "page-map.json").write_text(
        json.dumps(page_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "panel_plan.json").write_text(
        json.dumps(panel_plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def run_validator(
    args: argparse.Namespace,
    out_dir: Path,
    shot_data_path: Path,
    *,
    panel_plan_path: Path | None = None,
    report_path: Path | None = None,
    compiled_path: Path | None = None,
) -> int:
    cmd = [
        sys.executable,
        str(args.validator),
        "--mode",
        "full",
        "--canon",
        str(args.canon),
        "--panel-plan",
        str(panel_plan_path or out_dir / "panel_plan.json"),
        "--final-prompts",
        str(out_dir / "final_image_prompts.md"),
        "--shot-data",
        str(shot_data_path),
        "--report",
        str(report_path or out_dir / "validation_report.json"),
        "--out",
        str(compiled_path or out_dir / "final_image_prompts.compiled.md"),
    ]
    result = subprocess.run(cmd, text=True)
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Derive a fail-closed su-image9 v2.0.3 prompt package from shot_data.json.")
    parser.add_argument("--shot-data", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--canon", type=Path, default=Path(__file__).parents[1] / "references" / "canon-locks.md")
    parser.add_argument("--validator", type=Path, default=Path(__file__).with_name("validate_su_image9_prompt.py"))
    parser.add_argument("--page-size", type=int, choices=[PAGE_SIZE], default=PAGE_SIZE)
    parser.add_argument("--skip-validate", action="store_true")
    args = parser.parse_args()

    try:
        if args.out_dir.exists():
            if not args.out_dir.is_dir():
                print(f"CONTRACT_FAIL: --out-dir exists and is not a directory: {args.out_dir}", file=sys.stderr)
                return EXIT_CONTRACT_FAIL
            if next(args.out_dir.iterdir(), None) is not None:
                print(f"CONTRACT_FAIL: --out-dir must be absent or empty: {args.out_dir}", file=sys.stderr)
                return EXIT_CONTRACT_FAIL
    except OSError as exc:
        print(f"TOOL_ERROR: cannot inspect --out-dir: {exc}", file=sys.stderr)
        return EXIT_TOOL_ERROR

    if args.skip_validate:
        write_status_report(
            args.out_dir,
            "CONTRACT_FAIL",
            errors=["--skip-validate is disabled in v2.0.3 because an unvalidated package cannot be release-ready."],
        )
        return EXIT_CONTRACT_FAIL

    try:
        data = json.loads(args.shot_data.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError) as exc:
        print(f"TOOL_ERROR: cannot read shot_data.json: {exc}", file=sys.stderr)
        return EXIT_TOOL_ERROR
    except json.JSONDecodeError as exc:
        write_status_report(args.out_dir, "CONTRACT_FAIL", errors=[f"shot_data.json is invalid JSON: {exc}"])
        return EXIT_CONTRACT_FAIL

    input_errors = validate_shot_data(data)
    if input_errors:
        write_status_report(args.out_dir, "CONTRACT_FAIL", errors=input_errors)
        return EXIT_CONTRACT_FAIL

    shots = data["shots"]
    logs = scene_logs(data)
    pages = page_chunks(shots, args.page_size, logs)
    review_reasons = review_required_reasons(data, pages)
    if review_reasons:
        write_status_report(args.out_dir, "REVIEW_REQUIRED", review_reasons=review_reasons)
        return EXIT_REVIEW_REQUIRED

    try:
        canon_available = args.canon.is_file()
    except OSError as exc:
        print(f"TOOL_ERROR: cannot inspect canon: {exc}", file=sys.stderr)
        return EXIT_TOOL_ERROR
    if not canon_available:
        reason = {
            "code": "R-CANON-MISSING",
            "page": "PACKAGE",
            "message": f"The required canon file is unavailable: {args.canon}",
        }
        write_status_report(args.out_dir, "REVIEW_REQUIRED", review_reasons=[reason])
        return EXIT_REVIEW_REQUIRED

    try:
        validator_available = args.validator.is_file()
    except OSError as exc:
        print(f"TOOL_ERROR: cannot inspect validator: {exc}", file=sys.stderr)
        return EXIT_TOOL_ERROR
    if not validator_available:
        reason = {
            "code": "R-VALIDATOR-MISSING",
            "page": "PACKAGE",
            "message": f"The required validator is unavailable: {args.validator}",
        }
        write_status_report(args.out_dir, "REVIEW_REQUIRED", review_reasons=[reason])
        return EXIT_REVIEW_REQUIRED

    args.out_dir.mkdir(parents=True, exist_ok=True)
    panel_plan = build_panel_plan(data, pages)
    page_map = build_page_map(pages)
    prompts = "\n\n".join(page_prompt(page_no, chunk, logs, len(chunk) < args.page_size) for page_no, chunk in enumerate(pages, 1))

    write_release_manifests(args.out_dir, panel_plan, page_map)
    (args.out_dir / "final_image_prompts.md").write_text(prompts + "\n", encoding="utf-8")
    (args.out_dir / "分析与锁定.md").write_text(analysis_doc(data, pages, args.out_dir), encoding="utf-8")

    candidate_plan = json.loads(json.dumps(panel_plan, ensure_ascii=False))
    candidate_map = json.loads(json.dumps(page_map, ensure_ascii=False))
    set_release_state(candidate_plan, candidate_map, ready=True, reasons=[])
    with tempfile.TemporaryDirectory(prefix="su-image9-v203-") as tmp:
        temp_dir = Path(tmp)
        candidate_path = temp_dir / "panel_plan.json"
        candidate_report = temp_dir / "validation_report.json"
        candidate_compiled = temp_dir / "final_image_prompts.compiled.md"
        candidate_path.write_text(
            json.dumps(candidate_plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        preflight_code = run_validator(
            args,
            args.out_dir,
            args.shot_data,
            panel_plan_path=candidate_path,
            report_path=candidate_report,
            compiled_path=candidate_compiled,
        )
        if preflight_code == EXIT_PASS:
            if not candidate_report.is_file() or not candidate_compiled.is_file():
                reason = {
                    "code": "R-VALIDATOR-OUTPUT-MISSING",
                    "page": "PACKAGE",
                    "message": "Validator returned PASS without both compiled prompt and validation report outputs.",
                }
                set_release_state(panel_plan, page_map, ready=False, reasons=[reason])
                write_release_manifests(args.out_dir, panel_plan, page_map)
                return EXIT_TOOL_ERROR
            final_compiled = args.out_dir / "final_image_prompts.compiled.md"
            try:
                report_data = json.loads(candidate_report.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                reason = {
                    "code": "R-VALIDATOR-REPORT-INVALID",
                    "page": "PACKAGE",
                    "message": f"Validator returned PASS with an unreadable report: {exc}",
                }
                set_release_state(panel_plan, page_map, ready=False, reasons=[reason])
                write_release_manifests(args.out_dir, panel_plan, page_map)
                write_status_report(args.out_dir, "TOOL_ERROR", errors=[reason["message"]], review_reasons=[reason])
                return EXIT_TOOL_ERROR
            if not isinstance(report_data, dict):
                reason = {
                    "code": "R-VALIDATOR-REPORT-INVALID",
                    "page": "PACKAGE",
                    "message": "Validator returned PASS with a non-object report.",
                }
                set_release_state(panel_plan, page_map, ready=False, reasons=[reason])
                write_release_manifests(args.out_dir, panel_plan, page_map)
                write_status_report(args.out_dir, "TOOL_ERROR", errors=[reason["message"]], review_reasons=[reason])
                return EXIT_TOOL_ERROR
            report_data["compiled_path"] = str(final_compiled.resolve())
            final_compiled.write_bytes(candidate_compiled.read_bytes())
            (args.out_dir / "validation_report.json").write_text(
                json.dumps(report_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            set_release_state(panel_plan, page_map, ready=True, reasons=[])
            write_release_manifests(args.out_dir, panel_plan, page_map)
            return EXIT_PASS

    reason = {
        "code": "R-VALIDATION-FAILED",
        "page": "PACKAGE",
        "message": f"Full validator sign-off failed with exit code {preflight_code}.",
    }
    set_release_state(panel_plan, page_map, ready=False, reasons=[reason])
    write_release_manifests(args.out_dir, panel_plan, page_map)
    run_validator(args, args.out_dir, args.shot_data)
    return preflight_code


if __name__ == "__main__":
    raise SystemExit(main())
