---
status: go
series: econ_establishment
round: r17
date: 2026-08-17
viewpoint: 2026-08-17T08:49+08:00
paste: "E0-ddl-go"
plan: reports/augur_econ_prove_edge_plan_r17_20260817.md
adopted: audits/ECON-PROVE-EDGE-PLAN-R17-ADOPTED-20260817.md
shell: scripts/migrate_econ_establishment_ddl.py
self_reported: true
layer: "[I]"
---

# GO｜E0 經濟確立閘 DDL

Steward 貼 `E0-ddl-go`。對齊已採納計畫 §8 Phase E0。

## 准

- 冪等建 `econ_establishment_gate`＋挪門柱 trigger
- 冪等建 `econ_eval_run`＋只追加 trigger
- `--verify`（含突變：已核准後改 criteria 必須被拒）
- 對帳：`direction_gate` 列數不變；`econ_verdict_rule` 不變

## 禁

- preregister／approve／evaluate 閘
- 寫 `trial_ledger`、跑經濟回測、改 verdict
- 動 `direction_gate` 列、假 B3、promote、sim-apply、塗 established、救 H20
