from __future__ import annotations

import pytest

from journal_guide.filters import filter_journals, select_for_comparison


RECORDS = [
    {
        "id": "nature-materials",
        "name": "Nature Materials",
        "abbreviation": "Nat. Mater.",
        "publisher": "Springer Nature",
        "tier": "大子刊",
        "topics": ["材料科学", "高熵合金"],
        "scope": "具有广泛材料学意义的研究。",
        "oa_model": "Hybrid",
    },
    {
        "id": "advanced-materials",
        "name": "Advanced Materials",
        "abbreviation": "Adv. Mater.",
        "publisher": "Wiley",
        "tier": "材料综合旗舰刊",
        "topics": ["材料科学", "功能材料"],
        "scope": "跨学科材料研究。",
        "oa_model": "Hybrid",
    },
    {
        "id": "acta-materialia",
        "name": "Acta Materialia",
        "abbreviation": "Acta Mater.",
        "publisher": "Elsevier",
        "tier": "金属材料核心刊",
        "topics": ["金属材料", "高熵合金", "力学性能"],
        "scope": "结构—性能关系与机理。",
        "oa_model": "Hybrid",
    },
    {
        "id": "materials-design",
        "name": "Materials & Design",
        "abbreviation": "Mater. Des.",
        "publisher": "Elsevier",
        "tier": "金属材料核心刊",
        "topics": ["材料设计", "制造"],
        "scope": "设计、加工和工程性能。",
        "oa_model": "Gold Open Access",
    },
    {
        "id": "corrosion-science",
        "name": "Corrosion Science",
        "abbreviation": "Corros. Sci.",
        "publisher": "Elsevier",
        "tier": "金属材料核心刊",
        "topics": ["腐蚀", "金属材料"],
        "scope": "环境退化与腐蚀机理。",
        "oa_model": "Hybrid",
    },
]


def ids(records: list[dict[str, object]]) -> list[str]:
    return [str(record["id"]) for record in records]


def test_empty_filters_return_all_records_in_original_order() -> None:
    assert filter_journals(RECORDS) == RECORDS


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("ACTA", ["acta-materialia"]),
        ("nat. mater.", ["nature-materials"]),
        ("高熵合金", ["nature-materials", "acta-materialia"]),
        ("环境退化", ["corrosion-science"]),
    ],
)
def test_search_is_case_insensitive_and_multilingual(
    query: str, expected: list[str]
) -> None:
    assert ids(filter_journals(RECORDS, query=query)) == expected


def test_filters_use_or_within_field_and_and_across_fields() -> None:
    result = filter_journals(
        RECORDS,
        tiers=["大子刊", "金属材料核心刊"],
        publishers=["Elsevier"],
        topics=["高熵合金", "腐蚀"],
        oa_models=["Hybrid"],
    )

    assert ids(result) == ["acta-materialia", "corrosion-science"]


def test_comparison_preserves_catalogue_order_not_click_order() -> None:
    selected = select_for_comparison(
        RECORDS, ["materials-design", "nature-materials", "acta-materialia"]
    )

    assert ids(selected) == [
        "nature-materials",
        "acta-materialia",
        "materials-design",
    ]


def test_comparison_rejects_unknown_ids() -> None:
    with pytest.raises(ValueError, match=r"unknown journal id.*missing"):
        select_for_comparison(RECORDS, ["acta-materialia", "missing"])


def test_comparison_rejects_more_than_four_unique_journals() -> None:
    with pytest.raises(ValueError, match="at most 4"):
        select_for_comparison(RECORDS, ids(RECORDS))
