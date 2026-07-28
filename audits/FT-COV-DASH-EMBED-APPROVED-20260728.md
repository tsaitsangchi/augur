# FT-COV-DASH＋FT-COV-EMBED 拍板登錄（2026-07-28）

> **性質**：拍板登錄（[I]；不創設 [N]）。  
> **計畫**：`reports/augur_knowledge_fulltext_coverage_plan_20260728.md`  
> **hugo／Steward 對話拍板原文（逐字）**：`FT-COV-DASH`＋`FT-COV-EMBED`  
> **簽名誠實註記**：本檔由 agent 依 Steward 拍板繕寫登錄；決策者＝hugo、繕寫者＝agent，二者分立。

## 一、近程採納範圍（本輪）

| 碼 | 含義 | 本輪 |
|---|---|---|
| **`FT-COV-PLAN`（近程）** | 計畫書 what／分桶／階段／非目標——**僅 P0＋P1 近程採納** | ✅ 以 DASH＋EMBED 明示開工一併登錄 |
| **`FT-COV-DASH`** | P0：gov 儀表＋分桶腳本（零外部 API） | ✅ 核准並執行 |
| **`FT-COV-EMBED`** | P1：庫內 `ft_no_sent`／`sent_no_emb` 補洞 | ✅ 核准並執行 |
| **`HAR-ext`** | 外部 OA／fetch 窄窗或放量 | ❌ **不含**（另句） |
| **`FT-COV-BATCH`** | P3 批次 | ❌ 不含 |
| **清 pending 放量** | 猛抓 metadata pending 全文 | ❌ 不含 |
| **`FZ-keep`** | FinMind／FRED 維持凍結 | ✅ 預設維持 |

## 二、驗收錨（對齊計畫 §3.2／§5／§7）

### DASH（P0）

- gov 每 domain 顯示：`items`／`answerable`／`terminal_blocked`／`pending`
- **覆蓋（可答）**＝`answerable / items`；另列 **終態完成率**＝`(answerable + terminal_blocked) / items`
- 標題／文案不得把 `length>200` 舊式全文率單獨當「可檢索覆蓋」headline
- 固化唯讀腳本 `scripts/report_knowledge_fulltext_buckets.py`（頁面數字可對腳本）
- erp_tiptop：可答≈100% 可見（舊式 ~7% 假低不得再當 headline）

### EMBED（P1）

- 掃並補 `ft_no_sent`／`sent_no_emb`（chemistry 等優先；resume-safe；本地）
- erp_tiptop 已全 embed → **勿假重做**
- **禁止**：`skip_license`／`skip_no_oa`／blocked 灌成全文；素養層進預測；他域進化閉環；FinMind／FRED

## 三、硬邊界核對（開工前）

| 項 | 本輪 |
|---|---|
| 零 FinMind／FRED；不解凍 | ✅ |
| 不把 blocked 洗成全文 | ✅ |
| 不開太陽能↔儲能他域進化閉環 | ✅ |
| 素養層不進預測管線 | ✅ |
| #1／#8／全文三軌 | ✅ |

## 四、執行落點（後填 CLOSED／STATUS）

- 執行／數字：`audits/FT-COV-DASH-EMBED-CLOSED-20260728.md`（或同日 STATUS）
- HANDOFF 一句更新
- 封存：`bash scripts/archive_push.sh --slug ft-cov-dash-embed`
