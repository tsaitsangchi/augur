# augur-code 憲章化移轉暨擴張計畫書 [I]（v0.1-draft，提交 Steward）

* **性質**：[I] 計畫書（不創設義務；一切 apply／併 main／充任屬 Steward，`AUGUR-MC v1.3 §8.1`／P5.W2）。依 augur-code CLAUDE.md #20（計畫先行）與大憲章「計畫完整性」紀律（附 DDL＋python 程式規畫）作成。
* **目標**：把活的台股系統（tsaitsangchi/augur）**逐步移轉到元憲章治理之下**，並使**一切後續擴張自動生於憲章之內**——不推倒重來、不讓 F1 遺產定義未來。
* **法源與素材**：`AUGUR-MC v1.3` 五原則；`AUGUR-WM/ONT/ID/KS v1.0` 生效規格；`GROUNDING-MAP.md`（44 條物理義務對映）；`CONSTITUTIONAL-ROLLOUT-PLAN.md` 軌道 B/C 與 strangler-fig 三接縫；合憲審計（critical 3／major 11／minor 12，54 亮點）。
* **快照日**：2026-07-18。數字紀律：凡數字附產生指令；未驗者明標。
* ✅ **審查狀態**：本計畫書已經對抗審查（2026-07-18，wf_91983484-608，go=false→8 issues 全採納）：修訂 owner 分離斷線風險（major）、Phase 5/1 閘機器可判性、新增 Phase 8 誠實揭露 AUD-09/21 等未涵蓋發現、亮點不可動區改非閉集聲明。事實基線經審查官親驗（250 表/十表零列/37 檔/420 verdict/247 表 owner 皆命中）。

---

## 〇、現況基線（本計畫的起點，已實測）

| 項 | 狀態 | 證據 |
|---|---|---|
| 結構層 | ✅ **十張憲章表已 apply 生產**（250 表、18 護欄 trigger、SECURITY DEFINER×2、predict 隔離全拒） | GROUNDING-MAP §四步 5（commit aa8bb61）；`psql -d augur -tAc "SELECT count(*) FROM information_schema.tables WHERE table_schema='public'"` → 250 |
| 行為層 | ⬜ 新表**全零列**——code 未接線（heal 快照 code 在分支未併 main；mint/action_log 零呼叫端） | 各表 `SELECT count(*)` → 0 |
| 規格層 | L0–L6 生效；L7 修復中（D1–D6）；#22 標籤更正中（RULING-2026-010） | AL-2026-001…013 |
| 治權檔 | 檔頭從屬聲明✓；完整合規聲明**未作**（期限 2026-10-14） | RULING-2026-002 主文二 |
| 沙盒 | ✅ augur_sandbox（55GB 複本＋十表）＝常設驗證閘 | build_sandbox [4/4] |
| 節拍器 | ✅ 已實證之移轉節拍：**沙盒實測 → P5 拍板 → 生產 apply → 唯讀驗證** | 2026-07-18 首輪全程走通 |
| 未涵蓋發現 | ⚠️ AUD-09/21（MAJOR）＋多項 minor 前七期未涵蓋——列 **Phase 8**（誠實揭露、不沉默） | 審查官親驗；REMEDIATION-ROADMAP 第二波 |

## 一、移轉原則（自憲章導出，全程不變）

1. **strangler-fig，不推倒**（WM.10）：raw 鏡像層＝合法且必要的 Observation Store，「必須建立於其上、不得取而代之」。病灶只在「vendor 表即世界模型、下游直綁」。
2. **三接縫絞殺**（ROLLOUT-PLAN §4.1）：①World Model 投影（WM.36 registry）②Identity registry（mint-on-admission）③Confidence 語義層（KS L_C）。消費者逐檔改繫、**一次一檔、雙讀影子比對 diff 零方切、任一非零即熔斷回退**。
3. **亮點不可動區**（**首要 7 項具名；完整清單以審計報告第三節 54 亮點原文為權威**，本處非閉集）：verify_claim 唯一寫點（⚠️ 見下 AUD-17：目前僅 app 層紀律、DB 未 trigger 強制）、admission 四件閘、TTY 唯人閘、guard 閉集、fred_series vintage、review_log append-only、「不下單不動錢」。**改壞任何一項（含未具名之其餘 47 項）＝拆掉憲章在此系統中已有的落地。**
4. **每步一節拍**：沙盒實測→P5 拍板→生產 apply→唯讀驗證→記錄 push。行為驗證一律在沙盒（生產側破壞性測試禁止）。
5. **擴張一律 greenfield 合憲**（軌道 C）：新 dataset／新市場／新能力 spec-first——先過 WM.35（落地即整合：世界概念映射登錄，unmapped 得存不得消費）、繫 ONT 型別、mint identifier，**永不再走 raw 直綁老路**。
6. **誠實邊界**：每期完成判準機器可判；不可落地者（owner 分離前的 trigger 極限、單人、無 GPU）明標不掩蓋。

