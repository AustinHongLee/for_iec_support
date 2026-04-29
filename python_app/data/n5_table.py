"""
N-5 Molded Thermaform metadata table.
"""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


N5_TABLE = build_metadata_component(
    component_id="N-5",
    name_en="MODLDED THERMAFORM",
    category="component_cold",
    pdf_file="N-5-MODLDED THERMAFORM.pdf",
    summary="Metadata-only entry for molded Thermaform cold-support filler material.",
)


def get_n5_component() -> dict:
    return clone_metadata_component(N5_TABLE)
