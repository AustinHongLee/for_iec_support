from core import config_loader
from core.calculator import analyze_single


def test_project_header_shows_versions_after_analysis():
    import os
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PyQt6.QtWidgets import QApplication
    from ui.main_window import MainWindow

    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    try:
        window._add_item_to_list("01-2B-05A")
        window._on_analyze()
        app.processEvents()
        assert window.project_header.version_label.isEnabled()
        assert "1.2" in window.project_header.version_label.text()

        window._invalidate_analysis_outputs("test")
        assert not window.project_header.version_label.isEnabled()
        assert "待分析" in window.project_header.version_label.text()
    finally:
        window.close()


def test_analyze_single_records_json_config_version():
    result = analyze_single("01-2B-05A")

    assert not result.error
    assert result.meta["config_version"] == "1.2"
    assert result.meta["config_updated"]


def test_rebuilt_type03_config_version_is_explicit():
    assert config_loader.get_config_version_info("03") == (
        "2.0",
        "2026-07-31",
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
