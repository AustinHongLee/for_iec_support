# Type 66 — 管鞍座 Pipe Shoe (Saddle Support Interface)

> **圖號**: 66 &nbsp;|&nbsp; **分類**: 支撐型式（管線介面層） &nbsp;|&nbsp; **狀態**: ✅ 已實作
> **圖面編號**: E1906-DSP-500-006 &nbsp;|&nbsp; **圖面頁**: D-80 (1/3), D-80A (2/3), D-80B (3/3)
> **日期**: 12/12/19

**管鞍座（Pipe Shoe / Saddle）**——管線與支撐結構之間的曲面適配介面層。
包覆角 120°。適用 **1/2"~42"** 全管徑。三種結構型態按管徑分組。
是 Type 46 / Type 47 圖面標註 "DETAIL SEE D-80 (TYP.)" 的實體定義。

> **本型不是支撐骨架，而是「管線↔支撐」之間的介面層。**
> 正確的荷重路徑為：Pipe → Shoe (Type 66) → Support Structure (Type 44/45/46/47 etc.)

---

## 系統定位

```
原始模型: Pipe → Support
正確模型: Pipe → Shoe (Type 66) → Support

TYPE-46 / TYPE-47 的 "DETAIL SEE D-80 (TYP.)" = 本型 (Type 66)
```

### 為什麼需要 Pipe Shoe

- 管線是**圓的**，支撐結構是**平的**
- 直接接觸 → 線接觸 → 應力集中
- Shoe（120° 鞍座）→ **面接觸** → 應力分散

---

## 三種結構型態（依管徑 / 製造方式分級）

| 管徑範圍 | 製造分級 | 特徵 |
|:---:|------|------|
| **1/2"~8"** | 簡易鞍座 | 無側板 (B=—)，直接 saddle + plate |
| **10"~24"** | 含側板鞍座 | 有側板 (B=9 or 12)，有 Member "C"，有 Reinforcing Pad |
| **26"~42"** | 多件組裝鞍座 | 5 件組裝，16mm PLATE + 12mm PAD，TYPE-A/B 保溫分型 |

> ℹ️ 此分級反映的是**製造方式（fabrication level）**，不是力學行為分類。
> 三種型態的力學行為相同：120°鞍座提供面接觸承托，將線接觸轉為面接觸。

---

## 共通幾何

| 項目 | 值 |
|------|------|
| 包覆角 | **120°** |
| Ø6 WEEP HOLE | Reinforcing Pad 上（排水/排氣用） |
| 最小邊距 | 25 MIN. (TYP.) |
| Field Weld | SEE NOTE 7（D-80A 定義） |

---

## 表 1：主尺寸表（D-80，1/2"~24"）

DIMENSION (mm)

| LINE SIZE | A | B | C (NOTE 1) | D (NOTE 4) | E |
|:---:|:---:|:---:|------|:---:|:---:|
| 1/2" | 100 | — | | 150 | — |
| 3/4" | 100 | — | | 150 | — |
| 1" | 100 | — | | 150 | — |
| 1 1/2" | 100 | — | | 150 | — |
| 2" | 100 | — | | 150 | 50 |
| 2 1/2" | 100 | — | CUT FROM H-200×100×5.5×8 | 150 | 50 |
| 3" | 100 | — | CUT FROM H-200×100×5.5×8 | 250 | 50 |
| 4" | 100 | — | CUT FROM H-200×100×5.5×8 | 250 | 50 |
| 5" | 100 | — | | 250 | 50 |
| 6" | 100 | — | | 250 | 50 |
| 8" | 100 | — | | 250 | 50 |
| 10" | 130 | 9 | CUT FROM H-200×200×8×12 | — | 50 |
| 12" | 130 | 9 | CUT FROM H-200×200×8×12 | — | 50 |
| 14" | 130 | 9 | | — | 50 |
| 16" | 250 | 12 | FAB. FROM 12^t PLATE | — | 50 |
| 18" | 250 | 12 | FAB. FROM 12^t PLATE | — | 50 |
| 20" | 250 | 12 | FAB. FROM 12^t PLATE | — | 50 |
| 24" | 300 | 12 | FAB. FROM 12^t PLATE | — | 50 |

### 欄位說明

