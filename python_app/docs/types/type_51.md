# TYPE-51 — Pipe Saddle Support（管線鞍座承托支撐）

| 項目 | 內容 |
|------|------|
| 圖號 | D-62（1 OF 2）/ D-62A（2 OF 2） |
| 管徑 | 3/4"~42" |
| 分類 | Pipe Saddle Support（直接承托型） |
| 圖面數 | 2 頁 |
| 圖面編號 | E1906-DSP-500-006 |

---

## 系統本質

TYPE-51 是**直接承托型管線支撐**——管線直接坐在鞍座/支撐件上，
全部以焊接連接，無 bolt、無 clamp、無 lug。

與 TYPE-66（Pipe Shoe, 120° 包覆）不同：
- TYPE-51 的接觸角較小（80°），承托為主
- TYPE-66 是曲面適配介面層，用於分散應力

TYPE-51 是**結構型支撐（Structure Type）**，TYPE-66 是**介面型（Interface Type）**。

---

## 三種結構型態（依管徑 / 製造方式分級）

| 管徑範圍 | 結構型態 | 支撐件 | 來源 |
|:---:|------|------|:---:|
| **3/4"~3"** | Flat Bar 承托 | "H"×50×9 FLAT BAR，無 Member "M" | D-62 |
| **4"~24"** | 角鐵夾持承托 | Member "M"（L型角鐵）兩側對稱 | D-62 |
| **26"~42"** | 槽鋼 + 鞍座組裝 | C 型槽鋼 + 雙側板 + 中央 saddle | D-62A |

> 此分級反映**製造方式**，三者力學行為相同：管線靠自重坐在支撐面上。

---

## 尺寸表（D-62, 第1頁）

| LINE SIZE | MEMBER "M" | H (mm) |
|:---:|:---:|:---:|
| 3/4" | — | 25 |
| 1" | — | 30 |
| 1-1/2" | — | 45 |
| 2" | — | 60 |
| 2-1/2" | — | 70 |
| 3" | — | 80 |
| 4" | L50×50×6 | 125 |
| 5" | L50×50×6 | 125 |
| 6" | L50×50×6 | 125 |
| 8" | L65×65×6 | 150 |
| 10" | L65×65×6 | 150 |
| 12" | L65×65×6 | 200 |
| 14" | L65×65×6 | 200 |
| 16" | L65×65×6 | 250 |
| 18" | L65×65×6 | 300 |
| 20" | L65×65×6 | 300 |
| 24" | L65×65×6 | 300 |

### Member "M" 分組

| 管徑 | Member "M" |
|:---:|:---:|
| 3/4"~3" | 無（Flat Bar 代替） |
| 4"~6" | L50×50×6 |
| 8"~24" | L65×65×6 |

### H 值觀察

- H 是 **pipe 底部到 base 的支撐高度**（非管徑）
- 3"→80, 4"→125：跳躍明顯（對應從 Flat Bar 切換到角鐵結構）
- 12"~24" 範圍：H = 200~300，隨管徑漸增

---

## 大管補充表（D-62A, 第2頁）

| 管徑範圍 | 支撐件 |
|:---:|------|
| 26"~32" | C125×65×6 |
| 36"~42" | C150×75×9 |

### 第2頁結構特徵

- 雙側板 + 中央 saddle
- 鞍座包覆角：**80°**
- 三面焊接（3 SIDES TYP.）
- 側板高度：50mm
- REIN. PAD SEE SH'T **D-91**（Reinforcing Pad 另見圖紙）

---

## 幾何關鍵參數

| 參數 | 值 | 說明 |
|:---:|:---:|------|
| Pipe ↔ 側板間隙 | 3 mm（兩側） | 避免卡死，允許熱膨脹 |
| Saddle 包覆角 | 80°（D-62A） | 小於 TYPE-66 的 120° |
| Flat Bar 寬度 | 50 mm | 3" & smaller 專用 |
| Flat Bar 厚度 | 9 mm | 3" & smaller 專用 |
| 焊接尺寸 | 6V TYP. | 全焊接連接 |

---

## 連接方式

TYPE-51 **全部為焊接**，無任何螺栓/夾具連接：

| 連接 | 方式 |
|------|------|
| Pipe ↔ Saddle/Bar | 焊接 |
| Saddle/Bar ↔ Base | 焊接 |
| Side Plates ↔ Base | 焊接 |
| Member M ↔ Base | 焊接 |

> 第2頁特別標註 **3 SIDES TYP.** + **6V TYP.**，表示結構性焊接。

---

## 約束行為

| 自由度 | 狀態 | 說明 |
|:---:|:---:|------|
| 軸向（Axial） | **FREE** | 無 clamp/bolt 固定，管線可沿軸向滑動 |
| 橫向（Lateral） | **LIMITED** | 兩側 Member / Flat Bar + 3mm gap 提供鬆約束 |
| 垂直（Vertical ↓） | **RESTRAINED** | 管線靠自重坐在支撐面上 |
| 垂直（Vertical ↑） | **FREE** | 無 clamp，管線可被抬起 |
| 旋轉（Rotation） | **FREE** | 無鎖固機構 |

→ TYPE-51 本質上是 **REST SUPPORT**（承托型），非 Fixed Support。
管線可在軸向自由滑動，橫向受兩側構件鬆約束。

---

## Load Path（荷重路徑）

### 3" & Smaller

```
Pipe（水平）
→ Flat Bar（"H"×50×9）
→ Base Beam / Slab
```

