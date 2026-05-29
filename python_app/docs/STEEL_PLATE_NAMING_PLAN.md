# 鋼板類命名標準化計畫

> 目標：所有 `category="鋼板類"` 的 `AnalysisEntry.name` 遵循一套命名規則，讓 BOM、採購、CAD 分配三端都讀得懂。

---

## 一、目標命名規則

```
{type_id}_{source_role}_{shape_spec}

type_id     — 所屬 Type 編號（如 07、59、M42）
source_role — M42 共用件用 m42_{a|b|c|d|e}，自有件用 ComponentRole（如 lug_plate、stopper_plate）
shape_spec  — 放樣尺寸字串（四方板 AxBxt，異形板 AxBxCxDxt）
```

### 範例

| 分類 | 最終 name |
|------|----------|
| M42 底板 a 型 | `M42_a_200x200x9` |
| M42 底板 b 型（有鑽孔） | `M42_b_250x250x12` |
| Type 07 滑動板 | `07_generic_plate_300x200x9t` |
| Type 08 止擋板 | `08_stopper_plate_100x100x6t` |
| Type 14 翼板 | `14_wing_plate_150x80x6t` |
| Type 59 角板（L型切口） | `59_lug_plate_150x130x25x50x12t` |
| Type 62 LUG PLATE TYPE-B | `62_lug_plate_B_200x120x12t` |
| Type 76 弧形補強板 | `76_reinforcement_pad_400x180x12t` |

---

## 二、現狀盤點

### 2.1 核心函式 `plate.py::add_plate_entry`

| 現狀 | 說明 |
|------|------|
| `plate_name` 由呼叫方傳入 | 各 type 各行其是 |
| `shape_spec` 參數已加入 | ✅ 異形板放樣資訊可傳入 `GeometryHints` |
| `entry.name = plate_name` | 直接寫入，無加工 |

### 2.2 各來源檔案現有名稱一覽

#### A. M42 底板 (`m42.py`)

```python
# 現有
plate_name = f"Plate_{plate_type}" + ("_有鑽孔" if require_drilling else "_無鑽孔")
# → "Plate_a_無鑽孔", "Plate_b_有鑽孔" ...
```

| 板型 | 現有名稱 | 目標名稱 |
|------|---------|---------|
| a | `Plate_a_無鑽孔` | `M42_a_{size}x{size}x{t}` |
| b | `Plate_b_有鑽孔` | `M42_b_{size}x{size}x{t}` |
| c | `Plate_c_有鑽孔` | `M42_c_{size}x{size}x{t}` |
| d | `Plate_d_有鑽孔` | `M42_d_{size}x{size}x{t}` |
| e | `Plate_e_無鑽孔` | `M42_e_{size}x{size}x{t}` |

#### B. Type 計算器直接呼叫 `add_plate_entry`

| Type | 現有名稱 | 建議名稱 | role |
|------|---------|---------|------|
| 07 | `Plate_E` | `07_generic_plate_{A}x{B}x{t}t` | generic_plate |
| 07 | `Plate_F` | `07_generic_plate_{A}x{B}x{t}t` | generic_plate |
| 08 | `Plate_STOPPER` | `08_stopper_plate_{A}x{B}x{t}t` | stopper_plate |
| 08 | `Plate_TOP` | `08_top_plate_{A}x{A}x6t` | top_plate |
| 10 | `Plate_F` | `10_generic_plate_{A}x{B}x{t}t` | generic_plate |
| 12 | `Plate_P` | `12_cover_plate_{A}x{B}x{t}t` | cover_plate |
| 12 | `COVER_PL` | `12_cover_plate_{A}x{B}x{t}t` | cover_plate |
| 13 | `Plate_P` | `13_cover_plate_{A}x{B}x{t}t` | cover_plate |
| 13 | `COVER_PL` | `13_cover_plate_{A}x{B}x{t}t` | cover_plate |
| 14 | `Plate_WING` | `14_wing_plate_{A}x{B}x{t}t` | wing_plate |
| 14 | `Plate_STOPPER` | `14_stopper_plate_{A}x{B}x{t}t` | stopper_plate |
| 14 | `Plate_BASE` | `14_base_plate_{A}x{B}x{t}t` | base_plate |
| 14 | `Plate_TOP` | `14_top_plate_{A}x{B}x{t}t` | top_plate |
| 15 | `Plate_WING` | `15_wing_plate_{A}x{B}x{t}t` | wing_plate |
| 15 | `Plate_STOPPER` | `15_stopper_plate_{A}x{B}x{t}t` | stopper_plate |
| 15 | `Plate_BASE` | `15_base_plate_{A}x{B}x{t}t` | base_plate |
| 15 | `Plate_TOP` | `15_top_plate_{A}x{B}x{t}t` | top_plate |
| 16 | `Plate` | `16_generic_plate_{A}x{A}x6t` | generic_plate |
| 25 | `LUG_PLATE_C` | `25_lug_plate_{A}x{B}x{t}t` | lug_plate |
| 26 | `LUG_PLATE_C` | `26_lug_plate_{A}x{B}x{t}t` | lug_plate |
| 27 | `Plate_6t_Side` | `27_side_plate_{A}x{B}x6t` | side_plate |
| 27 | `Plate_9t_Wing` | `27_wing_plate_{A}x{B}x9t` | wing_plate |
| 36 | `LUG PLATE TYPE-C` | `36_lug_plate_{A}x{B}x{t}t` | lug_plate |
| 39 | `LUG PLATE TYPE-C` | `39_lug_plate_{A}x{B}x{t}t` | lug_plate |
| 39 | `LUG PLATE TYPE-D`/`TYPE-E` | `39_lug_plate_{D|E}_{A}x{B}x{t}t` | lug_plate |
| 41 | `BASE PLATE` | `41_base_plate_{A}x{A}x{t}t` | base_plate |
| 43 | `LUG PLATE TYPE-C` | `43_lug_plate_{A}x{B}x{t}t` | lug_plate |
| 43 | `LUG PLATE TYPE-D`/`TYPE-E` | `43_lug_plate_{D|E}_{A}x{B}x{t}t` | lug_plate |
| 44 | `PLATE` | `44_generic_plate_90x45x6t` | generic_plate |
| 45 | `LUG PLATE TYPE-C` | `45_lug_plate_{A}x{B}x{t}t` | lug_plate |
| 45 | `LUG PLATE TYPE-D`/`TYPE-E` | `45_lug_plate_{D|E}_{A}x{B}x{t}t` | lug_plate |
| 46 | `PLATE` | `46_generic_plate_90x45x6t` | generic_plate |
| 47 | `LUG PLATE TYPE-C` | `47_lug_plate_{A}x{B}x{t}t` | lug_plate |
| 47 | `LUG PLATE TYPE-D`/`TYPE-E` | `47_lug_plate_{D|E}_{A}x{B}x{t}t` | lug_plate |
| 51 | `FLAT BAR` | `51_flat_bar_{H}x50x9t` | flat_bar |
| 56 | `PLATE` | `56_generic_plate_{A}x{B}x{t}t` | generic_plate |
| 56 | `MEMBER C` | `56_member_c_{A}x{B}x{t}t` | channel |
| 56 | `SIDE PLATE` | `56_side_plate_{A}x{B}x{t}t` | side_plate |
| 56 | `SADDLE (120°)` | `56_saddle_plate_{A}x{B}x{t}t` | saddle_plate |
| 59 | `LUG PLATE` | `59_lug_plate_{A}x{B}x25x{C}x{t}t` ✅ 已完成 | lug_plate |
| 61 | `REIN. PAD` | `61_reinforcement_pad_{A}x{A}x12t` | reinforcement_pad |
| 80 | `REINFORCING_PAD` | `80_reinforcement_pad_400x{W}x12t` | reinforcement_pad |
| 80 | `SADDLE_SIDE_PLATE` | `80_saddle_side_{L}x{H}x16t` | side_plate |
| 80 | `SADDLE_FOOT_PLATE` | `80_saddle_foot_{L}x{W}x16t` | generic_plate |
| 80 | `SADDLE_ARC_PLATE` | `80_saddle_arc_{L}x{b}x16t` | saddle_plate |
| 80 | `STIFFENER_PLATE` | `80_stiffener_{A}x{B}x12t` | generic_plate |
| — | `C/S SHIM` (trunnion) | `{type}_shim_plate_{A}x{B}x{t}t` | shim_plate |

#### C. Pipe Shoe Engine (`pipe_shoe_engine.py`，覆蓋 Type 52/53/54/55/66/67)

