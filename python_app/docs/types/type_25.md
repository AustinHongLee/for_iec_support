# Type 25 — 懸臂式角鋼支撐

| 項目 | 內容 |
|------|------|
| 中文名稱 | 懸臂式角鋼支撐 |
| 英文名稱 | Cantilever Angle Support |
| 圖號 | 25 |
| 適用範圍 | L50(L≤1000/H≤500), L65(L≤1000/H≤500), L75(L≤1000/H≤2000) |
| PDF | `25.pdf` |
| 狀態 | ✅ 已分析 |

---

## 系統本質

懸臂角鋼: H段(垂直)+L段(水平), FIG-A基本/FIG-B附U-bolt/FIG-C附Lug Plate(M-34)+K Bolt

FIG-A簡易懸臂; FIG-B附U-bolt/Down Stopper(不含供貨); FIG-C附LUG PLATE TYPE-C(M-34查表)+K Bolt×2。第四段可選L1L2修改尺寸(供建模)。

---

## 編碼格式

```text
25-L50-0505A  第二段=型鋼, 第三段=LL+HH+Fig(A/B/C), 第四段(選填)=L1L2
```

---

## 核心運算邏輯

```text
角鋼×1, Total=H+L; FIG-C追加Lug Plate(M-34查表)+K Bolt×2
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
