# IEC 管架支撐分析工具 — 風險報告與優化前瞻建議

> 分析日期：2026-06-15
> 分析模型：DeepSeek V4 Pro（Deep Code）
> 專案總規模：~34,000 行 Python／60 個 Type 計算器／67 個支援 Type
> 測試狀態：validate_tables.py ✅ / pytest 40 個 ✅ 全綠

---

## 一、總體狀態一覽

| 指標 | 數值 | 健康度 |
|------|------|--------|
| 支援 Type 總數 | 67 | 🟢 全覆蓋 |
| 計算器實作率 | 67/67（100%） | 🟢 |
| JSON config 覆蓋 | 39/67（58%） | 🟡 |
| 共用引擎覆蓋 | 7/67（pipe_shoe） | 🟢 |
| **Calculator-only 技術債** | **21 個 Type** | 🔴 |
| Component table 模組入口 | 71/71（100%） | 🟢 |
| Component table lookup-ready | 19/71（27%） | 🔴 |
| Component table metadata-only | 49/71（69%） | 🔴 |
| N-series（Cold Support） | 29/29 metadata-only | 🔴 |
| validate_tables.py | 2,866 行，全部 PASS | 🟢 |
| pytest 測試案例 | 40 個，全部 PASS | 🟢 |
| 測試檔案數 vs Type 數 | 11 vs 60+ | 🔴 |
| 未提交變更 | 8 modified + 2 untracked | 🟡 |
| Material canonical_id 未管理 | 21 個 entry | 🟡 |

---

## 二、🔴 高風險項（建議立即或本月內處理）

### 🔴 風險 1：21 個 Calculator-Only Type — 數據與邏輯混雜

**現狀：** 以下 Type 的所有尺寸表、分表邏輯、查表規則寫死在 `python_app/core/types/type_XX.py` 程式碼中，無對應的 `configs/type_XX.json`：

```
03, 05, 06, 16, 24, 25, 26, 27, 28,
30, 31, 32, 33, 34, 35, 36, 37, 47, 49, 61, 78
```

**為什麼是風險：**

1. **圖面改版時改數據要動程式碼**：任何尺寸調整都需開發者介入，無法由工程師直接改 JSON
2. **無法獨立稽核數據版本**：`data_updated_at` / `data_update_note` 機制無法套用
3. **UI 無法顯示數據來源**：Type 總覽頁面看不到「數據從哪來、何時更新」
4. **新人接手成本高**：要從幾百行程式碼中讀懂查表規則，而非從結構化 JSON 一眼看懂

**稽核工具確認：**

```
$ python python_app/tools/audit_table_json_coverage.py
calculator-only risk: 03, 05, 06, 16, 24, 25, 26, 27, 28,
                      30, 31, 32, 33, 34, 35, 36, 37, 47, 49, 61, 78
```

**建議遷移順序（依業務影響排序）：**

| 優先 | Type | 理由 |
|------|------|------|
| 1 | 49 | 有 M-11/M-12/M-41 相依，目前仍是 custom estimate |
| 2 | 36, 37 | Trunnion 群組，使用頻率高 |
| 3 | 25, 26, 27, 28 | Portal frame 群組，結構相似可一起遷移 |
| 4 | 30, 31, 32, 33, 34 | 懸臂框群組 |
| 5 | 35 | 托條群組 |
| 6 | 03, 05, 06, 16, 24, 47, 61, 78 | 各別評估 |

**遷移方法（依 TYPE_DEFINITION_CONTRACT.md §「Refactoring Existing Flat Types」）：**

```
1. 先加 golden case（確保行為鎖定）
2. 提取表格數據 → configs/type_XX.json
3. 建立 data/typeXX_table.py bridge（保持 API 相容）
4. 保持計算器行為不變
5. 跑 validate_tables.py 確認
6. 更新 docs/types/type_XX.md
```

---

### 🔴 風險 2：Component Table 實質可算率僅 27%

**現狀：**

| 狀態 | 數量 | 占比 | 可否精算 |
|------|------|------|----------|
| `lookup-ready` | 19 | 27% | ✅ 可查表計算 |
| `partial-lookup` | 3 | 4% | ⚠️ 部分欄位可查 |
| `metadata-only` | 49 | 69% | ❌ 僅有 PDF 來源，無尺寸表 |

M-series 還好（重要零件多已轉錄），但 **N-series（Cold Support）全線 29 個 table 都是 metadata-only**，完全無法精算。

**直接受影響的 Type：**

