# [DRAFT 呈案] D2S｜sim 軸合法評估之 prereg gate——SIM-CAL-R1 預註冊門呈案（未經拍板不得施作）

> **[DRAFT 呈案] 未經拍板不得施作。**
> **日期**：2026-08-01（六）深夜｜**呈案人**：AI（W2 呈案批 D2S）｜**裁決**：專屬 Constitution Steward（`AUGUR-MC v1.6 §8.1`／L6.18(a)）
> **自我利益揭露（L6.18(c)）**：本呈案由 AI 起草，所擬之門直接界定「AI 產出之模擬候選（`origin='llm_local'`）何時得被評為有能力」——即 AI 為自身能力宣稱之量尺提案。方向為**建門收緊**（現況＝無門＝評了也非法且寫不進；本案不放寬任何既有判準），且門檻數字、臂定義、簽核全數保留 Steward 圈選、hugo TTY／psql 親簽；AI 機械上不可代填任何人簽欄。
> **設計 SSOT**：`docs/模擬方法自進化專章_v1.0.md` §3.1-3.7／§5.3（gp_86c8063fc688 enacted 07-31）＋`reports/augur_local_ai_sim_evolution_impl_plan_20260731.md` §9 D-2・§10 U-1＋`reports/w2_20260801/H2_sim_first_method.md`（x-scope-warning：入冊僅解 B-1，合法評估待 D-2＝本案）。
> **親驗基準**：git HEAD `b98bc04`；DB 現查時刻 2026-08-01 深夜（iid_bootstrap 入冊親簽 21:53 之後）；所有數字出自 §2 之 SQL（#9/#10）。**本呈案全程唯讀（零 DDL、零 DB 寫入、零 commit）；不開跑 sim、不代簽。**

---

## §0 摘要（30 秒版）

專章 §3.1 明文：sim 軸**每一輪評估前**須於 `evolution_prereg_gate` 建一列（`axis='sim'`，內含可證偽條件、樣本外窗、臂組成、判準門檻、criteria_sha）。現況親驗：該表 `axis='sim'`＝**0 列**；且 `sim_calibration_eval.gate_id` 為 NOT NULL FK→本表 ⇒ 無門不只「評了非法」，是**任何校準評測列在 DB 層寫不進去**。iid_bootstrap 今晚已入冊（B-1 解），下一個斷點就是本門。本呈案給出 **SIM-CAL-R1** 之判準全文草案（criteria_text 為唯一 binding、sha 錨定依本表既有 64-hex 口徑親驗）、五臂定義凍結、兩組門檻（T-A 嚴／T-B 寬-只判死）、hugo psql/TTY 親簽流程與機械驗收。建議案＝**形制甲＋門檻 T-A＋首輪單列＋零新碼親簽路徑**。

---

## §1 問題與授權鏈

### 1.1 問題

1. **程序缺門**：`evolution_prereg_gate` 無 `axis='sim'` 列（§2.1）。專章 §3.1「判準先於資料」：先跑後補門＝非法評估，分數不得作能力宣稱。
2. **物理缺門**：`sim_calibration_eval.gate_id NOT NULL` FK→`evolution_prereg_gate` ⇒ 評測列一筆都落不了地（§2.2）。W3（evaluate）以後全部卡在本門之後。
3. **判準數字空懸（U-1）**：impl plan 明文「校準門檻之合理值無先例，須 D-2 定；本計畫不代擬數字」——本呈案即 D-2 之呈案：**代擬選項、不代裁**。
4. **覆算機制缺位**：goalpost trigger 護的是 `criteria_sha` **欄**，不護 criteria payload（§2.3）；評估側覆算在本表先例（settle_sunset）中**不存在**——sim 評估器須內建，本案將其寫進判準本文。

### 1.2 授權鏈（P5.W2／L6.5-L6.8 四要件留痕）

