"""N-11 Expansion Bolt metadata table."""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


N11_TABLE = build_metadata_component(
    component_id="N-11",
    name_en="EXPANSION BOLT",
    category="component_cold",
    pdf_file="N-11-EXPANSION BOLT.pdf",
    summary="Metadata-only intake entry for N-11 expansion bolt.",
    notes=["Cold-service expansion bolt details require PDF visual transcription."],
)


def get_n11_component() -> dict:
    return clone_metadata_component(N11_TABLE)
