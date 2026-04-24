# TYPE-53 — Guided Pipe Shoe Support（帶導向的 Shoe 承托支撐）

| 項目 | 內容 |
|------|------|
| 圖號 | D-64（1 OF 2）/ D-64A（2 OF 2） |
| 管徑 | 3/4"~42" |
| 分類 | Guided Pipe Shoe Support |
| 圖面數 | 2 頁 |
| 圖面編號 | E1906-DSP-500-006 |
| 狀態 | ✅ 3/4"~24" 已共用 Type 52 幾何；⚠️ 26"~42" D-64A 尚未獨立接線 |

---

## 系統本質

TYPE-53 是**帶導向功能的 Pipe Shoe 支撐架**——以 TYPE-66（D-80/D-80B）的 120° 鞍座為核心，
加裝 L-angle 側邊構件作為 **GUIDE（導向）**，使管線**可沿軸向自由滑動，但不可橫向偏移**。

與 TYPE-52 的核心差異：
- TYPE-52 = Shoe + **Side Retainer**（側擋，防止偏位）
- TYPE-53 = Shoe + **Guide**（導向，允許軸向滑動、強制限制橫向）

> **TYPE-52：「不要亂跑」→ TYPE-53：「只能這樣走」**

---

## 兩種結構型態（依管徑分頁）

| 管徑範圍 | 結構型態 | 圖號 | Shoe 來源 | Guide 構件 |
|:---:|------|:---:|:---:|:---:|
| **3/4"~24"** | Shoe + L-angle 導向 | D-64 | D-80 | L40×40×5 |
| **26"~42"** | 多件組裝 + Guide block | D-64A | D-80B | L50×50×6（NO.6 ×2） |

---

## 第 1 頁（D-64）：3/4"~24"

### 兩個 size group

| 管徑 | 視圖 | 特徵 |
|:---:|------|------|
| 8" & SMALLER | 左上 + 右上 | L40×40×5 兩側，簡易結構 |
| 10"~24" PIPE | 左下 + 右下 | L40×40×5 兩側，底座更完整 |

### 幾何參數

| 參數 | 值 | 說明 |
|:---:|:---:|------|
| Saddle 包覆角 | **120°** | 來自 D-80（TYPE-66） |
| 側邊間隙 | 3 mm（TYP.） | 兩側各 3mm |
| Guide 角鐵 | L40×40×5 | CUT IN FIELD |
| 焊接 | 5V, 3 SIDES TYP. | 三面焊 |
| 底座寬度 | 150 (NOTE 2) | 受 beam width 約束 |
| Shoe Detail | DETAIL SEE D-80 | 鞍座設計委託 D-80 |

### 與 TYPE-52（D-63）第 1 頁的比較

第 1 頁的結構外觀與 TYPE-52 幾乎完全一致：同樣的 L40×40×5、120°、3mm gap、5V weld、
DETAIL SEE D-80、150 (NOTE 2)。

推定差異在於 **L-angle 的軸向延伸長度**：
- TYPE-52 的 L-angle 為短段 retainer（在支撐點處局部夾持）
- TYPE-53 的 L-angle 沿管線軸向延長，形成持續的 guide channel

> ⚠️ 此差異從平面圖難以判別，但 TYPE 編號區分與 designation 分離
> 表明工程意圖不同：52 = retainer，53 = guide。

---

## 第 2 頁（D-64A）：26"~42"

### 多件組裝結構

第 2 頁使用件號 1~6 的組裝結構（類似 D-80B 的擴展版）：

| 件號 | 數量 | 推定角色 |
|:---:|:---:|------|
| 1 | — | 側板 |
| 2 | — | 底板 |
| 3 | — | 鞍座弧面 |
| 4 | — | 頂部蓋板（如有） |
| 5 | — | 加勁板 |
| **6** | **2** | **GUIDE = L50×50×6** |

> 件號 6 是 TYPE-53 獨有的 **GUIDE 構件**——兩側各一支 L50×50×6。
> 這是與 TYPE-66 D-80B 組裝的核心增加項。

### GUIDE 表

| PIPE SIZE | GUIDE |
|:---:|:---:|
| 26" | L50×50×6 |
| 28" | L50×50×6 |
| 30" | L50×50×6 |
| 32" | L50×50×6 |
| 36" | L50×50×6 |
| 40" | L50×50×6 |
| 42" | L50×50×6 |

> 所有 26"~42" 均使用相同的 L50×50×6 GUIDE。

### 其他幾何參數

| 參數 | 值 | 說明 |
|:---:|:---:|------|
| 底座寬度 | 350 mm | 比 D-64 的 150mm 大幅增加 |
| Saddle 角 | 120° + 90°（可見） | 與 D-80B 一致 |
| 焊接 | 6V, 3 SIDES TYP. | 比第1頁的 5V 加大 |
| Side plate 間距 | 16 + b + 16（左右） | 對應 D-80B 尺寸 |
| 未標尺寸 | SEE SH'T D-80B（NOTE 1） | 委託 D-80B 補充 |

