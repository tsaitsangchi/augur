"""KH 讀出臂——標題／檔名／文首產品名 resolve＋有界原文入引文（READOUT-RESOLVE）。

🎯 這支在做什麼(白話):處理「國碩-ERP-GP_DR說明…：請讀出具體內容」這類問句——
   先判讀出意圖、用標題／檔名定位 item（落空則文首產品名，如 aap.pdf←應付帳款管理系統），
   再把 item_text 有界切段成 ItemCitation（via=readout），供 advise grounding；禁幻造；
   RBAC 與 CLEAN 同 retrieve。
守 憲章 #1· readout plan ADOPTED· FZ-keep· no-web-approve· #15。

執行指令矩陣(本檔=library #18):
  python -m augur.knowledge.readout --selftest
  python -m augur.knowledge.readout   # 印用途
"""
from __future__ import annotations

import re
import unicodedata
from typing import Any, Sequence

from augur.knowledge.citations import ItemCitation
from augur.knowledge import corpus


# 有界：單答最多灌入 LLM 的原文總字元（仍可被 prompt 層再截）
MAX_CHARS_DEFAULT = 6000
CHUNK_CHARS = 900
RESOLVE_LIMIT = 3
# 標題／檔名落空時，以文首一段做產品名／內文標題 resolve（對症 aap.pdf＝應付帳款…）
CONTENT_HEAD_CHARS = 4000
CONTENT_RESOLVE_SCAN = 40
MIN_CONTENT_HINT_CHARS = 6
_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9._-]{1,}|[\u4e00-\u9fff]{2,}")

_READOUT_RE = re.compile(
    r"(讀出|具體內容|全文|整份|整篇|原文內容|請讀|讀一遍|內容是什麼|說了什麼)"
)
_SPLIT_RE = re.compile(r"[：:]")
_EXT_RE = re.compile(r"\.(docx|pdf|xlsx|txt|md|ppt|pptx|DOCX|PDF|PPT|PPTX)\s*$")


_ASK_RE = re.compile(
    r"(嗎|呢|如何|怎麼|為什么|為什麼|什么|什麼|該不該|可不可以|怎辦|请问|請問|为什么)"
)
# UI／口語常在手冊題後多打 ? —— 不當真假問句語氣（對症：tiptop 應付帳款系統說明?）
_TRAIL_ASK_PUNCT_RE = re.compile(r"[?？\s]+$")
_ERP_PREFIX_RE = re.compile(r"^(tiptop|erp)\s*", re.I)
# 文首產品名別名：aap.pdf 內建＝「應付帳款管理系統」（裸「應付帳款」會被大量雜件洗掉）
_HANDBOOK_ALIASES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"應付帳款.*(系統)?(說明|手冊|介紹|指南)?"), "應付帳款管理系統"),
    (re.compile(r"应付账款.*(系统)?(说明|手册|介绍|指南)?"), "應付帳款管理系統"),
]


def _strip_trail_ask_punct(q: str) -> str:
    return _TRAIL_ASK_PUNCT_RE.sub("", (q or "").strip())


def is_readout_intent(query: str) -> bool:
    """明示讀出／具體內容，或「標題：問句」；或整句本身像匯入檔名／長標題（UI 常只貼檔名）。"""
    q = (query or "").strip()
    if not q:
        return False
    if _READOUT_RE.search(q):
        return True
    # 左側像檔名／長標題，右側是問句
    parts = _SPLIT_RE.split(q, maxsplit=1)
    if len(parts) == 2 and _looks_like_title(parts[0]) and len(parts[1].strip()) >= 2:
        return True
    # 純貼檔名／標題（無問句語氣）→ 視為讀出／依文作答（對症：UI 複製標題卻回「知識庫中無此內容」）
    # 有副檔名時：檔名常含「如何／什麼」（如 TIPTOP如何新增使用者.pdf）→ 勿當問句否決
    # 尾綴 ?／？：手冊題口語標點，剝掉後再判 bare-title（勿因單一字元翻 intent）
    bare = _strip_trail_ask_punct(q)
    if (
        len(bare) <= 160
        and _looks_like_title(bare)
        and (bool(_EXT_RE.search(bare)) or not _ASK_RE.search(bare))
    ):
        return True
    return False


