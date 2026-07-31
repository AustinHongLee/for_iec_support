# Type 62 — Pipe Hanger Combination

| 項目 | 內容 |
|---|---|
| 中威圖號 | D-75 / D-76 Rev.1 |
| 中威構件圖 | M-3 / M-8 / M-9 / M-10 / M-31 / M-33 Rev.1 |
| 分類 | Rod hanger / pipe hanger combination |
| 狀態 | 中威選型已接表；整組 BOM / 加工圖仍 partial |

## 來源邊界

目前 calculator 只開放中威 `cw_e25_24_hp6`。

中鼎 `ctci_20e4588` 雖也有 D-75/D-76，但不是同一套規則：

- 中威 lower figures 為 `E/G/H/J/K/L/M/N/Q`
- 中鼎 20E4588 lower figures 只見 `P/Q`
- 中威使用英制 fractional rod，例如 `5/8`
- 中鼎範例使用公制 rod，例如 `M16`
- 中鼎另有 Detail Z、LGP-A、reinforcing pad、bolt 與 insulation 規則

因此中鼎 Type 62 仍由 source-profile safety gate 阻擋，不能套用中威的 M-3/M-31/M-33。

## 中威編碼

```text
62-{line_size}B-{rod_size}-{HH}[~{HH2}]{upper_fig}-{lower_fig}[(T)]
```

圖面範例：

```text
62-4B-5/8-05~30D-J(T)
```

`HH` 以 100 mm 為單位；`(T)` 表示使用 turnbuckle。

## FIG 對應表

| FIG | Role | M-No. | Pipe size range | 目前成熟度 |
|---|---|---|---|---|
| A | Upper | M-31 | — | 尺寸與方板扣中心圓孔淨重可算 |
| C/D | Upper | M-28 | — | 既有 lookup |
| E | Lower | M-3 | 1/2"~30" | 21 列尺寸/負載可查；成品重量未給 |
| G | Lower | M-4 | 1/2"~24" | 尺寸可查；來源成品重量未給 |
| H | Lower | M-5 | 3"~42" | partial lookup |
| J | Lower | M-6 | 3/4"~24" | partial lookup |
| K | Lower | M-7 | 6"~36" | partial lookup |
| L | Lower | M-8 | 1-1/2"~10" | 9 列尺寸/分溫負載可查；成品重量未給 |
| M | Lower | M-9 | 4"~16" | 7 列尺寸/分溫負載可查；成品重量未給 |
| N | Lower | M-10 | 10"~24" | 7 列尺寸/OD range/分溫負載可查；成品重量未給 |
| Q | Lower | M-24 + M-33 | 2"~24" | M-33 12 列尺寸/負載可查；淨輪廓/重量未完成 |

M-3 與 M-33 都採原表 exact-row 選型，不做區間內插，且 designation rod 必須等於 component row 指定的 rod。

M-8/M-9/M-10 也只接受原表存在的 line-size row，不會因為落在 D-76
最小/最大範圍內就內插。這三張 clamp 圖的 F/H 是 cross-pin、cross-bolt
或 U-bolt 尺寸，不是 Type 62 designation 的 hanger rod，因此不做
`F/H == rod` 的錯誤限制。

## 重量與加工圖邊界

### M-31 Steel Washer Plate

M-31 是方板、中心圓孔：

```text
net area = C² - πD²/4
weight = net area × T × 7.85e-6 kg/mm³
```

方板與孔位可直接結構化。原圖只寫 carbon steel，未給正式 grade/coating；Type 62 FIG-A 的現場焊接位置也須由 project layout 確認，因此整體仍不是 fabrication-ready。

Rev.1 的 `SWP-3 1/2` 明確列 `D=75 mm`。此值雖不符合相鄰列的單調規律，程式忠實保留，不自行改成 95。

### M-3 Adjustable Clevis

M-3 已保存 21 列 `ADC-*` 的 load、upper/lower steel、A~G 尺寸。它是 formed purchased assembly；原圖沒有：

- finished unit weight
- bend radius / developed strip length
- cross-bolt length/grade 與 nut/washer 完整 scope
- carbon-steel grade/coating

所以 M-3 輸出真實 designation 與尺寸，但重量為 0，不再用 missing-table estimate。

### M-33 Lug Plate Type-B

M-33 已保存 12 列 `LGP-B-*` 的 rod、C/D/E/K/R/T/S 與 maximum load。原圖仍不足以唯一產生 pipe-contact flat contour / bevel，也沒有 finished weight，因此只輸出可查尺寸與加工 blockers，不用外接矩形猜重量。

### M-8 / M-9 / M-10 High-temperature Pipe Clamps

三張 Rev.1 原圖共保存 23 列：

- M-8 Type-E：B/C/D/E/F/G/H，650/750/1000/1050°F load，材料 ASTM A387 Gr.22
- M-9 Type-F：C/D/E/F/H/K，750/950/1000/1050°F load
- M-10 Type-G：used-on O.D. range、C/D/E/F/H/K/M，950/1000/1050/1075°F load

M-9/M-10 原圖指定 chrome-moly clamp body、stainless U-bolt，但未給兩者
grade。三張圖都沒有 finished unit weight，也沒有足以唯一產生 flat
development 的 bend radius/allowance、完整 pin/bolt 長度與 fastener
scope。因此 runtime 輸出真實 designation、材料、尺寸及負載，但 clamp
重量為 0，不能標成 BOM-ready 或 fabrication-ready。

## H 與 M-22

D-75 的 `H` 是整組 hanger assembly dimension，不是 M-22 成品 cut length。舊邏輯曾直接以 H 算 rod 重量，現在已取消。

- 未提供 `rod_cut_length_mm`：M-22 為零重量 reference
- 明確提供 `rod_cut_length_mm`：才用 M-22 rod table 計算該切長重量
- H range 只保存在 assembly metadata，不會自動取最大值當切長

## Turnbuckle Notes

- `(T)` 時加入 M-21
- `H > 2000 mm` 但沒有 `(T)` 時發出 NOTE 3 warning
- Upper FIG-D 沒有 turnbuckle 時依 NOTE 4 加 left-hand M-25，並保留 warning

## 殘留風險

- M-8/M-9/M-10 已可選型，但缺成品重量、完整展開與緊固件釋出資料
- M-4~M-7、M-3、M-33 與 heavy-hex nut 缺可證實成品重量
- M-33 pipe-contact contour / groove 未達可出加工圖程度
- M-22 finished cut 必須由 project takeoff 明示
- 中鼎 20E4588 Type 62 必須另做 P/Q、metric rod 與 Detail Z 邏輯
