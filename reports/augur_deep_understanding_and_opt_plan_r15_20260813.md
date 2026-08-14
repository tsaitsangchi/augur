---
title: augur 深化理解＋專案優化地基（合併）r15
status: final
series: deep_understanding_and_opt
round: r15
date: 2026-08-13
viewpoint: 2026-08-13T11:49+08:00
layer: "[I]"
role: 後續優化地基（理解＋對齊雙軌選刀）；刷新 r14；市場選刀以 r15 導航為準、KH 選刀以外置專檔為準
supersedes_as_understanding:
  - reports/augur_deep_understanding_and_opt_plan_r14_20260811.md
inherits_understanding:
  - reports/augur_deep_understanding_and_opt_plan_r14_20260811.md
  - reports/augur_deep_understanding_and_opt_plan_r13_20260808.md
  - reports/augur_deep_understanding_and_opt_plan_r11_20260807.md
companion_plain_charter: reports/augur_project_charter_plain_zh_r15_20260813.md
exec_nav: reports/augur_opt_stepwise_all_problems_r15_20260813.md
exec_nav_market: reports/augur_opt_stepwise_best_next_plan_r15_20260813.md
exec_nav_kh: reports/augur_kh_opt_stepwise_best_next_plan_20260813.md
s1_s5_ssot: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_r16_20260813.md
s1_s5_parent: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md
kh_evolve_ssot: reports/augur_local_ai_kh_loop_evolve_opt_plan_20260806_readout.md
archive_tip: archive-20260814-h240-retrain-0813
prior_archive: archive-20260814-l0-retrain-r16-b3-0813
self_reported: true
---

# augur 深化理解＋專案優化地基 r15（2026-08-13）

> **性質**：[I]；**不創** [N]；不解凍；不 sim `--apply`；不假關確立級；**勿重掃假綠**。  
> **一句**：在 r14 上吸收 **08-11→08-13** 增量——**市場／知識徹底分軌**、B3＋L2＠0812、NF＠0812 有界收口、KH 閉環 K0–K15＋A2-L3（誠實未過 θ）、假「無此內容」機器閘——收成**下一段優化地基**。  
> **疊用**：人話憲章 r15 → **本檔理解** → **全專案逐步執行** `reports/augur_opt_stepwise_all_problems_r15_20260813.md`（後續優化 SSOT）→ 長板市場／KH（細節）→ 准否／驗收＝S1→S5 SSOT＋KH evolve＋ARCHIVE／standing／audit。  
> **覆蓋誠實**：非整庫逐檔複讀。倉內約 **144** 支 `src/augur` Python、**382** 支 `scripts/`、**485** 份 `reports/`、**876** 份 `audits/`、**59** 份 `constitution/`。本輪＝**結構地圖＋LIVE 親查＋08-11→08-13 收斂＋雙軌治權＋知識假 decline 熱路徑**；長細節仍回 r6／r8／r11／r13／r14／INVENTORY。

---

## 第一部｜深化理解

### §1 專案是什麼（產品真相）

**Augur**＝古羅馬「觀兆者」；「兆」只能是**真實觀測**，「預言」只能是**帶不確定性的相對排序／機率**。

一句話產品：

> **只用真資料，誠實判斷台股誰比較強、知識庫裡到底寫了什麼；說得出依據，也說得出什麼時候該閉嘴。**

它同時承載**三條軸**（領域大憲章 v1.54.0 已對齊；**08-12 起市場與知識的日常選刀再拆成兩塊獨立導航**）：

| 軸 | 白話 | 倉內主落點 | 日常選刀 |
|---|---|---|---|
| **① 市場預測** | as-of → 特徵 → 宇宙 → 模型 → 日更名單／經濟尺 | `ingestion`／`features`／`universe`／`models`／`evaluation`／日更殼 | **r15 市場板** |
| **② 知識素養＋顧問** | 可溯源文件／公開源／自有私有；誠實檢索與作答 | `knowledge`／`philosophy`／`advisor`；`:8500`／`:8090`／`:8399` | **KH 20260813 板** |
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

