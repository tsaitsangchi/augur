---
status: executed
series: c1_arc_b
go:
  - audits/LOOP-S2-TO-S1-EXPAND-GO-20260805.md
  - audits/S1-TRI-DIM-SYNC-narrow-GO-20260805.md
gap_list: audits/S1-RAW-GAP-FROM-S2-20260805.md
self_reported: true
---

# EXECUTED｜LOOP-S2-TO-S1-EXPAND（＋TRI 窄窗）· 2026-08-05

> **GO**：`LOOP-S2-TO-S1-EXPAND-go`（adopt_go）＋補句 `S1-TRI-DIM-SYNC-narrow-go`  
> **範圍**：gap list §2 P0–P1；TRI 僅 `TaiwanStockTotalReturnIndex`  
> **self-reported（#32a）**。

---

## 執行摘要

| 步 | 指令／動作 | 結果 |
|---|---|---|
| P0 MACRO | `sync_macro.py --no-catalog` | **RC=0**；31 series → `fred_series`；**344,897** 列落地；`max(date)=2026-08-04` |
| P0 DIR（初） | `derive_market_iv --until 2026-08-04` | **RC=0**；383 交易日 |
| P0 DIR（初） | `build_market_direction_features --until 2026-08-04` | **RC=0** 但 **mdf.max 仍 07-31**——根因 **TRI 日曆滯後** |
| TRI 窄窗 | `daily_maintenance --datasets TaiwanStockTotalReturnIndex --with-dim-sync --end 2026-08-04` | **RC=0**；by-dim-id（TAIEX／TPEx）；TRI max→**2026-08-04** |
| P0 DIR（閉） | 重跑 `build_market_direction_features --since 2025-01-01 --until 2026-08-04` | **RC=0**；7653 列；**mdf.max=2026-08-04** |
| P1 PX／CHIP | 唯讀 | PriceAdj／Inst／Margin／Lending max＝**2026-08-04**（無需 heal） |
| P1 Info | 唯讀 | `TaiwanStockInfo` **4300／4300** 有 `industry_category`；IndustryChain **51124** |

### 誠實殘差

| 項 | 狀態 |
|---|---|
| `market_direction_feature`＠08-04 | **19** features（他日 20）——當日缺 1 欄（lag1／源遲到類）；**不**假綠補洞 |
| RG-MACRO-XSEC-05／SEQ／GRAPH／DIV | **still-gap／另帳**（本 GO 排除） |
| 其他 by-dim-id 表 | **未**開；僅 TRI |

---

## Gap 回寫

| gap_id | 結果 |
|---|---|
| RG-DIR-PIT-03 | **closed**（經 TRI 窄窗＋mdf rebuild） |
| RG-MACRO-SER-04 | **closed**（fred_series 至 08-04；股級 macro 特徵仍 SKIP） |
| RG-PX-COV-01／RG-CHIP-COV-02 | **closed**（本窗已對齊 D） |
| RG-XSEC-INFO-06 | **稽核 done**；晉升仍另句 |
| RG-MACRO-XSEC-05／07／08／09／10 | **unchanged**（排除集） |

---

## 不做（已守）

- 全量 `AUGUR_DIM_SYNC`／無過濾 `--with-dim-sync`  
- Dividend／dim-sync 其他表／S3 feature build／NF-pause 解凍／sim `--apply`

*完。C1 Arc B EXPAND 本輪收口。*
