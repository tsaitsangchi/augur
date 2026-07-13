---
name: no-concurrent-agents-same-files
description: 不要同時派兩個 background agent 改同一批檔案——會併發撞檔、且 agent 死活難判
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c3c40e0c-7154-4936-8937-6d9ce947808c
---

派 background agent 時,**不得讓兩個 agent 同時編輯同一批檔案**。

**Why**:2026-07-07 教訓——N9(跨語重建,改 advise.py/relevance.py)還在跑時,我誤判它「死了」(output 檔停在 129 bytes/舊 mtime),就 revert 它的改動 + 又派 D4 agent 改**同一個 advise.py**。結果 N9 其實還活著(output mtime 是假象、agent 仍在寫檔),兩個 agent 的改動在 advise.py 混在一起、D4 疊在未驗證的 N9 上,還得花大量工夫拆解驗證才敢收。

**How to apply**:
- 派 agent 前先確認**檔案集不重疊**;會碰同檔的任務**排序執行**(一個結算再派下一個),不並行。
- **不要用 output 檔 size/mtime 判 agent 死活**——background agent 的 transcript 檔 mtime 可能不即時更新,看起來 stale 不代表死。要停一個 agent 用 `TaskStop`(它回報最後狀態),別靠猜。
- 若真發生撞檔:先 `TaskStop` 所有相關 agent、`git status`/`git diff` 盤點混雜程度、逐 claim 獨立實證(尤 guard byte-identical、治權閘),分不開就 revert 到 HEAD 重做乾淨的那個。

相關:[[bounded-autonomy-mode]](執行層主動但碰護欄停)、[[rigor-completeness-discipline]](實證不憑「我以為死了」)。
