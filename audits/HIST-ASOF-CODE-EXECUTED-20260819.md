---
status: executed
series: s1s5_loop
track: hist-asof-code
date: 2026-08-19
viewpoint: 2026-08-19T14:45+08:00
go: audits/HIST-ASOF-CODE-GO-20260819.md
fired: audits/HIST-ASOF-CODE-FIRED-20260819.md
plan: reports/augur_s1s5_asof_verify_best_next_r19_20260819.md
paste: "HIST-ASOF-code EXECUTED | fake-b3-date=08-19 | 08-12 dry train | no-apply | V0 64/64 | selftest pass"
self_reported: true
layer: "[I]"
---

# EXECUTED｜歷史 as-of 殼／探針（改程式；未訓 08-12）

## 答 Steward

**可以。** 過去 as-of（D ≤ PriceAdj 價頂）是收特徵、訓截面 8 族、OOS 驗証的正門。不是假跑今天。08-19 仍假 B3。真訓 08-12 須另句 `HIST-ASOF-apply`。

## 程式

| 檔 | 改什麼 | 自測 |
|---|---|---|
| `src/augur/core/asof_ready.py` | `fake_b3_probe_date`；`hist_next_action` | `--selftest` 全過 |
| `scripts/check_asof_ready.py` | `--fake-b3-date`；scan 建議下一未齊；印下一刀 | 探針 08-19；08-12＝train 32／64 |
| `scripts/run_asof_collect_train_verify.sh` | 假 B3 跟價頂次日；缺 core 仍補宇宙；08-12 dry 列入自測 | `--selftest` 全過 |
| `scripts/verify_asof_families.py` | 註解不再把 08-18 當假 B3 | V0＠08-18 64／64 |

`--track other --apply`＠08-12 仍 **rc=6**（未開訓）。

## 其他模型驗証（本窗複驗）

V0＠08-18＝64／64。其他車道 n=0。V1 H5／H10 數字見 `audits/S1S5-OTHER-VERIFY-0818-EXECUTED-20260819.md`（不重訓、不升格）。

## 沒做

假 B3＠08-19 訓／出單；HIST `--apply`＠08-12；promote；0812 重掃；KH `--apply`。
