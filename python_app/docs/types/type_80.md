# Type 80 — Pipe Shoe

| 項目 | 內容 |
|------|------|
| 圖號 | D-95 / D-96 |
| 分類 | Pipe shoe / saddle |
| 適用範圍 | 3/4"~42" |
| 狀態 | 已建立保守 calculator |

---

## 系統本質

Type 80 是 D-80 family 的 pipe shoe 本體。

- `3/4"~24"`：依 D-95，以 `Member C` 承托管線。
- `26"~42"`：依 D-96，使用 D-80B 大管 saddle 組合。
- `(P)` 表示 reinforcing pad required。
- HOPS / LOPS 可由 designation 後段覆寫。

---

## 編碼格式

```text
80-2B(P)-A(A)-130-500
80-30B-A(A)-130-500
```

---

## Calculator 規則

### 3/4"~24"

| 管徑 | Member C |
|------|----------|
| 3/4"~8" | CUT FROM H200x100x5.5x8 |
| 10"~14" | CUT FROM H200x200x8x12 |
| 16"~24" | FAB. FROM 12t PLATE |

若有 `(P)`，會加入 `REINFORCING_PAD`。

### 26"~42"

目前依 D-96 / D-80B 建立：

- `SADDLE_SIDE_PLATE` x2
- `SADDLE_FOOT_PLATE` x1
- `SADDLE_ARC_PLATE` x1
- `STIFFENER_PLATE` x4
- `REINFORCING_PAD` x1
- `STOP ANGLE` x2

`NO.7 PLATE 6 THK x6` 在本圖未提供切割尺寸，暫以 warning 標記，不納入 BOM。

---

## 注意事項

- D-95 的 10"~24" `12t STIFF.PL` 圖面有標註，但未給完整下料尺寸，目前以 warning 保留。
- D-96 大管件的 No.6 stop angle 長度暫用 LOPS，需後續以 D-80B 加工圖確認。
- 本型是急件加固版，未標尺寸不偽裝為精算。
