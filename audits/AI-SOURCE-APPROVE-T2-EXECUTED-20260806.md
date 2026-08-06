---
status: executed
series: governance
date: 2026-08-06
choice: T2
go: audits/AI-SOURCE-APPROVE-T2-GO-20260806.md
plan: reports/augur_ai_source_approve_thaw_plan_20260806.md
paste: "AI-SOURCE-APPROVE-T2-EXECUTED | activate-default-on | max-sources-1 | selftest-pass | FZ/GATE-keep"
self_reported: true
---

# EXECUTED｜AI-SOURCE-APPROVE T2 · AUTO-LIFT 機械 activate · 2026-08-06

Steward 確認：**憲章 v1.48 機械 `system=True` 可 approve／activate** → **T2-go**。本輪落地。

## 碼

| 檔 | 變更 |
|---|---|
| `src/augur/knowledge/answer_auto_lift.py` | `ACTIVATE_SOURCE_DEFAULT=True`；`MAX_SOURCES_PER_LIFT=1`；`lift_items` 每批最多 1 `source_key` 且須 `has_text` 才 `activate_source=True`；`lift_log.note` 交鏈 activate |
| `scripts/kh0_answer_auto_lift.py` | 預設機械 activate；`--no-activate-source` 關 |

實際 activate 仍走 `auto_admit.maybe_activate_source`（actor=`system:kh10_auto_admit`）；題目-only 不經此放行源。

## 驗

```text
./venv/bin/python -m augur.knowledge.answer_auto_lift --selftest   # 全通過
./venv/bin/python scripts/kh0_answer_auto_lift.py --selftest       # 全通過
```

### LIVE smoke（`--apply` · item=4 · europepmc）

```text
lifted=True cite_pass=True activate=True lift_id=2
  depth 7→7 ok · act=True · src=europepmc · src_actions=[]
```

| 項 | 誠實讀法 |
|---|---|
| `act=True` | T2 允動：`has_text` ∧ 批次 ≤1 → 進 `maybe_activate_source` |
| `src_actions=[]` | 現庫 **全部 has_text 源已是 `active`**（非-active `approved`／`proposed` 源無正文件）→ 無可升級遷移；**不是**路徑沒走 |
| depth 7→7 | cap=`up_to=2`；水印已深於 2 → admit 不動（預期） |

無「真 approve→activate 狀態翻轉」樣本可供本輪無害煙測；若需真翻轉須另裁對 **approved 無正文源** 補正文，或另授降級再用。

## 仍禁

- web／對話裸 SQL approve
- 無 `has_text` 靠本路徑 activate 整源
- 單批 >1 `source_key`
- 改 `HUMAN_ONLY`／gov 寫路徑

T0 敘事仍有效（web／對話不可）；AUTO-LIFT 預設由 False → **True（T2）**。

*executed。advise 掛線另 GO，非本輪。*
