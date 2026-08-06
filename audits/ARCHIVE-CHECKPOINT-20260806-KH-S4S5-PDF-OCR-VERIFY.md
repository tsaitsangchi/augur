---
status: checkpoint
series: archive
date: 2026-08-06
slug: kh-s4s5-pdf-ocr-verify
self_reported: true
---

# ARCHIVE-CHECKPOINT｜KH 閉環＋PDF-C OCR＋S4／S5 驗証矩陣 · 2026-08-06

> **授權**：Steward「更新全部檔案上傳到 github…並做封存點」。  
> **硬邊界**：FZ／GATE-keep；**無** sim `--apply`；**無** cron B3 假跑；NF-pause／M／β5 **未撤**；KH AUTO-LIFT **預設 off**；web／dialog **裸 approve 禁**；T2＝系統源 only。  
> **LIVE 錨（封時）**：PriceAdj 頂 **2026-08-05**；#1 watcher 候 **08-06**；`evaluated_pass=0`；H20 `econ=dead`。

## 1. 納入（本波主軸）

| 軌 | 代表 |
|---|---|
| **KH 閉環** | readout／content-title resolve；compact stepwise；concordance catch-up；bare-title UI；KH0 auto-lift 計畫＋wire（預設 off）；KH0–KH9 專案計畫 |
| **PDF-C OCR** | `fileparse.ocr_pdf_pages`；`backfill_pdf_ocr.py`；acquire `--ocr`；P0 APPLY＋KIP 帳戶 |
| **S4／S5 驗証** | 其他模型矩陣 ADOPTED；**V5** OOS 輕驗 EXECUTED；**V1·H60** 三 seed EXECUTED（M1 不升格） |
| **開問題∥** | OPEN-1-2-3 tick；PHASE2 #7／#8／#9 候 A 文件；GRAPH-CONSUME probe；r10 刀板刷新 |
| **T2** | AI-SOURCE-APPROVE T2 GO／EXECUTED（系統源） |

## 2. 碼／脚本（摘要）

- `src/augur/knowledge/{readout,fileparse,auto_admit,answer_auto_lift,compact_answer}.py`
- `src/augur/advisor/{advise,prompt,ollama}.py`
- `scripts/{backfill_pdf_ocr,kh0_answer_auto_lift,migrate_kh0_answer_lift_log_ddl,acquire_local_files,build_concordance,run_knowhow_auto_admit,serve_advisor_openai}.py`
- 計畫／帳：`reports/augur_{local_ai_kh_loop_*,pdf_c_ocr,s4_other_model_verify_matrix,kh0_*}*_20260806.md`＋對應 `audits/*-20260806.md`

## 3. 明確不納／未做

- B3＠08-06（價未 READY → **不假跑**）  
- `S4-V1` H20／全表；`LOOP-S5-TO-S4-OPT-run`  
- 撤 NF-pause／新族 train；C1 EXPAND 放量；sim `--apply`  
- 默開 KH AUTO-LIFT 生產旗  

## 4. Tag／SHA（封後填）

- commit：`待填`
- tag：`archive-20260806-kh-s4s5-pdf-ocr-verify`

*候 commit／push。*
