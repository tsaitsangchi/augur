---
status: checkpoint
series: archive
date: 2026-08-06
slug: b1-b3-p6-other-h-mstop-standing
depends_on:
  - audits/CORE-B1-INCREMENTAL-EXECUTED-20260805.md
  - audits/DAILY-ASOF-B3-P2-LIVE-20260805-EXECUTED-20260805.md
  - audits/POST-CLOSE-DAILY-ASOF-standing-go-ADOPTED-20260805.md
  - audits/P6-OTHER-H-FIT-20260804-EXECUTED-20260806.md
  - audits/S3-MACRO-STOCK-M-STOP-ACCEPTED-20260805.md
---

# ARCHIVE-CHECKPOINT｜B1＋B3＋P6 other-H＋M-stop＋standing · 2026-08-06

> **授權**：Steward「更新全部檔案上傳 github 並做封存點」  
> slug＝`b1-b3-p6-other-h-mstop-standing`  
> **硬邊界**：無 cron／無 SIM-apply／未撤 NF-pause／β5／M-stop；H82 ghost 未 train。  
> **self-reported（#32a）**。

## 1. 納入（本封主軸）

| 類 | 路徑／摘要 |
|---|---|
| **B1** | `core_gate.build_universe_asof_incremental`＋`build_core_universe.py --incremental`；EXECUTED＠08-05 |
| **B3** | `scripts/run_daily_asof_predict.sh`；LIVE＠**2026-08-05** RC=0（core n=285） |
| **Ops** | post-close daily asof 設計＋**standing GO** 採納；runbook 更新（B1／B3） |
| **P6** | FREEZE→08-04（H20／H60 既封）；**other-H** fit 40／82／120；emit＠08-05＝H40／H120（H82 ghost） |
| **S3** | 軌 M VERIFY keep_staged → **M-stop**；macro_stock 碼／contract 帳 |
| **S4** | NF-pause／β5_stop 接受帳仍帶入（未撤） |
| **Adv** | 相對 TopN／絕對方向誠實切片＋`advise`／`payload`／`relevance` 碼 |
| **監看** | ack_wait／A ping_later armed＠08-06（價頂仍 08-05；B3＠08-06 候 A） |

## 1b. WM.36 修閘（本封）

- `macro_stock`：PriceAdj／Info 經 `resolve_sql`；市報改 PriceAdj TAIEX.close（不直綁 TRI）
- `build_macro_stock_candidates.py`：補「執行指令矩陣」

## 2. 明確不納／未做

- systemd timer／`install_cron`  
- sim `--apply`；撤 NF-pause／β5／M-stop  
- H82 `train_ranker`（artifact ghost）  
- Dividend／wide dim-sync；graph_edge rebuild（asof 仍 06-30）  
- 假關確立級（dgate／econ 誠實標籤保留）

## 3. 產品錨（封存時點 ≈2026-08-06 早晨）

- 價／fv／core／pp H20／H60 頂＝**2026-08-05**  
- Adv 2330 H20 as_of＝**2026-08-05**；econ H20＝`dead`／H60＝`thin_unestablished`  
- P6 other：`platt_RankRidge_h{40,82,120}_asof2026-08-04_g0fb5c95`

## 4. Tag／SHA（封後填）

- commit：`68abfdda01971ee1e91dc406308a241847384bcc`
- tag：`archive-20260806-b1-b3-p6-other-h-mstop-standing`
- remote：`https://github.com/tsaitsangchi/augur`