## 二、分期計畫

> 節奏標記：⚡週級｜🪨月級。每期附【閘】（機器可判完成判準）與【DDL/程式規畫】（計畫完整性）。

### Phase 0 — 結構層落地 ✅（2026-07-18 已完成）
十表＋trigger＋REVOKE apply 生產；15/15 行為測試（沙盒）。**本計畫其餘各期皆立於此。**

### Phase 1 — code 部署與 P4.E5 行為生效 ⚡（最高優先：讓已 apply 的表開始工作）
**內容**：(a) `remediation/impl-2026-07-17`＋PR #2 測試檔經 Steward #19 檢視後**併 main**；(b) 生產執行環境切至含快照 gate 之 code（daily_maintenance heal 自此透傳 `snapshot_reason` → raw_supersede_log 開始收衝突留痕）；(c) `setup_predict_role --apply --confirm`（人工跑，分類器擋 AI）；(d) **owner 分離**：建 `augur_app` 應用角色、十張憲章表 owner 改隸 `augur_owner`（或 postgres），應用連線不再用 owner 身分——補上「trigger 擋不住 owner」的最後一塊。
**【閘】**：下次 heal 遇 value_mismatch 後 `SELECT count(*) FROM raw_supersede_log` > 0 且 old_row/new_row 並存；`SELECT tableowner FROM pg_tables WHERE tablename='raw_supersede_log'` ≠ 應用角色；**且以應用角色（augur_app）實測對十表最小 INSERT/SELECT 成功**（沙盒——否則 owner 已改而應用斷寫之失敗態會被漏判）。
**【規畫】**（親驗現況：全 247 表 owner＝augur、應用即以 `DB_USER=augur` 連線，`augur_owner`／`augur_app` 角色尚不存在——直接改 owner 會使應用喪失 owner 隱含權限而斷寫）：(a) `CREATE ROLE augur_owner NOLOGIN`＋`CREATE ROLE augur_app LOGIN`；(b) 十張憲章表 `ALTER TABLE … OWNER TO augur_owner`＋逐表 `GRANT INSERT/SELECT`（憲章表禁 UPDATE/DELETE，由 trigger 兜底；serving 例外許 superseded_by）予 augur_app；(c) **其餘 237 張應用需用表之 GRANT 盤點**（現靠 owner 隱含權限，切角色後須顯式 GRANT）；(d) 應用連線角色切換：`.env` `DB_USER=augur→augur_app`、`config.DB_PARAMS`、systemd 服務重啟（CLAUDE #7）；(e) **沙盒實跑一次 heal 寫 raw_supersede_log＋mint 寫 entity_registry，驗權限鏈完整**方得生產。⚠️ 本子項為 major 風險（斷線），須整包沙盒驗證後 P5 拍板。**〔2026-07-18 沙盒實測已完成 7/7 ✅（十表 ACL 10/10、heal/mint 真實寫入、augur_app 與原 owner augur 之 UPDATE/DELETE/ALTER/DISABLE TRIGGER 全拒）——施工包 ops/phase1/（施工 SQL＋回退 SQL＋P5 呈核單），待 P5 拍板即可生產施作。〕**
**〔2026-07-18 P5 已准、生產施作完畢 ✅：備份 10.04GB＋還原實測 5/5 吻合→手術→閘 A 全綠（十表 owner=augur_owner、augur_app 可寫、augur DELETE 42501 拒、資料零觸動）→augur_app 登入實測成功。殘餘＝hugo 側 .env 切換＋服務重啟（Steward 側，過渡橋零斷線）。執行記錄 ops/phase1/EXECUTION-RECORD-2026-07-18.md。〕**

