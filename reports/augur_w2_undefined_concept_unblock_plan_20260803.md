# W2 後繼｜「十條卡概念未定義」解阻計畫 — 2026-08-03

> **位階**：[I] 計畫書（CLAUDE #20／憲章第六部計畫先行）。**非** [N]；不入憲、不偽稱已拍板。  
> **性質**：回應 Steward 新問「十條全部卡在『概念未定義』？請寫計畫書」。同時收斂先前「9/98 機械可自動配對」與並行研究「65/98 沒東西可對」——**單檔、勿另立打架計畫**（本目錄無既有 `augur_w2_mechanical_pairing_plan_*`；若後續另開，以本檔為 SSOT）。  
> **硬紀律**：FZ-keep（不打 FinMind／FRED）；M-T5 不搶 `heavy_slot`；本輪交付＝本計畫書，**不 commit／不 push、不實作大遷移**。  
> **上游證據**：`reports/augur_w2_source_column_reconcile_sampling_20260803.md`（§0／§1.4–1.5／§2／§3.3／§4）·`reports/augur_optimization_master_plan_20260803.md`（M-W2／M-W3／M-W4／M-W5／M-N7）·`reports/wm_channel_registration_draft_20260803.md`（23 概念草案＋Q-R1…Q-R9）·規格原文 WM.36（constitution-mcp）。  
> **數字時點**：抽樣報告＝2026-08-03 唯讀親驗；本計畫寫作當日 **live 複核**（見 §1.3）——若 DB 後續漂移，以 §0.2 探針為準。

---

## §0 一句判決（讀完可停）

**否——不宜讀成「十條全部僅卡概念未定義」。**  
Registry 層：**10/10** 皆 `concept_key IS NULL`／`mapping_status='unmapped'`（live 複核成立）。  
定案阻塞原文（抽樣 §2 結語）＝「概念未定義**或**結構性待裁」——**定案率 0/10** 為真，但主因須**分桶**，不可整包塞進「缺 concept」。  
真正瓶頸與母體一致：**先有概念／草案可映，才有欄位級配對與對帳**；9.2% 機械自動配對率是「有尺之後」的窄規則問題，**勿與概念覆蓋、唱讀對帳成功率混口徑**。

### 0.1 口徑表（四通道勿混）

| 口徑 | 定義 | 現況（2026-08-03） | 出處 |
|---|---|---|---|
| **A. 通道列** | `world_channel_binding` 現行列 | **98** | 抽樣 §1.1；`--survey` |
| **B. 世界概念覆蓋** | 通道已有可映之概念（mapped）／草案已擬／完全無 | **10** mapped ＋ **23** 草案 ＋ **65** 完全無＝98 | 抽樣 §1.5；本輪複核同值 |
| **C. 機械可自動配對** | 恰一非 PK 值欄且逐欄唱讀零問題 | **9/98（9.2%）** | 抽樣 §1.4；`--survey` 複核同值 |
| **D. 唱讀對帳成功** | catalog ∪ 實體表欄名／型別／PK 對得上 | vendor×實體：**2 欄／687 對不上（0.29%）** | 抽樣 §1.3 |

**禁混讀**：把 C 當「對帳失敗率」、把 D 的 88.6% 當「概念完成度」、或把「定案率 0/10」讀成「十條只缺 concept」——皆假口徑。

### 0.2 探針（Phase 0；零寫入、零 Claude usage）

