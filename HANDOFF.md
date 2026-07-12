# HANDOFF — augur 跨機接續指南

> **這份文件是什麼**：augur 會在**另一台電腦接續開發**。這是「新機 clone 後第一份該讀的文件」——
> 告訴你**從哪接、怎麼跑起來、哪些不在 git、進度到哪、紅線是什麼**。
> 快照時點：**2026-07-09**（`main` HEAD = commit `5ad038f`；HEAD 之後會前進,以 `git log` 為準）。

---

## 0. 一句話

源碼在 GitHub（clone 即得全部,含預測層+顧問層）;**DB 不在 git、靠 C:\AI dump 搬**;`.env` 與 build 產物不在 git、**須手動重建**;治權、計劃、建構理解都在 repo 內（讀 §1）。**Claude memory 原機器本地、不隨 git**——現用 `sync_memory.py export` 快照進 repo `handoff_memory/`(隨 git 遷移),新機 clone 後 `python3 sync_memory.py restore` 還原回活 memory(見 §2)。換機續作以本 HANDOFF + repo 內文件為 SSOT。

## 1. 先讀這些（治權 SSOT + 建構理解 + 路線圖,勿憑記憶)

| 檔 | 是什麼 |
|---|---|
| `docs/系統核心思想_v1.8.0.md` | **靈魂**：預測**相對強弱**＋預言機軸(絕對方向機率,唯過 direction_gate;v1.6.0;v1.8.0 三度堅持刪「不是預測絕對漲跌幅」句,E[r] 升格幅度級得逐股(GATE/econ 同源/揭露硬綁不動))（非絕對漲跌機率）、成功=經濟價值非 IC、系統建議人決策、禁 AI 占卜大師 |
| `docs/原則精華_v1.9.0.md` | **20 條不可違反法律** + 資料完整性判準（**FREEZE 已解凍→live 增量維運** v1.9.0/2026-07-12） |
| `docs/系統架構大憲章_v1.45.0.md` | **憲法**：三敵×管線、12-PHASE、升版規則、**第六部計畫先行/計畫完整性 v1.39.0**、修訂歷程 |
| `CLAUDE.md`（v1.25） | AI 協作工具規則（Read-before-Edit、clean-room #16、plan-first #20、一支一支檢視 #19、常駐服務改碼須重啟實測 #7、最小 usage #28、DB 備份慣例 #30） |
| `reports/augur_construction_understanding_20260709.md` | **⭐建構作法完整理解 v2（code-verified、對抗審查）**：兩半系統框架、逐層 how-built、跨系統 meta-pattern、治權→code 接線——**接手必讀「這專案怎麼建的」** |
| `reports/augur_omniscient_advisor_plan_20260709.md` | **活躍計畫①**：全能全知顧問端到端（know-how→DB→逐字理解→Qdrant→qwen→web UI）——**未執行、待拍板** |
| `reports/augur_prediction_short_horizon_model_plan_20260709.md` | **活躍計畫②**：H20/H40/H60「30/60 天」誠實 horizon 模型——**未執行、待拍板+釐清日曆日/交易日** |
| `reports/augur_prediction_sop_master_20260706.md` | 股市預測 SOP 主計劃（端到端、階段、拍板點） |

> **紀律**：clean-room（零 stock_backend 參考）、plan-first（**所有計畫書須附 table schema + python 程式規畫、v1.39.0**）、一支一支檢視、改常駐服務後重啟再實測、#15 親驗 code 非「我以為」。

## 2. 新機 setup 序

```bash
git clone https://github.com/tsaitsangchi/augur.git && cd augur
# OS 依賴：PostgreSQL 17(含 headers)、OpenMP(libgomp,lightgbm 需)
python -m venv venv && source venv/bin/activate
pip install -e .                       # scripts 個別可執行(#29 _bootstrap、不依賴 PYTHONPATH)
# 還原 DB(不在 git,見 §3):
createdb augur                         # 或先建 augur 角色/庫
pg_restore -j 4 -h 127.0.0.1 -U augur -d augur /path/to/augur_pg17_20260709.dump   # #30 平行還原
python scripts/setup_predict_role.py --apply   # 重建 augur_predict role(#8 動態 GRANT 隔離閘)
# 重建 .env(見 §3)才會過:
PYTHONPATH=src python -c "from augur.core import db; print('smoke', db.ping())"
# 常駐服務(可選,WSL2):serve_advisor_openai:8399 / serve_chat_ui:8090 / serve_admin_console:8500 / ollama(qwen3:8b):11434
```
工作目錄隨機器變（WSL2 `/home/<user>/project/augur`；程式一律寫真實工作目錄 CLAUDE #13）。

