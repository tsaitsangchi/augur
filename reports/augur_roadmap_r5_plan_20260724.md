# Roadmap R5 計畫 — 預測半系統對齊落地 [I]（2026-07-24）

* **性質**：[I] plan-first 計畫書（CLAUDE #16／#20；憲章第六部計畫完整性）— **不創設 [N] 義務**；**計畫已拍板；S1＋S2 已開跑並閉合**
* **授權觸發**：Steward「**開 R5 計畫**」＝只寫計畫（✅）；「**開 R5**」＝啟動實作（✅ **2026-07-24 已授權**；範圍 `R5-E12`）
* **對齊落地 〔A〕**：`reports/augur_constitution_to_implementation_roadmap_20260724.md` §3.6／§7.1
* **Gap SSOT**：`reports/augur_roadmap_r3_gap_ledger_20260724.md`（G-ISO-2／G-PV-1／G-OUT-*；G-DIV-1／G-CAT-1＝依賴邊界）
* **前置**：R0–R4 ✅ DONE；direction product gate 本機親驗 PASS（`audits/ROADMAP-U3-DB-VERIFY-20260724.md`）；`import_isolation`／`test_philosophy_isolation` 靜態閘綠
* **並行注意**：Dividend 重建＋窄窗 audit 工單仍在（`reports/augur_dividend_rebuild_20260724.md`）— **本計畫不改該檔**；見 §3；**FinMind／FRED 操作凍結下該線 PAUSED**（`.cursor/rules/finmind-fred-api-freeze.mdc`）

### Steward 已拍板（2026-07-24）

| 欄 | 內容 |
|---|---|
| **日期** | 2026-07-24 |
| **四碼** | `R5-P-yes` ＋ `R5-E12` ＋ `PV-α` ＋ `PAR` |
| **效力** | **計畫採納**為 R5 執行藍圖；**執行已開**（「開 R5」→ S1＋S2 閉；見 `audits/ROADMAP-R5-S12-CLOSED-20260724.md`） |
| **範圍** | `R5-E12`＝S1＋S2（predict wiring＋G-PV-1）；`PV-α`＝AST 字面禁；`PAR`＝採納 §3 並行／等待判準；**S3／U5 未授權** |
| **解凍／Dividend 邊界** | **仍有效**：FinMind／FRED **操作凍結**至 **constitution-to-implementation 全部階段落地＋用戶明示解凍**（禁 sync／probe／放量／窄窗／Dividend 重建 API；**R5 S1–S2／局部完成 ≠ 解凍**）；不 DROP Dividend；不改 [N]；不假關 10-14；零 `evaluated_pass` 禁確立級宣稱 |
| **留痕** | 拍板：`audits/ROADMAP-R5-PLAN-APPROVED-20260724.md`；S12 閉：`audits/ROADMAP-R5-S12-CLOSED-20260724.md` |

**四碼展開（§10 原文對照）**：

| 碼 | §10 含義 |
|---|---|
| **R5-P-yes** | 採納本計畫為 R5 執行藍圖；實作另待「開 R5」／分階授權 |
| **R5-E12** | 授權 S1＋S2（wiring＋G-PV-1；**零 API**）— ✅ 已執行閉合 |
| **PV-α** | G-PV-1 採 AST 字面禁（預設建議）；不採裸 γ |
| **PAR** | wiring／AST 可與 Dividend 並行；確立級與 Dividend 特徵鏈須等條件（採納 §3） |

---

## 0. 一句結論

R5 要把「預測半系統」從**靜態隔離綠＋輸出契約 armed**，推進到 **runtime predict role 真接線**、**`prediction_values` 禁回讀當特徵有機械閘（解 G-PV-1 conflict）**、以及 **確立級／econ 宣稱前的 U5 對抗**——全程零 FinMind 放量、不假關 10-14、不碰 Dividend DROP。

---

## 1. What／Why（對齊 〔A〕）

### 1.1 What — R5 要閉的義務

