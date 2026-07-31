"""Drawing-truth locks for DSP-500-006 Type 01C~26C."""

import json
from pathlib import Path

import pytest

from core import config_loader
from core.calculator import analyze_single, get_supported_types
from core.source_profiles import CTCI_20E4588


COLD_TYPE_IDS = [f"{number:02d}C" for number in range(1, 27)]


def _parameters(result):
    assert not result.error
    assemblies = [
        entry
        for entry in result.entries
        if entry.geometry.shape_kind == "cold_support_assembly_reference"
    ]
    assert len(assemblies) == 1
    return assemblies[0].geometry.parameters


def _source_row(result, name):
    return _parameters(result)["source_rows"][name]


@pytest.mark.parametrize(
    "designation",
    [
        "01C-05B(A)",
        "02C-2B-05B",
        "03C-2B-05B",
        "04C-6B-12B",
        "05C-2B-20",
        "06C-12B",
        "07C-2B-12G",
        "08C-2B-12J",
        "09C-2B-08B",
        "10C-6B-08B",
        "11C-A-CR12-8B",
        "12C-CR12-8B",
        "13C-B-CR32-30B",
        "14C-CR32-30B-1 1/2-250",
        "15C-A-CR12-8B",
        "16C-A-CR6-3B",
        "17C-A-CR8-4B-G",
        "18C-B-CR8-4B",
        "19C-A-CR12-3B",
        "20C-3B-500",
        "21C-3B-500-100",
        "22C-A-CR9-2B-500",
        "23C-CR12-3B-500-500",
        "24C-CR15-6B-500-500",
        "25C-CR14-4B-500",
        "26C-CR12-4B-T1",
    ],
)
def test_every_01c_to_26c_drawing_has_a_routed_source_safe_handler(
    designation,
):
    result = analyze_single(designation)

    assert not result.error
    if designation[:3] in {
        "06C",
        "07C",
        "08C",
        "09C",
        "10C",
        "17C",
        "18C",
        "22C",
    }:
        assert result.total_weight > 0
    else:
        assert result.total_weight == 0
    assert result.meta["fabrication"]["source_profile"] == "cw_e25_24_hp6"
    assert not result.meta["fabrication"]["bom_ready"]
    assert not result.meta["fabrication"]["fabrication_ready"]
    assert result.meta["fabrication"]["blockers"]


def test_all_01c_to_26c_configs_catalog_docs_and_handlers_exist():
    supported = set(get_supported_types())
    catalog_path = Path(__file__).parents[1] / "configs" / "type_catalog.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    by_id = {row["type_id"]: row for row in catalog["types"]}

    for type_id in COLD_TYPE_IDS:
        config = config_loader.load_config(type_id, strict=True)
        assert config["type_id"] == type_id
        assert config["data_updated_at"] == "2026-07-30"
        assert config["data_update_note"]
        assert type_id in supported
        assert by_id[type_id]["status"] == "fabrication_partial"
        doc = Path(__file__).parents[1] / "docs" / "types" / by_id[type_id][
            "doc_file"
        ]
        assert doc.exists()


def test_stanchion_tables_preserve_c2_c5_c10_rows():
    c2 = _source_row(analyze_single("02C-18B-05B"), "line_size")
    c5 = _source_row(analyze_single("05C-24B-20"), "line_size")
    c10 = _source_row(analyze_single("10C-12B-08B"), "line_size")

    assert c2["supporting_pipe"] == "12in SCH.40"
    assert c5 == {"pipe_B": "16in STD.WT", "C_mm": 430}
    assert c10 == {
        "F_mm": 240,
        "K_mm": 16,
        "pipe_B": "8in SCH.40",
        "C_mm": 230,
        "D_mm": 300,
        "E_mm": 9,
        "G_mm": 19,
        "stud_J": "5/8in x 165",
        "pu_block_no": 5,
    }


def test_type08c_keeps_spacer_hardware_row_without_fake_plate_weight():
    result = analyze_single("08C-14B-12J")
    row = _source_row(result, "line_size")

    assert row["pipe_B"] == "10in SCH.40"
    assert row["C_mm"] == 260
    assert row["D_mm"] == 350
    assert row["E_mm"] == 9
    assert row["G_mm"] == 19
    assert row["stud_J"] == "5/8in x 165"
    assert result.total_weight == pytest.approx(3.66)
    assert any("clipped net contour" in warning for warning in result.warnings)


def test_type11c_and_15c_resolve_optional_cradle_length_groups():
    type11_none = _parameters(analyze_single("11C-CR4-2B"))
    type11_b = _parameters(analyze_single("11C-B-CR12-8B"))
    type15_large = _parameters(analyze_single("15C-B-CR40-30B"))

    assert type11_none["cradle_length_code"] == "NONE"
    assert type11_none["pipe_group_data"]["cradle_lengths_mm"]["NONE"] == 150
    assert type11_b["pipe_group_data"]["cradle_lengths_mm"]["B"] == 600
    assert type15_large["pipe_group"] == "thirty_to_sixty"
    assert type15_large["pipe_group_data"]["cradle_lengths_mm"] == {
        "NONE": 300,
        "B": 600,
    }


