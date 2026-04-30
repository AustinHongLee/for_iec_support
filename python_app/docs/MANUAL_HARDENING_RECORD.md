# Manual Hardening Record

Purpose: keep human-confirmed drawing interpretations separate from ordinary calculator assumptions. When future agents work on procurement-sensitive steel or M42 logic, read this file first, then check the linked calculator and golden assertions.

Last updated: 2026-04-30.

## Verification Standard

| Area | Confirmed source |
|---|---|
| M42 / M42A / M43 | `HP6-DSD-A4-500-001`, Rev.1, standard/check date `2024-07-15` |
| Type drawings | User-provided PDF image snapshots, manually interpreted and corrected by user |
| Golden assertions | `python_app/validate_tables.py` |
| Steel/M42 matrix | `python_app/docs/STEEL_M42_TYPE_VERIFICATION_MATRIX.md` |

## Confirmed Rules

| Type / area | Human-confirmed rule | Code anchor | Golden anchor |
|---|---|---|---|
| M42 plate `c` | `L3` / `L4` are support-steel positioning center distances, not plate cutouts. | `data/m42_table.py`, `core/m42.py` | M42 fallback and Type golden cases |
| M42 Type E | Components are plate `a` + plate `d` + L40x40x5x150 angle x2 + expansion bolt x4. | `core/m42.py` | M42 / Type golden cases |
| M42 Type F | Components are plate `a` + L40x40x5x150 angle x2 on existing steel. | `core/m42.py` | M42 / Type golden cases |
| M42 Type G | Components are plate `b` + expansion bolt x4. | `core/m42.py` | Type 08 golden case |
| M42 Type J | Components are plate `b` + expansion bolt x4, foundation by civil. | `core/m42.py` | Type 07 golden case |
| M42 Type K | Components are plate `a` + L40x40x5x150 angle x2, foundation by civil. | `core/m42.py` | M42 / Type golden cases |
| M42 Type L | Components are plate `c` + expansion bolt x4 for angle steel or H-beam. | `core/m42.py` | Type 03 / Type 05 golden cases |
| M42 missing pipe sizes | `0.5"` / `0.75"` use 1" row with warning; `20"` / `22"` use 24" row with warning; `26"` uses 28" row with warning. | `data/m42_table.py` | `validate_tables.py` |
| M42 missing steel sizes | Use next same-family listed steel row when possible and emit warning; if no larger same-family row exists, use largest same-family row with stronger warning. | `data/m42_table.py` | `validate_tables.py` |
| Type 03 | Vertical angle length is `H*100 + 1.5*NPS*25.4 + 20 + supported line OD/2`; example `03-1B-05L = 574.8mm`. | `core/types/type_03.py` | `validate_tables.py` |
| Type 05 | Vertical member length is `H*100 - 15`; example `05-L50-05L = 485mm`. | `core/types/type_05.py` | `validate_tables.py` |
| Type 06 | H length remains the input H value, but always emits warning: `H值長是欲保留現場裁切預量`. | `core/types/type_06.py` | `validate_tables.py` |
| Type 07 | Shared elbow offset is `200`; Pipe B length is `L + 200`; Pipe C length is `H - 200 - Plate F thickness - M42 plate thickness`; H range warning is `1500~3500`; always emits H field-trim warning. | `core/types/type_07.py` | `validate_tables.py` |
| Type 08 | Pipe A formula remains `H - 6 - channel height/2 - M42 plate thickness`; Channel N remains `L`; top plate remains `B x B x 6`; Stopper is fixed quantity 2, with `10C chamfer / 10mm` drawing feature kept as note. | `core/types/type_08.py` | `validate_tables.py` |
| Type 66 / pipe shoe core | Type 66 D-80 is the pipe shoe core. Type 52/53/54/55 add small restraint/guide components; they do not change the shoe core. Pad width is `OD*pi/3` with practical-calculation warning. Pad length is `LOPS + E*2` for `<=8"` and `LOPS + E*2 + 25*2` for `>=10"`. Pad thickness is SCH10S wall. Member C length is `LOPS/D` for `<=8"` and `LOPS + 25*2` for `10"~14"`. For `16"~24"`, fabricated 12t plates use width `A`, length `LOPS + 25*2`, height `HOPS`. `10"~24"` adds four reinforcing flat bars: thickness `B`, height `HOPS` as calculation-only warning, width `A`. | `core/pipe_shoe_engine.py`, `configs/pipe_shoe_spec.json` | `validate_tables.py` |

## Revoked / Reopened Assumptions

| Area | Reopened issue | Immediate policy |
|---|---|---|
| Pipe shoe family `52/53/54/55/66/67/80/85` | Earlier shared spec used `+25*2` on all H-beam member lengths and fixed pad thickness ranges. User clarified the Type 66 core rules above. | `<=24"` shared Type 66 core has been corrected and guarded. `26"~50"` D-80B remains provisional and should stay `review` until separately hardened. |

## Batch Verification Strategy

Use this when a long procurement list must be checked faster than manual drawing-by-drawing review.

1. Export or paste the support designation list as plain text or CSV. Avoid screenshots when possible; OCR errors are a bigger risk than calculator errors.
2. Run `python python_app/tools/batch_verify_designations.py --input <list.txt> --format md --output <report.md>`.
3. Sort the report by status:
   - `error`: designation cannot calculate; fix parser/input first.
   - `high`: Type has steel/M42 procurement impact but is not locked.
   - `review`: calculator emits warnings; verify before procurement.
   - `hardened`: Type has manual hardening or locked golden coverage.
   - `ok`: no warning/error, lower immediate risk.
4. For high-volume review, check one representative per Type/shape/branch first, then expand only the failing or warning-heavy groups.

## Current Fast Path

The fastest practical path is not to manually inspect every line first. Instead:

1. Batch-run all designations.
2. Group by Type and warning/error.
3. For Types already hardened here, trust calculator output unless the designation uses an untested branch.
4. For pending steel/M42 Types in `STEEL_M42_TYPE_VERIFICATION_MATRIX.md`, verify the drawing branch and add one golden assertion before approving bulk output.
5. Commit each Type correction separately, keeping procurement history traceable.
