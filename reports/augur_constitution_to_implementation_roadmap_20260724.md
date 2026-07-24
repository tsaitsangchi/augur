# 從憲章到實作落地——端到端路線圖（plan-first）

**日期**：2026-07-24  
**性質**：[I] 計劃報告（規劃類；本輪**零改**任何 [N]、**零實作** code）  
**觸發**：用戶問——「如果要從頭開始做 augur 從憲章到具體實作落地此專案，請先規畫一個計畫來一步一步執行，可以 ultracode 來完善嗎？」  
**命名**：`reports/augur_constitution_to_implementation_roadmap_20260724.md`（CLAUDE #16）  
**必讀錨點（本輪已對照）**：`constitution/GOVERNANCE-MAP.md` · AUGUR-MC **v1.6**（constitution-mcp `layer_status`／`get_clause`）· `ULTRACODE-SCHEDULE.md` · `docs/原則精華_v1.10.0.md` · `HANDOFF.md` · `reports/augur_construction_understanding_20260713.md`（v4；HANDOFF 仍鏈 20260710 作索引，**以較新 v4 為建構理解 SSOT**）· `reports/augur_docs_into_mc_initial_constitution_plan_20260723.md`（案 D）· 既有 ultracode 計畫／呈核（L0–L7 單層＋交互＋ residual omnibus）

---

## 0. 一句結論（給 Steward／父代理）

**不要綠地重寫憲章與管線；以既有 AUGUR-MC v1.6＋L1–L7 蓋章規格為 lex superior，對齊既有 code／DB／12-PHASE 做「規格→機械閘→可驗產物」落地，並用 ultracode 在各階段邊界做對抗完善（計畫本體＋落地驗收），而非當第一天重立憲工具。**

---

## 1. 「從頭」定義：綠地 vs 對齊落地

### 1.1 兩種「從頭」

| 定義 | 含義 | 代價 | 是否誠實面對現況 |
|---|---|---|---|
| **G：綠地（Greenfield）** | 假裝無 L0–L7、無 docs、無 DB／scripts；從空白重寫 META／規格／管線 | 摧毀已蓋章八層、ultracode 投資、live DB／arena／知識層；觸發 §8.6 major／全下層複審；違反 clean-room 精神（原則 #16＝依自身治權重建，**非**否認已有治權） | **否**——史實上 L0–L7 已生效、monorepo 已併倉、code／DB 已承重 |
| **A：對齊落地（Align-and-Land）**（**推薦**） | 「從頭」＝**認知從頭**（依 GOVERNANCE-MAP 讀序）＋**施工從頭**（12-PHASE／換機接續序）＋**缺口從頭**（規格義務→code／DB 機械閘對帳表，逐項閉合） | 保留法律脊椎；工作量落在 gap audit、殘留日曆、產品計畫拍板後實作 | **是**——承認已有憲章／規格／code／DB／工具，禁止事後改稱「最初版 L0」掩蓋並存體系（案 D／E4；見 docs 整合計畫） |

### 1.2 推薦定義句（拍板用）

> 本專案之「從頭開始做 augur」＝**以現行 AUGUR-MC v1.6 與 L1–L7 生效規格為約束脊椎，以 docs 三件套＋CLAUDE 為領域紀律，以既有 repo／DB 為承載事實，依 GOVERNANCE-MAP 讀序與領域大憲章 12-PHASE 逐步對齊落地**；**不是**綠地重立憲、不是把今日狀態假裝成尚未存在之 L0–L7。

### 1.3 為何拒 G、採 A（誠實現況）

| 事實層 | 現況（2026-07-24 對照） |
|---|---|
| L0–L7 | 八層 G5 蓋章；`layer_status`：MC **v1.6**，L1–L7 皆 **mc-version＝v1.6** |
| Ultracode | 單層 L0–L7 呈核＋RULING 定案；交互 3a／3b＋038／039；殘留綁 **2026-10-14** checklist（禁假關） |
| 領域治權 | 靈魂／原則精華 v1.10.0／領域大憲章／CLAUDE 已 §0.5 登錄；GOVERNANCE-MAP＝案 D P1；P2 合規聲明＋P3 #7↔P4.E5（041）已閉 |
| Code／DB | 雙半系統（預測×素養顧問）＋審議引擎已存在；換機／12-PHASE／arena live／大量 scripts 已落地 |
| 入口 | `GOVERNANCE-MAP.md` 回答「先讀哪、義務落哪」；義務查找序禁止雙寫 |

綠地重做＝同時違反比例原則、§0.6 lex superior 投資、以及三敵人中的「自我欺騙」（#15／靈魂）。

---

## 2. 治權讀序與義務落點（施工前脊椎）

依 `constitution/GOVERNANCE-MAP.md`（[I] 導航，不創設義務）：

1. **本地圖** → 10 分鐘知義務落點  
2. **L0** `META-CONSTITUTION.md`（§0.5 對照、§0.6 lex superior／概念層獨立）  
3. **需要正式規格** → `specs/*-SPECIFICATION.md`（先 `layer_status`／constitution-mcp，勿整檔灌入）  
4. **領域產品紀律** → 靈魂 → 原則精華 → 領域大憲章（勿倒讀當元法）  
5. **動手改碼／AI** → `CLAUDE.md`＋`README.md`；換機 → `HANDOFF.md`