**日常同步（非新機首clone）**：跑 `bash sync_from_github.sh`——只做安全 fast-forward + 按需 `pip install -e .` + import smoke test；工作樹不乾淨或與遠端分岔一律停手印訊息、不自動 merge/reset,交人（或 Claude）判斷。全本地、零 Claude usage（CLAUDE #28 本地優先之落地工具）。

**讀取專案接續狀態（零 Claude usage）**：跑 `python3 read_handoff.py`——一次讀出本 HANDOFF + Claude memory（`~/.claude/projects/<mangled>/memory/`,機器本地不隨 git,缺失則 graceful 降級只印 HANDOFF）全內文。`--list` 快速一覽、`--out FILE` 寫檔、`--memory-only`/`--handoff-only` 篩段;可 `python3 read_handoff.py | ollama run qwen3:8b "…"` 直接餵本地 AI（人/本地 AI 不必開 Claude session 即讀全狀態 = 實質省 token）。

**記憶跨機遷移（新機接續 memory）**：本機 commit 前跑 `python3 sync_memory.py export`（活 memory → repo `handoff_memory/`,隨 git 走）;**新機 clone 後跑 `python3 sync_memory.py restore`** 還原回 `~/.claude/projects/<mangled>/memory/`(覆蓋前自動備份、活記憶獨有檔保留)。無參數 = `status` 唯讀比對。活記憶目錄由當前 repo 位置推導,故 clone 到不同路徑亦正確。⚠ repo 為 public,`handoff_memory/` 內容公開(記憶無機密、為 docs 濃縮)。

## 3. 不在 git、新機須重建（皆 gitignored）

- **DB**（靠 dump 搬、#30):最新 = **`augur_pgdump_20260711_Fd`**（`-Fd` 平行目錄 dump、**7.0GB 壓縮**、雙份:本地 ext4 `~/db_dumps/` + `D:\database\`;`pg_restore -l` TOC 已驗、還原用 `pg_restore -j 4`）。含 **public 220 表 + ttai_import 16 表**（預測層/知識層/向量 pgvector + 方向軸 direction_gate·direction_probability·mc_simulation_run 等;⚠ **不含擂台 A0 4 表**——dump(22:51) 後才建,還原後跑 `python scripts/migrate_direction_arena_ddl.py` 補）。舊 `C:\AI\augur_pg17_20260709.dump`（-Fc 單檔 6.62GB）仍在、可備援。**dump 不進 git**,用外接碟/雲端搬。
- **`.env`**（手動重建、值不入 git):`DB_HOST/PORT/NAME/USER/PASSWORD`、`DB_SUPERUSER_*`、`DB_PREDICT_PASSWORD`、`FINMIND_TOKEN`（⏰ 2026-06-24 已過期→降 free tier）、`FRED_API_KEY`、`AUGUR_ADMIN_PASSWORD`、`AUGUR_INTERNAL_SECRET`、`UNPAYWALL_EMAIL`;+ `git config user.name/email`。（⚠ **advisor LLM 本機限定 v1.37.0**——不接任何外部 LLM,GEMINI 等 key 即使存在亦不用於 advisor。）
- **向量庫**：生產 = **pgvector（在 DB dump 內、跟著 DB 走）**;`~/qdrant_local`（194MB 休眠驗證產物）= **可從 DB 用 `export_qdrant_index.py` 重建、不需跨機搬**。
- **build 產物**（可重生勿 commit):`models_artifacts/`（.joblib、train_ranker 重生）、`data/`、`/models/`。⚠ `.gitignore` 模型輸出規則錨定 `/models/`（根限定）——**勿改回 `models/`**（會遞迴誤傷 `src/augur/models/` 源）。

