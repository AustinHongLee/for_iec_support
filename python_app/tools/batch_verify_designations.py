from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Iterable


APP_DIR = Path(__file__).resolve().parents[1]

HARDENED_TYPES = {"03", "05", "06", "07", "08", "27", "39", "42", "43"}
PIPE_SHOE_REVIEW_TYPES = {"52", "53", "54", "55", "66", "67", "80", "85"}
STEEL_M42_TYPES = {
    "03", "05", "07", "08", "14", "15", "19", "20", "21", "22", "23", "24",
    "25", "26", "27", "28", "30", "31", "32", "33", "34", "35", "36", "37",
    "39", "41", "42", "43", "44", "45", "46", "47", "51", "52", "53", "54",
    "55", "65", "66", "67", "80", "85",
}

TOKEN_RE = re.compile(r"\b\d{1,2}[A-Z]?(?:-[A-Z0-9./()*~+]+)+\b", re.IGNORECASE)


def _ensure_import_path() -> None:
    app_dir = str(APP_DIR)
    if app_dir not in sys.path:
        sys.path.insert(0, app_dir)


def normalize_designation(value: str) -> str:
    return value.strip().upper().replace(" ", "")


def type_id_for(designation: str) -> str:
    raw = designation.split("-", 1)[0]
    if raw[-1:].isalpha() and raw[:-1].isdigit():
        return f"{int(raw[:-1]):02d}{raw[-1]}"
    return f"{int(raw):02d}" if raw.isdigit() else raw


def extract_designations(text: str) -> list[str]:
    seen: set[str] = set()
    values: list[str] = []
    for match in TOKEN_RE.finditer(text.replace("－", "-").replace("–", "-")):
        value = normalize_designation(match.group(0))
        if value not in seen:
            seen.add(value)
            values.append(value)
    return values


def _entry_summary(entry) -> dict[str, object]:
    return {
        "name": entry.name,
        "spec": entry.spec,
        "length": entry.length,
        "width": entry.width,
        "quantity": entry.quantity,
        "weight": entry.weight_output,
        "material": entry.material,
        "remark": entry.display_remark,
    }


def risk_status(type_id: str, error: str, warnings: list[str]) -> str:
    if error:
        return "error"
    if type_id in PIPE_SHOE_REVIEW_TYPES:
        return "review"
    if type_id in HARDENED_TYPES:
        return "hardened" if not warnings else "review"
    if warnings:
        return "review"
    if type_id in STEEL_M42_TYPES:
        return "high"
    return "ok"


def analyze_designations(designations: Iterable[str]) -> list[dict[str, object]]:
    _ensure_import_path()
    from core.calculator import analyze_single

    rows: list[dict[str, object]] = []
    for designation in designations:
        type_id = type_id_for(designation)
        result = analyze_single(designation)
        rows.append(
            {
                "designation": designation,
                "type": type_id,
                "status": risk_status(type_id, result.error, result.warnings),
                "error": result.error,
                "warnings": result.warnings,
                "total_weight": round(result.total_weight, 2),
                "entry_count": len(result.entries),
                "entries": [_entry_summary(entry) for entry in result.entries],
            }
        )
    return rows


def render_markdown(rows: list[dict[str, object]]) -> str:
    lines = [
        "# Batch Verification Report",
        "",
        "| Designation | Type | Status | Total kg | Warnings | Error |",
        "|---|---:|---|---:|---|---|",
    ]
    for row in rows:
        warnings = "<br>".join(row["warnings"]) if row["warnings"] else ""
        lines.append(
            f"| `{row['designation']}` | {row['type']} | {row['status']} | "
            f"{row['total_weight']} | {warnings} | {row['error']} |"
        )

    lines.extend(["", "## BOM Details", ""])
    for row in rows:
        lines.extend(
            [
                f"### `{row['designation']}`",
                "",
                "| Item | Name | Spec | L | W | Qty | Weight | Material | Remark |",
                "|---:|---|---|---:|---:|---:|---:|---|---|",
            ]
        )
        for index, entry in enumerate(row["entries"], start=1):
            lines.append(
                f"| {index} | {entry['name']} | `{entry['spec']}` | {entry['length']} | "
                f"{entry['width']} | {entry['quantity']} | {entry['weight']} | "
                f"{entry['material']} | {entry['remark']} |"
            )
        lines.append("")
    return "\n".join(lines)


def write_csv(rows: list[dict[str, object]], output: Path) -> None:
    with output.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "designation", "type", "status", "total_weight", "entry_index",
                "name", "spec", "length", "width", "quantity", "weight",
                "material", "remark", "warnings", "error",
            ]
        )
        for row in rows:
            for index, entry in enumerate(row["entries"], start=1):
                writer.writerow(
                    [
                        row["designation"],
                        row["type"],
                        row["status"],
                        row["total_weight"],
                        index,
                        entry["name"],
                        entry["spec"],
                        entry["length"],
                        entry["width"],
                        entry["quantity"],
                        entry["weight"],
                        entry["material"],
                        entry["remark"],
                        " | ".join(row["warnings"]),
                        row["error"],
                    ]
                )


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch-run support designations and emit a verification report.")
    parser.add_argument("--input", "-i", type=Path, help="Text/CSV file containing support designations. Defaults to stdin.")
    parser.add_argument("--output", "-o", type=Path, help="Output path. Defaults to stdout for md/json.")
    parser.add_argument("--format", choices=("md", "csv", "json"), default="md")
    args = parser.parse_args()

    text = args.input.read_text(encoding="utf-8-sig") if args.input else sys.stdin.read()
    designations = extract_designations(text)
    rows = analyze_designations(designations)

    if args.format == "csv":
        if not args.output:
            raise SystemExit("--output is required for csv format")
        write_csv(rows, args.output)
        return 0

    content = json.dumps(rows, ensure_ascii=False, indent=2) if args.format == "json" else render_markdown(rows)
    if args.output:
        args.output.write_text(content, encoding="utf-8")
    else:
        print(content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
