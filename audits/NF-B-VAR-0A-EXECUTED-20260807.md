---
status: executed
series: s4_models
track: NF-B-VAR
date: 2026-08-07
depends_on:
  - audits/NF-B-VAR-0A-GO-20260807.md
  - audits/NF-B-VAR-PLAN-ADOPTED-20260807.md
asof_pin: "2026-07-31"
paste: "NF-B-VAR-0a-go | FZ/GATE-keep | no-train-prod | hold-#1"
viewpoint: 2026-08-07T14:52+08:00
self_reported: true
---

# EXECUTED｜NF-B-VAR-0a · `VarSmall` 薄殼＋selftest

> RC=0 · **零 DB 探針** · **no-train-prod** · 未 registry · 未 serve · hold-#1  
> asof 釘（後續 0b）＝**2026-07-31**

## 產出

| 項 | 值 |
|---|---|
| 模組 | `src/augur/models/classical_ts.py` |
| class | **`VarSmall`**（`family=VarSmall`） |
| 契約 | k∈[2,5] · 預設 p=1 · forecast `(h,k)` |
| selftest | `python -m augur.models.classical_ts --selftest` → **全通過** |

## 未做

- 庫內 0b（須 `NF-B-VAR-0b-go`｜asof=2026-07-31｜H20）  
- CHK／registry／SERVE-SWAP  
- VECM  

下一句示意：

```text
NF-B-VAR-0b-go | FZ/GATE-keep | skip-sync | no-SIM-apply | asof=2026-07-31 | H20 | no-promote | no-serve-swap | hold-#1
```

*完。*
