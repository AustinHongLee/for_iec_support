# Type 114C — 壁夾式冷保溫支撐

來源：DSP-500-006 C-57/C-58/C-59 Rev.0。

編碼：`114C-{CRADLE LENGTH CODE}-{CR#}-{LINE}B-{C mm}`，例如 `114C-A-CR9-2B-500`。

系統依圖面列值分成 2 吋以下、3 與 4 吋、6~10 吋、12~24 吋四支，保存相應 section、clip reference 與 C 上限；前三支 C 最大 1000，12~24 吋為 1100。

CR/pipe 會接入 cold-core lookup。`B=F+13` 只套用到原圖實際標出 B 的
3/4、6~10、12~24 吋分支；2 吋以下不產生圖上不存在的 B。2 吋以下另接
N-7A SUB1 U-bolt rod 與四顆 finished nuts，3/4 吋 branch 接 N-8 的
R/A/B/T/holes。10 吋以下接 N-13 Clip Type 5 的 10t 雙板與 2-DIA22
孔，12~24 吋接 N-14 Type 6 的 12t 雙板與 4-DIA22 孔。

C 是組立 reach，不直接當型鋼 finished cut；N-8 flat development/bend allowance 仍缺。N-13/N-14 的立面與孔位已解析，但設備半徑 Q/R、theta、B 與 insulation t 才能完成平面 contour，且圖面明定由 vessel vendor furnish/weld，因此 clip 仍是零重量 vendor reference。
