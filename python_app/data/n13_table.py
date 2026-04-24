"""N-13 Vessel Clips metadata table."""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


N13_TABLE = build_metadata_component(
    component_id="N-13",
    name_en="VESSEL CLIPS",
    category="component_cold",
    pdf_file="N-13-VESSEL CLIPS.pdf",
    summary="Metadata-only intake entry for N-13 vessel clips.",
    notes=["Vessel clip dimensions require PDF visual transcription."],
)


def get_n13_component() -> dict:
    return clone_metadata_component(N13_TABLE)
