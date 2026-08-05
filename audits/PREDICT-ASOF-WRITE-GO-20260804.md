# predict-asof-write-go 授權留痕 [I]（2026-08-04）

> **位階**：[I] 拍板留痕（非 META-CONSTITUTION [N]）。
> **父 SSOT**：`reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md` §7.3（`predict-asof-write-go`，列於「加料，非默認」）；`reports/augur_project_optimization_plan_r6_20260804.md` §5 Tier 4 候選（B 軌 #9）。
> **本輪選項來源**：`AskQuestion`（Steward 從「Tier 4」清單選 `predict_asof_go`，並明示「可與 Tier 1／Tier 3 同時進行」）。

## 授權四要件（CLAUDE #26）

| 要件 | 內容 |
|---|---|
| (a) 範圍 | `scripts/predict_asof.py --run --dry-run`（唯讀試算）→ 呈結果 → 若乾淨則 `--run`（無 `--candidate`，正式 serve 語意）寫 `prediction_values`；**不**跑 `--rewrite-all`（D4 多 horizon 語意，範圍外）、**不**加 `--risk-control`（overlay 另計，本輪僅基本 serve） |
| (b) 期限 | 本次對話會話內；一次性出單動作（`--run` 非 `--candidate` 時為 DELETE+INSERT 同 key 冪等，非常駐） |
| (c) 可撤銷 | 隨時可撤；`prediction_values` 寫入為 DELETE WHERE (panel_date,model_id) + INSERT，非破壞性覆蓋其他 model_id／panel_date 之既有列；撤銷＝人工 DELETE 該 (panel_date, model_id) 或不再呼叫 |
| (d) 所繫計畫 | `augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md` §0.5／§7.3；S1→S5 主線 predict 側最後一塊未落地動作 |

## 事前 DB 現況核實（避免對「未寫」之誤判）

`prediction_values` 現況**非空**——已有 **2,373 列**，全部來自先前 D4 `--candidate --rewrite-all` 語意批次（`panel_date`∈{2026-05-31, 2026-06-30}，8 個 `model_id`，皆用**較舊** artifact 快照如 `..._2026-05-31_seed42_ce62866bb62de38b`／`..._3a4e66fae8cfa2fa`／`..._9a88039981b5a128`）。

**今日新出爐**之最新 H60 artifact（`RankRidge_H60_2026-06-30_seed42_56d03625463b3eba`，`asof_snapshot=2026-06-30`，2026-08-04 11:04 訓練）**尚未**被用於任何 `prediction_values` 寫入。`--run`（無 `--candidate`）之預設語意會呼叫 `registry.latest('RankRidge', 60, asof)`，在 `asof=core_universe_asof` 最新（**2026-06-30**）下應解析到此最新 artifact——**與既有 2,373 列之 model_id 皆不同key**，故本次寫入為**新增**（該 model_id 下 DELETE 為 no-op），不覆蓋／不刪除既有 D4 候選列。

## 效力邊界

| 是 | 不是 |
|---|---|
| 對 `asof=2026-06-30`、`family=RankRidge`、`horizon=60`（預設）跑一次正式（非 candidate）serve，寫 `prediction_values` | `--candidate`／`--rewrite-all` D4 語意；不動既有 2,373 列 |
| 系統建議、人決策——只出相對強弱排序＋long 部位建議 | 下單、動錢、可交易／確立級宣稱 |
| as-of 凍結：只用 ≤asof 已知特徵；feats_hash／漂移檢測全程守（script 內建，拒載即中止非強行） | 繞過 #8 as-of 凍結或 #15 feats_hash 鎖 |
| dry-run 先行、呈結果後才 `--run` 正式寫 | 未看過 dry-run 結果就直接寫庫 |

## 硬禁（本輪，繼承父計畫）

- 零 FinMind／FRED 放量；零 sync
- 零 `--risk-control`（風控 overlay 另計，本輪不加）
- 零假確立級／可交易宣稱
- 不 commit／push（除非另行明示）

## 執行序

1. `predict_asof.py`（無參數＝印指令矩陣＋操作值，確認預設 horizon=60/family=RankRidge/asof=最新）
2. `predict_asof.py --run --dry-run`（試算＋印排序＋投組，零寫庫）
3. 呈 dry-run 結果供確認
4. （若確認）`predict_asof.py --run`（正式寫 `prediction_values`）
5. 驗收：查 `prediction_values` 新增列數＋`model_id`＝預期之最新 H60 artifact
