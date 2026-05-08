from core.calculator import analyze_single
from data.type51_table import get_type51_data


def test_type51_half_inch_uses_same_flat_bar_path_as_three_quarter():
    half = get_type51_data(0.5)
    three_quarter = get_type51_data(0.75)

    assert half == {"member": None, "H": 25}
    assert half == three_quarter

    result = analyze_single("51-1/2B")

    assert not result.error
    assert [(entry.name, entry.length, entry.width, entry.spec, entry.quantity) for entry in result.entries] == [
        ("FLAT BAR", 25, 50, "9", 2),
    ]
    assert result.entries[0].remark == "鞍座, 25x50x9, 全焊接(6V), ×2"
