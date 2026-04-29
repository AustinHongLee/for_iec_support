# Type 20 — 長孔滑動底座支撐

| 項目 | 內容 |
|------|------|
| 中文名稱 | 長孔滑動底座支撐 |
| 英文名稱 | Slotted Clamp Base Support |
| 圖號 | — |
| 適用範圍 | 2"~12" (Z table) |
| PDF | `20.pdf` |
| 狀態 | ✅ 已分析 |

---

## 系統本質

U-bolt 固定點透過長孔(slot hole)產生滑移自由度的夾持式支撐底座

MEMBER M (Angle/Channel) + slot hole + washer，U-bolt NOT FURNISHED。FIG.A/B 兩種布置。H 現場裁切。

---

## 編碼格式

```text
20-{M}-{HH}{Fig}  M=型鋼代碼, HH=H/100mm, Fig=A/B
```

---

## 核心運算邏輯

```text
1 component: Member M (Angle or Channel) with length H. Member options: L50(H≤1500), L65(H≤1500), L75(H≤2000), C100(H≤3000).
```

補充:
- `Z_TABLE` 已保留在 `data/type20_table.py`，供未來 line size 接線時使用。
- 目前 designation 不含 line size，因此現行 BOM 不會輸出特定案例的 `Z` 值。

---

## 設計重點

- 此型式不依賴 `M-42` 下部構件，主要由本體鋼材或既有結構承載。
- 圖面若標示 `U-bolt NOT FURNISHED`，現行 calculator 不會把該夾具列入 BOM。
- `H`、`L` 或 `Hx` 等尺寸多為現場裁切值，文件中的公式代表估算與下料邏輯。
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
