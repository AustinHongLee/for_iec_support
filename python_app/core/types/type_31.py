"""
Type 31 計算器  (判讀來源: D-35M, E1906-DSP-500-006)
格式: 31-L50-1005

第二段: 型鋼代碼 (L50, L75, C125, C150, H250)
第三段: LLHH (4位純數字, 無末位字母)
        前2位 = L(水平橫梁跨距) ×100mm
        後2位 = H(垂直腿高) ×100mm

結構: 框架式支撐 — 焊接於 EXISTING STEEL 上, 無 M-42
────────────────────────────────────────────────────────────

  ELEV:
       ┌─── L ───┐
       │ MEMBER  │
       │  "M"    │ H        ↕ TYP. 6V weld
       │         │
  ═════╧═════════╧═════  EXISTING STEEL (dashed)

  圖面標示 "FOR CHANNEL" — C125/C150/H250 用於需要更高剛性場合

  結構拆分 (VBA 輸出 2 筆):
    ① H 方向 (垂直): 左腿(H) + 右腿(H) = H × 2 → 一筆合併
    ② L 方向 (水平): 上橫梁 = L → 一筆
    底部 = EXISTING STEEL 本身 (非 MEMBER "M" 範圍)

  ★ 無 M-42 — 不落地, 焊接至既有鋼構
  ★ 與 TYPE-28 差異: 28=開口門型(落地+M-42), 31=封閉框(架在既有鋼構上)
  ★ 與 TYPE-30 差異: 30=單支夾持, 31=矩形框架 (剛性更高)

BOM:
  ① 型鋼 (H方向) ×1 筆  Total = H × 2
  ② 型鋼 (L方向) ×1 筆  Total = L

DIMENSIONS TABLE (D-35M):
  MEMBER "M"      | L MAX | H MAX
  L50×50×6        | 1000  | 1000
  L75×75×9        | 1000  | 1500
  C125×65×6       | 1500  | 1500
  C150×75×9       | 1500  | 1500
  H250×125×6×9    | 1500  | 1500

NOTE 1: "H" & "L" SHALL BE CUT TO SUIT IN FIELD.
"""
from ..models import AnalysisResult
from ..parser import get_part
from ..steel import add_steel_section_entry
from data.steel_sections import get_section_details

# ── D-35M 限制表 ─────────────────────────────────────────
_LIMITS = {
    "L50":  {"L_max": 1000, "H_max": 1000},
    "L75":  {"L_max": 1000, "H_max": 1500},
    "C125": {"L_max": 1500, "H_max": 1500},
    "C150": {"L_max": 1500, "H_max": 1500},
    "H250": {"L_max": 1500, "H_max": 1500},
}


def calculate(fullstring: str) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)

    # ── 第二段: 型鋼代碼 ──
    part2 = get_part(fullstring, 2)
    details = get_section_details(part2)
    if not details:
        result.error = f"Type 31: 未知型鋼代碼 {part2}"
        return result

    section_type = details["type"]   # "Angle", "Channel", or "H Beam"
    full_size = details["size"]      # "L50*50*6", "C125*65*6", "H250*125*6"

    # ── 第三段: LLHH (4位純數字, 無字母) ──
    part3 = get_part(fullstring, 3)
    if not part3 or len(part3) < 4:
        result.error = f"Type 31: 第三段格式錯誤 '{part3}' (需4位數字, 如 1005)"
        return result

    try:
        section_L = int(part3[:2]) * 100  # 前兩位 = L (水平跨距)
        section_H = int(part3[2:4]) * 100  # 後兩位 = H (垂直腿高)
    except ValueError:
        result.error = f"Type 31: 無法解析 L/H 值 '{part3}'"
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

    section_dim = full_size[1:]  # 去掉前綴字母

    # ═══════════════════════════════════════════════════════
    # ① H 方向 — 垂直腿 ×2 (左腿 + 右腿, 各 H 長)
    #    VBA 合併成一筆 H*2, 但下料時是切 2 根獨立的
    #    故拆成 qty=2, 每根長 H
    # ═══════════════════════════════════════════════════════
    add_steel_section_entry(result, section_type, section_dim, section_H, steel_qty=2)
    result.entries[-1].remark = (
        f"框架H向(左右腿), H={section_H} ×2"
    )

    # ═══════════════════════════════════════════════════════
    # ② L 方向 — 上橫梁 ×1
    #    底部 = EXISTING STEEL (非 MEMBER)
    # ═══════════════════════════════════════════════════════
    add_steel_section_entry(result, section_type, section_dim, section_L)
    result.entries[-1].remark = (
        f"框架L向(上梁), L={section_L}"
    )

    return result
