# 股市預測 STAGE D — 穩健性延伸 + 部署前風控裁決

**日期**:2026-07-07 ｜ **口徑**:A'-3 embargo(h+62td 逐折)、asof(#8)、cost 0.585%、H120 non-overlap 稀釋(持有>rebalance 須稀釋才誠實)
**新增**:`portfolio.run_backtest(short_borrow=)` 放空年化借券成本建模(long_short 才套、按 h/252 折算短腿名目)
**方法**:{Ridge, GBDT}×H{60,120}×{LO, LS, LS+borrow2%}×since{2014,2021};數字全由作者親跑 `stage_d.py`(ground truth,非 agent)
**守**:#8 · #14 · #15(全 config、小樣本揭露、真兆判讀)· #11(GBDT 多 seed 中位)

> **⚠️ 2026-07-08 deflation 校正(#15 誠實、units bug 修正)**:本報告各 cell 淨 Sharpe(H60 LO 1.197 等)皆**未 deflate**。~~2026-07-07 初版 note 曾記「有效 Sharpe ~0.34、DSR 89.6%(N=16)」~~——**該值係年化 vs per-period 單位 bug、已作廢**(舊 `deflate_headline.py` 誤把年化 Sharpe 當 per-period sr_obs、z 被灌水 √ppy 倍 → DSR 高估)。**正確 per-period 版(3 鏡對抗驗證 CONFIRM、workflow `wkubx47g6`):headline H60 LO 2014 deflate 後 DSR = 75.6%(N=16 保守)~ 89.5%(N=8),兩端皆 < 95%;deflated 年化有效 Sharpe ≈ 0.26~0.48(point estimate 為正但未達統計確立)**。且此仍為樂觀上界(survivorship/單 seed/成本平坦/n 小 → 真實更低)。**SSOT=`reports/augur_prediction_deflation_verdict_20260708.md` + `scripts/deflate_headline_verdict.py`(可複現)**。另本報告「GBDT 回檔更深/Ridge>GBDT」對 **H120 近期(2021起 n=8)不成立**(GBDT 三項全勝:Sharpe 1.028/Calmar 1.42/MaxDD −14.8% vs Ridge 0.792/0.731/−24.1%),n=8 皆不足定論。詳見 `augur_prediction_model_improvement_plan_20260707.md`。

## 一、結果矩陣(淨 Sharpe、cost 0.585%、top10%)

| since | H | config | 淨 Sharpe | 基準 | Calmar | MaxDD | n |
|---|---|---|---|---|---|---|---|
| 2014 | 60 | Ridge LO | 1.197 | 0.762 | 1.19 | −13.9% | 25 |
| 2014 | 60 | Ridge LS | 1.678 | 0.762 | 2.44 | −5.7% | 25 |
| 2014 | 60 | Ridge LS+borrow2% | 1.515 | 0.762 | 1.88 | −6.6% | 25 |
| 2014 | 60 | GBDT LO | 0.913 | 0.762 | 0.65 | −20.6% | 25 |
| **2014** | **120** | **Ridge LO** | **1.251** | 0.938 | **2.21** | **−8.7%** | 14 |
| 2014 | 120 | Ridge LS | 0.874 | 0.938 | 1.42 | −6.3% | 14 |
| 2014 | 120 | Ridge LS+borrow2% | 0.727 | 0.938 | 0.90 | −8.2% | 14 |
| 2014 | 120 | GBDT LO | 1.113 | 0.938 | 1.10 | −17.8% | 14 |
| 2021 | 60 | Ridge LO | 1.265 | 0.938 | 1.00 | −19.4% | 18 |
| 2021 | 60 | Ridge LS | 0.406 | 0.938 | 0.26 | −22.3% | 18 |
| 2021 | 60 | Ridge LS+borrow2% | 0.289 | 0.938 | 0.14 | −24.9% | 18 |
| 2021 | 60 | GBDT LO | 1.109 | 0.938 | 0.84 | −23.5% | 18 |
| 2021 | 120 | Ridge LO | 0.792 | 0.807 | 0.73 | −24.1% | **8** |
| 2021 | 120 | Ridge LS | 0.126 | 0.807 | 0.00 | −42.1% | 8 |
| 2021 | 120 | GBDT LO | 1.028 | 0.807 | 1.42 | −14.8% | 8 |

## 二、三項發現

**① H120 對照 — H120 long-only 全期風險調整最佳**
Ridge H120 LO(2014起):Calmar **2.21**、MaxDD **−8.7%**、水下最長 2 期——顯著優於 H60 LO(Calmar 1.19、MaxDD −13.9%、水下 5 期)。**呼應 memory「horizon 前沿 H120>H60」,且是在 drawdown-adjusted 上更明確**。**caveat**:H120 樣本少(全期 n=14、**近期 n=8**),2021起 H120 LO 淨 Sharpe 0.792 ≈ 基準 0.807 → **近期優勢小樣本不足以定論**(此即 §四持續再驗證要消解的)。

**② 放空成本建模 — 坐實 long-short 不採**
2%/年借券套下去:H60 LS 1.678→1.515(全期仍贏但期間脆弱)、H120 LS 0.874→0.727(**輸基準**)、2021 H60 LS 0.406→0.289、2021 H120 LS 0.126→0.043(Calmar 近 0)。**long-short 期間脆弱(C 關已見)＋放空摩擦再砍 → 確定不採;alpha 在 long 尾、非市場中性。**

**③ Ridge > GBDT(風險調整)**:GBDT LO 回檔更深(H60 −20.6% vs Ridge −13.9%),額外彈性未轉成可交易 edge。Ridge 為部署首選。

## 三、部署前風控 profile(Ridge LO、實測 DD 統計)
| horizon | 最壞單期 | 最深回檔 | 最長水下 | 負期比例 |
|---|---|---|---|---|
| H60 | −8.3% | −13.9% | 5 期 | 28% |
| H120 | −8.7% | −8.7% | 2 期 | 14% |

**建議風控(部署層落地、閾值有據)**:⚠**閾值須以近期較深回檔校準(對抗驗證修正,#15)**——上表全期(2014起)DD 溫和(H60 −13.9%/H120 −8.7%),但**近期(2021起)regime DD 明顯更深:H60 −19.4%、H120 −24.1%**;故 DD 熔斷應設**保守(H60 ~−20% / H120 ~−25% 觸發降倉,或分級)**,用全期溫和序列會在近期被觸破。單標的部位上限、換手 ~65-71%/期預算、負期連續 ≥N 期告警。(全期看 H120 回檔淺、水下短、風控壓力小於 H60;但近期 H120 DD 反而最深〔−24.1%〕,再次坐實 §四 H120 近期小樣本 caveat。)

## 四、裁決 + 前沿
- **STAGE D 通過**:預測經濟價值**對 horizon(H120 更佳)、樣本期(全期穩健)、放空成本(LS 淘汰)三重穩健性檢驗**;Ridge long-only(H60 或 H120)為部署候選,風控 profile 已量化。
- **未消解**:H120 近期 n=8 小樣本 → **§四持續再驗證**(資料累積、as-of 前推,n 變大才定論 H120 近期是否真優)。
- **限制**:n 全域偏小(8-25)、放空成本簡化 2% 平坦(未計 locate 稀缺溢價)、僅 Ridge/GBDT top10%。

## 五、複現
```bash
cd /home/hugo/project/augur && source venv/bin/activate && source <PGENV>
PYTHONPATH=src python <stage_d.py>   # RAW_JSON 為機讀;portfolio.short_borrow 已入 code
```
評估碼 `evaluation/portfolio.py`(short_borrow 新增)。本報告數字對抗驗證另附(workflow)。
