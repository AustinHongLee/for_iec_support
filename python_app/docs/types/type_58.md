# TYPE-58 — U-Bolt Plate Saddle on Steel Plate / Shape Steel

| 項目 | 內容 |
|------|------|
| 圖號 | D-69 |
| 分類 | U-bolt clamp support |
| 適用範圍 | 1/4"~30" |
| 圖面頁數 | 1 |
| 狀態 | ✅ 已分析（待 calculator） |

---

## 系統本質

TYPE-58 是最直接的 `U-bolt + steel plate` 夾持式支撐。

它不是 shoe，也不是 pipe clamp 家族，而是把主管直接用 `M-26 U-bolt` 壓在一塊鋼板上，再把該鋼板安裝到支撐面。

圖面分成兩種安裝基準：

- `FIG-A`: 鋼板直接放在平板或支撐板上
- `FIG-B`: 鋼板放在型鋼上，增加一個 `X` 尺寸控制支撐高度

所以對 calculator 來說，TYPE-58 的核心不是幾何推導，而是：

- 依 line size 查表選對 `rod size`
- 建立一塊 steel plate
- 加上一組 `U-bolt (M-26)`
- `FIG-B` 額外記錄支撐面為 shape steel，並帶出 `X`

---

## 編碼格式

```text
58-{line_size}B-{FIG}
例: 58-1/2B-A
```

拆解如下：

- `58` = Type 編號
- `{line_size}B` = 管徑
- `{FIG}` = `A` 或 `B`

---

## 圖面構件

| 構件 | 來源 | 說明 |
|------|------|------|
| U-bolt | `M-26` | 主管固定件，圖面直接標 `U-BOLT SEE M-26` |
| Steel Plate | 本圖查表 | 用 `L×B×T` 定義 |
| Hole ×2 | 本圖查表 | `2-ØD HOLES` |
| Hole spacing | 本圖查表 | `P` |
| Offset `X` | 本圖查表 | 僅圖中 `FIG-B` 有意義 |

---

## 圖面表格欄位

圖面表格欄位如下：

| 欄位 | 含義 |
|------|------|
| `LINE SIZE` | 管徑 |
| `ROD SIZE` | 對應 U-bolt / rod 尺寸 |
| `D` | 兩孔孔徑 |
| `P` | 兩孔中心距 |
| `L×B×T` | 鋼板長、寬、厚 |
| `X` | 與型鋼安裝相關的額外尺寸 |

對 Claude 來說，最穩的資料模型是直接把這張表建成 `type58_table.py`，不要再從公式推導。

---

## Calculator Handoff

建議 calculator 只做查表與構件拼裝，不做幾何重建。

### 最小輸入

```text
58-{size}B-{fig}
```

### 建議輸出構件

| 構件 | 數量 | 來源 |
|------|------|------|
| Steel Plate | 1 | `L×B×T` |
| U-bolt set | 1 | `M-26`, rod size 來自表格 |

### 建議資料表結構

```python
TYPE58_TABLE = {
    "1/2": {
        "rod_size": '1/4"',
        "hole_d": 8,
        "hole_pitch": 30,
        "plate_l": 90,
        "plate_b": 50,
        "plate_t": 6,
        "x": 4,
    },
}
```

### 實作決策

- `FIG-A` 與 `FIG-B` 使用同一張尺寸表
- `FIG` 主要影響 remark / 安裝型態，不一定影響 BOM 數量
- 若目前系統還沒有 `M-26` table，可先以 custom entry 佔位，後續再接 component table

---

## 與相近 Type 的差異

| Type | 本質 | 差異 |
|------|------|------|
| `57` | U-bolt 直接固定在既有鋼構 | `58` 多了一塊明確尺寸化的 steel plate |
| `59` | Lug plate + shoe / U-bolt | `58` 沒有 lug plate，也不處理 insulation / material symbol |
| `60` | 大口徑 shoe 側板支撐 | `58` 是純 U-bolt 壓板做法，結構簡單得多 |

---

## 給 Claude 的一句話摘要

> TYPE-58 = `line size` 查表後，建立 `1 plate + 1 U-bolt set`；`FIG` 只決定安裝型態，不需要做複雜幾何運算。
