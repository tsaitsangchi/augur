---
status: archive_checkpoint
date: 2026-08-17
kind: archive_checkpoint
tag: archive-20260817-r18-htrack-hist-econ
sha: "7999af23b5230231c363cf49e96937de514ba7e6"
remote: https://github.com/tsaitsangchi/augur
auth: "Steward：更新全部檔案上傳到 https://github.com/tsaitsangchi/augur 並做封存點"
prior: archive-20260814-weekly-fd-tar
self_reported: true
---

# ARCHIVE · 20260817 · r18 鎖／H 軌八窗／HIST-ASOF／econ E4

date: 2026-08-17  
kind: archive_checkpoint  
tag: `archive-20260817-r18-htrack-hist-econ`  
sha: `7999af23b5230231c363cf49e96937de514ba7e6`  
remote: https://github.com/tsaitsangchi/augur

上一封存：`archive-20260814-weekly-fd-tar`（commit `1c5ee69`；回填 `455f50f`）。

## 範圍（本封存）

- **開工鎖**：r18 ADOPTED＋LOCKED（`OPT-R18-ALL`）。運轉 SSOT 仍＝r16；選刀／as-of 刀＝r18。
- **H 軌**：`H_TRACK={5,10,20,40,60,90,120,240}`；H82 已刪、CHECK 不准 82；H5／H90＝08-14 另開；H10＝08-16 另開。Standing 出門仍 **20,60**。
- **B3**：M1a＠08-14 EXECUTED；M1b **WAIT** `PriceAdj≥2026-08-17`。08-15／16／17＝假 B3。
- **HIST-ASOF**：07-31 `--track all` 截面 64／64；方向臂單一 ID 曾覆寫活鎖 → skip-rank 復原＠08-14。歷史 D 預設不覆寫 Daily／Mkt／DirStackM；`pack_complete` 歷史 D 只看截面 8×8。
- **econ #14**：egate DDL＋E1–E3；E4 ready-5 耗盡；E4b 鐘 WAIT、next_due＝2026-11-13。**不 E5**、不 dump canonical-31、不放寬 ρ 0.6／DSR 95%。
- **KH**：`--check` 已跑；**未** `--apply`。NF-pause。no-promote。

## 不做（本封不假裝已做）

- 不 SERVE-SWAP／不 promote
- 不開 B3＠08-15／16／17
- 不把分數／`p_beat`／`p_mkt`／`p_up` 當漲跌幅％
- 不 evaluate／approve `dgate_H_*`；不塗 established
- 不 KH `--apply`；不重掃 0812 NF 六族
- 不把 dump／tar／`.env`／`reports/*.json` 推進 git

## 驗收

- `git rev-parse HEAD` = 上列 sha（回填後）
- `git show archive-20260817-r18-htrack-hist-econ` 可取註解
- origin/main 已含本 commit；tag 已 push
