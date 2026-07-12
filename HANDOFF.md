# HANDOFF — augur 跨機接續指南

> **這份文件是什麼**：augur 會在**另一台電腦接續開發**。這是「新機 clone 後第一份該讀的文件」——
> 告訴你**從哪接、怎麼跑起來、哪些不在 git、進度到哪、紅線是什麼**。
> 快照時點：**2026-07-12**（`main` HEAD = `5a93cdc`、tag `archive-20260712-pregame-allsigned`;HEAD 之後會前進,以 `git log` 為準）。

---

## 0. 一句話

源碼在 GitHub（clone 即得全部,含預測層+顧問層）;**DB 不在 git、靠 dump 搬（最新位置見 §3）**;`.env` 與 build 產物不在 git、**須手動重建**;治權、計劃、建構理解都在 repo 內（讀 §1）。**Claude memory 原機器本地、不隨 git**——現用 `sync_memory.py export` 快照進 repo `handoff_memory/`(隨 git 遷移),新機 clone 後 `python3 sync_memory.py restore` 還原回活 memory(見 §2)。換機續作以本 HANDOFF + repo 內文件為 SSOT。

## 1. 先讀這些（治權 SSOT + 建構理解 + 路線圖,勿憑記憶)

| 檔 | 是什麼 |
|---|---|
| `docs/系統核心思想_v1.8.0.md` | **靈魂**：預測**相對強弱**＋預言機軸(絕對方向機率,唯過 direction_gate;v1.6.0;v1.8.0 三度堅持刪「不是預測絕對漲跌幅」句,E[r] 升格幅度級得逐股(GATE/econ 同源/揭露硬綁不動))（非絕對漲跌機率）、成功=經濟價值非 IC、系統建議人決策、禁 AI 占卜大師 |
| `docs/原則精華_v1.9.0.md` | **20 條不可違反法律** + 資料完整性判準（**FREEZE 已解凍→live 增量維運** v1.9.0/2026-07-12） |
| `docs/系統架構大憲章_v1.45.0.md` | **憲法**：三敵×管線、12-PHASE、升版規則、**第六部計畫先行/計畫完整性 v1.39.0**、修訂歷程 |
| `CLAUDE.md`（v1.25） | AI 協作工具規則（Read-before-Edit、clean-room #16、plan-first #20、一支一支檢視 #19、常駐服務改碼須重啟實測 #7、最小 usage #28、DB 備份慣例 #30） |
| `reports/augur_construction_understanding_20260710.md` | **⭐建構作法完整理解 v3（code-verified 16 子系統、supersede 20260709 版）**：兩半系統框架、逐層 how-built、跨系統 meta-pattern、治權→code 接線——**接手必讀「這專案怎麼建的」** |
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
# 還原 DB(不在 git,見 §3;一鍵=自動判格式+平行還原+setup_predict_role+smoke):
bash import_database.sh                # 或 import_database.sh /path/to/dump;取代既有庫須 --force
# 重建 .env(見 §3)才會過:
PYTHONPATH=src python -c "from augur.core import db; print('smoke', db.ping())"
# 常駐服務(可選,WSL2):serve_advisor_openai:8399 / serve_chat_ui:8090 / serve_admin_console:8500 / ollama(qwen3:8b):11434
```
工作目錄隨機器變（WSL2 `/home/<user>/project/augur`；程式一律寫真實工作目錄 CLAUDE #13）。

**日常同步（非新機首clone）**：跑 `bash sync_from_github.sh`——只做安全 fast-forward + 按需 `pip install -e .` + import smoke test；工作樹不乾淨或與遠端分岔一律停手印訊息、不自動 merge/reset,交人（或 Claude）判斷。全本地、零 Claude usage（CLAUDE #28 本地優先之落地工具）。

**讀取專案接續狀態（零 Claude usage）**：跑 `python3 read_handoff.py`——一次讀出本 HANDOFF + Claude memory（`~/.claude/projects/<mangled>/memory/`,機器本地不隨 git,缺失則 graceful 降級只印 HANDOFF）全內文。`--list` 快速一覽、`--out FILE` 寫檔、`--memory-only`/`--handoff-only` 篩段;可 `python3 read_handoff.py | ollama run qwen3:8b "…"` 直接餵本地 AI（人/本地 AI 不必開 Claude session 即讀全狀態 = 實質省 token）。

**記憶跨機遷移（新機接續 memory）**：本機 commit 前跑 `python3 sync_memory.py export`（活 memory → repo `handoff_memory/`,隨 git 走）;**新機 clone 後跑 `python3 sync_memory.py restore`** 還原回 `~/.claude/projects/<mangled>/memory/`(覆蓋前自動備份、活記憶獨有檔保留)。無參數 = `status` 唯讀比對。活記憶目錄由當前 repo 位置推導,故 clone 到不同路徑亦正確。⚠ repo 為 public,`handoff_memory/` 內容公開(記憶無機密、為 docs 濃縮)。

## 3. 不在 git、新機須重建（皆 gitignored）

- **DB**（靠 dump 搬、#30):最新 = **`augur_pgdump_20260712_Fd`**（本地 ext4 `~/db_dumps/` 目錄版 + `D:\database\augur_pgdump_20260712_Fd.tar` 單檔版、9.9GB;**247 表完整**含擂台 4 表/三鏡頭月頻/K 計畫橋表;56GB 庫=35GB 資料+21GB 索引故 9.9GB 屬正常;逐表 TOC 已驗、分區父表 knowledge_concordance 無 TABLE DATA 屬正常）。還原一律用 `bash import_database.sh`（自動判 tar/-Fd/-Fc、平行還原;新機庫不存在直接建、取代既有須 `--force`）。舊 dump（20260711_Fd 7.0GB 等）可備援。**dump 不進 git**,用外接碟/雲端搬。
- **`.env`**（手動重建、值不入 git):`DB_HOST/PORT/NAME/USER/PASSWORD`、`DB_SUPERUSER_*`、`DB_PREDICT_PASSWORD`、`FINMIND_TOKEN`（Sponsor 已續訂 2026-07-12;過期會降 free tier,錶=`/user_info`）、`FRED_API_KEY`、`AUGUR_ADMIN_PASSWORD`、`AUGUR_INTERNAL_SECRET`、`UNPAYWALL_EMAIL`;+ `git config user.name/email`。（⚠ **advisor LLM 本機限定 v1.37.0**——不接任何外部 LLM,GEMINI 等 key 即使存在亦不用於 advisor。）
- **向量庫**：生產 = **pgvector（在 DB dump 內、跟著 DB 走）**;`~/qdrant_local`（194MB 休眠驗證產物）= **可從 DB 用 `export_qdrant_index.py` 重建、不需跨機搬**。
- **build 產物**（可重生勿 commit):`models_artifacts/`（.joblib、train_ranker 重生）、`data/`、`/models/`。⚠ `.gitignore` 模型輸出規則錨定 `/models/`（根限定）——**勿改回 `models/`**（會遞迴誤傷 `src/augur/models/` 源）。

## 4. 現況 STATE（取代式：每次封存點整段重寫；歷史＝`git log -p HANDOFF.md`）

> 更新於 **2026-07-13 00:4x**、git 前一 commit `ddd4821`、最新 tag 見 `git tag -l 'archive-*'`。
> **紀律：本區每個宣稱都可能過期——待辦一律先跑附帶的驗證指令實查（#15），勿直接信。**

### 4.1 一句話現況
開賽前置**人工關卡全清**（A2 六門＋A3 `_r2` 三門皆簽、futility＋九候選凍結），audit 對帳已達 **[88/88] 進入尾段彙整**→ 哨兵句一出 AI 自動接 E1→strict→unfreeze evaluate→開賽。**知識層同日大豐收**：全文源專屬解析器 T1-T3 當日完成（IA/EDGAR/FRASER 三策略住 `adapter_config.fulltext`），公版全文落地 **491 件/66MB→已切 469,551 句**（嵌入由 03:30 timer 自動接）；PDF 抽取計畫書待 P0。

### 4.2 下一步（可直接執行，含前置條件）
```bash
# ① 等 audit 綠(哨兵句「✓ audit 完成(rc=0)」出現在 ~/audit_retry.log)
# ② E1 重驗:
python scripts/verify_validation_evidence.py --run --with-scripts
# ③ strict 全綠(exit 0 才准下一步):
python scripts/verify_validation_evidence.py --strict
# ④ GATE evaluate(僅 strict 綠後;--asof 用滾動 as-of'=raw 最新完整日):
python scripts/preregister_unfreeze_gate.py --evaluate unfreeze_06dcb178267d --asof <as-of'>
# ⑤ 開賽:
python scripts/run_arena_round.py   # (讀其矩陣;cron 掛載見 arena plan §A2)
```

### 4.3 正在跑的東西（殺掉前先看這裡）
| 工作 | 觀察方式 | 存活檢查 |
|---|---|---|
| audit 自癒跑者（nohup 脫離、撐過 session） | `tail -f ~/audit_retry.log` | `pgrep -f daily_maintenance` |
| systemd 六服務＋3 timers（開機自起） | `systemctl --user list-units 'augur-*'` | 端口 curl 序見 memory `restart-systemd-after-edit` |
| 重開機後重啟 audit | `nohup flock -n /tmp/augur_audit.lock bash ~/augur_audit_selfheal.sh &` | 探測先行＋PYTHONUNBUFFERED |

### 4.4 紅線（絕不能做）
- ⚠ **evaluate 嚴禁在 audit/strict 綠前跑**——gate 判準 g5：任一 fail＝`evaluated_fail` 終態、hugo 親簽的 gate 直接燒掉、須重預註冊重簽。
- ⚠ **FinMind 類作業（市場補同步／PriceAdj 修復）與 audit 互斥**——同一 IP，audit 跑完才輪它們（#24 IP sustained ban 07-12 實錘）。
- ⚠ **PDF 抽取未經 P0 拍板前不啟動**（含 OAPEN 61/skip_pdf 976）——OCR 維持不啟動（P8 原裁定）;IA 掃蕩已完成(491 抓/其餘誠實終態)、勿重複放量。

### 4.5 待人類 vs 待 AI
**待 hugo 拍板**（全部非阻塞開賽）：
1. **PDF 抽取計畫 P0**＝`reports/knowledge_pdf_extraction_plan_20260712.md`（D2 後續;pypdf+五道機械品質閘 fail-closed;OAPEN 61+skip_pdf 976）
2. 短 horizon 模型計畫②＋全能顧問計畫①：**hugo 已裁「開賽後 AI 先做時效性複核再拍」**（2026-07-12;兩案早於解凍/擂台設計,恐部分被超越）
3. 舊專案 stock_backend 的平日 16:00 FinMind cron 去留（與 augur 同 IP 疊加負載）

> 解析器計畫 T0 已拍(2026-07-12):D1 核准全計畫、D2 另立 PDF 計畫、D3 IA 200/批——**T1-T3 當日執行完畢**(FRASER textUrl 實證/三策略落 DB/IA 13 批掃蕩 491 抓、熔斷零觸發)。

**待 AI（條件觸發、零人工）**：audit 綠→4.2 全鏈；拍板後→解析器 T1-T3（全本地零 token）。

**驗證指令**（宣稱會過期，指令不會）：
```bash
# 門的現況:      SELECT gate_id,status,approved_by FROM direction_gate WHERE gate_id LIKE 'dgate_a%' OR gate_id LIKE 'dgate_arena%';
# 證據帳本:      python scripts/verify_validation_evidence.py --list   # 07-12 晚:14/15 綠、唯 E1 紅
# 擂台選手/對局: SELECT count(*) FROM direction_arena_candidate; SELECT count(*) FROM direction_arena_prediction;  # 9 / 0(未開賽)
```

### 4.6 已知陷阱（本專案特有假象，踩過的）
- **終端貼多行指令**：第一輪其實已成功、逐行重跑報「不存在/非法狀態」是假象——先查 DB 再下結論（07-12 兩次實例：activate×3、A3 approve×3）。
- **`pgrep -f` 自匹配**：會抓到含關鍵字的指令 wrapper 本身——kill 前先 `ps -o cmd= -p <pid>` 看清。
- **Python 背景 log 沉默**＝stdout 緩衝非當機——nohup 跑者一律加 `PYTHONUNBUFFERED=1`；判斷存活看 `/proc/<pid>/wchan` 與 rchar 增量。
- **dump「太小」疑慮**：56GB 庫＝35GB 資料＋21GB 索引（dump 不存索引）＋壓縮 → 9.9GB 正確；逐表驗證法見 git log `5a93cdc` 前後對話／`pg_restore -l` 比對活庫表數（分區父表無 TABLE DATA 屬正常）。
- **FRASER API 只收 `X-API-Key` header**（query param 必 401）；key 認證機制＝`knowledge_source.adapter_config.auth_header`。
- **額度錶低 ≠ IP 安全**：FinMind 403 有額度型與 IP sustained 型兩種，判斷一律問錶（`/user_info`）＋見訊號即停（#24）。

### 4.7 路由表（去哪讀什麼；本檔不複述）
| 要什麼 | 去哪 |
|---|---|
| 規則/工具紀律 | `CLAUDE.md`（v1.25；#31＝接續慣例） |
| 判準/憲法 | `docs/系統架構大憲章_v1.45.0.md`＋`docs/原則精華_v1.9.0.md`＋`docs/系統核心思想_v1.8.0.md` |
| 這專案怎麼建的 | `reports/augur_construction_understanding_20260710.md`（v3 code-verified） |
| 擂台規格 | `reports/augur_direction_live_arena_plan_20260711.md` |
| 已完成功能清單/演變史 | `git log`＋封存 tag 序列（`git tag -l 'archive-*'`） |
| 濃縮經驗/教訓 | memory（`read_handoff.py` 一次讀出；隨 repo＝`handoff_memory/`） |

## 5. 誠實紅線（不可逾）

- **三敵零容忍、非試錯對象**:①假資料 ②偷看未來（as-of/anti-leakage #8）③自我欺騙（out-of-sample #15）。
- **預測 edge 薄且未確立**:headline 淨 Sharpe ~1.20 = **樂觀上界、未過 deflation**（DSR <95%）;真實成本（小型股 1.5%+）下主地板 deflated 趨零至負;H20 經濟判死、H60 未確立、H120 近門檻。**引用任何 Sharpe 一律附「未過 deflation、未確立」**。真天花板=**資料累積+硬體**（FREEZE 下待系統完美後接新資料）,非碼。
- **「30/60 天絕對漲跌機率」= 假兆**:靈魂只做相對強弱排序;顧問回相對強弱+薄可信度+know-how 解讀,**不偽造絕對機率**。
- **know-how 不進預測管線**（#8 隔離命門、import_isolation 閘）;**advisor LLM 本機限定**（v1.37.0、含 owned_local 私有 citations 禁外流）。
- 決策層人拍板、執行層 AI 主動（#26）;碰治權判準變更/破壞性/API 放量/commit-push 即停下問。

---

**續建入口**:讀 §1 治權 + 建構理解 v3 → **§4 現況 STATE**（一句話現況→下一步→紅線→待辦附驗證指令）→ plan-first 實作、實測、誠實記錄。**現況一律實查**（§4 每個宣稱都可能過期,先跑其驗證指令;跨機各自獨立、勿照抄假設 #15）。
