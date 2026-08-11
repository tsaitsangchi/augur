---
status: executed
series: cycle
kind: fred_macro_heal
date: 2026-08-08
viewpoint: 2026-08-08T13:10+08:00
go: audits/FRED-MACRO-HEAL-GO-20260808.md
log: /tmp/fred-macro-heal-20260808.log
paste: "FRED-MACRO-HEAL-go | tip=2026-08-07 | FZ/GATE-keep | no-SIM-apply"
self_reported: true
layer: "[I]"
---

# EXECUTED｜FRED-MACRO-HEAL · 2026-08-08

```text
FRED-MACRO-HEAL-go | tip=2026-08-07 | FZ/GATE-keep | no-SIM-apply
```

## 跑

`python scripts/sync_macro.py --no-catalog` → **31** series · **344,957** 列落地。

## 對 tip＝2026-08-07

| 指標 | 值 |
|---|---|
| `fred_series` global max | **2026-08-07**（前＝08-06） |
| rows＠08-07 | **6** |
| rows＠08-06 | 15 |
| `T10Y2Y`／`NASDAQCOM` tip | **08-07** |
| `VIXCLS`／`DGS10`／`DFF` tip | 仍 **08-06**（發布／休市延遲；非假填） |
| `DEXTAUS` | **07-31**（FRED 匯率延遲；誠實） |
| Tier B `UNRATE`／`CPI` | 月頻 · 各自 vintage max（預期） |

## 判讀（Cycle-3 RG-MACRO）

- **抬升成立**：global max 達 tip。  
- **≠ 全檔齊 tip**：關鍵日頻（VIX／DGS）仍 lag 1 → 仍可標 **partial／improved**，禁塗「全齊」。  
- 未 SIM-apply；未改 prodset。

*完。[I]*