| 義務簇 | 帳本列 | R5 目標狀態 | 現況（2026-07-24 親驗／帳本） |
|---|---|---|---|
| 動態隔離閘 | **G-ISO-2** | `partial`→可機械判定之 runtime 接線（至少 opt-in `DB_PARAMS_PREDICT`＋predict 路徑走 `augur_predict`） | role **已存在**；`config.py` **無** `DB_PARAMS_PREDICT`；`db.connect()` 單一 `DB_PARAMS`（app user） |
| 產物禁自迴圈 | **G-PV-1** | `conflict`→機械閘（AST 字面＋／或 GRANT）**或** COMMENT／敘事降級為誠實一致 | COMMENT 自稱「AST+GRANT 雙閘」；`augur_predict` 對 `prediction_values` **SELECT+INSERT+UPDATE**；AST **不**擋讀該表 |
| 輸出契約方向軸 | **G-OUT-1** | 維持 `none`（armed）；R5 不重做，只納入哨兵回歸 | `--verify` exit 0；`evaluated_pass`＝**0** → 產物表零列＝fail-closed dormant |
| 幅度軸知情 | **G-OUT-2** | 維持 `doc-only`；禁止讀成「已機械滿足」 | 設計不對稱；非 R5 強制補 DB trigger |
| 靜態隔離 | **G-ISO-1** | 維持 `none`；R5 回歸必綠 | `tests/test_philosophy_isolation.py` 8 passed |
| 確立級門柱 | 原則精華 live／arena；路線圖驗收 | 「確立級」數字唯經門二 `direction_gate`（≥60 clusters 等既有判準）；**零 `evaluated_pass` 則禁確立級宣稱** | `direction_gate`：fail 10／approved 8／preregistered 3／**pass 0** |

路線圖 §3.6 原文步驟對映：PHASE 9–11＋arena／econ 終關、輸出契約 fail-closed、特徵提拔 HAC Eff-t、經濟價值≠IC —— **本計畫近程先閉「隔離 runtime＋G-PV-1＋哨兵」**；全量 universe→model→econ 放量屬 **拍板後另開執行工單**（見 §4 S3／§9 不在範圍）。

### 1.2 Why

* 〔A〕＝對齊落地、否決綠地：既有 predict／arena／gate **code 與表已在**；缺口是 **接線與宣稱誠實**，不是重寫半系統。
* U3（F-U3-4／F-U3-7）已釘死：G-PV-1 conflict、G-ISO-2 partial **非幽靈**——R5 不處理＝繼續帶著「COMMENT 謊言／role 空轉」。
* L6.21／P2.E5 精神：對人呈現之預測性產物須 fail-closed；Representation 錯誤時降級觀測——**機械閘＋誠實敘事**是執行層最小閉合。

### 1.3 明確不做（本計畫／預設 R5 執行）

| 不做 | 理由 |
|---|---|
| **R6** knowledge／advisor 半系統 | 路線圖另段；隔離命門禁止顧問回流預測 |
| **2026-10-14** 日曆假關（G-KDO／G-020／G-025 等） | R2 誠實；禁假關 |
| FinMind **放量** sync／寬窗探測 | #24／#25；Dividend 另線已授權者除外 |
| Dividend **DROP**／改 `augur_dividend_rebuild_*` | 他代理 IN PROGRESS；本檔獨立 |
| 改 MC／specs／原則精華 **[N]** | 硬邊界 |
| 幅度軸補等價 DB fail-closed（G-OUT-2→none） | 屬設計知情；另案才開 |
| AUD-08 全量把 `prediction_values` 改 append-only | Phase 4／另案；R5 可引用伴生表計畫但不併吞 |
| 宣稱「可交易／確立級」而無 `evaluated_pass`＋U5 | 路線圖 U5 前置 |

---

## 2. 治權錨點（原文路徑；不另寫第二套法）

