# TYPE-52 — Pipe Shoe Support with Lateral Retaining（帶側限位的 Shoe 承托支撐）

| 項目 | 內容 |
|------|------|
| 圖號 | D-63 |
| 管徑 | 1/2"~24" |
| 分類 | Pipe Shoe Support with Lateral Restraint |
| 圖面數 | 1 頁 |
| 圖面編號 | E1906-DSP-500-006 |
| 狀態 | ✅ 已實作 |

---

## 系統本質

TYPE-52 是**帶側向限位的 Pipe Shoe 支撐架**——以 TYPE-66（D-80）的 120° 鞍座為核心，
兩側加裝 L40×40×5 角鐵作為側向擋板，焊接於 base 上。

它不是純 shoe（TYPE-66），不是純承托（TYPE-51），而是：

> **D-80 Shoe + L-angle 側限位框架 = 完整的梁上支撐架**

主功能是承重，附功能是**控制橫向位移**——讓管線可以軸向熱膨脹，但不能橫向亂跑。

---

## 與 TYPE-51 / TYPE-66 的本質差異

| 比較項 | TYPE-51 | TYPE-52 | TYPE-66 |
|------|------|------|------|
| 角色 | 自成一體的承托 | **Shoe + 側限位框架** | 介面層（Shoe 本體） |
| 鞍座來源 | 自己設計（80° for 大管） | **引用 D-80**（120°） | 自身即 D-80 |
| 側向約束 | LIMITED（gap 鬆約束） | **RESTRAINED**（L-angle 擋板） | 無（純介面） |
| 獨立使用 | ✅ | ✅ | ❌（需搭配上層 Type） |
| 材質編碼 | 無 | **有**（D-80A TABLE A+B） | 有（自身定義） |
| HOPS/LOPS | 無（用 H 值） | **有**（繼承 D-80 系統） | 有（自身定義） |

---

## 兩種結構型態（依管徑 / 製造方式分級）

| 管徑範圍 | 結構型態 | 特徵 |
|:---:|------|------|
| **1/2"~8"** | 簡易 Shoe + 側擋 | L40×40×5 兩側，無底板補強 |
| **10"~24"** | 完整 Shoe + 底板 + 側擋 | L40×40×5 兩側 + **PL 12t** 底板補強 |

> 此分級反映**荷重等級差異**：大管需要更強的承托結構。

---

## 幾何關鍵參數

| 參數 | 值 | 說明 |
|:---:|:---:|------|
| Saddle 包覆角 | **120°** | 來自 D-80（TYPE-66），非 TYPE-52 自身定義 |
| 側邊間隙 | 3 mm（TYP.） | 兩側各 3mm，允許熱膨脹、避免卡死 |
| 側邊角鐵 | L40×40×5 | 兩個 size group 相同，CUT IN FIELD |
| 底板（10"~24"） | PL 12t | 12mm 厚鋼板底座 |
| 焊接 | 5V TYP. | 全焊接連接（比 TYPE-51 的 6V 小一號） |
| 底板寬度（10"~24"） | 25 + 100 + 25 = 150mm | 受 NOTE 2 約束（≤ beam width） |

---

## Shoe 設計來源（DETAIL SEE D-80）

TYPE-52 的鞍座**不是自己設計的**——兩個 size group 的右側 detail 都標註：

```
DETAIL SEE D-80
```

即 TYPE-52 的 shoe 幾何、HOPS、LOPS、材質、保溫等級全部來自 TYPE-66（D-80/D-80A）。

### D-80A TABLE "A"（保溫 → HOPS 符號）

| 保溫厚度 (mm) | HOPS (mm) | 符號 |
|:---:|:---:|:---:|
| 75 & LESSER | 100 | NONE |
| 80 THRU. 125 | 150 | A |
| 130 THRU. 175 | 200 | B |
| 180 THRU. 200 | 220 (NOTE 1) | C |

### D-80A TABLE "B"（材質符號）

| 材質 | 符號 |
|:---:|:---:|
| CARBON STEEL | NONE |
| ALLOY STEEL | (A) |
| STAINLESS STEEL | (S) |

> TYPE-52 的 designation 直接引用這兩個 TABLE——
> 這是與 TYPE-51（無材質編碼）的核心差異之一。

---

## 連接方式

TYPE-52 **全部為焊接**，無任何螺栓/夾具：

| 連接 | 方式 |
|------|------|
| Pipe ↔ Shoe | 焊接（D-80 NOTE 7 定義） |
| Shoe ↔ Base | 焊接 |
| L-angle ↔ Base | 焊接（5V TYP.） |
| PL 12t ↔ Base（10"~24"） | 焊接 |

---

## 約束行為

| 自由度 | 狀態 | 說明 |
|:---:|:---:|------|
| 垂直（↓） | **SUPPORTED** | Shoe 承重，管線靠自重坐穩 |
| 垂直（↑） | **FREE** | 無 clamp，管線可被抬起 |
| 軸向（Axial） | **PARTIALLY FREE** | 無 bolt/clamp 鎖固，但 shoe 摩擦提供部分阻力 |
| 橫向（Lateral） | **RESTRAINED** | L40×40×5 兩側擋板 + 3mm gap |
| 旋轉 | **LIMITED** | Shoe 120° 包覆提供部分約束 |

