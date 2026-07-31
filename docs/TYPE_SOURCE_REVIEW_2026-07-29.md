# Type 來源逐圖初審（2026-07-29）

> 本文件是人工視覺初審紀錄，不取代原圖、程式與 golden tests。機器盤點詳見
> `docs/type_source_audit.json`；contact sheets 由
> `python_app/tools/render_type_source_contact_sheets.py` 產生。

## 審查原則

- 同一 Type 在不同來源有圖時，每個來源至少看一次。
- 只有構造、尺寸表、適用管徑、designation 語意及引用圖均確認一致，才可共用。
- 頁數相同、名稱相同或外觀相似，均不足以自動判定一致。
- 本輪共檢視 46 個至少存在於兩個來源的 Type；目前沒有僅憑機器結果自動跳過者。

## 第一輪結果

| Type | 初審 | 主要觀察／下一步 |
|---|---|---|
| 01 | 差異 | 中威至 50 吋；兩套中鼎至 24 吋，24 吋支撐管與 L 值不同；H 上限也不同。 |
| 08 | 待表格確認 | 主構造近似；舊中鼎增加等分與 designation 說明，需逐表核對。 |
| 09 | 差異 | machine bolt／M42 與下部構件條件不同。 |
| 10 | 明顯差異 | 中威與舊中鼎的構造、管徑範圍、底部做法不同；22A 未供圖。 |
| 11 | 差異 | 中威與 22A 的 spring 表與 designation 欄位需分開；舊中鼎未供圖。 |
| 15 | 明顯差異 | 中威可用構件與尺寸表範圍較大；兩套中鼎較接近。 |
| 16 | 差異 | 主構造近似，但修改尺寸欄位、H 限制與表格版本不同。 |
| 20 | 差異 | 中威增加 C100 等 member 選項與較大適用範圍。 |
| 21 | 差異 | 中威增加 C125 等 member 選項；兩套中鼎較接近。 |
| 22 | 差異 | 中威增加 C100/C125 member；兩套中鼎較接近。 |
| 23 | 明顯差異 | 中威擴充 Channel/H-beam member 清單；中鼎僅 L50/L75。 |
| 25 | 差異 | member、螺栓與等效管徑表不同。 |
| 26 | 差異 | member 清單與尺寸表不同；三套皆須保留來源。 |
| 27 | 部分可共用 | 中威與 22A 表面上接近；舊中鼎增加 member 與接合選項，仍需 golden 核對。 |
| 28 | 差異 | 22A member 清單較少；中威與舊中鼎較接近。 |
| 30 | 差異 | 三套 member 的 L/H 上限不同。 |
| 31 | 差異 | 22A 缺少中威／舊中鼎的 H250 member。 |
| 32 | 差異 | 22A 缺少中威／舊中鼎的 H250 member。 |
| 33 | 差異 | 22A 缺少中威／舊中鼎的 H250 member。 |
| 34 | 差異 | 中威含 H250；22A 未列；舊中鼎未供圖。 |
| 35 | 差異 | 中威增加 H100/H150；兩套中鼎較接近。 |
| 37 | 高度相似，待確認 | 三套構造、member 表與 A/B 角度規則看起來一致；需逐值確認後才可跳過。 |
| 39 | 高度相似，待確認 | 主尺寸表接近；lug plate 引用與細節圖號不同，需逐值確認。 |
| 43 | 待表格確認 | 中威與舊中鼎均兩頁且構造相近；22A 未供圖。 |
| 47 | 高度相似，待確認 | 中威與舊中鼎主構造及尺寸表接近；22A 未供圖。 |
| 51 | 高度相似，待確認 | 中威與 22A 兩頁構造／表格接近；舊中鼎未供圖。 |
| 52 | 明顯差異 | 中威分 ≤8/10–24；22A 分 ≤4/6–24；舊中鼎分 ≤4、6/8、10–24，且 Detail A 構件不同。 |
| 53 | 明顯差異 | 頁數為 2/3/2，構造分支與大管細節不同。 |
| 54 | 明顯差異 | 中威分 ≤8/10–24；22A 分 ≤4/6–24。 |
| 55 | 明顯差異 | 中威兩頁、22A 兩頁，但分段與 insulation／clamp 細節不同。 |
| 57 | 明顯差異 | 中威／22A 為英制 U-bolt 表；舊中鼎為 M 制、僅至 6 吋並含 shim plate。 |
| 59 | 明顯差異 | 材料表、支撐板尺寸及 insulation/bare pipe 細節不同。 |
| 61 | 待逐表確認 | 三套皆三頁且構造相近，但 clamp／hanger 大表必須逐列核對。 |
| 62 | 明顯差異 | 中威與舊中鼎的下部構件、lug plate 與第二頁表格不同；22A 未供圖。 |
| 66 | 明顯差異 | 22A 的大分支自 6 吋開始；中威／舊中鼎自 10 吋開始；舊中鼎 E 全表 15 mm，22A 另有 D-80C。 |
| 67 | 明顯差異 | 中威／22A 的小大管分段與 D-81A 尺寸表不同；舊中鼎未供圖。 |
| 76 | 高度相似，待確認 | 中威／22A 均為 26–42 吋、120°、400 長與 12t 最小板；需確認全部 note 後才跳過。 |
| 80 | 明顯差異 | 三套 insulation、fire-proof、構件表與頁面內容不同。 |
| 83 | 明顯差異 | 頁數 2/2/3，舊中鼎另有大管頁，細節不同。 |
| 85 | 差異 | 三套頁面與大管做法相近但不完全一致，需依 D-80 profile 分流。 |
| 86 | 明顯差異 | 中威兩頁、22A 一頁；分段與 clamp/gasket 細節不同。 |
| 87 | 明顯差異 | 尺寸表 E 值與圖號不同。 |
| 101 | 差異 | 舊中鼎增加 support location／priority position 細節；22A 未供圖。 |
| 102 | 差異 | 中威與 22A 的 E plate 厚度切換管徑不同；舊中鼎未供圖。 |
| 103 | 明顯差異 | 中威／22A 為尺寸與 expansion-bolt 表；舊中鼎為荷重、板厚與 bolt 表，語意不同。 |
| 105 | 差異 | 中威與舊中鼎構造相近，但 member 組合表不同；22A 未供圖。 |

