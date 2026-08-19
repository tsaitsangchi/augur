---
title: augur 深化理解＋專案優化地基（合併）r19
status: superseded_as_understanding
superseded_by: reports/augur_deep_understanding_and_opt_plan_r20_20260819.md
series: deep_understanding_and_opt
round: r19
date: 2026-08-19
viewpoint: 2026-08-19T14:05+08:00
layer: "[I]"
role: 後續優化地基（理解＋對齊雙軌選刀＋路徑研究收斂）；刷新 r17
supersedes_as_understanding:
  - reports/augur_deep_understanding_and_opt_plan_r17_20260817.md
inherits_understanding:
  - reports/augur_deep_understanding_and_opt_plan_r17_20260817.md
  - reports/augur_deep_understanding_and_opt_plan_r15_20260813.md
  - reports/augur_deep_understanding_and_opt_plan_r14_20260811.md
  - reports/augur_deep_understanding_and_opt_plan_r13_20260808.md
companion_plain_charter: reports/augur_project_charter_plain_zh_r19_20260819.md
exec_nav: reports/augur_opt_stepwise_all_problems_r19_20260819.md
exec_nav_prior: reports/augur_opt_stepwise_all_problems_r18_20260817.md
s1_s5_ssot: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_r16_20260813.md
s1_s5_parent: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md
kh_evolve_ssot: reports/augur_local_ai_kh_loop_evolve_opt_plan_20260806_readout.md
path_opt_ops: reports/augur_path_timing_opt_ops_plan_r18_20260819.md
archive_tip: archive-20260819-path-opt-charge-t5-ridge
self_reported: true
---

# augur 深化理解＋專案優化地基 r19（2026-08-19）

> **現行理解＝r20**（`reports/augur_deep_understanding_and_opt_plan_r20_20260819.md`）。本檔 LIVE＠14:05 已過期（B3＠08-18／HIST＠08-12／08-11 其後已閉）。**市場開工鎖仍＝r19 執行板**。

> **性質**：[I]；**不創** [N]；不解凍；不 sim `--apply`；不假關確立級；**勿重掃假綠**；不假 B3＠08-19。  
> **一句**：在 r16／r17／r18 上吸收 **08-17→08-19** 增量——價頂跟到 08-18、日常出門仍停在 08-17 兩窗、路徑／進出研究已閉一批且宇宙扣成本失敗——收成**下一段優化地基**。  
> **疊用**：人話憲章 r19 → **本檔理解** → **全專案逐步執行** `reports/augur_opt_stepwise_all_problems_r19_20260819.md`（r18 執行板已 supersede）→ 准否／驗收＝S1→S5 運轉契約 r16＋KH evolve＋PATH-OPT 操作手冊＋ARCHIVE／standing／audit。  
> **覆蓋誠實**：非整庫逐檔複讀。倉內約 **151** 支 `src/augur` Python、**17** 個領域 package、**402** 支 `scripts/`、**520** 份 `reports/`、**1068** 份 `audits/`、**59** 份 `constitution/`、**14** 份 `specs/`、**30** 份 `tests/`、**17** 份 `docs/`。本輪＝**結構地圖＋LIVE 親查＋08-17→08-19 收斂＋路徑研究收口＋雙軌治權**；長細節仍回 r15／r16／r17／INVENTORY／治權檔／各軌長板。

---

## 第一部｜深化理解

### §1 專案是什麼（產品真相）

**Augur**＝古羅馬「觀兆者」；「兆」只能是**真實觀測**，「預言」只能是**帶不確定性的相對排序／機率**。

一句話產品：

> **只用真資料，誠實判斷台股誰比較強、知識庫裡到底寫了什麼；說得出依據，也說得出什麼時候該閉嘴。**

它同時承載**三條軸**（領域大憲章 v1.54.0 已對齊；**08-12 起市場與知識的日常選刀再拆成兩塊獨立導航**；**08-19 起市場軸旁另有路徑／進出研究手冊**）：