**義務查找序（禁止雙寫）**：MC [N] → 生效 Layer 規格 [N] → 領域檔現行義務句 → 地圖／HANDOFF（僅導航）。

**衝突**：下層／領域牴觸 MC 之部分無效（§0.6）；領域之間衝突未裁決前，禁止為「整合」雙寫或上收進 L0（案 D 近程；docs 整合計畫已採納）。

---

## 3. 分階段路線圖（R0–R7）

> 階段碼 **R**＝Roadmap（與領域 **12-PHASE**、治權案 D 之 **P0–P5**、ultracode 之 **Find→…** 區分）。  
> **紀律**：plan-first（領域大憲章第六部／CLAUDE #20）——規劃類須本類報告＋拍板後才實作；純機械落地不另立計畫。每階段結束須過「驗收」才進下一；碰護欄（改 [N]、放量 API、破壞性、真兆最終確認）停手問 Steward。

### 總表

| 階段 | 名稱 | 目標 | 治權對應 | 主要既有工具 | 驗收（可判定） |
|---|---|---|---|---|---|
| **R0** | 認知對齊 | 確認採「對齊落地」；讀序＋現況 STATE 親驗 | GOVERNANCE-MAP；HANDOFF §4；MC §0.5／§0.6 | `read_handoff.py`；constitution-mcp `layer_status`；`python3 -m tools.constitution_lint … report` | ✅ **DONE**（2026-07-24；見 §3.1／§7.1／`audits/ROADMAP-R0-CLOSED-20260724.md`） |
| **R1** | 環境可運作 | 機器／DB／服務可跑，零幻像接線 | 原則 #2／#6／#17；CLAUDE #23／#31；L7 | `resume_project.sh`；`import_database.sh`；`sync_from_github.sh`；import smoke | ✅ **DONE**（2026-07-24；本機 `db.ping()` True／pytest 15；見 §3.2） |
| **R2** | 治權衛生／殘留誠實 | 入口一致；10-14 checklist 明示；不合規假關 | 案 D；RULING-039；WM.44／合規聲明 | constitution-mcp；`constitution_lint`；GOVERNANCE-MAP | ✅ **DONE**（2026-07-24；見 §3.3／`audits/ROADMAP-R2-1014-CHECKLIST-STATUS-20260724.md`） |
| **R3** | 規格→實作 Gap 帳本 | 建立「義務→落點→證據」對帳表 | MC §8.2／§8.3；L4–L7 DEFER／TR；construction §9／§11 | `recall`／`local_research`（[I]）；`deliberate.py`；既有 audits | ✅ **DONE**（2026-07-24；見 §3.4／`reports/augur_roadmap_r3_gap_ledger_20260724.md`） |
| **R4** | 資料地基（12-PHASE 對齊） | raw／對帳／panel 可定案或 live 增量誠實 | 原則 #1／#7／#18；大憲章 PHASE 0–8；arena G1-PIN | `full_market_sync.py`；`daily_maintenance.py`；`audit_selfheal.sh`；reconcile | ✅ **DONE**（2026-07-24；親驗＋db_only＋工單；表級 catalog／Dividend／當日 e2e 仍 partial；見 §3.5／`audits/ROADMAP-R4-CLOSED-20260724.md`） |
| **R5** | 預測半系統落地 | universe→model→econ／arena 可驗 | 原則 #8／#11／#12–15；輸出契約；arena／direction_gate | `build_core_universe.py`；提拔／econ scripts；arena pipeline；DB triggers | ✅ **近程 DONE**（2026-07-24；S1–S3＋U5；計畫 §7 A*；**≠** 確立級／可交易／universe→econ 全綠；見 §3.6） |
| **R6** | 素養／顧問半系統落地 | acquire→promote→全文閘→embed→advisor | 憲章 philosophy；KS；原則 #1；L6 | knowledge 引擎腳本；`export_qdrant_index.py`；advisor／chat／admin 服務 | ✅ **S1＋S2＋U6 DONE**（2026-07-24；「開 R6」＝`R6-E12`＋`HAR-local`＋`FZ-keep`；哨兵綠；U6＝`audits/ROADMAP-U6-R6-ULTRACODE-20260724.md`；**S3a／HAR-ext pending**；≠可答完備／≠全域 harvest；見 §3.7／`ROADMAP-R6-S12-CLOSED`） |
| **R7** | 產品計畫閘＋持續 ultracode | 活躍產品計畫拍板後實作；邊界對抗 | plan-first；ULTRACODE-SCHEDULE；#28 | 既有 product plans；`ultracode-layer`；審議引擎 | ✅ **S1＋S2＋U7 DONE**（2026-07-24；S2 首掛 P-PME；U7＝`audits/ROADMAP-U7-R7-ULTRACODE-20260724.md`；PME **U-PME＋PRODSET＋S4 CLOSED**＋✅ **`PME-Efull-yes`**＝`PME-EFULL-APPROVED-20260724.md`；機械完備≠可交易／≠API 解凍／≠確立級；見 §3.8） |

### 3.1 R0 — 認知對齊（理解軸；ultracode 可完善「本路線圖」）

