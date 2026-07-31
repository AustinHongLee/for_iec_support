# Type 113C — 冷保溫懸臂型鋼支撐

來源：DSP-500-006 C-56 Rev.0。

編碼：`113C-{L50|L75|C100}-{C mm}`，例如 `113C-L75-500`。

designation 已直接給 Member M section 與 C 切長，因此可用核定 section kg/m 計算型鋼備料重。系統也依 `P × C <= 40 kg-m` 輸出該 C 對應的最大 P。

系統已展開 N-28 WOOD-1 尺寸與孔位；提供 row override `insulation_thickness_mm` 後，也可解析 N-12 CLIP TYPE 1 的 A/plate thickness。圖面仍未指定 Member M 鋼材牌號、N-28 白橡木密度／WOOD-1 chamfer 與實際載重 P，所以整體尚不可直接發加工圖。