| 軸 | 白話 | 倉內主落點 | 日常選刀 |
|---|---|---|---|
| **① 市場預測** | as-of → 特徵 → 宇宙 → 模型 → 日更名單／經濟尺 | `ingestion`／`features`／`universe`／`models`／`evaluation`／日更殼 | **r19 執行板** |
| **② 知識素養＋顧問** | 可溯源文件／公開源／自有私有；誠實檢索與作答 | `knowledge`／`philosophy`／`advisor`；`:8500`／`:8090`／`:8399` | **KH 20260813 板**（本輪未改選刀） |
| **③ 自反／演化** | 預註冊實驗、擂台、判準凍結、演化候選 | `arena`／`evolution`／`deliberation`／`audit` | 分屬兩板之凍結／實驗列；**互不等待** |
| **①b 路徑／進出研究** | 長窗定方向、短窗管進出；dry-run 探針 | `evaluation/{uptrend_pullback,twin_ex,charge_t5,bull5,trend_pullback_catalog}`＋`scripts/probe_*` | **PATH-OPT 操作手冊**（從屬 r19 開工順序） |

封閉迴路（優化節奏的脊椎，不是一次勾完的 checklist）：

```text
真實價／基本面／資金流（S1）
  → 知識／KH（S2）          ← 與市場日更分軌；共享最多是 LLM 鎖
    → 特徵／prodset（S3）
      → 模型族 train／serve（S4）
        → 日更預測／方向／經濟尺／顧問／模擬（S5）
  ↺ S5 證據回饋 S4／S3／S2
```

r16 把這條迴路收成可重複的心跳，本輪仍沿用：

```text
L0 取數（熱路徑）→ L1 出門（B3，預設 H20+H60）→ L2 邊界 A 重訓
RETRAIN-ALL 日更（8 族 × 8 窗＋方向臂；明確不 emit B3）
歷史 as-of 重覆驗（D ≤ 價頂；≠ 假今天）
```

| 它是 | 它不是 |
|---|---|
| as-of 凍結、walk-forward、多 seed、經濟終關 | 保證獲利／點位神算／自動下單 |
| 相對排序為生產熱路徑；方向屬可證偽實驗 | AI 代簽「已確立／可交易」 |
| Sole Steward；plan-first；AI self-reported | 假兆補表、偷看未來、把單次極值當定論 |
| 庫內有原文就必須答得出來 | 把弱模型亂喊「無此內容」當成語料真缺 |
| RankRidge 分數＝相對排序單位 | 漲跌幅％、目標價、起漲時點 |
| `p_beat_median`＝勝中位機率 | 報酬率％ |
| `p_mkt`／`p_up`／OOS hit＝方向基率／命中 | 個股會漲幾％ |
| 八窗訓練閉集 | 八窗每天出門（須另雙明示改殼） |
| 路徑探針＝條件地圖 | 可交易、可空、可融券 |
| 兩檔格子＝研究尺 | 宇宙產品績效 |
| 無成本正報酬 | 扣成本後仍可做 |

成功定義＝**經濟價值**（淨效用／hit vs 基準，**含來回成本**）＋知識側**可核引文**；不是裸 IC、不是「圖好看」、不是「模型有回覆」、不是「覆蓋 64/64」、不是「兩檔複利很好看」。

### §2 倉庫地圖（讀檔導航）

| 區 | 作用 |
|---|---|
| `constitution/` · `specs/` | Layer 0–7 **[N]** 治權與規格（合倉）；入口 `GOVERNANCE-MAP.md` |
| `docs/` | 靈魂 v1.10.0／原則精華 v1.12.0／領域大憲章 v1.54.0 |
| `src/augur/` | **17 pkg**：預測 7pkg 與知識／顧問機械隔離（`audit/import_isolation`） |
| `scripts/` | 薄 CLI（sync／train／predict／B3／L2／RETRAIN-ALL／KIP／ingest／admin／探針…） |
| `reports/` | 計畫／理解 **[I]**（本系列） |
| `audits/` | GO／EXECUTED／ADOPTED／ARMED／ACK 留痕 **[I]** |
| `models_artifacts/` | joblib；挑戰族可在／STOP≠換冠；**不進 git** |
| PostgreSQL `augur` | **唯一系統記錄**（LIVE **63 GB**） |
| GitHub | `https://github.com/tsaitsangchi/augur` · HEAD `6341cab` · 工作樹**乾淨** · tag `archive-20260819-path-opt-charge-t5-ridge` |

