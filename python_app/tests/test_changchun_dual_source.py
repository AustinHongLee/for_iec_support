"""Golden tests for the E25-24 + DES-M15172 combined project source."""

import pytest

from companies.registry import design_company_label
from core.calculator import analyze_single
from core.project_aggregation import ProjectInputRow, analyze_project_rows
from core.source_profiles import (
    CHANGCHUN_DES_M15172,
    CW_CHANGCHUN_E25_24,
    CW_E25_24_HP6,
    EKO,
    source_profile_choices,
)
from export.excel.confidence_summary import build_export_context


def _analyze(designation: str, overrides: dict | None = None):
    return analyze_single(
        designation,
        overrides,
        source_profile=CW_CHANGCHUN_E25_24,
    )


def _entry(result, name):
    return next(item for item in result.entries if item.name == name)


def test_source_choices_expose_standalone_and_combined_changchun_profiles():
    choices = dict(source_profile_choices())
    assert "長春" in choices[CHANGCHUN_DES_M15172]
    assert "中威＋長春" in choices[CW_CHANGCHUN_E25_24]


def test_combined_profile_routes_numeric_type_to_actual_chungwei_source():
    combined = _analyze("54-6B-A-150-250")
    direct = analyze_single(
        "54-6B-A-150-250",
        source_profile=CW_E25_24_HP6,
    )

    assert not combined.error
    assert combined.total_weight == direct.total_weight
    assert combined.meta["source_profile"] == CW_E25_24_HP6
    assert combined.meta["project_source_profile"] == CW_CHANGCHUN_E25_24


def test_combined_project_routes_each_family_without_guessing():
    project = analyze_project_rows(
        [
            ProjectInputRow("54-6B-A-150-250"),
            ProjectInputRow('S1-10"-125H'),
            ProjectInputRow("SS13SB-700L"),
            ProjectInputRow("SPS-001-C125-10-12-B"),
        ],
        source_profile=CW_CHANGCHUN_E25_24,
    )

    assert not project.errors
    assert [
        row.single_result.meta["source_profile"] for row in project.rows
    ] == [
        CW_E25_24_HP6,
        CHANGCHUN_DES_M15172,
        CHANGCHUN_DES_M15172,
        CW_E25_24_HP6,
    ]


def test_same_s1_code_is_source_locked_at_the_ten_inch_boundary():
    changchun_10 = _analyze('S1-10"-125H')
    changchun_12 = _analyze('S1-12"-125H')
    eko_10 = analyze_single('S1-10"-125H', source_profile=EKO)

    assert not any(item.name == "加強板" for item in changchun_10.entries)
    assert _entry(changchun_12, "加強板").quantity == 2
    assert _entry(eko_10, "加強板").quantity == 2


def test_explicit_chungwei_profile_rejects_ambiguous_s1_instead_of_using_eko():
    result = analyze_single(
        'S1-10"-125H',
        source_profile=CW_E25_24_HP6,
    )

    assert result.error
    assert "本列目前選用" in result.error
    assert "益高" in result.error
    assert "長春" in result.error


def test_source_aware_company_labels_match_combined_routing():
    assert design_company_label(
        "54-6B-A-150-250", CW_CHANGCHUN_E25_24
    ) == "中威"
    assert design_company_label(
        'S1-10"-125H', CW_CHANGCHUN_E25_24
    ) == "長春"
    assert design_company_label('S1-10"-125H', EKO) == "益高"


def test_fs15_uses_owner_standard_short_fasteners_and_structured_base():
    result = _analyze("FS15HA-1-900H-300H1")

    assert not result.error
    assert _entry(result, "角鋼立柱").length == 900
    assert _entry(result, "角鋼頂臂").length == 300
    assert _entry(result, "L型基礎螺栓").spec == "M16x200L"
    base = _entry(result, "底板")
    assert (base.length, base.width) == (260, 260)
    assert base.geometry.holes.pitch_x == 190
    assert base.geometry.holes.pitch_y == 190

    expansion = _analyze("FS15HE-1-900H-300H1")
    bolted = _analyze("FS15HB-1-900H")
    assert _entry(expansion, "擴展螺栓").spec == "EB2-M16-100L"
    assert _entry(bolted, "螺栓連帽").spec == "M16x40L"


