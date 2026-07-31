# Type 10 — 來源別可調式 Dummy Pipe 支撐

| 項目 | 中威 E25-24 | 中鼎 20E4588 |
|------|-------------|--------------|
| 圖面 | D-10 / D-10A | D-10 / M-1 |
| Supported line | 1.5"~50" | 6"~16" |
| H | `<1500 mm` | `<1500 mm` |
| Construction | 雙 Plate F＋4 adjustable bolts | 單柱＋annular base washer＋M-1 |
| 狀態 | BOM/零件幾何已建；上端 cope、weep-hole 位置待補 | BOM/零件幾何已建；上端 cope、M-1 成品重量待補 |

22A_5123A 沒有提供 Type 10，該 source profile 會明確停算。

## 中威 Branch

中威是四點可調平台：

```text
Upper dummy pipe
  = 200              (straight)
  = L + 200          (long-radius elbow)

Lower supporting pipe
  = H - 300

Plate F
  = side×side×t，2片
  = 4孔，孔徑 d、pitch W×W、邊距 35

Adjusting hardware
  = 4 adjustable bolts
  = 16 hex nuts
```

D-10A 的尺寸表已補齊 1.5"~50"，包括舊設定缺少的
22/24/26/30/34/38/40/42/46/48/50 吋 rows。

## 20E4588 Branch

20E4588 是另一種構造，不含 Plate F／四支 adjustable bolt：

```text
Upper dummy pipe
  = 100              (straight)
  = L + 100          (elbow)

Lower supporting pipe
  = H - 200

BASE WASHER
  = OD F / ID 95 / 12t annular plate

SPECIAL BASE PLATE
  = M-1 Rev.1 assembly
```

M-1 已保存下列加工／採購參數：

- 3" SCH40 A53-B galvanized straight-parallel threaded pipe，200L。
- thread major diameter 108、pipe OD 89。
- 3" 3000# A105 galvanized coupling，54 high，full female NPSM。
- Ø150×12t A283-C galvanized base plate。
- Ø10 half-hole drain/no-weld detail。

M-1 的 coupling/螺紋成品單重未由圖面提供，因此 assembly 重量暫不計入。

20E4588 的 D-10 主體圖列 B/C/H；依 M-43，B/H 會刪除 plate `a`，C 保留。
若使用同來源 M-42 標準已有定義、但 D-10 未列的型式，系統只會高風險暫算並
禁止正式 BOM／加工放行；來源 M-42 也未定義時仍停止。

H 上限採有限外插分級：差異不逾 100 mm 且不逾 10% 為一般警示，其餘在
2 倍／超額 2000 mm 護欄內為高風險，超出護欄仍停止。

## Fabrication Readiness

兩個來源都把 straight/elbow 畫成替代接法，但 designation 沒有 connection 欄。
系統提供 variation axis；未明確選擇時沿用 elbow 只為舊資料相容，
`bom_ready=false`。

整組仍不是 `fabrication_ready`：

- 上段 dummy pipe 與 straight/elbow 的 cope/fishmouth 沒有展開尺寸。
- 中威只標 Ø6 weep hole，沒有孔中心相對 Plate F 的定位尺寸。
- M-1 雖有加工幾何，供應件實重仍待供應商資料。
