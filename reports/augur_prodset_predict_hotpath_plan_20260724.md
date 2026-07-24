# Prodset → 預測熱路徑計畫 [I]（2026-07-24）

* **性質**：[I] plan-first 計畫書（CLAUDE #16／#20；憲章第六部計畫完整性）— **不創設 [N] 義務**；**計畫已拍板；S1–S3 CLOSED**
* **授權觸發**：Steward「**開 prodset→預測熱路徑計畫**」＝plan-first ✅；「**開 prodset 熱路徑**」＝實作 S1–S3 ✅ CLOSED（`audits/P2H-S123-CLOSED-20260724.md`）
* **閉合目標**：讓 train／選特徵／predict **真讀** `evolution_production_feature_set`（`set_status=active`），閉合 PME-Efull 邊界「**預測熱路徑尚未吃晉升**」
* **前置**：PME ✅ `PME-Efull-yes`（機械完備）；PRODSET ✅ CLOSED（真寫＋run5×2 active）；靈魂措辭 ✅ G-PME-SOUL=none；R5 近程 DONE（wiring／G-PV-1）
* **範式**：`reports/augur_roadmap_r5_plan_20260724.md`
* **硬邊界**：零 FinMind／FRED；不改 [N]；≠可交易／≠確立級；≠ runtime 讀原則文本加權

### Steward 已拍板＋執行 CLOSED（2026-07-24）

| 欄 | 內容 |
|---|---|
| **日期** | 2026-07-24 |
| **狀態** | ✅ **計畫已拍板＋S1–S3 CLOSED**（Steward「開 prodset 熱路徑」） |
| **四碼** | `P2H-P-yes` ＋ `P2H-E123` ＋ `FC-empty` ＋ `FZ-keep`（見 §10） |
| **效力** | 本檔＝執行藍圖；S123 已落地；G-PME-HOTPATH=none；U 另句「開 U-P2H」 |
| **解凍邊界** | **接 prodset ≠ 解凍 API**；FZ-keep；凍結維持**不影響**本計畫執行（見 §1.4；`.cursor/rules/predict-vs-market-api.mdc`） |
| **留痕** | `audits/P2H-PLAN-APPROVED-20260724.md`；`audits/P2H-S123-CLOSED-20260724.md` |

**四碼展開（§10 原文對照）**：

| 碼 | §10 含義 |
|---|---|
| **P2H-P-yes** | 採納本計畫為 prodset→預測熱路徑藍圖 |
| **P2H-E123** | S1–S3（契約＋train＋predict）— **已 CLOSED** |
| **FC-empty** | 空 active → fail-closed（禁回退 canonical） |
| **FZ-keep** | 維持 FinMind／FRED 凍結；接 prodset ≠ 解凍；庫內 as-of 可跑 |

---

## 0. 一句結論

把 PME APPLY 已寫入的 **生產特徵登錄表**接到相對強度訓練／出單熱路徑：特徵允許清單改由 DB `active` 列驅動（經 **共享契約／非 `augur.philosophy` import**），在 **庫內 as-of 切分**上可訓練與推估——**全程零市場 API**；G-PROM 僅 2 特徵 active 時熱路徑**誠實極窄**，不回退偷吃全量 canonical。

---

## 1. What／Why／非目標

### 1.1 What

| 義務 | 現況（2026-07-24） | 本計畫目標 |
|---|---|---|
| PME 晉升登錄 | ✅ `evolution_production_feature_set` 真寫；APPLY／backfill | 維持 writer＝philosophy／APPLY |
| 預測熱路徑特徵集 | ❌ 仍走 `baseline.canonical_features`（`feature_values` 跨 panel 交集） | train／predict **真讀** prodset `active` |
| 隔離 | ✅ PIPELINE 禁 import philosophy；prodset≠canonical 已文件化 | 讀取經 **DB／`augur.core` 契約**，不破 FORBIDDEN |
| Efull 邊界「熱路徑未吃晉升」 | ❌ 明示未閉 | 執行閉合後可標 **G-PME-HOTPATH→none**（≠可交易） |

### 1.2 Why

