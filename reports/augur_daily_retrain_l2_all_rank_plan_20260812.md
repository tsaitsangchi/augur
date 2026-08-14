---
title: DAILY-RETRAIN-L2-ALL-RANK｜每日窄重訓計畫書（邊界＝A）
status: plan_p1_shell_done
viewpoint: 2026-08-12T14:25+08:00
shell: scripts/run_daily_retrain_l2_all_rank.sh
shell_go: audits/DAILY-RETRAIN-L2-SHELL-GO-20260812.md
shell_executed: audits/DAILY-RETRAIN-L2-SHELL-EXECUTED-20260812.md
layer: "[I]"
series: s4_retrain
track: DAILY-RETRAIN-L2-ALL-RANK
role: 日更 L2＝ALL-RANK 包每日 as-of 重訓之執行契約（plan-first；**未授 cron**）
boundary: A
boundary_means: RankRidge×五 H＋既有 challenger×8（鏡 0810／0811 包 C）；非 NF／非 Daily*／非 taxonomy 全族
parent_ssot: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md
market_knife: reports/augur_opt_stepwise_best_next_plan_r14_20260811.md
l1_shell: scripts/run_daily_asof_predict.sh
l1_plan: reports/augur_daily_asof_b3_orchestrator_plan_20260805.md
s4_s5_loop: reports/augur_s4_s5_closed_loop_plan_20260804.md
mirror_executed:
  - audits/RETRAIN-ASOF-0810-ALL-RANK-EXECUTED-20260811.md
  - audits/RETRAIN-ASOF-0811-ALL-RANK-EXECUTED-20260812.md
register: audits/DAILY-RETRAIN-L2-ALL-RANK-PLAN-REGISTER-20260812.md
self_reported: true
---

# DAILY-RETRAIN-L2-ALL-RANK｜每日窄重訓計畫書（邊界＝A · 2026-08-12）

> **一句**：在 **L1＝B3 tip 日更成功**之後，對 **邊界 A＝ALL-RANK 包**做 as-of＝`D` 的重訓＋H20/60 repredict／emit；預設 **no-promote**、**不裝 cron**。  
> **性質**：[I] plan-first。**本檔≠GO 寫庫／≠安裝 timer**；解鎖分階段見 §6。  
> **閉環位階**：S4（多模型重覆驗·窄）→ S5（漲跌比／#14 誠實披露）；對齊 C2，**不做**自動升格。

---

## §0 邊界＝A（釘死）

| 在邊界內（每日可規畫） | 在邊界外（本計畫永不默納） |
|---|---|
| RankRidge × **H=20,40,60,82,120** | NF 族（TimesFM／Chronos／Moirai／GARCH…）· **NF-pause** |
| Challenger：**RankGBDT** 20/60；**RankXGB／Cat／RF／KNN／MLP** 60；**RankSVM** 20 | Daily* 方向臂（DailyLogit／DailyGBDT…） |
| seed＝**42**（與 0810／0811 鏡像） | Wave B–G 無 adapter／已 STOP 族之「同尺重掃變綠」 |
| repredict＋emit **H20,H60**（新 Ridge） | 默 **SERVE-SWAP**／registry 升格／sim `--apply` |
| 成功尺：registry `asof_snapshot=D` **≥13** 列＋artifact | taxonomy「所有模型」字面擴大（那是邊界 B／C，另 plan） |

**「所有模型」在本檔＝A 包**，與 Steward 既授 `RETRAIN-ASOF-081x-ALL-RANK` 同義；**≠** S4 Wave A–G 全表。

```text
paste（邊界）:
  DAILY-RETRAIN-L2 | boundary=A | Ridge×5H + chal×8
  | seed=42 | repredict=20,60 | no-promote | NF-pause | no-Daily*
```

---

## §1 為何需要 L2（與 L1 分工）

| 層 | 腳本／契約 | 做什麼 | 不做什麼 |
|---|---|---|---|
| **L0** | cron `run_arena_daily_pipeline` **20:00** 一～五（①＝`run_l0_hotpath_daily.sh` 核 A＋TRI＋FRED） | FinMind 核 A／TRI／FRED（API 門；**非** 93 表） | tip／重訓 |
| **L1** | `run_daily_asof_predict.sh`（B3） | feat／core／**既有 serve** predict＋emit＠`D` | 重訓；sync；cron |
| **L2** | **本計畫**（薄殼待 P1） | as-of＝`D` **重訓 A 包**→再 predict／emit H20/60 | promote；NF；無價假跑 |

L1 可在舊 `model_id` 上先出 tip；L2 把 **冠軍族＋challenger** 推到同一 `D`，避免「價新、模舊」長期漂移。  
0810 實證：B3 首槍曾掛 0731，**須 L2 repredict** 才把 H20/60 掛上當日 Ridge。

