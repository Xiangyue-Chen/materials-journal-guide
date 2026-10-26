from __future__ import annotations

from pathlib import Path
import re

import pytest
import yaml

from journal_guide import load_journals
from journal_guide.format_specs import ALLOWED_SCOPES, SPEC_KEYS, load_format_specs


ROOT = Path(__file__).parents[1]
CATALOGUE_PATH = ROOT / "data" / "journals.yaml"
FORMAT_SPECS_PATH = ROOT / "data" / "journal_format_specs.yaml"
FORBIDDEN_FILLER = ("需投稿前复核", "按指南执行", "具体见官网", "以官网为准")


def _load() -> tuple[list[dict[str, object]], dict[str, dict[str, object]]]:
    records = load_journals(CATALOGUE_PATH)
    specs = load_format_specs(
        FORMAT_SPECS_PATH, {str(record["id"]) for record in records}
    )
    return records, specs


def test_specs_cover_every_journal_with_six_actionable_fields() -> None:
    records, specs = _load()

    assert set(specs) == {str(record["id"]) for record in records}
    assert SPEC_KEYS == {
        "abstract",
        "manuscript_structure",
        "display_items",
        "panel_labels",
        "figure_legends",
        "references",
    }
    for journal_id, record in specs.items():
        assert set(record["quick_specs"]) == SPEC_KEYS
        assert len(record["blueprint"]) >= 5
        for key, item in record["quick_specs"].items():
            assert item["scope"] in ALLOWED_SCOPES
            assert str(item["source_url"]).startswith("https://")
            assert item["official"].strip()
            assert item["advice"].strip()
            combined = f'{item["official"]} {item["advice"]}'
            assert not any(token in combined for token in FORBIDDEN_FILLER), (
                journal_id,
                key,
                combined,
            )


def test_unknown_official_limits_still_have_a_concrete_site_recommendation() -> None:
    _, specs = _load()

    for journal_id, record in specs.items():
        for key, item in record["quick_specs"].items():
            if "官网未规定固定上限" not in item["official"]:
                continue
            assert item["scope"] == "官网未规定固定上限"
            assert re.search(r"\d|→|建议", item["advice"]), (journal_id, key)


def test_nature_quick_sheet_captures_exact_house_style() -> None:
    _, specs = _load()
    nature = specs["nature"]["quick_specs"]

    assert "不超过 200 词" in nature["abstract"]["official"]
    assert "4 个" in nature["display_items"]["official"]
    assert "5–6 个" in nature["display_items"]["official"]
    assert "小写粗体 a、b、c" in nature["panel_labels"]["official"]
    assert "8 pt" in nature["panel_labels"]["official"]
    assert "少于 300 词" in nature["figure_legends"]["official"]
    assert "上标编号" in nature["references"]["official"]
    assert "最多 50 条" in nature["references"]["official"]


def test_nature_family_research_formats_are_specific_not_generic() -> None:
    _, specs = _load()

    ncomms = specs["nature-communications"]["quick_specs"]
    assert "150 词" in ncomms["abstract"]["official"]
    assert "5000 词" in ncomms["manuscript_structure"]["official"]
    assert "10 个" in ncomms["display_items"]["official"]
    assert "小写 a、b、c" in ncomms["panel_labels"]["official"]
    assert "350 词" in ncomms["figure_legends"]["official"]
    assert "70 条" in ncomms["references"]["official"]

    nmat = specs["nature-materials"]["quick_specs"]
    assert "150 词" in nmat["abstract"]["official"]
    assert "3000 词" in nmat["manuscript_structure"]["official"]
    assert "最多 6 个" in nmat["display_items"]["official"]
    assert "Introduction 不设标题" in nmat["manuscript_structure"]["official"]
    assert "Discussion 不设小标题" in nmat["manuscript_structure"]["official"]

    commsmat = specs["communications-materials"]["quick_specs"]
    assert "150 词" in commsmat["abstract"]["official"]
    assert "最多 10 个" in commsmat["display_items"]["official"]
    assert "350 词" in commsmat["figure_legends"]["official"]
    assert "70 条" in commsmat["references"]["official"]


def test_advanced_materials_and_pnas_show_different_panel_and_reference_styles() -> None:
    _, specs = _load()
    advanced = specs["advanced-materials"]["quick_specs"]
    pnas = specs["pnas"]["quick_specs"]

    assert "小写 a、b、c" in advanced["panel_labels"]["official"]
    assert "12 pt" in advanced["panel_labels"]["official"]
    assert "左上角" in advanced["panel_labels"]["official"]
    assert "方括号" in advanced["references"]["official"]
    assert "[1]" in advanced["references"]["official"]
    assert "3–8 个" in advanced["display_items"]["official"]

    assert "不超过 250 词" in pnas["abstract"]["official"]
    assert "4 个中等大小" in pnas["display_items"]["official"]
    assert "大写 A、B、C" in pnas["panel_labels"]["official"]
    assert "圆括号编号" in pnas["references"]["official"]
    assert "(1)" in pnas["references"]["official"]


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("missing_journal", r"missing format specs.*nature"),
        ("missing_field", r"nature.*quick_specs.*references"),
        ("bad_source", r"nature.*source_url.*https"),
        ("bad_scope", r"nature.*unknown scope"),
        ("placeholder", r"nature.*forbidden placeholder"),
        ("weak_unknown", r"nature.*concrete advice"),
    ],
)
def test_loader_rejects_incomplete_or_vague_specs(
    tmp_path: Path, mutation: str, message: str
) -> None:
    data = yaml.safe_load(FORMAT_SPECS_PATH.read_text(encoding="utf-8"))
    if mutation == "missing_journal":
        data["journals"].pop("nature")
    elif mutation == "missing_field":
        data["journals"]["nature"]["quick_specs"].pop("references")
    elif mutation == "bad_source":
        data["journals"]["nature"]["quick_specs"]["abstract"]["source_url"] = ""
    elif mutation == "bad_scope":
        data["journals"]["nature"]["quick_specs"]["abstract"]["scope"] = "博客"
    elif mutation == "placeholder":
        data["journals"]["nature"]["quick_specs"]["abstract"]["official"] = (
            "需投稿前复核"
        )
    else:
        item = data["journals"]["nature"]["quick_specs"]["abstract"]
        item["official"] = "官网未规定固定上限"
        item["scope"] = "官网未规定固定上限"
        item["advice"] = "保持简洁"
    path = tmp_path / "format_specs.yaml"
    path.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        load_format_specs(path, set(data["journals"]) | {"nature"})

