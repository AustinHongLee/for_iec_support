"""N-20 Cradle No. of Cold Support metadata table."""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


N20_TABLE = build_metadata_component(
    component_id="N-20",
    name_en="CRADLE NO. OF COLD SUPPORT.1",
    category="component_cold",
    pdf_file="N-20-CRADLE NO. OF COLD SUPPORT.1.pdf",
    summary="Metadata-only intake entry for N-20 cold-support cradle.",
    notes=["Cradle dimensions require PDF visual transcription."],
)


def get_n20_component() -> dict:
    return clone_metadata_component(N20_TABLE)
