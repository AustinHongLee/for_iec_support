# IEC 管架支撐分析工具 — 程式架構介紹

> 本文件用於讓 AI 助手快速理解本專案的架構、邏輯與資料流，方便參與程式討論。

---

## 一、專案目標

這是一套 **工業管道支撐架（Pipe Support）的重量分析與材料採購規劃工具**，主要功能：

1. **重量分析**：輸入支撐編碼（如 `01-2B-05A`），自動拆解成零件清單（BOM），計算每個零件的尺寸、材質、重量
2. **材料合計**：將多筆分析結果匯總為採購清單，以 `(品名, 規格, 材質)` 分組統計
3. **下料最佳化**：用 FFD（First Fit Decreasing）演算法，規劃原料切割方案，減少浪費
4. **匯出報表**：支援 Excel / CSV / PDF 多格式輸出

本系統是從 VBA（Excel 巨集）版本遷移到 Python + PyQt6 桌面應用。

---

## 二、技術棧

| 層級 | 技術 |
|------|------|
| UI 框架 | PyQt6（Fusion style） |
| 核心計算 | 純 Python dataclass + 查表邏輯 |
| PDF 預覽 | PyMuPDF (fitz) |
| Markdown 渲染 | markdown 套件 |
| Excel 匯出 | openpyxl |
| PDF 匯出 | reportlab |
| 資料格式 | JSON 配置檔 + Python dict 查詢表 |

---

## 三、目錄結構

```
python_app/
├── main.py                  # 程式入口
├── core/                    # 【核心計算引擎】
│   ├── models.py            #   資料模型 (AnalysisEntry, AnalysisResult)
│   ├── parser.py            #   字串解析工具（拆解支撐編碼）
│   ├── calculator.py        #   主調度器（TYPE_HANDLERS 分派到各 type）
│   ├── config_loader.py     #   JSON 配置讀寫
│   ├── pipe.py              #   管件零件建立
│   ├── plate.py             #   鋼板零件建立
│   ├── steel.py             #   型鋼零件建立（角鋼/H型鋼/槽鋼）
│   ├── bolt.py              #   螺栓零件建立
│   ├── m42.py               #   M42 底板組件邏輯（字母 A~T 對應不同板+螺栓組合）
│   ├── material_summary.py  #   材料彙總（多筆結果 → 採購清單）
│   ├── cutting_optimizer.py #   1D 下料最佳化（FFD 演算法）
│   └── types/               #   各 Type 計算器
│       ├── type_01.py       #     Type 01: 假管支撐（彎頭/三通）
│       ├── type_03.py       #     Type 03: 小管角鋼支撐
│       ├── type_05.py       #     Type 05: 角鋼立式支撐
│       ├── type_07.py       #     Type 07: 滑動彎頭支撐
│       ├── ...              #     （共 37 種 Type）
│       └── type_85.py
├── data/                    # 【查詢表資料庫】
│   ├── pipe_table.py        #   管道外徑、壁厚、每米重量（69 種管徑×多種 Schedule）
│   ├── steel_sections.py    #   型鋼規格：角鋼/槽鋼/H型鋼 重量表 + 代碼映射
│   ├── stock_lengths.py     #   原料進貨長度(6000mm)、鋸口損耗(3mm)、餘量(2mm)等參數
│   ├── m42_table.py         #   M42 底板規格表（按管徑查板尺寸、螺栓規格）
│   ├── tee_table.py         #   ASME B16.9 三通尺寸表
│   └── type0X_table.py      #   各 Type 專用查詢表（type07~type23）
├── configs/                 # 【JSON 配置檔】
│   ├── type_catalog.json    #   所有 Type 的目錄（名稱、狀態、分類、PDF 路徑）
│   ├── type_01.json         #   Type 01 深層配置（連接方式、約束函數、查詢表）
│   └── support_ontology.json#   支撐型式語義分類、家族關係、選型決策樹
├── ui/                      # 【PyQt6 介面層】
│   ├── main_window.py       #   主視窗（4 個 Tab 頁面）
│   ├── type_manager.py      #   Type 總覽（目錄瀏覽 + PDF 預覽 + 文件閱讀）
│   ├── material_cutting_page.py  # 材料合計 + 下料方案顯示
│   └── ontology_browser.py  #   支撐架構瀏覽器（家族關係 + 選型決策）
├── export/                  # 【匯出模組】
│   ├── excel_export.py      #   重量分析 → Excel
│   ├── csv_export.py        #   重量分析 → CSV
│   ├── pdf_export.py        #   重量分析 → PDF（橫向 A4）
│   └── summary_export.py    #   材料合計 + 下料方案 → Excel（雙工作表）
├── assets/                  #   PDF 圖面、圖示
└── docs/types/              #   各 Type 的 Markdown 技術文件
```

