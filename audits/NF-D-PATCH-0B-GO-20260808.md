---
status: go
series: s4_models
track: NF-D-PATCH
date: 2026-08-08
viewpoint: 2026-08-08T18:50+08:00
prior_0a: audits/NF-D-PATCH-0A-EXECUTED-20260808.md
paste: "NF-D-PATCH-0b-go | FZ/GATE-keep | skip-sync | no-SIM-apply | asof=2026-07-31 | no-promote | no-serve-swap | hold-#1"
self_reported: true
---

# GO｜NF-D-PATCH-0b · SeqPatchTSTSmall · until=2026-07-31／H60

> Steward 貼句認可 → **0b**。  
> **一句**：同尺 Seq／TFM 經濟回測（sequence panel · H60 · seeds≥3）；**評測 only**；**不**塞 registry／serve。

## 護欄

```text
NF-D-PATCH-0b-go | FZ/GATE-keep | skip-sync | no-SIM-apply
| until=2026-07-31 | H60 | seeds=1,2,42 | no-promote | no-serve-swap | hold-#1
```

## 預凍門檻（#32b · 對齊 TFM／FTTR）

| # | 門 | 通過 |
|---|---|---|
| 1 | #11 | seeds=`1,2,42` |
| 2 | #14 vs 冠軍 | 3-seed **min** net Sharpe **>** RankRidge H60 **1.3016** |
| 3 | hit | min hit **≥** **0.6316** |
| 4 | 禁中桶 | 禁單 seed／median 單獨勝出 |

未過 → **STOP promote**。

## 指令

```bash
mkdir -p /tmp/nf-d-patch-0b-0731
PYTHONPATH=src ./venv/bin/python -u scripts/train_sequence_ranker.py --run \
  --family SeqPatchTSTSmall --until 2026-07-31 --horizon 60 --window 60 --seeds 1,2,42 \
  2>&1 | tee /tmp/nf-d-patch-0b-0731/phase0b.log
```

*go。*
