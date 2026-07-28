# KH-XDOM-PLAN＋KH-XDOM-S01 拍板登錄（2026-07-28）

> **性質**：拍板登錄（[I]；不創設 [N]）。  
> **計畫**：`reports/augur_knowhow_cross_domain_advisor_plan_20260728.md`  
> **hugo／Steward 對話拍板原文（逐字）**：`KH-XDOM-PLAN`＋`KH-XDOM-S01`＋`PME-XDOM-NO`＋`FZ-keep`  
> **簽名誠實註記**：本檔由 agent 依 Steward 拍板繕寫登錄；決策者＝hugo、繕寫者＝agent，二者分立。

## 一、四碼效力

| 碼 | 含義 | 本輪 |
|---|---|---|
| **`KH-XDOM-PLAN`** | 採納整合計畫（跨域作答＋gov 覆蓋 ATA 設計）為藍圖 | ✅ |
| **`KH-XDOM-S01`** | 開工 **S0＋S1＋S1b**（診斷帳＋檢索去作答分域閘＋ATA 骨架；零市場 API） | ✅ 核准並執行 |
| **`PME-XDOM-NO`** | 近程**不做**異域進化閉環灌預測因子（孫子↔ERP／太陽能↔儲能等） | ✅ 鎖定 |
| **`FZ-keep`** | FinMind／FRED 維持凍結 | ✅ |

## 二、S01 範圍（對齊計畫 §5／§9）

| 階段 | 做 | 驗收錨 |
|---|---|---|
| **S0** | 固化 D1–D11；PG 分桶對帳；列「作答曾傳 domain=」呼叫點 | 數字可複現；呼叫點清單完整 |
| **S1** | 預設關閉 D3（`retrieve_items(domain=)` 不作答閘）；`retrieve_all`／`advise` 預設跨標籤；文件化 RBAC≠策展 | 孫子×企管類 query 授權夠時可多標籤／works 命中（或誠實缺料，非因 domain= 空） |
| **S1b** | ATA 骨架：`advance_knowledge_terminal.py` dry-run／有界 apply；**禁** approve／activate | dry-run 清單；system 觸 HUMAN_ONLY → FAIL |

## 三、非目標（本輪明示不做）

| 不做 | 理由 |
|---|---|
| S2 評測集／`KH-XDOM-EVAL` | 另碼 |
| S2b 外部 OA 放量／`KH-ATA-EXEC` | 另碼；骨架可 dry-run，不默認放量 |
| S3／S3b 相關度調參＋gov ATA 呈現／`KH-XDOM-QUAL` | 另碼 |
| 自動 `approve`／`activate`／`ratify` 來源 | 憲章 v1.41.0；唯人 |
| 異域進化閉環灌因子 | `PME-XDOM-NO` |
| 解凍 FinMind／FRED | `FZ-keep` |
| CJK glossary hardcode→DB 入憲 | 另計畫 `augur_no_hardcode_*`；S01 不改 [N] |
| 鬆 license／全文三軌／素養進預測 | 紅線 |

## 四、執行落點（後填 CLOSED／STATUS）

- 執行／實測：`audits/KH-XDOM-S01-CLOSED-20260728.md`
- HANDOFF 一句
- 封存：`bash scripts/archive_push.sh --slug kh-xdom-s01`
