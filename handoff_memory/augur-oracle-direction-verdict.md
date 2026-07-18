---
name: augur-oracle-direction-verdict
description: 預言機 H 軌方向模型四座 GATE 全判死(絕對方向無顯著邊際);建置鏈與教訓
metadata: 
  node_type: memory
  type: project
  originSessionId: 72546fba-9700-443b-8926-863d212acd39
---

2026-07-11:預言機軸 H 軌端到端跑出**死亡證明**——DirStack(市場分量 P_mkt × 相對分量 rank_pctile 之 L2 logit 合成)對「個股絕對方向 P(ret>0)」在四 horizon **全部 evaluated_fail**、展示層=never_shown。

**判決數字(修正評估器後,唯讀覆算)**:關(i) hit 顯著優於樸素多數類基線——H20 edge +0.7% p=0.44 / H40 +4.9% p=0.105(最接近仍不過) / H82 +1.5% p=0.36 / H120 −2.1% p=0.91。**訊號本身近零**(非樣本太少埋沒),四門皆卡關(i)。這兌現靈魂「誠實不在都答對、在說得出自己多常對」。

**建置鏈(全本地零 token,scripts/)**:build_market_direction_features(56,673 列/4,271 panel 全史,14 特徵逐欄 visible_date #8)→ train_market_direction(MktLogit walk-forward P_mkt)→ train_direction_stack(DirStack 合成 → direction_oos_sample)→ evaluate_direction_gate(機械三關裁判)。

**關鍵教訓/踩雷**:
- macro_vintage.as_of 漏濾 `value IS NOT NULL`(FRED 缺值存 NULL)→ float(None) 崩;PIT 語意=缺值非觀測,writer 側加濾。
- walkforward.splits 的 `fold["test"]` 是**單一 panel**(pd[i])、`fold["train"]` 是 list;勿當 list iterate。
- 相對 OOS(probability_oos_sample)是**季度再平衡頻率**(每 horizon 僅 13-16 panel)、panel 落日曆期末(可能非交易日)→ 與市場分量(每日交易日)須 **LATERAL as-of 對齊**(最近交易日≤相對panel,#8 安全)非 exact-date join。
- **評估器千里眼 bug**:逐 panel 樸素基線若用 max(p̄_panel,1−p̄_panel)=偷看該 panel 實現值挑贏面;正解=全局多數類固定一個方向(p̄≥0.5→恆 up、逐 panel hit=p̄_panel)。
- **防挪門柱棘輪確實鎖死**:gate 進 evaluated_fail 即終態、trigger 拒任何轉移;發現評估器 bug 後**不可也不該偷偷重判**,改離線唯讀覆算確認判決穩健(仍全 fail)再上報。model_registry family CHECK 原僅 RankRidge/RankGBDT,方向軸加 MktLogit/DirStack/DailyLogit/DailyGBDT。

**D 軌日頻(2026-07-11 完成,全宇宙)**:build_daily_direction_features(12.4M 列/776 檔 PIT 成分/2777 交易日/9 特徵:價量動能波動 lag0+市場 IV/TAIEX context)→ train_daily_direction(DailyLogit+DailyGBDT 年塊 walk-forward、champion 寫 OOS 各~121萬列)→ 兩門判決:
- **dgate_D_1(次日)**:hit 0.5516 vs 多數類 0.5484,p=0.124 關(i)不過 → fail(校準佳 ECE 0.0145、但無顯著方向邊際)。
- **dgate_D_5(5日)**:關(i) **過了**(hit 0.5193 vs 0.5018,+1.75pp,Eff-t 1.773,p=0.038,120萬樣本)——六門唯一過顯著性者;**卻卡關(ii)Brier(0.2535>基準0.25)**=機率品質比猜基率還差、有信心猜錯吃光準確率優勢 → **仍 fail/never_shown**。教訓:有微弱統計訊號≠可交易;GATE 三關「不只問猜對沒、還問報的信心可不可信」正確攔下。經濟:+1.75pp 遠低於損益兩平≈66.5%(cost 0.585%)→ 經濟死透。

**經濟終關(run_direction_econ_eval)關鍵假兆**:DirStack p_up=f(P_mkt,rank_pctile)、P_mkt panel 內全股同值 → panel 內 p_up 排序≡rank_pctile 排序 → 「long top p_up」實測=既有相對模型已知邊際借屍還魂、**非絕對方向技能**(alive 屬假兆)。正解=隔離市場擇時 overlay(P_mkt>0.5 才進場 vs buy&hold):H40/82/120 擇時從沒差異化決策(P_mkt 恆>0.5)=零貢獻、H20 alive 屬 16 panel 雜訊。方向模型無獨特經濟價值。

**總結:六門(H20/40/82/120+D1/D5)全 evaluated_fail/never_shown**——預言機產不出可信可交易的絕對方向數字,每層照設計如實呈真相。

**MC 模擬情境(simulate_mc_paths.py,2026-07-11 完成)**:憲法唯一允許回應「逐日股價變化」的形式(§1.2 逐日價格路徑永久除外、唯以模擬呈現)。純歷史重抽(iid+block bootstrap 區塊21td、n_paths=10000、seed顯式可重現)、**不以任何模型 tilt 抽樣**(§3.8 杜絕模擬夾帶預測);只存 summary 分位錐(不存逐路徑)、is_simulation DB CHECK 硬綁 true(試插 false 被擋)。輸出=逐日 p5/25/50/75/95 錐+終值分布+模擬 P(終值>0)。**誠實陷阱**:純歷史重抽帶該股歷史漂移→2330 近3年AI大漲使長 horizon 中位大幅上揚(h126 中位+30%、P(終值>0)=91%),**極易誤讀成方向預測**——故四鎖(①disclaimer硬綁「模擬非預測」②數字不入 chat payload〔僅/simulate頁〕③只存摘要④憲章§1.2)。**UI+chat 誠實層(2026-07-11 完成)**:serve_probability_ui.py 加 `/simulate`(內嵌 SVG 扇形、琥珀系與 direction 零共用視覺、浮水印硬綁、seed 揭露)+ `/direction`(六門判死死亡證明誠實呈現、never_shown 不出方向機率)。advisor chat 閘⑥/lock②:prompt.py `_asks_direction_or_path`(每日/逐日/未來N天/準確率最高/漲跌/目標價)命中 → advise.py **短路弱 LLM 直回 DIRECTION_PATH_FIXED_RESPONSE 固定誠實句**(判死+指引模擬/相對頁);live 實測 0 秒即時、guard pass、零編造股價;純相對問(報酬最高前N、不含這些詞)不誤觸、照走選股主路徑。回歸 64 測試綠。

**專案完成度(誠實邊界)**:護欄內全建完(六門判決+MC+UI+chat 誠實);**未竟三項⚠2026-07-17 實查全已完成**:①GATE v3 已 PASS(`gate_43044a574c0d`,engine 100% vs 53.3%、假確認 0、McNemar 顯著)→引擎已脫 experimental;②frontend_tiers.enabled 已翻 true(2026-07-11);③方向軸全碼已在 origin/main。詳見 [[augur-oracle-pivot]] [[augur-validation-master-plan]] [[augur-deliberation-engine]]。
