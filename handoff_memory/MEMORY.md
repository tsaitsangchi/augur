# Memory Index

## ⭐ 核心基礎（2026-07-30 定案；後續發展一律以此三則為前提）
- [世界建構核心](augur-world-construction-core.md) — **augur＝從零建構的世界 L0-L7**;一條路×八行走者;法屬世界足跡屬域;自反性法源鏈(hugo 五度校正定案)
- [一條路實為六條並行](augur-path-six-parallel-gap.md) — 親驗:3 門表同骨架重複+6 裁決表異質(2 空表)+prodset 真名 evolution_production_feature_set;統一 path_* 三表設計
- [技術底座 20260730](augur-tech-baseline-20260730.md) — 294 表/8.54M/18 package/425 scripts/11 unit(user-level)/ollama 三模型/套件實況(無 peft)
- [全專案重讀・記憶級事實](../../../project/augur/reports/augur_full_reread_facts_20260730.md) — 339 事實/153 踩雷/117 廢棄(12 區逐檔;repo 內全文,此處僅指針)
- [驗證器陷阱 20260730](augur-verifier-traps-20260730.md) — verify_* 非唯讀+四支中位數灌滿覆蓋、reconcile_audit 假綠仍在、rc=0≠通過、門評跨軸(已修)
- [DB schema 陷阱 20260730](augur-db-schema-traps-20260730.md) — raw_* 前綴反義、Dividend PK 塌列根因、ExchangeRate 兩表差 6 年、candidate 表無 guard、reltuples=-1≠空

- [KH0 覆蓋≠品質](kh0-coverage-vs-quality.md) — KH0 底線入憲 v1.52.0(破口 0 已達);**「待人裁」根因=90.3s 逾時、本地AI從未答成**;ollama 無 systemd unit 故 is-active=假訊號;ERP 五錯處;來源層人簽動它會重啟 P8
- [三核 FAIL 九則](kh-verify-fail-three.md) — V-4 逐item全表掃=17天(已修凍結 5.6天→2秒)、V-1 fail-open死碼(已修 fail-closed);**六則未修**含 V-3 一列即解閘、V-5 DISABLE TRIGGER 可卸閘、V-6 假綠自測再犯
- [機械閘三層強度](augur-three-gate-strengths.md) — **硬33表/半14表/軟437支**用同一個詞稱呼=誤判根源;三個親驗假綠(綠燈帳本19/19實有3條false、孤兒佔埠使restart成功卻跑舊碼、人閘零DB強制);優化第一原則=先讓紅燈會亮
- [同尺四查](same-scale-precheck.md) — 07-28~30 六發尺陷阱歸納:A/B 前查覆蓋/網格(hash 自證)/重名/falsy 空集
- [便宜尺寸先行](cheap-scale-first.md) — 昂貴掃描前 preview 打熟引擎(23-cutoff 抓 3 bug 省 73h);sha 含網格自動分家;收 preview 讀帳本驗屍
- [git add 只逐檔明列](git-add-scoped-only.md) — 07-28 實犯:add -A 掃進並行 session 未提交檔;commit 逐檔列+status 先查+--allow-empty 零 add

- [慢可以、提升要精準](slow-but-precise.md) — hugo 07-27 指導原則:速度讓位正確性;驗收用精確計數/凍結尺實測不用估;timeout 放寬不猶豫(advisor 900s);不為快降 draws/seeds
- [兩台電腦同時進行](machines-two-concurrent.md) — 07-27:PC002+DESKTOP 並行非接力;**乙案=本機當家**(進化+arena 正典;DESKTOP 僅週末開=週間 cron 物理不可當家);週末待辦:停 DESKTOP cron+私有通道搬 07-26 增量;GB10 不存在再確認
- [本機 PC002-S1800 硬體](machine-pc002-s1800-hardware.md) — SSOT=ops/machines/PC002-S1800.md;單通道記憶體(hugo 拍板不修、勿再提案);無獨顯無 AVX-512;Trend Micro 企業機;AC 永不睡眠=可跑過夜
- [不代打人簽](never-type-human-signature.md) — **promoted_by/approved_by/decided_by 一律 hugo 親跑寫入**;07-25 實犯(代打 promoted_by='hugo' 使 P5.W2 保證變成我能自行滿足);判斷句「這欄位是不是為了證明某事由人做的?」;已犯列以註記自陳不竄改

