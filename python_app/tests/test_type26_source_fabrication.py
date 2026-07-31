from core.calculator import analyze_single


def _component(result, component_id):
    return next(entry for entry in result.entries if entry.geometry.component_id == component_id)


def test_type26_source_member_sets_are_separate():
    assert not analyze_single("26-L65-1005A", source_profile="cw_e25_24_hp6").error
    assert "未表列 MEMBER L65" in analyze_single("26-L65-0605A", source_profile="ctci_22a_5123a").error
    assert not analyze_single("26-C150-1515A", source_profile="ctci_22a_5123a").error


def test_type26_each_source_grades_upper_envelope_and_keeps_lower_bound():
    ctci = analyze_single("26-L50-0705A", source_profile="ctci_22a_5123a")
    cw = analyze_single("26-L75-1026A", source_profile="cw_e25_24_hp6")
    assert not ctci.error and ctci.meta["issues"][0]["severity"] == "high"
    assert not cw.error and cw.meta["issues"][0]["severity"] == "warning"
    assert "500<L≤1000" in analyze_single("26-L75-0510A", source_profile="ctci_20e4588").error


def test_type26_20e_down_stop_selection_matrix():
    valid = analyze_single("26-C125-1012B", source_profile="ctci_20e4588", overrides={"equivalent_pipe_size_in":6})
    wrong = analyze_single("26-L75-1012B", source_profile="ctci_20e4588", overrides={"equivalent_pipe_size_in":6})
    unavailable = analyze_single("26-L75-1008B", source_profile="ctci_20e4588", overrides={"equivalent_pipe_size_in":4})
    assert not valid.error
    assert "應選 C125" in wrong.error
    assert "未提供" in unavailable.error


def test_type26_20e_fig_b_without_pipe_size_is_bom_blocked():
    result = analyze_single("26-L75-1008B", source_profile="ctci_20e4588")
    assert not result.error
    assert result.meta["fabrication"]["bom_ready"] is False
    assert any("equivalent_pipe_size_in" in item for item in result.meta["fabrication"]["blockers"])


def test_type26_frame_has_two_h_and_one_l_members():
    result = analyze_single("26-L50-1005A", source_profile="cw_e25_24_hp6")
    assert not result.error
    assert [_component(result, cid).length for cid in (
        "D28-MEMBER-M-H-UPPER","D28-MEMBER-M-H-LOWER","D28-MEMBER-M-L-END"
    )] == [500,500,1000]


def test_type26_fig_c_uses_two_exact_m34_plates_and_eight_bolts():
    result = analyze_single("26-L50-1005C", source_profile="cw_e25_24_hp6")
    plate = _component(result,"M34-LGP-C-1")
    bolt = _component(result,"M34-K-BOLT")
    assert (plate.length,plate.width,plate.spec,plate.quantity)==(150,100,"9",2)
    assert plate.geometry.parameters["hole_count_per_plate"]==4
    assert bolt.quantity==8
    assert bolt.unit_weight>0
    assert bolt.density_requires_review


def test_type26_fig_b_records_not_furnished_interfaces():
    result=analyze_single("26-L50-1005B",source_profile="cw_e25_24_hp6")
    assert "DOWN STOPPER D-70" in result.meta["fabrication"]["not_furnished"]
    assert "STANDARD U-BOLT D-68" in result.meta["fabrication"]["not_furnished"]
