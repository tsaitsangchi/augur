"""augur 系統內部表 schema — infra log 表 DDL + 從 DB 推導任一表 schema 的 helper。

🎯 這支在做什麼（白話）：管兩件「系統內部表 / schema 查詢」的事（不碰 API 原始表）：
1. **infra log 表 DDL**（憲章第五部 PHASE 1「Infra bootstrap」）：
   - `pipeline_execution_log`：每次任務跑了什麼、成敗、幾列、起訖時間。
   - `data_audit_log`：哪個 dataset / 哪支股、做了什麼寫入或對帳、幾列。
   這兩張是**系統自己產生的運維表**（非 API 回應）→ 沒有 API schema 可推 → 用 **explicit DDL** 建
   （不走 generic auto-schema）。`bootstrap_infra(cur)` 建它們（冪等）。
2. **DB-derived schema helper**：
   - `get_dataset_columns(cur, table)`：從 `information_schema` 查任一表的 {欄位: 型別}。
   - `get_dataset_keys(cur, table)`：查該表的 PRIMARY KEY 欄（委派 generic_schema，不重複實作）。
   下游（reconcile / builder）藉此取得「這張表現在長怎樣」，**以 DB 為準、不另立手維白名單**（#2）。

邊界：不抓 API、不算特徵、不選股；**不建 API 原始表**（那是 generic_schema 的職責）。
infra log 表用**運維型別**（BIGSERIAL / TIMESTAMP / TEXT）——#5 的 VARCHAR(255)/NUMERIC(20,6) 是給
**API 資料表**的規則，系統內部運維表自訂明確型別。

守 #2（schema 以 DB 為準 / 不另立白名單）· 核心橫切基礎（infra 表 DDL + DB-derived schema 單一引用源，#12）。

自測（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.core.schema              # 印用途+公開入口（唯讀）
  python -m augur.core.schema --selftest   # 純紅綠自測（零 IO）
"""
from __future__ import annotations

from augur.core import generic_schema

# ── infra log 表（憲章 PHASE 1；系統內部運維表，explicit DDL，非 API auto-schema）──
INFRA_DDL = {
    "pipeline_execution_log": """
        CREATE TABLE IF NOT EXISTS pipeline_execution_log (
            id          BIGSERIAL PRIMARY KEY,
            task        VARCHAR(255) NOT NULL,
            target      VARCHAR(255),
            status      VARCHAR(255) NOT NULL,
            rows        BIGINT,
            started_at  TIMESTAMP NOT NULL DEFAULT now(),
            ended_at    TIMESTAMP,
            detail      TEXT
        )""",
    "data_audit_log": """
        CREATE TABLE IF NOT EXISTS data_audit_log (
            id          BIGSERIAL PRIMARY KEY,
            dataset     VARCHAR(255) NOT NULL,
            data_id     VARCHAR(255),
            action      VARCHAR(255) NOT NULL,
            rows        BIGINT,
            logged_at   TIMESTAMP NOT NULL DEFAULT now(),
            detail      TEXT
        )""",
    # #7 attestation verdict 留檔(2026-07-14 (a) hugo 拍板):正典驅動(daily_maintenance --audit-only --heal)
    # 對帳跑完寫一列;E1 gate 之 sql check 讀「最近 PASS 且夠新」——run(慢、async)與 gate 檢查(快、讀表)解耦。
    "attestation_result": """
        CREATE TABLE IF NOT EXISTS attestation_result (
            id             BIGSERIAL PRIMARY KEY,
            run_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
            driver         VARCHAR(64) NOT NULL,
            passed         BOOLEAN NOT NULL,
            matched        BIGINT,
            value_mismatch INT,
            extra_in_db    INT,
            missing_in_db  BIGINT,
            exempt_n       INT,
            sampled_n      INT,
            coverage_gap_n INT,
            incomplete_n   INT,
            audit_since    VARCHAR(16),
            note           TEXT
        )""",
    # AUD-02 補正:heal 覆寫前「被取代原值」快照帳本(P4.E5 矛盾保存、MUST NOT last-write-wins)。
    # store() 於 heal 路徑依賴其存在故納 INFRA_DDL(bootstrap 建表本體;append-only/truncate trigger + tombstone
    # 受控函式 + REVOKE 由 scripts/migrate_raw_supersede_ddl.py 硬化——bootstrap 只需表在、INSERT 不受 trigger
    # 擋;未硬化前 _snapshot_superseded fail-loud 拒絕落地，見 generic_schema._assert_append_only)。
    # **本 DDL 為表本體單一權威(issue 10)**:migrate 腳本引用本常數、不另手維 CREATE TABLE。
    # FK→attestation_result 故須排在其後(dict 序=建表序)。attestation_run_id 決策 B nullable(heal 直呼 sync
    # 無對帳 run 時結構上恆 None、非待回填);actor=P4.E6 斷言主體(產生此覆寫斷言之 agent/code 身分),reason=產生活動。
    "raw_supersede_log": """
        CREATE TABLE IF NOT EXISTS raw_supersede_log (
            id                 BIGSERIAL   PRIMARY KEY,
            "table"            TEXT        NOT NULL,
            pk                 JSONB       NOT NULL,
            old_row            JSONB       NOT NULL,
            new_row            JSONB       NOT NULL,
            superseded_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
            valid_time         DATE,
            reason             TEXT        NOT NULL,
            attestation_run_id BIGINT      REFERENCES attestation_result(id),
            actor              TEXT,
            note               TEXT
        )""",
}


