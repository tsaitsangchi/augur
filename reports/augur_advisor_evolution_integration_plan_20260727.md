# 「誠實博學的我」對話平台 × 三軸自進化——整合計畫書

> **性質**：[I] 工具層計畫（#20 計畫先行／憲章 v1.39.0 計畫完整性）
> **日期**：2026-07-27｜**機器**：PC002-S1800（乙案正典機）
> **拍板狀態**：**已採納（`INTEG-P-yes`，2026-07-27）**——hugo 對話拍板（逐字）：「可以整合，也把Qdrant serving 考量進去」；並附指導原則（逐字）：「此專案接受很慢，但所有的能力提高要精準」→ 本檔全部驗收以**精確計數／凍結尺實測**為準、不用估算，速度永遠讓位給正確性。各階段執行序 C→A→B→D→E（A 待 H2/LLM 臂；E 待背景清空）。繕寫者＝claude、決策者＝hugo（§8.1 分立記載）。
> **上位 SSOT**：`augur_self_evolution_master_plan_v2_20260726.md`（下稱 v2）；本檔＝v2 §11.3 **賭注 B5 之人裁材料**（「LAIEVO 變強會惠及全系統？」——其前置「Phase 1 結果出來」已成立）。
> **治理框架**：`V2-AUTOADVANCE`（ENACTED 2026-07-27）R1–R7 適用於本檔全部自動段。

## 〇、一句定錨

平台與進化**已經共用同一副骨架**（同一 DB、同一 Ollama、同一 guard 精神）——本計畫不是把兩個系統焊起來，而是把**四條本來就該通的邊**逐條開通，且每條邊都以凍結尺實測、措辭閘把守、fail-open 可回滾。

**成功定義**＝每條邊有機械可驗的接線證據（evidence_level／guard 攔截率／人簽記錄）；**≠** advisor「變聰明」、**≠** 素養層碰預測管線、**≠** 增加任何確立級宣稱。

## 一、現況實查（2026-07-27，本機）

**平台側**：chat(:8090)／advisor(:8399, qwen3:8b, timeout 900s)／admin(:8500)／probability(:8600) 全 live；端到端實測「知識庫中無此內容＋guard pass=true」誠實拒答正常。檢索 SSOT＝pgvector 1,719,542 句嵌入（HNSW 3/3）；qdrant serving 55,861 點（舊庫時代、待重建）。`chat_message` 169 列／12 session（含 `guard_pass` 欄）。蒸餾管線四支（S2–S4）＋`advisor_distill_context/question` 表在。

**進化側**：凍結尺 `4183475c5089`＋四離線臂本機逐位元複現；FAIL_SIGN 上閘（volume_gini 實判）；對照臂 200 draws（偽陽率 9.0%/10.5%、GATE-raise 觸發 p95=2.643）；R3 demote 通道＋R2 四篩落地；serving pack `pp_3ab2efebb04e`（**晉升依據已作廢**、H2 重評待 LLM 臂）。

**關鍵斷點（B5 實測）**：serving pack 只接了 **local-llm MCP 的 ask profile**；**advisor（8b）不讀 pack、pack 在 4b 上評**——平台與 LAIEVO 之間目前是斷的。

## 二、四條邊（P-A〜P-D）＋明確不做

### P-A：LAIEVO serving pack → advisor（B5 的證據式解法）
把 v2 留給人裁的二選一（接審議引擎 vs 誠實限縮射程）改為**第三路：在 advisor 實際使用的檔位（8b）上以凍結尺實測 pack**——
1. `eval_local_model` 以 `--model qwen3:8b` 跑 `grammar`／`behavior`／`pack:<vid>` 三臂（凍結集、`model` 欄既有）；
2. `evidence_level(pack vs floor/mismatched/shuffled)` ≥ `weak` 且不遜於 grammar → 才接線；否則**誠實記「8b 零增益、不接」**（DESKTOP 實測 grammar=behavior=0.933 已暗示 pack 可能無增量——本檔預註冊此可能結局為合法結案）；
3. 接線機制＝advisor 殼讀**同一份** serving-pack 檔（fail-open：檔不在＝基線行為；退役＝刪檔即回滾，與 MCP `_serving_pack` 同約定、#12 不另造）；
4. 晉升人簽 P5.W2 不變；R4 auto-retire 適用（未勝零訓練基線自動退）。

### P-B：chat 真實問答 → 進化燃料（部署域礦脈）
v2 §0.5 實證教材 87% 是文獻 metadata；而 chat 的真實使用軌跡正是部署域分布——**guard 拒答（`知識庫中無此內容`）的問題＝天然 L3/L4 候選**；答得好的問答＝gold 候選。
1. 唯讀掃 `chat_message`（`guard_pass`、role 配對）→ 候選寫入新表 `advisor_probe_candidate`（§四 DDL；append-only＋誠實閘）；
2. **人審後**才進：eval 題（**僅入 RUBRIC 後的新 `set_id`**——凍結集 `4183475c5089` 永不加題）或 gold（`provenance` 記 chat 來源、P4.E7 標記）；
3. 隱私硬界：`owned_local` 語料不出本機、不入 git；含私有標記之 session 整段跳過。

