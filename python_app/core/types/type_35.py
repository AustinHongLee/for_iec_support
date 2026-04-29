"""
Type 35 計算器  (判讀來源: D-35M, E1906-DSP-500-006)
格式: 35-C125-05A

第二段: 型鋼代碼 (L50, L75, C100, C125, C150, H100, H150)
第三段: HH + 末位字母(A/B)
        前2位 = H(構件長度) ×100mm
        末位 = FIG 類型

結構: 支撐軌道 / 托條 — 焊接 EXISTING SURFACE, 無 M-42
────────────────────────────────────────────────────────────

  FIG-A (單條):
  EXISTING ═══╪══════════╡
   SURFACE    │   6V     │ ← H →
              ╚══════════╛

  FIG-B (雙條, 間距 50mm):
  EXISTING ═══╪══════════╡
   SURFACE    │   6V     │ ← H →   (×2)
              ╚══════════╛

  ★ H 在此 TYPE 代表「長度」(非高度)
  ★ 線性構件焊接在既有結構面上
  ★ 無 M-42, 無螺栓 (全焊接)

BOM:
  FIG-A: ① 型鋼 ×1 筆  Total = H
  FIG-B: ① 型鋼 ×1 筆  qty=2, 每根 = H

DIMENSIONS TABLE (D-35M):
  MEMBER "M"      | H FIG-A MAX | H FIG-B MAX
  L50×50×6        | 600         | — (FIG-A only, NOTE 2)
  L75×75×9        | 800         | 900
  C100×50×5       | 1400        | 900
  C125×65×6       | 1400        | 900
  C150×75×9       | 1400        | — (FIG-A only, NOTE 2)
  H100×100×6      | 1400        | —
  H150×150×7      | 1400        | —

NOTE 1: DESIGNATION FORMAT: 35-C125-05A
NOTE 2: L50, C150 USE FIG-A ONLY.
"""
from ..models import AnalysisResult
from ..parser import get_part
from ..steel import add_steel_section_entry
from data.steel_sections import get_section_details

# ── D-35M 限制表 ─────────────────────────────────────────
_LIMITS = {
    "L50":  {"A": 600,  "B": None},
    "L75":  {"A": 800,  "B": 900},
    "C100": {"A": 1400, "B": 900},
    "C125": {"A": 1400, "B": 900},
    "C150": {"A": 1400, "B": None},
    "H100": {"A": 1400, "B": None},
    "H150": {"A": 1400, "B": None},
}

# NOTE 2: 只能用 FIG-A 的型鋼
_FIG_A_ONLY = {"L50", "C150"}


def calculate(fullstring: str) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)

    # ── 第二段: 型鋼代碼 ──
    part2 = get_part(fullstring, 2)
    # H150 在 Type 35 用 7mm (同 Type 37)
    details = get_section_details(part2, type_first="35" if part2 == "H150" else "")
    if not details:
        result.error = f"Type 35: 未知型鋼代碼 {part2}"
        return result

    section_type = details["type"]
    full_size = details["size"]

    # ── 第三段: HH + A/B ──
    part3 = get_part(fullstring, 3)
    if not part3 or len(part3) < 3:
        result.error = f"Type 35: 第三段格式錯誤 '{part3}' (需如 05A 或 09B)"
        return result

    fig_type = part3[-1].upper()
    if fig_type not in ("A", "B"):
        result.error = f"Type 35: FIG 類型必須為 A 或 B, 得到 '{fig_type}'"
        return result

    try:
        section_H = int(part3[:-1]) * 100
    except ValueError:
        result.error = f"Type 35: 無法解析 H 值 '{part3[:-1]}'"
        return result

    # ── FIG-A only 檢查 ──
    if fig_type == "B" and part2 in _FIG_A_ONLY:
        result.warnings.append(
            f"{part2} 僅支援 FIG-A (NOTE 2), 已收到 FIG-B"
        )

    # ── FIG-B 限制: H100, H150 無 FIG-B ──
    if fig_type == "B" and part2 in ("H100", "H150"):
        result.warnings.append(
            f"{part2} 無 FIG-B 規格, 已收到 FIG-B"
        )

    # ── 超限檢查 ──
    limits = _LIMITS.get(part2)
    if limits:
        h_max = limits.get(fig_type)
        if h_max and section_H > h_max:
            result.warnings.append(
                f"H={section_H}mm 超出 {part2} FIG-{fig_type} 標準範圍 (≤ {h_max}mm)"
            )

    section_dim = full_size[1:]  # 去掉前綴字母

    # ═══════════════════════════════════════════════════════
    # FIG-A: 單條  → qty=1, length=H
    # FIG-B: 雙條  → qty=2, length=H (下料切 2 根)
    #
    # VBA: FIG-B 用 H*2 合併一筆, 此處拆成 qty=2
    # ═══════════════════════════════════════════════════════
    if fig_type == "A":
        add_steel_section_entry(result, section_type, section_dim, section_H)
        result.entries[-1].remark = f"托條 FIG-A, H={section_H}"
    else:
        add_steel_section_entry(result, section_type, section_dim, section_H, steel_qty=2)
        result.entries[-1].remark = f"托條 FIG-B(雙條), H={section_H} ×2"

    return result
