from core.calculator import analyze_single
from data.type51_table import get_type51_data


def test_type51_half_inch_uses_project_approved_high_risk_three_quarter_row():
    assert get_type51_data(0.5) is None
    assert get_type51_data(0.75) == {"member": None, "H": 25}

    result = analyze_single("51-1/2B")

    assert not result.error
    assert result.meta["issue_summary"]["highest_severity"] == "high"
    assert not result.meta["fabrication"]["bom_ready"]
    assert not result.meta["fabrication"]["fabrication_ready"]
    assert (result.entries[0].length, result.entries[0].width) == (25, 50)
    assert result.evidence[-1]["value"]["requested_line_size"] == 0.5
    assert result.evidence[-1]["value"]["resolved_table_line_size"] == 0.75
