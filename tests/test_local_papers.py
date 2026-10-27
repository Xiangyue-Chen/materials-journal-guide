from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
import yaml

from journal_guide.data import load_journals
from journal_guide.examples import load_examples
from journal_guide.local_papers import LOCAL_PAPER_FIELDS, load_local_papers


ROOT = Path(__file__).parents[1]
MANIFEST_PATH = ROOT / "data" / "local_papers.yaml"
EXAMPLES_PATH = ROOT / "data" / "journal_examples.yaml"
JOURNALS_PATH = ROOT / "data" / "journals.yaml"


def example_records() -> dict[str, list[dict[str, object]]]:
    journal_ids = {
        str(item["id"]) for item in load_journals(JOURNALS_PATH)
    }
    return load_examples(EXAMPLES_PATH, journal_ids)


def test_manifest_packages_three_known_pdfs_without_local_source_paths() -> None:
    papers = load_local_papers(MANIFEST_PATH, ROOT, example_records())

    assert set(papers) == {
        "https://doi.org/10.1038/nature17981",
        "https://doi.org/10.1126/science.1254581",
        "https://doi.org/10.1016/j.actamat.2015.08.076",
    }
    assert "D:\\" not in MANIFEST_PATH.read_text(encoding="utf-8")
    for record in papers.values():
        assert set(record) == LOCAL_PAPER_FIELDS | {"path"}
        path = record["path"]
        assert isinstance(path, Path)
        assert path.is_file()
        assert path.suffix.lower() == ".pdf"
        assert path.is_relative_to(ROOT / "assets" / "papers")
        assert path.stat().st_size == record["size_bytes"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"]


def test_manifest_identifies_each_pdf_with_its_curated_example() -> None:
    papers = load_local_papers(MANIFEST_PATH, ROOT, example_records())

    nature = papers["https://doi.org/10.1038/nature17981"]
    assert nature["journal_id"] == "nature"
    assert nature["title"].startswith("Metastable high-entropy dual-phase")
    assert nature["file"] == "assets/papers/nature17981.pdf"

    science = papers["https://doi.org/10.1126/science.1254581"]
    assert science["journal_id"] == "science"
    assert science["file"] == "assets/papers/science1254581.pdf"

    acta = papers["https://doi.org/10.1016/j.actamat.2015.08.076"]
    assert acta["journal_id"] == "acta-materialia"
    assert acta["file"] == "assets/papers/acta2015-08-076.pdf"


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("wrong_count", r"exactly 3"),
        ("unknown_doi", r"unknown curated example"),
        ("wrong_journal", r"journal_id does not match"),
        ("wrong_title", r"title does not match"),
        ("path_traversal", r"must stay under assets/papers"),
        ("wrong_extension", r"must be a PDF"),
        ("missing_file", r"does not exist"),
        ("wrong_size", r"size does not match"),
        ("wrong_hash", r"SHA-256 does not match"),
    ],
)
def test_loader_rejects_untrusted_or_mismatched_manifest_entries(
    tmp_path: Path, mutation: str, message: str
) -> None:
    data = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    doi = "https://doi.org/10.1038/nature17981"
    record = data["papers"][doi]
    if mutation == "wrong_count":
        data["papers"].pop(doi)
    elif mutation == "unknown_doi":
        data["papers"]["https://doi.org/10.0000/unknown"] = data["papers"].pop(doi)
    elif mutation == "wrong_journal":
        record["journal_id"] = "science"
    elif mutation == "wrong_title":
        record["title"] = "A different paper"
    elif mutation == "path_traversal":
        record["file"] = "../private.pdf"
    elif mutation == "wrong_extension":
        record["file"] = "assets/papers/nature17981.txt"
    elif mutation == "missing_file":
        record["file"] = "assets/papers/missing.pdf"
    elif mutation == "wrong_size":
        record["size_bytes"] += 1
    else:
        record["sha256"] = "0" * 64

    path = tmp_path / "local_papers.yaml"
    path.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        load_local_papers(path, ROOT, example_records())