**步驟**
1. 讀 GOVERNANCE-MAP → MC §0.5／§0.6（mcp 取原文）→ 需要時 specs。  
2. 讀原則精華基石 #1／#8／#15＋解凍／arena 准入句。  
3. 讀 HANDOFF §0／§4 STATE＋construction understanding v4 §0／§9／§11（債與 wiring）。  
4. Steward 拍板：採 **A** 或明示堅持 **G**（本計畫預設否決 G）。

**驗收**：書面拍板句；操作者能指出「義務不住 HANDOFF／不住本路線圖」。

**狀態**：✅ **DONE**（2026-07-24）。Steward 指令「閉合 R0」＝書面〔A〕；近程〔U-defer〕〔S1〕（R0–R3）。親驗證據見 `audits/ROADMAP-R0-CLOSED-20260724.md`。

**Ultracode 插入點 U0**：〔U-defer〕跳過 U0；R3 Gap 帳本完成後再跑 **U3**（高槓桿）。對本路線圖做一轮 Find→Verify→Critic→Synthesize（攻擊：幽靈階段、與 10-14 搶頻寬、把操作參數抬成元法、低估已有 code）。產出 `[I]` 審查附錄或另檔 `audits/…`；**不改本檔 [I] 結論除非 Steward 採納**。

### 3.2 R1 — 環境可運作

**步驟**：依 HANDOFF §2／CLAUDE #31——`.env`（人）→ dump（人）→ `resume_project.sh`／`import_database.sh` → smoke →（可選）服務與 ollama。

**表／程式**：不新產表；讀既有 public schema；工具見總表。

**驗收**：`from augur.core import db; db.ping()`；`pip install -e .` 後 scripts 個別可執行（#29）。

**狀態**：✅ **DONE**（2026-07-24）。Steward 本機：PG 17 online、`db.ping()=True`、AUD-02 pytest **15 passed**、ollama 就緒；其後 superuser 重跑 `migrate_raw_supersede_ddl.py` **全 ✓**（trigger／tombstone 硬化已解消）。親驗證據：`audits/ROADMAP-R1-ENV-STATUS-20260724.md`。

**Ultracode**：通常不需；若換機反覆失敗，用審議引擎對「環境宣稱」做 oracle 裁（本地優先 #28）。

### 3.3 R2 — 治權衛生／殘留誠實

**步驟**
1. 確認案 D 入口（GOVERNANCE-MAP）與 README 導讀一致（執行層文件，另工單）。  
2. 對照 `ULTRACODE-SCHEDULE.md` **2026-10-14 併結 checklist**——逐項「狀態／證據／禁止假關」。  
3. 不合規：開補正計畫，不開「把 docs 併進 META」（案 A／C 近程否決）。

**驗收**：checklist 無勾「結清」除非有 RULING／Evidence；lint PASS 不當作合憲唯一依據（ultracode 鐵律）。

**狀態**：✅ **DONE**（2026-07-24）。Steward「**開 R2**」＝建立 10-14 checklist 誠實狀態表；七項仍 calendar／deferred／observation（**零假關**）。親驗證據：`audits/ROADMAP-R2-1014-CHECKLIST-STATUS-20260724.md` · 閉合留痕 `audits/ROADMAP-R2-CLOSED-20260724.md`。

**Ultracode 插入點 U2**：殘留 omnibus 複核前，對「宣稱已閉」項做幽靈落點抽查（親讀下層條文）。

### 3.4 R3 — 規格→實作 Gap 帳本（落地核心帳）

**步驟**：建帳本（建議欄）：

| 欄 | 說明 |
|---|---|
| `layer` / `clause` | 如 `KS.51`、`L7.16`、原則 #7 |
| `obligation_summary` | 一句義務（引 [N] 代號，不改寫為第二套法律） |
| `claimed_landing` | TR／合規聲明／wiring 表宣稱 |
| `actual_evidence` | path:line／DB 物件／「無」 |
| `gap_class` | none／doc-only／partial／missing／conflict |
| `next` | 機械修正／另立計畫／DEFER 至日曆／Steward |

種子來源：construction v4 §9 wiring＋§11 債；AUD 補正；L7 residual；knowledge DEFER（KDO.*）等。

**驗收**：帳本覆蓋「承重義務」集合（至少：三敵人機械閘、輸出契約、隔離、attestation、owner／app、全文三軌）；每一「已落地」宣稱有親驗證據。

**狀態**：✅ **DONE**（2026-07-24）。Steward「**開 R3**」＝交付 Gap 帳本；承重列齊；G-ATT-1／G-ISO-1 當日親驗為 `none`；predict runtime／L7.16 全矩陣等為 **partial**（不假關）。帳本：`reports/augur_roadmap_r3_gap_ledger_20260724.md`。

**Ultracode U3**：✅ **DONE**（2026-07-24；Steward「**開 U3**」）。對抗報告 `audits/ROADMAP-U3-GAP-LEDGER-ULTRACODE-20260724.md`：F-U3-1 major 帳本錯（G-FT-1「遷移無」已否證）已回寫；G-OUT-2 改 doc-only；G-OUT-1 補 migrate path:line。無新 [N] RULING。