這些 plate name 由 JSON config 的 `name` 欄位決定（來自 `type_52.json` ~ `type_67.json`），不經 Python code 寫死。需要檢查各 JSON 內的 name 值。

#### D. 直接設 `category="鋼板類"` 但不經 `add_plate_entry` 的項目

| Type | 現有名稱 | 出處 |
|------|---------|------|
| 51 | `FLAT BAR` / `SIDE PLATE` | `type_51.py:101` |
| 62 | `LUG PLATE TYPE-B` | `type_62.py:342` |
| 72 | `STRAP` | `type_72.py:48` |
| 73 | `STRAP`, `WASHER`, `GUSSET` | `type_73.py:57,111` |
| 76 | `REINFORCING PAD` | `type_76.py:45` |
| 77 | `SADDLE` | `type_77.py:51` |
| 78 | `STRAP` | `type_78.py:48` |

> 建議：這些最終也統一經 `add_plate_entry` 產出，避免 name 格式不一致。

---

## 三、關鍵決策

### 3.1 M42 底板：不用 Type 前綴

```
✅ M42_a_200x200x9
❌ 07_M42_a_200x200x9
```

理由：
- M42 底板是標準共用件，同一尺寸被多個 Type 引用
- `name` 負責去重 → 不掛 Type 才能自動聚合為一行採購
- CAD 分配時由匯出層動態拼接 Type 前綴（`f"{type_id}_{entry.name}"`）

### 3.2 自有件：一律掛 Type 前綴

```
✅ 07_sliding_plate_300x200x9t
```

理由：
- 自有件不會跨 Type 共用，掛 Type 不影響去重
- CAD 師傅一看就知道歸屬哪張圖

### 3.3 四方板 vs 異形板：shape_spec 區分

```python
# 四方板
plate_name = f"{type_id}_{role}_{A}x{B}x{t}t"

# 異形板（L 型 Lug Plate）
plate_name = f"{type_id}_{role}_{A}x{B}x{C}x{D}x{t}t"
shape_spec  = f"{A}x{B}x{C}x{D}x{t}t"    # 進 GeometryHints
```

重量永遠用 A×B 外框矩形算（不變），`shape_spec` 只影響放樣尺寸的溝通。

### 3.4 去重相容性

目前 `material_summary.py` 的 plate 去重 key：
```python
key = (entry.name, entry.material,
       round(entry.length, 1), round(entry.width, 1), entry.spec)
```

- M42：name 不含 Type → 同板跨 Type 自動聚合 ✅
- 自有件：name 含 Type → 不會誤聚合（因為跨 Type 同名但不同 Type 是正常的不同板）✅
- shape_spec 不參與 key → 異形板的外框尺寸相同時仍會聚合 ✅

---

## 四、實施步驟

### Step 1：改 `plate.py` 核心（1 個檔案）

在 `add_plate_entry` 內提供 name 生成輔助函式，呼叫方可選用：

```python
def build_plate_name(type_id: str, role: str, plate_a: float, plate_b: float,
                     thickness: float, *, extra_dims: str = "") -> str:
    """產生標準化 plate name"""
    dims = f"{_fmt(plate_a)}x{_fmt(plate_b)}x{_fmt(thickness)}t"
    if extra_dims:
        dims = extra_dims  # 異形板直接用完整 shape_spec
    return f"{type_id}_{role}_{dims}"
```

### Step 2：改 `m42.py`（1 個檔案）

```python
# 舊
plate_name = f"Plate_{plate_type}" + ("_有鑽孔" if require_drilling else "_無鑽孔")
# 新
plate_name = f"M42_{plate_type}_{fmt(plate_size)}x{fmt(plate_size)}x{fmt(plate_thickness)}t"
```

### Step 3：改各 Type 計算器（約 20 個檔案）

逐一改 `add_plate_entry` 的 `plate_name` 參數，從 legacy name 改為結構化 name。

### Step 4：處理直接設 category 的項目（約 7 個檔案）

將 `category="鋼板類"` 的直接賦值改為走 `add_plate_entry`，或至少統一名稱格式。

### Step 5：驗證

- 跑 `pytest` 確保去重不壞
- 檢查所有 plate name 符合 `{type_id}_{role}_{shape_spec}` 模式
- 抽查 BOM 輸出比對舊版

---

## 五、預期收穫

| 面向 | 改善前 | 改善後 |
|------|--------|--------|
| **BOM 可讀性** | `Plate_a_有鑽孔` → 不知道多大 | `M42_a_200x200x9t` → 一眼看懂 |
| **CAD 分配** | `Plate_E` → 問人才知道哪張圖 | `07_generic_plate_300x200x9t` → 直接開 Type 07 PDF |
| **M42 去重** | 已有 name+(l,w,t) 做 key → 聚合 OK | 不變，維持正確聚合 |
| **異形板放樣** | C、D 尺寸被吃掉 | `shape_spec` 保存完整放樣資訊 |
| **跨 Type 搜尋** | 搜 `LUG PLATE` 出來一堆不分來源 | 搜 `59_lug_plate_*` vs `39_lug_plate_*` 立刻區分 |
| **程式可解析性** | 無規則，只能當純文字 | `name.split("_")[0]` = type_id, `[1]` = role |

---

## 六、風險與注意事項

1. **測試覆蓋**：現有 `validate_tables.py` 和 `test_*.py` 有比對舊 name 的 assertion，需先更新
2. **Pipe Shoe JSON configs**：Type 52~67 的 name 在 JSON 裡，不在 Python 裡，需另外處理
3. **匯出層**：Excel/CSV/PDF 匯出目前直接印 `entry.name`，改名後自動生效，不需要額外修改
4. **向後相容**：若有外部系統依賴舊 name，需評估影響範圍

---

*文件建立：2026-05-29 | 狀態：計畫階段 | 作者：Deep Code*

---

## 七、Claude 補充建議（2026-05-29）

> 以下為 Claude 對本計畫的審閱意見，標記用途：方便日後辨識哪些是初稿、哪些是 review 後追加。決定是否採納由人類確認。

### 7.1 〔Claude 意見〕缺失欄位：影響追溯性

目前 name 只含「歸屬 + 角色 + 尺寸」，CAD/PDM/採購會反問的三件事缺位：

**(a) 材質代號** — Inventor BOM、採購單第一個會問。建議加在 shape 後面：

```
07_lug_plate_300x200x9t_SS400
```

材質用 enum 白名單（SS400 / A36 / S275JR / SUS304…），機器端可驗證、避免手滑拼錯。

**(b) 版次（Rev）** — 板子改尺寸或鑽孔位置時，舊圖在用、新圖已改，BOM 不能混。建議結尾加 `_rA`、`_rB`：

```
07_lug_plate_300x200x9t_SS400_rA
```

首次發行就標 `_rA`，免得日後找不到 rev0 是哪一版。

**(c) 專案/案號（可選但強烈建議）** — 跨案追溯用。若工具會長期跨多專案，留前綴位置：

```
{project}-{type_id}_{role}_{shape}_{mat}_{rev}
例：IEC26-07_lug_plate_300x200x9t_SS400_rA
```

用 `-` 隔開專案、`_` 隔開內部欄位，正則可一刀切。

### 7.2 〔Claude 意見〕一致性問題（現在就會踩雷）

**(a) `t` 後綴前後不一致**

- M42 範例：`M42_a_200x200x9`（無 `t`）
- 其他範例：`07_generic_plate_300x200x9t`（有 `t`）

建議統一「一律帶 `t`」。理由：`9` 可能被誤讀為長度，`9t` 明確是厚度。

**(b) 異形板 shape_spec 維度順序需寫死規格**

`59_lug_plate_150x130x25x50x12t` 的 5 個數字對應 L 型板的哪幾條邊？文件只說 A×B×C×D×t，但 A/B/C/D 在 L 型 / 梯形 / 弧形板上的對應邊長需要標註圖。建議在 `docs/` 補一張各 role 的 shape 標註示意圖（PNG 或 mermaid）。

**(c) role 命名要建白名單**

目前表格出現 `generic_plate / stopper_plate / lug_plate / wing_plate / base_plate / top_plate / cover_plate / side_plate / saddle_plate / reinforcement_pad / shim_plate / flat_bar / channel / member_c`。建議在 `plate.py` 定：

```python
from enum import Enum

class PlateRole(str, Enum):
    GENERIC_PLATE = "generic_plate"
    LUG_PLATE = "lug_plate"
    WING_PLATE = "wing_plate"
    # ...
```

