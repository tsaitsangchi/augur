---
status: executed
series: local_ai_kh
kind: kh8_a1_t2_shadow_s1b
date: 2026-08-08
viewpoint: 2026-08-08T21:48+08:00
go: audits/KH8-DISCRIM-A1-T2-SHADOW-S1B-GO-20260808.md
log: /tmp/kh8-a1-s1/s1b.log
paste: "KH8-DISCRIM-A1-T2-shadow-S1b-EXECUTED | N=12000 | union-ok=True | main-still-False | no-main-swap | E-keep | hold-#1"
self_reported: true
layer: "[I]"
---

# EXECUTED｜A1-T2-shadow S1b · 2026-08-08

```text
N=12000 absent shadow | main∪shadow disc ok=True | MAIN alone still False | 禁止当生产绿
```

## 結果

| 尺 | 值 |
|---|---|
| 影子 | **12000** · 全 absent · batch=`a1t2_s1b_20260808` |
| 主表 | **146808 不變** |
| 主 disc | **ok=False**（minority≈0.0027） |
| **主∪影 disc** | **ok=True** · band 非眾數 **0.078** · 分量非眾數 ≈0.076–0.078 |

## 硬邊界（必讀）

1. **ok=True 僅影子實驗母體**——**≠** 生產 `population_discriminates(主表)` 已綠。  
2. **E 仍適用**於生产／抬層；**禁** depth≥8、禁熱路徑讀影、禁默併主表。  
3. 若將來併主表：须另双明示 GO＋答池污染驗收＋A2 公式落地策略。

## 未動

advise／retrieve／auto_admit 讀路徑；θ；hold-#1。

*完。實驗綠 ≠ 生產綠。*