* Efull 呈核已承認機械完環，但 **強化預測**仍缺「晉升結果進入 fit／serve」——否則 prodset 只是帳本、預測半系統仍吃資料交集偽「全市場特徵」。
* 靈魂↔raw 邊界（`.cursor/rules/soul-vs-raw-correlation.mdc`）：熱路徑吃的是 **已閘後登錄之特徵名 allowlist**（概念／假說落地產物的**許可集合**），**不是**原則文本加權、**不是**整庫 raw 灌入。
* AUTO-B 已寫入靈魂措辭：有界自動上線＝寫 prodset；本計畫＝**消費端**閉合，不改上線政策。

### 1.3 明確非目標

| 非目標 | 理由 |
|---|---|
| ≠可交易／≠確立級 | `direction_gate.evaluated_pass=0`；prodset active ≠ 門二 |
| ≠解凍 FinMind／FRED | FZ-keep；**接 prodset 不寫成解凍前提** |
| ≠ runtime 讀原則／know-how 文本加權 | 只讀特徵名清單；禁把 `philosophy_principle` 敘事當權重 |
| ≠自動下單 | G-NOEXEC 不變 |
| ≠改 [N]／改 MC 條文 | [I] 計畫＋執行層 wiring |
| ≠全量 G-PROM／G-ECON 變綠 | 既有 partial 誠實；本計畫消費**已 active** 列 |
| ≠他域進化閉環 | HANDOFF §4.0 |

### 1.4 零 API／庫內 as-of（用戶明示・必須）

> **所有預測與 FinMind／FRED 無關；無最新資料時，庫內既有資料仍可切分並預測推估。**

| 不變式 | 含義 |
|---|---|
| **熱路徑實作與驗收零依賴市場 API** | 不呼叫 FinMind／FRED；不因缺增量 sync 而阻塞本計畫 |
| **訓練／predict 以 DB as-of 切分為準** | panel／`--asof`／universe／`feature_values` 皆庫內既有；切分＝時間／panel 邊界，非「等最新 API」 |
| **凍結維持不影響本計畫執行** | FZ-keep 下本計畫可拍板、可實作、可驗收 |
| **勿把「接 prodset」寫成需要解凍** | 解凍屬資料地基另線；本計畫閉合≠解凍條件 |

**誠實**：無最新 raw 時，推估品質受庫內 as-of 上限約束（例如既有 panel 止於某日）——屬資料時間界，**不是**本計畫缺 API 的阻斷理由。

---

## 2. 架構（prodset → 允許清單 → train／predict）

```text
PME APPLY (philosophy / apply_evolution_promotions)
    │  UPSERT evolution_production_feature_set (active|removed)
    ▼
┌───────────────────────────────────────┐
│  DB 表 evolution_production_feature_set │  ← SSOT 登錄（已存在）
└───────────────────────────────────────┘
    │  SELECT feature WHERE set_status='active'
    ▼
┌───────────────────────────────────────┐
│  augur.core.prodset_contract（新建）   │  ← 共享讀契約；PIPELINE 可 import core
│  load_active_features(conn) → list[str]│
└───────────────────────────────────────┘
    │
    ├─► resolve_train_feats(conn, panels)  = active ∩ panel 覆蓋紀律
    │         ▲
    │         │  evaluation.baseline 擴充（或薄 wrapper）
    │         │  **禁止** import augur.philosophy
    │
    ├─► scripts/train_ranker.py   --feature-source=prodset（預設建議）
    └─► scripts/predict_asof.py   載 artifact.feats；漂移對照＝當下 prodset 解析集
```

### 2.1 如何不破 FORBIDDEN import

| 層 | 允許 | 禁止 |
|---|---|---|
| Writer | `augur.philosophy.evolution`／`apply_evolution_promotions.py` 寫表 | — |
| Reader（熱路徑） | `augur.core.prodset_contract` 唯讀 SQL；`evaluation`／`models`／scripts 只 import **core** | `from augur.philosophy …`（AST 閘） |
| 字面 | 表名字串可出現在 core／evaluation（**不**列入 `import_isolation` 禁字面——該表即允許清單來源） | 禁把 `philosophy_principle`／bridge／distill 字面塞進 PREDICT_CONSUMERS |
| DB 雙閘 | predict role：**僅** `evolution_production_feature_set` SELECT（建議）；其餘 `evolution_*` 帳本表 REVOKE | 勿 GRANT 整包 evolution 帳本給 predict「圖省事」 |

