---
title: 長線順勢 × 短線逆勢進場——市場同類模型閉集驗証計畫書 r18
status: adopted
series: s4_s5_verify
round: r18
role: 把「市場上有沒有這類模型」收成可實作、可對照、可 OOS 的閉集目錄（已採納；W1＋W2＋W3＠08-18 已閉）
date: 2026-08-19
viewpoint: 2026-08-19T08:50+08:00
layer: "[I]"
parent_ssot: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_r16_20260813.md
exec_nav: reports/augur_opt_stepwise_all_problems_r18_20260817.md
up_pull: reports/augur_uptrend_pullback_ls_top10_plan_r18_20260819.md
econ_path: reports/augur_econ_prove_edge_plan_r17_20260817.md
philosophy: src/augur/philosophy/framework.py
adopted: audits/TREND-PB-CATALOG-ADOPTED-20260819.md
locked_k: 10
self_reported: true
---

# 長線順勢 × 短線逆勢進場——市場同類模型閉集驗証（2026-08-19）

> **一句**：市場上大量規則／因子本質是「長線定方向、短線等回撤（做多）或等反彈（做空）」。本檔把**能在台股還原價＋核心宇宙上機算**的同類收成閉集 **T01–T12**，另設對照組 **C01–C07**（短線也順勢／純動能／現役 Ridge），用**同一把 OOS 尺**驗証。  
> **本檔＝已採納計畫**（`audits/TREND-PB-CATALOG-ADOPTED-20260819.md`）。採納 ≠ 開跑；開跑依 §7 分族 GO。不取代 standing RankRidge H20+H60、不 promote、不 sim-apply、不倒 canonical 31。  
> **「所有模型」的誠實邊界**：無法枚舉全球零售 EA／私募黑箱。閉集＝公開文獻或教科書裡、能用日頻還原收盤複寫的命名規則。其餘進 §4 SKIP。  
> **與 UP-PULL**：T01＝已閉的 UP-PULL-v1 探針（＠08-18 做多 5／做空 2）。本檔是把它放進同類賽道，不是重寫 θ。

---

## §0 護欄

```text
TREND-PB-CATALOG-plan | no-fake-B3@08-19 | no-promote | no-SIM-apply | NF-pause
| standing=20,60 不改 | 路徑％ ≠ 未來漲跌幅％ | score／IC ≠ 報酬％
| 做空名單 ≠ 可融券可成交 | 不倒 canonical 31 | 探針現算 ≠ 灌 prodset
| 改 θ＝新 ID | SKIP 不是失敗
```

| 可 | 不可 |
|---|---|
| 規則探針／歷史 as-of walk（stamp＜panel） | 把任一 T／C 名單當可交易、當 #14 已過 |
| 從 PriceAdj **現算** SMA／RSI／布林（只活在探針） | 把 RSI／SMA200 倒進 canonical 31／prodset |
| 對照組（突破、全窗上漲、Ridge）同尺比較 | 無 GO 開 NF／VECM／TCN／PullbackLS 訓練 |
| 過閘不足 10 如實少列 | 為湊 10 暗改 θ 卻沿用同一 ID |

**台股做空**：所有空方集合＝條件排序，不是下單。平盤下禁空、無券、成本地板 **0.585%** 不進 v1 尺。

---

## §1 問題定義

### 1.1 要驗什麼

給定合法 as-of 日 D≤價頂、核心宇宙＠D：

1. **同族（T）**：長線結構往上（往下）＋短線已拉回（已反彈）→ 做多（做空）集合。  
2. **異族對照（C）**：短線也順勢、或只有長線、或現役 RankRidge。用來回答「這兩段閘有沒有比『繼續追高』更有未來相對名次」。  
3. **共同產出**：每模型 `n_long`／`n_short`、與 T01 重疊、OOS 相對名次／dummy-IC（標 ≠確立）。

### 1.2 不要什麼

- 宣稱「市場上所有量化基金都在用 X」。  
- 用單日＠08-18 的 5／2 檔當勝。  
- 把突破模型（Turtle／TSMOM 純號）叫做本概念的實作。  
- 為了 RSI 去改 RankRidge 的 3 欄包。

### 1.3 尺（全目錄共用；凍結）

| 項 | 口徑 |
|---|---|
| 宇宙 | `core_universe_asof`＠D |
| 價 | 還原收盤 `tw.daily_bar_adjusted`；H＝交易日 |
| 進場 | **t+1**（label 層；#8） |
| 持有 | H∈{5,10,20,60}，僅標籤已實現者 |
| 多空 | 過閘集合 vs 宇宙其餘；做多看後續相對強、做空看後續相對弱 |
| 禁 | 同日 stamp 當 OOS；路徑％當未來％；n＜門檻卻報勝 |
| H10 日曆閘 | panel 後須 ≥11 交易日才評 H10（與 V1 同一刀） |

