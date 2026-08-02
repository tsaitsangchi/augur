#!/usr/bin/env python3
"""🎯 把 world_concept_registry 拆成「身分表＋版本表」——人類簽核從 UPDATE 變成 INSERT。

丙案（Steward 2026-08-03 圈選;裁決登錄住 reports/w2_20260801/WM_M1_pk_vs_appendonly_20260802.md 文末）：
概念之**身分**（concept_key）與**內容版本**（其餘欄）拆表——身分表持自然鍵真 PK 供外鍵參照、版本表持
(concept_key, transaction_time) 複合鍵真 append-only。先例＝生產中之 `entity_registry`＋
`entity_attribute_version`（9,288 列同形）。舊表 **更名保留為史料、不 DROP**。

守原則 #6（--apply 才動 DB;冪等可重跑;--apply 歸主 session 窗、須 hugo 明示;不 DROP 舊表）、
#9/#10（無損以「遷移前後逐列 sha256 對帳」實證,非宣稱）、#12（guard 函式復用
migrate_honesty_guards_ddl.py 單一住所,本支零 CREATE FUNCTION）、#15（對帳不過即整筆 rollback,
不留半套;fail-closed）、#29a/d、#35（壞變體驗紅）。
**人簽欄紀律**：`decided_by`／`decided_at` 於本支**只被逐欄直搬**（原值 NULL 搬過去仍 NULL），
本支永不寫入任何字面值——採認＝Steward 附卷裁定,唯 hugo 親跑（never-type-human-signature）。

## 為什麼另立一支（不併入 migrate_world_concept_registry_ddl.py;#12 單一住所之判斷）

1. **M1 那支已 --apply 生效於生產**,其 `ddl_invariants` 凍住「`concept_key text PRIMARY KEY`／恰二表／
   恰四 trigger」等計數——PK 重構若併入,必須改寫**已生效之回歸鎖**（#35 向前生效之界線）。同一論證
   已是 `migrate_strangler_ledger_ddl.py` 分家之先例（該支標頭「為什麼另立一支」第 2 點）。
2. **生命週期不同**：M1＝長期冪等之「建二表＋種子」;本支＝一次性前向遷移（搬列→改外鍵→更名史料）。
3. **#12 之標的是「同一件事的實作」**：M1 是「建 M1 二表」之單一住所（其文本即 live 現況之來源,須原樣
   保留可考）;本支是「把概念表拆為身分/版本」之單一住所。二者不重疊,不構成第二實作。
4. 防呆：本支落地後,M1 那支之 `--apply` 會重建空的 `world_concept_registry` 並重種 6 列＝影子表。
   故已於 M1 那支 `_apply()`／`_check()` 加一道 fail-closed 前置（偵測 `world_concept_version` 即拒）。

## 遷移後之形制（逐項對應裁決與呈案 §4 丙）

  world_concept                身分表:concept_key text PRIMARY KEY（**真 PK**——沙盒已證 partial unique
                               不能作 FK 被參照鍵,故身分必須有真 PK,見呈案附記）＋created_at
  world_concept_version        版本表:PRIMARY KEY (concept_key, transaction_time)＝雙時間 append-only
                               形（同 entity_attribute_version）;內容七欄＋衝突落點＋人簽欄＋superseded_at
  uq_world_concept_current     partial unique on (concept_key) WHERE superseded_at IS NULL ⇒「現行列恰一」
                               （此索引**不被任何 FK 參照**故合法;WM.14 恰一之 DB 層載體）
  world_concept_registry_current  相容 view＝版本表現行列 JOIN 身分表取 created_at ⇒ **舊表十三欄全覆蓋**;
                               解析 API 之讀取面改指它（src/augur/catalog/world_concept.py:CONCEPT_TABLE）。
                               刻意做成 JOIN view（**非自動可更新**）⇒ 寫入被迫走版本表,不會誤 INSERT 進 view。
  world_channel_binding.concept_key FK 改指 world_concept(concept_key)（原指舊表;98 列參照完整性不落地程式層）
  world_concept_registry_legacy   舊表更名保留為史料（honesty trigger 隨表保留 ⇒ 史料寫保護;**不 DROP**）

**治權面之效果**：honesty guard 只擋 UPDATE/DELETE/TRUNCATE,INSERT 自由 ⇒ Annex F 六條採認親簽變成
**INSERT 一列新版本**,不再需要 `SET LOCAL augur.honesty_write='on'`（＝默改通行證）。施作序依裁決：
本支先於 Annex F 六條採認親簽。

執行指令矩陣
------------
    python3 scripts/migrate_world_concept_identity_split_ddl.py              # 無參數=印矩陣+--check（唯讀,DB 不可達則 graceful）
    python3 scripts/migrate_world_concept_identity_split_ddl.py --check      # 唯讀:遷移狀態（五物件在否/列數/FK 指向）
    python3 scripts/migrate_world_concept_identity_split_ddl.py --print-ddl  # 唯讀:印將執行之 DDL 全文（零連線,過目用）
    python3 scripts/migrate_world_concept_identity_split_ddl.py --verify     # 唯讀:遷移無損對帳（逐列 sha256＋count＋時戳來源）
    python3 scripts/migrate_world_concept_identity_split_ddl.py --apply      # 遷移（單一交易;對帳不過即 rollback;須 hugo #6 明示;dump 期間禁跑 #30）
    python3 scripts/migrate_world_concept_identity_split_ddl.py --selftest   # 紅綠自測（免 DB 免 API;壞變體驗紅 #35）
"""

