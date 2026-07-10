"""P3 混合檢索 API — 語義 kNN + verbatim 逐字子字串回查、逐字可溯源引用。

🎯 哲學素養框架 L2 知識檢索層核心(學習計畫 P3):給查詢 → e5-small 嵌入 → pgvector cosine kNN
   → 回逐字 chunk + Citation(work/thinker/chapter/char_range/source_url),供顧問引經據典。
   只回 DB 既存逐字字串、溯源三元組強制、verbatim 子字串存在性回查閘防「潤飾原文」。
   L5 擴充(text 計畫 v1.6):lexicon_lookup(公版辭書/註疏定義)+ concordance_lookup(逐字用例);
   N7 擴充(e2e 計畫 §3-S7):雙側檢索——retrieve_items(items 側文獻句;CLEAN_ITEM 閘=corpus SSOT;
   讀路徑=textnorm 全形集→exact SQL 零向量優先→ANN 補位→一律 PG JOIN 取原文)+
   verify_verbatim 雙側分派(item 側=item_text substring(FROM char_start+1) 定位他證)。
   L2/L3 表未建或庫無此詞 → 誠實回空 [](誠實率 100% 機制,配 advisor.guard 固定誠實句)。
守 #1(只回逐字原文、不生成不改寫)· #28(本地嵌入、零 LLM API)·
   憲章 v1.17.0(檢索層對預測表零寫入、與預測管線物理隔離)· #18。
"""
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from itertools import zip_longest

from augur.core import db
from augur.knowledge import corpus, embedspec, textnorm


@dataclass
class Citation:
    """一筆逐字可溯源的哲學引用。"""
    chunk_id: int
    work_id: int
    work_title: str
    thinker: str
    chapter: str
    char_start: int
    char_end: int
    source_url: str
    text: str        # 逐字原文(== work_text.content[char_start:char_end])
    score: float     # cosine 相似度(0~1)


@dataclass
class AttachedCitation:
    """Mode B(對話「+」附加檔只問這次)之逐字引用 — 不入庫、僅本回合。
    verify_verbatim 對 source_text(附加檔全文)作子字串他證(text ⊂ source_text);guard 照常對 .text 逐字比對。"""
    text: str            # 逐字段落(== source_text 之子字串)
    source_text: str     # 附加檔全文(verify 基準;不渲染)
    work_title: str      # 檔名(顯示用)
    thinker: str = ""
    chapter: str = ""
    char_start: int = 0
    char_end: int = 0
    source_url: str = ""
    score: float = 0.0


@lru_cache(maxsize=1)
def _model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(embedspec.MODEL_TAG, device=embedspec.QUERY_DEVICE)


def _query_vec(query):
    emb = _model().encode(["query: " + query], normalize_embeddings=True)[0]
    return "[" + ",".join(f"{x:.6f}" for x in emb) + "]"


def retrieve(query, k=8, work_id=None, scope=None):
    """語義檢索(works 側)＋ RBAC(A/B 裁決＝B、憲章 v1.29.0/用戶拍板):**works＝哲學/文學公版素養,對【所有
    登入者】公開、不 domain 收窄**(review_flag=false × literary 之 CLEAN 閘仍過);**未登入(scope=None)→ deny**
    (fail-closed)。scope=(is_super, allowed) 或 None;work_id 可限縮單一著作;回 [Citation](逐字可溯源、相似度降序)。"""
    if scope is None:
        return []                                  # 未登入/無身分 → fail-closed deny(P4 後對話皆登入;None 僅內部誤用)
    qv = _query_vec(query)
    where = "WHERE " + corpus.clean_work_sql("w")   # works 亦過 CLEAN 閘(C5 修);works 公版素養對所有登入者公開
    if work_id:
        where += " AND c.work_id = %s"
    sql = f"""
    SELECT c.chunk_id, c.work_id, COALESCE(w.title_zh, w.title), th.name_zh,
           t.chapter, c.char_start, c.char_end, t.source_url, c.content,
           1 - (e.embedding <=> %s::vector) AS score
    FROM philosophy_chunk_embedding e
    JOIN philosophy_chunk c USING(chunk_id)
    JOIN philosophy_work w USING(work_id)
    JOIN philosophy_thinker th ON th.thinker_id = w.thinker_id
    JOIN philosophy_work_text t ON t.text_id = c.text_id
    {where}
    ORDER BY e.embedding <=> %s::vector
    LIMIT %s
    """
    params = [qv] + ([work_id] if work_id else []) + [qv, k]
    out = []
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute(sql, params)
        for r in cur.fetchall():
            out.append(Citation(chunk_id=r[0], work_id=r[1], work_title=r[2], thinker=r[3],
                                chapter=r[4], char_start=r[5], char_end=r[6], source_url=r[7],
                                text=r[8], score=float(r[9])))
    return out


