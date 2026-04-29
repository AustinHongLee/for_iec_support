# Type 45 — 曲面設備直接夾持支撐 (Vessel Direct Clamp Support)

> **圖號**: 45 &nbsp;|&nbsp; **分類**: 支撐型式 &nbsp;|&nbsp; **狀態**: ✅ 已實作
> **圖面編號**: E1906-DSP-500-006 &nbsp;|&nbsp; **圖面頁**: D-54 (1/2), D-55 (2/2)
> **日期**: 12/12/19

**無 Trunnion、有 Lug Plate clamp** 的 Vessel 支撐——Type 44 的升級版，加入夾持系統與保溫修正。
A 型 (θ=30°) / B 型 (θ=45°)。僅適用 8"~14" 管徑。
公式 `H = P − √(R²−Q²) − 60 − t` 含保溫(t)和 Lug 偏移(60)修正。

> **注意**: Type 45（支撐型式）與 M-45（Expansion Bolt 零件）是完全不同的東西。

---

## 系統定位

```
TYPE-44 → 直接承托（無 clamp，無保溫修正）
TYPE-45 → 直接 + Lug Plate clamp + 保溫修正 ← 本型
TYPE-42 → Trunnion 承托（無 clamp）
TYPE-43 → Trunnion + Lug Plate clamp（全約束）
```

> Type 45 = Type 44 + Lug Plate clamp + 保溫修正。
> 與 Type 43 的差異：43 有 Trunnion，45 無 Trunnion（直接接 Vessel）。
> 適用：需夾持固定、有保溫、無需 Trunnion 的中型 Vessel 管線支撐。

---

## 結構組成

