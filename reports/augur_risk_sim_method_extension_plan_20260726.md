# augur_risk_sim_method_extension_plan_20260726 — 組合風險模擬方法擴充（stationary bootstrap＋GARCH-FHS 對照組）

> **性質**：#20 計畫書；hugo 2026-07-26 指示擴方法。**分級＝非高風險**（單一 script 域、零新表、零治權檔變更、append-only 帳本可逆）→ 單視角自審＋完整性對抗自問，未動用多 agent 審查（#28 非必要不 fan-out）。定位＝**A 軌（07-25 拍板）之對照組擴充**，非新軸——A 軌全部誠實硬綁原封繼承。
> 現況錨（2026-07-26 實probe，非記憶）：①venv **無 `arch`**、有 scipy 1.18.0 ②`simulate_mc_paths.py` 引擎簽名 `_simulate(logr, h, n_paths, method, block_len, rng)`、`BLOCK_LEN=21` ③**`mc_simulation_run.method` 有 CHECK 白名單（僅現有 5 值）→ 新方法值須先遷移約束** ④帳本現況 525 筆（iid 265／block 265／episode 15）。

## 一、What／Why 與資訊增益上限（事前聲明，防事後美化）

**目的**：檢驗 A 軌 bootstrap 參考分布對「方法假設」的敏感度——現有兩式各含一個可疑假設：iid（無叢聚）與固定塊長 21（塊界人為）。兩個新方法各拆一個假設：

| 新方法 | 拆掉的假設 | 保留的假設 |
|---|---|---|
| **stationary bootstrap**（Politis-Romano 1994） | 固定塊長（改幾何分布隨機塊長、期望 21td，與 block 引擎同均值＝單獨隔離「塊長固定 vs 隨機」） | 仍從同一 749td 窗重抽 |
| **GARCH(1,1)-FHS**（filtered historical simulation） | 波動齊性（GARCH 濾波→標準化殘差重抽→前向波動遞迴，壞日的波動會傳染） | 殘差仍來自同一窗；參數擬合於平靜窗 |

**資訊增益上限（誠實天花板，寫在跑之前）**：兩法**都仍從同一 749td 窗取材——窗內沒有 -20% 級聯合回檔，任何重抽法都變不出窗外的 2008**。故：(a) episode 重放的主結論地位**不因本擴充改變**；(b) 本擴充回答的唯一問題是「參考分布對方法選擇穩不穩」，不是「尾部風險有多大」；(c) 若新舊方法給出相近數字，結論是「方法穩健」而非「風險已知」。

**預註冊判讀規則（跑之前定死，防 post-hoc）**：
1. H60／H120 之 P(MaxDD<政策閾) 四法（iid/block/stationary/garch_fhs）落同一數量級 → 記「方法穩健」；跨數量級 → 逐法列出、以**最保守值**入風險畫像敘述。
2. GARCH-FHS 之 MaxDD p5 比 block 深 ≥1.5× → 記「波動叢聚被固定塊長低估」，此發現升級為風險畫像註記（仍屬參考層）。
3. 任何結果**不得**回寫、觸發或預告 risk_control；不得使 bootstrap 族升為主結論。

## 二、表結構（v1.39.0 (a)；零新表＋一條約束遷移 DDL）

**寫入表＝既有 `mc_simulation_run`**（run_id PK／target_id／asof_date／horizon_td／method／block_len_td／n_paths／seed／summary jsonb／is_simulation CHECK true／git_sha／created_at）。**讀**：`prediction_values`（panel_date/model_id/stock_id/in_portfolio/weight）、`TaiwanStockPriceAdj`、`risk_policy`（閾值唯讀）。

**唯一 DDL＝method CHECK 白名單加寬**（幂等遷移；白名單保留＝繼續擋 typo 方法名，非改成自由文字）：

```sql
ALTER TABLE mc_simulation_run DROP CONSTRAINT mc_simulation_run_method_check;
ALTER TABLE mc_simulation_run ADD CONSTRAINT mc_simulation_run_method_check
  CHECK (method = ANY (ARRAY['iid_bootstrap','block_bootstrap','stationary_bootstrap','garch_fhs',
                             'episode_replay_2008','episode_replay_2020','episode_replay_2022']));
```

新列口徑：stationary → `block_len_td=21`（記期望塊長）；garch_fhs → `block_len_td=NULL`；`summary.kind='bootstrap_reference'` 不變（同層級）、另加 `summary.fit_diag`（garch_fhs 專用：ω/α/β/persistence/擬合視窗 n、收斂旗標——擬合品質入帳可稽）。

