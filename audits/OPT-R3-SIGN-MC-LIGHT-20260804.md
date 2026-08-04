# 符號尺／MC cone 有界輕量帳（2026-08-04）

> **位階**：[I]。**授權**：批次「符號尺有界 `--record`／MC cone as-of」（次急）。  
> **硬禁**：不 `SIM-FIRST-CELL --apply`；不寬窗 FinMind／FRED；不假設 `lending_fee_rate_mean_20d` 現役。

---

## 1. MC cone as-of（庫內）

| 項 | 結果 |
|---|---|
| 既有 EXECUTED | `audits/MC-ASOF-20260803-RERUN-20260804.md` |
| 本輪親查 | `asof_date='2026-08-03'` ∧ cone ∧ h=30：**52** block + **52** iid；distinct target=**52** |
| 舊 freeze 列 | `2026-05-31` cone **520** 仍並存（未刪） |
| 本輪動作 | **未**重跑全宇宙／多 horizon（已達 UI／Top10 口徑）；`simulate_mc_paths` 無參數唯讀現況 ✓ |
| API | **零**新抓 |

→ **A4 主目標（08-03／h=30／52 檔雙法）＝已完成（前輪）**；本輪＝複核。多 horizon 全量重跑＝另授／可 defer。

---

## 2. 符號尺（active 三顆）

| 現役（禁假設舊名） | h=20 FSC | h=60 FSC（最近） |
|---|---|---|
| `cycle_position_252d` | **缺** | PASS（2026-08-03 23:14） |
| `inst_cumflow_position_120d` | PASS（2026-08-01） | PASS（2026-08-04 00:55） |
| `lending_fee_rate_mean_30d` | **缺** | PASS（2026-08-04 01:57） |

| 本輪 | 結果 |
|---|---|
| `heavy_slot` | 空（無現持有者） |
| `--selftest` | 前輪 S1P1 已綠；未重跑長 IC |
| `--record` 全三顆×h=20,60 | **defer**——每 (feature×h) 重算 as-of IC，屬重活；h=60 已近新；補 h=20 缺口另開有界窗較妥 |
| 舊名 `mean_20d` | 庫內仍有歷史 PASS 列；**非**現役——本輪不對它 `--record` 充當 all_active |

建議續句（若要補 h=20）：

```text
SIGN-ACTIVE3-h20-record-go
```

```bash
python scripts/verify_sign_consistency.py --run --record \
  --features cycle_position_252d,inst_cumflow_position_120d,lending_fee_rate_mean_30d \
  --h 20,60
```

（與 I3／閘評估錯開；可加 `PYTHONUNBUFFERED=1`。）

> **can-do2（2026-08-04 ≈11:00）**：用戶明示另句才跑 → **未**執行 `--record`。待命帳＝`audits/OPT-R3-SIGN-H20-STANDBY-20260804.md`。

---

*完。*
