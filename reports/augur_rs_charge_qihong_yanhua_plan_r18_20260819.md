---
title: 相對強 × 長窗多 × 短窗仍衝——奇鋐／研華交集計畫書 r18
status: adopted
series: s4_s5_verify
round: r18
role: 把 3017 奇鋐與 2395 研華的交集硬閘落成可機算觀察篩（無 20 日高回撤帶；不是進場；P0 已採納；P1 另句）
date: 2026-08-19
viewpoint: 2026-08-19T11:05+08:00
layer: "[I]"
product_id: RS-CHARGE-v1
adopted: audits/RS-CHARGE-PLAN-ADOPTED-20260819.md
parent_ssot: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_r16_20260813.md
exec_nav: reports/augur_opt_stepwise_all_problems_r19_20260819.md
up_pull: reports/augur_uptrend_pullback_ls_top10_plan_r18_20260819.md
watch_pb: reports/augur_watch_pullback_inband_plan_r18_20260819.md
bull5: reports/augur_bull5_hstack_pullback_plan_r18_20260819.md
econ_path: reports/augur_econ_prove_edge_plan_r17_20260817.md
locked_k_ridge: 10
self_reported: true
---

# 相對強 × 長窗多 × 短窗仍衝（2026-08-19）

> **一句**：用 **3017 奇鋐**與 **2395 研華**＠**2026-08-18** 的**交集**當硬閘——相對強、長窗往上、結構未破、近 5／10 日都還在漲——**不**要求已距 20 日高 −15%～−3%（否則研華出局）。名單一律「等回撤，不是進場」。  
> **本檔＝已採納計畫**（`audits/RS-CHARGE-PLAN-ADOPTED-20260819.md`）。採納 ≠ 探針已閉；探針另句 `RS-CHARGE-probe-go`。不用兩檔的 H5／H10／回撤％當門檻。不改 UP-PULL／WATCH-PB／BULL5／standing。08-19＝假 B3。

---

## §0 護欄

```text
RS-CHARGE-v1 | no-fake-B3@08-19 | no-promote | no-SIM-apply | NF-pause
| standing=20,60 不改 | 路徑％ ≠ 未來漲跌幅％ | score ≠ 報酬％
| 觀察 ≠ 進場 | 做空 ≠ 可空 | 不放寬 L-B | 不套樣單檔％
| 不倒 canonical 31 | 探針零寫 prediction_values | 改 θ＝新 ID
```

| 可 | 不可 |
|---|---|
| 交集硬閘＋Ridge 池 | 把奇鋐 H5≈+10%、研華 dd≈−2.7% 寫成 θ |
| 與 WATCH／BULL5／UP-PULL 並列 | 混成同一張 Top10 卻沿用別軌 ID |
| 之後另句 OOS | 無 GO 改 standing／promote |

樣板日＝最後交易日 **2026-08-18**（庫裡最後一盤還原價）。兩檔只用來**發現交集**；規則過閘後允許別人進來（＠08-18 Ridge 池另有光寶科、台光電、潤泰新、厚生、正隆）。

---

## §1 兩檔各自有什麼、交集只留什麼

| 項 | 奇鋐 | 研華 | 進 v1？ |
|---|---|---|---|
| Ridge 八窗均分相對強 Top10 | 原序 9 | 原序 5 | **是（池）** |
| L-A 長窗全正 | 是 | 是 | **是** |
| L-D 結構未破 | 是 | 是 | **是** |
| H5＞0 且 H10＞0 | +10.0%／+16.7% | +2.7%／+17.9% | **是（只留正負，不留％）** |
| L-C 距 20 日高 ∈[−15%,−3%] | −6.2% **過** | −2.7% **不過** | **否**（要兩檔都在就必須拿掉） |
| UP-PULL 四閘／BULL5（H5＜0） | 否 | 否 | **否** |

禁止寫進 θ：H240 +202% vs +119%、cycle 精確值、Ridge 均分必須 0.54。

---

## §2 硬閘（凍結）

記名 **RS-CHARGE-v1**。路徑＝還原收盤 logret；H＝交易日。

### 2.1 池

RankRidge 八窗分數都有，依八窗**平均分數**高→低取 Top **k=10**（dry-run，不寫 `prediction_values`）。  
分數無單位、≠漲跌幅％。

### 2.2 做多 `charge_long`（在池內 AND）

| 閘 | 條件 |
|---|---|
| RC-A | L-A：H40／60／90／120／240 log 報酬全＞0 |
| RC-D | L-D：`cycle_position_252d ≥ 0.40` 且 `price_to_252d_high ≥ 0.80` |
| RC-S | H5＞0 **且** H10＞0 |

**不**用 L-C。不足 k **不補**（strict）。

### 2.3 做空鏡像 `charge_short`

相對弱 Top10 池；S-A 長窗全負；S-D 結構未修；H5＜0 且 H10＜0。  
標「等反彈，不是進場」。≠可空。預診＠08-18 僅 **1** 檔（3548 兆利）——如實少列。

