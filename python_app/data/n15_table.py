"""N-15 U-Band metadata table."""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


N15_TABLE = build_metadata_component(
    component_id="N-15",
    name_en="U-BAND.1",
    category="component_cold",
    pdf_file="N-15-U-BAND.1.pdf",
    summary="Metadata-only intake entry for N-15 cold-service U-band.",
    notes=["U-band dimensions require PDF visual transcription."],
)


def get_n15_component() -> dict:
    return clone_metadata_component(N15_TABLE)
