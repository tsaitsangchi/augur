#!/usr/bin/env python3
"""🎯 建 World Concept Registry 二表——「世界概念 → 來源 Observation 位置」終於有機器可解析的家。

WM.36 合規弧 M1（G0 格 3「照案」2026-08-02 hugo 拍板;設計 SSOT=reports/wm3536_vendor_registry_plan_20260802.md §4）。
守原則 #6（--apply 才動 DB;冪等可重跑;--apply 歸主 session 窗、須 hugo 明示）、#9/#10（種子逐列溯源
Annex F 文本＋dataset_catalog 實列）、#12（honesty guard 函式復用 migrate_honesty_guards_ddl 單一住所,
不自造第二實作）、#15（unmapped 誠實預設;採認狀態 pending 不假關）、#29a/d、#35（壞變體驗紅）。
決策欄紀律:decided_by/decided_at **本腳本永不觸碰**——採認=Steward 附卷裁定（G0 格 4「簽核即附卷」）,
唯 hugo 親跑寫入（never-type-human-signature）。

逐欄條文錨（specs/WORLD-MODEL-SPECIFICATION.md WM.36:344-358;WM.35:336-340;binding 逐字對齊）
----------------------------------------------------------------------------------------
① world_concept_registry（概念主表;欄 3 由 ② 承載——七欄=登錄項之邏輯欄,由二表 join 呈現,
   符合 :358「登錄項七欄俱全且各欄可解析」判準;載體=[I]、DEFER D18〔:357〕）
  concept_key              ← 欄1 :347 世界概念（具名、繫結 Identity 語義;命名空間例 'tw.daily_bar'）
  category                 ← 欄2 :348 歸類閉集 entity/event/state/relation/quantity（關係/量定義見 WM.8）
  （通道映射）             ← 欄3 :349 粒度至欄位級、一對多 ⇒ ② world_channel_binding 整表承載
  authoritative_binding_id ← 欄4 :350 權威表徵指定（WM.14 恰一;NULL=尚未指定=WM.14 違反態、不得被消費）
  ts_semantics             ← 欄5 :351 通道時間屬性雙宣告之 WM.31(a) 時間戳語義
  knowability_rule         ← 欄5 :351 之 WM.31(b) 可知規則（anti-leakage 錨,#8）
  cross_market_axis        ← 欄5 :351 之 A.35 第三項跨市場軸對映（如適用;RULING-2026-030 §五(f)/AL-2026-033）
  provenance               ← 欄6 :352 provenance
  finality_predicate       ← 欄7 :353 定案性述語（WM.32/A.37;'未宣告'→依 WM.32 缺省規則推定 non-final）
  conflict_set_ref         ← WM.37:360-362 多通道衝突保存落點（預留承載位,非七欄之一）
  created_at/superseded_at ← WM.25 表徵狀態變更 × WM.13 版本化:append-only——變更=新列、舊列標時戳,
                             不 UPDATE 內容欄（honesty guard 之 UPDATE-GUC 通行證僅供標 superseded_at）
  decided_by/decided_at    ← Annex F:939 採認與登錄由 Steward 附卷裁定（hugo 親簽;本腳本不代填）
② world_channel_binding（欄 3 本體:欄位級、一對多）
  mapping_status ∈ {mapped,unmapped} ＋ CHECK 雙條件式 ← WM.35:338 **unmapped=顯式合法過渡態**、
    不得曖昧;unmapped/未登錄通道之資料僅具 Observation 地位（得保存/對帳/追溯,不得被消費為
    Representation 或 Knowledge 之依據）
  source_table/source_column ← 供應商表名/欄名字面之**唯一合法住所**（WM.36:356 消費禁令之對偶;
    source_column NULL=表級暫登,是否構成登錄完成=計畫 §9 Q5 待 Steward）
  channel_role ∈ {observation,derived} ← WM.15 衍生觀測（如 TaiwanStockPriceAdj 對 TaiwanStockPrice）
guard trigger ← 同 honesty 家族（G0 格 3 裁示「trigger 同 honesty 家族」）:二表各掛
  BEFORE UPDATE OR DELETE row 級＋BEFORE TRUNCATE statement 級,函式=honesty_ledger_guard()
  （復用 #12;--apply 前置檢查其存在,不存在即拒——先跑 migrate_honesty_guards_ddl.py --apply）

解析 API 空殼規畫（實作歸 M3 絞殺批,本批零實作;#18 禁通用角色名故檔名已定=src/augur/catalog/world_concept.py）
----------------------------------------------------------------------------------------
  resolve(concept_key: str) -> Binding    # Binding=(table, column, role);經 ① authoritative_binding_id → ②
  resolve_sql(concept_key: str) -> str    # 回引號表名字面,供 f-string 組 SQL;lru_cache
  # --selftest=凍結 fixture 零 DB 結構斷言（#18 v1.28）;vendor 字面自此只活在 DB 資料列

種子策略（計畫 §4 種子節;--apply 才執行,--seed-dry 唯讀預覽不執行）
----------------------------------------------------------------------------------------
  ① Annex F 六條（spec :941-946）→ 六列:provenance.採認狀態='pending'、decided_by 留空待 hugo;
    F-1 歸類原文為雙寫「事件／狀態」,閉集單值 seed 暫置 'event' 並於 provenance 保留原文待採認校正。
  ② dataset_catalog（live 97 列）→ 全量通道登錄:表級（source_column NULL,§9 Q5 暫登)、初始
    mapping_status='unmapped' 為誠實預設;Annex F 涉及之通道先 mapped（ANNEX_F_CHANNELS 十映射,
    TaiwanStockDelisting 一對多服務 F-5/F-6 兩概念故較 97 多一列;實數以 --seed-dry 實跑為準）。
    column_catalog（769 列）=欄位級候補來源,不在本批種子（Q5 裁後另批）。

執行指令矩陣
------------
    python3 scripts/migrate_world_concept_registry_ddl.py             # 無參數=印矩陣+--check（唯讀,DB 不可達則 graceful）
    python3 scripts/migrate_world_concept_registry_ddl.py --check     # 唯讀:二表/四 trigger/種子列況
    python3 scripts/migrate_world_concept_registry_ddl.py --seed-dry  # 唯讀:讀 dataset_catalog 預覽種子 SQL 與筆數（不執行）
    python3 scripts/migrate_world_concept_registry_ddl.py --apply     # DDL+種子（冪等;須 hugo #6 明示;dump 期間禁跑 #30）
    python3 scripts/migrate_world_concept_registry_ddl.py --selftest  # 紅綠自測（免 DB 免 API;壞變體驗紅 #35）
"""

