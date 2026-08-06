---
status: executed
series: retrieval
date: 2026-08-06
trigger: local know-how miss (國碩-ERP-GP_DR item=277948)
paste: "LOCAL-KH-HIT-FIX-EXECUTED | exact-cap | drop-unigram | latin-in-zh | selftest-pass"
self_reported: true
---

# EXECUTED｜local know-how 檢索命中修復 · 2026-08-06

## 根因

1. zh 問句 tokenize 帶 **CJK 單字** → concordance exact 占滿 `k` → **ANN 不跑**
2. 混合問句（國碩＋ERP／Oracle／RMAN）之 **拉丁詞被 zh tokenize 丟棄**
3. 本件 **無 concordance 列** → 只能靠 ANN；ANN 被擠掉即永不可見  
   （本件 ANN 全域 rank=1，語意本身沒問題）

## 修（`src/augur/philosophy/retrieval.py`）

- `_item_query_terms`：≥2 字 CJK＋補 en 拉丁詞；丟單字
- exact：`HAVING` 至少 2 辨識詞（詞數≥2 時）；`exact_cap = k//2` 預留 ANN

## 驗（國碩 DR 問句 · scope=super＋local）

| 步 | hit 277948 |
|---|---|
| `retrieve_items` | ✓（via=ann） |
| `retrieve_all` | ✓ |
| `relevant_citations` | ✓ |
| `advise` cites＋guard | ✓ |

*殘：本件仍無 concordance（資料層另建可再加 exact）；非本輪。*