def _looks_like_title(s: str) -> bool:
    s = (s or "").strip()
    if len(s) < 6:
        return False
    if _EXT_RE.search(s):
        return True
    if re.search(r"\d{8}", s):  # 20211007
        return True
    if any(k in s for k in ("說明", "SOP", "辦法", "教學", "手冊", "紀錄", "演練")):
        return True
    return len(s) >= 12


def extract_title_hint(query: str) -> str:
    """自問句抽出標題／檔名提示（去副檔名、去讀出套語）。"""
    q = _strip_trail_ask_punct(query or "")
    parts = _SPLIT_RE.split(q, maxsplit=1)
    head = parts[0].strip() if parts else q
    if len(parts) == 2 and _looks_like_title(parts[0]):
        hint = parts[0].strip()
    elif _READOUT_RE.search(q):
        hint = _READOUT_RE.split(q, maxsplit=1)[0].strip(" ：:，,")
        if len(hint) < 4:
            hint = head
    else:
        hint = head
    # 檔名（aap.pdf）保留副檔名：剝成「aap」會撞 aapt* 雜件；非檔名標題仍去副檔名
    if not _EXT_RE.search(hint):
        hint = _EXT_RE.sub("", hint).strip()
    # 過短則退回原 query 去套語後的可搜片段
    if len(hint) < 4:
        hint = re.sub(r"[：:].*$", "", q).strip()
        if not _EXT_RE.search(hint):
            hint = _EXT_RE.sub("", hint).strip()
    return _strip_trail_ask_punct(hint)


def _resolve_hint_variants(hint: str) -> list[str]:
    """標題／產品別名候選（去 ERP 前綴＋手冊別名）。保序去重。"""
    h0 = _strip_trail_ask_punct(hint or "")
    out: list[str] = []
    seen: set[str] = set()

    def add(s: str) -> None:
        s = (s or "").strip()
        if len(s) < 2:
            return
        key = s.casefold()
        if key in seen:
            return
        seen.add(key)
        out.append(s)

    add(h0)
    stripped = _ERP_PREFIX_RE.sub("", h0).strip()
    add(stripped)
    for blob in (h0, stripped):
        for pat, alias in _HANDBOOK_ALIASES:
            if pat.search(blob):
                add(alias)
    return out


def _scope_tuple(scope) -> tuple[bool, Any, Any]:
    if not scope:
        return False, frozenset(), None
    is_super, allowed = scope[0], scope[1]
    user_id = scope[2] if len(scope) > 2 else None
    return bool(is_super), allowed, user_id


def _nfkc_compact(s: str) -> str:
    """NFKC＋去空白＋casefold：對 PDF 相容字（理→理）與字間空白。"""
    s = unicodedata.normalize("NFKC", s or "")
    s = re.sub(r"\s+", "", s)
    return s.casefold()


def _hint_tokens(hint: str) -> list[str]:
    h = unicodedata.normalize("NFKC", hint or "")
    h = _EXT_RE.sub("", h).strip()
    out: list[str] = []
    seen: set[str] = set()
    for t in _TOKEN_RE.findall(h):
        key = t.casefold()
        if key in seen or len(t) < 2:
            continue
        seen.add(key)
        out.append(t)
    return out


def _sql_prefilter_tokens(hint: str) -> list[str]:
    """SQL ILIKE 預篩用 token：長 CJK 只取 4 字前綴，避開「管理／管理」相容字卡死。"""
    out: list[str] = []
    seen: set[str] = set()
    for t in _hint_tokens(hint):
        if re.fullmatch(r"[\u4e00-\u9fff]+", t) and len(t) >= 4:
            piece = t[:4]
        else:
            piece = t
        key = piece.casefold()
        if key in seen or len(piece) < 2:
            continue
        seen.add(key)
        out.append(piece)
    return out