---

## §2 同族閉集 T01–T12（要實作驗証的「這類模型」）

每檔 ID 凍結 θ。改數字＝新 ID（例 T05b），禁止同一 JSON 混版本。  
空方＝多方鏡像，除非「鏡像」欄另註。

| ID | 市場名稱（對照） | 長線（結構） | 短線（進出） | 鏡像做空 | 現算來源 | 波次 |
|---|---|---|---|---|---|---|
| **T01** | UP-PULL-v1（本倉已探針） | H40／60／90／120／240 logret **全＞0** | H5 與 H10 **全＜0**；20 日高回撤 ∈[−15%,−3%]；cycle≥0.40 且 p2h≥0.80 | 是（對稱 θ） | 八窗路徑＋特徵欄 | W0 已閉＠08-18 |
| **T02** | 最小兩段閘 | H60＞0 | H5＜0 | 是 | 路徑 | W1 |
| **T03** | 年線上的均線回撤 | 收盤＞SMA200 且 SMA200 斜率＞0（200 日點差） | 收盤／SMA20−1 ∈[−15%,−3%] | 是（＜SMA200 且反彈 SMA20） | PriceAdj 現算均線 | W2 |
| **T04** | 季線上的 20 日回撤 | 收盤＞SMA60 | 收盤／SMA20−1 ∈[−15%,−3%] | 是 | 現算 | W2 |
| **T05** | Connors RSI(2) | 收盤＞SMA200 | RSI(2)＜10 | 是：＜SMA200 且 RSI(2)＞90 | 現算 RSI／SMA | W2 |
| **T06** | Connors RSI(2) 嚴 | 收盤＞SMA200 | RSI(2)＜5 | 是：RSI(2)＞95 | 同 T05 | W2 |
| **T07** | Elder Triple Screen（日頻簡化） | 週線代理：每 5 交易日抽樣之 MACD 柱斜率＞0 | 日 RSI(2)＜50（Force Index 無量則退化為此） | 是 | 現算 MACD／RSI | W3 |
| **T08** | Wilder RSI(14) 回撤帶 | 收盤＞SMA200 | RSI(14)∈[30,50] | 是：＜SMA200 且 RSI(14)∈[50,70] | 現算 | W2 |
| **T09** | MOM×STREV（週） | 橫斷面：H120 路徑前 1/3 | 橫斷面：H5 路徑後 1/3 | 是（H120 後 1/3 ∩ H5 前 1/3） | 路徑＋截面分位 | W4 |
| **T10** | MOM×STREV（月） | 橫斷面：H120 前 1/3 | 橫斷面：H20 後 1/3 | 是 | 同 T09 | W4 |
| **T11** | TSMOM＋拉回覆層 | sign(H120)＞0 | H5＜0 且 20 日高回撤 ∈[−15%,−3%] | 是 | 路徑 | W1 |
| **T12** | 布林下軌回撤 | 收盤＞SMA200 | 收盤≤布林下軌(20,2σ) | 是：＜SMA200 且≥上軌 | 現算 | W2 |

**T01 備註**：P1 已閉；本目錄的 OOS（W5）仍須對 T01 重跑，才能跟 T02–T12 同尺，不把 08-18 單日當勝。

**T07 誠實**：Elder 原書第三屏是更短框觸發／買進停損。日頻宇宙**沒有**盤中框 → 本 ID 是「潮＋浪」兩屏，不是三屏原作。寫進 JSON `approx=elder_2screen_daily`。

---

## §3 對照組 C01–C07（不是這類，但必須同尺）

沒有對照組，T 族贏了也不知道是「拉回有用」還是「長線動能本來就有用」。

| ID | 名稱 | 規則（做多；空則鏡像或另註） | 用來否定什麼 | 波次 |
|---|---|---|---|---|
| **C01** | 八窗全正 | H_TRACK 八窗 logret **全＞0**（08-18 預診 25 檔，含光寶科） | 「只要在漲就好」 | W1 |
| **C02** | 現役 RankRidge | 該 as-of 已寫入或 dry-run 的 H20 分數 Top10（無則 skip 並記 `no_score`） | 「Ridge 高位相對強＝本概念」 | W1 |
| **C03** | 純 TSMOM | sign(H120)＞0，**不**要求短窗為負 | 拉回覆層有沒有增量 | W1 |
| **C04** | Donchian 突破 | 收盤＝近 20 日最高（做多）／最低（做空） | 突破進場 vs 回撤進場 | W2 |
| **C05** | 經典 12–1 動能 | H252 路徑橫斷面前 1/3，**跳過** H20（不看最近月） | 學術動能「避開反轉」vs 本概念「要求反轉」 | W4 |
| **C06** | 年線高位 | `cycle_position_252d`≥0.90 | Ridge 實際在做的事 | W1 |
| **C07** | 純短窗逆向 | H5＜0，**不**要求長窗為正（跌刀） | 沒有趨勢過濾的假拉回 | W1 |