| 要件 | 內容 |
|---|---|
| (a) 範圍 | 呈案草擬：唯讀查證（repo＋DB 唯讀探測）；唯一寫入＝本檔；不施作、不 commit、不 DDL、不碰演化引擎四檔 |
| (b) 結束條件 | 本呈案完稿交回 orchestrator 即結；施作須另經 Steward 圈選 §7 |
| (c) 可撤銷 | 隨時 |
| (d) 任務參照 | W2 呈案批 D2S 項；上游＝impl plan §9 D-2＋H2 x-scope-warning（「sim 合法評估仍待 D-2」）＋專章 §3.1 |

**裁決分工**：形制、門檻組、輪次、簽核路徑、親簽時點＝Steward 圈選；圈選後之 criteria_text 定稿與覆算＝AI 呈最終文；**INSERT 與簽名＝hugo 親跑**（gate 預註冊＝人簽）。

---

## §2 現況親驗（2026-08-01 深夜現查；勿沿用舊數）

### 2.1 門與軸

```sql
SELECT axis, count(*) FROM evolution_prereg_gate GROUP BY axis;
--  program | 2        （V2-SUNSET superseded／V2-SUNSET-r2 evaluated_pass，皆 hugo 簽）
--  axis='sim' ⇒ 0 列   （tw/lai/raw 亦皆 0——全表僅 program 軸曾用過此門）
```

- `axis` 已改 FK→`evolution_axis`（5 軸含 sim，gp_86c8063fc688 註記在列）⇒ sim 列**物理可寫**、純程序缺門。
- 附帶親驗：tw 軸之 `V2-AUTOADVANCE` **不是本表列**——它只是 `run_evolution_iteration.py:46` 的常數字串＋`audits/V2-AUTOADVANCE-PROPOSAL-20260727.md`，`promotion_queue.gate_ref` 留痕用。即：**sim 若照專章走，將是第一個「軸級評估門真正入表」的軸**；tw 之先例只提供 criteria 形制與 trigger 行為，不提供「入表」先例（入表先例唯 program 軸 SUNSET 兩列）。

### 2.2 物理鎖鏈（誰擋住誰）

| 環節 | 親驗事實 | 效果 |
|---|---|---|
| `sim_calibration_eval.gate_id` | **NOT NULL**＋FK→`evolution_prereg_gate` | 無門 ⇒ 評測列寫不進（連煙測都不行） |
| `sim_evolution_verdict.gate_id` | NOT NULL＋FK 同上；`chk_sev_five_arm_floor`（promoted ⇒ arms_covered ⊇ 五臂）、`chk_sev_promote_signed`（promoted ⇒ decided_by/decided_at/gate_proposal_ref 非空，後者 FK→governance_proposal） | 判決亦繫門；晉升＝門＋人簽＋enacted 提案**三鎖** |
| `sim_evolution_candidate.gate_ref` | nullable FK | 候選可先入冊、評估時補繫門（H2 已明辨 procedural 非 physical） |
| `simulation_method_registry` | **1 列**：iid_bootstrap registered（approved_by=hugo 2026-08-01 21:53、gate_ref=gp_df544cbb1b94 **enacted**）；param_schema 內建 x-scope-warning「不得據此宣稱 sim 可開跑」 | B-1 已解；本案是下一斷點 |
| sim 八表 | candidate/eval/verdict/ledger/llm_proposal/realized/run_link 全 **0 列**；registry 1 | 軸仍空轉 |
| kill switch | `scope='sim'` 已在（state=clear、set_by=migrate_sim_constraints_ddl；CHECK 五值含 sim） | 煞車作用點已預置（消費者仍缺＝已知，W5） |

### 2.3 criteria_sha 口徑與 trigger 射程（本案形制之依據）

```sql
SELECT gate_id, criteria_sha = encode(sha256(convert_to(criteria->>'criteria_text','UTF8')),'hex')
FROM evolution_prereg_gate;   -- V2-SUNSET t／V2-SUNSET-r2 t
```