```bash
cd /home/hugo/project/augur
venv/bin/python scripts/reconcile_channel_columns.py --survey | head -20
# 期望保底：source_column 已填：0/98；自動配對率 9/98；mapped 10/98

venv/bin/python - <<'PY'
import sys; sys.path.insert(0,"src"); sys.path.insert(0,"scripts")
from augur.core import db
SAMPLE=[7,11,31,37,50,62,65,80,93,97]
DRAFT23=[78,60,56,49,62,43,68,35,85,93,44,38,69,23,86,51,53,77,31,83,70,17,30]
with db.connect() as conn:
    with conn.cursor() as cur:
        cur.execute("SET statement_timeout='40s'")
        cur.execute("""SELECT binding_id, source_table, mapping_status, concept_key IS NULL AS no_key
                       FROM world_channel_binding
                       WHERE superseded_at IS NULL AND binding_id = ANY(%s)
                       ORDER BY 1""", (SAMPLE,))
        print("sample:", cur.fetchall())
        cur.execute("""SELECT count(*) FILTER (WHERE mapping_status='mapped'),
              count(*) FILTER (WHERE mapping_status='unmapped' AND binding_id = ANY(%s)),
              count(*) FILTER (WHERE mapping_status='unmapped' AND NOT (binding_id = ANY(%s))),
              count(*) FROM world_channel_binding WHERE superseded_at IS NULL""",
              (DRAFT23, DRAFT23))
        print("mapped, draft23, no_concept, total =", cur.fetchone())
PY
```

---

## §1 What／Why：十條精確所指與誠實分桶

### 1.1 「十條」是什麼

| 項 | 值 | 出處 |
|---|---|---|
| 抽樣方法 | 六桶分層 × 最大餘數配額 × `md5("w2:<binding_id>")` | 抽樣 §2 |
| seed／N | `--sample 10 --seed w2` | 同上 |
| binding_id | **7, 11, 31, 37, 50, 62, 65, 80, 93, 97** | 抽樣 §2 表 |
| 定案率 | **0/10**（無可直接寫入 DB 之 `source_column`） | 抽樣 §2 結語 |
| 原文阻塞措辭 | 「概念未定義**或**結構性待裁」 | 同上（**非**「全部僅概念未定義」） |

### 1.2 誠實分桶（AI self-reported 分類；軸＝抽樣 §2 逐條「阻塞／殘留」主詞）

> **軸 A（Registry 事實，可機讀）**：有無 `concept_key`。  
> **軸 B（定案阻塞主因，讀 §2 敘事）**：主阻塞屬哪一類。兩軸不可互代。

#### 軸 A｜Registry（live 複核 2026-08-03）

十條 **全部** `mapping_status='unmapped'`、`concept_key IS NULL`、`source_column IS NULL`。  
⇒ **若問「十條在 Registry 上都還沒掛概念鍵？」→ 是，10/10。**

#### 軸 B｜定案阻塞主因（讀抽樣 §2；self-reported）

| 桶 | 定義 | binding（表） | n | 說明 |
|---|---|---|---|---|
| **U0 概念空白需新建** | 無草案列、§2 須新提案 `concept_key` | **7** ConvertibleBondInfo；**37** JapanStockPrice；**50** GoldPrice；**65** OptionInstAfterHours；**80** SplitPrice；**97** FuturesDaily | **6** | 主標籤＝概念未立；多數**同時**夾帶結構待裁（見共病欄） |
| **U1 草案已擬、採認／粒度未裁** | 已在 `wm_channel_registration_draft` 建議鍵 | **31** BalanceSheet（`tw.financial_statement.balance`）；**62** Shareholding（`tw.foreign_ownership.stock`）；**93** BusinessIndicator（`tw.business_cycle_indicator`） | **3** | **不是「沒概念名字」**，是「名字草了但粒度／A.11／knowability 未裁」 |
| **U2 結構性不可展開為主** | 即使有概念名也不可誠實填欄 | **11** TaiwanFuturesTick（excluded／零落地） | **1** | 主阻塞＝W2-2（未落地通道射程）；填欄＝不可驗宣稱（違原則精華 #1） |

**共病（非互斥）**：U0／U1 多條同時撞 W2-1（多欄單 text）、W2-3／W2-5（同表雙概念／derived）、W2-6（全 PK 值欄偵測失效）、Q-R8（命名空間）。⇒ **解阻順序必須「概念決策佇列 → 結構形制 → 填欄」**，顛倒必返工。

#### 與 Steward 問句的對應答

