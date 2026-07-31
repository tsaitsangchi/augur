# SUNSET (a) 裁定之證據整備 [呈案，非裁決]（2026-07-31）

> **性質**：`AUGUR-MC v1.6 §8.1` 條文解釋權**專屬 Constitution Steward**。本檔為證據整備與論證呈報，
> **不構成裁決**，亦不得被引為裁決依據。AI 不得代判、不得寫 `evaluated_at`／`result_snapshot`。
>
> **產出方式**：7 路平行對抗審議（`wf_1dfa10d6-854`：兩造辯護／第三路徑／治權機制／停損目的／公平審判＋1 對抗合成），
> 其發現全部經主 session 以 live DB 與 repo 逐項親驗後始錄入本檔。未親驗者一律標 UNKNOWN。
>
> **本檔記錄一次立場翻轉**：主 session 於審議前之建議為「(a) 達成」，審議後經親驗**推翻自己**。
> 翻轉之依據與原論證之缺陷一併留存（#15 判死留檔），不粉飾為一路正確。

---

## 一、標的

`evolution_prereg_gate` 之 `V2-SUNSET-r2`（2026-07-31 19:05:51 hugo TTY 親簽；
`criteria_sha=2d2b9f5d7c93…`；deadline 已 GATE-raise 至 **2026-07-31**；`evaluated_at` 仍 **NULL**）。

凍結 criteria 逐字（三選一，達成任一即續命）：

```
期限：2026-07-31
(a) arena 至少結算一批且方向門有可讀數；或
(b) evolution_production_feature_set active 由 2 成長，且每一新成員通過符號一致性檢查；或
(c) LAIEVO 有任一臂在 F@L1 上同時勝過 floor 與 mismatched，且該結論可被獨立重跑複現。
全未達成：三軸整體停止、帳本封存、不得換 trigger_code 重開。
```

---

## 二、(a) 之三種讀法（原「原文 vs 程式」二分係誤framing）

| | 讀法 | 今日判定 |
|---|---|---|
| **R1** | 任一 `direction_gate` 列有可讀之數 | **達成** |
| **R2** | **arena 之**方向門產出可評之數 | **未達成** |
| **R3** | 判定程式：`status='evaluated_pass' > 0` | **未達成** |

**R2 與 R3 今日結論相同**，因為 arena 門一個都沒被評估過——二者之差集（「arena 門已 evaluate 但 verdict=fail」）**筆數為 0**。
故「該程式那把較嚴的尺從未走過 GATE-raise」之程序爭點，在今日事實下**翻不動結論**（但制度缺口仍在，見 §五）。

### 2.1 R1 之三項反證（皆親驗）

**(i) arena 門零可讀數。**

```sql
SELECT gate_id, status, evaluated_at, result_snapshot FROM direction_gate WHERE gate_id LIKE '%arena%';
```
→ `dgate_arena_chronos_5`／`own_daily_5`／`own_stack_20`／`own_stack_40`／`own_stack_82`／`timesfm_5`
共 6 列，**`evaluated_at` 與 `result_snapshot` 全部為 NULL**。

**(ii) 那 12 個有數字的 `evaluated_fail`，沒有一個是 arena 門。**

| gate_id | evaluated_at | 性質 |
|---|---|---|
| `dgate_H_20`／`H_40`／`H_82`／`H_120`／`D_1`／`D_5`＋4 個 `_v2` 變體 | 2026-07-11 | **已二次證偽判死之舊方向門** |
| `dgate_replay_momentum_20_5`／`dgate_replay_mc_bootstrap_5` | 2026-07-30 | **replay 軌**（`n_panels=2798`），非 arena 軌 |

**(iii) 拍板當日之凍結基線已明文否定 R1。**
`audits/V2-ADOPTED-SUNSET-20260726.md:32`（同檔尾載 `criteria_sha256=65eda893…`）逐字：

> 條件 (a)：**半達成**——arena 首批 4,128 列已結算（07-26）；「方向門有可讀數」**未達**（cluster=2／需 60；每日出單 cron 已掛、07-27 起走）。

而上表那 10 個 07-11 之門**連同其非空 `result_snapshot`，在 2026-07-26 簽字當下即已在庫**。
⇒ 簽字者在明知該等數字存在之情形下仍判 (a) 未達；其當下語意顯為
「**arena 餵養之方向門累積至足夠 cluster 而產生讀數**」，非「表裡任一列有數字」。

**(iv) R1 使停損閘結構性失效。** 依 R1，(a) 於 `preregistered_at`（2026-07-27 15:30:36）之瞬間即已成立
（該時點前之 `evaluated_fail` ＝10 筆、已結算 arena 列＝4,128 筆），且因舊 snapshot 為不可變史料而**永遠成立**。
一條簽下去即成立且不可能失敗的續命條件，與其不可逆重罰之條文不自洽。

