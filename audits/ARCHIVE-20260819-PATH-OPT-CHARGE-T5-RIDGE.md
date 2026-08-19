---
status: archive_checkpoint
date: 2026-08-19
kind: archive_checkpoint
tag: archive-20260819-path-opt-charge-t5-ridge
sha: pending
remote: https://github.com/tsaitsangchi/augur
auth: "Steward：更新全部檔案上傳到 https://github.com/tsaitsangchi/augur 並做封存點"
prior: archive-20260818-b3-retrain-force-hist-oos
self_reported: true
layer: "[I]"
---

# ARCHIVE · 20260819 · PATH-OPT／CHARGE-T5／RankRidge 八窗＠08-18

date: 2026-08-19  
kind: archive_checkpoint  
tag: `archive-20260819-path-opt-charge-t5-ridge`  
sha: pending  
remote: https://github.com/tsaitsangchi/augur

上一封存：`archive-20260818-b3-retrain-force-hist-oos`（commit `c38395a`；回填 `9710e5e`）。

## 範圍（本封存）

- **LIVE**：價頂／fv／包＝**2026-08-18**。**08-19＝假 B3**。standing 出門仍 **H20+H60**。未 SERVE-SWAP、未 promote。
- **PATH-OPT-OPS-v1**：操作手冊 P0 已採納。M29–M35：UP-PULL／WATCH／BULL5／TWIN-EX／CHARGE-T5 探針或宇宙已閉；TREND-PB W1–W3 已閉；RS-CHARGE P0 已採納。
- **TWIN-EX**：兩檔不要抱牢格子＠08-18 冠軍 E-charge×T5（僅兩檔；≠可交易）。
- **CHARGE-T5-v1**：P0 採納＋核心宇宙 P1＠08-18。等權 k=10：無成本兩窗正，成本後 IS **−64.8%**；T20／T40 不當冠。兩檔無 k 對上舊帳。≠#14。
- **RankRidge 八窗**：最後交易日 08-18 dry-run，H5…H240 皆有；286 檔齊。做多相對強 Top10 當池不剔除、回撤近→遠；可當進場＝0／10。
- **HIST**：H10 OOS walk 全 no_model（日曆閘）入帳；`asof_ready` 其他車道表／walk 提示。
- **程式**：`uptrend_pullback`／`twin_ex`／`charge_t5`／`bull5`／`trend_pullback_catalog`＋對應 `scripts/probe_*`。

## 不做（本封不假裝已做）

- 不 SERVE-SWAP／不 promote／不改 standing 20,60
- 不開 B3 emit＠08-18（另句）
- 不把分數／路徑％／兩檔複利當未來漲跌幅或 #14
- 不 evaluate／approve `dgate_H_*`；不塗 established
- 不重掃 0812 NF 六族；不 `--track other --apply`
- 不把 CHARGE-T5 接顧問；不把 39 筆兩檔帳當宇宙產品績效
- 不把 dump／tar／`.env`／`reports/*.json`／`models_artifacts`／Cursor canvases 推進 git

## 驗收

- `git rev-parse HEAD` = 上列 sha（回填後）
- `git show archive-20260819-path-opt-charge-t5-ridge` 可取註解
- origin/main 已含本 commit；tag 已 push
