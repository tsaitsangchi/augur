---
title: 日頻 as-of 出單 runbook（feat→core→predict→emit）
status: Steward-usable
date: 2026-08-05
layer: "[I]"
role: 操作 runbook（非憲章；沿用已驗證 2026-08-04 鏈）
ssot_validations:
  - audits/S5-DAILY-20260804-CHAIN-EXECUTED-20260805.md
  - audits/PREDICT-EMIT-H60-20260804-EXECUTED-20260805.md
  - audits/PREDICT-EMIT-H20-20260731-EXECUTED-20260805.md
---

# 日頻 as-of 出單 runbook（2026-08-05）

> **一句**：把庫內最新交易日 `D` 做成可顧問消費的相對機率／排序——**不是**自動 cron；每步須 Steward GO（或本 runbook 明示一句）。  
> **經濟冠軍尺**：RankRidge **H60**（OOS）；**≈30 日題**：H20。兩尺可同日面板並存。  
> **硬邊界**：`FZ/GATE-keep` · `skip-sync` · `no-SIM-apply` · 禁假確立級（dgate pass=0 仍誠實）。

## 0. 前置檢查（唯讀）

```bash
# 價最新日、特徵/core/出單覆蓋
venv/bin/python -c "
from augur.core import db
with db.connect() as c, c.cursor() as cur:
    cur.execute('SELECT max(date) FROM \"TaiwanStockPriceAdj\" WHERE stock_id=%s',('TAIEX',)); print('price',cur.fetchone())
    cur.execute('SELECT max(panel_date) FROM feature_values'); print('fv',cur.fetchone())
    cur.execute('SELECT max(as_of_date) FROM core_universe_asof'); print('core',cur.fetchone())
    cur.execute('SELECT max(panel_date), count(DISTINCT horizon) FROM prediction_probability'); print('pp',cur.fetchone())
"
```

設 `D`＝目標出單日（須為交易日；例：`2026-08-04`）。若 `feature_values`／`core_universe_asof` 已含 `D` → 可跳過 §1–2。

## 1. 特徵面板（`feature_values`）

```bash
venv/bin/python scripts/build_feature_panel.py --panels <D> --asof
```

- `--panels` 可新建非月末交易日面板（日頻錨＝交易日，非另建日頻表）。  
- `--asof`＝現有 core 宇宙股聯集（非全 roster）。  
- RankRidge／prodset 讀 **此表**；`daily_direction_feature_values` 是方向臂另一路，**不替代**本步。

## 2. 核心宇宙 asof

```bash
venv/bin/python scripts/build_core_universe.py \
  --since 2014-01-01 --liquidity-pct 25 --exempt-revenue-financial --asof
```

- **必須** `--since 2014-01-01`（對齊 S1；勿省略→會把 2007 面板灌進來收斂過度）。  
- `build_universe_asof` 會 **DELETE 全表再灌**——故須帶齊全部 ≥2014 之 `feature_values` panel（含新建的 `D`）。  
- 預期：`core_universe_asof` 於 `D` 有列（近窗常 ≈200 檔量級）。

## 3. 出單（`prediction_values`）

```bash
# 顧問 ≈30 日／相對機率主路徑
venv/bin/python scripts/predict_asof.py --run --horizon 20 --asof <D>

# 經濟冠軍尺（可與 H20 同日）
venv/bin/python scripts/predict_asof.py --run --horizon 60 --asof <D>
```

- 建議新日先 `--dry-run` 過目再 `--run`。  
- 模型：`registry.latest(RankRidge, H, asof≤D)`（例：`…_2026-06-30_seed42_56d03625463b3eba`）。

## 4. 相對機率 emit（`prediction_probability`）

```bash
venv/bin/python scripts/calibrate_relative_probability.py --emit --horizon 20 --asof <D>
venv/bin/python scripts/calibrate_relative_probability.py --emit --horizon 60 --asof <D>
```

- 預設沿用既有 Platt calibrator（FREEZE 常仍為 2026-05-31 id）；**重 fit＝另 GO**。  
- 顧問 `max(panel_date)` 會自動指到最新 `D`（一般無需重啟服務）。

## 5. 驗收

```bash
venv/bin/python -c "
from augur.advisor.payload import build_single_ticker_rel_payload
p=build_single_ticker_rel_payload('2330', horizon=20)
print(p.as_of, p.picks[0].score if p.picks else None, (p.prob_note or '')[:100])
"
```

期望：`as_of == <D>`；`econ_verdict` 與 GATE 誠實標示（dead／thin_unestablished／未確立）。

## 6. Paste-ready GO 模板

```
S5-DAILY-ASOF-CHAIN-go | FZ/GATE-keep | skip-sync | no-SIM-apply
# D=<YYYY-MM-DD> horizons=20[,60]
```

## 7. 不做（除非另句）

- FinMind／FRED 放量；sim `--apply`  
- 撤 NF-pause／β5；重訓 RankRidge  
- P6 `--fit` 滾 FREEZE；改 `direction_gate` 門柱  
- 只重建 core `--since D`（會抹掉歷史 asof）

*完。對照執行帳：`S5-DAILY-20260804-CHAIN-EXECUTED`／`PREDICT-EMIT-H{20,60}-20260804`。*
