# KDO.4／LDO.4 量測落地——口徑呈案

**日期**：2026-08-03
**性質**：L7 量測實作之**口徑呈案**（非計畫書、非裁決）。AI 草擬與比對，**條文解釋權專屬 Constitution Steward**（`AUGUR-MC v1.6 §8.1`；CLAUDE.md #28 檔位≠權限）。
**觸發**：F2 備料 `reports/augur_1014_review_evidence_prep_20260801.md` §5 checklist 第 5 項；`RULING-2026-039` 五.3「觸發＝LDO.4／LDI.31 實作落地或 2026-10-14 併審」。
**交付物**：`scripts/report_identity_resolution_metrics.py`（唯讀量測器）＋ 本呈案。
**本呈案不主張**：不主張 KDO.4 已履行、不主張任何門檻值、不主張 10-14 日曆項可提早結清（`RULING-2026-039` 六「無 Evidence 不提早結清」）。

---

## §1 條文定錨與下放鏈

量測義務自 L3 概念定義逐層下放至 L7 物理落地，鏈路如下（各節點行號為 2026-08-03 現查）：

| 層 | 條款 | 錨（file:line） | 該層所定之事 |
|---|---|---|---|
| L3 | `AUGUR-ID v1.0` ID.51 | `specs/IDENTITY-SPECIFICATION.md:280-288` | **定三指標之概念與可盤點性**；量測落地與門檻 DEFER |
| L3 | `AUGUR-ID v1.0` IDO.4 | `specs/IDENTITY-SPECIFICATION.md:380` | 下放列：resolution 演算實作＋量測落地與門檻值，目標 L4 |
| L4 | `AUGUR-KS v1.1` KS.83(i) | `specs/KNOWLEDGE-SYSTEM-SPECIFICATION.md:511-518` | 定三指標於**完備性等級之納入語義**；量測落地 DEFER |
| L4 | `AUGUR-KS v1.1` KDO.4 | `specs/KNOWLEDGE-SYSTEM-SPECIFICATION.md:637` | 下放列：未解析存量量測落地，目標 **L5/L7** |
| L5 | `AUGUR-L5 v1.0` L5.9 | `specs/COGNITIVE-KERNEL-SPECIFICATION.md:159-160` | **定性承接**（T-KS-6 解消）；量測實作再下放 |
| L5 | LDI.4 ／ LDO.4 | `:199` ／ `:216` | 承接（L5 面向）／ 下放量測實作，目標 **L7** |
| L7 | `AUGUR-L7 v1.0` L7.26 | `specs/INFRASTRUCTURE-SPECIFICATION.md:294-301` | **本層量測落地之實體義務**（本呈案落點） |
| 旁 | `AUGUR-WM v1.0` WM.15 ／ WM.35 | `specs/WORLD-MODEL-SPECIFICATION.md:188-190` ／ `:336-358` | 顯式待決同一性存量之法源 ／ unmapped 存量之法源 |

### 1.1 L7.26 逐字（本層義務主文）

> **L7.26（未解析存量與待決同一性存量之量測落地）**
> 本層承接未解析存量指標（provisional identity 未解析存量、解析時效、`AUGUR-WM v1.0 §WM.35` unmapped 存量、`§WM.15` 顯式待決同一性存量）之**物理量測、擷取與快照儲存**。落地**必須**滿足：
> (a) 四類存量各具**可查詢之顯式清單**與時間序列快照，其**擷取路徑不得由被量測之構件自身支配**（準用 L7.5(c) 度量不可自我洗白）。
> (b) 快照留痕為 Observation，攜 provenance。
> (c) **量測不得為零**：量測構件失效或指標不可得期間，一律推定存量為**不可知**，走保守解釋——受影響範圍內之 provisional Observation **不得**升級為 Knowledge（`§P3.E1`），待決同一性**不得**合併消費（`§WM.15`）。
> **門檻值之登錄**屬 Threshold Registry（L7.45）；**指標之語義**屬 Layer 3／4，本層僅落地、不重定義。

