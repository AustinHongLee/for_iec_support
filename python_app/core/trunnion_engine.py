"""
trunnion_engine.py
------------------
共用基礎模組，供 Type 42 (D-50) 與 Type 43 (D-51/52) 使用。

提供：
  1. 材料常數（4 種）
  2. _parse_inputs()  — 解析 designation 第 2~4 段並做超限驗證
  3. add_trunnion()   — 新增 TRUNNION 項目
  4. add_cs_shim()    — 新增 C/S SHIM 項目
  5. add_bolt_set()   — 新增 M.BOLT 或 K.BOLT 項目

type_42.py / type_43.py 只需保留各自的 BOM 差異邏輯（G 公式 / S·N 公式 + lug plates）。
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from .models import AnalysisResult
from .parser import get_part, get_lookup_value
from .plate import add_plate_entry
from .steel import add_steel_section_entry
from .bolt import add_custom_entry
from .material_specs import (
    ANCHOR_BOLT_SUS304,
    PLATE_LUG_A36_SS400,
    STRUCTURAL_A36_SS400,
    SUPPORT_PIPE_A53GRB,
    SUPPORT_PLATE_A36_SS400,
)
from data.steel_sections import get_section_details


# ── 材料常數（type_42 & type_43 共用） ───────────────────────────────────────

STRUCTURAL_MATERIAL = STRUCTURAL_A36_SS400
SUPPORT_PIPE_MATERIAL = SUPPORT_PIPE_A53GRB
SUPPORT_PLATE_MATERIAL = SUPPORT_PLATE_A36_SS400
PLATE_LUG_MATERIAL = PLATE_LUG_A36_SS400
ANCHOR_BOLT_MATERIAL = ANCHOR_BOLT_SUS304


# ── 解析結果容器 ──────────────────────────────────────────────────────────────

@dataclass
class TrunnionInputs:
    """parse_inputs() 的成功回傳值"""
    line_size: float       # 數值管徑 (inch)
    pipe_data: dict        # 來自 type_XX_pipe table
    member_code: str       # 如 "C125", "L75"
    member_data: dict      # 來自 type_XX_member / data table
    section_type: str      # "Channel" / "Angle" / "H Beam"
    section_dim: str       # 如 "125*65*6"（去掉前綴字母）
    h_mm: int              # 第四段 H 值
    fig_type: str          # "A" 或 "B"
    theta: int             # 30 (FIG-A) 或 45 (FIG-B)


def parse_inputs(
    fullstring: str,
    type_label: str,
    get_pipe_fn,
    get_member_fn,
    get_h_max_fn=None,
) -> tuple[Optional[TrunnionInputs], Optional[AnalysisResult]]:
    """
    解析 Trunnion 系列 designation 的前四段，並做超限驗證。

    成功 → (TrunnionInputs, None)
    失敗 → (None, AnalysisResult with .error set)

    get_pipe_fn(line_size)   → dict | None
    get_member_fn(code)      → dict | None
    get_h_max_fn(code)       → int | None  （可選，傳 None 表示不做超限檢查）
    """
    result_err = AnalysisResult(fullstring=fullstring)

    # 第二段: 管徑
    part2 = get_part(fullstring, 2)
    if not part2:
        result_err.error = f"{type_label}: 缺少管徑"
        return None, result_err
    line_size = get_lookup_value(part2)
    pipe_data = get_pipe_fn(line_size)
    if not pipe_data:
        result_err.error = f"{type_label}: 管徑 {part2} ({line_size}\") 不在查表範圍 (2\"~24\")"
        return None, result_err

    # 第三段: 型鋼代碼
    part3 = get_part(fullstring, 3)
    if not part3:
        result_err.error = f"{type_label}: 缺少型鋼代碼"
        return None, result_err
    member_code = part3.strip()
    member_data = get_member_fn(member_code)
    if not member_data:
        result_err.error = f"{type_label}: 未知型鋼 {member_code} (支援 L75~C200)"
        return None, result_err
    details = get_section_details(member_code)
    if not details:
        result_err.error = f"{type_label}: steel_sections 無 {member_code}"
        return None, result_err

    # 第四段: "H FIG"
    part4 = get_part(fullstring, 4)
    if not part4:
        result_err.error = f"{type_label}: 缺少 H 值與 FIG 類型"
        return None, result_err
    parts4 = part4.strip().split()
    try:
        h_mm = int(parts4[0])
    except ValueError:
        result_err.error = f"{type_label}: H 值無法解析 '{parts4[0]}'"
        return None, result_err
    fig_type = parts4[1].upper() if len(parts4) > 1 else "A"
    if fig_type not in ("A", "B"):
        result_err.error = f"{type_label}: FIG 型式 '{fig_type}' 無效 (A=30°, B=45°)"
        return None, result_err

    inputs = TrunnionInputs(
        line_size=line_size,
        pipe_data=pipe_data,
        member_code=member_code,
        member_data=member_data,
        section_type=details["type"],
        section_dim=details["size"][1:],
        h_mm=h_mm,
        fig_type=fig_type,
        theta=30 if fig_type == "A" else 45,
    )

    # 超限警告（不阻擋，回傳 inputs 同時也設置 warnings）
    if get_h_max_fn:
        h_max = get_h_max_fn(member_code)
        if h_max and h_mm > h_max:
            # 呼叫方需要一個暫時 result 來收警告；engine 只回傳 warning 文字
            inputs._h_warning = f"H={h_mm}mm 超出 {member_code} 上限 ({h_max}mm)"
        else:
            inputs._h_warning = None
    else:
        inputs._h_warning = None

    return inputs, None


# ── 共用 BOM 項目輔助函式 ─────────────────────────────────────────────────────

def add_trunnion(result: AnalysisResult, trunnion_spec: str, note: str) -> None:
    """③ Trunnion 管件"""
    add_custom_entry(
        result,
        name="TRUNNION",
        spec=trunnion_spec,
        material=SUPPORT_PIPE_MATERIAL,
        quantity=1,
        unit_weight=2.0,
        unit="SET",
    )
    result.entries[-1].remark = note


def add_cs_shim(result: AnalysisResult, shim_a: int, shim_b: int) -> None:
    """C/S SHIM — 現場微調用"""
    add_plate_entry(
        result,
        plate_a=shim_a,
        plate_b=shim_b,
        plate_thickness=6,
        plate_name="C/S SHIM",
        plate_role="shim_plate",
        material=SUPPORT_PLATE_MATERIAL,
        plate_qty=1,
    )
    result.entries[-1].remark = "現場微調用"


def add_bolt_set(
    result: AnalysisResult,
    name: str,
    spec: str,
    quantity: int,
    remark: str = "",
) -> None:
    """M.BOLT 或 K BOLT（通用）"""
    add_custom_entry(
        result,
        name=name,
        spec=spec,
        material=ANCHOR_BOLT_MATERIAL,
        quantity=quantity,
        unit_weight=0.8,
        unit="SET",
    )
    if remark:
        result.entries[-1].remark = remark
