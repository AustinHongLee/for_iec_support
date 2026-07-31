"""Type 34 source-aware top cantilever frame (D-39)."""
from ._frame_support_common import calculate_frame


def calculate(fullstring, overrides=None, source_profile=None):
    return calculate_frame("34", fullstring, overrides, source_profile)
