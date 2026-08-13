# 無回覆／檔名+問句 系統硬化 · EXECUTED

date: 2026-08-12  
kind: bugfix_executed  
status: EXECUTED  
symptom: `….ppt提到…`／`….ppt中，…` → UI `(無回覆)`；同型反覆

## 根因族
1. readout 整句當檔名 → 0 cite（先前 EXT-THEN-ASK）  
2. 長答 SSE **無 heartbeat** → 空線／重啟 → 空包仍寫庫成 `(無回覆)`  
3. 引文錨到文首「Server」字樣，未到 `fgl_ws_server_start` 段  

## 修
| 層 | 改 |
|---|---|
| `readout` | 檔名.ext＋問句；ask 種子詞；密度＋`fgl_ws` 加權錨點；多 seq 併文 |
| `compact_answer.freeze` | `prefer_terms` 密高優先 |
| `oai_compat` | **所有** stream worker＋15s heartbeat；BrokenPipe 不炸 |
| `serve_chat_ui` | 空包／`(無回覆*` **不寫庫**；errcard＋重試 |
| sess92 | 542／543 補正確答 |

## 驗
`readout`／`compact_answer` selftest 全過；server 題 cite 含 `fgl_ws_server_start`。

## paste
```text
NO-REPLY-FILENAME-ASK-HARDENING | sse-hb | no-persist-empty | prefer-fgl_ws | sess92-ok
```
