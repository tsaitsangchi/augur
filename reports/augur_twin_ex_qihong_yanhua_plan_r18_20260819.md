---
title: 奇鋐／研華進出最佳化（不要抱牢）計畫書 r18
status: adopted
series: s4_s5_verify
round: r18
role: 對 3017／2395 在「不要抱牢」目標下搜尋進場×出場；禁止用全樣本或大多頭窗的最長持有當最佳（P0＋P1＠08-18 已閉）
date: 2026-08-19
viewpoint: 2026-08-19T11:26+08:00
layer: "[I]"
product_id: TWIN-EX-v1
adopted: audits/TWIN-EX-PLAN-ADOPTED-20260819.md
parent_ssot: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_r16_20260813.md
exec_nav: reports/augur_opt_stepwise_all_problems_r19_20260819.md
rs_charge: reports/augur_rs_charge_qihong_yanhua_plan_r18_20260819.md
watch_pb: reports/augur_watch_pullback_inband_plan_r18_20260819.md
bull5: reports/augur_bull5_hstack_pullback_plan_r18_20260819.md
econ_path: reports/augur_econ_prove_edge_plan_r17_20260817.md
self_reported: true
---

# 奇鋐／研華進出最佳化（不要抱牢）（2026-08-19）

> **一句**：目標不是打敗「一直抱著」，而是在**進出規則之間**找對這兩檔較穩的一組。已見：20 日轉折進出遠輸抱牢（奇鋐複利 +137% vs 抱牢 +840%）。若用 2025–26 大多頭去比「誰複利最高」，贏家一定偏向**持有愈長**，等於把抱牢從後門加回來。  
> **本檔＝已採納計畫**（`audits/TWIN-EX-PLAN-ADOPTED-20260819.md`）。P1 格子＠08-18 **已閉**（`audits/TWIN-EX-GRID-0818-EXECUTED-20260819.md`）：工作假說 E-charge×T5 在此兩檔尺下仍是冠軍。採納／格子 ≠ 可交易、≠ 改 standing、≠ 全宇宙。抱牢只當對照。08-19＝假 B3。

---

## §0 護欄

```text
TWIN-EX-v1 | no-fake-B3@08-19 | no-promote | no-SIM-apply | NF-pause
| standing=20,60 不改 | 路徑％ ≠ 未來％ | 兩檔 ≠ 宇宙
| 進出 ≠ 可交易 | 未扣成本先標明 | 全樣本最大複利 ≠ 最佳
| 不把 T20／T40 在大多頭窗的勝出當成「不要抱牢的解」
```

| 可 | 不可 |
|---|---|
| 凍結搜尋空間＋IS／OOS 切法 | 用 16＋9 筆全樣本冠軍當 v1 出場 |
| 以「短持有、IS 與 OOS 同號」當不要抱牢的尺 | 只報 OOS 複利最高（2025–26 趨勢會選長持有） |
| 成本敏感性另欄 | 無 GO 當 live 下單、改 standing |

---

## §1 問題定義

只對 **3017 奇鋐、2395 研華**。價＝還原收盤。進場＝訊號日 **t+1**。出場前同檔不加倉。

**要最佳化的**：進場閘 × 出場規則 → 交易序列的複利（簡單報酬連乘）。

**不要最佳化的**：抱牢報酬（已算過，當對照、不當目標）。Ridge 每日 Top10（歷史分數不足，進場不靠它）。

**「最佳」凍結定義（不要抱牢）**：

1. 先丟持有 40 日的候選（太近抱牢）。  
2. 訓練窗與保留窗**複利同號**（都＞0 或都＜0；＜0 整組淘汰）。  
3. 保留窗交易數 **n≥8**（兩檔合計）。  
4. 在合格組裡，主鍵＝訓練窗複利；次鍵＝保留窗複利；三鍵＝持有日數**升序**（同樣報酬取更短）。  
5. 不得只用保留窗最大複利定冠。

切窗（凍結）：

| 窗 | 訊號日 | 用途 |
|---|---|---|
| IS | 2024-01-02～2024-12-31 | 選規則 |
| OOS | 2025-01-02～2026-06-30 | 只驗證；出場須在價頂 **2026-08-18** 前結束 |
| 價頂當日 | 2026-08-18 | 可有訊號，**無**未來報酬 |

L-D 用近 **252 交易日**還原高低現算（庫內 `feature_values` 不是每日）。

---

## §2 搜尋空間（凍結；加點＝新 ID）

### 2.1 進場（條件由否→是才開一筆）

| ID | 規則 | 來源 |
|---|---|---|
| E-charge | L-A ∧ L-D ∧ H5＞0 ∧ H10＞0 | RS-CHARGE 路徑交集（無 Ridge 池） |
| E-h5dip | H10…H240 全＞0 ∧ H5＜0 ∧ L-D | BULL5 |
| E-watch | L-A ∧ L-C ∧ L-D ∧ ¬L-B | WATCH-PB（研華少過 L-C） |

### 2.2 出場（先到先出；皆 t+1 成交）