| 欄位 | 說明 |
|:---:|------|
| A | 鞍座基座寬度 (mm) |
| B | 側板厚度 (mm)，1/2"~8" 無側板 |
| C (NOTE 1) | 製造來源/方法 |
| D (NOTE 4) | LOPS 預設長度 (mm)，10"+ 由設計計算 |
| E | 側板高度 (mm)，2"+ = 50mm |

### 製造來源分組

| 管徑 | 板厚 (NOTE 1) | 來源 |
|------|:---:|------|
| ≤1 1/2" | 6^t PLATE | 薄板彎製 |
| 2"~14" | 9 PLATE | H 型鋼切割或 9mm 板 |
| 16"~24" | 12 PLATE | 12mm 板製造 |

> **NOTE 1**: SHOES FOR PIPES 1 1/2" & SMALLER MAY BE FABRICATED FROM 6^t PLATE,
> 2" THRU. 14" FROM 9 PLATE, 16" THRU. 24" FROM 12 PLATE

> **NOTE 4**: LONGITUDINAL LENGTH OF PIPE SHOE (SAY LOPS) SHALL BE CALCULATED IN THE CASE WITH PIPE STOP.
> （10"+ 的 LOPS 由 Pipe Stop 工況計算決定，不是固定值）

---

## TABLE "A"：保溫厚度 → HOPS 高度（D-80A）

| INSULATION TH'K (mm) | HEIGHT OF SHOE (HOPS) (mm) | SYMBOL |
|:---:|:---:|:---:|
| 75 & LESSER | 100 | NONE |
| 80 THRU. 125 | 150 | A |
| 130 THRU. 175 | 200 | B |
| 180 THRU. 200 | 220 (NOTE 1) | C |

> 保溫越厚 → Shoe 越高，確保保溫層不被壓迫。
> HOPS = Height Of Pipe Shoe。

---

## TABLE "B"：材質分類（D-80A）

| MAT'L OF SHOES | FABRICATED FROM (NOTE 1) | SYMBOL |
|------|------|:---:|
| CARBON STEEL | SHAPE STEEL OR C/S PLATE | NONE |
| ALLOY STEEL | A/S PLATE | (A) |
| STAINLESS STEEL | S/S PLATE | (S) |

> **NOTE 3** (D-80): FOR PADS MATERIAL USE PIPE MATERIAL THAT CUT FROM THE PIPE OR EQUIVALENT TO THE PIPE.
> （Reinforcing Pad 材料 = 管材或同等材料）

---

## Field Weld 焊接規格（D-80A NOTE 7）

四種管徑分組的焊接方式：

### 1/2"~2"（最小管）

| 條件 | 焊腳 W |
|------|:---:|
| PIPE SCH. 80 & BELOW | 4 |
| PIPE SCH. 160 & ABOVE | 6 |

焊長 50~100mm。

### 2 1/2"~8"

6V 焊接，焊長 50~100mm。

### 10"~24"

6V 焊接，**3 SIDES TYP.**（三面焊），焊長 50~100mm。

### 26"~42"

6V 焊接，**3 SIDES TYP.**（三面焊），焊長 50~100mm。含額外的上方結構焊接。

---

## 表 2：大管鞍座尺寸（D-80B，26"~42"）

> **FOR PIPE SIZE 26"~42"** — 5 件組裝結構
> PLATE = 16 TH'K, PAD = 12 TH'K（全部管徑）

### 構件明細

| NO | PIECE (數量) | 說明 |
|:---:|:---:|------|
| 1 | 2 | 側板 |
| 2 | 1 | 底板 (NOTE 4, FOOT) |
| 3 | 1 | 鞍座弧面，**PLATE 16 TH'K** |
| 4 | 4 | 加勁板，**PLATE 12 TH'K** |
| 5 | 1 | Reinforcing PAD，**12 TH'K (MIN.)**，**(OPTION)** |

### TYPE-A / TYPE-B 分型（D-80B NOTE 2）

| TYPE | 保溫厚度條件 |
|:---:|------|
| **TYPE-A** | 保溫厚度 ≤ 100mm |
| **TYPE-B** | 保溫厚度 > 100mm 且 ≤ 150mm |

> 影響 FOOT、a、e、h 尺寸（表中 A/B 雙欄）。

### 完整尺寸表

