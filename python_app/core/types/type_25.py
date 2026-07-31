"""Type 25 source-aware cantilever with optional D-68/D-70 or M-34 (D-27)."""
from __future__ import annotations

from ..bolt import add_custom_entry
from ..config_loader import load_config
from ..hardware_material import HardwareKind, parse_hardware_material_context, resolve_hardware_material
from ..issues import add_issue, register_source_envelope
from ..models import AnalysisResult
from ..plate import add_plate_entry
from ..source_profiles import normalize_source_profile
from ..steel import add_steel_section_entry
from ..truth import make_evidence
from data.m34_table import get_m34_by_member
from ._lug_plate_common import lug_hole_count


def _parse(fullstring):
    parts = str(fullstring).split("-")
    if len(parts) not in (3, 4):
        raise ValueError("格式應為 25-{M}-{LL}{HH}{Fig}[-{L1}{L2}]")
    member, token = parts[1].upper(), parts[2]
    if len(token) != 5 or token[-1].upper() not in "ABC" or not token[:4].isdigit():
        raise ValueError("第三段需為2位L+2位H+Fig A/B/C")
    l_mm, h_mm, fig = int(token[:2]) * 100, int(token[2:4]) * 100, token[-1].upper()
    l1 = l2 = None
    if len(parts) == 4:
        if len(parts[3]) != 4 or not parts[3].isdigit():
            raise ValueError("第四段需為2位L1+2位L2")
        l1, l2 = int(parts[3][:2]) * 100, int(parts[3][2:]) * 100
    if min(l_mm, h_mm) <= 0:
        raise ValueError("L與H必須大於0")
    return member, l_mm, h_mm, fig, l1, l2


def calculate(fullstring, overrides=None, source_profile=None):
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}
    config = load_config("25", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 25: 尚未建立來源 profile {profile_id}"
        return result
    try:
        member, l_mm, h_mm, fig, l1, l2 = _parse(fullstring)
    except ValueError as exc:
        result.error = f"Type 25: {exc}"
        return result
    row = config[profile["table"]].get(member)
    if not row:
        result.error = f"Type 25 / {profile_id}: D-27 未表列 MEMBER {member}"
        return result
    if l1 is not None and l1 + l2 != l_mm:
        add_issue(
            result,
            code="DESIGNATION_L1_L2_MISMATCH",
            severity="high",
            message=(
                f"Type 25 / {profile_id}: L1+L2={l1}+{l2}={l1+l2}mm，"
                f"不等於 L={l_mm}mm；BOM仍按L/H暫算，支撐定位須確認"
            ),
            scope="designation_consistency",
            calculation_allowed=True,
            bom_allowed=False,
            fabrication_allowed=False,
            source="D-27",
        )
    if not register_source_envelope(
        result,
        type_label=f"Type 25 / {profile_id}",
        source_ref=f"D-27 {member} L/H(MAX)",
        checks=(
            ("L", l_mm, row["L_MAX"], True),
            ("H", h_mm, row["H_MAX"], True),
        ),
    ):
        return result

    ctx = parse_hardware_material_context(overrides, legacy_material_keys=("material",), legacy_material_kinds=(HardwareKind.STRUCTURAL_STRUT,))
    material = resolve_hardware_material(HardwareKind.STRUCTURAL_STRUT, service=ctx.service, overrides=ctx.material_overrides)
    bolt_material = resolve_hardware_material(HardwareKind.ANCHOR_BOLT, service=ctx.service, overrides=ctx.material_overrides)
    blockers = ["兩段member交接端部切削/貼合輪廓未在D-27完整尺寸化"]
    if l1 is None:
        blockers.append("L1/L2未指定，無法定位supported lines於L段")
    if profile["fire_protection_detail"] and fig == "A":
        blockers.append("Fig-A fire-protection support spacer/no-grating條件未編入designation")

    for cid, segment, length in (("D27-MEMBER-M-L", "L", l_mm), ("D27-MEMBER-M-H", "H", h_mm)):
        add_steel_section_entry(result, row["section_type"], row["lookup_dim"], length, material=material)
        entry = result.entries[-1]
        entry.geometry.component_id = cid
        entry.geometry.source_drawing = profile["drawing"]
        entry.geometry.source_revision = profile["revision"]
        entry.geometry.shape_kind = "stock_section_cut"
        entry.geometry.shape_spec = f'{row["full_spec"]}; CUT {segment}={length}; FIG-{fig}'
        entry.geometry.parameters = {"segment":segment,"L_mm":l_mm,"H_mm":h_mm,"L1_mm":l1,"L2_mm":l2,"figure":fig,"field_fillet_weld_mm":6}
        entry.geometry.fabrication_ready = False
        entry.geometry.fabrication_blockers = blockers[:]

    if fig == "C":
        lug = get_m34_by_member(member)
        if not lug:
            result.error = f"Type 25: M-34無 {member} Lug Plate Type-C"
            result.entries.clear()
            return result
        holes = lug_hole_count(lug)
        add_plate_entry(result, lug["A"], lug["B"], lug["T"], "LUG_PLATE_C", material=material, plate_qty=1, bolt_switch=True, bolt_x=2*lug["E"]+lug["F"], bolt_y=0, bolt_hole=lug["J"], bolt_size=row["K"], plate_role="lug_plate")
        plate = result.entries[-1]
        plate.geometry.component_id = f'M34-{lug["type"]}'
        plate.geometry.source_drawing = "LUG-PLATE_TYPE-C_M-34.pdf"
        plate.geometry.source_revision = "1"
        plate.geometry.shape_kind = "lug_plate_type_c"
        plate.geometry.shape_spec = f'{lug["type"]}; {lug["A"]}x{lug["B"]}x{lug["T"]}t; {holes}-HOLE DIA{lug["J"]}'
        plate.geometry.holes.count = holes
        plate.geometry.parameters.update({"lgp_type":lug["type"],"A_mm":lug["A"],"B_mm":lug["B"],"T_mm":lug["T"],"hole_count":holes,"hole_diameter_mm":lug["J"],"hole_pitch_mm":2*lug["E"]+lug["F"],"G_mm":lug.get("G"),"H_mm":lug.get("H")})
        plate.geometry.fabrication_ready = True
        add_custom_entry(result, name="K BOLT", spec=row["K"], material=bolt_material, quantity=holes, unit_weight=0, unit="PC")
        bolt = result.entries[-1]
        bolt.geometry.component_id = "M34-K-BOLT"
        bolt.geometry.source_drawing = profile["drawing"]
        bolt.geometry.source_revision = profile["revision"]
        bolt.geometry.shape_kind = "purchased_fastener"
        bolt.geometry.parameters = {"spec":row["K"],"quantity":holes}
        bolt.geometry.fabrication_ready = True
        result.warnings.append("D-27/M-34只給K bolt規格與數量，未提供單重")

    result.meta["fabrication"] = {
        "source_profile":profile_id,"source_drawing":profile["drawing"],"source_revision":profile["revision"],
        "branch":f"{member}/FIG-{fig}","bom_ready":True,"fabrication_ready":False,"blockers":blockers,
        "not_furnished": config["fabrication_contract"]["fig_b_not_furnished"] if fig == "B" else [],
    }
    result.evidence.append(make_evidence("type25_row", row, "visual_transcription", source=profile["drawing"], confidence=0.99))
    return result