---

## 連接方式

全部為焊接，無任何螺栓/夾具：

| 連接 | 方式 |
|------|------|
| Pipe ↔ Shoe | 焊接（D-80 NOTE 7） |
| Shoe ↔ Frame | 焊接 |
| Guide ↔ Frame/Base | 焊接 |
| Frame ↔ Base | 焊接 |

---

## 約束行為

| 自由度 | 狀態 | 說明 |
|:---:|:---:|------|
| 垂直（↓） | **SUPPORTED** | Shoe 承重 |
| 垂直（↑） | **FREE** | 無 clamp |
| 軸向（Axial） | **FREE** | Guide 允許軸向滑動（熱膨脹） |
| 橫向（Lateral） | **STRONGLY RESTRAINED** | Guide 結構明確限制 |
| 旋轉 | **LIMITED** | 120° 包覆 + guide 約束 |

→ TYPE-53 是 **GUIDED SUPPORT**：允許管線軸向自由滑動，嚴格限制橫向位移。

### 與 TYPE-51 / TYPE-52 的約束比較

| 自由度 | TYPE-51 | TYPE-52 | TYPE-53 |
|:---:|:---:|:---:|:---:|
| Axial | FREE | PARTIAL FREE | **FREE** |
| Lateral | LIMITED | RESTRAINED | **STRONGLY RESTRAINED** |
| 功能定位 | 承托 | 承托+防偏 | **承托+導向** |

---

## Load Path（荷重路徑）

### 3/4"~24"

```
Pipe（水平）
→ Shoe（120°, D-80）
→ Guide（L40×40×5，lateral restraint）
→ Base Beam
```

### 26"~42"

```
Pipe（水平）
→ Shoe（120°, D-80B 組裝）
→ Guide NO.6（L50×50×6 ×2，lateral restraint）
→ Multi-piece Frame（件 1~5）
→ Base Beam
```

---

## 構件清單

### 3/4"~24"（D-64）

| # | 構件 | 規格 |
|:---:|------|------|
| 1 | Pipe Shoe | 120°（DETAIL SEE D-80） |
| 2 | Guide L-angle ×2 | L40×40×5, CUT IN FIELD |
| 3 | Reinforcing Pad | 依需求，designation 中用 (P) 標記 |
| 4 | Weld | 5V, 3 SIDES TYP. |

### 26"~42"（D-64A）

| # | 構件 | 規格 |
|:---:|------|------|
| 1~5 | 多件組裝本體 | 尺寸見 D-80B |
| **6** | **Guide ×2** | **L50×50×6** |
| — | Weld | 6V, 3 SIDES TYP. |

### 不存在的構件

- Bolt / Nut
- Clamp
- Lug Plate
- Trunnion
- Brace（斜撐）

---

## Designation（編碼格式）

### 第 1 頁格式（3/4"~24"）— NOTE 1

```
53-2B(P)-A(A)-130-500
│   │  │   │  │   └── MODIFY LOPS=500 (mm) IF ANY
│   │  │   │  └────── MODIFY HOPS=130 (mm) IF ANY
│   │  │   └───────── SEE SH'T D-80A TABLE "B"（材質符號）
│   │  └───────────── SEE SH'T D-80A TABLE "A"（保溫→HOPS符號）
│   └──────────────── DENOTE REIN. PAD IS REQ'D
└──────────────────── DENOTE LINE SIZE
53 ← DENOTE TYPE NO.
```

### 第 2 頁格式（26"~42"）— NOTE 2

```
53-30B-A(A)-130-500
│   │   │  │   └── MODIFY LOPS=500 (mm) IF ANY
│   │   │  └────── MODIFY HOPS=130 (mm) IF ANY
│   │   └───────── SEE SH'T D-80A TABLE "B"（材質符號）
│   └───────────── SEE NOTE 3（TYPE-A/B 保溫分類）
└───────────────── DENOTE LINE SIZE
53 ← DENOTE TYPE NO.
```

> ⚠️ 兩頁 designation 格式有差異：
> - 第1頁有 `(P)` Rein. Pad，保溫用 TABLE "A" 符號
> - 第2頁無 `(P)`，保溫用 NOTE 3 TYPE-A/B 分類
> 
> 此差異與 TYPE-66 的 D-80 vs D-80B designation 系統完全一致。
> 也與 TYPE-52 的 designation 系統完全一致（僅 prefix 53 vs 52）。

### 範例

| 管徑 | 組態 | Designation |
|:---:|------|------|
| 2" | Pad, 保溫A, AS | 53-2B(P)-A(A)-130-500 |
| 8" | 無Pad, 無保溫, CS | 53-8B |
| 30" | TYPE-A, AS | 53-30B-A(A) |
| 42" | TYPE-B, SS, HOPS修改 | 53-42B-B(S)-200 |

---

## NOTES 摘要

### D-64（第1頁）

