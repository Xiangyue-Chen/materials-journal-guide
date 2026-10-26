"""Streamlit entry point for the metallic-materials journal guide."""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any

import streamlit as st

from journal_guide import (
    build_workbench,
    explain_requirement,
    filter_journals,
    freshness_notice,
    load_guidance,
    load_journals,
    select_for_comparison,
)


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "journals.yaml"
GUIDANCE_PATH = ROOT / "data" / "journal_guidance.yaml"

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

OFFICIAL_REQUIREMENT_FIELDS = (
    ("初投格式", "initial_submission"),
    ("摘要限制", "abstract_limit"),
    ("篇幅限制", "word_limit"),
    ("图文摘要", "graphical_abstract"),
    ("Highlights", "highlights"),
    ("参考文献", "references"),
    ("图片要求", "figures"),
    ("数据政策", "data_policy"),
    ("同行评审", "peer_review"),
)
EVIDENCE_FIELDS = {field for _, field in OFFICIAL_REQUIREMENT_FIELDS} | {"oa_model"}


@st.cache_data(show_spinner=False)
def get_journals() -> list[dict[str, Any]]:
    return load_journals(DATA_PATH)


@st.cache_data(show_spinner=False)
def get_guidance(journal_ids: tuple[str, ...]) -> dict[str, dict[str, Any]]:
    return load_guidance(GUIDANCE_PATH, set(journal_ids))


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


def _render_requirement(label: str, value: object) -> None:
    explained = explain_requirement(value)
    st.markdown(
        f'**{escape(label)}**　{escape(explained["summary"])} '
        f'<span class="evidence-badge">{escape(explained["status"])}</span>',
        unsafe_allow_html=True,
    )
    if explained["status"] != "官网明确":
        st.caption(explained["reason"])


