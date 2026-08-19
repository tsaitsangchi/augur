---
title: 長線結構 × 短線進出——做多／做空 Top10 計畫書 r18
status: adopted
series: s4_s5_verify
round: r18
role: 長線結構×短線進出兩段閘 → 做多／做空 Top10（已採納；P1 探針＠08-18 已閉）
date: 2026-08-19
viewpoint: 2026-08-19T08:40+08:00
layer: "[I]"
parent_ssot: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_r16_20260813.md
exec_nav: reports/augur_opt_stepwise_all_problems_r18_20260817.md
econ_path: reports/augur_econ_prove_edge_plan_r17_20260817.md
philosophy: src/augur/philosophy/framework.py
adopted: audits/UP-PULL-LS-TOP10-PLAN-ADOPTED-20260819.md
locked_policy: strict
locked_k: 10
self_reported: true
---

# 長線結構 × 短線進出——做多／做空 Top10 計畫書（2026-08-19）

> **一句**：在**最近合法 as-of**（現＝**2026-08-18**；08-19 價未進＝假 B3）對核心宇宙做兩段硬閘——**做多＝長窗往上＋短窗拉回**、**做空＝長窗往下＋短窗反彈**——再在過閘集合裡排序，輸出做多 Top10 與做空 Top10。  
> **本檔＝已採納計畫**（`audits/UP-PULL-LS-TOP10-PLAN-ADOPTED-20260819.md`）。P1 探針＠08-18 **已閉**（`audits/UP-PULL-PROBE-0818-EXECUTED-20260819.md`；strict n_long=5／n_short=2）。P2／P1b／P3／P4 另句。不取代 standing RankRidge H20+H60、不 promote、不 sim-apply、不塗 established。  
> **凍結**：`policy=strict` · `k=10` · 做空≠可空 · 路徑％≠未來％。  
> **預診（唯讀＠08-18，硬閘）**：做多過齊 **5** 檔；做空過齊 **2** 檔。strict＝不足不補。  
> **與同類目錄**：市場規則閉集見 `reports/augur_trend_pullback_model_catalog_verify_plan_r18_20260819.md`（**已採納**；T01＝本檔 v1）。W1 另句，不在本槍默開。

---

## §0 護欄

```text
UP-PULL-LS-top10-plan | no-fake-B3 | no-promote | no-SIM-apply | NF-pause
| standing=20,60 不改 | 過去路徑％ ≠ 未來漲跌幅％ | score ≠ 報酬％
| 做空名單 ≠ 可融券可成交 | 不救 H20 | 不放寬 DSR | 不倒 canonical 31
| 不取代 RankRidge 出門 | 探針零寫 prediction_values（除非另句）
```

| 可 | 不可 |
|---|---|
| 規則探針／歷史 as-of walk（stamp＜panel） | 把探針名單當可交易、當 #14 已過 |
| 過閘不足 10 檔就**如實少列** | 為湊滿 10 暗改 θ |
| 連續分數「軟名單」當**另欄**（標 soft） | 軟硬混成同一張 Top10 卻不標 |
| 點名後才訓交互模型 | 無 GO 改 prodset／SERVE-SWAP |

**與現役 RankRidge 的關係**：Ridge＠08-18 實際 3 欄，把 `cycle_position_252d` 高、借券費低排前面（貼年線高點）。本計畫要的是**高位拉回／低位反彈**，是**另一條產品軌**，並列、不覆蓋。

**台股做空**：名單是「空方條件排序」，不是下單指令。平盤下禁空、無券、擔保維持率、成本地板 **0.585%** 未計入探針。

---

## §1 問題定義（唯一口徑）

### 1.1 要什麼

給定 as-of 日 D＝`min(指定日, PriceAdj TAIEX 價頂)`，核心宇宙＠D：

1. **做多條件**（兩段，缺一不可）  
   - 長線整體往上：H**40／60／90／120／240** 的**已發生**還原 log 報酬全＞0。  
   - 短線已拉到滿足點：H**5 與 10** 全＜0，且現價相對近 20 日高點回撤 ∈ **[−15%, −3%]**，且結構未破。
2. **做空條件**（鏡像）  
   - 長線整體往下：同一組長窗 log 報酬全＜0。  
   - 短線已反彈到滿足點：H**5 與 10** 全＞0，且現價相對近 20 日低點反彈 ∈ **[+3%, +15%]**，且結構未修。
3. **輸出**：做多 Top10、做空 Top10（過閘集合內排序；不足則全列＋`n<k` 旗）。