def is_low_content(text):
    """低內容 junk chunk 判定(B-1 檢索相關度收尾,計畫 augur_advisor_empty_retrieval_boundary_plan §14):
    去空白後可讀字元(字母/數字/CJK)過少或占比過低 → 非有效引文(如 '--'、'’”'、純導覽符)。
    量測:e5-small cosine 分數 0.80~0.88 窄帶與相關性幾乎無關、絕對門檻不可行(相關/junk 重疊,故不設分數門檻);
    唯 junk chunk(全表 52/126,609≈0.04%)會被 off-topic 題不成比例撈中 → 此為門檻外之安全確定子集。回 bool。"""
    s = (text or "").strip()
    if len(s) < 12:
        return True
    content = sum(1 for ch in s if ch.isalnum())
    return content < 10 or content / len(s) < 0.55


def verify_verbatim(citation):
    """verbatim 逐字回查(多側分派;M2 注入後驗共用單一入口):
    Citation(work chunk)=原文子字串存在性比對;ItemCitation=item_text 定位他證;
    AttachedCitation(Mode B 附加檔)=對附加檔全文子字串他證(不觸 DB)。回 bool。"""
    if isinstance(citation, AttachedCitation):
        return bool(citation.text) and citation.text in citation.source_text
    if isinstance(citation, ItemCitation):
        return verify_verbatim_item(citation)
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT t.content FROM philosophy_work_text t "
                    "JOIN philosophy_chunk c ON c.text_id = t.text_id WHERE c.chunk_id = %s",
                    (citation.chunk_id,))
        row = cur.fetchone()
        return bool(row) and citation.text in row[0]


@dataclass
class LexEntry:
    """一則公版辭書/註疏定義(L3,逐字、可溯源)。"""
    term: str            # 正規化詞形(JOIN 鍵,契約 SSOT=augur.knowledge.textnorm)
    term_display: str    # 原詞條形(繁簡/大小寫原貌)
    language: str
    definition: str      # 逐字定義原文(公版來源,無 AI 改寫)
    work_title: str      # 出處著作(philosophy_work)
    source_locator: str  # 卷/部首/頁碼(引用必附,見 advisor.guard)
    lex_type: str        # dictionary/commentary/thesaurus


@dataclass
class ConcordanceHit:
    """一處逐字用例(L2:knowledge_concordance → knowledge_sentence 回句)。"""
    term: str
    sentence: str        # 逐字原句
    char_start: int      # 相對來源 content 之 char_range(逐字回溯)
    char_end: int
    source_title: str    # work 或 item 標題
    sent_id: int
    position: int


def _tables_exist(cur, *names):
    cur.execute("SELECT " + ", ".join("to_regclass(%s)" for _ in names), names)
    return all(cur.fetchone())


