# 五軸自進化——逐步執行計畫書（2026-07-31 夜）

> **性質**：執行計畫，非治權提案。凡標【Steward】者為呈案、AI 不代決。
> **依據**：本日 9 路平行審議（`wf_7a33c928-aaf`）＋主 session 逐項親驗。
> **前提變更**：`V2-SUNSET-r2` 已於 19:45:26 經 Steward 親簽裁 `evaluated_pass`（basis=R1）
> ⇒ **三軸續命**、落日壓力解除。本計畫據此排序：不再以「趕在期限前」為驅動，
> 改以「**先讓量測可信，再談產出**」為主軸。

---

## 一、現況（21:30 實查，非估算）

| 軸 | 帳本 | 狀態 |
|---|---|---|
| **tw**（台股預測） | `evolution_iteration_ledger` 4 輪 | **1 輪 running**：`tw-20260728-r01`，I3 進行中 **20/37 features**、3h11m |
| **raw**（資料覆蓋） | `raw_evolution_iteration_ledger` 1 輪 | 週六 09:00 cron（**明早**）；今日已補 kill switch |
| **lai**（本地 AI） | `local_ai_iteration_ledger` **0 輪** | 從未跑過；量尺可疑（零知識 robot 臂過地板） |
| **sim**（模擬方法） | `simulation_method_registry` **0 列** | 專章已生效，但候選寫不進去（registry 空＋FK） |
| **PME**（哲學↔市場） | 即 tw 之 I3 所跑之 `--local-gates` | 與 tw 共用車道，非獨立軸 |

**阻塞物**：殭屍 `evolution_run` **10 筆**（其中 **4 筆為本人回歸鎖探針所造**，21:01:38）、
未清 `deferred` **6 筆**（同上，4 筆為探針）、`pending_auto` **67 筆**、
`feature_sign_check` **0 列**（表今日剛建）。

**唯一真瓶頸**：heavy slot 單槽。五軸共用，I3 獨佔中。

---

## 二、今日已完成（本計畫之地基，不重複做）

| commit | 內容 |
|---|---|
| `97de39b` | 逾時落帳假修（bytes）／人裁不被覆寫（machine_note 分欄）／KH5-6 逐 item |
| `21a10b0` | cron 三行漂移回寫＋兩個假綠＋可當閘之 `--check` |
| `7397281` `1f8d56a` | raw／tw driver 補 kill switch ⇒ **三軸「停機實為照跑」補齊** |
| `04ad288` `30eb063` | 週報 (b) 兩要件合取＋期限改讀 DB；射程 all_active（Steward 裁） |
| `9730dfe` `37a3e37` | `feature_sign_check` 建表＋符號尺 `--record` |

---

## 三、逐步執行（依相依性排序；並行組以 ‖ 標記）

### W1 — 今晚，零介入（自動）

**W1-1｜等 I3 完成。** 20/37、9.4 分/feature ⇒ 推估 **00:07 前後**（此外推今日錯過兩次，不當承諾）。
**W1-2｜23:00 cron 自動接手結輪。** 該 cron 帶 `--slot-wait 10800`（3h），I3 釋放 slot 後接手跑
I4→I9（實測合計約 2 秒）再 `--close`。**你什麼都不用做。**

> ⚠ 結輪時 `compare_gain` 會回報有增益，來源＝`prodset_delta`（1→2）——**那個 2 是 07-29 手動搬的**，
> 非 TWEVO 掙得。已於 `_snapshot` 分開引擎輪與人工紀錄，但 `prodset_delta` 之增益基準本身未改
> ⇒ 【Steward】是否把它限縮為「source_run_id 屬本輪」才算數。
> ⚠ I5 **不會 APPLY**（`apply_allowed=false`、cron 無 `--allow-apply`），`cycle_position_252d`
> 停在 `pending_auto`——正確，符號檢查尚未跑過。

### W2 — 明早，可三組並行 ‖

結輪後 slot 釋放。以下三組**互不共用車道／表**，可同時跑：

| 組 | 動作 | 車道 | 層級 |
|---|---|---|---|
| **‖A** | 對兩顆現役跑符號尺並落帳：`verify_sign_consistency.py --run --record --features inst_cumflow_position_120d,lending_fee_rate_mean_20d` | CPU（重算 as-of IC）**須 slot 空閒** | AI 可為（唯讀＋只寫 sign 表） |
| **‖B** | 清殭屍與 deferred（含本人探針之 4+4 筆） | 無 | 【Steward】寫帳本 |
| **‖C** | RAWEVO 週六 09:00 cron 自動跑（今日已補 kill switch，首次受閘保護） | 無（庫內唯讀） | 自動 |

