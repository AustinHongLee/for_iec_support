# Phase 4A Warning Classification

Scope: current Phase 2L-A soft-lock warnings after Phase 3B Batch 3C.

Validation source: `python_app/validate_tables.py`

Current warning count: 23

- MUST_FIX: 1
- SHOULD_FIX: 4
- ACCEPTABLE: 18

## Classification Rules

- MUST_FIX: helper default material or clearly mappable standard material that should not remain unmanaged.
- SHOULD_FIX: manual entry or simple non-dynamic Type where canonical id can be added safely in a future migration.
- ACCEPTABLE: dynamic material, visual/estimated Type, descriptive material string, or material without a stable canonical standard in the current catalog.

## MUST_FIX

| Source | Type | Entry | Material | Category | Reason |
|---|---:|---:|---|---|---|
| `core/plate.py:34` | N/A | N/A | `A36/SS400` | MUST_FIX | Helper default material still emits unmanaged string when caller omits material. This is a core helper fallback and should be replaced with a `MaterialSpec` default or removed after all callers pass explicit material. |

## SHOULD_FIX

| Source | Type | Entry | Material | Category | Reason |
|---|---:|---:|---|---|---|
| soft-lock | `03` | 3 | `SUS304` | SHOULD_FIX | Manual U-bolt `AnalysisEntry`; material is canonicalizable (`JIS_SUS304`) and can be migrated without changing weight or BOM string. |
| soft-lock | `19` | 1 | `A36/SS400` | SHOULD_FIX | Simple steel-only Type; material is canonicalizable and should be a low-risk direct MaterialSpec migration. |
| soft-lock | `57` | 1 | `SUS304` | SHOULD_FIX | Manual U-bolt `AnalysisEntry`; canonicalizable but requires hand-setting `material_canonical_id`. |
| soft-lock | `57` | 2 | `SUS304` | SHOULD_FIX | Manual rod `AnalysisEntry`; canonicalizable but requires hand-setting `material_canonical_id`. |

## ACCEPTABLE

| Source | Type | Entry | Material | Category | Reason |
|---|---:|---:|---|---|---|
| soft-lock | `48` | 1 | `A36/SS400` | ACCEPTABLE | Dynamic material suffix Type; should be handled with the broader dynamic-material batch rather than patched singly. |
| soft-lock | `49` | 1 | `A36/SS400` | ACCEPTABLE | Dynamic material / riser clamp component path; depends on component-table truth source and should not be force-mapped in this phase. |
| soft-lock | `49` | 2 | `A36/SS400` | ACCEPTABLE | Dynamic material / lug plate component path; acceptable until Type 49 component truth source is normalized. |
| soft-lock | `52` | 1 | `A36/SS400` | ACCEPTABLE | Multi-code calculator with dynamic material flow; defer to dedicated Type 52 migration to avoid mixing material identity with branch logic. |
| soft-lock | `52` | 2 | `AS` | ACCEPTABLE | Dynamic material abbreviation with ambiguous canonical target in current catalog; defer until material aliases are reviewed. |
| soft-lock | `52` | 3 | `AS` | ACCEPTABLE | Dynamic material abbreviation with ambiguous canonical target in current catalog; defer until material aliases are reviewed. |
| soft-lock | `59` | 1 | `A283 Gr.C` | ACCEPTABLE | Dynamic/component estimate Type; material can be canonicalized later, but this path is coupled with U-bolt estimate behavior. |
| soft-lock | `72` | 1 | `Carbon Steel` | ACCEPTABLE | Visual/estimated Type; generic material string is intentionally non-specific and requires engineering review before canonical lock-in. |
| soft-lock | `72` | 2 | `SUS304` | ACCEPTABLE | Visual/estimated Type; keep grouped with Type 72 evidence cleanup rather than isolated material patch. |
| soft-lock | `73` | 1 | `A283-C` | ACCEPTABLE | Visual/estimated Type and component-derived geometry; canonical mapping should be reviewed with Type 73 evidence. |
| soft-lock | `73` | 2 | `ASTM A229 Class 1` | ACCEPTABLE | Spring material string is specific but belongs to visual/estimated Type 73 and should be handled with spring/component evidence. |
| soft-lock | `73` | 3 | `Carbon Steel` | ACCEPTABLE | Generic visual/estimated material string; requires engineering review before canonical lock-in. |
| soft-lock | `73` | 4 | `Carbon Steel` | ACCEPTABLE | Generic visual/estimated material string; requires engineering review before canonical lock-in. |
| soft-lock | `73` | 5 | `A36/SS400` | ACCEPTABLE | Type 73 is visual/estimated; defer until Type 73 material/evidence pass. |
| soft-lock | `76` | 1 | `Same as pipe / Carbon Steel` | ACCEPTABLE | Descriptive material string, not a single canonical material; requires engineering decision before normalization. |
| soft-lock | `77` | 1 | `Same/similar to pipe` | ACCEPTABLE | Descriptive material string, not a single canonical material; requires engineering decision before normalization. |
| soft-lock | `78` | 1 | `Carbon Steel` | ACCEPTABLE | Visual/estimated Type with generic material string; defer to Type 78 evidence cleanup. |
| soft-lock | `79` | 1 | `Carbon Steel` | ACCEPTABLE | Visual/estimated Type with generic material string and known M-55 weight risk; defer to Type 79 evidence/component cleanup. |

## Recommended Next Order

1. Fix MUST item: remove or MaterialSpec-manage `core/plate.py` default material path once remaining callers are controlled.
2. Batch SHOULD items: migrate `Type 03`, `Type 19`, and `Type 57` as a small manual/simple Type batch.
3. Leave ACCEPTABLE items documented until dynamic-material and visual/estimated evidence phases.
