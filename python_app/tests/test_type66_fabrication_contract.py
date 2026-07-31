from core.calculator import analyze_single
from core.pipe_shoe_engine import get_fabrication_context
from core.source_profiles import (
    CTCI_20E4588,
    CTCI_22A_5123A,
    CW_E25_24_HP6,
)
from export.inventor_params import extract_params


def _entry(result, name):
    return next(entry for entry in result.entries if entry.name == name)


def _values(params):
    return {name: value for name, value, _unit, _comment in params["params"]}


def test_cw_small_d80_is_shop_drawing_ready_and_traceable():
    result = analyze_single(
        "66-6B(P)-A(A)-150-250",
        source_profile=CW_E25_24_HP6,
    )

    assert not result.error
    fabrication = result.meta["fabrication"]
    assert fabrication["fabrication_ready"] is True
    assert fabrication["branch"] == "D-80"
    assert fabrication["source_drawing"] == "TYPE-66_D-80.pdf"
    assert fabrication["dimensions"]["member_c_full_spec"] == "H200*100*5.5*8"
    assert fabrication["dimensions"]["saddle_angle_deg"] == 120

    member = _entry(result, "H型鋼")
    assert member.material == "AS"
    assert member.geometry.component_id == "D80-MEMBER-C"
    assert member.geometry.fabrication_ready is True
    assert member.geometry.source_revision == "1"
    assert member.geometry.parameters["raw_section"] == "H200*100*5.5*8"
    assert member.geometry.parameters["cut_length_mm"] == 250
    assert "SADDLE=120deg" in member.geometry.shape_spec

    pad = _entry(result, "Pad_52Type")
    assert pad.material == "AS"
    assert pad.geometry.component_id == "D80-REINFORCING-PAD"
    assert pad.geometry.parameters["weep_hole_diameter_mm"] == 6
    assert pad.geometry.parameters["roll_angle_deg"] == 120


def test_legacy_material_symbol_separates_cs_shoe_from_ss_pad():
    result = analyze_single(
        "66-6B(P)-A(S)-150-250",
        source_profile=CTCI_20E4588,
    )

    assert not result.error
    assert _entry(result, "H型鋼").material == "A36/SS400"
    assert _entry(result, "Pad_52Type").material == "SUS304"
    assert any(
        "45 degree V-NOTCH" in item
        for item in result.meta["fabrication"]["special_fabrication"]
    )


def test_reinforced_d80_ranges_block_calculation_only_geometry():
    cw = analyze_single(
        "66-10B(P)-A(A)-150-250",
        source_profile=CW_E25_24_HP6,
    )
    ctci = analyze_single(
        "66-6B(P)-A(A)-150-250",
        source_profile=CTCI_22A_5123A,
    )

    for result in (cw, ctci):
        assert result.error
        assert "尚未達可出加工圖程度" in result.error
        assert not result.entries
        assert result.meta["fabrication"]["fabrication_ready"] is False


def test_large_d80b_and_d80c_tables_are_preserved_for_future_cad_recipe():
    cw = get_fabrication_context(
        "66-44B-B(A)-200-940",
        "66",
        source_profile=CW_E25_24_HP6,
    )
    ctci = get_fabrication_context(
        "66-78B-C(A)-300-600",
        "66",
        source_profile=CTCI_22A_5123A,
    )
    legacy = get_fabrication_context(
        "66-30B-A(A)-150-540",
        "66",
        source_profile=CTCI_20E4588,
    )

    assert cw["branch"] == "D-80B"
    assert cw["dimensions"]["H"] == {"A": 710, "B": 860}
    assert cw["dimensions"]["L"] == 940
    assert ctci["branch"] == "D-80C"
    assert ctci["dimensions"]["a"] == {"A": 536, "B": 586, "C": 686}
    assert ctci["dimensions"]["b"] == 1600
    assert ctci["dimensions"]["L"] == 600
    assert legacy["component_contract_status"] == "unsupported_table_row"


def test_inventor_contract_exposes_readiness_and_blocks_fake_large_geometry():
    ready = extract_params(
        "66-6B(P)-A(A)-150-250",
        "66",
        source_profile=CW_E25_24_HP6,
    )
    blocked = extract_params(
        "66-20B(P)-A(A)-200-600",
        "66",
        source_profile=CW_E25_24_HP6,
    )

    ready_values = _values(ready)
    blocked_values = _values(blocked)
    assert ready["fabrication_ready"] is True
    assert ready_values["IEC_FabricationReady"] == "YES"
    assert ready_values["fab_member_c_full_spec"] == "H200*100*5.5*8"
    assert blocked["fabrication_ready"] is False
    assert blocked_values["IEC_FabricationReady"] == "NO"
    assert "C_type" not in blocked_values