- [venv 微調棧未備](venv-finetune-stack-absent.md) — 07-30 親驗:無 peft/trl/bitsandbytes/gguf;LoRA 計畫須先列環境前置 P0+import smoke
- [GB10 不可用](gb10-unavailable.md) — **hugo 07-25 宣告:沒有 GB10、進化只能本機**;07-26 修正:1.7b QLoRA 可行/4b no-go(embedding 不被量化)、GTX1650 無 tensor core 故 bf16 快 3×、CPU LoRA 退場、權重鏈唯 convert_lora_to_gguf 路
- [防呆機制自己靜默失效](guard-mechanisms-that-silently-fail.md) — 四型實犯(欄名錯被except吞/測試靜默skip/斷言掃到自己/字面斷言驗不到真行為);判斷句「這機制若壞了會不會安靜變綠燈?」;先唯讀比對再apply
- [評測樣板地板](eval-boilerplate-floor.md) — **鐵律:宣稱分數代表能力前必跑 ceiling/floor/mismatched 三臂**;07-26 常數字串 0.654>冠軍 0.492;**07-27 新尺同病復發→07-28 已修尺**(V2-RUBRIC-go:robot 第五臂+加料年份否決+真地板;新尺 ef142e9374c1;robot 五格全 1.000=本集無可證格,真訊號唯 S-4 重建)
- [自我進化計畫地貌](augur-self-evolution-plan-map.md) — SSOT=v2 總控(20260726,TRI-v1 降前身);Phase 0/1 ✅(behavior F@L1 0.933=判準A PASS)、Phase 2 焊死待 V2-P-yes;V2-SUNSET 落日 hugo 親填;六條邊/共用零件裁決/I1-I9/H1-H10/明確不做 全錄;⚠讀計畫須帶 07-26 晚更正(arena 已結+每日 cron)
- 【07-25 晚新增,詳細記憶待寫】**憲章已 v1.47.0**(跨域原理映射準則;principle_domain_map 表);**人閘機制 live**(governance_proposal 三表三鎖+governance_queue CLI,首案全循環:v1 審查退回→v2 hugo 人簽→enacted);演化迴圈 evolve_cycle 首輪跑通(gold+50/pack pp_7c55);夜間收割 cron 01:30 已掛(quant_finance/software_engineering 新域);~~venv 新增 peft/trl/dspy/gguf~~〔**07-30 親驗推翻：本機無此四者，見 [venv 微調棧未備](venv-finetune-stack-absent.md)**〕;**演化鏈全自動編排 run_evolution_chain.sh(01:30)+2h 快車道+6h 自我求知;hugo 鐵律:演化教師永久本地化(oracle>8b教4b>人裁)、外部 AI token 歸零、僅 hugo 可反轉**