| Type | 缺失的 Component | 目前影響 |
|------|-----------------|----------|
| 49 | M-11, M-12, M-41 | 使用 custom estimate，非精算 |
| 62（lower figures） | M-3, M-31, M-33 | 拋出 missing-table warning |
| 62（lower clamp） | M-8, M-9, M-10 | metadata-only，無法查尺寸 |
| 全部 Cold Support | N-1 ~ N-28 | 完全無法計算 |

**建議（同 COMPONENT_TABLE_STATUS.md §「後續升級順序」）：**

```
Priority 1: M-11 / M-12 / M-41  →  解救 Type 49
Priority 2: M-3 / M-31 / M-33   →  消除 Type 62 warning
Priority 3: M-8 / M-9 / M-10    →  完成 Type 62 lower clamp
Priority 4: N-series 第一批     →  啟動 Cold Support
Priority 5: M-55 reviewer spot  →  驗收 M-55 重量估算
```

---

### 🔴 風險 3：鋼板命名標準化 — 1,365 行討論，0 行實作

**現狀：** `python_app/docs/STEEL_PLATE_NAMING_PLAN.md` 經過四個 AI 模型（Deep Code、Claude、Grok、Codex）共 14 節的深度辯論，已在 §12 達成最終決議：

- **name 格式**：`{family}_{role}_[{variant}_]{shape_spec}`
- **stock_id**：`PL-{6碼hash}`（`AnalysisEntry` 獨立欄位，不塞進 name）
- **variant 寫法**：選 A（獨立 variant 段，保護 `ComponentRole` 白名單）
- **shape_kind 前綴**：`rect_` / `lugz_` / `arc_` / `saddle_` 顯式標記
- **材質 / rev / 專案號**：一律不進 name（獨立欄位或 PDM 層管理）

**但目前程式碼端完全未開始實作。** 現有 BOM 中 plate name 仍是：

```
Plate_a_無鑽孔 / Plate_F / LUG PLATE TYPE-C / PLATE / COVER_PL ...
```

**風險：**

1. CAD 師傅看 BOM 無法一眼辨識板件歸屬與尺寸
2. 跨 Type 搜尋無法區分同名板（如 `LUG PLATE TYPE-C` 出現在 36/39/43/45/47 等多個 Type）
3. 異形板放樣尺寸（Type 59 Lug Plate）藏在 `GeometryHints.shape_spec` 中，但 `name` 欄位仍是舊格式
4. 每延期一個月，`validate_tables.py` 中鎖定舊 name 的 golden case 就更多，未來遷移成本更高

**建議實施步驟（依 §12.6）：**

```
Step 0:   建 tests/fixtures/plate_name_migration.json（新舊 name 對照表）
Step 0.5: 產出 docs/plate_shape_reference.md  ← 🚧 阻擋後續步驟
Step 1:   pytest baseline（確認舊 name 現狀全綠）
Step 2:   改 plate.py（build_plate_name + build_stock_id 輔助函式）
Step 3:   改 m42.py → 跑測試
Step 4:   逐 type 改 → 每改一個跑測試
Step 5:   切換 fixture 為新 name ground truth
Step 6:   處理 D 區直接賦值項（統一走 add_plate_entry）
Step 7:   Pipe Shoe JSON configs（Type 52~67 的 name 在 JSON 中）
Step 8:   Inventor 參數對接驗證
```

---

## 三、🟡 中等風險（建議排入季度內計畫）

### 🟡 風險 4：測試覆蓋密度過低

**現狀：**

| 指標 | 數值 |
|------|------|
| pytest 測試案例 | 40 個 |
| 獨立 test file | 11 個 |
| 支援 Type 數 | 67 個 |
| 平均每 Type 測試案例 | < 1 個 |
| validate_tables.py | 2,866 行（集中式 smoke tests） |

大多數 Type 只有 `validate_tables.py` 中的一兩個 smoke case，缺乏邊界條件、錯誤輸入、fallback 行為的獨立測試。

**風險：** 重構 calculator-only Type 或實施鋼板改名時，regression safety net 太薄。

**建議：**

1. 每個 calculator-only Type 遷移到 JSON 時，**同步添加 3~5 個 pytest case** 到獨立 `tests/test_type_XX.py`
2. 測試至少涵蓋：
   - 最小 pipe size 輸入
   - 最大 pipe size 輸入
   - 邊界 fallback row（如 M42 的 0.5" → 1" fallback）
   - 預期警告產出
   - 預期 BOM 結構（name / spec / material / quantity）

