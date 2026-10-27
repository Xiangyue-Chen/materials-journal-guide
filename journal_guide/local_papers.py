"""Strict manifest loader for packaged user-supplied paper PDFs."""

from __future__ import annotations

from copy import deepcopy
import hashlib
from pathlib import Path
import re

import yaml


LOCAL_PAPER_FIELDS = {
    "journal_id",
    "title",
    "file",
    "size_bytes",
    "sha256",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_local_papers(
    manifest_path: Path,
    root: Path,
    examples: dict[str, list[dict[str, object]]],
) -> dict[str, dict[str, object]]:
    """Load packaged PDFs and prove they match curated published examples."""

    raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or set(raw) != {"papers"}:
        raise ValueError("local paper manifest root must contain only papers")
    papers = raw["papers"]
    if not isinstance(papers, dict):
        raise ValueError("local paper manifest papers must be a mapping")

    curated: dict[str, tuple[str, dict[str, object]]] = {}
    for journal_id, records in examples.items():
        for record in records:
            curated[str(record["url"])] = (journal_id, record)

    resolved_root = root.resolve()
    papers_root = (resolved_root / "assets" / "papers").resolve()
    validated: dict[str, dict[str, object]] = {}
    for url, record in papers.items():
        prefix = f"local paper {url}"
        if str(url) not in curated:
            raise ValueError(f"{prefix}: unknown curated example")
        if not isinstance(record, dict) or set(record) != LOCAL_PAPER_FIELDS:
            raise ValueError(
                f"{prefix}: record must contain exactly "
                f"{', '.join(sorted(LOCAL_PAPER_FIELDS))}"
            )

        expected_journal, example = curated[str(url)]
        if record["journal_id"] != expected_journal:
            raise ValueError(f"{prefix}: journal_id does not match curated example")
        if record["title"] != example["title"]:
            raise ValueError(f"{prefix}: title does not match curated example")

        relative_file = record["file"]
        if not isinstance(relative_file, str) or not relative_file.strip():
            raise ValueError(f"{prefix}: file must be a nonblank relative path")
        candidate = (resolved_root / relative_file).resolve()
        if not candidate.is_relative_to(papers_root):
            raise ValueError(f"{prefix}: file must stay under assets/papers")
        if candidate.suffix.lower() != ".pdf":
            raise ValueError(f"{prefix}: file must be a PDF")
        if not candidate.is_file():
            raise ValueError(f"{prefix}: file does not exist")

        size_bytes = record["size_bytes"]
        if not isinstance(size_bytes, int) or size_bytes <= 0:
            raise ValueError(f"{prefix}: size_bytes must be a positive integer")
        if candidate.stat().st_size != size_bytes:
            raise ValueError(f"{prefix}: size does not match manifest")

        expected_hash = record["sha256"]
        if not isinstance(expected_hash, str) or not re.fullmatch(
            r"[0-9a-f]{64}", expected_hash
        ):
            raise ValueError(f"{prefix}: sha256 must be 64 lowercase hex characters")
        if _sha256(candidate) != expected_hash:
            raise ValueError(f"{prefix}: SHA-256 does not match manifest")

        item = deepcopy(record)
        item["path"] = candidate
        validated[str(url)] = item
    return validated

