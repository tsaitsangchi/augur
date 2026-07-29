# KH7-REJUDGE CLOSED（2026-07-29）

> **性質**：[I] 執行收官；不創設 [N]。  
> **拍板**：`audits/SIX-TRACK-WAVE-APPROVED-20260729.md`（`KH7-rejudge`＋`FZ-keep`）  
> **前案**：`audits/KH7-S1-CLOSED-20260729.md`；計畫 §3.1＝`reports/augur_kh7_adversarial_eligibility_plan_20260729.md`  
> **明文**：`eligibility_pass` ≠ approve ≠ activate ≠ 可交易；**HUMAN-APPROVE-keep**。

## 一、診斷（誠實）

| 觀測 | 判讀 |
|---|---|
| run_id≤5 四探針皆 `ungrounded_axis_labels` | 複合軸標（如「太陽能材料研發技術核心」）須**整串**出現於 merged top → 誤嚴 |
| 語料已有 eligible `rdai_*太陽能*`／光伏論文 | 檢索 exact 路找得到，但 RRF 被哲學近鄰淹沒；merged top 缺錨點字 |
| `KNI-EVAL-EMPTY-CORPUS` | 無意義軸＋近鄰命中 → **應繼續 fail**（防假綠） |
| `evaluate_layer(7)` 舊邏輯 | `ORDER BY decided_at LIMIT 1`；同批 timestamp 相同＋回放舊 fail 會蓋掉 pass |

**採納修法**：錨點校準＋證據路徑 enrichment＋exact RRF 加權＋layer7 改讀「最新 run_id 是否有 pass」。  
**不採**：放寬規則讓 ZZZZ／無錨點近鄰假綠；不自動 approve／activate；不標 KH8/9 LAND。

## 二、實作變更

| 檔 | 變更 |
|---|---|
| `interaction_probe.py` | `label_anchor_tokens`（CJK 3–4 字 n-gram／短 run／拉丁≥3）；`grounding_hits`＝merged∪各軸 ranked；`RRF_EXACT_BONUS`；snippet 160 |
| `kh7_eligibility.py` | `detect_ungrounded` 共用 `axis_labels_ungrounded`；認 `grounding_hits` |
| `run_kh7_eligibility.py` | `_row_to_summary` 傳 `grounding_hits` |
| `auto_admit.py` | depth7：`max(run_id)` 上是否存在 `eligibility_pass` |
| `run_knowhow_auto_admit.py`／drain 腳本 | 實務天花板 6→**7**（KH8/9 仍未 LAND） |

## 三、真兆 metrics

### 3.1 Probe re-run → `run_id=6`

| probe_id | gap | spur | multi |
|---|---|---|---:|
| KNI-EVAL-EMPTY-CORPUS | `ungrounded_hits` | high | 3 |
| RKI-AI-SOLAR-RD | `[]` | low | 3 |
| RKI-FP-AI-SOLAR | `[]` | low | 4 |
| RKI-FP-SOLAR-CORE | `[]` | low | 3 |

### 3.2 KH7 eligibility 前後

| 批次 | pass | fail | human | 說明 |
|---|---:|---:|---:|---|
| **前** run_id=5（修訂後規則） | 0 | 4 | 0 | 皆 `ungrounded_axis_labels` |
| **後** run_id=6（rejudge） | **3** | **1** | 0 | decline 仍 fail；三 RKI **pass** |
| 舊 tops 回放 run_id=5 | 0 | 4 | 0 | 無 `grounding_hits`／無太陽能標題 → 仍 fail（誠實） |

### 3.3 Admit layer 7

| 檢查 | 結果 |
|---|---|
| `evaluate_layer(7)` | **pass**（`run_id=6` 有 eligibility_pass；≠approve） |
| dry `--apply-up-to 7 --min-depth 6 --limit 1` | `depth 6→7` advanced |
| KH8／KH9 | 仍 UNBUILT `skipped`；不擋 7、不抬 8+ |
| approve／activate／`approval_status` | **未改** |

## 四、驗證

| 檢查 | 結果 |
|---|---|
| `python -m augur.knowledge.interaction_probe --selftest` | ✅ |
| `python -m augur.knowledge.kh7_eligibility --selftest` | ✅ |
| `python scripts/run_kh7_eligibility.py --selftest` | ✅ |
| `python -m augur.knowledge.auto_admit --selftest` | ✅ |
| FZ-keep | ✅ 零 FinMind／FRED |

## 五、硬邊界

| 項 | 結果 |
|---|---|
| HUMAN-APPROVE-keep | ✅ |
| FZ-keep | ✅ |
| eligibility_pass ≠ 可交易 | ✅ |
| KH8／KH9 LAND | ❌ 未標 |
| 自動 approve／activate | ❌ 未做 |
