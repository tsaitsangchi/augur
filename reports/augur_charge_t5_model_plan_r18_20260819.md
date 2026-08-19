---
title: 衝勢 5 日進出——新交易模型計畫書 r18
status: adopted
series: s4_s5_verify
round: r18
role: 把奇鋐／研華交集走出的 E-charge×T5 收成可命名、可宇宙驗證的新規則模型；兩檔研究 ≠ 已有交易模型
date: 2026-08-19
viewpoint: 2026-08-19T13:36+08:00
layer: "[I]"
product_id: CHARGE-T5-v1
adopted: audits/CHARGE-T5-PLAN-ADOPTED-20260819.md
executed_p1: audits/CHARGE-T5-UNIVERSE-0818-EXECUTED-20260819.md
parent_twin: reports/augur_twin_ex_qihong_yanhua_plan_r18_20260819.md
two_name_ops: reports/augur_qihong_yanhua_conditions_ops_plan_r18_20260819.md
ops_handbook: reports/augur_path_timing_opt_ops_plan_r18_20260819.md
exec_nav: reports/augur_opt_stepwise_all_problems_r19_20260819.md
econ_path: reports/augur_econ_prove_edge_plan_r17_20260817.md
self_reported: true
---

# 衝勢 5 日進出——新交易模型（2026-08-19）

> **一句**：可以自創，但必須是**新 ID**，不能把「奇鋐／研華 39 筆賺到的％」當成全市場模型已證明。新模型 **CHARGE-T5-v1**＝長窗仍多、結構未破、近 5／10 日還在漲的第一天進，五個交易日出。先規則、後宇宙驗證；不取代 RankRidge standing。  
> **本檔＝已採納計畫**（`audits/CHARGE-T5-PLAN-ADOPTED-20260819.md`）。P1 宇宙＠08-18 **已閉**（`audits/CHARGE-T5-UNIVERSE-0818-EXECUTED-20260819.md`）：無成本兩窗正，成本後訓練窗為負；T20／T40 不當冠。採納／宇宙 ≠ 可交易、≠ 改 standing、≠ #14。兩檔 39 筆％不是本模型績效。08-19＝假 B3。

---

## §0 護欄

```text
CHARGE-T5-v1 | no-fake-B3@08-19 | no-promote | no-SIM-apply | NF-pause
| standing=20,60 不改 | 兩檔研究 ≠ 宇宙模型 | 條件 ≠ 可交易
| 禁OOS最長持有當冠 | 不套樣奇鋐／研華％ | 路徑％ ≠ 未來％
| 不倒 canonical 31 | 不寫 prediction_values | 改 θ＝新 ID
```

| 可 | 不可 |
|---|---|
| 把 TWIN-EX 冠軍規則命名成新模型 | 沿用 TWIN-EX-v1 卻宣稱已是全市場策略 |
| 核心宇宙 IS／OOS 重跑同一尺 | 把兩檔複利當預期報酬 |
| 同日多檔用排序＋上限 k | 假設資金可同時全押每一筆轉折 |
| 成本地板另欄 | 無宇宙驗證就接顧問／改 standing |

---

## §1 為什麼算「新模型」、為什麼現在還不是

**已經有的**：TWIN-EX 在 **兩檔**上選出 E-charge×T5；條件計畫書列出了 39 筆報酬。那是**研究結論**，產品 ID 仍是 TWIN-EX-v1。

**還缺的（沒有這些就不叫交易模型）**

1. **宇宙**：同一規則在核心宇宙是否仍兩窗同號、是否仍短持有勝出。兩檔最佳不必宇宙最佳。  
2. **同日撞車**：真模型一天可能出現很多檔轉折；兩檔回測是「每檔 100% 資金連乘」，不能直接當組合。  
3. **倖存者**：先因為現在看起來強才選奇鋐／研華，再回測會偏樂觀。  
4. **Ridge 池**：RS-CHARGE 要每天 Top10；歷史分數幾乎沒有。新模型 v1 **不**靠 Ridge。  
5. **#14**：路徑複利 ≠ 確立能賺錢。

所以：**可以自創**＝新 ID＋凍結規則＋宇宙驗證。  
**不可以**：把兩檔進出表直接當成已上線的新模型。

---

## §2 模型定義（已凍結）

記名 **CHARGE-T5-v1**。規則模型，不是 RankRidge 的新 family，也不在本版訓練權重。