**注意兩點**：① L7.26 列**四類**存量，ID.51 列**三指標**——差異在 ID.51(c) 一條文內同時涵蓋 WM.15 待決與 WM.35 unmapped 兩者，L7.26 將其拆為二類。本實作採四節呈列（見 Q6）。② L7.26 要求「物理量測、擷取**與快照儲存**」三事，本次交付之腳本為**唯讀**，只覆蓋前二事（見 §5）。

---

## §2 三指標：條文原文逐字 → 本實作口徑 → 物理載體

### M1 — 未解析存量（unresolved backlog）

**條文原文逐字**（ID.51(a)，`specs/IDENTITY-SPECIFICATION.md:283`）：
> **(a) 未解析存量（unresolved backlog）**：任一 as-of 時點，處於 provisional 狀態之 Observation 指涉集合之基數，**必須**可盤點；

**本實作口徑**：計 `entity_alias` 中 `alias_status='provisional'` 之列數，as-of ＝ `now()` 單點。

**依據**：`entity_alias.alias_status` 之 CHECK 約束允許 `provisional`／`adopted`／`retired`，是全庫唯一以 `provisional` 為值域之欄位，即 ID.21「未採認即未解析」之物理載體。`entity_registry.status` 之值域為 `active`／`tombstoned`，不承載解析狀態，故非本指標載體。

**條文未逐字定義之處**：計數單位（Q1）、as-of 可重建性（Q2）。

---

### M2 — 解析時效（resolution latency）

**條文原文逐字**（ID.51(b)，`:284`）：
> **(b) 解析時效（resolution latency）**：自 provisional 進入至解析（成功或登錄為顯式待決）之時間分佈，**必須**可量測；

**本實作口徑**：**判為不可知（UNKNOWN）**，另附右設限滯留時長為可得下界。

**依據（此為本呈案最重要之發現）**：條文所求之分佈需要**兩個時點**——進入 provisional、離開 provisional。現行 schema：
* 進入時點：`entity_alias.transaction_time`（有載體）。
* 離開時點：**無載體**。`entity_alias` 無 `resolved_at` 或等價欄位。
* 且 `entity_alias` **未掛 append-only 觸發器**（僅 `trg_alias_no_delete`／`trg_alias_no_truncate`，無 `identity_append_only`）——與 `identity_claim`／`identity_lifecycle_event`／`entity_attribute_version` 三表皆掛 `trg_*_append_only` 形成對照。故 `alias_status` 可**就地 UPDATE 覆寫**，狀態轉換史不留痕。

⇒ 已完成解析之時效分佈**在現行 schema 下不可導出**，且此不可導出性**不會隨資料累積自行消失**——即使日後大量 provisional 被解析，其解析時點仍不被記錄。依 L7.26(c) 標為不可知，不以任何替代數字冒充。

**條文未逐字定義之處**：完成時效之補正方案（Q3）、「進入」時點之定義（Q4）。

---

### M3 — 顯式待決同一性存量

**條文原文逐字**（ID.51(c)，`:285`）：
> **(c) 顯式待決同一性存量**：疑似同一而尚無同一性宣告者（`AUGUR-WM v1.0 §WM.15` 顯式待決同一性存量之法源；結構位置錨 `§WM.21`）與 unmapped 顯式存量（`§WM.35`）**必須**登錄，**待決期間依保守解釋不得合併消費**。

**本實作口徑（WM.15 面）**：**判為不可知（UNKNOWN）**。

**依據（第二個關鍵發現）**：本指標為**否定集**——「疑似同一**而尚無**同一性宣告者」。現行 `identity_claim` 表量的是**已作成之同一性宣告**（現 0 列），**不是**待決集。以「宣告數 ＝ 0」推論「待決數 ＝ 0」是把「沒有人宣告過任何同一性」誤讀為「沒有任何疑似同一待決」——恰為 L7.26(c) 所禁之「量測不得為零」。DB 內查無任何「疑似同一候選」登錄表（腳本實查 `identity_pending_match`／`identity_match_candidate`／`identity_suspected_same` 三候選名皆不存在）。

**已知場外下界**：`reports/identity_retire_name_mismatch_20260801.csv` 之名實不符 **37 例**（Steward 已裁 MM 甲案：A 34＋B 1 認同一實體、C 2 留人裁；**施作屬另案、尚未執行**）。此 37 例正是條文所指之「疑似同一而尚無同一性宣告者」，現存於 CSV、**未入 DB**，故不可查詢、不滿足 ID.51「必須登錄」與 L7.26(a)「可查詢之顯式清單」。

