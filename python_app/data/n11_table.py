"""N-11 expansion-bolt compatibility exports."""

from .cold_interface_tables import (
    N11_COMPONENT_INFO,
    N11_TABLE,
    get_n11_by_size,
    get_n11_component,
)

__all__ = [
    "N11_COMPONENT_INFO",
    "N11_TABLE",
    "get_n11_by_size",
    "get_n11_component",
]
