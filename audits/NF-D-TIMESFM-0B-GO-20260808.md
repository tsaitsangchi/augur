---
status: go
series: s4_models
track: NF-D-TIMESFM
date: 2026-08-08
viewpoint: 2026-08-08T18:30+08:00
prior_0a: audits/NF-D-TIMESFM-0A-EXECUTED-20260808.md
plan: reports/augur_nf_d_timesfm_0b_go_plan_20260808.md
paste: "NF-D-TIMESFM-0b-go | FZ/GATE-keep | skip-sync | no-SIM-apply | asof=2026-07-31 | H20 | full-core | offline-local | no-promote | no-serve-swap | hold-#1"
self_reported: true
---

# GO｜NF-D-TIMESFM-0b · 全 core＠2026-07-31／H20

> Steward：下一族再開 → **TimesFMRank25 · 0b** · asof=**2026-07-31**。

```text
NF-D-TIMESFM-0b-go | FZ/GATE-keep | skip-sync | no-SIM-apply
| asof=2026-07-31 | H20 | full-core | offline-local | no-promote | no-serve-swap | hold-#1
# 先決：forecast 非 NaN 覆蓋率 gate；否則 STOP／SKIP
```

| 項 | 裁 |
|---|---|
| 腳本 | `scripts/probe_timesfm_phase0b.py` |
| 尺 | mean(TimesFM hit) > mean(naive) → 有證據；升格仍 **STOP promote** |
| hub | **禁**；`HF_HUB_OFFLINE`／`local_files_only` |
| registry／serve | **禁** |
| NF-pause／#1 | keep／hold |

CLI：

```bash
mkdir -p /tmp/nf-d-timesfm-0b-0731
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
  ./venv/bin/python -u scripts/probe_timesfm_phase0b.py --run \
  --asof 2026-07-31 --horizon 20 --n-stocks 300 \
  2>&1 | tee /tmp/nf-d-timesfm-0b-0731/phase0b.log
```

*go。*
