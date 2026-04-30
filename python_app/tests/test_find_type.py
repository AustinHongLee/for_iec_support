from tools.find_type import locate_type, normalize_type_id


def test_normalize_type_id():
    assert normalize_type_id("1") == "01"
    assert normalize_type_id("type-51") == "51"
    assert normalize_type_id("01t") == "01T"


def test_locate_direct_type():
    info = locate_type("51")

    assert info["type_id"] == "51"
    assert info["handler"]["supported"] is True
    assert info["handler"]["calculator"] == "python_app/core/types/type_51.py"
    assert info["shared_dispatch"] is False
    assert info["config"]["exists"] is True
    assert info["data_bridge"]["exists"] is True
    assert info["doc"]["exists"] is True


def test_locate_shared_dispatch_type():
    info = locate_type("66")

    assert info["type_id"] == "66"
    assert info["handler"]["supported"] is True
    assert info["handler"]["calculator"] == "python_app/core/types/type_52.py"
    assert info["expected_calculator"]["path"] == "python_app/core/types/type_66.py"
    assert info["expected_calculator"]["exists"] is False
    assert info["shared_dispatch"] is True


def test_locate_type_spec_engine():
    info = locate_type("48")
    assert info["handler"]["calculator"] == "python_app/core/types/type_48.py"
    assert info["config"]["type_spec_engine"] == "table_parts_v1"

    info = locate_type("57")
    assert info["handler"]["calculator"] == "python_app/core/types/type_57.py"
    assert info["config"]["type_spec_engine"] == "table_parts_v1"

    info = locate_type("58")

    assert info["handler"]["supported"] is True
    assert info["handler"]["calculator"] == "python_app/core/types/type_58.py"
    assert info["config"]["exists"] is True
    assert info["config"]["type_spec_engine"] == "table_parts_v1"

    info = locate_type("60")
    assert info["config"]["type_spec_engine"] == "table_plate_v1"