def test_type16c_preserves_both_cr2_5_source_rows_and_enforces_pairing():
    half = _source_row(analyze_single("16C-A-CR2.5-1/2B"), "cradle")
    three_quarter = _source_row(
        analyze_single("16C-A-CR2.5-3/4B"), "cradle"
    )
    mismatch = analyze_single("16C-A-CR6-4B")

    assert half["pipe_OD_mm"] == 21.3
    assert half["tie_A_mm"] == 39
    assert three_quarter["pipe_OD_mm"] == 26.7
    assert three_quarter["tie_A_mm"] == 40
    assert mismatch.error and "應搭配" in mismatch.error
    assert mismatch.entries == []


def test_type17c_locks_irregular_source_rows_instead_of_smoothing_them():
    cr14 = _source_row(analyze_single("17C-A-CR14-8B-G"), "cradle")
    cr34 = _source_row(analyze_single("17C-B-CR34-20B-G"), "cradle")
    cr40 = _source_row(analyze_single("17C-B-CR40-24B-G"), "cradle")

    assert cr14["bar_Q"] == "75x12"
    assert cr14["angle_S"] == "65x65x6"
    assert cr14["hole_E_mm"] == 15
    assert cr34["RG_mm"] == 448
    assert cr34["H_mm"] == 495
    assert cr40["bar_Q"] == "130x25"
    assert cr40["bolts_V"] == "5/8in x 60"


def test_type18c_locks_c26_c27_anchor_table_anomalies():
    cr17 = _source_row(analyze_single("18C-A-CR17-12B"), "cradle")
    cr22 = _source_row(analyze_single("18C-B-CR22-18B"), "cradle")
    cr25 = _source_row(analyze_single("18C-B-CR25-20B"), "cradle")

    assert cr17["H_mm"] == 252
    assert cr22["W_mm"] == 597
    assert cr25["H_mm"] == 357
    assert cr17["L_cut_mm"] == 500
    assert cr17["L_quantity"] == 2


@pytest.mark.parametrize(
    ("designation", "branch"),
    [
        ("20C-3B-500", "four_and_smaller"),
        ("20C-8B-500", "six_eight_ten"),
        ("20C-14B-500", "twelve_to_twenty_four"),
        ("21C-3B-500-100", "three_four"),
        ("21C-8B-500-100", "six_eight_ten"),
        ("21C-14B-500-100", "twelve_to_twenty_four"),
        ("22C-A-CR9-2B-500", "two_and_smaller"),
        ("22C-A-CR9-4B-500", "three_four"),
        ("22C-A-CR10-8B-500", "six_eight_ten"),
        ("22C-B-CR20-14B-700", "twelve_to_twenty_four"),
    ],
)
def test_vessel_interface_types_keep_source_branches_separate(
    designation, branch
):
    parameters = _parameters(analyze_single(designation))

    assert parameters["pipe_group"] == branch


def test_type23c_to_26c_preserve_designation_dimensions_and_limits():
    type23 = _parameters(analyze_single("23C-CR12-3B-500-600"))
    type24 = _parameters(analyze_single("24C-CR15-6B-700-800"))
    type25 = _parameters(analyze_single("25C-CR14-4B-900"))
    type26 = _parameters(analyze_single("26C-CR12-4B-T2"))

    assert type23["C_mm"] == 500 and type23["B_mm"] == 600
    assert type24["orientation_default_deg"] == 45
    assert type24["sections"][0] == "C180x75x7x10.5"
    assert type25["maximum_load_kg"] == 5500
    assert type25["C_mm"] == 900
    assert type26["trunnion_type"] == "T2"


@pytest.mark.parametrize(
    "designation",
    [
        "02C-5B-05B",
        "03C-6B-05B",
        "10C-5B-08B",
        "13C-B-CR32-24B",
        "14C-CR32-24B-1-250",
        "17C-A-CR13-8B-G",
        "17C-A-CR8-4B-A",
        "21C-2B-500-100",
        "22C-A-CR9-5B-500",
        "26C-CR12-4B-T3",
    ],
)
def test_cold_types_reject_non_source_designations(designation):
    result = analyze_single(designation)

    assert result.error
    assert result.entries == []


def test_01c_to_26c_do_not_run_under_unverified_20e_profile():
    result = analyze_single(
        "17C-A-CR8-4B-G",
        source_profile=CTCI_20E4588,
    )

    assert result.error and "尚未完成" in result.error
    assert result.entries == []
