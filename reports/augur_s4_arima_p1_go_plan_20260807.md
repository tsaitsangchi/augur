---
title: S4-ARIMA-P1 · B-1a Phase 1 go-plan（有界；零默訓）
status: plan_first
series: s4_models
track: NF-B-P1
date: 2026-08-07
viewpoint: 2026-08-07T14:20+08:00
paste: "S4-ARIMA-P1-go-plan | FZ/GATE-keep | skip-sync | no-SIM-apply | hist-until=2026-06-30"
inventory: audits/S4-ALL-PREDICTION-MODELS-INVENTORY-20260807.md
v2: audits/S4-V2-SKIP-HIST-QUEUE-ADOPTED-20260807.md
phase0b: audits/S4-WAVE-B-ADAPTER-PHASE0B-EXECUTED-20260805.md
nf_pause: audits/S4-NF-PAUSE-ACCEPTED-20260805.md
layer: "[I]"
role: Wave-A 收官後「下一族」＝B-1a ARIMA Phase 1 計畫；零碼／零開訓
self_reported: true
---

# S4-ARIMA-P1-go-plan｜B-1a ARIMA／SARIMA · Phase 1 · 2026-08-07

> **Steward**：Wave-A sklearn 有界重驗全 STOP → V2 下一格＝**B-1a ARIMA**；本檔＝**P1 plan-first**。  
> **一句**：Phase 0b 已證 mean hit > naive；Phase 1＝擴大宇宙／釘歷史窗／另書量尺閉合——**仍 ≠ #14 可交易、≠ 塞 RankRidge serve**。  
> **本檔 ≠** `S4-ARIMA-P1-go`（執行）· ≠ 改 `model_family_chk` · ≠ promote。

---

## §0 護欄

```text
S4-ARIMA-P1-go-plan | FZ/GATE-keep | skip-sync | no-SIM-apply | hist-until=2026-06-30 | hold-#1
# ≠ S4-ARIMA-P1-go；≠ 撤全域 NF-pause（僅本族另句有界）；≠ 混截面 #14；≠ sim-apply
```

| 可（本計畫） | 不可 |
|---|---|
| 寫 P1 範圍／尺／階段／paste | 本句跑全宇宙 fit／寫 registry |
| 釐清 0b 有證據≠可交易 | 把 0b 綠當確立級／升格 LIVE |
| 排執行 GO／可選 schema | 連帶解凍 GARCH／VAR／GNN |
| hold #1 | 改 dgate；`predict_asof` 默認換族 |

---

## §1 為什麼是 ARIMA（佇列答）

| 項 | 值 |
|---|---|
| V2 優先 | **3**（Wave-A 樹／sklearn 已關；classical 首格） |
| Wave-A | RF／XGB／Cat／SVM／MLP／KNN＝**STOP** · **勿重掃** |
| Phase 0b | ARIMA mean hit **0.5370** > naive **0.5185**（15 股＠05-31／H20）→ **有證據** |
| adapter | `ArimaUnivariate`＋`probe_classical_ts_phase0b.py` **已在** |
| 歷史資料 | PriceAdj 單股序列 · 庫內 as-of；特徵＝可選（P1 默認**純價序列**） |
| registry | family 字面 **`ArimaUnivariate`** 尚**不在** `model_family_chk`——登錄須另 `SCHEMA-…` 或 P1 明示 ALTER |

---

## §2 Phase 1 範圍（執行時才做）

若後續貼 **`S4-ARIMA-P1-go`**：

### 2.1 有界撤 pause（僅 B-1a）

- **僅**授權 ARIMA／`ArimaUnivariate` 歷史窗作業；全域 NF 對其他族 **keep**。  
- **不做**：GARCH 預測綠、VAR、塞進 `train_ranker`／截面 backtest 冒充冠軍。

### 2.2 建議網格（示意；執行帳可縮小）

| 參數 | 預設草案 |
|---|---|
| asof／until | **2026-06-30**（與 Wave-A 凍結窗對齊） |
| horizon | **H20**（延續 0b；H60 另授） |
| 宇宙 | core_universe_asof＠asof · 可分批（先 n=50 → 全 core） |
| order | 固定 **(1,0,1)**（#15；禁自動搜參當完成） |
| walk-forward | 月步；`train_window`／`max_folds` 寫死並標「近端窗≠全史」 |
| 地板臂 | naive（近 1 日號）；可選常數 0.5 |

```bash
# 須另句 S4-ARIMA-P1-go 才跑——示意
PYTHONPATH=src ./venv/bin/python scripts/probe_classical_ts_phase0b.py --run \
  --n-stocks 50 --horizon 20 --asof 2026-06-30 --max-folds 36
# 全宇宙／registry／OOS 落表＝同 GO 子步或再另句
```

### 2.3 預凍通過門（寫死後再跑）

| 尺 | 門檻 |
|---|---|
| 主 | 宇宙 mean(ARIMA hit) **嚴格 >** mean(naive hit) |
| 穩 | 有效股覆蓋誠實陳報；失敗股＝SKIP 不填假 |
| 經濟／可交易 | **不適用**本尺當 #14；禁宣稱可換 RankRidge |
| registry／serve | **預設不登錄**；若要登須子句＋ CHK 含 `ArimaUnivariate`＋ **no-serve-swap** |

未過門 → **STOP P1 promote**（帳面收口，可留探針）。

---

## §3 與既有交叉

| 檔 | 關係 |
|---|---|
| `S4-WAVE-B-ADAPTER-PHASE0B-EXECUTED` | 0b 有證據＝本 P1 開門前提 |
| `augur_s4_wave_b_classical_ts_adapter_plan` | P1＝其 Phase 1 格 |
| `S4-NF-PAUSE-ACCEPTED` | 解凍路徑＝`S4-ARIMA-P1-go`（本檔只 plan） |
| `SCHEMA-FAMILY-CHK-*` | 挑戰 ranker 已開；**ARIMA 字面未加入** |
| #1 A→B3 | **hold**；P1 閒時 ⊥ live B3 |

---

## §4 Paste-ready

採納本計畫（零開訓）：

```text
S4-ARIMA-P1-plan-adopt | FZ/GATE-keep | NF-pause-others | no-train | hold-#1
```

執行 Phase 1（另決策）：

```text
S4-ARIMA-P1-go | FZ/GATE-keep | skip-sync | no-SIM-apply | hist-until=2026-06-30 | H20 | no-promote | no-serve-swap | hold-#1
```

可選子句（執行後才談）：

```text
S4-ARIMA-P1-registry-go | … | ADD family=ArimaUnivariate | no-serve-swap
```

---

## §5 驗收（本窗 plan）

- [x] 點名佇列下一族＝**B-1a**；Wave-A 已關不重掃  
- [x] 0b 數字＋P1 範圍／預凍門寫死  
- [x] 明文 **≠ #14 混尺／≠ 默認 serve／≠ 本窗開訓**  
- [ ] 真跑 → 須 `S4-ARIMA-P1-go`  

*完。[I] plan-first · self-reported。*
