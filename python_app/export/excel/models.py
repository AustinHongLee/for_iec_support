"""Small data containers used by Excel sheet renderers."""

from dataclasses import dataclass


@dataclass(frozen=True)
class LeaderStatRow:
    item: str
    label: str
    unit: str
    key: str
    criteria: str


@dataclass(frozen=True)
class LeaderHitDetail:
    stat_key: str
    status: str
    category: str
    label: str
    drawing_line_number: str
    serial: str
    source_unit: str
    designation: str
    project_qty: int
    pipe_size: float | None
    amount: float
    unit: str
    matched_detail: str
    material_basis: str
    criteria: str
    note: str = ""
    single_weight: float = 0.0
    project_weight: float = 0.0
    claim_calculation: str = ""
