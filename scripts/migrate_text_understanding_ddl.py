#!/usr/bin/env python
"""知識全文理解層 schema 遷移(T0+M5+M4)— S3-S5 全部 DDL 之單一住所,一次冪等落地。

🎯 這支在做什麼(白話):建立「全文→逐句→逐字理解→嵌入」的接收 schema——
   knowledge_item_text(L1 OA/CC 全文,license 白名單硬擋)、knowledge_sentence(L2 逐句,
   text_id|itext_id 二擇一)、knowledge_concordance(L2 逐字索引,HASH 16 分區)、
   knowledge_lexicon(L3 公版辭書/註疏定義,限 public_domain)、knowledge_build_meta(L2 進度游標)、
   philosophy_chunk 泛化(L4:itext_id 補欄+二擇一 CHECK)+ philosophy_work.review_flag(T-1 稽核欄)
   + 嵌入表世代(M5/P6):knowledge_{lexicon,sentence}_embedding 複合鍵 (id, model_tag)
   (既有單欄 PK 表=就地遷移;防換模重嵌 ON CONFLICT 靜默零寫入假成功)+ knowledge_embed_ledger
   (S5 排除帳落庫非 stdout)。嵌入表 DDL 自 embed_knowledge.py 收編至此=單一住所(#12)。
   + S4 統計層 DDL(M4,拍板 P1-P3 2026-07-04):STATS_DDL 全清單收編至此=正式住所
   (build_cross_school_stats.py import 同一清單自舉=機器強制同步)——group_kind 四值
   ('school','thinker','domain','taxonomy',P1)、knowledge_domain 維度表(收編 domain_map
   為域啟用 SSOT,P2)、knowledge_item_term_stats item 側平行分母(P3,禁動 work FK 脊椎)、
   knowledge_group_affinity.pair_rank(taxonomy pair top-K 截斷之稽核欄)、
   method 種子 cnt_term_item/agg_domain_rollup/agg_taxonomy_rollup(四值 kind 內合法擴列)。
   全部 IF NOT EXISTS / 先查 pg catalog 才 ADD,重跑零副作用;
   先決 = knowledge_item 已由計畫②(harvest)建成(knowledge_item_text FK 依賴)。
守 #6(冪等、重跑安全)· #1(license CHECK 硬擋版權未明/AI 生成)· #12(DDL 單一住所)·
   #15(驗證清單=實查 pg catalog)· CLAUDE #29。
   SSOT=reports/augur_knowledge_text_understanding_plan_20260702.md §二 +
   reports/augur_knowhow_e2e_pipeline_plan_20260704.md §3-S4/S5/§4 M4/M5/§8 P1-P3/P6 +
   reports/augur_cross_school_stats_schema_20260704.md。

執行指令矩陣:
  python scripts/migrate_text_understanding_ddl.py           # 冪等執行全部 DDL + 印驗證清單(安全預設)
  python scripts/migrate_text_understanding_ddl.py --check   # 唯讀:只印驗證清單、不執行 DDL
"""
import sys
import argparse

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db

N_PARTITIONS = 16

