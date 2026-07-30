# NHC-DISTILL-S3-TEACHER CLOSED（2026-07-29）

> **性質**：[I] 執行收官；不創設 [N]。  
> **授權**：Steward NET8「**`NHC-distill-S3-teacher`**＋**`FZ-keep`**」（`audits/NET8-WAVE-APPROVED-20260729.md`）  
> **前置**：`audits/NHC-DISTILL-BATCH-CLOSED-20260729.md`（nhc_wave2_20260729 = 31 題已生成）  
> **不含**：改 [N]／FinMind／FRED／S5 validate `--run`

## 一、做了什麼

| 項 | 狀態 | 摘要 |
|---|---|---|
| S3 build_context | ✅ | `advisor_distill_build_context.py --run`；31 題 context 全建（真實 retrieve_all 檢索、零編造） |
| S4 teacher 啟動 | ✅ 背景中 | `advisor_distill_teacher.py --run --confirm`；nohup PID **2604401**（子 PID 2604402）；model=**qwen3:4b**（think=True） |
| teacher timeout 修正 | ✅ | `_call_teacher` timeout 改為 env `DISTILL_TEACHER_TIMEOUT`（預設 1800s）；CPU-only 8b 600s 不夠 |
| FZ-keep | ✅ | 零 FinMind／FRED |

## 二、S3 context 計數（真兆 stdout）

### 本批 nhc_wave2_20260729（31 題）

全部 context_built=true。

### 全庫（build_context 後 stdout）

| 情境 | relevant | n |
|---|---|---|
| 1（in-corpus） | False | 33 |
| 1（in-corpus） | True | 105 |
| 2（out-of-corpus） | False | 142 |
| 2（out-of-corpus） | True | 38 |
| 3（impossible） | False | 13 |
| 3（impossible） | True | 3 |
| **合計** | | **334** |

## 三、S4 teacher 進度（截至 ≈17:05 +08）

| 指標 | 值 |
|---|---|
| 全庫待生 gold | **60**（29 舊 delib_bridge_v2 + 31 nhc_wave2） |
| 已完成 | **2**（teacher 持續背景運行中） |
| model | qwen3:4b（think=True、零 Claude token #28） |
| 預估速度 | ~5 min/題（CPU-only） |
| 預估完成 | ~5 hr（背景自動走完；中斷可續——冪等游標） |
| log | `logs/nhc_wave2_teacher_20260729.log` |
| nohup PID | **2604401** |

**備註**：qwen3:8b CPU-only 於 600s 內無法完成單題（兩次 timeout）；降為 4b 後正常出金。

## 四、code 變更

- `scripts/advisor_distill_teacher.py` — timeout 改 env-driven（`DISTILL_TEACHER_TIMEOUT`，預設 1800s）；增逐題 flush 進度 log

## 五、硬邊界

| 項 | 結果 |
|---|---|
| 零 FinMind／FRED | ✅ |
| 不改 [N] | ✅ |
| 零 Claude token（本地 ollama） | ✅ |
| teacher gold ⊂ context 驗證 | 待 S5 `--run`（非本輪範圍） |

## 六、下一步（待人拍）

1. 等 teacher 背景跑完（`tail -f logs/nhc_wave2_teacher_20260729.log`）  
2. S5 `advisor_distill_validate.py --run`（驗 gold ⊂ context）  
3. 可選：`archive-push`（Steward 已授權同批）