---

## §2 觸發與時刻（人／半自動；非默認 cron）

### 2.1 觸發條件（AND）

1. `TaiwanStockPriceAdj`（TAIEX）`max(date) ≥ D`  
2. L1 B3＠`D` **RC=0**（fv／core／predict／emit／2330@H20 accept）  
3. 顯式 GO 或 **standing 日更臂**已含「L1 成功後接 L2」（見 §6 P3；**P0 本檔未授自動接）  
4. `flock` 取得 `/tmp/augur_llm.lock`（或約定重訓專鎖，避免與 TWEVO／arena 重 LLM 互撞）

**失敗／跳過**：價 `<D` → **整鏈 SKIP**（對齊 B3；不假跑）。L1 失敗 → **不開 L2**。

### 2.2 建議時刻窗（Asia/Taipei）

| 窗 | 用途 | 備註 |
|---|---|---|
| 20:00 | L0 sync（已排；核 A＋TRI） | 本計畫不改 |
| 21:40／09:20 | RETRAIN-ALL 全包重訓（另軸 cron；**不含**本殼 emit） | `RETRAIN-ALL-ASOF-DAILY-CRON-ADOPTED`；本計畫仍**不**裝 L2 emit cron |
| 價到～21:30 | L1 B3（watcher／人） | 截止常 **23:50** TIMEOUT |
| L1 OK 後～次日 02:00 | **L2 ALL-RANK** | 錯開 TWEVO **23:00**；必要時 L2 延到 00:30+ |
| 休市 | 不跑 | 無新 `D` |

### 2.3 與硬門對齊

```text
FZ/GATE-keep | hold-#1 | skip-sync-B（L2 不 sync）
| no-fake-B3 | no-cron-B3（L2 默認同禁；timer＝另授）
| no-SIM-apply | no-promote | NF-pause | 勿重掃假綠 | 誠實 #14
```

---

## §3 標準日步驟（as-of＝`D`）

> 指令要旨＝鏡 `RETRAIN-ASOF-0811`；實作薄殼時只編排、不新造估計量邏輯。

| # | 步 | 指令要旨 | 失敗 |
|---|---|---|---|
| 0 | 閘 | 唯讀：PriceAdj／fv／core／既有 tip；確認 L1＠`D` OK | 價或 L1 不足 → SKIP |
| 1 | Ridge×5 | `train_ranker.py --run --family RankRidge --horizon {20,40,60,82,120} --asof D --seed 42` | 任 H RC≠0 → 停；不半套 promote |
| 2 | Challenger×8 | 同 CLI：`RankGBDT`@20,60；`RankXGB`/`RankCat`/`RankRF`/`RankKNN`/`RankMLP`@60；`RankSVM`@20 | 單臂失敗 → 記帳＋可續跑其餘（**預設 fail-soft 挑戰／fail-hard Ridge**；薄殼旗標可選） |
| 3 | repredict | `predict_asof.py --run --family RankRidge --horizon {20,60} --asof D`（吃新 asof 列） | 停 |
| 4 | emit | `calibrate_relative_probability.py --emit --horizon {20,60} --asof D` | 停；撞 PK 時沿用「只取 max asof_snapshot」修法 |
| 5 | #14 披露 | 讀 econ／dgate 狀態；**dead／thin 照實**入 audit | 禁塗綠 |
| 6 | 帳 | `audits/DAILY-RETRAIN-L2-YYYYMMDD-EXECUTED.md`＋`/tmp/daily-retrain-l2-D/` log | 缺帳＝未完成 |

**預期產物命名**（與現況一致）：

```text
{Family}_H{h}_{D}_seed42_{feats_hash}
例：RankRidge_H60_2026-08-11_seed42_56d03625463b3eba
```

`feats_hash` 隨 prodset；若與前日相同＝特徵契約未變（誠實註記即可）。

---

## §4 驗收尺

| 尺 | 通過條件 |
|---|---|
| **R1 registry** | `model_registry` 中 `asof_snapshot=D` 且屬 A 包家族 **≥13** |
| **R2 artifact** | 對應 `.joblib`（或既有 artifact 根）存在 |
| **R3 tip 掛新** | H20／H60 `prediction_values` 所用 RankRidge 之 asof＝`D`（非殘留舊日） |
| **R4 誠實 econ** | emit／#14 有數字或明示 dead／thin；**不**要求 evaluated_pass |
| **R5 護欄** | audit 含 `no-promote`；無 SERVE-SWAP；無 NF／Daily* 列 |

**非驗收**：IC 變好、自動換冠、dgate 變綠、sim 校準綠。

---

## §5 CLI／產物草案（P1 解鎖後）

