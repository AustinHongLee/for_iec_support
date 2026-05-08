from core.calculator import analyze_single


def _entries(result, name):
    return [entry for entry in result.entries if entry.name == name]


def _first(result, name):
    matches = _entries(result, name)
    assert matches, f"missing entry: {name}"
    return matches[0]


def test_type56_small_pipe_uses_two_100_square_plates():
    result = analyze_single("56-2B")

    plate = _first(result, "PLATE")

    assert plate.length == 100
    assert plate.width == 100
    assert plate.spec == "6"
    assert plate.quantity == 2
    assert plate.category == "鋼板類"


def test_type56_3_to_4_inch_uses_member_and_side_plates():
    result = analyze_single("56-3B")

    member = _first(result, "MEMBER C")
    side = _first(result, "SIDE PLATE")

    assert (member.length, member.width, member.spec, member.quantity) == (75, 100, "6", 2)
    assert (side.length, side.width, side.spec, side.quantity) == (75, 100, "6", 2)
    assert any("外接矩形重量估算" in warning for warning in result.warnings)


def test_type56_5_to_8_inch_uses_h_section_member_pairs():
    five = analyze_single("56-5B")
    six = analyze_single("56-6B")

    five_member = _first(five, "MEMBER C")
    six_member = _first(six, "MEMBER C")

    assert five_member.category == "型鋼類"
    assert five_member.role == "h_section"
    assert (five_member.spec, five_member.length, five_member.quantity) == ("200*100*5.5", 100, 2)
    assert "剖半" in five_member.display_remark

    assert six_member.category == "型鋼類"
    assert (six_member.spec, six_member.length, six_member.quantity) == ("194*150*6", 100, 2)
    assert "餘料/可用性需人工評估" in six_member.display_remark


def test_type56_10_to_14_inch_uses_two_h200_square_members():
    result = analyze_single("56-10B")

    member = _first(result, "MEMBER C")

    assert member.category == "型鋼類"
    assert member.role == "h_section"
    assert (member.spec, member.length, member.quantity) == ("200*200*8", 200, 2)
    assert "左右各一" in member.display_remark


def test_type56_16_to_24_inch_plate_formula_uses_four_member_and_two_side_plates():
    result = analyze_single("56-16B")

    member = _first(result, "MEMBER C")
    side = _first(result, "SIDE PLATE")

    assert (member.length, member.width, member.spec, member.quantity) == (300, 250, "12", 4)
    assert (side.length, side.width, side.spec, side.quantity) == (276, 250, "12", 2)
    assert "(D-2E)=276" in side.display_remark
