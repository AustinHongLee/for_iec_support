"""
Type 52/53/54/55/66/67 — Pipe Shoe (D-62, D-62A, D-80)

Calculation logic lives in:
  python_app/configs/pipe_shoe_spec.json   <- declarative sizing rules
  python_app/core/pipe_shoe_engine.py      <- thin engine

This file is a dispatcher: extracts the type ID and delegates to the engine.
"""

from core.models import AnalysisResult
from core.parser import get_part
from core import pipe_shoe_engine


def calculate(fullstring: str) -> AnalysisResult:
    type_id = get_part(fullstring, 1)   # "52", "53", ... "67"
    return pipe_shoe_engine.calculate(fullstring, type_id)
