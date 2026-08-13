# K7 產品預設 8b · EXECUTED

date: 2026-08-12  
kind: code_executed  
status: EXECUTED  
go: `audits/KH-K7-PRODUCT-8B-GO-20260812.md`  
prior: `audits/KH-K7-STEPWISE-TONE-EXECUTED-20260812.md`

## 落地
| 項 | 內容 |
|---|---|
| `compact_answer.COMPACT_NUM_PREDICT` | 預設 **960**（env 可覆寫） |
| `effort.prefer_8b_for_stepwise` | 步驟／操作題＋4b → 同 effort **8b** |
| `oai_compat` | resolve 後套用上述升檔 |
| systemd／install | `AUGUR_COMPACT_NUM_PREDICT=960` · `AUGUR_STEPWISE_FORCE_8B=1` |
| `frontend_tiers.default_tier` | 已是 `augur-8b-fast`（未改） |

## 自測
`python -m augur.advisor.effort --selftest` · `compact_answer --selftest` → 全通過。

## paste
```text
KH-K7-PRODUCT-8B-EXECUTED | predict=960 | stepwise-4b→8b | default=augur-8b-fast
```
