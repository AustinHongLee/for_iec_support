# Type 67 — 夾持式隔離管鞍座 Clamped Pipe Shoe with Gasket Isolation

> **圖號**: 67 &nbsp;|&nbsp; **分類**: 支撐型式（管線介面層） &nbsp;|&nbsp; **狀態**: ✅ 已實作
> **圖面編號**: E1906-DSP-500-006 &nbsp;|&nbsp; **圖面頁**: D-81 (1/2), D-81A (2/2)
> **日期**: 12/12/19

**夾持式隔離管鞍座（Clamped Pipe Shoe with Gasket Isolation）**——在 TYPE-66 管鞍座基礎上，加入 **Pipe Clamp** 和 **Non-Asbestos Gasket**，形成完整的管線夾持固定系統。
適用 **1/2"~42"** 全管徑。專為 **Alloy Steel / Stainless Steel** 管線設計（MAX. 750°F）。
是 TYPE-54 圖面標註 "DETAIL SEE D-81" 的實體定義。

> **本型不是支撐骨架，而是「管線↔支撐」之間的夾持隔離介面層。**
> TYPE-66（D-80）= 純鞍座介面；TYPE-67（D-81）= 鞍座 + Clamp + Gasket 隔離介面。

---

## 系統本質

TYPE-67 是 TYPE-66（D-80 Pipe Shoe）的**隔離型夾固版本**：

| 比較 | TYPE-66 (D-80) | **TYPE-67 (D-81)** |
|------|------|------|
| 核心功能 | 鞍座承托 | **鞍座承托 + 夾固 + 隔離** |
| Pipe Clamp | ❌ | **✅** M-4（≤24"）/ M-56（26"~42"） |
| Non-Asbestos Gasket | ❌ | **✅** M-47 |
| Reinforcing Pad | ✅ (optional) | ❌（不適用，Clamp 取代 Pad 的固定功能） |
| 材質限定 | 無 | **AS / SS only**（NOTE 3） |
| 約束類型 | REST（承托） | **FIXED（夾固）** |
| 引用者 | TYPE-46, 47, 52, 53 | **TYPE-54** |

### 為什麼需要 TYPE-67

1. **材料隔離**——SS/AS 管線不可直接接觸 CS 支撐結構（防電偶腐蝕 galvanic corrosion）
2. **固定約束**——Clamp 提供管線全方位固定（不只是承托）
3. **標準化**——將 Shoe + Clamp + Gasket 統一為標準型號系統

> TYPE-66 解決的是「圓管 vs 平面」的幾何問題
> TYPE-67 解決的是「圓管 vs 平面 **+ 材料隔離 + 位置固定**」的複合問題

---

## 系統定位

```
TYPE-66 (D-80): Pipe → [Shoe]                              → Support
TYPE-67 (D-81): Pipe → [Gasket] → [Clamp] → [Shoe]        → Support
```

### D-80 / D-81 平行家族

```
D-80 (TYPE-66): Shoe only            → TYPE 46, 47, 52, 53
D-81 (TYPE-67): Shoe+Clamp+Gasket    → TYPE 54
```

### 分層模型

```
SYSTEM LAYERS:

Pipe
↓
Isolation Layer      → Non-Asbestos Gasket（M-47）
↓
Clamp Layer          → Pipe Clamp（M-4 ≤24" / M-56 26"~42"）
↓
Interface Layer      → Shoe / Saddle（鞍座承托）
↓
Structure Layer      → Member "C" / Base Beam
```

---

## 三種結構型態（依管徑 / 製造方式分級）

| 管徑範圍 | 製造分級 | 圖面 | 特徵 |
|:---:|------|:---:|------|
| **1/2"~8"** | 簡易鞍座 + Clamp | D-81 | 無側板 (B=—)，CUT FROM H-beam，Clamp PCL-A series（M-4） |
| **10"~24"** | 含側板鞍座 + Clamp | D-81 | 有側板 (B=9 or 12)，Member "C"，Clamp PCL-A series（M-4） |
| **26"~42"** | 多件組裝 + Clamp | D-81A | 6 件組裝，16t/12t PLATE，Clamp（M-56），Gasket 1.5t |

