"""
N-4 Cold Insulation Protection metadata table.
"""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


N4_TABLE = build_metadata_component(
    component_id="N-4",
    name_en="COLD INSULATION PROTECTION",
    category="component_cold",
    pdf_file="N-4-COLD INSULATION PROTECTION.pdf",
    summary="Metadata-only entry for the cold-support protection/cover sheet.",
)


def get_n4_component() -> dict:
    return clone_metadata_component(N4_TABLE)