**Ultracode 插入點 U3（高槓桿）**：對 Gap 帳本做對抗——專打幽靈落點與不實「缺 0 條」；方法同 `ULTRACODE-SCHEDULE.md` 共用鐵律。major → 另案 RULING／實作計畫，不在帳本內偷改 [N]。

### 3.5 R4 — 資料地基（對齊 12-PHASE 0–8）

**對映**（領域大憲章第五部；不可跳序）：

| 12-PHASE | 本路線圖動作 | 既有主程式 |
|---|---|---|
| 0–1 | 環境＋infra log | bootstrap／migrate 慣例 |
| 2／2b／3／4 | 名冊／FRED／宇宙引導／全史或增量 sync | `full_market_sync.py`；`daily_maintenance.py` |
| 5 | raw 對帳 | reconcile／`audit_selfheal.sh` |
| 6–8 | raw 核心→feature→最終核心 | universe／features builders；`build_core_universe.py` |

**Live 現況誠實句**（原則精華）：歷史完整性 as-of `2026-05-31` 定案性保留；解凍後 live 增量常態；arena 資料地基 **G1-PIN `2026-06-30`**；確立級數字唯 `direction_gate`（≥60 clusters）。

**驗收**：attestation 以現行哨兵句為準；禁 hand-patch（#12／原則 #7 操作閉合受 AUD-02 閘）。

**狀態**：✅ **DONE**（2026-07-24）。Steward「**開 R4**」＝親驗＋安全最小動作＋帳本／工單更新（≠全量放量修復）。證據：`reports/augur_roadmap_r4_data_foundation_20260724.md` · `audits/ROADMAP-R4-CLOSED-20260724.md`。殘留：**G-CAT-1** 表級 STALE、**G-DIV-1** 重建中（U4：live 表已 rename bak）、**G-ATTEST** 當日 e2e SKIP（史料 id=4 PASS）。

**Ultracode U4**：✅ **DONE**（2026-07-24；Steward「**開 U4（零 API）**」）。對抗報告 `audits/ROADMAP-U4-R4-ULTRACODE-20260724.md`：F-U4-2 major 帳本幽靈（G-DIV-1 live 數字過時）已回寫；db_only／史料 attestation 假綠誤讀路徑＋ IP ban 停手未完整機械化已標。無新 [N] RULING。

### 3.6 R5 — 預測半系統

**步驟**：PHASE 9–11＋arena／econ 終關；守輸出契約 fail-closed（DB trigger）；特徵提拔走方法論關卡（HAC Eff-t，禁裸 iid）；經濟價值≠IC。

**驗收**：`tests/test_philosophy_isolation.py` 綠；direction 產物非 evaluated_pass 不得寫入；arena 雙閘／TTY 紅線依 HANDOFF。

**狀態**：✅ **近程 DONE**（2026-07-24；Steward「先短跑 R5 S3 → 立刻 U5」）。S1＋S2：`audits/ROADMAP-R5-S12-CLOSED-20260724.md`；ping：`ROADMAP-R5-PREDICT-PING-20260724.md`；S3 哨兵：`ROADMAP-R5-S3-STATUS-20260724.md`（A1–A10 PASS；`evaluated_pass=0`）。G-PV-1／G-ISO-2／G-OUT-1→**none**（α／live）。**≠** 路線圖大標「universe→model→econ 全綠」；**≠** 確立級／可交易。計畫：`reports/augur_roadmap_r5_plan_20260724.md`。FinMind／FRED **操作凍結**仍有效（近程 R5 DONE ≠ 解凍）；Dividend API 線 PAUSED。

**Ultracode U5**：✅ **DONE**（2026-07-24）。對抗報告 `audits/ROADMAP-U5-R5-ULTRACODE-20260724.md`：F-U5-1～6（文件幽靈／PV-α 誤讀／範圍膨脹／凍結破口／arena≠direction／計畫 as-of）；**禁**把近程 DONE 讀成可交易。無新 [N] RULING。

### 3.7 R6 — 素養／顧問半系統

**步驟**：knowledge_source→acquire→staging→promote→（license 閘）fetch_fulltext→sentences→embed→advisor；ERP owned_local＝dump-only 保命。

**驗收**：「harvest 完成」＝license 允許終態；非授權＝誠實 `fulltext_blocked`（落點＝`knowledge_fulltext_status`）；顧問本機 LLM（不接外部）。

**Ultracode 插入點 U6**：攻擊「metadata 當可答」、隔離被顧問反向污染、RBAC／role 虛報。

**狀態**：✅ **S1＋S2＋U6 DONE**（2026-07-24）。Steward「**開 R6**」＝`R6-E12`＋`HAR-local`＋`FZ-keep`；「**開 U6**」＝對抗呈核。閉合：`audits/ROADMAP-R6-S12-CLOSED-20260724.md`；U6：`audits/ROADMAP-U6-R6-ULTRACODE-20260724.md`；哨兵＝`scripts/verify_roadmap_r6_s12.py`（A1–A8＋A10 PASS；A9＝U6 本檔補）。計畫：`reports/augur_roadmap_r6_plan_20260724.md`。FinMind／FRED **FZ-keep**；Dividend PAUSED；G-FT-1／G-ISO-1＝**none**；G-KDO-1＝calendar（**未假關**）；**G-HAR-1＝partial**（UI 完成詞／庫存 pending）。**S3a／HAR-ext 未開**；≠可答完備／≠全域 harvest 完成／≠產品全量 R6。

