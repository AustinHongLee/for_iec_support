# Type Definition Contract

Purpose: this file tells future agents how to locate, extend, and refactor support Type definitions without losing the relationship between calculator code, JSON tables, bridge modules, documentation, drawings, and tests.

If this contract conflicts with executable code, inspect the code first, then update this file in the same change.

---

## One Type, Six Anchors

Every implemented support Type should be traceable through these anchors:

| Anchor | Path pattern | Responsibility |
|---|---|---|
| Dispatcher | `python_app/core/calculator.py` | Registers the Type code in `TYPE_HANDLERS`. |
| Calculator | `python_app/core/types/type_XX.py` | Parses designation and assembles BOM rows. Avoid hardcoded lookup tables when practical. |
| Config table | `python_app/configs/type_XX.json` | Data-first source for standard dimensions, sizing tables, component lists, and declarative rules. |
| Data bridge | `python_app/data/typeXX_table.py` | Compatibility layer for existing calculators. It may read JSON and expose old `get_typeXX_*` APIs. |
| Type doc | `python_app/docs/types/type_XX.md` | Human-readable drawing interpretation, designation format, assumptions, limits, and evidence. |
| Regression | `python_app/validate_tables.py` or `python_app/tests/` | Smoke/golden cases locking parser behavior, BOM structure, warnings, and critical values. |

Optional anchors:

| Anchor | Path pattern | Use when |
|---|---|---|
| Shared engine | `python_app/core/*_engine.py` | Multiple Types share the same sizing and BOM structure. Example: `pipe_shoe_engine.py`, `trunnion_engine.py`. |
| Catalog metadata | `python_app/configs/type_catalog.json` | UI/search/catalog metadata, not the source of calculation truth. |
| Source drawing | `python_app/assets/Type/*.pdf` | Original drawing evidence. Keep references in docs when interpretation matters. |

---

## Calculation Data Anchor Rule

Every Type registered in `TYPE_HANDLERS` must have one primary visible calculation data anchor:

| Anchor kind | Valid when | Example |
|---|---|---|
| Direct config | The Type has its own calculation JSON. | `configs/type_01.json` |
| Storage alias | A Type variant intentionally reuses another Type's calculator and config. | `01T` uses `type_01.py` and `configs/type_01.json` |
| Shared spec | Multiple Types intentionally share one declarative spec and shared engine. | `configs/pipe_shoe_spec.json` for 52/53/54/55/66/67/85 |
| Legacy data bridge | The only verified table still lives in `data/typeXX_table.py`. | Temporary migration state only |

`support_ontology.json` and `type_catalog.json` are metadata. They may describe grouping, names, UI search, tags, or selection logic, but they do not count as calculation data anchors.

Use `configs/type_anchor_index.json` as the human-readable map for non-obvious anchors. This index should list storage aliases and shared specs so searching for a Type id like `66` immediately reveals `configs/pipe_shoe_spec.json`.

Calculator-only constants are allowed only as temporary technical debt. If a supported Type stores limits, allowed members, material maps, dimensions, or component decisions only inside `core/types/type_XX.py`, the Type must appear in the calculator-only risk list from:

```powershell
python python_app/tools/audit_table_json_coverage.py
```

When adding or refactoring a Type, do not hide new standard data only in Python. Add a direct config, register a storage alias in `configs/type_anchor_index.json`, or register a shared spec in `configs/type_anchor_index.json` and document any new pattern here.

---

## Fast Locator Rules

Given a Type id `XX`, inspect in this order:

1. `python_app/core/calculator.py`
   - Find `TYPE_HANDLERS`.
   - Confirm whether `XX` dispatches directly to `core/types/type_XX.py` or to a shared dispatcher.

2. `python_app/core/types/type_XX.py`
   - This is the calculator entry unless `TYPE_HANDLERS` says otherwise.
   - If this file is tiny, it may dispatch into a shared engine.

3. `python_app/configs/type_XX.json`
   - If present, prefer this as table/config data.
   - Do not duplicate JSON table values back into the calculator.

4. `python_app/data/typeXX_table.py`
   - If present, this may be a JSON bridge or an old hardcoded table.
   - If it bridges JSON, preserve API compatibility unless intentionally migrating callers.

5. `python_app/docs/types/type_XX.md`
   - Read drawing assumptions before changing formulas or BOM order.

6. `python_app/validate_tables.py` and `python_app/tests/`
   - Add or update regression cases before broad refactors.

Useful command:

```powershell
rg -n "TYPE_HANDLERS|type_XX|typeXX|XX-" python_app/core python_app/data python_app/configs python_app/docs python_app/tests python_app/validate_tables.py
```

Replace `XX` with the two-digit Type id, for example `51`.

Preferred locator tool:

```powershell
python python_app/tools/find_type.py 51
python python_app/tools/find_type.py 66 --json
```

