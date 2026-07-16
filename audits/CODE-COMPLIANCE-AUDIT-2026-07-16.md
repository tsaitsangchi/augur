# Augur 程式碼庫合憲審計報告（初步）

* **審計日期**：2026-07-16
* **審計對象**：[tsaitsangchi/augur](https://github.com/tsaitsangchi/augur)（台股預測系統，shallow clone @ main，2026-07-15 最後推送）
* **審計基準**：《Augur Meta-Constitution》v1.2（AUGUR-MC v1.2）
* **報告狀態**：✅ **已驗證＋裁決定調（VERIFIED & ADJUDICATED）**——2026-07-16 完成雙重對抗驗證（52 驗證代理＋報告門檢，見第七節）；P4.E3 刪除家族分級判準經 **Steward 解釋裁決第 2026-001 號**定調（採「原始 vs 衍生＋緩解程度」尺度，見 7.5 節與 [../constitution/INTERPRETATION-RULING-2026-001.md](../constitution/INTERPRETATION-RULING-2026-001.md)）。~~⚠️ 初步（PRELIMINARY）— 未完成對抗驗證~~ 個別發現之正式違憲認定仍屬 Steward §8.2 個案裁定權限
* **發現統計**：26 項（初步：critical 3 / major 10 / minor 13 → 驗證後暫計：critical 4 / major 9 / minor 12 ＋ 1 待裁定 → **裁決後定稿：critical 3 / major 11 / minor 12；0 項被推翻**）＋合憲亮點 54 項

---

## 一、Executive Summary

本審計以 6 個偵察代理建立程式碼地圖、6 位審計官分持五大原則與治權整合維度並行審計、整併官跨視角去重並親自重驗每項證據（報告中「親查屬實」標注），產出 26 項差距發現與 54 項合憲亮點。

**總體結論**：這是一個**精神高度合憲、結構顯著缺層**的系統。既有治權體系（三個敵人、二十條原則、as-of 紀律、「系統建議人決策」）與 Meta-Constitution 五原則高度同構 —— P5（人類權威）與 P4 的 valid-time 面向落實程度甚至超出一般業界水準；審議通道（候選斷言 → 機械裁決 → fail-closed）是 P2.W2 的教科書級實作。

但憲章要求的三個**結構層完全缺位**：(1) 無 World Model／Ontology 層 —— 「API 即權威」被治權條文立為法律，資料來源 schema 即系統最高抽象（F1 教科書式命中）；(2) 無系統鑄造的 Identity 層 —— 世界實體身份直接等同外部 API 識別碼字串，無生命週期管理；(3) 無 Confidence 語義 —— Knowledge 五元組缺第五元（grep 全庫零命中）。另有一項治權條文與憲章 MUST NOT 直接牴觸：原則精華 #7 明文制度化 last-write-wins 覆寫（P4.E5 禁止、依 §8.4 不可豁免）。

好消息是：多數補正為**增量而非重寫** —— raw 鏡像層本身是高品質的 Observation 儲存（合法且應保留）、系統內已存在幾乎每一種正確範式（FRED vintage 雙時間、review_log 留痕、trigger 級不變式、superseded 標記），缺的是把這些範式推廣為全系統義務。

## 二、合憲計分卡

| 原則 | 符合度 | 關鍵依據 |
|---|---|---|
| **P1 Reality First** | 🔴 顯著缺口 | 世界觀哲學正確（真兆框架、release_lag 把「公開時刻≠資料日期」當本體問題），但無 World Model 層，「API 即權威」立法為 F1（AUD-01）|
| **P2 Representation Before Intelligence** | 🟡 部分符合 | 審議通道教科書級（AUD 亮點 46–54）、advisor 機械閘 fail-closed；但主出單表可靜默重寫（AUD-08）、per-pick 解釋缺（AUD-18）|
| **P3 Identity Before Knowledge** | 🔴 顯著缺口 | 無 Identity 層（唯一 identity.py 是使用者認證）、無 lifecycle、跨來源零繫結（AUD-04/05/06/07）；量化知識繫識別碼、模型/文獻/來源身份治理是亮點 |
| **P4 Evidence Before Conclusion** | 🟡 部分符合 | valid-time PIT 紀律成熟、FRED 雙時間樣板級、byte-level attestation；但 LWW 制度化（AUD-02）、無 Confidence（AUD-03）、多處 DELETE 重建（AUD-09/20/21/22）|
| **P5 Accountability Before Action** | 🟢 大致符合 | 「不下單、不動錢」防線經全庫查證屬實、人拍板文化強、敏感自動化預設關閉；行動留痕缺六元組欄位（AUD-10/11）|
| **治權整合** | 🟡 部分符合 | 二十條與五原則映射基礎極佳；程序介面全缺：兩憲章撞名、無 Layer 登錄、無合規聲明（AUD-12/13/25）|

## 三、合憲亮點（54 項）

既有系統做對的事必須被記錄 —— 這些亮點同時是補正的既有範式庫。

### P1 Reality First（8 項）

* 北極星「真兆 vs 假兆」框架以世界真實性為最高判準：核心思想 v1.8.0 明文「只讀真兆，不造假兆。這就是系統的命」，每個量化數字須 trace 回真實 API 回應——表徵的合法性繫於 Reality 對應（referent），與 §1.3 第一條對稱禁令「沒有 Reality 對應，不允許 Representation」精神一致。
* release_lag.py 與 macro_vintage.py 把「DB 的 date 欄 ≠ 資訊在世界中公開可得的時刻」當第一級本體問題處理：財報/月營收/集保的 date 被換算為法定公開日，FRED 依「該數列在真實世界會不會被回溯修訂」分 Tier A/B 決定抓法（macro.py 明文：抓法由世界性質決定，非由 API 結構決定）——這是「資料結構不是世界結構」（P1.Y）的具體工程實踐。
* chip.py `_table_covers` 機械區分兩種缺席語意：「無列＝世界真無事件（真零）」vs「無列＝我們未同步（缺列）」，由雙側覆蓋 gate 強制判定而非假設——系統不把資料庫狀態誤當世界事實，直接呼應 P2.E4「Representation 不得被視為 Reality 本身」且服務 P1 的世界忠實性。
* 特徵定義以市場現實為準、拒絕資料表面值：panel.py 選用還原價因「除權息跳空非真報酬」（世界語意裁決資料選擇）；45 日 recency gate 防 stale 資料冒充當下世界狀態；valuation f5 特意用原始價防還原因子回溯洩漏——各處以「世界中真實發生什麼」覆核資料表提供什麼。
* 「日為最小單位」是由預測任務的世界時間尺度決定的資料本質界線（核心思想：「凡 API 有的日級真兆皆值得抓……不因抓取方式麻煩而捨棄真實資料」）——世界觀約束資料擷取，而非 API 供給約束世界觀；INTRADAY 物理拒收即此界線的機械執法。
* core_gate.py 明確認知「來源名冊 ≠ 世界實體集合」：TaiwanStockInfo 混入 'Automobile'/'TAIEX' 等非股票項（roster 污染，實證 31 項曾通過 gate），以結構性 predicate 排除並排 ETF（「被動指數追蹤非個股預測對象」）——以世界本體（什麼才是可預測的個股實體）修正來源資料的實體宣稱。
* catalog 層（dataset_catalog/column_catalog）對每欄做中文語意標註＋provenance＋last_verified，並明標「型別/中文＝augur 推導非 FinMind 權威」——雖仍以來源表為鍵，但已是朝向語意層映射的既有基礎設施，可作為補正的施工起點。
* raw 層作為 Observation 儲存的忠實性極高：NULL＝無值不捏造、值逐字照 API、DB↔API byte-level attestation、FRED vintage 保存雙時間——就 Meta-Constitution 的 Observation 義務（有 Source、有 Timestamp、忠實記錄）而言，這一層是模範品質的觀測層，補正時應保留而非拆除。

### P2 Representation Before Intelligence（9 項）

* 【P2.W2 候選斷言通道之教科書級實作】deliberation 層 LLM 輸出永遠只是提案：claim 以 status='pending' 落 deliberation_claim（含 provenance 記 model/lens/fast_path），唯 verifiers.verify_claim（src/augur/deliberation/verifiers.py:152-158，docstring 明文「全系統唯一把 status 寫成 'confirmed' 的地方」）能依五種確定性 oracle（information_schema/import_isolation/file_grep/db_query/pytest）之輸出升格 confirmed；我以 grep 全庫驗證 UPDATE deliberation_claim SET status 僅存在於 verifiers.py 兩處。anchor 不合契約=undecidable→escalated（fail-closed，寧升級人裁不硬猜）。
* 【多數不造真、人裁亦不造真】consensus.py:37-47 三級殺權：oracle refuted 單票即殺 > 任一 oracle confirmed > 全升級 escalated；consensus 絕不自行升 confirmed，並有零 IO selftest 固化為回歸鎖（consensus.py:83-94）。scripts/resolve_escalation.py 明文人裁只寫 escalation 三欄、人若認定為真須補可機驗 anchor 重裁——LLM 意見與人類意見皆零證據力，只有可重跑之確定性工具輸出（Observation of system reality）能生成 confirmed，完全符合 P2.E1 之精神。
* 【說話者身份與背書範圍機械分離】ledger.py report（98-106 行）之 confirmed·bound vs confirmed·anchor-only 二級制：系統只為錨點證明到的範圍背書，未語意綁定之 LLM 文字降格標註；advisor verdict_block/ultracode 尾註明示「宣稱原文=LLM 提出、非系統背書」。LLM 產物與系統背書全程雙標示，杜絕 P2.E2 之「model output 冒充權威表徵」。
* 【advisor 生成後機械閘（非 prompt 自律）】advise.py：檢索全空→不經 LLM 直回固定誠實句閉集（192-214 行）；數字必須 ∈ frozen PredictionPayload.numbers() ∪ citation_numbers 雙源白名單（guard.py:59-64、95-107）；引文須逐字 ∈ 檢索原文；picks 表由 payload 確定性排版、不經弱 LLM（advise.py _render_picks_table，註明「弱本機模型實證會幻覺選股」）；guard fail→固定誠實句、偽 SSE 全文過閘後才 emit（oai_compat.py _reply_text）。模型輸出中一切量化宣稱被機械限制在可溯源集合內。
* 【F5 於機率層之落實】prediction_probability 每列 calibrator_id FK 溯源至 probability_calibrator（method/params/Brier/ECE/reliability_bins/purge_verified/git_sha 全落表，migrate_probability_ddl.py:51-71），econ_verdict 判死標籤與機率同列硬綁不可分離；payload.validation 每個數字以 _VALIDATION_LEDGER_KEYS 座標 trace 回 revalidation_ledger 一列（payload.py:96-109，「非記憶/估算」）——每個對人呈現的機率/驗證數字都能回答「為什麼、依據哪次驗證」。
* 【絕對方向機率之預註冊 GATE 治理】advise.py:152-154 對方向/目標價/逐日漲跌題短路弱 LLM 直回固定誠實句（gate 狀態 SSOT=direction_gate 表）；direction_gate 有 DB trigger 機械擋挪門柱（migrate_direction_gate_ddl.py:42-75：非 preregistered 後 criteria 不可變、終態 result_snapshot 不可回改、非 preregistered 不得刪、approve 須簽核），evaluated_fail 判死留檔永不出 UI——未經 Evidence 通道確立的方向智慧被結構性禁止對人輸出。
* 【F2 反模型優先之架構事實】表徵管線（raw→feature→universe→label）先於且獨立於模型；models/ranker.py 契約極薄（fit/predict，「SHAP 明訂不在此層」防模型層膨脹）；advisor llm_fn 為抽象界面「advisor 本身不綁特定 LLM」（advise.py docstring）；model_registry 凍結 feats_hash/git_sha/seed/train_span，predict_asof.py:123-124 feats_hash 不符即拒出單——模型是可換的推理工具，世界表徵層是恆定基座。
* 【模型輸出不得自迴圈（防信任洗白）】prediction_values 與 prediction_probability 皆以 COMMENT+AST 稽核（import_isolation）+DB GRANT（augur_predict role 不授 SELECT）三重強制「禁被預測 7 package 回讀當特徵」（migrate_prediction_ddl.py:61-63、migrate_probability_ddl.py:88-90 A-28）——Computational Evidence 不會經轉手變成 Observation。
* 【Learning 產物過通道（EV.12 通道義務）】蒸餾管線：teacher 只教行為不供事實（advisor_distill_teacher.py 界線-B）；S5 硬校驗 gold 內任何事實斷言 token ⊂ 真實檢索 context、不過即丟「絕不放流暢唬爛入訓練集」（advisor_distill_validate.py）；bridge_deliberation_distill.py eligible() 只橋接有 is_deterministic verdict 之 confirmed/refuted claim，escalated/undecidable 不入題「無機械真值=不可教」；distill 表已自 augur_predict REVOKE。

### P3 Identity Before Knowledge（9 項）

* 量化 Knowledge 全數繫結識別碼（F4 大體滿足）：feature_values PK=(panel_date, stock_id, feature)（src/augur/features/panel.py DDL）；prediction_values PK=(panel_date, model_id, stock_id) 且 model_id FK 至 model_registry（scripts/migrate_prediction_ddl.py）；direction_arena_prediction PK=(model_key, target_id, pred_date, horizon_td) 且 FK 至 direction_arena_candidate（scripts/migrate_direction_arena_ddl.py）——每筆特徵值/預測皆可回答「關於哪個標的、由哪個模型產生」
* Agentive Entity 身份完備：model_registry 以 model_id 為永久識別碼並凍結 git_sha/feats_hash/seed/artifact_path/train_span；direction_arena_candidate 凍結 code_sha/weights_hash 且 status 用 retired（非 DELETE）——模型作為行動者之身份可溯且退役留痕
* 識別碼語意保護：generic_schema.py 的 FORCE_STR 保識別碼前導零（'0050'≠50），防止 identifier 被數值化而失去身份語意
* 下市實體之資料層身份持續：raw 層 upsert 不刪列，已下市股全史保留；audit/reconcile.py 明文「已下市/名冊外但 DB 有史之股仍保留比對、不產假 EX」（line 144, 273）——實體退場後其 Observation 不消滅；core_universe_asof 逐 as-of 快照消 survivorship、settle_arena_labels 對消失標的標 unsettleable 而非靜默排除
* 知識來源身份治理成熟：knowledge_source 以 source_key 為識別碼，knowledge_source_review_log 記錄全生命週期每次狀態轉移（actor/os_user/reason/probe_result，scripts/migrate_source_governance.py:84-97）；curation.norm_doi 為 DOI 跨形態同一性判準之 SSOT（明文處理「同一 DOI 多種寫法」之 identity resolution）
* 文獻實體有一級身份表：philosophy_thinker（name UNIQUE + 生卒年）、philosophy_work（thinker_id FK）（src/augur/philosophy/framework.py:69-87）；scripts/audit_work_attribution.py 以 gutendex 確定性比對作者姓名 token+生卒年驗證「作品↔作者」identity claim，誤配即 review_flag 隔離——身份錯繫被視為必須主動稽核之風險
* 資料源（dataset）身份：dataset_catalog 每 dataset 一列含 source/source_provenance/last_verified，column_catalog 欄級 provenance（src/augur/catalog/__init__.py:225-268）——資料來源本身是有身份、有生命週期戳記的一級物件
* 對人輸出之身份幻覺防護：advisor/guard.py 第⑤閘機械校驗輸出中「股號+緊鄰股名」須與 payload 身份相容（如 '2330 鴻海' 被擋，line 74-81）——身份錯配被當防幻覺一級檢查
* 使用者身份 fail-closed：knowledge/identity.py + RBAC resolver 對 None/不存在使用者絕不當 super、空群組=deny——行動者身份缺失一律拒絕

### P4 Evidence Before Conclusion（10 項）

* P4.E2 樣板級實作（FRED）：src/augur/ingestion/fred.py 以 (series_id, date, realtime_start) 複合主鍵存 ALFRED 全 vintage，realtime_start＝該值成為現行版之起日（真 transaction time）；ingest 落地前守門既有 PK 必含 realtime_start，把「靜默塌版」變成程式強制錯誤——這正是憲章 valid time／transaction time 二分的正確實作，可作為全系統雙時間化的內部範本
* P4.E6 遞迴溯源（審議層）：deliberation_claim.provenance（jsonb，記 model/lens/fast_path/lint/redline）＋ deliberation_verdict 之 DDL CHECK「verdict='undecidable' OR evidence IS NOT NULL」（scripts/migrate_deliberation_ddl.py:75）——裁決不得無證據，且 verdict 為 append-only 附 ran_at，證據鏈機器可稽核
* P4.E5 尾句「目前證據不足為合法且必須可表達之狀態」已制度化：claim status 含 undecidable/escalated、deliberation_escalation 表落帳待人裁；advisor 檢索空時不經 LLM 直回誠實固定句閉集（src/augur/advisor/guard.py 二句閉集＝憲章判準）——「不知道」是一級狀態而非失敗
* P4.E7 信任不可洗白（結構性強制而非標記自律）：knowledge/admission.py:62-63 冗餘明擋 source_type='ai_generated'（DB CHECK 同錨，philosophy/framework.py:52）；LLM 輸出在審議引擎中零證據力——verifiers.verify_claim 為全系統唯一 confirmed 寫點，consensus「多數不造真、oracle 反證單票即殺」；advisor/effort.py:159-165 verdict_block 逐行標「宣稱原文(LLM 提出)、非系統背書；系統背書僅及 oracle 證據行」——說話者身份被機械標記，等效於 synthetic 標記且更嚴
* P4.E7 高風險結論不得僅以系統自身產出為據：gate 裁決以 OOS 市場資料（獨立 Data Evidence）為準、approve 唯人（TTY 閘＋approved_by 姓名留痕）；HANDOFF 誠實紅線「Sharpe 引用必附未過 deflation」＝信任上限受最弱環節約束的實務化
* P4.E6 Computational Evidence 溯源：model_registry 以 model_id 記 family/horizon/train_span/asof/feats_hash/git_sha（scripts/migrate_prediction_ddl.py:25-36），prediction_values FK 至 registry——每個模型輸出可回溯至凍結之程式版本與特徵口徑；trial_ledger 機械計多重比較 N，禁人手
* P4.E3 精神在治權層已現：gate 廢止＝superseded 非 DELETE、終態 result_snapshot 有 DB trigger 擋回改、結算欄 trigger 保證唯 NULL→值一次（settle_arena_labels）；knowledge/curation.py 每次狀態轉移 append review_log（actor/os_user/reason/probe 證據）——覆寫式 UPDATE 被日誌補齊為全歷史
* P4.E4 可謬性（部分）：philosophy/framework.py 明文 direction＝文獻預期假說、validated_ic 須系統自身實證回填——文獻主張不被當真值；憲章修訂歷程三度留痕「AI 勸阻全文＋用戶堅持決定」並列，修憲本身踐行 Evidence Before Conclusion
* P4 證據正面性：audit/reconcile.py 之 coverage_gap/incomplete blocker（「沒比到≠比過且乾淨」）、假綠教訓（rc=0≠PASS）入憲成回歸鎖、負向自證紅測（leak_mode）——系統對「證據缺席」與「證據存在」嚴格區分，不以程序成功冒充語意證據
* P4.E2 valid-time PIT 紀律極強：features/release_lag.py 將「date≠公開日」翻成法定公開可得日、macro_vintage 為 fred_series 唯一 PIT 消費門（未知 series fail-loud）、core_universe_asof 逐 t 快照消 survivorship——「決策當下看得到嗎」已是機械化公理

### P5 Accountability Before Action（7 項）

* 「不下單、不動錢」經全庫查證屬實（P5.W2/EV.9）：grep 全庫無任何券商/下單 API 整合（無 shioaji/fugle/place_order 等實際整合，唯一命中為註解與 dataset 名稱）；src/augur/execution/risk_control.py 明文「只出降倉建議 + 告警旗標 + cap 後權重,不自動下單、不動錢」且僅回傳建議 dict；scripts/predict_asof.py 出口三處明文「系統建議、人決策、不下單」。系統對外的因果迴路在 Action 端天然斷開，Human Authority Gate 由架構保證而非僅口號。
* 人類權威為授權鏈根節點之機械強制（P5.W2）：src/augur/knowledge/curation.py:46-50 升級動作須 sys.stdin.isatty() + getpass.getuser()（明文「防被腳本/AI 管道呼叫」），每步寫 knowledge_source_review_log(actor/os_user/reason/probe)；scripts/preregister_direction_gate.py:323 與 preregister_unfreeze_gate.py approve/freeze 同樣 TTY 閘 + approved_by/approved_at 留痕 + DB trigger 擋事後挪門柱；scripts/serve_admin_console.py:639 明文「升級動作(approve 唯人)不經 web,只印 copy-ready CLI」——web 面板無法繞過 TTY 人核閘。
* 自我修復行動邊界收斂且終態回到人（P5.W3 精神）：audit_selfheal.sh rc=2（attestation FAIL 終態）明文「不重試,待根因」直接 exit；48 次上限後「人工介入」；audit_watchdog.sh:21-24 見 FAIL 終態「不 relaunch,待根因」；daily_maintenance.py --heal 明文「EX 紅旗仍不自動碰」且 src/augur/audit/reconcile.py:82 fix_keys 註解「EX 不入=紅旗不自動碰」、heal「寫入仍走 sync_by_date 的 upsert 路徑（非 hand-patch）」——自動化僅限可重試之資料補抓，判準/部署/金錢層永不自動觸及。
* 敏感自動化預設關閉、待人開閘（P5.W5）：install_services.sh:199-202 l2-deliberation 與 knowhow-refresh timer 僅 enable 不 start，明文「待 hugo 開閘(--with-l2/--with-refresh)」；scripts/run_daily_deliberation.py 明文「本工具永不改資料/不 commit/不觸外部 API;裁決效力止於帳本,人只看佇列」——延長無人工檢核之自動執行鏈的變更保留給人類逐案決定，與 P5.W5 推定同向。
* 非 Agent First 的建構順序（F3 反面對齊）：advisor/deliberation 等 agent 全部建立在先行完成的資料治理之上——advisor 有生成後 guard 機械閘、knowledge 有 admission 四件 fail-closed 閘、deliberation 的 LLM 輸出僅為提案且 verify_claim 為全系統唯一 confirmed 寫點、import_isolation AST 稽核保證預測管線零 import 素養層。資料治理先於且約束 agent，恰為 F3 所要求之順序。
* 行動留痕文化已具雛形（P5.E1 部分要素）：serve_admin_console.py 有審計 log（明文「誰/何時/何動作」，AUDIT_LOG 落檔）；attestation_result 表有 driver 欄記錄驅動者（daily_maintenance.py:140 組合 driver 字串含 --audit-only/--heal 旗標）；review_log 記 actor/os_user；人為拍板以「hugo YYYY-MM-DD 拍板」+ 理由嵌入程式註解，形成非結構化但密集的決策審計軌。
* 內部治權已有與 P5 同構的「決策層人拍板/執行層 AI 自駕」原則（原則精華 #20/#26），且有 AI 拒絕違反核心紀律指令之先例——授權鏈根節點為人類的精神已內化為既有憲章實踐，補正主要是形式化與機讀化而非文化重建。

### 治權整合（11 項）

* 20 條→MC 五原則映射總覽（親讀全文比對）：A 區 #1-7/#17/#18 → P1/P4（資料忠實與溯源）之領域實例化；B 區 #8-12 → P4.E2 雙時間性/P2 表徵先行/§2.3 語義唯一性；C 區 #13-15/#19 → P4 證據紀律與 P5 風險精神；D 區 #16/#20 → P4.E7 信任不洗白/P5 人類權威。整體高度相容——唯 P3 Identity 完全無對應原則（見 findings）。
* #1 零幻像＋#15 誠實回報＋北極星三問＝PA「以可追溯 Evidence 忠實表徵真實世界」的成熟先行實踐：「每個量化數字 trace 回 (a)程式/(b)DB/(c)API」直接落實 P4.E1/P4.E6；「不存沒有 API 來源的值」逐字對應 §1.3 第一禁令（沒有 Reality referent 不允許 Representation）；「不把計畫當成果」對應 P2.E3 禁止意圖直寫為世界狀態。
* #8 Anti-Leakage 體系（release_lag 法定公開日 gate、fred_series realtime_start vintage、purged walk-forward＋embargo、core_universe_asof 快照消 survivorship）＝P4.E2「任一過去時刻系統之認識狀態必須可追溯」之深度領域操作化，其機制精細度超出 MC 現文——值得上呈為 Layer 4 Knowledge System 規格之 as-of 重建能力素材。
* 審議引擎（大憲章 v1.45.0 承載＋deliberation package）＝P2.W2 候選斷言機制與 §2.11 Evidence 通道的完整機械實作：LLM 輸出＝提案零證據力、verify_claim 為全系統唯一 confirmed 寫點（DB CHECK 同錨）、oracle 反證單票即殺、undecidable 一律 escalated 進人裁佇列、人裁亦不造真——「多數不造真」比 MC 條文更嚴。
* P5 人類權威已為活紀律：決策層人拍板/執行層 AI 自駕（原則精華 #20）、approve/activate 唯 superuser TTY 人執行（憲章 v1.41.0 來源治理審批不變式）、系統「不下單、不動錢」（靈魂邊界）＝P5.W2 授權鏈根節點為人類；v1.18.0 修訂歷程記載 AI 拒絕用戶「AI 整理版權著作入庫」指令（違 #1 命門）改提合規路獲接受——原則位階高於單次指令之實例，與 §8.2 保守解釋同向。
* 修訂治理實質接近 §8.5/§8.6：憲章修訂歷程 45 版逐版記動因＋同步清單＋SUPERSEDED/ACTIVE 狀態（≈Amendment Log）；原則條號按新增順序編、永不重排（#1-20 非連續）＝§8.6 編號穩定性；「AI 勸阻全文與用戶三度堅持並列留痕（勸阻不消音、決策不掩蓋）」（v1.42.0/v1.44.0/v1.45.0）＝裁決書面化、附理由、公開存檔之精神。
* #9「思想≠特定值」與 philosophy 層「哲學＝假說非真兆、驗證活下來非大師說了算、禁 AI 生成入庫」＝MC 現文所無的「外部知識如何合法進入 World Representation」判準（假說→可證偽因子→OOS＋經濟裁決）——值得上呈至 Layer 4/5 規格。
* 預註冊可證偽 GATE 體系（判準 sha256 先凍後跑、DB trigger 機械擋挪門柱、家族 K 封閉 Bonferroni＋跨家族全序列揭露、no-v3 二次證偽凍結、fail 判死留檔永不出 UI）＝P4「Evidence Before Conclusion」之統計嚴謹化與多重比較治理，MC 未涵蓋——上呈候選。
* #19 凌駕邊界「三敵零容忍、不是試錯對象」與 #12 SSOT「一概念一權威家」分別同構於 §8.4 不可豁免核心與 §2.3 語義唯一性；guard 單向棘輪（只得加嚴、放鬆＝禁）同構於 §8.2 較嚴格解讀原則。
* P4.E7 NoLaundering 精神已有等價物：禁 AI 生成內容入庫（admission_gate fail-closed＋DB CHECK）、advisor verdict_block 雙標示（宣稱原文＝LLM 提出非系統背書；系統背書僅及 oracle 證據行）、審議 claim provenance 全鏈留痕＝synthetic 標記與「說話者身份」機械區分。
* append-only 與留痕傾向部分落實 P4.E3/§5 角色一：gate 廢止＝superseded 非 DELETE、attestation_result/data_audit_log/trial_ledger/review_log 構成證據帳本、附錄 A「寧空不填舊數字」；「目前證據不足」為合法狀態（escalated＝誠實待人裁非失敗）直接對應 P4.E5 末句。

## 四、差距發現（26 項，依嚴重度排序）

> severity 分級（依 AUGUR-MC §8.2/§8.4）：critical＝違反不可豁免核心或禁止性規定；major＝違反 [N] 義務；minor＝部分符合但有缺口。
> ⚠️ 所有發現之證據均經整併官親自重驗（「親查屬實」），但設計中的獨立雙重對抗驗證（程式碼查證官＋憲章適用裁判官）因故未執行 —— severity 與條款適用暫列為初步判定。

### AUD-01【CRITICAL】資料來源 schema 即系統最高抽象：全系統無 World Model／Ontology 層，治權條文（「API 即權威」）且將此立為法律（F1 教科書式命中）

* **憲章條款**：F1（禁止 Data First Architecture）、P1.E1（資料來源不得成為最高抽象）、P1.E2、§0.5（Layer 1/2 規格缺位）
* **位置**：src/augur/core/generic_schema.py（全檔）；docs/原則精華_v1.9.0.md #2/#3；docs/系統架構大憲章_v1.45.0.md L26-28 及第三部管線分層
* **發現視角**：P1 Reality First + F1 Data First Architecture、治權整合（文件級審計）

**描述**：系統的 schema 生成哲學是「看 API 資料長相，自動推導型別、建表」：表名＝FinMind dataset 名逐字、欄名/欄序照 API（#2）、型別由觀測值推導、主鍵貪婪偵測，且治權條文明文立法——原則精華 #2「表名/欄位/型別一律以 API 回應為準（逐字）…API 是唯一事實」、#3「無 dataset 白名單」、大憲章第三部以資料流（raw→feature→universe→model→validate）為全部架構組織軸。全 repo 不存在任何 World Model/Ontology 等價層：僅 3 個 VIEW（皆為知識覆蓋統計）、無語意映射層、無世界實體/事件/狀態宣告；下游智慧層以 SQL 字面常數直綁 vendor 表名消費（整併官親查 grep 'FROM "Taiwan' 命中 15+ 檔，較原審計 10 檔更廣）——資料來源的結構就是系統理解世界的結構，即 F1 明文禁止之「先建資料表，再想世界模型」且至今未想。文件鏡頭指出重要化解路徑：raw 鏡像層本身作為 Observation 儲存是合法且高品質的（忠實鏡像 API＝忠實保存觀測，符合 P2.E4），靈魂之世界觀（相對強弱、三敵）扮演隱式 world model——違憲點在於治權檔從未做此定位宣告，「API 即權威」現為無限定之最高抽象宣稱，其上無 Representation 層。

**證據**：generic_schema.py L1-17 docstring（親查屬實）：「看 API 資料長相，自動推導型別、建表…欄名/欄序照 API（#2）…任意 API dataset 都能落地、無白名單（#3）」；panel.py L49-53 _PRICE_SQL 直綁 'FROM "TaiwanStockPriceAdj"'；grep 'FROM "Taiwan' 命中 features/chip.py、valuation.py、phase.py、margin_cycle.py、advisor/payload.py、arena/adapters.py、audit/、scripts/ 等 15+ 檔；grep 'CREATE.*VIEW' 全庫僅 migrate_source_governance.py 3 個知識統計 view（親查屬實）；原則精華 #2/#3 條文與大憲章 L26-28「一切資料的唯一真相來源(SSOT)…皆為本地 PostgreSQL」親查屬實；docs/ 無任何 world model/ontology 文件。

**補正方向**：雙軌補正：（一）規格面——撰寫最小 Layer 1 World Model／Layer 2 Ontology 規格，列舉台股市場世界的實體（Security、Issuer、TradingCalendar、CorporateAction、EconomicIndicator、行動者）、事件與狀態；原則精華 #2 加定位限定：「API 即權威」之權威範圍＝Observation 之形（schema/值域），非世界結構之權威；明文宣告 raw 鏡像表＝Observation 儲存（保留其全部 attestation 紀律）、其上建共同表徵層。（二）工程面漸進路徑——第一步建「世界概念→來源表.欄」映射 registry（可擴充既有 column_catalog），第二步把消費模組的 SQL 字面常數改為經 registry 解析（消除表名直綁），第三步以 view/中介表落實世界概念的唯一權威表徵。依 §8.3 過渡規則申請既存實作補正期；此定位化解後 F1 之最嚴重形態即不成立。

### AUD-02【CRITICAL】raw 層系統性 last-write-wins：治權條文（原則精華 #6/#7）明文制度化覆寫，value_mismatch 舊值經 heal 滅失、矛盾證據不共存

* **憲章條款**：P4.E5（禁止 last-write-wins，MUST NOT 依 §8.4 不得豁免）、P4.E3（只失效不刪除）、P4.E2（雙時間性）
* **位置**：src/augur/core/generic_schema.py:256-273（upsert）；src/augur/audit/reconcile.py:48,93,125（_EXAMPLES_CAP）；docs/原則精華_v1.9.0.md #6/#7（L52）；src/augur/core/schema.py:53-69（attestation_result 僅存計數）
* **發現視角**：P4 Evidence Before Conclusion、治權整合（文件級審計）

**描述**：此非實作偏差而是治權條文明文要求：原則精華 #7 ENFORCE（親查 L52）規定 value_mismatch 修正路徑＝「用同一條 sync 路徑重抓…冪等 ON CONFLICT DO UPDATE 自然覆蓋為當前 API 值。無獨立修正程式：correction＝重跑正常 sync」。實作完全遵行：generic_schema.upsert 為 ON CONFLICT DO UPDATE SET col=EXCLUDED.col，批次內去重明文「保留最後一筆＝API 最新」；當 attestation 偵測到 value_mismatch（DB≠API，即兩個不同時點的 Observation 互相衝突），heal_by_date「寫入仍走 sync_by_date 的 upsert 路徑」將 DB 既有值原地覆寫為 API 現值。衝突舊值僅以 examples 留存，上限 10 筆且只存在於回傳值/日誌；attestation_result 表僅落計數與 note，不落被覆寫舊值本體。舊值一經 heal 即不可恢復（API 已不供應該版本）。這正是 P4.E5 明文禁止的 last-write-wins：衝突證據未共存、未顯式標記、被靜默消滅；憲章要求裁決（API wins）作為新 Knowledge 落帳、永不覆寫原始證據。大憲章附錄 C 自承此缺口（「可選補之小缺口…as-of/bitemporal 形式化」）。部分緩解已存在：#7 要求差異記錄留存、data_audit_log 批次留痕、fred_series 有 realtime_start vintage、FRED 路徑明文「不刪 DB 真值」（reconcile.py:487 親查屬實）——證明系統知道且能做到保存，僅 FinMind 主路徑未做。

**證據**：整併官親查全部屬實：generic_schema.py:256-273 upsert 註解「批次內同主鍵去重（保留最後一筆＝API 最新）」＋ 'INSERT INTO … ON CONFLICT ({conflict}) DO UPDATE SET {sets}'；reconcile.py:19-20「寫入仍走 sync_by_date 的 upsert 路徑」、:48 _EXAMPLES_CAP=10、:93 examples 截斷、:125 聚合再截斷；attestation_result DDL（schema.py）僅 passed/matched/value_mismatch 等計數欄無差異值欄；原則精華 #7 L52 條文逐字屬實；reconcile.py:487「不刪 DB 真值」對照組屬實。

**補正方向**：MUST NOT 牴觸、依 §8.4 無時限豁免可言，列補正計畫最高優先：(1) 最小侵入——heal 覆寫前將受影響舊列快照至 supersede 帳表（raw_supersede_log：table/pk/old_row jsonb/superseded_at/reason/attestation_run_id），與 heal 同交易寫入，衝突雙方共存、裁決成為攜帶自身 Evidence 的新紀錄，upsert 主路徑不動；(2) 修訂原則精華 #7 條文：correction 由「覆蓋為當前值」改為「新版本入庫、舊版本標 superseded、對帳以現行版比對」，「byte-equal API」判準重述為「現行版 byte-equal API 當前回應」以保留 attestation 語意；(3) 長期對已知會 restate 的 FinMind 表比照 fred_series 加 transaction-time 版本欄；(4) 於合規聲明揭露此緊張關係與補正期程。

### AUD-03【CRITICAL】全系統無 Confidence 概念：Knowledge 五元組缺第五元、無單一形式化語義、不傳播——量化軸校準成熟但與知識/審議軸互不相通

* **憲章條款**：P4.E1（不可豁免核心）、P4.E8（單一形式化定義、沿推理鏈傳播）、P4.E4（Confidence 不得隱含 1.0）
* **位置**：src/ 與 scripts/ 全域（grep -ri confidence 零命中，整併官親自重跑確認）；scripts/migrate_deliberation_ddl.py:59-60；src/augur/philosophy/framework.py:43-44；docs/系統架構大憲章_v1.45.0.md（v1.40.0/v1.42.0 誠實判準條）
* **發現視角**：P4 Evidence Before Conclusion、治權整合（文件級審計）

**描述**：P4.E1 要求任何 Knowledge 必須具 Source/Timestamp/Identity/Evidence/Confidence 五元組為最低不變式；P4.E8 要求 Confidence 於 Layer 4 以單一形式化定義、全系統可比較、沿推理鏈向下游傳播。整併官親自重跑 grep -rni confidence 於 src/ 與 scripts/ 全部 .py：零命中。系統以類別型狀態替代：deliberation_claim.status 五值枚舉（oracle confirmed 事實上隱含 1.0）、attestation passed BOOLEAN、validation_evidence green/amber/red——隱性的二值/三值 confidence，無形式化定義、彼此不可比較、不傳播。文件鏡頭補充重要脈絡：預測軸的可信度治理極成熟（walk-forward IC/Eff-t、Brier/ECE/可靠度分箱、purged 校準器 provenance、禁 iid 顯著性），是 P4.E8「評定方法可追溯」的優秀實例——但校準機率與審議裁決、知識層信任分級是三個互不相通的物件，無「Action 允許等級受最低 Confidence 約束」之對應（P4.E8 末句），knowledge item/philosophy_principle 無 confidence 欄（validated_ic 為 IC 統計量而非 confidence）。P4.E1 屬憲章不可豁免核心，缺一元即構成核心違反。

**證據**：grep -rn -i "confidence" src/ scripts/ --include="*.py" 回傳空（整併官親自執行確認）；deliberation_claim DDL status CHECK 僅 ('pending','confirmed','refuted','undecidable','escalated') 五類別值（親查 migrate_deliberation_ddl.py 屬實）；attestation_result.passed BOOLEAN（親查 core/schema.py 屬實）；大憲章 v1.40.0 相對機率誠實判準僅及預測輸出；審議 confirmed·bound/anchor-only 二級制為呈現級非信心值；全治權檔無 confidence 傳播/消費規則條款。

**補正方向**：於 Layer 4 規格定義單一 Confidence 形式化語義（可為有序類別而非機率——憲章未強制數值），並建立既有狀態之官方映射表：oracle confirmed＝確定性證據（明文其 1.0 正當性依據＝可重放機械驗證）、校準機率＝預測 Confidence、confirmed·bound／confirmed·anchor-only／escalated／refuted／green／amber／red 各映 confidence 等級、knowledge item 至少繼承來源信任分級（license/審批狀態已是現成基礎）；新增 Knowledge 承載表之 confidence 欄與消費規則（Action 允許等級受最低 confidence 約束）；映射表本身依 P4.E6 留 provenance；暫行期依 §8.3 保守解釋（無 Confidence＝不得升高信任）。既有機制大多可保留，缺的是統一語義層而非重寫。

### AUD-04【MAJOR】無系統鑄造之 Identity 層：世界實體身份直接等同外部 API 識別碼字串、命名空間混雜多種實體類型、治權二十條對 P3 完全無對應原則

* **憲章條款**：P3.W1、P3.E2（identifier 鑄造與生命週期）、P1.E2（Identity 跨部署邊界可解析對齊）、F4
* **位置**：src/augur/universe/core_gate.py:9-13,74-79；src/augur/knowledge/identity.py；src/augur/ingestion/sync.py:47-48；scripts/build_market_direction_features.py:52-54；docs/原則精華_v1.9.0.md（全檔四區）
* **發現視角**：P1 Reality First + F1 Data First Architecture、P3 Identity Before Knowledge + F4 Knowledge Without Identity、治權整合（文件級審計）

**描述**：全系統唯一名為 identity 的模組（knowledge/identity.py）僅處理使用者密碼/session 認證（親查：hash_password/authenticate/issue_session 等函數）；世界實體（股票、指數、公司）無任何系統鑄造之 identifier、無 identity 表、無 identity 層。股票身份＝FinMind 原生 stock_id 字串，TaiwanStockInfo（來源鏡像表）即名冊權威（sync.py seed_roster 親查屬實），而該命名空間實證混入產業分類名（'Automobile'/'Tourism'）與指數代號（'TAIEX'/'TPEx'）——實證 2026-06-24 曾有 31 個污染項通過 gate；系統以各消費端自備的 regex 啟發式（_REAL_STOCK_PREDICATE = "stock_id ~ '^[0-9]'"）判定「什麼是真股票」，同一字串空間同時被 panel.py 當股票身份、被 build_market_direction_features.py 當指數身份（WHERE stock_id='TAIEX'，親查屬實）消費——實體類型由每個消費者臨場判定，而非由 Identity/Ontology 層宣告。FRED 實體用 series_id，與 stock_id 零交集且無跨來源解析設施。每新增一個資料來源，其識別碼空間即自動成為又一個平行身份空間；來源識別碼空間的缺陷（roster 污染）直接成為系統身份空間的缺陷，由下游逐點過濾而非在身份層一次解決。文件鏡頭確認此缺口同時是治權缺口：逐條映射顯示 MC 五原則中唯 P3 在二十條中無任何對應——identifier 之鑄造、永不刪除、下市/更名/代碼重用之 lineage、同一性判準宣告皆無治權條款承載。

**證據**：core_gate.py:77-79（親查屬實）：「真股票代碼 SQL predicate:數字開頭…roster 污染如 'Automobile' / 'TAIEX' / 'Tourism' 純字母開頭排除」＋ docstring L9-13「TaiwanStockInfo.stock_id 欄混入產業分類名＋指數代號…實證 2026-06-24 PHASE 8 後處理發現 31 個污染項通過 gate」；build_market_direction_features.py:53-54（親查屬實）：SELECT … FROM "TaiwanStockTotalReturnIndex" WHERE stock_id='TAIEX'；knowledge/identity.py 全檔僅使用者認證函數（親查屬實）；sync.py:47-48 seed_roster 以 TaiwanStockInfo 回 stock_id list（親查屬實）；全庫無 entity/identifier 鑄造表、無 alias/identity-claim 表；原則精華四類分布（A 資料/B 建模/C 風險治理/D 開發協作）遍查無 identity/同一性/identifier 生命週期條款。

**補正方向**：建立 Layer 3 Identity 規格與最小 entity registry：系統自鑄永久 identifier（如 augur:security/2330、augur:index/TAIEX、augur:fred_series/DGS10），mint 後永不刪除（P3.E2）；來源識別碼（stock_id/series_id）降格為繫結於系統 identifier 之 identity claim/alias；實體類型由 registry 宣告而非消費端 regex 判定；roster 淨化移至身份解析層一次完成（污染項＝解析失敗的 provisional identity、不升級），下游 predicate 過濾改為引用已解析身份。既有 raw 表可不動（外部識別碼為 Observation 之指涉資訊，符合 P3.E1 provisional identity），Knowledge 層（feature_values 等）逐步改繫系統 identifier。治權面同步補身份條款（依既有升版規則屬新增原則→升版），涵蓋 philosophy_work/thinker、app_user 等既有實體表之同一性判準宣告。

### AUD-05【MAJOR】Identity Lifecycle 全面缺席：下市資料已落地但零身份層消費，stock_id 回收重用會使兩家公司歷史靜默縫合

* **憲章條款**：P3.E2（Identity Lifecycle：merge/split/retire 為 Evidence 支持之 Knowledge、identity lineage）
* **位置**：scripts/migrate_attestation_catalog_ddl.py:38；src/augur/features/panel.py:49-53；src/augur/features/valuation.py
* **發現視角**：P3 Identity Before Knowledge + F4 Knowledge Without Identity

**描述**：FinMind 提供 TaiwanStockDelisting（下市櫃事件）且已入 raw 層，但整併官親查 grep 全 src/+scripts/：僅命中 migrate_attestation_catalog_ddl.py:38 一處（cadence 豁免註記「事件(下市、週-月間隔)」）——全 codebase 無任何消費者將下市事件升級為身份層 Knowledge：沒有 retire 狀態、沒有 merge/split/改名追溯、沒有 identity lineage。具體風險：台灣交易所會回收重用股票代碼；特徵計算一律以裸 stock_id 取全史（panel.py _PRICE_SQL：WHERE stock_id=%s AND date<=%s ORDER BY date，親查屬實；valuation 十年線位置取 10 年史），若代碼被重用，前一家公司的價格史會直接餵進新公司的動能/波動/十年百分位特徵，且無任何機械防護或告警。公司改名/合併同樣不可表徵。survivorship 相關處理（unsettleable、asof 快照）是行為層誠實，不是身份層生命週期——系統知道「標的消失了」，但不知道「這個 identifier 現在指誰」。（緩解：panel.py 之 recency gate MAX_STALE_CALENDAR_DAYS=45 會使長期停更股整股缺列，可部分緩衝重用縫合之即時影響，但非身份層機制、不解歷史縫合。）

**證據**：grep TaiwanStockDelisting 全 src/+scripts/ 僅 migrate_attestation_catalog_ddl.py:38 一處命中（整併官親自執行確認）；panel.py _PRICE_SQL 'FROM "TaiwanStockPriceAdj" WHERE stock_id = %s AND date <= %s AND close > 0 ORDER BY date'（親查屬實）；grep '下市|delist|merger|合併' 於 src/ 命中處全為對帳豁免與倖存偏差統計，無 identifier 轉指/退役機制。

**補正方向**：以既有 TaiwanStockDelisting raw 資料建 identity lifecycle 事件表（identifier、event_type=retire/relist、event_date、evidence 引用 raw 列）；feature builder 與 label 構造取全史時以 lifecycle 邊界截斷（同一 stock_id 之不同存續期視為不同實體實例）；代碼重用偵測可機械化（同 stock_id 在 delisting 事件後再現於名冊即紅旗）。此為 P3.E2「merge/split/retire 為必須引用 Evidence 之 Knowledge」的最小落地，與 AUD-04 之 entity registry 相銜接。

### AUD-06【MAJOR】FinMind 與 FRED 各自為政：無共同世界模型映射、無同一性判準宣告、零跨來源繫結機制，唯一設計交會點（feature_values macro）目前為空

* **憲章條款**：P1.E2（所有資料來源映射至共同世界模型、每一世界事實有唯一權威表徵）、P3.E3（每類 Identity 必須宣告同一性判準；instance/type 明示）
* **位置**：src/augur/features/macro_vintage.py:13-14；src/augur/features/macro.py:52；src/augur/ingestion/fred.py；src/augur/features/panel.py:40-47；src/augur/philosophy/framework.py:39-46
* **發現視角**：P1 Reality First + F1 Data First Architecture、P3 Identity Before Knowledge + F4 Knowledge Without Identity

**描述**：兩個資料來源以完全不同的 schema 形態各居孤島：FinMind＝逐 dataset 鏡像表（鍵 stock_id/date），FRED＝fred_series 長表（鍵 series_id/date/realtime_start），無任何共同世界模型交會——設計上預定的交會點 feature_values 目前「零 macro 特徵」（macro_vintage.py 自我誠實揭露，親查屬實），且 feature_values 本身是衍生訊號面板（panel_date, stock_id, feature, value），記錄計算產物而非世界事實表徵，無法承擔共同世界模型角色。同一性判準層面：「TaiwanStockPrice 的 2330、TaiwanStockInfo 的 2330、feature_values 的 2330 是同一實體」是隱含的字串相等假設，無任何地方宣告股票類 Identity 的同一性判準（P3.E3 義務）；FRED DEXTAUS（新台幣對美元匯率，macro.py:52 親查屬實）與 FinMind 匯率類 dataset 描述同一世界事實，兩者在系統內是互不知情的平行表徵，無 identity claim 機制可表達「兩個 identifier 指涉同一世界事實」、無唯一權威表徵指定。Knowledge 繫結對象屬 instance 或 type 亦未明示（principle_factor_map 之 feature 欄為裸 VARCHAR、type 級；feature_values 為 instance 級，結構上無區分標記）。P1.E2 現況成立僅因每類事實恰好單一來源供應（偶然滿足）；任何第二來源接入（如另一台股資料商），同一世界事實將立即出現兩個無法對齊的平行表徵，且無 P4.E5 衝突保存之落點。

**證據**：macro_vintage.py L13-14 docstring（親查屬實）：「現況誠實:尚無任何生產特徵消費總經(feature_values 零 macro 特徵)——本模組是『接線前先建好門』」；macro.py:52 _a("DEXTAUS", "新台幣對美元匯率")（親查屬實）；feature_values DDL 四欄 (panel_date, stock_id, feature, value) 純衍生訊號 schema（親查屬實）；fred_series 與 Taiwan* 表無任何 join 鍵或映射表；全庫無 identity_claim / entity_alias / xref 類表；principle_factor_map 之 feature 欄為裸 VARCHAR 特徵名，無 instance/type 標記。

**補正方向**：在補正 AUD-01 世界模型層時將兩來源同時納入：EconomicIndicator 作為世界實體（DEXTAUS＝「新台幣對美元匯率」這一世界量的表徵，而非 FRED 的一個 series_id）；macro 特徵接線時即以世界概念鍵入而非 series_id 直綁。Layer 3 規格中為每類實體（security、index、fred_series、thinker、work、dataset、model）宣告同一性判準（現況多數可一句寫定：「FinMind stock_id 字串相等且存續期間重疊」）；identity claim 建為一級表（identifier_a, identifier_b, criterion, evidence, confidence），建立「世界事實→來源 Observation」一對多映射，使未來多來源供應同一事實時有唯一權威表徵＋衝突保存（P4.E5）落點；Knowledge 表加 binding_kind（instance/type）標記或在規格中按表宣告。

### AUD-07【MAJOR】身份屬性無時間繫結：以「今日的」industry_category 判定全部歷史 panel 的宇宙准入，PIT 紀律及於觀測值、未及於身份屬性

* **憲章條款**：P3.E3（同一性判準與屬性繫結）、P4.E2（雙時間性）交界
* **位置**：src/augur/universe/core_gate.py:159-176；src/augur/core/generic_schema.py:256-273
* **發現視角**：P3 Identity Before Knowledge + F4 Knowledge Without Identity

**描述**：core_universe 的 ETF 排除與 conditional 產業豁免都 join 到 TaiwanStockInfo 的 industry_category，而該表為 upsert 原地覆蓋之現況快照（ON CONFLICT DO UPDATE、「API 最新值 wins」）——實體屬性（產業分類、股名）無 valid time、無歷史版本。結果：build_universe_asof 雖對「特徵完整度」做了 point-in-time 快照（親查其 docstring 明訂「只用 t 當時已知資訊」消 survivorship），但對「身份屬性」用的是今日狀態套用到歷史 panel：整併官親查 _select_core 之 ETF 排除子查詢（NOT EXISTS … si.industry_category IN %s）與 conditional 豁免子查詢（EXISTS … ci.industry_category IN %s）均無任何日期條件。若某股曾轉產業分類（如金控改組）、或 ETF 分類名變更，歷史宇宙判定會被今日屬性汙染，且不可重建「當時系統認為它是什麼」。這與系統自身把 PIT 奉為公理的立場（release_lag、macro_vintage、asof 快照）不一致。

**證據**：core_gate.py _select_core（親查屬實）：ETF 排除「AND NOT EXISTS (SELECT 1 FROM "TaiwanStockInfo" si WHERE si.stock_id = fv.stock_id AND si.industry_category IN %s)」與 conditional 豁免「EXISTS (SELECT 1 FROM "TaiwanStockInfo" ci WHERE ci.stock_id=fv.stock_id AND ci.industry_category IN %s)」——join 均無日期條件；generic_schema.py:261 註解「批次內同主鍵去重（保留最後一筆＝API 最新）」、DO UPDATE SET 全欄覆寫（親查屬實）；build_universe_asof docstring 之 PIT 宣稱僅及特徵完整度與流動性分位。

**補正方向**：對名冊類 snapshot 表加 transaction-time 留痕（最輕量：每日 sync 時將 TaiwanStockInfo 差異列 append 進 roster_history，或改用 SCD-2 式 valid_from/valid_to）；build_universe_asof 的產業判定改讀 as-of 當時之屬性版本。在 Layer 3 規格中明文：實體屬性（分類、名稱）屬 Identity 之時變屬性，其消費必須 as-of。

### AUD-08【MAJOR｜⚖️ 經解釋裁決 2026-001 定為 MAJOR，見 7.5 節】雙時間性僅覆蓋 FRED 一源：FinMind raw／feature_values 無 transaction time，prediction_values 更以 DELETE+INSERT 覆寫——已對人呈現之建議可被靜默重寫、過去認識狀態不可重建

* **憲章條款**：P4.E2（雙時間性）、P2.E2／F5（交叉 P4.E3）
* **位置**：scripts/predict_asof.py:145-151,196-198；scripts/migrate_prediction_ddl.py:46-60；src/augur/features/panel.py:40-47,169；src/augur/core/generic_schema.py（auto-schema 無 ingested_at）；src/augur/core/schema.py:41-50（data_audit_log）
* **發現視角**：P2 Representation Before Intelligence + F2 Model First + F5 Intelligence Without Evidence、P4 Evidence Before Conclusion

**描述**：P4.E2 要求任何 Observation 與 Knowledge 區分 valid time 與 transaction time，「任一過去時刻系統之認識狀態必須可追溯且可稽核」為不變式。實查三層皆缺：(a) FinMind raw 表由 auto-schema 建表、欄位逐字照 API，無 ingested_at/version 欄——只有 valid time；(b) feature_values 僅四欄無 computed_at，且 ON CONFLICT DO UPDATE 覆寫（panel.py:169 親查屬實）；(c) 最嚴重者為產品出單口：prediction_values 是 advisor PredictionPayload 組 picks 與風控 _deployed_dd_returns 算 DD 熔斷的權威承載表，但每次 predict() 對同 (panel_date, model_id) 先 DELETE 再 INSERT（親查 predict_asof.py:145-151 屬實），DDL 僅 panel_date/model_id/stock_id/score/rank/in_portfolio/weight——無 created_at、無 run 級 git_sha、無 superseded 標記（親查 DDL 屬實）；--rewrite-all 更明文提供「既有列 per (panel_date,model_id) DELETE+INSERT 冪等重寫」。這意味「系統在某時刻實際對人提出過什麼建議」不可事後重建：以不同 top_frac/weight/風控參數重跑即無痕取代舊建議，F5 之「為什麼當時建議 X」失去可追溯基礎，風控回讀的歷史投組成分亦會靜默改變。系統的「as-of 紀律」是強大的 valid-time PIT，回答「時刻 t 世界上什麼已公開」，而非憲章要求的「時刻 t 系統知道什麼」；data_audit_log 僅批次級（dataset/action/rows/logged_at，親查 DDL 屬實），可旁證「何時寫過」但無法重建「寫了什麼」。對照組：arena 結算表有 created_at 與 trigger、prediction_probability 有 created_at、fred_series 有 realtime_start——系統自身已有正確範式，唯獨主出單表與主衍生表缺席。

**證據**：predict_asof.py:145-151（親查屬實）：cur.execute("DELETE FROM prediction_values WHERE panel_date=%s AND model_id=%s", …) 後 executemany INSERT；migrate_prediction_ddl.py CREATE TABLE prediction_values 欄位清單無任何時間戳/版本欄（親查屬實）；--rewrite-all help 文字「既有列 per (panel_date,model_id) DELETE+INSERT 冪等重寫」（親查屬實）；feature_values DDL 四欄＋panel.py:169 ON CONFLICT DO UPDATE SET value=EXCLUDED.value（親查屬實）；data_audit_log DDL 僅 id/dataset/data_id/action/rows/logged_at/detail（親查屬實）。

**補正方向**：分級補正：(1) 最優先——prediction_values 改 append-only + serving 語意欄（run_id/created_at/git_sha + superseded_by 或 is_current 旗標，配 BEFORE DELETE trigger 禁物理刪除），重寫改為「新列插入＋舊列標 superseded」，至少先加 created_at 並將重寫事件同交易寫 data_audit_log，使任一過去時刻系統實際出過的建議可 as-of 重建；(2) 低成本並行——feature_values 加 computed_at TIMESTAMPTZ DEFAULT now()；(3) FinMind raw 之認識狀態變遷由 AUD-02 之 supersede 帳承載；(4) Layer 4 規格明文宣告哪些表為「可重算之衍生快照」（as-of 重建能力＝由凍結輸入重算）、哪些必須原生雙時間，把 P4.E2 尾句「機制與能力等級由 Layer 4 定義」落地為表級分類。

### AUD-09【MAJOR｜⚖️ 門檢曾升 critical（附覆核條件），經解釋裁決 2026-001 回 MAJOR，見 7.5 節】衍生 Knowledge 以 DELETE 全量重建：核心宇宙快照與 column_catalog 舊版無 superseded 標記即滅失

* **憲章條款**：P4.E3（只失效不刪除）
* **位置**：src/augur/universe/core_gate.py:196,213（DELETE FROM CORE_TABLE / ASOF_TABLE）；src/augur/catalog/__init__.py:312（DELETE FROM column_catalog）
* **發現視角**：P4 Evidence Before Conclusion

**描述**：P4.E3 規定 Knowledge 與 Evidence 不得刪除、僅得標記 superseded/retracted/invalidated。整併官親查三處 DELETE 重建屬實：core_gate.py build_universe 之 DELETE FROM {CORE_TABLE}（註解「commit 新快照（取代舊核心名單）」）、build_universe_asof 之 DELETE FROM {ASOF_TABLE}（註解「重建全 as-of 快照」）、catalog/__init__.py:312 之 DELETE FROM column_catalog WHERE dataset=%s（註解「重探即全換（#6）」）。核心宇宙成員資格與 catalog 欄級 provenance（含 last_verified）均為 Knowledge 級斷言；全量刪除使「系統上一版相信哪些股票屬核心宇宙」「catalog 上一版怎麼描述此欄」不可考。緩解因素：core_universe_build_meta append 保留每次 build 參數（但不存成員名單本身），理論上可由 raw 重算舊快照——但 raw 本身會被 heal 覆寫（AUD-02），重算保證因此不完整；列 major 而非 critical 係因內容原則上為確定性衍生物、非原始證據滅失。

**證據**：core_gate.py（親查屬實）：「cur.execute(f"DELETE FROM {CORE_TABLE}")          # commit 新快照（取代舊核心名單）」與「cur.execute(f"DELETE FROM {ASOF_TABLE}")          # 重建全 as-of 快照」；catalog/__init__.py:312（親查屬實）：「cur.execute("DELETE FROM column_catalog WHERE dataset=%s", (dataset,))   # 重探即全換（#6）」；build_meta 僅存參數列（panel 範圍/閾值/特徵清單/核心數）。

**補正方向**：以版本化取代刪除：加 build_id（FK 至 build_meta）入快照表 PK，新 build append 新版本、舊版本標 superseded_by_build；或最低限度在 DELETE 前將舊快照聚合簽章（列數＋內容 hash）落 build_meta，使「舊認識狀態存在過且長什麼樣」可稽核。column_catalog 同理：重探時 UPDATE＋歷史表，或 DELETE 前留 snapshot。

### AUD-10【MAJOR】自動行動之 P5.E1 六元組欄位缺失：留痕表無 Actor Identity 與 Authorization 欄，授權鏈僅存在於 shell 註解

* **憲章條款**：P5.E1（Action 六元組）、§8.3（Action 之 Identity 歸因必須可機器稽核）、F6
* **位置**：src/augur/core/schema.py:30-50（pipeline_execution_log、data_audit_log DDL）；audit_selfheal.sh:23-28；install_services.sh
* **發現視角**：P5 Accountability Before Action + F6 Unaccountable Action + F3 Agent First

**描述**：系統的自動行動鏈（systemd timer → audit_watchdog → audit_selfheal → daily_maintenance --heal → FinMind API 放量重抓）可造成 Reality 變更（對外 API 請求消耗帳號額度、可觸發 403/IP ban；殺進程與 relaunch 改變系統運行狀態，依 §2.1 自反性條款屬 Reality）。此鏈的人類授權確實存在，但只以 shell 註解形式記載（「hugo 2026-07-14 拍板實驗值 #27」「hugo 07-14 拍板 (a)+(b)」——整併官親查 audit_selfheal.sh:23-28 屬實），非機器可查詢的授權記錄；且 DB 留痕表 schema 完全沒有 actor/authorization/expected_effect 欄位——整併官親查 DDL：pipeline_execution_log 僅 (id, task, target, status, rows, started_at, ended_at, detail)、data_audit_log 僅 (id, dataset, data_id, action, rows, logged_at, detail)——任何一列寫入紀錄無法機器回答「誰發起、憑什麼授權」。attestation_result 的 driver 欄（VARCHAR）是唯一的 actor 雛形，但只覆蓋對帳 verdict、不覆蓋 heal 重抓與 sync 寫入本身。P5.E1 六元組（Actor Identity、Authorization、Knowledge Basis、Timestamp、Expected Effect、Observed Effect）現況僅 Timestamp 與部分 Observed Effect 結構化。

**證據**：schema.py DDL 整併官親查屬實（兩表欄位清單如上，無任何 Identity/Authorization 欄）；audit_selfheal.sh:23-24 親查屬實：「FINMIND_MIN_INTERVAL=0.7(hugo 2026-07-14 拍板實驗值 #27;>0.9 已驗證值、IP 剛 sustained ban 後屬激進——放量後緊盯,撞 403 即退回 0.9…)」——授權之唯一載體為註解；attestation_result.driver VARCHAR(64)（親查屬實）。

**補正方向**：為自動行動建立機讀授權登錄：(1) Layer 6 落地前先增設 authorization 登錄表（authorization_id、授權人已解析 Identity、授權範圍/參數邊界、生效日、依據文件），把現存註解中的 hugo 拍板逐筆遷入；(2) pipeline_execution_log/data_audit_log 增列 actor_identity 與 authorization_ref 欄（selfheal/watchdog/daily_maintenance 各鑄造 Agent Identity）；(3) 放量 API 行動於啟動時寫入 expected_effect（窗、interval、預估請求量），完成時連結 observed_effect（attestation_result id）。此為欄位擴充，與既有「只擴不縮」schema 紀律相容。

### AUD-11【MAJOR】watchdog/selfheal 的行動記錄與決策依據繫於家目錄可變純文字檔：殺進程/relaunch 無 DB 留痕，log 檔缺失即無條件觸發 relaunch

* **憲章條款**：P5.E1（Observed Effect 連結 Feedback）、P4.E3/P4.E6（append-only、provenance）延伸至行動記錄、F6
* **位置**：audit_selfheal.sh:9,33-37（LOG=$HOME/audit_retry.log；殺進程僅寫此檔）；audit_watchdog.sh:11-41
* **發現視角**：P5 Accountability Before Action + F6 Unaccountable Action + F3 Agent First

**描述**：看門狗的兩類自動行動——kill/kill -9 殺進程（audit_selfheal.sh 內迴圈，親查屬實）與 setsid relaunch（audit_watchdog.sh:39，親查屬實）——只留痕於 ~/audit_retry.log 與 ~/audit_watchdog.log 兩個可覆寫、可遺失、不隨 repo/DB 遷移的純文字檔，DB 中無對應行動記錄。更關鍵的是 watchdog 的決策 Knowledge Basis 本身就是同一可變檔：audit_watchdog.sh:17 以 grep 該檔最後一條 attestation 行判態（整併官親查：last_att=$(grep -E 'attestation：' "$LOG" 2>/dev/null | tail -1)）、:29 以該檔 mtime 判停滯，且檔案不存在時 `stat … || echo 0` 使 logage 變成 epoch 秒數→必然 >2700 直接走 relaunch 分支（親查屬實）——log 檔被清空或搬家即觸發無條件重啟，行動依據不可稽核亦不可重建。相較之下系統對「資料」的留痕（data_audit_log 與資料同交易）遠嚴於對「行動」的留痕，形成不對稱。

**證據**：audit_watchdog.sh:29 整併官親查逐字屬實：logage=$(( $(date +%s) - $(stat -c %Y "$LOG" 2>/dev/null || echo 0) ))；:17 last_att grep 為終態判定唯一依據（親查屬實）；audit_selfheal.sh 殺進程段（親查屬實）：echo "…看門狗:log 靜默 ${age}s>45min=卡死 → 殺進程記中斷" >> "$LOG" 後 kill "$py"; sleep 5; kill -9 "$py"——無 DB 留痕；audit_watchdog.sh:39 setsid nohup flock … relaunch（親查屬實）。

**補正方向**：(1) 將 watchdog 的終態判定來源從 grep log 檔改為讀 attestation_result 表（該表本就是為「run 與 gate 檢查解耦」設計的正典留檔，schema.py 註解親查屬實）——判態依據即刻變為 append-only 可稽核；(2) watchdog/selfheal 的 kill、relaunch、探測結果等行動事件同步 INSERT 至 pipeline_execution_log（或新設 automation_action_log），文字 log 降級為人讀便利品；(3) log 檔缺失時 fail-loud 記異常而非默認走 relaunch。

### AUD-12【MAJOR】兩套「憲章」撞名且無 Layer 登錄：大憲章自稱最高承載文件、README 逕稱「憲法」，與 Layer 0 形成雙重最高權威歧義

* **憲章條款**：§0.5（Layer 對照表：每份規格恰屬一層、先登錄方生效力）、§0.6 Lex superior、§8.3
* **位置**：docs/系統架構大憲章_v1.45.0.md L3（「性質」段）；README.md L24；HANDOFF.md §4.7
* **發現視角**：治權整合（文件級審計）

**描述**：既有治權體系是一條自足的位階鏈（靈魂＞原則精華＞大憲章＞CLAUDE.md＞README），大憲章自我定位為「Augur 架構治理之最高承載文件」且 README/HANDOFF 逕稱「憲法」。MC v1.2 生效後，依 §0.5-0.6 全部五檔皆屬 Layer 1–7 之規格、受 Layer 0 約束，但無一檔登錄所屬 Layer、無一處聲明從屬關係——整併官親自重跑 grep -ril "meta-constitution|AUGUR-MC|元憲章" 全 repo（.md/.py）：零命中。「憲章/憲法」名稱與 Layer 0「Supreme Design Constitution」撞名，會使後續工程師無從判斷牴觸時何者為準；且原則精華自稱「20 條＝不可違反法律、違反任一條＝治權違規」，其中 #7 已證與 P4 核心條款牴觸（AUD-02），依 lex superior 牴觸部分無效——此後果現無任何文件承認。

**證據**：大憲章 L3 整併官親查逐字屬實：「**性質**：Augur 架構治理之最高承載文件（位階次於靈魂與原則精華）」；README L24 親查屬實：「docs/系統架構大憲章_v1.45.0.md | **憲法**：三個敵人 × 管線…」；grep 全 repo Meta-Constitution/AUGUR-MC/元憲章 零命中（親自執行確認）。

**補正方向**：(1) 在 §0.5 Layer 對照表登錄五檔（建議：系統核心思想→Layer 1 World Model 規格之領域前身；原則精華→跨層 domain profile 逐條標注所屬 Layer；大憲章→Layer 4–7 架構/維運規格；CLAUDE.md→Layer 6 Agent Runtime 協作規格；datasets_zh.md/finmind-references→Layer 7）；(2) 大憲章更名或加副標（如「Augur Domain Architecture Charter — Layer 4–7 Specification」），「性質」段改為「受 AUGUR-MC v1.2 約束之最高**領域**承載文件」；(3) 各檔檔頭加從屬聲明與 `AUGUR-MC v1.2 §{條款}` 引用格式（§8.6）。

### AUD-13【MAJOR】全部既存規格缺 §8.3 Constitutional Compliance Statement——依條文「無此聲明之規格不生效力」，僅賴過渡規則推定有效

* **憲章條款**：§8.3（合規聲明義務）、§8.3 可判定性元規則
* **位置**：docs/系統核心思想_v1.8.0.md、docs/原則精華_v1.9.0.md、docs/系統架構大憲章_v1.45.0.md、CLAUDE.md、README.md（五檔皆缺）；reports/（全部計畫書）
* **發現視角**：治權整合（文件級審計）

**描述**：程式碼庫寫於 MC 誕生前（MC 生效日 2026-07-16＝今日），五份治權檔與全部 reports/ 計畫書均無合規聲明：無聲明合規之憲章版本、無逐原則（P1–P5）合規論證、無已知緊張關係之揭露。依 §8.3 過渡規則 (b) 既存規格享 Steward 裁定之補正期、期內推定有效，故非立即失效；但補正所需三項內容目前零基礎，且本次審計已查得至少四項應揭露之緊張關係：① raw 層無 transaction time／#7 覆寫（對 P4.E2/E3/E5，＝AUD-02）；② 「PostgreSQL＝唯一真相來源」措辭（對 P2.E4，＝AUD-26）；③ RBAC deny 與「庫中確無」位元級不可區分之呈現（內部表徵正確、對外斷言與系統真實認識狀態不一致，屬 P1.E3 合規優先可辯護但須揭露）；④ 無 Layer 1/2 規格（對 §0.5，＝AUD-01）。另 §8.3 可判定性元規則：治權檔評價性謂詞多已有可判定判準（優勢），但「系統完美後」「30 分鐘可讀」等仍無判準。

**證據**：grep 全 repo（*.md/*.py）"Meta-Constitution|AUGUR-MC|Constitutional Compliance" 零命中（整併官親自執行確認）；四項緊張關係分別經 AUD-01/AUD-02/AUD-26 之獨立程式碼與文件親查支持。

**補正方向**：(1) 請 Steward 依過渡規則 (a) 發布暫行模板並裁定補正期；(2) 為五治權檔各補一節 Compliance Statement：聲明 AUGUR-MC v1.2、逐 P1–P5 論證（可大量引用既有三敵×二十條框架——映射基礎極佳）、揭露上列四項緊張關係與補正期程；(3) 新計畫書（plan-first 產物）自此一律內含聲明——可直接併入既有「計畫完整性 v1.39.0」條款成為必附項。

### AUD-14【MINOR｜✏️ 驗證後證據修正：「除權息世界事件無表徵」子宣稱被推翻，見第七節】同一世界現實的多個表級表徵（原始價 vs 還原價）無同一性宣告，除權息世界事件無表徵、擇用知識散落於各消費模組註解

* **憲章條款**：P1.E2（每一世界事實有唯一權威表徵）、P1.Y（資料結構不是世界結構）
* **位置**：src/augur/features/panel.py:5-9；src/augur/features/valuation.py；docs/原則精華_v1.9.0.md #7（restatement 豁免段）
* **發現視角**：P1 Reality First + F1 Data First Architecture

**描述**：TaiwanStockPrice（原始價，含 28 萬列停牌 close=0 哨兵）與 TaiwanStockPriceAdj（還原價，隨未來除權息回溯重算）是同一批市場成交事件的兩種 vendor 轉換，系統中並存為兩張無關聯的表。「哪張表對應哪個世界語意、何時該用哪張」的知識以 docstring 形式分散存在於各消費模組（panel.py 用 Adj 並解釋原因，親查屬實；valuation f5 特意用原始價防洩漏），無中央宣告。更根本地：除權息這一世界事件本身在系統中無表徵——它只隱含於 vendor 還原因子的回溯重算行為中，reconcile 將其列為 restatement 豁免來吸收。這是資料表結構隱性承載世界知識的典型成本：世界事件（配息）→只能從資料異動（歷史列改寫）反推。

**證據**：panel.py L5-9 親查屬實：「價量特徵一律用**還原價** TaiwanStockPriceAdj……(a) 除權息跳空非真報酬，原始價會污染動能/區間位置；(b) 該表**無停牌 close=0 哨兵列**（raw 有 28 萬列）」——同一世界現實的兩種表徵、擇用理由住在註解；原則精華 #7 之 restatement 豁免段：世界事件僅以資料異動豁免形式存在。

**補正方向**：在世界模型層（AUD-01）宣告：MarketTrade/DailyBar（世界事實）、CorporateAction（世界事件，含除權息）為一級概念，TaiwanStockPrice 與 TaiwanStockPriceAdj 為同一事實的兩個 Observation 通道（後者為含 CorporateAction 調整的衍生觀測）。將「還原 vs 原始」的擇用規則從各模組註解上收為世界模型層的單一宣告，消費端引用概念而非表名。

### AUD-15【MINOR】新來源吸收機制為 F1 方向之負向棘輪：零重構落地＝零本體整合，catalog 只答「怎麼抓」不答「這是世界中的什麼」

* **憲章條款**：P1.E1、F1（審計問題四：資料來源新增時是否需重構世界觀）
* **位置**：src/augur/catalog/__init__.py:1-17；src/augur/core/generic_schema.py:18（「任意 API dataset 都能落地、無白名單（#3）」）
* **發現視角**：P1 Reality First + F1 Data First Architecture

**描述**：「新增資料來源是否需重構世界觀」的答案是：不需要——但原因是沒有世界觀可重構。generic_schema 讓任何新 API dataset 零重構落地（工程上優秀），落地即成為又一個 source-shaped 孤島；catalog 記錄的元資料全部是擷取語意（tier/intraday/data_id 來源/最早日期/最優抓取模式/排除），無一欄回答該 dataset 對應世界中的什麼實體/事件/狀態。機制越順手，來源孤島累積越快，距共同世界模型越遠——這是結構性的，不會隨資料量增長自行收斂。此項單獨列出是因為它決定補正的急迫性排序：世界模型層晚建一天，需回頭映射的孤島就多一批。

**證據**：catalog/__init__.py docstring：「對每個 FinMind/FRED dataset 做 API 探測，取得『怎麼抓』的元資料……作後續所有 API 抓取的單一驅動依據」——通篇為 fetch 元資料；dataset_catalog/column_catalog 無任何本體/世界概念欄位；generic_schema.py:18 親查逐字屬實：「任意 API dataset 都能落地、無白名單（#3）」。

**補正方向**：短期低成本補正：在 dataset_catalog/column_catalog 增列世界概念欄（entity_type/world_concept/maps_to），新 dataset 落地時強制登錄其世界映射（可先人工策展，如 datasets_zh.md 既有模式），使「落地」與「本體整合」綁定為同一動作——把負向棘輪反轉為正向：每新增一來源即豐富而非稀釋世界模型。

### AUD-16【MINOR】審議通道之 P2.E1 標準鏈缺兩節點：claim 指涉對象為自由文字 anchor（無 Identity 繫結）、verdict 無 Confidence 欄

* **憲章條款**：P2.E1、P3.E1（Knowledge 必須引用已解析之 Identity）、§2.1 自反性條款（交叉 P4.E1、P4.E8）
* **位置**：scripts/migrate_deliberation_ddl.py:46-77（deliberation_claim/deliberation_verdict DDL）；src/augur/deliberation/verifiers.py:168-197；src/augur/deliberation/consensus.py:22；src/augur/deliberation/redlines.py
* **發現視角**：P2 Representation Before Intelligence + F2 Model First + F5 Intelligence Without Evidence、P3 Identity Before Knowledge + F4 Knowledge Without Identity

**描述**：審議通道實作為：LLM claim（候選斷言）→ anchor（字串指涉）→ oracle verdict（Evidence，附 evidence 文字與 is_deterministic）→ status='confirmed'。對照 P2.E1 標準鏈 Observation→Representation→Identity→Evidence→Knowledge，缺兩節點：(a) claim 指涉之對象（表、欄、檔案、規則）以裸字串 anchor 表達（親查 DDL：anchor text NOT NULL CHECK (btrim(anchor) <> '')，無 FK、無結構化 target 欄），未繫結任何系統鑄造之 identifier——同一張表在不同 claim 中僅靠 anchor 字串正規化（strip+lower）對齊；憲章自反性條款下 Augur 自身構件（表、模組、gate）也是 Reality 實體，被指涉之表若改名，歷史 confirmed claim（系統背書之 Knowledge）之指涉即斷鏈不可追。(b) confirmed 為二值終態，無 Confidence 附掛（P4.E1 五元組第五欄缺席，併入 AUD-03 統一語義補正），亦無語義區分「information_schema 存在性證明」與「file_grep 單行匹配」兩種強度迥異的證據。通道骨架（候選斷言、機械裁決、fail-closed 升級、verdict 之 evidence 非空 CHECK）完全正確；現行部分緩解：anchors.py 之 schema grounding 將表名 ground 到 information_schema（執行期解析防臆造），但解析結果未回寫成結構化繫結。

**證據**：migrate_deliberation_ddl.py 整併官親查屬實：deliberation_claim 欄位為 session_id/perspective/category/claim_text/anchor/assigned_verifier/status/provenance/created_at，無 identity/referent FK 欄；deliberation_verdict 欄位 verifier/verdict/evidence/is_deterministic/ran_at，無 confidence 欄；consensus.py:22 去重鍵僅 (assigned_verifier, anchor.strip().lower()) 字串正規化；provenance jsonb 記 model/lens/fast_path 但無 resolved identity。

**補正方向**：為 claim 增設結構化指涉欄（target_kind: table/column/file/doctrine + target_ref，可先以 dataset_catalog/information_schema 之表級 identifier 為錨，AUD-04 之 entity registry 就緒後遷移 FK 繫結）；schema grounding 的解析結果落庫；verdict 增 confidence 語義欄（機械 oracle 可先定義為封閉集之證據強度分級，接軌 AUD-03 之統一映射），使 confirmed claim 升格為報告/蒸餾消費時符合 Knowledge 五元組。低優先——現行 anchor 契約＋grounding 已擋住最危險的臆造指涉。

### AUD-17【MINOR】「confirmed 唯一寫點」為應用層紀律：DB 層無 trigger 阻止旁路寫入無證據的 confirmed claim

* **憲章條款**：P2.E2（交叉 §8.3 核心不變式可機器稽核）
* **位置**：src/augur/deliberation/verifiers.py:182,195；scripts/migrate_deliberation_ddl.py:59-60
* **發現視角**：P2 Representation Before Intelligence + F2 Model First + F5 Intelligence Without Evidence

**描述**：verify_claim 為唯一 confirmed 寫點是靠程式碼慣例維持——整併官親自重跑 grep 'SET status' 全庫：deliberation_claim 寫點確僅 verifiers.py:182（escalated）與 :195（動態 status）兩處，現況屬實。但 DDL 對 status 只有值域 CHECK 五值枚舉，沒有 trigger 要求「status→confirmed 時必須已存在對應之 is_deterministic verdict 列」。任何持 DB 權限之 script/人可直接 UPDATE 造出無證據的 confirmed claim，且下游 bridge_deliberation_distill 雖有 EXISTS deterministic verdict 過濾、但報告面（ledger.report）與 consensus 聚合並無此防線。對照系統自身範式：direction_gate 有 no-goalpost trigger、knowledge 有 item_source_gate BEFORE INSERT trigger——同等關鍵的裁決不變式在 deliberation_claim 上未 DB 化。

**證據**：migrate_deliberation_ddl.py 親查屬實：status CHECK (status IN ('pending','confirmed','refuted','undecidable','escalated')) 僅值域約束；grep 'SET status' 全庫命中清單親查：deliberation_claim 之 UPDATE 僅 verifiers.py:182/195（其餘為 deliberation_task/session/run 與 arena/gate 等他表）；migrate_direction_gate_ddl.py 已示範 trigger 級不變式強制。

**補正方向**：加 BEFORE UPDATE trigger：NEW.status IN ('confirmed','refuted') 時斷言 EXISTS (SELECT 1 FROM deliberation_verdict WHERE claim_id=NEW.claim_id AND verdict=NEW.status AND is_deterministic)，否則 RAISE——把「LLM 輸出唯經確定性證據才成結論」從 code 紀律升為機器稽核之不變式，並補 --selftest 實測 trigger（鏡射 unfreeze_gate 既有做法）。

### AUD-18【MINOR】個股建議無 per-pick 解釋面：F5 之「為什麼」僅能答到模型/方法層，答不到「為什麼是這一檔」

* **憲章條款**：F5（交叉 P4.E6）
* **位置**：src/augur/models/ranker.py:8（docstring）；src/augur/advisor/payload.py:14-21；scripts/migrate_prediction_ddl.py:47-60
* **發現視角**：P2 Representation Before Intelligence + F2 Model First + F5 Intelligence Without Evidence

**描述**：系統對「為什麼建議 2330」的可追溯答覆鏈為：score→model_id→model_registry（feats_hash/git_sha/train_span/metrics）→artifact（凍結特徵集）→revalidation_ledger/trial_ledger——方法層溯源完整。但 per-pick 層級：StockPick 只帶 symbol/rank/score/source_ref/name（親查屬實），prediction_values 只存 score/rank/in_portfolio/weight（親查 DDL 屬實），ranker.py:8 明訂「SHAP/可解釋明訂不在此層(留 audit,防膨脹侵入預測 SSOT)」（親查逐字屬實），而 audit 層的 feature_diagnostics 五鏡是特徵治理用、非出單時之解釋。用戶問顧問「為什麼選這檔」時，LLM 受 guard 約束不能編理由（正確），但系統也沒有任何真實依據可供它轉述——個股級「為什麼」的誠實答案只剩「模型分數高」。對主力 RankRidge（線性模型）而言，係數×標準化特徵值之貢獻分解是零推論成本的確定性計算，此缺口是未操作化而非不可行。

**證據**：ranker.py:8 親查逐字屬實：「SHAP/可解釋明訂不在此層(留 audit,防膨脹侵入預測 SSOT)」；payload.py StockPick dataclass 欄位僅 symbol/rank/score/source_ref/name（親查屬實）；prediction_values DDL 無任何 attribution 欄（親查屬實）；advise.py _render_picks_table 輸出僅 rank/symbol/name/score/機率附欄。

**補正方向**：出單時對 in_portfolio 股計算確定性 feature contribution（RankRidge＝係數×標準化特徵值 top-k），落獨立表（如 prediction_attribution，同受隔離不變式保護）並選擇性注入 payload 供顧問確定性排版（不經 LLM）；GBDT 挑戰者提拔前將 per-prediction SHAP 之 serving 化列入提拔驗收，使每筆 recommendation 能機械回答「為什麼是它」。

### AUD-19【MINOR】通識白名單放行路之 LLM 內容無機械強制的「非出自語料/AI 生成」正面標記——teacher prompt 已認定該標記為正確行為，serve 時卻依賴 LLM 自律

* **憲章條款**：P2.E2（交叉 P4.E7 synthetic 標記）
* **位置**：src/augur/advisor/advise.py:195-211；src/augur/advisor/safe_general.py；src/augur/advisor/oai_compat.py:68-74；scripts/advisor_distill_teacher.py:35
* **發現視角**：P2 Representation Before Intelligence + F2 Model First + F5 Intelligence Without Evidence

**描述**：當檢索空且題目過 general_safe_answerable 三閘白名單時，LLM 以 empty_payload（數字/引文白名單=∅）作答並過 guard_knowledge+guard_attribution 後直接出檔（親查 advise.py 放行路屬實，guard 不過即 fail-closed 回 NO_KNOWLEDGE_RESPONSE——骨架正確）。guard 是負面閘（擋編造數字/引文/出處），但對「這段內容是 LLM 通用常識、非出自 augur 語料庫」沒有任何機械強制的正面標示——機械尾註 [augur-guard] 只揭露 pass/issues/citations 計數（親查 oai_compat.py _verdict_note 屬實），一般用戶無從解讀 citations=0 的含義。對照：蒸餾 teacher prompt 鐵律已明文要求 gold 示範「標註『以下為通用常識、非出自 augur 語料』」（親查 advisor_distill_teacher.py:35 屬實），即系統已認定此標記是正確行為，但 serve 時它依賴 LLM 自律而非機械前置。P2.E4/P4.E7 之精神：AI 生成內容之來源屬性標記不應依賴生成者自己記得標。

**證據**：advise.py:199-208 親查屬實：lvl==1 且 whitelist_route 時 gen_resp=llm_fn(gen_prompt)，guard 通過即 return {'response': gen_resp,…}，無任何 disclaimer 前置；oai_compat.py:68-74 尾註僅統計行（親查屬實）；advisor_distill_teacher.py:35 親查逐字屬實：「可給一句標註『以下為通用常識、非出自 augur 語料』的簡短說明」；grep '通用常識' 於 src/augur/advisor/prompt.py 僅 Mode B 附檔規則一處，主路徑 build_prompt 無此指示。

**補正方向**：白名單放行路比照固定誠實句模式，由 advise() 機械前置固定標頭（如「以下為通用常識、非出自 augur 語料庫：」）於 LLM 回覆之前（與 _render_picks_table 前置手法一致、零 LLM 參與），並加入 advisor 回歸金題集固化為測試判準。

### AUD-20【MINOR】identifier 與 Evidence 可被物理消滅：ON DELETE CASCADE 遍布自鑄 identifier 之下游，誤配知識之 chunk/embedding 以硬 DELETE 級聯清除、無 tombstone

* **憲章條款**：P3.E2（identifier 一經鑄造永不刪除、更正全程留痕）、P4.E3（只失效不刪除；物理刪除限法規強制抹除且須 tombstone）
* **位置**：src/augur/philosophy/framework.py:34,41,49,57,80,89-90；scripts/migrate_deliberation_ddl.py:49,69,82,188；scripts/audit_work_attribution.py:106-113
* **發現視角**：P3 Identity Before Knowledge + F4 Knowledge Without Identity、P4 Evidence Before Conclusion

**描述**：系統自鑄的 serial identifier（school_id、principle_id、claim_id、work_id 之下游）以 ON DELETE CASCADE 掛接——整併官親查命中 11 處：刪 philosophy_school 會級聯滅掉 principle/factor_map/source/tag，刪 deliberation_session 會級聯滅掉 claim/verdict/escalation——identifier 與其繫結之 Knowledge 在 DDL 層面可一鍵消失，違反「mint 永不刪除」不變式。實際運作已有先例：audit_work_attribution --fix 對誤配作品級聯硬 DELETE philosophy_chunk_embedding 與 philosophy_chunk（親查 :109-113 兩條 DELETE 屬實，docstring 自述「寧殺勿留」）。「作品繫錯作者」正是一個 identity claim 錯誤，憲章要求其更正本身成為引用 Evidence 之 Knowledge 並保留 lineage；被刪的 chunk 是 Evidence 級物件（逐字語料、供 citation 溯源），刪除使「曾有多少污染內容、污染長什麼樣」不可稽核，且 --fix 一跑即不可逆。緩解：work 本體保留並標 review_flag=true＋note（work 級 tombstone 存在，親查屬實）、刪除動機是防污染語料進入檢索（服務 P1 忠實性）、內容可自源檔重抽；gate/來源治理處已有正確範式（superseded 非 DELETE、review_log 留痕）——缺口是局部而非全面。

**證據**：整併官親查：framework.py:34,41,49,57,80,89,90 與 migrate_deliberation_ddl.py:49,69,82,188 共 11 處 ON DELETE CASCADE；audit_work_attribution.py:109-113 親查屬實：DELETE FROM philosophy_chunk_embedding e USING philosophy_chunk c WHERE …work_id = ANY(%s) ＋ DELETE FROM philosophy_chunk WHERE work_id = ANY(%s)；:106-108 work 級僅 UPDATE review_flag 留痕。

**補正方向**：將 ON DELETE CASCADE 改為 ON DELETE RESTRICT（或移除 FK 級聯），刪除語意改為 status 標記（quarantined/retracted）；檢索隔離改用標記：chunk 加 invalidated BOOLEAN（或沿用 work.review_flag 於檢索 SQL JOIN 過濾——retrieval.py 已有 CLEAN 准入述詞可掛），使污染內容留存但機制性不可檢索；誤配更正落 attribution_correction 事件表（work_id、舊繫結、新裁定、evidence、actor）；若堅持物理刪（儲存/授權考量），刪前落 tombstone 帳（work_id/chunk 數/內容 hash/deleted_at/reason）。與 knowledge_source_review_log 既有範式對齊即可，工程量低。

### AUD-21【MINOR｜⬆️ 驗證後升級：MAJOR，見第七節】philosophy 假說與方向欄位 in-place UPDATE：修訂無 supersede 歷史，何時改、從什麼改來、憑什麼改均不可考

* **憲章條款**：P4.E3、P4.E4
* **位置**：src/augur/philosophy/framework.py:291,302
* **發現視角**：P4 Evidence Before Conclusion

**描述**：framework.py seed 對齊路徑對既有列執行 UPDATE philosophy_principle SET hypothesis=%s WHERE principle_id=%s 與 UPDATE principle_factor_map SET direction=%s WHERE map_id=%s（整併官親查兩條裸 UPDATE 屬實）——投資哲學假說文字與文獻預期方向（皆為 Knowledge 級斷言）被原地覆寫，前值不留痕。P4.E4 要求 Knowledge 可被推翻，此處確實可改（符合可謬性），但 P4.E3 要求推翻是「需要 Evidence 之知識行為、全歷史保留」。此為 seed 對齊路徑、頻率低、且大師假說本體另有文獻 source 錨定，故列 minor。

**證據**：framework.py:291 與 :302 之裸 UPDATE 親查屬實，無伴隨歷史表寫入或 note 欄記錄前值；對照 knowledge/curation.py 同類狀態轉移均 append review_log，證明 repo 內已有正確模式可套用。

**補正方向**：比照 curation.py 的 review_log 模式：假說/方向變更時 append 一列變更帳（map_id/old/new/reason/changed_at/actor），或直接改為「寫新列＋舊列標 superseded」。成本極低，模式已存在於同 repo。

### AUD-22【MINOR】chat session 硬刪除無留痕，且非法規強制抹除路徑

* **憲章條款**：P4.E3
* **位置**：src/augur/advisor/chat_history.py:86
* **發現視角**：P4 Evidence Before Conclusion

**描述**：delete_session 執行 DELETE FROM chat_session WHERE session_id=%s AND user_id=%s（整併官親查屬實），無 tombstone、無抹除事件 provenance。chat 訊息是對「用戶與系統互動」這一 Reality 的 Observation（且 advisor 回答含系統背書內容，事後追查誤導性回答時需要它）。P4.E3 唯一允許的內容移除是法規強制抹除，且抹除事件自身必須留痕；此處是一般功能性刪除。緩解：owner 收窄（AND user_id=%s）防 IDOR 做得對、chat 表已被隔離於預測管線與知識庫之外（不是任何 Knowledge 的 Evidence 上游），影響面小。若此刪除是為滿足用戶隱私權（準法規事由），則缺的只是留痕。

**證據**：chat_history.py:86 親查逐字屬實：cur.execute("DELETE FROM chat_session WHERE session_id=%s AND user_id=%s", (session_id, user_id))；無對應之 deletion log 表。

**補正方向**：刪除改兩段式：內容置 NULL/去識別化＋session 列標 deleted_at/deleted_by（tombstone 存續），或另落 chat_deletion_log（session_id/user_id/deleted_at/reason）；並於 Layer 4 規格明文此刪除之事由分類（用戶隱私＝準用法規抹除例外）。

### AUD-23【MINOR】P5.E2 行動風險分級表缺位：分級散落為事實慣例、無單一權威家，放量 API 行動僅憑註解中的常設授權

* **憲章條款**：P5.E2（風險分級 DEFER 與缺位預設規則）、P5.W3
* **位置**：全庫（無任何風險分級表/文件）；audit_selfheal.sh:22-28；scripts/daily_maintenance.py
* **發現視角**：P5 Accountability Before Action + F6 Unaccountable Action + F3 Agent First

**描述**：全庫不存在 P5.E2 意義下的風險分級表（各級 Evidence 完備性要求、Confidence 門檻、核准流程之單一對照）。現況有豐富但散落的事實分級：exit code 三態（0/2/3）劃分自動重試權限、EX 紅旗禁自動處置（watchdog 對 attestation FAIL 明文「終態——不 relaunch,待根因」，親查屬實——此為正確範式）、migrate --apply 須 pg_dump 快照、破壞性操作須 --force、approve 須 TTY——但這些是各自為政的慣例，無「一個權威家」可讓新增自動化行動對號入座。系統無實體世界 Action，故缺位預設規則未被實質違反；但 selfheal 的放量 API 重抓（FINMIND_MIN_INTERVAL=0.7 激進實驗值，會實際影響外部帳號額度與 IP 信譽）由 watchdog 自動 relaunch 反覆發起，僅憑一次性常設授權（且只在註解中），「放量後緊盯」之義務主體與退場判準（撞 403 即退回 0.9）無機械化。

**證據**：audit_selfheal.sh:23-24 親查屬實：「FINMIND_MIN_INTERVAL=0.7(hugo 2026-07-14 拍板實驗值 #27;>0.9 已驗證值、IP 剛 sustained ban 後屬激進——放量後緊盯,撞 403 即退回 0.9…)」；audit_watchdog.sh FAIL 分支「終態——不 relaunch,待根因」親查屬實；grep 全庫無 risk tier/風險分級對照表（risk_policy 表僅為投組風控閾值，非行動風險分級）。

**補正方向**：建立行動風險分級表（可為 DB 表或治權文件一節，作為 Layer 6 風險分級之前身）：列舉系統全部行動類型（API 放量重抓、殺進程、relaunch、DDL migrate、DB 還原 --force、gate approve、服務安裝），各配風險級、允許之自動化程度（自動/常設授權/逐案人核）、授權形式與留痕要求。將既有 exit code 三態與 EX 紅旗慣例正式掛入此表，並補記現行放量授權為暫行分級；退場判準（撞 403 退回 0.9）機械化為程式內建而非人工緊盯。

### AUD-24【MINOR】admin console env 後門之行動歸責繫於共享環境憑證，非已解析 Identity

* **憲章條款**：P5.W1（任何 Action 必須可歸責於單一 Identity）、P5.E1（Actor Identity）
* **位置**：scripts/serve_admin_console.py:8-13（登入兩路說明）
* **發現視角**：P5 Accountability Before Action + F6 Unaccountable Action + F3 Agent First

**描述**：admin console 可觸發具外部效果之行動（主題自動抓 acquire_topic 對外部網站發出抓取請求）。登入路徑 (1) 為 env 帳密後門（親查 docstring 屬實）：「帳號留空、或帳號等於 AUGUR_ADMIN_USER → 比對 AUGUR_ADMIN_PASSWORD（支援 .env 明文…臨時 superuser、記憶體 session）」——經此路徑發起的行動歸責到一個共享環境變數憑證，而非 app_user 中已解析之個人 Identity。在單人系統（superuser hugo）現況下實害有限，且有審計 log、綁 127.0.0.1 僅本機、路徑圍欄與 pbkdf2 240k 正規路徑並存（安全工程本身紮實）；但一旦多使用者化（RBAC 已建），此後門使 P5.W1 的單一 Identity 歸責無法區分實際操作者。

**證據**：serve_admin_console.py docstring 親查逐字屬實：「(1) env 帳密後門——帳號留空、或帳號等於 `AUGUR_ADMIN_USER` → 比對 `AUGUR_ADMIN_PASSWORD`(**支援 .env 明文**…臨時 superuser、記憶體 session)」；「(2) DB 群組使用者——`identity.authenticate` 查 `app_user` + pbkdf2 240k」為正規路徑。

**補正方向**：短期：audit log 對 env 後門登入之行動顯式標記 credential_type=env_backdoor，使歸責極限可稽核；中期：多使用者化後停用 env 後門或降級為僅可讀，行動類端點（topic 抓取、資料夾解析入庫）一律要求 DB 已解析 Identity 之 session。

### AUD-25【MINOR】升版規則與 §8 修訂程序介面缺漏：無 Steward 登錄、修訂動因非失效 Evidence、微修不改版號、無對 Layer 0 之牴觸檢查

* **憲章條款**：§8.1（Constitution Steward）、§8.5(a)（修憲附書面 Evidence）、§8.6（版本語義）
* **位置**：docs/系統架構大憲章_v1.45.0.md（第六部升版規則、修訂歷程）；docs/原則精華_v1.9.0.md（升版哲學）
* **發現視角**：治權整合（文件級審計）

**描述**：既有升版規則與 §8.6 三級版本語義概念相容（新增原則→升版≈major；重大判準修正→minor；架構承載→憲章升版），且修訂歷程之動因/同步清單/狀態標記實質優於一般工程實務。缺口為程序介面：(i) hugo 事實上行使 Steward 全部權力（親核拍板、親簽、TTY approve）但從未具名登錄為 Steward——整併官親查 grep 全 repo 無 Steward 一詞；§8.1 要求唯一人類憲章權威且其設立適用原則級門檻；(ii) 修訂動因多為「用戶 directive」而非 §8.5(a) 之「現行原則失效或矛盾之書面 Evidence」（惟多數修訂附「實證動因」欄、精神相近）；(iii) 「純文字微修正→不升版」使同一版號對應多個文本狀態（如 v1.7.1 承載兩個不同日期/內容之狀態），無法以檔名_v{x} 精確引用歷史文本，與 §8.6 patch 語義不合；(iv) 無對 Layer 0 之違憲審查/牴觸檢查步驟。

**證據**：原則精華升版哲學：「既有原則的純文字微修正→改該條文字，不新增 treaty、不升版」＋演進記錄「v1.7.1 內文字修正（2026-07-04，不升版）」；修訂歷程各版動因欄多記「用戶 directive『…入憲』」；grep 全 repo 無 Steward。

**補正方向**：(1) 於 MC 治理附則（或 augur 合規聲明）具名登錄 hugo 為 Steward 或其授權代理，既有「決策層人拍板」機制原樣承接 §8.1 職能；(2) 升版規則補「patch」級：純文字微修至少升 patch 版號；(3) 修訂流程加一步「MC 牴觸檢查」（CLAUDE.md #19 跨檔一致性檢查已存在，擴一項對 Layer 0 即可）；(4) 治權判準變更之計畫書補「原則失效 Evidence」段以對齊 §8.5(a)。

### AUD-26【MINOR】「PostgreSQL＝唯一真相來源」措辭將 Representation 稱為真相，牴觸 P2.E4 用語紀律；全體系「真相/事實」指涉三處不一

* **憲章條款**：P2.E4（禁止 Representation 被視為 Reality 本身）、§2.1、§5 角色一
* **位置**：docs/系統架構大憲章_v1.45.0.md L26-28（第一部「資料本質」條，v1.26.0）
* **發現視角**：治權整合（文件級審計）

**描述**：大憲章第一部立「PostgreSQL＝唯一真相來源（single system of record）」總綱（整併官親查 L26-28 逐字屬實）。其英文括注與實質內容（外部 API 為擷取源先落地、下游只讀 PG、「外部 API 為原始擷取源、非資料家」）完全符合 §5 角色一 World State System of Record；但中文「唯一真相來源」在 MC 術語下屬類別錯置——真相（Reality）不以被表徵為前提（§2.1），PG 僅為權威 Representation 存放處。且同體系內「真相/事實」三處指涉不一：原則精華 #2 以 API 為「唯一事實」、靈魂以「真實 API 資料」為兆、大憲章以 PG 為「唯一真相」——MC §2 定義可一次收斂。此為純措辭問題，但該句已被全庫 docstring 與下游文件廣泛引用，會在合規論證時反覆製造表面牴觸。

**證據**：大憲章 L26-28 親查逐字屬實：「本專案**一切資料的唯一真相來源(SSOT)與系統記錄，皆為本地 PostgreSQL**……外部 API（FinMind／FRED／OpenAlex…）為原始擷取源、非資料家」；對照原則精華 #2「API 是唯一事實」——兩份治權檔對「唯一真相/事實」指涉不同物。

**補正方向**：藉合規聲明補正時將該條更名為「PostgreSQL＝唯一系統記錄（single system of record）」，一句釐清：「Reality 之權威＝API 觀測；系統內權威 Representation＝PG」；下游引用逐步隨改（非緊急、可列 patch 級）。

## 五、治權整合路線圖

既有治權體系（靈魂＞原則精華＞大憲章＞CLAUDE.md＞README）需與 AUGUR-MC v1.2 完成四步整合：

1. **Layer 登錄（AUD-12）**：於 MC §0.5 Layer 對照表登錄五份治權檔 —— 建議：系統核心思想 → Layer 1 World Model 規格之領域前身；原則精華 → 跨層 domain profile（逐條標注所屬 Layer）；系統架構大憲章 → Layer 4–7 架構/維運規格；CLAUDE.md → Layer 6 Agent Runtime 協作規格；datasets 參考文件 → Layer 7。
2. **正名與從屬宣告（AUD-12/26）**：大憲章加副標（Domain Architecture Charter — Layer 4–7 Specification），「性質」段改為「受 AUGUR-MC v1.2 約束之最高**領域**承載文件」；「PostgreSQL＝唯一真相來源」更名為「唯一系統記錄（single system of record）」；各檔檔頭加 `AUGUR-MC v1.2 §{條款}` 引用。
3. **合規聲明補件（AUD-13）**：Steward 依 §8.3 過渡規則發布暫行模板並裁定補正期；五治權檔各補 Constitutional Compliance Statement（聲明版本、逐 P1–P5 論證、揭露四項已知緊張關係：#7 覆寫、SSOT 措辭、RBAC deny 呈現、Layer 1/2 缺位）。
4. **修訂程序接軌（AUD-25）**：hugo 登錄為 Steward 或其授權代理；升版規則補 patch 級；修訂流程加「MC 牴觸檢查」一步；治權判準變更計畫書補「原則失效 Evidence」段。

## 六、補正優先序建議

依 AUGUR-MC §8.2 補正期紀律分三波：

### 第一波（立即 — MUST NOT 牴觸與低成本高價值項）

| 項目 | 理由 | 工程量 |
|---|---|---|
| AUD-02 | P4.E5 為 MUST NOT，依 §8.4 無時限豁免可言 — 建 raw_supersede_log 帳表（heal 覆寫前快照舊列），upsert 主路徑不動 | 小 |
| AUD-12 | 治權撞名是所有後續合規工作的法源前提 | 極小（文件）|
| AUD-13 | 無合規聲明依條文「規格不生效力」，僅賴過渡規則推定有效 — 請 Steward 發布暫行模板 | 小（文件）|
| AUD-10/11 | 行動留痕表加 actor_identity/authorization_ref 欄；watchdog 判態改讀 attestation_result 表 | 小 |
| AUD-26 | SSOT 措辭修正 — 順手夾帶 | 極小 |

**critical 但屬結構工程者（AUD-01/03）**：第一波先做補償控制 —— 於合規聲明揭露緊張關係＋暫行保守規則（無 Confidence＝不得升高信任，依 §8.3 保守解釋），結構性補正排入第二波。

### 第二波（一個版本週期內 — 結構層建設）

AUD-01（世界概念 registry → SQL 直綁消除 → 唯一權威表徵，配合 Layer 1 規格）、AUD-03（Layer 4 Confidence 統一語義＋既有狀態官方映射表）、AUD-04/05（entity registry ＋ identity lifecycle 事件表）、AUD-06（跨來源 identity claim）、AUD-07（名冊屬性 as-of 化）、AUD-08（prediction_values 改 append-only）、AUD-09（快照版本化）、AUD-17（confirmed trigger 化）、AUD-20（CASCADE → RESTRICT ＋隔離標記）、AUD-23（行動風險分級表）、AUD-25（治權程序接軌）。

### 第三波（長期 — 品質完善）

AUD-14（除權息世界事件表徵）、AUD-15（catalog 世界概念欄）、AUD-16（claim 結構化指涉）、AUD-18（per-pick 解釋面）、AUD-19（通識標頭機械前置）、AUD-21（假說變更留痕）、AUD-22（chat 刪除 tombstone）、AUD-24（env 後門歸責標記）。

---

## 七、雙重對抗驗證結果（2026-07-16）

原設計之第 4–6 階段已於 2026-07-16 補齊執行（Run ID `wf_94841fac-18f`；因原 run 快取不可跨工作階段恢復，本輪為**全新即時查證**，不依賴任何舊快取）：26 項發現 × 2 位獨立對抗驗證官（**程式碼查證官**——逐項親自重跑 grep、逐字比對引文，預設立場為推翻；**憲章適用裁判官**——假定事實為真，只裁條款適用與 severity）＋ 1 位**報告門檢官**（跨發現一致性與最終處置），共 53 代理、758 次工具呼叫、0 錯誤。查證基準：本地 clone HEAD `e23a102`（2026-07-16「arena 開賽」，較審計基準 2026-07-15 有增量提交；驗證官逐項標注 code drift，全部漂移方向為強化而非削弱原發現）。

### 7.1 總體裁決

**26 項發現 0 項被推翻（REFUTED=0）**。25 項核心事實 100% 重現，行號偏移全部在容差內（最大一處 +15 行、內容逐字在位）；唯一被實質推翻之事實子宣稱為 AUD-14 之「除權息世界事件在系統中無表徵」（TaiwanStockDividend／TaiwanStockDividendResult 兩事件 raw 表實已入庫），該發現改寫為弱版本後仍成立、維持 minor。原審計之偏差方向一致偏保守（如 AUD-01 稱 vendor 表名直綁「15+ 檔」，現行 HEAD 實測 37 檔）。

**驗證後統計（門檢當時暫計；裁決後定稿見 7.5）**：critical 4／major 9／minor 12＋1 項待 Steward 裁定（AUD-08）。變動三項：

| 項目 | 初步 | 驗證後 | 理由 |
|---|---|---|---|
| AUD-09 | major | **critical**（附覆核條件） | P4.E3「不得刪除」為 MUST NOT，依報告自訂判準（critical＝違反禁止性規定）應為 critical；原降級理由（確定性衍生物可重算）之事實前提被同段自我否定（raw 遭 heal 覆寫、build_meta 不存成員名單）。惟若 Steward 將「原始 vs 衍生＋緩解程度」尺度明文化入判準，本項應回 major |
| AUD-21 | minor | **major** | P4.E3 supersede 義務三要件（superseded 標記／歷史保留／失效 Evidence）零履行，非「部分符合」；緩解（seed 低頻、文獻錨定）屬影響面因素而非判準構成要件，與 AUD-09 同類應同級 |
| AUD-08 | major | **待 Steward 裁定** | 兩官原均裁 major，但其錨定之先例（AUD-09 同類列 major）已被升級推翻；本項同類且事實更重（無 run_id/git_sha 留痕、已呈現出單、風控 DD 熔斷回讀）。critical vs major 之擇定即 P4.E3 家族判準決策，依 §8.2 屬 Steward 權限 |

### 7.2 全 26 項處置表

| ID | 處置 | 驗證後級別 | 門檢要旨 |
|---|---|---|---|
| AUD-01 | CONFIRMED | critical | 逐字重現且命中面擴大至 37 檔；修辭級補正：§0.5 改標脈絡定位、補正期依據 §8.3→§8.2 第四點 |
| AUD-02 | CONFIRMED | critical | P4.E5 MUST NOT 該當閉合，治權條文明文立法化屬加重；修 reconcile.py 行錨 487→502 |
| AUD-03 | CONFIRMED | critical | 零命中 grep 親自重現、P4.E1 不可豁免核心該當；標題宜限縮至知識／審議軸（預測軸校準機率為部分等價物） |
| AUD-04 | CONFIRMED | major | 行號零偏移；條款欄應移除 F4、補列 P3.E1 為核心錨點 |
| AUD-05 | CONFIRMED | major | P3.E2 不變式義務不因 Layer 3 缺位消滅；建議明文處理「未鑄造故無附著對象」抗辯 |
| AUD-06 | CONFIRMED | major | macro_vintage docstring 已過時（fred_series 已被 build_market_direction_features 消費），feature_values 零 macro 宣稱仍真 |
| AUD-07 | CONFIRMED | major | 加重發現：industry_category 在 live PK 內致新舊分類殘留並存；法源收斂為 P4.E2 單軸（P3.E3 為誤引） |
| AUD-08 | **NEEDS_HUMAN** | 待裁定 | 見 7.1 |
| AUD-09 | CONFIRMED_REVISED | **critical** | 見 7.1；三處 DELETE 逐字重現、superseded 全庫零命中 |
| AUD-10 | CONFIRMED | major | 六元組缺欄與 §8.3 機器稽核不變式違反確認；F6 應改標風險視角（「無法回答」要件未該當） |
| AUD-11 | CONFIRMED | major | fail-open epoch 分支經 Bash 重現；最強條文組合應改 P5.E1＋§8.3＋P2.E3 |
| AUD-12 | CONFIRMED | major | 雙重最高權威歧義與零從屬聲明確認；§0.5「先登錄方生效力」構成要件限新增規格 |
| AUD-13 | CONFIRMED | major | 零命中以更嚴格參數重跑仍成立；刪「可判定性元規則」對治權檔自有謂詞之誤用 |
| AUD-14 | DOWNGRADED_EVIDENCE | minor | 「除權息事件無表徵」被推翻（兩事件表已入庫）；改寫為弱版本：無 CorporateAction 一級概念、事件表與價格表還原關係零宣告繫結（多表徵問題實際更廣） |
| AUD-15 | CONFIRMED | minor | 四項核心證據重現；補 P1.E2 為直接依據、F1/P1.E1 標明為 AUD-01 已承載 |
| AUD-16 | CONFIRMED | minor | 行號零偏移；Confidence 錨定應更正至 P4.E1/P4.E8 |
| AUD-17 | CONFIRMED | minor | 行為面合規（status 寫點僅 verifiers 兩處）、缺口為 DB 級機器化保證——「部分符合」精確命中 minor |
| AUD-18 | CONFIRMED | minor | 事實全數重現；F5/P4.E6 構成要件未該當，應改寫為「解釋粒度未操作化之缺口」而非違反語氣 |
| AUD-19 | CONFIRMED | minor | 核心落差成立；主引條款應改 P4.E7；grep 檢索詞「通用常識」更正為「常識」 |
| AUD-20 | CONFIRMED | minor | 11 處 CASCADE 行號全中；分級受 AUD-08/09 家族判準連動，--fix 已行使之 DELETE 屆時一併覆核 |
| AUD-21 | CONFIRMED_REVISED | **major** | 見 7.1 |
| AUD-22 | CONFIRMED | minor | 事實零偏移；P4.E3 構成要件實未該當（chat 非 Knowledge/Evidence），重定性為防護性治理缺口、補引 P1.E3 |
| AUD-23 | CONFIRMED | minor | 11/12 查核成立；「只在註解中」修正為條件性（HANDOFF.md 亦有散文留痕） |
| AUD-24 | CONFIRMED | minor | env 後門歸責缺陷程式碼層完整確證；補引 P3.E1 與 §8.3 第三點 |
| AUD-25 | CONFIRMED | minor | 四項缺口重現；§8.1 論證重寫——首任 Steward 已於本 repo 具名登錄，缺口改述為「領域治權檔未承接 Steward 角色」 |
| AUD-26 | CONFIRMED | minor | 三處指涉不一屬實；主錨由 P2.E4 改為 §2.1＋§2 定義元規則（P2.E4 為 MUST NOT，列名即與 minor 自相矛盾） |

### 7.3 跨發現一致性裁定（門檢官）

1. **P4.E3 刪除／覆寫家族異級為最大跨發現矛盾**（AUD-02 critical／AUD-08 待裁定／AUD-09 升 critical／AUD-20 minor／AUD-21 升 major／AUD-22 minor）。Steward 須擇一：**(A)** 修正判準文字，將「原始 vs 衍生＋緩解程度」尺度明文化（則 AUD-09 回 major、AUD-08 維持 major）；**(B)** 依判準字面機械適用（則 AUD-08 升 critical、AUD-20 已行使之 `--fix` DELETE 須覆核）。此擇一屬 §8.2 Steward 權限——**本報告在正式採認前唯一的實質未決點**。（✅ 已裁決：採選項 (A)，見 7.5 節與解釋裁決第 2026-001 號）
2. **體例缺陷（系統性）**：多項發現將禁止性規定或不可豁免核心（F4@AUD-04、F6@AUD-10/11/24、F5+P4.E6@AUD-18、P2.E2@AUD-19、P2.E4@AUD-26、F1/P1.E1@AUD-15）列於【憲章條款】欄卻裁 major/minor，按自訂判準列名即應觸發 critical，形成表面自相矛盾。應建立「受違條款」與「風險視角／對照條款」之區分標注體例。
3. **重複計數檢核**：無實質重複計罪——F1/P1.E1 系統性違反由 AUD-01 單獨承載；P1.E2 四項分工（AUD-01/06/14/15）可辯護但需明文；P4.E1 Confidence 由 AUD-03 承載；同一 selfheal 鏈四項發現（AUD-10/11/23/24）各有獨立構成要件。

### 7.4 總體結論複核

「精神高度合憲、結構顯著缺層」**驗證後不僅成立且被強化**：「缺層」半句獲全面事實加固（四大結構層缺席診斷全數重現、多處證據比原審計更強）；「合憲」半句同樣經受檢驗（law 官在 AUD-18/22/26 等項認定所引條款構成要件實未該當，實際違憲面比報告標題語氣更窄；亮點描述全部屬實）。需修正處三項（嚴重度重心微幅上移、條款引用體例整修、AUD-14 子宣稱改寫）均不動搖總體結論。~~在 Steward 完成家族判準裁定（7.3 第 1 點）與體例整修前，本報告以「驗證後草案」地位流通，非終局違憲認定文書。~~（家族判準已經 7.5 節裁決定調）

### 7.5 Steward 裁決（2026-07-16，解釋裁決第 2026-001 號）

7.3 第 1 點之待決問題已由 Constitution Steward 裁決：**採選項 (A)**——P4.E3／P4.E5 家族之 severity 依「**滅失對象性質（原始 vs 衍生）＋緩解程度**」二軸綜合認定，不以 MUST NOT 單一要件機械觸發 critical。裁決全文（含理由與拘束力聲明）：[../constitution/INTERPRETATION-RULING-2026-001.md](../constitution/INTERPRETATION-RULING-2026-001.md)（AL-2026-004）。

**適用結果**：

| 項目 | 門檢暫定 | 裁決後定稿 | 適用理由 |
|---|---|---|---|
| AUD-02 | critical | **critical** | 原始證據覆寫滅失（尺度第一層） |
| AUD-08 | 待裁定 | **major** | 衍生物 DELETE 重建（尺度第二層） |
| AUD-09 | critical（附覆核條件） | **major** | 衍生物 DELETE 重建；重建保證缺損之根因為 AUD-02，繫於其補正（裁決理由三） |
| AUD-20 | minor | **minor** | tombstone／留痕緩解、影響面局部（尺度第三層）；已行使之 `--fix` DELETE 無須升級覆核 |
| AUD-21 | major | **major** | 升級理由（supersede 義務零履行）獨立於本尺度，維持 |
| AUD-22 | minor | **minor** | 構成要件未該當＋防護性缺口定性，維持 |

**定稿統計：critical 3（AUD-01/02/03）／major 11／minor 12；0 項被推翻。** 本報告自本節作成起以「已驗證＋裁決定調」地位流通；個別發現之正式違憲認定（§8.2）仍由 Steward 個案裁定。第四節 severity 分級導言自此併同本裁決尺度適用。

---

## 附錄：審計方法與狀態揭露

* **方法**：多代理工作流程（Run ID `wf_386f28b1-d49`）—— 6 偵察建圖 → 6 維度審計（35 項原始發現、54 項亮點）→ 跨視角去重整併（26 項，整併官親自重驗每項證據）。
* **未完成階段（已補齊）**：~~設計中的第 4–6 階段（52 個獨立驗證代理之雙重對抗驗證、報告門檢）因執行資源之月度上限而未運行。本報告由主迴圈依整併官輸出直接撰寫。~~ → **已於 2026-07-16 以全新 Run `wf_94841fac-18f` 補齊執行**（53 代理、0 錯誤；因快取不可跨工作階段恢復，未使用 `resumeFromRunId`，全部證據為即時重查），結果見第七節。
* **證據狀態**：每項發現的程式碼證據均經整併官親自重跑 grep／重讀檔案確認，**並已經 52 位獨立對抗驗證官雙重驗證（0 項被推翻）**；severity 分級經憲章適用裁判官與門檢官複核，除 AUD-08 與 P4.E3 家族判準待 Steward 依 §8.2 裁定外均已確認。正式違憲認定仍屬 Steward 權限。
* **驗證產物**：門檢處置表與逐項驗證裁決要旨見第七節；per-finding 原始驗證裁決全文（含每項 checks 的重現方法與實際觀察）存於 [VERIFICATION-2026-07-16-wf_94841fac.json](VERIFICATION-2026-07-16-wf_94841fac.json)。
