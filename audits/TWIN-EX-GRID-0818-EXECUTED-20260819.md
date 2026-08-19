---
status: executed
series: s4_s5_verify
track: TWIN-EX
date: 2026-08-19
viewpoint: 2026-08-19T11:26+08:00
tip: "2026-08-18"
kind: grid_p1
sids: ["3017", "2395"]
dry_run: true
wrote_prediction_values: false
paste: "TWIN-EX-grid-go | sids=3017,2395 | dry-run | 不要抱牢"
plan: reports/augur_twin_ex_qihong_yanhua_plan_r18_20260819.md
json: audits/TWIN-EX-GRID-0818.json
shell: scripts/probe_twin_ex.py
selftest: green
fake_b3_0819: rc=3
self_reported: true
layer: "[I]"
---

# EXECUTED｜TWIN-EX 格子＠切窗（不要抱牢）

Steward 貼 `TWIN-EX-grid-go | sids=3017,2395 | dry-run | 不要抱牢`。零寫庫。08-19＝假 B3（探針 rc=3）。≠可交易、≠全宇宙、≠改 standing。

## 尺（凍結）

IS＝2024 訊號日；OOS＝2025-01-02～2026-06-30；出場須在價頂 2026-08-18 內結束。合格＝非 T40、OOS n≥8、IS 與 OOS 複利都＞0。冠軍主鍵＝IS 複利；OOS 不當主鍵。抱牢只對照。

成本地板＝來回 **0.585%**（`direction_product_config.cost_roundtrip`）。排序仍用無成本欄；成本欄作敏感度。

兩檔合計＝交易序列連乘，不是同時持有的組合帳。

## 不要抱牢冠軍

**E-charge × X-T5**（工作假說仍成立，**僅此兩檔格子**）。

| | n／勝 | 無成本複利 | 成本後 |
|---|---|---|---|
| IS | 15／9 | **+56.8%** | +43.6% |
| OOS | 24／15 | **+72.9%** | +50.2% |

分檔兩窗都正：奇鋐 IS +39.7%（11）／OOS +36.0%（16）；研華 IS +12.2%（4）／OOS +27.1%（8）。

成本後此組仍兩窗都正，且 IS 成本複利仍高於其他合格組。

## 沒當冠（刻意）

- **E-watch × T20**：OOS **+341%**（格子最高），IS 只有 +4.7% → 排合格組第 9。禁 OOS 長持有當冠。
- **E-charge × T20**：OOS +310%，IS +0.7%；扣成本後 IS **−5.0%**。偏抱牢。
- **X-T40**：對照不當冠（charge 的 OOS n=7 也不滿 8）。

次名合格組：E-watch×T10（IS +38.7%／OOS +195%），持有更長，主鍵仍低於 T5。

## 抱牢對照（不是目標）

| | IS | OOS | 2024-01-02→08-18 |
|---|---|---|---|
| 3017 奇鋐 | +91.3% | +314.2% | +840.1% |
| 2395 研華 | −3.8% | +46.7% | +93.3% |

奇鋐進出遠小於抱牢；研華 2024 抱牢為負、進出為正。本軌本來就不是要贏「一直抱著」。

## 本窗未做

寫 `prediction_values`；promote；sim `--apply`；假 B3＠08-19；宇宙外推（`TWIN-EX-universe-go`）；commit。
