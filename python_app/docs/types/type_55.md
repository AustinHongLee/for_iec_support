# TYPE-55 — 帶導向的隔離型夾固 Shoe 支撐（Guided Clamped Shoe with Gasket Isolation）

| 項目 | 內容 |
|------|------|
| 圖號 | D-66（1 OF 2）/ D-66A（2 OF 2） |
| 管徑 | 3/4"~42" |
| 分類 | Guided Clamped Shoe Support with Gasket Isolation |
| 圖面數 | 2 頁 |
| 圖面編號 | E1906-DSP-500-006 |
| 狀態 | ✅ 已實作 |

---

## 系統本質

TYPE-55 是 **51~55 系列中控制最完整的型式**——在 TYPE-54（D-81 Clamp + Shoe + Gasket）基礎上，
加裝 **Guide（導向角鐵）**，形成**隔離 + 固定 + 導向的三合一系統**。

```
TYPE-52 = Shoe + Retainer（防偏）
TYPE-53 = Shoe + Guide（導向）
TYPE-54 = Shoe + Clamp + Gasket（隔離固定）
TYPE-55 = Shoe + Clamp + Guide + Gasket（隔離固定 + 導向 = 完整控制）
```

> **TYPE-54：「不能動，但要保護管子」**
> **TYPE-55：「不能動，要保護管子，而且側向力要由 Guide 分擔」**

### 為什麼需要 TYPE-55

TYPE-54 的 Clamp 已提供全方位固定，為何還要加 Guide？

1. **側向荷重分擔**——大管徑側向力大，Guide 防止剪力全部集中在 Clamp bolt 上
2. **結構冗餘**——雙重橫向約束（Clamp + Guide），提升可靠度
3. **大管必要性**——26"~42" 管徑才出現明確的 Guide 件（piece NO.7），小管靠 L-angle 即可

---

## 系統定位

### 平行家族對照（關鍵架構）

| 介面層 | 無 Guide | 有 Guide |
|------|------|------|
| **D-80（TYPE-66）Shoe only** | TYPE-52（Retainer） | **TYPE-53**（Guide） |
| **D-81（TYPE-67）Shoe+Clamp+Gasket** | **TYPE-54**（隔離固定） | **TYPE-55**（隔離固定+導向） |

> TYPE-55 與 TYPE-53 的關係 = TYPE-54 與 TYPE-52 的關係
> **TYPE-53 : TYPE-66 = TYPE-55 : TYPE-67**

### 分層模型

```
SYSTEM LAYERS:

Pipe
↓
Isolation Layer      → Non-Asbestos Gasket（M-47）
↓
Clamp Layer          → Pipe Clamp（D-81 / D-81A 內含）
↓
Interface Layer      → Shoe / Saddle（鞍座承托）
↓
Guide Layer          → L40×40×5 (≤24") / L50×50×6 (26"~42")
↓
Structure Layer      → Base Beam
```

---

## 兩種結構型態（依管徑分頁）

| 管徑範圍 | 結構型態 | 圖號 | Shoe/Clamp 來源 | Guide 構件 |
|:---:|------|:---:|:---:|:---:|
| **3/4"~24"** | Shoe+Clamp+Gasket+L-angle | D-66 | D-81（TYPE-67） | L40×40×5 |
| **26"~42"** | 多件組裝+Guide block | D-66A | D-81A（TYPE-67） | L50×50×6（NO.7 ×2） |

---

## 第 1 頁（D-66）：3/4"~24"

### 兩個 size group

| 管徑 | 視圖 | 特徵 |
|:---:|------|------|
| 8" & SMALLER | 上方 | L40×40×5 兩側，簡易結構 |
| 10"~24" PIPE | 下方 | L40×40×5 兩側，底座更完整 |

### 幾何參數

| 參數 | 值 | 說明 |
|:---:|:---:|------|
| Shoe/Clamp/Gasket | **DETAIL SEE D-81** | 委託 TYPE-67（D-81） |
| Guide 角鐵 | L40×40×5 | 3 SIDES TYP. 焊接 |
| 側邊間隙 | 3 mm（TYP.） | 兩側各 3mm |
| 焊接 | 5V, 3 SIDES TYP. | 三面焊 |
| 底座寬度 | 150 (NOTE 2) | Member 最大長度不得超過 beam 寬度 |
| Gasket | NON-ASBESTOS GASKET (SEE M-47) | NOTE 3 |

