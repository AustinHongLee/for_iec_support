from core.bolt import add_bolt_entry
from core.calculator import analyze_single
from core.models import AnalysisResult
from core.pipe import add_pipe_entry
from core.plate import add_plate_entry
from core.steel import add_steel_section_entry


def test_core_material_helpers_assign_distinct_categories():
    result = AnalysisResult(fullstring="category-smoke")

    add_pipe_entry(result, "2B", "SCH.40", 1000, "A53Gr.B")
    add_steel_section_entry(result, "Angle", "75*75*9", 500)
    add_steel_section_entry(result, "Channel", "100*50*5", 500)
    add_plate_entry(result, 100, 80, 6, "Plate")
    add_bolt_entry(result, "2B", 4)

    categories = {entry.name: entry.category for entry in result.entries}
    assert categories["管路"] == "管路類"
    assert categories["角鋼"] == "型鋼類"
    assert categories["槽鐵"] == "型鋼類"
    assert categories["Plate"] == "鋼板類"
    assert categories["EXP.BOLT"] == "螺栓類"


def test_type03_angle_and_ubolt_categories():
    result = analyze_single("03-1B-05N")

    assert not result.error
    angle_entries = [entry for entry in result.entries if entry.name == "角鋼"]
    ubolt = next(entry for entry in result.entries if entry.name == "U.bolt")
    assert angle_entries
    assert {entry.category for entry in angle_entries} == {"型鋼類"}
    assert ubolt.category == "螺栓類"


def test_type13_clamp_and_gasket_categories():
    result = analyze_single("13-6B-05B")

    assert not result.error
    clamp = next(entry for entry in result.entries if entry.name == "PIPE CLAMP")
    gasket = next(entry for entry in result.entries if entry.name == "NON-ASBESTOS")
    pipe = next(entry for entry in result.entries if entry.name == "管路")
    assert clamp.category == "管夾類"
    assert gasket.category == "墊片類"
    assert pipe.category == "管路類"
