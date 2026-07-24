> **Monorepo 註（2026-07-22）**：本倉已合併治權樹。治權交接見 [`HANDOFF-governance.md`](HANDOFF-governance.md)；遷移清單見 [`ops/phase2/MONOREPO-LEARNING-MIGRATION.md`](ops/phase2/MONOREPO-LEARNING-MIGRATION.md)。

# HANDOFF — augur 跨機接續指南

> **這份文件是什麼**：augur 會在**另一台電腦接續開發**。這是「新機 clone 後第一份該讀的文件」——
> 告訴你**從哪接、怎麼跑起來、哪些不在 git、進度到哪、紅線是什麼**。
> 快照時點：**2026-07-23**（最新封存 tag＝`archive-20260723-lint-p1p3-cmd-matrix`；HEAD 以 `git log -1`／該 tag 為準）。

---

## 0.5 增補快照 2026-07-18（Phase 1 憲章化收官——接續者必讀）

**main HEAD＝`f95557b`**（AUD-02＋identity 補正已併入並部署生產）。本日完成：
* **Phase 1 全線收官**（憲章移轉計畫第一期）：(a) 分支三鏡對抗審查全 GO＋Steward 准併；(b) hugo 側部署＋heal 快照 gate 上線；(c) predict role refresh（REVOKE 84 素養／GRANT 163 預測）；(d) **owner 分離生產生效**——十張憲章表＋2 抹除函式隸 `augur_owner`（NOLOGIN），應用角色 `augur_app` 僅 SELECT/INSERT，`augur` 留維運通道；服務連線已切 `augur_app`。
* **權限紅線（新）**：憲章十表 append-only＝ACL＋19 trigger 雙層；抹除函式唯 owner/superuser；tombstone 測試已把「應用角色被拒」鎖為回歸。**測試要跑 DB 行為層須有 `DB_SUPERUSER_PASSWORD` env（fixture 雙角色模式）**。
* **備份**：`/home/giga/augur/backups/`（10GB dump）＋restic 異碟庫 `D:\augur_restic`（密碼檔 backups/restic.pass，600，不在 git）；pg_stat_statements 已預載。
* **詳細執行記錄／裁決軌跡**＝augur-constitution 倉 `ops/phase1/`（EXECUTION-RECORD、#19 卷宗）與 `CODE-MIGRATION-PLAN.md`（Phase 2–8 路線）。
* 待組織性事件：heal 首遇 value_mismatch → `raw_supersede_log` 首列（P4.E5 行為生效之標誌）。

## 0. 一句話

源碼在 GitHub（clone 即得全部,含預測層+顧問層）;**DB 不在 git、靠 dump 搬（最新位置見 §3）**;`.env` 與 build 產物不在 git、**須手動重建**;治權、計劃、建構理解都在 repo 內（讀 §1）。**Claude memory 原機器本地、不隨 git**——現用 `sync_memory.py export` 快照進 repo `handoff_memory/`(隨 git 遷移),新機 clone 後 `python3 sync_memory.py restore` 還原回活 memory(見 §2)。換機續作以本 HANDOFF + repo 內文件為 SSOT。

## 1. 先讀這些（治權 SSOT + 建構理解 + 路線圖,勿憑記憶)

> **統一入口**：[`constitution/GOVERNANCE-MAP.md`](constitution/GOVERNANCE-MAP.md)（[I] 治權地圖；L0／specs／docs／CLAUDE；docs 不上收 L0）

| 檔 | 是什麼 |
|---|---|
| `docs/系統核心思想_v1.8.0.md` | **靈魂**：預測**相對強弱**＋預言機軸(絕對方向機率,唯過 direction_gate;v1.6.0;v1.8.0 三度堅持刪「不是預測絕對漲跌幅」句,E[r] 升格幅度級得逐股(GATE/econ 同源/揭露硬綁不動))（非絕對漲跌機率）、成功=經濟價值非 IC、系統建議人決策、禁 AI 占卜大師 |
| `docs/原則精華_v1.10.0.md` | **20 條不可違反法律** + 資料完整性判準（**FREEZE 已解凍→live 增量維運**;live 准入=arena 前置 G1-G5 機制；**#7 supersede／RULING-2026-041**） |
| `docs/系統架構大憲章_v1.46.0.md` | **憲法**：三敵×管線、12-PHASE、升版規則、**第六部計畫先行/計畫完整性 v1.39.0**、修訂歷程 |
| `CLAUDE.md`（版本見檔頭） | AI 協作工具規則（Read-before-Edit、clean-room #16、plan-first #20、一支一支檢視 #19、常駐服務改碼須重啟實測 #7、最小 usage #28、DB 備份慣例 #30） |
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

