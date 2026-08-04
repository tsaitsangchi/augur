# OPT-W0-RUN22 最終觀察帳（2026-08-04）

> 位階：[I] · M-T6／runbook T-22:5x＋隔晨 · **零人工搶 slot、零 --allow-apply**  
> 寫入：2026-08-04T09:47:48+08:00（`observe_twevo_run22.py --morning --write-audit`）  
> 授權鏈：`OPT-STEP-R2-20260804-GO`（結輪後收口）＋甲案 `OPT-P0-20260804-go`（見 `audits/OPT-P0-TRIAGE65-20260804.md`）  
> 取代作廢早帳：`audits/OPT-W0-RUN22-20260803.md`（跑太早；不得引為 I5B 失效）

## ④ 根因（本輪真修）

- **假紅**：舊探針 `SELECT gain_evidence->>'basis'`；結輪後 JSON 無 `basis` 鍵 → `None`。  
- **真值**：正規欄 `gain_basis='none'`（`tw-20260803-r01`／run22 succeeded；可比、無增益）。  
- **修法**：observe 改 `COALESCE(gain_basis, gain_evidence->>'basis')`——**未**手補 ledger。

## 前置快照

- CSV：`audits/prerun22_pending_snapshot_20260803.csv`

## 隔晨機械五項

| # | 條件 | 結果 |
|---|---|---|
| ① latest evolution_run status=succeeded 且 run_id=22 | ✓ |
| ② superseded 列 > 0（I5B 首次） | ✓ |
| ③ pending_auto 全屬 run 22（或 0 列） | ✓ |
| ④ 最新 ledger gain basis ≠ incomparable | ✓ |
| ⑤ evolution_apply_log 無偷跑新增（相對窗） | ✓ |

## 現查數字

```json
{
  "n_pending_auto": 19,
  "pending_run_min": 22,
  "pending_run_max": 22,
  "pending_by_run": {
    "22": 19
  },
  "n_superseded": 17,
  "latest_run_id": 22,
  "latest_run_status": "succeeded",
  "gain_basis": "none",
  "apply_log_new_since_prerun": 0,
  "apply_log_today_n": 0
}
```

**總評**：全綠
