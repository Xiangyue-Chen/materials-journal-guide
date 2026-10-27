# Journal Paper Examples Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add three source-linked, instructive published-paper examples for every journal in the guide.

**Architecture:** Store examples in a new strict YAML dataset, validate them with a focused loader, and render them as a separate workbench section after official resources. Keep published examples distinct from official templates and editorial advice.

**Tech Stack:** Python 3.11+, PyYAML, Streamlit, pytest.

**Spec:** `docs/superpowers/specs/2026-10-26-journal-paper-examples-design.md`

## Global Constraints

- Exactly 3 examples for each of the existing 17 journal IDs.
- Every example has `title`, `year`, `article_type`, `topic`, `why_recommended`, `look_at`, and `url`.
- Links are HTTPS DOI or official publisher pages; no images or full-text copying.
- Published examples never appear as official templates or mandatory house style.

## Review Focus

- Missing or extra journal IDs must fail loading.
- Fewer or more than three examples must fail loading.
- Duplicate URLs within one journal must fail loading.
- Blank guidance fields and non-HTTPS URLs must fail loading.
- UI must render the selected journal's examples, not the default journal's examples after selection.

---

### Task 1: Example dataset and loader

**Files:**
- Create: `data/journal_examples.yaml`
- Create: `journal_guide/examples.py`
- Modify: `journal_guide/__init__.py`
- Create: `tests/test_examples.py`

**Interfaces:**
- Produces: `load_examples(path: Path, journal_ids: set[str]) -> dict[str, list[dict[str, object]]]`

- [ ] **Step 1: Write failing loader and data-contract tests**

Assert 17-journal coverage, exactly three records, exact fields, valid years, HTTPS URLs, unique per-journal URLs, representative DOI values, and mutation failures.

- [ ] **Step 2: Run the focused test and verify RED**

Run: `python -m pytest tests/test_examples.py -v`
Expected: FAIL because `journal_guide.examples` does not exist.

- [ ] **Step 3: Implement loader and 51 verified records**

Use strict exact-key validation and deep-copy validated records.

- [ ] **Step 4: Run the focused test and verify GREEN**

Run: `python -m pytest tests/test_examples.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

Commit: `feat: add curated journal paper examples`

### Task 2: Workbench rendering

**Files:**
- Modify: `app.py`
- Modify: `tests/test_app_smoke.py`
- Modify: `README.md`

**Interfaces:**
- Consumes: `load_examples(...)` from Task 1.
- Produces: visible “精选已发表实例” cards in `render_deep_workbench(...)`.

- [ ] **Step 1: Write failing Streamlit behavior tests**

Assert the new heading, disclaimer, three Nature examples, DOI link, reason and observation labels; update direct renderer fixtures for the new argument.

- [ ] **Step 2: Run the focused test and verify RED**

Run: `python -m pytest tests/test_app_smoke.py -v`
Expected: FAIL because the examples section is absent.

- [ ] **Step 3: Implement cached loading and responsive cards**

Render after official templates, before site editorial advice, and document the feature/data boundary.

- [ ] **Step 4: Run the focused and full suites**

Run: `python -m pytest tests/test_app_smoke.py -v`
Expected: PASS.

Run: `python -m pytest -q`
Expected: PASS.

- [ ] **Step 5: Commit**

Commit: `feat: show selected papers for every journal`

### Task 3: Release verification

**Files:**
- Modify: `.superpowers/sdd/2026-10-26-deep-journal-guidance/verify_public_streamlit.py`

**Interfaces:**
- Consumes: completed examples UI.
- Produces: verified public Streamlit release.

- [ ] **Step 1: Add public verifier expectations**

Check the section title, disclaimer, one Nature DOI/title and absence of old placeholders.

- [ ] **Step 2: Run final local verification and review**

Run: `python -m pytest -q`, `python -m py_compile app.py journal_guide/examples.py`, and `git diff --check`.

- [ ] **Step 3: Merge, push, and run the public verifier**

Confirm remote `main`, Streamlit script completion, all expected phrases present, and no runtime exception.