**條文未逐字定義之處**：「疑似同一」之判定與載體（Q5）。

---

### M4 — unmapped 顯式存量（ID.51(c) 之 WM.35 面／L7.26 第四類）

**條文原文逐字**（WM.35，`specs/WORLD-MODEL-SPECIFICATION.md:336`／ID.52，`:290-292`）：ID.52 定「unmapped 顯式存量與 provisional 同構，一律列入解析義務；unmapped 或未登錄映射之通道資料**僅具 Observation 地位**，**不得**被消費為 Representation 或 Knowledge 之依據」。

**本實作口徑**：計 `world_channel_binding` 中 `mapping_status='unmapped'` 且 `superseded_at IS NULL` 之列數。

**依據**：`world_channel_binding` 之 CHECK 約束 `mapping_status = ANY(ARRAY['mapped','unmapped'])`，且 `(mapping_status='mapped') = (concept_key IS NOT NULL)`——即 unmapped 之定義已被 DB 約束釘死，非本實作自創。`superseded_at IS NULL` 過濾為「現行」語義。

**條文未逐字定義之處**：三指標與四類之對應（Q6）。

---

## §3 live 首跑數字（唯讀實跑，2026-08-03 08:31 +08）

指令：`set -a && . ./.env && set +a && venv/bin/python scripts/report_identity_resolution_metrics.py`

| 指標 | 條文錨 | 結果 | 狀態 |
|---|---|---|---|
| **M1** 未解析存量 | ID.51(a) `:283` | **237** | measured |
| **M2** 解析時效 | ID.51(b) `:284` | **不可知（UNKNOWN）** | 無離開時點載體 |
| **M3** 顯式待決同一性存量 | ID.51(c) `:285` | **不可知（UNKNOWN）** | 無候選登錄載體 |
| **M4** unmapped 顯式存量 | WM.35 `:336-358` | **88** | measured |

腳本輸出摘錄（逐字）：

```
【M1】未解析存量（unresolved backlog）
  採用口徑　：計 `entity_alias` 中 alias_status='provisional' 之列數（as-of ＝ now() 單點）
  量測結果　：237
    · total_alias_rows = 3503
    · provisional_by_entity_type = {"Security": 237}
    · ks83_per_identity_capped = 237
    · ks83_per_type_capped = 3440

【M2】解析時效（resolution latency）
  量測結果　：不可知（UNKNOWN）　※ L7.26(c)：不得以 0 冒充
  不可知理由：entity_alias 無『離開 provisional』時點欄、且非 append-only（可就地覆寫狀態），
              已完成解析之時效分佈無資料載體 ⇒ 依 L7.26(c) 標為不可知。
    · censored_dwell_of_currently_provisional =
        {"n": 237, "min_days": 1.4441, "median_days": 1.4441, "max_days": 1.4441}

【M3】顯式待決同一性存量（WM.15 面）
  量測結果　：不可知（UNKNOWN）　※ L7.26(c)：不得以 0 冒充
  不可知理由：DB 無『疑似同一候選』登錄表 ⇒ 待決存量無載體。`identity_claim` 現有 0 列量的是
              『已宣告』而非『待決』，不得以宣告數 0 推論待決數 0（L7.26(c)）。
    · identity_claim_rows = 0
    · carrier_present = False

【M4】unmapped 顯式存量（WM.35 面／L7.26 第四類）
  量測結果　：88
    · total_binding_rows = 98
```

**M2 之滯留時長三值全等（1.4441 日）之解讀**：237 列 provisional 之 `transaction_time` 落在同一次批次載入（2026-08-01 21:52），故 min＝median＝max。此為**資料前置甫落地**之表徵，非量測異常。

---

## §4 【口徑待裁】8 處 — Steward 決定欄

以下 8 處為**條文未逐字定義**之計算口徑。本實作採暫行口徑以產出數字，暫行口徑**不具解釋效力**（`§8.1`）。決定欄留白，待 Steward 填。

