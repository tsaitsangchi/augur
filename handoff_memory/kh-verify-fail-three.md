---
name: kh-verify-fail-three
description: 三核 FAIL 九則:V-4 全表掃逐item重算=17天(已修凍結)、V-1 fail-open死碼、六則未修
metadata:
  type: project
---

第三次獨立核驗（`wf_b5489382-1a1`，2026-07-30）判 **FAIL／9 則**。**3 修 6 未修**，未修者不假關。

**已修**
- **V-4＋V-2（同一修法）**：`evidence.population_discriminates` 為 146k 列全表掃（核驗量 4.9–7.7s／次），原**逐 item 逐層各呼一次** ⇒ 批次約 17 天、常駐 advisor **每答 +10s**；且 `record_weight` 在判準消費前無條件寫列 ⇒ **批內第一個 fail 就替後面所有 item 開閘**（`exclude_item_id` 擋不到同交易 peer）。修法＝`evidence.frozen_population_verdict()` **批次／進程首呼算一次即凍結**。實測首呼 1.66s、之後 0.000ms ⇒ **5.6 天 → 2 秒**。凍結亦使 peer 無從污染。
- **V-1**：前版要求呼叫端自傳 `cur`，錯了被 `except: pass` 吞成靜默 **fail-open**（正是它宣稱要封的洞）。修法＝`auto_admit.kh_evidence_valid()` **呼叫端零配合**（自開唯讀連線）＋進程級記憶化＋**fail-closed**。
- **V-6 半**：`migrate_admit_state_guard_ddl.py --apply` 已施作，`reevaluate_kh_depths.py` 出示之 `augur.admit_depth_lower` 通行證終於有對象。

**未修（六則）**
- **V-3**：仍「**一列即解閘**」（該列帶不同分量值即可）；`--widen` 之 396 列（0.271%）正是走了這個洞。判準應改量「**通過者之間**」之分散度。
- **V-5**：`ALTER TABLE ... DISABLE TRIGGER ALL` 可整體卸閘（`knowhow_auto_admit_gate_change`／`knowhow_depth_reevaluation`／`knowhow_auto_admit_state` owner 皆 `augur`＝所有 script 用的角色）；兩帳本可 DELETE／UPDATE。⇒ guard docstring 之「**不可無痕」是過度宣稱**。需角色分離。
- **V-6 另半**：`reevaluate_kh_depths.py:186-187` 兩行自測仍假綠（「DDL 字串無 DELETE」證 append-only／「常數等於自己」證有通行證）。**這是 [[guard-mechanisms-that-silently-fail]] 所警告之同型，我再犯一次。**
- **V-7**：145,949 件會原封不動回到 depth 9；KH8 對「它所通過者」**仍零鑑別**（high 母體分量組合唯一 `(1,1,1)`）。
- **V-8**：`prior_depth` 短路＋`upsert_state` 之 `GREATEST` 單調升（日後關閘對已授予 depth 無效）；**KH7 通過理由仍為庫級**（最新 run 中任一 item 過 ⇒ 全庫每 item 都過）。
- **V-9**：丙-4 四項自測全用預設 `exclude_item_id=None`、`_FakeCur` 丟棄 SQL args ⇒ 未覆蓋所修行為。

**事故教訓**：對熱表下 DDL 前須先確認無長交易——補掛 admit_state 閘時 `DROP TRIGGER` 之 ACCESS EXCLUSIVE 被 hugo 當時之 runner 擋住、排隊 5:38；依 CLAUDE #30，排隊中之 EXCLUSIVE 會**反向擋住該表後續一切查詢**。已查證唯一等鎖者是我自己、無他者受累。
