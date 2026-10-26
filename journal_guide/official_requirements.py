"""Validated, source-backed manuscript requirements for each journal."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml


RECORD_FIELDS = {
    "default_article_type",
    "requirement_scope",
    "verified_on",
    "source_urls",
    "section_requirements",
    "technical_requirements",
    "resources",
}
REQUIREMENT_FIELDS = {"section", "requirement", "scope", "source_url"}
TECHNICAL_FIELDS = {"item", "requirement", "scope", "source_url"}
RESOURCE_FIELDS = {"label", "kind", "url", "note"}
ALLOWED_SCOPES = {"期刊专属", "出版社通用", "官网未公开稳定值"}
ALLOWED_RESOURCE_KINDS = {
    "官方指南",
    "官方模板",
    "官方示例",
    "已发表论文实例",
}
FORBIDDEN_PLACEHOLDERS = ("需投稿前复核",)


def _nonblank(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _https_url(value: object) -> bool:
    return _nonblank(value) and str(value).startswith("https://")


def _validate_requirement_items(
    journal_id: str,
    field: str,
    items: object,
    *,
    minimum: int,
    expected_fields: set[str],
) -> None:
    if not isinstance(items, list) or len(items) < minimum:
        raise ValueError(
            f"{journal_id}: {field} must contain at least {minimum} items"
        )
    label_field = "section" if field == "section_requirements" else "item"
    for index, item in enumerate(items):
        if not isinstance(item, dict) or set(item) != expected_fields:
            raise ValueError(
                f"{journal_id}: {field}[{index}] must contain "
                f"{', '.join(sorted(expected_fields))}"
            )
        text_fields = expected_fields - {"source_url"}
        if not all(_nonblank(item[key]) for key in text_fields):
            raise ValueError(f"{journal_id}: {field}[{index}] values must be nonblank")
        if item["scope"] not in ALLOWED_SCOPES:
            raise ValueError(
                f"{journal_id}: {field}[{index}] has unknown scope {item['scope']}"
            )
        if not _https_url(item["source_url"]):
            raise ValueError(
                f"{journal_id}: {field}[{index}] source_url must be an https URL"
            )
        if any(token in item["requirement"] for token in FORBIDDEN_PLACEHOLDERS):
            raise ValueError(
                f"{journal_id}: {field}[{index}] contains forbidden placeholder"
            )
        if not _nonblank(item[label_field]):
            raise ValueError(f"{journal_id}: {field}[{index}] label must be nonblank")


def _validate_record(journal_id: str, record: object) -> None:
    if not isinstance(record, dict) or set(record) != RECORD_FIELDS:
        raise ValueError(
            f"{journal_id}: official record must contain exactly "
            f"{', '.join(sorted(RECORD_FIELDS))}"
        )
    for field in ("default_article_type", "verified_on"):
        if not _nonblank(record[field]):
            raise ValueError(f"{journal_id}: {field} must be a nonblank string")
    if record["requirement_scope"] not in ALLOWED_SCOPES:
        raise ValueError(
            f"{journal_id}: unknown requirement_scope {record['requirement_scope']}"
        )
    source_urls = record["source_urls"]
    if not isinstance(source_urls, list) or not source_urls:
        raise ValueError(f"{journal_id}: source_urls must be a nonempty list")
    if any(not _https_url(url) for url in source_urls):
        raise ValueError(f"{journal_id}: source_urls must contain https URLs")

    _validate_requirement_items(
        journal_id,
        "section_requirements",
        record["section_requirements"],
        minimum=5,
        expected_fields=REQUIREMENT_FIELDS,
    )
    _validate_requirement_items(
        journal_id,
        "technical_requirements",
        record["technical_requirements"],
        minimum=1,
        expected_fields=TECHNICAL_FIELDS,
    )

    resources = record["resources"]
    if not isinstance(resources, list) or not resources:
        raise ValueError(f"{journal_id}: resources must be a nonempty list")
    for index, resource in enumerate(resources):
        if not isinstance(resource, dict) or set(resource) != RESOURCE_FIELDS:
            raise ValueError(
                f"{journal_id}: resources[{index}] must contain "
                f"{', '.join(sorted(RESOURCE_FIELDS))}"
            )
        if not all(_nonblank(resource[key]) for key in RESOURCE_FIELDS):
            raise ValueError(f"{journal_id}: resources[{index}] values must be nonblank")
        if resource["kind"] not in ALLOWED_RESOURCE_KINDS:
            raise ValueError(
                f"{journal_id}: unknown resource kind {resource['kind']}"
            )
        if not _https_url(resource["url"]):
            raise ValueError(
                f"{journal_id}: resources[{index}] url must be an https URL"
            )


def load_official_requirements(
    path: Path, journal_ids: set[str]
) -> dict[str, dict[str, Any]]:
    """Load and validate official requirements against the journal catalogue."""

    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or set(raw) != {"journals"}:
        raise ValueError("official requirements root must contain only journals")
    journals = raw["journals"]
    if not isinstance(journals, dict):
        raise ValueError("official requirements journals must be a mapping")

    configured_ids = set(journals)
    missing = sorted(journal_ids - configured_ids)
    extra = sorted(configured_ids - journal_ids)
    if missing:
        raise ValueError(
            f"missing official requirements for journal IDs: {', '.join(missing)}"
        )
    if extra:
        raise ValueError(
            f"official requirements contain unknown journal IDs: {', '.join(extra)}"
        )

    validated: dict[str, dict[str, Any]] = {}
    for journal_id, record in journals.items():
        _validate_record(str(journal_id), record)
        validated[str(journal_id)] = deepcopy(record)
    return validated


def build_official_workbench(
    record: dict[str, Any],
    official: dict[str, Any],
    guidance: dict[str, Any],
) -> dict[str, Any]:
    """Keep sourced requirements and site-authored editorial advice separate."""

    return {
        "journal_id": record["id"],
        "journal_name": record["name"],
        "abbreviation": record["abbreviation"],
        "tier": record["tier"],
        "guide_url": record["guide_url"],
        "official": deepcopy(official),
        "editorial": {
            "label": "本站写作建议",
            "profile_label": guidance["profile_label"],
            "editorial_angle": guidance["editorial_angle"],
            "fit_signals": deepcopy(guidance["fit_signals"]),
            "risk_signals": deepcopy(guidance["risk_signals"]),
            "structure": deepcopy(guidance["structure"]),
            "checklist": deepcopy(guidance["checklist"]),
        },
    }
