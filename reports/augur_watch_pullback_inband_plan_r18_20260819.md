---
title: 已離高、短窗仍衝——全宇宙觀察篩計畫書 r18
status: adopted
series: s4_s5_verify
round: r18
role: 從核心宇宙挑「長窗仍上＋已距 20 日高 −15%～−3%＋結構未破＋短窗尚未雙負」的觀察名單（不是進場；P0 已採納；P1＠08-18 已閉）
date: 2026-08-19
viewpoint: 2026-08-19T10:38+08:00
layer: "[I]"
product_id: WATCH-PB-v1
adopted: audits/WATCH-PB-PLAN-ADOPTED-20260819.md
parent_ssot: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_r16_20260813.md
exec_nav: reports/augur_opt_stepwise_all_problems_r18_20260817.md
up_pull: reports/augur_uptrend_pullback_ls_top10_plan_r18_20260819.md
ridge_then_pb: audits/RIDGE-THEN-PB-LS-0818-EXECUTED-20260819.md
econ_path: reports/augur_econ_prove_edge_plan_r17_20260817.md
probe: scripts/probe_watch_pullback.py
locked_k_display: 10
self_reported: true
---

# 已離高、短窗仍衝——全宇宙觀察篩（2026-08-19）

> **一句**：在**最後交易日**（庫裡最後一盤還原價，現＝**2026-08-18**；08-19＝假 B3）對核心宇宙做觀察篩——**長窗仍往上、已經離開 20 日高 −15%～−3%、結構未破、但近 5／10 日還沒雙負**。名單一律標「等回撤，不是進場」。鏡像空方標「等反彈，不是進場」，且≠可空。  
> **本檔＝已採納計畫**（`audits/WATCH-PB-PLAN-ADOPTED-20260819.md`）。P1 探針＠08-18 **已閉**。P2 另句。不取代 standing RankRidge H20+H60、不 promote、不把觀察寫成進場、不放寬 UP-PULL L-B。  
> **為什麼另開一軌**：RIDGE-THEN-PB 只在 Ridge 相對強 Top10 裡找，會漏掉不在前 10、但同樣「已離高、短窗還在衝」的名字（＠08-18 預診：全宇宙 13 檔觀察多，Ridge 強池只抓到奇鋐 1 檔）。UP-PULL-v1 進場閘故意排除這型。

---

## §0 護欄

```text
WATCH-PB-v1 | no-fake-B3@08-19 | no-promote | no-SIM-apply | NF-pause
| standing=20,60 不改 | 過去路徑％ ≠ 未來漲跌幅％ | score ≠ 報酬％
| 觀察 ≠ 進場 | 做空名單 ≠ 可融券可成交 | 不救 H20 | 不放寬 DSR
| 不倒 canonical 31 | 不取代 RankRidge 出門 | 探針零寫 prediction_values
| 不把 L-B 放寬後沿用 UP-PULL-v1 | 不用單檔 H5／H10 ％去套樣
```

| 可 | 不可 |
|---|---|
| 全宇宙規則篩（不從 Ridge Top10 生） | 把觀察名單當買點、當 #14 已過 |
| JSON 全列；stdout 截展示 k | 為湊 10 暗改 θ |
| 與 UP-PULL 進場欄並列（兩欄不同 ID） | 觀察／進場混成同一張 Top10 卻不標 |
| 之後另句 OOS walk | 無 GO 改 prodset／SERVE-SWAP |
| 空方鏡像觀察 | 寫成可空、可融券、可下單 |

**與 UP-PULL-v1**：進場＝四閘 AND（含 L-B／S-B）。本軌＝同一組 A／C／D，但**要求尚未** B。集合不相交（預診∩＝0）。改任一 θ＝新 ID（v1b），禁止同一 JSON 混版本。

**與 RIDGE-THEN-PB**：那條是「相對強／弱 Top10 當池，不剔除，再依回撤／反彈近→遠」。本軌**先**用硬閘從全宇宙篩，**不用** Ridge 分數進池、也不用它排序。

**與現役 RankRidge**：Ridge 管相對強弱出門（standing 20,60）。本軌不管分數。可選在 JSON 附註「是否也在當日 Ridge 強 Top10」，只當對照，不當閘。

---

## §1 問題定義（唯一口徑）

### 1.1 要什麼

給定 as-of 日 D＝`min(指定日, PriceAdj TAIEX 價頂)`，核心宇宙＠D、八窗路徑可算者：

1. **觀察多（奇鋐這型）**  
   - 長窗往上：H**40／60／90／120／240** 已發生還原 log 報酬全＞0（L-A）。  
   - 已離 20 日高：現價／近 20 日高 − 1 ∈ **[−15%, −3%]**（L-C）。  
   - 結構未破：`cycle_position_252d ≥ 0.40` 且 `price_to_252d_high ≥ 0.80`（L-D）。  
   - **短窗尚未拉完**：H5、H10 **不是**雙負（¬L-B）。即至少一窗 ≥0。
