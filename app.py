"""Streamlit entry point for the metallic-materials journal guide."""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any

import streamlit as st

from journal_guide import filter_journals, load_journals, select_for_comparison


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "journals.yaml"

TIER_DESCRIPTIONS = {
    "正刊": "跨学科影响与普适意义",
    "大子刊": "领域级重要推进",
    "小子刊": "专业方向显著推进",
    "材料综合旗舰刊": "材料领域广泛影响",
    "金属材料核心刊": "机制、组织与性能深度",
}

COMPARISON_FIELDS = (
    ("投稿梯队", "tier"),
    ("出版社", "publisher"),
    ("研究定位", "scope"),
    ("文章类型", "article_types"),
    ("初投格式", "initial_submission"),
    ("摘要限制", "abstract_limit"),
    ("篇幅限制", "word_limit"),
    ("图文摘要", "graphical_abstract"),
    ("Highlights", "highlights"),
    ("参考文献", "references"),
    ("开放获取", "oa_model"),
    ("同行评审", "peer_review"),
    ("数据政策", "data_policy"),
    ("核验状态", "verification_status"),
    ("核验日期", "verified_on"),
)


@st.cache_data(show_spinner=False)
def get_journals() -> list[dict[str, Any]]:
    return load_journals(DATA_PATH)


def _unique(records: list[dict[str, Any]], field: str) -> list[str]:
    values: set[str] = set()
    for record in records:
        value = record.get(field, "")
        if isinstance(value, list):
            values.update(str(item) for item in value)
        elif value:
            values.add(str(value))
    return sorted(values, key=str.casefold)


def _as_text(value: object) -> str:
    if isinstance(value, list):
        return "；".join(str(item) for item in value)
    return str(value)


