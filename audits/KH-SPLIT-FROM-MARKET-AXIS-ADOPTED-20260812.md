# KH-SPLIT-FROM-MARKET-AXIS-ADOPTED · 2026-08-12

date: 2026-08-12  
kind: nav_adopted  
status: ADOPTED  
decision: **所有 KH 專案／選刀退出市場主軸編排**

## 決策（Steward）
1. KH 與市場 tip／B3／hold-#1 **完全分軌**：互不為主軸、互不等待、互不附屬 ∥。  
2. KH 選刀 SSOT＝`reports/augur_kh_opt_stepwise_best_next_plan_20260812.md`。  
3. r14＝**市場（＋結構／凍結）**選刀；不再用「∥ KH／讓 B3 才開 KH」敘事。  
4. `augur_llm.lock`＝基礎設施互斥，**≠**市場指揮 KH。  
5. C1 EXPAND 若碰特徵／predict → **另 GO**，且標「非市場日更義務」。

## 落地
- 新建 KH 選刀專檔  
- 改 r14：抽離 KH 主編排、硬門去 KH 日曆耦  
- 改 KH readout／ingest-B：去「收盤讓 B3／∥市場主軸」開工條件  

## 驗收
- [x] 問「最佳下一步」若指市場 → 只答 tip／B3  
- [x] 問「KH 下一步」→ 只答 KH 專檔／S*  
- [x] 無「候 PriceAdj 才能開 KH」殘句於 KH SSOT  

## paste
```text
KH-SPLIT-FROM-MARKET-AXIS-ADOPTED | dual-SSOT
| market=r14 | kh=kh_opt_stepwise_20260812 | no-yield-to-B3-as-command
```
