---
status: accepted
series: kh_ops
track: K3
date: 2026-08-13
viewpoint: 2026-08-13T10:42+08:00
prior: audits/AUTO-LIFT-RESIDENT-EXECUTED-20260812.md
ssot: reports/augur_kh_opt_stepwise_best_next_plan_20260812.md
paste: "K3-ack | ops-flag-ok | code-default=off | no-beyond-KH2 | T0-keep"
self_reported: true
layer: "[I]"
---

# ACK｜K3 AUTO-LIFT · ops 旗可開／碼預設仍 off

```text
K3-ack | ops-flag-ok | code-default=off | no-beyond-KH2 | T0-keep
```

## 親查（2026-08-13）

| 尺 | 值 |
|---|---|
| 碼 `auto_lift_enabled()` 無 env | **False**（預設 off） |
| ops drop-in | `~/.config/systemd/user/augur-advisor.service.d/kh-k3-k7.conf` → `AUGUR_KH0_ANSWER_AUTO_LIFT=1` |
| 既帳 | `AUTO-LIFT-RESIDENT-EXECUTED` |
| 禁 | 抬 **>KH2**；web／對話 approve；默改碼預設為 on |

## 注

若 advisor 以 **非 systemd** 腳本起（本機 `/tmp/kh-serve` 常見），進程 **未必**帶 ops env——熱路徑仍隨該進程環境。要進程內開：重啟 systemd unit 或 export 同旗後重起 serve。

本 ACK **不**改碼預設、**不**授 >KH2。

*ack。*
