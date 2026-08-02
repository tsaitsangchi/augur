# [DRAFT 呈案] I5B｜promotion_queue 舊世代 pending_auto 殘留之處置（未經拍板不得施作）

> **狀態**：DRAFT 呈案——W2 批追加（AGO 親驗發現之後續）；**未經 Steward 拍板不得施作**。
> **L6.18(c) 自我利益揭露**：本案由 AI 呈議 AI 自建之進化引擎佇列機制的變更；且選項丙所倚
> 之 `--queue-id` 旗標為**同日由 AI 施作**（TWEVO-APPLY-go「一次一顆」既裁事項之落地），
> AI 於本案對丙有「自己作品」之利益關聯，故三案並列、建議案附證偽條件、裁決權全在 Steward。
> 甲案含**機器自動改列**（引擎自動關閉同 feature 舊 pending 列）＝自動鏈行為之變更，L6.16
> 四項對照見 §4 甲案風險欄。
> **撰寫**：2026-08-02（日）；所有查詢唯讀（零 DDL、零寫入）。

---

## §1 問題與授權鏈

**問題**（AGO 親驗發現）：promotion_queue 存在「同 feature 已被新世代（新 run）列蓋過、
仍掛 pending_auto」之舊世代殘留；I5 整批消費（`STEP_CMD["I5"] = ["scripts/apply_evolution_promotions.py"]`，
`scripts/run_evolution_iteration.py:68`，**無 --run-id／--queue-id 篩選**）會**連舊帶新**一次吃掉。

**授權鏈**：AGO 發現→本呈案（呈案與證據整備屬 AI 可為；裁決專屬 Steward）。相關既裁：
TWEVO-APPLY-go「一次一顆」（S-i 逐顆人裁）已裁，其 CLI 載體（`--queue-id`）同日已落地
（`scripts/apply_evolution_promotions.py`；見 §5 丙案現況）。

---

## §2 現況親驗（2026-08-02；live DB 唯讀；#15 不靠快照抄數）

### 2.1 誠實聲明：AGO 快照之「6 列」已不可自 live 重現——州已被 08-01 18:40 遷移改寫

AGO 所見「6 列舊世代殘留」**無 as-of 快照可逐列覆核**。live 考古（下表）證實**同型態確實存在
過**，惟本次可數得之舊世代殘留為 **7 列**（run 19 世代、2 個 feature），與「6」差 1；差異
無法歸因（該 7 列 `created_at` 皆 NULL，無法時序回放 AGO 查詢當下之列數）。以下一律以
live 可證數字為準（承「live-vs-repo drift」教訓：驗 DB 層宣稱查 live，不抄舊報告）。

### 2.2 考古：AGO 型態之實體——7 列 run-19 殘留 ↔ run-20 新世代 1:1 蓋過（皆已非 pending）

`decided_by='gate_set_migration_gsign'` 於 **2026-08-01 18:40:09** 一次關閉之 run-19 列：

| 舊列 queue_id | run | feature | action | principle_id | 蓋過它的 run-20 列（同 feature） |
|---|---|---|---|---|---|
| 427 | 19 | cycle_position_252d | promote | 77 | 444（p77） |
| 428 | 19 | cycle_position_252d | promote | 98 | 445（p98） |
| 437 | 19 | debt_ratio | demote | 85 | 454（p85） |
| 438 | 19 | debt_ratio | demote | 109 | 455（p109） |
| 439 | 19 | debt_ratio | demote | 114 | 456（p114） |
| 440 | 19 | debt_ratio | demote | 120 | 457（p120） |
| 441 | 19 | debt_ratio | demote | 125 | 458（p125） |

同 feature＋同 principle 1:1 對應——舊世代列與新世代列**是同一顆候選的兩代重發**。

### 2.3 該殘留如何消失的：一次性遷移之副產品，非機制閉合

時間線（live `promotion_queue.decided_at`／`evolution_run`）：

