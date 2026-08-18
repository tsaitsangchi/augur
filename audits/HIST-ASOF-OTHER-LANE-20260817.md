---
status: executed
series: s1s5_loop
date: 2026-08-17
viewpoint: 2026-08-17T16:40+08:00
layer: "[I]"
self_reported: true
paste: "HIST-ASOF-other-lane | track=other rc=6 | no-apply | NF-pause | no-fake-B3"
---

# EXECUTED｜其他模型歷史 as-of 車道（程式；未訓）

Steward 再問：全問題下一步＋其他模型驗証＋過去 as-of 能否收特徵／訓／驗、並改程式。

- **答**：能——正門是 D≤價頂、共用當時 `feature_values`。`--track A|all` 只覆蓋截面 8 族（＋價頂方向臂）。**不是** VECM／TCN／NB／RL／0812 NF。
- **程式**：`--track other` → **rc=6** fail-loud（假 B3 仍 rc=3 優先）。探針印其他車道一行。
- **未** `--apply`；**未**開 NF；**未**假 B3＠08-15／16／17。
