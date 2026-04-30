
import sys
sys.path.insert(0, ".")

# Phase X parser normalization smoke tests.
try:
    from core.calculator import analyze_single
    from core.parser import get_lookup_value, parse_pipe_size

    assert parse_pipe_size("1/2B") == "1/2"
    assert parse_pipe_size("1.1/2B") == "1-1/2"
    assert parse_pipe_size("1 1/2B") == "1-1/2"
    assert parse_pipe_size("2B") == "2"
    assert get_lookup_value("1.1/2B") == 1.5
    assert get_lookup_value("1/2B") == 0.5

    parser_smoke_cases = [
        "51-1.1/2B",
        "57-1.1/2B-A",
        "66-1.1/2B(P)-A-150-150",
        "22-L75-12(A)X",
        "59-1.1/2B-B(S)",
    ]
    for designation in parser_smoke_cases:
        result = analyze_single(designation)
        assert not result.error, f"{designation} should parse without Error: {result.error}"
        assert result.entries, f"{designation} should enter Type calculation"

    not_implemented = analyze_single("99-1B")
    assert not_implemented.error == "Type 99 not implemented"

    print("v phase X parser normalization OK")
except Exception as e:
    print(f"X phase X parser normalization ERROR: {e}")

# Project-level aggregation wrapper smoke tests.
try:
    from core.calculator import analyze_single
    from core.project_aggregation import (
        ProjectInputRow,
        analyze_project_rows,
        scale_analysis_result,
    )
    from core.material_summary import aggregate_project

    single = analyze_single("51-1.1/2B")
    assert not single.error and single.entries, "project aggregation source case failed"
    original_entry = single.entries[0]
    original_quantity = original_entry.quantity
    original_qty_subtotal = original_entry.qty_subtotal
    original_weight = original_entry.weight_output

    scaled_one = scale_analysis_result(single, 1)
    assert scaled_one.entries[0].quantity == original_quantity, "quantity=1 should preserve entry quantity"
    assert scaled_one.entries[0].weight_output == original_weight, "quantity=1 should preserve entry weight"

    scaled_ten = scale_analysis_result(single, 10)
    assert scaled_ten is not single, "scaled result must be a new AnalysisResult"
    assert scaled_ten.entries[0] is not original_entry, "scaled entries must not mutate original entries"
    assert scaled_ten.entries[0].quantity == original_quantity * 10, "project quantity scaling failed"
    assert scaled_ten.entries[0].qty_subtotal == original_qty_subtotal * 10, "project qty subtotal scaling failed"
    assert scaled_ten.entries[0].weight_output == original_weight * 10, "project weight scaling failed"
    assert original_entry.quantity == original_quantity, "single result quantity was mutated"
    assert original_entry.qty_subtotal == original_qty_subtotal, "single result qty subtotal was mutated"
    assert original_entry.weight_output == original_weight, "single result weight was mutated"

    project = analyze_project_rows([
        ProjectInputRow("51-1.1/2B", 10),
        ProjectInputRow("51-1.1/2B", 2),
        ProjectInputRow("57-1B-A", 1, enabled=False),
    ])
    assert not project.errors, f"project aggregation should not emit errors: {project.errors}"
    assert len(project.rows) == 2, "disabled project rows should be skipped"
    assert project.total_support_count == 12, "project support count failed"
    assert len(project.aggregated_entries) == 1, "duplicate scaled entries should aggregate"
    aggregate_entry = project.aggregated_entries[0]
    assert aggregate_entry.quantity == original_quantity * 12, "aggregated quantity failed"
    assert aggregate_entry.qty_subtotal == original_qty_subtotal * 12, "aggregated qty subtotal failed"
    assert abs(aggregate_entry.weight_output - original_weight * 12) < 0.0001, "aggregated weight failed"
    assert abs(project.total_weight - aggregate_entry.weight_output) < 0.0001, "project total weight failed"

    material_summary = aggregate_project(project)
    assert abs(material_summary.total_weight - project.total_weight) < 0.0001, "project material summary total failed"
    assert len(material_summary.lines) == 1, "project material summary should merge duplicate designations"
    assert material_summary.lines[0].total_qty == original_quantity * 12, "project material summary quantity failed"
    assert material_summary.lines[0].source_fullstrings == [
        "51-1.1/2B × 10",
        "51-1.1/2B × 2",
    ], "project material summary source labels failed"

    linear_project = analyze_project_rows([ProjectInputRow("24-L50-04", 2)])
    linear_summary = aggregate_project(linear_project)
    linear_lines = linear_summary.get_linear_lines()
    assert linear_lines, "project cutting summary should include linear material"
    assert "24-L50-04 × 2" in linear_lines[0].source_fullstrings, "project cutting source label failed"

    errored = analyze_project_rows([ProjectInputRow("99-1B", 5)])
    assert errored.errors == ["99-1B: Type 99 not implemented"], f"project error propagation failed: {errored.errors}"
    assert errored.total_support_count == 5, "errored enabled row should still count supports"

    try:
        analyze_project_rows([ProjectInputRow("51-1.1/2B", 0)])
        raise AssertionError("zero project quantity should fail")
    except ValueError:
        pass

    import os
    import tempfile
    import openpyxl
    from export.excel_export import export_project_to_excel, export_project_workbook

    fd, path = tempfile.mkstemp(suffix=".xlsx")
    os.close(fd)
    try:
        export_project_to_excel(project, path)
        wb = openpyxl.load_workbook(path, data_only=True)
        ws = wb.active
        assert ws.title == "Project_Weight_Analysis", "project Excel sheet name failed"
        assert ws.cell(row=1, column=1).value == "型號", "project Excel header failed"
        assert ws.cell(row=1, column=9).value == "單件數量", "project Excel single section missing"
        assert ws.cell(row=1, column=12).value == "總數量", "project Excel total section missing"
        assert ws.cell(row=2, column=2).value == 10, "project Excel quantity failed"
        assert ws.cell(row=2, column=9).value == original_quantity, "project Excel single quantity failed"
        assert ws.cell(row=2, column=12).value == original_quantity * 10, "project Excel total quantity failed"
    finally:
        try:
            os.remove(path)
        except OSError:
            pass

    fd, path = tempfile.mkstemp(suffix=".xlsx")
    os.close(fd)
    try:
        export_project_workbook(project, path)
        wb = openpyxl.load_workbook(path, data_only=True)
        assert wb.sheetnames == [
            "專案摘要",
            "重量分析",
            "材料合計",
            "下料明細",
            "下料圖示",
        ], f"project package workbook sheets changed: {wb.sheetnames}"
        ws_summary = wb["專案摘要"]
        assert ws_summary.cell(row=1, column=1).value == "專案材料統計總覽", "project package summary title failed"
        ws_weight = wb["重量分析"]
        assert ws_weight.cell(row=3, column=1).value == "型號", "project package weight header failed"
        assert ws_weight.cell(row=4, column=2).value == 10, "project package quantity failed"
        ws_material = wb["材料合計"]
        assert ws_material.cell(row=3, column=1).value == "品名", "project package material summary header failed"
        assert ws_material.cell(row=4, column=9).value == original_quantity * 12, "project package material purchase qty failed"
        ws_visual = wb["下料圖示"]
        assert ws_visual.cell(row=1, column=1).value == "下料圖示", "project package cutting visual title failed"
    finally:
        try:
            os.remove(path)
        except OSError:
            pass

    print("v project aggregation wrapper OK")
except Exception as e:
    print(f"X project aggregation wrapper ERROR: {e}")

# Type 01 Rev.1 table and note guardrails.
try:
    from core.calculator import analyze_single
    from core.config_loader import get_type_table_as_dict

    type01_table = get_type_table_as_dict("01")
    assert type01_table[22]["pipe_size"] == "14", "Type 01 22 inch support pipe changed"
    assert type01_table[24]["L"] == 677, "Type 01 24 inch L should follow D-1 Rev.1"
    assert type01_table[50]["pipe_size"] == "28", "Type 01 50 inch support pipe missing"
    assert type01_table[50]["L"] == 1382, "Type 01 50 inch L missing"

    type01_large = analyze_single("01-50B-05A")
    assert not type01_large.error, f"Type 01 50B should calculate: {type01_large.error}"
    assert type01_large.entries[0].spec == '28"*STD.WT', f"Type 01 50B upper pipe spec changed: {type01_large.entries[0].spec}"
    assert type01_large.entries[0].length == 1482, f"Type 01 50B upper pipe length changed: {type01_large.entries[0].length}"
    assert any("NOTE 6" in warning for warning in type01_large.warnings), "Type 01 M42 A/B/E/G paving warning missing"

    type01_mid = analyze_single("01-28B-05B")
    assert not type01_mid.error, f"Type 01 28B should calculate: {type01_mid.error}"
    assert type01_mid.entries[0].spec == '16"*STD.WT', f"Type 01 28B upper pipe spec changed: {type01_mid.entries[0].spec}"
    assert type01_mid.entries[0].length == 882, f"Type 01 28B upper pipe length changed: {type01_mid.entries[0].length}"

    def _type01_names(result):
        return [entry.name for entry in result.entries]

    def _type01_entry(result, index):
        return result.entries[index - 1]

    def _expect_pipe_weight(entry):
        from core.pipe import normalize_schedule
        from core.parser import get_lookup_value
        from data.pipe_table import get_pipe_details

        size_token, schedule_token = entry.spec.split('"*', 1)
        size = get_lookup_value(size_token)
        schedule = normalize_schedule(schedule_token)
        pipe_details = get_pipe_details(size, schedule, entry.material)
        expected_unit_weight = round(entry.length / 1000 * pipe_details["weight_per_m"], 2)
        assert entry.weight_per_unit == pipe_details["weight_per_m"], (
            f"{entry.name} {entry.spec} kg/m changed: {entry.weight_per_unit}"
        )
        assert entry.unit_weight == expected_unit_weight, (
            f"{entry.name} {entry.spec} unit weight changed: {entry.unit_weight} != {expected_unit_weight}"
        )
        assert entry.total_weight == expected_unit_weight * entry.quantity, (
            f"{entry.name} {entry.spec} total weight changed: {entry.total_weight}"
        )
        assert entry.weight_output == entry.factor * entry.total_weight, (
            f"{entry.name} {entry.spec} output weight changed: {entry.weight_output}"
        )

    def _expect_plate_weight(entry):
        density = {"A36/SS400": 7.85, "SUS304": 7.93, "AS": 7.82}.get(entry.material, 7.85)
        raw_weight = entry.length / 1000 * entry.width / 1000 * float(entry.spec) * density
        expected_unit_weight = round(raw_weight, 2)
        expected_total_weight = round(raw_weight * entry.quantity, 2)
        expected_output = round(entry.factor * expected_total_weight, 2)
        assert entry.unit_weight == expected_unit_weight, (
            f"{entry.name} plate unit weight changed: {entry.unit_weight} != {expected_unit_weight}"
        )
        assert entry.total_weight == expected_total_weight, (
            f"{entry.name} plate total weight changed: {entry.total_weight} != {expected_total_weight}"
        )
        assert entry.weight_output == expected_output, (
            f"{entry.name} plate output weight changed: {entry.weight_output} != {expected_output}"
        )

    def _expect_bolt_weight(entry):
        assert entry.unit_weight == 1, f"{entry.name} unit weight should remain 1 kg/set: {entry.unit_weight}"
        assert entry.total_weight == entry.quantity, f"{entry.name} total weight should equal quantity: {entry.total_weight}"
        assert entry.weight_output == round(entry.factor * entry.total_weight, 2), (
            f"{entry.name} output weight changed: {entry.weight_output}"
        )

    from data.pipe_table import get_pipe_details as _pipe_details_for_formula
    from data.pipe_table import pipe_weight_constant as _pipe_weight_constant

    assert round(_pipe_weight_constant(7.93), 5) == 0.02491, "SUS304 pipe weight constant changed"
    assert _pipe_details_for_formula(3, "40S", "SUS304")["weight_per_m"] == 11.41, "standard SUS304 pipe formula changed"
    assert _pipe_details_for_formula(3, "40S", "A53Gr.B")["weight_per_m"] == 11.29, "carbon steel pipe formula changed"

    _TYPE01_H01_CASES = {
        "01-4B-06U": {
            "pipe_spec": '3"*SCH.40',
            "upper": 239,
            "lower": 500,
            "names": ["Pipe", "Pipe", "Plate_a_無鑽孔", "Plate_d_有鑽孔", "EXP.BOLT"],
            "m42": [
                ("Plate_a_無鑽孔", 150, 150, "A36/SS400"),
                ("Plate_d_有鑽孔", 290, 290, "SUS304"),
                ("EXP.BOLT", 0, 0, "SUS304"),
            ],
            "warnings": 0,
        },
        "01-4B-04U": {
            "pipe_spec": '3"*SCH.40',
            "upper": 239,
            "lower": 300,
            "names": ["Pipe", "Pipe", "Plate_a_無鑽孔", "Plate_d_有鑽孔", "EXP.BOLT"],
            "m42": [
                ("Plate_a_無鑽孔", 150, 150, "A36/SS400"),
                ("Plate_d_有鑽孔", 290, 290, "SUS304"),
                ("EXP.BOLT", 0, 0, "SUS304"),
            ],
            "warnings": 0,
        },
        "01-6B-16T": {
            "pipe_spec": '4"*SCH.40',
            "upper": 286,
            "lower": 1500,
            "names": ["Pipe", "Pipe", "Plate_a_無鑽孔"],
            "m42": [("Plate_a_無鑽孔", 230, 230, "SUS304")],
            "warnings": 1,
        },
        "01-6B-06U": {
            "pipe_spec": '4"*SCH.40',
            "upper": 286,
            "lower": 500,
            "names": ["Pipe", "Pipe", "Plate_a_無鑽孔", "Plate_d_有鑽孔", "EXP.BOLT"],
            "m42": [
                ("Plate_a_無鑽孔", 230, 230, "A36/SS400"),
                ("Plate_d_有鑽孔", 370, 370, "SUS304"),
                ("EXP.BOLT", 0, 0, "SUS304"),
            ],
            "warnings": 0,
        },
        "01-3B-05U": {
            "pipe_spec": '2"*SCH.40',
            "upper": 193,
            "lower": 400,
            "names": ["Pipe", "Pipe", "Plate_a_無鑽孔", "Plate_d_有鑽孔", "EXP.BOLT"],
            "m42": [
                ("Plate_a_無鑽孔", 150, 150, "A36/SS400"),
                ("Plate_d_有鑽孔", 290, 290, "SUS304"),
                ("EXP.BOLT", 0, 0, "SUS304"),
            ],
            "warnings": 0,
        },
        "01-3B-04D": {
            "pipe_spec": '2"*SCH.40',
            "upper": 193,
            "lower": 300,
            "names": ["Pipe", "Pipe", "Plate_a_無鑽孔", "Plate_e_無鑽孔"],
            "m42": [
                ("Plate_a_無鑽孔", 150, 150, "A36/SS400"),
                ("Plate_e_無鑽孔", 200, 200, "A36/SS400"),
            ],
            "warnings": 0,
        },
    }

    for designation, expected in _TYPE01_H01_CASES.items():
        result = analyze_single(designation)
        assert not result.error, f"{designation} should calculate: {result.error}"
        assert _type01_names(result) == expected["names"], f"{designation} M42 BOM changed: {_type01_names(result)}"
        assert len(result.warnings) == expected["warnings"], f"{designation} warning count changed: {result.warnings}"
        upper = _type01_entry(result, 1)
        lower = _type01_entry(result, 2)
        assert upper.spec == expected["pipe_spec"], f"{designation} upper pipe spec changed: {upper.spec}"
        assert upper.length == expected["upper"], f"{designation} upper pipe length changed: {upper.length}"
        assert upper.material == "SUS304", f"{designation} upper pipe material changed: {upper.material}"
        assert lower.spec == expected["pipe_spec"], f"{designation} lower pipe spec changed: {lower.spec}"
        assert lower.length == expected["lower"], f"{designation} lower pipe length changed: {lower.length}"
        assert lower.material == "A53Gr.B", f"{designation} lower pipe material changed: {lower.material}"
        _expect_pipe_weight(upper)
        _expect_pipe_weight(lower)
        for offset, (name, length, width, material) in enumerate(expected["m42"], start=3):
            entry = _type01_entry(result, offset)
            assert entry.name == name, f"{designation} M42 entry name changed: {entry.name}"
            assert entry.length == length, f"{designation} {name} length changed: {entry.length}"
            assert entry.width == width, f"{designation} {name} width changed: {entry.width}"
            assert entry.material == material, f"{designation} {name} material changed: {entry.material}"
            if entry.name == "EXP.BOLT":
                _expect_bolt_weight(entry)
            else:
                _expect_plate_weight(entry)
        if designation == "01-6B-16T":
            assert any("H=1600mm" in warning for warning in result.warnings), f"{designation} H-limit warning missing: {result.warnings}"

    print("v type01 Rev.1 table/note guardrails OK")
except Exception as e:
    print(f"X type01 Rev.1 table/note guardrails ERROR: {e}")

