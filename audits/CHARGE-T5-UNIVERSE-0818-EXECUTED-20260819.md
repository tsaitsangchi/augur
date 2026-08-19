---
status: executed
series: s4_s5_verify
track: CHARGE-T5
date: 2026-08-19
viewpoint: 2026-08-19T13:36+08:00
tip: "2026-08-18"
kind: universe_p1
dry_run: true
wrote_prediction_values: false
standing_unchanged: true
paste: "CHARGE-T5-universe-go | dry-run | IS=2024 OOS=2025-01..2026-06 | 不要抱牢"
plan: reports/augur_charge_t5_model_plan_r18_20260819.md
json: audits/CHARGE-T5-UNIVERSE-0818.json
shell: scripts/probe_charge_t5.py
lib: src/augur/evaluation/charge_t5.py
selftest: green
fake_b3_0819: rc=3
version: CHARGE-T5-v1
k: 10
hold: 5
pit: nearest_asof_le_D
n_sids: 372
is_baskets: 240
oos_baskets: 340
is_gross_pct: 43.8
oos_gross_pct: 2181.0
is_cost_pct: -64.8
oos_cost_pct: 210.3
both_windows_gross: true
both_windows_after_cost: false
self_reported: true
layer: "[I]"
---

# EXECUTED｜CHARGE-T5 宇宙＠切窗（不要抱牢）

Steward 貼 `CHARGE-T5-universe-go | dry-run | IS=2024 OOS=2025-01..2026-06 | 不要抱牢`。零寫庫。08-19＝假 B3（探針 rc=3）。≠可交易、≠改 standing、≠#14。兩檔 39 筆％不是本模型績效。

## 尺（凍結）

規則＝E-charge×T5。宇宙＝`core_universe_asof` **PIT**（最近 as_of≤D；2024–25 月頻快照往前帶，無更早快照才跳過）。同日新訊號依 mean(H60,H120,H240) 取 **k=10**、等權；檔內持有 5 交易日；在倉不加倉。IS＝2024 訊號；OOS＝2025-01-02～2026-06-30；出場 ≤ 2026-08-18。

成本地板＝來回 **0.585%**。排序／是否兩窗同號先看無成本；成本欄作敏感度。T10／T20／T40＝同一進場改持有，**不當冠**。逐檔 100% 連乘＝非組合對照。

## 組合帳（模型）

| | 籃／檔次／勝 | 無成本複利 | 成本後 | 日均檔數 | 截斷日 |
|---|---|---|---|---|---|
| IS | 240／1646／132 | **+43.8%** | **−64.8%** | 6.9 | 74 |
| OOS | 340／1714／188 | **+2181%** | +210% | 5.0 | 39 |

兩窗同號：無成本 **是**；成本後 **否**（訓練窗被週轉打穿）。

IS 幾乎每個交易日都有一籃（240 籃／年）。這不是「奇鋐偶爾轉折」，是全宇宙幾乎天天換約 7 檔。240 次來回 × 0.585% 的連乘拖累約把 +44% 吃成 −65%。OOS 無成本 +2181% 是 2025–26 大多頭＋高週轉連乘，**不是**預期報酬。

## 不要抱牢（對照，不當冠）

同一進場、改持有：

| 持有 | IS | OOS | 標 |
|---|---|---|---|
| T5 | +43.8% | +2181% | 模型 |
| T10 | +469% | +3.4萬% | 對照 |
| T20 | +2056% | 數百萬％ | 偏抱牢；OOS 更高仍不當冠 |
| T40 | +9.9萬% | 無意義連乘 | 對照不當冠 |

OOS 愈長愈大，正是這把尺要擋的。不改模型持有。

逐檔 100% 連乘（非組合）IS n=1916 **+1231%**（成本後 −100%）；OOS n=1827 無成本亦是極端連乘。不當產品績效。

## 兩檔對帳（探針沒算錯）

| | IS | OOS |
|---|---|---|
| 舊帳（TWIN-EX 兩檔連乘） | 15／+56.8% | 24／+72.9% |
| 宇宙 PIT、無 k | **15／+56.8%** | **24／+72.9%** |
| 宇宙 k=10 入選 | 14／+46.4% | 24／+64.0% |

無 k 與舊帳對上。k=10 在 2024 擠掉 1 筆。兩檔最佳仍不是宇宙組合的成本後結果。

入選次數最多（不是買點）：IS 聖暉*／漢平／億光；OOS 欣銓／台光電／日電貿。台積電兩窗都在前段。

## 結論（誠實）

CHARGE-T5-v1 **宇宙走步已閉**。規則能在核心宇宙重現，但訓練窗扣成本後為負；OOS 大數不可當預期。**未**通過成本後兩窗同號。≠可交易、≠確立、不改 standing。若要降週轉（冷卻、隔日上限、更小 k）＝**新 ID**，本版不改 θ。

## 本窗未做

單日探針；emit；FIT／SHORT；寫 `prediction_values`；promote；commit；假 B3＠08-19。
