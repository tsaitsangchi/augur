# OPT r3「可先做」五項批次落地帳（2026-08-04）

> **位階**：[I]。**Steward 批次 GO**（貼「可先做」清單＝五項授權）。  
> **硬守**：不殺不疊 A1；不 Registry COMMIT；不 Dividend／寬窗；不 `SIM --apply`；無 git commit。

---

## 總表

| # | 項 | 狀態 | 產物 |
|---|---|---|---|
| 1 | A1 收尾記帳 | **partial**（仍跑） | `audits/OPT-R3-W2PREP-A1-WATCH-20260804.md`（刷新） |
| 2 | P1 特徵漂移呈案 | **done** | `reports/augur_p1_feature_drift_plan_20260804.md` |
| 3 | G3 假綠探針殘 | **done** | `audits/OPT-R3-W1B-G3-PROBE-EXECUTED-20260804.md` |
| 4 | HANDOFF 08-04 刷新 | **done** | `HANDOFF.md`（mapped 20／sc 10 等） |
| 5 | 符號尺／MC cone 輕量 | **partial**（MC 已齊；sign h=20 defer） | `audits/OPT-R3-SIGN-MC-LIGHT-20260804.md` |

---

## 1. A1

| 事實 | 值 |
|---|---|
| pid | **877801**（仍跑；elapsed≈33m @10:50） |
| cmd | `daily_maintenance.py --end 2026-08-04 --audit-days 14 --audit-all --heal` |
| log | `/home/hugo/logs/daily_maintenance_2026-08-04_a1a2.log`（已有內容；前段曾 0-byte） |
| 403 | **未見**；見額度閘 `5972/6000 ≥ 5800` 主動暫停 |
| exit | **尚未** |
| 處置 | **未殺**、**未**開第二支 |

A2 仍 ✅（既有批次帳）。

---

## 2. P1-DRIFT-PLAN

- 唯讀複現 dry-run：**拒載**（frozen `mean_20d` 雙顆 vs current 三顆含 `mean_30d`＋`cycle_position_252d`）。  
- 呈案含 A rename-align／B canonical／C retrain-asof＋建議裁句。  
- **零**特徵改名／重訓碼改動。

---

## 3. G3

- 跑 M-G11 pytest、M-G12／G13／G16 `--selftest`、G13／G16 live `--check`（皆 **紅 rc=1**＝探針有效）、`check_false_assertions --gate` ✓。  
- 不代裁 Q22／ALWAYS。

---

## 4. HANDOFF

- 08-04 段改寫：mapped **20**／sc **10**；UNBIND／U0／OUT8·N7·043；A1 態；next-best／本批次指針。  
- 刪「mapped 15／Wave-1 進行中」過時敘事。

---

## 5. 符號尺／MC

- MC as-of 08-03 h=30／52×雙法＝**已在庫**（複核；見既有 `MC-ASOF-20260803-RERUN`）。  
- active 三顆 h=60 FSC 近新 PASS；**h=20 缺口**（`cycle_position_252d`／`mean_30d`）→ 全量 `--record` **defer**（重 IC；建議 `SIGN-ACTIVE3-h20-record-go`）。

---

## Steward 後續可一句

```text
U0-STRUCT: 37=俟|… ; 80=… ; 97=…
P1-DRIFT: A|B|C|defer
SIGN-ACTIVE3-h20-record-go
G13-Q22: … | G16-ALWAYS: …
```

*批次結束 ≈10:52+08。*
