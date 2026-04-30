# Steel / M42 Type Verification Matrix

Purpose: track verification of support Types that affect structural steel procurement or M42 lower-component procurement.

Verification basis:

- M42/M42A/M43 standard source: `HP6-DSD-A4-500-001`, Rev.1, standard/check date 2024-07-15.
- M42 visual rules: `docs/M42_BASE_SUPPORT_RULES.md`.
- Steel weight source: `data/steel_sections.py`.
- Current calculator smoke/golden entry point: `validate_tables.py`.

Status legend:

- `locked`: has explicit golden assertions for steel/M42 BOM details.
- `partial`: has smoke or some assertions, but not enough drawing-by-drawing coverage.
- `pending`: calculator runs or source exists, but steel/M42 correctness still needs manual verification.

## Scope Matrix

| Type | Steel procurement path | M42 path | Current status | Next verification focus |
|---|---|---|---|---|
| 03 | Angle L75 vertical formula + 130 horizontal | Yes, by fixed `L75*75*9` | partial | Confirm U-bolt supply rule and M42 letter options. |
| 05 | Angle by member vertical formula + fixed 130 horizontal | Yes, by member steel | partial | Confirm allowed M42 D/L/P/R and member-to-M42 lookup. |
| 06 | Angle by member, H + L with field-trim warning | No | partial | Confirm no M37 supply rule and whether L also needs user-facing warning. |
| 07 | Pipe B/C + Plate E/F sliding support | Yes, fixed `J` by Pipe C | partial | Confirm material override scope and H field-trim warning wording. |
| 08 | Channel N + pipe + top/stopper plates | Yes, G/J by pipe size | partial | Confirm material rule and whether H/L needs user-facing field-trim warning. |
| 14 | Channel N plus plates/anchor bolt | No M42 | partial | Confirm DETAIL a logic for 10"/12" and steel length. |
| 15 | Channel N plus plates | No M42 | partial | Confirm DETAIL a logic for 10"/12" and steel length. |
| 19 | Angle/H Beam from table | No | pending | Confirm M-43-like section table and line-size row mapping. |
| 20 | Angle/Channel H member | No | partial | Confirm single member H and section table. |
| 21 | Angle member H + L | No | pending | Confirm figure/length rules. |
| 22 | Angle member H + L | Yes, L/P by member steel | pending | Confirm Fig A/B/C parsing and M42 L/P. |
| 23 | Angle member H + L | No | pending | Confirm figure/length rules. |
| 24 | Single Angle H | No | pending | Confirm no U-bolt supply and no M42. |
| 25 | Angle H + L | No | partial | Confirm Fig C optional L1/L2 split. |
| 26 | Angle/Channel multi-member | No | partial | Confirm Fig A/C member split and lengths. |
| 27 | Angle/H Beam column + top beam | Yes, by member steel | locked | Expand golden set only if new member/M42 variants appear. |
| 28 | Angle/Channel portal frame | Yes, by member steel | partial | Lock golden cases for all standard M42 L/P and channel variant. |
| 30 | Angle/Channel clamp frame | No | partial | Confirm Fig A/B offset and no M42. |
| 31 | Angle/Channel/H Beam frame | No | pending | Confirm three-member frame lengths. |
| 32 | Angle/Channel/H Beam hanging frame | No | pending | Confirm lower beam and hanging-leg lengths. |
| 33 | Angle/Channel half frame | No | pending | Confirm side/low beam orientation and lengths. |
| 34 | Angle/Channel cantilever | No | pending | Confirm column + top beam lengths. |
| 35 | Channel rail | No | partial | Confirm Fig A qty=1 and Fig B qty=2. |
| 36 | Section member by table | No | pending | Confirm source drawing formula and steel quantity. |
| 37 | H/Angle beam + brace | No | pending | Confirm H150 special thickness and brace formula. |
| 39 | Angle/Channel trunnion support | No M42 | locked | Keep golden cases for L75/C125/C200. |
| 41 | Parsed steel spec + optional extra member | No | pending | Confirm all supported patterns and steel spec parser. |
| 42 | Trunnion main beam + diagonal brace | No M42 | locked | Keep golden cases for L75/C125/C200. |
| 43 | Trunnion main beam + diagonal brace | No M42 | locked | Keep golden cases for L75/C125/C200 plus lug plates. |
| 44 | Channel main column + conditional L50 brace | No M42 | pending | Confirm brace trigger and length. |
| 45 | Channel main column + conditional L50 brace | No M42 | pending | Confirm H+A length and brace trigger. |
| 46 | Channel main column + conditional L50 brace | No M42 | pending | Confirm H length and brace trigger. |
| 47 | Channel main column + conditional L50 brace | No M42 | pending | Confirm H+A length and brace trigger. |
| 51 | Small pipe flat bar, larger pipe Angle/Channel | No M42 | partial | Confirm small vs large branch and steel quantity. |
| 52 | Pipe shoe Angle/H Beam by shared spec | No M42 | locked | Confirm shared spec against D-80 for more sizes. |
| 53 | Pipe shoe Angle/H Beam by shared spec | No M42 | pending | Confirm variant-specific restraint/guiding differences. |
| 54 | Pipe shoe Angle/H Beam by shared spec | No M42 | pending | Confirm clamp/gasket variants. |
| 55 | Pipe shoe Angle/H Beam by shared spec | No M42 | pending | Confirm clamp/gasket variants. |
| 66 | Pipe shoe H Beam / fabricated plate path | No M42 | locked | Confirm compact and large-pipe D-80A cases. |
| 67 | Pipe shoe H Beam / fabricated plate path | No M42 | pending | Confirm variant-specific differences from 66. |
| 85 | Pipe shoe shared spec | No M42 | pending | Confirm why it shares `type_52.py` and any drawing delta. |
| 65 | Parsed Angle/Channel/H Beam member | No M42 | pending | Confirm member parser and plate/angle bracket supply. |
| 80 | H Beam or Angle path by D-95/D-96 | No M42 | locked | Keep small/big golden cases; add mid-size if needed. |