2. **觀察空（鏡像）**  
   - 長窗往下（S-A）、已離 20 日低 ∈ **[+3%, +15%]**（S-C）、結構未修（S-D）、H5／H10 **不是**雙正（¬S-B）。
3. **標**：觀察多一律「等回撤，不是進場」；觀察空一律「等反彈，不是進場」。**禁止**標「可當進場條件」。
4. **輸出**：過篩全列（`n_watch_*`）；展示欄預設 Top **k=10**（超過截、不足不補）。

### 1.2 不要什麼

| 常被誤認 | 為什麼不做 |
|---|---|
| 用奇鋐＠08-18 的 H5≈+10%、H10≈+17% 當門檻 | 單日單檔樣子，不是規則 |
| 從 Ridge 相對強 Top10 當池 | 漏掉不在前 10 的同型（預診漏 12 檔） |
| 把 L-B 放寬、沿用 UP-PULL-v1 | 進場閘故意不要「短窗還在衝」 |
| 觀察名單後來漲了 | 單期軼事；未扣成本、未對基準 |
| 八窗分數高低 | 本軌不排序、不進閘 |

**長窗管結構，短窗管「還沒進出」。** 已離高點只說明相對 20 日高的位置；近 5／10 日仍漲＝還在追這段，不是買點。

### 1.3 標籤與特徵

與 UP-PULL 計畫書 §1.3 同一套現算（八窗 logret、20 日高回撤、20 日低反彈、cycle、p2h）。不灌 RSI／SMA 進 prodset。

---

## §2 硬閘（凍結；改數字＝新變體）

記名 **WATCH-PB-v1**。

### 2.1 觀察多 `watch_long`（四項 AND）

| 閘 | 條件 | 08-18 預診（核心宇宙可算 284） |
|---|---|---|
| L-A | H40、60、90、120、240 log 報酬全＞0 | 47 |
| L-C | 20 日高回撤 ∈ **[−0.15, −0.03]** | （與 L-A、L-D 同時） |
| L-D | cycle≥0.40 且 p2h≥0.80 | （與 L-A、L-C 同時） |
| ¬L-B | H5、H10 **並非**全＜0 | **13**＝觀察多 |

L-A∧L-C∧L-D 共 18；其中 L-B 已過＝5（＝UP-PULL 進場多），其餘 13＝本軌。  
本軌 ∩ UP-PULL 做多進場＝**0**（構造如此）。

### 2.2 觀察空 `watch_short`（鏡像）

| 閘 | 條件 | 08-18 預診 |
|---|---|---|
| S-A | 長窗 log 報酬全＜0 | 30 |
| S-C | 20 日低反彈 ∈ **[+0.03, +0.15]** | （與 S-A、S-D 同時） |
| S-D | cycle≤0.60 且 p2h≤0.90 | （與 S-A、S-C 同時） |
| ¬S-B | H5、H10 **並非**全＞0 | **6**＝觀察空 |

S-A∧S-C∧S-D 共 8；其中 S-B 已過＝2（＝UP-PULL 進場空），其餘 6＝本軌。∩進場空＝**0**。

### 2.3 預診名單＠2026-08-18（規則通過＝已發生路徑，**不是預測**；**不是 P1 已閉**）

**觀察多 13 檔**（序＝短窗仍漲多→少；展示若 k=10 則截前 10）：

| 序 | 代號 | 名稱 | 距 20 日高 | H5 | H10 |
|---|---|---|---|---|---|
| 1 | 3017 | 奇鋐 | −6.2% | +10.0% | +16.7% |
| 2 | 2324 | 仁寶 | −6.0% | +11.8% | +9.7% |
| 3 | 2357 | 華碩 | −8.6% | +8.5% | +12.9% |
| 4 | 4163 | 鐿鈦 | −3.0% | 0.0% | +19.3% |
| 5 | 6277 | 宏正 | −4.0% | +5.0% | +8.1% |
| 6 | 2108 | 南帝 | −4.5% | −1.0% | +7.3% |
| 7 | 2362 | 藍天 | −7.6% | −0.2% | +5.6% |
| 8 | 2376 | 技嘉 | −12.4% | −0.7% | +4.8% |
| 9 | 5306 | 桂盟 | −6.2% | −6.2% | +4.1% |
| 10 | 6206 | 飛捷 | −9.2% | +0.3% | +2.5% |
| 11 | 3213 | 茂訊 | −4.7% | −2.9% | +2.3% |
| 12 | 1434 | 福懋 | −10.0% | −1.1% | +1.2% |
| 13 | 5511 | 德昌 | −6.3% | −0.8% | +0.4% |

Ridge 相對強 Top10 ∩ 本表＝**僅 3017**。仁寶、華碩、技嘉等不在 Ridge 強池，正是本軌要補的。

**觀察空 6 檔**（序＝短窗仍跌多→少；≠可空）：3152 璟德、3548 兆利、3078 僑威、1522 堤維西、2471 資通、4129 聯合。

預診用 `score_universe` 唯讀，未寫 `prediction_values`。P1 正式閉包須另句探針。

---

## §3 過篩後如何排序（凍結）

**禁止**用 RankRidge score 當本軌序位。