**日常同步（非新機首 clone）**：跑 `bash sync_from_github.sh`——只做安全 fast-forward + 按需 `pip install -e .` + import smoke test；工作樹不乾淨或與遠端分岔一律停手印訊息、不自動 merge/reset,交人（或 Claude）判斷。全本地、零 Claude usage（CLAUDE #28 本地優先之落地工具）。

**封存 push（commit＋push＋tag）**：跑 `bash scripts/archive_push.sh [--slug SLUG]`——`.env` 之 `GITHUB_TOKEN` 經 GIT_ASKPASS；禁止 stage 秘密/ dump/大型檔；`--dry-run` 預覽、`--retag` 才 force 重打 tag。對稱於 `sync_from_github.sh`。

**讀取專案接續狀態（零 Claude usage）**：跑 `python3 read_handoff.py`——一次讀出本 HANDOFF + Claude memory（`~/.claude/projects/<mangled>/memory/`,機器本地不隨 git,缺失則 graceful 降級只印 HANDOFF）全內文。`--list` 快速一覽、`--out FILE` 寫檔、`--memory-only`/`--handoff-only` 篩段;可 `python3 read_handoff.py | ollama run qwen3:8b "…"` 直接餵本地 AI（人/本地 AI 不必開 Claude session 即讀全狀態 = 實質省 token）。

**記憶跨機遷移（新機接續 memory）**：本機 commit 前跑 `python3 sync_memory.py export`（活 memory → repo `handoff_memory/`,隨 git 走）;**新機 clone 後跑 `python3 sync_memory.py restore`** 還原回 `~/.claude/projects/<mangled>/memory/`(覆蓋前自動備份、活記憶獨有檔保留)。無參數 = `status` 唯讀比對。活記憶目錄由當前 repo 位置推導,故 clone 到不同路徑亦正確。⚠ repo 為 public,`handoff_memory/` 內容公開(記憶無機密、為 docs 濃縮)。

## 3. 不在 git、新機須重建（皆 gitignored）

- **DB**（靠 dump 搬、#30):最新 = **`augur_pgdump_20260713_Fd`**（換機用;本地 ext4 `~/db_dumps/` 目錄版 + `D:\database\augur_pgdump_20260713_Fd.tar` 單檔版;含 07-12 全日成果=擂台九門簽核/三鏡頭月頻/491 件公版全文+469,551 句/K 計畫橋表/**audit 增量 658,911 列**;⚠ dump 取於 audit 尾段對帳中——新機還原後 audit 須續跑至綠,見 §4）。還原一律用 `bash import_database.sh`（自動判 tar/-Fd/-Fc、平行還原;新機庫不存在直接建、取代既有須 `--force`）。舊 dump（20260712_Fd 9.9GB/20260711_Fd 7.0GB）可備援。56GB 庫=35GB 資料+21GB 索引,dump ~10GB 屬正常。**dump 不進 git**,用外接碟/雲端搬。
- **`.env`**（手動重建、值不入 git;**按通道分組——漏鍵=對應通道靜默失效**):
  | 通道/層 | 鍵 | 漏了會怎樣 |
  |---|---|---|
  | DB(一切之本) | `DB_HOST/PORT/NAME/USER/PASSWORD`、`DB_SUPERUSER_*`、`DB_PREDICT_PASSWORD` | 全系統不動 |
  | 市場資料(預測管線) | `FINMIND_TOKEN`（Sponsor 已續訂 2026-07-12;過期降 free tier,錶=`/user_info`）、`FRED_API_KEY` | sync/audit 死 |
  | 知識抓取①(主題/全文/abstract) | `UNPAYWALL_EMAIL`、`FRASER_API_KEY`、`SEMANTIC_SCHOLAR_API_KEY`（有則提速,無則匿名慢速）、`GITHUB_TOKEN`(如用) | OA 全文/abstract 缺源 |
  | 本機匯入②之 ERP 重抓 | `ORACLE_HOST/PORT/SERVICE_NAME/USER/PASSWORD/DSN` | ERP 語料**無法重抓**(見下 dump-only 警語) |
  | 服務層 | `AUGUR_ADMIN_PASSWORD`、`AUGUR_INTERNAL_SECRET` | admin/advisor RBAC 死 |
  | git | `git config user.name/email`(檔內註記) | commit 身分缺 |

  （⚠ **advisor LLM 本機限定 v1.37.0**——不接任何外部 LLM,GEMINI 等 key 即使存在亦不用於 advisor。）
