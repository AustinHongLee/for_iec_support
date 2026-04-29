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
from ..component_rules import estimate_m28_weight, estimate_rod_weight
from ..hardware_material import (
    HardwareKind,
    MaterialSpec,
    parse_hardware_material_context,
    resolve_hardware_material,
)
from data.type65_table import get_type65_data, snap_l_bucket
from data.m23_table import build_m23_item
from data.m28_table import get_m28_by_rod_size


def _material(
    kind: HardwareKind,
    *,
    service,
    overrides,
) -> MaterialSpec:
    return resolve_hardware_material(kind, service=service, overrides=overrides)


def _attach_material_identity(result: AnalysisResult, material: MaterialSpec):
    if result.entries:
        result.entries[-1].material_canonical_id = material.canonical_id


def _add_custom_entry(
    result: AnalysisResult,
    name: str,
    spec: str,
    material: MaterialSpec,
    quantity: int,
    unit_weight: float,
    unit: str = "SET",
    remark: str = "",
    category: str = "螺栓類",
):
    add_custom_entry(
        result,
        name,
        spec,
        material.name,
        quantity,
        unit_weight,
        unit,
        remark=remark,
        category=category,
    )
    _attach_material_identity(result, material)


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


# Stiffener plate dimensions (width_mm, height_mm, thickness_mm) by nominal pipe size.
# Source: geometry-based estimate, dimensions increase with pipe size.
# Weight = W × H × T × 7.85e-6 kg
_STIFFENER_PL = {
    12: (200, 150,  8),
    14: (225, 160,  8),
    16: (250, 170, 10),
    18: (280, 180, 10),
    20: (310, 190, 12),
    24: (370, 210, 12),
    28: (430, 230, 14),
    30: (460, 240, 14),
    32: (490, 260, 16),
    34: (520, 270, 16),
    36: (550, 280, 19),
    42: (630, 310, 19),
}


def _stiffener_pl(d_size: int) -> tuple[int, int, int]:
    """依管徑取最近（不超過）的 stiffener PL 規格。"""
    candidates = sorted(k for k in _STIFFENER_PL if k <= d_size)
    return _STIFFENER_PL[candidates[-1]] if candidates else (200, 150, 8)


def _build_inference_remark(item: dict | None) -> str:
    if not item or not item.get("row_inferred"):
        return ""
    return item.get("inference_notes", "row inferred from neighboring sizes")


def calculate(fullstring: str, overrides: dict | None = None) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    material_context = parse_hardware_material_context(
        overrides,
        all_hardware_keys=("hardware_material", "material", "upper_material"),
    )
    service = material_context.service
    material_overrides = material_context.material_overrides
    strut_material = _material(HardwareKind.STRUCTURAL_STRUT, service=service, overrides=material_overrides)
    rod_material = _material(HardwareKind.THREADED_ROD, service=service, overrides=material_overrides)
    bracket_material = _material(HardwareKind.BEAM_ATTACHMENT, service=service, overrides=material_overrides)
    stiffener_material = _material(HardwareKind.GUSSET_PLATE, service=service, overrides=material_overrides)

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

    # ① Cross Member ×1 (依 L bucket)
    sec_type, sec_dim = _parse_member_spec(member_spec)
    add_steel_section_entry(result, sec_type, sec_dim, l_mm, 1, strut_material.name)
    _attach_material_identity(result, strut_material)

    # ② Welded Eye Rod ×2 (M-23), 長度 ≈ H
    rod_item = build_m23_item(rod_size, h_mm)
    _add_custom_entry(
        result, "WELDED EYE ROD",
        rod_item["designation"] if rod_item else f"M-23, {rod_size}, L={h_mm}mm",
        rod_material, 2, rod_item["unit_weight_kg"] if rod_item else estimate_rod_weight(rod_size, h_mm), "PC",
        remark=_build_inference_remark(rod_item),
    )
    if not rod_item:
        result.warnings.append(f"M-23 table 尚無 rod size {rod_size}，暫以 rod 鋼材重量估算")

    # ③ Angle Bracket ×2 (M-28)
    bracket_item = get_m28_by_rod_size(rod_size)
    _add_custom_entry(
        result, "ANGLE BRACKET",
        bracket_item["type"] if bracket_item else f"M-28, {rod_size}",
        bracket_material, 2, bracket_item["unit_weight_kg"] if bracket_item else estimate_m28_weight(rod_size), "SET",
        remark=_build_inference_remark(bracket_item),
    )
    if not bracket_item:
        result.warnings.append(f"M-28 table 尚無 rod size {rod_size}，angle bracket 重量暫用估算值")

    # ④ Stiffener (D ≥ 12")
    if d_size >= 12:
        pl_w, pl_h, pl_t = _stiffener_pl(d_size)
        stiffener_wt = round(pl_w * pl_h * pl_t * 7.85e-6, 2)
        stiffener_desc = f"PL {pl_w}x{pl_h}x{pl_t}"
        _add_custom_entry(
            result, "STIFFENER",
            stiffener_desc,
            stiffener_material, 1, stiffener_wt, "SET"
        )
        result.warnings.append(f'12" & larger: Stiffener ({stiffener_desc}) 重量為幾何估算值')

    return result
