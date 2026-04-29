"""M-31 Steel Washer Plate metadata table."""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


M31_TABLE = build_metadata_component(
    component_id="M-31",
    name_en="STEEL WASHER PLATE",
    category="component",
    pdf_file="M-31-STEEL WASHER PLATE.pdf",
    summary="Metadata-only intake entry for M-31 steel washer plate.",
    notes=["Referenced by Type 62 lower figures; plate dimensions and hole details require PDF review."],
)


def get_m31_component() -> dict:
    return clone_metadata_component(M31_TABLE)
