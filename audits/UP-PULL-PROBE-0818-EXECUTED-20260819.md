---
status: executed
series: s4_s5_verify
track: UP-PULL
date: 2026-08-19
viewpoint: 2026-08-19T08:40+08:00
asof: "2026-08-18"
shell: scripts/probe_uptrend_pullback.py
json: /tmp/up-pull-2026-08-18-strict.json
paste: "UP-PULL-probe-go | date=2026-08-18 | side=both | k=10 | policy=strict"
selftest: green
n_long: 5
n_short: 2
policy: strict
version: UP-PULL-v1
self_reported: true
layer: "[I]"
---

# EXECUTED｜UP-PULL 探針＠2026-08-18 · both · strict · k=10

Steward 08:32 明示 GO。零寫 `prediction_values`。未 promote。未改 standing 20,60。`--date 2026-08-19` → rc=3。

## 答（誠實）

- as-of＝**2026-08-18**＝價頂；`check_asof_ready` ready。08-19＝假 B3。
- **strict**：做多 **5**／k=10；做空 **2**／k=10。不足不補。`n_long_lt_k`／`n_short_lt_k`＝true。
- 路徑％＝已發生還原價，**不是**未來漲跌幅。做空 **≠** 可融券可成交。
- 排序＝`mean(H60,H120,H240)`，**不用** RankRidge score。同 5＋2 檔與預診；做多序因主鍵改為三窗均勻，**微星**升到第 2。

## 漏斗（核心＠08-18）

| | 宇宙 | 八窗齊 | A | B | C | 過齊 |
|---|---|---|---|---|---|---|
| 做多 | 286 | 284 | 47 | 7 | 5 | **5** |
| 做空 | 286 | 284 | 30 | 5 | 2 | **2** |

## 做多（已發生路徑％）

| # | 代號 | 名稱 | 距20日高 | H5 | H10 | H60 | H120 | H240 |
|---|---|---|---|---|---|---|---|---|
| 1 | 3231 | 緯創 | −8.1% | −5.2% | −7.2% | +29.9% | +44.9% | +65.3% |
| 2 | 2377 | 微星 | −12.4% | −3.9% | −1.0% | +19.4% | +59.8% | +9.3% |
| 3 | 2006 | 東和鋼鐵 | −8.7% | −5.5% | −2.1% | +23.4% | +19.0% | +35.0% |
| 4 | 1907 | 永豐餘 | −5.0% | −3.1% | −0.7% | +24.3% | +17.4% | +21.1% |
| 5 | 3293 | 鈊象 | −7.7% | −7.7% | −4.1% | +4.1% | +14.3% | +0.2% |

## 做空（條件排序；≠可空）

| # | 代號 | 名稱 | 距20日低 | H5 | H10 | H60 | H120 | H240 |
|---|---|---|---|---|---|---|---|---|
| 1 | 1215 | 卜蜂 | +6.8% | +0.9% | +6.3% | −19.1% | −22.1% | −15.3% |
| 2 | 8099 | 大世科 | +7.1% | +2.6% | +5.9% | −1.0% | −14.0% | −6.7% |

## 殼

| 檔 | 角色 |
|---|---|
| `src/augur/evaluation/uptrend_pullback.py` | v1 四閘／排序／strict 截 k；`--selftest` 綠 |
| `scripts/probe_uptrend_pullback.py` | 唯讀 CLI；假 B3 rc=3；soft-fill 拒 rc=2 |

自測：library rc=0；CLI rc=0。探針 rc=0。假 B3＠08-19 rc=3。

## 不做（本槍未開）

P1b soft-fill；P2 OOS walk；P3 PullbackLS；P4 emit；改 standing；當可交易。