C02 若該 D 無 `prediction_values`：列 `skip=no_standing_scores`，不幻造分數、不改 standing。

---

## §4 刻意 SKIP（不是失敗；禁止當「已驗証」）

| 名稱 | 為什麼不進閉集 |
|---|---|
| Turtle 原規則（55／20 突破＋N 停損） | 突破族；且部位公式與期貨 N 與台股日頻權益不直接對 |
| Minervini VCP／樞紐、Wyckoff spring | 型態辨識，日頻規則無法忠實複寫 |
| Ichimoku 雲上回撤、Guppy MMA | 參數面太大；邊際資訊≈均線回撤（T03／T04） |
| IBD CAN SLIM 基本面＋RS | 需基本面＋相對強度產品定義；RS 子集已由 T09／T16 精神覆蓋，完整 CAN SLIM 另 GO |
| Connors TPS 加碼 | 執行層（分批）不是選股閘；可在 T05 勝出後另 overlay |
| 盤中 Triple Screen 第三屏 | 無分鐘線 |
| 具名 CTA／AQR／私募「trend+MR」產品 | 黑箱；無法 source-pure 複寫 |
| VECM／TCN／NB／RL／0812 NF | 別條軌；`--track other --apply` 仍 rc=6 |
| 把 RSI／SMA 寫進 RankRidge prodset | 倒特徵；E4／canonical 鎖 |

**T16 不開**：IBD 式「對大盤 RS + 10 週線回撤」可後補為 T13（H120 減 TAIEX 路徑＋SMA50 回撤），須另句加 ID，不塞進本版 12 檔。

---

## §5 庫內怎麼算（禁倒 31）

| 量 | 做法 | 進 `feature_values`？ |
|---|---|---|
| 八窗路徑、20 日高／低 | 與 UP-PULL 探針同一函式 | 否（現算） |
| `cycle_position_252d`／`price_to_252d_high` | 已有欄＠D | 讀；不改 |
| SMA20／60／200、RSI(2)／RSI(14)、布林(20,2)、MACD(12,26,9) | 探針內對 ≤D 還原收盤現算；算不出→該股缺列 | **否** |
| 橫斷面 1/3 | 當日核心宇宙內分位 | 否 |
| RankRidge 分數 | 唯讀 `prediction_values` 或 dry-run；零寫 | 否 |

新指標**不**進 panel.py、**不**進 canonical、**不**進 prodset，除非另句「特徵漏斗點名」且通過 E4 路徑（本計畫不開）。

現成動能欄：`momentum_5d`／`20d`／`60d`／`120d`／`252d`、`return_1d`。H10／40／90／240 仍須現算（與 T01 相同）。

---

## §6 實作殼（採納後才寫碼）

擬議（零寫 `prediction_values`）：

```text
python scripts/probe_trend_pb_catalog.py --selftest
python scripts/probe_trend_pb_catalog.py --date 2026-08-18 --family T05 --side both --k 10
python scripts/probe_trend_pb_catalog.py --date 2026-08-18 --family all --wave W1
python scripts/walk_trend_pb_catalog.py --origin 2026-07-31 --families T01,T05,C01,C03 --oos --horizon 5
```

驗收：

- `--date 2026-08-19` → rc=3。  
- `--family` 不在閉集 → rc=2。  
- JSON：`/tmp/trend-pb-{asof}-{family}.json`；表頭固定「已發生路徑／條件，不是未來漲跌幅；≠可交易」。  
- `all` 一次跑完一波次，輸出重疊矩陣（T 與 C、T 與 T01）。

函式住 `src/augur/evaluation/trend_pullback_catalog.py`（純閘；自測免 DB）。T01 呼叫既有 `uptrend_pullback`，禁止複製一份 θ。

---

## §7 分階（Phase／Wave）

| 階 | 做 | 須 GO | 不做 |
|---|---|---|---|
| **P0** | 本檔採納；ID／θ 凍結 | ✅ 已貼 `TREND-PB-CATALOG-adopt` | 當日開 12 套探針 |
| **W1** | 只走路徑能算的：T01 重出、T02、T11、C01、C03、C06、C07（C02 有分數才跑） | ✅ 已貼 `TREND-PB-W1-go`＠08-18 | 現算 RSI |
| **W2** | T03–T06、T08、T12、C04 | ✅ 已貼 `TREND-PB-W2-go`＠08-18 | 把均線寫進 panel |
| **W3** | T07（Elder 兩屏近似） | ✅ 已貼 `TREND-PB-W3-go`＠08-18 | 宣稱＝原書三屏 |
| **W4** | T09、T10、C05 | `TREND-PB-W4-go` | 把截面分位當確立 |
| **W5** | 全閉集 OOS walk（已實現 H） | `TREND-PB-oos-walk-go \| origin=2026-07-31 \| no-promote` | 同日 IC；H10 日曆不足當失敗 |
| **W6** | 僅當 W5 顯示 T 族穩定優於 C01／C03／C07 | `TREND-PB-model-go \| family=PullbackLS`（或勝出 ID） | 改 RankRidge 包；SERVE-SWAP |
| **P4** | 顧問兩欄仍須 `UP-PULL-emit-go`；本目錄不自動出門 | 雙明示 | 改 standing 20,60 |