### Phase 2 — Identity 接縫：mint-on-admission ＋ 存量鑄造 🪨（AUD-04/05/06/07 行為面；ID.11 義務結清）
**內容**：(a) `ingestion/ingest.py::store` 准入點接 `resolve_or_mint`（外部碼→entity_alias→augur_id；查無→mint＋alias 登錄；`detect_code_reuse` 紅旗→provisional 不縫合）；(b) **存量鑄造 backfill**：對現有名冊實體一次性 mint（Security ≈3,114、Index、FredSeries——數量以 `core_gate` 名冊實跑為準，勿轉抄）；(c) TaiwanStockInfo 屬性快照開始寫 `entity_attribute_version`（daily sync 差異偵測 → SCD-2 append），`core_gate` 產業判定改讀 as-of（AUD-07 解）；(d) 下市事件消費：TaiwanStockDelisting → `identity_lifecycle_event(retire)`（AUD-05 解）。
**【閘】**：`SELECT count(*) FROM entity_registry` ≈ 名冊實體數；`SELECT count(*) FROM entity_alias WHERE alias_status='provisional'` 之解析存量指標可查（ID.51）；code-reuse 紅旗測試（沙盒重演歷史重用案例）通過；`core_gate --selftest` as-of 模式綠。
**【規畫】**：python——`src/augur/identity/resolve.py`（新，resolve_or_mint 入口）、`scripts/backfill_entity_registry.py`（新，冪等、分批、記 mint evidence=名冊來源列）、`scripts/sync_attribute_versions.py`（新或併入 daily_maintenance）；ingest.py/store 增一參數化 hook（比照 snapshot_reason gate 模式：預設不動、逐通道開啟）。DDL：無新表（六表已 apply）。

### Phase 3 — 行動六元組接線 ⚡（AUD-10/11 行為面）
**內容**：(a) `authorization_grant` 首批登錄：把 shell 註解中的既有拍板（FINMIND_MIN_INTERVAL 0.7、heal 放量等「hugo YYYY-MM-DD 拍板」）遷入結構化授權（**內容照錄、Steward 簽核**）；(b) watchdog／selfheal／daily_maintenance 之 kill、relaunch、放量重抓改經 `action_log.log_action`（六元組：actor＝服務 identity、authorization_ref、expected/observed_effect）；家目錄純文字 log 降為人讀副本；(c) watchdog 判態改讀 attestation_result 表（AUD-11 建議）。
**【閘】**：一輪 selfheal 後 `SELECT count(*) FROM automation_action_log` > 0 且每列 authorization_ref 非 NULL（或依 Steward 對升裁決 C 之裁定）；log 檔刪除實驗（沙盒）不再誤觸 relaunch。
**【規畫】**：python——audit_selfheal.sh/audit_watchdog.sh 加 psql 寫入段或改呼叫 python helper；`scripts/seed_authorization_grants.py`（新，一次性遷移＋TTY 人核）。

### Phase 4 — Serving append-only 消費切換 ⚡（AUD-08 行為面）
**內容**：(a) `predict_asof.py::predict` 出單時**同交易** append `prediction_serving_log`（含 run_id/git_sha）；(b) 建 `prediction_current` 視圖（serving_log 之 superseded_by IS NULL 面）；(c) advisor payload 與風控 `_deployed_dd_returns` 改讀視圖；(d) 穩定一個驗證週期後，prediction_values 之 DELETE+INSERT 路徑退役（改 append＋標記）——**屬破壞性改動（現 1695 列活資料），另立獨立提案經 §8.2/P5.W2 治理程序，非本計畫任一 Phase；此處僅預告，不排入本計畫排程**。
**【閘】**：出單一次後 serving_log 有列且 `--rewrite-all` 重跑時舊列 superseded_by 被標記而非消失；advisor 回歸金題集綠。
**【規畫】**：python——predict_asof.py 出單段＋10 行；`CREATE VIEW prediction_current AS SELECT … WHERE superseded_by IS NULL`（DDL 一支，入 migrate 腳本）。