| 錨 | 用途 | 取法 |
|---|---|---|
| **L6.21** | 誠實輸出契約行動側：產物閉集／硬綁揭露／展示分級／fail-closed；L7 物理強制部分 **DEFER**（RULING-020 M2） | constitution-mcp `get_spec_clause L6.21` |
| **P2.E5** | Fail-safe：錯誤／撤回 → 衍生 Knowledge 重評、Plan 暫停、降級觀測 | `get_clause P2.E5` |
| **P4.E4** | Defeasible：Confidence 不得隱含 1.0 | `get_clause P4.E4` |
| 領域大憲章輸出契約 v1.45＋direction product gate | G-OUT-1 落點 | `scripts/migrate_direction_product_gate_ddl.py`；U3-DB-VERIFY |
| 原則精華 #8／#11／#15；live 確立級唯門二 | R5 驗收語意 | `docs/原則精華_v1.10.0.md`（執行時親讀；本計畫不改） |

> 治理權威路徑不做 LLM 濃縮；上表僅索引。衝突時以 [N] 原文＋Steward 為準。

---

## 3. 依賴與並行（Dividend／窄窗 audit／catalog）

### 3.1 進行中作業（只讀邊界）

| 作業 | 狀態 | 對 R5 |
|---|---|---|
| Dividend 重建＋窄窗 audit | **IN PROGRESS**（`reports/augur_dividend_rebuild_20260724.md`） | **勿大改該檔**；R5 計畫／wiring 獨立 |
| G-CAT-1 表級 STALE | R4 partial；欄級 db-only 已對齊 | 全量 `build_catalog` **非** R5 預設；另授權 |
| G-ATTEST 當日 e2e | R4 SKIP 放量；史料 id=4 PASS | R5 可接受史料＋infra；刷新另授權 |

### 3.2 可與 Dividend **並行**（零 API／不碰 raw DROP）

* 本計畫書撰寫與修訂  
* **S0** 盤點（讀 code／GRANT／AST；可選本機 DB 唯讀）  
* **S1** `DB_PARAMS_PREDICT`＋`db.connect` 分流＋pytest（role 已 provision 則本機可測）  
* **S2** G-PV-1 機械閘設計落地（AST 字面／REVOKE 方案／COMMENT 對齊）— **不**觸 FinMind  
* **U5** 對抗審查（只讀宣稱／registry／文件）  
* G-OUT-1／G-ISO-1 回歸哨兵（既有 `--verify`／isolation tests）

### 3.3 **須等**或另授權才做

| 條件 | 等待什麼 | 為何 |
|---|---|---|
| 消費 Dividend 特徵之 rebuild／提拔 | G-DIV-1 親驗閉合（PK⊇`(stock_id,date)` 等） | 塌列會污染特徵／假兆 |
| 「資料地基已完整」入 R5 DONE 敘事 | G-DIV-1 與（若宣稱 catalog 真值）G-CAT-1 | #15 |
| 確立級／可交易行銷句 | ≥1 `direction_gate.status=evaluated_pass` **且** U5 呈核 | 現 pass＝0；門柱未過＝禁宣稱 |
| 新 gate evaluate／approve | Steward TTY 人裁＋#25 紀律 | approve 唯人；禁 AI 代簽 |
| FinMind 放量 panel／sync | 明示授權＋IP 健康最小探測 | #24／#25 |

**判準句**：R5 **wiring／機械閘**可與 Dividend 夜批並行；R5 **數據親驗宣稱「半系統可交易」**須等門二＋（若敘事綁地基）Dividend／catalog 條件。

---

## 4. 分階段

```mermaid
flowchart LR
  S0[S0盤點] --> S1[S1 predict連線]
  S1 --> S2[S2 G-PV-1機械閘]
  S2 --> S3[S3親驗哨兵]
  S3 --> U5[U5對抗]
  U5 --> DONE[R5呈核／另開執行工單]
```

### S0 — 盤點（只讀）

| | |
|---|---|
| **輸入** | Gap 帳本；`setup_predict_role.py`；`config.py`／`db.py`；`import_isolation.py`；`migrate_prediction_ddl.py` COMMENT；live `pg_roles`／`role_table_grants`；U3／R4 audits |
| **輸出** | 本計畫 §1／§5／§6 凍結為執行清單；可選 `audits/ROADMAP-R5-INVENTORY-*.md`（若執行輪需要） |
| **風險** | 把 construction 舊敘事當現況；Dividend 檔被誤改 |
| **停手** | 發現需改 [N]／假關 10-14；DB 不可達則標 SKIP 不假 PASS |

