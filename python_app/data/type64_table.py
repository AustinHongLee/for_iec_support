"""
Type 64 查表資料 — 資料來源: configs/type_64.json
Bridge module (auto-generated 2026-04-29): interface 不變，底層讀 JSON。
原始資料備份: data/_pre_json_backup/type64_table.py
  Type 64 — Pipe-to-Pipe Rod Hanger
  圖號: D-78
  Supported line E: 1/2"~12"
  H: 500~3000mm
  
  E → rod size G
  FIG-A~D → upper/lower clamp 組合
"""
import json as _json, os as _os

_HERE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_JSON_PATH = _os.path.join(_HERE, "configs", "type_64.json")

with open(_JSON_PATH, encoding="utf-8") as _f:
    _DATA = _json.load(_f)

# TYPE64_FIGURE_MAP
TYPE64_FIGURE_MAP = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["TYPE64_FIGURE_MAP"].items()
}

# TYPE64_ROD_TABLE
TYPE64_ROD_TABLE = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["TYPE64_ROD_TABLE"].items()
}


# ── 原始查詢函式（interface 不變）────────────────────────
def get_type64_rod(supported_size: str) -> dict | None:
    """依 supported line size 查 rod size"""
    return TYPE64_ROD_TABLE.get(normalize_fractional_size(supported_size))

def get_type64_figure(fig: str) -> dict | None:
    """依 FIG 查 clamp 組合"""
    return TYPE64_FIGURE_MAP.get(fig.upper())


if __name__ == "__main__":
    print("Type 64 Rod Table:")
    for k, v in TYPE64_ROD_TABLE.items():
        bc = " (FIG-B/C only)" if v['fig_bc_only'] else ""
        print(f"  E={k:>7} → G={v['g']}{bc}")
    print("\nFigure Map:")
    for f, c in TYPE64_FIGURE_MAP.items():
        print(f"  FIG-{f}: upper={c['upper_clamp']}, lower={c['lower_clamp']}")

