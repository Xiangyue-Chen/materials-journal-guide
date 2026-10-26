from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


APP_PATH = Path(__file__).parents[1] / "app.py"


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
    assert any("文章结构地图" in heading.value for heading in app.subheader)
    assert any("主图蓝图" in heading.value for heading in app.subheader)
    assert any("投稿前清单" in heading.value for heading in app.subheader)
    markdown = "\n".join(element.value for element in app.markdown)
    assert "本站写作建议" in markdown
    assert "官方要求" in markdown
    assert "storyboard-card" in markdown
    assert "<svg" in markdown


def test_workbench_explains_unknown_requirements_without_raw_placeholder() -> None:
    app = AppTest.from_file(str(APP_PATH)).run(timeout=20)
    workbench = next(
        widget for widget in app.selectbox if widget.key == "workbench_journal"
    )
    workbench.set_value("Science")
    app.run(timeout=20)

    assert not app.exception
    assert any(
        "官网未给统一值" in caption.value and "按文章类型变化" in caption.value
        for caption in app.caption
    )
    assert len(app.table[0].value) == 9
