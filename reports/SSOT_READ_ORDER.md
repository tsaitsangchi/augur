---
title: Augur 精要讀序（現行 SSOT 索引）
status: current_index
date: 2026-08-19
viewpoint: 2026-08-19T15:40+08:00
layer: "[I]"
role: 把 500+ 份 reports／1000+ 份 audits **合併為精要讀序**；不取代 [N]；不拼接全文
companion_understanding: reports/augur_deep_understanding_and_opt_plan_r20_20260819.md
slim_plan: reports/augur_repo_slim_opt_plan_r20_20260819.md
exec_nav_market: reports/augur_opt_stepwise_all_problems_r19_20260819.md
self_reported: true
---

# Augur 精要讀序（2026-08-19）

> **一句**：不要從 524 份 `reports/` 或 1106 份 `audits/` 從頭讀。先讀下面 **≤15** 條現行入口；其餘是紙本／歷史，不是開工 SSOT。  
> **性質**：[I] 索引。治權義務仍住 `constitution/`／`specs/`／`docs/`／`CLAUDE.md`。  
> **不是**：把所有 md 拼成一份；不是授權刪歷史帳。

---

## A. 治權（什麼不能碰）

1. [`constitution/GOVERNANCE-MAP.md`](../constitution/GOVERNANCE-MAP.md) — 位階與義務落點  
2. [`docs/系統核心思想_v1.10.0.md`](../docs/系統核心思想_v1.10.0.md) — 靈魂  
3. [`docs/原則精華_v1.12.0.md`](../docs/原則精華_v1.12.0.md) — 20 條原則  
4. [`docs/系統架構大憲章_v1.54.0.md`](../docs/系統架構大憲章_v1.54.0.md) — 領域架構  
5. [`CLAUDE.md`](../CLAUDE.md) — AI 協作／#29 矩陣  

正式規格在需要時才打開：`constitution/META-CONSTITUTION.md`、`specs/`。

---

## B. 人話＋理解＋開工（市場／知識／路徑）

6. [`reports/augur_project_charter_plain_zh_r19_20260819.md`](augur_project_charter_plain_zh_r19_20260819.md) — 人話憲章（不創 [N]）  
7. [`reports/augur_deep_understanding_and_opt_plan_r20_20260819.md`](augur_deep_understanding_and_opt_plan_r20_20260819.md) — **現行理解**（刷新 r19 LIVE）  
8. [`reports/augur_opt_stepwise_all_problems_r19_20260819.md`](augur_opt_stepwise_all_problems_r19_20260819.md) — **市場／知識／路徑開工鎖**（r20 **不**取代）  
9. [`reports/augur_local_ai_predict_sim_self_evolve_opt_plan_r16_20260813.md`](augur_local_ai_predict_sim_self_evolve_opt_plan_r16_20260813.md) — S1→S5 心跳契約  
10. [`reports/augur_s1s5_asof_verify_best_next_r19_20260819.md`](augur_s1s5_asof_verify_best_next_r19_20260819.md) — 歷史 as-of 刀  
11. [`reports/augur_path_timing_opt_ops_plan_r18_20260819.md`](augur_path_timing_opt_ops_plan_r18_20260819.md) — 路徑／進出操作手冊  
12. KH：[`reports/augur_local_ai_kh_loop_evolve_opt_plan_20260806_readout.md`](augur_local_ai_kh_loop_evolve_opt_plan_20260806_readout.md) ＋ [`reports/augur_kh_opt_stepwise_best_next_plan_20260813.md`](augur_kh_opt_stepwise_best_next_plan_20260813.md)

---

## C. 本輪專題：倉精化（M14）

13. [`reports/augur_repo_slim_opt_plan_r20_20260819.md`](augur_repo_slim_opt_plan_r20_20260819.md) — **逐步刪／併計畫書**（T0–T4 已做）

---

## D. 碼熱路徑（改行為才讀）

14. `src/augur/core/closed_horizons.py` · `src/augur/core/asof_ready.py`  
15. 日更殼：`scripts/run_daily_asof_predict.sh` · `scripts/run_l0_hotpath_daily.sh` · `scripts/run_daily_retrain_l2_all_rank.sh` · `scripts/run_retrain_all_asof_daily.sh` · `scripts/run_asof_collect_train_verify.sh` · `scripts/check_asof_ready.py` · `scripts/train_ranker.py` · `scripts/predict_asof.py`

---

## 不要當開工入口

| 區 | 為什麼留著 | 何時才打開 |
|---|---|---|
| `audits/*-GO/FIRED/EXECUTED` | 紙本；禁默刪 | 對某一槍的證據 |
| `archive/slim-t2/`（31 份舊輪報告） | 繼承鏈；T2 自 reports/ 搬來 | 查「當時怎麼寫」 |
| `archive/slim-t3/`（14 份祖先計畫） | T3 封存；08-04 閉環 GO 仍在 reports/ | 查 08-03～08-13 優化祖先 |
| `archive/slim-t4/`（7 份 opt_next_best） | T4 封存；非開工入口 | 查 08-04 當日便利條 |
| `handoff_memory/` | 跨對話記憶碎片 | Agent 檢索；人不必讀完 |
| `GROUNDING-MAP.md` | 2026-07-17 快照 [I] | 查當時 schema 盤點；**不是** 2026-08 LIVE |
| `HANDOFF.md` §4 | 多數過期 | 換機手續；現況以理解 r20 LIVE 為準 |

---

## 舊輪報告（T2 封存）

31 份 superseded 理解／執行板／憲章／as-of／KH 譜系在 [`archive/slim-t2/`](../archive/slim-t2/README.md)。**不是**開工入口。

## 祖先計畫（T3 封存）

14 份 08-03～08-13 優化／s1s5 舊窗在 [`archive/slim-t3/`](../archive/slim-t3/README.md)。08-04 閉環 GO 仍在 `reports/`。

## 便利條（T4 封存）

7 份 `opt_next_best` 在 [`archive/slim-t4/`](../archive/slim-t4/README.md)。KH 20260812 選刀檔仍在 `reports/`。

---

## 硬門（讀序不放寬）

```text
no-fake-B3@08-19 | no-promote | no-SIM-apply | NF-pause | standing=H20+H60
| 分數／p_beat／p_mkt ≠ 報酬％ | 觀察≠進場 | 做空≠可融券
| 禁默刪 constitution／specs／heartbeat 殼／GO 紙本
```