**‖A 完成後**週報 (b) 之訊息會由「未通過/未檢」轉為逐顆 verdict——**這是 (b) 第一次可機械查證**。

### W3 — G-SIGN 升嚴【Steward】

**前置**：W1 結輪 ∧ W2-‖A 完成（否則加了閘也沒有紀錄可查）。

同一批四件，缺一不可：
1. `GATE_IDS` 加 `"G-SIGN"`（`all_gates_green` 綁 `may_apply`，是**單一判準住所**——
   不得改放 APPLY 腳本，那會開第二個閘的住所＝#12 之病）
2. `evaluate_g_sign()`：複用 `judge_sign`／`build_sign_rows`，**同時**寫 `gate_json` 與 `feature_sign_check`
3. **不得動 `FAIL_SIGN` 字串**——R3 除役通道（`may_apply` 之 demote 分支）依賴它
4. `DEFAULT_GATE_CONFIG` 增 G-SIGN 參數並納入 `config_sha256`

**blast radius（實數）**：`pending_auto` **67 筆**會因缺 key 而 `all_gates_green=False`，
須下一輪重評。cron 無 `--allow-apply`（0 行）故不會有東西突然停擺，但這不是零影響。

**時機硬約束**：**不得於輪進行中改**——`config_sha256` 會與人簽 baseline 不符，
且同一輪內出現兩種標準判出來的列。

### W4 — 量尺可信度（本計畫真正的主軸）

SUNSET 已 pass，壓力解除，**這是現在最該做的事**。四個未修假綠，依「不修會怎樣」排序：

| 項 | 現況 | 層級 |
|---|---|---|
| **LAIEVO 量尺** | 零知識 robot 臂過地板 ⇒ 任何 lai 分數目前無證據力；`local_ai_iteration_ledger` 0 輪 | 【Steward】改尺屬升嚴 |
| **`validation_evidence` 5 條 manual** | 對紅燈永久免疫（2 條 `last_verified_at` 為 NULL） | 【Steward】加有效期＝新判準 |
| **`constitution_lint report`** | 7/7 PASS 量的是「文件有無引到條號」非義務落地 | AI 可為（加射程標示） |
| **OCV** | 全 repo 僅 1 處註解、**零機械實作**，而 L6.16 明文要求可機器擷取 | AI 可為（最小可行分量） |

### W5 — sim 軸開張

專章已生效但 registry 0 列＋FK ⇒ 候選寫不進去。詳見
`reports/augur_local_ai_sim_evolution_impl_plan_20260731.md`。**須先過 W4 之量尺工作**，
否則又是一條「跑得動但量不準」的線。

### W6 — 基礎設施債（不進 slot，隨時可做）

- **備份單點**：全機**只有一顆實體磁碟**（`WDC WDS100T2B0C`；`/dev/sdd` 為 C 碟上之 vhdx、
  `/mnt/c` 同碟）⇒ **本機無法解**。唯一真異裝置＝公司 NAS，但庫含 `owned_local` 私有全文
  與 FinMind 授權資料，放全網域可 Modify 之儲存與授權前提衝突【Steward】。
  **零定期備份機制**（12 條 cron 無任何 `pg_dump`）。
- **P3 identity 六表從未建立**（碼在、DDL 在、表不在）；元憲章 §1.3「沒有 Identity 不允許
  Knowledge」在本機**反向成立**（`knowledge_item` 285,179 列）。
- **KH**：13.8 萬件無原文，其中約 7.9 萬件從未嘗試抓取、約 1.39 萬件 license 永久擋住（誠實終態）。

---

## 四、對應 table schema（#20 要件）

**新表**：本計畫不再建新表（`feature_sign_check` 已於 `9730dfe` 建；DDL 全文見該檔）。

**所讀既有表**：

| 表 | 用途 | 本計畫之落點 |
|---|---|---|
| `evolution_iteration_ledger` | tw 輪帳 | W1 結輪；`steps_json` 之 I3 rc |
| `evolution_run` / `evolution_deferred_work` | 引擎輪／積壓 | W2-‖B 清殭屍 |
| `promotion_queue` | 候選×閘 | W3 之 67 筆重評；`gate_json` 加 G-SIGN |
| `evolution_production_feature_set` | prodset | (b) 之 active 計數；W2-‖A 之受檢母體 |
| `feature_sign_check` | 符號判定落帳 | W2-‖A 寫入；週報讀 |
| `evolution_prereg_gate` | SUNSET 閘 | 週報之期限來源（`04ad288` 起改讀 DB） |
| `evolution_kill_switch` | 三軸停機 | 今日已接線；W4 之 consequence 實作標的 |
| `principle_factor_map` / `factor_direction_ruling` | 方向來源 | 符號尺之 `direction_source` |

