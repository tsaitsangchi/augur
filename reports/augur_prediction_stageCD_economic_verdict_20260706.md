# 股市預測 STAGE C/D — 經濟價值 #14 終關裁決(IC 是否轉成可交易)

**日期**:2026-07-06 ｜ **口徑**:A'-3 embargo 保證下界(h+62td 逐折)、asof point-in-time(#8 消 survivorship)、成本 0.585% 來回套換手
**判準**:靈魂成功定義=**經濟價值**(淨 Sharpe/MaxDD/Calmar 扣成本)**非 IC**;#14「IC 撐住 ≠ 可交易」
**方法**:8-cell 矩陣 {Ridge, GBDT} × H{20,60} × long-short{F,T}、top10%;工具 `evaluation/portfolio.py run_backtest`
**守**:#8 · #14 · #15(全 config 揭露、真兆假兆判讀、n 揭露)· #11(GBDT 多 seed 中位)
**審查**:兩鏡對抗(成本誠實鏡 PASS;cherrypick 鏡對 long-short 起爭議)→ **作者親跑 --since 2014 vs 2021 定案**(下 §三)

## 一、核心結果(Ridge,兩鏡+作者親跑三方一致)

| cell | 淨 Sharpe(2014起 n=25) | 淨 Sharpe(2021起 n=18) | 基準 | 判定 |
|---|---|---|---|---|
| **Ridge H60 long-only** | **+1.197** | **+1.265** | 0.76 / 0.94 | ✅ **穩健勝基準(兩期)** |
| Ridge H60 long-short | +1.678 | +0.406(**輸基準**) | 0.76 / 0.94 | ⚠ 期間脆弱 |
| Ridge H20 long-only | +0.265 | +0.033 | 0.30 / 0.42 | ❌ 邊際到死 |
| Ridge H20 long-short | +0.579 | −0.572 | 0.30 / 0.42 | ❌ 近期崩 |

Ridge H60 LO 全指標(2014起):淨 CAGR **16.6%**、MaxDD **−13.9%**、Calmar **1.19**、換手 0.65。**Ridge 於每個 H60 cell 皆優於 GBDT**(GBDT H60 LO 0.91、MaxDD −20.6% 更深);GBDT 額外彈性未轉成可交易 edge。

## 二、#14 裁決

**經濟價值成立——但僅在 H60 long-only(穩健真兆),非 long-short、非 H20。**
1. **H60 long-only = 可交易真兆**:扣 0.585% 成本後淨 Sharpe ~1.2、勝等權基準(亦扣成本、net-vs-net 對稱),**且對樣本期穩健**(2014起與 2021起皆勝)。**IC(B 關 +0.15)確實在 H60 long 尾轉成經濟價值。**
2. **H20 經濟上已死**:扣成本後 ≈/低於基準,alpha 需較長持有期(呼應特徵層「前沿=horizon」定論)。
3. **long-short 非穩健改良**:全期(2014起)亮眼但**近期(2021起)崩潰輸基準**;短腿的市場中性對沖是 2014-2020 regime 的產物、近期失效。**不採為結論**。

## 三、審查爭議之作者定案(#15 不憑 agent 自述)
- **run agent 未捏造**:作者以 --since 2014 親跑,精確重現其 Ridge H60 LS=+1.678 / H20 LS=+0.579 / H60 LO=+1.197。數字為真。
- **cherrypick 鏡「捏造」指控有誤**:該鏡用 --since 2021(21 panels→18 折)、據此判 run agent n=25「不可能=捏造」——實為 **--since 口徑不同**(run agent 明載 --since 2014、28 panels、n=25,與 STAGE B 同),非造假。
- **但 cherrypick 鏡的實質擔憂正確且重要**:run agent headline 把「long-short=最佳 cell 1.68、NOT worthless」拔高為結論,**未查近期穩健性**;作者親跑證實 LS 近期(2021起)輸基準 → **舊 memory「alpha 只在 long 側、long-short 不穩」於近期 regime 被重新確認**。headline 過度樂觀,應以 long-only 為準。
- **教訓(#15)**:對抗驗證抓到 headline 過度樂觀(價值),但其「捏造」歸因錯誤(--since 口徑);**唯作者親跑同口徑對照才定案**——兩個 agent 都不完全對,真兆須自證。

## 四、限制(不誇大)
1. **n 小(18-25 期)**:Sharpe/Calmar 抽樣誤差大,排名屬**方向性非精確**。
2. **成本模型簡化**:0.585% 平坦來回套換手(~65% 每期),**未計滑價/市場衝擊/放空借券成本**——真實 long-short 淨值**比表列更差**(台股放空有 locate/borrow 摩擦),更坐實 §二.3。
3. **僅 Ridge/GBDT、top10%、季頻**;H≥252 未跑(walkforward gate raise)。
4. GBDT seed 離散大(H60 LS Calmar min 0.50/max 2.06),中位為誠實中心估計(#11)。

## 五、結論
**STAGE C/D 通過(有界):augur 的預測在 H60 long-only 具真實、扣成本後、對樣本期穩健的經濟價值(淨 Sharpe ~1.2 / Calmar ~1.2 勝基準)——這是靈魂成功定義(經濟價值非 IC)的達成。** long-short 與 H20 不採。下一步 D:穩健性延伸(H120 對照、放空成本建模、更長樣本待資料累積)、部署前風控。**顧問輸出仍守「系統建議、人決策」——經濟價值成立 ≠ 保證未來、n 小屬方向性。**
