# Local PDF Library Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Package three user-authorized local papers and make their full PDFs readable inside the existing journal workbench.

**Architecture:** A strict manifest binds known example DOI URLs to packaged PDF assets with recorded size and SHA-256. The Streamlit workbench loads the manifest once, marks available examples, and renders the selected PDF through native `st.pdf` below the example-card row.

**Tech Stack:** Python 3.11+, PyYAML, Streamlit with PDF extra, pytest.

**Spec:** `docs/superpowers/specs/2026-10-26-local-pdf-library-design.md`

## Global Constraints

- Upload only the three explicitly selected Nature, Science, and Acta Materialia PDFs.
- Copy files; never move or edit the originals under `D:\论文提取`.
- Do not publish local source paths.
- Reject a manifest entry whose DOI/title/journal does not match the curated example dataset.
- Reject path traversal, missing files, non-PDF files, size mismatches, and SHA-256 mismatches.
- Keep DOI access as a secondary verification path.

## Review Focus

- A tampered or partially copied PDF must fail manifest loading before rendering.
- A manifest path escaping the repository root must fail safely.
- Journals without packaged PDFs must continue rendering normally.
- Selecting Science or Acta Materialia must show its own PDF, not the Nature file.
- The app must state the current public/personal-study boundary without calling the PDF an official template.

---

### Task 1: PDF assets and strict manifest

**Files:**
- Create: `assets/papers/nature17981.pdf`
- Create: `assets/papers/science1254581.pdf`
- Create: `assets/papers/acta2015-08-076.pdf`
- Create: `data/local_papers.yaml`
- Create: `journal_guide/local_papers.py`
- Modify: `journal_guide/__init__.py`
- Create: `tests/test_local_papers.py`

**Interfaces:**
- Produces: `load_local_papers(manifest_path: Path, root: Path, examples: dict[str, list[dict[str, object]]]) -> dict[str, dict[str, object]]`

- [ ] **Step 1: Write failing loader tests**

Assert exactly three records; representative DOI-to-file mappings; files exist and are PDFs; recorded sizes and SHA-256 values match; local `D:` paths are absent; mutation cases reject unknown DOI, mismatched journal/title, path traversal, wrong extension, missing file, wrong size, and wrong hash.

- [ ] **Step 2: Run the focused test and verify RED**

Run: `python -m pytest tests/test_local_papers.py -v`
Expected: FAIL because `journal_guide.local_papers` does not exist.

- [ ] **Step 3: Copy the three PDFs and implement the strict loader**

Copy verified source files to the three fixed asset names, record their exact size and SHA-256, then implement the loader without exposing source-library paths.

- [ ] **Step 4: Run the focused test and verify GREEN**

Run: `python -m pytest tests/test_local_papers.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

Commit: `feat: package selected local paper PDFs`

### Task 2: In-page PDF viewer

**Files:**
- Modify: `app.py`
- Modify: `requirements.txt`
- Modify: `tests/test_app_smoke.py`
- Modify: `README.md`

**Interfaces:**
- Consumes: `load_local_papers(...)` from Task 1.
- Produces: a selected-journal `st.pdf` viewer and download action below the published-example cards.

- [ ] **Step 1: Write failing Streamlit behavior tests**

Assert the Nature workbench labels the available local PDF, shows the personal-study notice and PDF viewer, and the Science/Acta selections identify their own packaged PDF while a journal without a packaged file shows no viewer.

- [ ] **Step 2: Run the focused test and verify RED**

Run: `python -m pytest tests/test_app_smoke.py -v`
Expected: FAIL because the packaged PDF viewer is absent.

- [ ] **Step 3: Add the Streamlit PDF extra and render the viewer**

Use native `st.pdf` at full workbench width, a stable selected-paper control when needed, and a download button. Keep the DOI link in each card as the secondary original-source route.

- [ ] **Step 4: Run focused and full verification**

Run: `python -m pytest tests/test_app_smoke.py -v`
Expected: PASS.

Run: `python -m pytest -q`
Expected: PASS.

- [ ] **Step 5: Commit**

Commit: `feat: render packaged PDFs in journal workbench`

### Task 3: Release verification

**Files:**
- Modify: `.superpowers/sdd/2026-10-26-deep-journal-guidance/verify_public_streamlit.py`

**Interfaces:**
- Consumes: the completed viewer UI and packaged files.
- Produces: a verified public Streamlit release.

- [ ] **Step 1: Add public verifier expectations**

Check the PDF-library heading, personal-study notice, Nature packaged filename/title, and absence of runtime exceptions.

- [ ] **Step 2: Run local verification and visual QA**

Run the full test suite, Python compilation, manifest hash audit, and `git diff --check`; preview Nature and Acta Materialia locally and confirm that the viewer loads at readable width.

- [ ] **Step 3: Merge, push, and verify the public release**

Confirm remote `main`, `script_finished`, all expected UI phrases, and that each published PDF URL/download returns the recorded byte count.