避免日後手滑打成 `lugplate` 或 `lug-plate`，破壞去重 key。

### 7.3 〔Claude 意見〕CAD / Inventor 端銜接

**(a) 檔名 = Part Number = entry.name 三者統一**

讓 Inventor 的 `iProperty.PartNumber` 直接吃 `entry.name`，不要再轉一手。`.ipt` / `.dwg` 檔名也用同一個字串。三邊永遠一致，BOM 對得起來。

**(b) 避免特殊字元**

- 安全：`_` `x` `-` `0-9` `A-Z` `a-z`
- 禁用（Windows 檔名 / Inventor PartNumber）：`< > : " / \ | ? *`
- 禁用（CSV / BOM 解析會炸）：`,` `;`

目前新格式都 OK，但 §二 D 區直接賦值的舊名要特別清掉：
- `LUG PLATE TYPE-B`（空格）
- `SADDLE (120°)`（括號、度數符號）
- `LUG_PLATE_C`（雖然安全但要改成 lowercase 一致風格）

**(c) 建議加 Stock Number / Hash 欄位**

給每個唯一規格算一個短 hash（MD5/SHA1 前 6 碼），存在 `AnalysisEntry.stock_number`。CAD 端用這個做交叉引用比解析字串穩、不怕 rename：

```
07_lug_plate_300x200x9t_SS400_rA  →  stock = PL-3F9A2B
```

對 Inventor 來說，stock_number 還能塞進 `iProperty.StockNumber`，做為跨檔案的穩定 ID。

### 7.4 〔Claude 意見〕落地步驟順序建議調整

§四的 Step 1~5 順序建議把「測試 fixture」提到最前面：

1. **先寫對照表 fixture**：建一份 `tests/fixtures/plate_name_migration.json`，包含 `{舊 name → 新 name}` 的完整映射
2. **跑驗證舊 name 還在**（baseline）
3. 改 `plate.py` 加 `build_plate_name()` 輔助函式
4. 改 `m42.py` → 跑測試比對 fixture
5. 逐 type 改 → 每改一個跑一次測試
6. 改完切換 fixture，用新 name 做為 ground truth
7. 處理 D 區直接賦值項
8. Pipe Shoe JSON configs（Type 52~67）

這樣每改一個 type 都能立刻知道有沒有破壞 BOM 去重。

### 7.5 〔Claude 意見〕最終建議格式

```
{type_id}_{role}_{shape_spec}_{material}_r{rev}

範例：
M42_a_200x200x9t_SS400_rA              ← 共用件，無 type 前綴
07_lug_plate_300x200x9t_SS400_rA       ← 自有件、四方板
59_lug_plate_150x130x25x50x12t_SS400_rA ← 自有件、異形板
```

對應正則：

```python
PLATE_NAME_RE = re.compile(
    r"^(M42|\d{2,3})"        # type_id
    r"_([a-z][a-z0-9_]*?)"   # role
    r"_([\dx]+t)"            # shape_spec
    r"_([A-Z0-9]+)"          # material
    r"_r([A-Z])$"            # rev
)
```

### 7.6 〔Claude 意見〕風險補充

§六之外，再補三點：

1. **Rev 演進策略需先定義**：是「每次改尺寸就 +1」還是「對外發圖才 +1」？建議後者，避免內部 WIP 把 rev 跑掉
2. **Stock number 衝突處理**：6 碼 hash 約 1600 萬組合，跨專案累積可能撞到。撞到時是 fail-fast 還是自動加長到 8 碼？要先想好
3. **匯出層的欄位拆分**：BOM Excel 建議拆成 `[Type | Role | A | B | C | D | t | Material | Rev | Name | Stock#]` 多欄，而不是只印一個長 name。長 name 留作 PartNumber，多欄方便排序/篩選/Pivot

---

*Claude 補充：2026-05-29 | 用途：review 意見，待人類確認採納*

---

## 八、Deep Code 審閱意見（2026-05-29）

> 以下是 Deep Code 對 Claude 建議的回應與取捨判斷。

### 8.1 對 7.1(a) 材質代號 — ❌ 不建議放進 name

```
同意：BOM / 採購需要材質
不同意：材質應該放進 name
```

理由：
- `entry.material` 已經是獨立欄位，BOM 匯出時自然會帶
- 材質放進 name 會破壞 M42 去重：同尺寸 `M42_a_200x200x9t` 若材質不同（CS vs SUS304），現有 dedup key 會把它們分開 → 這反而是正確行為。但加了材質進 name 後，語意上變成「兩個不同零件」，實際上它們是同一個板型。
- 材質變更不應觸發 name 改變（name = 識別碼，material = 屬性）

```
✅ M42_a_200x200x9t
❌ M42_a_200x200x9t_SS400
```

---

### 8.2 對 7.1(b) Rev 版次 — ⚠️ 方向對，時機不對

Rev 是 PDM 層的事，不是計算引擎的事。BOM 產出時還沒有發圖，rev 只能是 `_rA`（空的）。建議：

- 現階段 **不加 rev**
- 未來 CAD/PDM 端接到 name 後，自己加後綴：`07_lug_plate_300x200x9t` → 存成 `07_lug_plate_300x200x9t_rA.ipt`
- 引擎端保持單純：算尺寸、給名字，不管理版次

---

### 8.3 對 7.1(c) 專案前綴 — ❌ 不建議

```
❌ IEC26-07_lug_plate_300x200x9t
```

理由：同一塊板跨專案本來就是同一塊板。專案資訊應由匯出層的「來源編碼」欄位攜帶（`material_summary.py` 第 88 行的 `source_fullstrings` 已經在做了）。

---

### 8.4 對 7.2(a) `t` 後綴不一致 — ✅ 同意，一律加 `t`

M42 範例目前寫 `200x200x9`，應改為 `200x200x9t`，與其他範例一致。

---

### 8.5 對 7.2(b) Shape 標註圖 — ✅ 同意，但先不急

異形板（L 型 Lug Plate、弧形鞍板…）的尺寸標註確實需要一張圖。建議先完成改名，再補 `docs/plate_shape_reference.md`。

[! 6 碼 hash 跨專案碰撞機率極低（1600 萬），撞到時改 8 碼即可，不需預設機制]

---

### 8.6 對 7.2(c) Role 白名單 — ✅ 同意，但已有 ComponentRole

`component_roles.py` 已經定義了 `ComponentRole` enum。只需要：
1. 確保 `plate.py::add_plate_entry` 的 `plate_role` 參數接受 `ComponentRole` 型別（目前是 `str`）
2. 在 `build_plate_name()` 內直接從 enum 取 `.value`

不需要另建 `PlateRole` enum，避免兩套體系互相翻譯。

---

### 8.7 對 7.3(a)(b) CAD 銜接 / 特殊字元 — ✅ 完全同意

- name = PartNumber = 檔名 → 鐵律，不轉手
- 禁用字元清單直接寫進 `build_plate_name()` 做 assertion，發現就炸

---

### 8.8 對 7.3(c) Stock Number / Hash — ⚠️ 有用，但先不要

好處是真的有（跨檔穩定 ID、不怕 rename），但：
- 這是「加分項」，不是「先決條件」
- 現有 dedup key 已經夠穩
- 先把名字統一了，再加 hash 欄位不遲
- 真要加的話，hash 應該基於 `(type_id, role, length, width, spec, material)` 而非 name 字串，這樣 name 改名後 hash 不變

---

### 8.9 對 7.4 落地步驟順序 — ✅ 同意 fixture 先行

原有 Step 1~5 順序調整為：

```
Step 0: 建 fixture 對照表 (plate_name_migration.json)
Step 1: 跑 baseline 測試（確認舊 name 現狀）
Step 2: 改 plate.py（build_plate_name 輔助函式）
Step 3: 改 m42.py → 跑測試
Step 4: 逐 type 改 → 每改一個跑測試
Step 5: 切換 fixture 為新 name ground truth
Step 6: 處理 D 區直接賦值項
Step 7: Pipe Shoe JSON configs
```

---

### 8.10 對 7.5 最終建議格式 — ⚠️ 部分採納

Claude 建議：
```
{type_id}_{role}_{shape_spec}_{material}_r{rev}
```

我的建議（化簡版）：
```
{type_id}_{role}_{shape_spec}
```

