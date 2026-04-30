from core.calculator import analyze_single


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