| 它是 | 它不是 |
|---|---|
| as-of 凍結、walk-forward、多 seed、經濟終關 | 保證獲利／點位神算／自動下單 |
| 相對排序為生產熱路徑；方向屬可證偽實驗 | AI 代簽「已確立／可交易」 |
| Sole Steward；plan-first；AI self-reported | 假兆補表、偷看未來、把單次極值當定論 |
| 庫內有原文就必須答得出來 | 把弱模型亂喊「無此內容」當成語料真缺 |
| `p_beat_median`＝相對機率 | 報酬率％、目標價、保證漲跌 |

成功定義＝**經濟價值**（淨效用／hit vs 基準）＋知識側**可核引文**；不是裸 IC、不是「圖好看」、不是「模型有回覆」。

### §2 倉庫地圖（讀檔導航）

| 區 | 作用 |
|---|---|
| `constitution/` · `specs/` | Layer 0–7 **[N]** 治權與規格（合倉）；入口 `GOVERNANCE-MAP.md` |
| `docs/` | 靈魂 v1.10.0／原則精華 v1.12.0／領域大憲章 v1.54.0 |
| `src/augur/` | **17 pkg**：預測 7pkg 與知識／顧問機械隔離（`audit/import_isolation` 本輪自測通過） |
| `scripts/` | 薄 CLI（sync／train／predict／B3／L2／KIP／ingest／admin／探針…） |
| `reports/` | 計畫／理解 **[I]**（本系列） |
| `audits/` | GO／EXECUTED／ADOPTED／ARMED／ACK 留痕 **[I]** |
| `models_artifacts/` | joblib；挑戰族可在／STOP≠換冠 |
| PostgreSQL `augur` | **唯一系統記錄**（LIVE **63 GB**） |
| GitHub | `https://github.com/tsaitsangchi/augur` · tip `5f342f8` · tag 見 §4 |

**預測 7pkg（熱路徑，禁吸知識）**：`ingestion` · `features` · `universe` · `models` · `evaluation` · `catalog` · `audit`。`core` 共用基礎設施，同樣禁拼 RBAC／chat SQL。  
**知識旁軌**：`knowledge` · `philosophy` · `advisor` · `llm` · `identity`（知識 RBAC）。顧問可讀庫，**不得**把 KH 塞進特徵／預測權重（K10 C1 EXPAND＝另 GO、禁默加權 predict）。  
**其餘橫切**：`arena` · `evolution` · `deliberation` · `execution`。

工具規則：`CLAUDE.md`（plan-first、真兆、經濟終關、預凍、回歸鎖、白名單三側同步、執行指令矩陣）。

### §3 S1→S5 × 硬邊界（運轉真相 · 08-13）

| 階 | 08-13 一句 |
|---|---|
| **S1** | 價到 D 才日更；**禁假 B3**；PriceAdj tip＝**2026-08-12**（尚無 ≥08-13） |
| **S2** | KH 分軌；ingest S0／S3 綠；FillAuto／ext-ask／假 decline 閘；KH8 **stop-at-7**、A2-L3 已寫仍 **disc=False** |
| **S3** | prodset 熱路徑穩；圖旁路可消費；**不**默入熱路徑；C1→feat **隔離** |
| **S4** | 冠軍 **RankRidge**；冰上 asof **08-12** ALL-RANK（`feats_hash=56d03625463b3eba`、**no-promote**）；NF＠0812 有界 EVIDENCE 後 **pause 續** |
| **S5** | tip＝**2026-08-12** 兩窗；H20＝**dead**、H60＝**thin_unestablished**；standing 預設仍 **20,60**；sim **禁 apply**；hold-#1 候 **tip≥08-13**（watcher ARMED） |

硬邊界（雙軌都要守各自那一列）：

