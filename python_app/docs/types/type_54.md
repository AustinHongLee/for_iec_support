# TYPE-54 — Isolated Clamp Shoe Support（隔離型夾固 Shoe 支撐）

| 項目 | 內容 |
|------|------|
| 圖號 | D-65 |
| 管徑 | 推定 3/4"~24"（圖面標示 8" & smaller / 10"~24"） |
| 分類 | Isolated Clamp Shoe Support（隔離型固定支撐） |
| 圖面數 | 1 頁 |
| 圖面編號 | E1906-DSP-500-006 |
| 狀態 | ✅ 已實作 |

---

## 系統本質

TYPE-54 是**材料導向的隔離型固定支撐**——專為 **Alloy Steel** 和 **Stainless Steel** 管線設計。

核心特徵：
1. **NON-ASBESTOS GASKET（M-47）**——在管線與支撐結構之間加入隔離層
2. **Clamp 夾固**——提供完整的位置固定（不是純 rest）
3. **DETAIL SEE D-81**——不是引用 D-80（TYPE-66），而是**獨立的 D-81 shoe/clamp 系統**

TYPE-54 存在的唯一原因：**管線材質不允許直接接觸碳鋼支撐結構**。

> NOTE 3 明確寫出：
> *THIS TYPE IS USUALLY USED FOR ALLOY STEEL AND STAINLESS STEEL LINES*
> *(MAX. LINE TEMP.: 750°F)*

---

## 與 TYPE-52 / TYPE-53 的核心差異

| 特徵 | TYPE-52 | TYPE-53 | **TYPE-54** |
|------|------|------|------|
| Shoe 來源 | D-80 | D-80/D-80B | **D-81** |
| 側邊功能 | Retainer（防偏） | Guide（導向） | **Clamp（夾固）** |
| Gasket | ❌ | ❌ | **✅ M-47** |
| Bolt | ❌ | ❌ | **✅（Clamp bolt）** |
| Axial | Partial free | Free | **Fixed** |
| Lateral | Restrained | Strongly restrained | **Fixed** |
| 材質限定 | 無 | 無 | **AS / SS only** |
| Designation 材質碼 | 有（TABLE B） | 有（TABLE B） | **無**（材質已隱含） |

> **TYPE-52：「不要亂跑」**
> **TYPE-53：「只能這樣走」**
> **TYPE-54：「不能動，但要保護管子」**

---

## 兩種結構型態（依管徑分級）

| 管徑範圍 | 結構型態 | 特徵 |
|:---:|------|------|
| **8" & SMALLER** | 簡易型 | L40×40×5 兩側 + Clamp + Gasket |
| **10"~24"** | 補強型 | L40×40×5 + PL 12t 底板 + Clamp + Gasket |

---

## 幾何關鍵參數