| 欄位 | Claude | 我 | 理由 |
|------|--------|-----|------|
| type_id | ✅ | ✅ | |
| role | ✅ | ✅ | |
| shape_spec | ✅ | ✅ | 加 `t` 後綴 |
| material | ✅ | ❌ | 獨立欄位，不進 name |
| rev | ✅ | ❌ | PDM 層的事 |

最終落地格式：
```
M42_a_200x200x9t
07_lug_plate_300x200x9t
59_lug_plate_150x130x25x50x12t
```

---

### 8.11 額外意見：7.6 風險補充的回應

1. **Rev 演進** — 同意「對外發圖才 +1」。引擎不碰 rev。
2. **Hash 碰撞** — 同意風險低，真撞到改 8 碼即可。
3. **BOM 多欄拆分** — ✅ 強烈同意。匯出層應拆 `[Type | Role | A | B | t | Material | Name]`，但這是 Step 5+ 的事，不影響改名計畫本身。

---

*Deep Code 審閱：2026-05-29 | 用途：對 Claude 建議的取捨判斷，標記為 Deep Code 意見*

---

## 九、Grok 審閱意見（2026-06-03）

> 以下為 Grok 對本計畫的審閱意見，標記用途：方便日後辨識哪些是初稿、review 意見、與後續實務調整。**本節所有內容均為 Grok 想法**，與 Claude / Deep Code 意見獨立。

### 9.1 整體評價

現有計畫方向**大致正確**，特別是：
- M42 共用件不掛 Type 前綴的決策非常關鍵（正確保護了 BOM 去重邏輯）。
- `ComponentRole` enum 已經是很好的機器可讀基礎。
- `GeometryHints.shape_spec` + `formula` + `notes_zh` 的架構已經往「結構化追溯」前進。

但就「後續要能配合 AutoCAD / Inventor 實際作業 + 具有實用追溯性」這兩個最硬的需求來看，**目前版本仍有明顯落差**。主要問題是把太多期望壓在單一 `name` 字串上。

### 9.2 針對四大需求的診斷

| 需求 | 現況評價 | 主要風險 |
|------|----------|----------|
| **人看得懂** | 中等 | 異形板 `150x130x25x50x12t` 沒人知道 25 和 50 分別對應哪一邊；很多 legacy 名稱仍充斥「PLATE」「LUG PLATE TYPE-C」這種模糊字串 |
| **機器看得懂** | 良好（基礎已備） | `role` + `shape_spec` 結構已存在，但 `name` 本身還混亂，無法直接當 PartNumber 解析 |
| **配合 AutoCAD / Inventor** | 弱 | `inventor_params.py` 幾乎只服務 Pipe Shoe；鋼板類仍抓 legacy name（如 `Plate_` 開頭）；沒有穩定 ID 機制，未來改命名規則會斷線 |
| **具有追溯性** | 中等偏弱 | 目前把追溯性想像成「把材質、rev、公式塞進 name」，這是錯誤方向。真正有價值的追溯資訊應放在結構化欄位 |

**Grok 核心判斷**：`name` 應該越乾淨、越穩定越好。**追溯性不是靠把什麼都塞進 name**，而是靠已經存在的 `geometry.*` + `source_fullstrings` + `material_canonical_id` 這三樣。

### 9.3 核心建議：採「雙軌制」+ 盡早引入穩定識別碼

#### 建議最終 `entry.name` 格式（機器主鍵 / PartNumber 用）

```
{type_or_family}_{role}_{shape_spec}_{short_hash}
```

範例：
```
M42_base_300x300x12t_7B4K2P
07_generic_plate_300x200x9t_A9X3M1
59_lug_plate_150x130x25x50x12t_3F9A2B
```

**為什麼要加短 hash（6~8 碼）？**
- 這是給 Inventor / Vault / PDM 用的**穩定實體 ID**。
- 未來即使調整命名規則、微調尺寸、或補強 shape 描述，hash 只要計算基礎不變，就永遠指向同一塊板。
- hash 建議基於 `(role, A, B, 關鍵異形參數, t, material_family)` 計算，而非整個 name 字串。

#### 人看得懂的資訊 → 拆欄位，不要全塞 name

建議在 BOM / 材料合計表 / Inventor iProperty 同時輸出以下獨立欄位：

| 欄位 | 用途 | 目前狀態 | 建議 |
|------|------|----------|------|
| `role` (ComponentRole) | CAD 對應圖庫、UI 分類 | 已很好 | 繼續強化 |
| `shape_spec` | 放樣 / 裁切用完整輪廓 | 已支援 | **必須補視覺定義文件** |
| `geometry.formula` | 「這塊板尺寸怎麼來的」追溯 | 多數 type 還沒填 | 強烈建議補齊 |
| `source_fullstrings` | 「這塊板被哪些 designation 引用」 | MaterialSummary 已做 | 匯出層要暴露出來 |
| `notes_zh` | CAD 師傅需要的補充說明 | 已有機制 | 鼓勵各 type 多填 |
| `material_canonical_id` | 材質正規化 ID | 已存在 | 未來可考慮當作 hash 計算因子之一 |

這樣 CAD 師傅看 Excel 時有乾淨的 PartNumber，同時又有完整的人類可讀資訊。

### 9.4 對現有計畫的具體回應與調整建議

1. **對 Claude 建議「把材質放進 name」**  
   **Grok 完全同意 Deep Code 的反對意見**。材質變更不應改變零件識別碼，否則同尺寸不同材質的 M42 底板會被錯誤拆成兩筆採購。

2. **對 Rev 版次**  
   **Grok 同意**：引擎端絕對不要管 rev。rev 是發圖 / PDM 層的事。`name` 永遠保持「設計意圖版」，CAD 端存檔時再自己加 `_rA.ipt`。

3. **對 shape_spec 的語義問題（最嚴重）**  
   這是目前計畫最大的落地風險。Type 59 的 `150x130x25x50x12t` 如果沒有圖或文件定義，CAD 師傅永遠要問人。  
   **Grok 強烈建議**：在改名前就先產出 `docs/plate_shape_reference.md`，裡面用表格 + 簡單示意圖（mermaid 或截圖）定義每一種常見 role 的 shape 順序。

4. **對 Inventor 銜接**  
   目前 inventor_params.py 幾乎只處理管鞋。鋼板類未來要能直接把標準化後的 `name` 當成 PartNumber 餵給 Inventor，同時要把 `shape_spec` + `holes` 結構化傳過去。  
   **Grok 建議**：把「鋼板類 Inventor 參數模型設計」跟 naming 計畫綁在一起做，而不是之後再接。

5. **對落地步驟**  
   同意 Claude → Deep Code 的「fixture 先行」思路。但我再加一條：  
   **Step 0.5** 就應該先把「異形板 shape 語義定義文件」寫好，否則後面每個 type 改名時都會卡住。

### 9.5 風險與優先順序建議（Grok 觀點）

**最高優先（現在就該做）：**
- 補 `docs/plate_shape_reference.md`（含常見 L 型、弧形、T 型、梯形等 shape 標註）
- 在 `build_plate_name()` 內同時計算並回傳 short_hash
- 盤點所有目前直接寫死 `category="鋼板類"` 且不走 `add_plate_entry` 的地方（type_51, 62, 72, 73, 76, 77, 78 等）

**次高優先：**
- 把 `geometry.formula` 填滿（這才是真正的計算追溯性）
- 讓匯出層同時輸出「結構化欄位版 BOM」與「單一 name 版 BOM」，給不同角色使用

**可以後面再做：**
- Stock Number 獨立欄位（hash 已經夠用，先別急）
- Rev 機制（PDM 層的事）

---

**Grok 總結建議格式（2026-06-03 版）：**

```
{type_or_family}_{role}_{shape_spec}_{short_hash}
```

範例：
```
M42_base_300x300x12t_7B4K2P
59_lug_plate_150x130x25x50x12t_3F9A2B
```

**鐵律（給後續實作者）：**
- name 裡永遠不要出現材質、rev、專案號、空格、括號、中文。
- 所有需要「人看得懂」的資訊，優先走結構化欄位（role / shape_spec / formula / notes_zh / source_fullstrings）。
- 穩定性 > 可讀性。PartNumber 改一次，Inventor 歷史資料就斷一次。

---

*Grok 審閱：2026-06-03 | 用途：針對「人機可讀 + AutoCAD/Inventor 實務 + 追溯性」四大需求給出診斷與調整建議，標記為 Grok 想法*

---

## 十、Claude 第二輪意見（2026-06-03，看完 Deep Code §八 與 Grok §九 之後）

