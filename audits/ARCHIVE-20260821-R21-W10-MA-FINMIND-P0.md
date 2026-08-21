---
status: archive_checkpoint
date: 2026-08-21
kind: archive_checkpoint
tag: archive-20260821-r21-w10-ma-finmind-p0
sha: pending
remote: https://github.com/tsaitsangchi/augur
auth: "Steward：更新全部檔案上傳到 https://github.com/tsaitsangchi/augur 並做封存點"
prior: archive-20260820-r21-hist-wf-ridge-pb-close
self_reported: true
layer: "[I]"
---

# ARCHIVE · 20260821 · W10／MA10／MA20／FinMind P0／Sponsor 09-14

date: 2026-08-21  
kind: archive_checkpoint  
tag: `archive-20260821-r21-w10-ma-finmind-p0`  
sha: pending（commit 後回填）  
remote: https://github.com/tsaitsangchi/augur

上一封存：`archive-20260820-r21-hist-wf-ridge-pb-close`（commit `5eb1cd2`；回填 `db9ce0f`）。

## 範圍（本封存）

- **LIVE**：價頂＝**2026-08-20**。出門仍 **H20+H60** RankRidge。**08-21＝假 B3**。未 SERVE-SWAP、未 promote、未改 L0。
- **HIST-RIDGE-WF**：全交易日 asof=D 八窗河仍在跑（進度快照 `audits/HIST-RIDGE-WF-ALLDAYS-PROGRESS.json`）。本封不聲稱已灌到價頂。
- **RIDGE-THEN-PB 平行做多**（各表、各鎖、不覆寫 v1）：
  - W10：四閘＋八窗 `|路徑％|≤10` → `ridge_then_pb_long_w10_*`
  - MA10：均線多頭＋均價差≤10% → `ridge_then_pb_long_ma10_*`
  - MA20：均線多頭＋均價差≤20% → `ridge_then_pb_long_ma20_*`
  - v1 做多／做空監看仍在。條件≠可交易。
- **FinMind free**：計畫 `reports/augur_finmind_free_rankridge_plan_r21_20260821.md`。P0 探針＠08-20＝仍 **0/6000**、三張 by-date（scenario A）。**不是** free 終局。
- **Sponsor 到期**（帳號頁）：**2026-09-14**。到期前不改 L0；P0′＝錶 `api_request_limit≠6000` 當日重探。
- **程式**：`ma_stack.py`；`run_ridge_then_pb_long_{w10,ma10,ma20}.py`；`probe_finmind_free_rankridge.py`；store／四閘擴 W10。

## 不做（本封不假裝已做）

- 不假 B3＠08-21；不把全交易日八窗河說成已灌完
- 不 SERVE-SWAP／不 promote／不改 standing 20,60
- 不改 L0／cron；不解凍 FinMind；不 93 表
- 不 sim `--apply`；不 E5；不 dump canonical-31
- 不把分數／路徑％／收盤買進當可交易或未來漲跌幅
- 不把 Cursor canvases、`.env`、`models_artifacts`、dump／tar 推進 git

## 驗收

- `git rev-parse HEAD`＝回填前之封存 commit（tag 打在該 commit）
- `git show archive-20260821-r21-w10-ma-finmind-p0` 可取註解
- origin/main 已含本 commit；tag 已 push
