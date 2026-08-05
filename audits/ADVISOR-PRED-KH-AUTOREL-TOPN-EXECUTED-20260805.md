---
status: executed
series: advisor_integration
depends_on:
  - reports/augur_advisor_predict_as_knowledge_plan_20260805.md
---

# ADVISOR-PRED-KH Phase 1b EXECUTED — auto_rel_topn（2026-08-05）

> **裁示**：plan `plan_only`→拍板 `go_b2`＋AskQuestion **`auto_rel_topn`**（「未來N天上漲機率 topK」→ 改答相對機率 TopK）。  
> **self-reported（#32a）**。

---

## 做了什麼

| 項 | 落地 |
|---|---|
| 意圖 | `rel_prob_topk_intent`／`single_ticker_rel_intent`（`relevance.py`） |
| payload | `build_rel_prob_topk_payload`／`build_single_ticker_rel_payload` |
| 分派 | `oai_compat.chat_completion`：選股 → TopK → 單股 → empty |
| 方向短路 | `advise`：若已有 `picks` **不**短路（改走真兆＋`prob_note` 改寫說明） |
| 服務 | 重啟 `augur-advisor`／`augur-chat` |

## 煙測（mock LLM）

問句：`未來30天上漲機率最高的top 3`  
intent=`(3,20)`；payload as-of **2026-05-31** picks：

1. 2330 台積電 p≈0.5874（econ dead）  
2. 2542 興富發  
3. 2347 聯強  

→ **非**「知識庫中無此內容」；guard pass；附「非上漲機率」disclaimer。

## 誠實邊界

- 數字＝`p_beat_median`，**不是**絕對上漲機率  
- `direction_gate` pass=0 不變  
- MC 數字仍不進 chat  

## 追加：大盤「漲還是跌」（同日）

無股號＋「上漲還是下跌的機率高」→ `market_binary_dir_intent` → 方向拒答附加**【預測知識通道・大盤】**：結論仍是絕對方向不可用（閘 pass=0／判死 12），周邊真兆（截面中位≈半、研究列未過閘）明示非明牌。服務已重啟。

## 回歸 smoke（同日；批次 `rec_1_2_3`）

庫內重跑（`/tmp/pred-kh-smoke.log`）：

| 題 | 結果 |
|---|---|
| top3 上漲機率 | intent `(3,20)`；as-of **2026-05-31** picks **2330／2542／2347**（p≈0.5874／0.5869／0.5864；econ dead） |
| 2330 未來30天走勢 | intent＋單股 payload 1 pick／同 p |
| 無股號漲跌 | `market_binary_dir_intent`＋拒答含「預測知識通道」 |
| relevance／payload／prompt `--selftest` | 全通過 |

**PRED-KH smoke PASS**。另：`check_vendor_binding --gate` 現紅於 `src/augur/advisor/payload.py` `TaiwanStockInfo` **1→3**（PRED-KH 名稱解析增處）——**非本 smoke 範圍**、另帳 WM36。

*同日追加。*
