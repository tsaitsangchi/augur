---
status: draft_for_steward
series: s3_macro_stock
parent_contract: audits/S3-MACRO-STOCK-CONTRACT-20260805.md
build_result: audits/S3-MACRO-STOCK-BUILD-EXECUTED-20260805.md
date: 2026-08-05
layer: "[I]"
self_reported: true
---

# CONTRACT-v2 草案｜股級 macro 下一輪 ≤3 名（2026-08-05）

> **觸發**：M2 三名已落地但 **HAC \|t\|≪2**；broadcast 截面無變異＝對照成立。  
> **紀律**：不重跑同三名 VERIFY；不放寬門檻；新名＝新假說。  
> **本檔**：候裁選組合 —— **零 build** 至 `S3-MACRO-STOCK-CONTRACT-v2-go`。

---

## 0. 首輪失敗提示（設計用）

| 觀察 | 含義 |
|---|---|
| β×VIX、mom×利差變動 IC≈0 | 「連續播乘市場標量」增量弱 |
| VIX broadcast 無截面 IC | 對照正確；下一輪對照可改**有異質的假對照**或省略 |
| mom 取自 `momentum_20d` | 原料 OK；互動形或條件化不足 |

下一輪偏向：**截面相對化後再×macro**（母原則③）或 **異質敏感度（非水準播乘）**。

---

## 1. 候選池（請圈 ≤3）

| ID | 建議名 | 定義草案 | 為何可能優於 v1 |
|---|---|---|---|
| **A** | `z_mom20_x_vix` | 同 panel 橫斷面 z(`momentum_20d`) × VIX as-of | 相對化動能再乘 regime |
| **B** | `z_mom20_x_t10y2y_chg` | z(mom20) × T10Y2Y panel 差 | 同 v1#2 但先 z |
| **C** | `ind_demean_mom20_x_vix` | (mom20 − 產業內中位) × VIX | 產業中性×風險偏好 |
| **D** | `beta60_x_hyoas` | β60 × `BAMLH0A0HYM2` as-of | 信用壓力取代 VIX |
| **E** | `z_vol60_x_vix_chg` | z(`volatility_60d`) × (VIX_t − VIX_{prev panel}) | 波動擁擠×VIX 變化 |
| **F** | `beta60_x_dextaus_chg` | β60 × DEXTAUS panel 差（台幣） | 出口／匯率敏感 |
| **G** | `z_beta60_x_vix` | 同 panel z(β60) × VIX | β 相對化後再乘（非 raw β×VIX） |

**PIT**：仍一律 `macro_vintage`；價／特徵 ≤panel；缺列不補。  
**落表**：`feature_candidate_values`；禁 prodset／Tier-B 首輪。

---

## 2. 預組套餐（裁示用）

| 套餐 | 三名 | 定位 |
|---|---|---|
| **P1 相對化** | A + B + C | 主打母原則③（推薦若信「播乘失敗因未 z／未產業中性」） |
| **P2 壓力／匯率** | D + E + F | 換 macro 通道（HY／VIX 變化／USD-TWD） |
| **P3 混合** | A + D + G | z-mom×VIX + 信用×β + z-β×VIX |
| **P4 自揀** | 自 A–G 圈恰好 3 個 | — |

---

## 3. Paste-ready（裁後）

```text
S3-MACRO-STOCK-CONTRACT-v2-go | FZ/GATE-keep | skip-sync | no-SIM-apply
# pack=<P1|P2|P3|custom> · names=...
# then optional: S3-MACRO-STOCK-BUILD-v2-go
```

---

## 4. 請 Steward 裁示

擇套餐或自揀 3 名 → 定稿 `audits/S3-MACRO-STOCK-CONTRACT-v2-YYYYMMDD.md` → 另 BUILD GO。

*草案。*
