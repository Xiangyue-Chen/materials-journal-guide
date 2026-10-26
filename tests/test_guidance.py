from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from journal_guide.data import load_journals
from journal_guide.guidance import (
    build_workbench,
    explain_requirement,
    load_guidance,
)


ROOT = Path(__file__).parents[1]
CATALOGUE_PATH = ROOT / "data" / "journals.yaml"
GUIDANCE_PATH = ROOT / "data" / "journal_guidance.yaml"


def test_guidance_covers_every_catalogue_journal_with_actionable_content() -> None:
    records = load_journals(CATALOGUE_PATH)
    guidance = load_guidance(GUIDANCE_PATH, {record["id"] for record in records})

    assert set(guidance) == {record["id"] for record in records}
    for record in records:
        workbench = build_workbench(record, guidance[record["id"]])
        assert len(workbench["structure"]) >= 5
        assert len(workbench["figure_story"]) >= 5
        assert len(workbench["fit_signals"]) >= 3
        assert len(workbench["risk_signals"]) >= 3
        assert len(workbench["checklist"]) >= 5
        assert workbench["editorial_angle"].strip()


def test_load_guidance_rejects_missing_journal_coverage(tmp_path: Path) -> None:
    data = yaml.safe_load(GUIDANCE_PATH.read_text(encoding="utf-8"))
    data["journals"].pop("nature")
    path = tmp_path / "guidance.yaml"
    path.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")

    with pytest.raises(ValueError, match=r"missing guidance.*nature"):
        load_guidance(path, {"nature", "acta-materialia"})


def test_load_guidance_reports_unknown_profile_with_journal_id(tmp_path: Path) -> None:
    data = yaml.safe_load(GUIDANCE_PATH.read_text(encoding="utf-8"))
    data["journals"]["nature"]["profile"] = "not-a-profile"
    path = tmp_path / "guidance.yaml"
    path.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")

    with pytest.raises(ValueError, match=r"nature.*unknown profile.*not-a-profile"):
        load_guidance(path, set(data["journals"]))


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("structure", [], r"nature.*structure.*at least 5"),
        ("figure_story", None, r"nature.*figure_story.*at least 5"),
        ("checklist", [""], r"nature.*checklist.*at least 5"),
    ],
)
def test_load_guidance_validates_merged_journal_overrides(
    tmp_path: Path, field: str, value: object, message: str
) -> None:
    data = yaml.safe_load(GUIDANCE_PATH.read_text(encoding="utf-8"))
    data["journals"]["nature"][field] = value
    path = tmp_path / "guidance.yaml"
    path.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        load_guidance(path, set(data["journals"]))


def test_load_guidance_rejects_unknown_storyboard_kind(tmp_path: Path) -> None:
    data = yaml.safe_load(GUIDANCE_PATH.read_text(encoding="utf-8"))
    data["profiles"]["cross-disciplinary"]["figure_story"][0]["kind"] = "typo"
    path = tmp_path / "guidance.yaml"
    path.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")

    with pytest.raises(ValueError, match=r"cross-disciplinary.*unknown figure kind.*typo"):
        load_guidance(path, set(data["journals"]))


@pytest.mark.parametrize(
    ("raw", "status", "summary_fragment", "reason_fragment"),
    [
        ("需投稿前复核", "官网未给统一值", "未找到稳定统一值", "公开指南"),
        (
            "随稿件类型变化，需投稿前复核",
            "按文章类型变化",
            "随稿件类型变化",
            "Article、Review、Letter",
        ),
        (
            "未列为 Article 常规必交项",
            "非必交项",
            "未列为 Article 常规必交项",
            "不是常规必交材料",
        ),
        ("Abstract 不超过 250 词", "官网明确", "Abstract 不超过 250 词", "已记录明确要求"),
        (
            "具体等效页数或字数需按最新作者指南复核",
            "官网未给统一值",
            "具体等效页数或字数",
            "公开指南",
        ),
        (
            "采用 Science 编号制，具体上限和格式随稿件类型变化。",
            "按文章类型变化",
            "采用 Science 编号制",
            "Article、Review、Letter",
        ),
    ],
)
def test_explain_requirement_replaces_placeholder_with_specific_evidence(
    raw: str, status: str, summary_fragment: str, reason_fragment: str
) -> None:
    explained = explain_requirement(raw)

    assert explained["status"] == status
    assert summary_fragment in explained["summary"]
    assert reason_fragment in explained["reason"]
    assert "需投稿前复核" not in " ".join(explained.values())


def test_build_workbench_keeps_official_and_guidance_boundaries_separate() -> None:
    records = load_journals(CATALOGUE_PATH)
    guidance = load_guidance(GUIDANCE_PATH, {record["id"] for record in records})
    nature = next(record for record in records if record["id"] == "nature")

    workbench = build_workbench(nature, guidance["nature"])

    assert workbench["journal_name"] == "Nature"
    assert workbench["guidance_label"] == "本站写作建议"
    assert workbench["official_label"] == "官方要求"
    assert workbench["guide_url"] == nature["guide_url"]
    assert workbench["editorial_angle"].startswith("把材料现象写成")