```text
市場: FZ/GATE-keep | skip-sync-B | no-SIM-apply | NF-pause
    | no-cron-B3 | 誠實 econ | no-promote 默認 | 勿重掃假綠 | hold-#1 | no-fake-B3
知識: FZ/GATE-keep(知識) | T0 no-web-dialog-approve | PDF-C-no-ASR
    | ASR=owned_local+local_private | no-KH10 | KH8-prod-stop-at-7
    | apply=opt-in | no-calendar-fake-evolve | 禁放寬θ／假 depth8
    | 有引文禁假「無此內容」
分軌: 市場不等 KH；KH 不等 tip／B3；augur_llm.lock＝互斥≠指揮
```

### §4 LIVE 錨（2026-08-13 ≈11:49+08 · 親查）

| 錨 | 值 |
|---|---|
| 日曆 | **2026-08-13 四**（交易日；價尖仍 **08-12** → 候 08-13 價） |
| `TaiwanStockPriceAdj` max | **2026-08-12** |
| `feature_values` max `panel_date` | **2026-08-12** · 特徵種類 **37** |
| `prediction_probability` tip | **2026-08-12** · **H20＋H60**（各 568 列；含 08-11／08-12 兩代 artifact 並列） |
| #14＠tip | H20＝**dead**；H60＝**thin_unestablished** |
| 冠軍 artifact | `RankRidge_H{20,60}_2026-08-12_seed42_56d03625463b3eba` |
| A2B3 | **ARMED** watcher pid **230370**；log `/tmp/asof-ping-0813/watch.log`；11:45 ping 仍 `max=08-12 need=08-13`；截止 **23:50+08** |
| `knowledge_item` | **286,054** |
| KH4 eligible | **146,334** |
| ASR 入庫 | `asr_transcribe` **6** |
| DB size | **63 GB** |
| 服務 | admin **8500** · chat **8090** · advisor **8399**（假 decline 閘後已重載 8399） |
| 封存點 | tag `archive-20260813-b3-0812-kh-a2l3-nf0812` @ `5f342f8`（遠端已 push） |
| 封存後未提交 | 假 decline 閘（`compact_answer`／`advise`／`oai_compat`）＋兩則 KH-GENERO audit |

### §5 08-11→08-13 理解增量

| # | 增量 | 證據帳（示例） |
|---|---|---|
| 1 | **KH 退出市場主軸編排**（雙 SSOT） | `KH-SPLIT-FROM-MARKET-AXIS-ADOPTED` |
| 2 | B3＠**08-12** EXECUTED（H20 dead／H60 thin）；L2 ALL-RANK＠08-12 no-promote | `OPS-B3-20260812-EXECUTED` · `RETRAIN-ASOF-0812-ALL-RANK-EXECUTED` |
| 3 | 日更殼：L1 `run_daily_asof_predict.sh`；L2 `run_daily_retrain_l2_all_rank.sh` | `DAILY-RETRAIN-L2-*` |
| 4 | hold-#1 續候 **≥08-13**；A2B3 ARMED | `OPS-B3-A2B3-ARMED-20260813` |
| 5 | 相對機率雙窗看板（H20+H60 強／弱＋交集；**數字＝p_beat 非報酬％**；免 LLM） | `REL-PROB-DUAL-BOARD-FIX-EXECUTED` |
| 6 | NF＠0812：ARIMA／VAR／Kalman／COINT／GARCH／GNN **有界 EVIDENCE、皆 no-promote**；closeout-ack；殘格點名 | `NF-0812-CLOSEOUT-ACK` · residual card |
| 7 | ingest 階梯＋S0→S3 apply；LIVE breach=0 | `KH-INGEST-APPLY-S0-S3-EXECUTED` · `K2-INGEST-LADDER-ACK` |
| 8 | K0–K15 盤點／ACK（FillAuto、matrix、private smoke、ASR 抽樣、8b 產品、Doc1 hold、KH10 禁） | `KH-OPT-STEPWISE-ACK` 及各 K* ACK |
| 9 | KH8 A2-L3 寫庫 146399 列；**population_discriminates.ok=False** → E-keep／stop-at-7 | `KH8-DISCRIM-A2-L3-EXECUTED` · hard-gate card |
| 10 | K9 domain FT **僅 plan-first**（首隊建議 quant_finance）；**未訓** | `K9-DOMAIN-FT-PLAN-REGISTER` |
| 11 | K10 C1 EXPAND→feat **隔離**；禁默加權 predict | `K10-C1-EXPAND-ISOLATION-ACK` |
| 12 | 假「無此內容」：item **1818824** 已在庫；弱模型／guard-fail 閉集句 → `ensure_cite_backed_response` | `KH-GENERO-TP3X-FALSE-DECLINE-*`（封存後） |

