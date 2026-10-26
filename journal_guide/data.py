"""Load and validate the source-backed journal catalogue."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml


REQUIRED_FIELDS = (
    "id",
    "name",
    "abbreviation",
    "publisher",
    "tier",
    "tier_order",
    "topics",
    "scope",
    "article_types",
    "initial_submission",
    "abstract_limit",
    "word_limit",
    "graphical_abstract",
    "highlights",
    "references",
    "figures",
    "data_policy",
    "oa_model",
    "peer_review",
    "special_notes",
    "homepage_url",
    "guide_url",
    "source_urls",
    "verified_on",
    "verification_status",
)

LIST_FIELDS = ("topics", "article_types", "special_notes", "source_urls")
URL_FIELDS = ("homepage_url", "guide_url")
STRING_FIELDS = tuple(
    field for field in REQUIRED_FIELDS if field not in LIST_FIELDS and field != "tier_order"
)
NONEMPTY_LIST_FIELDS = ("topics", "article_types", "source_urls")


def _is_https_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def validate_journals(records: list[dict[str, Any]]) -> None:
    """Validate journal records and raise ``ValueError`` on the first defect."""

    if not isinstance(records, list):
        raise ValueError("journal records must be a list")

    seen_ids: set[str] = set()
    seen_names: set[str] = set()

    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(f"record {index} must be a mapping")

        raw_id = record.get("id")
        journal_id = (
            raw_id.strip()
            if isinstance(raw_id, str) and raw_id.strip()
            else f"record-{index}"
        )
        for field in REQUIRED_FIELDS:
            if field not in record:
                raise ValueError(f"{journal_id}: missing required field {field}")

        for field in STRING_FIELDS:
            value = record[field]
            if not isinstance(value, str):
                raise ValueError(f"{journal_id}: {field} must be a string")
            if not value.strip():
                raise ValueError(f"{journal_id}: {field} must be a nonblank string")

        normalized_id = record["id"].strip().casefold()
        normalized_name = record["name"].strip().casefold()
        if normalized_id in seen_ids:
            raise ValueError(f"duplicate id: {record['id']}")
        if normalized_name in seen_names:
            raise ValueError(f"duplicate name: {record['name']}")
        seen_ids.add(normalized_id)
        seen_names.add(normalized_name)

        if not isinstance(record["tier_order"], int) or record["tier_order"] < 1:
            raise ValueError(f"{journal_id}: tier_order must be a positive integer")

        for field in LIST_FIELDS:
            if not isinstance(record[field], list):
                raise ValueError(f"{journal_id}: {field} must be a list")
            if any(not isinstance(item, str) or not item.strip() for item in record[field]):
                raise ValueError(f"{journal_id}: {field} must contain nonblank strings")
        for field in NONEMPTY_LIST_FIELDS:
            if not record[field]:
                raise ValueError(f"{journal_id}: {field} must contain at least one item")

        for field in URL_FIELDS:
            if not _is_https_url(record[field]):
                raise ValueError(f"{journal_id}: {field} must be an HTTPS URL")
        for source_url in record["source_urls"]:
            if not _is_https_url(source_url):
                raise ValueError(f"{journal_id}: source_urls must contain HTTPS URLs")

        try:
            date.fromisoformat(str(record["verified_on"]))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{journal_id}: verified_on must use YYYY-MM-DD") from exc


def freshness_notice(
    verified_on: str,
    *,
    today: date | None = None,
    stale_after_days: int = 180,
) -> str | None:
    """Return a warning when a record is older than the verification window."""

    verified_date = date.fromisoformat(verified_on)
    age_days = ((today or date.today()) - verified_date).days
    if age_days > stale_after_days:
        return f"已超过 {stale_after_days} 天未核验，请打开官方指南复核"
    return None


def load_journals(path: Path) -> list[dict[str, Any]]:
    """Load journal records from YAML, normalize list fields, and validate them."""

    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("YAML root must be a list")

    records: list[dict[str, Any]] = []
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ValueError(f"record {index} must be a mapping")
        record = dict(item)
        journal_id = record.get("id") or f"record-{index}"
        for field in REQUIRED_FIELDS:
            if field not in record:
                raise ValueError(f"{journal_id}: missing required field {field}")
        for field in LIST_FIELDS:
            value = record[field]
            if value is None:
                record[field] = []
            elif isinstance(value, str):
                record[field] = [value]
        records.append(record)

    validate_journals(records)
    return records
