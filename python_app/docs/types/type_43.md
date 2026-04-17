# Type 43 — Trunnion 曲面設備全約束支撐 (Trunnion Vessel Clamp Support)

> **圖號**: 43 &nbsp;|&nbsp; **分類**: 支撐型式 &nbsp;|&nbsp; **狀態**: 🔲 參考
> **圖面編號**: E1906-DSP-500-006 &nbsp;|&nbsp; **圖面頁**: D-51 (1/2), D-52 (2/2)
> **日期**: 12/12/19

透過 Trunnion + Lug Plate 將管線**全約束（full restraint）固定**在 Vessel 上的斜撐系統。
A 型 (θ=30°) / B 型 (θ=45°)。
**與 Type 42 的本質差異**：Type 42 管線僅「靠」在 Trunnion 上（承托），Type 43 管線被 Lug Plate「鎖」住（clamp）。

---

## 系統定位

```
TYPE-37 → 平面斜撐（無曲面）
TYPE-39 → 曲面 + Lug Plate 直接接 Vessel（無 Trunnion）
TYPE-42 → 曲面 + Trunnion 承托（不鎖管）
TYPE-43 → 曲面 + Trunnion + Lug Plate clamp（完全鎖管） ← 本型
```

> Type 43 = Type 39 的結構 + Type 42 的 Trunnion 接口。
> 適用：高溫、高振動、不允許滑動的 Vessel 管線支撐。

---

## 結構組成

| 元件 | 說明 |
|------|------|
| TRUNNION SIZE "P" | 短管支座，焊在 Vessel 上，由 D-72/73/74 (Type 61) 校核 |
| MEMBER "M" | 斜撐主桿（L 角鋼或 C 槽鋼，6 種規格） |
| L75×75×9 | 頂部水平角鋼（固定） |
| LUG PLATE TYPE-C (M-34) | DETAIL Y — 管線端 clamp |
| LUG PLATE TYPE-D/E (M-35/36) | DETAIL Z — Trunnion/Vessel 端接合 |
| Ø22 HOLES + 3/4"×50 M.B. | 機械螺栓連接（兩端皆有） |
| C/S SHIM IN FIELD (TYP.) | 現場碳鋼墊片調整 |
| INSUL. "t" | 保溫層厚度 |

### DETAIL Y（管線端）

- LUG PLATE TYPE-C → SEE M-34
- 將管線**夾住**固定在 Member 上
- 尺寸：A, E, F, G, U, J（由表 1 查）

### DETAIL Z（Vessel/Trunnion 端）

- LUG PLATE TYPE-D & E → SEE M-35, 36
- 依斜撐角度選用：θ=30° → TYPE-E (M-36)；θ=45° → TYPE-D (M-35)
- 與 Type 39 DETAIL Z 選用規則相同

---

## 幾何公式

### H 計算（NOTE 3）

```
H = K - √(R² - Q²) - t - E - 30
```

| 符號 | 意義 |
|:---:|------|
| K | Vessel ℄ 到管線支撐點距離 |
| R | Vessel 半徑 |
| Q | 管線水平偏移（由表 3 查） |
| t | 保溫層厚度 |
| E | Lug 偏移（由表 1 查，30 或 35mm） |
| 30 | 固定間距 (mm) |

### 與 Type 42 公式比較

| | Type 42 | Type 43 |
|------|---------|---------|
| 公式 | H = F - √(R² - E²) | H = K - √(R² - Q²) - t - E - 30 |
| 管線偏移 | E（直接查表） | Q（由管徑查表） |
| 保溫 | 未明確扣除 | 明確扣 t |
| Lug 偏移 | 無（不用 Lug） | 扣 E |

### 斜撐尺寸公式

| θ | S（斜撐端距） | N（斜撐全長） |
|:---:|------|------|
| 30° (A) | 0.577H + offset | 1.155H + offset |
| 45° (B) | H + offset | 1.414H + offset |