from __future__ import annotations

import argparse
import re
import sys

import _bootstrap  # noqa: F401

# ── DDL:計畫 §4 二表形制照案（僅加冪等外衣:IF NOT EXISTS/DO-guard/DROP TRIGGER IF EXISTS;#30 lock_timeout）──
DDL = """
SET lock_timeout = '5s';

CREATE TABLE IF NOT EXISTS world_concept_registry (
    concept_key        text PRIMARY KEY,
    category           text NOT NULL
        CHECK (category IN ('entity','event','state','relation','quantity')),
    authoritative_binding_id bigint,
    ts_semantics       text NOT NULL,
    knowability_rule   text NOT NULL,
    cross_market_axis  text,
    provenance         jsonb NOT NULL,
    finality_predicate text NOT NULL DEFAULT '未宣告',
    conflict_set_ref   text,
    decided_by         text,
    decided_at         timestamptz,
    created_at         timestamptz NOT NULL DEFAULT now(),
    superseded_at      timestamptz
);

CREATE TABLE IF NOT EXISTS world_channel_binding (
    binding_id     bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    concept_key    text REFERENCES world_concept_registry(concept_key),
    source_table   text NOT NULL,
    source_column  text,
    channel_role   text NOT NULL DEFAULT 'observation'
        CHECK (channel_role IN ('observation','derived')),
    mapping_status text NOT NULL CHECK (mapping_status IN ('mapped','unmapped')),
    CHECK ((mapping_status='mapped') = (concept_key IS NOT NULL)),
    provenance     jsonb NOT NULL,
    created_at     timestamptz NOT NULL DEFAULT now(),
    superseded_at  timestamptz
);

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_auth_binding') THEN
        ALTER TABLE world_concept_registry ADD CONSTRAINT fk_auth_binding
            FOREIGN KEY (authoritative_binding_id) REFERENCES world_channel_binding(binding_id);
    END IF;
END $$;

DROP TRIGGER IF EXISTS trg_world_concept_registry_honesty_row ON world_concept_registry;
CREATE TRIGGER trg_world_concept_registry_honesty_row
  BEFORE UPDATE OR DELETE ON world_concept_registry
  FOR EACH ROW EXECUTE FUNCTION honesty_ledger_guard();
DROP TRIGGER IF EXISTS trg_world_concept_registry_honesty_trunc ON world_concept_registry;
CREATE TRIGGER trg_world_concept_registry_honesty_trunc
  BEFORE TRUNCATE ON world_concept_registry
  FOR EACH STATEMENT EXECUTE FUNCTION honesty_ledger_guard();

DROP TRIGGER IF EXISTS trg_world_channel_binding_honesty_row ON world_channel_binding;
CREATE TRIGGER trg_world_channel_binding_honesty_row
  BEFORE UPDATE OR DELETE ON world_channel_binding
  FOR EACH ROW EXECUTE FUNCTION honesty_ledger_guard();
DROP TRIGGER IF EXISTS trg_world_channel_binding_honesty_trunc ON world_channel_binding;
CREATE TRIGGER trg_world_channel_binding_honesty_trunc
  BEFORE TRUNCATE ON world_channel_binding
  FOR EACH STATEMENT EXECUTE FUNCTION honesty_ledger_guard();

COMMENT ON TABLE world_concept_registry IS
  'World Concept Registry 概念主表(WM.36 欄1/2/4/5/6/7+WM.37 衝突落點;欄3=world_channel_binding;七欄=二表 join 呈現;append-only:變更=新列+superseded_at,honesty guard 同家族;decided_by 唯 hugo 親簽=Annex F 附卷裁定;M1 2026-08-02 G0 格3 照案)';
COMMENT ON TABLE world_channel_binding IS
  '通道映射表(WM.36 欄3:欄位級一對多;WM.35 unmapped=顯式合法過渡態僅具 Observation 地位;供應商表名/欄名字面之唯一合法住所——消費端一律經 concept_key 解析,WM.36:356 直綁禁令 2026-10-15 起無條件適用)';
"""

