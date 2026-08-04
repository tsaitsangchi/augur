# W2 65 無概念通道唯讀 triage（2026-08-04）

> **位階**：[I] 執行報告（非治權 [N]）。**授權**：Steward 甲案 `OPT-P0-20260804-go + TRIAGE-65-go + FZ/GATE/NHC-keep`。
> **紀律**：零 `world_concept` INSERT；零假 mapped；不解凍 FinMind／FRED。
> **寫入**：2026-08-04T09:42:52+08:00

## 0. 複核指令

```bash
cd /home/hugo/project/augur && set -a && . ./.env && set +a
venv/bin/python scripts/reconcile_channel_columns.py --survey
# 概念覆蓋（mapped / 草案殘 / 無概念）＝下節 SQL
```

```sql
-- 母體 98；草案 binding 集合見 reports/wm_channel_registration_draft_20260803.md §4
SELECT count(*) FILTER (WHERE concept_key IS NOT NULL) AS mapped,
       count(*) FILTER (WHERE concept_key IS NULL) AS unmapped,
       count(*) AS total
FROM world_channel_binding WHERE superseded_at IS NULL;
```

## 1. 現查覆蓋

| 項 | 值 |
|---|---:|
| 現行通道總數 | 98 |
| mapped（有 concept_key） | 13 |
| unmapped | 85 |
| 其中：草案殘（仍 unmapped） | 20 |
| 其中：**完全無概念（本 triage 母體）** | **65** |
| source_column 非空 | 3 |

草案殘 binding_id（20）：`17, 23, 30, 35, 38, 43, 44, 49, 51, 53, 56, 60, 68, 69, 70, 77, 78, 83, 85, 86`

## 2. 分流計數（計畫四欄；分類覆蓋 65/65）

| 分流 | 筆數 | 子桶 |
|---|---:|---|
| 已被草案／mapped 消費 | **0** | 見下 |
| B0/infra 緩登 | **13** | 見下 |
| 需新概念卡 | **44** | 見下 |
| out_of_scope 候補 | **8** | 見下 |
| **合計** | **65** | ＝65 |

### 2.1 子桶明細

| 子桶 | 筆數 |
|---|---:|
| `out_候補` | 8 |
| `緩_B0` | 11 |
| `緩_infra` | 2 |
| `需新卡` | 37 |
| `需新卡_U0抽樣` | 6 |
| `需新卡_熱路徑` | 1 |

## 3. 逐通道表

### 緩_B0（11）

| binding_id | source_table | vendor 熱路徑 | note |
|---:|---|:---:|---|
| 11 | `TaiwanFuturesTick` |  | B0 無實體表；緩登（W2-2）；禁造假 concept |
| 16 | `TaiwanVariousIndicators5Seconds` |  | B0 無實體表；緩登（W2-2）；禁造假 concept |
| 24 | `TaiwanStockKBar` |  | B0 無實體表；緩登（W2-2）；禁造假 concept |
| 26 | `USStockPriceMinute` |  | B0 無實體表；緩登（W2-2）；禁造假 concept |
| 27 | `TaiwanOptionTick` |  | B0 無實體表；緩登（W2-2）；禁造假 concept |
| 42 | `TaiwanStockBlockTradingDailyReport` |  | B0 無實體表；緩登（W2-2）；禁造假 concept |
| 45 | `TaiwanStockPriceTick` |  | B0 無實體表；緩登（W2-2）；禁造假 concept |
| 59 | `TaiwanStockWarrantTradingDailyReport` |  | B0 無實體表；緩登（W2-2）；禁造假 concept |
| 61 | `TaiwanStockEvery5SecondsIndex` |  | B0 無實體表；緩登（W2-2）；禁造假 concept |
| 76 | `TaiwanStockTradingDailyReport` |  | B0 無實體表；緩登（W2-2）；禁造假 concept |
| 94 | `TaiwanStockStatisticsOfOrderBookAndTrade` |  | B0 無實體表；緩登（W2-2）；禁造假 concept |

### 緩_infra（2）

| binding_id | source_table | vendor 熱路徑 | note |
|---:|---|:---:|---|
| 88 | `data_audit_log` |  | infra log；非世界觀測；緩登另裁 |
| 89 | `pipeline_execution_log` |  | infra log；非世界觀測；緩登另裁 |