## 4. 進度快照（2026-07-09;**2026-07-10 增補**:憲章 v1.40.0(相對機率判準+管線暢通不變式)、e2e 主計畫 D0-D12 簽核且 P1/P2/P5/P6 已執行(機率層上線:OOS 42,456→校準器 4→prediction_probability 1,376→picks 附欄 P30/P60/P120+四標記硬綁)、本地審議引擎 MVP(deliberation pkg+4 oracle+機械鎖,實戰假確認 0)、換機工具鏈+memory 隨 repo;詳 git log 與 reports/*20260710*。**2026-07-11 增補**:預言機軸立法(憲章 v1.42/靈魂 v1.6 用戶親核;勸阻雙留痕)+CLAUDE v1.24(本地審議引擎為主);方向軸全建置鏈落檔且**經濟終關六門全判死**(H40/H82/H120 擇時=buy&hold、H20 alive 唯屬 GATE 外獨立標示軸;`reports/direction_econ_20260711.md`+memory `augur-oracle-direction-verdict`);advisor 方向/逐日價格誠實硬規則(lock②/閘⑥短路固定句);probability UI 增 MC 模擬情境頁(四鎖硬綁「模擬非預測」);systemd user unit 排序循環修復(augur-ollama 誤 `After=default.target` 致 advisor/chat/admin 開機被棄,已刪)）。**2026-07-12 日間增補**:①IP sustained ban 實錘(伺服器原話 msg=ip banned;一夜 4,000+ requests 觸發 #24 已知現象)——自癒 runner 已掛(nohup+flock,30 分/發探測,癒合即自動跑對帳,log=~/audit_retry.log);②對帳綠後終局鏈=E1 重驗→strict 全綠→unfreeze evaluate→--preregister-arena→hugo TTY 6 門;③settle factor 檢核鑑識定案:拼接與減資統計不可分→改逐標的 unsettleable(factor_event)揭露、批次熔斷唯留時間旅行;④L2 首個全自動日完成(15 confirmed/4 escalated、新增 5 單人裁);⑤方向特徵四鏈+TRI 已補至 07-09;首個凍結後 panel 2026-06-30(91,385 值)落地;⑥arena futility policy 建議值(待 A2 hugo 併核):futility_min_clusters=60、futility_z=1.645。

