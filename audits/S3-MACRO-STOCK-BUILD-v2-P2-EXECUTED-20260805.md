---
status: executed
series: s3_macro_stock
go: audits/S3-MACRO-STOCK-CONTRACT-v2-P2-GO-20260805.md
contract: audits/S3-MACRO-STOCK-CONTRACT-v2-P2-20260805.md
self_reported: true
---

# EXECUTED｜S3-MACRO-STOCK-BUILD-v2-P2 · 2026-08-05

> **GO**：CONTRACT-v2-P2 ＋ BUILD（Steward `p2_pack`）  
> log：`/tmp/macro_stock_p2.log` · **self-reported（#32a）**

---

## 1. 材料化

| feature | n | panel 窗 |
|---|---:|---|
| `beta60_x_hyoas` | **8,982** | 2023-07-31→2026-08-04（**短窗**；HY 可見段） |
| `z_vol60_x_vix_chg` | **36,104** | 2015-12-31→2026-08-04 |
| `beta60_x_dextaus_chg` | **36,103** | 2015-12-31→2026-08-04 |
| **合計** | **81,189** | |

---

## 2. IC

| feature | pan-hist H20／H60 HAC-t | as-of H20／H60 HAC-t |
|---|---|---|
| `beta60_x_hyoas` | −0.05／**+1.05**（n≈34–36） | −0.18／+1.06 |
| `z_vol60_x_vix_chg` | +0.89／**+2.08** ✅ | +0.90／**+1.98**（貼門） |
| `beta60_x_dextaus_chg` | +1.32／−0.69 | +1.16／−1.05 |

**判定**：`z_vol60_x_vix_chg` **pan-hist H60 \|HAC\|≥2**（2.08）；as-of **1.98** 未滿 2。  
→ 可呈 **`S3-MACRO-STOCK-VERIFY-v2-P2-go`**（單名、H60、`--seeds 3 --keep`）——Steward 須明示是否接受「as-of 貼門仍跑」或要求 as-of≥2 才 VERIFY。

其餘兩名未過門；HY 臂樣本短，不當 VERIFY 主體。

---

## 3. 不做

prodset · 自動 #11 · 清 v1／P1 staged  

*完。*