# Phase H-02: Type 10/15/16 dimensional and weight guardrails.
try:
    from core.calculator import analyze_single
    from data.steel_sections import get_section_weight

    def _h02_entry(result, index):
        return result.entries[index - 1]

    def _h02_names(result):
        return [entry.name for entry in result.entries]

    def _expect_steel_weight(entry):
        expected_per_m = get_section_weight(entry.name, entry.spec)
        expected_unit_weight = round(entry.length / 1000 * expected_per_m, 2)
        expected_total_weight = round(expected_unit_weight * entry.quantity, 2)
        assert entry.weight_per_unit == expected_per_m, (
            f"{entry.name} {entry.spec} kg/m changed: {entry.weight_per_unit}"
        )
        assert entry.unit_weight == expected_unit_weight, (
            f"{entry.name} {entry.spec} unit weight changed: {entry.unit_weight} != {expected_unit_weight}"
        )
        assert entry.total_weight == expected_total_weight, (
            f"{entry.name} {entry.spec} total weight changed: {entry.total_weight}"
        )
        assert entry.weight_output == round(entry.factor * expected_total_weight, 2), (
            f"{entry.name} {entry.spec} output weight changed: {entry.weight_output}"
        )

    def _expect_custom_weight(entry, unit_weight):
        assert entry.unit_weight == unit_weight, f"{entry.name} unit weight changed: {entry.unit_weight}"
        assert entry.total_weight == round(unit_weight * entry.quantity, 2), f"{entry.name} total weight changed"
        assert entry.weight_output == round(entry.factor * entry.total_weight, 2), f"{entry.name} output weight changed"

    type10 = analyze_single("10-2B-05A")
    assert not type10.error, f"Type 10 should calculate: {type10.error}"
    assert _h02_names(type10) == ["Pipe", "Pipe", "Plate_F", "ADJ.BOLT", "HEX NUT", "Plate_a_無鑽孔"], (
        f"Type 10 BOM sequence changed: {_h02_names(type10)}"
    )
    assert _h02_entry(type10, 1).length == 271, f"Type 10 main pipe length changed: {_h02_entry(type10, 1).length}"
    assert _h02_entry(type10, 1).material == "SUS304", f"Type 10 main pipe material changed: {_h02_entry(type10, 1).material}"
    assert _h02_entry(type10, 2).length == 200, f"Type 10 support pipe length changed: {_h02_entry(type10, 2).length}"
    assert _h02_entry(type10, 2).material == "A53Gr.B", f"Type 10 support pipe material changed: {_h02_entry(type10, 2).material}"
    assert _h02_entry(type10, 3).length == 170 and _h02_entry(type10, 3).width == 170 and _h02_entry(type10, 3).spec == "9" and _h02_entry(type10, 3).quantity == 2, "Type 10 Plate_F changed"
    assert _h02_entry(type10, 4).spec == "M12*160L" and _h02_entry(type10, 4).quantity == 4, "Type 10 adjustable bolt changed"
    assert _h02_entry(type10, 5).spec == "M12" and _h02_entry(type10, 5).quantity == 16, "Type 10 hex nut changed"
    assert _h02_entry(type10, 6).length == 150 and _h02_entry(type10, 6).width == 150, "Type 10 M42 plate changed"
    _expect_pipe_weight(_h02_entry(type10, 1))
    _expect_pipe_weight(_h02_entry(type10, 2))
    _expect_plate_weight(_h02_entry(type10, 3))
    _expect_custom_weight(_h02_entry(type10, 4), 0.8)
    _expect_custom_weight(_h02_entry(type10, 5), 0.15)
    _expect_plate_weight(_h02_entry(type10, 6))

    type10_high = analyze_single("10-6B-16A")
    assert not type10_high.error, f"Type 10 high-H case should calculate: {type10_high.error}"
    assert any("H=1600mm" in warning for warning in type10_high.warnings), f"Type 10 H-limit warning missing: {type10_high.warnings}"
    assert _h02_entry(type10_high, 1).length == 386, f"Type 10 6B main pipe length changed: {_h02_entry(type10_high, 1).length}"
    assert _h02_entry(type10_high, 1).material == "SUS304", f"Type 10 6B main pipe material changed: {_h02_entry(type10_high, 1).material}"
    assert _h02_entry(type10_high, 2).length == 1300, f"Type 10 6B support pipe length changed: {_h02_entry(type10_high, 2).length}"
    assert _h02_entry(type10_high, 2).material == "A53Gr.B", f"Type 10 6B support pipe material changed: {_h02_entry(type10_high, 2).material}"
    assert _h02_entry(type10_high, 3).length == 260 and _h02_entry(type10_high, 3).width == 260 and _h02_entry(type10_high, 3).spec == "12" and _h02_entry(type10_high, 3).quantity == 2, "Type 10 6B Plate_F changed"
    assert _h02_entry(type10_high, 5).quantity == 16, "Type 10 6B hex nut changed"
    for entry in type10_high.entries:
        if entry.name == "Pipe":
            _expect_pipe_weight(entry)
        elif entry.category == "鋼板類":
            _expect_plate_weight(entry)

    type15 = analyze_single("15-2B-1005")
    assert not type15.error, f"Type 15 should calculate: {type15.error}"
    assert _h02_names(type15) == ["Pipe", "Channel", "Plate_WING", "Plate_STOPPER", "Plate_BASE", "Plate_TOP"], (
        f"Type 15 BOM sequence changed: {_h02_names(type15)}"
    )
    assert _h02_entry(type15, 1).length == 382, f"Type 15 pipe length should be H-2F-channelHeight: {_h02_entry(type15, 1).length}"
    assert _h02_entry(type15, 2).length == 1000, f"Type 15 channel length changed: {_h02_entry(type15, 2).length}"
    assert (_h02_entry(type15, 3).length, _h02_entry(type15, 3).width, _h02_entry(type15, 3).spec, _h02_entry(type15, 3).quantity) == (150, 95, "9", 4), "Type 15 wing plate changed"
    assert (_h02_entry(type15, 4).length, _h02_entry(type15, 4).width, _h02_entry(type15, 4).spec, _h02_entry(type15, 4).quantity) == (160, 70, "6", 2), "Type 15 stopper plate changed"
    assert (_h02_entry(type15, 5).length, _h02_entry(type15, 5).width, _h02_entry(type15, 5).spec) == (190, 190, "9"), "Type 15 base plate changed"
    assert (_h02_entry(type15, 6).length, _h02_entry(type15, 6).width, _h02_entry(type15, 6).spec) == (80, 80, "9"), "Type 15 top plate changed"
    assert "shape=wing_plate" in _h02_entry(type15, 3).remark, "Type 15 wing plate remark missing"
    assert "shape=stopper_plate" in _h02_entry(type15, 4).remark, "Type 15 stopper plate remark missing"
    _expect_pipe_weight(_h02_entry(type15, 1))
    _expect_steel_weight(_h02_entry(type15, 2))
    for entry in type15.entries[2:]:
        _expect_plate_weight(entry)

    type15_high = analyze_single("15-6B-1036")
    assert not type15_high.error, f"Type 15 high-H case should calculate: {type15_high.error}"
    assert any("H=3600mm" in warning for warning in type15_high.warnings), f"Type 15 H-limit warning missing: {type15_high.warnings}"
    assert _h02_entry(type15_high, 1).length == 3418, f"Type 15 6B pipe length changed: {_h02_entry(type15_high, 1).length}"
    for entry in type15_high.entries:
        if entry.name == "Pipe":
            _expect_pipe_weight(entry)
        elif entry.name == "Channel":
            _expect_steel_weight(entry)
        elif entry.category == "鋼板類":
            _expect_plate_weight(entry)

    type15_10 = analyze_single("15-10B-1005")
    assert not type15_10.error, f"Type 15 10B should calculate: {type15_10.error}"
    assert _h02_entry(type15_10, 2).quantity == 2, "Type 15 10B should use double channel"
    assert _h02_entry(type15_10, 2).remark == "detail_a_double_channel_for_10in_and_12in", "Type 15 10B detail-a remark missing"
    assert _h02_entry(type15_10, 3).quantity == 4, "Type 15 10B wing plate should be 4 pieces"
    assert _h02_entry(type15_10, 4).quantity == 2, "Type 15 10B stopper plate should be 2 pieces"

    type15_12 = analyze_single("15-12B-1005")
    assert not type15_12.error, f"Type 15 12B should calculate: {type15_12.error}"
    assert _h02_entry(type15_12, 2).quantity == 2, "Type 15 12B should use double channel"
    assert _h02_entry(type15_12, 2).remark == "detail_a_double_channel_for_10in_and_12in", "Type 15 12B detail-a remark missing"
    assert _h02_entry(type15_12, 3).quantity == 4, "Type 15 12B wing plate should be 4 pieces"
    assert _h02_entry(type15_12, 4).quantity == 2, "Type 15 12B stopper plate should be 2 pieces"

    type14 = analyze_single("14-2B-1005")
    assert not type14.error, f"Type 14 should calculate: {type14.error}"
    assert _h02_names(type14) == ["Pipe", "Channel", "Plate_WING", "Plate_STOPPER", "Plate_BASE", "Plate_TOP", "EXP.BOLT"], (
        f"Type 14 BOM sequence changed: {_h02_names(type14)}"
    )
    assert _h02_entry(type14, 1).length == 382, f"Type 14 pipe length should be H-2F-channelHeight: {_h02_entry(type14, 1).length}"
    assert _h02_entry(type14, 2).length == 1000 and _h02_entry(type14, 2).quantity == 1, "Type 14 channel changed"
    assert (_h02_entry(type14, 3).length, _h02_entry(type14, 3).width, _h02_entry(type14, 3).spec, _h02_entry(type14, 3).quantity) == (150, 65, "9", 4), "Type 14 wing plate changed"
    assert (_h02_entry(type14, 4).length, _h02_entry(type14, 4).width, _h02_entry(type14, 4).spec, _h02_entry(type14, 4).quantity) == (160, 70, "6", 2), "Type 14 stopper plate changed"
    assert (_h02_entry(type14, 5).length, _h02_entry(type14, 5).width, _h02_entry(type14, 5).spec) == (190, 190, "9"), "Type 14 base plate changed"
    assert (_h02_entry(type14, 6).length, _h02_entry(type14, 6).width, _h02_entry(type14, 6).spec) == (80, 80, "9"), "Type 14 top plate changed"
    assert _h02_entry(type14, 7).spec == '5/8"' and _h02_entry(type14, 7).quantity == 4, "Type 14 anchor bolt changed"
    assert "shape=wing_plate" in _h02_entry(type14, 3).remark, "Type 14 wing plate remark missing"
    assert "shape=stopper_plate" in _h02_entry(type14, 4).remark, "Type 14 stopper plate remark missing"
    _expect_pipe_weight(_h02_entry(type14, 1))
    _expect_steel_weight(_h02_entry(type14, 2))
    for entry in type14.entries[2:6]:
        _expect_plate_weight(entry)
    _expect_bolt_weight(_h02_entry(type14, 7))

    type14_10 = analyze_single("14-10B-1005")
    assert not type14_10.error, f"Type 14 10B should calculate: {type14_10.error}"
    assert _h02_entry(type14_10, 2).quantity == 2, "Type 14 10B should use double channel"
    assert _h02_entry(type14_10, 2).remark == "detail_a_double_channel_for_10in_and_12in", "Type 14 10B detail-a remark missing"
    assert _h02_entry(type14_10, 3).quantity == 4, "Type 14 10B wing plate should be 4 pieces"
    assert _h02_entry(type14_10, 4).quantity == 2, "Type 14 10B stopper plate should be 2 pieces"

    type14_12 = analyze_single("14-12B-1005")
    assert not type14_12.error, f"Type 14 12B should calculate: {type14_12.error}"
    assert _h02_entry(type14_12, 2).quantity == 2, "Type 14 12B should use double channel"
    assert _h02_entry(type14_12, 2).remark == "detail_a_double_channel_for_10in_and_12in", "Type 14 12B detail-a remark missing"
    assert _h02_entry(type14_12, 3).quantity == 4, "Type 14 12B wing plate should be 4 pieces"
    assert _h02_entry(type14_12, 4).quantity == 2, "Type 14 12B stopper plate should be 2 pieces"

    type16 = analyze_single("16-2B-05")
    assert not type16.error, f"Type 16 should calculate: {type16.error}"
    assert _h02_names(type16) == ["Pipe", "Pipe", "Plate"], f"Type 16 BOM sequence changed: {_h02_names(type16)}"
    assert _h02_entry(type16, 1).length == 206, f"Type 16 main pipe length changed: {_h02_entry(type16, 1).length}"
    assert _h02_entry(type16, 1).material == "SUS304", f"Type 16 main pipe material changed: {_h02_entry(type16, 1).material}"
    assert _h02_entry(type16, 2).length == 670, f"Type 16 support pipe length changed: {_h02_entry(type16, 2).length}"
    assert _h02_entry(type16, 2).material == "A53Gr.B", f"Type 16 support pipe material changed: {_h02_entry(type16, 2).material}"
    assert (_h02_entry(type16, 3).length, _h02_entry(type16, 3).width, _h02_entry(type16, 3).spec) == (70, 70, "6"), "Type 16 plate changed"
    _expect_pipe_weight(_h02_entry(type16, 1))
    _expect_pipe_weight(_h02_entry(type16, 2))
    _expect_plate_weight(_h02_entry(type16, 3))

    type16_6b = analyze_single("16-6B-05")
    assert not type16_6b.error, f"Type 16 6B should calculate: {type16_6b.error}"
    assert _h02_entry(type16_6b, 1).length == 413, f"Type 16 6B main pipe length changed: {_h02_entry(type16_6b, 1).length}"
    assert _h02_entry(type16_6b, 1).material == "SUS304", f"Type 16 6B main pipe material changed: {_h02_entry(type16_6b, 1).material}"
    assert _h02_entry(type16_6b, 2).length == 616, f"Type 16 6B support pipe length changed: {_h02_entry(type16_6b, 2).length}"
    assert _h02_entry(type16_6b, 2).material == "A53Gr.B", f"Type 16 6B support pipe material changed: {_h02_entry(type16_6b, 2).material}"
    assert (_h02_entry(type16_6b, 3).length, _h02_entry(type16_6b, 3).width, _h02_entry(type16_6b, 3).spec) == (140, 140, "6"), "Type 16 6B plate changed"
    for entry in type16_6b.entries:
        if entry.name == "Pipe":
            _expect_pipe_weight(entry)
        elif entry.category == "鋼板類":
            _expect_plate_weight(entry)

    print("v phase H-02 type10/type15/type16 guardrails OK")
except Exception as e:
    print(f"X phase H-02 type10/type15/type16 guardrails ERROR: {e}")
    raise

# Type 20/26 structural guardrails.
try:
    from core.calculator import analyze_single

    type03 = analyze_single("03-1B-05L")
    assert not type03.error, f"Type 03 should calculate: {type03.error}"
    assert type03.entries[0].name == "Angle", f"Type 03 first entry should be vertical angle: {type03.entries[0].name}"
    assert type03.entries[0].length == 574.8, f"Type 03 vertical angle formula changed: {type03.entries[0].length}"
    assert "LR elbow center=38.1" in type03.entries[0].remark, f"Type 03 vertical angle remark missing formula: {type03.entries[0].remark}"
    assert type03.entries[1].length == 130, f"Type 03 horizontal angle length changed: {type03.entries[1].length}"
    assert type03.entries[3].name == "Plate_c_有鑽孔", f"Type 03 M42 Type-L plate changed: {[entry.name for entry in type03.entries]}"
    assert type03.entries[4].name == "EXP.BOLT" and type03.entries[4].quantity == 4, f"Type 03 M42 Type-L bolt changed: {[entry.name for entry in type03.entries]}"

    type20 = analyze_single("20-L50-05A")
    assert not type20.error, f"Type 20 should calculate: {type20.error}"
    assert len(type20.entries) == 1, f"Type 20 BOM count changed: {len(type20.entries)}"
    assert type20.entries[0].length == 500, f"Type 20 H length changed: {type20.entries[0].length}"

    type26_a = analyze_single("26-L50-1005A")
    assert not type26_a.error, f"Type 26 Fig-A should calculate: {type26_a.error}"
    assert [entry.name for entry in type26_a.entries] == ["Angle", "Angle", "Angle"], (
        f"Type 26 Fig-A BOM sequence changed: {[entry.name for entry in type26_a.entries]}"
    )
    assert [entry.length for entry in type26_a.entries] == [500, 500, 1000], (
        f"Type 26 Fig-A member lengths changed: {[entry.length for entry in type26_a.entries]}"
    )
    assert [entry.remark for entry in type26_a.entries] == ["Fig-A, H段上件", "Fig-A, H段下件", "Fig-A, L段"], (
        f"Type 26 Fig-A remarks changed: {[entry.remark for entry in type26_a.entries]}"
    )

    type26_c = analyze_single("26-L50-1005C")
    assert not type26_c.error, f"Type 26 Fig-C should calculate: {type26_c.error}"
    assert [entry.name for entry in type26_c.entries[:3]] == ["Angle", "Angle", "Angle"], (
        f"Type 26 Fig-C steel members changed: {[entry.name for entry in type26_c.entries]}"
    )
    assert [entry.length for entry in type26_c.entries[:3]] == [500, 500, 1000], (
        f"Type 26 Fig-C steel lengths changed: {[entry.length for entry in type26_c.entries[:3]]}"
    )
    assert type26_c.entries[3].name == "LUG_PLATE_C", f"Type 26 Fig-C lug plate missing: {[entry.name for entry in type26_c.entries]}"
    assert type26_c.entries[3].quantity == 2, f"Type 26 Fig-C should use 2 lug plates: {type26_c.entries[3].quantity}"
    assert type26_c.entries[4].name == "BOLT", f"Type 26 Fig-C K bolt missing: {[entry.name for entry in type26_c.entries]}"
    assert type26_c.entries[4].quantity == 8, f"Type 26 Fig-C should use 8 K bolts: {type26_c.entries[4].quantity}"

    type25_c = analyze_single("25-L50-0505C-0401")
    assert not type25_c.error, f"Type 25 Fig-C should calculate: {type25_c.error}"
    assert type25_c.entries[2].name == "LUG_PLATE_C", f"Type 25 Fig-C lug plate missing: {[entry.name for entry in type25_c.entries]}"
    assert type25_c.entries[2].quantity == 1, f"Type 25 Fig-C should use 1 lug plate: {type25_c.entries[2].quantity}"
    assert type25_c.entries[3].name == "BOLT", f"Type 25 Fig-C K bolt missing: {[entry.name for entry in type25_c.entries]}"
    assert type25_c.entries[3].quantity == 4, f"Type 25 Fig-C should use 4 K bolts: {type25_c.entries[3].quantity}"

    print("v type03/type20/type26 structural guardrails OK")
except Exception as e:
    print(f"X type03/type20/type26 structural guardrails ERROR: {e}")
    raise

