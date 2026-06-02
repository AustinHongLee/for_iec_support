# Phase 1D-5A Diff Report - Type 14 Support Pipe Material Semantics

Scope: Type 14 targeted material semantics only.

Code change:
- `HardwareKind.SUPPORT_PIPE` high-temperature default changed from `SA-240` to `SA-106 Gr.B`.
- `type_14.py` already dispatched the vertical supporting pipe to `HardwareKind.SUPPORT_PIPE`; no Type 14 weight or BOM assembly code was changed.
- `validate_tables.py` contract expectation was updated to the new SUPPORT_PIPE high-temperature default.

Expected material change:

| case | line | name | spec | before_material | after_material | before_weight | after_weight | expected_change | reason |
|---|---:|---|---|---|---|---:|---:|---|---|
| `14-2B-1005`, `service=high_temp` | 2 | Pipe | `2.0"*SCH.40` | `SA-240` | `SA-106 Gr.B` | 2.0800 | 2.0800 | yes | Type 14 vertical supporting pipe is pipe stock, not plate/bracket stock. |
| `14-6B-1508`, `service=high_temp` | 2 | Pipe | `6.0"*SCH.40` | `SA-240` | `SA-106 Gr.B` | 17.4600 | 17.4600 | yes | Same SUPPORT_PIPE semantic correction for larger Type 14 smoke case. |

Unchanged Type 14 rows:

| case | row group | material status | weight status | reason |
|---|---|---|---|---|
| `14-2B-1005`, default | all rows | unchanged | unchanged | Ambient SUPPORT_PIPE remains `A36 / SS400`. |
| `14-2B-1005`, `service=cryo` | all rows | unchanged | unchanged | CRYO SUPPORT_PIPE uses the `*` default for now. |
| `14-2B-1005`, `pipe_material=A335 P11` | all rows | unchanged | unchanged | `pipe_material` is intentionally ignored by hardware resolver. |
| `14-2B-1005`, `hardware_material_by_kind` | support pipe / plates only | override behavior unchanged | unchanged | Per-kind override still wins over defaults. |
| `14-2B-1005`, `upper_material=LEGACY_U` | support pipe + anchor bolt | legacy behavior unchanged | unchanged | Type 14 legacy scope remains SUPPORT_PIPE + ANCHOR_BOLT. |

Verification notes:
- Type 14 high-temperature support pipe now resolves to `SA-106 Gr.B`.
- Plate rows remain `A36 / SS400`; they do not inherit the pipe-stock default.
- Weight formula and weight outputs were not changed.
- This phase corrects the SUPPORT_PIPE default used by Type 14. Other remapped Types that explicitly request `service=high_temp` and use `SUPPORT_PIPE` will also resolve to the corrected pipe-stock material by design of the shared material contract.
