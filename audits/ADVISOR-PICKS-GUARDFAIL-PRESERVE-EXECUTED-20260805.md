---
status: executed
series: advisor_pred_kh
depends_on:
  - audits/ADVISOR-PICKS-SKIP-A-EXECUTED-20260805.md
  - audits/ADVISOR-PRED-KH-AUTOREL-TOPN-EXECUTED-20260805.md
---

# EXECUTED｜PRED-KH：guard fail 不得抹掉 picks 真兆 · 2026-08-05

> **觸發**：Steward 實問「2330個股未來30天走勢?」→ 見 ultracode fallback 注＋「知識庫中無此內容」。  
> **授權**：`diagnose_fix` → `reply_preserve`。  
> **self-reported（#32a）**。

## 1. 根因（親證）

| 層 | 事實 |
|---|---|
| intent | `single_ticker_rel_intent` → `("2330", 20)` ✓ |
| payload | `build_single_ticker_rel_payload` → 1 pick（as-of 2026-05-31、H20）✓ |
| advise | 確定性 picks 表已注入 response ✓ |
| LLM | 常觸 C7「可交易」等黑名單 → `guard.pass=false` |
| **bug** | `oai_compat._reply_text` 對任何公版 guard fail → 一律换成 `知識庫中無此內容`，**整段丟棄 picks 表** |

故用戶看到「知識庫無」＝呈現層謊稱；庫內／預測表皆有真兆。ultracode 前置注僅說明非機械可驗域，**非**本題主因。

## 2. 修復

- `advise` 回傳加 `picks_ground_truth`
- `_reply_text`：該旗為真且 guard fail → 只留 picks 表＋`PICKS_CAVEAT_BLOCKED`；**不**回 NO_KNOWLEDGE
- 無 picks 之路仍走閉集二句（既有測試不變）
- selftest：合成 fail＋TEMP-RED 對偶（無旗標→仍閉集）

## 3. 驗收

- [x] `python -m augur.advisor.oai_compat --selftest`
- [x] `python -m augur.advisor.advise --selftest`
- [x] 同句＋故意「已可交易」LLM → 正文含 2330／表＋機械說明、**無**「知識庫中無此內容」

## 4. 運維

改動常駐 `augur-advisor` → **須重啟 user unit** 後 live chat 才載入新碼（#7）。

## 5. 未做

- 未改誠實句閉集 cardinality  
- 未收緊 picks prompt 禁語（可另項）  
- 本 audit 不默授 archive／commit  
