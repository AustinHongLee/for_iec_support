"""Type 27 source-aware post support with 6t top plate and M-42 (D-30)."""
from __future__ import annotations

from ..bolt import add_custom_entry
from ..bom_policy import exclude_unresolved_entry
from ..config_loader import load_config
from ..hardware_material import HardwareKind, parse_hardware_material_context, resolve_hardware_material
from ..issues import (
    add_issue,
    register_host_m42_variance,
    register_source_envelope,
)
from ..m42 import perform_action_by_letter, source_allows_m42_type
from ..models import AnalysisResult
from ..plate import add_plate_entry
from ..source_profiles import normalize_source_profile
from ..steel import add_steel_section_entry
from ..truth import make_evidence


def _parse(fullstring):
    parts=str(fullstring).split("-")
    if len(parts) not in (3,4) or len(parts[2])!=5 or not parts[2][:4].isdigit() or not parts[2][-1].isalpha():
        raise ValueError("格式應為 27-{M}-{LL}{HH}{M42}[-{L1}{L2}]")
    member=parts[1].upper(); l=int(parts[2][:2])*100; h=int(parts[2][2:4])*100; letter=parts[2][-1].upper()
    l1=l2=None
    if len(parts)==4:
        if len(parts[3])!=4 or not parts[3].isdigit(): raise ValueError("第四段需為2位L1+2位L2")
        l1=int(parts[3][:2])*100; l2=int(parts[3][2:])*100
    return member,l,h,letter,l1,l2


def _positive_override(overrides,key):
    raw=overrides.get(key)
    if raw in (None,""): return None
    value=float(raw)
    if value<=0: raise ValueError(f"{key}必須大於0")
    return value


def _decorate_m42(entries,profile,ready):
    for entry in entries:
        entry.geometry.source_drawing=profile["drawing"]; entry.geometry.source_revision=profile["revision"]; entry.geometry.fabrication_ready=ready
        if entry.category=="鋼板類":
            code=entry.name.split("_")[1].upper(); entry.geometry.component_id=f"M42-PLATE-{code}"; entry.geometry.shape_kind="rectangular_base_plate"; entry.geometry.shape_spec=entry.geometry.shape_spec or f"{entry.length:g}x{entry.width:g}x{entry.spec}t"
        elif entry.category=="螺栓類":
            entry.geometry.component_id="M42-FASTENER"; entry.geometry.shape_kind="purchased_fastener"