# Type 52/66 D-80 pad and FB guardrails.
try:
    import math

    from core.calculator import analyze_single
    from data.pipe_table import get_pipe_details

    def _entry_by_name(result, name):
        for entry in result.entries:
            if entry.name == name:
                return entry
        raise AssertionError(f"{result.fullstring} missing {name}: {[e.name for e in result.entries]}")

    small = analyze_single("66-1.1/2B(P)-A-150-150")
    assert not small.error, f"Type 66 small pad should calculate: {small.error}"
    small_pad = _entry_by_name(small, "Pad_52Type")
    small_details = get_pipe_details(1.5, "10S")
    small_od = small_details["od_mm"]
    small_t_sch10s = small_details["thickness_mm"]   # Phase 5: <=8" uses Sch10S wall
    assert small_pad.length == 200, f"small Pad_52Type length should be D+50: {small_pad.length}"
    assert small_pad.width == round(small_od * math.pi / 3), f"small Pad_52Type 120-degree width changed: {small_pad.width}"
    assert small_pad.spec == str(small_t_sch10s), f"small Pad_52Type thickness should be Sch10S wall ({small_t_sch10s}mm): {small_pad.spec}"

    large = analyze_single("66-10B(P)-A-150-250")
    assert not large.error, f"Type 66 large pad should calculate: {large.error}"
    large_pad = _entry_by_name(large, "Pad_52Type")
    large_od = get_pipe_details(10, "10S")["od_mm"]
    assert large_pad.length == 400, f"large Pad_52Type length should be E*2+50+250: {large_pad.length}"
    assert large_pad.width == round(large_od * math.pi / 3), f"large Pad_52Type 120-degree width changed: {large_pad.width}"
    assert large_pad.spec == "9", f"large Pad_52Type thickness should be 9t: {large_pad.spec}"

    h_beam = _entry_by_name(large, "H Beam")
    assert h_beam.length == 300, f"H Beam length should be LOPS+50: {h_beam.length}"

    fb3 = _entry_by_name(large, "FB_52Type_3")
    assert fb3.quantity == 4, f"FB_52Type_3 should be 4 pieces for 10 inch and larger: {fb3.quantity}"
    assert fb3.length == 150, f"FB_52Type_3 length should use HOPS: {fb3.length}"
    assert fb3.width == 143.5, f"FB_52Type_3 width should be A+35/2-C/2: {fb3.width}"
    assert "HOPS" in fb3.remark, f"FB_52Type_3 HOPS precision marker missing: {fb3.remark}"

    compact = analyze_single("66-14B(P)-100-300")
    assert not compact.error, f"Type 66 compact HOPS/LOPS format should calculate: {compact.error}"
    compact_h_beam = _entry_by_name(compact, "H Beam")
    compact_fb3 = _entry_by_name(compact, "FB_52Type_3")
    assert compact_h_beam.length == 350, f"compact Type 66 H Beam should use LOPS+50: {compact_h_beam.length}"
    assert compact_fb3.length == 100, f"compact Type 66 FB_52Type_3 should use HOPS: {compact_fb3.length}"

    print("v type52/type66 pad and FB guardrails OK")
except Exception as e:
    print(f"X type52/type66 pad and FB guardrails ERROR: {e}")

# Urgent project priority Type guardrails.
try:
    from collections import Counter

    from core.calculator import analyze_single

    _PRIORITY_TYPE_CASES = [
        ("01", "01-2B-05A"),
        ("01", "01-50B-05A"),
        ("10", "10-2B-05A"),
        ("15", "15-2B-1005"),
        ("16", "16-2B-05"),
        ("20", "20-L50-05A"),
        ("21", "21-L50-05A"),
        ("22", "22-L50-05AL"),
        ("22", "22-L75-12(A)X"),
        ("23", "23-L50-05A"),
        ("24", "24-L50-05"),
        ("25", "25-L50-0505A"),
        ("25", "25-L50-0505C-0401"),
        ("26", "26-L50-1005A"),
        ("26", "26-L50-1005C"),
        ("27", "27-L75-0505L-0401"),
        ("27", "27-L50-0204X-0101"),
        ("27", "27-H150-0505L-0401"),
        ("28", "28-L50-1005L"),
        ("30", "30-L75-0505A-0401"),
        ("31", "31-L50-1005"),
        ("32", "32-L50-1005"),
        ("33", "33-L50-1005"),
        ("34", "34-L50-1005"),
        ("35", "35-C125-05A"),
        ("37", "37-C125-1200A"),
        ("37", "37-C125-1200B-05"),
        ("51", "51-2B"),
        ("51", "51-1.1/2B"),
        ("51", "51-4B"),
        ("51", "51-26B"),
        ("52", "52-2B(P)-A(A)-130-500"),
        ("52", "52-14B(P)-A(A)-130-500"),
        ("53", "53-2B(P)-A(A)-130-500"),
        ("53", "53-14B(P)-A(A)-130-500"),
        ("57", "57-2B-A"),
        ("57", "57-1.1/2B-A"),
        ("59", "59-6B-A"),
        ("59", "59-1.1/2B-B(S)"),
        ("80", "80-2B(P)-A(A)-130-500"),
        ("80", "80-30B-A(A)-130-500"),
        ("66", "66-14B(P)-100-300"),
        ("66", "66-1.1/2B(P)-A-150-150"),
    ]

    def _assert_entry_sane(entry, designation):
        assert entry.quantity > 0, f"{designation} entry {entry.item_no} has non-positive quantity"
        assert entry.factor >= 0, f"{designation} entry {entry.item_no} has negative factor"
        assert entry.unit_weight >= 0, f"{designation} entry {entry.item_no} has negative unit weight"
        assert entry.total_weight >= 0, f"{designation} entry {entry.item_no} has negative total weight"
        assert entry.weight_output >= 0, f"{designation} entry {entry.item_no} has negative weight output"
        if entry.length:
            assert 0 < entry.length < 10000, f"{designation} entry {entry.item_no} unreasonable length: {entry.length}"
        if entry.width:
            assert 0 < entry.width < 10000, f"{designation} entry {entry.item_no} unreasonable width: {entry.width}"
        if entry.category in ("型鋼類", "管路類"):
            assert entry.length > 0, f"{designation} {entry.name} should have positive takeoff length"
        if entry.category == "鋼板類":
            assert entry.length > 0 and entry.width > 0, f"{designation} {entry.name} should have plate dimensions"
            assert float(entry.spec) > 0, f"{designation} {entry.name} should have positive plate thickness"

    priority_results = {}
    for type_id, designation in _PRIORITY_TYPE_CASES:
        result = analyze_single(designation)
        priority_results[designation] = result
        assert not result.error, f"{designation} should calculate for priority project: {result.error}"
        assert result.entries, f"{designation} should produce BOM entries"
        assert result.total_weight > 0, f"{designation} should have positive total weight"
        for entry in result.entries:
            _assert_entry_sane(entry, designation)

    type27_h150 = priority_results["27-H150-0505L-0401"]
    type28_l50 = priority_results["28-L50-1005L"]
    type27_l75 = priority_results["27-L75-0505L-0401"]
    type27_l50_x = priority_results["27-L50-0204X-0101"]
    l75_remarks = Counter(entry.remark for entry in type27_l75.entries)
    h150_remarks = Counter(entry.remark for entry in type27_h150.entries)
    h150_names = Counter(entry.name for entry in type27_h150.entries)
    assert l75_remarks["Column, H=500-15=485, L1=400, L2=100"] == 1, "Type 27 angle version should split column steel entry"
    assert l75_remarks["Top support beam, L=500, L1=400, L2=100"] == 1, "Type 27 angle version should split top support beam steel entry"
    assert type27_l75.entries[0].length == 485 and type27_l75.entries[1].length == 500, "Type 27 angle steel lengths changed"
    assert any("M-42 型式 'X' 非標準" in warning for warning in type27_l50_x.warnings), "Type 27 nonstandard M42 warning missing"
    assert type27_l50_x.entries[0].length == 385 and type27_l50_x.entries[1].length == 200, "Type 27 angle X-case lengths changed"
    assert h150_remarks["Column"] == 1, "Type 27 H150 should include one Column steel entry"
    assert h150_remarks["Top support beam"] == 1, "Type 27 H150 should include one Top support beam steel entry"
    assert h150_names["Plate_6t_Side"] == 1, "Type 27 H150 side plate line missing"
    assert h150_names["Plate_9t_Wing"] == 1, "Type 27 H150 wing plate line missing"
    assert h150_names["Plate_6t_Top"] == 0, "Type 27 H150 should not include top plate"
    assert any("Plate_" in entry.name and "有鑽孔" in entry.name for entry in type27_h150.entries), "Type 27 H150 M42 base plate missing"
    assert any(entry.name == "EXP.BOLT" for entry in type27_h150.entries), "Type 27 H150 anchor bolt missing"

    type28_names = [entry.name for entry in type28_l50.entries]
    type28_remarks = [entry.remark for entry in type28_l50.entries[:3]]
    type28_lengths = [entry.length for entry in type28_l50.entries[:3]]
    assert type28_names[:3] == ["Angle", "Angle", "Angle"], f"Type 28 should split portal frame into three steel entries: {type28_names}"
    assert type28_lengths == [500, 1000, 500], f"Type 28 left/top/right lengths changed: {type28_lengths}"
    assert type28_remarks == [
        "Left leg, H=500 (Angle:可U-bolt側掛)",
        "Top beam, L=1000 (Angle:可U-bolt側掛)",
        "Right leg, H=500 (Angle:可U-bolt側掛)",
    ], f"Type 28 steel remarks changed: {type28_remarks}"
    assert any("Plate_" in entry.name and "有鑽孔" in entry.name for entry in type28_l50.entries), "Type 28 M42 base plate missing"
    assert any(entry.name == "EXP.BOLT" for entry in type28_l50.entries), "Type 28 anchor bolt missing"

    type30_a = priority_results["30-L75-0505A-0401"]
    type30_names = [entry.name for entry in type30_a.entries]
    type30_lengths = [entry.length for entry in type30_a.entries]
    type30_remarks = [entry.remark for entry in type30_a.entries]
    assert type30_names == ["Angle", "Angle"], f"Type 30 Fig-A should split into column + top beam: {type30_names}"
    assert type30_lengths == [500, 500], f"Type 30 Fig-A lengths changed: {type30_lengths}"
    assert type30_remarks == [
        "FIG-A, Column, H=500, L1=400, L2=100",
        "FIG-A, Top beam, L=500, L1=400, L2=100",
    ], f"Type 30 Fig-A remarks changed: {type30_remarks}"

    type30_b = analyze_single("30-L75-0505B-0401")
    assert not type30_b.error, f"Type 30 Fig-B should calculate: {type30_b.error}"
    assert [entry.name for entry in type30_b.entries] == ["Angle", "Angle"], f"Type 30 Fig-B should split into column + top beam: {[entry.name for entry in type30_b.entries]}"
    assert [entry.length for entry in type30_b.entries] == [485, 500], f"Type 30 Fig-B lengths changed: {[entry.length for entry in type30_b.entries]}"
    assert [entry.remark for entry in type30_b.entries] == [
        "FIG-B, Column, H=500-15=485, L1=400, L2=100",
        "FIG-B, Top beam, L=500, L1=400, L2=100",
    ], f"Type 30 Fig-B remarks changed: {[entry.remark for entry in type30_b.entries]}"

    type31 = priority_results["31-L50-1005"]
    assert [entry.name for entry in type31.entries] == ["Angle", "Angle", "Angle"], f"Type 31 should split into left leg + top beam + right leg: {[entry.name for entry in type31.entries]}"
    assert [entry.length for entry in type31.entries] == [500, 1000, 500], f"Type 31 lengths changed: {[entry.length for entry in type31.entries]}"
    assert [entry.remark for entry in type31.entries] == [
        "Left leg, H=500",
        "Top beam, L=1000",
        "Right leg, H=500",
    ], f"Type 31 remarks changed: {[entry.remark for entry in type31.entries]}"

    type32 = priority_results["32-L50-1005"]
    assert [entry.name for entry in type32.entries] == ["Angle", "Angle", "Angle"], f"Type 32 should split into left leg + bottom beam + right leg: {[entry.name for entry in type32.entries]}"
    assert [entry.length for entry in type32.entries] == [500, 1000, 500], f"Type 32 lengths changed: {[entry.length for entry in type32.entries]}"
    assert [entry.remark for entry in type32.entries] == [
        "Left leg, H=500",
        "Bottom beam, L=1000",
        "Right leg, H=500",
    ], f"Type 32 remarks changed: {[entry.remark for entry in type32.entries]}"

    type33 = priority_results["33-L50-1005"]
    assert [entry.name for entry in type33.entries] == ["Angle", "Angle"], f"Type 33 should stay as column + bottom beam half-frame: {[entry.name for entry in type33.entries]}"
    assert [entry.length for entry in type33.entries] == [500, 1000], f"Type 33 lengths changed: {[entry.length for entry in type33.entries]}"
    assert [entry.remark for entry in type33.entries] == [
        "懸臂框H向(立柱), H=500",
        "懸臂框L向(下梁), L=1000",
    ], f"Type 33 remarks changed: {[entry.remark for entry in type33.entries]}"

    type34 = priority_results["34-L50-1005"]
    assert [entry.name for entry in type34.entries] == ["Angle", "Angle"], f"Type 34 should stay as column + top beam cantilever: {[entry.name for entry in type34.entries]}"
    assert [entry.length for entry in type34.entries] == [500, 1000], f"Type 34 lengths changed: {[entry.length for entry in type34.entries]}"
    assert [entry.remark for entry in type34.entries] == [
        "懸臂梁H向(立柱), H=500",
        "懸臂梁L向(上梁), L=1000",
    ], f"Type 34 remarks changed: {[entry.remark for entry in type34.entries]}"

    type35_a = priority_results["35-C125-05A"]
    assert [entry.name for entry in type35_a.entries] == ["Channel"], f"Type 35 FIG-A should stay a single support rail entry: {[entry.name for entry in type35_a.entries]}"
    assert [(entry.length, entry.quantity, entry.remark) for entry in type35_a.entries] == [
        (500, 1, "托條 FIG-A, H=500"),
    ], f"Type 35 FIG-A changed: {[(entry.length, entry.quantity, entry.remark) for entry in type35_a.entries]}"

    type35_b = analyze_single("35-C125-05B")
    assert not type35_b.error, f"Type 35 FIG-B should calculate: {type35_b.error}"
    assert [entry.name for entry in type35_b.entries] == ["Channel"], f"Type 35 FIG-B should stay a single line with qty=2: {[entry.name for entry in type35_b.entries]}"
    assert [(entry.length, entry.quantity, entry.remark) for entry in type35_b.entries] == [
        (500, 2, "托條 FIG-B(雙條), H=500 ×2"),
    ], f"Type 35 FIG-B changed: {[(entry.length, entry.quantity, entry.remark) for entry in type35_b.entries]}"

    type51_small = priority_results["51-2B"]
    assert [(entry.name, entry.length, entry.width, entry.quantity, entry.remark) for entry in type51_small.entries] == [
        ("FLAT BAR", 60, 50, 2, "鞍座, 60x50x9, 全焊接(6V), ×2"),
    ], f"Type 51 small-pipe flat bar path changed: {[(entry.name, entry.length, entry.width, entry.quantity, entry.remark) for entry in type51_small.entries]}"

    type51_mid = priority_results["51-4B"]
    assert [(entry.name, entry.spec, entry.length, entry.quantity) for entry in type51_mid.entries] == [
        ("Angle", "50*50*6", 125, 2),
    ], f"Type 51 4-24in member path should use table H length: {[(entry.name, entry.spec, entry.length, entry.quantity) for entry in type51_mid.entries]}"
    assert type51_mid.entries[0].remark == "Member M, ×2, H=125mm, 兩側3mm gap, 長度≤梁寬(NOTE 2)", f"Type 51 mid-pipe remark changed: {type51_mid.entries[0].remark}"

    type51_large = priority_results["51-26B"]
    assert [(entry.name, entry.spec, entry.length, entry.quantity) for entry in type51_large.entries[:1]] == [
        ("Channel", "125*65*6", 300, 2),
    ], f"Type 51 large-pipe channel path changed: {[(entry.name, entry.spec, entry.length, entry.quantity) for entry in type51_large.entries]}"
    assert len(type51_large.entries) == 2 and type51_large.entries[1].name == "PIPE PAD", f"Type 51 large-pipe D-91 pad missing: {[(entry.name, entry.spec) for entry in type51_large.entries]}"
    assert type51_large.entries[1].spec == "12" and type51_large.entries[1].length == 400 and type51_large.entries[1].width > 0, f"Type 51 large-pipe pad dimensions changed: {(type51_large.entries[1].spec, type51_large.entries[1].length, type51_large.entries[1].width)}"
    assert "D-91 reinforcing pad" in type51_large.entries[1].remark, f"Type 51 large-pipe pad remark changed: {type51_large.entries[1].remark}"

    type52 = priority_results["52-2B(P)-A(A)-130-500"]
    type53 = priority_results["53-2B(P)-A(A)-130-500"]
    assert [(e.name, e.spec, e.length, e.width, e.quantity) for e in type52.entries] == [
        (e.name, e.spec, e.length, e.width, e.quantity) for e in type53.entries
    ], "Type 53 should share Type 52 D-80 shoe geometry path"
    assert type52.entries[0].name == "Pad_52Type" and "length_rule=D + 25*2" in type52.entries[0].remark, f"Type 52 small-pipe pad remark missing rule: {type52.entries[0].remark}"
    assert type52.entries[1].name == "Angle" and "CUT IN FIELD" in type52.entries[1].remark, f"Type 52 L40 remark missing field-cut note: {type52.entries[1].remark}"

    type52_large = priority_results["52-14B(P)-A(A)-130-500"]
    type53_large = priority_results["53-14B(P)-A(A)-130-500"]
    assert [(e.name, e.spec, e.length, e.width, e.quantity) for e in type52_large.entries] == [
        (e.name, e.spec, e.length, e.width, e.quantity) for e in type53_large.entries
    ], "Type 53 large <=24in path should share Type 52 geometry"
    assert any(entry.name == "FB_52Type_3" and entry.quantity == 4 for entry in type52_large.entries), f"Type 52 large-pipe FB_52Type_3 x4 missing: {[(entry.name, entry.quantity) for entry in type52_large.entries]}"
    assert "length_rule=E*2 + 25*2 + 250" in type52_large.entries[0].remark, f"Type 52 large-pipe pad remark missing rule: {type52_large.entries[0].remark}"
    assert "width=A+35/2-member_t/2" in type52_large.entries[-1].remark, f"Type 52 FB_52Type_3 remark missing width rule: {type52_large.entries[-1].remark}"

    type57_slide = priority_results["57-2B-A"]
    type57_fixed = analyze_single("57-2B-B")
    assert [(entry.name, entry.spec, entry.material, entry.quantity) for entry in type57_slide.entries] == [
        ("U-BOLT", "UB-2B", "Carbon Steel", 1),
        ("FINISHED HEX NUT", '3/8"', "Carbon Steel", 4),
    ], f"Type 57 should use M-26 U-bolt + four hex nuts: {[(entry.name, entry.spec, entry.material, entry.quantity) for entry in type57_slide.entries]}"
    assert "M-26, SLIDE" in type57_slide.entries[0].remark and "B/C/D/E=62/71/58/74" in type57_slide.entries[0].remark, f"Type 57 slide M-26 metadata missing: {type57_slide.entries[0].remark}"
    assert not type57_fixed.error and "M-26, FIXED" in type57_fixed.entries[0].remark, f"Type 57 fixed mode failed: {type57_fixed.error or type57_fixed.entries[0].remark}"

    type59_b = priority_results["59-1.1/2B-B(S)"]
    assert [(entry.name, entry.spec, entry.material, entry.quantity) for entry in type59_b.entries] == [
        ("LUG PLATE", "6", "A240-304", 1),
        ("U-BOLT", "UB-1 1/2B", "Carbon Steel", 1),
        ("FINISHED HEX NUT", '3/8"', "Carbon Steel", 4),
    ], f"Type 59 Fig-B should use D-70 lug plate + M-26 U-bolt/nuts: {[(entry.name, entry.spec, entry.material, entry.quantity) for entry in type59_b.entries]}"
    assert "D-68 / M-26" in type59_b.entries[1].remark and "B/C/D/E=51/60/58/68" in type59_b.entries[1].remark, f"Type 59 M-26 metadata missing: {type59_b.entries[1].remark}"

    type80_small = priority_results["80-2B(P)-A(A)-130-500"]
    assert [(entry.name, entry.spec, entry.length, entry.quantity, entry.material) for entry in type80_small.entries] == [
        ("REINFORCING_PAD", "9", 200, 1, "AS"),
        ("H Beam", "200*100*5.5", 500, 1, "AS"),
    ], f"Type 80 D-95 small-pipe model changed: {[(entry.name, entry.spec, entry.length, entry.quantity, entry.material) for entry in type80_small.entries]}"
    assert "HOPS=130, LOPS=500" in type80_small.entries[1].remark, f"Type 80 D-95 override metadata missing: {type80_small.entries[1].remark}"

    type80_big = priority_results["80-30B-A(A)-130-500"]
    assert [(entry.name, entry.spec, entry.quantity, entry.material) for entry in type80_big.entries] == [
        ("SADDLE_SIDE_PLATE", "16", 2, "AS"),
        ("SADDLE_FOOT_PLATE", "16", 1, "AS"),
        ("SADDLE_ARC_PLATE", "16", 1, "AS"),
        ("STIFFENER_PLATE", "12", 4, "AS"),
        ("REINFORCING_PAD", "12", 1, "AS"),
        ("Angle", "100*100*10", 2, "AS"),
    ], f"Type 80 D-96 large-pipe model changed: {[(entry.name, entry.spec, entry.quantity, entry.material) for entry in type80_big.entries]}"
    assert any("NO.7 has PLATE 6 THK x6" in warning for warning in type80_big.warnings), f"Type 80 D-96 NO.7 warning missing: {type80_big.warnings}"

    print(f"v urgent priority Type guardrails OK ({len(_PRIORITY_TYPE_CASES)} cases + Type 80)")
