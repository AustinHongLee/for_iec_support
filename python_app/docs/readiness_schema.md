# Readiness Matrix Schema

Phase: 0A scaffold only. This document defines the target schema; existing
component tables are not migrated in this phase.

## Purpose

Readiness must become field-level, not table-level. A component table can be
usable for one field and still missing another field. For example, a clamp table
may have source-transcribed `rod_size_a` and `load_650f_kg`, while dimensions
`B/C/D/E/G/H` are still missing.

## Target Shape

```python
READINESS_MATRIX = {
    "indexable_by": ["line_size"],
    "source_pdf": "M-5-PIPE CLAMP B.pdf",
    "transcription_method": "ai_visual",
    "fields": {
        "line_size": {
            "state": "source",
            "source_ref": "PDF row LINE SIZE",
        },
        "rod_size_a": {
            "state": "source",
            "source_ref": "PDF row F-col",
        },
        "load_650f_kg": {
            "state": "source",
            "source_ref": "PDF row LOAD@650F",
        },
        "load_750f_kg": {
            "state": "source_blank_conditional",
            "source_ref": "PDF row LOAD@750F",
            "applies_to": "rows where drawing leaves LOAD@750F blank",
        },
        "B": {"state": "missing"},
        "C": {"state": "missing"},
        "D": {"state": "missing"},
        "E": {"state": "missing"},
        "G": {"state": "missing"},
        "H": {"state": "missing"},
    },
    "weight": {
        "basis": "not_available",
        "estimator_id": None,
    },
}
```

## Field States

| State | Meaning |
|---|---|
| `source` | Directly transcribed from the source drawing or approved source table. |
| `source_blank_conditional` | The source intentionally leaves the field blank for a documented condition. |
| `derived` | Derived from source fields by a deterministic rule. |
| `estimated` | Engineering estimate with an estimator id. |
| `missing` | Field has not been transcribed or verified. |
| `not_applicable` | Field does not apply to this component. |

## Weight Basis

Weight basis must align with `core.weight_policy.WeightBasis`:

| Basis | Intended meaning |
|---|---|
| `source_unit_weight` | Source drawing/table explicitly lists unit weight. |
| `source_dimension_geometry` | Weight is calculated from source-ready dimensions and density. |
| `engineering_estimate` | Weight uses a declared estimator and requires review. |
| `not_available` | No acceptable basis exists; caller must decide explicitly. |

## Phase 0A Non-Goals

- Do not migrate existing M/N tables yet.
- Do not remove current `lookup_ready` or `weight_ready` flags yet.
- Do not change UI, registry, or calculator behavior yet.
