"""
M-47 Compressed Gasket 資料表。

目前來源:
- 舊有 `m42_table.py` 內的 M47 width/length 尺寸映射
- Type 13 既有厚度假設: <= 24" 採 3t
- Type 67 / D-81A 文件註記: 26"~42" gasket 採 1.5t

這代表 M-47 已有可用的尺寸 lookup，但厚度仍屬 repo 內推論整合，
不是逐字逐表從原始 M-47 PDF 全轉錄。
"""
from __future__ import annotations

from .component_size_utils import normalize_fractional_size, size_to_float


M47_DENSITY_KG_M3 = 1500.0

_RAW_M47_DIMENSIONS = {
    0.75: (50, 83),
    1.0: (50, 105),
    1.5: (50, 152),
    2.0: (50, 190),
    2.5: (50, 229),
    3.0: (50, 279),
    4.0: (50, 359),
    5.0: (50, 444),
    6.0: (50, 529),
    8.0: (80, 688),
    10.0: (80, 858),
    12.0: (80, 1017),
    14.0: (80, 1117),
    16.0: (80, 1277),
    18.0: (80, 1436),
    20.0: (90, 1596),
    24.0: (90, 1915),
    26.0: (90, 2074),
    28.0: (90, 2234),
    30.0: (90, 2393),
    32.0: (90, 2553),
    34.0: (110, 2712),
    36.0: (110, 2872),
    40.0: (110, 3191),
    42.0: (110, 3350),
}


def _default_thickness_mm(line_size_float: float) -> float:
    if line_size_float >= 26:
        return 1.5
    return 3.0


def _thickness_source(line_size_float: float) -> str:
    if line_size_float >= 26:
        return 'Type 67 / D-81A note (1.5t for 26"~42")'
    return 'legacy Type 13 calculator assumption (3t for <=24")'


def _calc_weight_kg(width_mm: float, length_mm: float, thickness_mm: float) -> float:
    volume_m3 = (width_mm / 1000.0) * (length_mm / 1000.0) * (thickness_mm / 1000.0)
    weight = volume_m3 * M47_DENSITY_KG_M3
    return max(round(weight, 2), 0.01)


M47_TABLE = {}
for _line_size_float, (_width_mm, _length_mm) in _RAW_M47_DIMENSIONS.items():
    _line_size = normalize_fractional_size(_line_size_float)
    _thickness_mm = _default_thickness_mm(_line_size_float)
    M47_TABLE[_line_size] = {
        "designation": f"M-47 {_line_size.replace(chr(34), 'B')}",
        "designation_inferred": True,
        "line_size": _line_size,
        "width_mm": _width_mm,
        "length_mm": _length_mm,
        "thickness_mm": _thickness_mm,
        "thickness_inferred": True,
        "thickness_source": _thickness_source(_line_size_float),
        "density_kg_m3": M47_DENSITY_KG_M3,
        "unit_weight_kg": _calc_weight_kg(_width_mm, _length_mm, _thickness_mm),
        "spec": f"{_width_mm}×{_length_mm}×{_thickness_mm:g}t",
    }


def get_m47_by_line_size(line_size) -> dict | None:
    return M47_TABLE.get(normalize_fractional_size(line_size))


def get_m47_dimensions(line_size) -> tuple[int, int]:
    row = get_m47_by_line_size(line_size)
    if not row:
        raise ValueError(f"管徑 {line_size} 不在 M47 查詢表中")
    return row["width_mm"], row["length_mm"]


def build_m47_item(line_size, *, thickness_mm: float | None = None) -> dict | None:
    row = get_m47_by_line_size(line_size)
    if not row:
        return None
    item = dict(row)
    if thickness_mm is not None:
        item["thickness_mm"] = thickness_mm
        item["unit_weight_kg"] = _calc_weight_kg(
            item["width_mm"],
            item["length_mm"],
            thickness_mm,
        )
        item["spec"] = f'{item["width_mm"]}×{item["length_mm"]}×{thickness_mm:g}t'
    return item


def estimate_m47_weight(line_size, *, thickness_mm: float | None = None) -> float:
    row = build_m47_item(line_size, thickness_mm=thickness_mm)
    if not row:
        raise ValueError(f"管徑 {line_size} 不在 M47 查詢表中")
    return row["unit_weight_kg"]