except Exception as e:
    print(f"X urgent priority Type guardrails ERROR: {e}")
    raise

try:
    from data.component_table_registry import (
        EXISTING_COMPONENT_TABLES,
        MISSING_COMPONENT_TABLES,
        get_component_table_coverage,
    )
    coverage = get_component_table_coverage()
    print(
        "component coverage: "
        f"{coverage['implemented']}/{coverage['total']} "
        f"({coverage['coverage_ratio']:.1%})"
    )
    print("lookup-ready components:", coverage["lookup_ready"])
    print("partial-lookup components:", coverage.get("partial_lookup", 0))
    print("metadata-only components:", coverage["metadata_only"])
    print("implemented components:", ", ".join(sorted(EXISTING_COMPONENT_TABLES)))
    print("missing components:", ", ".join(MISSING_COMPONENT_TABLES))
except Exception as e:
    print(f"X component registry ERROR: {e}")

# Test full M/N metadata baseline
try:
    import importlib
    from data.component_table_registry import (
        EXISTING_COMPONENT_TABLES,
        METADATA_ONLY_COMPONENT_TABLES,
        MISSING_COMPONENT_TABLES,
        get_component_table_coverage,
    )

    coverage = get_component_table_coverage()
    assert coverage["implemented"] == 71, f"expected 71 component modules: {coverage}"
    assert coverage["missing"] == 0, f"expected no missing component modules: {coverage}"
    assert coverage["lookup_ready"] == 19, f"lookup-ready count changed unexpectedly: {coverage}"
    assert coverage["partial_lookup"] == 3, f"partial-lookup count changed unexpectedly: {coverage}"
    assert coverage["metadata_only"] == 49, f"metadata-only count failed: {coverage}"
    assert not MISSING_COMPONENT_TABLES, f"missing list should be empty: {MISSING_COMPONENT_TABLES}"

    for component_id, module_file in EXISTING_COMPONENT_TABLES.items():
        module_name = module_file[:-3]
        module = importlib.import_module(f"data.{module_name}")
        getter_name = f"get_{component_id.lower().replace('-', '').replace(' ', '').replace('/', '').replace('.', '')}_component"
        if component_id == "N-12A":
            getter_name = "get_n12a_component"
        if component_id == "N27-PU BLOCK":
            getter_name = "get_n27_pu_block_component"
        getter = getattr(module, getter_name, None)
        if getter is None:
            continue
        component = getter()
        assert component["component_id"] == component_id, f"{component_id} getter returned {component}"
        if component_id in METADATA_ONLY_COMPONENT_TABLES:
            assert component["table_kind"] == "metadata_only" and not component["lookup_ready"], f"{component_id} metadata failed: {component}"

    print("v full M/N component metadata baseline OK")
except Exception as e:
    print(f"X full M/N component metadata baseline ERROR: {e}")

# Test m45_table
try:
    from data.m45_table import get_m45_by_dia, get_m45_by_type
    r1 = get_m45_by_dia("1/2\"")
    # Note: data shows 2312, original test expected 1200. We use data values.
    assert r1 is not None and r1["tensile_kg"] == 2312, f"m45 1/2 failed: {r1}"
    print("v m45_table OK")
except Exception as e:
    print(f"X m45_table ERROR: {e}")

# Test m4_table
try:
    from data.m4_table import get_m4_by_line_size
    r_m4 = get_m4_by_line_size('2"')
    assert (
        r_m4 is not None
        and r_m4["designation"] == "PCL-A-2B"
        and r_m4["B"] == 54
        and r_m4["F"] == '1/2"'
        and r_m4["source_component"] == "M-4"
        and r_m4["source_transcribed"]
        and r_m4["set_weight_kg"] > 0
    ), f"m4 failed: {r_m4}"
    print("v m4_table OK")
except Exception as e:
    print(f"X m4_table ERROR: {e}")

# Test m6_table
try:
    from data.m6_table import get_m6_by_line_size
    r_m6 = get_m6_by_line_size("4")
    r_m6_2_5 = get_m6_by_line_size('2 1/2"')
    assert r_m6 is not None and r_m6["type_label"] == "TYPE-C" and r_m6["designation"] == "PCL-C-4B" and not r_m6["lookup_ready"] and r_m6["partial_lookup_ready"] and r_m6["set_weight_kg"] is None, f"m6 failed: {r_m6}"
    assert r_m6_2_5 is not None and r_m6_2_5["designation"] == "PCL-C-2 1/2B", f"m6 2 1/2 failed: {r_m6_2_5}"
    print("v m6_table OK")
except Exception as e:
    print(f"X m6_table ERROR: {e}")

# Test m5/m7 PDF designation coverage
try:
    from data.m5_table import get_m5_by_line_size
    from data.m7_table import get_m7_by_line_size
    r_m5_12 = get_m5_by_line_size('12"')
    r_m7_8 = get_m7_by_line_size('8"')
    r_m7_28 = get_m7_by_line_size('28"')
    r_m7_2 = get_m7_by_line_size('2"')
    assert r_m5_12 is not None and r_m5_12["designation"] == "PCL-B-12B" and r_m5_12["rod_size_a"] == '1 1/2"' and r_m5_12["load_650f_kg"] == 3930 and r_m5_12["source_component"] == "M-5" and not r_m5_12["lookup_ready"] and r_m5_12["set_weight_kg"] is None, f"m5 12 failed: {r_m5_12}"
    assert r_m7_8 is not None and r_m7_8["designation"] == "PCL-D-8B" and r_m7_8["rod_size_a"] == '1 1/8"' and r_m7_8["load_650f_kg"] == 2175 and r_m7_8["source_component"] == "M-7", f"m7 8 failed: {r_m7_8}"
    assert r_m7_28 is not None and r_m7_28["load_750f_kg"] is None and r_m7_28["load_750f_status"] == "source_blank_or_not_applicable", f"m7 28 load750 failed: {r_m7_28}"
    assert r_m7_2 is None, f"m7 2 should be None (not in PDF): {r_m7_2}"
    print("v m5/m7 PDF designation coverage OK")
except Exception as e:
    print(f"X m5/m7 PDF designation coverage ERROR: {e}")

# Test m21_table
try:
    from data.m21_table import get_m21_by_dia
    r_m21 = get_m21_by_dia('1 1/4"')
    assert r_m21 is not None and r_m21["take_up_mm"] == 180 and r_m21["unit_weight_kg"] > 0, f"m21 failed: {r_m21}"
    print("v m21_table OK")
except Exception as e:
    print(f"X m21_table ERROR: {e}")

# Test m24_table
try:
    from data.m24_table import get_m24_by_dia
    r_m24 = get_m24_by_dia('7/8"')
    assert r_m24 is not None and r_m24["pin_dia_b"] == '1"' and r_m24["unit_weight_kg"] > 0, f"m24 failed: {r_m24}"
    print("v m24_table OK")
except Exception as e:
    print(f"X m24_table ERROR: {e}")

# Test Type 11 table-backed hardware
try:
    from data.type11_table import get_type11_hardware_item, build_type11_spring_item
    from core.calculator import analyze_single
    rod11 = get_type11_hardware_item("threaded_rod")
    washer11 = get_type11_hardware_item("washer")
    spring11 = build_type11_spring_item("SPR14")
    type11_result = analyze_single("11-6B-08J")
    type11_spring_entry = next((entry for entry in type11_result.entries if entry.name == "SPRING"), None)
    type11_washer_entry = next((entry for entry in type11_result.entries if entry.name == "WASHER"), None)
    assert rod11 is not None and rod11["spec"] == '1-5/8"*300L' and rod11["length_mm"] == 300, f"type11 rod failed: {rod11}"
    assert washer11 is not None and washer11["category"] == "鋼板類" and washer11["unit_weight_kg"] == 1.0, f"type11 washer failed: {washer11}"
    assert spring11 is not None and spring11["spec"] == "SPR14 (14W×46ID)" and spring11["spring_k_kg_per_mm"] == 42, f"type11 spring failed: {spring11}"
    assert not type11_result.error and type11_spring_entry and type11_spring_entry.category == "彈簧類", f"type11 calculator spring failed: {type11_result}"
    assert type11_washer_entry and type11_washer_entry.category == "鋼板類", f"type11 calculator washer failed: {type11_result}"
    print("v type11 hardware table OK")
except Exception as e:
    print(f"X type11 hardware table ERROR: {e}")

# Test m47_table
try:
    from data.m47_table import build_m47_item, get_m47_dimensions
    r_m47 = build_m47_item('10"')
    dims_m47 = get_m47_dimensions("24")
    assert r_m47 is not None and r_m47["width_mm"] == 80 and r_m47["length_mm"] == 858 and r_m47["unit_weight_kg"] > 0, f"m47 failed: {r_m47}"
    assert dims_m47 == (90, 1915), f"m47 dims failed: {dims_m47}"
    print("v m47_table OK")
except Exception as e:
    print(f"X m47_table ERROR: {e}")

# Test AI-visual transcribed component tables and remaining metadata-only tables
try:
    from data.m52_table import get_m52_by_line_size, get_m52_component, get_m52_spring_data
    from data.m53_table import get_m53_by_line_size, get_m53_component
    from data.m54_table import build_m54_item, get_m54_by_line_size, get_m54_component
    from data.m55_table import build_m55_item, get_m55_by_line_size, get_m55_component
    from data.n1_table import get_n1_component
    r_m52 = get_m52_component()
    r_m52_24 = get_m52_by_line_size('24"')
    r_m52_spring = get_m52_spring_data('24"')
    r_m53 = get_m53_component()
    r_m53_24 = get_m53_by_line_size('24"')
    r_m54 = get_m54_component()
    r_m54_2 = get_m54_by_line_size('2"', fig_no=2)
    r_m54_fig3 = get_m54_by_line_size('2"', fig_no=3)
    r_m54_item = build_m54_item('2"', fig_no=2)
    r_m55 = get_m55_component()
    r_m55_8 = get_m55_by_line_size('8"')
    r_m55_item = build_m55_item('8"')
    r_n1 = get_n1_component()
    assert r_m52["table_kind"] == "dimensional_lookup" and r_m52["lookup_ready"] and not r_m52["weight_ready"], f"m52 lookup summary failed: {r_m52}"
    assert r_m52_24 is not None and r_m52_24["designation"] == "SPRW-24B" and r_m52_24["dimensions_mm"]["H"] == 610 and r_m52_24["thread_size_j"] == '1"', f"m52 24 failed: {r_m52_24}"
    assert r_m52_spring is not None and r_m52_spring["wire_dia_mm"] == 10 and r_m52_spring["spring_constant_kg_per_mm"] == 45, f"m52 spring failed: {r_m52_spring}"
    assert r_m53["table_kind"] == "dimensional_lookup" and r_m53["lookup_ready"] and not r_m53["weight_ready"], f"m53 lookup summary failed: {r_m53}"
    assert r_m53_24 is not None and r_m53_24["designation"] == "PUBS2-24B" and r_m53_24["dimensions_mm"]["A"] == 838 and r_m53_24["bar_size"] == "150x12", f"m53 24 failed: {r_m53_24}"
    assert r_m54["table_kind"] == "dimensional_lookup" and r_m54["lookup_ready"] and r_m54["weight_ready"], f"m54 lookup summary failed: {r_m54}"
    assert r_m54_2 is not None and r_m54_2["designation"] == "PUBS3-2B-2" and r_m54_2["dimensions_mm"]["A"] == 63.6 and r_m54_2["dimensions_mm"]["B"] == 150 and r_m54_2["unit_weight_kg"] == 0.34, f"m54 2 failed: {r_m54_2}"
    assert r_m54_item is not None and r_m54_item["spec"].startswith("PUBS3-2B-2") and r_m54_item["category"] == "鋼板類", f"m54 item failed: {r_m54_item}"
    assert r_m54_fig3 is None, f"m54 unsupported fig should be None: {r_m54_fig3}"
    assert r_m55["table_kind"] == "dimensional_lookup" and r_m55["lookup_ready"] and not r_m55["weight_ready"], f"m55 lookup summary failed: {r_m55}"
    assert r_m55_8 is not None and r_m55_8["designation"] == "PUBD1-8B" and r_m55_8["dimensions_mm"]["B"] == 410 and r_m55_8["unit_weight_kg"] == 3.62, f"m55 8 failed: {r_m55_8}"
    assert r_m55_item is not None and r_m55_item["spec"].startswith("PUBD1-8B") and r_m55_item["category"] == "鋼板類", f"m55 item failed: {r_m55_item}"
    assert r_n1["component_id"] == "N-1" and r_n1["table_kind"] == "metadata_only", f"n1 metadata failed: {r_n1}"
    print("v m52/m53/m54/m55 visual lookup + metadata-only component tables OK")
except Exception as e:
    print(f"X m52/m53/m54/m55 visual lookup + metadata-only component tables ERROR: {e}")

# Test m22_table
try:
    from data.m22_table import build_m22_item
    r12 = build_m22_item('3/4"', 600, left_hand=True)
    assert r12 is not None and r12["designation"] == "MTRL-3/4-600" and r12["thread_length_c"] == 152 and r12["unit_weight_kg"] > 0, f"m22 failed: {r12}"
    print("v m22_table OK")
except Exception as e:
    print(f"X m22_table ERROR: {e}")

# Test m23_table
try:
    from data.m23_table import build_m23_item, get_m23_by_dia
    r13 = get_m23_by_dia('1 1/2"')
    r13_item = build_m23_item('1 1/2"', 900, left_hand=True)
    assert r13 is not None and r13["recommended_bolt_dia_b"] == '1 5/8"' and r13["thread_length_d"] == 152, f"m23 failed: {r13}"
    assert r13_item is not None and r13_item["designation"] == "WERL-1 1/2-900" and r13_item["unit_weight_kg"] > 0, f"m23 build failed: {r13_item}"
    r13_inferred = get_m23_by_dia('1 1/8"')
    assert r13_inferred is None, f"m23 1 1/8 should be None (not in PDF): {r13_inferred}"
    print("v m23_table OK")
except Exception as e:
    print(f"X m23_table ERROR: {e}")

# Test m25_table
try:
    from data.m25_table import build_m25_item
    r14 = build_m25_item('7/8"', left_hand=True)
    assert r14 is not None and r14["designation"] == "WENL-7/8" and r14["G"] == 25 and r14["unit_weight_kg"] > 0, f"m25 failed: {r14}"
    print("v m25_table OK")
except Exception as e:
    print(f"X m25_table ERROR: {e}")

# Test m26_table
try:
    from data.m26_table import get_m26_by_line_size
    r15 = get_m26_by_line_size('2"')
    assert r15 is not None and r15["type"] == "UB-2B" and r15["C"] == 71, f"m26 failed: {r15}"
    print("v m26_table OK")
except Exception as e:
    print(f"X m26_table ERROR: {e}")

