# Batch Verify: Leader List

Date: 2026-04-30.

Input: user-provided text list under header `型號`.

Tool: `python_app/tools/batch_verify_designations.py`.

## Summary

| Metric | Count |
|---|---:|
| Total designations parsed | 253 |
| `hardened` | 0 |
| `review` | 80 |
| `high` | 143 |
| `ok` | 29 |
| `error` | 1 |

Status meaning:

- `hardened`: Type has manual hardening or locked golden coverage and no warning.
- `review`: calculator emits warnings, or a hardened Type uses a warning path.
- `high`: steel/M42 procurement-sensitive Type that is not yet manually hardened.
- `ok`: no warning/error and not currently flagged as steel/M42 high-risk.
- `error`: calculator cannot produce a result.

## Type Distribution

| Type | Count |
|---:|---:|
| 01 | 6 |
| 10 | 2 |
| 15 | 1 |
| 16 | 1 |
| 20 | 2 |
| 21 | 2 |
| 22 | 2 |
| 23 | 52 |
| 24 | 12 |
| 25 | 12 |
| 26 | 3 |
| 27 | 4 |
| 28 | 2 |
| 30 | 4 |
| 32 | 30 |
| 33 | 1 |
| 35 | 24 |
| 37 | 2 |
| 51 | 8 |
| 52 | 27 |
| 53 | 2 |
| 57 | 14 |
| 59 | 16 |
| 66 | 22 |
| 80 | 2 |

## Blocking Error

| Designation | Error |
|---|---|
| `51-1/2B` | `Type 51: 管徑 1/2B (0.5") 不在範圍 (3/4"~42")` |

## Warning Items

After the pipe shoe Type 66 core rework, pipe shoe rows with reinforcing pads emit:

```text
Pipe shoe pad width uses OD*pi/3 as practical calculation value
```

Rows in `52/53/54/55/66/67/80/85` are still classified as `review` by the batch tool until D-80B / D-96 branches are separately hardened.

| Designation | Warning |
|---|---|
| `01-6B-16T` | `H=1600mm 超出 Type 01 適用範圍 (<= 1500mm), 非標準設計` |
| `10-3B-05U` | `M42 字母 'U' 不在 Type 10 允許範圍 ['A', 'B', 'E', 'G']（照算）` |
| `10-3B-10U` | `M42 字母 'U' 不在 Type 10 允許範圍 ['A', 'B', 'E', 'G']（照算）` |
| `22-L75-12(A)X` | `M42 字母 'A' 不在 Type 22 允許範圍 (僅 L/P)` |
| `22-L75-14(A)X` | `M42 字母 'A' 不在 Type 22 允許範圍 (僅 L/P)` |
| `23-L50-06B` | `H=600mm 超過 L50 的上限 500mm` |
| `23-L50-06C-04` | `H=600mm 超過 L50 的上限 500mm` |
| `23-L50-07A` | `H=700mm 超過 L50 的上限 500mm` |
| `23-L50-08A` | `H=800mm 超過 L50 的上限 500mm` |
| `23-L65-19B` | `H=1900mm 超過 L65 的上限 1500mm` |
| `27-L50-0204X-0101` | `M-42 型式 'X' 非標準 (NOTE 4: USE TYPE-L & P ONLY)` |
| `27-L75-0305X-0202` | `M-42 型式 'X' 非標準 (NOTE 4: USE TYPE-L & P ONLY)` |
| `27-L75-0306U-0202` | `M-42 型式 'U' 非標準 (NOTE 4: USE TYPE-L & P ONLY); H=600mm 超出 L75 標準範圍 (<= 500mm), 非標準設計` |
| `27-L75-0306X-0202` | `M-42 型式 'X' 非標準 (NOTE 4: USE TYPE-L & P ONLY); H=600mm 超出 L75 標準範圍 (<= 500mm), 非標準設計` |
| `28-L75-0405D` | `M-42 型式 'D' 非標準 (NOTE 4: USE TYPE-L & P ONLY)` |
| `28-L75-0813D` | `M-42 型式 'D' 非標準 (NOTE 4: USE TYPE-L & P ONLY)` |
| `30-L50-0407B-0202` | `L=400mm 超出 L50 標準範圍 (<= 300mm); H=700mm 超出 L50 標準範圍 (<= 600mm)` |
| `30-L75-1109B-0704` | `L=1100mm 超出 L75 標準範圍 (<= 700mm)` |
| `32-C150-1610` | `L=1600mm 超出 C150 標準範圍 (<= 1500mm)` |
| `32-L75-1110` | `L=1100mm 超出 L75 標準範圍 (<= 1000mm)` |
| `32-L75-1308` | `L=1300mm 超出 L75 標準範圍 (<= 1000mm)` |
| `35-L75-09A` | `H=900mm 超出 L75 FIG-A 標準範圍 (<= 800mm)` |
| `59-1/2B-A` | `FIG-A: Pipe Shoe (D-63) NOT FURNISHED, 需另行計算` |
| `59-3/4B-A` | `FIG-A: Pipe Shoe (D-63) NOT FURNISHED, 需另行計算` |
| `59-2B-A` | `FIG-A: Pipe Shoe (D-63) NOT FURNISHED, 需另行計算` |
| `59-3B-A` | `FIG-A: Pipe Shoe (D-63) NOT FURNISHED, 需另行計算` |
| `59-4B-A` | `FIG-A: Pipe Shoe (D-63) NOT FURNISHED, 需另行計算` |
| `59-6B-A` | `FIG-A: Pipe Shoe (D-63) NOT FURNISHED, 需另行計算` |
| `59-14B-A` | `FIG-A: Pipe Shoe (D-63) NOT FURNISHED, 需另行計算` |

