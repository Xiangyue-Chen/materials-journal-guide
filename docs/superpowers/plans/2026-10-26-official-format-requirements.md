# Official Format Requirements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace schematic journal guidance with a source-backed, section-by-section official submission-requirements workbench.

**Architecture:** Store official requirements in a dedicated validated YAML catalogue, merge it into the existing journal workbench by journal ID, and render official requirements before secondary editorial advice. Keep publisher-generic evidence explicitly scoped and expose official templates/examples as links.

**Tech Stack:** Python 3, Streamlit, PyYAML, pytest

**Spec:** `docs/superpowers/specs/2026-10-26-official-format-requirements-design.md`

## Global Constraints

- Cover every journal ID in `data/journals.yaml`.
- Every visible requirement has a scope and official source URL.
- Never display the phrase `需投稿前复核`.
- Remove the storyboard/SVG illustration feature completely.
- Preserve the existing filters, comparison workflow, and Streamlit deployment.

## Review Focus

- A missing journal ID must fail catalogue loading with a useful error.
- A requirement with an empty or non-HTTP source must fail validation.
- Publisher-level Elsevier guidance must not be labelled journal-specific.
- Unknown official values must render as an honest evidence state, not as a fabricated number or old placeholder.
- Resource links must remain clickable and classified as guide, template, official example, or published example.

---

### Task 1: Official requirements data model

**Files:**
- Create: `journal_guide/official_requirements.py`
- Create: `data/journal_official_requirements.yaml`
- Create: `tests/test_official_requirements.py`

**Interfaces:**
- Produces: `load_official_requirements(path: Path, journal_ids: set[str]) -> dict[str, dict[str, Any]]`
- Produces: `build_official_workbench(record: dict[str, Any], official: dict[str, Any], guidance: dict[str, Any]) -> dict[str, Any]`

- [ ] **Step 1: Write failing catalogue-validation and exact-requirement tests**

Add tests for full journal coverage; required fields and URLs; Nature title/summary/methods/legend limits; Nature Materials main-text/abstract/display/reference limits; Advanced Materials abstract/keywords/ToC/figure/template rules; and Elsevier scope labels.

- [ ] **Step 2: Run the focused tests and verify they fail**

Run: `python -m pytest tests/test_official_requirements.py -q`

Expected: FAIL because the module and catalogue do not exist.

- [ ] **Step 3: Implement the loader, validator, workbench builder, and complete catalogue**

Validate exact key sets, per-item fields, HTTP(S) URLs, allowed scopes/resource kinds, minimum item counts, journal-ID coverage, and forbidden placeholder text.

- [ ] **Step 4: Run the focused tests and verify they pass**

Run: `python -m pytest tests/test_official_requirements.py -q`

Expected: PASS.

- [ ] **Step 5: Commit**

Commit message: `feat: add sourced journal format requirements`

### Task 2: Official-first Streamlit workbench

**Files:**
- Modify: `app.py`
- Modify: `tests/test_app_smoke.py`
- Modify: `tests/test_guidance.py`
- Modify: `journal_guide/guidance.py`
- Modify: `data/journal_guidance.yaml`

**Interfaces:**
- Consumes: `load_official_requirements(...)` and `build_official_workbench(...)` from Task 1.
- Produces: official overview, section-format table, technical-requirements table, and official resource links in `render_deep_workbench(...)`.

- [ ] **Step 1: Replace storyboard smoke assertions with official-workbench assertions**

Assert headings `官方要求总览`, `稿件各部分格式`, `提交文件与技术规格`, and `官方模板与实例`; assert no `主图蓝图`, no storyboard SVG, and no old placeholder text.

- [ ] **Step 2: Run focused UI/guidance tests and verify they fail**

Run: `python -m pytest tests/test_app_smoke.py tests/test_guidance.py -q`

Expected: FAIL on missing new sections and remaining storyboard data.

- [ ] **Step 3: Remove storyboard data/validation/rendering and implement official-first UI**

Delete `_figure_svg`, `_render_storyboard`, related CSS/data validation, and `figure_story`; load the official catalogue at startup and render source links beside requirements. Keep editorial advice in a clearly labelled secondary container.

- [ ] **Step 4: Run focused UI/guidance tests and verify they pass**

Run: `python -m pytest tests/test_app_smoke.py tests/test_guidance.py -q`

Expected: PASS.

- [ ] **Step 5: Commit**

Commit message: `feat: render official submission requirements first`

### Task 3: Documentation and release verification

**Files:**
- Modify: `README.md`
- Modify: `tests/test_app_smoke.py`

**Interfaces:**
- Consumes: the final official workbench UI and data schema.
- Produces: accurate repository documentation and deployable verified application.

- [ ] **Step 1: Add a failing documentation assertion**

Assert the README documents source scopes, official section requirements, official templates/examples, and contains no storyboard claim.

- [ ] **Step 2: Run the documentation test and verify it fails**

Run: `python -m pytest tests/test_app_smoke.py -q`

Expected: FAIL on outdated README wording.

- [ ] **Step 3: Update README and perform self-review**

Document the evidence model and official-first page; check every spec requirement maps to Tasks 1–3 and ensure interface names match.

- [ ] **Step 4: Run full verification**

Run: `python -m pytest -q`

Expected: all tests pass.

Run: `git diff --check`

Expected: no output.

- [ ] **Step 5: Commit and deploy**

Commit message: `docs: explain official journal requirement evidence`

Push the completed changes to `main`, verify the remote commit, and smoke-check the public Streamlit app for all four official headings and the absence of storyboard text.
