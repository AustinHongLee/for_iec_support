import pytest

from core.calculator import analyze_single


@pytest.mark.parametrize("type_id", ["31", "32", "33"])
def test_type31_33_source_tables_are_not_interchanged(type_id):
    assert "未表列 MEMBER C100" in analyze_single(
        f"{type_id}-C100-1215", source_profile="ctci_22a_5123a"
    ).error
    assert not analyze_single(
        f"{type_id}-C100-1215", source_profile="ctci_20e4588"
    ).error
    overrun = analyze_single(
        f"{type_id}-C150-2020", source_profile="cw_e25_24_hp6"
    )
    assert not overrun.error
    assert overrun.meta["issues"][0]["severity"] == "high"
    assert not analyze_single(
        f"{type_id}-C150-2020", source_profile="ctci_22a_5123a"
    ).error


def test_type31_upstand_frame_is_h_l_h():
    result = analyze_single("31-L50-1010", source_profile="cw_e25_24_hp6")
    assert [entry.length for entry in result.entries] == [1000, 1000, 1000]
    assert [entry.geometry.component_id for entry in result.entries] == [
        "D36-LEG-1", "D36-TOP-BEAM", "D36-LEG-2"
    ]


def test_type32_hanger_frame_is_h_l_h():
    result = analyze_single("32-L75-1015", source_profile="cw_e25_24_hp6")
    assert [entry.length for entry in result.entries] == [1500, 1000, 1500]
    assert result.entries[1].geometry.component_id == "D37-BOTTOM-BEAM"


def test_type33_is_only_one_post_and_one_beam():
    result = analyze_single("33-L75-1015", source_profile="cw_e25_24_hp6")
    assert [entry.length for entry in result.entries] == [1500, 1000]
    assert [entry.geometry.component_id for entry in result.entries] == [
        "D38-END-POST", "D38-BOTTOM-BEAM"
    ]


@pytest.mark.parametrize("type_id", ["31", "32", "33"])
def test_type31_33_keep_fabrication_interface_blockers(type_id):
    result = analyze_single(f"{type_id}-L50-1010", source_profile="cw_e25_24_hp6")
    assert result.meta["fabrication"]["bom_ready"] is True
    assert result.meta["fabrication"]["fabrication_ready"] is False
    assert any("existing steel" in item for item in result.meta["fabrication"]["blockers"])
