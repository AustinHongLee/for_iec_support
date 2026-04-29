# Phase 1D-5B Diff Report - Type 15 Support Pipe Material Semantics

Scope: Type 15 targeted material semantics only.

Code change:
- `type_15.py` now documents the vertical supporting pipe as `SUPPORT_PIPE` material resolved by the hardware material resolver.
- No Type 15 weight formula or BOM assembly code was changed.
- No resolver or override contract was changed.
- No additional `SUPPORT_PIPE` default change was required in this phase because Phase 1D-5A already corrected the shared high-temperature default to `SA-106 Gr.B`.

Expected material change:

| case | line | name | spec | before_material | after_material | before_weight | after_weight | expected_change | reason |
|---|---:|---|---|---|---|---:|---:|---|---|
| `15-2B-1005`, `service=high_temp` | 2 | Pipe | `2.0"*SCH.40` | `SA-240` | `SA-106 Gr.B` | 2.0800 | 2.0800 | yes | Type 15 vertical supporting pipe is pipe stock, not plate/bracket stock. |
| `15-6B-1508`, `service=high_temp` | 2 | Pipe | `6.0"*SCH.40` | `SA-240` | `SA-106 Gr.B` | 17.4600 | 17.4600 | yes | Same SUPPORT_PIPE semantic correction for larger Type 15 smoke case. |

Unchanged Type 15 rows:

| case | row group | material status | weight status | reason |
|---|---|---|---|---|
| `15-2B-1005`, default | all rows | unchanged | unchanged | Ambient SUPPORT_PIPE remains `A36 / SS400`. |
| `15-2B-1005`, `service=cryo` | all rows | unchanged | unchanged | CRYO SUPPORT_PIPE uses the `*` default for now. |
| `15-2B-1005`, `pipe_material=A335 P11` | all rows | unchanged | unchanged | `pipe_material` is intentionally ignored by hardware resolver. |
| `15-2B-1005`, `hardware_material_by_kind` | support pipe / plates only | override behavior unchanged | unchanged | Per-kind override still wins over defaults. |
| `15-2B-1005`, `upper_material=LEGACY_U` | support pipe only | legacy behavior unchanged | unchanged | Type 15 legacy scope remains SUPPORT_PIPE. |

Verification notes:
- Type 15 high-temperature support pipe resolves to `SA-106 Gr.B`.
- Channel and plate rows remain `A36 / SS400`; they do not inherit the pipe-stock default.
- Weight formula and weight outputs were not changed.
- This phase confirms Type 15 consumes the corrected `SUPPORT_PIPE` material semantics from the shared material contract.