## 已落地的第一個差異

- 專案來源 profile 已建立：
  - `cw_e25_24_hp6`
  - `ctci_22a_5123a`
  - `ctci_20e4588`
  - `eko`
- Type 52/66 共用的 D-80 sizing 已開始依來源分流。
- 6 吋案例：
  - 中威：`H200×100×5.5`，不進大管 gusset 分支。
  - 22A：`H200×200×8`，進入 6–24 吋分支。
  - 舊中鼎：`H200×100×5.5`，且 E=15 mm。
- Type 52 D-63 已拆成三套 recipe：
  - 中威：L40×40×5；10–24 吋另見 PL12t，但圖面未給完整平面尺寸，僅警示。
  - 22A：L40×40×5；6–24 吋另見 PL6t，但圖面未給完整平面尺寸，僅警示。
  - 舊中鼎：`<=4"` 為 9t 板組、`6"/8"` 為 L40＋9t 小板、`10"–24"` 為 L50＋6t/9t 小板。
- 未逐圖開放的中鼎 Type 會停算，不會回退套用中威 handler。

## 第二輪落地：Type 53/54/55/67/85

- Type 53 D-64 已依三套圖拆分至 24 吋：
  - 中威：至 24 吋為雙側 L40×40×5。
  - 22A：`<=4"` 為 L40；`6"~24"` 另加 6t×35×35 三角板。
  - 20E4588：`<=4"` 為 9t×150×40 板；`6"/8"` 為 L40＋6t×35×35；`10"~24"` 為 L50＋6t×44×44。
  - 26 吋以上雖有型鋼規格，但 supplied sheet 未提供可信下料長度，因此停算。
- Type 67 D-81 已建立中威與 22A 的 `<=14"` 核定路徑：M-4 PIPE CLAMP、M-47 NON-ASBESTOS GASKET、來源別 H 型鋼與預設 LOPS。16~24 吋 fabricated 12t 與 26 吋以上 D-81A 尚未開放；20E4588 未供 Type 67。
- Type 54 已改為正確的「D-81 core + D-65 retainer」，不再借用 D-80：
  - 中威 `<=8"` 為 L40；`10"~14"` 為 L40＋12t×40×150 雙側底板。
  - 22A `<=4"` 為 L40；`6"~14"` 為 L40＋6t×40×150 雙側底板。
- Type 55 已改為「D-81 core + D-66 guide」：
  - 中威核定範圍為雙側 L40。
  - 22A 的 `6"` 以上另見 6t×35×35 Detail a 異形小件；因淨面積與數量未充分標示，僅警示、不列重量。
