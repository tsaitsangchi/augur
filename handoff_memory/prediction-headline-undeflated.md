---
name: prediction-headline-undeflated
description: "選股 headline 淨 Sharpe~1.20 未過 deflation(DSR 75.6-89.5%<95%、units 修正後);下市 survivorship≈0、incumbency −16.5%;成本敏感度帶=主地板 pit_broad deflated 於 1.5% 成本翻負;H120 全期近門檻(保守 93.6%)但取保守未確立;別當已驗證終判引用"
metadata: 
  node_type: memory
  type: project
  originSessionId: c3c40e0c-7154-4936-8937-6d9ce947808c
---

augur 選股模型的 headline「H60 long-only 淨 Sharpe ~1.20」**不是已驗證的鐵地板**——按專案自己的 SOP(`sop_master` 債 d)它是**「12 選 1、多重比較 deflation 之前、單 seed、僅比例成本」的樂觀上界**。

**關鍵事實(2026-07-08 釘實地板、tag `prediction-floor-deflation-survivorship-20260708`、commits 0a35232+e7595ab)**:
- **deflation 閘已建並實算+units bug 修正**(`trial_ledger`+`metrics.py` DSR+`scripts/deflate_headline_verdict.py`、3 鏡對抗驗證 CONFIRM):headline 1.20 **未過 deflation**——**正確 per-period 版 DSR = 75.6%(N=16 保守)~ 89.5%(N=8),兩端皆 <95%;deflated 年化有效 Sharpe ≈ 0.26~0.48**。⚠**舊記「~0.34 / DSR 89.6% / N=8 96.9% 勉強過」係年化 vs per-period 單位 bug、已作廢**(舊 `deflate_headline.py` 誤把年化 Sharpe 當 per-period sr_obs 配 sqrt(T−1)、z 灌水 √ppy 倍 → DSR 高估~14pp)。SSOT=`reports/augur_prediction_deflation_verdict_20260708.md`。**引用 1.20 一律附「未過 deflation、DSR<95%」**。
- **survivorship 債 b 經濟閉環(2026-07-08、3 鏡 CONFIRM w4jj7dos1、`survivorship_economic_verdict.py`/報告)**:拆兩效應——**①經典下市 survivorship=實證≈0**(邊際 +0.0023 Sharpe、16 clearing 事件 0 落 top-decile;隔離跑 PIT 排除下市股仍 1.0000)**②完整度閘 incumbency(全史齊 vs 當下可算)=−16.5%**(1.20→1.00)。**教訓#15:天真「survivorship −16.3%」是誤歸(敵③)**——production `build_universe_asof` 要求「[首panel,t]全史齊」= point-in-time 無 look-ahead 但偏連續在世老股(incumbency),真下市偏誤近零、−16.5% 全來自宇宙定義;**v1-vs-v2 非單調(v2 補更多下市股 95 降幅反更小)為佐證**。**用戶拍板兩宇宙並存標註**:headline 1.20(全史齊穩定核心)/ 1.00(當下可算廣宇宙、更誠實可部署;deflation 以此 base 會更低)。清算 label(`forward_returns_pit` last_px≤exit)== 生產 forward_returns 0 diff、#8 乾淨。
- **0-B 消融**:旗艦 alpha(cycle/p2h)清洗後 Δ IC=0——「殘留污染」係誤判、特徵乾淨、飽和定論成立(不因污染動搖)。
- 所以任何「已驗證可交易」的宣稱都帶未揭露的樂觀偏誤。
- 另一相關樂觀源:**survivorship 債 b 未閉環**(`model_registry.note` 白紙黑字)、成本模型 flat 0.585% 無滑價/衝擊/借券。
- **GBDT 非「全輸 Ridge」**:H120 近期(2021起 n=8)GBDT 三項全勝(Sharpe 1.028/Calmar 1.42/MaxDD −14.8% vs Ridge 0.792/0.731/−24.1%);Ridge 只勝 H60+H120 全期。別說「換模型已否證」當定論。
- **「特徵三層飽和定論」帶條件**:掃描是在帶 close=0 污染的特徵層上跑的(cycle/p2h 旗艦 alpha),清乾淨重跑才算數。

