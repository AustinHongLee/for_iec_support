"""Type 32 source-aware hanger frame (D-37)."""
from ._frame_support_common import calculate_frame


def calculate(fullstring, overrides=None, source_profile=None):
    return calculate_frame("32", fullstring, overrides, source_profile)
