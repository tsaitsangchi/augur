---
title: augur 深化理解＋專案優化地基（合併）r14
status: final
series: deep_understanding_and_opt
round: r14
date: 2026-08-11
viewpoint: 2026-08-11T16:40+08:00
layer: "[I]"
role: 後續優化地基（理解＋對齊選刀）；刷新 r13；選刀以 r14 導航為準
supersedes_as_understanding:
  - reports/augur_deep_understanding_and_opt_plan_r13_20260808.md
inherits_understanding:
  - reports/augur_deep_understanding_and_opt_plan_r13_20260808.md
  - reports/augur_deep_understanding_and_opt_plan_r11_20260807.md
companion_plain_charter: reports/augur_project_charter_plain_zh_r14_20260811.md
exec_nav: reports/augur_opt_stepwise_best_next_plan_r14_20260811.md
s1_s5_ssot: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md
archive_tip: archive-20260811-b3-kh8-ppt-aap-hold
self_reported: true
---

# augur 深化理解＋專案優化地基 r14（2026-08-11）

> **性質**：[I]；**不創** [N]；不解凍；不 sim `--apply`；不假關確立級；**勿重掃假綠**。  
> **一句**：在 r13 上吸收 **08-08→08-11** 增量（B3＠0810／RankRidge 冰上移／KH 本機文件＆ASR／readout 私有／hold→下一 tip），收成**下一段優化地基**。  
> **疊用**：人話憲章 r14 → **本檔理解** → **`reports/augur_opt_stepwise_best_next_plan_r14_20260811.md` 選刀** → 准否／驗收＝S1→S5 SSOT＋ARCHIVE／standing／audit。  
> **覆蓋誠實**：非整庫逐檔複讀（`reports/`／`audits/`／`scripts/` 體量大）；本輪＝**結構地圖＋LIVE 親查＋08-08→08-11 收斂＋知識入庫熱路徑盤點**；長細節仍回 r6／r8／r11／r13／INVENTORY。

---

## 第一部｜深化理解

### §1 專案是什麼（產品真相）

**Augur**＝古羅馬「觀兆者」；「兆」只能是**真實觀測**，「預言」只能是**帶不確定性的相對排序／機率**。

一句話產品：

> **只用真資料，誠實預測台股誰比較強；說得出自己多常對，也說得出什麼時候不該裝懂。**

它同時承載**三條軸**（領域大憲章 v1.54.0 已對齊；勿只當「量化一管線」讀）：

| 軸 | 白話 | 倉內主落點 |
|---|---|---|
| **① 市場預測** | as-of → 特徵 → 宇宙 → 模型 → 日更名單／經濟尺 | `ingestion`／`features`／`universe`／`models`／`evaluation`／`scripts` 日更 |
| **② 知識素養＋顧問** | 可溯源文件／公開源／自有私有；誠實檢索與作答 | `knowledge`／`philosophy`／`advisor`；admin `:8500`／chat `:8090`／advisor `:8399` |
| **③ 自反／演化** | 預註冊實驗、擂台、判準凍結、演化候選 | `arena`／`evolution`／`deliberation`／`audit` |

封閉迴路（仍是優化節奏的脊椎，不是一次勾完的 checklist）：

```text
真實價／基本面／資金流（S1）
  → 知識／KH（S2）
    → 特徵／prodset（S3）
      → 模型族 train／serve（S4）
        → 日更預測／方向／經濟尺／顧問／模擬（S5）
  ↺ S5 證據回饋 S4／S3／S2
```

| 它是 | 它不是 |
|---|---|
| as-of 凍結、walk-forward、多 seed、#14 經濟終關 | 保證獲利／點位神算／自動下單 |
| 相對排序為生產熱路徑；方向屬可證偽實驗 | AI 代簽「已確立／可交易」 |
| Sole Steward；plan-first；AI self-reported | 假兆補表、偷看未來、把單次極值當定論 |