### P-C：TWEVO brief/1 → advisor 情境註記（v2 §3.2 邊 3，前置已成立）
arena 已有 settled 列（4,128，本機獨立結算）→ 邊 3 開通條件達成：
1. 新 `export_evolution_advisor_brief.py`：從 arena／prodset **帳本事實**產 `brief/1` JSON（`claim_level ∈ {ledger_fact, paper, gap_debt}`、≤20 claims、**禁數值陣列**）；
2. 新 `validate_evolution_contract.py`（v2 C7）：schema 版本首欄、未知欄 fail-closed、產消兩端同一 validator；
3. advisor 注入為 system prompt 情境節（僅 `ledger_fact`）→ 平台能誠實回答「arena 現況？」而**不逾輸出契約**；
4. **guard 措辭閘擴充**：advisor 輸出端硬攔黑名單「可交易／確立級／已解凍／更準／更聰明」（C7 黑名單首次接到 live 對話面）。

### P-D：admin console → R6 週日 digest 頁
`:8500` 加唯讀 digest 頁（本週全部 `gate_ref='V2-AUTOADVANCE'` 自動決策＋pending hints）；hugo 於 console 批覆 hint（admin 密碼驗證＝比 CLI 更強的「是人」證據，§8.1 誠實條文照錄——仍為榮譽制＋事後偵測，不宣稱機械保證）。

### P-E：Qdrant serving 對齊新庫（檢索地基的維運邊）
DB 取代（2026-07-27）後 serving 落後 SSOT。**精確現況**（`export_qdrant_index.py` CLEAN 反差矩陣實測）：

| side/lang | CLEAN 放行 | serving 已同步 | 落差 |
|---|---|---|---|
| items/en（advisor 主用） | **78,419** | 55,861 | **+22,558 待補** |
| works/zh | 33,314 | 33,314 | ✓ 已齊 |
| items/zh | 0（147,196 全私有擋下） | — | ✓ 正確不外流 |
| works/en | 1,455,960 | **未建** | 既有範圍決策，本檔**不**擅擴（要建另拍） |

1. 重建＝既有 `export_qdrant_index.py --side items --language en`（工具在、零新碼；私有 `local_private` 硬擋不外流，憲章 v1.36.0）；
2. **排程化**：embed catchup（03:30）後接 serving 增量同步（`daily_green.py` 鏈或新 timer——採前者，#12 不另造鏈）；
3. 驗收（精準原則）：同步後 CLEAN 反差矩陣 items/en 落差＝**0**；`verify_qdrant_shadow.py` 影子比對綠；
4. 執行時機：待背景重活（驗收重跑／LLM 臂）清空後，不搶資源。

### 明確不做（本檔重申、不因整合鬆動）
| 不做 | 依據 |
|---|---|
| 素養層／advisor 任何產物 → 預測管線、`feature_values`、prodset | #8 雙閘、I2、界線-A、`augur_predict` REVOKE |
| chat 內容未經人審直灌 gold／題庫 | I5、P4.E7 |
| brief 帶 panel／數值陣列；brief 進凍結集或 gold | v2 §3.2 邊 3 明禁 |
| pack 接審議引擎 | v2 §7 前置（82 件 escalation 未清）未達成 |
| advisor 答預測問題逾「幅度級」 | 靈魂 v1.8.0／憲章 v1.45.0 輸出契約 |

## 三、(a) Table schema（v1.39.0）

**所讀既有表**（唯讀）：`chat_message(message_id, session_id, role, content, guard_pass, created_at)`／`chat_session`／`local_model_version`／`local_model_eval_item`／`local_model_eval_run`／`direction_arena_prediction`（settled 事實）／`evolution_production_feature_set`／`evolution_evidence_run`（ctrl 證據）。

**結果落點**：P-A→`local_model_eval_run`（既有，`model='qwen3:8b'` 列）＋serving-pack 檔；P-B→新表（下）；P-C→brief 檔（path+hash，入 LAI ledger `briefs_in` 待 Phase 5 表活）；P-D→零寫入（唯讀渲染；hint 批覆寫 `evolution_hypothesis_hint.decision`）。

