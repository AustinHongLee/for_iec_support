"""Type 86 D-107/D-108 clamp-on-pipe-shoe wrapper."""

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
        type_id="86",
        source_profile=source_profile,
    )
