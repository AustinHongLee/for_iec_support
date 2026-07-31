# Type 64 — Pipe-to-Pipe Rod Hanger

| 項目 | 內容 |
|---|---|
| 圖面 | D-78 |
| 編號 | `64-{E}-{F}-{HH}{FIG}` |
| 狀態 | D-78 尺寸／figure 表已重抄；成品吊桿長與部分採購重量仍阻擋 |

`E` 是 supported line，`F` 是 supporting line，`H=HH×100 mm` 是上下管中心距，不是 M-22 finished rod cut。Supporting line 必須為 2" 以上，`500≤H≤3000`。

## D-78 rod 表

| E | G |
|---|---|
| 1/2"*、3/4"、1"、1-1/2"、2" | 3/8" |
| 2-1/2"、3"、3-1/2"* | 1/2" |
| 4"、5" | 5/8" |
| 6" | 3/4" |
| 8"、10"、12" | 7/8" |

`*` 只允許 FIG-B/C。圖面沒有 1-1/4" 列。

## 加工圖契約

未提供 `rod_cut_length_mm` 時，M-22 為零重量 reference，禁止把 H 直接當切長。M-25 可依來源表計重；finished hex nut 與 M-4/M-6 clamp 沒有可信來源單重，維持零重量及採購 blocker，所以整筆不能標成完整 BOM。
