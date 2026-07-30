# NHC-DISTILL-S5 CLOSED（2026-07-30）

> **性質**：[I] 執行收官；不創設 [N]。  
> **授權**：Steward「**NHC-distill-S5 — 硬校驗（接 60 gold）**」＋`FZ-keep`  
> **拍板**：`audits/NHC-DISTILL-S5-APPROVED-20260730.md`  
> **前置**：S4 teacher 完（log 60/60；庫內實際 `target_response` 非 NULL＝**334**）

## 一、做了什麼

| 項 | 結果 |
|---|---|
| `advisor_distill_validate.py --run` | ✅ |
| 輸出 | `data/distill/sft_nhc_20260730.jsonl`（**227** 行） |
| FZ-keep | ✅ 零 FinMind／FRED |
| guard 鬆動 | ❌ 未改 |

## 二、真兆（stdout）

| 範圍 | gold | 通過 | drop | GATE(>40%?) |
|---|---:|---:|---:|---|
| **pooled**（參考） | 334 | 227 | 32.0% | — |
| `delib_bridge_v2` | 29 | 29 | 0.0% | ✓ |
| **`nhc_wave2_20260729`** | **31** | **28** | **9.7%** | ✓ |
| `pilot2` | 274 | 170 | 38.0% | ✓ |

- 指令：`python scripts/advisor_distill_validate.py --run --out data/distill/sft_nhc_20260730.jsonl`
- log：`/tmp/nhc_distill_s5_20260730.log`
- **各 batch drop 皆 ≤40%** → 無「回 S4 調 teacher」旗標

## 三、硬邊界

| 項 | |
|---|---|
| ≠ 開 SFT 訓練 | ✅ 只寫 jsonl |
| ≠ 放寬 guard／grounding | ✅ |
| ≠ 改 [N] | ✅ |

## 四、下一步（待另令）

1. 可選：用 `sft_nhc_20260730.jsonl` 開本地 SFT（另碼）  
2. 抽查 `nhc_wave2` 未過 3 題之 `validate_verdict`（若要調 teacher）
