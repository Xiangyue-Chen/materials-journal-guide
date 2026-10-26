"""Validated quick-reference manuscript format specifications."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import re
from typing import Any

import yaml


SPEC_KEYS = {
    "abstract",
    "manuscript_structure",
    "display_items",
    "panel_labels",
    "figure_legends",
    "references",
}
SPEC_ITEM_FIELDS = {"official", "advice", "scope", "source_url"}
BLUEPRINT_FIELDS = {"section", "task"}
RECORD_FIELDS = {
    "default_article_type",
    "verified_on",
    "quick_specs",
    "blueprint",
}
ALLOWED_SCOPES = {
    "官方硬性",
    "官方惯例",
    "官网未规定固定上限",
    "本站建议",
}
FORBIDDEN_PLACEHOLDERS = (
    "需投稿前复核",
    "按指南执行",
    "具体见官网",
    "以官网为准",
)


def _nonblank(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _validate_record(journal_id: str, record: object) -> None:
    if not isinstance(record, dict) or set(record) != RECORD_FIELDS:
        raise ValueError(
            f"{journal_id}: record must contain exactly "
            f"{', '.join(sorted(RECORD_FIELDS))}"
        )
    for field in ("default_article_type", "verified_on"):
        if not _nonblank(record[field]):
            raise ValueError(f"{journal_id}: {field} must be a nonblank string")

    quick_specs = record["quick_specs"]
    if not isinstance(quick_specs, dict) or set(quick_specs) != SPEC_KEYS:
        missing = sorted(SPEC_KEYS - set(quick_specs or {}))
        detail = f"; missing {', '.join(missing)}" if missing else ""
        raise ValueError(
            f"{journal_id}: quick_specs must contain {', '.join(sorted(SPEC_KEYS))}{detail}"
        )
    for key, item in quick_specs.items():
        if not isinstance(item, dict) or set(item) != SPEC_ITEM_FIELDS:
            raise ValueError(
                f"{journal_id}: quick_specs.{key} must contain "
                f"{', '.join(sorted(SPEC_ITEM_FIELDS))}"
            )
        for field in ("official", "advice", "scope"):
            if not _nonblank(item[field]):
                raise ValueError(
                    f"{journal_id}: quick_specs.{key}.{field} must be nonblank"
                )
        if not _nonblank(item["source_url"]) or not str(
            item["source_url"]
        ).startswith("https://"):
            raise ValueError(
                f"{journal_id}: quick_specs.{key} source_url must be an https URL"
            )
        if item["scope"] not in ALLOWED_SCOPES:
            raise ValueError(
                f"{journal_id}: quick_specs.{key} has unknown scope {item['scope']}"
            )
        combined = f'{item["official"]} {item["advice"]}'
        if any(token in combined for token in FORBIDDEN_PLACEHOLDERS):
            raise ValueError(
                f"{journal_id}: quick_specs.{key} contains forbidden placeholder"
            )
        if "官网未规定固定上限" in item["official"]:
            if item["scope"] != "官网未规定固定上限":
                raise ValueError(
                    f"{journal_id}: quick_specs.{key} unknown limit has wrong scope"
                )
            if not re.search(r"\d|→|建议", item["advice"]):
                raise ValueError(
                    f"{journal_id}: quick_specs.{key} must include concrete advice"
                )

    blueprint = record["blueprint"]
    if not isinstance(blueprint, list) or len(blueprint) < 5:
        raise ValueError(f"{journal_id}: blueprint must contain at least 5 sections")
    for index, item in enumerate(blueprint):
        if not isinstance(item, dict) or set(item) != BLUEPRINT_FIELDS:
            raise ValueError(
                f"{journal_id}: blueprint[{index}] must contain section and task"
            )
        if not all(_nonblank(item[field]) for field in BLUEPRINT_FIELDS):
            raise ValueError(f"{journal_id}: blueprint[{index}] values must be nonblank")


def load_format_specs(
    path: Path, journal_ids: set[str]
) -> dict[str, dict[str, Any]]:
    """Load and validate quick-reference specs against the journal catalogue."""

    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or set(raw) != {"journals"}:
        raise ValueError("format specs root must contain only journals")
    journals = raw["journals"]
    if not isinstance(journals, dict):
        raise ValueError("format specs journals must be a mapping")

    configured_ids = set(journals)
    missing = sorted(journal_ids - configured_ids)
    extra = sorted(configured_ids - journal_ids)
    if missing:
        raise ValueError(f"missing format specs for journal IDs: {', '.join(missing)}")
    if extra:
        raise ValueError(f"format specs contain unknown journal IDs: {', '.join(extra)}")

    validated: dict[str, dict[str, Any]] = {}
    for journal_id, record in journals.items():
        _validate_record(str(journal_id), record)
        validated[str(journal_id)] = deepcopy(record)
    return validated