from __future__ import annotations

import argparse
import re
import sys

import _bootstrap  # noqa: F401

LEGACY_TABLE = "world_concept_registry"
ARCHIVE_TABLE = "world_concept_registry_legacy"
IDENTITY_TABLE = "world_concept"
VERSION_TABLE = "world_concept_version"
COMPAT_VIEW = "world_concept_registry_current"
BINDING_TABLE = "world_channel_binding"
BINDING_FK = "world_channel_binding_concept_key_fkey"
CURRENT_UNIQUE_INDEX = "uq_world_concept_current"

# 舊表十三欄——相容 view 之覆蓋口徑（view 少任一欄即相容性破口）
LEGACY_COLS = ("concept_key", "category", "authoritative_binding_id", "ts_semantics",
               "knowability_rule", "cross_market_axis", "provenance", "finality_predicate",
               "conflict_set_ref", "decided_by", "decided_at", "created_at", "superseded_at")

# 逐列 sha256 之口徑＝十三欄**去掉 superseded_at**（順序即串接順序;調換即 digest 變 ⇒ 欄位錯位會被抓）。
# 為何獨留 superseded_at：它是**遷移後仍會合法變動**之欄（修訂＝標舊列 superseded＋INSERT 新版本）。
# 若併入 digest,第一次 Annex F 採認一落地,--verify 就會對一個完全正確的狀態報紅（假紅＝狼來了,與
# 假綠同樣使紅燈失去意義）。故 superseded_at 另立**更嚴之規則**驗:見 SUPERSEDE_RULE_SQL——遷移列
# 只准 NULL→非 NULL,且必須有後繼版本列;無後繼卻被 supersede＝概念被靜默下架,一律紅。
CONTENT_COLS = tuple(c for c in LEGACY_COLS if c != "superseded_at")

# 搬列對映（版本表欄 ← 舊表欄）。`transaction_time ← created_at`＝**不虛構新時戳**:版本時點取舊列真實
# 寫入時點,遷移不製造「這一版是今天才有的」假象。其餘一律同名直搬（人簽欄亦在此列,不填值）。
COPY_MAP = (
    ("concept_key", "concept_key"),
    ("transaction_time", "created_at"),
    ("category", "category"),
    ("authoritative_binding_id", "authoritative_binding_id"),
    ("ts_semantics", "ts_semantics"),
    ("knowability_rule", "knowability_rule"),
    ("cross_market_axis", "cross_market_axis"),
    ("provenance", "provenance"),
    ("finality_predicate", "finality_predicate"),
    ("conflict_set_ref", "conflict_set_ref"),
    ("decided_by", "decided_by"),
    ("decided_at", "decided_at"),
    ("superseded_at", "superseded_at"),
)

# ── P1:建二表＋現行唯一索引＋四 guard trigger ──────────────────────────────────────────
SQL_TABLES = """
SET lock_timeout = '5s';

CREATE TABLE IF NOT EXISTS world_concept (
    concept_key text PRIMARY KEY,
    created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS world_concept_version (
    concept_key      text NOT NULL REFERENCES world_concept(concept_key),
    transaction_time timestamptz NOT NULL DEFAULT clock_timestamp(),
    category         text NOT NULL
        CHECK (category IN ('entity','event','state','relation','quantity')),
    authoritative_binding_id bigint REFERENCES world_channel_binding(binding_id),
    ts_semantics       text NOT NULL,
    knowability_rule   text NOT NULL,
    cross_market_axis  text,
    provenance         jsonb NOT NULL,
    finality_predicate text NOT NULL DEFAULT '未宣告',
    conflict_set_ref   text,
    decided_by         text,
    decided_at         timestamptz,
    superseded_at      timestamptz,
    PRIMARY KEY (concept_key, transaction_time)
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_world_concept_current
    ON world_concept_version (concept_key) WHERE superseded_at IS NULL;

DROP TRIGGER IF EXISTS trg_world_concept_honesty_row ON world_concept;
CREATE TRIGGER trg_world_concept_honesty_row
  BEFORE UPDATE OR DELETE ON world_concept
  FOR EACH ROW EXECUTE FUNCTION honesty_ledger_guard();
DROP TRIGGER IF EXISTS trg_world_concept_honesty_trunc ON world_concept;
CREATE TRIGGER trg_world_concept_honesty_trunc
  BEFORE TRUNCATE ON world_concept
  FOR EACH STATEMENT EXECUTE FUNCTION honesty_ledger_guard();

DROP TRIGGER IF EXISTS trg_world_concept_version_honesty_row ON world_concept_version;
CREATE TRIGGER trg_world_concept_version_honesty_row
  BEFORE UPDATE OR DELETE ON world_concept_version
  FOR EACH ROW EXECUTE FUNCTION honesty_ledger_guard();
DROP TRIGGER IF EXISTS trg_world_concept_version_honesty_trunc ON world_concept_version;
CREATE TRIGGER trg_world_concept_version_honesty_trunc
  BEFORE TRUNCATE ON world_concept_version
  FOR EACH STATEMENT EXECUTE FUNCTION honesty_ledger_guard();

COMMENT ON TABLE world_concept IS
  '世界概念身分表(丙案 2026-08-03 Steward 圈選;先例 entity_registry):只存 concept_key 與首次登錄時點——自然鍵為真 PK,故 world_channel_binding 之外鍵得以指向此表(partial unique 不能作 FK 被參照鍵,沙盒已實證);內容一律住 world_concept_version';
COMMENT ON TABLE world_concept_version IS
  '世界概念版本表(WM.13/WM.25 版本化之機械載體;先例 entity_attribute_version 之雙時間 append-only 形):修訂=INSERT 新列+舊列標 superseded_at,永不原地改內容欄;uq_world_concept_current 保「現行列恰一」(WM.14);decided_by/decided_at 唯 hugo 親簽(Annex F 附卷裁定)且因 INSERT 免通行證,治權簽核不再與默改共用形狀';
"""

