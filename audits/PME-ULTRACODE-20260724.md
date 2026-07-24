# U-PME Ultracode — 哲學↔市場進化閉環對抗 [I]（2026-07-24）

* Steward：「**開 U-PME**」；輸入＝PME 計畫＋E12／E123 閉合＋Gap 帳本＋`evolution`／APPLY／kill 碼
* **方法**：Find→Verify→Critic→Synthesize（對齊 U5／U6 鐵律）
* **硬邊界**：不改 [N]；不解凍 FinMind／FRED；**不**重跑完整 E123 放量（引用 `run_id=5`）；可跑免 API selftest／kill 負向；**不開 U7**（無交叉幽靈升格）
* 證據錨：`audits/PME-E123-STATUS-20260724.md` · `PME-E123-CLOSED-20260724.md` · `PME-S012-STATUS-20260724.md` · `PME-PLAN-APPROVED-20260724.md` · `reports/augur_philosophy_market_evolution_loop_plan_20260724.md` · `reports/augur_pme_gap_ledger_20260724.md` · `src/augur/philosophy/evolution.py` · `scripts/{run_philosophy_evolution,apply_evolution_promotions,set_evolution_kill_switch}.py`

---

## 一、Find（攻擊面）

| 攻擊 | 假說 |
|---|---|
| APPLY 假綠 | APPLY×2 來自 skeleton SKIP／缺閘／僅單閘 PASS |
| G-PROM Goodhart | 為過門事後降 `min_abs_hac_t`／放寬 seed；多數 FAIL 被改寫成「實質過關」 |
| kill 繞過 | DB=`clear` 即可 APPLY；env halt 無效；`--force` 跳閘 |
| 隔離破口 | `features`／`models`／`universe`／`evaluation`／`ingestion`／`audit`／`catalog` import `philosophy` |
| A7 假關 | desync／missing 被標 none 或全量 validated |
| 靈魂謊稱已解 | 「自主上線」寫成已修 [N]「非自動駕駛」 |
| 生產集幽靈 | 計畫「登錄生產特徵集」但 APPLY 只翻 status／空 delta |
| 自動降級幽靈 | 閘紅宣稱「自動降級／凍結」卻只 `rejected_gate`、不改 status |

---

## 二、Verify（親驗證據 → 裁決）

