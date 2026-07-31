"""Type 33 source-aware side cantilever frame (D-38)."""
from ._frame_support_common import calculate_frame


def calculate(fullstring, overrides=None, source_profile=None):
    return calculate_frame("33", fullstring, overrides, source_profile)