### 1.2 不要什麼（八窗不能同時「現在都往上」）

5／10／20 若也要求與 240 日一樣「現在為正」，就沒有拉回，只會再找出光寶科那種貼高點的股票。  
**長窗管結構，短窗管進出。** H20 可作觀察欄，**不**進硬閘（與 H5／H10 同向時會吃掉滿足點；與長窗同向時又太寬）。

### 1.3 標籤與特徵（庫內）

| 量 | 算法 | 現成欄？ |
|---|---|---|
| H∈{5,10,20,40,60,90,120,240} 路徑 | `log(P_D / P_{D−H})`，P＝還原收盤，H＝交易日 | 5／20／60／120／252 有 `momentum_*d`；**10／40／90／240 須現算** |
| 20 日高回撤 | `P_D / max(P_{D−19…D}) − 1` | 無；現算 |
| 20 日低反彈 | `P_D / min(P_{D−19…D}) − 1` | 無；現算 |
| 結構未破（多） | `cycle_position_252d ≥ 0.40` 且 `price_to_252d_high ≥ 0.80` | 有 |
| 結構未修（空） | `cycle_position_252d ≤ 0.60` 且 `price_to_252d_high ≤ 0.90` | 有 |

哲學對照（非證明）：中期動能正向（60／120／252）；極短窗反轉（`return_1d`／`momentum_5d`）。本計畫是把兩者**拆閘**，不是再把年線位置正向塞進 Ridge。

### 1.4 不是什麼

| 常被誤認 | 為什麼不夠 |
|---|---|
| RankRidge 八窗均分 Top10 | 高位相對強，幾乎無拉回 |
| 相對弱 Top10 當抄底／當空 | 年線低＋借券費高＝跌破，不是「結構往下＋短彈」 |
| 探針名單後來漲了 | 單期軼事；未扣成本、未對基準 |
| 做空 Top10 | ≠ 可空、≠ 已確立 |

---

## §2 硬閘（凍結；改數字＝新變體、另記 N）

記名 **UP-PULL-v1**。改任一 θ 須改名（v1b／v2），禁止同一 JSON 混版本。

### 2.1 做多 `long`（四閘 AND）

| 閘 | 條件 | 08-18 核心宇宙漏斗 |
|---|---|---|
| L-A | H40、60、90、120、240 log 報酬 **全＞0** | 47 |
| L-B | H5＜0 **且** H10＜0 | 7（在 L-A 內） |
| L-C | 20 日高回撤 ∈ **[−0.15, −0.03]** | 5 |
| L-D | `cycle_position_252d ≥ 0.40` 且 `price_to_252d_high ≥ 0.80` | **5** |

### 2.2 做空 `short`（四閘 AND，鏡像）

| 閘 | 條件 | 08-18 漏斗 |
|---|---|---|
| S-A | H40、60、90、120、240 log 報酬 **全＜0** | 30 |
| S-B | H5＞0 **且** H10＞0 | 5（在 S-A 內） |
| S-C | 20 日低反彈 ∈ **[+0.03, +0.15]** | 2 |
| S-D | `cycle_position_252d ≤ 0.60` 且 `price_to_252d_high ≤ 0.90` | **2** |

### 2.3 預診名單（規則通過＝已發生路徑，**不是預測**）

**做多 5 檔＠08-18**（v1 序＝mean(H60,120,240)）：3231 緯創、2377 微星、2006 東和鋼鐵、1907 永豐餘、3293 鈊象。  
**做空 2 檔＠08-18**：1215 卜蜂、8099 大世科。

詳見先前探針；本計畫不把此 7 檔當訊號。

---

## §3 過閘後如何變成「Top10」（排序契約）

硬閘先濾，再排序。**禁止**用 RankRidge score 當本軌序位。

### 3.1 做多序（高→低）

主鍵：`mean(ret_60, ret_120, ret_240)` 降序（長窗愈強愈前）。  
次鍵：回撤深度距甜蜜帶中點 −8% 的絕對差 **升序**（太淺／太深往後）。  
三鍵：`stock_id` 升序（穩序）。

### 3.2 做空序（空方條件強→弱）

主鍵：`mean(ret_60, ret_120, ret_240)` **升序**（長窗愈負愈前）。  
次鍵：反彈幅度距中點 +8% 的絕對差升序。  
三鍵：`stock_id` 升序。

### 3.3 填滿政策（必須三選一，預設 **strict**）

