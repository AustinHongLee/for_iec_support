# Type 115C — 既有面冷保溫支撐

來源：DSP-500-006 C-60/C-61 Rev.0。

編碼：`115C-{CRADLE LENGTH CODE}{CR#}-{LINE}B-{C mm}`，例如 `115C-ACR9-2B-500`。

cradle length code 與 CR number 位於同一段；系統會拆解後依 2 吋以下、3 與 4 吋、6~24 吋分流。C 最大 1000。

CR/pipe 會接入 cold-core lookup，依 branch 解析 `B=F+3` 或 `B=F+13`。2 吋以下接 N-7A 並計 rod-only 重量；3/4 吋接 N-8 的 formed dimensions。

C 是 existing surface 到 pipe centerline 的組立距離；N-7A thread/nuts、N-8 flat development 與 C-21/C-24 型鋼展開未完整，不把 C 當 finished cut。
