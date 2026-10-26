from __future__ import annotations

from copy import deepcopy
from datetime import date
from pathlib import Path

import pytest
import yaml

from journal_guide.data import freshness_notice, load_journals, validate_journals


CATALOGUE_PATH = Path(__file__).parents[1] / "data" / "journals.yaml"
EXPECTED_JOURNAL_IDS = {
    "nature",
    "science",
    "nature-materials",
    "nature-communications",
    "science-advances",
    "communications-materials",
    "advanced-materials",
    "materials-today",
    "pnas",
    "acta-materialia",
    "scripta-materialia",
    "materials-science-engineering-a",
    "journal-materials-science-technology",
    "journal-alloys-compounds",
    "materials-design",
    "intermetallics",
    "corrosion-science",
}
EXPECTED_TIERS = {
    "正刊",
    "大子刊",
    "小子刊",
    "材料综合旗舰刊",
    "金属材料核心刊",
}


def valid_record(**overrides: object) -> dict[str, object]:
    record: dict[str, object] = {
        "id": "acta-materialia",
        "name": "Acta Materialia",
        "abbreviation": "Acta Mater.",
        "publisher": "Elsevier",
        "tier": "金属材料核心刊",
        "tier_order": 5,
        "topics": ["金属材料", "高熵合金", "力学性能"],
        "scope": "金属与材料科学的基础研究。",
        "article_types": ["Full Length Article"],
        "initial_submission": "单个 Word 或 PDF 文件可用于初投。",
        "abstract_limit": "需投稿前复核",
        "word_limit": "需投稿前复核",
        "graphical_abstract": "可选",
        "highlights": "需投稿前复核",
        "references": "初投格式可灵活，但须保持一致。",
        "figures": "初投图片须足以供同行评审。",
        "data_policy": "建议共享支撑研究结论的数据。",
        "oa_model": "Hybrid",
        "peer_review": "Single anonymized",
        "special_notes": ["具体限制随文章类型变化。"],
        "homepage_url": "https://www.sciencedirect.com/journal/acta-materialia",
        "guide_url": "https://www.sciencedirect.com/journal/acta-materialia/publish/guide-for-authors",
        "source_urls": [
            "https://www.sciencedirect.com/journal/acta-materialia/publish/guide-for-authors"
        ],
        "verified_on": "2026-10-26",
        "verification_status": "已核验",
    }
    record.update(overrides)
    return record


def test_validate_journals_accepts_complete_records() -> None:
    validate_journals([valid_record()])


def test_validate_journals_reports_missing_field_and_journal_id() -> None:
    record = valid_record()
    del record["name"]

    with pytest.raises(ValueError, match=r"acta-materialia.*name"):
        validate_journals([record])


@pytest.mark.parametrize("duplicate_field", ["id", "name"])
def test_validate_journals_rejects_duplicate_identity(duplicate_field: str) -> None:
    first = valid_record()
    second = deepcopy(first)
    second["id"] = "second-journal"
    second["name"] = "Second Journal"
    second[duplicate_field] = first[duplicate_field]

    with pytest.raises(ValueError, match=rf"duplicate {duplicate_field}"):
        validate_journals([first, second])


def test_validate_journals_rejects_non_https_official_links() -> None:
    record = valid_record(homepage_url="http://example.com/journal")

    with pytest.raises(ValueError, match=r"acta-materialia.*homepage_url.*HTTPS"):
        validate_journals([record])


def test_load_journals_requires_yaml_list_root(tmp_path: Path) -> None:
    path = tmp_path / "journals.yaml"
    path.write_text("journals: []\n", encoding="utf-8")

    with pytest.raises(ValueError, match="YAML root must be a list"):
        load_journals(path)


def test_load_journals_normalizes_list_fields(tmp_path: Path) -> None:
    record = valid_record(
        topics="高熵合金",
        article_types="Article",
        special_notes=None,
        source_urls="https://example.com/guide",
    )
    path = tmp_path / "journals.yaml"
    path.write_text(yaml.safe_dump([record], allow_unicode=True), encoding="utf-8")

    loaded = load_journals(path)

    assert loaded[0]["topics"] == ["高熵合金"]
    assert loaded[0]["article_types"] == ["Article"]
    assert loaded[0]["special_notes"] == []
    assert loaded[0]["source_urls"] == ["https://example.com/guide"]


@pytest.mark.parametrize(
    "missing_field", ["topics", "article_types", "special_notes", "source_urls"]
)
def test_load_journals_rejects_missing_required_list_fields(
    tmp_path: Path, missing_field: str
) -> None:
    record = valid_record()
    del record[missing_field]
    path = tmp_path / "journals.yaml"
    path.write_text(yaml.safe_dump([record], allow_unicode=True), encoding="utf-8")

    with pytest.raises(ValueError, match=rf"acta-materialia.*{missing_field}"):
        load_journals(path)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("name", "", r"acta-materialia.*name.*nonblank"),
        ("tier", {}, r"acta-materialia.*tier.*string"),
        ("topics", ["高熵合金", 7], r"acta-materialia.*topics.*strings"),
        ("source_urls", [], r"acta-materialia.*source_urls.*at least one"),
    ],
)
def test_validate_journals_rejects_malformed_values(
    field: str, value: object, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        validate_journals([valid_record(**{field: value})])


def test_freshness_notice_appears_only_after_180_days() -> None:
    assert freshness_notice("2026-01-01", today=date(2026, 6, 30)) is None
    assert freshness_notice("2026-01-01", today=date(2026, 7, 1)) == (
        "已超过 180 天未核验，请打开官方指南复核"
    )


def test_seed_catalogue_contains_expected_source_backed_journals() -> None:
    records = load_journals(CATALOGUE_PATH)

    assert len(records) == 17
    assert {record["id"] for record in records} == EXPECTED_JOURNAL_IDS
    assert {record["tier"] for record in records} == EXPECTED_TIERS
    assert all(record["source_urls"] for record in records)
    assert all(date.fromisoformat(record["verified_on"]) for record in records)


def test_seed_catalogue_is_ordered_by_tier_then_name() -> None:
    records = load_journals(CATALOGUE_PATH)

    keys = [(record["tier_order"], record["name"].casefold()) for record in records]
    assert keys == sorted(keys)
