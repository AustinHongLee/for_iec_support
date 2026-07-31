# Type 60 以上原圖複驗與加工圖契約重製

日期：2026-07-30

## 範圍與判定方法

第一階段盤點當時 runtime 已實作的 15 個 Type 60 以上項目：

`60, 61, 62, 64, 65, 66, 67, 72, 73, 76, 77, 78, 79, 80, 85`

第二階段再逐圖建立 10 個來源群組：

`81, 82, 82A, 83, 84, 85, 86, 87, 101, 102`

第三階段逐圖建立 10 個來源群組：

`103, 104, 105, 108, 110, 112, 115, 118, 119, 120`

第四階段逐圖建立最後 5 個來源群組：

`125, 126, 127, 128, 129`

第五階段補回原 numeric audit 漏掉的 11 個 cold-support 來源群組：

`109C, 110C, 112C, 113C, 114C, 115C, 116C, 117C, 119C, 120C, 121C`

Type 85 在第二階段重新判讀後修正第一階段的「專屬保溫鞍座」結論，詳見下表。

每個 Type 都以 `單張-本案有關/` 的原始 PDF 為第一真值，並檢查：

1. designation 能否唯一決定尺寸與來源；
2. 表格轉錄是否與原圖一致；
3. assembly dimension 是否被誤當 finished cut/developed blank；
4. 重量是否來自可證實的淨幾何或來源單重；
5. 是否已包含未來加工圖需要的 component ID、來源、孔／輪廓／焊接資料及 blocker。

「複驗通過」不等於 fabrication-ready。資料不足時，正確結果是零重量 reference 加明確 blocker，不是以外框或 placeholder 補數。

## 結果總覽

| Type | 本輪結果 | 核心結論 |
|---|---|---|
| 60 | 複驗維持 | D-71 FIG-A exact；FIG-B 接觸輪廓仍阻擋 |
| 61 | 重製 | 三來源 profile；正確 trunnion schedule/wall；移除 OD+50 pad |
| 62 | 後續重製 | 來源 gate 保留；後續 M-3/M-31/M-33 批次發現 H≠rod cut，已移除 rod/clamp/nut 假重量 |
| 64 | 重製 | D-78 E/G 表與 starred figure 修正；H 不再當 rod cut |
| 65 | 重製 | D-79 表重抄；移除不存在尺寸與自創 stiffener |
| 66 | 複驗維持 | 來源別 D-80 engine 與既有加工 blocker 可保留 |
| 67 | 複驗維持 | D-81 來源別邊界／clamp／gasket 可保留 |
| 72 | 重製 | M-54 B 為成形跨距；退休 B×C×T 與 1 kg bolt placeholder |
| 73 | 重製 | M-53 A 可作展開長；strap 扣孔精算，其餘假重量退休 |
| 76 | 重製 | D-91 只給 120°、400L、12t MIN；需實際展開寬／厚度 |
| 77 | 重製 | 多片 saddle 不可用 C×H+A×B 外框估重 |
| 78 | 重製 | M-54 FIG.1 仍缺展開基準；重量阻擋 |
| 79 | 重製 | M-55 為多片組立；退休 B×E×T 單板估重 |
| 80 | 重製 | 三來源 D-95/D-96；D-95 復用同來源 D-80，D-96 大件阻擋 |
| 85 | 第二階段重製 | D-105/D-106 直接引用同來源 D-80/D-80B；撤回專屬 insulation-saddle 解讀 |

## Type 81~102 第二階段結果

| Type | 原圖判定 | 實作結果 |
|---|---|---|
| 81 | 中威 D-97/D-98 引用 D-81/D-81A | 復用 D-81；M-4/M-47 估重退休，16"+ 安全 reference |
| 82 | 中威 D-99/D-100 guide，3 mm clearance | Member M angle 精算；Member C/large saddle 多片輪廓阻擋 |
| 82A | 中威 D-100A-1/-2 fixed | 共用尺寸表但 clearance=0、來源圖與焊接語意獨立 |
| 83 | 三來源 D-101/D-102 為 D-80 shoe 加 axial stop | 復用同來源 Type 80；stop assembly 零重量待片件 recipe |
| 84 | 中威 D-103/D-104 為 D-81 加 guide angle | 復用 Type 81；L40 guide cut/片數未定時歸零 |
| 85 | 三來源 D-105/D-106 直接引用 D-80/D-80B | 移除舊 Type 52/停算路徑；來源範圍與 D-80 readiness 分流 |
| 86 | 中威 D-107/D-108、22A D-107 引用 D-81 family | 復用 D-81；22A 不接受不存在的大管 branch |
| 87 | 中威 D-109、22A D-108 adjustable post | H 保持組立高度；中威 round Plate D 精算，其餘缺口歸零 |
| 101 | D-110 small-bore rib；中威三片、20E 單片 | 保存來源 rib count；缺 OD/cope 時不以 190/sin60 假造切長 |
| 102 | D-111 E-plate interface | 保存 E/W 與 FIG offsets；不供應項及 plate 輪廓明確阻擋 |