| 政策 | 行為 | 何時用 |
|---|---|---|
| **strict**（預設） | 過閘幾檔列幾檔；`n_long`／`n_short` 寫進 JSON；不足 10 **不補** | 誠實盤、本計畫 P1 |
| **soft-fill** | 另算連續分數（無硬閘）取滿 10，欄位 `tier=soft` | 要「永遠 10 檔」的展示；**不得與 strict 混標** |
| **relax-A** | 長窗改「5 中≥4」——**v1b**，另 GO | 樣本太稀；須重跑 OOS，另付 N |

08-18 預診：strict → 做多 5／做空 2。若 Steward 要「畫面永遠 10+10」，只准 **soft-fill 另欄**，不准把 soft 寫成硬閘通過。

**soft-fill 分數（僅 P1b，不進 v1 硬閘）**：

- 多方：`z(mean(m60,m120,m252)) + z(−m5) + z(−return_1d)`，再剔除 `cycle_position>0.98`（已在高點無進出）。  
- 空方：`z(−mean(m60,m120,m252)) + z(m5) + z(return_1d)`，再剔除 `cycle_position<0.05`（已崩）。

---

## §4 分階執行（Phase）

### Phase 0｜凍結定義（本檔；零碼可閉）

驗收：Steward 確認 §2 θ、§3 序、§3.3 政策＝strict 或明示 soft-fill。  
GO：`UP-PULL-plan-adopt`

### Phase 1｜探針殼（最近日 → JSON → Top 表）✅ 已閉＠08-18

**已跑**（2026-08-19；as-of＝2026-08-18＝價頂）。零寫 `prediction_values`。strict n_long=**5**／n_short=**2**。audit＝`audits/UP-PULL-PROBE-0818-EXECUTED-20260819.md`。

擬議：

```text
python scripts/probe_uptrend_pullback.py --date 2026-08-18 --side both --k 10 --policy strict
# 假 B3 → rc=3；D>價頂拒絕
# stdout：做多／做空表；JSON /tmp/up-pull-{asof}-strict.json
```

驗收：

- `check_asof_ready` 過才跑。  
- 每檔列出八窗**已發生**路徑％、回撤／反彈、cycle、p2h、閘位元。  
- 表頭固定：「已發生路徑，不是未來漲跌幅；≠可交易」。  
- `--selftest`：鏡像（把報酬變號 → 多空集合對調）、θ 邊界、假 B3。

GO：`UP-PULL-probe-go | date=2026-08-18 | side=both | k=10 | policy=strict`

### Phase 1b｜soft-fill（可選，另句）

同一腳本 `--policy soft-fill`，輸出第二張表。不覆蓋 strict。

### Phase 2｜歷史 as-of OOS（這條軌有沒有預測力）

客體：過閘日 D 之後的**未來**橫斷面相對名次／log 報酬（entry＝D 的下一交易日，持有 H∈{5,10,20,60}，以標籤已實現者為限）。  
尺：過閘集合 vs 核心宇宙其餘；做多看後續相對強、做空看後續相對弱；**IC ≠ 確立 ≠ 報酬％**。  
`--oos`：閘只用 ≤D 可見價；禁未來高點。  
H10 日曆閘仍在：評 H10 須 panel 後 ≥11 交易日。

GO：`UP-PULL-oos-walk-go | origin=2026-07-31 | policy=strict | no-promote`  
未過 Phase 2 不得宣稱「找出可進場滿足點」。

### Phase 3｜模型化（延後；點名才訓）

僅當 Phase 2 顯示硬閘集合的未來相對名次穩定優於隨機。  
做法：交互特徵（長窗動能 × 短窗反轉），**新 family 名**（例 `PullbackLS`），不改 RankRidge 3 欄包。  
禁倒 canonical 31。禁 SERVE-SWAP。

GO：`UP-PULL-model-go | family=PullbackLS | asof=<價頂> | no-promote`

### Phase 4｜產品輸出（最終形態）

日更 as-of 後（B3 之後、讓路 LLM）：跑 P1 → 顧問／畫布兩欄「做多 Top10／做空 Top10」。  
**不**寫進日常 `prediction_values` standing（仍 H20+H60 RankRidge），除非雙明示改殼。  
做空欄硬綁：「條件排序，非下單、非可空確認」。

GO：`UP-PULL-emit-go | standing-unchanged | dry-run 先`

### 本檔附：標註 Ridge（copy-only；非 P4 emit）✅