# (標籤, 冪等 DDL);順序有相依:item_text 先建(chunk.itext_id FK 依賴)
DDL = [
    ("table knowledge_item_text", """
        CREATE TABLE IF NOT EXISTS knowledge_item_text (
          itext_id   serial PRIMARY KEY,
          item_id    int NOT NULL REFERENCES knowledge_item(item_id),
          seq        int NOT NULL,
          content    text NOT NULL,
          language   varchar(8),
          source_url text NOT NULL,
          license    varchar(64) NOT NULL CHECK (license IN ('public_domain','cc-by','cc-by-sa','cc0','owned_local')),
          fetched_at timestamptz DEFAULT now(),
          UNIQUE (item_id, seq)
        )"""),
    ("index idx_itext_item", "CREATE INDEX IF NOT EXISTS idx_itext_item ON knowledge_item_text (item_id)"),
    ("table knowledge_sentence", """
        CREATE TABLE IF NOT EXISTS knowledge_sentence (
          sent_id    serial PRIMARY KEY,
          text_id    int REFERENCES philosophy_work_text(text_id),
          itext_id   int REFERENCES knowledge_item_text(itext_id),
          seq        int NOT NULL,
          sentence   text NOT NULL,
          language   varchar(8) NOT NULL,
          char_start int NOT NULL,
          char_end   int NOT NULL,
          CHECK (num_nonnulls(text_id, itext_id) = 1)
        )"""),
    ("index uq_sent_text(partial unique)",
     "CREATE UNIQUE INDEX IF NOT EXISTS uq_sent_text ON knowledge_sentence (text_id, seq) WHERE text_id IS NOT NULL"),
    ("index uq_sent_itext(partial unique)",
     "CREATE UNIQUE INDEX IF NOT EXISTS uq_sent_itext ON knowledge_sentence (itext_id, seq) WHERE itext_id IS NOT NULL"),
    ("table knowledge_concordance(PARTITION BY HASH)", """
        CREATE TABLE IF NOT EXISTS knowledge_concordance (
          term     text NOT NULL,
          language varchar(8) NOT NULL,
          sent_id  int NOT NULL,
          position int NOT NULL,
          PRIMARY KEY (term, sent_id, position)
        ) PARTITION BY HASH (term)"""),
    # p0..p15 分區於 main() 迴圈建(同樣 IF NOT EXISTS)
    ("table knowledge_lexicon", """
        CREATE TABLE IF NOT EXISTS knowledge_lexicon (
          lex_id         serial PRIMARY KEY,
          term           text NOT NULL,
          term_display   text,
          language       varchar(8) NOT NULL,
          definition     text NOT NULL,
          source_work_id int NOT NULL REFERENCES philosophy_work(work_id),
          source_locator text,
          lex_type       varchar(16) CHECK (lex_type IN ('dictionary','commentary','thesaurus')),
          license        varchar(64) NOT NULL DEFAULT 'public_domain' CHECK (license='public_domain'),
          UNIQUE NULLS NOT DISTINCT (term, language, source_work_id, source_locator)
        )"""),
    ("index idx_lex_term", "CREATE INDEX IF NOT EXISTS idx_lex_term ON knowledge_lexicon (language, term)"),
    ("table knowledge_build_meta", """
        CREATE TABLE IF NOT EXISTS knowledge_build_meta (
          scope          varchar(32) PRIMARY KEY,
          cursor_sent_id bigint NOT NULL DEFAULT 0,
          updated_at     timestamptz DEFAULT now()
        )"""),
    ("column philosophy_chunk.itext_id",
     "ALTER TABLE philosophy_chunk ADD COLUMN IF NOT EXISTS itext_id int REFERENCES knowledge_item_text(itext_id)"),
    ("philosophy_chunk.text_id DROP NOT NULL", "ALTER TABLE philosophy_chunk ALTER COLUMN text_id DROP NOT NULL"),
    ("philosophy_chunk.work_id DROP NOT NULL", "ALTER TABLE philosophy_chunk ALTER COLUMN work_id DROP NOT NULL"),
    ("index uq_chunk_itext(partial unique)",
     "CREATE UNIQUE INDEX IF NOT EXISTS uq_chunk_itext ON philosophy_chunk (itext_id, chunk_seq) WHERE itext_id IS NOT NULL"),
    ("column philosophy_work.review_flag(T-1 稽核欄)",
     "ALTER TABLE philosophy_work ADD COLUMN IF NOT EXISTS review_flag boolean"),
    # ── admin 控制台 P0(計畫 §〇.3③/拍板P2-P3new,#1 禁AI生成+access_scope 隔離)──────────
    ("column knowledge_item_text.source_type(禁 AI 生成硬擋)",
     "ALTER TABLE knowledge_item_text ADD COLUMN IF NOT EXISTS source_type varchar(24)"),
    ("column knowledge_item_text.access_scope(對外/本機私有隔離)",
     "ALTER TABLE knowledge_item_text ADD COLUMN IF NOT EXISTS access_scope varchar(16) NOT NULL DEFAULT 'public'"),
    # ── M5/P6:嵌入表世代(收編自 embed_knowledge.py=單一住所 #12)──────────────
    # dim=384 寫死=本表世代之維度(e5-small);異維模型=新表世代(embedspec 命名),不改本表
    ("extension vector(pgvector,嵌入表依賴)", "CREATE EXTENSION IF NOT EXISTS vector"),
    ("table knowledge_lexicon_embedding(P6 複合鍵世代)", """
        CREATE TABLE IF NOT EXISTS knowledge_lexicon_embedding (
          lex_id    int NOT NULL REFERENCES knowledge_lexicon(lex_id) ON DELETE CASCADE,
          embedding vector(384) NOT NULL,
          model_tag varchar(64) NOT NULL,
          PRIMARY KEY (lex_id, model_tag)
        )"""),
    ("table knowledge_sentence_embedding(P6 複合鍵世代)", """
        CREATE TABLE IF NOT EXISTS knowledge_sentence_embedding (
          sent_id   int NOT NULL REFERENCES knowledge_sentence(sent_id) ON DELETE CASCADE,
          embedding vector(384) NOT NULL,
          model_tag varchar(64) NOT NULL,
          PRIMARY KEY (sent_id, model_tag)
        )"""),
    ("table knowledge_embed_ledger(S5 排除帳落庫非 stdout)", """
        CREATE TABLE IF NOT EXISTS knowledge_embed_ledger (
          ledger_id     serial PRIMARY KEY,
          scope         varchar(32) NOT NULL,
          model_tag     varchar(64) NOT NULL,
          processed     int NOT NULL,
          embedded      int NOT NULL,
          junk_excluded int NOT NULL,
          note          text,
          run_at        timestamptz DEFAULT now()
        )"""),
]