**預測 7pkg（熱路徑，禁吸知識）**：`ingestion` · `features` · `universe` · `models` · `evaluation` · `catalog` · `audit`。`core` 共用基礎設施，同樣禁拼 RBAC／chat SQL。  
**知識旁軌**：`knowledge` · `philosophy` · `advisor` · `llm` · `identity`（知識 RBAC）。顧問可讀庫，**不得**把 KH 塞進特徵／預測權重（K10 C1 EXPAND＝另 GO、禁默加權 predict）。  
**其餘橫切**：`arena` · `evolution` · `deliberation` · `execution`。

**H 軌 SSOT（code）**：`src/augur/core/closed_horizons.py`

```text
H_TRACK = (5, 10, 20, 40, 60, 90, 120, 240)
H_MONTHLY_RANKS = (5, 10, 20, 40, 60, 90, 240)   # 無 120
CHECK_ANY = H_TRACK                              # 不准 82
```

- **H5**＝5 個交易日（2026-08-14 開）≠ Daily D 軌 k=5  
- **H10**＝10 個交易日（2026-08-16 開）≠ KH10（知識第 10 層，禁）  
- **H90**＝90 個交易日（2026-08-14 取代 H82；庫列已刪）  
- v2 K=4／arena／A3 **代碼**仍可能留歷史 H82 配方（不改 SHA）；**不得無新 GO 再插入庫列**

**截面 8 族（熱路徑冠軍＋挑戰）**：RankRidge（生產）＋ RankGBDT／XGB／Cat／RF／SVM／KNN／MLP。LIVE＠08-18 各 8 窗都在。  
**方向臂（另一軸）**：DailyLogit／DailyGBDT／DailyGBDT_cal；MktLogit×2；DirStackM×1。價頂鎖。  
**08-12 NF 六族**：EVIDENCE、**勿同尺重掃**；`--track other --apply`＝rc=6。

工具規則：`CLAUDE.md`（plan-first、真兆、經濟終關、預凍、回歸鎖、執行指令矩陣）。  
接續：`HANDOFF.md`（跨機；§4 多數段落過期，**現況以本檔 LIVE 為準**）。

### §3 S1→S5 × 硬邊界（運轉真相 · 08-19 14:05）

| 階 | 08-19 一句 |
|---|---|
| **S1** | 價頂＝**2026-08-18**；08-19＝假 B3；L0 熱路徑已採納（核 A＋TRI＋FRED） |
| **S2** | KH 分軌；ingest 穩態；KH8 **stop-at-7**；假 decline 閘在碼；item **286 339** |
| **S3** | tip 37 種＠08-18；核心 **286**；prodset active＝3；P6 校準 H20／H60 仍＠**08-14** |
| **S4** | 冠軍 **RankRidge**；8×8 COMPLETE＠08-18；方向臂在價頂；**no-promote**；NF-pause 續 |
| **S5** | **emit tip＝2026-08-17、僅 H20＋H60**；08-18 無 `prediction_values`／`prediction_probability`；H20＝dead、其餘 thin |
| **①b** | PATH-OPT P0 已採納；CHARGE-T5 宇宙扣成本 IS 負；可當進場＠Ridge 池＝0／10 |

硬邊界（雙軌都要守各自那一列）：

