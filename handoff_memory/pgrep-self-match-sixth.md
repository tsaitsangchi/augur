---
name: pgrep-self-match-sixth
description: pgrep -f 命中自己的 bash wrapper——2026-08-02 一日三犯（第六犯）；正法唯 /proc/<pid>/comm 過濾
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b877d307-e736-407a-aa6a-200f3758f684
  modified: 2026-08-02T14:21:41.899Z
---

**`pgrep -f "<pattern>"` 會命中執行該指令的 bash wrapper 自身**——Claude Code 的 shell 把整條指令包進 `bash -c 'eval …'`，pattern 出現在 wrapper 的 cmdline 裡。

**2026-08-02 一日三犯**（全專案累計第六犯，屬 [[guard-mechanisms-that-silently-fail]] 之「掃到自己」家族）：
1. `pgrep -f pytest` → 誤判「pytest 仍在跑」，實際首發已因 `--timeout` 旗標啟動即死＝**假跑**（真結果 260 passed 是重發後才有）。
2. DDL 窗前檢 `pgrep -f "run_evolution_iteration|run_philosophy"` → 誤報「⚠引擎在跑!」，實際 run 21 早已結輪。
3. `pgrep -af "project_memory_mcp index"` → 誤判索引存活，實際進程已死、log 從未產生。

**正法**（唯一可靠）：逐 pid 讀 `/proc/<pid>/comm` 過濾出真執行檔名——
```bash
for p in $(pgrep -f "<pattern>"); do c=$(cat /proc/$p/comm 2>/dev/null); \
  [ "$c" = "python3" ] && echo "$p $(tr '\0' ' ' < /proc/$p/cmdline | cut -c1-60)"; done
```
先例：`backfill_evolution_run_zombies.py` 之 `_engine_alive()` 已用此法（2026-08-01 同因修過一次——**修過的坑仍在別處重踩，因為正法沒有住所**）。

**判斷句**：「這個 pgrep 命中的，會不會就是我自己？」——只要 pattern 是我剛打進去的字串，答案永遠是「會」。

同型還有 `grep -c` 掃到程式自己的輸出（`✗ 未更新任何列`）、掃描器掃到自己的說明字串（check_false_assertions／check_vendor_binding 皆已加自檔豁免）。