成功定義＝**經濟價值**（淨效用／hit vs 基準），不是裸 IC 或「圖好看」。

### §2 倉庫地圖（讀檔導航）

| 區 | 作用 |
|---|---|
| `constitution/` · `specs/` | Layer 0–7 **[N]** 治權與規格（合倉） |
| `docs/` | 靈魂／原則精華／領域大憲章（doctrine）；`系統架構大憲章_v1.54.0.md` |
| `src/augur/` | 實作（≈16 pkg）：預測 7pkg 與知識／顧問機械隔離 |
| `scripts/` | 薄 CLI（sync／train／predict／B3／KIP／admin／探針…）體量大 |
| `reports/` | 計畫／理解 **[I]**（本系列） |
| `audits/` | GO／EXECUTED／ADOPTED／ARMED 留痕 **[I]** |
| `models_artifacts/` | joblib；挑戰族可在／STOP≠換冠 |
| `handoff_memory/` · `HANDOFF.md` | 接續記憶；**現況以本檔＋r14 導航＋最近 audit 為準** |
| PostgreSQL `augur` | **唯一系統記錄**（≈**62 GB**） |

工具規則：`CLAUDE.md`（plan-first、#9 真兆、#11／#14、#32 預凍、#35 回歸鎖、#19 白名單三側同步）。

**預測 7pkg（熱路徑，禁吸知識）**：`core` 外之 `ingestion` · `features` · `universe` · `models` · `evaluation` · `catalog` · `audit`（以 `audit/import_isolation` 機械鎖為準）。  
**知識旁軌**：`knowledge` · `philosophy` · `advisor` · `llm`…——顧問可讀庫，**不得**把 KH 塞進特徵／預測權重（PME-XDOM 另案）。

### §3 S1→S5 × 硬邊界（運轉真相 · 08-11）

| 階 | 08-11 一句 |
|---|---|
| **S1** | 價到 D 才日更；**禁假 B3**；PriceAdj tip＝**2026-08-10** |
| **S2** | KH 大擴：PPT／PDF-C OCR／AVI-ASR；pool-gate／readout 私有可解；KH8 discrim **止於生產 stop-at-7** |
| **S3** | prodset 熱路徑穩；圖旁路可消費；**不**默入熱路徑 |
| **S4** | 冠軍 **RankRidge**；冰上已有 **asof 2026-08-10** retrain 鏈（VERIFY）；**NF-pause**；挑戰多 **STOP promote** |
| **S5** | tip＝**2026-08-10** 五窗已掛；H20 **dead**；standing 預設仍偏 **20,60**；sim **禁 apply**；hold-#1 候 **tip≥08-11** |

硬邊界（導航釘）：

```text
FZ/GATE-keep | skip-sync-B | no-SIM-apply | NF-pause
| no-cron-B3 | 誠實 econ | no-promote 默認 | 勿重掃假綠 | hold-#1
| PDF-C no-ASR | ASR＝owned_local+local_private only
```

### §4 LIVE 錨（2026-08-11 ≈16:40+08 · 親查）

| 錨 | 值 |
|---|---|
| 日曆 | **2026-08-11 二**（交易日；價尖仍 **08-10** → 候 08-11 價） |
| `TaiwanStockPriceAdj` max | **2026-08-10** |
| `feature_values` max `panel_date` | **2026-08-10** · 特徵種類約 **38** |
| `prediction_probability` tip | **2026-08-10** · **五 H** |
| #14＠tip | H20=**dead**；H40／60／82／120=**thin_unestablished** |
| ASR 入庫 | `source_type=asr_transcribe` **5** items（WebService 影音批） |
| KH4 eligible | ≈**146k** items（庫體量大；eligible≠皆可被 readout 標題命中） |
| DB size | **≈62 GB** |
| 服務 | admin **8500** · chat **8090** · advisor **8399**（本輪曾為 readout／ASR 重啟） |
| 封存點 | tag `archive-20260811-b3-kh8-ppt-aap-hold`（詳 ARCHIVE 帳；含 B3／KH8／PPT／hold） |

