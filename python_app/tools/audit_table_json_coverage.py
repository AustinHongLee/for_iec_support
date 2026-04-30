from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


APP_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = APP_DIR / "data"
CONFIG_DIR = APP_DIR / "configs"


def _ensure_import_path() -> None:
    app_dir = str(APP_DIR)
    if app_dir not in sys.path:
        sys.path.insert(0, app_dir)


def _table_id(path: Path) -> str | None:
    match = re.fullmatch(r"(type\d+|m\d+|n\d+[a-z]?|n\d+_pu_block)_table", path.stem)
    if not match:
        return None
    return match.group(1)


def _expected_config_name(table_id: str) -> str:
    if table_id.startswith("type"):
        return f"type_{table_id[4:].zfill(2)}.json"
    return f"{table_id}.json"


def _is_json_bridge(path: Path) -> bool:
    text = path.read_text(encoding="utf-8", errors="ignore")
    return "configs" in text and "json.load" in text


def _supported_type_rows() -> list[dict]:
    _ensure_import_path()
    from core.calculator import get_supported_types
    from tools.find_type import locate_type

    rows = []
    for type_id in get_supported_types():
        info = locate_type(type_id)
        if info["config"]["exists"]:
            anchor_kind = "config"
            anchor_path = info["config"]["path"]
        elif info.get("shared_spec") and info["shared_spec"]["exists"]:
            anchor_kind = "shared_spec"
            anchor_path = info["shared_spec"]["path"]
        elif info["data_bridge"]["exists"]:
            anchor_kind = "data_bridge"
            anchor_path = info["data_bridge"]["path"]
        else:
            anchor_kind = "calculator_only"
            anchor_path = info["handler"].get("calculator")

        rows.append({
            "type_id": type_id,
            "handler": info["handler"].get("calculator"),
            "anchor_kind": anchor_kind,
            "anchor_path": anchor_path,
            "config": info["config"]["path"],
            "config_exists": info["config"]["exists"],
            "type_spec_engine": info["config"].get("type_spec_engine"),
            "shared_spec": info.get("shared_spec"),
            "data_bridge": info["data_bridge"]["path"],
            "data_bridge_exists": info["data_bridge"]["exists"],
        })
    return rows


def _supported_type_summary(rows: list[dict]) -> dict:
    by_anchor = {}
    for row in rows:
        by_anchor[row["anchor_kind"]] = by_anchor.get(row["anchor_kind"], 0) + 1
    return {
        "total": len(rows),
        "by_anchor": by_anchor,
        "calculator_only": [
            row["type_id"] for row in rows if row["anchor_kind"] == "calculator_only"
        ],
        "type_spec": [
            row["type_id"] for row in rows if row.get("type_spec_engine")
        ],
        "shared_spec": [
            row["type_id"] for row in rows if row["anchor_kind"] == "shared_spec"
        ],
    }


def audit_coverage() -> dict:
    rows = []
    for path in sorted(DATA_DIR.glob("*_table.py")):
        table_id = _table_id(path)
        if not table_id:
            continue
        config_name = _expected_config_name(table_id)
        config_path = CONFIG_DIR / config_name
        rows.append({
            "table_id": table_id,
            "table_path": path.relative_to(APP_DIR).as_posix(),
            "expected_config": f"configs/{config_name}",
            "config_exists": config_path.exists(),
            "json_bridge": _is_json_bridge(path),
            "family": (
                "type" if table_id.startswith("type")
                else "m" if table_id.startswith("m")
                else "n"
            ),
        })

    summary = {}
    for family in ("type", "m", "n"):
        family_rows = [row for row in rows if row["family"] == family]
        summary[family] = {
            "total": len(family_rows),
            "config_exists": sum(1 for row in family_rows if row["config_exists"]),
            "json_bridge": sum(1 for row in family_rows if row["json_bridge"]),
            "missing_config": [
                row["table_id"] for row in family_rows if not row["config_exists"]
            ],
            "not_json_bridge": [
                row["table_id"] for row in family_rows if not row["json_bridge"]
            ],
        }

    supported_type_rows = _supported_type_rows()
    return {
        "summary": summary,
        "rows": rows,
        "supported_types": {
            "summary": _supported_type_summary(supported_type_rows),
            "rows": supported_type_rows,
        },
    }


def format_report(audit: dict) -> str:
    lines = ["# Table JSON Coverage Audit", ""]
    supported = audit["supported_types"]["summary"]
    lines.extend([
        "## Supported Type Calculation Anchors",
        "",
        f"- total: {supported['total']}",
        f"- by anchor: {json.dumps(supported['by_anchor'], ensure_ascii=False, sort_keys=True)}",
        f"- type spec: {', '.join(supported['type_spec']) or '-'}",
        f"- shared spec: {', '.join(supported['shared_spec']) or '-'}",
        f"- calculator-only risk: {', '.join(supported['calculator_only']) or '-'}",
        "",
        "Rule: support_ontology.json and type_catalog.json are metadata only; they do not count as calculation anchors.",
        "",
    ])
    for family, data in audit["summary"].items():
        lines.extend([
            f"## {family.upper()} Tables",
            "",
            f"- total: {data['total']}",
            f"- config exists: {data['config_exists']}",
            f"- json bridge: {data['json_bridge']}",
            f"- missing config: {', '.join(data['missing_config']) or '-'}",
            f"- not json bridge: {', '.join(data['not_json_bridge']) or '-'}",
            "",
        ])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit data/*_table.py JSON coverage.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    args = parser.parse_args(argv)

    audit = audit_coverage()
    if args.json:
        print(json.dumps(audit, ensure_ascii=False, indent=2))
    else:
        print(format_report(audit))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
