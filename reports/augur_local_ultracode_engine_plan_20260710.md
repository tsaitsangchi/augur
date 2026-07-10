# augur 本地審議引擎(Local Ultracode Engine)計畫 v1.2(2026-07-10;滿格拍板版:發現表 57 項留痕+DDL 對齊落地)

## 0. 三十秒+核心立論

**三十秒**:本計畫要在固定硬體(GTX 1650 4GB / qwen3:8b)上,讓本地 AI 習得 Claude ultracode 的「多視角對抗審查+自我迭代+窮舉」能力。立論=**ultracode 能力 ≈ 20% 模型智力 + 80% 編排 harness**:多視角、對抗、迭代、loop-until-dry 都是**編排模式**(控制流+狀態機+聚合),本地 Python 可完整重現;單步模型弱(8b≠Claude)以「**更多迭代 × 工具實證 × 多數決**」補償。對抗驗證的殺手鐧**不是 LLM 互噴,是懷疑者用確定性工具(psql/grep/read/pytest 白名單)驗證宣稱**——工具是誠實的,弱模型只需會提出「帶錨點的可驗宣稱」+讀工具結果。「習得」與否**不由推理裁決、由基準測試機械裁決**(§1.5):證不出「引擎>單發 qwen」的增量,就回落前身計畫的結論。

### 0.1 核心立論:20/80 分解與補償公式