- Type 85 三套 D-105/D-106 均已檢視。小管分界、最大管徑及 insulation class 不同，而且另含保溫鞍座專屬構件；現有 Type 52 fallback 已移除，專屬 recipe 完成前明確停算。

## 尚未宣告完成

- Type 52 的可讀尺寸已建 recipe；中威 PL12t 與 22A PL6t 仍缺完整幾何，維持 partial。
- Type 53 的 26 吋以上、Type 54/55/67 的 16 吋以上，以及 Type 80/83/85/86 仍需逐張完成 component recipe。
- 「高度相似」項目尚未等於「可跳過」；必須補逐值確認與 golden tests。

## 第三輪落地：Type 66 加工圖契約

- 20E4588 原有 37 個數字 Type PDF 已來源保留後攤成 51 份單頁，命名改為
  `TYPE-XX_D-XX.pdf`；原檔收在 `中鼎/長春_Type/_原始合併檔/`。
- Type 66 已新增來源別加工資料表，保存 D-80/D-80A/D-80B，以及 22A D-80C：
  - 中威 D-80B 26–50 吋尺寸表；
  - 22A D-80B 26–42 吋與 D-80C 44–78 吋尺寸表；
  - 20E4588 D-80B 26/28 吋尺寸表、E=15 與跨管焊道 V-notch 規則。
- 現階段只有能追溯到構件、切長、120° 弧面／展開、孔與焊接規則的小管分支開放：
  - 中威與 20E4588：≤8 吋；
  - 22A：≤5 吋（6 吋已進入四片補強分支）。
- 10–24 吋與 D-80B/D-80C 雖已保存可讀組立尺寸，但逐件輪廓／展開與焊接定位未齊，
  因此停算，不再用 `HOPS×A` 或 gross rectangle 當成可加工幾何。
- 結果與 Inventor 參數現在保留 source profile、原圖、版次、branch、component ID、
  fabrication readiness 與 blockers；未核定分支不輸出假的 C-type／製作高度。

## 第四輪落地：Type 01 D-1 / M-42

- 三套 D-1 已逐頁核對，不能共用單一表：
  - 中威至 50 吋、H<1500；
  - 22A 至 24 吋、無 22 吋 row、H≤1200；
  - 20E4588 至 24 吋、無 22 吋 row、H<1500；
  - 中鼎兩套的 24 吋皆為 12" STD.WT、L=647；中威為 14" STD.WT、L=677。
- 三張圖都把 Supporting Pipe B 定義為單一連續假管。舊程式拆成上段同主管、
  下段固定 A53Gr.B 是歷史估算；現在改為一支同主管材質，elbow 切長 H+L、
  tee 切長 H+M。
- M-42/M-42A/M-43 也依來源分流：
  - 中威保留 A~Y 圖示範圍；
  - 22A/20E4588 僅開放 B/C/E/F/G/H/K/L/R/S/T；
  - 22A 使用英制 expansion bolt，20E4588 使用公制 machine bolt + hex nut。
- Pipe、plate、angle、fastener 已帶 component ID、來源／版次、切長、孔距與規格。
  Supporting Pipe 頂端 cope/fishmouth 尚未參數化，restrain element 亦僅有示意；
  因此 BOM 可算但整體 `fabrication_ready=false`，不輸出平口假管加工圖。

## 第五輪落地：Type 08 D-8

- 三套 D-8 已逐張核對，原本的單一 `2"~4" / L≤1000 / H≤1500 / G/J`
  規則只適用中威：
  - 中威：2"/3"/4"，L≤1000、H≤1500、M-42 G/J；
  - 22A：表列 3"/4"，L 上限 500/800、H 最高 2500、M-42 G/R/T；
  - 20E4588：同樣表列 3"/4" 與 G/R/T，但 Rev.1B 增加 L1/L2 配置碼。
- 中威與 22A 的 L 尺寸界線落在兩端 6t STOPPER 外緣，MEMBER N 正確切長為
  `L-12`；舊程式直接採 L 會多算 12 mm。STOPPER 已按 K×M、4-C10 的淨面積
  算重，不再以毛矩形估重。
- 20E4588 Rev.1B 的主視圖沒有兩端 STOPPER，MEMBER N 切長為 L；系統會解析
  第四段 L1/L2 並要求 `L1+L2=L`。由於尺寸表仍殘留 K/M 欄，STOPPER 是否刪除
  存在來源內部歧義，因此不自行加入構件，並把 BOM 標成需工程師核定。