- [憲章 corpus 已讀 20260723](augur-constitution-corpus-20260723.md) — monorepo 治權全貌：入口 GOVERNANCE-MAP；**MC v1.6**；L1–L7 生效版；領域靈魂／原則／大憲章／CLAUDE；RULING-041 #7 規範閉合；10-14 勿假關
- [AUGUR-MC 上位治權體系](augur-mc-upper-governance.md) — **MC v1.6 原文在 `constitution/`**（不再「不在本機」）；領域 Layer 登錄；#7↔P4.E5 規範已閉（RULING-041）；AUD-02 code 仍受閘；2026-10-14 日曆項勿假關
- [機械閘缺口盤點](augur-mechanical-gate-gaps.md) — **07-25 兩項已封:①兩帳本表 honesty trigger 上閘(DELETE 拒/UPDATE 綁 GUC 通行證,migrate_honesty_guards_ddl.py)②vol_target #8 前視親驗 CONFIRMED 已修(幸生產零呼叫)**;殘:base_rate寫死0.5、全新DB trial_ledger UNIQUE 7vs8欄、refetch_fixed_tables無參數=DROP+放量、feats_hash/deflated_floor 疑空轉未親驗
- [跨宣稱矛盾檢查](cross-claim-contradiction-check.md) — 對抗驗證抓不到跨章矛盾(v4 §3.3vs§8.3自打架存活58agent);鐘擺型記憶自帶權威口吻最危險;索引/frontmatter/內文三處各自漂移;無對抗層深讀結論須標【親驗/單域/索引時效】級別
- [PriceAdj修復=減資非除息](priceadj-repair-capital-reduction.md) — 175檔「除息誤標」真機制=減資(1109在減資表親驗);結構反證=除息使factor上跳不可能觸發guard;⚠backlog照「排除除息日」字面實作只消5/250、殘留245會白打FinMind撞#24
- [alpha Phase1 錨修復鏈](alpha-phase1-anchor-repair.md) — 簽核錨 1.1321(hugo,另一台機器);⚠本機07-16快照 dry-run=1.1302/DSR 34.3%(差0.0019=PriceAdj快照漂;DSR「47.9%」查無來源、真值≈34.5%@N=32);PriceAdj 41真損傷/175減資誤標(非除息);7候選全滅headline未動;踩雷四型
- [arena 前置 G1-G5 機制計畫](arena-g1g5-admission-plan.md) — unfreeze gate 退史料;arena 前置改 G1-G5;Phase 0 **全7顆已拍板**、gate evaluated_pass、**arena 已開賽(4,128列/8隊/結算0)**
- [audit 假綠+v1.28 自測入憲](audit-attestation-falsegreen.md) — audit「PASS」曾假綠(死表空視窗靜默PASS);⚠**射程註記:reconcile_audit.py 仍會假綠**(不呼叫 verdict()、:158 自算漏 coverage_gap);v1.28 library 自測CLI;死表=本機漏sync可補
- [件A admission 硬化+健檢](jian-a-admission-hardening.md) — 對抗審查 R1-R6 硬化+verify_knowledge_admission_health.py 日常哨兵;**live-vs-repo drift 教訓**:驗 DB 層宣稱查 live DB 非只 grep repo(chk 存 live 但曾無 migration)
- [Qdrant serving+HNSW over-filter 陷阱](qdrant-serving-hnsw-overfilter.md) — augur-qdrant.service 上線(07-14 拍板);pgvector HNSW+CLEAN WHERE over-filter 假空/假FAIL 鑑識法=exact baseline;Qdrant 只服務 public、private 走 pgvector
- [背景作業須可見](background-tasks-visible.md) — 每個背景 shell 都要 TaskCreate 登記+更新狀態，用戶介面才看得到；不得靜默跑（2026-07-13 directive）
- [建構理解 v4](augur-construction-v4.md) — 20260713 報告指針(58-agent深讀+12 REFUTED+終審16修);三塊架構;斷線清單(predict role未接線/A3=preregistered〔有2026-08 deadline〕);⚠**redline失聯已修(redlines.py 在)、macro埋雷為假(macro_vintage.py 07-11 已在=v4 §8.3 自相矛盾)**
- [記憶 export 密碼掃描](memory-export-secret-scan.md) — sync_memory export 全量推 public repo；記憶不存明碼憑證、commit/push 前必掃密碼（2026-07-13 差點洩漏 ttai admin 密碼）
- [DB 匯入調優+HNSW OOM 陷阱](db-import-tuning-hnsw-oom.md) — HNSW×並發=記憶體乘數OOM(07-17又踩:IDX_MEM 4GB×-j2>/dev/shm 7.8G);**07-25 極限版調優已 ALTER SYSTEM 持久化**(sb=6GB/wm=256MB/mwm=2GB封頂+維護並行2=OOM護欄),匯入前仍實查 pg_settings;information_schema漏報IDENTITY須用pg_class;大檔匯入SOP
- [Git 身分在 .env](git_identity_in_env.md) — commit 遇身分未設時查 .env 的 `git config --global` 指令,不問用戶、不自設
- [augur 專案地圖](augur-project-map.md) — 治權 SSOT(憲章v1.46.0/CLAUDE v1.29;受上位 AUGUR-MC v1.3)+ 程式地圖(15 package)+ 知識/哲學/顧問層 + 兩機/dump/token 約束(⚠內文 v1.20-v1.25 為史料細節)
- [知識三部曲+哲學顧問層](augur-knowledge-philosophy.md) — 八層金字塔、命門7條、隔離不變式、T/W 工具鏈、review_flag 三態、e5-small 嵌入口徑、版權三軌五值(owned_local 佔96.8%)、未實作債
- [augur 特徵值全貌](augur-feature-values.md) — 產生器地圖 + feature_values 35特徵/**36 panel/2.51M 列(廣宇宙3,093檔非core 344)**;⚠**35產生≠29入模**(6個被交集gate剔除,含康波C4兩支);headline 1.26=2026-06史料(現1.1302)
- [三鏡頭研究報告](augur-three-lens-research.md) — 第一性/八二/康波思想根源精萃 + 各鏡頭關鍵教訓與批判(α≈1.16 才給80/20、康波實證最弱故數字最不可回流、Bessembinder 4%股造全部財富)
- [特徵發現工具鏈](augur-feature-toolkit.md) — 標準流程(探索→候選→四道漏斗→經濟驗證→穩健終關)工具用法 + 判準魔數 + 鐵律教訓(覆蓋假象/強單因子≠增量/已淘汰名錄)
- [Raw Data 定義字典](augur-raw-data-defs.md) — 全84表據實 profile + 跨表髒值/語意陷阱(財報單季/累計YTD、**close=0=權證空報價非停牌**、**PER=0才是哨兵(23.5%)、PER=-1僅2列**、發布日gate 15日、月營收=元、Dividend塌列~92%消滅)
- [改常駐服務後須重啟](restart-systemd-after-edit.md) — 改 serve_*.py/src 後須 systemctl restart 對應服務再實測(http.server 不熱更新;CLAUDE #7);附停電/重開機災後檢查序+ollama unit 排序循環已修(2026-07-11)
- [限額錯誤處置紀律](quota-error-discipline.md) — API 限額錯誤≠定論,先請用戶看儀表再下判斷;失誤成本實例 2026-07-04
- [跨機接續交接](cross-machine-handoff.md) — 現行 SSOT=repo HANDOFF.md;**DB=augur_pgdump_20260718_Fd.tar(年代≈07-16、缺07-17重定錨)**、記憶隨repo遷移、**v4建構理解 20260713**;⚠**DB狀態不隨git;crontab/systemd/Qdrant皆機器本地須重掛**
- [本地接續工具](local-handoff-tooling.md) — **五支**零-usage工具(resume_project/sync_from_github/sync_memory/import_database/read_handoff)+ 記憶隨repo遷移機制(export→commit→新機restore)
- [預言機方向拍板(史料)](augur-oracle-pivot.md) — 轉向當日紀錄;現況見 verdict/v2-plan/unfreeze 三檔
- [驗證總綱 V0-V2](augur-validation-master-plan.md) — 證據帳本/R軌/解凍GATE hugo 親簽;#8 修 4 洩漏;canonical 29 特徵(⚠headline實際口徑可能為34特徵、待釐清)
- [審議引擎+前台檔位](augur-deliberation-engine.md) — GATE PASS 效力成立;**F1 已開閘、L2 已掛且首個全自動日完成(07-12)**;A5 七片全 ✅
- [預言機方向軸判決](augur-oracle-direction-verdict.md) — 六門(H20/40/82/120+D1/D5)全判死/never_shown;建置鏈+踩雷+MC模擬情境(逐日股價唯一合法答法、四鎖硬綁模擬非預測)
- [方向軸 v2 復活計畫+終局](augur-oracle-v2-plan.md) — **v2 全家族判死(二次證偽)**:D5 hit p=.072(灌水懷疑實證)、Brier 四門全敗;方向軸凍結至解凍+新資料、不開 v3;結案報告待親簽
- [FREEZE 解凍+四項親核](augur-unfreeze-20260712.md) — 2026-07-12 解凍入憲(v1.9.0/v1.43.0);no-v3 入憲;殘餘=FinMind 續訂+E 債裁定→unfreeze evaluate→arena 開賽
- [輸出契約入憲+三鏡頭候選](augur-output-contract.md) — 三度堅持刪句(靈魂v1.8.0/憲章v1.46.0):E[r]升格幅度級得逐股;**A3 已拆彈(07-25 hugo 甲′)**:own_threelens retired+三門 superseded(原「已簽」為假、以DB為準之教訓留檔);Wave1 R4+activate 完

## 本機封存記憶（2026-07-09 前舊索引；上方新索引為現況權威；史料檔仍在、recall 可讀，各檔內文警語為準）

- 紀律類仍有效：[有界自主模式](bounded-autonomy-mode.md)、[不同時派 agent 改同檔](no-concurrent-agents-same-files.md)、[DB 跨機獨立不隨 git](db-cross-machine-independent.md)、[改治權/commit 前先 git fetch](git-fetch-before-treaty-commit.md)、[Rigor 完整性紀律](rigor-completeness-discipline.md)
- [選股 headline 未 deflate](prediction-headline-undeflated.md) — 數字全過期(已被 07-17 重錨取代)；唯「引用 headline 必附未過 deflation、units bug 揭露」紀律仍有效
- 史料檔（已被新索引對應檔取代，僅考古用；⚠finmind-fetch-methods 之 OUT_OF_UNIT 段方向相反於現行 code）：finmind-data-source／finmind-fetch-methods／fred-data-source／augur-construction-map／augur-data-layer／investment-philosophy-framework／ttai-integration-and-platform／augur_project_overview／core-universe-and-f3-model／feature-execution-plan／asof-completeness／data-source-consistency／ingestion-strengthen
