"""
Type 36 計算器  (判讀來源: D-35M + M-34, E1906-DSP-500-006)
格式: 36-C125-05

第二段: 型鋼代碼 (L50, L75, C100, C125, C150)
第三段: HH (2位純數字)
        H = 構件長度 ×100mm (注意: H 代表長度, 非高度)

結構: 夾持/固定型支撐 — 焊接 EXISTING STRUCTURE, 含 Bolt + Lug Plate
────────────────────────────────────────────────────────────

  ELEV:
  ┌──────────── H ──────────────┐
  ╔═══╪════════╪═══════╪════════╗   MEMBER "M"
  ║   ○  bolt  ○       ○  bolt ║
  ╚═══╪════════╪═══════╪════════╝
      │   ØJ HOLE for K BOLT   │
      └── SEE DETAIL "A" ──────┘

  DETAIL "A" (M-34):
  管線(含 INSULATION) → LUG PLATE TYPE-C (A×B×T) → K BOLT → MEMBER

  力傳遞: 管線 → Lug Plate → K Bolt → MEMBER → 結構

  ★ TYPE-35 vs TYPE-36:
    35: 托條, 管線放上去 (resting)
    36: 固定, 管線鎖住 (restraint), 含 bolt + lug plate
  ★ VBA 無此 Type 計算器, 完全依圖紙重新設計
  ★ Lug Plate 規格由 M-34 (LGP-C-x) 查表決定

BOM (3 筆):
  ① 型鋼 (MEMBER) ×1 筆  Total = H
  ② LUG PLATE TYPE-C ×1 筆  A×B×T (M-34 查表)
  ③ K BOLT ×1 SET  (數量依管線數調整)

DIMENSIONS TABLE (D-35M TYPE-36):
  MEMBER "M"  | H MAX | 對應 M-34
  L50×50×6    | 600   | LGP-C-1
  L75×75×9    | 800   | LGP-C-3
  C100×50×5   | 1400  | LGP-C-4
  C125×65×6   | 1400  | LGP-C-6
  C150×75×9   | 1400  | LGP-C-7

NOTE 1: DESIGNATION FORMAT: 36-C125-05
NOTE 2: M-34 material same as connected metal
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
from data.m34_table import get_m34_by_member


def _material_spec(kind: HardwareKind, material_name: str):
    return resolve_hardware_material(
        kind,
        overrides=HardwareMaterialOverrides(per_kind={kind: material_name}),
    )


_STRUCTURAL_MATERIAL = _material_spec(HardwareKind.STRUCTURAL_STRUT, "A36/SS400")
_PLATE_LUG_MATERIAL = _material_spec(HardwareKind.PLATE_LUG, "A36/SS400")
_ANCHOR_BOLT_MATERIAL = _material_spec(HardwareKind.ANCHOR_BOLT, "SUS304")


# ── D-35M 限制表 ─────────────────────────────────────────
_H_MAX = {
    "L50":  600,
    "L75":  800,
    "C100": 1400,
    "C125": 1400,
    "C150": 1400,
}


def calculate(fullstring: str) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)

    # ── 第二段: 型鋼代碼 ──
    part2 = get_part(fullstring, 2)
    details = get_section_details(part2)
    if not details:
        result.error = f"Type 36: 未知型鋼代碼 {part2}"
        return result

    section_type = details["type"]
    full_size = details["size"]

    # ── 第三段: HH (2位純數字) ──
    part3 = get_part(fullstring, 3)
    if not part3:
        result.error = f"Type 36: 缺少第三段 (H 值)"
        return result

    try:
        section_H = int(part3) * 100
    except ValueError:
        result.error = f"Type 36: 無法解析 H 值 '{part3}'"
        return result

    # ── 超限檢查 ──
    h_max = _H_MAX.get(part2)
    if not h_max:
        result.error = f"Type 36: {part2} 不在支援清單 (L50/L75/C100/C125/C150)"
        return result
    if section_H > h_max:
        result.warnings.append(
            f"H={section_H}mm 超出 {part2} 標準範圍 (≤ {h_max}mm)"
        )

    # ── M-34 Lug Plate 查表 ──
    m34 = get_m34_by_member(part2)
    if not m34:
        result.error = f"Type 36: M-34 無 {part2} 對應的 Lug Plate"
        return result

    section_dim = full_size[1:]  # 去掉前綴字母

    # ═══════════════════════════════════════════════════════
    # ① MEMBER — 主構件, length = H
    # ═══════════════════════════════════════════════════════
    add_steel_section_entry(
        result, section_type, section_dim, section_H,
        material=_STRUCTURAL_MATERIAL,
    )
    result.entries[-1].remark = f"固定型托條, H={section_H}"

    # ═══════════════════════════════════════════════════════
    # ② LUG PLATE TYPE-C — M-34 標準子零件
    #    plate_a = A (板寬), plate_b = B (板高), T (板厚)
    #    數量依管線數, 此處以 1 PC 為最小單位
    # ═══════════════════════════════════════════════════════
    lgp_type = m34["type"]
    plate_a = m34["A"]
    plate_b = m34["B"]
    plate_t = m34["T"]
    bolt_k = m34["K"]
    hole_j = m34["J"]

    add_plate_entry(
        result,
        plate_a=plate_a,
        plate_b=plate_b,
        plate_thickness=plate_t,
        plate_name=f"LUG PLATE TYPE-C",
        material=_PLATE_LUG_MATERIAL,
        plate_qty=1,
    )
    result.entries[-1].remark = (
        f"{lgp_type}, {plate_a}x{plate_b}x{plate_t}t, "
        f"ØJ={hole_j}, K bolt={bolt_k}, 數量依管線數調整"
    )

    # ═══════════════════════════════════════════════════════
    # ③ K BOLT — 螺栓組
    #    bolt 規格由 M-34 決定, 數量依管線數
    #    此處 1 SET 為最小單位
    # ═══════════════════════════════════════════════════════
    add_custom_entry(
        result,
        name="K BOLT",
        spec=f'{bolt_k}x{"40" if bolt_k.startswith("5/8") else "50"}',
        material=_ANCHOR_BOLT_MATERIAL,
        quantity=1,
        unit_weight=0.5 if bolt_k.startswith("5/8") else 0.8,
        unit="SET",
    )
    result.entries[-1].remark = f"配合 {lgp_type}, 數量依管線數調整"

    return result
