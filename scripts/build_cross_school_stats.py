#!/usr/bin/env python
"""跨學說統計層 builder — (d)(e)(f) 族擴充:聚合基表 → 有界物化 affinity(合成 A/B/C 三案、fatal/major 全修)。

🎯 這支在做什麼(白話):把已窮舉物化的逐字層(knowledge_concordance ~49.1M postings、
   knowledge_sentence 1.54M 句)以純計算方法(counting / closed_form_stat / string_rule / sql_join,
   =knowledge_derivation_method 四值 CHECK,DB 硬擋 embedding/LLM)聚合成:
     L1 計數基表:knowledge_term_stats(term×work)+ knowledge_term_corpus_stats(term×語言,分母 SSOT)
     L2 統計詞彙閘:knowledge_stat_vocab(en 未去 stopword 之顯式對策;閘參數=操作值不入 schema)
     L3 歸屬鏈:knowledge_school_thinker_seed(proponents string_rule + 既存 school_thinker 表匯入;
        人工僅得 confirm/reject,confirmed 才投影 knowledge_edge thinker_of_school=fail-closed)
     L4 群組聚合:knowledge_term_group_stats(group_kind ∈ school/thinker;school 現況近空=誠實揭露,
        thinker 軌 173 位有全文=當下非空交付;學說語料補救三選一=決策層另拍板)
     L5 共現:knowledge_term_cooccurrence(唯一 pair 級物化;vocab 閘+min-count+zh 詞↔構成字排除;
        anchor-block×sent_terms staging,不逐分區自交——concordance 分區鍵=HASH(term) 實查)
     L6 親和:knowledge_term_affinity(npmi/jaccard/llr,長格式一列一公式一 method_key,top-K 有界)
        + knowledge_term_group_affinity(keyness)+ knowledge_group_affinity(school 全量/thinker top-K)
   嵌入=索引非內容:本 builder 零向量;Milvus 只鏡 sentence/lexicon 嵌入,統計永不進 Milvus。
守 #6(冪等+游標 resume)· #9/#10/#15(數字全 SQL 實算、吞吐誠實印出)· #28(本地零 usage)· CLAUDE #29。

執行指令矩陣:
  python scripts/build_cross_school_stats.py                      # 無參數:唯讀資訊矩陣(表/游標/待處理/學說鏈誠實現況)
  python scripts/build_cross_school_stats.py --phase ddl --run    # DDL+method 種子(冪等;正式住所=migrate_text_understanding_ddl.py,本檔內嵌同文以利自舉)
  python scripts/build_cross_school_stats.py --phase stats --run  # L1 逐 concordance 分區聚合(游標 resume)
  python scripts/build_cross_school_stats.py --phase vocab --run  # L2 詞彙閘(重跑=重置下游共現/親和,會印警告)
  python scripts/build_cross_school_stats.py --phase seed --run   # L3 種子(誠實印匹配率+全文覆蓋=揭露學說層空集)
  python scripts/build_cross_school_stats.py --list-seeds         # 唯讀:列 seed 現況
  python scripts/build_cross_school_stats.py --confirm-seed 85:123 --run   # 人工確認(決策層;僅改 review_status)
  python scripts/build_cross_school_stats.py --phase edge --run   # L3 投影 edge(work_of_thinker 全量+confirmed thinker_of_school)
  python scripts/build_cross_school_stats.py --phase groupstats --run
  python scripts/build_cross_school_stats.py --phase cooc --run   # L5 staging(逐分區游標)+anchor-block(游標)
  python scripts/build_cross_school_stats.py --phase affinity --run
  python scripts/build_cross_school_stats.py --phase groupaff --run
  python scripts/build_cross_school_stats.py --phase metrics --run
  python scripts/build_cross_school_stats.py --phase charter --run  # 宣稱列(不含於 all;先印全文=用戶過目後才入庫)
  python scripts/build_cross_school_stats.py --phase all --run    # ddl→stats→vocab→seed→edge→groupstats→cooc→affinity→groupaff→metrics
  python scripts/build_cross_school_stats.py --phase all --run --smoke   # 微測:p0 分區+2 blocks+zh 先行(寫入=真值子集)
  python scripts/build_cross_school_stats.py --phase cooc --run --limit 4  # 本次只推進 4 個分區/區塊(配額護欄 #28)
"""
import time
import argparse

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path

from augur.core import db

N_PARTITIONS = 16                 # knowledge_concordance 16 hash 分區(實查 pg_get_partkeydef='HASH (term)')
BLOCK_SIZE = 500                  # cooc anchor block 大小(操作值)
DEFAULTS = {                      # 全部=操作值(#27 實驗中,印 log 不入 schema;調整不需 ALTER)
    "gate_topband": {"en": 200, "zh": 100},   # 頻率帶排除(the/of/之/不 在庫=實測,必須顯式閘)
    "gate_dfmin": 3,
    "gate_cap": {"en": 30000, "zh": 10000},
    "min_cooc": 5,
    "topk_term": 50,              # term_affinity 每 anchor 每 stat 上限
    "topm_group": 500,            # term_group_affinity 每群每 stat 上限
    "topk_grouppair": 20,         # thinker×thinker 對每 anchor 上限(school=946 上界全量)
    "logodds_a0": 500.0,          # Monroe 2008 informative Dirichlet prior 總量
}
CLEAN = "w.review_flag = false AND w.corpus_class = 'literary'"   # W1 目標形 fail-closed(NULL 不放行)

