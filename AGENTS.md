# AI Working Rules For This Repo

This repository has many Markdown files from audits, handoffs, planning, and old AI sessions. Treat Markdown as human context unless the file is explicitly listed below as authoritative.

## Calculation Truth Priority

When answering or changing BOM, dimensions, weights, material logic, or Type behavior, use this order:

1. Current user instruction in the active thread.
2. Original drawing/PDF when available.
3. Runtime behavior in `python_app/core/`, especially `core/types/type_XX.py`.
4. Table/config data in `python_app/configs/type_XX.json`, `python_app/data/*.py`, and shared specs.
5. Regression expectations in `python_app/tests/` and `python_app/validate_tables.py`.
6. `python_app/docs/types/type_XX.md` only as a UI-facing explanation and interpretation aid.
7. Catalog metadata such as `python_app/configs/type_catalog.json` only for UI/search/status labels.

If Markdown conflicts with code/config/tests/PDF, do not trust the Markdown. Inspect the implementation and mention the conflict.

## Markdown Authority

- `python_app/docs/types/*.md`: Type overview text for humans and the Type overview UI. It may be stale.
- `python_app/docs/TYPE_DEFINITION_CONTRACT.md`: architecture guidance, not per-Type calculation truth.
- `python_app/docs/COMPONENT_TABLE_STATUS.md`: component readiness summary. Confirm with `python_app/data/component_table_registry.py`.
- `python_app/docs/M42_BASE_SUPPORT_RULES.md`: human-confirmed M-42/M-43 interpretation notes.
- `python_app/docs/STEEL_PLATE_NAMING_PLAN.md`: design discussion/draft unless code and tests already implement the same rule.
- `python_app/coordination/*.md`: historical coordination, review, and handoff logs. Never treat these as current calculation truth.
- `*_REPORT.md`, `*_HANDOFF.md`, `WORKLOG.md`, `IN_PROGRESS.md`: historical snapshots only.

## Data Update Rule

When changing a Type's calculation data or interpretation, update the relevant `python_app/configs/type_XX.json` with:

- `data_updated_at`
- `data_update_note`

Update `python_app/docs/types/type_XX.md` only if the Type overview UI would otherwise show misleading text.