| PIPE SIZE | FOOT A | FOOT B | b | c | a(A) | a(B) | e(A) | e(B) | h(A) | h(B) | L | m | n |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 26" | 148 | 198 | 430 | 230 | 222 | 272 | 150 | 200 | 480 | 530 | 540 | 35 | 75 |
| 28" | 148 | 198 | 440 | 240 | 230 | 280 | 150 | 200 | 506 | 556 | 540 | 35 | 75 |
| 30" | 148 | 198 | 450 | 250 | 237 | 287 | 150 | 200 | 531 | 581 | 540 | 35 | 75 |
| 32" | 148 | 198 | 460 | 260 | 244 | 294 | 150 | 200 | 556 | 606 | 740 | 40 | 75 |
| 36" | 152 | 202 | 500 | 300 | 259 | 309 | 150 | 200 | 607 | 657 | 740 | 40 | 75 |
| 40" | 156 | 206 | 535 | 335 | 274 | 324 | 150 | 200 | 658 | 708 | 740 | 40 | 75 |
| 42" | 156 | 206 | 550 | 350 | 281 | 331 | 150 | 200 | 683 | 733 | 740 | 40 | 75 |

### 欄位說明

| 欄位 | 說明 |
|:---:|------|
| FOOT A/B | 底座尺寸 (mm)，A=TYPE-A, B=TYPE-B |
| b | 鞍座底部寬度 |
| c | 鞍座內部間距 |
| a (NOTE 2,4) | 鞍座弧面投影高度，A/B 分型。基於 12mm REINF. PAD 計算 |
| e (NOTE 2) | 側板高度，A/B 分型 |
| h (NOTE 2) | 總高度，A/B 分型 |
| L | 縱向長度 (LOPS 相關) |
| m | 焊接接合段 |
| n | 端部延伸 |

> **NOTE 4** (D-80B): DIMENSION "a" & "e" ARE CALCULATED BASE ON PIPE SHOE WITH 12 mm TH'K REINF. PAD.

### ℹ️ 欄位判讀說明（重要）

> D-80B 表頭結構複雜，容易混淆。以下是欄位對應數值的工程判斷：
>
> - **e(A)=150, e(B)=200**：全部管徑一致。與 TABLE "A" 的 HOPS 值 (150=A, 200=B) 對應，合理為側板高度。
> - **h(A)=480~683, h(B)=530~733**：隨管徑增大而增長。合理為鞍座總高度（含管徑、側板、底板）。
> - 26" 管 OD ≈ 660mm，若 h 只有 150mm 在工程上不合理。
>
> ❗ GPT 有一版分析將 h 讀為 150/200、另一組數值讀為 "a_right"，**該判讀不採用**。

### D-80B 分組規律

| 管徑 | FOOT A/B | L | m |
|:---:|:---:|:---:|:---:|
| 26"~30" | 148/198 | 540 | 35 |
| 32" | 148/198 | 740 | 40 |
| 36" | 152/202 | 740 | 40 |
| 40"~42" | 156/206 | 740 | 40 |

> e(A)=150, e(B)=200 全部管徑一致。
> n=75 全部管徑一致。

### D-80B 荷重條件（NOTE 3）

> **LOADING CONDITION**: CARBON STEEL SADDLE WITH MAX. PIPE TEMPERATURE **700°F** & PRESSURE **300 PSI**.

---

## 編碼格式

### D-80 格式（1/2"~24"）

**格式**: `66-{size}{pad}-{HOPS_sym}({material_sym})-{HOPS}-{LOPS}`

```
66-1 1/2B(P)-A(A)-130-500
│  │       │  │ │   │    └─ MODIFY LOPS (mm) IF ANY
│  │       │  │ │   └────── MODIFY HOPS (mm) IF ANY
│  │       │  │ └─────────── TABLE "B" 材質符號: NONE/A/S
│  │       │  └───────────── TABLE "A" HOPS 符號: NONE/A/B/C
│  │       └──────────────── (P) = REINFORCING PAD REQ'D
│  └──────────────────────── LINE SIZE
└─────────────────────────── TYPE NO.
```

### D-80B 格式（26"~42"）

**格式**: `66-{size}{insul_type}-{?}({material_sym})-{HOPS}-{LOPS}`

