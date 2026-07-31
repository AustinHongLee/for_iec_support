# Type 09 — 來源別可調式 Dummy-Leg

| 項目 | 內容 |
|------|------|
| 圖號 | D-9 |
| 來源 | 中威 E25-24／中鼎 22A_5123A／中鼎 20E4588 |
| Supported line | 2"~4" |
| 狀態 | ⚠️ BOM/下料已來源化；上端相貫輪廓未完成 |

## 來源差異

| 來源 | H | M-42 | 調整螺栓 |
|------|---|------|----------|
| 中威 | `H≤1500` | B/H | 1-5/8"×150L full threaded |
| 中鼎 22A | `300≤H≤1800` | B/C/H/R | 1-3/4"×150L full threaded |
| 中鼎 20E4588 | `H≤1500` | B/C/H | M42×150L full threaded |

H 下限仍是硬條件，上限採有限外插分級。表列 M-42 是 D-9 主體圖型式；
同來源 M-42 標準已有、但 D-9 未列的型式只可高風險暫算。

各來源均使用 2" SCH.40 supporting pipe、A307-B galvanized adjusting bolt
及兩顆 heavy hex nuts。D-9 沒有提供螺帽單重，因此螺帽重量不列；螺栓重量只以
nominal solid-cylinder blank 概算，採購實重仍需供應商確認。

## Connection 必須另外選

Type 編碼不包含上端接在直管或 long-radius elbow。系統提供：

```text
connection = straight → 上段特殊材 dummy leg 切長 100
connection = elbow    → 上段特殊材 dummy leg 切長 L + 100
```

若未明確選擇，為相容舊資料會暫用 elbow，但 `bom_ready=false`，不可把這個預設
當成加工圖依據。

## 正確的垂直下料鏈

D-9 圖上有兩個各 100 mm 的區段：

1. 主管／彎頭到上下材質接縫的特殊材尾段 100 mm。
2. resting surface 到 supporting pipe 底端的調整空間 100 mm。

因此：

```text
Upper dummy leg = 100 或 L+100
Lower 2" SCH40 supporting pipe = H - 100 - 100 = H-200
```

舊程式的 `H-100` 少扣了底部調整空間，會使下段管多 100 mm，已修正。

## Type 09 專用 M-43 規則

一般 M-42 recipe 不能原樣套用。M-43 明確要求 Type 09 刪除部分 plate `a`：

- 中威：B/H 刪除 plate `a`。
- 22A：B/C/H 刪除 plate `a`；R 仍保留圖示構件。
- 20E4588：B/H 刪除 plate `a`；C 保留 150×150×9 plate `a`，並依 D-9
  detail 焊在 embedded plate/free surface。

例如 Type B 會保留 plate `d` 與其來源別扣件，但刪除直接位於 dummy leg 下的
plate `a`；Type H 刪除 plate `a` 後沒有另列 civil foundation。

## 加工圖資料

已輸出：

- `D9-UPPER-DUMMY-LEG`：2" SCH40、材質同主管、connection、L、切長與 6 mm weld。
- `D9-LOWER-SUPPORTING-PIPE`：A53 Gr.B、`H-200` 切長、方切端與底部螺帽焊接。
- `D9-ADJUSTING-BOLT`：來源別直徑、150L、full thread、A307-B galvanized。
- `D9-HEAVY-HEX-NUT`：來源別規格、2 EA，其中一顆焊至 dummy leg。
- M-42 plate/fastener：依來源與 Type 09 專用 plate-a omission。

尚未達整組 `fabrication_ready`：D-9 只畫出上段 dummy leg 與直管／彎頭的相貫
接合，沒有足以展開 cope/fishmouth 的輪廓尺寸。
