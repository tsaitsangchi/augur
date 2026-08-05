---
status: accepted
series: s3_macro_stock
date: 2026-08-05
layer: "[I]"
depends_on:
  - audits/S3-MACRO-STOCK-VERIFY-v2-P2-EXECUTED-20260805.md
  - reports/augur_s3_n3_xsec_macro_dual_track_plan_20260805.md
self_reported: true
---

# ACCEPT｜軌 M 停（MACRO-STOCK KEEP）· 2026-08-05

> **授權**：Steward AskQuestion `heavy` → **`m_stop`**（開問題「1＋2」重刀）  
> paste：

```text
S3-MACRO-STOCK-M-STOP-ack | FZ/GATE-keep | no-build | no-verify | no-prodset
# keep staged (incl. z_vol60_x_vix_chg); pause track M research
```

## 1. 為何停

| 事實 | 帳 |
|---|---|
| P2 VERIFY | as-of HAC≈1.98；ridge/gbdt **Δ 微負** → **keep_staged** |
| 增量不成立 | 單因子弱訊號≠生產集增量 |
| 日更優先 | B1／B3 已通；CPU／注意力給收盤鏈 |

## 2. 生效

| 是 | 否 |
|---|---|
| 軌 M **研究暫停**；staged 列保留 | 清候選、prodset、重跑同一 `#11` |
| xsec／β5_stop **仍凍結**（正交） | 默授 CONTRACT-v3 |
| 可隨時另句重開 | 本 ack＝永久判死科學結論 |

## 3. 重開要件（另句）

```text
S3-MACRO-STOCK-CONTRACT-v3-go | FZ/GATE-keep | skip-sync | no-SIM-apply
# ≤3 新名；須新假說（非重跑 z_vol60_x_vix_chg 同尺）
```

*完。self-reported（#32a）。*
