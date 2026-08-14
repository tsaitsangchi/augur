---
status: archive_checkpoint
date: 2026-08-14
kind: archive_checkpoint
tag: archive-20260814-l0-retrain-r16-b3-0813
sha: `31998b0eb704ae365fa47ec8c940fe1944569cc1`
remote: https://github.com/tsaitsangchi/augur
auth: "Steward：更新全部檔案上傳到 github 並做封存點"
prior: archive-20260813-b3-0812-kh-a2l3-nf0812
self_reported: true
---

# ARCHIVE · 20260814 · L0 熱路徑 / RETRAIN-ALL 日更 / r16 / B3@0813

date: 2026-08-14  
kind: archive_checkpoint  
tag: `archive-20260814-l0-retrain-r16-b3-0813`  
sha: `31998b0eb704ae365fa47ec8c940fe1944569cc1`  
remote: https://github.com/tsaitsangchi/augur

上一封存：`archive-20260813-b3-0812-kh-a2l3-nf0812`（commit `828c8e9`；回填 `5f342f8`）。  
本封含其後未推之 `01e9f28`（KH 假 decline 閘＋r15 雙軌計畫）以及 08-13 午後→08-14 工作樹。

## 範圍（本封存）

- **S1／L0**：預測日更 L0＝核 A 14 張＋TRI（TAIEX／TPEx）＋熱路徑 FRED；arena 20:00 第①步改呼叫 `run_l0_hotpath_daily.sh`；**不是** 93 表、**不是** `AUGUR_DIM_SYNC=1`
- **S4／重訓**：`run_retrain_all_asof.sh`＋日更驅動；live cron 平日 21:40／09:20；**no-promote／no-emit／no-fake-B3**；0813 包 COMPLETE（rank 40/40＋Daily*＋Mkt*＋DirStackM）
- **S5／B3／L2**：B3＋L2 ALL-RANK＠**2026-08-13**（H20 dead／H60 thin；H40／82／120 無 LIVE emit）；08-14 價未到＝禁假 B3
- **as-of 閘**：`src/augur/core/asof_ready.py`（價頂鎖／假 B3 分類）；方向臂／ranker／predict／panel 接線；WM.36 價頂經 `tw.daily_bar_adjusted`
- **閉環 SSOT**：S1→S5 r16；L0 熱路徑計畫＋ADOPTED
- **KH（已在 `01e9f28`）**：有引文禁假「無此內容」；r15 理解／全板／人話憲章
- **硬門**：FZ/GATE-keep｜no-fake-B3｜NF-pause｜no-SIM-apply｜no-promote｜PDF-C-no-ASR｜T0

## 不做（本封不假裝已做）

- 不 SERVE-SWAP／不 promote 挑戰者
- 不開 B3＠08-14（FinMind 當日收盤列未到）
- 不把 `p_beat_median` 當漲跌幅％
- 不 evaluate／approve `dgate_H_60`
- 不解 NF-pause、不 sim `--apply`

## 驗收

- `git rev-parse HEAD` = 上列 sha（回填後）
- `git show archive-20260814-l0-retrain-r16-b3-0813` 可取註解
- origin/main 已含本 commit；tag 已 push
