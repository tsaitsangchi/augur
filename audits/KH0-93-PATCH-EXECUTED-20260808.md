---
status: executed
series: local_ai_kh
kind: kh0_breach_patch
date: 2026-08-08
viewpoint: 2026-08-08T20:45+08:00
go: audits/KH0-93-PATCH-GO-20260808.md
board: audits/KH-LOOP-BOARD-REFRESH-20260808.md
log: /tmp/kh0-93-patch/run.log
paste: "KH0-93-patch | FZ/GATE-keep | --apply-up-to 0 | limit=200 | --no-activate-source | hold-#1"
self_reported: true
layer: "[I]"
---

# EXECUTED｜KH0-93-patch · 2026-08-08

```text
KH0-93-patch | FZ/GATE-keep | --apply-up-to 0 | seeded=93 | kh0_breach 93→0 | hold-#1
```

## 結果

| 尺 | 前 | 後 |
|---|---:|---:|
| kh0_breach | **93**（biology 標題／無全文） | **0** ✓ |
| seeded | | **93** |
| admit_depth=0 | 138,949 | **139,042**（+93） |
| advanced／activate | | 0／未開 |

## 碼補丁（本窗必要）

`list_candidate_item_ids`：`--apply-up-to 0`／`--apply-raw` 時，`COALESCE(無列→0) < 0` 永空。  
→ `max_depth_lt<=0` 改掃 **僅無 state**。自測加鎖；全通過。

指令：

```bash
venv/bin/python scripts/run_knowhow_auto_admit.py \
  --apply-up-to 0 --limit 200 --no-activate-source
# check → KH0 破口 0
```

## 未動

市場 hold-#1／watcher；KH8 鑑別力 False；全量 PDF；AUTO-LIFT；approve／activate。

## 下一步候選（另授）

1. `#1c` AUTO-LIFT 試點  
2. `KH8-DISCRIM-go-plan`  
3. `#3` 治權抽樣  
4. `PDF-C-P2-go` 有界 ≠全量  
5. hold｜等 08-10 B3

*完。*
