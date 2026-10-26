from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from journal_guide import load_journals
from journal_guide.official_requirements import (
    build_official_workbench,
    load_official_requirements,
)


ROOT = Path(__file__).parents[1]
CATALOGUE_PATH = ROOT / "data" / "journals.yaml"
OFFICIAL_PATH = ROOT / "data" / "journal_official_requirements.yaml"


def _load() -> tuple[list[dict[str, object]], dict[str, dict[str, object]]]:
    records = load_journals(CATALOGUE_PATH)
    official = load_official_requirements(
        OFFICIAL_PATH, {str(record["id"]) for record in records}
    )
    return records, official


def _requirements_text(record: dict[str, object]) -> str:
    section_text = " ".join(
        str(item["requirement"]) for item in record["section_requirements"]
    )
    technical_text = " ".join(
        str(item["requirement"]) for item in record["technical_requirements"]
    )
    return f"{section_text} {technical_text}"


def test_official_catalogue_covers_every_journal_with_sourced_actionable_content() -> None:
    records, official = _load()

    assert set(official) == {str(record["id"]) for record in records}
    for record in records:
        item = official[str(record["id"])]
        assert len(item["section_requirements"]) >= 5
        assert len(item["technical_requirements"]) >= 1
        assert len(item["resources"]) >= 1
        assert "需投稿前复核" not in _requirements_text(item)
        for requirement in [
            *item["section_requirements"],
            *item["technical_requirements"],
        ]:
            assert requirement["scope"] in {
                "期刊专属",
                "出版社通用",
                "官网未公开稳定值",
            }
            assert str(requirement["source_url"]).startswith("https://")
        for resource in item["resources"]:
            assert resource["kind"] in {
                "官方指南",
                "官方模板",
                "官方示例",
                "已发表论文实例",
            }
            assert str(resource["url"]).startswith("https://")


def test_nature_has_exact_official_article_limits_and_annotated_example() -> None:
    _, official = _load()
    nature = official["nature"]
    text = _requirements_text(nature)

    assert "75 个字符" in text
    assert "不超过 200 词" in text
    assert "通常不超过 3000 词" in text
    assert "少于 300 词" in text
    assert any(
        resource["url"]
        == "https://www.nature.com/documents/nature-summary-paragraph.pdf"
        and resource["kind"] == "官方示例"
        for resource in nature["resources"]
    )


def test_nature_materials_has_article_structure_and_exact_limits() -> None:
    _, official = _load()
    nature_materials = official["nature-materials"]
    text = _requirements_text(nature_materials)

    for fragment in (
        "不超过 3000 词",
        "不超过 150 词",
        "最多 6 个展示项目",
        "最多 50 条参考文献",
        "Introduction 不设标题",
        "Discussion 不设小标题",
    ):
        assert fragment in text


def test_advanced_materials_has_exact_abstract_keyword_toc_and_figure_rules() -> None:
    _, official = _load()
    advanced_materials = official["advanced-materials"]
    text = _requirements_text(advanced_materials)

    for fragment in (
        "不超过 200 词",
        "3–7 个关键词",
        "50–60 词",
        "55 × 50 mm",
        "110 × 20 mm",
        "至少 300 dpi",
    ):
        assert fragment in text
    assert any(
        resource["kind"] == "官方模板"
        for resource in advanced_materials["resources"]
    )


def test_elsevier_journals_label_shared_rules_as_publisher_generic() -> None:
    _, official = _load()

    for journal_id in (
        "acta-materialia",
        "corrosion-science",
        "intermetallics",
        "journal-alloys-compounds",
        "materials-design",
        "materials-science-engineering-a",
        "scripta-materialia",
    ):
        item = official[journal_id]
        assert item["requirement_scope"] == "出版社通用"
        assert all(
            requirement["scope"] == "出版社通用"
            for requirement in [
                *item["section_requirements"],
                *item["technical_requirements"],
            ]
        )


def test_build_official_workbench_keeps_official_and_editorial_data_separate() -> None:
    records, official = _load()
    nature = next(record for record in records if record["id"] == "nature")
    guidance = {
        "profile_label": "跨学科概念突破",
        "editorial_angle": "本站角度",
        "fit_signals": ["a", "b", "c"],
        "risk_signals": ["d", "e", "f"],
        "structure": [{"title": "A", "task": "B"}],
        "checklist": ["x"],
    }

    workbench = build_official_workbench(nature, official["nature"], guidance)

    assert workbench["official"]["default_article_type"] == "Article"
    assert workbench["official"]["requirement_scope"] == "期刊专属"
    assert workbench["editorial"]["label"] == "本站写作建议"
    assert workbench["editorial"]["editorial_angle"] == "本站角度"


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("missing_journal", r"missing official requirements.*nature"),
        ("bad_source", r"nature.*source_url.*https"),
        ("placeholder", r"nature.*forbidden placeholder"),
        ("bad_kind", r"nature.*resource kind"),
    ],
)
def test_loader_rejects_incomplete_or_untraceable_data(
    tmp_path: Path, mutation: str, message: str
) -> None:
    data = yaml.safe_load(OFFICIAL_PATH.read_text(encoding="utf-8"))
    if mutation == "missing_journal":
        data["journals"].pop("nature")
    elif mutation == "bad_source":
        data["journals"]["nature"]["section_requirements"][0]["source_url"] = ""
    elif mutation == "placeholder":
        data["journals"]["nature"]["section_requirements"][0][
            "requirement"
        ] = "需投稿前复核"
    else:
        data["journals"]["nature"]["resources"][0]["kind"] = "博客"
    path = tmp_path / "official.yaml"
    path.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        load_official_requirements(path, set(data["journals"]) | {"nature"})
