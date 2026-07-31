"""Type 31 source-aware upstand frame (D-36)."""
from ._frame_support_common import calculate_frame


def calculate(fullstring, overrides=None, source_profile=None):
    return calculate_frame("31", fullstring, overrides, source_profile)