def test_pu5_uses_owner_standard_base_holes_and_70l_expansion_bolt():
    result = _analyze('PU5E-1.1/2"-500L')

    assert not result.error
    assert _entry(result, "托撐角鋼").length == 500
    assert _entry(result, "擴展螺栓").spec == "EB2-M12-70L"
    base = _entry(result, "底板")
    assert (base.length, base.width) == (150, 150)
    assert base.geometry.holes.diameter == 14
    rod = _entry(result, "M-26 U-BOLT ROD")
    nuts = _entry(result, "M-26 FINISHED HEX NUTS")
    expansion = _entry(result, "擴展螺栓")
    assert rod.spec.startswith("UB-1 1/2B;")
    assert rod.unit_weight > 0
    assert nuts.unit_weight > 0
    assert expansion.unit_weight > 0
    assert expansion.geometry.parameters["weight_estimate"][
        "kind"
    ] == "expansion_bolt"


def test_pu5_accepts_project_nominal_bore_b_suffix():
    result = _analyze("PU5B-1.1/2B-600L")

    assert not result.error
    assert _entry(result, "托撐角鋼").length == 600
    assert _entry(result, "M-26 U-BOLT ROD").spec.startswith("UB-1 1/2B;")
    assert _entry(result, "M-26 FINISHED HEX NUTS").unit_weight > 0
    fastener = _entry(result, "螺栓連帽含墊圈")
    assert fastener.spec == "M12x50L W./WASHER"
    assert fastener.unit_weight > 0
    assert fastener.geometry.parameters["weight_estimate"]["washer_count"] == 1


def test_combined_profile_routes_project_ub1_alias_to_cw_m26():
    result = _analyze('UB1-4"')

    assert not result.error
    assert result.meta["fabrication"]["branch"] == "M-26-PROJECT-ALIAS"
    assert result.meta["issue_summary"]["highest_severity"] == "warning"
    rod = _entry(result, "M-26 U-BOLT ROD")
    nuts = _entry(result, "M-26 FINISHED HEX NUTS")
    assert rod.spec.startswith("UB-4B;")
    assert rod.unit_weight > 0
    assert nuts.quantity == 4
    assert nuts.unit_weight > 0
    assert nuts.geometry.parameters["weight_basis"].startswith(
        "proportional finished-hex-nut"
    )
    assert not result.meta["fabrication"]["bom_ready"]


def test_combined_profile_converts_open_nominal_size_to_cw_po1():
    expected = {
        'OPEN-1"': ("PO1-90", 90, 1.06),
        'OPEN-1.1/2"': ("PO1-120", 120, 1.41),
        'OPEN-4"': ("PO1-180", 180, 2.12),
        'OPEN-6"': ("PO1-240", 240, 2.83),
    }

    for designation, (resolved, length, weight) in expected.items():
        result = _analyze(designation)
        assert not result.error, designation
        assembly = result.meta["fabrication"]["assembly_dimensions"]
        assert assembly["resolved_po_designation"] == resolved
        assert assembly["selected_table_L_mm"] == length
        assert result.total_weight == pytest.approx(weight, abs=0.01)
        assert result.meta["issue_summary"]["highest_severity"] == "high"
        assert not result.meta["fabrication"]["bom_ready"]
        assert {entry.spec for entry in result.entries} == {
            "FB50×6",
            "FB75×6",
        }


