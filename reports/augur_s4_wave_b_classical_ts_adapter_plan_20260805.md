---
status: draft
series: s4_model_families
depends_on:
  - reports/augur_s4_market_model_families_opt_plan_20260804.md
  - audits/S4-WAVE-B-EXECUTED-20260804.md
  - audits/S4-MODELS-TRIED-LIST-20260804.md
---

# S4-Wave-B 後續 — classical TS 首個預測薄殼 adapter plan-first（2026-08-05）

> **性質**：[I] plan-first（憲章第六部；CLAUDE #20）。**不含**假訓湊數、不含把 sim GARCH 當預測綠燈。
> **誠實定錨**：`S4-WAVE-B-go` **已 EXECUTED**（2026-08-04）＝五族**誠實 SKIP 普查**，非「尚未開波」。本檔＝該帳 §6「薄殼 adapter／單股尺＝另 plan＋另 GO」之接續案。
> **self-reported（#32a）**。

---

## 0. 一句話

**Wave-B 普查已證明：statsmodels／arch 在場 ≠ 預測熱路徑；下一刀若要做，只准做「有另書量尺、可誠實 SKIP 失敗」的單族薄殼——首選 B-1a ARIMA／SARIMA，且不得與截面 #14 混稱可交易。**

---

## 1. 普查結論（不重做）

| ID | 族 | 普查裁決 | 本檔是否碰 |
|---|---|---|---|
| B-1a | ARIMA／SARIMA | SKIP（無預測薄殼） | **是——首候選實作** |
| B-1b | GARCH | SKIP（預測）＋n/a-sim | **否**（sim 風險尺另冊；禁冒充） |
| B-1c | VAR／VECM | SKIP（缺多序列契約） | 否（依賴 S3 外生／面板契約成熟） |
| B-1d | Kalman／狀態空間 | SKIP | 否 |
| B-1e | 協整 | SKIP | 否 |

證據 SSOT＝`audits/S4-WAVE-B-EXECUTED-20260804.md`。

---

## 2. 為何首選 ARIMA／SARIMA（B-1a）

| 判準 | 說明 |
|---|---|
| 依賴最小 | 單股單序列價／報酬；S3 組 1–2 **have**；不需圖／序列窗新表 |
| 套件已在 | `statsmodels` 可 import（普查已證） |
| 失敗可誠實 | 不收斂／樣本不足 → SKIP 該股該折，不填假預測 |
| 量尺需另書 | **非**橫斷面 rank 主尺；不可直接套 `RankRidge` 冠軍門檻自稱「贏了可交易」 |

**明確不做**：用 `simulate_*` GARCH 路徑宣稱 S4 預測 PASS。

---

## 3. (a) table schema

| 表 | 動作 |
|---|---|
| 新特徵表 | **無**（讀既有 PriceAdj／`feature_values` 報酬通道） |
| `model_registry` | Phase 1 評測通過後才允許登錄（另授）；Phase 0 **零寫入** |
| 可選研究表 | 若需落 OOS 單股預測：`classical_ts_oos_sample`（僅授權後建；本檔 Phase 0 可不建表、stdout／JSON 即可） |

## 4. (b) python 規畫

| 檔 | 角色 |
|---|---|
| `src/augur/models/classical_ts.py`（新） | 薄殼：`fit(series)`／`predict_horizon(h)`；family 名如 `ArimaUnivariate`；`--selftest` 零 IO |
| `scripts/train_classical_ts.py`（新） | CLI：庫內 as-of、單股或小宇宙、`--dry-run` 預設；矩陣＋`--selftest` |
| `scripts/eval_classical_ts_probe.py`（新或暫 `/tmp`） | Phase 0：另書量尺（例：單股方向 hit／RMSE vs naive）×≥3 seed（若有隨機）或確定性重跑 |
| `ranker.py`／`predict_asof.py` | **零改**（不同任務；不得塞進截面 rank 熱路徑） |
| `portfolio.run_backtest` | **零改**（截面尺≠本族尺） |

---

## 5. 另書量尺（#14 邊界誠實）

| 尺 | 用途 | 禁稱 |
|---|---|---|
| 單股 forward 方向 hit＠H20／H60 | 可行性 | 「可交易」「確立級」 |
| vs naive（歷史均值／前值） | 地板臂（#32b） | 勝過地板≠晉升 ranker |
| 截面彙總（可選後期） | 多股平均 hit | 不得替代 `run_economic_eval` 冠軍門 |

**預凍對照臂**：至少常數／naive 地板；未嚴格勝過地板 → 「無證據」、不進 Phase 1。

---

## 6. 分階段

| 階段 | 內容 | Gate | 另授權？ |
|---|---|---|---|
| **Phase 0** | library＋CLI 骨架＋單股煙測＋地板臂 | selftest 綠；≥1 股可跑；誠實 SKIP 路徑可證紅 | 本計畫審過後 |
| **Phase 0b** | 小宇宙（如 10–20 股）×主 horizon 探針 | 分布陳報；未過地板＝停 | 是 |
| **Phase 1** | registry／serving | 另 plan；預設**不**接 `predict_asof` 主路徑 | 是 |

---

## 7. 硬邊界

- `S4-WAVE-B-ADAPTER-go | FZ/GATE-keep | skip-sync | no-SIM-apply`（建議 GO 句；**≠**重跑已完成之 Wave-B 普查 GO）
- 禁 sim GARCH→預測綠；禁解凍 API 補洞；禁與 RankSVM／DirStack 升格綁票。

---

## 8. 請 Steward 裁示

1. **approve_phase0** — 授權 B-1a 薄殼 Phase 0（推薦）
2. **defer** — classical 維持 SKIP 列帳，本輪不做碼
3. **other_family** — 改先做 B-1c／B-1d（須說明為何覆寫「依賴最小」排序）

---

*定版（2026-08-05）。Wave-B 普查不重開；本檔只覆蓋「SKIP → 可選薄殼」之接續。*