## Type 103~120 第三階段結果

| Type | 原圖判定 | 實作結果 |
|---|---|---|
| 103 | 三來源 D-112；中威/22A 的 d 是 bolt size，20E 另有 hole d | 外框/孔距分來源；只有 20E 計四孔淨板，FIG-C 兩片 |
| 104 | 中威 D-113 引用 M-52 | B/C/D/E/F 與 spring data 保存；組立/flat-bar scope 不完整時歸零 |
| 105 | 中威與 20E D-114/D-115 | M/N/P 來源表分開；field-cut 與 300 MAX 不冒充 finished cut |
| 108 | 中威 D-119/D-120，同一 line/H 可有兩種 Pipe B | 多解時強制選 B；FIG-C FB 精算，fishmouth/lug/spacer 阻擋 |
| 110 | 只有 20E D-123 | 保存 FIG/L/section；site-fit assembly 不以 clear span 假算 BOM |
| 112 | 中威 D-125 | 底板精算；ANSI 150# flange drilling 未完整前兩片立板歸零 |
| 115 | 中威 D-128 | M/P 下料、片數、等距位置可發圖；existing-steel positions 待 project layout |
| 118 | 中威 D-131/M-57 | actual OD 驅動兩片 saddle、四 drilled lugs 與中性層展開 |
| 119 | 中威 D-132/M-57~59 | 1~8 吋 M-58+二孔板；10~32 吋 M-59，分流公式鎖定 |
| 120 | 中威 D-133/D-134 | guide hardware 分流；M-57 CUT 3MM、M-59 CUT TO SUIT 及複合 collar/pour shoulder 歸零 |

## Type 125~129 第四階段結果

| Type | 原圖判定 | 實作結果 |
|---|---|---|
| 125 | 中威 D-135 U-bolt + I-Rod clamp | 逐列保存 d1/L/P/A/I/F/G/H、扭矩與載重；片數/溫度級明選，未提供的採購重量不猜 |
| 126 | 中威 D-136 I-Rod cross-beam pad | 逐列保存 L/C/D；schedule 明選後回傳最大間距 M，無表列值時要求專案結構計算 |
| 127 | 中威 D-137 C150 field-cut support | PL12x170x330 四孔淨板可發圖；C150x75x6.5 無核定 kg/m，不套相近 section |
| 128 | 中威 D-138 C200 field-cut support | PyMuPDF 恢復完整向量頁複驗；C200 備料重及 PL12x170x380 四孔淨板可算 |
| 129 | 中威 D-139 twin H150 field support | 兩支 H150 備料與動態 `170x(W+330)` 底板可算；CHANNEL/H-section 來源衝突保留警告 |

## Cold-support xxC 第五階段結果

| Type | 原圖判定 | 實作結果 |
|---|---|---|
| 109C | DSP-500-006 C-52 vessel/trunnion cold support | 保存 line/B/C/45° 與 section/reference；組立尺寸不冒充 finished cuts |
| 110C | C-53 opposed-clip trunnion cold support | 保存 line/B/C/45°；L100/L75 frame 與 ending scope 未唯一化時歸零 |
| 112C | C-55 diagonal vessel cold support | 保存 B/C/45°；不以三角形外框推算 brace cuts |
| 113C | C-56 cantilever Member M | 依 L50/L75/C100 與 C 精算型鋼備料；輸出 `P×C<=40 kg-m` 載重邊界 |
| 114C | C-57/C-58/C-59 wall-clip cold support | 嚴格分管徑與 C=1000/1100 上限；C-21/C-24/N 表未補前整組歸零 |
| 115C | C-60/C-61 existing-surface cold support | 拆解合併 cradle token；C 不當 finished cut |
| 116C | C-62/C-63 FIG-A/B/C interfaces | 三個 figure component chain 分開保存，不跨圖套料 |
| 117C | C-64 cantilever with 9t end plate | Member M cut=`C-9` 可算；端板第二方向未給，板件歸零 |
| 119C | C-67 nozzle cold support | 只接受明列管徑並選 L75/L100；無 Q 展開長時整組歸零 |
| 120C | C-68 FIG-A/B cold hanger | H 為組立高度；`H>2000` 才標 M-21，M-22/M-23 chain 分開 |
| 121C | C-69/C-70 30-inch+ cold guide | CR32~CR46 表逐列轉錄；左右 H125 Member Q×2 可算，其餘板件歸零 |