- **SFTP 通道③ 前置（與 .env 同級人工重建;通道選配、缺=僅 SFTP 啞火）**：`~/.config/augur-sftp.json`（host/port/user/**key_path**,chmod 600、絕不存密碼）+ 其引用之 **SSH 私鑰檔**（須搬入本機且遠端重新授權）+ **.env 憑證** `SFTP_<NAME>_USER`/`SFTP_<NAME>_KEYPATH`（件 A2 `acquire_remote_files.py` 讀）。三者不在 git/dump/sync_memory——新機不重建則 SFTP 通道不可用。
- **apk 反組譯前置（#23 OS 層、非 pip、選配）**：`jadx`（skylot/jadx GitHub release 解壓、bin/jadx 入 PATH）+ JRE（如 default-jre）——`scripts/decompile_apk_to_owned.py` 依賴;未裝則該工具 graceful 報錯、不影響其餘。paramiko 已入 pyproject admin extra（`pip install -e '.[admin]'` 自帶）。
- **⚠ owned_local ERP 語料＝dump-only**：erp_tiptop 150,685 段 item_text（最大語料、佔 99%）**唯一換機載具＝DB dump**——augur repo 內無 Oracle 連接器（抽取屬外部 TTAI 工具）,dump 遺失＋原機不在＝**此語料不可復原**。dump 備份＝此語料唯一保命符。
- **向量庫**：生產 SSOT = **pgvector（在 DB dump 內、跟著 DB 走）**;Qdrant serving（`~/qdrant_augur`,augur-qdrant.service,2026-07-14 上線）= **可拋棄、`export_qdrant_index.py` 從 PG 全量重建、不需跨機搬**;舊 `~/qdrant_local`（194MB 休眠驗證產物）同可重建。
- **build 產物**（可重生勿 commit):`models_artifacts/`（.joblib、train_ranker 重生）、`data/`、`/models/`。⚠ `.gitignore` 模型輸出規則錨定 `/models/`（根限定）——**勿改回 `models/`**（會遞迴誤傷 `src/augur/models/` 源）。

## 4. 現況 STATE（取代式：每次封存點整段重寫；歷史＝`git log -p HANDOFF.md`）

> 更新於 **2026-07-23**（lint P1–P3＋執行指令矩陣入憲封存）、tag `archive-20260723-lint-p1p3-cmd-matrix`；最新 tag 見 `git tag -l 'archive-*'`。
> **紀律：本區每個宣稱都可能過期——待辦一律先跑附帶的驗證指令實查（#15），勿直接信。**

### 4.0 近程優先（2026-07-24 Steward 拍板）

> **要強化預測：力氣留在 PME（哲學↔市場）＋資料地基。**（優先序／範圍決策；**API 仍凍**——庫內可做 ≠ 解凍）

| | |
|---|---|
| **做** | **PME**（哲學↔市場進化閉環）強化預測；**資料地基庫內段**（catalog `db_only`、Dividend／attestation 唯讀親驗——已跑 2026-07-24；見下） |
| **PME 靈魂措辭** | ✅ **G-PME-SOUL=none**（2026-07-24；`SOUL-PME-B-yes`＋採納並寫入；`audits/G-PME-SOUL-CLOSED-20260724.md`）——適用**新入 know-how**（新哲學／新研發技術／新學術論文等）閘後有界自動晉升；**自動下單仍禁**；**與 FinMind／FRED 正交（≠解凍）** |
| **不做（近程）** | 孫子↔ERP、太陽能↔儲能 等**他域進化閉環**計畫／實作；不以他域進化「灌進」台股因子 |
| **凍結** | FinMind／FRED **仍凍**（條件＝憲章→實作全部落地＋明示解凍；見 §4.4）—本節不改凍結 |
| **API 洞另帳** | Dividend resume／全量 `build_catalog`／當日 attestation audit·heal — **解凍＋明示後**；G-CAT-1／G-DIV-1／G-ATTEST 仍 **partial** |
| **庫內證據** | `reports/augur_data_foundation_db_only_20260724.md` · `audits/ROADMAP-DATA-FOUNDATION-DB-ONLY-20260724.md` · tag `archive-20260724-data-foundation-db-only` |

### 4.1 一句話現況（2026-07-23；取代前版）

**本封存點**：治權 lint 清冊 P1–P3 落地＋可執行 Python「執行指令矩陣」升格元憲章（§8.1 解釋／RULING-2026-026／AL-2026-029）。

* **P1（桶 B）**：`IDO.*` 權威歸 `AUGUR-ID`；表列 IDO.1–8 入枚舉；selftest G12。
* **P2（桶 A）**：`A`／`T`／`DI`／`DO`／`EO` 可受檢（權威 WM／ONT）；L3 TR 標籤對齊；selftest G13。
* **P3（桶 C）**：L1–L6 CS／C.10「MC [N] 條款覆蓋清單」→ 全層 `wm44_uncited=0`；selftest G14；`report --sync`。
* **驗收（實跑）**：corpus **PASS 7／error 0**；L3／L4 warning **0**；L5 剩 1（既有 `KDI.18` 形態未受檢）。計畫書＝`reports/augur_l3_l4_lint_warning_remediation_plan_20260723.md`。
* **執行指令矩陣**：可執行入口 docstring 補齊 canonical「執行指令矩陣」；CLAUDE.md 從屬改引 **AUGUR-MC v1.4**；MC §0.5 L6／Appendix G 留痕（§8 [N] 本文未動、102 母集不變）。
* **機器**：本機 PC002-S1800（WSL2）；MCP `qwen3:4b` 釘死見前 commit `ac0fa35`。

**仍有效之上一錨（07-17～07-22，細節見 git／舊 STATE）**：arena 8 隊 live；alpha Phase 1 落定；monorepo 治權合併；GB10／DESKTOP 環境基準。歷史 STATE 全文＝`git log -p HANDOFF.md`。

### 4.1b 上一大進度日摘要（2026-07-17；保留索引，細節以 git 為準）

**① arena 8 隊 live（A4 波次 07-17 加入）**：07-16 開賽（gate `arena_adm_5305655ad1cd` evaluated_pass ∧ 閘一 approved；cron 三行 22:30/23:10/月初）。**07-17 加 A4 兩隊**（Chronos-2 `chronos2_market_5` + Moirai-2.0 `moirai2_small_5`；dgate_a4 K=2/α=0.025/21 門全序列揭露；hugo TTY approve×2——**憲章 v1.42.0 TTY 閘實證擋 AI 代跑**）。**8 隊全員 live**（4 本地+4 TSFM）；chronos/timesfm 套件已補（uni2ts 降級 numpy/torch、四關驗綠）。review_observation_only tier、確立唯門二（≥60 clusters）。license 白名單擴 cc-by-nc-4.0（Moirai NC、**商業化前須清算**）。

**② 治權批次（07-17 hugo「全批照案」）**：原則精華 **v1.9.1**／憲章 **v1.46.0**／CLAUDE **v1.29**／README／HANDOFF——live 准入 unfreeze gate(退史料)→arena 前置 G1-G5 機制；判準值零變動。**+平行 meta-憲章體系**（你另一會話：`augur-constitution` AUGUR-MC v1.3 Layer 0 lex superior、5 治權檔已加從屬聲明檔頭、AUD 審計；rebase 整合乾淨）。

**③ TSFM benchmark（鏡射 arXiv:2606.27100）**：台股 top5×10 窗×6 模型——**20 個 DM 檢定零顯著勝隨機漫步**（Chronos-2 最不退化）；「最適合台股點預測=零報酬 RW」。TSFM 正確用途=arena 候選非點預測。報告=`reports/tsfm_taiwan_benchmark_20260717.md`+工具 `scripts/benchmark_tsfm_taiwan.py`。

**④ alpha 提升計畫（07-17 拍板開工）**：`reports/taiwan_alpha_improvement_plan_20260717.md`（三軸 D/P/M、51 項對抗審查、11 拍板點）。**Phase 1 進度**：1-0 P0 診斷 ✅→**§0 驚雷=headline 錨 1.1972 不可再現**→修復鏈（見⑤）；1-1 recipe DDL ✅（trial_ledger +recipe 欄/UNIQUE 8）；1-2 P2 turnover 半和量尺 ✅（headline→1.1302）；1-3 P1 buffer **判死**（雙宇宙判準攔 asof 假象、ledger N=33）；1-4 P4 vol-target **無靶不啟用**（能力清償）；1-5 全鏈刷新 ✅；**1-6~1-9 完成**（opus-4-8 resume；**D2+D3 共 7 候選全滅、無一抵經濟終關**——預診放棄 3〔size/vol 代理〕、死於 IC 3〔x_foreign_streak_60d=iid −2.22 越線但 HAC −1.78 崩線=G8 教科書〕、死於增量 1〔x_limitup_reversal_5d Δ−0.049，帶稀疏宇宙混淆→S1〕；**N 維持 33、headline 1.1302 不動、生產表全淨**）。1-8 D1 前置=純盤點（BS 15 系統性缺季/~2.4–3.1k calls 待授權、去累計 32+2、金融股 60d 分支設計）；1-9 live OOS 承接=草案（排程歸屬+R1–R8 預註冊+**DSR N 陳舊斷鏈發現**）。報告=`reports/alpha_phase1_tail_verdict_20260717.md`；**9 拍板點待 hugo**（重點 C2=DSR 重算涵蓋修 N=32/33 陳舊）。**→ Phase 1 全 9 項落定（1-3/1-4/1-6~1-7 全誠實紅=功能非缺陷）**。

**⑤ 錨修復鏈（hugo A/(a)/(i) 三裁）**：PriceAdj 修復（41 真損傷/175=除息跳點誤標定案）→新錨 **net 1.1302／超額+0.372／HAC-t 6.70／DSR 47.9%**（KPI SSOT=N=32 保守口徑）→`revalidation_baseline` re-freeze→**judgestop 相對式條款**（`deflated_decay_margin=0.10` frozen 取代絕對零線；絕對線在 N=32 下 baseline 自身為負=恆觸發失鑑別力）→verdict state=`deploying_unestablished`。econ_verdict 全程 thin 未變向。**DB dump=`C:\database\augur_pgdump_20260718_Fd.tar`（修復後乾淨快照）**。

**舊狀態（07-16 及前，仍有效）**：unfreeze gate 路徑退役+G1-PIN+G1-G5 七元件+撤列容忍——詳 git `f851742`/`1ac820c` 版本段。件 A DDL 待 apply+TTY 活化；件 B harvest 停 ~99,229 abstracts 待續；Qdrant serving 運行中。
**unfreeze gate 路徑退役（hugo 拍板 07-16）**：`preregister_unfreeze_gate.evaluate()` 實測=純唯讀診斷（守門1-4 過但 G1-G5 標「本計畫內不可達」未實作、不改 status）→ 接受解凍已由 07-12 入憲完成、`unfreeze_06dcb178267d` **superseded 史料**（evaluation_ref 雙向鏈指新 gate）；**arena 前置改 G1-G5 實質驗證機制**（計畫+決策紀錄＝`reports/arena_g1g5_admission_gate_plan_20260716.md`：D-1~D-6/D-11 全拍板、D-2=Reading A 方向確立走門二、G3/G4 歸相對強度部署）。
**G1-PIN（hugo 拍板）**：arena 資料地基 **as-of 釘死 2026-06-30、不再滾動追資料完整**（live byte 對帳=移動標靶=「凍一條河」概念錯誤）；≤05-31 凍結期認證+06 月窗抽樣對帳 **PASS**（attestation #4：VM0/EX0、撤列容忍 36 揭露、`audit_since=2026-06-01`）。
**G1-G5 機制七元件全落地**（`migrate_arena_admission_gate_ddl`/`preregister_arena_admission_gate`(繼承 990ddea sha 斷言)/`freeze_feature_panel_hash`(兩軸 36+2,830 panel 洩漏鎖)/`verify_score_repro`(112 組 5 位復現)/`report_restatement_diff`(U5 佇列)/`evaluate_arena_admission`(核心裁判、--check 唯讀預演)/雙閘接線 daily_pipeline+arena_round fail-closed）。
**撤列容忍第三層（hugo 拍 A）**：per-stock EX 雙端點證實 API 現況無=上游撤列=合法 restatement 容忍揭露（FRED Tier A 同構；抓失敗保守留 EX）；3 表先例歸類（TaiwanStockInfo→snapshot、SplitPrice→cadence、FuturesDealer→restating 上游整批撤申報實證）。
**件 A/件 B/Qdrant**：狀態同 07-14 版（件 A DDL 待 apply+TTY 活化；件 B harvest 熔斷停於 ~99,229 abstracts 待續；Qdrant serving 運行中）——見 git log `c7656ac` 前版本段。

> **⚠ #7 attestation 對帳範圍變更（hugo 拍板 2026-07-14，決策層）**：對帳窗由 `since=2026-06-01` **縮至 `2026-07-01`（近 ~14 日）**。理由：6/1 起全量對帳（75 dataset×數十交易日=數千 fetch）之 **sustained API 負載 throttle FinMind IP（sustained 403、額度不滿仍拒）**，反覆循環無法綠；歷史凍結期（至 2026-05-31）已對帳定案、近 14 日足以 attestation 最近 live 增量。同步修：daily_maintenance 對帳加 per-dataset log＋reconcile per-3-date progress（解 audit_selfheal v2 看門狗誤殺無-log 長對帳之死循環）；audit interval 實驗值 0.7（#27，撞 403 退回 0.9）。落地＝`audit_selfheal.sh`。

> **⚠ #7 attestation 判準二次變更（hugo 拍板 2026-07-14 (a)+(b)，決策層）**：07-14 首輪 FAIL（VM 3,760/EX 84,996/MIS 9,759）鑑識＝三家族且全數入帳——①**端點錯配**（EX 之 94%：roster-scoped 名錄被 by-date 端點對帳→假 EX；catalog `reconcile_scope` 早已標對、daily_maintenance 未路由）②**移動邊緣**（外盤時差 UK VM 3,451/期貨夜盤/T+1 發布——把未定稿日納入比對必紅）③**合法重述**（PriceAdj 除權息季全序列重算）。裁決：**(a) 滾動安全邊緣**＝各表對帳窗上限 today−`finalize_lag_days`（外盤/夜盤/T+1 類=2，餘=1；**不是**固定封 6/30——固定封頂使 live 增量永不被 attest 且治不了①③）；**(b) 分類感知**＝catalog 加 `attestation_mode`（byte/snapshot/restating/coverage；snapshot 名錄=API 僅現況宇宙、DB as-of 保存反倖存偏差→豁免誠實列印；restating 豁免註記；coverage=News 量級對帳）＋ 對帳依 `reconcile_scope` 路由端點。落地＝`migrate_attestation_catalog_ddl.py`（seed snapshot 7/restating 1/coverage 1/lag2 6）＋ `reconcile_by_date/heal_by_date` 加 `until` ＋ `daily_maintenance` 路由+`--audit-all --heal`+exit 三態（0 綠/2 對帳紅終態不重試/3 未完整可重試——**rc=0≠PASS 假綠鏈已修**：selfheal rc=2 終態、watchdog 以最後 attestation 行判態）。**綠哨兵句改為「attestation：✅ PASS」**（舊「✓ audit 完成(rc=0)」廢止——rc=0 曾致三層假綠）。債：snapshot 表專屬「現況快照比對」未建（現=豁免+可 `reconcile_market` 手動抽驗）；roster-scoped 日常 attest=40 股抽樣（部分覆蓋、誠實列印）。
> **⚠ 同日三次微調（hugo 拍板 2026-07-14）**：①外盤 `finalize_lag_days` 2→**3**（UK/EU/JP/US Price；全球化+天災延遲發布餘裕；期貨夜盤/T+1 維持 2）——hugo 原提滯後 10 天，裁後採 3：偵測延遲代價（10 天未 attest 資料入管線）> 收益，且晚修正由滾動再驗視窗（每夜重驗 14 天）+heal 承接、非 lag 職責。②對帳窗改**滾動 `--audit-days 14`**（since=today−14；取代寫死 2026-07-01——寫死窗隨時間膨脹重演 IP throttle；**滾出窗之日以最後一次 attest 定案**，同 05-31 凍結先例）。③selfheal 改用 `--audit-days 14 --audit-all --heal`。

### 4.2 下一步（可直接執行，含前置條件）
```bash
# 前置已全達成(07-16):E1/strict 19 綠、arena_admission_gate evaluated_pass、雙閘開。驗現況:
python scripts/run_arena_daily_pipeline.py --dry-run     # 應印「機械閘一…(開) | 機械閘二…✓(開)」
python scripts/evaluate_arena_admission.py --check arena_adm_5305655ad1cd   # 唯讀預演、應 rc=0
# ① 開賽(hugo 拍板時點):掛 A2 已核 cron 三行(arena launch plan §5;10 23 * * 1-5 等)+首日手動陪跑:
python scripts/run_arena_daily_pipeline.py --run          # 雙閘 AND 放行才真跑
# ② 開賽後常態:每日管線+settle_arena_labels+arena_scoreboard(cron);方向確立=門二 evaluate(≥60 clusters)
# ③ 治權修訂批次(§8 提案待 hugo,見 4.5-6)
```

### 4.3 正在跑的東西（殺掉前先看這裡）
| 工作 | 觀察方式 | 存活檢查 |
|---|---|---|
| audit 自癒跑者（nohup 脫離、撐過 session） | `tail -f ~/audit_retry.log` | `pgrep -f daily_maintenance` |
| systemd 六服務＋3 timers（開機自起） | `systemctl --user list-units 'augur-*'` | 端口 curl 序見 memory `restart-systemd-after-edit` |
| audit 續跑/重啟（**腳本已入 repo=`audit_selfheal.sh`**） | `nohup flock -n /tmp/augur_audit.lock bash audit_selfheal.sh >/dev/null 2>&1 &` | 探測先行＋PYTHONUNBUFFERED;log=~/audit_retry.log |

**⚠ 換機注意（2026-07-13）**：舊機的 audit 跑者/watcher **不隨機器遷移**——新機還原 DB 後，audit 對帳狀態已在 DB（dump 含 658,911 列增量、取於尾段對帳中），**新機第一件事＝`bash audit_selfheal.sh` 續跑至綠**（DB-driven resume、冪等快轉已對帳段;新 IP 對 FinMind 反而有利），綠後接 4.2 鏈。嵌入積壓（469,551 句）由新機 03:30 timer 或手動 `systemctl --user start augur-embed-catchup` 補。

### 4.4 紅線（絕不能做）
- ⚠ **操作凍結（2026-07-24；同日收緊）**：**FinMind／FRED 外部 API 一律不開**，直至 **憲章→實作路線圖（constitution-to-implementation）全部階段落地完成之後**，且用戶明示解凍（「解凍 FinMind／FRED」等）——含 sync／probe／放量／窄窗／Dividend 重建；**「計畫落地」／近程 R5 DONE（S1–S3＋U5）／局部階段完成 ≠ 解凍**；護欄＝`.cursor/rules/finmind-fred-api-freeze.mdc`（alwaysApply）。允許本地 DB 唯讀／零網路／計畫／免 API pytest／零 API 實作。R5 近程證據：`audits/ROADMAP-R5-S3-STATUS-20260724.md` · `ROADMAP-U5-R5-ULTRACODE-20260724.md`（**禁**確立級／可交易宣稱；`direction_gate.evaluated_pass=0`）。
- ⚠ **`evaluate_arena_admission --evaluate` 是終態寫入**（evaluated_pass/fail 皆不可回改、複核=另立新 gate）——**必先 `--check`（唯讀預演）綠才 evaluate**（07-16 實證:--check 曾因 bug 假紅,預演救了不白燒）。舊「unfreeze gate evaluate」紅線已隨 gate 退史料失效（該 evaluate 實為唯讀 stub）。
- ⚠ **FinMind 類作業（市場補同步／PriceAdj 修復）與 audit 互斥**——同一 IP，audit 跑完才輪它們（#24 IP sustained ban 07-12 實錘）。**本階段兩者皆凍（見上條操作凍結）**。
- ⚠ **PDF 抽取未經 P0 拍板前不啟動**（含 OAPEN 61/skip_pdf 976）——OCR 維持不啟動（P8 原裁定）;IA 掃蕩已完成(491 抓/其餘誠實終態)、勿重複放量。

### 4.5 待人類 vs 待 AI
**待 hugo 拍板**（全部非阻塞開賽）：
1. **PDF 抽取計畫 P0**＝`reports/knowledge_pdf_extraction_plan_20260712.md`（D2 後續;pypdf+五道機械品質閘 fail-closed;OAPEN 61+skip_pdf 976）
2. 短 horizon 模型計畫②＋全能顧問計畫①：**hugo 已裁「開賽後 AI 先做時效性複核再拍」**（2026-07-12;兩案早於解凍/擂台設計,恐部分被超越）
3. ~~舊專案 stock_backend 的平日 16:00 FinMind cron 去留~~ **已裁定（2026-07-13 hugo）：4 條 cron 全部取消**（同 IP 疊加解除；備份=`~/crontab_stock_backend_backup_20260713.txt` 可復原）
4. **件 A 三通道公民化 DDL apply + 源活化**（code 已完成、非阻塞開賽）：`python scripts/migrate_local_admission_ddl.py --apply` ＋ `python scripts/migrate_sftp_sync_ddl.py --apply`（**須 audit 綠 + harvest 靜止後**，#30 dump 期禁 DDL）→ 再由 hugo **TTY 逐源 approve/activate**（AI 不自活化源、憲章 v1.41.0）→ `systemctl --user restart augur-admin`（載入 P-web 新碼）→ `bash install_services.sh --with-refresh`（開 know-how 週更 timer，R-A-R3）。SFTP/apk 另需 §3 人工前置（`augur-sftp.json`+私鑰 / jadx+JRE）。
5. **R-H 修憲（OCR/ASR 轉錄≠AI + 本機/SFTP 明文豁免）**：v3 提案＝`reports/augur_rh_amendment_transcription_exemption_v3_20260714.md`；T2 CLAUDE #29b 條文（Fable 5 檔位、治權檔）待 hugo 確認後才動筆改治權檔。
6. **arena 開賽 cron 掛載時點**（雙閘已開、機械前置全綠;掛載＝開賽＝hugo 決策）。
7. ~~G1-G5 治權修訂批次~~ **已完成（2026-07-17 hugo「全批照案」）**：原則精華 v1.9.1／憲章 v1.46.0／CLAUDE v1.29／README／HANDOFF 全鏈級聯（判準值零變動、僅機制指向;詳憲章修訂歷程 v1.46.0）。
8. **alpha 計畫 11 拍板點**（`reports/taiwan_alpha_improvement_plan_20260717.md` §七）——大部分候選待逐支 productionize 拍板;Phase 1 已執行 1-0~1-5+1-6 部分。
9. **alpha 1-6~1-9 之 9 拍板點**（`reports/alpha_phase1_tail_verdict_20260717.md`）：S1 稀疏公平測、D1-放量(BS 缺季 API)、D1-lag(金融法源)、A1 systemd timer、A2 季頻續建、A3 告警檢視、B(R1–R8 凍結)、C1 dsr provenance、**C2 DSR 重算涵蓋(修 N=32/33 陳舊斷鏈,最實質)**。
10. **A4 Moirai NC license 清算**（商業化前）：cc-by-nc-4.0 依賴 provenance 已留痕。

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
- **audit 對帳段會無聲卡死**（2026-07-13 實證:API 讀無效 timeout 掛 9h,`poll_schedule_timeout`+rchar 0）——「進程活著+log 靜默」≠ 在跑;診斷=`/proc/<pid>/wchan`+10s rchar 差;`audit_selfheal.sh` v2 已內建 45 分靜默看門狗自動殺掉續跑。
- **pgvector HNSW + CLEAN WHERE 過濾＝假空/假 FAIL**（2026-07-14 實證,記憶 `qdrant-serving-hnsw-overfilter`）：最近向量多為 local_private,HNSW 先取 top-ef 再 WHERE 濾 public→濾空→retrieval 假空、shadow eval 假 FAIL(0.302)。**鑑識法＝exact baseline**(`SET LOCAL enable_indexscan=off` 強制精確)比對；Qdrant 對 exact=0.988(非 Qdrant 之過)。shadow eval baseline 已改強制 exact→0.972 PASS。
- **FinMind per-stock vs by-date 端點不對稱＝假 EX**（2026-07-14 實證）：同 dataset,名錄(roster-scoped)以 by-date 端點對帳、生產以 per-stock 抓,某日 per-stock 缺該 date 但 by-date 有→假 extra_in_db(非幻像)。**A 案交叉驗證**（by-date confirms→扣抵 EX）已入 `reconcile.py`;catalog `reconcile_scope` 標端點、`daily_maintenance` 依此路由。
- **scripts/ 改動不入 pytest 回歸＝靜默 regression**（2026-07-14 實證）：P-A1 令 `acquire_local_files.py` --source-key 必填,弄壞 `verify_knowledge_e2e_smoke.py`(scripts/ 非 pytest,200 passed 全套沒抓到)。教訓＝改共用 acquire 函式後須手跑 `verify_knowledge_e2e_smoke.py`(暢通不變式機械判定,憲章 v1.40.0);已修(fixture 帶 --source-key + active 源需 approved_by 過 `chk_ks_active_needs_approval`)。
- **`SELECT run_at::date … ORDER BY run_at` = 別名遮蔽排序退化**（2026-07-16 實證）：cast 輸出欄名仍=`run_at`,ORDER BY 綁到輸出欄(date 型)→同日兩列未定序→evaluator 抓到舊 FAIL 列(gate --check 假紅)。修=cast 一律 `AS` 別名。
- **psycopg2 named cursor 跨 commit 即失效**（2026-07-16 實證）：流式讀+分批 commit 必 `conn.cursor(name=…, withhold=True)`,否則首次 commit 殺 cursor(`named cursor isn't valid anymore`)。
- **背景命令包 `| tail` = exit code 假綠**（2026-07-16 實證）：pipe 的 exit=尾端命令,traceback 進程顯示 exit 0。背景跑不包 pipe、或 `set -o pipefail`。

### 4.7 路由表（去哪讀什麼；本檔不複述）
| 要什麼 | 去哪 |
|---|---|
| 規則/工具紀律 | `CLAUDE.md`（版本見檔頭；#31＝接續慣例） |
| 判準/憲法 | `docs/系統架構大憲章_v1.46.0.md`＋`docs/原則精華_v1.10.0.md`＋`docs/系統核心思想_v1.8.0.md` |
| 這專案怎麼建的 | `reports/augur_construction_understanding_20260710.md`（v3 code-verified） |
| 擂台規格 | `reports/augur_direction_live_arena_plan_20260711.md` |
| arena 前置 G1-G5 gate（現行開賽機制+Phase 0 決策紀錄） | `reports/arena_g1g5_admission_gate_plan_20260716.md` |
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
