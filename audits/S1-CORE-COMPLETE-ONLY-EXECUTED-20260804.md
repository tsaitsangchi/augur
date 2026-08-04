# EXECUTED｜S1 核心股＝僅資料完整 · 2026-08-04

> **位階**：[I]  
> **定錨**：`audits/S1-CORE-COMPLETE-ONLY-20260804.md`  
> **Steward**：只取資料完整為核心個股；不完整排外  
> **指令**：`build_core_universe.py --since 2014-01-01 --liquidity-pct 25 --exempt-revenue-financial --asof`  
> **self-reported（#32a）**：數字＝(a) stdout／(b) DB

## 結果（RC=0）

| 項 | 重建前 | 重建後 |
|---|---|---|
| `core_universe`（pan-hist） | 244 股 | **225** 股／**38** 特徵 |
| `core_universe_asof` | 42,782 列／895 股／102 panel | **36,405** 列／**762** 股／**106** panel |
| 最新 as-of `2026-06-30` | 244 | **225** |
| 流動性閾值（log） | — | **14.8238…**（P25 動態） |
| 月營收金融豁免 | — | **True** |

as-of 核心數跨窗：**218…703**（晚→早區間見 log；最早 2014-12-31＝703；最新 2026-06-30＝225）。

## 含義

- **完整入／不完整排**：過閘＝source-pure 完整＋流動性地板＋（金融）月營收豁免；未過＝**不在核心**。  
- **取數層**（FinMind／FRED THAW／A1）**另軌**：本帳**零 API**；不因本句放量或 kill A1。  
- 預測仍 ⊥ live sync；訓練／OOS 吃 `core_universe_asof`。

## 路徑

- log：`/tmp/s1-core-20260804/build.log`  
- parent 計畫已補 §0.5 S1 第 5 點  

---

*完。EXECUTED。*
