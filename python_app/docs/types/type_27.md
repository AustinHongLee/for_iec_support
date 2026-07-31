# Type 27 - 單立柱頂板支撐

- 圖面：D-30
- 編碼：`27-{M}-{LL}{HH}{M42}[-{L1}{L2}]`
- 正確結構：一支 member、6t 頂板、來源條件式 9t 肋板、M-42
- 必要加工輸入：`member_cut_length_mm`、`top_plate_width_mm`

D-30 的 H 是組立/現場高度，不能用 `H-15` 或 `H-150` 猜 member 切長。頂部是 6t plate，不是第二支 member；`3 SIDES TYP.` 是焊接註記，不是三片假側板。頂板只標長 L，未標寬。缺 override 的 member、頂板，以及只有直徑而無長度的 M-42 fastener 會留在 `excluded_bom_components` 與 blocker，不以 0 mm／0 kg placeholder 混入材料 BOM。

L/H 超界採有限外插分級；主體 D-30 未列但同來源 M-42 標準已定義的底板可高風險暫算。
L1+L2 不等於 L 也列高風險。以上情況都會保留查核用計算，但不等於正式 BOM 或加工放行。
