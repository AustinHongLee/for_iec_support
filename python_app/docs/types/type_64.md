# TYPE-64 — Pipe-to-Pipe Rod Hanger

| 項目 | 內容 |
|------|------|
| 圖號 | D-78 |
| 分類 | Rod hanger between supporting line and supported line |
| 適用範圍 | Supported line `E` = 1/2"~12" |
| 圖面頁數 | 1 |
| 狀態 | ✅ 已分析（待 calculator） |

---

## 系統本質

TYPE-64 是「由上方管線吊下方管線」的 rod hanger。

圖面中有兩條管：

- `SUPPORTING LINE SIZE "F"` = 上方承載管
- `SUPPORTED LINE SIZE "E"` = 下方被吊掛的管

中間用的構件是：

- pipe clamp `TYPE-A (M-4)` 或 `TYPE-C (M-6)`
- `WELDLESS EYE NUT (M-25)`
- `MACHINE THREADED ROD (M-22)`

本質上這不是鋼構吊架，而是 `pipe-to-pipe hanger`。

---

## 四種 Figure

圖面有 `FIG-A ~ FIG-D` 四種變體，代表上下端 clamp 組合不同。

對 calculator 最重要的事不是重新解圖，而是：

- figure 會影響上端 / 下端使用哪種 clamp
- 其餘共同件仍是 `rod + eye nut + nut`

如果第一版無法完全把 4 種 clamp 組合辨識乾淨，建議先把它做成 `FIG → clamp preset` 對照表。

---

## 編碼格式

圖面範例：

```text
64-2-8-05A
```

拆解如下：

- `64` = Type 編號
- `2` = supported line size `E`
- `8` = supporting line size `F`
- `05` = `H` 尺寸，單位 100 mm
- `A` = figure no.

所以格式可整理成：

```text
64-{E}-{F}-{HH}{FIG}
```

---

## 圖面限制

圖面直接寫出：

- `500 ≤ H ≤ 3000`
- `SUPPORTING LINE MUST BE SIZED TO CARRY TOTAL SUPPORT LOAD`

這代表 calculator 至少要做兩件事：

- 驗證 `H` 範圍
- 把 `F` 當作必要輸入，不是由 `E` 自動推導

---

## 表格欄位

圖面中央表格只有兩欄：

| 欄位 | 含義 |
|------|------|
| `E` | supported line size |
| `G` | rod / thread size |

所以 `rod size` 只由被吊掛管徑 `E` 決定。

註記 `*` 表示某些列只用於 `FIG-B` 與 `FIG-C`，Claude 實作時應把這件事寫入 table metadata。

---

## Calculator Handoff

### 最小輸入

```text
64-{supported_size}-{supporting_size}-{H}{fig}
```

### BOM 建議

| 構件 | 數量 | 來源 |
|------|------|------|
| Upper clamp | 2 half / 1 set | `M-4` 或 `M-6`，依 figure |
| Lower clamp | 2 half / 1 set | `M-4` 或 `M-6`，依 figure |
| Weldless eye nut | 2 | `M-25`, size = `G` |
| Threaded rod | 2 | `M-22`, size = `G`, length ≈ `H` |
| Heavy hex nut | 若系統需要 | 圖面標示存在 |

### 建議 table

```python
TYPE64_ROD_TABLE = {
    '1/2': {'g': '3/8"', 'fig_bc_only': False},
}

TYPE64_FIGURE_MAP = {
    'A': {'upper_clamp': 'M-6', 'lower_clamp': 'M-6'},
    'B': {'upper_clamp': 'M-6', 'lower_clamp': 'M-4'},
    'C': {'upper_clamp': 'M-4', 'lower_clamp': 'M-6'},
    'D': {'upper_clamp': 'M-4', 'lower_clamp': 'M-4'},
}
```

### 實作重點

- rod 長度第一版可直接用 `H * 100`
- `LH` 在圖面上是局部調整長度，若目前系統沒有組裝級建模，可先不獨立輸出
- `supporting size F` 主要是編碼與 engineering constraint，不一定直接影響 BOM

---

## 與相近 Type 的差異

| Type | 本質 | 差異 |
|------|------|------|
| `65` | 吊桿 + 橫向 member 的吊架 | `64` 沒有橫梁，直接從上管吊下管 |
| `21/22/23` | 鋼構懸臂/吊掛 | `64` 的支點是另一條管，不是鋼構 |

---

## 給 Claude 的一句話摘要

> TYPE-64 = 以 `supported size E` 查 rod size `G`，再依 `FIG-A~D` 決定上下端 clamp 類型；第一版重點是 clamp 組合與 rod 長度，不是細部裝配尺寸。
