from core.issues import classify_upper_limit, combine_limit_checks


def test_upper_limit_within_drawing_has_no_issue():
    assert classify_upper_limit(1500, 1500) is None


def test_exclusive_boundary_is_a_warning():
    issue = classify_upper_limit(1500, 1500, inclusive=False)
    assert issue is not None
    assert issue["severity"] == "warning"


def test_small_overrun_is_warning():
    assert classify_upper_limit(1600, 1500)["severity"] == "warning"


def test_material_overrun_is_high_risk():
    assert classify_upper_limit(800, 500)["severity"] == "high"


def test_unbounded_extrapolation_remains_error():
    assert classify_upper_limit(1600, 500)["severity"] == "error"
    assert classify_upper_limit(4500, 2500)["severity"] == "high"
    assert classify_upper_limit(5001, 2500)["severity"] == "error"


def test_combined_check_uses_highest_severity():
    issue = combine_limit_checks(
        [
            ("L", 1600, 1500, True),
            ("H", 800, 500, True),
        ]
    )
    assert issue is not None
    assert issue["severity"] == "high"
