---
status: executed
series: s4_models
track: NF-D-TIMESFM
date: 2026-08-08
depends_on:
  - audits/NF-D-TIMESFM-0A-GO-20260808.md
  - audits/NF-D-TIMESFM-PLAN-ADOPTED-20260808.md
asof_pin: "2026-07-31"
paste: "NF-D-TIMESFM-0a-go | FZ/GATE-keep | no-train-prod | hold-#1 | asof=2026-07-31 | offline-local"
viewpoint: 2026-08-08T00:20+08:00
self_reported: true
---

# EXECUTED｜NF-D-TIMESFM-0a · `TimesFMRank25`＋selftest

> RC=0 · stub selftest **全通過** · 離線**權重可載**但本機 CPU `forecast` 回 **全 NaN** → 真載路徑 **誠實 SKIP** · 零 DB · 未 registry · hold-#1  
> asof 釘（後續 0b）＝**2026-07-31**

| 項 | 值 |
|---|---|
| 模組 | `src/augur/models/timesfm_rank.py` |
| class | **`TimesFMRank25`** · `google/timesfm-2.5-200m-pytorch` |
| 分數口徑 | 複用 `chronos_rank.score_from_quantiles` |
| 預設 | `local_files_only=True` |
| selftest stub | **全通過** |
| selftest real | 權重載入 OK；`forecast` 全 NaN → **SKIP**（非塗綠可用） |

### 誠實殘差

本機（torch CUDA unavailable）TimesFM-2.5 `forecast` 對常量／隨機遊走／線性上下文皆回 NaN — **0b 不得默當可跑**；須另證非 NaN 覆蓋率或 SKIP 收口／換環境。

未做：0b／registry／serve／Chronos 0b 併跑。

```text
NF-D-TIMESFM-0b-go | … | asof=2026-07-31 | no-promote | offline-local
# 先決：forecast 非 NaN 覆蓋率 gate；否則 STOP／SKIP
```

*完。*
