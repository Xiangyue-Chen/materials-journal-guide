# Materials Journal Guide Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and deploy a source-backed Streamlit website for querying and comparing official submission requirements of commonly targeted metallic-materials journals.

**Architecture:** A validated YAML file is the source of truth. Small pure-Python modules load and filter journal records, while a single Streamlit entry point renders browsing and comparison views. Tests protect required fields, evidence boundaries, filtering, and comparison limits.

**Tech Stack:** Python 3.11+, Streamlit, PyYAML, pytest, GitHub, Streamlit Community Cloud

**Spec:** `docs/superpowers/specs/2026-10-26-materials-journal-guide-design.md`

## Global Constraints

- Initial scope is 17 journals focused on metallic materials, high-entropy alloys, and structural materials.
- Tier labels are navigation aids, not official rankings.
- Official journal or publisher pages are the only sources for hard submission requirements.
- Unknown or article-type-dependent values must remain explicitly unconfirmed.
- No fixed impact-factor, quartile, APC, or unofficial review-time values in version 1.
- Comparison accepts 2–4 journals.

## Review Focus

- Missing required YAML fields must fail validation with the journal ID in the error.
- Duplicate journal IDs or names must fail validation rather than silently overwrite records.
- Empty filters must return all journals, while combined filters must use AND semantics.
- Search must be case-insensitive and match English names, abbreviations, Chinese summaries, and tags.
- More than four comparison selections must be rejected deterministically.

---

### Task 1: Repository skeleton and validated journal schema

**Files:**
- Create: `pyproject.toml`
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `journal_guide/__init__.py`
- Create: `journal_guide/data.py`
- Create: `tests/test_data.py`

**Interfaces:**
- Produces: `load_journals(path: Path) -> list[dict[str, Any]]`
- Produces: `validate_journals(records: list[dict[str, Any]]) -> None`

- [x] **Step 1: Write failing schema tests**

Test that required fields are enforced, duplicate IDs/names are rejected, valid records load, and source URLs use HTTPS.

- [x] **Step 2: Run tests and confirm failure**

Run: `python -m pytest tests/test_data.py -v`

Expected: FAIL because `journal_guide.data` does not exist.

- [x] **Step 3: Implement validation and loading**

Add the exact interfaces above, YAML root validation, clear `ValueError` messages, and normalized list fields.

- [x] **Step 4: Run tests and confirm pass**

Run: `python -m pytest tests/test_data.py -v`

Expected: PASS.

- [x] **Step 5: Commit**

Commit message: `feat: add validated journal data model`

### Task 2: Seed the official-source journal database

**Files:**
- Create: `data/journals.yaml`
- Modify: `tests/test_data.py`

**Interfaces:**
- Consumes: `load_journals()` and `validate_journals()` from Task 1.
- Produces: 17 validated records ordered by `tier_order` and `name`.

- [x] **Step 1: Add failing seed-data assertions**

Assert the expected 17 IDs, supported tiers, official URLs, nonempty source lists, and ISO-format verification dates.

- [x] **Step 2: Run seed-data tests and confirm failure**

Run: `python -m pytest tests/test_data.py -v`

Expected: FAIL because `data/journals.yaml` is missing.

- [x] **Step 3: Add 17 source-backed journal records**

Populate the exact fields in the spec. Use `需投稿前复核` for any official requirement not confirmed on a current official page.

- [x] **Step 4: Run seed-data tests and confirm pass**

Run: `python -m pytest tests/test_data.py -v`

Expected: PASS with 17 records.

- [x] **Step 5: Commit**

Commit message: `data: add metallic materials journal requirements`

### Task 3: Search, filters, and comparison rules

**Files:**
- Create: `journal_guide/filters.py`
- Create: `tests/test_filters.py`

**Interfaces:**
- Consumes: validated journal dictionaries from Task 1.
- Produces: `filter_journals(records, query="", tiers=None, publishers=None, topics=None, oa_models=None) -> list[dict]`
- Produces: `select_for_comparison(records, ids: list[str]) -> list[dict]`

- [x] **Step 1: Write failing filtering tests**

Cover empty filters, case-insensitive multilingual search, AND semantics across filters, OR semantics within one filter, order preservation, unknown IDs, and the 4-journal ceiling.

- [x] **Step 2: Run tests and confirm failure**

Run: `python -m pytest tests/test_filters.py -v`

Expected: FAIL because `journal_guide.filters` does not exist.

- [x] **Step 3: Implement pure filtering functions**

Use normalized text matching and preserve the database order; raise `ValueError` when more than four IDs are supplied.

- [x] **Step 4: Run tests and confirm pass**

Run: `python -m pytest tests/test_filters.py -v`

Expected: PASS.

- [x] **Step 5: Commit**

Commit message: `feat: add journal search and comparison logic`

### Task 4: Streamlit browsing and comparison interface

**Files:**
- Create: `app.py`
- Create: `.streamlit/config.toml`
- Create: `tests/test_app_smoke.py`

**Interfaces:**
- Consumes: `load_journals()`, `filter_journals()`, and `select_for_comparison()`.
- Produces: Streamlit app with filters, journal cards, comparison table, evidence links, and freshness notices.

- [x] **Step 1: Write failing app smoke test**

Use Streamlit AppTest to require the title, 17 loaded records, filter widgets, zero uncaught exceptions, and a visible evidence disclaimer.

- [x] **Step 2: Run smoke test and confirm failure**

Run: `python -m pytest tests/test_app_smoke.py -v`

Expected: FAIL because `app.py` does not exist.

- [x] **Step 3: Implement the responsive Streamlit interface**

Render the academic editorial visual system, sidebar filters, tier summary, expandable cards, 2–4 journal comparison, official links, and Chinese evidence messaging.

- [x] **Step 4: Run app tests and confirm pass**

Run: `python -m pytest tests/test_app_smoke.py -v`

Expected: PASS.

- [x] **Step 5: Commit**

Commit message: `feat: build journal comparison web app`

### Task 5: Documentation, full verification, and publication

**Files:**
- Create: `README.md`
- Create: `CONTRIBUTING.md`
- Modify: `docs/superpowers/plans/2026-10-26-materials-journal-guide.md`

**Interfaces:**
- Consumes: all prior tasks.
- Produces: reproducible setup instructions, maintenance rules, verified GitHub repository, and deployed Streamlit URL.

- [ ] **Step 1: Document local use and evidence maintenance**

Describe setup, run, test, YAML fields, official-source rule, verification dates, correction workflow, and Streamlit deployment.

- [ ] **Step 2: Run full automated verification**

Run: `python -m pytest -v`

Expected: all tests PASS.

- [ ] **Step 3: Run noninteractive Streamlit startup check**

Run Streamlit headless on a temporary port, request its health endpoint, and stop it after a successful response.

Expected: HTTP 200 and `ok` health body.

- [ ] **Step 4: Initialize and commit the repository**

Run Git initialization, configure `main`, and commit all tracked files.

- [ ] **Step 5: Create GitHub repository and push**

Create the separate public repository `materials-journal-guide`, push `main`, and verify the remote commit.

- [ ] **Step 6: Deploy and verify Streamlit Community Cloud**

Create the app from `app.py`, wait for a healthy deployment, and open the public URL.