---

### 🟡 風險 5：Material Canonical ID 未完整覆蓋（21 個 entry）

**現狀：** `validate_tables.py` Phase 2L-A 軟鎖定回報 21 個 entry 使用 legacy string material path，缺乏 `material_canonical_id`：

| 來源 Type | 問題 Material | Entry 數 |
|-----------|--------------|----------|
| 03 | SUS304 | 1 |
| 19 | A36/SS400 | 1 |
| 48 | A36/SS400 | 1 |
| 49 | A36/SS400 | 2 |
| 52 | A36/SS400 | 2 |
| 57 | Carbon Steel | 2 |
| 59 | A283 Gr.C | 1 |
| 72 | Carbon Steel, SUS304 | 2 |
| 73 | A283-C, ASTM A229, Carbon Steel | 5 |
| 76 | Same as pipe / Carbon Steel | 1 |
| 77 | Same/similar to pipe | 1 |
| 78 | Carbon Steel | 1 |
| 79 | Carbon Steel | 1 |

**風險：**

- BOM 聚合時同材質可能因拼寫不同無法正規化（`A283 Gr.C` vs `A283-C` vs `A283 Gr.C`）
- 材質替換（cryo / high-temp service class）無法自動傳遞
- `material_summary.py` dedup 依賴材質字串完全匹配，不一致會導致同一塊板被拆成兩行

**建議：**

1. 所有新 Type 或重構 Type **必須走 `MaterialSpec`**（或至少 `canonical_material_id()`）
2. 21 個 legacy entry 逐步修正；不需要一次全改（可隨各 Type 的 calculator-only 遷移一起修）
3. 最終目標：0 個 `phase 2L-A` warning

---

### 🟡 風險 6：未提交變更累積

**現狀（`git status --short`）：**

```
M  AGENTS.md
M  pytest.ini
M  python_app/validate_tables.py
M  python_app/export/excel/calculation_sheets.py
M  python_app/export/excel/headers.py
M  python_app/export/excel/simple_exports.py
M  python_app/export/excel/weight_sheets.py
?? IEC_管架支撐分析工具_專案介紹.pptx
?? docs/
```

**風險：**

1. Excel export 層有 5 個檔案同時處於修改狀態，彼此可能有隱性相依
2. `docs/` 目錄在 repo 根目錄而非 `python_app/docs/` 下，結構不一致
3. `.pptx` binary 不適合放 Git（1.5MB），應考慮 Git LFS 或外部儲存

**建議：**

1. 提交或 stash 目前 working tree
2. 確認 `docs/` 目錄的定位：是新的頂層 AI 審閱報告區，還是應合併回 `python_app/docs/`？
3. `.pptx` 加入 `.gitignore` 或使用 Git LFS

---

### 🟡 風險 7：Shape 語義參考文件缺失（阻擋鋼板改名 Step 0.5）

**問題：** `STEEL_PLATE_NAMING_PLAN.md` 中所有 AI 審閱者一致認定 `docs/plate_shape_reference.md` 是鋼板改名計畫的前置阻擋項。沒有這份文件：

- `lugz_150x130x25x50x12t`（Type 59 L 型 Lug Plate）的 25 和 50 分別對應哪條邊？沒人知道
- 弧形板 `arc_ch400_s50_w180x12t` 的 `ch` / `s` / `w` 語義未定義
- CAD 師傅仍需口頭問人，改名的核心價值（「人看得懂」）無法實現

**目前狀態：不存在。**

**建議：**

- 以 Type 59 Detail Z 的 L 型 Lug Plate 作為第一個範本
- 每個 shape_kind（rect / lugz / arc / saddle）至少需要一張示意圖（mermaid 或截圖）
- 標註各維度符號（A / B / C / D / t / ch / s / w）對應的實際邊

---

## 四、🟢 低風險但值得關注

| 項目 | 說明 | 建議 |
|------|------|------|
| N-series（Cold Support） | 全系列 29 個 table metadata-only | 無短期需求可暫緩；待有 Cold Support 專案時再啟動轉錄 |
| Pipe Shoe JSON 中的 name | Type 52~67 plate name 寫在 JSON config 中，不在 Python | 改名 Step 7 時需特別處理 |
| `cutting_optimizer.py` | 已存在但成熟度未知，無專屬測試 | 補一個 smoke test |
| GUI `main_window.py` | 123KB / ~3,000 行 | 考慮拆分為多個 page/panel 模組 |
| 無 CI/CD | 沒有 GitHub Actions 或其他自動化 | 建議加一個最簡的 `pytest` + `validate_tables.py` workflow |
| `Module占存區` | 頂層目錄，用途不明 | 確認後清理或歸檔 |
| `analysis_result.xlsx` | Binary artifact 存在於 `python_app/docs/` | 移除或加入 `.gitignore` |