> 此分級反映的是**製造方式（fabrication level）**。
> 三種型態的力學行為相同：Shoe 承托 + Clamp 夾固 + Gasket 隔離。

---

## 共通幾何

| 項目 | 值 |
|------|------|
| Gasket | NON-ASBESTOS（M-47） |
| Pipe Clamp（≤24"） | PCL-A-{size}B 系列（SEE M-4） |
| Pipe Clamp（26"~42"） | SEE M-56 |
| HOPS（≤24" 圖示） | 100 |
| LOPS（10"~24" 圖示） | 200（兩側各 50 邊距） |
| 最小邊距 | 25 MIN. (TYP.) |
| 焊接 | 6V TYP. |
| 材質限定 | AS / SS lines（NOTE 3，MAX. 750°F） |

---

## 表 1：主尺寸表（D-81，1/2"~24"）

DIMENSION (mm)

| LINE SIZE | A | B | C (製造來源) | PIPE CLAMP TYPE | D (NOTE 2) |
|:---:|:---:|:---:|------|:---:|:---:|
| 1/2" | 100 | — | CUT FROM H200×100×5.5×8 | PCL-A-1/2B | 80 |
| 3/4" | 100 | — | CUT FROM H200×100×5.5×8 | PCL-A-3/4B | 80 |
| 1" | 100 | — | CUT FROM H200×100×5.5×8 | PCL-A-1B | 80 |
| 1 1/2" | 100 | — | CUT FROM H200×100×5.5×8 | PCL-A-1 1/2B | 80 |
| 2" | 100 | — | CUT FROM H200×100×5.5×8 | PCL-A-2B | 80 |
| 2 1/2" | 100 | — | CUT FROM H200×100×5.5×8 | PCL-A-2 1/2B | 80 |
| 3" | 100 | — | CUT FROM H200×100×5.5×8 | PCL-A-3B | 180 |
| 4" | 100 | — | CUT FROM H200×100×5.5×8 | PCL-A-4B | 180 |
| 5" | 100 | — | CUT FROM H200×100×5.5×8 | PCL-A-5B | 180 |
| 6" | 100 | — | CUT FROM H200×100×5.5×8 | PCL-A-6B | 180 |
| 8" | 100 | — | CUT FROM H200×100×5.5×8 | PCL-A-8B | 180 |
| 10" | 130 | 9 | CUT FROM H200×200×8×12 | PCL-A-10B | — |
| 12" | 130 | 9 | CUT FROM H200×200×8×12 | PCL-A-12B | — |
| 14" | 130 | 9 | CUT FROM H200×200×8×12 | PCL-A-14B | — |
| 16" | 250 | 12 | FAB. FROM 12t PLATE | PCL-A-16B | — |
| 18" | 250 | 12 | FAB. FROM 12t PLATE | PCL-A-18B | — |
| 20" | 250 | 12 | FAB. FROM 12t PLATE | PCL-A-20B | — |
| 24" | 300 | 12 | FAB. FROM 12t PLATE | PCL-A-24B | — |

### 欄位說明

| 欄位 | 說明 |
|:---:|------|
| A | 鞍座基座寬度 (mm) |
| B | 側板厚度 (mm)，1/2"~8" 無側板 |
| C | 製造來源/方法（與 TYPE-66 相同） |
| PIPE CLAMP TYPE | 管夾型號，PCL-A 系列（detail SEE M-4） |
| D (NOTE 2) | LOPS 預設長度 (mm)，10"+ 由設計計算 |

### D 欄（LOPS）分析

| 管徑 | D 值 | 含義 |
|:---:|:---:|------|
| ≤2-1/2" | 80 | 小管徑標準 LOPS |
| 3"~8" | 180 | 中管徑標準 LOPS |
| 10"~24" | — | 由設計計算（NOTE 2） |

