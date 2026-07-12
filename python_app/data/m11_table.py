"""M-11 Riser Clamp A metadata table."""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


M11_TABLE = build_metadata_component(
    component_id="M-11",
    name_en="RISER CLAMP A",
    category="component",
    pdf_file="M-11-RISER CLAMP A.pdf",
    summary="Metadata-only intake entry for M-11 riser clamp type A.",
    notes=["Referenced by Type 49 FIG-A; current Type 49 still uses custom estimate until this table is transcribed."],
)


def get_m11_component() -> dict:
    return clone_metadata_component(M11_TABLE)
