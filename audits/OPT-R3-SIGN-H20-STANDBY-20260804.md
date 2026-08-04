# SIGN active3 h=20｜待命帳（can-do2 · 2026-08-04）

> **位階**：[I]。**授權邊界**：用戶列 SIGN 於「另句」→ **本輪不跑 `--record`**。  
> **等候句**：`SIGN-ACTIVE3-h20-record-go`  
> **上游**：`audits/OPT-R3-SIGN-MC-LIGHT-20260804.md`

---

## 現況（2026-08-04 `--record` 後；見 EXECUTED）

| 現役特徵 | h=20 FSC | h=60 FSC |
|---|---|---|
| `cycle_position_252d` | PASS | PASS |
| `inst_cumflow_position_120d` | PASS | PASS |
| `lending_fee_rate_mean_30d` | PASS | PASS |

- MC cone as-of 08-03／h=30／52×雙法＝庫內已齊（前輪）。  
- 舊名 `lending_fee_rate_mean_20d`＝**非**現役；授權後**不**對它充當 all_active。

---

## 待命：授權後精確指令

**勿現跑。** 收到 `SIGN-ACTIVE3-h20-record-go` 後建議：

```bash
cd /home/hugo/project/augur && \
PYTHONUNBUFFERED=1 ./venv/bin/python scripts/verify_sign_consistency.py --run --record \
  --features cycle_position_252d,inst_cumflow_position_120d,lending_fee_rate_mean_30d \
  --h 20,60
```

護欄：不 `SIM --apply`；不寬窗 FinMind／FRED；與 I3／heavy_slot 錯開。

---

## 本輪動作

| 項 | 結果 |
|---|---|
| `--record` | ✅ **已跑**（收到 `SIGN-ACTIVE3-h20-record-go`）→ `audits/OPT-R3-SIGN-ACTIVE3-H20-RECORD-EXECUTED-20260804.md`（PASS 3／0；h=20／60 落帳 6 列） |
| 本檔 | 狀態＋就緒指令留痕；執行後指向 EXECUTED |

*完。*
