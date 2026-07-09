# 股市預測 — H120 部署評估(H120 vs 部署主投組 H60)

**日期**:2026-07-09 ｜ **性質**:部署決策支援(READ-ONLY 分析、凍結快照 as-of 2026-05-31)｜ **層級**:決策層建議(部署切換=人拍板,靈魂「系統建議、人決策」)
**口徑**:Ridge LO top10%、cost 0.585%、asof panels、A'-3 embargo;數字全由作者親查 `revalidation_ledger`(非轉述 agent、#15)
**守**:#8 · #12 · #14(經濟價值)· #15(誠實、取保守 N、n 小標 exploratory)· #19/#26(部署切換屬決策層停下問)· 原則精華 FREEZE(凍結快照上評估)

---

## 0. 三十秒結論

**H120 是「最強候選」、不是「明確可部署」。維持現狀:H60 續為部署主投組、H120 續為追蹤候選。不切換。定論待資料累積(卡~5 年)。部署切換屬決策層、須人拍板。**

- **全期(since2014)H120 全面勝 H60**(Sharpe 1.251>1.197、Calmar 2.21>1.19、MaxDD −8.7%>−13.9%、DSR 93.6%>75.6%),且 DSR 93.6% 是**所有 cell 中最接近 95% 門檻者**。
- **但三道封鎖**:(a) 保守 DSR 93.6% 仍 **<95%**、取保守 N 機械閘判**未確立**;(b) 近期(since2021)n=8 崩壞——deflated **翻負 −0.054**、Sharpe 0.792≈基準、輸同格 GBDT;(c) 方向隨樣本期反轉(全期 H120 勝/近期 H60 勝)、n 全小、差值可能在抽樣誤差內。

---

## 1. H60 vs H120 對比(親查 revalidation_ledger)

| 指標 | H60 全期 | **H120 全期** | H60 近期 | H120 近期 |
|---|---|---|---|---|
| **n(非重疊期)** | 25 | 14 | 18 | 8 |
| as-of IC / HAC-t | 0.1521 / 6.945 | 0.1551 / 6.929 | — | — |
| 淨 Sharpe | 1.1972 | **1.2510** | 1.2654 | 0.7917 |
| Calmar | 1.1889 | **2.2082** | 1.0002 | 0.7309 |
| MaxDD | −13.92% | **−8.72%** | −19.43% | −24.14% |
| DSR(保守 N) | 75.56% | **93.59%** | 57.94% | 46.78% |
| deflated 有效 Sharpe | 0.2646 | **0.5327** | 0.1142 | **−0.0539** |

- **as-of IC**:H120(0.1551)≈ H60(0.1521),HAC-t 皆 ~6.9 顯著;IC 層 H120 略勝但差微。
- **全期經濟**:H120 風險調整**全面較優**——尤 Calmar 近 2×(2.21 vs 1.19)、MaxDD 淺 5pp(−8.7% vs −13.9%)=H120 長 horizon 之低頻換手/深度更穩。
- **近期經濟**:反轉——H120 崩(Sharpe 0.792、deflated 負),H60 尚可(1.265)。**根因=H120 近期 n 僅 8**(長 horizon→非重疊期少→近窗樣本極小)。

## 2. 對 SOP 部署判準(§3-V5)之評比

部署門檻(deflated net Sharpe≥1.0 ∧ Calmar≥0.5 ∧ MaxDD≤25% ∧ 優基準 ∧ 過 deflation 確立):

| 判準 | H120 全期 | 達標? |
|---|---|---|
| deflation 確立(DSR≥95%) | 93.6%(保守 N) | ❌ **未過**(最接近、仍差 1.4pp) |
| deflated net Sharpe≥1.0 | 0.53(deflated)/ 1.25(未 deflate) | ⚠ 未 deflate 過、deflated 後 0.53 |
| Calmar≥0.5 | 2.21 | ✅ |
| MaxDD≤25% | 8.7% | ✅ |
| 優基準 | 1.251 vs bench 0.938 | ✅ |

**H120 全期過多數子項、唯 deflation 確立(命門閘)未過** → 機械判**未確立(deploying_unestablished)**,同 H60。H120 只是「最接近門檻的候選」、非「已驗證可部署」。

## 3. 誠實封鎖(不可宣稱之事)

