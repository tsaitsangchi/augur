---
status: go
series: s4_models
track: NF-A-FTTR
date: 2026-08-08
viewpoint: 2026-08-08T00:56+08:00
prior_0a: audits/NF-A-FTTR-0A-EXECUTED-20260808.md
paste: "NF-A-FTTR-0b-go | FZ/GATE-keep | skip-sync | no-SIM-apply | asof=2026-07-31 | H60 | seeds=1,2,42 | no-promote | no-serve-swap | hold-#1"
self_reported: true
---

# GO｜NF-A-FTTR-0b · RankFTTransformer · until=2026-07-31／H60

> Steward：接續「FT-Transformer 純 torch」→ **0b**。  
> **一句**：同尺 Wave-A／Seq 經濟回測（prodset · H60 · seeds≥3）；**portfolio 評測支路 only**；**不**塞 `ALL_FAMILIES`／registry。

## 護欄

```text
NF-A-FTTR-0b-go | FZ/GATE-keep | skip-sync | no-SIM-apply | NF-pause-others
| until=2026-07-31 | H60 | seeds=1,2,42 | no-promote | no-serve-swap | hold-#1
```

## 預凍門檻（#32b）

| # | 門 | 通過 |
|---|---|---|
| 1 | #11 | seeds=`1,2,42` |
| 2 | #14 vs 冠軍 | 3-seed **min** net Sharpe **>** `RankRidge_H60` **1.3016** |
| 3 | hit | min hit **≥** **0.6316**（與 Wave-A 同慣例） |
| 4 | 禁中桶 | 禁單 seed／median 單獨勝出 |

未過 → **STOP promote**。

## 指令

```bash
PYTHONPATH=src ./venv/bin/python -u scripts/probe_fttr_phase0b.py --run \
  --since 2021-01-01 --until 2026-07-31 --horizon 60 --seeds 1,2,42
```

log：`/tmp/nf-a-fttr-0b-0731/phase0b.log`

*go。*
