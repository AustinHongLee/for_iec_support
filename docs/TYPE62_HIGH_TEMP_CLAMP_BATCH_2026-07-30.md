# Type 62 M-8 / M-9 / M-10 High-temperature Clamp Batch — 2026-07-30

## Scope

This batch rendered and visually reopened the three Chung Wei Rev.1 sheets:

- `單張-本案有關/中威/PIPE-CLAMP_TYPE-E_M-8.pdf`
- `單張-本案有關/中威/PIPE-CLAMP_TYPE-F_M-9.pdf`
- `單張-本案有關/中威/PIPE-CLAMP_TYPE-G_M-10.pdf`

They are the D-76 lower FIG-L / FIG-M / FIG-N component sources.

## Transcription result

| Component | Rows | Source fields |
|---|---:|---|
| M-8 Type-E | 9 | line size; 650/750/1000/1050°F load; B/C/D/E/F/G/H |
| M-9 Type-F | 7 | line size; 750/950/1000/1050°F load; C/D/E/F/H/K |
| M-10 Type-G | 7 | line size; used-on O.D. range; 950/1000/1050/1075°F load; C/D/E/F/H/K/M |

All three tables now use exact source rows. A line size that lies inside the
D-76 minimum/maximum range but has no component row is rejected; it is not
interpolated.

## Interface interpretation

The clamp-table F/H values are clamp cross-bolt, upper cross-pin or U-bolt
diameters. They are not the hanger-rod size encoded in the Type 62
designation.

This is independently supported by the existing D-75 example:

```text
62-4B-5/8-05~30D-J(T)
```

The selected M-6 4-inch clamp row has a different F size. Requiring the clamp
F/H value to equal the Type 62 hanger rod would therefore reject a released
drawing example. The runtime preserves both sets of dimensions without adding
that false equality rule.

## Material

- M-8: `CHROME MOLYBDENUM STEEL (ASTM A387-GR.22)`
- M-9/M-10: chrome-moly clamp body, except stainless-steel U-bolt

The M-9/M-10 drawing does not release either material grade. Runtime therefore
uses the source composite material description and retains a procurement /
fabrication blocker.

## Weight and fabrication boundary

No sheet has a finished unit-weight column. They also do not fully release:

- formed-part bend radii, allowance and flat development
- pin/bolt length, grade and complete nut/washer scope
- U-bolt developed length and threaded-end length for M-9/M-10
- required material grades for M-9/M-10

The Type 62 BOM now emits the exact `PCL-E/F/G-*` designation, source material,
dimensions and temperature/load table, but keeps clamp weight at zero.
Bounding-box or catalog-style estimated weights were not introduced.

## Type 62 integration

- FIG-L selects M-8 exact rows.
- FIG-M selects M-9 exact rows.
- FIG-N selects M-10 exact rows.
- M-25 and the D-75 heavy-hex-nut callouts remain separate assembly entries.
- Assembly H still does not become an M-22 cut length.
- The CTCI 20E4588 Type 62 source remains blocked by its separate source gate.

## Validation

- 18 dedicated Type 62/component tests pass.
- 97 related Type 62/Type 49/cold-component registry tests pass.
- Full suite: 740 passed.
- `validate_tables.py`: `VALIDATION COMPLETE`; 40 expected phase 2L-A material warnings.