| ID | 標的 | 嚴重度 | 文本／形式／實務 | 裁決 |
|---|---|---|---|---|
| **F-U-PME-1** | APPLY×2 雙閘 | **pass（真綠）** | **文本**：E123 `applied=2`。**形式**：live `run_id=5` 兩列 `inst_cumflow_position_120d`／`volume_gini_60d`：七閘皆 `PASS`；`APPLIED_NON_PASS_GATES=none`；`decided_by=evolution_engine`；`untested→validated`。**實務**：非 skeleton（skeleton＝SKIP→`rejected_gate`，unit 再證 SKIP 即使偽造 `pending_auto` 亦被 `may_apply` 拒）。 | **不成立為缺陷**；真雙綠 APPLY |
| **F-U-PME-2** | G-PROM Goodhart | **pass（誠實嚴）** | **文本**：PASS=2／FAIL=34／SKIP=6。**形式**：`config_json` 釘 `min_abs_hac_t=2`／`min_seeds=3`／`min_delta_ic=0`；交叉表 `PROM=FAIL∧ECON=PASS`＝**13**（含 `cycle_position` Δ 不穩、`days_since_high` \|hac_t\|=1.673）→ 正確 `rejected_gate`。**實務**：多數 FAIL＝門檻生效，非事後挪柱。 | **不成立為 Goodhart**；殘留＝未來 run 改 DEFAULT 門檻須另 ultracode（Critic） |
| **F-U-PME-3** | kill 繞過 | **pass** | **文本**：PME-KILL＋env OR。**形式**：selftest A5；live `AUGUR_EVOLUTION_KILL_SWITCH=halt` → APPLY `kill=halt` exit=1（DB 仍 `clear`）；`--force` → exit 2「禁止跳閘」。**實務**：env OR 不可靠清 DB  alone 繞過。 | **維持 G-PME-KILL=none** |
| **F-U-PME-4** | PIPELINE 隔離 | **pass** | **形式**：`import_isolation` exit 0；`pytest tests/test_philosophy_isolation.py` → 9 passed；PIPELINE 七 pkg grep `augur.philosophy`＝0；僅 `advisor` 讀 `retrieval`（允許）。 | **維持隔離綠** |
| **F-U-PME-5** | A7／missing 假關 | **pass（誠實 partial）** | **形式**：`status_desync(untested∩validated_*)=21`；principle `untested=24`／`validated=2`；missing／blocked_div → G-PROM／G-ECON=`SKIP`（6）。**實務**：帳本仍 **partial**；未全翻 validated。 | **不成立為假關**；維持 G-PME-STATUS partial |
| **F-U-PME-6** | 靈魂已修謊言 | **pass（已閉）** | **文本（U-PME 當輪）**：當時 `soul_wording_pending=True`、無假稱已修。**補註（2026-07-24 apply）**：Steward `SOUL-PME-B-yes`＋採納並寫入 → 靈魂／#20／A.53 已寫；`soul_wording_pending=False`；`audits/G-PME-SOUL-CLOSED-20260724.md`。 | **G-PME-SOUL=none** |
| **F-U-PME-7** | 生產特徵集幽靈 | **major（宣稱＞實作）** | **文本**：計畫 S3「翻 status、**登錄生產特徵集**、寫 apply_log」；§6「只更新 philosophy 狀態＋生產特徵登錄表」。**形式**：`apply_evolution_promotions` 僅 `UPDATE philosophy_principle.status`＋`evolution_apply_log.production_set_delta={"feature","action"}`；live 無 `production_features`／allowlist 表寫入；`canonical_features`＝evaluation 讀 panel，非 APPLY 登錄。**實務**：稱「特徵已進生產集／可交易上線」＝假綠；稱「原則 status→validated」＝真。 | **成立** → 新 **G-PME-PRODSET=partial** |
| **F-U-PME-8** | 自動降級幽靈 | **medium（用語）** | **文本**：閘紅→「不上線／自動降級或凍結」。**形式**：run5 `demote×34`／`freeze×6` 皆 `rejected_gate`；APPLY 從不消費非 `pending_auto`；`status_after_apply(demote)` 有碼但本輪無路徑觸發。**實務**：「不上線」真；「自動降級已執行」＝過讀。 | **成立（敘事）** → **G-PME-DEMOTE=doc-only** |
| **F-U-PME-9** | gate_json 信任邊界 | **low（殘留）** | APPLY 再驗 `may_apply`／七閘 PASS，**不**重算 IC／#14。偽造 `pending_auto`＋全 PASS `gate_json`（需 DB 寫入）可過。 | **知情殘留**；不升 conflict（ops／DB 信任域）；Critic 列 |

**本輪親驗指令摘要**（零 FinMind／FRED；不重跑 E123）：

* `python -m augur.philosophy.evolution --selftest` → 全通過
* `python scripts/apply_evolution_promotions.py --selftest` → 全通過
* `python scripts/set_evolution_kill_switch.py --selftest` → 全通過
* `python -m augur.audit.import_isolation` → exit 0
* `pytest tests/test_philosophy_isolation.py` → 9 passed
* `AUGUR_EVOLUTION_KILL_SWITCH=halt python scripts/apply_evolution_promotions.py --dry-run` → exit 1
* `python scripts/audit_philosophy_feature_coverage.py` → desync=21；validated=2
* DB 唯讀：`run_id=5` applied×2 七閘 PASS；PROM×ECON 交叉表如上

---

## 三、Critic（還沒查什麼）

