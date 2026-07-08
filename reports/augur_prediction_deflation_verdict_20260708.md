# 股市預測 — Deflated Sharpe 地板裁決(釘實地板)

**日期**:2026-07-08 ｜ **性質**:誠實終判前置閘裁決(SOP §5 債 d / §6 G7 / STAGE C-V5 收尾)｜ **對抗驗證**:3 鏡全 CONFIRM(workflow `wkubx47g6`)
**口徑**:headline = Ridge H60 long-only since2014、cost 0.585%、asof、A'-3 embargo(h+62td 逐折);數字全由作者親跑 `scripts/deflate_headline_verdict.py`(ground truth,非 agent 轉述)
**守**:#12(DSR 住 metrics.py) · #14(經濟終判前置) · #15(per-period 正確口徑、真兆判讀、bug 值作廢揭露)

---

## 0. 三十秒結論

**headline 淨 Sharpe ~1.20 未過 deflation**。扣掉「搜過 8~16 個 config 才挑到最好」的選型偏誤後:
**DSR = 75.6%(N=16 保守)~ 89.5%(N=8),兩端皆 < 95% 統計確立門檻**。deflated 年化有效 Sharpe ≈ **0.26~0.48**。

**這不是「edge 不存在」**——point estimate 為正(有效 Sharpe > 0、in-sample 經濟價值真實存在),**是「顯著性未達確立」**:
現有證據不足以在多重比較校正後、以 95% 信心宣稱這條 edge 非運氣。**且 75.6% 本身仍是樂觀上界**(見 §4)。

**對 STAGE C/D「通過(有界)」的意義**:C/D 說的是「in-sample 扣成本後經濟價值成立」,本裁決量化了「(有界)」到底多有界——
**統計上未確立、屬 promising-not-proven**。兩者並存不矛盾:可作部署候選,但**不得對用戶宣稱「已驗證可交易」**(SOP 拍板 4)。

---

## 1. 方法 — 為何舊「89.6%」是錯的(units bug)

Bailey & López de Prado (2014) Deflated Sharpe Ratio:

```
SR_0 = √Var(SR_trials) · [ (1−γ)·Φ⁻¹(1−1/N) + γ·Φ⁻¹(1−1/(N·e)) ]      γ=0.5772(Euler)
DSR  = Φ[ (SR_obs − SR_0)·√(T−1) / √(1 − skew·SR_obs + ((kurt−1)/4)·SR_obs²) ]
```

分母是 Sharpe 估計量之漸近標準誤(Lo 2002 / Mertens),與 `SR²`、`skew·SR` 校正項、以及 `T`(期數)**全部定義在報酬被觀測的頻率上=per-period**。

**舊 `deflate_headline.py`(scratchpad)餵年化 net Sharpe 1.1972 當 `SR_obs`、卻仍配 `T=25` 的 √(T−1)**:
分子是年化尺度(= per-period × √ppy = 0.7185 × √2.776)、分母/T 是期數尺度 → **z 被灌水 √ppy 倍 → DSR 系統性高估**(把未過門檻的 edge 講成接近過門檻——最危險的樂觀偏誤,敵③向量)。

**對抗驗證**(workflow `wkubx47g6`、3 鏡獨立):
- 單位理論鏡:CONFIRM per-period 才對;isolate 實驗證年化使 z 1.25→2.96(N=8)、0.69→2.46(N=16)單調灌水。
- 獨立重算鏡:**從公式手刻**(不呼叫 augur.metrics 避同源錯)→ N=8 **0.8951** / N=16 **0.7556**,與作者逐位吻合(差 0.0000)。
- 裁決誠實鏡:CONFIRM 措辭無過度宣稱;測 1.197 正確且偏保守、N=16 保守/N=8 上界並陳誠實。

---

## 2. 結果(正確 per-period 口徑)

headline 真實序列(重跑):T=25 期、ppy=2.776、**per-period SR=0.7185**(× √2.776 = 年化 1.1972 ✓ 自洽)、
真實 skew=−0.148、raw kurtosis=2.218(薄尾,非常態校正幾乎不動 DSR)。試驗數 N 由 `trial_ledger` 機械 query(禁人手填,§6 G7)。

| N 口徑 | N | SR_0 | haircut(pp) | deflated 年化有效 Sharpe | **DSR(正確)** | 判定 | buggy 年化版(作廢) |
|---|---|---|---|---|---|---|---|
| H60 同頻家族(樂觀上界) | 8 | 0.431 | 0.288 | **≈0.48** | **89.5%** | FAIL≥95% | 96.9% |
| 全試驗混頻(保守下界) | 16 | 0.560 | 0.159 | **≈0.26** | **75.6%** | FAIL≥95% | ⚠**89.6%**(舊 note 出處) |