**常數重複策略（建議）**：表名／status 字面以 **core 為讀側 SSOT**；philosophy writer 可 `from augur.core.prodset_contract import PRODSET_TABLE, …`（素養→core 合法），避免兩套漂移。若短期雙常數，S1 selftest 必須字面相等斷言。

### 2.2 特徵解析語意（建議釘死）

```text
active = SELECT feature FROM evolution_production_feature_set WHERE set_status='active'
covered = 在 train panels（≥CANONICAL_START 紀律可複用）皆出現於 feature_values 之特徵
feats  = sorted(active ∩ covered)
```

* **不是**「canonical 全量再 optional filter」當預設——那會在空／窄 prodset 時偷吃 29～35 特徵。  
* **不是**裸用 active 而不查 `feature_values`——缺列＝假矩陣。  
* `feats_hash`／`model_registry` 仍凍結該次 fit 的 feats（既有 artifact 契約）。

### 2.3 與 kill-switch／AUTO-B／空 prodset

| 機制 | 建議行為 | 理由 |
|---|---|---|
| **AUTO-B** | 不變：閘全綠∧kill clear → APPLY 寫 prodset | 本計畫只消費 |
| **kill-switch=halt** | **擋新 APPLY**；熱路徑仍讀**當下已 active**（可選 stderr 警告） | predict≠下單；halt≠抹除已登錄 |
| **空 active（0 列）** | **`FC-empty`＝fail-closed**：train／predict 預設中止，印「prodset empty」 | 「真讀」不可回退全量 canonical 假裝吃了晉升 |
| **legacy 逃生口** | CLI `--feature-source=canonical` **僅研究／對照**；預設＝`prodset`；文件標非 PME 熱路徑 | 保留可重現舊實驗，禁當 production 預設 |
| **G-PROM 僅 2 active** | **預期極窄**：fit／serve 僅這 2（∩覆蓋）維；metrics 必記 `n_feats`／feature 名單 | 誠實窄＞假寬 |

---

## 3. 分階段

```mermaid
flowchart LR
  S0[S0盤點] --> S1[S1讀取契約]
  S1 --> S2[S2接train]
  S2 --> S3[S3接predict]
  S3 --> U[U對抗]
  U --> DONE[呈核／Gap回寫]
```

### S0 — 盤點（只讀）

| | |
|---|---|
| **輸入** | PRODSET CLOSED；`evolution.py` DDL／APPLY；`baseline.canonical_features`；`train_ranker`／`predict_asof`；`import_isolation`；`setup_predict_role.classify`；live prodset 列數（DB 可達時） |
| **輸出** | 本計畫 §1–§2 凍結；可選 `audits/P2H-INVENTORY-*.md` |
| **停手** | 發現須改 [N]；誤開 API；把「需解凍」寫進執行前提 |

### S1 — 讀取契約

| | |
|---|---|
| **輸入** | S0 |
| **輸出** | `augur.core.prodset_contract`（`load_active_features`／`--selftest`）；GRANT 政策：predict **只** SELECT prodset 表；`setup_predict_role` 調整＋dry-run；isolation／pytest 綠 |
| **停手** | pipeline 出現 philosophy import；把整包 `evolution_*` 敞開給 predict |

### S2 — 接 train

| | |
|---|---|
| **輸入** | S1；`train_ranker.py` |
| **輸出** | 預設 `--feature-source=prodset`；`resolve` 進 artifact／registry；空集 fail-closed；零 API 實測（庫內 as-of） |
| **停手** | 空 prodset 卻 silent fallback canonical；觸發 FinMind |

### S3 — 接 predict

| | |
|---|---|
| **輸入** | S2 產物 artifact |
| **輸出** | `predict_asof`：serve 仍用 artifact 凍結 feats；**修復／落實**「當下解析集 vs 凍結」漂移檢測（現況 `cur_feats` 死變數知情債）；prodset 模式下記錄來源 |
| **停手** | 漂移時靜默用舊集卻宣稱已接 prodset |