def render_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
          --ink: #172321;
          --muted: #5d6b67;
          --teal: #0f6f66;
          --teal-soft: #e4f0ed;
          --gold: #b58b3d;
          --paper: #fbfaf6;
        }
        .stApp {
          background:
            radial-gradient(circle at 90% 2%, rgba(15,111,102,.08), transparent 28rem),
            linear-gradient(180deg, #fdfcf8 0%, #f7f5ef 100%);
          color: var(--ink);
        }
        .block-container { max-width: 1240px; padding-top: 2.2rem; }
        h1, h2, h3 { letter-spacing: -.025em; color: var(--ink); }
        [data-testid="stMetric"] {
          background: rgba(255,255,255,.78);
          border: 1px solid rgba(23,35,33,.10);
          border-radius: 14px;
          padding: .75rem 1rem;
          box-shadow: 0 8px 28px rgba(27,54,49,.05);
        }
        [data-testid="stVerticalBlockBorderWrapper"] {
          background: rgba(255,255,255,.78);
          border-color: rgba(23,35,33,.12) !important;
          box-shadow: 0 12px 32px rgba(27,54,49,.05);
        }
        .journal-kicker {
          color: var(--teal); font-size: .78rem; font-weight: 750;
          letter-spacing: .08em; text-transform: uppercase;
        }
        .journal-name { margin: .22rem 0 .35rem; font-size: 1.28rem; font-weight: 760; }
        .journal-scope { color: var(--muted); min-height: 4.7rem; line-height: 1.65; }
        .tag {
          display: inline-block; margin: .14rem .22rem .14rem 0; padding: .2rem .5rem;
          border-radius: 999px; background: var(--teal-soft); color: #174f49; font-size: .75rem;
        }
        .source-note { color: var(--muted); font-size: .82rem; }
        .hero-rule { width: 72px; height: 3px; background: var(--gold); margin: .9rem 0 1.1rem; }
        a { color: var(--teal) !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(records: list[dict[str, Any]]) -> None:
    st.caption("METALLIC MATERIALS · JOURNAL INTELLIGENCE")
    st.title("金属材料期刊导航")
    st.markdown('<div class="hero-rule"></div>', unsafe_allow_html=True)
    st.write(
        "从综合正刊到金属材料核心刊，集中查询投稿格式、文章类型、图表要求与数据政策。"
        "首版聚焦高熵合金、结构材料、力学性能和腐蚀研究。"
    )

    metrics = st.columns(4)
    metrics[0].metric("已收录期刊", str(len(records)))
    metrics[1].metric("投稿梯队", str(len({r['tier'] for r in records})))
    metrics[2].metric("出版社", str(len({r['publisher'] for r in records})))
    metrics[3].metric("最近核验", max(str(r["verified_on"]) for r in records))

    st.info(
        "页面摘要仅整理官方作者指南与出版社页面；投稿要求会更新，正式提交前请点击“官方作者指南”再次核对。"
    )


def render_sidebar(records: list[dict[str, Any]]) -> dict[str, object]:
    with st.sidebar:
        st.header("筛选期刊")
        query = st.text_input(
            "关键词",
            placeholder="期刊名、高熵合金、腐蚀、力学性能…",
        )
        tiers = st.multiselect(
            "投稿梯队", _unique(records, "tier"), placeholder="全部梯队"
        )
        publishers = st.multiselect(
            "出版社", _unique(records, "publisher"), placeholder="全部出版社"
        )
        topics = st.multiselect(
            "研究方向", _unique(records, "topics"), placeholder="全部方向"
        )
        oa_models = st.multiselect(
            "开放获取模式", _unique(records, "oa_model"), placeholder="全部模式"
        )
        st.divider()
        st.caption("多个筛选类别之间取交集；同一类别内取并集。")
    return {
        "query": query,
        "tiers": tiers,
        "publishers": publishers,
        "topics": topics,
        "oa_models": oa_models,
    }


def render_tier_guide(records: list[dict[str, Any]]) -> None:
    st.subheader("投稿梯队")
    tiers = sorted(
        {(int(record["tier_order"]), str(record["tier"])) for record in records}
    )
    columns = st.columns(len(tiers))
    for column, (_, tier) in zip(columns, tiers, strict=True):
        count = sum(record["tier"] == tier for record in records)
        with column:
            st.markdown(f"**{tier}**")
            st.caption(f"{TIER_DESCRIPTIONS.get(tier, '')} · {count} 本")
    st.caption("梯队为本站检索导航，不是官方排名，也不等同于影响因子或中科院分区。")


def render_journal_card(record: dict[str, Any]) -> None:
    topics = "".join(
        f'<span class="tag">{escape(str(topic))}</span>' for topic in record["topics"]
    )
    st.markdown(
        f"""
        <div class="journal-kicker">{escape(str(record['tier']))} · {escape(str(record['publisher']))}</div>
        <div class="journal-name">{escape(str(record['name']))} <small>· {escape(str(record['abbreviation']))}</small></div>
        <div class="journal-scope">{escape(str(record['scope']))}</div>
        <div>{topics}</div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2)
    c1.caption(f"OA：{record['oa_model']}")
    c2.caption(f"核验：{record['verified_on']}")
    st.markdown(
        f"[期刊主页]({record['homepage_url']}) · "
        f"[官方作者指南]({record['guide_url']})"
    )
    with st.expander("查看投稿要求"):
        st.markdown(f"**文章类型**　{_as_text(record['article_types'])}")
        st.markdown(f"**初投格式**　{record['initial_submission']}")
        st.markdown(f"**摘要限制**　{record['abstract_limit']}")
        st.markdown(f"**篇幅限制**　{record['word_limit']}")
        st.markdown(f"**图文摘要**　{record['graphical_abstract']}")
        st.markdown(f"**Highlights**　{record['highlights']}")
        st.markdown(f"**参考文献**　{record['references']}")
        st.markdown(f"**图片要求**　{record['figures']}")
        st.markdown(f"**数据政策**　{record['data_policy']}")
        st.markdown(f"**同行评审**　{record['peer_review']}")
        for note in record["special_notes"]:
            st.warning(str(note))
        st.markdown(
            f'<div class="source-note">记录状态：{escape(str(record["verification_status"]))}</div>',
            unsafe_allow_html=True,
        )


def render_catalogue(records: list[dict[str, Any]]) -> None:
    st.subheader(f"期刊列表 · {len(records)} 本")
    if not records:
        st.warning("没有匹配结果，请减少筛选条件或更换关键词。")
        return

    columns = st.columns(2)
    for index, record in enumerate(records):
        with columns[index % 2]:
            with st.container(border=True):
                render_journal_card(record)


def render_comparison(records: list[dict[str, Any]]) -> None:
    st.subheader("期刊对比")
    name_to_id = {str(record["name"]): str(record["id"]) for record in records}
    selected_names = st.multiselect(
        "选择 2–4 本期刊",
        options=list(name_to_id),
        max_selections=4,
        key="comparison_ids",
        placeholder="输入期刊名或展开选择",
    )
    if len(selected_names) < 2:
        st.caption("选择至少 2 本期刊后，将按投稿要求逐项横向比较。")
        return

    selected_ids = [name_to_id[name] for name in selected_names]
    selected = select_for_comparison(records, selected_ids)
    comparison_rows: list[dict[str, str]] = []
    for label, field in COMPARISON_FIELDS:
        row = {"比较项目": label}
        for record in selected:
            row[str(record["name"])] = _as_text(record[field])
        comparison_rows.append(row)
    st.table(comparison_rows)
    st.caption("对比表用于准备初稿；遇到“需投稿前复核”或文章类型差异时，请打开对应官方指南。")


def render_footer() -> None:
    st.divider()
    st.markdown("#### 数据边界")
    st.caption(
        "不把投稿梯队当作官方排名；不固定展示易过时的影响因子、分区、APC 或非官方审稿时长。"
        "当前信息以原创研究论文为主，不同文章类型可能有独立限制。"
    )


def main() -> None:
    st.set_page_config(
        page_title="金属材料期刊导航",
        page_icon="◫",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    render_styles()
    records = get_journals()
    render_header(records)
    filters = render_sidebar(records)
    filtered = filter_journals(records, **filters)
    render_tier_guide(records)
    st.divider()
    render_catalogue(filtered)
    st.divider()
    render_comparison(records)
    render_footer()


if __name__ == "__main__":
    main()
