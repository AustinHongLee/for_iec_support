# Type 62 / M-3 / M-31 / M-33 Rebuild — 2026-07-30

## Scope

This batch visually reopened and implemented:

- `單張-本案有關/中威/TYPE-62_D-75.pdf`
- `單張-本案有關/中威/TYPE-62_D-76.pdf`
- `單張-本案有關/中威/ADJUSTABLE-CLEVIS_M-3.pdf`
- `單張-本案有關/中威/STEEL-WASHER-PLATE_M-31.pdf`
- `單張-本案有關/中威/LUG-PLATE_TYPE-B_M-33.pdf`

The two available CTCI 20E4588 Type 62 pages were also visually compared:

- `單張-本案有關/中鼎/長春_Type/TYPE-62_D-75.pdf`
- `單張-本案有關/中鼎/長春_Type/TYPE-62_D-76.pdf`

## Source-family decision

The CTCI 20E4588 pair cannot reuse the Chung Wei runtime:

- Chung Wei lower figures: E/G/H/J/K/L/M/N/Q
- CTCI lower figures: P/Q
- Chung Wei designation uses fractional-inch rod sizes
- CTCI example uses metric `M16`
- CTCI adds Detail Z, LGP-A, reinforcing-pad, bolt and insulation rules

No CTCI M-3/M-31/M-33 component sheets were found in the supplied source tree. The generic source-profile gate therefore continues to block CTCI Type 62 instead of silently applying Chung Wei data.

## Component transcription

### M-3 Adjustable Clevis

- 21 exact rows: 1/2 through 30 inch
- Stored fields: ADC designation, line size, maximum recommended load, upper/lower steel size, A rod, B/C/D/E, F adjustment and G cross bolt
- Exact-row lookup only; no interpolation
- Type 62 FIG-E now enforces the source A rod against the designation rod

M-3 is a formed purchased assembly. The source gives no finished weight, bend radii/developed strip lengths, cross-bolt length/grade or complete nut/washer scope. Runtime therefore emits a zero-weight purchased component with the real row parameters.

### M-31 Steel Washer Plate

- 17 exact rod-size rows: 3/8 through 3-3/4 inch
- Square side `C`, centered hole diameter `D`, thickness `T`
- Net weight:

```text
net area = C² - πD²/4
weight = net area × T × 7.85e-6 kg/mm³
```

The source explicitly lists `SWP-3 1/2` as `C=178, D=75, T=19`. The non-monotonic `D=75` value is preserved and marked as a source anomaly; it was not silently changed to a guessed 95.

### M-33 Lug Plate Type-B

- 12 exact rows: 2/3/4/6/8/10/12/14/16/18/20/24 inch
- Stored fields: LGP-B designation, A line size, B hanger rod, C/D/E/K/R/T/S, maximum recommended load, weld callout and the source 12/24 contact-detail callouts
- Exact-row lookup only; no interpolation
- Type 62 FIG-Q now enforces the source B rod against the designation rod

The source does not uniquely release the pipe-contact flat contour/bevel, and it gives no finished plate weight. Runtime therefore emits zero weight with a shaped-plate blocker instead of calculating a bounding-box estimate.

## Type 62 formula correction

D-75 dimension `H` is the hanger assembly dimension. It is not a released M-22 rod cut length.

The previous implementation used maximum H as M-22 cut length and calculated round-bar weight. That behavior was removed:

- no `rod_cut_length_mm`: M-22 remains a zero-weight reference
- explicit positive `rod_cut_length_mm`: M-22 table calculates that released cut
- H/H-range remains structured assembly metadata

The same truth-first rule now excludes Type 62 fallback estimates for unresolved M-4~M-10 clamps, missing M-21/M-24/M-25/M-28 rows and heavy-hex nuts. Existing exact rows still calculate.

## Fabrication maturity

| Component | Lookup | Weight | Blank / shop drawing |
|---|---|---|---|
| M-3 | complete dimensional/load lookup | unavailable | purchased assembly; source manufacturing details incomplete |
| M-31 | complete | exact net steel weight | geometry complete; material grade/coating and host weld location remain |
| M-33 | complete dimensional/load lookup | unavailable | pipe-contact contour/bevel unresolved |
| M-22 in Type 62 | component table exists | only with explicit cut | H cannot be used as cut length |

Type 62 remains `bom_ready=false` and `fabrication_ready=false` whenever any selected component has excluded weight or unresolved fabrication geometry.

## Validation

- 11 dedicated Type 62/component tests pass.
- 104 related source/component tests pass.
- Full suite: 733 passed.
- `validate_tables.py`: `VALIDATION COMPLETE`; 40 expected phase 2L-A material warnings.