# ── 種子 ①:Annex F 六條（spec :941-946 逐條;採認狀態=pending、decided_by 不入列=留空待 hugo）──
SEED_CONCEPTS_SQL = """
INSERT INTO world_concept_registry
    (concept_key, category, ts_semantics, knowability_rule, finality_predicate, provenance)
VALUES
('tw.daily_bar', 'event', '交易日', '收盤後當日可得', '次一交易日定案述語適用',
 jsonb_build_object('annex_f_entry', 1,
   'annex_f_text', 'MarketTrade/DailyBar|事件／狀態(日級成交)|兩通道:原始成交價通道+含 CorporateAction 調整之衍生通道(WM.15)|同一世界事實之同一性宣告與擇用規則單一登錄(A.58;AUD-14-R)|時間戳語義:交易日;可知規則:收盤後當日可得、次一交易日定案述語適用',
   'category_note', '原文雙寫「事件／狀態」,閉集單值暫置 event,採認時校正',
   'source', '所列通道之當次回應', 'basis', '本規格起草程序(審計補正 AUD-01-R4 隨卷)',
   '採認狀態', 'pending')),
('tw.corporate_action.ex_dividend', 'event', '除權息交易日', '公告時點欄為可知規則錨(WM.31(b))', '未宣告',
 jsonb_build_object('annex_f_entry', 2,
   'annex_f_text', 'CorporateAction.除權息|世界事件|股利與除權息結果通道|權威表徵指定於事件概念|時間戳語義:除權息交易日;可知規則:公告時點欄為可知規則錨(WM.31(b))',
   'source', '所列通道之當次回應', 'basis', '本規格起草程序(審計補正 AUD-01-R4 隨卷)',
   '採認狀態', 'pending')),
('tw.fx.twd_usd', 'quantity', '觀測日', '依通道各自宣告(vintage 通道逐版)', '未宣告',
 jsonb_build_object('annex_f_entry', 3,
   'annex_f_text', 'EconomicIndicator.新台幣對美元匯率|世界量|兩供應商通道(本國供應商匯率資料集+外國經濟資料庫對應 series)|一權威表徵指定+衝突保存落點(AUD-06-R1/R2)|時間戳語義:觀測日;可知規則:依通道各自宣告(vintage 通道逐版)',
   'conflict_note', '多通道衝突保存落點=conflict_set_ref,值待採認',
   'source', '所列通道之當次回應', 'basis', '本規格起草程序(審計補正 AUD-01-R4 隨卷)',
   '採認狀態', 'pending')),
('tw.trading_calendar', 'relation', '交易日', '事前公告之市場日曆', '未宣告',
 jsonb_build_object('annex_f_entry', 4,
   'annex_f_text', 'TradingCalendar|世界關係(日曆日↔交易日)|交易日通道|單通道權威|時間戳語義:交易日;可知規則:事前公告之市場日曆',
   'source', '所列通道之當次回應', 'basis', '本規格起草程序(審計補正 AUD-01-R4 隨卷)',
   '採認狀態', 'pending')),
('tw.roster_membership', 'state', '快照日', '快照當日', '未宣告',
 jsonb_build_object('annex_f_entry', 5,
   'annex_f_text', 'Roster 成員資格|世界狀態(point-in-time)|基本資訊快照+下市通道|權威表徵為時間函數之成員資格概念(A.2 survivorship 禁令適用)|時間戳語義:快照日;可知規則:快照當日',
   'source', '所列通道之當次回應', 'basis', '本規格起草程序(審計補正 AUD-01-R4 隨卷)',
   '採認狀態', 'pending')),
('tw.delisting', 'event', '下市日', '主管機關公告', '未宣告',
 jsonb_build_object('annex_f_entry', 6,
   'annex_f_text', 'Delisting|世界事件|下市通道|單通道權威(A.25 可見性語義適用)|時間戳語義:下市日;可知規則:主管機關公告',
   'source', '所列通道之當次回應', 'basis', '本規格起草程序(審計補正 AUD-01-R4 隨卷)',
   '採認狀態', 'pending'))
ON CONFLICT (concept_key) DO NOTHING;
"""

