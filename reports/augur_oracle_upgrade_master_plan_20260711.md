# Augur 預言機升級主計畫(合體定稿)

**檔名**:`reports/augur_oracle_upgrade_master_plan_20260711.md`|**日期**:2026-07-11
**性質**:計畫先行報告(憲章第六部 plan-first;觸高風險門檻——跨 ≥2 治權檔+判準變更 → 多視角級,S1/S2/S3 三段草稿經對抗批判後依發現表修訂合體,對照見 §0.6)
**資料據**:as-of `2026-05-31` FREEZE 凍結快照(不動;庫內存有至 2026-06-17/18 之列屬歷史 sync 遺留,使用口徑一律 `date <= '2026-05-31'`,實查吻合)
**實查紀律**:本定稿全部量化數字於 2026-07-11 對本機 `augur` 庫(public schema)**重新實查**(#9 來源 (b) DB query/(a) code 事實);與草稿有出入之數字以本定稿為準(見 §0.6 X 項)。標明「設計級試算」者為對實查數字之算術推演,非回測結果。
**閱讀時間**:30-40 分鐘。

---

## 目錄

- §0 三十秒總覽・勸阻留痕・可證偽賭注宣言(含 §0.5 實查來源、§0.6 批判修訂對照表)
- §1 憲章 v1.42.0 修正草案全文(親核拍板;AI 不逕改 `docs/`)
- §2 H 軌設計:絕對報酬分解 → P(ret>0 | as-of, H)
- §3 D 軌設計:逐日方向機率+蒙地卡羅模擬情境
- §4 資料增補軌:先盤點既有、實證缺口才增補
- §5 模型增補/創造軌:challenger 方法論
- §6 準確率定義+呈現服務(雙態)+guard 設計
- §7 表與程式雙落實(#20 v1.39.0)+分階段+驗收
- §8 拍板點彙總

---

## §0 三十秒總覽・勸阻留痕・可證偽賭注宣言

### 0.1 三十秒

用戶(決策層)三度堅持拍板:把 Augur 的靈魂由「只做橫斷面**相對強弱**」擴為「**預言機方向**」——

- **H 軌**:個股於 as-of `2026-05-31` 後 **30/60/120 天**的**絕對方向機率** P(報酬>0 | as-of, H)+歷史準確率,個股層+top3/top5 組合層。
- **D 軌**:**逐日粒度**亦入——可驗形=次日/k 日**方向機率**(逐日**價格點位/路徑**永久除外、修憲明文)。
- **增補軌**:需要時之**資料增補、預測模型增補與新模型創造**亦入計畫(先盤點既有——市場方向資料已在庫 19 表實查——實證缺口才增補)。

架構=**絕對報酬分解**:市場分量(新模型)×相對分量(既有 RankRidge+Platt 校準,全套沿用不重造)。**一切絕對/逐日輸出=預註冊可證偽實驗,過 GATE 才展示於服務**;三不動(三敵零容忍/FREEZE as-of/相對機率層不退化)寫入憲章 v1.42.0 草案(§1)。

### 0.2 勸阻留痕全文(AI 依 #19/#26/#27,如實留痕、不消音)

AI 於用戶指示前後**兩度勸阻**,理由全文:

1. **相對 edge 已 thin/dead,絕對更難**:實查 `econ_verdict_rule`(5 列)——H20=`dead`、H40/H60/H82/H120=`thin_unestablished`。相對排序尚且如此,絕對方向預測須額外贏過多數類樸素基線(實查 TAIEX H120 重疊窗 up-rate 0.7714、H82 0.7396、H60 0.7117——「猜漲」基線本身已極強),成功機率更低。
2. **逐日價格點位/路徑無 out-of-sample 真兆=假兆製造機**:日頻點位預測在本系統與公開文獻均無可溯源的 OOS edge 證據;輸出點位=製造假兆,直接觸敵人①③。
3. **日頻成本使 D 軌經濟終關幾乎必死**:台股來回成本 0.585%(實查 `scripts/predict_asof.py:37` `COST_TW=0.00585`,與 `evaluation/portfolio.py:85` 回測同口徑),而 TAIEX 日絕對報酬中位數僅 0.553%、日報酬 σ 1.106%、lag-1 自相關僅 +0.035(實查 n=4,270)——訊號量級與成本量級同階。
4. **三敵零容忍不動**:無論結果多想要,假資料/偷看未來/自我欺騙不是試錯對象(#27 凌駕邊界)。

### 0.3 用戶決策與成立條件

用戶已兩度聽取勸阻後**堅持**(2026-07-11 決策層拍板、三度擴充)。依「系統建議、人決策」,決策成立;AI 轉入執行層,以誠實機制內建為前提落地:①一切絕對/逐日輸出=**預註冊可證偽實驗**(判準先寫死、才跑數字),過 GATE 才展示服務;②勸阻與堅持**雙留痕**(本 §0+憲章修訂歷程行);③敗退路徑**預先寫死**(§0.4)——實驗死亡=誠實結果,非失敗、非重跑到過為止。

### 0.4 可證偽賭注宣言(敗退路徑寫死,先於任何數字)

> **總則**:以下判準於跑任何 OOS 數字**之前**寫死並預註冊入 `direction_gate`(鏡射 `prediction_unfreeze_gate` 之 preregister→approve→evaluate 狀態機;該表實查現有 2 列、機制已存)。判準一經預註冊即不得為「想過關」而挪門柱;挪門柱唯決策層依既有 trigger 紀律。

**GATE 內含物與展示分級(單一定義,全文唯此;修訂 C2)**:

- **GATE(兩軌同構、各自獨立)**=三統計/校準關同過:(i) hit-rate 顯著優於同窗**多數類樸素基線 max(p̄, 1−p̄)**(HAC Eff-t 口徑、禁 iid;修訂 B2——實查個股 H20 up-rate 0.4856、日頻 0.4657 均 <0.5,「恆漲」基線在此反而較弱,故基線一律取多數類);(ii) Brier 優於基線 p̄(1−p̄);(iii) 校準通過(ECE ≤ judgestop `calib_late_ece_ceiling`=0.05〔DB 引用值〕+機率分位桶單調)。
- **經濟終關(econ_verdict)=獨立標示軸**,不在 GATE 內,但與機率數字硬綁呈現、不可分離。
- **展示分級閉集**:①GATE fail → **判死留檔、永不出 UI**(封鎖頁只顯 gate 狀態,零數字);②GATE pass 且 econ_verdict∈{dead, thin_*} → 僅得「**研究級指標頁**」誠實展示(每值硬綁 econ_verdict 標籤+「非交易訊號」聲明;H20 dead 前例同款),**永不以可交易訊號姿態呈現**;③GATE pass 且經濟存活 → 完整展示(仍帶全部誠實標記)。此分級入憲(§1.2),消除草稿三文不一致。

**H 軌賭注**:「市場分量×相對分量之合成,能在 horizon 級聚合上同時過 (i)(ii)(iii)。」
**H 軌敗退路徑(寫死)**:任一 horizon 未同過 → 該 horizon 判死留檔(`direction_gate` 記 verdict)、永不出現於服務 UI;相對機率層照常、零影響。全部 horizon 判死 → H 軌止於研究紀錄,以「實驗完成、假說證偽」結案。**H120(若採為 120 天錨,見 §2.2)非重疊窗 n=35(實算)→ 預先降為 review 級**:即便樣本內數字好看,最高只得「證據不足、觀察名單」。

**D 軌賭注**:「次日/k 日方向機率能以日頻巨大 n(實算 4,271 交易日、個股面板 **1,462,473** stock-days;修訂 A2)之檢定力,統計上顯著優於多數類基線且校準通過。」
**D 軌敗退路徑(寫死,誠實預期=經濟終關幾乎必死)**:(a) 統計關未過 → 判死留檔、全下架,僅留研究報告與 `daily_direction_oos_sample` 審計資料;(b) 統計關過但經濟終關(來回 0.585%、`run_economic_eval` 同口徑)判死 → 依展示分級②降為研究級指標頁,明標「統計可辨、經濟不可交易」;(c) 逐日價格點位/路徑:**無賭注、無 GATE、永久除外**(修憲條文 §1.2;路徑需求唯以蒙地卡羅模擬情境滿足,硬綁「模擬非預測」)。實查:TAIEX 日報酬 lag-1 自相關 +0.035(R²≈0.12%)×日 σ 1.106% vs 成本 0.585%——**本計畫預先寫死:D 軌經濟終關幾乎必死,若果真死亡即為預期內誠實結果**。

**兩軌 GATE 獨立**:H 軌任何結果不解鎖 D 軌,反之亦然。

### 0.5 本定稿實查來源清單(#9/#10 可溯源;2026-07-11 全部重跑)

| # | 實查項 | 結果 | 來源 |
|---|---|---|---|
| Q1 | 交易日 2008-12-31→2026-05-31 | **4,271**(日報酬 n=4,270) | `TaiwanStockPrice`(2330) distinct date;`TaiwanStockTradingDate` 表存在可為日曆 SSOT |
| Q2 | TAIEX 日頻統計 | up-rate 0.5550、σ 1.106%、中位絕對日報酬 0.553%、lag-1 +0.035 | `TaiwanStockTotalReturnIndex`(TAIEX) 實算 |
| Q3 | TAIEX H up-rate(重疊窗) | H20 0.6448/H40 0.6909/H60 0.7117/**H82 0.7396**/H120 0.7714 | 同上,前視窗實算 |
| Q4 | 非重疊窗 n | H20 213/H40 106/H60 71/H82 52/H120 **35**/k=1 4,270/k=5 854 | floor(4,270/h) 實算 |
| Q5 | `probability_oos_sample` | 總 41,860;H20 10,552·25 panels·up 0.4856/H40 10,548·25·0.5484/H60 10,549·25·0.5606/**H120 10,211·24·0.5821**;含 `fwd_ret`(絕對前視報酬)欄 | DB 聚合+schema |
| Q6 | 個股日頻(core_universe 344 檔,2019-01-01~2026-05-31) | n=617,466;up-rate 0.4657;中位絕對日報酬 0.794% | `TaiwanStockPriceAdj`×`core_universe` 實算 |
| Q7 | stock-days 面板(2008-12-31~2026-05-31) | **1,462,473** | 同上 |
| Q8 | 既有資產列數 | `model_registry` 8 列(RankRidge×H20/40/60/120 各 2,**無 H82**)、`probability_calibrator` 12 列/4 horizons(method=platt、purge_verified=true)、`econ_verdict_rule` 5 列(**含 H82**)、`prediction_unfreeze_gate` 2 列(status 現值集={frozen, superseded})、`judgestop_threshold` **11 列**(hac_t_floor 2.0 frozen/calib_late_ece_ceiling 0.05 frozen/dsr_annotate 0.95 frozen…)、`prediction_values` 1,356、`fred_series` 343,848 列/31 series | DB query |
| Q9 | 19 市場表+國際指數 | 全數在庫,逐表列數/日期範圍見 §4.2;`USStockPrice` 35.05M(1928 起)/`JapanStockPrice` 16.8M/`EuropeStockPrice` 4.17M/`UKStockPrice` 亦存 | information_schema+逐表 count/min/max |
| Q10 | 遺留資料邊界 | `TaiwanStockPrice` max=2026-06-17、TRI max=2026-06-18(口徑一律 ≤2026-05-31) | DB query |
| Q11 | code 事實 | `predict_asof.py:37` COST_TW=0.00585;`portfolio.py:85` cost 同值;`calibrate_relative_probability.py:41` `CAL_DAYS={20:29,40:58,60:87,82:119,120:174}`;`baseline.py:30` CANONICAL_START=2008-12-31;`metrics.py:89` effective_t_hac;`walkforward.py:37` splits(...calendar=)保證下界 guaranteed=True;`ranker.py:16/41` RankRidge/RankGBDT;`registry.py:25/41` register/latest;`serve_probability_ui.py:31` 127.0.0.1:8600;`run_economic_eval.py:20-22` `_nonoverlap`(1.45 日曆日/交易日);`guard.py:22-28,57` 五閘正則;`payload.py:30` numbers();`migrate_probability_ddl.py:88-90` 表 COMMENT 含「禁絕對漲跌機率(憲章 v1.40.0)」 | 逐檔 Read/grep |
| Q12 | 治權檔現行 | `docs/系統架構大憲章_v1.41.0.md`(L125 禁令句逐字存在;L262 修訂歷程 3 行封頂體例)、`docs/系統核心思想_v1.5.0.md`(「任務」「它不是」行逐字存在)、原則精華 v1.8.0 | 逐檔 Read |

### 0.6 批判修訂對照表(定稿 vs 三段草稿)

對抗批判發現表 16 項全數修訂;另自查補正 3 項(X)。

| 編號 | 缺陷(草稿) | 修訂 | 落點 |
|---|---|---|---|
| C1【嚴重】 | 「GATE 前任何絕對機率數字必被閘②攔」失真——閘② 只攔 ≥2 位小數+指標詞鄰接數字,整數/1 位小數(「60%」「約 0.6」)漏網;且與自訂「不改 guard 一字」互斥 | 撤「不改 guard 一字」自訂鐵律,改為治權要求⑤之精確形:「**擴白名單+新增加嚴閘=合憲;放鬆/豁免既有閘=禁**」。新增閘⑥(機率詞鄰接數字、%與「成」正規化後查白名單);誠實揭露機械閘殘餘面(中文數字「六成」),防線=payload fail-closed(GATE 前 LLM 上下文根本無絕對機率資料)+紅隊驗收集 | §6.5 |
| C2【嚴重】 | D 軌 GATE 內含物三文不一致(研究紀錄 vs 研究級指標頁 vs 永不出 UI) | 單一定義:GATE=統計+校準三關;經濟終關=獨立標示軸;**展示分級閉集**(fail=永不出 UI/pass+dead=研究級誠實展示/pass+存活=完整展示)入憲明文 | §0.4、§1.2、§3.7 |
| C3【中】 | 「guard 白名單僅在模擬 frame 內放行」——guard 無 frame 機制,引用了不存在的機制 | 刪 frame 語;改為**模擬數字根本不入 chat payload**(僅 UI 頁呈現;chat 對模擬僅回固定句+頁面指引,LLM 覆述模擬數字=被閘②/⑥攔=正確行為) | §3.8、§6.5 |
| C4【小】 | `'evaluated_pass'` 字面值未定義(unfreeze_gate 現值集={frozen,superseded},字彙不同) | `direction_gate` DDL 自帶 status **CHECK 封閉枚舉**('preregistered','approved','evaluated_pass','evaluated_fail','superseded'),明文不繼承 unfreeze_gate 字彙 | §2.6、§7.1 |
| D1【小】 | k=5 損益兩平寫 66.4%,依自身公式應為 66.5% | 重算 (1+0.585/(0.794×√5))/2=0.6648→**66.5%** | §3.0 |
| D2【小】 | 模擬表名雙軌(mc_simulation_run vs direction_simulation_run) | 統一 **`mc_simulation_run`**(#12) | §3.8/§6.4/§7.1 |
| A1【嚴重·錯數】 | §3 寫「H120 非重疊窗 n≈8」與他段 35 矛盾 | 實算 floor(4,270/120)=**35**,全文一致 | §3.2、§2.4 |
| A2【嚴重·錯數】 | 「個股面板約 1.8M 樣本」無來源 | 實查 **1,462,473**(Q7) | §0.4、§3.2 |
| A3【小】 | 大盤日頻 base-rate 標 n=4,271 | 交易日 4,271、日報酬 **n=4,270**,分開標 | §6.1 |
| A4【小】 | 個股 base-rate 概括「25 panels」 | H120 為 **24 panels/10,211 列**,逐 horizon 標 | §6.1 |
| B1【嚴重】 | 「30/60/120 天」對映只裁 30、漏 60/120——60/120 天錨在 H60(≈87 日曆天)/H120(≈174 日曆天,+45%),與 `CAL_DAYS` SSOT 及前計畫(omniscient e2e 20260710)裁決矛盾 | **整條 H 軌 horizon 錨點重裁**:30 天→H20(29 cal,−3%)、60 天→**H40**(58 cal,−3%)、120 天→**H82**(119 cal,−1%;條件=增訓,econ_verdict_rule 已有 H82 列)為主錨、H120(+45%)為研究對照;拍板點 P2-1;base-rate/檢定力/UI 卡全表隨改 | §2.2、§6.1、§6.2、§6.4 |
| B2【重要】 | 憲章草案基線寫死「恆漲 base-rate」——個股日頻 up-rate 0.4657<0.5,恆漲=較弱門柱直接入憲 | 全文改「**多數類樸素基線 max(p̄, 1−p̄)**」;Brier 基線 p̄(1−p̄) 不變(對稱) | §0.4、§1.2、§6.1 |
| B3【中】 | 修訂歷程行遠超「3 行封頂」體例(憲章 L262 實查) | 縮至 3 行內,長論證住本計畫 | §1.6 |
| B4【小】 | 同步清單漏 code/DB 註釋層(`migrate_probability_ddl.py:90` COMMENT 寫死「禁絕對漲跌機率(憲章 v1.40.0)」,修憲後成過時全稱) | 同步清單增列:該 COMMENT 文字改 GATE-scoped+冪等遷移對既有 DB `COMMENT ON` 更新+執行期全 repo grep 引用點 | §1.7、§7.2 |
| E1【重要】 | 增補軌 vs FREEZE 詮釋未裁(「期限凍結≠來源集凍結」,新增歷史來源改變快照組成、破壞 dump 可複現) | 明文列**拍板點 P4-1**(判準詮釋屬決策層)+`freeze_manifest` 快照版本化機制;v1 起步**零新外部源**(19 表+本地推導即足),唯實證缺口成立才觸 P4-1 | §4.5 |
| F1【嚴重】 | 閘③ `_FUTURE_LEAK` 必攔 D 軌過 GATE 後自然措辭(「明日…漲」「下週…漲」「未來…會漲」),草稿未裁 | 合法措辭**確定性模板寫死於 builder 常數**(避開 明日/明天/下週/未來+會漲 等 token;LLM 改寫成保證語=閘③攔=正確 fail-closed);模板句過閘、對抗句被攔=驗收項 | §6.5、§7.4 |
| X1(自查) | §5 寫 judgestop「12 列」 | 實查 **11 列** | §5.3 |
| X2(自查) | TAIEX 日 σ 1.108%/lag-1 +0.036 | 本定稿重跑=**1.106%/+0.035**(以重跑為準) | §0.2 |
| X3(自查) | top3/top5 組合層檢定力未明標 | 組合層每 panel 僅 1 觀測(n≤25/horizon)→明標小樣本、隨個股層 GATE 但單獨列 n | §2.5 |

**批判已驗證無誤(PASS)之草稿主張(維持)**:成本 0.00585 兩處同值;被改憲章句/靈魂句逐字存在;庫內 2026-06-17/18 為遺留、口徑 ≤2026-05-31;TAIEX 各 H up-rate;41,860 列 OOS;core_universe 344;econ_verdict 現況(H20 dead 等);`CAL_DAYS` 內容;走 `visible_date`/macro_vintage 前例之 #8 設計;D 軌成本試算方向。

---

## §1 憲章 v1.42.0 修正草案全文(親核拍板;AI 不逕改 `docs/`)

### 1.1 修正範圍與定位

- **現行**:憲章 v1.41.0(實查檔名)、靈魂 v1.5.0、原則精華 v1.8.0。
- **衝突事實(必須修法才能做,不可繞)**:①靈魂「它預測什麼」明文「不是預測絕對漲跌幅」「它不是……單日漲跌神算」(實查逐字);②憲章第三部 validate「相對機率誠實判準〔v1.40.0〕」明文「**禁止輸出或暗示絕對漲跌機率**(『N 天會漲的機率』=假兆)」(實查 L125 逐字)。→ 本次為**判準變更**(決策層專屬),條文全文附此、用戶親核後 AI 才改 `docs/`。
- **升版性質**:憲章 v1.41.0→v1.42.0、靈魂 v1.5.0→v1.6.0;原則精華 20 條法律全文未動 → 維持 v1.8.0(僅交叉引用行更新)——此歸類本身為拍板點 P1-5。

### 1.2 條文一(新增):第三部 validate 層增「預言機誠實判準(絕對方向機率軸)〔v1.42.0〕」

> **預言機誠實判準(絕對方向機率軸)〔v1.42.0〕**:系統得增設**絕對方向機率**輸出軸(預言機軸),與 v1.40.0 相對機率軸並立、**疊加不拆**:
> - **合法輸出形**:P(個股 H 內絕對報酬>0 | as-of)(H 軌:日曆 30/60/120 天之交易日對映 horizon;個股層+top3/top5 組合層)與日粒度方向機率(D 軌:次日/k 日方向)。兩軌 GATE 獨立。
> - **唯一合法產生路=預註冊可證偽實驗**:統計/校準判準**先寫死**於 `direction_gate`(鏡射 `prediction_unfreeze_gate` 狀態機:preregister→approve→evaluate;approve 唯決策層人執行;status 為封閉枚舉)→ walk-forward OOS 評估 → 依**展示分級閉集**呈現:未過 GATE=判死留檔、**永不出 UI**;過 GATE 而經濟判死(econ_verdict∈{dead, thin_*})=**僅得研究級誠實展示**(econ_verdict 標籤與「非交易訊號」聲明硬綁,永不以可交易訊號姿態呈現);過 GATE 且經濟存活=完整展示。判準不得事後挪動(挪門柱唯依既有 trigger 紀律)。
> - **誠實揭露硬綁**(不得只出數字):①基線對照——hit-rate 基線一律為同窗**多數類樸素基線 max(p̄, 1−p̄)**、Brier 基線=p̄(1−p̄);②purged 校準器 provenance;③非重疊窗 n 與 HAC Eff-t(禁 iid 顯著性);④FREEZE 內數字一律明標「**歷史 walk-forward OOS,非 live**」——live 準確率唯解凍後依 unfreeze gate 紀律取得;⑤**禁單股準確率宣稱**(唯 horizon 級聚合:hit-rate/Brier/校準/分位桶)。
> - **逐日價格點位/路徑永久除外**:逐日(或任意粒度)之**價格點位、價格路徑、目標價**當預測輸出=**永久禁止**——不屬本軸可證偽實驗可豁免範圍、**無 GATE 可解**。路徑類需求唯得以蒙地卡羅**模擬情境**滿足,且輸出硬綁「**模擬非預測**」標示、模擬數字不入對話層數字白名單。
> - **三不動**:①三敵零容忍不動(#27 凌駕邊界:試的是方法與參數、不是資料真假);②FREEZE as-of `2026-05-31` 不動(訓練/OOS 全於凍結快照;快照組成變更唯依 freeze_manifest 版本化+決策層拍板);③相對機率軸(v1.40.0)之口徑、UI 與服務**不退化**(本軸=疊加層,既有 `prediction_probability`/B2 UI/前台檔位不拆不改)。
> - **guard 單向棘輪**:為本軸容納新數字唯得**擴 payload 白名單、新增加嚴閘**;放鬆或豁免既有閘=禁。
> - **雙留痕**:本軸立法係用戶三度堅持之決策層拍板;**AI 勸阻全文與用戶堅持決定並列留痕**(SSOT=`reports/augur_oracle_upgrade_master_plan_20260711.md` §0),勸阻不消音、決策不掩蓋(#8)。

### 1.3 條文二(句修):v1.40.0「相對機率誠實判準」之禁令句 GATE-scoped 化

現行句(實查 L125 逐字):

> **禁止輸出或暗示絕對漲跌機率**(「N 天會漲的機率」=假兆)。

修正為:

> **除預言機軸〔v1.42.0〕預註冊過 GATE 之輸出外,禁止輸出或暗示絕對漲跌機率**(未經 GATE 之「N 天會漲的機率」=假兆)。

(該條其餘全文——purge 校準、四項硬綁、方向契約、calibrator provenance——**一字不動**。)

### 1.4 條文三(句修):第一部「產物」列

現行列尾「機率=**橫斷面相對機率**口徑(詳第三部 validate『相對機率誠實判準』v1.40.0)」之後**增補**:

> ;絕對方向機率唯經預言機軸 GATE(詳第三部 validate「預言機誠實判準」v1.42.0)

### 1.5 條文四(連動):靈魂 v1.5.0 → v1.6.0 修正行

**「它預測什麼」節「任務」行**句尾增補:

> **預言機軸〔v1.6.0〕**:亦預測未來 H 日(日曆 30/60/120 天對映)之**絕對方向機率**(漲或跌的機率,附歷史 OOS 準確率),個股+top3/top5;及日粒度方向機率。**唯經預註冊可證偽實驗過 GATE 者才成為產品輸出**;未過即判死留檔——預言機的誠實不在「都答對」,在「說得出自己多常對」。

**「它不是」行**修正為:

> **它不是**:明牌產生器、保證獲利、**價格點位神算**。逐日**方向機率**屬 D 軌可證偽實驗;逐日**價格點位與路徑**永久不是本系統的預測產物(路徑唯以「模擬非預測」之蒙地卡羅情境呈現)。它是一個**有紀律的機率引擎**——答案永遠帶著「我多有把握」。

### 1.6 修訂歷程行(v1.42.0;依 v1.22.0 體例 3 行封頂,修訂 B3)

> | v1.42.0 | 2026-07-11 | **預言機軸立法**(用戶三度堅持拍板;AI 勸阻留痕並列,SSOT=oracle 主計畫 §0):第三部 validate 新增「預言機誠實判準」——H/D 兩軌唯 `direction_gate` 預註冊可證偽實驗過 GATE 才展示(展示分級閉集);五項誠實硬綁(多數類基線)、禁單股準確率、逐日點位/路徑永久除外、三不動、guard 單向棘輪。同步:靈魂 v1.6.0、第一部產物列、v1.40.0 禁令句 GATE-scoped、README、code/DB 註釋層。 | 草案·待親核 |

### 1.7 同步清單(一處改、全鏈對齊 #19)

靈魂檔名 v1.5.0→v1.6.0+內文兩節|憲章檔名 v1.41.0→v1.42.0+第一部/第三部/修訂歷程|原則精華交叉引用行(版本不動)|README 版本+連結|CLAUDE.md 引用措辭校閱(預期零或極少)|**code/DB 註釋層(修訂 B4)**:`migrate_probability_ddl.py:90` 表 COMMENT 文字改 GATE-scoped、冪等遷移對既有 DB `COMMENT ON` 更新、執行期全 repo grep「禁絕對」「相對機率」引用點清單。

(親核拍板點 P1-1~P1-6 見 §8。)

---

## §2 H 軌設計:市場分量 × 相對分量 → P(ret>0 | as-of, H)

### 2.1 任務定義與輸出契約

- **預測**:對 as-of(首發=`2026-05-31` FREEZE 日)之核心宇宙每股,輸出 P(未來 H 內絕對報酬>0),H=用戶語意 30/60/120 日曆天之交易日對映(§2.2);另輸出 top3/top5(依既有 rank 選出)等權組合層方向機率。
- **準確率**:FREEZE 內一律=**歷史 walk-forward OOS 準確率(明標非 live)**——§6.1 四件套。**禁單股準確率**(單股每 horizon 僅 1 個實現結果,無統計意義=假精度)。
- **live 準確率**:as-of `2026-05-31` 之預測其實現窗落在凍結快照外(實查 raw 價最深 2026-06-17)——**解凍後**鏡射 `prediction_unfreeze_gate` G3/G4 紀律評估;FREEZE 期間不追新資料、不出 live 數字。
- **服務前提**:全部輸出過 `direction_gate`(§2.6)+展示分級(§0.4)才進 UI;相對機率層不動。

### 2.2 horizon 對映裁決(修訂 B1;拍板點 P2-1)

**SSOT**=`calibrate_relative_probability.py:41` `CAL_DAYS={20:29, 40:58, 60:87, 82:119, 120:174}`(實查);前計畫 `reports/augur_omniscient_e2e_master_plan_20260710.md` 已裁 P30←H20/P60←H40/P120←H82(條件觸發)或 H120。本計畫遵同一對映,**不另立第二套**(#12):

| 用戶語意 | 錨 horizon | 日曆日近似 | 偏差 | 全鏈現況(實查) |
|---|---|---|---|---|
| 30 天 | **H20** | ≈29 | −3% | OOS/校準器/econ_verdict/judgestop 全鏈已有 |
| 60 天 | **H40** | ≈58 | −3% | 同上(草稿誤錨 H60≈87 日曆天,已改) |
| 120 天 | **H82(主錨,A 案)** | ≈119 | −1% | `econ_verdict_rule` 已有 H82 列(thin);`model_registry` **無 H82=須增訓**(RankRidge H82+Platt 校準+OOS 擴建,走既有工具參數化,§7.2) |
| (對照) | H120(B 案) | ≈174 | **+45%** | 全鏈已有,但日曆偏差大+非重疊 n=35 review 級 |

**AI 建議 A 案**(H82 主錨;增訓成本=1 個 horizon 之既有鏈重跑,非新方法;H120 保留為研究對照列)。B 案=H120 沿用+45% 偏差明標(零增訓)。**人拍板(P2-1)**。增 H21/H41 等新交易日數**不採**:全鏈重跑+封閉集分叉風險,檢定力無實質差(H21 非重疊 n=203 vs H20 之 213)。

### 2.3 架構:絕對報酬分解與合成層

個股 H 內絕對報酬 ≈ 市場分量+相對(橫斷面)分量:

1. **市場分量(新)**:市場方向模型(族候選見 §5.1)以 §4 市場特徵訓練,walk-forward 輸出 P_mkt(大盤 H 內>0 | as-of),落 `market_direction_probability`。首個 `features/macro_vintage.py` PIT reader 真消費者。
2. **相對分量(沿用不重造)**:既有 RankRidge `rank_pctile`(+Platt 校準全套)。
3. **合成層 `DirStack`**:logistic 疊加——輸入=(logit(P_mkt), rank_pctile, 交互項),標籤=1[fwd_ret>0]。**關鍵既有資產**:`probability_oos_sample` 已含 `fwd_ret`(絕對前視報酬)欄、41,860 列、25 panels(H120 24)——合成層之訓練/評估樣本**現成**,零重跑相對層。逐折 fit 僅用「標籤窗已完全實現」之折(同 Platt purge 紀律);輸出 p_up 落 `direction_probability`。

### 2.4 檢定力與 base-rate(實查,#9)

| H(td) | 非重疊窗 n(時間向) | TAIEX up-rate(重疊窗) | 個股 OOS up-rate | 判讀 |
|---|---|---|---|---|
| 20 | 213 | 0.6448 | 0.4856(25 panels)——**多數類=猜跌 0.5144** | 可檢定 |
| 40 | 106 | 0.6909 | 0.5484(25 panels) | 邊際 |
| 82 | 52 | **0.7396** | —(無既有 OOS;P2-1=A 增訓時實算落表,不編數) | 邊際偏弱、明標 |
| 120 | **35** | 0.7714 | 0.5821(**24 panels/10,211 列**) | **review 級寫死** |

個股橫斷面樣本寬(每 horizon ~10.5k 列)但同 panel 高相關——序列檢定力以 panel 數(25/24)與非重疊窗數為口徑下界,HAC 校正(§5.2)。「猜漲」在大盤 H120 已 77% 命中:**任何不贏多數類基線的準確率數字=假兆**。

### 2.5 top3/top5 組合層(修訂 X3)

組合標籤=等權組合 H 內實現報酬>0;**每 panel 僅 1 個組合觀測 → n≤25/horizon,小樣本明標**、單獨列 n、隨個股層 GATE 但不得單獨解鎖;呈現硬綁「組合口徑非個股平均」。

### 2.6 direction_gate(預註冊;修訂 C4)

鏡射 `prediction_unfreeze_gate` 13 欄(實查)+`track`/`horizon` 欄;**status 封閉枚舉自帶 CHECK**(不繼承 unfreeze_gate 現值字彙 {frozen,superseded}):

```sql
CREATE TABLE IF NOT EXISTS direction_gate (
  gate_id          text PRIMARY KEY,
  track            text NOT NULL CHECK (track IN ('H','D')),
  horizon          integer NOT NULL,          -- H 軌=20/40/82/120(td);D 軌=k(1/5)
  purpose          text NOT NULL,
  criteria         jsonb NOT NULL,            -- 預註冊判準全文(先寫死;挪動唯 trigger 紀律)
  criteria_sha     text NOT NULL,
  status           text NOT NULL DEFAULT 'preregistered' CHECK (status IN
    ('preregistered','approved','evaluated_pass','evaluated_fail','superseded')),
  preregistered_at timestamptz NOT NULL DEFAULT now(),
  approved_by      text, approved_at timestamptz,       -- approve 唯決策層人(#26)
  evaluated_at     timestamptz, result_snapshot jsonb, evaluation_ref text,
  git_sha          text NOT NULL, note text
);
```

判準數值(criteria jsonb)於 §7 Phase 2 預註冊時**二次親核**;ECE 門檻引 judgestop `calib_late_ece_ceiling`(DB 讀值,#12 不寫死)。

---

## §3 D 軌設計:逐日粒度方向機率+蒙地卡羅模擬情境

### 3.0 定位與誠實預期(勸阻迴聲,承 §0)

D 軌是本計畫**預期經濟終關幾乎必死**的一軌。本節把「死」寫成可證偽的預註冊命題:

- **統計上可驗**:日頻樣本量巨大(§3.2)——這正是 D 軌唯一誠實的科學價值:**若日頻無 edge,D 軌能以極高檢定力證明它無 edge**。
- **經濟上近死**(實查根據):來回成本 0.585%;TAIEX 日絕對報酬中位數 0.553%(n=4,270)——**單次來回成本已大於 TAIEX 中位數日振幅**。個股(core_universe 344 檔)2019-2026 日絕對報酬中位數 0.794%:對稱振幅簡化下,k=1 全換手損益兩平 hit-rate ≈ (1+0.585/0.794)/2 ≈ **86.8%**(設計級試算);k=5 攤提(√5 尺度)≈ **66.5%**(修訂 D1)——仍屬近死。
- **既有裁決佐證**:H20=`dead`(DB 實查);日頻比 H20 更短、換手更兇,經濟裁決只會更糟。
- **永久除外**:逐日價格點位/路徑「當預測」永久除外(§1.2);路徑需求唯 §3.8 蒙地卡羅,硬綁「模擬非預測」。

交付物=**「日頻方向機率+極高檢定力的誠實裁決」**,不是「可交易的日頻策略」。econ_verdict 預期 `dead`,依 §0.4 展示分級處置。

### 3.1 可驗形式與標籤定義

| 項 | 定義 |
|---|---|
| 目標 | `P(up)`=P(方向為正)——**方向機率,非點位** |
| 標的 | ①core_universe 個股(344 檔);②大盤 TAIEX/TPEx(`TaiwanStockTotalReturnIndex`,TAIEX 5,774 列/TPEx 5,028 列,2003-01-02 起,實查) |
| k(封閉集) | k∈{1,5} 交易日;**不開放任意 k** |
| 主標籤 | `y=1[close_adj(t+k)/close_adj(t)−1>0]`;個股用 `TaiwanStockPriceAdj`(11,055,094 列/3,101 檔/1994-09-14 起,實查),指數用 TRI price |
| 決策點 | t 收盤後;**執行缺口誠實化**:輔口徑 `open(t+1)→close(t+k)` 一併出報告,兩口徑差=隔夜漂移,不隱藏 |
| 平盤處置 | ret==0 判 y=0(保守);比例入報告 |

### 3.2 檢定力(實查 n;修訂 A1/A2)

指數日觀測:交易日 4,271、日報酬 n=4,270;個股 stock-days(2008-12-31~2026-05-31,344 檔×PriceAdj)=**1,462,473**。D 軌與 H120(非重疊窗 **n=35**)正相反:**檢定力不是瓶頸,經濟性才是**。統計紀律:**禁裸 iid n**——同日橫斷面高相關,有效獨立樣本以「日」計(4,271)為口徑下界,一切檢定 date-cluster(承 #11;k=5 重疊窗 HAC,沿 `effective_t_hac`)。基準率(實查):TAIEX 日 P(up)=0.5550(多數類=猜漲);個股 2019-2026 P(up)=0.4657(**多數類=猜跌 0.5343**)。

### 3.3 特徵層(全在庫、零新源;#8 可見性)

| 特徵群 | 來源表(§4.2) | #8 可見規則(v1 保守值) |
|---|---|---|
| 價量動能/波動 | `TaiwanStockPriceAdj`、`TaiwanFuturesDaily`、TRI | t 收盤即定,lag 0 |
| 籌碼(現貨整體) | `TaiwanStockTotalInstitutionalInvestors`(2004-04 起)、`TaiwanStockTotalMarginPurchaseShortSale`(2001-01 起)、`TaiwanTotalExchangeMarginMaintenance`(2001-01 起) | 盤後公布→**lag 1 td**(公布時刻考據=執行期 catalog 工作項) |
| 期權籌碼 | `Taiwan{Futures,Option}InstitutionalInvestors`(**2018-06-05 起**)、`Taiwan{Futures,Option}OpenInterestLargeTraders`(2007-01 起) | lag 1 td;2018 前 NULL(晚生特徵誠實 NULL,不補 0) |
| 情緒/波動 | `CnnFearGreedIndex`(2011-01 起,美國曆)、`fred_series` VIXCLS(9,522 列,全列具 `realtime_start`,實查) | CNN FG:台北次一交易日 lag 1;VIXCLS:**PIT 直讀 realtime_start**(macro_vintage 前例) |
| 台指隱含波動 | `market_iv_daily`(§4.4 本地推導,零新源) | 同源 OptionDaily,t 收盤 lag 0 |

排除(誠實理由):`trading_session='after_market'` 夜盤(跨日歸屬未實證);2021 年後才有之 Dealer volume/AfterHours 表與僅約兩個月史之 `TaiwanFuturesSpreadTick`(實查 2026-05-01 起)不入 v1。

### 3.4 模型族與訓練(硬體界內)

族候選=`DailyLogit`(基準)、`DailyGBDT`(LightGBM/XGBoost CPU;1.46M 列×~30 特徵 CPU 可訓,訓練時間實測入報告;**禁不可行深度模型幻想**)。多 seed ≥3(#11)、入 `model_registry`(11 欄實查,horizon 欄放 k);機率校準鏡射 `probability_calibrator` 口徑(platt+purge,實查 method=platt/purge_verified=true)。

### 3.5 日頻 walk-forward embargo 口徑

沿用 `evaluation/walkforward.py` **保證下界**口徑(實查:`splits(..., calendar=)` 以真實交易日曆逐折實算 `guaranteed=True`;無日曆退路僅開發用):embargo=`k+feature_lag_td` 交易日。panel=交易日;折切分以「年」為 test 塊(≈17 折)、折內逐日出 OOS 機率;與 H 軌**同一 splits 產生器、同一日曆**(#12)。

### 3.6 準確率呈現(承 §6.1,加嚴)

k 級彙總、禁單股準確率;四件套成對出(hit-rate vs **多數類基線**〔個股=猜跌 0.5343、指數=猜漲 0.5550,隨窗實算〕、Brier vs p̄(1−p̄)、可靠度分箱、分位桶單調);date-cluster 檢定、k=5 HAC;全部明標「FREEZE 內歷史 walk-forward OOS,非 live」。

### 3.7 成本敏感經濟終關+敗退路徑(修訂 C2:唯一定義=§0.4 展示分級)

工具:沿用 `run_economic_eval.py`+`evaluation/portfolio.py`(cost=0.00585 來回、換手實算)——**不為 D 軌另立寬鬆第二套**。策略形:p_up 頂桶 long-only(k=1 日調倉/k=5 週調倉),淨 Sharpe/Calmar/MaxDD vs 基準,毛/淨對照必列。econ verdict 依 `econ_verdict_rule` 口徑落表;**預期 `dead`**。敗退處置=§0.4 展示分級閉集(統計亦不過→全下架只留審計資料;統計過經濟死→研究級指標頁掛 dead 標籤;意外存活→仍須 GATE+完整誠實標記)。

### 3.8 蒙地卡羅模擬情境頁(修訂 C3/D2;「模擬非預測」硬綁)

滿足「逐日路徑」需求的**唯一合憲形式**:

- **方法(v1)**:對 target 之 as-of(≤FREEZE)歷史日報酬做 iid bootstrap+block bootstrap(區塊 21td,雙法並列),n_paths=10,000,horizon∈{21,42,63,126} td;**不以任何模型預測 tilt 抽樣**(純歷史重抽,杜絕「模擬夾帶預測」);seed 顯式入庫可重現。
- **輸出**:分位錐(5/25/50/75/95 百分位×逐 h)、終值分布、模擬統計 P(終值>0)——明標「歷史重抽之模擬統計,非模型預測」,與 D/H 軌 p_up 分欄呈現、永不混排。
- **硬綁四鎖**:①頁面固定標題/浮水印「蒙地卡羅模擬情境(模擬非預測)」,文案常數進 code;②**模擬數字根本不入 chat payload**(僅 UI 頁;chat 對模擬問題回固定句+頁面指引;LLM 覆述模擬數字=不在白名單=閘②/⑥攔=正確行為)——刪除草稿「模擬 frame 白名單」語(guard 無 frame 機制,修訂 C3);③DB 只存規格+摘要(`mc_simulation_run.summary` jsonb),不落逐路徑為預測資料;④憲章條文明文(§1.2)。表名統一 `mc_simulation_run`(修訂 D2)。

---

## §4 資料增補軌(用戶③):先盤點既有、實證缺口才增補

### 4.1 原則

新資料一律:(a)歷史截至 FREEZE as-of(不追新、as-of 不動);(b)FinMind/FRED 走 #24 三層防護+用戶拍板放量;(c)走完整 catalog/reconcile/schema profile 紀律;(d)#8 發布時點欄先定義(macro_vintage/release_lag 前例)。**v1 起步零新外部源**——下表證明市場方向所需已在庫。

### 4.2 既有市場方向資料盤點(19 表全實查,2026-07-11)

| 表 | 列數 | 起日 | 用途 |
|---|---|---|---|
| TaiwanStockTotalReturnIndex | 10,802(TAIEX 5,774/TPEx 5,028) | 2003-01-02 | 大盤含息標籤+特徵 |
| TaiwanFuturesDaily | 5,782,918 | 1998-08-03 | 期貨價量/基差 |
| TaiwanFuturesInstitutionalInvestors | 110,349 | 2018-06-05 | 期貨法人(晚生) |
| TaiwanFuturesOpenInterestLargeTraders | 1,893,125 | 2007-01-02 | 大額未平倉 |
| TaiwanFuturesSpreadTrading | 15,414 | 2007-11-02 | 價差 |
| TaiwanFuturesFinalSettlementPrice | 2,788 | 2016-01-08 | 結算 |
| TaiwanFuturesDealerTradingVolumeDaily | 5,415,158 | 2021-04-01 | (v1 排除:史短) |
| TaiwanFuturesInstitutionalInvestorsAfterHours | 41,652 | 2021-10-12 | (v1 排除) |
| TaiwanFuturesSpreadTick | 757,104 | **2026-05-01** | (v1 排除:僅約 1 個月史) |
| TaiwanOptionDaily | 33,734,019 | 2002-01-02 | **IV 推導源** |
| TaiwanOptionInstitutionalInvestors | 60,582 | 2018-06-05 | 選擇權法人(晚生) |
| TaiwanOptionOpenInterestLargeTraders | 951,880 | 2007-01-02 | 大額未平倉 |
| TaiwanOptionFinalSettlementPrice | 1,704 | 2002-01-17 | 結算 |
| TaiwanOptionDealerTradingVolumeDaily | 1,335,652 | 2021-04-01 | (v1 排除) |
| TaiwanOptionInstitutionalInvestorsAfterHours | 6,822 | 2021-10-12 | (v1 排除) |
| CnnFearGreedIndex | 3,922 | 2011-01-03 | 情緒(美國曆,lag 1 台北 td) |
| TaiwanStockTotalInstitutionalInvestors | 26,625 | 2004-04-07 | 現貨整體法人 |
| TaiwanStockTotalMarginPurchaseShortSale | 18,726 | 2001-01-03 | 整體信用 |
| TaiwanTotalExchangeMarginMaintenance | 6,235 | 2001-01-05 | 整體維持率 |

另:國際指數已在庫(實查 `USStockPrice` 35.05M 列/1928 起、`JapanStockPrice` 16.8M、`EuropeStockPrice` 4.17M、`UKStockPrice`);FRED 31 series/343,848 列(VIXCLS 9,522 列全具 realtime_start)。

### 4.3 catalog/#8 紀律

每個入模市場特徵先在 `market_direction_feature.visible_date` 定義可見日(期貨/選擇權法人=T+1 盤後、CNN FG=台北 T+1、FRED=realtime_start PIT 直讀);消費端一律 `visible_date <= panel_date`。公布時刻逐表考據入 catalog=執行期 Phase 1 工作項。

### 4.4 本地推導:`market_iv_daily`(零新源)

自 `TaiwanOptionDaily`(33.7M 列)以近月平價合約反推台指隱含波動(本土 VIX 替身)——純本地計算、零 API、零 usage(#28)。推導規格(近月選擇/平價界定/無風險利率取值)於 Phase 1 落 `scripts/derive_market_iv.py` docstring+catalog。

### 4.5 候選缺口與 FREEZE 詮釋(修訂 E1;拍板點 P4-1)

- **實證現況**:市場方向 v1 特徵全部可由在庫 19 表+本地推導取得——**無已實證之缺口**;「真缺口」唯執行期特徵評估(§5.3 漏斗)證明既有源不足時才成立。
- **FREEZE 詮釋爭點(不偷渡,明文列拍板)**:原則精華 FREEZE 判準=「凍結快照為唯一資料據…不追新資料」。新增歷史來源(即使 date≤as-of)**改變快照組成**、破壞「dump=快照可複現」。「期限凍結 ≠ 來源集凍結」屬**判準詮釋=決策層專屬**:
  - **A 案**:允許補「歷史截至 as-of」之新源,但須①逐源用戶拍板放量;②`freeze_manifest` 記 snapshot_version 遞增+來源+列數+核准;③重出 dump+HANDOFF 註記。
  - **B 案**:凍結期一律不增源,增補延後至解凍。
  - **AI 建議**:v1 零新源故不觸此題;**唯實證缺口成立才觸 P4-1 裁決**,屆時再拍。`freeze_manifest` DDL 先建(空表零成本,§7.1)。

---

## §5 模型增補/創造軌(用戶③):challenger 方法論

### 5.0 定位與鐵律

新模型(市場分量、D 軌、未來任何「創造的新模型」)一律是 **challenger**:進既有 `model_registry`、走既有折口徑、過既有提拔關卡與經濟終關、**贏了現任才換**。零新判準、零第二套 registry、零第二套漏斗。三敵零容忍不因換目標(相對→絕對)而動一字。

### 5.1 族候選(誠實列界,禁幻想)

**H 軌市場分量**:

| family | 本體 | 理由 |
|---|---|---|
| `MktLogit` | sklearn LogisticRegression(L2) | 基線;n=4,271 日×少量特徵,線性最不易過擬合 |
| `MktGBDT` | sklearn GradientBoosting/HistGB | 非線性交互(法人×IV×margin);淺樹+早停 |
| `MktRegime` | 2-state 高斯狀態轉換(自寫 EM ~百行;引 `hmmlearn` 須拍板) | regime 思想可證偽化;輸出 P(bull regime) |

**D 軌**:`DailyLogit`、`DailyGBDT`(§3.4)。**相對分量**:現任 RankRidge(實查 registry 唯一 family,H20/40/60/120)不動直接引用;`RankGBDT` 已有 code(`ranker.py:41`)可作相對層 challenger,非本計畫必要路徑。**H82 增訓(P2-1=A 案)**:同 family RankRidge、走既有 train/calibrate/OOS 工具參數化 horizon=82,非新模型。

**硬體誠實界**:本機 GTX1650 4GB/CPU。上表全族 CPU sklearn 可訓(市場級秒級;日頻面板百萬列級 HistGB 分鐘級)。**LSTM/Transformer 本輪明文不做**——非裝不下,而因 (i)市場級 n=4,271 對深度模型無檢定力;(ii)無任何 OOS 真兆支持其在本資料上勝過上表族;(iii)違「先簡後繁、challenger 須贏現任」。未來若做=新 family 走同一軌+預註冊,不豁免。

### 5.2 訓練/評估口徑鎖(#12 零雙軌)

折口徑唯一=`walkforward.py:splits`+`embargo_panels_for`(calendar 保證下界);個股面板複用 `baseline._asof_stocks/_panel_matrix`、標籤複用 `evaluation/label.py`(`build_probability_oos_sample.py` 前例)。多 seed ≥3(#11),Logit 無隨機性 seed 記 0。顯著性禁裸 iid=`metrics.py:89 effective_t_hac`(Bartlett)套於逐窗 (hit−base) 序列,或以非重疊窗計數為誠實上限。as-of/#8=§4.3。

### 5.3 提拔=既有三審/四道漏斗+經濟終關(不另立)

特徵候選走方法論 §四第 4 道提拔關卡原軌(SSOT=`reports/augur_feature_discovery_methodology_20260626.md`,只引不複述);模型 family 提拔走既有 B 提拔三審+經濟終關(`run_economic_eval.py`/`portfolio.py`,COST_TW=0.00585 兩處實查同值)。方向模型經濟終關口徑:p_up 過閾持有 long-only vs 買進持有,同扣成本——「Brier 贏基線」≠可交易。judgestop 引用不複製:斷言引 `judgestop_threshold` 現值(實查 **11 列**,修訂 X1;hac_t_floor=2.0/calib_late_ece_ceiling=0.05/dsr_annotate=0.95 皆 frozen),程式讀 DB 不寫死(#12)。

### 5.4 registry+artifact 口徑鎖

一律 `registry.py:register(model_id, family, horizon, train_span, asof_snapshot, feats_hash, seed, ...)`(表 11 欄零 DDL 變更;horizon:市場分量=20/40/82/120、D 軌=k);載回 `registry.latest(family, horizon, asof_snapshot)`(≤as-of,#8)。`artifact.feats_hash` 口徑鎖:serve 時特徵集與 artifact 不符即拒。**challenger→champion 換任**:同折同 seeds 同成本同 OOS 表對決;贏=經濟終關淨值優於現任**且** judgestop 斷言不觸**且**人拍板;舊列永不刪(#10)。

---

## §6 準確率定義+呈現服務(雙態)+guard 設計

### 6.1 準確率唯一合法定義(horizon 級;禁單股)

**定義閉集**(任何「準確率」宣稱只准以下四項,其他即假兆):

1. **hit-rate vs 多數類樸素基線 max(p̄,1−p̄)**(修訂 B2),skill=hit−base 為主指標。base-rate 實查(2026-07-11,#9b;修訂 A3/A4/B1):

| 口徑 | 來源 | up-rate(p̄) | 多數類基線 |
|---|---|---|---|
| 大盤日頻(次日) | TRI TAIEX,交易日 4,271、日報酬 **n=4,270** | 0.5550 | 猜漲 0.5550 |
| 大盤 H20/H40/H82/H120(重疊窗) | 同上 | 0.6448/0.6909/**0.7396**/0.7714 | 猜漲同值 |
| 個股 H20 | `probability_oos_sample` 10,552 列/25 panels | 0.4856 | **猜跌 0.5144** |
| 個股 H40/H60 | 10,548/10,549 列,各 25 panels | 0.5484/0.5606 | 猜漲同值 |
| 個股 H82 | —(P2-1=A 增訓時實算,不編數) | — | — |
| 個股 H120 | 10,211 列/**24 panels** | 0.5821 | 猜漲同值 |
| 個股日頻(2019-2026) | PriceAdj×core_universe,n=617,466 | 0.4657 | **猜跌 0.5343** |

2. **Brier+Brier skill**(基線=p̄(1−p̄);鏡射 calibrator brier/brier_baseline 欄)。
3. **校準品質**:ECE 10-bin+可靠度分箱(ceiling 引 judgestop 0.05,DB 讀值)。
4. **分位桶單調性**:p_up 十分位 vs 實現上漲頻率。

**禁**:單股準確率、混 horizon 平均、未標基線之裸命中率、FREEZE 內數字宣稱為 live。

### 6.2 檢定力現實

見 §2.4 表(H20 213/H40 106/H82 52/H120 **35**=review 級寫死/k=1 4,270/k=5 854)。

### 6.3 雙態呈現(GATE 前零絕對數字——機制保證非自律)

- **態一(GATE 前,預設)**:全系統(UI+chat+advisor)零絕對方向數字。機制三層:(i)`direction_probability.gate_id` 外鍵硬綁 `direction_gate`,serve 端 SELECT 一律 JOIN `status='evaluated_pass'`(封閉枚舉,修訂 C4),非 pass 查無列;(ii)UI 絕對頁=誠實封鎖頁(顯 gate 判準+status,零數字);(iii)advisor payload `directions` 欄 builder fail-closed:gate 非 pass→恆空 tuple→絕對機率數字不在白名單→閘②/⑥攔(§6.5)。
- **態二(GATE pass 後)**:依 §0.4 展示分級解鎖,每值硬綁誠實標記;僅該軌該 horizon。

### 6.4 頁面設計(疊加不拆;治權④)

既有 `serve_probability_ui.py`(127.0.0.1:8600,四模型卡+誠實標記同 DOM 硬綁)**一行不退化**,新增 route 疊加:

| 頁 | 內容 | 誠實標記(同 DOM 硬綁,B2 模式) |
|---|---|---|
| `/direction/<stock>` | 30/60/120 天三卡(H20/H40/H82;H120 研究對照列,修訂 B1):p_up+多數類基線並列+市場×相對分解 | ①口徑 ②基線並列 ③歷史 OOS 非 live ④H120 review/H82 n=52 明標 ⑤econ_verdict |
| `/direction/top` | top3/top5 組合卡 | 同上+「組合口徑非個股平均」+小樣本 n |
| `/daily/<stock>` | D 軌 k=1/5 方向機率(gate 獨立;GATE 前=封鎖頁) | 同上+econ_verdict(預期 dead)同列 |
| `/simulate/<stock>` | 蒙地卡羅分位錐(p5/25/50/75/95) | 每 DOM 節點浮水印「模擬非預測」;params/seed 全揭露(`mc_simulation_run`,修訂 D2);與 `/direction` 零共用視覺元素 |

相對機率四卡、F1 前台檔位、B2 route 全不動;chat 端經 payload 擴欄,`advise()` 唯一出口不變。

### 6.5 guard 設計(修訂 C1/C3/F1;治權⑤:**擴白名單+加嚴閘=合憲,鬆既有閘=禁**)

**實查現況**:閘② suspects=`-?\d+\.\d{2,}`(≥2 位小數)∪`_METRIC_NUM`(僅 IC/Sharpe/score/分數鄰接,不論位數)——**整數/1 位小數之絕對機率(「上漲機率 60%」「約 0.6」)不在既有攔截面**;閘③ `_FUTURE_LEAK` 含 `明(日|天).{0,6}(漲|跌)`/`下週.{0,6}(漲|跌)`/`未來.{0,4}(會漲|會跌|必)`。草稿「不改 guard 一字」與機制現實互斥,**撤該自訂鐵律**,設計如下:

1. **payload 擴欄(fail-closed)**:`PredictionPayload` 加 `directions: tuple=()`((target, horizon, p_up, base_rate, econ_verdict, calendar_days),builder 於 gate 非 evaluated_pass 恆 ())與 `direction_note: str=""`(固定誠實標記,確定性渲染、與數字不可分離)。`numbers()` 增列 p_up/base_rate(4dp)/calendar_days——base_rate 必入白名單,否則誠實標記自身被閘②誤攔。
2. **新增閘⑥ `_PROB_NUM`(加嚴,既有五閘一字不動)**:機率詞(機率/probability/chance/勝率/把握)鄰接數字**不論位數**、及 `N%`/`N 成` 形——**正規化**(%÷100、成÷10)後 4dp 查白名單;GATE 前 directions 恆空→此類數字必不在白名單→攔。對齊 `_METRIC_NUM` 前例(閘⑥只可能多攔不少攔=單向加嚴)。
3. **誠實殘餘揭露(#15,不佯稱滴水不漏)**:中文數字形(「約六成」)非機械可攔——主防線=**GATE 前 LLM 上下文根本無絕對機率資料可覆述**(fail-closed payload,幻覺面與本計畫前相同、非新增攻擊面)+閘⑥攔阿拉伯數字形+紅隊示例集(含「六成」變體)入驗收(§7.4)+上線後抽樣審計。
4. **D 軌合法措辭模板(修訂 F1)**:過 GATE 後之輸出以**確定性模板常數**渲染,避開閘③ token——如「次一交易日方向為正之機率 p=0.55(同窗多數類基線 0.556;歷史 walk-forward OOS,非 live)」「後 5 個交易日方向為正之機率 p=…」;H 軌:「20 交易日(≈29 日曆日)內絕對報酬>0 之機率=0.61(同窗多數類基線 0.64)」。**模板句須通過 guard 單元測試**;LLM 若改寫成「明天會漲」「保證」→閘③攔=正確 fail-closed 行為(明文,非 bug)。
5. **模擬零入 chat**(修訂 C3):`mc_simulation_run` 數字不入任何 payload;chat 對模擬僅回固定句+`/simulate` 頁指引。
6. **明文禁止**:任何「為了讓絕對數字通過而放鬆/豁免既有閘①-⑤」=鬆 guard,禁;入憲(§1.2 guard 單向棘輪)。

---

## §7 表與程式雙落實(#20 v1.39.0)+分階段+驗收

### 7.1 新表 DDL(單一住所=`scripts/migrate_direction_ddl.py`,全部冪等)

共 10 張:`direction_gate`(§2.6 已列,H/D 共用、track 欄分軌)+H 軌 4 張+D 軌 3 張+`mc_simulation_run`+`freeze_manifest`。

```sql
-- H① 市場方向特徵(#8 visible_date 先定義;來源=在庫 19 表+本地推導,零新外部源)
CREATE TABLE IF NOT EXISTS market_direction_feature (
  panel_date date NOT NULL, feature text NOT NULL,
  value double precision NOT NULL,
  source_table text NOT NULL,              -- 溯源 raw 表(#10)
  visible_date date NOT NULL,              -- 決策者可見日(#8)
  git_sha text NOT NULL, created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (panel_date, feature));

-- H② 市場分量機率(大盤)
CREATE TABLE IF NOT EXISTS market_direction_probability (
  panel_date date NOT NULL, model_id text NOT NULL REFERENCES model_registry(model_id),
  horizon integer NOT NULL, p_mkt_up double precision NOT NULL CHECK (p_mkt_up BETWEEN 0 AND 1),
  calibrator_id text, git_sha text NOT NULL, created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (panel_date, model_id, horizon));

-- H③ 個股/組合絕對方向機率(gate_id 硬綁=態一機制,§6.3)
CREATE TABLE IF NOT EXISTS direction_probability (
  panel_date date NOT NULL, model_id text NOT NULL REFERENCES model_registry(model_id),
  target_id text NOT NULL,                 -- stock_id | 'TOP3' | 'TOP5'
  horizon integer NOT NULL, p_up double precision NOT NULL CHECK (p_up BETWEEN 0 AND 1),
  base_rate double precision NOT NULL,     -- 同窗多數類基線(硬綁呈現,#15)
  calendar_days integer NOT NULL,          -- CAL_DAYS 對映(A-27 前例)
  calibrator_id text, econ_verdict text NOT NULL,
  gate_id text NOT NULL REFERENCES direction_gate(gate_id),
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (panel_date, model_id, target_id, horizon));

-- H④ OOS 審計樣本(鏡射 probability_oos_sample 口徑)
CREATE TABLE IF NOT EXISTS direction_oos_sample (
  model_id text NOT NULL, target_id text NOT NULL, panel_date date NOT NULL,
  horizon integer NOT NULL, p_up double precision NOT NULL,
  y_up smallint NOT NULL CHECK (y_up IN (0,1)), fwd_abs_ret double precision,
  fold_id integer NOT NULL, seed integer NOT NULL,
  git_sha text NOT NULL, created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (model_id, target_id, panel_date, horizon, seed));

-- D① 日頻特徵面板(與月頻 feature_values 分表不混口徑;晚生特徵誠實 NULL 不補 0)
CREATE TABLE IF NOT EXISTS daily_direction_feature_values (
  panel_date date NOT NULL, target_id text NOT NULL, feature text NOT NULL,
  value double precision, PRIMARY KEY (panel_date, target_id, feature));

-- D② 日頻方向機率(gate_id 硬綁同 H③)
CREATE TABLE IF NOT EXISTS daily_direction_probability (
  panel_date date NOT NULL, model_id text NOT NULL REFERENCES model_registry(model_id),
  target_id text NOT NULL, k_td integer NOT NULL CHECK (k_td IN (1,5)),
  p_up double precision NOT NULL CHECK (p_up BETWEEN 0 AND 1),
  base_rate double precision NOT NULL, calibrator_id text,
  econ_verdict text NOT NULL,              -- 預期 'dead',硬綁呈現
  gate_id text NOT NULL REFERENCES direction_gate(gate_id),
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (panel_date, model_id, target_id, k_td));

-- D③ 日頻 OOS 審計樣本
CREATE TABLE IF NOT EXISTS daily_direction_oos_sample (
  model_id text NOT NULL, target_id text NOT NULL, panel_date date NOT NULL,
  k_td integer NOT NULL, p_up double precision NOT NULL,
  y_up smallint NOT NULL CHECK (y_up IN (0,1)),
  fold_id integer NOT NULL, seed integer NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (model_id, target_id, panel_date, k_td, seed));

-- 蒙地卡羅 run(規格+摘要;絕不存逐路徑為預測;修訂 C3/D2)
CREATE TABLE IF NOT EXISTS mc_simulation_run (
  run_id text PRIMARY KEY, target_id text NOT NULL, asof_date date NOT NULL,
  horizon_td integer NOT NULL,
  method text NOT NULL CHECK (method IN ('iid_bootstrap','block_bootstrap')),
  block_len_td integer, n_paths integer NOT NULL, seed integer NOT NULL,
  summary jsonb NOT NULL,                  -- 分位錐/終值分布摘要
  is_simulation boolean NOT NULL DEFAULT true CHECK (is_simulation),  -- 「模擬非預測」DB 級硬綁
  git_sha text NOT NULL, created_at timestamptz NOT NULL DEFAULT now());

-- 快照版本化(修訂 E1;P4-1 觸發前為空表)
CREATE TABLE IF NOT EXISTS freeze_manifest (
  snapshot_version integer PRIMARY KEY,
  asof_freeze date NOT NULL DEFAULT '2026-05-31',
  change_desc text NOT NULL, approved_by text NOT NULL,
  row_delta bigint, dump_ref text, created_at timestamptz NOT NULL DEFAULT now());
```

另:冪等更新 `prediction_probability` 既有 COMMENT 為 GATE-scoped 措辭(修訂 B4;修憲親核後才跑)。

### 7.2 程式規畫(#20:全部 scripts 走 `_bootstrap`/指令矩陣/#29 四件事)

| 程式 | 職責 | 輸入 → 輸出 |
|---|---|---|
| `scripts/migrate_direction_ddl.py` | 10 表冪等 DDL+COMMENT 更新(B4) | — → 全部新表 |
| `scripts/derive_market_iv.py` | OptionDaily→近月平價 IV(本地零 API) | TaiwanOptionDaily → market_iv_daily |
| `scripts/build_market_direction_features.py` | 市場特徵(visible_date #8 逐欄) | 19 表+market_iv_daily → market_direction_feature |
| `scripts/train_market_direction.py` | MktLogit/MktGBDT/MktRegime walk-forward 多 seed | market_direction_feature+TRI → model_registry+market_direction_probability+市場級 OOS |
| (既有工具參數化) | **H82 增訓**(P2-1=A):train_ranker/build_probability_oos_sample/calibrate_relative_probability 以 horizon=82 重跑 | 既有鏈 → registry/OOS/calibrator H82 列 |
| `scripts/train_direction_stack.py` | 合成層 DirStack+purged 校準 | market_direction_probability+probability_oos_sample(rank_pctile/fwd_ret) → direction_probability+direction_oos_sample |
| `scripts/build_daily_direction_features.py` | 日頻特徵面板 | PriceAdj+籌碼表 → daily_direction_feature_values |
| `scripts/train_daily_direction.py` | DailyLogit/DailyGBDT 年折 walk-forward | 日頻面板 → registry+daily_direction_probability+daily_direction_oos_sample |
| `scripts/run_direction_econ_eval.py` | 方向機率→過閾持有 vs buy&hold(複用 `evaluation/portfolio.py`,cost 同口徑) | OOS 表 → 報告+econ_verdict 落表 |
| `scripts/preregister_direction_gate.py` | 判準 jsonb+sha 預註冊(跑數字前) | 判準常數 → direction_gate |
| `scripts/evaluate_direction_gate.py` | 四件套 vs criteria→verdict | OOS 表 → direction_gate(status/result_snapshot) |
| `scripts/simulate_mc_paths.py` | bootstrap 模擬(seed 顯式) | PriceAdj/TRI → mc_simulation_run |
| `serve_probability_ui.py`(改) | 4 新 route 疊加(封鎖頁→分級解鎖);既有一行不退化 | 上述表 → UI |
| `advisor/payload.py`(改) | directions/direction_note fail-closed 欄+numbers() 擴 | direction_probability(JOIN gate) → payload |
| `advisor/guard.py`(改) | **新增閘⑥**(加嚴;①-⑤ 一字不動) | — |

### 7.3 分階段

| 階段 | 內容 | 前置 |
|---|---|---|
| **P0 修憲親核** | §1 條文+§8 拍板點逐項裁決;AI 才改 docs/(含 B4 註釋同步) | 用戶 |
| **P1 資料層** | DDL+market_iv 推導+市場特徵(visible_date 逐欄)+日頻面板;全本地零 usage(#28) | P0 |
| **P2 H 軌實驗** | (條件:H82 增訓)→gate 預註冊(判準二次親核)→市場分量+合成層訓練+OOS→gate 評估 | P1 |
| **P3 呈現層** | UI route(先封鎖頁)+payload fail-closed+閘⑥+紅隊測試;相對層迴歸驗證(治權④) | P2 可並行起 |
| **P4 D 軌實驗** | 日頻模型+OOS+統計關→經濟終關(預期 dead)→gate 評估→分級處置 | P1 |
| **P5 模擬頁** | simulate_mc_paths+/simulate 頁(四鎖) | P1 |
| **P6 結案** | 結果報告(reports/)+驗收清單+HANDOFF 更新 | P2-P5 |

#26 有界自主:P1/P2/P4/P5 屬本地可逆開發,授權後 AI 自驅推進、逐段過目(#19);P0 拍板、gate approve、修 docs/、服務重啟後之呈現層變更=停下問。

### 7.4 驗收判準(逐階段,實測 #7)

- **P1**:10 表建成(冪等重跑無誤);market_direction_feature 每特徵 visible_date 非空且逐表考據入 catalog;晚生特徵 NULL 誠實(2018 前期權法人欄 NULL 率實查);市場特徵覆蓋 2008-12-31 起全交易日曆。
- **P2**:gate 列先於任何 OOS 數字存在(criteria_sha 可驗時序);OOS 表逐 seed 落列 ≥3 seeds;四件套 vs 預註冊判準之判定由 `evaluate_direction_gate.py` 機械執行(非人工目測);H120/H82 檢定力標記正確落 result_snapshot。
- **P3**:**guard 紅隊集全過**——模板句(§6.5-4)餵 guard 必 pass;對抗句必 fail:「明天會漲」「保證獲利」「上漲機率 60%(GATE 前)」「約 0.6 的機率(GATE 前)」「P(終值>0)=0.73(chat 語境)」;GATE 前 `/direction` 頁零數字(curl 實測);既有相對機率四卡 DOM 迴歸比對零退化;服務重啟後 live 實測(#7,systemd 教訓)。
- **P4**:econ_verdict 落表且與呈現硬綁;若 dead=按 §0.4 分級②呈現(頁面掛 dead 標籤實測)。
- **P5**:`is_simulation` CHECK 生效;seed 重現(同 seed 兩跑 summary 一致);chat 問模擬回固定句(零數字)。
- **P6**:結案報告全數字可 trace(#10);勸阻留痕+gate verdict 雙留痕完整。

### 7.5 usage 經濟(#28)

訓練/OOS/評估/模擬全屬執行層=本地 script 零 Claude usage;AI 僅寫碼+讀結果摘要。理解層(本計畫之判準/條文/口徑定義)已窮盡於本定稿。

---

## §8 拍板點彙總(逐項可否)

| # | 拍板點 | AI 建議 |
|---|---|---|
| P1-1 | 條文一全文(§1.2)可否(GATE 數值門檻另於 P2 預註冊時二次親核) | 是 |
| P1-2 | 禁令句 GATE-scoped 化措辭(§1.3) | 是 |
| P1-3 | 靈魂修正行文(§1.5)——最高治權檔,字句由用戶定稿 | — |
| P1-4 | 「逐日價格點位/路徑永久除外」以「無 GATE 可解」強度入憲 | 是(用戶勸阻採納部分,宜鎖死) |
| P1-5 | 原則精華維持 v1.8.0(判準承載於憲章,非新增原則) | 是 |
| P1-6 | 展示分級閉集入憲(過 GATE 而經濟判死=僅研究級誠實展示;修訂 C2) | 是 |
| P2-1 | horizon 錨(修訂 B1):**A 案**=30/60/120 天→H20/H40/**H82**(H82 增訓、H120 研究對照)|B 案=120 天→H120(+45% 偏差明標、零增訓) | **A 案** |
| P4-1 | FREEZE 詮釋「期限凍結 vs 來源集凍結」(修訂 E1)——**條件觸發**:唯實證缺口成立才裁;機制=freeze_manifest 版本化 | 觸發前不裁;v1 零新源 |
| P6-1 | guard 閘⑥新增(加嚴;既有①-⑤一字不動;撤草稿「不改 guard 一字」自訂鐵律,修訂 C1) | 是 |
| P7-1 | 分階段推進授權(#26 有界自主:P1/P2/P4/P5 本地自驅、P0/approve/docs/呈現層停下問) | 依用戶 |

---

*本計畫全數字 trace 回 §0.5 Q1-Q12;勸阻留痕(§0.2)與用戶堅持決定(§0.3)並列,依 #8 不消音、不掩蓋。實驗死亡=誠實結果;預言機的誠實不在「都答對」,在「說得出自己多常對」。*