### 與 TYPE-54（D-65）第 1 頁的比較

兩者外觀幾乎完全一致——同樣的 L40×40×5、3mm gap、3 SIDES TYP.、DETAIL SEE D-81、150 (NOTE 2)。

| 差異點 | TYPE-54 | TYPE-55 |
|------|------|------|
| L-angle 功能 | 側向擋板（side restraint） | **Guide（導向）** |
| 管徑範圍 | 3/4"~24"（1 頁） | **3/4"~42"（2 頁）** |
| 大管延伸 | ❌ 無 D-65A | **✅ 有 D-66A（26"~42"）** |
| 圖號 | D-65 | D-66 / D-66A |

> 在 3/4"~24" 範圍內，TYPE-54 與 TYPE-55 圖面結構幾乎相同。
> 核心差異在於 **工程意圖**（designation TYPE 編號區分）和 **大管延伸能力**。

---

## 第 2 頁（D-66A）：26"~42"

### 多件組裝結構（件 1~7）

| 件號 | 數量 | 角色 | 來源 |
|:---:|:---:|------|------|
| 1~6 | — | Shoe + Clamp + Gasket 組裝 | **SEE SH'T D-81A**（NOTE 1） |
| **7** | **2** | **GUIDE** | **L50×50×6（本圖定義）** |

> 件 1~6 的尺寸完全來自 D-81A（TYPE-67 第 2 頁）。
> TYPE-55 第 2 頁**只定義 piece 7（Guide）**——其餘委託 TYPE-67。
> 這與 TYPE-53 第 2 頁的架構一致（TYPE-53 委託 D-80B，TYPE-55 委託 D-81A）。

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

> 所有 26"~42" 均使用相同的 L50×50×6 GUIDE（與 TYPE-53 第 2 頁完全一致）。

### 其他幾何參數

| 參數 | 值 | 說明 |
|:---:|:---:|------|
| 底座寬度 | 350 mm | 與 TYPE-53 D-64A 一致 |
| 焊接 | 6V, 3 SIDES TYP. | 比第 1 頁的 5V 加大 |
| Side plate 間距 | 16 + b + 16（左右） | 對應 D-81A 尺寸 |
| 焊接尺寸標示 | 12 + 12 | 圖上標示 |
| 未標尺寸 | SEE SH'T D-81A（NOTE 1） | 委託 TYPE-67 補充 |

### TYPE-A / TYPE-B 分型（NOTE 3）

| TYPE | 保溫厚度條件 |
|:---:|------|
| **TYPE-A** | 保溫厚度 ≤ 100mm |
| **TYPE-B** | 保溫厚度 > 100mm 且 ≤ 150mm |

### 荷重條件（NOTE 4）

> **LOADING CONDITION**: CARBON STEEL SADDLE WITH MAX. PIPE TEMPERATURE **700°F**

---

## 連接方式

### 混合式系統（bolt + weld）

TYPE-55 是 51~55 系列中**唯一同時具備機械連接和焊接的 Guide 型式**：

| 連接界面 | 方式 |
|------|------|
| Pipe ↔ Gasket | 接觸（壓持） |
| Gasket ↔ Clamp | 夾持（bolt，機械連接） |
| Clamp ↔ Shoe | 壓持 / 夾持 |
| Guide ↔ Base | 焊接（5V / 6V, 3 SIDES TYP.） |
| Shoe ↔ Base | 焊接 |

### 荷重路徑

```
Pipe（水平管線）
→ NON-ASBESTOS GASKET（M-47，隔離層）
→ PIPE CLAMP（D-81 / D-81A 內含，夾持固定）
→ Shoe / Saddle（鞍座承托）
→ Guide（L40×40×5 / L50×50×6，橫向荷重分擔）
→ Base Beam
```

---

## 約束行為

