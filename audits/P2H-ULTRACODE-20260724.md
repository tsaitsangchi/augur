# U-P2H Ultracode — prodset→預測熱路徑對抗 [I]（2026-07-24）

* Steward：「**開 U-P2H**」；輸入＝P2H 計畫＋S123 CLOSED＋Gap G-PME-HOTPATH＋`prodset_contract`／`train_ranker`／`predict_asof`／`verify_prodset_hotpath`
* **方法**：Find→Verify→Critic→Synthesize（對齊 U5／U-PME 鐵律）
* **硬邊界**：不改 [N]；不解凍 FinMind／FRED；可跑庫內 selftest／哨兵／isolation；**不**自動開更多實作除非 finding 必修且最小
* 證據錨：`reports/augur_prodset_predict_hotpath_plan_20260724.md` · `audits/P2H-PLAN-APPROVED-20260724.md` · `audits/P2H-S123-CLOSED-20260724.md` · `audits/PME-ULTRACODE-20260724.md` · `.cursor/rules/predict-vs-market-api.mdc` · `src/augur/core/prodset_contract.py` · `scripts/{train_ranker,predict_asof,verify_prodset_hotpath}.py` · `src/augur/audit/import_isolation.py`

---

## 一、Find（攻擊面）

| 攻擊 | 假說 |
|---|---|
| 假吃晉升 | train／predict 宣稱 prodset，實則仍走 canonical 交集；或 active 非 APPLY 產物 |
| 偷吃 canonical | 空／窄 prodset silent fallback 全量 canonical（假寬） |
| 空集未 fail-closed | active=0 仍 fit／serve；或覆蓋空卻不中止 |
| 破 isolation | PIPELINE／evaluation／scripts import `augur.philosophy`；predict GRANT 整包 evolution／philosophy |
| n_feats=2 吹成可交易／確立級 | 報告／對外句把極窄 2 特徵說成生產完備／可交易 |
| 仍依賴 FinMind／FRED | 熱路徑硬前提 live API；或本輪仍有 sync／probe 進程 |
| 文件幽靈 | 路線圖／計畫仍寫「執行未開／HOTPATH open／U 未開」與 S123 衝突 |

---

## 二、Verify（親驗證據 → 裁決）

| ID | 標的 | 嚴重度 | 文本／形式／實務 | 裁決 |
|---|---|---|---|---|
| **F-U-P2H-1** | 假吃晉升 | **pass（真吃）** | **文本**：S123 A2／A4／A8。**形式**：live `evolution_production_feature_set`×2＝`inst_cumflow_position_120d`／`volume_gini_60d`，`source_run_id=5`、`last_action=promote`；`apply_log`×2 delta 同特徵；`model_registry` `RankRidge_H60_2026-05-31_seed42_1420b777665a099f`：`feature_source=prodset`、`n_feats=2`、feats⊆active。**實務**：predict dry-run 同 model、`n_feats=2`、凍結 feats＝active。 | **不成立為缺陷**；真讀晉升子集 |
| **F-U-P2H-2** | 偷吃 canonical | **pass** | **文本**：FC-empty；禁 silent fallback。**形式**：`resolve_train_feats` 預設 `prodset`；空 active／覆蓋空→`ProdsetEmptyError`（monkeypatch 親驗兩支）；`train_ranker` catch→中止。**實務**：無「空則改走 canonical」碼徑於熱路徑。 | **不成立**；殘留＝`run_ladder` 之 `feats or canonical`（非 hotpath；Critic） |
| **F-U-P2H-3** | 空集未 FC | **pass** | **形式**：`require_nonempty`＋cover-empty 再 raise；`predict_asof` 空 active→`ProdsetEmptyError` 中止；prodset 漂移≠凍結→拒載。 | **維持 FC-empty** |
| **F-U-P2H-4** | isolation／GRANT | **pass** | **形式**：`import_isolation` exit 0；`pytest tests/test_philosophy_isolation.py` 9 passed；train／predict／baseline／prodset_contract AST 零 philosophy；predict SELECT：prodset＝准、`evolution_run`／`promotion_queue`／`apply_log`／`kill_switch`／`philosophy_*`＝拒。 | **維持隔離綠** |
| **F-U-P2H-5** | 2 特徵誇大 | **pass（誠實窄）** | **文本**：計畫 §6／S123 A11 明示極窄。**形式**：metrics／dry-run 皆 `n_feats=2`；`direction_gate` `status=evaluated_pass` **count=0**。**實務**：本輪 audits／HANDOFF／哨兵輸出皆帶「≠可交易／≠確立級」。 | **不成立為吹噓**；禁誤讀 none＝可交易 |
| **F-U-P2H-6** | FinMind／FRED | **pass** | **形式**：熱路徑模組無 fetch import（僅 docstring 禁語）；本輪零 sync／dividend_resume 進程；庫內 as-of `2026-05-31` train 已登錄＋predict dry-run 成功。 | **維持 FZ-keep；預測↔API 正交** |
| **F-U-P2H-7** | 路線圖幽靈 | **medium（時點漂移）** | **文本**：`augur_constitution_to_implementation_roadmap` §9 仍「計畫已拍板／**執行未開**」「G-PME-HOTPATH 仍 open」；建議下一句仍「開 prodset 熱路徑」。**形式**：S123 CLOSED＋HANDOFF／Gap 已 none。**實務**：只讀路線圖＝以為未接線。 | **成立（文件）** → 本輪刷幽靈（[I]） |
| **F-U-P2H-8** | 計畫 §2.2 ∩ 語意 | **low（知情差）** | **文本**：計畫曾寫「全 panel 嚴格交集」。**形式**：code＝`active ∩ 窗內至少一次`（防短史晉升被誤殺成空→誘假寬）。**實務**：現況 active×2 於 as-of 全覆蓋，train／pred resolve 集合相等。 | **成立（敘事）** → 計畫最小對齊；**非**安全破口 |
| **F-U-P2H-9** | 計畫 §1.1 現況表 | **low** | §1.1 仍列熱路徑「❌ 仍走 canonical」／Efull「未閉」——與文首 S123 CLOSED 衝突。 | **成立** → 刷現況列 |