| 時點（08-01） | 事件 |
|---|---|
| 04:11 | run 20 收尾，**留 19 列 pending_auto**（七閘世代） |
| 16:27 | run 19 判 failed（其 7 列殘留仍 pending_auto）——**此刻 pending 混池＝7（run19）＋19（run20）＝26 列**，I5 整批消費會 26 列全吃＝AGO 所指風險之實體 |
| 18:32:14 | q487（lending_fee_rate_mean_20d demote）由 **hugo 親跑 applied**（`decided_by='hugo'`）＝S-i 逐顆之首例 |
| **18:40:09** | `gate_set_migration_gsign` 把 **26 列**（7＋19）整批標 `rejected_gate`——**名目是 G-SIGN 八閘遷移**（七閘世代列作廢），非世代 supersede 機制 |
| 18:41:39 | run 21 起跑（八閘 `gate_set_rev='8g-sign-v1'`），將 run-20 之 19 顆**同 feature＋同 principle 1:1 重發** |

### 2.4 現況：跨 run 殘留＝0，但結構性缺口原封不動

- 現行 pending_auto **19 列全屬 run 21**（run 21 已於 08-02 04:11 succeeded）；跨 run 殘留今日為 0。
- **引擎無任何世代 supersede 邏輯**（grep `supersede` 於 `scripts/`＋`src/augur/` 之進化鏈檔案零命中；命中者皆為無關 migration）。08-01 的清空繫於「剛好換閘集」這個一次性理由——**run 22 起跑時，run 21 之 19 列（屆時殘餘）將重演 §2.3 的 26 列混池型態**，I5 整批照樣連舊帶新。
- 機械事實一：`promotion_queue_queue_status_check` CHECK 僅允許 `pending_auto/applied/rejected_gate/halted`——**無 `superseded` 值**；字面「標 superseded」須 DDL 放寬 CHECK。
- 機械事實二：`philosophy_principle` 無 generation 欄——「世代」唯一可機械判定之尺＝`run_id`。
- 機械事實三：promotion_queue 受誠實閘（B4-P2a GUC），任何清理 UPDATE 須帶 `SET LOCAL augur.honesty_write='on'` 通行證，否則被 trigger 拒。
- 現行 19 列另有**同 run 多 principle 並存**（cycle_position_252d×2、debt_ratio×5、gov_bank_net_buy_60d×2、top_holders_pct×2）——此為同批合法多列、**非**本案之跨世代殘留，不在處置範圍。

---

## §3 選項

### 甲｜引擎開新世代列時，自動把同 feature 舊 pending_auto 標 superseded

- **內容**：queue 寫入端（`run_philosophy_evolution.py`／`src/augur/philosophy/evolution.py` 之
  入佇列路徑）於 INSERT 新列前，將同 feature（同 axis）且 `run_id < 本 run` 之 `pending_auto`
  列改標終態＋`decided_by='superseded_by_run_<N>'`。
- **前置**：`superseded` 入 CHECK（DDL）或沿用 `rejected_gate`＋decided_by 註記（零 DDL、語意次佳）。
- **優點**：結構閉合、每個 run 邊界自動生效、一勞永逸。
- **風險／窗口**：涉引擎檔＝**run 21 後窗**才可動（本呈案絕不碰該三檔）。L6.16 四項對照：
  人類介入點數**不減**（被關列本就不會等到人裁——新世代列才是人裁對象）、否決可達性不變、
  揭露比例**增**（decided_by 逐列自陳）、最大自動鏈長**不增**（同一 INSERT 交易內的標記，未加鏈節）；
  惟「機器覆寫 pending 列」屬防呆記憶中之高危型（機器覆寫人裁），須以「僅動 `run_id < 本 run`
  且同 feature」之最窄謂詞＋回歸鎖（拔謂詞驗紅）釘死。

### 乙｜一次性清理 SQL 標 superseded，不改引擎

- **內容**：run 邊界時人工跑一段 SQL（帶 GUC 通行證）關閉跨 run 殘留。
- **今日之標的集＝空**（§2.4：跨 run 殘留現為 0）——乙案今日無事可做，實際用途是 **run 22
  起跑前**的邊界清理。模板（屆時依實況改列、由 hugo 過目後執行；字面 superseded 版另需 DDL）：
  ```sql
  BEGIN;
  SET LOCAL augur.honesty_write = 'on';
  UPDATE promotion_queue q SET queue_status='rejected_gate',  -- 或 'superseded'（需先 DDL 放寬 CHECK）
         decided_at=now(), decided_by='stale_supersede_manual_<YYYYMMDD>'
   WHERE q.queue_status='pending_auto' AND q.run_id < <新 run_id>
     AND EXISTS (SELECT 1 FROM promotion_queue x
                  WHERE x.feature=q.feature AND x.run_id=<新 run_id>);
  COMMIT;
  ```