### Q1（M1）計數單位
ID.51(a) 字面為「處於 provisional 狀態之 **Observation 指涉集合**之基數」。`entity_alias` 一列＝一個外部碼別名，**非**一筆 Observation；一個 provisional 別名可被數以百萬計之觀測列引用。二讀之數量級差距極大。
* 讀法甲＝計 alias 列數（**本實作暫採**：解析動作之單位、機器可判、保守不膨脹）→ 237
* 讀法乙＝計其所指涉之觀測列數 → 未計（量級遠大）

**Steward 決定**：〔　　　　　　　　　　　　　　　　〕

### Q2（M1）as-of 可重建性
ID.51(a) 字面為「**任一** as-of 時點」。現行 `alias_status` 就地 UPDATE、無狀態史，僅 `now()` 可量，歷史時點不可重建。
* 暫採＝as-of ＝ `now()` 單點
* 待裁＝是否要求歷史可重建（須加狀態史表或 append-only 觸發器）

**Steward 決定**：〔　　　　　　　　　　　　　　　　〕

### Q3（M2）完成時效不可導出之補正
現行 schema 無「離開 provisional」時點欄且非 append-only，完成時效分佈不可導出。
* 暫採＝依 L7.26(c) 標不可知，另印右設限滯留時長為下界
* 補正選項＝(i) 加 `entity_alias.resolved_at` 欄；(ii) 對 `entity_alias` 掛 `identity_append_only` 觸發器並改以版本列表達狀態轉換；(iii) 另立 alias 狀態史表
* 註：本補正屬 **DDL 變更**，非本次唯讀交付範圍，須另案授權

**Steward 決定**：〔　　　　　　　　　　　　　　　　〕

### Q4（M2）「進入」時點之定義
「進入 provisional」採 DB 插入時點（`transaction_time`）或該觀測之實際攝取／發生時點，條文未定。
* 暫採＝`transaction_time`（唯一有載體者）

**Steward 決定**：〔　　　　　　　　　　　　　　　　〕

### Q5（M3）「疑似同一」之判定與載體
ID.51(c)「疑似同一」未定判定門檻（ID.51 末句明言「不內嵌具體門檻」），且 DB 無候選登錄表。
* 暫採＝依 L7.26(c) 標不可知（**非** 0）
* 待裁＝(i) 判定「疑似」之判準來源；(ii) 是否須建候選登錄表以滿足 ID.51「必須登錄」；(iii) 已裁之 MM 37 例是否即為首批應登錄之待決存量

**Steward 決定**：〔　　　　　　　　　　　　　　　　〕

### Q6（M4）三指標 vs 四類存量之對應
ID.51 列三指標、L7.26 列四類（多列 WM.35 unmapped 為獨立類）；ID.51(c) 文內同時涵蓋 WM.15 與 WM.35。
* 暫採＝獨立成節（M4）呈列，並於 (c) 家族下併述
* 待裁＝是否應合併為單一指標，或 L7.26 之四類拆分即為權威口徑

**Steward 決定**：〔　　　　　　　　　　　　　　　　〕

### Q7（全體）門檻值
`RULING-2026-039` 五.3 明示「門檻數值不現寫」，且 L7.26 末句將門檻登錄歸 Threshold Registry（L7.45）。本器**只報數、不判 PASS/FAIL**，未自訂任何門檻。
* 待裁＝是否於 10-14 併審時開始登錄門檻，或續 DEFER

**Steward 決定**：〔　　　　　　　　　　　　　　　　〕

### Q8（全體）KS.83(i)(a) 之射程
KS.83(i)(a) 使「未解析存量＞0」之 Identity 其 Knowledge 完備性**不得高於 E1**，射程原文為「指涉該 Identity **或其所屬類型**之 unresolved backlog 非零」。
* 逐個體讀 → 受限者 **237**
* 逐類型讀 → `Security` 型 backlog 非零 ⇒ 該型全體受限 → **3,440**
* 本器兩者並陳，不代為裁定。**此裁定直接決定多少 Knowledge 被壓在 E1**，射程差 14.5 倍。

**Steward 決定**：〔　　　　　　　　　　　　　　　　〕

---

