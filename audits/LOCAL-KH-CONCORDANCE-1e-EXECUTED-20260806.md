# LOCAL-KH-CONCORDANCE-1e — EXECUTED 2026-08-06

```text
LOCAL-KH-CONCORDANCE-1e-executed | FZ/GATE-keep
# GO: audits/LOCAL-KH-CONCORDANCE-1e-GO-20260806.md
```

## 變更

- `scripts/build_concordance.py` 增 `--backfill-local-eligible`  
  - 差集補 `domain=local` ∧ `answer_status=eligible` 且句無 concordance 之列  
  - **不推進** `concordance_items_{zh,en}` 主游標（另 meta `conc_bf_local_elig_{lang}` ≤32）

## 跑批

| lang | 句總／待補 | 實插 term 列 |
|---|---|---|
| zh | 966／961（5 已由微測） | 96907 |
| en | 21173／4 | 0（空 tokenize） |

## 驗

| 項 | 結果 |
|---|---|
| local eligible 仍無 conc 的件 | **0／330** |
| 277948 | 23 句中 **22** 有 conc（1 句 0 term＝正常） |
| 主游標 `concordance_items_zh` | 仍 **1815403**（未動） |
| `retrieve_items` 國碩問 | hit **277948**（VERIFY_1e_OK） |

## 計畫

§4 **#1e**／Ρ0.4 → ✅；殘：items 主游標後仍有非 local 待追上（另刀、可選）。

*executed。*
