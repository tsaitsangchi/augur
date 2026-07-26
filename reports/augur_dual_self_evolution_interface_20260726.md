# 雙軸自進化協作介面（TWEVO × LAIEVO）[I]

> **SSOT 已移轉（V2-P-yes，2026-07-26 hugo 拍板、登錄 `audits/V2-ADOPTED-SUNSET-20260726.md`）**：本檔之總控／介面契約 SSOT＝`augur_self_evolution_master_plan_v2_20260726.md`；本檔降為前身史料，衝突時以 v2 為準；v2 §0.6 明列本檔哪些段落作廢／修訂／撤回。

> **已升格為三軸**（2026-07-26，加入 RAWEVO 資料地基）：介面契約 SSOT 移至 `reports/augur_triple_self_evolution_master_plan_20260726.md`；本檔留為前身史料，`DUAL-IFACE-yes` 視為 `TRI-IFACE-yes` 之等價舊碼。衝突時以 triple master 之**更嚴邊界**為準。

> **性質**：[I] 介面／正交矩陣短檔（≤80 行）— **不創設 [N]**；拍板碼可選 `DUAL-IFACE-yes`  
> **主檔**：預測＝`reports/augur_tw_prediction_self_evolution_loop_plan_20260726.md` §8；advisor＝`reports/augur_local_ai_route_b_no_gpu_plan_20260726.md` §十二  
> **一句**：兩閉環、兩帳本、兩晉升閘；只共享**唯讀摘要契約＋通知＋錯峰**。

## 正交（禁）

| 禁 | 理由 |
|---|---|
| 混閉環／共用 iteration id 命名空間 | 假兆、錯歸因 |
| 共享晉升閘（APPLY⇔serving） | 監督空洞 |
| LLM 權重／teacher 答 → 預測特徵／prodset | #1／隔離／GATE-keep |
| raw panel／整庫 → 靈魂或 advisor「權威」 | soul↔raw；禁確立級話術 |
| 未過閘 IC 當確立級／可交易 | `evaluated_pass=0`；三敵 |
| 自動下單 | 靈魂紅線 |

## 允許流向

| 方向 | 允許 | 入口 |
|---|---|---|
| TWEVO→LAIEVO | ledger 結論、近失**特徵名**、settle 後 scoreboard 公開數、gap 路徑 | `export_evolution_advisor_brief`；LAIEVO `consumed_briefs` |
| LAIEVO→TWEVO | 假說文字／map curate **提示**（人閘後 PME） | `hypothesis_hints_out` → 人 → `curate_pme_map_expand` |
| 雙向通知 | kill／`stopped_no_gain` 寫 `cross_notify_json`；對偶只讀告警 | 各方 ledger；**不**連鎖自動閘 |
| 儀表 | 兩 ledger **並列** | `report_dual_evolution_week.py` |

## 錯峰

TWEVO `I3`／`I6` ∥ LAIEVO embed／B2／B3 — 同機滿載互斥；可 `--defer-heavy`。

## 拍板

| 同批 OK | 必須分開 |
|---|---|
| `TWEVO-P-yes`＋`LAIEVO-P-yes`＋`DUAL-IFACE-yes`＋`FZ-keep`＋`GATE-keep` | `TWEVO-APPLY-go` ≠ 人簽 serving |
| `TWEVO-S0/S1/S2`∥`LAIEVO-B0/B1/B4` | `TWEVO-S3/S4` ≠ `LAIEVO-B2-train`／`B3` |

**建議下一步**：先同批採納兩計畫＋介面 → 分軸 S0／B0（或 B1）。

*完。[I]*
