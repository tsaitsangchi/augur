---
status: executed
series: s4_models
track: NF-D-CHRONOS
date: 2026-08-08
depends_on:
  - audits/NF-D-CHRONOS-0A-GO-20260808.md
  - audits/NF-D-CHRONOS-PLAN-ADOPTED-20260808.md
asof_pin: "2026-07-31"
paste: "NF-D-CHRONOS-0a-go | FZ/GATE-keep | no-train-prod | hold-#1 | asof=2026-07-31 | offline-local"
viewpoint: 2026-08-08T00:15+08:00
self_reported: true
---

# EXECUTED｜NF-D-CHRONOS-0a · `ChronosRankBolt`＋selftest

> RC=0 · stub selftest **全通過** · 離線真載本地權重 **可用** · 零 DB · 未 registry · hold-#1  
> asof 釘（後續 0b）＝**2026-07-31**

| 項 | 值 |
|---|---|
| 模組 | `src/augur/models/chronos_rank.py` |
| class | **`ChronosRankBolt`** · `amazon/chronos-bolt-small` |
| 分數 | `log(q50_end / last_px)` |
| 預設 | `local_files_only=True`；缺權重＝RuntimeError／SKIP |
| selftest | stub **8／8**；`AUGUR_CHRONOS_REAL_SELFTEST=1` 真載 **OK**（~12s） |

未做：庫內 0b＠07-31／TimesFM 雙臂／registry／serve／arena dgate 翻案。

```text
NF-D-CHRONOS-0b-go | FZ/GATE-keep | skip-sync | no-SIM-apply | asof=2026-07-31 | no-promote | no-serve-swap | hold-#1 | offline-local
```

*完。*
