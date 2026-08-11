---
title: RETRAIN-ASOF-0731 · RankRidge 五 horizon 重訓計畫
status: plan_first
series: s4_retrain
track: RETRAIN-ASOF-0731
date: 2026-08-07
viewpoint: 2026-08-07T13:32+08:00
paste: "RETRAIN-ASOF-0731-go-plan | FZ/GATE-keep | skip-sync | no-SIM-apply | RankRidge | asof=2026-07-31 | H=20,40,60,82,120"
nav: reports/augur_opt_stepwise_best_next_plan_r12_20260807.md
layer: "[I]"
role: LIVE 熱路徑 RankRidge 重訓到 asof=2026-07-31；本檔≠開訓 GO；≠默換 LIVE serve
self_reported: true
---

# RETRAIN-ASOF-0731-go-plan｜RankRidge × 五 horizon · 2026-08-07

> **Steward 選**：LIVE 熱路徑 **RankRidge**；horizon＝**H20／40／60／82／120**；**plan_first**（本檔零開訓）。  
> **一句**：把生產族 asof 自現行多為 `2026-06-30` **重訓到 `2026-07-31`**（prodset）；**不**因此自動換每日 B3 serve、**不**升格確立級、**不**開挑戰族。  
> **主軸疊加**：#1 候 A→B3＠08-07 **hold**——執行波須讓 B3／錯峰。

---

## §0 護欄

```text
RETRAIN-ASOF-0731-go-plan | FZ/GATE-keep | skip-sync | no-SIM-apply
| RankRidge-only | asof=2026-07-31 | seeds=42 | no-promote-default | hold-#1
# ≠ RETRAIN-ASOF-0731-go（開訓）；≠ 換 LIVE model_id；≠ 撤 NF；≠ direction 臂
```

| 可（計畫書） | 不可 |
|---|---|
| 寫範圍／指令／驗收／風險 | 本句 `train_ranker --run` |
| 預設 seed**=42**（與現行 LIVE 同位；Ridge 確定性） | 默認改 `predict_asof`／standing 掛載 |
| 五 H 產物寫 `model_registry`＋joblib | sim `--apply`；改 dgate；假 B3 |
| 錯峰 #1 | 順帶重訓 RankGBDT／Wave-A |

---

## §1 範圍（誠實縮小「所有模型」）

| 項 | 值 |
|---|---|
| 族 | **僅 `RankRidge`**（LIVE 相對排序主族） |
| asof | **`2026-07-31`**（train 用 ≤asof panels；`asof=True` point-in-time） |
| feature_source | **`prodset`** |
| seed | **42**（與現 LIVE 一致；RankRidge 忽略 seed 變異） |
| horizon | **20, 40, 60, 82, 120**（Steward：五窗全訓） |
| 不做 | RankGBDT／Wave-A／Daily*／Mkt*／DirStack* |

現 LIVE（對照；asof 仍多為 06-30）：

- H20／H60＝每日 B3 主掛  
- H40／H82／H120＝旁掛

---

## §2 執行波（須另句 GO）

```bash
# 僅在 Steward 貼 RETRAIN-ASOF-0731-go 後跑
# 若 run_daily_asof_predict 在場 → YIELD，不搶
for h in 20 40 60 82 120; do
  PYTHONPATH=src ./venv/bin/python scripts/train_ranker.py --run \
    --family RankRidge --horizon "$h" --seed 42 \
    --asof 2026-07-31 --feature-source=prodset
done
```

預期 model_id 形：

`RankRidge_H{h}_2026-07-31_seed42_{feature_hash}`

---

## §3 驗收

| # | 尺 |
|---|---|
| 1 | 五 H 皆 RC=0；joblib 在 `models_artifacts/`；`model_registry` 有對應列 |
| 2 | `trained_asof`／id 內日期＝**2026-07-31**；feature_hash 與 prodset 契約可溯 |
| 3 | **不**自動改 LIVE serve／standing；換掛須另句（如 `SERVE-SWAP-0731-go`） |
| 4 | #14 可選：對 H60（主尺）用既有 walk-forward 探針對照舊冠軍門檻——**另選**，非本 GO 默認 |
| 5 | 全程 skip-sync；無假 B3；NF-pause 其他族 keep |

---

## §4 風險／誠實

- asof 07-31 **晚於**驗證常用 until=06-30：屬**前進重訓**，非同窗復現；OOS 數字會變，禁止用舊 1.30／1.25 直接宣稱「一樣」。  
- H20 仍可能 `econ=dead`——重訓≠修綠。  
- H82／H120 樣本薄——旁掛可訓，升格敘事仍弱。  
- registry 已允許 `RankRidge`——與 Wave-A CHK 問題無關。

---

## §5 Paste-ready

採納計畫（零開訓）：

```text
RETRAIN-ASOF-0731-plan-adopt | FZ/GATE-keep | RankRidge | H=20,40,60,82,120 | asof=2026-07-31 | no-train | hold-#1
```

開訓執行：

```text
RETRAIN-ASOF-0731-go | FZ/GATE-keep | skip-sync | no-SIM-apply | RankRidge | seeds=42 | H=20,40,60,82,120 | asof=2026-07-31 | no-promote-default | hold-#1
```

換 LIVE serve（**另句、本計畫不授**）：

```text
SERVE-SWAP-0731-go | FZ/GATE-keep | RankRidge | asof=2026-07-31 | …（須明示 horizon）
```

---

## §6 本計畫書驗收

1. 範圍＝RankRidge 五 H · asof=2026-07-31 · prodset · seed42。  
2. 本檔≠開訓、≠換 serve。  
3. 與 #1／NF-pause／no-promote 對齊。  

*完。[I] plan_first。*