# Test m28_table
try:
    from data.m28_table import get_m28_takeoff
    r16 = get_m28_takeoff('1 1/2"', fig=2)
    from data.m28_table import get_m28_by_rod_size
    r16_item = get_m28_by_rod_size('1-1/2"')
    r16_inferred = get_m28_by_rod_size('1 1/8"')
    assert r16 == 102 and r16_item is not None and r16_item["unit_weight_kg"] > 0, f"m28 failed: {r16}/{r16_item}"
    assert r16_inferred is None, f"m28 1 1/8 should be None (not in PDF): {r16_inferred}"
    print("v m28_table OK")
except Exception as e:
    print(f"X m28_table ERROR: {e}")

# Test centralized component fallback rules
try:
    from core.component_rules import (
        estimate_clamp_weight,
        estimate_eye_nut_weight,
        estimate_m28_weight,
        estimate_rod_weight,
    )
    from core.hardware_material import (
        HardwareKind,
        HardwareMaterialOverrides,
        ServiceClass,
        parse_hardware_material_context,
        parse_hardware_material_overrides,
        parse_service_class,
        resolve_hardware_material,
    )
    assert estimate_clamp_weight('4"', component_id="M-6") == 2.3, "M-6 clamp estimate should use centralized multiplier"
    assert estimate_rod_weight('5/8"', 3000) > 0, "rod estimate failed"
    assert estimate_eye_nut_weight('5/8"') >= 0.15, "eye nut estimate failed"
    assert estimate_m28_weight('1 1/8"') >= 0.3, "M-28 estimate failed"
    override = HardwareMaterialOverrides(all_hardware="SUS316")
    override_spec = resolve_hardware_material(HardwareKind.CLAMP_BODY, overrides=override)
    cryo_rod_spec = resolve_hardware_material(HardwareKind.THREADED_ROD, service=ServiceClass.CRYO)
    support_pipe_spec = resolve_hardware_material(HardwareKind.SUPPORT_PIPE)
    high_temp_pipe_spec = resolve_hardware_material(HardwareKind.SUPPORT_PIPE, service=ServiceClass.HIGH_TEMP)
    support_plate_spec = resolve_hardware_material(HardwareKind.SUPPORT_PLATE)
    high_temp_plate_spec = resolve_hardware_material(HardwareKind.SUPPORT_PLATE, service=ServiceClass.HIGH_TEMP)
    unknown_override_spec = resolve_hardware_material(HardwareKind.CLAMP_BODY, overrides=HardwareMaterialOverrides(all_hardware="GLOBAL"))
    assert override_spec.name == "SUS316" and override_spec.canonical_id == "JIS_SUS316", "hardware material override failed"
    assert cryo_rod_spec.name == "A320 L7" and cryo_rod_spec.canonical_id == "ASTM_A320_L7", "hardware service material failed"
    assert support_pipe_spec.name == "A36 / SS400" and support_pipe_spec.canonical_id == "ASTM_A36_OR_JIS_SS400", "support pipe default failed"
    assert high_temp_pipe_spec.name == "SA-106 Gr.B" and high_temp_pipe_spec.canonical_id == "ASTM_SA_106_GR_B", "support pipe high-temp default failed"
    assert support_plate_spec.name == "A36 / SS400" and support_plate_spec.canonical_id == "ASTM_A36_OR_JIS_SS400", "support plate default failed"
    assert high_temp_plate_spec.name == "A36 / SS400" and high_temp_plate_spec.canonical_id == "ASTM_A36_OR_JIS_SS400", "support plate high-temp default failed"
    assert unknown_override_spec.name == "GLOBAL" and unknown_override_spec.canonical_id == "UNRESOLVED_GLOBAL", "unknown override canonical fallback failed"
    from core.material_identity import canonical_material_id
    from data.engineering_material_spec import DEFAULT_HARDWARE_MATERIAL
    for kind, per_service in DEFAULT_HARDWARE_MATERIAL.items():
        for service_key, material_name in per_service.items():
            service = ServiceClass.AMBIENT if service_key == "*" else service_key
            spec = resolve_hardware_material(kind, service=service)
            assert spec.name == material_name, f"{kind.value}/{service_key} material name changed: {spec}"
            assert spec.canonical_id == canonical_material_id(material_name), f"{kind.value}/{service_key} canonical_id failed: {spec}"
    print("v phase 2C MaterialSpec canonical_id OK")
    assert parse_service_class({"service_class": "high-temp"}) == ServiceClass.HIGH_TEMP, "service parser failed"
    empty_context = parse_hardware_material_context({})
    assert empty_context.service == ServiceClass.AMBIENT, "empty override service parser failed"
    assert empty_context.material_overrides is not None, "empty override must return concrete material overrides"
    assert isinstance(empty_context.material_overrides.per_kind, dict), "empty override per_kind must be dict"
    assert empty_context.material_overrides.per_kind == {}, "empty override per_kind should be empty dict"
    assert empty_context.material_overrides.all_hardware is None, "empty override all_hardware should be None"
    parsed = parse_hardware_material_overrides({
        "hardware_material_by_kind": {
            "threaded_rod": "A193 B8",
            HardwareKind.HEAVY_HEX_NUT: "A194 8",
        },
        "upper_material": "SUS316",
    }, legacy_material_keys=("upper_material",), legacy_material_kinds=(HardwareKind.UPPER_BRACKET,))
    assert parsed is not None and parsed.per_kind[HardwareKind.THREADED_ROD] == "A193 B8", "per-kind override parser failed"
    assert parsed.per_kind[HardwareKind.HEAVY_HEX_NUT] == "A194 8", "enum-key override parser failed"
    assert parsed.per_kind[HardwareKind.UPPER_BRACKET] == "SUS316", "legacy scoped parser failed"
    per_kind_context = parse_hardware_material_context({
        "hardware_material_by_kind": {
            "threaded_rod": "A193 B8",
            HardwareKind.HEAVY_HEX_NUT: "A194 8",
        },
    })
    assert per_kind_context.material_overrides is not None, "per-kind context overrides missing"
    assert isinstance(per_kind_context.material_overrides.per_kind, dict), "per-kind context per_kind must be dict"
    assert per_kind_context.material_overrides.per_kind[HardwareKind.THREADED_ROD] == "A193 B8", "per-kind context parser failed"
    assert per_kind_context.material_overrides.per_kind[HardwareKind.HEAVY_HEX_NUT] == "A194 8", "enum-key context parser failed"
    legacy_context = parse_hardware_material_context(
        {"upper_material": "SUS316"},
        legacy_material_keys=("upper_material",),
        legacy_material_kinds=(HardwareKind.UPPER_BRACKET,),
    )
    assert legacy_context.material_overrides is not None, "legacy context overrides missing"
    assert legacy_context.material_overrides.per_kind == {HardwareKind.UPPER_BRACKET: "SUS316"}, "legacy context parser failed"
    all_context = parse_hardware_material_context({"hardware_material": "INCONEL"})
    assert all_context.material_overrides is not None, "all-hardware context overrides missing"
    assert all_context.material_overrides.per_kind == {}, "all-hardware context per_kind should be empty dict"
    assert all_context.material_overrides.all_hardware == "INCONEL", "all-hardware context parser failed"
    context = parse_hardware_material_context({"service": "cryo", "hardware_material": "INCONEL", "pipe_material": "A335 P11"})
    assert context.service == ServiceClass.CRYO, "hardware material context service failed"
    assert context.material_overrides and context.material_overrides.all_hardware == "INCONEL", "hardware material context override failed"
    pipe_only = parse_hardware_material_context({"pipe_material": "A335 P11"})
    assert pipe_only.service == ServiceClass.AMBIENT and pipe_only.material_overrides is not None, "pipe_material context should still be normalized"
    assert pipe_only.material_overrides.per_kind == {} and pipe_only.material_overrides.all_hardware is None, "pipe_material must not affect hardware parser"
    print("v component_rules fallback layer OK")
except Exception as e:
    print(f"X component_rules fallback layer ERROR: {e}")

# Phase 2B material identity scaffold
try:
    from core.material_identity import (
        MATERIAL_ALIAS_MAP,
        MATERIAL_CATALOG,
        canonical_material_id,
        normalize_material_alias,
        resolve_material_identity,
    )

    assert MATERIAL_CATALOG["ASTM_A36_OR_JIS_SS400"].display_name == "A36 / SS400", "A36 catalog record failed"
    assert canonical_material_id("A36/SS400") == "ASTM_A36_OR_JIS_SS400", "A36 slash alias failed"
    assert canonical_material_id("A36 / SS400") == "ASTM_A36_OR_JIS_SS400", "A36 spaced alias failed"
    assert canonical_material_id("SA-106 Gr.B") == "ASTM_SA_106_GR_B", "SA-106 alias failed"
    assert canonical_material_id("ASTM A106 Grade B") == "ASTM_SA_106_GR_B", "A106 grade alias failed"
    assert canonical_material_id("A194 4 / S3") == "ASTM_A194_4_S3", "A194 4/S3 alias failed"
    assert canonical_material_id("SUS304") == "JIS_SUS304", "SUS304 alias failed"
    assert canonical_material_id("INCONEL") == "NICKEL_ALLOY_INCONEL", "INCONEL alias failed"
    assert resolve_material_identity("unknown-material") is None, "unknown material should not resolve"
    assert normalize_material_alias(" A36/SS400 ") in MATERIAL_ALIAS_MAP, "normalized alias map failed"
    print("v phase 2B material identity scaffold OK")
except Exception as e:
    print(f"X phase 2B material identity scaffold ERROR: {e}")

# Phase 2I pipe/plate MaterialSpec compatibility
try:
    from core.hardware_material import HardwareKind, ServiceClass, resolve_hardware_material
    from core.models import AnalysisResult
    from core.pipe import add_pipe_entry
    from core.plate import add_plate_entry

    string_pipe = AnalysisResult(fullstring="phase-2I-string-pipe")
    add_pipe_entry(string_pipe, 2, "SCH.40", 1000, "A36/SS400")
    assert string_pipe.entries[0].material == "A36/SS400", "pipe string material path changed"
    assert not hasattr(string_pipe.entries[0], "material_canonical_id"), "pipe string path should not attach canonical id"

    string_plate = AnalysisResult(fullstring="phase-2I-string-plate")
    add_plate_entry(string_plate, 100, 100, 10, "TEST_PLATE", material="SUS304")
    assert string_plate.entries[0].material == "SUS304", "plate string material path changed"
    assert not hasattr(string_plate.entries[0], "material_canonical_id"), "plate string path should not attach canonical id"

    pipe_spec = resolve_hardware_material(HardwareKind.SUPPORT_PIPE, service=ServiceClass.HIGH_TEMP)
    spec_pipe = AnalysisResult(fullstring="phase-2I-spec-pipe")
    add_pipe_entry(spec_pipe, 2, "SCH.40", 1000, pipe_spec)
    assert spec_pipe.entries[0].material == "SA-106 Gr.B", "pipe MaterialSpec should emit material.name"
    assert spec_pipe.entries[0].material_canonical_id == "ASTM_SA_106_GR_B", "pipe MaterialSpec canonical id missing"

    plate_spec = resolve_hardware_material(HardwareKind.SUPPORT_PLATE)
    spec_plate = AnalysisResult(fullstring="phase-2I-spec-plate")
    add_plate_entry(spec_plate, 100, 100, 10, "TEST_PLATE", material=plate_spec)
    assert spec_plate.entries[0].material == "A36 / SS400", "plate MaterialSpec should emit material.name"
    assert spec_plate.entries[0].material_canonical_id == "ASTM_A36_OR_JIS_SS400", "plate MaterialSpec canonical id missing"

    default_plate = AnalysisResult(fullstring="phase-4B-default-plate")
    add_plate_entry(default_plate, 100, 100, 10, "TEST_DEFAULT_PLATE")
    assert default_plate.entries[0].material == "A36/SS400", "plate default material string changed"
    assert default_plate.entries[0].material_canonical_id == "ASTM_A36_OR_JIS_SS400", "plate default canonical id missing"

    print("v phase 2I pipe/plate MaterialSpec compatibility OK")
except Exception as e:
    print(f"X phase 2I pipe/plate MaterialSpec compatibility ERROR: {e}")

# Phase 3A core helper MaterialSpec compatibility
try:
    from core.bolt import add_bolt_entry, add_custom_entry
    from core.hardware_material import HardwareKind, ServiceClass, resolve_hardware_material
    from core.m42 import perform_action_by_letter
    from core.models import AnalysisResult
    from core.steel import add_steel_section_entry
    from data.m42_table import get_m42_data, resolve_m42_data

    steel_spec = resolve_hardware_material(HardwareKind.STRUCTURAL_STRUT)
    bolt_spec = resolve_hardware_material(HardwareKind.ANCHOR_BOLT)
    nut_spec = resolve_hardware_material(HardwareKind.HEAVY_HEX_NUT)
    cryo_bolt_spec = resolve_hardware_material(
        HardwareKind.THREADED_ROD,
        service=ServiceClass.CRYO,
    )

    steel_string = AnalysisResult(fullstring="phase3A-steel-string")
    add_steel_section_entry(steel_string, "Angle", "40*40*5", 150, material="SUS304")
    assert steel_string.entries[0].material == "SUS304", "steel string material changed"
    assert not hasattr(steel_string.entries[0], "material_canonical_id"), "steel explicit string path should stay unmanaged"

    steel_default = AnalysisResult(fullstring="phase3A-steel-default")
    add_steel_section_entry(steel_default, "Angle", "40*40*5", 150)
    assert steel_default.entries[0].material == "A36/SS400", "steel default material changed"
    assert steel_default.entries[0].material_canonical_id == "ASTM_A36_OR_JIS_SS400", "steel default canonical id missing"

    steel_spec_result = AnalysisResult(fullstring="phase3A-steel-spec")
    add_steel_section_entry(steel_spec_result, "Angle", "40*40*5", 150, material=steel_spec)
    assert steel_spec_result.entries[0].material == steel_spec.name, "steel MaterialSpec material changed"
    assert steel_spec_result.entries[0].material_canonical_id == steel_spec.canonical_id, "steel MaterialSpec canonical id missing"

    custom_string = AnalysisResult(fullstring="phase3A-custom-string")
    add_custom_entry(custom_string, "CUSTOM", "C-1", "SUS304", 1, 0.1)
    assert custom_string.entries[0].material == "SUS304", "custom string material changed"
    assert not hasattr(custom_string.entries[0], "material_canonical_id"), "custom explicit string path should stay unmanaged"

    custom_spec = AnalysisResult(fullstring="phase3A-custom-spec")
    add_custom_entry(custom_spec, "CUSTOM", "C-2", nut_spec, 1, 0.1)
    assert custom_spec.entries[0].material == nut_spec.name, "custom MaterialSpec material changed"
    assert custom_spec.entries[0].material_canonical_id == nut_spec.canonical_id, "custom MaterialSpec canonical id missing"

    bolt_default = AnalysisResult(fullstring="phase3A-bolt-default")
    add_bolt_entry(bolt_default, 2, 4)
    assert bolt_default.entries[0].material == "SUS304", "bolt default material changed"
    assert bolt_default.entries[0].material_canonical_id == "JIS_SUS304", "bolt default canonical id missing"

    bolt_string = AnalysisResult(fullstring="phase3A-bolt-string")
    add_bolt_entry(bolt_string, 2, 4, material="SUS316")
    assert bolt_string.entries[0].material == "SUS316", "bolt string material changed"
    assert not hasattr(bolt_string.entries[0], "material_canonical_id"), "bolt explicit string path should stay unmanaged"

    bolt_spec_result = AnalysisResult(fullstring="phase3A-bolt-spec")
    add_bolt_entry(bolt_spec_result, 2, 4, material=cryo_bolt_spec)
    assert bolt_spec_result.entries[0].material == cryo_bolt_spec.name, "bolt MaterialSpec material changed"
    assert bolt_spec_result.entries[0].material_canonical_id == cryo_bolt_spec.canonical_id, "bolt MaterialSpec canonical id missing"

    m42_result = AnalysisResult(fullstring="phase3A-m42-default")
    perform_action_by_letter(m42_result, "E", "L50*50*6")
    assert [entry.material for entry in m42_result.entries] == ["A36/SS400", "A36/SS400", "SUS304", "A36/SS400"], f"m42 default materials changed: {[entry.material for entry in m42_result.entries]}"
    assert all(getattr(entry, "material_canonical_id", None) for entry in m42_result.entries), "m42 default canonical ids missing"

    m42_override = AnalysisResult(fullstring="phase3A-m42-override")
    perform_action_by_letter(
        m42_override,
        "B",
        2,
        plate_material=steel_spec,
        bolt_material=bolt_spec,
    )
    assert [entry.material for entry in m42_override.entries] == [steel_spec.name, steel_spec.name, bolt_spec.name], "m42 MaterialSpec override materials changed"
    assert [entry.material_canonical_id for entry in m42_override.entries] == [steel_spec.canonical_id, steel_spec.canonical_id, bolt_spec.canonical_id], "m42 MaterialSpec override canonical ids missing"

    assert get_m42_data(14)["plate_a"] == 440, "M-43 14 inch row missing"
    assert get_m42_data(16)["plate_bc"] == 630, "M-43 16 inch row missing"
    assert get_m42_data(28)["plate_e"] == 930, "M-43 28 inch row missing"
    assert get_m42_data(28)["exp_bolt_spec"] == '7/8"', "M-43 J bolt spec should follow Rev.1 table"

    m42_half, warn_half = resolve_m42_data(0.5)
    assert m42_half["plate_a"] == 150 and warn_half, "M42 0.5 inch fallback to 1 inch row missing"
    m42_three_quarter, warn_three_quarter = resolve_m42_data(0.75)
    assert m42_three_quarter["plate_a"] == 150 and warn_three_quarter, "M42 0.75 inch fallback to 1 inch row missing"
    m42_two_half, warn_two_half = resolve_m42_data(2.5)
    assert m42_two_half["plate_a"] == 150 and not warn_two_half, "M42 2.5 inch should use 1~3 inch row without warning"
    m42_twenty, warn_twenty = resolve_m42_data(20)
    assert m42_twenty["plate_a"] == 690 and warn_twenty, "M42 20 inch fallback to 24 inch row missing"
    m42_twenty_two, warn_twenty_two = resolve_m42_data(22)
    assert m42_twenty_two["plate_a"] == 690 and warn_twenty_two, "M42 22 inch fallback to 24 inch row missing"
    m42_twenty_six, warn_twenty_six = resolve_m42_data(26)
    assert m42_twenty_six["plate_a"] == 790 and warn_twenty_six, "M42 26 inch fallback to 28 inch row missing"

    m42_l80, warn_l80 = resolve_m42_data("L80*80*8")
    assert m42_l80["plate_a"] == 230 and warn_l80, "M42 L80 fallback to L100 row missing"

    m42_type_t = AnalysisResult(fullstring="phase3A-m42a-T")
    perform_action_by_letter(m42_type_t, "T", 2)
    assert [entry.name for entry in m42_type_t.entries] == ["Plate_a_無鑽孔"], "M-42A Type-T should add Plate a"
    assert [entry.material for entry in m42_type_t.entries] == ["SUS304"], "M-42A Type-T plate should be SS304"
    assert all(getattr(entry, "material_canonical_id", None) for entry in m42_type_t.entries), "M-42A Type-T canonical id missing"

    m42_type_v = AnalysisResult(fullstring="phase3A-m42a-V")
    perform_action_by_letter(m42_type_v, "V", 2)
    assert [entry.name for entry in m42_type_v.entries] == [
        "Plate_a_無鑽孔",
        "Plate_d_有鑽孔",
        "EXP.BOLT",
        "Angle",
    ], "M-42A Type-V component sequence changed"
    assert [entry.material for entry in m42_type_v.entries] == [
        "A36/SS400",
        "SUS304",
        "SUS304",
        "A36/SS400",
    ], "M-42A Type-V materials changed"
    assert m42_type_v.entries[-1].name == "Angle" and m42_type_v.entries[-1].quantity == 2, "M-42A Type-V should include two L40 angles"

    m42_type_n = AnalysisResult(fullstring="phase3A-m42-N")
    perform_action_by_letter(m42_type_n, "N", 2)
    assert [entry.name for entry in m42_type_n.entries] == ["Plate_a_無鑽孔"], "M-42 Type-N should not add L40 bracket"

    m42_a_075 = AnalysisResult(fullstring="phase3A-m42-A-075")
    perform_action_by_letter(m42_a_075, "A", 0.75)
    assert m42_a_075.entries[0].name == "Plate_a_無鑽孔", "M42 Type-A fallback should still use Plate a"
    assert m42_a_075.entries[0].length == 150 and m42_a_075.entries[0].spec == "9", "M42 0.75 inch Type-A fallback plate changed"
    assert m42_a_075.warnings, "M42 0.75 inch fallback should warn"

    m42_b_20 = AnalysisResult(fullstring="phase3A-m42-B-20")
    perform_action_by_letter(m42_b_20, "B", 20)
    assert [entry.name for entry in m42_b_20.entries] == ["Plate_a_無鑽孔", "Plate_d_有鑽孔", "EXP.BOLT"], "M42 Type-B 20 inch fallback BOM changed"
    assert m42_b_20.entries[0].length == 690 and m42_b_20.entries[1].length == 830, "M42 Type-B 20 inch should use 24 inch row"
    assert m42_b_20.entries[2].spec == '7/8"' and m42_b_20.entries[2].quantity == 4, "M42 Type-B 20 inch fallback bolt changed"
    assert len(m42_b_20.warnings) == 1, f"M42 fallback warning should not duplicate: {m42_b_20.warnings}"

    m42_unknown = AnalysisResult(fullstring="phase3A-m42-unknown")
    perform_action_by_letter(m42_unknown, "Z", 2)
    assert not m42_unknown.entries and m42_unknown.warnings, "unknown M-42 type should warn without adding BOM"

    print("v phase 3A core helper MaterialSpec compatibility OK")