| 件 | 內容 |
|---|---|
| 宇宙 | 該日 `core_universe_asof`（無則跳過該日） |
| 訊號 | L-A ∧ L-D ∧ H5＞0 ∧ H10＞0（L-D 現算近 252 交易日還原高低） |
| 開倉 | 該檔條件由否→是；出場前不加倉 |
| 進場 | 訊號日 t+1 還原收盤 |
| 出場 | 進場後第 5 交易日收盤 |
| 同日多名 | 當日新訊號依 `mean(H60,H120,H240)` 降序取 **k=10**，不足不補 |
| 組合尺 | 宇宙驗證用「當日入選等權、檔內仍 T5」；另報「逐檔連乘」對照（與兩檔研究同口徑） |
| 切窗 | 與 TWIN-EX 同：IS＝2024，OOS＝2025-01～2026-06，出場 ≤ 2026-08-18 |
| 不要抱牢尺 | 同 TWIN-EX：T40 不當冠；主鍵 IS 複利；禁只看 OOS 最長持有 |
| 不做 | L-C、L-B、Ridge 分數、停損％、把奇鋐 H5≈+10% 寫死 |

空方鏡像（長窗全負 ∧ H5＞0 ∧ H10＞0，5 日出）＝**CHARGE-T5-SHORT-v1**，另句才開；本檔 P0 只做多。

若要改成可學習的打分器（在閘內再排），新 ID **CHARGE-T5-FIT-v1**，且不得倒 31 欄、不得 SERVE-SWAP。

---

## §3 與已有軌

| ID | 關係 |
|---|---|
| TWIN-EX-v1 | 兩檔選規則的實驗室；本模型＝把它的冠軍拿到宇宙 |
| RS-CHARGE-v1 | 觀察篩＋Ridge 池；本模型**無** Ridge、**有**出場 |
| UP-PULL-v1 | 進場要短窗雙負＋回撤帶；本模型是短窗仍衝就進、5 日出 |
| WATCH-PB／BULL5 | 觀察／5 日回跌；不是本模型 |
| RankRidge standing | 日常出門仍 H20+H60；本模型並列、不覆蓋 |

TWIN-EX 的 `TWIN-EX-universe-go` 與本檔 P1 **同一槍**。P0 已採納，宇宙驗證用 `CHARGE-T5-universe-go`。

---

## §4 工作包

### WP-P0｜採納模型定義 ✅

```text
WHEN: Steward 貼 CHARGE-T5-plan-adopt
DO:   本檔 status → adopted；寫 audits/CHARGE-T5-PLAN-ADOPTED-20260819.md
DONT: 自動開宇宙走步；不改 standing；不把 39 筆當產品績效
DONE: 2026-08-19 ADOPTED；ID 與閘／T5／k=10／切窗凍結
```

### WP-P1｜核心宇宙 IS／OOS（這槍才配叫模型驗證） ✅

```text
WHEN: Steward 貼 CHARGE-T5-universe-go
DO:   核心宇宙重跑 E-charge×T5；等權 k=10；無成本／成本地板；IS／OOS；對照兩檔舊帳
DONT: 假 B3；寫庫；OOS 長持有當冠；宣稱 #14
DONE: 2026-08-19 EXECUTED＠tip 08-18；JSON audits/CHARGE-T5-UNIVERSE-0818.json；無成本兩窗正、成本後 IS 負；T20／T40 不當冠；≠可交易
```

### WP-P2｜單日探針＠價頂

```text
WHEN: P1 殼綠或 Steward 先要看今天誰觸發；貼 CHARGE-T5-probe-go | date=2026-08-18
DO:   列出當日轉折名單（上限 k）；標 ≠可交易
DONT: 接 live 顧問
DONE: n、名單、與 UP-PULL／WATCH 交集
```

### WP-P3｜產出／訓練（延後）

emit 須 `CHARGE-T5-emit-go | standing-unchanged | dry-run 先`。  
FIT 須另 ID。皆不在 P0 自動開。

---

## §5 與 r18

| 本計畫 | 可先？ | 備註 |
|---|---|---|
| P0 採納 | **已閉** | 2026-08-19 ADOPTED |
| P1 宇宙 | **已閉** | 成本後 IS 負；≠可交易 |
| P2 單日探針 | 可與 P1 分槍 | 08-19 假 B3 |
| emit／standing | **否** | |

採納（仍不開宇宙）：

```text
CHARGE-T5-plan-adopt | no-promote | standing=20,60 | no-fake-B3@08-19
| 規則＝E-charge×T5 | 宇宙≠兩檔 | k=10 | 條件≠可交易 | 禁OOS最長持有當冠
```

宇宙驗證另貼：

```text
CHARGE-T5-universe-go | dry-run | IS=2024 OOS=2025-01..2026-06 | 不要抱牢
```

---

## §6 驗收（本計畫書）

- [x] 回答「可以自創」但必須新 ID、必須宇宙驗證  
- [x] 規則寫死；同日 k=10 等權寫死  
- [x] 與 TWIN-EX／RS-CHARGE／UP-PULL／standing 邊界寫死  
- [x] 禁止把兩檔％當模型績效  
- [x] P0 採納  
- [x] P1 宇宙閉  

*完。[I] · adopted · P1 EXECUTED＠08-18；成本後 IS 負；兩檔％未升格；≠可交易。*
