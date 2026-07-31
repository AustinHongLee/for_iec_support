"""EKO 圖號安全驗證：會影響選鋼/完整 BOM 的缺漏或越界一律阻擋。"""

import pytest

from core.calculator import analyze_single


@pytest.mark.parametrize(
    "designation, expected",
    [
        ("FS4E-400L-2300H-20H1", "序號"),
        ("FS9E-400L-2300H", "序號"),
        ('FS9E-1"-200L-1830H-20H1', "序號"),
        ('FS31W-1.1/2"-1000H', "下限"),
        ('FS31N-4"-534H-H1', "圖面格式沒有"),
        ('FS33N-3/4"-989H', "FS32"),
        ('G2-3"', "H"),
        ('S1-3"', "H"),
        ('PU4W-3/4"', "L"),
        ('PU23W-6"-300L-700L1', "圖面格式沒有"),
        ("SS8W-1-1050H", "圖面格式沒有"),
        ("SS8W-8000H", "結構設計確認"),
        ("SS24W-1350H-1500L", None),
        ("SS25W-2056H-750L", "1600"),
        ("SS28W-1806H", "1600"),
        ('FS5N-6"-900H', "小於"),
        ('FS15W-V-1"-2-1500H', "圖面格式沒有"),
        ('ST3-3"', "Cr"),
        ("SS28W-500H-1800H", "重複"),
        ('PU4W-1"-300L-C20', "圖面格式沒有"),
    ],
)
def test_owner_samples_are_safely_classified(designation, expected):
    result = analyze_single(designation)
    if expected is None:
        assert not result.error, result.error
    else:
        assert result.error, designation
        assert expected in result.error
        assert not result.entries


@pytest.mark.parametrize(
    "designation",
    [
        "FS4E-2-400L-2300H-20H1",
        "FS9E-3-400L-307H",
        'FS31N-4"-534H-20H1',
        'FS5N-6"-899H',
        'G2-3"-100H',
        'S1-3"-100H',
        'PU4W-3/4"-300L',
        "PU23W-500L-350L1",
        "SS8W-1050H",
        "FS15W-V-2-1500H",
        "SS25W-1600H-750L",
        "SS28W-1600H",
    ],
)
def test_strict_validation_keeps_valid_designations(designation):
    result = analyze_single(designation)
    assert not result.error, f"{designation}: {result.error}"
    assert result.entries


def test_ss12_range_serial_and_diagonal():
    assert analyze_single("SS12W-1-700L").error
    assert analyze_single("SS12W-1-900L").error
    assert analyze_single("SS12W-5-1000L").error
    assert analyze_single("SS12W-1-1051L").error
    assert analyze_single("SS12W-4-1500L").error

    result = analyze_single("SS12W-1-1000L")
    assert not result.error, result.error
    angles = [entry for entry in result.entries if entry.name == "角鋼"]
    assert sorted(entry.length for entry in angles) == [924, 1000]
