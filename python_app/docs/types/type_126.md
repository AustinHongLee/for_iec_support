# Type 126 — I-Rod 橫樑墊片

來源為中威 D-136；格式 `126-{line}B`，表列範圍 1/2"~12"。

依 line size 保存 I-Rod `L/C/D`。`pipe_schedule` 明選
STD／SCH40／XS／SCH80 後，回傳圖面以充水管重量計算的最大橫樑
間距 M；圖面未列數值的尺寸不外推，改要求專案結構計算。

並排片數與溫度級未寫入 designation，須用 `i_rod_count`（1~3）
及 `i_rod_temperature_class` 明選。專有 thermoplastic 淨斷面、
密度、成品單重及 3M/原廠黏著劑用量未提供，維持零重量採購
reference。
