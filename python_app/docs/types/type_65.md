# TYPE-65 — Trapeze Hanger with Cross Member

| 項目 | 內容 |
|------|------|
| 圖號 | D-79 |
| 分類 | Trapeze / cross-member hanger |
| 適用範圍 | 2"~24" |
| 圖面頁數 | 1 |
| 狀態 | ✅ 已分析（待 calculator） |

---

## 系統本質

TYPE-65 是典型的 trapeze hanger：

- 上方以 `ANGLE BRACKET (M-28)` 固定
- 垂直件是 `"A" WELDED EYE ROD (M-23)`
- 下方橫梁是 `MEMBER "M"`
- 被支撐管線放在橫梁上

這種型式的計算重點非常明確：

- 2 支吊桿
- 2 個 angle bracket
- 1 支橫向 member
- 必要時 12" 以上加 stiffener

---

## 編碼格式

圖面範例：

```text
65-2B-1505
```

拆解如下：

- `65` = Type 編號
- `2B` = equivalent line size `D`
- `15` = `L` 尺寸（100 mm）
- `05` = `H` 尺寸（100 mm）

所以格式可整理為：

```text
65-{D}B-{LLHH}
```

其中：

- `L = LL × 100 mm`
- `H = HH × 100 mm`

---

## 圖面表格

表格欄位：

| 欄位 | 含義 |
|------|------|
| `LINE SIZE "D"` | 等效管徑 |
| `ROD SIZE "A"` | 吊桿尺寸 |
| `MEMBER "M"` | 依不同 `L` 區間選用型鋼 |
| `Y` | 焊角尺寸 |

`MEMBER "M"` 不是單一欄，而是分成：

- `L=500`
- `L=1000`
- `L=1500`
- `L=2000`
- `L=2500`

這代表 calculator 必須先把輸入的 `L` 落到對應欄位，再選出 member。

---

## 12" & Larger 的補強

圖面左側另外畫了：

- `STIFFENER FOR 12" & LARGER`

所以 Claude 實作時要把這件事當成條件邏輯：

- 若 `D >= 12"`，除基本 member 外，還要再加 stiffener plate

如果第一版不確定 stiffener 展開尺寸如何建模，也至少要：

- 加 remark
- 或用 custom plate entry 佔位

---

## Calculator Handoff

### 最小輸入

```text
65-{line_size}B-{LLHH}
```

### BOM 建議

| 構件 | 數量 | 來源 |
|------|------|------|
| Angle Bracket | 2 | `M-28`, size = rod size `A` |
| Welded Eye Rod | 2 | `M-23`, size = `A`, length ≈ `H` |
| Cross Member | 1 | 依 `D` 與 `L bucket` 查 `MEMBER "M"` |
| Washer / Hex Nut | 視系統策略 | 圖面有標示 |
| Stiffener | 條件式 | `D >= 12"` |

### 建議 table

```python
TYPE65_TABLE = {
    '2': {
        'rod_size': '3/8"',
        'member_by_l': {
            500: 'L65X65X6',
            1000: 'L65X65X6',
            1500: 'L75X75X9',
            2000: 'L90X90X10',
            2500: 'L90X90X10',
        },
        'weld_y': 6,
    },
}
```

### 實作重點

- `L` 為 bucket 化尺寸，不是連續公式
- `H` 主要對應 rod 長度
- `Dimension "L" shall be cut to suit in field`，所以超出 bucket 的輸入需要你決定是：
  - 向上取最接近 bucket
  - 或限制只能輸入 500/1000/1500/2000/2500

我會建議第一版先只接受這五種標準值，最穩。

---

## 與相近 Type 的差異

| Type | 本質 | 差異 |
|------|------|------|
| `64` | 兩條管之間的 rod hanger | `65` 是由上部結構吊一支橫梁來承管 |
| `31/32` | 框架式鋼構支撐 | `65` 是吊掛，不是立柱或框架 |

---

## 給 Claude 的一句話摘要

> TYPE-65 = `line size D` 先決定 rod size，再用 `L bucket` 選 cross member；BOM 主要是 `2 rods + 2 angle brackets + 1 member + optional stiffener`。