### 3.8 R7 — 產品閘＋持續 ultracode

**活躍產品計畫（HANDOFF 索引，皆待拍板）**示例：全能顧問 E2E、短 horizon 誠實模型、alpha 後續、omniscient 等——**各須獨立 plan-first**，本路線圖只規定閘：

1. 計畫完整性：表 schema＋python 規畫（v1.39.0）。  
2. 執行前確認四判準（完整／一致／與現況一致／可實作）。  
3. 階段邊界跑 ultracode 或審議引擎（機械可驗優先本地）。  
4. major／治權判準變更 → Steward；不假關 10-14 項。

**獨立計畫已拍板＋近程執行已開（R7 候選，不取代本節產品全貌）**：哲學↔市場進化閉環＝`reports/augur_philosophy_market_evolution_loop_plan_20260724.md`（✅ `PME-P-yes`＋`PME-AUTO-B`＋`PME-KILL`＋`FZ-keep`；「**開 PME**」→ E12／E123；✅ **U-PME DONE**＝`audits/PME-ULTRACODE-20260724.md`；✅ **PRODSET 真寫**＝`audits/PME-PRODSET-CLOSED-20260724.md`；✅ **S4 CLOSED**＝`audits/PME-S4-CLOSED-20260724.md`（G-PME-S4=none；≠可交易）；✅ **`PME-Efull-yes`**＝`audits/PME-EFULL-APPROVED-20260724.md`（近程閉環**機械完備**；§3 邊界不可分割；**≠**可交易／≠確立級／≠API 解凍）；✅ **G-PME-SOUL=none**＝`audits/G-PME-SOUL-CLOSED-20260724.md`（靈魂措辭已寫入）；Gap `reports/augur_pme_gap_ledger_20260724.md`）。與 R7 上線政策引用交叉：R7 已綁 `PME-AUTO-B`；**R7 S2 已首掛 P-PME**。

**狀態**：✅ **R7 S1＋S2＋U7 DONE**（2026-07-24）。S1＝「開 R7，只跑 S1」；S2＝「開 R7 S2」→ 首掛 P-PME（閘紀錄 `audits/ROADMAP-R7-GATE-PME-20260724.md`）；U7＝「開 U7」→ `audits/ROADMAP-U7-R7-ULTRACODE-20260724.md`（A9 PASS；G-R7-1 doc-only；幽靈詞已補禁）。四碼 `R7-P-yes`＋`R7-G12`＋`FZ-keep`＋`PME-AUTO-B`；哨兵＝`scripts/verify_roadmap_r7_gate.py`（結構綠≠語義完備）。上線政策**引用 PME-AUTO-B**。**≠** 產品全量出貨；**≠** API 解凍；**≠** 可答完備／確立級可交易；PME ✅ **`PME-Efull-yes`**（機械完備）仍**≠**「可交易完備／預測熱路徑已吃晉升」；靈魂措辭 ✅ **已寫入**（G-PME-SOUL=none）。

**Ultracode 插入點 U7**：各產品計畫拍板前／閘框架宣稱前——攻擊閘幽靈、範圍膨脹、上線政策與 PME 衝突、假關 10-14、凍結破口（見 R7 計畫 §5 U7；✅ **DONE** 2026-07-24）。

---

## 4. Ultracode 如何完善「計畫」與「落地」

### 4.1 角色定位

| 用途 | 說明 |
|---|---|
| **完善計畫** | 对本路線圖與後續子計畫做攻擊者視角：找幽靈階段、過寬驗收、與殘留日曆衝突、把領域操作抬成 L0 |
| **完善落地** | 對 Gap 帳本／合規聲明／「已完備」宣稱做親讀落點；產出 [I] 呈核，處置權在 Steward（§8.1／§8.5／§8.6） |
| **不是** | 綠地重寫憲章的第一步；不是 lint 綠燈的替代豁免；不是自動改 [N] |

### 4.2 方法 SSOT

- 單層／通用骨架：`ULTRACODE-SCHEDULE.md`（Find→Verify→Critic→Synthesize；反駁官預設 refuted=true；幽靈落點必查）。  
- 跨層接縫：`LAYER-SEALING-SCHEDULE.md` 第三階段；先例 `audits/L0-L7-INTERACTION-ULTRACODE-2026-07-23.md`。  
- 本地機械可驗：`scripts/deliberate.py`（#28 本地審議優先於 Claude fan-out）。  
- 參數化：`ultracode-layer`（args=`layer:Lx`）；L0 專屬腳本另冊。

### 4.3 插入點一覽（與 R 階段對齊）