- 22A/20E4588 的 3" 高支架若 `1500<H≤2500`，NOTE 4 另要求 supported line
  不大於 2" single line；編碼沒有此欄，未提供 override 時保留 blocker。
- Pipe/Channel/Top Plate/Stopper/M-42 已帶 component ID、切長、位置、輪廓與焊接
  參數。三張圖均未給 Ø6 weep hole 孔中心離底板尺寸，所以整組仍為
  `fabrication_ready=false`。

## 第六輪落地：Type 09 D-9 / M-43

- 三套 D-9 的調整五金不能共用：
  - 中威：H≤1500、M-42 B/H、1-5/8"×150L full-thread bolt；
  - 22A：300≤H≤1800、M-42 B/C/H/R、1-3/4"×150L；
  - 20E4588：H≤1500、M-42 B/C/H、M42×150L。
- 三張圖的 supporting pipe 都是 2" SCH40。垂直鏈包含主管側特殊材尾段 100 mm
  與 resting surface 到 pipe bottom 的調整空間 100 mm，因此下段正確切長為
  `H-200`；舊程式的 `H-100` 會多料 100 mm。
- 上段特殊材 dummy leg 依 connection 分流：straight=100、elbow=L+100。
  designation 沒有 connection 欄，未明確選擇時雖沿用舊 elbow 預設，但
  `bom_ready=false`。
- M-43 的 Type 09 plate-a omission 已實作：
  - 中威 B/H 刪 plate a；
  - 22A B/C/H 刪 plate a，R 保留；
  - 20E4588 B/H 刪 plate a，C 保留 150×150×9 plate a 並依 D-9 detail 焊接。
- 上下管、adjusting bolt/nut 與剩餘 M-42 構件已帶 component ID 與加工參數。
  上端與 straight/elbow 的 cope/fishmouth 未尺寸化，仍為 fabrication blocker。

## 第七輪落地：Type 10 D-10 / D-10A / M-1

- Type 10 不是單純來源表不同，而是兩種 construction：
  - 中威 D-10/D-10A：雙 Plate F、4 adjustable bolts、16 nuts；
  - 20E4588 D-10：單柱、12t annular BASE WASHER、M-1 special base plate；
  - 22A 未供 Type 10，維持停算。
- 中威 D-10A 已補齊 1.5~50 吋表，包含舊 config 缺少的
  22/24/26/30/34/38/40/42/46/48/50 吋 rows。Plate F 的 side/t、4孔徑、
  W×W pitch、35 edge offset 與數量已結構化。
- 20E4588 只開放圖面表列 6~16 吋：
  - upper pipe=100 或 L+100；
  - lower pipe=H-200；
  - BASE WASHER=OD F / ID95 / 12t；
  - M-1 的 3" threaded pipe、3000# coupling、Ø150×12 plate 與 Ø10 half-hole
    已保存為加工／採購參數。
- M-43 對 20E4588 Type 10 的 B/H plate-a deletion 已套用；C 保留 plate a。
- 中威 upper/lower 仍是 200/L+200 與 H-300。兩來源都嚴格執行 H<1500，
  不再超限照算。
- 上端 cope/fishmouth、CW Ø6 weep-hole 定位與 M-1 coupling 成品重量仍是明示
  blocker；未選 connection 的 row 為 `bom_ready=false`。

## 第八輪落地：Type 11 D-11

- 中威與 22A 的 D-11 外形相似，但不能共用單一 profile：
  - 中威表列 2~10 吋，H=600/1200，M-42 僅 G/J，全牙螺桿為
    1-5/8"×300；
  - 22A 僅表列 2~4 吋，H=600/1200，M-42 僅 G/R/T，全牙螺桿為
    1-3/4"×300 A307-B GALV.；
  - 20E4588 未供 Type 11，維持停算。
- 22A 的第四段料號是彈簧安裝長度 D，例如 `11-2B-06G-88`；系統會依
  spring free length / max recommended deflection 檢查 D。中威料號不含 D，
  出組立圖前須由 row override 提供。
- D-11 NOTE 4 將下方 2" SCH40 supporting pipe 定義為 field cut to suit。
  舊程式的 `H-391` 沒有圖面尺寸鏈依據，已移除；缺現場切長時保留零長度
  component 與 blocker，不計重量。
