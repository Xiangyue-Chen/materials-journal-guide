"""Validated writing guidance for the journal submission workbench."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml


JOURNAL_LIST_FIELDS = ("fit_signals", "risk_signals")
FIGURE_KINDS = {
    "concept",
    "process",
    "microstructure",
    "performance",
    "mechanism",
    "validation",
    "summary",
}


def _nonblank(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _validate_string_list(owner: str, field: str, value: object, minimum: int) -> None:
    if not isinstance(value, list) or len(value) < minimum:
        raise ValueError(f"{owner}: {field} must contain at least {minimum} items")
    if any(not _nonblank(item) for item in value):
        raise ValueError(f"{owner}: {field} must contain nonblank strings")


def _validate_profile(profile_id: str, profile: object) -> None:
    if not isinstance(profile, dict):
        raise ValueError(f"profile {profile_id} must be a mapping")
    if not _nonblank(profile.get("label")):
        raise ValueError(f"profile {profile_id}: label must be a nonblank string")

    structure = profile.get("structure")
    if not isinstance(structure, list) or len(structure) < 5:
        raise ValueError(f"profile {profile_id}: structure must contain at least 5 steps")
    for step in structure:
        if not isinstance(step, dict) or not all(
            _nonblank(step.get(field)) for field in ("title", "task")
        ):
            raise ValueError(
                f"profile {profile_id}: structure steps require title and task"
            )

    figure_story = profile.get("figure_story")
    if not isinstance(figure_story, list) or len(figure_story) < 5:
        raise ValueError(
            f"profile {profile_id}: figure_story must contain at least 5 steps"
        )
    for figure in figure_story:
        if not isinstance(figure, dict) or not all(
            _nonblank(figure.get(field)) for field in ("title", "question", "kind")
        ):
            raise ValueError(
                f"profile {profile_id}: figure_story items require title, question and kind"
            )
        if figure["kind"] not in FIGURE_KINDS:
            raise ValueError(
                f"profile {profile_id}: unknown figure kind {figure['kind']}"
            )

    _validate_string_list(profile_id, "checklist", profile.get("checklist"), 5)


def load_guidance(
    path: Path, journal_ids: set[str]
) -> dict[str, dict[str, Any]]:
    """Load, validate, and merge writing profiles with journal overrides."""

    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("guidance root must be a mapping")
    profiles = raw.get("profiles")
    journals = raw.get("journals")
    if not isinstance(profiles, dict) or not profiles:
        raise ValueError("guidance profiles must be a nonempty mapping")
    if not isinstance(journals, dict):
        raise ValueError("guidance journals must be a mapping")

    for profile_id, profile in profiles.items():
        _validate_profile(str(profile_id), profile)

    configured_ids = set(journals)
    missing = sorted(journal_ids - configured_ids)
    extra = sorted(configured_ids - journal_ids)
    if missing:
        raise ValueError(f"missing guidance for journal IDs: {', '.join(missing)}")
    if extra:
        raise ValueError(f"guidance contains unknown journal IDs: {', '.join(extra)}")

    merged: dict[str, dict[str, Any]] = {}
    for journal_id, override in journals.items():
        if not isinstance(override, dict):
            raise ValueError(f"{journal_id}: guidance must be a mapping")
        profile_id = override.get("profile")
        if not _nonblank(profile_id) or profile_id not in profiles:
            raise ValueError(f"{journal_id}: unknown profile {profile_id}")
        if not _nonblank(override.get("editorial_angle")):
            raise ValueError(f"{journal_id}: editorial_angle must be a nonblank string")
        for field in JOURNAL_LIST_FIELDS:
            _validate_string_list(journal_id, field, override.get(field), 3)

        profile = deepcopy(profiles[profile_id])
        profile.update(deepcopy(override))
        profile["profile_id"] = profile_id
        profile["profile_label"] = profiles[profile_id]["label"]
        _validate_profile(str(journal_id), profile)
        merged[journal_id] = profile

    return merged


def explain_requirement(value: object) -> dict[str, str]:
    """Turn a raw requirement into an explicit evidence state and explanation."""

    raw = str(value).strip()
    if ("稿件类型" in raw or "文章类型" in raw) and "变化" in raw:
        summary = raw.replace("，需投稿前复核", "").replace("需投稿前复核", "").strip("，；。 ")
        return {
            "status": "按文章类型变化",
            "summary": summary,
            "reason": "Article、Review、Letter 等内容类型使用不同限制，不能合并成一个数字。",
        }

    if raw == "需投稿前复核":
        return {
            "status": "官网未给统一值",
            "summary": "当前未找到稳定统一值",
            "reason": "公开指南未给出可适用于全部原创研究稿件的固定要求，不用二手信息补空。",
        }

    if "需投稿前复核" in raw:
        summary = raw.replace("，需投稿前复核", "").replace("需投稿前复核", "").strip("，； ")
        if ("随" in raw and "变化" in raw) or "依文章类型" in raw:
            return {
                "status": "按文章类型变化",
                "summary": summary or "由所选文章类型决定",
                "reason": "Article、Review、Letter 等内容类型使用不同限制，不能合并成一个数字。",
            }
        return {
            "status": "以投稿系统为准",
            "summary": summary or "提交时由投稿系统给出",
            "reason": "该选项会随稿件或投稿流程动态出现，公开页面没有稳定的统一设置。",
        }

    if "需按最新作者指南复核" in raw:
        summary = raw.replace("需按最新作者指南复核", "").strip("，；。 ")
        return {
            "status": "官网未给统一值",
            "summary": summary or "当前未找到稳定统一值",
            "reason": "公开指南未给出稳定统一值；保留问题本身，不用二手信息补空。",
        }

    if raw.startswith("未列为"):
        return {
            "status": "非必交项",
            "summary": raw,
            "reason": "官方原创研究论文清单中不是常规必交材料；特殊稿件类型仍可能另有要求。",
        }

    return {
        "status": "官网明确",
        "summary": raw,
        "reason": "官方作者指南已记录明确要求；页面同时保留核验日期与原始链接。",
    }


def build_workbench(
    record: dict[str, Any], guidance: dict[str, Any]
) -> dict[str, Any]:
    """Compose official metadata and clearly labelled writing guidance."""

    return {
        "journal_id": record["id"],
        "journal_name": record["name"],
        "abbreviation": record["abbreviation"],
        "tier": record["tier"],
        "scope": record["scope"],
        "guide_url": record["guide_url"],
        "verified_on": record["verified_on"],
        "guidance_label": "本站写作建议",
        "official_label": "官方要求",
        "profile_label": guidance["profile_label"],
        "editorial_angle": guidance["editorial_angle"],
        "fit_signals": deepcopy(guidance["fit_signals"]),
        "risk_signals": deepcopy(guidance["risk_signals"]),
        "structure": deepcopy(guidance["structure"]),
        "figure_story": deepcopy(guidance["figure_story"]),
        "checklist": deepcopy(guidance["checklist"]),
    }