**新表 DDL**（唯一新表；`migrate_advisor_probe_ddl.py` 落地、冪等）：
```sql
CREATE TABLE IF NOT EXISTS advisor_probe_candidate (
    probe_id      BIGSERIAL PRIMARY KEY,
    source_kind   TEXT NOT NULL CHECK (source_kind IN ('chat_decline','chat_ambig','chat_gold')),
    session_id    BIGINT NOT NULL,
    message_id    BIGINT NOT NULL,
    question      TEXT NOT NULL,
    answer        TEXT,                          -- gold 候選才有
    dedup_key     TEXT NOT NULL UNIQUE,          -- sha256(question 正規化)[:16]
    review_status TEXT NOT NULL DEFAULT 'pending'
                  CHECK (review_status IN ('pending','approved_eval','approved_gold','rejected')),
    reviewed_by   TEXT, reviewed_at TIMESTAMPTZ,
    contains_private BOOLEAN NOT NULL DEFAULT false,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
-- 誠實閘:DELETE/TRUNCATE 拒(同 honesty_delete_only_guard);review_status 單向前進 trigger
```

## 四、(b) Python 程式規畫（v1.39.0）

| 檔 | 動作 | 職責／簽名 |
|---|---|---|
| `scripts/eval_local_model.py` | **改** | 加 `--model <tag>`（預設現行 4b）；run 落 `model` 欄既有，跨 model 比較沿用 same_scale fail-loud |
| `scripts/serve_advisor_openai.py` | **改** | ① serving-pack 檔讀取（fail-open、僅 `INTEG-A-go` 後且 8b 實測過門）② guard 黑名單擴充（5 詞硬攔）③ brief 情境節注入（僅 ledger_fact） |
| `scripts/mine_advisor_probes.py` | **新** | 唯讀掃 chat → 寫 `advisor_probe_candidate`；`--dry-run`／`--run`／`--selftest`；私有 session 跳過 |
| `scripts/migrate_advisor_probe_ddl.py` | **新** | 上表 DDL＋trigger，冪等 |
| `scripts/export_evolution_advisor_brief.py` | **新** | 帳本事實→`brief/1` JSON＋hash；零數值陣列斷言 |
| `scripts/validate_evolution_contract.py` | **新** | C7：brief/1 validator＋措辭黑名單；`--file`／`--scan`；產消共用 |
| `scripts/serve_admin_console.py` | **改** | digest 唯讀頁＋hint 批覆 POST（寫 `decision`、`decided_by='hugo@admin-console'`） |

全部新增入口首次提交即含執行指令矩陣＋`--selftest`（#18/#29；`check_cmd_matrix` 射程內）。

## 五、分階段・驗收・回滾・停損

| 階段 | 前置 | 驗收（機械） | 回滾 |
|---|---|---|---|
| **A**（pack→advisor） | `INTEG-A-go`＋H2 重評完＋8b 三臂跑完 | 8b `pack` 臂 `evidence_level≥weak` 且 ≥grammar 才接；advisor 讀檔後回歸測試（`verify_advisor_regression.py`）綠 | 刪 pack 檔＝即回基線（fail-open） |
| **B**（chat 礦脈） | `INTEG-B-go` | miner `--dry-run` 列數＝實寫數；私有 session 零洩漏（斷言）；候選僅入新 set_id | 表 append-only、不動既有集 |
| **C**（brief＋措辭閘） | `INTEG-C-go` | validator rc=0；guard 攔截測試（5 黑名單詞注入→全攔）；brief 零數值陣列 | 移除 system prompt 節 |
| **D**（digest 頁） | `INTEG-D-go` | 頁面唯讀斷言（GET 零寫入）；批覆寫入與 CLI 同一 decision 路徑 | 下架路由 |

**停損**：任一階段連 2 輪驗收紅→ 該階段 halt、不阻他階；P-A 若 8b 零增益→誠實結案「不接」（**這是合法終局，不是失敗**——B5 賭輸的樣子）。

## 六、人閘與拍板碼

`INTEG-P-yes`（採納本檔）→ `INTEG-A-go`／`INTEG-B-go`／`INTEG-C-go`／`INTEG-D-go`（可同批拍、執行序 A→C→B→D）。
**仍須人**：pack 晉升簽名（P5.W2）、probe 候選審核（B 之 approved_*）、hint 批覆（H3）——皆已在 AUTOADVANCE 殘餘清單內，**本檔不新增人力負擔**（digest 頁反而降低）。

## 七、誠實天花板

1. P-A 最可能的結局是「8b 上 pack 無增量」——grammar 已 0.933，天花板本來就低；接線價值屆時歸零，本檔預先承認。
2. P-B 的礦脈規模現況僅 169 則訊息——燃料成長速度受限於真實使用量，不可為衝量灌合成問題（P4.E7）。
3. P-C 讓平台「能引帳本事實」，**不會**讓它懂市場——brief 是註記不是知識。
4. 整合不改變 F/P/A 的量測邊界：A 軸仍只證行為類別（RUBRIC 前）。

## 八、30 分鐘閱讀地圖

趕時間：§〇＋§二（四條邊＋不做）＋§五（驗收）。要 schema/程式細節：§三/§四。B5 背景：v2 §11.3。
