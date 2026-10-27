"""Streamlit entry point for the metallic-materials journal guide."""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any

import streamlit as st

from journal_guide import (
    build_official_workbench,
    explain_requirement,
    filter_journals,
    freshness_notice,
    load_guidance,
    load_journals,
    load_official_requirements,
    select_for_comparison,
)
from journal_guide.format_specs import load_format_specs
from journal_guide.examples import load_examples
from journal_guide.local_papers import load_local_papers


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "journals.yaml"
GUIDANCE_PATH = ROOT / "data" / "journal_guidance.yaml"
OFFICIAL_REQUIREMENTS_PATH = ROOT / "data" / "journal_official_requirements.yaml"
FORMAT_SPECS_PATH = ROOT / "data" / "journal_format_specs.yaml"
EXAMPLES_PATH = ROOT / "data" / "journal_examples.yaml"
LOCAL_PAPERS_PATH = ROOT / "data" / "local_papers.yaml"

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
FORMAT_SPEC_FIELDS = (
    ("摘要", "abstract"),
    ("正文骨架", "manuscript_structure"),
    ("图表数量", "display_items"),
    ("分图标注", "panel_labels"),
    ("图注", "figure_legends"),
    ("参考文献", "references"),
)


@st.cache_data(show_spinner=False)
def get_journals() -> list[dict[str, Any]]:
    return load_journals(DATA_PATH)


@st.cache_data(show_spinner=False)
def get_guidance(journal_ids: tuple[str, ...]) -> dict[str, dict[str, Any]]:
    return load_guidance(GUIDANCE_PATH, set(journal_ids))


@st.cache_data(show_spinner=False)
def get_official_requirements(
    journal_ids: tuple[str, ...],
) -> dict[str, dict[str, Any]]:
    return load_official_requirements(OFFICIAL_REQUIREMENTS_PATH, set(journal_ids))


@st.cache_data(show_spinner=False)
def get_format_specs(
    journal_ids: tuple[str, ...],
) -> dict[str, dict[str, Any]]:
    return load_format_specs(FORMAT_SPECS_PATH, set(journal_ids))


@st.cache_data(show_spinner=False)
def get_examples(
    journal_ids: tuple[str, ...],
) -> dict[str, list[dict[str, object]]]:
    return load_examples(EXAMPLES_PATH, set(journal_ids))


