"""
Type 28 計算器  (判讀來源: D-31, E1906-DSP-500-006)
格式: 28-L50-1005L

第二段: 型鋼代碼 (L50, L75, C125, C150)
第三段: LL+HH+M42Letter
        前2位 = L(橫梁跨距) ×100mm
        後2位 = H(支腿高度, TO GRADE OR FDN) ×100mm
        末1位 = M-42 下部組件型式字母 (NOTE 4: USE TYPE-L & P ONLY)

結構: 門型支撐 (Portal Frame)
────────────────────────────────────────────────────────────

  ELEV:
       ┌──── L ────┐
       │            │
   H   │  MEMBER"M" │   H
       │            │
       └────────────┘
     WELD TO PLATE     WELD TO PLATE
     (SEE NOTE 4)      (SEE NOTE 4)

  力傳遞: 管線 → 上橫梁 → 左右支腿 → M-42 底板 → 基礎

  門型框架由一根 MEMBER 折/焊構成:
    左腿(H) + 橫梁(L) + 右腿(H) = 2H + L

  圖面標示 "FOR CHANNEL" — C125/C150 用槽鋼; L50/L75 用角鐵

使用模式 (D-31 圖面左右兩視圖):
  - FOR HOR. LINE (左側圖): 水平管放置於門型橫梁上方
    → Channel(C125/C150) 開口朝外, 管線置於凹槽內較穩定
  - FOR VERTICAL LINE (右側圖): 垂直管以 U-BOLT(D-68) 側掛夾持
    → Angle(L50/L75) 截面 L 型, 適合搭配 U-bolt 側掛
  ※ STANDARD U-BOLT(D-68) (NOT FURNISHED) — U-bolt 不含在本 Type BOM 內

BOM (所有 MEMBER 共通, 無板件):
  ① MEMBER "M" ×1  Total_Length = 2H + L
  ② M-42 lower component ×1 set

DIMENSIONS TABLE (D-31):
  MEMBER "M"    | L MAX | H MAX
  L50×50×6      | 1000  |  500
  L75×75×9      | 1000  | 1500
  C125×65×6     | 1500  | 1500
  C150×75×9     | 1500  | 1500

NOTE 1: "H" & "L" SHALL BE CUT TO SUIT IN FIELD.
NOTE 3: IF THE FOUNDATION IS NOT USED, "H" = FROM LOWEST POINT OF PAVING.
NOTE 4: THIS TYPE SHALL BE USED WITH M-42. USE TYPE-L & P ONLY.

VBA BUG: Section_Length_L 漏乘 * 100，導致 L 值差 100 倍。
         Python 版已修正。
"""
from ..models import AnalysisResult
from ..parser import get_part
from ..steel import add_steel_section_entry
from ..m42 import perform_action_by_letter
from data.steel_sections import get_section_details

# ── D-31 限制表 ──────────────────────────────────────────
_LIMITS = {
    "L50":  {"L_max": 1000, "H_max":  500},
    "L75":  {"L_max": 1000, "H_max": 1500},
    "C125": {"L_max": 1500, "H_max": 1500},
    "C150": {"L_max": 1500, "H_max": 1500},
}


def calculate(fullstring: str) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)

    # ── 第二段: 型鋼代碼 ──
    part2 = get_part(fullstring, 2)
    details = get_section_details(part2)
    if not details:
        result.error = f"Type 28: 未知型鋼代碼 {part2}"
        return result

    section_type = details["type"]   # "Angle" or "Channel"
    full_size = details["size"]      # "L50*50*6" or "C125*65*6"

    # ── 第三段: LLHH + M42Letter ──
    part3 = get_part(fullstring, 3)
    if not part3 or len(part3) < 5:
        result.error = f"Type 28: 第三段格式錯誤 '{part3}' (需至少5字元, 如 1005L)"
        return result

    m42_letter = part3[-1].upper()
    if m42_letter.isdigit():
        result.error = f"Type 28: 缺少 M-42 型式字母 (末位='{m42_letter}' 不是字母)"
        return result

    # NOTE 4: USE TYPE-L & P ONLY
    if m42_letter not in ("L", "P"):
        result.warnings.append(
            f"M-42 型式 '{m42_letter}' 非標準 (NOTE 4: USE TYPE-L & P ONLY)"
        )

    digits = part3[:-1]  # 去掉末位字母
    try:
        section_L = int(digits[:2]) * 100  # 前兩位 = L (橫梁跨距)
        section_H = int(digits[2:]) * 100  # 後兩位 = H (支腿高度)
    except ValueError:
        result.error = f"Type 28: 無法解析 L/H 值 '{part3}'"
        return result

    # ── 超限檢查 ──
    limits = _LIMITS.get(part2, {"L_max": 1500, "H_max": 1500})
    if section_L > limits["L_max"]:
        result.warnings.append(
            f"L={section_L}mm 超出 {part2} 標準範圍 (≤ {limits['L_max']}mm)"
        )
    if section_H > limits["H_max"]:
        result.warnings.append(
            f"H={section_H}mm 超出 {part2} 標準範圍 (≤ {limits['H_max']}mm)"
        )

    # ═══════════════════════════════════════════════════════
    # ① MEMBER "M" — 門型框架 (一根構件折/焊成)
    #    Total_Length = 2H + L
    #    左腿(H) + 橫梁(L) + 右腿(H)
    #
    #    VBA BUG: Section_Length_L 漏乘 *100
    #    VBA: Total = (H * 100 * 2) + L_digits  ← 錯
    #    正確: Total = (H * 100 * 2) + (L * 100) = 2H + L
    # ═══════════════════════════════════════════════════════
    total_length = section_H * 2 + section_L
    section_dim = full_size[1:]  # 去掉前綴字母
    add_steel_section_entry(result, section_type, section_dim, total_length)
    usage_hint = "Channel:管置上方" if section_type == "Channel" else "Angle:可U-bolt側掛"
    result.entries[-1].remark = (
        f"門型 M-42:{m42_letter}, 2×H={section_H}+L={section_L}={total_length} ({usage_hint})"
    )

    # ═══════════════════════════════════════════════════════
    # ② M-42 下部組件 (底板 + 螺栓)
    #    NOTE 4: USE TYPE-L & P ONLY
    # ═══════════════════════════════════════════════════════
    perform_action_by_letter(result, m42_letter, full_size)

    return result
