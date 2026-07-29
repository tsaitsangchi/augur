# KH4-residual-504 收官（2026-07-29）

> **性質**：[I] 實作留痕；數字皆出自 DB／stdout。  
> **拍板**：`KH4-residual-504`＋`FZ-keep`（`audits/WAVE2-SIX-TRACK-APPROVED-20260729.md`）  
> **機器**：PC002 WSL · `/home/hugo/project/augur`  
> **銜接**：前置 `audits/KH4-HEAL-CLOSED-20260729.md`（2994→504）＋admit drain 終態 `{3:504, 7:145770}`

## 一、一句定錨

對 depth=3 殘留 **504** 做誠實處置：能嵌的嵌、能分類的分類；**永久不合格明文入帳**；**不**假抬 `admit_depth`／不假 `eligible`。

## 二、Before（本軌開工＝drain 後）

| 來源 | 值 |
|---|---|
| WAVE2／drain | `buckets={3:504, 7:145770}` |
| DB 重查 | `{3:504, 7:145770}` |

### depth=3＝504 分類（KH4）

| answer_status | status_reason | n | 含義 |
|---|---|---:|---|
| `ineligible` | `non_semantic_entity_type` | **396** | 非語意層 `entity_type`（corpus `SEMANTIC_ENTITY_TYPES`＝paper/report/document） |
| `provisional` | `awaiting_projection` | **108** | 語意型別＋license 過閘，但無通過 junk 閘之可嵌句 → 無 embedding |

#### 396 permanent ineligible（entity）

| entity_type | n | 判定 |
|---|---:|---|
| material | 201 | **永久**——不入語意層（KH4／embed CLEAN） |
| compound | 186 | 同上 |
| book | 9 | 同上（P4：book 首期不入語意層） |

#### 108 provisional 診斷（真兆）

| 指標 | 值 |
|---|---|
| 有 text／sentence／embedding | 108／108／**0** |
| en 句數 | 1458（皆未嵌） |
| 其中 `10≤len≤1000` 可過 `is_junk` | **3** 句／**3** item（皆 `domain=smoke_test`） |
| 其餘 | **1455** 句／**105** item 僅有 `len>1000`（embed junk 擋）或無 mid-len 句 |
| CLEAN 未嵌 en（含全庫） | 9111＝junk 9108＋mid 3；mid 前須掃過 9088 junk |

結論：殘留 **不是**「再跑一次 until-empty 就會動」——396 真不准入；105 缺可嵌句（確定性切句後仍整段過長／ERP 雜訊）；僅 3 句機械可嵌。

## 三、做了什麼（FZ-keep；零 FinMind／FRED）

1. **分類**（唯讀 DB）：上表；不改 `SEMANTIC_ENTITY_TYPES`、不造假抬 eligible。
2. **嵌入**（既有腳本）：  
   `embed_knowledge.py --layer sentence --language en --scope items --gap-fill --limit 10000`  
   → 處理 9111、**新嵌 3**、junk 排除 9108（`/tmp/kh4_residual504/05_embed_gapfill_en.log`）。
3. **KH4 刷新**：對 depth=3 的 504 item `kh4.refresh_items` → eligible **3**／provisional **105**／ineligible **396**。
4. **admit（只抬真 eligible）**：對 `item_id∈{277938,277945,277946}` 各跑  
   `run_knowhow_auto_admit.py --apply-up-to 7 --item-id …`  
   → 皆 **3→7**（各 advanced=1）。  
   **未**再開 `--until-empty` 對 501 假衝；**未**抬 `max_auto_depth`。

未做（誠實邊界）：

- **不**刪既有過長句重切（`build_sentences` resume＝`NOT EXISTS`；重切需另案破壞性／新 splitter）。
- **不**把 material／compound／book 改標 paper／document 以假過 CLEAN。
- **不** claim 105 provisional「可檢索可答」。

## 四、After（真兆）

| | Before | After |
|---|---:|---:|
| depth 3 | 504 | **501** |
| depth 7 | 145770 | **145773** |
| advanced（本軌） | — | **3**（真 eligible→7） |
| ineligible @depth3 | 396 | **396**（不變；永久） |
| provisional @depth3 | 108 | **105** |
| eligible 新嵌後抬升 | 0 | **3**（smoke_test document；已離 depth3） |

### 殘留 depth=3＝501（誠實終態）

| 桶 | n | 處置登錄 |
|---|---:|---|
| **permanent ineligible** | **396** | material 201／compound 186／book 9；`status_reason=non_semantic_entity_type`；除非 Steward 另改 corpus 准入集，否則 **不入 KH4 一般回答池、不抬 admit** |
| **permanent provisional（現行閘）** | **105** | paper 29＋document 76；皆有句但 **無** mid-len 可嵌句（`is_junk`：en `len>1000`）；`status_reason=awaiting_projection`；待另案切句／雜訊治理——**本軌不假 eligible** |

provisional 域分布（105）：`local` document 68；decision_sciences paper 10；economics… paper 9；business… paper 9；erp_semantics document 5；smoke_test document 3；production_mgmt paper 1。

驗：provisional emb gap＝`(105, has_emb=0, mid_unemb_left=0)`——可嵌缺口已耗盡。

## 五、Log 路徑

| 步驟 | path |
|---|---|
| before breakdown | `/tmp/kh4_residual504/01_before_breakdown.log` |
| provisional detail | `/tmp/kh4_residual504/02_provisional_detail.log` |
| classify | `/tmp/kh4_residual504/03_classify.log` |
| global embed gap | `/tmp/kh4_residual504/04_global_embed_gap.log` |
| embed gap-fill | `/tmp/kh4_residual504/05_embed_gapfill_en.log` |
| KH4 refresh | `/tmp/kh4_residual504/06_refresh_kh4.log` |
| admit healed×3 | `/tmp/kh4_residual504/07_admit_healed.log` |
| final breakdown | `/tmp/kh4_residual504/08_final_breakdown.log` |

## 六、程式變更

本軌 **零 code 變更**——只跑既有 `embed_knowledge`／`kh4.refresh_items`／`run_knowhow_auto_admit`。