## 主要修正

### Type 61

- `2"` trunnion 為 SCH.80；`3"~10"` 為 SCH.40 or greater；`12"/14"` 為 3/8" wall or greater。
- T1/T2 與 H 可決定直管備料，但 main-line saddle cut 仍需 main-line OD／模板。
- `(P)` 無法由編號決定 pad 尺寸。只有提供完整展開長、寬、厚 override 才計重。
- D-73/D-74 capacity 還需要 main-line size/schedule、材質、溫度及 moment。

### Type 64 / 65

- D-78 移除不存在的 1-1/4" row，補正 3-1/2" 與 4"~12" rod sizes；1/2"、3-1/2" 只允許 FIG-B/C。
- Type 64 的 H 是兩管中心距，不是 M-22 finished cut。
- D-79 移除不存在的 2-1/2"、5" rows，重抄 L bucket/member/rod/Y。
- Type 65 的 H 是組立高度，不是 M-23 finished cut；12" 以上 stiffener 不再依管徑自創輪廓。

### Type 72 / 73 / 78 / 79

- M-54 的 B 是成形後外側跨距；Type 72/78 的 strap 沒有 flat development 時歸零。
- M-53 的 A 是可使用的平板總長；Type 73 strap 依 `A×F×T` 扣 `D+3` holes 精算。
- Spring ideal-helix、stud G-length、washer placeholder、`E×H/2` gusset estimate 全部退休。
- M-55 的 B/E/T 是 assembly dimensions；Type 79 不再把整組當單一平板。

### Type 76 / 77 / 80

- D-91 pad 可由 main pipe 切取或 C/S plate 製作，12t 只是 minimum；沒有 actual development/thickness 時不算重量。
- D-92 saddle 是多片複合輪廓；A/B/C/T/H 不能直接當矩形 blank。
- D-95 明示 upper shoe 參照 D-80，因此 Type 80 復用同來源 Type 66 engine，再加入 beam-interface member。
- 中威、22A、20E 的 D-95 grouping 不同；20E D-96 只表列 26/28"，不可接受 30"+。
- 16"~24" fabricated member 與 D-96 大 saddle 在 piece decomposition／淨輪廓未完成前維持零重量 reference。

## Type 60+ 來源覆蓋

`docs/type_source_audit.json` 目前盤點到的 39 個「數字／hot support」
Type 60+ 來源群組均已有 runtime handler。

另有一套未被 `TYPE-*.pdf` audit 納入的 cold-support `xxC` 原圖，位於
`python_app/assets/Type/`。本輪已逐頁檢查並實作其中 60 以上的 11 組：

`109C, 110C, 112C, 113C, 114C, 115C, 116C, 117C, 119C, 120C, 121C`

因此目前 numeric/hot 的 39 組與這 11 組 cold-support 均已有 runtime
handler、config、UI 說明與 drawing-truth tests。原 audit 仍明確只代表
numeric/hot，避免把兩套資產的覆蓋數混為一談。

這不表示每組都已 fabrication-ready。現場切配、供應商成品單重、專有
I-Rod 淨斷面、複合輪廓及未提供的 project layout 仍依各 Type 的 blocker
管理，沒有以外框或近似型鋼補數。

## 驗證

- `pytest -q`：588 passed。
- `python validate_tables.py`：`VALIDATION COMPLETE`。
- 40 個 `phase 2L-A unmanaged material entry` 為既有 soft-lock 清單；本輪新增 Type 61 的 A53 Gr.B 路徑，因此由 39 增為 40。
- Type 61~80 有 13 個專用 source/fabrication regression tests；Type 81~102 有 20 個；Type 103~120 有 19 個；Type 125~129 有 15 個；cold-support xxC 另有 20 個，鎖定來源表格、明選分支、動態板件公式、現場切配及加工圖 blocker。
