# Type 21 — D-23 側掛懸臂 U-bolt 支撐

| 項目 | 內容 |
|------|------|
| 中文名稱 | 側掛懸臂 U-bolt 支撐 |
| 英文名稱 | Cantilever U-bolt Support |
| 圖號 | D-23 |
| 來源 | 中威 E25-24、CTCI 22A_5123A、CTCI 20E4588 |
| 編碼 | `21-{M}-{HH}{Fig}`；Fig C 再加 `-{LL}` |
| 狀態 | 三來源 BOM 已分流；加工圖仍有接頭與孔位 blocker |

## 來源差異

| 來源 | MEMBER M | H(MAX) | L(MAX) |
|------|----------|--------|--------|
| 中威 E25-24 | L50 / L65 / L75 | 1000 / 1500 / 2000 | 圖面未列 |
| CTCI 22A_5123A | L50 / L75 | 1000 / 1500 | 500 / 800 |
| CTCI 20E4588 | L50 / L75 | 1000 / 1500 | 500 / 800 |

兩份中鼎並註明 Fig C 的 L 大於 500 mm 時只能使用 L75。系統依所選來源
驗證 member、H(MAX) 與 L(MAX)：未表列 member 仍停止，L/H 上限則採有限
外插分級。一般警示可保留 BOM；高風險只供查核暫算，禁止正式放行。

## 編碼與 BOM

```text
21-{M}-{HH}A       L 固定 300 mm
21-{M}-{HH}B       L 固定 500 mm
21-{M}-{HH}C-{LL}  L = LL × 100 mm
```

H 與 L 各對應一段相同規格角鋼。NOTE 2 雖要求 H 現場切合，但 H 已明確編入
designation，因此系統將它視為該支撐的實際切長；這和只有圖面參考長度、
designation 未帶現場值的型式不同。

Standard U-bolt D-68 標示 NOT FURNISHED，不列入 Type 21 BOM。

## 加工資料

目前已保存：

- 垂直角鋼 H 切長與水平角鋼 L 切長。
- supported line center 距水平構件自由端 100 mm。
- 底部與 existing steel 為 6 mm、all-around、field fillet weld。
- Fig A/B/C、來源圖號、版次、member 上限與 D-68 不供應狀態。

仍需補齊：

- 上角兩段角鋼的精確端切／貼合輪廓。
- 上角接頭焊道未標示的焊腳尺寸。
- designation 不含 supported line size；D-23 也未直接給 D-68 U-bolt
  所需的孔徑與孔距。

因此型鋼 BOM 已是 `bom_ready=true`，但上述資料確認前
`fabrication_ready=false`。
