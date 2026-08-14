---
status: archive_checkpoint
date: 2026-08-14
kind: archive_checkpoint
tag: archive-20260814-weekly-fd-tar
sha: pending_backfill
remote: https://github.com/tsaitsangchi/augur
auth: "Steward：更新全部檔案上傳到 https://github.com/tsaitsangchi/augur 並做封存點"
prior: archive-20260814-h240-retrain-0813
self_reported: true
---

# ARCHIVE · 20260814 · weekly -Fd 單檔 tar／備份還原

date: 2026-08-14  
kind: archive_checkpoint  
tag: `archive-20260814-weekly-fd-tar`  
sha: pending_backfill  
remote: https://github.com/tsaitsangchi/augur

上一封存：`archive-20260814-h240-retrain-0813`（commit `f7695af`；回填 `3fce324`）。

## 範圍（本封存）

- **產物（不進 git）**：`~/db_dumps/augur_20260814_weekly_Fd`（-Fd 目錄）＋ sibling `augur_20260814_weekly_Fd.tar`；鏡像 `C:\database\` 同名目錄與 `.tar`
- **tar 口徑**：未再 gzip（內層已 `-Z1`）；根成員 `augur_YYYYMMDD_weekly_Fd/toc.dat`；先寫 `.part` 再轉正
- **備份**：`scripts/backup_database.sh` dump 後打 tar；目錄／tar 分開輪替；鏡像位元組相符跳過 cp；冪等跳過 dump 仍確保 tar＋鏡像
- **還原**：`import_database.sh` 搜 `/mnt/c/database`；同資料夾目錄優先於 `.tar`；`pg_restore` 不直接吃 tar-of-Fd（先解到本地 ext4 再 `-Fd -j4`）
- **哨兵**：`verify_backup_mirror.py` 認 `.tar`（`tar -tf`＋抽出 toc 跑 `pg_restore -l`）；不拿目錄位元組跟 tar 比
- **實測**：本地／鏡像 tar `11164651520` B；哨兵 green（2888 物件／343 資料檔）

## 不做（本封不假裝已做）

- 不把 11G dump／tar 推進 git
- 不 `pg_dump -Fc`、不重 dump 活庫
- 不 SERVE-SWAP／不 promote／不開 B3＠08-14
- 不把分數／`p_beat_median`／`p_mkt`／`p_up` 當漲跌幅％
- 不 evaluate／approve `dgate_H_240`／`dgate_H_60`

## 驗收

- `git rev-parse HEAD` = 上列 sha（回填後）
- `git show archive-20260814-weekly-fd-tar` 可取註解
- origin/main 已含本 commit；tag 已 push
