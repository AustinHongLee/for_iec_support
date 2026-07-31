# Type 08 — 來源別立柱式托架

| 項目 | 內容 |
|------|------|
| 圖號 | D-8 |
| 來源 | 中威 E25-24／中鼎 22A_5123A／中鼎 20E4588 |
| 狀態 | ⚠️ 來源別 recipe 已建立；加工圖仍有明示缺口 |

## 來源差異

| 來源 | Supporting Pipe A | L/H | M-42 | 上部構造 |
|------|-------------------|-----|------|----------|
| 中威 E25-24 | 2"/3"/4" | L≤1000、H≤1500 | G/J | 兩端 STOPPER；槽鐵切長 `L-12` |
| 中鼎 22A_5123A | 表列 3"/4" | 3": L≤500；4": L≤800；H 最高 2500 | G/R/T | 兩端 STOPPER；槽鐵切長 `L-12` |
| 中鼎 20E4588 Rev.1B | 表列 3"/4" | 同 22A 表列 | G/R/T | 可用 L1/L2 配置；槽鐵切長 `L`；修訂圖未再畫 STOPPER |

22A/20E4588 的 3" supporting pipe 若 `1500 < H ≤ 2500`，圖面 NOTE 4
另要求 supported line 必須是 2" 以下 single line。Type 編碼沒有 supported line
size，因此未提供該覆寫值時會保留警告與 fabrication blocker。

20E4588 的尺寸表仍保留 K/M 欄，但 Rev.1B 主視圖沒有兩端 STOPPER，也沒有
STOPPER detail。系統依可見構造不自動加入 STOPPER，並將 BOM 標成未完成確認，
避免把舊版構件直接推定為現版構件。

表內 M-42 欄是 D-8 主體圖的列舉；其他型式若同來源 M-42 標準確有定義，
只可高風險暫算。L/H 上限採有限外插分級，所有外插均禁止直接宣稱可出加工圖。

## 編碼

```text
中威／22A:
08-{supporting_pipe_size}B-{LL}{HH}{M42}

20E4588:
08-{supporting_pipe_size}B-{LL}{HH}{M42}[-{L1}{L2}]
```

尺寸碼單位為 100 mm。20E4588 若省略第四段，預設 `L1=L2=L/2`；若提供，
必須滿足 `L1+L2=L`。

## 計算與下料

```text
Supporting Pipe A cut
  = H - TOP PLATE 6t - MEMBER N depth/2 - M42 plate thickness

MEMBER N cut
  = L - 2×6  (中威／22A，L 為 STOPPER 外緣總長)
  = L        (20E4588 Rev.1B)

STOPPER
  = K × M × 6t，2片，4-C10  (僅中威／22A)

TOP PLATE
  = B × B × 6t
```

STOPPER 重量已按四角 10C 的淨面積計算，不再用 K×M 毛矩形估重。

## 加工圖資料狀態

已結構化輸出：

- `D8-SUPPORTING-PIPE-A`：管徑、schedule、切長、上下焊接、weep hole 直徑。
- `D8-MEMBER-N`：型鋼規格、來源別切長公式、支撐軸位置、L1/L2。
- `D8-STOPPER`：K/M/6t、4-C10、數量與端部位置。
- `D8-TOP-PLATE-B`：B×B×6t、中心位置與焊接。
- M-42 板件／扣件：沿用來源別 M-42/M-43 profile。

尚未達整組 `fabrication_ready` 的原因：

- 三張 D-8 都只示意 `Ø6 weep hole` 位於立管低點，沒有孔中心離底板尺寸。
- 20E4588 Rev.1B 的 STOPPER 是否刪除與 K/M 欄殘留互相矛盾，需工程師核定。
- 22A/20E4588 的 3" 高支架條件需要額外 supported line size。