### §5 08-08→08-11 理解增量

| # | 增量 | 證據帳（示例） |
|---|---|---|
| 1 | B3＠**08-10** 五窗 VERIFY PASS；發射經濟軸誠實 | `VERIFY-B3-20260810-EXECUTED` |
| 2 | RankRidge **retrain asof 08-10** 鏈執行 | `RETRAIN-ASOF-0810-*-EXECUTED` |
| 3 | hold-#1 續候 **tip≥08-11**；A2B3 arm 帳 | `OPS-B3-A2B3-ARMED-20260811`／`HOLD-*` |
| 4 | PPT：`.ppt`→Impress／pptx 抽字＋補入庫／KIP | `PPT-PARSE-REINGEST-EXECUTED` |
| 5 | PDF-C：有界 OCR 波次；**禁 ASR／caption** 不動 | `PDF-C-OCR5*-EXECUTED`／PDF-C plan |
| 6 | AVI-ASR 窄切 CODE；ffmpeg UTF-8 hotfix；5 avi owned_local 入庫＋KIP#28 | `AVI-ASR-*`／對話帳 |
| 7 | readout：`public ∪ local_private`（登入／super）；`.avi` 副檔名 | `readout.py` 本輪 |
| 8 | AAP／手冊題假拒：尾綴 `?`＋別名 | 對話／readout 既修 |
| 9 | KH8 discrim／M3 pool-gate 帳；生產 discrim **stop-at-7** | `KH8-DISCRIM-M3-*` |
| 10 | Package C／市場 VERIFY 與知識線並行；**不**因 KH 開工默升格模型 | ARCHIVE／standing |

**未變**：確立級假不了；sim 禁 apply；NF／M／β5 凍結預設；Sole Steward；冠軍護城河深（挑戰族多數 STOP）。

### §6 知識入庫熱路徑（本輪加深）

```text
瀏覽／資料夾選取
  → admin multipart（影音 BATCH=1；文件≤50MB／AV≤200MB）
    → ~/.augur_uploads/<token>/
      → acquire_local_files
        → fileparse.extract_text
           ├ PDF（± OCR 旗標；禁 ASR）
           ├ Office／圖／文字
           └ AV → transcribe_asr（faster-whisper）
        → ingest：sha1 冪等；ASR→asr_transcribe＋S0 mark＋owned_local 閘
          → KIP（句→嵌→kh4→admit≤9）
            → retrieve_all（public∥private）／readout（標題讀出）
              → advise（guard／誠實分級）
```

**設計命門**：

1. **#1**：抽字／ASR＝轉錄草稿，**不是** AI 改寫作文；失敗＝誠實 skip。  
2. **owned_local ⇒ local_private**：ASR 寫死；公網 license 不得走 ASR 入庫。  
3. **PDF-C ≠ AVI-ASR**：掃圖 PDF 走 OCR；影音另窄切——勿混成「全面開 ASR」。  
4. **#19**：`SOURCE_TYPE_WHITELIST`／CLI choices／admission 一處擴。  
5. **RBAC**：未登入＝public；登入／super 才見私有——readout 已對齊 `retrieve_all`。

殘債（知識）：`.doc` 常缺 **libreoffice-writer**；`.msg`／`.rar`＝unknown_ext；ASR 品質／幻覺閘；長影音 CPU 慢；admin 重啟後才能吃到新 UI／碼。

### §7 模型／特徵誠實結論（刷新）

