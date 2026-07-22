# T1 smoke — aitopatom-b96e — 2026-07-22T09:21:36

## import
- import augur OK (`/home/giga/augur/src/augur/__init__.py`)

## DB connect
- connected: db=augur user=augur public_tables=0
- **blocker for full DoD**: empty schema — need dump from DESKTOP

## Dump transfer (run on DESKTOP=`PC002-S1800`)
```bash
mkdir -p ~/db_dumps
pg_dump -h 127.0.0.1 -U augur -d augur -Fc -f ~/db_dumps/augur_pg17_$(date +%Y%m%d).dump
# scp to GB10:
scp ~/db_dumps/augur_pg17_*.dump giga@aitopatom-b96e:/home/giga/db_dumps/
# on GB10:
cd /home/giga/augur && PATH=/home/giga/mamba/envs/augur-pg/bin:$PATH bash import_database.sh ~/db_dumps/augur_pg17_YYYYMMDD.dump --migrate
```

## Services
- ollama UP · qdrant UP · postgres UP (micromamba userspace, pgvector)
- docker sock: no passwordless sudo → userspace PG path used
