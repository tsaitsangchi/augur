---
title: r16 閉環 × r18 LIVE——各段最佳下一步／可先／可同步＋歷史 as-of 答覆
status: final
series: s1s5_loop
round: r18
date: 2026-08-17
viewpoint: 2026-08-17T16:15+08:00
layer: "[I]"
role: 把 r16 運轉 SSOT 對到 r18 視點；答「過去 as-of 能否收特徵／訓／驗」；V0 已刷新
parent_ssot: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_r16_20260813.md
exec_nav: reports/augur_opt_stepwise_all_problems_r18_20260817.md
other_verify: reports/augur_s4_other_model_verify_matrix_plan_20260806.md
code:
  - scripts/run_asof_collect_train_verify.sh
  - src/augur/core/asof_ready.py
  - scripts/check_asof_ready.py
  - scripts/build_core_universe.py
self_reported: true
---

# r16 閉環問題板（對齊 2026-08-17 16:15 LIVE）

> **一句**：閉環怎麼轉仍＝r16；開工順序＝r18。**可以**用過去 as-of 收特徵、訓練、驗証——這是正門，不是假今天。  
> **LIVE 16:15**：HIST-ASOF＠07-31 已跑（截面 64）；方向臂活鎖已拉回 08-14。歷史 D 的 `--track all` **不再**覆寫 Daily*。

## §1 過去 as-of：可以，而且是唯一合法做法

| 可以 | 不可以 |
|---|---|
| D ≤ PriceAdj TAIEX 價頂，且只用當時可見資料 | 08-15／16／17 當 as-of（價頂仍 **08-14**） |
| 截面族**共用** `feature_values`＠D（不必每族重抓 API） | 拿 D+1 價回填 D 的特徵 |
| `check_asof_ready.py --date D` → ready 才 collect／訓 | 無價卻 `train_* --asof D` |
| 多 D walk-forward 當重覆驗（#11） | 同尺重掃 0812 NF 六族變綠 |
| `--track A`＝L2 邊界 A；`--track all`＝各生產模型（不 emit 今日 B3） | promote／sim-apply／把 Daily* 塞進日常 L2 出門 |

殼：

```text
python scripts/check_asof_ready.py --date 2026-08-14          # 價頂；方向臂須在此 D
python scripts/check_asof_ready.py --date 2026-08-17          # rc=3 假 B3
bash scripts/run_asof_collect_train_verify.sh --date 2026-07-31 --dry-plan --track all
# 截面 8×8 已齊 → SKIP 訓；方向臂不計入歷史 D
```

**pack_complete**：歷史 D＝截面 64 格；價頂才加 Daily3＋Mkt2＋DirStackM。`--track all`＠非價頂預設 `--skip-daily --skip-mkt --skip-stack`（`--force-direction` 才覆寫活鎖）。

## §2 r16 各段 × 現在最佳下一步／可先／可同步

| 段 | 問題 | 最佳下一步 | 可先？ | 可同步？ | 11:04 |
|---|---|---|---|---|---|
| **S0** | 運轉契約 | 跟 r16；開工跟 r18 | — | — | 🟢 |
| **S1** | 日更心跳 | 候 `PriceAdj≥08-17` → B3 20,60（M1b） | **否**（無價） | 開火獨佔 | 🟡 WAIT |
| **S2** | KH | `--check`；apply 另句 | 巡檢已做 | 避開 B3 | 🟡 S0 FIRE 213 |
| **S3** | 特徵 | 沿用 panel＠08-14；缺 D 才 collect | 文件 | 訓 P6＝否 | 🟢 37 欄 |
| **S4 日更** | 邊界 A | 新價才 L2；禁同尺 08-14 | 否 | 歷史 D 須 GO | 🟢＠08-14 |
| **S4 普查** | 其他族 | V0 本窗；殘格點名 | V0＝已做 | 開新族＝否 | V0🟢；V4❄ |
| **S5** | #14 | 披露 dead／thin；不塗綠 | 是 | evaluate＝否 | 🟡 誠實形 |
| **S5 sim** | 風險形狀 | 禁 apply | 否 | 否 | 禁 |
| **C2** | 模型↔漲跌比 | 日更時披露；重選族另句 | 文件 | 重訓讓 B3 | 🟡 |
| **歷史 as-of** | 重覆驗 | 07-31 截面已齊；下一未齊 D 或新價 | dry-plan＝是 | `--apply` 讓 B3 | 🟢 07-31 EXECUTED；方向臂已回 08-14 |
| **M28** | 確立 | E4b 鐘 WAIT；不 E5 | 鐘可重讀 | 否 | 🟡 |

**全專案最佳下一步仍是 M1b**（r18 鎖）。本路徑不取代心跳。

## §3 其他模型驗証（進行到哪）

| 軌 | 本窗 | 下一步 |
|---|---|---|
| **V0** | **EXECUTED** 11:04；方向臂已回 08-14（07-31 曾覆寫，已 skip-rank 復原） | 當帳 |
| **V1** | 07-31 與 08-14 截面皆 64；方向臂鎖＝價頂 08-14 | 歷史 D 勿 `--force-direction` |
| **V2** | 殘格：VECM／TCN／NB／RL | **點名**才 0a |
| **V3** | 08-07 已跑過 | 新 asof 回饋另句；讓 B3 |
| **V4** | 0812 六族 EVIDENCE no-promote | **禁重掃** |
| **V5** | H20 dead、其餘 thin | 不修綠 |

## §4 本窗改了哪些程式

| 檔 | 改什麼 |
|---|---|
| `src/augur/core/asof_ready.py` | snapshot 加 A 格／Daily／Mkt／stack／`at_tip`／`pack_complete`（歷史 D 只看 8×8） |
| `scripts/check_asof_ready.py` | 印上列；假 B3 例改 08-17 |
| `scripts/run_asof_collect_train_verify.sh` | `--track A\|all`；歷史 D 預設不覆寫方向臂；`--force-direction` 才動活鎖 |
| `scripts/run_retrain_all_asof.sh` | mkt-feat 拒倒區間（D < 2026-08-01 不跑 `--since 08-01 --until D`） |
| `scripts/build_core_universe.py` | `--asof-date` 拒假 B3（rc=3） |
| `scripts/run_daily_retrain_l2_all_rank.sh` | 價頂改走 `asof_ready.taiex_price_max` |

未改 standing 20,60；未解 NF；未 promote。

07-31 已跑：`audits/HIST-ASOF-0731-EXECUTED-20260817.md`。下一歷史 D 另貼 HIST-ASOF-apply；禁 `--force-direction` 除非要故意把活鎖往回搬。
