# GO｜Genero TP3x Client PPT 假「無此內容」

date: 2026-08-13  
kind: go  
auth: "Steward：Genero Web Services 教育訓練(Clinet端程式-for TP 3x)／知識庫中無此內容。請處理"

## 事實
- 庫內 **已有** `item_id=1818824`（`public`／`public_domain`／KH4 `eligible`）
- sess96 msg572 問無副檔名標題 → msg573 回「知識庫中無此內容」（~4.5min）
- 根因：**非缺件**；有引文時弱模型／guard-fail 仍落誠實閉集句＝**假 decline**

## 准許
1. 機器閘：有 item 引文卻吐閉集句 → 有界摘錄（`ensure_cite_backed_response`）
2. 補寫 msg573；重載 advisor 殼載入閘
3. **不**整庫 reingest；**不**放寬未登入 RBAC

## 驗
- `advise_readout_citations(標題)` → 1818824
- 假 decline 自測綠；msg573 ≠「知識庫中無此內容」