### S1 — predict 連線（G-ISO-2）

| | |
|---|---|
| **輸入** | S0；env 鍵設計（`DB_PREDICT_PASSWORD` 已由 setup 使用）；`tests/test_predict_role_isolation.py` |
| **輸出** | `DB_PARAMS_PREDICT`（或等價）；`connect`／`connect_predict` 分流；predict 入口腳本 opt-in；selftest／pytest 綠；帳本 G-ISO-2 證據路徑 |
| **風險** | 誤讓 advisor／admin 全改走 predict role → 素養表被拒＝服務掛；或接線後仍預設 app user＝假閉合 |
| **停手** | 破壞性 `--apply` role 未授權；密碼入 git；無 `--confirm` 建 role |

**建議設計（拍板後實作，非本輪）**：

1. `config.DB_PARAMS_PREDICT`：同 host／port／dbname，`user=augur_predict`，password=`DB_PREDICT_PASSWORD`；缺密碼 → 結構可建、連線 FAIL 誠實。  
2. `db.connect(params=None)` 預設 `DB_PARAMS`；`db.connect_predict()` 或 `connect(role="predict")` **顯式**。  
3. 僅 `scripts/predict_*.py`／模型寫入路徑改用 predict；advisor／knowledge／migrate **維持 app／superuser**。  
4. 驗收：以 predict 連線 `SELECT` 素養表 → 拒；`INSERT prediction_values`（測試交易 ROLLBACK）→ 准。

### S2 — 機械閘 G-PV-1

| | |
|---|---|
| **輸入** | S1（role 行為已知）；U3 F-U3-4；COMMENT 原文；features SQL 字面掃描結果 |
| **輸出** | 三選一（或組合）落地＋測試；COMMENT／帳本 gap_class 一致 |
| **風險** | REVOKE SELECT 過猛 → predict 寫入路徑自讀失敗；只改 COMMENT＝降級敘事須 Steward 明示接受 |
| **停手** | 無法在「寫入仍可、特徵消費不可」之間機械切開且無降級授權 |

**方案矩陣（執行前擇一）**：

| 方案 | 作法 | 優 | 劣 |
|---|---|---|---|
| **α AST 字面**（建議預設最小） | `import_isolation` 對 `PREDICT_CONSUMERS` 禁字面 `prediction_values`／`prediction_probability`（對稱 SUPERSEDE_LITERALS） | 零 DB 破壞；對齊既有雙閘套路 | 擋不到動態組字串（靠 S1 GRANT 縱深） |
| **β GRANT 收斂** | predict role：輸出表 **INSERT／UPDATE**；**REVOKE SELECT** on `prediction_values`（若寫入不需自讀）；或另 role `augur_feature` 無 SELECT 產物表 | DB 硬擋 | 須證明 writer 路徑零自讀；改 `setup_predict_role.WRITABLE`＋測試 |
| **γ 敘事降級** | COMMENT 改為「意圖：禁回讀；現況：AST 部分＋GRANT 未收 SELECT」；gap→`doc-only`／`partial` | 誠實 | **不**閉機械義務；僅當 α／β 不可行時之 Steward 明示 |

**預設建議**：先 **α**，再視 writer 自讀需求決定是否 **β**；禁止只做 γ 卻宣稱 conflict 已解。

### S3 — 親驗哨兵（零放量）

| | |
|---|---|
| **輸入** | S1／S2 合併；既有 migrate `--verify`；isolation／predict_role tests |
| **輸出** | `audits/ROADMAP-R5-*-VERIFY-*.md`；Gap 帳本回寫證據；**確立級＝仍禁宣稱**（除非另授權 evaluate 且 pass） |
| **風險** | 把「哨兵綠」寫成「可交易」；撞 FinMind |
| **停手** | 任何 API 放量衝動；`evaluated_pass` 仍 0 卻寫確立級 |

**哨兵清單（機械）**：見 §7。

### U5 — 對抗（確立級／econ 宣稱前）

