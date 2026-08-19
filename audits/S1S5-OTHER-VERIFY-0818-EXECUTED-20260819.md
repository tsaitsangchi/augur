---
status: executed
series: s1s5_loop
track: other-verify
date: 2026-08-19
viewpoint: 2026-08-19T14:40+08:00
go: audits/S1S5-OTHER-VERIFY-0818-GO-20260819.md
fired: audits/S1S5-OTHER-VERIFY-0818-FIRED-20260819.md
plan: reports/augur_s1s5_asof_verify_best_next_r19_20260819.md
paste: "S1S5-OTHER-VERIFY-EXECUTED | D≤08-18 | V0 64/64 | V1 H5 walk n=6 | H10 all no_model | no-apply | no-promote | fake-B3@08-19 rc=3"
self_reported: true
layer: "[I]"
---

# EXECUTED｜其他模型驗証 V0／V1＠價頂 08-18

## 做了什麼

| 步 | 指令 | 結果 |
|---|---|---|
| scan | `check_asof_ready.py --scan` | 已齊近：08-18／17／14／13／07／07-31。未齊下一＝**08-12 缺 32**（無已實現窗）。08-10 未齊 52 但 **realized_H=5** |
| V0 | `verify_asof_families.py --date 2026-08-18` | ready；A格 64／64；pack=True；其他車道 n=0 |
| 假 B3 | `--date 2026-08-19` | **fake_b3 rc=3** |
| other dry | `run_asof_collect_train_verify.sh --date 2026-08-18 --dry-plan --track other` | **rc=0** 盤點；不訓 |
| V1 H5 | `--walk --oos --horizon 5 --limit 6` | 6 panel；JSON `/tmp/v1-oos-walk-h5.json` |
| V1 H10 | `--walk --oos --horizon 10 --limit 4` | 4 panel **全 no_model**；JSON `/tmp/v1-oos-walk-h10.json` |
| IC 08-07 | `--date 2026-08-07 --ic --oos` | 僅 H5；與 walk 同列 |
| IC 07-31 | `--date 2026-07-31 --ic --oos` | H5+H10 全 no_model |
| IC 08-18 | `--date 2026-08-18 --ic --oos` | 無已實現窗 → 略過 |

零寫 `prediction_values`。未 `--apply`。未 promote。未重掃 0812。

## V1 H5 摘要（OOS；IC ≠ 報酬％）

- **新**：panel **2026-08-10**（n_after=6）八族 IC 皆正；最高 RankKNN +0.2724；冠軍 RankRidge +0.0915。當日 8×8 **未齊**（12／64）。
- **舊**：08-07／06／05／04 均值負或近 0。07-31 OOS＝no_model。
- 五 panel 族均值：KNN +0.069；Ridge −0.064。**不升格。**

## V1 H10

已實現該窗的 panel 沒有 stamp < panel 的模型。08-07 之後交易日＝7＜11。不是假綠。

## 下一槍（本帳不開）

```text
# 候價
B3-go | D≥2026-08-19 | horizons=20,60 | 須 PriceAdj≥該日

# 另句
HIST-ASOF-apply | date=2026-08-12 | track=all | no-force-direction
KH-S0-apply-go | drain up_to=0 limit=63 | no-lift-gt-KH2
```