# ---------------------------------------------------------------------------
# DDL(冪等;與交付 ddl_sql 同文。正式住所=scripts/migrate_text_understanding_ddl.py,
# 本檔內嵌同一份以利自舉;兩處必須同步改)
# ---------------------------------------------------------------------------
DDL = [
    ("knowledge_derivation_method", """
CREATE TABLE IF NOT EXISTS knowledge_derivation_method (
  method_key  varchar(64) PRIMARY KEY,
  method_kind varchar(24) NOT NULL CHECK (method_kind IN ('counting','closed_form_stat','string_rule','sql_join')),
  definition  text NOT NULL
)"""),
    ("knowledge_term_stats", """
CREATE TABLE IF NOT EXISTS knowledge_term_stats (
  term       text        NOT NULL,
  language   varchar(8)  NOT NULL,
  work_id    int         NOT NULL REFERENCES philosophy_work(work_id),
  tf         int         NOT NULL,
  df_works   int         NOT NULL,
  method_key varchar(64) NOT NULL REFERENCES knowledge_derivation_method(method_key),
  PRIMARY KEY (term, language, work_id)
)"""),
    ("knowledge_term_corpus_stats", """
CREATE TABLE IF NOT EXISTS knowledge_term_corpus_stats (
  term       text        NOT NULL,
  language   varchar(8)  NOT NULL,
  tf_total   bigint      NOT NULL,
  df_works   int         NOT NULL,
  df_sents   bigint      NOT NULL,
  method_key varchar(64) NOT NULL REFERENCES knowledge_derivation_method(method_key),
  PRIMARY KEY (term, language)
)"""),
    ("knowledge_stat_vocab", """
CREATE TABLE IF NOT EXISTS knowledge_stat_vocab (
  term        text        NOT NULL,
  language    varchar(8)  NOT NULL,
  gate_reason varchar(24) NOT NULL CHECK (gate_reason IN ('freq_gate','lexicon_hit')),
  method_key  varchar(64) NOT NULL REFERENCES knowledge_derivation_method(method_key),
  PRIMARY KEY (term, language)
)"""),
    ("knowledge_school_thinker_seed", """
CREATE TABLE IF NOT EXISTS knowledge_school_thinker_seed (
  school_id     int         NOT NULL REFERENCES philosophy_school(school_id),
  thinker_id    int         NOT NULL REFERENCES philosophy_thinker(thinker_id),
  matched_text  text        NOT NULL,
  match_rule    varchar(24) NOT NULL CHECK (match_rule IN ('exact_name','normalized_name','name_zh','prior_table')),
  review_status varchar(12) NOT NULL DEFAULT 'seed' CHECK (review_status IN ('seed','confirmed','rejected')),
  method_key    varchar(64) NOT NULL REFERENCES knowledge_derivation_method(method_key),
  PRIMARY KEY (school_id, thinker_id)
)"""),
    ("knowledge_term_group_stats", """
CREATE TABLE IF NOT EXISTS knowledge_term_group_stats (
  group_kind varchar(12) NOT NULL CHECK (group_kind IN ('school','thinker')),
  group_id   int         NOT NULL,
  term       text        NOT NULL,
  language   varchar(8)  NOT NULL,
  tf         bigint      NOT NULL,
  df_works   int         NOT NULL,
  method_key varchar(64) NOT NULL REFERENCES knowledge_derivation_method(method_key),
  PRIMARY KEY (group_kind, group_id, term, language)
)"""),
    ("knowledge_term_cooccurrence", """
CREATE TABLE IF NOT EXISTS knowledge_term_cooccurrence (
  term_a     text        NOT NULL,
  term_b     text        NOT NULL,
  language   varchar(8)  NOT NULL,
  cooc_sents bigint      NOT NULL,
  cooc_works int         NOT NULL,
  method_key varchar(64) NOT NULL REFERENCES knowledge_derivation_method(method_key),
  PRIMARY KEY (language, term_a, term_b),
  CHECK (term_a < term_b)
)"""),
    ("knowledge_term_affinity", """
CREATE TABLE IF NOT EXISTS knowledge_term_affinity (
  term_a     text             NOT NULL,
  term_b     text             NOT NULL,
  language   varchar(8)       NOT NULL,
  stat_key   varchar(16)      NOT NULL CHECK (stat_key IN ('npmi','jaccard','llr')),
  stat_value double precision NOT NULL,
  basis_n    bigint           NOT NULL,
  rank_in_a  smallint         NOT NULL,
  method_key varchar(64)      NOT NULL REFERENCES knowledge_derivation_method(method_key),
  PRIMARY KEY (term_a, term_b, language, stat_key)
)"""),
    ("knowledge_term_group_affinity", """
CREATE TABLE IF NOT EXISTS knowledge_term_group_affinity (
  group_kind    varchar(12)      NOT NULL CHECK (group_kind IN ('school','thinker')),
  group_id      int              NOT NULL,
  term          text             NOT NULL,
  language      varchar(8)       NOT NULL,
  stat_key      varchar(24)      NOT NULL CHECK (stat_key IN ('keyness_llr','log_odds_dirichlet','tf_share')),
  stat_value    double precision NOT NULL,
  basis_n       bigint           NOT NULL,
  rank_in_group smallint         NOT NULL,
  method_key    varchar(64)      NOT NULL REFERENCES knowledge_derivation_method(method_key),
  PRIMARY KEY (group_kind, group_id, term, language, stat_key)
)"""),
    ("knowledge_group_affinity", """
CREATE TABLE IF NOT EXISTS knowledge_group_affinity (
  group_kind varchar(12)      NOT NULL CHECK (group_kind IN ('school','thinker')),
  group_a    int              NOT NULL,
  group_b    int              NOT NULL,
  language   varchar(8)       NOT NULL,
  stat_key   varchar(24)      NOT NULL CHECK (stat_key IN ('tfidf_cosine_counts','keyness_topk_jaccard')),
  stat_value double precision NOT NULL,
  basis_n    bigint           NOT NULL,
  method_key varchar(64)      NOT NULL REFERENCES knowledge_derivation_method(method_key),
  PRIMARY KEY (group_kind, group_a, group_b, language, stat_key),
  CHECK (group_a < group_b)
)"""),
    ("knowledge_alignment", """
CREATE TABLE IF NOT EXISTS knowledge_alignment (
  align_id     serial PRIMARY KEY,
  grain        varchar(16) CHECK (grain IN ('chapter','quote')),
  src_sent_id  int,
  dst_sent_id  int,
  src_work_id  int,
  dst_work_id  int,
  anchor       text NOT NULL,
  matched_text text,
  method_key   varchar(64) NOT NULL REFERENCES knowledge_derivation_method(method_key)
)"""),
    ("knowledge_edge", """
CREATE TABLE IF NOT EXISTS knowledge_edge (
  edge_id    serial PRIMARY KEY,
  predicate  varchar(32) NOT NULL CHECK (predicate IN
    ('term_in_work','term_defined_by','work_of_thinker','thinker_of_school','work_in_taxonomy','work_quotes_work')),
  src_id     int NOT NULL,
  dst_id     int NOT NULL,
  provenance varchar(16) CHECK (provenance IN ('join','string_rule','counting')),
  method_key varchar(64) NOT NULL REFERENCES knowledge_derivation_method(method_key),
  UNIQUE (predicate, src_id, dst_id)
)"""),
    ("knowledge_edge.evidence_n(族內擴欄)", """
ALTER TABLE knowledge_edge ADD COLUMN IF NOT EXISTS evidence_n int NOT NULL DEFAULT 1"""),
    ("knowledge_coverage_metric", """
CREATE TABLE IF NOT EXISTS knowledge_coverage_metric (
  metric_date date,
  metric_key  varchar(32),
  numerator   bigint,
  denominator bigint,
  note        text,
  PRIMARY KEY (metric_date, metric_key)
)"""),
    ("knowledge_capability_charter", """
CREATE TABLE IF NOT EXISTS knowledge_capability_charter (
  layer         varchar(32) PRIMARY KEY,
  can_answer    text NOT NULL,
  cannot_answer text NOT NULL,
  forbidden_pat text
)"""),
    ("knowledge_sent_terms_stage(推導快取,零新事實,可 TRUNCATE 重建)", """
CREATE UNLOGGED TABLE IF NOT EXISTS knowledge_sent_terms_stage (
  language varchar(8) NOT NULL,
  term     text       NOT NULL,
  sent_id  int        NOT NULL,
  work_id  int        NOT NULL,
  PRIMARY KEY (language, term, sent_id)
)"""),
    ("comments(口徑入庫)", """
COMMENT ON COLUMN knowledge_term_affinity.rank_in_a IS
  '口徑:僅「通過 vocab 閘+min-cooc 門檻之已物化 pair」中的名次,非全域 top-K(低頻 pair 可按需 SQL 對 concordance 精確重算)';
COMMENT ON TABLE knowledge_term_cooccurrence IS
  '唯一 pair 級物化:兩端∈knowledge_stat_vocab+cooc_sents≥min_cooc;zh 排除子字串 pair(詞↔構成字 P=1 artifact);其餘 pair=按需 SQL 精確重算';
COMMENT ON COLUMN knowledge_term_stats.df_works IS
  '語料級 df 之反正規化副本(SSOT=knowledge_term_corpus_stats.df_works);同一 phase 同一掃描寫入,重建必同步';
COMMENT ON COLUMN knowledge_group_affinity.basis_n IS
  'tfidf_cosine_counts=兩向量共享 vocab 詞數;keyness_topk_jaccard=top-M keyness 詞集聯集基數'"""),
]

