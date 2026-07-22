#!/usr/bin/env bash
# Prefer systemd --user unit augur-postgres.service for linger boot; this script is manual fallback.
# T1：userspace PostgreSQL 17（micromamba）啟動／停止——免 sudo docker。
set -euo pipefail
export MAMBA_ROOT_PREFIX="${MAMBA_ROOT_PREFIX:-/home/giga/mamba}"
BIN="${MAMBA_ROOT_PREFIX}/envs/augur-pg/bin"
PGDATA="${PGDATA:-/home/giga/augur-data/postgres}"
LOG="${LOG:-/home/giga/augur-data/postgres.log}"
CMD="${1:-status}"

case "$CMD" in
  start)
    "$BIN/pg_ctl" -D "$PGDATA" -l "$LOG" -o "-p 5432" start
    "$BIN/pg_isready" -h 127.0.0.1 -p 5432
    ;;
  stop)
    "$BIN/pg_ctl" -D "$PGDATA" stop -m fast
    ;;
  status)
    "$BIN/pg_ctl" -D "$PGDATA" status || true
    "$BIN/pg_isready" -h 127.0.0.1 -p 5432 || true
    ;;
  *)
    echo "usage: $0 {start|stop|status}"; exit 1
    ;;
esac