# P6:既有單欄 PK 嵌入表 → (id, model_tag) 複合鍵就地遷移(表, id 欄)
EMBED_PK_MIGRATION = [
    ("knowledge_lexicon_embedding", "lex_id"),
    ("knowledge_sentence_embedding", "sent_id"),
]

# (名稱, 表, 定義);ADD CONSTRAINT 無 IF NOT EXISTS → 先查 pg_constraint
CONSTRAINTS = [
    ("chk_itext_source_type", "knowledge_item_text",
     "CHECK (source_type IS NULL OR source_type <> 'ai_generated')"),   # #1 禁 AI 生成入庫(admin P0)
    ("chk_itext_access_scope", "knowledge_item_text",
     "CHECK (access_scope IN ('public','local_private'))"),             # 對外/本機私有隔離(拍板P2)
    ("chk_itext_owned_local_private", "knowledge_item_text",
     "CHECK (license <> 'owned_local' OR access_scope = 'local_private')"),  # owned_local⇒local_private 隔離命門 v1.36.0
    # ↑ R1(2026-07-14 對抗審查):此 CHECK 存 live DB 但曾無 repo migration 重建→換機/重建 schema 漏命門牆;
    #   codify 於此(與其餘 chk_itext_* 同住#12);ensure_constraint 冪等,現機已在=no-op、新機才建。
    ("chk_chunk_src", "philosophy_chunk", "CHECK (num_nonnulls(text_id, itext_id) = 1)"),
    ("chk_chunk_work", "philosophy_chunk", "CHECK ((text_id IS NULL) = (work_id IS NULL))"),
]


def precheck(cur):
    """先決:knowledge_item(計畫② harvest)與哲學層既有表須已建成(FK 依賴)。"""
    cur.execute("SELECT to_regclass('knowledge_item'), to_regclass('philosophy_work_text'), "
                "to_regclass('philosophy_work'), to_regclass('philosophy_chunk')")
    ki, pwt, pw, pc = cur.fetchone()
    if not ki:
        sys.exit("先決缺:knowledge_item 未建(knowledge_item_text FK 依賴)\n"
                 "→ 先跑計畫② harvest 建表:python scripts/harvest_knowledge.py --migrate-only")
    if not (pwt and pw and pc):
        sys.exit("先決缺:philosophy_work_text / philosophy_work / philosophy_chunk 未齊"
                 "(哲學層既有 schema)→ 請先確認哲學管線已建(見 memory/哲學素養框架層)")


def ensure_constraint(cur, name, table, defn):
    cur.execute("SELECT 1 FROM pg_constraint WHERE conname=%s AND conrelid=to_regclass(%s)", (name, table))
    if cur.fetchone():
        return "已在"
    cur.execute(f"ALTER TABLE {table} ADD CONSTRAINT {name} {defn}")
    return "新建"


def _pk_cols(cur, table):
    cur.execute("""SELECT a.attname FROM pg_index i
        JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
        WHERE i.indrelid = to_regclass(%s) AND i.indisprimary""", (table,))
    return {r[0] for r in cur.fetchall()}


def ensure_composite_pk(cur, table, idcol):
    """P6:單欄 PK → (idcol, model_tag) 複合鍵就地遷移(冪等;防換模重嵌 DO NOTHING 靜默假成功)。"""
    if "model_tag" in _pk_cols(cur, table):
        return "已在(複合鍵)"
    cur.execute("SELECT conname FROM pg_constraint WHERE conrelid=to_regclass(%s) AND contype='p'", (table,))
    pkname = cur.fetchone()[0]
    cur.execute(f"ALTER TABLE {table} DROP CONSTRAINT {pkname}, ADD PRIMARY KEY ({idcol}, model_tag)")
    return "遷移(單欄→複合鍵)"