SIX_CONCEPT_KEYS = ("tw.daily_bar", "tw.corporate_action.ex_dividend", "tw.fx.twd_usd",
                    "tw.trading_calendar", "tw.roster_membership", "tw.delisting")

# Annex F 涉及之通道映射（concept_key, source_table=dataset_catalog.dataset, channel_role, note）。
# TaiwanStockDelisting 一對多服務 F-5/F-6（WM.36 欄3「一對多」明文）。fred_series 之 series 識別碼
# 於採認時 [I] 註記——2026-08-02 live 親驗本庫尚無新台幣對美元直接 series（僅 DTWEXBGS）,誠實入 note。
ANNEX_F_CHANNELS = (
    ("tw.daily_bar", "TaiwanStockPrice", "observation", "Annex F-1 原始成交價通道"),
    ("tw.daily_bar", "TaiwanStockPriceAdj", "derived", "Annex F-1 含 CorporateAction 調整之衍生通道(WM.15)"),
    ("tw.corporate_action.ex_dividend", "TaiwanStockDividend", "observation", "Annex F-2 股利通道"),
    ("tw.corporate_action.ex_dividend", "TaiwanStockDividendResult", "observation", "Annex F-2 除權息結果通道"),
    ("tw.fx.twd_usd", "TaiwanExchangeRate", "observation", "Annex F-3 本國供應商匯率資料集"),
    ("tw.fx.twd_usd", "fred_series", "observation",
     "Annex F-3 外國經濟資料庫對應 series(識別碼採認時註記;2026-08-02 親驗本庫無新台幣對美元直接 series,僅 DTWEXBGS)"),
    ("tw.trading_calendar", "TaiwanStockTradingDate", "observation", "Annex F-4 交易日通道"),
    ("tw.roster_membership", "TaiwanStockInfo", "observation", "Annex F-5 基本資訊快照通道"),
    ("tw.roster_membership", "TaiwanStockDelisting", "observation", "Annex F-5 下市通道(成員資格時間函數輸入;A.2)"),
    ("tw.delisting", "TaiwanStockDelisting", "observation", "Annex F-6 下市通道(A.25)"),
)


