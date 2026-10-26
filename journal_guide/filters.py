"""Pure search and comparison-selection logic for journal records."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any
import unicodedata


def _normalize(value: object) -> str:
    return unicodedata.normalize("NFKC", str(value)).strip().casefold()


def _selected(values: Iterable[str] | None) -> set[str]:
    return {_normalize(value) for value in (values or []) if str(value).strip()}


def _record_search_text(record: dict[str, Any]) -> str:
    fields: list[object] = [
        record.get("name", ""),
        record.get("abbreviation", ""),
        record.get("publisher", ""),
        record.get("tier", ""),
        record.get("scope", ""),
    ]
    fields.extend(record.get("topics", []))
    return _normalize(" ".join(str(field) for field in fields))


def filter_journals(
    records: Sequence[dict[str, Any]],
    query: str = "",
    tiers: Iterable[str] | None = None,
    publishers: Iterable[str] | None = None,
    topics: Iterable[str] | None = None,
    oa_models: Iterable[str] | None = None,
) -> list[dict[str, Any]]:
    """Return journals matching all active filter groups in catalogue order."""

    query_text = _normalize(query)
    tier_set = _selected(tiers)
    publisher_set = _selected(publishers)
    topic_set = _selected(topics)
    oa_set = _selected(oa_models)

    matches: list[dict[str, Any]] = []
    for record in records:
        if query_text and query_text not in _record_search_text(record):
            continue
        if tier_set and _normalize(record.get("tier", "")) not in tier_set:
            continue
        if publisher_set and _normalize(record.get("publisher", "")) not in publisher_set:
            continue
        record_topics = {_normalize(topic) for topic in record.get("topics", [])}
        if topic_set and not record_topics.intersection(topic_set):
            continue
        if oa_set and _normalize(record.get("oa_model", "")) not in oa_set:
            continue
        matches.append(record)

    return matches


def select_for_comparison(
    records: Sequence[dict[str, Any]], ids: list[str]
) -> list[dict[str, Any]]:
    """Select up to four journals by ID while preserving catalogue order."""

    selected_ids = list(dict.fromkeys(ids))
    if len(selected_ids) > 4:
        raise ValueError("select at most 4 journals for comparison")

    known_ids = {str(record.get("id")) for record in records}
    unknown_ids = [journal_id for journal_id in selected_ids if journal_id not in known_ids]
    if unknown_ids:
        raise ValueError(f"unknown journal id: {', '.join(unknown_ids)}")

    selected_set = set(selected_ids)
    return [record for record in records if str(record.get("id")) in selected_set]