- 舊 BOM 把剖面線誤讀成兩支 spring；圖面實際為 1 支 spring 夾在 2 片
  OD92/ID50×9t washer 之間。washer 已按環形淨面積算重，SPR12/SPR14 則
  以 4 active + 2 inactive coils 的線材毛坯估重。
- 全牙螺桿/螺帽沒有來源成品單重；螺桿僅列 nominal blank estimate，
  螺帽重量保持 0。中威圖也沒有標兩者材質，因此不從主管材質猜測。
- Pipe、washer、spring、threaded rod、nut 與 M-42 已帶 component ID、來源、
  版次與具名加工／採購參數。上端 cope、現場下管切長，以及中威 D/五金材質
  未完成前，整體仍為 fabrication-partial。

## 第九輪落地：Type 12 D-12

- 供圖中只有中威 E25-24 D-12；22A_5123A 與 20E4588 都沒有 Type 12，
  因此兩套中鼎維持來源安全閘門停算。
- D-12 NOTE 3 明寫 supporting pipe dimension shall be cut to suit in field；
  圖上沒有舊程式採用的 `H-100` 尺寸鏈。現在只接受
  `support_pipe_cut_length_mm` 現場值，缺值時 pipe 長度／重量為 0 並保留
  blocker。
- Plate P 是兩片夾板，舊 BOM 只列一片。現在依表列 P 尺寸列 2 EA，並保存
  C 管中心距、10 吋以上 Detail A、6 mm weld；Cover Plate 為 75×75×6t、
  1 EA。
- NOTE 4 的空白/(A)/(S) 只代表 CARBON/ALLOY/STAINLESS STEEL 類別，
  並沒有給實際牌號。系統不再把它們暗自指定為 A36 或 SUS304；最終 BOM
  必須另給 plate material grade。
- Supporting Pipe、兩片 Plate P、Cover Plate 與 M-42 都已帶 component ID、
  來源／版次及加工參數。Ø6 weep hole 未標孔中心離底板尺寸，故整體仍為
  fabrication-partial。

## 第十輪落地：Type 13 D-13 / M-4 / M-47

- 供圖中只有中威 E25-24 D-13；22A_5123A 與 20E4588 都沒有 Type 13，
  因此兩套中鼎維持停算。
- D-13 與 D-12 共用 B/C/P 尺寸概念，但主管接點改為 M-4 PIPE CLAMP
  TYPE-A + M-47 COMPRESSED GASKET，最高使用溫度 750°F。
- M-4 表的 PCL-A designation、650/750°F load、B~H 與 rod size 已接入
  component parameters；原圖沒有成品單重，所以 clamp 重量仍明示為估算。
- M-47 原圖重新核對後，NOTE 1 明定所有尺寸均為 1.5t，designation 為
  `ASB-*`，材料為 Garlock Blue-Gard Style 3000 or equivalent。舊共用表把
  24 吋以下設成 3t，會將相關 gasket 重量算成兩倍，已修正；Type 54 等共用
  M-47 的既有輸出也同步更新 golden expectations。
- D-13 NOTE 4 同樣要求 supporting pipe 現場切割，舊 `H-100` 已移除；
  Plate P 也由單片修正為雙片，Cover Plate 保持 75×75×6t。
- M-4、M-47、Supporting Pipe、Plate P、Cover Plate 與 M-42 已帶 component
  ID、來源／版次和加工／採購參數。現場切長、結構板牌號與 Ø6 weep-hole
  中心定位未完成前，整體仍是 fabrication-partial。

## 第十一輪落地：Type 14 D-14 / D-15

- Type 14 是中威同一型式的兩頁圖：D-14 為組立／標準尺寸，D-15 為 L/H
  上限；兩套中鼎都沒有 Type 14，維持停算。
- D-15 L/H envelope 已改為硬限制；L 超過表列最大值或 H 超限不再照算。
- Supporting Pipe 切長 `H-2F-MEMBER depth` 已結構化；L 是兩片 6t
  Stopper 的外側總長，MEMBER N 切長修正為 `L-12`。10/12 吋仍為
  Detail a 雙 Channel。
- Stopper 的四個 10C 已從 M×K 毛矩形扣除；Base Plate 的 C/D/E/J、
  Top Plate B/F 與 6 mm weld 亦保存為加工參數。