| 元件 | 說明 |
|------|------|
| Channel Member | C100×50×5 / C125×65×6 / C150×75×9（3 種） |
| L50×50×6 斜撐 | **僅 H > 1140mm 時安裝**，θ=30° 長 1008mm / θ=45° 長 1150mm |
| LUG PLATE TYPE-D/E (M-35/36) | DETAIL Y — **Vessel 端**接合（⚠️ 與 Type 39/43 的 Y/Z 反轉） |
| LUG PLATE TYPE-C (M-34) | DETAIL Z — **管線端** clamp |
| PLATE 90×45×6 | 端板 VIEW "A"~"A"，Ø16 孔 for 1/2"×30 M.B. |
| C100×50×5 座板 | Vessel 接觸端（PLAN 視圖） |
| Ø19 HOLE + 5/8"×40 M.B. | Detail Y — Lug Plate 連接螺栓 |
| ØJ HOLE + "K" bolt (3/4"×50) | Detail Z — Lug Plate 連接螺栓 |
| 6mm 焊接 (TYP.) | 全焊接構造 |
| INSUL. "t" | 保溫層厚度 |

### Detail Y/Z 反轉警告

| | Type 39 / 43 | **Type 45** |
|------|---------|---------|
| DETAIL Y | 管線端 → M-34 (Type-C) | **Vessel 端 → M-35/36 (Type-D/E)** |
| DETAIL Z | Vessel 端 → M-35/36 | **管線端 → M-34 (Type-C)** |

> ⚠️ **切勿混淆**。Type 45 的 Y/Z 分配與 Type 39/43 相反。

### DETAIL Y（Vessel 端）

- LUG PLATE TYPE-D/E → SEE M-35, 36
- Ø19 HOLE FOR 5/8"×40 M.B.
- 依斜撐角度：θ=30° → TYPE-E (M-36)；θ=45° → TYPE-D (M-35)
- 角度標註：30°/60°/30°

### DETAIL Z（管線端）

- LUG PLATE TYPE-C → SEE M-34
- ØJ HOLE FOR "K" BOLT (3/4"×50)
- INSUL. "t" 標示
- 尺寸：A, E, F, G, D, B, C（由表查）

---

## 幾何公式

### H 計算（D-55 表中公式）

```
H = P - √(R² - Q²) - 60 - t
```

| 符號 | 意義 |
|:---:|------|
| P | Vessel ℄ 到管線支撐點水平距離 |
| R | Vessel 半徑 |
| Q | 管線水平偏移（由表 1 查） |
| 60 | Lug + 連接固定偏移 (mm) |
| t | 保溫層厚度 |

### 公式演進比較

| | Type 44 | **Type 45** | Type 43 |
|------|---------|---------|---------|
| 公式 | P−√(R²−Q²) | **P−√(R²−Q²)−60−t** | K−√(R²−Q²)−t−E−30 |
| 保溫 | 無 | **扣 t** | 扣 t |
| Lug 偏移 | 無 | **扣 60（固定值）** | 扣 E+30（查表） |
| Trunnion | 無 | 無 | 有 |

> Type 45 的 60mm 固定值 = 等效於 Type 43 的 E(30)+30=60。

### 斜撐幾何

| θ | 垂直投影 | 水平基準 | L50 斜撐長 | 條件 |
|:---:|:---:|:---:|:---:|------|
| 30° (A) | 400 | 758 | 1008 | H > 1140 ONLY |
| 45° (B) | 693 | 758 | 1150 | H > 1140 ONLY |

> 758 為固定水平跨距（Type 44 = 780，略有不同）。
> 驗算：tan(30°) = 400/693 ≈ 0.577 ✓（693/758 斜面投影）

### 與 Type 44 斜撐比較

| | Type 44 | Type 45 |
|------|---------|---------|
| 水平跨距 | 780 | 758 |
| θ=30° 投影 | 450 | 400 |
| θ=45° 投影 | 780 | 693 |
| 斜撐長(30°) | 1016 | 1008 |
| 斜撐長(45°) | 1203 | 1150 |
| 安裝條件 | H ≥ 1200 | **H > 1140** |

---

## 表 1：管徑 → Q（D-54）

| LINE SIZE | 8" | 10" | 12" | 14" |
|:---:|:---:|:---:|:---:|:---:|
| Q (mm) | 113 | 140 | 165 | 181 |

> 與 Type 44 完全相同。

---

## 表 2：Member 尺寸（D-55）

DIMENSION (mm)

| MEMBER "M" | A | B | C | D | E | F | G | J | K |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| C100×50×5 | 170 | 50 | 100 | — | 30 | 80 | — | 22 | 3/4"×50 |
| C125×65×6 | 170 | — | 125 | 55 | 30 | 80 | 35 | 22 | 3/4"×50 |
| C150×75×9 | 190 | — | 150 | 70 | 30 | 100 | 40 | 22 | 3/4"×50 |

> C100 有 B=50 但無 D/G（直接定位）。C125/C150 無 B 但有 D/G（改用偏位定位）。
> J = Ø22 (bolt hole)，K = 3/4"×50 (bolt size)。

### 與 Type 44 尺寸比較

| | Type 44 | Type 45 |
|------|---------|---------|
| Member 數量 | 3 種 | 3 種（相同） |
| 有 K (bolt) 欄 | 無 | **有 (3/4"×50)** |
| 有 J (hole) 欄 | 無 | **有 (Ø22)** |
| B/D/G 配置 | 與 Type 43 類似 | C100 有 B, C125/C150 有 D+G |

> Type 45 比 Type 44 多 J/K 欄——因為 Type 45 有 Lug Plate 螺栓連接。

---

## Member 選型圖表（D-55）

MIN. CHANNEL REQUIRED — LINE SIZE × LENGTH "H" 雙軸圖形判讀：

| LINE SIZE | H ≤ ~850 | H ~850~1250 | H ≥ 1250 |
|:---:|:---:|:---:|:---:|
| 8" | C100 | C100 | C100 |
| 10" | C100 | C125 | C125 |
| 12" | C125 | C125 | C150 |
| 14" | C150 | C150 | C150 |

> ⚠️ 以上為圖形判讀近似值，精確分界請查原圖 D-55。

---

## 編碼格式（NOTE 1）

**格式**: `45-{N}-{M}-{H} {A|B}[-{Q}]`

```
45-8B-C100-840 A OR B-175
│  │   │    │   │      └─ MODIFY DIMENSION Q (mm), SEE NOTE 2
│  │   │    │   └──────── A: θ=30°, B: θ=45°
│  │   │    └──────────── LENGTH "H" (mm)
│  │   └───────────────── MEMBER SIZE (C100/C125/C150)
│  └───────────────────── SUPPORTED LINE SIZE
└──────────────────────── TYPE NO.
```

---

## 工程 NOTES（原圖標註）

1. **DESIGNATION**: 如上述編碼格式
2. **A: FOR θ = 30°, B: FOR θ = 45°**

---

## BOM（材料清單）

| # | 品名 | 說明 |
|:---:|------|------|
| 1 | Channel Member | C100/C125/C150，依管徑+H 選型 |
| 2 | L50×50×6 斜撐 | θ=30°: 1008mm / θ=45°: 1150mm。**H > 1140 時才安裝** |
| 3 | Lug Plate (Detail Y) Type-D/E | M-35/36，Vessel 端接合 |
| 4 | Lug Plate (Detail Z) Type-C | M-34，管線端 clamp |
| 5 | PLATE 90×45×6 | 端板 |
| 6 | C100×50×5 座板 | Vessel 接觸端 |
| 7 | 5/8"×40 M.B. + Nut | Ø19 孔，Detail Y 螺栓 |
| 8 | 3/4"×50 M.B. + Nut | ØJ=22 孔，Detail Z 螺栓 (K) |
| 9 | 1/2"×30 M.B. + Nut | Ø16 孔，端板螺栓 |
| 10 | 6mm 焊接 | TYP. 全焊 |

---

## 設計流程

```
1. 確定: LINE SIZE (8"/10"/12"/14"), Vessel R, P, 保溫 t
2. 查表 1: LINE SIZE → Q
3. 計算 H = P - √(R² - Q²) - 60 - t
4. 選 Channel Member (依管徑+H, 查圖表)
5. 選 θ (30° 或 45°)
6. 判斷斜撐: H > 1140 → 裝 L50×50×6 (1008 or 1150mm)
             H ≤ 1140 → 不裝斜撐
7. Lug Plate 選型:
   - Detail Y (Vessel 端): θ=30° → M-36 (Type-E), θ=45° → M-35 (Type-D)
   - Detail Z (管線端): M-34 (Type-C)
8. 查表 2: Member → A, B/D, C, E, F, G, J, K
9. 編碼: 45-{N}-{M}-{H} {A|B}[-{Q}]
```

---

## 關聯 Type

| 關聯 Type | 關係 |
|------|------|
| Type 44 | 同為無 Trunnion Vessel 支撐，但 44 無 clamp、無保溫修正。45 = 44 + clamp + 保溫 |
| Type 43 | 同為 clamp 支撐，但 43 有 Trunnion + 適用 2"~24"。45 = 43 去掉 Trunnion、限 8"~14" |
| Type 42 | 同為 Vessel 斜撐，但 42 用 Trunnion、無 clamp |
| M-34 | Lug Plate Type-C，Detail Z（管線端 clamp）|
| M-35 | Lug Plate Type-D (45°)，Detail Y 當 θ=45° 時 |
| M-36 | Lug Plate Type-E (60°補償)，Detail Y 當 θ=30° 時 |

### 完整比較：Type 42 / 43 / 44 / 45

| | Type 42 | Type 43 | Type 44 | **Type 45** |
|------|---------|---------|---------|---------|
| 接 Vessel | Trunnion | Trunnion | 直接 | **直接** |
| 管線固定 | 承托 | clamp | 承托 | **clamp** |
| H 公式 | F−√(R²−E²) | K−√(R²−Q²)−t−E−30 | P−√(R²−Q²) | **P−√(R²−Q²)−60−t** |
| Trunnion | 需要 | 需要 | 不需要 | **不需要** |
| Lug Plate | 無 | M-34+M-35/36 | 無 | **M-34+M-35/36** |
| 保溫修正 | 未明確 | 扣 t | 無 | **扣 t** |
| 管徑範圍 | 2"~24" | 2"~24" | 8"~14" | **8"~14"** |
| 斜撐條件 | 全裝 | 全裝 | H≥1200 | **H>1140** |
| 約束程度 | 僅支撐 | 全約束 | 僅支撐 | **全約束** |
| Detail Y | — | 管線端 M-34 | — | **Vessel端 M-35/36** |
| Detail Z | — | Vessel端 M-35/36 | — | **管線端 M-34** |
