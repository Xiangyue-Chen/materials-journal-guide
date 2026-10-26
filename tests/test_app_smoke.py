from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

from journal_guide import load_guidance, load_journals, load_official_requirements


APP_PATH = Path(__file__).parents[1] / "app.py"


def visible_text(app: AppTest) -> str:
    groups = (app.markdown, app.caption, app.info, app.warning, app.error)
    return "\n".join(element.value for group in groups for element in group)


def table_text(app: AppTest) -> str:
    return "\n".join(
        str(value)
        for table in app.table
        for value in table.value.to_numpy().flatten()
    )


def test_app_starts_with_catalogue_filters_and_evidence_notice() -> None:
    app = AppTest.from_file(str(APP_PATH)).run(timeout=20)

    assert not app.exception
    assert app.title[0].value == "金属材料期刊导航"
    assert app.metric[0].value == "17"
    assert len(app.text_input) == 1
    assert len(app.multiselect) >= 5
    assert any("官方作者指南" in notice.value for notice in app.info)


def test_app_can_render_a_two_journal_comparison() -> None:
    app = AppTest.from_file(str(APP_PATH)).run(timeout=20)

    comparison = next(
        widget for widget in app.multiselect if widget.key == "comparison_ids"
    )
    comparison.select("Nature Materials").select("Acta Materialia")
    app.run(timeout=20)

    assert not app.exception
    assert any("期刊对比" in heading.value for heading in app.subheader)
    assert any("比较项目" in str(table.value) for table in app.table)


def test_app_renders_actionable_deep_submission_workbench() -> None:
    app = AppTest.from_file(str(APP_PATH)).run(timeout=20)

    workbench = next(
        widget for widget in app.selectbox if widget.key == "workbench_journal"
    )
    workbench.set_value("Nature Materials")
    app.run(timeout=20)

    assert not app.exception
    assert any("深度投稿工作台" in heading.value for heading in app.subheader)
    assert any("官方要求总览" in heading.value for heading in app.subheader)
    assert any("稿件各部分格式" in heading.value for heading in app.subheader)
    assert any("提交文件与技术规格" in heading.value for heading in app.subheader)
    assert any("官方模板与实例" in heading.value for heading in app.subheader)
    markdown = "\n".join(element.value for element in app.markdown)
    assert "本站写作建议" in markdown
    assert "官方要求" in markdown
    assert "storyboard-card" not in markdown
    assert "<svg" not in markdown
    assert "主图蓝图" not in visible_text(app)
    tables = table_text(app)
    assert "Introduction 不设标题" in tables
    assert "Discussion 不设小标题" in tables
    assert "最多 6 个展示项目" in tables


def test_workbench_explains_unknown_requirements_without_raw_placeholder() -> None:
    app = AppTest.from_file(str(APP_PATH)).run(timeout=20)
    workbench = next(
        widget for widget in app.selectbox if widget.key == "workbench_journal"
    )
    workbench.set_value("Science")
    app.run(timeout=20)

    assert not app.exception
    tables = table_text(app)
    assert "官网未公开稳定值" in tables
    assert "官方初投稿页面" in tables
    assert "需投稿前复核" not in tables


def test_advanced_materials_workbench_links_official_templates() -> None:
    app = AppTest.from_file(str(APP_PATH)).run(timeout=20)
    workbench = next(
        widget for widget in app.selectbox if widget.key == "workbench_journal"
    )
    workbench.set_value("Advanced Materials")
    app.run(timeout=20)

    assert not app.exception
    markdown = "\n".join(element.value for element in app.markdown)
    assert "Advanced Materials Word 模板" in markdown
    assert "Advanced Materials LaTeX 模板" in markdown
    assert "官方模板" in markdown


def test_default_view_never_exposes_raw_review_placeholder() -> None:
    app = AppTest.from_file(str(APP_PATH)).run(timeout=20)

    assert not app.exception
    assert "需投稿前复核" not in visible_text(app)


def test_comparison_uses_explanatory_evidence_states() -> None:
    app = AppTest.from_file(str(APP_PATH)).run(timeout=20)
    comparison = next(
        widget for widget in app.multiselect if widget.key == "comparison_ids"
    )
    comparison.select("Science").select("Nature Materials")
    app.run(timeout=20)

    assert not app.exception
    text = visible_text(app)
    assert "需投稿前复核" not in text
    assert "证据状态" in text


def test_oa_filter_never_exposes_raw_review_placeholder() -> None:
    app = AppTest.from_file(str(APP_PATH)).run(timeout=20)
    oa_filter = next(
        widget for widget in app.multiselect if widget.label == "开放获取模式"
    )

    assert "需投稿前复核" not in oa_filter.options
    assert "官网未给统一值" in oa_filter.options


def test_workbench_warns_when_official_requirements_are_stale(tmp_path: Path) -> None:
    records = load_journals(APP_PATH.parent / "data" / "journals.yaml")
    record = dict(next(item for item in records if item["id"] == "nature"))
    record["verified_on"] = "2020-01-01"
    guidance = load_guidance(
        APP_PATH.parent / "data" / "journal_guidance.yaml", {item["id"] for item in records}
    )
    official = load_official_requirements(
        APP_PATH.parent / "data" / "journal_official_requirements.yaml",
        {item["id"] for item in records},
    )
    stale_official = dict(official["nature"])
    stale_official["verified_on"] = "2020-01-01"
    script = tmp_path / "stale_workbench.py"
    script.write_text(
        "from app import render_deep_workbench\n"
        f"render_deep_workbench({[record]!r}, {{'nature': {guidance['nature']!r}}}, "
        f"{{'nature': {stale_official!r}}})\n",
        encoding="utf-8",
    )

    app = AppTest.from_file(str(script)).run(timeout=20)

    assert not app.exception
    assert any("超过 180 天未核验" in warning.value for warning in app.error)
