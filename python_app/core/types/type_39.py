"""
Type 39 計算器  (判讀來源: D-45, E1906-DSP-500-006)
格式: 39-C100-500 A  或  39-C100-500 B-05

第二段: 型鋼代碼 (L75, C100, C125, C150, C180, C200)
第三段: H(mm) + 空格 + FIG(A/B)
        H = 由 K-R-t-E-30 反算 (mm)
        FIG: A = θ=30°, B = θ=45° (空格隔開)
第四段: (選填) L 修正尺寸 ×100mm, 預設 02 (=200mm)

結構: Vessel 斜撐支撐 (Braced Cantilever) — Bolt + Lug Plate 接 Vessel
────────────────────────────────────────────────────────────

  ELEV:
  TO VESSEL ℄
       │    ├──── H ────┤("L")
       │    │            200 (default)
       │    │            │
       │   S│    LUG PLATE TYPE-C
       │    │      SEE M-34 (DETAIL Y)
       │    │  ╲
       │    │    ╲    N (斜撐)
       │    │      ╲
       │    │   M-35/36 ╲
       │    ▼  (DETAIL Z) ▼

  力傳遞: 管線 → 主梁(H+L) → 斜撐(N) → Lug Plate → Vessel

BOM (5 筆):
  ① 主梁   ×1 — 型鋼, length = H + L
  ② 斜撐   ×1 — 同型鋼, length = N
  ③ LUG PLATE TYPE-C ×1 — M-34 (DETAIL Y, 上部水平接)
  ④ LUG PLATE TYPE-D/E ×1 — M-35 (FIG-B, θ=45°) 或 M-36 (FIG-A, θ=30°) (DETAIL Z)
  ⑤ K BOLT ×2 SET — 3/4"x50
"""
from ..models import AnalysisResult
from ..parser import get_part
from ..steel import add_steel_section_entry
from ..plate import add_plate_entry
from ..bolt import add_custom_entry
from ..hardware_material import (
    HardwareKind,
    HardwareMaterialOverrides,
    resolve_hardware_material,
)
from data.steel_sections import get_section_details
from data.type39_table import get_type39_data, get_type39_formula
from data.m34_table import get_m34_by_member
from data.m35_table import get_m35_by_member
from data.m36_table import get_m36_by_member


def _material_spec(kind: HardwareKind, material_name: str):
    return resolve_hardware_material(
        kind,
        overrides=HardwareMaterialOverrides(per_kind={kind: material_name}),
    )


_STRUCTURAL_MATERIAL = _material_spec(HardwareKind.STRUCTURAL_STRUT, "A36/SS400")
_PLATE_LUG_MATERIAL = _material_spec(HardwareKind.PLATE_LUG, "A36/SS400")
_ANCHOR_BOLT_MATERIAL = _material_spec(HardwareKind.ANCHOR_BOLT, "SUS304")


