"""
Type 26 計算器  (判讀來源: D-28 + D-29, E1906-DSP-500-006)
格式: 26-L50-1005A

第二段: 型鋼代碼 (L50, L65, L75, C125)
第三段: LL+HH+Fig
        前2位 = L(垂直/端部) ×100mm
        中2位 = H(水平/懸臂) ×100mm
        末1位 = Fig 字母 (A / B / C)

結構: 標準化懸臂框架支撐 (Catalog Cantilever Frame Support)
────────────────────────────────────────────────────────────
 與 Type 25 (單純懸臂) 的關鍵差異:
 - Type 26 是框架/搖籃型, H 方向有「上下兩支」構件
 - 多支援 C125×65×6 槽鋼 (Channel)
 - H/L 上限不同 (普遍更大)
────────────────────────────────────────────────────────────

FIG-A  基本框架型
  ├ 框架結構: H段×2 (上下平行, 分列兩件) + L段×1
  └ 焊接組合, 全結構 6mm 角焊

FIG-B  附 U-bolt / Down Stopper 型
  ├ 框架結構: 同 FIG-A
  ├ DOWN STOPPER (D-70) — NOT FURNISHED
  └ STANDARD U-BOLT (D-68) — NOT FURNISHED

FIG-C  附連接板型
  ├ 框架結構: 同 FIG-A
  ├ LUG PLATE TYPE-C (SEE M-34) — 連接板 ×2
  ├ K BOLT — 連接螺栓 ×8
  └ SEE DETAIL "A" (底部連接)

力傳遞路徑:
  管線 → U-bolt → Lug Plate → 主梁框架 → 固定端 (牆/鋼構)

DIMENSIONS (Page 2, D-29):
  MEMBER "M"  | L MAX | H MAX
  L50×50×6    | 1000  | 1000
  L65×65×6    | 1000  | 1000
  L75×75×9    | 1000  | 2500
  C125×65×6   | 1500  | 1500

  MEMBER | A   | C   | D  | E  | F  | G  | N  | ØJ | K
  L50    | 150 | 50  | 30 | 30 | 60 | -  | -  | 19 | 5/8"×40
  L65    | 160 | 65  | 35 | 30 | 70 | -  | -  | 22 | 3/4"×50
  L75    | 160 | 75  | 40 | 30 | 70 | -  | -  | 22 | 3/4"×50
  C125   | 170 | 125 | -  | 30 | 80 | 35 | 55 | 22 | 3/4"×50

NOTE 2: "L" & "H" SHALL BE CUT TO SUIT IN FIELD.
NOTE 3: FOR DIMENSIONAL DATA, SEE SH'T D-29.
"""
from ..models import AnalysisResult
from ..parser import get_part
from ..steel import add_steel_section_entry
from ..plate import add_plate_entry
from ..bolt import add_custom_entry
from data.steel_sections import get_section_details

# ── D-29 限制表 ──────────────────────────────────────────
_LIMITS = {
    "L50":  {"L_max": 1000, "H_max": 1000},
    "L65":  {"L_max": 1000, "H_max": 1000},
    "L75":  {"L_max": 1000, "H_max": 2500},
    "C125": {"L_max": 1500, "H_max": 1500},
}

# ── D-29 尺寸表 ──────────────────────────────────────────
_TABLE = {
    "L50":  {"A": 150, "C":  50, "D": 30, "E": 30, "F": 60,
             "G": None, "N": None, "OJ": 19, "K": '5/8"X40', "t": 6},
    "L65":  {"A": 160, "C":  65, "D": 35, "E": 30, "F": 70,
             "G": None, "N": None, "OJ": 22, "K": '3/4"X50', "t": 6},
    "L75":  {"A": 160, "C":  75, "D": 40, "E": 30, "F": 70,
             "G": None, "N": None, "OJ": 22, "K": '3/4"X50', "t": 9},
    "C125": {"A": 170, "C": 125, "D": None, "E": 30, "F": 80,
             "G": 35,  "N": 55,  "OJ": 22, "K": '3/4"X50', "t": 6},
}


