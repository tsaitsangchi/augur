---
status: executed
series: kh_ops
track: KH-INGEST-APPLY
date: 2026-08-13
viewpoint: 2026-08-13T10:09+08:00
go: audits/KH-INGEST-APPLY-S0-S3-GO-20260813.md
fired: audits/KH-INGEST-APPLY-S0-S3-FIRED-20260813.md
log: /tmp/kh-ingest-apply-0813/s0-s3.log
paste: "KH-INGEST-APPLY-S0-S3-EXECUTED | S0=0 | S3 zh+en lag=0 | priority_hit=∅ | no-autolift | no-timer"
self_reported: true
layer: "[I]"
---

# EXECUTED｜kh_ingest_trigger --apply · S0→S3（含 en）

> Steward：直接開。一次一槍×3（S0 → S3-zh → S3-en）。未開 AUTO-LIFT／timer。

## 結果

| 步 | 動作 | RC | 結果 |
|---|---|---|---|
| PRE | `--check` | 0 | S0 FIRE×6；S3 zh lag≈369／en≈292 |
| APPLY-1 | S0 `run_kh_chain … --up-to 0 --limit 6` | **0** | KH0 破口 **6→0** |
| MID | `--check` | 0 | S0 ok；S3 仍 FIRE |
| APPLY-2 | S3 `build_concordance … zh --limit 5000` | **0** | zh 游標→1936271；句 316／列 10787 |
| APPLY-3 | S3 `… en --limit 5000` | **0** | en 游標→1936188；句 53／列 2197 |
| FINAL | `--check` | 0 | **S0 ok · S3 ok · `priority_hit: ∅`** |

## 終態（親查）

```text
S0 kh0_breach=0
S3 zh lag_est=0 · en lag_est=0
priority_hit: ∅ → no-op
```

## 未做

≠ AUTO-LIFT · ≠ cron／timer · ≠ KH8 加深 · ≠ 市場 tip／B3

*完。*
