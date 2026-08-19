---
title: 路徑／進出最佳化——操作計畫書 r18
status: adopted
series: s4_s5_verify
round: r18
role: 把 2026-08-19 已做的長短窗路徑、觀察篩、兩檔進出收成一份可重複執行的操作手冊（P0 已採納；不取代 r16 心跳、不取代 r18 全專案執行板）
date: 2026-08-19
viewpoint: 2026-08-19T13:01+08:00
layer: "[I]"
product_id: PATH-OPT-OPS-v1
adopted: audits/PATH-OPT-OPS-PLAN-ADOPTED-20260819.md
parent_ssot: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_r16_20260813.md
exec_nav: reports/augur_opt_stepwise_all_problems_r18_20260817.md
econ_path: reports/augur_econ_prove_edge_plan_r17_20260817.md
up_pull: reports/augur_uptrend_pullback_ls_top10_plan_r18_20260819.md
trend_pb: reports/augur_trend_pullback_model_catalog_verify_plan_r18_20260819.md
watch_pb: reports/augur_watch_pullback_inband_plan_r18_20260819.md
bull5: reports/augur_bull5_hstack_pullback_plan_r18_20260819.md
rs_charge: reports/augur_rs_charge_qihong_yanhua_plan_r18_20260819.md
twin_ex: reports/augur_twin_ex_qihong_yanhua_plan_r18_20260819.md
charge_t5: reports/augur_charge_t5_model_plan_r18_20260819.md
self_reported: true
---

# 路徑／進出最佳化——操作計畫書（2026-08-19）

> **一句**：日常出門仍是 standing **H20+H60 RankRidge**。本檔管的是旁邊那條「長窗定方向、短窗管進出」的**操作順序**：先閘、再觀察、再兩檔進出尺；每槍一張產品 ID、dry-run、不把條件當可交易。  
> **本檔＝已採納操作手冊**（`audits/PATH-OPT-OPS-PLAN-ADOPTED-20260819.md`）。採納 ≠ 改 standing、≠ #14、≠ 自動開未閉工作包。08-19＝假 B3；最近合法價頂＝**2026-08-18**。  
> **位階**：r18 全專案執行板的**子操作手冊**（M29–M35）。衝突時：開工順序以 r18 執行板為準；本族 θ／GO 文案以各軌長板為準。

---

## §0 護欄（每次開工先讀）

```text
PATH-OPT-OPS-v1 | no-fake-B3@08-19 | no-promote | no-SIM-apply | NF-pause
| standing=20,60 不改 | 路徑％ ≠ 未來漲跌幅％ | score／p_beat／IC ≠ 報酬％
| 觀察 ≠ 進場 | 條件 ≠ 可交易 | 做空名單 ≠ 可融券可成交
| 兩檔 ≠ 宇宙 | 禁 OOS 最長持有當冠 | 不套樣單檔％
| 不放寬 UP-PULL L-B | 不倒 canonical 31 | 探針零寫 prediction_values
| 改 θ＝新 ID | 混表＝禁
```

| 可 | 不可 |
|---|---|
| 對 **D ≤ 價頂** 做 dry-run 探針／格子 | 把 as-of 設成還沒進庫的日（現＝08-19） |
| 一槍一個 `product_id`，audit＋JSON | 把 UP-PULL／WATCH／RS-CHARGE 合成一張 Top10 卻只寫一個 ID |
| 抱牢、T20／T40 當**對照欄** | 用 2025–26 大多頭窗的最長持有當「最佳進出」 |
| 成本地板另欄（0.585%） | 無 GO 接 live 顧問、改 standing、sim `--apply` |

---

## §1 這族在最佳化什麼、不最佳化什麼

**要最佳化的**

1. **進場滿足點**：長窗已發生路徑定方向，短窗拉回／反彈／仍衝決定「現在能不能進、還是只能等」。  
2. **觀察池**：還沒過進場閘、但結構仍在的名字，標等回撤／等反彈。  
3. **進出規則（兩檔研究）**：在進出組合之間選較穩的一組；尺＝訓練／保留同號且都＞0、短持有優先，**不是**打敗抱牢。

**不要最佳化的**

- RankRidge 日常出門窗、promote、#14 確立、把路徑％當未來漲跌幅。  
- 把奇鋐 H5≈+10%、研華 dd20≈−2.7% 寫死成 θ。  
- 用全樣本或 OOS 複利最高（會選出抱牢）。

