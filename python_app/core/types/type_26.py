"""Type 26 source-aware rectangular cantilever frame (D-28/D-29)."""
from __future__ import annotations

from ..bolt import add_custom_entry
from ..config_loader import load_config
from ..hardware_material import HardwareKind, parse_hardware_material_context, resolve_hardware_material
from ..issues import register_source_envelope
from ..models import AnalysisResult, set_remark
from ..plate import add_plate_entry
from ..source_profiles import normalize_source_profile
from ..steel import add_steel_section_entry
from ..truth import make_evidence
from data.m34_table import get_m34_by_member
from ._lug_plate_common import lug_hole_count


def _parse(fullstring):
    parts = str(fullstring).split("-")
    if len(parts) != 3 or len(parts[2]) != 5 or not parts[2][:4].isdigit() or parts[2][-1].upper() not in "ABC":
        raise ValueError("格式應為 26-{M}-{LL}{HH}{Fig}")
    return parts[1].upper(), int(parts[2][:2])*100, int(parts[2][2:4])*100, parts[2][-1].upper()


def _optional_pipe_size(overrides):
    raw = overrides.get("equivalent_pipe_size_in")
    if raw in (None, ""):
        return None
    value = float(raw)
    if value <= 0:
        raise ValueError("equivalent_pipe_size_in必須大於0")
    return value