def bootstrap_infra(cur):
    """建立 infra log 表（憲章 PHASE 1）；冪等（CREATE IF NOT EXISTS）。回傳已確保之表名 list。"""
    for ddl in INFRA_DDL.values():
        cur.execute(ddl)
    return list(INFRA_DDL)


# ── DB-derived schema（#2：以 DB 為準，不另立白名單）──
def _pg_type(data_type, char_len, precision, scale):
    """information_schema 欄位資訊 → 還原成 PG 型別字串。"""
    dt = data_type.upper()
    if dt in ("CHARACTER VARYING", "VARCHAR"):
        return f"VARCHAR({char_len})" if char_len else "VARCHAR"
    if dt == "NUMERIC":
        return f"NUMERIC({precision},{scale})" if precision is not None else "NUMERIC"
    if dt == "TIMESTAMP WITHOUT TIME ZONE":
        return "TIMESTAMP"
    return dt  # DATE / TEXT / BIGINT / INTEGER / BOOLEAN …


def get_dataset_columns(cur, table):
    """{col: pg_type_str}，依該表在 DB 之實況（information_schema，按欄序）；表不存在 → {}。"""
    cur.execute(
        "SELECT column_name, data_type, character_maximum_length, numeric_precision, numeric_scale "
        "FROM information_schema.columns WHERE table_name=%s ORDER BY ordinal_position",
        (table,))
    return {r[0]: _pg_type(r[1], r[2], r[3], r[4]) for r in cur.fetchall()}


def get_dataset_keys(cur, table):
    """表之 PRIMARY KEY 欄（依序）；無表/無 PK → []。委派 generic_schema（#12 不重複實作）。"""
    return generic_schema.db_primary_key(cur, table)


def _selftest():
    """自測（零 DB/零 API、可個別驗證 #29a）：純函式紅綠測 _pg_type（型別還原不變式）+
    INFRA_DDL 結構斷言 + DB-derived helper 公開名存在（IO-bound、僅 hasattr smoke）。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    # _pg_type：information_schema 欄資訊 → PG 型別字串（核心不變式，零 IO）
    chk("_pg_type VARCHAR 帶長度", _pg_type("character varying", 255, None, None) == "VARCHAR(255)")
    chk("_pg_type VARCHAR 無長度→裸 VARCHAR", _pg_type("character varying", None, None, None) == "VARCHAR")
    chk("_pg_type NUMERIC 帶精度", _pg_type("numeric", None, 20, 6) == "NUMERIC(20,6)")
    chk("_pg_type NUMERIC 無精度→裸 NUMERIC", _pg_type("numeric", None, None, None) == "NUMERIC")
    chk("_pg_type TIMESTAMP 去時區", _pg_type("timestamp without time zone", None, None, None) == "TIMESTAMP")
    chk("_pg_type 其餘型別大寫直通", _pg_type("date", None, None, None) == "DATE"
        and _pg_type("bigint", None, None, None) == "BIGINT")
    # INFRA_DDL：四張運維表、皆冪等 CREATE、皆帶 PK（explicit DDL 結構鎖；AUD-02 補入 raw_supersede_log）
    chk("INFRA_DDL 含 pipeline_execution_log + data_audit_log + attestation_result + raw_supersede_log",
        set(INFRA_DDL) == {"pipeline_execution_log", "data_audit_log", "attestation_result", "raw_supersede_log"})
    # raw_supersede_log 之 FK 標的須先建 → dict 序中 attestation_result 早於 raw_supersede_log
    chk("raw_supersede_log 排在 attestation_result 之後（FK 建表序）",
        list(INFRA_DDL).index("attestation_result") < list(INFRA_DDL).index("raw_supersede_log"))
    chk("INFRA_DDL 皆 CREATE IF NOT EXISTS（冪等）",
        all("CREATE TABLE IF NOT EXISTS" in ddl for ddl in INFRA_DDL.values()))
    chk("INFRA_DDL 皆含 PRIMARY KEY", all("PRIMARY KEY" in ddl for ddl in INFRA_DDL.values()))
    # DB-derived helper（IO-bound）：公開入口存在（import-smoke，不觸 DB）
    chk("公開入口皆存在", all(callable(g) for g in
        (bootstrap_infra, get_dataset_columns, get_dataset_keys)))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.core.schema --selftest;免 DB 免 API)")
