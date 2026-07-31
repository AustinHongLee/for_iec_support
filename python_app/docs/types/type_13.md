# Type 13 — Clamp 式雙板夾持支撐

H 圖示上限採有限外插分級；缺中威以外的來源圖、格式錯誤或過度外插仍停止。

目前只開放中威 E25-24 D-13；22A_5123A 與 20E4588 都沒有 Type 13。

## 編碼與限制

```text
13-{A}B-{HH}{M42}
```

- 表列管徑：2"~16"。
- H 必須 `≤1500 mm`。
- 最高管線溫度：750°F。
- 通常用於 alloy steel / stainless steel line，以 clamp/gasket 避免直接焊主管。
- M-42 A/B/E/G 的 H 從最低鋪面高程起算。

## 已核對的 BOM 與幾何

- M-4 PIPE CLAMP TYPE-A：1 SET。designation、允許荷重、B~H 與 rod size
  均由 M-4 原圖表取得；原圖沒有成品單重，現有重量仍是工程估算。
- M-47 COMPRESSED GASKET：1 PC。原圖 designation 為 `ASB-*`，所有尺寸
  均為 1.5t，材料為 Garlock Blue-Gard Style 3000 or equivalent。
- Supporting Pipe B：依 D-13 表取管徑／schedule；NOTE 4 明定現場切割，
  未提供 `support_pipe_cut_length_mm` 時不計長度與重量。
- Plate P：依表取 P 尺寸，2 EA；保存 C 管中心距及 10" 以上 Detail A。
- Cover Plate：75×75×6t，1 EA。
- 焊道：6 mm；底部依來源別 M-42。

## 加工圖狀態

M-4、M-47、Plate P、Cover Plate 與 M-42 已有 component ID、來源／版次及
具名加工／採購參數。整體仍是 fabrication-partial：

- Supporting Pipe B 需要現場實測切長。
- Ø6 weep hole 沒有孔中心離底板尺寸。
- 結構板只確定為 carbon steel 類別，尚缺實際牌號。
- M-4 與 M-47 的來源都沒有成品單重／材料密度，現有重量是估算值。

舊計算的 `H-100` pipe 公式與 M-47 3t 假設皆與原圖衝突，已移除。