METHOD_SEEDS = [
    ("cnt_term_work", "counting",
     "tf(t,l,w)=COUNT(*) postings FROM knowledge_concordance c JOIN knowledge_sentence s ON s.sent_id=c.sent_id "
     "JOIN philosophy_work_text wt ON wt.text_id=s.text_id JOIN philosophy_work w ON w.work_id=wt.work_id "
     "WHERE review_flag=false AND corpus_class='literary' GROUP BY term,language,work_id;"
     "df_works(t,l)=COUNT(*) OVER (PARTITION BY term,language)(=corpus_stats.df_works 同掃描反正規化副本)"),
    ("cnt_term_corpus", "counting",
     "同 cnt_term_work 之 CLEAN 掃描聚合到 (term,language):tf_total=SUM(tf);df_works=COUNT(DISTINCT work_id);"
     "df_sents=COUNT(DISTINCT sent_id)(NPMI/Jaccard/LLR 句級邊際分母之 SSOT)"),
    ("gate_stat_vocab", "closed_form_stat",
     "入閘=tf_rank(語言內,ORDER BY tf_total DESC)>R AND df_works>=F,取前 K;R/F/K=操作值(#27),"
     "每次 build 印於 log,不鑄入 schema。en 未去 stopword(the 3.2M/of 2.1M postings 實測在庫)故必須顯式閘"),
    ("rule_proponents_parse", "string_rule",
     "philosophy_school.proponents 以 [;,、/]+' and ' 切分→trim→與 philosophy_thinker.name/name_zh 精確或 "
     "lower(trim()) 正規化等值匹配;人工不得手建列,僅得改 review_status(confirm/reject)"),
    ("join_prior_school_thinker", "sql_join",
     "既存 school_thinker 表(19 列,無 provenance/review 欄,框架 build 非冪等所產)之列重述為 seed(review_status='seed');"
     "matched_text=school.name||' <- '||thinker.name;不直接採信=fail-closed"),
    ("rule_confirmed_school_edge", "string_rule",
     "knowledge_edge(thinker_of_school) = seed 表 WHERE review_status='confirmed' 之投影;"
     "非 confirmed 之既存邊同步刪除(fail-closed 投影,人拍板才進圖)"),
    ("join_work_of_thinker", "sql_join",
     "knowledge_edge(work_of_thinker) = philosophy_work(work_id,thinker_id) 重述,零新事實"),
    ("agg_group_rollup", "sql_join",
     "tf(t,l,g)=SUM(term_stats.tf) over 群組 works;thinker 群=work.thinker_id;school 群=confirmed "
     "thinker_of_school edge∘work_of_thinker 鏈;term 域=knowledge_stat_vocab(有界)"),
    ("cnt_cooc_sentence", "counting",
     "cooc_sents(a,b,l)=COUNT(DISTINCT sent_id) 同句含 a,b;cooc_works 同理;域=兩端∈stat_vocab 且 a<b;"
     "zh 排除 a 為 b 子字串(或反之)之 pair(textnorm 雙軌 詞↔構成字 P=1 之確定性 artifact);"
     "留存門檻 cooc_sents>=min_cooc(操作值印 log);句集=CLEAN works 句"),
    ("stat_npmi", "closed_form_stat",
     "pmi=ln(c_ab*N/(c_a*c_b));npmi=pmi/(-ln(c_ab/N));c_x=corpus_stats.df_sents,c_ab=cooc_sents,"
     "N=CLEAN 句數(語言內,basis_n 落欄)"),
    ("stat_jaccard", "closed_form_stat", "J=c_ab/(c_a+c_b-c_ab),句級,分母來源同 stat_npmi"),
    ("stat_llr_dunning", "closed_form_stat",
     "Dunning 1993 G2 over 2x2 句計數表(k11=c_ab,k12=c_a-c_ab,k21=c_b-c_ab,k22=N-c_a-c_b+c_ab);"
     "符號=sign(c_ab*N-c_a*c_b)"),
    ("stat_keyness_llr", "closed_form_stat",
     "G2 over 2x2 token 表(群內 tf vs 同語言其餘語料 tf;域=vocab terms;符號=群內相對頻率高為正);"
     "basis_n=語言內 vocab token 總量"),
    ("stat_log_odds_dirichlet", "closed_form_stat",
     "Monroe et al. 2008 informative Dirichlet prior log-odds z-score;prior α_t=a0*tf_total(t)/T,"
     "a0=操作值印 log;群 vs 同語言其餘語料"),
    ("stat_tf_share", "closed_form_stat", "tf(t,g)/tf_total(t)(群佔比,0..1)"),
    ("stat_tfidf_cosine", "closed_form_stat",
     "cosine over 群組詞頻向量;權重=tf*ln(G/df_groups),G=同 kind 同語言有語料之群數,df_groups=含該 term 之群數;"
     "全由 counts 導出,零 embedding"),
    ("stat_keyness_topk_jaccard", "closed_form_stat",
     "J=|A∩B|/|A∪B|,A/B=兩群 keyness_llr>0 之 top-M term 集(M=操作值印 log);basis_n=|A∪B|"),
]

CHARTER_ROWS = [
    ("affinity_stats",
     "語料內 term/群組(學說·思想家)之計數與閉式統計:tf/df/共現、NPMI/Jaccard/LLR、keyness、"
     "log-odds、tfidf-cosine;每個數字附 method_key(公式)與 basis_n(分母),可回鏈 concordance 逐字位置",
     "語意等同、因果、思想影響方向、未收錄著作之主張;向量相似度與 LLM 判斷不構成任何知識宣稱;"
     "school 層統計以 confirmed 歸屬鏈為界,鏈外不宣稱",
     "(?i)(truth|omniscien)|全知|真理"),
]

META_UPSERT = ("INSERT INTO knowledge_build_meta (scope, cursor_sent_id, updated_at) VALUES (%s,%s,now()) "
               "ON CONFLICT (scope) DO UPDATE SET cursor_sent_id=EXCLUDED.cursor_sent_id, updated_at=now()")


def _cursor(conn, scope):
    with db.transaction(conn) as cur:
        cur.execute("SELECT cursor_sent_id FROM knowledge_build_meta WHERE scope=%s", (scope,))
        r = cur.fetchone()
    return int(r[0]) if r else 0


def _exists(cur, name):
    cur.execute("SELECT to_regclass(%s)", (name,))
    return cur.fetchone()[0] is not None


def _count(cur, name):
    if not _exists(cur, name):
        return None
    cur.execute(f"SELECT count(*) FROM {name}")  # noqa: S608 表名來自本檔白名單
    return cur.fetchone()[0]


def _g2(a, b, c, d):
    """Dunning G2 SQL 運算式(a,b,c,d=2x2 cell 之 SQL 子式;0 cell 貢獻 0)。"""
    n = f"(({a})+({b})+({c})+({d}))"
    r1, r2, c1, c2 = f"(({a})+({b}))", f"(({c})+({d}))", f"(({a})+({c}))", f"(({b})+({d}))"

    def cell(k, r, co):
        return f"(CASE WHEN ({k})>0 THEN ({k})*ln(({k})*{n}/(({r})*({co}))) ELSE 0 END)"
    return f"2*({cell(a, r1, c1)}+{cell(b, r1, c2)}+{cell(c, r2, c1)}+{cell(d, r2, c2)})"


# ---------------------------------------------------------------------------
# phases
# ---------------------------------------------------------------------------

def phase_ddl(conn):
    t0 = time.time()
    with db.transaction(conn) as cur:
        for label, sql in DDL:
            cur.execute(sql)
            print(f"  DDL:{label}")
        for key, kind, definition in METHOD_SEEDS:
            cur.execute("INSERT INTO knowledge_derivation_method (method_key, method_kind, definition) "
                        "VALUES (%s,%s,%s) ON CONFLICT (method_key) DO UPDATE SET "
                        "method_kind=EXCLUDED.method_kind, definition=EXCLUDED.definition", (key, kind, definition))
        print(f"  method 種子:{len(METHOD_SEEDS)} 列(四值 kind 白名單=紅線① DB 硬擋)")
    print(f"[ddl] 完成 {time.time() - t0:.1f}s")


