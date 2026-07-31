from core.calculator import analyze_single
from core.pipe_shoe_engine import get_sizing_context
from core.project_aggregation import ProjectInputRow, analyze_project_rows
from core.source_profiles import (
    CTCI_20E4588,
    CTCI_22A_5123A,
    CW_E25_24_HP6,
)


DESIGNATION_6_INCH = "52-6B(P)-A(A)-130-500"


def _entry(result, name):
    return next(entry for entry in result.entries if entry.name == name)


def test_type52_six_inch_uses_project_source_profile_boundary():
    cw = analyze_single(DESIGNATION_6_INCH, source_profile=CW_E25_24_HP6)
    ctci22 = analyze_single(
        DESIGNATION_6_INCH, source_profile=CTCI_22A_5123A
    )

    assert not cw.error
    assert not ctci22.error
    assert _entry(cw, "H型鋼").spec == "200*100*5.5"
    assert _entry(ctci22, "H型鋼").spec == "200*200*8"
    assert not any(entry.name == "FB_52Type_3" for entry in cw.entries)
    assert _entry(ctci22, "FB_52Type_3").quantity == 4


def test_type52_legacy_profile_uses_d80_e_dimension_from_20e4588():
    context = get_sizing_context(
        DESIGNATION_6_INCH,
        "52",
        source_profile=CTCI_20E4588,
    )

    assert context["E_mm"] == 15
    assert context["C_spec"] == "200*100*5.5"
    assert context["source_profile"] == CTCI_20E4588


def test_type52_retainer_recipe_follows_each_d63_source_drawing():
    cw_large = analyze_single(
        "52-10B-A-150-250",
        source_profile=CW_E25_24_HP6,
    )
    ctci22_large = analyze_single(
        "52-6B-A-150-250",
        source_profile=CTCI_22A_5123A,
    )
    legacy_small = analyze_single(
        "52-4B-A-150-250",
        source_profile=CTCI_20E4588,
    )
    legacy_mid = analyze_single(
        "52-6B-A-150-250",
        source_profile=CTCI_20E4588,
    )
    legacy_large = analyze_single(
        "52-10B-A-150-250",
        source_profile=CTCI_20E4588,
    )

    assert _entry(cw_large, "角鋼").spec == "40*40*5"
    assert any("PL12t" in warning for warning in cw_large.warnings)
    assert _entry(ctci22_large, "角鋼").spec == "40*40*5"
    assert any("PL6t" in warning for warning in ctci22_large.warnings)

    assert not any(entry.name == "角鋼" for entry in legacy_small.entries)
    assert _entry(
        legacy_small, "Retainer_52_9x150x25"
    ).quantity == 2
    assert _entry(legacy_mid, "角鋼").spec == "40*40*5"
    assert _entry(legacy_large, "角鋼").spec == "50*50*6"
    assert _entry(
        legacy_large, "Retainer_52_6x44x23"
    ).quantity == 2


def test_type53_guide_recipe_follows_each_d64_source_drawing():
    cw = analyze_single(
        "53-6B-A-150-250",
        source_profile=CW_E25_24_HP6,
    )
    ctci22 = analyze_single(
        "53-6B-A-150-250",
        source_profile=CTCI_22A_5123A,
    )
    legacy_small = analyze_single(
        "53-4B-A-150-250",
        source_profile=CTCI_20E4588,
    )
    legacy_mid = analyze_single(
        "53-6B-A-150-250",
        source_profile=CTCI_20E4588,
    )
    legacy_large = analyze_single(
        "53-10B-A-150-250",
        source_profile=CTCI_20E4588,
    )

    assert _entry(cw, "角鋼").spec == "40*40*5"
    assert not any(
        entry.name.startswith("Guide_53_")
        for entry in cw.entries
    )
    assert _entry(ctci22, "Guide_53_6x35x35").quantity == 2
    assert _entry(ctci22, "Guide_53_6x35x35").geometry.shape_kind == "triangle"
    assert not any(entry.name == "角鋼" for entry in legacy_small.entries)
    assert _entry(legacy_small, "Guide_53_9x150x40").quantity == 2
    assert _entry(legacy_mid, "角鋼").spec == "40*40*5"
    assert _entry(legacy_large, "角鋼").spec == "50*50*6"
    assert _entry(legacy_large, "Guide_53_6x44x44").quantity == 2


def test_type53_large_guide_is_blocked_when_d64_length_is_not_dimensioned():
    result = analyze_single(
        "53-26B-A-150-350",
        source_profile=CTCI_22A_5123A,
    )

    assert result.error
    assert "未給可信下料長度" in result.error


def test_type67_d81_uses_source_specific_boundary_and_clamp_gasket():
    cw = analyze_single(
        "67-6B-A-150-250",
        source_profile=CW_E25_24_HP6,
    )
    ctci22 = analyze_single(
        "67-6B-A-150-300",
        source_profile=CTCI_22A_5123A,
    )

    assert not cw.error
    assert not ctci22.error
    assert _entry(cw, "H型鋼").spec == "200*100*5.5"
    assert _entry(ctci22, "H型鋼").spec == "200*200*8"
    assert _entry(cw, "PIPE CLAMP").spec == "PCL-A-6B"
    assert _entry(cw, "NON-ASBESTOS").role == "gasket"
    assert any("M-4" in warning for warning in cw.warnings)
    assert any("M-47" in warning for warning in cw.warnings)


