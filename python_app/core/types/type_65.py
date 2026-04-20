"""
Type 65 計算器 — Trapeze Hanger with Cross Member
圖號: D-79
格式: 65-{D}B-{LLHH}
例: 65-6B-1505 → D=6", L=1500mm, H=500mm
D = equivalent line size
L = LL × 100 mm (500/1000/1500/2000/2500)
H = HH × 100 mm
"""
from ..models import AnalysisResult
from ..parser import get_part, get_lookup_value
from ..steel import add_steel_section_entry
from ..bolt import add_custom_entry
from data.type65_table import (
    get_type65_data, snap_l_bucket, ROD_WEIGHT_PER_M,
)


def _parse_member_spec(member_str: str):
    """解析 member 字串如 'L75*75*9' → ('Angle', '75*75*9')
    或 'C125*65*6' → ('Channel', '125*65*6')"""
    if member_str.startswith("L"):
        return "Angle", member_str[1:]
    elif member_str.startswith("C"):
        return "Channel", member_str[1:]
    elif member_str.startswith("H"):
        return "H Beam", member_str[1:]
    return "Angle", member_str


def calculate(fullstring: str) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)

    # ── 解析: 65-{D}B-{LLHH} ──
    part2 = get_part(fullstring, 2)  # {D}B
    part3 = get_part(fullstring, 3)  # {LLHH}

    if not part2 or not part3:
        result.error = "格式錯誤，應為 65-{D}B-{LLHH}"
        return result

    d_str = part2.replace("B", "").strip()
    d_size = get_lookup_value(d_str)

    # 拆 LLHH (4 digits)
    p3 = part3.strip()
    if len(p3) != 4 or not p3.isdigit():
        result.error = f"LLHH 應為 4 位數字，實際='{p3}'"
        return result

    ll = int(p3[:2])
    hh = int(p3[2:])
    l_mm = ll * 100
    h_mm = hh * 100

    if h_mm < 300:
        result.error = f"H={h_mm}mm 過短"
        return result

    # ── 查表 ──
    data = get_type65_data(d_str)
    if not data:
        result.error = f"管徑 {d_str}\" 不在 Type 65 查詢表中 (2\"~24\")"
        return result

    rod_size = data["rod_size"]

    # L bucket
    l_bucket = snap_l_bucket(l_mm)
    if not l_bucket:
        result.error = f"L={l_mm}mm 超出最大值 2500mm"
        return result

    member_spec = data["member_by_l"].get(l_bucket)
    if not member_spec:
        result.error = f"L bucket={l_bucket}mm 無對應 member"
        return result

    if l_mm != l_bucket:
        result.warnings.append(f"L={l_mm}mm 取至標準 bucket {l_bucket}mm")

    material = "A36/SS400"

    # ① Cross Member ×1 (依 L bucket)
    sec_type, sec_dim = _parse_member_spec(member_spec)
    add_steel_section_entry(result, sec_type, sec_dim, l_mm, 1, material)

    # ② Welded Eye Rod ×2 (M-23), 長度 ≈ H
    rod_wt_m = ROD_WEIGHT_PER_M.get(rod_size, 1.0)
    rod_unit_wt = round(rod_wt_m * (h_mm / 1000.0), 2)
    add_custom_entry(
        result, "WELDED EYE ROD",
        f"M-23, {rod_size}, L={h_mm}mm",
        material, 2, rod_unit_wt, "PC"
    )

    # ③ Angle Bracket ×2 (M-28)
    # M-28 table 由 Codex 施工中，先以估算佔位
    bracket_wt = 0.8 if d_size <= 8 else 1.5
    add_custom_entry(
        result, "ANGLE BRACKET",
        f"M-28, {rod_size}",
        material, 2, bracket_wt, "SET"
    )

    # ④ Stiffener (D ≥ 12")
    if d_size >= 12:
        # stiffener 板尺寸待精確化，先以 custom entry 佔位
        add_custom_entry(
            result, "STIFFENER",
            f"PL for {d_str}\"",
            material, 1, 2.0, "SET"
        )
        result.warnings.append("12\" & larger: Stiffener 重量為估算值")

    return result