### U — 對抗（熱路徑宣稱前）

| | |
|---|---|
| **輸入** | S1–S3 證據；Efull §3；soul-vs-raw |
| **輸出** | `audits/P2H-ULTRACODE-*.md`（Find→Verify→Critic→Synthesize）；存活 finding → 修計畫或擋「已吃晉升」對外句 |
| **焦點** | 假寬（fallback）；FORBIDDEN 旁路；空集行為；2 特徵極窄被說成「生產完備」；解凍話術偷渡；原則文本加權 |

---

## 4. (a) Table schema

### 4.1 既有表（為主；本計畫預設不產新表）

| 物件 | 角色 | 本計畫 |
|---|---|---|
| **`evolution_production_feature_set`** | PME 生產特徵登錄；PK `feature`；`set_status∈{active,removed}`；provenance→run／queue／apply_log | **讀側 SSOT**；COMMENT 可補一句「熱路徑經 core 契約消費（執行後）」——**不**改成可交易 |
| `evolution_apply_log.production_set_delta` | APPLY 可溯源 | 唯讀對帳 |
| `evolution_kill_switch` | AUTO-B 急停 | 不擋讀已 active（§2.3） |
| `feature_values` | 特徵真值 | 覆蓋 ∩；as-of 切分原料 |
| `core_universe_asof` | 名單 | 既有 |
| `model_registry`／artifact | feats_hash 凍結 | train 寫入；predict 載入 |
| `prediction_values` | 出單產物 | 既有 R5 契約 |

**現行 DDL（已落地；引用）**：

```sql
-- 已存在於 EVOLUTION_DDL（philosophy.evolution / migrate_philosophy_evolution_ddl）
CREATE TABLE IF NOT EXISTS evolution_production_feature_set (
    feature           VARCHAR(255) PRIMARY KEY,
    set_status        VARCHAR(16) NOT NULL DEFAULT 'active',
    registered_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    source_run_id     BIGINT NOT NULL REFERENCES evolution_run(run_id),
    source_queue_id   BIGINT NOT NULL REFERENCES promotion_queue(queue_id),
    apply_log_id      BIGINT NOT NULL REFERENCES evolution_apply_log(apply_log_id),
    principle_id      INTEGER REFERENCES philosophy_principle(principle_id),
    last_action       VARCHAR(16) NOT NULL,
    CHECK (set_status IN ('active','removed')),
    CHECK (last_action IN ('promote','demote','freeze'))
);
```

### 4.2 新表

**預設無。** 若 U 對抗要求「熱路徑消費審計」才另開薄表（如 `prodset_consume_log`）——**須另句授權**，不塞進近程 S1–S3。

### 4.3 GRANT（非新表；setup 冪等）

```sql
-- 草案：predict 只讀登錄表；其餘 evolution 帳本拒
GRANT SELECT ON TABLE evolution_production_feature_set TO augur_predict;
REVOKE ALL ON TABLE evolution_run, evolution_coverage_snapshot,
  promotion_queue, evolution_apply_log, evolution_kill_switch FROM augur_predict;
```

（實作落 `setup_predict_role.classify`：prodset→allowed；其他 `evolution_*`→forbidden 或 explicit revoke。）

---

## 5. (b) Python 檔／函式／角色

