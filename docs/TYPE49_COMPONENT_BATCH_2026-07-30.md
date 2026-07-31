# Type 49 Component Batch — 2026-07-30

## Scope

This batch visually reopened and implemented the complete Chung Wei Type 49
component chain:

- `TYPE-49_D-60.pdf`
- `RISER-CLAMP_TYPE-A_M-11.pdf`
- `RISER-CLAMP_TYPE-B_M-12.pdf`
- `LUG-PLATE_TYPE-P_M-41.pdf`

No CTCI Type 49 source sheet is present in the current split assets, so the
existing Chung Wei-only source gate remains.

## D-60 designation and branch truth

The released designation is:

`49-{LINE SIZE}B-{FIG A/B}{MATERIAL SYMBOL}`

The drawing example is `49-3/4B-A(A)`. The historical calculator only
recognized the compact form `49-{SIZE}{FIG}{SYMBOL}`. Runtime now accepts the
released form and retains the compact form as a compatibility alias.

Branch selection remains:

| Figure | Range | Components |
|---|---|---|
| A | 3/4"~2-1/2" | M-11 |
| A | 3"~20" | M-11 + M-41 |
| B | 3/4"~20" | M-12 |

The range is not interpolated. A line size absent from the selected M-11 or
M-12 table stops with an error.

## M-11 and M-12 are distinct tables

Both drawings define two carbon-steel formed flat bars around the supported
pipe, but several rows differ materially. For example:

| Size | M-11 A / stock / bolt | M-12 L / stock / bolt |
|---|---|---|
| 8" | 470 / 9x51 / 5/8"x70 | 470 / 10x51 / 5/8"x60 |
| 10" | 514 / 9x51 / 5/8"x70 | 527 / 10x51 / 5/8"x60 |
| 12" | 578 / 12x51 / 5/8"x70 | 578 / 13x51 / 5/8"x70 |

The exact source tables are retained separately in `m11_table.py` and
`m12_table.py`.

### Known strip-weight calculation

For each clamp half:

- neutral radius = `pipe OD / 2 + stock thickness / 2`
- M-11 straight total = `A - pipe OD - 2 x stock thickness`
- M-12 straight total = `150 + 50`
- developed length = `straight total + pi x neutral radius`
- known clamp steel = `2 x developed length x width x thickness x 7850 kg/m3`

M-12 directly dimensions the 150/50 straight projections. M-11 only
dimensions overall A; the symmetric split is derived from the fitted view and
is not released as a fabrication dimension.

The calculated weight intentionally excludes bolt/nut weight and hole
deductions.

## M-41 blank calculation

M-41 supplies four line-size ranges and exact A/B/C/D/S/T values plus the
required quantity. The face contour is represented by:

`[(0,0), (C,0), (C,A), (C-D,A), (0,B)]`

Therefore:

- gross area = `A x C`
- triangular cutout = `(C-D) x (A-B) / 2`
- net blank area = `gross - cutout`
- blank weight = `net area x T x material-class density x quantity`

D-60 material `(B)` means stainless plate, while M-41 internally uses suffix
`S`; runtime performs that translation. M-11/M-12 remain carbon steel because
their own sheets state carbon steel.

## Fabrication maturity

| Component | Lookup | Known weight | Blank / flat pattern | Finished fabrication |
|---|---|---|---|---|
| M-11 | ready | two strip blanks | partial | blocked |
| M-12 | ready | two strip blanks | partial | blocked |
| M-41 | ready | polygon plate blanks | ready | blocked |

Remaining blockers:

- M-11/M-12 do not dimension bolt-hole diameter, hole centers or end radii.
- Clamp material grade/coating and bolt/nut grade/scope/unit weight are absent.
- M-11 straight-leg split is derived rather than directly dimensioned.
- M-41 shows S, `T/2-S` and a 6 mm weld callout, but the pipe-end bevel
  length/angle and exact three-dimensional fit-up contour are not released.
- Hole deductions, M-41 end-preparation deductions and weld-metal weight are
  not estimated.

Type 49 now returns positive, source-traceable known steel weight while
retaining `bom_ready=false` and `fabrication_ready=false`.

## Validation

- `python -m pytest -q python_app/tests`: **722 passed**
- Dedicated new Type 49 component tests: **13 passed**
- `python python_app/validate_tables.py`: **VALIDATION COMPLETE**
- Existing phase 2L-A soft warnings: **40**
- Component registry: **54 lookup-ready / 3 partial / 14 metadata-only**
