---
status: executed
series: advisor_integration
depends_on:
  - reports/augur_advisor_picks_skip_heavy_retrieve_plan_20260805.md
---

# picks_skip_A EXECUTED（2026-08-05）

> **裁示**：Steward `picks_skip_A-go`＋AskQuestion `skip_evo_too`。  
> **self-reported（#32a）**。

## 行為

`advise()` 當 `payload.picks` 非空且非 Mode B：

1. **不**呼叫 `retrieve_fn`／譯英／KH0／KH9 重排 → `citations=[]`  
2. **不**注入 evolution_md  
3. **不**跑 K1 `_bridge_links`（再開庫）  
4. lexicon（若有 `lex_terms`）仍可  
5. guard／確定性 picks 表注入**不變**

## 驗收

| 檢 | 結果 |
|---|---|
| `--selftest` | 全通過；含 retrieve 絆線 |
| TEMP-RED | 改 `if False and has_picks…` → rc≠0；已還原 |
| DB smoke | `build_single_ticker_rel_payload(2330)`＋boom retrieve → 零呼叫；表含 2330 |
| 服務 | `systemctl --user restart augur-advisor` |

## 誠實邊界

- 知識／哲學無 picks 題 → 仍全速檢索  
- 11GB 仍可能因他因 OOM；本改只去掉 picks 路徑上的 embed  

*完。*