- EXP.BOLT 原本硬算 1 kg/支但 D-14 沒有單重，現改為 0 並保留採購 blocker。
- Wing Plate 的 P 由 NOTE 3 指定現場切割；20/25/10C 已轉成六頂點 polygon，
  未提供 override 時以表值作 polygon 估重。Ø6 weep hole 缺中心定位，
  10/12 吋雙 Channel 也缺組立間距，因此整體維持 fabrication-partial。

## 第十二輪落地：Type 15 三份 D-16

- 三來源都有 Type 15，但構造不能共用一套表：
  - 中威為 2~12 吋 Channel，10/12 吋依 Detail o 使用雙槽鐵；
  - 22A 與 20E4588 為 4~12 吋單支 H Beam，另有 I×J×T reinforcement plate；
  - 22A 的 12 吋 F=16，20E4588 為 F=19，已保留來源差異。
- 中威依各尺寸的 L/H 矩陣硬限制；兩份中鼎皆為 L≤1000，並依表列
  H(MAX)=3000/4000 硬限制。designation 的前兩碼仍是 L、後兩碼是 H。
- L 尺寸標在兩片 6t Stopper 外側，MEMBER N 切長採 `L-12`。中威 supporting
  pipe 為 `H-2F-member depth`；中鼎因 B plate 與 H Beam 間多一片
  reinforcement plate，切長再扣 T。
- Wing Plate 已依 Q/P/20/25/10C 建六頂點 polygon，Stopper 依 M/K/四角10C
  建八頂點 polygon；Base/Top/reinforcement plate、焊腳與各構件來源／版次
  都已結構化。
- P 仍由 NOTE 3 指定現場切割；Ø6 weep hole 未標中心高度。中威 10/12 吋
  Detail o 也沒有標雙槽鐵間距，因此整體保留 fabrication blocker。

## 第十三輪落地：Type 16 三份 D-18

- 三來源的 A→Pipe B→cover side 表相同，範圍 2~24 吋，但 designation
  不同：中威只有 H 且右端 overhang 固定300；22A/20E4588 的第四段可修改
  overhang C，未填時預設200。中威 cover side 符號是 C，中鼎是 D。
- 舊程式把兩段 Pipe B 固定成 SUS304/A53Gr.B，並用
  `1.5A+OD/2+100` 與其互補式推切長；D-18 沒有這些公式。中威 NOTE 3
  反而明定 Hx field cut。現在缺 `dummy_pipe_cut_length_mm` 時管長／重量為0，
  不再產生看似精確的假下料。
- NOTE 2 只針對 alloy/stainless/stress-relief main line：接主管的 segment
  必須同主管材且與主管在 shop 一起製作。`special_main_line=true` 時系統要求
  `main_line_material` 與 `special_main_line_piece_cut_length_mm` 後才分段。
- D-80 interface 在三張圖皆是 IF REQUIRED / NOT FURNISHED，不列 BOM。
  Cover Plate 依表列 square×6t，焊腳6 mm與 pipe-weld 厚度限制已保存。
- 四種主管接合外形沒有 designation axis，cope/fishmouth 也沒有下料輪廓；
  特殊案例 Ø6 weep hole 缺中心定位。這些維持 fabrication blocker。

## 第十四輪落地：Type 19 D-21

- 只有中威 E25-24 供 Type 19；22A/20E4588 沒有 D-21，維持來源安全閘門。
- D-21 NOTE 1 明定 L 現場切割。舊程式把表列600/1200直接當成下料長度，
  現改為缺 `member_cut_length_mm` 時長度／重量0；表值只保留 drawing
  reference。
- 1~6吋的 L40/L50/L75 angle 規格不變；8~12吋 A-A 視圖是
  `CUT FROM H194X150X6X9` 的 T-section，不是整支 H Beam。重量改按 parent
  30.6 kg/m 的一半15.3 kg/m，並保存 nominal T 截面與剖分來源。
- 1:1（45°）斜率、6 mm兩側焊與 L-angle Detail-Z 20C pocket-drain cut
  已結構化。上下端貼管 cope、20C完整arc與H剖分kerf仍是加工 blocker。

## 第十五輪落地：Type 20 三份 D-22

- 三來源外形與 designation 相同，但 MEMBER/H(MAX) 表不能共用。中威為
  L50/1500、L65/1500、L75/2000、C100/3000；22A 與20E4588為
  L50/1000、L75/1500、C125/2000。未表列 member 或 H 超限均硬停止。
- `20-{M}-{HH}{Fig}` 可確定 member、H 與 Fig A/B，但沒有 supported line
  size 或 U-bolt rod diameter。兩者改由 row override 明確輸入，不由其他欄位
  或來源自動猜測。
