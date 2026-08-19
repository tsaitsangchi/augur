---
status: executed
series: s4_s5_verify
track: TREND-PB
date: 2026-08-19
viewpoint: 2026-08-19T08:55+08:00
asof: "2026-08-18"
wave: W1
shell: scripts/probe_trend_pb_catalog.py
json: /tmp/trend-pb-2026-08-18-W1.json
paste: "TREND-PB-W1-go | date=2026-08-18 | families=T01,T02,T11,C01,C03,C06,C07 | k=10"
selftest: green
self_reported: true
layer: "[I]"
---

# EXECUTED｜TREND-PB W1＠2026-08-18

Steward 08:51 明示。零寫 `prediction_values`。未 promote。W2 未開。`--date 2026-08-19` → rc=3。C02 不在 paste。

## 答（誠實）

- as-of＝**2026-08-18**＝價頂；scored＝284／宇宙 286。
- **T01**＝UP-PULL-v1 重出：做多 **5**、做空 **2**（緯創／微星／東和鋼鐵／永豐餘／鈊象；卜蜂／大世科）。
- **C01（八窗全正）∩ T01 = 0**；**C06（年線高位）∩ T01 = 0**。拉回進場與「正在漲／貼高」不是同一批。
- T01 的 5 檔全部落在 T02（71）、T11（86）、C03（193）、C07（177）的**過閘集**；但這些寬閘的 listed Top10 與 T01 **0 重疊**（長窗更強的名字排前面）。
- 單日重疊 ≠ OOS、≠可交易。做空 ≠ 可空。

## 規模

| ID | 做多 pass／listed | 做空 pass／listed | vs T01 做多交集 |
|---|---|---|---|
| T01 | 5／5 | 2／2 | — |
| T02 | 71／10 | 29／10 | 5 |
| T11 | 86／10 | 9／9 | 5 |
| C01 | 25／10 | 18／10 | **0** |
| C03 | 193／10 | 91／10 | 5 |
| C06 | 18／10 | 20／10 | **0** |
| C07 | 177／10 | 101／10 | 5 |

C01 listed 含光寶科、台光電、大立光。C06 listed 第一名光寶科。

## 殼

| 檔 | 角色 |
|---|---|
| `src/augur/evaluation/trend_pullback_catalog.py` | W1 閘；T01 呼叫 UP-PULL-v1；T05＠W1 拒 |
| `scripts/probe_trend_pb_catalog.py` | 唯讀 CLI；假 B3 rc=3 |

自測 library／CLI rc=0。探針 rc=0。假 B3 rc=3。

## 不做（本槍未開）

W2 RSI／均線；W5 OOS；W6 訓練；C02；改 standing；當可交易。