def phase_stats(conn, smoke=False, limit=None):
    """L1:逐 concordance 分區聚合(分區鍵=HASH(term) → 每 term 完整落單一分區,分區=完備 resume 單位)。"""
    scope = "xs_term_stats"
    done = _cursor(conn, scope)
    todo = list(range(done, 1 if smoke else N_PARTITIONS))
    if limit:
        todo = todo[:limit]
    if not todo:
        print(f"[stats] 游標={done}/{N_PARTITIONS},無待處理分區")
        return
    print(f"[stats] 自分區 p{todo[0]} 起({len(todo)} 個;CLEAN={CLEAN})")
    for i in todo:
        t0 = time.time()
        with db.transaction(conn) as cur:   # 聚合+雙表寫入+游標=同一 tx(崩潰一致)
            cur.execute(f"""
                CREATE TEMP TABLE _g ON COMMIT DROP AS
                SELECT c.term, c.language, wt.work_id,
                       count(*) AS tf, count(DISTINCT c.sent_id) AS sent_df
                FROM knowledge_concordance_p{i} c
                JOIN knowledge_sentence s   ON s.sent_id = c.sent_id
                JOIN philosophy_work_text wt ON wt.text_id = s.text_id
                JOIN philosophy_work w      ON w.work_id = wt.work_id
                WHERE {CLEAN}
                GROUP BY 1,2,3""")
            cur.execute("""
                INSERT INTO knowledge_term_corpus_stats (term, language, tf_total, df_works, df_sents, method_key)
                SELECT term, language, sum(tf), count(*), sum(sent_df), 'cnt_term_corpus' FROM _g GROUP BY 1,2
                ON CONFLICT (term, language, corpus) DO UPDATE SET
                  tf_total=EXCLUDED.tf_total, df_works=EXCLUDED.df_works, df_sents=EXCLUDED.df_sents""")
            n_corpus = cur.rowcount
            cur.execute("""
                INSERT INTO knowledge_term_stats (term, language, work_id, tf, df_works, method_key)
                SELECT term, language, work_id, tf,
                       count(*) OVER (PARTITION BY term, language), 'cnt_term_work'
                FROM _g
                ON CONFLICT (term, language, work_id) DO UPDATE SET tf=EXCLUDED.tf, df_works=EXCLUDED.df_works""")
            n_ts = cur.rowcount
            cur.execute(META_UPSERT, (scope, i + 1))
        el = time.time() - t0
        print(f"  p{i}:corpus_stats {n_corpus} 列、term_stats {n_ts} 列、{el:.1f}s"
              f"({(n_ts / el) if el > 0 else 0:.0f} 列/s)", flush=True)
    with db.transaction(conn) as cur:
        cur.execute("ANALYZE knowledge_term_stats"); cur.execute("ANALYZE knowledge_term_corpus_stats")


def phase_vocab(conn, args):
    """L2:詞彙閘(deterministic DELETE+INSERT;重跑=下游共現/親和口徑改變 → 同步重置,誠實印出)。"""
    for lang in ("en", "zh"):
        r, f, k = args.gate_topband[lang], args.gate_dfmin, args.gate_cap[lang]
        t0 = time.time()
        with db.transaction(conn) as cur:
            cur.execute("DELETE FROM knowledge_stat_vocab WHERE language=%s", (lang,))
            cur.execute("""
                INSERT INTO knowledge_stat_vocab (term, language, gate_reason, method_key)
                SELECT term, language, 'freq_gate', 'gate_stat_vocab'
                FROM (SELECT term, language, row_number() OVER (ORDER BY tf_total DESC, term) AS rnk
                      FROM knowledge_term_corpus_stats WHERE language=%s AND df_works >= %s) t
                WHERE rnk > %s ORDER BY rnk LIMIT %s""", (lang, f, r, k))
            n = cur.rowcount
            # 閘口徑改變 → 下游確定性重算域失效:重置游標+清空快取與 pair 層(誠實,不留舊口徑幽靈列)
            cur.execute(META_UPSERT, ("xs_sterms", 0))
            cur.execute(META_UPSERT, (f"xs_cooc_{lang}", 0))
            cur.execute("TRUNCATE knowledge_sent_terms_stage")
            cur.execute("DELETE FROM knowledge_term_cooccurrence WHERE language=%s AND corpus='philosophy'", (lang,))
            cur.execute("DELETE FROM knowledge_term_affinity WHERE language=%s AND corpus='philosophy'", (lang,))
        print(f"[vocab] {lang}:入閘 {n} 列(排除頻帶 rank<={r}、df_works>={f}、cap={k}=操作值)"
              f"、{time.time() - t0:.1f}s;⚠ 已重置下游 staging/cooc/affinity({lang})")


def _norm_name(s):
    return " ".join(s.lower().split())


def phase_seed(conn):
    """L3:歸屬鏈種子(string_rule+既存表匯入;誠實印匹配率與全文覆蓋=揭露 school 層現況空集)。"""
    t0 = time.time()
    with db.transaction(conn) as cur:
        cur.execute("SELECT thinker_id, name, coalesce(name_zh,'') FROM philosophy_thinker")
        by_exact, by_norm, by_zh = {}, {}, {}
        for tid, name, zh in cur.fetchall():
            by_exact[name] = tid
            by_norm.setdefault(_norm_name(name), tid)
            if zh:
                by_zh[zh] = tid
        cur.execute("SELECT school_id, coalesce(proponents,'') FROM philosophy_school")
        schools = cur.fetchall()
    tokens, matched, rows = 0, 0, []
    for sid, prop in schools:
        for chunk in prop.replace(" and ", ";").replace("、", ";").replace("/", ";").replace(",", ";").split(";"):
            tok = chunk.strip().strip(".")
            if not tok:
                continue
            tokens += 1
            hit = None
            if tok in by_exact:
                hit = (by_exact[tok], "exact_name")
            elif tok in by_zh:
                hit = (by_zh[tok], "name_zh")
            elif _norm_name(tok) in by_norm:
                hit = (by_norm[_norm_name(tok)], "normalized_name")
            if hit:
                matched += 1
                rows.append((sid, hit[0], tok, hit[1], "rule_proponents_parse"))
    with db.transaction(conn) as cur:
        ins = 0
        for r in rows:   # ON CONFLICT DO NOTHING:絕不覆寫既有 review_status(人拍板不可被重跑洗掉)
            cur.execute("""INSERT INTO knowledge_school_thinker_seed
                           (school_id, thinker_id, matched_text, match_rule, method_key)
                           VALUES (%s,%s,%s,%s,%s) ON CONFLICT (school_id, thinker_id) DO NOTHING""", r)
            ins += cur.rowcount
        cur.execute("""INSERT INTO knowledge_school_thinker_seed
                       (school_id, thinker_id, matched_text, match_rule, method_key)
                       SELECT st.school_id, st.thinker_id, s.name || ' <- ' || t.name, 'prior_table',
                              'join_prior_school_thinker'
                       FROM school_thinker st
                       JOIN philosophy_school s USING (school_id) JOIN philosophy_thinker t USING (thinker_id)
                       ON CONFLICT (school_id, thinker_id) DO NOTHING""")
        prior = cur.rowcount
        cur.execute(f"""SELECT
                          (SELECT count(DISTINCT school_id) FROM knowledge_school_thinker_seed),
                          (SELECT count(DISTINCT sd.school_id) FROM knowledge_school_thinker_seed sd
                             JOIN philosophy_work w ON w.thinker_id = sd.thinker_id AND {CLEAN}
                             JOIN philosophy_work_text t ON t.work_id = w.work_id),
                          coalesce((SELECT sum(length(t.content))
                             FROM (SELECT DISTINCT thinker_id FROM knowledge_school_thinker_seed) th
                             JOIN philosophy_work w ON w.thinker_id = th.thinker_id AND {CLEAN}
                             JOIN philosophy_work_text t ON t.work_id = w.work_id), 0)""")
        n_sch, n_sch_txt, chars = cur.fetchone()
        cur.execute("SELECT sum(length(content)) FROM philosophy_work_text")
        total_chars = cur.fetchone()[0]
    print(f"[seed] proponents token {tokens}、匹配 {matched}(新插 {ins})+既存 school_thinker 匯入 {prior} 列;"
          f"{time.time() - t0:.1f}s")
    print(f"[seed] ⚠ 誠實現況:seed 覆蓋 {n_sch} 校、其中有 CLEAN 全文者 {n_sch_txt} 校、"
          f"全文 {chars:,}/{total_chars:,} 字元({(chars / total_chars * 100) if total_chars else 0:.3f}%)。"
          f"en 語料=古典文本、44 校 proponents=現代作者 → school 層統計現況近空;"
          f"補救(補現代文本/古典思想家 re-seed/其他分群)=決策層拍板,本 builder 不越權。")


