# TYPE-49 — Riser Support（立管固定支撐）

| 項目 | 內容 |
|------|------|
| 圖號 | D-60 |
| 管徑 | 3/4"~20" |
| 分類 | Riser Support（立管固定） |
| 圖面數 | 1 頁 |
| 圖面編號 | E1906-DSP-500-006 |
| 狀態 | ✅ 已實作 |

---

## 系統本質

TYPE-49 **不是**傳統意義上的承重支撐架（如 Type 44~47）。

它是**立管固定裝置（Riser Support）**——用於控制垂直管線（riser）的位置，
防止軸向滑動、橫向位移與旋轉。承重僅為附帶功能。

典型場景：設備區、樓板穿管、立管固定。

---

## 兩種組態（FIG-A / FIG-B）

| 組態 | 管徑 | Riser Clamp | Lug Plate | 適用場景 |
|:---:|:---:|:---:|:---:|------|
| **FIG-A** | 3"~20" | TYPE-A（M-11） | TYPE-P（M-41） | 大管：需 Lug Plate 分散力 |
| **FIG-B** | 3/4"~20" | TYPE-B（M-12） | 無 | 小管：Clamp 直接固定 |

> ⚠️ NOTE 2 明確標註：LUG PLATE TYPE-P 僅用於 **3" & LARGER**。
>
> 推論：小管（< 3"）一律用 FIG-B；大管（≥ 3"）可選 FIG-A 或 FIG-B，
> 但工程上 ≥ 3" 通常使用 FIG-A（有 Lug Plate 分散集中荷重）。

---

## 基座

兩種 FIG 共用相同基座條件：

```
CONC. SLAB OR STEEL
```

即混凝土板或鋼構平面——非 Vessel、非 Grade。

---

## Load Path（荷重路徑）

### FIG-A（有 Lug Plate）

```
Pipe（垂直）
→ Riser Clamp TYPE-A（M-11）
→ Lug Plate TYPE-P（M-41）
→ Base（CONC. SLAB / STEEL）
```

### FIG-B（無 Lug Plate）

```
Pipe（垂直）
→ Riser Clamp TYPE-B（M-12）
→ Base（CONC. SLAB / STEEL）
```

---

## 約束行為

| 自由度 | 約束狀態 |
|:---:|:---:|
| 軸向（Axial） | **固定** |
| 橫向（Lateral） | **固定** |
| 旋轉（Rotation） | **限制** |

→ TYPE-49 為局部 **FIXED SUPPORT**——不允許滑動、不允許導引，
比 Type 44~47 的「承重支撐」更接近「位置鎖定」。

---

## 構件清單

### 一定存在

| 構件 | 說明 |
|------|------|
| Pipe（垂直） | Riser，被支撐對象 |
| Riser Clamp | TYPE-A（M-11）或 TYPE-B（M-12） |
| Base | CONC. SLAB 或 STEEL |
| Bolt | Clamp 鎖固用（隱含） |

### 條件存在

| 構件 | 條件 |
|------|------|
| Lug Plate TYPE-P（M-41） | 僅 FIG-A，3" & LARGER |

### 不存在

- Brace（斜撐）
- Beam（橫梁）
- Trunnion
- Shoe（TYPE-66）
- Insulation 標註

---

## TABLE "A"（材料符號）

| 材質 | 符號 |
|:---:|:---:|
| CARBON STEEL | NONE |
| ALLOY STEEL | (A) |
| STAINLESS STEEL | (B) |

> 注意：SS 符號 **(B)** 與 Type 48 相同，但與 Type 66 的 **(S)** 不同。
> 各 Type 的 TABLE 符號系統互相獨立。

---

## Designation（編碼格式）

### NOTE 1 格式

```
49-3/4B-A(A)
│   │  │  └── SEE TABLE "A"（材質符號）
│   │  └──── DENOTE FIG. NO.（A 或 B）
│   └──────── DENOTE SUPPORTED LINE SIZE
└──────────── DENOTE TYPE NO.
```

### 格式

```
49-{size}{fig}{mat_symbol}
```

### 範例

| 管徑 | FIG | 材質 | Designation |
|:---:|:---:|:---:|:---:|
| 3/4" | B | CS | 49-3/4B |
| 2" | B | AS | 49-2B(A) |
| 6" | A | CS | 49-6A |
| 6" | A | SS | 49-6A(B) |
| 20" | A | AS | 49-20A(A) |

---

## 設計流程

```
1. 確定: LINE SIZE (3/4"~20"), 管材
2. 選擇組態:
   - pipe_size ≥ 3" → FIG-A（Lug Plate + Riser Clamp TYPE-A）
   - pipe_size < 3" → FIG-B（Riser Clamp TYPE-B 直接固定）
3. 查 TABLE "A": 管材 → 材質符號
4. 確認 Base 類型（CONC. SLAB / STEEL）
5. 編碼: 49-{size}{fig}{mat_symbol}
```

---

## Riser Clamp 差異

| 型號 | 名稱 | 搭配組態 | 推定用途 |
|:---:|------|:---:|------|
| M-11 | RISER CLAMP TYPE-A | FIG-A | Heavy duty，搭配 Lug Plate 使用 |
| M-12 | RISER CLAMP TYPE-B | FIG-B | Light duty，直接壓於 Base |

> M-11 和 M-12 的詳細尺寸見各自的 component 圖紙。
> TYPE-A vs TYPE-B 的差異推定為承載等級不同（圖面未明示）。

---

## 關聯 Type

| 關聯 Type | 關係 |
|------|------|
| **M-11** | Riser Clamp TYPE-A（FIG-A 專用） |
| **M-12** | Riser Clamp TYPE-B（FIG-B 專用） |
| **M-41** | Lug Plate TYPE-P（FIG-A，3" & LARGER） |
| Type 44~47 | 不同族群——Type 44~47 是 Vessel 支撐；TYPE-49 是 Riser 固定 |
| Type 48 | 不同族群——Type 48 是落地偏移底座 |
| Type 66 | 無關——TYPE-49 不使用 Shoe |

---

## 系統分層定位

```
SYSTEM LAYERS:

Pipe（垂直 Riser）
↓
Interface Layer      → Riser Clamp（M-11 / M-12）
↓
(Optional) Lug       → Lug Plate TYPE-P（M-41），≥3" only
↓
Support Base         → CONC. SLAB / STEEL
```

### 與其他 Type 的差異

```
Type 44~47: 水平管 → 支撐架 → Vessel      （承重為主）
Type 48:    水平管 → 偏移底座 → GRADE       （小管落地）
Type 49:    垂直管 → Riser Clamp → Base     （位置固定為主）
```

> TYPE-49 是目前已分析 Type 中唯一專門處理**垂直管線**（Riser）的固定型式。

---

## 圖面 NOTES 摘要

| NOTE | 內容 |
|:---:|------|
| 1 | Designation 編碼格式（見上方拆解） |
| 2 | LUG PLATE TYPE-P（M-41）FOR 3" & LARGER |