### 需新卡_熱路徑（1）

| binding_id | source_table | vendor 熱路徑 | note |
|---:|---|:---:|---|
| 39 | `TaiwanStockBlockTrade` | Y | vendor 直綁基線仍消費＝P1 優先概念卡 |

### 需新卡_U0抽樣（6）

| binding_id | source_table | vendor 熱路徑 | note |
|---:|---|:---:|---|
| 7 | `TaiwanStockConvertibleBondInfo` |  | 解阻／抽樣已提方向；待概念卡＋人裁 |
| 37 | `JapanStockPrice` |  | 解阻／抽樣已提方向；待概念卡＋人裁 |
| 50 | `GoldPrice` |  | 解阻／抽樣已提方向；待概念卡＋人裁 |
| 65 | `TaiwanOptionInstitutionalInvestorsAfterHours` |  | 解阻／抽樣已提方向；待概念卡＋人裁 |
| 80 | `TaiwanStockSplitPrice` |  | 解阻／抽樣已提方向；待概念卡＋人裁 |
| 97 | `TaiwanFuturesDaily` |  | 解阻／抽樣已提方向；待概念卡＋人裁 |

### 需新卡（37）

| binding_id | source_table | vendor 熱路徑 | note |
|---:|---|:---:|---|
| 1 | `TaiwanStockInstitutionalInvestorsBuySellWide` |  | 無草案、非 B0/infra；P3/P4 提案或後標 out |
| 5 | `TaiwanOptionInstitutionalInvestors` |  | 無草案、非 B0/infra；P3/P4 提案或後標 out |
| 6 | `TaiwanStockMarketValueWeight` |  | 無草案、非 B0/infra；P3/P4 提案或後標 out |
| 8 | `TaiwanFutOptDailyInfo` |  | 無草案、非 B0/infra；P3/P4 提案或後標 out |
| 9 | `USStockPrice` |  | 無草案、非 B0/infra；P3/P4 提案或後標 out |
| 10 | `TaiwanFutOptTickInfo` |  | 無草案、非 B0/infra；P3/P4 提案或後標 out |
| 13 | `TaiwanFuturesDealerTradingVolumeDaily` |  | 無草案、非 B0/infra；P3/P4 提案或後標 out |
| 15 | `TaiwanOptionFinalSettlementPrice` |  | 無草案、非 B0/infra；P3/P4 提案或後標 out |
| 18 | `TaiwanFuturesInstitutionalInvestorsAfterHours` |  | 無草案、非 B0/infra；P3/P4 提案或後標 out |
| 19 | `TaiwanStockMarginShortSaleSuspension` |  | 無草案、非 B0/infra；P3/P4 提案或後標 out |
| 20 | `TaiwanStockDispositionSecuritiesPeriod` |  | 無草案、非 B0/infra；P3/P4 提案或後標 out |
| 21 | `TaiwanStockWeekPrice` |  | 無草案、非 B0/infra；P3/P4 提案或後標 out |
| 29 | `EuropeStockPrice` |  | 無草案、非 B0/infra；P3/P4 提案或後標 out |
| 34 | `TaiwanStockSuspended` |  | 無草案、非 B0/infra；P3/P4 提案或後標 out |
| 40 | `TaiwanStockLoanCollateralBalance` |  | 無草案、非 B0/infra；P3/P4 提案或後標 out |
| 41 | `TaiwanStockConvertibleBondInstitutionalInvestors` |  | 無草案、非 B0/infra；P3/P4 提案或後標 out |
| 46 | `TaiwanStockParValueChange` |  | 無草案、非 B0/infra；P3/P4 提案或後標 out |
| 47 | `TaiwanStockMonthPrice` |  | 無草案、非 B0/infra；P3/P4 提案或後標 out |
| 52 | `TaiwanFutOptInstitutionalInvestors` |  | 無草案、非 B0/infra；P3/P4 提案或後標 out |
| 54 | `TaiwanFuturesFinalSettlementPrice` |  | 無草案、非 B0/infra；P3/P4 提案或後標 out |
| 55 | `TaiwanStockDayTradingBorrowingFeeRate` |  | 無草案、非 B0/infra；P3/P4 提案或後標 out |
| 57 | `TaiwanStockPriceLimit` |  | 無草案、非 B0/infra；P3/P4 提案或後標 out |
| 63 | `TaiwanStockIndustryChain` |  | 無草案、非 B0/infra；P3/P4 提案或後標 out |
| 64 | `UKStockPrice` |  | 無草案、非 B0/infra；P3/P4 提案或後標 out |
| 66 | `ExchangeRate` |  | 無草案、非 B0/infra；P3/P4 提案或後標 out |
| 71 | `InterestRate` |  | 無草案、非 B0/infra；P3/P4 提案或後標 out |
| 72 | `GovernmentBondsYield` |  | 無草案、非 B0/infra；P3/P4 提案或後標 out |
| 73 | `TaiwanFuturesSpreadTrading` |  | 無草案、非 B0/infra；P3/P4 提案或後標 out |
| 74 | `CrudeOilPrices` |  | 無草案、非 B0/infra；P3/P4 提案或後標 out |
| 79 | `TaiwanStockConvertibleBondDaily` |  | 無草案、非 B0/infra；P3/P4 提案或後標 out |
| 82 | `TaiwanOptionOpenInterestLargeTraders` |  | 無草案、非 B0/infra；P3/P4 提案或後標 out |
| 87 | `TaiwanStockDayTradingSuspension` |  | 無草案、非 B0/infra；P3/P4 提案或後標 out |
| 90 | `TaiwanStockConvertibleBondDailyOverview` |  | 無草案、非 B0/infra；P3/P4 提案或後標 out |
| 92 | `TaiwanOptionDealerTradingVolumeDaily` |  | 無草案、非 B0/infra；P3/P4 提案或後標 out |
| 95 | `TaiwanFuturesSpreadTick` |  | 無草案、非 B0/infra；P3/P4 提案或後標 out |
| 96 | `TaiwanStockCashFlowsStatement` |  | 無草案、非 B0/infra；P3/P4 提案或後標 out |
| 98 | `TaiwanStockCapitalReductionReferencePrice` |  | 無草案、非 B0/infra；P3/P4 提案或後標 out |