> 0.577 = tan(30°)，1.155 = 2×tan(30°) = 1/cos(30°)
> offset 因 Member 規格而異（見表 2）

---

## 表 1：Member 尺寸（D-51）

DIMENSION (mm)

| MEMBER "M" | A | C | D | E | F | G | J |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| L75×75×9 | 160 | 75 | 40 | 30 | 70 | — | — |
| C100×50×5 | 170 | 100 | 50 | 30 | 80 | — | — |
| C125×65×6 | 170 | 125 | — | 30 | 80 | 35 | 55 |
| C150×75×9 | 190 | 150 | — | 30 | 100 | 40 | 70 |
| C180×75×7 | 210 | 180 | — | 35 | 110 | 45 | 90 |
| C200×90×8 | 220 | 200 | — | 35 | 120 | 50 | 100 |

> L75/C100 無 G, J 欄（D = 40/50mm 直接定位）
> C125 以上無 D 欄（改用 G, J 定位）

---

## 表 2：斜撐參數（D-52）

### θ = 30°（FIG-A）

| MEMBER "M" | H(MAX.) | B | S | N |
|:---:|:---:|:---:|------|------|
| L75×75×9 | 950 | 135 | 0.577H − 8 | 1.155H + 92 |
| C100×50×5 | 950 | 145 | 0.577H − 7 | 1.155H + 100 |
| C125×65×6 | 1750 | 145 | 0.577H + 4 | 1.155H + 114 |
| C150×75×9 | 1750 | 165 | 0.577H + 3 | 1.155H + 125 |
| C180×75×7 | 1750 | 185 | 0.577H + 7 | 1.155H + 145 |
| C200×90×8 | 1750 | 195 | 0.577H + 9 | 1.155H + 155 |

### θ = 45°（FIG-B）

| MEMBER "M" | B | S | N |
|:---:|:---:|------|------|
| L75×75×9 | 115 | H − 30 | 1.414H + 57 |
| C100×50×5 | 120 | H − 31 | 1.414H + 55 |
| C125×65×6 | 130 | H − 33 | 1.414H + 41 |
| C150×75×9 | 140 | H − 36 | 1.414H + 47 |
| C180×75×7 | 150 | H − 32 | 1.414H + 60 |
| C200×90×8 | 160 | H − 36 | 1.414H + 56 |

> H(MAX.) 45° 欄未獨立標示，與 30° 共用。

---

## 表 3：管徑 → Trunnion / Q（D-52）

| LINE SIZE "N" | 2" | 3" | 4" | 6" | 8" | 10" | 12" | 14" | 16" | 18" | 20" | 24" |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| TRUNNION SIZE "P" | 1-1/2" | 2" | 2" | 3" | 4" | 6" | 8" | 10" | 10" | 12" | 12" | 14" |
| Q (mm) | 85 | 100 | 113 | 140 | 165 | 195 | 215 | 230 | 255 | 280 | 305 | 355 |

### 與 Type 42 表 2 比較

| LINE SIZE | Type 42 Trunnion | Type 43 Trunnion | Type 43 Q |
|:---:|:---:|:---:|:---:|
| 2" | 2" | 1-1/2" | 85 |
| 4" | 3" | 2" | 113 |
| 8" | 4" | 4" | 165 |
| 12" | 8" | 8" | 215 |
| 24" | 14" | 14" | 355 |

> Type 43 小管徑 Trunnion 普遍比 Type 42 小一號（2"→1-1/2", 4"→2"）。
> Type 42 用 E（管偏移），Type 43 用 Q——變數名稱不同但意義相近。

---

## 編碼格式（NOTE 1）

**格式**: `43-{N}-{M}-{H} {A|B}[-{Q}]`

