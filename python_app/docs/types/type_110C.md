# Type 110C — 對向夾片耳軸冷保溫支撐

來源：DSP-500-006 C-53 Rev.0。

編碼：`110C-{LINE}B-{B mm}-{C mm}`，例如 `110C-4B-200-500`。

目前保存 line size、B、C、預設 45° 安裝角、L100/L75 section 與 stud。系統依 C-53 的 B 公式反算保溫厚度，解析 N-12 CLIP TYPE 2 的 A/plate thickness，並展開 N-28 WOOD-1 尺寸與孔位。角度可用 `orientation_angle_deg` 單筆覆寫。

opposed frame 的片數與 finished cuts、clip host placement、N-28 白橡木密度與 WOOD-1 chamfer、ending plate/trunnion scope 尚未由圖面唯一化，故整組仍是 fabrication-partial。
