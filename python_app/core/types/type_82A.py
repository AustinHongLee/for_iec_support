"""Type 82A fixed variant of the D-99/D-100 support family."""

from __future__ import annotations

from ..models import AnalysisResult
from .type_82 import calculate_family


def calculate(
    fullstring: str,
    overrides: dict | None = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    return calculate_family(
        fullstring,
        type_id="82A",
        source_profile=source_profile,
    )
