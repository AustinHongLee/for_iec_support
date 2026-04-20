"""
Type 64 計算器 — Pipe-to-Pipe Rod Hanger
圖號: D-78
格式: 64-{E}-{F}-{HH}{FIG}
例: 64-2-8-05A, 64-6-12-15C
E = supported line size, F = supporting line size
H = HH × 100 mm (500~3000)
FIG = A/B/C/D (決定 upper/lower clamp 類型)
"""
from ..models import AnalysisResult
from ..parser import get_part, get_lookup_value
from ..bolt import add_custom_entry
from data.type64_table import (
    get_type64_rod, get_type64_figure,
    ROD_WEIGHT_PER_M, EYE_NUT_WEIGHT,
)


def calculate(fullstring: str) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)

    # ── 解析: 64-{E}-{F}-{HH}{FIG} ──
    part2 = get_part(fullstring, 2)  # E (supported)
    part3 = get_part(fullstring, 3)  # F (supporting)
    part4 = get_part(fullstring, 4)  # {HH}{FIG}

    if not part2 or not part3 or not part4:
        result.error = "格式錯誤，應為 64-{E}-{F}-{HH}{FIG}"
        return result

    e_str = part2.replace("B", "").strip()
    f_str = part3.replace("B", "").strip()
    e_size = get_lookup_value(e_str)
    f_size = get_lookup_value(f_str)

    # 拆 HH 和 FIG
    p4 = part4.strip()
    fig = ""
    hh_str = ""
    if p4 and p4[-1].isalpha():
        fig = p4[-1].upper()
        hh_str = p4[:-1]
    else:
        result.error = f"無法辨識 FIG，part4='{p4}'"
        return result

    if not hh_str.isdigit():
        result.error = f"無法解析 H 值，HH='{hh_str}'"
        return result

    h_mm = int(hh_str) * 100

    # ── 驗證 ──
    if h_mm < 500 or h_mm > 3000:
        result.error = f"H={h_mm}mm 超出範圍 (500~3000)"
        return result

    if f_size <= e_size:
        result.warnings.append(
            f"⚠ Supporting line ({f_str}\") 不應小於 Supported line ({e_str}\")"
        )

    # ── 查表 ──
    rod_info = get_type64_rod(e_str)
    if not rod_info:
        result.error = f"Supported size {e_str}\" 不在 Type 64 查詢表中"
        return result

    fig_info = get_type64_figure(fig)
    if not fig_info:
        result.error = f"FIG-{fig} 無效 (應為 A/B/C/D)"
        return result

    # 檢查 fig_bc_only
    if rod_info["fig_bc_only"] and fig not in ("B", "C"):
        result.warnings.append(
            f"管徑 {e_str}\" 圖面標記僅適用 FIG-B/C, 目前選用 FIG-{fig}"
        )

    rod_size = rod_info["g"]
    rod_wt_m = ROD_WEIGHT_PER_M.get(rod_size, 1.0)
    eye_nut_wt = EYE_NUT_WEIGHT.get(rod_size, 0.2)

    # ① Threaded Rod ×2 (M-22), 長度 ≈ H
    rod_length_m = h_mm / 1000.0
    rod_unit_wt = round(rod_wt_m * rod_length_m, 2)
    add_custom_entry(
        result, "THREADED ROD",
        f"M-22, {rod_size}, L={h_mm}mm",
        "A36/SS400", 2, rod_unit_wt, "PC"
    )

    # ② Weldless Eye Nut ×2 (M-25)
    add_custom_entry(
        result, "WELDLESS EYE NUT",
        f"M-25, {rod_size}",
        "A36/SS400", 2, eye_nut_wt, "PC"
    )

    # ③ Upper Clamp ×1 set
    add_custom_entry(
        result, "UPPER CLAMP",
        f"{fig_info['upper_clamp']}, {f_str}\"",
        "A36/SS400", 1, 0.5 if e_size <= 4 else 1.5, "SET"
    )

    # ④ Lower Clamp ×1 set
    add_custom_entry(
        result, "LOWER CLAMP",
        f"{fig_info['lower_clamp']}, {e_str}\"",
        "A36/SS400", 1, 0.5 if e_size <= 4 else 1.5, "SET"
    )

    result.warnings.append(
        "Clamp 重量為估算值, 待 M-4/M-6 table 完成後可精確化"
    )

    return result