def phase_edge(conn):
    """L3 投影:work_of_thinker 全量 + confirmed thinker_of_school(fail-closed 同步:非 confirmed 邊刪除)。"""
    t0 = time.time()
    with db.transaction(conn) as cur:
        cur.execute("""INSERT INTO knowledge_edge (predicate, src_id, dst_id, provenance, method_key, evidence_n)
                       SELECT 'work_of_thinker', w.work_id, w.thinker_id, 'join', 'join_work_of_thinker', 1
                       FROM philosophy_work w
                       ON CONFLICT (predicate, src_id, dst_id) DO NOTHING""")
        n_wt = cur.rowcount
        cur.execute("""INSERT INTO knowledge_edge (predicate, src_id, dst_id, provenance, method_key, evidence_n)
                       SELECT 'thinker_of_school', sd.thinker_id, sd.school_id, 'string_rule',
                              'rule_confirmed_school_edge', 1
                       FROM knowledge_school_thinker_seed sd WHERE sd.review_status='confirmed'
                       ON CONFLICT (predicate, src_id, dst_id) DO NOTHING""")
        n_ts = cur.rowcount
        cur.execute("""DELETE FROM knowledge_edge e WHERE e.predicate='thinker_of_school' AND NOT EXISTS (
                         SELECT 1 FROM knowledge_school_thinker_seed sd
                         WHERE sd.thinker_id=e.src_id AND sd.school_id=e.dst_id AND sd.review_status='confirmed')""")
        n_del = cur.rowcount
        cur.execute("SELECT count(*) FROM knowledge_edge WHERE predicate='thinker_of_school'")
        n_conf = cur.fetchone()[0]
    print(f"[edge] work_of_thinker 新插 {n_wt};thinker_of_school 新插 {n_ts}、fail-closed 撤 {n_del}、"
          f"現存 {n_conf}(=confirmed seed 數;0=尚無人工確認,school 下游=空,誠實);{time.time() - t0:.1f}s")


def phase_groupstats(conn):
    """L4:群組聚合(deterministic DELETE+INSERT per kind;term 域=vocab=有界)。"""
    for kind, join_sql in (
        ("thinker", "JOIN philosophy_work w ON w.work_id = ts.work_id"),
        ("school", """JOIN philosophy_work w ON w.work_id = ts.work_id
                      JOIN knowledge_edge e ON e.predicate='thinker_of_school' AND e.src_id = w.thinker_id"""),
    ):
        gid = "w.thinker_id" if kind == "thinker" else "e.dst_id"
        t0 = time.time()
        with db.transaction(conn) as cur:
            cur.execute("DELETE FROM knowledge_term_group_stats WHERE group_kind=%s", (kind,))
            cur.execute(f"""
                INSERT INTO knowledge_term_group_stats (group_kind, group_id, term, language, tf, df_works, method_key)
                SELECT %s, {gid}, ts.term, ts.language, sum(ts.tf), count(DISTINCT ts.work_id), 'agg_group_rollup'
                FROM knowledge_term_stats ts
                JOIN knowledge_stat_vocab v ON v.term = ts.term AND v.language = ts.language
                {join_sql}
                GROUP BY 2,3,4""", (kind,))
            n = cur.rowcount
        el = time.time() - t0
        print(f"[groupstats] {kind}:{n} 列、{el:.1f}s({(n / el) if el > 0 else 0:.0f} 列/s)"
              + ("  ⚠ school=0 列=歸屬鏈未 confirmed,誠實非 bug" if kind == "school" and n == 0 else ""))


def phase_cooc(conn, args):
    """L5:共現。step1 staging(逐 concordance 分區,游標);step2 anchor-block 自交(游標)。
    不逐分區自交——分區鍵=HASH(term),同句 terms 散在 16 分區,逐分區自交=系統性漏計(對抗驗證修正)。"""
    scope_s = "xs_sterms"
    done = _cursor(conn, scope_s)
    with db.transaction(conn) as cur:
        cur.execute("SELECT count(*) FROM knowledge_sent_terms_stage")
        n_stage = cur.fetchone()[0]
    if done > 0 and n_stage == 0 and not args.rebuild_staging:
        print("[cooc] ⚠ staging 空但游標>0(UNLOGGED 崩潰截斷)→ 加 --rebuild-staging 重建")
        return
    if args.rebuild_staging:
        with db.transaction(conn) as cur:
            cur.execute("TRUNCATE knowledge_sent_terms_stage")
            cur.execute(META_UPSERT, (scope_s, 0))
        done = 0
        print("[cooc] staging 已重置")
    todo = list(range(done, 1 if args.smoke else N_PARTITIONS))
    if args.limit:
        todo = todo[:args.limit]
    for i in todo:
        t0 = time.time()
        with db.transaction(conn) as cur:
            cur.execute(f"""
                INSERT INTO knowledge_sent_terms_stage (language, term, sent_id, work_id)
                SELECT DISTINCT c.language, c.term, c.sent_id, wt.work_id
                FROM knowledge_concordance_p{i} c
                JOIN knowledge_stat_vocab v ON v.term = c.term AND v.language = c.language
                JOIN knowledge_sentence s   ON s.sent_id = c.sent_id
                JOIN philosophy_work_text wt ON wt.text_id = s.text_id
                JOIN philosophy_work w      ON w.work_id = wt.work_id
                WHERE {CLEAN}
                ON CONFLICT DO NOTHING""")
            n = cur.rowcount
            cur.execute(META_UPSERT, (scope_s, i + 1))
        print(f"  staging p{i}:{n} 列、{time.time() - t0:.1f}s", flush=True)
    staged = _cursor(conn, scope_s) >= (1 if args.smoke else N_PARTITIONS)
    if not staged:
        print("[cooc] staging 未達本次目標分區數(--limit 截斷)→ 先續跑 staging,再進 block 自交")
        return
    with db.transaction(conn) as cur:
        cur.execute("CREATE INDEX IF NOT EXISTS idx_sts_sent ON knowledge_sent_terms_stage (language, sent_id, term)")
        cur.execute("ANALYZE knowledge_sent_terms_stage")
    for lang in ("zh", "en") if args.smoke else ("en", "zh"):
        scope_b = f"xs_cooc_{lang}"
        with db.transaction(conn) as cur:
            cur.execute("SELECT term FROM knowledge_stat_vocab WHERE language=%s ORDER BY term", (lang,))
            terms = [r[0] for r in cur.fetchall()]
        blocks = [terms[j:j + BLOCK_SIZE] for j in range(0, len(terms), BLOCK_SIZE)]
        bdone = _cursor(conn, scope_b)
        btodo = list(range(bdone, len(blocks)))
        if args.smoke:
            btodo = btodo[:2]
        if args.limit:
            btodo = btodo[:args.limit]
        if not btodo:
            print(f"[cooc] {lang}:block 游標={bdone}/{len(blocks)},無待處理")
            continue
        zh_excl = ("AND NOT (strpos(b.term, a.term) > 0 OR strpos(a.term, b.term) > 0)"
                   if lang.startswith("zh") else "")
        print(f"[cooc] {lang}:{len(blocks)} blocks(×{BLOCK_SIZE} anchors),自 block {btodo[0]} 起,"
              f"min_cooc={args.min_cooc}(操作值)")
        for bi in btodo:
            t0 = time.time()
            with db.transaction(conn) as cur:   # 計數 upsert=DO UPDATE(語料增長重跑=刷新,不凍結首建值)
                cur.execute(f"""
                    INSERT INTO knowledge_term_cooccurrence
                          (term_a, term_b, language, cooc_sents, cooc_works, method_key)
                    SELECT a.term, b.term, a.language,
                           count(DISTINCT a.sent_id), count(DISTINCT a.work_id), 'cnt_cooc_sentence'
                    FROM knowledge_sent_terms_stage a
                    JOIN knowledge_sent_terms_stage b
                      ON b.language = a.language AND b.sent_id = a.sent_id AND b.term > a.term
                    WHERE a.language = %s AND a.term = ANY(%s) {zh_excl}
                    GROUP BY 1,2,3
                    HAVING count(DISTINCT a.sent_id) >= %s
                    ON CONFLICT (language, term_a, term_b) DO UPDATE SET
                      cooc_sents=EXCLUDED.cooc_sents, cooc_works=EXCLUDED.cooc_works""",
                            (lang, blocks[bi], args.min_cooc))
                n = cur.rowcount
                cur.execute(META_UPSERT, (scope_b, bi + 1))
            el = time.time() - t0
            print(f"  {lang} block {bi + 1}/{len(blocks)}:pair {n} 列、{el:.1f}s"
                  f"({(n / el) if el > 0 else 0:.0f} 列/s)", flush=True)