| NOTE | 內容 |
|:---:|------|
| 1 | Designation 格式（≤24" 版） |
| 2 | **Member 最大長度不得超過 Beam 寬度** |
| 3 | HOPS = Height of Pipe Shoe, LOPS = Length of Pipe Shoe |

目前 calculator 對 3/4"~24" 走 `type_52.py` 共用路徑，因此 `Pad_52Type`、`L40x40x5`、`H Beam / FB_52Type_3` 的幾何與 Type 52 保持一致。

### D-64A（第2頁）

| NOTE | 內容 |
|:---:|------|
| 1 | 未標尺寸見 SH'T **D-80B** |
| 2 | Designation 格式（26"~42" 版） |
| 3 | TYPE-A: 保溫 ≤100mm, TYPE-B: 保溫 >100 ≤150mm |
| 4 | 荷重條件: CS saddle, MAX 700°F & 300 PSI |
| 5 | HOPS = Height of Pipe Shoe, LOPS = Length of Pipe Shoe |

目前 calculator 尚未獨立落地 D-64A 的 26"~42" 大管 guide 結構；後續應補 `Guide NO.6 = L50x50x6 x2` 與 D-80B 多件組裝路徑。

---

## 設計流程

```
1. 確定: LINE SIZE (3/4"~42"), 管材, 保溫厚度
2. 選結構型態:
   - 3/4"~24" → D-64（Shoe + L40×40×5 Guide）
   - 26"~42" → D-64A（多件組裝 + L50×50×6 Guide）
3. Shoe 設計:
   - ≤24" → 查 D-80（TYPE-66 主表）
   - 26"~42" → 查 D-80B（TYPE-66 大管表）
4. 保溫符號:
   - ≤24" → D-80A TABLE "A"（NONE/A/B/C）
   - 26"~42" → NOTE 3（TYPE-A/B）
5. 材質符號: D-80A TABLE "B"（NONE/(A)/(S)）
6. 確認 Rein. Pad 需求（≤24" only）
7. 確認 Member 長度 ≤ Beam 寬度（NOTE 2）
8. 編碼
```

---

## 關聯 Type

| 關聯 Type | 關係 |
|------|------|
| **Type 66 (D-80/D-80B)** | **核心依賴**：Shoe 設計、HOPS/LOPS、TABLE A/B 全部來自 D-80 |
| **Type 52** | **最近親**：結構幾乎一致，差異在 52=retainer / 53=guide |
| Type 51 | 同為梁上承托，但 51 自成一體（80° 自有鞍座、無材質碼） |
| Type 46/47 | 同屬 D-80 引用家族，但 46/47 是 Vessel 支撐架 |
| Type 48 | 不同族群——48 是 Drain Hub 偏移底座 |
| Type 49 | 不同族群——49 是立管(Riser)固定 |

---

## 系統分層定位

```
SYSTEM LAYERS:

Pipe（水平）
↓
Interface Layer      → TYPE-66 Shoe（120°, D-80/D-80B）
↓
Guide Structure      → L40×40×5 (≤24") / L50×50×6 (26"~42")
↓
Support Base         → Beam / CONC. SLAB / STEEL
```

### D-80 引用家族（完整）

```
Type 46: Pipe → [Shoe D-80] → Structure → Vessel           （Vessel 承托）
Type 47: Pipe → [Shoe D-80] → [Lug Plate] → Structure → Vessel（Vessel Lug）
Type 52: Pipe → [Shoe D-80] → [L-angle 側擋] → Beam       （梁上防偏）
Type 53: Pipe → [Shoe D-80] → [L-angle Guide] → Beam      （梁上導向）← 本型
```

---

## TYPE-51 / TYPE-52 / TYPE-53 完整對照

| 特徵 | TYPE-51 | TYPE-52 | TYPE-53 |
|------|------|------|------|
| 圖號 | D-62/D-62A | D-63 | D-64/D-64A |
| 鞍座來源 | 自己設計 | D-80 | D-80 / D-80B |
| 鞍座角度 | 80°（大管） | 120° | 120° |
| 側邊功能 | 鬆約束 | **Retainer** | **Guide** |
| 側邊構件 | Member M | L40×40×5 | L40×40×5 / L50×50×6 |
| 管徑 | 3/4"~42"（3級） | 1/2"~24"（2級） | 3/4"~42"（2級+大管） |
| 焊接 | 6V | 5V | 5V / 6V |
| Designation | `51-{size}B` | 52-格式（含 TABLE A/B） | 53-格式（含 TABLE A/B） |
| Material 編碼 | 無 | 有 | 有 |
| 大管 Guide | 無 | 無 | **L50×50×6 (NO.6 ×2)** |
| Axial | FREE | PARTIAL FREE | **FREE** |
| Lateral | LIMITED | RESTRAINED | **STRONGLY RESTRAINED** |

> **TYPE-51 = 承托（自成一體）**
> **TYPE-52 = Shoe承托 + 側擋（防偏）**
> **TYPE-53 = Shoe承托 + 導向（定向滑動）**
