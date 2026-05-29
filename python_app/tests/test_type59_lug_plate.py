from core.calculator import analyze_single
from core.material_summary import aggregate


def _expected_lug_weight(a, b, c, t, density=7.85, qty=1):
    net_area = a * b - (b - c) * (a - 25) / 2
    unit = round(net_area * t * density / 1_000_000, 2)
    total = round(net_area * t * density / 1_000_000 * qty, 2)
    return net_area, unit, total


def _lug_plate(result):
    matches = [
        entry for entry in result.entries
        if entry.role == "lug_plate" and entry.geometry.shape_kind == "wing"
    ]
    assert matches, "missing Type 59 lug plate"
    return matches[0]


def test_type59_lug_plate_keeps_full_lofting_shape_spec():
    result = analyze_single("59-6B-A")

    assert not result.error
    assert [entry.name for entry in result.entries] == ["TYPE 59 翼形角板"]
    assert result.warnings == []
    plate = _lug_plate(result)

    assert (plate.length, plate.width, plate.spec, plate.quantity) == (150, 100, "12", 1)
    assert plate.name == "TYPE 59 翼形角板"
    assert plate.role == "lug_plate"
    assert plate.item_class == "fabricated_part"
    assert plate.manufacturing_type == "shaped_plate"
    assert plate.geometry.shape_kind == "wing"
    assert plate.geometry.shape_spec == "A150 x B100 x P25 x C50 x t12"
    assert plate.display_spec == "A150 x B100 x P25 x C50 x t12"
    assert plate.part_key == "59_lug_plate_wing_a150_b100_p25_c50_t12"
    assert plate.stock_id.startswith("PL-")
    assert len(plate.stock_id) == 11
    assert plate.remark == "A150 x B100 x P25 x C50 x t12"
    net_area, unit_weight, total_weight = _expected_lug_weight(150, 100, 50, 12)
    assert plate.geometry.gross_area_mm2 == 15000
    assert plate.geometry.cutout_area_mm2 == 3125
    assert plate.geometry.net_area_mm2 == net_area
    assert plate.unit_weight == unit_weight
    assert plate.total_weight == total_weight
    assert "淨面積 150×100 - (100-50)×(150-25)/2 = 11875 mm2" in plate.display_remark

    summary = aggregate([result])
    lug_summary = [line for line in summary.lines if line.name == "TYPE 59 翼形角板"][0]
    assert lug_summary.spec == "A150 x B100 x P25 x C50 x t12"


def test_type59_small_and_large_lug_plate_shape_specs():
    small = analyze_single("59-2B-A")
    stainless = analyze_single("59-6B-B(S)")
    large = analyze_single("59-14B-B")

    assert not small.error
    assert not stainless.error
    assert not large.error
    assert [entry.name for entry in small.entries] == ["TYPE 59 翼形角板"]
    assert [entry.name for entry in stainless.entries] == ["TYPE 59 翼形角板"]
    assert [entry.name for entry in large.entries] == ["TYPE 59 翼形角板"]
    assert _lug_plate(small).geometry.shape_spec == "A80 x B55 x P25 x C15 x t9"
    assert _lug_plate(stainless).geometry.shape_spec == "A150 x B100 x P25 x C50 x t9"
    assert _lug_plate(large).geometry.shape_spec == "A150 x B130 x P25 x C50 x t12"
    assert _lug_plate(small).unit_weight == _expected_lug_weight(80, 55, 15, 9)[1]
    assert _lug_plate(stainless).unit_weight == _expected_lug_weight(150, 100, 50, 9, density=7.93)[1]
    assert _lug_plate(large).unit_weight == _expected_lug_weight(150, 130, 50, 12)[1]
    assert _lug_plate(large).total_weight == _expected_lug_weight(150, 130, 50, 12, qty=2)[2]
    assert _lug_plate(large).quantity == 2