| 參數 | 值 | 說明 |
|:---:|:---:|------|
| Saddle 包覆角 | 120° | 可見於 ELEV 視圖 |
| 側邊間隙 | 3 mm（TYP.） | 兩側各 3mm |
| 側邊角鐵 | L40×40×5 | CUT IN FIELD |
| 底板（10"~24"） | PL 12t | 12mm 厚鋼板 |
| 焊接 | 5V TYP. | 構造焊接 |
| 底座寬度 (8" & smaller) | 150 (SEE NOTE 2) | 受 beam width 約束 |
| 底座寬度 (10"~24") | 25 + 100 + 25 = 150 | 同上 |
| Shoe/Clamp Detail | **DETAIL (SEE D-81)** | ⚠️ 不是 D-80！ |

---

## NON-ASBESTOS GASKET（M-47）

| 項目 | 內容 |
|------|------|
| 標註位置 | 兩個 size group 右側 plan view 頂部 |
| 組件圖 | M-47（COMPRESSED GASKET） |
| 功能 | 管線與支撐結構之間的隔離層 |
| 引用 | (SEE NOTE 3) |

### 為什麼需要 Gasket？

NOTE 3 說明本型「usually used for AS and SS lines」——

1. **防止異種金屬接觸**——SS/AS 管線若直接接觸 CS 支撐，會產生電位差腐蝕（galvanic corrosion）
2. **減少磨損**——AS/SS 在高溫下（≤750°F）的接觸面容易 galling
3. **熱隔離**——gasket 提供一定程度的熱阻隔

---

## DETAIL SEE D-81（關鍵差異）

TYPE-54 引用的是 **D-81**，不是 D-80（TYPE-66）。

| 比較 | TYPE-52/53 | TYPE-54 |
|------|------|------|
| Shoe Detail | D-80（TYPE-66） | **D-81** |
| 含 Clamp | ❌ | **✅** |
| 含 Gasket slot | ❌ | **✅**（推定） |

> D-81 的詳細內容需要另外查閱其圖紙。
> 推定 D-81 是含 clamp 固定機構的 shoe/clamp 組合詳圖。

---

## 連接方式

TYPE-54 是 51~54 系列中**唯一非純焊接系統**——加入了 clamp bolt 機械連接：

| 連接 | 方式 |
|------|------|
| Pipe ↔ Gasket | **接觸**（壓持） |
| Gasket ↔ Clamp | **壓持** |
| Clamp ↔ Structure | **Bolt**（機械連接） |
| L-angle ↔ Base | 焊接（5V TYP.） |
| PL 12t ↔ Base | 焊接 |

---

## 約束行為

| 自由度 | 狀態 | 說明 |
|:---:|:---:|------|
| 垂直（↓） | **FIXED** | Shoe 承重 + Clamp 壓持 |
| 垂直（↑） | **FIXED** | Clamp 防止抬起 |
| 軸向（Axial） | **FIXED** | Clamp 夾固 + Gasket 摩擦 |
| 橫向（Lateral） | **FIXED** | L-angle + Clamp 側向約束 |
| 旋轉 | **FIXED** | Clamp 全包覆約束 |

→ TYPE-54 是 **FIXED SUPPORT**（anchor point）。
管線在此處**不允許任何方向的移動**。

> ⚠️ Gasket 的壓縮特性使其不是 100% rigid，但工程上仍歸類為 fixed。

### 51~54 系列約束等級遞進

| 自由度 | TYPE-51 | TYPE-52 | TYPE-53 | **TYPE-54** |
|:---:|:---:|:---:|:---:|:---:|
| Axial | FREE | PARTIAL | FREE | **FIXED** |
| Lateral | LIMITED | RESTRAINED | STRONGLY RESTRAINED | **FIXED** |
| Vertical ↑ | FREE | FREE | FREE | **FIXED** |
| 定位 | 承托 | 防偏 | 導向 | **錨定** |

---

## Load Path（荷重路徑）

### 8" & Smaller

```
Pipe（水平）
→ NON-ASBESTOS GASKET（M-47，隔離）
→ Clamp（D-81，夾固）
→ Shoe / Support Structure
→ L40×40×5
→ Base Beam
```

### 10"~24"

```
Pipe（水平）
→ NON-ASBESTOS GASKET（M-47，隔離）
→ Clamp（D-81，夾固）
→ Shoe / Support Structure
→ PL 12t
→ L40×40×5
→ Base Beam
```

---

## 構件清單

### 8" & Smaller

| # | 構件 | 規格 / 來源 |
|:---:|------|------|
| 1 | Shoe + Clamp | DETAIL SEE D-81 |
| 2 | NON-ASBESTOS GASKET | M-47 |
| 3 | L-angle ×2 | L40×40×5, CUT IN FIELD |
| 4 | Clamp Bolt | 見 D-81 |
| 5 | Weld | 5V TYP. |

### 10"~24"

| # | 構件 | 規格 / 來源 |
|:---:|------|------|
| 1 | Shoe + Clamp | DETAIL SEE D-81 |
| 2 | NON-ASBESTOS GASKET | M-47 |
| 3 | Base Plate | PL 12t |
| 4 | L-angle ×2 | L40×40×5, CUT IN FIELD |
| 5 | Clamp Bolt | 見 D-81 |
| 6 | Weld | 5V TYP. |

### 不存在的構件

- Lug Plate
- Trunnion
- Brace（斜撐）
- Guide（那是 TYPE-53）

---

## Designation（編碼格式）

### NOTE 1 格式

```
54-2B-A-130-500
│   │  │  │   └── MODIFY LOPS=500 (mm) IF ANY
│   │  │  └────── MODIFY HOPS=130 (mm) IF ANY
│   │  └───────── SEE SH'T D-80A TABLE "A"（保溫→HOPS符號）
│   └──────────── DENOTE LINE SIZE
└──────────────── DENOTE TYPE NO.
```

### 格式

```
54-{size}B-{TABLE_A}-{HOPS}-{LOPS}
```

> ⚠️ **與 TYPE-52/53 的 designation 有重要差異：**
> - **無 `(P)` Rein. Pad 欄位**
> - **無 TABLE "B" 材質符號**
> 
> 原因：TYPE-54 本身就限定 AS/SS（NOTE 3），不需再標材質。
> 保溫符號仍來自 D-80A TABLE "A"。

### 範例

| 管徑 | 保溫 | HOPS/LOPS 修改 | Designation |
|:---:|:---:|:---:|------|
| 2" | A級 | HOPS=130, LOPS=500 | 54-2B-A-130-500 |
| 8" | 無保溫 | 無修改 | 54-8B |
| 14" | B級 | LOPS=400 | 54-14B-B-400 |

---

## NOTES 摘要

| NOTE | 內容 |
|:---:|------|
| 1 | Designation 格式 |
| 2 | **Member 最大長度不得超過 Beam 寬度** |
| 3 | **通常用於 Alloy Steel 和 Stainless Steel，MAX 750°F** |
| 4 | HOPS = Height of Pipe Shoe, LOPS = Length of Pipe Shoe |

---

## 設計流程

```
1. 確認材質: AS / SS（NOTE 3 限定）
2. 確認溫度: ≤ 750°F
3. 確定: LINE SIZE, 保溫厚度
4. 選結構型態:
   - ≤8" → 簡易型
   - 10"~24" → 補強型（+ PL 12t）
5. 查 D-80A TABLE "A": 保溫厚度 → HOPS 符號
6. 查 D-81: Shoe + Clamp 詳細設計
7. 選用 M-47 Gasket
8. 確認 Member 長度 ≤ Beam 寬度（NOTE 2）
9. 如需修改 HOPS/LOPS，加入 designation
10. 編碼: 54-{size}B-{TABLE_A}-{HOPS}-{LOPS}
```

---

## 關聯 Type

| 關聯 Type | 關係 |
|------|------|
| **D-81** | **核心依賴**：Shoe + Clamp 詳細設計（不是 D-80！） |
| **M-47** | NON-ASBESTOS GASKET（隔離層組件） |
| D-80A TABLE "A" | 保溫 → HOPS 符號（designation 仍引用） |
| Type 52 | 同族（梁上 Shoe 支撐），52 = retainer，54 = clamp + gasket |
| Type 53 | 同族，53 = guide，54 = fixed |
| Type 51 | 同族（梁上承托），51 = 自成一體純承托 |
| Type 66 (D-80) | **TYPE-54 不引用 D-80**——引用 D-81（不同的 shoe/clamp 系統） |

---

## 系統分層定位

```
SYSTEM LAYERS:

Pipe（水平，AS/SS material）
↓
Isolation Layer      → NON-ASBESTOS GASKET（M-47）
↓
Clamp Layer          → Clamp（D-81，bolt 固定）
↓
Support Structure    → Shoe + L40×40×5（+ PL 12t for 10"~24"）
↓
Support Base         → Beam
```

### 梁上支撐族群完整對照

```
Type 51: Pipe → [自有Saddle] → Beam                   （自由承托）
Type 52: Pipe → [Shoe D-80] → [L-angle 側擋] → Beam   （防偏）
Type 53: Pipe → [Shoe D-80] → [L-angle Guide] → Beam  （導向）
Type 54: Pipe → [Gasket] → [Clamp D-81] → [Shoe] → Beam（隔離固定）← 本型
```

> TYPE-54 是梁上支撐族群中：
> - 唯一有 **Gasket 隔離**
> - 唯一有 **Clamp bolt 機械固定**
> - 唯一**限定材質**（AS/SS）
> - 唯一引用 **D-81**（非 D-80）
> - 唯一的 **FIXED SUPPORT**（錨定點）
