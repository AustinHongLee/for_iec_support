"""N-6 special-base-plate source lookup."""

from .cold_restraint_tables import N6_COMPONENT, get_n6_component


N6_TABLE = N6_COMPONENT

__all__ = ["N6_TABLE", "get_n6_component"]
