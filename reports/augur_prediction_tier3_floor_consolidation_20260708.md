# 股市預測 — Tier3 地板再夯實(多 seed / 成本 realism / H120 收尾)

**日期**:2026-07-08 ｜ **性質**:誠實地板夯實(deflation §4 續、SOP 債 d 收斂)｜ **層級**:執行層(本地零 API、冪等、不改判準)
**口徑**:Ridge H60 LO top10%、asof panels 2016-2025、A'-3 embargo(h+62td);數字全由作者親跑腳本(ground truth,非 agent)
**守**:#8 · #11(多 seed 條件式)· #12(DSR/portfolio/pit SSOT 複用)· #14 · #15(敏感度帶不造假兆、per-period 正確口徑)· #28

---

## 0. 三十秒結論

Tier3 三子項**皆不把已 FAIL 的 deflation 地板翻成 PASS**——它們把「未確立(deploying_unestablished)」講到滴水不漏,不解鎖部署。真正的解鎖=資料累積(Tier4,卡~季/~5 年)。

| 子項 | grounding 真相 | 對地板效應 |
|---|---|---|
| **多 seed** | 幾乎已建:Ridge 確定性單跑、GBDT (42,43,44) 取中位;seed∉N 鍵 | **不移地板**;只防 GBDT lucky-seed |
| **成本 realism** | cost 已 turnover-aware(非 flat);缺流動性感知價差/衝擊 | **單調壓低**(敏感度帶) |
| **H120** | ~90% 已建;全期近門檻、近期 n=8 卡資料 | 候選非部署;取保守 N 仍未確立 |

**bonus catch(H120 揭出)**:修 `deflate_headline_verdict.py` 取保守 N bug——原用樂觀(較小)N 判 pass 違方法論「取較保守 N」;H120 since2014 跨 95%(N=8 過/N=16 未過)暴露之靜默樂觀(敵③)已修。

---

## 1. 多 seed — near-vacuous(已建、DDL 實證)

- **機制(revalidate.py:47,200-224)**:`_backtest_cell` — Ridge `seeds=(42,)` 確定性單跑;GBDT `GBDT_SEEDS=(42,43,44)` 三 seed 取**中位**(`_med`)。
- **seed∉ deflation N 鍵**:`trial_ledger` DISTINCT 鍵 = `(model,top_frac,weight,feats_hash,cost,horizon)`(migrate_trial_ledger_ddl.py:55-56);`seed` 僅揭露欄。DB 實證:16 列 seed 全 NULL、N_strict=8 / N_upper(含 sample_since)=16。
- **結論**:多 seed **不動 N、不移 DSR 地板**(grounding 中方法論鏡「多seed 抬高 N」之說被 DDL 證偽)。其唯一價值=(a) GBDT 取中位防 lucky-seed cherry-pick、(b) #11 揭露。Ridge 為 headline、確定性,單 seed 正確、無分散度可報。

## 2. 成本敏感度帶 — cost realism 的 #15-clean 落地

**為何是帶不是單一數字**:headline 成本用平坦 0.585%(手續費 2×0.1425%+證交稅 0.3%),**未計** bid-ask 價差/市場衝擊/借券稀缺。台股低流動性小型股真實成本達 1-2%+。**我們無真實 tick/價差資料**(intraday 唯一真排除 BACKFILL_DEFERRED)→ 硬報單一「真實成本」=造假兆(敵①)。故報敏感度帶。

