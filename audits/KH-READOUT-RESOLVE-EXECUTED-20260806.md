---
status: executed
series: kh_loop_evolve
date: 2026-08-06
go: audits/KH-READOUT-RESOLVE-GO-20260806.md
plan: reports/augur_local_ai_kh_loop_evolve_opt_plan_20260806_readout.md
paste: "KH-READOUT-RESOLVE-EXECUTED | title-resolve | bounded-fulltext | anchor-guoshuo-pass"
self_reported: true
---

# EXECUTED｜KH-READOUT-RESOLVE · 2026-08-06

## 碼

| 檔 | 變更 |
|---|---|
| `src/augur/knowledge/readout.py` | 意圖／title hint／resolve／有界 chunk→`ItemCitation(via=readout)` |
| `src/augur/advisor/advise.py` | 讀出意圖優先於 ANN；回傳 `readout` meta |

## 錨題

```text
國碩-ERP-GP_DR說明(20211007-4-rman)1：請讀出具體內容
scope=(super, {local}, None)
→ item_ids=[277948] · n_cites=5 · verify_verbatim 全過 · guard pass
· prompt 含 國碩科技／r-man／NBU／tiptop2／/u5/mntnas
```

## 驗

```text
./venv/bin/python -m augur.knowledge.readout --selftest  # ✓
./venv/bin/python -m augur.advisor.advise --selftest     # ✓
```

*executed。本地 Ollama 真跑非本輪必交。*
