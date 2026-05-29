# Documentation Map

This folder contains a mix of current UI-facing explanations, design notes, and historical reports. Do not treat every Markdown file here as current engineering truth.

## Authority Levels

| Area | Status | How to Use |
|---|---|---|
| `../core/`, `../data/`, `../configs/type_XX.json`, `../tests/` | Authoritative for implemented behavior | Use first for BOM, weight, dimensions, and material logic |
| `types/type_XX.md` | UI-facing explanation | Useful for Type overview text, but verify against code/config/tests |
| `TYPE_DEFINITION_CONTRACT.md` | Architecture guidance | Use for structure and maintenance rules, not per-Type values |
| `COMPONENT_TABLE_STATUS.md` | Readiness summary | Confirm against `data/component_table_registry.py` before relying on it |
| `M42_BASE_SUPPORT_RULES.md` | Human-confirmed drawing notes | High value for M-42/M-43 interpretation |
| `STEEL_PLATE_NAMING_PLAN.md` | Draft/design discussion | Not authoritative until implemented in code/tests |
| `*_REPORT.md`, `*_HANDOFF.md`, audit files | Historical snapshot | Background only; can be stale |

## Rule Of Thumb

If a document says "建議", "handoff", "Claude", "Codex", "待", "估算", or "first version", treat it as context rather than a current rule.

For current Type data, prefer `configs/type_XX.json` with `data_updated_at` and `data_update_note`.