def _clean_sents(conn, lang):
    with db.transaction(conn) as cur:
        cur.execute(f"""SELECT count(*) FROM knowledge_sentence s
                        JOIN philosophy_work_text wt ON wt.text_id = s.text_id
                        JOIN philosophy_work w ON w.work_id = wt.work_id
                        WHERE {CLEAN} AND s.language = %s""", (lang,))
        return cur.fetchone()[0]


def phase_affinity(conn, args):
    """L6a:term 親和(長格式=一列一公式一 method_key;deterministic DELETE+INSERT;雙向 anchor top-K)。"""
    langs = ("zh",) if args.smoke else (("en", "zh") if not args.language else (args.language,))
    for lang in langs:
        n_sents = _clean_sents(conn, lang)
        if n_sents == 0:
            print(f"[affinity] {lang}:CLEAN 句數=0,跳過")
            continue
        t0 = time.time()
        llr = _g2("cab", "ca-cab", "cb-cab", "nn-ca-cb+cab")
        with db.transaction(conn) as cur:
            cur.execute("DELETE FROM knowledge_term_affinity WHERE language=%s", (lang,))
            cur.execute(f"""
                INSERT INTO knowledge_term_affinity
                      (term_a, term_b, language, stat_key, stat_value, basis_n, rank_in_a, method_key)
                WITH d AS (
                  SELECT term_a AS a, term_b AS b, cooc_sents FROM knowledge_term_cooccurrence WHERE language=%s AND corpus='philosophy'
                  UNION ALL
                  SELECT term_b, term_a, cooc_sents FROM knowledge_term_cooccurrence WHERE language=%s AND corpus='philosophy'
                ), j AS (
                  SELECT d.a, d.b, d.cooc_sents::double precision AS cab,
                         ca.df_sents::double precision AS ca, cb.df_sents::double precision AS cb,
                         %s::double precision AS nn
                  FROM d
                  JOIN knowledge_term_corpus_stats ca ON ca.term = d.a AND ca.language = %s AND ca.corpus='philosophy'
                  JOIN knowledge_term_corpus_stats cb ON cb.term = d.b AND cb.language = %s AND cb.corpus='philosophy'
                ), s AS (
                  SELECT a, b, v.stat_key, v.stat_value FROM j CROSS JOIN LATERAL (VALUES
                    ('npmi', CASE WHEN cab < nn THEN ln(cab*nn/(ca*cb)) / (-ln(cab/nn)) END),
                    ('jaccard', cab/(ca+cb-cab)),
                    ('llr', sign(cab*nn - ca*cb) * ({llr}))
                  ) v(stat_key, stat_value)
                  WHERE v.stat_value IS NOT NULL
                ), r AS (
                  SELECT *, row_number() OVER (PARTITION BY a, stat_key ORDER BY stat_value DESC, b) AS rk FROM s
                )
                SELECT a, b, %s, stat_key, stat_value, %s::bigint, rk,
                       CASE stat_key WHEN 'npmi' THEN 'stat_npmi'
                                     WHEN 'jaccard' THEN 'stat_jaccard' ELSE 'stat_llr_dunning' END
                FROM r WHERE rk <= %s""",
                        (lang, lang, n_sents, lang, lang, lang, n_sents, args.topk_term))
            n = cur.rowcount
        el = time.time() - t0
        print(f"[affinity] {lang}:{n} 列(top-K={args.topk_term}/anchor/stat=操作值;N={n_sents} CLEAN 句)、"
              f"{el:.1f}s({(n / el) if el > 0 else 0:.0f} 列/s)")


