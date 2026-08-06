---
status: executed
series: kh0_kh9
wave: "Κ0.1 / BREACH-DRAIN"
date: 2026-08-06
viewpoint: 2026-08-06T09:34+08:00
go: audits/KH0-BREACH-DRAIN-GO-20260806.md
log: /tmp/kh0-breach-drain/run.log
self_reported: true
---

# EXECUTED｜KH0-BREACH-DRAIN · 2026-08-06

```text
KH0-BREACH-DRAIN-go | FZ/GATE-keep | --phase advance | limit=5000 | no-activate-source
# RC=0 · ~25s · seeded=5000
```

## 1. 碼要件（本 GO 內最小修正）

| 變更 | 何以必要 |
|---|---|
| `list_candidate_item_ids` | 納 title／破口優先——舊 JOIN 全文**永遠掃不到** ~139k 破口 |
| `seeded` 計數 | 標題件 KH0 後停在 depth0；`after==before==0` 不得當卡死 |
| `--no-activate-source` | 本輪零機械 approve／activate |

自測：`python -m augur.knowledge.auto_admit --selftest` ✓

## 2. 本輪結果

| 尺 | 前 | 後 |
|---|---:|---:|
| kh0_breach | **138,999（48.7%）** | **133,999（47.0%）** |
| Δ | | **−5,000** |
| admit_depth=0 | （無） | **5,000** |
| done | | ok=5000 · advanced=0 · **seeded=5000** · held=0 |

指令：

```bash
venv/bin/python scripts/run_knowhow_auto_admit.py \
  --apply-up-to 9 --limit 5000 --no-activate-source
```

（未走 `run_kh_chain --until-empty` 單輪限量；避免與 data 段混跑。）

## 3. 門／旁軸

| 項 | 狀態 |
|---|---|
| #1 watcher | ALIVE · WAIT（未搶 B3） |
| KH8 鑑別力 | 仍 False（未動尺） |
| KH3 domain | **未開** |
| NF／approve | **未動** |

## 4. 下一步（Steward 已宣告方向；本裁未授）

1. 續 Drain（多輪 limit=5000）直至破口→0 — 另句或同 paste 加輪  
2. `KH3-FT-DOMAIN-go`（分域終態）  
3. `KH8-DISCRIM-go-plan`（判準層）

*完。*
