from __future__ import annotations

import argparse
import inspect
import json
import sys
from pathlib import Path
from typing import Any


APP_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = APP_DIR.parent


def _ensure_import_path() -> None:
    app_dir = str(APP_DIR)
    if app_dir not in sys.path:
        sys.path.insert(0, app_dir)


def normalize_type_id(type_id: str) -> str:
    value = type_id.strip().upper().replace("TYPE-", "").replace("TYPE_", "")
    if value.endswith("C"):
        prefix = value[:-1]
        return f"{int(prefix):02d}C" if prefix.isdigit() else value
    if value.endswith("T"):
        prefix = value[:-1]
        return f"{int(prefix):02d}T" if prefix.isdigit() else value
    return f"{int(value):02d}" if value.isdigit() else value


def _rel(path: Path | None) -> str | None:
    if not path:
        return None
    try:
        return path.resolve().relative_to(REPO_DIR).as_posix()
    except ValueError:
        return str(path)


def _path_info(path: Path) -> dict[str, Any]:
    return {
        "path": _rel(path),
        "exists": path.exists(),
    }


def _config_info(path: Path) -> dict[str, Any]:
    info = _path_info(path)
    info["type_spec_engine"] = None
    if not path.exists():
        return info
    with path.open("r", encoding="utf-8") as fh:
        config = json.load(fh)
    info["type_spec_engine"] = config.get("TYPE_SPEC", {}).get("engine")
    return info


def _handler_info(type_id: str) -> dict[str, Any]:
    _ensure_import_path()
    from core import calculator

    if not calculator.TYPE_HANDLERS:
        calculator._register_types()

    handler = calculator.TYPE_HANDLERS.get(type_id)
    if not handler:
        return {"supported": False}

    module = inspect.getmodule(handler)
    module_path = Path(module.__file__).resolve() if module and module.__file__ else None
    return {
        "supported": True,
        "handler": f"{handler.__module__}.{handler.__name__}",
        "calculator": _rel(module_path),
    }


def _catalog_entry(type_id: str) -> dict[str, Any]:
    catalog_path = APP_DIR / "configs" / "type_catalog.json"
    if not catalog_path.exists():
        return {"path": _rel(catalog_path), "exists": False, "entry": None}

    with catalog_path.open("r", encoding="utf-8") as fh:
        catalog = json.load(fh)

    entry = next(
        (item for item in catalog.get("types", []) if item.get("type_id") == type_id),
        None,
    )
    summary = None
    if entry:
        summary = {
            "type_id": entry.get("type_id"),
            "name_en": entry.get("name_en"),
            "name_zh": entry.get("name_zh"),
            "status": entry.get("status"),
            "pdf_file": entry.get("pdf_file"),
        }

    return {"path": _rel(catalog_path), "exists": True, "entry": summary}


def _test_mentions(type_id: str) -> list[str]:
    needles = {
        f'"{type_id}-',
        f"'{type_id}-",
        f"Type {type_id}",
        f"type_{type_id.lower()}",
    }
    candidates = [APP_DIR / "validate_tables.py"]
    tests_dir = APP_DIR / "tests"
    if tests_dir.exists():
        candidates.extend(tests_dir.rglob("*.py"))

    mentions: list[str] = []
    for path in candidates:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if any(needle in text for needle in needles):
            mentions.append(_rel(path) or str(path))
    return mentions


def locate_type(type_id: str) -> dict[str, Any]:
    type_id = normalize_type_id(type_id)
    config_name = type_id.lower()
    data_name = type_id.lower().replace("t", "")

    expected_calculator = APP_DIR / "core" / "types" / f"type_{config_name}.py"
    config = APP_DIR / "configs" / f"type_{config_name}.json"
    data_bridge = APP_DIR / "data" / f"type{data_name}_table.py"
    doc = APP_DIR / "docs" / "types" / f"type_{config_name}.md"
    drawing = APP_DIR / "assets" / "Type" / f"{type_id}.pdf"

    info = {
        "type_id": type_id,
        "dispatcher": _path_info(APP_DIR / "core" / "calculator.py"),
        "handler": _handler_info(type_id),
        "expected_calculator": _path_info(expected_calculator),
        "config": _config_info(config),
        "data_bridge": _path_info(data_bridge),
        "doc": _path_info(doc),
        "drawing": _path_info(drawing),
        "catalog": _catalog_entry(type_id),
        "tests": _test_mentions(type_id),
    }

    handler_calculator = info["handler"].get("calculator")
    expected = info["expected_calculator"]["path"]
    info["shared_dispatch"] = bool(handler_calculator and expected and handler_calculator != expected)
    return info


def _format_bool(value: bool) -> str:
    return "yes" if value else "no"


def format_report(info: dict[str, Any]) -> str:
    handler = info["handler"]
    lines = [
        f"Type {info['type_id']}",
        f"supported: {_format_bool(handler.get('supported', False))}",
    ]
    if handler.get("handler"):
        lines.append(f"handler: {handler['handler']}")
    if handler.get("calculator"):
        lines.append(f"calculator: {handler['calculator']}")
    lines.extend([
        f"expected_calculator: {info['expected_calculator']['path']} ({'exists' if info['expected_calculator']['exists'] else 'missing'})",
        f"shared_dispatch: {_format_bool(info['shared_dispatch'])}",
        f"config: {info['config']['path']} ({'exists' if info['config']['exists'] else 'missing'})",
        f"data_bridge: {info['data_bridge']['path']} ({'exists' if info['data_bridge']['exists'] else 'missing'})",
        f"doc: {info['doc']['path']} ({'exists' if info['doc']['exists'] else 'missing'})",
        f"drawing: {info['drawing']['path']} ({'exists' if info['drawing']['exists'] else 'missing'})",
    ])
    if info["config"].get("type_spec_engine"):
        lines.append(f"type_spec_engine: {info['config']['type_spec_engine']}")
    catalog_entry = info["catalog"]["entry"]
    if catalog_entry:
        lines.append(
            "catalog: "
            f"{catalog_entry.get('status') or 'unknown'} | "
            f"{catalog_entry.get('name_en') or '-'} | "
            f"{catalog_entry.get('name_zh') or '-'}"
        )
    else:
        lines.append("catalog: missing entry")

    if info["tests"]:
        lines.append("tests:")
        lines.extend(f"  - {path}" for path in info["tests"])
    else:
        lines.append("tests: no direct mention found")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Locate Type calculator/config/doc/test anchors.")
    parser.add_argument("type_id", help="Type id, e.g. 51, 01T, 66")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    args = parser.parse_args(argv)

    info = locate_type(args.type_id)
    if args.json:
        print(json.dumps(info, ensure_ascii=False, indent=2))
    else:
        print(format_report(info))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
