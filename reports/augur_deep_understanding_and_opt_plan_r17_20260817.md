---
title: augur 深化理解＋專案優化地基（合併）r17
status: final
series: deep_understanding_and_opt
round: r17
date: 2026-08-17
viewpoint: 2026-08-17T08:10+08:00
layer: "[I]"
role: 後續優化地基（理解＋對齊雙軌選刀）；刷新 r15；市場選刀以 r18 執行板為準
supersedes_as_understanding:
  - reports/augur_deep_understanding_and_opt_plan_r15_20260813.md
inherits_understanding:
  - reports/augur_deep_understanding_and_opt_plan_r15_20260813.md
  - reports/augur_deep_understanding_and_opt_plan_r14_20260811.md
  - reports/augur_deep_understanding_and_opt_plan_r13_20260808.md
companion_plain_charter: reports/augur_project_charter_plain_zh_r17_20260817.md
exec_nav: reports/augur_opt_stepwise_all_problems_r18_20260817.md
exec_nav_superseded: reports/augur_opt_stepwise_all_problems_r17_20260817.md
s1_s5_ssot: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_r16_20260813.md
s1_s5_parent: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md
kh_evolve_ssot: reports/augur_local_ai_kh_loop_evolve_opt_plan_20260806_readout.md
archive_tip: archive-20260814-weekly-fd-tar
self_reported: true
---

# augur 深化理解＋專案優化地基 r17（2026-08-17）

> **性質**：[I]；**不創** [N]；不解凍；不 sim `--apply`；不假關確立級；**勿重掃假綠**；不假 B3＠08-15／16／17。  
> **一句**：在 r15／r16 上吸收 **08-13→08-17** 增量——H 軌收成八窗、跟價重訓到 08-14、日常出門仍停在 08-13 兩窗——收成**下一段優化地基**。  
> **疊用**：人話憲章 r17 → **本檔理解** → **全專案逐步執行** `reports/augur_opt_stepwise_all_problems_r18_20260817.md`（r17 執行板已 supersede）→ 准否／驗收＝S1→S5 運轉契約 r16＋KH evolve＋ARCHIVE／standing／audit。  
> **LIVE 過期註**：本檔 08:10 視點仍寫「出門停在 08-13」。r18 親查 10:13：emit 已＝**2026-08-14** H20+H60。開工順序以 r18 為準。  
> **覆蓋誠實**：非整庫逐檔複讀。倉內約 **146** 支 `src/augur` Python、**399** 支 `scripts/`、**496** 份 `reports/`、**940** 份 `audits/`、**59** 份 `constitution/`、**14** 份 `specs/`、**30** 份 `tests/`。本輪＝**結構地圖＋LIVE 親查＋08-13→08-17 收斂＋雙軌治權**；長細節仍回 r15／r16／INVENTORY／治權檔。

---

## 第一部｜深化理解

### §1 專案是什麼（產品真相）

**Augur**＝古羅馬「觀兆者」；「兆」只能是**真實觀測**，「預言」只能是**帶不確定性的相對排序／機率**。

一句話產品：

> **只用真資料，誠實判斷台股誰比較強、知識庫裡到底寫了什麼；說得出依據，也說得出什麼時候該閉嘴。**

它同時承載**三條軸**（領域大憲章 v1.54.0 已對齊；**08-12 起市場與知識的日常選刀再拆成兩塊獨立導航**）：

| 軸 | 白話 | 倉內主落點 | 日常選刀 |
|---|---|---|---|
| **① 市場預測** | as-of → 特徵 → 宇宙 → 模型 → 日更名單／經濟尺 | `ingestion`／`features`／`universe`／`models`／`evaluation`／日更殼 | **r17 執行板** |
| **② 知識素養＋顧問** | 可溯源文件／公開源／自有私有；誠實檢索與作答 | `knowledge`／`philosophy`／`advisor`；`:8500`／`:8090`／`:8399` | **KH 20260813 板**（本輪未改選刀） |
| **③ 自反／演化** | 預註冊實驗、擂台、判準凍結、演化候選 | `arena`／`evolution`／`deliberation`／`audit` | 分屬兩板之凍結／實驗列；**互不等待** |

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

成功定義＝**經濟價值**（淨效用／hit vs 基準）＋知識側**可核引文**；不是裸 IC、不是「圖好看」、不是「模型有回覆」、不是「覆蓋 64/64」。

### §2 倉庫地圖（讀檔導航）