def calculate(fullstring: str) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)

    # ── 第二段: 型鋼代碼 ──
    part2 = get_part(fullstring, 2)
    details = get_section_details(part2)
    if not details:
        result.error = f"Type 26: 未知型鋼代碼 {part2}"
        return result

    section_type = details["type"]   # "Angle" or "Channel"
    full_size = details["size"]      # "L50*50*6" or "C125*65*6"

    # ── 第三段: LLHH + Fig ──
    part3 = get_part(fullstring, 3)
    if not part3 or len(part3) < 5:
        result.error = f"Type 26: 第三段格式錯誤 '{part3}' (需至少5字元, 如 1005A)"
        return result

    fig = part3[-1].upper()
    if fig.isdigit():
        result.error = f"Type 26: 缺少 Fig 字母 (末位='{fig}' 不是字母)"
        return result

    try:
        section_L = int(part3[:2]) * 100   # 前兩位 = L (垂直/端部)
        section_H = int(part3[2:-1]) * 100  # 中間   = H (水平/懸臂)
    except ValueError:
        result.error = f"Type 26: 無法解析 L/H 值 '{part3}'"
        return result

    # ── 超限檢查 (WARNING, 不阻擋 — 可施工但非標準設計) ──
    limits = _LIMITS.get(part2, {"L_max": 1500, "H_max": 2500})
    if section_L > limits["L_max"]:
        result.warnings.append(
            f"L={section_L}mm 超出 {part2} 標準範圍 (≤ {limits['L_max']}mm), 非標準設計"
        )
    if section_H > limits["H_max"]:
        result.warnings.append(
            f"H={section_H}mm 超出 {part2} 標準範圍 (≤ {limits['H_max']}mm), 非標準設計"
        )

    fig_tag = f"Fig-{fig}"

    # 去掉型鋼前綴字母 (L50*50*6 → 50*50*6, C125*65*6 → 125*65*6)
    section_dim = full_size[1:]

    # ═══════════════════════════════════════════════════════
    # 共通: 框架結構 (所有 Fig 皆有)
    #   H段 ×2 (上下兩支平行構件, 分列兩件) + L段 ×1
    # ═══════════════════════════════════════════════════════

    # 1. H 段上件
    add_steel_section_entry(result, section_type, section_dim, section_H)
    result.entries[-1].remark = f"{fig_tag}, H段上件"

    # 2. H 段下件
    add_steel_section_entry(result, section_type, section_dim, section_H)
    result.entries[-1].remark = f"{fig_tag}, H段下件"

    # 3. L 段 — 垂直/端部構件 ×1
    add_steel_section_entry(result, section_type, section_dim, section_L)
    result.entries[-1].remark = f"{fig_tag}, L段"

    # ═══════════════════════════════════════════════════════
    # FIG-C 額外: LUG PLATE TYPE-C (M-34) + K bolt
    # ═══════════════════════════════════════════════════════
    if fig == "C":
        table = _TABLE.get(part2, {})
        k_spec = table.get("K", "")
        plate_a = table.get("A", 0)
        plate_c = table.get("C", 0)
        plate_d = table.get("D")
        plate_t = table.get("t", 6)
        oj = table.get("OJ", 0)

        # DETAIL "A" — LUG PLATE TYPE-C (SEE M-34)
        # Type 26 Fig-C 依框架上下兩支 H 段視為兩片 lug plate。
        if plate_a > 0:
            # C125 沒有 D 值, 使用 C 值作為板高估值
            plate_height = plate_c + (plate_d if plate_d else 0)
            add_plate_entry(
                result,
                plate_a=plate_a,
                plate_b=plate_height,
                plate_thickness=plate_t,
                plate_name="LUG_PLATE_C",
                material="A36/SS400",
                plate_qty=2,
                bolt_switch=True,
                bolt_x=2 * table.get("E", 0) + table.get("F", 0),
                bolt_y=0,
                bolt_hole=oj,
                bolt_size=k_spec,
                plate_role="lug_plate",
            )
            result.entries[-1].remark = f"SEE M-34, {fig_tag}"

        # K BOLT ×8 (兩片 lug plate, 每片四孔)
        if k_spec:
            add_custom_entry(
                result,
                name="BOLT",
                spec=k_spec,
                material="SS400",
                quantity=8,
                unit_weight=0.1,
                unit="PC",
            )
            result.entries[-1].remark = f"M-34 K bolt, {fig_tag}"

    return result
