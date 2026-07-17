# arena 新候選提案：Chronos-2 + Moirai-2.0 入賽（2026-07-17，呈 hugo 拍板）

**性質**：A-3 候選定版流程之新候選提案（#20 計畫先行；拍板後才實作）。
**先例**：market 隊 chronos_bolt_small／timesfm_25_200m（已在賽、07-16 起出手）。

## 一、依據（全實證）

1. **本日台股 benchmark**（`reports/tsfm_taiwan_benchmark_20260717.md`）：Chronos-2＝四 TSFM 中**一致最不退化**（五股 skill −0.0002~−0.0031、全池最穩）；
2. **論文 arXiv:2606.27100**：Moirai-2.0＝美股平均排名最佳（2.9）、唯二達 DM 顯著者之一；
3. **誠實前提**：benchmark 已證**點預測無 edge**（20 檢定零顯著）——但 arena 裁的是**方向機率品質**（命中率/Brier/校準、≥60 clusters 門二），與點預測不同軸。入賽期望＝**保守**：給擂台加入 2026 最強兩員、讓它們接受與其他隊完全相同的判準；勝負由市場開牌，不預設它們會贏。

## 二、候選 spec（凍結內容；INSERT `direction_arena_candidate`）

| 欄 | market_chronos2 | market_moirai2 |
|---|---|---|
| model_key | `chronos2_market_5` | `moirai2_small_5` |
| team／track／h | market／D／5 | market／D／5 |
| 權重 | `amazon/chronos-2`（HF、本地推論） | `Salesforce/moirai-2.0-R-small`（HF、本地推論） |
| 轉換口徑 | **凍結＝同既有 market 隊**：close 序列（≤512）→ H=5 終點九分位 → P(up)＝1−interp(現價, 分位曲線)（`adapters.py` MarketChronos 口徑原文） | 同左（樣本分位版：num_samples→九分位→同插值） |
| gate_eligible | True | True |
| weights_hash | 凍結時記 HF revision hash | 同左 |

**實作備註（實測已知）**：Chronos-2 `predict_quantiles` 回 `list[(1,H,9)]`（與 v1 stacked 不同、squeeze 統一——benchmark 已踩雷修過）；Moirai 走 gluonts `ListDataset` 路徑（benchmark 已驗可跑）；uni2ts 依賴已入主 venv 且四關驗綠（arena 冒煙/score repro 112 復現/e5/DB）。

## 三、程式規畫（拍板後實作；#29 全規格）

| 件 | 內容 |
|---|---|
| `src/augur/arena/adapters.py` | 加 `MarketChronos2`／`MarketMoirai2` 兩 class（鏡射 MarketChronos ~35 行/支、lazy load）＋入 `REGISTRY`＋selftest 結構鎖 |
| 候選註冊 | INSERT 兩列 `direction_arena_candidate`（spec JSONB 凍結+code_sha+weights_hash；status=active） |
| gate | `preregister_direction_gate.py` 加 `dgate_arena_chronos2_5`／`dgate_arena_moirai2_5` draft（判準＝完全複製既有六門：先凍後跑、futility 60/1.645） |
| 驗收 | A0 合成冒煙（`--smoke-synthetic`）雙過 → 首手落 ledger ≥1 日 |

## 四、風險與邊界

- **推論成本**：每日 344 檔×2 模型、本地 GPU/CPU 秒-分級（benchmark 實測快）；失敗＝誠實缺席不阻他隊（既有韌性）。
- **判準零特權**：兩隊與所有隊同判準、同 tier（review_observation_only）、同門二升格路徑；**不因「2026 最強」降低任何門檻**。
- **不可逆點唯一**：dgate approve（你 TTY 或授權代跑；approve 後 criteria trigger 鎖）。
- 落後入賽＝比其他隊晚 ~2 日樣本，對 ≥60 clusters 時程影響可忽略。

## 五、拍板點

1. 兩候選 spec 照案凍結？（§二）
2. dgate approve 方式：你 TTY 親核（六門慣例）或聊天授權代跑（07-16 admission gate 先例）？

拍板後實作鏈：adapter＋selftest → 冒煙 → 候選 INSERT → dgate 預註冊 → approve → 首手 → 封存。
