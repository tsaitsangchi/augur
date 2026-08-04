# SIGN active3 h=20／60 `--record` EXECUTED（2026-08-04）

> **位階**：[I] 執行留痕。  
> **授權**：Steward `SIGN-ACTIVE3-h20-record-go`  
> **待命 SSOT**：`audits/OPT-R3-SIGN-H20-STANDBY-20260804.md`（can-do2）  
> **特徵名**：依 standby／現役集＝`cycle_position_252d`（**非** `cycle_position_20d`；舊名 `lending_fee_rate_mean_20d` 亦不充當 all_active）

---

## 指令（實跑）

```bash
cd /home/hugo/project/augur && \
PYTHONUNBUFFERED=1 ./venv/bin/python scripts/verify_sign_consistency.py --run --record \
  --features cycle_position_252d,inst_cumflow_position_120d,lending_fee_rate_mean_30d \
  --h 20,60
```

| 項 | 值 |
|---|---|
| exit | **0** |
| wall | ≈158 s（本機） |
| log | `/tmp/sign-active3-h20-record-20260804.log` |
| code_sha（落帳） | `0287a25635be…` |

---

## stdout 全文（#9／#10）

```
═══ 符號一致性檢查(SIGN-B;判式=點估計+5 bootstrap 全同號==map.direction)═══
  --record:判定將落帳 feature_sign_check(每個 h 一列)
同尺同窗:as-of panels=102(2018-01-31..2026-06-30);h=[20, 60]
  ✓ cycle_position_252d: PASS(map.direction=+1) h20:PASS(IC均值+0.0455,n=102) h60:PASS(IC均值+0.0880,n=100)
  ✓ inst_cumflow_position_120d: PASS(map.direction=+1) h20:PASS(IC均值+0.0095,n=102) h60:PASS(IC均值+0.0331,n=100)
  ✓ lending_fee_rate_mean_30d: PASS(map.direction=-1) h20:PASS(IC均值-0.0449,n=102) h60:PASS(IC均值-0.0512,n=100)

合計:PASS 3/FAIL 0/不可判 0(不可判=人閘,非通過;全 h 同 PASS 才過=保守,落註)
```

---

## 判定摘要

| 特徵 | map.direction | h=20 | h=60 | 全 h |
|---|---|---|---|---|
| `cycle_position_252d` | +1 | PASS IC均值 **+0.0455** n=102 | PASS IC均值 **+0.0880** n=100 | **PASS** |
| `inst_cumflow_position_120d` | +1 | PASS IC均值 **+0.0095** n=102 | PASS IC均值 **+0.0331** n=100 | **PASS** |
| `lending_fee_rate_mean_30d` | −1 | PASS IC均值 **−0.0449** n=102 | PASS IC均值 **−0.0512** n=100 | **PASS** |

**合計：PASS 3／FAIL 0／不可判 0** → 本輪 **pass**。

同尺同窗：as-of panels=**102**（2018-01-31..2026-06-30）；h∈{20,60}。

---

## 落帳驗收（DB 複核）

`feature_sign_check` 本輪 append **6** 列（3 特徵 × h∈{20,60}）；`checked_at` ≈ 2026-08-04 11:04+08；verdict 全 **PASS**。

| feature | h | direction | point_ic（DB） | n_panels | verdict |
|---|---|---|---|---|---|
| `cycle_position_252d` | 20 | +1 | 0.04553594078419178 | 102 | PASS |
| `cycle_position_252d` | 60 | +1 | 0.0880047248041921 | 100 | PASS |
| `inst_cumflow_position_120d` | 20 | +1 | 0.00946547462864095 | 102 | PASS |
| `inst_cumflow_position_120d` | 60 | +1 | 0.033091411483452696 | 100 | PASS |
| `lending_fee_rate_mean_30d` | 20 | −1 | −0.044866566170432894 | 102 | PASS |
| `lending_fee_rate_mean_30d` | 60 | −1 | −0.05121737297318146 | 100 | PASS |

相對 standby「h=20 FSC 缺」：本輪已補齊三現役於 h=20／h=60。

---

## 不做／護欄

- 未 `SIM --apply`；未寬窗 FinMind／FRED；未 Registry world_* COMMIT；未 git commit  
- 未殺／未再開第二個 A1  
- 未代裁 G13-Q22／G16-ALWAYS（見 `audits/OPT-R3-G13-G16-AWAIT-ARM-20260804.md`）

*完。*
