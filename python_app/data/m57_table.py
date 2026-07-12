"""M-57 Non-Ferrous Pipe Saddle metadata table."""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


M57_TABLE = build_metadata_component(
    component_id="M-57",
    name_en="NON-FERROUS PIPE SADDLE",
    category="component",
    pdf_file="M-57-NON-FERROUS PIPE SADDLE.pdf",
    summary="Metadata-only intake entry for M-57 non-ferrous pipe saddle.",
    notes=["Saddle dimensions and material-specific rules require PDF visual transcription."],
)


def get_m57_component() -> dict:
    return clone_metadata_component(M57_TABLE)
