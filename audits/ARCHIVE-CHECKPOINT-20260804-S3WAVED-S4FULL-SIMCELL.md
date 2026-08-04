# 封存點：S3-WAVE-D 全線＋S4 Wave A-G 收官＋深化理解優化計畫 r6＋sim 首格 [I]（2026-08-04）

> **位階**：[I] 封存留痕（非 META-CONSTITUTION [N]）。
> **範圍**：自上一封存點 `archive-20260804-s3wab-kh-s4`（commit `779305d`，2026-08-04 15:11）起之全部變更。
> **工具**：`bash scripts/archive_push.sh --slug s3waved-s4full-r6-simcell`（`.env` `GITHUB_TOKEN` 經 `GIT_ASKPASS`；不改寫 origin URL、不嵌 token）。

## 本次封存包含什麼

| 軌 | 內容 | 關鍵檔 |
|---|---|---|
| **S3-WAVE-D 全線（Phase 1-2c）** | 序列窗 library＋CLI（唯讀重排既有 raw，不新表）；圖邊 DDL＋builder；13,021 條圖邊 `--commit` 落地 `stock_graph_edge` | `src/augur/features/sequence.py`；`scripts/build_sequence_panel.py`／`migrate_stock_graph_edge_ddl.py`／`build_stock_graph_edges.py`；`reports/augur_s3_wave_d_sequence_graph_plan_20260804.md`；`audits/S3-WAVE-D-GO/EXECUTED-20260804.md` |
| **S4 Wave B–G 收官** | 古典 TS／序列 DL／Transformer／圖模型／RL／混合-alt-NLP-Bayesian 六波，taxonomy A-G 全掃；多數誠實 SKIP（缺 adapter，非缺資料——S3-WAVE-D 已解除資料契約缺口） | `audits/S4-WAVE-{B..G}-GO/EXECUTED-20260804.md`；`audits/S4-MODELS-TRIED-LIST-20260804.md` |
| **深化理解＋專案優化計畫 r6** | 5 subagent＋DB 實測合成；36 項債務表；四軌優化計畫（治理收斂／預測閉環深化／code 結構健檢／scripts 體積收斂） | `reports/augur_deep_understanding_r6_20260804.md`；`reports/augur_project_optimization_plan_r6_20260804.md` |
| **sim 自我進化首格** | `SIM-FIRST-CELL-go` 執行：格點 `2026-08-03`、52/52 檔、迭代帳本 `sim-20260803-r01` running；時鐘 K=1/3；settle/evaluate/decide 誠實回報未到，0 自動 promoted | `audits/SIM-FIRST-CELL-GO/EXECUTED-20260804.md` |
| **既有支線收尾補寫** | `U0-37`／`U0-75` registry 執行細節補記；`SIM-S0-RESIDUAL` 殘差窗確認 checked-off；`SIM-SELF-EVOLVE-S0-DISCOVERY` 第 4 項建議勾除 | 對應 `audits/U0-*`／`audits/SIM-S0-RESIDUAL-*`／`audits/SIM-SELF-EVOLVE-S0-DISCOVERY-20260804.md` |

## 誠實邊界

- **不含**：commit 前未過的 FinMind／FRED 放量、Registry 新 INSERT（除已明示授權之 `U0-75`／`stock_graph_edge` 兩項——皆為先前既有 GO 之延續執行，非本次新開）、sim `--apply` 之後續格點（僅首格）、任何自動 `promoted` 判決。
- **`.env`／dump／秘密**：`archive_push.sh` 既有禁止清單擋——本次未新增任何此類檔案於 staging。
- **push SHA／tag**：見下方「執行結果」。

## 例外：本次 commit 之 pre-commit 閘處置（`--no-verify`，Steward 明示）

`archive_push.sh` 內部 `git commit` 撞上「WM.36 vendor 直綁止血閘」——`scripts/build_stock_graph_edges.py`（本封存新檔）新增 2 處直綁（`TaiwanStockInfo`／`TaiwanStockPriceAdj`）未過。經查證，閘建議之「改走 registry 解析」會**悄悄把報酬相關性計算換成未調整價**（`tw.daily_bar` 權威今早已指向 raw 表 binding 75，registry `resolve()` 無法指名候選），屬正確性倒退非風格問題，故**不**照建議自行改線。呈 `AskQuestion` 由 Steward 選定：**本次 commit 明示 `--no-verify` 跳過**（其餘三道閘——治權引用稽核／執行指令矩陣／假斷言閘——皆已通過），另開追蹤項 `audits/WM36-GAP-RAW-VS-ADJUSTED-CONCEPT-20260804.md` 記錄缺口與三個未決選項，留待後續批次裁示。**改用手動 git 指令**（`git add` 同一批安全路徑 → `git commit --no-verify` → `git push` → `git tag -a` → `git push tag`）複刻 `archive_push.sh` 邏輯，因該腳本無 `--no-verify` 透傳旗標。

## 執行結果

- commit SHA：`<pending，見下方指令輸出>`
- tag：`archive-20260804-s3waved-s4full-r6-simcell`
- push 分支／tag：`<pending>`
