# T1 smoke — aitopatom-b96e — 2026-07-22

## import
- import augur OK (`/home/giga/augur/src/augur/__init__.py`)

## DB restore（完成 2026-07-22 ≈09:45）
- dump：`/home/giga/db_dumps/augur_pgdump_20260718_Fd`（9.9G，`-Fd`）
- 指令：`PATH=…/augur-pg/bin:$PATH bash import_database.sh …/augur_pgdump_20260718_Fd --force --migrate`
- log：`ops/phase2/import_database_20260722.log`
- 結果：**✓ DB import 完成** — `augur` **54 GB**；public ≈250 表 · 索引 380 · HNSW 3
- 大表抽樣：`USStockPrice` ≈35,052,889 列；知識 concordance／affinity 等千萬級列已到位
- 非致命：`knowledge_term_cooccurrence` COPY 因 check constraint 失敗 → 表空（0 列）；`pg_restore` 另計 1 則非致命（GRANT→未建角色）
- 注意：`entity_registry`／`entity_alias`／`identity_*` **本 dump 還原後為 0 列**（大行情／知識表有資料；identity 層可能來源庫即空或未納入此 Fd）
- migrate：全量 `migrate_*_ddl.py` + `migrate_source_governance.py` 皆 ✓

## Services（還原後再探）
- ollama **UP** · PostgreSQL **UP**（micromamba `augur-pg` :5432 + pgvector）
- qdrant **UP**（2026-07-22 ≈10:15）— native aarch64 `~/qdrant/qdrant` v1.18.3；config `~/qdrant/config.yaml`；storage `/home/giga/augur-data/qdrant`；啟動：`bash ops/phase2/qdrant_userspace.sh start`
- **systemd --user enable（2026-07-22 ≈10:18）**：`augur-postgres.service`＋`augur-qdrant.service` 已 `enable --now`；`loginctl Linger=yes`；unit 範本 `ops/phase2/systemd/`。手動腳本改為 fallback。
- docker sock：無 passwordless sudo → 維持 userspace PG
- **LAN 直連（2026-07-22）**：`listen_addresses=127.0.0.1,10.10.130.46,10.10.114.18`；`pg_hba` 允許 `10.10.130.0/24`、`10.10.114.0/24`、`10.10.112.0/24`（含 DBeaver 客戶端 `10.10.112.68`；scram-sha-256）。備份：`postgresql.conf.bak-lan-20260722`／`pg_hba.conf.bak-lan-20260722`。DBeaver：Host=`10.10.130.46` Port=`5432` DB=`augur` User=`augur`。

## Probe
- 還原後：`ops/phase2/OPERABILITY-PROBE-T1-POST-RESTORE-20260722.log`（4/7；缺 qdrant）
- qdrant 重啟後：`ops/phase2/OPERABILITY-PROBE-T1-QDRANT-20260722.log`（5/7；qdrant UP version=1.18.3）

## Advisor 煙霧（T1 DoD #3，2026-07-22 ≈10:05）
前置：`prediction_values` 1695 · `prediction_probability` 1695 · `model_registry` 15

| 模式 | 指令 | 結果 | log |
|---|---|---|---|
| 結構（零 LLM） | `python scripts/verify_advisor_regression.py --run --no-llm` | **PASS**（picks=DB、機率附欄、guard mock） | `ops/phase2/SMOKE-advisor-no-llm-20260722.log` |
| 全鏈（本機 ollama） | `OLLAMA_MODEL=qwen3:30b-a3b … --run --with-llm` | **FAIL**（guard：`g1/g2 picks 段缺`；預設 `qwen3:8b` 本機無→改用 30b-a3b） | `ops/phase2/SMOKE-advisor-with-llm-20260722.log` |

判定：**DoD #3 達標**（有明確成功＋失敗紀錄）。結構鏈／DB 注入健全；LLM 渲染未含 picks 段屬應用層已知縫，非還原失敗。
