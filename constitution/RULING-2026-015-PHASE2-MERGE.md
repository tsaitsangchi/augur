# Augur Steward 裁決第 2026-015 號

**Phase 2 Identity 分支准併暨裁①裁③處置；生產施作採「retire 先行」順序、P5 一次拍板制**

* **依據**：`AUGUR-MC v1.3 §8.1`、P5.W2；Phase 2 #19 卷宗（ops/phase2/BRANCH-19-DOSSIER-2026-07-18.md，三鏡全 GO）；RULING-2026-014（裁②已結）
* **裁決人**：Constitution Steward（tsaitsangchi）——2026-07-18 書面核示「三勾齊」
* **日期**：2026-07-18｜**登錄**：Amendment Log AL-2026-018

## 主文

1. **（准併）** `remediation/phase2-identity`（22468bb）併入 main（merge `4c6d3b6`）；併後測試 27/27 綠（Phase 2 十二測＋supersede 十五測）。
2. **（裁①：並發防護）** `resolve_or_mint` 之 **advisory lock 防護列為 Phase 2 後段攝取接線之前置條件**（親測雙鑄成立；UNIQUE 不可行——ID.43 合法同碼二列）；**生產 backfill 以單實例執行**載入 runbook。
3. **（裁③：生產順序）** Phase 2 生產施作順序裁定為：**(1) 型別判準載體（已施作，RULING-2026-014）→ (2) retire backfill 先行**（TaiwanStockDelisting 342 筆→lifecycle retire 事件；補件腳本另審）**→ (3) 存量鑄造 →(4) 屬性同步**。效果預告並採認：生產 minted 預期 ~3,149 含 **~235 枚 provisional**（重用碼正確不縫合——此為憲章正確樣貌，非缺陷）；~35 例名實不符入人裁佇列。
4. **（P5 一次拍板制）** retire-backfill 補件經審查後，**生產施作以單一 P5 核准涵蓋全順序**（(2)(3)(4) 一次呈核），不逐步分批請示。
5. **（minors 小修批）** 卷宗七 minors（名冊殘差計數／resolve docstring 退役軸與 tie-break／valid_from 兜底改誠實跳過／runbook 載明 seed 先行〔已滿足〕等）併入補件分支一次辦理。

## 程序聲明

併入與順序裁定為 Steward 裁決；效果預告（235 provisional）源於審查鏡對沙盒同庫下市紀錄之實測推估，生產實跑數以 runbook 驗收為準（#9 不轉抄）。
