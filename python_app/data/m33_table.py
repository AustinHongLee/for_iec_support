"""M-33 Lug Plate B metadata table."""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


M33_TABLE = build_metadata_component(
    component_id="M-33",
    name_en="LUG PLATE B",
    category="component",
    pdf_file="M-33-LUG PLATE B.pdf",
    summary="Metadata-only intake entry for M-33 lug plate B.",
    notes=["Referenced by Type 62 lower figures; lug dimensions and weights require PDF review."],
)


def get_m33_component() -> dict:
    return clone_metadata_component(M33_TABLE)