```
43-2B-L75-520 A OR B-175
│  │   │   │   │      └─ MODIFY DIMENSION Q (mm), SEE NOTE 4
│  │   │   │   └──────── A: θ=30°, B: θ=45°
│  │   │   └───────────── DIMENSION H (mm)
│  │   └───────────────── MEMBER "M"
│  └───────────────────── SUPPORTED LINE SIZE "N"
└──────────────────────── TYPE NO.
```

> NOTE 4: Q 為標準值時可省略，非標準時附加於末尾。

---

## 工程 NOTES（原圖標註）

1. **DESIGNATION**: 如上述編碼格式
2. **TRUNNION SIZE MUST BE CHECKED BY SH'T D-72, 73 & 74** — Trunnion 結構強度由 Type 61 驗算
3. **H = K − √(R² − Q²) − t − E − 30**
4. **A: FOR θ = 30°, B: FOR θ = 45°**

---

## BOM（材料清單）

| # | 品名 | 說明 |
|:---:|------|------|
| 1 | Member "M" | L75×75×9 ~ C200×90×8，斜撐主桿 |
| 2 | L75×75×9 | 頂部水平角鋼（固定） |
| 3 | Trunnion "P" | 1-1/2"~14"，由表 3 查。須 D-72/73/74 校核 |
| 4 | Lug Plate (上) Type-C | M-34，DETAIL Y 鎖管 |
| 5 | Lug Plate (下) | DETAIL Z：θ=30° → M-36 (Type-E)；θ=45° → M-35 (Type-D) |
| 6 | 3/4"×50 M.B. + Nut | Ø22 孔，機械螺栓 |
| 7 | C/S Shim | 現場調整墊片 |

---

## 設計流程

```
1. 確定: LINE SIZE "N", Vessel R, 保溫 t, K
2. 查表 3: N → TRUNNION SIZE "P", Q
3. 計算 H = K - √(R² - Q²) - t - E - 30
4. 檢查 H ≤ H_MAX (表 2)
5. 選 Member "M" (依載荷/跨度)
6. 選 θ (30° 或 45°):
   - θ=30°: S = 0.577H+offset, N = 1.155H+offset
   - θ=45°: S = H+offset, N = 1.414H+offset
7. 查表 1: Member → A, C, D/G/J, E, F
8. Trunnion 校核: D-72/73/74 (Type 61)
9. Lug Plate 選型: DETAIL Y → M-34, DETAIL Z → M-35 或 M-36
10. 編碼: 43-{N}-{M}-{H} {A|B}[-{Q}]
```

---

## 關聯 Type

| 關聯 Type | 關係 |
|------|------|
| Type 39 | 同為曲面 clamp 支撐，但 39 直接接 Vessel（無 Trunnion），H = K−R−t−E−30 |
| Type 42 | 同為 Trunnion 支撐，但 42 不鎖管（承托），H = F−√(R²−E²)。共用 Trunnion + D-72/73/74 |
| Type 61 | Trunnion 結構校核（D-72/73/74）。NOTE 2 明確引用 |
| M-34 | Lug Plate Type-C，DETAIL Y（管線端 clamp） |
| M-35 | Lug Plate Type-D (45°)，DETAIL Z 當 θ=45° 時使用 |
| M-36 | Lug Plate Type-E (60°補償)，DETAIL Z 當 θ=30° 時使用 |

### 完整比較：Type 39 / 42 / 43

| | Type 39 | Type 42 | Type 43 |
|------|---------|---------|---------|
| 接 Vessel | 直接焊 Lug | Trunnion | Trunnion |
| 管線固定 | Lug Plate clamp | 承托（不鎖） | Lug Plate clamp |
| H 公式 | K−R−t−E−30 | F−√(R²−E²) | K−√(R²−Q²)−t−E−30 |
| Lug Plate | M-34 + M-35/36 | 無 | M-34 + M-35/36 |
| Trunnion 校核 | 不需要 | D-72/73/74 | D-72/73/74 |
| 約束程度 | 全約束 | 僅支撐 | 全約束 |
