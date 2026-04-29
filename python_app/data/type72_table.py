"""
Type 72 strap support dimensional table (D-87).

Source status:
- `72.pdf` is vector-outline based; text extraction returns no usable text.
- 2026-04-21 Codex rendered the vector PDF and transcribed the visible table by
  AI visual inspection.

The drawing calls out:
- STRAP FIG.2 SEE M-54
- 2-phi11 bolt holes for EB-3/8" expansion bolt (M-45)

M-54 is now table-backed in `data.m54_table`; Type 72 keeps this D-87 table for
format/range validation and drawing documentation.
"""
from __future__ import annotations

from copy import deepcopy

from .component_size_utils import normalize_fractional_size


TYPE72_TABLE = {
    '3/4"':   {"line_size": '3/4"', "A": 30.0,  "B": 110, "T": 6, "C": 32, "H": 13.4, "R": 15.0, "D": 20},
    '1"':     {"line_size": '1"',   "A": 36.6,  "B": 120, "T": 6, "C": 32, "H": 16.7, "R": 18.3, "D": 20},
    '1 1/2"': {"line_size": '1 1/2"', "A": 51.6, "B": 140, "T": 6, "C": 50, "H": 24.2, "R": 25.8, "D": 20},
    '2"':     {"line_size": '2"',   "A": 63.6,  "B": 150, "T": 6, "C": 50, "H": 30.2, "R": 31.8, "D": 20},
    '2 1/2"': {"line_size": '2 1/2"', "A": 76.0, "B": 220, "T": 9, "C": 65, "H": 36.5, "R": 38.0, "D": 40},
    '3"':     {"line_size": '3"',   "A": 92.0,  "B": 230, "T": 9, "C": 65, "H": 44.5, "R": 46.0, "D": 40},
    '3 1/2"': {"line_size": '3 1/2"', "A": 105.0, "B": 240, "T": 9, "C": 65, "H": 50.8, "R": 52.5, "D": 40},
    '4"':     {"line_size": '4"',   "A": 117.6, "B": 255, "T": 9, "C": 65, "H": 57.2, "R": 58.8, "D": 40},
}


def get_type72_data(line_size) -> dict | None:
    row = TYPE72_TABLE.get(normalize_fractional_size(line_size))
    return deepcopy(row) if row else None


def list_type72_sizes() -> list[str]:
    return list(TYPE72_TABLE.keys())
