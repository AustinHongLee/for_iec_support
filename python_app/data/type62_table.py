"""
Type 62 查表資料 — 資料來源: configs/type_62.json
Bridge module (auto-generated 2026-04-29): interface 不變，底層讀 JSON。
原始資料備份: data/_pre_json_backup/type62_table.py
  Type 62 hanger combination table (D-75/D-76).
  
  The source PDF has no extractable text layer.  The table below is transcribed
  from the rendered vector drawing:
  
  - page 1: upper/lower part sketches and component callouts
  - page 2: TYPE / M-NO. / GRINNELL FIG. NO. / range / temperature table
  
  This table intentionally stores selection metadata only.  Weight precision still
  depends on each M-series component table.
"""
import json as _json, os as _os

_HERE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_JSON_PATH = _os.path.join(_HERE, "configs", "type_62.json")

with open(_JSON_PATH, encoding="utf-8") as _f:
    _DATA = _json.load(_f)

# TYPE62_PART_TABLE
TYPE62_PART_TABLE = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["TYPE62_PART_TABLE"].items()
}


# ── 原始查詢函式（interface 不變）────────────────────────
def get_type62_part(fig: str) -> dict | None:
    row = TYPE62_PART_TABLE.get(str(fig).strip().upper())
    return deepcopy(row) if row else None

def get_type62_upper_part(fig: str) -> dict | None:
    row = get_type62_part(fig)
    return row if row and row["role"] == "upper" else None

def get_type62_lower_part(fig: str) -> dict | None:
    row = get_type62_part(fig)
    return row if row and row["role"] == "lower" else None

def validate_type62_lower_pipe_size(fig: str, line_size) -> tuple[bool, str]:
    row = get_type62_lower_part(fig)
    if not row:
        return False, f"FIG-{fig} is not a Type 62 lower part"

    size = size_to_float(normalize_fractional_size(line_size))
    if size is None:
        return False, f"Cannot parse line size {line_size!r}"

    min_size = row["pipe_size_min"]
    max_size = row["pipe_size_max"]
    if min_size is not None and size < min_size:
        return False, f"FIG-{fig} range is {min_size:g}\"~{max_size:g}\""
    if max_size is not None and size > max_size:
        return False, f"FIG-{fig} range is {min_size:g}\"~{max_size:g}\""
    return True, ""


# TYPE62_UPPER/LOWER_FIGS (set)
TYPE62_UPPER_FIGS = set(_DATA["TYPE62_UPPER_FIGS"])
TYPE62_LOWER_FIGS = set(_DATA["TYPE62_LOWER_FIGS"])