def _oa_filter_label(value: str) -> str:
    explained = explain_requirement(value)
    if explained["status"] == "官网明确":
        return explained["summary"]
    return explained["status"]


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
        .guidance-banner {
          border-left: 4px solid var(--gold); background: rgba(255,255,255,.78);
          padding: 1rem 1.15rem; border-radius: 0 14px 14px 0; margin: .6rem 0 1.1rem;
        }
        .guidance-label, .official-label {
          display: inline-block; border-radius: 999px; padding: .2rem .58rem;
          font-size: .73rem; font-weight: 750; letter-spacing: .03em;
        }
        .guidance-label { background: #f6ead1; color: #76571f; }
        .official-label { background: var(--teal-soft); color: #174f49; }
        .evidence-badge {
          display: inline-block; margin-left: .35rem; border: 1px solid rgba(15,111,102,.22);
          border-radius: 999px; padding: .08rem .45rem; color: #174f49; font-size: .7rem;
          vertical-align: .08rem;
        }
        .structure-map {
          display: grid; grid-template-columns: repeat(auto-fit, minmax(175px, 1fr));
          gap: .7rem; margin: .6rem 0 1.2rem;
        }
        .structure-step {
          position: relative; background: rgba(255,255,255,.82); border: 1px solid rgba(23,35,33,.10);
          border-radius: 12px; padding: .9rem; min-height: 150px;
        }
        .step-number { color: var(--gold); font-weight: 800; font-size: .78rem; }
        .step-title { color: var(--ink); font-weight: 760; margin: .2rem 0 .45rem; }
        .step-task { color: var(--muted); font-size: .84rem; line-height: 1.55; }
        .storyboard-grid {
          display: grid; grid-template-columns: repeat(auto-fit, minmax(205px, 1fr));
          gap: .85rem; margin: .7rem 0 1.2rem;
        }
        .storyboard-card {
          overflow: hidden; background: #fff; border: 1px solid rgba(23,35,33,.12);
          border-radius: 14px; box-shadow: 0 10px 24px rgba(27,54,49,.06);
        }
        .storyboard-card svg { display: block; width: 100%; height: 126px; background: #eef3f0; }
        .storyboard-copy { padding: .75rem .85rem .9rem; }
        .storyboard-title { font-weight: 760; color: var(--ink); margin-bottom: .25rem; }
        .storyboard-question { color: var(--muted); font-size: .82rem; line-height: 1.5; }
        .signal-good, .signal-risk {
          border-radius: 12px; padding: .8rem 1rem; margin-bottom: .55rem; font-size: .88rem;
        }
        .signal-good { background: #e8f2ed; color: #174f49; }
        .signal-risk { background: #f7ece7; color: #7b3d2b; }
        @media (max-width: 700px) {
          .structure-map, .storyboard-grid { grid-template-columns: 1fr; }
          .structure-step { min-height: auto; }
        }
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
            "开放获取模式",
            _unique(records, "oa_model"),
            placeholder="全部模式",
            format_func=_oa_filter_label,
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
    oa = explain_requirement(record["oa_model"])
    c1.caption(f"OA：{oa['summary']} · {oa['status']}")
    c2.caption(f"核验：{record['verified_on']}")
    if notice := freshness_notice(str(record["verified_on"])):
        st.error(notice)
    st.markdown(
        f"[期刊主页]({record['homepage_url']}) · "
        f"[官方作者指南]({record['guide_url']})"
    )
    with st.expander("查看投稿要求"):
        st.markdown(f"**文章类型**　{_as_text(record['article_types'])}")
        for label, field in OFFICIAL_REQUIREMENT_FIELDS:
            _render_requirement(label, record[field])
        for note in record["special_notes"]:
            st.warning(str(note))
        st.markdown(
            f'<div class="source-note">记录状态：{escape(str(record["verification_status"]))}</div>',
            unsafe_allow_html=True,
        )


def _figure_svg(kind: str, index: int) -> str:
    """Return an original, decorative mini-figure for a storyboard card."""

    accent = ("#0f6f66", "#b58b3d", "#c66a4a", "#586f8c")[index % 4]
    common = f'<rect width="240" height="126" rx="14" fill="#eef3f0"/><text x="16" y="22" font-size="11" font-family="Arial" fill="#5d6b67">FIG. {index + 1}</text>'
    drawings = {
        "concept": f'{common}<rect x="22" y="43" width="54" height="42" rx="8" fill="#fff" stroke="{accent}"/><rect x="164" y="43" width="54" height="42" rx="8" fill="#fff" stroke="{accent}"/><path d="M82 64 H153" stroke="{accent}" stroke-width="3"/><path d="M145 57 L154 64 L145 71" fill="none" stroke="{accent}" stroke-width="3"/><circle cx="48" cy="64" r="11" fill="{accent}" opacity=".25"/><path d="M178 69 l10 -14 10 14" fill="none" stroke="{accent}" stroke-width="3"/>',
        "process": f'{common}<path d="M28 70 H212" stroke="#9eb3ad" stroke-width="4"/><circle cx="45" cy="70" r="13" fill="{accent}"/><circle cx="100" cy="70" r="13" fill="#fff" stroke="{accent}" stroke-width="3"/><circle cx="155" cy="70" r="13" fill="#fff" stroke="{accent}" stroke-width="3"/><circle cx="205" cy="70" r="13" fill="{accent}"/><path d="M88 40 h24 v14 H88z M143 86 h24 v14 h-24z" fill="{accent}" opacity=".28"/>',
        "microstructure": f'{common}<rect x="22" y="37" width="196" height="72" rx="8" fill="#dfe9e5"/><path d="M24 70 Q58 38 92 70 T160 70 T218 70 M24 91 Q58 58 92 91 T160 91 T218 91" fill="none" stroke="#7d9991" stroke-width="2"/><circle cx="60" cy="60" r="8" fill="{accent}"/><circle cx="132" cy="83" r="10" fill="{accent}" opacity=".7"/><circle cx="184" cy="55" r="6" fill="{accent}" opacity=".45"/><rect x="164" y="99" width="34" height="3" fill="#172321"/>',
        "performance": f'{common}<path d="M38 98 V36 M38 98 H216" stroke="#72827e" stroke-width="2"/><path d="M42 91 C72 86 83 68 108 65 S151 54 174 36 S202 42 212 29" fill="none" stroke="{accent}" stroke-width="4"/><path d="M42 94 C77 88 105 83 132 78 S180 72 210 70" fill="none" stroke="#98aaa5" stroke-width="3" stroke-dasharray="5 5"/><circle cx="174" cy="36" r="5" fill="{accent}"/>',
        "mechanism": f'{common}<rect x="25" y="43" width="190" height="18" rx="4" fill="#cbdcd7"/><rect x="25" y="73" width="190" height="18" rx="4" fill="#d9c69f"/><path d="M58 38 v62 M104 38 v62 M150 38 v62 M196 38 v62" stroke="{accent}" stroke-width="2" stroke-dasharray="4 3"/><path d="M75 29 l10 10 -10 10 M121 29 l10 10 -10 10 M167 29 l10 10 -10 10" fill="none" stroke="{accent}" stroke-width="3"/>',
        "validation": f'{common}<g transform="translate(38 38)"><rect width="164" height="68" rx="6" fill="#fff"/>' + "".join(
            f'<rect x="{c * 32 + 8}" y="{r * 20 + 6}" width="24" height="14" rx="3" fill="{accent}" opacity="{0.22 + 0.13 * ((r + c) % 4)}"/>'
            for r in range(3) for c in range(5)
        ) + '</g>',
        "summary": f'{common}<circle cx="120" cy="66" r="23" fill="{accent}" opacity=".22" stroke="{accent}" stroke-width="2"/><circle cx="48" cy="48" r="12" fill="#fff" stroke="{accent}"/><circle cx="192" cy="48" r="12" fill="#fff" stroke="{accent}"/><circle cx="48" cy="94" r="12" fill="#fff" stroke="{accent}"/><circle cx="192" cy="94" r="12" fill="#fff" stroke="{accent}"/><path d="M60 52 L96 62 M180 52 L144 62 M60 90 L96 72 M180 90 L144 72" stroke="{accent}" stroke-width="2"/>',
    }
    drawing = drawings.get(kind, drawings["summary"])
    return f'<svg viewBox="0 0 240 126" role="img" aria-label="原创图稿布局示意">{drawing}</svg>'


def _render_structure_map(structure: list[dict[str, str]]) -> None:
    cards = []
    for index, step in enumerate(structure, start=1):
        cards.append(
            '<div class="structure-step">'
            f'<div class="step-number">STEP {index:02d}</div>'
            f'<div class="step-title">{escape(step["title"])}</div>'
            f'<div class="step-task">{escape(step["task"])}</div>'
            '</div>'
        )
    st.markdown(
        f'<div class="structure-map">{"".join(cards)}</div>',
        unsafe_allow_html=True,
    )


def _render_storyboard(figures: list[dict[str, str]]) -> None:
    cards = []
    for index, figure in enumerate(figures):
        cards.append(
            '<div class="storyboard-card">'
            f'{_figure_svg(figure["kind"], index)}'
            '<div class="storyboard-copy">'
            f'<div class="storyboard-title">图 {index + 1} · {escape(figure["title"])}</div>'
            f'<div class="storyboard-question">{escape(figure["question"])}</div>'
            '</div></div>'
        )
    st.markdown(
        f'<div class="storyboard-grid">{"".join(cards)}</div>',
        unsafe_allow_html=True,
    )


def _official_requirement_rows(record: dict[str, Any]) -> list[dict[str, str]]:
    rows = []
    for label, field in OFFICIAL_REQUIREMENT_FIELDS:
        explained = explain_requirement(record[field])
        rows.append(
            {
                "项目": label,
                "证据状态": explained["status"],
                "当前要求": explained["summary"],
                "为什么这样标": explained["reason"],
            }
        )
    return rows


def render_deep_workbench(
    records: list[dict[str, Any]], guidance: dict[str, dict[str, Any]]
) -> None:
    st.subheader("深度投稿工作台")
    st.caption("先搭叙事和主图，再核格式。工作台默认面向原创研究论文。")
    names = [str(record["name"]) for record in records]
    selected_name = st.selectbox(
        "选择要准备的期刊",
        names,
        key="workbench_journal",
    )
    record = next(record for record in records if record["name"] == selected_name)
    workbench = build_workbench(record, guidance[str(record["id"])])

    st.markdown(
        '<div class="guidance-banner">'
        '<span class="guidance-label">本站写作建议</span> '
        f'<strong>{escape(workbench["profile_label"])}</strong><br>'
        f'{escape(workbench["editorial_angle"])}'
        '</div>',
        unsafe_allow_html=True,
    )
    good, risk = st.columns(2)
    with good:
        st.markdown("#### 更像适合这本期刊")
        for signal in workbench["fit_signals"]:
            st.markdown(
                f'<div class="signal-good">✓ {escape(signal)}</div>',
                unsafe_allow_html=True,
            )
    with risk:
        st.markdown("#### 容易被编辑认为不够")
        for signal in workbench["risk_signals"]:
            st.markdown(
                f'<div class="signal-risk">△ {escape(signal)}</div>',
                unsafe_allow_html=True,
            )

    st.subheader("文章结构地图")
    st.caption("本站写作建议 · 每一段只承担一个论证任务")
    _render_structure_map(workbench["structure"])

    st.subheader("主图蓝图")
    st.caption("本站原创示意，不是期刊模板或已发表论文图片；重点是每张图要回答的问题。")
    _render_storyboard(workbench["figure_story"])

    st.subheader("官方要求 · 逐项证据")
    st.markdown(
        '<span class="official-label">官方要求</span> '
        f'核验日期：{escape(str(record["verified_on"]))} · '
        f'<a href="{escape(str(record["guide_url"]))}">打开官方作者指南</a>',
        unsafe_allow_html=True,
    )
    if notice := freshness_notice(str(record["verified_on"])):
        st.error(notice)
    st.caption("证据状态：官网明确 / 按文章类型变化 / 官网未给统一值 / 非必交项 / 以投稿系统为准")
    st.table(_official_requirement_rows(record))

    st.subheader("投稿前清单")
    st.caption("本站写作建议 · 用于自查，不替代投稿系统中的实时问题")
    for item in workbench["checklist"]:
        st.markdown(f"- [ ] {item}")


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
            if field in EVIDENCE_FIELDS:
                explained = explain_requirement(record[field])
                value = f"{explained['summary']}【{explained['status']}】"
            else:
                value = _as_text(record[field])
            if field == "verified_on":
                if notice := freshness_notice(str(record["verified_on"])):
                    value = f"{value} · {notice}"
            row[str(record["name"])] = value
        comparison_rows.append(row)
    st.table(comparison_rows)
    st.caption("证据状态已区分官网明确、按文章类型变化、官网未给统一值和投稿系统动态项；对比后可打开对应官方指南定位原文。")


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
    guidance = get_guidance(tuple(str(record["id"]) for record in records))
    render_header(records)
    filters = render_sidebar(records)
    filtered = filter_journals(records, **filters)
    render_tier_guide(records)
    st.divider()
    render_deep_workbench(records, guidance)
    st.divider()
    render_catalogue(filtered)
    st.divider()
    render_comparison(records)
    render_footer()


if __name__ == "__main__":
    main()
