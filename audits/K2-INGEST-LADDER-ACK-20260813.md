---
status: accepted
series: kh_ops
track: K2
date: 2026-08-13
viewpoint: 2026-08-13T10:41+08:00
prior_b: audits/KH-INGEST-TRIGGER-B-ADOPTED-20260812.md
prior_c: audits/KH-INGEST-TRIGGER-C-EXECUTED-20260812.md
ssot: reports/augur_kh_opt_stepwise_best_next_plan_20260812.md
paste: "K2-ack | A→B→C 已收口 | apply=opt-in | check-default | no-timer"
self_reported: true
layer: "[I]"
---

# ACK｜K2 ingest 階梯 · 已收口／apply 選開

```text
K2-ack | A→B→C 已收口 | apply=opt-in | check-default | no-timer
```

## 親查（2026-08-13）

| 尺 | 值 |
|---|---|
| 階梯 | B ADOPTED · C EXECUTED（訊號＋CLI＋hook） |
| `enabled()` | **True**（量測開） |
| `apply_enabled()` | **False**（無 env；須 `--apply` 或 `AUGUR_KH_INGEST_TRIGGER_APPLY=1`） |
| timer／cron | **未**默裝 |
| LIVE | `priority_hit: ∅`（無強制刀） |

守：apply **選開**；不因本 ACK 改默認開 apply。

*ack。*
