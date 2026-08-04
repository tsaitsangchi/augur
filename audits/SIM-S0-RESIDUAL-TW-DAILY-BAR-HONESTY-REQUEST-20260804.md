# 呈請：`tw.daily_bar`／binding 75 honesty＋REGISTRY-GO（2026-08-04）

> **位階**：[I] 呈裁卡（非發證、非 [N]）。  
> **殘差授權已有**：`SIM-S0-RESIDUAL: tw.daily_bar authoritative-binding | GATE-keep | no-SIM-apply`  
> **DRY**：`audits/SIM-S0-RESIDUAL-TW-DAILY-BAR-DRY-SQL-20260804.md`  
> **主 audit**：`audits/SIM-S0-RESIDUAL-TW-DAILY-BAR-20260804.md`

## 建議裁示（原文形；AI 不代勾）

```text
REGISTRY-GO: binding=75 + honesty=75 + decided_by=hugo
```

（可選併裁：Annex F §7 Q1／Q6——adj 消費者合法載體、`category` 維持 `event` 或改 `state`；**不**併則沿 seed：`event`＋權威 75。）

## 意義邊界（發證後）

| 是 | 否 |
|---|---|
| `SET LOCAL augur.honesty_write='on'` 於 **75** 親簽窗合法 | 擴及其他 Annex F 未採認概念（ex_div／fx／roster／calendar／delisting） |
| 得依 DRY 將 `tw.daily_bar.authoritative_binding_id` → **75** | 改指 **81**（Adj／derived）除非另句明示 |
| `decided_by=hugo` 由人親打 | AI 代填；殘差句本身＝COMMIT |

## 現況

- ✅ **已發證**（`audits/U0-75-HONESTY-ISSUED-20260804.md`）· ✅ **已 COMMIT**（`audits/U0-75-REGISTRY-EXECUTED-20260804.md`；`decided_at=2026-08-04 13:37:44+08`）  
- 權威＝**75** `TaiwanStockPrice`；通行證 **已消費**  
