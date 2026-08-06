# KH compact live 口吻／逾時最佳化 — EXECUTED 2026-08-06

```text
KH-COMPACT-LIVE-OPT-executed | FZ/GATE-keep | against=KH-ANCHOR-REGRESSION-1h-LIVE
```

## 對症

| 現象 | 處置 |
|---|---|
| 想題中洩「我需要從這些…」 | `polish`：`_strip_mid_think`＋`_prefer_step_lines` |
| `- [1]` 非 `1.` | `_normalize_cite_bullets` → `1.` `2.` |
| env `NUM_PREDICT` 不進 llm | `make_llm_fn._augur_bind_options`；`wrap_compact_llm` 合併 `num_predict`（預設 **480**） |
| CPU 逾時／cite 過重 | 預設 `CITE_CHARS=2000`／`CITE_N=3` |

## 驗

- `compact_answer --selftest` 全過（含 live_leak 拋光／bind）  
- 對 `/tmp/kh_1h_live_Q1b.json` 原文拋光 → **去掉想題、成 1./2. 條列**

## 運維

改碼後重啟 `augur-advisor`。旋鈕：`AUGUR_COMPACT_NUM_PREDICT`／`AUGUR_COMPACT_CITE_*`／`AUGUR_SERVE_NUM_PREDICT`。

*executed。*