| 區 | 作用 |
|---|---|
| `constitution/` · `specs/` | Layer 0–7 **[N]** 治權與規格（合倉）；入口 `GOVERNANCE-MAP.md` |
| `docs/` | 靈魂 v1.10.0／原則精華 v1.12.0／領域大憲章 v1.54.0 |
| `src/augur/` | **17 pkg**：預測 7pkg 與知識／顧問機械隔離（`audit/import_isolation`） |
| `scripts/` | 薄 CLI（sync／train／predict／B3／L2／RETRAIN-ALL／KIP／ingest／admin／探針…） |
| `reports/` | 計畫／理解 **[I]**（本系列） |
| `audits/` | GO／EXECUTED／ADOPTED／ARMED／ACK 留痕 **[I]** |
| `models_artifacts/` | joblib；挑戰族可在／STOP≠換冠 |
| PostgreSQL `augur` | **唯一系統記錄**（LIVE **63.3 GB**） |
| GitHub | `https://github.com/tsaitsangchi/augur` · HEAD `455f50f` · 工作樹**不乾淨**（H5／H10 碼與帳未入倉） |

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

工具規則：`CLAUDE.md`（plan-first、真兆、經濟終關、預凍、回歸鎖、執行指令矩陣）。  
接續：`HANDOFF.md`（跨機；§4 多數段落過期，**現況以本檔 LIVE 為準**）。

### §3 S1→S5 × 硬邊界（運轉真相 · 08-17 08:10）

| 階 | 08-17 一句 |
|---|---|
| **S1** | 價頂＝**2026-08-14**；08-15／16／17＝假 B3；L0 熱路徑已採納（核 A＋TRI＋FRED） |
| **S2** | KH 分軌；ingest 穩態；KH8 **stop-at-7**；假 decline 閘在碼 |
| **S3** | tip 37 種＠08-14；核心 286；prodset active＝3；P6 校準仍＠**08-04／08-07** |
| **S4** | 冠軍 **RankRidge**；8×8 COMPLETE＠08-14；**no-promote**；NF-pause 續 |
| **S5** | **emit tip＝2026-08-13、僅 H20＋H60**；08-14 無 `prediction_values`／`prediction_probability`；H20＝dead、其餘 thin |

硬邊界（雙軌都要守各自那一列）：

```text
市場: FZ/GATE-keep | skip-sync-B | no-SIM-apply | NF-pause
    | no-cron-B3 | 誠實 econ | no-promote 默認 | 勿重掃假綠 | no-fake-B3
    | p_beat／score／p_mkt／p_up ≠ 報酬％ | 八窗訓 ≠ 八窗出門
知識: FZ/GATE-keep(知識) | T0 no-web-dialog-approve | PDF-C-no-ASR
    | ASR=owned_local+local_private | no-KH10 | KH8-prod-stop-at-7
    | apply=opt-in | no-calendar-fake-evolve | 禁放寬θ／假 depth8
    | 有引文禁假「無此內容」
分軌: 市場不等 KH；KH 不等 tip／B3；augur_llm.lock＝互斥≠指揮
```

### §4 LIVE 錨（2026-08-17 ≈08:10+08 · 親查）

| 錨 | 值 |
|---|---|
| 日曆 | **2026-08-17 週一 08:10+08**（開盤前） |
| `TaiwanStockPriceAdj` max（TAIEX） | **2026-08-14** |
| `feature_values` max `panel_date` | **2026-08-14** · 特徵種類 **37** · 列 **27 958** |
| 核心宇宙＠08-14 | **286** 檔 |
| asof_ready＠08-14 | **ready**（rc=0；has_core） |
| 假 B3＠08-15／16／17 | **是**（價頂 08-14） |
| 截面 registry＠08-14 | **64／64**（8 族 × 8 窗） |
| 方向臂＠08-14 | DailyLogit／DailyGBDT／DailyGBDT_cal；MktLogit×2；DirStackM×1 |
| `prediction_values` max | **2026-08-13**（1144 列） |
| `prediction_probability` max | **2026-08-13** · 僅 horizon **20、60** |
| #14 | H20＝**dead**；H5／10／40／60／90／120／240＝**thin_unestablished** |
| Platt 校準器 | 僅 H20／40／60／120（fit 錨 08-04／08-07） |
| `dgate_H_*` | H5／10／60／90／240＝**preregistered**；H20／40／120＝**evaluated_fail** |
| prodset active | `cycle_position_252d`／`inst_cumflow_position_120d`／`lending_fee_rate_mean_30d`（**3**） |
| `knowledge_item` | **286 271** |
| KH4 eligible | **146 338** |
| DB size | **63.3 GB** |
| 服務 | admin **8500** · chat **8090** · advisor **8399**（`/`→404 正常）· ollama **11434** |
| crontab 列 | **17** |
| 封存點 | tag `archive-20260814-weekly-fd-tar` |
| dump SSOT | `~/db_dumps/augur_20260814_weekly_Fd` |
| git | `455f50f` · `main...origin/main` · **dirty**（H 軌開窗／重訓殼未提交） |

### §5 08-13→08-17 理解增量

