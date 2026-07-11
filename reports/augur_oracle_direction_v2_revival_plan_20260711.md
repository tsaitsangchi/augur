# Augur 預言機方向軸 v2 復活攻堅計畫(對抗審查後定稿・待拍板)

> **性質**:計畫先行文件(憲章第六部 v1.39.0;plan-first、用戶拍板後才實作)。
> **前情**:v1 六門 direction_gate 於 2026-07-11 全判 `evaluated_fail`(hugo 親核、機械裁決、留檔)。
> 本計畫=在**憲章 v1.42.0 現法之內**的**二次可證偽實驗**;初稿經 4 視角對抗審查(28 項發現、7 blocker),
> **全數採納修訂**,發現表全文見 §8。數字可溯源(§0.5;#9/#10)。

---

## §0 三十秒總覽・勸阻留痕・可證偽賭注宣言

### 0.1 三十秒

v1 死了,解剖發現:**(a)** 兩門近失——D5 的 hit-rate 關已過(p=0.038,**但此值含 best-of-2 champion 選擇、未校正**),只敗 Brier 0.00346(校準問題);H40 在修正基線下 p≈0.105 且 Brier 大勝。**(b)** 一批彈藥未上膛——5 個市場籌碼/情緒特徵因 visible_date 對位缺陷 0 列進過模型;D 軌個股籌碼族明文留給 v2;TXO P/C、IV skew、TX 大額 OI、殖利率曲線、景氣燈號在庫未用。**(c)** v1 有程序缺陷須先修(基線口徑、evaluate 判前斷言、D 軌零 purge、estimand 未釘死、v1 證據保全)。v2=修繕加固 → 上膛彈藥 → **K=4 門新 gate 先凍後跑** → 機械裁決。**判死=誠實結果**;全家族再死 → 二次證偽結案,方向軸蓋棺至解凍後新資料,**不開 v3**(寫入 criteria 凍結)。

### 0.2 AI 勸阻留痕(v2 版全文;依 #19/#26/#27 如實留痕、不消音)

1. **先驗不利**:v1 六門全判死非執行失誤——校準普遍良好(D1 ECE 0.0145),死在「無超越多數類基線的訊號」;修正基線重算 H 軌 hit 關仍全 fail(eff-t +0.146/+1.253/+0.358/−1.314)。且 v2 的近失證據(D5/H40)**與 v1 同源、非獨立**——同一份凍結資料上這已是第 7-10 次觀看。(來源:direction_gate.result_snapshot;§8-S7)
2. **獎品上限=研究級**:即使統計全過,經濟終關預期仍死(D5 預註冊 expected_econ=dead:來回 0.585% vs 損益兩平≈66.5%;H 軌擇時 overlay 於 H40+ 從未出場)。最好結局=「統計可辨、經濟不可交易」的研究級誠實展示。(來源:dgate_D_5.criteria、reports/direction_econ_20260711.md)
3. **FREEZE 下樣本不會長大**:H 軌月頻化的真實檢定力增益只有 **×1.5~2**(對抗審查實算:同 v1 窗等效 n≈25;宣稱 ×3 是把「換評估窗」混進「換頻率」的假象,已修正 §3.4)。真天花板=解凍後資料累積,非方法。(§8-S3/F6)
4. **對抗審查已代跑的壞消息**:D1 高 IV regime 門在其自身 v2 PIT 口徑下**今天就不過關**(trailing 分位重算 p=0.108),且其假說係看過評估資料後選出(double-dipping)——該門已從 v2 撤除(§8-S1/S2)。
5. **三敵不是試錯對象**:v2 之「試」限於方法與參數;為過關挪門柱、換基線、選擇性報告=零容忍。

### 0.3 用戶指示與成立條件

用戶於 2026-07-11(v1 判死當日)指示:依 ultracode 多視角對抗審查窮舉方法,寫 v2 升級計畫,目標=個股 as-of 2026-05-31 之 30/60/120 天方向報酬機率與準確率、個股或全市場 top3/top5。成立條件(承 v1 主計畫 §0.3):①預註冊可證偽(先凍後跑、hugo TTY 親核、機械裁決);②勸阻與堅持雙留痕(本節);③敗退路徑預先寫死(§0.4)——**實驗死亡=誠實結果、非重跑到過為止**。

### 0.4 可證偽賭注宣言+敗退路徑(先於任何數字寫死)

v2 家族 **K=4 門**一次揭露、家族封閉(執行中不得追加);**完整測試序列=v1 六門+v2 四門=同一凍結資料上共 10 門**,結案報告一律按 10 門揭露:

| 門 | 級別 | 賭注一句話 | 綁定判準加嚴 | 誠實預期(寫入 criteria) |
|---|---|---|---|---|
| `dgate_D_5_v2` | 主 | purged 校準層+籌碼五族能讓 D5 的 Brier 翻正、hit 關(不保證)續過 | α=0.05;受判 family 預先鎖定 `DailyGBDT_cal` | 全家族最高;econ 仍預期 dead |
| `dgate_H_40_v2` | 主 | 月頻 panel+特徵直餵+市場分量升級讓 H40(60 天)三關同過 | α=0.05;family=`DirStackM`;窗預先凍結 | 低中(修正基線 p≈0.105 起點) |
| `dgate_H_20_v2` | 次 | 同 H40 v2 架構之 30 天門 | **α=0.01 綁定**;pass=provisional(§3.7) | 低(v1 修正基線 p≈0.44) |
| `dgate_H_82_v2` | 次 | 同 H40 v2 架構之 120 天主錨門 | **α=0.01 綁定**;pass=provisional | 低(v1 三關全敗) |

**撤除**(對抗審查裁定):`dgate_D_1_hiiv_v2`——PIT trailing 口徑下前提已不成立(p=0.108)+post-hoc regime selection 無法以預註冊恢復效度+「條件輸出」形不在憲章展示分級閉集內(§8-S1/S2/D6);降級為解凍後研究線索留檔,不立門。
**不復活**:H120(四軸全爛+退化恆漲)、D1 全樣本(121 萬樣本下 p=0.124=訊號本質近零)。
**永久除外(不因 v2 鬆動)**:逐日/任意粒度**價格點位・路徑・目標價**=永久禁止、無 GATE 可解;路徑好奇心唯 MC 模擬情境頁。

**敗退路徑(寫死,並隨 criteria sha 凍結——取代 v1 模板中對終態列不可實作的「舊列 superseded」句)**:
- 任一門未同過三關 →`evaluated_fail` 判死留檔、永不出 UI;相對機率層零影響。
- **v2 全家族判死 → 二次證偽結案報告親簽;方向軸凍結至 FREEZE 解凍+新資料累積,期間不得另立同假說新 gate(不開 v3)**——此句寫入每門 criteria fail_path 隨 sha 凍結;是否再上升為治權檔條文=拍板點③。
- 次門(H20/H82)即便 pass:**provisional**——不解鎖完整展示,唯解凍後新資料 confirmatory gate 確證才升級(寫入 criteria)。
- 統計過但經濟 dead/thin → 研究級誠實展示(「非交易訊號」硬綁)。
- top3/top5 組合層隨個股門、不得單獨解鎖;兩軌獨立互不解鎖;trigger 機械禁挪門柱。

### 0.5 實查來源清單(#9/#10)

| 數字/宣稱 | 來源 |
|---|---|
| 六門死因全數字 | DB `direction_gate.result_snapshot`(對抗審查獨立覆算逐格一致,§8-S8) |
| H 軌千里眼 vs 修正基線重算 | `direction_oos_sample` 重算(初稿研究+審查雙覆算一致) |
| 5 個 lag-1 特徵 0 列被消費 | SQL(五特徵全列 visible>panel)+`train_market_direction.py` WHERE 句(審查雙證實) |
| D5 p=0.038 含 best-of-2 | `train_daily_direction.py` champion 迴圈(以 OOS hit 擇 2 族之勝者;§8-D2) |
| D1 hiIV PIT 重算 p=0.108 | 對抗審查代跑(trailing 252td 嚴格前一日分位;§8-S1) |
| 月頻等效 n(×1.5~2) | 審查親算(MA(1) ρ₁=19/40;probability_oos_sample 2016-2020 實為**年頻**、2021+ 才季頻) |
| v1 D 軌實跑時長 ~14 分鐘 | model_registry created_at 17:15:56 → oos 落表 17:22/17:29(§8-F8) |
| 籌碼五族列數 | **以 §5 建置腳本內明寫 SQL 重算為準**(初稿引數不可重現已撤,§8-F4);表名/起始年已驗:Inst 2012+/Margin 2001+/ShortSale 2005+/DayTrading 2014+/Shareholding 2004+ |
| evaluate 腳本 git 狀態 | 判決當時未追蹤(歷史事實);**已於 163caf0(19:11)補 commit**;殘餘工作=判前 clean 斷言(§3.1) |

---

## §1 治權對齊(零修憲;含一個待裁合法性問題)

- 憲章 v1.42.0「預言機誠實判準」ACTIVE:v2 全程走唯一合法路(preregister→approve(TTY)→evaluate→展示分級閉集)。v1 六列終態不動,v2=全新 gate_id 新列。
- ECE 門檻由 `judgestop_threshold.calib_late_ece_ceiling`(0.05 frozen)DB 讀值。
- FREEZE 不動:v2 彈藥全在庫;**庫內部分源表含 FREEZE 後資料(如 fred_series 至 2026-07-02)→ 全部 builder 一律截尾 ≤2026-05-31,P1 驗收機械斷言**(§8-C11)。
- 相對機率軸零退化;guard 單向棘輪(W6 只加閘不鬆閘;合法措辭不得倒逼放鬆閘③,§8-D8)。
- hit-rate 基線=**全局多數類固定方向 max(p̄,1−p̄) 同窗實算、禁逐 panel 實現值(千里眼)基線**——寫死於每門 criteria。
- **已識別的治權邊界問題(不偷渡)**:「條件輸出門」(如高 IV 日才輸出)之合法形不在現行展示分級閉集內——本計畫**不採用**該形;若未來要用,屬治權判準變更、須用戶親核修文(§8-D6)。

## §2 v1 判死解剖(事實基礎;數字經審查獨立覆算)

### 2.1 六門死因總表

| 門 | hit / base | eff-t(存檔) | eff-t(修正基線) | Brier(model/base) | ECE | 單調 | 敗關 |
|---|---|---|---|---|---|---|---|
| H20 | .5482/.5398 | −3.354 | **+0.146**(p≈.44) | .24608/.24842 ✓ | .029 ✓ | .952 | hit |
| H40 | .6035/.5561 | −4.984 | **+1.253**(p≈.105) | **.23521/.24685 ✓** | .0502 ✗(超 .0002) | .988 | hit+ECE 毫釐 |
| H82 | .5712/.5573 | −5.787 | +0.358 | .24702/.24672 ✗ | .0752 ✗ | .794 | 三關 |
| H120 | .5665/.5891 | −1.887 | −1.314 | .25123/.24206 ✗ | .1153 ✗ | **−0.212 ✗** | 全滅+退化恆漲 |
| D1 | .5516/.5484 | +1.157(p=.124) | 同左 | .24716/.24766 ✓ | .0145 ✓ | 1.0 | hit 顯著性 |
| D5 | .5193/.5018 | **+1.773(p=.038)✓**(best-of-2 未校正) | 同左 | .25346/.25 ✗(差 .00346) | .0465 ✓ | .685 | 僅 Brier |

三關定義:(i) 逐 panel (hit−多數類 base) 序列 HAC Eff-t 單尾 p<α;(ii) OOS Brier < p̄(1−p̄);(iii) ECE≤0.05(DB 讀值)且十分位 Spearman 單調>0。粒度:H 軌=個股 pooled 騎相對軌 panel 網格(**2016-2020 年頻、2021+ 季頻**;stack OOS 實際 2022-03-31 起 16 季);D 軌=1.21M 樣本、2,528+ 日 cluster。

### 2.2 程序發現(v2 之 P0 修繕標的;判死結論不受影響)

1. **H 軌評測基線=千里眼口徑**(嚴於預註冊意圖);修正重算仍全敗=判死穩健;v2 criteria 基線句寫死到無歧義。
2. **evaluate 判決時未入 git**(已於 163caf0 補 commit);殘餘=判前斷言(工作樹 clean+evaluation_ref=HEAD)未實作。
3. **D 軌零 purge**(docstring 與實碼不符);D5 近失可能微幅高估;v2 補真 purge。
4. **estimand 未釘死**:evaluate 取樣 `WHERE {hcol}=%s` 無 model_id/seed/頻率過濾(v1 靠「一表一 champion」僥倖成立);criteria 無樣本定義欄=挪門柱後門。
5. **champion 以 OOS hit 擇勝**(best-of-2)後才判門=門內選擇偏誤;v1 criteria 未載。
6. **v1 證據無保全機制**:trainer `DELETE WHERE k_td` 整段刪、MktLogit 同 id upsert 覆寫;trigger 不保護終態列之 result_snapshot 重寫。
7. **特徵消費缺口**:5 個 lag-1 市場特徵 0 列進過 MktLogit(未試非死)。

## §3 v2 攻堅設計

### 3.1 W1 程序修繕與證據保全(前置;純執行層)

| 修繕 | 檔 | 內容 |
|---|---|---|
| v1 證據備份 | (P0 一次性) | `pg_dump` 方向軸 6 表基線備份(#30 慣例;dump 期間禁 DDL) |
| trainer 刪除範圍 | `train_daily_direction.py` | `DELETE ... WHERE k_td=%s AND model_id=%s`;v2 一律新 model_id、v1 列不動;驗收=v1 列數逐表不變(DailyLogit k1=1,210,073、DailyGBDT k5=1,208,701) |
| 市場模型隔離 | `train_market_direction.py` | v2 用 `MktLogit_v2`/`MktGBDT` 新 model_id 新 registry 列(新 feats_hash);v1 `MktLogit` 16,276 列 P_mkt 不覆寫 |
| builder 刪除範圍 | `build_daily_direction_features.py` 等 | DELETE 改 (panel_date, feature IN 本次建置集) |
| trigger 加固 | `migrate_direction_ddl.py` | 終態列(`evaluated_*`)之 result_snapshot/evaluated_at/evaluation_ref/git_sha 任一 DISTINCT 即 RAISE;附負向單測 |
| 判前斷言 | `evaluate_direction_gate.py` | 斷言工作樹 clean 且 evaluation_ref=實際 HEAD,否則拒判 |
| estimand 引擎 | `evaluate_direction_gate.py`+criteria 模板 | criteria 新增機械樣本定義欄:`model_id` 精確值、`seed_aggregation`(凍結:同 (panel,target) 對 seeds 取 mean 成一列)、panel 頻率與**起訖窗**、取樣述詞全文;evaluate 依 criteria 參數化過濾,表內多 family 而 criteria 未指名→拒判 |
| trainer as-of join | `train_market_direction.py::_load_features` | 逐特徵取最新 visible≤panel 值;per-feature 入模非 NaN 計數落 log(驗收據此,非查表) |
| D 軌真 purge | `train_daily_direction.py::_year_blocks` | train 標籤右端 < test 年首日(截尾 k td);單測 |
| HAC lag 顯式 | `evaluate_direction_gate.py` | 月頻門顯式 lag ≥ ceil(h_td/21)+1(H40→3、H82→5),lag 規則寫入 criteria 凍結 |

### 3.2 W2 `dgate_D_5_v2`:purged 校準層+個股籌碼族(主賭注)

- **訊號基礎**:v1 hit 51.93% vs 50.18%、p=0.038(**含 best-of-2、未校正**——v2 之新可證偽內容=Brier 翻正+新特徵增量,hit 續過不視為新證據)。
- **purged 校準層(憲章硬綁②合規版;取代初稿有洩漏疑慮的「train 尾段」寫法,§8-S4)**:每折 train 內切 fit-set 與校準尾段、兩者間留 **k td 內層 embargo**(fit-set 標籤右端<尾段首日);GBDT 只 fit 於 fit-set;對尾段做 **out-of-sample** 預測,在 (OOS 預測,標籤) 上 fit isotonic;凍結複合模型套 test。calibrator provenance=model_id 命名規約 `DailyGBDT_cal@<fold>#<calibrator_sha>` 寫入 criteria。**誠實註記入 criteria**:isotonic 可移動 p=0.5 交叉點,D5 的 hit 過關不自動保留。
- **個股籌碼五族**(全 lag-1;**D 軌落表口徑寫死:panel_date=可見交易日(值位移一日),表無 visible_date 欄**;驗收=抽 n 筆核對 feature 值=源表前一交易日值,§8-C4):`d_inst_net_z`(Inst 2012+)、`d_margin_chg_5`(Margin 2001+)、`d_short_bal_chg_5`(ShortSale 2005+)、`d_daytrade_ratio`(DayTrading 2014+;**逐年覆蓋表列入 P1 驗收**——2015 年僅 ~291/776 檔有值,NULL 政策:GBDT 原生 NaN、Logit 折內 median impute,與現碼一致)、`d_foreign_hold_chg_20`(Shareholding 2004+)。列數以建置腳本明寫 SQL 重算為準。
- **seeds 口徑(修正初稿失實敘述)**:v1 GBDT 本已 3 seeds 但只落均值單列(seed=0);v2 改 **per-seed 落列**(PK 已含 seed)以滿足 #11 逐 seed 統計;判門依 criteria 凍結之聚合規則。
- **受判 family 預先鎖定 `DailyGBDT_cal`**(criteria 載明);DailyLogit/DailyGBDT 陪跑列報、不入裁決。
- econ 終關:統計過關才跑;預期 dead 已寫死。

### 3.3 (已撤除)D1 高 IV regime 條件門

對抗審查三重裁定(PIT 重算 p=0.108 前提不成立;post-hoc regime selection 同資料雙重使用;條件輸出形不在憲章閉集)→ **不立門**。診斷線索(edge 表面集中高 IV,實為基率假象:高 IV tercile 內模型 hit 反低 2.05pp)留檔於本節供解凍後參考。若未來復議:先過「條件輸出合法形」治權拍板,且假說須以解凍後**新資料**立 confirmatory gate。

### 3.4 W4 `dgate_H_40_v2`(主)+`dgate_H_20_v2`/`dgate_H_82_v2`(次;α=0.01 綁定+provisional):月頻 panel+特徵直餵+市場分量升級

**誠實的檢定力帳(修正初稿 ×3 宣稱)**:相對軌 panel 2016-2020 為年頻、2021+ 才季頻;月頻化真實增益:

- **方案 A(推薦)**:月頻窗凍結於 **2021-04→2025-12(季頻 rank 時代)**≈57 個月末 panel,embargo 後 OOS ~45-50;h=40td 重疊下等效獨立 n≈25-28(**×1.5~1.75 於 v1 的 16**)。rank_pctile 取最近季度 as-of 值(stale≤3 個月,如實)。
- **方案 B**:延伸窗 2017+(~95 panel、等效 n≈50)——代價=2017-2020 rank 為**年頻**(stale 可達 12 個月)+評估母體與 v1 不同、「復活」語意受限。
- **窗的選擇=拍板點②之一部,選定後寫入 criteria 凍結,evaluate 時無挑窗自由度。**

**工程如實(修正初稿「一個 flag」的失實描述,§8-F1)**:月頻 stack 需要**新特徵建置**——`feature_values` 無月頻 panel,不得污染其 canonical 網格;新增表 `direction_stack_feature_monthly` + 新 builder 於各月末直接由日價算:`volatility_60d`、`momentum_60d`、`beta_252`(TRI 對 TAIEX;beta 不在 35 特徵之列、於此表落地)、`d_inst_net_z` 月頻聚合;月頻標籤 y_up/fwd_ret 由 `TaiwanStockPriceAdj` 新算(月末 as-of、h td 前瞻、FREEZE 截尾);月末宇宙=最近相對 panel 股票集 as-of。`train_direction_stack.py` 近乎重寫(非加 flag)。

**市場分量升級**(MktLogit_v2/MktGBDT;修復 as-of join 後籌碼/情緒 5 特徵首次進場,再加):`mkt_pc_ratio`+`mkt_iv_skew`(TaiwanOptionDaily 33.7M 列 2002+,derive 擴推)、`tx_large_oi_z`(2007+)、`t10y2y`/`t10y3m`(vintage PIT;builder 截尾 FREEZE)、`biz_signal`(**visible_date=資料月+2 個月**,對齊 repo 先例 `verify_regime_timing.py --lag 2;初稿 +27 日=偷看未來已修正**,§8-F3)。
**受判 family 預先鎖定 `DirStackM`**;MktGBDT 為市場分量 challenger,其取捨規則(train 內部驗證選定、非 OOS)寫入 criteria。

### 3.5 W5 top3/top5 組合層(隨個股門)

組合標籤=等權組合 H 內實現報酬>0;月頻方案 A 下 n≈57/horizon(**小樣本明標、單獨列 n**);隨個股層 GATE、不得單獨解鎖;呈現硬綁「組合口徑非個股平均」。建置=`build_direction_combo_oos.py`(P3 建、P3 驗收列數)。

### 3.6 W6 呈現層+生產端(唯 pass 後實作;fail-closed)

- **生產腳本(初稿缺位,§8-C7)**:`produce_direction_probability.py`——唯 `evaluated_pass` 之門觸發;以 criteria 同配方全資料重訓、對 as-of 2026-05-31 出 P(up),寫 `direction_probability`/`daily_direction_probability`(帶 gate_id/econ_verdict/base_rate 硬綁欄)。
- `payload.py` 增 `directions` fail-closed 欄;`guard.py` 閘⑥ `_PROB_NUM` 白名單。
- **advisor 短路句改 DB 驅動**(現為 Python 常數「六門判死」——v2 後 10 門,無論結果皆失準):即時讀 direction_gate 組句、fail-closed 預設全拒(§8-D7)。
- **紅隊驗收**:每一合法措辭模板實例通過現行 guard 全部閘且**不得改動閘①-⑤ 任一 regex**(措辭避開閘③觸發詞:用「次 N 日」不用「明日」)。

### 3.7 家族多重測試誠實(綁定、非修辭)

- 家族句全文(K=4、完整序列=v1+v2 共 10 門、D5 hit 含 best-of-2 之相依聲明)**寫進每門 criteria 隨 sha 凍結**,evaluate 家族總表機械輸出——不能挪、不能消失(§8-D9)。
- 主門 α=0.05;**次門 α=0.01 綁定入 criteria**;次門 pass=provisional 不解鎖完整展示。
- 門內模型選擇:受判 family 逐門預先鎖定(§3.2/§3.4),champion-by-OOS 廢止。
- 證據相依聲明:v2 假說選自 v1 解剖(同一凍結資料)——名義 p 值帶選擇偏誤,結案報告如實載明。

## §4 Table Schema(v1.39.0 (a))

### 4.1 新 DDL(住所:family CHECK 沿 v1 慣例改 `migrate_prediction_ddl.py`(單一住所 #12);其餘住 `migrate_direction_ddl.py::apply_v2`;全部冪等)

```sql
-- (1) model_registry family CHECK(migrate_prediction_ddl.py 就地改清單,+3 族)
--     ('RankRidge','RankGBDT','MktLogit','DirStack','DailyLogit','DailyGBDT',
--      'DailyGBDT_cal','MktGBDT','DirStackM')
-- (2) 月頻 stack 特徵表(新;不污染 feature_values canonical 網格)
CREATE TABLE IF NOT EXISTS direction_stack_feature_monthly (
  panel_date  date   NOT NULL,          -- 月末 as-of(≤2026-05-31)
  target_id   text   NOT NULL,
  feature     text   NOT NULL,          -- volatility_60d/momentum_60d/beta_252/d_inst_net_z_m
  value       float8,
  git_sha     text   NOT NULL,
  PRIMARY KEY (panel_date, target_id, feature)
);
-- (3) 組合層 OOS(欄位對齊既有 OOS 慣例:y_up smallint、horizon、git_sha、model_id)
CREATE TABLE IF NOT EXISTS direction_combo_oos_sample (
  combo      text     NOT NULL CHECK (combo IN ('TOP3','TOP5')),
  horizon    int      NOT NULL,
  panel_date date     NOT NULL,
  p_up       float8   NOT NULL CHECK (p_up BETWEEN 0 AND 1),
  y_up       smallint NOT NULL CHECK (y_up IN (0,1)),
  fwd_ret    float8   NOT NULL,
  model_id   text     NOT NULL,
  seed       int      NOT NULL DEFAULT 0,
  git_sha    text     NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (combo, horizon, panel_date, model_id, seed)
);
-- (4) direction_gate trigger 加固(§3.1):終態列 result_snapshot 等欄禁改
```

### 4.2 所讀既有表(schema 引用經審查更正)

| 表 | 關鍵欄(實查) | v2 動作 |
|---|---|---|
| `direction_gate` | criteria/criteria_sha/status/result_snapshot;trigger | INSERT 4 新列;trigger 加固 |
| `market_direction_feature` | feature/panel_date/**visible_date**/value | +6 新 feature;lag-1 特徵經 as-of join 開始被消費 |
| `daily_direction_feature_values` | **(panel_date,target_id,feature,value)——無 visible_date** | +5 籌碼族(panel_date=可見日口徑,§3.2) |
| `direction_oos_sample`/`daily_direction_oos_sample` | **model_id**(非 model_family)/seed/panel_date/p_up/y_up/git_sha | +新 model_id 列(per-seed);v1 列不動(P0 斷言) |
| `direction_probability`/`daily_direction_probability`(0 列) | gate_id FK 等硬綁欄 | 唯 pass 門由 `produce_direction_probability.py` 寫入 |
| `market_direction_probability` | PK(panel_date,model_id,horizon) | +`MktLogit_v2`/`MktGBDT` 列;v1 `MktLogit` 不覆寫 |
| `judgestop_threshold` | calib_late_ece_ceiling=0.05 | 唯讀 |
| 源表(唯讀) | Inst/Margin/ShortSale/DayTrading/Shareholding/TaiwanOptionDaily/TaiwanFuturesOpenInterestLargeTraders/fred_series(**含 FREEZE 後列,builder 須截尾**)/TaiwanBusinessIndicator/TaiwanStockPriceAdj/TaiwanStockTotalReturnIndex(beta 原料)/feature_values(quarterly as-of 唯讀)/probability_oos_sample(**2016-2020 年頻、2021+ 季頻**) | — |

## §5 Python 程式規畫(v1.39.0 (b);全本地零 Claude usage #28)

| 檔(改/新) | 職責 | 輸入 → 輸出 |
|---|---|---|
| `migrate_prediction_ddl.py`(改) | family CHECK +3 族(單一住所) | — → model_registry |
| `migrate_direction_ddl.py`(改) | `apply_v2()`:新 2 表+trigger 加固(冪等,IF EXISTS) | — → §4.1 |
| `derive_market_iv.py`(改) | +`derive_pc_ratio()`/`derive_iv_skew()` | TaiwanOptionDaily → market_direction_feature |
| `build_market_direction_features.py`(改) | +tx_large_oi_z/t10y2y/t10y3m/biz_signal(**+2 月 lag**);全 builder FREEZE 截尾 | 源表 → market_direction_feature |
| `build_daily_direction_features.py`(改) | +籌碼五族(panel_date=可見日;DELETE scoped;resume-safe;逐年覆蓋率輸出) | 籌碼源表 → daily_direction_feature_values |
| `build_direction_stack_monthly.py`(**新**) | 月末宇宙(最近相對 panel as-of)+vol/momentum/beta_252/籌碼月聚合+月頻標籤(PriceAdj h td 前瞻) | PriceAdj/TRI/日籌碼 → direction_stack_feature_monthly |
| `train_market_direction.py`(改) | as-of join 修復;新 model_id `MktLogit_v2`+`MktGBDT`(challenger 以 train 內部驗證取捨);per-feature 消費計數落 log | market_direction_feature → market_direction_probability(新列) |
| `train_direction_stack.py`(**近乎重寫**) | 月頻 panel(窗=criteria 凍結值);family `DirStackM`;豐富 stack 特徵 | P_mkt(v2)+direction_stack_feature_monthly+probability_oos_sample(rank as-of) → direction_oos_sample |
| `train_daily_direction.py`(改) | 真 purge;purged isotonic(§3.2 spec);per-seed 落列;DELETE scoped;family `DailyGBDT_cal` | daily_direction_feature_values → daily_direction_oos_sample |
| `build_direction_combo_oos.py`(新) | top3/top5 組合 OOS | direction_oos_sample+probability_oos_sample → direction_combo_oos_sample |
| `preregister_direction_gate.py`(改) | v2 四門 criteria 模板:基線句/estimand 欄(model_id/seed 聚合/窗/述詞)/家族句/α 分級/provisional 條款/fail_path 改寫/HAC lag 規則/誠實預期 | — → direction_gate 4 新列 |
| `evaluate_direction_gate.py`(改) | 判前 clean 斷言;依 criteria estimand 參數化取樣;顯式 HAC lag;家族總表(10 門)機械輸出 | oos 表 → result_snapshot |
| `run_direction_econ_eval.py`(改) | +D 軌經濟終關;+--family 參數(不混 v1/v2) | oos 表 → reports/direction_econ_v2_<date>.md |
| `produce_direction_probability.py`(**新;唯 pass 後**) | criteria 同配方全資料重訓、as-of 2026-05-31 前瞻推論 | 特徵表 → direction_probability/daily_direction_probability |

每支守 #29(_bootstrap、個別可執行、graceful、指令矩陣+實測)。

## §6 分階段執行・驗收・拍板點(**順序修正:先凍後跑**,§8-C1)

| 階段 | 內容 | 驗收(機械可查) | 拍板 |
|---|---|---|---|
| **P0** 修繕+保全 | §3.1 全表+DDL+**v1 證據 pg_dump 備份** | v1 OOS 列數不變斷言;trigger 負向單測;purge 單測;estimand 拒判單測 | **①本計畫拍板** |
| **P1** 特徵建置 | 五族+六市場特徵+月頻表 | 每特徵:`max(panel_date)≤2026-05-31` 斷言;lag 正確性抽查 SQL(D 軌:值=源表前一交易日);DayTrading 逐年覆蓋表;per-feature 消費計數>0(trainer log) | — |
| **P2** 預註冊 | 4 門 criteria 凍結+sha(estimand/窗/α/家族句/fail_path 全入)+**hugo TTY approve** | `--check` sha 覆算;criteria 含 model_id+seed_aggregation+窗欄之機械斷言 | **②criteria 親核(TTY;含方案 A/B 窗選擇)** |
| **P3** 訓練+OOS | 三族 per-seed 落表+combo 建置(#22:背景+sentinel+逐 (family,k,seed) 可續) | 新 model_id 列數;distinct seed=3(GBDT 族);combo 列數+n 明標;v1 列數再斷言 | — |
| **P4** 機械裁決 | evaluate(clean 斷言+estimand 過濾) | 4 門 result_snapshot;家族總表(10 門全列) | — |
| **P5** 經濟終關 | H 全 horizon+D 過關者(--family 隔離) | econ 報告落 reports/ | — |
| **P6** 呈現+生產 | 唯 pass 門:produce 腳本+payload/閘⑥/DB 驅動短路句+紅隊 | guard 全閘相容紅隊單測;payload fail-closed 單測;閘①-⑤ regex 零改動 diff 斷言 | **③全敗→二次證偽結案親簽(含 no-v3 條款是否入治權檔)** |

**回滾/中止**:P0 備份=回滾錨;任一階段中止→v1 狀態零損(v2 全部走新 model_id/新表/新 gate 列);P3 長跑 resume=DB 帳(落表即帳)。
**時長(實證基準)**:v1 D 軌全跑 ~14 分鐘(§0.5)→ v2 全家族訓練估 **30-90 分鐘**(裕度含 isotonic+月頻 builder);非過夜級。

## §7 誠實邊界:v2 之後,web UI 能答什麼

| 問法 | v2 對應門 pass 後 | 永遠 |
|---|---|---|
| 「2330 未來 30/60/120 天方向機率?」 | 30→H20(**次門:即便 pass 也 provisional、不完整展示**)、60→H40、120→H82;研究級:P(up)+「歷史 walk-forward OOS 準確率(horizon 級聚合),非 live、非交易訊號」 | 未過門 horizon 誠實拒答(DB 驅動句) |
| 「top3/top5 組合會漲嗎?」 | 組合 p_up+n 明標+「組合口徑非個股平均」 | 不單獨解鎖 |
| 「每日預測股價變化/目標價/路徑?」 | — | **永久拒答**(修憲鎖死);唯 MC 模擬情境頁 |
| 「哪支準確率最高?」 | — | 永久拒答(禁單股準確率) |

## §8 對抗審查發現表(多視角級留痕;4 agent 平行、28 項、全數裁處)

| # | 視角 | 發現(摘) | 裁處 |
|---|---|---|---|
| S1 | 統計(blocker) | D1 hiIV 門前提在 PIT trailing 口徑下已不成立(審查代跑 p=0.108;「edge 集中高 IV」係基率假象) | **撤門**(§3.3) |
| S2 | 統計(blocker) | hiIV 假說=post-hoc regime selection、同資料雙重使用,預註冊無法恢復 p 效度 | 併 S1 撤門;留檔解凍後 confirmatory |
| S3 | 統計(blocker) | 月頻「×3 檢定力」混淆換窗與換頻;2016-2020 年頻 rank;真實 ×1.5~2 | §3.4 改雙方案+窗凍結;勸阻 §0.2-3 改寫 |
| S4 | 統計(major) | isotonic「train 尾段」spec 有洩漏且機制無效(in-sample fit);缺 provenance | §3.2 改 purged 兩段式+內層 embargo+provenance;hit 不保證註記 |
| S5 | 統計(major) | estimand 未釘死(evaluate 無 family/seed 過濾)=挪門柱後門 | §3.1 estimand 引擎;criteria 機械欄;P0 拒判單測 |
| S6 | 統計(major) | champion-by-OOS(v1 D5 p=0.038 為 best-of-2);trainer DELETE 毀 v1 列 | 受判 family 預鎖;DELETE scoped;§2 註記 best-of-2 |
| S7 | 統計(major) | 家族修正非綁定;順跑門僥倖 pass 無閘;真實序列=10 門非 5 門 | §3.7 綁定:次門 α=0.01+provisional;家族句入 criteria;10 門揭露 |
| S8 | 統計(minor) | §2.1 六門數字覆算**逐格一致**(正面確認) | 留痕 |
| F1 | 可行性(blocker) | feature_values 無月頻 panel;beta 不存在;月頻標籤無源;「+flag」工程量嚴重失實 | 新表 direction_stack_feature_monthly+新 builder;§5 重寫該列 |
| F2 | 可行性(blocker) | evaluate 無過濾將混 v1/v2/seeds 成一鍋 | 同 S5 |
| F3 | 可行性(blocker) | biz_signal「+27 日」=偷看未來 ~1 月;repo 先例 lag=2 月 | §3.4 改 +2 月、引 verify_regime_timing.py |
| F4 | 可行性(major) | 籌碼五族宇宙列數不可重現(一數大於全期實查) | 撤數字;以建置腳本明寫 SQL 重算為準;逐年覆蓋表 |
| F5 | 可行性(major) | MktLogit 覆寫/DELETE 毀 v1 溯源 | §3.1 新 model_id+scoped DELETE+P0 備份 |
| F6 | 可行性(major) | HAC lag 經驗式蓋不住月頻重疊(H82 假過風險);OOS panel 實際 ~95 非 110 | §3.1 顯式 lag 入 criteria;§3.4 數字下修 |
| F7 | 可行性(major) | 月頻 rank stale(年頻時代 12 個月)貢獻大半新 cluster | §3.4 方案 A 窗避開/方案 B 如實揭露 |
| F8 | 可行性(minor) | 「數小時」估計失實(v1 實測 ~14 分);「1-seed」敘述錯(真缺口=per-seed 落列) | §6 時長改實證基準;§3.2 seeds 口徑改寫 |
| F9 | 可行性(minor) | DDL:DROP 無 IF EXISTS;combo 表欄名/型別/git_sha 不齊 | §4.1 修正 |
| D1 | 治權(blocker) | DELETE-by-k_td 銷毀 v1 審計資料,違主計畫 §0.4「僅留審計資料」承諾 | 同 F5/S6 |
| D2 | 治權(blocker) | champion 選擇偏差=敵③藏於裁決前一步 | 同 S6 |
| D3 | 治權(major) | criteria 未釘 estimand;OOS 表欄名係 model_id 非 model_family(schema 引用失實) | §4.2 更正;同 S5 |
| D4 | 治權(major) | 「不開 v3」無機械錨;fail_path 模板「舊列 superseded」對終態不可實作;前科=v1 敗退承諾當日即被 v2 復活 | §0.4 fail_path 改寫入 criteria 凍結;治權檔入條=拍板點③ |
| D5 | 治權(major) | trigger 不保護終態列 result_snapshot(判決快照可被無聲改寫) | §3.1 trigger 加固+負向單測 |
| D6 | 治權(major) | 條件輸出門不在憲章展示分級閉集;「abstain 無」句牴觸 | 撤門(併 S1);合法形問題明列 §1 不偷渡 |
| D7 | 治權(minor) | advisor 短路句 hardcode「六門」;v2 後必失準 | §3.6 改 DB 驅動 fail-closed |
| D8 | 治權(minor) | D 軌措辭「明日」撞既有閘③;驗收缺全閘相容測試 | §3.6 紅隊驗收+選字規範 |
| D9 | 治權(minor) | 家族 Bonferroni「參考值」=影子判準無歸屬 | §3.7 入 criteria 凍結+機械輸出 |
| C1 | 完整性(blocker) | P2(訓練)先於 P3(預註冊)違「先凍後跑」 | §6 重排:P2=預註冊、P3=訓練 |
| C2-C11 | 完整性(blocker/major/minor) | evaluate/econ 過濾口徑;v1 證據保全+回滾缺位;daily 特徵表無 visible_date(驗收 SQL 跑不了);3 seeds 口徑矛盾;W3/W5 無家;stack 特徵來源斷鏈;生產端腳本缺位(§7 承諾不可兌現);同樣本二次檢定;「未入 git」已過時;DDL 雙住所;驗收可執行性;FREEZE 邊界斷言+#22 缺位 | 全數採納:§3.1/§3.2/§3.4/§3.6/§4/§5/§6 對應改寫(本定稿即含) |

---

**結語**:v2 的成功定義不是「過門」,是**把答案釘死**——四門任一過=研究級誠實展示解鎖(次門 provisional);全敗=二次證偽、方向軸蓋棺至新資料時代、不開 v3。兩個結局都讓系統更誠實。**下一步=拍板點①**:本計畫過目;若准,P0 動工,P2 預註冊時再親核 criteria(TTY)。
