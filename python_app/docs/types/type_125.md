# Type 125 — I-Rod U 型螺栓夾持支撐

來源為中威 D-135；格式 `125-{line}B`，表列範圍 1/2"~12"。

依 line size 保存 pipe OD、U-bolt `d1/L/P/A`、緊固扭矩及 I-Rod
`I/F/G/H`。designation 未指定並排 I-Rod 片數與
Regular／High Temp／PEEK 溫度級，須分別以 `i_rod_count`（1~3）
及 `i_rod_temperature_class` 明選。

D-135 的圖示足以確認 U-bolt `L` 為冠頂外緣至端部、`P` 為兩腳
中心距，因此桿件依 `πP/2 + 2×(L-P/2-d1/2)` 求中心線展開，
並連同圖示兩只螺帽以碳鋼密度列高風險理論估重。成品材質、螺帽
牌號與供應商重量仍須確認。

I-Rod 的兩孔中心偏距、齒形淨斷面/密度或供應商單重未提供，故
I-Rod 本體仍輸出零重量採購 reference，不以外框猜算。