| | |
|---|---|
| **輸入** | S3 證據；路線圖 U5 焦點；registry／HANDOFF／advisor 文案 |
| **輸出** | `audits/ROADMAP-U5-*.md`（Find→Verify→Critic→Synthesize）；存活 finding → 修計畫或 RULING 材料 |
| **風險** | 以 lint 綠替代對抗；Goodhart（為過門改 criteria） |
| **停手** | 發現門柱挪動／洩漏／假確立 → 不進「R5 DONE＝可交易」敘事 |

插入點對齊路線圖 §4.3：**U5 在確立級／econ 宣稱前**；本計畫把 U5 訂為 R5 閉合前置，非可選裝飾。

---

## 5. (a) Table schema

### 5.1 不產新表（預設）

R5 近程 **不**新建表。讀／強制既有物件：

| 物件 | 角色 | 結果落哪 |
|---|---|---|
| `pg_roles`／`role_table_grants`／`has_table_privilege` | G-ISO-2／G-PV-1 親驗 | audits＋Gap 帳本 |
| `prediction_values` | 產物；PK `(panel_date,model_id,stock_id)`；欄 score/rank/in_portfolio/weight | 寫入仍走既有 predict；**禁** features 回讀 |
| `model_registry` | 模型身分證 | 不變 |
| `prediction_probability` | 相對機率軸 | 知情；G-PV-1 建議一併納字面禁（對稱） |
| `direction_gate` | 門二狀態機；trigger `trg_direction_no_goalpost` | 哨兵讀 status 分布；**不**本輪 evaluate |
| `direction_probability`／`daily_direction_probability` | 方向產物；gate guard triggers | 維持 0 列直至 pass |
| `direction_arena_*`／`direction_econ_verdict` | arena／econ | S3 可選存在性檢查；不放量重跑 |
| `feature_values`／`core_universe_*` | 上游 | 唯讀盤點；Dividend 相關 rebuild **等 G-DIV-1** |
| `prediction_unfreeze_gate` | 解凍史料 | 知情；不與 direction 門二混稱 |

### 5.2 若 S2 選 β — DDL／GRANT 草案（非新表）

```sql
-- 草案：僅示意；拍板＋dry-run 後由 setup_predict_role 冪等編排，禁手改 production
REVOKE SELECT ON TABLE prediction_values FROM augur_predict;
-- INSERT/UPDATE 保留（WRITABLE）；若 ON CONFLICT 需自讀則本方案否決→改 α 或分 role
```

`prediction_serving_log`：migrate 已存在於 repo，**本機表可能未 apply**（2026-07-24 探針：relation 可不存在）— R5 **不**強制 apply；列為可選 follow-up，避免與 AUD-08 Phase 4 搶頻寬。

### 5.3 禁止本輪 DDL

* DROP／TRUNCATE raw（含 Dividend）  
* 改 `direction_gate` criteria／伪造 `evaluated_pass`  
* 把手改 COMMENT 卻不改閘（除非方案 γ 經拍板）

---

## 6. (b) Python 程式規畫

| 檔／入口 | 函式／角色 | 階段 | 備註 |
|---|---|---|---|
| `src/augur/core/config.py` | 新增 `DB_PARAMS_PREDICT`；`--selftest` 擴五鍵結構（可允許 password 空＝未配置） | S1 | #12 SSOT；密鑰仍 `.env` |
| `src/augur/core/db.py` | `connect_predict()` 或 `connect(*, params=)`；`ping_predict()` 可選 | S1 | 預設行為不變＝不破 advisor |
| `scripts/setup_predict_role.py` | 維持 provision；若 β：調整 WRITABLE vs SELECT 分離；矩陣已含 `--dry-run`／`--apply --confirm` | S1–S2 | 本輪計畫不執行 `--apply` 除非缺 role |
| `src/augur/audit/import_isolation.py` | 新增產物表字面常數＋`PREDICT_CONSUMERS` 掃描（方案 α） | S2 | #18 矩陣／`--selftest` 既有 |
| `tests/test_philosophy_isolation.py` | 回歸 | S2–S3 | 必綠 |
| `tests/test_predict_role_isolation.py` | 依 α／β 更新 EXPECT（SELECT 准／拒） | S1–S2 | role 未建→skip 誠實 |
| `scripts/migrate_prediction_ddl.py` | COMMENT 與真實閘對齊（α／β 後改文，或 γ） | S2 | 冪等 COMMENT |
| `scripts/migrate_direction_product_gate_ddl.py --verify` | 哨兵 | S3 | 已親驗；回歸 |
| `scripts/predict_asof.py` 等寫入入口 | 改 `connect_predict` | S1 | **最小改**呼叫點；不順手重構 DELETE+INSERT |
| `scripts/check_cmd_matrix.py` | 新入口若有 `__main__` 必過 | S1 | RULING-026 |
| （不改）`augur/advisor/payload.py` | 繼續 app role 讀 `prediction_values` | — | 顧問消費合法；非預測 7 package |

