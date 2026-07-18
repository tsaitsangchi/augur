# Memory Index

- [AUGUR-MC 上位治權體系](augur-mc-upper-governance.md) — ⚠**augur 已受外部憲章 AUGUR-MC v1.3 約束(Layer 0 lex superior)**;四治權檔 Layer 登錄(L1/L4/L6/L7、README無檔頭);AUD-02 critical=原則精華#7違§P4.E5;補正期2026-10-14;三條未併remediation分支;**憲章原文不在本機=本機無法驗證合憲性**
- [機械閘缺口盤點](augur-mechanical-gate-gaps.md) — 最弱防護在最關鍵表(trial_ledger/revalidation_baseline 零DB trigger);base_rate寫死0.5=誠實鎖沒接線;全新DB上trial_ledger建不起來(UNIQUE 7欄vs ON CONFLICT 8欄);refetch_fixed_tables無參數=DROP+放量;vol_target #8前視(未親驗待複)
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
- [DB 匯入調優+HNSW OOM 陷阱](db-import-tuning-hnsw-oom.md) — HNSW×並發=記憶體乘數OOM(07-17又踩:IDX_MEM 4GB×-j2>/dev/shm 7.8G);⚠**該檔10個PG17調優值 live 多已失效(maintenance_work_mem 回64MB)、匯入前務必實查 pg_settings**;information_schema漏報IDENTITY須用pg_class;大檔匯入SOP
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
- [輸出契約入憲+三鏡頭候選](augur-output-contract.md) — 三度堅持刪句(靈魂v1.8.0/憲章v1.46.0):E[r]升格幅度級得逐股;⚠**A3 `_r2`三門「已簽」為假**——live DB 零`_r2`列、原三門仍preregistered/approved_by NULL(以DB為準)、有2026-08 deadline;Wave1 R4+activate 完

## 本機封存記憶（2026-07-09 前舊索引；上方新索引為現況權威，下列可能部分過時、已被新檔取代者以新檔為準）

- [換機工具已改版](machine-switch-tooling.md) — scripts/ 五件組已被根目錄工具組取代(#31);⚠**其指向的封存分支 backup/local-wsl2-20260713(856ab86) 本機不存在**(git branch/rev-parse 皆 fatal)=指針指向虛空、提案建議刪此則
- [FinMind資料源全貌](finmind-data-source.md) — 限流三層防護/rolling視窗/anti-leakage公告欄金礦(細節研究,新索引 raw-data-defs 部分涵蓋)
- [FinMind抓取方法地圖](finmind-fetch-methods.md) — endpoint全集/抓取模式/data_id階層;⚠**內文OUT_OF_UNIT段方向相反於現行code(06-23/24已翻回治權級排除、BACKFILL_DEFERRED=空集)**
- [FRED資料源全貌](fred-data-source.md) — 第二資料源(API事實仍有效);⚠**vintage #8警示已解除**——fred.py早已實作vintage、PK含realtime_start、真vintage已落地
- [augur 建構作法完整心智圖](augur-construction-map.md) — 20260709 版(遠端已有 20260710 v3 報告 supersede)
- [資料層四層理解](augur-data-layer.md) — 94表772欄實證/恆等式/已知bug(新索引 raw-data-defs 為濃縮版)
- [哲學素養框架層](investment-philosophy-framework.md) — 哲學/知識層演進全史(新索引 knowledge-philosophy 為濃縮版)
- [TTAI整合與平台重建](ttai-integration-and-platform.md) — 本機(WSL2)服務端口/密碼/TTAI嵌入/advisor Tier-1
- [Rigor 完整性紀律](rigor-completeness-discipline.md) — 完整性天職/真窮舉到真邊界
- [有界自主模式](bounded-autonomy-mode.md)、[不同時派 agent 改同檔](no-concurrent-agents-same-files.md)、[DB 跨機獨立不隨 git](db-cross-machine-independent.md)、[改治權/commit 前先 git fetch](git-fetch-before-treaty-commit.md) — 紀律類仍有效
- [選股 headline 未 deflate](prediction-headline-undeflated.md) — ⚠**狀態檔非純紀律**:數字全面過期(1.20/DSR 75.6%已被07-17重錨1.1302取代、FREEZE段已因解凍失效);唯「引用headline必附未過deflation/DSR<95%、units bug作廢揭露」之紀律部分仍有效
- 其餘（augur_project_overview / core-universe-and-f3-model / feature-execution-plan / asof-completeness / data-source-consistency / ingestion-strengthen）＝已被新索引對應檔大幅取代之史料