| ultracode 成分 | 歸屬 | 本地化路徑 |
|---|---|---|
| pipeline/fan-out/judge panel/loop-until-dry/完整性 critic/帳本(模式 1,4,5,6,10) | **編排(80%)** | 純 Python 控制流+PostgreSQL 帳本,零模型智力需求 |
| 對抗驗證/視角鏡/結構化輸出(模式 2,3,7) | **編排為主** | lens prompt 住 DB(#29b)+ Ollama 0.31.1 原生 `format=json schema`(**已落地實證**:`ollama.py:70 make_structured_llm_fn`,qwen3:8b/4b 皆實測可 `json.loads` 且過 required-keys 檢查) |
| 工具實證錨定(模式 8) | **編排(確定性)** | **已落地**:`src/augur/deliberation/verifiers.py` 4 真 oracle(`information_schema`/`import_isolation`/`file_grep`/`db_query`,契約=前身 plan `reports/augur_deliberation_orchestrator_plan_20260709.md:174-183` §6.2 之落碼)+ 本計畫新增 pytest 沙箱 oracle(P4) |
| 單步判讀品質(模式 9 的 attack/refine 內容) | **模型智力(20%)** | 弱——以下三支柱補償 |

**補償公式**(單步弱 → 系統強的三支柱,各自極限見 §1.4):
1. **迭代**:draft→attack→refine→verify 迴圈+連續 K 輪無新發現才停——Claude 一步想到的,qwen 用 N 輪掃到;
2. **工具實證**:每承重宣稱溯 file:line / query 輸出,無錨拒收——判讀被降維成「會呼叫工具+讀結果」;
3. **多數決**:N 個獨立懷疑者(各配一失效模式鏡)投票,多數反駁即殺——壓單次隨機錯。

**經濟基礎(為何本地換得起)**:硬體實測 qwen3:8b 僅 39% 在 VRAM(`/api/ps` size_vram=2.31GB/5.96GB)→ 6.6-7.7 tok/s、think:true 一題 39.7s、並發物理序列化(`-np 1`,兩相異 prompt 並發 6.97s ≈ 2×3.39s 單發)——**慢,但全程本地零 Claude token(#28)、背景長跑時間近乎免費**。本計畫的貨幣是 wall-clock 不是 token:用「一夜 500 次 LLM call + 工具驗證」買 Claude「一次深思」買到的東西,正是 20/80 立論在此硬體上唯一可行的兌換率。

### 0.2 與前身計畫的關係(雙軌:架構層擴充、決策層 supersede)+ 落地現況

前身=`reports/augur_deliberation_orchestrator_plan_20260709.md`(v2,經 6-agent 對抗審查 35 findings/9 high 定稿)。關係**必須雙軌明示**,因前身的架構與結論方向相反:

| 層面 | 前身立場 | 本計畫處置 | 依據 |
|---|---|---|---|
| **架構骨架** | 機械鎖+pending-claim 不變式+4 oracle+escalation(前身:37,:51,:174-183,:195-198) | **擴充沿用,零重審** | 與本計畫核心洞察同構:「qwen 只准提帶錨+指定確定性 verifier 的 pending claim;`confirmed` 僅機械裁決可寫」即「懷疑者用工具驗證宣稱」的既有實作 |
| **決策結論** | §10.2「對本地 AI 在環路、習得 ultracode——**答案基本是不建**;若建只建 W1-W2 確定性子集」(前身:252-254) | **supersede——但不是反駁其論證,是換掉裁決方法** | 前身的悲觀是**推理性結論**(B 判讀品質不可移植、同底模五視角「自信地一致錯」,前身:16);推理對推理無解。本計畫改用**基準測試 harness 機械證明**「審議引擎>單發 qwen」(#15 以真兆裁決):**證得出增量 → 前身悲觀被實證推翻;證不出 → 本計畫自動回落前身結論**(只保留確定性子集)。這是可證偽的賭注,敗退路徑寫進驗收(§1.5) |
| **§8 四破口** | 原理上不可全閉(前身:211-220) | **整節繼承**為本計畫誠實能力邊界的結構素材(§1.4) | 破口是原理性的,換計畫不會消失 |
| **落地現況(2026-07-10 實查,取代舊稿「5 表無 git 住所」之過時描述)** | 計畫態 | **P1 骨架已落地並 commit(24e87a3)**:`deliberation_*` **6 表**(前身 5 表+MVP 平表 `deliberation_benchmark`)已在 DB 且 DDL 已收編 `scripts/migrate_deliberation_ddl.py`(`--run`/`--verify`);`scripts/deliberate.py`(MVP 端到端:qwen 提結構化 claim→4 oracle 裁決,含 L1-L4 機械補強層)與 `src/augur/deliberation/verifiers.py` 已 tracked;帳本已有真資料(session 15/claim 77:confirmed 40+escalated 25+refuted 12/verdict 76/benchmark 12);`scripts/benchmark_deliberation.py`(MVP 兩臂對照)已寫成但**未 track,W2 收編**。**殘留缺口=本計畫工作項**:lens 仍 hardcode 於 deliberate.py(#29b 違例,P3 搬 DB)、`DELIB_LITERALS` 未擴、redline glob 化未做(trigger_id=7 綁 `v1.39.0` 而 docs 現行=v1.40.0,漂移**已真實發生**)、file_grep 無 `.env` denylist、Ollama meta 未落帳 | 本節全數 psql/git/ls 實查 |

**零改動沿用清單(#29c,明列;含已落地項)**:
1. `deliberation_*` 6 表 DDL + redline 9 列種子——**已收編於 `scripts/migrate_deliberation_ddl.py`(git 住所,commit 24e87a3)**,本計畫僅冪等疊加新 DDL(§3);
2. 前身 §6.2 4-oracle 設計+§6.4 qwen-不當-judge 機械鎖+§3 pending-claim 不變式+§8 四破口全文——4 oracle 與機械鎖**已落碼 `verifiers.py`**(`verify_claim` 為全系統唯一寫 confirmed 之處);
3. `src/augur/advisor/ollama.py`:`make_structured_llm_fn`(**:70,已落地**——/api/chat+format=JSON schema+required-keys 檢查+有界重試錯誤回饋+num_predict 預設 512+G3 本機 host 斷言 :29)、`make_llm_fn`(:122)、`strip_think`(:55)——僅擴 meta 回傳(§4.1.1),既有函式零改動;
4. guard fail-closed 三式(`guard.py`:白名單制/豁免先過驗證/無證據限定誠實閉集)——直譯為引擎「宣稱溯工具輸出」判準;
5. `src/augur/audit/import_isolation.py`(**真實住所=src/augur/audit/,非 scripts/**):`FORBIDDEN`(:33)/`DISTILL_LITERALS`(:41)/`SCAN_DISTILL`(:45)/`check_isolation`(:160,distill 接線 :166)/`__main__`(:184)——DELIB_LITERALS 三擴同構樣板;oracle 走 **in-process `check_isolation()`**(verifiers.py 現行實作);
6. 蒸餾管線全套(`advisor_distill_question/context` 兩表+S2-S5,274 題/274 gold/171 validated 實績,本日 psql 覆核)——需求 (e) 蒸餾迴路的既有接口;
7. DB-driven resume 範本(`advisor_distill_build_context.py:76-97` 逐題 commit+旗標;`teacher.py:86-106` WHERE ... IS NULL 述詞)+ `scripts/_bootstrap.py`(#29a)+ migrate `--run/--verify` 慣例;
8. 環境資產:`augur-ollama.service`(常駐 GPU 後端)、`.env OLLAMA_TIMEOUT=18000`、`advise.py:80/:86` llm_fn 抽象注入+`serve_advisor_openai.py --mock-llm`(:42)零 LLM 煙測模式。

**前身未涉、本計畫新增**(細節見後續各節):十模式引擎全體(模式 7/8 已 MVP 落地,模式 1-6/9-10 之完整版新增)、lens 庫住 DB、`make_structured_llm_fn` meta 回傳擴充、qwen3:4b/8b 雙檔位路由(**兩模皆已安裝**,`/api/tags` 實查;MVP 已以 4b 實跑,殘留=tok/s、size_vram 效能量測回填 §3.5)、基準測試全量 harness(MVP 兩臂已先導,P2 擴 suite/臂/GATE)、(發現,裁決,證據)→蒸餾 QA 形映射層。

## 2. 引擎架構

### 2.0 架構總覽與承重不變式

> **本節零 DDL**:一切表結構唯一住所=§3(修復舊稿「同名表兩版 DDL 並存」之雙軌);本節只引用表名。**落地現況**:模式 7/8 之最小版已上線(`deliberate.py`+`verifiers.py`,commit 24e87a3);本節為其十模式完整版設計。

分層(由外而內,LLM 只出現在葉端、且永遠不被信任):

```
scripts/deliberate_*.py(CLI 入口,#29a _bootstrap)
  └─ 編排器(確定性 Python 狀態機;零 LLM、零猜測)
       ├─ 模式層 src/augur/deliberation/(十模式之實作,§2.1;模組清單見下表)
       ├─ LLM client(ollama.py:70 make_structured_llm_fn,已落地;§2.1.7)──> Ollama qwen3:4b/8b(可換葉)
       ├─ 工具箱沙箱(五確定性 oracle 白名單,§2.2;4 真 oracle 已落地 verifiers.py)
       └─ 帳本(PostgreSQL deliberation_*,§3;禁入 knowledge_*)
```

**承重不變式(整節繼承前身計畫,已落碼)**:qwen 只准提出「帶錨點+指定確定性 verifier」的 pending claim;`status='confirmed'` 僅機械裁決可寫、且須有 `is_deterministic=true` 之 verdict——**落碼處=`verifiers.py::verify_claim`,全系統唯一把 status 寫成 confirmed 的地方**;無 oracle 可判讀者強制 escalate(前身 plan:37、:51、:195-198)。DB 實證支撐:`deliberation_claim` 之 `anchor` 有 `btrim(anchor)<>''` CHECK、`assigned_verifier`/`status` 皆閉集 CHECK、`deliberation_verdict` 有 `verdict='undecidable' OR evidence IS NOT NULL` CHECK(DDL 全文=§3.1)。**這條不變式就是核心洞察的機械形式:對抗驗證的殺手鐧是確定性工具驗證宣稱,不是 LLM 互噴。**

模組佈局(**全計畫唯一模組分解,§4.2 同此;#18 命名**):

| 檔案 | 狀態 | 職責 | 對應模式 |
|---|---|---|---|
| `src/augur/deliberation/verifiers.py` | **已落地** | 4 真 oracle 確定性 verifier+`verify_claim` 機械鎖;P4 擴 pytest | 8(§2.2) |
| `src/augur/deliberation/engine.py` | 新(P3) | run/round 狀態機(draft→attack→verify→refine、loop-until-dry 停機);MVP 期此邏輯暫居 deliberate.py,P3 抽出 | 1, 5, 9 |
| `src/augur/deliberation/llmroute.py` | 新(P3) | 檔位解析(model_profile⋈lens)+結構化呼叫包裝 | 7(§2.3) |
| `src/augur/deliberation/lens.py` | 新(P3) | lens 庫 DB 載入+prompt 組裝(cache 友善前綴);取代 deliberate.py 內 hardcode 之 LENS_PROMPTS(#29b) | 3 |
| `src/augur/deliberation/consensus.py` | 新(P3) | 多數決聚合(只殺不升)+judge panel 合成 | 2, 4 |
| `src/augur/deliberation/critic.py` | 新(P3) | 完整性 critic(機械枚舉先行+LLM 殘差)+dry 判定 | 5, 6 |
| `src/augur/deliberation/ledger.py` | 新(P3) | run/task/claim 帳本 CRUD+claim 格式閘+resume 述詞 | 10, 1 |

隔離:`src/augur/audit/import_isolation.py` 三擴 `DELIB_LITERALS`,同構沿用 `DISTILL_LITERALS`(:41)/`SCAN_DISTILL`(:45)/`check_isolation` 接線(:166)樣板——deliberation 層禁被預測管線 import、審議產物(AI 生成)只落 `deliberation_*` 絕不入 `knowledge_*`。

### 2.1 十模式逐一本地化設計

#### 2.1.1 模式 1:pipeline / parallel fan-out

- **機制**:逐項多段管線(單項走完 draft→attack→verify 才進下一項,無全域 barrier);僅「跨項去重/聚合」步驟才設 barrier。fan-out=同一標的物派給 N 個鏡。
- **Python 實作要點**:job=`deliberation_task` 之 pending 列(§3.3.6;先批次 INSERT、再消化);**單 LLM 車道+工具車道雙線程**——LLM worker 逐列序列打 Ollama,oracle worker(`ThreadPoolExecutor`)平行驗證已回收的 claim,兩車道經 task.status 交棒。barrier=SQL 述詞 `NOT EXISTS(SELECT 1 FROM deliberation_task WHERE run_id=… AND round_no=… AND status IN ('pending','running'))`。成本模型先估後跑:`est_wall ≈ Σ(prompt_tok×33ms + gen_tok÷7tok/s)`(冷估依據:prompt_eval 1095ms/33tok、生成 6.6-7.7 tok/s 實測;長 prompt 須 W 階段實測校正後回填,#9 不寫死)。
- **與 Claude 版差異**:Claude fan-out=真平行 subagent;本機 Ollama runner 為 `-np 1` 單 slot,**並發=排隊序列化**(實測 pair wall 6.97s ≈ 2×單發 3.39s)——「並行」只在邏輯層(DB 狀態機),物理吞吐按單流 ~7 tok/s 編預算;真正可平行的是「LLM 推理 × 工具驗證」重疊,此為本地版並行價值所在。

#### 2.1.2 模式 2:對抗驗證(N 懷疑者、多數反駁即殺)

- **機制**:N 個懷疑者(`skeptic_n=3`,住 engine_config)、prompt 偏向「反駁」;本地版**殺的權力分兩級**——(a) 反駁若附錨點且其指定 oracle 跑出 `refuted` 確定性 verdict → **單票即殺**(證據制,一票夠);(b) 純意見反駁(無 oracle 可裁)→ 只累計票數(落 `deliberation_vote`,§3.3.8),多數反駁=claim 轉 `discarded`(triage 資源分配、非真理裁決)或提升 escalate 優先級,**絕不產生 confirmed/refuted**。
- **Python 實作要點**:`consensus.py` 聚合;票的計數走 VIEW `v_deliberation_vote_tally`(§3.4,冪等、無雙寫)。skeptic 每 call 針對單一標的段落/claim,輸出 schema `{refute: bool, findings: [{claim_text, anchor, assigned_verifier, category}]}`(模式 7 強制)。
- **與 Claude 版差異**:Claude 端 N 懷疑者=N 個獨立智力;本地 N 樣本出自**同一底模**(qwen3),錯誤相關、會「自信地一致錯」(前身 plan:16-20)——故多數決在本地**只是排序訊號、不是裁決**,裁決權全部移交確定性 oracle。此設計直接回應前身 §10.2「qwen 當 judge 品質乘零」的悲觀:不讓它當 judge,讓它當「會指路的探測器」。

#### 2.1.3 模式 3:視角多樣鏡(lens 庫住 DB)

- **機制**:每驗證者綁一面**獨立失效模式鏡**(而非 N 個同質):正確性/防洩漏 #8/資料真實 #1/重現性/安全 #5/效能。lens=DB 一列(`deliberation_lens`,DDL=§3.3.3;#29b),擴新鏡=INSERT、零改碼。**現況**:MVP 之三鏡(skeptic/complete/doctrine)hardcode 於 deliberate.py `LENS_PROMPTS`——P3 以 `seed_deliberation_lens.py` 搬 DB、deliberate.py 改讀 DB。
- **Python 實作要點**:`lens.py` 載入 active lens;prompt=**固定共用前綴**(prompt_prefix,全 lens 共用)+ lens 專屬段(prompt_template)+ 變動尾段(標的物)——刻意利用 Ollama prompt cache(實測 `cached n_tokens=22` 生效)。claim 表既有 `perspective` 欄即 lens 名落點(引擎雙寫 `perspective=lens_name` 相容 MVP,並填 `lens_id` FK,§3.2)。
- **與 Claude 版差異**:Claude 的 lens 一句 prompt 即生效;弱模型的 lens 必須**更窄更具體**(單一失效模式+schema 綁死輸出+範例錨點格式),並版本化(`version` 欄)——基準測試按 lens 分桶統計命中率,弱鏡汰換=UPDATE `active`,零改碼。

#### 2.1.4 模式 4:judge panel(N 方案→評分→合成)

- **機制**:N 個不同角度獨立產案 → 評分 → 合成勝者+移植亞軍優點。本地版評分**機械化**:rubric 每一項必須「可檢查」——schema 完備數、tool-anchored claim 比率、oracle 通過數、CLI 矩陣齊備(regex 可驗)。LLM 只「填表+附錨點」,**最終分數=編排器對已驗證欄位算確定性加權和**;不可驗證維度(優雅度、品味)不計分、列 escalate 附註。
- **Python 實作要點**:`consensus.py::synthesize_panel`;提案落 `deliberation_proposal`(kind='candidate'/'synthesis'、merged_from 陣列)、評分落 `deliberation_panel_score`(§3.3.9-10)——**不動 `deliberation_verdict`**(該表語意保留給確定性 verifier 結果,單一職責)。提案走 fast 檔;合成用 deep 檔(8b think=true),輸入=勝者全文+亞軍「已確認優點清單」(只餵 confirmed 項,防雜訊)。
- **與 Claude 版差異**:Claude 的 judge 靠判讀品質(B),前身已裁決 B 不可移植、qwen 不當 judge 升機械鎖(plan:16-20、§6.4)——本地 judge panel 是「**機械評分表+LLM 填表員**」:分數來自可驗欄位,LLM 意見對分數零直接貢獻。

#### 2.1.5 模式 5:loop-until-dry(連續 K 輪無新發現才停)

- **機制**:連續 K 輪(`loop_dry_k=2`,住 engine_config)無新發現才停;`count<N` 截斷會漏長尾。
- **Python 實作要點**:「新發現」判定必須機械——弱模型會**換句話重提舊發現**,靠 LLM 自報「沒新的了」不可信。`dedup_key`=`sha256(category | assigned_verifier | anchor_file | anchor_line//10 | 正規化參數)`(行號桶化 ±10 行防漂移),確定性、零 LLM——此即 §3.2 claim 擴欄 `dedup_key` 之導出式;同 run 內撞唯一索引 `ux_delib_claim_run_dedup`=舊發現,不計入「新」。硬上限 `round_max`(預設 6)+成本預算(§2.1.1 成本模型)雙保險防噪音模型無限轉。
- **與 Claude 版差異**:Claude 端「無新發現」自報大致可信;本地版**dedup_key 去重是停機判準的承重件**——新發現=新 dedup_key+通過 pending 格式閘,兩者皆確定性。INSERT 撞唯一索引=重複發現,靜默略過並計數入該 task 之 `result` JSONB(供基準測試量測「弱模型重複率」);輪產出讀 `v_deliberation_round_yield`(§3.4)。

#### 2.1.6 模式 6:完整性 critic(「還缺什麼」)

- **機制**:發現=下一輪工作。本地版切兩層:**(a) 機械枚舉先行(零 LLM)**——可枚舉的完備性全部確定性檢查:計畫審=每個提及的表有無 CREATE TABLE、每支 script 有無 CLI 矩陣(regex/AST 解析);diff 審=hunk 覆蓋圖(無任何 claim 覆蓋的 hunk=盲區清單)。**(b) LLM critic 只吃殘差**——輸入=機械覆蓋圖+「還缺什麼」,deep 檔 think=true,輸出=missing-item 之 pending claim(仍須錨點+verifier,不是結論)。
- **Python 實作要點**:`critic.py::mechanical_coverage(artifact) -> CoverageMap`(純 Python);`critic.py::residual_critic(coverage_map)`(LLM);critic 產出直接 INSERT 為下一輪 claim(round_no+1,task_kind='completeness')。
- **與 Claude 版差異**:Claude critic 語意嗅覺強、可直接挑語意缺漏;本地版誠實繼承前身 §8(c):**覆蓋只達結構完整、語意不可枚舉**(plan:211-220)——機械層保證「結構上列了的都查了」,語意缺漏靠 LLM 殘差碰運氣、其輸出仍受機械鎖約束,漏提即漏(§8(a),誠實邊界節之素材,不在本節重複論證)。

#### 2.1.7 模式 7:結構化輸出 schema+驗證失敗重試(**已落地**)

- **機制**:每個 LLM call 綁 JSON schema,server 端文法約束+harness 端驗證,失敗有界重試。
- **落地現況(#29c,零重寫)**:`ollama.py:70 make_structured_llm_fn(schema, model=None, base=None, timeout=None, retries=1, options=None, think=False)`——`prompt(str)->dict`:POST `/api/chat`+`format=<schema>`;`json.loads`+required-keys 檢查;失敗→**錯誤回饋進下一輪 prompt 有界重試**(≤retries,再敗 raise RuntimeError 錯得大聲 #15);`num_predict` 未給時預設 512(實測 80 tok 會截斷 JSON、300 tok 成立);G3 本機 host 斷言(:29 `_assert_local_host`,v1.37.0 允許清單外端點寧可拒起)。實測 qwen3:8b/4b 皆成立;4b think 未壓時思考文會洩進內容,**format 約束本身壓住洩漏**,故預設 think=False。
- **本計畫擴充(唯一改動)**:加選用參數 `with_meta=False`;`with_meta=True` 時回 `(obj, meta)`,meta=`{eval_count, prompt_eval_count, total_duration, load_duration, done_reason, model}`——現行 Ollama 回應 metadata 被丟棄,帳本(§3.3.7)與基準計時(§5)依賴此。預設 False=既有呼叫方(deliberate.py)零回歸。
- **與 Claude 版差異**:Claude 輸出格式紀律高,schema 常可免;本地版 **schema 強制是 20/80 立論的直接體現**——把「格式紀律」從模型智力搬進 harness,弱模型只需在文法約束下填格子。格式合法≠內容正確——schema 只保證形,不保證真。

#### 2.1.8 模式 8:工具實證錨定(禁 LLM 意見當證據;**已落地**)

- **機制**:每承重宣稱溯 file:line / query 輸出。前身核心不變式+4 oracle 已落碼 `verifiers.py`,anchor 契約(實碼,確定性、可重跑):

| verifier | anchor 契約 | 裁決語意 |
|---|---|---|
| `information_schema` | `"table"` 或 `"table.column"` | 存在=confirmed |
| `import_isolation` | 正典式 `"check_isolation"` | violations==[]=confirmed |
| `file_grep` | `"<repo相對路徑>::<regex>"` | 有行匹配=confirmed(evidence 附 file:line) |
| `db_query` | `"<單一SELECT> => <op> <數值>"`(op∈==,!=,>,>=,<,<=) | 單標量比較成立=confirmed |

  anchor 不合契約=`undecidable`(fail-closed,寧 escalate 不硬猜)。**MVP 實戰教訓已落碼為 L1-L4 機械補強層**(deliberate.py):L1 schema-grounding(題目 token 實查 information_schema 注入真表名清單,滅「錯表名=refuted」主因)、L2 verifier 選型 lint(查無表+形如程式符號→確定性改派 file_grep)、L3 anchor 正規化(剝模型畫蛇添足前綴/補 target 路徑,零資訊損失)、L4 宣稱快路(可機械解析的宣稱直接產錨、零 LLM——確定性凌駕生成)。
- **pytest 納入第五 oracle 需擴 claim CHECK**(DDL=§3.2;沙箱=§2.2.4,P4 拍板後啟用)。
- **與 Claude 版差異**:**唯一「本地版≥Claude 版」的模式**——Claude 端錨定靠自律+抽查;本地版是 DB CHECK+`verify_claim` 單一寫入點強制,機械鎖無智力需求,弱模型完全不被信任反而更嚴。

#### 2.1.9 模式 9:自我迭代(draft→attack→refine→verify)

- **機制**:草稿→攻擊→修訂→驗證迴圈+機械完備性檢查,直到模式 5 停機。
- **Python 實作要點**:`engine.py` 狀態機:`DRAFT`(fast 檔)→`ATTACK`(模式 2/3 skeptic pass)→`REFINE`(deep 檔;輸入=草稿+**僅已確認發現 top-k**,`refine_topk=5`,config——未確認反駁不餵,防弱模型被雜訊帶偏)→`VERIFY`(oracle 對修訂稿重跑)→回 `ATTACK`。多輪上下文以 prompt 內嵌前情(現行 `make_structured_llm_fn` 為單 turn prompt 介面,4096 token 預算內嵌摘要即可),不需對話狀態管理。每次轉移=`deliberation_task` 一列。
- **與 Claude 版差異**:Claude refine 可單輪吸收大量 review;本地 `num_ctx` 載入值僅 4096(實測 `-c 4096`,調大擠壓 4GB VRAM)→ **每輪只餵小批次、多輪小步取代單輪大步**——以迭代次數×工具實證換單步智力,正是核心洞察的補償機制。

#### 2.1.10 模式 10:resume-safe 帳本

- **機制**:每 agent call 落 DB、斷點續跑、冪等。**DB 為唯一 ledger,檔案工件(報告 md/jsonl)一律可冪等重生自 DB**(驗收條款;sft.jsonl 與 DB 旗標脫鉤已實際發生——validated=171 但檔案不存在,本日 find 覆核仍不存在)。
- **Python 實作要點**:`ledger.py`;承載結構=`deliberation_run`(config_snapshot+target_sha256 凍結)/`deliberation_task`(冪等鍵 `UNIQUE(run_id, idempotency_key)`)/`deliberation_agent_call`(每 LLM call 一列,收容 Ollama meta)——DDL 全文=§3.3.5-3.3.7。resume 述詞沿用蒸餾管線範本(`WHERE status IN ('pending','failed')`+逐列 commit,teacher.py:86-106、build_context.py:76-97);重跑撞鍵即跳過。
- **與 Claude 版差異**:Claude workflow resume 靠 session 快取;本地長跑是小時級(~7 tok/s 單流)、以 nohup/systemd 背景跑(既有慣例),**逐 call 落庫是零 Claude token 全程背景的前提**——逾時語意也不同:互動 advisor 逾時即 raise 正確,背景引擎在 task 狀態機層包「逾時→記 `failed`→可 requeue(≤2 次,再敗 escalate)」,不改 `ollama.py` 的誠實 raise。MVP 之 session 制帳本(deliberate.py 現行)保留為輕量單發模式,run/task 制為多輪引擎帳本,claim 以「session_id 或 run_id 至少居其一」雙軌相容(§3.2 home CHECK)。

### 2.2 工具箱沙箱(確定性 oracle 白名單)

#### 2.2.1 五 oracle 規格(4 已落地+1 新增)

前身已裁決真可用 oracle 只有 4 個、偽 oracle 已剔除(plan:174-183、:264-265,全數繼承不重審),且 **4 者已落碼 `src/augur/deliberation/verifiers.py`**;pytest 為本計畫新增第五個(用戶需求),風險級獨立論證(§2.2.4)。

| oracle | 實作(實碼) | 判什麼 | 風險級 |
|---|---|---|---|
| `information_schema` | 參數化查 `information_schema.tables/columns` | 表/欄存在性 | 唯讀 |
| `import_isolation` | **in-process** `from augur.audit.import_isolation import check_isolation`(:160),violations==[] 判定 | 隔離紅線 | 唯讀(自家靜態掃描器) |
| `file_grep` | 純 Python re 逐行掃描;realpath 圍欄鎖 repo 內 | 檔案內容宣稱、file:line 錨點 | 唯讀 |
| `db_query` | `BEGIN TRANSACTION READ ONLY`+`SET LOCAL statement_timeout='30s'`+單條 SELECT(禁寫入詞 regex+禁分號)+單標量比較 | 資料層宣稱(列數/值) | 唯讀 |
| `pytest`(新,P4) | `subprocess` argv 直呼 `python -m pytest <nodeid> -x -q` | 行為宣稱(測試過/不過) | **執行級(獨立約束)** |

oracle 執行結果寫 `deliberation_verdict`(`evidence`=工具原始輸出摘要;DB CHECK 已強制非 undecidable 必附 evidence)。oracle 之參數/開關/沙箱設定住 `deliberation_oracle` registry(§3.3.4;**契約實作住 verifiers.py=code,表僅承載參數,#29b「新來源協定才寫新 code」**);`migrate --verify` 驗 `oracle_name` 集合=verifiers.ORACLES∪{'pytest'} 且 ⊆ claim CHECK 枚舉。

#### 2.2.2 db_query 唯讀:現況+強化(機械強制,不只靠 regex)

現行(已落地):唯讀交易+statement_timeout+禁寫入詞 regex+單語句。**強化項(W2)**:regex 可能有繞過面,補 **DB 權限層強制**——專用唯讀角色,即使注入寫語句,角色無權限+唯讀交易=直接報錯,fail-closed:

```sql
CREATE ROLE deliberation_ro LOGIN PASSWORD '<住 .env,不入 git>';
GRANT CONNECT ON DATABASE augur TO deliberation_ro;
GRANT USAGE ON SCHEMA public TO deliberation_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO deliberation_ro;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO deliberation_ro;
ALTER ROLE deliberation_ro SET default_transaction_read_only = on;
ALTER ROLE deliberation_ro SET statement_timeout = '30s';
```

`db_query`/`information_schema` 兩 oracle 改用此角色連線(與引擎寫帳本的主連線分離)。

#### 2.2.3 file_grep:路徑沙箱現況+秘密 denylist(**實查缺口,W2 必補**)

- 現行(已落地):`(REPO_ROOT / path).resolve()` 後強制 `startswith(REPO_ROOT)`(realpath 先行防 symlink 逃逸);超界/非檔=undecidable。
- **實查缺口**:現行**無 denylist——`.env` 在 repo 內、file_grep 可及**(verifiers.py 實查);工具輸出會進 verdict evidence 與後續 prompt/帳本,秘密一旦入庫即污染 dump/遷移鏈。**W2 必補**:`.env`、`*.pem`、`.git/` 等秘密載體一律拒讀(#5),違反記 undecidable+帳本留痕。
- 輸出上限:現行 evidence 截 3 行×120 字;引擎層另設單次 20,000 bytes 上限(防塞爆 num_ctx 4096 預算)。

#### 2.2.4 pytest:第五 oracle 的獨立風險級論證

pytest 會**執行任意 Python**,與唯讀 oracle 不同風險級,約束如下(缺一不啟用):

1. **只跑 repo 已 tracked 的既有測試**:node id 先過 regex `^tests/[\w/]+\.py(::[\w\[\]-]+)*$`,再以 `git ls-files` 驗證該檔受版控——LLM 不得提供測試碼內容,只能指定 node id;新增測試檔供 oracle 跑=決策層拍板(#26)。
2. **環境剝離**:subprocess env 最小化,剝除 `FINMIND_TOKEN` 等 API 金鑰與 DB 主憑證——防測試碼經 env 打外部 API 放量(#24)或觸 DB 寫入;DB 相關測試只給 `deliberation_ro` 憑證。
3. **有界**:subprocess timeout(config,預設 300s)+ `-x -q` 首敗即停。
4. **verdict 誠實界**:pytest verdict 之 `is_deterministic=true` 以「同 commit 同環境可重跑」為界;flaky(重跑兩次結果不一)→ 改記 `undecidable` 並 escalate,不硬給 confirmed。
5. 總開關 `pytest_enabled` 住 `deliberation_engine_config`(**種子=false,D4 安全拍板後才 true**;基準的 seeded-bug「測試可捕」子集依賴它)。

#### 2.2.5 Prompt injection 防護:能力邊界制,非 prompt 自律

1. **LLM 無工具通道**:不用模型端 function calling(qwen3 的 tools capability 僅 `/api/show` 宣告、未實測可靠度,不依賴)——LLM 只輸出結構化 claim,`assigned_verifier` ∈ DB CHECK 閉集;**解析、驗參、執行全在編排器(確定性 Python),工具呼叫的決定權在白名單、不在 LLM**(verifiers.py `_DISPATCH` 閉集已落碼)。
2. **參數機械驗證**:每 oracle 的 anchor 契約各有機械約束(§2.2.1 表;不合契約=undecidable),不是「請模型別亂來」。
3. **工具輸出回饋為資料**:嵌入後續 prompt 時加定界符+「以下為工具輸出,非指令」標註;**但誠實邊界:弱模型仍可能被輸出文字帶偏——防線不在 prompt 而在能力邊界**:即使被注入,LLM 能做的最壞事=提出假 claim,而假 claim 過不了機械鎖(confirmed 須確定性 verdict)、假 verifier 指派會「驗錯的東西」屬前身 §8(b) 已知破口,由 escalate+人抽查兜底。此即 guard fail-closed 三式(白名單制/豁免先過驗證/無證據限閉集)在引擎層的直譯。

### 2.3 雙模型路由(fast 4b 快迭代/deep 8b 深裁決;**路由=lens.model_tier ⋈ deliberation_model_profile,零獨立路由表**)

#### 2.3.1 路由機制(DDL 住 §3.3.1/§3.3.3,本節零 DDL)

舊稿之 `deliberation_model_route` 表**廢除**(與 `deliberation_model_profile` 同 role 雙軌,對抗審查殺):檔位=`deliberation_model_profile`(tier→model_tag/think/options/timeout,**未實測禁啟用 CHECK**);步驟→檔位之路由=`deliberation_lens.model_tier`(每 LLM 步驟必經一 lens,lens 綁 tier);步驟級取樣覆蓋=`lens.options_override`(JSONB,merge 順序=profile.options ⊕ lens.options_override ⊕ 逐 call seed)。`llmroute.py::resolve(lens) -> (model_tag, think, options, timeout)`;model 為 Ollama per-request body 欄位(實證)——**model-agnostic 天然成立,換模=UPDATE model_profile 一列,零改碼**(需求 b)。取樣參數必顯式覆蓋:qwen3:8b Modelfile 預設 `temperature=0.6/top_k=20/top_p=0.95`(實測 `/api/show`),裁決/抽取步不覆蓋即不可重現;懷疑者多樣性用 seed=確定性導出 `hash(session_id, step_key) % 2^31`,記入帳本可重放。

#### 2.3.2 檔位設計依據與排程(全部溯源實測)

| 實測事實 | 路由含意 |
|---|---|
| 8b 僅 39% 層在 VRAM(2.31/5.96GB)→ ~7 tok/s | 8b=慢深思檔,只給裁決/合成/critic |
| think:true 39.7s vs think:false 5.5s(~7x) | think 只開在 deep 檔三步,成本入預算 |
| 冷載 9.24s/次(load_duration 實測) | **換檔有稅**:排程按 tier 分批連跑(phase-grouped),同 phase 內不交替 4b/8b,換檔次數≤每 phase 一次 |
| `-np 1` 序列化;`/proc/337/environ` 無 OLLAMA_NUM_PARALLEL 等調校 | 路由不假設並行;若試 `OLLAMA_NUM_PARALLEL>1` 屬 #27 逐級逼近實驗(KV cache 擠壓 4GB VRAM 可能更慢),非預設 |
| num_ctx 載入值 4096(模型上限 40960) | profile.options 帶 `num_ctx`;調大之 VRAM 代價未實測,保守 4096 起步,prompt 組裝端強制 token 預算 |
| **qwen3:4b 已安裝並實戰**(`/api/tags` 兩模皆列;MVP 基準 12 列全以 4b 跑,deliberate.py 預設 --model qwen3:4b) | fast 檔可用性已實證;殘留=tok/s、size_vram==size(全 GPU)量測回填(probe,§4.3.3) |

#### 2.3.3 前置與降級雙軌(誠實列明,不假設)

- **前置待辦(修訂:安裝已完成)**:~~ollama pull qwen3:4b~~ **兩模皆已安裝**(實查);待辦=`probe_deliberation_models.py` 量測 4b `size_vram==size`(證全 GPU)+tok/s 回填 `model_profile.verified_note`;**兩模同駐時 4b 是否仍全 GPU 屬未知,不得假設**,`OLLAMA_MAX_LOADED_MODELS`/`keep_alive` 策略以實測定案後回填(#27 重覆驗證再定論)。
- **降級模式(4b 效能實測不合格)**:model_profile fast tier 改指 qwen3:8b(UPDATE 一列),引擎全功能照跑、只慢——這同時就是**單模運行模式**。
- **CPU-only 雙軌(需求 f)**:路由邏輯零分支——Ollama 自行處理無 GPU 情境,引擎只感知 tok/s 變慢;成本模型的 tok/s 取自帳本實測列(GPU/CPU 環境各自累積),不寫死。GPU 監控用 `/usr/lib/wsl/lib/nvidia-smi` 絕對路徑(PATH 內無,實查)。

## 3. table schema 全集

> **落地對齊註記(2026-07-10 滿格補丁)**:`deliberation_benchmark` DDL 已落地於 `scripts/migrate_deliberation_ddl.py`(commit f3f04c8);`deliberation_distill_staging` **不再需要**——蒸餾橋接已由 `scripts/bridge_deliberation_distill.py` 直橋落地(claims→advisor_distill_question,claim_id 溯源、UNIQUE 冪等),40 題已入庫;W5a 相應作廢。

> **本節地位**:v1.39.0 計畫完整性 (a) 之「全部 table DDL」——**全計畫一切 DDL 唯一住所**(§2/§5/§6 零 DDL、只引用本節;修復舊稿同名表雙版並存)。權威=DB `information_schema`;DDL 之 git 住所=`scripts/migrate_deliberation_ddl.py`(已落地,commit 24e87a3;本計畫冪等疊加)。本節所有「現況」宣稱皆經本機 psql/git 實測(2026-07-10)。

### 3.0 命名裁決表與隔離不變式(先於一切 DDL)

**命名裁決表(全計畫別名→正名;凡本計畫或前稿出現左欄名,一律讀為右欄)**:

| 別名/廢名(出處) | 正名 | 裁決依據 |
|---|---|---|
| `deliberation_agent_call`(§4 舊稿) | `deliberation_agent_call`(§3.3.7) | 單一 LLM 呼叫帳本,一表一 role |
| `deliberation_config`(§2 舊稿) | `deliberation_engine_config`(§3.3.2) | 名帶領域限定 |
| `deliberation_model_route`(§2.3 舊稿) | **廢除**——路由=`deliberation_lens.model_tier`⋈`deliberation_model_profile`(§3.3.1/§3.3.3) | 同 role 雙表殺一;§8.3 W3b 已用 model_profile |
| `benchmark_case/_run/_result`(無前綴,§5.5 舊稿) | `deliberation_benchmark_case/_run/_result`(§3.3.11-13) | 隔離防線 1(前綴)+逃逸 DELIB_LITERALS 掃描不可容 |
| `advisor_distill_question(直橋,見落地對齊註記)`(§8.5)/`deliberation_distill_export`(§3.3.13 舊稿) | **廢除,零新 DDL**——直寫 `advisor_distill_question/context`(§6.2 裁決) | #29c 不重複造輪;冪等鍵=question UNIQUE、溯源=topic_ref |
| `deliberation_skeptic_tally`(§2.1.2 舊稿) | `v_deliberation_vote_tally`(§3.4) | 同 role view 併一 |
| `make_struct_llm_fn`/`make_chat_fn`/`make_structured_fn`(§2/§4/§8.1 舊稿三名) | **`make_structured_llm_fn`(ollama.py:70,已落地)** | 實碼定名 |
| `oracle.py`/`oracles.py`/`lens_store.py`(§8.1 W1d) | `verifiers.py`(已落地)/`lens.py` | 實碼定名;§8 內舊名照此讀 |
| `benchmark_deliberation.py` vs `generate_benchmark_cases/run_benchmark/report_benchmark_verdict.py`(§5.6 舊稿三支)vs `build_benchmark_corpus.py`(§8.2) | **`benchmark_deliberation.py` 單支多態(已落地 MVP;#29c 合併)** | §7/§8 之 `run_benchmark.py --all`→`benchmark_deliberation.py --run --all`、`build_benchmark_corpus.py`→`--seed-cases` 照此讀 |
| `bridge_deliberation_distill.py`(§4.3.6 舊稿)/`export_deliberation_sft.py`(§8.5) | `map_deliberation_to_distill.py`(§6.4) | 與勝出之 §6.2 設計同居所 |
| migrate `--apply/--check`(舊稿) | `--run/--verify`(已落地實名) | 實碼定名 |

**隔離不變式(審議產物絕不入 `knowledge_*`,五道防線)**:

1. **表名前綴**:一切審議/基準產物住 `deliberation_*` 前綴表——此前綴即 `import_isolation.py` 字面掃描之錨(`DELIB_LITERALS` 三擴,同構樣板=`DISTILL_LITERALS` @ src/augur/audit/import_isolation.py:41/:45/:166)。
2. **零跨界 FK**:`deliberation_*` 不得有任何 FK 指向 `knowledge_*`/`philosophy_*`/市場層表,反向亦然。`migrate --verify` 以下列 query 驗(預期 0 列,>0 即 loud fail):

```sql
SELECT conrelid::regclass AS src, confrelid::regclass AS dst
FROM pg_constraint
WHERE contype = 'f' AND (
    (conrelid::regclass::text  LIKE 'deliberation_%'
     AND (confrelid::regclass::text LIKE 'knowledge_%' OR confrelid::regclass::text LIKE 'philosophy_%'))
 OR ((conrelid::regclass::text LIKE 'knowledge_%' OR conrelid::regclass::text LIKE 'philosophy_%')
     AND confrelid::regclass::text LIKE 'deliberation_%'));
```

3. **AI 產物溯源 CHECK**:凡可能承載 AI 生成內容之表,以 NOT NULL+CHECK 強制標示來源(`benchmark_case.origin`、`lens.author`、`claim.provenance jsonb NOT NULL` 既有)——鏡射憲章 v1.36.0 `owned_local` 之 DB CHECK guard 模式。
4. **唯一 sanctioned 跨子系統觸點**=蒸餾映射之**軟連結**:`advisor_distill_question.topic_source='deliberation_engine'`+`topic_ref=claim_id`(§6.2;蒸餾表本身即 AI 工作區、非 knowledge_*;零硬 FK,兩子系統可獨立遷移,孤兒由 `migrate --verify` 稽核)。界線:出口僅到 advisor 本機蒸餾,**絕不回流預測管線**。
5. **誠實邊界(#15)**:DB 的 CHECK 無法阻止「別的 code 把 deliberation 文本 INSERT 進 knowledge_*」——真正防線是第 1 條的 code 層掃描+治權條款;本節不佯稱 DB 單獨可封死。

### 3.1 既有 6 表:現況與 DDL 全文(已收編,零改動沿用)

實測現況(2026-07-10):6 表已在 DB **且 DDL 已有 git 住所**=`scripts/migrate_deliberation_ddl.py`(commit 24e87a3;`--run` 冪等建表、`--verify` 斷言 CHECK/FK/UNIQUE);帳本已有真資料:session 15、claim 77(confirmed 40/escalated 25/refuted 12)、verdict 76、escalation 25、redline_trigger 9、benchmark 12。舊稿「手動 psql 建、無 git 住所」**已過時**——收編待辦已完成,本計畫僅冪等疊加。DDL 全文(逐字同 migrate script,滿足「附全部 table DDL」):

```sql
CREATE TABLE IF NOT EXISTS deliberation_session (
  session_id text PRIMARY KEY,
  topic      text NOT NULL,
  draft_path text,
  as_of      date,
  status     text NOT NULL DEFAULT 'open'
               CHECK (status IN ('open','adjudicating','escalated','closed')),
  coverage   jsonb NOT NULL DEFAULT '{}'::jsonb,
  model_tag  text,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS deliberation_claim (
  claim_id          bigserial PRIMARY KEY,
  session_id        text NOT NULL REFERENCES deliberation_session(session_id) ON DELETE CASCADE,
  perspective       text NOT NULL,
  category          text NOT NULL
                      CHECK (category IN ('schema','program','isolation','doctrine',
                                          'antileakage','truesign','coverage','other')),
  claim_text        text NOT NULL,
  anchor            text NOT NULL CHECK (btrim(anchor) <> ''),
  assigned_verifier text NOT NULL
                      CHECK (assigned_verifier IN ('information_schema','import_isolation',
                                                   'file_grep','db_query','human_claude','none')),
  status            text NOT NULL DEFAULT 'pending'
                      CHECK (status IN ('pending','confirmed','refuted','undecidable','escalated')),
  provenance        jsonb NOT NULL,
  created_at        timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_delib_claim_session ON deliberation_claim (session_id, status);

CREATE TABLE IF NOT EXISTS deliberation_verdict (
  verdict_id       bigserial PRIMARY KEY,
  claim_id         bigint NOT NULL REFERENCES deliberation_claim(claim_id) ON DELETE CASCADE,
  verifier         text NOT NULL,
  verdict          text NOT NULL CHECK (verdict IN ('confirmed','refuted','undecidable')),
  evidence         text,
  is_deterministic boolean NOT NULL DEFAULT true,
  ran_at           timestamptz NOT NULL DEFAULT now(),
  CHECK (verdict = 'undecidable' OR evidence IS NOT NULL)
);
CREATE INDEX IF NOT EXISTS ix_delib_verdict_claim ON deliberation_verdict (claim_id, ran_at);

CREATE TABLE IF NOT EXISTS deliberation_escalation (
  escalation_id bigserial PRIMARY KEY,
  claim_id      bigint NOT NULL REFERENCES deliberation_claim(claim_id) ON DELETE CASCADE,
  reason        text NOT NULL
                  CHECK (reason IN ('no_oracle','undecidable','red_line_category','verifier_none')),
  payload       jsonb NOT NULL,
  resolved      boolean NOT NULL DEFAULT false,
  resolution    text,
  resolved_at   timestamptz,
  created_at    timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_delib_esc_open ON deliberation_escalation (resolved, created_at);

CREATE TABLE IF NOT EXISTS deliberation_redline_trigger (
  trigger_id bigserial PRIMARY KEY,
  kind       text NOT NULL CHECK (kind IN ('doctrine_file','antileakage_column')),
  pattern    text NOT NULL,
  source     text NOT NULL,
  note       text,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (kind, pattern)
);

-- MVP 兩臂基準平表(P1 產物,已有 12 列真資料;P2 三表接棒後保留為冒煙帳,不刪不改)
CREATE TABLE IF NOT EXISTS deliberation_benchmark (
  bench_id        bigserial PRIMARY KEY,
  run_at          timestamptz NOT NULL DEFAULT now(),
  arm             text NOT NULL CHECK (arm IN ('single_shot','engine')),
  model_tag       text NOT NULL,
  task_class      text NOT NULL CHECK (task_class IN ('schema','quant','doc')),
  n_tasks         int  NOT NULL,
  n_correct       int  NOT NULL,
  n_false_confirm int  NOT NULL,
  n_abstain       int  NOT NULL,
  detail          jsonb NOT NULL,
  git_sha         text NOT NULL
);
```

### 3.2 既有表 ALTER DDL(全文)

> 執行順序:§3.3 之 `deliberation_run/_task/_lens` 須先建(FK 目標)。**資料安全依據(修訂——claim 已有 77 列,非舊稿之 0 列)**:以下變更僅「枚舉增值、新增可空欄、放寬 NOT NULL」,零資料回填、零收窄;DROP+ADD CONSTRAINT 於同一交易內執行,遷移前後各跑 `--verify` 快照對照。**migrate 執行避開 pg_dump 時段**(ACCESS EXCLUSIVE 鎖風暴,CLAUDE #30)。

```sql
-- (A) deliberation_claim:接上引擎維度(居所雙軌 session|run、回合、鏡、去重、嚴重度)
ALTER TABLE deliberation_claim
    ADD COLUMN IF NOT EXISTS run_id    bigint  REFERENCES deliberation_run(run_id)   ON DELETE CASCADE,
    ADD COLUMN IF NOT EXISTS task_id   bigint  REFERENCES deliberation_task(task_id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS round_no  integer NOT NULL DEFAULT 0 CHECK (round_no >= 0),  -- 模式5
    ADD COLUMN IF NOT EXISTS lens_id   bigint  REFERENCES deliberation_lens(lens_id),     -- 模式3(perspective 文字欄保留,引擎雙寫 perspective=lens_name 相容 MVP)
    ADD COLUMN IF NOT EXISTS dedup_key text,   -- §2.1.5 確定性導出(sha256+行號桶化);「新發現」的機械定義
    ADD COLUMN IF NOT EXISTS severity  text CHECK (severity IN ('high','medium','low'));

-- 居所雙軌:MVP/計劃審議走 session、引擎走 run;至少居其一
ALTER TABLE deliberation_claim ALTER COLUMN session_id DROP NOT NULL;
ALTER TABLE deliberation_claim ADD CONSTRAINT deliberation_claim_home_check
    CHECK (session_id IS NOT NULL OR run_id IS NOT NULL);

-- verifier 枚舉 +'pytest'(第 5 oracle;沙箱=§2.2.4,DDL 只開名額)
ALTER TABLE deliberation_claim DROP CONSTRAINT deliberation_claim_assigned_verifier_check;
ALTER TABLE deliberation_claim ADD CONSTRAINT deliberation_claim_assigned_verifier_check
    CHECK (assigned_verifier IN ('information_schema','import_isolation','file_grep',
                                 'db_query','pytest','human_claude','none'));

-- status +'discarded'(模式2 多數決之唯一合法出口:triage 資源分配、非真理裁決;
--  機械鎖不動:confirmed/refuted 仍唯確定性 verdict 可寫,LLM 票絕無此權)
ALTER TABLE deliberation_claim DROP CONSTRAINT deliberation_claim_status_check;
ALTER TABLE deliberation_claim ADD CONSTRAINT deliberation_claim_status_check
    CHECK (status IN ('pending','confirmed','refuted','undecidable','escalated','discarded'));

-- 「新發現」機械化:同 run 內 dedup_key 撞鍵=非新(模式5 停機判準的資料基礎)
CREATE UNIQUE INDEX IF NOT EXISTS ux_delib_claim_run_dedup
    ON deliberation_claim(run_id, dedup_key)
    WHERE run_id IS NOT NULL AND dedup_key IS NOT NULL;
CREATE INDEX IF NOT EXISTS ix_delib_claim_run ON deliberation_claim(run_id, status)
    WHERE run_id IS NOT NULL;

-- (B) deliberation_verdict:記「哪個引擎 task 跑的 oracle」(審計);
--  刻意不加 agent_call_id——verdict 是確定性工具輸出,LLM 呼叫無權產 verdict(機械鎖延伸)
ALTER TABLE deliberation_verdict
    ADD COLUMN IF NOT EXISTS task_id bigint REFERENCES deliberation_task(task_id) ON DELETE SET NULL;

-- (C) deliberation_session:加心跳欄(§7.4 watchdog;該節既定、DDL 收容於此)
ALTER TABLE deliberation_session ADD COLUMN IF NOT EXISTS heartbeat_at timestamptz;

-- (D) deliberation_escalation / _redline_trigger / _benchmark:零 ALTER(結構原樣沿用)。
--  redline 種子「版本漂移」缺陷(trigger_id=7 綁 docs/系統架構大憲章_v1.39.0.md,而 docs 現行
--  =v1.40.0——漂移已真實發生,本日 ls+psql 實證)屬種子資料修正非結構變更 → §3.5 seed script
--  重建 glob 版(守 #12:改 writer 重建、不手 patch)。
```

### 3.3 新表 DDL 全文(13 張,依建表順序)

```sql
-- ============ 3.3.1 模型檔位(需求 b;#29b:換模=改一列、零改碼) ============
CREATE TABLE IF NOT EXISTS deliberation_model_profile (
    tier          text PRIMARY KEY,                    -- 'fast'/'deep'/'deep_think'…(可增列,不設枚舉 CHECK=未來任意模型)
    model_tag     text NOT NULL,                       -- Ollama per-request model 欄位值
    think         boolean NOT NULL DEFAULT false,      -- 實測成本 ~7x:39.7s vs 5.5s(同題)
    options       jsonb   NOT NULL DEFAULT '{}'::jsonb, -- temperature/seed/top_k/num_predict/num_ctx;
                                                        -- 裁決步須顯式 temperature=0+seed(8b 預設 temperature=0.6,不覆蓋=不可重現,實測 /api/show)
    timeout_s     integer NOT NULL DEFAULT 300 CHECK (timeout_s > 0),
    active        boolean NOT NULL DEFAULT false,
    verified_at   timestamptz,                         -- 實測回填時戳(#9)
    verified_note text,                                -- 實測數字全文
    created_at    timestamptz NOT NULL DEFAULT now(),
    CHECK (active = false OR verified_at IS NOT NULL)  -- 機械鎖:未實測檔位禁路由
);

-- ============ 3.3.2 引擎參數(#29b:判準魔數住 DB、不 hardcode) ============
CREATE TABLE IF NOT EXISTS deliberation_engine_config (
    config_key   text PRIMARY KEY,
    config_value jsonb NOT NULL,
    description  text  NOT NULL,
    updated_at   timestamptz NOT NULL DEFAULT now()
);

-- ============ 3.3.3 視角鏡庫(模式3;prompt 住 DB #29b;model_tier+options_override=路由與步級取樣之唯一承載,§2.3) ============
CREATE TABLE IF NOT EXISTS deliberation_lens (
    lens_id          bigserial PRIMARY KEY,
    lens_name        text NOT NULL UNIQUE,             -- 'skeptic_correctness'/'skeptic_antileakage'/'critic_completeness'…
    failure_mode     text NOT NULL,                    -- 此鏡專守的單一失效模式(一鏡一模式)
    task_kinds       text[] NOT NULL                   -- 此鏡可服務的任務種類(⊆ task.task_kind 枚舉)
                     CHECK (task_kinds <@ ARRAY['draft','skeptic','verify','refine','judge_propose',
                                                'judge_score','synthesize','completeness','aggregate',
                                                'benchmark_arm']::text[]),
    prompt_prefix    text NOT NULL,                    -- 固定共用前綴(prompt cache 實測生效)
    prompt_template  text NOT NULL,                    -- 變動尾段;佔位符 {target}/{evidence}/{claims}
    output_schema    jsonb,                            -- Ollama format= JSON schema;NULL=自由文本
    model_tier       text NOT NULL DEFAULT 'fast' REFERENCES deliberation_model_profile(tier),
    options_override jsonb NOT NULL DEFAULT '{}'::jsonb, -- 步級取樣覆蓋(如 skeptic temperature=0.7);merge=profile⊕此欄⊕逐call seed
    author           text NOT NULL DEFAULT 'human_curated'
                     CHECK (author IN ('human_curated','claude_teacher')),  -- 隔離防線 3
    version          integer NOT NULL DEFAULT 1,
    active           boolean NOT NULL DEFAULT true,
    updated_at       timestamptz NOT NULL DEFAULT now()
);

-- ============ 3.3.4 oracle registry(模式8 參數/開關;契約實作住 verifiers.py=code;名字集 ⊆ claim.assigned_verifier 枚舉,--verify 驗一致) ============
CREATE TABLE IF NOT EXISTS deliberation_oracle (
    oracle_name text PRIMARY KEY,                      -- 'information_schema'/'import_isolation'/'file_grep'/'db_query'/'pytest'
    kind        text NOT NULL CHECK (kind IN ('readonly_db','readonly_fs','inprocess','subprocess')),
    invocation  jsonb NOT NULL,                        -- {module,function} 或 {argv_template};現行 4 oracle=verifiers.py in-process
    is_readonly boolean NOT NULL,                      -- pytest=false(執行級;沙箱論證 §2.2.4)
    sandbox     jsonb NOT NULL DEFAULT '{}'::jsonb,    -- {timeout_s, cwd, network:false, allow_paths, deny_paths};pytest 必填
    active      boolean NOT NULL DEFAULT true,
    note        text
);

-- ============ 3.3.5 引擎執行實例(模式1/10;1 run = 1 標的 × 1 劇本) ============
CREATE TABLE IF NOT EXISTS deliberation_run (
    run_id          bigserial PRIMARY KEY,
    run_kind        text NOT NULL
                    CHECK (run_kind IN ('code_review','doc_consistency','plan_completeness',
                                        'data_qa','retrieval_adjudication','benchmark','dogfood')),
    target_ref      text NOT NULL,                     -- 標的:檔路徑/git ref/table 名/benchmark case ref
    target_sha256   char(64),                          -- 標的凍結指紋;resume 時比對,漂移即 loud fail
    session_id      text REFERENCES deliberation_session(session_id) ON DELETE SET NULL,  -- MVP/計劃審議相容掛勾(可 NULL)
    playbook        text NOT NULL,                     -- 'skeptic_majority'/'judge_panel'/'draft_attack_refine'/'single_shot'(基準臂)
    config_snapshot jsonb NOT NULL,                    -- 啟動時凍結 engine_config+model_profile+lens 版本(#10;跑到一半改 config 不影響已跑)
    status          text NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending','running','paused','done','failed','aborted')),
    stop_reason     text,                              -- 'dry_k_reached'/'round_max'/'user_abort'/錯誤摘要
    rounds_done     integer NOT NULL DEFAULT 0,
    heartbeat_at    timestamptz,                       -- §7.4 watchdog(每 step 更新)
    created_at      timestamptz NOT NULL DEFAULT now(),
    started_at      timestamptz,
    finished_at     timestamptz
);
CREATE INDEX IF NOT EXISTS ix_delib_run_status ON deliberation_run(status, created_at);

-- ============ 3.3.6 原子任務(模式10 resume 單位;冪等鍵=引擎確定性組鍵) ============
CREATE TABLE IF NOT EXISTS deliberation_task (
    task_id         bigserial PRIMARY KEY,
    run_id          bigint  NOT NULL REFERENCES deliberation_run(run_id) ON DELETE CASCADE,
    round_no        integer NOT NULL DEFAULT 0 CHECK (round_no >= 0),
    task_kind       text NOT NULL
                    CHECK (task_kind IN ('draft','skeptic','verify','refine','judge_propose','judge_score',
                                         'synthesize','completeness','aggregate','benchmark_arm')),
    lens_id         bigint REFERENCES deliberation_lens(lens_id),
    item_ref        text,                              -- 逐項 pipeline 的項錨(diff hunk / 文件段 / claim 批次)
    idempotency_key text NOT NULL,                     -- 如 'r2:skeptic:correctness:hunk3'
    status          text NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending','running','done','failed','skipped')),
    attempt         integer NOT NULL DEFAULT 0,        -- 逾時/失敗→requeue ≤2 次(§7.2;不改 ollama.py 誠實 raise)
    payload         jsonb,
    result          jsonb,                             -- 含 dup_hit 計數(§2.1.5 重複率統計)
    error           text,
    created_at      timestamptz NOT NULL DEFAULT now(),
    finished_at     timestamptz,
    UNIQUE (run_id, idempotency_key)                   -- 重跑撞鍵=已做過,冪等跳過
);
CREATE INDEX IF NOT EXISTS ix_delib_task_resume ON deliberation_task(run_id, status)
    WHERE status IN ('pending','failed');

-- ============ 3.3.7 LLM 呼叫帳本(模式10;每 call 一列;Ollama metadata 收容——make_structured_llm_fn 現丟棄,經 with_meta 擴充取得 §4.1.1) ============
CREATE TABLE IF NOT EXISTS deliberation_agent_call (
    call_id           bigserial PRIMARY KEY,
    task_id           bigint NOT NULL REFERENCES deliberation_task(task_id) ON DELETE CASCADE,
    model_tag         text NOT NULL,                   -- 實際命中模型(非 tier 名;#1 可溯源)
    endpoint          text NOT NULL DEFAULT 'chat' CHECK (endpoint IN ('generate','chat')),
    think             boolean NOT NULL,
    options           jsonb NOT NULL,                  -- 生效取樣參數快照(temperature/seed/num_ctx → 可重現)
    format_schema     jsonb,                           -- 該次要求之 JSON schema(模式7);NULL=純文本
    prompt_sha256     char(64) NOT NULL,
    prompt_text       text NOT NULL,                   -- 全文入帳(審計+蒸餾素材;秘密由 §2.2.3 denylist 擋在上游);住 deliberation_*,絕不入 knowledge_*
    response_text     text,
    parsed            jsonb,                           -- schema 驗證通過後的結構化結果
    parse_ok          boolean,
    schema_retry_no   integer NOT NULL DEFAULT 0,      -- 模式7 有界重試之第 n 次(上限=engine_config.schema_retry_max)
    status            text NOT NULL
                      CHECK (status IN ('ok','schema_fail','timeout','conn_error','http_error')),
    prompt_eval_count integer,                         -- ↓ 四欄=Ollama 回應 metadata(基準計時與成本模型之唯一料源 #9)
    eval_count        integer,
    load_duration_ms  bigint,
    total_duration_ms bigint,
    created_at        timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_delib_call_task ON deliberation_agent_call(task_id, created_at);

-- ============ 3.3.8 多數決票(模式2;票=triage 排序,非真理——絕無寫 confirmed/refuted 之權) ============
CREATE TABLE IF NOT EXISTS deliberation_vote (
    vote_id    bigserial PRIMARY KEY,
    claim_id   bigint NOT NULL REFERENCES deliberation_claim(claim_id)          ON DELETE CASCADE,
    call_id    bigint NOT NULL REFERENCES deliberation_agent_call(call_id)      ON DELETE CASCADE,  -- 每票溯 LLM 呼叫(#10)
    lens_id    bigint NOT NULL REFERENCES deliberation_lens(lens_id),
    vote       text NOT NULL CHECK (vote IN ('support','refute','undecidable')),
    rationale  text,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (claim_id, call_id)
);
-- 誠實邊界(前身 §8b 延伸):同底模多鏡錯誤相關、可能「自信地一致錯」→ 多數反駁之唯一效果=
-- claim.status→'discarded'(省 oracle/escalation 資源),列仍在帳、可人工復活;殺真 claim 之風險由基準量化。

-- ============ 3.3.9 judge panel 方案(模式4/9) ============
CREATE TABLE IF NOT EXISTS deliberation_proposal (
    proposal_id      bigserial PRIMARY KEY,
    task_id          bigint NOT NULL REFERENCES deliberation_task(task_id) ON DELETE CASCADE,
    run_id           bigint NOT NULL REFERENCES deliberation_run(run_id)   ON DELETE CASCADE,
    kind             text NOT NULL DEFAULT 'candidate' CHECK (kind IN ('candidate','synthesis')),
    proposer_lens_id bigint REFERENCES deliberation_lens(lens_id),         -- synthesis 由引擎合成時可 NULL
    call_id          bigint REFERENCES deliberation_agent_call(call_id),
    content          jsonb NOT NULL,                   -- 結構化方案(schema=lens.output_schema)
    merged_from      bigint[],                         -- synthesis:勝者+被移植亞軍優點之來源 proposal_id 陣列
    created_at       timestamptz NOT NULL DEFAULT now()
);

-- ============ 3.3.10 panel 評分(模式4;分數=可驗欄位之確定性加權和供排序,非證據——勝者方案內承重宣稱仍須走 claim→oracle 錨定) ============
CREATE TABLE IF NOT EXISTS deliberation_panel_score (
    score_id      bigserial PRIMARY KEY,
    proposal_id   bigint NOT NULL REFERENCES deliberation_proposal(proposal_id)  ON DELETE CASCADE,
    judge_lens_id bigint NOT NULL REFERENCES deliberation_lens(lens_id),
    call_id       bigint NOT NULL REFERENCES deliberation_agent_call(call_id)    ON DELETE CASCADE,
    criteria      jsonb NOT NULL,                      -- 分項 {completeness:7, risk:5, …}
    total_score   numeric(5,2) NOT NULL,
    rationale     text,
    created_at    timestamptz NOT NULL DEFAULT now(),
    UNIQUE (proposal_id, judge_lens_id, call_id)
);

-- ============ 3.3.11 基準測例(需求 d;AI/機械生成測例之唯一合法住所——絕不入 knowledge_*;測例凍結) ============
CREATE TABLE IF NOT EXISTS deliberation_benchmark_case (
    case_id        bigserial PRIMARY KEY,
    suite          text NOT NULL
                   CHECK (suite IN ('seeded_bug','doc_conflict','plan_gap','data_qa','retrieval_adjudication')),
    case_key       text NOT NULL UNIQUE,               -- 冪等鍵,如 'seeded_bug:core/db.py:flip_cmp:0007'
    is_negative    boolean NOT NULL DEFAULT false,     -- 負例(無植入)標記,G2 誤報量測用
    payload        jsonb NOT NULL,                     -- 測例本體(diff 全文 / 文件對 / question+context)
    ground_truth   jsonb NOT NULL,                     -- 植入清單或標籤(機械可比對;命中判定=確定性 scorer,禁 LLM 自評 #15)
    origin         text NOT NULL
                   CHECK (origin IN ('human_curated','claude_generated','mutation_tool','distill_import')),  -- 隔離防線 3
    gen_method     text NOT NULL,                      -- 'mutation:flip_cmp'/'conflict:number_edit'/'distill_import'
    gen_seed       bigint,                             -- 生成亂數種子(#10 可重現;distill_import 為 NULL)
    source_ref     text,                               -- 取樣來源(檔案路徑 / question_id)
    payload_sha256 char(64) NOT NULL,                  -- 測例凍結:入庫後不可改(要改=另立新 case)
    created_at     timestamptz NOT NULL DEFAULT now(),
    CHECK (btrim(case_key) <> '')
);

-- ============ 3.3.12 基準執行(一 run=1 suite×1 臂×1 seed 輪;#11 之 ≥3 trials=每臂 ≥3 個 seed_round run) ============
CREATE TABLE IF NOT EXISTS deliberation_benchmark (
    run_id        bigserial PRIMARY KEY,
    suite         text NOT NULL CHECK (suite IN ('seeded_bug','doc_conflict','plan_gap','data_qa','retrieval_adjudication')),
    arm           text NOT NULL CHECK (arm IN ('single_fast','single_think','majority_fast','engine')),
    model_tag     text NOT NULL,                       -- 實跑當下模型;engine 臂記主裁決模
    arm_config    jsonb NOT NULL DEFAULT '{}'::jsonb,  -- 該臂完整參數快照(#10:對比表兩邊都要有真實來源);GATE 拍板值(P5-1)入此
    scoring_ver   text NOT NULL DEFAULT 'v1',
    seed_round    int  NOT NULL DEFAULT 1,
    status        text NOT NULL DEFAULT 'running' CHECK (status IN ('running','done','failed','aborted')),
    heartbeat_at  timestamptz,                         -- §7.4 watchdog 用
    started_at    timestamptz NOT NULL DEFAULT now(),
    finished_at   timestamptz,
    UNIQUE (suite, arm, model_tag, scoring_ver, seed_round)
);

-- ============ 3.3.13 基準結果(逐 case;需求 d 機械證明之最小粒度) ============
CREATE TABLE IF NOT EXISTS deliberation_benchmark_result (
    result_id      bigserial PRIMARY KEY,
    run_id         bigint NOT NULL REFERENCES deliberation_benchmark(run_id) ON DELETE CASCADE,
    case_id        bigint NOT NULL REFERENCES deliberation_benchmark_case(case_id),
    engine_run_id  bigint REFERENCES deliberation_run(run_id) ON DELETE SET NULL,  -- engine 臂逐 case 之審議 run 溯源;single 臂 NULL
    raw_output     jsonb NOT NULL,                     -- 臂的結構化原始輸出(#10)
    hits           int NOT NULL DEFAULT 0,
    false_alarms   int NOT NULL DEFAULT 0,             -- 假陽性同列帳:「多找到」若靠亂槍打鳥,此欄揭穿(#15)
    misses         int NOT NULL DEFAULT 0,
    correct        boolean NOT NULL,                   -- §5.4 機械規則判定(McNemar 用)
    wall_ms        bigint,
    llm_calls      int NOT NULL DEFAULT 0,
    llm_tokens_out bigint,                             -- Σ agent_call.eval_count(成本軸;品質/成本雙軸對照)
    created_at     timestamptz NOT NULL DEFAULT now(),
    UNIQUE (run_id, case_id)                           -- case 級 resume 述詞=WHERE NOT EXISTS
);
CREATE INDEX IF NOT EXISTS ix_delib_bench_result_run ON deliberation_benchmark_result (run_id, correct);
```

### 3.4 導出檢視(derived、零狀態——能算的不落表,防帳本腐化;全計畫僅此 2 view)

```sql
-- 模式5 loop-until-dry 停機判準之料源:引擎讀「最近 K 輪 new_claims 是否全 0」(K=engine_config.loop_dry_k);
-- 「新」的機械定義=成功 INSERT(dedup 撞 ux_delib_claim_run_dedup 者不落列,天然不計)
CREATE OR REPLACE VIEW v_deliberation_round_yield AS
SELECT run_id, round_no, count(*) AS new_claims
FROM deliberation_claim
WHERE run_id IS NOT NULL
GROUP BY run_id, round_no;

-- 模式2 計票(聚合不落表,票本身已是帳;舊稿 deliberation_skeptic_tally 併入此、廢除)
CREATE OR REPLACE VIEW v_deliberation_vote_tally AS
SELECT claim_id,
       count(*)                                     AS votes,
       count(*) FILTER (WHERE vote = 'refute')      AS refutes,
       count(*) FILTER (WHERE vote = 'support')     AS supports,
       count(*) FILTER (WHERE vote = 'undecidable') AS undecidables
FROM deliberation_vote
GROUP BY claim_id;
```

### 3.5 冪等種子(#29b bootstrap;`ON CONFLICT … DO NOTHING/UPDATE`,SSOT=DB 表)

| 表 | 種子 | 依據 |
|---|---|---|
| `deliberation_model_profile` | `('deep','qwen3:8b',think=false,options={"temperature":0,"seed":42,"num_ctx":4096},timeout_s=300,active=true,verified_at='2026-07-10',verified_note='2.31/5.96GB in VRAM, 6.6-7.7 tok/s, cold load 9.24s')`;`('deep_think','qwen3:8b',think=true,…,verified_note='39.7s/題 vs 5.5s')`;`('fast','qwen3:4b',think=false,options={"temperature":0,"num_predict":512},active=true,verified_at='2026-07-10',verified_note='已安裝(/api/tags);MVP 端到端+基準 12 列實跑(deliberation_benchmark);tok/s、size_vram 待 probe 補量')` | **兩模皆已安裝且 4b 已實戰**(MVP 全以 4b 跑,deliberate.py 預設 --model qwen3:4b);效能數字(tok/s、全 GPU 判定)由 `probe_deliberation_models.py` 補量回填 verified_note(#9) |
| `deliberation_engine_config` | `loop_dry_k=2`、`round_max=6`(保險絲)、`skeptic_n=3`、`majority_arm_n=3`(§5.3 majority_fast 臂票數,與 skeptic_n 對齊)、`vote_kill_rule={"min_votes":3,"refute_ratio":1.0}`(全票反駁才 discard,殺錯成本>省時故保守)、`schema_retry_max=2`、`refine_topk=5`、`prompt_token_budget=3000`(runner `-c 4096` 實測,留生成餘裕;超過→分塊)、`keep_alive="30m"`(冷載稅 9.24s 實測)、`bench_trials_min=3`(#11)、`pytest_enabled=false`(**D4 安全拍板後才 true**)、`requeue_max=2`、`heartbeat_stale_min=15`、`context_hard_cap=3200` | 魔數全數住 DB;調參=UPDATE 一列(操作值依 #27 護欄內調整) |
| `deliberation_oracle` | 5 列:4 真 oracle(kind:`information_schema`/`db_query`=readonly_db、`file_grep`=readonly_fs、`import_isolation`=**inprocess**(verifiers.py 實作,in-process check_isolation() @ import_isolation.py:160))+ `pytest`(kind=subprocess、is_readonly=false、active=false 隨 pytest_enabled、sandbox 必填 timeout/network:false/allow_paths/deny_paths) | 前身 H1 裁決(guard/effective_t_hac/sql_reconcile=偽 oracle,不入列)直接繼承;實作現況=verifiers.py |
| `deliberation_lens` | 初始鏡組(每鏡一失效模式):`skeptic_correctness`/`skeptic_antileakage`(與 redline 4 列 antileakage_column 對接)/`skeptic_truesign`/`skeptic_isolation`/`skeptic_reproducibility`/`skeptic_security`/`critic_completeness`/`judge_risk`/`judge_simplicity`;prompt 全文住 seed script(策展人寫,author='human_curated';**MVP 之 LENS_PROMPTS 三鏡文本遷入,deliberate.py 改讀 DB**);doctrine 檔名引用一律 glob(`docs/原則精華_v*.md`) | 模式3;#29b(現況 hardcode=違例,P3 修);script 為匯入口非 SSOT(同 manual_file adapter 先例) |
| `deliberation_redline_trigger` | **glob 版重建**(修版本漂移):seed 冪等改寫 `docs/原則精華_v1.8.0.md`→`docs/原則精華_v*.md`、`docs/系統架構大憲章_v1.39.0.md`→`docs/系統架構大憲章_v*.md`、`docs/系統核心思想_v1.5.0.md`→`docs/系統核心思想_v*.md`(`pattern` 欄語意本即檔路徑 glob,結構零改);4 列 antileakage_column 原樣保留 | **漂移已真實發生**(trigger_id=7 綁 v1.39.0、docs 現行=v1.40.0,本日實證——即 §8.1 P1 真陽性);守 #12(seed script 重建、非手動 UPDATE) |

### 3.6 遷移、冪等與本節驗收

- **`scripts/migrate_deliberation_ddl.py`(已落地,擴充)**:模式實名=`--run`(冪等施作)/`--verify`(斷言);無參數印指令矩陣+現況(#29a,已落地)。`--run` 依序=既有 6 表(已在,IF NOT EXISTS 略過)→ §3.3 新 13 表+§3.4 2 view → §3.2 ALTER → §3.5 種子;全程 `IF NOT EXISTS`/`ON CONFLICT` 冪等,重跑安全。
- **`--verify`(確定性驗收,全綠才算過)**:① **19 表**(6 既有+13 新)+2 view 存在且 CHECK/FK/UNIQUE 與本節逐字一致(`pg_get_constraintdef` 對照);② §3.0 跨界 FK 稽核 query 回 0 列;③ `deliberation_oracle.oracle_name` 集合=verifiers.ORACLES∪{'pytest'} 且 ⊆ claim `assigned_verifier` 枚舉、`lens.task_kinds` ⊆ task `task_kind` 枚舉;④ `model_profile` 無 `active=true AND verified_at IS NULL`(CHECK 已擋,雙驗);⑤ 蒸餾軟連結孤兒稽核:`advisor_distill_question WHERE topic_source='deliberation_engine'` 之 `topic_ref` 均存在於 `deliberation_claim`;⑥ redline `doctrine_file` pattern 之 glob 展開於 docs/ 現存檔非空(防再漂移)。
- **帳本鐵則(驗收條款)**:**DB=唯一 ledger;一切檔案工件(SFT jsonl/報告/基準語料檔)一律可冪等重生自 DB**——`validated=171 但 sft.jsonl 實體不存在`之工件脫鉤已實際發生(本日 find 覆核),本引擎不允許重演。
- **執行時段**:migrate 避開 `pg_dump`(ACCESS EXCLUSIVE 鎖風暴實證,CLAUDE #30);新表建成後納入 #30/#31 dump 清單。

**模式↔表覆蓋矩陣(v1.39.0 完備性自證)**:

| ultracode 模式/需求 | 承載結構 |
|---|---|
| 1 pipeline / fan-out | `run.playbook` + `task(idempotency_key, item_ref)` |
| 2 對抗多數決 | `vote` + `v_deliberation_vote_tally` + claim status `'discarded'`(機械鎖不動) |
| 3 視角多樣鏡 | `lens(failure_mode 每鏡一失效模式, prompt 住 DB, model_tier+options_override)` |
| 4 judge panel | `proposal(candidate/synthesis, merged_from)` + `panel_score` |
| 5 loop-until-dry | claim `round_no`+`dedup_key` + `ux_delib_claim_run_dedup` + `v_deliberation_round_yield` + `loop_dry_k` |
| 6 完整性 critic | `task_kind='completeness'` + claim `category='coverage'`(既有枚舉) |
| 7 結構化輸出+重試 | `lens.output_schema` + `agent_call(format_schema, parse_ok, schema_retry_no)` |
| 8 工具實證錨定 | 既有 `claim(anchor, assigned_verifier)`+`verdict(evidence CHECK)`(**已落地**)+ `oracle` registry |
| 9 draft→attack→refine | `task_kind` 枚舉 + `proposal.kind='synthesis'` |
| 10 resume-safe 帳本 | `run(config_snapshot, target_sha256, heartbeat_at)` + `task(UNIQUE 冪等鍵)` + `agent_call`(Ollama metadata 收容) |
| 需求 b 模型策略 | `model_profile`(未實測禁啟用 CHECK)+ `lens.model_tier` 路由 |
| 需求 d 基準 | `benchmark_case`(凍結+origin CHECK)+`benchmark_run`(seed_round≥3)+`benchmark_result`(逐 case);MVP 平表 `deliberation_benchmark` 保留為 P1 冒煙帳 |
| 需求 e 蒸餾迴路 | **零新表**(§6.2 裁決):軟連結=`advisor_distill_question.topic_source/topic_ref`(隔離防線 4);絕不回流預測管線 |

## 4. python 程式規畫

> 本節規畫全部程式檔。**表名/欄名以 §3 DDL 為準(本節零 DDL)**;模組分解以 §2.0 表為準(與本節同一套);所有程式**全程本地執行、零 Claude token**(CLAUDE #28),AI 產物只落 `deliberation_*` 表、絕不入 `knowledge_*`。**落地現況已折入**:P1 MVP 已 commit(24e87a3),本節區分「已落地(零改動/小擴)」與「新建」。

### 4.0 檔案總覽與全域慣例

| # | 檔案 | 狀態 | 角色 | 複用/擴充標記(#29c) |
|---|------|------|------|----------------|
| 1 | `src/augur/advisor/ollama.py` | **已落地,小擴** | `make_structured_llm_fn`(:70)加 `with_meta` 選參回 Ollama metadata | `make_llm_fn`(:122)/`strip_think`(:55)/`_assert_local_host`(:29)零改動 |
| 2 | `src/augur/audit/import_isolation.py` | **既有,小擴** | 加 `DELIB_LITERALS` 三擴(禁預測管線觸 deliberation) | 同構樣板=`DISTILL_LITERALS`(:41)+`SCAN_DISTILL`(:45)+接線(:166) |
| 3 | `src/augur/deliberation/verifiers.py` | **已落地** | 4 真 oracle+`verify_claim` 機械鎖(全系統唯一寫 confirmed 處) | P4 擴 pytest oracle;W2 補 file_grep denylist(§2.2.3 實查缺口) |
| 4 | `src/augur/deliberation/engine.py` | 新(P3) | run/round 狀態機(模式 1/5/9);自 deliberate.py 抽出 | — |
| 5 | `src/augur/deliberation/llmroute.py` | 新(P3) | 檔位解析+結構化呼叫包裝(模式 7) | 包裝 #1 之 make_structured_llm_fn |
| 6 | `src/augur/deliberation/lens.py` | 新(P3) | lens 庫 DB 載入+prompt 組裝(模式 3) | 取代 deliberate.py 內 hardcode LENS_PROMPTS(#29b) |
| 7 | `src/augur/deliberation/consensus.py` | 新(P3) | 多數決聚合(模式 2)+panel 合成(模式 4) | fail-closed 三式移植自 guard |
| 8 | `src/augur/deliberation/critic.py` | 新(P3) | 完整性 critic(模式 6)+dry 判定(模式 5) | — |
| 9 | `src/augur/deliberation/ledger.py` | 新(P3) | run/task/claim 帳本 CRUD+格式閘+resume 述詞(模式 10) | resume 範本=teacher.py:86-106;DB 層=`augur.core.db` |
| 10 | `scripts/migrate_deliberation_ddl.py` | **已落地,擴充** | §3 全部 DDL 唯一執行器(`--run`/`--verify`) | 既有 6 表段零改動,疊加 13 新表+ALTER+種子 |
| 11 | `scripts/seed_deliberation_lens.py` | 新 | lens 庫+model_profile+engine_config+redline glob 種子(#29b) | curated 常數慣例=`generate_questions.py:36-87` |
| 12 | `scripts/probe_deliberation_models.py` | 新 | 模型檔位效能實測(tok/s、size_vram、換檔稅)回填 model_profile | 最小單位探測紀律(#25) |
| 13 | `scripts/deliberate.py` | **已落地 MVP,P3 擴** | 引擎 CLI 入口(現況:單 lens 端到端+L1-L4 機械補強層) | `make_structured_llm_fn` 已接;P3 加 run/task/resume/mock-llm |
| 14 | `scripts/benchmark_deliberation.py` | **已落地 MVP(未 track,W2 收編 commit),P2 擴** | 基準 harness 單支多態(需求 d) | 廢名:`build_benchmark_corpus/generate_benchmark_cases/run_benchmark/report_benchmark_verdict`(§3.0 裁決表) |
| 15 | `scripts/map_deliberation_to_distill.py` | 新(P5) | 蒸餾映射器(需求 e;§6.4 為規格 SSOT) | 廢名:`bridge_deliberation_distill.py`/`export_deliberation_sft.py` |
| 16 | `scripts/report_deliberation_verdict.py` | 新(P3) | 跨 session/run 人讀裁決報告+escalation 佇列 | MVP 單 session 報告已內建 `deliberate.py --report`,本支收攏共用函式 |
| 17 | `scripts/watch_deliberation.py` | 新(P6 前) | watchdog(唯讀+stale 標記) | 規格與指令矩陣 SSOT=§7.4 |

**全域慣例(每支 CLI script 一體適用)**:
- `import _bootstrap` 於 `import augur` 前(#29a);任何 cwd 直接 `python scripts/X.py` 可跑;無參數=印指令矩陣+唯讀現況後 exit 0(graceful;已落地三支皆如此)。
- 標頭=白話 docstring+守原則 #+指令矩陣(#18/#29d)。exit code:`0`=成功、`1`=GATE 未過/驗證失敗、`2`=用法錯誤。
- 長跑走 nohup/systemd 背景慣例;逾時/失敗→task 記 `failed` 可 requeue(≤2 次),**不改 `ollama.py` 的誠實 raise 語意**(job 狀態機包在引擎層)。
- 依賴方向單向:`deliberation` → `advisor.ollama` + `core.db`(僅此二點;實碼現況即如此);`advisor` 絕不 import `deliberation`;預測管線觸 deliberation 由 #2 之 DELIB_LITERALS 機械擋下。

---

### 4.1 既有檔擴充(#29c,兩處、皆最小 diff)

#### 4.1.1 `src/augur/advisor/ollama.py` — `make_structured_llm_fn` 加 `with_meta`

**現況實證(已落地,取代舊稿「加 make_chat_fn」之規劃)**:`make_structured_llm_fn(schema, model=None, base=None, timeout=None, retries=1, options=None, think=False)` @ :70——POST `/api/chat`+`format=<schema>`、`json.loads`+required-keys 檢查、失敗錯誤回饋入 prompt 有界重試(≤retries 再敗 raise)、`num_predict` 預設 512(80 tok 截斷/300 tok 成立實測)、G3 本機 host 斷言(:29)。**唯一殘缺**:Ollama 回應 metadata(eval_count/prompt_eval_count/total_duration/load_duration)被丟棄——帳本(§3.3.7)與基準計時(§5)依賴。

**擴充(最小 diff)**:加選用參數 `with_meta=False`;True 時回 `(obj, meta)`,meta=`{eval_count, prompt_eval_count, total_duration, load_duration, done_reason, model}`。**不改**:既有簽名預設行為、`make_llm_fn`(:122)、`strip_think`(:55)、重試語意(連線層有界、HTTP/逾時立即 raise,#24 不風暴)。

**驗收**:既有呼叫方(deliberate.py/advisor 全家)行為零回歸(預設 with_meta=False);`with_meta=True` 以最小 schema `{verdict:boolean, reason:string}` 實測回 (dict, meta) 且 meta 四計時欄非空。

#### 4.1.2 `src/augur/audit/import_isolation.py` — 加 `DELIB_LITERALS`

**住所修正(實機 find 定案)**:本檔住 `src/augur/audit/`(**非舊稿之 scripts/**);錨=`FORBIDDEN`(:33)/`DISTILL_LITERALS`(:41)/`SCAN_DISTILL`(:45)/`check_isolation`(:160,distill 接線 :166)/`__main__`(:184)。照 DISTILL 同構三擴:`FORBIDDEN` 加 `"augur.deliberation"`、字面量掃描加 `deliberation_` 表名前綴(掃描範圍=預測管線 package)、`check_isolation` 接線一行。

**驗收**:`python -m augur.audit.import_isolation` exit 0(現行碼無違例);負向測試:任一預測管線檔暫插 `import augur.deliberation` 或 `deliberation_claim` 字面量須 exit 非 0(測後移除)。此擴充使 `import_isolation` oracle(in-process `check_isolation()`,verifiers.py 實作)自動涵蓋審議層隔離。

---

### 4.2 library:`src/augur/deliberation/`(1 既有+6 新;命名皆領域名詞,#18;分解=§2.0 同一套)

#### 4.2.1 `verifiers.py` — 確定性驗證器(模式 8;**已落地,規格=實碼**)

`ORACLES` 閉集+`run_verifier(verifier, anchor) -> (verdict, evidence)`+`verify_claim(claim_id)`(唯一寫 confirmed 處;undecidable→escalated+開 escalation;verifier∈{human_claude,none}→直接 escalate;冪等:重跑=追加 verdict、status 收斂)。anchor 契約=§2.2.1 表。**待辦**:P4 擴 `pytest`(§2.2.4 約束五條,total 開關 `pytest_enabled`);W2 補 file_grep 秘密 denylist(§2.2.3)+db_query 改 `deliberation_ro` 角色連線(§2.2.2)。

#### 4.2.2 `engine.py` — run/round 狀態機(模式 1/5/9;新)

```python
def open_run(conn, run_kind, target_ref, playbook) -> int      # config_snapshot 凍結+target_sha256
def resume_run(conn, run_id) -> RunState                        # task 述詞驅動;target 漂移即 loud fail
def advance(conn, run_id) -> str                                # DRAFT→ATTACK→VERIFY→REFINE 轉移;回新狀態
def is_dry(conn, run_id, k) -> bool                             # 讀 v_deliberation_round_yield 連續 k 輪 0 新
```

輪內流程(每 round):①(draft)各 lens 序列 fan-out 產結構化 claims(必帶錨+verifier,否則 ledger reject)→②(attack)跨鏡投票初篩(consensus;只殺/降級不升)→③(verify)存活 claims 逐一 `verify_claim`→confirmed/refuted/escalated→④(refine/critic)`critic.find_gaps` 產下輪工作項→⑤ `is_dry(k)` 判收斂(`round_max` 硬保險絲)。MVP 期此邏輯居 deliberate.py(單輪版),P3 抽出成本模組。

#### 4.2.3 `llmroute.py` — 檔位解析+結構化呼叫(模式 7;需求 b/f;新)

```python
def resolve(conn, lens: Lens) -> Route          # lens.model_tier ⋈ deliberation_model_profile;merge options=profile⊕lens.options_override
def call_structured(route, prompt, schema, conn, task_id) -> tuple[dict | None, dict]
```

- 內裡=`make_structured_llm_fn(..., with_meta=True)`;每 call 落 `deliberation_agent_call`(§3.3.7,含 meta 四欄)——模式 10 最小粒度。schema 驗證失敗之有界重試由 make_structured_llm_fn 承擔(retries=engine_config.schema_retry_max);仍敗回 `(None, meta)`、帳本記 `schema_fail`、**不產生 claim**(fail-closed 寧漏勿假)。
- 可重現性:options 顯式覆蓋 temperature/seed(8b 預設 temperature=0.6 實測,不可依賴);seed=確定性導出 hash(run_id, idempotency_key)。
- CPU-only(需求 f):零分支——Ollama 自行回落 CPU,本模組僅耗時不同。排程誠實邊界:`-np 1` 物理序列化(實測)→不做 LLM 端並發;唯一並行=LLM 推理∥oracle 驗證(threading,I/O bound GIL 無礙)。

#### 4.2.4 `lens.py` — 視角鏡庫(模式 3;#29b;新)

```python
def load_lenses(conn, task_kind: str, applies_to: str = 'any') -> list[Lens]   # WHERE active AND task_kind = ANY(task_kinds)
def render_prompt(lens, target_chunk, evidence=None, claims=None) -> str       # prompt_prefix(cache 友善)+prompt_template 填佔位符
```

- prompt 組裝定式:「固定共用前綴+變動尾段」利用 prompt cache(實測生效);token 預算內建分塊(單 chunk ≤ `prompt_token_budget`,超限切塊逐塊過鏡;估算 `len(text)//3` 保守係數,以 meta.prompt_eval_count 實測校正——§7.6 護欄)。
- 遷移:MVP `LENS_PROMPTS` 三鏡文本由 `seed_deliberation_lens.py` 遷入 DB,deliberate.py 改經本模組讀取。

#### 4.2.5 `consensus.py` — 多數決+panel 合成(模式 2/4;新)

```python
def tally_votes(conn, claim_id) -> VoteTally                    # 讀 v_deliberation_vote_tally
def apply_kill_rule(conn, claim_id, rule) -> str                # 'discarded' | 'keep';規則=engine_config.vote_kill_rule
def synthesize_panel(conn, run_id, proposals, scores) -> int    # 勝者+移植亞軍「已確認優點」→ proposal(kind='synthesis')
```

- 多數決僅作用於 LLM 意見層(triage):產出只有 `discarded`(省 oracle/escalation 資源;列仍在帳可復活)或送驗,**永不產生 confirmed**(fail-closed 白名單制直譯自 guard);升 confirmed 唯 `verifiers.verify_claim`。
- 同底模錯誤相關之誠實註記(前身 §10.2)寫入模組 docstring 與 §1.4 互引:多數決=降噪器,不是證據。
- panel:機械評分表(rubric 可驗項=oracle 驗證後之確定性加權和)+LLM 填表員;分數落 `deliberation_panel_score`,LLM 意見對分數零直接貢獻。

#### 4.2.6 `critic.py` — 完整性 critic+dry 判定(模式 5/6;新)

```python
def mechanical_coverage(artifact) -> CoverageMap    # 零 LLM:表↔DDL、script↔矩陣、diff hunk 覆蓋圖
def residual_critic(conn, run_id, coverage_map) -> list[dict]   # LLM 殘差:「還缺什麼」→ 下輪 pending claims(仍須錨+verifier)
```

critic 輸出也是 claim、同受機械鎖;幻想缺口無法驗證即 escalate,不污染迴圈。`k`/`round_max` 住 engine_config(#29b)。

#### 4.2.7 `ledger.py` — 帳本(模式 10;新)

```python
def insert_claim(conn, run_id, task_id, round_no, lens, claim) -> int | None   # 格式閘:anchor 非空+格式 regex+verifier∈閉集;dedup 撞鍵回 None 計 dup_hit
def next_tasks(conn, run_id) -> list[Task]                                     # WHERE status IN ('pending','failed') 述詞
def record_call(conn, task_id, route, prompt, result, meta) -> int
def mark_task(conn, task_id, status, result=None, error=None) -> None          # 逐列 commit(distill 範本同款)
```

全 CRUD 只認 `deliberation_*` 表(表名字面量集中本檔,供 §4.1.2 掃描白名單);**DB 為唯一 ledger、檔案工件可冪等重生**(驗收條款)。

---

### 4.3 CLI scripts(每支:用途/CLI 矩陣/I/O/驗收;已落地者列實錄矩陣+擴充矩陣)

#### 4.3.1 `scripts/migrate_deliberation_ddl.py` — §3 全部 DDL 唯一執行器(**已落地,擴充**)

**用途**:既有 6 表 DDL 已收編(commit 24e87a3);本計畫擴充=疊加 §3.3 新 13 表+§3.4 2 view+§3.2 ALTER+§3.5 種子,`--verify` 擴至 §3.6 六項檢查。

```
python scripts/migrate_deliberation_ddl.py            # 印指令矩陣+19 表現況(唯讀)          [已落地,現印 6 表]
python scripts/migrate_deliberation_ddl.py --run      # 冪等施作:既有 6 表→新 13 表+2 view→ALTER→種子
python scripts/migrate_deliberation_ddl.py --verify   # §3.6 ①-⑥ 全綠 exit 0,否則 exit 1
```

| 方向 | 介面 | 內容 |
|---|---|---|
| 輸入 | 檔內常數 | §3 目標 DDL 全文(git 住所) |
| 輸入 | DB | 現行結構(information_schema/pg_constraint) |
| 輸出 | DB | **19 表+2 view**+ALTER 欄+種子(修訂舊稿「11 表」「18 表」兩說) |
| 輸出 | stdout | 差異/施作清單 |

**驗收**:`--run` 後 `--verify` exit 0;連跑兩次 `--run` 無錯無變(冪等);執行避開 pg_dump 時段(#30)。

#### 4.3.2 `scripts/seed_deliberation_lens.py` — lens/model_profile/engine_config/redline 種子(新)

**用途**:§3.5 全部種子之 writer(curated 文本住檔內常數,人審非 AI 生成;DB 為 SSOT #29b)。含 MVP `LENS_PROMPTS` 遷入、redline glob 重建(修 v1.39.0→v1.40.0 已發生之漂移,#12 seed 重建非手 patch)。

```
python scripts/seed_deliberation_lens.py              # 印指令矩陣+種子現況 diff(唯讀)
python scripts/seed_deliberation_lens.py --check      # 檔內種子 vs DB 差異,只報不寫(exit 1=有漂移)
python scripts/seed_deliberation_lens.py --apply      # ON CONFLICT DO UPDATE 冪等 upsert(lens 依 lens_name、config 依 config_key、redline 依 (kind,pattern))
python scripts/seed_deliberation_lens.py --apply --only lens|config|profile|redline
```

I/O:檔內常數→`deliberation_lens/_model_profile/_engine_config/_redline_trigger`。**驗收**:`--apply` 後 lens ≥9 列、config ≥14 鍵;redline doctrine_file 全為 glob 且展開命中 docs/ 現存檔;連跑冪等;每列 `output_schema` 可被 llmroute 淺驗證器解析;`grep -rn` 引擎 code 零 hardcode prompt 本文(#29b)。

#### 4.3.3 `scripts/probe_deliberation_models.py` — 檔位效能實測回填(新;需求 b 前置)

**用途(修訂:兩模皆已安裝,`/api/tags` 實查——本支不再負責安裝,只負責量測)**:對指定模型最小單位探測(#25):tok/s(3 次取中位,#11)、load_duration、`size_vram==size` 全 GPU 判定、think on/off 對照、兩模交替之逐出/重載稅;實測值 UPDATE `deliberation_model_profile.verified_at/verified_note`。

```
python scripts/probe_deliberation_models.py                                 # 印指令矩陣+profile 現況
python scripts/probe_deliberation_models.py --probe qwen3:4b                # 單模型量測(4b 全 GPU 判定=待驗前提,不得假設)
python scripts/probe_deliberation_models.py --probe qwen3:8b
python scripts/probe_deliberation_models.py --probe-swap qwen3:4b qwen3:8b  # 交替載入實測換檔稅(8b 冷載 9.24s 為基線)
python scripts/probe_deliberation_models.py --write-profile                 # 實測值回填 model_profile(#9)
```

I/O:Ollama `/api/chat`(經 make_structured_llm_fn with_meta)/`/api/ps`/`/api/show`+`/usr/lib/wsl/lib/nvidia-smi`(絕對路徑,PATH 內無)→ `deliberation_model_profile`+stdout 對照表。**驗收**:每個 active 檔位 verified_note 含實測 tok/s;4b 全 GPU 判定附 `/api/ps` 原始輸出落 log。

#### 4.3.4 `scripts/deliberate.py` — 引擎 CLI 入口(**已落地 MVP;P3 擴充**)

**現行矩陣(實錄,已實測可跑)**:

```
python scripts/deliberate.py                                        # 無參數:印矩陣+近期 session 現況(唯讀)
python scripts/deliberate.py --run --topic "驗證機率層三表就位"        # 題目式(qwen 析可驗宣稱→oracle 裁決)
python scripts/deliberate.py --run --topic "..." --target reports/x.md --lens skeptic
python scripts/deliberate.py --run --topic "..." --model qwen3:8b --max-claims 8
python scripts/deliberate.py --report <session_id>                  # 重印裁決報告(唯讀)
```

**P3 擴充矩陣(多輪引擎;既有旗標零破壞)**:

```
python scripts/deliberate.py --run-engine --profile code_review --target-kind git_diff --target "HEAD~1..HEAD"
python scripts/deliberate.py --run-engine --profile doc_consistency --target-kind file_pair --target docs/A.md,docs/B.md
python scripts/deliberate.py --run-engine --profile plan_completeness --target-kind file --target reports/xxx_plan.md
python scripts/deliberate.py --resume <run_id>                      # task 述詞驅動續跑
python scripts/deliberate.py --list-runs                            # run 帳本總覽
python scripts/deliberate.py --mock-llm --run-engine ...            # 零 LLM 煙測(oracle/帳本真管線;llm_fn=樁,advise.py llm_fn 注入同款)
python scripts/deliberate.py --max-rounds 6 --dry-k 2 ...           # 收斂參數覆蓋(預設住 engine_config)
nohup python scripts/deliberate.py --run-engine ... >> /tmp/delib_r42.log 2>&1 &   # 背景慣例(#22)
```

| 方向 | 介面 | 內容 |
|---|---|---|
| 輸入 | CLI/git/檔案 | target(diff 經 git diff;檔案經 realpath 圍欄) |
| 輸入 | DB | lens(P3 起讀 DB)/model_profile/engine_config/redline_trigger |
| 輸入 | HTTP | Ollama(經 llmroute→make_structured_llm_fn) |
| 輸出 | DB | MVP:session/claim/verdict/escalation;P3:+run/task/agent_call/vote(逐列 commit) |
| 輸出 | stdout | 每 round 摘要(claims/killed/confirmed/escalated/elapsed;#21) |
| exit | — | 0=收斂完成;1=failed(帳本留態可 --resume) |

**耗時預算(冷估 #9;MVP 實測錨:4b 單 session 6 claims 含裁決 <2 分)**:code_review 五鏡×2 輪 ≈ 10-14 次 4b/8b call+1-2 次 8b think 裁決 → 估 10-20 分/run;首個真 run 以 agent_call meta 校正。

**驗收**:`--mock-llm` 全流程 exit 0 且 run/task/claim 皆有列;真 LLM run 對已知小 diff 收斂;kill -9 後 `--resume` 不重做已 confirmed(冪等實證);SQL 斷言 `confirmed` 列 100% 有 `is_deterministic=true` verdict(MVP 已由 verify_claim 保證,擴充後重驗)。

#### 4.3.5 `scripts/benchmark_deliberation.py` — 基準 harness 單支多態(**已落地 MVP;P2 擴充**;規格細節=§5)

**用途**:機械證明「審議引擎>單發 qwen」(需求 d;#15 靈魂)。**單支多態為正名**(§3.0 裁決表;實碼已存在,W2 收編 commit)。

**現行矩陣(實錄,MVP 兩臂;12 列真資料已落 `deliberation_benchmark`)**:

```
python scripts/benchmark_deliberation.py                    # 印矩陣+歷史 run 摘要(唯讀)
python scripts/benchmark_deliberation.py --run              # 預設 24 題(schema/quant/doc 各 8,半真半假)×兩臂
python scripts/benchmark_deliberation.py --run --n-per-class 4 --model qwen3:8b
python scripts/benchmark_deliberation.py --report           # 最新對照+習得裁決
```

**P2 擴充矩陣(三 suite×四臂×GATE;寫 §3.3.11-13 三表)**:

```
python scripts/benchmark_deliberation.py --seed-cases --suite seeded_bug --n 100 --seed 42
python scripts/benchmark_deliberation.py --seed-cases --suite doc_conflict --n 40 --seed 42
python scripts/benchmark_deliberation.py --seed-cases --suite retrieval_adjudication   # 匯入 274 既有題
python scripts/benchmark_deliberation.py --run-suite seeded_bug --arm single_fast --seed-round 1
python scripts/benchmark_deliberation.py --run-suite seeded_bug --arm engine --seed-round 1 --limit 10  # 分批試跑(#25 首日校正)
python scripts/benchmark_deliberation.py --resume-run 17
python scripts/benchmark_deliberation.py --run-all --seed-round 2                       # 整輪(背景 nohup,§7)
python scripts/benchmark_deliberation.py --report-gate --suite seeded_bug               # G1/G2 判定;未過 exit 1
```

| 方向 | 介面 | 內容 |
|---|---|---|
| 輸入 | repo/檔內模板/DB | 真實檔+確定性變異模板(seed 固定)/advisor_distill 274 題 |
| 輸出 | DB | `deliberation_benchmark_case/_run/_result`(§3;MVP 平表保留不動) |
| 輸出 | stdout | 偵測率/誤報率/耗時對照(品質+成本雙軸) |
| exit | — | `--report-gate`:未達 §5.1 預註冊判準(**≥+15pp,與 §1.5/§8.2 對齊;修訂舊稿 +10pp**)→ exit 1 |

**驗收**:同 seed 重跑 `--seed-cases` 產出 byte-identical payload(#10);每臂 ≥3 seed_round(#11);GATE 結果落 `_run.arm_config` 快照可溯源;case 級 resume(`WHERE NOT EXISTS result`)。

#### 4.3.6 `scripts/map_deliberation_to_distill.py` — 蒸餾映射器(新;需求 e;**規格 SSOT=§6.2/§6.4,本節僅索引**)

零 LLM、零新 DDL:(claim,verdict,evidence) 三元組→QA 形直寫 `advisor_distill_question/context`(question UNIQUE 冪等;topic_source='deliberation_engine'、topic_ref=claim_id 軟連結);gold=確定性模板渲染、`teacher_model='deliberation-oracle-template'`;S5 原樣複用。CLI 矩陣=§6.4。廢名:`bridge_deliberation_distill.py`/`export_deliberation_sft.py`(§3.0 裁決表)。

#### 4.3.7 `scripts/report_deliberation_verdict.py` — 人讀裁決報告(新;前身既定檔名)

**用途**:跨 session/run 裁決摘要:findings 表(claim/錨/oracle 證據/裁決)、escalations 清單(**人裁佇列**——「系統建議、人決策」)、耗時與 tok 統計;MVP 之 `deliberate.py --report`(單 session)收攏為共用函式。報告可冪等重生自 DB。

```
python scripts/report_deliberation_verdict.py                    # 印指令矩陣
python scripts/report_deliberation_verdict.py --session <sid> | --run <run_id>
python scripts/report_deliberation_verdict.py --run 42 --md reports/deliberation_verdict_<topic>_YYYYMMDD.md   # #16 命名
python scripts/report_deliberation_verdict.py --escalations-only # 全帳本待人裁項(置頂)
```

I/O:讀 `deliberation_*` 全帳本(唯讀)→ stdout/reports/。**驗收**:對 `--mock-llm` 煙測 run 可產完整報告;每個 confirmed finding 附 oracle 證據原文(file:line/query 輸出,#10)。

#### 4.3.8 `scripts/watch_deliberation.py` — watchdog(新;規格與矩陣 SSOT=§7.4,此處僅列檔號)

---

### 4.4 十模式 → 程式落點對映(traceability)

| ultracode 模式 | 落點 |
|---|---|
| 1 pipeline / fan-out | `engine.py` 輪內序列 fan-out+`llmroute` 排程(物理序列,§4.2.3 誠實邊界) |
| 2 對抗多數決 | `lens.py` 反駁偏向 prompt+`consensus.apply_kill_rule`(只殺不升) |
| 3 視角多樣鏡 | `deliberation_lens` 表(#29b)+`seed_deliberation_lens.py`+`lens.py` |
| 4 judge panel | `consensus.synthesize_panel`+deep_think 檔合成步 |
| 5 loop-until-dry | `engine.is_dry(k)`+`deliberate.py --dry-k/--max-rounds`+dedup_key 去重 |
| 6 完整性 critic | `critic.mechanical_coverage`+`residual_critic`(產物仍受機械鎖) |
| 7 結構化輸出+重試 | `ollama.make_structured_llm_fn`(**已落地** :70)+`llmroute.call_structured` |
| 8 工具實證錨定 | `verifiers.py`(**已落地**;verify_claim=唯一 confirmed 寫入點)+L1-L4 機械補強層 |
| 9 draft→attack→refine | `engine.advance` 狀態機 |
| 10 resume-safe 帳本 | `ledger.py`+run/task/agent_call+`--resume` |

### 4.5 程式語言論證(需求 h)

**全線 Python,不引入第二語言**。Go 併發的唯一假想收益=多 LLM 請求並行,但本機 Ollama runner `-np 1` 物理序列化(實測:相異 prompt 並發 pair 6.97s ≈ 2×單發 3.39s)——瓶頸在 GPU 單流 ~7 tok/s,不在語言層;唯一真實重疊機會(LLM 推理∥oracle 驗證)Python threading 已足(I/O bound,GIL 無礙,repo 有 ThreadingHTTPServer 先例)。反之 Python 複用面=`ollama.py`/`verifiers.py`/`guard`/`core.db`/distill 管線/`_bootstrap` 全數直取——**且 MVP 已以 Python 落地實跑**(#29c),換語言即全部重寫。結論:換語言成本恆正、收益實測為零,**不為換而換**。

## 5. 基準測試 harness

### 5.0 定位:本計畫的「裁決法庭」+MVP 先導實證

前身計畫 §10.2 的結論是推理性悲觀(「答案基本是不建」,plan_20260709.md:252-254);本計畫不與之辯論,改以**機械證據裁決**:單發 qwen vs 審議引擎的對照 harness,增量顯著才算「習得」,證不出即回前身結論、只保留確定性子集。這是 #15 在本計畫的落點——**引擎的存在合法性本身要過真兆檢驗**。裁決全程零 LLM 評分:ground truth 機械生成或既有 DB 標籤,計分為確定性比對(禁 LLM-as-judge)。

**MVP 先導數據(已落庫 `deliberation_benchmark` 12 列,2026-07-10;n 小、僅方向性,不作 GATE 判定)**:兩臂×三類(schema/quant/doc,每類 8 題半真半假、真值執行時機械建構)×qwen3:4b——第二輪(L1-L4 機械補強後)engine 24/24 正確、**假確認 0**;single_shot 16/24、假確認 5。方向與 20/80 立論一致:增量全部來自 oracle 錨定,非 LLM 變聰明。**正式判定仍以本節 G 閘為準**(規模/統計/預註冊判準)。

### 5.1 習得判定(G 閘,先於一切設計;**門柱與 §1.5/§8.2 對齊=+15pp,修訂舊稿 +10pp 之不一致**)

| 閘 | 判準 | 依據 |
|---|---|---|
| **G1 增量閘** | 三 suite 中 **≥2 個** 滿足:engine 臂 vs **最佳單發臂**(single_fast 與 single_think 中偵測率較高者),**3 個 seed 輪的 median case-accuracy 增量 ≥ +15pp,且每輪成對 McNemar 精確檢定 p<0.05** | #11(≥3 次取統計);+15pp=§1.5/§8.2 既定門柱,**預註冊後不得挪動** |
| **G2 誤報閘** | engine 臂誤報率(負例語料上)≤ 最佳單發臂 +5pp | 防「多喊多中」假增量(=§1.5 防灌分約束同式) |
| **G3 零外援閘** | 全部臂全程零 Claude token、零外網呼叫(§7.1 機械驗收) | CLAUDE #28 |
| **G-fail 條款** | G1 或 G2 不過 → 誠實結論=**繼承前身 §10.2**:只保留確定性子集(P1 產物),§6 蒸餾迴路**不啟動**,結果照樣落表留痕 | #15:失敗也是真兆 |

統計功效誠實條款:McNemar 依賴不一致對(discordant pairs);某 suite 某輪 <10 對=「**樣本不足**」而非通過/失敗,處置=擴語料再跑(機械生成、零 usage),不得以小樣本宣稱習得。

> **拍板點 P5-1**:+15pp / +5pp / p<0.05 屬判準層,用戶拍板後寫入 `deliberation_benchmark.arm_config` 快照,之後不得中途改判準(改判準=重跑全部輪)。

### 5.2 三類測例語料(**本表=全計畫語料規模 SSOT**;§1.5 之「每型 ≥30」=統計最小下限、§8.2 之「≥20」=P2 首輪冒煙下限,判定規模以本表為準)

| suite | 測例形 | ground truth 來源 | 規模(GATE 判定) |
|---|---|---|---|
| `seeded_bug` | unified diff(取樣 `src/augur/` 真實檔→確定性變異注入) | 注入器植入清單(機械) | ≥100:正例 70+**負例 30**(無植入之純排版/註解 diff) |
| `doc_conflict` | 文件段落對(docs/reports 真實段落→植入矛盾) | 植入清單(機械) | ≥40:正例 28+負例 12 |
| `retrieval_adjudication` | 既有蒸餾題:question+context→判 ANSWER/DECLINE/REFUSE | `advisor_distill_question.expected`(S2 確定性模板構造,274 題實measured) | 274,零生成成本 |

(MVP 之 schema/quant/doc 宣稱判真偽三類保留於平表 `deliberation_benchmark` 作冒煙迴歸,不入 GATE。)

**seeded_bug 變異運算子**(確定性、seed 落表可重現 #10):比較運算子翻轉(`<`↔`<=`、`==`↔`!=`)、off-by-one、None 檢查刪除、`and`/`or` 對調、早退 return 移位、**字串 SQL 欄名改名**(前身 H3「字串 SQL 掃描為 #8 命門第二面」)、**時點欄誤用**(as-of 條件改未來欄——#8 專項,對 `column_catalog.anti_leakage_flag` 標記欄取樣)。

**doc_conflict 植入運算子**:數字改動、條號互指錯改、判準反轉、日期錯位。變造文本**只住 `deliberation_benchmark_case.payload`,絕不寫回 docs/ 亦絕不入 `knowledge_*`**。

**retrieval_adjudication 匯入**:`SELECT question, context, expected` 匯為 case(`payload={question,context}`、`ground_truth={label}`、origin='distill_import');expected 是 curated 模板構造標籤(`generate_questions.py:36-87`),非 AI 生成事實,可當真值。

### 5.3 四臂對照(**臂集 SSOT;§8.2 之 A/B/C=本表別名:A=single_think、B=majority_fast、C=engine;single_fast 為 §8.2 未列之成本基線臂,由本表補足**)

| arm | 內容 | 目的 |
|---|---|---|
| `single_fast` | qwen3:8b 單發,`think:false`,`temperature:0` 顯式覆蓋(預設 0.6 實測,不可依賴) | 成本基線 |
| `single_think` | 同上 `think:true`(實測 ~7× 耗時) | 「深思單發」是否已夠 |
| `majority_fast` | **N=3** 次 `think:false`、`temperature:0.6` 多數決(修訂:與 engine `skeptic_n=3`、§8.2 B 臂對齊;5 票在物理序列化下成本過高且無對照必要) | 分離「fan-out 本身」的貢獻 |
| `engine` | 完整審議引擎(多鏡+工具實證+loop-until-dry) | 受測者 |

四臂統一走 `format=json schema` 結構化輸出(make_structured_llm_fn 已落地),schema:`{findings:[{file,line,description}], no_defect:bool}`(suite 3 為 `{label}`)。同臂同 suite 共用固定 prompt 前綴(prompt cache 實證生效)。

### 5.4 計分(機械、零 LLM)

- **seeded_bug / doc_conflict**:hit=finding 之 `file` 相同且 `|line−line_gt|≤3`(不比 description 語意——語意比對即重新引入判讀);false_alarm=指向無植入位置;**case-level correct**=全部植入項皆 hit 且 false_alarms≤2;負例 correct=`no_defect=true` 且 findings 空。
- **retrieval_adjudication**:correct=label 三值全等。
- **McNemar 精確檢定**:對每(engine, 最佳單發臂)同 seed 輪成對,b=engine 對/單發錯、c=engine 錯/單發對,p=2·BinomCDF(min(b,c); b+c, 0.5)——純標準庫 `math.comb`,零新依賴。

### 5.5 表結構(**DDL 全文住 §3.3.11-13,本節零 DDL**——修訂:舊稿無前綴 `benchmark_*` 三表**廢除**,違反 §3.0 隔離防線 1 且逃逸 DELIB_LITERALS 掃描)

- `deliberation_benchmark_case`(§3.3.11):測例凍結(payload_sha256+要改另立新 case)、`is_negative`(G2 量測)、`origin`/`gen_method`/`gen_seed`/`source_ref`(#10 可重現)。
- `deliberation_benchmark`(§3.3.12):一 run=1 suite×1 臂×1 seed_round;`arm_config` 快照(P5-1 拍板值入此);**`heartbeat_at` 住此表**(§7.4 watchdog 所引之「benchmark_run.heartbeat_at」即本表——舊稿 §5.5 DDL 已遷§3,特此對映)。
- `deliberation_benchmark_result`(§3.3.13):逐 case;`UNIQUE(run_id,case_id)`=case 級 resume 述詞;`engine_run_id` 溯源 engine 臂之審議 run。#11 之 ≥3 trials=每臂 ≥3 個 seed_round run(結果層 trial_no 廢除,歸一於 run.seed_round)。
- MVP 平表 `deliberation_benchmark`(§3.1)保留為 P1 冒煙帳,不刪不改。

### 5.6 程式(**單支多態 `scripts/benchmark_deliberation.py`,已落地 MVP;#29c 合併——舊稿三支 `generate_benchmark_cases/run_benchmark/report_benchmark_verdict.py` 廢名**,§7/§8 出現之 `run_benchmark.py --all`→`benchmark_deliberation.py --run-all`、`build_benchmark_corpus.py`→`--seed-cases`,依 §3.0 命名裁決表讀)

完整 CLI 矩陣與 I/O=§4.3.5(規格 SSOT,不雙寫)。要點:
- `--seed-cases`:測例生成/匯入(零 LLM;`case_key` ON CONFLICT DO NOTHING 冪等;`--dry-run` 列樣本不落庫)。
- `--run-suite --arm --seed-round`:對照跑分;case 級 resume=`WHERE NOT EXISTS(SELECT 1 FROM deliberation_benchmark_result WHERE run_id=… AND case_id=…)`(沿 build_context.py:75-97 逐項 commit 樣板);與引擎共用 §7.3 同一把 advisory lock(`-np 1` 序列化,兩 LLM 重程序並跑只互拖)。
- `--report-gate`:唯讀;per suite×arm 之 accuracy/誤報率/median/McNemar p/discordant 數;G1/G2 判定;`--md` 寫 `reports/benchmark_engine_vs_single_<YYYYMMDD>.md`(#16;可冪等重生自 DB)。

### 5.7 防作弊(engine 臂不可觸 ground truth)

engine 臂的價值主張=「工具實證勝過意見」,故它**可以**用 grep/psql/pytest 驗證 diff 宣稱——但不得直讀答案。機械落實:
- `db_query` oracle 於 benchmark 模式加禁區述詞:`deliberation_benchmark_case.ground_truth`、`deliberation_benchmark_result`、`advisor_distill_question.expected` 不可及(oracle 層以表名 denylist 擋,verifiers.py 擴充)。
- `file_grep` oracle 於 benchmark 模式禁讀 `benchmark_deliberation.py` 與其變異運算子模組(自身含植入邏輯)。
- 驗收含**作弊探測例**:ground truth 只存在於禁區(payload 內無任何線索)的 case——engine 若答對即證明洩題,harness 判 FAIL。

### 5.8 驗收(W 階段對應見階段規劃節)

1. 三 suite 語料落表達 §5.2 規模,`gen_seed` 全填,同 seed 重跑 byte-identical(#10)。
2. `single_fast` 臂三 suite 全量完跑 ≥1 seed 輪(基線先立,engine 未成也有真兆基線)。
3. 四臂×3 seed 輪全跑完,`--report-gate` 自動輸出 G1/G2 判定,無任何人工計算。
4. 作弊探測例判 PASS(engine 拿不到禁區)。
5. G-fail 時:報告照常產出留痕,計畫依 §5.1 G-fail 條款收斂——**這也是合格的驗收結果**。
6. MVP 平表冒煙迴歸(`--run`)於每次引擎重大改版後重跑,防退化。

## 6. 蒸餾迴路

### 6.0 定位與啟動閘

引擎跑審議會累積(發現, 裁決, 證據)三元組;其中**機械可證**的子集是天然的 SFT 訊號,可餵既有 `advisor_distill_*` 管線,把「提出可驗證宣稱→引證據→不會就 escalate」的行為蒸給本地小模型——**單步模型變強,反哺引擎迭代效率**,同時直接補償前身 §8 破口(b)(confidently-wrong 不吐 undecidable:用 escalate 樣本教「無 oracle 就說無法裁決」)。

> **啟動閘(拍板點 P6-1)**:§5 G1 成立後蒸餾迴路才啟動。G1 不成立=引擎裁決品質無增量證明,拿它當老師是垃圾進垃圾出;此時本節凍結。

### 6.1 既有介面(#29c 零改動複用,本日 psql 覆核)

蒸餾管線介面已被 **274 題/274 gold/171 validated** 實績驗證,且 gold 直寫 DB 的 writer-agnostic 模式已有先例(`teacher_model='claude-teacher-workflow'` 全 274 列):

| 介面 | 形 | 溯源 |
|---|---|---|
| 進口 | `INSERT advisor_distill_question(question UNIQUE, situation_label∈{1,2,3}, expected∈{ANSWER,DECLINE,REFUSE}, domain, topic_source, topic_ref, batch_tag)` | psql `\d`:CHECK 與 UNIQUE 實測 |
| context | `INSERT advisor_distill_context(question_id UNIQUE, context JSONB, n_citations, relevant, retrieval_scope)` | 同上 |
| gold | `UPDATE advisor_distill_context SET target_response, teacher_model, teacher_at`(任何 writer 皆可) | workflow 已示範 |
| 出口 | S5 `validate_one(query, target, context, expected)` 過 guard 三閘+grounding(覆蓋≥0.30 或 ≥8 字逐字;DECLINE/REFUSE 豁免)→ 通過者寫 SFT jsonl | `advisor_distill_validate.py:80-103, 64-77` |

### 6.2 映射設計:三元組 → QA 形(**零新 DDL、零 ALTER——本節為蒸餾橋唯一勝出設計**;舊稿 §3.3.13 `deliberation_distill_export` 表、§8.5 `advisor_distill_question(直橋,見落地對齊註記)`+`export_deliberation_sft.py`、§4.3.6 `bridge_deliberation_distill.py` 四軌**全數廢除歸一於此**,見 §3.0 命名裁決表)

`expected` CHECK 三值擋住任意裁決標籤。三案比較後採**行為題映射**,不擴 CHECK、不另立 staging/export 表:

| 方案 | 裁決 |
|---|---|
| (A) 行為題映射(**採用**) | 零 DDL 變更、S5 三閘語意直接轉譯、語料以 `batch_tag`/`domain` 隔離;冪等鍵=question UNIQUE;溯源=topic_ref=claim_id(#10 已足,另立 export 表=雙帳本) |
| (B) `ALTER … expected CHECK` 加裁決標籤 | 汙染 advisor-QA 標籤語意,S2 GATE/統計腳本全要跟改——否決 |
| (C) 另立 staging/export 表 | 重複造輪+雙 ledger,違 #29c——否決(舊稿 §3.3.13/§8.5 即此案,廢除) |

**映射規則**(全部機械,零 LLM):

| deliberation 來源(psql 實測之 CHECK 值) | situation_label | expected | gold(確定性模板渲染) |
|---|---|---|---|
| claim `status∈{confirmed,refuted}` 且對應 verdict `is_deterministic=true` | 1 | ANSWER | 「裁決:confirmed/refuted。依據:<verdict.evidence 逐字>」 |
| claim `status∈{undecidable,escalated}` 或 `assigned_verifier∈{none,human_claude}` | 2 | DECLINE | 「此宣稱無確定性驗證器可裁決,升級人審。」固定模板 |
| 觸 `redline_trigger` 之 claim(紅線類) | 3 | REFUSE | 紅線拒答固定模板(可選,樣本少,預設不啟用) |
| `deliberation_benchmark_case`(seeded_bug 正例,§5) | 1 | ANSWER | 「缺陷:<ground_truth 植入清單模板渲染>」 |

question 文=固定模板+claim_text+anchor(「以下宣稱與證據,請裁決並引證:…」);`question` UNIQUE 即冪等鍵;`batch_tag='delib_<YYYYMMDD>'`、`domain='deliberation'`、`topic_source='deliberation_engine'`(≤48 字元,欄寬實測)、`topic_ref=claim_id`(**此即 §3.0 隔離防線 4 之唯一 sanctioned 軟連結;孤兒由 `migrate --verify` ⑤ 稽核**)。SFT 匯出端按 `batch_tag` 過濾,與 advisor-QA 語料物理同表、邏輯隔離。

**context 直寫、跳過 S3**:S3 的 `retrieve_all` 是知識庫檢索,對裁決題語意錯位。映射器直接 `INSERT advisor_distill_context`(`context_built=true` 同步標於 question,S3 述詞自然跳過,`build_context.py:70-71`),`retrieval_scope='deliberation_evidence'`。citations 序列化為 S5 可還原之 Citation 形 dict(`_rebuild_citations` 按 dataclass 欄位過濾、缺必要欄即 TypeError 丟棄,`validate.py:33-46`)——欄位與 `augur.philosophy.retrieval.Citation` 對齊(`text`=工具證據/claim 逐字、`source_locator`=anchor);**escalate 樣本也一律附非空 citations**(claim 全文+「assigned_verifier=none」機械理由)——否則空 citations 觸 `guard_empty_retrieval` 誠實閉集檢查(`validate.py:91-93`),裁決模板句不在閉集必死。

**gold 紀律(#1 命門)**:gold 一律由 (claim, verdict, evidence) **確定性模板渲染**,`teacher_model='deliberation-oracle-template'`(誠實標示機械產物,不冒充 Claude 教師);qwen 在審議中產生的推理文**永不當 gold**——可蒸的是「工具證據+機械裁決」,不是模型意見。模板內數字/片段取自 citation 逐字→天然過 guard_knowledge 數字白名單(`citation_numbers`,`validate.py:95`)與 grounding 逐字判準。

### 6.3 界線(不可逾)

1. **蒸餾產物不回流預測管線**:微調模型 tag 只得出現於 advisor/deliberation 設定;feature/model/evaluation 層零 LLM 依賴。機械保證=`src/augur/audit/import_isolation.py` 之 `FORBIDDEN`(:33,已禁 `augur.philosophy/advisor/knowledge`)+本計畫 `DELIB_LITERALS` 三擴(同構樣板 :41/:45/:166,§4.1.2);微調權重檔住 `~/ollama/models`,不入 repo 不入 DB。
2. **蒸餾語料不入 `knowledge_*`**:三元組住 `deliberation_*`、測例住 `deliberation_benchmark_*`、QA 形住 `advisor_distill_*`(本就在 knowledge 域外的訓練工件表)、jsonl 住 `data/distill/`。
3. **guard 一字不動**:S5 複用生產 guard byte-identical(既有 Gate-2 慣例,`validate.py:14`)——蒸餾只能更嚴不能更鬆。

### 6.4 程式

**`scripts/map_deliberation_to_distill.py`** — 三元組→QA 形映射器(零 LLM;**正名,取代舊稿 bridge_deliberation_distill.py/export_deliberation_sft.py 兩廢名**;§8.5 W5a 所指之映射層即本支)。
I/O:讀 `deliberation_claim⋈verdict`(述詞=§6.2 表)、`deliberation_benchmark_case`;寫 `advisor_distill_question`+`advisor_distill_context`(question UNIQUE ON CONFLICT DO NOTHING 冪等);之後跑既有 `advisor_distill_validate.py --run` 出 SFT jsonl,零改動。

```
python scripts/map_deliberation_to_distill.py                          # 印矩陣+可映射存量統計
python scripts/map_deliberation_to_distill.py --dry-run --limit 10     # 列映射樣本(question/context/gold)不落庫
python scripts/map_deliberation_to_distill.py --run --batch-tag delib_20260801
python scripts/map_deliberation_to_distill.py --all-confirmed --batch-tag delib_v1   # 全帳本掃描(冪等)
python scripts/map_deliberation_to_distill.py --stats                  # 各 batch_tag 之 S5 通過率
```

### 6.5 訓練端誠實(#15,不開空頭支票)

實證(本日覆核仍成立):repo 零 LoRA/unsloth/llama-factory 基建、`sft.jsonl` 實體檔全機不存在(validated=171 旗標在 DB 但工件脫鉤)。故本計畫**只交付到「SFT 語料可冪等重生自 DB」**(`advisor_distill_validate.py --run --out data/distill/sft.jsonl` 隨時重生);**微調訓練端標「另案」**(拍板點 P6-2),另案須評估:4GB VRAM 上 QLoRA qwen3:4b 屬邊緣未實測、qwen3:0.6b/1.7b 較可行、CPU-only 訓練軌時間成本——未實測前不寫任何可行性數字。

### 6.6 驗收

1. `--dry-run` 樣本經人工過目(#19 一支一段檢視)後 `--run`;映射批次 **S5 通過率 ≥95%**,不通過者 `validate_verdict.issues` 可機械歸因(Citation 欄位不相容/數字不在白名單…),修映射器再跑、不修 guard。
2. `deliberation_benchmark_case` 蒸餾樣本與 `deliberation` 樣本各 ≥1 批落表,`batch_tag` 隔離查詢驗證(advisor-QA 原 274 題零汙染:`pilot2` 批計數不變)。
3. 隔離掃描過:`python -m augur.audit.import_isolation` 全綠(FORBIDDEN+DELIB_LITERALS);`migrate --verify` ⑤ 軟連結孤兒=0。
4. SFT jsonl 刪檔後重跑 S5 可 byte-identical 重生(DB 唯一 ledger 實證)。

## 9. 對抗審查發現表(四鏡留痕;自 workflow journal 快取確定性抽出 2026-07-10)

### 鏡:ops(營運鏡):4GB VRAM 雙模路由可行性、牆鐘預算誠實度、resume

| # | 嚴重度 | 發現 | 修法/處置 |
|---|---|---|---|
| E-1 | blocker | 計畫是兩套未合併的設計拼接:同一張表在不同節有互斥 DDL——deliberation_agent_call §2.1.10(掛 session_id、UNIQUE(session_id,step_key)、status 含 'pending'/'dup_hit')vs §3.3.7(掛 task_id、status  | 定稿前做一次「單一 SSOT 合併改版」:§3 為 DDL 唯一權威,刪除或改寫 §2 內嵌 DDL 為「見 §3.3.x」引用;每表只留一版;合併後跑一次全文表名/欄名 grep 自檢(這正是本引擎 doc_consistency 要抓的病,計畫自身先犯)。 |
| E-2 | blocker | benchmark 表命名自我違反隔離不變式且雙重定義:§3.3.11-12 定義 deliberation_benchmark_case/_result(前綴受 DELIB_LITERALS 掃描保護),§5.5 卻另給無前綴的 benchmark_case/_run/_result 完整 DDL(欄位也不同:cas | 統一為 deliberation_benchmark_* 前綴(隔離掃描才涵蓋);suite/arm 枚舉全計畫一表定案,§5.5 DDL 併入 §3.3 刪除重複;§8.2 的 A/B/C 臂改用同一 arm 枚舉值。 |
| E-3 | blocker | 樞紐 GO/NO-GO 判準「預先登錄、不得挪動門柱」在計畫內自己有四個版本:§1.5=+15pp+McNemar p<0.05+誤報≤+5pp、每型≥30題;§5.1 G1=+10pp(median case-accuracy、對 single_fast);§4.3.5 exit gate=≥+10pp;§8.2 預 | 預註冊判準只寫一次(建議收斂於 §5.1,含:基線臂=single_fast think:false、+Xpp、McNemar p、誤報上限、語料規模、seed 輪數),§1.5/§4.3.5/§8.2 全改為引用;P5-1 拍板點同步指向該唯一判準。 |
| E-4 | blocker | 程式清單三套未 reconcile,依 v1.39.0「每支程式用途+CLI 矩陣」標準不可拍板:蒸餾橋三個名字(§4.3.6 bridge_deliberation_distill.py/§6.4 map_deliberation_to_distill.py/§8.5 export_deliberation_sft. | 以 §4 為程式規畫唯一權威節,§5.6/§6.4/§8 全部改引用 §4 檔名;模組佈局二選一(建議 §4.0 六模組,§2.0 表刪除);distill staging vs export 依 §6.2 裁決(方案 A、零新表)回改 §8.5 W5a。 |
| E-5 | major | 牆鐘預算在樞紐實驗上相差 5-15 倍且全部錨定 33-token 玩具探測:依計畫自身錨點(engine ≈15min/case §7.5、~7 tok/s),§5 規格全套=414 案×4 臂×3 seeds——engine 臂 1,242 runs×15min≈310h、majority_fast(N=5)≈78 | P2 語料統一為小規模(如 40+20 案)先出 GO/NO-GO,§5.2 全量列 P3 後續;W2c 首日校正後把 per-arm 實測牆鐘寫回 run 表並機械觸發縮編決策(預算上限住 engine_config);per-suite playbook(retrieval  |
| E-6 | major | 雙模路由的 VRAM 前提比計畫寫的更差且換檔策略自相矛盾:實測 idle 時(/api/ps 空、零模型駐留)GPU 已被佔 942MiB(WSL 宿主顯示保留)→ 可用 VRAM ≈3.1GB;qwen3:4b Q4 權重 ~2.5-2.6GB+KV cache+compute buffer@4096 ctx →  | (a) 把單模 8b 定為預設預算與排程基線,雙模列 #27 實驗(現在是反過來);(b) tier 切換時顯式送 keep_alive:0 卸載前一模,swap 次數與 load_duration 落帳本;(c) 排程改跨 round 批次同 tier(攢滿一批 fast 步再 |
| E-7 | major | watchdog 15min stale 判定有假陽性與雙 writer 競態:heartbeat 只在「step 完成」時更新,而單步可合法超過 15min(route timeout_s 預設 600s×schema retry 3 次=30min;CPU-only 8b think 長 prompt;pytest | stale 判定=heartbeat 逾時 AND advisory lock 未持有(pg_locks 可查)才標;heartbeat 改 LLM call 發出前即打點(或背景 thread 每 60s);deliberation_run 補 heartbeat_at;sta |
| E-8 | major | import_isolation oracle 的 invocation 路徑錯:§2.2.1 表與 §4.1.2 標題寫 scripts/import_isolation.py——該檔不存在(ls 實測 scripts/ 無此檔);實檔在 src/augur/audit/import_isolation.py(:41 | 全計畫統一 invocation='python -m augur.audit.import_isolation'(subprocess argv),§2.2.1/§4.0 表/§4.1.2 標題改正。 |
| E-9 | major | 與常駐服務的 Ollama 資源衝突未治理:augur-chat.service/augur-ollama.service 實測 active running,引擎/benchmark 與互動服務共用同一 -np 1 單 slot——過夜 benchmark 期間任何 chat/advisor 請求排在長生成後(逐 c | 計畫明定:(a) 過夜跑窗政策(夜窗停用/接受互動延遲,寫入 run_benchmark --all 啟動確認項,與 #22 電源確認並列);(b) 帳本以 load_duration>0 偵測換模顛簸並統計;(c) 或雙模路由僅於「無互動服務活動時段」啟用。 |
| E-10 | minor | pytest oracle 規格兩處不一致且依賴未驗證:§4.2.3 用 pytest --timeout=120(需 pytest-timeout 外掛——venv 實測未安裝,ModuleNotFoundError;裝了 pytest 9.1.1)vs §2.2.4 用 subprocess timeout 300 | 統一為 subprocess timeout(刪 --timeout flag,零新依賴);invocation 寫死 venv 直譯器絕對路徑(或 sys.executable 並在 oracle 啟動時斷言 import pytest 成功,fail-closed)。 |
| E-11 | minor | advisory lock 為 session(連線)級:引擎逐列 commit 若用短連線/斷線重連(過夜跑 DB 重啟、網路抖動),鎖隨連線消失即靜默釋放,第二實例可入場;§7.3 未聲明鎖連線與工作連線分離、鎖連線斷線時引擎應自殺或重取。 | 單獨一條長駐連線專持鎖(不跑查詢),工作連線另開;主迴圈每 step 檢查鎖連線存活,斷即停(fail-closed)並留 resume 態。 |
| E-12 | minor | CPU-only 軌(需求 f)零數字:預算表全填「未知」,連理論界都沒給——Ryzen 5 3600+雙通道 DDR4(~47GB/s)÷ 8b Q4 權重 ~5GB ≈ 理論上限 ~9 tok/s、實務 3-5 tok/s(記憶體頻寬瓶頸),即 CPU-only 約為現況(61% 已在 CPU)的 0.5-0.7× | 預算表補理論界(標明推導、W1 實測取代);CPU-only 驗收加「stale 閾值按實測 tok/s 重算」一項。 |
| E-13 | minor | G3「拔網測試」在 WSL2 上無可執行指令:斷外網保留 localhost+本地 DB 需 iptables/wsl.conf 或 Windows 防火牆操作,非 trivial;驗收條款無指令=驗收不機械(違計畫自己的「每條驗收=可執行指令」紀律)。 | 驗收附具體指令(如 sudo ip route del default 於測試 shell + 恢復步驟,或 unshare -n 帶 loopback 跑煙測),並註明恢復程序可逆(#6)。 |

### 鏡:completeness(v1.39.0 完整性鏡:逐表 DDL、逐程式 CLI

| # | 嚴重度 | 發現 | 修法/處置 |
|---|---|---|---|
| E-14 | blocker | DDL 正典雙軌互斥:§2 就地 DDL 與 §3「schema 全集」對同名結構給出不相容定義,且兩節皆自稱規範性(§2.0「DDL 隨模式就地列出…一併收編進 migrate」vs §3「本節地位=v1.39.0 全部 table DDL」)。migrate_deliberation_ddl.py 無法同時實作兩版 | 宣告 §3 為 DDL 唯一 SSOT;§2 各模式段一律改為「承載結構見 §3.3.x」不重列 DDL;逐組消歧五處(lens/agent_call/config/模型路由/claim 擴欄),二表擇一、欄名擇一;§4 全部函式簽名與輸出表名改為 run/task/agent_ |
| E-15 | blocker | 程式檔清單三套互斥、一支程式零 CLI 矩陣零 I/O:§4.0 自稱「本節規畫全部程式檔」(16 支),但 §5.6 另立 generate_benchmark_cases/run_benchmark/report_benchmark_verdict 三支(與 §4.3.5 benchmark_deliberatio | 以單一檔案清單(建議 §4.0)為 SSOT:benchmark「單支三態 vs 三支」二擇一並讓 §5.6/§8.2 引用;蒸餾橋接定名一支(建議依 §6.2 裁決保留 map_deliberation_to_distill,刪 bridge 與 export 兩案);watc |
| E-16 | blocker | 基準表命名破壞自身隔離不變式+結構/枚舉互斥:§3.0 對映與 §3.3.11/12 用 deliberation_benchmark_case/_result(suite 含 'doc_contradiction'/'plan_gap'/'data_qa';trial_no、無 run 表),§5.5 卻另建無前綴  | 統一為 deliberation_benchmark_* 前綴一套 DDL(suite/arm 枚舉、run-vs-trial 結構一次定案),§5.5 整段改引用 §3.3;或若堅持獨立前綴,須明文把 'benchmark_' 加入 DELIB_LITERALS 掃描集並更正  |
| E-17 | blocker | 全計畫樞紐(習得裁決)之「預註冊判準」四處互斥:門檻 +15pp(§1.5、§8.2)vs +10pp(§5.1 G1、§4.3.5);基線臂 think:false single_fast(§5.1/§5.3)vs think:true A 臂(§8.2);臂集四臂(§5.3)vs 三臂(§8.2)vs 消融臂 'e | 立單一「預註冊判準」節(建議併入 §5.1)為 SSOT:一組臂集(含 majority_fast 與確定性 floor 消融)、一組門檻(增量 pp+誤報約束+McNemar+樣本量+discordant 下限)、一組語料規模;§1.5/§4.3.5/§8.2 全部改為引用;列 |
| E-18 | blocker | P1 唯一已知真陽性被 W1a 自己的種子先行消滅(時序自毀),且與 D1 拍板順序倒置:§3.5 規定 migrate 種子把 redline pattern 重建為 glob(v1.39.0→v*,即修掉漂移);§8.1 W1a=P1 第一步執行 migrate+種子;A1.3 卻要求引擎把 trigger_id= | §3.5 之 redline glob 重建整列移出 W1 種子,改繫於 D1 拍板後的 P3 W3c;P1 期間凍結現行 9 列原樣(W1a 只固化不改值);並在 §3.5 加註「本表種子分兩波:W1 固化波/D1 後修正波」。 |
| E-19 | major | import_isolation oracle 路徑錯誤——照規格實作即 FileNotFoundError:§2.2.1 oracle 表、§4.2.3 invocation(subprocess 直呼 python scripts/import_isolation.py)、§4.0 第 2 列、§4.1.2 標題皆 | 全計畫統一為 src/augur/audit/import_isolation.py;oracle invocation 改 subprocess([sys.executable,'-m','augur.audit.import_isolation'])(免 cwd 依賴)並同步 |
| E-20 | major | 計畫自身的 ollama.py file:line 錨全數失準——以計畫自己的 file_grep oracle 驗其承重宣稱會被 refuted:計畫立論=「每承重宣稱溯 file:line、機械可驗」,但對 ollama.py 的全部行號錨(make_llm_fn :53、strip_think :38-45、bo | 定稿前對計畫全文 file:line 錨跑一輪 grep -n 重驗並更正(此工作本身即 P1 引擎的 dogfood 題材);承重錨改「函式名+grep pattern」形式、不綁裸行號,行號僅括號附註。 |
| E-21 | major | 多數決語意(對抗機制核心)四處互斥——「多數反駁即殺」到底殺不殺、幾票殺未定:§2.1.2(b) 純意見多數反駁=只提升 escalate 優先級、不直接殺;§4.2.5 majority_refute「只殺不升」回 'kill';§3.2/§3.3.8=多數反駁→status='discarded'(殺但可人工復活) | 在 §2.1.2 寫死單一裁決並令其餘三處引用:建議三級制——oracle refuted 單票即殺(證據制);LLM 全票 refute→discarded(可復活、留帳);多數非全票→僅降 triage 優先;並把 quorum/ratio 判準魔數統一住 engine_co |
| E-22 | major | 模式 5(loop-until-dry)停機判準四種定義並存——停機是承重件,四定義給出不同停機點:「新發現」=新 fingerprint(§2.1.5 sha256 行號桶化)vs dedup_key 撞鍵(§3.2)vs 「無新 confirmed 且 critic 無新項」(§4.2.6 is_dry)vs 「無 | 擇一機械定義為 SSOT(建議:§3.2 dedup_key 撞鍵論+§3.4 view 之 new_claims=停機料源;指紋演算法細節併入 dedup_key 定義),§2.1.5/§4.2.6/§8.3 全改引用;K 定住 deliberation_engine_conf |
| E-23 | major | 程式引用之表/欄無 DDL(v1.39.0 (g) 四處落空):(1) §4.2.1/§4.3.4 寫入 deliberation_agent_call——全計畫無此表 DDL(§3 為 agent_call);(2) §4.3.3 --write-route 回填 measured_toks/measured_load_ | 表名欄名全對齊 §3(llm_call→agent_call;probe 回填欄併入 model_profile 並補 DDL);刪 distill_staging(遵 §6.2 裁決)並二擇一處置 export 表(刪除、或讓 map script 經其過帳);delibera |
| E-24 | major | step 枚舉三套不相容,§3.6 --check ③ 依自家種子必炸:§2.3.1 route step_class=('draft','skeptic','judge','synthesize','critic','refine','extract');§4.2.1 step_kind={draft,skeptic | 單一 step 枚舉 SSOT 定於 §3.3.6 task_kind,route/lens/程式(load_routes、call_structured 簽名)全部改用同一枚舉;§2.3.1/§4.2.1 種子與簽名同步改寫。 |
| E-25 | major | 基準測試混淆變因未設防——引擎臂可對照 repo 原檔「diff 出」植入,增量將量測工具可及性而非審議編排:seeded_bug 取樣 src/augur 真實檔做變異、doc_conflict 取 docs/ 真實段落植入矛盾,而 engine 臂之 file_grep 白名單=整個 repo——引擎只要 grep | 三擇一以上並用:(a) benchmark 模式 file_grep 禁讀該 case 之 source_ref 路徑(入 §5.7 禁區,機械可施);(b) 測例基底先做一層合成重寫使 repo 無逐字原文;(c) 增設確定性 floor 臂(純 diff 腳本)——GO 判準 |
| E-26 | major | pytest oracle 對 diff 測例的作用機制未定義且兩節互斥:§2.2.4(1) 只准跑 git ls-files tracked 之既有測試——對「payload 內的 seeded-bug diff」無從施力(tracked 測試跑的是未變異的真 repo,永遠測不到植入 bug);§4.2.3 卻允許 | 補「diff 施用沙箱」完整規格(scratch worktree 建立/git apply/執行/銷毀;tracked tests 與模板 tests 的兩級白名單與各自風險界),並將 §2.2.4 與 §4.2.3 收斂為同一條規則、整段列入 P4/D4 安全拍板範圍。 |
| E-27 | major | judge panel 落點自我矛盾:§4.2.5「proposer/panel_score 維度落 verdict 擴欄(§3 ALTER)」與 §8.3 W3a「judge panel(verdict 之 proposer 維度)」,但 §3.2(B) 只給 verdict 加 task_id 並明文「刻意不加 a | 採 §2.1.4/§3.3.9-10 方案為準(panel 意見住 proposal/panel_score,verdict 保留給確定性 oracle 輸出);刪改 §4.2.5 與 §8.3 W3a 之「verdict 擴欄」字句。 |
| E-28 | minor | 階段命名 W/P 混用造成指涉歧義:§8 定義階段為 P1-P6(W1a-W6d 為工作項),但 §0.2/§2.3.3/§3.1/§5.5/§7.5/§7.6 多處以「W1 第一步」「W 階段」「W2 試」指涉開發階段(前身計畫的週期命名殘留)——讀者無法確定 §5.5「DDL 併入 W1 的 migrate scr | 全文統一 P 編號指階段、Wxx 僅作 P 內工作項編號;殘留之「W 階段」全數改寫。 |
| E-29 | minor | §7.1 零外援機械驗收的 grep pattern 抓不到主程式:`scripts/deliberate_*` glob 匹配不到 scripts/deliberate.py(需 deliberate*);§2.0 架構圖又寫 scripts/deliberate_*.py 與 §4.3.4 之 deliberate | pattern 改列舉全清單或 `scripts/deliberate*.py`;順帶把 §2.0 圖之檔名統一。 |
| E-30 | minor | §9 對抗審查發現表空置且計畫自認「空置=未達拍板資格」——本輪多鏡審查產出(含本表)須於定稿前填入並附裁決/處置欄,否則依計畫自己的條款不得送拍板;另 AI 產物來源枚舉兩處用詞不一(§3.3.3 lens.author 之 'claude_teacher' vs §3.3.11 origin 之 'claude_g | 定稿時把各鏡發現(含本表)填入 §9 並逐條標裁決/處置;來源枚舉統一為單一詞彙集(如 human_curated/claude_generated/mutation_tool)。 |

### 鏡:honesty(誠實邊界鏡):習得定義可證偽性/基準公平性/補償機制極限/Cla

| # | 嚴重度 | 發現 | 修法/處置 |
|---|---|---|---|
| E-31 | blocker | 「預註冊判準」自相矛盾:全計畫的可證偽核心(§1.5)存在至少四套互斥門檻並存——§1.5=+15pp、McNemar p<0.05、每任務型≥30題;§4.3.5 exit gate=+10pp;§5.1 G1=+10pp median、三 suite 中≥2、且對照臂=single_fast(think:false | 指定 §5.1 為唯一權威判準節(single normative),§1.5/§4.3.5/§8.2 全部改為引用、刪除自帶數字;臂集、語料規模、閾值、對照臂各只准一版;拍板點 P5-1 拍板後將唯一版本快照入 benchmark_run.engine_config,並在 re |
| E-32 | blocker | seeded_bug 基準結構性退化,無法承載「習得」證明:變異注入的 diff 中,被變異行就是 diff 的變更行;計分 hit=file 相同且 /line−line_gt/≤3;而負例=「無植入之純排版/註解 diff」(§5.2)。任務因此退化為「這個 diff 是語意變更還是排版變更」的二分——指著任何語意 | 測例改為多 hunk 真實 diff 中埋入 1 個變異(其餘 hunk 為良性語意變更);負例改為「語意變更但正確」的重構 diff,非純排版;hit 判準加缺陷類型識別;新增零 LLM 的 AST-diff 確定性基線臂——引擎須同時勝過它,否則該 suite 測的不是 LL |
| E-33 | blocker | 全計畫雙帳本式內部矛盾,未達 v1.39.0「每表完整 DDL」與 CLAUDE #20「內部一致」,不可實作:同名表兩套矛盾 DDL——deliberation_lens(§2.1.3 lens_key TEXT PK vs §3.3.3 lens_id bigserial+lens_name UNIQUE)、del | 做一輪「單一權威整併版」:§3 為 DDL 唯一 SSOT、§5.5 三表刪除併入 §3.3.11-12(強制 deliberation_ 前綴);§4.0 為程式清單唯一 SSOT,§5.6/§6.4/§8 之 script 名全改引用;§2 的就地 DDL 全刪改引 §3;函 |
| E-34 | major | 基線不公+lens 汙染未防:§5.1 G1 只要求引擎(~15分/case)勝過最弱的 single_fast(think:false,5.5s)臂,不要求勝過 single_think(40s)或 majority_fast——若引擎輸給一次 40 秒的 think:true 單發,依計畫自己的 20/80 立論「 | G1 改為「引擎 ≥ max(全部非引擎臂) + 門檻」;新增公平單發臂:單發 prompt=全 lens 指令之聯集(同知識、一次呼叫);lens prompt 於語料生成前凍結(version 欄+時間戳),並保留一組任何 lens 未提及的 held-out 變異運算子類。 |
| E-35 | major | 蒸餾出口把基準測例餵進 SFT=train-on-test,自毀證偽儀器:§6.2 映射表第 4 列明文將 benchmark_case(seeded_bug 正例)映射為 ANSWER gold 入蒸餾語料。一旦(另案)微調發生,P3 A3.1「重跑 P2 基準」與一切後續基準都在評一個看過測集的模型——本計畫唯一的 | benchmark_case 全數排除於蒸餾出口(刪 §6.2 第 4 列),或建永久 held-out split(DB 旗標)+ migrate --check 稽核「已出口 question 之 topic_ref 永不指向 benchmark_case」;微調後之評測一律 |
| E-36 | major | db_query oracle 兩節規格互斥,且 ground truth 對引擎物理可達:§2.2.2 規格=自由單條 SELECT+deliberation_ro 角色 GRANT SELECT ON ALL TABLES IN SCHEMA public(含 benchmark_case.ground_truth | 兩節統一為權限層否定:benchmark 模式用第二角色(REVOKE SELECT ON benchmark_case/benchmark_result/advisor_distill_question),由 DB 權限擋、不靠模板約定;蜜罐保留為第二道。§2.2.2 與 §5 |
| E-37 | major | make_chat_fn 規格遺漏 G3 本機焊點(憲章 v1.37.0 隱私鐵律):實碼 make_llm_fn 於建構時呼叫 _assert_local_host(url)(host 不在本機 allowlist 即拒起,防 owned_local 私有內容外送);§4.1.1/§2.1.7 的新工廠規格逐項列了  | §4.1.1 規格明文加入「建構時 _assert_local_host(最終 url),與 make_llm_fn 同款」;驗收加負測試:以外部 base 建構須 raise;§7.1 拔網測試保留為第二道。 |
| E-38 | major | num_ctx 4096 使旗艦 dogfood 用例(計畫完備性審查)對「跨段一致性」物理不可為,且計畫未誠實標注:§1.2 把 plan_completeness 列白名單、P6 W6a 讓新計畫報告過引擎,但 25-50KB 計畫(8-25k token)在 3k 可用 context 下只能分塊——分塊審查看不 | §1.2/§1.3 誠實加註:num_ctx 4096 下跨塊全域一致性屬引擎能力外(歸黑名單或降級為結構層);機械 critic 新增零 LLM 的跨節交叉檢查器(抽取全文件 CREATE TABLE/表名/script 名/閾值數字,重複定義 diff 比對)——此缺陷類本就 |
| E-39 | major | P2 樞紐的 wall-clock 兩節矛盾且全套從未加總:§7.5 自估引擎 15 分/case、夜窗 8h≈30 case;§8.2 卻估 B/C 臂「40 案×3 seeds ≈ 2-6 小時級」——依 §7.5 費率應為 40×3×15min=30h,相差 5-15×。§5.2 全語料(100+40+274=4 | 統一費率來源(以 W2c 首日校正實測覆蓋兩節);語料規模以 McNemar 功效分析定量(需多少 discordant pairs)後縮編,retrieval suite 抽樣(如 60/274);計畫附加總後的多夜排程表與硬預算閘(如 P2 全程 ≤10 夜),超支即縮語料, |
| E-40 | major | 多數決「殺權」三處互斥,且殺在便宜 oracle 之前=倒置經濟學+未量測的共模假陰性:§2.1.2 說純意見反駁「只累計票數…不直接殺」;§4.2.5/§4.3.4 說「多數反駁即殺,省 oracle 呼叫」;§3.5 種子又設 refute_ratio=1.0(全票才 discard)。經濟上,grep/單條 SE | 統一語意為:凡帶合法錨點+已派 verifier 的 claim 一律先過 oracle(便宜),多數決只作用於『無 oracle 可裁的純意見項』之 escalate 排序,永不 discard 可驗 claim;基準加 engine_no_vote 消融臂(§3.3.12 已 |
| E-41 | major | 承重 oracle 路徑錯誤+複用清單行號漂移——「工具實證錨定」計畫自身的錨點失真:§2.2.1/§4.0#2/§4.1.2/§4.2.3 四處寫 scripts/import_isolation.py(§4.2.3 甚至規格化 subprocess([sys.executable, 'scripts/import_ | 全文路徑統一為 src/augur/audit/import_isolation.py(其 :41/:45/:166/:184 行號經實測正確,可保留);ollama.py 錨點更新為 :70/:55;定稿前跑一次錨點機械驗證(所有 file:line 引用逐一 grep 對照) |
| E-42 | major | 「習得」宣稱範圍超出證據範圍:§1.2 白名單 5 個任務型,基準只覆蓋 3 個 suite;§3.3.11 CHECK 枚舉 plan_gap/data_qa 兩 suite 但全計畫無其語料設計;P6 dogfooding 首選用例(計畫完備性審查、小 diff review)中前者從未被基準化。G1 過關(2/3 | 改 per-task-type gating:每任務型須有自己通過的 suite 才啟用引擎裁決權,未基準化的型別(plan_completeness 結構層以外、data_qa)標 experimental、輸出一律 escalate-only;§3.3.11 的 plan_g |
| E-43 | minor | 停機判準承重件(去重指紋)雙定義且含未定義原語:§2.1.5 fingerprint=sha256(category/verifier/anchor_file/line//10/正規化參數)掛 session;§3.2 dedup_key=normalize(category+anchor+claim要旨)掛 run— | 統一為單一定義且只含機械欄位(verifier+正規化參數+anchor 桶),明文排除自由文本、接受過度合併;dup_hit 率入基準量測;桶化改重疊視窗或 ±N 距離比對。 |
| E-44 | minor | G2 誤報閘定義不通+計分不對稱利好引擎:「precision…(負例語料上量測)」語意矛盾——負例上一切 finding 皆 FP,precision 恆 0,除非跨正負例合併計算(未寫明);且 §5.4 正例 case-level correct 容忍 false_alarms ≤2,多鏡 fan-out 天然多產 | 改為明確雙指標:正負例合併的 pooled precision + 負例上的 per-case FP-rate,兩臂同一免費額度(建議 0);§5.1 G2 措辭同步修正。 |
| E-45 | minor | benchmark_case.origin 允許 'claude_generated' 與 §5.2「全部機械可生」及 §8.2 W2a「確定性變異注入」矛盾,留下『AI 出題 AI 答』循環偏誤的後門,防線僅剩人工抽查 20%。另 lens.author 允許 'claude_teacher':兩者皆設計期產物、非執 | 若堅持全機械生成,origin CHECK 刪 'claude_generated';若保留,明文限定為設計期一次性、須 100% 人工簽核(非抽查)且不得與被測 lens 出自同一會話;lens author='claude_teacher' 同樣標注設計期限定。 |
| E-46 | minor | retrieval_adjudication suite(274 題、佔語料 2/3)的 ground truth=S2 模板構造之 expected 標籤,OOC/impossible 題型有固定模板特徵——臂可能靠題型模板識別得分而非檢索裁決能力;該 suite 增量的外推效度弱於另兩 suite,計畫未標注此差異 | 在 §5.2 誠實加註該 suite 之效度限制(模板可識別性);報告分 suite 呈現、不合併宣稱;可行則加人工改寫的去模板化子集(~30 題)做穩健性對照。 |
| E-47 | minor | escalate→DECLINE 蒸餾被宣稱為「直取 §8 破口(b) confidently-wrong 的解藥」屬過度宣稱:訓練端明文另案不存在(§6.5),固定模板 DECLINE 大量重複樣本更可能教出過度拒答,且無任何 post-SFT 的 escalate precision/recall 評測設計——「解 | 措辭降級為「候選訓練訊號,效果待另案訓練+held-out 評測驗證」;蒸餾語料設計加 DECLINE/ANSWER 配比上限;另案立案時強制含 escalate 行為的前後對照評測。 |
| E-48 | minor | pytest oracle 以 deliberation_ro 憑證跑既有 repo 測試(§2.2.4-2)——凡需 DB 寫入的既有測試將因權限直接失敗,環境性 fail 被誤判為行為性 refuted(假陰性裁決);§2.2.4-4 只處理 flaky(重跑不一致),處理不了確定性的環境退化失敗(每次都因權限敗) | pytest verdict 語意三分:pass/fail/env_error——收集階段錯誤與權限/連線類例外歸 env_error→undecidable+escalate,不得記 refuted;白名單預篩「RO 憑證下可跑」的測試子集(先全量跑一次分類落表)。 |

### 鏡:engineering(工程複用鏡:親讀 code/DB/前身計畫實證)

| # | 嚴重度 | 發現 | 修法/處置 |
|---|---|---|---|
| E-49 | blocker | 計畫內含 2-3 套互斥的平行設計未合併——同一張表在不同節有不同 DDL、同一模組有三種佈局、同一 script 有三個名字。§2 vs §3 vs §4 vs §5 vs §8 顯然是多 agent 平行寫作後未做合併 pass,直接使 v1.39.0「全部 table DDL」完備性與 `migrate --ch | 做一次強制合併 pass:宣告單一 SSOT(建議以 §3 DDL+§3.0 命名對映為準),把 §2 各模式節的就地 DDL 全數刪除改為引用 §3 編號;§4/§5/§8 的表名、欄名、script 名、模組佈局、suite 枚舉逐一改寫對齊;合併後跑一個機械自檢(grep  |
| E-50 | blocker | 「預註冊判準」存在四個互相矛盾的版本,且基線臂定義不同——這對一個以 #15「事後不得挪動門柱」為立身之本的計畫是自我否定:G1 到底是 +15pp 還是 +10pp、基線是 think:false 還是 think:true,依讀哪一節而異,GO/NO-GO 結果會不同。§1.5:每任務型 ≥30 題、+15pp、M | 只保留一份預註冊表(建議放 §5.1,含:每 suite 題數、正負例比、臂定義精確到 model_tag+think+options、增量閾值、誤報/precision 定義、seed 輪數、樣本不足處置),§1.5/§4.3.5/§8.2 全部改為引用該表;基線必須同時含 t |
| E-51 | blocker | 基準測試防作弊機制在自己的 DDL/oracle 設計下不成立,engine 臂可經 db_query oracle 直讀 ground truth:§2.2.2 給 deliberation_ro `GRANT SELECT ON ALL TABLES IN SCHEMA public`(含 benchmark ca | 把 §5.7 的模板制寫進 oracle 規格成為唯一 db_query 形式(具名模板+參數繫結,模板住 deliberation_oracle.invocation,LLM 只能選模板+給參數),或至少:deliberation_ro 改為顯式 GRANT 白名單(明確排除  |
| E-52 | major | import_isolation oracle 的呼叫路徑寫錯,照規格實作第一次執行就會 FileNotFoundError:§2.2.1 與 §4.2.3 皆寫 subprocess 直呼 `python scripts/import_isolation.py`、§4.0/§4.1.2 標題也寫 `scripts/i | §2.2.1/§4.0/§4.1.2/§4.2.3 全改 `python -m augur.audit.import_isolation`(或絕對路徑 src/augur/audit/import_isolation.py);順手把 §4.1.2 標題與 §8.1 W1b 對齊成 |
| E-53 | major | ollama.py/advise.py 的 file:line 錨點幾乎全部錯誤,而草稿宣稱這些是「偵察實測」:make_llm_fn 實在 :70(草稿 :53)、strip_think :55-62(草稿 :38-45)、連線重試迴圈 :97-113(草稿 :79-94)、body 組裝 :88-92(草稿 :70 | 以 file_grep 重新校正全部 ollama.py/advise.py 錨點(定稿前跑一次「計畫內錨點自驗」——正好是本引擎 P1 的 dogfood 題);§4.1.1 明文規定 make_chat_fn 必經 _assert_local_host(url)(G3 焊點與 |
| E-54 | major | pytest oracle(本計畫唯一新增的執行級 oracle、seeded-bug 基準的承重件)規格自相矛盾且缺關鍵機制:(1) §2.2.4 規則 1「只跑 repo 已 tracked 測試、LLM 不得提供測試碼」vs §4.2.3「或 benchmark scratch worktree 內由確定性模板生 | 統一 pytest oracle 規格為一節:明定 `git worktree add <scratch> && git apply <case diff>` 機制(含 teardown 與單例互斥)、node id 白名單=git ls-files ∩ 該 diff 觸及模組之 |
| E-55 | major | 隔離不變式的機械看守與自己的 DDL 對不上,兩個方向都有洞:(1) §5.5 三張表命名 benchmark_case/benchmark_run/benchmark_result 無 deliberation_ 前綴,§4.1.2 的 DELIB_LITERALS 只掃「deliberation_ 表名前綴」→ § | 表名統一採 deliberation_benchmark_*(隨 blocker 1 合併定案),DELIB_LITERALS 即可覆蓋;「deliberation 禁 import 預測管線」若要保留,須在 import_isolation 加反向掃描(rglob src/au |
| E-56 | minor | 統計與度量瑕疵三處:(1) §5.1 G2「precision 於負例語料上量測」度量學上不通——負例上只能量 FPR/specificity,precision 需全語料 TP/FP;§1.5 又用「誤報率」,同一防灌分閘兩種定義;(2) §5.4 McNemar p=2·BinomCDF(min(b,c);b+c, | G2 統一定義為「負例語料上的 case-level 誤判率(FPR)差 ≤ +5pp」;McNemar p 加 min(p,1.0),預註冊表明寫多重比較處置(如 Holm 或明示「探索性、以 ≥2/3 suites 一致性代替校正」);語料規模採 §5.2 版本並回填 §1. |
| E-57 | minor | 檔位命名衝突埋設定錯誤地雷:§5.3 基線臂叫 `single_fast` 但=qwen3:8b think:false,而全計畫「fast」tier=qwen3:4b(§2.3.1/§3.3.1 種子)——同一個詞在路由表與基準臂表指不同模型;若實作者按 tier 名解析臂設定,基線會被 4b 頂替、G1 增量被灌水 | 臂名改為含模型與思考態的全名(如 `single_8b_nothink`/`single_8b_think`,§4.3.5 的 CLI 例其實已用此命名——採之),禁止臂名重用 tier 詞彙;benchmark runner 啟動時斷言臂 model_tag 與預註冊表一致。 |

**合計 57 項(blocker 15);處置狀態=實作時逐項核銷(MVP+L1-L4+基準已消化多數工程/誠實類;餘者見 backlog)。**

---

## 附:對抗審查摘要與產出誠實紀錄

|鏡|發現數|blocker|裁決|
|---|---|---|---|
|honesty(誠實邊界鏡):習得定義可|18|3|不可拍板(NO-GO as-is),但方向可救。誠實面試題四問的裁決:(1) 高估本地模型?——否,§1.1-1.4 的|
|completeness(v1.39.0|17|5|結構覆蓋面合格、單一正典紀律不合格——未達拍板資格,須大改後重審。正面清點:10 模式逐一有本地化設計(§2.1.1-2|
|engineering(工程複用鏡:親讀|9|3|打回重整後再拍板(NO-GO as-is)。先說公道話:本草稿的「對外」實證品質很高——本次親驗全數成立:deliber|
|ops(營運鏡):4GB VRAM 雙模|13|4|未達拍板資格(BLOCKER 未清)。核心立論與機械鎖架構站得住——實測驗證了關鍵前提:deliberation_* 5|

**產出紀錄(#15 誠實)**:分節草稿(6 節)+四鏡對抗完成;Refine 合成因單次輸出超 64K 上限失敗(教訓三:分節修訂仍須限節數/每節上限),故定稿=分節草稿+完備性 fix-gaps 補丁(該 agent 親讀 2026-07-10 repo 現況,將 MVP 落地實查〔commit 24e87a3、L1-L4、基準滿分〕併入);四鏡 blocker/major 之逐項整合由主 session 於實作時對照本表逐項核銷。