**凍結日曆**

| 窗 | 日 | 用途 |
|---|---|---|
| 最近合法 as-of | **2026-08-18** | 所有單日探針 |
| 假 B3 | 2026-08-19 | 禁止當 as-of |
| TWIN-EX IS | 2024-01-02～2024-12-31 | 選進出規則 |
| TWIN-EX OOS | 2025-01-02～2026-06-30 | 只驗證；出場須在 08-18 內結束 |
| 進場成交 | 訊號日 **t+1** 還原收盤 | 與 `label.forward_returns` 同口徑 |

---

## §2 產品地圖（禁止混 ID）

長窗 **L-A**＝H40／60／90／120／240 log 報酬全＞0。結構 **L-D**＝`cycle_position_252d ≥ 0.40` 且 `price_to_252d_high ≥ 0.80`（歷史日現算近 252 交易日還原高低；庫內 `feature_values` 不是每日）。L-C＝20 日高回撤 ∈ [−15%, −3%]。L-B＝H5 與 H10 全＜0。

| ID | 人話 | 硬閘 | 標籤 | 08-18 實況 | 狀態 |
|---|---|---|---|---|---|
| **UP-PULL-v1** | 長上＋短回 → 進場排序 | L-A∧L-B∧L-C∧L-D（空方鏡像） | 可當進場條件 | 做多 5／做空 2 | P0＋P1 閉 |
| **RIDGE-THEN-PB** | Ridge 八窗均分 Top10 當池，回撤近→遠 | 池不剔除；過齊四閘才叫進場 | 等回撤，不是進場 | 進場 0／0 | 已閉＠08-18 |
| **WATCH-PB-v1** | 已離高、短窗仍衝（全宇宙） | L-A∧L-C∧L-D∧¬L-B | 等回撤，不是進場 | 觀察多 13／空 6 | P0＋P1 閉 |
| **BULL5-v1** | 長線多頭、只跌近 5 日 | H10…H240 全＞0 ∧ H5＜0 | 條件≠進場 | 做多 9／空 1；∩進場＝0 | **P0＋P1 閉** |
| **RS-CHARGE-v1** | 相對強×仍在衝（無回撤帶） | Ridge Top10 ∩ L-A ∩ L-D ∩ H5＞0 ∩ H10＞0；**無 L-C** | 等回撤，不是進場 | 預診多 7／空 1（含奇鋐＋研華） | P0 閉；P1 另句 |
| **TWIN-EX-v1** | 奇鋐／研華進出（不要抱牢） | 進×出格子；T40 不當冠 | ≠可交易、≠宇宙 | 冠軍 E-charge×T5 | P0＋P1 閉 |
| **CHARGE-T5-v1** | 衝勢 5 日進出（新規則模型） | E-charge×T5；同日 k=10 等權 | ≠可交易；成本後 IS 負 | P0＋P1＠08-18 已閉 | P1 閉 |

**為什麼要分軌**：UP-PULL 進場故意排除「短窗還在衝」。WATCH 補那批。RS-CHARGE 再放掉 L-C，否則研華出局。BULL5 要的是「只有 H5 回跌」。TWIN-EX 只管兩檔的進出尺，不外推全市場。CHARGE-T5 才是把冠軍規則拿到宇宙的新 ID。Ridge 池與全宇宙觀察不得當成同一張表。

---

## §3 已閉操作（＠價頂 2026-08-18）

探針一律 dry-run、零寫 `prediction_values`。08-19 探針須 rc=3。

| 操作 | 指令／產物 | 結果 |
|---|---|---|
| UP-PULL P1 | `scripts/probe_uptrend_pullback.py` | n_long=5／n_short=2；strict 不足不補 |
| Ridge 標註 | copy-only | 八窗均分 Top10 全「等回撤」；∩進場＝0 |
| RIDGE-THEN-PB | `scripts/probe_ridge_then_pb.py` | 強／弱池各 10；可當進場 0／0 |
| TREND-PB W1–W3 | `scripts/probe_trend_pb_catalog.py` | C04∩T01＝0；T07∩T01＝0；T04 做多＝0 |
| WATCH-PB P1 | `scripts/probe_watch_pullback.py` | 觀察 13／6；∩進場＝0 |
| TWIN-EX P1 | `scripts/probe_twin_ex.py --tip 2026-08-18 --sids 3017,2395` | 冠軍 **E-charge×T5**：IS +56.8%（15／9）、OOS +72.9%（24／15）；成本 0.585% 後仍 +43.6%／+50.2% |
| CHARGE-T5 P1 | `scripts/probe_charge_t5.py --tip 2026-08-18` | 等權 k=10：IS 240 籃 **+43.8%**（成本後 **−64.8%**）；OOS +2181%（成本後 +210%；不當預期）；T20／T40 不當冠；兩檔無 k 對上舊帳 |
| 假 B3 閘 | `--date 2026-08-19` | rc=3 |