# ── P2:搬列（身分 1 列/概念、版本 1 列/概念;逐欄直搬,人簽欄不填值）────────────────────
SQL_COPY = """
INSERT INTO world_concept (concept_key, created_at)
SELECT concept_key, created_at FROM {src}
ON CONFLICT (concept_key) DO NOTHING;

INSERT INTO world_concept_version
    (concept_key, transaction_time, category, authoritative_binding_id, ts_semantics,
     knowability_rule, cross_market_axis, provenance, finality_predicate,
     conflict_set_ref, decided_by, decided_at, superseded_at)
SELECT concept_key, created_at, category, authoritative_binding_id, ts_semantics,
       knowability_rule, cross_market_axis, provenance, finality_predicate,
       conflict_set_ref, decided_by, decided_at, superseded_at
FROM {src}
ON CONFLICT (concept_key, transaction_time) DO NOTHING;
"""

# ── P3:通道表外鍵改指身分表（98 列參照完整性續由 DB 層擔保,不退為程式層）──────────────
SQL_REPOINT_FK = """
ALTER TABLE world_channel_binding DROP CONSTRAINT IF EXISTS world_channel_binding_concept_key_fkey;
ALTER TABLE world_channel_binding ADD CONSTRAINT world_channel_binding_concept_key_fkey
    FOREIGN KEY (concept_key) REFERENCES world_concept(concept_key);
"""

# ── P4:相容 view（解析 API 讀取面;JOIN 形 ⇒ 非自動可更新,寫入被迫走版本表）──────────────
SQL_VIEW = """
CREATE OR REPLACE VIEW world_concept_registry_current AS
SELECT v.concept_key, v.category, v.authoritative_binding_id, v.ts_semantics,
       v.knowability_rule, v.cross_market_axis, v.provenance, v.finality_predicate,
       v.conflict_set_ref, v.decided_by, v.decided_at,
       c.created_at, v.transaction_time, v.superseded_at
FROM world_concept_version v
JOIN world_concept c ON c.concept_key = v.concept_key
WHERE v.superseded_at IS NULL;

COMMENT ON VIEW world_concept_registry_current IS
  '相容 view:世界概念之現行版本(舊 world_concept_registry 十三欄全覆蓋+transaction_time);解析 API(src/augur/catalog/world_concept.py) 之唯一讀取面;JOIN 形故非自動可更新——登錄/修訂一律 INSERT 進 world_concept_version';
"""

# ── P5:舊表更名保留為史料（不 DROP;honesty trigger 隨表保留 ⇒ 史料寫保護）─────────────
SQL_ARCHIVE = """
ALTER TABLE {src} RENAME TO world_concept_registry_legacy;

COMMENT ON TABLE world_concept_registry_legacy IS
  '史料:M1(2026-08-02)之單表形 world_concept_registry,已於 2026-08-03 依丙案拆為 world_concept + world_concept_version;不 DROP 以保留遷移前原貌可逐列覆核(honesty trigger 隨表保留=寫保護);現行讀取面=world_concept_registry_current';
"""

PHASES = (
    ("P1 身分表/版本表/現行唯一索引/四 guard trigger", SQL_TABLES),
    ("P2 搬列（逐欄直搬;transaction_time←created_at 不虛構時戳;人簽欄不填值）", SQL_COPY),
    ("P3 通道表外鍵改指身分表", SQL_REPOINT_FK),
    ("P4 相容 view（解析 API 讀取面）", SQL_VIEW),
    ("P5 舊表更名保留為史料（不 DROP）", SQL_ARCHIVE),
)


def build_sql(src: str = LEGACY_TABLE) -> str:
    """→ 將執行之 DDL 全文（純函式）。src＝來源表名（遷移已跑過時＝史料表名）。"""
    return "\n".join(f"-- ── {name} ──{tpl.format(src=src)}" for name, tpl in PHASES)


# ── 對帳 SQL（純函式;逐列 sha256——欄位錯位/漏搬/被竄改皆變 digest）────────────────────
_NUL = "~∅~"  # NULL 哨兵（資料中不可能出現;與空字串可區分）

_RECON_FROM = (f"{VERSION_TABLE} v JOIN {IDENTITY_TABLE} c "
               "ON c.concept_key = v.concept_key AND v.transaction_time = c.created_at")


def digest_sql(from_clause: str, qualify: str = "") -> str:
    """逐列 digest SQL（純函式）:回 (concept_key, row_sha)。qualify＝欄前綴（''／'v.'）。

    `created_at` 於重建側取自身分表（c.），其餘取版本表（v.）——此即無損之定義:
    重建出來的十二欄必須逐 byte 等於舊表（superseded_at 另由 SUPERSEDE_RULE_SQL 更嚴驗）。
    """
    def col(c):
        p = "c." if (qualify and c == "created_at") else qualify
        return f"coalesce({p}{c}::text, '{_NUL}')"
    exprs = ", ".join(col(c) for c in CONTENT_COLS)
    key = f"{qualify}concept_key"
    return (f"SELECT {key} AS concept_key,\n"
            f"       encode(sha256(convert_to(concat_ws(chr(31), {exprs}), 'UTF8')), 'hex') AS row_sha\n"
            f"FROM {from_clause}")