## §5 與 2026-10-14 併審之關係（誠實判，不誇大）

### 5.1 本量測**不**構成 KDO.4／LDO.4 之完整履行

L7.26 主文要求「物理量測、擷取**與快照儲存**」三事，並於 (a)(b) 課明確義務。逐項對照：

| L7.26 款 | 義務 | 本次交付 | 判 |
|---|---|---|---|
| (a) 前段 | 四類存量各具**可查詢之顯式清單** | M1／M4 可查詢；M2／M3 無載體 ⇒ 清單不存在 | **部分達成** |
| (a) 中段 | 各具**時間序列快照** | 本器唯讀、**未寫任何快照** | **未達成** |
| (a) 後段 | 擷取路徑不得由被量測構件自身支配 | 本器獨立連線、非由攝取管線觸發、唯讀 | **達成** |
| (b) | 快照留痕為 Observation，攜 provenance | 無快照即無留痕 | **未達成** |
| (c) | 量測不得為零；不可得推定不可知 | 四指標中二者誠實標 UNKNOWN；量測構件失效時全標 UNKNOWN（已驗紅） | **達成** |

⇒ **結論：本次交付為 KDO.4／LDO.4 履行之「其一部分」，非其全部。** 具體言之，達成「點時量測與擷取」與「保守處置」，未達成「時間序列快照儲存與 Observation 留痕」。後者屬**寫入**行為，需另案授權（新表 DDL ＋ 寫入路徑），不在本次唯讀範圍。

### 5.2 對 10-14 併審之意義

`RULING-2026-039` 五.3 之觸發條件為「LDO.4／LDI.31 實作落地**或** 2026-10-14 併審」。本次交付使 F2 備料 §5(b) 所載「量測實作仍 0 命中」之現況改變——但**改變的是「量測之可行性已被實證」**，而非「義務已結」。誠實表述應為：

* **可主張**：三（四）指標之量測**可行性已實證**；其中二項已產出真數字（237／88），二項經實證為**結構性不可量**（缺載體，非缺努力）。
* **不可主張**：不可主張 KDO.4 已履行；不可據此提早結清 10-14 日曆項（`RULING-2026-039` 六「無 Evidence 不提早結清」、`RULING-2026-042` 四「禁止假關」）。

### 5.3 併審日之選項（供 Steward 參考，非建議）

F2 備料 §5(d) 已載「〔hugo 裁〕併審日二擇——開實作議程或明示續 DEFER」。本呈案為該二擇提供之新事實為：**M2／M3 之不可量測係 schema 缺載體所致**，故「開實作議程」之最小範圍已可具體化為 Q3／Q5 兩項 DDL 決定，而非泛論。

---

## §6 所讀既有表 schema 與程式職責（#20 v1.39.0 雙落實）

### 6.1 所讀既有表（本次**零新表、零 DDL、零寫入**）

| 表 | 本量測所讀欄位 | 用途 |
|---|---|---|
| `entity_alias` | `alias_status`、`transaction_time` | M1 計數、M2 滯留時長 |
| `entity_registry` | `augur_id`、`entity_type` | M1 之 entity_type 分群（Q8 射程二讀） |
| `identity_claim` | （僅 `count(*)`） | M3 之「已宣告數」，**非**待決數 |
| `world_channel_binding` | `mapping_status`、`superseded_at` | M4 計數 |
| `information_schema.columns` | `column_name` | M2 判斷離開時點欄是否存在 |
| `pg_trigger` | `tgfoid`、`tgisinternal` | M2 判斷 `entity_alias` 是否 append-only |

**結果落哪張表**：**不落表**。本次為唯讀量測，輸出至 stdout（人可讀／`--json`）。快照持久化屬 L7.26(a)(b)，見 §5.1 未達成項，須另案。

### 6.2 程式職責

`scripts/report_identity_resolution_metrics.py`（單一檔，唯讀）：