def phase_groupaff(conn, args):
    """L6b:群組 keyness + 群組×群組親和(school 全量≤C(44,2);thinker=anchor top-K 有界)。"""
    langs = ("zh",) if args.smoke else (("en", "zh") if not args.language else (args.language,))
    for kind in ("thinker", "school"):
        for lang in langs:
            t0 = time.time()
            a0 = args.logodds_a0
            g2 = _g2("y1", "n1-y1", "yt-y1", "(t-n1)-(yt-y1)")
            with db.transaction(conn) as cur:
                cur.execute("DELETE FROM knowledge_term_group_affinity WHERE group_kind=%s AND language=%s",
                            (kind, lang))
                cur.execute(f"""
                    INSERT INTO knowledge_term_group_affinity
                          (group_kind, group_id, term, language, stat_key, stat_value, basis_n,
                           rank_in_group, method_key)
                    WITH corp AS (
                      SELECT cs.term, cs.tf_total::double precision AS yt
                      FROM knowledge_term_corpus_stats cs
                      JOIN knowledge_stat_vocab v ON v.term = cs.term AND v.language = cs.language
                      WHERE cs.language = %s
                    ), tt AS (SELECT sum(yt) AS t FROM corp),
                    g AS (SELECT group_id, term, tf::double precision AS y1
                          FROM knowledge_term_group_stats WHERE group_kind = %s AND language = %s),
                    ng AS (SELECT group_id, sum(y1) AS n1 FROM g GROUP BY 1),
                    j AS (SELECT g.group_id, g.term, g.y1, ng.n1, corp.yt, tt.t
                          FROM g JOIN ng USING (group_id) JOIN corp USING (term) CROSS JOIN tt
                          WHERE tt.t > 0 AND ng.n1 < tt.t),
                    s AS (
                      SELECT group_id, term, v.stat_key, v.stat_value, t FROM j CROSS JOIN LATERAL (VALUES
                        ('keyness_llr', sign(y1*(t-n1) - (yt-y1)*n1) * ({g2})),
                        ('log_odds_dirichlet',
                          (ln((y1 + {a0}*yt/t) / (n1 + {a0} - y1 - {a0}*yt/t))
                           - ln(((yt-y1) + {a0}*yt/t) / ((t-n1) + {a0} - (yt-y1) - {a0}*yt/t)))
                          / sqrt(1.0/(y1 + {a0}*yt/t) + 1.0/((yt-y1) + {a0}*yt/t))),
                        ('tf_share', y1/yt)
                      ) v(stat_key, stat_value)
                      WHERE v.stat_value IS NOT NULL
                    ),
                    r AS (SELECT *, row_number() OVER (PARTITION BY group_id, stat_key
                                                       ORDER BY stat_value DESC, term) AS rk FROM s)
                    SELECT %s, group_id, term, %s, stat_key, stat_value, t::bigint, rk,
                           CASE stat_key WHEN 'keyness_llr' THEN 'stat_keyness_llr'
                                         WHEN 'log_odds_dirichlet' THEN 'stat_log_odds_dirichlet'
                                         ELSE 'stat_tf_share' END
                    FROM r WHERE rk <= %s""",
                            (lang, kind, lang, kind, lang, args.topm_group))
                n_key = cur.rowcount
                cur.execute("DELETE FROM knowledge_group_affinity WHERE group_kind=%s AND language=%s",
                            (kind, lang))
                keep = 10 ** 9 if kind == "school" else args.topk_grouppair   # school 上界 C(44,2)=946 → 全量
                cur.execute("""
                    INSERT INTO knowledge_group_affinity
                          (group_kind, group_a, group_b, language, stat_key, stat_value, basis_n, method_key)
                    WITH base AS (SELECT group_id, term, tf FROM knowledge_term_group_stats
                                  WHERE group_kind = %s AND language = %s),
                    df AS (SELECT term, count(*)::double precision AS dfg FROM base GROUP BY 1),
                    gc AS (SELECT count(DISTINCT group_id)::double precision AS g FROM base),
                    gv AS (SELECT b.group_id, b.term, b.tf * ln(gc.g/df.dfg) AS wgt
                           FROM base b JOIN df USING (term) CROSS JOIN gc WHERE df.dfg < gc.g),
                    nrm AS (SELECT group_id, sqrt(sum(wgt*wgt)) AS n FROM gv GROUP BY 1),
                    dot AS (SELECT a.group_id AS ga, b.group_id AS gb, sum(a.wgt*b.wgt) AS d,
                                   count(*) AS shared
                            FROM gv a JOIN gv b ON b.term = a.term AND b.group_id > a.group_id GROUP BY 1,2),
                    cosims AS (SELECT ga, gb, d/(na.n*nb.n) AS val, shared FROM dot
                               JOIN nrm na ON na.group_id = ga JOIN nrm nb ON nb.group_id = gb
                               WHERE na.n > 0 AND nb.n > 0),
                    topk AS (SELECT ga, gb, val, shared,
                                    row_number() OVER (PARTITION BY ga ORDER BY val DESC) AS ra,
                                    row_number() OVER (PARTITION BY gb ORDER BY val DESC) AS rb
                             FROM cosims)
                    SELECT %s, ga, gb, %s, 'tfidf_cosine_counts', val, shared, 'stat_tfidf_cosine'
                    FROM topk WHERE ra <= %s OR rb <= %s""",
                            (kind, lang, kind, lang, keep, keep))
                n_cos = cur.rowcount
                cur.execute("""
                    INSERT INTO knowledge_group_affinity
                          (group_kind, group_a, group_b, language, stat_key, stat_value, basis_n, method_key)
                    WITH s AS (SELECT group_id, term FROM knowledge_term_group_affinity
                               WHERE group_kind = %s AND language = %s AND stat_key = 'keyness_llr'
                                 AND stat_value > 0 AND rank_in_group <= %s),
                    sz AS (SELECT group_id, count(*) AS n FROM s GROUP BY 1),
                    p AS (SELECT a.group_id AS ga, b.group_id AS gb, count(*) AS inter
                          FROM s a JOIN s b ON b.term = a.term AND b.group_id > a.group_id GROUP BY 1,2),
                    vals AS (SELECT p.ga, p.gb, p.inter::double precision/(sa.n+sb.n-p.inter) AS val,
                                    (sa.n+sb.n-p.inter)::bigint AS uni
                             FROM p JOIN sz sa ON sa.group_id = p.ga JOIN sz sb ON sb.group_id = p.gb),
                    topk AS (SELECT ga, gb, val, uni,
                                    row_number() OVER (PARTITION BY ga ORDER BY val DESC) AS ra,
                                    row_number() OVER (PARTITION BY gb ORDER BY val DESC) AS rb
                             FROM vals)
                    SELECT %s, ga, gb, %s, 'keyness_topk_jaccard', val, uni, 'stat_keyness_topk_jaccard'
                    FROM topk WHERE ra <= %s OR rb <= %s""",
                            (kind, lang, args.topm_group, kind, lang, keep, keep))
                n_jac = cur.rowcount
            el = time.time() - t0
            print(f"[groupaff] {kind}/{lang}:keyness {n_key} 列、cosine {n_cos}、jaccard {n_jac}、{el:.1f}s"
                  + ("  ⚠ school=0=歸屬鏈未 confirmed,誠實" if kind == "school" and n_key == 0 else ""))


def phase_metrics(conn):
    """coverage_metric append(分子/分母全 COUNT 實查;同日重跑=re-measure 更新,不改往日列)。"""
    t0 = time.time()
    metrics = []
    with db.transaction(conn) as cur:
        for lang in ("en", "zh"):
            cur.execute(f"""SELECT count(*) FROM knowledge_sentence s
                            JOIN philosophy_work_text wt ON wt.text_id = s.text_id
                            JOIN philosophy_work w ON w.work_id = wt.work_id
                            WHERE {CLEAN} AND s.language = %s""", (lang,))
            clean = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM knowledge_sentence WHERE language = %s", (lang,))
            metrics.append((f"clean_sents_{lang}", clean, cur.fetchone()[0], "CLEAN 句/全句(affinity N 分母)"))
            cur.execute("SELECT count(*) FROM knowledge_stat_vocab WHERE language = %s", (lang,))
            cur2 = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM knowledge_term_corpus_stats WHERE language = %s", (lang,))
            metrics.append((f"stat_vocab_{lang}", cur2, cur.fetchone()[0], "入閘 term/全 distinct term"))
            cur.execute("SELECT count(*) FROM knowledge_term_cooccurrence WHERE language = %s", (lang,))
            metrics.append((f"cooc_pairs_{lang}", cur.fetchone()[0], None, "有界物化 pair(其餘=按需 SQL)"))
        for t in ("knowledge_term_stats", "knowledge_term_affinity", "knowledge_term_group_stats",
                  "knowledge_term_group_affinity", "knowledge_group_affinity"):
            metrics.append((t.replace("knowledge_", "rows_")[:32], _count(cur, t), None, "表列數"))
        cur.execute("SELECT count(*), count(*) FILTER (WHERE review_status='confirmed') "
                    "FROM knowledge_school_thinker_seed")
        tot, conf = cur.fetchone()
        metrics.append(("school_seed_confirmed", conf, tot, "confirmed/seed 全數(fail-closed 鏈)"))
        cur.execute(f"""SELECT count(DISTINCT e.dst_id) FROM knowledge_edge e
                        JOIN philosophy_work w ON w.thinker_id = e.src_id AND {CLEAN}
                        JOIN philosophy_work_text t ON t.work_id = w.work_id
                        WHERE e.predicate = 'thinker_of_school'""")
        metrics.append(("schools_with_clean_text", cur.fetchone()[0], 44,
                        "有 confirmed 鏈+CLEAN 全文之校/全 44 校(fatal 揭露之誠實錶)"))
        cur.execute("""SELECT count(*) FROM (
                         SELECT work_id FROM philosophy_work_text
                         GROUP BY work_id HAVING count(DISTINCT language) > 1) t""")
        metrics.append(("xlang_parallel_works", cur.fetchone()[0], None,
                        "同 work 雙語文本數(實測 0=跨語 alignment 基質缺,另拍板)"))
        for key, num, den, note in metrics:
            cur.execute("""INSERT INTO knowledge_coverage_metric (metric_date, metric_key, numerator, denominator, note)
                           VALUES (CURRENT_DATE, %s, %s, %s, %s)
                           ON CONFLICT (metric_date, metric_key) DO UPDATE SET
                             numerator=EXCLUDED.numerator, denominator=EXCLUDED.denominator, note=EXCLUDED.note""",
                        (key, num, den, note))
            print(f"  {key}: {num} / {den}  ({note})")
    print(f"[metrics] {len(metrics)} 列 append({time.time() - t0:.1f}s)")