**強制／消費關係**：

* **建表**：無（預設）  
* **遷移**：僅 COMMENT／GRANT 腳本冪等；direction gate migrate **只 verify**  
* **消費**：predict 寫入→產物表；features **不得**消費產物表當特徵  
* **強制**：AST＋（可選）REVOKE＋既有 direction product triggers  

---

## 7. 驗收表（機械 PASS／FAIL）

| ID | 驗收項 | PASS | FAIL |
|---|---|---|---|
| A1 | `DB_PARAMS_PREDICT`（或等價）存在於 `config` 且 selftest 結構斷言綠 | exit 0 | 缺鍵／仍單一 params 卻宣稱 G-ISO-2 閉 |
| A2 | 顯式 predict 連線：`has_table_privilege(augur_predict, philosophy_work, SELECT)=false`（取樣≥3 素養表） | 皆 false | 任一 true |
| A3 | 預測管線入口（清單釘死）預設或旗標走 predict params | 程式路徑可證 | 僅文件宣稱 |
| A4 | G-PV-1：方案 α 下 `check_isolation()` 對 features 字面 `prediction_values`＝0 違規；或 β 下 predict **無** SELECT | 與選案一致 | COMMENT 仍稱雙閘但證據反向 |
| A5 | `tests/test_philosophy_isolation.py` | 全 passed | 任一 failed |
| A6 | `migrate_direction_product_gate_ddl.py --verify` | exit 0 | 非 0 |
| A7 | `direction_gate` 無 `evaluated_pass` 時，任何「確立級／可交易」對外句 | **零出現**於本輪報告／HANDOFF 新增句 | 出現＝FAIL |
| A8 | 本輪 git diff **無** FinMind 放量 log／無 Dividend DROP DDL | 乾淨 | 有放量或 DROP |
| A9 | U5 呈核檔存在且含 Critic「未查項」 | 有 audits | 無對抗即稱 R5 DONE |
| A10 | Gap 帳本 G-ISO-2／G-PV-1 回寫 `actual_evidence` | path:line＋指令輸出 | 只改 gap_class 無證據 |

**R5 階段 DONE（建議定義，拍板確認）**＝ A1–A6＋A8＋A10 全 PASS，且 A7／A9 滿足；**≠** arena 全綠、≠ econ 過關、≠ Dividend 閉合。

---

## 8. 風險與停手總表

| 風險 | 緩解 | 停手訊號 |
|---|---|---|
| 假閉合 G-ISO-2（role 在、code 不連） | A1–A3 強制 | 只有 setup 綠 |
| G-PV-1 只改字不改閘 | 禁裸 γ；U5 打 COMMENT | conflict 仍在卻標 none |
| 顧問／migrate 誤接 predict | 預設 `DB_PARAMS` 不變 | chat／knowledge 502／permission denied 風暴 |
| 與 Dividend 代理衝突 | 獨立檔；不改 rebuild 報告 | 兩代理同改一檔 |
| API ban | 本計畫零放量 | 任何 403／寬窗 |
| 確立級搶跑 | A7＋U5 | pass＝0 仍行銷 |

---

## 9. 明確不在範圍（再聲明）

1. FinMind 放量／ overnight sync  
2. Dividend DROP＋re-sync（他線；本計畫不發令）  
3. 假關 10-14／calendar Gap  
4. R6 素養管線／owned_local 語料  
5. 改 [N] 憲章／specs  
6. 偽造或人手 UPDATE `direction_gate`→`evaluated_pass`  
7. 全量 `build_catalog`（非 db-only）除非另授權  

