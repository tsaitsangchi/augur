# alpha Phase 1 尾段(1-6/1-9 部分)——配額中斷、搶救留檔

> **狀態(#8 誠實)**:workflow wf_390aeef6-155 於 2026-07-17 撞月度配額上限,7 agents 中僅 2 完成(D2 選定、1-9 草案);
> **1-7 D3 選定 / 1-8 D1 前置盤點 / D2 兩候選漏斗四道 / 判決合成 = 全被配額擋、未執行**(非判死、是未跑)。
> 續跑=配額重置後 resume(resumeFromRunId=wf_390aeef6-155,已完成 agent 快取零重耗)。本檔僅存已完成之 2 段,不補未跑段。


## 1-9 live OOS 承接草案(已完成;呈 hugo 拍板)

以下為任務 1-9 交付:live OOS 承接管線明文化草案(預註冊文本,呈 hugo 拍板;數字全實查,來源=live DB + repo 實讀)。

---

# 1-9 草案:live OOS 承接管線明文化(預註冊文本)

## A. `scripts/run_revalidation_cycle.py` 現況行為+排程歸屬提案

**現況行為(實讀)**:四步編排——① `#8` gate(跑 `tests/test_release_lag_antileakage.py`,不過即中止 fail-closed)→ ② `scripts/revalidate.py --run --skip-existing`(B/C/D 全 cell 重跑+deflation 整合,寫 `revalidation_ledger`;同 as_of 已有列則整輪跳過=冪等)→ ③ `scripts/revalidate_verdict.py`(兩軌三態判停,寫 `revalidation_verdict`)→ ④ 告警落地(print 橫幅一次性)。panel 資料驅動:as_of = **min(max core_universe_asof.as_of_date, max feature_values.panel_date)**(`revalidate.py:80`),無新 panel 即 no-op,故可安全過度排程。

**實查發現(承接的斷鏈,1-9 驗收「live panel 續建節奏確認」之答案)**:
- 現況 `feature_values` max panel=**2026-06-30**(G1-PIN 已建),但 `core_universe_asof` max=**2026-05-31** → cycle 的 as_of 被 min() 釘死在 05-31,`revalidation_ledger` max as_of 亦=05-31。**宇宙續建是缺口**:不補則 live OOS 永遠進不了 ledger。
- 故每季承接鏈明文為四段(全本地零 usage,除上游 sync):**(1)** 季末後 attestation 綠(`audit_selfheal.sh`/daily_maintenance,既有)→ **(2)** `python scripts/build_core_universe.py --since 2014-01-01 --liquidity-pct 25 --exempt-revenue-financial --asof`(補新季 as-of 宇宙)→ **(3)** `python scripts/build_feature_panel.py --panels <季末日>`(如已建則跳過)→ **(4)** `python scripts/run_revalidation_cycle.py`。
- **settle 滯後誠實條款**:H60 期需 ~60 交易日 forward settle——2026-06-30 panel 的首個 live 期約 **2026-09 下旬**才入淨值序列;live T 增量固有約一季滯後,排程月頻+冪等自動吸收,不必人為對時。
- **panel 續建頻率口徑(拍板點 A2)**:`feature_values` 已含月末 05-31/06-30 兩個非純季 panel,而 STAGE C/D 經濟序列吃範圍內**全部** panel(`revalidate.py:238`)——續建頻率本身就是建構口徑。**建議預設=季頻續建**(與凍結配方同頻;下一個=2026-09-30);月頻併入=P6(tr3m)預註冊事項、未過前不建月末 panel(C-x7 混頻並池覆核未完前尤然)。

**排程歸屬提案(拍板點 A1)**:
- **主案=systemd --user timer**(oneshot service+timer,`Persistent=true`),**月頻**觸發(如每月 5 日 04:30,避開 03:30 augur-embed-catchup 與 audit 對帳窗之 CPU/DB 峰;本支零 API,B-m4 IP 互斥不適用)。理由:本機已有先例(`~/.config/systemd/user/augur-embed-catchup.timer` 等三支);WSL2 常關機,`Persistent=true` 補漏跑——季頻工作漏一次=延誤三個月,cron 無此保障。月頻+`--skip-existing` ⇒ 無新 as_of 時為 no-op,最壞延遲 ~35 天。
- 替代案=user crontab(arena 三條先例、flock 模式);功能等價但漏跑不補,列為次選。
- 符合 CLAUDE #28/docstring「一次性排程或用戶手動觸發、非常駐 daemon」:timer 觸發 oneshot,非駐留。
- **告警承接誠實條款**:現行告警為 print 一次性、假設「執行者當下看見」——無人值守排程下此假設破。明文:service stdout 落 `~/revalidation_cycle.log`;裁決 SSOT=DB `revalidation_verdict`(已落地);**hugo 檢視點=每季 settle 窗後(約 1/4/7/10 月上旬)檢視 log 與 verdict**;非 deploying 狀態=人審,系統不自動下架(靈魂:建議/決策分層)。

## B. live 期 trial 記帳口徑預註冊(N/T 界線;引 P0 §6 錨)

**錨(P0 §6 實算,`reports/alpha_p0_diagnostics_20260718.md`)**:每筆 trial 抬確立門檻 +0.0086 年化 SR、即期 −0.7pp DSR(N=32→33);每個 live 期降門檻 −0.0162;1 trial ≈ 0.53 live 期 ≈ 1.6 個月 live 等效紅利。**誠實框架**:因現行 sr_pp < SR_0(N=32),do-nothing 之 DSR 隨 T **微降而非爬升**——live T 的價值=門檻下移+真 OOS 檢定力,不是 DSR 自然過線;預註冊此句以防有人以「等 T」為 DSR 操作手段。

**規則(R1-R8;凍結,改動=新預註冊須 hugo)**:
- **R1(同 trial 之 T 延伸=免 N)**:trial 身分=`trial_ledger` UNIQUE 八元組 `(model,horizon,top_frac,weight,feats_hash,cost,sample_since,recipe)`。同 key 對**末端延長**之窗(新 live panel append、`sample_since` 不動)重評=同 trial:ON CONFLICT UPDATE 更新 metric_value/n_periods,**N 不動**。此界線已 schema 機械強制(UNIQUE 不含 as_of;`revalidate.py:refresh_trial_ledger` docstring),非紀律口約。
- **R2(新 trial=N+1)**:八元組任一分量變動=新 trial,**live 期不豁免**——live 資料給的是免費 T,永遠不給免費 N。新 recipe 詞仍須先入 §4.3(b) 凍結詞彙表。
- **R3(窗方向性)**:「T 延伸」僅指末端追加。改起點(`sample_since`)、剔除中段 panel、改 panel 頻率=建構變更→新 trial 或獨立預註冊項(P6)。
- **R4(feats_hash 穩定 guard)**:live 續跑時 feats_hash 必須等於凍結配方(`canonical34_stageB_20260706`);若因 live panel 特徵覆蓋缺損致交集漂移→**資料品質事故,非 trial**:該輪中止不入 ledger、修 writer/重建(#12),禁以新 hash 列入帳。建議落地為 cycle 內 assert(fail-closed,小改、判準零改動)。
- **R5(per-trial confirmatory clock)**:每筆 trial 之 confirmatory live T 只計**該 key 首次入 ledger(min run_at)之後才 settle 的期數**——設計當下已可觀測的 live 期對該 trial 屬 in-sample,不得回收充作其 OOS。headline(07-06 凍結)自 G1-PIN(2026-06-30)起全數乾淨。此條封「看了 live 再註冊一個貼合配方、回頭宣稱 live 為其 OOS」之洞。
- **R6(live 期診斷)**:本地唯讀診斷/預診不入 ledger 照舊(§4.3(a));因看 live 數據而放棄之候選同樣入 reports 留痕(N 語境可稽核,P0 §8 先例)。判準=是否產出用於挑選的淨值成績:confirmatory 評估必入帳,唯讀量測不入。
- **R7(記帳算術=界線的操作定義)**:每季重算 N=ledger 當下機械 DISTINCT(含 recipe;現=33)、T=headline 淨值序列全期數(含已 settle live 期;現=25)。**N 與 T 去耦**:T 隨 R1 成長、N 只隨 R2 成長。任何 DSR 引用一律帶戳記「DSR x% @ N=y, T=z, as_of=w」(P0 §5 配套紀律)。
- **R8(負面清單,皆付 N)**:改 cost 常數(P7 per-stock 落鍵=另行預註冊表示法)、任何形式 H20 借道(h20_dead_no_shortcut)、live 期試跑新 overlay 變體出成績後不入帳(=敵③)。

## C. 每季 DSR 隨 T 重算並入檔:機制點

- **重算引擎=既存,零新碼**:`scripts/revalidate.py` 之 `refresh_trial_ledger`(寫 net_sharpe→refresh)→`deflation_rows`(讀 ledger N→`src/augur/evaluation/deflation.py::deflated_floor`)→逐 cell 寫 `revalidation_ledger` 之 `dsr`+`deflated_sharpe_ann` 列(as_of 戳)。每季 cycle 跑到新 as_of,DSR 即隨新 T、當下 N 自動重算入 DB——**入檔住所 SSOT=`revalidation_ledger`**。
- **headline KPI 戳記**:KPI SSOT=`scripts/deflate_headline_verdict.py`(print 級)。**建議(零 code 變動)**:排程 unit 內 cycle 後串跑之、輸出 append 同一 log;次選=cycle 加第 5 步(小改)。
- **殘留債承接(拍板點 C1;P0 §5「建議、未做」)**:`deflation_rows` 寫 dsr 列時 note 未持久化 sr_pp/ppy/skew/kurt→歷史 DSR 無法免重跑復現。建議併 1-9 落地:note 字串補此四值+T(判準零改動、純 provenance,改 `revalidate.py` 一處+selftest)。
- 可選人讀層:每季 digest 落 `reports/revalidation_digest_<YYYYQn>.md`(由 log 整理,非 SSOT)。

## 拍板點彙總(全須 hugo)
A1 排程歸屬(建議 systemd --user timer 月頻 Persistent)|A2 live panel 續建頻率(建議季頻預設、月頻繫 P6)|A3 告警承接檢視點(季檢 log+DB verdict)|B R1-R8 預註冊文本凍結|C1 dsr note 持久化小改。

**未做/未測聲明**:本草案為文本交付,未建 timer unit、未改任何 code、未跑 cycle;§A 斷鏈與 §C 機制皆 live DB/repo 實查(`trial_ledger`=33 列 recipe 含 buf10/20;`revalidation_ledger` max as_of=2026-05-31;panel max=2026-06-30;`core_universe_asof` max=2026-05-31)。

**關鍵路徑**:`/home/hugo/project/augur/scripts/run_revalidation_cycle.py`、`/home/hugo/project/augur/scripts/revalidate.py`(:80 as_of min 邏輯、:284 refresh_trial_ledger、:292 deflation_rows)、`/home/hugo/project/augur/scripts/deflate_headline_verdict.py`、`/home/hugo/project/augur/scripts/build_core_universe.py`、`/home/hugo/project/augur/scripts/build_feature_panel.py`、`/home/hugo/project/augur/reports/alpha_p0_diagnostics_20260718.md`(§5/§6 錨)、`/home/hugo/project/augur/reports/taiwan_alpha_improvement_plan_20260717.md`(§4.3、1-9 列)。

## 1-6 D2 候選選定(已完成;**尚未進漏斗、僅選定+預診**)