def test_type67_d81_defaults_lops_from_each_source_drawing():
    cw_small = analyze_single(
        "67-2B-A",
        source_profile=CW_E25_24_HP6,
    )
    cw_mid = analyze_single(
        "67-6B-A",
        source_profile=CW_E25_24_HP6,
    )
    ctci22_large_group = analyze_single(
        "67-6B-A",
        source_profile=CTCI_22A_5123A,
    )

    assert _entry(cw_small, "H型鋼").length == 150
    assert _entry(cw_mid, "H型鋼").length == 250
    assert _entry(ctci22_large_group, "H型鋼").length == 300


def test_type67_blocks_missing_legacy_d81_and_unhardened_fabricated_range():
    legacy = analyze_single(
        "67-6B-A",
        source_profile=CTCI_20E4588,
    )
    fabricated = analyze_single(
        "67-16B-A",
        source_profile=CW_E25_24_HP6,
    )

    assert legacy.error
    assert "尚未完成" in legacy.error
    assert fabricated.error
    assert "目前只完成 D-81 至 14 吋" in fabricated.error


def test_type54_d65_large_group_boundary_and_plate_follow_source_drawing():
    cw_8 = analyze_single(
        "54-8B-A-150-250",
        source_profile=CW_E25_24_HP6,
    )
    cw_10 = analyze_single(
        "54-10B-A-150-300",
        source_profile=CW_E25_24_HP6,
    )
    ctci_4 = analyze_single(
        "54-4B-A-150-250",
        source_profile=CTCI_22A_5123A,
    )
    ctci_6 = analyze_single(
        "54-6B-A-150-300",
        source_profile=CTCI_22A_5123A,
    )

    assert all(
        entry.name != "Retainer_54_12x150x40"
        for entry in cw_8.entries
    )
    assert _entry(cw_10, "Retainer_54_12x150x40").quantity == 2
    assert all(
        entry.name != "Retainer_54_6x150x40"
        for entry in ctci_4.entries
    )
    assert _entry(ctci_6, "Retainer_54_6x150x40").quantity == 2
    assert _entry(cw_10, "PIPE CLAMP") is not None
    assert _entry(ctci_6, "NON-ASBESTOS") is not None


def test_type55_d66_uses_d81_core_and_preserves_unresolved_ctci_shape():
    cw = analyze_single(
        "55-6B-A-150-300",
        source_profile=CW_E25_24_HP6,
    )
    ctci = analyze_single(
        "55-6B-A-150-300",
        source_profile=CTCI_22A_5123A,
    )

    for result in (cw, ctci):
        assert not result.error
        assert _entry(result, "角鋼").spec == "40*40*5"
        assert _entry(result, "角鋼").quantity == 2
        assert _entry(result, "PIPE CLAMP") is not None
        assert _entry(result, "NON-ASBESTOS") is not None
    assert not any("35×35" in warning for warning in cw.warnings)
    assert any("35×35" in warning for warning in ctci.warnings)


def test_type85_delegates_to_same_source_d80_instead_of_type52_recipe():
    result = analyze_single(
        "85-6B(P)-A(A)-150-250",
        source_profile=CW_E25_24_HP6,
    )

    assert not result.error
    assert result.meta["fabrication"]["branch"] == "D-80"
    assert {
        entry.geometry.component_id for entry in result.entries
    } == {"D80-REINFORCING-PAD", "D80-MEMBER-C"}
    assert all(
        entry.geometry.parameters["parent_type"] == "85"
        for entry in result.entries
    )


def test_source_profile_is_recorded_in_result_meta():
    result = analyze_single(
        DESIGNATION_6_INCH,
        source_profile=CTCI_22A_5123A,
    )

    assert result.meta["source_profile"] == CTCI_22A_5123A
    assert "22A_5123A" in result.meta["source_profile_label"]
    assert result.meta["source_drawing_standard"] == "D7TS-701-E"
    assert result.meta["source_profile_rule_status"] == "partial"
    assert any("僅開放已逐圖建檔" in item for item in result.warnings)


def test_reviewed_ctci_type01_uses_source_specific_rules():
    result = analyze_single(
        "01-24B-05B",
        source_profile=CTCI_22A_5123A,
    )

    assert not result.error
    assert result.entries[0].spec == '12"*STD.WT'
    assert result.entries[0].length == 1147
    assert result.meta["source_profile_rule_status"] == "partial"


def test_row_source_profile_explicitly_overrides_project_profile():
    rows = [
        ProjectInputRow(DESIGNATION_6_INCH),
        ProjectInputRow(
            DESIGNATION_6_INCH,
            source_profile=CTCI_20E4588,
        ),
    ]

    project = analyze_project_rows(
        rows,
        source_profile=CTCI_22A_5123A,
    )

    assert project.source_profile == CTCI_22A_5123A
    assert [
        row.single_result.meta["source_profile"] for row in project.rows
    ] == [CTCI_22A_5123A, CTCI_20E4588]
