---
status: executed
series: local_ai_kh
kind: kh8_a1_t2_shadow_s2
date: 2026-08-08
viewpoint: 2026-08-08T21:35+08:00
go: audits/KH8-DISCRIM-A1-T2-SHADOW-S2-GO-20260808.md
log: /tmp/kh8-a1-s2/run.log
batch: a1t2_s2_20260808
paste: "KH8-DISCRIM-A1-T2-shadow-S2-EXECUTED | n=139043 | union-ok=True | main-False | no-main-swap | E-keep | hold-#1"
self_reported: true
layer: "[I]"
---

# EXECUTED｜A1-T2-shadow S2 · 2026-08-08

```text
full T2 shadow n=139,043 | main∪shadow ok=True minority≈0.49 | MAIN still False | ~29s
```

## 結果

| 尺 | 值 |
|---|---|
| 影子 | **139,043** · 全 absent · batch=`a1t2_s2_20260808` |
| 主表 | **146,808 不變** |
| 主 disc | **ok=False** |
| 主∪影 | **ok=True** · band 非眾數 **≈0.488** · 分量非眾數 ≈0.486 |
| ∪ n | **285,851**（≈全 item） |

## 硬邊界

**實驗母體綠 ≠ 生產綠。** 禁併主表／禁熱路徑讀影／禁 depth≥8／E 仍守。合併＝另高門檻双明示 GO。

hold-#1 不讓。

*完。*
