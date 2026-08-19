---
status: executed
series: s4_s5_verify
track: TREND-PB
date: 2026-08-19
viewpoint: 2026-08-19T09:12+08:00
asof: "2026-08-18"
wave: W3
shell: scripts/probe_trend_pb_catalog.py
json: /tmp/trend-pb-2026-08-18-W3.json
audit_json: audits/TREND-PB-W3-0818.json
paste: "TREND-PB-W3-go | date=2026-08-18 | families=T07 | k=10"
selftest: green
approx: elder_2screen_daily
self_reported: true
layer: "[I]"
---

# EXECUTED｜TREND-PB W3＠2026-08-18

Steward 09:05 明示。零寫 `prediction_values`／`feature_values`。未倒 canonical 31。未 promote。`--date 2026-08-19` → rc=3。

T07 **不是** Elder Triple Screen 原作。日頻無盤中第三屏；JSON `approx=elder_2screen_daily`。Force Index／量能振盪器省略。週線代理＝每 5 交易日抽樣（末點＝asof）之 MACD(12,26,9) 柱斜率。

## 答（誠實）

- as-of＝**2026-08-18**＝價頂；scored＝284／宇宙＝286。T01 做多過閘仍＝**5**（內部對照）。
- **T07 ∩ T01 做多＝0**；做空亦＝0。T01 要 H5／H10 都負，那一段拉回常把「週 MACD 柱仍在上升」翻掉——兩套閘在 08-18 不相交。
- 做多過閘 **67**（RSI(2)＜50 很寬）；listed 依 RSI(2) 由低到高截 10。做空過閘 **19**／listed 10。做空 ≠ 可空。
- 柱斜率＞0 允許柱仍為負（動量還在水下但柱在抬）。單日 ≠ OOS。

## 規模

| ID | 做多 pass／listed | 做空 pass／listed | vs T01 做多 | vs T01 做空 |
|---|---|---|---|---|
| T07 | 67／10 | 19／10 | **0** | **0** |

做多 listed：2354 鴻準、3529 力旺、3324 雙鴻、6261 久元、3689 湧德、3548 兆利、8074 鉅橡、2451 創見、3029 零壹、3491 昇達科。

做空 listed（≠可空）：1231 聯華食、2412 中華電、3045 台灣大、4904 遠傳、1210 大成、1722 台肥、1227 佳格、1232 大統益、5522 遠雄、9911 櫻花。

## 殼

`trend_pullback_catalog.py` 增 MACD／週抽樣／T07 閘；探針 `--wave W3`。T07＠W2、T05＠W3 拒。指標不進 panel。

自測 rc=0。探針 rc=0。假 B3 rc=3。

## 不做

W4 截面；W5 OOS；倒 MACD／RSI 進 31；改 standing；宣稱＝三屏原作。
