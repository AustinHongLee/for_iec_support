from core.calculator import analyze_single


def _entry(result, component_id):
    return next(entry for entry in result.entries if entry.geometry.component_id == component_id)


def test_type56_small_pipe_uses_exact_two_100_square_plates():
    result = analyze_single("56-2B")
    plate = _entry(result, "D67-PL100-PIPE-STOPS")

    assert (plate.length, plate.width, plate.spec, plate.quantity) == (100, 100, "6", 2)
    assert plate.category == "鋼板類"
    assert plate.geometry.fabrication_ready
    assert result.meta["fabrication"]["bom_ready"]


def test_type56_3_to_4_keeps_drawing_assembly_instead_of_invented_rectangles():
    result = analyze_single("56-3B")
    member = _entry(result, "D67-3-MEMBER-C-ASSEMBLY")

    assert member.name == "MEMBER C ASSEMBLY"
    assert member.spec == "MEMBER C / FAB. FROM 6t PLATE"
    assert member.quantity == 2
    assert member.unit_weight == 0
    assert not result.meta["fabrication"]["bom_ready"]


def test_type56_5_to_14_does_not_count_two_whole_parent_h_sections():
    five = analyze_single("56-5B")
    ten = analyze_single("56-10B")

    five_member = _entry(five, "D67-5-MEMBER-C-ASSEMBLY")
    ten_member = _entry(ten, "D67-10-MEMBER-C-ASSEMBLY")
    assert "CUT FROM H200*100*5.5*8" in five_member.spec
    assert "CUT FROM H200*200*8*12" in ten_member.spec
    assert five_member.unit_weight == ten_member.unit_weight == 0
    assert not five.meta["fabrication"]["bom_ready"]
    assert not ten.meta["fabrication"]["bom_ready"]


def test_type56_16_to_24_keeps_fabricated_member_as_unresolved_assembly():
    result = analyze_single("56-16B")
    member = _entry(result, "D67-16-MEMBER-C-ASSEMBLY")

    assert member.spec == "MEMBER C / FAB. FROM 12t PLATE"
    assert member.quantity == 2
    assert member.unit_weight == 0
    assert not result.meta["fabrication"]["bom_ready"]


def test_type56_d67a_carries_d91_constraints_without_fake_pad_weight():
    result = analyze_single("56-26B")
    member = _entry(result, "D67-26-MEMBER-C-ASSEMBLY")
    pad = _entry(result, "D67A-D91-REINFORCING-PAD")

    assert member.quantity == 2
    assert member.unit_weight == pad.unit_weight == 0
    assert pad.geometry.parameters["angle_deg"] == 120
    assert pad.geometry.parameters["axial_length_mm"] == 400
    assert pad.geometry.parameters["minimum_thickness_mm"] == 12
    assert not result.meta["fabrication"]["bom_ready"]
