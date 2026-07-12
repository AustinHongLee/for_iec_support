# Type 23 — 頂掛式懸臂支撐

| 項目 | 內容 |
|------|------|
| 中文名稱 | 頂掛式懸臂支撐 |
| 英文名稱 | Top-mounted Cantilever Support |
| 圖號 | E1906-DSP-500-006 D-25 |
| 適用範圍 | — |
| PDF | `23.pdf` |
| 狀態 | ✅ 已分析 |

---

## 系統本質

從上方既有結構向下懸掛的支撐架。無 U-bolt、無 M42、無滑動。

Member M (Angle/Channel/H Beam) H段+L段。Fig.A=L300, Fig.B=L500, Fig.C=自訂L。L50~H150 共 8 種型鋼。

---

## 編碼格式

```text
23-{M}-{HH}{Fig} or 23-{M}-{HH}{Fig}-{LL}
```

---

## 核心運算邏輯

```text
2 components: Member(H) + Member(L). L50(H≤500), L65(H≤1500), others(H≤2000). H150 uses 7mm.
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