→ TYPE-52 本質上是 **REST SUPPORT with LATERAL GUIDE**。
比 TYPE-51 多了明確的側向限位功能。

> **核心行為：「可軸向滑動，不可橫向偏移」**

---

## Load Path（荷重路徑）

### 8" & Smaller

```
Pipe（水平）
→ Shoe（120°, D-80）
→ L40×40×5 側擋（lateral restraint）
→ Base Beam
```

### 10"~24"

```
Pipe（水平）
→ Shoe（120°, D-80）
→ PL 12t 底板
→ L40×40×5 側擋（lateral restraint）
→ Base Beam
```

---

## 構件清單

### 1/2"~8"（簡易型）

| # | 構件 | 規格 |
|:---:|------|------|
| 1 | Pipe Shoe | 120° 鞍座（DETAIL SEE D-80） |
| 2 | L-angle ×2 | L40×40×5, CUT IN FIELD |
| 3 | Reinforcing Pad | 依需求（designation 中用 (P) 標記） |
| 4 | Weld | 5V TYP. |

目前 calculator 會把 `Pad_52Type` 的公式來源寫入 remark：

```text
width = OD*pi/3
<10": length = D + 25*2
>=10": length = E*2 + 25*2 + 250
```

### 10"~24"（補強型）

| # | 構件 | 規格 |
|:---:|------|------|
| 1 | Pipe Shoe | 120° 鞍座（DETAIL SEE D-80） |
| 2 | Base Plate | PL 12t，寬 150mm（25+100+25） |
| 3 | L-angle ×2 | L40×40×5, CUT IN FIELD |
| 4 | Reinforcing Pad | 依需求（designation 中用 (P) 標記） |
| 5 | Weld | 5V TYP. |

`FB_52Type_3` 僅在 10" 以上出現，目前以：

```text
length = HOPS
width = A + 35/2 - member_t/2
qty = 4
```

其中 length 仍標記為 `pending precision check`。

### 不存在的構件

- Bolt / Nut
- Clamp
- Lug Plate
- Trunnion
- Brace（斜撐）

---

## Designation（編碼格式）

### NOTE 1 格式

```
52-2B(P)-A(A)-130-500
│   │  │   │  │   └── MODIFY LOPS=500 (mm) IF ANY
│   │  │   │  └────── MODIFY HOPS=130 (mm) IF ANY
│   │  │   └───────── SEE SH'T D-80A TABLE "B"（材質符號）
│   │  └───────────── SEE SH'T D-80A TABLE "A"（保溫→HOPS符號）
│   └──────────────── DENOTE REIN. PAD IS REQ'D
└──────────────────── DENOTE LINE SIZE（B=bore）
52 ← DENOTE TYPE NO.
```

### 格式

```
52-{size}B{(P)}-{TABLE_A}{(TABLE_B)}-{HOPS}-{LOPS}
```

其中：
- `{(P)}` = 可選，有 Reinforcing Pad 時加
- `{TABLE_A}` = D-80A TABLE "A" 符號（NONE/A/B/C）
- `{(TABLE_B)}` = D-80A TABLE "B" 符號（NONE/(A)/(S)）
- `{HOPS}` / `{LOPS}` = 可選，有修改值時加

> ⚠️ 此格式與 TYPE-66 的 designation 系統**完全相同**（僅 prefix 52 vs 66）。
> 對照 D-80A NOTE 2: `66-1 1/2B(P)-A(A)-130-500`。

### 範例

| 管徑 | Pad | 保溫 | 材質 | HOPS/LOPS 修改 | Designation |
|:---:|:---:|:---:|:---:|:---:|------|
| 2" | 有 | A級 | AS | HOPS=130, LOPS=500 | 52-2B(P)-A(A)-130-500 |
| 6" | 無 | 無 | CS | 無修改 | 52-6B |
| 12" | 有 | B級 | SS | LOPS=400 | 52-12B(P)-B(S)-400 |
| 3/4" | 無 | A級 | CS | 無修改 | 52-3/4B-A |

---

## NOTES 摘要

| NOTE | 內容 |
|:---:|------|
| 1 | Designation 格式（見上方完整拆解） |
| 2 | **Member 最大長度不得超過 Beam 寬度**（同 TYPE-51 NOTE 2） |
| 3 | HOPS = Height of Pipe Shoe, LOPS = Length of Pipe Shoe |

---

## 設計流程

