# NHC-DISTILL-BATCH CLOSED（2026-07-29）

> **性質**：[I] 執行收官；不創設 [N]。  
> **授權**：Steward WAVE2＝**`NHC-distill-batch`**＋**`FZ-keep`**（**無** `NHC-CONSTITUTE`）。  
> **拍板**：`audits/WAVE2-SIX-TRACK-APPROVED-20260729.md`  
> **前置**：`audits/NHC-S3-CLOSED-20260729.md`（`advisor_distill_seed_topic` 住 DB）  
> **不含**：改憲章 [N]／S3 build_context／S4 teacher／全量 S5 `--run`／FinMind／FRED／領域答案樹

## 一、做了什麼

| 項 | 狀態 | 摘要 |
|---|---|---|
| 新 `batch_tag` | ✅ | `nhc_wave2_20260729` |
| 消費 DB 種子 | ✅ | runtime `_load_seed_topics`；ooc active=**30**／impossible=**16** |
| 最小有意義 S2 生成 | ✅ | `--n-incorpus 1 --tpl-per-topic 1 --ooc-tpl 6` |
| 冪等 | ✅ | 同 tag 重跑 →「已有 31 題,冪等跳過」 |
| DP7 GATE | ✅ | 全庫情境 2+3＝**58.7%** ≥ 55% |
| 便宜 S5 | ✅ | `advisor_distill_validate.py --self-test` 綠（未跑 `--run`：本批尚無 context／gold） |
| FZ-keep | ✅ | 零 FinMind／FRED |
| 入憲 | ❌ | **無** `NHC-CONSTITUTE` → 未改 META／大憲章 |

**註（邏輯側模板）**：既有 5 個 OOC 問法 × 30 種子主題已在 `pilot2` 飽和（UNIQUE `question`）。為讓新 batch 能落地 DECLINE 變體（主題仍讀表、非領域 hardcode），於 `_OOC_TEMPLATES` 增第 6 問法「從工程視角如何評估{t}?」。

## 二、計數（真兆：stdout／DB）

### S2 生成（stdout）

| 指標 | 值 |
|---|---|
| 嘗試 | 221 |
| 新增 | **31**（其餘冪等去重） |
| 重跑 | 跳過（已有 31） |

### `batch_tag=nhc_wave2_20260729`（DB）

| situation | expected | topic_source | n |
|---|---|---|---|
| 1 | ANSWER | embedded_work | 1 |
| 2 | DECLINE | curated_ooc | **30** |
| **batch 合計** | | | **31** |

- `curated_ooc` ∩ active `advisor_distill_seed_topic`（join `topic_ref`）＝**30**／30  
- 本批 S3 context＝**0**（未跑 `advisor_distill_build_context`；本輪範圍僅 generate）

### 全庫（生成後）

| 指標 | 值 |
|---|---|
| total | **334** |
| 情境2 DECLINE | 180（53.9%） |
| 情境3 REFUSE | 16（4.8%） |
| 情境2+3 佔比 | **58.7%**（GATE ✓） |

### 其他 `batch_tag`

| tag | n |
|---|---|
| `pilot2` | 274 |
| `nhc_wave2_20260729` | 31 |
| `delib_bridge_v2` | 29 |

### S5 現況（全庫；非本批）

context 303、已生 gold 274、已驗 171（`validate` 無參數 stdout）。

## 三、驗證

| 檢查 | 結果 |
|---|---|
| `advisor_distill_generate_questions.py --selftest` | ✅ 無 `_OOC_TOPICS`／`_IMPOSSIBLE_TOPICS` |
| 生成 exit／GATE | ✅ 0／58.7% |
| 同 tag 重跑冪等 | ✅ |
| `advisor_distill_validate.py --self-test` | ✅ |
| 零專題答案樹 | ✅ |
| 零 FinMind／FRED | ✅ |

## 四、變更檔

- `scripts/advisor_distill_generate_questions.py` — `_OOC_TEMPLATES` ＋1 問法變體（邏輯側）
- 本 CLOSED；`audits/WAVE2-SIX-TRACK-APPROVED-20260729.md` §三 留痕

## 五、硬邊界

| 項 | 結果 |
|---|---|
| 零 FinMind／FRED | ✅ |
| 不改 [N] | ✅ |
| 無領域專答／答案常數 | ✅ |
| 主題策展 SSOT＝PG | ✅ |

## 六、下一步（待人拍）

1. 可選：本批 S3 `build_context` → S4 teacher → S5 `--run`（另令；非本 CLOSED 範圍）  
2. **`NHC-CONSTITUTE`** — 仍須另拍；本輪未開  
3. 擴 OOC 主題＝`INSERT advisor_distill_seed_topic`，零改碼  