### 2.4 標籤

做多一律「等回撤，不是進場」。**禁止**「可當進場條件」（那是 UP-PULL 四閘）。

---

## §3 排序與展示

池內過閘後：主鍵 Ridge 八窗均分 **降序**（相對強仍在前）；次鍵 `stock_id`。  
**不用**回撤深度排序（那是 RIDGE-THEN-PB；本軌刻意不靠 L-C）。

JSON 全列過閘者。stdout 即該列（＠08-18 預診 7＜10）。

---

## §4 預診＠2026-08-18（已發生路徑，**不是預測**；**不是 P1 已閉**）

Ridge 強 Top10 過 RC-A／D／S：**7** 檔（剔除台積電／聯發科／致茂：長窗未全正或 H5 未嚴格為正）。

| Ridge原序 | 代號 | 名稱 | H5 | H10 | 距20日高 | L-C |
|---|---|---|---|---|---|---|
| 1 | 2301 | 光寶科 | +1.9% | +8.5% | 0.0% | 否 |
| 3 | 2383 | 台光電 | +12.1% | +20.7% | −2.3% | 否 |
| 4 | 9945 | 潤泰新 | +9.8% | +11.2% | −1.7% | 否 |
| 5 | 2395 | **研華** | +2.7% | +17.9% | −2.7% | 否 |
| 6 | 2107 | 厚生 | +1.8% | +2.2% | 0.0% | 否 |
| 7 | 1904 | 正隆 | +0.2% | +15.0% | −2.4% | 否 |
| 9 | 3017 | **奇鋐** | +10.0% | +16.7% | −6.2% | 是 |

∩ UP-PULL 做多進場＝**0**。∩ WATCH-PB＝僅奇鋐（WATCH 要 L-C）。  
全宇宙同閘不加 Ridge 池＝28 檔；本 v1 **不**用全宇宙當池（要相對強）。改池＝**RS-CHARGE-UNI-v1** 另句。

預診唯讀，未寫庫。

---

## §5 與已有軌

| 軌 | 差別 |
|---|---|
| RIDGE-THEN-PB | 同 Ridge Top10 池，但**不剔除**、依回撤近→遠；本軌**剔除**未過 RC-A／D／S |
| WATCH-PB | 全宇宙＋**要** L-C；研華不在 |
| BULL5 | 要 H5＜0；兩檔都不在 |
| UP-PULL 進場 | 要 H5 與 H10 雙負＋L-C；兩檔都不在 |

---

## §6 工作包

### WP-P0｜採納 ✅

```text
WHEN: Steward 貼 RS-CHARGE-plan-adopt
DO:   本檔 status → adopted；寫 audits/RS-CHARGE-PLAN-ADOPTED-20260819.md
DONT: 把 §4 預診當買點；不自動開 P1；不改他軌 θ
DONE: 2026-08-19 ADOPTED；θ 未改；他軌未改；P1 未開
```

### WP-P1｜探針

```text
WHEN: 價頂 D ready 且非 B3；Steward 貼 RS-CHARGE-probe-go
DO:   新腳本 scripts/probe_rs_charge.py --date <D> --k 10（採納後才寫）
DONT: 寫 prediction_values；假 B3；標可當進場條件；用單檔％
DONE: n；含 3017 與 2395＠08-18；∩進場＝0；selftest 綠
```

### WP-P2｜OOS

```text
WHEN: P1 殼綠；Steward 貼 RS-CHARGE-oos-walk-go
DO:   歷史 D 重跑＋已實現相對名次
DONT: 同日 stamp；兩檔軼事當勝
DONE: ≠確立
```

---

## §7 與 r18

| 本計畫 | 可先？ | 備註 |
|---|---|---|
| P0 採納 | **已閉** | 觀察≠進場；無 L-C；不套樣％ |
| P1 探針 | 採納後 | 預診 7／1 |
| P2 OOS | 探針後 | 單日兩檔 ≠ 證明 |
| emit／standing | **否** | |

採納：

```text
RS-CHARGE-plan-adopt | no-promote | standing=20,60 | no-fake-B3@08-19
| pool=Ridge八窗均分Top10 | L-A∧L-D∧H5>0∧H10>0 | 無L-C | 觀察≠進場 | 做空≠可空
```

探針另貼：

```text
RS-CHARGE-probe-go | date=2026-08-18 | k=10 | dry-run | 觀察≠進場
```

---

## §8 驗收

- [x] 兩檔交集寫成硬閘；L-C 明確排除  
- [x] 禁止單檔％套樣寫死  
- [x] 預診＠08-18：7 檔含奇鋐＋研華；∩進場＝0  
- [x] 與 RIDGE-THEN-PB／WATCH／BULL5／UP-PULL 邊界寫死  
- [x] P0 採納  
- [ ] P1 探針  

*完。[I] · adopted · 預診＠08-18 唯讀；P1 未閉。*
