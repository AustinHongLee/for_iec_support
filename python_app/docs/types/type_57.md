# Type 57 — U型螺栓鋼構直接固定支撐

| 項目 | 內容 |
|------|------|
| 中文名稱 | U型螺栓鋼構直接固定支撐 |
| 英文名稱 | U-Bolt on Existing Steel |
| 圖號 | D-68 |
| 適用範圍 | 1/4"~30" |
| PDF | `57.pdf` |
| 狀態 | ✅ 已分析 |

---

## 系統本質

以 U-Bolt 直接固定於既有鋼構，最低成本基本支撐。FIG-A: SLIDE, FIG-B: FIXED。

TYPE-57 不是工程化支撐系統，而是使用 U-bolt 直接夾持於既有鋼構的最低成本安裝方案。僅適用碳鋼管、非保溫管、非高溫管、非關鍵管線。構件為 U-BOLT (ref M-26) + FINISHED HEX NUT x4，無底板、無 Shoe、無 Clamp。

---

## 編碼格式

```text
57-{line_size}B-{mode(A/B)}
```

---

## 核心運算邏輯

```text
1. LINE SIZE → 查 M-26 取得 U-BOLT 規格、rod size、B/C/D/E 與 load
2. BOM: U-BOLT (ref M-26, 1 SET) + FINISHED HEX NUT (4 PCS)
3. 幾何尺寸 B/C/D/E 與 load 由 M-26 table 提供
```

---

## 設計重點

- 此型式不依賴 `M-42` 下部構件，直接以 M-26 U-bolt 固定於既有鋼構。
- M-26 NOTE 1 指定材質為 Carbon Steel U-bolt and four finished hex nuts。
- 目前 U-bolt 幾何與 load 已接 M-26；重量仍為 placeholder，待 M-26 weight policy 補齊。

---

## 與相近 Type 的關係

| 類別 | 型式 | 說明 |
|------|------|------|
| Pipe Shoe / Clamp 家族 | 52 / 53 / 54 / 55 / 56 / 57 / 61 / 66 / 67 | 建議對照同族型式的約束行為與附件需求。 |

---

## 備註

- 本文件先依現有 `calculator`、`type_catalog.json` 與圖面可辨識資訊整理。
- 若後續需要進一步資料化，可再補 `幾何參數表`、`BOM 結構表`、`PDF note 摘要` 與 `限制條件矩陣`。