| 讀法 | 答案 |
|---|---|
| 「十條全部卡在概念未定義？」若＝**定案主因皆為概念缺席** | **否**（至少 3 條草案已擬、1 條主因未落地） |
| 若＝**Registry 皆無 concept_key** | **是（10/10）** |
| 抽樣原文是否寫「全部卡概念未定義」 | **否**；寫的是「概念未定義**或**結構性待裁」 |

### 1.3 Live 複核摘要（本計畫寫作當日）

| 指標 | 複核值 | 與抽樣一致？ |
|---|---|---|
| `source_column` 已填 | 0/98 | ✓ |
| `mapping_status=mapped` | 10/98 | ✓ |
| 機械自動配對 | 9/98（9.2%） | ✓ |
| 概念覆蓋 (mapped, 草案23, 無概念, 總) | (10, 23, 65, 98) | ✓ |
| 十條 sample 皆 `concept_key IS NULL` | 是 | ✓（抽樣時未單獨印，本輪補機讀） |
| `world_concept` 身分列 | 6 | ✓（與抽樣 §7.1） |

> 複核指令＝§0.2；工具＝`scripts/reconcile_channel_columns.py --survey`＋上列 SQL。**未**重跑 10 條 AI 草擬段（耗時／定案率不因複核而變；草擬屬 self-reported）。

### 1.4 為什麼「解概念」優先於「提高 9.2%」

1. 母體 **65/98** 完全無概念（抽樣 §1.5）⇒ 對它們談 `source_column`＝**順序顛倒**（WM.36 欄 3＝「世界概念 → 通道位置」）。  
2. 抽樣定案 0/10 的外推結論：**AI 草擬 ~29 分不是關鍵路徑；裁決佇列才是**（§3.3）。  
3. B2 機械可配對最多再挖 1 條（binding 12 因 catalog_missing 被扣）——**對 65／結構 15 項待裁幾乎無槓桿**。  
4. 9.2% 是「單值欄＋唱讀乾淨」之**規則命中率**，不是欄位值對帳成功率（後者 vendor 側已 99.7%）。

---

## §2 解法階梯（分階段）

### Phase 0｜量測儀器固定（可先做；🟢）

| 項 | 內容 |
|---|---|
| **做** | 凍結本計畫 §0.1 四口徑；探針＝§0.2；抽樣十條 ID／seed 釘死 |
| **可選最小探針增補** | 在 `reconcile_channel_columns.py --survey` 增印一行 `concept_coverage=(mapped,draft23,none)`（純 SELECT；**非必做**，本計畫不實作） |
| **不做** | 不填 `source_column`；不改 mapped；不搶 heavy_slot |
| **驗收** | 同日兩次跑探針數字一致（或漂移有差分說明） |

### Phase 1｜概念補齊／註冊（主戰場；🟡→🔴）

**目標**：把「沒東西可對」變成「有可圈選之概念提案＋Steward 可決」。

#### 1.1 納入優先序判準（建議；Steward 可改）

| 優先 | 判準 | 理由 |
|---|---|---|
| P1 | **預測熱路徑／arena 已消費**之表 | 直綁清償與 10-14 硬期限直接相關（總計畫 D／M-W5） |
| P2 | 已在 **23 表草案圈選單**者 | 備料沉沒成本最高、差人裁即可動 |
| P3 | 高用量 dataset（features／train 引用頻次） | 執行層盤點；本計畫不另造用量榜（重用既有 vendor 直綁掃描／GROUNDing） |
| P4 | 其餘 unmapped | 可後置；**能抓 ≠ 該抓**——無消費、無世界事實錨者**不為提高覆蓋率而灌 concept** |

**排除／緩登（建議預設）**：

- **B0 未落地 excluded**（11 條，含 sample binding 11）：先裁 W2-2／是否屬 WM.35 射程，**禁止**為填欄而造假 concept。  
- **infra log**（`data_audit_log`／`pipeline_execution_log`）：非世界觀測；去留另裁，不進概念優先佇列。  
- **無 Identity 語義、僅供應商標籤堆砌**者：不登錄（對齊 WM.36 欄 1「具名，繫結 Identity」）。