TWIN-EX 沒當冠（刻意）：WATCH×T20 的 OOS **+341%** 排合格組第 9。抱牢只對照（奇鋐起源→頂 +840%、研華 +93%）。

程式庫：`src/augur/evaluation/uptrend_pullback.py`、`src/augur/evaluation/twin_ex.py`、`src/augur/evaluation/charge_t5.py`。

---

## §4 標準操作（每一槍照抄）

```text
1. LIVE：python scripts/check_asof_ready.py --latest-date
         D 必須 ≤ PriceAdj TAIEX 價頂；大於價頂＝停
2. 只貼一條 GO（一個 product_id）。adopt ≠ probe ≠ emit
3. 先 --selftest，再 dry-run；禁止 --apply／寫 prediction_values
4. 產出：stdout 護欄句 + /tmp JSON + audits/*-EXECUTED + 必要時 canvas
5. 改 r18 M29–M35 狀態；本族長板 WP 打勾
6. 回 Steward：數字、≠可交易、下一槍 paste；不 commit 除非另句
```

**混用檢查（出表前）**

- 進場欄只有 UP-PULL 過齊四閘（或 RIDGE-THEN-PB 過齊者）。  
- 觀察欄不得寫「可當進場條件」。  
- 做空欄固定句：條件排序，不是下單、不是可融券可成交。  
- 兩檔格子不得寫成全宇宙最佳。  
- 分數、IC、路徑％旁邊必須有單位／口徑，禁止當報酬％。

**Python**：`/home/hugo/project/augur/venv/bin/python`。

---

## §5 開著的下一步（排序＝建議工時）

此刻全專案最佳下一步仍以 r18 決策卡為準：**等下一句 GO**。本族內部若要動，按下表，**不要一次開兩槍**。

| 序 | 項 | 可先？ | 為什麼是這個順序 | paste |
|---|---|---|---|---|
| 1 | **BULL5 P0 採納** | **已閉** | 閘凍結＝全正窗＋H5＜0 | — |
| 2 | **RS-CHARGE P1 探針＠08-18** | 是 | P0 已採納；預診 7／1 須正式閉 | `RS-CHARGE-probe-go` |
| 3 | **BULL5 P1 探針** | **已閉＠08-18** | n=9／1；∩進場＝0；與預診同序 | — |
| 4 | **TREND-PB W4** | 是 | W1–W3 已閉；截面分位族 | `TREND-PB-W4-go` |
| 5 | **UP-PULL／WATCH P2 OOS** | 探針已綠 | 單日名單 ≠ 預測力；H10 日曆閘仍在 | 各 `*-oos-walk-go` |
| 6 | **TREND-PB W5 共同 OOS** | W4 後或與 P2 合併 | IC ≠ 確立 | `TREND-PB-W5-go` |
| 7 | **CHARGE-T5 P0 採納** | **已閉** | 規則／T5／k=10／切窗凍結；≠宇宙驗證 | — |
| 8 | **CHARGE-T5／TWIN-EX 宇宙** | **已閉＠08-18** | 成本後 IS 負；T20／T40 不當冠；≠可交易 | — |
| 9 | **UP-PULL emit** | **否**（雙明示） | 不改 standing | `UP-PULL-emit-go` |
| — | B3 emit＠08-18 | 另族 | 仍 H20+H60；#14 誠實 | `B3-go`（本檔不開） |
| — | 停損／停利 θ | 禁（本版） | 兩檔會套死 θ | TWIN-EX-v1b 另句 |

**不要做**：假 B3＠08-19；把 TWIN-EX 冠軍接進顧問；為湊 Top10 放寬 L-B；把抱牢寫成本族操作；commit／push 無句。

---