```text
市場: FZ/GATE-keep | skip-sync-B | no-SIM-apply | NF-pause
    | no-cron-B3 | 誠實 econ | no-promote 默認 | 勿重掃假綠 | no-fake-B3
    | p_beat／score／p_mkt／p_up ≠ 報酬％ | 八窗訓 ≠ 八窗出門
知識: FZ/GATE-keep(知識) | T0 no-web-dialog-approve | PDF-C-no-ASR
    | ASR=owned_local+local_private | no-KH10 | KH8-prod-stop-at-7
    | apply=opt-in | no-calendar-fake-evolve | 禁放寬θ／假 depth8
    | 有引文禁假「無此內容」
路徑: 觀察≠進場 | 條件≠可交易 | 兩檔≠宇宙 | 做空≠可空
    | 禁 OOS 最長持有當冠 | 不套樣單檔％ | 改θ＝新 ID
分軌: 市場不等 KH；KH 不等 tip／B3；augur_llm.lock＝互斥≠指揮
```

### §4 LIVE 錨（2026-08-19 ≈14:05+08 · 親查）

| 錨 | 值 |
|---|---|
| 日曆 | **2026-08-19 週三 14:05+08** |
| `TaiwanStockPriceAdj` max（TAIEX） | **2026-08-18**（`check_asof_ready --latest-date`） |
| `feature_values` max `panel_date` | **2026-08-18** · 特徵種類 **37** · 列 **27 958** |
| 核心宇宙＠08-18 | **286** 檔（＠08-17 曾 287） |
| asof_ready＠08-18 | **ready**（rc=0；has_core；pack_complete） |
| 假 B3＠08-19 | **是**（rc=3） |
| 截面 registry＠08-18 | **64／64**（8 族 × 8 窗） |
| 方向臂＠08-18 | DailyLogit／DailyGBDT／DailyGBDT_cal；MktLogit×2；DirStackM×1 |
| `prediction_values` max | **2026-08-17**（2 model_id · 574 列） |
| `prediction_probability` max | **2026-08-17** · 僅 horizon **20、60** · 各 287 列 |
| #14 | H20＝**dead**；H5／10／40／60／90／120／240＝**thin_unestablished** |
| Platt 校準器 | H20／60 最近 **08-14**；H40 有 08-04；H120 最近 **08-04**；H5／10／90／240 無 |
| `dgate_H_*` | H5／10／60／90／240＝**preregistered**；H20／40／120＝**evaluated_fail** |
| prodset active | `cycle_position_252d`／`inst_cumflow_position_120d`／`lending_fee_rate_mean_30d`（**3**） |
| `knowledge_item` | **286 339** |
| KH4 eligible | **146 338**（`knowledge_kh4_state.answer_status`） |
| DB size | **63 GB** |
| 服務 | admin **8500** · chat **8090** · advisor **8399** · ollama **11434** · postgres **5432** |
| crontab 列 | **17** 條非空非註解（含 RETRAIN-ALL 平日 21:40／09:20；**無** cron B3） |
| 封存點 | tag `archive-20260819-path-opt-charge-t5-ridge` · commit `ad7db10` · tip `6341cab` |
| git | `main...origin/main` · **clean** |
| 歷史截面未齊（示例） | 08-12 缺 32；08-11 缺 52；06-30 缺 52（補齊須另句 HIST-ASOF-apply） |

### §5 08-17→08-19 理解增量