1. **近期 n=8 硬封鎖**:H120 since2021 DSR 55%→無法宣稱 out-of-sample 撐住;n≥20 需 ~5 年資料(AI 無法加速、原則精華 FREEZE 下明文待系統完美後接新資料)。近期定論一律標 exploratory(SOP §228 樣本閘、`model_registry.note` 已自標)。
2. **deflation 未過為兩 horizon 共通**:H120 93.6% / H60 75.6%,**皆未確立**;且 93.6% 仍是樂觀上界(單 seed、成本平坦 0.585% 未計滑價/衝擊、廣宇宙 base 更低——Tier3 成本敏感度帶:主地板 1.5% 成本即翻負)。
3. **不可宣稱「H120 明確優於 H60、可切換」**:全期 H120 勝、近期 H60 勝,方向相反、n 全小(8-25)、Sharpe 差 0.05-0.3 可能在抽樣誤差內。
4. **部署切換屬決策層**:靈魂「系統建議、人決策」+ #19/#26——AI 只出建議+逐項證據,**不自行改 `prediction_values.in_portfolio` / `payload._DEPLOY_HORIZON`**。

## 4. 部署機制現況 + 「切換」會動什麼

- 現況:H60 `in_portfolio=34`(部署主投組)、H120 `in_portfolio=0`(追蹤候選);`payload.py` `_DEPLOY_FAMILY=RankRidge`+`horizon=60` 選出部署 cell;`prediction_values.in_portfolio` 為 DB 側 SSOT;risk_policy 已備 H120 −25% DD 熔斷。
- 「切換 H120」會動:`predict_asof --horizon 120` 標 in_portfolio、`payload._DEPLOY_HORIZON=120`、harness 部署 cell 改 `ridge_H120_LO`、凍結 H120 baseline。**這些都不做**(未達確立、屬人拍板)。

## 5. 建議(決策支援、非執行)

**維持現狀 + 強化追蹤**(可 AI 執行之部分,凍結快照內):
1. **H60 續部署、H120 續追蹤候選**——不切換(未過確立、近期未證)。
2. **H120 harness bookkeeping 補全**(可選,執行層):凍結 H120 tracked-candidate baseline + verdict(標 deploying_unestablished、非部署),使軌B 未來資料到時能同時追 H120 衰減。(注:此非「部署」、僅「追蹤登錄」;若做需明確標候選非部署。)
3. **定論待資料**:H120 全期近門檻是「值得等」的訊號;待 as-of 推進(系統完美後接新資料)、H120 非重疊期 n 由 14→≥20,再複評是否切換。

**須你拍板者**:是否 (a) 維持 H60 部署(建議)/ (b) 切 H120 / (c) 為 H120 補 tracked-candidate baseline(讓軌B 未來一併追)。**AI 不自行切換**。

## 5.1 已執行(用戶拍板 2026-07-09:維 H60 + 補 H120 追蹤候選 baseline)

- **`revalidate_baseline.py` 參數化**(--cell/--horizon/--role);`--role candidate` 標「追蹤候選·非部署(in_portfolio=0)·軌B 待新資料追衰減」。
- **凍結 H120 tracked-candidate baseline**(`revalidation_baseline` cell=ridge_H120_LO 兩宇宙):asof_incumbent net 1.2510/DSR 93.6%/deflated 0.533/n=14、pit_broad net 1.0903/DSR 82.9%/n=14。**非部署**(H60 續為 in_portfolio 部署主投組、未動)。
- **⚠ non-overlap 口徑 bug 修(#15、freeze() 命門)**:原 `freeze()` 走 `run_backtest`→`walkforward.splits`(每 panel 一 fold=**重疊窗**);H60 因 spacing(78d)<panel gap(91d) 恰=非重疊(故部署 baseline 一直正確、bug 被遮),但 **H120 需隔期非重疊、原用重疊窗 → n=24 灌水 net 1.4272**(親查對不上 ledger 1.251 才抓到)。修:freeze() 套 `_nonoverlap(pds, H)`(H60 全保留不變、H120 隔期取 n=14)→ **H120 候選與 eval/ledger 一致(1.251/93.6%)、H60 部署不變(1.1972)確認**。此為 baseline 口徑正確化,凡凍結 H>60 cell 皆受惠。
- **軌B verdict 未寫**:FREEZE 下無新資料可判、且 `revalidation_verdict.state` CHECK 僅 3 部署態(無 candidate 態)→ verdict-tracking H120 屬未來階段(隨軌B/B 延後至系統完美後);baseline 參考點已就位、待新資料到時即可追衰減。

## 6. 複現
```bash
# H60 vs H120 對比(親查):
psql -d augur -c "SELECT horizon,config,metric_name,metric_value,n_periods FROM revalidation_ledger WHERE model='ridge' AND config LIKE 'LO|%' AND metric_name IN ('net_sharpe','net_calmar','net_maxdd','dsr','deflated_sharpe_ann') AND horizon IN (60,120) ORDER BY config,horizon;"
python scripts/deflate_headline_verdict.py --horizon 120 --since 2014   # H120 全期 deflation(取保守 N)
```
- 全數字 trace 回 `revalidation_ledger`(as-of 2026-05-31 凍結快照);未親跑新回測(READ-ONLY、FREEZE)。