| ID | 時機 | 攻擊焦點 | 產出 |
|---|---|---|---|
| **U0** | R0 後、R3 前 | 本路線圖完整性／可執行性 | `audits/` 或本報告附錄 [I] |
| **U2** | R2／10-14 前 | 假關、殘留狀態謊言 | 呈核；禁改 checklist 為結清 |
| **U3** | R3 Gap 帳本初版後 | 幽靈落點、不實完備 | ✅ DONE 2026-07-24：`audits/ROADMAP-U3-…`；帳本已補正 |
| **U4** | R4 attestation／開賽宣稱前 | 假綠、IP ban 路徑 | ✅ DONE 2026-07-24：`audits/ROADMAP-U4-…`；帳本 G-CAT／G-DIV／G-ATTEST evidence 補正 |
| **U5** | R5 確立級／econ 宣稱前 | Goodhart、洩漏、門柱挪動 | ✅ DONE 2026-07-24：`audits/ROADMAP-U5-R5-ULTRACODE-20260724.md`；近程 R5 DONE≠可交易 |
| **U6** | R6 「可答／完成」宣稱前 | 半套 harvest、隔離破口 | ✅ **DONE**（2026-07-24；`audits/ROADMAP-U6-R6-ULTRACODE-20260724.md`；G-HAR-1 partial；禁可答完備） |
| **U-PME** | PME 真綠 APPLY／閉環宣稱前 | 假綠 APPLY、Goodhart、kill 繞過、隔離、A7 假關、靈魂謊稱、PRODSET 幽靈 | ✅ **DONE**（2026-07-24；`audits/PME-ULTRACODE-20260724.md`；後續 PRODSET 真寫→G-PME-PRODSET=none） |
| **U7** | 各產品計畫拍板前／R7 閘宣稱前 | 閘幽靈、範圍膨脹、上線政策≠PME-AUTO-B、假關、凍結破口 | ✅ **DONE**（2026-07-24；`audits/ROADMAP-U7-R7-ULTRACODE-20260724.md`）；見 `augur_roadmap_r7_plan_20260724.md` §5 U7 |

### 4.4 與既有 ultracode 投資之關係

L0–L7 **單層＋交互＋039 residual** 已大量完成——本路線圖 **不重跑全八層** 作為開工條件；僅在 (a) 規格升版、(b) 新 DEFER 實作閉合、(c) 10-14 復審、(d) Gap 帳本揭露動搖蓋章 時，才對**受影響層**開定向 ultracode。與 `reports/augur_l1_l7_per_layer_ultracode_plan_20260723.md`「循序、勿七層齊發」一致。

---

## 5. 表／程式規劃（計畫完整性）

> 本路線圖為**總綱**；多數階段**不產新表**，而以既有 schema／腳本為承載。子計畫若產表，須另附完整 DDL＋遷移器（領域大憲章 v1.39.0）。

### 5.1 本總綱直接涉及

| 項 | 規劃 |
|---|---|
| **新表 DDL** | **無**（R0–R2／U* 為文件與審查；R3 帳本建議先落 `reports/` Markdown 表；若升格 DB 帳本另開計畫） |
| **既有表（讀／驗收）** | raw API 表；`feature_*`；`core_universe_*`；`direction_*`／arena；`knowledge_*`／`philosophy_*`；infra `pipeline_execution_log`／`data_audit_log`；憲章十表（owner 分離）等——以 live `information_schema`＋construction §9 為準 |
| **結果落點** | 本檔；Gap 帳本建議 `reports/augur_spec_to_code_gap_ledger_<YYYYMMDD>.md`；ultracode 呈核 `audits/`；裁決 `constitution/RULING-*.md`（僅 Steward） |

### 5.2 程式／腳色矩陣（總綱層）

| 角色 | 路徑／入口 | 職責 |
|---|---|---|
| 治權查詢 | `tools/constitution_mcp`（get_clause／layer_status／lint_compliance） | [N] 原文與層況 |
| Lint | `tools/constitution_lint`（report／selftest） | 形式合規；**非**實質合憲唯一依據 |
| 換機編排 | `resume_project.sh`、`import_database.sh`、`sync_from_github.sh`、`sync_memory.py`、`read_handoff.py` | R1；零 Claude usage |
| 資料管線 | `scripts/full_market_sync.py`、`daily_maintenance.py`、`audit_selfheal.sh` | R4 |
| 核心／特徵 | `scripts/build_core_universe.py`、features builders、提拔／econ scripts | R5 |
| 知識 | `acquire_knowledge.py`／`promote_knowledge.py`／`harvest_knowledge.py` 等 | R6 |
| 審議 | `scripts/deliberate.py` | 機械可驗宣稱；U* 後備 |
| 隔離測試 | `tests/test_philosophy_isolation.py` | R5／R6 硬閘 |
| 指令矩陣稽核 | `scripts/check_cmd_matrix.py` | 新入口合規（RULING-2026-026） |

### 5.3 若 R3 帳本日後「表化」（可選子計畫，未授權不開工）

| 表（草案名） | 用途 | 備註 |
|---|---|---|
| `spec_landing_ledger` | 義務→證據→gap_class | 須另 plan＋DDL；附 provenance；禁止當第二套 [N] |

對應 Python（草案）：`scripts/build_spec_landing_ledger.py`（唯讀掃描＋寫 staging）、`scripts/report_spec_landing_gaps.py`（報表）。**本總綱不建立上述表。**

---

## 6. 風險

