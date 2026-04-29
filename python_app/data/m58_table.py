"""M-58 U-Bolt A metadata table."""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


M58_TABLE = build_metadata_component(
    component_id="M-58",
    name_en="U-BOLT A",
    category="component",
    pdf_file="M-58-U-BOLT A.pdf",
    summary="Metadata-only intake entry for M-58 U-bolt A.",
    notes=["U-bolt dimensions and weight require PDF visual transcription."],
)


def get_m58_component() -> dict:
    return clone_metadata_component(M58_TABLE)