def calculate(fullstring: str) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)

    # ── 第二段: 型鋼代碼 ──
    part2 = get_part(fullstring, 2)
    details = get_section_details(part2)
    if not details:
        result.error = f"Type 39: 未知型鋼代碼 {part2}"
        return result

    section_type = details["type"]
    full_size = details["size"]

    # ── 第三段: H(mm) + 空格 + FIG(A/B) ──
    # 格式: "500 A" 或 "500 B"
    part3 = get_part(fullstring, 3)
    if not part3:
        result.error = "Type 39: 缺少第三段 (H + FIG)"
        return result

    parts3 = part3.strip().split()
    if len(parts3) != 2:
        result.error = f"Type 39: 第三段格式錯誤 '{part3}' (需如 '500 A' 或 '800 B')"
        return result

    try:
        h_mm = int(parts3[0])
    except ValueError:
        result.error = f"Type 39: 無法解析 H 值 '{parts3[0]}'"
        return result

    fig_type = parts3[1].upper()
    if fig_type not in ("A", "B"):
        result.error = f"Type 39: FIG 類型必須為 A 或 B, 得到 '{fig_type}'"
        return result

    # ── 第四段: L 修正尺寸 (選填, ×100mm, 預設 200mm) ──
    part4 = get_part(fullstring, 4)
    if part4:
        try:
            l_mm = int(part4) * 100
        except ValueError:
            l_mm = 200
    else:
        l_mm = 200

    # ── 查表: 基本尺寸 ──
    t39_data = get_type39_data(part2)
    if not t39_data:
        result.error = f"Type 39: {part2} 不在支援清單 (L75/C100/C125/C150/C180/C200)"
        return result

    # ── 超限檢查 ──
    h_max = t39_data["H_MAX"]
    if h_mm > h_max:
        result.warnings.append(
            f"H={h_mm}mm 超出 {part2} 標準範圍 (≤ {h_max}mm)"
        )

    # ── 查公式表: S / N ──
    formula = get_type39_formula(part2, fig_type)
    if not formula:
        result.error = f"Type 39: 無法查到 {part2} FIG-{fig_type} 的公式"
        return result

    b_val = formula["B"]
    s_val = round(formula["s_coeff"] * h_mm + formula["s_offset"])
    n_val = round(formula["n_coeff"] * h_mm + formula["n_offset"])

    # ── 查 M-34 (DETAIL Y, 上部水平接) ──
    m34 = get_m34_by_member(part2)
    if not m34:
        result.error = f"Type 39: M-34 無 {part2} 對應的 Lug Plate Type-C"
        return result

    # ── 查 M-35 或 M-36 (DETAIL Z, 下部斜向接) ──
    if fig_type == "B":
        # θ=45° → Type-D (M-35)
        m_detail_z = get_m35_by_member(part2)
        detail_z_label = "TYPE-D"
        detail_z_ref = "M-35"
    else:
        # θ=30° → Type-E (M-36)
        m_detail_z = get_m36_by_member(part2)
        detail_z_label = "TYPE-E"
        detail_z_ref = "M-36"

    if not m_detail_z:
        result.error = f"Type 39: {detail_z_ref} 無 {part2} 對應的 Lug Plate {detail_z_label}"
        return result

    section_dim = full_size[1:]  # 去掉前綴字母
    theta = 30 if fig_type == "A" else 45

    # ═══════════════════════════════════════════════════════
    # ① 主梁 — length = H + L
    # ═══════════════════════════════════════════════════════
    beam_length = h_mm + l_mm
    add_steel_section_entry(
        result, section_type, section_dim, beam_length,
        material=_STRUCTURAL_MATERIAL,
    )
    result.entries[-1].remark = (
        f"主梁, H={h_mm}+L={l_mm}={beam_length}"
    )

    # ═══════════════════════════════════════════════════════
    # ② 斜撐 — length = N (公式計算)
    # ═══════════════════════════════════════════════════════
    add_steel_section_entry(
        result, section_type, section_dim, n_val,
        material=_STRUCTURAL_MATERIAL,
    )
    result.entries[-1].remark = (
        f"斜撐 FIG-{fig_type}(θ={theta}°), S={s_val}, N={n_val}"
    )

    # ═══════════════════════════════════════════════════════
    # ③ LUG PLATE TYPE-C — M-34, DETAIL Y (上部水平接)
    # ═══════════════════════════════════════════════════════
    lgp_y = m34["type"]
    add_plate_entry(
        result,
        plate_a=m34["A"],
        plate_b=m34["B"],
        plate_thickness=m34["T"],
        plate_name="LUG PLATE TYPE-C",
        material=_PLATE_LUG_MATERIAL,
        plate_qty=1,
        plate_role="lug_plate",
    )
    result.entries[-1].remark = (
        f"{lgp_y} (DETAIL Y), {m34['A']}x{m34['B']}x{m34['T']}t"
    )

    # ═══════════════════════════════════════════════════════
    # ④ LUG PLATE TYPE-D 或 TYPE-E — DETAIL Z (下部斜向接)
    # ═══════════════════════════════════════════════════════
    lgp_z = m_detail_z["type"]
    add_plate_entry(
        result,
        plate_a=m_detail_z["A"],
        plate_b=m_detail_z["B"],
        plate_thickness=m_detail_z["T"],
        plate_name=f"LUG PLATE {detail_z_label}",
        material=_PLATE_LUG_MATERIAL,
        plate_qty=1,
        plate_role="lug_plate",
    )
    result.entries[-1].remark = (
        f"{lgp_z} (DETAIL Z, {detail_z_ref}), "
        f"{m_detail_z['A']}x{m_detail_z['B']}x{m_detail_z['T']}t"
    )

    # ═══════════════════════════════════════════════════════
    # ⑤ K BOLT — 3/4"x50, ×2 SET (DETAIL Y + DETAIL Z 各一)
    # ═══════════════════════════════════════════════════════
    add_custom_entry(
        result,
        name="K BOLT",
        spec='3/4"x50',
        material=_ANCHOR_BOLT_MATERIAL,
        quantity=2,
        unit_weight=0.8,
        unit="SET",
    )
    result.entries[-1].remark = f"DETAIL Y + DETAIL Z 各 1 SET"

    return result
