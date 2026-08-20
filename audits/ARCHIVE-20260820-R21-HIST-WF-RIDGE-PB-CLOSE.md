---
status: archive_checkpoint
date: 2026-08-20
kind: archive_checkpoint
tag: archive-20260820-r21-hist-wf-ridge-pb-close
sha: "5eb1cd28c71c22213bd16f73c5c3f9ab2e94b008"
remote: https://github.com/tsaitsangchi/augur
auth: "Steward：更新全部檔案上傳到 https://github.com/tsaitsangchi/augur 並做封存點"
prior: archive-20260819-b3-hist-slim-r20
self_reported: true
layer: "[I]"
---

# ARCHIVE · 20260820 · r21／asof=D 八窗河／做多收盤買／做空收盤賣

date: 2026-08-20  
kind: archive_checkpoint  
tag: `archive-20260820-r21-hist-wf-ridge-pb-close`  
sha: `5eb1cd28c71c22213bd16f73c5c3f9ab2e94b008`  
remote: https://github.com/tsaitsangchi/augur

上一封存：`archive-20260819-b3-hist-slim-r20`（commit `63752bb`；回填 `3bd1a37`）。

## 範圍（本封存）

- **LIVE**：價頂／fv／core＝**2026-08-19**。出門仍 **H20+H60** RankRidge（standing 未改八窗）。**08-20＝假 B3**（rc=3）。未 SERVE-SWAP、未 promote。
- **r21**：理解／憲章／執行板／精要讀序／HIST-RIDGE-WF 計畫入倉。
- **HIST-RIDGE-WF**：每個交易日 asof=D 重訓 RankRidge 八窗（標出場≤D）；河在跑、未聲稱已灌到價頂。進度快照見 `audits/HIST-RIDGE-WF-ALLDAYS-PROGRESS.json`。
- **RIDGE-THEN-PB 做多收盤買**：相對強 Top10 不剔除、回撤近→遠；過齊才寫 `ridge_then_pb_long_buy`（該日還原收盤）。條件≠可交易。
- **RIDGE-THEN-PB 做空收盤賣**：相對弱 Top10 不剔除、反彈近→遠；過齊才寫 `ridge_then_pb_short_sell`（該日還原收盤）。做空≠下單≠可融券。
- **PATH-HIT-LIFT**：P5 墓碑仍閉；不重開勝率河。
- **slim T6／T7**：PME leftover backup、sim evolution 專章草案搬入 `archive/slim-t6/`、`archive/slim-t7/`。
- **程式**：`train_ranker` 防洩漏；`baseline` 空 PIT 回退 panel；`label_realized_by`；`ridge_then_pb_store` 收盤帳；`run_hist_ridge_wf*`；`run_ridge_then_pb_long_buy.py`；`run_ridge_then_pb_short_sell.py`。

## 不做（本封不假裝已做）

- 不假 B3＠08-20；不把全交易日八窗河說成已灌完
- 不 SERVE-SWAP／不 promote／不改 standing 20,60
- 不 sim `--apply`；不 E5；不 dump canonical-31
- 不把分數／路徑％／收盤買進／收盤賣出當可交易或未來漲跌幅
- 不把做空名單當可融券
- 不把 Cursor canvases、`.env`、`models_artifacts`、dump／tar 推進 git

## 驗收

- `git rev-parse HEAD` = 回填後之 sha（tag 打在本封存 commit）
- `git show archive-20260820-r21-hist-wf-ridge-pb-close` 可取註解
- origin/main 已含本 commit；tag 已 push