def _resolve_by_title(cur, hint: str, *, scope=None, limit: int = RESOLVE_LIMIT) -> list[int]:
    """標題／檔名／title_zh／external_id ILIKE。"""
    hint = (hint or "").strip()
    if len(hint) < 2:
        return []
    is_super, allowed, _uid = _scope_tuple(scope)
    cfrag, cparams = corpus.clean_item_sql(
        "i", "x", access_scope="public",
        is_super=is_super, allowed_domains=allowed,
    )
    like = f"%{hint}%"
    stem = _EXT_RE.sub("", hint).strip()
    # 短 stem（aap）會撞 aapt*；有副檔名時只打完整檔名／title_zh
    use_stem = (
        bool(stem) and stem != hint and len(stem) >= 6 and not _EXT_RE.search(hint)
    )
    like_stem = f"%{stem}%" if use_stem else like
    cur.execute(
        f"""
        SELECT i.item_id
        FROM knowledge_item i
        JOIN knowledge_item_text x ON x.item_id = i.item_id
        JOIN knowledge_kh4_state k4 ON k4.item_id = i.item_id
        WHERE k4.answer_status = 'eligible'
          AND {cfrag}
          AND (
            coalesce(i.title_zh, i.title) ILIKE %s
            OR coalesce(i.title, '') ILIKE %s
            OR coalesce(i.title_zh, '') ILIKE %s
            OR coalesce(i.external_id, '') ILIKE %s
            OR (%s AND (
              coalesce(i.title_zh, i.title) ILIKE %s
              OR coalesce(i.title, '') ILIKE %s
            ))
          )
        GROUP BY i.item_id, coalesce(i.title_zh, i.title)
        ORDER BY
          CASE
            WHEN coalesce(i.title_zh, i.title) ILIKE %s THEN 0
            WHEN coalesce(i.title, '') ILIKE %s THEN 1
            ELSE 2
          END,
          length(coalesce(i.title_zh, i.title)),
          i.item_id
        LIMIT %s
        """,
        (*cparams, like, like, like, like, use_stem, like_stem, like_stem,
         f"{hint}%", f"{hint}%", limit),
    )
    return [int(r[0]) for r in cur.fetchall()]


def _resolve_by_content_head(cur, hint: str, *, scope=None, limit: int = RESOLVE_LIMIT) -> list[int]:
    """文首內容標題／產品名（標題落空時）：NFKC 緊湊比對，SQL 先用 token 預篩。"""
    raw = (hint or "").strip()
    stem = _EXT_RE.sub("", raw).strip() or raw
    target = _nfkc_compact(stem)
    if len(target) < MIN_CONTENT_HINT_CHARS:
        return []
    tokens = _hint_tokens(stem)
    sql_toks = _sql_prefilter_tokens(stem)
    if not tokens or not sql_toks:
        return []
    # 預篩：最長的 1～2 個 SQL-safe token（勿單用過短）
    strong = sorted(sql_toks, key=len, reverse=True)
    strong = [t for t in strong if len(t) >= 2][:2]
    if not strong or (len(strong) == 1 and len(strong[0]) < 4):
        return []
    is_super, allowed, _uid = _scope_tuple(scope)
    cfrag, cparams = corpus.clean_item_sql(
        "i", "x", access_scope="public",
        is_super=is_super, allowed_domains=allowed,
    )
    where_tok = " AND ".join(
        [f"left(x.content, {CONTENT_HEAD_CHARS}) ILIKE %s" for _ in strong]
    )
    tok_params = [f"%{t}%" for t in strong]
    cur.execute(
        f"""
        SELECT i.item_id, left(x.content, {CONTENT_HEAD_CHARS})
        FROM knowledge_item i
        JOIN knowledge_item_text x ON x.item_id = i.item_id
        JOIN knowledge_kh4_state k4 ON k4.item_id = i.item_id
        WHERE k4.answer_status = 'eligible'
          AND {cfrag}
          AND x.seq = (
            SELECT MIN(xx.seq) FROM knowledge_item_text xx WHERE xx.item_id = i.item_id
          )
          AND {where_tok}
        ORDER BY i.item_id
        LIMIT %s
        """,
        (*cparams, *tok_params, CONTENT_RESOLVE_SCAN),
    )
    scored: list[tuple[int, int, int]] = []
    # 終判用完整 NFKC token（可吃 管理→管理）；不止 SQL 前綴
    full_c = [_nfkc_compact(t) for t in tokens]
    for item_id, head in cur.fetchall():
        compact = _nfkc_compact(head or "")
        if target in compact:
            pos = compact.find(target)
            scored.append((0, pos, int(item_id)))
        elif full_c and all(t in compact for t in full_c):
            pos = min((compact.find(t) for t in full_c if t in compact), default=10**9)
            scored.append((1, pos, int(item_id)))
    scored.sort()
    out: list[int] = []
    seen: set[int] = set()
    for _, _, iid in scored:
        if iid in seen:
            continue
        seen.add(iid)
        out.append(iid)
        if len(out) >= limit:
            break
    return out


