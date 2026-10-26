# Deep Journal Guidance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the journal catalogue into an actionable manuscript-structure and figure-storyboard workbench for all 17 metallic-materials journals.

**Architecture:** Keep official requirements in the existing journal catalogue and add a separate validated guidance catalogue. Pure-Python composition functions merge reusable writing profiles with journal-specific editorial guidance, while Streamlit renders the result as a focused workbench with original inline SVG storyboards and explicit evidence labels.

**Tech Stack:** Python 3.11+, Streamlit, PyYAML, inline SVG/CSS, pytest, GitHub, Streamlit Community Cloud

**Spec:** `docs/superpowers/specs/2026-10-26-deep-journal-guidance-design.md`

## Global Constraints

- Preserve all 17 journals and the existing filters and comparison flow.
- Separate official requirements from site-authored guidance in both data and UI.
- Do not copy article images; all visual examples are original inline SVG.
- Do not show the raw phrase `需投稿前复核` in user-facing output.
- Keep official URLs, verification dates, and 180-day freshness warnings.

## Review Focus

- A guidance catalogue missing one of the 17 journal IDs must fail validation, not silently fall back.
- An unknown writing profile must report the affected journal ID.
- Raw uncertainty placeholders must map to an explanatory status and reason.
- Inline SVG must escape all journal-authored strings before interpolation.
- The workbench must still render when the selected journal is filtered out of the card list.

---

### Task 1: Validated guidance model

**Files:**
- Create: `data/journal_guidance.yaml`
- Create: `journal_guide/guidance.py`
- Modify: `journal_guide/__init__.py`
- Create: `tests/test_guidance.py`

**Interfaces:**
- Consumes: `load_journals(path: Path) -> list[dict[str, Any]]`.
- Produces: `load_guidance(path: Path, journal_ids: set[str]) -> dict[str, dict[str, Any]]`, `build_workbench(record, guidance) -> dict[str, Any]`, and `explain_requirement(value: object) -> dict[str, str]`.

- [x] **Step 1: Write failing tests for full 17-journal coverage, profile validation, merged workbench shape, and uncertainty explanations**
- [x] **Step 2: Run `python -m pytest tests/test_guidance.py -v` and verify failures are caused by missing guidance APIs**
- [x] **Step 3: Add the guidance catalogue, validation, profile merge, and requirement explanation functions**
- [x] **Step 4: Run `python -m pytest tests/test_guidance.py -v` and the full suite**
- [x] **Step 5: Commit the validated guidance model**

### Task 2: Deep submission workbench UI

**Files:**
- Modify: `app.py`
- Modify: `tests/test_app_smoke.py`

**Interfaces:**
- Consumes: Task 1 workbench dictionaries and requirement evidence dictionaries.
- Produces: `render_deep_workbench(records, guidance)` plus structure, storyboard, evidence-table, and checklist renderers.

- [x] **Step 1: Write failing AppTest assertions for the workbench title, guidance/official labels, structure map, SVG storyboard, and absence of the raw placeholder phrase**
- [x] **Step 2: Run the focused AppTest cases and verify expected failures**
- [x] **Step 3: Implement the workbench and responsive SVG/CSS rendering in `app.py`**
- [x] **Step 4: Run focused tests and the full suite**
- [x] **Step 5: Commit the workbench UI**

### Task 3: Evidence-focused catalogue and comparison

**Files:**
- Modify: `app.py`
- Modify: `tests/test_app_smoke.py`
- Modify: `README.md`

**Interfaces:**
- Consumes: `explain_requirement` from Task 1.
- Produces: concise journal cards and comparison rows with specific evidence states and reasons.

- [x] **Step 1: Write failing tests that prohibit the raw placeholder phrase in the default and comparison views**
- [x] **Step 2: Run focused tests and verify they fail on current raw values**
- [x] **Step 3: Replace generic warnings with evidence badges/reasons and document the boundary**
- [x] **Step 4: Run the full automated suite and `git diff --check`**
- [x] **Step 5: Commit the evidence-focused UI**

### Task 4: Visual QA and publication

**Files:**
- Modify: `docs/superpowers/plans/2026-10-26-deep-journal-guidance.md`

**Interfaces:**
- Consumes: all previous tasks.
- Produces: browser-verified local UI, pushed GitHub `main`, and refreshed Streamlit deployment.

- [x] **Step 1: Run Streamlit locally and verify health**
- [x] **Step 2: Browser-check desktop and narrow layouts, journal switching, storyboards, and evidence tables**
- [x] **Step 3: Run `python -m pytest -q`, `git diff --check`, and a clean-status audit**
- [ ] **Step 4: Merge to `main`, push, and verify the remote commit**
- [ ] **Step 5: Wait for Streamlit redeployment and verify the public workbench**
