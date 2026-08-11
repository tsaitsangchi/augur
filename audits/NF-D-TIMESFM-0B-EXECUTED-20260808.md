---
status: executed
series: s4_models
track: NF-D-TIMESFM
date: 2026-08-08
asof: "2026-07-31"
horizon: 20
depends_on:
  - audits/NF-D-TIMESFM-0B-GO-20260808.md
  - audits/NF-D-TIMESFM-0A-EXECUTED-20260808.md
  - reports/augur_nf_d_timesfm_0b_go_plan_20260808.md
log: /tmp/nf-d-timesfm-0b-0731/phase0b.log
script: scripts/probe_timesfm_phase0b.py
paste: "NF-D-TIMESFM-0b-go | asof=2026-07-31 | H20 | full-core | offline-local | no-promote"
viewpoint: 2026-08-08T18:35+08:00
result: stop_skip_nan_gate
self_reported: true
---

# EXECUTED｜NF-D-TIMESFM-0b · asof=2026-07-31／H20

> **誠實 STOP／SKIP** · 先決 NaN 覆蓋率未過 · **未**跑全 core hit 尺 · offline-local · 未 registry · 未 serve · hold-#1  
> CLI：`probe_timesfm_phase0b.py --run --asof 2026-07-31 --horizon 20 --n-stocks 300`

## 結果

| 尺 | 值 |
|---|---|
| 權重／載入 | 本機可載（對齊 0a） |
| finite_cov（預熱 8 試） | **0.000**（門 ≥ 0.5） |
| 全 core hit vs naive | **未跑**（先決擋） |
| 證據門 | **無**（蓋不住就沒有） |
| 升格 | **STOP promote**（預凍＋本輪 SKIP） |

### 誠實殘差

對齊 `NF-D-TIMESFM-0A-EXECUTED`：本機 CPU 上 TimesFM-2.5 `forecast` 回全 NaN → 分數皆非 finite。**≠** stub 塗綠；**≠** 默換 CUDA／hub 下載解鎖。

再開條件（另句）：可證非 NaN 覆蓋率的環境／compile 設定，或改 SKIP-closed 族帳直至另證。

```text
# 本輪收口
NF-D-TIMESFM-0b @0731 = STOP/SKIP (nan-gate)
# ≠ Chronos／Moirai 0b 併卷塗綠；≠ registry／serve
```

*完。勿重掃當綠／默升格。*