---

## 10. Steward 拍板句（請擇一或組合回覆）

> 回覆字串即可生效為本計畫授權登錄（路線圖同例；**不**自動等於「開 R5 實作」除非含執行項）。
>
> **✅ 已登錄（2026-07-24）**：`R5-P-yes`＋`R5-E12`＋`PV-α`＋`PAR` — 見文首「Steward 已拍板」；**執行仍待「開 R5」**。

### 10.1 計畫採納（必選）

- **〔R5-P-yes〕** 採納本計畫為 R5 執行藍圖；**實作另待「開 R5」／分階授權**。  
- **〔R5-P-rev〕** 須修訂後再呈（請註條款號）。  
- **〔R5-P-no〕** 否決；R5 改定義或延期。

### 10.2 執行範圍（計畫採納後、開實作時）

- **〔R5-E0〕** 只做 S0 盤點留痕（仍可與 Dividend 並行）。  
- **〔R5-E12〕** 授權 S1＋S2（wiring＋G-PV-1；**零 API**）— **建議近程**。  
- **〔R5-E123〕** 授權至 S3 哨兵（仍禁確立級宣稱）。  
- **〔R5-Efull〕** S0–S3＋U5 一次授權（仍禁放量／禁假確立）。

### 10.3 G-PV-1 方案（若授權 S2）

- **〔PV-α〕** AST 字面禁（預設建議）。  
- **〔PV-αβ〕** α＋GRANT 收斂（須先證明 writer 零自讀）。  
- **〔PV-γ〕** 僅敘事降級（明示接受機械義務未閉）。

### 10.4 並行／等待

- **〔PAR〕** 確認：wiring／AST 可與 Dividend 並行；確立級與 Dividend 特徵鏈須等條件（採納 §3）。  
- **〔WAIT-DIV〕** R5 實作整體等到 G-DIV-1 閉合後再開（較保守）。

### 10.5 明確不授權（預設）

- 不放量 FinMind；不 DROP Dividend；不改 [N]；不假關 10-14；不無 U5 宣稱確立級。

---

## 11. 產物與下一步

| 產物 | 路徑 |
|---|---|
| **本計畫** | `reports/augur_roadmap_r5_plan_20260724.md` |
| 路線圖 R5 節 | `reports/augur_constitution_to_implementation_roadmap_20260724.md` §3.6 |
| Gap 帳本 | `reports/augur_roadmap_r3_gap_ledger_20260724.md` |
| U3／gate 親驗 | `audits/ROADMAP-U3-*.md` |
| R4 閉合 | `audits/ROADMAP-R4-CLOSED-20260724.md` |
| Dividend（只讀邊界） | `reports/augur_dividend_rebuild_20260724.md` |

**建議下一句（用戶）**：G-ISO-2 已 **none**（`ROADMAP-R5-PREDICT-PING`）；另發「**開 S3**」／「**開 U5**」（S1＋S2 已閉）。

---

## 12. 本輪邊界（誠實）

- ✅ 產出本 plan-first 計畫書  
- ✅ 對齊 〔A〕／R5 定義／Gap／並行邊界  
- ✅ 附 schema＋python 規畫＋驗收表＋拍板句  
- ✅ **Steward 已拍板**（2026-07-24；`R5-P-yes`＋`R5-E12`＋`PV-α`＋`PAR`）  
- ✅ **開 R5 → S1＋S2 閉**（2026-07-24；`audits/ROADMAP-R5-S12-CLOSED-20260724.md`）  
- ❌ 未做 S3／U5、未放量 API、未改 [N]、未改 Dividend 報告、未解凍  
- ⚠ FinMind／FRED 操作凍結仍有效（至 constitution-to-implementation 全部落地＋明示解凍；R5 局部完成不解凍）；Dividend API 線 PAUSED
- ✅ G-ISO-2 → **none**（2026-07-24 live `ping_predict` PASS；`audits/ROADMAP-R5-PREDICT-PING-20260724.md`）
