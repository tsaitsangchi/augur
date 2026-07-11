# 短 horizon 計畫(H20/H40)結案釐清報告

**日期**:2026-07-11 ｜ **性質**:結案對照(#15 實查、#16)｜ **對象**:`reports/augur_prediction_short_horizon_model_plan_20260709.md`(當時「未執行待拍板」)
**結論**:**建議結案**。原計畫 W1-W5 五工項已全數被後續工作(短 horizon 裁決 20260709、驗證總綱 V0-V2、機率層上線、方向軸判決)實質完成或升級取代;僅列 3 項誠實殘留(見 §3,皆非本計畫債、不擋結案)。

## 1. 逐項對照(W1-W5)

| 工項 | 原驗收 | 現況判定 | 證據(2026-07-11 psql 實查) |
|---|---|---|---|
| **W1** H40 口徑/embargo | walkforward splits 不 raise | **已成**(隱含) | H40 已完訓+驗證:revalidation_ledger H40 有 B(3)/D(48)/R(89) 列、trial_ledger H40=8——splits 若 raise 則無此鏈 |
| **W2** train H20/H40 + predict_asof | model_registry 加列、prediction_values 出候選 | **已成(且演化)** | model_registry `RankRidge` H20/H40 各 2 列(feats_hash `ce6286`/`3a4e66`=canonical 29 重訓,seed 42);prediction_values H20/H40 各 339 列@panel 2026-05-31、**in_portfolio=33**(計畫寫 0 候選→機率層上線後演化為每 horizon 標 top decile) |
| **W3** 誠實四關 B/C/D + deflation | ledger 補 H20/H40、DSR 出 | **已成(C 併入 D、加碼 R 軸)** | revalidation_ledger:H20/H40 各 B=3、D=48、R=89(stage C 之經濟指標 bench_sharpe/net_sharpe/dsr/deflated_sharpe_ann 全在 D;R=驗證總綱五軸,超出原計畫);`revalidate.py` B_HORIZONS/CD_HORIZONS=(20,40,60,120);DSR:H20 LO since2014=0.0013、H40=0.3083(ledger metric_name='dsr') |
| **W4** 誠實裁決報告 | 每 horizon 標裁決+日曆日對映 | **已成** | `reports/augur_short_horizon_verdict_20260709.md` + `scripts/report_short_horizon_verdict.py`:H20(≈29 日曆日)**判死**(淨 Sharpe 0.27<基準 0.30、DSR 0.001)、H40 **未確立(薄)**(alpha +0.23、DSR 0.308)、H60/H120 未確立(薄);日曆日對映在表頭 |
| **W5** 接顧問(30/60 天問題) | 端到端相對強弱+可信度+caveat+guard | **已成(被機率層升級取代)** | `advisor/payload.py` P6 相對機率附欄:讀 prediction_probability H20/40/120、prob_note 固定用語「P30←H20 ≈29 日曆日·dead;P60←H40 ≈58 日曆日·thin_unestablished」+逐折 n+同族標記;`advisor/prompt.py` 方向類問題→判死聲明+導向相對機率頁(`serve_probability_ui.py`) |

## 2. 取代/升級鏈(原計畫之外、覆蓋其意圖)

- **驗證總綱 V0-V2**:stage R 穩健性五軸(H20/H40 各 89 列)+ canonical 29 特徵重訓(feats_hash `3a4e66`)——比原計畫四關更嚴。
- **機率層上線**:`probability_oos_sample` 全 5 horizon(H20=10552 列/25 panels、H40=10548/25、H60=10549/25、H82=10545/25、H120=10211/24)→ `probability_calibrator`(platt、24 folds、purge_verified=t;H20/40/60/120 各 3 fit、H82=1)→ `prediction_probability` 5 horizon × 339 列@2026-05-31,econ_verdict 硬綁(H20=dead、餘=thin_unestablished)——原計畫「顧問回薄可信度讀數」被升級為**校準後相對機率+四誠實標記**。
- **H82 增訓**:RankRidge H82 入 registry+機率鏈全掛(隸屬方向軸 GATE 基建,非本計畫工項)。
- **方向軸判決**:六門(含 H20/H40 方向門)全判死——顧問對「30/60 天會不會漲」現答**判死聲明**、相對強弱另導機率頁,正是原計畫 §5「不會變成可靠漲跌預言」誠實預期之最終形。

## 3. 誠實殘留(照實列;皆不擋結案)

1. **RankGBDT 未入 model_registry**:計畫 W2 寫「RankRidge+GBDT 多 seed」;gbdt 有走經濟驗證(ledger H20/H40 有 `gbdt LO` 之 DSR 列:H40 since2014=0.443)但無 registry artifact、無多 seed 揭露列——裁決以 RankRidge 確定性模型為 headline。屬「已評估未存檔」,若日後要部署 gbdt 需重訓入 registry。
2. **H82 無 revalidation_ledger B/D、無 trial_ledger 列**(僅 20/40/60/120 有)——H82 之 econ_verdict=thin_unestablished 來源在機率層族群標記,非本計畫範圍,記於此供 H82 軌追蹤。
3. **本次結案未重跑顧問端到端 live 問答**(「2330 未來 30 天?」):僅以 code+DB 實查確認管線在位;W5 驗收之 live 實測依過往工作紀錄,本次未複測(#7 誠實)。

## 4. 結案裁定建議

原計畫的**全部意圖已達成**:H20/H40 誠實訓練+四關驗證+裁決標籤(判死/薄)+顧問誠實作答,且被機率層/驗證總綱以更嚴口徑覆蓋;殘留 3 項皆屬鄰接軌或工程備忘。**建議標記原計畫為「已結案(2026-07-11,由後續工作完成+取代)」**,殘留項移交:#1 → 若未來拍板部署 gbdt 時處理;#2 → H82/方向軸 GATE 軌;#3 → 顧問層例行 e2e 時順帶複測。

## 附:證據來源(#9/#10 全出自 psql/檔案實查)

DB(as-of 2026-05-31 FREEZE):model_registry(RankRidge 20/40/60/120 各 2、82=1)· prediction_values(5 horizon × 339、in_pf=33)· revalidation_ledger(20/40:B3/D48/R89;60 另有 C6)· trial_ledger(20/40/60/120 各 8)· probability_oos_sample/calibrator/prediction_probability(如 §2)。檔案:`augur_short_horizon_verdict_20260709.md`、`scripts/revalidate.py:48-49`、`advisor/payload.py:205-228`、`advisor/prompt.py:32-57`、`scripts/serve_probability_ui.py` 標頭。
