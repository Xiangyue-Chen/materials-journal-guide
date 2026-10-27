"""Validated published-paper examples for every journal."""

from __future__ import annotations

from copy import deepcopy
from datetime import date
from pathlib import Path

import yaml


EXAMPLE_FIELDS = {
    "title",
    "year",
    "article_type",
    "topic",
    "why_recommended",
    "look_at",
    "url",
}


def _nonblank(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _validate_examples(journal_id: str, records: object) -> None:
    if not isinstance(records, list) or len(records) != 3:
        raise ValueError(f"{journal_id}: examples must contain exactly 3 records")

    seen_urls: set[str] = set()
    for index, record in enumerate(records):
        prefix = f"{journal_id}: examples[{index}]"
        if not isinstance(record, dict) or set(record) != EXAMPLE_FIELDS:
            missing = sorted(EXAMPLE_FIELDS - set(record or {}))
            detail = f"; missing {', '.join(missing)}" if missing else ""
            raise ValueError(
                f"{prefix} must contain exactly {', '.join(sorted(EXAMPLE_FIELDS))}"
                f"{detail}"
            )
        year = record["year"]
        if not isinstance(year, int) or not 1900 <= year <= date.today().year:
            raise ValueError(f"{prefix}.year must be between 1900 and current year")
        for field in EXAMPLE_FIELDS - {"year", "url"}:
            if not _nonblank(record[field]):
                raise ValueError(f"{prefix}.{field} must be nonblank")
        url = record["url"]
        if not _nonblank(url) or not str(url).startswith("https://"):
            raise ValueError(f"{prefix}.url must be an https URL")
        if str(url) in seen_urls:
            raise ValueError(f"{journal_id}: duplicate example url {url}")
        seen_urls.add(str(url))


def load_examples(
    path: Path, journal_ids: set[str]
) -> dict[str, list[dict[str, object]]]:
    """Load and strictly validate three published examples per journal."""

    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or set(raw) != {"journals"}:
        raise ValueError("examples root must contain only journals")
    journals = raw["journals"]
    if not isinstance(journals, dict):
        raise ValueError("examples journals must be a mapping")

    configured = set(journals)
    missing = sorted(journal_ids - configured)
    extra = sorted(configured - journal_ids)
    if missing:
        raise ValueError(f"missing examples for journal IDs: {', '.join(missing)}")
    if extra:
        raise ValueError(f"examples contain unknown journal IDs: {', '.join(extra)}")

    validated: dict[str, list[dict[str, object]]] = {}
    for journal_id, records in journals.items():
        _validate_examples(str(journal_id), records)
        validated[str(journal_id)] = deepcopy(records)
    return validated
