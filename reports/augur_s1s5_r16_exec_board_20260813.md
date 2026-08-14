---
title: r16 閉環——全問題選刀＋歷史 as-of 程式閘＋V1＠08-07
status: final
series: s1s5_loop
date: 2026-08-13
viewpoint: 2026-08-13T13:25+08:00
layer: "[I]"
parent_ssot: reports/augur_local_ai_predict_sim_self_evolve_opt_plan_r16_20260813.md
exec_nav: reports/augur_opt_stepwise_all_problems_r15_20260813.md
shell: scripts/run_asof_collect_train_verify.sh
self_reported: true
---

# r16 執行板｜最佳下一步／可先／可同步＋ as-of 程式（2026-08-13）

> **一句**：依 r16 轉。主軸仍候 08-13；**可先**＝歷史 as-of 閘已寫進程式；**其他模型驗証**＝邊界 A＠**08-07**（共用已有 37 種特徵，不重抓 API、不假 B3、不重掃 0812 NF）。  
> **可否用過去 as-of 收特徵／訓／驗**：**可以**，而且殼現在會擋「價還沒到的 D」。

---

## §1 決策卡

| 問 | 答 |
|---|---|
| **全專案最佳下一步** | M1：候 `PriceAdj≥08-13` → B3 `20,60` → L2（禁假跑） |
| **可先（本窗）** | as-of 閘程式；08-07 特徵已在故 skip collect；V1 訓邊界 A＠08-07 |
| **可同步** | KH `--check`；誠實 #14；閘自測。B3 開火讓出 CPU |
| **其他模型驗証** | V0 已做；V1＝WP-H **08-07**（本窗 apply）；V4 禁重掃；殘格仍須點名 |
| **過去 as-of？** | **能**。截面族共用 `feature_values`；`check_asof_ready` rc=0 才訓；rc=3＝假 B3 |
| **不要** | 假 B3＠08-13；sim-apply；promote；NF 六族再刷；Daily* 塞 L2 |

---

## §2 全問題（r16 視點）

市場主軸 M1＝WAIT。其餘與 r15 全板同；本窗動到的列：

| # | 最佳下一步 | 可先 | 可同步 | 本窗 |
|---|---|---|---|---|
| **M1** | 候 08-13 → B3→L2 | 否 | 開火獨佔 | WAIT |
| **M18／V1** | 歷史 as-of 邊界 A | 是（≠假今天） | 讓 B3 | **08-07 apply** |
| **S3 collect** | 缺 panel 才 `build_feature_panel --panels D` | 08-07 已有 → skip | 是 | 閘已寫 |
| **K0** | ingest `--check` | 是 | 避開 B3 | 維持 |

其餘 M2 披露、M9 P6 訓❄、M10 NF-pause、M12 禁 sim、K8 E-keep、K9 plan-only——不改。

---

## §3 程式改了什麼

| 檔 | 做什麼 |
|---|---|
| `src/augur/core/asof_ready.py` | 純閘：ready／need_collect／fake_b3 |
| `scripts/check_asof_ready.py` | 唯讀探針；rc 0／2／3／4 |
| `scripts/train_ranker.py` | asof > 價頂 → 中止 |
| `scripts/predict_asof.py` | 假 B3 或無 panel → 中止 |
| `scripts/build_feature_panel.py` | `--panels` 晚於價頂 → rc=3 |
| `scripts/run_daily_retrain_l2_all_rank.sh` | apply 時無 fv＠D → rc=4 |
| `scripts/run_asof_collect_train_verify.sh` | collect→L2 A→誠實 #14；no-promote |

實測：`--date 2026-08-13` train／panel／hist 殼皆 **拒**；`--date 2026-08-07` **ready**（37 種、27930 列、registry_a 原 0）。

---

## §4 其他模型 × as-of

截面八族 **共用** 08-07 panel，不是各族各採一套價。序列／圖／Daily*／NF 殘格 **不是**這張表就能訓。

*完。*