| 自由度 | 狀態 | 說明 |
|:---:|:---:|------|
| 垂直（↓） | **FIXED** | Shoe 承重 + Clamp 壓持 |
| 垂直（↑） | **FIXED** | Clamp 防止抬起 |
| 軸向（Axial） | **FIXED** | Clamp 夾固 + Gasket 摩擦 |
| 橫向（Lateral） | **FIXED** | Clamp + Guide 雙重約束 |
| 旋轉 | **FIXED** | Clamp 全包覆 + Guide 結構約束 |

→ TYPE-55 是 **FIXED SUPPORT**（同 TYPE-54），但具備**更高的橫向荷重承載能力**。

> ⚠️ Gasket 的壓縮特性使其不是理論剛體固定（engineering-fixed, not mathematically rigid）。

### 51~55 系列完整約束等級遞進

| 自由度 | TYPE-51 | TYPE-52 | TYPE-53 | TYPE-54 | **TYPE-55** |
|:---:|:---:|:---:|:---:|:---:|:---:|
| Axial | FREE | PARTIAL | FREE | **FIXED** | **FIXED** |
| Lateral | LIMITED | RESTRAINED | STRONGLY RESTRAINED | **FIXED** | **FIXED** |
| Vertical ↑ | FREE | FREE | FREE | **FIXED** | **FIXED** |
| 材質隔離 | ❌ | ❌ | ❌ | **✅** | **✅** |
| Guide | ❌ | ❌ | **✅** | ❌ | **✅** |
| 定位 | 承托 | 防偏 | 導向 | 隔離固定 | **隔離固定+導向** |

---

## 編碼格式（Designation）

### D-66 格式（3/4"~24"）— NOTE 1

**格式**: `55-{size}B-{TABLE_A}-{HOPS}-{LOPS}`

```
55-2B-A-130-500
│  │  │  │    └─ MODIFY LOPS (mm) IF ANY
│  │  │  └────── MODIFY HOPS (mm) IF ANY
│  │  └───────── SEE SH'T D-80A TABLE "A"
│  └───────────── LINE SIZE
└──────────────── TYPE NO.
```

### D-66A 格式（26"~42"）— NOTE 2

**格式**: `55-{size}B-{insul_type}-{HOPS}-{LOPS}`

```
55-30B-A-130-500
│  │  │  │    └─ MODIFY LOPS (mm) IF ANY
│  │  │  └────── MODIFY HOPS (mm) IF ANY
│  │  └───────── SEE NOTE 3: A=保溫≤100, B=保溫>100≤150
│  └───────────── LINE SIZE
└──────────────── TYPE NO.
```

### ⚠️ 與 TYPE-54 Designation 完全同構

| 項目 | TYPE-54 | **TYPE-55** |
|------|------|------|
| 格式 | `54-{size}B-{TABLE_A}-{HOPS}-{LOPS}` | **`55-{size}B-{TABLE_A}-{HOPS}-{LOPS}`** |
| (P) Reinf. Pad | ❌ | **❌** |
| TABLE "B" 材質碼 | ❌ | **❌** |
| 唯一差異 | TYPE NO. = 54 | TYPE NO. = **55** |

> TYPE-54 / TYPE-55 / TYPE-67 三者 designation 結構完全一致：無 (P)、無 TABLE B。
> 這是因為三者都專用於 AS/SS 管線，材質已隱含在 TYPE 本身。

---

## 工程 NOTES 彙整

### D-66 NOTES（3/4"~24"）

| NOTE | 內容 |
|:---:|------|
| 1 | Designation 格式（見上方） |
| 2 | Member 最大長度不得超過 beam 寬度 |
| 3 | 本型通常用於 AS 和 SS 管線（MAX. LINE TEMP.: 750°F） |
| 4 | HOPS = Height Of Shoe, LOPS = Length Of Shoe |

### D-66A NOTES（26"~42"）

| NOTE | 內容 |
|:---:|------|
| 1 | 未標尺寸見 SH'T **D-81A** |
| 2 | Designation 格式（見上方） |
| 3 | TYPE-A: 保溫 ≤100mm, TYPE-B: 保溫 >100 ≤150mm |
| 4 | 荷重條件: CS saddle, MAX PIPE TEMPERATURE 700°F |
| 5 | HOPS = Height Of Shoe, LOPS = Length Of Shoe |

---

## 構件清單

### 3/4"~24"（D-66）