def _term_forms(term):
    """查詢詞形集合(去重保序):NFC 原形 + 小寫 + textnorm 正規形(zh 原貌/en Porter stem),
    履行三方 JOIN 契約(SSOT=augur.knowledge.textnorm);空詞回 []。"""
    t = unicodedata.normalize("NFC", (term or "").strip())
    if not t:
        return []
    forms = [t, t.lower(), textnorm.norm_headword(t, "zh"), textnorm.norm_headword(t, "en")]
    return list(dict.fromkeys(f for f in forms if f))


def lexicon_lookup(term):
    """辭書/註疏定義查詢(L3→L5):回 [LexEntry](逐字定義+出處+locator)。
    庫無此詞或 knowledge_lexicon 未建 → 誠實回空 [](不生成、不猜)。"""
    forms = _term_forms(term)
    if not forms:
        return []
    ph = ", ".join("%s" for _ in forms)
    out = []
    with db.connect() as conn, db.transaction(conn) as cur:
        if not _tables_exist(cur, "knowledge_lexicon"):
            return []
        cur.execute(f"""
        SELECT l.term, l.term_display, l.language, l.definition,
               COALESCE(w.title_zh, w.title), l.source_locator, l.lex_type
        FROM knowledge_lexicon l
        JOIN philosophy_work w ON w.work_id = l.source_work_id
        WHERE l.term IN ({ph}) OR l.term_display IN ({ph})
        ORDER BY l.lex_type, l.lex_id
        """, (*forms, *forms))
        for r in cur.fetchall():
            out.append(LexEntry(term=r[0], term_display=r[1], language=r[2], definition=r[3],
                                work_title=r[4], source_locator=r[5], lex_type=r[6]))
    return out


def concordance_lookup(term, limit=10):
    """逐字用例查詢(L2→L5):回 [ConcordanceHit](原句+char_range+work/item 標題)。
    庫無此詞或 L2 表未建 → 誠實回空 []。
    ⚠ RBAC(§4.5、憲章 v1.29.0):本函式回 knowledge_item 逐字內容但**不過 clean_item_sql domain/擁有者收窄**;
      **目前未接進 advise()/retrieve_all**(僅獨立 L2 查詢)故非現行洩漏面;若未來接入顧問讀取路徑,
      **必先加 clean_item_sql 收窄**(否則繞過 RBAC 洩漏 domain 受限/local_private 內容,破 #1/#5 命門)。"""
    forms = _term_forms(term)
    if not forms:
        return []
    ph = ", ".join("%s" for _ in forms)
    out = []
    with db.connect() as conn, db.transaction(conn) as cur:
        if not _tables_exist(cur, "knowledge_concordance", "knowledge_sentence",
                             "knowledge_item_text", "knowledge_item"):
            return []
        cur.execute(f"""
        SELECT c.term, s.sentence, s.char_start, s.char_end,
               COALESCE(w.title_zh, w.title, i.title_zh, i.title, '') AS source_title,
               s.sent_id, c.position
        FROM knowledge_concordance c
        JOIN knowledge_sentence s ON s.sent_id = c.sent_id
        LEFT JOIN philosophy_work_text wt ON wt.text_id = s.text_id
        LEFT JOIN philosophy_work w ON w.work_id = wt.work_id
        LEFT JOIN knowledge_item_text x ON x.itext_id = s.itext_id
        LEFT JOIN knowledge_item i ON i.item_id = x.item_id
        WHERE c.term IN ({ph})
        ORDER BY s.sent_id, c.position
        LIMIT %s
        """, (*forms, limit))
        for r in cur.fetchall():
            out.append(ConcordanceHit(term=r[0], sentence=r[1], char_start=r[2], char_end=r[3],
                                      source_title=r[4], sent_id=r[5], position=r[6]))
    return out


# ── items 側(N7,e2e 計畫 §3-S7)──────────────────────────────────────────────