- Slot Detail 已保存2孔、半長30（完整長60）、寬=`rod+3`，以及2~12吋的
  Z=76/104/130/184/235/286/340。D-80、standard U-bolt與washer/U-bolt
  assembly依圖面標註不供應，不列BOM。
- 型鋼規格與H切長已達BOM-ready；但Detail的80/30/30基準不足以無歧義輸出
  兩個孔中心座標，所以仍明列加工blocker，不製造假定位尺寸。

## 第十六輪落地：Type 21 三份 D-23

- 中威的member表為L50/H1000、L65/H1500、L75/H2000，未列L(MAX)；
  22A與20E4588只有L50/H1000/Lmax500、L75/H1500/Lmax800，並註明
  Fig C若L>500只能使用L75。來源member及H/L超限均改成硬停止。
- Fig A/B的L固定300/500；Fig C第四段為L×100。NOTE 2雖稱H field cut，
  但H已編入designation，故仍是該支撐的實際垂直角鋼切長，不另套假公式。
- 垂直H段、水平L段、管中心離自由端100、底部6 mm全周現場fillet weld與
  D-68不供應狀態已結構化，型鋼BOM可成立。
- 上角接頭的精確端切／貼合輪廓及焊腳尺寸沒有完整標註；designation也不含
  supported line size，不能展開D-68孔徑與孔距。這些維持加工blocker。

## 第十七輪落地：Type 22 三份 D-24

- 中威使用`HH(Fig)M42`，member為L50/L65/L75/C100且D-24只准M-42 L/P；
  22A與20E改用`HHFig-M42`，只有L50/L75及L(MAX)500/800，22A准L/T、
  20E准L/P/T。舊程式只解析中威格式且錯放行幾乎全部M-42字母，已按來源分開。
- H/L上限改硬停止；Fig A/B固定300/500，Fig C依來源格式讀末段L。
- 修正共用M-42型鋼扣件級距：過去L50字串被誤當50吋管徑，20E會錯選M24；
  現依M-43型鋼row選取，L50正確為M16×40。
- 中威C100雖在D-24表列，但M-43沒有精確C100 row；C125 fallback只保留估算
  並令`bom_ready=false`。上角接頭與D-68孔位仍是加工blocker。

## 第十八至二十七輪落地：Type 23-28、30-33

- Type 23 D-25：三來源 member/envelope 分流。支撐是 H/L 兩件，管線直接坐在
  水平件上，不含舊文件所稱 U-bolt。下角端切、焊腳與止滑方式維持 blocker。
- Type 24 D-26：只有中威有圖。單支角鋼切長為 H，不是 H+100；三種安裝方向
  沒有編入 designation，需明示 `mounting_orientation`。
- Type 25 D-27：來源表分流；Fig.C 改用 M-34 精確外形。再核 M-34 後確認標準板
  依版型為四孔或六孔，K bolt 數與孔數一致，不再使用估算板。
- Type 26 D-28/D-29：三件框架保持 H/H/L；Fig.C 為兩片 M-34 plate，每片依
  版型四孔或六孔，因此 K bolt 合計八支或十二支。
  20E Fig.B 的 down-stop 選型需管徑，表格空白範圍直接停算。
- Type 27 D-30：移除 `H-15`/`H-150` 假切長、假第二 member 與假三片側板。
  member 切長及 6t 頂板寬度缺值時保持零重量 blocker；9t polygon 肋板依來源規則。
- Type 28 D-31：三來源 member/envelope 與 M-42 subset 分流。門架為 H/L/H 三件，
  左右腿各有一組 M-42。水平/垂直管配置不可由 member 猜，改由 override 選擇。
- Type 30 D-35：Fig.A/B 都是 H 向件 `H-15` 加 L 向件 L；L1/L2 必須合計為 L。
- Type 31 D-36、Type 32 D-37、Type 33 D-38：來源 member/envelope 分流；
  結構分別為 H/L/H 上立框、H/L/H 吊架、H/L 側焊半框。三者皆保存 existing
  steel 接合與角部端切 blocker，不以可算重量冒充完整加工圖。

## 第二十八至三十七輪落地：Type 34-37、39、41-45

- Type 34 D-39：中威與22A分流；20E無圖。結構為H右柱與L上梁各一支，
  C150在22A可到2000mm，中威仍為1500mm。現場裁切與existing steel接合保留blocker。