| # | 增量 | 證據帳（示例） |
|---|---|---|
| 1 | B3＋L2＠**08-13** EXECUTED（standing 仍 20,60） | `OPS-B3-20260813-EXECUTED` · `OPS-DAILY-0813-EXECUTED` |
| 2 | L0 熱路徑計畫＋arena 20:00 改核 A＋TRI＋FRED | `L0-HOTPATH-PREDICT-DAILY-ADOPTED` |
| 3 | H90 取代 H82；庫列刪；CHECK 不准 82 | `H90-REPLACE-H82-EXECUTED` |
| 4 | H5 開窗（≠ Daily k=5） | `H5-OPEN-EXECUTED` |
| 5 | H240 開窗＋跟價重訓＠08-13 | `RETRAIN-ALL-ASOF-0813-H240-EXECUTED` |
| 6 | RETRAIN-ALL 日更 cron 採納（不 emit B3） | `RETRAIN-ALL-ASOF-DAILY-CRON-ADOPTED` |
| 7 | 全量重訓＠**08-14**（當時 7 窗）再加 H10 成 **8×8 COMPLETE 64/64** | `RETRAIN-ALL-ASOF-0814-EXECUTED` · `RETRAIN-ALL-ASOF-0814-H10-EXECUTED` |
| 8 | H10 開窗（≠ KH10）；`dgate_H_10` draft | `H10-OPEN-EXECUTED` |
| 9 | RankRidge＠08-14 八窗相對強弱條列（dry；未寫 `prediction_values`） | 會話產物；分數≠漲跌幅％ |
| 10 | PME 閘診斷＠08-14：mapped 36／missing 14；PASS×PASS＝4 | `augur_pme_gate_diagnosis_20260814.md` |
| 11 | **未變** | 確立級假不了；sim 禁 apply；NF／M／β5 凍結；Sole Steward；KH10 禁；未登入看不到私有；B3 standing＝20,60 |

**本輪最重要的帳**：S4 已跟到價頂，S5 出門沒跟到。r16 心跳把 RETRAIN-ALL 設計成「不 emit B3」是對的（避免兩套出門搶寫）；但站式 L1＠08-14 **沒有對應 OPS-B3 EXECUTED**。優化時必須把「重訓」和「出門」當兩張工單。

### §6 知識入庫與作答熱路徑（繼承 r15，本輪未改產品行為）

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

### §7 模型／特徵誠實結論（刷新）

| 結論 | 含義 |
|---|---|
| 冠軍仍深 | 熱路徑仍 **RankRidge**；L2／RETRAIN-ALL 可跟價重訓，**≠**換樹／序列／GNN |
| 訓到價頂 ≠ 出門到價頂 | 08-14 COMPLETE；emit 仍 08-13 兩窗 |
| 八窗可訓 ≠ 八窗該出門 | standing 改殼須雙明示 |
| tip≠經濟綠 | H20 **dead**、其餘 **thin**——**不塗綠** |
| 有證據≠可升格 | NF＠0812 六族 EVIDENCE 全部 **no-promote**；殘格須點名；**勿重掃** |
| 方向閘草稿≠已過門 | `dgate_H_5/10/60/90/240` 禁 evaluate／approve（無新 GO） |
| 校準器落後 | P6 未對齊 08-14；H5／10／90／240 無 Platt |
| 相對分數看板 | 確定性表、免 LLM；**勿把 score／p_beat 讀成報酬％** |
| 下一進化常不是新族 | **補齊心跳（出門）＋誠實尺＋知識可用＋有界提拔**＞假掃族表 |
| prodset | active 從歷史「2」長到 **3**；仍極窄；≠可交易 |

### §8 綜合債表（r17）

