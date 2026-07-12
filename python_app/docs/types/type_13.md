# Type 13 — Clamp式雙板夾持支撐

| 項目 | 內容 |
|------|------|
| 中文名稱 | Clamp式雙板夾持支撐 |
| 英文名稱 | Clamped Dummy Pipe Support with Plate Reinforcement |
| 圖號 | TYPE-13 |
| 適用範圍 | 2~16 |
| PDF | `13.pdf` |
| 狀態 | ✅ 已分析 |

---

## 系統本質

TYPE-12 的非焊接版本，用 Pipe Clamp TYPE-A(M-4) + Non-Asbestos Sheet(M-47) 代替焊接

通常用於合金鋼/不鏽鋼管線（不允許焊接主管）。Pipe Clamp 夾持主管，中間墊非石棉墨片隔熱防磨，支撐管透過 Plate P + Cover Plate 組焊固定。MAX TEMP 750°F。

---

## 編碼格式

```text
13-{A}-{H}{M42}  例: 13-6B-05B
```

---

## 核心運算邏輯

```text
查表取 pipe_size_b/pipe_sch/plate 尺寸 → Pipe Clamp(M-4) + Non-Asbestos Sheet(M-47) + Support Pipe(H-100) + Plate P + Cover Plate + M42
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