> 以下為 Claude 看過 Deep Code 反駁與 Grok 第三方意見後的更新立場。標記用途：明確區隔哪些是我收回、哪些是我堅持、哪些是新發現。**本節所有內容均為 Claude 想法**。

### 10.1 〔Claude 第二輪意見〕收回的部分

Deep Code §8.1 / §8.2 / §8.3 的反駁我認了。理由比我原本想的更紮實：

**(a) 材質不進 name** — 收回 §7.1(a)
- `entry.material` 已是獨立欄位，且 dedup key 已含 material（§3.4），把材質塞 name 純屬冗餘
- 真正的原則：**name = 身份識別碼，material = 屬性**。同一塊板換鋼種不變身份；變身份就該是不同零件
- 這個分離原則我原本沒拉出來，是 Deep Code §8.1 的洞察

**(b) Rev 不進 name** — 收回 §7.1(b)
- Rev 是發圖週期的概念，計算引擎根本不知道現在是 rev A 還 rev B
- 引擎輸出 = 「設計意圖版」，PDM 落地時自己加 `_rA.ipt`
- 強塞 rev 違反單一職責

**(c) 專案前綴不進 name** — 收回 §7.1(c)
- `source_fullstrings` 已承載專案/來源資訊，重複會破壞同板跨案聚合

### 10.2 〔Claude 第二輪意見〕仍堅持的部分：Stock Number / Hash 必須「現在」加

Deep Code §8.8 說「先別急」，但我和 Grok §9.3 立場一致：**就是因為現在在動資料模型，才該一次到位**。

論證：
- name 未來幾乎一定會微調（補新 role、shape_spec 修語法、prefix 規則調整）。每次微調都是字串比對的潛在斷點
- 一旦 Inventor / Vault 拿 name 當 PartNumber 建檔，**name 改一次 = 歷史資料斷一次**
- short_hash 的計算基礎應該是「物理屬性」而非 name 字串本身（否則 hash 跟 name 一起斷）
- 建議基礎：

```python
hash_input = (
    role.value,                # ComponentRole.value
    round(A, 1),               # 標準化到 0.1mm
    round(B, 1),
    round(t, 1),
    shape_kind,                # "rect" | "L" | "arc" | "trapezoid"
    material_canonical_id,     # 已存在
)
stock_id = "PL-" + hashlib.sha1(repr(hash_input).encode()).hexdigest()[:6].upper()
```

這樣 name 怎麼改、role 標籤怎麼修正，只要物理沒換，hash 永遠一致。Inventor 用這個當穩定主鍵。

落地成本極低：`AnalysisEntry` 多一個 `stock_id: str | None`，旁邊加 `build_stock_id()`，不影響 dedup。

### 10.3 〔Claude 第二輪意見〕對 Grok §9.3 加碼：shape 語義文件是阻擋項

我原本 §7.2(b) 只輕描淡寫，Grok 把它定位為 Step 0.5。**我同意而且要再加碼**：

> shape_spec 沒有視覺定義 → 改名 100% 完成，CAD 師傅還是要問人 → 改名價值打對折

具體建議：
- `docs/plate_shape_reference.md` **不是「之後補」，是改名計畫的前置可交付物**
- 每個 role 至少要有一張示意圖，標 A/B/C/D/t 對應的邊
- **弧形板要特別處理**：弧長 vs 弦長 vs 半徑 哪個進 shape_spec？目前 §一沒寫，Type 76/77/80 SADDLE_ARC 都會卡
- L 型 Lug Plate 的 5 個維度 `150x130x25x50x12t` 需對照圖

建議 Step 0.5 阻擋後續所有步驟：

```
Step 0:   建 fixture 對照表
Step 0.5: 產出 plate_shape_reference.md ← 阻擋後續
Step 1:   pytest baseline
Step 2:   改 plate.py
...
```

### 10.4 〔Claude 第二輪意見〕新發現：variant 寫法兩種並存，§一正則無法 match

回頭仔細看 §二 B 區，發現 §一格式沒處理的問題：

| 範例 | 結構 |
|------|------|
| `M42_a_200x200x9t` | 3 段（type / role / shape）— variant `a` 塞在 role 位 |
| `39_lug_plate_D_300x200x9t` | 4 段（type / role / variant / shape） |
| `62_lug_plate_B_200x120x12t` | 4 段 |

兩種寫法並存。§一目前的正則無法同時 match。建議統一：

**選項 A**：variant 一律放 role 之後
```
M42_base_a_200x200x9t
39_lug_plate_D_300x200x9t
```

**選項 B**：variant 一律併進 role 位（小寫）
```
M42_a_200x200x9t           ← 現狀保留
39_lug_plate_d_300x200x9t  ← D → d
```

我傾向 **A**：role 是有限白名單（ComponentRole），不該因變體膨脹。但需要 Deep Code 拍板。

### 10.5 〔Claude 第二輪意見〕對 Grok §9.4(4) Inventor 綁定 — 強烈同意，再進一步

Grok 提「鋼板類 Inventor 參數模型設計綁進 naming 計畫」這點我同意。再進一步：

**這應該是改名的「驗證標準」**，而不只是延伸。

衡量改名成功的真標準不是「pytest 過了」，而是 **「Inventor 端能用 name 自動撈到正確的板模型生成參數」**。建議：

- §四加 Step 6：寫 mock Inventor 接收端，驗證每個新 name → 能正確解析出 `(type, role, dims, shape_kind)`
- 這比單純字串 regex 驗證實用得多

### 10.6 〔Claude 第二輪意見〕修正後的最終格式建議

整合 Deep Code §8.10、Grok §9.3、加我第二輪：

```
name 格式：    {type_or_family}_{role}_[{variant}_]{shape_spec}
stock_id：    PL-{6 碼 hash}（獨立欄位，不進 name）
material：    獨立欄位（不進 name）
rev：         獨立欄位（PDM 管，引擎不碰）
```

範例：

| name | stock_id | material | rev (PDM 端) |
|------|----------|----------|--------------|
| `M42_a_200x200x9t` | `PL-7B4K2P` | SS400 | — |
| `07_lug_plate_300x200x9t` | `PL-A9X3M1` | SS400 | rA (CAD 落地時加) |
| `59_lug_plate_150x130x25x50x12t` | `PL-3F9A2B` | SS400 | — |

正則（含 §10.4 選項 A variant）：

```python
PLATE_NAME_RE = re.compile(
    r"^(M42|\d{2,3})"          # type_or_family
    r"_([a-z][a-z0-9_]*?)"     # role
    r"(?:_([a-zA-Z]))?"        # optional variant
    r"_([\dx]+t)$"             # shape_spec
)
```

### 10.7 〔Claude 第二輪意見〕剩下需 Deep Code 拍板的 4 個問題

1. **variant 寫法**：§10.4 選 A 還 B？
2. **stock_id 時機**：Deep Code §8.8「先別急」 vs Grok+Claude「現在就加」？
3. **弧形板 shape_spec**：弧長 / 弦長 / 半徑 哪個進去？Type 76 / 77 / 80 SADDLE_ARC 待解
4. **shape_reference.md 是否阻擋 Step 1**：我和 Grok 都認為「是」，但會多一週前置時間，可接受嗎？

---

*Claude 第二輪：2026-06-03 | 用途：在 Deep Code §八 與 Grok §九 之後的回應，標記為 Claude 想法*

---

## 十一、Codex 審閱意見（2026-05-29）

> 以下為 Codex 對 §九 / §十 更新後的補充意見。**本節所有內容均為 Codex 想法**，用於補充決策依據；是否採納仍需人類確認。

### 11.1 〔Codex 想法〕文件目前是討論紀錄，還不是可執行規格

目前前半部仍保留初稿格式，後半部則有 Deep Code / Grok / Claude 第二輪的修正。若直接照文件前段實作，會踩到已被後段推翻的規則。

建議在文件最前面新增一節「目前決議版」，明確列出：

```text
name:      {type_or_family}_{role}_[{variant}_]{shape_spec}
stock_id:  PL-{6 碼 hash}，獨立欄位，不進 name
material:  獨立欄位，不進 name
rev:       PDM / CAD 發圖層管理，引擎不碰
```

前面所有舊範例若與「目前決議版」衝突，應標記為歷史討論或更新。

### 11.2 〔Codex 想法〕M42 與所有厚度格式應一律帶 `t`

前半部仍有：

```text
M42_a_200x200x9
M42_b_250x250x12
```

但後面已形成共識：厚度一律帶 `t`。建議全部改為：

