---
name: augur-three-gate-strengths
description: 機械閘三層強度(硬33表/半14表/軟437支);綠燈帳本假綠;孤兒佔埠假綠;人閘零DB強制
metadata:
  type: project
---

**一句話**：augur 是**一台以 PostgreSQL 為唯一系統記錄、把「什麼才算真的」寫成表與 trigger 的誠實性機器**；台股預測與知識庫是它的**測試載荷**，不是產品。產品是那套機制本身。

**三層強度（誤判之根源——專案用同一個詞「機械閘」稱呼三者）**
- **L-硬**：PG trigger／GRANT，**33 表**，真的擋、不需人記得
- **L-半**：trigger 只綁 DELETE+TRUNCATE，**14 表**，UPDATE 全裸（一句 UPDATE 可把 prodset 從 removed 翻回 active、關 kill switch、改原則）
- **L-軟**：Python `--selftest`，**<!--probe:doc_mem_tgs_matrix-->495<!--/probe--> 支入口**（probe `doc_mem_tgs_matrix`，`read_treaty_probes.py --check` 驗 diff；07-31 快照＝437）、**零 CI 零 git hook**（07-31 當日值），大量在驗「字串出現在自己原始碼裡」
⇒ **最承重那條（只有人能做）落在 L-軟甚至更弱**。

**三個親驗的假綠（2026-07-31）**
1. **綠燈帳本自己是假的**：`validation_evidence` 19/19 green（07-31 當日值；live 現況＝probe `doc_mem_tgs_ve`：<!--probe:doc_mem_tgs_ve-->total=25 green=14 red=9 unverified=2<!--/probe-->），但只 12 列有 `check_sql`，**逐條重跑 3 條回 false**（`E1_raw_reconcile_exit` last_verified 07-15、`E2_feature_frozen_panel`／`E4_exclusion_set_contract` 07-11），而 `verify_validation_evidence.py` **不在任何排程**。⚠ 三個 false 是三種病：E1 真退步（正典對帳最後 passed=t 為 07-16、07-25 後停跑）；E2/E4 是**凍結期契約被「解凍→live 增量」政策合法作廢**（契約寫死 35 特徵/2,418,655 列，live 已 38/8,540,331）——**混為一談會有人去改 check_sql 湊綠＝違 #12**。
2. **孤兒佔埠假綠（最會騙人）**：`:8090`/`:8500` 被 07-30 手動起的 `./venv/python serve_*.py` 佔住（相對路徑＝shell 起），systemd 副本 NRestarts **12005/12059** 仍 activating。⇒ **`systemctl restart` 成功、埠通、頁面開，載入的卻是 18–20 小時前的記憶體版**——CLAUDE #7 以「重啟成功」的形式失效。判斷法：`ss -tlnp` 看 pid 的 `ps -o lstart` 與**啟動路徑是否絕對**。對照組 advisor/probability/ollama 皆 systemd 絕對路徑起、NRestarts=0。
3. **人閘零 DB 強制**：16 條簽核 CHECK 全只驗非空、零 `current_user` trigger、7 個 guard 全是可自設 GUC、單一 `augur` role。已有 3 筆 `selftest`/`hugo-authorized-selftest` 寫進人簽帳本。`governance_queue.py` 曾以 `getpass.getuser()` 自動代簽（**已修：commit 847f65a 加 TTY＋親手打簽名**）。

**優化第一原則**：**在加任何新能力之前，先讓紅燈會亮**——`check_cmd_matrix`／`check_treaty_refs`／`verify_validation_evidence` 四個真有價值的閘全部「存在但不會自己跑」（`.git/hooks/` 非 sample 檔 0、無 `.github/workflows/`）。

**不要動的五件（真的做對了）**：預測⊥知識三道隔離閘（AST＋grep＋GRANT）／`heavy_slot.py` advisory lock 設計／`check_cmd_matrix` 受檢全數通過（07-31 快照 437/437；現值＝probe `doc_mem_tgs_matrix`，見上）／`specs/` lint 7/7／**「禁止假關」文化**（10-14 七項至今全 `[ ]`，沒人偷勾）。

詳見 `reports/augur_deep_understanding_20260731.md`（40 則債務依「不修會怎樣」排序）。相關：[[augur-verifier-traps-20260730]]、[[guard-mechanisms-that-silently-fail]]、[[restart-systemd-after-edit]]
