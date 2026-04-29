"""M-60 Slide Plate A metadata table."""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


M60_TABLE = build_metadata_component(
    component_id="M-60",
    name_en="SLIDE PLATE A",
    category="component",
    pdf_file="M-60-SLIDE PLATE A.pdf",
    summary="Metadata-only intake entry for M-60 slide plate A.",
    notes=["Slide plate dimensions, material stack, and weight require PDF visual transcription."],
)


def get_m60_component() -> dict:
    return clone_metadata_component(M60_TABLE)
