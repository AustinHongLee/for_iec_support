# Type Variant Overlay 規格

本資料夾是設計公司／專案差異設定的預留落點。目前刻意不放置任何 overlay 資料，也尚未啟用合併引擎；啟用前置條件見 [`docs/裁決_B3_2026-06-22.md`](../../../docs/裁決_B3_2026-06-22.md) §6。

## 命名慣例

- overlay 檔名：`type_XX__<company>.json`，例如 `type_01__acme.json`
- `variant_id`：`XX@COMPANY`，例如 `01@ACME`
- alias key：`type_XX@company`，例如 `type_01@acme`；格式與 `configs/code_aliases.json` 一致

## Overlay schema 範例

以下範例保留原方案書的完整 schema 形狀，僅供未來實作與資料建檔時對照；它不是目前可載入的設定檔。

```jsonc
// python_app/configs/variants/type_01__acme.json
{
  "schema": "type-variant/1",
  "base_type_id": "01",                 // 形狀來源：沿用 type_01 的 calculator 與結構
  "variant_id": "01@ACME",              // 本變體的唯一識別
  "source": {                            // 這份差異是誰、哪個專案
    "design_company": "ACME Engineering",
    "project": "P-2026-樂工",
    "drawing_no": "ACME-PS-01 Rev.A"
  },
  "merge": "deep",                       // overlay 有的欄覆寫 base，沒有的沿用 base
  "code_alias_ref": "type_01@acme",      // 對應 configs/code_aliases.json 的 key
  "overrides": {                          // 只寫「和 base 不一樣」的部分
    "h_limit": 1800,
    "designation_format": {
      "pattern": "{vendor}-{shape}-{line_size}-{H_code}",
      "example": "ACME-PS01-200-12",
      "fields": {
        "vendor": "ACME",
        "shape": "PS01",
        "line_size": "管線尺寸(mm)",
        "H_code": "H 高度(×100)"
      }
    },
    "table_replace": [                    // 與 base 不同時整表替換
      { "line_size": 2, "pipe_size": "1-1/2", "schedule": "SCH.80", "L": 75 },
      { "line_size": 3, "pipe_size": "2", "schedule": "SCH.40", "L": 96 }
      // …目標公司的完整 L 表
    ]
  },
  "data_updated_at": "2026-06-18",
  "data_update_note": "ACME 專案首版，L 表依 ACME-PS-01 Rev.A 轉錄"
}
```

## 合併規則

- `overrides` 內的純量與物件採 deep-merge；overlay 未提供的欄位沿用 base。
- `table_replace` 一律取代整張 base 表，禁止依列或依儲存格混併，以免新舊版本資料同時參與計算。
- 合併結果必須通過嚴格 config 驗證後才能交給 calculator；不得回傳半套設定。

## 第一版安全限制

第一版 overlay 只准覆寫常數與表格，不准覆寫公式或表達式。特別是 pipe-shoe spec 目前存在以 `eval` 執行的表達式；任何外部資料都不得成為可執行碼。若未來完成 AST 白名單求值器與相應安全測試，才可另案評估解除限制。

上方 `designation_format` 是從原方案書直接保留的未來 schema 範例，不代表第一版合併引擎會接受該結構欄位；第一版允許欄位須由實作時的 schema 白名單明確定義。
