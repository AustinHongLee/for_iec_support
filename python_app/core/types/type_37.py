"""
Type 37 計算器  (判讀來源: D-35M, E1906-DSP-500-006)
格式: 37-C125-1200A  或  37-C125-1200B-05

第二段: 型鋼代碼 (L75, C100, C125, H100, H125, H150)
第三段: H(mm) + 末位字母(A/B)
        數字部分 = H(水平懸臂長) 直接 mm
        末位 A = θ=30°, B = θ=45°
第四段: (選填) C 尺寸 ×100mm, 預設 02 (=200mm)

結構: 斜撐懸臂支撐 (Braced Cantilever) — 焊接 EXISTING SURFACE
────────────────────────────────────────────────────────────

  ELEV:
              ┌─────── H ───────┐ ("C")
  EXISTING    ╔═════════════════╪═══╗   ← 上主梁 (承管)
   SURFACE    ║        θ        │   ║
              ║      ╱          │   ║
              ║    ╱  斜撐      │   ║
              ║  ╱              │   ║
              ╚╱════════════════╛   ║
              6V                   6V

  力傳遞: 管線 → 上梁(H+C) → 斜撐(L) → 牆
  ★ 斜撐承壓, 梁承彎
  ★ θ=30° (A型): 水平力較大, 適合長距離
  ★ θ=45° (B型): 力較均勻, 剛性較高
  ★ 無 M-42, 無螺栓 (全焊接)

VBA 三角函數拆解:
  d = member 深度 (C125→125mm)
  A型 (θ_X=30°, θ_Y=60°):
    斜撐 L = (d + H) / cos(30°) = (d + H) × 2/√3
  B型 (θ_X=45°, θ_Y=45°):
    斜撐 L = d + H × √2

BOM (2 筆, VBA 合併成 1 筆):
  ① 上主梁: length = H + C
  ② 斜撐:   length = L (三角函數計算)

DIMENSIONS TABLE:
  MEMBER "M"      | H MAX
  L75×75×9        | 1450
  C100×50×5       | 1450
  C125×65×6       | 1450
  H100×100×6      | 2050
  H125×125×6.5    | 2050
  H150×150×7      | 2050

NOTE 2: A=θ30°, B=θ45°
"""
import math
from ..config_loader import load_config
from ..hardware_material import HardwareKind, parse_hardware_material_context, resolve_hardware_material
from ..issues import register_source_envelope
from ..models import AnalysisResult, set_remark
from ..source_profiles import normalize_source_profile
from ..steel import add_steel_section_entry
from ..truth import make_evidence

# ── 限制表 ────────────────────────────────────────────────
_LIMITS = {
    "L75":  1450,
    "C100": 1450,
    "C125": 1450,
    "H100": 2050,
    "H125": 2050,
    "H150": 2050,
}

# ── member code → depth (mm) ──────────────────────────────
# 從 code 取出數字部分作為 member 深度
def _get_member_depth(code: str) -> int:
    """L75→75, C125→125, H150→150"""
    num = ""
    for ch in code:
        if ch.isdigit():
            num += ch
    return int(num) if num else 0


def _calc_brace_length(member_depth: float, h_mm: float, fig_type: str) -> float:
    """
    計算斜撐長度 (VBA 4-step 公式, 忠實還原)

    Parameters:
        member_depth: 型鋼深度 d (mm), 如 C125→125
        h_mm: 水平懸臂長 H (mm)
        fig_type: "A" (θ=30°) 或 "B" (θ=45°)

    VBA 公式數學簡化:
        A型: L = (d + H) / cos(30°)
        B型: L = d + H × √2
    """
    d = member_depth
    if fig_type == "A":
        angle_x = 30
        angle_y = 60
    else:
        angle_x = 45
        angle_y = 45

    rad_x = math.radians(angle_x)
    rad_y = math.radians(angle_y)

    # VBA 4-step (忠實還原, 包含 round)
    # Step 1
    first_step = (d / 2) * math.tan(rad_y)
    # Step 2
    half_section = d / 2
    second_step = round(math.sqrt(round(half_section ** 2) + first_step ** 2))
    # Step 3
    third_step = round(math.sqrt((second_step * math.tan(rad_x)) ** 2 + second_step ** 2))
    # Step 4
    forth_step = round(math.sqrt((h_mm * math.tan(rad_x)) ** 2 + h_mm ** 2))

    return round(third_step + forth_step)


