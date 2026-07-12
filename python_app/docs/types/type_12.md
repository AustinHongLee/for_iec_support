# Type 12 — 焊接式雙板夾持支撐

| 項目 | 內容 |
|------|------|
| 中文名稱 | 焊接式雙板夾持支撐 |
| 英文名稱 | Rigid Welded Dummy Pipe Support with Plate Reinforcement |
| 圖號 | TYPE-12 |
| 適用範圍 | 2~16 |
| PDF | `12.pdf` |
| 狀態 | ✅ 已分析 |

---

## 系統本質

Supporting pipe + Plate P + Cover plate 組焊剛性支撐頭，板材材料可加尾碼 (A)合金/(S)不鏽鋼

以 supporting pipe B 承接主管，再透過 Plate P + 6t Cover Plate 組焊固定的剛性支撐。Designation 依板材材料附加 (A)/(S) 符號。M42 底座類型 A/B/E/G 時 H 從地坪最低點起算。

---

## 編碼格式

```text
12-{A}-{H}{M42}  或  12-{A}-{H}{M42}(A)/(S)  例: 12-6B-05B, 12-6B-05B(A)
```

---

## 核心運算邏輯

```text
查表取 pipe_size_b/pipe_sch/plate 尺寸 → Support Pipe(H-100, A53Gr.B) + Plate P(材料依尾碼) + Cover Plate(75×75×6t) + M42
```

---

## 設計重點

- 與 `M-42` 下部構件有關，最終組成會受到末段字母或允許型別限制。

---

## 與相近 Type 的關係

| 類別 | 型式 | 說明 |
|------|------|------|
| Dummy Pipe 家族 | 01 / 07 / 09 / 10 / 11 / 12 / 13 / 16 | 共通點是從主管引出支撐腿，再決定底部承載或限制方式。 |

---

## 備註

- 本文件先依現有 `calculator`、`type_catalog.json` 與圖面可辨識資訊整理。
- 若後續需要進一步資料化，可再補 `幾何參數表`、`BOM 結構表`、`PDF note 摘要` 與 `限制條件矩陣`。