| ID | 規則 |
|---|---|
| X-T5／T10／T20 | 進場後第 5／10／20 交易日收盤出 |
| X-H5cap20 | 進場後首次 H5＜0 之次日，最長 20 日 |
| X-LAcap20 | 進場後首次 L-A 失敗之次日，最長 20 日 |

**X-T40 可算進表當對照，不當「不要抱牢」冠軍。**

停損％、停利％本版不開（兩檔樣本會把 θ 套死）。要開＝TWIN-EX-v1b 另句。

---

## §3 預診格子（方法展示，**不是**已採納冠軍）

兩檔合計、未扣成本、轉折進場。IS＝2024；OOS＝2025-01-02～2026-06-30。

| 進場 | 出場 | IS n／複利％ | OOS n／複利％ | 不要抱牢尺 |
|---|---|---|---|---|
| E-charge | T5 | 15／+57 | 24／+73 | 同號、持有短 |
| E-charge | T10 | 14／**−9** | 20／+86 | IS 負 → 淘汰 |
| E-charge | T20 | 10／+1 | 14／+310 | OOS 像趨勢抱；不當冠 |
| E-charge | H5cap20 | 16／+27 | 25／+112 | 可留 |
| E-h5dip | T5 | 11／+17 | 18／+39 | 可留 |
| E-h5dip | T10 | 10／+31 | 13／+19 | 可留（OOS 較溫） |
| E-watch | T5 | 12／+14 | 32／+31 | 可留 |
| E-watch | T20 | 6／+5 | 16／+341 | OOS 最高但是長持有＋這波多頭；**禁當冠** |

若硬套 §1 尺（丟 T40、OOS 不當主鍵、要 IS＞0）：工作假說 **E-charge × T5**（訓練複利最高的短持有合格組）。  
這句**尚未**寫成 v1 出場；P1 須重跑＋成本欄＋分檔揭露。奇鋐／研華不得平均成一條就假裝兩檔一樣。

---

## §4 工作假說（P1 要證實或推翻）

**TWIN-EX-v1 候選**：進＝E-charge 轉折；出＝X-T5。  
人話：長線仍多、5／10 日還在漲的**第一天**進，**五個交易日**就出。不靠回撤帶、不等 5 日先跌、不拿到 20 日。

對照（必須同表）：E-h5dip×T10、E-watch×T5、E-charge×T20（後者標「偏抱牢」）。

---

## §5 與已有軌

不改 RS-CHARGE／WATCH／BULL5／UP-PULL θ。本檔只多「出場＋切窗選規則」。不接 live 顧問。不寫 `prediction_values`。

---

## §6 工作包

### WP-P0｜採納定義 ✅

```text
WHEN: Steward 貼 TWIN-EX-plan-adopt
DO:   本檔 status → adopted；寫 audits/TWIN-EX-PLAN-ADOPTED-20260819.md
DONT: 把 §3 格子當已最佳；不自動開 P1；不把抱牢寫成本軌操作
DONE: 2026-08-19 ADOPTED；尺與搜尋空間凍結；θ 未把 T20 寫死
```

### WP-P1｜格子＠切窗 ✅

```text
WHEN: Steward 貼 TWIN-EX-grid-go
DO:   重跑 §2 全格；分檔＋合計；無成本／成本地板兩欄；印合格組與假說是否仍是 charge×T5
DONT: 全樣本重選冠軍；假 B3；寫庫
DONE: 2026-08-19 EXECUTED＠tip 08-18；假說 charge×T5 仍冠（僅兩檔）；JSON audits/TWIN-EX-GRID-0818.json
```

### WP-P2｜宇宙外推（＝CHARGE-T5 P1）✅

把勝出規則拿到核心宇宙（不是這兩檔）做相對名次。兩檔最佳 **不必** 宇宙最佳。  
已由 `CHARGE-T5-universe-go`＠08-18 閉（`audits/CHARGE-T5-UNIVERSE-0818-EXECUTED-20260819.md`）：等權 k=10 成本後 IS 負；T20／T40 不當冠。≠可交易。

---

## §7 與 r18

採納：

```text
TWIN-EX-plan-adopt | no-promote | standing=20,60 | no-fake-B3@08-19
| 不要抱牢 | IS=2024 OOS=2025-01..2026-06 | 禁OOS最長持有當冠 | 兩檔≠宇宙 | 條件≠可交易
```

格子開工：

```text
TWIN-EX-grid-go | sids=3017,2395 | dry-run | 不要抱牢
```

---

## §8 驗收

- [x] 目標寫成「進出規則之間的最佳」，明確排除抱牢  
- [x] 禁 OOS 長持有複利當冠  
- [x] 搜尋空間與切窗凍結  
- [x] 預診格子入檔；工作假說 charge×T5 **未**升格為已證實  
- [x] P0 採納  
- [x] P1 格子閉（charge×T5 仍冠；僅兩檔；≠可交易）  
- [x] 宇宙外推＝CHARGE-T5 P1＠08-18 已閉（成本後 IS 負；≠可交易）  

*完。[I] · adopted · P1 EXECUTED＠08-18；CHARGE-T5 宇宙已閉；≠可交易。*
