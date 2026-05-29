# Item Classification Audit

> Transient audit only. This file is a working snapshot for coordination and is
> not calculation truth, not architecture truth, and not a source of current
> runtime behavior. If this file conflicts with code, configs, tests, or the
> original drawing/PDF, trust those sources in that order.

Snapshot date: 2026-05-29

This audit inventories existing concepts related to:

- `primary_structure` / 主要結構體
- `fabricated_part` / 加工品
- `accessory` / 配件類

The repo is actively changing around `core/models`, helpers, exports, and tests.
Use this file as scratch coordination context only.

## Existing Concepts

### `AnalysisEntry.category`

`category` is the existing BOM/export-facing material attribute, shown as
`屬性` in UI/CSV/Excel/PDF paths. It is mostly a human/material bucket, not a
manufacturing or procurement semantic model.

Observed BOM categories:

| BOM category | Current meaning | Typical source |
| --- | --- | --- |
| `管路類` | pipe stock | `core/pipe.py` |
| `型鋼類` | section steel stock | `core/steel.py` |
| `鋼材類` | legacy alias for section steel in summary ordering | `core/material_summary.py` only |
| `鋼板類` | plate/plate-like BOM rows | `core/plate.py`, some direct/custom entries |
| `螺栓類` | bolts, nuts, washers, U-bolts, misc fasteners by default | `core/bolt.py`, direct type code |
| `管夾類` | clamp components | direct type code, e.g. Type 13 |
| `墊片類` | gasket components | direct type code, e.g. Type 13 |
| `彈簧類` | spring components | config/custom entries |

Important conflict: `category` also appears in `configs/type_catalog.json`,
component table metadata, and ontology files with values such as `support`,
`component`, `component_cold`, or `special`. Those are Type/catalog metadata,
not BOM item categories. Do not mix these meanings.

### `AnalysisEntry.role`

`role` is a component semantic role, intended to use `ComponentRole` values in
`core/component_roles.py`. `GeometryHints.role` mirrors this intent for geometry
consumers. Current coverage is partial:

- `add_plate_entry()` usually fills `entry.role` and `entry.geometry`.
- `add_steel_section_entry()` fills roles only for `Angle`, `Channel`, `H Beam`,
  and `I Beam`.
- `add_pipe_entry()` currently fills `category="管路類"` but not `role`.
- `add_bolt_entry()` and `add_custom_entry()` currently fill `category` but not
  `role`.
- Many direct/custom Type rows use `category` only; some plate-like components
  are therefore not role-classified.

Non-BOM role-like fields also exist:

- `configs/pipe_shoe_spec.json` uses role values such as `reinforcement_pad`,
  `angle`, `h_section`, and `stopper_plate`; these are intended to flow into BOM
  roles through the pipe shoe engine.
- `configs/type_62.json` has `role: upper/lower`; these are table selector
  roles, not `ComponentRole` values.
- `support_ontology.json` has family relation labels named `role`; these are UI
  ontology labels, not BOM roles.

### `ROLE_AGGREGATE_TYPE`

`ROLE_AGGREGATE_TYPE` maps `ComponentRole` to the material summary aggregate
axis:

| Aggregate type | Behavior in material summary | Current role examples |
| --- | --- | --- |
| `linear` | sum cut lengths, use stock lengths, purchase unit `根` | `pipe`, `column`, `top_beam`, `diagonal_brace`, `trunnion`, `angle`, `channel`, `h_section` |
| `plate` | group by plate dimensions/shape, count sheets/pieces, purchase unit `片` | `base_plate`, `lug_plate`, `shim_plate`, `cover_plate`, `wing_plate`, `stopper_plate`, `side_plate`, `top_plate`, `saddle_plate`, `reinforcement_pad`, `generic_plate`, currently also `flat_bar` |
| `piece` | count pieces/sets, purchase unit `組` | bolts, nuts, washer, U-bolt, gasket, PU block, clamp, unknown |

`core/material_summary.py` first classifies by `entry.role`; if the role is empty
or unknown, it falls back to legacy name/unit heuristics. This means role values
can override what `category` visually suggests.

### `item_class` / `manufacturing_type` WIP

