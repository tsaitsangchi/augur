> **Monorepo 註（2026-07-22）**：本倉已合併治權樹。治權交接見 [`HANDOFF-governance.md`](HANDOFF-governance.md)；遷移清單見 [`ops/phase2/MONOREPO-LEARNING-MIGRATION.md`](ops/phase2/MONOREPO-LEARNING-MIGRATION.md)。

# HANDOFF — augur 跨機接續指南

> **這份文件是什麼**：augur 會在**另一台電腦接續開發**。這是「新機 clone 後第一份該讀的文件」——
> 告訴你**從哪接、怎麼跑起來、哪些不在 git、進度到哪、紅線是什麼**。
> 快照時點：**2026-07-30**（最新封存 tag＝`archive-20260730-net8-tail-closed`，一覽＝`git tag -l 'archive-*' | tail -3`；HEAD 以 `git log -1` 為準——**HEAD 每日多次前進，勿以本行推斷現況**）。（2026-07-30 機械軌：依實跑 `git tag -l 'archive-*'`／`git log -1` 重戳；原戳＝2026-07-26／`archive-20260726-evo-ruler-v2plan-phase0`）
>
> **2026-07-26 地基級更正（接續者必讀）**：本地 AI 演化的舊評測尺經親驗失效——一條不看題目的常數樣板得 0.654、高於當時現役 pack 的 0.492；竄改金標數字仍得 1.000（事實敏感度 0%）；`think:false` 對 qwen3:4b 無效致評到的是被截斷的思考鏈。**今日之前所有 LAIEVO 能力數字（0.492/0.567/0.521…）無證據力**。新尺已建（凍結集 `local_model_eval_item`＋三軸 0/1 `src/augur/evolution/behavior_rubric.py`＋多臂 `scripts/eval_local_model.py`），首個有證據力的數字＝behavior 臂 **F@L1 0.933**（floor 0.000／mismatched 0.000／shuffled 0.167）。新一代總控計畫＝`reports/augur_self_evolution_master_plan_v2_20260726.md`。
>
> **⚠ 2026-07-30 機械軌補註（本段為 07-26 當日史述、其值不改）**：尺已於 **07-28 再換一次**——`V2-RUBRIC-go`（`audits/V2-RUBRIC-GO-20260728.md`）加 robot 第五對照臂＋L1「加料年份否決」＋換真地板，`eval_code_hash` `f3075238eb55`→**`ef142e9374c1`**。新尺離線實測 **robot 五格全 1.000**＝本凍結集每一格皆「零知識格式即可達」，依同檔鐵則 **live 臂於本集任何格至多判 `none`**；故上句 **0.933 不得再作為「有證據力之能力數字」引用**（尺誠實說出本集無可證格；可證能力之格待 S-4 凍結集重建拍板）。

---


## 重開機／接續狀態（2026-08-02 00:xx，封存點 `adjudication-complete-20260801`＋後續 commits）

**08-01 一日要旨（接續者最速讀法＝記憶 `augur-adjudication-exec-20260801` → 終版圈選單 `reports/augur_final_adjudication_ballot_20260801.md` → 登錄冊全冊 ☑）**：
治理迴路首次全循環——24 項問題「呈案→12 路鮮度驗證→Steward 圈選→機械施作（全程突變驗紅）→TTY 親簽→驗收落帳」一日閉環；追加迷你批 3 裁（MM 37 例／D2S sim 門 T-A／P2a+§5乙）。
**當日落地之新機制（接續者須知其存在）**：TWEVO 八閘含 G-SIGN（77 筆乙案遷移訖）；UPDATE-GUC 閘擴至 15 表（治權表裸 UPDATE 面 20→15；kill_switch 依乙案豁免=緊急煞車零摩擦）；validation_evidence manual 90 天有效期（10-09/10-10 到期）；identity 六表生產（registry 3,503；37 例 mismatch 已裁 A/B 收 C 留）；fulltext `unattempted` 121,389；CLAUDE.md **v1.35 #35 回歸鎖三規則**＋pre-commit 假斷言第四閘；RULING-2026-042 生效（L7.16 衝突登錄）；`iid_bootstrap` 入 sim registry（門待 D2S INSERT 親簽後才可評）；週報 (b) per-(feature,h) 口徑。
**08-02 晚已兌現**：run 21 succeeded→hugo `--queue-id` 逐顆親簽 556/599＝**首兩顆引擎自掙晉升**（prodset active=3、週報 (b) ✅）；SIM-CAL-R1 sim 門親簽生效＋四件套落地＋P0 候選落戶（`sim-clock-armed-20260802`；首格待 08-03 anchor、T-A 首判 ~11 月上旬；S-4=人工逐次觸發勿排程）；P2a+P2b 全落（裸 UPDATE 面 20→9 表）。**餘**：I5B-甲 **已落地**（`2b6350d`；run 22 首次生效）；run 22=**今晚 23:00** TWEVO 仍發車；attestation watchdog **今晚不發車**（見夜 runbook）；10-14 備料＝`reports/augur_1014_review_evidence_prep_20260801.md`。**優化**：**逐步執行**＝`reports/augur_optimization_step_plan_20260803.md`；理解＝`augur_optimization_foundation_unified_20260803.md`；細項＝`augur_optimization_master_plan_20260803.md`；今晚＝`ops/RUNBOOK-20260803-night.md`；**守門就緒包**＝`audits/NIGHT-GUARD-CHECKLIST-20260803.md`（M-T5＋19:30＋22:5x `--prerun`＋隔晨 observe）；落地帳＝`audits/MN1-MN2-LANDING-20260803.md`（探針骨架）＋本檔 M-N4 數字校正。

## 重開機／接續狀態（2026-07-31 11:2x，封存點 `archive-20260731-sim-axis-live`）

**重開後會自己回來**：13 個 enabled user unit（chat/admin/advisor/probability/ollama/qdrant
＋7 個 timer）＋**<!--probe:doc_handoff_cron_lines-->15<!--/probe-->** 條 crontab（probe `doc_handoff_cron_lines`＝`crontab -l | grep -c '^[0-9*]'`，`read_treaty_probes.py --check` 驗 diff；M-N4 2026-08-03 由手抄 12 校正）。`Linger=yes` 已設，**無登入亦自起**。
帶 `Persistent=true` 的 timer 會在開機後補跑錯過的班次。

**重開後須人工確認的三件**
1. **五埠實測**（不能只看 `systemctl is-active`）：
   `for p in 8090 8500 8399 8600 11434; do curl -s -o /dev/null -w "$p:%{http_code}\n" --max-time 8 http://127.0.0.1:$p/; done`
   advisor(:8399) 對 `/` 回 **404 是正常**（OpenAI 相容 API），驗 `/v1/models` 應回 200。
2. **孤兒佔埠檢查**（2026-07-31 實踩：`systemctl restart` 成功但跑的是 20 小時前的碼）：
   `ss -tlnp | grep -E ':(8090|8500|8399|8600|11434)'` → 取 pid → `ps -o lstart,cmd -p <pid>`
   ——**啟動路徑須為絕對路徑**（`/home/hugo/project/augur/venv/...`）；
   若見相對路徑 `./venv/...` 即為 shell 起的孤兒，systemd 副本會在背後崩潰重啟。
3. ~~**qdrant 二進位在 `~/project/ttai/.qdrant_server/`（跨專案依賴）**~~
   **【2026-07-31 已解除】** `~/project/ttai/` 已刪除；二進位遷入 **`~/project/augur/.qdrant_server/qdrant`**
   （unit 之 `ExecStart` 與 `install_services.sh:26` 已同步改指，重啟後以 `ps` 實測確認跑的是新路徑）。
   storage 仍在 `~/qdrant_augur`、未受影響；pgvector 仍是 SSOT。**r2 債 #40 至此結案。**

**重開會中斷、且不可自動續跑者（2026-07-31 當下在跑）**
- `run_philosophy_evolution.py --local-gates` ×2（**resume 跡象 0 ＝重跑須從頭**）。
- `run_evolution_iteration.py`（drain timer 補跑 `tw-20260728-r01`，**resume 完整**）
  ——中斷後由 30 分一次的 `augur-drain-deferred.timer` 自動再補，不需人管。
- DB 進行中交易將 rollback（皆為冪等管線，重跑即續）。

