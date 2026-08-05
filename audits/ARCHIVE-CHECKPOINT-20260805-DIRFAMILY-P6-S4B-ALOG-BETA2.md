# 封存點 ARCHIVE — 2026-08-05 DIRFAMILY／P6／S4-B／action_log／β2

> **位階**：[I] 封存留痕（非 META-CONSTITUTION [N]）。  
> **觸發**：Steward「更新全部檔案上傳到 github 並做封存點」  
> **範圍**：自上一封存點 `archive-20260804-s3waved-s4full-r6-simcell`（commit `b266e26`／補記 `5a96c09`）起之全部工作樹變更。  
> **self-reported（#32a）**：SHA／tag 以 `archive_push.sh` 實推後回填為準。

---

## 本次封存包含什麼（摘要）

| 軌 | 內容 | 主帳 |
|---|---|---|
| S4 DIRFAMILY | Phase 0 generalize＋Phase 1 RankSVM→DirStack（未贏既有 DirStack） | `S4-DIRFAMILY-*-2026080{4,5}.md` |
| P6 | AS_OF 邊界 A+B＋C/D 參數釘錨 | `S4-PROB-ASOF-*`／`S4-P6-ASOF-CD-*` |
| S4-B classical | Phase 0 薄殼＋Phase 0b 微勝 naive 地板 | `S4-WAVE-B-ADAPTER-PHASE0{,B}-*` |
| S4 其他 | Wave-A sklearn eval、SeqLSTM／RankEnsemble 評測帳、多份 plan | audits／reports 20260804–05 |
| S3 | Wave-C／E-KEEP；殘帳 β plan；**β2** 交互材料化＋IC（verify **in-flight**） | `S3-BETA-BETA2-*`／`S3-WAVE-*` |
| C 軌 | `action_log` 三點接線＋grants | `C-TRACK-ACTION-LOG-WIRED-20260805.md` |
| 結構 | obsolete scripts→`archive/`；刪 `sync_memory.sh`；WM36／CS 等小修 | working tree |
| r6 | 優化計畫／深化理解簿記更新 | `augur_project_optimization_plan_r6_*`／`augur_deep_understanding_r6_*` |

## 誠實邊界（封存時）

- **S3-BETA-beta2**：IC 預篩已完（as-of H60 HAC-t≈−2.81）；`verify_candidate_promotion` **仍 in-flight**——見 `audits/S3-BETA-BETA2-EXECUTED-20260805.md`（partial）。**不**假稱多 seed 終表／提拔結論已定。
- FZ/GATE-keep · skip-sync · no-SIM-apply 本批未解凍放量、未 sim `--apply`。
- 未入庫：`scratchpad/`、`.env`、dump／venv。

## 前次封存（仍有效）

- `archive-20260804-s3waved-s4full-r6-simcell`（`b266e26`）
- 帳：`audits/ARCHIVE-CHECKPOINT-20260804-S3WAVED-S4FULL-SIMCELL.md`

## Push 實況（已回填）

| 項 | 值 |
|---|---|
| slug | `dirfamily-p6-s4b-alog-beta2` |
| tag | `archive-20260805-dirfamily-p6-s4b-alog-beta2` |
| commit | `4a21cda`（full `4a21cda8d65a5492666f5c816f51b31935e84f6e`） |
| tag object | `0b5b073cd99918782c822179db8d51aed76f4ca0` |
| remote | `https://github.com/tsaitsangchi/augur.git` `main` |

### WM.36 處置（本封存）

pre-commit vendor 直綁閘擋新增：
- `scripts/probe_classical_ts_phase0b.py` → `TaiwanStockPriceAdj`
- `scripts/train_classical_ts.py` → `TaiwanStockPriceAdj`

Steward 經 AskQuestion 選定：**本次 commit 明示 `--no-verify`**（同 `ARCHIVE-CHECKPOINT-20260804-S3WAVED-S4FULL-SIMCELL` 先例）；其餘閘（治權引用／指令矩陣／#8 AST／假斷言）已綠。兩處 PriceAdj 直綁併入 WM.36 追蹤（需 `tw.*.adjusted` 權威，不可 silently 改 registry→raw）。

*手動複刻 `archive_push.sh`（rename pathspec 腳本尚不能 stage `R old -> new`；且無 `--no-verify` 透傳）。*

