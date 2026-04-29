"""
N-1 Cold Insulation Support metadata table.
"""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


N1_TABLE = build_metadata_component(
    component_id="N-1",
    name_en="COLD INSULATION SUPPORT",
    category="component_cold",
    pdf_file="N-1-COLD INSULATION SUPPORT.pdf",
    summary="Metadata-only intake entry for the cold-support master/support definition sheet.",
    notes=["Cold-support family dimensions are pending manual PDF transcription."],
)


def get_n1_component() -> dict:
    return clone_metadata_component(N1_TABLE)