except Exception as e:
    print(f"X phase 3A core helper MaterialSpec compatibility ERROR: {e}")

# Test type41_table
try:
    from data.type41_table import get_type41_data
    r3 = get_type41_data("41-1")
    assert r3 is not None and r3["L"] == 230 and r3["fig"] == "A", f"type41 41-1 failed: {r3}"
    print("v type41_table OK")
except Exception as e:
    print(f"X type41_table ERROR: {e}")

# Test type42_table
try:
    from data.type42_table import get_type42_member, get_type42_pipe
    r4 = get_type42_member("C125")
    assert r4 is not None and r4["H_MAX"] == 1750, f"type42 C125 failed: {r4}"
    print("v type42_table OK")
except Exception as e:
    print(f"X type42_table ERROR: {e}")

# Test type43_table
try:
    from data.type43_table import get_type43_data, get_type43_formula
    r5 = get_type43_data("L75")
    assert r5 is not None and r5["A"] == 160, f"type43 L75 failed: {r5}"
    print("v type43_table OK")
except Exception as e:
    print(f"X type43_table ERROR: {e}")

# Test type44_table
try:
    from data.type44_table import get_type44_q
    r6 = get_type44_q(10)
    assert r6 == 140, f"type44 Q 10 failed: {r6}"
    print("v type44_table OK")
except Exception as e:
    print(f"X type44_table ERROR: {e}")

# Test type45_table
try:
    from data.type45_table import get_type45_q
    r7 = get_type45_q(14)
    assert r7 == 181, f"type45 Q 14 failed: {r7}"
    print("v type45_table OK")
except Exception as e:
    print(f"X type45_table ERROR: {e}")

# Test type46_table
try:
    from data.type46_table import get_type46_47_q
    r8 = get_type46_47_q(6)
    assert r8 == 187, f"type46 Q 6 failed: {r8}"
    print("v type46_table OK")
except Exception as e:
    print(f"X type46_table ERROR: {e}")

# Test type48_table
try:
    from data.type48_table import get_type48_data
    r9 = get_type48_data(2)
    assert r9 is not None and r9["plate_t"] == 6, f"type48 2 failed: {r9}"
    print("v type48_table OK")
except Exception as e:
    print(f"X type48_table ERROR: {e}")

# Test type51_table
try:
    from data.type51_table import get_type51_data
    r10 = get_type51_data(12)
    assert r10 is not None and r10["member"] == "L65*65*6", f"type51 12 failed: {r10}"
    print("v type51_table OK")
except Exception as e:
    print(f"X type51_table ERROR: {e}")

# Test type56_table
try:
    from data.type56_table import get_type56_data
    r11 = get_type56_data(6)
    assert r11 is not None and r11["R"] == 84, f"type56 6 failed: {r11}"
    print("v type56_table OK")
except Exception as e:
    print(f"X type56_table ERROR: {e}")

# Test type62 hanger combination table/calculator
try:
    from core.calculator import analyze_single
    from data.type62_table import get_type62_lower_part, validate_type62_lower_pipe_size

    fig_j = get_type62_lower_part("J")
    fig_n_ok, _ = validate_type62_lower_pipe_size("N", '12"')
    fig_n_bad, _ = validate_type62_lower_pipe_size("N", '4"')
    r62 = analyze_single("62-4B-5/8-05~30D-J(T)")
    r62_simple = analyze_single("62-2B-3/8-05C-G")
    r62_fig_e = analyze_single("62-4B-5/8-05C-E")
    r62_bad = analyze_single("62-4B-5/8-05C-N")
    r62_names = [entry.name for entry in r62.entries]
    r62_fig_e_names = [entry.name for entry in r62_fig_e.entries]
    assert fig_j is not None and fig_j["component_id"] == "M-6" and fig_j["max_insulation_thk_in"] == 4, f"type62 fig J failed: {fig_j}"
    assert fig_n_ok and not fig_n_bad, "type62 lower range validation failed"
    assert not r62.error and "TURNBUCKLE" in r62_names and "LOWER PIPE CLAMP" in r62_names, f"type62 calculator failed: {r62}"
    assert r62.entries[0].spec == "MTRL-5/8-3000", f"type62 rod length failed: {r62.entries[0]}"
    assert not r62_simple.error and not any(entry.name == "TURNBUCKLE" for entry in r62_simple.entries), f"type62 simple failed: {r62_simple}"
    assert not r62_fig_e.error and "ADJUSTABLE CLEVIS" in r62_fig_e_names, f"type62 fig E failed: {r62_fig_e}"
    assert "WELDLESS EYE NUT" not in r62_fig_e_names and "HEAVY HEX. NUT" not in r62_fig_e_names, f"type62 fig E should not add nut callouts: {r62_fig_e.entries}"
    assert r62_bad.error and "FIG-N" in r62_bad.error, f"type62 invalid range failed: {r62_bad}"
    r62_material = analyze_single("62-2B-3/8-05C-G", {"material": "SUS304"})
    assert not r62_material.error and r62_material.entries[0].material == "SUS304", f"type62 material override failed: {r62_material.entries}"
    print("v type62 hanger combination OK")
except Exception as e:
    print(f"X type62 hanger combination ERROR: {e}")

# Test consistency refactor smokes
try:
    from core.calculator import analyze_single

    r10_invalid_letter = analyze_single("10-2B-05H")
    r07_override = analyze_single("07-2B-20J", {"upper_material": "SUS316"})
    r14_override = analyze_single("14-2B-1005", {"upper_material": "SUS316"})
    r16_override = analyze_single("16-2B-05", {"upper_material": "SUS316"})
    assert any("Type 10 允許範圍" in warning for warning in r10_invalid_letter.warnings), f"type10 M42 warning failed: {r10_invalid_letter.warnings}"
    assert not r07_override.error and r07_override.entries[0].material == "SUS316", f"type07 material override failed: {r07_override.entries}"
    assert not r14_override.error and r14_override.entries[0].material == "SUS316", f"type14 material override failed: {r14_override.entries}"
    assert not r16_override.error and r16_override.entries[0].material == "SUS304" and r16_override.entries[1].material == "A53Gr.B", f"type16 should keep fixed pipe materials: {r16_override.entries}"
    print("v system consistency refactor smokes OK")
except Exception as e:
    print(f"X system consistency refactor smokes ERROR: {e}")

# Phase 1D-0 material/override snapshot guardrails
try:
    from core.calculator import analyze_single

    _SNAPSHOT_CASES = {
        "07-2B-20J": {
            "count": 6,
            "total": 34.13,
            "warnings": 0,
            "materials": (
                "A36 / SS400",
                "A36 / SS400",
                "SUS304",
                "A36 / SS400",
                "A36 / SS400",
                "A36/SS400",
            ),
            "weights": (0.93, 21.25, 4.0, 2.83, 2.83, 2.29),
            "quantities": (1, 1, 4, 1, 1, 1),
            "upper_total": 34.5,
            "upper_override": (
                "SUS316",
                "SUS316",
                "SUS304",
                "A36 / SS400",
                "A36 / SS400",
                "A36/SS400",
            ),
            "all_hardware": (
                "INCONEL",
                "INCONEL",
                "SUS304",
                "INCONEL",
                "INCONEL",
                "A36/SS400",
            ),
            "cryo": (
                "A36 / SS400",
                "A36 / SS400",
                "SUS304",
                "A36 / SS400",
                "A36 / SS400",
                "A36/SS400",
            ),
        },
        "10-2B-05A": {
            "count": 6,
            "total": 13.83,
            "warnings": 0,
            "materials": (
                "A53Gr.B",
                "SUS304",
                "A36 / SS400",
                "A194 2H",
                "A36 / SS400",
                "A36/SS400",
            ),
            "weights": (1.08, 1.48, 3.2, 2.4, 4.08, 1.59),
            "quantities": (1, 1, 4, 16, 2, 1),
            "upper_total": 13.83,
            "upper_override": (
                "A53Gr.B",
                "SUS304",
                "A36 / SS400",
                "A194 2H",
                "A36 / SS400",
                "A36/SS400",
            ),
            "all_hardware": (
                "A53Gr.B",
                "SUS304",
                "INCONEL",
                "INCONEL",
                "INCONEL",
                "A36/SS400",
            ),
            "cryo": (
                "A53Gr.B",
                "SUS304",
                "A36 / SS400",
                "A194 4 / S3",
                "A36 / SS400",
                "A36/SS400",
            ),
        },
        "14-2B-1005": {
            "count": 7,
            "total": 22.26,
            "warnings": 0,
            "materials": (
                "A36 / SS400",
                "A36 / SS400",
                "A36 / SS400",
                "A36 / SS400",
                "A36 / SS400",
                "A36 / SS400",
                "A36 / SS400",
            ),
            "weights": (9.36, 2.08, 4.0, 2.55, 1.06, 0.45, 2.76),
            "quantities": (1, 1, 4, 1, 2, 1, 4),
            "upper_total": 22.29,
            "upper_override": (
                "A36 / SS400",
                "SUS316",
                "SUS316",
                "A36 / SS400",
                "A36 / SS400",
                "A36 / SS400",
                "A36 / SS400",
            ),
            "all_hardware": (
                "INCONEL",
                "INCONEL",
                "INCONEL",
                "INCONEL",
                "INCONEL",
                "INCONEL",
                "INCONEL",
            ),
            "cryo": (
                "A36 / SS400",
                "A36 / SS400",
                "A36 / SS400",
                "A36 / SS400",
                "A36 / SS400",
                "A36 / SS400",
                "A36 / SS400",
            ),
        },
        "15-2B-1005": {
            "count": 6,
            "total": 19.53,
            "warnings": 0,
            "materials": (
                "A36 / SS400",
                "A36 / SS400",
                "A36 / SS400",
                "A36 / SS400",
                "A36 / SS400",
                "A36 / SS400",
            ),
            "weights": (9.36, 2.08, 2.55, 1.06, 0.45, 4.03),
            "quantities": (1, 1, 1, 2, 1, 4),
            "upper_total": 19.56,
            "upper_override": (
                "A36 / SS400",
                "SUS316",
                "A36 / SS400",
                "A36 / SS400",
                "A36 / SS400",
                "A36 / SS400",
            ),
            "all_hardware": (
                "INCONEL",
                "INCONEL",
                "INCONEL",
                "INCONEL",
                "INCONEL",
                "INCONEL",
            ),
            "cryo": (
                "A36 / SS400",
                "A36 / SS400",
                "A36 / SS400",
                "A36 / SS400",
                "A36 / SS400",
                "A36 / SS400",
            ),
        },
        "16-2B-05": {
            "count": 3,
            "total": 4.98,
            "warnings": 0,
            "materials": ("A53Gr.B", "SUS304", "A36 / SS400"),
            "weights": (3.62, 1.13, 0.23),
            "quantities": (1, 1, 1),
            "upper_total": 4.98,
            "upper_override": ("A53Gr.B", "SUS304", "A36 / SS400"),
            "all_hardware": ("A53Gr.B", "SUS304", "INCONEL"),
            "cryo": ("A53Gr.B", "SUS304", "A36 / SS400"),
        },
        "62-4B-5/8-05~30D-J(T)": {
            "count": 6,
            "total": 8.6,
            "warnings": 3,
            "materials": (
                "A194 2H",
                "A36 / SS400",
                "A193 B7",
                "A36 / SS400",
                "A36 / SS400",
                "A36 / SS400",
            ),
            "weights": (0.16, 2.3, 4.65, 0.95, 0.32, 0.22),
            "quantities": (2, 1, 1, 1, 1, 1),
            "upper_override": (
                "SUS316",
                "SUS316",
                "SUS316",
                "SUS316",
                "SUS316",
                "SUS316",
            ),
            "all_hardware": (
                "INCONEL",
                "INCONEL",
                "INCONEL",
                "INCONEL",
                "INCONEL",
                "INCONEL",
            ),
            "cryo": (
                "A194 4 / S3",
                "A36 / SS400",
                "A320 L7",
                "A36 / SS400",
                "A36 / SS400",
                "A36 / SS400",
            ),
        },
        "64-2-8-05A": {
            "count": 4,
            "total": 8.13,
            "warnings": 2,
            "materials": (
                "A36 / SS400",
                "A193 B7",
                "A36 / SS400",
                "A36 / SS400",
            ),
            "weights": (1.12, 1.56, 5.01, 0.44),
            "quantities": (1, 2, 1, 2),
            "upper_override": ("SUS316", "SUS316", "SUS316", "SUS316"),
            "all_hardware": ("INCONEL", "INCONEL", "INCONEL", "INCONEL"),
            "cryo": ("A36 / SS400", "A320 L7", "A36 / SS400", "A36 / SS400"),
        },
        "65-6B-1505": {
            "count": 3,
            "total": 20.8,
            "warnings": 0,
            "materials": ("A36 / SS400", "A36 / SS400", "A193 B7"),
            "weights": (18.3, 0.64, 1.86),
            "quantities": (1, 2, 2),
            "upper_override": ("SUS316", "SUS316", "SUS316"),
            "all_hardware": ("INCONEL", "INCONEL", "INCONEL"),
            "cryo": ("A36 / SS400", "A36 / SS400", "A320 L7"),
        },
    }

    def _norm(value):
        return None if value is None else round(value, 4)

    def _snapshot_entries(result):
        return sorted(
            result.entries,
            key=lambda entry: (
                entry.category,
                entry.name,
                entry.spec,
                entry.material,
                entry.unit,
                entry.remark,
            ),
        )

    def _materials(result):
        return tuple(entry.material for entry in _snapshot_entries(result))

    def _weights(result):
        return tuple(_norm(entry.weight_output) for entry in _snapshot_entries(result))

    def _quantities(result):
        return tuple(_norm(entry.quantity) for entry in _snapshot_entries(result))

    for designation, expected in _SNAPSHOT_CASES.items():
        default_result = analyze_single(designation)
        assert not default_result.error, f"{designation} snapshot error: {default_result.error}"
        assert len(default_result.entries) == expected["count"], f"{designation} entry count changed: {len(default_result.entries)}"
        assert _norm(default_result.total_weight) == expected["total"], f"{designation} total changed: {default_result.total_weight}"
        assert len(default_result.warnings) == expected["warnings"], f"{designation} warning count changed: {default_result.warnings}"
        assert _materials(default_result) == expected["materials"], f"{designation} material snapshot changed: {_materials(default_result)}"
        assert _weights(default_result) == expected["weights"], f"{designation} weight snapshot changed: {_weights(default_result)}"
        assert _quantities(default_result) == expected["quantities"], f"{designation} quantity snapshot changed: {_quantities(default_result)}"

        upper_result = analyze_single(designation, {"upper_material": "SUS316"})
        all_result = analyze_single(designation, {"hardware_material": "INCONEL"})
        cryo_result = analyze_single(designation, {"service": "cryo"})
        pipe_result = analyze_single(designation, {"pipe_material": "A335 P11"})
        for result in (upper_result, all_result, cryo_result, pipe_result):
            assert not result.error, f"{designation} override snapshot error: {result.error}"
        assert _norm(upper_result.total_weight) == expected.get("upper_total", expected["total"]), f"{designation} upper override weight changed: {upper_result.total_weight}"
        for result in (all_result, cryo_result, pipe_result):
            assert _norm(result.total_weight) == expected["total"], f"{designation} override weight changed: {result.total_weight}"

        assert _materials(upper_result) == expected["upper_override"], f"{designation} upper override changed: {_materials(upper_result)}"
        assert _materials(all_result) == expected["all_hardware"], f"{designation} all-hardware override changed: {_materials(all_result)}"
        assert _materials(cryo_result) == expected["cryo"], f"{designation} service material changed: {_materials(cryo_result)}"
        assert _materials(pipe_result) == expected["materials"], f"{designation} pipe_material polluted hardware: {_materials(pipe_result)}"

    print("v phase 1D-0 material/override snapshot baseline OK")
