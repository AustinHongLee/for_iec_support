from tools.audit_table_json_coverage import audit_coverage


def test_supported_type_anchor_audit_flags_calculator_only_types():
    audit = audit_coverage()
    summary = audit["supported_types"]["summary"]

    assert "03" in summary["calculator_only"]
    assert "05" in summary["calculator_only"]
    assert "01T" not in summary["calculator_only"]
    assert "66" not in summary["calculator_only"]
    assert "66" in summary["shared_spec"]


def test_type_table_json_bridge_coverage_is_complete_for_existing_type_tables():
    audit = audit_coverage()
    type_summary = audit["summary"]["type"]

    assert type_summary["missing_config"] == []
    assert type_summary["not_json_bridge"] == []