def build_binding_seed_sql(channels=ANNEX_F_CHANNELS) -> str:
    """種子 ② SQL（純函式;#29(b) 資料驅動——來源=live dataset_catalog,不 hardcode 97 列）。
    idempotent:同 (source_table, source_column, concept_key) 組合曾登錄過（含已 superseded）即不再插——
    bootstrap 一次性,不復活已被治理程序 supersede 之列。"""
    vals = ",\n        ".join(
        f"('{ck}', '{tbl}', '{role}', '{note}')" for ck, tbl, role, note in channels)
    return f"""
WITH annex_map(concept_key, source_table, channel_role, map_note) AS (
    VALUES
        {vals}
)
INSERT INTO world_channel_binding
    (concept_key, source_table, source_column, channel_role, mapping_status, provenance)
SELECT m.concept_key,
       d.dataset,
       NULL,
       coalesce(m.channel_role, 'observation'),
       CASE WHEN m.concept_key IS NULL THEN 'unmapped' ELSE 'mapped' END,
       jsonb_strip_nulls(jsonb_build_object(
           'seed_source', 'dataset_catalog',
           'seed_basis', 'reports/wm3536_vendor_registry_plan_20260802.md §4 種子(G0 格3 照案)',
           'vendor_source', d.source,
           'catalog_category', d.category,
           'granularity', 'table_level(§9 Q5 表級暫登;欄位級=column_catalog 待後批)',
           'map_note', m.map_note))
FROM dataset_catalog d
LEFT JOIN annex_map m ON m.source_table = d.dataset
WHERE NOT EXISTS (
    SELECT 1 FROM world_channel_binding b
    WHERE b.source_table = d.dataset
      AND b.source_column IS NULL
      AND b.concept_key IS NOT DISTINCT FROM m.concept_key
);
"""


# ── 不變式（純函式;DDL/種子字串即被逐字執行之行為載體,對載體驗形=對行為驗形——#35 型3 註記同 E2 先例）──
def ddl_invariants(ddl: str) -> list[str]:
    """回傳被違反之不變式名清單（空=全守）。selftest 以本尊驗綠、壞變體驗紅。"""
    bad = []
    if "SET lock_timeout" not in ddl:
        bad.append("lock_timeout")
    if (ddl.count("CREATE TABLE IF NOT EXISTS world_concept_registry") != 1
            or ddl.count("CREATE TABLE IF NOT EXISTS world_channel_binding") != 1):
        bad.append("two_tables_idempotent")
    if not re.search(r"concept_key\s+text PRIMARY KEY", ddl):
        bad.append("concept_pk")
    if ddl.count("'entity','event','state','relation','quantity'") != 1:
        bad.append("category_closed_set")
    seven = ("concept_key", "category", "authoritative_binding_id", "ts_semantics",
             "knowability_rule", "cross_market_axis", "provenance", "finality_predicate")
    if not all(col in ddl for col in seven):
        bad.append("seven_column_carriers")
    if "GENERATED ALWAYS AS IDENTITY PRIMARY KEY" not in ddl:
        bad.append("binding_identity_pk")
    if "(mapping_status='mapped') = (concept_key IS NOT NULL)" not in ddl:
        bad.append("unmapped_biconditional")
    if "IN ('mapped','unmapped')" not in ddl:
        bad.append("mapping_status_closed")
    if "IN ('observation','derived')" not in ddl:
        bad.append("channel_role_closed")
    if "fk_auth_binding" not in ddl or "REFERENCES world_channel_binding(binding_id)" not in ddl:
        bad.append("auth_fk")
    if ddl.count("honesty_ledger_guard()") != 4 or ddl.count("DROP TRIGGER IF EXISTS") != 4:
        bad.append("four_guard_triggers")
    if "CREATE OR REPLACE FUNCTION" in ddl or "CREATE FUNCTION" in ddl:
        bad.append("guard_fn_not_self_made")
    if ddl.count("superseded_at") < 2:
        bad.append("append_only_versioning")
    if len(re.findall(r"provenance\s+jsonb NOT NULL", ddl)) != 2:
        bad.append("provenance_not_null")
    if "DEFAULT '未宣告'" not in ddl:
        bad.append("finality_default_undeclared")
    if "INSERT INTO" in ddl:
        bad.append("no_insert_in_ddl")
    if not re.search(r"decided_by\s+text\s*,", ddl):
        bad.append("human_sign_nullable_no_default")
    return bad