def calculate(fullstring, overrides=None, source_profile=None):
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}
    config = load_config("26", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 26: 尚未建立來源 profile {profile_id}"
        return result
    try:
        member, l_mm, h_mm, fig = _parse(fullstring)
        pipe_size = _optional_pipe_size(overrides)
    except ValueError as exc:
        result.error = f"Type 26: {exc}"
        return result
    row = config[profile["table"]].get(member)
    if not row:
        result.error = f"Type 26 / {profile_id}: D-29 未表列 MEMBER {member}"
        return result
    envelope = profile["global_envelope"]
    if envelope:
        if l_mm <= envelope["L_MIN_EXCLUSIVE"]:
            result.error = f"Type 26 / {profile_id}: L/H={l_mm}/{h_mm} 超出 500<L≤1000、H≤1500"
            return result
        checks = (
            ("L", l_mm, envelope["L_MAX"], True),
            ("H", h_mm, envelope["H_MAX"], True),
        )
        source_ref = "D-29 500<L≤1000、H≤1500"
    else:
        checks = (
            ("L", l_mm, row["L_MAX"], True),
            ("H", h_mm, row["H_MAX"], True),
        )
        source_ref = f"D-28 {member} L/H(MAX)"
    if not register_source_envelope(
        result,
        type_label=f"Type 26 / {profile_id}",
        source_ref=source_ref,
        checks=checks,
    ):
        return result
    selection_blocker = None
    if profile_id == "ctci_20e4588" and fig == "B":
        if pipe_size is None:
            selection_blocker = "Fig-B缺equivalent_pipe_size_in，無法核對D-29 down-stop member selection"
        else:
            group = "le4" if pipe_size <= 4 else "6_8" if pipe_size <= 8 else None
            if group is None:
                result.error = f'Type 26 / 20E: equivalent pipe size {pipe_size:g}" 超出D-29 8"'
                return result
            band = "H_LE_1000" if h_mm <= 1000 else "H_GT_1000"
            expected = config["DOWN_STOP_SELECTION_20E"][group][band]
            if expected is None:
                result.error = f'Type 26 / 20E: D-29未提供 pipe≤4", H≤1000 的down-stop member'
                return result
            if member != expected:
                result.error = f"Type 26 / 20E: D-29 down-stop應選 {expected}，不是 {member}"
                return result

    ctx = parse_hardware_material_context(overrides, legacy_material_keys=("material",), legacy_material_kinds=(HardwareKind.STRUCTURAL_STRUT,))
    material = resolve_hardware_material(HardwareKind.STRUCTURAL_STRUT, service=ctx.service, overrides=ctx.material_overrides)
    bolt_material = resolve_hardware_material(HardwareKind.ANCHOR_BOLT, service=ctx.service, overrides=ctx.material_overrides)
    blockers = ["框架四角接頭端切/貼合輪廓與15mm callout製程解讀尚未完整"]
    if selection_blocker:
        blockers.append(selection_blocker)
    if profile["fire_protection_detail"] and fig == "A":
        blockers.append("Fig-A fire-protection support spacer/no-grating條件未編入designation")
    drawing = " / ".join(profile["drawings"])
    for cid, segment, length, role in (
        ("D28-MEMBER-M-H-UPPER","H",h_mm,"H段上件"),
        ("D28-MEMBER-M-H-LOWER","H",h_mm,"H段下件"),
        ("D28-MEMBER-M-L-END","L",l_mm,"L段"),
    ):
        add_steel_section_entry(result,row["section_type"],row["lookup_dim"],length,material=material)
        entry=result.entries[-1]
        entry.geometry.component_id=cid; entry.geometry.source_drawing=drawing; entry.geometry.source_revision=profile["revision"]
        entry.geometry.shape_kind="stock_section_cut"; entry.geometry.shape_spec=f'{row["full_spec"]}; CUT {segment}={length}; FIG-{fig}'
        entry.geometry.parameters={"segment":segment,"L_mm":l_mm,"H_mm":h_mm,"figure":fig,"field_fillet_weld_mm":6,"joint_overlap_callout_mm":15,"equivalent_pipe_size_in":pipe_size}
        entry.geometry.fabrication_ready=False; entry.geometry.fabrication_blockers=blockers[:]
        set_remark(entry, f"Fig-{fig}, {role}", f"Fig-{fig}, {role}")
    if fig=="C":
        lug=get_m34_by_member(member)
        if not lug:
            result.error=f"Type 26: M-34無 {member} Lug Plate Type-C"; result.entries.clear(); return result
        holes_per_plate=lug_hole_count(lug); total_holes=holes_per_plate*2
        add_plate_entry(result,lug["A"],lug["B"],lug["T"],"LUG_PLATE_C",material=material,plate_qty=2,bolt_switch=True,bolt_x=2*lug["E"]+lug["F"],bolt_y=2*(lug.get("G") or 0),bolt_hole=lug["J"],bolt_size=row["K"],plate_role="lug_plate")
        plate=result.entries[-1]; plate.geometry.component_id=f'M34-{lug["type"]}'; plate.geometry.source_drawing="LUG-PLATE_TYPE-C_M-34.pdf"; plate.geometry.source_revision="1"; plate.geometry.shape_kind="lug_plate_type_c"; plate.geometry.shape_spec=f'{lug["type"]}; {lug["A"]}x{lug["B"]}x{lug["T"]}t; {holes_per_plate}-HOLE DIA{lug["J"]}; QTY2'; plate.geometry.holes.count=holes_per_plate; plate.geometry.parameters.update({"lgp_type":lug["type"],"hole_count_per_plate":holes_per_plate,"quantity":2,"G_mm":lug.get("G"),"H_mm":lug.get("H")}); plate.geometry.fabrication_ready=True
        add_custom_entry(result,name="K BOLT",spec=row["K"],material=bolt_material,quantity=total_holes,unit_weight=0,unit="PC")
        bolt=result.entries[-1]; bolt.geometry.component_id="M34-K-BOLT"; bolt.geometry.source_drawing=drawing; bolt.geometry.source_revision=profile["revision"]; bolt.geometry.shape_kind="purchased_fastener"; bolt.geometry.parameters={"spec":row["K"],"quantity":total_holes}; bolt.geometry.fabrication_ready=True
        result.warnings.append("D-29/M-34只給K bolt規格與數量，未提供單重")
    result.meta["fabrication"]={"source_profile":profile_id,"source_drawing":drawing,"source_revision":profile["revision"],"branch":f"{member}/FIG-{fig}","bom_ready":selection_blocker is None,"fabrication_ready":False,"blockers":blockers,"not_furnished":config["fabrication_contract"]["fig_b_not_furnished"] if fig=="B" else []}
    result.evidence.append(make_evidence("type26_row",row,"visual_transcription",source=drawing,confidence=0.99))
    return result
