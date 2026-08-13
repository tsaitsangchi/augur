# 清歷史 chat `(無回覆)` · GO

date: 2026-08-12  
kind: ops_go  
status: GO  
open: Steward 口令「GO 清歷史無回覆」

## 授權
1. 僅 `chat_message`：`role=assistant` 且 `content LIKE '(無回覆%'`  
2. 改寫為誠實作廢句（`guard_pass=false`）；**不刪** user 列；**不動** `knowledge_*`  
3. 可重跑：已作廢句不再匹配 `(無回覆%`

## 禁
整庫 KH 回填；改其他正常回覆；web approve。
