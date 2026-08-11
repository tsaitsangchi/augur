---
title: KH8 鑑別力 · go-plan（plan-first）
subtitle: 診斷板＋可選路徑；禁假綠抬 depth≥8
status: plan
date: 2026-08-08
viewpoint: 2026-08-08T21:05+08:00
layer: "[I]"
ssot_nav: reports/augur_local_ai_kh_loop_evolve_opt_plan_20260806_readout.md
prior_d2: reports/w2_20260801/D2_kh8_discrimination.md
paste: "KH8-DISCRIM-go-plan | FZ/GATE-keep | no-fake-depth8 | hold-#1 | plan-only"
self_reported: true
---

# KH8-DISCRIM · go-plan（2026-08-08）

> **一句**：母體 **不具鑑別力（ok=False）** 是誠實閘——**禁止**宣稱 depth≥8 進化成功；本檔只給診斷與可裁路徑。  
> **本窗**＝plan-only（Steward 選）；**不**改 `MIN_MINORITY_MASS`、**不**抬層、**不**假綠。  
> **正交**：市場 **hold-#1＠08-10**。

## §0 LIVE（2026-08-08 親查）

| 尺 | 值 |
|---|---|
| `population_discriminates` | **ok=False** |
| note | 判準(1′)不過：band 非眾數質量 **0.002697 ＜ 0.05** |
| n | **146,808** |
| bands | high **146,412** · absent **380** · low **16** |
| `MIN_MINORITY_MASS` | **0.05**（D2 中庸；已入碼） |
| admit_depth | 0:139042 · 3:396 · 7:**146001** · 9:2 |
| 推進實務 | `run_kh_chain --check`：**止於 7**（require_kh8 → fail） |

→ D2 質量門**已生效且在擋假開閘**。問題不再是「缺門檻」，而是「母體分數／band 仍幾乎全 high」。

## §1 問題分解

| # | 問題 | 真相 | 假綠禁 |
|---|---|---|---|
| P1 | 為何 ok=False？ | 非眾數質量≈**0.27%** ≪ 5% | 把門檻降到 0.002 讓 ok=True |
| P2 | 為何幾乎全 high？ | 證據公式＋母體選擇（已終態／已嵌／eligible）→ score 簇在 pass-band | 不重算、只改 band 標籤 |
| P3 | depth≈7 海 | KH8 fail → 誠實停 7；d9=2 歷史殘 | 強制 `--apply-up-to 9` 灌 depth8 |
| P4 | 排序 | 不具鑑別力 → **不**套 KH9-first 深度優先 | 強開排序當「進化成功」 |

## §2 可裁路徑（須另 GO；本檔不代選生效）

| ID | 路徑 | 做什麼 | 風險 | 預效 |
|---|---|---|---|---|
| **A** | **守閘＋治本計分** | 重審 `evidence_score` 分量（terminal／embed／kh4）權重與 band 切點；目標：真實語意薄／厚可分到 ≥5% 非眾數 | 中：重算成本；須回歸鎖 | 正途 |
| **B** | **子母體尺** | 對「可答池／local／某域」另算 disc；全庫尺仍守 | 中：雙尺混淆 | 產品可先讀局部 |
| **C** | **尾巴特赦否** | 明示化學 depth3 未嵌批不算鑑別源（已接近現況 note） | 低 | 敘事 |
| **D** | **放寬 θ** | `MIN_MINORITY_MASS`→0.02／自訂 | **高**（D2 已否決存在性洞） | **不薦** |
| **E** | **凍結 KH8 消費** | 維持 ok=False；深層進化 KPI 改「止於 7 為成功邊界」直到 A 達標 | 低 | 與 readout 一致 |

**建議討論預設（非自動生效）**：**E 守＋排 A plan**；B 可∥產品；**禁 D**；未裁 A 前 **禁** depth≥8 宣稱。

## §3 後續 GO 模板（待 Steward 圈選）

```text
# 診斷／重算（另授）
KH8-DISCRIM-A-score-go-plan | FZ/GATE-keep | no-fake-depth8 | sample-domain=?

# 若裁局部尺
KH8-DISCRIM-B-subset-go | domain=local|… | full-pop-still-strict

# 明確禁
KH8-DISCRIM-D-relax-θ | 不薦
```

## §4 驗收（本 plan 檔）

1. 能復述：ok=False 因 **質量門**非缺碼。  
2. 列出 A–E 與「禁假綠」。  
3. **未**改碼／未抬層／未動 θ。  

## §5 Paste

```text
KH8-DISCRIM-go-plan | FZ/GATE-keep | no-fake-depth8 | hold-#1 | plan-only
# LIVE: ok=False | minority≈0.0027 < 0.05 | stop-at-7
```

*完。[I] plan-only。*
