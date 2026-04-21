"""N-12A Vessel Clips metadata table."""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


N12A_TABLE = build_metadata_component(
    component_id="N-12A",
    name_en="VESSEL CLIPS.2",
    category="component_cold",
    pdf_file="N-12A-VESSEL CLIPS.2.pdf",
    summary="Metadata-only intake entry for N-12A vessel clips.",
    notes=["Vessel clip dimensions require PDF visual transcription."],
)


def get_n12a_component() -> dict:
    return clone_metadata_component(N12A_TABLE)