* 未來 run 改 `DEFAULT_GATE_CONFIG` 門檻之機械哨兵（無 `verify_roadmap_pme_sentry.py`）
* APPLY 是否應強制重算 G-PROM／G-ECON（vs 信任同 run `gate_json`）
* `production_set_delta` 應對接哪張既有 registry／allowlist（產品決策；禁假造表）
* demote／freeze 是否另開「降級 APPLY」工單，或計畫改寫為「僅拒上線」
* advisor live 是否把 `validated` 原則說成可交易／確立級（需 chat；本輪未打）
* 動態 SQL 自 PIPELINE 旁路讀 philosophy 表（AST 外；U5／U6 Critic 同族）
* U7 產品閘幽靈（本輪禁開；無交叉強制）

---

## 四、Synthesize（呈核）

### 結論句

PME **E123＋U-PME** 在「本地真閘＋雙綠才 APPLY＋kill 硬拒＋隔離＋不謊稱靈魂已修」意義上**可呈核階段 DONE（A11）**——**前提**：對外嚴格＝「原則 `status→validated` 有界自動」，**不是**「特徵已登錄生產集／可交易／進化閉環產品可用／靈魂 [N] 已改」。

`run_id=5` APPLY×2＝真七閘 PASS；G-PROM 多數 FAIL＝誠實；**F-U-PME-7**＝生產集登錄仍為幽靈落點（已入帳本）。

### gap_class 建議（本輪）

| ID | 建議 | 理由 |
|---|---|---|
| G-PME-KILL | **維持 none** | env OR＋halt 再親驗 |
| G-PME-AUTO-PATH | **維持 none** | 真綠 APPLY×2；路徑非 skeleton |
| G-PME-COV | **維持 none** | S0／S1 可重跑 |
| G-PME-ECON | **維持 partial** | 本地真跑；非全綠／非解凍全量 |
| G-PME-PROM | **維持 partial** | PASS=2 誠實；非假全綠 |
| G-PME-STATUS | **維持 partial** | desync=21；禁假翻 |
| G-PME-SOUL | **none** | 2026-07-24 apply：`audits/G-PME-SOUL-CLOSED-20260724.md` |
| **G-PME-U** | **none** | 本檔＝A11／U-PME DONE |
| **G-PME-PRODSET**（新） | **partial** | apply_log delta 有；生產登錄表無 |
| **G-PME-DEMOTE**（新） | **doc-only** | 閘紅＝拒上線；降級 status 未自動執行 |

### 可否「PME 全量／進化閉環可用」？

| 語義 | 可否 |
|---|---|
| E123＋U-PME（A0–A6／A8–A11；A7 partial 知情） | **可呈核 YES**（本 U-PME） |
| 生產特徵集已登錄／預測熱路徑已吃晉升 | **NO** — F-U-PME-7 |
| A7 全閉／多數 G-PROM PASS | **NO** |
| 靈魂「非自動駕駛」[N] 已對齊 B | **YES** — G-PME-SOUL=none（`audits/G-PME-SOUL-CLOSED-20260724.md`）；自動下單仍禁 |
| 確立級／可交易／解凍 API | **NO** — FZ-keep；`evaluated_pass=0` |
| 開 U7 | **NO** — 本輪不開 |

### 建議處置（執行層、零 [N]）

1. 本檔＝**U-PME DONE**；Gap 最小 diff；計畫／路線圖標 U-PME DONE  
2. 另案：定義並實作「生產特徵登錄」真寫入（或計畫改寫為「僅 principle status」消歧）  
3. 計畫 S3 句「自動降級或凍結」→ 改「拒上線（rejected_gate）；降級另路徑」或補 demote APPLY  
4. 維持 FZ-keep；禁假關 A7；✅ 靈魂措辭已寫入（G-PME-SOUL=none）  
5. `archive_push.sh --slug philosophy-market-evolution-u-pme`

### A11

| ID | 結果 | 證據 |
|---|---|---|
| **A11** | **PASS** | 本檔含 Find／Verify／Critic／Synthesize；Critic「未查項」已列 |
