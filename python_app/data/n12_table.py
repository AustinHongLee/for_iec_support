"""N-12 Vessel Clips metadata table."""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


N12_TABLE = build_metadata_component(
    component_id="N-12",
    name_en="VESSEL CLIPS.1",
    category="component_cold",
    pdf_file="N-12-VESSEL CLIPS.1.pdf",
    summary="Metadata-only intake entry for N-12 vessel clips.",
    notes=["Vessel clip dimensions require PDF visual transcription."],
)


def get_n12_component() -> dict:
    return clone_metadata_component(N12_TABLE)