> **原論證之缺陷（留檔）**：主 session 原持 R1 並稱之為「凍結原文字面」，實則 R1 係將主詞由
> 「arena 之方向門」放寬為「任一 direction_gate 列」之**第三種讀法**，非原文之自然解。
> 該錯誤之型態＝**未讀同批之凍結基線即宣稱掌握原意**；同批文件就在 `audits/` 內。

---

## 三、0/3 不等於「程式沒有產出」——三條件之失敗各有非假說性成因

### 3.1 (b)：合格候選存在，卡在一道從未打開的人閘（**本檔最具行動性之發現**）

```sql
SELECT feature, run_id FROM promotion_queue
 WHERE gate_json->'G-PROM'->>'verdict'='PASS' AND gate_json->'G-ECON'->>'verdict'='PASS';
```

→ **`cycle_position_252d` 自 run 11 起，於 run 12／15／16／17／18／19／20 每一輪皆雙綠**
（含 2026-07-31 晚正在跑之 I3）。其 run 20 之 `G-PROM` 證據：

```
hac_t = 3.5225   mean_ic = 0.08810   hit_rate = 0.78125   n_panels = 64
seed_deltas = [0.002162, 0.003305, 0.005495]   （三個 seed 全正）
checks = {hac_t: true, asof_ic: true, multi_seed_delta: true}
```

而 `evolution_production_feature_set` 之 `active` 為 `inst_cumflow_position_120d`、`lending_fee_rate_mean_20d`
——**`cycle_position_252d` 不在其中，從未被 APPLY**。

原因：`scripts/run_evolution_iteration.py:12-14` 之 I5 預設 `apply_allowed=false`；
放行須 `--allow-apply --gate-ref TWEVO-APPLY-go`，而**人閘碼 `TWEVO-APPLY-go` 由 hugo 親跑、driver 不代簽**。
該閘從未開啟。

⇒ **(b) 之失敗為治理吞吐失能，非程式無產出。**

**⚠ 未驗之前置**：(b) 尚要求「每一新成員**通過符號一致性檢查**」。`gate_json` 內查無該欄
（`G-PROM.checks` 僅 `hac_t`／`asof_ic`／`multi_seed_delta`）。**該檢查之實作位置與判準＝UNKNOWN**；
開閘前須先確認其存在且通過，否則即為「宣稱通過但無對應機制」之同型假綠。

### 3.2 (c)：部分歸因於今日始修之機械故障鏈

四晚零產出之因果鏈已於 2026-07-31 查明並修復（詳 commit `97de39b`）：
heavy slot 被 `run_philosophy_evolution --local-gates` 獨佔，該步實測需 **7-10 小時**
（645-720 s/feature × 37 mapped feature），而 `STEP_TIMEOUT_SEC` 原為 **7200s**
⇒ 每 2 小時被砍再由 `augur-drain-deferred.timer` 重啟，永動且零產出；
且 W0-0 之逾時捕捉原為**假修**（`TimeoutExpired.stdout` 為 bytes ⇒ `json.dumps` TypeError ⇒ 步仍落不了帳）。
今日修畢並停 timer 後，I3 為四晚來第一次真正在跑。

⇒ 於工具故障期間收集到之零產出，證明的是工具壞了。

### 3.3 (a)：arena 門從未被評估

見 §2.1(i)。非「評估後不合格」，是「未評估」。

---

## 四、結算在機械層之實際效果

| 項目 | 實查 |
|---|---|
| `evolution_kill_switch` | `global`／`tw`／`raw`／`lai` 四 scope **全 `clear`** |
| `run_evolution_iteration.py`（tw） | `kill_switch` 引用 **0 處** |
| `run_raw_evolution_iteration.py`（raw） | `kill_switch` 引用 **0 處** |
| `run_philosophy_evolution.py`（PME） | 引用 3 處 |
| 封存／halt 腳本 | **不存在** |
| 依 deadline 自動動作之 code | **無**（`report_triple_evolution_week.py` 唯讀印倒數，不寫 gate） |

⇒ 三軸有兩軸之 runner **根本不讀 kill switch**；「三軸整體停止、帳本封存」目前**只能停在文字上**。

**且終態不可逆**：`prereg_gate_no_goalpost` 對 `status IN ('evaluated_pass','evaluated_fail','superseded')`
之列拒絕**全欄 UPDATE**，連日後 supersede 補正亦不可能。
⇒ 將 r2 設為 `evaluated_fail`＝以最大不可逆性換取零機械效果。

---