@dataclass
class ItemCitation:
    """一筆逐字可溯源的知識文獻句引用(items 側)。"""
    sent_id: int
    itext_id: int
    item_id: int
    item_title: str
    domain: str
    entity_type: str
    char_start: int      # 相對 item_text.content 之定位(verify_verbatim_item 他證基準)
    char_end: int
    source_url: str
    license: str
    text: str            # 逐字原句(== item_text.content[char_start:char_end])
    score: float         # via='exact':查詢詞命中比(counts 類);via='ann':cosine 相似度
    via: str             # 'exact' | 'ann'


_ITEM_COLS = """s.sent_id, s.itext_id, i.item_id, COALESCE(i.title_zh, i.title), i.domain,
           i.entity_type, s.char_start, s.char_end, x.source_url, x.license, s.sentence"""
_ITEM_JOIN = """FROM knowledge_sentence s
        JOIN knowledge_item_text x ON x.itext_id = s.itext_id
        JOIN knowledge_item i ON i.item_id = x.item_id"""


def _guess_language(text):
    """查詢語言判定(確定性、零 ML):含 CJK 即 zh,否則 en。"""
    return "zh" if any("一" <= ch <= "鿿" for ch in text or "") else "en"


def _item_citations(cur, where, params, order, scores, via):
    cur.execute(f"SELECT {_ITEM_COLS} {_ITEM_JOIN} WHERE {where} ORDER BY {order}", params)
    return [ItemCitation(sent_id=r[0], itext_id=r[1], item_id=r[2], item_title=r[3], domain=r[4],
                         entity_type=r[5], char_start=r[6], char_end=r[7], source_url=r[8],
                         license=r[9], text=r[10], score=scores[r[0]], via=via)
            for r in cur.fetchall()]