| 函式 | 簽名 | 角色 |
|---|---|---|
| `is_unresolved_alias` | `(row) -> bool` | M1 個體層判準（純函式） |
| `count_unresolved` | `(rows) -> int` | M1 基數 |
| `completed_latency_measurable` | `(columns, has_state_history) -> bool` | M2 可導出性判準 |
| `censored_dwell_stats` | `(rows, now) -> dict` | M2 右設限滯留分佈 |
| `pending_identity_stock` | `(declaration_count, carrier_present) -> int\|None` | M3；**無載體必回 None** |
| `is_active_unmapped` / `count_unmapped` | `(row) -> bool` / `(rows) -> int` | M4 判準與基數 |
| `_fetch_all` | `(conn) -> dict` | 唯讀擷取（`SET SESSION READ ONLY`） |
| `build_metrics` | `(data\|None) -> list[Metric]` | 組裝；`None` ⇒ 全 UNKNOWN（L7.26(c)） |
| `_selftest` | `() -> int` | 紅綠自測，免 DB 免 API |

---

## §7 驗紅記錄（#35 回歸鎖三規則）

`--selftest` 共 19 條斷言，全部為**純函式餵真列形 fixture**（欄位與型別取自 live 表），**無任何字面／原始碼字串斷言**。提交前依 #35「凡新回歸鎖必先驗紅」跑 5 組突變，逐一親證會紅：

| # | 突變 | 預期紅 | 實測 |
|---|---|---|---|
| 1 | `is_unresolved_alias` → 恆 `False`（未解析判準弱化成恆 0） | M1 全組紅 | ✅ 4 條 FAIL |
| 2 | `pending_identity_stock` 無載體時回 `0`（冒充「待決為零」） | M3 紅 | ✅ 2 條 FAIL |
| 3 | `is_active_unmapped` → 恆 `True`（不看 superseded_at） | M4 全組紅 | ✅ 4 條 FAIL |
| 4 | `completed_latency_measurable` → 恆 `True`（謊稱可導出） | M2 紅 | ✅ 1 條 FAIL |
| 5 | `build_metrics(None)` 之 M1 報 `0`（違 L7.26(c)） | 失效模式紅 | ✅ 1 條 FAIL |

突變副本置於 scratchpad，未入 repo。基準跑：`--selftest` → **ALL PASS**（19/19）。

**唯讀性之下游絆線（#35(2)：不拆守衛去測，在守衛下游注入絆線）**：「本器唯讀」不以「原始碼無 INSERT 字樣」證明（#35(3) 禁字面斷言），改以行為實證——在與量測器**相同之連線設定**（`connect()` ＋ `set_session(readonly=True)`）下注入寫入絆線：

```
絆線 OK：寫入被擋 -> ReadOnlySqlTransaction cannot execute INSERT in a read-only transaction
對照 SELECT 可跑 -> 3503
```

寫入遭 PostgreSQL 交易層擋下（非應用層自律），且對照 SELECT 仍可跑（證明擋的是寫、非連線失效）。⇒ 唯讀性由 DB 強制，`readonly` 若被拿掉，絆線即會寫入成功而炸。

**判斷句自答**（#35）：
* 「這個綠燈量的是不是它宣稱在量的東西？」——是。M1／M4 之綠燈繫於「真列形 fixture 中恰 N 列符合判準」且同時斷言 `N≠0` 與 `N≠全體`，故恆 0 與恆真兩種弱化皆會紅（突變 1、3 已證）。
* 「這機制若壞了，會不會安靜變綠燈？」——不會。最危險之靜默失效模式＝「量不到卻報 0」，已由突變 2、5 雙向釘死。

---

## §8 五閘實測（2026-08-03）

| 閘 | 指令 | rc |
|---|---|---|
| 1 治權引用稽核 | `scripts/check_treaty_refs.py` | 0 |
| 2 執行指令矩陣 | `scripts/check_cmd_matrix.py` | 0（受檢 467 支／缺漏 0） |
| 3 #8 隔離 AST | `augur.audit.import_isolation.check_isolation` | 0 |
| 4 假斷言閘 | `scripts/check_false_assertions.py --gate` | 0（無新增） |
| 5 vendor 直綁閘 | `scripts/check_vendor_binding.py --gate` | 0（無新增） |

第 5 閘特記：本腳本讀 identity 表與 `world_channel_binding`，**零 vendor 表名字面**，故無新增命中。基線未紅，無須 stash 對照。

---

