"""N-19 Slide Plate A metadata table."""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


N19_TABLE = build_metadata_component(
    component_id="N-19",
    name_en="SLIDE PLATE A",
    category="component_cold",
    pdf_file="N-19-SLIDE PLATE A.pdf",
    summary="Metadata-only intake entry for N-19 slide plate A.",
    notes=["Cold-service slide plate dimensions and material stack require PDF visual transcription."],
)


def get_n19_component() -> dict:
    return clone_metadata_component(N19_TABLE)
