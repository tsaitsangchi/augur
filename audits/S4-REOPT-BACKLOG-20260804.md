# S4 再訓／再驗 backlog（S5→S4）· 2026-08-04

> **位階**：[I]  
> **觸發**：`LOOP-S5-TO-S4-OPT-go` · 分數 SSOT＝`audits/S5-OOS-20260804.md`  
> **硬禁**：本窗**不**重訓全 taxonomy；**不** APPLY；**不**假 pass

---

## 優先序（下一 WAVE／錯峰）

| # | 動作 | 依據 | 窗內？ |
|---|---|---|---|
| 1 | **維持** RankRidge H60／H20 為 serve／OOS 主尺 | hit＞bench＋Sharpe 優 | **是**（docs only；無重訓） |
| 2 | **降優先** H40 作方向／漲跌比臂 | hit 0.567＜bench 0.633 | **是**（優先序註記） |
| 3 | H120 **defer 升格**直至 n 或 folds 補強 | n=8；late fold 掉到 0.667 | backlog |
| 4 | RankGBDT：**不**挑戰生產；可留 artifact 作 #11 對照 | hit＝bench；Sharpe≈基準 | STOP promote |
| 5 | Wave A 殘：direction 臂（A-2a／A-D1／A-D2） | train-matrix 未含 | 下一刀／Wave A EXECUTED 收口 |
| 6 | H20 GBDT ≥3 seed OOS hit（本窗僅 H60） | 對稱 #11 | 下一 WAVE |
| 7 | 可選下鑽 S3／C1 | 僅當特徵覆蓋被指為根因——本窗**未**觸發 | defer |
| 8 | `predict-asof-write-go`／sim apply | **另句** | 未授 |

---

## 本窗最小安全 opt（已做＝文件）

1. 生產熱路徑優先：**H60＞H20≫H40**；H120 觀察帳。  
2. GBDT／RankGBDT：**SKIP 升格**（非 SKIP 測——artifact 已有）。  
3. **零**新 train／零 registry APPLY／零寫庫。

*完。*
