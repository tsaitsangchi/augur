# augur 前台檔位(模型 × effort)× ultracode 審議母幹對接計畫(定稿)

**檔名**:`reports/augur_frontend_tiers_ultracode_backbone_plan_20260711.md`
**日期**:2026-07-11
**性質**:計畫先行報告(CLAUDE #20 / 憲章第六部;v1.39.0 表與程式雙落實)。**程式先落、旗標關;翻開條件=GATE(`gate_663fecd41783`)+A5 復審過(用戶已核),翻開動作=用戶拍板後 UPDATE 一列。**
**承前拍板(不重辯)**:Q2 分層原則——驗證/審查/裁決類→審議引擎當母幹;純機械執行(sync/build/embed/guard)→維持確定性工具、不包 LLM。
**SSOT 參照**:本地審議引擎計畫(`reports/augur_local_ultracode_engine_plan_20260710.md`)、advisor 前台鏈現況(§1.1 實查)、CLAUDE #29b(決定行為的資料住 DB)。

## 目錄

- §0 三十秒總覽(含誠實邊界)
- §0.5 批判修訂對照表(草稿→定稿全部差異之依據)
- §1 前台檔位設計(1.1 現況實查/1.2 檔位語意/1.3 API 擴充點/1.4 呈現設計)
- §2 轉接器設計(2.0 改動面總表/2.1 effort.py/2.2 路由與 target_block/2.3 guard 併入與命門/2.4 進度回饋/2.5 DB 開關/2.6 並發護欄)
- §3 表與程式雙落實(3.1 所讀既有表 schema/3.2 config 規格/3.3 python 程式規畫/3.4 `/api/tiers` 端點)
- §4 後台「驗證母幹」分層落地
- §5 分階段(F0→F3)
- §6 驗收總表(V0–V10)
- §7 誠實邊界+不做清單+拍板點(P1–P6)

---

## §0 三十秒總覽

**要做什麼**:把前台對話(`serve_chat_ui` :8090 → `serve_advisor_openai` :8399 → `advise()` guard 鏈)升級為「仿 Claude 前台」的雙選單——

- **模型選單**:`qwen3:4b`(D1 實測 avg **17.1 tok/s**)/ `qwen3:8b`(avg **6.7 tok/s**,4GB VRAM 部分 CPU offload)——tok/s 為 `deliberation_model_probe` 實測(各 model 3 task_kind × n=3 共 n=9;2026-07-11 DB 再驗:4b=mean(15.6, 18.0, 17.7)、8b=mean(7.7, 5.9, 6.6)),UI 顯示值**現算自 DB、不寫死**。
- **effort 三檔**:
  - **fast** = 現行單發(think=False、temp 0.15、num_predict 900;零行為變化=預設檔)。
  - **think** = `make_llm_fn(think=True)` 深思;**num_predict 4096(對齊 GATE 預註冊 think_spec,非拍腦)**;qwen3 推理段照 `strip_think` 機械剝除、永不呈現、不進 guard;**截斷偵測**:剝除後空輸出→機械誠實句,不回空字串。
  - **ultracode** = **審議引擎轉接**:機械可驗宣稱交 `engine.deliberate`(單 lens 預設;panel/iterate 選配)→ 5-oracle 裁決 → 裁決區塊以**機械模板**併入 guard 後回覆(**模板與背書數字零-LLM;宣稱原文=LLM 提出、逐行明標非系統背書**,見 §1.4)。

**上線開關(#29b)**:`deliberation_engine_config` 增一列 `config_key='frontend_tiers'`、`enabled:false` 先落;GATE+A5 過 → UPDATE 一列翻開,**零改碼**。關閉態=行為逐位元等同現行(單 model、fast 唯一檔、UI 無選單)。

> ### 誠實邊界(大字,呈現於 UI 與本計畫雙處)
> **前台 ultracode 檔 ≠ Claude ultracode 全能。**它只把「機械可驗宣稱」(augur 自身的 schema/資料量/檔案內容/隔離不變式)交 5 真 oracle 裁決;**LLM 意見零證據力、confirmed 唯一寫點=`verify_claim` 不變**;其餘內容一律走既有誠實 guard 鏈(相對機率誠實/引文 grounding/數字白名單,一條不鬆)。escalated=誠實「已進人裁佇列」,不是失敗。#28 理解層(doctrine 詮釋/真兆判讀)仍為 Claude 保留區——本地審議引擎不越此線。
> **另兩條本定稿新增的誠實聲明**:① 裁決區塊內的宣稱原文是 LLM(qwen lens)提出的文句,系統只背書 oracle 證據行,不背書宣稱全文;② 選 `augur-8b-ultra` 時,**審議引擎本體跑 qwen3:4b**(承 `deliberate.py` 預設+GATE 預註冊 model)、只有白話解讀用 8b——UI 選單明示,不誤導。

---

## §0.5 批判修訂對照表

> 批判收訖範圍之誠實聲明:收到之批判清單自稱「按六軸列」,實際收訖至第 4 軸第 4b 項(4b 文末截斷於「佇列+誠」)。本對照表涵蓋收訖之 1a–4b 全部 14 項;4b 依其可辨語意(單飛鎖/佇列+誠實拒絕)補完。**若原批判尚有第 5/6 軸,請於 F0 過目時補列,本稿不佯稱已涵蓋。**

| 批判# | 缺陷要旨 | 定稿修訂落點 |
|---|---|---|
| 1a | §3 整節缺漏(v1.39.0 表與程式雙落實不在稿內);P3–P5 拍板點懸空 | 補齊 §3 全節(3.1 所讀既有表 schema 實查/3.2 config 規格/3.3 程式規畫表/3.4 `/api/tiers`);§7.3 拍板點補至 P1–P6,§4.2/§5 之 P4/P5 引用全部落實 |
| 1b | 改動面聲明不完整(engine.py progress_cb/engine_config fresh/oai_compat model 回顯未列) | 新增 §2.0 改動面總表:明列 6 檔+1 列 INSERT,含 deliberation package 兩檔之最小修改與其 byte-同保證(V1) |
| 1c | `target_block` 未定義 | 新增 §2.2.1:target_block 三型機械組法(表名命中/檔案路徑命中/無標的),沿用 `_target_from_block` 既有「目標檔案 」首行格式=零 engine 解析改動 |
| 1d | `/api/tiers` 無元件/程式/驗收定義 | §3.4 端點全規格(advisor 側 `/v1/models` 擴充+chat_ui 側 `/api/tiers` 轉發塑形)+驗收 V4 併驗 |
| 2a | 「裁決區塊=零-LLM」名不符實(claim_text=LLM 文句繞 guard 進 UI) | §1.4 重定義:區塊標題改「模板機械;宣稱原文=LLM 提出、非系統背書」;每行 claim_text 明標;**背書數字唯 `deliberation_verdict.evidence` 行(工具輸出)**;嚴格模式(claim_text 數字白名單同級檢查)列拍板點 P6 |
| 2b | advisor「唯讀零寫」命門被靜默改變(engine 會寫審議帳本) | §2.3.1 命門變更明文化:諮詢資料面維持唯讀零寫、新增例外=deliberation_* 帳本(僅經既有 ledger/verifiers 寫點);oai_compat 檔頭 L8 聲明同步修訂;DB 角色分離方案列**拍板點 P3** |
| 2c | narrative 與裁決可互相矛盾而無呈現規則 | §1.4 固定機械尾註:「白話解讀與審議裁決各自獨立產生;不一致時以 oracle 裁決為準」——零-LLM 模板句,每則 ultracode 回覆必附 |
| 2d | `augur-8b-ultra` 標籤誤導(引擎實跑 4b) | §1.2/§3.4:tier label 明寫「審議引擎=4b;白話解讀=8b」;§0 誠實邊界同步聲明 |
| 3a | fail-closed 400 在主路徑(stream:true 先 200)不可能 | §2.3.2:tier 解析**前移至 `send_response` 之前**(串流/非串流皆然);未知 tier → HTTP 400 真回;已 200 後的錯誤維持既有 `[augur-error]` 語意;驗收 V7 |
| 3b | `[augur-progress]` 會污染 chat_message 歷史(完成路徑 L364-366/recordMsg L388 只濾 [augur-guard]) | §2.4:renderStream **與完成路徑雙處**同濾 `[augur-progress]` 段;新驗收 V8「進度行不落 chat_message」(SQL 機驗) |
| 3c | `load_rules(cur,…)` 需外部游標;config 讀取失敗語意未規畫 | §2.5/§3.3:`effort.load_tiers()` 自管短連線;`load_rules` 增 `fresh=False` 參數;**DB 讀失敗→fail-safe 回 `{"enabled":False}`=走 legacy 現行路徑並 log,不 500** |
| 3d | 閘數口徑不一(四閘 vs 五閘) | 口徑定錨(§4.1#13/§7):**「guard 閘鏈」=`guard()` 總閘+`guard_knowledge`/`guard_empty_retrieval`/`guard_attribution`/`guard_definition` 四具名子閘**(=回歸檔頭「五閘」之函式計數;草稿「四閘」=四具名子閘);本計畫一律稱「guard 閘鏈(五函式)」 |
| 4a | think 檔 num_predict 1400 必截斷=空回覆;與 GATE 預註冊 spec(4096)矛盾 | §1.2:think 檔 num_predict 改 **4096、timeout 900s(=GATE `think_spec` 預註冊值,DB arm_config 實查)**;延遲誠實重估(8b 最壞 ~10 分鐘);`strip_think` 後空輸出→機械誠實截斷句(驗收 V10) |
| 4b | 零並發護欄(AbortController 只斷前端;兩組審議互踩) | 新增 §2.6:ultracode 檔**單飛鎖**(config `max_concurrent:1`),忙碌→即時機械誠實拒絕句;孤兒審議誠實記帳至完成;驗收 V9 |

---

## §1 前台檔位設計

### 1.1 現況實查(讀碼結果 2026-07-11 再驗;API 擴充點依此定)

| 部位 | 實查事實(檔:行) | 對本計畫的含義 |
|---|---|---|
| `scripts/serve_chat_ui.py` L653 | POST `/chat` 轉發體硬綁 `fwd={"model":"augur-advisor","messages":…,"stream":True}` | model 欄由 proxy 塑形——前端選檔位後由此處帶入 |
| 同檔 L244/L468 | composer 的 `.modelpill` 僅靜態顯示 env `OLLAMA_MODEL` | 換成雙選單(model+effort)的掛點 |
| 同檔 L347 | 前端 `renderStream` 以 `\n---\n` 分段、濾除段首 `[augur-guard]` 段至獨立狀態列 | 同機制可濾 `[augur-progress]`(§2.4) |
| 同檔 L364-366/L388 | **完成路徑**組 `body` 時同樣只濾 `[augur-guard]`,`recordMsg('a',body)` 落 `chat_message` 並隨「重試」重播 | **進度行須在此雙處同濾,否則污染歷史**(批判 3b;驗收 V8) |
| 同檔 L659-661/L668 | 送 `X-Augur-Internal`/`X-Augur-Session`;上游 timeout=**1800s** | ultracode 分鐘級預算之外框上限 |
| `src/augur/advisor/oai_compat.py` L21/L26-30 | `MODEL_ID="augur-advisor"` 常數;`/v1/models` 只列 1 個 model | tiers 開啟時改列全部啟用組合(§3.4) |
| 同檔 `chat_completion`(L96-138) | **不讀 `body["model"]`**(全檔無 `body.get("model")`)——model 欄現為無效載體 | **天然擴充點:model 欄承載檔位,零相容性破壞** |
| 同檔 L133/L145 | 回應體與 chunk 之 `"model": MODEL_ID` 寫死 | 須隨 tier 回顯(§2.0 改動面) |
| 同檔 L219-233 | **串流分支先 `send_response(200)`+role chunk 才呼叫 `chat_completion`**;例外→`[augur-error]` 內容 chunk | **未知 tier 之 400 必須在 200 之前解析**(批判 3a;§2.3.2) |
| 同檔 L8 | 檔頭明文「對全部表唯讀零寫(命門 5/6)」 | effort→engine 寫審議帳本=命門變更,須明文修訂+拍板(§2.3.1/P3) |
| 同檔 L251-263 | `make_server` 把單一 `llm_fn` 焊死於 server 屬性 | per-request 檔位需改注入 **llm 工廠** |
| `scripts/serve_advisor_openai.py` L59-61 | 現行 llm_fn=`make_llm_fn(think=False, strip_quotes=True, options={"temperature":0.15,"num_predict":900})`,model 預設 env→`qwen3:8b` | 此組參數=**fast 檔的凍結定義**(R2 調校沿用) |
| `src/augur/advisor/ollama.py` L55-62 | `strip_think`:未閉合 `<think>`(截斷)→ 自標籤起全刪 **fail-closed,可致空字串** | think 檔須配足 num_predict+截斷偵測誠實句(批判 4a;V10) |
| `src/augur/deliberation/engine.py` L32 | `deliberate(topic, target_block, lens, model, n, timeout)`——**無 callback 參數,進度現況=print stdout** | progress_cb 須改此檔(最小增參,預設 None=現行為;§2.0) |
| `src/augur/deliberation/engine_config.py` L20 | `load_rules(cur, key)` 需外部游標+`_CACHE` 進程快取 | 增 `fresh=False`;effort 自管短連線(§2.5) |
| DB `deliberation_model_probe` | avg tok/s:`qwen3:4b`=17.1、`qwen3:8b`=6.7(各 n=9;欄位=`model_tag`/`tok_per_s`) | UI 誠實預期顯示之唯一來源(#9(b)) |
| DB `deliberation_bench_batch` gate 列 | `think_spec={"timeout":900,"num_predict":4096,…}`;thresholds=min_pp_gain 15/McNemar α=0.05 pooled/fc_rule;model=qwen3:4b;rules_config_sha=`78d2a81d63204531` | think 檔參數定錨於此預註冊 spec(批判 4a 修) |
| DB `deliberation_run` | `dlrun_8bcf7470c87c` status=running(GATE run) | F2 前置 V0 之標的 |

### 1.2 檔位語意(2 模型 × 3 effort)

| effort | 定義(機械參數,住 config §3.2) | 誠實預期延遲(**上限估算=num_predict÷實測 avg tok/s,僅生成段**、不含 prompt eval/檢索;F1 實測端到端後以實測值取代,V10) |
|---|---|---|
| **fast** | think=False、temp 0.15、num_predict 900、timeout 300s(=現行 R2 調校,逐位元不變) | 4b:≤900/17.1≈**~53s**;8b:≤900/6.7≈**~134s** |
| **think** | think=True、temp 0.15、**num_predict 4096、timeout 900s(=GATE 預註冊 think_spec,DB 實查定錨)**;`strip_think` 照剝、思考段永不呈現、不進 guard(P8 閘鏈一環不變);**截斷偵測:剝除後空輸出→機械誠實句「深思輸出因長度上限截斷…請改 fast 檔或再試」,不回空字串** | 思考段+正文皆計:4b 最壞 4096/17.1≈**~4 分**;8b 最壞 4096/6.7≈**~10 分**(timeout 900s 外框);典型 qwen3 思考 1500–3000 tok → 8b 約 4–7.5 分。UI 選單即標示 |
| **ultracode** | 審議引擎轉接(§2):**engine 模型固定 `qwen3:4b`**(承 `deliberate.py` 預設+GATE 預註冊 model;format 約束壓思考洩漏)、narrative 用所選模型 fast 參數;**UI 於 8b-ultra label 明示「審議引擎=4b;白話=8b」(批判 2d 修)** | **分鐘級**(propose+逐 claim oracle+narrative);UI 進度回饋必備(§2.4);單飛鎖(§2.6) |

- 模型選單顯示:「qwen3:4b — 實測 17.1 tok/s(快)」/「qwen3:8b — 實測 6.7 tok/s(4GB VRAM 部分 CPU offload,慢而穩)」;數字由 `/api/tiers` 現算 `deliberation_model_probe` avg(`model_tag`/`tok_per_s` 欄)——**probe 無資料則顯示「未量測」,不編數字**(#9)。
- 組合=6 tier + legacy `augur-advisor`(=`default_tier`,現行 8b+fast;舊 client 零破壞)。

### 1.3 API 擴充點拍板:model 欄承載檔位

**拍板:tier id 走 OpenAI-compat 之 `model` 欄**,理由:
1. §1.1 實查:`chat_completion` 現不讀 `body["model"]` → 啟用它**零相容性破壞**;
2. model 欄是 OpenAI 協定原生載體——任何 OpenAI client(含未來 Open WebUI)的模型下拉即自動成為檔位選單,`/v1/models` 即檔位清單;
3. 否決自訂 header/body 欄方案:第三方 client 無法呈現、且多一條非標準契約。

**tier id 閉集住 DB config(#29b)**:`frontend_tiers.tiers` 映射 `id → {model, effort}`(§3.2);新增/停用檔位=UPDATE config 一列,零改碼。id 命名(不含 `:`,避免與 Ollama tag 撞):

```
augur-advisor            (legacy 別名 → default_tier)
augur-4b-fast | augur-4b-think | augur-4b-ultra
augur-8b-fast | augur-8b-think | augur-8b-ultra
```

**fail-closed(批判 3a 修正版)**:tier 解析**一律於 `send_response` 之前**執行(§2.3.2)——未知 model id → **HTTP 400 誠實拒絕**(`invalid_request_error`),串流與非串流請求皆然,**不靜默降級**成預設檔(#15 不佯稱)。已進入 200 串流後才發生的錯誤(engine/LLM 例外)維持既有 `[augur-error]` 內容 chunk 語意(誠實揭露,非新設計)。`/v1/models`:tiers enabled → 列全部啟用 tier(id+label 含實測 tok/s,§3.4);disabled → 維持只列 `augur-advisor`(=回歸基線)。

### 1.4 呈現設計(ultracode 檔回覆之分級顯示;批判 2a/2c 修訂版)

裁決區塊=**機械模板**(模板結構、狀態圖標、背書數字皆零-LLM;前例:`_verdict_note`/`_citations_block`/D4b picks 表)。**但區塊內的 `claim_text` 是 qwen lens 提出的 LLM 文句——定稿明文承認此事並逐行標示,不再自稱「零-LLM 區塊」**:

- **區塊標題**:`── 本地審議裁決(模板機械;宣稱原文=LLM 提出、非系統背書;系統背書僅及 oracle 證據行)──`
- **背書數字紀律**:區塊內「系統背書」的數字**唯出現於 evidence 行**(`deliberation_verdict.evidence`=oracle 工具輸出,#9(b));claim_text 行內數字一律屬 LLM 宣稱、由狀態前綴標明背書態。
- **嚴格模式(選配,拍板點 P6)**:對顯示之 claim_text 跑數字白名單同級檢查(claim 內數字 ⊆ evidence∪payload 白名單,不符→該行遮蔽數字並註明)——預設不開,雙標示已足誠實;開否由用戶裁。

| claim 終態 | 顯示(每行 claim_text 前綴狀態詞+「LLM 宣稱原文」標示) | 依據欄位 |
|---|---|---|
| confirmed **且** `semantic_bound=true` | ✓ **confirmed·bound**〔宣稱原文(LLM 提出):…〕+ oracle 證據行(verifier/anchor/`deliberation_verdict.evidence` 摘要=系統背書) | claim.status+claim.semantic_bound+verdict.evidence |
| confirmed 但 `semantic_bound=false` | ◐ **anchor-only(降格)**〔宣稱原文(LLM 提出):…〕:「錨點成立、語意未綁——僅代表錨點查證通過,**不背書宣稱全文**」;不得與 confirmed·bound 同格呈現(B1 二級制) | 同上 |
| refuted | ✗ **已被 oracle 反證**〔宣稱原文(LLM 提出):…〕(oracle 證據附上;不隱藏反證) | 同上 |
| escalated(undecidable / no_oracle / red_line_category) | ⚠ 「**已進人裁佇列 #<escalation_id>**」〔宣稱原文(LLM 提出):…〕(誠實「待人裁」非失敗;人裁走既有 `resolve_escalation` CLI) | `deliberation_escalation.escalation_id/reason` |

- **矛盾呈現規則(批判 2c 修)**:每則 ultracode 回覆固定機械尾註兩句——①「本檔位僅對機械可驗宣稱給 oracle 裁決;其餘為 LLM 白話+誠實 guard 鏈;LLM 意見零證據力」;②「**白話解讀與審議裁決各自獨立產生;兩者不一致時,以下方 oracle 裁決為準**」。零-LLM 模板句、必附。
- `[augur-guard]` 尾註照舊;4GB 吞吐誠實:選單標示預期延遲、ultracode 進行中顯示 `[augur-progress]` 機械進度行(§2.4,前端**渲染與落庫雙路徑**皆濾至狀態列、不入泡泡正文、不落歷史)。

---

## §2 轉接器設計(advisor 側 effort router)

### 2.0 改動面總表(批判 1b 修;誠實列全)

| 檔 | 動作 | 內容 | 風險緩解 |
|---|---|---|---|
| `src/augur/advisor/effort.py` | **新增** | 轉接器本體(§2.1/§3.3) | 旗標關=零 import(V1 file_grep) |
| `src/augur/advisor/oai_compat.py` | 修改 | ① tier 解析前移至 send_response 之前(3a);② `models_payload` 依 config 列 tier;③ 回應體/chunk `model` 欄回顯 tier id(L133/L145);④ 串流分支 worker thread+progress queue(§2.4);⑤ 檔頭 L8 命門聲明修訂(P3) | disabled 路徑=現行碼路;V1 回歸 |
| `src/augur/deliberation/engine.py` | 修改(**最小**) | `deliberate(…, progress_cb=None)`:propose 前與每 claim 裁決後呼叫;**預設 None=現行 print 行為不變** | 預設路徑 byte-同(V1) |
| `src/augur/deliberation/engine_config.py` | 修改(**最小**) | `load_rules(cur, key, fresh=False)`:fresh=True 跳 `_CACHE` | 預設 fresh=False=現行為 |
| `scripts/serve_chat_ui.py` | 修改 | 雙選單(model×effort→tier id)、`fwd["model"]`=tier、renderStream **與完成路徑雙處**濾 `[augur-progress]`、GET `/api/tiers` | disabled→無選單=現行 UI |
| `scripts/serve_advisor_openai.py` | 修改 | 注入 llm 工廠+config;現行參數組=fast 檔凍結定義 | legacy 路徑走原 llm_fn |
| DB | **INSERT 1 列** | `deliberation_engine_config` `frontend_tiers`(enabled:false) | 新表 0、新 DDL 0 |

deliberation package 兩檔之修改均為向後相容增參(預設值=現行為);advisor 觸及 `deliberation_*` 字面屬合法(實查 `import_isolation.py`:`DELIB_LITERALS` 掃描面=`SCAN_DISTILL`=PIPELINE+core+knowledge+philosophy,**不含 advisor**;新增 code 不得擴此面)。

### 2.1 新模組 `src/augur/advisor/effort.py`

命名過 #18 三問:(a) *effort* 是本功能的領域概念(推理力度檔位),非通用角色名;(b) `augur.advisor.effort` 讀起來=「顧問的力度檔位」單看即知;(c) 別的領域不會搶此名。職責=tier 解析+llm 工廠+ultracode 路由;**對諮詢資料面唯讀**;不碰 guard 內部、不新造編排器(advise() 仍唯一諮詢編排出口)。寫入面之命門變更見 §2.3.1(拍板點 P3)。函式簽名與輸入輸出表見 §3.3。

### 2.2 ultracode 路由:哪些問題適合、topic/target_block 怎麼轉

- **適用域=機械可驗宣稱域**:關於 augur 自身、可錨定 5 oracle(`information_schema`/`db_query`/`file_grep`/`import_isolation`/`pytest`〔dormant〕)之題——表/欄存在、列數比較、檔案內含字串、隔離不變式。判定=**機械規則零 LLM**:eligibility 詞表+表名/檔名命中規則住 config(#29b 資料側;安全不繫於詞表——誤放行頂多得 undecidable→escalated,誠實不損,合 v1.35.0「安全繫於機械閘」裁例)。
- **topic 轉換**:`topic = "[frontend] " + 用戶問題原文`(前綴標 provenance,帳可溯 #10;session.topic 存全文)。mode 依 config:預設 `single`(`engine.deliberate` 單 lens、≤6 claims,時間預算內),`panel`/`iterate` 選配。redline consult 照走(治權觸線→`human_claude`→escalation,人拍板 #19/#26 不因前台鬆動)。

#### 2.2.1 target_block 組法(批判 1c 修;機械規則零 LLM)

`engine.deliberate` 必填參數 `target_block`=lens 攻擊標的文本,且 `_target_from_block`(engine.py:67-71)自**首行**解析「目標檔案 X(」格式——組法沿用此既有契約、零 engine 解析改動:

| 命中型 | 機械判定 | target_block 首行+內容 |
|---|---|---|
| **檔案標的** | query 內 token 經 repo 相對路徑存在性檢查命中(`pathlib` 機械驗) | `目標檔案 <path>(內容可經 file_grep 錨定)` + 換行 + query 原文 → `_target_from_block` 取回檔名,L3/L4 補全照現行 |
| **表標的** | query 內 token 對 `information_schema.tables` 現有表名機械比對命中(一次 SELECT) | `目標=資料庫表 <t1>,<t2>(schema/列數可經 information_schema/db_query 錨定)` + query 原文(非「目標檔案 」開頭→target=None,claims 以表錨自派,合法) |
| **無標的** | 皆未命中但過 eligibility 詞表 | `目標=augur 資料庫與 repo(無單一檔案標的)` + query 原文;claim 錨由 lens 自派,錨不出→undecidable→escalated=誠實 |

- **不適合 → 誠實 fallback**:哲學/市場解讀/通識/檢索類題 → 走原 `advise()`(所選 model+fast/think 參數),回覆**前置一行機械說明**:「此題不屬機械可驗域,ultracode 檔改以一般誠實管線作答」——不佯稱有審議。
- **選股題(`relevance.picking_intent`)不進審議**:payload 真兆已是 ground truth(D4),審議 claim 非真兆(界線-A),混入反而降純度;照走現行 picking payload 分派。

### 2.3 結果併入 guard 鏈(不繞 guard)

```
ultracode tier 請求
 ① effort.run_ultracode(query)          → 單飛鎖(§2.6)→ engine.deliberate(全帳落 deliberation_*;
                                           confirmed 唯一寫點=verify_claim 不變)
 ② advise(query, payload, llm_fn_fast)  → narrative 過完整 guard 閘鏈(五函式:總閘+四具名子閘),一條不少
 ③ oai_compat 機械合成                   → guarded narrative
                                          + "── 本地審議裁決(模板機械;宣稱原文=LLM 提出、非系統背書…)──"
                                            分級區塊(§1.4)
                                          + 誠實邊界尾註(含「以裁決為準」句) + [augur-guard] 尾註
```

不變式(驗收逐條測,§6):
1. **LLM narrative 不注入 oracle 數字**(否則觸 guard 數字白名單);審議區塊之**背書數字**全出 `deliberation_verdict.evidence`/claim 欄(#9(b) DB 來源),與 narrative 以分隔線硬隔;claim_text 行依 §1.4 標示 LLM 原文。
2. **界線-A 同構鐵則**:審議 claim/verdict=審議行為樣本、**非真兆**——絕不成 citation、絕不寫 `knowledge_*`/`feature_values`、不回流檢索。`import_isolation` 現況:`DELIB_LITERALS` 掃描面=PIPELINE+core+knowledge+philosophy;advisor 唯讀觸及合法,新增 code 不得擴此面。
3. **confirmed 唯一寫點不變**:前台只「呼叫」既有管線,零新增 confirmed 寫點;panel/迭代照舊零 confirmed 權。
4. guard fail 行為不變:narrative 被攔 → `NO_KNOWLEDGE_RESPONSE` 閉集句照回,審議區塊仍附(oracle 證據是工具真兆,不因 LLM 敘述失格而消失;claim_text 標示規則照 §1.4)。

#### 2.3.1 命門變更明文化(批判 2b 修;拍板點 P3)

oai_compat.py L8 現行聲明「對全部表唯讀零寫(命門 5/6)」——ultracode 檔啟用後**此聲明不再全真**:effort→`engine.deliberate` 會 INSERT `deliberation_session`/`deliberation_claim`、UPDATE heartbeat(engine.py:40-61),verify_claim 寫 verdict/escalation。定稿處置:

1. **命門修訂文字(隨 F1 落檔頭)**:「對**諮詢資料面**(knowledge_*/philosophy_*/feature/prediction/chat_*)唯讀零寫不變;**唯一例外=deliberation_* 審議帳本**,且僅經 deliberation package 既有寫點(ledger/verifiers/engine),advisor package 自身零 SQL 寫入語句」。
2. **程式層保證**:effort.py 不含任何 INSERT/UPDATE 字面(file_grep 可驗,V2 併驗);寫入全在 deliberation package 內。
3. **DB 角色雙保險(對齊 §4.3 鐵則 1)**:是否為 advisor 服務建專用 DB 角色(對 deliberation_* 以外 REVOKE 寫權)→ **拍板點 P3**;建議=F1 先程式層+file_grep 稽核,角色分離與 F3(後台母幹化本就要 REVOKE 證明)併案做,不在 F1 順手擴 scope(#3 最小邊界)。

#### 2.3.2 fail-closed 落點(批判 3a 修)

`do_POST` 重排:讀 body → JSON 解析 →(tiers enabled 時)`effort.resolve_tier(body.get("model"))` → **未知 tier → `_send_json(400,…)` 即返,此時尚未送任何串流 header** → 才進 `send_response(200)`+role chunk+worker。非串流分支同序。已 200 後之例外維持 `[augur-error]` chunk(既有語意)。驗收 V7:`stream:true`+未知 model 實測回 HTTP 400。

### 2.4 進度回饋(分鐘級延遲的 UI 誠實;批判 3b 修)

現況偽 SSE 只先發 role chunk;`engine.deliberate` 無 callback、進度=print stdout(實查)。改法(stdlib 內):

- **engine 側(最小改)**:`deliberate(…, progress_cb=None)`——propose 前、每 claim 裁決後呼叫 `progress_cb("claim 3/6 裁決中(lens=skeptic)")`;None=現行 print 行為不變。
- **oai_compat 側**:串流分支將 `chat_completion` 移入 worker thread;主線程自 `queue.Queue` 取事件,每事件發一個 `\n---\n[augur-progress] …` 段落 chunk;閒置 >`heartbeat_idle_s`(config,預設 15s)發空 delta heartbeat。進度行=零-LLM 機械模板。
- **前端(雙處濾,批判 3b 核心)**:`renderStream`(L347)**與完成路徑(L364-366 組 body → L388 `recordMsg`)兩處**皆把段首 `[augur-progress]` 之段濾至狀態列——濾後才落 `chat_message`,**進度行不落歷史、不隨重試重播**(驗收 V8)。
- 總預算受 chat_ui 上游 1800s timeout 外框約束 → config 之 engine `timeout_s`/claims/rounds 預設值以單審議(≤6 claims)為準,panel 僅在預算內選配。

### 2.5 DB 開關 `frontend_tiers`(#29b;批判 3c 修)

- **落點**:`deliberation_engine_config` **INSERT 一列**(非新表;現表僅 `fast_anchor_rules` 一列,DB 實查),`enabled:false` 隨程式先落。
- **翻開**:GATE(`gate_663fecd41783`)+A5 復審過(用戶已核之對接條件)→ 用戶拍板後 `UPDATE deliberation_engine_config SET config=jsonb_set(config,'{enabled}','true'), config_sha=<重算>, updated_at=now() WHERE config_key='frontend_tiers'`。AI 不擅翻(#26 護欄)。
- **讀取**:`engine_config.load_rules` 增 `fresh=False` 參數(#12 config 讀取單一住所;`_CACHE` 進程快取若沿用,翻旗標還得重啟服務——正是 memory「改常駐服務須重啟」教訓的反面設計)。`effort.load_tiers()` **自管 `db.connect()` 短連線**(load_rules 需外部游標之實查對策)每請求 fresh 讀單列(單列 SELECT,成本可忽略),**翻開即生效、免重啟**。
- **失敗語意(誠實規畫)**:config 讀取遇 DB 例外 → **fail-safe 回 `{"enabled":False}`+stderr log 一行**,整條請求走 legacy 現行路徑、不 500(檢索層若同時斷線,其自身錯誤照既有語意誠實揭露,不由 tiers 層掩蓋)。
- **關閉態=現行為**:缺列或 `enabled:false` → 回 `{"enabled":False}`,oai_compat/chat_ui 全部走現行路徑(fail-safe 保守,同 `fast_anchor_rules` 缺列全關前例)。

### 2.6 並發護欄(批判 4b 修;4GB 現實)

- **ultracode 單飛鎖**:effort 模組級 `threading.Semaphore(cfg.ultra.max_concurrent)`(預設 **1**,住 config)。非阻塞 acquire 失敗 → **不排隊、不啟 engine**,即時回機械誠實句(零-LLM 模板):「審議引擎使用中(單飛):另一場審議進行中,其帳本將完整落庫。請稍候再送,或改用 fast/think 檔。」——此為服務狀態句(同 `[augur-error]` 層),非 guard 閉集變更。
- **孤兒審議誠實記帳**:AbortController 只斷前端;server 端 engine 續跑至完成、session/claim/verdict 照落帳(誠實非 bug)、鎖於完成時釋放——UI 忙碌句已明示此事。
- **fast/think 檔**:不加應用層鎖——Ollama 端本就序列化排隊,併發只是排隊變慢(誠實延遲已標示);1800s 外框為最終護欄。ThreadingHTTPServer 全域上限不在本計畫動(現況風險=既有,非本計畫引入;若要加列後續小計畫,不順手擴 scope)。
- 驗收 V9:雙併發 ultracode 請求 → 第二個 <2s 內收到忙碌句、`deliberation_session` 僅新增 1 筆。

---

## §3 表與程式雙落實(憲章 v1.39.0;批判 1a 修)

### 3.1 所讀既有表 schema(2026-07-11 information_schema 實查;**本計畫新表=0、新 DDL=0**)

**寫入面總結**:審議結果落 `deliberation_session/claim/verdict/escalation` 既有四表(僅經 deliberation package 既有寫點);config 落 `deliberation_engine_config` 既有表 INSERT 一列;`chat_message` 由 chat_ui 既有路徑寫(內容經 §2.4 過濾)。

```
deliberation_engine_config            -- 開關+tier 定義住此(#29b);INSERT frontend_tiers 一列
  config_key text NOT NULL (PK) | config jsonb NOT NULL | config_sha text NOT NULL
  | updated_at timestamptz NOT NULL
  現況列:fast_anchor_rules(sha 78d2a81d63204531)

deliberation_model_probe              -- /api/tiers 現算 tok/s 之唯一來源(#9(b))
  probe_id bigint | run_at timestamptz | model_tag text | task_kind text | prompt_chars int
  | prompt_eval_count int | eval_count int | load_ms bigint | prompt_eval_ms bigint
  | eval_ms bigint | total_ms bigint | tok_per_s numeric | gpu_mem_used_mb int | note | git_sha
  現況:qwen3:4b avg 17.1(anchor 15.6/propose 18.0/structured 17.7,各 n=3)
       qwen3:8b avg 6.7(7.7/5.9/6.6)

deliberation_session                  -- engine 寫;effort 唯讀(report/進度)
  session_id text | topic text | draft_path | as_of date | status text | coverage jsonb
  | model_tag | created_at | heartbeat_at | finished_at | duration_s numeric

deliberation_claim                    -- engine/ledger 寫;§1.4 區塊讀
  claim_id bigint | session_id text | perspective text | category text | claim_text text
  | anchor text | assigned_verifier text | status text | provenance jsonb | created_at
  | semantic_bound boolean NOT NULL   -- B1 二級制依據欄

deliberation_verdict                  -- verify_claim 寫;§1.4 背書數字唯一來源
  verdict_id bigint | claim_id bigint | verifier text | verdict text | evidence text
  | is_deterministic boolean NOT NULL | ran_at

deliberation_escalation               -- 人裁佇列;§1.4 ⚠ 行依據
  escalation_id bigint | claim_id bigint | reason text | payload jsonb | resolved boolean
  | resolution text | resolved_at | created_at
  現況積壓:unresolved 77=undecidable 76+no_oracle 1(P4)

chat_message                          -- V8 驗「進度行不落此表」
  message_id bigint | session_id bigint | role varchar | content text
  | guard_pass boolean | created_at
```

### 3.2 `frontend_tiers` config 內容規格(INSERT 之 jsonb;操作值全住此、UPDATE 可調零改碼)

```json
{
  "enabled": false,
  "default_tier": "augur-8b-fast",
  "tiers": {
    "augur-4b-fast":  {"model": "qwen3:4b", "effort": "fast"},
    "augur-4b-think": {"model": "qwen3:4b", "effort": "think"},
    "augur-4b-ultra": {"model": "qwen3:4b", "effort": "ultra"},
    "augur-8b-fast":  {"model": "qwen3:8b", "effort": "fast"},
    "augur-8b-think": {"model": "qwen3:8b", "effort": "think"},
    "augur-8b-ultra": {"model": "qwen3:8b", "effort": "ultra"}
  },
  "effort_params": {
    "fast":  {"think": false, "temperature": 0.15, "num_predict": 900,  "timeout_s": 300},
    "think": {"think": true,  "temperature": 0.15, "num_predict": 4096, "timeout_s": 900}
  },
  "ultra": {"engine_model": "qwen3:4b", "mode": "single", "max_claims": 6,
            "engine_timeout_s": 240, "max_concurrent": 1,
            "eligibility_keywords": ["表", "欄位", "schema", "列數", "檔案", "隔離", "import"]},
  "progress": {"heartbeat_idle_s": 15}
}
```

(think 之 num_predict 4096/timeout 900=GATE `think_spec` 預註冊值定錨;fast=serve_advisor_openai.py L59-61 現行參數凍結;eligibility_keywords 為資料側詞表、誤放行僅得 escalated 不損誠實。)

### 3.3 python 程式規畫表(檔・函式・簽名・輸入輸出表;含純讀寫角色)

| 檔(動作) | 函式/職責 | 簽名(輸入→輸出) | 讀表 | 寫表 |
|---|---|---|---|---|
| `src/augur/advisor/effort.py`(新增) | config 讀取 | `load_tiers() -> dict`——自管 `db.connect()` 短連線+`load_rules(cur,'frontend_tiers',fresh=True)`;缺列/DB 例外→`{"enabled":False}`+log | deliberation_engine_config | — |
| 〃 | tier 解析 | `resolve_tier(model_field: str\|None, cfg) -> Tier(id, model, effort)`——`augur-advisor`/None→default_tier;未知→raise `UnknownTierError`(handler 轉 400) | —(純函式) | — |
| 〃 | llm 工廠 | `make_tier_llm_fn(tier, cfg) -> Callable[[str],str]`——fast/think 參數→`ollama.make_llm_fn`;think 檔包截斷偵測(strip_think 後空→機械誠實句) | — | — |
| 〃 | 速度顯示 | `probe_speed(model_tag) -> float\|None`——`SELECT round(avg(tok_per_s),1) … WHERE model_tag=%s`;無列→None(UI「未量測」) | deliberation_model_probe | — |
| 〃 | eligibility+標的 | `route_ultracode(query, cfg, cur) -> (eligible: bool, topic: str, target_block: str)`——§2.2/2.2.1 機械規則 | information_schema.tables(表名比對) | — |
| 〃 | ultracode 執行 | `run_ultracode(query, cfg, progress_cb) -> UltraResult(session_id, rows, escalations)\|None`——單飛鎖→`engine.deliberate`;鎖忙→BusyResult(機械忙碌句);不合格→None(fallback) | deliberation_claim/verdict/escalation(結果回讀) | **零直接寫**(寫入全在 engine/ledger/verifiers 既有寫點;effort.py 零 INSERT/UPDATE 字面,file_grep 可驗) |
| 〃 | 裁決區塊 | `verdict_block(result) -> str`——§1.4 分級機械模板(含雙標示+尾註兩句) | —(吃 UltraResult) | — |
| `src/augur/advisor/oai_compat.py`(修改) | `models_payload(cfg)` 依 enabled 列 tier(附 `augur_tier` 擴充欄,§3.4);`chat_completion(body, …, tier)` 回應 `model`=tier id;`do_POST` tier 解析前移+worker thread/progress queue;檔頭命門聲明修訂 | — | 同現行(諮詢面唯讀) | — |
| `src/augur/deliberation/engine.py`(修改,最小) | `deliberate(topic, target_block, lens, model, n, timeout, progress_cb=None)`——None=現行 print 不變 | 同現行 | 同現行(session/claim;heartbeat) |
| `src/augur/deliberation/engine_config.py`(修改,最小) | `load_rules(cur, key='fast_anchor_rules', fresh=False)`——fresh=True 跳 `_CACHE` | deliberation_engine_config | — |
| `scripts/serve_chat_ui.py`(修改) | 雙選單 UI(tier id 組裝)、`fwd["model"]`=所選 tier、`GET /api/tiers`(轉發塑形 §3.4)、renderStream+完成路徑雙濾 `[augur-progress]` | chat_message(既有) | chat_message(既有路徑;內容濾後) |
| `scripts/serve_advisor_openai.py`(修改) | 啟動時載 config、注入 llm 工廠;disabled→現行單 llm_fn 路徑 | — | — |

### 3.4 `/api/tiers` 端點定義(批判 1d 修)

- **advisor 側(SSOT)**:`GET /v1/models` 於 enabled 時每項附擴充欄(OpenAI 協定容忍額外欄):
  `{"id":"augur-8b-ultra","object":"model","owned_by":"augur","augur_tier":{"model_tag":"qwen3:8b","effort":"ultra","tok_per_s":6.7,"engine_model":"qwen3:4b","label":"8b·ultracode(審議引擎=4b;白話=8b;分鐘級)"}}`——`tok_per_s`=`probe_speed()` 現算,無資料→`null`(UI 顯「未量測」);disabled→現行單列(零擴充欄)。
- **chat_ui 側**:`GET /api/tiers`(登入後)→ 轉發 `/v1/models` 並塑形 `{enabled, default_tier, tiers:[{id,label,tok_per_s,…}]}`;advisor 不可達或 disabled → `{"enabled":false}` → UI 隱藏選單、modelpill 維持現行。
- 驗收:V4 併驗(grep 無 17.1/6.7 字面+回傳值與 DB avg 一致)。

---

## §4 後台「驗證母幹」分層落地(Q2 已裁原則之展開,不重辯)

### 4.0 分層判準(引用,一句話)

Q2 已裁:**交付物=「裁決/審查/驗證一個宣稱」→ 審議引擎當母幹;交付物=「確定性落地/機械閘」→ 維持確定性工具,不包 LLM**;一功能兩者混雜 → 拆列為「混合」,逐段歸邊。全類共同不變式(不因母幹化鬆動):

- LLM 意見零證據力——唯 oracle `verify_claim`(`src/augur/deliberation/verifiers.py`)寫 confirmed;`panel_judge` soft 排序零 confirmed 權。
- escalated=誠實「待人裁」非失敗,唯一去向=`deliberation_escalation` 佇列 → `scripts/resolve_escalation.py`。
- 機械閘(guard 閘鏈/staging BEFORE INSERT trigger/`validation_evidence` SELECT 白名單/DB CHECK)一字不動——母幹化=**前置補強,不取代**。
- 涉治權判準之宣稱 → `redlines.consult` 觸線(4 antileakage_column+5 doctrine_file 死設定)→ 強制 human,oracle 證據僅供人參考。

### 4.1 後台功能盤點總表(逐項三類+理由;住所皆實查)

| # | 後台功能 | 住所(實查) | 分類 | 理由 |
|---|---|---|---|---|
| 1 | 常綠驗證編排 daily_green | `scripts/daily_green.py`(smoke/regression/shadow/delib-watch 四段) | **維持確定性** | exit-code 語意的機械綠檢編排;其 `delib-watch` 段已是審議佇列監看(warn-only,已落地),編排本身包 LLM=降級 |
| 2 | 證據帳本重驗:sql/script_exit 列 | `scripts/verify_validation_evidence.py`(SELECT 前綴白名單+命令白名單) | **維持確定性** | 這兩型本身就是 oracle 同構物(db_query/script exit);`--strict` 之 GATE 前置語意不得混入軟裁決 |
| 3 | 證據帳本重驗:**manual 列** | 同上(manual 型現況=跳過待人審) | **母幹化(前置)** | 人審前無任何結構化攻防;panel 可先產「前置檢查報告+可機驗子宣稱之 oracle 證據」,人仍唯一 green 寫點 → 明細 4.2-A |
| 4 | 深抓來源審批(proposed→active 狀態機) | `scripts/migrate_source_governance.py`(M1-M5+review_log+staging trigger) | **母幹化(前置)** | 准入判準(license 軌/納排範圍/能抓≠該抓)=多視角裁量,天然 panel 題;涉治權文字必觸 doctrine_file redline → 強制人裁 → 明細 4.2-B |
| 5 | 知識入庫晉升(機械段) | `scripts/promote_knowledge.py`(冪等去重+entity mapping) | **維持確定性** | mapping=schema 知識=code;冪等晉升包 LLM 徒增不確定性 |
| 6 | 入庫疑難列(dedupe 邊界/license 疑義/domain 歸屬) | `knowledge_staging` 待審流(promote 之上游) | **母幹化(前置)** | 裁量型判斷;oracle 可驗子宣稱(重複計數/DOI 正規化命中)先機驗,殘餘 escalated 人裁 → 明細 4.2-C |
| 7 | admin 治理呈現 | `scripts/serve_admin_console.py`(:8500) | **維持確定性** | UI/認證/觸發器零 LLM;F3 僅選配加「人裁佇列」唯讀頁(呈現層,resolve_escalation 之 web 鏡像) |
| 8 | distill 校驗 S5 | `scripts/advisor_distill_validate.py`(guard 閘前置+grounding) | **維持確定性** | 界線-B 機械保證;鬆動即違「不放流暢唬爛入訓練集」 |
| 9 | 審議→蒸餾橋 | `scripts/bridge_deliberation_distill.py` | **已是母幹接點(維持現狀)** | 只橋 oracle 裁決過者;escalated/undecidable 不入題——現行設計即正解,零改動 |
| 10 | market sync | `scripts/full_market_sync.py`/`sync_macro.py` | **維持確定性** | FREEZE 休眠+#24 三層防護;純機械 |
| 11 | feature build | `scripts/build_feature_panel.py`/`rebuild_feature.py` | **維持確定性** | anti-leakage 由 code+提拔關卡管;LLM 不得碰 |
| 12 | embed | `scripts/embed_knowledge.py`/`embed_philosophy_chunks.py` | **維持確定性** | e5-small 口徑機械;向量口徑混入 LLM=污染檢索 |
| 13 | guard 閘鏈 | `src/augur/advisor/guard.py`(**口徑定錨:`guard()` 總閘+guard_knowledge/guard_empty_retrieval/guard_attribution/guard_definition 四具名子閘,合稱「guard 閘鏈(五函式)」**;回歸檔頭「五閘」=同一鏈之函式計數,草稿「四閘」=四具名子閘——批判 3d 修) | **維持確定性(治權紅線)** | 諮詢紅線不因 ultracode 鬆動;審議產出進前台仍全過 guard |
| 14 | 特徵提拔/經濟驗證關卡 | `scripts/verify_candidate_promotion.py`/`scripts/run_economic_eval.py` | **維持確定性** | 數字裁決=統計關卡(#11);LLM 對數字零證據力 |
| 15 | 機械審計類 | `scripts/audit_domain_hygiene.py`/`verify_hygiene.py` 等 | **維持確定性** | SQL 審計機械;其發現之「真兆/假兆詮釋」屬 #28 理解層=**Claude 保留區,不外包 qwen** |
| 16 | L2 每日自主審議 | `scripts/run_daily_deliberation.py`+`deliberation_daily_topic`(現 3 題全 enabled,DB 實查) | **母幹本體(已備)** | F2 掛 cron 即上線;增題=INSERT 一列(#29b) |

### 4.2 母幹化項明細(topic 形態/escalated 去向/與既有機制關係;表與程式雙落實 #20)

**A. validation_evidence manual 列前置檢查(F3 第一項,風險最低)**
- topic 形態:每 manual 列一 topic——「證據列 `<evidence_id>` 之斷言於今日 DB 仍成立?」;target_block=該列斷言全文+note+最近 status;`engine.deliberate_panel`(3 lens 住 DB,max_rounds 2)攻防,panel 拆出的可機驗子宣稱(表存在/列數/欄語意)交 `db_query`/`information_schema` oracle。
- escalated 去向:`deliberation_escalation`(no_oracle/undecidable)→ `resolve_escalation --list` 人裁;裁後由**人**手動 UPDATE `validation_evidence`——**green 唯人寫,引擎對該表零寫入權**。
- 與既有機制:補強不取代——`verify_validation_evidence.py --run` 之 sql/script 列照舊、`--strict` 語意不變;manual 列從「純人肉」升級為「panel 前置報告+部分 oracle 證據+人終裁」。
- 表與程式:**新表 0**(落 `deliberation_claim/verdict/escalation` 既有表,provenance 帶 evidence_id 溯源);薄接線 script(建議名 `scripts/precheck_manual_evidence.py`,#18 動詞片語,F3-A 小計畫定案)——職責:讀 manual 列 → 組 topic → panel → 印報告+落審議帳本;輸入=`validation_evidence`(唯讀),輸出=deliberation_* 三表。

**B. 深抓來源審批前置(F3 第二項,涉治權)**
- topic 形態:「來源 `<source_key>` 依憲章准入判準(license 軌/納排範圍/能抓≠該抓/domain 隔離)應否轉 active?」;target_block=`knowledge_source` 該列 14 治理欄+`probe_knowledge_source.py` 實測摘要。
- redline:治權判準文字必觸 doctrine_file 觸線 → assigned_verifier 強制 human_claude;oracle 只驗機械子宣稱(license 欄值/CHECK 存在/probe 回應碼)。
- escalated 去向:同佇列;人裁 approve 後仍走**既有**審批動作(人更新狀態機+review_log 留痕);staging BEFORE INSERT trigger(fail-closed 第三層)一字不動。
- 表與程式:新表 0;建議名 `scripts/precheck_source_approval.py`——讀 proposed 列 → panel → 建議書印出+審議帳本 ref(是否回寫 review_log 備註欄,F3-B 小計畫依該表實際欄位定案,不預設)。

**C. 知識入庫疑難列前置(F3 第三項)**
- topic 形態:「staging 列 `<staging_id>` 之 `<疑點>`(重複合併/license 歸軌/domain 歸屬)應如何裁?」;oracle 可驗部分=db_query(重複計數/norm_doi 命中)。
- escalated 去向:同佇列;人裁後人跑 `promote_knowledge.py --dry-run` 確認再晉升。
- 與既有機制:promote 冪等引擎零改動;**僅疑難列掛審、非全量**——全量掛審=噪音+浪費。

**觀察名單(不承諾,F3 完成後另議=拍板點 P5)**:distill S4 teacher gold 抽樣復審、benchmark 題庫增補審——先看 A/B/C 實跑效益再談。

### 4.3 母幹化三鐵則(全項共通)

1. **引擎唯讀,審議帳本唯一寫點**——對目標表(validation_evidence/knowledge_source/knowledge_staging)零寫入權,程式層+DB 角色雙保險。
2. **決策動作(green/approve/promote)唯人執行**,走各功能既有路徑——靈魂「系統建議、人決策」。
3. **每項獨立落地獨立回退**(topic 種子 DELETE+接線 script 移除=完全復原),逐項 #19 過目後才進下一項。

---

## §5 分階段(F0→F3;各階段 GATE/回退/成本誠實)

| 階段 | 內容 | GATE(進下一階段條件) | 回退 | 成本(誠實) |
|---|---|---|---|---|
| **F0** | 本定稿(§0–§7)用戶過目,裁定拍板點 P1–P6;批判若有第 5/6 軸於此補列 | 用戶核可 | n/a | 零 Claude 執行 token(計畫=理解層,已花) |
| **F1** | 轉接器+UI 落地,**旗標關、零行為變**:§2.0 改動面總表全部(effort.py 新增+oai_compat/engine/engine_config/chat_ui/serve_advisor 五檔修改);chat UI 雙選單(tok/s 顯示=取 `deliberation_model_probe` avg 現算,**不硬編 17.1/6.7**);旗標列 INSERT(enabled=false,#29b);oai_compat 檔頭命門聲明修訂(依 P3 裁定文字);**實測 think 檔(4b/8b)與 ultracode 檔端到端延遲並落 UI 標示,不用估算值**(V10) | §6 V1/V4/V7/V8/V10(旗標關 byte-同確定性回歸;手動翻開冒煙一次後翻回) | 旗標本來即關;新增檔案+五檔 diff 可整組 revert,零遷移、零 DDL | 零 Claude token(本地開發+qwen 實測) |
| **F2** | 翻旗標+掛 L2 cron | **前置=GATE+A5 雙過(用戶已核此對接,本計畫不另設新門)**:① `gate_663fecd41783`(deliberation_bench_batch 預註冊,三臂×3 seeds,run `dlrun_8bcf7470c87c` 現 running)完跑且逐條過預註冊門檻(min_pp_gain≥15pp、McNemar α=0.05 pooled、engine fc≤min(other) 逐輪且彙總,criteria 以 rules_config_sha=`78d2a81d63204531` 凍結版為準);② A5 復審 pending 人裁解除 | 旗標 UPDATE 一列翻回+crontab 移除一行,秒級,零資料損 | 零 token;人時=A5 復審+escalation 積壓 77 列處置(P4)。**GATE 未過→旗標維持關、cron 不掛、F1 產物靜置零損;不重跑硬凹,補強另立小計畫** |
| **F3** | 後台母幹化逐項:順序 **A→B→C**(風險低→高:A 唯讀對帳本/B 涉治權 redline/C 涉入庫流);每項=最小計畫(#20 比例原則:既定計畫展開,附 topic 種子+script 職責)→實作→實測→**#19 過目**→下一項;DB 角色 REVOKE 雙保險隨 A 項一併落(P3 若裁角色分離,前台 advisor 角色併此做) | 各項 §6 V6 驗收+用戶過目 | 每項獨立回退(4.3 鐵則 3) | 執行全零 Claude token(qwen 本地);Claude 僅計畫與過目(#28 執行/理解二分) |

**成本誠實總註**:全鏈本地 qwen(4b 17.1 tok/s、8b 6.7 tok/s,D1 實測);審議耗時以 run 帳本實測為準——2026-07-11 實查 fast-anchor 6 題 plan 55–100 秒(oracle 快路,**不可外推至深審 panel**;深審時長待 GATE run 落數)。cron 掛載=外部副作用,由用戶執行或當次明示授權(#26)。

---

## §6 驗收總表(全部機械可驗)

| # | 驗收項 | 機械檢法 | 通過判準 |
|---|---|---|---|
| V0 | F2 前置 GATE | SQL:`deliberation_bench_batch` 之 gate_663fecd41783 對應 run(`dlrun_8bcf7470c87c`)完成、結果落庫;逐條比對預註冊 thresholds(arm_config 快照為準) | 三門檻全過+A5 人裁紀錄在案;任一不過=F2 不啟動 |
| V1 | 旗標關=零行為變 | `verify_advisor_regression.py --run --no-llm` 於 F1 合入前後各跑一次比對;file_grep:旗標關路徑零 import effort;`deliberate()` 無 progress_cb 呼叫時 stdout 輸出不變(同 topic 重放比對) | 確定性回歸輸出 **byte-同**(誠實範圍:byte-同僅對 --no-llm 確定性路徑宣稱,帶溫度生成不宣稱 byte-同) |
| V2 | 翻開後裁決區塊誠實 | ultracode 檔回覆含裁決區塊:標題含「宣稱原文=LLM 提出、非系統背書」字樣、每行 claim_text 帶標示、每條 confirmed 引 `deliberation_verdict` id;SQL 抽驗該 verdict 存在且 `is_deterministic=true`;file_grep effort.py 零 INSERT/UPDATE 字面(命門 §2.3.1) | 區塊呈現三態邊界+雙標示;無 verdict id 之 confirmed=FAIL;區塊自稱「零-LLM」=FAIL |
| V3 | escalated 入佇列 | 發一含不可機驗宣稱之測題 → `SELECT count(*) FROM deliberation_escalation WHERE NOT resolved AND created_at>now()-interval '10 min'` | ≥1,且 UI 顯示「待人裁」非錯誤態 |
| V4 | tok/s 實測非硬編+`/api/tiers` | file_grep `serve_chat_ui.py`/effort.py/oai_compat.py 無 `17.1`/`6.7` 字面;`/api/tiers` 回傳值與 `SELECT round(avg(tok_per_s),1)…GROUP BY model_tag` 一致;probe 清空之 staging 測試→顯示「未量測」 | grep 零命中+數值一致+無資料誠實顯示 |
| V5 | L2 cron 活著 | `crontab -l` 匹配 run_daily_deliberation;翌日 SQL `deliberation_session` 當日新增>0;daily_green `delib-watch` 段無殭屍警示 | 三者同時成立 |
| V6 | F3 各項 | topic 種子列 SQL 存在;跑一輪後 claim/verdict/escalation 落帳且 provenance 帶目標列 id;目標表在審議 run 時間窗內**零由引擎寫入**(權限 REVOKE 證明+時戳比對) | 逐項驗,過目後才下一項 |
| V7 | 未知 tier fail-closed(批判 3a) | `curl` 帶 `{"model":"augur-nope","stream":true}` 直打 :8399 → 檢 HTTP 狀態碼;code review:tier 解析位於 `send_response(200)` 之前 | 回 **HTTP 400**(非 200+`[augur-error]` chunk);非串流同 |
| V8 | 進度行不落歷史(批判 3b) | 實測一次 ultracode 對話(含進度行)後:`SELECT count(*) FROM chat_message WHERE content LIKE '%[augur-progress]%'` ;再按「重試」確認不重播進度行 | 0 列+重試無進度殘留 |
| V9 | 並發單飛鎖(批判 4b) | 併發送兩個 ultracode 請求 → 第二個回應時間+內容;窗內 `deliberation_session` 新增數 | 第二個 <2s 收到機械忙碌句;session 僅新增 1 筆 |
| V10 | think 檔截斷誠實+延遲實測(批判 4a) | staging 以人為極小 num_predict 觸發截斷→檢回覆;正常 4096 配置下 4b/8b 各手測一次端到端延遲,記錄並比對 UI 標示 | 截斷→機械誠實句非空字串;UI 標示=實測值(非 §1.2 估算值) |

---

## §7 誠實邊界+不做清單+拍板點

### 7.1 誠實邊界(逐條列管)

1. **不繞 guard**:前台 payload 硬綁不動;審議產出之 narrative 進回覆前仍全過 guard 閘鏈(五函式:`guard()` 總閘+四具名子閘——本計畫口徑定錨,批判 3d);`guard.py` byte-identical。
2. **治權紅線不動**:相對機率誠實/引文 grounding/數字白名單三紅線、redline 9 列死設定(4 antileakage+5 doctrine,redlines.py 實查)全程凍結;semantic_bound 二級制(confirmed·bound vs anchor-only)不變。
3. **理解層仍 Claude(#28 二分)**:qwen 母幹只裁「機械可驗宣稱」;doctrine 詮釋/真兆假兆判讀/審計發現之意義解讀不外包 qwen。**前台 ultracode 檔≠Claude ultracode 全能——UI 須明示此邊界(V2 三態區塊)**。
4. **LLM 意見零證據力**:唯 `verify_claim` 寫 confirmed;panel_judge soft 排序零 confirmed 權——母幹化任何一項皆不豁免。**裁決區塊內 claim_text=LLM 宣稱原文,逐行標示、系統只背書 evidence 行(批判 2a 修)**;白話與裁決不一致時以裁決為準之尾註必附(批判 2c 修)。
5. **8b 吞吐限制明示**:6.7 tok/s(4GB VRAM CPU offload 實測),think 檔最壞 ~10 分鐘、ultracode 分鐘級;UI 顯示進度+實測 tok/s+實測延遲(V10),不佯稱即時。**8b-ultra 之審議引擎=4b,UI label 明示(批判 2d 修)**。
6. **escalated=誠實待人裁非失敗**;現積壓 **77 列(76 undecidable+1 no_oracle,2026-07-11 DB 再驗)**列管 → 拍板點 P4。
7. **pytest oracle 維持 dormant(P-2 裁定不變)**:ORACLES 含 pytest 但不啟用於前台/L2 topic(`fast_anchor_rules.L6_pytest=false`,DB 實查)。
8. **零新 DDL**:本計畫新表=0(全落既有 deliberation_* 表);若 F1 實作發現需擴欄,先回 #19 過目,不順手加。
9. **命門修訂透明(批判 2b)**:前台服務自 F1 起對 deliberation_* 帳本有寫入路徑(僅經 deliberation package 既有寫點);oai_compat 檔頭聲明同步改寫,不留與事實不符的「對全部表唯讀」字樣(#15)。
10. **並發誠實(批判 4b)**:ultracode 單飛,忙碌即說忙碌;前端中止後 server 端審議續跑至完整落帳,UI 忙碌句明示此事。

### 7.2 不做清單

- 不做引擎自動寫 validation_evidence green/自動 approve 來源/自動 promote staging——決策動作唯人。
- 不把 sync/build/embed/guard/提拔關卡包 LLM(§4 已裁維持確定性各項)。
- 不對 claim_text 做 LLM 改寫/摘要後呈現(改寫=第二層 LLM 內容,誠實性更劣;只做機械標示與截斷)。
- 不追新資料(FREEZE as-of 2026-05-31;L2 題庫與母幹化三項全部零市場資料觸碰)。
- 不自行 commit/push;不自行掛 cron(F2 cron=用戶動作或當次明示授權);不自行翻 enabled 旗標(#26)。
- 不做 8b 常駐服務(VRAM 不足以常駐;僅批次/深檔按需)。
- 不在本計畫內動 ThreadingHTTPServer 全域併發上限(既有現況,非本計畫引入;要動另立小計畫)。
- GATE 未過不硬凹:不改判準遷就結果、不換題庫重跑至過——補強另立計畫再預註冊。

### 7.3 拍板點(P1–P6 完整;批判 1a 修)

| # | 拍板點 | 性質 |
|---|---|---|
| P1 | 本定稿整體(§1–§3 前台+§4 分層盤點+§5 階段+§6 驗收)核可;批判第 5/6 軸若存在於此補列 | F0 |
| P2 | F2 對接條件覆核留痕:「`gate_663fecd41783` 三門檻全過+A5 復審解除 → 翻旗標」——用戶已核此對接,此處僅記錄確認、不另設新門(GATE run `dlrun_8bcf7470c87c` 現 running) | F0 記錄/F2 執行 |
| P3 | **命門修訂(批判 2b)**:①oai_compat 檔頭「唯讀零寫」聲明修訂文字(§2.3.1 案文)核可;②是否建 advisor 專用 DB 角色(deliberation_* 以外 REVOKE 寫權)——建議 F1 先程式層+file_grep 稽核、角色分離併 F3-A 的 REVOKE 一起做 | F0 裁 |
| P4 | escalation 積壓 77 列(76 undecidable+1 no_oracle)處置方針:F2 翻旗標前人裁清零,或明示帶帳上線(UI 佇列數誠實顯示) | F2 前裁 |
| P5 | F3 觀察名單(distill S4 teacher gold 抽樣復審/benchmark 題庫增補審)是否續辦——A/B/C 實跑效益出來後再議,本計畫不承諾 | F3 後裁 |
| P6 | **嚴格模式(批判 2a 選配)**:裁決區塊 claim_text 是否加數字白名單同級檢查(claim 內數字 ⊆ evidence∪payload,不符→遮蔽並註明)——預設不開(雙標示已足誠實),開否用戶裁 | F0/F1 裁 |