## §9 附帶發現（非本次任務範圍，據實登錄）

1. **retire 事件未傳導至 registry 狀態**：`identity_lifecycle_event` 有 **344** 筆 `event_type='retire'`（涉 344 個相異 `augur_id`），但 `entity_registry.status` 之 `tombstoned` 為 **0**、全部 3,503 列皆 `active`。retire 生命週期事件與 registry 狀態欄目前**不同步**。是否應同步屬 L3／L4 語義問題，本呈案僅登錄事實、不判。
2. **237 provisional 與 344 retired 零交集**（實查 `count=0`）：二集合互斥，故 M1 之 237 不含已退場實體。
3. **`entity_alias` 為六表中唯一未掛 append-only 觸發器者**：其餘 `identity_claim`／`identity_lifecycle_event`／`entity_attribute_version` 皆掛 `trg_*_append_only`。此不對稱即 M2 不可量測之根因（見 Q3）。

---

## §10 證偽條件

本呈案之結論若下列任一成立即被推翻，屆時應撤回或修正：

| # | 結論 | 證偽條件 |
|---|---|---|
| F1 | M1 ＝ 237 | 於 `entity_alias` 外另存在承載 `provisional`／未解析語義之欄位或表（則 237 為低估）；或 Q1 裁為讀法乙（則單位改變） |
| F2 | M2 完成時效不可導出 | 出示任一可還原「離開 provisional 時點」之載體（狀態史表、WAL 保留期內之邏輯解碼、稽核表等）；或 `entity_alias` 被掛上 append-only 且既有轉換已留痕 |
| F3 | M3 不可知 | 出示 DB 內任一「疑似同一候選」登錄載體；或 Steward 裁定「無候選登錄＝待決為 0」（則 L7.26(c) 之適用範圍須同步釐清） |
| F4 | M4 ＝ 88 | `world_channel_binding` 非 WM.35 unmapped 之唯一載體；或 `superseded_at IS NULL` 非「現行」之正確口徑 |
| F5 | 本交付非 KDO.4 完整履行 | Steward 裁定 L7.26(a)(b) 之「時間序列快照」與「Observation 留痕」不適用於本階段，或已由他處滿足 |
| F6 | 五個驗紅有效 | 任一突變副本實為與基準版行為等價（即突變未真正弱化判準）——可由重跑突變副本 `--selftest` 複驗 |

---

## §11 呈案人簽欄

* **草擬**：AI（self-reported，CLAUDE.md #32(a)；本呈案之文字與口徑判讀均為 self-reported，非權威確認）
* **量測數字來源**：`scripts/report_identity_resolution_metrics.py` live 實跑 stdout（#9(a)）＋ `psql` query（#9(b)）
* **Steward 裁定**：〔　　　　　　　　　　　　　　　　〕
* **裁定日期**：〔　　　　　　　　　　　　　　　　〕

---

## 附記：tombstoned 交叉澄清（主 session 補，2026-08-03）

本報告 §9 把「344 retire 事件 vs `entity_registry.status` tombstoned＝0（全 3,503 active）」列為附帶發現。
**同一張力另有一份記載**：G3 沙盒演練回報（2026-08-01）已將其列為「觀察（非修）」——
「DDL comment 稱『下市以 status=tombstoned 標記』，但 retire backfill **既定設計**＝retire 住 lifecycle 事件、
registry status 留 active（344 預鑄身皆 active；tombstoned **專屬去識別化路徑**）」；
且 `G3_identity_sandbox.md:201` 明載 tombstoned 之語義為**生產回退之前向補償**（＋lifecycle `correct` 事件、EVIDENCE_REQUIRED）。

⇒ 兩份報告對同一事實給了不同框架（**KDO.4 讀為「未傳導」缺口／G3 讀為「既定設計」**）。
主 session 現查：`entity_registry` 3,503 列全 `active`、零 `tombstoned`，兩份所述之**數字一致**，分歧在**語義歸屬**。
本附記僅登錄此分歧，**不裁**——`status` 之語義（下市是否應反映於 registry status，抑或僅存於 lifecycle 事件）
屬 identity 規格解釋，歸 Steward（§8.1）。列為 §Q 之外之第 9 題。