def seed_problems(concepts_sql: str, binding_sql: str, channels) -> list[str]:
    """種子不變式（純函式）:人簽欄不代填/冪等/pending 誠實/資料驅動/append-only/映射完備。"""
    bad = []
    if "decided_by" in concepts_sql or "decided_at" in concepts_sql:
        bad.append("concepts_touch_human_sign")
    if "ON CONFLICT (concept_key) DO NOTHING" not in concepts_sql:
        bad.append("concepts_not_idempotent")
    if "採認狀態" not in concepts_sql or "'pending'" not in concepts_sql:
        bad.append("concepts_admission_not_pending")
    if not all(f"'{k}'" in concepts_sql for k in SIX_CONCEPT_KEYS):
        bad.append("concepts_six_keys_incomplete")
    if concepts_sql.count("annex_f_entry") != 6:
        bad.append("concepts_not_exactly_six")
    if "FROM dataset_catalog" not in binding_sql:
        bad.append("binding_not_data_driven")
    if "NOT EXISTS" not in binding_sql:
        bad.append("binding_not_idempotent")
    if "'unmapped'" not in binding_sql or "CASE WHEN m.concept_key IS NULL" not in binding_sql:
        bad.append("binding_unmapped_default_missing")
    for sql in (concepts_sql, binding_sql):
        if "UPDATE " in sql or "DELETE " in sql:
            bad.append("seed_not_append_only")
            break
    keys = {c[0] for c in channels}
    if not keys <= set(SIX_CONCEPT_KEYS):
        bad.append("channel_unknown_concept_key")
    if keys != set(SIX_CONCEPT_KEYS):
        bad.append("channel_concept_uncovered")
    pairs = [(c[0], c[1]) for c in channels]
    if len(set(pairs)) != len(pairs):
        bad.append("channel_duplicate_mapping")
    if not all(c[1] in binding_sql for c in channels):
        bad.append("channel_missing_in_sql")
    return bad


# ── DB 面 ──
def _annex_tables_missing(cur) -> list[str]:
    """映射表列之 dataset 不在 dataset_catalog 者（fail-closed:有缺即拒種）。"""
    tables = sorted({c[1] for c in ANNEX_F_CHANNELS})
    cur.execute("SELECT dataset FROM dataset_catalog WHERE dataset = ANY(%s)", (tables,))
    have = {r[0] for r in cur.fetchall()}
    return [t for t in tables if t not in have]


def _check(conn) -> int:
    with conn.cursor() as cur:
        ok_all = True
        for tbl in ("world_concept_registry", "world_channel_binding"):
            cur.execute("SELECT to_regclass(%s)", (f"public.{tbl}",))
            exists = bool(cur.fetchone()[0])
            ok_all &= exists
            print(f"  {'✓' if exists else '·'} table {tbl} {'在' if exists else '不在（未 --apply）'}")
        if not ok_all:
            return 0
        for tbl in ("world_concept_registry", "world_channel_binding"):
            cur.execute("SELECT count(*) FROM pg_trigger "
                        "WHERE tgrelid = %s::regclass AND NOT tgisinternal", (tbl,))
            n = cur.fetchone()[0]
            print(f"  {'✓' if n == 2 else '✗'} {tbl} guard trigger {n}/2")
        cur.execute("SELECT count(*), count(decided_by) FROM world_concept_registry")
        n_c, n_signed = cur.fetchone()
        print(f"  概念列 {n_c}（已親簽採認 {n_signed}——空=待 hugo 附卷裁定）")
        cur.execute("SELECT mapping_status, count(*) FROM world_channel_binding "
                    "WHERE superseded_at IS NULL GROUP BY 1 ORDER BY 1")
        rows = cur.fetchall()
        print("  通道列:" + ("（空——種子待 --apply）" if not rows
                            else "; ".join(f"{k} {n}" for k, n in rows)))
    return 0