1. **綠地幻覺**：把「從頭」做成重寫 L0／吞併 docs → SSOT 分裂、觸發 major 全下層複審、與 10-14 殘留搶頻寬（docs 整合計畫風險 1–3 同構）。  
2. **Lint／蓋章＝落地**：形式 PASS 或 G5 蓋章被當成 code／DB 已承載 → 幽靈落點復發（ultracode 緣起）。  
3. **假關日曆項**：OT-5／T-KS-6／T-L6-5／025／029／020 M2 等標「完成」而無 Evidence → 違 039「禁止假關」。  
4. **執行軸誤傷理解軸**：為省 usage 不讀清 as-of／anti-leakage／gate 語義 → 沉默污染下游（#28 裁決句：搞錯會污染 → 歸理解）。  
5. **API／配額**：FinMind sustained 403；Claude limit 中斷半套狀態——須 resume-safe＋見訊號即停（#22／#24／#28）。  
6. **Dump／owned_local**：ERP 語料 dump-only；遺失不可復原（HANDOFF）。  
7. **雙半污染**：顧問／knowledge 回流預測 package → 破隔離命門。

---

## 7. Steward 拍板句（請擇一或組合回覆）

### 7.1 已登錄（2026-07-24；R0 閉合）

Steward 指令「**閉合 R0**」＝以下組合**即書面〔A〕**（路線圖 §7 不要求另立 RULING）：

| 代號 | 決定 | 效力 |
|---|---|---|
| **〔A〕** | 採納「對齊落地」定義；否決綠地重立憲 | R0 驗收核心；授權依 R0→R7 推進，**每階段結束呈核後再開下一** |
| **〔U-defer〕** | 跳過 U0；R3 Gap 帳本後再跑 U3 | ultracode 近程不開 U0 |
| **〔S1〕** | 近程只做 R0–R3 | R4–R7 另案；R0 已 DONE |

**未採納**：〔G〕綠地；〔U-yes〕U0 先行；〔U-no〕；〔S2〕〔S3〕。

**留痕**：`audits/ROADMAP-R0-CLOSED-20260724.md`。

---

**主問題（必選）**——*以下為初稿拍板句；§7.1 為生效登錄。*

- **〔A〕採納本路線圖之「對齊落地」定義**，否決綠地重立憲；授權依 R0→R7 推進，**每階段結束呈核後再開下一**（預設）。  
- **〔G〕堅持綠地**：停止本路線圖；另立「廢止／重建 L0–L7」原則級提案（須 §8.5 Evidence）——**不建議**。

**Ultracode（可選）**

- **〔U-yes〕** 授權先跑 **U0**（攻擊本路線圖）再進 R3；呈核後修訂本報告再施工。  
- **〔U-defer〕** 跳過 U0；R3 Gap 帳本完成後再跑 **U3**（高槓桿）。  
- **〔U-no〕** 本季不開新 ultracode；僅用 lint＋審議引擎＋10-14 checklist。

**近程範圍（可選）**

- **〔S1〕** 只做 R0–R3（認知＋環境＋衛生＋Gap 帳本），產品計畫（R7）另案。  
- **〔S2〕** R0–R5（含資料地基＋預測半系統對齊），顧問半系統 R6 另案。  
- **〔S3〕** 全 R0–R7（須接受較長週期與多份子計畫）。

**明確不授權（本報告預設）**

- 本輪不改 MC／specs／原則精華 [N]；不上收 docs 進 META；不假關 2026-10-14 項；不自行 commit／push。

---

## 8. 產物索引與依賴

| 產物 | 路徑 |
|---|---|
| **本路線圖** | `reports/augur_constitution_to_implementation_roadmap_20260724.md` |
| 治權入口 | `constitution/GOVERNANCE-MAP.md` |
| docs↔MC 近程案 | `reports/augur_docs_into_mc_initial_constitution_plan_20260723.md`（案 D） |
| Ultracode 方法 | `ULTRACODE-SCHEDULE.md` |
| 建構理解 | `reports/augur_construction_understanding_20260713.md` |
| 接續 STATE | `HANDOFF.md` |
| 領域 12-PHASE | `docs/系統架構大憲章_v1.46.0.md` 第五部 |
| 原則 | `docs/原則精華_v1.10.0.md` |

---

## 9. 本輪邊界（誠實）

