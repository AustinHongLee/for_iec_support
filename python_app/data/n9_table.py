"""
N-9 Lower Component Of Base Cold Support 1 metadata table.
"""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


N9_TABLE = build_metadata_component(
    component_id="N-9",
    name_en="LOWER COMPONENT OF BASE COLD SUPPORT 1",
    category="component_cold",
    pdf_file="N-9-LOWER COMPONENT OF BASE COLD SUPPORT.1.pdf",
    summary="Metadata-only entry for the first lower-base component in the cold-support family.",
)


def get_n9_component() -> dict:
    return clone_metadata_component(N9_TABLE)
