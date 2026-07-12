"""N-14 Vessel Clips metadata table."""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


N14_TABLE = build_metadata_component(
    component_id="N-14",
    name_en="VESSEL CLIPS",
    category="component_cold",
    pdf_file="N-14-VESSEL CLIPS.pdf",
    summary="Metadata-only intake entry for N-14 vessel clips.",
    notes=["Vessel clip dimensions require PDF visual transcription."],
)


def get_n14_component() -> dict:
    return clone_metadata_component(N14_TABLE)