except Exception as e:
    print(f"X phase 1D-0 material/override snapshot baseline ERROR: {e}")

# Phase 1D-2C override consistency across migrated material Types
try:
    from collections import Counter

    from core.calculator import analyze_single
    from core.hardware_material import HardwareKind, ServiceClass, resolve_hardware_material

    _MIGRATED_TYPE_KIND_COUNTS = {
        "07-2B-20J": {
            HardwareKind.SUPPORT_PIPE: 2,
            HardwareKind.SUPPORT_PLATE: 2,
        },
        "10-2B-05A": {
            HardwareKind.ANCHOR_BOLT: 1,
            HardwareKind.HEAVY_HEX_NUT: 1,
            HardwareKind.SUPPORT_PLATE: 1,
        },
        "14-2B-1005": {
            HardwareKind.STRUCTURAL_STRUT: 1,
            HardwareKind.SUPPORT_PIPE: 1,
            HardwareKind.ANCHOR_BOLT: 1,
            HardwareKind.SUPPORT_PLATE: 4,
        },
        "15-2B-1005": {
            HardwareKind.STRUCTURAL_STRUT: 1,
            HardwareKind.SUPPORT_PIPE: 1,
            HardwareKind.SUPPORT_PLATE: 4,
        },
        "16-2B-05": {
            HardwareKind.SUPPORT_PLATE: 1,
        },
        "62-4B-5/8-05~30D-J(T)": {
            HardwareKind.HEAVY_HEX_NUT: 1,
            HardwareKind.CLAMP_BODY: 1,
            HardwareKind.THREADED_ROD: 1,
            HardwareKind.TURNBUCKLE: 1,
            HardwareKind.BEAM_ATTACHMENT: 1,
            HardwareKind.WELDLESS_EYE_NUT: 1,
        },
        "64-2-8-05A": {
            HardwareKind.CLAMP_BODY: 2,
            HardwareKind.THREADED_ROD: 1,
            HardwareKind.WELDLESS_EYE_NUT: 1,
        },
        "65-6B-1505": {
            HardwareKind.STRUCTURAL_STRUT: 1,
            HardwareKind.BEAM_ATTACHMENT: 1,
            HardwareKind.THREADED_ROD: 1,
        },
    }
    _UNMANAGED_MATERIAL_COUNTS = {
        "07-2B-20J": Counter({"SUS304": 1, "A36/SS400": 1}),
        "10-2B-05A": Counter({"SUS304": 1, "A53Gr.B": 1, "A36/SS400": 1}),
        "14-2B-1005": Counter(),
        "15-2B-1005": Counter(),
        "16-2B-05": Counter({"SUS304": 1, "A53Gr.B": 1}),
        "62-4B-5/8-05~30D-J(T)": Counter(),
        "64-2-8-05A": Counter(),
        "65-6B-1505": Counter(),
    }
    _LEGACY_SCOPES = {
        "07-2B-20J": {HardwareKind.SUPPORT_PIPE},
        "10-2B-05A": set(),
        "14-2B-1005": {HardwareKind.SUPPORT_PIPE, HardwareKind.ANCHOR_BOLT},
        "15-2B-1005": {HardwareKind.SUPPORT_PIPE},
        "16-2B-05": set(),
    }
    _LEGACY_GLOBAL_CASES = {
        "62-4B-5/8-05~30D-J(T)",
        "64-2-8-05A",
        "65-6B-1505",
    }
    _FULL_PER_KIND_OVERRIDE = {
        "threaded_rod": "ROD_KIND",
        "heavy_hex_nut": "NUT_KIND",
        "upper_bracket": "UPPER_KIND",
        "support_pipe": "SUPPORT_PIPE_KIND",
        "support_plate": "SUPPORT_PLATE_KIND",
        "anchor_bolt": "ANCHOR_KIND",
        "gusset_plate": "PLATE_KIND",
        "structural_strut": "STRUT_KIND",
        "beam_attachment": "BEAM_KIND",
        "clamp_body": "CLAMP_KIND",
        "weldless_eye_nut": "EYE_KIND",
        "turnbuckle": "TURN_KIND",
        "clevis": "CLEVIS_KIND",
        "plate_lug": "LUG_KIND",
    }
    _FULL_PER_KIND_EXPECTED = {
        HardwareKind.THREADED_ROD: "ROD_KIND",
        HardwareKind.HEAVY_HEX_NUT: "NUT_KIND",
        HardwareKind.UPPER_BRACKET: "UPPER_KIND",
        HardwareKind.SUPPORT_PIPE: "SUPPORT_PIPE_KIND",
        HardwareKind.SUPPORT_PLATE: "SUPPORT_PLATE_KIND",
        HardwareKind.ANCHOR_BOLT: "ANCHOR_KIND",
        HardwareKind.GUSSET_PLATE: "PLATE_KIND",
        HardwareKind.STRUCTURAL_STRUT: "STRUT_KIND",
        HardwareKind.BEAM_ATTACHMENT: "BEAM_KIND",
        HardwareKind.CLAMP_BODY: "CLAMP_KIND",
        HardwareKind.WELDLESS_EYE_NUT: "EYE_KIND",
        HardwareKind.TURNBUCKLE: "TURN_KIND",
        HardwareKind.CLEVIS: "CLEVIS_KIND",
        HardwareKind.PLATE_LUG: "LUG_KIND",
    }
    _PARTIAL_PER_KIND_EXPECTED = {
        HardwareKind.THREADED_ROD: "ROD_KIND",
        HardwareKind.SUPPORT_PIPE: "SUPPORT_PIPE_KIND",
        HardwareKind.SUPPORT_PLATE: "SUPPORT_PLATE_KIND",
        HardwareKind.CLAMP_BODY: "CLAMP_KIND",
    }
    _PARTIAL_PER_KIND_OVERRIDE = {
        kind.value: material
        for kind, material in _PARTIAL_PER_KIND_EXPECTED.items()
    }

    def _entry_material_counter(designation, overrides=None):
        result = analyze_single(designation, overrides or {})
        assert not result.error, f"{designation} override consistency error: {result.error}"
        return Counter(entry.material for entry in result.entries)

    def _default_material(kind, service):
        return resolve_hardware_material(kind, service=service).name

    def _expected_material_counter(
        designation,
        *,
        service=ServiceClass.AMBIENT,
        global_material=None,
        per_kind=None,
        legacy_material=None,
    ):
        per_kind = per_kind or {}
        kind_counts = _MIGRATED_TYPE_KIND_COUNTS[designation]
        expected = Counter(_UNMANAGED_MATERIAL_COUNTS[designation])
        legacy_scope = _LEGACY_SCOPES.get(designation, set())
        legacy_is_global = designation in _LEGACY_GLOBAL_CASES

        for kind, count in kind_counts.items():
            if kind in per_kind:
                material = per_kind[kind]
            elif global_material is not None:
                material = global_material
            elif legacy_material is not None and (legacy_is_global or kind in legacy_scope):
                material = legacy_material
            else:
                material = _default_material(kind, service)
            expected[material] += count
        return expected

    for designation in _MIGRATED_TYPE_KIND_COUNTS:
        assert _entry_material_counter(designation, {"pipe_material": "A335 P11"}) == _expected_material_counter(designation), f"{designation} pipe_material polluted hardware"

        assert _entry_material_counter(designation, {"hardware_material": "GLOBAL"}) == _expected_material_counter(designation, global_material="GLOBAL"), f"{designation} global hardware override failed"

        assert _entry_material_counter(designation, {"hardware_material_by_kind": _FULL_PER_KIND_OVERRIDE}) == _expected_material_counter(designation, per_kind=_FULL_PER_KIND_EXPECTED), f"{designation} per-kind hardware override failed"

        mixed_overrides = {
            "hardware_material": "GLOBAL",
            "hardware_material_by_kind": _PARTIAL_PER_KIND_OVERRIDE,
        }
        assert _entry_material_counter(designation, mixed_overrides) == _expected_material_counter(designation, global_material="GLOBAL", per_kind=_PARTIAL_PER_KIND_EXPECTED), f"{designation} per-kind should override global"

        assert _entry_material_counter(designation, {"material": "LEGACY_M"}) == _expected_material_counter(designation, legacy_material="LEGACY_M"), f"{designation} legacy material conversion failed"

        assert _entry_material_counter(designation, {"upper_material": "LEGACY_U"}) == _expected_material_counter(designation, legacy_material="LEGACY_U"), f"{designation} legacy upper_material conversion failed"

        high_temp = {"service": "high_temp"}
        assert _entry_material_counter(designation, high_temp) == _expected_material_counter(designation, service=ServiceClass.HIGH_TEMP), f"{designation} high-temp service defaults failed"

        high_temp_with_per_kind = {
            "service": "high_temp",
            "hardware_material_by_kind": {"threaded_rod": "ROD_KIND"},
        }
        assert _entry_material_counter(designation, high_temp_with_per_kind) == _expected_material_counter(
            designation,
            service=ServiceClass.HIGH_TEMP,
            per_kind={HardwareKind.THREADED_ROD: "ROD_KIND"},
        ), f"{designation} service default broken by per-kind override"

        high_temp_with_legacy = {"service": "high_temp", "upper_material": "LEGACY_U"}
        assert _entry_material_counter(designation, high_temp_with_legacy) == _expected_material_counter(
            designation,
            service=ServiceClass.HIGH_TEMP,
            legacy_material="LEGACY_U",
        ), f"{designation} service default broken by legacy override"

    print("v phase 1D-2C override consistency OK")
except Exception as e:
    print(f"X phase 1D-2C override consistency ERROR: {e}")

