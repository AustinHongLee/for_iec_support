# Type 20 — D-22 長孔式 U-bolt 支撐

各來源的 H(MAX) 採有限外插分級；未表列 member、slot 選型資料缺失或過度外插仍停止／保留 blocker。

| 項目 | 內容 |
|------|------|
| 中文名稱 | 長孔式 U-bolt 支撐 |
| 英文名稱 | Slotted U-bolt Support |
| 圖號 | D-22 |
| 來源 | 中威 E25-24、CTCI 22A_5123A、CTCI 20E4588 |
| 編碼 | `20-{M}-{HH}{Fig}` |
| 狀態 | 三來源 BOM 已分流；加工圖仍有定位 blocker |

## 來源差異

三張 D-22 的外形與編碼相近，但 MEMBER M 與 H(MAX) 不能共用。

| 來源 | MEMBER M / H(MAX) |
|------|-------------------|
| 中威 E25-24 | L50/1500、L65/1500、L75/2000、C100/3000 |
| CTCI 22A_5123A | L50/1000、L75/1500、C125/2000 |
| CTCI 20E4588 | L50/1000、L75/1500、C125/2000 |

超出所選來源表列 MEMBER 或 H(MAX) 時會停止計算，不再只顯示警告。

## 編碼與計算

```text
20-{M}-{HH}{Fig}

M    = L50 / L65 / L75 / C100 / C125（依來源）
HH   = H / 100 mm
Fig  = A 或 B
```

MEMBER M 依 H 下料並計算型鋼重量。D-22 的 D-80 接口、standard U-bolt
及 washer/U-bolt assembly 都標示不供應，因此不列入本 Type BOM。

## 加工資料

圖面已能確定：

- 長孔 2 個。
- 長孔半長 30 mm，完整長度為 60 mm。
- 長孔寬度為 `U-bolt rod diameter + 3 mm`。
- Z 依 supported line size：2/3/4/6/8/10/12 吋分別為
  76/104/130/184/235/286/340 mm。
- 角鋼或槽鋼規格、H 切長、Fig A/B 與 6 mm fillet weld。

designation 本身沒有 supported line size 與 U-bolt rod diameter，因此需要
row override：

- `supported_line_size_in`
- `u_bolt_rod_diameter_mm`

缺少這兩項時 MEMBER 的 BOM 仍可成立，但不能輸出完整長孔尺寸。即使兩項都有，
圖中 Slot Detail 的 80/30/30 尺寸基準仍不足以無歧義決定兩個孔中心座標；
在基準線經工程確認前，`fabrication_ready` 維持 false，系統不會自行猜測。
