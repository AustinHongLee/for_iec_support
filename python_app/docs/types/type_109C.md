# Type 109C — 容器／耳軸冷保溫支撐

來源：DSP-500-006 C-52 Rev.0。

編碼：`109C-{LINE}B-{B mm}-{C mm}`，例如 `109C-6B-300-500`。

目前保存 line size、B、C、預設 45° 安裝角、C180/L130/L75 section 與 stud。系統依 C-52 的 `B=OD/2+insulation+60` 反算保溫厚度，再查 N-12A CLIP TYPE 3 的 A/plate thickness，並展開 N-28 WOOD-2/3/4 尺寸與孔位。角度可用 `orientation_angle_deg` 單筆覆寫。

C-52 未把組立 B/C 唯一轉成各型鋼 finished cuts；N-12A clip 的 host placement、N-28 白橡木密度與 WOOD-2 chamfer、ending plate 及 trunnion scope 仍未完整。因此不以外框尺寸假算加工料。