```
66-28B-A(A)-130-500
│  │  │  │ │   │    └─ MODIFY LOPS (mm) IF ANY
│  │  │  │ │   └────── MODIFY HOPS (mm) IF ANY
│  │  │  │ └─────────── TABLE "B" 材質符號
│  │  │  └───────────── (未明確標註)
│  │  └──────────────── NOTE 2: A=保溫≤100, B=保溫>100≤150
│  └─────────────────── LINE SIZE
└────────────────────── TYPE NO.
```

---

## HOPS / LOPS 定義（NOTE 5）

| 縮寫 | 全名 | 意義 |
|:---:|------|------|
| **HOPS** | Height Of Pipe Shoe | 鞍座高度 (垂直方向) |
| **LOPS** | Length Of Pipe Shoe | 鞍座長度 (管軸方向) |

> LOPS 在有 Pipe Stop 的工況下需另行計算（NOTE 4）。
> HOPS 由保溫厚度決定（TABLE "A"）。

**計算優先序**：designation 末段若明確給出 `HOPS` / `LOPS`，必須優先於 D-80 表格/預設值。
例如 `66-1/2B(P)-A-150-200` 使用 `HOPS=150`, `LOPS=200`；未給修改值時才使用 D-80 表格/預設尺寸。

---

## 工程 NOTES 彙整

### D-80 NOTES（FOR SH'T D-80, 80A ONLY）

| NOTE | 內容 |
|:---:|------|
| 1 | Shoe 板厚: ≤1-1/2"用 6^t, 2"~14"用 9, 16"~24"用 12 |
| 2 | Designation 格式（見上方編碼格式） |
| 3 | Pad 材料 = 管材或同等材料 |
| 4 | 有 Pipe Stop 時，LOPS 需另行計算 |
| 5 | HOPS=Height, LOPS=Length |
| 6 | 材料規格見 SH'T P-2 |
| 7 | Field Weld（見上方焊接規格） |

### D-80B NOTES（FOR SH'T D-80B ONLY）

| NOTE | 內容 |
|:---:|------|
| 1 | Designation 格式（D-80B 版） |
| 2 | TYPE-A: 保溫 ≤100mm, TYPE-B: 保溫 >100mm ≤150mm |
| 3 | 荷重條件: CS saddle, MAX 700°F & 300 PSI |
| 4 | a 和 e 尺寸基於 12mm REINF. PAD 計算 |
| 5 | HOPS=Height, LOPS=Length |

---

## 幾何語意（工程運算層）

### HOPS（Height of Pipe Shoe）

HOPS 不是固定尺寸，而是由以下條件決定：

- **保溫厚度**（TABLE A）→ 直接查表
- Pipe OD → 影響鞍座最小高度
- 淨空要求（clearance）

→ HOPS ≈ f(insulation, OD, clearance)

### LOPS（Length of Pipe Shoe）

LOPS 分兩種情況：

| 條件 | LOPS 來源 |
|------|------|
| 無 Pipe Stop | 使用表值（D 欄，僅 ≤8"） |
| 有 Pipe Stop | **必須重新計算**（NOTE 4） |

→ LOPS ≈ f(load, friction, stop condition)

### e（側板高度）

- 主要作用為 structural stiffener
- 與保溫等級直接對應（TYPE-A: e=150 / TYPE-B: e=200）

### h（總高度）

- 包含: pipe 半徑 + shoe 弧面 + pad + plate + 側板
- 必須隨 pipe size 增加（480~733mm for 26"~42"）

---

## BOM（材料清單概要）

### 小管 1/2"~8"

| # | 品名 | 說明 |
|:---:|------|------|
| 1 | 鞍座本體 | 120° 弧形，依管徑板厚不同 |
| 2 | 底板 | 寬 A=100mm |
| 3 | Reinforcing Pad (optional) | Ø6 WEEP HOLE，材料同管材 |
| 4 | Field Weld | W=4(SCH≤80) / W=6(SCH≥160) |

Calculator rule for the D-80 shared core:

```text
Pad (if P):
  width = OD*pi/3  (practical calculation warning)
  length = LOPS + E*2
  thickness = pipe SCH10S wall

Member C:
  width = A or member C width
  length = LOPS or D
  height = HOPS or 100
```

### 中管 10"~24"

