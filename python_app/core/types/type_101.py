"""Type 101 small-bore connection rib support (D-110)."""

from __future__ import annotations

from ..config_loader import load_config
from ..models import AnalysisResult
from ..parser import extract_parts, get_lookup_value, get_part
from ..source_profiles import normalize_source_profile
from ..truth import make_evidence
from ._source_reference import add_reference


def calculate(
    fullstring: str,
    overrides: dict | None = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    config = load_config("101", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 101: 尚未建立來源 profile {profile_id}"
        return result

    size_token, material_symbol = extract_parts(get_part(fullstring, 2) or "")
    size = get_lookup_value(size_token)
    figure = (get_part(fullstring, 3) or "").upper()
    if size not in [float(value) for value in profile["line_sizes"]]:
        result.error = f'Type 101 / {profile_id}: D-110 限定 1/2"~1-1/2"'
        return result
    if figure != "A":
        result.error = "Type 101: designation 的 figure 只允許 A"
        return result
    if material_symbol not in profile["material_symbols"]:
        result.error = (
            f"Type 101 / {profile_id}: material symbol {material_symbol!r} 無效；"
            f"允許 {sorted(profile['material_symbols'])}"
        )
        return result

    blocker = (
        "D-110 給 6t×50 flat-bar、60°、190 vertical envelope 與 rib 數量，"
        "但 rib 兩端需貼合 main/branch pipe 曲面；缺兩管實際 OD、交角與"
        "cope contour，禁止以 190/sin60 當 finished cut"
    )
    add_reference(
        result,
        name="SMALL-BORE CONNECTION RIB SET",
        spec=f'FB6x50; QTY{profile["rib_count"]}; 60deg; 190H',
        material=profile["material_symbols"][material_symbol],
        quantity=1,
        category="鋼板類",
        component_id="D110-SMALL-BORE-RIB-SET",
        drawing=profile["drawing"],
        revision=profile["revision"],
        shape_kind="pipe_to_pipe_contoured_rib_set",
        parameters={
            "branch_line_size_in": size,
            "rib_count": profile["rib_count"],
            "flat_bar_thickness_mm": 6,
            "flat_bar_width_mm": 50,
            "rib_angle_deg": 60,
            "vertical_envelope_mm": 190,
            "top_offset_mm": 20,
            "plan_spacing_deg": profile["plan_spacing_deg"],
            "material_symbol": material_symbol,
            "location_rule": profile["location_rule"],
        },
        blocker=blocker,
        manufacturing_type="shaped_plate",
    )
    warnings = [blocker, *profile.get("warnings", [])]
    result.warnings.extend(warnings)
    result.meta["type_id"] = "101"
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": profile["drawing"],
        "source_revision": profile["revision"],
        "bom_ready": False,
        "fabrication_ready": False,
        "blockers": warnings,
        "assembly_dimensions": result.entries[0].geometry.parameters,
    }
    result.evidence.append(
        make_evidence(
            "type101_rib_geometry",
            result.meta["fabrication"]["assembly_dimensions"],
            "visual_transcription",
            source=profile["drawing"],
            confidence=0.99,
        )
    )
    return result