**未變**：確立級假不了；sim 禁 apply；NF／M／β5 凍結預設；Sole Steward；冠軍護城河深；KH10 禁；未登入看不到私有。

### §6 知識入庫與作答熱路徑（本輪加深）

```text
瀏覽／上傳
  → ~/.augur_uploads/<token>/
    → acquire_local_files → fileparse.extract_text
         ├ PDF（± OCR；禁 ASR）
         ├ Office／PPT（Impress→pptx）／圖／文字
         └ AV → faster-whisper（owned_local+private only）
      → sha1 冪等 ingest → KIP（句→嵌→kh4→admit≤9）
        → retrieve_all ∥ readout（標題／檔名.ext＋問句）
          → compact freeze → 本機 LLM → guard／抛光
            → FillAuto 欄位=值閘
            → 假 decline 閘（有 item 引文禁閉集句 → 有界摘錄）
```

**設計命門（在 r14 五條上再加兩條）**：

1. **#1**：抽字／ASR＝轉錄草稿，不是 AI 改寫；失敗＝誠實 skip。  
2. **owned_local ⇒ local_private**：ASR 寫死。  
3. **PDF-C ≠ AVI-ASR**。  
4. **#19** 白名單三側同步。  
5. **RBAC**：未登入＝public；登入／super 才見私有。`scope=None` 的 public 路徑對非 super **fail-closed AND false**——這是預期 deny，不是缺件。  
6. **假 decline ≠ 缺件**：eligible＋readout 命中後仍吐「知識庫中無此內容」＝產品 bug；應用摘錄／LLM 依引文作答，**禁止**整庫回填當進化。  
7. **空包不進化**：`(無回覆)`／空 SSE 不寫庫、不抬 KH。

殘債（知識）：Doc1 純圖 hold；`.msg`／`.rar` skip；K9 他域 FT 未授；KH8 θ 未過（禁放寬）；長 LLM 仍可能慢（摘錄閘是保底不是變聰明）。

### §7 模型／特徵誠實結論（刷新）

| 結論 | 含義 |
|---|---|
| 冠軍仍深 | 熱路徑仍 **RankRidge**；L2 可跟價重訓，**≠**換樹／序列／GNN |
| tip≠經濟綠 | 兩窗可 RC=0；H20 **dead**、H60 **thin**——**不塗綠** |
| 有證據≠可升格 | NF＠0812 六族 EVIDENCE 全部 **no-promote**；殘格須點名；**勿重掃** |
| 圖 | 旁路可；熱路徑／GNN 翻案＝高門檻另 VERIFY |
| 相對機率看板 | 確定性表、免 LLM；**勿把 p_beat 讀成報酬％** |
| 下一進化常不是新族 | **日更穩態＋誠實尺＋知識可用＋有界提拔**＞假掃族表 |

### §8 綜合債表（r15）

