from core.calculator import analyze_single
from core.source_profiles import (
    CTCI_20E4588,
    CTCI_22A_5123A,
    CW_E25_24_HP6,
)


def _pipe(result):
    return next(entry for entry in result.entries if entry.name == "管路")


def test_cw_type01_uses_one_continuous_same_material_supporting_pipe():
    result = analyze_single(
        "01-50B-05A",
        {"upper_material": "SUS316"},
        source_profile=CW_E25_24_HP6,
    )

    assert not result.error
    pipe_entries = [entry for entry in result.entries if entry.name == "管路"]
    assert len(pipe_entries) == 1
    assert pipe_entries[0].spec == '28"*STD.WT'
    assert pipe_entries[0].length == 500 + 1382
    assert pipe_entries[0].material == "SUS316"
    assert pipe_entries[0].geometry.component_id == "D1-SUPPORTING-PIPE-B"
    assert not pipe_entries[0].geometry.fabrication_ready
    assert "cope/fishmouth" in " ".join(
        pipe_entries[0].geometry.fabrication_blockers
    )
    assert result.meta["fabrication"]["bom_ready"] is True
    assert result.meta["fabrication"]["fabrication_ready"] is False


def test_ctci22_has_its_own_range_table_and_h_limit():
    valid = analyze_single(
        "01-24B-12B",
        source_profile=CTCI_22A_5123A,
    )
    missing_22 = analyze_single(
        "01-22B-05B",
        source_profile=CTCI_22A_5123A,
    )
    too_high = analyze_single(
        "01-6B-13B",
        source_profile=CTCI_22A_5123A,
    )

    assert not valid.error
    assert _pipe(valid).spec == '12"*STD.WT'
    assert _pipe(valid).length == 1200 + 647
    assert missing_22.error and "不支援管徑 22" in missing_22.error
    assert not too_high.error
    assert too_high.meta["issues"][0]["severity"] == "warning"
    assert too_high.meta["issues"][0]["code"] == "SOURCE_ENVELOPE_EXTRAPOLATION"
    assert too_high.meta["fabrication"]["bom_ready"] is True


def test_ctci_profiles_reject_cw_only_m42_type():
    for profile in (CTCI_22A_5123A, CTCI_20E4588):
        result = analyze_single("01-6B-05A", source_profile=profile)
        assert result.error
        assert "下部構件 A" in result.error
        assert not result.entries


def test_ctci22_and_20e_use_different_drawing_fasteners():
    ctci22 = analyze_single(
        "01-24B-05B",
        source_profile=CTCI_22A_5123A,
    )
    legacy = analyze_single(
        "01-24B-05B",
        source_profile=CTCI_20E4588,
    )

    assert not ctci22.error
    assert not legacy.error
    fastener_22 = next(
        entry for entry in ctci22.entries if entry.category == "螺栓類"
    )
    fastener_20e = next(
        entry for entry in legacy.entries if entry.category == "螺栓類"
    )
    assert (fastener_22.name, fastener_22.spec) == ("EXP.BOLT", '1"')
    assert (fastener_20e.name, fastener_20e.spec) == (
        "MACH.BOLT W/ HEX NUT",
        "M24 X 60",
    )
    assert fastener_22.quantity == fastener_20e.quantity == 4
    assert fastener_22.unit_weight == 0
    assert fastener_20e.unit_weight > 0
    assert fastener_20e.geometry.parameters["weight_estimate"][
        "kind"
    ] == "machine_bolt_with_nut"
    for fastener in (fastener_22, fastener_20e):
        assert fastener.geometry.component_id == "M42-FASTENER"
        assert fastener.geometry.fabrication_ready


def test_restrained_and_tee_variants_keep_explicit_fabrication_blockers():
    restrained = analyze_single(
        "01-6B-05B-A",
        source_profile=CTCI_20E4588,
    )
    tee = analyze_single(
        "01T-6B-05B",
        {"connection": "tee"},
        source_profile=CTCI_20E4588,
    )

    assert not restrained.error
    assert "restraint element" in " ".join(
        restrained.meta["fabrication"]["blockers"]
    )
    assert not tee.error
    assert tee.meta["fabrication"]["branch"] == "D-1/tee"
    assert any(
        "三通接法" in blocker
        for blocker in tee.meta["fabrication"]["blockers"]
    )