def calculate(fullstring,overrides=None,source_profile=None):
    result=AnalysisResult(fullstring=fullstring); overrides=overrides or {}; config=load_config("27",strict=True)
    profile_id=normalize_source_profile(source_profile); profile=config["source_profiles"].get(profile_id)
    if not profile: result.error=f"Type 27: 尚未建立來源 profile {profile_id}"; return result
    try:
        member,l_mm,h_mm,letter,l1,l2=_parse(fullstring); cut=_positive_override(overrides,"member_cut_length_mm"); top_width=_positive_override(overrides,"top_plate_width_mm")
    except ValueError as exc: result.error=f"Type 27: {exc}"; return result
    row=config[profile["table"]].get(member)
    if not row: result.error=f"Type 27 / {profile_id}: D-30未表列 MEMBER {member}"; return result
    if l1 is not None and l1+l2 != l_mm:
        add_issue(result,code="DESIGNATION_L1_L2_MISMATCH",severity="high",message=f"Type 27 / {profile_id}: L1+L2={l1}+{l2}={l1+l2}mm，不等於L={l_mm}mm；BOM暫按L/H計算，定位須確認",scope="designation_consistency",calculation_allowed=True,bom_allowed=False,fabrication_allowed=False,source="D-30")
    if letter not in profile["allowed_m42"]:
        if not source_allows_m42_type(profile_id,letter): result.error=f"Type 27 / {profile_id}: M-42 {letter}不存在於此來源 M-42 圖"; return result
        register_host_m42_variance(result,type_label=f"Type 27 / {profile_id}",source_ref="D-30",letter=letter,host_allowed=profile["allowed_m42"])
    if not register_source_envelope(result,type_label=f"Type 27 / {profile_id}",source_ref=f"D-30 {member} L/H(MAX)",checks=(("L",l_mm,row["L_MAX"],True),("H",h_mm,row["H_MAX"],True))): return result
    ctx=parse_hardware_material_context(overrides,legacy_material_keys=("material",),legacy_material_kinds=(HardwareKind.STRUCTURAL_STRUT,))
    material=resolve_hardware_material(HardwareKind.STRUCTURAL_STRUT,service=ctx.service,overrides=ctx.material_overrides)
    blockers=[]
    if cut is None: blockers.append("D-30 H為組立高度且field cut；缺member_cut_length_mm")
    if top_width is None: blockers.append("6t top plate只標長L，未標plate width")
    if l1 is None: blockers.append("L1/L2未指定，無法定位上板中心")
    if profile["adjustable_joint"]: blockers.append("20E NOTE5可依現場調整兩member joint，未選option")
    add_steel_section_entry(result,row["section_type"],row["lookup_dim"],cut or 0,material=material)
    post=result.entries[-1]; post.geometry.component_id="D30-MEMBER-M"; post.geometry.source_drawing=profile["drawing"]; post.geometry.source_revision=profile["revision"]; post.geometry.shape_kind="vertical_post_field_cut"; post.geometry.shape_spec=f'{row["full_spec"]}; FIELD CUT={cut or "TBD"}'; post.geometry.parameters={"assembly_H_mm":h_mm,"cut_length_mm":cut,"L_mm":l_mm,"L1_mm":l1,"L2_mm":l2,"C_mm":row["C"]}; post.geometry.fabrication_ready=cut is not None; post.geometry.fabrication_blockers=[] if cut else [blockers[0]]
    if cut is None:
        exclude_unresolved_entry(
            result,
            post,
            reason=(
                "D-30 member is field cut；member_cut_length_mm 未提供，"
                "故不以 0 mm 型鋼列入材料 BOM"
            ),
        )
    if top_width is not None:
        add_plate_entry(result,l_mm,top_width,6,"D30-TOP-PLATE",material=material,plate_qty=1,plate_role="support_plate")
    else:
        add_custom_entry(result,name="D30-TOP-PLATE",spec="6t; WIDTH TBD",material=material,quantity=1,unit_weight=0,unit="PC",role="support_plate")
    top=result.entries[-1]; top.geometry.component_id="D30-TOP-PLATE"; top.geometry.source_drawing=profile["drawing"]; top.geometry.source_revision=profile["revision"]; top.geometry.shape_kind="rectangular_top_plate"; top.geometry.shape_spec=f"{l_mm}x{top_width or 'TBD'}x6t"; top.geometry.parameters={"length_L_mm":l_mm,"width_mm":top_width,"thickness_mm":6,"three_side_weld":True,"weld_mm":6}; top.geometry.fabrication_ready=top_width is not None; top.geometry.fabrication_blockers=[] if top_width else ["top plate width未標"]
    if top_width is None:
        exclude_unresolved_entry(
            result,
            top,
            reason=(
                "D-30 top plate width 未標且未提供 top_plate_width_mm，"
                "故不以 0 kg plate placeholder 列入材料 BOM"
            ),
        )
    gusset_needed=profile["gusset_rule"]=="always" or h_mm>=1000
    if gusset_needed:
        points=config["fabrication_contract"]["gusset"]["polygon_points_mm"]
        add_plate_entry(result,100,200,9,"D30-GUSSET-PLATE",material=material,plate_qty=2,plate_role="gusset_plate",net_area_mm2=18750,shape_kind="polygon")
        gus=result.entries[-1]; gus.geometry.component_id="D30-GUSSET-PLATE"; gus.geometry.source_drawing=profile["drawing"]; gus.geometry.source_revision=profile["revision"]; gus.geometry.shape_kind="polygon"; gus.geometry.shape_spec="9t polygon 100x200 with outer height25; QTY2"; gus.geometry.parameters={"polygon_points_mm":points,"thickness_mm":9,"quantity":2,"web_gap_callout_mm":20}; gus.geometry.fabrication_ready=True
    start=len(result.entries); perform_action_by_letter(result,letter,row["full_spec"].replace("X","*"),source_profile=profile_id)
    if result.error: result.entries.clear(); return result
    if not row["m42_exact"]: blockers.append(f"{member}未在M-43精確表列，lower component row為fallback")
    m42_entries=list(result.entries[start:])
    _decorate_m42(m42_entries,profile,row["m42_exact"])
    for entry in m42_entries:
        if entry.category=="螺栓類" and entry.unit_weight<=0:
            exclude_unresolved_entry(
                result,
                entry,
                reason=(
                    f"M-42 fastener {entry.spec} 只有名義直徑、沒有長度；"
                    "不以 0 kg 採購件列入材料 BOM"
                ),
            )
    bom_ready=cut is not None and top_width is not None and row["m42_exact"]
    result.meta["fabrication"]={"source_profile":profile_id,"source_drawing":profile["drawing"],"source_revision":profile["revision"],"branch":f"{member}/M42-{letter}","bom_ready":bom_ready,"fabrication_ready":False,"blockers":blockers,"excluded_bom_components":result.meta.get("excluded_bom_components",[])}
    result.evidence.append(make_evidence("type27_row",row,"visual_transcription",source=profile["drawing"],confidence=0.99))
    return result
