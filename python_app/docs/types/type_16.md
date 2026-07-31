# Type 16 — Dummy Pipe Guide Support with Cover Plate

三來源都有 D-18 Rev.1，A/B/cover plate 尺寸表相同，適用 2–24 in。
但 designation 與現場切長語意不同，必須使用專案來源 profile。

## 來源與編碼

- 中威：`16-{A}-{HH}`，例 `16-2B-05`。右端 overhang 固定 300 mm，
  cover plate 邊長符號為 C；NOTE 3 明定 Hx 現場切割。
- 22A / 20E4588：`16-{A}-{HH}-{CC}`，例 `16-2B-04-03`。
  第四段是可選的 C 修改值；未填時圖面預設 200 mm。cover plate 邊長符號為 D。

HH/CC 均以 100 mm 為單位。D-80 interface 標為 IF REQUIRED / NOT FURNISHED，
因此不列入 Type 16 BOM。

## BOM 與輸入

- Pipe B：管徑與 schedule 依 D-18 表。圖面沒有舊程式採用的
  `1.5A + OD/2 + 100` 下料公式；三張 D-18 的尺寸鏈都直接給出
  名義下料 `Hx = H + C`。中威 C=300 mm，中鼎預設 C=200 mm 或依第四段修改。
  因此 `16-4B-03` 的 Pipe B 為 300+300=600 mm，不得輸出 0 mm。
  NOTE 3 的 cut to suit in field 是最終現場修切要求；
  `dummy_pipe_cut_length_mm` 保留為實測長度覆寫。
- Cover Plate：表列 70–430 square×6t，1 EA。
- `special_main_line=true` 時，NOTE 2 要求接主管的一段同主管材質且與主管在
  shop 一起製作；需另提供 `main_line_material` 與
  `special_main_line_piece_cut_length_mm`，系統才會分成 special/outboard 兩段。
- 非特殊主管也必須明確设 `special_main_line=false`，避免系統暗自猜測。

## 加工圖狀態

三張圖呈現四種主管接合外形，但 designation 不含此資訊。即使提供
`connection_layout`，主管端 cope/fishmouth 的實際輪廓仍未尺寸化；特殊主管
案例的 Ø6 weep hole 也缺中心定位。因此名義 `H+C` 可供 BOM 估重；
special mode 明確後可完成材料拆分，但整體 fabrication 在實測 Hx 與端部輪廓
確認前仍保留 blocker。