**舊報告 note 引用的「有效 Sharpe ~0.34、DSR 89.6%」= buggy 年化 N=16 版,作廢**;正確值 DSR 75.6%(N=16)/ 89.5%(N=8)。

---

## 3. N 與候選選擇(誠實揭露)

- **候選 SR_obs=1.197**(2014 headline):是被宣稱要 deflate 的那個 headline,正確且偏保守;不偷換成 LO 最大 1.265(2021、更短樣本=另一次選型)或全體最大 1.678(LS、已因借券成本經濟淘汰、拿死候選抬分不誠實)。
- **N=8 vs N=16**:since∈{2014,2021} 是真的搜過的自由度,SOP「取較大 N」對多重比較曝險更誠實 → N=16 為保守值。**結論不因 N 翻轉:兩端都 FAIL 95%**。
- **N=16 混頻近似**:H60(ppy 2.776)/H120(ppy 1.647)各除自身 ppy 轉 per-period 才並池算 Var(SR)——隱含「各頻率 null per-period Sharpe 同分布」之近似,但方向**保守偏嚴**(納更多試驗只會抬 SR_0、壓 DSR),不會由通過翻成失敗的相反錯誤。

---

## 4. 為何 75.6% 仍是樂觀上界(真實 DSR 只會更低)

三個未計入的樂觀偏誤,把真實 DSR 往**下**推:
1. **單 seed**:未計模型隨機性 = 少算一個搜尋維度 → N 被低估。
2. **成本平坦 0.585%**:未計市場衝擊/滑價非線性、locate 稀缺溢價。
3. **樣本 n=25 極小**:√(T−1)=√24 主導、檢定力天生低;skew/kurt 估計本身雜訊大。

故本裁決之 DSR 應讀作**「已知偏誤下的上界之保守端」,非絕對地板**。

> **⚠️ 2026-07-08 修正(survivorship 經濟重跑後)**:本節初版列「survivorship 債未閉環 → 報酬序列偏高 → 真實 DSR 更低」為第 1 偏誤——**就經典下市 survivorship 而言方向錯、已刪**。經濟重跑實證(`augur_prediction_survivorship_economic_verdict_20260708.md`、3 鏡 CONFIRM):**下市 survivorship 邊際 ≈0(+0.0023 Sharpe、16 clearing 事件 0 落 top-decile),不推低 DSR**。真正壓低 headline 的是**宇宙定義**(全史齊 1.20 vs 當下可算廣宇宙 1.00、−16.5%,屬 incumbency 非 look-ahead);用戶拍板兩宇宙並存。**若以更誠實的廣宇宙 1.00 為 base 複算 deflation,DSR 會再更低**(per-period SR 0.72→~0.60)——地板比 1.20 版更低,方向與本節結論一致(headline 為樂觀上界)、僅偏誤來源更正。

---

## 5. 對部署與後續的意義

- **可作部署候選**(H60/H120 Ridge LO,STAGE C/D in-sample 經濟價值成立、風控 profile 已量化),但**部署層須掛 `deflation_unpassed=true` 誠實旗標**、對用戶措辭為「promising-not-proven、非已驗證可交易」。
- **真正的地板釘實 = 消解 §4 四偏誤**:優先序 survivorship 債 b 經濟重跑(方向已知會下修)> 多 seed > 成本 realism;非「換更強模型」(模型側已證飽和、階段 3 ensemble 未勝)。
- **SOP 債 d(deflation 閘)狀態**:機制已建(`metrics.py` DSR + `trial_ledger` + 本裁決腳本)、已跑、誠實結果=**headline 未過**。債 d 由「未建」→「已建已跑、結果為 FAIL、待 §4 偏誤消解後複跑」。

---

## 6. 複現

```bash
cd /home/hugo/project/augur && source venv/bin/activate
python scripts/deflate_headline_verdict.py                      # 預設 Ridge H60 LO 2014、N 自 trial_ledger
python scripts/deflate_headline_verdict.py --horizon 120        # H120 候選
```
DSR 實作 `evaluation/metrics.py`(`expected_max_sharpe`/`deflated_sharpe`,單元自證見 scratchpad `deflate_headline.py` PART 1)。
N 一律由 `trial_ledger` DB query(禁人手填)。對抗驗證軌跡:workflow `wkubx47g6`(3 鏡 CONFIRM)。
