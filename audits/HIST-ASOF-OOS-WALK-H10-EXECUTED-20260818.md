---
status: executed
series: s1s5_loop
track: V1-oos-h10
date: 2026-08-18
viewpoint: 2026-08-18T14:55+08:00
plan: reports/augur_s1s5_asof_verify_best_next_r18_20260817.md
nav: reports/augur_opt_stepwise_all_problems_r18_20260817.md
paste: "再進行其他模型驗証＋過去 as-of 收特徵／訓／驗＋改程式"
self_reported: true
layer: "[I]"
---

# EXECUTED｜V1 OOS walk H10（日曆閘；全 no_model）

Steward：全問題下一步＋其他模型驗証＋過去 as-of 能否收特徵／訓／驗＋改程式。

## 答（H10 這一槍）

- 可以 walk 任意 `H_TRACK`：`--walk --oos --horizon 10`。非法窗（例 H82）→ rc=2。
- **本槍結果**：四個已實現 H10 的 panel（07-31／06-30／05-31／04-30）**全族 no_model**。
- 原因不是程式壞：`--oos` 要求 stamp < panel。最早完整 8×8 且 H10 已實現＝**07-31**，但其 stamp 是同日 → 被排除。較新完整日 08-07 之後僅 **6** 個交易日（H10 須 **11**）。
- 不是假綠、不升格、IC ≠ 報酬％。

## 可先／須 GO

| 路 | 何時 | 須 GO？ |
|---|---|---|
| 候價蓋過，使 08-07 的 n_after≥11（約再 5 個交易日）再 `--walk --horizon 10` | 價到 | 否（唯讀） |
| HIST 訓 **06-30**（缺 52）再 walk panel **07-31** | 現在可排 | **是** `HIST-ASOF-apply` |
| 補 08-12（缺 32） | 現在可排；**無已實現窗** | **是**；不解決 H10 OOS |

JSON：`/tmp/v1-oos-walk-h10.json`。
