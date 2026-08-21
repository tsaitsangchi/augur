---
status: executed
series: kh_ops
track: KH-S0-APPLY
date: 2026-08-21
viewpoint: 2026-08-21T14:57+08:00
go: audits/KH-S0-APPLY-GO-20260821.md
fired: audits/KH-S0-APPLY-FIRED-20260821.md
log: /tmp/kh-s0-apply-20260821/apply.log
paste: "KH-S0-APPLY-EXECUTED | S0=0 | 63→0 | up_to=0 | no-lift>KH2 | no-B3"
elapsed_ms: 20878
self_reported: true
layer: "[I]"
---

# EXECUTED｜KH S0 drain

Steward `KH-S0-apply-go`。一槍 `--apply`。B3 未開火。未抬層。

| 步 | 動作 | RC | 結果 |
|---|---|---|---|
| PRE | 量測（apply 開頭） | 0 | S0 FIRE **63**；S1–S3 ok |
| APPLY-1 | S0 `run_kh_chain --phase advance --up-to 0 --limit 63` | **0** | KH0 不變式：破口已回復為 0（推進前 63） |
| FINAL | `--check` | 0 | **S0 ok（0）** · S1–S3 ok · priority_hit ∅ |

`up_to=0` ⇒ 只種 KH0。本槍未授 S3、未 AUTO-LIFT、未假 B3＠08-21、未 promote、未改 L0。

## 未做

市場刀 A／A2／B · P6 refit · 第二支 WF `--apply`
