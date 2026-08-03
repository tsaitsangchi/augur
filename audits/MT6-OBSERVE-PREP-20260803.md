# M-T6 觀察帳預稿（2026-08-03）

> 位階：[I] · 工具就緒；**真正 prerun 時刻＝22:5x 再跑一次 `--prerun` 覆寫 CSV**  
> 腳本：`scripts/observe_twevo_run22.py` · runbook：`ops/RUNBOOK-20260803-night.md`  
> 今晚守門全文：`audits/NIGHT-GUARD-CHECKLIST-20260803.md`

## 已就緒

| 項 | 狀態 |
|---|---|
| `--selftest` | rc=0（隔晨五項純函式紅綠） |
| 首輪 `--prerun`（現查） | CSV 17 列＝run 21 全集；superseded=0；run=21/succeeded |
| 首輪 `--morning`（run 22 前） | **rc=1 四紅**＝工具先驗紅成立（尚未有 run 22） |
| `check_cmd_matrix` | 含本支；NEED=0 |

## 今晚操作（人／cron）

```bash
# ~22:5x（覆蓋本檔 CSV）
venv/bin/python scripts/observe_twevo_run22.py --prerun

# 23:00 cron 自動；守 M-T5：勿改 evolution driver、勿 --allow-apply、勿搶 heavy_slot

# 結輪後或隔晨
venv/bin/python scripts/observe_twevo_run22.py --morning --write-audit
# → audits/OPT-W0-RUN22-20260803.md
```

## 驗收期待（master 第 8 步）

① run 22 `succeeded` ② superseded>0（I5B）③ pending 全屬 22 ④ gain≠incomparable ⑤ 無 apply 偷跑
