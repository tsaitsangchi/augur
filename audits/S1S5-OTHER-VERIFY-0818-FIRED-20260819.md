---
status: fired
series: s1s5_loop
track: other-verify
date: 2026-08-19
viewpoint: 2026-08-19T14:21+08:00
go: audits/S1S5-OTHER-VERIFY-0818-GO-20260819.md
paste: "S1S5-OTHER-VERIFY-FIRED | D≤08-18 | V0/V1 dry | no-apply | no-promote | no-fake-B3@08-19"
self_reported: true
layer: "[I]"
---

# FIRED｜其他模型驗証 V0／V1＠價頂 08-18

```text
python scripts/check_asof_ready.py --scan
python scripts/verify_asof_families.py --date 2026-08-18
python scripts/verify_asof_families.py --date 2026-08-19
bash scripts/run_asof_collect_train_verify.sh --date 2026-08-18 --dry-plan --track other
python scripts/verify_asof_families.py --walk --oos --horizon 5 --limit 6
python scripts/verify_asof_families.py --walk --oos --horizon 10 --limit 4
python scripts/verify_asof_families.py --date 2026-08-07 --ic --oos
```

候 EXECUTED。零寫 `prediction_values`。
