---
status: archive_checkpoint
date: 2026-08-24
kind: archive_checkpoint
tag: archive-20260824-k9-cquant-ma10dn-hk
sha: pending
remote: https://github.com/tsaitsangchi/augur
auth: "Steward：更新全部檔案上傳到 https://github.com/tsaitsangchi/augur 並做封存點"
prior: archive-20260821-r22-b3-kh-s0
self_reported: true
layer: "[I]"
---

# ARCHIVE · 20260824 · K9 C-quant×2＋concordance＋MA10DN／MA10HK

date: 2026-08-24  
kind: archive_checkpoint  
tag: `archive-20260824-k9-cquant-ma10dn-hk`  
sha: pending（打 tag 後回填）  
remote: https://github.com/tsaitsangchi/augur

上一封存：`archive-20260821-r22-b3-kh-s0`（commit `63a2fc9`；回填 `9da7bd3`）。

## 範圍（本封存）

- **LIVE**：PriceAdj TAIEX 價頂＝**2026-08-21**。本封不改 standing／不 SERVE-SWAP／不 promote／不改 L0。本封≠B3-go。
- **K9**：分隊 A–E **adopted**（仍 no-train）。C 隊兩槍 `limit=1000`：kip-45／kip-46，admit 上限 **7**，未抬 ≥8。skip_* 不是綠。殘 DOI 另句。
- **concordance**：zh／en catch-up 本窗 pending=0。
- **KH**：S0 第三槍 EXECUTED（已 0 之 no-op）。選刀仍守穩態。
- **條件帳碼**：MA10DN（5<…<240 ≤10%）＋MA10HK（5>10 且 10 起倒排 ≤10%）。表 `ridge_then_pb_long_ma10dn_*`／`ridge_then_pb_long_ma10hk_*`。不覆寫 v1／w10／ma10／ma20。條件≠可交易。
- **watch（08-24 Steward 點名）**：已停做空、W10、MA10DN、MA10HK。仍跑：HIST-WF 八窗河、做多 v1、MA10、MA20。
- **河／進度**：HIST-WF 與條件帳進度 JSON 快照入倉。不聲稱河已灌到價頂。

## 不做（本封不假裝已做）

- 不把本封當 B3-go；不 SERVE-SWAP／不 promote／不改 standing 20,60
- 不改 L0；不 KH8 L3；不 K9 開訓；不抬 admit＞7
- 不重開已 kill 的四支 watch；不第二支 HIST-WF `--apply`
- 不 sim `--apply`；不 E5
- 不把分數／均線閘／收盤買進當可交易或未來漲跌幅
- 不把 Cursor canvases、`.env`、`reports/*.json`、`models_artifacts` 推進 git

## 驗收

- `git rev-parse` 封存 commit＝pending（tag 打在此；回填為後一 commit）
- `git show archive-20260824-k9-cquant-ma10dn-hk` 可取註解
- origin/main 已含本 commit；tag 已 push
