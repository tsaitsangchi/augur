---
status: executed
series: local_ai_kh
kind: kh8_a1_t2_shadow_s1
date: 2026-08-08
viewpoint: 2026-08-08T21:45+08:00
go: audits/KH8-DISCRIM-A1-T2-SHADOW-S1-GO-20260808.md
log: /tmp/kh8-a1-s1/run.log
table: knowhow_evidence_weight_shadow_t2
batch: a1t2_s1_20260808
paste: "KH8-DISCRIM-A1-T2-shadow-S1-EXECUTED | N=5000 | main-unchanged | union-ok=False | minority0.0355 | E-keep | hold-#1"
self_reported: true
layer: "[I]"
---

# EXECUTED｜A1-T2-shadow S1 · 2026-08-08

```text
shadow N=5000 absent | main 146808 unchanged | union minority 0.0027→0.0355 | still ok=False
```

## 結果

| 尺 | 值 |
|---|---|
| 表 | `knowhow_evidence_weight_shadow_t2` batch=`a1t2_s1_20260808` |
| 影列 | **5000** · band 全 **absent**（A2 草案＋title_only） |
| 主表 count | **146808→146808**（未動） |
| 主 disc | ok=False · minority≈0.0027 |
| **主∪影 disc** | ok=False · band 非眾數 **0.0355＜0.05** |
| 分量（∪） | terminal／embed／kh4 非眾數 ≈**0.033–0.036**（開始有變異） |

## 判讀

- S1 方向正確：標題影子拉高少數質量，**尚未過門**。  
- 粗估：若影列皆 absent，約需 **n_union ≳ high/0.95 ≈ 154.1k** → 再增 ≈**7.3k** 級 absent 影（或一次拉更大 N）才可能過 0.05——**仍須**防答池污染；且過門≠自動合主表。  
- **E／hold-#1**；熱路徑未讀影。

## 下一刀候選

```text
KH8-DISCRIM-A1-T2-shadow-S1b-go | N=12000 | no-main-swap
# 或 S2 全 T2 影子（高成本；另授）
```

*完。*