| 檔／入口 | 函式／角色 | 階段 |
|---|---|---|
| **`src/augur/core/prodset_contract.py`**（新） | `PRODSET_TABLE`／`PRODSET_ACTIVE`；`load_active_features(conn)→list[str]`；`resolve_prodset_feats(conn, panels)→list[str]`（active∩覆蓋）；`--selftest` 零 IO | S1 |
| `src/augur/philosophy/evolution.py` | writer 常數改 import core（或 selftest 對齊）；**不**被 pipeline import | S1 |
| `scripts/setup_predict_role.py` | classify：prodset GRANT；其他 evolution_* REVOKE | S1 |
| `src/augur/evaluation/baseline.py` | 薄接 `resolve_prodset_feats` **或** scripts 層組裝後傳 `feats=`；保持 `canonical_features` 作 legacy | S2 |
| `scripts/train_ranker.py` | `--feature-source={prodset,canonical}`；預設 prodset；空→exit≠0 | S2 |
| `src/augur/models/artifact.py` | 既有 feats_hash；不變 | S2 |
| `scripts/predict_asof.py` | 載 artifact feats；漂移：`resolve_prodset_feats`（或 registry 標註之 source）vs 凍結 hash；修死變數債 | S3 |
| `src/augur/audit/import_isolation.py` | 回歸：PIPELINE 仍 0×philosophy；**不**禁 prodset 表名字面於 core／evaluation | S1–U |
| `tests/test_philosophy_isolation.py` | 必綠 | S1–S3 |
| `scripts/apply_evolution_promotions.py` | **不改語意**（已寫 prodset） | — |
| （可選）`scripts/verify_prodset_hotpath.py` | 哨兵：active 列、train dry 解析、isolation、零 API | S3 |

**強制／消費**：

* **寫**：僅 APPLY／backfill（既有）  
* **讀**：core 契約 → train／predict  
* **強制**：空集 fail-closed；isolation AST；predict GRANT 收斂  

---

## 6. 誠實預期：G-PROM 僅 2 特徵 active

| 事實錨 | 內容 |
|---|---|
| 證據 | `audits/PME-PRODSET-CLOSED-20260724.md`：`inst_cumflow_position_120d`、`volume_gini_60d` → **active**（run_id=5） |
| 熱路徑預期 | 預設 prodset 模式下 **n_feats≤2**（再 ∩ 覆蓋；若其一缺 panel 覆蓋則更少或 fail） |
| 正確敘事 | 「PME 晉升子集已進 fit／serve」 |
| 錯誤敘事 | 「生產特徵完備／可交易／等同舊 29～35 canonical」 |
| 對照實驗 | 另跑 `--feature-source=canonical` **不**覆蓋 prodset 宣稱 |

---

## 7. 驗收表 A*

| ID | 驗收項 | PASS | FAIL |
|---|---|---|---|
| **A0** | 本計畫含 what／why／非目標／架構／階段／schema／python／空集建議／零 API | 本檔 | 缺件 |
| **A1** | `augur.core.prodset_contract` 存在；PIPELINE／evaluation／models **無** philosophy import | `check_isolation` 0 違規 | 任一 import |
| **A2** | `load_active_features` 回列＝DB `set_status=active`（親驗） | 集合相等 | 硬編／錯表 |
| **A3** | predict role：prodset SELECT＝准；抽樣其他 `evolution_*`＝拒 | 與 §4.3 一致 | 整包 evolution 敞開 |
| **A4** | `train_ranker --feature-source=prodset`：feats⊆active∩covered；registry 記 n_feats／名單 | 可溯源 | 靜默用 canonical |
| **A5** | 空 active：預設 train／predict **中止**（FC-empty） | exit≠0＋訊息 | fallback 全量 |
| **A6** | `predict_asof`：artifact feats 出單；漂移檢測非死變數 | 漂移拒載或誠實告警（釘死一種） | 假口徑鎖 |
| **A7** | 本輪／驗收 **零** FinMind／FRED 呼叫 | 無 API log | 有 sync／probe |
| **A8** | 庫內 as-of（無最新 raw）仍可完成一次 train 或 predict dry／run（既有 panel） | 成功或誠實缺覆蓋 | 因「未解凍」拒跑 |
| **A9** | 對外句無「可交易／確立級／已解凍」 | 零出現 | 出現＝FAIL |
| **A10** | U 對抗檔含 Critic「未查項」；Gap **G-PME-HOTPATH** 回寫 | audits path | 無對抗即稱閉合 |
| **A11** | 2-feature 極窄：報告／metrics 明示 n_feats | 明示 | 誇大完備 |

**階段 DONE（建議）**＝ A1–A8＋A11 機械 PASS，且 A9／A10 滿足；**≠**可交易、**≠**解凍、**≠** G-PROM 多數綠。

---

## 8. 風險與停手