| # | 品名 | 說明 |
|:---:|------|------|
| 1 | 鞍座本體 | 120° 弧形 |
| 2 | 側板 | 厚 B=9(10"~14") / B=12(16"~24")，高 E=50 |
| 3 | Member "C" | 底部結構件 |
| 4 | Reinforcing Pad | Ø6 WEEP HOLE |
| 5 | Field Weld | 6V, 3 SIDES TYP. |

Calculator rule for the D-80 shared core:

```text
Pad (if P):
  width = OD*pi/3  (practical calculation warning)
  length = LOPS + E*2 + 25*2
  thickness = pipe SCH10S wall

Member C, 10"~14":
  width = A + 35*2, or member C width when using H200x200x8
  length = LOPS + 25*2
  height = HOPS or 100

Member C, 16"~24":
  fabricated from 12t flat bar
  width = A
  length = LOPS + 25*2
  height = HOPS or 100

Reinforcing flat bar, 10"~24":
  quantity = 4
  thickness = B
  height = HOPS (calculation only, not fabrication height)
  width = A
```

### 大管 26"~42"

| # | 品名 | 說明 |
|:---:|------|------|
| 1 | NO.1 件 ×2 | 側板 |
| 2 | NO.2 件 ×1 | 底板 (16 TH'K), FOOT |
| 3 | NO.3 件 ×1 | 鞍座弧面 (16 TH'K) |
| 4 | NO.4 件 ×4 | 加勁板 (12 TH'K) |
| 5 | NO.5 件 ×1 **(OPTION)** | 頂部蓋板 |
| 6 | PAD 12 TH'K (MIN.) | Reinforcing Pad **(OPTION)** |
| 7 | Field Weld | 6V, 3 SIDES TYP. |

---

## 設計流程

```
1. 確定: LINE SIZE (1/2"~42"), 管材, 保溫厚度
2. 選結構型態:
   - ≤8" → 簡易鞍座 (D-80)
   - 10"~24" → 含側板鞍座 (D-80)
   - 26"~42" → 多件組裝 (D-80B)
3. 查 TABLE "A" (D-80A): 保溫厚度 → HOPS + 符號
   (26"~42" 另查 NOTE 2: TYPE-A or TYPE-B)
4. 查 TABLE "B" (D-80A): 管材 → 材質符號
5. 查主尺寸表:
   - ≤24" → 表 1 (D-80)
   - 26"~42" → 表 2 (D-80B)
6. 計算 LOPS (有 Pipe Stop 時另行計算)
7. 確認 Reinforcing Pad 需求
8. 選焊接方式 (NOTE 7)
9. 編碼
```

---

## 關聯 Type

| 關聯 Type | 關係 |
|------|------|
| **Type 46** | D-56 標註 "DETAIL SEE D-80 (TYP.)"——Type 46 使用本型作為管線接口 |
| **Type 47** | D-57 標註 "DETAIL SEE D-80 (TYP.)"——Type 47 同時使用本型 + Lug Plate |
| Type 44 | 無 D-80 參照（管線直接靠） |
| Type 45 | 無 D-80 參照（用 Lug Plate clamp） |
| M-34 | Lug Plate TYPE-C（Type 47 的管線端，本型之上） |
| M-35/36 | Lug Plate TYPE-D/E（Type 47 的 Vessel 端） |

### D-80 在系統中的角色（分層模型）

```
SYSTEM LAYERS:

Pipe
↓
Interface Layer      → TYPE-66 Shoe（曲面適配 + 荷重分散）
↓
Connection Layer     → Lug Plate / Clamp / Weld（M-34, M-35/36 等）
↓
Structure Layer      → Type 44~47（支撐骨架）
↓
Support Base         → Vessel / Steel / GRADE
```

### 各 Type 的分層組合

```
Type 44: Pipe → [直接]                         → Structure → Vessel
Type 45: Pipe → [Lug Plate]                    → Structure → Vessel
Type 46: Pipe → [Shoe D-80]                     → Structure → Vessel
Type 47: Pipe → [Shoe D-80] → [Lug Plate]       → Structure → Vessel
Type 48: Pipe → [weld]                          → Plate → GRADE
```

> Type 66 (D-80) 是 Type 46/47 的**介面層**，不是獨立的支撐骨架。
> 它解決了「圓管 vs 平面」的幾何不兼容問題。