def _seed_dry(conn) -> int:
    """唯讀預覽:印種子 SQL＋以 live dataset_catalog 實跑筆數（零寫入）。"""
    binding_sql = build_binding_seed_sql()
    print("── 種子 ①（Annex F 六概念;decided_by 不入列）──")
    print(SEED_CONCEPTS_SQL)
    print("── 種子 ②（dataset_catalog → 通道全量;INSERT..SELECT 資料驅動）──")
    print(binding_sql)
    with conn.cursor() as cur:
        missing = _annex_tables_missing(cur)
        if missing:
            print(f"✗ 映射資料集不在 dataset_catalog:{missing}——fail-closed,--apply 會拒種")
            return 1
        cur.execute("SELECT count(*) FROM dataset_catalog")
        n_ds = cur.fetchone()[0]
        cur.execute("""
            WITH annex_map(concept_key, source_table) AS (VALUES {})
            SELECT count(*),
                   count(*) FILTER (WHERE m.concept_key IS NOT NULL),
                   count(*) FILTER (WHERE m.concept_key IS NULL)
            FROM dataset_catalog d LEFT JOIN annex_map m ON m.source_table = d.dataset
        """.format(", ".join(f"('{c[0]}', '{c[1]}')" for c in ANNEX_F_CHANNELS)))
        total, mapped, unmapped = cur.fetchone()
        print(f"── 預覽（live 實跑）:dataset_catalog {n_ds} 列 → 通道列 {total}"
              f"（mapped {mapped} / unmapped {unmapped};概念列 6）──")
    print("（未執行任何寫入;--apply 歸主 session 窗、須 hugo #6 明示）")
    return 0


def _apply(conn) -> int:
    from augur.core import db
    with db.transaction(conn) as cur:
        cur.execute("SELECT count(*) FROM pg_proc WHERE proname='honesty_ledger_guard'")
        if cur.fetchone()[0] == 0:
            print("✗ honesty_ledger_guard 函式不存在——先跑 migrate_honesty_guards_ddl.py --apply"
                  "（#12 不自造第二住所）")
            return 1
        missing = _annex_tables_missing(cur)
        if missing:
            print(f"✗ 映射資料集不在 dataset_catalog:{missing}——fail-closed 拒種（先修映射常數）")
            return 1
    with db.transaction(conn) as cur:
        cur.execute(DDL)
    print("✓ DDL 冪等完成（二表+四 trigger+fk_auth_binding）")
    with db.transaction(conn) as cur:
        cur.execute(SEED_CONCEPTS_SQL)
        cur.execute(build_binding_seed_sql())
    print("✓ 種子冪等完成（decided_by 全留空=待 hugo 附卷裁定親簽）")
    return _check(conn)


