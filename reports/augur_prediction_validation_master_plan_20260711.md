# Augur 預測驗證總綱主計畫(定稿)

**日期**:2026-07-11
**檔名(落點)**:`reports/augur_prediction_validation_master_plan_20260711.md`
**性質**:計畫書(#20 v1.39.0:附所讀既有表 schema+結果落點+新表 DDL+程式規畫+分階段+驗收);30 分鐘可讀。
**查證聲明(#9/#10)**:本文所有量化數字均於 **2026-07-11** 以 `venv/bin/python` + `augur.core.db` 對本地 `augur` 庫(`table_schema='public'`)直查、或讀 repo 現行檔案實證;程式行號釘 HEAD `08356fd`。無一數字出自記憶或推估。批判審查(2026-07-11,對前後半草稿)之 10 項缺陷 F1–F10 已逐項修訂,對照表見 §8。

## 目錄

- §0 三十秒摘要與定位
- §1 驗證證據地圖(缺口①)
- §2 模型級穩健性設計(缺口②)
- §3 Schema 變更總表(新表 DDL+既有表擴充)
- §4 FREEZE 解凍 GATE 預註冊(缺口③)
- §5 分階段 V0→V1→V2
- §6 總驗收
- §7 誠實邊界與已知債
- §8 批判修訂對照(F1–F10)

---

## §0 三十秒摘要與定位

**這份計畫不是重問「有沒有 edge」。** 那題已誠實回答並落帳:`econ_verdict_rule` 5 列(DB 實查,`source_report` 欄溯源)——H20=`dead`(short_horizon 裁決報告)、H40/60/82=`thin_unestablished`(tier3 裁決報告)、H120=`thin_unestablished`(H120 裁決報告);機率校準後 Brier 僅薄勝基線(H20 0.2477 / H40 0.2463 / H60 0.2475 / H120 0.2468,vs base-rate 0.2500,`probability_calibrator` 實查)。**edge 是薄的,系統已經誠實說了。**

本計畫問的是另一題:**「憑什麼相信這條鏈的每一環?」**——並在 FREEZE(as-of 2026-05-31)不破、零新資料的前提下,補齊三個缺口:

| 缺口 | 交付 | 落在 |
|---|---|---|
| ① 驗證證據地圖 | raw→呈現逐環「已驗什麼/工具/落帳/report·commit/殘留」總綱 + 機械證據帳本 `validation_evidence`(新表) | §1、§3.1 |
| ② 模型級穩健性系統跑 | 子期間校準穩定/橫斷面 rank 穩定/gross_margin 提拔↔canonical 斷點調查——全部在**既有** OOS/特徵面板上重算,判準先凍後跑 | §2、§3.2 |
| ③ FREEZE 解凍 GATE 預註冊 | 接新資料/live 再驗證之通過判準,**現在凍結**(B2 GATE-lite 精神:先凍結後開跑、不挪門柱) | §4、§3.3 |

**三條紅線**:(a) FREEZE 內完成,不追新資料、不以資料過期為缺陷;(b) Ridge 決定性——seed 軸對它零資訊,穩健性軸誠實選子期間/特徵擾動/宇宙子集(§2.0);(c) 產出=**裁決建議**,判準值與選項採行由決策層人拍板(靈魂:系統建議、人決策)。

---

## §1 驗證證據地圖(缺口①)

### 1.1 逐環證據矩陣(實查彙整)

以下每列之「已驗」均可 trace 回工具輸出/DB 落帳/report·commit(#10);「殘留」列為誠實債、非既成綠燈。

| # | 環節(chain_link) | 已驗什麼 | 工具(檔:函式) | 落帳表 | report / commit | 殘留 |
|---|---|---|---|---|---|---|
| E1 | raw 對帳(`raw`) | byte-level 對帳、敵①(假資料)attestation | `scripts/reconcile_audit.py` | **無落帳表——stdout+exit-code 工具**(實查:全庫無 `%reconcil%` 表、該檔零 INSERT/UPDATE;F1 修訂,誠實標示) | SOP master §PHASE 5 ✅(`augur_prediction_sop_master_20260706.md`) | 重驗=人跑該 script 看 exit code(evidence 列 `check_type='script_exit'`,§1.3);FREEZE 後不追新(治權判準、非缺陷) |
| E2 | 特徵層 anti-leakage(`feature`) | 兩輪審計(4 靶深查+13 agent 對抗掃 5 模組);4 洩漏確認並修復重建:`price_to_10yr` 前向還原分子、`gross_margin_pctile` 陳舊冒充當季、IC 工具存活偏誤、`chip.top_holders_pct` 無公布 gate(1A +7日 gate);重建後 `feature_values`=**2,418,655 列/35 特徵/35 panel**(2007-12-31→2026-05-31,DB 實查) | `scripts/rebuild_feature.py`(registry 驅動,#12 不 hand-patch) | `feature_values` | `augur_antileakage_audit_20260711.md`;commit `cd8b35e`(第一輪)、`abf5da8`(chip 1A+macro PIT) | macro 兩潛伏債(零現行消費者,觸發條件已定於審計 §4);`release_lag` 金融業 60 日 vs 碼 45 日已明文記錄休眠 |
| E3 | 特徵提拔紀律(`promotion`) | 四道漏斗+as-of HAC Eff-t+多 seed 增量+經濟終關 | `scripts/verify_candidate_promotion.py`、`src/augur/evaluation/metrics.py:89 effective_t_hac`(Newey-West/Bartlett,禁裸 iid;F5c 全路徑) | (研究流程) | 方法論 SSOT `augur_feature_discovery_methodology_20260626.md` §四;`augur_prediction_stageB_promotion_verdict_20260706.md` | **提拔↔canonical 銜接無契約**(§2.3 斷點) |
| E4 | 特徵→模型口徑鎖(`gate`) | canonical=全 panel 交集 gate(`src/augur/evaluation/baseline.py:30 canonical_features`)→ **28 特徵**(35−7 sub-coverage,DB 實查,名單見 §2.3);`feats_hash` 凍結、predict 載入不符即拒(`models/artifact.py`) | `baseline.canonical_features`、`artifact.feats_hash` | `model_registry.feats_hash` | — | 交集 gate **靜默剔除**、不回報誰被踢(§2.3 契約化) |
| E5 | 模型訓練(`train`) | 4 生產模型 `RankRidge_H{20,40,60,120}_2026-05-31_seed42_ce62866bb62de38b`(`model_registry` 4 列 11 欄,created 2026-07-11,實查);訓練/驗證/上線全複用 baseline 同一 helper(#12 零雙軌);**面板重建後乾淨重訓與重建前同值到 5 位小數**(2026-07-11 管線決定性實證) | `scripts/train_ranker.py` | `model_registry` | — | survivorship 債 b:`core_universe_asof` 實為當前存活名單→as-of IC 帶樂觀偏誤(`train_ranker._train_note` 明標;`augur_prediction_survivorship_economic_verdict_20260708.md`) |
| E6 | OOS 樣本(`oos`) | `probability_oos_sample` **42,456 列**(H20 10,703/H40 10,699/H60 10,699 各 25 panel,2016-12-31→2025-12-31;H120 10,355/24 panel,→2025-09-30;exit_date 零 NULL,全數 DB 實查);`--verify` purge 機械斷言全綠 | `scripts/build_probability_oos_sample.py --verify`;`walkforward.splits`(embargo 保證下界=h+feature_lag 交易日) | `probability_oos_sample` | e2e 主計畫 `augur_omniscient_e2e_master_plan_20260710.md` §6.2 | 折級樣本承 E5 survivorship 債 |
| E7 | 機率校準(`calibration`) | Platt×4 horizon,expanding purge fit(`purge_verified=true` 全 8 列);n_fit_folds 24/24/24/23;Brier/ECE 落帳(ECE 0.0085/0.0082/0.0157/0.0088) | `scripts/calibrate_relative_probability.py --fit/--report` | `probability_calibrator`(8 列=4 horizon×2 git_sha 重跑同值) | e2e §6.3;憲章 v1.40.0 相對機率誠實判準 | **子期間穩定未驗**(§2.1 補);H60 ECE 偏高待判讀 |
| E8 | 機率呈現(`probability`) | P(勝同儕中位數) **1,376 列/1 panel**(as-of 2026-05-31,DB 實查);econ_verdict 判死標籤同列硬綁;誠實 UI | `calibrate_relative_probability.py --emit` | `prediction_probability` | commit `7fd3426`(誠實 UI) | 僅 1 panel=FREEZE 快照,live 呈現屬解凍後 |
| E9 | 經濟終判(`economic`) | 扣真成本(0.00585 來回)非重疊 walk-forward 投組;DSR deflation;判停閾 **6 列(4 frozen)**、trial_ledger **32 列**(實查) | `scripts/run_economic_eval.py`+`evaluation/portfolio.py:run_backtest`;`deflate_headline_verdict.py` | `econ_verdict_rule`(5 列)、`judgestop_threshold`、`trial_ledger` | stageCD/stageD/tier3/short_horizon/H120/deflation 六份裁決報告(20260706–09) | H120 近期非重疊 n≈8 小樣本(registry note 明標) |
| E10 | 持續常綠(`harness`) | smoke/advisor 回歸/Qdrant 影子每日機械綠檢;再驗證 harness(ledger **204** 列/baseline **4**/verdict **2**,實查) | `scripts/daily_green.py`;`revalidate*.py` 系列 | `revalidation_ledger/baseline/verdict` | `augur_prediction_revalidation_harness_plan_20260708.md` | 軌B 衰減偵測需 live 資料=解凍後才有牙 |

### 1.2 地圖落點設計(#29b 裁決:資料還是文件?)

**裁決:雙層落點——敘事層=文件、機械層=DB 表。**

- **敘事層(為何可信、caveat、判讀方法)是「論證」不是「資料」**:不增減、不由外部產生、讀者是人→住 `reports/`(#16),即本報告 §1.1 + 各 SSOT 裁決報告。SOP master 附錄「現況宣稱來源對照」由本 §1.1 承接升級。
- **機械層(claim→重驗方式→狀態)按 #29b 三問皆「資料」**:策展的(每列人審後入)、會增減(審計/修復/重訓都新增或翻紅)、可外部產生(admin INSERT 零改碼)→**住 DB 表 `validation_evidence`**(DDL §3.1)。
- **為何是表、不是視圖**:證據列的本體是**策展斷言+其重驗方式**(不存在可導出它的上游表)→只能是表。
- **重驗方式三型(F1 修訂)**:`check_type IN ('sql','script_exit','manual')`——SQL 型(如「oos 恰 42,456 列且 exit_date 零 NULL」)自動重驗;**script_exit 型**(E1 對帳這種 stdout+exit-code 工具)記白名單命令、`--run --with-scripts` 才執行採 exit code,預設跳過並提示;manual 型(方法論判讀)只能人審更新。
- **斷言設計原則(F6 修訂)**:**可增長之落帳表用語意型斷言**(如「每 horizon 最新 calibrator 列 purge_verified 且 brier<baseline」——calibrator 合法再 fit 不翻紅);**凍結快照才用精確計數**(如 FREEZE 內 oos=42,456;解凍重建時該列隨 GATE 流程更新、非假警報)。
- **「決定行為」的臨門一腳**:解凍 GATE(§4)以 `verify_validation_evidence.py --strict` 全綠(已知債紅列須先人裁除名或修復)為機械前置之一——帳本從「文件索引」升格為「gate 消費的資料」,#29b 資格確立。
- **誠實邊界**:一列 `green` 只代表「該斷言此刻對 DB 重驗為真」,**不**代表方法論正確(那住報告、由人審);已知債(E5 survivorship、E3/E4 gm 斷點、E2 macro 潛伏債)以 `red`/`amber` 誠實入帳——帳本存在的意義正是讓紅列無處可藏。

### 1.3 程式規畫(#20 v1.39.0 (b))

| 檔 | 角色 | 關鍵函式(簽名) | 輸入 | 輸出 |
|---|---|---|---|---|
| `scripts/migrate_validation_evidence_ddl.py`(新) | 冪等建表+種子 bootstrap(§1.1 矩陣轉 ~20 列種子,10 環節各≥1;#29b 種子一次性遷移、SSOT=DB)+**§3.2 兩條既有表 CHECK 擴充之協調說明(實際 ALTER 住各自 DDL 檔,#12)** | 遵 `migrate_probability_ddl.py` 模式:無參數唯讀印矩陣/`--run` 冪等/`--verify` exit 0/1 | — | `validation_evidence` |
| `scripts/verify_validation_evidence.py`(新) | 逐列重驗+狀態更新 | `_load_rows(cur)->list[dict]`;`_run_sql_check(cur,check_sql)->bool`(斷言回單列單欄 boolean、唯讀);`_run_script_check(check_cmd)->bool`(僅 `--with-scripts`;命令須以 `venv/bin/python scripts/` 開頭之白名單機械擋);`_update_status(cur,id,ok,note)`;CLI:`--list`/`--run [--id X] [--with-scripts]`/`--strict`(任一非 green→exit 1,供 daily_green 選配步驟與解凍 GATE) | `validation_evidence`+各 check_sql 指涉表(唯讀) | 更新 `status`/`status_note`/`last_verified_at` |

`check_sql` 安全約束:僅允許 SELECT(前綴白名單機械擋)、必回 boolean;寫壞之列 `--run` 標 `red`+note,不 crash 整批(#15 誠實)。範例:

```sql
-- E7(語意型,表可增長;F6):
SELECT bool_and(purge_verified AND brier < brier_baseline) FROM (
  SELECT DISTINCT ON (horizon) purge_verified, brier, brier_baseline
  FROM probability_calibrator ORDER BY horizon, created_at DESC) t;
-- E6(凍結快照型,FREEZE 內精確計數;F6):
SELECT count(*) = 42456 AND bool_and(exit_date IS NOT NULL) FROM probability_oos_sample;
```

### 1.4 驗收 SQL(F5b 修訂:枚舉精確)

```sql
-- (1) 種子齊:總數 ≥18 列,且 10 個 chain_link
--     ('raw','feature','promotion','gate','train','oos','calibration','probability','economic','harness')
--     各 ≥1(與 §3.1 CHECK 枚舉一字不差):
SELECT chain_link, count(*) FROM validation_evidence GROUP BY 1 ORDER BY 1;
-- (2) 重驗後:已知債紅列存在(不許全綠假象)、其餘 green:
SELECT evidence_id, status FROM validation_evidence WHERE status <> 'green' ORDER BY 1;
--     期望:至少 E5 survivorship 債、E3/E4 gm 斷點契約列非 green
-- (3) --strict 行為:紅列在 → exit 1(shell 驗)
```

---

## §2 模型級穩健性設計(缺口②)

### 2.0 共同紀律:軸的誠實選擇+判準先凍後跑

**Ridge 決定性 → seed 軸零資訊**(同資料同解,「多 seed 全一致」是假穩健)。誠實軸=**資料切法與模型擾動**:子期間(§2.1)、相鄰 panel rank 穩定/LOFO/特徵擾動/宇宙子集(§2.2)。唯一引入隨機處(噪聲擾動、隨機子集)守 #11 固定 seeds{41,42,43} ≥3。全部在既有 `probability_oos_sample`/`feature_values` 上重算,**零新資料、零 API**。

**「重切既有 OOS」的誠實口徑(F8 修訂)**:§2.1 與 rank 穩定確為重切既有 OOS;但 **LOFO 與特徵擾動必然涉及重訓/重打分**(oos 表只有 score/rank_pctile、無 per-feature 貢獻)——仍零新資料(合規),但口徑必須先凍:

- **LOFO 口徑凍結=選 (i) 真 LOFO 全 walk-forward 重訓**:逐特徵剔除→同一 walk-forward 折結構重訓 Ridge 重打分。語意=「該特徵之資訊邊際貢獻(含係數重估、共線性重分配)」,正是「單點依賴」要問的問題。成本誠實:28 特徵×4 horizon×≤24 折≈2,688 次 Ridge 擬合——閉式解、本地零 usage(#28),可行。
- **明文棄用 (ii) 固定係數刪特徵重打分**:係數不重估、共線性不重分配→量的是「分數對缺格的敏感度」而非依賴,**會系統性高估單點依賴**(共線雙生特徵無法接手)——與判準語意不符,棄用並留此紀錄防未來誤採。

**預註冊(鏡射 B2 GATE-lite:先凍結、後開跑、不挪門柱)**:下表判準值為**建議值**,用戶拍板後、開跑前 INSERT 進 `judgestop_threshold`(新 track `'R_robust'`,`frozen=true`,`source_ref='augur_prediction_validation_master_plan_20260711.md §2.0'`,CHECK 擴充見 §3.2)——跑完不得回頭調。**horizon 口徑定案(F3 修訂)**:五列一律 `horizon=0` 全域哨兵(與既有 6 列一致、PK 相容,實查現行全 horizon=0);threshold 全 horizon 同值→單列,**評估逐 horizon 進行**、語意寫入 note;未來若需 per-horizon 差異值,PK(policy_key,horizon) 天然容納另立具體列。**口徑亦凍**:LOFO=(i) 真重訓,寫入 R 列 note——凍的是值+口徑。R 軌性質=**annotate/review、非自動判停**(econ 已判 thin,本節守的是「機率數字可不可信」;觸紅→人裁)。

| policy_key(建議) | threshold(建議) | horizon | 語意 |
|---|---|---|---|
| `calib_late_skill_floor` | 0.0 | 0(哨兵,逐 horizon 評) | 季頻 era 之 median 折級 skill(=brier_baseline−brier)≥0:近代校準不失效 |
| `calib_late_ece_ceiling` | 0.05 | 0(同上) | 季頻 era ECE ≤ 0.05 |
| `rank_autocorr_annotate` | 0.3 | 0(同上) | 相鄰**季頻** panel 之 median Spearman <0.3 → annotate+換手一致性複核(語意防誤讀見 §2.2) |
| `lofo_ic_signflip_zero` | 0.0 | 0(同上) | 任一 LOFO 剔除使該 horizon 全期 median rank IC 翻負 → 單點依賴紅旗 |
| `subset_ic_sign_agree` | 0.75 | 0(同上) | 宇宙隨機半子集 IC 與全宇宙同號率 ≥0.75 |

**「先凍後跑」機械錨(誠實補強)**:實查 `judgestop_threshold` 現無時間戳欄(7 欄:policy_key,horizon,track,threshold,frozen,source_ref,note)→ §3.2 補冪等 `ADD COLUMN created_at`(既有 6 列 created_at=遷移時刻、非原凍結時刻,note 明記、不冒充);`run_model_robustness.py` 開跑守門斷言:R 五列 frozen=true 皆在否則 exit 1,且 ledger `run_at > max(R 列 created_at)` 供 §2.5 機械驗收。

**結果落點=既有 `revalidation_ledger`(stage 新值 `'R'`,§3.2)**,不建新表(#29c 復用;該表本就是通用 metrics 帳本,`config` 欄攜 JSON 序列化之 axis/era/seed)。

**所讀既有表 schema 節錄(實查)**:

```
probability_oos_sample(horizon int CHECK in(20,40,60,82,120), panel_date date, model_family text,
  stock_id text, score float8, rank_pctile float8, fwd_ret float8, peer_median_ret float8,
  label_beat_median bool, exit_date date, git_sha text, created_at timestamptz)
feature_values(panel_date date, stock_id varchar, feature varchar, value numeric)
probability_calibrator(calibrator_id, horizon, method, fit_asof, n_fit_samples, n_fit_folds,
  purge_verified, params jsonb, brier, brier_baseline, ece, reliability_bins jsonb, family_note, git_sha, created_at)
revalidation_ledger(run_at, as_of_date, stage, horizon, model, config text,
  metric_name, metric_value, n_periods, hac_t, note)   -- stage CHECK 'revalidation_stage_chk'(B,C,D)→擴 R
judgestop_threshold(policy_key, horizon, track, threshold, frozen, source_ref, note,
  PK(policy_key,horizon))                               -- track CHECK 'chk_js_track'(A_annotate,B_decay)→擴 R_robust
```

### 2.1 軸 (a):子期間校準穩定

**資料事實(實查)**:OOS 25 panel=**年頻 2016-12-31…2020-12-31(5 panel)+季頻 2021-03-31…2025-12-31(20 panel)**;era 邊界=**2021-01-01,按資料 cadence 切、不按折數機械均分**(前 12 折/後 12 折會把兩種節奏混在同 era,量出的是節奏差不是時代差)。expanding-purge 可評折 24(首折無前置已實現樣本;H120=23、末 panel 2025-09-30)。

**做法**:複用 `calibrate_relative_probability.py` 之 expanding-purge 折迴圈(#12 不另寫第二套)產出**折級** brier/brier_baseline/ece,按 era 聚合:

- 每 horizon×era:median 折級 skill(=brier_baseline−brier)、era ECE(era 內樣本合併算)、折級 skill 之 min/max(誠實展示分佈、非只報中位數)。
- **判準(凍結後)**:季頻 era median skill ≥ `calib_late_skill_floor`(0.0)且 era ECE ≤ `calib_late_ece_ceiling`(0.05)。年頻 era 為描述性參照(樣本僅 4-5 折,不設判準、不假裝有檢定力)。
- **附帶問題**:H60 全期 ECE 0.0157 偏高(其餘 0.0082–0.0088)——era 分解看它集中在哪個時代,判讀寫入穩健性報告。

**落帳**:`revalidation_ledger` stage='R',config 如 `{"axis":"calib_era","era":"quarterly"}`,metric_name ∈ ('brier_skill_median','ece_era','brier_skill_min','brier_skill_max'),n_periods=折數,hac_t=NULL(annotate 性質)。

### 2.2 軸 (b):橫斷面 rank 穩定・單點依賴・宇宙子集

**(b1) 相鄰 panel rank 自相關**:對每 horizon,取相鄰**季頻** panel(20 panel→19 對)兩期皆在之股票交集,算 score 之 Spearman;年頻對(4 對)與跨節奏邊界對(2020-12-31→2021-03-31)另列描述性(間隔不同、期望值不同,不與季頻混評)。判準:季頻 median <`rank_autocorr_annotate`(0.3)→annotate。
**語意防誤讀(F9 修訂,寫入 ledger note 與報告)**:此值量的是**訊號換手率**——低值可能是季頻訊號本性(如 chip 類快變因子)而非不穩健;annotate-only,**解凍後不得被誤當紅旗裁決依據**,觸發時的正確動作=複核換手成本一致性(econ 鏈已扣真成本,低自相關→高換手→驗證 portfolio 回測換手假設仍成立),非直接判劣。

**(b2) LOFO 單點依賴(口徑=§2.0 凍結之真重訓)**:逐特徵(28 canonical)剔除→walk-forward 重訓重打分→全期逐 panel rank IC。判準:任一剔除使該 horizon 全期 median rank IC 翻負(<`lofo_ic_signflip_zero`)→單點依賴紅旗、人裁。副產品:28 特徵之邊際貢獻排序表(入穩健性報告,供未來特徵治理參照、不自動除名)。

**(b3) 特徵擾動(描述性,不設判準——避免無據門檻)**:對標準化特徵加 N(0, 0.1²) 噪聲(建議值,拍板點),seeds **{41,42,43}**(#11 ≥3);metric=逐 panel Spearman(基準 score, 擾動 score) 之 median/min。落帳供人判讀分數對輸入噪聲之敏感度,不觸發任何自動動作。

**(b4) 宇宙子集**:隨機半切 seeds {41,42,43}×2 半=每 panel 6 子集;每子集逐 panel rank IC 與全宇宙 IC 同號率。判準:同號率 ≥`subset_ic_sign_agree`(0.75)。市值大小半切(若面板內有現成市值特徵可切)另列描述性——凍結判準只繫於**確定可算**的隨機半切,不繫於待確認的資料欄(防判準凍了才發現算不出=被迫挪門柱)。

### 2.3 gross_margin_pctile 提拔↔canonical 斷點調查

**斷點事實(本計畫已實查定位)**:`gross_margin_pctile` 覆蓋 **34/35 panel,缺的唯一 panel=2007-12-31(最早一個)**;交集 gate(`baseline.py:30`,要求全 35 panel)故將其靜默剔除。同批被剔的 7 特徵(實查,panel 數):`gov_bank_net_buy_60d`(19)、`inst_cumflow_position_60d/120d`(30/30)、`institutional_net_buy_ratio_20d`(30)、`price_to_10yr`(31)、`top_holders_pct`(32)、`gross_margin_pctile`(34)。

**張力**:margin_cycle.py docstring(L10-11 實查)自述 2026-06-28 過四道漏斗+經濟驗證(Ridge/H60 ΔSharpe+0.12/ΔCalmar+0.23、逐期 t=2.05、LOO 不翻負)——**提拔了卻不在生產**,且無任何機械記錄揭露此事(E3→E4 銜接無契約)。

**調查項(V1 執行)**:
1. **缺因確認**:2007-12-31 缺列的資料層原因(假說:percentile 需 8 季毛利歷史、最早 panel 財報源覆蓋不足——以 raw 財報表實查確認,不猜)。
2. **影響量化**:2007-12-31 距最早 OOS panel(2016-12-31)9 年——該 panel 只進訓練不進 OOS 評估;量化「若 gate 起點改 2008-12-31」canonical 會變成幾特徵、feats_hash 是否變。

**選項(人拍板,本計畫不代裁)**:
- (a) canonical gate 加「最小覆蓋起點」參數(如 2008-12-31 起全覆蓋即入)——**feats_hash 變→重訓+重跑 OOS/校準/經濟全鏈**,FREEZE 內技術可行但屬判準變更=決策層;
- (b) 誠實除名:承認「提拔但未入生產」,提拔紀錄補 exclusion 註記;
- (c) 維持現狀+**契約化**(本計畫內完成):`validation_evidence` 增契約列(check_type='sql')——斷言「交集 gate 剔除集合=已知已文檔化之 7 特徵」,未來任何新靜默剔除即翻紅;gm 列標 `red` 直到人裁 (a)/(b)。

本計畫內只做 1+2+契約化+紅列入帳;(a) 之重訓不自動執行。

### 2.4 程式規畫(F4 修訂:補齊 #20(b))

| 檔 | 角色 | 關鍵函式(簽名) | 輸入(讀) | 輸出(寫) |
|---|---|---|---|---|
| `scripts/run_model_robustness.py`(新) | 缺口②五軸單一參數化工具(#29c) | `_assert_prereg_frozen(cur)->None`(R 五列 frozen 皆在否則 exit 1;先凍後跑守門);`_era_calibration(cur,h)->list[Row]`(§2.1,複用 calibrate 模組折迴圈);`_rank_autocorr(cur,h)->list[Row]`;`_lofo(conn,h)->list[Row]`(真重訓,複用 train_ranker/baseline helper #12);`_perturb(conn,h,seeds=(41,42,43))->list[Row]`;`_universe_subsets(conn,h,seeds=(41,42,43))->list[Row]`;`_write_ledger(cur,rows)`(stage='R');`main(argv)` | `probability_oos_sample`、`feature_values`、`probability_calibrator`、`judgestop_threshold`(唯讀) | `revalidation_ledger`(stage='R') |

CLI 指令矩陣(#29d):`--axis {calib,rank,lofo,perturb,subset,all}` / `--horizon {20,40,60,120}` / `--dry-run`(算不落帳);無參數 graceful 印矩陣(#29a)。實測分級:`--dry-run` 單 horizon 單軸實跑驗證,LOFO 全量屬本地放量(零 API、零 usage,#28 本地優先)。斷點調查(§2.3)=查詢+報告,不另立 script(#29c 不為一次性分析立永久工具);契約化落於 validation_evidence 種子列。

### 2.5 驗收

```sql
-- (1) 判準先凍後跑(機械):
SELECT count(*)=5 AND bool_and(frozen) FROM judgestop_threshold WHERE track='R_robust';
SELECT bool_and(l.run_at > t.mx) FROM revalidation_ledger l,
  (SELECT max(created_at) mx FROM judgestop_threshold WHERE track='R_robust') t
 WHERE l.stage='R';
-- (2) 五軸×4 horizon 落帳齊(perturb/subset 各含 3 seeds):
SELECT config, count(*) FROM revalidation_ledger WHERE stage='R' GROUP BY 1 ORDER BY 1;
-- (3) FREEZE 不破:
SELECT max(panel_date) <= DATE '2026-05-31' FROM feature_values;
```

人工驗收:穩健性報告(`reports/augur_model_robustness_20260711.md`,#16)含各軸判讀+H60 ECE 分解+gm 斷點調查+選項 (a)/(b)/(c) 呈人拍板;觸紅列=人裁留痕、非自動動作。

---

## §3 Schema 變更總表

### 3.1 新表 `validation_evidence`(住所=新檔 `scripts/migrate_validation_evidence_ddl.py`)

```sql
CREATE TABLE IF NOT EXISTS validation_evidence (
  evidence_id      text PRIMARY KEY,              -- 如 'E6_oos_frozen_rowcount'
  chain_link       text NOT NULL CHECK (chain_link IN
                     ('raw','feature','promotion','gate','train','oos',
                      'calibration','probability','economic','harness')),
  claim            text NOT NULL,                 -- 人話斷言
  check_type       text NOT NULL DEFAULT 'sql'
                     CHECK (check_type IN ('sql','script_exit','manual')),   -- F1
  check_sql        text,                          -- sql 型:唯讀 SELECT、回單列單欄 boolean
  check_cmd        text,                          -- script_exit 型:白名單命令(--with-scripts 才執行)
  source_ref       text NOT NULL,                 -- report 路徑/commit(#10 溯源)
  status           text NOT NULL DEFAULT 'unverified'
                     CHECK (status IN ('green','amber','red','unverified')),
  status_note      text,
  last_verified_at timestamptz,
  created_at       timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT chk_ve_sql_presence CHECK (check_type <> 'sql' OR check_sql IS NOT NULL),
  CONSTRAINT chk_ve_cmd_presence CHECK (check_type <> 'script_exit' OR check_cmd IS NOT NULL)
);
COMMENT ON TABLE validation_evidence IS
  '驗證證據帳本(缺口①機械層):策展斷言+重驗方式;green=斷言此刻對 DB 為真,非方法論背書;已知債紅列誠實入帳;解凍 GATE 之 --strict 前置消費此表';
```

### 3.2 既有表擴充(F2 修訂:constraint 實名+住所檔+同步義務)

**ALTER 住各自 DDL 住所檔(#12 單一住所),非集中在新遷移**:

```sql
-- 住所=scripts/migrate_revalidation_ledger_ddl.py(實查該檔為 revalidation_ledger DDL 唯一住所);
-- constraint 實名=revalidation_stage_chk(實查 pg_constraint):
ALTER TABLE revalidation_ledger DROP CONSTRAINT IF EXISTS revalidation_stage_chk;
ALTER TABLE revalidation_ledger ADD CONSTRAINT revalidation_stage_chk
  CHECK (stage IN ('B','C','D','R'));

-- 住所=scripts/migrate_judgestop_ddl.py;constraint 實名=chk_js_track(實查):
ALTER TABLE judgestop_threshold DROP CONSTRAINT IF EXISTS chk_js_track;
ALTER TABLE judgestop_threshold ADD CONSTRAINT chk_js_track
  CHECK (track IN ('A_annotate','B_decay','R_robust'));

-- 先凍後跑機械錨(§2.0;既有 6 列回填值=遷移時刻,note 明記非原凍結時刻、不冒充):
ALTER TABLE judgestop_threshold ADD COLUMN IF NOT EXISTS created_at timestamptz NOT NULL DEFAULT now();
```

**同步義務(#19 跨檔一致,誠實校正 F2 之斷言)**:實查 `migrate_judgestop_ddl.py` 為 `--check`(非 `--verify`)且 `_verify` 為 **print-only 不 assert**(L92-100)——擴充**不會**使其機械翻紅;但該檔 L42 之 in-file CREATE TABLE CHECK 定義與 L87-88 驗證清單輸出**須同步改為擴充後集合**(否則 fresh DB 重跑遷移會建回舊 CHECK=跨檔不一致);`migrate_revalidation_ledger_ddl.py` 同理。改後各跑一次 `--check`/`--verify` 迴歸確認。

### 3.3 新表 `prediction_unfreeze_gate`

DDL 全文與 trigger 見 §4.1(住所=新檔 `scripts/migrate_unfreeze_gate_ddl.py`)。

---

## §4 FREEZE 解凍 GATE 預註冊(缺口③;本計畫最高值)

### 4.0 定位:管什麼、不管什麼(補充不取代、引用不複述)

**一句話**:把「將來接新資料/live 再驗證時,怎樣才算通過」的**判準值現在凍結入 DB**,解凍當天只執行、不得邊看結果邊定標準。

| 既有機制 | SSOT | GATE 與它的關係 |
|---|---|---|
| FREEZE(as-of 2026-05-31) | 原則精華 v1.8.0「資料完整性判準·FREEZE」 | **不動**。as-of 更新=治權參數、用戶決策入憲,GATE 不代行、不觸發解凍;GATE 只凍結「解凍後的通過判準」 |
| judgestop 兩軌三態 | `scripts/migrate_judgestop_ddl.py`+`judgestop_threshold` | judgestop=**部署後持續衰減監測**;GATE=**解凍當下一次性准入閘**。GATE 快照 judgestop frozen 列之值、evaluate 時斷言等值——引用不另立分叉常數(#12) |
| live 再驗證流程 | SOP 主計劃 `reports/augur_prediction_sop_master_20260706.md`(STAGE D/軌B) | 流程步驟 SSOT 在 SOP;GATE 只凍「通過判準值」。補充不取代 |
| 預註冊前例 | `deliberation_bench_batch`(`migrate_deliberation_ddl.py` L161-169)+`benchmark_deliberation.py`(sha 漂移拒跑 L313-315、`preregistered_at < min(run_at)` 斷言 L393) | **鏡射** B2 模式:jsonb 快照+`preregistered_at`+開跑前 sha 漂移拒跑+先凍後跑斷言 exit 1(均實查) |

**對 B2 模式的一項升級(有據)**:B2 防挪門柱只靠 CLI 斷言;解凍在數月後、可能異機異 session,故本 GATE 加 **DB trigger 機械防挪門柱**(安全繫於機械閘,與本庫既有 `staging_source_gate` trigger 風格一致——實查 pg_trigger 存在)。

### 4.1 表 DDL+trigger(新檔 `scripts/migrate_unfreeze_gate_ddl.py`,冪等;#12 DDL 單一住所;**F10 修訂:狀態轉移白名單**)

```sql
CREATE TABLE IF NOT EXISTS prediction_unfreeze_gate (
  gate_id          text PRIMARY KEY,                  -- 'unfreeze_'||12hex(鏡射 B2 batch_id)
  purpose          text NOT NULL DEFAULT 'unfreeze'
                     CHECK (purpose IN ('unfreeze','adhoc')),
  criteria         jsonb NOT NULL,                    -- §4.2 五 gate 判準快照(值+口徑+溯源)
  criteria_sha     text  NOT NULL,                    -- 正規化 json sha256[:16](挪門柱斷言錨)
  status           text  NOT NULL DEFAULT 'draft'
                     CHECK (status IN ('draft','frozen','evaluated_pass','evaluated_fail','superseded')),
  preregistered_at timestamptz NOT NULL DEFAULT now(),
  approved_by      text,                              -- 人拍板留痕(判準值=決策層,AI 不代拍)
  approved_at      timestamptz,
  git_sha          text NOT NULL,
  evaluated_at     timestamptz,
  result_snapshot  jsonb,                             -- evaluate 逐 gate 機械 pass/fail 快照
  evaluation_ref   text,                              -- 裁決報告路徑(reports/,#16 命名)
  note             text,
  CONSTRAINT chk_ug_frozen_signed CHECK
    (status <> 'frozen' OR (approved_by IS NOT NULL AND approved_at IS NOT NULL)),
  CONSTRAINT chk_ug_eval_signed CHECK
    (status NOT IN ('evaluated_pass','evaluated_fail')
     OR (approved_at IS NOT NULL AND evaluated_at IS NOT NULL))
);

CREATE OR REPLACE FUNCTION unfreeze_gate_no_goalpost() RETURNS trigger AS $$
DECLARE legal boolean;
BEGIN
  IF TG_OP = 'DELETE' THEN
    IF OLD.status <> 'draft' THEN
      RAISE EXCEPTION 'unfreeze gate %: 非 draft 不得刪(留痕;廢止=status superseded)', OLD.gate_id;
    END IF;
    RETURN OLD;
  END IF;
  -- (1) 非 draft 後 criteria 不可變:
  IF OLD.status <> 'draft'
     AND (NEW.criteria_sha IS DISTINCT FROM OLD.criteria_sha
          OR NEW.criteria::text IS DISTINCT FROM OLD.criteria::text) THEN
    RAISE EXCEPTION 'unfreeze gate %: 已凍結,criteria 不得變更(挪門柱);另立新 gate、舊列 superseded', OLD.gate_id;
  END IF;
  -- (2) 簽核欄凍後鎖定:
  IF OLD.status <> 'draft' AND OLD.approved_at IS NOT NULL
     AND (NEW.approved_by IS DISTINCT FROM OLD.approved_by
          OR NEW.approved_at IS DISTINCT FROM OLD.approved_at) THEN
    RAISE EXCEPTION 'unfreeze gate %: 凍結後簽核欄不得改', OLD.gate_id;
  END IF;
  -- (3) 狀態轉移白名單(F10:堵 frozen→draft 兩步降級挪門柱——回退 draft 改 criteria 再凍=繞過(1)):
  IF NEW.status IS DISTINCT FROM OLD.status THEN
    legal := (OLD.status = 'draft'  AND NEW.status IN ('frozen','superseded'))
          OR (OLD.status = 'frozen' AND NEW.status IN ('evaluated_pass','evaluated_fail','superseded'));
    IF NOT legal THEN
      RAISE EXCEPTION 'unfreeze gate %: 非法狀態轉移 %→%(白名單:draft→frozen|superseded;frozen→evaluated_*|superseded;evaluated_*/superseded=終態不可回改,複核=另立新 gate)',
        OLD.gate_id, OLD.status, NEW.status;
    END IF;
  END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_unfreeze_no_goalpost ON prediction_unfreeze_gate;
CREATE TRIGGER trg_unfreeze_no_goalpost
  BEFORE UPDATE OR DELETE ON prediction_unfreeze_gate
  FOR EACH ROW EXECUTE FUNCTION unfreeze_gate_no_goalpost();

COMMENT ON TABLE prediction_unfreeze_gate IS
  'FREEZE 解凍 GATE 預註冊(鏡射 deliberation_bench_batch B2):判準先凍結後評估,挪門柱=trigger 狀態白名單拒+CLI exit 1;判準值人拍板(approved_by 留痕);唯記錄面、不進預測管線';
```

### 4.2 criteria jsonb 快照內容(五 gate;引用值=DB 現值快照+溯源鍵)

```jsonc
{
  "scope": {
    "freeze_asof": "2026-05-31",
    "horizons": [20, 40, 60, 120],            // 封閉集(build_probability_oos_sample.py:34 HORIZONS,實查)
    "h82_excluded": "econ_verdict_rule 有 82 列但 HORIZONS 封閉集無 82(D1(a) 條件觸發未啟用),GATE 誠實不含",
    "cells": ["ridge_H60_LO", "ridge_H120_LO"],
    "universes": ["asof_incumbent", "pit_broad"],
    "model_ids": ["RankRidge_H20/H40/H60/H120_2026-05-31_seed42_ce62866bb62de38b"]   // 實查 model_registry 4 列
  },
  "baseline_refs": {                           // 比較基線之凍結參照(值不複製、evaluate 時讀表斷言仍在)
    "revalidation_baseline": "4 列(ridge_H60_LO asof 2026-05-31 / ridge_H120_LO asof 2025-12-31 × asof_incumbent/pit_broad,實查)",
    "calibrators": "platt×4 horizon, Brier 0.2463–0.2477 vs 基線 0.2500, ECE 0.0082–0.0157, purge_verified=true",
    "econ_verdict_rule": {"20": "dead", "40": "thin_unestablished", "60": "thin_unestablished",
                           "82": "thin_unestablished", "120": "thin_unestablished"}
  },
  "judgestop_snapshot": {                      // 實查 judgestop_threshold frozen=true 四列(引用不分叉)
    "dsr_annotate": 0.95, "hac_t_floor": 2.0, "net_excess_zero": 0.0, "deflated_floor_zero": 0.0
  },
  "evidence_ledger_gate": "verify_validation_evidence.py --strict 全綠(已知債列須人裁除名或修復留痕)",  // §1.2
  "g1_data":        { /* §4.3 */ },
  "g2_repro":       { },
  "g3_calibration": { },
  "g4_econ_upgrade":{ },
  "g5_rollback":    { }
}
```

### 4.3 五 gate 建議判準值+論證(**判準值本身=拍板點 U1–U6,人凍結才生效;下列為 AI 建議+論證,非裁決**)

| # | gate | 建議判準 | 論證(溯源) | 替代選項 |
|---|---|---|---|---|
| **G1 資料供應鏈** | 新 as-of' 資料完整 | (a) in-scope 表 byte-level 對帳全綠至 as-of'(PHASE 5 既有工具);(b) as-of' 更新已入憲(憲章/原則精華 commit 存在且 commit 時間 > approved_at) | 對帳=敵①防線既有機制,引用不重造;(b) 確保「解凍是人決策在先」 | 無(既有紀律引用) |
| **G2 舊區段復現(anti-leakage 迴歸)** | (a) panel_date ≤ 2026-05-31 之 feature_values 逐 panel 值 hash 不變;(b) registry 4 模型於舊 panel 分數復現至 **5 位小數** | 5 位小數有真兆依據:2026-07-11 乾淨重訓同值到 5 位(管線決定性實證);舊區段變動=新資料洩入舊時點之訊號(#8 迴歸測試) | **U5**:源 restatement(FinMind 歷史修正非我方可控)→出 diff 報告**人裁**(review),非自動 fail 亦非自動 pass |
| **G3 校準存活(live 視窗)** | (a) 視窗 ≥ **6 個非重疊 rebalance 期**/horizon 才可下「確立」級結論(4–5 期只出 review 級中期讀數);(b) live Brier−0.2500:≤0=pass、(0,+0.005]=review、>+0.005=fail;(c) ECE ≤ 0.05 | (a) HAC-t/DSR 在 n<6 幾無檢定力(`src/augur/evaluation/metrics.py:89 effective_t_hac`);單點不判精神同 judgestop consecutive_k。**誠實換算:H60 6 期≈1.4 年、H120 6 期≈2.9 年——不因等不及降門檻**。(b) FREEZE 內勝幅僅 0.0023–0.0037(實查),+0.005=完全失守再反向一個勝幅級。(c) FREEZE 內 ECE 0.0082–0.0157,0.05≈最差值 3× 餘裕 | **U1** 視窗 4/6/8 期;**U2** Brier 容忍分級制 vs 單一硬線;**U3** ECE 0.03/0.05 |
| **G4 econ_verdict 升級** | thin_unestablished→established 需 live 視窗**同時**:net_excess>0 **且** HAC-t≥2.0 **且** DSR≥0.95,**連續 2 輪**評估成立。**H20(dead)不在升級軌**——復活須重走 B 提拔三審,GATE 不提供捷徑 | 三閾值=judgestop_threshold frozen 列現值(0.0/2.0/0.95,實查),快照+evaluate 等值斷言,零分叉常數(#12);連續 2 輪=與判停 consecutive_k 對稱——**升級與判停同紀律,防單點運氣升級**(#15) | **U4**:連續輪數 2/3;是否加 deflated_ann>0 第四條件(建議加,同為 frozen 列 deflated_floor_zero) |
| **G5 回退條款** | (a) 單一 gate_id **原子裁決**:任一 gate fail→status=evaluated_fail,econ_verdict **不升級**、系統維持 deploying_unestablished 標註,不得部分通過部分採納;(b) judgestop 軌B 監看照常運作,不受 GATE 結果影響;(c) fail 後再試=**另立新 gate_id**(舊列 superseded、不刪留痕),新 gate 若判準較舊 gate 放鬆,**須於 note 記人簽核理由**(留痕防「換個門柱再跑」) | 原子性防 cherry-pick;superseded 鏈=完整審計軌;放鬆留痕承 judgestop「調整須人留痕、不調鬆」精神 | **U6**:放鬆一律禁止(更嚴)vs 留痕即可(建議,保留正當修正空間) |

### 4.4 CLI 程式規畫(新檔 `scripts/preregister_unfreeze_gate.py`;#29a/c/d)

| 函式 | 簽名 | 讀 | 寫 | 職責 |
|---|---|---|---|---|
| `_criteria_draft` | `(cur) -> dict` | judgestop_threshold / revalidation_baseline / probability_calibrator / econ_verdict_rule / model_registry | — | 組草案:DB 現值快照(零 hardcode 已在 DB 之值)+U 系列建議值(標 `"proposal": true`) |
| `_criteria_sha` | `(criteria) -> str` | — | — | `sha256(json.dumps(sort_keys=True))[:16]` |
| `preregister` | `(note) -> int` | 上列 | prediction_unfreeze_gate(draft 列) | INSERT+印 30 行摘要+U 系列拍板點清單 |
| `freeze` | `(gate_id, approved_by) -> int` | gate 列+judgestop_threshold | status→frozen, approved_by/at | 斷言 status=draft、judgestop 快照與現值等值,才凍結 |
| `check` | `(gate_id) -> int` | 唯讀 | — | 印快照;覆算 criteria_sha;斷言 trigger 存在 |
| `evaluate` | `(gate_id, new_asof) -> int` | gate+全判準源表 | result_snapshot/status/evaluated_at | 守門斷言鏈(下)→G1–G5 逐項機械 pass/fail;唯記錄面 |
| `selftest` | `() -> int` | — | —(合成 dict/adhoc 假列) | **F7 緩解**:G2–G4 判定純函式以合成 fixture 單測;trigger 白名單以 `purpose='adhoc'` draft 假列實測非法轉移必 RAISE(draft 列可刪、FREEZE 內可跑) |
| `main` | argv | — | — | 指令矩陣;無參數 graceful 印矩陣(#29a) |

**evaluate 守門斷言鏈(依序,任一敗=exit 1=挪門柱/越權)**:
1. `status='frozen'`(draft/superseded 不得評);
2. criteria_sha 覆算=存列(挪門柱,鏡射 B2 rules_sha 拒跑 L313-315);
3. judgestop_threshold frozen 列現值=快照(判準分叉拒跑);
4. `new_asof > '2026-05-31'` **且** feature_values 實有 panel_date>FREEZE——否則印「FREEZE 生效中,evaluate 不可跑」exit 1(**本計畫內唯一可實測之 evaluate 主路徑,#7 實測不違 FREEZE**);
5. `approved_at <` 解凍後評估工件最早 `created_at`(model_registry / probability_oos_sample / probability_calibrator 之 as-of' 列;三表皆有 created_at,實查)——先凍結後開跑,鏡射 B2 `preregistered_at < min(run_at)`(L393)。

指令矩陣:`--preregister [--note ...]` / `--freeze <gate_id> --approved-by <name>` / `--check <gate_id>` / `--evaluate <gate_id> --asof <date>`(FREEZE 內必拒)/ `--selftest` / 無參數=印矩陣。

---

## §5 分階段(V0→V1→V2)

**順序論證**:V0 先立證據帳本=V1/V2 的證據錨(穩健性結果與 GATE 前置都掛回帳本);V1 子期間 Brier/ECE 分佈給 U2/U3 容忍值做 sanity(凍 GATE 前用 FREEZE 內分佈檢查建議值不離譜——用歷史分佈校 sanity 不算偷看未來,live 資料尚不存在);V2 收官凍結。

| 階段 | 內容(缺口) | 產出(落點) | GATE(過關條件) | 回退 | 成本(誠實:撰寫≠執行) |
|---|---|---|---|---|---|
| **V0 證據地圖** | 缺口①:migrate DDL+§3.2 擴充+種子 ~20 列+verify 首跑 | `validation_evidence`;本文件 §1.1 即敘事層總綱 | §1.4 (1)–(3) 過;已知債紅列如實在帳(不許全綠假象) | `DROP TABLE validation_evidence`(唯記錄面、零下游);§3.2 CHECK 縮回=反向 ALTER | 本地零 API 零 usage;小時級 |
| **V1 穩健性** | 缺口②:R 軌閾值人拍板→INSERT(frozen)→五軸跑→gm 斷點調查 | `revalidation_ledger` stage='R';`reports/augur_model_robustness_20260711.md`;gm 契約列入帳 | §2.5 (1)–(3) 過;判準先凍後跑機械可證;觸紅→人裁留痕 | `DELETE FROM revalidation_ledger WHERE stage='R'`(annotate 性質、不動生產);R 閾值列留(凍結紀錄不刪) | 本地重訓 ~2,688 次 Ridge 閉式解=小時級;零 API 零 usage(#28) |
| **V2 GATE 預註冊** | 缺口③:migrate gate DDL→preregister→人拍板 U1–U6→freeze;selftest+trigger 實測+evaluate FREEZE 拒跑實測 | `prediction_unfreeze_gate`(frozen 列);預註冊紀要入本報告附錄或獨立 report | gate 列 status='frozen'+approved_by 留痕;`check` 綠;`selftest` 綠;`evaluate --asof 2026-06-30` 於 FREEZE 內**必拒 exit 1**(實測);非法轉移實測必 RAISE | draft 列可刪;frozen 列 superseded(trigger 白名單容許) | 本地零 API 零 usage;小時級 |

各階段完成即呈用戶過目再進下一(#19 逐段檢視);V1 選項 (a)/(b)/(c) 與 V2 U1–U6 為**明確拍板點**,AI 不代裁。

---

## §6 總驗收

**機械項(SQL/shell,全部本地)**:
1. §1.4 (1)–(3):種子齊(10 chain_link 各≥1、≥18 列)、紅列如實、`--strict` 紅列在→exit 1。
2. §2.5 (1)–(3):R 五列 frozen 且先凍後跑時序成立、五軸×4 horizon 落帳、FREEZE 不破(`max(panel_date)<=2026-05-31`)。
3. §3.2:兩 CHECK 含新值(`pg_get_constraintdef` 驗)、住所檔 in-file DDL 同步、`migrate_judgestop_ddl.py --check` 迴歸輸出正常。
4. §4:gate frozen 列 approved_by 非空;`check`/`selftest` exit 0;`evaluate` FREEZE 內 exit 1;`UPDATE ... SET status='draft'`(frozen 列)實測必 RAISE(F10 堵漏驗證);`UPDATE criteria`(frozen 列)必 RAISE。
5. 全程零外部 API 呼叫、零新資料落地(FREEZE 紅線 a)。

**人工項**:穩健性報告 30 分鐘可讀+判讀誠實(F9 語意註記在);gm 選項呈拍板;U1–U6 拍板紀錄留痕;三份新 script 標頭合 #18/#29d(指令矩陣+實測聲明)。

---

## §7 誠實邊界與已知債(不粉飾,逐條列管)

1. **survivorship 債 b(E5)**:as-of IC 帶樂觀偏誤,pit_broad 誠實錨已量化(−16.5%);帳本紅/amber 列列管,修復屬另案。
2. **E2 macro 兩潛伏債+release_lag 金融業 60/45 日休眠債**:零現行消費者、觸發條件已文檔化;amber 列管。
3. **H120 小樣本**:近期非重疊 n≈8;所有 H120 結論帶此 caveat(registry note 已明標)。
4. **gm 斷點**:調查+契約化在本計畫內;是否重訓(選項 a)=人拍板,紅列直到裁決。
5. **G1–G5 pass/fail 判定碼=FREEZE 內永遠未 live 實測(F7)**:FREEZE 內只能實測 evaluate 的拒跑分支;緩解=`--selftest` 合成 fixture 單測判定純函式+trigger 白名單 adhoc 假列實測;首次真跑=解凍當天,此為結構性限制、誠實記載而非宣稱已測。
6. **R 軌=annotate/review 非自動判停**:觸紅→人裁;rank_autocorr 低值≠不穩健(F9,換手率語意)。
7. **evidence green ≠ 方法論正確**:帳本只驗「斷言對 DB 為真」;方法論正確性住裁決報告、由人審。
8. **judgestop created_at 回填**:既有 6 列時間戳=遷移時刻非原凍結時刻(note 明記);「先凍後跑」時序證明對**新增之 R 列與其後**才有完整機械力,既有列時序繫於 git 歷史。
9. **本計畫產出全部=建議**:R 閾值五列、U1–U6、gm 選項、GATE 判準值——人凍結才生效;AI 不代拍(靈魂:系統建議、人決策)。
10. **live 呈現/軌B 衰減偵測**:解凍後才有牙;本計畫只預凍判準,不真跑 live(FREEZE 紅線)。

---

## §8 批判修訂對照(F1–F10)

| # | 批判要旨 | 處置 | 落點 |
|---|---|---|---|
| F1 | E1「reconcile 帳本」是幻像(無表、script 零 INSERT),且 SELECT-only check 無法承載 exit-code 型證據 | **採納**:E1 落帳欄改「無落帳表(stdout+exit-code),誠實標示」;`validation_evidence` 增 `check_type('sql','script_exit','manual')`+`check_cmd`(白名單、`--with-scripts` 才執行);驗收 (1) 之 raw 環節由 script_exit 列承載,矛盾解除 | §1.1 E1、§1.2、§1.3、§3.1 |
| F2 | CHECK 擴充未落實為程式規畫;constraint 實名;住所檔 verify 同步 | **採納+誠實校正**:兩條冪等 ALTER 以實名(`revalidation_stage_chk`/`chk_js_track`)寫明、住各自 DDL 住所檔(`migrate_revalidation_ledger_ddl.py`/`migrate_judgestop_ddl.py`,後者實查為 in-file CHECK 須同步);校正:該檔為 `--check` 且 `_verify` print-only 不 assert(實查 L92-100),故「自己翻紅」不成立,但 fresh-DB 重跑會建回舊 CHECK=跨檔不一致,同步義務仍成立 | §3.2 |
| F3 | R 軌閾值列缺 horizon 口徑,卡 PK | **採納**:定案五列全 `horizon=0` 哨兵(與既有 6 列一致)、評估逐 horizon、語意入 note;未來 per-horizon 差異值由 PK 天然容納另立列 | §2.0 |
| F4 | §2 程式規畫缺席 | **採納**:補 §2.4——`run_model_robustness.py` 檔/函式簽名/輸入輸出表/CLI 矩陣/實測分級;斷點調查明文不另立 script(#29c) | §2.4 |
| F5 | (a) 後半節號對映錯 (b) 驗收「七環節」枚舉 9 個 (c) metrics.py 路徑不全 | **採納**:(a) 定稿統一節號(§1 地圖/§2 穩健/§3 schema/§4 GATE);(b) 枚舉定為 10 chain_link、與 DDL CHECK 一字不差;(c) 全路徑 `src/augur/evaluation/metrics.py:89` | 全文、§1.4、§3.1 |
| F6 | 計數型 check_sql 脆弱(合法重跑翻紅=假警報) | **採納**:設計原則入文——可增長表用語意型斷言、凍結快照才精確計數;附兩型範例 | §1.2、§1.3 |
| F7 | G1–G5 評估碼=FREEZE 內永遠未實測 | **採納**:`--selftest`(合成 fixture 單測 G2–G4 判定純函式+adhoc 假列實測 trigger);結構性限制誠實入 §7 債 5、不宣稱已測 | §4.4、§5 V2、§7 |
| F8 | 「重切既有 OOS」掩蓋 LOFO/擾動須重訓之口徑,未凍 (i)/(ii) | **採納**:口徑凍結=選 (i) 真 LOFO 全 walk-forward 重訓(Ridge 閉式解本地可行,~2,688 次),明文棄用 (ii) 並記其語意偏差(高估單點依賴);口徑寫入 R 列 note 一併凍結 | §2.0、§2.2(b2) |
| F9 | rank_autocorr 低值可能是季頻訊號本性,防解凍後誤當紅旗 | **採納**:語意註記(換手率、annotate-only、觸發之正確動作=換手成本一致性複核)寫入 ledger note 與報告;年頻對/跨節奏邊界對另列描述性不混評 | §2.2(b1)、§7 債 6 |
| F10 | trigger 不擋 frozen→draft 回退=兩步降級挪門柱真漏洞 | **採納**:trigger 改狀態轉移白名單(draft→frozen\|superseded;frozen→evaluated_*\|superseded;終態不可回改)+凍後簽核欄鎖定;§6 機械驗收含 frozen→draft 實測必 RAISE | §4.1、§6 項 4 |

---

*本計畫全程 FREEZE 內、本地零 API、零新資料;所有判準值與選項為建議,人拍板凍結才生效。*
