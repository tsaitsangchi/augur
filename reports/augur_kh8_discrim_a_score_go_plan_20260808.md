---
title: KH8 路徑 A · evidence score 治本 go-plan
subtitle: 破母體選擇效應／分數簇 high；plan-only 不改碼
status: plan
date: 2026-08-08
viewpoint: 2026-08-08T21:15+08:00
layer: "[I]"
parent: reports/augur_kh8_discrim_go_plan_20260808.md
e_adopted: audits/KH8-DISCRIM-E-ADOPTED-20260808.md
paste: "KH8-DISCRIM-A-score-go-plan | FZ/GATE-keep | no-fake-depth8 | E-keep | hold-#1 | plan-only"
self_reported: true
---

# KH8-DISCRIM · A · evidence score go-plan（2026-08-08）

> **一句**：鑑別力假綠的根因是 **計分公式＋母體選擇** 使≈99.7% 落在 score≥0.72＝high；A＝治本重審計分，**不是**降 θ。  
> **繼承 E**：止於 7 成功邊界直至本 A 達標且 disc ok=True。  
> **本窗**＝plan-only；零改碼／零重算／零抬層。

## §0 LIVE 診斷（親查）

| 尺 | 值 |
|---|---|
| score 分位 | min0 · p10=**0.72** · p50=**0.72** · p90=**0.72** · max1 |
| 峰 | **0.72 × 136,739**（≈93%）；次峰 0.86／1.00 |
| band | high **146,412** · absent 380 · low 16 · **medium≈0** |
| components | terminal **全 1.0**；embed／kh4_ok 僅 396 列為 0（depth3 未嵌尾巴） |
| disc | ok=False · minority≈0.0027＜0.05 |

### 結構恒等式（碼）

```text
score = 0.35*cite_norm + 0.25*terminal + 0.25*embed + 0.15*kh4_ok − 0.40*contra
band  = high if ≥0.70 | medium ≥0.40 | low ≥0.15 | absent
```

母體幾乎皆＝「已句切＋已嵌＋eligible」→  
`terminal=embed=kh4_ok=1` → 底線 **0.65**；再加 ≥1 句 → **≥0.72 → 必 high**。  
→ **結構上不可鑑別**（`evidence.py` C-2 註已釘）。尾巴 396＝未嵌批，不是語意薄厚。

## §1 治本選項（Steward 裁一主軸；可混）

| ID | 方向 | 作法摘要 | 預期 disc | 風險 |
|---|---|---|---|---|
| **A1 擴母體** | 權重覆蓋「薄項」 | 對有標題／有文未嵌／未 eligible 亦寫 weight（诚实低分） | 非眾數質量↑ | 庫寫量大；須防污染答池 |
| **A2 改公式** | 打破 0.65 底線 | 降「齊備獎勵」；加**相對**訊號（來源權威階、引文多樣、時新、domain 稀有度、矛盾／過期） | 分數展開 | 須 #15 缺料誠實；回歸自測 |
| **A3 重切 band** | 只改閾值 | 依現分佈用分位切 high／medium／low | 可立刻過 θ | **高假綠風險**（標籤假分級）；**不薦獨用** |
| **A4 相對尺** | disc 改用組內秩 | 母體內 z-score／分位秩，band＝分位桶 | 可過質量門 | 與絕對分數雙軌；文件要釘 |
| **A5 分域 disc** | 與父 plan B 合流 | local／哲學等子集先達標 | 產品臂先綠 | 全庫尺仍 E |

**建議預設（討論用）**：**A2 為主**＋**A1 有界試點**；**禁 A3 獨裁**；A4／A5 可∥。

## §2 建議執行波（另 GO 才跑）

| 波 | 內容 | 准／禁 |
|---|---|---|
| **A-0** | 本 plan＋樣本 score 直述（已做） | 只讀 |
| **A-1** | 紙上／scratch 模擬：候選公式在 1k 抽樣之 band 質量 | 不寫庫 |
| **A-2** | `--dry-run` 重算影子表或側表 | 禁覆寫主表直至双明示 |
| **A-3** | 有界 domain 切換＋`population_discriminates` 複測 | 仍 **no-fake-depth8**；E 到 ok |
| **A-4** | 全量切換＋深度優先恢復條件明文 | 須 disc ok 且 Steward 宣佈撤 E 成功邊界 |

## §3 成功／證偽

| | |
|---|---|
| **成功** | 全庫（或宣佈的子集）`band_minority_mass≥0.05` 且至少一 component 非眾數質量≥0.05；**且**抽樣人工看「high≠僅齊備項」 |
| **證偽** | 只靠降 θ 或只挪 band 切點使 ok=True，分數分佈形狀不變 |
| **仍守** | E：在成功前 **stop-at-7**；hold-#1；無 web／對話 approve |

## §4 Paste

```text
KH8-DISCRIM-A-score-go-plan | FZ/GATE-keep | no-fake-depth8 | E-keep | hold-#1 | plan-only
# 建議主軸 A2（改公式）＋A1 試點；禁 A3 獨用
# 下一刀候選: KH8-DISCRIM-A1-sim-go | sample=1000 | no-write
```

*完。[I] plan-only。*