## 三、程式規畫（v1.39.0 (b)；三檔、全部既有慣例內）

| 檔 | 動作 | 內容 |
|---|---|---|
| `scripts/migrate_mc_method_check_ddl.py` | **新增** | §二 DDL 幂等遷移；#18/#29 全矩陣＋`--selftest`（零 DB：SQL 文字含七方法值紅綠）；`--dry-run` 只印不動 |
| `scripts/simulate_mc_paths.py` | 修改（引擎之家） | 加兩個純 numpy 單序列引擎，簽名對齊既有：`_stationary_paths(logr, h, n_paths, mean_block, rng) -> paths`（幾何塊長 p=1/mean_block、環繞取樣）；`_garch_fhs_paths(logr, h, n_paths, rng) -> (paths, fit_diag)`（arch 套件 QMLE 擬合 GARCH(1,1)→經驗標準化殘差重抽→前向 σ 遞迴） |
| `scripts/simulate_portfolio_risk.py` | 修改（消費端） | `--run` 方法迴圈納入兩新法（缺 arch → garch_fhs graceful SKIP 印明因、其餘照跑）；新增 `--compare [--cell X]` 唯讀模式：同 cell 四法 MaxDD 分位＋P(MaxDD<閾) 並排表（純讀帳本、零重算） |

**selftest 增項**（零 DB／零 arch 硬依賴）：①stationary 以 mean_block=1 退化＝逐步獨立抽樣（塊長全 1 斷言）②塊長樣本均值≈mean_block（寬容差）③同 seed 重現④garch_fhs：合成 GARCH 序列擬合 persistence 方向正確＋合成 iid 序列 α+β 低（arch 缺席→此兩項 SKIP 非 FAIL，#18 慣例）⑤NaN／短序列 fail-closed。

**新依賴（須你點頭的唯一外部項）**：`venv pip install arch`（Kevin Sheppard 套件，GARCH QMLE 業界標準）。**建議採用**：手刻 MLE 是「搞錯沉默污染下游」型風險（擬合錯→分布錯→帳本錯），成熟套件優於自製；本地安裝零 usage、venv 近日已有 peft/trl 先例。若你否決新依賴 → garch_fhs 整項降級為「不做、留檔原因」，stationary（純 numpy）照做。

## 四、分階段與驗收

| 階段 | 內容 | 驗收 |
|---|---|---|
| P1 | 遷移＋兩引擎＋selftest | selftest 全綠；CHECK 遷移後七值可寫、typo 值仍被擋（負向測試） |
| P2 | 凍結 panel（2026-05-31）五 cell × 兩新法實跑 | 帳本 +10 筆（run_id 雜湊幂等）；每筆 summary 含 disclaimer 全 note（grep 驗）＋garch_fhs 含 fit_diag；seed=42 重跑逐位重現 |
| P3 | `--compare` 對照表＋收尾報告（`reports/augur_risk_sim_method_comparison_20260726.md`，數字全出自 stdout/DB #9） | 對照表按 §一預註冊規則判讀；報告含「窗偏差不變、episode 主結論不變」聲明 |

**成本**：一條 DDL＋兩個引擎函式＋一個唯讀模式，<半天工；runtime：GARCH 擬合 749 obs 秒級、10k 路徑×120td numpy 向量化＜1 分鐘/cell；全程本地零 usage。**人閘**：本計畫拍板（含 arch 依賴同意與否）＝唯一閘；晉升/治權零涉及。

## 五、完整性對抗自問（單視角分級之替代審查，留痕）

- *為何不用 Politis-White 自動塊長選擇？*——會引入第二個自由度，破壞「與 block 引擎同均值＝單獨隔離塊長假設」的對照設計；留作未來敏感度選項。
- *為何 GARCH 用經驗殘差不用 t 分布抽樣？*——FHS 的定義即經驗殘差（保留窗內真實偏態/峰度）；參數化殘差是另一方法（Monte Carlo GARCH），會混入分布假設、偏離「對照」目的。
- *擬合於平靜窗的 GARCH 前向波動會不會太樂觀？*——會，且無法在本窗內修復；已入 §一天花板聲明＋fit_diag 落帳供日後檢視。
- *episode 重放要不要也擴（如 2011/2015/2018）？*——屬另案（擴窗不擴法）；本計畫守最小邊界不夾帶。
- *CHECK 改自由文字更省事？*——否，白名單擋 typo 方法名是機械誠實閘的一部分，加寬不拆除。
