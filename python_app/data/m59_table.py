"""M-59 U-Band A metadata table."""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


M59_TABLE = build_metadata_component(
    component_id="M-59",
    name_en="U-BAND A",
    category="component",
    pdf_file="M-59-U-BAND A.pdf",
    summary="Metadata-only intake entry for M-59 U-band A.",
    notes=["U-band dimensions and weight require PDF visual transcription."],
)


def get_m59_component() -> dict:
    return clone_metadata_component(M59_TABLE)