@st.cache_data(show_spinner=False)
def get_local_papers(
    journal_ids: tuple[str, ...],
) -> dict[str, dict[str, object]]:
    examples = load_examples(EXAMPLES_PATH, set(journal_ids))
    return load_local_papers(LOCAL_PAPERS_PATH, ROOT, examples)


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
        .signal-good, .signal-risk {
          border-radius: 12px; padding: .8rem 1rem; margin-bottom: .55rem; font-size: .88rem;
        }
        .signal-good { background: #e8f2ed; color: #174f49; }
        .signal-risk { background: #f7ece7; color: #7b3d2b; }
        .format-card-title {
          color: var(--teal); font-size: .84rem; font-weight: 800;
          letter-spacing: .05em; margin-bottom: .55rem;
        }
        .format-card-copy { color: var(--ink); line-height: 1.65; margin: .35rem 0 .72rem; }
        .format-card-advice {
          background: #f7f1e4; border-radius: 10px; color: #624d27;
          line-height: 1.6; margin: .55rem 0; padding: .58rem .7rem;
        }
        .blueprint-step {
          color: var(--gold); font-size: .76rem; font-weight: 800; letter-spacing: .08em;
        }
        .paper-card-title {
          font-size: 1rem; font-weight: 760; line-height: 1.42; margin: .25rem 0 .65rem;
          min-height: 4.25rem;
        }
        .paper-meta { margin-bottom: .75rem; }
        .paper-copy { color: var(--ink); font-size: .88rem; line-height: 1.62; margin-top: .55rem; }
        .paper-copy strong { color: #624d27; }
        @media (max-width: 700px) {
          .block-container { padding-left: 1rem; padding-right: 1rem; }
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
    )

    metrics = st.columns(4)
    metrics[0].metric("已收录期刊", str(len(records)))
    metrics[1].metric("投稿梯队", str(len({r['tier'] for r in records})))
    metrics[2].metric("出版社", str(len({r['publisher'] for r in records})))
    metrics[3].metric("最近核验", max(str(r["verified_on"]) for r in records))

    st.markdown("#### 官方作者指南直达")
    st.markdown(
        " · ".join(
            f'[{record["name"]}]({record["guide_url"]})' for record in records
        )
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


def _requirement_rows(
    items: list[dict[str, str]], label_key: str
) -> list[dict[str, str]]:
    label = "稿件部分" if label_key == "section" else "项目"
    return [
        {
            label: item[label_key],
            "官方明确要求": item["requirement"],
            "证据范围": item["scope"],
            "官方原文": item["source_url"],
        }
        for item in items
    ]


def render_format_quick_sheet(
    record: dict[str, Any], spec: dict[str, Any]
) -> None:
    """Render source-linked house style before the broader submission details."""

    st.subheader("投稿硬参数速查")
    st.caption(
        f"默认稿型：{spec['default_article_type']}　·　"
        f"规则核验：{spec['verified_on']}"
    )
    available_specs = [
        (label, key, spec["quick_specs"][key])
        for label, key in FORMAT_SPEC_FIELDS
        if spec["quick_specs"][key]["scope"] != "官网未规定固定上限"
    ]
    cards = st.columns(2)
    for index, (label, _, item) in enumerate(available_specs):
        with cards[index % 2]:
            with st.container(border=True):
                st.markdown(
                    f'<div class="format-card-title">{escape(label)}</div>'
                    f'<span class="official-label">官方规则</span> '
                    f'<span class="evidence-badge">{escape(str(item["scope"]))}</span>'
                    f'<div class="format-card-copy">{escape(str(item["official"]))}</div>'
                    f'<div class="format-card-advice"><strong>本站建议</strong>　'
                    f'{escape(str(item["advice"]))}</div>'
                    f'<a href="{escape(str(item["source_url"]))}" target="_blank">'
                    f'{escape(str(record["name"]))} 格式指南 ↗</a>',
                    unsafe_allow_html=True,
                )

    st.subheader("推荐排稿骨架")
    route = " → ".join(str(item["section"]) for item in spec["blueprint"])
    st.caption(f"建议写作顺序：{route}")
    for index, item in enumerate(spec["blueprint"], start=1):
        with st.container(border=True):
            st.markdown(
                f'<span class="blueprint-step">STEP {index:02d}</span>　'
                f'<strong>{escape(str(item["section"]))}</strong><br>'
                f'{escape(str(item["task"]))}',
                unsafe_allow_html=True,
            )


def render_paper_examples(
    record: dict[str, Any],
    examples: list[dict[str, object]],
    local_papers: dict[str, dict[str, object]],
) -> None:
    """Render three real papers as learning examples, not official templates."""

    st.subheader("精选已发表实例")
    st.caption("查看同刊真实论文的写法、图组和参考文献呈现。")
    columns = st.columns(3)
    for index, item in enumerate(examples):
        has_local_pdf = str(item["url"]) in local_papers
        local_badge = '<span class="tag">站内 PDF</span>' if has_local_pdf else ""
        with columns[index]:
            with st.container(border=True):
                st.markdown(
                    f'<div class="paper-card-title"><a href="{escape(str(item["url"]))}" '
                    f'target="_blank">{escape(str(item["title"]))} ↗</a></div>'
                    f'<div class="paper-meta">'
                    f'<span class="tag">{escape(str(item["year"]))}</span>'
                    f'<span class="tag">{escape(str(item["article_type"]))}</span>'
                    f'<span class="tag">{escape(str(item["topic"]))}</span>'
                    f'{local_badge}'
                    f'</div>'
                    f'<div class="paper-copy"><strong>为什么选</strong>　'
                    f'{escape(str(item["why_recommended"]))}</div>'
                    f'<div class="paper-copy"><strong>重点观察</strong>　'
                    f'{escape(str(item["look_at"]))}</div>',
                    unsafe_allow_html=True,
                )

    available = [
        local_papers[str(item["url"])]
        for item in examples
        if str(item["url"]) in local_papers
    ]
    if not available:
        return

    st.subheader("站内 PDF 正文")
    st.caption("以下为用户从本地论文库提供的论文副本。")
    if len(available) == 1:
        selected = available[0]
    else:
        titles = [str(item["title"]) for item in available]
        selected_title = st.selectbox(
            "选择站内论文",
            titles,
            key=f"local_pdf_{record['id']}",
        )
        selected = available[titles.index(selected_title)]

    pdf_path = Path(selected["path"])
    file_name = Path(str(selected["file"])).name
    st.markdown(f"**{escape(str(selected['title']))}**")
    st.caption(
        f"文件：{file_name} · 下方可下载这篇 PDF，并可核验 DOI 原文。"
    )
    st.pdf(
        pdf_path,
        height=900,
        key=f"pdf_viewer_{record['id']}_{selected['sha256']}",
        alt=str(selected["title"]),
    )
    actions = st.columns([1, 1, 2])
    with actions[0]:
        st.download_button(
            "下载这篇 PDF",
            data=pdf_path.read_bytes(),
            file_name=file_name,
            mime="application/pdf",
            key=f"download_pdf_{record['id']}_{selected['sha256']}",
        )
    with actions[1]:
        source_url = next(
            item["url"] for item in examples if item["title"] == selected["title"]
        )
        st.link_button("核验 DOI 原文", str(source_url))


def render_deep_workbench(
    records: list[dict[str, Any]],
    guidance: dict[str, dict[str, Any]],
    official_requirements: dict[str, dict[str, Any]],
    format_specs: dict[str, dict[str, Any]],
    examples: dict[str, list[dict[str, object]]],
    local_papers: dict[str, dict[str, object]],
) -> None:
    st.subheader("深度投稿工作台")
    st.caption("先按官方要求搭好稿件，再使用本站建议检查选刊契合度。")
    names = [str(record["name"]) for record in records]
    selected_name = st.selectbox(
        "选择要准备的期刊",
        names,
        key="workbench_journal",
    )
    record = next(record for record in records if record["name"] == selected_name)
    journal_id = str(record["id"])
    workbench = build_official_workbench(
        record,
        official_requirements[journal_id],
        guidance[journal_id],
    )
    official = workbench["official"]
    editorial = workbench["editorial"]

    render_format_quick_sheet(record, format_specs[journal_id])

    st.subheader("官方要求总览")
    st.markdown(
        '<div class="guidance-banner">'
        '<span class="official-label">官方要求</span> '
        f'<strong>{escape(str(workbench["journal_name"]))} · '
        f'{escape(str(official["default_article_type"]))}</strong><br>'
        f'证据范围：{escape(str(official["requirement_scope"]))}　·　'
        f'核验日期：{escape(str(official["verified_on"]))}'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        " · ".join(
            f"[官方来源 {index}]({url})"
            for index, url in enumerate(official["source_urls"], start=1)
        )
    )
    if notice := freshness_notice(str(official["verified_on"])):
        st.error(notice)

    st.subheader("稿件各部分格式")
    st.caption("每一行包含官方要求、适用范围和官方原文入口。")
    st.table(_requirement_rows(official["section_requirements"], "section"))

    st.subheader("提交文件与技术规格")
    st.table(_requirement_rows(official["technical_requirements"], "item"))

    st.subheader("官方模板与实例")
    st.caption("按资源类型查看官方模板、官方示例和已发表论文实例。")
    for resource in official["resources"]:
        st.markdown(
            f'**[{resource["label"]}]({resource["url"]})**　'
            f'<span class="evidence-badge">{escape(resource["kind"])}</span><br>'
            f'{escape(resource["note"])}',
            unsafe_allow_html=True,
        )

    render_paper_examples(record, examples[journal_id], local_papers)

    with st.expander("本站建议 · 选刊契合度与投稿前自查"):
        st.markdown(
            '<span class="guidance-label">本站写作建议</span> '
            f'<strong>{escape(editorial["profile_label"])}</strong><br>'
            f'{escape(editorial["editorial_angle"])}',
            unsafe_allow_html=True,
        )
        good, risk = st.columns(2)
        with good:
            st.markdown("#### 更像适合这本期刊")
            for signal in editorial["fit_signals"]:
                st.markdown(
                    f'<div class="signal-good">✓ {escape(signal)}</div>',
                    unsafe_allow_html=True,
                )
        with risk:
            st.markdown("#### 容易被编辑认为不够")
            for signal in editorial["risk_signals"]:
                st.markdown(
                    f'<div class="signal-risk">△ {escape(signal)}</div>',
                    unsafe_allow_html=True,
                )
        st.markdown("#### 投稿前清单")
        for item in editorial["checklist"]:
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


def main() -> None:
    st.set_page_config(
        page_title="金属材料期刊导航",
        page_icon="◫",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    render_styles()
    records = get_journals()
    journal_ids = tuple(str(record["id"]) for record in records)
    guidance = get_guidance(journal_ids)
    official_requirements = get_official_requirements(journal_ids)
    format_specs = get_format_specs(journal_ids)
    examples = get_examples(journal_ids)
    local_papers = get_local_papers(journal_ids)
    render_header(records)
    filters = render_sidebar(records)
    filtered = filter_journals(records, **filters)
    render_tier_guide(records)
    st.divider()
    render_deep_workbench(
        records,
        guidance,
        official_requirements,
        format_specs,
        examples,
        local_papers,
    )
    st.divider()
    render_catalogue(filtered)
    st.divider()
    render_comparison(records)


if __name__ == "__main__":
    main()
