import json
from pathlib import Path

from core.calculator import analyze_single


def _entry_by_name(result, name):
    return next((entry for entry in result.entries if entry.name == name), None)


def test_type54_10_to_14_adds_40_square_stopper_plates():
    result = analyze_single("54-10B-A-150-250")

    stopper = _entry_by_name(result, "檔板_54Type")
    legacy_gusset = _entry_by_name(result, "FB_52Type_3")

    assert stopper is not None
    assert stopper.length == 40
    assert stopper.width == 40
    assert stopper.spec == "12.0"
    assert stopper.quantity == 4
    assert stopper.role == "stopper_plate"
    assert "倒角" in stopper.display_remark
    assert "重量計算不扣除" in stopper.display_remark
    assert legacy_gusset is None


def test_type54_stopper_plate_range_is_inclusive_10_to_14_only():
    eight_inch = analyze_single("54-8B-A-150-250")
    fourteen_inch = analyze_single("54-14B-A-150-250")
    sixteen_inch = analyze_single("54-16B-A-200-600")

    assert _entry_by_name(eight_inch, "檔板_54Type") is None
    assert _entry_by_name(fourteen_inch, "檔板_54Type") is not None
    assert _entry_by_name(sixteen_inch, "檔板_54Type") is None
    assert _entry_by_name(sixteen_inch, "FB_52Type_3") is not None


def test_type54_and_type55_ignore_invalid_pad_marker():
    for designation in ("54-6B(P)-A-150-250", "55-6B(P)-A-150-250"):
        result = analyze_single(designation)

        assert _entry_by_name(result, "Pad_52Type") is None
        assert any("不接受 (P)" in warning for warning in result.warnings)


def test_clamp_family_is_semi_archived_at_runtime():
    for designation in ("54-6B-A-150-250", "55-6B-A-150-250", "67-6B-A-150-250"):
        result = analyze_single(designation)

        assert any("半封存/未完工建檔" in warning for warning in result.warnings)


def test_clamp_family_catalog_entries_are_downgraded_to_cataloged():
    catalog_path = Path(__file__).resolve().parents[1] / "configs" / "type_catalog.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    entries = {entry["type_id"]: entry for entry in catalog["types"]}

    for type_id in ("54", "55", "67"):
        entry = entries[type_id]
        assert entry["status"] == "cataloged"
        assert entry["archive_status"] == "semi_archived"
        assert entry["requires_review"] is True
        assert "半封存/未完工建檔" in entry["trust_notes"]

    assert entries["66"]["status"] == "documented"
    assert "archive_status" not in entries["66"]
