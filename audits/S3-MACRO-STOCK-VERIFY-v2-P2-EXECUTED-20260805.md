---
status: executed
series: s3_macro_stock
go: audits/S3-MACRO-STOCK-VERIFY-v2-P2-GO-20260805.md
build: audits/S3-MACRO-STOCK-BUILD-v2-P2-EXECUTED-20260805.md
verdict: keep_staged
self_reported: true
---

# EXECUTED｜S3-MACRO-STOCK-VERIFY-v2-P2 · 2026-08-05

> **GO**：`S3-MACRO-STOCK-VERIFY-v2-P2-go`（Steward `verify_asof_near`）  
> **CLI**：`verify_candidate_promotion.py --features z_vol60_x_vix_chg --h 60 --seeds 3 --keep`  
> **log**：`/tmp/macro_stock_verify_p2.log` · RC=**0** · 約 15:14→17:12+08（~2h）  
> **裁**：Steward AskQuestion `after_v` → **`keep_staged`**（書面維持；**不** prodset）  
> **self-reported（#32a）**

---

## 1. as-of 單因子 IC（§1）

| feature | H | IC | iid-t | HAC-t | 勝率 | n |
|---|---:|---:|---:|---:|---:|---:|
| `z_vol60_x_vix_chg` | 60 | +0.0487 | 2.13 | **1.98** | 0.54 | 103 |

as-of 複核：**108** panel（2014-12-31..2026-08-04）；候選有值比較尺＝**107** panel（2015-12-31..2026-08-04）。  
as-of \|HAC-t\| **未滿 2**（貼門 1.98；與 BUILD 帳一致）。GO 明示接受「貼門仍跑」。

---

## 2. 多 seed 增量 Δ（§2｜生產基準 34 feat）

| feature | H | model | 基準 mean IC | +候選 | **Δ** |
|---|---:|---|---:|---:|---:|
| `z_vol60_x_vix_chg` | 60 | B2_ridge | +0.1602 | +0.1599 | **−0.0003** |
| `z_vol60_x_vix_chg` | 60 | M1_gbdt | +0.1476 | +0.1466 | **−0.0011** |

種子＝3（`seed=42+k`）；`--keep` → 候選表**保留**（不清）。

---

## 3. 判讀（機械）

提拔條件＝as-of \|HAC-t\|≥2 **且** 多 seed Δ **穩定為正**。  
本輪：**HAC as-of 1.98＜2**；**兩臂 Δ 皆微負** → **維持候選待強化**（非提拔）。

---

## 4. Steward 終裁

| 是 | 否 |
|---|---|
| 書面 **keep_staged**；V 閉環本刀關閉 | prodset／自動晉升 |
| staged 列保留供後續假說對照 | 解讀為「過門可交易／確立級」 |
| 下一刀另授（新 hyp CONTRACT／軌 M 停／他項） | 本帳默授 CONTRACT-v3 或 β5 解凍 |

---

## 5. 不做

prodset · 重跑同一 `#11` 當推進 · 清 staged · 開新 builder（本帳）

*完。V＝EXECUTED + keep_staged。*