## 五、結構缺口（獨立於本案，應另案處置）

**判準凍結了文字，未凍結解釋它的程式。** `prereg_gate_no_goalpost` 守 DB 列
（DELETE／終態列／`criteria_sha`），**守不到 `report_triple_evolution_week.py` 那把尺**——
該尺無 sha 錨、無簽核、無 trigger 覆蓋。今日因差集為空而未影響結論，但側門仍開著。

**另一洞**：`evolution_prereg_gate` 之非終態列，其 `criteria` jsonb 在 `criteria_sha` 不變之情形下
可被改寫而無紅燈（其餘三個 gate 族 trigger 皆有 `criteria::text` 比對保護，唯獨 prereg 沒有）。UNKNOWN 是否曾被利用。

---

## 六、呈報（Steward 裁）

**事實認定**：(a) 依 R2／R3 **未達成**；(b)(c) 亦未達成 ⇒ **0/3**。證據強度足以支撐。

**惟以下三點須與結論等重併呈**：

1. 三條件之失敗**各有非假說性成因**（人閘未開／機械故障／未評估），0/3 不等同「假說被證偽」。
2. 執行結算**無實質停止效果**（機制不存在）而**製造永久不可更正之終態列**。
3. r2 之期限係於今日 19:05:51 同一秒預登記並核准、自 10-31 壓縮 92 日；
   在原期限下 arena 達最低凍結門檻（36 clusters；現 6）為可及。

**最具行動性之單一步驟**：開 `TWEVO-APPLY-go`，讓連續十輪雙綠之 `cycle_position_252d` 進入 prodset
——(b) 即以**程式自身之實力**達成，不依賴任何對判準之重新解釋。
**前置**：先確認「符號一致性檢查」之實作與通過（§3.1 之 UNKNOWN）。

**自我利益揭露（`AUGUR-L6 v1.2` L6.18(c)／CLAUDE #32(a)）**：本檔由 AI 起草，
而起草者即今日修復該等故障、且於程式續行時將承擔更多工作之一方。
對抗審議之 critic 對「裁 0/3 但不執行」提出之自我批評——
「若停損閘觸發時後果從不執行，即證明一個夠會講話的 agent 永遠找得到延後的理由」——
**對本檔成立**，一併呈報，不予淡化。

---

## 七、對應 table schema（#20 要件）

**本檔為純分析，不產新表。** 所讀既有表與其相關欄位：

| 表 | 讀取之欄位 | 用途 |
|---|---|---|
| `evolution_prereg_gate` | `gate_id, axis, criteria(jsonb), criteria_sha, status, preregistered_at, approved_by, approved_at, evaluated_at, result_snapshot, note` | 閘之凍結文字、簽核與終態 |
| `direction_gate` | `gate_id, status, evaluated_at, result_snapshot, criteria->>'min_clusters'` | (a) 之「方向門可讀數」判定母體 |
| `direction_arena_prediction` | `settled_at, pred_date` | (a) 之「arena 結算一批」 |
| `evolution_production_feature_set` | `feature, set_status` | (b) 之 active 計數 |
| `promotion_queue` | `feature, run_id, gate_json->'G-PROM'／'G-ECON'` | (b) 之候選與雙綠判定 |
| `evolution_run` | `run_id, status, config_json` | 引擎輪 vs 人工紀錄之分辨 |
| `evolution_kill_switch` | `scope, state` | §四 停止機制現況 |
| `pg_trigger`／`pg_proc` | trigger 本體 | 終態不可逆性之驗證 |

**結果落點**：本檔（`reports/`）＋ [[sunset-deadline-today-pending-a]] 記憶。**不寫任何 DB 表**。

## 八、對應 python 程式規畫（#20 要件）

| 檔 | 角色 | 本案中之地位 |
|---|---|---|
| `scripts/gate_raise_sunset_deadline.py` | GATE-raise 呈案（已執行，hugo 親簽） | 產生 r2；**結構上不 evaluate** |
| `scripts/report_triple_evolution_week.py` | 三條件週儀表（唯讀） | **爭點所在**：其 :35-40 之尺無 sha 錨 |
| `scripts/run_evolution_iteration.py` | TWEVO driver | I5 之 `apply_allowed`／`TWEVO-APPLY-go` 人閘所在 |
| `scripts/migrate_evolution_v2_ddl.py` | SUNSET 種子與 sha 常數 | 凍結文字之 repo 側 SSOT |

**本案不新增、不修改任何程式。** 若 Steward 裁後需執行結算或開 r3，屆時之腳本另案規畫並須含
#29 指令矩陣、`--selftest`、以及**強制互動 TTY 之人閘**（同 `gate_raise_sunset_deadline.py` 口徑）。
