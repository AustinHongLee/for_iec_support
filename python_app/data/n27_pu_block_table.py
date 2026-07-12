"""N27-PU Block metadata table."""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


N27_PU_BLOCK_TABLE = build_metadata_component(
    component_id="N27-PU BLOCK",
    name_en="PU BLOCK",
    category="component_cold",
    pdf_file="N27-PU BLOCK.pdf",
    summary="Metadata-only intake entry for N27 PU block.",
    notes=["Catalog uses non-hyphenated N27 naming; dimensions require PDF visual transcription."],
)


def get_n27_pu_block_component() -> dict:
    return clone_metadata_component(N27_PU_BLOCK_TABLE)
