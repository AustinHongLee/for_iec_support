# Type 10 — 可調式四螺栓平台支撐

| 項目 | 內容 |
|------|------|
| 中文名稱 | 可調式四螺栓平台支撐 |
| 英文名稱 | Four-Bolt Adjustable Dummy Pipe Support |
| 圖號 | STM-05.10 |
| 適用範圍 | 1.5"~44" |
| PDF | `10.pdf` |
| 狀態 | ✅ 已分析 |

---

## 系統本質

透過 Plate F + 4支 Adjustable Bolt (J bolt) 做現場精調的 dummy pipe 支撐，比 Type-09 更穩定。

Type 10 以 supporting pipe B 承接主線，下方以 Plate F (有鑽孔) + 4支 J bolt 做四點式高度與水平調整，再落在垂直支撐柱上。適用 1.5"~44" 管徑，H≤1500mm。NOTE 6: 禁用於溫度≤10°C或96≥400°C，壓力≥70Kg/cm²G。

目前圖面可見彎頭型與插管型兩種實作，但現行 designation 無法區分；計算器暫採共同下料基準，後續若圖號或輸入欄位可分辨時再拆 variant。

---

## 編碼格式

```text
10-{A}B-{H}{M42字母}
```

---

## 核心運算邏輯

```text
Main Pipe(dummy/上段管) = L+100+100mm, 暫定 SUS304
Support Pipe(垂直下段管) = H-100-100-100mm, 暫定 A53Gr.B
Plate F: W×W×t (有鑽孔), 2 PC
Adj.Bolt(J): 4EA
Hex Nut: 16EA (鎖 ADJ.BOLT)
M42底板(用pipe_size_B查表)
```

---

## 設計重點

- 與 `M-42` 下部構件有關，最終組成會受到末段字母或允許型別限制。
- `H`、`L` 或 `Hx` 等尺寸多為現場裁切值，文件中的公式代表估算與下料邏輯。

---

## 與相近 Type 的關係

| 類別 | 型式 | 說明 |
|------|------|------|
| Dummy Pipe 家族 | 01 / 07 / 09 / 10 / 11 / 12 / 13 / 16 | 共通點是從主管引出支撐腿，再決定底部承載或限制方式。 |

---

## 備註

- 本文件先依現有 `calculator`、`type_catalog.json` 與圖面可辨識資訊整理。
- 若後續需要進一步資料化，可再補 `幾何參數表`、`BOM 結構表`、`PDF note 摘要` 與 `限制條件矩陣`。