### out_候補（8）

| binding_id | source_table | vendor 熱路徑 | note |
|---:|---|:---:|---|
| 14 | `EuropeStockInfo` |  | 名冊／新聞／摘要類；候補 out_of_scope（須人裁，非自動踢出） |
| 22 | `JapanStockInfo` |  | 名冊／新聞／摘要類；候補 out_of_scope（須人裁，非自動踢出） |
| 33 | `TaiwanStockInfoWithWarrantSummary` |  | 名冊／新聞／摘要類；候補 out_of_scope（須人裁，非自動踢出） |
| 36 | `USStockInfo` |  | 名冊／新聞／摘要類；候補 out_of_scope（須人裁，非自動踢出） |
| 58 | `TaiwanStockInfoWithWarrant` |  | 名冊／新聞／摘要類；候補 out_of_scope（須人裁，非自動踢出） |
| 67 | `TaiwanSecuritiesTraderInfo` |  | 名冊／新聞／摘要類；候補 out_of_scope（須人裁，非自動踢出） |
| 84 | `TaiwanStockNews` |  | 名冊／新聞／摘要類；候補 out_of_scope（須人裁，非自動踢出） |
| 91 | `UKStockInfo` |  | 名冊／新聞／摘要類；候補 out_of_scope（須人裁，非自動踢出） |

## 4. 下一步建議（不自動 APPLY）

1. **緩登 13**（B0×11＋infra×2）：維持不進概念優先佇列；W2-2／infra 去留另裁。
2. **熱路徑 1**：`binding_id=39` `TaiwanStockBlockTrade`——優先概念卡（基線仍直綁）。
3. **U0 抽樣 6**：延續解阻概念卡形制（7／37／50／65／80／97），**親簽＋honesty 證**才寫庫。
4. **其餘需新卡**：按 P3（用量）→P4；**禁**為覆蓋率灌空殼 concept。
5. **out 候補 8**：Steward 一句確認是否踢出分母（K1），或改回需新卡。
6. **草案殘 20**：不在本 65 內；dry／親簽另刀（P0-C），本報告不碰。

## 5. 未做／硬禁

- 未 INSERT／UPDATE `world_concept`／`world_channel_binding`
- 未 `--allow-apply`、未搶 `heavy_slot`、未打 FinMind／FRED
- 分類 ≠ WM.36 完成；mapped 仍為 13／98

