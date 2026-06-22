import json

from core.code_aliases import (
    DEFAULT_ALIAS_PATH,
    load_code_aliases,
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
