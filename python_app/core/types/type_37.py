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
from ..models import AnalysisResult
from ..parser import get_part
from ..steel import add_steel_section_entry
from data.steel_sections import get_section_details

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


def calculate(fullstring: str) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)

    # ── 第二段: 型鋼代碼 ──
    part2 = get_part(fullstring, 2)
    # H150 在 Type 37 用 7mm
    details = get_section_details(part2, type_first="37" if part2 == "H150" else "")
    if not details:
        result.error = f"Type 37: 未知型鋼代碼 {part2}"
        return result

    section_type = details["type"]
    full_size = details["size"]

    # ── 第三段: H(mm) + A/B ──
    part3 = get_part(fullstring, 3)
    if not part3 or len(part3) < 2:
        result.error = f"Type 37: 第三段格式錯誤 '{part3}' (需如 1200A 或 800B)"
        return result

    fig_type = part3[-1].upper()
    if fig_type not in ("A", "B"):
        result.error = f"Type 37: FIG 類型必須為 A 或 B, 得到 '{fig_type}'"
        return result

    try:
        h_mm = int(part3[:-1])  # H 直接 mm (非 ×100)
    except ValueError:
        result.error = f"Type 37: 無法解析 H 值 '{part3[:-1]}'"
        return result

    # ── 第四段: C 尺寸 (選填, ×100mm, 預設 200mm) ──
    part4 = get_part(fullstring, 4)
    if part4:
        try:
            c_mm = int(part4) * 100
        except ValueError:
            c_mm = 200
    else:
        c_mm = 200

    # ── 超限檢查 ──
    h_max = _LIMITS.get(part2)
    if not h_max:
        result.error = f"Type 37: {part2} 不在支援清單"
        return result
    if h_mm > h_max:
        result.warnings.append(
            f"H={h_mm}mm 超出 {part2} 標準範圍 (≤ {h_max}mm)"
        )

    # ── 計算斜撐長度 ──
    member_depth = _get_member_depth(part2)
    brace_length = _calc_brace_length(member_depth, h_mm, fig_type)

    section_dim = full_size[1:]  # 去掉前綴字母

    # ═══════════════════════════════════════════════════════
    # ① 上主梁 — 水平懸臂 + C 延伸
    #    VBA: Section_Length_H = H + C
    # ═══════════════════════════════════════════════════════
    beam_length = h_mm + c_mm
    add_steel_section_entry(result, section_type, section_dim, beam_length)
    result.entries[-1].remark = (
        f"上主梁(懸臂), H={h_mm}+C={c_mm}={beam_length}"
    )

    # ═══════════════════════════════════════════════════════
    # ② 斜撐 — 三角函數計算
    #    VBA: Section_Length_L = f(d, H, θ)
    #    VBA 合併成一筆 Total=H_part+L, 此處拆開
    # ═══════════════════════════════════════════════════════
    theta = 30 if fig_type == "A" else 45
    add_steel_section_entry(result, section_type, section_dim, brace_length)
    result.entries[-1].remark = (
        f"斜撐 FIG-{fig_type}(θ={theta}°), L={brace_length}"
    )

    return result