> **與 TYPE-66 比較**：TYPE-66 的 D = 150（1/2"~8" 全部一致）。
> TYPE-67 因加入 Clamp 而改為 80/180 分段，分界點在 2-1/2"/3"。

### A / B / C 與 TYPE-66 的對應

TYPE-67 的 A / B / C 欄位值**與 TYPE-66 完全相同**——底層鞍座結構共用。
差異在於 TYPE-67 新增 PIPE CLAMP TYPE 欄位、不同的 D 值、且無 E 欄（TYPE-66 的 E=50 側板高度）。

---

## TABLE "A"：保溫厚度 → HOPS 高度（參照 D-80A）

> **NOTE 4 (D-81)**: REF. SH'T D-80A TABLE "A"

TYPE-67 共用 TYPE-66 的 TABLE "A"，HOPS 由保溫厚度決定。

| INSULATION TH'K (mm) | HEIGHT OF SHOE (HOPS) (mm) | SYMBOL |
|:---:|:---:|:---:|
| 75 & LESSER | 100 | NONE |
| 80 THRU. 125 | 150 | A |
| 130 THRU. 175 | 200 | B |
| 180 THRU. 200 | 220 (NOTE 1) | C |

### ⚠️ 無 TABLE "B"（材質符號）

TYPE-67 **不使用 TABLE "B"**。
原因：本型專為 AS/SS 設計（NOTE 3），材質已隱含，不需額外編碼。
與 TYPE-54 的 designation 一致——無 (P)、無 TABLE B。

---

## 表 2：大管尺寸表（D-81A，26"~42"）

> **FOR PIPE SIZE 26"~42"** — 6 件組裝結構（含 Clamp + Gasket）

### 構件明細

| NO | PIECE (數量) | 說明 | 備註 |
|:---:|:---:|------|------|
| 1 | 2 | 側板 | — |
| 2 | 1 | 底板 (FOOT)，**16 TH'K** | FOOT PLATE |
| 3 | 1 | 鞍座板，**12 TH'K** | PLATE |
| 4 | 4 | 加勁板，**FAB. FROM 12t** | — |
| 5 | 2 | **CLAMP** | **NOTE 3 → SEE SH'T M-56** |
| 6 | 2 | **NON-ASBESTOS GASKET**，**1.5t** | **NOTE 4 → SEE SH'T M-47** |

> **與 TYPE-66 D-80B 差異**：TYPE-66 有 5 件（NO.1~4 + optional Reinforcing Pad NO.5）；
> TYPE-67 有 6 件——無 Reinforcing Pad，改為 NO.5 CLAMP + NO.6 GASKET。

### TYPE-A / TYPE-B 分型（D-81A NOTE 2）

| TYPE | 保溫厚度條件 |
|:---:|------|
| **TYPE-A** | 保溫厚度 ≤ 100mm |
| **TYPE-B** | 保溫厚度 > 100mm 且 ≤ 150mm |

> 影響 FOOT、e、h、H 尺寸（表中 A/B 雙欄）。

### 完整尺寸表

| PIPE SIZE | FOOT A | FOOT B | b | c | e(A) | e(B) | h(A) | h(B) | H(A) | H(B) | L | m |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 26" | 148 | 198 | 430 | 230 | 222 | 272 | 150 | 200 | 480 | 530 | 540 | 35 |
| 28" | 148 | 198 | 440 | 240 | 230 | 280 | 150 | 200 | 506 | 556 | 540 | 35 |
| 30" | 148 | 198 | 450 | 250 | 237 | 287 | 150 | 200 | 531 | 581 | 540 | 35 |
| 32" | 148 | 198 | 460 | 260 | 244 | 294 | 150 | 200 | 556 | 606 | 740 | 40 |
| 36" | 152 | 202 | 500 | 300 | 259 | 309 | 150 | 200 | 607 | 657 | 740 | 40 |
| 40" | 156 | 206 | 535 | 335 | 274 | 324 | 150 | 200 | 658 | 708 | 740 | 40 |
| 42" | 156 | 206 | 550 | 350 | 281 | 331 | 150 | 200 | 683 | 733 | 740 | 40 |

