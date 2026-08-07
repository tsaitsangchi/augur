---
status: executed
series: advisor_honesty
date: 2026-08-07
viewpoint: 2026-08-07T09:25+08:00
paste: "DIR-ADVICE-BUNDLE | hard-refuse-abs | relative-or-gap | no-fake-%"
steward: "要能給建議（bundle）"
self_reported: true
---

# EXECUTED｜絕對方向硬拒＋誠實建議包 · 2026-08-07

## 根因（0050／十天）

1. 股號正則禁 `0xxx` → ETF **0050** 意圖漏失 → 空拒。  
2. 問「十天」未對齊短尺 → 現改 **H20**（明示非十日絕對）。  
3. `0050` **不在** `prediction_probability` 宇宙 → 不可捏相對／絕對％。  
4. 拒答句缺「可建議」區塊 → Steward 感知＝只能拒絕。

## 做了什麼

| 檔 | 變動 |
|---|---|
| `relevance.py` | ETF 四碼；年號剔除；10 天→H20；`extract_tw_tickers` |
| `prompt.py` | `_advice_bundle_for_query` 掛在 `build_direction_refusal` |
| `advise.py` | 宇宙外單股 → 建議包短路（含純相對問） |

## 驗收

- 0050 十天漲跌機率問：硬拒絕對％＋建議包（宇宙無列／H20／MC／怎麼問）。  
- 2330 同型問：改寫相對 `P(beat)`＋econ＋GATE 未過（非看漲％）。  
- `relevance`／`prompt` selftest 全過。  
- advisor `:8399` 已重載。

## 迭代（同日・Steward「我要建議」）

宇宙外 ETF 再補：
- 歷史約十日上漲**頻度**（明示過去≠未來）  
- 權值股相對快照（≠0050 方向）  
- 行動清單（MC／改問個股／禁当进场％）

*完。*