- **本表 house 口徑（親驗成立）**：`criteria_sha = sha256(criteria->>'criteria_text')`，64-hex，**sha 對象＝criteria_text 字串本身**（`gate_raise_sunset_deadline.py:90` 同式）。另一族 gate（arena/unfreeze）用 sort_keys-JSON 16-hex（`preregister_unfreeze_gate._criteria_sha`）——**兩口徑並存，新列必須明選**（§4 形制案）。
- **goalpost trigger（`prereg_gate_no_goalpost`，prosrc 親讀）**：DELETE 一律拒；終態列（evaluated_pass/fail/superseded）不可改；`criteria_sha` 欄不可改。**射程誠實**：它不驗「criteria payload 仍與 sha 相符」——UPDATE criteria 而不動 sha 欄可過 trigger。真鎖＝**評估時覆算**。
- **評估側覆算現況**：具覆算者僅 `evaluate_arena_admission.py`／`preregister_unfreeze_gate.py`（16-hex 族）；本表唯一結算先例 `settle_sunset_gate.py` **不覆算**（grep 0 hit）。⇒ sim 評估器（W3/W4）之覆算義務必須寫進判準本文（§3.2 草案已寫入）。

### 2.4 樣本外素材之時鐘（§3.3 之硬約束）

```sql
SELECT count(*), count(DISTINCT method), min(asof_date), max(asof_date) FROM mc_simulation_run;
--  540 | 20 | 2026-05-31 | 2026-05-31      （iid_bootstrap 261 列；52 個股 target＋1 PORT_*；19 horizon 全法/6 horizon iid）
SELECT count(*) FROM sim_realized_outcome;   -- 0（結算管線 W5 未建）
```

- **540 列史料全部 asof=2026-05-31＝判準凍結時點之前** ⇒ 依專章 §3.3（評估窗須完全落在判準凍結時點之後），**不得作本門之樣本外證據**；D-5 之「史料回填」只能當管線煙測／診斷（且因 §2.2 物理鎖，煙測結果**只能落 stdout、不得落 `sim_calibration_eval`**——該表無門不收、有門也不得混入證據列）。
- live 臂之新 run 由 `simulate_mc_paths.py` 產（既有 writer、mc 四鎖在位：`is_simulation` CHECK 親驗存在）；實現值結算腳本（→`sim_realized_outcome`）尚未存在——**本門可先立，證據收集繫 W3/W5 工具**，時鐘見 §4 門檻案。

### 2.5 與登錄冊／計畫不符處或新事實（明標）

1. 任務語「tw 軸之 V2-AUTOADVANCE 等列」——**非本表列**（§2.1 親驗）；criteria 形制之入表先例唯 program 軸兩列。
2. 任務語「mc_baseline/derive schema」——`mc_baseline`／`mc_derive` 二表**不存在**；正名＝`simulation_method_registry.param_schema`（derive 草案已隨 iid_bootstrap 入冊）＋素材表 `mc_simulation_run`（H2 §2.3-1 之正名裁定已執行落地）。
3. impl plan §5.2 之三 CHECK＋`arms_covered`＋kill_switch sim scope——**已全部落地**（live `\d` 親驗；H2 統一窗已執行）。本呈案不重提 DDL；**本案零 DDL**。
4. trigger 護 sha 欄非護 payload（§2.3）——七型「防呆機制自己靜默失效」之潛在第八型，本案以「覆算寫進判準本文」封口。

### 2.6 本呈案所讀之既有表 schema（#20 v1.39.0 (a)；**不新建任何表**）