### 欄位說明

| 欄位 | 說明 |
|:---:|------|
| FOOT A/B | 底座尺寸 (mm)，A=TYPE-A, B=TYPE-B |
| b | 鞍座底部寬度 |
| c | 鞍座內部間距 |
| e (A/B) | 鞍座弧面投影高度，A/B 分型 |
| h (A/B) | 側板高度 = HOPS，A=150 / B=200，全部管徑一致 |
| H (A/B) | 鞍座總高度，A/B 分型，隨管徑增大 |
| L | 縱向長度（LOPS 相關） |
| m | 焊接接合段 |

### ℹ️ D-81A vs D-80B 欄位名稱對照（重要）

> D-81A 與 D-80B 使用**不同欄位字母**表示**相同物理量**，數值完全一致：
>
> | 物理量 | D-80B (TYPE-66) | D-81A (TYPE-67) | 26" 值 (A/B) |
> |------|:---:|:---:|:---:|
> | 弧面投影高度 | a | **e** | 222 / 272 |
> | 側板高度 (HOPS) | e | **h** | 150 / 200 |
> | 總高度 | h | **H** | 480 / 530 |
>
> D-81A 無 n 欄（D-80B 的 n=75 端部延伸在 TYPE-67 中不列出）。

### D-81A 分組規律

| 管徑 | FOOT A/B | L | m |
|:---:|:---:|:---:|:---:|
| 26"~30" | 148/198 | 540 | 35 |
| 32" | 148/198 | 740 | 40 |
| 36" | 152/202 | 740 | 40 |
| 40"~42" | 156/206 | 740 | 40 |

> h(A)=150, h(B)=200 全部管徑一致（與 TYPE-66 的 e 值一致）。

### 焊接規格

| 管徑 | 焊接 |
|:---:|------|
| 26"~30" | 6V 120，3 SIDES TYP.，v/3 TYP. |
| 32"~42" | 6V 160，3 SIDES TYP.，v/3 TYP. |

### 荷重條件（D-81A NOTE 6）

> **LOADING CONDITION**: CARBON STEEL SADDLE WITH MAX. PIPE TEMPERATURE **700°F**

---

## 編碼格式（Designation）

### D-81 格式（1/2"~24"）

**格式**: `67-{size}B-{TABLE_A}-{HOPS}-{LOPS}`

```
67-3/4B-A-130-500
│  │    │  │    └─ MODIFY LOPS (mm) IF ANY
│  │    │  └────── MODIFY HOPS (mm) IF ANY
│  │    └───────── SEE NOTE 4 → D-80A TABLE "A" 符號 (NONE/A/B/C)
│  └────────────── LINE SIZE
└───────────────── TYPE NO.
```

### D-81A 格式（26"~42"）

**格式**: `67-{size}B-{insul_type}-{HOPS}-{LOPS}`

```
67-30B-A-130-500
│  │  │  │    └─ MODIFY LOPS (mm) IF ANY
│  │  │  └────── MODIFY HOPS (mm) IF ANY
│  │  └───────── SEE NOTE 2: A=保溫≤100, B=保溫>100≤150
│  └───────────── LINE SIZE
└──────────────── TYPE NO.
```

### ⚠️ 與 TYPE-66 Designation 的差異

| 項目 | TYPE-66 (D-80) | **TYPE-67 (D-81)** |
|------|------|------|
| 格式 | `66-{size}{pad/type}-{HOPS}({mat})-{HOPS}-{LOPS}` | **`67-{size}B-{TABLE_A}-{HOPS}-{LOPS}`** |
| (P) Reinf. Pad | ✅ | **❌** |
| TABLE "B" 材質碼 | ✅ NONE/(A)/(S) | **❌**（AS/SS 已隱含） |
| 編碼長度 | 較長 | **較短** |

