# S4 新模型族計畫｜RankEnsemble（RankRidge×RankGBDT rank-average blend）· 2026-08-04

> **性質**：[I] plan-first（CLAUDE #20——新增 `model_registry` 家族屬架構層決定，量體雖小仍先計畫）。
> **觸發**：Steward 選定「T4a 多模型融合」為下一手（本檔 2026-08-04 對話拍板）。
> **前置 SSOT**：`reports/augur_project_optimization_plan_r6_20260804.md`§5 T4a、`audits/S5-OOS-20260804.md`（RankRidge H20/H60 OOS 基準）、`audits/S4-REOPT-BACKLOG-20260804.md`（RankGBDT 未升格之判準先例）。
> **self-reported（#32a）**：本文為 AI 呈案；一切數字待 Phase 0 實跑後以 stdout 為準，本檔內引用之既有數字皆出自既有 audit。

---

## 0. 一句話

**不是造新模型，是把已經寫在 `portfolio.py` 裡、從未被真正評測/升格的 `ENS_ridge_gbdt`（RankRidge×RankGBDT rank-average）跑一次完整 #11(多seed)+#14(經濟) 評測；只有真贏過現任冠軍 RankRidge_H60 才升格為正式 `model_registry` 家族。**

---

## 1. 為何是這把（背景查證）

`src/augur/evaluation/portfolio.py:183-189` 的 `run_backtest()` 已內建 `model="ENS_ridge_gbdt"` 分支（等權 rank-average：`(rankdata(p_r)+rankdata(p_g))/2`），但**從未被 `run_economic_eval.py` 的 `for model in (...)` 迴圈納入**、**從未有 #11 多 seed 報告**、**從未被登錄為 `model_registry` 家族**（`train_ranker.py` FAMILIES 只有 RankRidge/RankGBDT）。這是一段「已寫但未評測、未升格」的死角，不是全新架構——利用既有碼即可低成本補齊。

**與既有基準之關係**（`audits/S5-OOS-20260804.md`）：

| 模型 | H | net Sharpe | net hit |
|---|---|---|---|
| RankRidge（現任冠軍） | 60 | **1.3016** | 0.6316 |
| RankRidge | 20 | 1.1684 | 0.6393 |
| RankGBDT（3-seed，未升格） | 60 | min 1.031／med 1.090／max 1.153 | 全 seed＝bench 0.5789 |

RankGBDT 未升格理由（`S4-REOPT-BACKLOG` 項4）＝「hit＝bench；Sharpe≈基準」。**Ensemble 若只是兩者內插，大機率也过不了同一關**——這正是本計畫先評測、後決定是否寫碼升格的理由，避免重蹈"單臂高分宣稱"覆轍（CLAUDE #32b 預凍對照臂）。

---

## 2. (a) 對應 table schema

**零新表**。全部讀寫既有表，schema 如下（供對照，非新建）：

| 表 | 用途 | 關鍵欄位 |
|---|---|---|
| `model_registry`（既有） | Phase 1 才寫：登錄 `RankEnsemble` 家族一列 | `model_id, family, horizon, train_span, asof_snapshot, feats_hash, seed, metrics jsonb, artifact_path, git_sha` |
| `prediction_values`（既有） | 若日後選擇出單才寫；本計畫 Phase 0/1 皆不觸 | `panel_date, model_id, stock_id, score, rank, in_portfolio, weight` |
| `models_artifacts/*.joblib`（既有目錄，非 DB 表） | Phase 1 存 `RankEnsemble` artifact | `{estimator, feats, horizon, asof_snapshot, family, seed, feats_hash}`（`artifact.save` 既有格式，零改動） |

---

## 3. (b) 對應 python 程式規劃

### Phase 0（評測；零產品碼變動、零 registry 寫入）

| 檔 | 動作 | 函式/角色 |
|---|---|---|
| `scripts/run_economic_eval.py` | **改 1 行**：`for model in ("B2_ridge", "M1_gbdt")` → 加入 `"ENS_ridge_gbdt"` | 既有迴圈自動跑 top{10/20/30}%×{equal/pred} 全網格（`run()` 函式內，行 114） |
| 一次性 3-seed 探針（沿用本次工作階段既有模式，如 `/tmp/rank-ensemble-3seed-probe.py`） | 呼叫既有 `portfolio.run_backtest(model="ENS_ridge_gbdt", seed=1/2/42)`，H20/H60 各 3 seed | 零新函式——與 GBDT 3-seed probe（`423016.txt`／`423018.txt` 既有模式）同構，僅替換 `model=` 參數 |

**驗收（Phase 0 gate，任一不過即停、不進 Phase 1）**：
1. H60：ensemble net Sharpe **3-seed min** 須 **> 1.3016**（現任冠軍單值，因 RankRidge 本身無隨機性=不動點）。
2. H60：ensemble net hit **3-seed min** 須 **> 0.6316**（或至少不劣於冠軍，因 Sharpe/hit 可能背離，兩者需一併看）。
3. 不得以「中位數勝出」或「單 seed 勝出」宣稱（承 CLAUDE #32b 預凍對照臂紀律——地板＝現任冠軍本身）。
4. H20 同框比較，非升格門檻（H60 為主戰場，H20 供交叉參考）。