---

## 五、綜合優先序建議

```
🔴 優先 1（本月）：鋼板改名 Step 0 + 0.5
                  ─ 建 plate_name_migration.json fixture
                  ─ 產出 plate_shape_reference.md

🔴 優先 2（本月）：Calculator-only Type 遷移（前 5 個）
                  ─ Type 49（有 component 相依）
                  ─ Type 36, 37（trunnion 群）
                  ─ Type 25, 26（portal frame 群）

🔴 優先 3（下月）：Component table M-11/M-12/M-41 轉錄
                  ─ 讓 Type 49 從 custom estimate 升級為精算

🟡 優先 4（下月）：Material canonical_id 21 個 entry 清零
                  ─ 隨各 Type 重構一起修，不另排專項

🟡 優先 5（季度）：Component table M-3/M-31/M-33 + M-8/M-9/M-10
                  ─ 消除 Type 62 lower figures 警告

🟡 優先 6（季度）：鋼板改名 Step 1~8 完整實施
                  ─ 逐 Type 改 name、跑 pytest、切換 fixture

🟢 優先 7（遠期）：N-series Cold Support 第一批轉錄
🟢 優先 8（遠期）：CI/CD pipeline、GUI 拆分
```

---

## 六、前瞻性建議

### 6.1 建立 stock_id 機制

`AnalysisEntry.stock_id` 欄位已定義但從未被計算填充。鋼板改名時應同步實作 `build_stock_id()`：

```python
hash_input = (
    family, role.value, variant or "",
    round(A, 1), round(B, 1), round(t, 1),
    shape_kind, extra_shape_params,
    material_canonical_id,
)
stock_id = "PL-" + hashlib.sha1(repr(hash_input).encode()).hexdigest()[:6].upper()
```

這讓 Inventor / Vault 端有一個穩定的實體主鍵，與 name 字串脫鉤。

### 6.2 BOM 欄位拆分

目前 BOM Excel 只有一個 `name` 欄位承載所有資訊。建議匯出層增加結構化欄位：

`[Type | Role | Variant | A | B | C | D | t | Material | Name | Stock#]`

這對 CAD 師傅的排序 / 篩選 / Pivot 是革命性提升。Name 保留為 PartNumber，結構化欄位供採購與圖面管理使用。

### 6.3 Component Table Readiness 升級為 Field-Level

目前 table-level 的 `lookup_ready` 太粗糙。`docs/readiness_schema.md` 已定義 field-level 的 readiness matrix schema（`source` / `derived` / `estimated` / `missing`），但從 Phase 0A 至今未開始遷移。

建議：選一個 partial-lookup 的 table（如 M-5、M-6 或 M-7）做為 pilot，先升級為 field-level，驗證可行性後再逐步推廣。

### 6.4 CLI 介面

目前只有 PyQt6 GUI + Excel 匯出。未來若需 CI 整合或批次處理，建議暴露 headless CLI：

```bash
python -m python_app.cli analyze "51-1.1/2B" --json
python -m python_app.cli batch input.csv --output output.xlsx
```

### 6.5 多語言 i18n 預留

`notes_zh`、`display_remark` 等欄位已預留中文路徑。若未來有國際專案需求，可在 `GeometryHints` 加 `notes_en`，在 `set_remark()` 增加 locale 參數。

---

## 七、結論

**一句話總結：**

> 專案引擎跑得很穩（全部測試 PASS），但數據治理層（component table 轉錄、steel plate naming、calculator-only 遷移）有顯著的「文件 vs 程式碼」落差。這 21 個 calculator-only Type 和 49 個 metadata-only component table 是最需要投入的區域。鋼板命名標準化已經完成設計收斂（§12 拍板），缺的只是動手做。

**當前最該做的三件事：**

1. ✏️ 建 `tests/fixtures/plate_name_migration.json` + `docs/plate_shape_reference.md`
2. 🔨 開始提取前 5 個 calculator-only Type 的 JSON config
3. 📋 轉錄 M-11 / M-12 / M-41 component tables（解救 Type 49）

---

*報告結束 | 作者：DeepSeek V4 Pro（Deep Code） | 日期：2026-06-15*