---

## 四、核心資料模型

### `AnalysisEntry`（一個零件/行項目）
```python
@dataclass
class AnalysisEntry:
    item_no: int          # 項次（自動編號）
    name: str             # 品名，如 "Pipe A (upper)", "Plate_d_有鑽孔"
    spec: str             # 規格，如 "1-1/2\"", "9mm"
    material: str         # 材質，如 "SUS304", "A53Gr.B", "A36"
    length: float         # 長度 mm
    width: float          # 寬度 mm（鋼板用）
    quantity: int          # 數量
    weight_per_unit: float # 每米重/每件重
    unit_weight: float     # 單重 kg
    total_weight: float    # 總重 kg
    unit: str             # 單位 "M"(米), "PC"(片), "SET"(組)
    category: str         # 屬性 "管路類", "鋼板類"
    factor: float         # 係數
    remark: str           # 備註
```

### `AnalysisResult`（一筆支撐編碼的完整分析結果）
```python
@dataclass
class AnalysisResult:
    fullstring: str          # 原始輸入，如 "01-2B-05A"
    entries: List[AnalysisEntry]  # 零件清單
    error: str               # 錯誤訊息（若有）
    warnings: List[str]      # 警告
    total_weight: float      # 總重量（property）
```

---

## 五、核心運算流程

### 5.1 支撐編碼格式

支撐編碼以 `-` 分隔，格式因 Type 而異：

| Type | 格式 | 範例 | 意義 |
|------|------|------|------|
| 01 | `01-{管徑}-{H高度}{M42字母}` | `01-2B-05A` | 2" 管、H=500mm、M42底板型式A |
| 03 | `03-{管徑}-{H}{M42字母}` | `03-1B-05N` | 1" 管、H=500mm、底板型式N |
| 07 | `07-{管徑}-{H}{M42字母}` | `07-2B-20J` | 2" 管、H=2000mm、底板型式J |

- **管徑**格式：`2B` = 2 吋, `10` = 10 吋, `1/2` = 1/2 吋
- **H 高度**：`05` = 500mm, `20` = 2000mm（乘以 100）
- **M42 字母**：A~T，代表底板組件配置

### 5.2 主調度邏輯 (`calculator.py`)

```
使用者輸入: "01-2B-05A"
    │
    ├─ parser.get_type_code() → "01"
    │
    ├─ TYPE_HANDLERS["01"] → type_01.calculate()
    │
    ├─ 套用 overrides（若有）: connection, upper_material, pipe_size...
    │
    └─ 回傳 AnalysisResult
```

- `TYPE_HANDLERS` 是一個 dict，映射 37 種 type code 到對應的 `calculate()` 函數
- 支援全域設定 (`_ANALYSIS_SETTINGS`) + 逐筆覆寫 (`overrides`)

### 5.3 Type 計算器模式（以 Type 01 為例）

```python
def calculate(fullstring, connection="elbow", upper_material="SUS304", overrides=None):
    # 1. 解析編碼
    line_size = get_part(fullstring, 2)   # "2B" → 2.0
    h_code = get_part(fullstring, 3)      # "05A" → H=5, letter="A"

    # 2. 查表取得管件規格
    table_row = TYPE01_TABLE[line_size]   # → pipe_size="1-1/2", schedule="SCH.80", L=71

    # 3. 計算上段管長度
    if connection == "elbow":
        length_a = L + 100               # 171 mm
    else:  # tee
        length_a = 100 + TEE_DATA[line_size]["M"]

    # 4. 計算下段管長度
    length_c = H * 100 - 100             # 400 mm

    # 5. 建立零件
    add_pipe_entry(result, "Pipe A", pipe_size, schedule, length_a, upper_material)
    add_pipe_entry(result, "Pipe C", support_pipe_size, "SCH.40", length_c, "A53Gr.B")

    # 6. M42 底板組件
    perform_action_by_letter(result, letter="A", pipe_size=support_pipe_size)

    return result
```

### 5.4 M42 底板系統 (`m42.py`)

M42 是底板組件的統稱，用**字母 A~T** 代表不同的板+螺栓組合：

| 字母 | 組件內容 |
|------|----------|
| A | 底板 a（無鑽孔） |
| B | 底板 a + 底板 d（有鑽孔）+ 4×膨脹螺栓 |
| D | 底板 a + 底板 e |
| E | 底板 a + 底板 d + 4×螺栓 + 2×角鋼 L40×40×5 |
| G | 底板 a + b + 2×螺栓 |
| J | 底板 a + b + c + 4×螺栓 |
| L | 底板 a + b + c + d + 8×螺栓 |
| T | 無底板（直接固定於基礎） |
| ... | 其他組合 |

