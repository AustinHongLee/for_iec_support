# Type 22 — 落地式懸臂 U-bolt 支撐

| 項目 | 內容 |
|------|------|
| 中文名稱 | 落地式懸臂 U-bolt 支撐 |
| 英文名稱 | Ground Cantilever Clamp Support |
| 圖號 | E1906-DSP-500-006 D-24 |
| 適用範圍 | — |
| PDF | `22.pdf` |
| 狀態 | ✅ 已分析 |

---

## 系統本質

Type 21 的落地版，有 base plate + M42 下部構件。U-bolt NOT FURNISHED。

Member M (Angle) H段+L段 + M42(L/P only)。Fig.A=L300, Fig.B=L500, Fig.C=自L。焊接於 base plate，接地面/基礎。

---

## 編碼格式

```text
22-{M}-{HH}{Fig}{M42} or 22-{M}-{HH}C{M42}-{LL}
```

---

## 核心運算邏輯

```text
2+M42 components: Member(H) + Member(L) + M42 lower. Members: L50(H≤1000), L65(H≤1000), L75(H≤1500).
```

---

## 設計重點

- 與 `M-42` 下部構件有關，最終組成會受到末段字母或允許型別限制。
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