### 4"~24"

```
Pipe（水平）
→ Saddle / 底面接觸
→ Member "M"（L型角鐵，兩側）
→ Base Beam / Slab
```

### 26"~42"

```
Pipe（水平）
→ Saddle（80° 弧面）
→ Side Plates + C-Channel
→ Base Beam / Slab
```

---

## 構件清單

### 3" & Smaller（Flat Bar 型）

| # | 構件 | 規格 |
|:---:|------|------|
| 1 | Flat Bar | "H"×50×9 |
| 2 | Weld | 6V TYP. |

### 4"~24"（角鐵型）

| # | 構件 | 規格 |
|:---:|------|------|
| 1 | Member "M" ×2 | L50×50×6（4"~6"）/ L65×65×6（8"~24"） |
| 2 | Base Plate / Saddle | 管線承托面 |
| 3 | Weld | 6V TYP. |

### 26"~42"（槽鋼組裝型）

| # | 構件 | 規格 |
|:---:|------|------|
| 1 | C-Channel ×2 | C125×65×6（26"~32"）/ C150×75×9（36"~42"） |
| 2 | Saddle | 80° 弧面，中央承托 |
| 3 | Side Plates | 高 50mm |
| 4 | Reinforcing Pad | SEE D-91（大管必要） |
| 5 | Weld | 6V, 3 SIDES TYP. |

### 不存在的構件

- Bolt / Nut
- Clamp
- Lug Plate
- Trunnion
- Shoe（TYPE-66）
- Brace（斜撐）
- Insulation 相關標註

---

## Designation（編碼格式）

### NOTE 1 格式

```
51-2B
│   └── DENOTE LINE SIZE（B = bore，吋）
└────── DENOTE TYPE NO.
```

### 格式

```
51-{size}B
```

> **無材質符號**——TYPE-51 的 designation 不含材料代碼。
> 圖面上無 TABLE "A"（材料表），這是與 Type 48/49/66 的重要差異。

### 範例

| 管徑 | Designation |
|:---:|:---:|
| 3/4" | 51-3/4B |
| 2" | 51-2B |
| 10" | 51-10B |
| 24" | 51-24B |

---

## NOTES 摘要

| NOTE | 內容 |
|:---:|------|
| 1 | Designation 格式（見上方拆解） |
| 2 | **Member 最大長度不得超過 Beam 寬度** |

> NOTE 2 是重要設計約束：支撐構件長度受限於所坐落的梁寬。

---

## 設計流程

```
1. 確定: LINE SIZE (3/4"~42")
2. 選結構型態:
   - ≤3" → Flat Bar 承托（D-62）
   - 4"~24" → 角鐵夾持承托（D-62）
   - 26"~42" → 槽鋼組裝承托（D-62A）
3. 查尺寸表:
   - ≤24" → D-62 主表（H, Member "M"）
   - 26"~42" → D-62A 補充表
4. 確認 Member 長度 ≤ Beam 寬度（NOTE 2）
5. 大管確認 Reinforcing Pad 需求（D-91）
6. 編碼: 51-{size}B
```

---

## 與 TYPE-66 的差異（關鍵比較）

| 比較項 | TYPE-51 | TYPE-66 |
|------|------|------|
| 角色 | **Structure**（直接承托） | **Interface**（曲面適配） |
| 接觸角 | 80° | 120° |
| 管徑 | 3/4"~42" | 1/2"~42" |
| 獨立使用 | ✅ 直接坐落 beam | ❌ 需搭配 Type 46/47 |
| 應力分散 | 較集中 | 較分散（120° 面接觸） |
| 保溫考量 | 無（未標） | 有（HOPS from TABLE A） |
| 焊接 | 全焊接 | 全焊接 |
| 用途 | 管線直接架設於梁上 | 管線需經 shoe 轉接到支撐架 |

> TYPE-51 解決的是「撐住 pipe」；TYPE-66 解決的是「讓 pipe 不被壓壞」。

---

## 關聯 Type

| 關聯 Type | 關係 |
|------|------|
| **Type 66** | 不同族群：TYPE-66 是介面層 shoe，TYPE-51 是結構層直接承托 |
| Type 44~47 | 不同場景：44~47 是 Vessel 支撐架，51 是 Beam 上直接承托 |
| Type 48 | 不同場景：48 是落地偏移底座（Drain Hub），51 是梁上承托 |
| Type 49 | 不同場景：49 是立管(Riser)固定，51 是水平管承托 |
| **D-91** | Reinforcing Pad（大管 26"~42" 補強用） |

---

## 系統分層定位

```
SYSTEM LAYERS:

Pipe（水平）
↓
Support Layer        → TYPE-51 Saddle / Flat Bar / C-Channel
↓
Base                 → Beam / CONC. SLAB / STEEL
```

### 與其他 Type 的分層差異

```
Type 44~47: Pipe → [Interface] → Structure → Vessel    （Vessel 掛管）
Type 48:    Pipe → Offset Plate → GRADE                 （小管落地）
Type 49:    Pipe → Riser Clamp → CONC/STEEL             （立管固定）
Type 51:    Pipe → Saddle/Bar → Beam                    （梁上承托）
Type 66:    Pipe → Shoe(120°) → [需搭配上層 Type]        （介面轉接）
```

> TYPE-51 是目前已分析 Type 中唯一的**梁上直接承托型**——
> 管線直接坐在支撐件上，靠自重固定，無任何機械夾固。
