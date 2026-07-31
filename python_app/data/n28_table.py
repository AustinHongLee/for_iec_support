"""N-28 white-oak block dimensional table.

Source: ``N-28-WOOD BLOCK.pdf`` / DSP-500-006 / N-28 / Rev.0.
The drawing identifies white oak but supplies no density, so this module
provides fabrication geometry and net volume without inventing a weight.
"""

from __future__ import annotations

from copy import deepcopy
import math


N28_COMPONENT_INFO = {
    "component_id": "N-28",
    "name_en": "WOOD BLOCK",
    "category": "component_cold",
    "pdf_file": "N-28-WOOD BLOCK.pdf",
    "engineering_standard": "DSP-500-006",
    "drawing_no": "N-28",
    "revision": "0",
    "table_kind": "dimensional_lookup",
    "lookup_ready": True,
    "weight_ready": False,
    "transcription_status": "drawing_reverified",
    "material": "WHITE OAK",
}


N28_TABLE = {
    "WOOD-1": {
        "block_no": "WOOD-1",
        "L1_mm": 300,
        "L3_mm": 50,
        "W1_mm": 180,
        "W2_mm": 40,
        "W3_mm": 40,
        "T1_mm": 40,
        "hole_diameter_mm": 24,
        "hole_count": 4,
        "edge_chamfer_mm": 10,
    },
    "WOOD-2": {
        "block_no": "WOOD-2",
        "L1_mm": 200,
        "L3_mm": 50,
        "W1_mm": 230,
        "W2_mm": 40,
        "W3_mm": 40,
        "T1_mm": 40,
        "hole_diameter_mm": 24,
        "hole_count": 4,
        "edge_chamfer_mm": 10,
    },
    "WOOD-3": {
        "block_no": "WOOD-3",
        "L1_mm": 230,
        "L3_mm": 40,
        "W1_mm": 170,
        "W2_mm": None,
        "W3_mm": 60,
        "T1_mm": 40,
        "hole_diameter_mm": 24,
        "hole_count": 2,
        "edge_chamfer_mm": None,
    },
    "WOOD-4": {
        "block_no": "WOOD-4",
        "L1_mm": 230,
        "L3_mm": 40,
        "W1_mm": 130,
        "W2_mm": None,
        "W3_mm": 60,
        "T1_mm": 40,
        "hole_diameter_mm": 24,
        "hole_count": 2,
        "edge_chamfer_mm": None,
    },
}


def _normalize_block_no(value) -> str:
    text = str(value).strip().upper()
    if text.startswith("WOOD-"):
        return text
    return f"WOOD-{text}"


def _hole_centers(row: dict) -> list[dict]:
    x_values = [row["L3_mm"], row["L1_mm"] - row["L3_mm"]]
    if row["hole_count"] == 2:
        y_values = [row["W1_mm"] - row["W3_mm"]]
    else:
        y_values = [row["W2_mm"], row["W1_mm"] - row["W3_mm"]]
    return [
        {"x_mm": x_value, "y_mm": y_value}
        for y_value in y_values
        for x_value in x_values
    ]


def get_n28_component() -> dict:
    return {
        **deepcopy(N28_COMPONENT_INFO),
        "designation": "WOOD-{1|2|3|4}",
        "line_size_range": "selected by host cold-support drawing",
        "notes": [
            "Cut geometry is complete.",
            "Weight remains unresolved because N-28 supplies no white-oak density.",
        ],
    }


def get_n28_by_number(block_no) -> dict | None:
    row = N28_TABLE.get(_normalize_block_no(block_no))
    if not row:
        return None
    resolved = deepcopy(row)
    gross_volume = row["L1_mm"] * row["W1_mm"] * row["T1_mm"]
    hole_volume = (
        row["hole_count"]
        * math.pi
        * (row["hole_diameter_mm"] / 2) ** 2
        * row["T1_mm"]
    )
    fabrication_blockers = []
    if row["edge_chamfer_mm"] is not None:
        fabrication_blockers.append(
            "N-28 shows a 10 mm chamfer for WOOD-1/2 but does not "
            "unambiguously state its edge extent/multiplicity"
        )
    resolved.update(
        {
            **deepcopy(N28_COMPONENT_INFO),
            "gross_volume_mm3": gross_volume,
            "hole_volume_mm3": hole_volume,
            "volume_before_chamfer_mm3": gross_volume - hole_volume,
            "hole_centers_mm": _hole_centers(row),
            "fabrication_ready": not fabrication_blockers,
            "fabrication_blockers": fabrication_blockers,
        }
    )
    return resolved
