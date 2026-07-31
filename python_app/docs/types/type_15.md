# Type 15 — 結構鋼立柱限位支撐（落於既有鋼構）

| 項目 | 內容 |
|------|------|
| 中文名稱 | 結構鋼立柱限位支撐（落於既有鋼構） |
| 英文名稱 | Heavy Duty Structural Sliding Support on Existing Steel |
| 圖號 | 三來源皆為 TYPE-15 / D-16 Rev.1 |
| 編碼 | `15-{A}-{LL}{HH}`；例 `15-2B-1005` = L 1000、H 500 mm |
| 狀態 | 三來源已分流；加工資料仍有圖面缺口 |

## 來源差異

| 來源 | 尺寸 | MEMBER N | 限制 |
|------|------|----------|------|
| 中威 E25-24 | 2–12 in | C Channel；10/12 in 為 Detail o 雙槽鐵 | 依 D-16 的 L/H 矩陣 |
| 中鼎 22A_5123A | 4–12 in | 單支 H Beam + I×J×T 補強板 | L≤1000；H≤3000/4000 |
| 中鼎 20E4588 | 4–12 in | 單支 H Beam + I×J×T 補強板 | L≤1000；H≤3000/4000 |

22A 與 20E4588 的 12 in 列並不相同：22A 的 F=16 mm，20E4588 的
F=19 mm。因此不能只用一份中鼎表。

L/H 超出上述 envelope 時不會無限制套公式：差異不逾 100 mm 且不逾 10%
為一般警示；其餘在上限 2 倍且超額不逾 2000 mm 內列高風險暫算；再超出即停止。

## 計算與加工資料

- L 是兩片 6t Stopper 的外側總長，MEMBER N 切長為 `L-2×6`。
- 中威 supporting pipe 切長為 `H-2F-MEMBER depth`。
- 中鼎 supporting pipe 另須扣除 I×J×T 補強板厚度：
  `H-2F-MEMBER depth-T`。
- Wing Plate 已依 Q、P、上緣 20、右下 25、左下 10C 建成六頂點 polygon；
  Stopper 依 M×K、四角 10C 建成八頂點 polygon，重量採淨面積。
- Base Plate 為 D square×F；Top Plate 為 B square×F。
- 中鼎另列一片 I×J×T reinforcement plate。

## 尚未完成的加工條件

- NOTE 3 指定 Wing Plate P 現場切割；未提供 `wing_plate_P_mm` 時只可估重。
- 三張 D-16 都沒有標 Ø6 weep-hole 中心離底板尺寸。
- 中威 10/12 in Detail o 未標雙槽鐵間距；單支切長可用，但組立圖仍缺定位。

因此有明確 P 時 BOM 可以完成，但整體 `fabrication_ready` 仍保持 false，
直到上述定位尺寸補齊。