def legacy_digest_sql(src: str) -> str:
    return digest_sql(src)


def reconstructed_digest_sql() -> str:
    return digest_sql(_RECON_FROM, qualify="v.")


# superseded_at 之對帳規則（純 SQL 模板）:遷移列之 superseded_at 只准與舊表相同,或 NULL→非 NULL
# **且有後繼版本列**（＝合法修訂）。無後繼卻被 supersede＝該概念被靜默下架（view 從此空、消費端全拒）,
# 必須紅。回 (concept_key, legacy_superseded, migrated_superseded) 之違規列。
SUPERSEDE_RULE_SQL = """
SELECT l.concept_key, l.superseded_at::text, v.superseded_at::text
FROM {src} l
JOIN world_concept c ON c.concept_key = l.concept_key
JOIN world_concept_version v
  ON v.concept_key = l.concept_key AND v.transaction_time = c.created_at
WHERE l.superseded_at IS DISTINCT FROM v.superseded_at
  AND NOT (l.superseded_at IS NULL AND v.superseded_at IS NOT NULL
           AND EXISTS (SELECT 1 FROM world_concept_version w
                       WHERE w.concept_key = l.concept_key
                         AND w.transaction_time > v.transaction_time))
"""

# 合法修訂之計數（資訊性,非違規）——供 --verify 誠實揭露「這些列已被後續修訂取代」。
REVISION_COUNT_SQL = """
SELECT count(*) FROM world_concept_version v
JOIN world_concept c ON c.concept_key = v.concept_key
WHERE v.transaction_time > c.created_at
"""


def supersede_rule_problems(sql: str) -> list:
    """superseded_at 對帳規則自身之不變式（純函式）:漏任一半 ⇒ 對帳假綠或假紅。"""
    bad = []
    if "l.superseded_at IS DISTINCT FROM v.superseded_at" not in sql:
        bad.append("supersede_no_comparison")      # 不比就永遠綠
    if "l.superseded_at IS NULL AND v.superseded_at IS NOT NULL" not in sql:
        bad.append("supersede_direction_unbounded")  # 未限方向 ⇒ 非 NULL→NULL（復活）也放行
    if "w.transaction_time > v.transaction_time" not in sql:
        bad.append("supersede_successor_not_required")  # 無後繼即放行 ⇒ 靜默下架抓不到
    return bad


# ── 不變式（純函式;DDL 字串即被逐字執行之行為載體,對載體驗形＝對行為驗形——#35 型3 註記同 M1/E2
#    先例;**更強之證據＝沙盒實跑後 --verify 對帳**,本支已備該路徑）──────────────────────
def ddl_invariants(sql: str) -> list:
    """回傳被違反之不變式名清單（空＝全守）。selftest 以本尊驗綠、壞變體驗紅。"""
    bad = []
    if "SET lock_timeout" not in sql:
        bad.append("lock_timeout")
    if not re.search(r"CREATE TABLE IF NOT EXISTS world_concept \(\s*\n\s*concept_key text PRIMARY KEY", sql):
        bad.append("identity_natural_pk")        # 身分表須真 PK,否則 FK 撐不住（沙盒已證）
    if f"CREATE TABLE IF NOT EXISTS {VERSION_TABLE}" not in sql:
        bad.append("version_table")
    if "PRIMARY KEY (concept_key, transaction_time)" not in sql:
        bad.append("version_composite_pk")       # 同鍵多版本之物理可能性
    if not re.search(rf"CREATE UNIQUE INDEX IF NOT EXISTS {CURRENT_UNIQUE_INDEX}\s*\n?\s*"
                     rf"ON {VERSION_TABLE} \(concept_key\) WHERE superseded_at IS NULL", sql):
        bad.append("current_partial_unique")     # 現行列恰一（WM.14）之 DB 層載體
    if f"text NOT NULL REFERENCES {IDENTITY_TABLE}(concept_key)" not in sql:
        bad.append("version_fk_to_identity")
    if (f"DROP CONSTRAINT IF EXISTS {BINDING_FK}" not in sql
            or not re.search(rf"ADD CONSTRAINT {BINDING_FK}\s*\n?\s*"
                             rf"FOREIGN KEY \(concept_key\) REFERENCES {IDENTITY_TABLE}\(concept_key\)", sql)):
        bad.append("binding_fk_repointed")
    if re.search(rf"ADD CONSTRAINT {BINDING_FK}[\s\S]{{0,120}}REFERENCES {VERSION_TABLE}", sql):
        bad.append("binding_fk_points_at_version")  # partial unique 撐不住 FK ⇒ 一定失敗
    if sql.count("honesty_ledger_guard()") != 4 or sql.count("DROP TRIGGER IF EXISTS") != 4:
        bad.append("four_guard_triggers")
    if "CREATE OR REPLACE FUNCTION" in sql or "CREATE FUNCTION" in sql:
        bad.append("guard_fn_not_self_made")     # #12:函式住 migrate_honesty_guards_ddl.py
    if f"CREATE OR REPLACE VIEW {COMPAT_VIEW}" not in sql:
        bad.append("compat_view")
    if "WHERE v.superseded_at IS NULL" not in sql:
        bad.append("view_filters_current")       # view 漏濾 ⇒ 已 supersede 之列會被解析 API 讀到
    view_body = sql.split(f"CREATE OR REPLACE VIEW {COMPAT_VIEW} AS")[-1].split(";")[0]
    if not all(c in view_body for c in LEGACY_COLS):
        bad.append("view_covers_legacy_cols")    # 相容 view 須覆蓋舊表十三欄
    if f"RENAME TO {ARCHIVE_TABLE}" not in sql:
        bad.append("legacy_archived")
    if "DROP TABLE" in sql:
        bad.append("legacy_not_dropped")         # #6:舊表不 DROP
    # guard trigger 之 `BEFORE TRUNCATE` 是掛閘、不是清表 ⇒ 先剔除再驗,否則本尊自己會假紅
    if "DELETE FROM" in sql or re.search(r"\bTRUNCATE\b", sql.replace("BEFORE TRUNCATE", "")):
        bad.append("no_destructive_dml")
    if sql.count("'entity','event','state','relation','quantity'") != 1:
        bad.append("category_closed_set")
    if "DEFAULT '未宣告'" not in sql:
        bad.append("finality_default_undeclared")
    if not re.search(r"decided_by\s+text\s*,", sql) or re.search(r"decided_by[^,\n]*DEFAULT", sql):
        bad.append("human_sign_no_default")      # 人簽欄不得有機器預設
    bad += copy_problems(sql)
    return bad