def retrieve_items(query, k=8, domain=None, language=None, access_scope="public",
                   is_super=False, allowed_domains=None, owner_user_id=None):
    """items 側檢索(讀路徑鐵則 §3-S7)＋ RBAC 收窄(P3/群組建置,§4.2/4.5):
    query→textnorm 全形集→(a)exact SQL 零向量優先→(c)ANN 補位→一律 PG JOIN 取原文;
    CLEAN_ITEM 閘＋RBAC 由 corpus.clean_item_sql 產 (frag, params)、**exact 計數/exact 取原文/ann 三段同帶**
    (一改三處自動同帶、關 L274 與 ANN 補位兩洩漏面);fail-closed:非 super 無授權 → AND false。
    access_scope='public'→domain 收窄(is_super/allowed_domains);='local_private'→擁有者收窄(owner_user_id=登入者)。
    語料空/表未建 → 誠實回空 []。回 [ItemCitation](exact 先、ann 補位)。"""
    if not (query or "").strip():
        return []
    cfrag, cparams = corpus.clean_item_sql("i", "x", access_scope=access_scope,
                                           is_super=is_super, allowed_domains=allowed_domains,
                                           owner_user_id=owner_user_id)
    extra, extra_params = "", []
    if domain:
        extra += " AND i.domain = %s"; extra_params.append(domain)
    if language:
        extra += " AND s.language = %s"; extra_params.append(language)
    out = []
    with db.connect() as conn, db.transaction(conn) as cur:
        if not _tables_exist(cur, "knowledge_item", "knowledge_item_text", "knowledge_sentence"):
            return []
        terms = list({t for t, _ in textnorm.tokenize(query, language or _guess_language(query))})
        if terms and _tables_exist(cur, "knowledge_concordance"):
            cur.execute(f"""SELECT c.sent_id, count(DISTINCT c.term) AS n
                FROM knowledge_concordance c
                JOIN knowledge_sentence s ON s.sent_id = c.sent_id
                JOIN knowledge_item_text x ON x.itext_id = s.itext_id
                JOIN knowledge_item i ON i.item_id = x.item_id
                WHERE c.term = ANY(%s) AND {cfrag}{extra}
                GROUP BY c.sent_id ORDER BY n DESC, c.sent_id LIMIT %s""",
                        (terms, *cparams, *extra_params, k))
            scores = {sid: n / len(terms) for sid, n in cur.fetchall()}
            if scores:
                out = _item_citations(cur, f"s.sent_id = ANY(%s) AND {cfrag}",
                                      (list(scores), *cparams), "s.sent_id", scores, "exact")
                out.sort(key=lambda c: (-c.score, c.sent_id))
        need = k - len(out)
        if need > 0 and _tables_exist(cur, "knowledge_sentence_embedding"):
            cur.execute("SELECT 1 FROM knowledge_sentence_embedding e "
                        "JOIN knowledge_sentence s USING (sent_id) WHERE s.itext_id IS NOT NULL LIMIT 1")
            if cur.fetchone():   # 零向量優先:items 側無嵌入=不載模型(#28)
                qv = _query_vec(query)
                # P4 factory 路(v1.40.0 接縫 DB 化):config=qdrant_* 時 ANN 走外部索引(只回 id+distance),
                # 內容/CLEAN/RBAC 一律回 PG JOIN(雙庫鐵則;外部 id 過不了 cfrag 即被丟=零洩漏面);
                # 外部索引任何故障 → 自動降級 pgvector(D6 fallback 常備)、log 一行不 raise。
                try:
                    from augur.knowledge.vectorindex import make_index
                    _idx = make_index("sentence_items")
                except Exception as e:
                    print(f"[vectorstore] factory 降級 pgvector:{type(e).__name__}: {str(e)[:80]}")
                    _idx = None
                if _idx is not None:
                    try:
                        from augur.knowledge.vectorindex import CollectionSpec
                        _idx.ensure_collection(CollectionSpec(
                            name=embedspec.collection_name("sentence", "items"), dim=embedspec.dim_for()))
                        _vec = [float(v) for v in qv.strip("[]").split(",")]
                        _hits = _idx.search(_vec, max(need * 3, 12))
                        _keep = [int(h[0]) for h in _hits if int(h[0]) not in {c.sent_id for c in out}]
                        if _keep:
                            _rows = _item_citations(cur, f"s.sent_id = ANY(%s) AND {cfrag}{extra}",
                                                    (_keep, *cparams, *extra_params), "s.sent_id",
                                                    {i: 0.0 for i in _keep}, "ann")
                            _order = {sid: n for n, sid in enumerate(_keep)}
                            _rows.sort(key=lambda c: _order.get(c.sent_id, 9e9))
                            out.extend(_rows[:need])
                        return out
                    except Exception as e:                  # server 掛 → 降級走下方 pgvector SQL
                        print(f"[vectorstore] qdrant 故障降級 pgvector:{type(e).__name__}: {str(e)[:80]}")
                seen = [c.sent_id for c in out]
                dedup = " AND s.sent_id != ALL(%s)" if seen else ""
                cur.execute(f"""SELECT {_ITEM_COLS}, 1 - (e.embedding <=> %s::vector) AS score
                    {_ITEM_JOIN}
                    JOIN knowledge_sentence_embedding e ON e.sent_id = s.sent_id
                    WHERE e.model_tag = %s AND {cfrag}{extra}{dedup}
                    ORDER BY e.embedding <=> %s::vector LIMIT %s""",
                            (qv, embedspec.MODEL_TAG, *cparams, *extra_params, *([seen] if seen else []), qv, need))
                for r in cur.fetchall():
                    out.append(ItemCitation(sent_id=r[0], itext_id=r[1], item_id=r[2], item_title=r[3],
                                            domain=r[4], entity_type=r[5], char_start=r[6], char_end=r[7],
                                            source_url=r[8], license=r[9], text=r[10],
                                            score=float(r[11]), via="ann"))
    return out


