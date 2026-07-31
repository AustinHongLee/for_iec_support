"""Audit numeric Type drawing coverage across the known source profiles.

This tool is intentionally conservative.  It only marks drawings as identical
when their ordered PDF files have identical SHA-256 hashes.  Text similarity is
reported as a review aid, never as proof that two calculation rules are equal.

Usage:
    python tools/audit_type_source_sets.py
    python tools/audit_type_source_sets.py --json-output ../docs/type_source_audit.json
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import asdict, dataclass
from difflib import SequenceMatcher
import hashlib
import json
from pathlib import Path
import re
import sys

from pypdf import PdfReader


APP_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = APP_DIR.parent

SOURCE_DIRS = {
    "cw_e25_24_hp6": REPO_DIR / "單張-本案有關" / "中威",
    "ctci_22a_5123a": REPO_DIR / "單張-本案有關" / "中鼎" / "22A_5123A",
    "ctci_20e4588": REPO_DIR / "單張-本案有關" / "中鼎" / "長春_Type",
}
CURRENT_ASSET_DIR = APP_DIR / "assets" / "Type_cp129_2026"

TYPE_FILENAME_RE = re.compile(r"^TYPE-(\d+[A-Z]?)_", re.IGNORECASE)
LEGACY_FILENAME_RE = re.compile(r"^(\d+[A-Z]?)$", re.IGNORECASE)
DROP_TEXT_LINE_RE = re.compile(
    r"(PROJECT\s*NO|ENGINEERING\s+STANDARD|CTCI|CHUNG\s+WEI|"
    r"中鼎|中威|^\s*(BY|DATE|CHK|APPR|REV)\b)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class PdfFact:
    path: str
    name: str
    sha256: str
    page_content_sha256: list[str]
    pages: int
    page_sizes_pt: list[list[float]]
    normalized_text_sha256: str


def _normalize_type_id(raw: str) -> str:
    value = str(raw).strip().upper()
    if value.endswith(("C", "T")) and value[:-1].isdigit():
        return f"{int(value[:-1]):02d}{value[-1]}"
    return f"{int(value):02d}" if value.isdigit() else value


def _type_id_from_path(path: Path, *, legacy: bool) -> str | None:
    if legacy:
        # The 20E4588 source originally used grouped files such as ``66.pdf``.
        # After the source-preserving split it follows the same one-drawing
        # convention as the other profiles, e.g. ``TYPE-66_D-80A.pdf``.
        match = (
            TYPE_FILENAME_RE.match(path.name)
            or LEGACY_FILENAME_RE.fullmatch(path.stem)
        )
    else:
        match = TYPE_FILENAME_RE.match(path.name)
    return _normalize_type_id(match.group(1)) if match else None


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _normalized_pdf_text(reader: PdfReader) -> str:
    kept: list[str] = []
    for page in reader.pages:
        for line in (page.extract_text() or "").splitlines():
            value = " ".join(line.upper().split())
            if not value or DROP_TEXT_LINE_RE.search(value):
                continue
            kept.append(value)
    return "\n".join(kept)


def _pdf_fact(path: Path) -> tuple[PdfFact, str]:
    reader = PdfReader(str(path))
    sizes = [
        [
            round(float(page.mediabox.width), 2),
            round(float(page.mediabox.height), 2),
        ]
        for page in reader.pages
    ]
    normalized_text = _normalized_pdf_text(reader)
    page_content_hashes = []
    for page, size in zip(reader.pages, sizes):
        digest = hashlib.sha256()
        digest.update(json.dumps(size).encode("ascii"))
        contents = page.get_contents()
        digest.update(contents.get_data() if contents is not None else b"")
        page_content_hashes.append(digest.hexdigest())
    fact = PdfFact(
        path=str(path.relative_to(REPO_DIR)).replace("\\", "/"),
        name=path.name,
        sha256=_sha256(path),
        page_content_sha256=page_content_hashes,
        pages=len(reader.pages),
        page_sizes_pt=sizes,
        normalized_text_sha256=hashlib.sha256(
            normalized_text.encode("utf-8")
        ).hexdigest(),
    )
    return fact, normalized_text


def _collect_source(
    root: Path, *, legacy: bool = False
) -> tuple[dict[str, list[PdfFact]], dict[str, str]]:
    facts: dict[str, list[PdfFact]] = defaultdict(list)
    texts: dict[str, list[str]] = defaultdict(list)
    for path in sorted(root.glob("*.pdf"), key=lambda item: item.name.casefold()):
        type_id = _type_id_from_path(path, legacy=legacy)
        if not type_id:
            continue
        fact, text = _pdf_fact(path)
        facts[type_id].append(fact)
        texts[type_id].append(text)
    return dict(facts), {
        type_id: "\n".join(parts) for type_id, parts in texts.items()
    }


def _implemented_type_ids() -> set[str]:
    if str(APP_DIR) not in sys.path:
        sys.path.insert(0, str(APP_DIR))
    from core import calculator

    calculator._register_types()
    return set(calculator.TYPE_HANDLERS)


def _group_hashes(facts: list[PdfFact]) -> list[str]:
    return [
        page_hash
        for fact in facts
        for page_hash in fact.page_content_sha256
    ]


def _page_count(facts: list[PdfFact]) -> int:
    return sum(fact.pages for fact in facts)


def _similarity(left: str, right: str) -> float | None:
    if not left or not right:
        return None
    return round(SequenceMatcher(None, left, right).ratio(), 4)


def build_audit() -> dict:
    sources: dict[str, dict[str, list[PdfFact]]] = {}
    texts: dict[str, dict[str, str]] = {}
    for source_id, root in SOURCE_DIRS.items():
        source_facts, source_texts = _collect_source(
            root, legacy=source_id == "ctci_20e4588"
        )
        sources[source_id] = source_facts
        texts[source_id] = source_texts

    current_assets, _ = _collect_source(CURRENT_ASSET_DIR)
    implemented = _implemented_type_ids()
    all_type_ids = sorted(
        set().union(*(set(source) for source in sources.values())),
        key=lambda value: (int(re.match(r"\d+", value).group()), value),
    )

    rows = []
    for type_id in all_type_ids:
        presence = {
            source_id: type_id in source_facts
            for source_id, source_facts in sources.items()
        }
        page_counts = {
            source_id: _page_count(source_facts.get(type_id, []))
            for source_id, source_facts in sources.items()
        }
        cw_hashes = _group_hashes(sources["cw_e25_24_hp6"].get(type_id, []))
        asset_hashes = _group_hashes(current_assets.get(type_id, []))
        cw_matches_current_assets = bool(cw_hashes) and cw_hashes == asset_hashes

        pair_similarity = {
            "cw_vs_ctci22": _similarity(
                texts["cw_e25_24_hp6"].get(type_id, ""),
                texts["ctci_22a_5123a"].get(type_id, ""),
            ),
            "cw_vs_ctci20e": _similarity(
                texts["cw_e25_24_hp6"].get(type_id, ""),
                texts["ctci_20e4588"].get(type_id, ""),
            ),
            "ctci22_vs_ctci20e": _similarity(
                texts["ctci_22a_5123a"].get(type_id, ""),
                texts["ctci_20e4588"].get(type_id, ""),
            ),
        }

        present_groups = [
            _group_hashes(source_facts[type_id])
            for source_facts in sources.values()
            if type_id in source_facts
        ]
        binary_identical_across_present_sources = (
            len(present_groups) >= 2
            and all(group == present_groups[0] for group in present_groups[1:])
        )
        review_status = (
            "identical_binary_skip"
            if binary_identical_across_present_sources
            else "visual_and_rule_review_required"
            if sum(presence.values()) >= 2
            else "single_source_only"
        )

        rows.append(
            {
                "type_id": type_id,
                "implemented": type_id in implemented,
                "presence": presence,
                "page_counts": page_counts,
                "files": {
                    source_id: [
                        asdict(fact) for fact in source_facts.get(type_id, [])
                    ]
                    for source_id, source_facts in sources.items()
                },
                "current_asset_files": [
                    asdict(fact) for fact in current_assets.get(type_id, [])
                ],
                "cw_matches_current_assets": cw_matches_current_assets,
                "text_similarity_review_aid": pair_similarity,
                "review_status": review_status,
                "review_decision": "",
                "review_notes": "",
            }
        )

    return {
        "schema": "type-source-audit/1",
        "policy": (
            "Only identical ordered PDF page-content SHA-256 groups with matching "
            "MediaBox sizes may be skipped automatically. Text similarity is a "
            "review aid and never calculation truth."
        ),
        "sources": {
            source_id: str(path.relative_to(REPO_DIR)).replace("\\", "/")
            for source_id, path in SOURCE_DIRS.items()
        },
        "current_asset_source": str(
            CURRENT_ASSET_DIR.relative_to(REPO_DIR)
        ).replace("\\", "/"),
        "summary": {
            "type_count_by_source": {
                source_id: len(source_facts)
                for source_id, source_facts in sources.items()
            },
            "all_type_ids": len(all_type_ids),
            "implemented_type_ids": sum(row["implemented"] for row in rows),
            "common_to_all_sources": sum(
                all(row["presence"].values()) for row in rows
            ),
            "cw_current_asset_exact_matches": sum(
                row["cw_matches_current_assets"] for row in rows
            ),
            "automatic_identical_skips": sum(
                row["review_status"] == "identical_binary_skip" for row in rows
            ),
        },
        "types": rows,
    }


def _markdown(audit: dict) -> str:
    lines = [
        "# Type Drawing Source Audit",
        "",
        "> Generated by `python_app/tools/audit_type_source_sets.py`. "
        "This is an audit aid, not calculation truth.",
        "",
        f"- Total Type IDs: {audit['summary']['all_type_ids']}",
        f"- Common to all three sources: {audit['summary']['common_to_all_sources']}",
        f"- Current assets exactly matching Chung Wei: "
        f"{audit['summary']['cw_current_asset_exact_matches']}",
        f"- Automatic binary-identical skips: "
        f"{audit['summary']['automatic_identical_skips']}",
        "",
        "| Type | Implemented | CW pages | CTCI 22A pages | CTCI 20E pages | "
        "CW=current asset | CW/22 text | CW/20E text | Review |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in audit["types"]:
        similarity = row["text_similarity_review_aid"]

        def fmt(value):
            return "-" if value is None else f"{value:.3f}"

        lines.append(
            f"| {row['type_id']} | {'yes' if row['implemented'] else 'no'} | "
            f"{row['page_counts']['cw_e25_24_hp6']} | "
            f"{row['page_counts']['ctci_22a_5123a']} | "
            f"{row['page_counts']['ctci_20e4588']} | "
            f"{'yes' if row['cw_matches_current_assets'] else 'no'} | "
            f"{fmt(similarity['cw_vs_ctci22'])} | "
            f"{fmt(similarity['cw_vs_ctci20e'])} | "
            f"{row['review_status']} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--json-output",
        type=Path,
        default=REPO_DIR / "docs" / "type_source_audit.json",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=REPO_DIR / "docs" / "type_source_audit.md",
    )
    args = parser.parse_args()

    audit = build_audit()
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    args.markdown_output.write_text(_markdown(audit), encoding="utf-8")
    print(json.dumps(audit["summary"], ensure_ascii=False, indent=2))
    print(f"Wrote {args.json_output}")
    print(f"Wrote {args.markdown_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