def phase_charter(conn):
    """宣稱列(不含於 --phase all;先全文印出=用戶過目,--run 才入庫)。"""
    for layer, can, cannot, pat in CHARTER_ROWS:
        print(f"  layer={layer}\n  can_answer={can}\n  cannot_answer={cannot}\n  forbidden_pat={pat}")
    with db.transaction(conn) as cur:
        for row in CHARTER_ROWS:
            cur.execute("""INSERT INTO knowledge_capability_charter (layer, can_answer, cannot_answer, forbidden_pat)
                           VALUES (%s,%s,%s,%s) ON CONFLICT (layer) DO NOTHING""", row)
    print("[charter] 入庫(ON CONFLICT DO NOTHING;變更既有列=決策層,另議)")


# ---------------------------------------------------------------------------
# 唯讀資訊矩陣 / seed 治理
# ---------------------------------------------------------------------------

def info(conn):
    print("=" * 78)
    print("build_cross_school_stats — 唯讀資訊矩陣(未加 --run,零寫入)")
    print("=" * 78)
    tables = [d[0].split("(")[0].strip() for d in DDL if d[0][0] != "c" and "evidence" not in d[0]]
    with db.transaction(conn) as cur:
        for t in tables:
            print(f"  {t:38s} {'存在,' + format(_count(cur, t), ',') + ' 列' if _exists(cur, t) else '不存在(先 --phase ddl --run)'}")
        if _exists(cur, "knowledge_build_meta"):
            cur.execute("SELECT scope, cursor_sent_id, updated_at FROM knowledge_build_meta "
                        "WHERE scope LIKE 'xs_%' ORDER BY scope")
            rows = cur.fetchall()
            print("  游標:" + ("(無)" if not rows else ""))
            for s, c, u in rows:
                print(f"    {s:16s} cursor={c}  {u}")
        if _exists(cur, "knowledge_school_thinker_seed"):
            cur.execute("SELECT review_status, count(*) FROM knowledge_school_thinker_seed GROUP BY 1")
            print(f"  seed 現況:{dict(cur.fetchall())}(confirmed 才進 edge=fail-closed)")
    for lang in ("en", "zh"):
        print(f"  CLEAN 句({lang})={_clean_sents(conn, lang):,}(review_flag=false AND corpus_class='literary')")
    print("-" * 78)
    print("phase 順序:ddl → stats → vocab → seed → [人工 confirm] → edge → groupstats → cooc")
    print("           → affinity → groupaff → metrics;charter 另跑(用戶過目)")
    print("耗時計畫值=SQL 實算÷實測吞吐之快照,非承諾(#15);外部定錨:p0 聚合 <280s、插入 ~44k 列/s")
    print("=" * 78)


def list_seeds(conn):
    with db.transaction(conn) as cur:
        if not _exists(cur, "knowledge_school_thinker_seed"):
            return print("  seed 表不存在(先 --phase ddl --run,再 --phase seed --run)")
        cur.execute("""SELECT sd.school_id, s.name, sd.thinker_id, t.name, sd.match_rule, sd.review_status,
                              sd.matched_text
                       FROM knowledge_school_thinker_seed sd
                       JOIN philosophy_school s USING (school_id) JOIN philosophy_thinker t USING (thinker_id)
                       ORDER BY sd.school_id, sd.thinker_id""")
        for r in cur.fetchall():
            print(f"  {r[0]:>3}:{r[1]:<18} <- {r[2]:>5}:{r[3]:<28} [{r[4]}/{r[5]}] '{r[6]}'")


def set_seed_status(conn, spec, status):
    sid, tid = (int(x) for x in spec.split(":"))
    with db.transaction(conn) as cur:
        cur.execute("UPDATE knowledge_school_thinker_seed SET review_status=%s "
                    "WHERE school_id=%s AND thinker_id=%s", (status, sid, tid))
        if cur.rowcount == 0:
            print(f"  ⚠ seed ({sid},{tid}) 不存在——列一律由 string_rule/join 產生,人工僅得 confirm/reject")
        else:
            print(f"  seed ({sid},{tid}) -> {status}(記得重跑 --phase edge 同步投影)")


# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--phase", choices=["ddl", "stats", "vocab", "seed", "edge", "groupstats", "cooc",
                                        "affinity", "groupaff", "metrics", "charter", "all"])
    ap.add_argument("--run", action="store_true", help="實際寫入(預設=唯讀資訊矩陣)")
    ap.add_argument("--smoke", action="store_true", help="微測:p0 分區+2 blocks+zh 先行(寫入=真值子集)")
    ap.add_argument("--limit", type=int, help="本次最多推進 N 個分區/區塊(配額護欄,游標可續)")
    ap.add_argument("--language", choices=["en", "zh"], help="affinity/groupaff 限單語言")
    ap.add_argument("--list-seeds", action="store_true")
    ap.add_argument("--confirm-seed", metavar="SCHOOL:THINKER")
    ap.add_argument("--reject-seed", metavar="SCHOOL:THINKER")
    ap.add_argument("--rebuild-staging", action="store_true")
    ap.add_argument("--gate-dfmin", type=int, default=DEFAULTS["gate_dfmin"])
    ap.add_argument("--min-cooc", type=int, default=DEFAULTS["min_cooc"])
    ap.add_argument("--topk-term", type=int, default=DEFAULTS["topk_term"])
    ap.add_argument("--topm-group", type=int, default=DEFAULTS["topm_group"])
    ap.add_argument("--topk-grouppair", type=int, default=DEFAULTS["topk_grouppair"])
    ap.add_argument("--logodds-a0", type=float, default=DEFAULTS["logodds_a0"])
    args = ap.parse_args()
    args.gate_topband, args.gate_cap = DEFAULTS["gate_topband"], DEFAULTS["gate_cap"]

    with db.connect() as conn:
        if args.list_seeds:
            return list_seeds(conn)
        if args.confirm_seed or args.reject_seed:
            if not args.run:
                return print("人工 confirm/reject 亦須 --run(決策層動作顯式化)")
            if args.confirm_seed:
                set_seed_status(conn, args.confirm_seed, "confirmed")
            if args.reject_seed:
                set_seed_status(conn, args.reject_seed, "rejected")
            return
        if not (args.phase and args.run):
            return info(conn)
        t0 = time.time()
        order = ([args.phase] if args.phase != "all"
                 else ["ddl", "stats", "vocab", "seed", "edge", "groupstats", "cooc", "affinity",
                       "groupaff", "metrics"])
        fns = {"ddl": lambda: phase_ddl(conn),
               "stats": lambda: phase_stats(conn, args.smoke, args.limit),
               "vocab": lambda: phase_vocab(conn, args),
               "seed": lambda: phase_seed(conn),
               "edge": lambda: phase_edge(conn),
               "groupstats": lambda: phase_groupstats(conn),
               "cooc": lambda: phase_cooc(conn, args),
               "affinity": lambda: phase_affinity(conn, args),
               "groupaff": lambda: phase_groupaff(conn, args),
               "metrics": lambda: phase_metrics(conn),
               "charter": lambda: phase_charter(conn)}
        for p in order:
            print(f"\n===== phase {p} =====")
            fns[p]()
        print(f"\n全部完成:{time.time() - t0:.1f}s(吞吐已逐段誠實印出;計畫值=快照非承諾)")


if __name__ == "__main__":
    main()