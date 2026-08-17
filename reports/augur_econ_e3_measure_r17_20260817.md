---
title: E3 同尺誠實量產（research）— RankRidge H60
status: research_readout
series: econ_establishment
round: r17
date: 2026-08-17
viewpoint: 2026-08-17T09:12+08:00
layer: "[I]"
gate: egate_H_60_ridge_LO_prodset_r17
until: "2026-04-30"
self_reported: true
---

# E3 同尺誠實量產（research；≠ established）

> **一句**：現役 3 欄 prodset 在 H60 主格上，2014 在位／廣宇宙淨 Sharpe 都贏過扣成本基準，但 DSR 約 0.57、遠低於 0.95；2021 在位宇宙 **輸給基準**。這不是「已經證明能賺錢」。  
> **until**：最後已實現 H60 panel＝**2026-04-30**（進場 05-04、出場 07-29；價頂 08-14）。08-14 出門段未算進淨值。  
> **未做**：付 N、改 verdict、evaluate 閘。H20 仍 dead、H60 仍 thin。

## 凍結細胞（已核准 sha=`1ed91ef5d57c700f`）

RankRidge ≡ B2_ridge × H60 × long-only top 10% 等權 × cost 0.585% × seed 42 × 非重疊再平衡。  
N（ledger SOP-strict）＝**16**（未新寫）；H60 家族 N＝4。DSR 混頻 ppy 以 `60/h` 縮放近似（本窗不重跑他窗）。

## 結果

| 跑 | 來源 | since | 宇宙 | n | 淨 Sharpe | 基準 Sharpe | 相對基準 | DSR | 欄數 |
|---|---|---|---|---|---|---|---|---|---|
| A | **prodset** | 2014 | 在位 | 35 | **1.142** | 1.019 | 贏 | 0.572 | 3 |
| B | **prodset** | 2014 | 廣 | 35 | **1.145** | 0.852 | 贏 | 0.573 | 3 |
| C | **prodset** | 2021 | 在位 | 19 | 1.039 | **1.100** | **輸** | 0.449 | 3 |
| D | **prodset** | 2021 | 廣 | 19 | 0.895 | 0.764 | 贏 | 0.296 | 3 |
| E | canonical | 2014 | 在位 | 35 | 1.467 | 1.019 | 贏 | 0.865 | 34 |
| F | canonical | 2014 | 廣 | 35 | 1.255 | 0.906 | 贏 | 0.708 | 34 |
| G | canonical | 2021 | 在位 | 19 | 1.210 | 1.100 | 贏 | 0.615 | 34 |
| H | canonical | 2021 | 廣 | 19 | 1.126 | 0.880 | 贏 | 0.541 | 34 |
| I | prodset 1.5×成本 | 2014 | 在位 | 35 | 1.107 | 1.012 | 贏 | 0.528 | 3 |

`econ_eval_run` id **3–11**（`paid_n=false`）。`trial_ledger` 仍 32 列。閘仍 `approved`。

## 怎麼讀

1. **現役路徑還沒過 §5 AND**：2021 在位 prodset 淨 ≤ 基準。即便只看 2014，DSR 0.57 ≪ 0.95。  
2. **34 欄研究尺強過 3 欄現役**（2014 在位 1.47 vs 1.14），所以特徵漏斗（E4）是主升力，不是換模型族。  
3. **canonical 2014 在位 DSR 0.865 仍沒過 95%**——與 07-08 地板同方向（當時混頻 0.756；本窗 until／panel 集不同，**不**把 0.865 講成進步已確立）。  
4. 1.5× 成本下 2014 在位 prodset 仍贏基準，短窗成本不是這格的主死因；主死因是 **統計未確立 + 穩健窗未過 + 現役資訊量不足**。

## 不因此做的事

不改 `established`；不 evaluate 閘（live OOS K=4 未到；AND 已有一格失敗）；不救 H20；不把 canonical 1.47 講成用戶看到的產品。
