---
status: contract_accepted
series: s3_macro_stock
go: audits/S3-MACRO-STOCK-CONTRACT-v2-GO-20260805.md
pack: P1
supersedes_build: audits/S3-MACRO-STOCK-BUILD-EXECUTED-20260805.md
date: 2026-08-05
layer: "[I]"
self_reported: true
---

# CONTRACT-v2｜股級 macro P1（相對化）· 2026-08-05

> **套餐 P1**：截面／產業相對化後再×macro（回應 v1「裸播乘」IC≈0）。  
> **零 build** 至 `S3-MACRO-STOCK-BUILD-v2-go`。  
> **不退役** v1 三名（staged 保留）；本輪只**加**新名。

---

## 1. 凍結三名

| # | feature | 定義 |
|---|---|---|
| **A** | `z_mom20_x_vix` | 同 panel：橫斷面 z(`momentum_20d`)（≥3 股、母體 std；零變異→該 panel 全缺）× `macro_vintage.as_of(VIXCLS, panel)` |
| **B** | `z_mom20_x_t10y2y_chg` | 同 panel z(`momentum_20d`) × (T10Y2Y as-of panel − as-of 前一 `feature_values` panel)；首 panel／缺 T10→缺列 |
| **C** | `ind_demean_mom20_x_vix` | (`momentum_20d` − 同 panel 同 `industry_category` 中位) × VIX as-of；無產業或缺產業同伴→缺列 |

**原料**：`feature_values.momentum_20d`；`TaiwanStockInfo.industry_category`；PIT＝`macro_vintage` only。  
**宇宙／頻率**：`core_universe_asof`＠panel（無則 fallback `core_universe`）；月頻 panel。  
**落表**：`feature_candidate_values`；禁 `feature_values`／prodset／Tier-B／#11（除非另 VERIFY GO 且 HAC\|t\|≥2）。

---

## 2. 相對化細節

| 運算 | 規則 |
|---|---|
| z | 同 panel 核心宇宙內；N&lt;3 或 sd=0 → 不寫 A／B |
| 產業 demean | 同 `industry_category`；該產業 N&lt;2 → 該股缺列 |
| 缺 mom20 | 該股不進任何名 |

---

## 3. 驗收（BUILD-v2）

- 三名材料化＋覆蓋／缺列率  
- pan-hist＋as-of IC H20／H60；與 v1 分表對照  
- \|HAC\|≥2 之異質名才得另 `VERIFY-v2`  
- v1 三名**不**重算除非明示  

## 4. Next paste

```text
S3-MACRO-STOCK-BUILD-v2-go | FZ/GATE-keep | skip-sync | no-SIM-apply
# implements CONTRACT-v2 P1 three names; candidates only
```

*完。*