UP-PULL 計畫的 P2 與本檔 W5 **應合併成一次 walk**（同一 origin、同一 label），避免兩套未來報酬。合併 GO 文案可寫 `TREND-PB-oos-walk-go` 且 `families` 含 T01。

---

## §8 工作包（開跑複製）

### WP-P0｜採納目錄 ✅

```text
WHEN: Steward 貼 TREND-PB-CATALOG-adopt
DO:   本檔 status → adopted；寫 audits/TREND-PB-CATALOG-ADOPTED-20260819.md
DONT: 當日當可交易；開 W2 RSI；promote
DONE: 2026-08-19 ADOPTED；T01–T12／C01–C07 ID 未改；W1 未開
```

### WP-W1｜路徑族探針＠08-18 ✅

```text
WHEN: P0 已採納；價頂 ready；Steward 貼 TREND-PB-W1-go | date=2026-08-18
DO:   probe T01,T02,T11,C01,C03,C06,C07（+C02 若有分數）
DONT: 寫 prediction_values；假 B3＠08-19；W2 指標
DONE: 2026-08-19 EXECUTED；C02 不在 paste 未跑；T01＝5／2；C01∩T01＝0；C06∩T01＝0
```

### WP-W2｜指標族探針＠08-18 ✅

```text
WHEN: Steward 貼 TREND-PB-W2-go | date=2026-08-18
DO:   probe T03,T04,T05,T06,T08,T12,C04；SMA／RSI／布林現算
DONT: 寫 feature_values；倒 canonical 31；假 B3＠08-19
DONE: 2026-08-19 EXECUTED；T04 做多=0；C04∩T01=0；T12 做多=1
```

### WP-W3｜Elder 兩屏近似＠08-18 ✅

```text
WHEN: Steward 貼 TREND-PB-W3-go | date=2026-08-18 | families=T07 | k=10
DO:   probe T07；週 MACD 柱斜率＋日 RSI(2)；JSON approx=elder_2screen_daily
DONT: 宣稱＝原書三屏；寫 feature_values；假 B3＠08-19；W4 截面
DONE: 2026-08-19 EXECUTED；T07 做多 pass=67／listed=10；做空 19／10；∩T01 多空皆 0
```

### WP-W5｜共同 OOS

```text
WHEN: 至少 W1 殼綠；Steward 貼 TREND-PB-oos-walk-go
DO:   origin≤價頂且有已實現 H；stamp < panel；T 與 C 同尺
DONT: 不足樣本報勝；IC＝確立；做空＝可空
DONE: audit；dummy-IC／名次差標 ≠確立
```

---

## §9 與 r18／UP-PULL／#14

| 關係 | 說明 |
|---|---|
| M29 UP-PULL | T01 的產品閘；本檔＝賽道目錄 |
| M18 其他模型 | 那是 Rank*／NF 族；本檔是**規則閘**，不開 NF |
| M28 #14 | W5 的 IC ≠ egate；不 E5、不放寬 ρ |
| standing | 全程 H20+H60 RankRidge |

建議 paste（採納已閉；開工另句）：

```text
TREND-PB-CATALOG-adopt | T01-T12 + C01-C07 | no-promote | standing=20,60
| no-fake-B3 | 做空≠可空 | 路徑％≠未來％ | 不倒 canonical 31
```

W1 開工另貼：

```text
TREND-PB-W1-go | date=2026-08-18 | families=T01,T02,T11,C01,C03,C06,C07 | k=10
```

---

## §10 驗收（本計畫書）

- [x] 「市場上有沒有」改成可機算閉集，不是散文  
- [x] 同族 12 ＋對照 7 ＋ SKIP 表  
- [x] 每 ID 長線／短線／鏡像／波次寫死  
- [x] 共同 OOS 尺與假 B3／不倒 31／不做空可成交  
- [x] 分階 GO；T01 不重寫；W5 可與 UP-PULL P2 合併  
- [x] Steward 採納（`audits/TREND-PB-CATALOG-ADOPTED-20260819.md`）

*完。[I] · adopted · P0 閉；W1＋W2＋W3＠08-18 已閉；W4／W5 另句。*