**本輪親驗指令摘要**（零 FinMind／FRED）：

* `python -m augur.core.prodset_contract --selftest` → 全通過
* `python scripts/verify_prodset_hotpath.py --selftest` → 全通過
* `python scripts/verify_prodset_hotpath.py --check` → PASS（active n=2；GRANT 對）
* `python -m augur.audit.import_isolation` → exit 0
* `pytest tests/test_philosophy_isolation.py` → 9 passed
* `python scripts/predict_asof.py --run --dry-run --asof 2026-05-31` → exit 0；`feature_source=prodset`；`n_feats=2`
* DB 唯讀：prodset×2←run5 promote；registry prodset 模型 feats⊆active；`evaluated_pass=0`
* monkeypatch：空 active／覆蓋空 → `ProdsetEmptyError`

---

## 三、Critic（還沒查什麼）

* `evaluation.baseline.run_ladder` 之 `feats or canonical_features` 是否被他入口誤當 production 熱路徑（本輪確認 `train_ranker`／`predict_asof` 不走此）
* 動態 SQL 自 PIPELINE 旁路讀 `philosophy_*`（AST 外；U5／U-PME Critic 同族）
* predict 漂移窗＝`resolve([asof])` vs train＝全史 panels——他日 as-of 缺覆蓋時拒載行為的產品敘事（現況 MATCH）
* advisor live UI 是否把 `n_feats=2`／validated 原則說成可交易（需 chat；本輪未打）
* `--feature-source=canonical` 研究逃生口被誤標 production 的 ops 紀律（文件已標非 PME）
* kill-switch=halt 不擋讀已 active（計畫 §2.3 故意；未另測）

---

## 四、Synthesize（呈核）

### 結論句

P2H **E123＋U-P2H** 在「真讀 prodset active、FC-empty、禁 silent canonical、PIPELINE 零 philosophy、predict GRANT 收斂、庫內 as-of 零 API、n_feats=2 誠實極窄」意義上**可呈核階段 DONE（A10）**——**前提**：對外嚴格＝「PME 晉升子集已進 fit／serve」，**不是**「可交易／確立級／生產特徵完備／已解凍」。

本輪 **無必修 code 破口**；唯一成立 finding＝文件幽靈（路線圖／計畫現況表／§2.2 語意）→ [I] 最小刷齊。

### gap_class 建議（本輪）

| ID | 建議 | 理由 |
|---|---|---|
| **G-PME-HOTPATH** | **維持 none** | 機械＋U 對抗皆綠；仍≠可交易 |
| G-PME-PRODSET | **維持 none** | 熱路徑消費端對帳成立 |
| G-PME-PROM／G-PME-ECON | **維持 partial** | 非本 U 範圍；PASS=2 誠實 |
| FZ-keep／API | **維持凍結** | 本輪零呼叫 |

### 可否「預測熱路徑已吃晉升／可交易」？

| 語義 | 可否 |
|---|---|
| S123＋U-P2H（A1–A11；含 A10） | **可呈核 YES**（本 U-P2H） |
| 真讀 prodset active（n=2）進 train／predict | **YES** |
| 可交易／確立級／解凍 API | **NO** — `evaluated_pass=0`；FZ-keep |
| 等同舊 29～35 canonical 完備 | **NO** — 誠實極窄 |
| 開更多實作／改 [N] | **NO** — 本輪不自動開 |

### 建議處置（執行層、零 [N]）

1. 本檔＝**U-P2H DONE**；Gap 維持 HOTPATH **none**（補註 U 已跑）
2. 刷路線圖／計畫／HANDOFF 幽靈（F-U-P2H-7／8／9）
3. 維持 FZ-keep；禁把 n_feats=2 說成可交易
4. `archive_push.sh --slug prodset-predict-hotpath-u-p2h`

### A10

| ID | 結果 | 證據 |
|---|---|---|
| **A10** | **PASS** | 本檔含 Find／Verify／Critic／Synthesize；Critic「未查項」已列；Gap G-PME-HOTPATH 回寫維持 none＋U DONE |
