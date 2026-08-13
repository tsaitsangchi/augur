# AUTO-LIFT-1C-PILOT-GO · 2026-08-12（刷新試點）

date: 2026-08-12  
kind: ops_go  
status: GO  
open: readout #1c／r14  
prior: `audits/AUTO-LIFT-1C-PILOT-EXECUTED-20260808.md`

## 授權
1. CLI `--selftest`／`--dry-run`／`--apply --no-activate-source`（淺 depth 件）  
2. 進程內 `AUGUR_KH0_ANSWER_AUTO_LIFT=1` **僅本試點行程**；**禁** systemd 默開  
3. 查 `knowhow_answer_lift_log` 新列  

## 禁
默裝 timer／install_services 開旗；web／對話 approve；抬到 >KH2。