def copy_problems(sql: str) -> list:
    """搬列語句之欄位對位檢（純函式）:漏欄／錯位／人簽欄被寫死字面 → 報違。"""
    bad = []
    m = re.search(rf"INSERT INTO {VERSION_TABLE}\s*\(([^)]*)\)\s*SELECT\s+([\s\S]*?)\s+FROM ", sql)
    if not m:
        return ["copy_stmt_missing"]
    ins = [x.strip() for x in m.group(1).split(",")]
    sel = [x.strip() for x in m.group(2).split(",")]
    if len(ins) != len(COPY_MAP) or len(sel) != len(COPY_MAP):
        bad.append("copy_column_count")
        return bad
    if tuple(zip(ins, sel)) != COPY_MAP:
        bad.append("copy_column_alignment")      # 欄位錯位＝靜默竄改語意（ts_semantics↔knowability_rule…）
    if any(not re.fullmatch(r"[a-z_]+", e) for e in sel):
        bad.append("copy_not_bare_columns")      # 任何字面/表達式＝可能代填（尤人簽欄）
    if dict(COPY_MAP).get("transaction_time") != "created_at":
        bad.append("copy_txtime_from_created_at")
    m2 = re.search(rf"INSERT INTO {IDENTITY_TABLE} \(concept_key, created_at\)\s*"
                   rf"SELECT concept_key, created_at FROM ", sql)
    if not m2:
        bad.append("copy_identity_stmt")
    return bad


def digest_problems(sql: str) -> list:
    """對帳 SQL 自身之不變式（純函式）:少欄／不含 NULL 哨兵 ⇒ 對帳會假綠。"""
    bad = []
    for c in CONTENT_COLS:
        if c not in sql:
            bad.append(f"digest_missing_{c}")
    if "sha256" not in sql:
        bad.append("digest_not_sha256")
    if _NUL not in sql:
        bad.append("digest_no_null_sentinel")    # 無哨兵時 NULL 與 '' 同 digest ⇒ 抓不到「值被清空」
    if "concat_ws(chr(31)" not in sql:
        bad.append("digest_no_separator")        # 無分隔字元 ⇒ 'ab'+'c' 與 'a'+'bc' 同 digest
    return bad


# ── DB 面 ─────────────────────────────────────────────────────────────────────────────
def _regclass(cur, name: str):
    cur.execute("SELECT to_regclass(%s)", (f"public.{name}",))
    return cur.fetchone()[0]


def _binding_fk_target(cur):
    cur.execute("SELECT confrelid::regclass::text FROM pg_constraint WHERE conname = %s", (BINDING_FK,))
    r = cur.fetchone()
    return r[0] if r else None


def _source_table(cur):
    """遷移來源表:未遷移＝舊表名;已遷移＝史料表名;皆無＝None（fail-closed）。"""
    if _regclass(cur, LEGACY_TABLE):
        return LEGACY_TABLE
    if _regclass(cur, ARCHIVE_TABLE):
        return ARCHIVE_TABLE
    return None


