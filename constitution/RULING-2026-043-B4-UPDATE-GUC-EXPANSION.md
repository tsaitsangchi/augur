# Augur Steward 裁決第 2026-043 號

**誠實帳本 UPDATE 面之擴大上閘（B4）——C5「僅 DELETE 面上閘」之一部翻案；kill_switch 依乙案排除**

* **依據**：`AUGUR-MC v1.6 §P5.W2`（人閘）、`§8.1`（解釋與裁決專屬 Steward）；`AUGUR-L6 v1.2` L6.18(a)（AI 不得為涉及自身監督機制變更之核准主體）；CLAUDE.md #12（單一住所）／#26（OCV 單向棘輪）；呈案 `reports/w2_20260801/B4_update_guc_upgrade.md`、`reports/w2_20260801/B4P2_remaining_tables_proposal.md`
* **裁決人**：Constitution Steward（tsaitsangchi）
* **登錄**：Amendment Log **AL-2026-047**
* **性質**：**既有裁決（C5）之一部翻案＋執行分批授權**；零條文變更、零 spec 觸動；C5 原文不刪不改（判死留檔，CLAUDE #32(c)）

## 〇、緣起與 C5 之射程

C5（2026-07-26）就誠實帳本之機械保護裁定「先上 DELETE 面」，理由為當時寫入者眾、UPDATE 面全面上閘之重構成本不成比例。其後（2026-07-31〜08-02）之實況推翻該前提之一部：

* **「機器覆寫人裁」之實犯風險已具體化**——決議欄／人簽欄／治理答案之裸 `UPDATE` 面在 20 張表上完全無阻擋（呈案 §2 親驗）。
* 單一角色整併（2026-07-31）後，`GRANT` 層區分力歸零（見 `RULING-2026-042` 主文二 2），使「應用層自律」成為唯一防線。

## 一、採案

**採甲案（分批擴大 UPDATE-GUC 閘）**，共三批：

| 批 | 表 | 施作日 | 狀態 |
|---|---|---|---|
| **P0** | `principle_factor_map`／`philosophy_principle`／`evolution_production_feature_set`／`feature_sign_check`（3 升級＋1 新掛） | 2026-08-01 | 已施作、行為探針全過 |
| **P2a** | `promotion_queue`／`steward_question_ledger`／`evolution_hypothesis_hint`／`evolution_apply_log`／`evolution_evidence_run` | 2026-08-02 | 已施作、legacy trigger 名 0 殘留 |
| **P2b** | `evolution_run`／`evolution_iteration_ledger`／`raw_evolution_iteration_ledger`／`evolution_coverage_snapshot`／`local_ai_iteration_ledger`／`mc_simulation_run` | 2026-08-02 | 已施作、六表裸拒／帶證雙向探針全過 |

**機制**：`honesty_ledger_guard`（單一住所＝`scripts/migrate_honesty_guards_ddl.py`）；合法寫入者於交易內帶通行證 `SET LOCAL augur.honesty_write='on'`；DELETE／TRUNCATE 一律拒。

## 二、主文

1. **翻案射程限於「UPDATE 面是否上閘」**；C5 之其餘裁定（DELETE 面既有保護、判死留檔慣例）不受影響，C5 全文保留為史料。
2. **`evolution_kill_switch` 排除（§5 乙案）**：緊急煞車須零摩擦，加通行證將降低**否決可達性**（CLAUDE #26 OCV 單向棘輪明文：否決可達性弱化屬治權變更）。其 `clear` 默改面之殘餘風險**明載不粉飾**，緩解＝C2 watchdog 對 halt 狀態之獨立監看＋`n_tup_upd` 事後稽核。
3. **P2c（sim 專章七表）緩議**：其 mutability 由 sim 專章逐表設計（先例＝`sev_no_update`、candidate forward-only），不由 honesty 機制代升，避免閘住所自 sim DDL 分裂（#12）。
4. **殘餘誠實揭露**：本閘為**引擎層**保護，非權限層錨定——`augur` 為 superuser，得 `ALTER TABLE … DISABLE TRIGGER` 或 `SET LOCAL session_replication_role='replica'` 卸除任一 guard（後者於 2026-08-03 r4 對抗核驗中親驗可行、無 DDL 無痕）。此殘餘與 `RULING-2026-042` 主文二 2 所載為同一風險，不重複計算亦不假關。

## 三、明示不為

* 不改任何 spec／[N] 條文；不升任何 Layer 版本號。
* 不豁免 L7.16；不重開 §8.2。
* 不刪改 C5 原文（判死留檔）。
* 不將 `kill_switch` 納入本批（乙案已裁）。
* 不代 P2c 預斷。

## 四、驗證（機械可判）

* `pg_trigger` 現查：P0＋P2a＋P2b 共 15 表各掛 `honesty_ledger_guard`（row＝UPDATE｜DELETE、statement＝TRUNCATE）；legacy 自訂名 0 殘留。
* 行為探針（BEGIN…ROLLBACK）：裸 `UPDATE` 拒、帶通行證過、`DELETE` 恆拒。
* `scripts/migrate_honesty_guards_ddl.py --check` rc=0；`--apply` 冪等重跑零變更。
* 全庫面：`honesty_delete_only_guard` 表數自 20 降至 9（`kill_switch`＋sim 七表＋其餘緩議者）。

## 五、施作紀錄

| 檔案 | 摘要 |
|---|---|
| `scripts/migrate_honesty_guards_ddl.py` | `GUC_TABLES_P0/P2A/P2B`＋`LEGACY_TRIGGERS` 映射＋`_registry_problems` 純函式 |
| `scripts/migrate_steward_qledger_ddl.py`／`src/augur/audit/evolution_ledger_ddl.py`／`scripts/migrate_sim_evolution_ddl.py` | 原住所同步（冪等重跑不掛回 delete-only） |
| 寫入者通行證補丁 | P0 10 點／P2a 9＋1 點／P2b 10 點（逐點列於 `audits/B4-*-RED-*.md`） |
| `audits/B4-UPDATE-GUC-RED-20260801.md`／`B4-P2A-…-20260801.md`／`B4-P2B-…-20260802.md` | 三批突變驗紅紀錄 |

## 六、程序瑕疵之誠實登錄（本裁決之產生過程）

**2026-08-03 r4 對抗核驗（X 鏡頭）發現**：Steward 於 2026-08-02 以「B4-043」指配本裁決編號後，AI 僅將編號補入 `migrate_honesty_guards_ddl.py` 之標頭，**未建立本裁決檔、未登錄 AL**——致使 6 個檔／18 處引用一個**當時尚不存在的法源**，而其所憑之閘已施作於 11＋張表。

本檔即該缺漏之補正。**施作在前、裁決檔在後**之事實據實記載，不追溯粉飾；三批施作之實質授權來自 Steward 於 2026-08-01／08-02 之逐案圈選（呈案 §7 決定欄與對話留痕），編號指配亦為 Steward 所為——**缺的是文件本體，不是授權**。

> **簽核欄（Steward）**
> - [x] **准：B4 三批 UPDATE-GUC 擴大上閘（C5 一部翻案；kill_switch 乙案排除；P2c 緩議）**（簽：hugo，日期：2026-08-04）

*本裁決於 Steward 簽核時生效——已簽核，本裁決自 2026-08-04 生效。簽核留痕：Cursor 對話明示指示「RULING-2026-043...要現在簽核（我會填入 hugo+今日日期，依您此處明示指示）」，Steward 選「是，現在簽核」（`ruling_043_decision=sign_now`）。施作內容於簽核前已完成並機械驗證（見上方§四），本簽核為文件補正、非變更已生效之機制。*