Current dirty-tree snapshot already contains:

- `AnalysisEntry.item_class`
- `AnalysisEntry.manufacturing_type`
- `ItemClass`
- `ManufacturingType`
- `ROLE_ITEM_CLASS`
- `ROLE_MANUFACTURING_TYPE`
- `CATEGORY_ITEM_CLASS`
- `CATEGORY_MANUFACTURING_TYPE`
- `item_class_for()`
- `manufacturing_type_for()`

At this snapshot, `core/plate.py` populates these fields for plate entries.
Other helpers do not yet appear to populate them consistently. Treat these as
mainline WIP, not established truth until tests/export behavior settle.

## Main Files And Behavior

| File | Current behavior relevant to classification |
| --- | --- |
| `python_app/core/models.py` | Defines `AnalysisEntry.category`, `role`, `geometry`, `part_key`, `stock_id`, and current WIP `item_class` / `manufacturing_type`. |
| `python_app/core/component_roles.py` | Defines `ComponentRole`, `ROLE_AGGREGATE_TYPE`, display names, legacy name mapping, and current WIP item/manufacturing mappings. |
| `python_app/core/material_summary.py` | Computes `linear` / `plate` / `piece`; role wins over fallback name/category heuristics. Category is used for display/sort, not primary classification. |
| `python_app/core/plate.py` | `add_plate_entry()` sets `category="鋼板類"`, role, geometry, and current WIP item/manufacturing fields. `shape_kind` currently pushes manufacturing toward `shaped_plate`. |
| `python_app/core/steel.py` | `add_steel_section_entry()` sets `category="型鋼類"` and role for Angle/Channel/H/I, but not Flat/Round Bar and not current WIP item/manufacturing fields. |
| `python_app/core/pipe.py` | `add_pipe_entry()` sets `category="管路類"` but not role/item/manufacturing fields. |
| `python_app/core/bolt.py` | `add_bolt_entry()` sets `category="螺栓類"`. `add_custom_entry()` defaults to `螺栓類` and can be overridden, but does not assign role/item/manufacturing fields. |
| `python_app/core/pipe_shoe_engine.py` + `python_app/configs/pipe_shoe_spec.json` | Shared Type 52/53/54/55/66/67 path carries role-like config into plate/steel helper calls. |
| `python_app/core/types/type_56.py` | Important mixed manufacturing case: Type 56 switches between plate-fabricated members and cut H-section members. Current code includes a plate entry with `plate_role="channel"` for large sizes, which is risky for summary classification. |
| `python_app/core/types/type_59.py` | Good example of irregular lug plate: `shape_kind`, `shape_spec`, gross/cutout/net area, `part_key`, and `stock_id` are populated for the lug plate. |
| `python_app/core/types/type_62.py`, `type_73.py`, `type_76.py`, `type_77.py`, `type_78.py` | Examples of `add_custom_entry(category="鋼板類")` or direct estimated components. These may look like plates in category but not have plate geometry/role. |
| `python_app/core/project_aggregation.py` | Project aggregation key includes category and geometry/part/stock identifiers, but not role/item/manufacturing fields in this snapshot. |
| `python_app/export/*`, `python_app/ui/material_cutting_page.py`, `python_app/ui/main_window.py` | Existing user-visible output primarily exposes `category` / `屬性`. Material summary exposes aggregate behavior indirectly through length vs qty columns. |
| `python_app/validate_tables.py`, `python_app/tests/*` | Regression expectations assert categories and some roles. Some validation assumes `category="鋼板類"` implies positive plate dimensions/spec. |

## Initial Mapping Proposal

This is a working recommendation, not an implementation request.

### Role-first mapping

Prefer role when it is valid, because it is closer to machine semantics than
the display category.