### Phase 1（僅當 Phase 0 全過；新寫碼）

| 檔 | 動作 | 函式/角色 |
|---|---|---|
| `src/augur/models/ranker.py` | 新增 `class RankEnsemble`：`family="RankEnsemble"`；`fit(X,y)` 內部 `self._ridge=RankRidge().fit(X,y)`、`self._gbdt=RankGBDT(seed=self.seed).fit(X,y)`；`predict(X)` 回 `(rankdata(ridge.predict(X))+rankdata(gbdt.predict(X)))/2`（與 `portfolio.py` 既有 `ENS_ridge_gbdt` 分支**逐值等同**，複用鐵律 #12） | 新增類別，契約與 RankRidge/RankGBDT 完全一致（薄殼、零新依賴） |
| `scripts/train_ranker.py` | **改 1 行**：`FAMILIES = {"RankRidge": RankRidge, "RankGBDT": RankGBDT, "RankEnsemble": RankEnsemble}` | 其餘 `train()`／`main()` 邏輯零改動（已泛化於 family 字串） |
| `scripts/predict_asof.py` | **零改動**（`registry.latest(family,...)`／`artifact.load()` 已泛化，`--family RankEnsemble` 即可用） | n/a |
| `src/augur/models/artifact.py` | **零改動**（`joblib.dump` 對任意可 import 類別皆通用） | n/a |

**驗收（Phase 1）**：`train_ranker.py --run --family RankEnsemble --horizon 60` 產生 artifact＋registry 列；`predict_asof.py --run --family RankEnsemble --horizon 60 --dry-run` 能載回並印出投組（不寫庫驗證，通過後才決定是否正式出單）。

---

## 4. 元件與端點

| 元件 | 端點/介面 |
|---|---|
| 評測（Phase 0） | CLI：`python scripts/run_economic_eval.py --h 60 --feature-source=prodset --cost 0.00585`（加了 ENS 分支後自動含）＋一次性 3-seed 探針腳本 |
| 訓練（Phase 1，條件觸發） | CLI：`python scripts/train_ranker.py --run --family RankEnsemble --horizon {20,60}` |
| 推論（Phase 1，條件觸發） | CLI：`python scripts/predict_asof.py --run --family RankEnsemble --horizon 60 --dry-run` |

---

## 5. 分階段與硬邊界

| 階段 | 內容 | 寫庫? | 需再授權? |
|---|---|---|---|
| Phase 0 | 評測（改 1 行 eval 迴圈 + 3-seed 探針） | 否 | 本 GO 涵蓋 |
| **決策點** | 對照 §1 驗收門檻，人／AI 呈數據 | — | 若不過→止於此，寫誠實 audit 收尾（同 RankGBDT 先例） |
| Phase 1 | 新增 `RankEnsemble` 類別＋註冊 family＋train＋dry-run predict | 是（`model_registry`＋artifact 檔） | 本 GO 涵蓋（`--dry-run` 不寫 `prediction_values`） |
| Phase 2（本計畫外） | 正式出單（`predict_asof.py --run` 無 `--dry-run`）、納入 serve 輪替 | 是（`prediction_values`） | **另句**——本計畫不含（比照 `predict-asof-write-go` 需另立明示） |

**硬禁**（承 FZ/GATE-keep／no-SIM-apply／skip-sync）：零 FinMind／FRED；零 sim `--apply`；零 `direction_gate` 改動；Phase 1 即便 artifact／registry 落地，**不視為確立級／可交易宣稱**（承既有全部模型 self-reported 邊界）。

---

## 6. 驗收方式總覽

- Phase 0：stdout 數字（(a) 程式輸出）對照 §1 表格門檻，決策留痕於 `audits/S4-RANKENSEMBLE-EVAL-20260804.md`。
- Phase 1（條件）：`git diff` 對照 `ranker.py`／`train_ranker.py` 改動範圍＝表列；`ReadLints` 確認無新增 lint；`--selftest`（`ranker.py` 既有自測擴充 `RankEnsemble` 結構斷言）。

---

*定版（2026-08-04）。下一手＝執行 Phase 0（零產品碼風險，僅評測）。*

---

## 執行後記（2026-08-04，同日）

**Phase 0 已執行，gate 未過，止於此、不進 Phase 1**。詳見 `audits/S4-RANKENSEMBLE-EVAL-20260804.md`——H60／H20 兩 horizon 之 3-seed ensemble net Sharpe 皆全數低於現任冠軍 `RankRidge`（H60 min 1.1641 vs 冠軍 1.3016；H20 min 1.0054 vs 冠軍 1.1684）。等權 rank-average 混入較弱之 RankGBDT 反而拖累強模型，與 `S4-REOPT-BACKLOG` 已知 RankGBDT 弱於冠軍之先驗一致。`run_economic_eval.py` 的 `ENS_ridge_gbdt` 掛載保留（零成本），`RankEnsemble` 類別／`model_registry` 家族未新增。本計畫**正式關閉**，未來若重啟模型融合方向須換有學習權重之設計、另立新計畫。
