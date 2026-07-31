import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication

from core.config_loader import get_variation_axes, load_config
from ui.main_window import SidePanel


_APP = QApplication.instance() or QApplication(sys.argv)


def _panel(monkeypatch) -> SidePanel:
    monkeypatch.setattr(SidePanel, "_load_pdf_for_type", lambda self, type_code: None)
    return SidePanel()


def test_type01_declares_existing_override_axes_with_unknown_material_enabled():
    config = load_config("01", strict=True)
    axes = get_variation_axes("01", config=config)

    assert list(axes) == ["connection", "upper_material", "table_override"]
    assert axes["connection"]["choices"] == ["elbow", "tee"]
    assert axes["upper_material"]["allow_unknown"] is True
    assert axes["table_override"]["fields"] == [
        "pipe_size",
        "schedule",
        "l_value",
    ]
    assert config["data_updated_at"] == "2026-07-31"
    assert config["data_update_note"]


def test_variation_axes_helper_returns_detached_data():
    first = get_variation_axes("01")
    first["connection"]["choices"].append("test-only")

    assert get_variation_axes("01")["connection"]["choices"] == ["elbow", "tee"]


def test_type01_declarative_form_preserves_existing_override_dict(monkeypatch):
    panel = _panel(monkeypatch)
    emitted = []
    panel.overrideChanged.connect(lambda idx, values: emitted.append((idx, values)))
    existing = {
        "connection": "tee",
        "upper_material": "SUS316",
        "pipe_size": "3",
        "schedule": "SCH.80",
        "l_value": 123,
    }

    panel.show_item(7, "01-2B-05A", existing)
    panel._on_field_changed()

    assert emitted[-1] == (7, existing)
    panel.close()


def test_type01_declarative_form_preserves_connection_defaults(monkeypatch):
    panel = _panel(monkeypatch)
    emitted = []
    panel.overrideChanged.connect(lambda idx, values: emitted.append(values))

    panel.show_item(0, "01-2B-05A", {})
    panel._on_field_changed()
    assert emitted[-1] == {"connection": "elbow"}

    panel.show_item(1, "01T-2B-05A", {})
    panel._on_field_changed()
    assert emitted[-1] == {"connection": "tee"}
    panel.close()