```text
# 計畫產物（尚未實作；本檔不授碼）
scripts/run_daily_retrain_l2_all_rank.sh
  --date YYYY-MM-DD
  [--dry-plan]
  [--skip-challenger]          # 成本降級：只 Ridge×5 + repredict
  [--fail-hard-challenger]     # 挑戰失敗也整鏈停（預設 fail-soft）
  [--skip-repredict]           # 僅訓不掛 tip（研究窗；日更勿用）
  [--selftest]
```

硬碼語意：

- **永不**呼叫 FinMind／FRED sync  
- **永不**寫入 cron／systemd（安裝＝§6 P4 另 GO）  
- 預設 **no-promote**

日誌根：`/tmp/daily-retrain-l2-$D/`（`ridge.log`／`challenger.log`／`repredict.log`／`driver.log`）。

---

## §6 分階段授權

| 階段 | 產出 | 授權句（示意） | 狀態 |
|---|---|---|---|
| **P0** | **本計畫書**＋register audit | Steward 委託起草＝本檔 | ✅ |
| **P1** | 薄殼 script＋`--dry-plan` selfsmoke | `DAILY-RETRAIN-L2-SHELL-go` | ✅ `scripts/run_daily_retrain_l2_all_rank.sh` |
| **P2** | 真跑一日（建議 `D`＝已有價且 L1 已綠之日，如 08-11 複跑或新 D）＋EXECUTED | 同 GO 或 `…-APPLY-go` | 🔴 |
| **P3** | 納入日更 standing：L1 成功→可選接 L2（仍人／watcher，**非 cron**） | `DAILY-RETRAIN-L2-STANDING-go` | 🔴 |
| **P4** | timer／cron | **雙明示另授**；本 plan **永不默授** | ❄ 禁默 |

```text
paste（開殼）:
  DAILY-RETRAIN-L2-SHELL-go | boundary=A | FZ/GATE-keep
  | no-promote | NF-pause | no-SIM-apply | no-cron | skip-sync
```

---

## §7 成本與降級

| 模式 | 內容 | 何時用 |
|---|---|---|
| **Full A** | Ridge×5＋chal×8＋repredict 20/60 | 預設交易日 |
| **Ridge-only** | `--skip-challenger` | lock 爭用／超時／GPU 忙 |
| **SKIP** | 整鏈不做 | 無價；L1 失敗；TIMEOUT |

經驗錨（self-reported）：0811 全日 ALL-RANK 可在數十分鐘量級完成（視負載）；薄殼應設 **wall-clock 上限**（建議 90–120 min），超限改 Ridge-only 並告警。

---

## §8 與選刀板／閉環的關係

| 文件 | 關係 |
|---|---|
| r14 `#1` B3 | **前置**；L2 不取代 L1 |
| r14 `#18` 其他模型 | L2＝A 包日更；**不是**解禁 NF／重掃 STOP |
| r14 `#20` 升格 | L2 產 artifact **≠** promote；升格另 `PROMOTE-TRACK` |
| S1→S5 SSOT | L2＝S4 窄日更弧；S5＝repredict＋#14 |
| KH 選刀 | **正交**；不候／不擋 |

---

## §9 硬禁（再列一次）

1. 無 `PriceAdj≥D` 假訓／假 tip  
2. 默裝 cron／systemd timer（無 P4）  
3. 默 promote／SERVE-SWAP／改五窗 standing 殼  
4. 納入 NF／Daily*／已 STOP 族同尺「刷綠」  
5. L2 內 sync FinMind／FRED  
6. sim `--apply`  
7. 把 L2 成功當成 dgate `evaluated_pass`

---

## §10 工作包卡片（開跑複製）

### WP-L2｜單日 ALL-RANK（人跑／P2）

```text
WHEN: L1 B3@D RC=0 AND PriceAdj≥D
DO:   Ridge×5 + chal×8 @asof=D seed=42
      → predict+emit H20,60 → #14 披露 → EXECUTED audit
DONT: promote; NF; Daily*; cron; sync; fake-D
DONE: registry asof=D ≥13 + tip Ridge asof=D + no-promote 帳
```

### WP-SHELL｜P1 薄殼

```text
WHEN: DAILY-RETRAIN-L2-SHELL-go
DO:   實作 run_daily_retrain_l2_all_rank.sh + --dry-plan selfsmoke
DONT: 真訓寫庫（除非同 GO 含 APPLY）; install_cron
DONE: --dry-plan 印滿 §3 步；--selftest 旗標／路徑綠
```

---

## §11 修訂

| 日 | 變更 |
|---|---|
| 2026-08-12 | P0 初稿：邊界 A；L1→L2；鏡 0810／0811；分階 P0–P4 |
| 2026-08-12 | P1：薄殼 `run_daily_retrain_l2_all_rank.sh`；selftest／dry-plan 綠；真訓須 `--apply` |

*plan_draft → 待 Steward ack／SHELL-go。*
