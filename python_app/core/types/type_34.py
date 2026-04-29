"""
Type 34 計算器  (判讀來源: D-35M, E1906-DSP-500-006)
格式: 34-L50-1005

第二段: 型鋼代碼 (L50, L75, C125, C150, H250)
第三段: LLHH (4位純數字, 無末位字母)
        前2位 = L(懸臂長度) ×100mm
        後2位 = H(垂直高度) ×100mm

結構: 強化型懸臂梁支撐 — 側邊焊接 EXISTING STEEL, 無 M-42
────────────────────────────────────────────────────────────

  ELEV:
                ┌─── L ───┐   ← MEMBER "M"
  EXISTING      │         │
   STEEL   ═════╪═════════╡   FOR CHANNEL
   (牆/柱)      │    6V   │
               │         │ H
               │    6V   │
               ╚═════════╛

  力傳遞: 管線 → 上梁(L) → 右柱(H) → 左側固定端 → EXISTING STEEL

  ★ L 型結構 — 上橫梁(L, 承管) + 右側立柱(H)
    左側由 EXISTING STEEL 本身提供
  ★ TYPE-33 vs TYPE-34:
    33: 管在下梁 (框撐管), H(立柱) + L(下梁)
    34: 管在上梁 (梁撐管), H(立柱) + L(上梁)
  ★ 無 M-42, 無螺栓 (全焊接)

BOM:
  ① 型鋼 (H方向, 立柱) ×1 筆  Total = H
  ② 型鋼 (L方向, 上梁) ×1 筆  Total = L

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
        result.error = f"Type 34: 未知型鋼代碼 {part2}"
        return result

    section_type = details["type"]
    full_size = details["size"]

    # ── 第三段: LLHH (4位純數字) ──
    part3 = get_part(fullstring, 3)
    if not part3 or len(part3) < 4:
        result.error = f"Type 34: 第三段格式錯誤 '{part3}' (需4位數字, 如 1005)"
        return result

    try:
        section_L = int(part3[:2]) * 100
        section_H = int(part3[2:4]) * 100
    except ValueError:
        result.error = f"Type 34: 無法解析 L/H 值 '{part3}'"
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
    # ① H 方向 — 立柱 (單支)
    #    VBA: Section_Length_H = H * 100
    # ═══════════════════════════════════════════════════════
    add_steel_section_entry(result, section_type, section_dim, section_H)
    result.entries[-1].remark = f"懸臂梁H向(立柱), H={section_H}"

    # ═══════════════════════════════════════════════════════
    # ② L 方向 — 上橫梁 (承管懸臂)
    #    VBA: Section_Length_L = L * 100
    # ═══════════════════════════════════════════════════════
    add_steel_section_entry(result, section_type, section_dim, section_L)
    result.entries[-1].remark = f"懸臂梁L向(上梁), L={section_L}"

    return result
