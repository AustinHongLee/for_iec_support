# Type 41 — 牆面錨定支撐 (Wall-Mounted Anchor Support)

> **圖號**: 41 &nbsp;|&nbsp; **分類**: 支撐型式 &nbsp;|&nbsp; **狀態**: 🔲 計畫中
> **圖面編號**: E1906-DSP-500-006 &nbsp;|&nbsp; **圖面頁**: D-49 &nbsp;|&nbsp; **日期**: 12/12/19

用膨脹螺栓 (Expansion Bolt, M-45) 鎖在混凝土上的懸臂/斜撐支撐。
FIG-A 單懸臂型，FIG-B 附斜撐強化型。
**整套系統中從「焊接→機械錨定」的關鍵轉折點。**

---

## 結構示意圖

### FIG-A（單懸臂）

```
      ┌──── L ────┐ 200
      │            ├──┤
      │  MEMBER 1  │
  ════╪════════════╡  P (管線)
      │            │
  ┌───┤ BASE PLATE │
  │ ⊙ │ (TH'K = T)│
  │ ⊙ │            │
  └───┘            │
  EXPANSION BOLT   │
  SEE M-45         │
  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
  混凝土牆 (CONCRETE)
```

### FIG-B（斜撐強化）

```
      ┌──── L ────┐ 200
      │            ├──┤
      │  MEMBER 1  │
  ════╪════════════╡  P (管線)
      │          ╱ │
  ┌───┤ MEMBER 2╱  │  ← 斜撐
  │ ⊙ │       ╱   │
  │ ⊙ │     ╱     │
  └───┘   ╱       │
  EXPANSION BOLT   │
  SEE M-45         │
  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
  混凝土牆 (CONCRETE)
```

**力傳遞**：管線 → MEMBER → Base Plate → Expansion Bolt (M-45) → 混凝土

---

## 本質與定位

| 系統 | 固定方式 | 固定目標 |
|------|---------|---------|
| Type 26~37 | 焊接 | 鋼構 |
| Type 39 | Bolt + Lug Plate | Vessel |
| **Type 41** | **Expansion Bolt** | **混凝土** |

> 第一次出現「結構→混凝土傳力」的 Type。

### FIG-A vs FIG-B

| 型式 | 結構 | 對應概念 |
|:---:|------|------|
| FIG-A | 單懸臂（Member 1 only） | 類似 Type 34（懸臂立柱） |
| FIG-B | 懸臂 + 斜撐（Member 1 + 2） | 類似 Type 37（斜撐懸臂） |

> 41-1~41-4 = FIG-A（無 Member 2）；41-5~41-9 = FIG-B（有 Member 2）。

---

## 編碼格式

**格式**: `41-{n}`

| 段位 | 意義 |
|:---:|------|
| 41 | Type 編號 |
| n | 系列號 1~9，直接對應距離/構件組合 |

> 不像其他 Type 用 Member+長度編碼，Type 41 是**固定規格表**，直接選號。

---

## 尺寸表

| SUPPORT NO. | L (mm) | MEMBER 1 | MEMBER 2 | BASE PLATE T (mm) | EXP. BOLT DIA | BOLT DIST (mm) | WELD SIZE (mm) | b (mm) | FIG |
|:---:|:---:|------|------|:---:|:---:|:---:|:---:|:---:|:---:|
| 41-1 | 230 | L50X50X6 | — | 16 | 1/2" | 150 | 5 | 25 | A |
| 41-2 | 460 | L75X75X9 | — | 16 | 5/8" | 200 | 6 | 30 | A |
| 41-3 | 610 | L100X100X10 | — | 19 | 3/4" | 230 | 6 | 35 | A |
| 41-4 | 915 | H150X150X7 | — | 19 | 3/4" | 250 | 6 | 35 | A |
| 41-5 | 610 | L75X75X9 | L75X75X9 | 16 | 5/8" | 200 | 6 | 30 | B |
| 41-6 | 915 | L75X75X9 | L75X75X9 | 16 | 5/8" | 200 | 6 | 30 | B |
| 41-7 | 1220 | L75X75X9 | L100X100X10 | 19 | 3/4" | 230 | 6 | 35 | B |
| 41-8 | 915 | H150X150X7 | L100X100X10 | 19 | 3/4" | 250 | 6 | 35 | B |
| 41-9 | 1220 | H150X150X7 | L100X100X10 | 19 | 3/4" | 250 | 6 | 35 | B |

---

## 欄位說明

| 欄位 | 意義 |
|:---:|------|
| L | 懸臂距離（管中心到牆面） |
| MEMBER 1 | 主梁（水平懸臂段） |
| MEMBER 2 | 斜撐（FIG-B 才有） |
| BASE PLATE T | 底板厚度 (mm) |
| EXP. BOLT DIA | Expansion Bolt 直徑（對應 M-45 查表） |
| BOLT DIST | 螺栓中心距 |
| WELD SIZE | 焊道尺寸（member 與 base plate 間） |
| b | 底板邊緣距 |

---

## BOM 組成

| # | 項目 | 來源 | 備註 |
|:---:|------|------|------|
| 1 | Member 1（主梁） | 型鋼，長度 = L | 全系列皆有 |
| 2 | Member 2（斜撐） | 型鋼 | FIG-B (41-5~41-9) 才有 |
| 3 | Base Plate | 鋼板 T=16/19mm | A283 Gr. C |
| 4 | Expansion Bolt | M-45 查表 | 1/2"~3/4"，含 washer/nut |
| 5 | 焊接 | Member ↔ Base Plate | 全周焊，size = 5~6mm |

---

## 材質規定

| 構件 | 材質 |
|:---:|------|
| Base Plate | A283 Gr. C |
| Shape Steel | A36 |

---

## 運算邏輯

```
1. 依管線載荷與懸臂距離選擇 SUPPORT NO. (41-1 ~ 41-9)
2. 判定 FIG 型式：
   - 無 Member 2 → FIG-A (41-1~41-4)
   - 有 Member 2 → FIG-B (41-5~41-9)
3. 查表得 L, Member 1/2, Base Plate T, Bolt DIA, Dist, Weld, b
4. Expansion Bolt 規格由 M-45 查表（DIA → EB-{size}）
5. BOM:
   - Member 1 ×1 (長度=L)
   - Member 2 ×1 (FIG-B only)
   - Base Plate ×1 (A283 Gr.C, T=16/19)
   - Expansion Bolt ×4 set (M-45 查表, 含 washer/nut)
```

---

## 與其他 Type 比較

| 比較項 | Type 34 | Type 37 | Type 41 |
|--------|---------|---------|---------|
| 安裝目標 | Existing Steel | Existing Surface | **Concrete** |
| 固定方式 | 焊接 | 焊接 | **Expansion Bolt** |
| 斜撐 | 無 | 有 | FIG-B 有 |
| 底板 | 無 | 無 | **有 (A283)** |
| 鑽孔 | 無 | 無 | **R.C. 鑽孔** |

---

## 關聯零件

| 零件 | 用途 |
|------|------|
| M-45 (Expansion Bolt) | 混凝土錨定，含載荷限制表 |
