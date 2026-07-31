# Type 46 以前原圖複驗（2026-07-30）

> 本文件是本輪人工複驗快照，不取代原始圖面、runtime、config 與 regression tests 的真值優先序。

## 範圍與方法

- 範圍：Type 編號小於 46、已有可辨識原圖且已有 calculator 的 38 個數字 Type。
- 已複驗：01、03、05、06、07、08、09、10、11、12、13、14、15、16、19、20、21、22、23、24、25、26、27、28、30、31、32、33、34、35、36、37、39、41、42、43、44、45。
- 未納入「通過」：02、04、17、18、29、38、40 等沒有本輪可對照 calculator／原圖組合的編號。
- 方法：開啟原始 PDF 的渲染頁逐張比對，而非只比程式、Markdown 或 catalog；再以 source-profile tests 與 `validate_tables.py` 鎖定結果。
- 判定原則：計算結果與來源相符，不等於可直接出加工圖。原圖未尺寸化的輪廓、孔位、現場配切、材質或外購件單重，均保留明確 blocker。

## 本輪發現並修正

| Type | 原圖基準 | 修正結果 | 加工圖狀態 |
|---|---|---|---|
| 03 | 中威 D-3 Rev.1 | 新增來源設定檔與硬限制；保留既有 574.8 mm 範例，但把 1.5D 彎頭中心半徑標成可覆寫假設；移除 U-bolt 的 SUS304／1 kg 假值 | H、彎頭中心半徑、U-bolt 規格／材質／單重未確認前阻擋 |
| 05 | 中威 D-5 Rev.1 | 重製 H-15、水平 130、L50/L65/L75、M-42 D/L/P/R；D-68 U-bolt 依原圖維持 NOT FURNISHED | H 為現場配切；須用現場實值才可定尺 |
| 06 | 中威 D-6 Rev.1、M-37 Rev.2 | 補回舊程式漏掉的 M-37 Type-F Lug Plate 與 K bolt；角鋼為 2 孔／2 bolt，C150 為 4 孔／4 bolt；修正 LGP-F-8 為 C200×90×8 | H/L 現場配切；K bolt 材質／單重待定；A+B≠L 時阻擋組立圖 |
| 07 | 中威 D-7 Rev.1 | 重製 Pipe B=L+200、Pipe C=H-200-Plate F-M-42；硬限制 `1500 < H < 3500` 且只允許 M-42 J；移除原圖不存在的 SUS304／4 kg U-bolt 假 BOM | 彎頭貼合端輪廓與 Ø6 weep-hole 定位未完整尺寸化，維持阻擋 |

Type 07 標準案例 `07-2B-20J` 的重量由舊快照 33.54 kg 修正為 29.54 kg；差額 4 kg 正是被移除的假 U-bolt。

## 逐 Type 複驗結論

「一致」表示本輪重開原圖後未發現新的來源矛盾；不表示所有構件都已 fabrication-ready。

| Type | 複驗結論 | 本輪確認重點 |
|---|---|---|
| 01 | 一致，保留 blockers | D-1 連續支撐管、來源表格、M-42 集合；頂端 cope／restraint 細節仍待定 |
| 03 | 已重製並修正 | 見上表 |
| 05 | 已重製並修正 | 見上表 |
| 06 | 已重製並修正 | 見上表 |
| 07 | 已重製並修正 | 見上表 |
| 08 | 一致，保留 blockers | D-8 stopper 分支、L-12／L 規則與來源差異 |
| 09 | 一致，保留 blockers | D-9 兩段 dummy-leg、M-43 刪除規則與來源硬體差異 |
| 10 | 一致，保留 blockers | 中威雙 Plate-F 與 20E 單腿／M-1 分支不混用 |
| 11 | 一致，保留 blockers | 彈簧數量、墊圈數量、field-cut 與來源範圍 |
| 12 | 一致，保留 blockers | 取消 H-100 假公式、Plate P×2、field-cut |
| 13 | 一致，保留 blockers | D-13／M-4／M-47，M-47 厚度 1.5 mm |
| 14 | 一致，保留 blockers | D-14/D-15 L-H envelope、Wing／Stopper 淨形 |
| 15 | 一致，保留 blockers | 三來源 Channel／H Beam 分支與 12" 板厚差異 |
| 16 | 一致，保留 blockers | D-18 A/B/cover 表、C 語意與 Pipe B field-cut |
| 19 | 一致，保留 blockers | D-21 field-cut 與 8–12" T-section 半母材重量 |
| 20 | 一致，保留 blockers | 三來源 member／尺寸上限與雙 60 mm slot |
| 21 | 一致，保留 blockers | 三來源 member／H-L envelope 與 D-68 介面 |
| 22 | 一致，保留 blockers | D-24 編碼分段與來源別 M-42 集合 |
| 23 | 一致，保留 blockers | D-25 來源 member／envelope |
| 24 | 一致，保留 blockers | D-26 來源 member／envelope |
| 25 | 一致，保留 blockers | D-27 M-34 plate／K bolt 數量 |
| 26 | 一致，保留 blockers | D-28 M-34 plate／K bolt 數量 |
| 27 | 一致，保留 blockers | D-29 不再發明 post／top-plate 幾何 |
| 28 | 一致，保留 blockers | D-30 雙 M-42 set 與 line-layout 分支 |
| 30 | 一致，保留 blockers | D-33 兩 figure 均使用 H-15 |
| 31 | 一致，保留 blockers | D-35 H-L-H 結構 |
| 32 | 一致，保留 blockers | D-36 H-L-H 結構 |
| 33 | 一致，保留 blockers | D-38 H-L 結構 |
| 34 | 一致，保留 blockers | 來源限制與無 20E Type 34 的硬 gate |
| 35 | 一致，保留 blockers | figure／member 排除規則 |
| 36 | 一致，保留 blockers | 中威專屬來源 gate |
| 37 | 一致，保留 blockers | 端部切形未完整尺寸化 |
| 39 | 一致，保留 blockers | 原圖三角函數尺寸鏈 |
| 41 | 一致，保留 blockers | 主件 L+200；brace 幾何未知不得出假加工圖 |
| 42 | 一致，保留 blockers | 原圖三角函數／來源公式與中威 gate |
| 43 | 一致，保留 blockers | 20E trunnion NOT FURNISHED 與中威未知單重分開 |
| 44 | 一致，保留 blockers | 縱向 H+Q+3、橫向 2Q+6、H≥1200 brace |
| 45 | 一致，保留 blockers | 縱向 H-A+Q+3、橫向 2Q+6、H>1140 brace |

## 驗證基線

- Type 46 以前 source-profile／source-fabrication tests：205 passed。
- 新增 Type 03／05／06／07 原圖與加工契約測試。
- `validate_tables.py`：`VALIDATION COMPLETE`。
- 完整 pytest 結果以 `docs/STATUS.md` 的本輪紀錄為準。
