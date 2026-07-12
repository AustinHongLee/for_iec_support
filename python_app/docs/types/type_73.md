# Type 73 — Spring Strap Support

| 項目 | 內容 |
|------|------|
| 圖號 | D-88 / D-88A |
| 圖名 | DETAIL OF PIPE SUPPORT |
| 分類 | Spring strap support |
| 適用範圍 | 1"~24" |
| 狀態 | 已實作 calculator；多數重量為幾何估算 |

---

## 系統本質

Type 73 是帶 spring coil 的 strap support。圖面分成 slide / guide 兩種孔位邏輯，主體 strap 參照 `M-53`，spring data 在 D-88A。

主要 callout：

- `STRAP SEE M-53`
- `"D" SIZE STUD BOLTS`
- `WASHERS`
- `GUSSET SAME THICKNESS AS BAR FOR 6" LINES & LARGER`
- `SPRING MARK NO. FOR ENG. DATA SEE SHT D-88A`

---

## 編碼格式

```text
73-{line_size}B-{S|G}
```

範例：

```text
73-6B-G
```

| 段位 | 例 | 意義 |
|------|----|------|
| `73` | `73` | Type number |
| line size | `6B` | 管徑 |
| support mode | `G` | `S` = slide support，`G` = guide support |

---

## Calculator Handoff

| 構件 | 來源 | 精度 |
|------|------|------|
| STRAP | Type 73 table + M-53 designation | 幾何估算，`M-53` 尚非 weight-ready |
| SPRING COIL | D-88A spring coil table | wire geometry calculated |
| STUD BOLT | D-88 `D` / `G` | rod geometry estimate |
| WASHER | D-88 callout | placeholder estimate |
| GUSSET | D-88 table `E/H`，6" 以上 | triangular plate estimate |

---

## 殘留風險

- PDF 無文字層，尺寸表由 rendered bitmap AI visual transcription 建立
- M-53 目前只有 dimension lookup，沒有 source unit-weight table
- Baseplate / hole detail A/B/C 目前只以 warnings 註記，未拆成完整製造件
