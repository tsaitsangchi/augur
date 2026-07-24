# PME 閘診斷帳 [I]（2026-07-24）

* run_id=6 · as_of=2026-07-24T13:22:53Z · 唯讀 · FZ-keep／GATE-keep
* coverage_tallies={'mapped': 35, 'blocked_div': 1, 'missing': 3}
* gate_cross={'FAIL×FAIL': 21, 'FAIL×PASS': 13, 'PASS×PASS': 2, 'SKIP×SKIP': 6}
* unmapped_in_fv n=1
* econ_only_features=['cycle_position_252d', 'days_since_high_252d', 'institutional_net_buy_ratio_20d', 'range_position_120d']
* missing_buildability={'macro_regime': 'blocked_fz', 'peg_ratio': 'deferred_growth', 'piotroski_fscore': 'deferred_complex'}

## 邊界

- ≠可交易／≠確立級；本檔不跑閘、不降閾、不手改 validated_*
- blocked_div／Dividend 另帳；macro_regime＝blocked_fz

## Coverage（map 特徵級）

| feature | class | maps | in_fv | buildability |
|---|---|---|---|---|
| `cycle_position_252d` | mapped | 2 | True | n/a |
| `days_since_high_252d` | mapped | 4 | True | n/a |
| `debt_ratio` | mapped | 1 | True | db_buildable |
| `dividend_yield` | blocked_div | 1 | True | unknown |
| `dollar_volume_log_20d` | mapped | 1 | True | n/a |
| `foreign_holding_pct` | mapped | 2 | True | n/a |
| `gov_bank_net_buy_60d` | mapped | 1 | True | n/a |
| `gross_margin_pctile` | mapped | 2 | True | n/a |
| `inst_cumflow_position_120d` | mapped | 1 | True | n/a |
| `inst_cumflow_position_60d` | mapped | 1 | True | n/a |
| `institutional_net_buy_ratio_20d` | mapped | 4 | True | n/a |
| `lending_fee_rate_mean_30d` | mapped | 1 | True | n/a |
| `macro_regime` | missing | 1 | False | blocked_fz |
| `market_cap_log` | mapped | 1 | True | n/a |
| `momentum_120d` | mapped | 3 | True | n/a |
| `momentum_20d` | mapped | 1 | True | n/a |
| `momentum_252d` | mapped | 1 | True | n/a |
| `momentum_5d` | mapped | 1 | True | n/a |
| `momentum_60d` | mapped | 4 | True | n/a |
| `monthly_revenue_yoy` | mapped | 2 | True | n/a |
| `pb_ratio` | mapped | 1 | True | n/a |
| `pe_ratio` | mapped | 2 | True | n/a |
| `peg_ratio` | missing | 1 | False | deferred_growth |
| `piotroski_fscore` | missing | 1 | False | deferred_complex |
| `price_to_10yr` | mapped | 1 | True | n/a |
| `price_to_252d_high` | mapped | 1 | True | n/a |
| `range_mean_20d` | mapped | 1 | True | n/a |
| `range_position_120d` | mapped | 3 | True | n/a |
| `return_1d` | mapped | 1 | True | n/a |
| `roe` | mapped | 1 | True | db_buildable |
| `sbl_short_balance_log` | mapped | 1 | True | n/a |
| `top_holders_pct` | mapped | 1 | True | n/a |
| `turnover_mean_20d` | mapped | 1 | True | n/a |
| `volatility_60d` | mapped | 2 | True | n/a |
| `volume_gini_20d` | mapped | 1 | True | n/a |
| `volume_gini_60d` | mapped | 1 | True | n/a |
| `volume_max_share_20d` | mapped | 1 | True | n/a |
| `volume_max_share_60d` | mapped | 1 | True | n/a |
| `volume_surge_5_60` | mapped | 1 | True | n/a |

## Unmapped-in-fv（S1 主彈藥）

- `margin_usage_ratio`

## ECON-only 特徵（禁 APPLY）

- `cycle_position_252d`
- `days_since_high_252d`
- `institutional_net_buy_ratio_20d`
- `range_position_120d`
