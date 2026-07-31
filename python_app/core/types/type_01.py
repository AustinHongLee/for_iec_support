"""
Type 01 / 01T 計算器 (Config 驅動)

Elbow 接入 (預設, code=01):
  格式: 01-2B-05A
  上段管: L(查表) + 100mm

Tee 接入 (code=01T):
  格式: 01T-2B-05A
  上段管: 100 + M(ASME B16.9 TEE_DATA, 依主管線尺寸查表)

共通:
  Supporting Pipe B 為單一連續構件，總切長 = H + L（tee 時 H + M）
  Supporting Pipe B 材質跟隨主管線 (預設 SUS304, 由 context 傳入)
  M42 底板依來源圖與字母代碼

查表資料來源: configs/type_01.json (唯一 source of truth)
  若 JSON 遺失或損毀, 計算會直接報錯, 請從備份還原或重新建立設定檔。
"""
from ..models import AnalysisResult
from ..parser import get_part, get_lookup_value
from ..pipe import add_pipe_entry
from ..issues import register_host_m42_variance, register_source_envelope
from ..m42 import perform_action_by_letter, source_allows_m42_type
from ..config_loader import load_config
from ..hardware_material import HardwareKind
from ..material_specs import material_spec
from ..source_profiles import normalize_source_profile
from ..truth import make_evidence
from data.tee_table import get_tee_M


_PAVING_LOW_POINT_M42_LETTERS = {"A", "B", "E", "G"}


# ─── 建立查表 (從 JSON config 讀取) ───

def _load_profile(source_profile: str | None) -> tuple[str, dict, dict]:
    """載入來源 profile 與其 D-1 尺寸表。

    JSON 為唯一 source of truth，若讀取失敗則直接報錯。
    """
    config = load_config("01", strict=True)
    if not config:
        raise FileNotFoundError(
            "Type 01 設定檔遺失或損毀 (configs/type_01.json)，"
            "請從備份還原或透過 GUI 設定介面重新建立。"
        )
    profile_id = normalize_source_profile(source_profile)
    try:
        profile = config["source_profiles"][profile_id]
    except KeyError as exc:
        raise ValueError(f"Type 01 尚未建立來源 profile: {profile_id}") from exc
    table_source = profile["table_source"]
    rows = (
        config["table"]
        if table_source == "root"
        else config["source_tables"][table_source]
    )
    return profile_id, profile, {int(row["line_size"]): row for row in rows}


def _h_within_profile(h_value: int, profile: dict) -> bool:
    limit = int(profile["h_max_mm"])
    if profile.get("h_max_inclusive"):
        return h_value <= limit
    return h_value < limit


