---
status: archive_checkpoint
date: 2026-08-18
kind: archive_checkpoint
tag: archive-20260818-b3-retrain-force-hist-oos
sha: "c38395a14f2424d83e3595970a49a07defff8e2b"
remote: https://github.com/tsaitsangchi/augur
auth: "Steward：更新全部檔案上傳到 https://github.com/tsaitsangchi/augur 並做封存點"
prior: archive-20260817-r18-htrack-hist-econ
self_reported: true
layer: "[I]"
---

# ARCHIVE · 20260818 · B3＠08-17／RETRAIN-ALL force／HIST-ASOF／OOS

date: 2026-08-18  
kind: archive_checkpoint  
tag: `archive-20260818-b3-retrain-force-hist-oos`  
sha: "c38395a14f2424d83e3595970a49a07defff8e2b"  
remote: https://github.com/tsaitsangchi/augur

上一封存：`archive-20260817-r18-htrack-hist-econ`（commit `7999af2`；回填 `e10dbc2`）。

## 範圍（本封存）

- **LIVE**：價頂／fv／包＝**2026-08-17**。08-18＝假 B3。standing 出門仍 **H20+H60**（本晨 B3 各 287 列）。方向臂活鎖＝08-17。P6 freeze 仍＠**08-14**。
- **B3**：M1b 出門＠08-17 H20+H60 EXECUTED。未八窗出門、未 SERVE-SWAP。
- **RETRAIN-ALL force**：`--date 2026-08-17 --apply --track all --force`（內殼 `--no-resume`）。截面 8×8 全重 fit＋Daily3＋Mkt2＋DirStackM。RC=0。未重 emit。
- **HIST-ASOF**：08-07／08-13 截面 64／64。歷史 D 不覆寫方向臂。下一未齊＝08-12 缺 32。
- **OOS 刀**：`registry.latest_before`；`verify_asof_families.py --oos`／`--walk`；佔位符 `D` fail-loud。V1 OOS walk H5 近 0／偏負；同日 IC 不採。
- **KH**：S0 drain＋S3 zh concordance APPLY 已閉；終檢 S0–S3 ok。
- **econ #14**：H20=`dead`；其餘 thin。E4b 鐘 WAIT、next_due＝2026-11-13。不 E5。
- **程式**：`asof_ready`／`run_asof_collect_train_verify.sh --force`→`--no-resume`／`predict_asof --strict-before`。

## 不做（本封不假裝已做）

- 不 SERVE-SWAP／不 promote
- 不開 B3＠08-18（無價）
- 不把分數／`p_beat`／`p_mkt`／`p_up`／IC 當漲跌幅％
- 不 evaluate／approve `dgate_H_*`；不塗 established
- 不重掃 0812 NF 六族；不 `--track other --apply`
- 不 P6-REFIT＠08-17（須另 GO）
- 不把 dump／tar／`.env`／`reports/*.json`／`models_artifacts` 推進 git

## 驗收

- `git rev-parse HEAD` = 上列 sha（回填後）
- `git show archive-20260818-b3-retrain-force-hist-oos` 可取註解
- origin/main 已含本 commit；tag 已 push
