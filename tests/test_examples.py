from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from journal_guide.data import load_journals
from journal_guide.examples import EXAMPLE_FIELDS, load_examples


ROOT = Path(__file__).parents[1]
EXAMPLES_PATH = ROOT / "data" / "journal_examples.yaml"
JOURNALS_PATH = ROOT / "data" / "journals.yaml"


def journal_ids() -> set[str]:
    return {str(item["id"]) for item in load_journals(JOURNALS_PATH)}


def test_every_journal_has_three_complete_unique_examples() -> None:
    examples = load_examples(EXAMPLES_PATH, journal_ids())

    assert set(examples) == journal_ids()
    assert sum(len(items) for items in examples.values()) == 51
    for items in examples.values():
        assert len(items) == 3
        assert len({str(item["url"]) for item in items}) == 3
        for item in items:
            assert set(item) == EXAMPLE_FIELDS
            assert 1900 <= item["year"] <= 2026
            assert str(item["url"]).startswith("https://")
            for field in EXAMPLE_FIELDS - {"year"}:
                assert str(item[field]).strip()


def test_representative_examples_are_real_topic_aligned_papers() -> None:
    examples = load_examples(EXAMPLES_PATH, journal_ids())

    assert examples["nature"][0]["url"] == "https://doi.org/10.1038/nature17981"
    assert "strength–ductility trade-off" in examples["nature"][0]["title"]
    assert examples["science"][0]["url"] == "https://doi.org/10.1126/science.1254581"
    assert examples["acta-materialia"][0]["url"] == (
        "https://doi.org/10.1016/j.actamat.2015.08.076"
    )
    assert examples["scripta-materialia"][1]["url"] == (
        "https://doi.org/10.1016/j.scriptamat.2016.06.046"
    )
    assert examples["journal-alloys-compounds"][0]["url"] == (
        "https://doi.org/10.1016/j.jallcom.2014.11.061"
    )


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("missing_journal", r"missing examples.*nature"),
        ("extra_journal", r"unknown journal IDs.*extra"),
        ("wrong_count", r"nature.*exactly 3"),
        ("missing_field", r"nature.*examples\[0\].*look_at"),
        ("bad_year", r"nature.*examples\[0\].*year"),
        ("bad_url", r"nature.*examples\[0\].*https"),
        ("duplicate_url", r"nature.*duplicate.*url"),
        ("blank_copy", r"nature.*examples\[0\].*why_recommended.*nonblank"),
    ],
)
def test_loader_rejects_incomplete_or_untrustworthy_examples(
    tmp_path: Path, mutation: str, message: str
) -> None:
    data = yaml.safe_load(EXAMPLES_PATH.read_text(encoding="utf-8"))
    nature = data["journals"]["nature"]
    if mutation == "missing_journal":
        data["journals"].pop("nature")
    elif mutation == "extra_journal":
        data["journals"]["extra"] = nature
    elif mutation == "wrong_count":
        nature.pop()
    elif mutation == "missing_field":
        nature[0].pop("look_at")
    elif mutation == "bad_year":
        nature[0]["year"] = 9999
    elif mutation == "bad_url":
        nature[0]["url"] = "http://example.com/paper"
    elif mutation == "duplicate_url":
        nature[1]["url"] = nature[0]["url"]
    else:
        nature[0]["why_recommended"] = " "

    path = tmp_path / "examples.yaml"
    path.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        load_examples(path, journal_ids())