def _decorate_fabrication_entries(
    result: AnalysisResult,
    *,
    profile_id: str,
    profile: dict,
    line_size: int,
    support_pipe_size: str,
    pipe_thickness: str,
    h_value: int,
    interface_dimension: int,
    connection: str,
    lower_component: str,
    restrain_function: str,
) -> None:
    pipe_blockers = [
        "Supporting Pipe B 與彎頭/三通相貫的頂端 cope/fishmouth 展開輪廓尚未參數化"
    ]
    if connection == "tee":
        pipe_blockers.append(
            "D-1 僅示意特殊主管/三通接法；M 值取 ASME B16.9，但接合切口尚未由來源圖核定"
        )
    if restrain_function:
        pipe_blockers.append(
            f"RESTRAIN FUNCTION {restrain_function} 的 restraint element 僅有示意，未提供零件尺寸"
        )

    pipe_entry = result.entries[0]
    pipe_entry.geometry.component_id = "D1-SUPPORTING-PIPE-B"
    pipe_entry.geometry.source_drawing = profile["drawing"]
    pipe_entry.geometry.source_revision = profile["revision"]
    pipe_entry.geometry.shape_kind = "dummy_support_pipe_with_top_cope"
    pipe_entry.geometry.shape_spec = (
        f'{support_pipe_size}"*{pipe_thickness}; CUT L={pipe_entry.length:g}; '
        f"TOP COPE TO {connection.upper()}; WEEP HOLE DIA6 AT LOW POINT"
    )
    pipe_entry.geometry.fabrication_ready = False
    pipe_entry.geometry.fabrication_blockers = list(pipe_blockers)
    pipe_entry.geometry.parameters = {
        "supported_line_size_in": line_size,
        "supporting_pipe_size_in": support_pipe_size,
        "supporting_pipe_schedule": pipe_thickness,
        "H_mm": h_value,
        "interface_dimension_mm": interface_dimension,
        "cut_length_mm": pipe_entry.length,
        "weep_hole_diameter_mm": 6,
        "weep_hole_location": "low point immediately above base weld per D-1",
        "field_weld_mm": 6,
        "connection": connection,
        "lower_component": lower_component,
        "restrain_function": restrain_function or "resting_only",
    }

    m42_source = " / ".join(profile["m42_drawings"])
    for entry in result.entries[1:]:
        entry.geometry.source_drawing = m42_source
        entry.geometry.source_revision = profile["m42_revision"]
        entry.geometry.fabrication_ready = True
        if entry.category == "鋼板類":
            plate_code = entry.name.split("_")[1].upper()
            entry.geometry.component_id = f"M42-PLATE-{plate_code}"
            entry.geometry.shape_kind = "rectangular_base_plate"
            if not entry.geometry.shape_spec:
                entry.geometry.shape_spec = (
                    f"{entry.length:g}x{entry.width:g}x{entry.spec}t"
                )
            entry.geometry.parameters.update(
                {
                    "length_mm": entry.length,
                    "width_mm": entry.width,
                    "thickness_mm": float(entry.spec),
                }
            )
        elif entry.category == "型鋼類":
            entry.geometry.component_id = "M42-ANGLE-RETAINER"
            entry.geometry.shape_kind = "stock_section_cut"
            entry.geometry.parameters.update(
                {"cut_length_mm": entry.length, "quantity": entry.quantity}
            )
        elif entry.category == "螺栓類":
            entry.geometry.component_id = "M42-FASTENER"
            entry.geometry.shape_kind = "purchased_fastener"
            entry.geometry.parameters.update(
                {"spec": entry.spec, "quantity": entry.quantity}
            )

    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": profile["drawing"],
        "source_revision": profile["revision"],
        "branch": f"D-1/{connection}",
        "bom_ready": True,
        "fabrication_ready": False,
        "blockers": pipe_blockers,
        "dimensions": {
            "H_mm": h_value,
            "interface_dimension_mm": interface_dimension,
            "supporting_pipe_cut_length_mm": pipe_entry.length,
            "supporting_pipe_size": support_pipe_size,
            "supporting_pipe_schedule": pipe_thickness,
        },
    }