| ID | 債 | 狀態 |
|---|---|---|
| R15-01 | A→B3＠**下一 tip（釘 ≥08-13）**＋L2 ALL-RANK | 🟡 **市場主軸** WAIT／ARMED |
| R15-02 | econ／dgate 誠實形（H20 dead／H60 thin） | 🟡 不修綠 · ∥ |
| R15-03 | standing 五窗永久化 | ❄ 須另雙明示改殼 |
| R15-04 | P6／長窗校準與 artifact 對齊 | 🟡 閒時 |
| R15-05 | 圖提拔／熱路徑 | 🔴 另 VERIFY |
| R15-06 | 升格挑戰族 | ❄ 另軌 · 禁默 |
| R15-07 | NF 新族／殘格（VECM／TCN／NB／Daily*／RL） | ❄ pause · 點名才開 · 勿重掃已閉 |
| R15-08 | STRUCT／scripts 冗餘 | 🔴 低優先 |
| R15-09 | M／β5／sim／Dividend | ❄ |
| R15-10 | 10–14 治權日曆 | 🟡 排程 · **不因本檔假關** |
| R15-11 | Writer／純圖 Doc1；OLE 殘 | 🟡 hold |
| R15-12 | `.msg`／`.rar` | 🔴 skip-hold |
| R15-13 | 私有／ASR 覆蓋回歸 | 🟡 抽樣已綠；持續 |
| R15-14 | tip＋N 日實現報酬研究 | 🔴 等價蓋過 tip＋N |
| R15-15 | KH8 discrim θ／depth8 | ❄ E-keep · 禁放寬 θ |
| R15-16 | K9 他域 FT | 🔴 plan-only · 未訓 |
| R15-17 | K10 C1→feat | 🔴 隔離 · 另 GO |
| R15-18 | 假 decline 閘入倉＋回歸套 | 🟡 碼已跑；**尚未 commit** |
| R15-19 | AUTO-LIFT 抬 >KH2 | 禁（常駐≠授權抬層） |

---

## 第二部｜優化計畫（選刀對齊）

> **後續優化執行 SSOT**＝`reports/augur_opt_stepwise_all_problems_r15_20260813.md`（最佳下一步／可先／可同步全板）。  
> 長板：市場 `augur_opt_stepwise_best_next_plan_r15` · KH `augur_kh_opt_stepwise_best_next_plan_20260813`。開工順序以全板為準。

### §9 讀序與操作協議

```text
人話憲章 r15
  → 本檔理解（第一部）
    → 問市場 → r15 市場導航
    → 問知識 → KH 20260813 導航
      → S1→S5／KH evolve + 最近 ARCHIVE/standing/audit
日更: skip-sync-B · no-SIM-apply · 誠實 econ · hold-#1 · 不假 B3
知識: owned_local ASR · PDF-C no-ASR · 登入才私有 · 有引文禁假無
分軌: 不互等、不互擋
```

1. 選刀＝對應導航板 `#` 或 Phase 步。  
2. 缺 GO → AskQuestion；禁默訓／默升格／默開 NF／默抬 KH8。  
3. 重大收斂 → r16 或刷新導航。  
4. **勿重掃假綠**；已 STOP／已 EVIDENCE 族同尺不刷。

### §10 最佳下一步（摘要）

| 角色 | 內容 |
|---|---|
| **市場主軸** | hold-#1 → 價≥**2026-08-13** → 站式 B3（**20,60**）→ L2 ALL-RANK `--apply`（僅 L1 RC=0；仍 no-promote） |
| **KH 主軸** | **守穩態**：`--check` 維持 S0／S3＝0；假 decline 閘入倉；**不**開 K9／K8 depth8／放寬 θ |
| **可∥** | #2 誠實披露；凍結輕監；KH ingest 巡檢（不搶 LLM 重活） |
| **可先（閒時）** | P6 長窗文件；升格門檻文件；K9 **僅**在另句 adopt 後 |
| **禁** | 假 B3；sim-apply；塗綠 dgate；默改五窗；SERVE-SWAP；ASR→PDF-C；用 tip 擋 KH；整庫回填當「有內容」 |

```text
market: hold-#1 | A→B3@≥2026-08-13 | horizons=20,60 | then-L2 | NF-pause | no-fake-B3
kh:     check-green | false-decline-gate | E-keep | stop-at-7 | no-K9-train | no-relax-θ
```

### §11 驗收

- [x] 產品／三軸／雙軌／地圖／S1–S5／LIVE／增量／知識熱路徑／模型結論／債表  
- [x] 選刀對齊 r15 市場＋KH 20260813；人話憲章成對  
- [x] 覆蓋誠實聲明  
- [x] 不創 [N]、不解凍、不開訓、不假 B3  

*完。[I] · self-reported · r15。*
