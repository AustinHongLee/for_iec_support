"""
N-7 Special U-Bolt Sub metadata table.
"""
from .component_metadata_registry import build_metadata_component, clone_metadata_component


N7_TABLE = build_metadata_component(
    component_id="N-7",
    name_en="SPECIAL U-BOLT SUB",
    category="component_cold",
    pdf_file="N-7-SPECIAL U-BOLT SUB.pdf",
    summary="Metadata-only entry for the special U-bolt subassembly used by cold supports.",
)


def get_n7_component() -> dict:
    return clone_metadata_component(N7_TABLE)
