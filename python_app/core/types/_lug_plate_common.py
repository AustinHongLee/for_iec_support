"""Shared M-34/M-35/M-36 lug-plate geometry rules."""
from __future__ import annotations


def lug_hole_count(row: dict) -> int:
    """Return the standard drawing's four- or six-hole layout."""
    return 4 if row.get("D") is not None else 6
