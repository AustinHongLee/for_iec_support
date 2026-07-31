# Type 73 — Spring Strap Support

| 項目 | 內容 |
|---|---|
| 圖面 | D-88 / D-88A / M-53 |
| 編號 | `73-{line_size}B-{S|G}` |
| 範圍 | 1"~24" |
| 狀態 | M-53 strap 淨重可精算；其餘構件維持阻擋 |

M-53 的 `A` 是平板展開總長，因此 strap 使用 `A×F×T`，並扣除圖面 `D+3` 孔，可輸出淨面積、孔資料與重量。

以下舊估算已停用：

- D-88A spring 不再以理想螺旋線長推成品重量。
- `G` 是組立高度，不是 stud finished cut；需 `stud_cut_length_mm`。
- Washer 沒有完整規格／單重。
- 6" 以上 gusset 的 E/H/R 與「same thickness as bar」不足以唯一建立片數及淨輪廓，不再用 `E×H/2` 三角形估重。

所以目前只有 strap 可標為 fabrication-ready；整組仍不是完整 BOM。