def _check(conn) -> int:
    with conn.cursor() as cur:
        src = _source_table(cur)
        for name in (LEGACY_TABLE, ARCHIVE_TABLE, IDENTITY_TABLE, VERSION_TABLE, COMPAT_VIEW):
            oid = _regclass(cur, name)
            print(f"  {'✓' if oid else '·'} {name} {'在' if oid else '不在'}")
        cur.execute("SELECT count(*) FROM pg_class WHERE relname = %s AND relkind = 'i'",
                    (CURRENT_UNIQUE_INDEX,))
        print(f"  {'✓' if cur.fetchone()[0] else '·'} {CURRENT_UNIQUE_INDEX}（現行列恰一）")
        tgt = _binding_fk_target(cur)
        want = IDENTITY_TABLE if _regclass(cur, IDENTITY_TABLE) else LEGACY_TABLE
        print(f"  {'✓' if tgt == want else '·'} {BINDING_FK} → {tgt}（應指 {want}）")
        if src:
            cur.execute(f"SELECT count(*) FROM {src}")
            print(f"  來源表 {src}:{cur.fetchone()[0]} 列")
        else:
            print("  · 來源表不在（舊表與史料表皆無）——未 M1 或已被移除")
        if _regclass(cur, VERSION_TABLE):
            cur.execute(f"SELECT (SELECT count(*) FROM {IDENTITY_TABLE}),"
                        f" (SELECT count(*) FROM {VERSION_TABLE}),"
                        f" (SELECT count(*) FROM {VERSION_TABLE} WHERE superseded_at IS NULL),"
                        f" (SELECT count(decided_by) FROM {VERSION_TABLE})")
            n_i, n_v, n_cur, n_sig = cur.fetchone()
            print(f"  身分 {n_i} 列／版本 {n_v} 列（現行 {n_cur}）／已親簽採認 {n_sig}"
                  "——空＝待 hugo 附卷裁定")
        if _regclass(cur, COMPAT_VIEW):
            cur.execute(f"SELECT count(*) FROM {COMPAT_VIEW}")
            print(f"  相容 view {COMPAT_VIEW}:{cur.fetchone()[0]} 列")
    return 0


def verify_problems(cur, src: str) -> list:
    """遷移無損對帳（唯讀純檢）:逐列 sha256＋count＋時戳來源＋superseded 方向。回問題清單（空＝無損）。"""
    bad = []
    cur.execute(legacy_digest_sql(src))
    old = dict(cur.fetchall())
    cur.execute(reconstructed_digest_sql())
    new = dict(cur.fetchall())
    if set(old) != set(new):
        bad.append(f"concept_key 集合不等:僅舊={sorted(set(old) - set(new))} "
                   f"僅新={sorted(set(new) - set(old))}")
    for k in sorted(set(old) & set(new)):
        if old[k] != new[k]:
            bad.append(f"列內容 sha 不等 {k}: 舊 {old[k][:16]}… vs 新 {new[k][:16]}…")
    cur.execute(f"SELECT count(*) FROM {src}")
    n_src = cur.fetchone()[0]
    cur.execute(f"SELECT count(*) FROM {IDENTITY_TABLE}")
    n_id = cur.fetchone()[0]
    if n_src != n_id:
        bad.append(f"身分列數 {n_id} ≠ 來源列數 {n_src}")
    if len(old) != n_src or len(new) != n_src:
        bad.append(f"digest 列數 舊 {len(old)}／新 {len(new)} ≠ 來源 {n_src}")
    cur.execute(f"SELECT count(*) FROM {IDENTITY_TABLE} c WHERE "
                f"(SELECT min(transaction_time) FROM {VERSION_TABLE} v "
                f" WHERE v.concept_key = c.concept_key) IS DISTINCT FROM c.created_at")
    n_bad_tt = cur.fetchone()[0]
    if n_bad_tt:
        bad.append(f"{n_bad_tt} 個概念之最早版本時點 ≠ 身分 created_at（時戳被虛構）")
    cur.execute(SUPERSEDE_RULE_SQL.format(src=src))
    for k, l_at, v_at in cur.fetchall():
        bad.append(f"superseded_at 不合法 {k}: 舊={l_at or 'NULL'} 新={v_at or 'NULL'}"
                   "（只准 NULL→非 NULL 且須有後繼版本列）")
    return bad


def _verify(conn) -> int:
    with conn.cursor() as cur:
        src = _source_table(cur)
        if not src or not _regclass(cur, VERSION_TABLE):
            print(f"  · 尚不可對帳（來源表={src}／{VERSION_TABLE} "
                  f"{'在' if _regclass(cur, VERSION_TABLE) else '不在'}）——先 --apply")
            return 0
        bad = verify_problems(cur, src)
        cur.execute(REVISION_COUNT_SQL)
        n_rev = cur.fetchone()[0]
    if bad:
        print(f"✗ 遷移對帳不過（{len(bad)} 項）:")
        for b in bad:
            print(f"    - {b}")
        return 1
    print(f"✓ 遷移無損:{src} 逐列 sha256（{len(CONTENT_COLS)} 欄）與 {IDENTITY_TABLE}+{VERSION_TABLE} "
          "重建結果全等；列數相符；版本時點取自舊列 created_at（未虛構）；"
          "superseded_at 只見合法方向且皆有後繼版本")
    print(f"  （遷移後已累積 {n_rev} 筆修訂版本列——資訊性揭露,非違規）")
    return 0


