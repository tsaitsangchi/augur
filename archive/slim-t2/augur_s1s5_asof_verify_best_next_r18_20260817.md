---
title: r16 閉環 × r18 LIVE——各段最佳下一步／可先／可同步＋歷史 as-of 答覆
status: superseded
superseded_by: reports/augur_s1s5_asof_verify_best_next_r19_20260819.md
series: s1s5_loop
round: r18
date: 2026-08-17
viewpoint: 2026-08-18T14:55+08:00
layer: "[I]"
role: 把 r16 運轉 SSOT 對到 r18 視點；答「過去 as-of 能否收特徵／訓／驗」；V0＋V1 已跑
parent_ssot: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_r16_20260813.md
exec_nav: reports/augur_opt_stepwise_all_problems_r18_20260817.md
other_verify: reports/augur_s4_other_model_verify_matrix_plan_20260806.md
code:
  - scripts/run_asof_collect_train_verify.sh
  - scripts/verify_asof_families.py
  - src/augur/core/asof_ready.py
  - scripts/check_asof_ready.py
  - scripts/build_core_universe.py
self_reported: true
---

# r16 閉環問題板（對齊 2026-08-18 13:50 LIVE）

> **已被 supersede**：開工請改讀 `reports/augur_s1s5_asof_verify_best_next_r19_20260819.md`（價頂／出門＝08-18；V1 已重跑）。本檔 LIVE（tip 08-17／08-18 假 B3）過期。

> **一句**：閉環怎麼轉仍＝r16；開工順序＝r18。**可以**用過去 as-of 收特徵、訓練、驗証——這是正門，不是假今天。  
> **LIVE 14:55**：價頂／包＝08-17。RETRAIN-ALL force 已閉。出門仍本晨 B3 H20+H60。08-18＝假 B3。KH S0–S3 ok。V1 H5 OOS 近 0。H10 OOS walk 全 no_model（日曆閘）。同日 IC 不採。

## §1 過去 as-of：可以，而且是唯一合法做法

| 可以 | 不可以 |
|---|---|
| D ≤ PriceAdj TAIEX 價頂，且只用當時可見資料 | 08-18 當 as-of（價頂仍 **08-17**） |
| 截面族**共用** `feature_values`＠D（不必每族重抓 API） | 拿 D+1 價回填 D 的特徵 |
| `check_asof_ready.py --date D` → ready 才 collect／訓 | 無價卻 `train_* --asof D` |
| 多 D walk-forward 當重覆驗（#11） | 同尺重掃 0812 NF 六族變綠 |
| `--track A`＝L2 邊界 A；`--track all`＝截面 8×8（價頂才動方向臂） | promote／sim-apply／把 Daily* 塞進日常 L2；`--track other --apply` |

殼：

```text
python scripts/check_asof_ready.py --date 2026-08-17          # 價頂；方向臂須在此 D
python scripts/check_asof_ready.py --date 2026-08-18          # rc=3 假 B3
bash scripts/run_asof_collect_train_verify.sh --date 2026-07-31 --dry-plan --track all
# 截面 8×8 已齊 → SKIP 訓；方向臂不計入歷史 D
```

**pack_complete**：歷史 D＝截面 64 格；價頂才加 Daily3＋Mkt2＋DirStackM。`--track all`＠非價頂預設 `--skip-daily --skip-mkt --skip-stack`（`--force-direction` 才覆寫活鎖）。

**其他模型**：共用 `feature_values`＠D 的只有截面 8 族。VECM／TCN／NB／RL 缺 adapter／額外張量，須點名 GO。0812 NF 六族禁同尺重掃。SeqLSTM 評測不寫庫。殼：

```text
bash scripts/run_asof_collect_train_verify.sh --date 2026-08-17 --dry-plan --track other
# rc=0：V0 族矩陣；不訓。--apply --track other 仍 rc=6
python scripts/verify_asof_families.py --date 2026-07-31 --ic --oos   # 已實現窗 rank IC（排除同日）
python scripts/verify_asof_families.py --walk --oos --horizon 10 --limit 4
python scripts/check_asof_ready.py --scan
```

## §2 r16 各段 × 現在最佳下一步／可先／可同步

