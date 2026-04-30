from core.calculator import analyze_single


def test_type58_fig_a_spec_outputs_plate_and_u_bolt():
    result = analyze_single("58-4B-A")

    assert not result.error
    assert [(entry.name, entry.spec, entry.length, entry.width, entry.quantity) for entry in result.entries] == [
        ("STEEL PLATE", "12", 180, 130, 1),
        ("U-BOLT", 'M-26, 3/4"', 0, 0, 1),
    ]
    assert result.entries[1].unit_weight == 0.9
    assert result.warnings == []


def test_type58_fig_b_spec_outputs_x_warning():
    result = analyze_single("58-4B-B")

    assert not result.error
    assert result.warnings == ["FIG-B: 鋼板安裝於型鋼上, X=16mm"]


def test_type60_fig_a_spec_outputs_side_plate_only():
    result = analyze_single("60-20B-A")

    assert not result.error
    assert [(entry.name, entry.spec, entry.length, entry.width, entry.quantity) for entry in result.entries] == [
        ("SIDE PLATE", "12", 300, 250, 2),
    ]
    assert result.warnings == [
        "FIG-A: Pipe Shoe (D-80/80B) NOT FURNISHED, 需另行計算 TYPE-66",
    ]


def test_type60_fig_b_spec_outputs_bottom_plate():
    result = analyze_single("60-20B-B")

    assert not result.error
    assert [(entry.name, entry.spec, entry.length, entry.width, entry.quantity) for entry in result.entries] == [
        ("SIDE PLATE", "12", 300, 250, 2),
        ("BOTTOM PLATE", "12", 100, 90, 1),
    ]
    assert result.warnings == [
        "FIG-B: Pipe Shoe (D-80/80B) NOT FURNISHED, 需另行計算 TYPE-66",
    ]