**機制**:cost 只作用 `net=gross−turn×cost`(LO sb=0),不影響選股/訓練/turnover → 每宇宙一次回測取 (gross,turn),對成本解析套用(工具 `scripts/deflate_cost_sensitivity.py`,#12 複用 deflation/portfolio/pit SSOT)。avg turnover asof=0.648 / pit=0.642。

### asof_incumbent(全史齊、穩定核心=上界對照;span 2016-2025)

| cost | net Sharpe | perpd SR | DSR(N=8) | DSR(N=16) | deflated eff |
|---|---|---|---|---|---|
| **0.585%**(現) | 1.1972 | 0.7185 | 89.5% | 75.6% | +0.265 |
| 1.000% | 1.1437 | 0.6864 | 86.9% | 71.1% | +0.211 |
| 1.500% | 1.0791 | 0.6477 | 83.2% | 65.2% | +0.147 |
| 2.000% | 1.0145 | 0.6089 | 78.7% | 58.7% | +0.082 |
| 3.000% | 0.8851 | 0.5312 | 67.6% | 44.9% | **−0.047** |

### pit_broad(廣宇宙、當下可算=主誠實地板;span 2016-2025)

| cost | net Sharpe | perpd SR | DSR(N=8) | DSR(N=16) | deflated eff |
|---|---|---|---|---|---|
| **0.585%**(現) | 1.0022 | 0.6015 | 78.6% | 57.7% | +0.070 |
| 1.000% | 0.9480 | 0.5690 | 74.0% | 51.7% | +0.015 |
| 1.500% | 0.8825 | 0.5297 | 67.9% | 44.4% | **−0.050** |
| 2.000% | 0.8168 | 0.4903 | 61.1% | 37.2% | −0.116 |
| 3.000% | 0.6851 | 0.4112 | 46.3% | 23.9% | −0.247 |

兩宇宙 ref 0.585% 列皆 **byte 級重現凍結 baseline**(asof DSR 75.6%/eff +0.265;pit DSR 57.7%/eff +0.070)=反推 turn 數學自洽驗證。

**裁決**:成本升向真實 1-2%+,兩宇宙 DSR 單調下滑。**主誠實地板 pit_broad 的 deflated 有效 Sharpe 在 ~1.1% 成本即穿零、1.5% 為 −0.050**——台股低流動性小型股真實成本下,主地板 deflated edge 基本歸零至負。全史齊上界較韌但 3% 成本亦翻負(−0.047)。地板不因細化成本而過門檻——樂觀上界被進一步夯實(#15)。**誠實邊界**:試驗搜尋 N/變異固定於 ledger 0.585% 基準(重跑試驗會使 SR_0 略降=部分抵消),故此帶 DSR 降幅為偏嚴上界。

## 3. H120 收尾 — 候選非部署、取保守 N 仍未確立

- **現況(grounding)**:H120 已訓練(model_registry RankRidge_H120 seed42、28 feats)、預測(prediction_values 344 列、**in_portfolio=0=追蹤候選非部署**)、Stage B(asof IC 0.1551 HAC-t 6.929)、Stage D 經濟(ridge LO 2014 淨 Sharpe **1.251=風險調整最佳**、Calmar 2.21;2021 near-term 0.792≈bench 0.807 n=8)、入 trial_ledger(8 列、已在 headline N=16 混頻池)。
- **H120 pooled deflation**(取較保守 N=16 為準):
  - **since2014(全期 n=14)**:DSR 保守 **93.6%** / 樂觀(N=8)95.8%;deflated eff **+0.53~0.61**。**跨 95%**——樂觀 N 過、保守 N 未過 → **取保守判未確立**(全 cell 中最接近門檻、最強候選)。
  - **since2021(近期 n=8)**:DSR 保守 55.3% / 樂觀 58.7%;deflated eff +0.09~0.15。皆 <95% 未確立、§228/C7 sample gate=exploratory 非硬 pass/fail。
- **⚠ 取保守 N bug 修正(execution-layer、H120 揭出)**:`deflate_headline_verdict.py:133` 原 `passed = dsr_hi>=0.95` 用**樂觀 N**(較小 N→較高 DSR),違方法論「deflation 一律取較保守(較大)N」。H60 兩 N 皆 FAIL 未暴露;H120 since2014 一跨 95%(N=8 過/N=16 未過)即現形=靜默樂觀(敵③)。已修為 `passed = dsr_lo>=0.95`(取保守),H120 since2014 正確判未確立。
- **裁決**:H120 為最佳風險調整 horizon 候選(全期近門檻),但近期 n=8 卡資料、方向性非精確保證;deflation 取保守 N 仍未確立。**不強制凍結部署 baseline**(H120 未部署、in_portfolio=0;baseline=部署參考點,提前凍結語意錯)。定論待 Tier4 資料累積(~2.3 非重疊期/年、n≥20 需~5 年)。

## 4. 誠實總裁決

三子項落地後,deployed cell(Ridge H60 LO)之地板:
- **仍 deploying_unestablished**(DSR 皆 <95%);多 seed 不移、cost realism 壓更低、H120 同未確立。
- **價值=誠實最大化**:把「地板為何未確立」講到滴水不漏(N 機械取保守、成本帶、seed 揭露),而非解鎖。
- **真天花板=資料累積 + 硬體**(Tier4 軌B 實戰驗證 / H120 n≥20),非碼、非再細化成本。

## 4.5 advisor caveat 實驗 → 撤回(#7/#15 教訓:單測過 ≠ live 過)

擬把成本敏感度誠實補進 advisor caveat(`payload.py`:「此薄地板對成本假設高度敏感、真實成本下 deflated 趨零/負」)。**單測過**(caveat 正確入 `validation.note`、`prompt.py:73` 確認送進 LLM prompt)。**但 #7 live 實測揭真相**:
- **暖機 Ollama、同 query、同狀態下**:新碼(含此 caveat)2/2 = **確定性 number-dump**(把 payload scores/metrics 全當股票排名亂列、零誠實資訊);舊碼(無此 caveat)2/2 = 正常 surface picks + 既有 caveats(deflation/薄 edge/deploying_unestablished)+ guard pass。
- **歸因**:此 caveat 加長 prompt,把已飽和的 qwen3:8b(8B)推過可靠處理臨界 → 打壞整則回應。caveat 個別更誠實,但**打壞回應=零誠實資訊輸出=淨誠實更差**(#15)→ **撤回**。成本誠實改住本報告 + 可複現腳本(#10 可溯源、不需塞進打壞弱模型的 caveat)。
- **教訓**:#7「常駐服務改碼須重啟 live 實測」正是為此——單測(caveat 入 note)過、live 行為(整則打壞)壞;不 live 測就會假通過。

**附帶揭出 advisor picks 可靠度問題(超出 Tier3、v1.37.0 本機模型天花板)**:qwen3:8b 對選股題不穩定——**幻覺股名**(payload 只有 symbol 無 name → 模型從記憶亂填,如 2330 標成台泥/聯發科,guard 查數字不查股名 → 錯名過閘)、prompt-length 敏感、偶誤 decline。屬 v1.37.0「advisor 只能本機 LLM、可靠度靠更大本機模型/GPU」之天花板,非 Tier3 範圍。

## 5. 落地清單(本輪)

| 項 | 檔 | 狀態 |
|---|---|---|
| 成本敏感度帶工具(新) | `scripts/deflate_cost_sensitivity.py` | ✅ |
| `run_pit_economic` cost 參數化 + 回 gross/turn(survivorship byte-identical 驗證) | `scripts/survivorship_economic_verdict.py` | ✅ |
| 取保守 N bug 修(#15 敵③、H120 揭出) | `scripts/deflate_headline_verdict.py` | ✅ |
| ~~advisor caveat 補成本敏感度~~ | ~~`src/augur/advisor/payload.py`~~ | ❌ 撤回(§4.5、打壞弱模型) |

## 6. 複現 + 誠實邊界
```bash
python scripts/deflate_cost_sensitivity.py                              # 兩宇宙成本帶
python scripts/deflate_headline_verdict.py --horizon 120 --since 2014   # H120 全期 pooled deflation
python scripts/deflate_headline_verdict.py --horizon 120 --since 2021   # H120 近期(n=8 exploratory)
python scripts/survivorship_economic_verdict.py                        # 兩宇宙 baseline byte-identical
```
- 多 seed 分散度未實測(median 機制本身防 cherry-pick、#28 省重跑);H120 未凍結 baseline(未部署)。
- 成本帶之試驗 N/變異固定於 ledger 0.585% 基準(偏嚴上界);真實成本無 tick 資料、以帶呈現不假裝單一值。