## §6 GO 目錄（複製即貼）

採納本操作手冊（仍不自動開工）：

```text
PATH-OPT-OPS-plan-adopt | no-promote | standing=20,60 | no-fake-B3@08-19
| 觀察≠進場 | 條件≠可交易 | 兩檔≠宇宙 | 禁OOS最長持有當冠 | 做空≠可空
```

本族未閉（各一槍）：

```text
BULL5-plan-adopt | no-promote | standing=20,60 | no-fake-B3@08-19
| 全正窗＝H10…H240 | H5<0 | 不用累積遞減當多頭 | 條件≠可交易 | 做空≠可空
```

```text
RS-CHARGE-probe-go | date=2026-08-18 | k=10 | dry-run | 觀察≠進場
```

```text
BULL5-probe-go | date=2026-08-18 | k=10 | dry-run | 條件≠可交易
```

```text
TREND-PB-W4-go | date=2026-08-18 | families=T09,T10,C05 | k=10
```

```text
UP-PULL-oos-walk-go | origin=2026-07-31 | policy=strict | no-promote
```

```text
WATCH-PB-oos-walk-go | origin=2026-07-31 | no-promote
```

```text
CHARGE-T5-plan-adopt | no-promote | standing=20,60 | no-fake-B3@08-19
| 規則＝E-charge×T5 | 宇宙≠兩檔 | k=10 | 條件≠可交易 | 禁OOS最長持有當冠
```

```text
CHARGE-T5-universe-go | dry-run | IS=2024 OOS=2025-01..2026-06 | 不要抱牢
```

```text
TWIN-EX-universe-go | rule=E-charge,X-T5 | dry-run | 不要抱牢 | 兩檔≠宇宙
```

> CHARGE-T5-universe-go 與 TWIN-EX-universe-go **同一槍**。P0 已採納，用前者。

已閉、禁止當「還沒做」再貼一次當新工單（重跑須明示 `re-run`）：UP-PULL-probe-go、WATCH-PB-probe-go、TWIN-EX-grid-go、TREND-PB-W1/W2/W3-go、RIDGE-THEN-PB、CHARGE-T5-plan-adopt、CHARGE-T5-universe-go、TWIN-EX-universe-go。

---

## §7 與 r16／r18／#14

| 檔 | 角色 |
|---|---|
| r16 心跳 | 運轉 SSOT；本族不改 S1–S5 |
| r18 執行板 | **全專案開工順序**；本檔＝M29–M35 操作細節 |
| 確立路徑 r17 | #14；本族路徑％／兩檔複利 **≠** egate、≠ E5 |
| 各軌長板 | θ 與驗收的 SSOT |

TWIN-EX 冠軍在兩檔格子上**已證實工作假說**，仍標：≠可交易、≠改 standing。CHARGE-T5 宇宙走步＠08-18 **已閉**：無成本兩窗正、成本後訓練窗為負；OOS 大數不當預期；T20／T40 不當冠。兩檔 39 筆％**不是** CHARGE-T5 的產品績效。不得繞過 #14。

---

## §8 工作包

### WP-P0｜採納本操作手冊 ✅

```text
WHEN: Steward 貼 PATH-OPT-OPS-plan-adopt
DO:   本檔 status → adopted；寫 audits/PATH-OPT-OPS-PLAN-ADOPTED-20260819.md；r18 §6 掛本檔
DONT: 自動開 BULL5／RS-CHARGE／W4／OOS／宇宙／emit
DONE: 2026-08-19 ADOPTED；操作協議凍結；各軌長板 θ 不改
```

### WP-P1｜依 §5 單槍執行

```text
WHEN: Steward 貼 §6 其中一條（且僅一條）
DO:   照該軌長板 WP；本檔 §5 列狀態
DONT: 順便再開下一槍；假 B3；寫庫
DONE: 該槍 EXECUTED audit
```

---

## §9 驗收（本計畫書）

- [x] 六軌 ID、閘、標籤、禁止混表寫在同一張地圖  
- [x] 已閉＠08-18 的數字與產物列清  
- [x] 標準操作 6 步＋假 B3 閘  
- [x] 開著的下一步有排序與 paste  
- [x] 明示不取代 r16／r18、不把兩檔當宇宙、不把進出當可交易  
- [x] P0 採納  

*完。[I] · adopted · 操作手冊；未閉槍另句。*
