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
    assert len(app.table) == 1