**未閉狀態（重開後仍在，非重開造成；數字＝2026-08-03 M-N4 現查，旁附可重跑指令）**
- `evolution_iteration_ledger.tw-20260728-r01` status=running、closed_at NULL（殭屍輪，補跑中）。
- `evolution_deferred_work` 未清 **<!--probe:doc_handoff_deferred_uncleared-->0<!--/probe-->** 筆／總 9 列已清（probe `doc_handoff_deferred_uncleared`＝`SELECT count(*) FROM evolution_deferred_work WHERE cleared_at IS NULL`，`read_treaty_probes.py --check` 驗 diff）。
- `validation_evidence` 現況 <!--probe:doc_handoff_ve_status-->total=25 green=14 red=9 unverified=2<!--/probe-->（probe `doc_handoff_ve_status`，`read_treaty_probes.py --check` 驗 diff；詳表＝`python scripts/verify_validation_evidence.py --list`；計畫舊抄「19／red 3」已過期）。

**接續讀序**：本檔 → **`reports/augur_optimization_step_plan_20260803.md`（逐步執行）** → `augur_optimization_foundation_unified_20260803.md`（理解）→ `augur_optimization_master_plan_20260803.md`（M-* 全表）→ `ops/RUNBOOK-20260803-night.md` → r3／建構理解。
→ sim＝子計畫＋候選已 1 列；I5B 已落地；今晚 TWEVO 23:00 仍發、attestation watchdog **不**發（操作 checklist＝`audits/NIGHT-GUARD-CHECKLIST-20260803.md`）。
memory 已 export 至 `handoff_memory/`，新機以 `python3 sync_memory.py restore` 還原。

## 0.5 增補快照 2026-07-18（Phase 1 憲章化收官——接續者必讀）

**main HEAD＝`f95557b`**（AUD-02＋identity 補正已併入並部署生產）。本日完成：
* **Phase 1 全線收官**（憲章移轉計畫第一期）：(a) 分支三鏡對抗審查全 GO＋Steward 准併；(b) hugo 側部署＋heal 快照 gate 上線；(c) predict role refresh（REVOKE 84 素養／GRANT 163 預測）；(d) ~~**owner 分離生產生效**——十張憲章表＋2 抹除函式隸 `augur_owner`（NOLOGIN），應用角色 `augur_app` 僅 SELECT/INSERT，`augur` 留維運通道；服務連線已切 `augur_app`。~~
  **【2026-07-31 誠實更正】本段所述於當家機 `PC002-S1800` **從未成立**：實查 `augur_owner`／`augur_app` 兩角色**皆不存在**、`augur` 缺 DELETE 之表數＝**0**（零 ACL 型 append-only）、306→322 張表 owner 全為 `augur`、服務連線一律 `augur`。本段所提之 `/home/giga/augur/backups/` 亦不存在（本機無 `giga` 帳號）⇒ **本節描述之對象應為另一載體**，本檔先前未標明。又：`augur` 已於 2026-07-31 升為 **superuser**（Steward 拍板），**owner 分離設計自此失去意義**。留痕見 `reports/augur_db_role_architecture_submission_20260731.md` §6.2（OCV 四項對照）。**
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
| `docs/系統核心思想_v1.10.0.md` | **靈魂**：預測**相對強弱**＋預言機軸(絕對方向機率,唯過 direction_gate;v1.6.0;v1.8.0 三度堅持刪「不是預測絕對漲跌幅」句,E[r] 升格幅度級得逐股(GATE/econ 同源/揭露硬綁不動))（非絕對漲跌機率）、成功=經濟價值非 IC、系統建議人決策、禁 AI 占卜大師 |
| `docs/原則精華_v1.12.0.md` | **20 條不可違反法律** + 資料完整性判準（**FREEZE 已解凍→live 增量維運**;live 准入=arena 前置 G1-G5 機制；**#7 supersede／RULING-2026-041**） |
| `docs/系統架構大憲章_v1.54.0.md` | **憲法**：三敵×管線、12-PHASE、升版規則、**知識一律准入＋漸進 KH（v1.48.0 入憲，現行 v1.51.0）**、第六部計畫先行、修訂歷程（2026-07-30 機械軌：14:33 親跑 `ls -1 docs/系統架構大憲章_*.md` ＋ `head -1` 實查現行＝**v1.51.0**〔同日 `4dae4bb` 升 v1.50.0、`24f020a` 再升 v1.51.0，一日兩升〕；原寫「現行 v1.49.0」與同列檔名自相矛盾故更正；「v1.48.0 入憲」為史述、未動。**本行版號一日內可再變——引用前一律 `ls docs/`**） |
| `CLAUDE.md`（版本見檔頭） | AI 協作工具規則（Read-before-Edit、clean-room #16、plan-first #20、一支一支檢視 #19、常駐服務改碼須重啟實測 #7、最小 usage #28、DB 備份慣例 #30） |
| `reports/augur_construction_understanding_20260713.md` | **⭐建構作法完整理解 v4（code-verified；58-agent 多視角深讀＋12 條承重宣稱 REFUTED 後採更正版；該檔自陳 supersede `20260710.md`＝v3）**：兩半系統＋第三塊審議引擎、逐層 how-built、治權→code 接線、§11 債/斷線/埋雷、§12 對 v3 差異——**接手必讀「這專案怎麼建的」**；`20260710.md`（v3）／`20260709.md` 降為史料（2026-07-30 機械軌：`ls reports/augur_construction_understanding_*` 實查 v4 在檔，原索引指 v3） |
| `reports/augur_omniscient_advisor_plan_20260709.md` | **活躍計畫①**：全能全知顧問端到端（know-how→DB→逐字理解→Qdrant→qwen→web UI）——**未執行、待拍板** |
| `reports/augur_prediction_short_horizon_model_plan_20260709.md` | **短 horizon（原計畫②）**：執行鏈已結案（closure 07-11）；**2026-07-29 採納 `SH-CAL-yes`＋`SH-CLOSE-yes`**（P30←H20、P60←H40；H60≠「60 天」）＋**WAVE2 `SH-ASOF-REFRESH-yes` CLOSED**（universe＋predict dry-run @2026-06-30；見 `audits/SH-ASOF-REFRESH-CLOSED-20260729.md`）——**`SH-REVAL` 仍未開**；GBDT registry 未拍；clarify＝`reports/augur_short_horizon_timeliness_clarify_20260729.md`／`audits/SH-CAL-CLOSE-APPROVED-20260729.md` |
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

> **排程：新機必跑兩支（2026-07-26 補齊；此前 cron 完全無工具管、換機即失）**
> - `bash install_services.sh` — systemd user 服務棧＋timers＋**drop-in**（l2-deliberation 的 LLM 單槽鎖、knowhow-refresh 時間平移）
> - `bash install_cron.sh --apply` — crontab 之 augur 區塊（以 `# >>> augur` 標記圍出，**合併而非覆蓋**：他人條目原封保留）。首次於已有舊條目的機器上跑會被拒絕並列出待取代項，確認後改 `--migrate`。無參數＝唯讀 diff、`--dry-run` 預覽、`--uninstall` 只移除 augur 區塊。
>
> 兩支的排程內容是各自檔內的單一 SSOT（改排程改檔、跑一次即生效、隨 git 走）。**共用一把 LLM 單槽鎖 `/tmp/augur_llm.lock`**——ollama `-np 1` 全域序列化，不鎖則多支互搶、全部變慢且結果不可比。

- **DB**（靠 dump 搬、#30;**本條＝dump 之單一住所 SSOT**，別處只許留指針、不得各自宣稱「最新」）:**⚠ 2026-07-31 全面更正——`~/db_dumps/` 已由 Steward 清空，本行原載之五份 dump 全部不存在。**
  **現行唯一備份＝`/mnt/c/database/augur_pgdump_20260731_Fd`**（Windows C 碟；本日 09:20:38 建、11 GB、`pg_restore -l` 可解析、**2,748 個物件**、含整併前之 `ttai_import` 151 物件與 `touch_updated_at()`＋2 trigger、承重表 DATA 段俱在——2026-07-31 實查）。**它是「augur ＝ 全部」整併前的最後快照**，亦是 `ttai_import`／`augur_predict` GRANT 佈局／兩個 touch trigger 之唯一復原來源。
  ~~原記述：最新＝`~/db_dumps/augur_20260726_Fd`；備援 `augur_pgdump_20260718_Fd`／`_20260714_Fd`／`_20260712_Fd.tar`；`augur_pg17_20260722.dump` 為 0 byte 空檔~~——**以上五者已於 2026-07-31 刪除，勿再引用**。⚠ **本機 `~/db_dumps/` 現為空目錄**；下次備份請重新產生並更新本條（本條為 dump 單一住所 SSOT）。;⚠ 本機**無 `/mnt/d`**（舊文所載 `D:\database\…tar` 單檔版於本機不可及;若在外接碟須先掛載並實查，勿假設存在）。**史註**：原文「最新＝`augur_pgdump_20260713_Fd`（含 07-12 全日成果＝擂台九門簽核／三鏡頭月頻／491 件公版全文＋469,551 句／K 計畫橋表／**audit 增量 658,911 列**;取於 audit 尾段對帳中）」係 **07-13 當時值**、已被 07-18／07-26 取代——**換機勿再取 07-13 庫**（其 headline 口徑早於 PriceAdj 錨修復）;audit 續跑之 API 面受 §4.4 凍結約束，見該條。還原一律用 `bash import_database.sh`（自動判 tar/-Fd/-Fc、平行還原;新機庫不存在直接建、取代既有須 `--force`）。56GB 庫=35GB 資料+21GB 索引,dump ~10GB 屬正常。**dump 不進 git**,用外接碟/雲端搬。