| 段 | 問題 | 最佳下一步 | 可先？ | 可同步？ | 13:50 |
|---|---|---|---|---|---|
| **S0** | 運轉契約 | 跟 r16；開工跟 r18 | — | — | 🟢 |
| **S1** | 日更心跳 | 候 `PriceAdj≥08-18` → B3 20,60（載本槍新 RankRidge） | **否**（無價） | 開火獨佔 | 🟢＠08-17；下一 D WAIT |
| **S2** | KH | 巡檢即可；S0／S3 已閉 | 是 | 避開 B3 | 🟢 priority_hit=∅ |
| **S3** | 特徵 | 沿用 panel＠08-17；缺 D 才 collect | 文件 | P6 freeze 仍＠08-14 | 🟢 37 欄；P6 缺口 |
| **S4 日更** | 邊界 A | 新價才 L2；禁同尺再 `--force` 無 GO | 否 | 歷史 D 須 GO | 🟢＠08-17 force 已閉 |
| **S4 普查** | 其他族 | V0／V1 H5 已跑；H10 日曆閘；殘格點名；禁 0812 | H5 walk＝已做；H10＝已探 | 開新族＝否 | V0🟢 V1 H5🟢；H10 閘；V4❄ |
| **S5** | #14 | 披露 dead／thin；不塗綠 | 是 | evaluate＝否 | 🟡 誠實形 |
| **S5 sim** | 風險形狀 | 禁 apply | 否 | 否 | 禁 |
| **C2** | 模型↔漲跌比 | 日更時披露；重選族另句 | 文件 | 重訓讓 B3 | 🟡 |
| **歷史 as-of** | 重覆驗 | 已齊＝07-31／08-07／08-13／08-14／08-17；下一未齊 08-12 缺 32（無已實現窗） | dry-plan／scan＝是 | `--apply` 須 HIST-ASOF-apply | 🟢＠08-13 |
| **M28** | 確立 | E4b 鐘 WAIT；不 E5 | 鐘可重讀 | 否 | 🟡 |

**全專案最佳下一步仍是 M1b**（r18 鎖）。本路徑不取代心跳。

## §3 其他模型驗証（進行到哪）

| 軌 | 本窗 | 下一步 |
|---|---|---|
| **V0** | **EXECUTED** force＠08-17 64／64；方向臂活鎖＝08-17（本槍重訓） | 當帳；下一 B3 載新 artifact |
| **V1** | **EXECUTED** H5＠08-04…08-07（stamp 07-31）近 0／偏負；**H10 walk 全 no_model**（最早完整且 H10 已實現＝07-31，同日 stamp 被 `--oos` 排除；08-07 後僅 6 日＜11） | 候價蓋過使 08-07 實現 H10；或另 HIST＠06-30 再 walk 07-31。勿 `--force-direction` |
| **V2** | 殘格：VECM／TCN／NB／RL 登錄＝0 | `--track other --apply` rc=6；**點名**才 0a |
| **V3** | 08-07 已跑過 | 新 asof 回饋另句；讓 B3 |
| **V4** | 0812 六族 EVIDENCE no-promote | **禁重掃** |
| **V5** | H20 dead、其餘 thin | 不修綠 |

## §4 本窗改了哪些程式

| 檔 | 改什麼 |
|---|---|
| `src/augur/core/asof_ready.py` | 族矩陣、`label_is_realized`、`stamp_kind`、`scan_realized_panels`、`format_other_lane_registry`、`walk_no_model_hint`；假 B3 例 08-18 |
| `src/augur/models/registry.py` | `latest_before`（OOS：stamp < D） |
| `scripts/verify_asof_families.py` | V0／V1；`--oos`／`--walk --horizon`；同日 stamp 標旗；其他車道表 |
| `scripts/check_asof_ready.py` | `--family-matrix` 印其他車道表；`--scan` 填 realized_H |
| `scripts/run_asof_collect_train_verify.sh` | `--track other --dry-plan`＝V0 rc=0；`--apply` 仍 rc=6 |
| `scripts/predict_asof.py` | `quiet=`；`strict_before=` |

未改 standing 20,60；未解 NF；未 promote。

V1：`audits/HIST-ASOF-V1-IC-EXECUTED-20260818.md`。OOS walk H5：`audits/HIST-ASOF-OOS-WALK-EXECUTED-20260818.md`。OOS walk H10：`audits/HIST-ASOF-OOS-WALK-H10-EXECUTED-20260818.md`。07-31 訓包：`audits/HIST-ASOF-0731-EXECUTED-20260817.md`。08-07 訓包：`audits/HIST-ASOF-0807-EXECUTED-20260818.md`。08-13 訓包：`audits/HIST-ASOF-0813-EXECUTED-20260818.md`。價頂 force：`audits/RETRAIN-ALL-0817-FORCE-EXECUTED-20260818.md`。下一未齊 08-12 另貼 HIST-ASOF-apply；禁 `--force-direction` 除非要故意把活鎖往回搬。
