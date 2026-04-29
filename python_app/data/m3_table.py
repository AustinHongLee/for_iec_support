"""M-3 Adjustable Clevis metadata table."""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


M3_TABLE = build_metadata_component(
    component_id="M-3",
    name_en="ADJUSTABLE CLEVIS",
    category="component",
    pdf_file="M-3-ADJUSTABLE CLEVIS.pdf",
    summary="Metadata-only intake entry for M-3 adjustable clevis.",
    notes=["Referenced by Type 62 FIG-E; dimensions and nut callouts still require PDF review."],
)


def get_m3_component() -> dict:
    return clone_metadata_component(M3_TABLE)
