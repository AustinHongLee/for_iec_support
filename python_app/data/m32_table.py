"""M-32 Lug Plate A metadata table."""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


M32_TABLE = build_metadata_component(
    component_id="M-32",
    name_en="LUG PLATE A",
    category="component",
    pdf_file="M-32-LUG PLATE A.pdf",
    summary="Metadata-only intake entry for M-32 lug plate A.",
    notes=["Lug plate dimensions and weights require PDF visual transcription."],
)


def get_m32_component() -> dict:
    return clone_metadata_component(M32_TABLE)
