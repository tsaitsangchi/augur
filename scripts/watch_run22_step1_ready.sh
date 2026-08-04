#!/usr/bin/env bash
# 🎯 唯讀監看 run22 結輪 → 寫 Step1-ready sentinel（喚醒＝auto）
# 守：不搶 heavy_slot、不 --allow-apply、不 --write-audit、不開 triage
# 超時 8h → 寫 RUN22-WATCH-TIMEOUT audit 後退出

set -u
REPO="${REPO:-/home/hugo/project/augur}"
cd "$REPO" || exit 1
set -a
# shellcheck disable=SC1091
[ -f .env ] && . ./.env
set +a

INTERVAL_SEC="${INTERVAL_SEC:-240}"   # 4 min
TIMEOUT_SEC="${TIMEOUT_SEC:-28800}"   # 8h
READY_SENTINEL="$REPO/audits/RUN22-READY-FOR-STEP1-20260804.md"
TIMEOUT_AUDIT="$REPO/audits/RUN22-WATCH-TIMEOUT-20260804.md"
PY="${REPO}/venv/bin/python"
LOG_TAG="[run22-step1-watch]"

START_EPOCH=$(date +%s)
START_ISO=$(date -Iseconds)
echo "$LOG_TAG START pid=$$ at $START_ISO interval=${INTERVAL_SEC}s timeout=${TIMEOUT_SEC}s"
echo "$LOG_TAG ready_sentinel=$READY_SENTINEL"

# Already ready?
if [[ -f "$READY_SENTINEL" ]]; then
  echo "$LOG_TAG already have sentinel; exit 0"
  exit 0
fi

check_once() {
  "$PY" - <<'PY'
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

REPO = Path("/home/hugo/project/augur")
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "scripts"))

TZ8 = timezone(timedelta(hours=8))
now = datetime.now(TZ8).strftime("%Y-%m-%d %H:%M:%S%z")

try:
    from augur.core import db
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT run_id, status, started_at, finished_at FROM evolution_run WHERE run_id=22"
        )
        row22 = cur.fetchone()
        cur.execute(
            "SELECT run_id, status FROM evolution_run ORDER BY run_id DESC LIMIT 1"
        )
        latest = cur.fetchone()
except Exception as e:
    print(f"DB_ERR {type(e).__name__}: {e}", flush=True)
    sys.exit(2)

status22 = row22[1] if row22 else None
fin22 = row22[3] if row22 else None
latest_id, latest_st = (latest[0], latest[1]) if latest else (None, None)
print(
    f"PROBE now={now} run22_status={status22!r} run22_finished={fin22!r} "
    f"latest=({latest_id},{latest_st})",
    flush=True,
)

# Use observe CLI for authoritative morning (stdout only)
import subprocess
r = subprocess.run(
    [str(Path("/home/hugo/project/augur") / "venv" / "bin" / "python"),
     "scripts/observe_twevo_run22.py", "--morning"],
    cwd="/home/hugo/project/augur",
    capture_output=True,
    text=True,
    timeout=120,
)
print("--- morning_rc=%s ---" % r.returncode, flush=True)
out = (r.stdout or "") + (r.stderr or "")
# keep last ~40 lines
lines = out.strip().splitlines()
for ln in lines[-40:]:
    print(ln, flush=True)

# Decision:
# A) morning rc==0 → full ready
# B) else latest run_id==22 and status==succeeded → min ready
min_ready = (latest_id == 22 and latest_st == "succeeded") or (
    status22 == "succeeded"
)
full_ready = (r.returncode == 0)

if full_ready or min_ready:
    kind = "full_morning" if full_ready else "min_succeeded"
    print(f"READY kind={kind}", flush=True)
    sentinel = Path("/home/hugo/project/augur/audits/RUN22-READY-FOR-STEP1-20260804.md")
    body = f"""# RUN22 READY FOR STEP1 [I]（{now}）

> **位階**：[I] 機械提醒 sentinel（非自動開 triage、非自動 write-audit）。  
> **觸發**：Step1 喚醒＝**auto**（`OPT-STEP-R2-20260804`）。

## 判定

| 項 | 值 |
|---|---|
| 時刻 | `{now}` |
| 判定種 | `{kind}` |
| run22 status | `{status22}` |
| run22 finished_at | `{fin22}` |
| latest (run_id, status) | `({latest_id}, {latest_st})` |
| observe --morning rc | `{r.returncode}`（**未** --write-audit） |

## 查詢證據（stdout 摘）

```
PROBE now={now} run22_status={status22!r} run22_finished={fin22!r} latest=({latest_id},{latest_st})
morning_rc={r.returncode}
```

```
{chr(10).join(lines[-25:])}
```

## 建議（人執行；本監看不代跑）

```bash
cd /home/hugo/project/augur && set -a && . ./.env && set +a
venv/bin/python scripts/observe_twevo_run22.py --morning --write-audit   # Step0 收口
# 再開 Step1 65 triage（唯讀）——勿自動
```

## 監看元資料

見 `audits/OPT-STEP-R2-20260804-GO.md`「監看已掛」段。
"""
    sentinel.write_text(body, encoding="utf-8")
    print("STEP1_READY run22 succeeded", flush=True)
    print(f"WROTE {sentinel}", flush=True)
    sys.exit(0)

# terminal failure of run22 — still ping with note? User asked succeeded path.
if status22 in ("failed", "aborted", "timeout") or (
    latest_id == 22 and latest_st in ("failed", "aborted", "timeout")
):
    print(f"TERMINAL_NON_SUCCESS status22={status22} latest={latest_st}", flush=True)
    # do not write READY; keep watching until timeout (honesty)
    sys.exit(1)

sys.exit(1)
PY
}

while true; do
  now_epoch=$(date +%s)
  elapsed=$((now_epoch - START_EPOCH))
  if (( elapsed >= TIMEOUT_SEC )); then
    ts=$(date -Iseconds)
    cat > "$TIMEOUT_AUDIT" <<TOE
# RUN22 WATCH TIMEOUT [I]（${ts}）

> 監看 pid=$$ 達上限 ${TIMEOUT_SEC}s（約 8h）仍未判定 Step1-ready。

| 項 | 值 |
|---|---|
| 開始 | ${START_ISO} |
| 結束 | ${ts} |
| elapsed_sec | ${elapsed} |
| interval_sec | ${INTERVAL_SEC} |
| ready_sentinel | 未寫 |

下一步：人工查 \`evolution_run\` run_id=22／\`observe_twevo_run22.py --morning\`。
TOE
    echo "$LOG_TAG TIMEOUT elapsed=${elapsed}s wrote $TIMEOUT_AUDIT"
    exit 3
  fi

  if [[ -f "$READY_SENTINEL" ]]; then
    echo "$LOG_TAG sentinel appeared externally; exit 0"
    exit 0
  fi

  echo "$LOG_TAG tick elapsed=${elapsed}s $(date -Iseconds)"
  set +e
  check_once
  rc=$?
  set -e
  if [[ $rc -eq 0 ]]; then
    echo "$LOG_TAG done ready rc=0"
    exit 0
  fi
  echo "$LOG_TAG not ready rc=$rc; sleep ${INTERVAL_SEC}"
  sleep "$INTERVAL_SEC"
done
