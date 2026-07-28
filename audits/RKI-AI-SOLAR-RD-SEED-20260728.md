# RKI-AI-SOLAR-RD 種子追加（2026-07-28）

> **性質**：[I] 短 audit；不創設 [N]。  
> **上位**：`RKI-PLAN`＋`RKI-SCOPE-ALL-KH`＋`NHC-keep`＋`FZ-keep`  
> **計畫**：`reports/augur_raw_knowhow_interaction_probe_plan_20260728.md`  
> **Steward 追加原文**：「AI模型進化來強化太陽能材料研發技術」  
> **不含**：`RKI-S2`／`PME-XDOM-SOLAR`／`PME-XDOM-AI-PREDICT`／FinMind／FRED／入憲

## 一、效力解讀

| 項 | 結論 |
|---|---|
| **落點** | `knowhow_interaction_probe` INSERT；屬 `RKI-SCOPE-ALL-KH` |
| **軸** | AI 模型進化 × 太陽能材料研發技術（可與第一性原理變體交叉） |
| **NHC-keep** | 禁 hardcode 太陽能／AI 專答樹；產生仍 advise／glossary |
| **≠ PME-XDOM-SOLAR** | 本輪**不**開未拍的太陽能→台股預測因子鏈；投資 map 須**另拍** |
| **≠ PME-XDOM-AI-PREDICT** | 正交：彼＝AI×**投資預測**；本＝AI×**太陽能研發**；勿混同一 map |

## 二、新增 probe_id

| probe_id | 軸 | kind |
|---|---|---|
| `RKI-AI-SOLAR-RD` | AI／ML 模型進化 × 太陽能材料研發技術 | `kh_x_kh` |
| `RKI-FP-AI-SOLAR` | 第一性→AI 進化 × 太陽能研發（optional 交叉） | `kh_x_kh` |

表：`knowhow_interaction_probe`；migrate＝`scripts/migrate_knowhow_interaction_probe_ddl.py --apply`；種子目標 **active≥14**。

## 三、硬邊界核對

| 項 | 結果 |
|---|---|
| 零 FinMind／FRED（`FZ-keep`） | ✅ |
| 無領域專答樹（`NHC-keep`） | ✅ |
| 不開 `PME-XDOM-SOLAR`／`PME-XDOM-AI-PREDICT` | ✅（另拍） |
| 不改 [N] | ✅ |

## 四、變更檔

- `scripts/migrate_knowhow_interaction_probe_ddl.py` — 種子＋selftest →14
- `reports/augur_raw_knowhow_interaction_probe_plan_20260728.md` — §1.2／拍板欄
- `audits/RKI-PLAN-APPROVED-20260728.md`／`audits/RKI-S01-CLOSED-20260728.md` — 補記
- `HANDOFF.md` — 一句
- 本檔

## 五、另拍條件（預設否）

若要將 AI×太陽能研發寫進 PME investment map／台股特徵鏈 → 須明示 **`PME-XDOM-SOLAR`**（或等價）並說明與市場特徵之可證偽對映。本輪預設 **不開**。
