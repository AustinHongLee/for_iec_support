# Type 01 — 假管支撐（含底板）

| 項目 | 內容 |
|------|------|
| 中文名稱 | 假管支撐（含底板） |
| 英文名稱 | Dummy Pipe & Plate |
| 圖號 | D-1（HP6 / D7TS-701-E / STM-05.01） |
| 適用範圍 | 中威 2"~50"；22A/20E4588 2"~24" |
| PDF | `TYPE-01_D-1.pdf` |
| 狀態 | ⚠️ 來源別 BOM 已核對；加工圖部分完成 |

---

## 系統本質

以焊接假管 (Dummy Pipe) 從主管線延伸至底板的基本支撐型式。

三套 D-1 都把 Supporting Pipe "B" 畫成一支連續構件。特殊主管材質時，
整支假管與主管同材質；舊程式的「上段同主管、下段固定 A53Gr.B」是歷史估算，
已不再採用。

## 三來源差異

| 來源 | 管徑表 | H 限制 | 24" row | M-42／扣件 |
|---|---|---|---|---|
| 中威 E25-24 | 2"~50" | H<1500 | 14" STD.WT，L=677 | A~Y 圖示範圍；英制 EXP.BOLT |
| 中鼎 22A | 2"~24"（無 22" row） | H≤1200 | 12" STD.WT，L=647 | 僅 B/C/E/F/G/H/K/L/R/S/T；英制 EXP.BOLT，12" row 為 1" |
| 中鼎 20E4588 | 2"~24"（無 22" row） | H<1500 | 12" STD.WT，L=647 | 同一組有限型式；公制 MACH.BOLT + HEX NUT |

專案必須先選來源；designation 本身無法可靠推斷這三套規則。

---

## 編碼格式

```text
01-{A}B-{H}{M42字母}
```

---

## 核心運算邏輯

```text
Supporting Pipe B 切長 = H + L（Elbow）
Supporting Pipe B 切長 = H + M（Tee，M 取 ASME B16.9）
Supporting Pipe B 材質 = 整支跟隨主管線
底板／角鋼／扣件 = 來源別 M-42/M-42A/M-43 recipe
```

H 超出來源限制時採有限外插分級：差異不逾 100 mm 且不逾 10% 為一般警示；
其餘在上限 2 倍且超額不逾 2000 mm 內列高風險暫算；超出護欄仍停止。
任何外插結果都不直接代表可出加工圖。

## 加工圖資料狀態

目前已結構化保存：

- `D1-SUPPORTING-PIPE-B` 構件 ID、完整管規、H、L/M、總切長；
- Ø6 weep hole、6 mm weld 與來源圖／版次；
- M-42 plate a/b/c/d/e 的長寬厚、四孔孔距／孔徑；
- 角鋼切長與來源別 fastener 規格、數量；
- restrain function 與 elbow/tee 分支。

仍未宣告可直接出完整加工圖，原因是 Supporting Pipe B 頂端與 elbow/tee
相貫的 cope/fishmouth 展開輪廓尚未參數化；A/G/F restraint element 也只有示意，
沒有零件尺寸。BOM 可依來源圖計算，但 `fabrication_ready=false`，不得把平口管端
當成已核定加工輪廓。

---

## 設計重點

- 與 `M-42` 下部構件有關，最終組成會受到末段字母或允許型別限制。

---

## 與相近 Type 的關係

| 類別 | 型式 | 說明 |
|------|------|------|
| Dummy Pipe 家族 | 01 / 07 / 09 / 10 / 11 / 12 / 13 / 16 | 共通點是從主管引出支撐腿，再決定底部承載或限制方式。 |

---

## 備註

- 計算真值以三套原始 D-1/M-42 PDF、`configs/type_01.json`、
  `configs/m42_profiles.json`、calculator 與 golden tests 為準。