**結果落點**：W2-‖A → `feature_sign_check`；W3 → `promotion_queue.gate_json`；
其餘為 repo 檔案與報告，**不寫 DB**。

## 五、對應 python 程式規畫（#20 要件）

| 檔 | 角色 | 本計畫之工作 |
|---|---|---|
| `scripts/run_evolution_iteration.py` | tw driver | W1 由 cron 自動續跑；已補 kill switch |
| `scripts/verify_sign_consistency.py` | 符號尺（SIGN-B） | W2-‖A 執行；`--record` 已就位 |
| `src/augur/philosophy/evolution.py` | **判準單一住所** | W3 加 `GATE_IDS` 之 `"G-SIGN"` ＋ `evaluate_g_sign()` |
| `scripts/apply_evolution_promotions.py` | APPLY | W3 **不改**（閘住 evolution.py；此處只消費） |
| `scripts/report_triple_evolution_week.py` | 三軸週儀表 | 已改；W2-‖A 後其 (b) 首次有實質內容 |
| `scripts/drain_deferred_work.py` | 積壓補跑 | W2-‖B 之工具；timer 目前**已停**（今日 C1 前置） |
| `scripts/migrate_feature_sign_check_ddl.py` | 落帳表 | 已 apply；`--check` 可查覆蓋 |
| `scripts/run_raw_evolution_iteration.py` | raw driver | W2-‖C 自動；已補 kill switch |

**新增程式**：W3 之 `evaluate_g_sign()` 為 `evolution.py` 內新函式（非新檔）。
W4 之 OCV 最小實作若成案，將為新 script，屆時須含 #29 指令矩陣、`--selftest`、無參數 graceful。

---

## 六、驗收（每步之機械判準）

| 步 | 驗收指令 | 通過條件 |
|---|---|---|
| W1 | `psql -tAc "SELECT status,jsonb_array_length(steps_json) FROM evolution_iteration_ledger WHERE iteration_uid='tw-20260728-r01'"` | `succeeded`；步數 >26 且含 I3 rc=0 |
| W2-‖A | `venv/bin/python scripts/migrate_feature_sign_check_ddl.py --check` | 兩顆現役皆有 verdict（非「無紀錄」） |
| W2-‖B | `psql -tAc "SELECT count(*) FROM evolution_run WHERE status='running'"` | 僅剩真正在跑者 |
| W2-‖C | `tail ~/logs/rawevo.log` | 週六 09:00 有輸出（該 log **從未存在過**，首次生成即為進展） |
| W3 | `psql -tAc "SELECT count(*) FROM promotion_queue WHERE gate_json ? 'G-SIGN'"` | 下一輪後 >0 |
| W4 | 各項另訂 | — |

---

## 七、必須停下問的點（AI 不代決）

1. **G-SIGN 升嚴**（W3）——改生產閘。
2. **殭屍與 deferred 之清理**（W2-‖B）——寫帳本；且其中 4+4 筆為**本人回歸鎖探針所造**，
   清理方式（標 `cleared_by='test-artifact'` 留痕 vs 刪除）請裁。
3. **`prodset_delta` 之增益基準**——是否限縮為 source_run_id 屬本輪。
4. **`TWEVO-APPLY-go`**——須在 G-SIGN 落地**之後**才考慮開。
5. **備份上 NAS**（W6）——外部副作用＋授權邊界。
6. **LAIEVO 量尺與 `validation_evidence` manual 有效期**（W4）——皆屬新判準。

---

## 八、本計畫之誠實限制

- **時間外推不可靠**：I3 完成時點我今日估錯兩次（22:50、00:30），現值 00:07 同樣是外推。
- **回歸鎖有代價**：以 `main()` 為標的之測試會在守衛拆除時真的執行——本日因此污染帳本
  8 筆（4 deferred + 4 evolution_run）。W2-‖B 之數字已含此污染。
- **本計畫由 AI 起草**，而 AI 是「程式續行則承擔更多工作」之一方（L6.18(c) 自我利益揭露）。
  W4 把「量尺可信度」排在產出之前，正是為了讓後續產出之宣稱可被獨立檢驗。