def verify(cur, applied=False):
    """驗證清單=實查 pg catalog(#15);回傳全數通過與否。jieba 為 T2-T4 前置,缺=警告不擋 DDL。
    P6 嵌入表世代物件三態:✓ 已符 / ✗ 應在而不在(applied=True 時計失敗)/ 待(--check 且遷移未執行,
    明列不計失敗——embed_knowledge 端另有 runtime fail-closed 防呆,見該檔)。"""
    checks = []
    pending = []
    for t in ("knowledge_item_text", "knowledge_sentence", "knowledge_concordance",
              "knowledge_lexicon", "knowledge_build_meta"):
        cur.execute("SELECT to_regclass(%s)", (t,))
        checks.append((f"table  {t}", bool(cur.fetchone()[0])))
    for t, idcol in EMBED_PK_MIGRATION + [("knowledge_embed_ledger", None)]:
        cur.execute("SELECT to_regclass(%s)", (t,))
        exists = bool(cur.fetchone()[0])
        ok = exists and (idcol is None or "model_tag" in _pk_cols(cur, t))
        label = f"table  {t}" + (f" pkey=({idcol},model_tag)" if idcol else "")
        if ok or applied:
            checks.append((label, ok))
        else:
            pending.append(label)
    cur.execute("SELECT count(*) FROM pg_inherits WHERE inhparent = to_regclass('knowledge_concordance')")
    nparts = cur.fetchone()[0]
    checks.append((f"partitions knowledge_concordance_p0..p{N_PARTITIONS - 1}({nparts}/{N_PARTITIONS})",
                   nparts == N_PARTITIONS))
    for idx in ("idx_itext_item", "uq_sent_text", "uq_sent_itext", "idx_conc_lang_term",
                "idx_lex_term", "uq_chunk_itext"):
        cur.execute("SELECT to_regclass(%s)", (idx,))
        checks.append((f"index  {idx}", bool(cur.fetchone()[0])))
    cur.execute("SELECT count(*) FROM pg_constraint WHERE contype='u' AND conrelid=to_regclass('knowledge_lexicon')")
    checks.append(("unique knowledge_lexicon(term,language,work,locator) NULLS NOT DISTINCT",
                   cur.fetchone()[0] >= 1))
    for name, table, _ in CONSTRAINTS:
        cur.execute("SELECT 1 FROM pg_constraint WHERE conname=%s AND conrelid=to_regclass(%s)", (name, table))
        checks.append((f"check  {table}.{name}", bool(cur.fetchone())))
    cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema=current_schema() "
                "AND table_name='philosophy_chunk' AND column_name='itext_id'")
    checks.append(("column philosophy_chunk.itext_id", cur.fetchone()[0] == 1))
    cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema=current_schema() "
                "AND table_name='philosophy_chunk' AND column_name IN ('text_id','work_id') AND is_nullable='YES'")
    checks.append(("column philosophy_chunk.text_id/work_id 可空", cur.fetchone()[0] == 2))
    cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema=current_schema() "
                "AND table_name='philosophy_work' AND column_name='review_flag'")
    checks.append(("column philosophy_work.review_flag", cur.fetchone()[0] == 1))

    print("── 驗證清單(實查 pg catalog)──")
    for label, ok in checks:
        print(f"  {'✓' if ok else '✗'} {label}")
    for label in pending:
        print(f"  待 {label}(P6/M5 遷移未執行 → python scripts/migrate_text_understanding_ddl.py)")
    try:
        import jieba  # noqa: F401
        print("  ✓ import jieba(T2-T4 中文分詞前置)")
    except ImportError:
        print("  ⚠ jieba 未安裝(T2-T4 前置;不影響 DDL)→ pip install jieba")
    n_ok = sum(1 for _, ok in checks if ok)
    print(f"→ {n_ok}/{len(checks)} 物件存在" + (f"、{len(pending)} 項待遷移" if pending else ""))
    return n_ok == len(checks)


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--check", action="store_true")
    args, _ = ap.parse_known_args()
    with db.connect() as conn:
        if not args.check:
            with db.transaction(conn) as cur:
                precheck(cur)
            with db.transaction(conn) as cur:  # 全部 DDL 單一交易:任一失敗整批回滾(#6)
                for label, sql in DDL:
                    cur.execute(sql)
                    print(f"  DDL 執行:{label}")
                for i in range(N_PARTITIONS):
                    cur.execute(f"CREATE TABLE IF NOT EXISTS knowledge_concordance_p{i} "
                                f"PARTITION OF knowledge_concordance FOR VALUES WITH (MODULUS {N_PARTITIONS}, REMAINDER {i})")
                print(f"  DDL 執行:partitions knowledge_concordance_p0..p{N_PARTITIONS - 1}")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_conc_lang_term ON knowledge_concordance (language, term)")
                print("  DDL 執行:index idx_conc_lang_term")
                for name, table, defn in CONSTRAINTS:
                    print(f"  constraint {table}.{name}:{ensure_constraint(cur, name, table, defn)}")
                for table, idcol in EMBED_PK_MIGRATION:
                    print(f"  pkey {table}:{ensure_composite_pk(cur, table, idcol)}")
        with db.transaction(conn) as cur:
            ok = verify(cur, applied=not args.check)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
