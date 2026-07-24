import json

from core.calculator import analyze_single
from core.code_aliases import (
    DEFAULT_ALIAS_PATH,
    analyze_with_designation_alias,
    load_code_aliases,
    normalize_designation_alias,
    resolve_designation_alias,
    validate_code_aliases,
)


def test_default_code_alias_config_is_valid():
    config = load_code_aliases()

    assert DEFAULT_ALIAS_PATH.exists()
    assert validate_code_aliases(config) == []


def test_resolve_designation_alias_maps_external_code_to_internal_designation():
    resolved = resolve_designation_alias(
        "ACME-PS01-2B-05A",
        alias_ref="type_01@acme",
    )

    assert resolved is not None
    assert resolved.original == "ACME-PS01-2B-05A"
    assert resolved.designation == "01-2B-05A"
    assert resolved.maps_to_base == "01"


def test_standard_designation_is_not_rewritten_without_match():
    assert resolve_designation_alias("01-2B-05A", alias_ref="type_01@acme") is None


def test_normalize_designation_alias_is_disabled_without_alias_ref():
    designation, alias = normalize_designation_alias("ACME-PS01-2B-05A")

    assert designation == "ACME-PS01-2B-05A"
    assert alias is None


def test_analyze_with_designation_alias_does_not_scan_without_alias_ref():
    result = analyze_with_designation_alias("ACME-PS01-2B-05A")

    assert result.fullstring == "ACME-PS01-2B-05A"
    assert result.error is not None
    assert "找不到型號 'ACME' 的可驗證計算規則" in result.error
    assert "避免無依據判斷" in result.error
    assert "alias_resolution" not in result.meta


def test_analyze_with_designation_alias_keeps_standard_designations_unchanged():
    for designation in ("01-2B-05A", "51-1.1/2B"):
        standard = analyze_single(designation)
        with_alias_enabled = analyze_with_designation_alias(
            designation,
            alias_ref="type_01@acme",
        )

        assert standard.error == ""
        assert with_alias_enabled.error == ""
        assert with_alias_enabled.fullstring == standard.fullstring
        assert with_alias_enabled.meta.get("type_id") == standard.meta.get("type_id")
        assert round(with_alias_enabled.total_weight, 6) == round(standard.total_weight, 6)
        assert "alias_resolution" not in with_alias_enabled.meta


def test_analyze_with_designation_alias_uses_explicit_alias_ref_after_standard_parse_fails():
    aliased = analyze_with_designation_alias("ACME-PS01-2B-05A", alias_ref="type_01@acme")
    standard = analyze_single("01-2B-05A")

    assert aliased.error == ""
    assert aliased.fullstring == "01-2B-05A"
    assert aliased.meta["alias_resolution"]["original"] == "ACME-PS01-2B-05A"
    assert aliased.meta["alias_resolution"]["designation"] == "01-2B-05A"
    assert aliased.meta["alias_resolution"]["alias_ref"] == "type_01@acme"
    assert aliased.meta["input_designation"] == "ACME-PS01-2B-05A"
    assert aliased.meta["normalized_designation"] == "01-2B-05A"
    assert len(aliased.entries) == len(standard.entries)
    assert round(aliased.total_weight, 6) == round(standard.total_weight, 6)


def test_validate_code_aliases_reports_bad_regex(tmp_path):
    path = tmp_path / "bad_aliases.json"
    path.write_text(
        json.dumps({
            "aliases": {
                "bad": {
                    "maps_to_base": "01",
                    "patterns": [{"match": "(", "designation": "01-{x}"}],
                }
            }
        }),
        encoding="utf-8",
    )

    issues = validate_code_aliases(load_code_aliases(path))

    assert any("regex error" in issue for issue in issues)
