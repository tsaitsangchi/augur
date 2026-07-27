# V2-AUTOADVANCE 預註冊自動推進規則集（**ENACTED 2026-07-27**）

> **性質**：治理裁決（PME-AUTO-B 同型：人拍板規則一次、機器在規則內自動；Sole Steward 專案不設公示要件，RULING-2026-031）。
> **動因**：hugo 2026-07-27 對話指示（逐字）：「此專案所有自進化迭代計畫可以自訂排程來逐項逐次的一步一步進行過程需要決策的項目，請依最佳化方案來做自行決策使專案自動往下執行」。
> **生效**：hugo 同日回覆（逐字）：「回覆 V2-AUTOADVANCE-yes 即生效」——`V2-AUTOADVANCE-yes` 成立，R1–R7 與 §四 H10 分層裁定即刻生效。本檔構成 H8／P5.W5 所需之書面裁決：人類監督由「逐案簽」改為「規則簽＋週掃視認領」（R6），監督形式改變、總量未實質降低——所有自動決策落帳可稽、緊急停恆在。
> **繕寫**：claude 起草並登錄、決策者＝hugo（§8.1 分立記載，不冒充親簽）。修訂唯增列（P4.E3）。

## 一、規則集（R1–R7；生效後機器可自動執行的決策）

**R1 RAWEVO 週輪自動**：每週六 09:00 全程唯讀跑 R0–R3；產出 hint 一律落 `evolution_hypothesis_hint(decision='pending')`。
  **hint 升級不自動**（保 Goodhart 防線）——改為**週日 digest 批次呈報**，hugo 一則 `RAWEVO-HINT-approve <ids>` 批覆。每輪 hint 上限 10 條、必附 provenance＋n_obs。

**R2 TWEVO 輪自動（I0–I4）＋ 閘內自動 APPLY**：driver 排程跑候選建值→漏斗→local-gates；I5 APPLY 依 PME-AUTO-B 既有語意自動，**加四道新篩**（全部機械）：
  (a) 雙綠 ∧ kill_switch clear（既有）；(b) **`FAIL_SIGN` 篩過**（符號一致性，Phase 4）；
  (c) 對照臂經驗偽陽率 ≤10%（GATE-raise 預註冊規則之閘綠；>10% 時自動改用經驗 95 分位重評）；
  (d) 單輪 auto-APPLY 上限 **1 特徵**、apply_log 追加 `gate_ref='V2-AUTOADVANCE'` 註記列。
  APPLY 後之 prodset 重訓＋hotpath 驗證＋arena 對局自動接續（arena 本已自動）。

**R3 H5 預註冊處置**：Phase 4 對照臂確認 `volume_gini_60d` 判 `FAIL_SIGN` ⇒ **自動 demote 出 prodset＋追加修訂列註記**（不 UPDATE 原列、P4.E3）；其 principle 由 `validated` 改 `sign_refuted`（追加列）。三選一在此預決＝demote＋註記。

**R4 LAIEVO 自動段**：RUBRIC 新尺落地後，離線臂自動複驗（秒級）＋ LLM 臂夜間 heavy-slot 自動跑；pack 候選在凍結集上自動評測。
  **auto-retire 允許**：現役/候選 pack 若 `evidence_level` 未達 `weak`（連零訓練基線都未勝）⇒ 自動 retire（serving 空缺＝MCP fail-open 回基線行為，安全可逆）。
  **晉升仍人簽**（P5.W2 憲章層，本規則集無權豁免；摩擦極小＝每次換 pack 一個 `promoted_by`）。

**R5 停損與 SUNSET**：停損計數與 `stopped_no_gain` 標記自動（A11；`incomparable` 不計入）；**停損後重啟＝人**。V2-SUNSET 三條件判定自動印於週儀表第一行；**續命／終止後果＝人**（program 級、criteria_sha 已凍結，機器不得代）。

**R6 留痕與掃視認領（§8.1 事後偵測之強化）**：每筆自動決策必帶 `gate_ref='V2-AUTOADVANCE'`＋寫入決策路徑；**週日 digest** 彙列本週全部自動決策（表、列、時戳、依據規則號）供 hugo 掃視認領；連續 2 週 digest 無人閱（無認領動作）⇒ 自動降回逐案人閘（防「規則簽」淪為無人監督）。

**R7 不可逾邊界（本規則集不鬆動）**：三敵零容忍；FZ-keep 豁免清單外零 API；GATE 只升不降；不自動下單；治權檔（靈魂／原則精華／憲章／CLAUDE.md）任何變更停下問；arena 預註冊死鎖不改；`evolution_kill_switch scope='global'` 恆可一鍵停全部（人得緊急停）。

## 二、仍須 hugo 的殘餘清單（生效後全部）

| 項 | 頻率 | 為何機器不能代 |
|---|---|---|
| 週日 digest 掃視＋hint 批覆 | 週一次 | Goodhart 防線＝哪條假說進量化鏈（H3） |
| serving pack 晉升 `promoted_by` | 每次換 pack | P5.W2 憲章層 |
| 停損後重啟／SUNSET 續命或終止 | 觸發時 | program 級價值判斷 |
| 跨域 principle 人撰（H10） | 隨需 | DB CHECK 硬擋 AI 生成入庫——機器物理上做不到 |
| 治權檔修訂 | 隨需 | 憲章升版程序 |

## 三、啟用序（生效碼後的實作順序，全部執行層）

1. Phase 4 完成（對照臂＋FAIL_SIGN；進行中）→ R3 自動處置隨即生效。
2. RUBRIC 換版（已拍 H6）→ R4 自動段就位。
3. TWEVO driver＋heavy_slot 第二版＋週儀表三支補寫（Phase 5/6 既定實作）。
4. 排程檔入 git（`e61eabc` 先例）＋掛載（本機＝正典機，AC 永不睡眠）：RAWEVO 週六 09:00／TWEVO 週間夜輪（heavy-slot 序列化、避開 22:30 arena）／哨兵每日 01:30 後／週儀表＋digest 週日 08:00。
5. kill_switch `scope` 欄 migration 補上（repo 級缺口，先決）。

## 四、H10 一併預決（同碼生效）

`field_lens_map`＝資料側「raw 欄位↔思想鏡頭」；`principle_domain_map`＝素養側「原理↔應用域＋引文」——**正交、並存、分層如上定義**；域＝應用注記＋治理把手、非知識圍牆（憲章 v1.47.0 (ii) 現行文義，無需修憲）。
