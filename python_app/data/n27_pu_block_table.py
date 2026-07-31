"""N-27 polyurethane block dimensional and weight table.

Source: ``N27-PU BLOCK.pdf`` / DSP-500-006 / N-27 / Rev.0.
"""

from __future__ import annotations

from copy import deepcopy
import math


N27_COMPONENT_INFO = {
    "component_id": "N27-PU BLOCK",
    "name_en": "PU BLOCK",
    "category": "component_cold",
    "pdf_file": "N27-PU BLOCK.pdf",
    "engineering_standard": "DSP-500-006",
    "drawing_no": "N-27",
    "revision": "0",
    "table_kind": "dimensional_lookup",
    "lookup_ready": True,
    "weight_ready": True,
    "transcription_status": "drawing_reverified",
    "material": "320 KG/M3 POLYURETHANE BLOCK",
    "density_kg_m3": 320,
}


N27_PU_BLOCK_TABLE = {
    "PUBK-1": {
        "block_no": "PUBK-1",
        "L1_mm": 125,
        "L3_mm": 20,
        "W1_mm": 70,
        "W2_mm": None,
        "W3_mm": 35,
        "T1_mm": 50,
        "hole_diameter_mm": 16,
        "hole_count": 2,
    },
    "PUBK-2": {
        "block_no": "PUBK-2",
        "L1_mm": 130,
        "L3_mm": 20,
        "W1_mm": 130,
        "W2_mm": 20,
        "W3_mm": 20,
        "T1_mm": 100,
        "hole_diameter_mm": 16,
        "hole_count": 4,
    },
    "PUBK-3": {
        "block_no": "PUBK-3",
        "L1_mm": 190,
        "L3_mm": 30,
        "W1_mm": 190,
        "W2_mm": 30,
        "W3_mm": 30,
        "T1_mm": 100,
        "hole_diameter_mm": 16,
        "hole_count": 4,
    },
    "PUBK-4": {
        "block_no": "PUBK-4",
        "L1_mm": 240,
        "L3_mm": 35,
        "W1_mm": 240,
        "W2_mm": 35,
        "W3_mm": 35,
        "T1_mm": 100,
        "hole_diameter_mm": 19,
        "hole_count": 4,
    },
    "PUBK-5": {
        "block_no": "PUBK-5",
        "L1_mm": 290,
        "L3_mm": 30,
        "W1_mm": 290,
        "W2_mm": 30,
        "W3_mm": 30,
        "T1_mm": 100,
        "hole_diameter_mm": 19,
        "hole_count": 4,
    },
    "PUBK-6": {
        "block_no": "PUBK-6",
        "L1_mm": 340,
        "L3_mm": 40,
        "W1_mm": 340,
        "W2_mm": 40,
        "W3_mm": 40,
        "T1_mm": 100,
        "hole_diameter_mm": 19,
        "hole_count": 4,
    },
    "PUBK-2U": {
        "block_no": "PUBK-2U",
        "L1_mm": 130,
        "L3_mm": None,
        "W1_mm": 130,
        "W2_mm": None,
        "W3_mm": None,
        "T1_mm": 100,
        "hole_diameter_mm": None,
        "hole_count": 0,
    },
    "PUBK-3U": {
        "block_no": "PUBK-3U",
        "L1_mm": 190,
        "L3_mm": None,
        "W1_mm": 190,
        "W2_mm": None,
        "W3_mm": None,
        "T1_mm": 100,
        "hole_diameter_mm": None,
        "hole_count": 0,
    },
    "PUBK-4U": {
        "block_no": "PUBK-4U",
        "L1_mm": 240,
        "L3_mm": None,
        "W1_mm": 240,
        "W2_mm": None,
        "W3_mm": None,
        "T1_mm": 100,
        "hole_diameter_mm": None,
        "hole_count": 0,
    },
    "PUBK-5U": {
        "block_no": "PUBK-5U",
        "L1_mm": 290,
        "L3_mm": None,
        "W1_mm": 290,
        "W2_mm": None,
        "W3_mm": None,
        "T1_mm": 100,
        "hole_diameter_mm": None,
        "hole_count": 0,
    },
    "PUBK-6U": {
        "block_no": "PUBK-6U",
        "L1_mm": 340,
        "L3_mm": None,
        "W1_mm": 340,
        "W2_mm": None,
        "W3_mm": None,
        "T1_mm": 100,
        "hole_diameter_mm": None,
        "hole_count": 0,
    },
}


def _normalize_block_no(value) -> str:
    text = str(value).strip().upper()
    if text.startswith("PUBK-"):
        return text
    return f"PUBK-{text}"


def _with_calculated_geometry(row: dict) -> dict:
    resolved = deepcopy(row)
    gross_volume = row["L1_mm"] * row["W1_mm"] * row["T1_mm"]
    hole_volume = 0.0
    if row["hole_count"]:
        hole_volume = (
            row["hole_count"]
            * math.pi
            * (row["hole_diameter_mm"] / 2) ** 2
            * row["T1_mm"]
        )
    net_volume = gross_volume - hole_volume
    resolved.update(
        {
            **deepcopy(N27_COMPONENT_INFO),
            "gross_volume_mm3": gross_volume,
            "hole_volume_mm3": hole_volume,
            "net_volume_mm3": net_volume,
            "unit_weight_kg": (
                net_volume
                / 1_000_000_000
                * N27_COMPONENT_INFO["density_kg_m3"]
            ),
            "hole_centers_mm": _hole_centers(row),
            "fabrication_ready": True,
            "fabrication_blockers": [],
        }
    )
    return resolved


def _hole_centers(row: dict) -> list[dict]:
    if not row["hole_count"]:
        return []
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


def get_n27_pu_block_component() -> dict:
    return {
        **deepcopy(N27_COMPONENT_INFO),
        "designation": "PUBK-{1|2|3|4|5|6|2U|3U|4U|5U|6U}",
        "line_size_range": "selected by host cold-support drawing",
        "notes": [
            "Regular rows are drilled rectangular blocks.",
            "U rows are un-drilled rectangular blocks.",
        ],
    }


def get_n27_pu_block(block_no) -> dict | None:
    row = N27_PU_BLOCK_TABLE.get(_normalize_block_no(block_no))
    return _with_calculated_geometry(row) if row else None
