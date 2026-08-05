---
status: executed
series: s3_macro_stock
go: audits/S3-MACRO-STOCK-BUILD-v2-GO-20260805.md
contract: audits/S3-MACRO-STOCK-CONTRACT-v2-20260805.md
self_reported: true
---

# EXECUTED｜S3-MACRO-STOCK-BUILD-v2（P1）· 2026-08-05

> **GO**：`S3-MACRO-STOCK-BUILD-v2-go | FZ/GATE-keep | skip-sync | no-SIM-apply`  
> **pack**：P1＝`z_mom20_x_vix`／`z_mom20_x_t10y2y_chg`／`ind_demean_mom20_x_vix`  
> **self-reported（#32a）**；log＝`/tmp/macro_stock_v2.log`

---

## 1. 材料化

| feature | n | panel 窗 | stocks |
|---|---:|---|---:|
| `z_mom20_x_vix` | **36,805** | 2014-12-31→2026-08-04 | 760 |
| `z_mom20_x_t10y2y_chg` | **36,104** | 2015-12-31→2026-08-04 | 684 |
| `ind_demean_mom20_x_vix` | **36,419** | 2014-12-31→2026-08-04 | 756 |
| **合計** | **109,328** | | |

v1 三名 **未刪**（staged 保留）。零 prodset／零 `#11`。

---

## 2. IC

### pan-hist

| feature | H20 IC／HAC-t | H60 IC／HAC-t |
|---|---|---|
| `z_mom20_x_vix` | −0.0219／−1.37 | +0.0050／+0.33 |
| `z_mom20_x_t10y2y_chg` | −0.0061／−0.42 | −0.0029／−0.26 |
| `ind_demean_mom20_x_vix` | −0.0158／−1.25 | +0.0070／+0.60 |

### as-of

| feature | H20 IC／HAC-t | H60 IC／HAC-t |
|---|---|---|
| `z_mom20_x_vix` | −0.0244／−**1.50** | +0.0084／+0.58 |
| `z_mom20_x_t10y2y_chg` | −0.0058／−0.40 | −0.0082／−0.75 |
| `ind_demean_mom20_x_vix` | −0.0189／−**1.51** | +0.0069／+0.60 |

**判定**：無異質名 \|HAC\|≥2 → **不建議 VERIFY-v2**。相對化相對 v1 有抬升 H20 \|t\|（≈1.5 vs ≪1），仍未過門。

**註**：`z_mom20_x_t10y2y_chg` 之 rank IC 與 v1 `stock_ret20_x_t10y2y_chg` 幾乎同數——panel 內常數 macro 差之下，z(mom)×c 與 mom×c 的橫斷面排序等價（母原則③ 對「常數播乘」不增資訊）。

---

## 3. #3 狀態

| 步 | 狀態 |
|---|---|
| 契約／builder 根因 | **已閉**（v1＋v2） |
| 預測力過門 | **未立**（兩輪） |
| VERIFY／prodset | **defer** |
| 軌 X β5 | 仍停 |

*完。*
