# Roadmap R6 計畫拍板登錄 [I]（2026-07-24）

* Steward 原文：`R6-P-yes`＋`R6-E12`＋`HAR-local`＋`FZ-keep`
* 計畫書：`reports/augur_roadmap_r6_plan_20260724.md`（§10 拍板句；文首「Steward 已拍板」）
* 路線圖：`reports/augur_constitution_to_implementation_roadmap_20260724.md` §3.7／總表 R6

## 效力

| 項 | 狀態 |
|---|---|
| 計畫採納 | ✅ 本檔＝R6 執行藍圖 |
| 執行授權 | ❌ **未開**（另待 Steward「**開 R6**」） |
| 執行範圍（預選） | `R6-E12`＝S1＋S2；`HAR-local`；**S3／U6／HAR-ext 未授權** |
| FinMind／FRED 凍結 | ⚠ **FZ-keep＝凍結維持**（`.cursor/rules/finmind-fred-api-freeze.mdc`；計畫拍板 ≠ 解凍） |
| Dividend 邊界 | ⚠ API 線 PAUSED；不續重建 |

## 四碼展開

| 碼 | 含義 |
|---|---|
| **R6-P-yes** | 採納計畫為 R6 執行藍圖；實作另待「開 R6」 |
| **R6-E12** | 開實作時預選 S1＋S2（終態＋本地暢通／隔離哨兵；零市場 API；零知識外部放量）— **本輪未跑** |
| **HAR-local** | 僅本地／manual／owned_local／庫內消費 |
| **FZ-keep** | R6 不解凍 FinMind／FRED；Dividend 維持 PAUSED |

## 下一步

Steward 明示「**開 R6**」後才實作（預選＝`R6-E12`＋`HAR-local`＋`FZ-keep`）；仍禁 FinMind／FRED、仍禁 metadata 當可答、仍禁假關 G-KDO／10-14。