def retrieve_all(query, k=6, access_scope="public", scope=None):
    """work + item 合併檢索 ＋ RBAC scoped(P3/群組建置,§4.5、憲章 v1.29.0)。對話端唯一組合檢索器:**三路徑**各取半、
    交錯合併、cap k——(1) works=哲學/文學公版經典**對所有登入者公開**;(2) public items 經 domain 群組收窄;
    (3) local_private items 經**擁有者收窄**(僅本人+super)。**scope=(is_super, allowed, user_id) 或 None**;
    None/未登入 → fail-closed 全 deny(非「不濾」)。回混合 [Citation|ItemCitation](verify/prompt/guard 型別感知相容)。
    (access_scope 參數保留為簽章相容;三路徑內部固定分流、不再由此參數決定。)"""
    if not scope:
        is_super, allowed, user_id = False, frozenset(), None
    else:                                                      # 容 2-tuple(舊)與 3-tuple(含 user_id);缺 user_id 視 None
        is_super, allowed = scope[0], scope[1]
        user_id = scope[2] if len(scope) > 2 else None
    half = max(2, (k + 1) // 2)
    works = retrieve(query, k=half, scope=scope)                          # 路徑1:登入者公開
    pub = retrieve_items(query, k=half, access_scope="public",
                         is_super=is_super, allowed_domains=allowed)      # 路徑2:domain 收窄
    priv = []
    if is_super or user_id is not None:                                   # 路徑3:有身分才查私有(否則必 deny、省一趟)
        priv = retrieve_items(query, k=half, access_scope="local_private",
                              is_super=is_super, owner_user_id=user_id)   # 擁有者收窄
    merged = [c for trio in zip_longest(works, pub, priv) for c in trio if c is not None]
    return merged[:k]

def verify_verbatim_item(citation):
    """item_text 定位基準他證(§3-S7):citation.text 須==content 之 substring(FROM char_start+1
    FOR char_end-char_start)——位置+內容雙重驗證,嚴於子字串存在性(防 char_range 錯位/潤飾)。回 bool。"""
    n = citation.char_end - citation.char_start
    if n <= 0:
        return False
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT substring(content FROM %s + 1 FOR %s) FROM knowledge_item_text WHERE itext_id = %s",
                    (citation.char_start, n, citation.itext_id))
        row = cur.fetchone()
        return bool(row) and row[0] == citation.text


# ── Mode B:對話「+」附加檔只問這次(不入庫、僅本回合;零嵌入零 LLM、純規則)────────────

def _passages(text, size=420):
    """把附加檔全文切成 ~size 字之段(依行邊界打包);回 [(char_start, segment)],seg==text[start:start+len]。"""
    out, buf, start, pos = [], [], 0, 0
    for line in text.splitlines(keepends=True):
        if buf and (pos - start) + len(line) > size:
            out.append((start, "".join(buf)))
            buf, start = [], pos
        buf.append(line)
        pos += len(line)
    if buf:
        out.append((start, "".join(buf)))
    return out


def retrieve_attached(query, doc_text, doc_title, k=6):
    """Mode B:把附加檔全文切段、以查詢詞重疊排序,回 [AttachedCitation](逐字對附檔他證)。
    text 為 doc_text 之逐字子字串故 verify_verbatim(AttachedCitation) 恆真;guard 照常對 .text 逐字把關。
    無查詢詞命中 → 回前 k 段(至少給脈絡,仍逐字);doc 空 → []。"""
    import re
    if not (doc_text or "").strip():
        return []
    toks = (set(re.findall(r"[0-9a-z]{2,}", (query or "").lower()))
            | {ch for ch in (query or "") if "一" <= ch <= "鿿"})
    scored = []
    for start, seg in _passages(doc_text):
        low = seg.lower()
        scored.append((sum(1 for t in toks if t in low), start, seg))
    scored.sort(key=lambda x: (-x[0], x[1]))
    top = [x for x in scored if x[0] > 0][:k] or scored[:k]
    out = []
    for s, start, seg in top:
        t = seg.strip()
        if t:
            out.append(AttachedCitation(text=t, source_text=doc_text, work_title=doc_title,
                                        char_start=start, char_end=start + len(seg),
                                        source_url=f"附加文件:{doc_title}", score=float(s)))
    return out
