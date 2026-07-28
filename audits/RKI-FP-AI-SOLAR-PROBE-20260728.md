# RKI-FP-AI-SOLAR 探針執行（2026-07-28）

> **性質**：[I] 短 audit；不創設 [N]。  
> **題**：「依第一性原理如何使用AI模型來強化太陽能材料研發技術核心？」  
> **硬邊界**：`NHC-keep`／`FZ-keep`／≠`PME-XDOM-SOLAR`

## 一、探針

| probe_id | kind | 狀態 |
|---|---|---|
| `RKI-AI-SOLAR-RD` | `kh_x_kh` | upsert active |
| `RKI-FP-AI-SOLAR` | `principle_x_rd` | upsert active（主探針） |

`knowhow_interaction_probe` **active=14**。migrate：`scripts/migrate_knowhow_interaction_probe_ddl.py --apply`／`--selftest` 綠。

## 二、顧問路徑

| 步驟 | 結果 |
|---|---|
| glossary | CJK 問句 → `None`（無寫死擴詞） |
| `retrieve_all`（CJK） | 混入哲學 works（傳習錄／王陽明）＋`solar_rd` 目錄碎片＋`decision_sciences` 噪音 |
| `advise` HTTP `:8399`（qwen3:8b） | guard **pass**；citations=2；回覆偏心學類比（**非**材料 ML 主軸） |
| EN／關鍵字庫內 | `solar_materials` 句面含 ML／DFT／first-principles 關鍵字 **224**；檢索可命中 perovskite×SCAPS×ML 等 |

## 三、引文厚度（誠實）

| 層 | 評估 |
|---|---|
| 太陽能×ML／DFT 語料 | **有**（`solar_materials` 為主；非空） |
| CJK「第一性原理」組答路徑 | **薄／偏題**（哲學詞面搶命中） |
| 可宣稱「庫內實證完備技術核心清單」 | **否**（且 NHC 禁寫死清單） |

## 四、邊界

- 零 FinMind／FRED  
- 未開 `PME-XDOM-SOLAR`  
- 產生＝探針＋`advise`／檢索；答案非 SSOT  
