---
status: executed
series: s4_s5_verify
track: TREND-PB
date: 2026-08-19
viewpoint: 2026-08-19T09:00+08:00
asof: "2026-08-18"
wave: W2
shell: scripts/probe_trend_pb_catalog.py
json: /tmp/trend-pb-2026-08-18-W2.json
paste: "TREND-PB-W2-go | date=2026-08-18 | families=T03,T04,T05,T06,T08,T12,C04 | k=10"
selftest: green
self_reported: true
layer: "[I]"
---

# EXECUTED｜TREND-PB W2＠2026-08-18

Steward 08:57 明示。零寫 `prediction_values`／`feature_values`。未倒 canonical 31。未 promote。`--date 2026-08-19` → rc=3。

## 答（誠實）

- as-of＝**2026-08-18**＝價頂；scored＝284。T01 做多過閘仍＝**5**（內部對照，未列入本 paste 族）。
- **C04（20 日高）∩ T01 = 0**。listed 含光寶科、台虹、聯茂、大立光——與 W1 的「正在漲」同味道。
- **T04 做多 0 檔**（季線上且 SMA20 回撤 3%～15% 當日沒人過）；做空 29。
- T05 ∩ T01 做多＝**1**；T08＝**2**；T03／T06／T12＝0。
- T12 做多僅 **3209 全科**（上年線仍觸／跌破布林下軌，極稀）。
- SMA200 斜率＝今日 SMA200 − 昨日 SMA200。RSI＝Wilder。C04＝收盤＝近 20 日最高（含今日）。單日 ≠ OOS。

## 規模

| ID | 做多 pass／listed | 做空 pass／listed | vs T01 做多 |
|---|---|---|---|
| T03 | 18／10 | 6／6 | 0 |
| T04 | **0／0** | 29／10 | 0 |
| T05 | 42／10 | 5／5 | 1 |
| T06 | 24／10 | 3／3 | 0 |
| T08 | 96／10 | 18／10 | 2 |
| T12 | 1／1 | 1／1 | 0 |
| C04 | 23／10 | 21／10 | **0** |

T05 做多 listed：聯強、聯詠、安勤、翔名、義隆、旺矽、豐藝、鴻準、瑞昱、廣積。

## 殼

`trend_pullback_catalog.py` 增 W2 閘／sma／rsi_wilder／bollinger；探針 `--wave W2`。T01＠W2 拒。指標不進 panel。

自測 rc=0。探針 rc=0。假 B3 rc=3。

## 不做

W3 Elder；W4 截面；W5 OOS；倒 31；改 standing。
