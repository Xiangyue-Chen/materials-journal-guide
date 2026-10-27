# Local PDF Library Design

## Intent

Make selected published-paper examples readable inside the existing Streamlit journal guide instead of forcing the user to leave for the publisher site. The first release packages three PDFs that the user explicitly authorized uploading from the local library.

## Goals

- Package one Nature, one Science, and one Acta Materialia PDF without modifying the originals under `D:\论文提取`.
- Show the PDF in a full-width native Streamlit viewer for the currently selected journal.
- Keep the DOI as a secondary source-verification link and provide a download action.
- Validate that every packaged file matches a known example, exists under the repository's paper-assets directory, and retains its recorded SHA-256 and byte size.

## Non-goals

- Do not scan or upload more local papers in this release.
- Do not make the GitHub repository or Streamlit app private.
- Do not imply that uploading changes the paper's copyright or publisher terms.

## Constraints

- The user explicitly chose to upload before changing the current public visibility.
- The deployed app uses Streamlit 1.66.1 and supports native `st.pdf` when the `pdf` extra is installed.
- PDF viewers stay outside the three-column paper-card row so that pages remain readable.
- Repository paths exposed in the application must be relative paths; local `D:` paths never appear in published data.

## Approaches

1. **Native `st.pdf` with packaged repository assets (selected).** Reliable in the current Streamlit runtime, supports a full-width viewer, and keeps the implementation small. It adds the official Streamlit PDF extra.
2. **Static-file iframe.** Avoids a dependency but requires static-serving configuration and is less reliable across local and cloud URL prefixes.
3. **Publisher iframe.** Rejected because publishers commonly block framing and the user would still depend on the external site.

## Design

`data/local_papers.yaml` is a strict manifest keyed by DOI URL. Each record stores journal ID, title, repository-relative file path, byte size, and SHA-256. `journal_guide/local_papers.py` validates the manifest against the existing example dataset and returns resolved file paths. The workbench marks cards that have a packaged PDF, then renders a selector and a full-width `st.pdf` viewer below the card row. A visible notice states that the files are user-supplied copies for personal study and that copyright remains with the authors and publishers.
