# Type 19 — Relief Valve Lateral Brace

目前只有中威 E25-24 的 D-21 Rev.1；22A_5123A 與 20E4588 沒有
Type 19，因此不能套用中威規則。

## 編碼與尺寸

```text
19-{A}B
```

適用 supported line size 1–12 in。designation 不含 L；D-21 NOTE 1 明定
L 必須在現場切割。系統只接受 `member_cut_length_mm` 作為實際下料，
表列 600/1200 mm 保留為 drawing reference，不再直接計重。

## MEMBER M

- 1/1.5 in：L40×40×5 angle。
- 2/3 in：L50×50×6 angle。
- 4/6 in：L75×75×9 angle。
- 8/10/12 in：A-A 視圖是從 H194×150×6×9 縱向剖分得到的 T-section，
  不是整支 H Beam。重量基準為 parent H section 30.6 kg/m 的一半，
  即 15.3 kg/m。

斜率為 1:1（45°），焊腳 6 mm、兩側焊。L-angle 下端依 Detail Z 有
20C pocket-drain cut。

## 加工圖狀態

提供 `member_cut_length_mm` 後 BOM 可以完成，但 D-21 沒有尺寸化上下端
貼管 cope。L-angle 的 20C arc/切線與 H194 剖分的 kerf/圓角也未完整標示，
所以 `fabrication_ready` 維持 false。
