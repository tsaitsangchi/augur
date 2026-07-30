---
name: augur-verifier-traps-20260730
description: 12-agent 重讀抓出之驗證器陷阱:verify_* 非唯讀且四支用中位數灌滿覆蓋、reconcile_audit 假綠仍在、rc=0≠通過、門評跨軸污染(已修)
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 223fa752-0df8-474d-aa39-9ddbcbfef034
  modified: 2026-07-30T04:35:44.992Z
---

2026-07-30 全專案重讀（12-agent／`reports/augur_full_reread_facts_20260730.md`）在 `scripts/` 驗證群抓到 16 則陷阱，最會咬人的六則：

1. **`verify_` 前綴不代表唯讀**：六支會 UPSERT 進**生產** `feature_values`（`verify_economic_candidate`／`economic_reexam`／`incremental_fair`／`interaction_promotion`／`signal_promotion`／`stability`），另七支寫 `vectorstore_shadow_eval`／`principle_factor_map` 等。
2. **覆蓋假象的製造端就在驗證器裡**：上列四支以 `vals.get(s, med)` **用中位數把候選特徵補滿整個 as-of 股票集**——之後任何「該特徵覆蓋率 100%／panel 全齊」都是自己灌出來的。對照組 `verify_candidate_promotion.py:131-135` 明文防這件事。
3. **`reconcile_audit.py:158` 假綠仍未修**：自算 `passed = vm==0 and ex==0 and not inc`，**漏掉 `mis`(missing_in_db)**，且不呼叫正典 `reconcile.verdict()`；DB 少一半資料照樣印 `PASS ✅`。另 `_summary` by-date 路徑遇空 `per_date` 也一律 PASS（死表靜默綠）。
4. **rc=0 不等於通過**：23 支 rc 恆 0；`verify_evolution_acceptance.py` 之 N/A 不計失敗且 A13 設計上永不 FAIL——全 N/A 亦 rc=0。掛 cron 只看 rc＝把「什麼都還沒證出來」讀成「全部合規」，必須看 `PASS x · FAIL y · N/A z` 三計數。
5. **門評跨軸污染（我 2026-07-30 已修）**：`evaluate_direction_gate.py --evaluate-all` 原 SQL 無 track 過濾，會撈進 track='M' 的 `dgate_meta_replay_B2_ridge`／`M1_gbdt`（屬 `evaluate_meta_replay_gate.py`）→ 已加 `AND track IN ('D','H')` ＋單門 fail-closed 守衛（非靜默跳過）。同支 `:225` 另有顯示債：D／M 軸一律顯示 OOS=0。
6. **`verify_sign_consistency.py` 文檔與碼不符**：docstring 稱「panel 級 block bootstrap」，`:96` 實作為 `ics[rng.integers(...)].mean()`＝**逐點 iid 有放回**、無 block——重疊窗自相關未吸收，與 CLAUDE #11 相違。（我今日才用這支當 SIGN-B 尺；改碼＝換尺須呈裁。）

**Why**：這些全屬 [[guard-mechanisms-that-silently-fail]] 的家族——機制壞了會安靜變綠燈。第 2 則尤惡：它讓「覆蓋對齊」這個紀律（[[same-scale-precheck]]）在特定工具下失效，因為覆蓋是被灌出來的。

**How to apply**：跑任何 `verify_*` 前先 `grep -n "INSERT\|UPDATE\|execute_values" <該檔>` 確認副作用；引用任何覆蓋率數字前先確認不是中位數補滿的產物；判「通過」一律讀三計數不讀 rc；門評務必先確認 track 與評估器相符、且 `_assert_clean_tree()` 會先攔（樹不乾淨即無法判，這是特性非 bug）。
