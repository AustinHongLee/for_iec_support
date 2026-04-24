"""M-12 Riser Clamp B metadata table."""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


M12_TABLE = build_metadata_component(
    component_id="M-12",
    name_en="RISER CLAMP B",
    category="component",
    pdf_file="M-12-RISER CLAMP B.pdf",
    summary="Metadata-only intake entry for M-12 riser clamp type B.",
    notes=["Referenced by Type 49 FIG-B; current Type 49 still uses custom estimate until this table is transcribed."],
)


def get_m12_component() -> dict:
    return clone_metadata_component(M12_TABLE)