def _apply(conn) -> int:
    from augur.core import db
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM pg_proc WHERE proname='honesty_ledger_guard'")
        if cur.fetchone()[0] == 0:
            print("✗ honesty_ledger_guard 函式不存在——先跑 migrate_honesty_guards_ddl.py --apply"
                  "（#12 不自造第二住所）")
            return 1
        if not _regclass(cur, BINDING_TABLE):
            print(f"✗ {BINDING_TABLE} 不在——先跑 migrate_world_concept_registry_ddl.py --apply（M1）")
            return 1
        src = _source_table(cur)
        if not src:
            print(f"✗ 來源表不在（{LEGACY_TABLE}／{ARCHIVE_TABLE} 皆無）——拒絕在無來源下建空表")
            return 1
    bad_ddl = ddl_invariants(build_sql(src)) + supersede_rule_problems(SUPERSEDE_RULE_SQL)
    if bad_ddl:
        print(f"✗ 待執行之 DDL／對帳規則自身違反不變式 {bad_ddl}——拒絕執行"
              "（回歸鎖不得因「只跑 --apply、沒跑 --selftest」而被繞過）")
        return 1
    try:
        with db.transaction(conn) as cur:
            for name, tpl in PHASES:
                if tpl is SQL_ARCHIVE and src == ARCHIVE_TABLE:
                    print(f"  · {name}:已為史料表名,跳過")
                    continue
                cur.execute(tpl.format(src=src))
                print(f"  ✓ {name}")
                if tpl is SQL_COPY:       # 對帳在交易內:不過即整筆 rollback（#15 不留半套）
                    bad = verify_problems(cur, src)
                    if bad:
                        raise RuntimeError("遷移對帳不過,整筆回滾:\n    - " + "\n    - ".join(bad))
                    print("  ✓ 交易內對帳:逐列 sha256 全等（無損）")
    except RuntimeError as e:
        print(f"✗ {e}")
        return 1
    print("✓ 遷移完成（單一交易;舊表已更名為史料、未 DROP）")
    return _check(conn)