### Phase 5 — Confidence L_C 落地 🪨（AUD-03 行為面；KS §4/Annex CM）
**內容**：(a) DDL：`CREATE TYPE lc_confidence AS ENUM ('INSUF','LOW','MODERATE','STRONG','DETERMINISTIC')`＋`deliberation_verdict` 加 confidence 欄＋`lc_mapping` 登錄表（CM.1(a) 十一列官方映射：oracle confirmed→DETERMINISTIC、校準機率→banding、green/amber/red→…）；(b) verify_claim 附掛 confidence（唯一寫點原則不變——只擴欄不改寫點）；(c) 消費保守規則：無 Confidence＝INSUF、不得升信（KS.38）；identity_claim.confidence_level 開始填值。
**【閘】**（親驗現有 420 列既有裁決，ADD COLUMN 後恆 NULL）：`SELECT count(*) FROM deliberation_verdict WHERE confidence IS NULL AND verdict<>'undecidable' AND verdict_id > :部署基準`（**須加序號/時間界方為機器可判**，否則既有 420 列使查詢永不趨零）趨零；lc_mapping 與 KS Annex CM 逐列相符（gate 或人工對照）。
**【規畫】**：DDL 一支 `migrate_lc_confidence_ddl.py`（ENUM＋兩 ALTER＋lc_mapping 表＋seed 十一列）；python——verifiers.py verify_claim 擴一參數（預設值依 oracle 種類）。

### Phase 6 — World Concept Registry ＋ 37 檔直綁絞殺 🪨🪨（AUD-01 根治；最大工程量）
**內容**：(a) DDL：`world_concept_registry`（WM.36 七欄：世界概念｜歸類閉集｜通道映射至欄位級｜權威表徵指定｜時間屬性雙宣告｜provenance｜定案性）＋首批條目自 Annex F 六條啟動、對齊 dataset_catalog；(b) `src/augur/core/registry.py` 解析 API（概念→表.欄）；(c) **37 檔逐檔絞殺**（`grep -rlE 'FROM\s+"Taiwan' src scripts --include='*.py'` 現值 37）：每檔改經 registry 解析、**雙讀影子比對**（舊直綁 vs 新解析，diff 零才切、非零熔斷回退）；順序：低風險 audit/scripts 先、feature/panel 次、advisor/predict 最後；(d) 新增 dataset 自此**強制**過 WM.35（落地即整合 hook：無概念映射→unmapped 登錄、消費閘拒）。
**【閘】**：直綁計數逐週遞減至 0（同 grep）；每檔切換附影子比對報告；unmapped 存量可查（WM.35 指標）。
**【規畫】**：DDL 一支；python——registry.py（新）、`scripts/shadow_compare.py`（新，通用雙讀比對器）、逐檔 PR（一檔一 commit、#19 逐支過目）。

### Phase 7 — 治權收尾 ⚡（期限 2026-10-14）
五份治權檔完整合規聲明（AUGUR-WM §11 格式＋WM.44 逐條矩陣，工具：constitution_lint 綠）；原則精華 #7 條文改「新版本入庫、舊版標 superseded」（**Steward 拍板後**與 Phase 1 部署對齊）；審計報告終局定案（§8.2）。

### Phase 8 — 二/三波審計發現（誠實揭露：本計畫前七期未涵蓋者）🪨

審查官親驗指出：審計 26 發現中，下列未被 Phase 0–7 任何期涵蓋。**在此明列而非沉默**（審計 REMEDIATION-ROADMAP 將 AUD-09/21 與已涵蓋之 AUD-08 同列第二波，計畫不得只做孿生之一）：

* **AUD-09（MAJOR）**：core_gate `build_universe`/`build_universe_asof` 之 `DELETE FROM` 與 `catalog/__init__.py` `DELETE FROM column_catalog`——衍生 Knowledge 全量重建無 superseded（違 P4.E3）。親驗 core_universe_asof 776 檔活資料、column_catalog 活表、DELETE 路徑仍在。**處置**：版本化 append＋superseded 標記（比照 Phase 4 之 serving 模式）。排入本期。
* **AUD-21（MAJOR）**：`framework.py` seed 對齊路徑 `UPDATE philosophy_principle SET hypothesis`／`UPDATE principle_factor_map SET direction`——supersede 三要件零履行（違 P4.E3）。**處置**：比照 curation.py review_log 模式（審計指定範式）。排入本期。
* **AUD-17（minor）**：verify_claim 唯一寫點僅 app 層紀律、DB 無 trigger 阻旁路寫 confirmed。**處置**：加 BEFORE UPDATE trigger（status→confirmed 須存在對應 is_deterministic verdict），比照 direction_gate trigger 範式。—— ⚠️ 此為 §一原則 3「亮點不可動區」中 verify_claim 之**已知殘餘**，不得呈現為已完成之保證。
* **AUD-16**（claim 結構化指涉＋verdict confidence 結構欄）、**AUD-20**（ON DELETE CASCADE 物理消滅 identifier/Evidence → RESTRICT＋隔離標記）、**AUD-22**（chat 硬刪除→tombstone）、**AUD-23**（P5.E2 行動風險分級表）、**AUD-24**（admin env 後門歸責）、**AUD-14/15/18/19**（除權息表徵／catalog 世界概念欄／per-pick 解釋／通識標記機械前置）——各為 minor，處置方向見審計第四節；**本計畫排入 Phase 8 或明示延後**，均不沉默。