| 結論 | 含義 |
|---|---|
| 冠軍仍深 | 熱路徑仍 **RankRidge**；冰上 tip 可跟價重訓，**≠**允許隨便換樹／序列 |
| tip≠經濟綠 | 五窗可 RC=0；H20 仍 **dead**；長窗 thin——**不塗綠** |
| 有證據≠可升格 | NF／預訓練／表格挑戰多數 STOP；**勿重掃假綠** |
| 圖 | 旁路可；熱路徑／GNN 翻案＝高門檻另 VERIFY |
| 下一進化常不是新族 | **日更穩態＋誠實尺＋知識可用＋特徵／圖有界提拔**＞假掃族表 |

### §8 綜合債表（r14）

| ID | 債 | 狀態 |
|---|---|---|
| R14-01 | A→B3＠**下一 tip（釘 ≥08-11）** | 🟡 **主軸** WAIT／ARMED |
| R14-02 | econ／dgate 誠實形（H20 dead） | 🟡 不修綠 · ∥ |
| R14-03 | standing 五窗永久化 | ❄ 須另雙明示改殼 |
| R14-04 | P6／長窗校準與 artifact 對齊 | 🟡 閒時 |
| R14-05 | 圖提拔／熱路徑 | 🔴 另 VERIFY |
| R14-06 | 升格挑戰族 | ❄ 另軌 · 禁默 |
| R14-07 | NF 新族 | ❄ pause · 勿重掃 |
| R14-08 | STRUCT／scripts 冗餘 | 🔴 低優先 |
| R14-09 | M／β5／sim／Dividend | ❄ |
| R14-10 | 10–14 治權日曆 | 🟡 排程 |
| R14-11 | Writer／`.doc` 解析棧；OLE 殘 | 🟡 OS 依賴 |
| R14-12 | ASR 品質量測／引文標示 UX | 🟡 有界 |
| R14-13 | 私有知識檢索覆蓋（ANN＋readout）回歸 | 🟡 |
| R14-14 | tip＋N 日實現報酬研究 | 🔴 等價蓋過 tip＋N |

---

## 第二部｜優化計畫（選刀對齊）

> **執行選刀 SSOT**＝`reports/augur_opt_stepwise_best_next_plan_r14_20260811.md`（**2026-08-11 16:57 刷新加強**＝後續優化單一導航；本檔不重複長板；冲突以導航為準）。

### §9 讀序與操作協議

```text
人話憲章 r14
  → 本檔理解（第一部）
    → r14 導航選刀
      → S1→S5 SSOT + 最近 ARCHIVE/standing/audit
日更: skip-sync-B · no-SIM-apply · 誠實 econ · hold-#1 · 不假 B3
知識: owned_local ASR · PDF-C no-ASR · readout 私有須登入
```

1. 選刀＝導航板 `#` 或 Phase 步。  
2. 缺 GO → AskQuestion；禁默訓／默升格／默開 NF。  
3. 重大收斂 → r15 或刷新導航。  
4. **勿重掃假綠**；已 STOP 族同尺不刷。

### §10 最佳下一步（摘要）

| 角色 | 內容 |
|---|---|
| **主軸** | hold-#1 → 價≥**2026-08-11** → 站式 B3（預設 **20,60**；五窗須另明示） |
| **可∥** | #2 誠實披露；知識 UX／Writer；ASR 回歸；凍結輕監 |
| **可先（閒時）** | P6 長窗；升格門檻文件；私有檢索回歸套件 |
| **禁** | sim-apply；塗綠 dgate；默改五窗 standing；挑戰 SERVE-SWAP；把 ASR 開进 PDF-C |

```text
hold-#1 | A→B3@≥2026-08-11 | horizons=20,60 | NF-pause | no-SIM-apply | no-fake-B3
```

### §11 驗收

- [x] 產品／三軸／地圖／S1–S5／LIVE／增量／知識熱路徑／模型結論／債表  
- [x] 選刀對齊 r14 導航；人話憲章成對  
- [x] 覆蓋誠實聲明  
- [x] 不創 [N]、不解凍、不開訓  

*完。[I] · self-reported · r14。*