```text
M42_a_200x200x9t
M42_b_250x250x12t
```

原因很單純：`9t` 明確是 thickness，`9` 容易被誤讀成尺寸段。

### 11.3 〔Codex 想法〕variant 寫法建議選 §10.4 的選項 A

建議採用：

```text
{type_or_family}_{role}_{variant}_{shape_spec}
```

範例：

```text
M42_base_a_200x200x9t
39_lug_plate_d_300x200x9t
62_lug_plate_b_200x120x12t
```

理由：

- `role` 應該永遠對齊 `ComponentRole` 白名單。
- `variant` 是角色底下的型式差異，不應併進 role。
- 未來解析時可以穩定得到 `role=lug_plate`、`variant=d`，不會出現 `lug_plate_d` 這種非標準 role。

如果採這個方向，M42 也應從 `M42_a_...` 改為 `M42_base_a_...`，讓 family / role / variant 三者清楚分離。

### 11.4 〔Codex 想法〕stock_id 可以現在加，但不要塞進 name

同意 Grok / Claude 第二輪：現在正在動資料模型，適合一起加入 `stock_id`。

但建議：

```text
name:     59_lug_plate_150x130x25x50x12t
stock_id: PL-3F9A2B
```

不要做成：

```text
59_lug_plate_150x130x25x50x12t_3F9A2B
```

原因：

- `name` 保持可讀與可排序。
- `stock_id` 保持穩定機器主鍵。
- 未來 hash 長度從 6 碼改 8 碼時，不需要重命名所有 PartNumber。
- CAD / Inventor 可同時使用 `name` 作 PartNumber，`stock_id` 作 Stock Number 或內部穩定 ID。

### 11.5 〔Codex 想法〕stock_id 語意要拆清楚：geometry_id vs procurement_id

文件目前一邊說「材質不進 name」，一邊建議 hash input 包含 `material_canonical_id`。這可以成立，但需要命名清楚。

建議分兩種概念：

| ID | 是否含材質 | 用途 |
|----|------------|------|
| `geometry_id` | 不含材質 | 同形狀 / 同放樣輪廓的穩定 ID |
| `stock_id` | 含材質 | 採購、PDM、Inventor 實體零件 ID |

第一階段若只做一個欄位，建議先做 `stock_id`，並明確定義它是「材質敏感」的 ID。

### 11.6 〔Codex 想法〕shape_reference.md 應作為阻擋項

同意 Grok / Claude 第二輪：`docs/plate_shape_reference.md` 應該在正式改名前完成。

沒有 shape 語義時：

```text
150x130x25x50x12t
```

只是比較長的謎語。CAD 師傅仍然需要問「25 是哪一段？50 是哪一段？」

建議 Step 0.5 成為阻擋項：

```text
Step 0:   建 fixture 對照表
Step 0.5: 產出 plate_shape_reference.md
Step 1:   pytest baseline
Step 2:   改 plate.py
```

Type 59 的 Detail Z L 型 Lug Plate 可以作為第一個 shape reference 範本。

### 11.7 〔Codex 想法〕弧形板不要硬塞進純 `AxBx...` 格式

弧形板需要顯式 `shape_kind`，不應只靠一串數字。

建議讓 `shape_spec` 依 `shape_kind` 有不同語法：

```text
rect_300x200x9t
lugz_150x130x25x50x12t
arc_ch300_sag50_w120x12t
```

其中：

- `rect`：矩形板。
- `lugz`：Type 59 Detail Z 這種 Lug Plate 輪廓。
- `arc`：弧形板，需明確定義弦長、拱高、板寬、厚度等參數。

這比 `300x50x120x12t` 更容易被人和機器同時理解。

### 11.8 〔Codex 想法〕§10.6 的 regex 不宜直接當最終規格

§10.6 的 regex 目前只適合整數尺寸與簡單 `x` 串接：

```python
r"_([\dx]+t)$"
```

它無法處理：

- 小數尺寸，例如 `276.5x100x12t`
- 顯式 shape kind，例如 `lugz_150x130x25x50x12t`
- 弧形板語法，例如 `arc_ch300_sag50_w120x12t`

建議把 regex 分階段定義：

```text
Phase 1: rect / lugz
Phase 2: arc / saddle / trapezoid
```

不要在現在把簡化 regex 寫成最終規格。

### 11.9 〔Codex 想法〕Type 59 狀態需精準標記

目前 Type 59 只能說：

```text
shape_spec 已完成；name migration 未完成
```

已完成內容：

- `GeometryHints.shape_spec`
- 材料合計 spec 顯示完整放樣尺寸
- display_remark 顯示完整放樣尺寸與重量計算方式

尚未完成內容：

- `entry.name` 尚未改為 `59_lug_plate_...`
- 尚未建立 `stock_id`
- 尚未建立 `plate_shape_reference.md` 中的 Type 59 Detail Z 語義圖

---

*Codex 審閱：2026-05-29 | 用途：補充 §九 / §十 後的落地建議，標記為 Codex 想法*

---

## 十二、Deep Code 第二輪 — 拍板決策（2026-06-03）

> 以下針對 Claude §10.7 四個待決問題 + Grok + Codex 的關鍵分歧，給出最終決定與理由。

### 12.1 variant 寫法 → 選 A（獨立段）

```
✅ M42_base_a_200x200x9t
✅ 39_lug_plate_d_300x200x9t
❌ M42_a_200x200x9t
❌ 39_lug_plate_d_300x200x9t  ← 保留，但 role=lug_plate, variant=d，非 role=lug_plate_d
```

理由（Codex §11.3 擊中要害）：
- `role` 對齊 `ComponentRole` 白名單 → 永遠可驗證
- `variant` 獨立 → 未來新增 variant 不需要改 enum
- M42 也適用：`M42_base_a` 而非 `M42_a`，family/role/variant 三板斧一致

**最終三段式：**
```
{family}_{role}_[{variant}_]{shape_spec}
  │       │        │          └─ 尺寸
  │       │        └─ a|b|c|d|e（可選，M42/Lug Plate 等需要時出現）
  │       └─ base_plate | lug_plate | stopper_plate ...
  └─ M42 | 07 | 14 | 59 ...
```

### 12.2 stock_id → 現在就加，但不進 name

Grok + Claude + Codex 三方一致要求，我收回 §8.8 的「先不要」。

格式：
```
name:      59_lug_plate_d_150x130x25x50x12t
stock_id:  PL-3F9A2B
```

**關鍵規則：**
1. `stock_id` 是 `AnalysisEntry` 的獨立欄位，**不塞進 name**
2. hash 基礎是物理屬性，不是 name 字串（name 可以改名，stock_id 不動）
3. 含 `material_canonical_id` → 同形狀不同材質 = 不同 stock_id（Codex §11.5 的 procurement_id 概念）
4. 未來可再加 `geometry_id`（不含材質），但第一階段只做 `stock_id`

### 12.3 弧形板 shape_spec → 顯式 shape_kind 前綴

純數字串對弧形板完全不可讀。採用 Codex §11.7 的方向：

| shape_kind | shape_spec 格式 | 範例 |
|------------|----------------|------|
| `rect` | `AxBxt` | `rect_300x200x9t` |
| `lugz` | `AxBxCxDxt` | `lugz_150x130x25x50x12t` |
| `arc` | `弦長x弧高x板寬xt` | `arc_ch300_s50_w120x12t` |
| `saddle` | `弦長x弧高x板寬xt` | `saddle_ch400_s80_w180x16t` |

規則：
- 四方板 `rect_` 可省略（預設 = rect）
- 非四方板 **必須** 帶 shape_kind 前綴
- 各 shape_kind 的參數順序定義在 `docs/plate_shape_reference.md`

### 12.4 shape_reference.md → 是阻擋項，列為 Step 0.5

三方一致。Type 59 Detail Z 的 Lug Plate 作為第一個範本。

---

### 12.5 最終決議格式（此版本為 ground truth）

```
name:      {family}_{role}_[{variant}_]{shape_spec}
stock_id:  PL-{6碼hash}（獨立欄位）
material:  獨立欄位（entry.material）
rev:       PDM / CAD 層管理，引擎不碰
```

完整範例：

