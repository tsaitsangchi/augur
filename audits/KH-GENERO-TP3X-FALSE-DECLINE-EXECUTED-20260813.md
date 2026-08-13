# EXECUTED｜Genero TP3x Client 假「無此內容」修復

date: 2026-08-13  
kind: bugfix_executed  
status: EXECUTED  
go: audits/KH-GENERO-TP3X-FALSE-DECLINE-GO-20260813.md  
paste: "KH-GENERO-TP3X | item=1818824 | false-decline-gate | msg573-patched | advisor-reload"

## 診斷
| 項 | 結果 |
|---|---|
| 庫內 | **有** `1818824` Genero…Clinet端程式-for TP 3x.ppt；eligible；正文含 fglwsdl／Client 流程 |
| sess96 | user#572 貼標題（無 `.ppt`）→ asst#573「知識庫中無此內容」 |
| 根因 | **非缺件**。未登入／deny scope → 閉集句屬預期；**已登入有引文**時弱模型仍吐閉集句／guard-fail 改口閉集＝**假 decline** |

## 修
1. `compact_answer.ensure_cite_backed_response`／`extractive_cite_reply`：有 item 引文＋閉集句 → 有界摘錄  
2. `advise` compact／主路徑出閘呼叫  
3. `oai_compat._reply_text`：pass 假 decline 改摘錄；fail＋item cite／readout 不得謊稱無  
4. 補寫 `chat_message` **573**；重載 `:8399`

## 驗
- `compact_answer`／`oai_compat --selftest` 全過（含假 decline 兩則）  
- readout 標題 → `1818824`  
- msg573 開頭「依庫內原文…」且含 Client／fglwsdl 線索  

## 未做
- 未整庫 reingest；未放寬未登入 RBAC；未改 LLM 權重
