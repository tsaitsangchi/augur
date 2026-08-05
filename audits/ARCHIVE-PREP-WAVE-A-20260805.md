---
status: prep
series: archive
depends_on:
  - audits/ARCHIVE-CHECKPOINT-20260805-DIRFAMILY-P6-S4B-ALOG-BETA2.md
---

# 封存準備清單（波次 A · 2026-08-05）— **未** commit／push

> **授權**：Steward AskQuestion `wave=wave_a`（準備）＋`next=1_archive`（封存 push）。  
> **CLAUDE #14**：本輪已授封存 push → 走 `archive_push.sh`。  
> **self-reported（#32a）**。

## 相對 HEAD（`c268b54`／tag `archive-20260805-dirfamily-p6-s4b-alog-beta2`）

### 修改（M）

| path | 要旨 |
|---|---|
| `src/augur/advisor/relevance.py` | PRED-KH 意圖（TopK／單股／大盤） |
| `src/augur/advisor/payload.py` | TopK／單股 payload＋`tw.stock_display_name` |
| `src/augur/advisor/oai_compat.py` | 分派 B2＞C |
| `src/augur/advisor/advise.py` | PRED-KH 不短路＋**picks_skip_A** |
| `src/augur/advisor/prompt.py` | 大盤拒答 enrichment |
| `scripts/serve_advisor_openai.py` | 啟動列印對齊 PRED-KH |
| `scripts/train_classical_ts.py` | WM.36→`tw.daily_bar_adjusted` |
| `scripts/probe_classical_ts_phase0b.py` | 同上 |
| `audits/S3-BETA-BETA2-EXECUTED-20260805.md` | #11 暫停（KeyboardInterrupt）追記 |

### 未追蹤（??）

| path | 要旨 |
|---|---|
| `audits/ADVISOR-PRED-KH-AUTOREL-TOPN-EXECUTED-20260805.md` | PRED-KH 執行帳 |
| `audits/WM36-CLASSICAL-TS-REGISTRY-EXECUTED-20260805.md` | classical TS registry |
| `audits/WM36-STOCK-DISPLAY-NAME-EXECUTED-20260805.md` | display_name binding 104 |
| `audits/MC-ASOF-20260804-RERUN-20260805.md` | MC asof 滾動（若本輪要一併封） |
| `reports/augur_advisor_predict_as_knowledge_plan_20260805.md` | PRED-KH 計畫 |
| `audits/ARCHIVE-PREP-WAVE-A-20260805.md` | 本檔 |
| `audits/WM36-PRICEADJ-INVENTORY-20260805.md` | #9 盤點 |
| `audits/S3-BETA5-STOP-ACCEPTED-20260805.md` | β5 停接受 |
| `reports/augur_s3_beta5_stop_and_beta2_pause_plan_20260805.md` | #5 |
| `reports/augur_s4_next_family_adapter_plan_20260805.md` | #8 |
| `audits/ADVISOR-PICKS-SKIP-A-EXECUTED-20260805.md` | picks_skip_A |
| `reports/augur_advisor_picks_skip_heavy_retrieve_plan_20260805.md` | picks_skip 計畫 |
| `audits/ARCHIVE-CHECKPOINT-20260805-PRED-KH-WM36-PICKS-SKIP.md` | 本封存點 |

## 建議 commit 訊息（待授）

```
2026-08-05 archive: PRED-KH / WM36 classical+display_name / wave-A plans

Co-Authored-By: Claude ...
```

## 硬邊界

- **不** push／**不** `--no-verify` 除非閘紅且 Steward 明示  
- DB 概念卡 `tw.stock_display_name`（binding 104）已落地——碼與 audit 須同封  

*prep only。*