#### 1.2 工作單元（對抽樣十條的對映）

| 單元 | 對象 | 動作 | 依賴 Steward |
|---|---|---|---|
| 1-A | U1＝31／62／93（＋草案其餘 20） | 呈圈選單執行；**不代簽** `decided_by` | Q-R1 形制＋各列圈選；93 另須 W2-4／A.11 |
| 1-B | U0 六條新提案 | 各產出「概念卡」：key／category／一句 Identity／建議欄集合／共病結構旗標 | Q-R8 命名；必要時跨市場軸 |
| 1-C | 母體 65 無概念 | 分批：先掃「是否已被 P1 消費」→ 提案 or 標 `out_of_scope` | 納入範圍裁示 |
| 1-D | U2＝11 等 B0 | **概念佇列暫停**；只產「射程裁決卷」 | W2-2 |

#### 1.3 「概念卡」最小欄位（文件／staging；尚未寫 DB 亦可）

```
concept_key | category(entity|event|state|relation|quantity)
| identity_one_liner | candidate_binding_ids | proposed_source_columns[]
| co_morbid(W2-*) | knows_consumption? | draft_ref
```

**禁假 concept**：不得用 vendor 表名充 Identity；不得為讓 `--survey` 變綠而 INSERT 空殼鍵；不得把 raw 列升格靈魂（`soul-vs-raw`）。

### Phase 2｜vendor↔concept／source_column 綁定規則擴張（🟡）

在 Phase 1 使「有概念可映」之後才做。

| 層 | 機械規則（可自動） | 人工策展（必人） |
|---|---|---|
| 單值欄 B2＋唱讀乾淨 | `auto_pairable`→建議 `source_column`（現 9 條） | 欄 1／5／權威／單位語意仍人裁（GoldPrice 先例） |
| 多值 B3–B5 | 枚舉值欄＋入／出建議 | 哪些欄屬該概念；是否拆第二 binding（W2-5） |
| 全 PK B1 | **必須先改值欄偵測器**（W2-6／Q-R7）後才談自動 | 哪些 PK 欄實為事實載體 |
| 形制 | — | **Q-R1** unmapped→mapped；(a) UPDATE vs (b) supersede+INSERT |
| 多欄承載 | — | **W2-1**：(a) CSV text／(b) 一欄一列／(c) 陣列 DDL |

重用：`scripts/reconcile_channel_columns.py`（唱讀／桶／auto_pairable）；`src/augur/catalog/world_concept.py`（`resolve`／`assert_mapped`）；草案親簽 SQL 範本（`wm_channel_registration_draft` §7）；**禁止**另寫第二套 Registry writer。

### Phase 3｜對帳本體與權威採認（🔴；＝總計畫 M-W5 走廊）

**前置硬閘**：M-W3（絞殺判準）／M-W4（列鍵）／Q-R1 未裁 ⇒ **不得宣稱 source_column 填滿＝WM.36 完成**（總計畫第 31 步警告）。

| 步 | 內容 | 誰 |
|---|---|---|
| 3-a | 有概念者填 `source_column`（依 W2-1 形制） | AI 備 SQL；hugo 親跑／親簽 |
| 3-b | `authoritative_binding_id`＋`decided_by` | **僅 hugo**（AI 不代打） |
| 3-c | 唱讀對帳修 catalog 漂移（vendor 僅 2 欄） | `build_catalog.py --db-only` 路徑（寫 DB，另授權） |
| 3-d | 機械配對率複測 | 僅作**有概念子集**之 KPI，不作全 98 唯一 KPI |

---

## §3 (a) Table schema

### 3.1 讀哪些既有表（不新建亦可開工）

