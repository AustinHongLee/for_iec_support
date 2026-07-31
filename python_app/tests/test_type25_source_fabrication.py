from core.calculator import analyze_single


def _component(result, component_id):
    return next(entry for entry in result.entries if entry.geometry.component_id == component_id)


def test_type25_source_member_sets_and_envelopes():
    assert not analyze_single("25-L65-0505A", source_profile="cw_e25_24_hp6").error
    assert "未表列 MEMBER L65" in analyze_single("25-L65-0505A", source_profile="ctci_22a_5123a").error
    assert not analyze_single("25-L75-0812A", source_profile="ctci_20e4588").error
    overrun = analyze_single("25-L75-0813A", source_profile="ctci_20e4588")
    assert not overrun.error
    assert overrun.meta["issues"][0]["severity"] == "warning"


def test_type25_20e_keeps_metric_k_bolt_and_a_difference():
    result = analyze_single("25-L75-0805C-0404", source_profile="ctci_20e4588")
    assert not result.error
    assert _component(result, "M34-K-BOLT").spec == "M20X50"
    assert result.evidence[0]["value"]["A"] == 150


def test_type25_fig_c_uses_exact_m34_plate_not_old_estimate():
    result = analyze_single("25-L50-0505C-0401", source_profile="cw_e25_24_hp6")
    plate = _component(result, "M34-LGP-C-1")
    assert (plate.length, plate.width, plate.spec, plate.quantity) == (150, 100, "9", 1)
    assert plate.geometry.parameters["hole_count"] == 4
    assert plate.geometry.holes.count == 4
    assert plate.geometry.fabrication_ready is True


def test_type25_fig_c_k_bolts_follow_the_four_m34_holes():
    result = analyze_single("25-L50-0505C-0401", source_profile="cw_e25_24_hp6")
    bolt = _component(result, "M34-K-BOLT")
    assert bolt.quantity == 4
    assert bolt.unit_weight > 0
    assert bolt.density_requires_review


def test_type25_l1_l2_mismatch_is_high_risk_but_keeps_bom_visible():
    invalid = analyze_single("25-L50-0505A-0202", source_profile="cw_e25_24_hp6")
    valid = analyze_single("25-L50-0505A-0401", source_profile="cw_e25_24_hp6")
    assert not invalid.error
    assert invalid.meta["issues"][0]["code"] == "DESIGNATION_L1_L2_MISMATCH"
    assert invalid.meta["issues"][0]["severity"] == "high"
    assert invalid.meta["fabrication"]["bom_ready"] is False
    assert not valid.error
    assert _component(valid, "D27-MEMBER-M-L").geometry.parameters["L1_mm"] == 400


def test_type25_fig_b_records_not_furnished_interfaces():
    result = analyze_single("25-L50-0505B", source_profile="cw_e25_24_hp6")
    assert not result.error
    assert "DOWN STOPPER D-70" in result.meta["fabrication"]["not_furnished"]
    assert "STANDARD U-BOLT D-68" in result.meta["fabrication"]["not_furnished"]


def test_type25_ctci_fig_a_retains_fire_protection_blocker():
    result = analyze_single("25-L50-0508A", source_profile="ctci_22a_5123a")
    assert not result.error
    assert any("fire-protection" in item for item in result.meta["fabrication"]["blockers"])
