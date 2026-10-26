# 期刊投稿硬参数速查 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 17 本材料类期刊增加可直接用于写作和排版的六项硬参数速查及推荐排稿骨架。

**Architecture:** 新建独立 YAML 数据层和严格加载器，把官方规则、证据范围与本站建议分开；现有 Streamlit 工作台在详细官方要求之前渲染卡片和骨架。现有期刊目录与官方要求模块保持不变。

**Tech Stack:** Python 3.13、Streamlit、PyYAML、pytest

**Spec:** `docs/superpowers/specs/2026-10-26-actionable-journal-format-specs-design.md`

## Global Constraints

- 覆盖 `data/journals.yaml` 中全部 17 本期刊。
- 六个固定字段均须包含 `official`、`advice`、`scope`、`source_url`。
- 官网没有稳定数值时，官方值必须明确写“官网未规定固定上限”，本站建议另列。
- 不出现“需投稿前复核”“按指南执行”“具体见官网”等空话。
- 只修改现有 GitHub/Streamlit 应用，不迁移平台。

## Review Focus

- 缺少任一期刊时，加载器应拒绝启动并列出缺失 ID。
- 六个字段缺失、来源不是 HTTPS、范围标签未知时，应抛出可定位错误。
- “官网未规定固定上限”项目不能缺少具体建议。
- 官方值和本站建议不能在 UI 中使用相同证据标签。
- 包含 Markdown 特殊字符的参考文献示例必须安全显示且链接可点击。

---

### Task 1: 速查数据契约与加载器

**Files:**
- Create: `tests/test_format_specs.py`
- Create: `journal_guide/format_specs.py`
- Create: `data/journal_format_specs.yaml`
- Modify: `journal_guide/__init__.py`

**Interfaces:**
- Consumes: `load_journals(path) -> list[dict]`
- Produces: `load_format_specs(path: Path, journal_ids: set[str]) -> dict[str, dict]`

- [ ] **Step 1: Write the failing tests**

覆盖全目录、六字段、HTTPS 来源、允许的证据标签、禁用空占位、未知上限必须有具体建议，以及 Nature/Advanced Materials/PNAS 的精确格式差异。

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_format_specs.py -v`
Expected: FAIL because `journal_guide.format_specs` does not exist.

- [ ] **Step 3: Implement the minimal loader and source-backed dataset**

实现常量 `SPEC_KEYS`、`ALLOWED_SCOPES` 和 `load_format_specs`；填充 17 本期刊的六项速查与蓝图。

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_format_specs.py -v`
Expected: PASS.

### Task 2: 第一屏速查与排稿骨架

**Files:**
- Modify: `tests/test_app_smoke.py`
- Modify: `app.py`

**Interfaces:**
- Consumes: `load_format_specs(...)`
- Produces: `render_format_quick_sheet(spec: dict) -> None` and `render_manuscript_blueprint(spec: dict) -> None`

- [ ] **Step 1: Write failing smoke assertions**

要求应用加载新数据，并在详细官方要求之前渲染“投稿硬参数速查”“推荐排稿骨架”“官方规则”“本站建议”。

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_app_smoke.py -v`
Expected: FAIL because the quick sheet is absent.

- [ ] **Step 3: Implement responsive cards and blueprint rendering**

在工作台期刊标题之后插入速查卡片与编号骨架；保留原有详细要求和模板实例。

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_app_smoke.py -v`
Expected: PASS.

### Task 3: 文档、回归验证与部署

**Files:**
- Modify: `README.md`
- Modify: `.superpowers/sdd/2026-10-26-deep-journal-guidance/verify_public_streamlit.py`

**Interfaces:**
- Consumes: completed data and UI
- Produces: documented and publicly verified Streamlit release

- [ ] **Step 1: Update documentation and public verifier expectations**

说明六项速查、证据标签和官方/建议边界；线上验证器检查新标题及至少一个具体格式片段。

- [ ] **Step 2: Run complete verification**

Run: `pytest -q`
Expected: all tests pass.

Run: `git diff --check`
Expected: no output.

- [ ] **Step 3: Perform local browser QA**

启动 Streamlit，检查桌面与窄屏下卡片、来源链接、骨架顺序和旧模块均可读。

- [ ] **Step 4: Commit, push, and verify the public application**

推送 `main`，等待 Streamlit Cloud 部署后运行公共验证器，确认线上包含新速查内容。