| name | stock_id | material |
|------|----------|----------|
| `M42_base_a_200x200x9t` | `PL-A1B2C3` | SS400 |
| `M42_base_b_250x250x12t` | `PL-D4E5F6` | SS400 |
| `07_generic_plate_rect_300x200x9t` | `PL-G7H8I9` | SS400 |
| `39_lug_plate_d_lugz_150x130x25x50x12t` | `PL-J0K1L2` | SS400 |
| `59_lug_plate_lugz_150x130x25x50x12t` | `PL-3F9A2B` | SS400 |
| `76_reinforcement_pad_arc_ch400_s50_w180x12t` | `PL-M3N4O5` | SS400 |
| `80_saddle_arc_arc_ch400_s80_w180x16t` | `PL-P6Q7R8` | SS400 |

---

### 12.6 調整後的實施步驟

```
Step 0:   建 fixture 對照表 (plate_name_migration.json)
Step 0.5: 產出 plate_shape_reference.md  ← 阻擋後續
Step 1:   pytest baseline（確認舊 name 現狀）
Step 2:   改 plate.py（build_plate_name + build_stock_id 輔助函式）
Step 3:   改 m42.py → 跑測試
Step 4:   逐 type 改 → 每改一個跑測試
Step 5:   切換 fixture 為新 name ground truth
Step 6:   處理 D 區直接賦值項（統一走 add_plate_entry）
Step 7:   Pipe Shoe JSON configs（Type 52~67）
Step 8:   Inventor 參數對接驗證
```

---

### 12.7 對前面各節不一致處的清理指示

以下內容因後續討論已過時，需在最終版中更正：

| 位置 | 舊內容 | 應改為 |
|------|--------|--------|
| §一 範例表 | `M42_a_200x200x9`（無 t） | `M42_base_a_200x200x9t` |
| §一 範例表 | `07_generic_plate_300x200x9t` | `07_generic_plate_rect_300x200x9t` |
| §三 3.1 | `M42_a_200x200x9` | `M42_base_a_200x200x9t` |
| §三 3.2 | `07_sliding_plate_300x200x9t` | role 應為 `generic_plate` 非 `sliding_plate` |
| §四 Step 1~5 | 順序 | 改為 §12.6 的 Step 0~8 |
| §八 8.10 | 最終落地格式缺 variant 段 | 依 §12.5 更新 |

---

*Deep Code 第二輪：2026-06-03 | 用途：對 Claude §10.7 四個待決問題的最終拍板 + 整合 Grok/Codex 共識*

---

## 十三、Grok 針對兩個最核心歧異點的獨立分析與建議（2026-06-03）

> **本節為 Grok 專為「兩個真正最吵、尚未完全收斂」的議題所寫的決策分析**，供 Claude、GPT 及其他 deep think AI 參考與再推理。所有內容均標記為 Grok 想法，與 Deep Code §12 的拍板獨立。

### 問題背景

經過多輪討論，目前最大兩個尚未完全收斂（或雖有拍板但仍有討論空間）的核心歧異是：

1. **Variant 語法位置**（M42 是最大雷）
2. **stock_id 是否該併入 `name` 字串**

以下針對這兩個問題，給出我目前的工程判斷與風險評估。

---

### 議題一：Variant 要獨立成段，還是併進 role 位置？

**Deep Code §12.1 已拍板選 A（獨立 variant）**：
- `M42_base_a_200x200x9t`
- `39_lug_plate_d_300x200x9t`

**我的分析（Grok）：**

**支持獨立 variant（選 A）的強烈理由：**
- `role` 必須永遠對齊 `ComponentRole` enum，這是整個架構的基石（機器可讀、聚合、CAD 對應圖庫）。
- 如果把 `a/b/c/d/e` 或 `B/D` 併進 role，會產生 `lug_plate_d`、`base_a` 這種「非標準 role」，未來 enum 會被污染。
- 長期維護性勝出：新增 variant 不需要改 ComponentRole。

**反對選 A 的現實成本（我必須誠實指出）：**
- M42 是全專案使用量最大的鋼板類共用件，現有程式碼、VBA、圖面、BOM 習慣大量依賴 `M42_a`、`M42_b` 這種簡潔寫法。
- 改成 `M42_base_a` 會讓大量現有使用者（尤其是 CAD 師傅）覺得「變複雜了」。
- 遷移成本比其他 type 高一個數量級。

**Grok 最終建議（議題一）：**

**我支持 Deep Code 的決定（選 A），但要誠實面對遷移痛點。**

推薦做法：
- 技術上鎖定選 A（保護 ComponentRole 純潔性）。
- 但在 `ROLE_DISPLAY_NAME` 或匯出層提供「簡潔別名」機制，讓 BOM / 圖面標題欄可以選擇顯示 `M42-a` 或 `M42 底板 a 型`，降低使用者衝擊。
- M42 的 variant（a~e）建議在 `plate_shape_reference.md` 特別說明其特殊地位（它是「標準共用底板家族的子型」）。

**如果硬要選 B（併進 role），我預測 2~3 年後一定會後悔**，因為 role 會越來越髒。

---

### 議題二：stock_id 要不要併入 `name` 結尾？

這是我在 §9.3 原本的立場，與 Codex §11.4 及 Deep Code §12.2 形成明顯分歧。

**我的原始立場（§9）**：
建議 `59_lug_plate_150x130x25x50x12t_3F9A2B`（hash 併在 name 尾端）

**反對併入 name 的有力論點（Codex + Deep Code）：**
- name 應該盡量「人類可讀 + 穩定可排序」。
- hash 長度未來可能從 6 碼變 8 碼，如果併在 name 裡，等於所有 PartNumber 都要改一次。
- Inventor / Vault 最怕「同一個實體零件因為命名規則演進而換 PartNumber」。
- 乾淨分離：`name` 給人看，`stock_id` 給機器當穩定主鍵，職責清楚。

**支持併入 name 的工程現實理由（我仍想保留這個聲音）：**

1. **單一字串優勢**：很多中小型專案、Excel BOM、AutoCAD 屬性、甚至部分 Inventor 流程，工程師還是習慣「一個欄位就搞定 PartNumber + 穩定 ID」。
2. **可見性**：如果 stock_id 完全隱藏在另一個欄位，很多 CAD 師傅在看圖或做簡單比對時會看不到，容易重複建模。
3. **過渡期容錯**：在 `stock_id` 機制還沒完全接進 Inventor iProperty 之前，把短 hash 放在 name 尾端，是一種「保險絲」——至少肉眼能看出「這兩個長得像的板其實是同一塊」。

**Grok 針對議題二的更新立場（2026-06-03）：**

我**部分收回 §9 的原始建議**，但不是完全投降。

**推薦混合策略（我認為最務實）：**

```
name:      59_lug_plate_lugz_150x130x25x50x12t          ← 不要 hash
stock_id:  PL-3F9A2B                                    ← 獨立欄位（主要穩定 ID）
alt_short: 59-LP-3F9A2B                                 ← 可選的「人類好記短代號」（非強制）
```

理由：
- 主力走 Deep Code / Codex 的「name 乾淨 + stock_id 獨立」路線（長期正確）。
- 但強烈建議在 `AnalysisEntry` 增加一個 `alt_short` 或 `display_code` 欄位，讓需要「單一短字串」的場合有東西可用（類似 Git 的 short hash 概念）。
- 這樣既保護了長期架構乾淨，又沒有完全犧牲實務便利性。

**如果一定要二選一**：
- 我現在傾向 **不併入 name**（接受 Deep Code §12.2）。
- 但我認為「完全沒有任何短識別碼出現在人類常用欄位」是另一種極端，未來使用時會痛。

---

### Grok 給決策者的總結建議

| 議題 | 我最終傾向 | 風險提醒 |
|------|------------|----------|
| Variant 位置 | 強力支持選 A（獨立 variant） | M42 遷移痛點要提前規劃「簡潔別名」緩衝機制 |
| stock_id 併入 name | 傾向不併入，但要補償提供 alt_short / display_code | 不要讓 CAD 師傅完全看不到穩定 ID |

**我認為目前最該做的事（優於再多一輪 AI review）：**

1. 請**人類決策者（你）**針對以上兩個議題明確拍板一次（即使是「暫時採用 Deep Code 方案，觀察 3 個月再檢討」也行）。
2. 拍板後，立刻在文件最前面新增一個 **「2026-06-03 共識決議版」** 區塊，把已鎖定的格式寫死。
3. 把 §1~6 裡所有與決議衝突的舊範例標記為「歷史討論」。

只有這樣，這份文件才能從「多 AI 吵架紀錄」真正轉變成「可執行的命名標準」。

---

*Grok 專節：2026-06-03 | 用途：針對 Variant 與 stock_id 兩個最核心未完全收斂議題，提供獨立工程判斷供 Claude / GPT 等 deep think AI 參考與挑戰，標記為 Grok 想法*