| 表／視圖 | 角色 |
|---|---|
| `world_concept` | 身分：`concept_key` PK |
| `world_concept_version` | 版本內容：category、authoritative_binding_id、ts_semantics、knowability_rule、cross_market_axis、provenance、finality_predicate、decided_by／at、superseded_at |
| `world_concept_registry_current` | 現行 view（JOIN；**不可**當寫入目標） |
| `world_channel_binding` | 通道：concept_key、source_table、source_column、channel_role、mapping_status、provenance；CHECK `(mapped)⇔(concept_key IS NOT NULL)`；honesty guard |
| `column_catalog`／`dataset_catalog` | 欄名／型別／中文名／排除理由 |
| `information_schema.columns`／`pg_constraint` | live 實體 PK／型別（對帳尺） |

既有 DDL 住所：`scripts/migrate_world_concept_registry_ddl.py`、`scripts/migrate_world_concept_identity_split_ddl.py`（身分／版本拆表已落地；本計畫**預設不新遷**）。

### 3.2 結果落哪

| 產物 | 住所 | 時點 |
|---|---|---|
| 概念提案／圈選狀態 | `reports/` 草案＋（建議）Steward 問題帳／圈選紀錄 | Phase 1 |
| 身分＋版本列 | `world_concept` INSERT；`world_concept_version` INSERT | Steward 圈選＋Q-R1 後 |
| 通道映射 | `world_channel_binding` UPDATE 或 supersede+INSERT | 同左 |
| 欄位級 | `source_column`（形制依 W2-1） | Phase 3 |
| 權威採認 | `world_concept_version.authoritative_binding_id`／`decided_by` | Phase 3；hugo 親簽 |

### 3.3 可選新表／擴欄（僅草案；**未裁勿建**）

| 提案 | DDL 草案要旨 | 觸發條件 |
|---|---|---|
| **W2-1c** `source_columns text[]` 或子表 `world_channel_binding_column(binding_id, column_name, ordinal)` | 一概念多欄之正規化 | Steward 選 (c) 或 (b) 爆炸列不可接受時 |
| **M-W4／Q-R2** `row_selector`／`series_predicate text` | 表內列鍵（TAIEX／TXO） | M-W4 裁「series 識別碼含列鍵」為是 |
| **staging** `concept_proposal_staging`（JSONB＋provenance） | 批量提案待審、零直接寫 Registry | 若 65 條提案量大到需 DB 佇列（否則 reports TSV 即可） |

```sql
-- 僅示意；非授權執行
CREATE TABLE IF NOT EXISTS concept_proposal_staging (
    proposal_id   bigserial PRIMARY KEY,
    concept_key   text NOT NULL,
    binding_id    bigint REFERENCES world_channel_binding(binding_id),
    payload       jsonb NOT NULL,
    status        text NOT NULL DEFAULT 'pending'
                  CHECK (status IN ('pending','accepted','rejected','superseded')),
    created_at    timestamptz NOT NULL DEFAULT now(),
    decided_by    text,
    decided_at    timestamptz
);
```

**預設建議**：Phase 1 用 reports／圈選單即可；**staging 表非啟動條件**。

---

## §4 (b) Python 程式規畫（重用既有；禁重造）

| 檔 | 角色 | 本計畫用法 |
|---|---|---|
| `scripts/reconcile_channel_columns.py` | M-W2 唱讀／桶／auto_pairable／sample | Phase 0／3 KPI；可選印 concept_coverage |
| `src/augur/catalog/world_concept.py` | `resolve`／`load_registry`／`--check`／`--selftest` | 登錄後消費端驗證；**不改 resolve 語意除非 M-W3／Q-R2 裁後** |
| `scripts/migrate_world_concept_*.py` | DDL／identity split | **只 --check／--verify**；`--apply` 須另授權 |
| `scripts/compare_shadow_binding.py` | M3 影子 | M-W3 裁後才指望 green；本計畫不改判式 |
| `reports/wm_channel_registration_draft_20260803.md` §7 SQL | 親簽範本 | Phase 1-A／3 執行劇本 |
| **新建（若拍板後）** `scripts/propose_concept_cards.py` | 唯讀：吃 binding_id 清單→吐概念卡 TSV／md | 參數化、`--selftest`、指令矩陣；**零 API** |
| **不新建** | 第二套 reconcile／第二套 Registry ORM | 明示禁止 |