| ID | 債 | 狀態 |
|---|---|---|
| R17-01 | L1 B3 出門＠價頂 **08-14**（20,60）尚未 EXECUTED | 🟡 **市場主軸缺口**（合法、須 GO） |
| R17-02 | 下一真交易日心跳＠**≥08-17 收盤**（此刻無價） | 🟡 WAIT · 禁假跑 |
| R17-03 | econ／dgate 誠實形 | 🟡 不修綠 · ∥ |
| R17-04 | standing 八窗永久化 | ❄ 須另雙明示改殼 |
| R17-05 | P6／長窗校準與 08-14 artifact 對齊 | 🟡 閒時文件；訓另 GO |
| R17-06 | 圖提拔／熱路徑 | 🔴 另 VERIFY |
| R17-07 | 升格挑戰族 | ❄ 另軌 · 禁默 |
| R17-08 | NF 新族／殘格（VECM／TCN／NB／Daily*／RL） | ❄ pause · 點名才開 · 勿重掃已閉 |
| R17-09 | STRUCT／scripts 冗餘 | 🔴 低優先 |
| R17-10 | M／β5／sim／Dividend | ❄ |
| R17-11 | 10–14 治權日曆 | 🟡 排程 · **不因本檔假關** |
| R17-12 | Writer／純圖 Doc1；OLE 殘 | 🟡 hold |
| R17-13 | `.msg`／`.rar` | 🔴 skip-hold |
| R17-14 | 私有／ASR 覆蓋回歸 | 🟡 抽樣已綠；持續 |
| R17-15 | tip＋N 日實現報酬研究 | 🔴 等價蓋過 tip＋N（08-14 起算尚未滿 5 交易日） |
| R17-16 | KH8 discrim θ／depth8 | ❄ E-keep · 禁放寬 θ |
| R17-17 | K9 他域 FT | 🔴 plan-only · 未訓 |
| R17-18 | K10 C1→feat | 🔴 隔離 · 另 GO |
| R17-19 | AUTO-LIFT 抬 >KH2 | 禁 |
| R17-20 | H5／H10／八窗殼 **工作樹未入倉** | 🟡 另句才 commit／push |
| R17-21 | `dgate_H_*` draft／fail | 禁 evaluate／approve（無新 GO） |
| R17-22 | HANDOFF.md §4 多數過期 | 🟡 接續以本檔 LIVE 為準；整段重寫另計畫 |
| R17-23 | PME map 缺 14／unmapped `margin_usage_ratio` | 🟡 診斷已出；APPLY／降閾禁 |

---

## 第二部｜優化計畫（選刀對齊）

> **後續優化執行 SSOT**＝`reports/augur_opt_stepwise_all_problems_r18_20260817.md`。  
> 閉環怎麼轉仍＝r16（L0→L1→L2＋歷史 as-of＋知識分軌）。本檔刷新「轉到哪裡了、下一槍是哪把」。

### §9 讀序與操作協議

```text
人話憲章 r17
  → 本檔理解（第一部）
    → 執行板 r18
      → 問市場細節 → r15 市場長板／r16 心跳
      → 問知識細節 → KH 20260813 導航
日更: skip-sync-B · no-SIM-apply · 誠實 econ · 不假 B3
知識: owned_local ASR · PDF-C no-ASR · 登入才私有 · 有引文禁假無
分軌: 不互等、不互擋
```

1. 選刀＝執行板 `#` 或 Phase 步。  
2. 缺 GO → 停、問 Steward；禁默訓／默升格／默開 NF／默抬 KH8／默改 standing。  
3. **勿重掃假綠**；已 STOP／已 EVIDENCE 族同尺不刷。  
4. 重大收斂 → 刷新執行板，不必每次重寫理解長文。

### §10 最佳下一步（摘要）

此刻（週一開盤前）**沒有** 08-17 價。市場主軸有兩把**都合法、互不預設**的刀，須 Steward 選：

| 角色 | 內容 |
|---|---|
| **刀 A · 補出門** | L1 B3＠**2026-08-14** `horizons=20,60`（價／特徵／核心／冠軍 artifact 已齊；**emit 缺口**）。不 promote、不改八窗 standing、不 evaluate dgate |
| **刀 B · 等新價** | hold 至 `PriceAdj≥2026-08-17` → L0（若需要）→ B3 20,60 → L2／RETRAIN-ALL（包未齊才訓） |
| **KH 主軸** | **守穩態**：`--check`；**不**開 K9／K8 depth8／放寬 θ |
| **可∥** | 誠實 #14 披露；凍結輕監；KH ingest 巡檢（不搶 LLM 重活） |
| **可先（閒時）** | R17-20 入倉清單（**另句才 commit**）；P6 對帳文件；升格門檻文件 |
| **禁** | 假 B3＠08-15／16／17；sim-apply；塗綠 dgate；默改八窗出門；SERVE-SWAP；ASR→PDF-C；用 tip 擋 KH；整庫回填當「有內容」；把 08-14 相對分數說成「從今天起漲」 |

```text
market: no-fake-B3@08-15/16/17 | emit-gap@08-14 | wait≥08-17-close
      | standing=20,60 | H_TRACK=8 | NF-pause | no-promote
kh:     check-green | E-keep | stop-at-7 | no-K9-train | no-relax-θ
```

建議（人話，非代裁）：若你在乎「看板／顧問讀到的名單跟已訓模型同一天」→ 選刀 A；若你在乎「只對最新交易日心跳、週末不補舊名單」→ 選刀 B。**兩把都不要在 08:10 假裝 08-17 已收盤。**

### §11 驗收

- [x] 產品／三軸／雙軌／地圖／S1–S5／LIVE／增量／知識熱路徑／模型結論／債表  
- [x] 選刀對齊 r17 執行板；人話憲章成對  
- [x] 覆蓋誠實聲明（非整庫逐檔）  
- [x] 不創 [N]、不解凍、不開訓、不假 B3、不 commit  

*完。[I] · self-reported · r17。*
