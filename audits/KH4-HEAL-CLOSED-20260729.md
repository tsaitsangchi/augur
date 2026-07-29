# KH4-heal 收官（2026-07-29）

> **性質**：[I] 實作留痕；數字皆出自 DB／stdout。  
> **拍板**：`KH4-heal`＋`FZ-keep`（`audits/SIX-TRACK-WAVE-APPROVED-20260729.md`）  
> **機器**：PC002 WSL · `/home/hugo/project/augur`

## 一、Before（drain 卡住快照）

| 來源 | 值 |
|---|---|
| `knowhow_admit_until_empty.log` round 10 | `state buckets= {3: 2994, 6: 143280}`；`advanced=0` stuck |
| DB 重查（本輪開工） | `{3: 2994, 6: 143280}` |

### depth=3 樣本診斷（2994）

| 缺口 | 計數 | 含義 |
|---|---:|---|
| 有 text | 2994 | 非缺文 |
| 有 sentence | 2986 | 8 缺句 |
| 有 embedding | 2487 | 507 缺嵌（含非語意型） |
| KH4 `answer_status=blocked`／`terminal_blocked` | 2511 | **誤擋主因**：有 `knowledge_fulltext_status`（skip_no_oa 等）**且已有全文**仍當 terminal block |
| KH4 `ineligible`／`non_semantic_entity_type` | 396 | material／compound／book 等——KH4 真不允許，**不假抬** |
| KH4 `provisional`／`awaiting_projection` | 87→heal 後 111 窗 | 缺可嵌 CLEAN 句／投影未就緒 |

結論：卡在 depth 3 **不是**「一律缺 embedding」——主因是 KH4 把「有 skip status 列」一概當 `terminal_blocked`，與 FT-COV「terminal_blocked＝有 status **且無 text**」不一致。

## 二、做了什麼（FZ-keep；零 FinMind／FRED）

1. **KH4 邏輯補正**（`src/augur/knowledge/kh4.py`）：`has_terminal_block`＝存在 `knowledge_fulltext_status` **且**不存在 `knowledge_item_text`。自測加「有 text 不因舊 skip 擋 eligible」。
2. **切句**：`build_sentences.py --scope items --limit 50` → 段 32／句 114（`/tmp/kh4_heal/02_build_sentences.log`）。
3. **嵌入**：
   - items/zh `--gap-fill --limit 500` → **新嵌 92**（`06_embed_gapfill_zh.log`）
   - items/en `--gap-fill` → CLEAN 可嵌幾乎耗盡；餘量多為 len>1000／junk 或無法通過 clean 閘 → **0 新嵌**（誠實；`04`／`07`）
4. **刷新**：對 2994 個 depth=3 `item_id` 批次 `kh4.refresh_items` → eligible **2487**，再 refresh provisional → eligible **2490**。
5. **admit（只掃已療癒候選）**：`run_batch(up_to=6, min_depth=3, limit=5000, apply=True, quiet=True)`  
   - **不**再開 `--until-empty` 全表 drain（避免與其他軌互搶）

## 三、After（真兆）

| | Before | After |
|---|---:|---:|
| depth 3 | 2994 | **504** |
| depth 6 | 143280 | **145770** |
| advanced（本批） | — | **2490**（3→6） |
| unchanged | — | **504** |

### 殘留 depth=3＝504（誠實不抬）

| answer_status | status_reason | n | 處置 |
|---|---|---:|---|
| ineligible | non_semantic_entity_type | 396 | material 201／compound 186／book 9；KH4 真不允許 |
| provisional | awaiting_projection | 108 | document 79＋paper 29；句多屬 en junk（>1000／ERP 雜訊）或 CLEAN 閘外——**未假 eligible** |

未假抬 admit_depth 越過 KH4 真允許範圍；未碰 KH7 pass／approve／activate 人閘；未開市場 API。

## 四、Log 路徑

| 步驟 | path |
|---|---|
| selftest | `/tmp/kh4_heal/01_selftest.log` |
| sentences | `/tmp/kh4_heal/02_build_sentences.log` |
| ATA dry-run | `/tmp/kh4_heal/03_ata_dryrun.log` |
| embed en/zh | `/tmp/kh4_heal/04_*.log`／`06_*`／`07_*` |
| KH4 refresh | `/tmp/kh4_heal/05_refresh_kh4_depth3.log`／`08_*` |
| admit apply | `/tmp/kh4_heal/10_admit_apply.log` |
| 殘留 breakdown | `/tmp/kh4_heal/12_final_breakdown.log` |
| 先前 stuck drain | `/tmp/knowhow_admit_until_empty.log` |

## 五、程式變更

- `src/augur/knowledge/kh4.py`：terminal_block 述詞＋自測（有 text 不誤擋／無 text+status 仍 blocked）
