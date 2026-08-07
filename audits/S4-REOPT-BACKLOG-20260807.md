---
status: backlog
series: s4_reopt
date: 2026-08-07
viewpoint: 2026-08-07T08:00+08:00
trigger: LOOP-S5-TO-S4-OPT-run
prior: audits/S4-REOPT-BACKLOG-20260804.md
score_ssot:
  - audits/S5-OOS-20260804.md
  - audits/S5-OOS-VERIFY-EXECUTED-20260806.md
  - audits/S4-V1-REVERIFY-EXECUTED-20260806.md
layer: "[I]"
self_reported: true
---

# S4 再訓／再驗 backlog（S5→S4 · 刷新）· 2026-08-07

> **位階**：[I] · **本窗＝文件優先序**；**零**重訓／**零** APPLY／**零**假 pass。  
> **消費**：08-04 投組 OOS ＋ 08-06 V5 方向尺 ＋ 08-06 V1·H60 三 seed。  
> **LIVE**：B3＠**08-06** ✅；pp／pv 頂＝08-06；H20 `econ=dead`；`evaluated_pass=0`；NF-pause **keep**；價尚無 **08-07**。

---

## 優先序（下一 WAVE／錯峰）

| # | 動作 | 依據（本波） | 窗內？ |
|---|---|---|---|
| 1 | **維持** RankRidge **H60＞H20** 為 serve／#14 主尺 | V1 H60 B2 net Sharpe **1.25＞bench 1.10**（三 seed 同位）；生產仍掛 H60／H20 | **是**（docs；無重訓） |
| 2 | **不升格** M1_gbdt／RankGBDT | V1 #11：Sharpe **0.97／1.09／1.18**；**seed2＜bench**；禁單 seed 勝 | **STOP promote** |
| 3 | **ENS** 不升格生產 | V1 ENS∈[1.16,1.26]；貼近／內插 Ridge；既有 EVAL 未過門 | STOP |
| 4 | H40 **降優先**（方向／漲跌比臂） | S5-OOS：net hit **劣** bench；未重跑否定 | 優先序註記 |
| 5 | H120 **defer 升格** | S5-OOS n=8；V5 top20% 尺≠投組；勿終局 | backlog |
| 6 | H20：**服務續掛**但 **econ=dead 誠實** | B3＠08-06 emit 仍 dead；V5 確認 | 敘事；另 H20 V1 可選 |
| 7 | Direction 臂：**弱信号、不開 GATE 綠** | V5 DirStackM hit≈0.50–0.54；日頻≈0.51–0.55；pass=0 | 監，不修綠 |
| 8 | 可選 **H20 V1**（三 seed／#14） | 對稱 H60；Steward 另 `S4-V1-REVERIFY-go`＋horizon | ✅ **EXECUTED** `S4-V1-REVERIFY-H20-EXECUTED-20260807`（M1 全＜bench） |
| 9 | **V2 adapter 債**（XGB／…） | NF-pause；開訓須先 `NF-*-go-plan` | **禁**默開 |
| 10 | 軟對帳：H60 B2 vs 08-04（1.30／63%→1.25／58%） | 同 hash `ca1b6ff379`／active3；**非 byte 復現** | 可選 reproprobe；不改冠軍 |
| 11 | 下鑽 S3／C1／GRAPH G2 | 僅當特徵／圖消費被指為根因 | 旁軌另 GO |
| 12 | `predict-asof-write-go`／sim apply | **另句** | 未授 |

---

## 本窗最小安全 opt（已做＝文件）

1. 熱路徑優先確認：**H60＞H20≫H40**；H120 觀察；H20 死經濟標不隱瞞。  
2. GBDT／M1／ENS：**SKIP 升格**（artifact 可留對照）。  
3. 下一「其他模型」：**不是**新族，而是（a）可選 H20 V1，或（b）撤 pause 後 V2／V4。  
4. **零**新 train／零 registry APPLY／零寫庫／零改 dgate。

---

## 相對 08-04 backlog 的差分

| 項 | 08-04 | 08-07 |
|---|---|---|
| H60 B2 | 1.30／0.632 | V1 重跑 **1.25／58%**（同尺軟差） |
| M1 三 seed | hit＝bench | 勝率印高但 **Sharpe 含＜bench** → 仍不升格 |
| V5 方向 | （較少寫入 backlog） | 明確：**弱**、pass=0 |
| A＠08-06 | 未完 | **B3 完**；回饋可消費 live pp 敘事 |

*完。*