- `evolution_prereg_gate`（**結果唯一落點：新 1 列**）：gate_id PK·axis FK·purpose·criteria JSONB·criteria_sha·status CHECK{preregistered,approved,evaluated_pass,evaluated_fail,superseded}·approved_by/at·git_sha·evaluated_at·result_snapshot·evaluation_ref·note；goalpost trigger。
- `sim_calibration_eval`（消費端；本案不寫）：eval_id·gate_id FK·candidate_id FK·arm CHECK{live,ceiling,floor,shuffled,mismatched,robot}·eval_set_id·eval_code_hash·n_runs/n_valid/n_excluded·is_invalid·cov_p50/p80/p90·pinball_mean·crps_mean·pit_ks_stat/p·detail·git_sha；`uq_sce_cell` UNIQUE(gate_id,candidate,arm,eval_set,code_hash)。
- `sim_evolution_verdict`／`sim_evolution_iteration_ledger`（gain_basis CHECK 含 calibration_delta）／`mc_simulation_run`／`sim_realized_outcome`（settle_mode CHECK{normal,last_trade,unsettleable}、`chk_sro_forward`）／`simulation_method_registry`——皆唯讀引用，欄位如 live `\d`。

---

## §3 方案：SIM-CAL-R1 判準草案

### 3.1 設計原則（自專章逐條對映）

| 專章條 | 落點 |
|---|---|
| §3.1 判準先於資料＋指紋 | 本門先立；criteria_sha 依 house 口徑；覆算義務入本文 |
| §3.2 可證偽須具體 | k1-k3 判死條件逐條寫死（§3.2 草案） |
| §3.3 樣本外＋去相關 | live 臂唯計 approved 後新 run；**非重疊窗設計**（每 21 交易日一格）使窗間 iid 合法化；跨 target 同日相關以**日期簇 bootstrap** 處理（不裸用 iid 統計） |
| §3.4 五臂地板 | 五臂定義凍結入本文；floor＝樣板常數錐（07-26 常數字串 0.654 教訓：**無條件覆蓋率好看≠有條件能力**，故判別主尺＝proper scoring rule 對三臂之勝出，非覆蓋率單尺） |
| §3.5 終審統計級 | 判準全部是覆蓋率／PIT／CRPS——零經濟量、零方向量 |
| §3.6/§3.7 | gain_basis 唯 calibration_delta；tilt_free 已由 registry CHECK 鎖 |
| §5.3 換尺＝換身分 | 判準/臂/評估碼變更 ⇒ 新 gate_id＋本列 superseded，寫入本文 |
| §5.4 誠實無能 | n 不足 ⇒ undecidable 非 pass；「全滅」為合法產出 |

### 3.2 criteria_text 草案全文（binding 本體；⟨⟩＝Steward 圈選後定稿處，定稿後零佔位才可簽）