| # | 增量 | 證據帳（示例） |
|---|---|---|
| 1 | B3 出門＠**08-17** H20+H60 EXECUTED | `OPS-B3-20260817-EXECUTED` |
| 2 | RETRAIN-ALL **force**＠08-17（8×8＋方向臂） | `RETRAIN-ALL-0817-FORCE-EXECUTED` |
| 3 | 價頂滾到 **08-18**；fv／core／pack 齊 | `check_asof_ready --date 2026-08-18` rc=0 |
| 4 | **未** B3 emit＠08-18（另句） | `prediction_*` max 仍 08-17 |
| 5 | HIST-ASOF＠08-07／08-13；H5 OOS walk 近 0；**H10 OOS 全 no_model**（日曆閘） | `HIST-ASOF-OOS-WALK-H10-EXECUTED` |
| 6 | PATH-OPT-OPS P0 採納 | `PATH-OPT-OPS-PLAN-ADOPTED` |
| 7 | UP-PULL／WATCH／BULL5／TWIN-EX／CHARGE-T5 P1＠08-18 已閉 | 各 `*-EXECUTED-20260819` |
| 8 | TREND-PB W1–W3＠08-18 已閉；W4／W5 另句 | 各 W*-EXECUTED |
| 9 | RS-CHARGE P0 採納；**P1 探針未寫**（`scripts/probe_rs_charge.py` 缺） | `RS-CHARGE-PLAN-ADOPTED` |
| 10 | CHARGE-T5 宇宙：無成本兩窗正；成本後 IS **−64.8%** | `CHARGE-T5-UNIVERSE-0818-EXECUTED` |
| 11 | RankRidge 八窗 dry＠08-18：286 齊；回撤序 Top10 可當進場 **0／10** | `RIDGE-THEN-PB-LONG-0818-EXECUTED` |
| 12 | 封存＋push GitHub | `ARCHIVE-20260819-PATH-OPT-CHARGE-T5-RIDGE` |
| 13 | **未變** | 確立級假不了；sim 禁 apply；NF／M／β5 凍結；Sole Steward；KH10 禁；未登入看不到私有；B3 standing＝20,60 |

**本輪最重要的兩本帳**：

1. **S4 已跟到價頂 08-18，S5 出門停在 08-17。** 與 r17 當時「訓到 08-14、出門停 08-13」同構。r16 把 RETRAIN-ALL 設計成「不 emit B3」是對的；優化時必須把「重訓」和「出門」當兩張工單。  
2. **路徑研究已經把「看起來像進場」拆成可證偽產品。** 兩檔偶爾做 ≠ 全宇宙幾乎天天換籃；扣成本後訓練窗可以翻負。這不是失敗隱瞞，這是產品邊界被量出來了。

### §6 知識入庫與作答熱路徑（繼承 r15／r17，本輪未改產品行為）

```text
瀏覽／上傳
  → ~/.augur_uploads/<token>/
    → acquire_local_files → fileparse.extract_text
         ├ PDF（± OCR；禁 ASR）
         ├ Office／PPT／圖／文字
         └ AV → faster-whisper（owned_local+private only）
      → sha1 冪等 ingest → KIP（句→嵌→kh4→admit≤9）
        → retrieve_all ∥ readout（標題／檔名.ext＋問句）
          → compact freeze → 本機 LLM → guard／抛光
            → FillAuto 欄位=值閘
            → 假 decline 閘（有 item 引文禁閉集句 → 有界摘錄）
```

命門不變：抽字≠AI 改寫；owned_local⇒local_private；PDF-C ≠ AVI-ASR；未登入看不到私有；有引文禁假「無此內容」；空包不進化。  
殘債：Doc1 純圖 hold；`.msg`／`.rar` skip；K9 他域 FT 未授；KH8 θ 未過（禁放寬）。

### §7 模型／特徵／路徑誠實結論（刷新）

