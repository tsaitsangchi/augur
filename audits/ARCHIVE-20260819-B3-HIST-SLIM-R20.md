---
status: archive_checkpoint
date: 2026-08-19
kind: archive_checkpoint
tag: archive-20260819-b3-hist-slim-r20
sha: "63752bb693293fba42fef2bb12b896b35b4a39d0"
remote: https://github.com/tsaitsangchi/augur
auth: "Steward：更新全部檔案上傳到 https://github.com/tsaitsangchi/augur 並做封存點"
prior: archive-20260819-path-opt-charge-t5-ridge
self_reported: true
layer: "[I]"
---

# ARCHIVE · 20260819 · B3＠08-18／HIST 08-11·12／slim T0–T4／r20

date: 2026-08-19  
kind: archive_checkpoint  
tag: `archive-20260819-b3-hist-slim-r20`  
sha: "63752bb693293fba42fef2bb12b896b35b4a39d0"  
remote: https://github.com/tsaitsangchi/augur

上一封存：`archive-20260819-path-opt-charge-t5-ridge`（commit `ad7db10`；回填 `6341cab`）。

## 範圍（本封存）

- **LIVE**：價頂／fv／包／出門＝**2026-08-18** H20+H60 RankRidge。**08-19＝假 B3**（rc=3）。standing 仍 **H20+H60**。未 SERVE-SWAP、未 promote。
- **B3＠08-18**：`OPS-B3-20260818-*` EXECUTED。
- **HIST-ASOF**：code（`asof_ready.fake_b3_probe_date`；缺 core 仍 `build_core`）＋ apply＠**08-12**、＠**08-11** 皆 64／64；無 `--ic`。方向臂 LIVE 鎖仍＠**08-18**。下一未齊日＝**08-10 缺 52**。
- **S4 other V0／V1＠08-18**：已閉；`--track other --apply`＝rc=6；**no-promote**。
- **RIDGE-THEN-PB-v1＠08-18**：多 0／10、空 0／10；空≠可融券。LS JSON SSOT＝`audits/RIDGE-THEN-PB-LS-0818.json`。
- **理解／開工鎖**：r20＝現行理解＋倉精化主題；**市場／KH／路徑開工鎖仍＝r19**。精要讀序＝`reports/SSOT_READ_ORDER.md`。
- **slim T0–T4 EXECUTED**：重複 CSV→`archive/slim-t0/`；5 inbound-zero scripts→`archive/slim-t1/`；31  superseded 輪次報告→`archive/slim-t2/`；14 祖先計畫→`archive/slim-t3/`；7 `opt_next_best*`→`archive/slim-t4/`。**未**搬 08-04 GO parent、**未**搬 KH `20260812` 選刀。`.py` 建議刪仍＝0。
- **程式**：`src/augur/core/asof_ready.py`、`scripts/check_asof_ready.py`、`scripts/verify_asof_families.py`、`scripts/run_asof_collect_train_verify.sh`；封存腳本 rename 列改列 dest。

## 不做（本封不假裝已做）

- 不假 B3＠08-19；不 HIST `--apply`＠08-10（另句）
- 不 SERVE-SWAP／不 promote／不改 standing 20,60
- 不 sim `--apply`；不 E5；不 dump canonical-31
- 不 KH `--apply`；不重掃 0812 NF 六族；不 `--track other --apply`
- 不把分數／`p_beat`／路徑％／兩檔複利當未來漲跌幅
- 不把 RIDGE-THEN-PB／CHARGE-T5／做空名單當可交易
- 不 mass-delete 剩餘 audits／`src/`；不 `rm` `archive/slim-t*`
- 不把 dump／tar／`.env`／`models_artifacts`／Cursor canvases 推進 git

## 驗收

- `git rev-parse HEAD` = 回填後之 sha
- `git show archive-20260819-b3-hist-slim-r20` 可取註解
- origin/main 已含本 commit；tag 已 push
