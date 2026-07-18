---
name: core-universe-and-f3-model
description: 核心股選拔四道閘(候選空間+完整度+流動性+conditional)→⚠**344(2026-07-17 實查 core_universe;原記 875 為 06-25 pilot 史值,已被 06-29 SOP P25 重建取代)**;F3 模型 as-of Ridge H60 rank IC+0.132(→現+0.1418);全管線打通
metadata:
  node_type: memory
  type: project
  originSessionId: c3c40e0c-7154-4936-8937-6d9ce947808c
---

augur 已從「raw 完整」推進到「**核心股選出 + 模型驗證 alpha 為真**」,**全管線 raw→feature→universe→model→validate 打通**(2026-06-25/26、兩機並行整合)。

**核心股選拔(`universe/core_gate.py`)＝四道閘**:
1. **候選空間關**:真台股個股代碼(`stock_id ~ '^[0-9]'`)∧ 非 ETF(`industry_category` 不在 ETF 類)— 排 ETF 505 檔 + roster 污染 31 項(產業名 'Automobile'/指數名 'TAIEX' 混入 stock_id)
2. **完整度關**:全 panel × 全 universal 特徵齊(pan-historical、缺列即排除、#1)
3. **流動性關**:`dollar_volume_log_20d ≥ latest panel P25`(動態分位、不寫死 #9)
4. **conditional 關**:`build_universe(conditional={feature:(豁免產業,)})` — 月營收對 `金融保險` 豁免完整度(金融業無月營收申報制度)

**pilot 演進(28-panel walk-forward、2014+ × 19 連續特徵、流動性 P25)**:roster 3105 → v1 1211(候選空間)→ v2 633(+月營收+流動性)→ v3 742(+籌碼+P/E教訓)→ **v4 875(兩 gate 修正)**;代表權值股 **10/10 全納入**。報告 reports/augur_phase78_core_universe_pilot_v1~v4。

**v4 兩 gate 正確性修正(commit `1a8fe01`、tag `gate-fixes-20260625`)**:
- **volatility robust**(`features/panel.py`):停牌 close=0→`log` 得 ±inf、`notna()` 擋不住 inf→`std` 含 inf 被 isfinite 濾掉→缺列;**1 天停牌誤殺整 volatility 窗、影響 ~126 股**(鴻海 2317 等)。正解＝最近 w 個 **finite 報酬**之 std(往前補足、無 magic number)。
- **conditional gate**(`core_gate.py`):月營收豁免金融保險→富邦金 2881/中信金等 +7(金融保險 26→33)。
- 相關:E 類真零(`features/chip.py`、tag `chip-e-truezero-20260625`):借券/官股稀疏事件無事件填中性 0(非缺列、前提＝表 sync 完整 #7)。

**F3 模型(`evaluation/`、另機 commit `08cfda0` 基於我的 `1a8fe01`)**:M-0 `label`/`metrics`/`walkforward` SSOT helpers + M-1 基準階梯(B0隨機/B1動能/B2 Ridge/GBDT)+ M-2 多週期;`core_gate.build_universe_asof`＝**point-in-time 核心快照表 `core_universe_asof`**(逐 as-of 用 ≤t panels 算完整度、消 survivorship #8、非 pan-historical 回填);F2c `features/valuation.py` 估值特徵。**關鍵成果:as-of Ridge H60 rank IC +0.132、Eff-t 6.13、勝率 0.96(25 panel 24 正)— alpha 為真**(遠超靈魂「rank IC 0.02-0.05 即實用」)。**已親讀 evaluation code 驗證口徑正確**(2026-06-26):purged walk-forward(expanding train→embargo→test 不回流)+ label t+1 進場 + as-of point-in-time(`build_universe_asof` 消 survivorship)+ rank IC;**最強證據＝as-of 消 survivorship 後 IC 不降反升(pan-hist 0.113→as-of 0.132、4 組全 as-of>pan-hist)→ alpha 非倖存者假象**;GBDT 4 組全輸 Ridge(非線性無增量);F2c 估值(低 PE→高報酬、方向符經濟學)是 alpha 主來源(五鏡證)。**caveat(非最終定論、待 M-3)**:①已下市股仍缺(as-of 只含現存 roster、survivorship 殘留)②單 seed(待≥3)③expanding 折重疊→Eff-t 可能高估 ④in-universe IC、經濟價值(top-N/MaxDD #14)未計。詳 reports/augur_evaluation_M1_baseline_20260626.md。

**Why**:核心股是 model 的 0 缺值乾淨輸入;兩 gate 修正讓核心正確涵蓋(代表股全納入、非偏嚴 742)。F3 IC+0.132 是 augur 核心目標(誠實預測台股)可達之關鍵驗證。
**How to apply**:核心股用 `build_universe`(pan-historical 單名單、含 look-ahead)或 `build_universe_asof`(walk-forward 嚴格 point-in-time);DB 成果(`core_universe` 875)**跨機獨立不進 git、永遠實查為準**[[db-cross-machine-independent]]。tag 序:gate-fixes-20260625 → chip-e-truezero → core-universe-* → evaluation-m2-asof-baseline-20260626。關聯 [[asof-completeness-per-table-verification]] [[rigor-completeness-discipline]]。