The tool reports the dispatcher handler, expected calculator path, actual calculator path, JSON config, shared spec when present, `TYPE_SPEC.engine` when present, data bridge, Type doc, drawing, catalog entry, test mentions, and whether the Type uses shared dispatch.

For shared or aliased Types, first check:

```powershell
rg -n '"66"|pipe_shoe' python_app/configs/type_anchor_index.json
```

To audit all implemented Type anchors at once:

```powershell
python python_app/tools/audit_table_json_coverage.py
```

Use the `Supported Type Calculation Anchors` section to find calculator-only Types. That list is the migration backlog for flattening risk.

---

## Source Of Truth Order

When values disagree, use this precedence:

1. Explicit original drawing evidence in `assets/Type/*.pdf` or a transcribed source note.
2. `configs/type_XX.json` if the Type is JSON-backed and verified.
3. Registered shared spec JSON when the Type intentionally uses shared dispatch.
4. `data/typeXX_table.py` if it is still the only implemented table.
5. `docs/types/type_XX.md` for interpretation, assumptions, and TODOs.
6. `type_catalog.json` and `support_ontology.json` only for metadata, never as calculation truth.

If a change is based on interpretation or estimation, record it in the Type doc and add a warning/evidence path in code when the existing model supports it.

---

## Calculator Responsibility

A Type calculator should mainly do orchestration:

- Parse designation parts.
- Select branch/figure.
- Look up dimensions from JSON/data bridge/component tables.
- Call shared builders: `pipe.py`, `plate.py`, `steel.py`, `bolt.py`, `m42.py`.
- Attach warnings and structured metadata when available.

A Type calculator should avoid:

- Large inline dimension tables.
- Repeated material resolver boilerplate.
- Parsing display remarks to recover geometry.
- Duplicating M/N component dimensions that already exist in component tables.

For material specs, prefer `python_app/core/material_specs.py` for fixed common materials. Use service-aware helpers only when the Type must respond to material overrides or operating context.

---

## JSON Bridge Contract

If a Type has `configs/type_XX.json` and still needs `data/typeXX_table.py`, the bridge should:

- Read JSON through `core/config_loader.py` where possible.
- Preserve existing function names used by calculators.
- Convert JSON string keys back to the expected lookup key type.
- Support int/float/string lookup when pipe sizes can be fractional.
- Avoid changing calculator behavior in the same patch unless covered by golden cases.

Known pitfall: JSON object keys are strings. If calculator lookup uses `float` from `get_lookup_value()`, bridge modules must normalize keys.

---

## Adding A New Type

Use this checklist:

1. Add `python_app/core/types/type_XX.py`.
2. Register it in `TYPE_HANDLERS` in `python_app/core/calculator.py`.
3. Put standard table data in `python_app/configs/type_XX.json` when the Type has tabular dimensions.
4. Add `python_app/data/typeXX_table.py` if a bridge API keeps the calculator smaller or preserves local patterns.
5. Add or update `python_app/docs/types/type_XX.md`.
6. Add catalog metadata in `python_app/configs/type_catalog.json` if the UI should expose it.
7. Add validation in `validate_tables.py` or a native pytest file under `python_app/tests/`.
8. Run:

```powershell
python validate_tables.py
pytest
```

If `python` is not on PATH in Codex, use the bundled Python path shown by `load_workspace_dependencies`.

---

## Refactoring Existing Flat Types

For a flat calculator with embedded tables:

1. Add golden cases first.
2. Extract table data into `configs/type_XX.json`.
3. Create/update `data/typeXX_table.py` as a bridge.
4. Keep the calculator behavior unchanged.
5. Run `validate_tables.py`.
6. Only then consider a shared engine or declarative spec.

Do not combine table migration, formula changes, material policy changes, and UI changes in one patch unless the user explicitly asks for a broad rewrite.

---

## Existing Pattern Examples

| Pattern | Example | Notes |
|---|---|---|
| JSON-backed single Type | `type_01.py` + `configs/type_01.json` | Calculator reads config table directly. |
| JSON bridge table | `data/type51_table.py` + `configs/type_51.json` | Bridge protects existing lookup API. |
| Shared declarative engine | `type_52.py` + `pipe_shoe_engine.py` + `pipe_shoe_spec.json` | One dispatcher covers 52/53/54/55/66/67/85. |
| Shared helper/constants | `trunnion_engine.py`, `material_specs.py` | Use for repeated behavior, not for unrelated Type coupling. |

---

## Required Agent Handoff Note

When an agent adds or changes Type structure, update this file if any of these change:

- Path conventions.
- Source-of-truth order.
- Required anchors.
- JSON bridge rules.
- New shared engine pattern.
- Validation entry point.

Also update `python_app/docs/AUDIT_2026-04-29.md` when the change completes or changes the next recommended session.
