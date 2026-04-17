"""
Type 32 計算器  (判讀來源: D-35M, E1906-DSP-500-006)
格式: 32-L50-1005

第二段: 型鋼代碼 (L50, L75, C125, C150, H250)
第三段: LLHH (4位純數字, 無末位字母)
        前2位 = L(底部橫梁跨距) ×100mm
        後2位 = H(垂直腿高) ×100mm

結構: 吊掛型框架支撐 — 從 EXISTING STEEL 向下吊掛, 無 M-42
────────────────────────────────────────────────────────────

  ═══════════════════════  EXISTING STEEL (上方)
       ┌─── L ───┐
       │  6V  6V │
       │ MEMBER  │ H     (管線在框內, 畫兩個圓)
       │  "M"    │
       └─────────┘  ← 底部橫梁 (L)  TYP. weld

  力傳遞: 管線 → 底梁 → 側柱 → 上方焊接點 → EXISTING STEEL
  方向: 由下往上 (吊掛)

  ★ TYPE-31 vs TYPE-32 (關鍵差異):
    31: 底部=EXISTING STEEL, 上部=框架   → 支撐框 (由下往上撐)
    32: 上部=EXISTING STEEL, 底部=框架   → 吊掛框 (從上往下吊)

  ★ VBA 輸出差異:
    31: 2 筆分開 (H*2 一筆, L 一筆)
    32: 1 筆合併 (H*2 + L)
    原因: 32 的 U 型框 (左腿+底梁+右腿) 是一體折/焊的,
          上方直接焊到 EXISTING STEEL, 不需額外上橫梁

  ★ 無 M-42, 無螺栓, 無 U-bolt

BOM:
  ① 型鋼 ×1 筆  Total = H × 2 + L

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
        result.error = f"Type 32: 未知型鋼代碼 {part2}"
        return result

    section_type = details["type"]   # "Angle", "Channel", or "H Beam"
    full_size = details["size"]

    # ── 第三段: LLHH (4位純數字) ──
    part3 = get_part(fullstring, 3)
    if not part3 or len(part3) < 4:
        result.error = f"Type 32: 第三段格式錯誤 '{part3}' (需4位數字, 如 1005)"
        return result

    try:
        section_L = int(part3[:2]) * 100  # 前兩位 = L (底部橫梁跨距)
        section_H = int(part3[2:4]) * 100  # 後兩位 = H (垂直腿高)
    except ValueError:
        result.error = f"Type 32: 無法解析 L/H 值 '{part3}'"
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
    # ① H 方向 — 垂直腿 ×2 (左腿 + 右腿)
    #    VBA 合併成一筆 H*2+L, 但下料時切 3 根獨立的
    #    故拆成: 腿 qty=2 + 梁 qty=1
    # ═══════════════════════════════════════════════════════
    add_steel_section_entry(result, section_type, section_dim, section_H, steel_qty=2)
    result.entries[-1].remark = (
        f"吊掛框H向(左右腿), H={section_H} ×2"
    )

    # ═══════════════════════════════════════════════════════
    # ② L 方向 — 底橫梁 ×1
    #    上方 = EXISTING STEEL (非 MEMBER)
    # ═══════════════════════════════════════════════════════
    add_steel_section_entry(result, section_type, section_dim, section_L)
    result.entries[-1].remark = (
        f"吊掛框L向(底梁), L={section_L}"
    )

    return result
