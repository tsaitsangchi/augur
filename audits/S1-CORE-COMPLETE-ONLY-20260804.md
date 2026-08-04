# S1｜資料完整→核心股（完整入／不完整排）· 2026-08-04

> **位階**：[I] Steward 定錨留痕（非改 [N]；對齊大憲章 universe／原則精華 source-pure）  
> **觸發**：Steward「抓取 finmind 及 fred 資料(資料完整)，只取資料完整做為核心個股，資料不完整的都排外」  
> **parent**：`reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md` §0.5 S1  
> **self-reported（#32a）**

## 一句

**S1「資料完整」落在宇宙層＝只收完整股進核心；不完整＝排除。** 不是把不完整股硬補齊進核心，也不是「339 表全齊才叫完整」。

## 兩層（勿混）

| 層 | 是什麼 | 機制 | 本窗 |
|---|---|---|---|
| **A · 取數（API 門）** | FinMind／FRED 熱路徑落地至 THAW-bounded as-of | `daily_maintenance`／`sync_macro`；403→停記缺席 | A1 仍跑；**≠**本句默授放量／Dividend／寬窗 |
| **B · 核心股（完整度閘）** | 任一面板任一 required 特徵缺 → **排外**；過線即入、**不評分不排名不設 top-N** | `scripts/build_core_universe.py` → `core_universe`／`core_universe_asof`（PIT／#8） | **庫內**；零 API；消費 `feature_values` |

## 既有治權對齊（非新發明）

- 大憲章 universe：核心股＝全部「source-pure 完整」的股；不完整即排除  
- 流動性 P25 地板＋金融保險月營收 conditional 豁免（生產慣例旗標）  
- 預測 ⊥ live API：S1 洞＝告警，**不是**拒訓硬閘；訓練吃 `core_universe_asof`

## 執行預設（生產旗標）

```bash
python scripts/build_core_universe.py \
  --since 2014-01-01 \
  --liquidity-pct 25 \
  --exempt-revenue-financial \
  --asof
```

## 硬禁

- 不以 median-fill／假列把不完整股「補完整」後納入核心  
- 不以本句解凍放量 FinMind／FRED 或 kill A1  
- 不以核心人數多寡當成功尺（質＞量）

---

*完。定錨帳；EXECUTED＝`audits/S1-CORE-COMPLETE-ONLY-EXECUTED-20260804.md`。*
