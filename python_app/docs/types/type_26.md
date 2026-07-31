# Type 26 - 三件式懸臂框架

L/H 上限採有限外插分級；20E 的 L 下限、down-stop 選材矩陣空格與未表列 member 仍是硬停止。

- 圖面：D-28 / D-29
- 編碼：`26-{M}-{LL}{HH}{A/B/C}`
- BOM：H 上件 + H 下件 + L 端件
- Fig.C：M-34 Lug Plate Type-C 兩片、每片兩孔，K Bolt 四支

20E4588 的 Fig.B down-stop member 需 `equivalent_pipe_size_in` 才能依 D-29 矩陣選型；其中 pipe<=4 且 H<=1000 的表格空白，程式會停止而不猜。框架四角端切/貼合與 15 mm callout 的製程解讀仍是加工 blocker。