| 風險 | 緩解 | 停手 |
|---|---|---|
| 空集／窄集回退 canonical＝假吃晉升 | FC-empty；預設 prodset | 發現 silent fallback |
| philosophy import 旁路 | AST＋code review | isolation≠0 |
| evolution 帳本洩漏進 predict | GRANT 收斂 | 其他 evolution_* SELECT＝准 |
| 把接線寫成須解凍 | §1.4 不變式＋A8 | 文件／碼路徑等 API |
| 2 特徵說成完備 | A11＋U | 行銷句越界 |
| kill halt 誤停預測 | §2.3 | 未授權改成「halt＝禁 predict」 |

---

## 9. 明確不在範圍

1. FinMind／FRED 任何呼叫或解凍敘事  
2. 改 META-CONSTITUTION／領域憲章 [N]  
3. 自動下單／券商  
4. 原則文本／embedding 進特徵矩陣  
5. 強制 G-PROM／G-ECON 全綠才許接線（消費已 active 即可）  
6. Dividend DROP／重建（PAUSED；正交）  
7. 本輪實作（除非 Steward 另句「開 prodset 熱路徑」）  

---

## 10. Steward 拍板句

> 回覆字串即可登錄為計畫授權（**不**自動等於開實作，除非含執行項）。
>
> **✅ 已登錄（2026-07-24）**：`P2H-P-yes`＋`P2H-E123`＋`FC-empty`＋`FZ-keep` — 見文首「Steward 已拍板」；**執行仍待「開 prodset 熱路徑」**。

### 10.1 計畫採納（必選）

- **〔P2H-P-yes〕** 採納本計畫為 prodset→預測熱路徑藍圖；實作另待「開 prodset 熱路徑」／分階。  
- **〔P2H-P-rev〕** 須修訂後再呈（請註條款）。  
- **〔P2H-P-no〕** 否決。

### 10.2 執行範圍（採納後、開實作時）

- **〔P2H-E0〕** 只做 S0 盤點留痕。  
- **〔P2H-E12〕** S1＋S2（契約＋train）。  
- **〔P2H-E123〕** S1–S3（含 predict；**建議近程**）。  
- **〔P2H-Efull〕** S0–S3＋U。

### 10.3 空集行為（建議預設）

- **〔FC-empty〕** 空 active → fail-closed（**建議**）。  
- **〔FB-canonical〕** 空則回退 canonical（**不建議**；與「真讀」衝突，僅當 Steward 明示接受假寬風險）。

### 10.4 凍結（建議併附）

- **〔FZ-keep〕** 維持 FinMind／FRED 凍結；**確認接 prodset 不構成解凍**。

### 10.5 建議回覆組合

```text
P2H-P-yes + P2H-E123 + FC-empty + FZ-keep
```

（要含對抗閉合再加 `P2H-Efull` 或另句「開 U」。）

---

## 11. Gap 登錄（執行後回寫）

| ID | 現 | 目標 |
|---|---|---|
| **G-PME-HOTPATH** | **none**（S123 CLOSED） | 執行 DONE → **none**（機械語意；仍≠可交易；U 另開） |

帳本：`reports/augur_pme_gap_ledger_20260724.md`（執行輪回寫；本 plan-first **不**假關）。

---

## 12. 本輪邊界（誠實）

- ✅ 產出 plan-first（含零 API／庫內 as-of／FORBIDDEN 解法／FC-empty／2 特徵極窄）  
- ✅ **Steward 已拍板**（2026-07-24；「回拍板碼」）：`P2H-P-yes`＋`P2H-E123`＋`FC-empty`＋`FZ-keep`（`audits/P2H-PLAN-APPROVED-20260724.md`）  
- ✅ **S1–S3 CLOSED**（「開 prodset 熱路徑」；`audits/P2H-S123-CLOSED-20260724.md`；G-PME-HOTPATH=none）  
- ⏳ U 對抗未開（另句「開 U-P2H」）  
- ❌ 未改 [N]／未解凍／未宣稱可交易  

---

*計畫完整性：§4 schema＋§5 python；30 分鐘可讀：§0–§2＋§1.4＋§10。*
