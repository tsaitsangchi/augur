---
status: go
series: local_ai_kh
kind: auto_lift_pilot
date: 2026-08-08
viewpoint: 2026-08-08T20:50+08:00
board: audits/KH-LOOP-BOARD-REFRESH-20260808.md
plan: reports/augur_local_ai_kh_loop_evolve_opt_plan_20260806_readout.md
paste: "AUTO-LIFT-1c-pilot | FZ/GATE-keep | env=1 session-only | --no-activate-source | lift_log | hold-#1"
self_reported: true
layer: "[I]"
---

# GO｜#1c AUTO-LIFT 試點

## 範圍

| 准 | 禁 |
|---|---|
| 進程／session 設 `AUGUR_KH0_ANSWER_AUTO_LIFT=1`（**不**寫入常駐預設） | 永久改 systemd／默開全服 |
| 錨 `277948`：CLI dry→apply；advise 一刀可選 | web／對話裸 approve |
| `--no-activate-source`（本試點關 T2 activate） | 批量抬整庫；KH＞2；深層宣稱 |
| 驗 `knowhow_answer_lift_log` 有列 | 搶市場 B3 |

## 成功尺

1. 旗關預設仍 off（系統環境未污染）  
2. 試點 session 內：R-cite pass → depth 向 ≤KH2；`lift_log` 有 `lift_id`  
3. 無 source activate（本 GO）  

## 指令

```bash
# A CLI 有界
venv/bin/python scripts/kh0_answer_auto_lift.py --dry-run ...
venv/bin/python scripts/kh0_answer_auto_lift.py --apply --no-activate-source ...
# B 旗（僅本 shell）
AUGUR_KH0_ANSWER_AUTO_LIFT=1  # advise 單次；勿 systemctl 默改
```