def test_open_alias_selects_po2_po3_and_keeps_600mm_upper_bound():
    po2 = _analyze('OPEN-10"')
    po3 = _analyze('OPEN-4"', {"opening_surface": "checker_plate"})
    too_large = _analyze('OPEN-24"')

    assert not po2.error
    po2_assembly = po2.meta["fabrication"]["assembly_dimensions"]
    assert po2_assembly["resolved_po_designation"] == "PO2-400"
    assert po2_assembly["minimum_required_L_mm"] == pytest.approx(323.0)
    assert po2.total_weight == pytest.approx(7.4)
    assert _entry(po2, "PO2 環形開孔補強扁鐵").length == pytest.approx(
        3.141592653589793 * 406
    )

    assert not po3.error
    po3_assembly = po3.meta["fabrication"]["assembly_dimensions"]
    assert po3_assembly["resolved_po_designation"] == "PO3-200"
    assert po3_assembly["surface"] == "checker_plate"
    assert po3.total_weight == pytest.approx(0.762)

    assert too_large.error
    assert "超出PO系列L≤600mm範圍" in too_large.error
    assert not too_large.entries


def test_s2_preserves_exact_table_and_blocks_unreleased_plate_development():
    result = _analyze('S2A-6"')

    assert not result.error
    assert _entry(result, "上導架").spec == "25*25*3"
    assert _entry(result, "下導架").spec == "50*50*6"
    assert result.meta["fabrication"]["assembly_dimensions"]["table_row"] == {
        "size": 6,
        "A": 6,
        "B": 100,
        "C": 200,
        "D": 300,
        "E": 360,
    }
    assert not result.meta["fabrication"]["fabrication_ready"]
    assert any("禁止以外包矩形" in warning for warning in result.warnings)


def test_ss2_has_source_specific_plate_outer_size_holes_and_fastener():
    result = _analyze("SS2E-2-500L")

    assert not result.error
    assert _entry(result, "懸臂槽鋼").spec == "100*50*5"
    base = _entry(result, "底板")
    assert (base.length, base.width) == (160, 200)
    assert base.geometry.holes.pitch_x == 100
    assert base.geometry.holes.pitch_y == 140
    assert base.geometry.holes.diameter == 23
    assert _entry(result, "擴展螺栓").spec == "EB2-M20-130L"


def test_ss5_and_ss6_use_three_member_frame_and_owner_fasteners():
    ss5 = _analyze("SS5E-2-500H-400L")
    ss6 = _analyze("SS6B-2-500H-400L")

    assert _entry(ss5, "垂直角鋼").quantity == 2
    assert _entry(ss5, "頂部水平角鋼").length == 400
    assert _entry(ss5, "圓棒止擋").quantity == 2
    assert _entry(ss5, "擴展螺栓").spec == "EB2-M16-100L"
    assert _entry(ss6, "垂直角鋼").quantity == 2
    assert _entry(ss6, "底部水平角鋼").length == 400
    assert _entry(ss6, "螺栓連帽").spec == "M16x55L"
    base = _entry(ss6, "底板")
    assert (base.length, base.width, base.quantity) == (90, 160, 2)
    assert base.geometry.holes.count == 2


def test_ss13_is_owner_cantilever_not_eko_double_height_portal():
    result = _analyze("SS13SB-700L")

    assert not result.error
    assert _entry(result, "懸臂角鋼").spec == "75*75*9"
    assert _entry(result, "懸臂角鋼").length == 700
    assert _entry(result, "端部止擋板").quantity == 1
    assert _entry(result, "底板").geometry.holes.diameter == 15
    assert not any(item.name.startswith("立柱") for item in result.entries)


def test_ss17_and_ss20_preserve_field_cut_blockers_and_exact_base_plates():
    ss17 = _analyze("SS17B-1000H-800L")
    ss20 = _analyze("SS20B-1000H-500L")

    assert _entry(ss17, "H型鋼立柱").quantity == 2
    assert _entry(ss17, "H型鋼橫樑").length == 800
    assert (_entry(ss17, "底板").length, _entry(ss17, "底板").width) == (
        290,
        195,
    )
    assert not ss17.meta["fabrication"]["fabrication_ready"]
    assert _entry(ss20, "水平角鋼").length == 500
    assert _entry(ss20, "垂直角鋼").length == 1000
    assert (_entry(ss20, "底板").length, _entry(ss20, "底板").width) == (
        215,
        170,
    )