```text
門：SIM-CAL-R1（sim 軸首輪校準評估之預註冊門；專章 §3.1；D-2）
評估對象：sim_evolution_candidate 之 method 於 simulation_method_registry status='registered'、
  且本輪繫 gate_ref='SIM-CAL-R1' 之候選（首輪即 iid_bootstrap 之 spec 變體；origin 依專章 §2.2-2.3）。
樣本外窗（§3.3）：live 臂唯計 mc_simulation_run.asof_date ≥ 本門 approved_at 次一交易日之新 run；
  首輪 horizon 唯 h=21（交易日）；asof 取樣＝每 21 個交易日一格（窗不重疊）、至少 K=⟨3|2⟩ 格；
  target 集＝史料 52 檔個股（凍結清單 SQL：SELECT DISTINCT target_id FROM mc_simulation_run
  WHERE target_id ~ '^[0-9]+$'；其排序串接 sha256=649221f491e67048b23ee19f36b85274b588d0896e86447a42203b4125982ce4）；
  PORT_* 不入首輪（結算口徑未定＝impl plan U-3）。
結算：sim_realized_outcome settle_mode∈{normal,last_trade}；unsettleable 除外並計入 n_excluded。
臂組成（§3.4 五臂地板；定義凍結）：
  live＝候選 spec 於真實資料之分位錐；
  ceiling＝同窗實現值之事後經驗分位錐（oracle 參照；僅作上界、不參賽）；
  floor＝無條件常數錐：全史 pooled 日報酬 σ 之常態錐、全 target 全 asof 同一 σ（樣板地板）；
  shuffled＝同 asof×h 內 target 間實現值重排（seed=42）；
  mismatched＝target i 之錐配 target j≠i 之實現值（固定 derangement；seed=42）；
  robot＝選配第六臂（加嚴參照、非地板要件）。
判準門檻（T-⟨A|B⟩；數值見 thresholds 鏡射，thresholds_sha 錨定於本文末行）。
判死（§3.2 可證偽；任一成立即 killed）：
  k1 |cov_p80−0.80|＞tol 或 |cov_p90−0.90|＞tol（tol 依 T-案）；
  k2 live 之 crps_mean 未依 T-案判法勝過 floor、shuffled、mismatched 三臂之每一臂；
  k3（唯 T-A）PIT KS 依日期簇 bootstrap 臨界值 p＜0.05。
undecidable（§5.4）：n_valid＜下限、或日期簇＜K、或任一臂缺 ⇒ undecidable（不得作 pass 用；誠實無能為合法產出）。
promoted 前提：k1-k3 全數反向成立＋arms_covered ⊇ 五臂（chk_sev_five_arm_floor）＋人簽三欄
  （chk_sev_promote_signed；gate_proposal_ref 指向 enacted governance_proposal）。本門非晉升唯一鎖。
  ⟨T-B 圈選時加：本輪 promoted 不可用——verdict 唯 killed/undecidable，晉升須另開 T-A 級新門。⟩
評估紀律：評估前覆算 sha256(criteria->>'criteria_text')＝criteria_sha、
  且覆算 sha256((criteria->'thresholds')::text)＝本文末行 thresholds_sha，任一不符即拒評（§3.1）；
  eval_code_hash 落 sim_calibration_eval；同 (gate,candidate,arm,eval_set,code_hash) 唯一（uq_sce_cell）；
  史料（asof≤2026-05-31）之任何數字不得入本門證據列。
換尺＝換身分（§5.3）：判準、臂定義、評估碼實質變更 ⇒ 開新 gate_id、本列轉 superseded；分數不跨尺比較。
thresholds_sha=⟨定稿時由 SQL 覆算填入⟩
```

### 3.3 thresholds 鏡射草案（non-normative 鏡射；由本文末行 thresholds_sha 錨定；鏡射與本文不符以本文為準）

**T-A（嚴案；可晉升）**：
```json
{"horizon_td": [21], "n_windows_min": 3, "n_valid_min": 100, "date_clusters_min": 3,
 "cov_tol": {"p80": 0.05, "p90": 0.05},
 "skill_metric": "crps_mean", "skill_arms": ["floor", "shuffled", "mismatched"],
 "skill_test": {"kind": "date_cluster_block_bootstrap", "B": 1000, "seed": 42, "one_sided_lcb": 0.95},
 "pit": {"test": "ks", "p_min": 0.05, "critical_values": "date_cluster_bootstrap"},
 "settle_modes": ["normal", "last_trade"],
 "targets_sha": "649221f491e67048b23ee19f36b85274b588d0896e86447a42203b4125982ce4",
 "promoted_allowed": true}
```
**T-B（寬案；只判死不晉升）**：同上惟 `n_windows_min:2, n_valid_min:50, date_clusters_min:2, cov_tol 0.10/0.10, skill_test:{"kind":"point_estimate_only"}, pit:{"advisory":true}, promoted_allowed:false`。

**數字之誠實標注**：以上皆**提案值非實測值**（U-1 明文無先例、impl plan 不代擬故由本案擬供圈選）。量級依據：52 target×3 窗＝156 名目對、日期簇僅 3——**iid 顯著性在此不合法**（§3.3），故 T-A 之 skill 檢定與 PIT 臨界值一律走日期簇 bootstrap；tol=0.05 約當 156 名目對之 2×binomial SE（p80）再放寬計簇縮水，屬工程保守值、非最優值——**首輪跑完之實測分佈即為 R2 校正門檻之素材**（試錯即進步 #27，但升嚴唯走新列）。