- ✅ 產出本計劃報告  
- ✅ **R0 閉合**（2026-07-24；§7.1 拍板〔A〕〔U-defer〕〔S1〕；audit 留痕）  
- ✅ **R2 閉合**（2026-07-24；10-14 checklist 誠實狀態表；日曆項仍 open）  
- ✅ **R3／U3 閉合**（2026-07-24；Gap 帳本＋對抗補正）  
- ✅ **R4 閉合**（2026-07-24；資料地基親驗＋db_only＋Dividend 工單；殘留 partial 見帳本）  
- ✅ **U4 閉合**（2026-07-24；零 API 對抗；`audits/ROADMAP-U4-R4-ULTRACODE-20260724.md`）  
- ✅ **R5 計畫已拍板**（2026-07-24；`R5-P-yes`＋`R5-E12`＋`PV-α`＋`PAR`）  
- ✅ **R5 S1＋S2 閉**（2026-07-24；「開 R5」；`audits/ROADMAP-R5-S12-CLOSED-20260724.md`；G-PV-1 none）  
- ✅ **G-ISO-2 live ping → none**（2026-07-24；`audits/ROADMAP-R5-PREDICT-PING-20260724.md`）  
- ✅ **R5 S3＋U5 閉**（2026-07-24；`ROADMAP-R5-S3-STATUS`＋`ROADMAP-U5-R5-ULTRACODE`）→ **近程 R5 DONE**（計畫 §7 A*）  
- ✅ **R6 計畫已拍板**（2026-07-24；`R6-P-yes`＋`R6-E12`＋`HAR-local`＋`FZ-keep`；`audits/ROADMAP-R6-PLAN-APPROVED-20260724.md`）  
- ✅ **R6 S1＋S2 閉**（2026-07-24；「開 R6」；`audits/ROADMAP-R6-S12-CLOSED-20260724.md`；哨兵 `--with-smoke` PASS）  
- ✅ **U6 DONE**（2026-07-24；「開 U6」；`audits/ROADMAP-U6-R6-ULTRACODE-20260724.md`；G-HAR-1 partial）  
- ✅ **哲學↔市場進化閉環：計畫拍板＋E12／E123＋U-PME＋PRODSET＋S4 CLOSED＋`PME-Efull-yes`＋G-PME-SOUL CLOSED**（2026-07-24；四碼；`audits/PME-S012-STATUS`／`PME-E123-STATUS`／`PME-ULTRACODE`／`PME-PRODSET-CLOSED`／`PME-S4-CLOSED-20260724.md`／`PME-EFULL-APPROVED-20260724.md`／`G-PME-SOUL-CLOSED-20260724.md`；Gap `reports/augur_pme_gap_ledger_20260724.md`；G-PME-SOUL=none；G-PME-S4=none；機械完備≠可交易）  
- ✅ **`PME-Efull-yes` 已登錄**（2026-07-24；呈核 `PME-EFULL-REVIEW`＋登錄 `PME-EFULL-APPROVED`；§3 邊界：G-PME-SOUL=none；G-PROM／G-ECON partial；FZ-keep／Dividend PAUSED；evaluated_pass=0；G-R7-1／G-PME-DEMOTE doc-only）  
- ✅ **R7 計畫已拍板**（2026-07-24；`R7-P-yes`＋`R7-G12`＋`FZ-keep`＋`PME-AUTO-B`；`reports/augur_roadmap_r7_plan_20260724.md`；`audits/ROADMAP-R7-PLAN-APPROVED-20260724.md`）  
- ✅ **R7 S1 DONE**（2026-07-24；「開 R7，只跑 S1」；哨兵＋模板；`audits/ROADMAP-R7-S1-CLOSED-20260724.md`）  
- ✅ **R7 S2 DONE**（2026-07-24；「開 R7 S2」；首掛 P-PME；G-P4＋閘 PASS；`audits/ROADMAP-R7-S2-CLOSED-20260724.md`）  
- ✅ **U7 DONE**（2026-07-24；「開 U7」；`audits/ROADMAP-U7-R7-ULTRACODE-20260724.md`；G-R7-1 doc-only；幽靈詞已補禁）  
- ✅ **G-PME-SOUL CLOSED**（2026-07-24；`SOUL-PME-B-yes`＋採納並寫入；靈魂／#20／A.53；MC P5 條文未改；`audits/G-PME-SOUL-CLOSED-20260724.md`）  
- ❌ **未**解凍 FinMind／FRED（FZ-keep）；**未**宣稱確立級／可交易／可答完備；**未**開 HAR-ext／S3a；**未**閉合 universe→econ 全量產品半系統；**`PME-Efull-yes`＝機械完備仍≠對外可交易完備**；**MC [N] 本輪未改**
- ✅ **prodset→預測熱路徑：S123 CLOSED＋U-P2H DONE**（2026-07-24；四碼 `P2H-P-yes`＋`P2H-E123`＋`FC-empty`＋`FZ-keep`；`audits/P2H-PLAN-APPROVED-20260724.md`／`P2H-S123-CLOSED-20260724.md`／`P2H-ULTRACODE-20260724.md`；計畫＝`reports/augur_prodset_predict_hotpath_plan_20260724.md`）—**G-PME-HOTPATH=none**；n_feats=2 誠實極窄；接線≠解凍／≠可交易
- ✅ **預測↔API 正交＋追溯**（2026-07-24；Steward）：庫內切分即可預測；凍結仍凍取數；預測拍板不因凍結否決 — `audits/PREDICT-ORTHOGONAL-API-RULING-20260724.md` · `audits/PREDICT-ORTHOGONAL-RETROACTIVE-APPROVALS-20260724.md`

- ⚠ construction v4 時點為 2026-07-13；HANDOFF STATE 為 2026-07-23——**執行 R3／R4／U4／R5 時已重跑親驗**，不得把舊 wiring 表當永真  

**建議下一句（對齊近程優先 2026-07-24）**：「**資料地基等解凍條件再續**」（取數洞另帳；FZ-keep）——P2H／U-P2H 已閉；**仍禁**把 n_feats=2 說成可交易、**仍禁**他域近程開工、**仍禁** API 未達條件自解凍。

---

*計畫完整性：總綱層表／程式見 §5；子階段產表者另立計畫。30 分鐘可讀目標：§0–§3 總表＋§4 插入點＋§7 拍板句。*
