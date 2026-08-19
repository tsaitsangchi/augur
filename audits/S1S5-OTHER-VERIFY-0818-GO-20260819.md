---
status: go
series: s1s5_loop
track: other-verify
date: 2026-08-19
viewpoint: 2026-08-19T14:21+08:00
paste: "列出所有問題處理的最佳下一步?可先做或同步做? 再進行其他模型驗証"
plan: reports/augur_s1s5_asof_verify_best_next_r19_20260819.md
nav: reports/augur_opt_stepwise_all_problems_r19_20260819.md
self_reported: true
layer: "[I]"
---

# GO｜r16 閉環全段下一步＋其他模型驗証（V0／V1 唯讀）

Steward：依 S1→S5 列出全問題最佳下一步／可先／可同步，**再進行其他模型驗証**。

| 准 | 禁 |
|---|---|
| 寫 r19 閉環問題板 | 假 B3＠08-19 |
| V0 盤點＠08-18；`--track other --dry-plan` | `--track other --apply`（rc=6） |
| V1 `--ic --oos`／`--walk --oos`（dry-run 不寫庫） | promote；重掃 0812 NF；開 VECM／TCN／NB／RL |
| `--scan` 未齊日 | HIST-ASOF `--apply`（另句）；`--force-direction` |