- **`.env`**（手動重建、值不入 git;**按通道分組——漏鍵=對應通道靜默失效**):
  | 通道/層 | 鍵 | 漏了會怎樣 |
  |---|---|---|
  | DB(一切之本) | `DB_HOST/PORT/NAME/USER/PASSWORD`、`DB_SUPERUSER_*`（⚠ `augur` 已為 superuser、此組現屬冗餘）;~~`DB_PREDICT_PASSWORD`~~（**2026-07-31 `augur_predict` 已退役、此鍵可移除**） | 全系統不動 |
  | 市場資料(預測管線) | `FINMIND_TOKEN`（Sponsor 已續訂 2026-07-12;過期降 free tier,錶=`/user_info`）、`FRED_API_KEY` | sync/audit 死 |
  | 知識抓取①(主題/全文/abstract) | `UNPAYWALL_EMAIL`、`FRASER_API_KEY`、`SEMANTIC_SCHOLAR_API_KEY`（有則提速,無則匿名慢速）、`GITHUB_TOKEN`(如用) | OA 全文/abstract 缺源 |
  | 本機匯入②之 ERP 重抓 | `ORACLE_HOST/…/DSN`（**2026-07-31：抽取工具隨 `~/project/ttai/` 刪除而消失，此五鍵現無對應工具、留存與否待裁**） | ERP 語料**無法重抓**；語料本身安全（`owned_local` item_text **150,772** 列在庫） |
  | 服務層 | `AUGUR_ADMIN_PASSWORD`、`AUGUR_INTERNAL_SECRET` | admin/advisor RBAC 死 |
  | git | `git config user.name/email`(檔內註記) | commit 身分缺 |

  （⚠ **advisor LLM 本機限定 v1.37.0**——不接任何外部 LLM,GEMINI 等 key 即使存在亦不用於 advisor。）