**2026-07-12 凌晨解凍執行段**:hugo 四項親核(結案親簽+no-v3 入憲/D3D4 措辭案/擂台 A-1/解凍拍板 as-of'=滾動)→ 修憲落地(原則精華 v1.9.0/憲章 v1.43.0/CLAUDE v1.25,commit 7d337ec);FinMind Sponsor 續訂驗證;E 債全清(E2/E5/E7 除名、3 過時斷言更新)——strict 剩 E1;FRED 34.4 萬列+FinMind 33 天缺口補齊(全表至 2026-07-09,OptionDaily +18.8 萬列);PriceAdj 拼接損傷全表掃描=325 檔、修復工具 repair_priceadj_basis.py 全量重抓中;arena gate 預註冊模板(MDE/檢定力機械凍入)+live 對局路徑已備。**下一棒:修復完→audit→E1 綠→feature panel 2026-06-30→unfreeze GATE evaluate→arena TTY 親核→開賽**。

**2026-07-11 晚間增補**:①方向軸 v2 復活攻堅(修 v1 程序缺陷後預註冊四門 dgate_H_20/40/82_v2+D_5_v2)**全 `evaluated_fail`=二次證偽**——依凍結 fail_path 方向軸凍結至解凍+新資料、**不開 v3**;結案報告 `reports/augur_oracle_direction_v2_verdict_20260711.md` 待 hugo 親簽;②本地審議引擎 GATE **PASS**(batch `gate_43044a574c0d`:engine 90/90 正確、0 假確認 vs single_fast 50/90(20 假確認)/single_think 47/90(7 假確認);A5 複量=`reports/augur_deliberation_a5_remeasure_20260711.md`);③F1 前台檔位旗標**已開**(`deliberation_engine_config.frontend_tiers` enabled=true,qwen3 4b/8b×fast/think/ultra 六檔 live、default=augur-8b-fast)+L2 每日自審 cron 已掛(06:15 `run_daily_deliberation.py --run`);④MC 模擬擴至 **52 picks**(×10 runs=520 列 mc_simulation_run,四鎖不變);⑤prediction_probability **真回歸修復**(H82 增訓時段誤失 P20/40/60/120,以既有 writer 重 emit 復原 **5 horizons×339 股**,#12 不 hand-patch);⑥方向 live 擂台計畫定稿(對抗審查 22 項/6 blocker 全採納,`reports/augur_direction_live_arena_plan_20260711.md`)+**A0 骨架落地**(arena 4 表+3 防篡改 trigger 負向單測過、8 候選註冊凍結、adapters+合成冒煙全過零 DB 寫);⑦解凍 A-2 牆前備料(`reports/augur_unfreeze_a2_prep_20260711.md`:修憲草案四處+證據債 7 筆逐筆盤點;**FinMind token 已過期降 Free=解凍硬前置**,sponsor 續訂待 hugo);⑧DB dump 20260711 `-Fd` 平行雙份(本地 ext4+D 碟各 7.0GB,見 §3;不含 A0 4 表)。

**架構（讀建構理解 v2 全貌）**:augur = **兩個半系統**,只被 **PostgreSQL(message bus)+ 一個唯讀 PredictionPayload** 接起來;import_isolation AST 閘 + augur_predict DB role 雙閘機械強制「素養層不進預測管線」（本輪實跑 exit 0）。

**已完成並 committed**:
- **市場資料層**:raw 全市場全史 sync 至 **as-of 2026-05-31（84/84 表完整性定案、~46GB、FREEZE 凍結）**;features 35 特徵入 feature_values（發布日 gate）;universe core_universe_asof（PIT 消 survivorship）;evaluation 七模組。
- **股市預測全鏈 + 誠實驗證**:models（RankRidge/RankGBDT/registry/artifact）;誠實四關（walk-forward embargo h+62td→HAC-t→經濟價值 #14→deflation DSR）;**deflation 地板已釘實**（headline 未過 deflation、DSR 75.6-93.6% <95%=**未確立**、per-period units bug 修）;survivorship 經濟閉環（下市偏誤≈0、incumbency −16.5%）;成本敏感度帶（主地板 pit_broad 1.5% 成本 deflated 翻負）;H120 部署評估（全期 DSR 93.6% 近門檻最強候選、已凍結 tracked-candidate baseline）;**持續再驗證 harness**（兩軌三態判停、LIVE:2 models/688 preds/105 ledger/4 baselines/verdict=deploying_unestablished）。
- **顧問層**:advisor 確定性 picks 注入（治 qwen3:8b 幻覺股名/數字）+ guard 五閘 + 白話誠實敘述磨版;RBAC/identity/access;蒸餾;serving 三 server。
- **治權**:靈魂 v1.5.0 / 原則精華 v1.8.0（FREEZE）/ 憲章 v1.39.0（計畫完整性強化）/ CLAUDE v1.22。

**⚠️ 尚未做（下一棒、皆 plan-first 待拍板+執行）**:
- **活躍計畫①全能全知顧問**（omniscient plan、W1..W8）:焊接既有鏈成一條 background pipeline + 補 5 道機械閘（尤 **G3 命門:ollama.base_url 無 host 驗證、須焊死 v1.37.0**）;唯一新 code=向量後端 factory `vectorstore.py`。~90% 已建、無須改靈魂/憲章。
- **活躍計畫②短 horizon 模型**（W1..W5）:訓 H20/H40（+H60 對照）走誠實四關;**待你釐清「30/60=日曆日(→H20/H40)還交易日」+ 接受「多半薄/未確立」誠實預期**。誠實四關全複用既有 SSOT。
- **其他排隊**:知識 works/en 嵌入補跑;軌B live 資料追蹤（**FREEZE 下屬「系統完美後」未來階段**、現無新資料可驗）。

## 5. 誠實紅線（不可逾）

- **三敵零容忍、非試錯對象**:①假資料 ②偷看未來（as-of/anti-leakage #8）③自我欺騙（out-of-sample #15）。
- **預測 edge 薄且未確立**:headline 淨 Sharpe ~1.20 = **樂觀上界、未過 deflation**（DSR <95%）;真實成本（小型股 1.5%+）下主地板 deflated 趨零至負;H20 經濟判死、H60 未確立、H120 近門檻。**引用任何 Sharpe 一律附「未過 deflation、未確立」**。真天花板=**資料累積+硬體**（FREEZE 下待系統完美後接新資料）,非碼。
- **「30/60 天絕對漲跌機率」= 假兆**:靈魂只做相對強弱排序;顧問回相對強弱+薄可信度+know-how 解讀,**不偽造絕對機率**。
- **know-how 不進預測管線**（#8 隔離命門、import_isolation 閘）;**advisor LLM 本機限定**（v1.37.0、含 owned_local 私有 citations 禁外流）。
- 決策層人拍板、執行層 AI 主動（#26）;碰治權判準變更/破壞性/API 放量/commit-push 即停下問。

---

**續建入口**:讀 §1 治權 + 建構理解 v2 → 選活躍計畫①或②（用戶拍板+釐清）→ 一支一支 plan-first 實作、實測、誠實記錄。**DB 現況一律實查**（跨機各自獨立、勿照抄 handoff 假設 #15）。
