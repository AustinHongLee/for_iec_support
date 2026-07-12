from pathlib import Path

import pytest

from core import config_loader


CONFIG_DIR = Path(__file__).resolve().parents[1] / "configs"


def test_config_path_uses_anchor_index_storage_alias():
    path = config_loader._config_path("01T")

    assert path is not None
    assert Path(path).name == "type_01.json"
    assert config_loader.load_config("01T")["type_id"] == "01"


def test_config_path_does_not_guess_non_numeric_external_codes():
    assert config_loader._config_path("ACME-PS01") is None
    assert config_loader.load_config("ACME-PS01") is None


def test_shared_spec_types_do_not_claim_direct_type_config():
    assert config_loader._config_path("52") is None
    assert config_loader.load_config("52") is None


def test_load_config_rejects_unimplemented_variant_overlay():
    with pytest.raises(NotImplementedError, match="configs/variants/README.md"):
        config_loader.load_config("01", variant="01@ACME")


def test_strict_load_accepts_existing_type_configs():
    for path in sorted(CONFIG_DIR.glob("type_*.json")):
        if path.name in {"type_anchor_index.json", "type_catalog.json"}:
            continue
        type_id = path.stem.removeprefix("type_").upper()
        if not type_id.isdigit():
            continue
        assert config_loader.load_config(type_id, strict=True)["type_id"]


def test_validate_config_reports_schema_issues():
    issues = config_loader.validate_config({"type_id": "", "table": {"bad": "shape"}})

    assert "type_id must be a non-empty string" in issues
    assert "table must be a list" in issues


def test_strict_load_raises_on_invalid_existing_config(monkeypatch, tmp_path):
    bad_path = tmp_path / "type_99.json"
    bad_path.write_text('{"type_id": "", "table": {}}', encoding="utf-8")

    monkeypatch.setattr(config_loader, "_config_path", lambda type_id, must_exist=True: str(bad_path))

    with pytest.raises(ValueError, match="Invalid config"):
        config_loader.load_config("99", strict=True)


def test_save_config_records_user_in_change_log(monkeypatch, tmp_path):
    config_path = tmp_path / "type_99.json"
    monkeypatch.setattr(
        config_loader, "_config_path", lambda type_id, must_exist=True: str(config_path)
    )
    monkeypatch.setattr(config_loader.getpass, "getuser", lambda: "test-user")
    config = {"type_id": "99", "table": []}

    config_loader.save_config("99", config, change_desc="test change")

    assert config["change_log"][-1]["by"] == "test-user"
    assert config_path.exists()


def test_save_config_uses_unknown_when_user_lookup_fails(monkeypatch, tmp_path):
    config_path = tmp_path / "type_99.json"
    monkeypatch.setattr(
        config_loader, "_config_path", lambda type_id, must_exist=True: str(config_path)
    )

    def fail_user_lookup():
        raise OSError("user lookup unavailable")

    monkeypatch.setattr(config_loader.getpass, "getuser", fail_user_lookup)
    config = {"type_id": "99", "table": []}

    config_loader.save_config("99", config, change_desc="test change")

    assert config["change_log"][-1]["by"] == "unknown"
