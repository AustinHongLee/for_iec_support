"""N-16 U-Band metadata table."""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


N16_TABLE = build_metadata_component(
    component_id="N-16",
    name_en="U-BAND.2",
    category="component_cold",
    pdf_file="N-16-U-BAND.2.pdf",
    summary="Metadata-only intake entry for N-16 cold-service U-band.",
    notes=["U-band dimensions require PDF visual transcription."],
)


def get_n16_component() -> dict:
    return clone_metadata_component(N16_TABLE)