### 3.4 程式規畫（#20 v1.39.0 (b)）

| 檔 | 職責 | 本案動作 |
|---|---|---|
| （無新檔） | R1 之 INSERT＝hugo psql 親跑（§7 步 3 全文） | **零新碼**（建議案；H2 步 6 先例） |
| `scripts/evaluate_sim_calibration.py`（W3 既定規畫） | 覆算兩 sha（§3.2 評估紀律行）→ 五＋一臂計算 → 落 `sim_calibration_eval` | 本案僅**釘其覆算義務入判準本文**，不在本案實作 |
| `scripts/decide_sim_verdict.py`（W4 既定規畫） | 讀 eval 列依 thresholds 判 k1-k3 → 落 `sim_evolution_verdict`（promoted 走人簽三欄） | 同上 |
| `scripts/preregister_sim_gate.py`（選配，§4 路徑乙） | --draft/--register/--approve(TTY isatty＋親打簽名、比照 gate_raise `_sign`；**不設人名旗標、selftest 不寫人簽欄**＝專章 §4.4 補強 2） | R2 起若輪次頻繁再立案；R1 不建 |

---

## §4 選項與建議案

**①形制｜criteria_sha 錨定方式**
| 案 | 內容 | 評註 |
|---|---|---|
| **甲（建議）** | house 口徑：sha 對象＝criteria_text 全文（64-hex）；thresholds 結構鏡射以「本文末行 thresholds_sha（SQL：`sha256((criteria->'thresholds')::text)`，jsonb 正規化文本、DB 側覆算）」二級錨定 | 與本表既有兩列**同口徑**（§2.3 親驗 t/t）——表級覆算工具未來可用同一式掃全表；binding 全在文、機讀走鏡射、鏡射被文鎖住 |
| 乙 | arena/unfreeze 口徑：sort_keys-JSON 16-hex 對整包 criteria | 單層乾淨；但同表兩口徑並存 ⇒ 覆算工具須逐列判口徑＝新的漂移面 |

**②門檻組（U-1 之 D-2 裁點）**
| 案 | 內容 | 時鐘（approved≈08 月初起算） | 評註 |
|---|---|---|---|
| **T-A（建議）** | K=3 窗·n≥100·簇≥3·tol 0.05·簇 bootstrap 顯著·PIT 判 | 第 3 窗 label 結清≈**2026-11 上旬**才可有 verdict | 推論站得住；promoted 可用；慢（「慢可以、提升要精準」） |
| T-B | K=2·n≥50·簇≥2·tol 0.10·點估勝·PIT advisory·**promoted 禁用** | 最早≈**2026-10 上旬**可判死 | 快篩用：只允許 killed/undecidable，把「弱推論卻晉升」的路事先焊死；倖存者仍須 T-A 級新門才可晉升 |

**③輪次形制**
| 案 | 內容 | 評註 |
|---|---|---|
| **甲（建議）** | 首輪單列 SIM-CAL-R1；後輪**逐輪開新列**（§3.1 字面「每一輪…建立一列」；criteria 沿用者僅改輪次與窗、重簽） | 合字面；每輪簽核成本小（diff 極小）；§5.3 換尺開新列與此同機制 |
| 乙 | 常設門一列、輪次由 eval_set_id 承載 | 省簽核；但「每一輪建立一列」須作擴張解釋＝治權解釋落 Steward，AI 不代解——列出不建議 |

**④註冊/簽核路徑**
| 案 | 內容 | 評註 |
|---|---|---|
| **甲（建議）** | **零新碼**：AI 呈定稿 criteria_text＋thresholds → hugo psql 親跑 §7 步 3 之 CTE INSERT（sha 由 SQL 就地覆算＝**sha 與文同源、不可能錯位**）、status 直入 'approved'、approved_by 由 hugo 親打 | H2 步 6 先例；V2-SUNSET-r2 亦直入 approved；「不代打人簽」全守 |
| 乙 | 新腳本 preregister_sim_gate.py（TTY 閘） | R2 起輪次頻繁才值得；R1 為它寫碼＝為一次 INSERT 造 CLI |

**建議案總成**：**①甲＋②T-A＋③甲＋④甲**。若 Steward 欲先快篩 iid_bootstrap 之變體再談晉升，②改 T-B 亦自洽（門文已含 promoted 禁用句之圈選位）。

---

## §5 風險與回滾

| # | 風險 | 說明與緩解 |
|---|---|---|
| 1 | 門立了、證據管線未建（W3/W5 工具與 `sim_realized_outcome` 結算皆未存在） | 誠實記載：本門**不啟動任何評估**；時鐘自 approved 起算但證據落地繫 W3/W5——若 W3/W5 遲到，唯一後果＝undecidable 變晚，**判準不因遲到放寬** |
| 2 | 錯列不可刪（goalpost trigger DELETE 拒） | 回滾＝開新列＋原列 UPDATE status='superseded'（非終態列可改 status；criteria_sha 不動）——與 V2-SUNSET→r2 同路 |
| 3 | payload 被改而 sha 欄未動（trigger 射程外） | 覆算義務已入判準本文＝評估器不覆算即違門文；驗收含覆算式（§6-2） |
| 4 | floor 無條件覆蓋率亦可能落在 tol 內 | 已預期（樣板地板教訓）：k2 以 CRPS 勝三臂為判別主尺，覆蓋率單獨好看不構成通過 |
| 5 | 52 target 同日截面高相關 ⇒ 名目 n 灌水 | 判準明文簇下限＋簇 bootstrap；n_valid 與 date_clusters 雙門檻 |
| 6 | T-A 時鐘長（~11 月）期間之宣稱壓力 | 專章 §2.4：候選期間數字不得入白名單；本門 undecidable 前一切 sim 數字＝self-reported |
| 7 | 「每 21 交易日一格」之交易日曆口徑 | 依 tw 交易日曆（資料驅動現查）；定稿時於 thresholds 鏡射補 `calendar:"twse"` 鍵 |

---

## §6 驗收判準（機械可判；施作後由 AI 跑、全唯讀）

1. **門成立**：`SELECT gate_id, axis, status, approved_by FROM evolution_prereg_gate WHERE axis='sim'`＝恰 1 列 `SIM-CAL-R1 | sim | approved | hugo`；`approved_at`/`git_sha` 非空。
2. **指紋自洽（兩級覆算）**：`SELECT criteria_sha = encode(sha256(convert_to(criteria->>'criteria_text','UTF8')),'hex') FROM evolution_prereg_gate WHERE gate_id='SIM-CAL-R1'`＝t；且本文末行 thresholds_sha＝`encode(sha256(convert_to((criteria->'thresholds')::text,'UTF8')),'hex')` 覆算值。
3. **零佔位**：`criteria->>'criteria_text'` 不含 '⟨' 字元（圈選已定稿之機械證）。
4. **goalpost 真會咬（negative；交易內、ROLLBACK 收尾）**：`BEGIN; UPDATE evolution_prereg_gate SET criteria_sha='x' WHERE gate_id='SIM-CAL-R1';` 必被 trigger 拒；`DELETE` 同；`ROLLBACK` 後列不變。
5. **物理解鎖證明**：門列存在後，`sim_calibration_eval` 之 FK 前提成立（不實插；以 `SELECT 1 FROM evolution_prereg_gate WHERE gate_id='SIM-CAL-R1'` 為 FK 可指向之證）。
6. **W3 評估器接線時（前瞻驗收，非本案）**：evaluate_sim_calibration 對「sha 不符之門」必須拒評——屆時以壞 sha 假門 fixture 驗紅（回歸鎖先驗紅紀律）。

---

## §7 hugo TTY／psql 親簽流程（★＝hugo 親為、AI 機械上不可代）

| 步 | 執行者 | 動作 |
|---|---|---|
| 0 | **★Steward** | §8 圈選：①形制 ②門檻 ③輪次 ④路徑＋親簽時點 |
| 1 | AI | 依圈選產**定稿** criteria_text（零 ⟨⟩）＋thresholds JSON；印 §7-3 之 INSERT 全文（含 SQL 就地覆算之 sha 式）與預覽 sha 值；全程唯讀 |
| 2 | **★hugo（人審）** | 過目定稿：可證偽條件是否具體（§3.2）、門檻數字、樣本外窗、臂定義——修訂則回步 1 |
| 3 | **★hugo（psql 親跑＋親打 'hugo'）** | 執行下方 CTE INSERT（criteria_text 只出現一次、sha 由同一綁定值覆算＝同源）：|
| 4 | AI | 跑 §6-1～4 驗收（唯讀＋negative-in-txn）；audit 留痕 `audits/`；W2 帳收口 |
| 5 | （日後）AI | W3/W4 實作時把覆算義務做進 evaluate/decide 兩支並先驗紅（§6-6） |

**步 3 之 INSERT 骨架（定稿值由步 1 填入；hugo 親跑）**：
```sql
WITH c(t) AS (VALUES ($CT$<定稿 criteria_text 全文>$CT$))
INSERT INTO evolution_prereg_gate
  (gate_id, axis, purpose, criteria, criteria_sha, status, approved_by, approved_at, git_sha, note)
SELECT 'SIM-CAL-R1', 'sim',
       'sim 軸首輪合法評估之預註冊門（專章 §3.1;判準先於資料;D-2）',
       jsonb_build_object('criteria_text', t, 'thresholds', $TH$<定稿 thresholds JSON>$TH$::jsonb, 'round', 'R1'),
       encode(sha256(convert_to(t, 'UTF8')), 'hex'),
       'approved', 'hugo', now(), '<git rev-parse --short HEAD>',
       'D2S 呈案;T-<A|B> 圈選;criteria_text 唯一 binding、thresholds 鏡射由文末 thresholds_sha 錨定'
FROM c;
```
（governance_proposal 不另立：專章 §3.1 之門以本表 approved_by 親簽為足，program 軸兩列先例同式；**晉升時**之 gate_proposal_ref 才須 enacted 提案＝三鎖之第三鎖，屆時另案。）

---

## §8 證偽條件（本呈案自身）

1. 門立後 W3 評估器落地時發現 `sim_calibration_eval` 欄位承載不了本文判準（如簇統計無處落）⇒ 判準與載體失配，門須 supersede 重開（detail JSONB 可承載為緩衝，屆時親驗）。
2. 非重疊窗設計下首輪 n_valid 實收＜下限（如新 run 產出中斷、unsettleable 超預期）⇒ undecidable——此為**設計內結果**非證偽；但若連續兩輪皆因產出斷供 undecidable ⇒ 時鐘設計錯，K/horizon 選擇須重擬。
3. 若 house sha 口徑之「sha 對象＝criteria_text」被日後表級工具誤當「sha 對象＝整包 JSON」掃描 ⇒ 假紅——§2.3 之口徑親驗（兩列 t/t）為對照證據，工具側修。
4. 若 Steward 裁定 §3.1「每一輪建立一列」應作常設門解釋（③乙）⇒ 本案③甲之輪次成本論證失效，改走乙不影響①②④。

## §9 Steward 決定欄（留白）

- [ ] D2S-同意（建議案總成：①甲 house-sha 二級錨定＋②T-A 嚴案＋③甲 逐輪一列＋④甲 零新碼 psql 親簽）
- [ ] D2S-改採：①＿＿ ②＿＿（T-A／T-B；門檻數字修訂：＿＿） ③＿＿ ④＿＿
- [ ] 親簽時點另約：＿＿＿＿＿＿
- 簽署：＿＿＿＿＿＿　時點：＿＿＿＿＿＿