### 3.1 觀察多

主鍵：H5／H10 仍為正的 log 報酬加總 **降序**（還在衝愈明顯愈前）。  
次鍵：`mean(ret_60, ret_120, ret_240)` 降序。  
三鍵：`stock_id` 升序。

不做「H5 必須約 +10%」。奇鋐＠08-18 會因短窗仍漲最多而排第 1，是規則結果，不是樣板門檻。

### 3.2 觀察空

主鍵：H5／H10 仍為負的 |log| 加總降序。  
次鍵：`mean(ret_60, ret_120, ret_240)` 升序（長窗愈負愈前）。  
三鍵：`stock_id` 升序。

### 3.3 展示 k

JSON：**全列**。stdout：前 k 名（預設 10）。`n_watch_long=13` 時展示 10、JSON 仍 13。禁止為湊畫面去改閘。

---

## §4 探針（P1；另句才算閉）

```text
PYTHONPATH=src python scripts/probe_watch_pullback.py --date 2026-08-18 --k 10
# JSON /tmp/watch-pb-2026-08-18.json
# --date 2026-08-19 → rc=3
```

- 每檔列出距 20 日高／低、H5／H10 已發生路徑％、閘位元、觀察標。  
- 路徑％＝截至 D 的過去，**零**筆 D 之後的實現報酬。  
- 自測：`python scripts/probe_watch_pullback.py --selftest`

### Phase 2｜OOS（延後）

與 UP-PULL P2 同尺：過篩集合 vs 宇宙其餘的後續相對名次；IC ≠ 確立 ≠ 報酬％。  
GO：`WATCH-PB-oos-walk-go | origin=2026-07-31 | no-promote`  
**不**與進場閘比「誰比較賺」直到這句跑完。

### 本檔不開

解凍 NF；sim `--apply`；改 standing；evaluate／approve `dgate_*`；E5；把觀察標成「可當進場條件」；用單檔％套樣；從 Ridge Top10 當唯一池。

---

## §5 工作包（開跑複製）

### WP-P0｜採納定義 ✅

```text
WHEN: Steward 貼 WATCH-PB-plan-adopt
DO:   本檔 status → adopted；寫 audits/WATCH-PB-PLAN-ADOPTED-20260819.md
DONT: 把 §2.3 預診當可交易名單；不自動開 P1
DONE: 2026-08-19 ADOPTED；θ 未改；UP-PULL-v1 未改
```

### WP-P1｜探針＠最近日 ✅

```text
WHEN: 價頂 D 已 ready 且非 B3 開火；Steward 貼 WATCH-PB-probe-go
DO:   scripts/probe_watch_pullback.py --date <D> --k 10
DONT: 寫 prediction_values；假 B3；用 Ridge score 排序；標可當進場條件
DONE: 2026-08-19 EXECUTED＠08-18；n_watch_long=13 n_watch_short=6；∩進場＝0
```

### WP-P2｜OOS walk

```text
WHEN: P1 殼綠；Steward 貼 WATCH-PB-oos-walk-go
DO:   對已實現窗的歷史 D 重跑觀察閘＋未來相對名次
DONT: 同日 stamp；不足樣本卻報勝；宣稱優於進場閘
DONE: audit；IC／名次差標 ≠確立
```

---

## §6 與 r18 執行板

| 本計畫 | 可先？ | 可同步？ | 備註 |
|---|---|---|---|
| P0 採納 | **已閉** | — | 觀察≠進場；不放寬 L-B |
| P1 探針＠08-18 | **已閉** | — | 觀察多 13／空 6；展示 10／6；∩進場＝0 |
| P2 OOS | 探針後 | 讓 B3／長訓 | 與 UP-PULL P2 同尺、不同集合 |
| emit／standing | **否** | **否** | 不改 20,60 |

建議 paste（採納本檔、仍不開工探針）：

```text
WATCH-PB-plan-adopt | no-promote | standing=20,60 | no-fake-B3@08-19
| 觀察≠進場 | 做空≠可空 | 路徑％≠未來％ | 不放寬 L-B
```

探針開工另貼：

```text
WATCH-PB-probe-go | date=2026-08-18 | k=10 | dry-run | 觀察≠進場
```

---

## §7 驗收（本計畫書）

- [x] 觀察多／觀察空寫成可機算硬閘（A∧C∧D∧¬B，鏡像）  
- [x] 與 UP-PULL 進場集合不相交寫死  
- [x] 不用 Ridge Top10 當池、不用 score 排序寫死  
- [x] 不用單檔 H5／H10 ％套樣寫死  
- [x] 標籤禁止「可當進場條件」寫死  
- [x] 排序鍵寫死；JSON 全列／展示截 k 寫死  
- [x] 08-18 預診入檔（多 13／空 6；奇鋐觀察多第 1）  
- [x] 探針腳本路徑寫死（P1 另句才閉）  
- [x] P0 採納 audit  
- [x] P1 EXECUTED audit  

*完。[I] · adopted · P1 探針＠08-18 已閉（13／6）；P2 另句。*