| # | 構件 | 規格 / 來源 |
|:---:|------|------|
| 1 | Shoe + Clamp + Gasket | DETAIL SEE D-81（TYPE-67） |
| 2 | Guide L-angle ×2 | L40×40×5, 3 SIDES TYP. |
| 3 | Non-Asbestos Gasket | M-47（SEE NOTE 3） |
| 4 | Weld | 5V, 3 SIDES TYP. |

### 26"~42"（D-66A）

| # | 構件 | 規格 / 來源 |
|:---:|------|------|
| 1~6 | Shoe+Clamp+Gasket 多件組裝 | SEE SH'T D-81A（TYPE-67） |
| **7** | **Guide ×2** | **L50×50×6** |
| — | Weld | 6V, 3 SIDES TYP. |

### 不存在的構件

- Reinforcing Pad（D-81 系統不使用）
- Retainer（TYPE-52/54 的擋板）
- Lug Plate
- Trunnion
- U-bolt

---

## 設計流程

```
1. 確定: LINE SIZE (3/4"~42"), 管材 (AS/SS), 保溫厚度
2. 確認材質適用性: 本型僅用於 AS/SS (NOTE 3, MAX. 750°F)
3. 選結構型態:
   - 3/4"~24" → D-66（Shoe+Clamp+Gasket D-81 + Guide L40×40×5）
   - 26"~42" → D-66A（D-81A 多件組裝 + Guide L50×50×6）
4. Shoe/Clamp/Gasket 設計:
   - ≤24" → 查 D-81（TYPE-67 主表）
   - 26"~42" → 查 D-81A（TYPE-67 大管表）
5. 保溫符號:
   - ≤24" → D-80A TABLE "A"（NONE/A/B/C）
   - 26"~42" → NOTE 3（TYPE-A/B）
6. 確認 Member 長度 ≤ Beam 寬度（NOTE 2，≤24" only）
7. 計算 LOPS（有 Pipe Stop 時另行計算）
8. 編碼: 55-{size}B-{A/B/C/NONE}-{HOPS}-{LOPS}
```

---

## 關聯 Type

| 關聯 Type | 關係 |
|------|------|
| **Type 67 (D-81/D-81A)** | **核心依賴**：Shoe+Clamp+Gasket 設計全部來自 D-81 |
| **Type 54** | **最近親**：同為 D-81 系隔離固定，差異在 54 無 Guide / 55 有 Guide |
| **Type 53** | **對稱對照**：53=D-80+Guide / 55=D-81+Guide |
| Type 66 (D-80) | 間接依賴——D-81 的底層鞍座結構來自 D-80 |
| Type 52 | 同系列——52=D-80+Retainer |
| Type 51 | 同系列——自有 80° 鞍座 |
| M-4 | Pipe Clamp（≤24"，via D-81） |
| M-47 | Non-Asbestos Gasket |
| M-56 | Pipe Clamp（26"~42"，via D-81A） |
| D-80A | TABLE "A"（保溫→HOPS） |

---

## 51~55 系列完整家族總覽

```
TYPE-51: Pipe → [自有Saddle 80°]                    → Beam （自由承托, 3/4"~42"）
TYPE-52: Pipe → [Shoe D-80 120°] → [Retainer]       → Beam （防偏, 1/2"~24"）
TYPE-53: Pipe → [Shoe D-80 120°] → [Guide]          → Beam （導向, 3/4"~42"）
TYPE-54: Pipe → [Gasket] → [Clamp D-81] → [Shoe]    → Beam （隔離固定, 3/4"~24"）
TYPE-55: Pipe → [Gasket] → [Clamp D-81] → [Shoe] → [Guide] → Beam （隔離固定+導向, 3/4"~42"）
```

### D-80 家族 vs D-81 家族

```
D-80 引用家族（純承托/導向）:
├── TYPE-46: Shoe → Vessel 支撐
├── TYPE-47: Shoe + Lug → Vessel 支撐
├── TYPE-52: Shoe + Retainer → Beam（防偏）
└── TYPE-53: Shoe + Guide → Beam（導向）

D-81 引用家族（隔離+夾固）:
├── TYPE-54: Clamp + Shoe + Gasket → Beam（隔離固定）
└── TYPE-55: Clamp + Shoe + Gasket + Guide → Beam（隔離固定+導向）
```
