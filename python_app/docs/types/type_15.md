# Type 15 — 結構鋼立柱限位支撐(落於鋼構)

| 項目 | 內容 |
|------|------|
| 中文名稱 | 結構鋼立柱限位支撐(落於鋼構) |
| 英文名稱 | Heavy Duty Structural Sliding Support on Existing Steel |
| 圖號 | TYPE-15 |
| 適用範圍 | 2~12 |
| PDF | `15.pdf` |
| 狀態 | ✅ 已分析 |

---

## 系統本質

TYPE-14 的鋼構版本，直接落在 existing steel 上，無 anchor bolt

與 TYPE-14 結構相同但底部直接落在既有鋼構上。無 foundation、無 anchor bolt。Base Plate = D×D×F(無鑽孔)。其餘構件與 TYPE-14 相同。

---

## 編碼格式

```text
15-{A}-{LL}{HH}  例: 15-2B-1005 (L=1000, H=500)
```

---

## 核心運算邏輯

```text
查表取各部件尺寸 → Pipe(H-2F-CH) + Channel(L) + Wing PL×4 + Stopper PL×2 + Base PL(D×D) + Top PL
```

補充判讀：
- `Plate_WING` 固定 4 片
- `Plate_STOPPER` 固定 2 片
- 10"、12" 依圖上 `MEMBER "N" ... SEE DETAIL "a"`，目前視為 2 支橫向 Channel
- 非四方板件已在 BOM remark 留幾何提示，方便後續自動化加工圖

---

## 設計重點

- 此型式不依賴 `M-42` 下部構件，主要由本體鋼材或既有結構承載。
- 此型式重點在滑動或限位功能，應優先比對圖面上的止擋、滑板與間隙設定。

---

## 與相近 Type 的關係

| 類別 | 型式 | 說明 |
|------|------|------|
| 相近型式 | 依 `type_catalog.json` 與圖面家族比對 | 後續可再補上更精細的 family / ontology 關聯。 |

---

## 備註

- 本文件先依現有 `calculator`、`type_catalog.json` 與圖面可辨識資訊整理。
- 若後續需要進一步資料化，可再補 `幾何參數表`、`BOM 結構表`、`PDF note 摘要` 與 `限制條件矩陣`。