def calculate(fullstring: str, overrides=None, source_profile=None) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}
    config = load_config("37", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 37: 尚未建立來源 profile {profile_id}"
        return result
    parts = str(fullstring).split("-")
    if len(parts) not in (3, 4) or len(parts[2]) < 2:
        result.error = "Type 37: 格式應為 37-{M}-{H}{A/B}[-{C×100}]"
        return result
    member = parts[1].upper()
    fig_type = parts[2][-1].upper()
    if fig_type not in ("A", "B"):
        result.error = "Type 37: FIG類型必須為A或B"
        return result
    try:
        h_mm = int(parts[2][:-1])
        c_mm = int(parts[3]) * 100 if len(parts) == 4 else config["fabrication_contract"]["default_C_mm"]
    except ValueError:
        result.error = "Type 37: H/C必須為正整數"
        return result
    row = config[profile["table"]].get(member)
    if not row:
        result.error = f"Type 37 / {profile_id}: D-42未表列 MEMBER {member}"
        return result
    if h_mm <= 0 or c_mm <= 0:
        result.error = f"Type 37 / {profile_id}: H={h_mm}超出{member} 0<H≤{row['H_MAX']}mm，且C需大於0"
        return result
    if not register_source_envelope(
        result,
        type_label=f"Type 37 / {profile_id}",
        source_ref=f"D-42 {member} H(MAX)",
        checks=(("H", h_mm, row["H_MAX"], True),),
    ):
        return result

    member_depth = row["depth"]
    brace_length = _calc_brace_length(member_depth, h_mm, fig_type)
    beam_length = h_mm + c_mm
    ctx = parse_hardware_material_context(
        overrides, legacy_material_keys=("material",),
        legacy_material_kinds=(HardwareKind.STRUCTURAL_STRUT,),
    )
    material = resolve_hardware_material(
        HardwareKind.STRUCTURAL_STRUT, service=ctx.service,
        overrides=ctx.material_overrides,
    )
    blocker = "斜撐兩端切角/貼合輪廓未在D-42完整尺寸化"
    theta = 30 if fig_type == "A" else 45
    for cid, role, length, formula in (
        ("D42-MAIN-BEAM", "上主梁", beam_length, "H + C"),
        ("D42-BRACE", "斜撐", brace_length, f"f(depth,H,{theta}deg)"),
    ):
        add_steel_section_entry(
            result, row["section_type"], row["lookup_dim"], length, material=material
        )
        entry = result.entries[-1]
        entry.geometry.component_id = cid
        entry.geometry.source_drawing = profile["drawing"]
        entry.geometry.source_revision = profile["revision"]
        entry.geometry.shape_kind = "stock_section_cut"
        entry.geometry.shape_spec = f'{row["full_spec"]}; CUT={length}'
        entry.geometry.formula = formula
        entry.geometry.parameters = {
            "H_mm": h_mm, "C_mm": c_mm, "member_depth_mm": member_depth,
            "figure": fig_type, "theta_deg": theta, "fillet_weld_mm": 6,
        }
        entry.geometry.fabrication_ready = cid == "D42-MAIN-BEAM"
        if cid == "D42-BRACE":
            entry.geometry.fabrication_blockers = [blocker]
        set_remark(entry, f"{role}，下料長度{length}mm")
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": profile["drawing"],
        "source_revision": profile["revision"],
        "branch": f"{member}/FIG-{fig_type}",
        "bom_ready": True,
        "fabrication_ready": False,
        "blockers": [blocker],
        "H_mm": h_mm,
        "C_mm": c_mm,
        "brace_length_mm": brace_length,
    }
    result.warnings.append("斜撐BOM長度可算；端切/貼合輪廓仍需加工圖確認")
    result.evidence.append(
        make_evidence("type37_member_row", row, "visual_transcription", source=profile["drawing"], confidence=0.99)
    )
    return result