**【閘】**：每項附審計條款與可判定測試（同各 AUD 補正方向之驗收）；Phase 8 得與擴張軌並行，非關鍵路徑。

### 擴張軌（與 Phase 2+ 並行，永續）

**原則：一切新增生於憲章之內。**
1. **新 dataset／新市場**：落地前先登錄 world_concept 映射（WM.35）＋ONT 型別繫結＋mint identifier；generic_schema 照舊 auto-schema（形權威），**但消費資格由 registry 決定**。新市場（如美股深化）＝新 Domain Profile 條目（WM §13，minor 升版）。
2. **新能力**（新模型、新 advisor 能力、新 agent 行為）：spec-first——先查 §0.5 歸屬 Layer、承接對應 DEFER 掛鉤（如 L6 風險分級）、audit_lint 綠才 merge（greenfield 政策：finding 即 error）。
3. **L7 生效後**：基建合憲化收編（qdrant/ollama/systemd 服務納 L7.10 Bearer Registry、L7.48 Channel 登錄；備份依 L7.25「未經實測之備份推定不存在」建立還原演練節奏）。
4. **稽核常態化**：audit_lint 增 `--db` 模式（對生產唯讀跑 §8.3 不變式：五元組齊備、六元組歸因、K→E→O 鏈）＋CI merge-gate（總綱階段 9，俟 #22 驗收後 Steward 裁）。

## 三、依賴與順序

```
Phase 0 ✅ ─→ Phase 1（code 部署）─→ Phase 2（Identity）─→ Phase 6（Registry 絞殺）
                    │                      │
                    ├→ Phase 3（行動）      └→（屬性 as-of 供 Phase 6 消費）
                    ├→ Phase 4（Serving）
                    └→ Phase 5（Confidence）──→ 擴張軌（隨時可始，Phase 2 後全速）
Phase 7（治權，期限驅動）與各期並行；L7／#22 由另案（RULING-2026-010、2008-DRAFT 復審）匯入
```
Phase 1 是唯一全域前置（code 不部署，一切行為面不動）。Phase 3/4/5 互相獨立可並行。Phase 6 依賴 2（identifier 就緒）與 5（Confidence 可附）。

## 四、風險與誠實殘餘

| 風險 | 處置 |
|---|---|
| owner 分離前 trigger 可被 owner 停用 | Phase 1(d) 首要處理；處理前誠實視為「約定級」保證 |
| 活系統改 code（heal 鏈、predict 出單） | 每步沙盒先行＋影子比對＋熔斷回退；服務重啟紀律（#7） |
| 單一自然人（雙人核准不可能） | 依 §8.4 豁免登錄＋冷卻期替代（GROUNDING-MAP §五既列） |
| 無 GPU（L5 引擎） | 擴張軌不含本機推論；外部 API＋synthetic 標記天花板 |
| backfill 大批量 mint 之錯鑄 | 分批＋冪等＋evidence 繫名冊來源列；錯鑄依 ID.40 correct 事件留痕修正（不刪除） |
| 37 檔絞殺期間新舊並存 | 雙讀影子比對為每檔硬閘；registry 未覆蓋之概念維持舊路（絞殺非斷供） |

## 五、Steward 決策點（本計畫書之待批）

1. **本計畫書採認**與各期排程節奏（幕僚建議：Phase 1 立即、2/3/4/5 兩週窗、6 一個月窗、7 期限驅動）。
2. Phase 1 之 **PR 併 main**（#19 檢視）＋ owner 分離方案。
3. Phase 3 之升裁決 C（authorization_ref 是否 NOT NULL）。
4. 原則精華 #7 條文改（Phase 7）。
5. 擴張軌之 CI merge-gate 時點（俟 #22 驗收）。

---
*[I] 計畫書 v0.1-draft。統整自 GROUNDING-MAP（44 條義務對映）、ROLLOUT-PLAN 軌道 B/C、審計 26 發現與 54 亮點、augur-code 九路全讀。凡數字附產生指令或明標未驗；一切 apply／併 main／充任屬 Steward。*
