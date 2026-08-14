---
status: executed
series: s4_s5_verify
track: RETRAIN-ALL
date: 2026-08-13
viewpoint: 2026-08-13T15:45+08:00
asof: "2026-08-12"
shell: scripts/run_retrain_all_asof.sh
paste: "DIRLOCK-latest | RETRAIN-ALL-0812 --no-resume | no-promote | no-fake-B3"
self_reported: true
layer: "[I]"
---

# EXECUTED｜方向臂改鎖可更新最新日＋全模型重訓＠2026-08-12

`bash scripts/run_retrain_all_asof.sh --date 2026-08-12 --apply --no-resume`  
RC=0 · 約 58 min · **resume=0**（40 格全重訓）· skip-sync · **no-promote**。

## 鎖（SSOT）

方向臂 `--asof`／`--until` **未指定 → PriceAdj TAIEX 價頂**（可更新最新日）。  
≠ 完整性定案錨 `COMPLETENESS_ASOF=2026-05-31`。  
指定日不得超過價頂（假 B3）。

| 探針 | 值 |
|---|---|
| `check_asof_ready.py --latest-date` | **2026-08-12** |
| `bind_iso(None)` | **2026-08-12** |
| `--asof 2026-08-13` | rc=3 |

落地：`asof_ready.pick_lock`／`resolve_lock`／`bind_iso`；Daily／Mkt／DirStack 訓練＋日／月／市場特徵＋`derive_market_iv` 預設改鎖。

## 重訓結果＠08-12

| 臂 | 結果 |
|---|---|
| 截面 8×5 | **40／40** 全重訓（無 resume 跳過） |
| DailyLogit／DailyGBDT／DailyGBDT_cal | asof＝**08-12**；v1 champion＝Logit |
| MktLogit／MktLogit_v2 | asof＝**08-12**；特徵頂仍 TRI **08-07** |
| DirStack／DirStackM | OOS 重寫；DirStackM asof＝**08-12** |

LIVE `prediction_probability` tip 仍 **08-12**（未 emit／未 SERVE-SWAP）。

## 誠實 SKIP

SeqLSTM／classical TS／threelens／0812 NF 六族／P6 重 fit／promote。

*v1 改鎖＋重訓；誠實形。*