| Role group | Suggested `item_class` | Suggested `manufacturing_type` | Material summary aggregate | Notes |
| --- | --- | --- | --- | --- |
| `pipe`, `column`, `top_beam`, `diagonal_brace`, `trunnion`, `angle`, `channel`, `h_section` | `primary_structure` | `raw_cut` | `linear` | Main load path / stock cut members. |
| `base_plate`, `lug_plate`, `shim_plate`, `cover_plate`, `wing_plate`, `stopper_plate`, `side_plate`, `top_plate`, `saddle_plate`, `reinforcement_pad`, `generic_plate` | `fabricated_part` | `plate_cut` | `plate` | Use `shaped_plate` when `shape_kind`, non-rectangular `shape_spec`, or net-area geometry is materially relevant. |
| `flat_bar` | `fabricated_part` or policy-specific `primary_structure` | `raw_cut` for bar stock, `plate_cut` if modeled through plate helper | currently `plate` | Ambiguous. Needs a policy decision because current aggregate/manufacturing semantics are not perfectly aligned. |
| `expansion_bolt`, `machine_bolt`, `k_bolt`, `nut`, `washer`, `u_bolt`, `gasket`, `pu_block`, `clamp` | `accessory` | `purchased` | `piece` | Purchased/standard or lookup components unless a specific Type proves fabrication. |
| `unknown` or invalid role | `unknown` | `unknown` | `piece` fallback | Keep visible for cleanup; do not silently coerce. |
| drawing reference / NOT FURNISHED item | `reference_only` | `not_furnished` | normally excluded from BOM | If represented at all, it should not affect procurement totals. |

### Category fallback mapping

Use category fallback only when role is blank/invalid.

| BOM category | Suggested `item_class` | Suggested `manufacturing_type` | Suggested aggregate |
| --- | --- | --- | --- |
| `管路類` | `primary_structure` | `raw_cut` | `linear` |
| `型鋼類` / `鋼材類` | `primary_structure` | `raw_cut` | `linear` |
| `鋼板類` | `fabricated_part` | `plate_cut` or `shaped_plate` when geometry proves it | `plate` only when dimensions/plate geometry exist; otherwise review |
| `螺栓類` | `accessory` | `purchased` | `piece` |
| `管夾類` | `accessory` | `purchased` | `piece` |
| `墊片類` | `accessory` | `purchased` | `piece` |
| `彈簧類` | `accessory` | `purchased` | `piece` |
| blank/other | `unknown` | `unknown` | `piece` |

## Risks

- `category` is overloaded across BOM rows and catalog/ontology metadata. Using
  catalog category as item class would corrupt semantics.
- Role coverage is incomplete. Pipe, bolt, and custom entries can still lack
  role, so role-only logic would drop or misclassify old calculators.
- `ROLE_AGGREGATE_TYPE` is an aggregation axis, not the same thing as
  `item_class` or `manufacturing_type`.
- Role has precedence in material summary. A plate row with a structural role
  such as `channel` can become `linear` even if `category="鋼板類"`.
- `add_custom_entry(category="鋼板類")` can create plate-looking entries without
  plate dimensions, role, or geometry. Category alone is not enough to treat the
  row as a plate summary row.
- `flat_bar` is currently semantically ambiguous: in some contexts it is a
  discrete fabricated part, but manufacturing may still be raw cut from bar
  stock.
- `shape_kind` currently drives `manufacturing_type_for()` to `shaped_plate`.
  That is useful for irregular plates, but should not be applied blindly to
  non-plate roles.
- Adding item/manufacturing fields into project or material summary grouping
  keys could split existing BOM totals unless carefully reviewed.
- Exports and UI mostly still show `category`; adding new fields to output is a
  product decision, not just a model change.
- Concurrent mainline changes can make this audit stale quickly.

## Do Not Do

- Do not edit runtime code from this audit.
- Do not revert dirty files in `core/`, helpers, tests, exports, configs, or UI.
- Do not treat this Markdown file as truth for BOM, dimensions, weights,
  material logic, or Type behavior.
- Do not replace `category` with `item_class`; they serve different users.
- Do not replace `ROLE_AGGREGATE_TYPE` with item/manufacturing mappings without
  preserving material summary behavior.
- Do not infer purchased/fabricated status from `name` strings alone when role,
  geometry, config data, or PDF evidence exists.
- Do not classify Type/catalog `category` values (`support`, `component`, etc.)
  as BOM item classes.
- Do not silently coerce unknown roles to fabricated/accessory; keep unknowns
  visible for cleanup.