# ── 紅綠自測（#35:本尊驗綠、壞變體驗紅;免 DB 免 API 零 usage）──
def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'✓' if cond else '✗'} {name}")

    binding_sql = build_binding_seed_sql()
    chk("本尊 DDL 全不變式守住（綠）", ddl_invariants(DDL) == [])
    chk("本尊種子全不變式守住（綠）",
        seed_problems(SEED_CONCEPTS_SQL, binding_sql, ANNEX_F_CHANNELS) == [])
    # —— 壞變體驗紅（#35「凡新回歸鎖必先驗紅」之在檔常駐版;scratch 突變另證,見 commit/report）——
    chk("驗紅:拿掉歸類閉集 → category_closed_set 報違",
        "category_closed_set" in ddl_invariants(
            DDL.replace("'entity','event','state','relation','quantity'", "'x'")))
    chk("驗紅:拿掉 unmapped 雙條件 CHECK → 報違（WM.35 顯式性之鎖）",
        "unmapped_biconditional" in ddl_invariants(
            DDL.replace("CHECK ((mapping_status='mapped') = (concept_key IS NOT NULL)),", "")))
    chk("驗紅:少一支 trigger → four_guard_triggers 報違",
        "four_guard_triggers" in ddl_invariants(
            DDL.replace("DROP TRIGGER IF EXISTS trg_world_channel_binding_honesty_trunc "
                        "ON world_channel_binding;", "", 1)))
    chk("驗紅:DDL 自造 guard 函式 → 報違（#12 單一住所）",
        "guard_fn_not_self_made" in ddl_invariants(
            DDL + "\nCREATE OR REPLACE FUNCTION honesty_ledger_guard() RETURNS trigger AS $$ $$;"))
    chk("驗紅:DDL 夾帶 INSERT → 報違（種子與 DDL 分離）",
        "no_insert_in_ddl" in ddl_invariants(DDL + "\nINSERT INTO world_concept_registry VALUES (1);"))
    chk("驗紅:拿掉 superseded_at → append_only_versioning 報違",
        "append_only_versioning" in ddl_invariants(DDL.replace("superseded_at", "obsolete_at")))
    chk("驗紅:decided_by 加 DEFAULT → 報違（人簽欄不得有機器預設）",
        "human_sign_nullable_no_default" in ddl_invariants(
            DDL.replace("decided_by         text,", "decided_by         text DEFAULT 'ai',")))
    chk("驗紅:種子夾帶 decided_by → 報違（不代打人簽）",
        "concepts_touch_human_sign" in seed_problems(
            SEED_CONCEPTS_SQL.replace("(concept_key, category", "(concept_key, decided_by, category"),
            binding_sql, ANNEX_F_CHANNELS))
    chk("驗紅:種子拿掉 ON CONFLICT → 報違（冪等）",
        "concepts_not_idempotent" in seed_problems(
            SEED_CONCEPTS_SQL.replace("ON CONFLICT (concept_key) DO NOTHING", ""),
            binding_sql, ANNEX_F_CHANNELS))
    chk("驗紅:種子 pending 假關 → 報違（#15 不假關）",
        "concepts_admission_not_pending" in seed_problems(
            SEED_CONCEPTS_SQL.replace("'pending'", "'accepted'"),
            binding_sql, ANNEX_F_CHANNELS))
    chk("驗紅:通道種子改 hardcode（去 FROM dataset_catalog）→ 報違（#29b）",
        "binding_not_data_driven" in seed_problems(
            SEED_CONCEPTS_SQL, binding_sql.replace("FROM dataset_catalog", "FROM (VALUES ('x')) v"),
            ANNEX_F_CHANNELS))
    chk("驗紅:映射重複列 → 報違",
        "channel_duplicate_mapping" in seed_problems(
            SEED_CONCEPTS_SQL, binding_sql, ANNEX_F_CHANNELS + (ANNEX_F_CHANNELS[0],)))
    chk("驗紅:映射掛未知概念鍵 → 報違",
        "channel_unknown_concept_key" in seed_problems(
            SEED_CONCEPTS_SQL, binding_sql,
            ANNEX_F_CHANNELS + (("xx.unknown", "TaiwanStockPrice", "observation", "n"),)))
    chk("驗紅:六概念漏映射（拿掉 tw.delisting 通道）→ 報違",
        "channel_concept_uncovered" in seed_problems(
            SEED_CONCEPTS_SQL, binding_sql,
            tuple(c for c in ANNEX_F_CHANNELS if c[0] != "tw.delisting")))
    # 純函式雙向:壞變體之 binding SQL 亦由本尊函式重生成可驗（餵真輸入,#35 規則1）
    alt = build_binding_seed_sql(ANNEX_F_CHANNELS[:1])
    chk("build_binding_seed_sql 為純函式:不同輸入生不同 SQL 且仍資料驅動",
        alt != binding_sql and "FROM dataset_catalog" in alt)
    print("自測:全通過 ✓" if ok else "自測:有失敗 ✗")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="World Concept Registry 二表 DDL＋種子（WM.35/36;G0 格3 照案;--apply 須 hugo 明示）")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--seed-dry", dest="seed_dry", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    no_args = not (a.check or a.seed_dry or a.apply)
    if no_args:
        print(__doc__.split("執行指令矩陣")[-1].split("------------\n")[-1])
    from augur.core import db
    if no_args:
        try:
            with db.connect() as conn:
                return _check(conn)
        except Exception as e:  # noqa: BLE001 — 無參數須 graceful 不裸 traceback（#29a）
            print(f"（--check 需 DB;現不可達:{e};--selftest 免 DB 可跑）")
            return 0
    with db.connect() as conn:
        if a.apply:
            return _apply(conn)
        if a.seed_dry:
            return _seed_dry(conn)
        return _check(conn)


if __name__ == "__main__":
    sys.exit(main())