底板尺寸從 `m42_table.py` 按管徑查詢。

### 5.5 零件建立函數

| 函數 | 用途 | 計算邏輯 |
|------|------|----------|
| `add_pipe_entry()` | 加入管件 | 查 pipe_table 取每米重 → 長度×每米重 = 單重 |
| `add_plate_entry()` | 加入鋼板 | 長×寬×厚×密度 = 重量 |
| `add_steel_section_entry()` | 加入型鋼 | 查 steel_sections 取每米重 → 長度×每米重 |
| `add_bolt_entry()` | 加入膨脹螺栓 | 查 m42_table 取規格，預設 1kg/SET |
| `add_custom_entry()` | 加入其他零件 | 自訂名稱/規格/重量 |

### 5.6 材料彙總 (`material_summary.py`)

```
多筆 AnalysisResult
    │
    ├─ 按 (品名, 規格, 材質) 分組
    │
    ├─ 管件/型鋼 (linear): 累加總長度 → 除以原料長度 → 計算採購根數
    ├─ 鋼板 (plate): 累加總片數
    └─ 螺栓 (piece): 累加總組數
    │
    └─ MaterialSummary (含 SummaryLine 列表)
```

### 5.7 下料最佳化 (`cutting_optimizer.py`)

使用 **FFD（First Fit Decreasing）演算法**解決 1D 下料問題：

```
輸入: 同規格的多段需求長度
    │
    ├─ 每段加上損耗: cut_length = demand + 鋸口(3mm) + 餘量(2mm)
    │
    ├─ 依長度由大到小排序
    │
    ├─ 逐段嘗試放入現有原料棒：
    │   ├─ 找到能放的 → 放入
    │   └─ 找不到 → 開新棒
    │
    └─ 輸出: CuttingPlan（每根原料的切割段落 + 餘料 + 使用率）
```

**原料參數**:
- 進貨長度: 6000mm（管件 5800mm）
- 有效長度: 5950mm（扣兩端 25mm 毛邊）
- 鋸口損耗: 3mm/刀
- 最小可用餘料: 100mm

---

## 六、UI 架構（4 個 Tab 頁面）

### Tab 1: 重量分析（主頁面）
```
┌──────────────┬────────────────────────┬──────────────┐
│  輸入清單     │    結果表格 (12欄)      │  參數面板    │
│  (QListWidget) │  (QTableWidget)       │  (SidePanel) │
│              │                        │              │
│ ☑ 01-2B-05A │ 項次|品名|規格|長度|... │ 連接方式:    │
│ ☑ 03-1B-05N │  1  |Pipe A|1-1/2|171  │ ○ 彎頭 ● 三通│
│ ☐ 07-2B-20J │  2  |Pipe C|3   |400   │ 材質: SUS304 │
│              │  3  |Plate a|...|...   │              │
│  [新增]      │                        │  [重置]      │
│  [批次貼上]   │  [▶ 開始分析]  [匯出]   │              │
└──────────────┴────────────────────────┴──────────────┘
```

**SidePanel** 依 Type 動態切換：
- Type 01: 彎頭/三通選擇、材質、pipe_size/schedule/L 覆寫
- 其他 Type: 僅材質覆寫

### Tab 2: 材料合計 / 下料
```
┌────────────────────────────────────────────┐
│  材料合計表 (上半)                           │
│  品名 | 規格 | 材質 | 需求總長 | 採購量 | ... │
├────────────────────────────────────────────┤
│  下料計算表 (下半)                           │
│  原料# | 切割段 | 需求長 | 含損耗 | 餘料 | ... │
│  [▶ 產生]  [匯出 Excel]                     │
└────────────────────────────────────────────┘
```

### Tab 3: Type 總覽
- 左側：樹狀目錄（按分類展開），可搜尋/篩選
- 右側：PDF 預覽 + Markdown 文件 + 規格資訊
- 狀態標籤：`documented`(綠) / `cataloged`(藍) / `placeholder`(灰)

### Tab 4: 支撐架構
- 設計標準選擇（IEC）
- 左側：語義樹（12 個家族分組 + 進度統計）
- 右側：Type 詳情（家族關係、約束矩陣、選型規則）
- 約束矩陣：軸向/側向/垂直 的約束等級（FREE / PARTIAL / RESTRAINED / FIXED）

---

## 七、匯出功能