> TYPE-67 的 designation 結構與 TYPE-54 完全同構：無 (P)、無 TABLE B。

---

## 工程 NOTES 彙整

### D-81 NOTES（1/2"~24"）

| NOTE | 內容 |
|:---:|------|
| 1 | Designation 格式（見上方編碼格式） |
| 2 | LOPS 在有 Pipe Stop 時需另行計算 |
| 3 | 本型通常用於 AS 和 SS 管線（MAX. LINE TEMP.: 750°F） |
| 4 | REF. SH'T D-80A TABLE "A" |
| 5 | HOPS = Height Of Pipe Shoe, LOPS = Length Of Pipe Shoe |

### D-81A NOTES（26"~42"）

| NOTE | 內容 |
|:---:|------|
| 1 | Designation 格式（見上方編碼格式） |
| 2 | TYPE-A: 保溫 ≤100mm, TYPE-B: 保溫 >100mm ≤150mm |
| 3 | Clamp detail SEE SH'T M-56 |
| 4 | Non-Asbestos Gasket SEE SH'T M-47 |
| 5 | 本型通常用於 AS 和 SS 管線（MAX. LINE TEMP.: 750°F） |
| 6 | 荷重條件: CS saddle, MAX PIPE TEMPERATURE 700°F |
| 7 | HOPS = Height Of Pipe Shoe, LOPS = Length Of Pipe Shoe |

---

## 連接方式

### 荷重路徑

```
Pipe（水平管線）
→ NON-ASBESTOS GASKET（M-47，隔離層）
→ PIPE CLAMP（M-4 ≤24" / M-56 26"~42"，夾持）
→ Shoe / Saddle（鞍座承托）
→ Member "C" / Base Beam
```

### 連接形式

| 連接界面 | 方式 |
|------|------|
| Pipe ↔ Gasket | 接觸（壓持） |
| Gasket ↔ Clamp | 夾持（機械連接） |
| Clamp ↔ Shoe | 壓持 / 夾持 |
| Shoe ↔ Member C / Base | 焊接（6V TYP.） |

---

## 約束行為

| 自由度 | 狀態 | 說明 |
|:---:|:---:|------|
| 垂直（↓） | **FIXED** | Shoe 承重 + Clamp 壓持 |
| 垂直（↑） | **FIXED** | Clamp 防止抬起 |
| 軸向（Axial） | **FIXED** | Clamp 夾固 + Gasket 摩擦 |
| 橫向（Lateral） | **FIXED** | Clamp 側向約束 |
| 旋轉 | **FIXED** | Clamp 全包覆約束 |

→ TYPE-67 是 **FIXED SUPPORT**（anchor point）。

> ⚠️ Gasket 的壓縮特性使其不是理論剛體固定（engineering-fixed, not mathematically rigid）。

---

## 構件清單

### 小管 1/2"~8"

| # | 構件 | 規格 / 來源 |
|:---:|------|------|
| 1 | Shoe / Saddle | CUT FROM H200×100×5.5×8 |
| 2 | Non-Asbestos Gasket | M-47 |
| 3 | Pipe Clamp | PCL-A-{size}B（SEE M-4） |
| 4 | Weld | 6V TYP. |

### 中管 10"~24"

| # | 構件 | 規格 / 來源 |
|:---:|------|------|
| 1 | Shoe / Saddle | CUT FROM H200×200×8×12（10"~14"）/ FAB FROM 12t（16"~24"） |
| 2 | 側板 | 厚 B=9（10"~14"）/ B=12（16"~24"） |
| 3 | Member "C" | 底部結構件 |
| 4 | Non-Asbestos Gasket | M-47 |
| 5 | Pipe Clamp | PCL-A-{size}B（SEE M-4） |
| 6 | Weld | 6V, 3 SIDES TYP. |

### 大管 26"~42"

