# READOUT 檔名.ext＋中文問 · EXECUTED

date: 2026-08-12  
kind: bugfix_executed  
status: EXECUTED  
symptom: UI `(無回覆)` on `….ppt中，詳細說明XML 的作用`（兼撞 advisor 重啟 BrokenPipe）

## 根因
`extract_title_hint` 把整句當 ILIKE → readout **0 cite** → 落到慢 ANN；重啟時 client 斷線 → 空 SSE → `(無回覆)`。

## 修
- `readout.py`：`_EXT_THEN_ASK_RE` 切 `檔名.ext`＋後綴問句（非冒號路徑）  
- `serve_chat_ui.py`：空正文提示改為可重試說明  
- sess92：message **540** 補寫 XML 答；**541** 補寫啟動 server／process 步驟答（guard 過）

## 驗
`python -m augur.knowledge.readout --selftest` 全過；XML 題 cite → `1818820`／`1818830`。

## paste
```text
READOUT-EXT-THEN-ASK-EXECUTED | ppt+中文問 | cite=1818820 | sess92-patched
```