函式責任切分（拍板後實作時）：

- `enumerate_value_columns(binding_row, live_cols, pk)` — 抽出；並修 B1（W2-6）須另案驗紅（#35）。  
- `auto_pairable(...)` — **保持嚴格**；禁為提高 9.2% 放寬（突變 M4／M5 已證放寬＝假綠）。  
- `concept_coverage(conn, draft_ids)` — 純 SQL 三元組。  
- 寫入路徑：**不**包進日常 script 自動跑；僅 hugo 親簽 SQL 或明示 `--allow-apply` 閘。

---

## §5 元件 · 端點 · 工作量 · 可同步

| 元件 | 端點／入口 | 估時（執行層） | 可同步？ |
|---|---|---|---|
| 探針 | `reconcile_channel_columns.py --survey` | <1 min | ✓ 隨時 |
| 草案 23 圈選執行卷 | 既有 draft §7 | 備料已在；**人裁時間 n=0 不可估** | 與 M-W3／M-W4 呈案同步 |
| 抽樣 U0 六張概念卡 | 文件＋可選 propose script | ~1–2 h AI 備料 | ✓ 與 23 圈選文件並行 |
| 65 無概念分流（P1 消費掃描） | 重用 `check_vendor_binding`／既有直綁清單 | 0.5–1 d 唯讀 | ✓ 輕量 PG；不搶 M-T5 heavy |
| W2-1／Q-R1 形制裁決卷 | 短呈案 | 0.5 d | 與概念圈選**同批裁**為佳 |
| 填欄 M-W5 | 總計畫第 31 步 | 08-31 窗口；人簽另計 | 前置未齊則禁搶跑 |

**可先做（無需本計畫完整拍板）**：Phase 0 探針日常化；併表六項 W2-* 進草案 §6（文件工作）。  
**須拍板後才做**：任何 Registry 寫入、DDL、放寬 auto_pairable、B0 填欄。

---

## §6 Steward 必裁清單（本計畫最小集）

> 下列為**啟動 Phase 1 寫入／圈選執行**前建議必裁；完整 Q-R1…Q-R9／W2-1…W2-6 仍有效，不在此廢止。

### 必裁三條（回報用最小集）

1. **Q-R1 形制**：unmapped→mapped 採 (a) 原地 UPDATE 還是 (b) supersede＋INSERT？（未裁＝任何登錄 SQL 不得執行——草案 §7 原文。）  
2. **納入範圍**：65 無概念通道之登錄邊界——是否採本計畫 P1→P4＋「B0／infra 預設緩登」？A.11 對指標類（含 binding 93）採「一指標一概念」還是「單表單概念」？（W2-4）  
3. **W2-1 多欄承載**：`source_column` 用 (a) 分隔字串／(b) 一欄一 binding 列／(c) 改 schema？——決定 Phase 2／3 資料形狀與 67 條多值通道成本。

### 強烈建議同批（否則 U0／抽樣馬上再卡）

| 代號 | 題 | 卡住誰 |
|---|---|---|
| W2-2 | 未落地通道可否登錄欄位映射 | sample 11 ＋ B0×11 |
| W2-6／Q-R7 | 全 PK 表值欄怎麼認 | sample 97 ＋ B1×10 |
| Q-R8 | 非 `tw.` 命名空間 | sample 37／50 等 |
| M-W3 | 權威表徵即 vendor 表時之合規判準 | **整條 M-W5／10-14** |
| M-N7 | vendor 直綁權威尺 | 清償配額與優先序 P1 度量 |

---

## §7 驗收與雙 KPI（配對率不是唯一 KPI）