| 格式 | 內容 | 用途 |
|------|------|------|
| Excel (.xlsx) | 重量分析 18 欄 | 完整 BOM 報表 |
| CSV (.csv) | 重量分析 18 欄 (UTF-8-sig) | 資料交換 |
| PDF (.pdf) | 重量分析 11 欄（橫向 A4） | 列印用 |
| Excel 雙表 (.xlsx) | 工作表1: 材料合計 + 工作表2: 下料方案 | 採購與生產 |

---

## 八、查詢表體系

| 模組 | 資料內容 | 索引鍵 |
|------|----------|--------|
| `pipe_table.py` | 管道外徑/壁厚/每米重 | (pipe_size, schedule) |
| `steel_sections.py` | 角鋼/槽鋼/H鋼 重量 + 代碼映射 | section_code |
| `m42_table.py` | M42 底板尺寸/螺栓規格 | pipe_size |
| `tee_table.py` | ASME B16.9 三通尺寸 (C, M) | pipe_size |
| `stock_lengths.py` | 原料長度 + 下料損耗參數 | — |
| `type07_table.py` | Type 07 管件/板件規格 | line_size |
| `type08_table.py` ~ `type23_table.py` | 各 Type 專用規格表 | line_size |

---

## 九、支援的 Type 總覽

目前共實作 **37 種** Type：

| 類別 | Types | 說明 |
|------|-------|------|
| 小管基本支撐 | 01, 01T, 03, 05, 06 | 假管支撐、角鋼支撐 |
| 滑動/可調式 | 07, 08, 09, 10, 20 | 滑動彎頭、托板、螺桿 |
| 彈簧支撐 | 11 | 彈簧吊架 |
| 夾持/固定型 | 12, 13, 30, 36 | 管夾、固定座 |
| 結構鋼立柱 | 14, 15 | 立柱限位 |
| 吊掛式 | 16, 21, 22, 23, 32 | 吊桿、吊架 |
| 側向/角鐵 | 19, 24, 25 | 側向支撐 |
| 框架/懸臂 | 26~37 | 懸臂支撐 |
| 梁上承托 | 52~67 | Pipe Shoe 系列 |
| 特殊 | 85 | 特殊型式 |

每種 Type 都有獨立的 `calculate()` 函數，遵循統一介面：
```python
def calculate(fullstring: str, connection: str = "elbow",
              upper_material: str = "SUS304", overrides: dict = None) -> AnalysisResult
```

---

## 十、設計模式與要點

1. **Plugin 架構**：`TYPE_HANDLERS` dict 註冊新 Type，新增 Type 只需寫 `type_XX.py` 並加入映射
2. **Config-Driven**：Type 規格可從 JSON 配置載入，也支援 hardcoded fallback
3. **兩層覆寫**：全域設定 → 逐筆 overrides（UI SidePanel 提供）
4. **Builder Pattern**：統一的 `add_pipe_entry()` / `add_plate_entry()` 等建立函數
5. **VBA 相容**：解析邏輯保持與原 VBA 版本一致（管徑格式轉換等）
6. **Signal/Slot**：PyQt6 的 `pyqtSignal` 驅動 UI 更新

---

## 十一、資料流總覽

```
使用者輸入支撐編碼 ("01-2B-05A")
        │
        ▼
    parser.py 拆解字串
        │
        ▼
    calculator.py 分派到 type_01.calculate()
        │
        ├─ parser: 解析各段
        ├─ data/pipe_table: 查管件規格
        ├─ data/m42_table: 查底板規格
        ├─ pipe.py: 建立管件 Entry
        ├─ plate.py: 建立鋼板 Entry
        ├─ bolt.py: 建立螺栓 Entry
        └─ m42.py: 建立底板組件
        │
        ▼
    AnalysisResult (含多個 AnalysisEntry)
        │
        ├─→ UI 表格顯示
        ├─→ Excel/CSV/PDF 匯出
        │
        ▼
    material_summary.aggregate() 彙總
        │
        ▼
    MaterialSummary (採購清單)
        │
        ▼
    cutting_optimizer.optimize_cutting() 下料最佳化
        │
        ▼
    CuttingPlan (切割方案 + 餘料 + 使用率)
        │
        └─→ Excel 雙表匯出
```

---

## 十二、如何新增一個 Type

1. 在 `data/` 新增 `typeXX_table.py`（若需要專用查詢表）
2. 在 `core/types/` 新增 `type_XX.py`，實作 `calculate(fullstring, ...)` 函數
3. 在 `calculator.py` 的 `_register_types()` 中加入映射：`"XX": type_XX.calculate`
4. 在 `configs/type_catalog.json` 加入 Type 資訊
5. （可選）在 `docs/types/` 加入 Markdown 文件

---

*此文件由 Copilot 自動產生，作為專案架構參考。最後更新：2026-04-20*
