---
status: go
series: s4_models
track: NF-D-MOIRAI
date: 2026-08-08
viewpoint: 2026-08-08T00:28+08:00
prior_0a: audits/NF-D-MOIRAI-0A-EXECUTED-20260808.md
paste: "NF-D-MOIRAI-0b-go | FZ/GATE-keep | skip-sync | no-SIM-apply | asof=2026-07-31 | H20 | full-core | no-promote | no-serve-swap | offline-local | hold-#1"
self_reported: true
---

# GO｜NF-D-MOIRAI-0b · 全 core＠2026-07-31／H20

> Steward：認可「本機可跑 → 0b」→ 本 GO。  
> **一句**：`MoiraiRank2Small` 方向 hit vs naive（月步 WF）；**offline-local**；**no-promote**。

## 護欄

```text
NF-D-MOIRAI-0b-go | FZ/GATE-keep | skip-sync | no-SIM-apply | NF-pause-others
| asof=2026-07-31 | H20 | full-core | no-promote | no-serve-swap | offline-local | hold-#1
```

## 預凍門檻（#32b）

| # | 門 | 通過 |
|---|---|---|
| 1 | 量尺 | 月步 WF · 標籤與上下文皆 ≤asof |
| 2 | 證據 | mean(Moirai hit) **>** mean(naive hit) → **有證據** |
| 3 | 升格 | **禁**；即使有證據亦 **STOP promote**／no-registry |

未過證據門 → **STOP／無證據**（誠實）。

## 指令

```bash
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONPATH=src \
  ./venv/bin/python -u scripts/probe_moirai_phase0b.py --run \
  --asof 2026-07-31 --horizon 20 --n-stocks 300
```

log：`/tmp/nf-d-moirai-0b-0731/phase0b.log`

*go。*