def calculate(fullstring: str, connection: str = "elbow",
              upper_material: str = "SUS304",
              overrides: dict = None,
              source_profile: str | None = None) -> AnalysisResult:
    """
    計算 Type 01 (或 01T) 材料清單

    Parameters
    ----------
    fullstring : 編碼字串
    connection : "elbow" 或 "tee"
    upper_material : 上段管材質
    overrides : 單筆覆寫 dict, 可包含:
        pipe_size, schedule, l_value
    """
    overrides = overrides or {}
    result = AnalysisResult(fullstring=fullstring)
    try:
        profile_id, profile, table = _load_profile(source_profile)
    except (FileNotFoundError, ValueError) as exc:
        result.error = str(exc)
        return result

    # 解析第二段: 主管線尺寸 (Line Size "A")
    try:
        part2 = get_part(fullstring, 2)
        line_size = int(get_lookup_value(part2))
    except (TypeError, ValueError):
        result.error = "Type 01: 第二段必須是圖面支援的整數主管線尺寸"
        return result

    if line_size not in table:
        result.error = (
            f"Type 01 / {profile_id}: 來源 D-1 不支援管徑 {line_size}\""
        )
        return result

    row = table[line_size]

    # 套用覆寫 (有覆寫值時優先使用)
    support_pipe_size = overrides.get("pipe_size") or row["pipe_size"]
    pipe_thickness = overrides.get("schedule") or row["schedule"]

    # 解析第三段: H高度 + M42字母代碼
    part3 = get_part(fullstring, 3)
    if len(part3) < 2 or not part3[:-1].isdigit() or not part3[-1].isalpha():
        result.error = "Type 01: 第三段格式應為 HH+M42 字母，例如 05B"
        return result
    letter = part3[-1].upper()
    h_value = int(part3[:-1]) * 100
    if not _h_within_profile(h_value, profile):
        relation = "≤" if profile.get("h_max_inclusive") else "<"
        if not register_source_envelope(
            result,
            type_label=f"Type 01 / {profile_id}",
            source_ref=f"D-1 H{relation}{profile['h_max_mm']}mm",
            checks=(
                (
                    "H",
                    h_value,
                    int(profile["h_max_mm"]),
                    bool(profile.get("h_max_inclusive")),
                ),
            ),
        ):
            return result
    if letter not in profile["allowed_lower_components"]:
        if not source_allows_m42_type(profile_id, letter):
            result.error = (
                f"Type 01 / {profile_id}: M-42 下部構件 {letter} "
                "不存在於此來源 M-42 圖"
            )
            return result
        register_host_m42_variance(
            result,
            type_label=f"Type 01 / {profile_id}",
            source_ref="D-1",
            letter=letter,
            host_allowed=profile["allowed_lower_components"],
        )

    restrain_function = str(get_part(fullstring, 4) or "").strip().upper()
    if restrain_function not in {"", "A", "G", "F"}:
        result.error = (
            f"Type 01: 不支援 RESTRAIN FUNCTION {restrain_function!r}；"
            "圖面僅定義空白/A/G/F"
        )
        return result

    if (
        profile_id != "ctci_22a_5123a"
        and letter in _PAVING_LOW_POINT_M42_LETTERS
    ):
        result.warnings.append(
            f"M42 底座類型 {letter} — H 應從鋪面最低點起算 (NOTE 6)"
        )

    # ─── Supporting Pipe B：來源圖是一支連續假管，整支材質同主管 ───
    support_pipe_material = material_spec(
        HardwareKind.SUPPORT_PIPE,
        upper_material,
    )
    if connection == "tee":
        interface_dimension = get_tee_M(line_size)
    else:
        l_value = overrides.get("l_value") or row["L"]
        if isinstance(l_value, str):
            l_value = int(l_value)
        interface_dimension = int(l_value)
    support_pipe_cut_length = h_value + interface_dimension
    add_pipe_entry(
        result,
        support_pipe_size,
        pipe_thickness,
        support_pipe_cut_length,
        support_pipe_material,
    )

    # ─── M42 底板 ───
    perform_action_by_letter(
        result,
        letter,
        support_pipe_size,
        source_profile=profile_id,
    )
    if result.error:
        result.entries.clear()
        return result

    _decorate_fabrication_entries(
        result,
        profile_id=profile_id,
        profile=profile,
        line_size=line_size,
        support_pipe_size=support_pipe_size,
        pipe_thickness=pipe_thickness,
        h_value=h_value,
        interface_dimension=interface_dimension,
        connection=connection,
        lower_component=letter,
        restrain_function=restrain_function,
    )
    result.warnings.append(
        "Type 01 BOM 已依來源圖核對；加工圖仍缺假管頂端 cope/fishmouth 展開輪廓"
    )
    result.evidence.extend(
        [
            make_evidence(
                "supporting_pipe_table",
                row,
                "visual_transcription",
                source=profile["drawing"],
                confidence=0.95,
                note=f"{profile_id} D-1 LINE SIZE/PIPE SIZE/L table",
            ),
            make_evidence(
                "supporting_pipe_cut_length_mm",
                support_pipe_cut_length,
                "formula",
                source=profile["drawing"],
                confidence=0.95,
                note="單一 Supporting Pipe B；elbow=H+L，tee=H+M",
            ),
        ]
    )

    return result
