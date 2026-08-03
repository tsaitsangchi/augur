# 今晚守門 checklist（2026-08-03）

> 位階：**[I]** 工具／操作清單（非治權 [N]）  
> 來源釘死：`ops/RUNBOOK-20260803-night.md` · `audits/MT6-OBSERVE-PREP-20260803.md` · step `reports/augur_optimization_step_plan_20260803.md` §1 · master M-T5／M-T6  
> 本包目標：今夜可獨立執行之指令釘死＋工具綠；**不**阻塞等到 22:5x、**不**搶 heavy_slot、**不**改 evolution driver、**不** `--allow-apply`

前置一律：

```bash
cd /home/hugo/project/augur && set -a && . ./.env && set +a
```

---

## M-T5 禁做清單（今晚紀律）

| 禁 | 理由 |
|---|---|
| 手動起 `run_evolution_iteration.py`／`eval_local_model.py` | 僅此二處取 heavy_slot；搶了＝23:00 cron 等滿 → rc=75 defer |
| 帶 `--allow-apply` | run 22 觀測窗；偷跑 apply＝驗收⑤紅 |
| 改 `run_evolution_iteration.py`／`verify_evolution_acceptance.py`／`run_philosophy_evolution.py` | 23:00 起跑到一半換碼＝結果不可歸因 |
| FinMind／FRED 額外呼叫、dim-sync、放量 audit | API 凍結／與 arena 正交；本包不碰 |
| 對 `evolution_*` 表之人工寫入（23:00–結輪） | 與 TWEVO 寫帳互搶 |
| 阻塞 `sleep` 等到 22:50 | #33；到點人跑或另掛提醒 |

可做：唯讀觀察、`--prerun`／`--morning`、讀 log、本 checklist 內指令。

---

## ~19:30｜attestation watchdog 不 relaunch

**讀哪個 log（現機親驗）**：實際寫入＝`~/audit_watchdog.log`（**不是** runbook 舊寫的 `~/logs/audit_watchdog.log`——該路徑目前不存在）。

```bash
tail -5 ~/audit_watchdog.log
# 或對照期望字樣：
grep -E '冷卻中|發車後夭折|relaunch' ~/audit_watchdog.log | tail -10
```

| 期望 | 禁止 |
|---|---|
| 「**冷卻中**」或「**⛔ 發車後夭折**」（M-G4 互斥） | 「relaunch 已送」／實際起 `audit_selfheal.sh` |

（甲案：12:07 FAIL 使 `recent_try≥1` → 態二擋發車，至 08-04 12:07 前後。）

---

## 22:5x｜prerun（**必須覆寫 CSV**）

```bash
venv/bin/python scripts/observe_twevo_run22.py --prerun
# → 覆寫 audits/prerun22_pending_snapshot_20260803.csv
```

- 現有 CSV（14:57 首輪）**存在但非最終**——仍須 22:5x 再跑一次覆寫（見 MT6 prep）。
- 今日午後若另跑驗證用 prerun，一律標「**非最終**」。

---

## 23:00｜cron 自動；只監看、不搶 slot

```text
0 23 * * 1-5 … run_evolution_iteration.py --run --slot-wait 10800 >> $HOME/logs/twevo.log
```

```bash
tail -f ~/logs/twevo.log          # 監看即可
# 勿手動再起 TWEVO；勿 --allow-apply
```

---

## 隔晨／結輪｜observe + audit

```bash
venv/bin/python scripts/observe_twevo_run22.py --morning --write-audit
# → audits/OPT-W0-RUN22-20260803.md
```

驗收期待：① run 22 `succeeded` ② superseded>0 ③ pending 全屬 22 ④ gain≠incomparable ⑤ 無 apply 偷跑。

---

## 就緒親驗（本包施作時 · 2026-08-03 ~15:3x）

| 項 | 結果 |
|---|---|
| `--selftest` | **rc=0**（四組純函式紅綠全過） |
| 無參數 status | `pending_auto=17` by_run=`{21:17}`；`superseded=0`；最新 `21/succeeded` |
| heavy_slot | PG holders=`[]`；`flock -n /tmp/augur_heavy_slot.lock` → **EMPTY** |
| kill switch | global／tw／lai／raw／sim 皆 **clear**；`effective[tw]=clear` |
| crontab TWEVO | `0 23 * * 1-5` … `--slot-wait 10800` → `~/logs/twevo.log`（hugo crontab 15 條） |
| prerun CSV | **在**（18 行＝header+17；mtime **14:57**）→ **仍須 22:5x 覆寫** |

護欄交叉：本包**不**當最終 prerun、**不** sim `--apply`、**不**改 systemd、**不** commit／push。
