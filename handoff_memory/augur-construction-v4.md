---
name: augur-construction-v4
description: 建構理解 v4 報告（20260713）指針＋本輪深讀的承重新發現——三塊架構/12 REFUTED/斷線清單，supersede v3 指針
metadata: 
  node_type: memory
  type: project
  originSessionId: 778040ca-21b5-4b60-ad2d-0fad302930ca
---

# augur 建構理解 v4（2026-07-13，code-verified）

**SSOT＝`reports/augur_construction_understanding_20260713.md`**（1,590 行；supersede 20260710 v3）。產法：58-agent 多視角深讀（16 子系統＋10 critic 補讀＋4 鏡頭）× 逐宣稱對抗驗證（12 REFUTED 全採更正版）× 終審 4 鏡頭（16 findings 已修）。

**架構心智模型（v4 更新）**：不是兩半、是**三塊**——半-1 預測、半-2 素養/顧問、**第三塊本地審議引擎（開發治理）**。總綱五句：先凍後跑（criteria_sha 鎖門柱）／強制下沉機械閘／做不到留誠實終態帳／長跑帳本冪等可續／拍板權綁人。

**本輪承重新發現（讀報告前先知道的）**：
1. **redline 對三大治權檔失聯**：`deliberation_redline_trigger` pattern 釘死舊版檔名（v1.5.0/v1.8.0/`_v%`），對現行靈魂/原則精華/憲章全 MISS→治權宣稱不會強制人裁；修法＝UPDATE 3 列。
2. **predict role applied-but-connection-unwired**：role+GRANT 已 live，但無 `DB_PARAMS_PREDICT`、無 code 用它連線。
3. **A3 三鏡頭三門 DB＝preregistered、approved_by 空**（07-12 17:39 重新預註冊、無 `_r2` gate_id）——與「已簽」記憶/commit 訊息不符，**以 DB 為準**；開賽鏈若含 A3 先問 hugo。
4. **本機 DB＝07-12 dump，無 491 件全文/47 萬句**（那批在原機落地；adapter_config.fulltext 本機 NULL）——引用時勿當本機事實。
5. **macro 埋雷不變**：fred_series 有 vintage PIT 結構、無 PIT reader；接 macro 特徵前必須先落 reader。
6. 方向軸 fail-closed＝DB trigger 物理零列；幅度軸判死列照存靠展示層貼標——**兩軸強制強度不對稱（by design）**。
7. 活體增量中途態：feature_values→2026-06-30、universe/prediction 仍 2026-05-31、payload as-of 錨自洽不污染。

**12 條 REFUTED 要點**（詳報告 §12）：升版連動≈10 次非 2 次；audit 層含 2 支專職 writer 非全唯讀；隔離掃描八道非七道；PIT 名單非單調（5 次窗間上升）；三鏡頭 adapter 隔離不乾淨（三處同動、gate 結果無法單因子歸因）；蒸餾 274 筆 gold teacher 全是 `claude-teacher-workflow` 非本機零 token；sync_memory 含 `.` 路徑會分岔；等。

[[cross-machine-handoff]]（其「v3 建構理解 20260710」指針已被本檔取代）[[augur-project-map]][[augur-deliberation-engine]]
