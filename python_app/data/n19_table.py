"""N-19 slide-plate compatibility exports."""

from .cold_interface_tables import (
    N19_COMPONENT_INFO,
    get_n19_component,
    resolve_n19_designation,
)

N19_TABLE = N19_COMPONENT_INFO

__all__ = [
    "N19_COMPONENT_INFO",
    "N19_TABLE",
    "get_n19_component",
    "resolve_n19_designation",
]
