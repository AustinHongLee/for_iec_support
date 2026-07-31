"""N-15 U-band compatibility exports."""

from .cold_interface_tables import (
    N15_COMPONENT_INFO,
    N15_TABLE,
    get_n15_by_cradle,
    get_n15_component,
)

__all__ = [
    "N15_COMPONENT_INFO",
    "N15_TABLE",
    "get_n15_by_cradle",
    "get_n15_component",
]