# ── 紅綠自測（#35:本尊驗綠、壞變體驗紅;免 DB 免 API 零 usage）──────────────────────────
def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'✓' if cond else '✗'} {name}")

    sql = build_sql()
    chk("本尊 DDL 全不變式守住（綠）", ddl_invariants(sql) == [])
    chk("本尊對帳 SQL 全不變式守住（綠）",
        digest_problems(legacy_digest_sql(LEGACY_TABLE)) == []
        and digest_problems(reconstructed_digest_sql()) == []
        and supersede_rule_problems(SUPERSEDE_RULE_SQL) == [])
    chk("digest 口徑刻意排除 superseded_at（否則第一次合法採認即報假紅）",
        "superseded_at" not in legacy_digest_sql(LEGACY_TABLE)
        and set(CONTENT_COLS) == set(LEGACY_COLS) - {"superseded_at"})
    chk("build_sql 為純函式:換來源表名只換來源、形制不變",
        build_sql(ARCHIVE_TABLE) != sql
        and ddl_invariants(build_sql(ARCHIVE_TABLE)) == []
        and f"FROM {ARCHIVE_TABLE}" in build_sql(ARCHIVE_TABLE))
    chk("重建側 created_at 取自身分表、其餘取版本表（無損之定義）",
        "c.created_at" in reconstructed_digest_sql()
        and "v.ts_semantics" in reconstructed_digest_sql())

    # ── 壞變體驗紅 ──
    chk("驗紅:身分表改用 partial unique 取代 PK → identity_natural_pk 報違（FK 撐不住,沙盒已證）",
        "identity_natural_pk" in ddl_invariants(sql.replace("concept_key text PRIMARY KEY", "concept_key text")))
    chk("驗紅:版本表退回單鍵 PK → version_composite_pk 報違（同鍵第二版物理不可能）",
        "version_composite_pk" in ddl_invariants(
            sql.replace("PRIMARY KEY (concept_key, transaction_time)", "PRIMARY KEY (concept_key)")))
    chk("驗紅:現行唯一索引拿掉 partial 條件 → current_partial_unique 報違（修訂列並存即撞唯一）",
        "current_partial_unique" in ddl_invariants(
            sql.replace("ON world_concept_version (concept_key) WHERE superseded_at IS NULL",
                        "ON world_concept_version (concept_key)")))
    chk("驗紅:通道外鍵改指版本表 → binding_fk_points_at_version 報違",
        "binding_fk_points_at_version" in ddl_invariants(sql.replace(
            f"FOREIGN KEY (concept_key) REFERENCES {IDENTITY_TABLE}(concept_key)",
            f"FOREIGN KEY (concept_key) REFERENCES {VERSION_TABLE}(concept_key)")))
    chk("驗紅:外鍵不改指（沿用舊表）→ binding_fk_repointed 報違",
        "binding_fk_repointed" in ddl_invariants(sql.replace(SQL_REPOINT_FK, "\n")))
    chk("驗紅:view 漏濾 superseded_at → view_filters_current 報違（已 supersede 之列會被解析）",
        "view_filters_current" in ddl_invariants(sql.replace("WHERE v.superseded_at IS NULL", "")))
    chk("驗紅:view 少一欄（provenance）→ view_covers_legacy_cols 報違（相容性破口）",
        "view_covers_legacy_cols" in ddl_invariants(
            sql.replace("v.provenance, v.finality_predicate", "v.finality_predicate")))
    chk("驗紅:舊表改成 DROP → legacy_not_dropped＋legacy_archived 報違（#6 不 DROP）",
        set(["legacy_not_dropped", "legacy_archived"]) <= set(ddl_invariants(
            sql.replace(f"ALTER TABLE {LEGACY_TABLE} RENAME TO {ARCHIVE_TABLE};",
                        f"DROP TABLE {LEGACY_TABLE};"))))
    chk("驗紅:少一支 guard trigger → four_guard_triggers 報違",
        "four_guard_triggers" in ddl_invariants(sql.replace(
            "DROP TRIGGER IF EXISTS trg_world_concept_version_honesty_trunc ON world_concept_version;",
            "", 1)))
    chk("驗紅:DDL 自造 guard 函式 → 報違（#12 單一住所）",
        "guard_fn_not_self_made" in ddl_invariants(
            sql + "\nCREATE OR REPLACE FUNCTION honesty_ledger_guard() RETURNS trigger AS $$ $$;"))
    chk("驗紅:decided_by 加 DEFAULT → human_sign_no_default 報違（人簽欄不得有機器預設）",
        "human_sign_no_default" in ddl_invariants(
            sql.replace("decided_by         text,", "decided_by         text DEFAULT 'ai',")))
    chk("驗紅:搬列把人簽欄寫成字面 → copy_not_bare_columns 報違（不代打人簽）",
        "copy_not_bare_columns" in ddl_invariants(sql.replace(
            "conflict_set_ref, decided_by, decided_at, superseded_at\nFROM {src}".format(src=LEGACY_TABLE),
            "conflict_set_ref, 'hugo', decided_at, superseded_at\nFROM {src}".format(src=LEGACY_TABLE))))
    chk("驗紅:搬列兩欄對調 → copy_column_alignment 報違（靜默竄改語意）",
        "copy_column_alignment" in ddl_invariants(sql.replace(
            "SELECT concept_key, created_at, category, authoritative_binding_id, ts_semantics,\n"
            "       knowability_rule,",
            "SELECT concept_key, created_at, category, authoritative_binding_id, knowability_rule,\n"
            "       ts_semantics,")))
    chk("驗紅:搬列少一欄 → copy_column_count 報違",
        "copy_column_count" in ddl_invariants(sql.replace(
            "     conflict_set_ref, decided_by, decided_at, superseded_at)",
            "     conflict_set_ref, decided_by, decided_at)")))
    chk("驗紅:transaction_time 改用 now() 而非舊 created_at → 報違（虛構時戳）",
        {"copy_column_alignment", "copy_not_bare_columns"} & set(ddl_invariants(sql.replace(
            "SELECT concept_key, created_at, category", "SELECT concept_key, now(), category"))))
    chk("驗紅:DDL 夾帶 DELETE FROM → no_destructive_dml 報違",
        "no_destructive_dml" in ddl_invariants(sql + f"\nDELETE FROM {LEGACY_TABLE};"))
    chk("驗紅:DDL 夾帶 TRUNCATE → no_destructive_dml 報違（且不與 BEFORE TRUNCATE 掛閘句混淆）",
        "no_destructive_dml" in ddl_invariants(sql + f"\nTRUNCATE {LEGACY_TABLE};"))
    chk("驗紅:拿掉 lock_timeout → 報違（#30 鎖風暴）",
        "lock_timeout" in ddl_invariants(sql.replace("SET lock_timeout = '5s';", "")))
    chk("驗紅:對帳 digest 少一欄（decided_by）→ 報違（人簽被竄改會查不出）",
        "digest_missing_decided_by" in digest_problems(
            legacy_digest_sql(LEGACY_TABLE).replace("coalesce(decided_by::text, '~∅~'), ", "")))
    chk("驗紅:對帳 digest 去掉 NULL 哨兵 → 報違（NULL 與空字串同 digest）",
        "digest_no_null_sentinel" in digest_problems(
            legacy_digest_sql(LEGACY_TABLE).replace(_NUL, "")))
    chk("驗紅:對帳 digest 去掉分隔字元 → 報違（欄界模糊 ⇒ 'ab|c' 與 'a|bc' 同 digest）",
        "digest_no_separator" in digest_problems(
            legacy_digest_sql(LEGACY_TABLE).replace("concat_ws(chr(31)", "concat(")))
    chk("驗紅:superseded 規則不比對 → supersede_no_comparison 報違（永遠綠）",
        "supersede_no_comparison" in supersede_rule_problems(SUPERSEDE_RULE_SQL.replace(
            "l.superseded_at IS DISTINCT FROM v.superseded_at", "true")))
    chk("驗紅:superseded 規則不要求後繼版本 → supersede_successor_not_required 報違（靜默下架放行）",
        "supersede_successor_not_required" in supersede_rule_problems(SUPERSEDE_RULE_SQL.replace(
            "w.transaction_time > v.transaction_time", "true")))
    chk("驗紅:superseded 規則不限方向 → supersede_direction_unbounded 報違（已 supersede 之列可復活）",
        "supersede_direction_unbounded" in supersede_rule_problems(SUPERSEDE_RULE_SQL.replace(
            "l.superseded_at IS NULL AND v.superseded_at IS NOT NULL", "true")))
    print("自測:全通過 ✓" if ok else "自測:有失敗 ✗")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="world_concept_registry → 身分表/版本表（丙案;--apply 須 hugo 明示）")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--print-ddl", dest="print_ddl", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.print_ddl:
        print(build_sql())
        return 0
    no_args = not (a.check or a.verify or a.apply)
    if no_args:
        print(__doc__.split("執行指令矩陣")[-1].split("------------\n")[-1])
    from augur.core import db
    if no_args:
        try:
            with db.connect() as conn:
                return _check(conn)
        except Exception as e:  # noqa: BLE001 — 無參數須 graceful 不裸 traceback（#29a）
            print(f"（--check 需 DB;現不可達:{e};--selftest／--print-ddl 免 DB 可跑）")
            return 0
    with db.connect() as conn:
        if a.apply:
            return _apply(conn)
        if a.verify:
            return _verify(conn)
        return _check(conn)


if __name__ == "__main__":
    sys.exit(main())
