---
status: fired
series: s1s5_loop
track: hist-asof-code
date: 2026-08-19
go: audits/HIST-ASOF-CODE-GO-20260819.md
paste: "HIST-ASOF-code | fake-b3-date | no-apply@08-12 | no-fake-B3@08-19 | no-promote"
self_reported: true
layer: "[I]"
---

# FIRED｜歷史 as-of 殼／探針（改程式；不訓）

```text
python -m augur.core.asof_ready --selftest
python scripts/check_asof_ready.py --selftest
bash scripts/run_asof_collect_train_verify.sh --selftest
python scripts/check_asof_ready.py --fake-b3-date
python scripts/check_asof_ready.py --date 2026-08-12
python scripts/check_asof_ready.py --scan
python scripts/verify_asof_families.py --date 2026-08-18
python scripts/verify_asof_families.py --date 2026-08-19
bash scripts/run_asof_collect_train_verify.sh --date 2026-08-12 --dry-plan --track all
bash scripts/run_asof_collect_train_verify.sh --date 2026-08-18 --dry-plan --track other
```

候 EXECUTED。零 `--apply`。
