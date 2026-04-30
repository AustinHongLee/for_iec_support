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


def test_type48_spec_handles_fractional_size_and_material_suffix():
    result = analyze_single("48-1/2B(B)")

    assert not result.error
    entry = result.entries[0]
    assert (entry.name, entry.spec, entry.length, entry.width, entry.quantity) == (
        "PLATE",
        "6",
        150,
        100,
        1,
    )
    assert entry.material == "SUS304"
    assert entry.remark == "Drain Hub 偏移底座, 150*100*6, offset=100mm, 全焊接(6V)"


def test_type57_spec_preserves_m26_metadata_and_invalid_mode_warning():
    slide = analyze_single("57-2B-A")
    fixed = analyze_single("57-2B-B")
    invalid = analyze_single("57-2B-Z")

    assert not slide.error
    assert [(entry.name, entry.spec, entry.material, entry.quantity) for entry in slide.entries] == [
        ("U-BOLT", "UB-2B", "Carbon Steel", 1),
        ("FINISHED HEX NUT", '3/8"', "Carbon Steel", 4),
    ]
    assert "M-26, SLIDE" in slide.entries[0].remark
    assert "B/C/D/E=62/71/58/74" in slide.entries[0].remark
    assert not fixed.error and "M-26, FIXED" in fixed.entries[0].remark
    assert invalid.warnings == ["模式 'Z' 無效，Type 57 僅支援 A(SLIDE) / B(FIXED)"]
    assert "M-26, Z" in invalid.entries[0].remark


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
