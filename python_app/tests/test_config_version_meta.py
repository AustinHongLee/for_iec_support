from core import config_loader
from core.calculator import analyze_single


def test_analyze_single_records_json_config_version():
    result = analyze_single("01-2B-05A")

    assert not result.error
    assert result.meta["config_version"] == "1.1"
    assert result.meta["config_updated"]


def test_calculator_only_version_marker_is_explicit():
    assert config_loader.get_config_version_info("03") == (
        "(calculator-only)",
        "",
    )


def test_save_config_invalidates_version_metadata_cache(monkeypatch, tmp_path):
    path = tmp_path / "type_99.json"
    monkeypatch.setattr(
        config_loader,
        "_config_path",
        lambda type_id, must_exist=True: str(path) if path.exists() or not must_exist else None,
    )
    config_loader.get_config_version_info.cache_clear()
    config = {"type_id": "99", "name": "test", "version": "1", "table": []}
    config_loader.save_config("99", config)
    assert config_loader.get_config_version_info("99")[0] == "1"

    config["version"] = "2"
    config_loader.save_config("99", config)
    assert config_loader.get_config_version_info("99")[0] == "2"