## Batch 1 Output For User Check

These are current calculator outputs, not yet declared correct until checked against drawings.

### Type 03

Input: `03-1B-05L`

Confirmed formula update:

```text
vertical Angle length = H*100 + 1.5*NPS*25.4 + 20 + supported line OD/2
03-1B-05L = 500 + 38.1 + 20 + 16.7 = 574.8mm
```

| Item | Name | Spec | L | W | Qty | Weight output | Material | Remark |
|---:|---|---|---:|---:|---:|---:|---|---|
| 1 | Angle | `75*75*9` | 574.8 | 0 | 1 | 5.73 | A36/SS400 | H=500 + LR elbow center=38.1 + clearance=20 + OD/2=16.7 |
| 2 | Angle | `75*75*9` | 130 | 0 | 1 | 1.29 | A36/SS400 |  |
| 3 | U.bolt | `UB-1B` | 0 | 0 | 1 | 1.00 | SUS304 |  |
| 4 | Plate_c_有鑽孔 | `9` | 260 | 260 | 1 | 4.78 | A36/SS400 | rect holes 190x190, dia 19, 5/8" x4 |
| 5 | EXP.BOLT | `5/8"` | 0 | 0 | 4 | 4.00 | SUS304 |  |

Total weight: 16.80 kg.

### Type 05

Input: `05-L50-05L`

Confirmed formula update:

```text
vertical Angle length = H*100 - 15
05-L50-05L = 500 - 15 = 485mm
```

| Item | Name | Spec | L | W | Qty | Weight output | Material | Remark |
|---:|---|---|---:|---:|---:|---:|---|---|
| 1 | Angle | `50*50*6` | 485 | 0 | 1 | 2.15 | A36/SS400 | H=500 - top offset=15 |
| 2 | Angle | `50*50*6` | 130 | 0 | 1 | 0.58 | A36/SS400 |  |
| 3 | Plate_c_有鑽孔 | `9` | 180 | 180 | 1 | 2.29 | A36/SS400 | rect holes 110x110, dia 19, 5/8" x4 |
| 4 | EXP.BOLT | `5/8"` | 0 | 0 | 4 | 4.00 | SUS304 |  |

Total weight: 9.02 kg.

### Type 06

Input: `06-L50-0510-0401`

Warnings:

```text
Type 06: H=500mm H值長是欲保留現場裁切預量
```

| Item | Name | Spec | L | W | Qty | Weight output | Material |
|---:|---|---|---:|---:|---:|---:|---|
| 1 | Angle | `50*50*6` | 500 | 0 | 1 | 2.21 | A36/SS400 |
| 2 | Angle | `50*50*6` | 1000 | 0 | 1 | 4.43 | A36/SS400 |

Total weight: 6.64 kg.

### Type 07

Input: `07-2B-20J`

Confirmed formula update:

```text
shared elbow offset = 200
Pipe B length = L + 200 = 71 + 200 = 271mm
Pipe C length = H - 200 - Plate F thickness - M42 plate thickness
Pipe C length = 2000 - 200 - 9 - 9 = 1782mm
H valid warning range = 1500~3500mm
```

Warnings:

```text
Type 07: H=2000mm H值長是欲保留現場裁切預量
```

| Item | Name | Spec | L | W | Qty | Weight output | Material | Remark |
|---:|---|---|---:|---:|---:|---:|---|---|
| 1 | Pipe | `1-1/2"*SCH.80` | 271 | 0 | 1 | 1.47 | A36 / SS400 |  |
| 2 | Pipe | `3"*SCH.40` | 1782 | 0 | 1 | 20.12 | A36 / SS400 |  |
| 3 | Plate_E | `9` | 200 | 200 | 1 | 2.83 | A36 / SS400 |  |
| 4 | Plate_F | `9` | 200 | 200 | 1 | 2.83 | A36 / SS400 |  |
| 5 | Plate_b_有鑽孔 | `9` | 180 | 180 | 1 | 2.29 | A36/SS400 | rect holes 110x110, dia 19, 5/8" x4 |
| 6 | EXP.BOLT | `5/8"` | 0 | 0 | 4 | 4.00 | SUS304 |  |

Total weight: 33.54 kg.

### Type 08

Input: `08-2B-1005G`

| Item | Name | Spec | L | W | Qty | Weight output | Material | Remark |
|---:|---|---|---:|---:|---:|---:|---|---|
| 1 | Pipe | `2"*SCH.40` | 435 | 0 | 1 | 2.37 | A53Gr.B |  |
| 2 | Channel | `100*50*5` | 1000 | 0 | 1 | 9.36 | A36/SS400 |  |
| 3 | Plate_b_有鑽孔 | `9` | 180 | 180 | 1 | 2.29 | A36/SS400 | rect holes 110x110, dia 19, 5/8" x4 |
| 4 | EXP.BOLT | `5/8"` | 0 | 0 | 4 | 4.00 | SUS304 |  |
| 5 | Plate_STOPPER | `6` | 70 | 160 | 2 | 1.06 | A36/SS400 | STOPPER 2片；圖面保留 10C chamfer / 10mm 折角特徵 |
| 6 | Plate_TOP | `6` | 80 | 80 | 1 | 0.30 | A36/SS400 |  |

Total weight: 19.38 kg.
