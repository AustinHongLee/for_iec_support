# Type 14 — 結構鋼立柱限位支撐

目前只開放中威 E25-24 的兩頁圖：D-14 為組立／標準尺寸，D-15 為 L/H
上限。22A_5123A 與 20E4588 都沒有 Type 14。

## 編碼與限制

```text
14-{A}B-{LL}{HH}
```

`LL`、`HH` 均以 100 mm 為單位。系統依 D-15 的管徑與 L 區間判定 envelope；
小幅超界為一般警示，較大但仍在護欄內為高風險，超過上限 2 倍或超額逾
2000 mm 仍停止。

## 已核對的 BOM

- Supporting Pipe A：`H - 2F - MEMBER N depth`；保存切長公式、6 mm weld
  與 Ø6 weep hole。
- MEMBER N：L 是兩片 6t Stopper 的外側總長，Channel 切長為 `L-12`；
  2"~8" 為單 Channel，10"/12" 依 Detail a 為兩支
  Channel 背靠背。
- Wing Plate：Q/P/上緣20/右下25/左下10C 六頂點 polygon，4 EA。P 依
  NOTE 3 現場切割。
- Stopper：M×K×6t，2 EA；四角 10C 已扣除淨面積。
- Base Plate：C SQ×F，4-ØE，孔距 D×D。
- Top Plate：B SQ×F。
- EXP.BOLT J：4 EA；D-14 未提供成品單重，重量不計入。

## 加工圖狀態

Pipe、Channel、Stopper、Base/Top Plate 與 anchor 已有 component ID、來源、
版次、孔／焊／切長參數。整體仍為 fabrication-partial：

- Wing Plate 的 P 須以 `wing_plate_P_mm` 提供現場值。
- 10"/12" Detail a 未標兩支 Channel 的組立間距。
- Ø6 weep hole 缺少孔中心離底板尺寸。
- EXP.BOLT 缺成品單重。