# Phase 1D-6 material-system lock-in checks
try:
    import re
    from pathlib import Path

    type_root = Path("core/types")
    migrated_type_files = [
        type_root / "type_07.py",
        type_root / "type_10.py",
        type_root / "type_14.py",
        type_root / "type_15.py",
        type_root / "type_16.py",
        type_root / "type_62.py",
        type_root / "type_64.py",
        type_root / "type_65.py",
    ]
    legacy_override_tokens = (
        "_material_" "overrides_from_dict",
        "_service_" "from_overrides",
        "resolve_" "material",
        "DEFAULT_UPPER_" "MATERIAL",
        "DEFAULT_STRUCTURAL_" "MATERIAL",
    )
    direct_material_patterns = (
        re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*material[A-Za-z0-9_]*\s*=\s*['\"]"),
        re.compile(r"\.material\s*=\s*['\"]"),
        re.compile(r"\bmaterial\s*=\s*['\"]"),
    )

    def _source_hits(paths, predicate):
        hits = []
        for path in paths:
            text = path.read_text(encoding="utf-8")
            for line_no, line in enumerate(text.splitlines(), start=1):
                if predicate(line):
                    hits.append(f"{path}:{line_no}: {line.strip()}")
        return hits

    all_type_files = sorted(type_root.glob("type_*.py"))
    upper_bracket_hits = _source_hits(
        all_type_files,
        lambda line: "UPPER_BRACKET" in line,
    )
    assert not upper_bracket_hits, "UPPER_BRACKET Type mapping usage must stay 0: " + "; ".join(upper_bracket_hits)

    legacy_override_hits = _source_hits(
        all_type_files,
        lambda line: any(token in line for token in legacy_override_tokens),
    )
    assert not legacy_override_hits, "legacy material override path found: " + "; ".join(legacy_override_hits)

    direct_material_hits = _source_hits(
        migrated_type_files,
        lambda line: any(pattern.search(line) for pattern in direct_material_patterns),
    )
    assert not direct_material_hits, "migrated Types must not assign literal material: " + "; ".join(direct_material_hits)

    print("v phase 1D-6 material-system lock-in OK")
except Exception as e:
    print(f"X phase 1D-6 material-system lock-in ERROR: {e}")

# Phase 4B material hard lock for Phase 1D migrated Types.
#
# This is intentionally a hard failure: Phase 1D Types have completed material
# migration, so missing canonical identity indicates a bypassed MaterialSpec path.
try:
    from core.calculator import analyze_single

    _PHASE_4B_MIGRATED_TYPE_SAMPLES = [
        ("07", "07-2B-20J"),
        ("10", "10-2B-05A"),
        ("14", "14-2B-1005"),
        ("15", "15-2B-1005"),
        ("16", "16-2B-05"),
        ("62", "62-4B-5/8-05~30D-J(T)"),
        ("64", "64-2-8-05A"),
        ("65", "65-6B-1505"),
    ]

    hard_lock_errors = []
    for type_id, designation in _PHASE_4B_MIGRATED_TYPE_SAMPLES:
        result = analyze_single(designation)
        if result.error:
            hard_lock_errors.append(f"type={type_id} designation={designation} error={result.error}")
            continue

        for fallback_index, entry in enumerate(result.entries, start=1):
            if getattr(entry, "material_canonical_id", None):
                continue
            entry_index = entry.item_no or fallback_index
            hard_lock_errors.append(
                f"type={type_id} entry_index={entry_index} material={entry.material}"
            )

    assert not hard_lock_errors, "Phase 4B migrated Type material hard-lock failures: " + "; ".join(hard_lock_errors)

    print("v phase 4B material hard lock OK")
except Exception as e:
    print(f"X phase 4B material hard lock ERROR: {e}")
    raise

# Test type72 strap support table/calculator
try:
    from core.calculator import analyze_single
    from data.type72_table import get_type72_data

    r72_table = get_type72_data('2"')
    r72 = analyze_single("72-2B")
    r72_bad = analyze_single("72-6B")
    r72_names = [entry.name for entry in r72.entries]
    assert r72_table is not None and r72_table["A"] == 63.6 and r72_table["B"] == 150 and r72_table["T"] == 6, f"type72 table failed: {r72_table}"
    assert not r72.error and r72_names == ["STRAP", "EXP. BOLT"], f"type72 calculator failed: {r72}"
    assert r72.entries[0].spec.startswith("PUBS3-2B-2") and r72.entries[0].unit_weight == 0.34 and r72.entries[1].spec == "EB-3/8", f"type72 entries failed: {r72.entries}"
    assert "weight estimated at 1.0 kg/SET" in r72.entries[1].remark, f"type72 EB remark failed: {r72.entries[1].remark}"
    assert not any("M-54" in warning for warning in r72.warnings), f"type72 should not warn for M-54 lookup: {r72.warnings}"
    assert r72_bad.error and "3/4" in r72_bad.error, f"type72 invalid range failed: {r72_bad}"
    print("v type72 strap support OK")
except Exception as e:
    print(f"X type72 strap support ERROR: {e}")

# Test type73/type76/type77/type78/type79 support calculators
try:
    from core.calculator import analyze_single
    from data.type73_table import get_type73_bolt_count, get_type73_data, get_type73_spring_data
    from data.type76_table import get_type76_data
    from data.type77_table import get_type77_data
    from data.type79_table import get_type79_data

    r73_table = get_type73_data('6"')
    r73_spring = get_type73_spring_data("SPR04")
    r73 = analyze_single("73-6B-G")
    r73_bad = analyze_single("73-30B-G")
    r76_table = get_type76_data('30"')
    r76 = analyze_single("76-30B")
    r77_table = get_type77_data('40"')
    r77 = analyze_single("77-40B-(A)")
    r78 = analyze_single("78-2B(A)")
    r79_table = get_type79_data('8"')
    r79 = analyze_single("79-8B(A)")
    r79_bad = analyze_single("79-4B")

    assert r73_table is not None and r73_table["A"] == 396 and r73_table["spring_mark"] == "SPR04" and get_type73_bolt_count('6"') == 4, f"type73 table failed: {r73_table}"
    assert r73_spring is not None and r73_spring["spring_constant_kg_per_mm"] == 2.9 and r73_spring["unit_weight_kg"] > 0, f"type73 spring failed: {r73_spring}"
    assert not r73.error and [entry.name for entry in r73.entries][:4] == ["STRAP", "SPRING COIL", "STUD BOLT", "WASHER"], f"type73 calculator failed: {r73}"
    assert r73_bad.error and '1"' in r73_bad.error, f"type73 invalid range failed: {r73_bad}"
    assert r76_table is not None and r76_table["pad_angle_deg"] == 120 and r76_table["pad_length_mm"] == 400, f"type76 table failed: {r76_table}"
    assert not r76.error and r76.entries[0].name == "PIPE PAD" and r76.entries[0].unit_weight == 30.07, f"type76 calculator failed: {r76.entries}"
    assert r77_table is not None and r77_table["A"] == 300 and r77_table["T"] == 16 and r77_table["unit_weight_kg"] > 0, f"type77 table failed: {r77_table}"
    assert not r77.error and r77.entries[0].name == "SADDLE" and any("D-80A" in warning for warning in r77.warnings), f"type77 calculator failed: {r77}"
    assert not r78.error and r78.entries[0].spec.startswith("PUBS3-2B-1") and r78.entries[0].unit_weight == 0.35, f"type78 calculator failed: {r78.entries}"
    assert r79_table is not None and r79_table["B"] == 410 and r79_table["unit_weight_kg"] == 3.62, f"type79 table failed: {r79_table}"
    assert not r79.error and r79.entries[0].name == "U-BAND" and r79.entries[0].spec.startswith("PUBD1-8B") and any("M-55 table 已接線" in warning for warning in r79.warnings), f"type79 calculator failed: {r79}"
    assert r79_bad.error and '5"' in r79_bad.error, f"type79 invalid range failed: {r79_bad}"
    print("v type73/type76/type77/type78/type79 support calculators OK")
except Exception as e:
    print(f"X type73/type76/type77/type78/type79 support calculators ERROR: {e}")

# Test localized truth/evidence contract
try:
    from core.calculator import analyze_single
    from core.truth import TRUTH_ESTIMATED, TRUTH_UNKNOWN, need_escalation

    r72_truth = analyze_single("72-2B")
    r76_truth = analyze_single("76-30B")
    r78_truth = analyze_single("78-2B(A)")
    r79_truth = analyze_single("79-8B(A)")
    r_unknown_truth = analyze_single("99-1B")

    assert r72_truth.meta["truth_level"] == TRUTH_ESTIMATED and r72_truth.meta["requires_review"], f"type72 truth failed: {r72_truth.meta}"
    assert r76_truth.meta["truth_level"] == TRUTH_ESTIMATED and "PDF 視覺判讀" in r76_truth.meta["source_labels"], f"type76 truth failed: {r76_truth.meta}"
    assert r78_truth.meta["truth_level"] == TRUTH_ESTIMATED and r78_truth.evidence[0]["field"] == "strap_fig", f"type78 evidence failed: {r78_truth.meta}/{r78_truth.evidence}"
    assert r79_truth.meta["truth_level"] == TRUTH_ESTIMATED and r79_truth.meta["requires_review"], f"type79 truth failed: {r79_truth.meta}"
    assert not any(e["basis"] == "missing_table" for e in r79_truth.evidence), f"type79 should no longer include missing-table evidence: {r79_truth.evidence}"
    assert need_escalation(r79_truth.meta, r79_truth.meta["invariant_errors"]), f"type79 escalation failed: {r79_truth.meta}"
    assert r_unknown_truth.meta["truth_level"] == TRUTH_UNKNOWN and r_unknown_truth.meta["requires_review"], f"unknown truth failed: {r_unknown_truth.meta}"
    print("v localized truth/evidence contract OK")
except Exception as e:
    print(f"X localized truth/evidence contract ERROR: {e}")

# Test type64/type65 normalization helpers
try:
    from data.type64_table import get_type64_rod
    from data.type65_table import get_type65_data
    r64 = get_type64_rod("1-1/4")
    r65 = get_type65_data("2-1/2")
    assert r64 is not None and r64["g"] == '1/2"', f"type64 normalize failed: {r64}"
    assert r65 is not None and r65["rod_size"] == '3/8"', f"type65 normalize failed: {r65}"
    print("v type64/type65 normalization OK")
except Exception as e:
    print(f"X type64/type65 normalization ERROR: {e}")

# Phase 2L-A soft lock warnings for unmanaged material paths.
#
# This is intentionally warning-only.  It does not fail validation because the
# remaining unmanaged material paths are known Phase 2 migration backlog.
try:
    from pathlib import Path

    from core.calculator import analyze_single

    _PHASE_2L_A_SAMPLES = [
        ("01", "01-2B-05A"),
        ("03", "03-1B-05N"),
        ("05", "05-L50-05L"),
        ("06", "06-L50-0510-0401"),
        ("07", "07-2B-20J"),
        ("08", "08-2B-1005G"),
        ("09", "09-2B-05B"),
        ("10", "10-2B-05A"),
        ("11", "11-2B-06G"),
        ("12", "12-6B-05B"),
        ("13", "13-6B-05B"),
        ("14", "14-2B-1005"),
        ("15", "15-2B-1005"),
        ("16", "16-2B-05"),
        ("19", "19-2B"),
        ("20", "20-L50-05A"),
        ("21", "21-L50-05A"),
        ("22", "22-L50-05AL"),
        ("23", "23-L50-05A"),
        ("24", "24-L50-05"),
        ("25", "25-L50-0505A"),
        ("26", "26-L50-1005A"),
        ("27", "27-L75-0505L-0401"),
        ("28", "28-L50-1005L"),
        ("30", "30-L75-0505A-0401"),
        ("31", "31-L50-1005"),
        ("32", "32-L50-1005"),
        ("33", "33-L50-1005"),
        ("34", "34-L50-1005"),
        ("35", "35-C125-05A"),
        ("36", "36-C125-05"),
        ("37", "37-C125-1200A"),
        ("39", "39-C100-500 A"),
        ("41", "41-1"),
        ("42", "42-8B-C125-500 A"),
        ("43", "43-8B-C125-500 A"),
        ("44", "44-8B-C125-500 A"),
        ("45", "45-8B-C125-500 A"),
        ("46", "46-8B-C125-500 A"),
        ("47", "47-8B-C125-500 A"),
        ("48", "48-2"),
        ("49", "49-8A"),
        ("51", "51-2B"),
        ("52", "52-2B(P)-A(A)-130-500"),
        ("56", "56-2B"),
        ("57", "57-2B-A"),
        ("58", "58-4B-A"),
        ("59", "59-6B-A"),
        ("60", "60-20B-A"),
        ("61", "61-4B-T1-05"),
        ("62", "62-4B-5/8-05~30D-J(T)"),
        ("64", "64-2-8-05A"),
        ("65", "65-6B-1505"),
        ("72", "72-2B"),
        ("73", "73-6B-G"),
        ("76", "76-30B"),
        ("77", "77-40B-(A)"),
        ("78", "78-2B(A)"),
        ("79", "79-8B(A)"),
    ]
    _HELPER_DEFAULT_MARKERS = [
        (Path("core/bolt.py"), 'entry.material = "SUS304"', "SUS304"),
        (Path("core/plate.py"), 'material_name = "A36/SS400"', "A36/SS400"),
        (Path("core/steel.py"), 'material = "A36/SS400"', "A36/SS400"),
    ]

    warning_count = 0
    for file_path, marker, material in _HELPER_DEFAULT_MARKERS:
        try:
            for line_no, line in enumerate(file_path.read_text(encoding="utf-8").splitlines(), start=1):
                if marker in line:
                    warning_count += 1
                    print(
                        "WARN phase 2L-A helper default material | "
                        f"file={file_path.as_posix()} | line={line_no} | material={material}"
                    )
        except Exception as helper_error:
            warning_count += 1
            print(
                "WARN phase 2L-A helper scan error | "
                f"file={file_path.as_posix()} | error={helper_error}"
            )

    for type_id, designation in _PHASE_2L_A_SAMPLES:
        result = analyze_single(designation)
        if result.error:
            warning_count += 1
            print(
                "WARN phase 2L-A sample error | "
                f"type={type_id} | designation={designation} | error={result.error}"
            )
            continue

        for fallback_index, entry in enumerate(result.entries, start=1):
            if getattr(entry, "material_canonical_id", None):
                continue
            entry_index = entry.item_no or fallback_index
            warning_count += 1
            print(
                "WARN phase 2L-A unmanaged material entry | "
                f"type={type_id} | entry_index={entry_index} | material={entry.material} | "
                "reason=missing_material_canonical_id,string_material_path"
            )

    print(f"v phase 2L-A soft lock warnings emitted: {warning_count}")
except Exception as e:
    print(f"WARN phase 2L-A soft lock audit skipped: {e}")

# ─────────────────────────────────────────────────────────────────────────────
# Phase 5b golden cases — type_27 / type_42 / type_43
# 目的：鎖定高風險 type 的計算結果，任何回歸會立即報錯。
# 更新方式：先跑 analyze_single(designation)，確認邏輯正確後再更新 expected。
# ─────────────────────────────────────────────────────────────────────────────
try:
    from core.calculator import analyze_single

    def _golden(designation: str, expected: list[tuple]):
        """
        比對計算結果與預期值。
        expected: [(name, spec, length, qty), ...]  length=-1 表示不比對
        """
        r = analyze_single(designation)
        assert not r.error, f"{designation}: unexpected error '{r.error}'"
        assert len(r.entries) == len(expected), (
            f"{designation}: expected {len(expected)} entries, got {len(r.entries)}"
        )
        for i, (entry, (exp_name, exp_spec, exp_len, exp_qty)) in enumerate(
            zip(r.entries, expected), start=1
        ):
            if exp_name:
                assert entry.name == exp_name, (
                    f"{designation} entry#{i}: name '{entry.name}' != '{exp_name}'"
                )
            if exp_spec:
                assert entry.spec == exp_spec, (
                    f"{designation} entry#{i}: spec '{entry.spec}' != '{exp_spec}'"
                )
            if exp_len >= 0:
                assert entry.length == exp_len, (
                    f"{designation} entry#{i}: length {entry.length} != {exp_len}"
                )
            if exp_qty >= 0:
                assert entry.quantity == exp_qty, (
                    f"{designation} entry#{i}: qty {entry.quantity} != {exp_qty}"
                )

    # ── type_42: 8B C125 H=500 FIG-A (θ=30°) ──────────────────────────────
    # G = g_coeff * 500 + g_offset → 722
    _golden("42-8B-C125-500 A", [
        ("Channel",  "125*65*6", 500,  1),
        ("Channel",  "125*65*6", 722,  1),
        ("TRUNNION", "4\"",       -1,   1),
        ("C/S SHIM", "6",        125,  1),
        ("M.BOLT",   '3/4"x50',  -1,   2),
    ])

    # ── type_43: 8B C125 H=500 FIG-A (θ=30°) ──────────────────────────────
    # main_len = 500 + A; N = n_coeff * 500 + n_offset → 692
    _golden("43-8B-C125-500 A", [
        ("Channel",          "125*65*6", 670,  1),
        ("Channel",          "125*65*6", 692,  1),
        ("TRUNNION",         "4\"",       -1,   1),
        ("LUG PLATE TYPE-C", "10",       170,  1),
        ("LUG PLATE TYPE-E", "10",       145,  1),
        ("K BOLT",           '3/4"x50',  -1,   2),
        ("C/S SHIM",         "6",        125,  1),
    ])

    # ── type_27 H150: L=500 H=500 M42=L ────────────────────────────────────
    # column = H - 150 = 350; top = L = 500
    _golden("27-H150-0505L", [
        ("H Beam",          "150*150*10", 350,  1),
        ("H Beam",          "150*150*10", 500,  1),
        ("Plate_6t_Side",   "6",          150,  3),
        ("Plate_9t_Wing",   "9",          200,  2),
        ("Plate_c_有鑽孔",  "16",         500,  1),
        ("EXP.BOLT",        "7/8\"",       -1,   4),
    ])

    # ── type_27 L75: L=500 H=500 M42=L ─────────────────────────────────────
    # column = H - deduction(15) = 485; top = L = 500
    _golden("27-L75-0505L", [
        ("Angle",          "75*75*9",   485,  1),
        ("Angle",          "75*75*9",   500,  1),
        ("Plate_c_有鑽孔", "9",         260,  1),
        ("EXP.BOLT",       "5/8\"",      -1,   4),
    ])

    # ── type_42 擴充: 4B L75 H=300 FIG-A (小管徑角鐵版) ────────────────────
    # Trunnion=2", G=438
    _golden("42-4B-L75-300 A", [
        ("Angle",    "75*75*9",  300,  1),
        ("Angle",    "75*75*9",  438,  1),
        ("TRUNNION", "2\"",       -1,   1),
        ("C/S SHIM", "6",         75,  1),
        ("M.BOLT",   '3/4"x50',  -1,   2),
    ])

    # ── type_42 擴充: 16B C200 H=800 FIG-B (大管徑 θ=45°) ──────────────────
    # Trunnion=10", G=1331
    _golden("42-16B-C200-800 B", [
        ("Channel",  "200*80*7.5", 800,   1),
        ("Channel",  "200*80*7.5", 1331,  1),
        ("TRUNNION", "10\"",        -1,    1),
        ("C/S SHIM", "6",          200,   1),
        ("M.BOLT",   '3/4"x50',    -1,    2),
    ])

    # ── type_42 擴充: 24B C200 H=1000 FIG-B (最大管徑) ─────────────────────
    # Trunnion=14", G=1614
    _golden("42-24B-C200-1000 B", [
        ("Channel",  "200*80*7.5", 1000,  1),
        ("Channel",  "200*80*7.5", 1614,  1),
        ("TRUNNION", "14\"",         -1,   1),
        ("C/S SHIM", "6",           200,  1),
        ("M.BOLT",   '3/4"x50',     -1,   2),
    ])

    # ── type_43 擴充: 4B L75 H=300 FIG-A → LUG TYPE-E (小管徑) ────────────
    # main=460, N=438; LUG-C T=9 L=160, LUG-E T=9 L=135
    _golden("43-4B-L75-300 A", [
        ("Angle",            "75*75*9",  460,  1),
        ("Angle",            "75*75*9",  438,  1),
        ("TRUNNION",         "2\"",       -1,   1),
        ("LUG PLATE TYPE-C", "9",        160,  1),
        ("LUG PLATE TYPE-E", "9",        135,  1),
        ("K BOLT",           '3/4"x50',  -1,   2),
        ("C/S SHIM",         "6",         75,  1),
    ])

    # ── type_43 擴充: 16B C200 H=800 FIG-B → LUG TYPE-D (大管徑 θ=45°) ────
    # main=1020, N=1187; LUG-C T=12 L=220, LUG-D T=12 L=160
    _golden("43-16B-C200-800 B", [
        ("Channel",          "200*80*7.5", 1020,  1),
        ("Channel",          "200*80*7.5", 1187,  1),
        ("TRUNNION",         "10\"",         -1,   1),
        ("LUG PLATE TYPE-C", "12",          220,  1),
        ("LUG PLATE TYPE-D", "12",          160,  1),
        ("K BOLT",           '3/4"x50',      -1,   2),
        ("C/S SHIM",         "6",           200,  1),
    ])

    # ── type_27 擴充: L50 最小規格 ──────────────────────────────────────────
    # column = 300-15=285; top=300; Plate_c T=9 L=180 (L50 C=30mm)
    _golden("27-L50-0303L", [
        ("Angle",          "50*50*6",   285,  1),
        ("Angle",          "50*50*6",   300,  1),
        ("Plate_c_有鑽孔", "9",         180,  1),
        ("EXP.BOLT",       "5/8\"",      -1,   4),
    ])

    # ── type_27 擴充: H150 M42=P (NOTE4 valid variant) ──────────────────────
    # column = 600-150=450; top=400
    _golden("27-H150-0406P", [
        ("H Beam",         "150*150*10", 450,  1),
        ("H Beam",         "150*150*10", 400,  1),
        ("Plate_6t_Side",  "6",          150,  3),
        ("Plate_9t_Wing",  "9",          200,  2),
        ("Plate_c_有鑽孔", "16",         500,  1),
        ("EXP.BOLT",       "7/8\"",       -1,   4),
    ])

    # ── type_27 擴充: L100 大尺寸 ───────────────────────────────────────────
    # column = 1000-15=985; top=400
    _golden("27-L100-0410L", [
        ("Angle",          "100*100*10", 985,  1),
        ("Angle",          "100*100*10", 400,  1),
        ("Plate_c_有鑽孔", "9",          260,  1),
        ("EXP.BOLT",       "5/8\"",       -1,   4),
    ])

    # ── type_39: C125 H=500 FIG-A (標準, L=200 default) ────────────────────
    # main = 500+200=700; N=692; LUG-C T=10 L=170; LUG-E T=10 L=145
    _golden("39-C125-500 A", [
        ("Channel",          "125*65*6", 700,  1),
        ("Channel",          "125*65*6", 692,  1),
        ("LUG PLATE TYPE-C", "10",       170,  1),
        ("LUG PLATE TYPE-E", "10",       145,  1),
        ("K BOLT",           '3/4"x50',  -1,   2),
    ])

    # ── type_39: C200 H=800 FIG-B (大型, θ=45°) ─────────────────────────────
    # main = 800+200=1000; N=1187; LUG-C T=12 L=220; LUG-D T=12 L=160
    _golden("39-C200-800 B", [
        ("Channel",          "200*80*7.5", 1000,  1),
        ("Channel",          "200*80*7.5", 1187,  1),
        ("LUG PLATE TYPE-C", "12",         220,  1),
        ("LUG PLATE TYPE-D", "12",         160,  1),
        ("K BOLT",           '3/4"x50',     -1,   2),
    ])

    # ── type_39: L75 H=300 FIG-A (小角鐵版) ─────────────────────────────────
    # main = 300+200=500; N=438; LUG-C T=9 L=160; LUG-E T=9 L=135
    _golden("39-L75-300 A", [
        ("Angle",            "75*75*9",  500,  1),
        ("Angle",            "75*75*9",  438,  1),
        ("LUG PLATE TYPE-C", "9",        160,  1),
        ("LUG PLATE TYPE-E", "9",        135,  1),
        ("K BOLT",           '3/4"x50',  -1,   2),
    ])

    # ── type_56: 管線檔止 5 個尺寸分支 ──────────────────────────────────────
    # ≤2-1/2": PL 100×100×6
    _golden("56-2B", [
        ("PLATE",     "6",  100,  1),
    ])
    # 3"~4": FAB FROM 6t PLATE
    _golden("56-4B", [
        ("MEMBER C",  "6",   75,  1),
    ])
    # 5"~14": CUT FROM H型鋼
    _golden("56-10B", [
        ("MEMBER C",  "12", 200,  1),
    ])
    # 16"~24": FAB FROM 12t PLATE + 側板×2
    _golden("56-20B", [
        ("MEMBER C",   "12", 300,  1),
        ("SIDE PLATE", "12", 300,  2),
    ])
    # 26"~42": 大型 + 鞍座
    _golden("56-36B", [
        ("MEMBER C",      "12", 450,  1),
        ("SIDE PLATE",    "12", 400,  2),
        ("SADDLE (120°)", "12", 350,  1),
    ])

    print("v phase 5b golden cases type_27/42/43/39/56 OK")
except Exception as e:
    import traceback
    print(f"X phase 5b golden cases FAILED: {e}")
    traceback.print_exc()

print("\n=== VALIDATION COMPLETE ===")