- **優點**：零引擎變更、零自動鏈變更、逐次人眼過目。
- **缺點**：不閉合結構缺口；每個 run 邊界都要記得跑（防呆繫於人的記憶＝已知失效型）；
  以 `rejected_gate` 冒名 supersede 與 08-01 遷移同一語意債（閘沒紅卻標 rejected_gate）。

### 丙｜不動機制，靠 --queue-id 逐顆迴避（已落地）

- **內容**：S-i 逐顆人裁一律走
  `venv/bin/python scripts/apply_evolution_promotions.py --queue-id <N> --allow-apply --gate-ref TWEVO-APPLY-go`
  （hugo 親跑；本日已落地，selftest＋突變驗紅＋live dry-run 皆過）；舊世代列因不被指名而永不被消費。
- **優點**：零機制變更；與「一次一顆」裁決同構；今日即生效。
- **缺點**：舊世代列**永遠掛著 pending_auto**（帳面噪音：I0 診斷、digest、admin console 之
  pending 計數失真；且任何一次「忘了用 --queue-id 的整批跑」風險原封不動——I5 driver 路
  （`run_evolution_iteration.py --step I5 --allow-apply ...`）仍是無篩整批）。

---

## §4 建議案（AI self-reported；裁決在 Steward）

**丙（已生效）為當下防線 ＋ 甲為結構解（run 21 後窗施作、另案附 diff 與回歸鎖呈拍板）；
乙之模板僅備 run 22 起跑前若甲未及落地時的邊界清理（屆時列清單交 hugo 過目親跑）。**
`superseded` 是否入 CHECK（DDL）併入甲案一起裁，避免二度動表。

**證偽條件**（任一成立即本建議案作廢重議）：
1. run 22 起跑前實查 `promotion_queue` 跨 run pending_auto 殘留＝0 且可證引擎已有隱性關閉
   機制（非又一次一次性遷移）⇒ 甲無標的、乙無標的，丙單獨已足。
2. Steward 裁 I5 整批路永久停用（一切 APPLY 唯 S-i 逐顆）⇒ 「連舊帶新」失去載體，
   甲降級為帳面清潔問題（僅乙之噪音清理仍可議）。
3. 甲之最窄謂詞在對抗審查中被證可誤傷同 run 合法多列（如 §2.4 之同批多 principle 列）
   ⇒ 甲退回重設計。

---

## §5 Steward 決定

> **（留白待 Steward 圈選）**
> 圈選格式：`I5B-同意`（＝建議案）／`I5B-改採乙`／`I5B-改採丙單獨`／`I5B-緩議`；
> 甲案之 DDL（superseded 入 CHECK）與引擎 diff 屆時另案附文供逐字過目。

---

### 附錄 A｜run-20 19 列 ↔ run-21 1:1 重發對照（08-01 18:40 關閉、18:41 起重發之全量證據）

| run-20 舊列 | feature | action | principle | run-21 新列（現 pending_auto） |
|---|---|---|---|---|
| 444 / 445 | cycle_position_252d | promote | 77 / 98 | 555 / 556 |
| 454–458 | debt_ratio | demote | 85,109,114,120,125 | 565–569 |
| 465 / 466 | gov_bank_net_buy_60d | demote | 101 / 108 | 576 / 577 |
| 488 | lending_fee_rate_mean_30d | promote | 107 | 599 |
| 492 | market_cap_log | demote | 80 | 603 |
| 501 | momentum_5d | demote | 106 | 612 |
| 541 / 542 | top_holders_pct | demote | 101 / 108 | 652 / 653 |
| 549 | volume_gini_20d | demote | 99 | 660 |
| 550 | volume_gini_60d | demote | 95 | 661 |
| 551 | volume_max_share_20d | demote | 99 | 662 |
| 552 | volume_max_share_60d | demote | 99 | 663 |
| 553 | volume_surge_5_60 | demote | 99 | 664 |

（19 列對 19 列、feature＋principle 全同——世代重發為引擎常態行為之直接實證；每個 run
邊界都會製造一批「舊世代殘留」，僅差有無人／機制去關舊列。）
