---
status: executed
series: infrastructure
date: 2026-08-07
kind: script_landed
script: scripts/explore_struct_cycles.py
depends_on:
  - audits/STRUCT-CYCLE-EXPLORE-EXECUTED-20260807.md
  - audits/STRUCT-CYCLE-EXPLORE-PLAN-ADOPTED-20260807.md
paste: "STRUCT-CYCLE-EXPLORE 探針收成"
viewpoint: 2026-08-07T19:50+08:00
self_reported: true
---

# EXECUTED｜STRUCT 探針收成 · `explore_struct_cycles.py`

> Steward：要把 STRUCT 探針收成 → **script＋`--selftest`**（零 DB）  
> `--selftest` RC=0 · `--run` 復現雙向 **5**／三角 **5**（與探索帳一致）

## CLI

```bash
python scripts/explore_struct_cycles.py --selftest
python scripts/explore_struct_cycles.py --run
python scripts/explore_struct_cycles.py --run --json
```

**仍不做**：解圈改碼、DDL、U0 80／97 REGISTRY-GO。

*完。*
