# Type 11 — 彈簧可變載支撐

| 來源 | 適用範圍 | H | M-42 | 全牙螺桿 | 編碼 |
|------|----------|---|------|----------|------|
| 中威 E25-24 | 2"~10" | 600 / 1200 | G / J | 1-5/8"×300 | `11-{A}B-{HH}{字母}` |
| 中鼎 22A_5123A | 2"~4" | 600 / 1200 | G / R / T | 1-3/4"×300, A307-B GALV. | `11-{A}B-{HH}{字母}-{D}` |
| 中鼎 20E4588 | 無 D-11 | — | — | — | 停算 |

H 是彈簧組合的離散表列值，並非可外插的連續上限，因此仍須完全命中。
M-42 若只是不在 D-11 主體圖列舉內、但同來源 M-42 標準已有定義，可高風險
暫算；來源標準也沒有則停止。

`D` 是彈簧安裝長度（mm）。22A 將它直接編入料號，例如
`11-2B-06G-88`；中威料號沒有這一段，必須由專案列另行提供。

## 已核對的 BOM 與幾何

- 上 dummy pipe：1.5" SCH.80；straight 為 100 mm，elbow 為 `L+100`。
- 下 supporting pipe：2" SCH.40。D-11 NOTE 4 明定現場切割，圖面沒有
  `H-391` 公式；未提供 `support_pipe_cut_length_mm` 時，長度與重量不計入。
- 全牙螺桿：1 EA；中威 1-5/8"×300，22A 1-3/4"×300。
- Heavy hex nut：2 EA。D-11 未提供成品單重，因此重量不計入。
- Wrought steel washer：OD92 / ID50 / 9t，2 EA；依環形淨面積算重。
- Spring：1 EA，而不是 2 EA。
  - SPR12：12 wire、46 ID、4 active + 2 inactive coils、free L=100、
    k=25 kg/mm、max deflection=22。
  - SPR14：14 wire、46 ID、4 active + 2 inactive coils、free L=115、
    k=42 kg/mm、max deflection=24。

彈簧重量是依六圈線材幾何的毛坯估算；螺桿是實心圓棒毛坯估算。兩者都不是
供應商成品重量。

## 加工圖狀態

每個構件已帶 component ID、來源圖／版次、切長或採購參數。下列資料仍是
明示 blocker：

- straight/elbow 接點不在料號內，必須由 variation axis 選擇。
- 上 dummy pipe 的 cope/fishmouth 輪廓未尺寸化。
- 下 supporting pipe 必須取得現場實測切長。
- 中威必須另給彈簧安裝長度 D。
- 中威 D-11 未標全牙螺桿及重型螺帽材質，不會從主管材質自行推定。

因此 Type 11 可以輸出已知 BOM 與採購／加工參數，但在 blocker 清除前不宣稱
整組可直接出加工圖。
