"""Type 120 anchor support for non-ferrous pipe (D-133/D-134)."""

from __future__ import annotations

from ..config_loader import load_config
from ..models import AnalysisResult
from ..parser import get_lookup_value, get_part
from ..source_profiles import normalize_source_profile
from ..truth import make_evidence
from ._nonferrous_support_common import (
    add_m57_saddle,
    add_m58_ubolt,
    add_m59_uband,
    add_small_guide_plate,
)
from ._source_reference import add_reference, retire_entry_weight


def _collar_bolt_spec(profile: dict, line_size: float) -> str:
    for row in profile["collar_bolt_groups"]:
        if line_size <= float(row["max_size_in"]):
            return str(row["spec"])
    raise ValueError(f'D-134 collar bolt table未涵蓋 {line_size:g}"')


def calculate(
    fullstring: str,
    overrides: dict | None = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    config = load_config("120", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 120: 尚未建立來源 profile {profile_id}"
        return result
    try:
        size = get_lookup_value((get_part(fullstring, 2) or "").replace("B", ""))
        pipe_od = float(get_part(fullstring, 3) or 0)
    except ValueError:
        result.error = "Type 120 格式應為 120-{LINE}B-{ACTUAL PIPE OD mm}"
        return result
    if pipe_od <= 0:
        result.error = "Type 120: actual non-ferrous pipe OD 必須大於 0 mm"
        return result
    if size not in [float(value) for value in profile["allowed_sizes"]]:
        result.error = f'Type 120: D-133/D-134 未表列 {size:g}"'
        return result

    drawing = profile["geometry_drawing"]
    revision = profile["revision"]
    blockers: list[str] = []
    try:
        m57, saddle_blockers = add_m57_saddle(
            result,
            line_size=size,
            pipe_od_mm=pipe_od,
            drawing=drawing,
            revision=revision,
            component_prefix="D133",
        )
        blockers.extend(saddle_blockers)
        saddle_shell = next(
            entry
            for entry in result.entries
            if entry.geometry.component_id
            == "D133-M57-ROLLED-SADDLE-HALVES"
        )
        saddle_fit_blocker = (
            "D-133 明示 M-57 lower half 需 CUT 3MM FOR WELD；"
            "標準 M-57 中性層展開可作母材參考，但 Type 120 finished "
            "saddle cut/淨重需先建立該局部切除輪廓"
        )
        retire_entry_weight(saddle_shell, blocker=saddle_fit_blocker)
        blockers.append(saddle_fit_blocker)
        if size <= 8:
            _, ubolt_blockers = add_m58_ubolt(
                result,
                line_size=size,
                pipe_od_mm=pipe_od,
                drawing=drawing,
                revision=revision,
                component_prefix="D133",
            )
            blockers.extend(ubolt_blockers)
            add_small_guide_plate(
                result,
                line_size=size,
                pipe_od_mm=pipe_od,
                row=profile["small_rows"][f"{size:g}"],
                drawing=drawing,
                revision=revision,
                component_prefix="D133",
            )
            branch = "M-58 U-BOLT / TWO-HOLE PLATE"
        else:
            _, uband_blockers = add_m59_uband(
                result,
                line_size=size,
                pipe_od_mm=pipe_od,
                drawing=drawing,
                revision=revision,
                component_prefix="D133",
            )
            blockers.extend(uband_blockers)
            uband = next(
                entry
                for entry in result.entries
                if entry.geometry.component_id == "D133-M59-U-BAND"
            )
            uband_fit_blocker = (
                "D-133 對 M-59 明記 CUT TO SUIT；不能直接使用標準 "
                "M-59 full neutral development 作 Type 120 finished cut/重量"
            )
            retire_entry_weight(uband, blocker=uband_fit_blocker)
            blockers.append(uband_fit_blocker)
            branch = "M-59 U-BAND"
    except (KeyError, ValueError) as exc:
        result.error = f"Type 120: {exc}"
        return result

    dims = m57["dimensions_mm"]
    h_mm = dims["H"]
    e_mm = pipe_od / 2 + 2 * h_mm
    f_mm = 1.5 * h_mm
    collar_bolt_spec = _collar_bolt_spec(profile, size)
    collar_blocker = (
        "D-134 Detail X 的 steel collar/pour shoulder 是沿管向多段複合輪廓；"
        "E/F/H 與 collar 厚 T+3 已知，但 shoulder taper、分片、實際 W tolerance "
        "及 field pour scope 未形成完整 cutting recipe"
    )
    add_reference(
        result,
        name="ANCHOR COLLAR / POUR-SHOULDER ASSEMBLY",
        spec=(
            f"COLLAR {dims['T'] + 3}t; E={e_mm:.3f}; "
            f"F={f_mm:.3f}; H={h_mm}"
        ),
        material="CARBON STEEL GRADE NOT SPECIFIED / FIELD POUR MATERIAL TBD",
        quantity=1,
        category="鋼板類",
        component_id="D134-ANCHOR-COLLAR-ASSEMBLY",
        drawing=profile["detail_drawing"],
        revision=revision,
        shape_kind="composite_anchor_collar_pour_shoulder",
        parameters={
            "line_size_in": size,
            "actual_pipe_od_mm": pipe_od,
            "saddle_W_mm": dims["W"],
            "saddle_T_mm": dims["T"],
            "collar_thickness_mm": dims["T"] + 3,
            "bolt_hole_H_mm": h_mm,
            "E_mm": e_mm,
            "F_mm": f_mm,
            "collar_machine_bolt_J": collar_bolt_spec,
            "collar_machine_bolt_quantity": 2,
        },
        blocker=collar_blocker,
        manufacturing_type="shaped_plate",
    )
    blockers.append(collar_blocker)
    collar_bolt_blocker = (
        "D-134 釋出 collar machine-bolt 尺寸與兩處接點，但未給 bolt/nut "
        "material grade、nut scope 或 finished unit-weight；保留零重量採購 reference"
    )
    add_reference(
        result,
        name="D-134 COLLAR MACHINE BOLT / NUT SET",
        spec=f"{collar_bolt_spec}; QTY2",
        material="GRADE / NUT SCOPE NOT SPECIFIED IN D-134",
        quantity=2,
        category="螺栓類",
        component_id="D134-COLLAR-MACHINE-BOLTS",
        drawing=profile["detail_drawing"],
        revision=revision,
        shape_kind="purchased_collar_machine_bolt_set",
        parameters={
            "line_size_in": size,
            "bolt_spec": collar_bolt_spec,
            "quantity": 2,
            "hole_diameter_H_mm": h_mm,
            "joint_basis": "two opposed collar joints shown in D-134 SECTION A-A",
        },
        blocker=collar_bolt_blocker,
        manufacturing_type="purchased",
    )
    blockers.append(collar_bolt_blocker)

    result.warnings.extend(blockers)
    result.meta["type_id"] = "120"
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": f"{drawing} / {profile['detail_drawing']}",
        "source_revision": revision,
        "branch": branch,
        "bom_ready": False,
        "fabrication_ready": False,
        "blockers": blockers,
        "assembly_dimensions": {
            "line_size_in": size,
            "actual_pipe_od_mm": pipe_od,
            "anchor_E_mm": e_mm,
            "anchor_F_mm": f_mm,
            "anchor_H_mm": h_mm,
        },
    }
    result.evidence.append(
        make_evidence(
            "type120_d133_d134_branch",
            result.meta["fabrication"]["assembly_dimensions"],
            "visual_transcription",
            source=f"{drawing} / {profile['detail_drawing']}",
            confidence=0.99,
        )
    )
    return result
