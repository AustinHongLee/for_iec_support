"""Type 84 D-103/D-104 clamped guide support."""

from __future__ import annotations

from ..models import AnalysisResult
from .type_81 import calculate_d81_wrapper


def calculate(
    fullstring: str,
    overrides: dict | None = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    return calculate_d81_wrapper(
        fullstring,
        type_id="84",
        source_profile=source_profile,
        extra_small_reference={
            "name": "GUIDE ANGLE SET",
            "spec": "L40*40*5; CUT LENGTH/PIECE COUNT TBD",
            "material": "A36/SS400",
            "component_id": "D103-GUIDE-ANGLE-SET",
            "shape_kind": "bilateral_guide_angle_set",
            "blocker": (
                "D-103 標示 L40x40x5 guide，但未唯一標出沿管方向 cut length/"
                "完整片數；不可用 LOPS 代替"
            ),
        },
    )
