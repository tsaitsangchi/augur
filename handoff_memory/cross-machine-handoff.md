---
name: cross-machine-handoff
description: "augur 專案將換另一台電腦接續;交接源=GitHub+D碟 dump,新機 setup 清單與不在 git 之本地物"
metadata: 
  node_type: memory
  type: project
  originSessionId: 9009c955-58bc-46c5-904b-ed515e2be723
---

**2026-07-06 用戶 directive:此 augur 專案進度會換另一台電腦接續。** 交接源與續建須知(承 [[augur-project-map]] 兩機約束):

> **⚡ 現行接續 SSOT = repo 內 `HANDOFF.md`(維護中、比本記憶新)**——換機第一份讀它。建構全貌讀 `reports/augur_construction_understanding_20260710.md`(v3、code-verified 16 子系統、supersede 20260709 版)。本記憶自 2026-07-06 後多處過時(HEAD/版本/dump),僅留歷史快照;版本以 on-disk 為準(2026-07-10:憲章 v1.39.0 / 原則精華 v1.8.0 / CLAUDE v1.22)。
> **記憶隨 repo 遷移**:活記憶本不隨 git;現用 `sync_memory.py export` 快照進 repo `handoff_memory/` → 新機 `restore` 還原(見 [[local-handoff-tooling]])。三支零-usage 工具:`sync_from_github.sh`/`read_handoff.py`/`sync_memory.py`。

**源碼 SSOT = GitHub** `https://github.com/tsaitsangchi/augur.git`
- 交接點(2026-07-10 晚):治權升 **憲章 v1.40.0**(端到端管線暢通不變式+相對機率誠實判準入憲);**e2e 主計畫定稿** `reports/augur_omniscient_e2e_master_plan_20260710.md`(機率=橫斷面相對機率轉譯、S1-S10 一條路、四接縫、§9 硬體雙軌;**拍板題 D0-D12 未簽核、實作未動工**)。本機 DB 已從 D:\database 07-09 dump 完整還原(183+22 表,備份庫 augur_pre_import_bak_20260710 留存)。admin 後台明文帳密(.env AUGUR_ADMIN_USER/PASSWORD,serve_admin_console 支援)。
- 日常同步用 `bash sync_from_github.sh`(只 fast-forward、分岔即停手);封存 tag 序列見 git tag。
- 新機 `git clone` 即得全部源碼(含 `src/augur/models/` 預測層——曾因 `.gitignore` 未錨定之 `models/` 遞迴誤傷而差點漏 commit,已修為 `/models/`;勿再退回)。

**DB 不在 git → 靠 dump 搬**(#30):
- 最新已知 = `D:\database\augur_20260705_2327.dump`(6.3G、`-Fc` 單檔、164 表含預測層 `model_registry`+`prediction_values`)。
- 還原:`pg_restore -j4 -h127.0.0.1 -U augur -d <新庫> <dump>`;或平行目錄版 `augur_20260705/`。
- **注意:git 已領先此 dump(07-06 新增 DDL)**——還原 07-05 dump 後須補跑 `scripts/migrate_advisor_distill_ddl.py`(蒸餾 4 表)+ `scripts/setup_predict_role.py`(預測隔離角色)才與源碼一致(#12 DDL 靠 migration、非 hand-patch);若來源機已產更新 dump 則以該檔為準。

**不在 git、新機須重建/重跑**(皆 gitignored):
- `.env`(**須手動重建**,鍵:`DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD`、`FINMIND_TOKEN`、`FRED_API_KEY`、`GITHUB_TOKEN`、`AUGUR_ADMIN_PASSWORD`、`AUGUR_INTERNAL_SECRET`、`UNPAYWALL_EMAIL`、`GEMINI_API_KEY` + `git config --global user.name/email` 兩行〔[[git_identity_in_env]]〕;**值不入記憶**)。
- `models_artifacts/`(.joblib,`train_ranker.py` 可重生)、`data/`、`models/`(輸出目錄,from-zero 重建)。

**新機 setup 序**:`git clone` → `pip install -e .`(README 標準)→ OS 依賴(**lightgbm 需 OpenMP `libgomp`**、PostgreSQL headers)→ `pg_restore` 還原 augur DB → 重建 `.env` → import smoke test → systemd 常駐服務(augur-chat:8090/advisor:8399/admin:8500/ollama:11434)重起。工作目錄隨機器變(CLAUDE #13:WSL2 `/home/hugo/project/augur`、Mac `/Users/hugo/project/augur`)。

**進度快照(2026-07-06 更新;憲章 v1.36.0 / CLAUDE v1.18)**:
- **預測 SOP A→D 全走完、且驗出真預測力+經濟價值**(前次僅骨幹、未驗):
  - **A' 隔離**:AST import 雙閘(`src/augur/audit/import_isolation.py`)+ embargo 保證下界(`walkforward.splits`,embargo≥h+62td)入憲 v1.36.0。
  - **B 提拔三審=通過**:as-of IC H20 +0.113 / H60 +0.152,HAC-t +6.09 / +6.95(≫2 硬 gate);shuffle 負對照 IC≈0(洩漏排除);B3 H60 輕微旗標列觀察。SSOT=`reports/augur_prediction_stageB_promotion_verdict_20260706.md`。
  - **C/D 經濟 #14=成立但僅 Ridge H60 long-only**(淨 Sharpe~1.2、CAGR 16.6%、MaxDD −13.9%、Calmar 1.19、扣 0.585% 成本、2014/2021 兩期皆勝基準);**H20 經濟已死、long-short 近期崩不採**。SSOT=`reports/augur_prediction_stageCD_economic_verdict_20260706.md`。
- **advisor**:Tier-1 誠實 relevance 閘(`src/augur/advisor/relevance.py`,四鏡對抗)+ 蒸餾管線 S1-S5 建置(界線 A/B/C 隔離,`scripts/advisor_distill_*.py` 4 支 + DDL)。
- **TTAI/Tiptop ERP**:全庫 141,825 item 嵌入 + owned_local 治理**竣工**,但**檢索品質尚不足**(zh 同語術語 rank@1 可用、跨語/en 幾乎全垮、e5-small 高分≠相關)→ 後續改進(清 boilerplate/建 concordance/rerank、跨語需 bge-m3)。裁決=`reports/augur_ttai_retrieval_verdict_20260706.md`;整合主計劃(M6/8/9 拍板)=`reports/augur_ttai_erp_integration_master_plan_20260706.md`。
- **主計劃 SSOT**=`reports/augur_prediction_sop_master_20260706.md`(取代舊 `_plan_20260705`)。**排隊未做**:v3.0 text W2.7(en 檢索命門)+W8(讀端 kNN API)、admin 控制台+資料夾抽取器、ERP 檢索改進、蒸餾管線實跑。
