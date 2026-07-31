# Cold-component 第一階段原圖複驗與 Type 接回

日期：2026-07-30

## 範圍

依 37 個 cold Type 的 reference/blocker 次數排序後，第一批選擇：

- `N-9`：9 個 Type 直接引用。
- `N-10`：N-9 的尺寸表，必須與 N-9 一起完成。
- `N-12/N-12A`：合計影響 15 個 Type，並控制 vessel clip A/plate thickness。
- `N-28`：10 個 Type 引用的 white-oak block。
- `N-27`：5 個 deep-cold stanchion 引用的 polyurethane block。

六張 PDF 均以 180 dpi 重新渲染並逐圖檢查，不只使用文字抽取。

## 成熟度判定

| Component | 本輪結果 | Weight ready | Fabrication 結論 |
|---|---|---:|---|
| N-9 | A/B/C/D/E/F/G/H/J/K/R/S arrangement 與 Note 1 | 否 | 可選正確 arrangement；材料與 host interface 仍阻擋 |
| N-10 | Supporting pipe 1-1/2~12 吋的 B/C/D/E/F/G/H/J/K 表 | 否 | Plate a/b/d/e 尺寸與孔位可查 |
| N-12 | Clip Type 1/2 固定尺寸與孔位 | 否 | A/t 可查；vessel radius、C/G、材質與 placement 仍阻擋 |
| N-12A | Note 2 insulation table 與 Clip Type 3 固定尺寸 | 否 | A/t 可查；D/G/C、材質與 working point 仍阻擋 |
| N-27 | PUBK-1~6、PUBK-2U~6U 完整表 | 是 | 尺寸、孔位、密度齊全，可加工且可精算 |
| N-28 | WOOD-1~4 尺寸、孔位與 WHITE OAK | 否 | WOOD-3/4 cut geometry 完整；WOOD-1/2 10 mm chamfer extent 仍需確認 |

`lookup-ready` 不等於 `weight-ready`。本輪只有 N-27 的來源圖明示
`320 KG/M³ POLYURETHANE BLOCK`，因此只有 N-27 可以安全從零重量 reference
升級為實際重量。

## N-27 精算

一般 PUBK row 使用：

`net volume = L1 × W1 × T1 - N × π × (D/2)² × T1`

U row 無鑽孔，使用：

`net volume = L1 × W1 × T1`

再乘來源密度 320 kg/m³。孔中心也以 L3/W2/W3 轉成具名座標，供後續 CAD
直接使用。

## N-9/N-10 下部組件

N-10 的 plate 對應已結構化：

- Plate a：`B × B × Kt`。
- Plate b：`C × C × Kt`，4-ØH，pitch `D × D`，expansion bolt J。
- Plate d：`E × E × Kt`，4-ØH，pitch `F × F`，expansion bolt J。
- Plate e：`G × G × Kt`。
- Type E/F/K/S 依 N-9 保留 `L40×40×5×150 LG` angle arrangement。

N-9 Note 1 也已實作：host Type 03C/04C/09C/10C 使用 lower Type B/H
時刪除 Plate a。

本輪接回的 Type 06C~10C 同時鎖定來源允許的 lower component：

- 06C：N-9 全組 A/B/C/D/E/F/G/H/J/K/R/S。
- 07C：只接受 G/J/R。
- 08C：只接受 E/F/G/J/K/R/S。
- 09C、10C：只接受 B/H。

## N-12/N-12A 與 N-28

N-12A Note 2 的邊界照圖保存：

| Insulation thickness | Plate t | A |
|---:|---:|---:|
| <=140 mm | 9 mm | 100 mm |
| 141~215 mm | 9 mm | 180 mm |
| 216~300 mm | 12 mm | 260 mm |

Type 109C/110C 的 B 公式包含 line OD 與 insulation，因此可從 designation
反算 insulation，再自動選 A/t。Type 112C/113C/117C 的 designation 不足以
反算 insulation；提供 row override `insulation_thickness_mm` 時才完成 lookup，
未提供時保留明確 blocker。

接回結果：

- 109C：Clip Type 3、WOOD-2/3/4。
- 110C：Clip Type 2、WOOD-1。
- 112C：Clip Type 3、WOOD-2/3/4。
- 113C：Clip Type 1、WOOD-1。
- 117C：Clip Type 1、WOOD-1。

N-28 只明示 WHITE OAK，未給密度，因此木塊維持零重量。WOOD-1/2 的 10 mm
chamfer 在兩個視圖出現，但 edge extent/multiplicity 不夠明確，未假設成完整
三維倒角；WOOD-3/4 則已標為 cut-geometry ready。

## 驗證

- 第一批 N-series tables 從 metadata-only 升級 6 個。
- Component registry：28 lookup-ready、3 partial-lookup、40 metadata-only。
- Cold Type/component 專屬測試：96 passed。
- 全庫 `pytest -q`：664 passed。
- `python validate_tables.py`：`VALIDATION COMPLETE`。
- 既有 `phase 2L-A` soft warnings：40，未增加。

## 下一批

下一階段依共用次數與互相依賴，處理 cradle／insulation 群：

`N-1, N-2, N-3, N-5, N-20, N-23`

這一批主要影響 Type 11C~18C、22C、119C、121C。仍採同一政策：先完成原圖
table/geometry，再由 host Type 明確選 row；缺密度、成品單重、接觸輪廓或施工
界面時維持 blocker。