| 結論 | 含義 |
|---|---|
| 冠軍仍深 | 熱路徑仍 **RankRidge**；L2／RETRAIN-ALL 可跟價重訓，**≠**換樹／序列／GNN |
| 訓到價頂 ≠ 出門到價頂 | 08-18 COMPLETE；emit 仍 08-17 兩窗 |
| 八窗可訓 ≠ 八窗該出門 | standing 改殼須雙明示 |
| tip≠經濟綠 | H20 **dead**、其餘 **thin**——**不塗綠** |
| 有證據≠可升格 | NF＠0812 六族 EVIDENCE 全部 **no-promote**；殘格須點名；**勿重掃** |
| 方向閘草稿≠已過門 | `dgate_H_5/10/60/90/240` 禁 evaluate／approve（無新 GO） |
| 校準器落後 | P6 H20／H60 凍＠08-14；包已＠08-18；H5／10／90／240 無 Platt |
| 相對分數看板 | 確定性表、免 LLM；**勿把 score／p_beat 讀成報酬％** |
| 兩檔正 ≠ 宇宙正 | TWIN-EX E-charge×T5 在 3017／2395 上兩窗同號；CHARGE-T5 宇宙扣成本 IS 負 |
| 觀察 ≠ 進場 | Ridge 均分 Top10 回撤序：可當進場 0／10 |
| 週轉是產品 | 幾乎每日等權 k=10 籃，成本地板 0.585% 會吃光毛利；降週轉＝新 ID |
| 下一進化常不是新族 | **補齊心跳（出門）＋誠實尺＋知識可用＋有界提拔**＞假掃族表＞把探針當 live |
| prodset | active 仍 **3**；極窄；≠可交易 |

### §8 綜合債表（r19）

| ID | 債 | 狀態 |
|---|---|---|
| **R19-01** | L1 B3 出門＠價頂 **08-18**（20,60）尚未 EXECUTED | 🟡 **市場主軸缺口**（合法、須 GO） |
| **R19-02** | 下一真交易日心跳＠**≥08-19 收盤**（此刻無價） | 🟡 WAIT · 禁假跑 |
| R19-03 | econ／dgate 誠實形 | 🟢 形已誠實 · 禁修綠 |
| R19-04 | standing 八窗永久化 | ❄ 須另雙明示改殼 |
| R19-05 | P6／長窗校準與 08-18 artifact 對齊 | 🟡 文件可先；訓另 GO（缺口 08-14 vs 包 08-18） |
| R19-06 | 圖提拔／熱路徑 | 🔴 另 VERIFY |
| R19-07 | 升格挑戰族 | ❄ 另軌 · 禁默 |
| R19-08 | NF 新族／殘格（VECM／TCN／NB／Daily*／RL） | ❄ pause · 點名才開 · 勿重掃已閉 |
| R19-09 | STRUCT／scripts 冗餘；循環依賴文件 | 🔴 低優先 |
| R19-10 | M／β5／sim／Dividend | ❄／禁 |
| R19-11 | 10–14 治權日曆 | 🟡 排程 · **不因本檔假關** |
| R19-12 | Writer／純圖 Doc1；OLE 殘 | 🟡 hold |
| R19-13 | `.msg`／`.rar` | 🔴 skip-hold |
| R19-14 | 私有／ASR 覆蓋回歸 | 🟡 抽樣已綠；持續 |
| R19-15 | tip＋N 日實現報酬；E4b 鐘 | 🔴 鐘 WAIT k=0；next＝**2026-11-13** |
| R19-16 | KH8 discrim θ／depth8 | ❄ E-keep · 禁放寬 θ |
| R19-17 | K9 他域 FT | 🔴 plan-only · 未訓 |
| R19-18 | K10 C1→feat | 🔴 隔離 · 另 GO |
| R19-19 | AUTO-LIFT 抬 >KH2 | 禁 |
| R19-20 | 工作樹入倉 | 🟢 已封存 20260819 |
| R19-21 | `dgate_H_*` draft／fail | 禁 evaluate／approve（無新 GO） |
| R19-22 | HANDOFF.md §4 多數過期 | 🟡 接續以本檔 LIVE 為準 |
| R19-23 | PME map 缺／unmapped | 🟡 診斷已出；APPLY／降閾禁 |
| R19-24 | #14 確立路徑 | 🟡 E4 就緒 5 耗盡；E5 禁；鐘 WAIT |
| R19-25 | PATH-OPT 未閉槍 | 🟡 RS-CHARGE P1、TREND-PB W4／W5、各 OOS walk、UP-PULL emit 皆**另句** |
| R19-26 | CHARGE-T5 宇宙成本失敗 | 🟢 已量出；≠可交易；降週轉須新 ID |
| R19-27 | HIST 未齊日（08-12 等） | 🟡 另句 `HIST-ASOF-apply`；無實現窗勿 `--ic` |

