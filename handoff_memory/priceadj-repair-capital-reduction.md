---
name: priceadj-repair-capital-reduction
description: PriceAdj「175 檔誤標」真機制=減資(CapitalReductionReferencePrice)非除息;結構反證=除息使 factor 上跳不可能觸發 guard;backlog 照「排除除息日」字面實作只消 5/250、殘留 245 會白打 FinMind
metadata: 
  node_type: memory
  type: reference
  originSessionId: aac75e63-bffa-4a09-be73-f8f4937ad7f1
---

**結論不變、機制歸因錯**——2026-07-17 alpha Phase 1 之 PriceAdj 修復裁決(41 檔真損傷已修、175 檔非真損傷)**結果正確**,但寫進 `HANDOFF.md:86`+報告+記憶的**機制標籤錯了**(標「除息跳點誤標」),且已被當「定案」傳播。錯源=`repair_priceadj_basis.py:5` docstring 把 factor 方向寫反(「除息點回落」)。

**真機制=減資,非除息**:
- 【親驗 2026-07-17】唯讀掃描 `repair_priceadj_basis.py`(無參數)=**175 檔受損**;前 10 檔首個即 **1109**,而 1109 在 `TaiwanStockCapitalReductionReferencePrice` 表有 **3 筆減資記錄**(SQL 實查)——受損股⊆減資股之直接佐證。
- 【深讀 data-raw 域、未逐點親驗】250 個違規點中 **242 精確落減資日**、5 筆為 DividendResult 負股利(現金減資),**普通除息 0 個**。
- 【深讀+結構推理】**結構反證(決定性)**:回溯調整下 `factor = adj/raw` 在除息日**必然上跳**(歷史價被下調);**只有減資才下跳** → 普通除息**在結構上不可能**觸發 `repair_priceadj_basis.py:36` 的 `factor < prev*0.995` guard。此推理成立則機制歸因確定為減資。

**⚠ 下游風險(照字面修 backlog 會出事)**:
- backlog 記「掃描工具**排除除息日**」→ 照此實作**只消 5/250(2%)、殘留 245**;
- 殘留非空 ⇒ 下次 `--repair` 對 ~170 檔**白打 FinMind 全史重抓**(撞 #24 IP ban),且 `remain` 非空**恆回 rc=1**=誤判修復失敗。
- **正解**:排除 `TaiwanStockCapitalReductionReferencePrice` 日期 **+** DividendResult 負股利列。

**⚠ 未驗證/未留檔**:`repair_priceadj_basis.py` 修復之「41 檔真損傷」**清單無 ledger**(掃描即時)⇒修復後無法回溯是哪 41 檔;1109 修復前「5 筆跳點」無法在本機 DB 復現(現 2 筆、皆減資日)。

**教訓**:「250/250 全由公司行動解釋、零未解釋殘留」這個**結論**撐得住,但**標籤錯了照樣毒下游**——因為 backlog 是照標籤寫的。此病 live 維運每逢減資/除息必復發(`repair_priceadj_basis.py:9` 自承過渡工具、長期正解=庫內以 raw+除權息事件自建調整序列)。關聯 [[alpha-phase1-anchor-repair]] [[augur-raw-data-defs]]。
