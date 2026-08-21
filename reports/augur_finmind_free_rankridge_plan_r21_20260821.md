---
title: FinMind 改 Free 後仍能產出 RankRidge｜計畫書
status: p0_sponsor_baseline
series: s1s5_loop
round: r21
date: 2026-08-21
viewpoint: 2026-08-21T10:57+08:00
layer: "[I]"
product_id: FINMIND-FREE-RIDGE-v1
sponsor_expires: 2026-09-14
role: Steward 帳號頁 Sponsor 到期 2026-09-14；P0 LIVE＝仍 6000／by-date A；P0′＝錶掉 600 當日重探
parent_ssot: reports/augur_l0_hotpath_daily_plan_20260814.md
ridge_wf: reports/augur_hist_ridge_wf_plan_r21_20260820.md
p0_json: audits/FINMIND-FREE-PROBE-20260821.json
official: https://finmind.github.io/
self_reported: true
---

# FinMind Free → 仍產出 RankRidge｜計畫書

> **一句**：RankRidge **訓練／打分不呼叫 FinMind**。改成 free 之後，只要庫裡的還原價、法人買賣、借券成交還能**日更到價頂**，既有 `train_ranker.py`／`predict_asof.py` 就能繼續產生模型。要改的是 **L0 取數閉集、額度閘、以及「不帶 data_id 的全市場日抓」若被拒時的逐股後備**。  
> **不是**：換冠、改 standing H20+H60、開 93 表／339 表、解凍放量、本輪改碼。  
> **官方**：[FinMind 文件](https://finmind.github.io/)；流量公開尺＝註冊 token **600 次／小時**（無 token 300；Sponsor 曾是 6,000）。實際「哪些表還能不帶 `data_id` 一次抓全日」**必須降級後親探**，不能用 Sponsor 時代的假設開工。

---

## §0 護欄

```text
FINMIND-FREE-RIDGE-v1 | 計畫-only | 零改碼 | 零 FinMind 放量 | 零刪歷史 raw
| 預測⊥API（庫內可訓）| 分數≠％ | 條件≠可交易 | standing=20,60 不改
| 不假 B3 | 見 403／register 即停 | 不開分點／tick／93 表 heal
| FRED 另帳（本檔不改）
```

貼 `FINMIND-FREE-RIDGE-go` 才開 P0 探針（讀錶＋各一筆試抓）。探針仍守 `_quota_gate`，禁 audit 對帳全表重抓。

**P0 LIVE（2026-08-21）**：Steward「依計畫進行最佳的下一步」已做探針。錶＝**0/6000（仍 Sponsor，不是 free）**。價頂 08-20 三張 **by-date 皆通**（各 1 call；PriceAdj 2802 列、法人 102023、借券 1171）。scenario=A。此結果＝現況基線，**不是** free 終局。未改 L0／cron。

**到期日（Steward 帳號頁、2026-08-21 貼）**：Sponsor **2026-09-14**。秒級掉級以當日 `/user_info` 的 `api_request_limit` 為準，本倉不猜 09-14 當天晚上還是 09-15 才變 600。P0′＝**第一次讀到 limit≠6000** 時重跑 `scripts/probe_finmind_free_rankridge.py --apply`。到期前 **不改 L0、不預先 93 表囤貨**（歷史 raw 已在庫）。

---

## §1 先講結論

| 問題 | 答案 |
|---|---|
| 訓練程式要不要為 free 重寫？ | **不必。** `train_ranker.py`／`predict_asof.py` 寫明零 FinMind；只讀 `feature_values`、`core_universe_asof`、還原價標。 |
| 歷史模型還在不在？ | **在。** 已登錄的 `RankRidge_H*_asof_*` 與庫內 2014 以降 raw **不因 token 降級消失**。 |
| 以後還能**新訓**每日 asof=D 嗎？ | **能，前提是 D 的世界還進得來**：`TaiwanStockPriceAdj` 有 TAIEX 價、三欄 prodset 特徵算得出、核心宇宙有列。這三件事今天靠 L0；free 後 L0 必須變瘦、變慢、變誠實。 |
| 最危險的不是 600 次／小時？ | 更危險的是：**free 拒「不帶 data_id 的全日全市場」**（回 `parameter data_id can't be none` 或 `Your level is register`）。現況日更 `sync_by_date` 就是這條路：一表一日 **1 次**。若被拒，變成一表一股一次，核 A 全 roster 會把 600／hr 吃光還不夠。 |

---

## §2 RankRidge 實際吃什麼（與 FinMind 的距離）

冠軍 prodset 三欄（`evolution_production_feature_set` active）：

| 特徵 | 怎麼算 | 源表（FinMind dataset 名＝表名） | 沒日更會怎樣 |
|---|---|---|---|
| `cycle_position_252d` | 還原收盤在近 252 交易日高低之相位 | **`TaiwanStockPriceAdj`** | 價頂停住 → `asof_ready` 假 B3；標也停 |
| `inst_cumflow_position_120d` | 法人累計淨買在自身 120 日區間之相位 | **`TaiwanStockInstitutionalInvestorsBuySell`** | 該欄缺列 → 核心交集變瘦或當日無法訓 |
| `lending_fee_rate_mean_30d` | 近 100 筆借券成交 `fee_rate` 均（E 類；無事件可真零） | **`TaiwanStockSecuritiesLending`** | 源表 max(date) 過舊 → `_table_covers` 拒真零 → 缺列 |

訓練標＝還原價 t+1 進場、持有 H 日（`evaluation/label.py`），同樣只靠 **PriceAdj**。  
核心宇宙＝特徵完整度閘；閘若仍要求「37 欄全到」，free 日更瘦閉集會讓宇宙縮小。**要繼續出 Ridge，閘必須對齊 prodset 三欄＋價量必要窗，不能默認 93 表完整。**

日更現況（Sponsor 時代 L0 核 A，14 張）比 Ridge **寬很多**。其中 **`TaiwanStockGovernmentBankBuySell` 已在 catalog `_SPONSOR_ONLY`**：free 後這張會直接 `level is register`，**Ridge 三欄用不到它**，日更應 SKIP，不是硬衝。

```text
FinMind API
    ↓  僅 L0／sync（API 門）
raw 表（PriceAdj／法人／借券／…）
    ↓  庫內、零 API
feature_values  →  core_universe_asof  →  train_ranker  →  model_registry
    ↓
predict_asof  →  prediction_values（standing 仍 H20+H60）
```

---

## §3 Free 與現況的差距（公開文件＋本倉假設）

公開尺（[Quick start](https://finmind.github.io/quickstart/)／[llms.txt](https://finmind.github.io/llms.txt)）：

| 項 | Sponsor 時代本倉 | Free（文件） |
|---|---|---|
| 額度錶 `api_request_limit` | 實測約 **6,000／hr** | 註冊 token **600／hr** |
| `_quota_gate` 暫停線 | `limit − 200` | 同一公式會自動變成 400；**閘已隨錶，不必為 600 重寫邏輯** |
| `MIN_INTERVAL=0.9s` | 為防 IP sustained 403（曾 8/6000 也被 ban） | **仍要**；free 更不能狂打 |
| 日更主路徑 | `sync_by_date`：**不帶 data_id**，一表一日 1 call | **未證實**。第三方整理常寫：free 每股資料集要 `data_id` |
| 分點／tick／鉅額／部分官股 | catalog `_SPONSOR_ONLY` | 應視為永久不可增量 |
| 93 表 heal／寬窗 attestation | 曾把 IP 打到 sustained 403 | **free 禁止** |

本倉 `finmind.py` 註解與 `check_finmind_quota.py` 自測例子仍寫 6000，那是 **Sponsor 經驗數字**，不是硬編碼上限（上限以 `/user_info` 為準）。降級後讀錶就會變成 600；**P1 要改的是註解、預設 fallback、以及「register 級拒表」的 SKIP 清單**，不是另造一套 client。

---

## §4 最小閉集：RankRidge-min

**日更只保證這三張進到 FinMind 已有的最新交易日**（再加名冊／交易日若 by-date 仍便宜）：

```text
必（Ridge 能訓）：
  TaiwanStockPriceAdj
  TaiwanStockInstitutionalInvestorsBuySell
  TaiwanStockSecuritiesLending

強建議（價頂／假 B3／名冊，call 很少）：
  TaiwanStockPrice          # 原始價；宇宙／對帳用，Ridge 標不用
  TaiwanStockInfo           # 名冊
  TaiwanStockTradingDate    # 若仍 by-date 便宜；否則用 PriceAdj distinct date

可延後／SKIP（核 A 有、Ridge 三欄沒有）：
  PER、十年線、融資券、外資持股、借券餘額、當沖、市場合計法人／融資券
  TaiwanStockGovernmentBankBuySell   # _SPONSOR_ONLY → free 必 SKIP

不做：
  分點、tick、News 全日、93 表、國際股 Info 回填、寬窗 reconcile heal
```

TRI（`TaiwanStockTotalReturnIndex`）走 **by-dim-id**（TAIEX／TPEx 兩顆種子），與 Ridge 標無關；站著 H20+H60 日常出門若還要大盤路徑可留，**不是 Ridge 硬依賴**。FRED 維持 `--no-catalog` 熱路徑，本計畫不併案。

---

## §5 額度帳（為什麼「能／不能同一晚補齊」）

假設每交易日只補 **昨天→今天** 一檔增量：

| 抓法 | 必三張 call 數 | 600／hr 夠不夠 |
|---|---|---|
| **A. by-date 仍通**（不帶 data_id） | **3**（核 A 若留 10 張免費日頻 ≈10） | 夠；20:00 一班可做完 |
| **B. 必須 data_id，只抓核心～300 檔** | 3×300＝**900** | 一小時不夠；拆兩段（20:00 價、次日 09:20 法人＋借券）或隔小時續 |
| **C. 必須 data_id，全 roster～1,800 檔** | 3×1,800＝**5,400** | 約 **9 小時** 額度窗；當晚無法三張齊，宇宙／特徵會晚一天 |
| **D. 核 A 14 張 × 全 roster** | 數萬 | **不要做** |

核心宇宙現況約 280 檔；特徵 build 的 roster 往往大於核心。P0 探完抓法後才能選 A／B／C。  
**原則**：free 只對「Ridge 要算的股」逐股，不對 1,800 檔名冊地毯。新上市先入 Info，次日再納入逐股清單。

既有 `sync_by_date` 已寫：首筆若訊息含 `data_id` → `not-by-date-capable`。P1 要接的是：**此 mode 不要再落到全史 `_per_stock_sync`**（那是首次落地用的），改成 **「只抓 asof 當日、只抓 Ridge roster」的窄窗逐股**。

---

## §6 分期

| 階 | 做什麼 | 產出 | 未 GO 不做 |
|---|---|---|---|
| **P0 探針** | 降級後（或另備 free token、**禁止與 Sponsor 同 IP 雙進程**）讀 `/user_info`；對 RankRidge-min 各打 **1 筆不帶 data_id 的單日**、失敗再打 **1 筆 data_id=2330**；記 status／msg／是否 `register` | `audits/FINMIND-FREE-PROBE-*.md`：每表 mode＝by-date｜per-stock｜forbidden | 全表 heal、93 表 |
| **P1 閘與閉集** | L0 預設 dataset＝RankRidge-min；`_SPONSOR_ONLY`＋探針 forbidden → SKIP；`level is register` **停該表、不重試風暴**；額度 fallback 600 非 6000；日誌印 `count/limit` | `run_l0_hotpath_daily.sh --datasets …`；finmind 註解／fallback；catalog 標 `tier=F` 與 `data_id_required` 以探針為準 | 改 train_ranker |
| **P2 日更節奏** | 若 A：維持平日 20:00 一班。若 B／C：價優先、法人／借券可 09:20 續；`_quota_gate` 睡到錶退。禁第二條白天 FinMind cron | 改 `install_cron.sh` 說明＋L0 分段，**不新增長自動鏈除非 Steward 點名** | 與 audit 同 IP 疊加 |
| **P3 特徵／宇宙誠實** | 核心完整度改「prodset 三欄＋PriceAdj 窗夠」為 Ridge 日更閘；其餘 37 欄缺＝缺，不 zero-fill。借券表若停更，E 類真零前提失敗 → 缺列，**不假裝有費率** | `build_core_universe`／asof_ready 對 Ridge 路徑的說明與可選旗標 | 默改 prodset 三欄定義 |
| **P4 庫內訓** | 與今日相同：`--skip-sync` 的 L2／HIST-RIDGE-WF／`train_ranker --asof D`。D≤價頂 | 新 `RankRidge_*` 只要世界齊 | 假 B3＠無價日 |
| **P5 放棄清單寫進憲章註** | 分點、tick、官股日更、93 表 attestation、寬窗 heal | 操作手冊一段；HANDOFF／L0 計畫修訂（另 GO） | 刪歷史分點表 |

**P0 未綠之前，禁止把 L0 閉集改進 cron。** 探針本身也要 `--limit` 式各一 call。

---

## §7 預計改哪些檔（P1 起，本輪不動手）

| 檔 | 為什麼 |
|---|---|
| `src/augur/ingestion/finmind.py` | 註解 6000→「以錶為準」；`_user_quota` fallback 600；辨識 `Your level is register`／`data_id can't be none` 為**應用層、不重試**（部分已是 FinMindError） |
| `src/augur/ingestion/sync.py` | `not-by-date-capable` 後接 **當日＋roster 窄窗逐股**，禁掉進全史 per-stock |
| `scripts/run_l0_hotpath_daily.sh` | 預設 dataset＝RankRidge-min；SKIP sponsor-only |
| `scripts/check_finmind_quota.py` | 自測例子可留 6000；文件寫明 LIVE 以錶為準 |
| `src/augur/catalog/__init__.py` | `_SPONSOR_ONLY` 在 free 當 excluded；`data_id_required` 用 P0 結果覆寫，不猜 |
| `scripts/install_cron.sh` | 註解：free 時禁 93 表；分段日更若 P0＝B／C |
| 核心閘（P3，另 GO） | Ridge 日更不要求核 A 14 張齊 |

**明確不改（除非另句）**：`train_ranker.py`、`predict_asof.py`、prodset 三欄公式、standing 20／60、HIST-RIDGE-WF 的 asof=D 契約、RIDGE-THEN-PB 表。

---

## §8 日曆與降級當天（給人看）

帳號頁到期 **2026-09-14（一）**。今天（2026-08-21）到那天還有 **24 個日曆日**。ops 早在 08-14 寫過「續至 09-14」，本句＝帳號頁對齊。

| 日 | 預期 | 做什麼 |
|---|---|---|
| 至 **2026-09-13** | 錶仍 6000 | L0 核 A 照舊；**不改閉集**；不 93 表囤貨 |
| **2026-09-14** | 帳面到期；當晚可能仍 6000 或已掉 | 20:00 前先 `check_finmind_quota.py --read`；limit 仍 6000 → 當日 L0 可照舊；**已變 600 → 先停非必要 FinMind，跑 P0′，不盲衝核 A 14 張** |
| **2026-09-15 起** | 多數情況已是 free | 若尚未 P0′：讀錶＋三張 ≤2 call；再決定 P1 |

降級當下順序：

1. **先確認庫**：PriceAdj／法人／借券 `max(date)`；歷史 raw **不刪**。  
2. **停** 任何 93 表／heal／寬窗 attestation／第二個 FinMind 進程。  
3. 等 Sponsor 到期自動掉級（不必另備第二支 token、**禁止同 IP 雙進程**）。  
4. **P0′ 探針**（同一支 `--apply`）。  
5. 依探針選 A／B／C，才改 L0 閉集（另貼 `FINMIND-FREE-L0-go`）。  
6. 當日若價未進：當日 **不訓、不假 B3**。  
7. 價進了、三欄算得出：照舊 `train_ranker --family RankRidge --asof D --resume`。

---

## §9 風險（誠實）

| 風險 | 含義 | 處理 |
|---|---|---|
| by-date 全死 | 當日 Ridge 世界可能隔日才齊 | 09:20 既有補班；asof_ready 缺即缺 |
| 借券為事件型、逐股貴 | 無成交日 API 仍可能要 1 call／股 | 只打核心 roster；無列＝真無事件僅當表仍覆蓋 asof |
| 核心閘仍要 37 欄 | 宇宙縮到接近 0，Ridge 無樣本 | P3 必須先於「只 sync 三張」上鐘 |
| IP sustained 403 | 600 次沒用完也被 ban | 維持 MIN_INTERVAL；見訊號即停 |
| 與舊 stock_backend／audit 同 IP | 額度相加 | 已取消的 16:00 cron 維持取消 |
| 以為「free 不能訓」 | 把 API 凍結當成預測凍結 | 預測⊥API 仍有效；凍的是取數 |

---

## §10 GO 矩陣

```text
DO NOT: 本檔未貼 GO 就改 L0／cron／finmind fallback
DO NOT: 用 free token 跑 daily_maintenance 無 --datasets
DO NOT: 全史 per-stock、93 表 heal、分點、假 B3
DO NOT: 改 standing、promote、sim --apply、刪 raw

P0:  FINMIND-FREE-PROBE-go     → 讀錶＋RankRidge-min 各 ≤2 call
P1:  FINMIND-FREE-L0-go        → 閉集＋register SKIP＋窄窗逐股後備
P2:  FINMIND-FREE-CRON-go      → 僅當 P0＝B／C 才動 cron 說明／分段
P3:  FINMIND-FREE-UNIVERSE-go  → 核心閘對齊 prodset（另句）
P4:  不另 GO（既有 train 契約）— 世界齊即可訓
```

---

## §11 驗收（P1 落地後才算）

1. `/user_info` 的 `api_request_limit`＝600（或當時真實 free 上限），閘在 `limit−200` 暫停。  
2. RankRidge-min 三張 `max(date)` 能跟到 FinMind 已公布的最近交易日（或探針證明該日 API 0 列＝真無價）。  
3. `check_asof_ready` 在有價日＝ready；無價日＝假 B3，不訓。  
4. `train_ranker --family RankRidge --horizon 60 --asof <價頂> --resume` 能寫出新 `model_id`（零 live fetch）。  
5. 日誌出現 `register`／403 時該表 SKIP，沒有重試風暴。  
6. `ridge_then_pb_long_*` 等條件帳仍只讀已完成模型日——**本計畫不保證進場條件產品**，只保證 **RankRidge 模型還能生**。

---

## §12 與現行 SSOT 的關係

- 取數閉環仍是 r16 **S1＝THAW-bounded 熱路徑完整 ≠ 339 表**。本檔把「熱路徑」從核 A 14 張收到 **Ridge 三張**。  
- L0 計畫（`augur_l0_hotpath_daily_plan_20260814.md`）在 P1 GO 後才改預設 dataset；在那之前 **Sponsor 核 A 契約仍有效**。  
- HIST-RIDGE-WF／RIDGE-THEN-PB **不因本檔重開或重跑**。  
- 本檔＝P0 Sponsor 基線＋到期日 **2026-09-14**。P1 仍須另貼 `FINMIND-FREE-L0-go`。不授權放量、不授權到期前改 L0。