def resolve_item_ids(cur, hint: str, *, scope=None, limit: int = RESOLVE_LIMIT) -> list[int]:
    """標題／檔名优先；落空則文首產品名／內文標題（eligible＋CLEAN＋RBAC public）。

    M3 pool-gate：resolve／citations 路徑必 JOIN knowledge_item_text——
    有 weight／標題列 ≠ 可答（見 augur.knowledge.pool_gate）。
    """
    hint = (hint or "").strip()
    if len(hint) < 2:
        return []
    for cand in _resolve_hint_variants(hint):
        ids = _resolve_by_title(cur, cand, scope=scope, limit=limit)
        if ids:
            return ids
        ids = _resolve_by_content_head(cur, cand, scope=scope, limit=limit)
        if ids:
            return ids
    return []


def _chunk_text(content: str, *, max_chars: int, chunk: int) -> list[tuple[int, int, str]]:
    """回 (char_start, char_end, text) 列表；總長 ≤ max_chars。"""
    content = content or ""
    out = []
    total = 0
    n = len(content)
    i = 0
    while i < n and total < max_chars:
        end = min(i + chunk, n, i + (max_chars - total))
        # 盡量在換行切斷
        if end < n:
            nl = content.rfind("\n", i + chunk // 2, end)
            if nl > i:
                end = nl + 1
        frag = content[i:end]
        if frag.strip():
            out.append((i, end, frag))
            total += len(frag)
        if end <= i:
            break
        i = end
    return out


def citations_for_items(
    cur,
    item_ids: Sequence[int],
    *,
    max_chars: int = MAX_CHARS_DEFAULT,
    chunk: int = CHUNK_CHARS,
) -> list[ItemCitation]:
    """依 item 載有界原文段為 ItemCitation（via=readout）。"""
    if not item_ids:
        return []
    per = max(chunk, max_chars // max(1, len(item_ids)))
    out: list[ItemCitation] = []
    budget = max_chars
    for iid in item_ids:
        if budget <= 0:
            break
        cur.execute(
            """
            SELECT i.item_id, coalesce(i.title_zh, i.title), i.domain, i.entity_type,
                   x.itext_id, x.content, coalesce(x.source_url, ''), coalesce(x.license, '')
            FROM knowledge_item i
            JOIN knowledge_item_text x ON x.item_id = i.item_id
            WHERE i.item_id = %s
            ORDER BY x.seq
            LIMIT 1
            """,
            (int(iid),),
        )
        row = cur.fetchone()
        if not row:
            continue
        _id, title, domain, etype, itext_id, content, url, lic = row
        pieces = _chunk_text(content or "", max_chars=min(budget, per), chunk=chunk)
        for start, end, text in pieces:
            out.append(
                ItemCitation(
                    sent_id=0,
                    itext_id=int(itext_id),
                    item_id=int(_id),
                    item_title=title or "",
                    domain=domain or "",
                    entity_type=etype or "document",
                    char_start=int(start),
                    char_end=int(end),
                    source_url=url or "",
                    license=lic or "",
                    text=text,
                    score=1.0,
                    via="readout",
                )
            )
            budget -= len(text)
            if budget <= 0:
                break
    return out


def advise_readout_citations(query: str, *, scope=None, max_chars: int = MAX_CHARS_DEFAULT) -> list[ItemCitation]:
    """advise 熱路徑入口：意圖→resolve→citations；無權／無件→[]。"""
    if not is_readout_intent(query):
        return []
    hint = extract_title_hint(query)
    if len(hint) < 2:
        return []
    from augur.core import db

    with db.connect() as conn, conn.cursor() as cur:
        ids = resolve_item_ids(cur, hint, scope=scope)
        if not ids:
            return []
        return citations_for_items(cur, ids, max_chars=max_chars)


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    q = "國碩-ERP-GP_DR說明(20211007-4-rman)1：請讀出具體內容"
    chk("intent readout", is_readout_intent(q) is True)
    chk("intent bare title", is_readout_intent("國碩-ERP-GP_DR說明(20211007-4-rman)1") is True)
    chk("intent plain no", is_readout_intent("什麼是知行合一") is False)
    chk("intent how-ask no", is_readout_intent("國碩 DR 演練要怎麼做") is False)
    chk("intent 檔名含如何", is_readout_intent("TIPTOP如何新增使用者.pdf") is True)
    chk("intent 無副檔名含如何當問句", is_readout_intent("TIPTOP如何新增使用者") is False)
    chk(
        "intent 手冊題尾綴?",
        is_readout_intent("tiptop 應付帳款系統說明?") is True,
    )
    chk(
        "hint 剝尾綴?",
        extract_title_hint("tiptop 應付帳款系統說明?") == "tiptop 應付帳款系統說明",
    )
    variants = _resolve_hint_variants("tiptop 應付帳款系統說明?")
    chk("alias 含應付帳款管理系統", "應付帳款管理系統" in variants)

    hint = extract_title_hint(q)
    chk("hint 含國碩", "國碩" in hint and "ERP" in hint)
    chk("hint 無請讀出", "請讀出" not in hint)
    chk("hint 保留 pdf", extract_title_hint("aap.pdf：請讀出具體內容") == "aap.pdf")
    chk("hint 保留 docx", extract_title_hint("報告.docx：請讀出") == "報告.docx")
    chk("intent bare ppt", is_readout_intent("TIPTOP GP5.3-生產管理.ppt") is True)
    chk("hint 保留 ppt", extract_title_hint("TIPTOP GP5.3-生產管理.ppt") == "TIPTOP GP5.3-生產管理.ppt")
    chk("hint 無副檔名仍去", ".pdf" not in extract_title_hint("無檔名長標題說明文件：請讀出.pdf附註"))
    chk("nfkc 理→理", _nfkc_compact("管理") == _nfkc_compact("管理"))
    chk("nfkc 去空白", "應付帳款" in _nfkc_compact("應 付 帳 款"))
    chunks = _chunk_text("a" * 2500, max_chars=2000, chunk=900)
    chk("chunk 有界", sum(len(t) for _, _, t in chunks) <= 2000 and len(chunks) >= 2)
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def main(argv=None) -> int:
    import sys

    argv = list(sys.argv[1:] if argv is None else argv)
    if "--selftest" in argv:
        return _selftest()
    print(__doc__)
    print("公開: is_readout_intent / extract_title_hint / advise_readout_citations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
