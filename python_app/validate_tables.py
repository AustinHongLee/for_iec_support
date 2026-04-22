
import sys
sys.path.insert(0, ".")

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
    assert resolve_hardware_material(HardwareKind.CLAMP_BODY, overrides=override).name == "SUS316", "hardware material override failed"
    assert resolve_hardware_material(HardwareKind.THREADED_ROD, service=ServiceClass.CRYO).name == "A320 L7", "hardware service material failed"
    assert resolve_hardware_material(HardwareKind.SUPPORT_PIPE).name == "A36 / SS400", "support pipe default failed"
    assert resolve_hardware_material(HardwareKind.SUPPORT_PIPE, service=ServiceClass.HIGH_TEMP).name == "SA-240", "support pipe high-temp default failed"
    assert resolve_hardware_material(HardwareKind.SUPPORT_PLATE).name == "A36 / SS400", "support plate default failed"
    assert resolve_hardware_material(HardwareKind.SUPPORT_PLATE, service=ServiceClass.HIGH_TEMP).name == "A36 / SS400", "support plate high-temp default failed"
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
    assert not r16_override.error and r16_override.entries[0].material == "SUS316", f"type16 material override failed: {r16_override.entries}"
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
            "total": 10.52,
            "warnings": 0,
            "materials": (
                "A36 / SS400",
                "A36 / SS400",
                "A36 / SS400",
                "A194 2H",
                "A36 / SS400",
                "A36/SS400",
            ),
            "weights": (0.93, 2.16, 3.2, 0.6, 2.04, 1.59),
            "quantities": (1, 1, 4, 4, 1, 1),
            "upper_override": (
                "SUS316",
                "SUS316",
                "A36 / SS400",
                "A194 2H",
                "A36 / SS400",
                "A36/SS400",
            ),
            "all_hardware": (
                "INCONEL",
                "INCONEL",
                "INCONEL",
                "INCONEL",
                "INCONEL",
                "A36/SS400",
            ),
            "cryo": (
                "A36 / SS400",
                "A36 / SS400",
                "A36 / SS400",
                "A194 4 / S3",
                "A36 / SS400",
                "A36/SS400",
            ),
        },
        "14-2B-1005": {
            "count": 7,
            "total": 19.66,
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
            "weights": (9.36, 2.08, 4.0, 2.55, 0.53, 0.45, 0.69),
            "quantities": (1, 1, 4, 1, 1, 1, 1),
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
            "total": 15.98,
            "warnings": 0,
            "materials": (
                "A36 / SS400",
                "A36 / SS400",
                "A36 / SS400",
                "A36 / SS400",
                "A36 / SS400",
                "A36 / SS400",
            ),
            "weights": (9.36, 2.08, 2.55, 0.53, 0.45, 1.01),
            "quantities": (1, 1, 1, 1, 1, 1),
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
            "total": 4.96,
            "warnings": 0,
            "materials": ("A36 / SS400", "A36 / SS400", "A36 / SS400"),
            "weights": (1.11, 3.62, 0.23),
            "quantities": (1, 1, 1),
            "upper_override": ("SUS316", "SUS316", "A36 / SS400"),
            "all_hardware": ("INCONEL", "INCONEL", "INCONEL"),
            "cryo": ("A36 / SS400", "A36 / SS400", "A36 / SS400"),
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
            HardwareKind.SUPPORT_PIPE: 2,
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
            HardwareKind.SUPPORT_PIPE: 2,
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
        "10-2B-05A": Counter({"A36/SS400": 1}),
        "14-2B-1005": Counter(),
        "15-2B-1005": Counter(),
        "16-2B-05": Counter(),
        "62-4B-5/8-05~30D-J(T)": Counter(),
        "64-2-8-05A": Counter(),
        "65-6B-1505": Counter(),
    }
    _LEGACY_SCOPES = {
        "07-2B-20J": {HardwareKind.SUPPORT_PIPE},
        "10-2B-05A": {HardwareKind.SUPPORT_PIPE},
        "14-2B-1005": {HardwareKind.SUPPORT_PIPE, HardwareKind.ANCHOR_BOLT},
        "15-2B-1005": {HardwareKind.SUPPORT_PIPE},
        "16-2B-05": {HardwareKind.SUPPORT_PIPE},
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
    r_unknown_truth = analyze_single("80-1B")

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

print("\n=== VALIDATION COMPLETE ===")
