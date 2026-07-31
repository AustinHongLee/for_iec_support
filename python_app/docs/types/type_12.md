# Type 12 — 焊接式雙板夾持支撐

H 圖示上限採有限外插分級；缺中威以外的來源圖、格式錯誤或過度外插仍停止。

目前只開放中威 E25-24 D-12；22A_5123A 與 20E4588 都沒有 Type 12，
選到這兩個來源時會停算。

## 編碼

```text
12-{A}B-{HH}{M42}
12-{A}B-{HH}{M42}(A)
12-{A}B-{HH}{M42}(S)
```

NOTE 4 的板材類別為：

- 無尾碼：CARBON STEEL
- `(A)`：ALLOY STEEL
- `(S)`：STAINLESS STEEL

圖面只指定類別，沒有牌號。系統不再把 stainless 自動當成 SUS304，也不把
carbon steel 自動當成 A36；最終 BOM 應以 `plate_material` 列覆寫確認牌號。

## 已核對的 BOM 與幾何

- 管徑表：2"~16"，H 必須 `≤1500 mm`。
- Supporting Pipe B：依表取管徑／schedule；D-12 NOTE 3 明定現場切割，
  未提供 `support_pipe_cut_length_mm` 時不計長度與重量。
- Plate P：依表取 P 尺寸，數量 2 EA，兩片夾板的管中心距為 C。
- Cover Plate：75×75×6t，1 EA。
- 組焊：6 mm fillet weld。
- 底部：依 M-42 字母建立來源別 lower component；A/B/E/G 的 H 從最低鋪面
  高程起算。

## 加工圖狀態

Plate P、Cover Plate 與 M-42 已有 component ID、來源／版次、外形、數量及
焊道參數。整體仍是 fabrication-partial：

- Supporting Pipe B 的實際切長須由現場提供。
- 圖面標了 Ø6 weep hole，但沒有孔中心離底板尺寸。
- 板材只有 carbon/alloy/stainless 類別，尚缺實際牌號。

舊計算的 `H-100` supporting-pipe 公式沒有 D-12 尺寸依據，已移除。
