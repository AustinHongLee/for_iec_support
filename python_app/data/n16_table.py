"""N-16 U-band compatibility exports."""

from .cold_interface_tables import (
    N16_COMPONENT_INFO,
    N16_TABLE,
    get_n16_by_cradle,
    get_n16_component,
)

__all__ = [
    "N16_COMPONENT_INFO",
    "N16_TABLE",
    "get_n16_by_cradle",
    "get_n16_component",
]
