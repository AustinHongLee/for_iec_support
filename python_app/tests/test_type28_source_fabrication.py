from core.calculator import analyze_single


def test_type28_source_member_tables_and_envelopes():
    assert "未表列 MEMBER C100" in analyze_single("28-C100-1215L", source_profile="cw_e25_24_hp6").error
    assert not analyze_single("28-C100-1215L", source_profile="ctci_20e4588").error
    overrun = analyze_single("28-L50-1005L", source_profile="ctci_20e4588")
    assert not overrun.error
    assert overrun.meta["issues"][0]["severity"] == "high"
    assert not analyze_single("28-C150-1520T", source_profile="ctci_22a_5123a").error


def test_type28_host_m42_variance_requires_source_m42_definition():
    cw = analyze_single("28-L50-1005T", source_profile="cw_e25_24_hp6")
    assert not cw.error
    assert cw.meta["issues"][0]["code"] == "HOST_M42_NOT_LISTED"
    assert "不存在於此來源 M-42 圖" in analyze_single(
        "28-L50-1005P", source_profile="ctci_22a_5123a"
    ).error


def test_type28_is_three_frame_members_and_two_m42_sets():
    result = analyze_single("28-L50-1005L", source_profile="cw_e25_24_hp6")
    ids = [entry.geometry.component_id for entry in result.entries]
    assert ids[:3] == ["D31-LEFT-LEG", "D31-TOP-BEAM", "D31-RIGHT-LEG"]
    assert result.meta["fabrication"]["m42_sets"] == 2
    assert all("BOTH" in item for item in ids[3:])
    assert all(
        entry.geometry.parameters["portal_legs"] == ["LEFT", "RIGHT"]
        for entry in result.entries[3:]
    )


def test_type28_screenshot_case_merges_identical_m42_rows_as_quantity_two():
    result = analyze_single("28-L75-0405D", source_profile="cw_e25_24_hp6")
    m42_entries = result.entries[3:]
    assert [entry.name for entry in m42_entries] == [
        "Plate_a_無鑽孔",
        "Plate_e_無鑽孔",
    ]
    assert [entry.quantity for entry in m42_entries] == [2, 2]
    assert result.total_weight == 32.5


def test_type28_line_orientation_is_not_inferred_from_member():
    result = analyze_single("28-C125-1515L", source_profile="cw_e25_24_hp6")
    assert any("line_orientation" in item for item in result.meta["fabrication"]["blockers"])
    vertical = analyze_single(
        "28-C125-1515L",
        source_profile="cw_e25_24_hp6",
        overrides={"line_orientation": "vertical", "supported_line_layout": [{"size_in": 4, "center_mm": 500}]},
    )
    assert vertical.entries[1].geometry.parameters["u_bolt_standard"] == "D-68"
    assert any("NOT FURNISHED" in item for item in vertical.meta["fabrication"]["blockers"])


def test_type28_c100_and_h250_m42_rows_stay_blocked():
    c100 = analyze_single("28-C100-1215L", source_profile="ctci_20e4588")
    h250 = analyze_single("28-H250-1515L", source_profile="cw_e25_24_hp6")
    assert c100.meta["fabrication"]["bom_ready"] is False
    assert h250.meta["fabrication"]["bom_ready"] is False
