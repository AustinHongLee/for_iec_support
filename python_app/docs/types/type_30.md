# Type 30 - 焊接既有鋼構的兩件式支撐

- 圖面：D-35
- 編碼：`30-{M}-{LL}{HH}{A/B}[-{L1}{L2}]`
- BOM：H 向 member 一支、L 向 member 一支
- 切長：Fig.A 與 Fig.B 都是 H 向件 `H-15`，L 向件 `L`
- L1/L2：預設各 L/2；第四段總和不等於 L 時列高風險暫算，禁止正式放行

Fig.A 將 L 向件置頂，Fig.B 置底。來源 member/envelope 不同。existing steel 接合面與角鋼/槽鋼截面朝向未編入 designation，因此 BOM 可算但加工圖仍需現場/工程輸入。

L/H 超界依差異分為一般警示或高風險；超過圖示上限 2 倍或超額逾 2000 mm 仍停止。
