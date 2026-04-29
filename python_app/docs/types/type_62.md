# Type 62 — Pipe Hanger Combination

| 項目 | 內容 |
|------|------|
| 圖號 | D-75 / D-76 |
| 圖名 | DETAIL OF PIPE SUPPORT |
| 分類 | Rod hanger / pipe hanger combination |
| 狀態 | 已實作 calculator，部分 component 仍為估算 |

---

## 系統本質

Type 62 不是單一零件，而是管線吊架的「組合選型圖」。

它由三段組成：

- Upper part：`FIG-A / FIG-C / FIG-D`
- Common rod hardware：`M-22` machine threaded rod，必要時加 `M-21` turnbuckle
- Lower part：`FIG-E / G / H / J / K / L / M / N / Q`

圖面 page 2 的表格將每個 FIG 對應到 M-series component，例如 `FIG-J -> M-6`、`FIG-Q -> M-24`。

---

## 編碼格式

```text
62-{line_size}B-{rod_size}-{HH}[~{HH2}]{upper_fig}-{lower_fig}[(T)]
```

圖面範例：

```text
62-4B-5/8-05~30D-J(T)
```

拆解如下：

| 段位 | 例 | 意義 |
|------|----|------|
| `62` | `62` | Type number |
| line size | `4B` | 管徑 |
| rod size | `5/8` | rod diameter |
| H | `05~30` | Dimension H，以 100mm 為單位；本例為 500~3000mm |
| upper fig | `D` | Upper part figure |
| lower fig | `J` | Lower part figure |
| `(T)` | `(T)` | With turnbuckle |

Calculator 也接受單一 H，例如：

```text
62-4B-5/8-05C-J
```

---

## FIG 對應表

| FIG | Role | M-No. | Grinnell Fig | Pipe size range | Max temp | Max insulation |
|-----|------|-------|---------------|-----------------|----------|----------------|
| A | Upper | M-31 | 60 | — | — | — |
| C | Upper | M-28 | 66 | — | 750°F | — |
| D | Upper | M-28 | 66 | — | 750°F | — |
| E | Lower | M-3 | 260 | 1/2"~30" | 650°F | — |
| G | Lower | M-4 | 212 | 1/2"~24" | 750°F | — |
| H | Lower | M-5 | 216 | 3"~42" | 750°F | — |
| J | Lower | M-6 | 295 | 3/4"~24" | 750°F | 4" |
| K | Lower | M-7 | 295H | 6"~36" | 750°F | 4" |
| L | Lower | M-8 | 295A | 1-1/2"~10" | 1050°F | 4" |
| M | Lower | M-9 | 224 | 4"~16" | 1050°F | 4" |
| N | Lower | M-10 | 246 | 10"~24" | 1075°F | 6" |
| Q | Lower | M-24 | 299 | 2"~24" | 750°F | — |

圖面 remarks：

- `FIG-H` load capacity greater than `FIG-G`
- `FIG-K` load capacity greater than `FIG-J`
- `FIG-M` load capacity greater than `FIG-L`
- `FIG-N` load capacity greater than `FIG-M`
- `FIG-Q` uses Lug Plate Type-B (`M-33`)

---

## Calculator Handoff

目前 calculator 採保守 BOM 組裝：

| 構件 | 來源 | 精度 |
|------|------|------|
| Machine threaded rod | `M-22` | table lookup，長度用 H 或 H range 的最大值 |
| Turnbuckle | `M-21` | `(T)` 時加入 |
| Upper `FIG-C/D` | `M-28` | table lookup |
| Lower `FIG-G/H/J/K` | `M-4/M-5/M-6/M-7` | table lookup |
| Lower `FIG-Q` clevis | `M-24` | table lookup |
| Weldless eye nut | `M-25` | lower clamp connector；table lookup |
| Heavy hex nut | drawing callout | 估算，待 nut table |
| `M-3/M-8/M-9/M-10/M-31/M-33` | missing component table | 明確 warning 為估算 |

FIG-E 補充判讀：

- D-75 page 1 的 FIG-E 只顯示 M-3 Adjustable Clevis 本體接 rod
- 圖面沒有像 FIG-G/H/J/K/L/M/N 那樣標出 `WELDLESS EYE NUT` 或 `HEAVY HEX. NUT`
- 因此 calculator 對 FIG-E 不另加 M-25 或 heavy hex nut，只輸出 M-3 估算 placeholder 與 warning

---

## Turnbuckle Notes

圖面 note 3：

- `H > 2000mm` 時需使用 turnbuckle
- Upper `FIG-D` 在 hanger combination 中需使用 turnbuckle

圖面 note 4：

- 若 Upper `FIG-D` 選用但沒有 turnbuckle，需使用 left-hand threaded weldless eye nut

Calculator 會：

- `(T)` 出現時加入 `M-21`
- `H > 2000mm` 但未標 `(T)` 時發 warning
- Upper `FIG-D` 未標 `(T)` 時加入 left-hand `M-25`，並發 warning

---

## 殘留風險

- `M-3/M-8/M-9/M-10/M-31/M-33` 尚未 component table 化，相關重量不是精算值
- 若 designation 使用 `05~30` 這種 H range，calculator 以最大 H 作 rod takeoff，屬保守估算
- Type 62 PDF 為 vector drawing，資料由 rendered bitmap AI visual transcription 建表，建議 Claude spot-check page 2 表格