---

## 第二部｜優化計畫（選刀對齊）

> **後續優化執行 SSOT**＝`reports/augur_opt_stepwise_all_problems_r19_20260819.md`。  
> 閉環怎麼轉仍＝r16（L0→L1→L2＋歷史 as-of＋知識分軌）。路徑族怎麼一槍一槍做＝PATH-OPT 手冊。本檔刷新「轉到哪裡了、下一槍是哪把」。

### §9 讀序與操作協議

```text
人話憲章 r19
  → 本檔理解（第一部）
    → 執行板 r19
      → 問市場細節 → r16 心跳／as-of 刀
      → 問路徑進出 → PATH-OPT 手冊／各軌長板
      → 問知識細節 → KH 20260813 導航
日更: skip-sync-B · no-SIM-apply · 誠實 econ · 不假 B3
知識: owned_local ASR · PDF-C no-ASR · 登入才私有 · 有引文禁假無
路徑: 觀察≠進場 · 兩檔≠宇宙 · 扣成本才算
分軌: 不互等、不互擋
```

1. 選刀＝執行板 `#` 或 Phase 步。  
2. 缺 GO → 停、問 Steward；禁默訓／默升格／默開 NF／默抬 KH8／默改 standing／默把探針接 live。  
3. **勿重掃假綠**；已 STOP／已 EVIDENCE 族同尺不刷。  
4. 重大收斂 → 刷新執行板，不必每次重寫理解長文。

### §10 最佳下一步（摘要）

此刻（週三午後）**沒有** 08-19 價。市場主軸有兩把**都合法、互不預設**的刀，須 Steward 選：

| 角色 | 內容 |
|---|---|
| **刀 A · 補出門** | L1 B3＠**2026-08-18** `horizons=20,60`（價／特徵／核心／冠軍 artifact 已齊；**emit 缺口**）。不 promote、不改八窗 standing、不 evaluate dgate |
| **刀 B · 等新價** | hold 至 `PriceAdj≥2026-08-19`（收盤進庫後）→ L0（若需要）→ B3 20,60 → L2／RETRAIN-ALL（包未齊才訓） |
| **路徑（可另句，不混日更）** | `RS-CHARGE-probe-go` 或 `TREND-PB-W4-go`；一次一槍；dry-run |
| **KH 主軸** | **守穩態**：`--check`；**不**開 K9／K8 depth8／放寬 θ |
| **可∥** | 誠實 #14 披露；凍結輕監；KH ingest 巡檢（不搶 LLM 重活） |
| **禁** | 假 B3＠08-19；sim-apply；塗綠 dgate；默改八窗出門；SERVE-SWAP；把 CHARGE-T5／兩檔％當可交易；用 tip 擋 KH |

```text
market: no-fake-B3@08-19 | emit-gap@08-18 | wait≥08-19-close
      | standing=20,60 | H_TRACK=8 | NF-pause | no-promote
path:   觀察≠進場 | 兩檔≠宇宙 | CHARGE-T5≠可交易
kh:     check-green | E-keep | stop-at-7 | no-K9-train | no-relax-θ
```

建議（人話，非代裁）：若你在乎「看板／顧問讀到的名單跟已訓模型同一天」→ 選刀 A；若你在乎「只對最新交易日心跳、盤中不補舊名單」→ 選刀 B。**兩把都不要在 14:05 假裝 08-19 已收盤。** 路徑槍不要混進這兩把。

### §11 驗收

- [x] 產品／三軸＋路徑旁軌／雙軌／地圖／S1–S5／LIVE／增量／知識熱路徑／模型＋路徑結論／債表  
- [x] 選刀對齊 r19 執行板；人話憲章成對  
- [x] 覆蓋誠實聲明（非整庫逐檔）  
- [x] 不創 [N]、不解凍、不開訓、不假 B3、不把探針當 live  

*完。[I] · self-reported · r19。*
