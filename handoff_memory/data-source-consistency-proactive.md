---
name: data-source-consistency-proactive
description: 資料來源一致性問題（漏抓/假設型捷徑）應主動發現並修好，非只報告等用戶決定
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 535524f8-f10a-43be-8ee8-7e88ab8d3ccf
---

用戶（2026-06-11）指正：發現 News 週末漏抓（`sync_by_date` 跳週末，但 News 是 24/7 事件型、週末有新聞）時，AI **該主動修好**、而非報告完丟給用戶決定——「這種問題你自己應知道要做，這樣才能有資料來源的一致性」。

**Why**：根本是「跳週末」本身是個**假設**（假設週末無資料），違 #18「抓取依 API 事實、不假設」精神——對 News datetime 事件型就漏抓、破壞資料來源一致性。資料完整/一致是 augur 核心（「只用真實資料、誠實預測」）。

**How to apply**：
- sync/抓取設計中任何「假設型捷徑」（跳週末、固定起點 `full_start`、固定探測股 2330+1990、固定取樣日…）都要自問「對**所有** dataset 都成立嗎？」——不成立就是潛在漏抓/誤判。
- 由**資料事實判定**取代假設（如 `_date_has_time`：date 含時間→事件型不跳週末；純 date→交易型跳）。
- 護欄內（改 code、clean-room、可逆）發現這類一致性缺口 → **主動修+實測**，不被動報告。延伸 [[bounded-autonomy-mode]]「護欄內主動」。
- 已修案例：finmind.fetch 單日型 `end_date` 相容（News size-too-large）+ sync `_date_has_time` 週末判定。連結 [[augur_project_overview]]。
