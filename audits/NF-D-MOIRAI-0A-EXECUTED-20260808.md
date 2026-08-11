---
status: executed
series: s4_models
track: NF-D-MOIRAI
date: 2026-08-08
depends_on:
  - audits/NF-D-MOIRAI-0A-GO-20260808.md
  - audits/NF-D-MOIRAI-PLAN-ADOPTED-20260808.md
asof_pin: "2026-07-31"
paste: "NF-D-MOIRAI-0a-go | FZ/GATE-keep | no-train-prod | hold-#1 | asof=2026-07-31 | offline-local"
viewpoint: 2026-08-08T00:24+08:00
self_reported: true
---

# EXECUTED｜NF-D-MOIRAI-0a · `MoiraiRank2Small`＋selftest

> RC=0 · stub **全通過** · 離線真載本地權重 **可用＋predict finite** · 零 DB · 未 registry · hold-#1  
> asof 釘（後續 0b）＝**2026-07-31**

| 項 | 值 |
|---|---|
| 模組 | `src/augur/models/moirai_rank.py` |
| class | **`MoiraiRank2Small`** · `Salesforce/moirai-2.0-R-small` |
| 分數 | 複用 `chronos_rank.score_from_quantiles` |
| 預設 | `local_files_only=True` |
| selftest stub | **通過** |
| selftest real | **OK**（~11s；gluonts Period FutureWarning 非阻斷） |

對照：TimesFM 本機 forecast 全 NaN；**Moirai 本機可推論** → 0b 候選高於 TimesFM。

未做：0b／registry／serve。

```text
NF-D-MOIRAI-0b-go | FZ/GATE-keep | skip-sync | no-SIM-apply | asof=2026-07-31 | no-promote | offline-local | hold-#1
```

*完。*
