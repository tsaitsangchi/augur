# KH-ATA-SCHED＋FZ-keep 拍板登錄（2026-07-28）

> **性質**：拍板登錄（[I]；不創設 [N]）。  
> **hugo／Steward 對話拍板原文（逐字）**：`KH-ATA-SCHED`＋`FZ-keep`  
> **簽名誠實註記**：本檔由 agent 依 Steward 拍板繕寫登錄；決策者＝hugo、繕寫者＝agent，二者分立。  
> **相關**：ATA 骨架＝`scripts/advance_knowledge_terminal.py`（KH-XDOM S1b）；計畫脈絡＝`reports/augur_knowhow_cross_domain_advisor_plan_20260728.md`

## 一、採納範圍（本輪）

| 碼 | 含義 | 本輪 |
|---|---|---|
| **`KH-ATA-SCHED`** | systemd user timer 定期跑**庫內** ATA：`advance_knowledge_terminal.py --apply --limit N`＋既有 sentences／embed 銜接 | ✅ 核准並執行 |
| **`FZ-keep`** | 零 FinMind／FRED；維持市場 API 凍結 | ✅ |
| **`KH-ATA-EXEC`** | 外部 OA／fetch 放量 | ❌ **不含**（另句） |
| **來源 approve／activate／HUMAN_ONLY** | timer／service 路徑 | ❌ **硬禁** |

## 二、驗收錨

- unit：`augur-ata-advance.service`＋`.timer`（`install_services.sh` 生成；日誌＝`~/ata_advance.log`）
- 節奏合理、limit 有界（勿過猛）
- `systemctl --user enable --now`＋`list-timers` 可見
- dry-run 證明指令清單**不含** approve／activate／fulltext
- HANDOFF 一句；封存 `archive_push.sh --slug kh-ata-sched`

## 三、硬邊界

| 項 | 本輪 |
|---|---|
| 零 FinMind／FRED | ✅ |
| 不含外部 OA 放量 | ✅ |
| timer 不呼叫來源 approve／activate | ✅ |
| 素養層不進預測 | ✅（未碰 predict） |

## 四、執行落點

- 收官：`audits/KH-ATA-SCHED-CLOSED-20260728.md`