## High-Risk Unhardened Type Groups

| Type | Count | Representative designations |
|---:|---:|---|
| 23 | 47 | `23-C100-04C-07`, `23-C100-05C-09`, `23-C100-07B`, `23-C100-07C-09`, `23-C150-05C-09`, `23-H100-04C-11`, `23-L50-02A`, `23-L75-12A` |
| 32 | 27 | `32-C125-0705`, `32-C125-0812`, `32-C150-1206`, `32-L50-0301`, `32-L75-0505`, `32-L75-0914` |
| 35 | 23 | `35-C100-03A`, `35-C125-04A`, `35-C150-09A`, `35-L50-01A`, `35-L75-03A` |
| 24 | 12 | `24-L50-02`, `24-L50-10`, `24-L75-04`, `24-L75-14` |
| 25 | 12 | `25-L50-0203A-0101`, `25-L65-0504A-0303`, `25-L75-0909A-0306` |
| 51 | 7 | `51-1B`, `51-1.1/2B`, `51-2B`, `51-3B`, `51-4B`, `51-6B`, `51-14B` |
| 26 | 3 | `26-C125-0904A`, `26-C125-1011A`, `26-L50-0401A` |
| 30 | 2 | `30-L75-0307A-0202`, `30-L75-0707B-0403` |
| 37 | 2 | `37-H100-1400A`, `37-H150-1800A` |
| 53 | 2 | `53-3B-A-150-250`, `53-4B-A-150-250` |
| 15 | 1 | `15-8B-1532` |
| 20 | 2 | `20-L50-04A`, `20-L75-13A` |
| 21 | 2 | `21-L50-07A`, `21-L65-07B` |
| 33 | 1 | `33-C150-1409` |

## Recommended Hardening Order

1. Fix or decide `51-1/2B` first, because it is the only blocking calculation error.
2. Keep pipe shoe family `52/53/54/55/66/67/80/85` in review. Type 66 D-80 core for `<=24"` has been reworked, but D-80B / D-96 branches remain provisional.
3. Resolve warning-only M42 designation anomalies before broad steel review:
   `22-L75-12(A)X`, `22-L75-14(A)X`, Type 27 `X/U`, and Type 28 `D`.
4. Harden Type 23 next. It accounts for the largest unverified structural-steel volume. Verify by branch/member family rather than all 52 rows:
   C100/C150/H100/L50/L65/L75/L100 and Fig A/B/C.
5. Harden Type 32 and Type 35 after Type 23. Together they represent 54 high-risk rows.
6. Then handle Type 24/25/26/30/37/51/53 as smaller batches.