def test_changchun_ss_continuous_dimensions_use_bounded_warning_levels():
    warning_cases = [
        "SS5B-2-650H-400L",
        "SS6B-2-653H-650L",
        "SS17B-1700H-3000L",
        "SS20B-1675H-500L",
        "SS20B-975H-700L",
    ]
    high_cases = [
        "SS2E-1-700L",
        "SS6B-3-850H-800L",
        "SS13VB-1100L",
        "SS17B-2500H-3000L",
        "SS20B-1965H-500L",
        "SS20B-700H-900L",
    ]

    for designation in warning_cases:
        result = _analyze(designation)
        assert not result.error, designation
        assert result.meta["issue_summary"]["highest_severity"] == "warning"
        assert result.meta["fabrication"]["bom_ready"]
        assert not result.meta["fabrication"]["fabrication_ready"]

    for designation in high_cases:
        result = _analyze(designation)
        assert not result.error, designation
        assert result.meta["issue_summary"]["highest_severity"] == "high"
        assert not result.meta["fabrication"]["bom_ready"]
        assert not result.meta["fabrication"]["fabrication_ready"]

    ss13 = _analyze("SS13VB-1100L")
    ss17 = _analyze("SS17B-2500H-3000L")
    assert ss13.meta["fabrication"]["assembly_dimensions"]["max_load_kg"] is None
    assert ss17.meta["fabrication"]["assembly_dimensions"]["max_load_kg"] is None
    assert "不得套用到超界尺寸" in ss13.warnings[0]
    assert "不得套用到超界尺寸" in ss17.warnings[0]


def test_changchun_ss_envelopes_keep_lower_and_unbounded_cases_hard():
    for designation in [
        "SS2E-1-200L",
        "SS20B-1000H-200L",
        "SS6B-1-1550H-400L",
        "SS17B-4000H-3000L",
    ]:
        result = _analyze(designation)
        assert result.error, designation
        assert not result.entries


def test_sps001_is_new_e2524_construction_and_accepts_final_field_lengths():
    nominal = _analyze("SPS-001-C125-10-12-B")
    final = analyze_single(
        "SPS-001-C125-10-12-B",
        {"final_h_mm": 980, "final_l_mm": 1180},
        source_profile=CW_CHANGCHUN_E25_24,
    )

    assert not nominal.error
    assert _entry(nominal, "垂直構件 M").spec == "125*65*6"
    assert _entry(nominal, "水平構件 M").length == 1200
    plate = _entry(nominal, "固定板")
    assert (plate.length, plate.width) == (265, 175)
    assert plate.geometry.holes.pitch_x == 195
    assert plate.geometry.holes.pitch_y == 105
    assert not nominal.meta["fabrication"]["fabrication_ready"]
    assert final.meta["fabrication"]["fabrication_ready"]
    assert _entry(final, "垂直構件 M").length == 980
    assert _entry(final, "水平構件 M").length == 1180


def test_export_context_records_actual_split_under_combined_profile():
    project = analyze_project_rows(
        [
            ProjectInputRow("54-6B-A-150-250"),
            ProjectInputRow('S1-10"-125H'),
            ProjectInputRow("SS13SW-700L"),
        ],
        source_profile=CW_CHANGCHUN_E25_24,
    )

    context = build_export_context(project, mode="estimate")
    routed = {
        item["source_profile"]: item["rows"]
        for item in context["source_routing"]
    }
    assert routed == {
        CW_E25_24_HP6: 1,
        CHANGCHUN_DES_M15172: 2,
    }