---

## 十四、Claude 第三輪意見（2026-06-03，回應 Codex §十一 / Deep Code §十二 / Grok §十三）

> 本節為 Claude 看過 Codex 補充、Deep Code 拍板、Grok 對兩大議題的獨立分析後的回應。**本節所有內容均為 Claude 想法**，分三類：(A) 回應 Grok §十三 兩大議題的挑戰、(B) 對 §十二 拍板版抓出的新問題、(C) 雜項補強。

### 14.1 〔Claude 第三輪意見〕回應 Grok §十三 議題一：variant 位置

**我與 Grok 立場一致：選 A 是對的**。

但對 Grok 的「簡潔別名 / display 緩衝」提議，**我有保留**：

- 別名機制本質上會分裂出第三個識別字串。CAD 師傅一旦看到 `M42-a` 出現在 BOM、看到 `M42_base_a_200x200x9t` 出現在 PartNumber、看到 `PL-A1B2C3` 出現在 StockNumber，三套對照表就開始繁殖。
- 真正的痛點不是「name 太長」，是「不熟悉的格式」。`M42_base_a_200x200x9t` 看一個月就習慣了；多增的 `_base_` 兩個 token 不會壓垮使用者。
- **建議**：別名先不做。等實際 BOM 上線後若有具體反饋（不是預估的不適應），再加 `display_alias` 欄位，且只用在「展示層」，絕不進 dedup key、不進 PartNumber、不進檔名。

簡言之：**保持兩個 ID（name + stock_id），第三個 alias 是 YAGNI**。

### 14.2 〔Claude 第三輪意見〕回應 Grok §十三 議題二：stock_id 進 name 與否

**完全同意 Deep Code §12.2：stock_id 獨立欄位，不進 name**。

對 Grok 「保險絲」論點（短 hash 在 name 尾端讓人肉眼比對）的回應：
- 這個需求在資料模型有 `stock_id` 獨立欄位 + 匯出層同時印兩欄之後就消失了
- 真正會發生的情境是「Excel BOM 只顯示 name 一欄」→ 解法是匯出層多印一欄，不是把 hash 灌回 name
- Inventor `iProperty.PartNumber` = name，`iProperty.StockNumber` = stock_id，肉眼比對問題在 CAD 端就解了

對 Grok 的 `alt_short` 建議同 §14.1 — **YAGNI**。

### 14.3 〔Claude 第三輪意見〕對 §12 拍板版發現的問題 — hash 計算缺 variant

**這是阻擋級的 bug**：

§10.2 / §12.2 hash 計算基礎為：
```python
(role.value, A, B, t, shape_kind, material_canonical_id)
```

漏了 `variant`。後果：

| name | variant | A×B×t | hash |
|------|---------|-------|------|
| `M42_base_a_200x200x9t` | a（無鑽孔） | 200×200×9 | PL-XXXXXX |
| `M42_base_b_200x200x9t`（假設同尺寸 b 型有鑽孔） | b | 200×200×9 | PL-XXXXXX ← 撞 |

a 型無鑽孔、b 型有鑽孔，物理上是兩個不同零件，hash 卻一樣 → Inventor / PDM 端會把兩者誤認為同一塊。

**修正**：hash 基礎必須加 variant：

```python
hash_input = (
    family,                  # 新增：M42 / 07 / 14 ...
    role.value,
    variant or "",           # 新增
    round(A, 1),
    round(B, 1),
    round(t, 1),
    shape_kind,
    extra_shape_params,      # 新增：弧形板的 ch/s/w 等
    material_canonical_id,
)
```

family 也建議加入：跨 type 的同尺寸同 role 板（如 14 與 15 都有 `wing_plate_rect_150x80x6t`）在物理上仍應視為「同物可採購、不同位置安裝」—— 這個應否合 hash 取決於採購策略。我傾向 **加入 family**，因為 §3.4 dedup 已用 name 含 type 來區隔自有件；hash 也應對齊此策略。

### 14.4 〔Claude 第三輪意見〕對 §12.3 弧形板 shape_spec 語法的一致性問題

§12.5 範例：
```
76_reinforcement_pad_arc_ch400_s50_w180x12t
80_saddle_arc_arc_ch400_s80_w180x16t
```

問題：分隔符混用 — `ch400_s50_w180` 用 `_` 隔開鍵值對，但結尾的 `w180x12t` 突然又變回 `x`。解析器要處理兩種風格。

**建議統一**為一種：

**方案 a**：全部 key-value（推薦）
```
arc_ch400_s50_w180_t12
```
- 解析簡單：`split("_")` 後每個 token 都是 `[key][value]` 形態
- 厚度 `t12` 而非 `12t`，雖然與四方板 `300x200x9t` 不一致，但弧形板已不適用 `x` 串接

**方案 b**：全 `x` 串接 + shape_kind 前綴
```
arc_400x50x180x12t
```
- 與四方板風格一致
- 但失去「哪個數字是弦長」的可讀性 — 又回到 Type 59 的謎語問題

我**強烈推薦方案 a**。為了一致性，建議四方板對應改為：
```
rect_a300_b200_t9
```

但這對既有討論影響太大，妥協方案是：
- **四方板維持 `AxBxt`**（最常見、最直觀）
- **複雜形狀一律 key-value**（弧形、L 型若採新版可改為 `lugz_a150_b130_c25_d50_t12`）

### 14.5 〔Claude 第三輪意見〕新發現：shape_kind 必須是結構化欄位，不只是 name 的 token

§12.3 只規定 shape_kind 是 shape_spec 的「字串前綴」。但實作上要避免「name 是 source of truth」的反模式。

**建議**：
- `GeometryHints` 新增 `shape_kind: Literal["rect", "lugz", "arc", "saddle", "trapezoid"]`
- `build_plate_name()` 從這個結構化欄位讀出後拼進 name
- 驗證層：`assert name.contains(shape_kind)` —— 雙向一致

理由：未來若有任何代碼路徑要查「這塊板是不是弧形」，應該讀 `entry.geometry.shape_kind`，不該 `name.split("_")[2] == "arc"`。後者一旦 name 規則變動就斷。

### 14.6 〔Claude 第三輪意見〕對 §12.7 清理表的補充

§12.7 已列出舊範例需更新，補充兩項：

| 位置 | 舊內容 | 應改為 |
|------|--------|--------|
| §五 預期收穫表 | `Plate_a_有鑽孔 → M42_a_200x200x9t` | `→ M42_base_a_200x200x9t` |
| §五 預期收穫表 | `07_generic_plate_300x200x9t → 直接開 Type 07 PDF` | `→ 07_generic_plate_rect_300x200x9t` |
| §二 B 區整張表 | 「建議名稱」欄全部 | 全部加 shape_kind 前綴（rect_ 可省，其他必須） |

§二 B 區的「建議名稱」欄是後續實作的對照表，**強烈建議在 Step 0 fixture 之前先把這張表更新為新格式**，否則 fixture 會基於過時規格生成。

### 14.7 〔Claude 第三輪意見〕對 §十二 拍板的整體判斷

§12 的拍板是這份計畫從「討論文件」走向「執行規格」的關鍵轉折。但目前仍有 §14.3 hash 缺 variant、§14.4 shape_spec 分隔符不一致、§14.5 shape_kind 結構化 三項在落地前必須補釘。

優先順序：
1. **必補（Step 0 之前）**：§14.3 hash variant、§14.5 shape_kind enum
2. **建議補（Step 0.5 之前）**：§14.4 shape_spec 統一語法
3. **可延後**：§14.6 §二 B 區表格更新可在 fixture 階段一起做
4. **YAGNI**：§14.1 / §14.2 別名與 alt_short 機制

### 14.8 〔Claude 第三輪意見〕剩下對人類決策者（你）的問題

收斂中，剩 2 個：

1. **§14.3 hash 是否含 family**？我推薦含，理由是與 dedup 策略一致；但若採購端認為「跨 type 同尺寸應視為同物」，則 hash 不含 family、dedup 也需鬆綁。這影響採購單合併邏輯。
2. **§14.4 shape_spec 分隔符**：接受四方板 `AxBxt` + 複雜形 `key-value` 的妥協方案嗎？還是要全 key-value 一致？

---

*Claude 第三輪：2026-06-03 | 用途：回應 Grok §十三 兩議題挑戰 + 抓出 §十二 拍板版的 hash/shape 三項落地阻擋點，標記為 Claude 想法*