**Why**:我先前直接對用戶引「Sharpe 1.20」「特徵飽和」當已驗證事實,正是 #15 自我欺騙——重複了 SOP 自己要防的樂觀偏誤。多視角 5 個 agent 也全犯同一錯,靠對抗審查 critic 才抓出。

**How to apply**:
- 引用 1.20 一律附標籤「12 選 1、deflation 之前、單 seed、僅比例成本 = 樂觀上界」,或說「deflated 後待定」。
- 提升精準度的**真第一優先不是換模型**,而是先釘實地板:①建 deflation 閘(trial_ledger+DSR)②清 cycle 殘留污染+raw-vs-clean 消融③消 survivorship 債(D1 已拍板方案A、閉環測試=補後 as-of IC 不升)④成本 realism。計畫見 `reports/augur_prediction_model_improvement_plan_20260707.md`。
- 「2026 最佳模型/Claude 造最精準模型」=假兆(靈魂:成功定義=經濟價值非 IC、報酬非試錯對象、clean-room 不移植外部)。

**⭐2026-07-08 部署層竣工(階段2 執行落地 + 持續再驗證 harness、tags `prediction-stage2-execution-20260708`/`prediction-revalidation-harness-20260708`)**:
- **階段2 執行落地**:風控 overlay 全接線(predict_asof 建投組+risk_control DD熔斷/cap/換手;`_deployed_dd_returns` #8 forward-窗-關閉 filter 兩向實證、off-by-one 修 future[h];prev_ids 換手 live)+ 驗收 `verify_risk_overlay.py`(生產 −20% dormant 無害、−10% 壓測證機制 MaxDD −19.4%→−16.6%、淨 Sharpe 仍勝基準)。靈魂:系統建議、人決策、不下單。
- **持續再驗證 harness(plan-first 5 鏡對抗審查 whvklsrw2 全 REVISE→v2.1、`revalidate.py` 早已是完整 harness=第2次現況救場)**:P0 兩宇宙 deflated 地板定錨(`revalidation_baseline`:全史齊 asof_incumbent net 1.197/DSR 0.756/deflated **0.265**、廣宇宙 pit_broad net 1.002/DSR 0.577/**deflated 0.070**=真可交易地板極薄但正)+ **#12 共用 `evaluation/deflation.py`**(headline verdict + harness 共用 per-period DSR、防年化 bug 復發);P1 deflation 整合進 revalidate(每輪追 DSR、部署 cell 0.7556 自洽、執行序寫→refresh trial_ledger→N→DSR、冪等);P2 **兩軌三態判停器**(`judgestop_threshold` #29b/`revalidation_verdict` no-AI;**軌A 絕對門檻 DSR<95% 只標註永不判停〔5 鏡抓 v1 首輪誤殺薄edge、命門〕、軌B 相對凍結 baseline 衰減才判停**、三態 deploying/suspected/confirmed、scoped 部署 cell、同宇宙鎖、HAC-t None 不觸發、連續 k 輪;5 命門單元測全過);P4 #8 build 端 gate 實查 `tests/test_release_lag_antileakage.py` 10 測 PASS 早存在(第3次現況救場、非重造);P3 `run_revalidation_cycle.py`(#8 gate fail-closed→revalidate→verdict→告警落地橫幅、panel-cadence #28 不輪詢)。**現況裁決 deploying_unestablished**(薄 edge 部署中、未達統計確立但無衰減=常態)。**教訓:每階段 grounding 先查現況救 3 次重造(harness/#8測試/verify都早在);plan-first 5 鏡對抗審查抓判停 DSR 誤殺命門;逐階段封存呈過目**。
**⭐2026-07-08 Tier3 地板再夯實(多seed/成本realism/H120 收尾;`reports/augur_prediction_tier3_floor_consolidation_20260708.md`)**:grounding(ultracode 4 鏡)先釘現況——三子項**皆不把已 FAIL 地板翻 PASS、只把「未確立」講到滴水不漏**,真解鎖=資料累積(Tier4)非碼:
- **多seed near-vacuous(已建)**:Ridge 確定性單跑、GBDT (42,43,44) 取中位(revalidate.py:47,202);**seed∉ trial_ledger N 鍵**(DDL migrate_trial_ledger_ddl.py:55-56 + DB 實證 seed 全 NULL、N_strict=8/N_upper=16)→ 多seed **不動 N、不移 DSR 地板**(grounding 方法論鏡「多seed 抬高 N」被 DDL 證偽);唯一價值=防 GBDT lucky-seed + #11 揭露。
- **成本敏感度帶(cost realism #15-clean、`scripts/deflate_cost_sensitivity.py` 新)**:無 tick/價差資料 → 硬報單一「真實成本」=造假兆(敵①),改報帶。cost 只作用 `net=gross−turn×cost`(LO sb=0)→ 每宇宙一次回測反推 turn 解析套用(省 N× 重跑)。ref 0.585% byte 級重現凍結 baseline。**關鍵:主誠實地板 pit_broad deflated 有效 Sharpe 於 ~1.1% 成本穿零、1.5% −0.050、2% −0.116;全史齊上界 3% 才翻負 −0.047**——台股小型股真實成本下主地板 edge 基本歸零至負。(小補 `run_pit_economic` cost 參數化+回 gross/turn,default=COST 保 survivorship byte-identical ①+0.0023/②−16.5% 驗證過。)
- **H120 收尾(候選非部署 in_portfolio=0)**:全期 since2014 DSR **保守 93.6%/樂觀 95.8%=跨 95%、取保守判未確立**(全 cell 最接近門檻最強候選、deflated eff +0.53~0.61);近期 since2021 n=8 DSR 55% exploratory。不強制凍結部署 baseline(未部署、baseline=部署參考點提前凍結語意錯)。
- **⭐bonus catch(H120 揭出敵③靜默樂觀)**:`deflate_headline_verdict.py:133` 原 `passed=dsr_hi>=0.95` **用樂觀(較小)N** 判 pass 違方法論「deflation 取較保守(較大)N」;H60 兩 N 皆 FAIL 未暴露、H120 一跨 95% 現形。**已修 `passed=dsr_lo>=0.95`**(取保守)。
- **advisor caveat 實驗→撤回(#7/#15 教訓)**:擬把成本敏感度補進 `payload.py` caveat,**單測過**(caveat 入 note、prompt.py:73 送進 LLM);**但 #7 live 實測**:暖機 Ollama 同 query 同狀態下,含此 caveat 之新碼 **2/2 確定性 number-dump**(把 payload 數字全當股票亂列、零誠實資訊)、舊碼 2/2 正常 surface picks+caveats+guard pass → **此 caveat 加長 prompt 打壞飽和的 qwen3:8b**;caveat 個別更誠實但打壞整則=淨誠實更差 → **撤回**,成本誠實住報告+腳本。**教訓:單測過≠live 過,#7「常駐服務改碼須重啟 live 實測」正為此——不 live 測就假通過**。
- **⭐2026-07-09 A(advisor 可靠度)修復(commit 8da02f0)**:grounding 定論 qwen3:8b 對選股題**連「選哪些股」都幻覺**(非只股名)+迴圈重複,**4 輪 prompt 迭代失敗模式全漂移**(number-dump→score當股票→decline→幻覺picks)=模型能力天花板、prompt engineering 負報酬。**正解=架構性:picks 是 payload ground truth→由程式確定性排版注入(advise.py `_render_picks_table`+prepend),LLM 只做它可靠的 caveat 敘述**(本機模型約束內、非換外部,v1.37.0)。配套:prompt −50%(source_ref 全同源只寫一次省~2900字/score 4dp 對齊白名單/列前15)、payload StockPick 加 name(TaiwanStockInfo)、guard⑤ 股名校驗(live 抓到「2379聯發科→應瑞昱」)。**live 實測 2/2=正確 picks(2330台積電/2542興富發…)+caveat+guard pass、零幻覺零 decline**。**教訓:弱 LLM 不該複述確定性資料(會幻覺)——確定性注入+LLM 只敘述;單測過≠live 過(#7 必重啟實測、caveat 加長 prompt 曾打壞模型 2/2 而撤回);pgrep -f 自匹配自殺 exit144 用 ss 取 listener PID。**
- **教訓**:H120 straddle 案例揭出 verdict 取樂觀 N 的靜默樂觀=deflation 閘自己也會有樂觀 bug、須用邊界案例逼出;#28 執行層本地跑腳本零 usage、grounding 用 workflow 但落地不繞 agent;**pkill -f 自匹配自殺 exit144(用具體 PID)**。
- **⭐2026-07-09 as-of 全系統凍結入憲(原則精華 v1.8.0/憲章 v1.38.0/CLAUDE v1.21、commit 5069a62)**:用戶 directive 全系統股市資料以 as-of 2026-05-31 為期限、系統完美後才接新資料。原則精華「資料完整性判準」增 **FREEZE 子條**(develop-on-frozen-snapshot、接新資料延後至系統完美後、不追新資料不以資料過期為缺陷)。**B(軌B live 新資料追蹤)正式歸未來階段**(grounding 證實現無新資料:harness 止於 2026-05-31、無排程、raw 價僅到 2026-06-17、下個 panel ~2026 末)。詳 [[ttai-integration-and-platform]]。
- **⭐2026-07-09 C(H120 部署評估)+ 追蹤候選 baseline(commit 491e595、報告 augur_prediction_h120_deployment_eval_20260709)**:親查 revalidation_ledger——**全期 H120 全面勝 H60**(Sharpe 1.251>1.197/Calmar 2.21>1.19/MaxDD −8.7%>−13.9%/DSR 93.6%>75.6%、最接近門檻)但三道封鎖(保守 DSR 93.6%<95% 未確立/近期 n=8 崩 deflated −0.054/方向隨樣本反轉 n 全小)→ **H120=最強候選非明確可部署**;用戶拍板**維 H60 部署 + 補 H120 tracked-candidate baseline**(revalidate_baseline.py 參數化 --cell/--horizon/--role candidate、明標非部署 in_portfolio=0、軌B 未來追;verdict 未寫因 state CHECK 僅 3 部署態+FREEZE 無新資料)。**⚠ freeze() non-overlap 口徑 bug catch+fix(#15)**:原走 run_backtest→walkforward.splits=每 panel 一 fold(重疊窗),H60 因 spacing 78d<panel gap 91d 恰=非重疊(部署 baseline 一直對、bug 被遮),H120 需隔期非重疊卻用重疊窗→n=24 灌水 net 1.4272;**親查對不上 ledger 1.251 才抓到**→套 `_nonoverlap(pds,H)`→H120 候選 1.251/93.6%/n=14 對齊 eval、H60 部署 1.1972/n=25 不變確認。凡凍結 H>60 cell 皆受惠。**教訓:親查數字對 SSOT(印出≠對);H60 特例會遮住 H>60 的口徑 bug**。

- 相關:[[core-universe-and-f3-model]] [[feature-execution-plan]] [[rigor-completeness-discipline]](實證不憑「我以為已驗證」)· [[ttai-integration-and-platform]](憲章 v1.37.0 advisor LLM 本機限定)。