```
1. 確定: LINE SIZE (1/2"~24"), 管材, 保溫厚度
2. 選結構型態:
   - ≤8" → 簡易型（Shoe + L-angle）
   - 10"~24" → 補強型（Shoe + PL 12t + L-angle）
3. 查 D-80A TABLE "A": 保溫厚度 → HOPS + 符號
4. 查 D-80A TABLE "B": 管材 → 材質符號
5. 確認 Reinforcing Pad 需求
6. 查 D-80 主表: Shoe 尺寸（A/B/C/D/E）
7. 確認 Member 長度 ≤ Beam 寬度（NOTE 2）
8. 如需修改 HOPS/LOPS，加入 designation
9. 編碼: 52-{size}B{(P)}-{TABLE_A}{(TABLE_B)}-{HOPS}-{LOPS}
```

---

## Calculator Handoff

給 Claude 的落地建議是：把 TYPE-52 當成 `D-80 shoe 外掛框件`，不要把 D-80 shoe 幾何重算在 TYPE-52 裡。

### 最小輸入

```text
52-{size}B{(P)}-{TABLE_A}{(TABLE_B)}-{HOPS}-{LOPS}
```

### 第一版 calculator 最穩的做法

| 項目 | 建議 |
|------|------|
| Shoe 幾何 | 直接引用 `D-80 / TYPE-66` 對應資料 |
| L-angle | 固定 `L40×40×5 ×2` |
| `≤ 8"` | 不加底板補強 |
| `10"~24"` | 加 `PL 12t` 底板 |
| `(P)` | 視為是否要加 reinforcing pad |
| `TABLE_A/B` | 視為 metadata + material / insulation decode |
| `HOPS/LOPS` | 覆寫值，若沒有就取 D-80 預設 |

### BOM 觀點

- TYPE-52 本體應該只負責：
  - lateral retaining angle ×2
  - optional base plate
  - optional pad
- shoe 本體若系統已由 TYPE-66 / D-80 建立，應避免重複計入

### 實作風險提醒

- 現有 `type_52.py` 已混合處理 `52/53/54/55/66/67/85`，之後若 Claude 要重構，最好先把各 type 的差異規則拆開
- `LOPS` / `HOPS` 與 `TABLE_A/B` 比較像 interface metadata，不應該全部硬塞成 plate 幾何公式

---

## 關聯 Type

| 關聯 Type | 關係 |
|------|------|
| **Type 66 (D-80)** | **核心依賴**：TYPE-52 的 shoe 設計、HOPS/LOPS、TABLE A/B 全部來自 D-80 |
| **Type 51** | 同為梁上承托支撐，但 TYPE-51 自成一體（自己的鞍座 80°）；TYPE-52 委託 D-80（120°） |
| Type 46 | TYPE-46 也引用 D-80，但 46 是 Vessel 支撐架；52 是 Beam 上支撐架 |
| Type 47 | 同上，47 = Vessel 支撐 + Lug Plate + D-80 |
| Type 44/45 | 無 D-80 參照的 Vessel 支撐 |
| Type 48 | 不同族群——48 是 Drain Hub 偏移底座 |
| Type 49 | 不同族群——49 是立管(Riser)固定 |

---

## 系統分層定位

```
SYSTEM LAYERS:

Pipe（水平）
↓
Interface Layer      → TYPE-66 Shoe（120°, D-80）
↓
Retaining Frame      → L40×40×5 側擋（TYPE-52 自身構件）
↓
(Optional) PL 12t    → 底板補強（10"~24"）
↓
Support Base         → Beam / CONC. SLAB / STEEL
```

### D-80 引用家族（使用 TYPE-66 shoe 的所有 Type）

```
Type 46: Pipe → [Shoe D-80] → Support Structure → Vessel
Type 47: Pipe → [Shoe D-80] → [Lug Plate] → Structure → Vessel
Type 52: Pipe → [Shoe D-80] → [L-angle 側擋] → Beam        ← 本型
```

> TYPE-52 是 D-80 引用家族中唯一以 **Beam 為 base** 的支撐架。
> Type 46/47 以 Vessel 為 base。

---

## TYPE-51 vs TYPE-52 完整對照

| 特徵 | TYPE-51 | TYPE-52 |
|------|------|------|
| 圖號 | D-62 / D-62A | D-63 |
| 鞍座 | 自己設計（80° for 大管） | **引用 D-80**（120°） |
| 側邊構件 | Member "M"（L50/L65）或 Flat Bar | **L40×40×5**（較小） |
| 底板 | 無 | PL 12t（10"~24"） |
| 管徑 | 3/4"~42"（3 級） | 1/2"~24"（2 級） |
| 焊接 | 6V | 5V |
| 側邊間隙 | 3mm | 3mm |
| Designation | `51-{size}B`（無材質） | `52-{size}B(P)-{A}{(B)}-{HOPS}-{LOPS}`（完整） |
| Material 編碼 | 無 | D-80A TABLE A + B |
| NOTE 2 | Member ≤ beam width | Member ≤ beam width |
| Rein. Pad | D-91（大管） | 在 designation 中標 (P) |
| 橫向約束 | LIMITED（gap 鬆約束） | **RESTRAINED**（L-angle 擋板） |

> **TYPE-51 = 自成一體的承托架（大範圍 3/4"~42"）**
> **TYPE-52 = D-80 shoe 為核心 + 側限位框架（精密 1/2"~24"）**