| # | 構件 | 規格 / 來源 |
|:---:|------|------|
| 1 | NO.1 件 ×2 | 側板 |
| 2 | NO.2 件 ×1 | 底板 (FOOT), 16 TH'K |
| 3 | NO.3 件 ×1 | 鞍座板, 12 TH'K |
| 4 | NO.4 件 ×4 | 加勁板, FAB FROM 12t |
| 5 | NO.5 件 ×2 | **CLAMP**（SEE M-56） |
| 6 | NO.6 件 ×2 | **NON-ASBESTOS GASKET**, 1.5t（SEE M-47） |
| 7 | Weld | 6V, 3 SIDES TYP.；120 (26"~30") / 160 (32"~42") |

### 不存在的構件

- Reinforcing Pad（TYPE-66 有，TYPE-67 以 Clamp 取代固定功能）
- Lug Plate
- Trunnion
- U-bolt
- Guide / Retainer

---

## Pipe Clamp 跨尺寸對照

| 管徑範圍 | Clamp 來源 | 型號系統 |
|:---:|:---:|------|
| **1/2"~24"** | **M-4** | PCL-A-{size}B（18 種標準型號） |
| **26"~42"** | **M-56** | 見 M-56 詳圖 |

> PCL-A = Pipe CLamp type A 系列，B = bare（未保溫狀態管徑標識）。

---

## 與 TYPE-54 / TYPE-66 的介面關係

### TYPE-54 ↔ TYPE-67

```
TYPE-54 (D-65): 管線層級配置圖（側邊 L-angle + Clamp 配置）
  ↓ "DETAIL SEE D-81"
TYPE-67 (D-81): Shoe + Clamp + Gasket 詳圖（本型）
```

### TYPE-52/53 ↔ TYPE-66

```
TYPE-52/53 (D-63/64): 管線層級配置圖（側邊 Retainer/Guide 配置）
  ↓ "DETAIL SEE D-80"
TYPE-66 (D-80): Shoe 詳圖（純鞍座）
```

### 平行對照

| 介面層 | 配置層 | 功能 |
|------|------|------|
| TYPE-66 (D-80) | TYPE-46, 47, 52, 53 | 純承托（REST） |
| **TYPE-67 (D-81)** | **TYPE-54** | **隔離夾固（FIXED + ISOLATED）** |

---

## 設計流程

```
1. 確定: LINE SIZE (1/2"~42"), 管材 (AS/SS), 保溫厚度
2. 確認材質適用性: 本型僅用於 AS/SS (NOTE 3, MAX. 750°F)
3. 選結構型態:
   - ≤8" → 簡易鞍座 + Clamp (D-81)
   - 10"~24" → 含側板鞍座 + Clamp (D-81)
   - 26"~42" → 多件組裝 + Clamp (D-81A)
4. 查 TABLE "A" (D-80A): 保溫厚度 → HOPS + 符號
   (26"~42" 另查 NOTE 2: TYPE-A or TYPE-B)
5. 查主尺寸表:
   - ≤24" → 表 1 (D-81)
   - 26"~42" → 表 2 (D-81A)
6. 選 Pipe Clamp: PCL-A-{size}B (≤24") 或查 M-56 (26"~42")
7. 配 Non-Asbestos Gasket (M-47)
8. 計算 LOPS (有 Pipe Stop 時另行計算, NOTE 2)
9. 編碼: 67-{size}B-{A/B/C/NONE}-{HOPS}-{LOPS}
```

---

## 關聯 Type

| 關聯 Type | 關係 |
|------|------|
| **Type 54** | D-65 標註 "DETAIL SEE D-81"——Type 54 使用本型作為 Shoe+Clamp+Gasket 介面 |
| **Type 66** | D-80——本型的鞍座結構基礎（A/B/C 欄位共用、TABLE A 共用） |
| M-4 | Pipe Clamp 詳圖（≤24"，PCL-A 系列） |
| M-47 | Non-Asbestos Gasket 詳圖 |
| M-56 | Pipe Clamp 詳圖（26"~42"） |
| D-80A | TABLE "A"（保溫→HOPS）+ TABLE "B"（材質，TYPE-67 不使用） |
