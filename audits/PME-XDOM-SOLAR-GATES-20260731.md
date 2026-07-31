# PME-XDOM-SOLAR GATES — 進行中／結果（2026-07-31）

> **拍板**：`audits/PME-XDOM-SOLAR-PLAN-APPROVED-20260731.md`  
> **FZ-keep／GATE-keep／NHC-keep**

## Dry-run

```text
venv/bin/python scripts/run_philosophy_evolution.py --local-gates --dry-run --skip-multi-seed
```

（並行 `pg_dump` IO 下，完整 triad dry 單特徵已 >15min；dry 採 `--skip-multi-seed` 僅驗 ISO／MAP／ATTEST／KILL＋IC／ECON 管線，**不作**雙綠憑據。）

| sample | PROM | ECON |
|---|---|---|
| close_x_sbl_balance_level | SKIP | SKIP |
| cycle_position_252d | SKIP | PASS |
| days_since_high_252d | SKIP | FAIL |

Log：`/tmp/pme_solar_gates_dry_20260731.log`

## 正式 `--local-gates`（full triad，無 skip）

```text
PYTHONUNBUFFERED=1 venv/bin/python -u scripts/run_philosophy_evolution.py --local-gates
```

- Log：`/tmp/pme_solar_gates_formal_20260731.log`
- `evolution_run`：**run_id=12**（status=running；coverage 51 unique features）
- 並行 dump 結束後續算；首 mapped 特徵 `cycle_position_252d` 含 multi-seed Ridge（canonical n=34）

**本節數字待正式跑結束後以 stdout／DB 回填（#9）。**

## 雙綠清單

_待正式跑結束回填。未結束前不宣稱雙綠。_

## APPLY

**未開 `PME-APPLY-go`** → 不跑 `apply_evolution_promotions`。
