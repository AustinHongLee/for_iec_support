# Type 51 — D-62／D-62A Pipe Saddle Support

> 2026-07-31 依中威與中鼎 22A_5123A 原圖分來源重製，並加入本專案 1/2" 高風險替代決議。

## 輸入

`51-{LINE SIZE}B`

## 尺寸分支

| 管徑 | 構造 |
|---|---|
| 3/4"～3" | 50×9 flat bar，左右各一 |
| 4"～24" | Angle Member M，左右各一 |
| 26"～42" | Channel Member M，左右各一；切長需 `member_cut_length_mm` |

1/2" 不在 D-62 圖面範圍。依本專案決議，中威來源的 `51-1/2B`
可暫借 3/4" 列（H=25、50×9 flat bar）計算，但固定列為高風險，
正式 BOM、間隙／焊接／承載確認、下料及加工圖皆 blocked。中鼎 22A
未取得相同決議，仍停止計算。中鼎 22A 的 24" Member M 長度為 350 mm。

## 來源差異

- 中威 D-62A 畫出 80° 接觸弧，但引用的 D-91 是 120°；這是原始來源衝突。系統列零重量 D-91 reference，完整 BOM 保持 blocked。
- 中鼎 22A D-62A 使用 120°，且明示 D-91 reinforcing pad `NOT FURNISHED`，不列入 BOM。

## 加工圖狀態

- Flat bar 與一般 angle 分支可直接下料。
- 26"～42" 即使輸入 channel 切長，貼管 cope／定位輪廓仍未完整尺寸化，整組加工圖保持 blocked。
- 未指定牌號的型鋼只標示依專案規範。
