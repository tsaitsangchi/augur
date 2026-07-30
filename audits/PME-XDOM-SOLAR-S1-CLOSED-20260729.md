# PME-XDOM-SOLAR S1 CLOSED [I]（2026-07-29）

* Steward 拍板：`PME-XDOM-SOLAR-S1`＋`GATE-keep`＋`FZ-keep`（`audits/NET8-WAVE-APPROVED-20260729.md`）
* S0：`reports/augur_pme_xdom_solar_s0_20260729.md`（H1–H6；桶 A 14 features）
* 性質：[I]；**不**創設 [N]；**未**跑 S3／S4；**≠**可交易／≠確立級；**≠**解凍

## 做了什麼

| 階段 | 狀態 | 摘要 |
|---|---|---|
| **S0** | ✅ 已 CLOSED | `audits/PME-XDOM-SOLAR-S0-CLOSED-20260729.md` |
| **S1** | ✅ | `scripts/curate_pme_xdom_solar_map.py --apply`；selftest 全綠；冪等再跑 maps_new=0 |
| **S2** | ⏸ | 缺特徵（桶 B：inventory_turnover／capex 等）——未建；FZ-keep |
| **S3／S4** | ❌ 未跑 | 待另令（GATE-keep） |

## 數字（DB 親驗 2026-07-29）

| 項 | 值 |
|---|---|
| **school_id** | **160** |
| school name | `solar_supply_invest` |
| domain | `investment` |
| principles 新增 | **6**（H1–H6） |
| factor maps 新增 | **15**（`provenance.xdom_loop=solar`） |
| sources 新增 | 3（ITRPV／Fraunhofer ISE／BNEF） |
| domain_notes | 0（本輪無跨域注記） |
| `principle_factor_map` 全表 | 89 + 15 = **104** |

### 新 map 特徵（14 distinct）

`gross_margin_pctile`／`range_mean_20d`／`volatility_60d`／`monthly_revenue_yoy`／`momentum_60d`／`debt_ratio`／`pe_ratio`／`pb_ratio`／`institutional_net_buy_ratio_20d`／`foreign_holding_pct`／`roe`／`range_position_120d`／`days_since_high_252d`／`momentum_20d`

## 硬邊界核對

| 碼 | 本輪 |
|---|---|
| `GATE-keep` | ✅ 未跑閘、未降閾、未手改舊 validated_* |
| `FZ-keep` | ✅ 零 FinMind／FRED |
| 禁 AI 造原則 | ✅ source_type≠ai_generated；selftest 鎖 |
| 拒 SEED 清單 | ✅ erp／rki／embedding／slurry／turnover 名衝突／ai_predict 混軸 |
| ≠自動下單／≠可交易 | ✅ |
| ZERO local-gates | ✅ |
| ZERO APPLY（閘） | ✅（此 APPLY 為策展 INSERT；非 G-PROM APPLY） |

## 下一步（人）

- S3（local-gates）另令；雙綠∧kill clear 才 APPLY prodset。
- S2 桶 B 缺特徵另估（FZ-keep；零 API 可建與否待議）。
