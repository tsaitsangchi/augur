---
name: augur-mechanical-gate-gaps
description: 2026-07-17 深讀盤出的機械閘缺口——最弱防護恰在最關鍵表(trial_ledger/revalidation_baseline 零 DB 防護)、誠實鎖沒接線(base_rate 寫死 0.5)、自測全綠≠不變式被鎖住、全新 DB blocker、refetch_fixed_tables 無參數即 DROP+放量
metadata: 
  node_type: memory
  type: project
  originSessionId: aac75e63-bffa-4a09-be73-f8f4937ad7f1
---

augur 的總綱是「**強制下沉機械閘**」。本檔記**那些看起來有閘、實際沒有**的地方。**共同型態:碼綠、自測綠、docstring 宣稱有鎖——但鎖不在、或鎖不住。**
> 驗證級別標註(承 [[cross-claim-contradiction-check]]):【親驗】=本則作者 2026-07-17 SQL/code 實查;【深讀】=引自深讀 agent 域切片、未親跑,信心較低(深讀無對抗層、約 1/5 宣稱可能有誤)。

## 1. 最弱防護在最關鍵表(最刺眼的不對稱)【親驗】
- `trial_ledger` 與 `revalidation_baseline` **各 0 trigger**(SQL 實查 pg_trigger),而 `arena_admission_gate` 有 trigger。
- 恰恰是最關乎「假兆」的兩表最弱:**刪 trial_ledger 列 ⇒ DSR 虛高且不留痕**(N 是機械來源);`revalidation_baseline` 之「凍結錨」**只是欄名 `frozen_at` 與慣例**、可被 UPDATE 靜默改寫。
- ✅ 良性對照(別誤判):`trial_ledger` 32 列但 trial_id 燒到高序號 ≠ 有人刪列——是 `ON CONFLICT DO NOTHING` 燒號機制,與 8 欄 UNIQUE 自洽。(典型「兩個各自正確的事實拼起來會誘導出錯誤結論」。)

## 2. 誠實鎖沒接線【親驗】
- **`scripts/produce_direction_probability.py:108` 把 `base_rate` 寫死 `0.5`**(`VALUES (%s,%s,%s,%s,%s,0.5,%s,'arena_live',...)`),而憲章誠實硬綁①要求 `max(p̄,1−p̄)`。因 `max(p̄,1−p̄)≥0.5` 恆成立 ⇒ **系統性把樸素基線報得偏低、只利模型**。**不是算不出來,是接線漏了。**（gate 端已算對存於 `direction_gate.result->>'majority_base'`＝【深讀】未親驗那一半。）
- **E[r] 四項閉式假設揭露**被 producer 外包給「呈現層」,而呈現層零消費者、無方向軸 UI ⇒ 四項揭露是**唯一無機械保護的鎖**（fail-closed/挪門柱有 trigger、編造有 guard,揭露只有人記得）。【深讀 doctrine-soul 域】

## 3. 「自測全綠 ≠ 不變式被鎖住」【深讀 code-evaluation 域、未親驗——最該親驗再引用】
- `evaluation/portfolio.py` `vol_target_series` 預設 target 用**全序列 vol** ⇒ `scale_t` 疑依賴未來(深讀稱實測 t=6 之 scale 被 t=8,9 改動 +0.34),而 docstring/commit/selftest 都掛「#8 無前視」、那條 selftest 斷言疑走 `or` 分支恆真抓不到。**⚠ 若屬實＝三敵之一(偷看未來),須最優先親驗**;本則作者尚未親跑,不敢斷言,但列為最高複驗優先。
- `predict_asof.py` feats_hash 防漂移鎖疑空轉(死變數+恆真比對);`deflation.deflated_floor()`(DSR 地板本尊)疑零斷言。【深讀,未親驗】

## 4. 全新 DB blocker(本機不發作)【親驗】
- `scripts/migrate_trial_ledger_ddl.py` **自我矛盾**:CREATE TABLE 之 `CONSTRAINT trial_ledger_uq UNIQUE` 為 **7 欄(無 recipe)**,同檔 `ON CONFLICT` 卻 **8 欄含 recipe**——SQL/code 皆親查坐實。若同一 transaction ⇒ **全新庫上建表/寫入失敗**。本機不發作(dump 已含 recipe 欄);但在乾淨機器重建會炸。07-17 修復只補 BACKFILL、回歸鎖只斷言 BACKFILL 字串＝**單邊鎖**。

## 5. 一閘半 / 函式孤兒 / 危險 script【親驗】
- **`augur_predict` role 未接線**:全 `src/augur/` **零 `DB_PARAMS_PREDICT`**(grep 零命中) ⇒ 預測管線仍以 owner role 連線、讀得到全部素養層。「AST+GRANT 雙閘」實為**一閘半**。
- **`item_source_gate` 函式孤兒**:`pg_proc`=**1**、`pg_trigger`=**0**(親查)。此組合**無法由 migration 任一次執行產生**(函式+CREATE TRIGGER 同一 transaction) ⇒ **有一條不在 repo 裡的執行路徑碰過 live DB**(成因未驗證)。同型見 [[jian-a-admission-hardening]]。
- **`scripts/refetch_fixed_tables.py`＝最危險 script**(親查:`argparse`/`--dry-run`/`--run` grep 全 0 命中＝**無任何閘**):裸跑即 DROP+全史重抓+撞 #24 IP ban。危險度高於已知的 `revalidate_*` 對,且因不在 alpha 域故從未被 memory 收錄。**探測任何陌生 script 前先 Read 檔頭**(#7 教訓已多次重演)。
- **`catalog/__init__.py`**:922 行(親查)、藏邏輯,因檔名是 `__init__.py` **同時掉出 #18「74 支自測」盤點與 `python -m` 可執行性分母**＝已知債。

**How to apply**:看到「有機械閘」的宣稱,先問三件事——**(a) 閘在 DB 還是只在 Python?(b) 有沒有 selftest 真的會紅?(c) 那個 selftest 的斷言是不是 `or` 恆真?** 關聯 [[augur-construction-v4]] [[alpha-phase1-anchor-repair]] [[audit-attestation-falsegreen]]。
