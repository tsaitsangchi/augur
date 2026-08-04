# EXECUTED｜LOOP-S5-TO-S4-OPT · 2026-08-04

> **位階**：[I] 執行帳（**partial／STOP+backlog**——非全 taxonomy 重訓）  
> **GO**：`audits/LOOP-S4-S5-FULL-GO-20260804.md`  
> **前置**：S5 分數已存在＝`audits/S5-OOS-20260804.md` · `audits/LOOP-S4-TO-S5-EXECUTED-20260804.md`  
> **WAVE-A**：train-matrix DONE；**尚無** `S4-WAVE-A-EXECUTED*`（方向臂未入本矩陣）→ 本帳 **不**代寫 Wave A 收口

---

## 1. 做了什麼

| 項 | 結果 |
|---|---|
| 讀 S5 OOS 分數表 | ✅ |
| 重排 horizon／族優先（文件） | ✅ → `audits/S4-REOPT-BACKLOG-20260804.md` |
| 最小安全 opt（in-window） | ✅ **僅** docs：H60/H20 主尺；H40 降權；GBDT 不升格 |
| 重訓／換掛／APPLY | **未做**（STOP） |
| 全 taxonomy 再訓 | **未做**（禁） |

---

## 2. 建議一句

**下一 WAVE**：方向臂補齊＋H120 樣本／folds 補強；**本窗不重開** RankRidge／GBDT 訓練矩陣（Wave A 已落地）。

---

## 3. 狀態標籤

| 標籤 | 含義 |
|---|---|
| **EXECUTED（opt-docs）** | backlog＋優先序落地 |
| **STOP（retrain）** | 無 in-window 重訓 |
| **WAIT** | `S4-WAVE-A-EXECUTED*`／direction 臂正式收口 |

*完。self-reported（#32a）。*