| KPI | 定義 | 目標（建議） | 非目標 |
|---|---|---|---|
| **K1 有概念覆蓋率** | `(mapped + Steward已圈選待寫入) / 納入範圍分母` | 納入範圍內 → 提案覆盖 100%；mapped 隨人裁上升 | 強求 98/98（含 B0／infra） |
| **K2a 有概念者之機械配對成功率** | `auto_pairable` ∩ 已有 concept_key | 監視；允許仍低（多值本質） | 用放寬規則刷高 |
| **K2b 有概念者之人工／圈選配對完成率** | 已填合法 `source_column`／已圈選欄集合 | Phase 3 | — |
| **K0 定案率（抽樣復測）** | 同十條可寫入比例 | 結構裁後應 >0 | 用假 concept 換 >0 |
| **對帳 D** | vendor 唱讀對不上欄數 | 維持 ≈2／687 或修 catalog 後 →0 | 與 K1 混報 |

**失敗態（紅）**：K1 上升但大量 concept 無 Identity／無消費錨；或 K2a 上升但突變 M4／M5 會綠＝假綠。

---

## §8 禁做（明示）

1. **假 concept**：無 Identity、無觀測錨、僅為覆蓋率／9.2% 美化而 INSERT。  
2. **放寬 `auto_pairable` 至假綠**（無視多值、無視唱讀問題）。  
3. **打 FinMind／FRED 補洞**（FZ-keep）；預測／概念登錄走庫內 as-of，不解凍。  
4. **把 raw／整表升格靈魂**；概念＝關係與 Identity，非觀測列本身。  
5. **AI 代填 `decided_by`／代簽權威**。  
6. **Q-R1／W2-1／M-W3 未裁即大規模寫 `source_column` 或宣稱 WM.36 完成**。  
7. **對 B0 未落地表登錄不可驗之欄位映射**。  
8. **搶 M-T5 `heavy_slot`**；本弧為輕量／裁决向。  
9. **重造**第二套 reconcile 或 Registry 寫入堆疊。

---

## §9 風險 · 非目標 · 與總計畫銜接

| | |
|---|---|
| **風險** | 人裁速率不可估（抽樣 n=0）；23 圈選與 65 分流並行時命名衝突；選 W2-1(b) 列數膨脹至 ~472 |
| **非目標** | 本計畫不完成 M-W5 98 填滿；不裁定 M-W3 甲乙丙；不解凍 API；不升治權 [N] |
| **上游** | M-W2 抽樣＝已完成（第 25 步） |
| **下游** | Phase 1–2 備料 → M-W5（第 31 步）；結構裁 → M-W3／M-W4 |
| **正交** | 9.2% 機械配對＝Phase 2 子題；唱讀 0.29%＝catalog 維運子題 |

---

## §10 建議第一階段下一刀（拍板後）

1. Steward 先裁 **§6 必裁三條**（Q-R1／納入範圍＋A.11／W2-1）。  
2. AI **不寫 DB**：產出（i）23 草案執行順序表（標 U1 三條優先）；（ii）U0 六張概念卡；（iii）B0／infra 緩登名單一行表。  
3. 再開第二刀：依圈選結果跑親簽 SQL（hugo），再用 §0.2 探針驗 K1 變動。

---

## §11 參考錨點（trace）

| 宣稱 | Trace |
|---|---|
| 定案率 0/10；阻塞＝概念未定義**或**結構性待裁 | `augur_w2_source_column_reconcile_sampling_20260803.md` §2 結語 |
| 10 binding IDs | 同檔 §2 表；§6 復現 `for b in 7 11 31…` |
| 65 無概念／23 草案／10 mapped | 同檔 §1.5；本計畫 §1.3 複核 |
| 9/98＝9.2% 機械自動配對 | 同檔 §1.4；`--survey` |
| vendor 對不上 0.29% | 同檔 §1.3 |
| WM.36 七欄／欄位級／不得直綁 | constitution-mcp `WM.36`；`specs/WORLD-MODEL-SPECIFICATION.md:344+` |
| M-W2 只抽樣不填欄；M-W5 需 M-W3／M-W4 | `augur_optimization_master_plan_20260803.md` 第 25／31 步 |

---

*完。請 Steward 對本計畫拍板／改優先序／暫擱（見會話 AskQuestion）。*