```text
WHEN: Steward 貼 UP-PULL-annotate-ridge-go | asof=2026-08-18 | copy-only | dry-run
DO:   Ridge 八窗均分 Top10 加「等回撤；≠進場」；進場欄＝UP-PULL-v1 strict
DONT: 寫 prediction_values；改 standing；接 live 顧問；寫成「等回跌」
DONE: 2026-08-19 EXECUTED；10／10 等回撤；∩進場＝0；做多 5／做空 2
```

### 本檔附：RIDGE-THEN-PB（強池回撤／弱池反彈；非 P4 emit）✅

```text
WHEN: Steward 人話 GO：相對強池回撤近→遠；相對弱池反彈近→遠
DO:   兩池不剔除；過齊四閘才「可當進場條件」；做空標「等反彈」且≠可空
DONT: 寫 prediction_values；改 standing；沿用 UP-PULL-v1 產品 ID；把分數當％
DONE: 2026-08-19 EXECUTED＠08-18；n_pool=10／10；n_entry=0／0；做空≠可空
```

### 本檔不開

解凍 NF；sim `--apply`；八窗改 standing；evaluate／approve `dgate_*`；E5；把 H20 塗綠；為湊 10 檔改 L-A／S-A 卻沿用 v1 名稱。

---

## §5 工作包（開跑複製）

### WP-P0｜採納定義

```text
WHEN: Steward 貼 UP-PULL-plan-adopt
DO:   本檔 status → adopted；寫 audits/UP-PULL-LS-TOP10-PLAN-ADOPTED-20260819.md
DONT: 當日就當可交易名單
DONE: audit 存在；θ 未改
```

### WP-P1｜探針＠最近日 ✅

```text
WHEN: 價頂 D 已 ready 且非 B3 開火；Steward 貼 UP-PULL-probe-go
DO:   scripts/probe_uptrend_pullback.py --date <D> --side both --k 10 --policy strict
DONT: 寫 prediction_values；假 B3；用 Ridge score 排序
DONE: 2026-08-19 EXECUTED；asof=2026-08-18；n_long=5 n_short=2；selftest 綠
```

### WP-P2｜OOS walk

```text
WHEN: P1 殼綠；Steward 貼 UP-PULL-oos-walk-go
DO:   對已實現窗的歷史 D 重跑閘＋未來相對名次
DONT: 同日 stamp；不足樣本卻報勝
DONE: audit；IC／名次差標 ≠確立
```

---

## §6 與 r18 執行板

| 本計畫 | 可先？ | 可同步？ | 備註 |
|---|---|---|---|
| P0 採納 | 是 | 是 | 零碼 |
| P1 探針＠08-18 | **已閉** | — | n_long=5／n_short=2；08-19 仍假 B3 |
| P1b soft-fill | 否（另句） | 是 | 展示用 |
| P2 OOS | 探針後 | 讓 B3／長訓 | H10 日曆閘仍在 |
| P3 模型 | 否 | 否 | 點名 GO |
| P4 emit | 否 | 否 | 不改 standing |
| 標註 Ridge copy-only | **已閉＠08-18** | — | 10／10 等回撤；∩進場＝0；未接 live |
| RIDGE-THEN-PB | **已閉＠08-18** | — | 強池回撤＋弱池反彈；進場 0／0；做空≠可空 |
| WATCH-PB 觀察篩 | **已閉＠08-18** | — | 觀察多 13／空 6；展示 10／6；∩進場＝0 |
| 全專案心跳 | — | — | 仍候下一交易日 B3；本軌不擋 |

建議 paste（採納本檔、仍不開工探針）：

```text
UP-PULL-plan-adopt | policy=strict | k=10 | no-promote | standing=20,60
| no-fake-B3 | 做空≠可空 | 路徑％≠未來％
```

探針開工另貼：

```text
UP-PULL-probe-go | date=2026-08-18 | side=both | k=10 | policy=strict
```

---

## §7 驗收（本計畫書）

- [x] 做多／做空兩段條件寫成可機算硬閘（鏡像）  
- [x] 過閘 → Top10 的排序鍵寫死  
- [x] 不足 10 檔的填滿政策寫死（預設 strict）  
- [x] 分階到「可輸出兩張 Top10」：P1 即能輸出；P2 才談有沒有用；P4 才進產品殼  
- [x] 與 RankRidge 出門隔離；#14／做空可成交未假裝完成  
- [x] 08-18 預診漏斗入檔（多 5／空 2），避免以為「計畫＝已有 10+10」

*完。[I] · adopted · P0 閉；P1 探針＠08-18 已閉（strict 5／2）；P2／P1b／P3／P4 另句。*
