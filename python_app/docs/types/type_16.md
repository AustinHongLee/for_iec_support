# Type 16 — 假管導向支撐（含端板）

| 項目 | 內容 |
|------|------|
| 中文名稱 | 假管導向支撐（含端板） |
| 英文名稱 | Dummy Pipe Guide Support with Cover Plate |
| 圖號 | D-18 |
| 適用範圍 | 2"~24" |
| PDF | `16.pdf` |
| 狀態 | ✅ 已分析 |

---

## 系統本質

以假管與下段支撐管組成的導向支撐，末端設 6t cover plate，可依需求搭配 D-80 介面。

Type 16 與 Type 01 同樣以 dummy pipe 自主管線引出，但支撐頭改為水平支管加端板，形成導向/限位式支撐。圖面列出 2"~24" 對應的 Pipe Size "B" 與 Cover Plate 尺寸 C，Hx 現場裁切。

目前最新版圖面判讀補充如下：
- `DETAIL SEE D-80 (IF REQUIRED)`：not furnished，現階段不納入 Type 16 BOM
- `FOR SPECIAL MAIN LINE SEE NOTE 2`：上下段管已明確拆開，上段暫定不銹鋼、下段暫定碳鋼
- `Hx SHALL BE CUT TO SUIT IN FIELD`：現階段只保留公式基準，暫視為 `H + 300`

---

## 編碼格式

```text
16-{A}B-{H}  例: 16-2B-05
```

---

## 核心運算邏輯

```text
Main Pipe(dummy) = 1.5A(inch)×25.4 + OD/2 + 100 mm, 暫定 SUS304
Support Pipe = H - OD/2 - 100 + 300 mm, 暫定 A53Gr.B
Cover Plate = C × C × 6t
無 M42，無夾具，D-80 介面本型式暫不供料
```

---

## 設計重點

- 此型式不依賴 `M-42` 下部構件，主要由本體鋼材或既有結構承載。
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