- Type 35 D-40：三張圖確認Fig A/B是同一支member的截面／安裝型式，不是
  Fig-B雙條。兩型qty皆為1；20E C100 Fig-A上限1200mm，其他來源1400mm。
- Type 36 D-41：只有中威有圖。單支member、M-34 Type-C一片；K bolt數按
  M-34四孔／六孔版型，未給bolt長度與單重時不補估值。
- Type 37 D-42：三來源表與公式相同；主梁H+C與斜撐長度可算BOM，斜撐端切
  與貼合輪廓未標完整，故加工狀態維持partial。
- Type 39 D-45：三來源幾何相同；中威/22A用3/4"x50，20E用M20x50。
  M-34與M-35/36各一片，K bolt數為兩片孔數總和（8或12），不是兩組。
- Type 41 D-49：只有中威有圖。主梁切長修正為L+200；表格箭頭確認41-4~9
  Member1均為H150，41-5~7的Member2為L75。刪除L×1.414斜撐與猜測正方底板；
  Fig-B需明示brace_cut_length_mm，base plate平面外形仍是blocker。
- Type 42 D-50：只有中威有圖。H/G與trunnion公稱尺寸表可用；trunnion的
  schedule、材質與切長須D-72/73/74核定，移除任意單重並令BOM未完成。
- Type 43 D-51/D-52：中威與20E分流；22A無圖。20E明註TRUNNION PIPE
  NOT FURNISHED，已排除BOM並採M20x50；中威保留trunnion但需後續核定。
  兩片lug plate的K bolt依孔數合計8或12。
- Type 44 D-53：只有中威有圖。框架攤開為兩支H+Q+3縱向member與兩支
  2Q+6橫向member，另有兩片90×45×6 clip plate與兩支bolt；H≥1200才加brace。
  MIN. CHANNEL選型圖仍待完整矩陣化。
- Type 45 D-54/D-55：只有中威有圖。框架攤開為兩支H-A+Q+3縱向與兩支
  2Q+6橫向member；M-34固定兩片。只有H>1140才加入brace與一片M-35/36，
  Detail Z/Y bolts皆按標準板四孔／六孔計。選型圖與vessel端實際端切保留blocker。

## 第三十八至四十七輪落地：Type 46-49、51、56-60

- Type 46 D-56：只有中威有圖。兩支縱向為`H+Q+3`、兩支橫向為`2Q+6`，
  clip plate/bolt各兩件；`H>1200`才加brace。D-80不重複列料。
- Type 47 D-57/D-58：中威與20E4588分流，22A無圖。四支框架、兩片M-34
  與孔數對應bolt已修正；只有`H>1140`才有brace及一片M-35/36。20E使用
  8~24吋、C100~C200與公制fastener；D-80為不供/另件引用。
- Type 48 D-59：只有中威有圖。單片150×100矩形板；1/2~2吋6t、3~6吋9t，
  保存100/20偏移與6mm weld。
- Type 49 D-60：只有中威有圖。FIG-A(>=3吋)引用M-11+M-41，FIG-B(<3吋)
  引用M-12。刪除任意重量；M圖未轉錄完成前只輸出零重量reference。
- Type 51 D-62/D-62A：中威與22A分流。8~24吋分別使用L65與L75；大管
  接觸角80°/120°，22A D-91不供。26~42吋取消舊300mm假切長，改要求
  `member_cut_length_mm`。
- Type 56 D-67/D-67A：只有中威有圖。A~R重新確認；<=2-1/2吋
  PL100×100×6×2可加工。3吋以上外接料估重保留，但加工輪廓明確阻擋。
- Type 57 D-68：三來源分流。中威/22A沿用M-26；20E為1/2~6吋公制表，
  `(S)`增加1t SS304 shim。刪除1kg placeholder；無效FIG硬停止。
- Type 58 D-69：只有中威有圖。舊推定表逐列重建，並移除圖上不存在的
  3/8、26、28吋。plate孔位與FIG-B焊腳X已結構化。
- Type 59 D-70：三來源輪廓相同而材質分流；22A增加`(N)` Alloy 825，
  20E只允許CS/`(S)`。後綴只允許FIG-B；10~14吋SS厚度空白改停算。
- Type 60 D-71：只有中威有圖。A~T逐列重建，刪除22/34/38吋與舊FIG-B
  假bottom plate。side plate貼合輪廓未完整，維持BOM/fabrication blocker。
