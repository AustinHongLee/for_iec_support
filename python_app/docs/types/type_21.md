# Type 21 — 側掛式懸臂 U-bolt 支撐

| 項目 | 內容 |
|------|------|
| 中文名稱 | 側掛式懸臂 U-bolt 支撐 |
| 英文名稱 | Cantilever Clamp Support (Side-Mounted) |
| 圖號 | E1906-DSP-500-006 D-23 |
| 適用範圍 | — |
| PDF | `21.pdf` |
| 狀態 | ✅ 已分析 |

---

## 系統本質

固定在 existing steel 上的側掛式支架，無滑動功能。U-bolt NOT FURNISHED。

Member M (Angle) H段+L段組成懸臂支架。Fig.A=L300, Fig.B=L500, Fig.C=自定L。焊接於既有鋼構。

---

## 編碼格式

```text
21-{M}-{HH}{Fig} or 21-{M}-{HH}C-{LL}  M=型鋼, HH=H/100, Fig=A/B/C, LL=L/100(Fig.C only)
```

---

## 核心運算邏輯

```text
2 components: Member M (H vertical) + Member M (L horizontal). Members: L50(H≤1000), L65(H≤1500), L75(H≤2000).
```

---

## 設計重點

- 此型式不依賴 `M-42` 下部構件，主要由本體鋼材或既有結構承載。
- 圖面若標示 `U-bolt NOT FURNISHED`，現行 calculator 不會把該夾具列入 BOM。

---

## 與相近 Type 的關係

| 類別 | 型式 | 說明 |
|------|------|------|
| 懸臂 / 側掛家族 | 21 / 22 / 23 / 25 / 26 / 30 / 33 / 34 | 差異主要在安裝基準面、是否落地，以及是單梁還是框架。 |

---

## 備註

- 本文件先依現有 `calculator`、`type_catalog.json` 與圖面可辨識資訊整理。
- 若後續需要進一步資料化，可再補 `幾何參數表`、`BOM 結構表`、`PDF note 摘要` 與 `限制條件矩陣`。
