---
status: executed
series: local_ai_kh
track: K4
date: 2026-08-13
viewpoint: 2026-08-13T10:43+08:00
script: scripts/kh_private_smoke.py
log: /tmp/kh-k4-private-smoke-0813/run.log
prior: audits/KH-PRIVATE-SMOKE-EXECUTED-20260812.md
paste: "K4-PRIVATE-SMOKE-EXECUTED | 4/4 PASS | ASR=via | PDF-C-no-ASR | no-promote"
self_reported: true
layer: "[I]"
---

# EXECUTED｜K4 `kh_private_smoke` · 2026-08-13

| 案 | 結果 |
|---|---|
| avi 未登入 → 0 | **PASS** |
| avi super → **1818835**＋via=asr | **PASS** |
| avi owner:1 → 同上 | **PASS** |
| doc super → **1818691** | **PASS** |

```text
SMOKE PASS · RC=0
```

守：ASR＝owned_local／via；**≠** PDF-C；未改 RBAC／未抬層。

*完。*
