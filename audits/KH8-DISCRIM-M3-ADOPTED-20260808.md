---
status: adopted
series: local_ai_kh
kind: kh8_merge_m3
date: 2026-08-08
viewpoint: 2026-08-08T21:45+08:00
plan: reports/augur_kh8_discrim_merge_adjudication_go_plan_20260808.md
register: audits/KH8-DISCRIM-MERGE-ADJUDICATION-PLAN-REGISTER-20260808.md
paste: "KH8-DISCRIM-M3-adopt | merge-with-pool-gate | no-merge-yet | E-keep | hold-#1"
choice: M3
self_reported: true
layer: "[I]"
---

# ADOPTED｜KH8-DISCRIM · M3 · 2026-08-08

Steward 選 **M3：准合併方向＝全量／標題權重可入主表路徑，但必須答池闸**。

## 採納條款

1. **方向**：允許未來將 T2 影列（诚实低分）併入主 `knowhow_evidence_weight`，使**生产** disc 可轉綠。  
2. **硬前置（缺一不可，施作 GO 再驗）**：  
   - retrieve／readout／AUTO-LIFT **不得**僅憑 weight 命中無全文標題件；  
   - 合并双明示 paste＋rollback；  
   - 錨題／有文回归；  
   - **E**：生产 disc 綠且闸过前，仍 **stop-at-7**。  
3. **本裁≠施作**：**此刻不 MERGE**；影子表可保留作预览。  
4. **禁裸 M2**（无闸合并）。  
5. **hold-#1** 不讓；合并窗口让日更。

```text
KH8-DISCRIM-M3-adopt | merge-with-pool-gate | no-merge-yet | E-keep | hold-#1
# 下一刀候選（另授）:
KH8-DISCRIM-M3-pool-gate-go | code-gate | no-merge
KH8-DISCRIM-merge-M3-go | dual-explicit | after-gate-green
```

*完。adopted（方向）；未合併。*