- **SFTP 通道③ 前置（與 .env 同級人工重建;通道選配、缺=僅 SFTP 啞火）**：`~/.config/augur-sftp.json`（host/port/user/**key_path**,chmod 600、絕不存密碼）+ 其引用之 **SSH 私鑰檔**（須搬入本機且遠端重新授權）+ **.env 憑證** `SFTP_<NAME>_USER`/`SFTP_<NAME>_KEYPATH`（件 A2 `acquire_remote_files.py` 讀）。三者不在 git/dump/sync_memory——新機不重建則 SFTP 通道不可用。
- **apk 反組譯前置（#23 OS 層、非 pip、選配）**：`jadx`（skylot/jadx GitHub release 解壓、bin/jadx 入 PATH）+ JRE（如 default-jre）——`scripts/decompile_apk_to_owned.py` 依賴;未裝則該工具 graceful 報錯、不影響其餘。paramiko 已入 pyproject admin extra（`pip install -e '.[admin]'` 自帶）。
- **⚠ owned_local ERP 語料＝dump-only**：erp_tiptop 150,685 段 item_text（最大語料、佔 99%）**唯一換機載具＝DB dump**——augur repo 內無 Oracle 連接器（抽取屬外部 TTAI 工具）,dump 遺失＋原機不在＝**此語料不可復原**。dump 備份＝此語料唯一保命符。
- **向量庫**：生產 SSOT = **pgvector（在 DB dump 內、跟著 DB 走）**;Qdrant serving（`~/qdrant_augur`,augur-qdrant.service,2026-07-14 上線）= **可拋棄、`export_qdrant_index.py` 從 PG 全量重建、不需跨機搬**;舊 `~/qdrant_local`（194MB 休眠驗證產物）同可重建。
- **build 產物**（可重生勿 commit):`models_artifacts/`（.joblib、train_ranker 重生）、`data/`、`/models/`。⚠ `.gitignore` 模型輸出規則錨定 `/models/`（根限定）——**勿改回 `models/`**（會遞迴誤傷 `src/augur/models/` 源）。

## 4. 現況 STATE（取代式：每次封存點整段重寫；歷史＝`git log -p HANDOFF.md`）

> 更新於 **2026-07-30**（機械軌事實對齊：§4.0 三軸自進化列改實態、新增 §4.0b「07-27～07-30 落地」、§4.2／§4.5 arena 由「待開賽」改常態運轉）、最新封存 tag `archive-20260730-net8-tail-closed`；最新 tag 一律 `git tag -l 'archive-*' | tail -3` 實查。**上一次整段重寫＝2026-07-23**（lint P1–P3＋執行指令矩陣入憲封存、tag `archive-20260723-lint-p1p3-cmd-matrix`）——**本區下方各列之日期即其各自時效，勿以本行日期當全區時效**。
> **紀律：本區每個宣稱都可能過期——待辦一律先跑附帶的驗證指令實查（#15），勿直接信。**

### 4.0 近程優先（2026-07-24 Steward 拍板）

> **要強化預測：力氣留在 PME（哲學↔市場）＋資料地基。**（優先序／範圍決策；**API 仍凍**——庫內可做 ≠ 解凍）

| | |
|---|---|
| **做** | **PME**（哲學↔市場進化閉環）強化預測；**資料地基庫內段**（catalog `db_only`、Dividend／attestation 唯讀親驗——已跑 2026-07-24；見下） |
| **prodset→熱路徑** | ✅ **S1–S3 CLOSED＋U-P2H DONE**（2026-07-24；Steward「開 prodset 熱路徑」＋「開 U-P2H」＝`P2H-E123`＋FC-empty＋FZ-keep；`audits/P2H-S123-CLOSED-20260724.md`＋`audits/P2H-ULTRACODE-20260724.md`；拍板＝`audits/P2H-PLAN-APPROVED-20260724.md`）——**G-PME-HOTPATH=none**；active n=2 誠實極窄；零 API／庫內 as-of；**≠**可交易／確立級。**再晉升 run6 後重訓**：`audits/PME-REPROMOTE-RETRAIN-20260724.md`（n_feats=2／rows=12034 穩定、無擴大）。**並行庫內 n=2 訓練／dry-run 預測已跑**（2026-07-24；`audits/DB-PREDICT-N2-PARALLEL-20260724.md`；同 model_id、無擴大） |
| **擴大假說／map 覆蓋** | ✅ **MAP-E012 CLOSED**（2026-07-24；`MAP-P-yes`＋`MAP-E012`＋`FZ-keep`＋`GATE-keep`；拍板＝`audits/PME-MAP-EXPAND-PLAN-APPROVED-20260724.md`；執行＝`audits/PME-MAP-E012-CLOSED-20260724.md`）——S0 診斷＋S1 新 map×16＋S2 `roe`／`debt_ratio`；mapped 17→35；**未**跑 S3／S4；deferred＝`margin_usage_ratio`／peg／F-Score／macro；**≠**解凍／≠放寬閘／≠可交易；計畫＝`reports/augur_pme_expand_hypothesis_map_coverage_plan_20260724.md` |
| **預測↔API** | **[I]** Steward 正式定義：所有預測與 FinMind／FRED **無關**——庫內已落地 raw／features／panel 即可 as-of 切分／訓練／推估；**凍結仍凍取數**，**預測拍板／執行／code 不因凍結否決**；過去因 API 不能拍板之**預測**文件可追溯 **yes**；**同日 code 效力**＝預測程式不得以 live API 為硬前提（見 code 補正）。仍守 #1／#8。rule＝`.cursor/rules/predict-vs-market-api.mdc`；裁決＝`audits/PREDICT-ORTHOGONAL-API-RULING-20260724.md`；追溯總表＝`audits/PREDICT-ORTHOGONAL-RETROACTIVE-APPROVALS-20260724.md`；code 補正＝`audits/PREDICT-ORTHOGONAL-CODE-REMEDIATION-20260724.md`；交叉＝`finmind-fred-api-freeze`／`soul-vs-raw-correlation`（**預測 ≠ 解凍**；**未改** [N]） |
| **追溯 yes 邊界** | **yes**＝庫內 plan／實作／驗收；**仍否**＝放量 sync、解凍取數、假稱洞已補、Dividend 已滿、可交易／確立級（除非原閘已過）；Dividend／FRED 新 series／attestation heal 等 **仍 API 門** |
| **PME 靈魂措辭** | ✅ **G-PME-SOUL=none**（2026-07-24；`SOUL-PME-B-yes`＋採納並寫入；`audits/G-PME-SOUL-CLOSED-20260724.md`）——適用**新入 know-how**（新哲學／新研發技術／新學術論文等）閘後有界自動晉升；**自動下單仍禁**；**與 FinMind／FRED 正交（≠解凍）** |
| **靈魂↔raw 邊界** | **[I]** raw＝觀測／結果呈現——**不**因「有 raw」升格靈魂；升到靈魂層的是 raw **交互**抽象出的**概念**與可證偽關係（相關係數等＝概念載體）。管線仍 source-pure raw→features；靈魂指導假說、不加權 runtime；禁整庫 raw 灌靈魂。API＝取 raw 通道≠靈魂。rule＝`.cursor/rules/soul-vs-raw-correlation.mdc`；留痕＝`audits/SOUL-VS-RAW-CORRELATION-20260724.md`（**未改** META-CONSTITUTION [N]） |
| **FT-COV 近程** | ✅ **DASH＋EMBED CLOSED**（2026-07-28；`audits/FT-COV-DASH-EMBED-*`）＋✅ **`HAR-ext`＋`FT-COV-BATCH` CLOSED**（同日；拍板＝`audits/HAR-EXT-APPROVED-20260728.md`；收官＝`audits/HAR-EXT-CLOSED-20260728.md`）＋✅ **EMBED-WAVE3 CLOSED**（2026-07-29；`audits/FT-COV-EMBED-WAVE3-CLOSED-20260729.md`——`build_sentences` +60 句＋zh gap-fill +42 新嵌＋Qdrant sync；殘餘 gap 全 junk）——8 pending 域 P2×3＋有界×50：終態帳↑（每域≈+53 blocked）、全文落地 **4**→句／嵌；**無熔斷**；**FZ-keep**（≠解凍市場 API）；計畫＝`reports/augur_knowledge_fulltext_coverage_plan_20260728.md` |
| **KH-XDOM 近程** | ✅ **S01 CLOSED**（2026-07-28；`KH-XDOM-PLAN`＋`KH-XDOM-S01`＋（當日）`PME-XDOM-NO`＋`FZ-keep`；拍板＝`audits/KH-XDOM-PLAN-APPROVED-20260728.md`；收官＝`audits/KH-XDOM-S01-CLOSED-20260728.md`）——檢索去作答分域閘＋ATA 骨架；孫子×企管探針多標籤命中；**顧問作答 ≠ 進化灌因子**；S2／S3／ATA 外部另碼。**`PME-XDOM-NO` 已由同日稍後 `PME-XDOM-YES` 廢止**（見下） |
| **KH-ATA-SCHED** | ✅ **CLOSED**（2026-07-28；`KH-ATA-SCHED`＋`FZ-keep`；**不含** `KH-ATA-EXEC`）——user timer `augur-ata-advance` 每日 **04:00**、`--apply --limit 200 --stages sentences embed`；日誌 `~/ata_advance.log`；硬禁 approve／activate；拍板／收官＝`audits/KH-ATA-SCHED-*-20260728.md`；停＝`systemctl --user disable --now augur-ata-advance.timer` |
| **KH4 最小 slice** | ✅ **CLOSED**（2026-07-28；`KH4-PLAN`＋`KH4-ANSWER-ORCH`＋`KH4-INGEST-ALL`＋`FZ-keep`＋`NHC-keep`）——新表 `knowledge_kh4_state`＋`kh4.py` 聚合器＋`refresh_kh4_state.py`；local/SFTP item 路徑、topic promote/pipeline 路徑已寫共同狀態；items 檢索綁 `answer_status='eligible'`，`provisional`／`blocked`／`ineligible` 不直入一般回答空間；**未**做全量語意投影器、**未**另建非 item 級 inbox；live DB apply/refresh 待有 `pip`／`psycopg2` 環境後補驗。留痕＝`audits/KH4-PLAN-APPROVED-20260728.md`／`audits/KH4-SLICE-CLOSED-20260728.md`／`reports/augur_kh4_answer_orchestrator_slice_20260728.md` |
| **PME-XDOM 近程** | ✅ **開通＋雙軸 S0／S1＋雙軸 S3**（S01＝2026-07-28；S3＝2026-07-29 Steward「所有 working 開始跑」＝開 `PME-XDOM-S3`／`PME-XDOM-AI-PREDICT-S3`＋GATE／FZ／NHC-keep）——①孫子×企管：`audits/PME-XDOM-SUNZI-MGMT-S01-CLOSED-20260728.md`＋**S3**＝`audits/PME-XDOM-SUNZI-MGMT-S3-CLOSED-20260729.md`；②AI-PREDICT：S01＝`audits/PME-XDOM-AI-PREDICT-S01-CLOSED-20260728.md`＋**S3**＝`audits/PME-XDOM-AI-PREDICT-S3-CLOSED-20260729.md`（共用 **run_id=6**；本軸 map×10 **零雙綠**；本軸未自行 APPLY；active n=1＝`inst_cumflow_position_120d`）；**S4 不建議急開**；ERP dump 不自動灌；≠可交易／≠解凍 |)
| **NHC 近程** | ✅ **S12＋S3 CLOSED**（S12＝2026-07-28；S3＝2026-07-29 Steward「所有 working 開始跑」＝開 `NHC-S3`＋`FZ-keep`；**無** `NHC-CONSTITUTE`）；拍板＝`audits/NHC-PLAN-APPROVED-20260728.md`；收官＝`audits/NHC-S12-CLOSED-20260728.md`＋`audits/NHC-S3-CLOSED-20260729.md`——glossary active=13；`advisor_distill_seed_topic` ooc=30／impossible=16；aggregate 欄 DB-first；A1／C1／L1 結案豁免；A0 禁領域 hardcode；**待** `NHC-CONSTITUTE`；計畫＝`reports/augur_no_hardcode_db_ssot_constitution_plan_20260728.md` |
| **RKI 近程** | ✅ **S01 CLOSED**（2026-07-28；`RKI-PLAN`＋`RKI-SCOPE-ALL-KH`＋`RKI-S01`＋`FZ-keep`＋`NHC-keep`；含同日追加 AI×預測／FP×AI／FP×預測迭代／**AI×太陽能研發**）；拍板＝`audits/RKI-PLAN-APPROVED-20260728.md`；收官＝`audits/RKI-S01-CLOSED-20260728.md`；追加＝`audits/RKI-AI-SOLAR-RD-SEED-20260728.md`；表 `knowhow_interaction_probe` **active=14**；S0＝`reports/augur_rki_s0_inventory_20260728.md`；**待** `RKI-S2`／`RKI-S3`；**`PME-XDOM-AI-PREDICT` 已另拍並 S01 CLOSED**（探針仍≠過閘憑據）；計畫＝`reports/augur_raw_knowhow_interaction_probe_plan_20260728.md` |
| **PME-XDOM-SOLAR 近程** | ✅ **開通＋S1（KH10 橋）**（2026-07-31；`PME-XDOM-SOLAR-go`＋`PME-XDOM-SOLAR-S1`＋`SEED-SIGN-off`＋FZ／GATE／NHC-keep）——school `solar_supply_invest` 追加 principle **124–126**（K1–K3）／map×7；ledger 2／3／9／18 `downstream_ref` 已回寫；腳本＝`scripts/curate_pme_xdom_solar_map.py`；計畫＝`reports/augur_pme_xdom_solar_from_kh10_plan_20260731.md`；拍板／S1＝`audits/PME-XDOM-SOLAR-PLAN-APPROVED-20260731.md`／`PME-XDOM-SOLAR-S1-CLOSED-20260731.md`；**local-gates 正式跑中**；**`PME-APPLY-go` 未開**（禁自動 APPLY）；defer 16／19–23 **不進**本輪 |
| **KNI 近程** | ✅ **S01 CLOSED**（2026-07-28；`KNI-PLAN`＋`KNI-S01`＋`RKI-keep`＋`NHC-keep`＋`FZ-keep`）——同表擴 `arity`／`axes[]`；升格 `RKI-FP-AI-SOLAR` **arity=3**；二元 13 列保留；**待另令** `KNI-S2`／`KNI-S3`；≠`PME-XDOM-SOLAR`；拍板＝`audits/KNI-PLAN-APPROVED-20260728.md`；收官＝`audits/KNI-S01-CLOSED-20260728.md`；計畫＝`reports/augur_knowhow_nary_interaction_plan_20260728.md` |
| **ADM-AI-ASSIST 近程** | ✅ **S01＋S2＋S3 CLOSED**（2026-07-28／29；`ADM-AI-ASSIST-PLAN`＋`FZ-keep`）——schema **選項 C**；有界 `--apply` 寫 assist＋`action=assist` audit（approval 零變）；`/gov` 唯讀建議列；timer `augur-admission-assist` 每日 **05:00 預設 dry-run**（apply 須 `--with-assist-apply`／`ADM_ASSIST_APPLY=1`）；**硬禁** AI／timer approve／activate；拍板＝`audits/ADM-AI-ASSIST-PLAN-APPROVED-20260728.md`；收官＝`audits/ADM-AI-ASSIST-S01-CLOSED-20260728.md`／`S2-CLOSED-20260729.md`／`S3-CLOSED-20260729.md`；計畫＝`reports/augur_ai_admission_assist_plan_20260728.md` |
| **IMPORT-QUAL-GATE 近程** | ✅ **S1 CLOSED**（2026-07-28；`IMPORT-QUAL-GATE-PLAN`＋`IMPORT-QUAL-GATE-S1`＋`FZ-keep`）——新表 `knowledge_import_job`／`knowledge_import_qualification`＋verdict/reason 字典 SSOT；`acquire_local_files.py` 已接 job/qualification writer，**dry-run 與真實最小匯入皆落 qualification、無 silent drop**；**未做** `/gov` 面板與 approve／activate；拍板＝`audits/IMPORT-QUAL-GATE-PLAN-APPROVED-20260728.md`；收官＝`audits/IMPORT-QUAL-GATE-S1-CLOSED-20260728.md`；計畫檔名以用戶指定為準，但本工作樹未見該 report，故本輪僅補 audit/HANDOFF 最小留痕 |
| **不做（近程）** | 孫子↔**ERP dump** 自動 map 仍禁；不以顧問／RKI cite 率當 G-PROM 通過；不降閘／不解凍；SUNZI／AI-PREDICT **S3 已 CLOSED**／**S4 未開**；**KNI-S2／S3 未開**；ADM-AI-ASSIST **timer 預設不 apply**（須顯式）；SOLAR **無 `PME-APPLY-go` 不 APPLY**／defer 六筆不灌 |
| **落地盤點** | ✅ **已出**（2026-07-24；`audits/ROADMAP-LANDING-INVENTORY-20260724.md`）——機械近程大致齊；**產品完備＝否**；預測正交 ≠ 解凍 |
| **INV-1「全部落地」** | ✅ **`INV1-LAND-MECH`**（2026-07-24；`audits/ROADMAP-INV1-APPROVED-20260724.md`＋定義檔）——機械近程＋另帳；附 **`INV2-THAW-STILL-REQUIRED`** → **仍凍**（無明示解凍句） |
| **凍結** | FinMind／FRED **仍凍**（前提 (1)＝LAND-MECH 已釘；(2)＝明示解凍**仍缺**；見 §4.4）—**未**解凍；預測熱路徑見上列「預測↔API」 |
| **API 洞另帳** | Dividend resume／全量 `build_catalog`／當日 attestation audit·heal — **解凍＋明示後**；G-CAT-1／G-DIV-1／G-ATTEST／G-HAR／10-14／evaluated_pass=0／R6 S3a 等 **另帳**（LAND-MECH 接受） |
| **庫內證據** | `reports/augur_data_foundation_db_only_20260724.md` · `audits/ROADMAP-DATA-FOUNDATION-DB-ONLY-20260724.md` · tag `archive-20260724-data-foundation-db-only` |
| **三軸自進化** | ✅ **V2 總控生效、執行已開**（**2026-07-30 機械軌取代前述「採納／未開執行」**——原列以 07-26「不執行」為終態，但同日 commit `396944b` 起 go／DDL／新腳本／iteration 四項均已發生；依據＝`audits/V2-ADOPTED-SUNSET-20260726.md`＋commit `396944b`＋本機 live DB 實查）。**①拍板**＝`V2-P-yes`：`reports/augur_self_evolution_master_plan_v2_20260726.md` 為總控／介面契約 **SSOT v2**；TRI-v1（`augur_triple_self_evolution_master_plan_20260726.md`）降**前身史料**、`TRI-P-yes`／`TRI-IFACE-yes` 由 `V2-P-yes` 承接；隨拍 **`V2-ISO-go`＋`V2-HONESTY-go`**（Phase 2 焊死）。**②SUNSET 已入表**：`evolution_prereg_gate` 實查 `V2-SUNSET`／axis=`program`／`status=approved`／`approved_by=hugo`／`criteria_sha=65eda893…`／deadline **2026-10-31**（`preregistered_at` 2026-07-27 15:30、`approved_at` 15:31；note 載 hugo 07-28 認領該 UPDATE 為本人親跑）。**③帳本落地**：`evolution_*` 族實查 **10 表**在庫（`iteration_ledger`／`hypothesis_hint`／`evidence_run`／`coverage_snapshot`／`deferred_work`／`prereg_gate`／`kill_switch`／`production_feature_set`／`apply_log`／`run`）；`evolution_kill_switch〔F6 更正：四列非同一 seed 時點——`tw`／`lai`／`raw` 為 2026-07-27 12:03，**`global` 列早於 v2、set_at 2026-07-24 21:11**〕` 4 列**全 `clear`**（scope `global`／`tw`／`lai`／`raw`；本機 v2 DDL seed 時戳 **2026-07-27 12:03**＝Phase 2／5 於本機 live 生效日）。**④已跑之輪（本機實查）**：TWEVO `tw-20260727-r01` `halted`（`--partial`、不完整之輪不計增益/停損）／`r02`·`r03` `succeeded`／**`tw-20260728-r01` 仍 `running` 且 `closed_at` NULL（07-30 實查——勿逕當「還在跑」，先查行程）**；RAWEVO 僅 `raw-20260727-r01` `succeeded`（其 hint 10 列全 `approved`、`decided_by='hugo(對話拍板)'`）。**⚠ 差異揭露**：commit `396944b` 訊息另載「RAWEVO r01–r03 三輪＋H3 人閘首循環（6 approved／14 rejected）」，**本機 DB 查無該三輪、亦無 6:14 分佈**——DB 不隨 git 跨機（疑落在並行載體 `DESKTOP-8MQPFS8` 之獨立庫），**引用前實查、勿當本機事實**。**⑤SUNSET 續命三條現況**：(a) arena 首批已結算、方向門 clusters 遠不足（見 §4.0b／§4.2）；(b) `evolution_production_feature_set` active **仍＝2**（`inst_cumflow_position_120d`／`lending_fee_rate_mean_20d`；`removed` 7 含 `volume_gini_60d`）→ **未**成長；(c) 尺 07-28 已換（`V2-RUBRIC-go`），新尺 robot 五格全 1.000＝本凍結集無可證格 → **未**達成（見檔頭補註）。**仍否**＝解凍市場 API（§4.4）／自動下單／AI 代簽人閘／挪門柱（放寬一律不許、升嚴唯 `GATE-raise`） |

### 4.0b 2026-07-27～07-30 落地（2026-07-30 新增段：原 §4 停在 07-23／檔頭停在 07-26，此四日成果全未收）

> **性質**：索引段——只列「已落地什麼＋去哪查」，數字一律標明來源（live DB 實查 vs 封存訊息）；細節見所引 `audits/`／`reports/`／commit。

* **arena 已常態運轉**（07-26 起）：見 §4.2（本輪已由「待開賽」改寫）。live 實查（2026-07-30，`direction_arena_prediction`）：**8 隊**、`pred_date` 2026-07-15～07-29 共 **5 個**、**11,440 列**，其中**已結算 4,128 列／已結算 cluster＝2**。
* **重演三軌（REPLAY／META-REPLAY／GRID-A）**：`direction_gate` 實查 `dgate_replay_*` **6 門**——`momentum_20_5`／`mc_bootstrap_5` ＝ **`evaluated_fail`（兩面門終判雙死）**，`own_daily_rolling_5`／`chronos_bolt_small_5`／`moirai2_small_5_5`／`timesfm_25_200m_5` ＝ `approved`；另 `dgate_meta_replay_M1_gbdt`／`B2_ridge` **2 門** `approved`。首讀報告＋11.5y 計分板＋W1 全窗（陣發性）＝commit `954a35a`；三軌全鏈封存＝`2877ce2`（07-29）。
* **FV-GUARD 誠實閘上線**（commit `1ec2438`，07-29）：`feature_values` 之 INSERT/UPDATE/DELETE 須帶 GUC 通行證、TRUNCATE 拒；writer 側已帶證。**live 實查**：`feature_values` 上 `fv_row`＋`fv_stmt` 兩 trigger 在庫且 enabled；`evolution_iteration_ledger`／`raw_evolution_iteration_ledger` 各有 `*_no_delete_row`＋`*_no_truncate`。
* **LANE-GOV 序列化**（commits `5a4e473`→`80102ed`→`90b810b`，07-30）：MCP **每請求** flock（鎖包單次請求、非常駐行程）＋`self_seek` cron 補 flock＋純度鎖開唯一明示例外（`/tmp/augur_llm.lock`）。⚠ 該串含**兩次「未實測即推」之自省在案**（`80102ed` 修 `5a4e473` 之 except 懸空語法破壞）——改共用閘後**先 ast＋selftest 再推**。
* **TIER／P6＋econ 尺陷阱三攔**（commits `995c38b`／`3a9d842`，07-30）：TIER 71 列 backfill＋P6 活化（分佈＝簽核表）；econ 尺三道自攔＝`--until` 釘網格 ＋ panel hash 同尺自證 ＋ `--panels-list` 顯式清單（覆蓋稀疏特徵之同尺比較）。**教訓＝同尺四查**（A/B 前查覆蓋／查網格 hash 自證／查重名／查 falsy 空集；第三度尺陷阱自攔）；另 `e0aa0e8` 修 meta-replay 靜態錨（空 prodset 無 IC＝靜態 None）與 `754e268` 修 `run_ladder(feats=[])` falsy 退回全 canonical 之卡空雷。
* **prodset 促升（lending）**：`audits/PRODSET-LENDING-PROMOTION-20260729.md`＋經濟補證全譜收案（`37a7446`）；**live active 仍＝2**（`inst_cumflow_position_120d`／`lending_fee_rate_mean_20d`）——SUNSET (b) 「active 由 2 成長」**尚未**成立。
* **知識線（LSRS／LSR-INGRESS／KH10／KH7／RKI-S2／NET8）**：`audits/LSRS-S01-CLOSED-20260730.md`＋`LSRS-S23-CLOSED-20260730.md`（S2 embed en 新嵌 **35,584**／zh **1,970**、Qdrant upsert 差＝0；S3 KH4 `eligible` 885→**997**、`provisional` 112→**0**、`admit_depth=3` 508→**396** 且明示「殘留＝永久 non-semantic、誠實不抬」）；`LSR-INGRESS-S01/S2-CLOSED-20260730`；`KH10-AUTO-ADMIT-CONSTITUTED-20260729`＋`KH10-ENABLE-S0-CLOSED-20260730`；`KH7-S1-CLOSED-20260729`；`RKI-S2-CLOSED-20260730`；`ARCHIVE-PUSH-NET8-TAIL-CLOSED-20260730`。
* **治權批次（07-30，一日內多批）**：14:33 逐檔親跑（`ls -1 docs/系統架構大憲章_*.md`／`head -1 docs/*.md`／`head -3 CLAUDE.md`／`grep -m1 'v1\.' constitution/GOVERNANCE-ANNEX.md`）實查現行＝**靈魂 v1.9.0／原則精華 v1.12.0／大憲章 v1.51.0／CLAUDE v1.32／`constitution/GOVERNANCE-ANNEX.md` v1.1**（`403ac97` 原則精華 v1.11.0 中繼 → `4dae4bb` 六包批次〔大憲章 v1.50.0＋靈魂 v1.9.0＋原則精華 v1.12.0＋CLAUDE v1.32＋ANNEX v1.1〕 → `24f020a` 大憲章再升 **v1.51.0**〔二通則入憲〕）。§1／§4.7 表已同步。⚠ **同日多 session 並行改治權檔，版號小時級變動——引用前一律 `ls docs/` 實查，勿抄本行**。
* **兩則誠實更正（07-30，均為他人 commit、此處只登錄）**：①**硬體載具錯置**（`81aedb8`）——**GB10／AI TOP ATOM 該機不存在**（hugo 2026-07-25 宣告、2026-07-27 再確認、2026-07-30 重申）；`GTX 1650 4GB／driver 560.94` 屬**並行第二載體 `DESKTOP-8MQPFS8`**。當家機＝`ops/machines/PC002-S1800.md`（本輪親跑 `hostname`／`lscpu`／`free -h`：`PC002-S1800`、Intel Core i5-10500（6C/12T）、WSL 可見記憶體 11 GiB、`nvidia-smi` **不存在＝無 GPU**）；第二載體＝`ops/machines/DESKTOP-8MQPFS8.md`（AMD Ryzen 5 3600、GTX 1650 4GB）。②**cluster 門檻誤述**（`9a45fca`）——live 確立門實查 `min_clusters` ＝ **250**（`dgate_arena_own_daily_5`／`chronos_5`／`timesfm_5`／`a4_chronos2_5`／`a4_moirai2_5` 及 replay 諸門；`own_stack` 三門＝36），**無任何門為 60**；已結算 cluster=2 → **live 路距 2026-10-31 物理不可達**。⚠ **治權檔三處仍寫「≥60」與凍結值不符＝判準級矛盾，已列呈 Steward 裁，本機械軌不擅改**。
* **全域重讀與排程文件**：`reports/augur_full_reread_facts_20260730.md`（全專案重讀 339 事實入 repo，`794a4ee`）；`reports/augur_open_problems_schedule_20260730.md`（開放問題總表×三批制行程，`561b680`）。
* **深化理解／優化地基（2026-07-30 晚）**：`reports/augur_deep_understanding_optimization_base_20260730.md`——合成治權×兩半×一條路×live 錨×優化槓桿 O1–O5；接續優化先讀此檔再開計畫。
* **EVO-EXEC-20260730 執行開**（同日）：拍板＝`audits/EVO-EXEC-20260730-APPROVED.md`（`W0-go`＋`W1-go`＋`FZ-keep`；**暫緩 W3**）；後補 `S4-eval-set-go`／`KH10-ENABLE-S1`＝`audits/EVO-S4-KH10-S1-APPROVED-20260730.md`（S4 收口＝`S4-EVAL-SET-GO-CLOSED` 採 v2 集 `4e15a143ff4b`；KH10-S1＝`KH10-ENABLE-S1-CLOSED`，人裁 approved **4**／pending 餘）；計畫＝`reports/augur_self_evolution_execution_plan_20260730.md`；進度＝`audits/EVO-EXEC-20260730-PROGRESS.md`。顧問側 KH9-first＋KH0／CJK 已落地；W0 庫內 ERP 檢索 HIT；W1 INTERACT 7×102 ＋孤兒已清；四關長跑中。

### 4.1 一句話現況（2026-07-23；取代前版）

**本封存點**：治權 lint 清冊 P1–P3 落地＋可執行 Python「執行指令矩陣」升格元憲章（§8.1 解釋／RULING-2026-026／AL-2026-029）。

* **P1（桶 B）**：`IDO.*` 權威歸 `AUGUR-ID`；表列 IDO.1–8 入枚舉；selftest G12。
* **P2（桶 A）**：`A`／`T`／`DI`／`DO`／`EO` 可受檢（權威 WM／ONT）；L3 TR 標籤對齊；selftest G13。
* **P3（桶 C）**：L1–L6 CS／C.10「MC [N] 條款覆蓋清單」→ 全層 `wm44_uncited=0`；selftest G14；`report --sync`。
* **驗收（實跑）**：corpus **PASS 7／error 0**；L3／L4 warning **0**；L5 剩 1（既有 `KDI.18` 形態未受檢）。計畫書＝`reports/augur_l3_l4_lint_warning_remediation_plan_20260723.md`。
* **執行指令矩陣**：可執行入口 docstring 補齊 canonical「執行指令矩陣」；CLAUDE.md 從屬改引 **AUGUR-MC v1.4**；MC §0.5 L6／Appendix G 留痕（§8 [N] 本文未動、102 母集不變）。
* **機器**：本機 PC002-S1800（WSL2）；MCP `qwen3:4b` 釘死見前 commit `ac0fa35`。

**仍有效之上一錨（07-17～07-22，細節見 git／舊 STATE）**：arena 8 隊 live；alpha Phase 1 落定；monorepo 治權合併；~~GB10／DESKTOP 環境基準~~ → **雙機環境基準**（2026-07-30 機械軌：Steward 同日宣告 **GB10／AI TOP ATOM 該機不存在**，凡以 GB10 為硬體基線之規劃於現行載體不可照用；現行雙載體＝當家機 `ops/machines/PC002-S1800.md`〔Intel Core i5-10500／**無 GPU**〕＋並行第二載體 `ops/machines/DESKTOP-8MQPFS8.md`〔AMD Ryzen 5 3600／GTX 1650 4GB〕；原字樣以刪除線留史、不抹除）。歷史 STATE 全文＝`git log -p HANDOFF.md`。

### 4.1b 上一大進度日摘要（2026-07-17；保留索引，細節以 git 為準）

**① arena 8 隊 live（A4 波次 07-17 加入）**：07-16 開賽（gate `arena_adm_5305655ad1cd` evaluated_pass ∧ 閘一 approved；cron 三行 22:30/23:10/月初）。**07-17 加 A4 兩隊**（Chronos-2 `chronos2_market_5` + Moirai-2.0 `moirai2_small_5`；dgate_a4 K=2/α=0.025/21 門全序列揭露；hugo TTY approve×2——**憲章 v1.42.0 TTY 閘實證擋 AI 代跑**）。**8 隊全員 live**（4 本地+4 TSFM）；chronos/timesfm 套件已補（uni2ts 降級 numpy/torch、四關驗綠）。review_observation_only tier、確立唯門二（≥60 clusters）。（⚠ 2026-07-30 機械軌註：此「≥60」係 **07-17 當時記載**；**live 門內凍結值實查＝`min_clusters` 250**〔`dgate_arena_own_stack_*` 三門＝36〕，治權檔三處「≥60」與凍結值不符＝**判準級矛盾已呈 Steward 裁**——本註只揭露、**不改數**、亦不代裁。）license 白名單擴 cc-by-nc-4.0（Moirai NC、**商業化前須清算**）。

**② 治權批次（07-17 hugo「全批照案」）**：原則精華 **v1.9.1**／憲章 **v1.46.0**／CLAUDE **v1.29**／README／HANDOFF——live 准入 unfreeze gate(退史料)→arena 前置 G1-G5 機制；判準值零變動。**+平行 meta-憲章體系**（你另一會話：`augur-constitution` AUGUR-MC v1.3 Layer 0 lex superior、5 治權檔已加從屬聲明檔頭、AUD 審計；rebase 整合乾淨）。

**③ TSFM benchmark（鏡射 arXiv:2606.27100）**：台股 top5×10 窗×6 模型——**20 個 DM 檢定零顯著勝隨機漫步**（Chronos-2 最不退化）；「最適合台股點預測=零報酬 RW」。TSFM 正確用途=arena 候選非點預測。報告=`reports/tsfm_taiwan_benchmark_20260717.md`+工具 `scripts/benchmark_tsfm_taiwan.py`。

**④ alpha 提升計畫（07-17 拍板開工）**：`reports/taiwan_alpha_improvement_plan_20260717.md`（三軸 D/P/M、51 項對抗審查、11 拍板點）。**Phase 1 進度**：1-0 P0 診斷 ✅→**§0 驚雷=headline 錨 1.1972 不可再現**→修復鏈（見⑤）；1-1 recipe DDL ✅（trial_ledger +recipe 欄/UNIQUE 8）；1-2 P2 turnover 半和量尺 ✅（headline→1.1302）；1-3 P1 buffer **判死**（雙宇宙判準攔 asof 假象、ledger N=33）；1-4 P4 vol-target **無靶不啟用**（能力清償）；1-5 全鏈刷新 ✅；**1-6~1-9 完成**（opus-4-8 resume；**D2+D3 共 7 候選全滅、無一抵經濟終關**——預診放棄 3〔size/vol 代理〕、死於 IC 3〔x_foreign_streak_60d=iid −2.22 越線但 HAC −1.78 崩線=G8 教科書〕、死於增量 1〔x_limitup_reversal_5d Δ−0.049，帶稀疏宇宙混淆→S1〕；**N 維持 33、headline 1.1302 不動、生產表全淨**）。1-8 D1 前置=純盤點（BS 15 系統性缺季/~2.4–3.1k calls 待授權、去累計 32+2、金融股 60d 分支設計）；1-9 live OOS 承接=草案（排程歸屬+R1–R8 預註冊+**DSR N 陳舊斷鏈發現**）。報告=`reports/alpha_phase1_tail_verdict_20260717.md`；**9 拍板點待 hugo**（重點 C2=DSR 重算涵蓋修 N=32/33 陳舊）。**→ Phase 1 全 9 項落定（1-3/1-4/1-6~1-7 全誠實紅=功能非缺陷）**。

**⑤ 錨修復鏈（hugo A/(a)/(i) 三裁）**：PriceAdj 修復（41 真損傷/175=除息跳點誤標定案）→新錨 **net 1.1302／超額+0.372／HAC-t 6.70／DSR 47.9%**（KPI SSOT=N=32 保守口徑）→`revalidation_baseline` re-freeze→**judgestop 相對式條款**（`deflated_decay_margin=0.10` frozen 取代絕對零線；絕對線在 N=32 下 baseline 自身為負=恆觸發失鑑別力）→verdict state=`deploying_unestablished`。econ_verdict 全程 thin 未變向。**DB dump＝`augur_pgdump_20260718_Fd`（修復後乾淨快照）**；原文另載單檔路徑 `C:\database\augur_pgdump_20260718_Fd.tar`——本機無 `/mnt/d`／未能實查（2026-07-30 機械軌）。**最新 dump 一律以 §3 為單一住所**（#12；此處只留指針、不另宣稱「最新」）。

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

> **⚠ 2026-07-30 機械軌取代（勿與舊句並存）**：本節原以「① 開賽（hugo 拍板時點）」為待辦——**arena 實已於 2026-07-26 開賽**、首批已結算、計分板誠實化並重掛每日出單排程（commits `afef5d7`／`e61eabc`／`9eb3399`），故**開賽步已刪**，改為「常態運轉中＋如何實查」。live 實查（2026-07-30）＝8 隊／5 個 `pred_date`（07-15～07-29）／11,440 列／已結算 4,128 列／**已結算 cluster＝2**。

```bash
# arena 常態運轉中(每日出單 cron + settle_arena_labels + arena_scoreboard)。唯讀查閘:
python scripts/run_arena_daily_pipeline.py --dry-run     # 應印「機械閘一…(開) | 機械閘二…✓(開)」
python scripts/evaluate_arena_admission.py --check arena_adm_5305655ad1cd   # 唯讀預演、應 rc=0
# 排程本身(換機必跑;檔內即單一 SSOT):
bash install_cron.sh                                     # 無參數=唯讀 diff
bash install_services.sh                                 # systemd user 服務棧+timers
```
**出單／結算現況（跑 SQL，勿信本檔數字；本輪係以 `venv/bin/python` ＋ `augur.core.db` 實跑）**：
```sql
-- 隊數/出單日/總列/已結算列/已結算 cluster:
SELECT count(DISTINCT model_key) AS teams, count(DISTINCT pred_date) AS dates, count(*) AS n_rows,
       count(*) FILTER (WHERE y_up IS NOT NULL) AS settled,
       count(DISTINCT pred_date) FILTER (WHERE y_up IS NOT NULL) AS settled_clusters
  FROM direction_arena_prediction;
-- 方向確立唯門二 evaluate;**門檻以門內凍結值為準、一律實查不憑記憶**(治權檔「≥60」與凍結值不符已呈裁):
SELECT gate_id, status, criteria->>'min_clusters' AS min_clusters
  FROM direction_gate WHERE gate_id LIKE 'dgate_arena%' OR gate_id LIKE 'dgate_a4%' ORDER BY gate_id;
```
* **仍待**：治權修訂批次與其餘待拍項見 §4.5；**API 凍結未解**（§4.4）——arena 運轉屬庫內作業，**≠** FinMind／FRED 解凍。

### 4.3 正在跑的東西（殺掉前先看這裡）
| 工作 | 觀察方式 | 存活檢查 |
|---|---|---|
| audit 自癒跑者（nohup 脫離、撐過 session） | `tail -f ~/audit_retry.log` | `pgrep -f daily_maintenance` |
| systemd 六服務＋3 timers（開機自起） | `systemctl --user list-units 'augur-*'` | 端口 curl 序見 memory `restart-systemd-after-edit` |
| audit 續跑/重啟（**腳本已入 repo=`audit_selfheal.sh`**） | `nohup flock -n /tmp/augur_audit.lock bash audit_selfheal.sh >/dev/null 2>&1 &` | 探測先行＋PYTHONUNBUFFERED;log=~/audit_retry.log |

**⚠ 換機注意（2026-07-13）**：舊機的 audit 跑者/watcher **不隨機器遷移**——新機還原 DB 後，audit 對帳狀態已在 DB（dump 含 658,911 列增量、取於尾段對帳中），**新機第一件事＝`bash audit_selfheal.sh` 續跑至綠**（DB-driven resume、冪等快轉已對帳段;新 IP 對 FinMind 反而有利），綠後接 4.2 鏈。嵌入積壓（469,551 句）由新機 03:30 timer 或手動 `systemctl --user start augur-embed-catchup` 補。

### 4.4 紅線（絕不能做）
- ⚠ **操作凍結（2026-07-24；同日收緊＋INV-1 釘義）**：**FinMind／FRED 外部 API 一律不開**，直至（1）**「全部落地」**＝Steward **`INV1-LAND-MECH`**（機械近程完備 ∧ 殘留 partial **另帳**；定義＝`audits/ROADMAP-INV1-FULL-LANDING-DEFINITION-20260724.md`；登錄＝`ROADMAP-INV1-APPROVED`）**之後**，且（2）用戶**明示**解凍（「解凍 FinMind／FRED」等）——**`INV2-THAW-STILL-REQUIRED`**（本輪無明示 → **仍凍**）。含 sync／probe／放量／窄窗／Dividend 重建；**「計畫落地」／近程 R5 DONE／局部階段／LAND-MECH 已拍 ≠ 已解凍**；護欄＝`.cursor/rules/finmind-fred-api-freeze.mdc`（alwaysApply）。允許本地 DB 唯讀／零網路／計畫／免 API pytest／零 API 實作。**預測拍板／庫內 train／predict 不因本凍結否決**（`.cursor/rules/predict-vs-market-api.mdc`；`audits/PREDICT-ORTHOGONAL-API-RULING-20260724.md`）。R5 近程證據：`audits/ROADMAP-R5-S3-STATUS-20260724.md` · `ROADMAP-U5-R5-ULTRACODE-20260724.md`（**禁**確立級／可交易宣稱；`direction_gate.evaluated_pass=0`）。
- ⚠ **`evaluate_arena_admission --evaluate` 是終態寫入**（evaluated_pass/fail 皆不可回改、複核=另立新 gate）——**必先 `--check`（唯讀預演）綠才 evaluate**（07-16 實證:--check 曾因 bug 假紅,預演救了不白燒）。舊「unfreeze gate evaluate」紅線已隨 gate 退史料失效（該 evaluate 實為唯讀 stub）。
- ⚠ **FinMind 類作業（市場補同步／PriceAdj 修復）與 audit 互斥**——同一 IP，audit 跑完才輪它們（#24 IP sustained ban 07-12 實錘）。**本階段兩者皆凍（見上條操作凍結）**。
- ⚠ **PDF 抽取未經 P0 拍板前不啟動**（含 OAPEN 61/skip_pdf 976）——OCR 維持不啟動（P8 原裁定）;IA 掃蕩已完成(491 抓/其餘誠實終態)、勿重複放量。

### 4.5 待人類 vs 待 AI
**待 hugo 拍板**（全部**非阻塞 arena 運轉**——arena 已於 2026-07-26 開賽，見下第 6 項；2026-07-30 機械軌）：
1. **PDF 抽取計畫 P0**＝`reports/knowledge_pdf_extraction_plan_20260712.md`（D2 後續;pypdf+五道機械品質閘 fail-closed;OAPEN 61+skip_pdf 976）
2. ~~短 horizon 模型計畫②~~：**已釐清／結案採納**（2026-07-29 `SH-CAL-yes`＋`SH-CLOSE-yes`＋`FZ-keep`；複核＝`reports/augur_short_horizon_timeliness_clarify_20260729.md`）＋**`SH-ASOF-REFRESH` CLOSED**（M2；as-of=`2026-06-30`；`audits/SH-ASOF-REFRESH-CLOSED-20260729.md`）——**`SH-REVAL`（M3）仍未開**。全能顧問計畫①仍：**hugo 已裁「開賽後 AI 先做時效性複核再拍」**（2026-07-12；早於解凍/擂台,恐部分被超越）——短 horizon 與顧問正交，顧問案另拍
3. ~~舊專案 stock_backend 的平日 16:00 FinMind cron 去留~~ **已裁定（2026-07-13 hugo）：4 條 cron 全部取消**（同 IP 疊加解除；備份=`~/crontab_stock_backend_backup_20260713.txt` 可復原）
4. **件 A 三通道公民化 DDL apply + 源活化**（code 已完成、非阻塞開賽）：`python scripts/migrate_local_admission_ddl.py --apply` ＋ `python scripts/migrate_sftp_sync_ddl.py --apply`（**須 audit 綠 + harvest 靜止後**，#30 dump 期禁 DDL）→ **憲章 v1.48.0 起來源可機械准入／activate**（不必 TTY 逐源；硬閘仍守）→ `systemctl --user restart augur-admin` → `bash install_services.sh --with-refresh`。SFTP/apk 另需 §3 人工前置（`augur-sftp.json`+私鑰 / jadx+JRE）。
5. **R-H 修憲（OCR/ASR 轉錄≠AI + 本機/SFTP 明文豁免）**：v3 提案＝`reports/augur_rh_amendment_transcription_exemption_v3_20260714.md`；T2 CLAUDE #29b 條文（Fable 5 檔位、治權檔）待 hugo 確認後才動筆改治權檔。
6. ~~**arena 開賽 cron 掛載時點**（雙閘已開、機械前置全綠;掛載＝開賽＝hugo 決策）~~ **已完成（2026-07-26 開賽）**：每日出單排程已（重）掛、首批已結算、計分板誠實化——commits `9eb3399`（arena 鐘重啟：每日出單排程＋FZ 有界豁免成文）／`afef5d7`（首批結算＋觀察級覆盤＋計分板誠實化）／`e61eabc`（cron／systemd drop-in／arena 腳本三缺口入 git）；現況實查見 §4.2 SQL（2026-07-30 機械軌）。
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
# 擂台選手/對局: SELECT count(*) FROM direction_arena_candidate; SELECT count(*) FROM direction_arena_prediction;
#                (2026-07-30 機械軌:原註「9 / 0(未開賽)」已過期——arena 07-26 起常態出單;本行只留指令、不附值,值一律跑 §4.2 SQL 實查)
# 三軸自進化:    SELECT axis,iteration_uid,status,opened_at::date,closed_at::date FROM evolution_iteration_ledger ORDER BY opened_at;
#                SELECT iteration_uid,status FROM raw_evolution_iteration_ledger ORDER BY iteration_id;
#                SELECT gate_id,status,approved_by,criteria->>'deadline' AS deadline FROM evolution_prereg_gate;
#                SELECT feature,set_status FROM evolution_production_feature_set ORDER BY set_status,feature;  -- SUNSET(b) 看 active 是否 >2
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
| 判準/憲法 | `docs/系統架構大憲章_v1.54.0.md`＋`docs/原則精華_v1.12.0.md`＋`docs/系統核心思想_v1.10.0.md` |
| 這專案怎麼建的 | `reports/augur_construction_understanding_20260713.md`（**v4** code-verified；20260710＝v3 史料。2026-07-30 機械軌：與 §1 同步） |
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

**續建入口**:讀 §1 治權 + 建構理解 **v4**（2026-07-30 機械軌：與 §1／§4.7 同步） → **§4 現況 STATE**（一句話現況→下一步→紅線→待辦附驗證指令）→ plan-first 實作、實測、誠實記錄。**現況一律實查**（§4 每個宣稱都可能過期,先跑其驗證指令;跨機各自獨立、勿照抄假設 #15）。
