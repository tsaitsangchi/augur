# Memory Index

- [背景作業須可見](background-tasks-visible.md) — 每個背景 shell 都要 TaskCreate 登記+更新狀態，用戶介面才看得到；不得靜默跑（2026-07-13 directive）
- [建構理解 v4](augur-construction-v4.md) — 20260713 報告指針(58-agent深讀+12 REFUTED+終審16修);三塊架構;斷線清單(redline失聯/predict role未接線/A3=preregistered/本機無491全文/macro埋雷)
- [記憶 export 密碼掃描](memory-export-secret-scan.md) — sync_memory export 全量推 public repo；記憶不存明碼憑證、commit/push 前必掃密碼（2026-07-13 差點洩漏 ttai admin 密碼）
- [DB 匯入調優+HNSW OOM 陷阱](db-import-tuning-hnsw-oom.md) — 3個HNSW索引×pg_restore -j4=maintenance_work_mem並發乘數OOM；information_schema漏報IDENTITY序列須用pg_class；本機WSL2 10GB+PG17調優值；大檔匯入SOP（2026-07-13）
- [Git 身分在 .env](git_identity_in_env.md) — commit 遇身分未設時查 .env 的 `git config --global` 指令,不問用戶、不自設
- [augur 專案地圖](augur-project-map.md) — 治權 SSOT(憲章v1.20/CLAUDE v1.16)+ 程式地圖(含知識/哲學/顧問層)+ 市場層飽和里程碑 + 知識層 W5 前沿 + 兩機/dump/token 約束
- [知識三部曲+哲學顧問層](augur-knowledge-philosophy.md) — 八層金字塔、命門7條、隔離不變式、T/W 工具鏈、review_flag 三態、e5-small 嵌入口徑、版權雙軌、未實作債
- [augur 特徵值全貌](augur-feature-values.md) — 產生器地圖 + feature_values 35 特徵(八二/康波 8 存活+gross_margin_pctile 翻案) + headline + 已修盲點與殘留
- [三鏡頭研究報告](augur-three-lens-research.md) — 第一性/八二/康波思想根源精萃 + 各鏡頭關鍵教訓與批判(α≈1.16 才給80/20、康波實證最弱故數字最不可回流、Bessembinder 4%股造全部財富)
- [特徵發現工具鏈](augur-feature-toolkit.md) — 標準流程(探索→候選→四道漏斗→經濟驗證→穩健終關)工具用法 + 判準魔數 + 鐵律教訓(覆蓋假象/強單因子≠增量/已淘汰名錄)
- [Raw Data 定義字典](augur-raw-data-defs.md) — 全84表據實 profile + 跨表髒值/語意陷阱(財報單季/累計YTD/snapshot、停牌哨兵、PER=-1、發布日 gate 15日、月營收=元、Dividend 塌列)
- [改常駐服務後須重啟](restart-systemd-after-edit.md) — 改 serve_*.py/src 後須 systemctl restart 對應服務再實測(http.server 不熱更新;CLAUDE #7);附停電/重開機災後檢查序+ollama unit 排序循環已修(2026-07-11)
- [限額錯誤處置紀律](quota-error-discipline.md) — API 限額錯誤≠定論,先請用戶看儀表再下判斷;失誤成本實例 2026-07-04
- [跨機接續交接](cross-machine-handoff.md) — 現行 SSOT=repo HANDOFF.md;源碼 GitHub(tag archive-20260712-pregame-allsigned)、DB=augur_pgdump_20260712_Fd(本地目錄+D碟tar)、記憶隨 repo 遷移(sync_memory)、v3 建構理解 20260710
- [本地接續工具](local-handoff-tooling.md) — 三支零-usage 工具(sync_from_github/read_handoff/sync_memory)+ 記憶隨 repo 遷移機制(export→commit→新機 restore),供跨機接續
- [預言機方向拍板(史料)](augur-oracle-pivot.md) — 轉向當日紀錄;現況見 verdict/v2-plan/unfreeze 三檔
- [驗證總綱 V0-V2](augur-validation-master-plan.md) — 證據帳本/R軌/解凍GATE hugo 親簽;#8 修 4 洩漏;canonical 29 特徵
- [審議引擎+前台檔位](augur-deliberation-engine.md) — GATE PASS 效力成立;**F1 已開閘、L2 已掛且首個全自動日完成(07-12)**;A5 七片全 ✅
- [預言機方向軸判決](augur-oracle-direction-verdict.md) — 六門(H20/40/82/120+D1/D5)全判死/never_shown;建置鏈+踩雷+MC模擬情境(逐日股價唯一合法答法、四鎖硬綁模擬非預測)
- [方向軸 v2 復活計畫+終局](augur-oracle-v2-plan.md) — **v2 全家族判死(二次證偽)**:D5 hit p=.072(灌水懷疑實證)、Brier 四門全敗;方向軸凍結至解凍+新資料、不開 v3;結案報告待親簽
- [FREEZE 解凍+四項親核](augur-unfreeze-20260712.md) — 2026-07-12 解凍入憲(v1.9.0/v1.43.0);no-v3 入憲;殘餘=FinMind 續訂+E 債裁定→unfreeze evaluate→arena 開賽
- [輸出契約入憲+三鏡頭候選](augur-output-contract.md) — 三度堅持刪句(靈魂v1.8.0/憲章v1.45.0):E[r]升格幅度級得逐股;A3 `_r2` 三門已簽(sha配方bug已修)、Wave1 R4+activate 完、開賽前置人工關卡全清(07-12 晚)

## 本機封存記憶（2026-07-09 前舊索引；上方新索引為現況權威，下列可能部分過時、已被新檔取代者以新檔為準）

- [換機工具已改版](machine-switch-tooling.md) — scripts/ 五件組已被根目錄工具組取代(#31);舊版+審議W1W2封存於本機分支 backup/local-wsl2-20260713
- [FinMind資料源全貌](finmind-data-source.md) — 限流三層防護/rolling視窗/anti-leakage公告欄金礦(細節研究,新索引 raw-data-defs 部分涵蓋)
- [FinMind抓取方法地圖](finmind-fetch-methods.md) — endpoint全集/抓取模式/data_id階層/edge cases
- [FRED資料源全貌](fred-data-source.md) — 第二資料源;vintage/ALFRED #8 警示
- [augur 建構作法完整心智圖](augur-construction-map.md) — 20260709 版(遠端已有 20260710 v3 報告 supersede)
- [資料層四層理解](augur-data-layer.md) — 94表772欄實證/恆等式/已知bug(新索引 raw-data-defs 為濃縮版)
- [哲學素養框架層](investment-philosophy-framework.md) — 哲學/知識層演進全史(新索引 knowledge-philosophy 為濃縮版)
- [TTAI整合與平台重建](ttai-integration-and-platform.md) — 本機(WSL2)服務端口/密碼/TTAI嵌入/advisor Tier-1
- [Rigor 完整性紀律](rigor-completeness-discipline.md) — 完整性天職/真窮舉到真邊界
- [有界自主模式](bounded-autonomy-mode.md)、[選股 headline 未 deflate](prediction-headline-undeflated.md)、[不同時派 agent 改同檔](no-concurrent-agents-same-files.md)、[DB 跨機獨立不隨 git](db-cross-machine-independent.md)、[改治權/commit 前先 git fetch](git-fetch-before-treaty-commit.md) — 紀律類仍有效
- 其餘（augur_project_overview / core-universe-and-f3-model / feature-execution-plan / asof-completeness / data-source-consistency / ingestion-strengthen）＝已被新索引對應檔大幅取代之史料
