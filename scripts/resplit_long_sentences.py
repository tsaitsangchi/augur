#!/usr/bin/env python
"""長句重切（items／works）— LSR-S1。

🎯 這支在做什麼(白話):找出超長 sentence（預設 len>max_chars），對整段 parent
   重編句列（硬切≤max_chars）→刪舊句（嵌 CASCADE）→插新句→寫 ledger。
   不改 junk 上限、不假抬 KH4、零市場 API。
守 #1· #6· #15· #29a/d· FZ-keep· LSR-PLAN D1–D5。

執行指令矩陣:
  python scripts/resplit_long_sentences.py                     # 矩陣+--check
  python scripts/resplit_long_sentences.py --check
  python scripts/resplit_long_sentences.py --dry-run --side items --limit 20
  python scripts/resplit_long_sentences.py --apply --side items --max-chars 800
  python scripts/resplit_long_sentences.py --apply --side items --itext-id 123
  python scripts/resplit_long_sentences.py --selftest
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import _bootstrap  # noqa: F401
from augur.core import db
from augur.knowledge import sent_resplit as sr

SCRIPT = "resplit_long_sentences.py"


def _git_sha() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=str(Path(__file__).resolve().parents[1]),
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return None


def inventory(cur, *, side: str, max_chars: int) -> dict:
    if side == "items":
        cur.execute(
            """
            SELECT count(*) FILTER (WHERE length(sentence) > %s),
                   count(DISTINCT itext_id) FILTER (WHERE length(sentence) > %s),
                   count(*)
            FROM knowledge_sentence WHERE itext_id IS NOT NULL
            """,
            (max_chars, max_chars),
        )
    else:
        cur.execute(
            """
            SELECT count(*) FILTER (WHERE length(sentence) > %s),
                   count(DISTINCT text_id) FILTER (WHERE length(sentence) > %s),
                   count(*)
            FROM knowledge_sentence WHERE text_id IS NOT NULL
            """,
            (max_chars, max_chars),
        )
    gt, parents, n = cur.fetchone()
    return {"gt_max": gt, "parents": parents, "n_sent": n, "side": side, "max_chars": max_chars}


def list_parent_ids(cur, *, side: str, max_chars: int, limit: int | None, parent_id: int | None):
    if side == "items":
        if parent_id is not None:
            return [parent_id]
        sql = (
            "SELECT DISTINCT itext_id FROM knowledge_sentence "
            "WHERE itext_id IS NOT NULL AND length(sentence) > %s ORDER BY 1"
        )
        params: list = [max_chars]
    else:
        if parent_id is not None:
            return [parent_id]
        sql = (
            "SELECT DISTINCT text_id FROM knowledge_sentence "
            "WHERE text_id IS NOT NULL AND length(sentence) > %s ORDER BY 1"
        )
        params = [max_chars]
    if limit is not None:
        sql += " LIMIT %s"
        params.append(limit)
    cur.execute(sql, params)
    return [r[0] for r in cur.fetchall()]


def load_parent(cur, *, side: str, parent_id: int):
    if side == "items":
        cur.execute(
            "SELECT content, COALESCE(language,'en') FROM knowledge_item_text WHERE itext_id=%s",
            (parent_id,),
        )
    else:
        cur.execute(
            "SELECT content, COALESCE(language,'zh') FROM philosophy_work_text WHERE text_id=%s",
            (parent_id,),
        )
    row = cur.fetchone()
    if not row:
        return None
    content, lang = row
    if side == "items":
        cur.execute(
            "SELECT sent_id, seq, char_start, char_end, length(sentence) "
            "FROM knowledge_sentence WHERE itext_id=%s ORDER BY seq, sent_id",
            (parent_id,),
        )
    else:
        cur.execute(
            "SELECT sent_id, seq, char_start, char_end, length(sentence) "
            "FROM knowledge_sentence WHERE text_id=%s ORDER BY seq, sent_id",
            (parent_id,),
        )
    sents = cur.fetchall()
    return {"content": content or "", "language": lang, "sents": sents}


def plan_parent(content: str, sents, *, max_chars: int) -> tuple[list[int], list[tuple[int, int]]]:
    """回 (old_sent_ids, new_spans)。以既有句 span 為底再硬切。"""
    old_ids = [r[0] for r in sents]
    if not sents:
        return [], []
    base = [(int(r[2]), int(r[3])) for r in sents]
    # 防壞 offset
    n = len(content)
    fixed = []
    for s, e in base:
        s = max(0, min(s, n))
        e = max(s, min(e, n))
        if e > s:
            fixed.append((s, e))
    new_spans = sr.expand_spans(content, fixed, max_chars=max_chars)
    return old_ids, new_spans


def apply_parent(cur, *, side: str, parent_id: int, max_chars: int, dry_run: bool, note: str | None):
    loaded = load_parent(cur, side=side, parent_id=parent_id)
    if not loaded:
        return {"ok": False, "error": "parent_missing", "parent_id": parent_id}
    content = loaded["content"]
    lang = loaded["language"]
    if not any(r[4] > max_chars for r in loaded["sents"]):
        return {"ok": True, "skipped": True, "parent_id": parent_id}
    old_ids, new_spans = plan_parent(content, loaded["sents"], max_chars=max_chars)
    if not new_spans:
        return {"ok": False, "error": "empty_new_spans", "parent_id": parent_id}

    preview = {
        "ok": True,
        "parent_id": parent_id,
        "old_n": len(old_ids),
        "new_n": len(new_spans),
        "max_new_len": max((e - s) for s, e in new_spans) if new_spans else 0,
        "dry_run": dry_run,
    }
    if dry_run:
        return preview

    # DELETE all sentences for parent (embedding CASCADE)
    if side == "items":
        cur.execute("DELETE FROM knowledge_sentence WHERE itext_id=%s RETURNING sent_id", (parent_id,))
    else:
        cur.execute("DELETE FROM knowledge_sentence WHERE text_id=%s RETURNING sent_id", (parent_id,))
    deleted = [r[0] for r in cur.fetchall()]

    new_ids = []
    for seq, (s, e) in enumerate(new_spans):
        sent = content[s:e]
        if side == "items":
            cur.execute(
                "INSERT INTO knowledge_sentence "
                "(text_id, itext_id, seq, sentence, language, char_start, char_end) "
                "VALUES (NULL,%s,%s,%s,%s,%s,%s) RETURNING sent_id",
                (parent_id, seq, sent, lang, s, e),
            )
        else:
            cur.execute(
                "INSERT INTO knowledge_sentence "
                "(text_id, itext_id, seq, sentence, language, char_start, char_end) "
                "VALUES (%s,NULL,%s,%s,%s,%s,%s) RETURNING sent_id",
                (parent_id, seq, sent, lang, s, e),
            )
        new_ids.append(cur.fetchone()[0])

    cur.execute(
        "INSERT INTO knowledge_sentence_resplit_ledger "
        "(side, parent_id, old_sent_ids, new_sent_ids, max_chars, old_count, new_count, "
        " bytes_in, script, git_sha, note) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (
            side,
            parent_id,
            deleted,
            new_ids,
            max_chars,
            len(deleted),
            len(new_ids),
            len(content.encode("utf-8")),
            SCRIPT,
            _git_sha(),
            note,
        ),
    )
    preview.update({"applied": True, "old_sent_ids_n": len(deleted), "new_sent_ids_n": len(new_ids)})
    return preview


def selftest() -> int:
    rc = sr._selftest()
    ok = rc == 0

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("指令矩陣含 --apply/--selftest", "--apply" in (__doc__ or "") and "--selftest" in (__doc__ or ""))
    chk("預設 max≤800 常量", sr.DEFAULT_MAX_CHARS <= 800)
    chk("零 FinMind 字樣於模組路徑", "finmind" not in SCRIPT.lower())
    # plan_parent 單元
    content = ("word " * 300).strip()
    fake_sents = [(1, 0, 0, len(content), len(content))]
    old, spans = plan_parent(content, fake_sents, max_chars=80)
    chk("plan 產出多段", len(spans) > 3)
    chk("plan 每段≤80", all(e - s <= 80 for s, e in spans))
    print("runner 自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="LSRS long sentence resplit")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--side", choices=("items", "works"), default="items")
    ap.add_argument("--max-chars", type=int, default=sr.DEFAULT_MAX_CHARS)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--itext-id", type=int, default=None, help="items 側 parent")
    ap.add_argument("--text-id", type=int, default=None, help="works 側 parent")
    ap.add_argument("--note", default="LSRS-S01")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    if args.max_chars > sr.MAX_CHARS_CAP:
        sys.exit(f"--max-chars 禁止 >{sr.MAX_CHARS_CAP}")

    parent_id = args.itext_id if args.side == "items" else args.text_id
    want = args.apply or args.dry_run or args.check
    if not want:
        print(__doc__)
        args.check = True

    with db.connect() as conn, conn.cursor() as cur:
        cur.execute("SELECT to_regclass('public.knowledge_sentence_resplit_ledger')")
        if not cur.fetchone()[0]:
            print("ledger 未建——先 migrate_sentence_resplit_ddl.py --apply")
            return 1
        inv = inventory(cur, side=args.side, max_chars=args.max_chars)
        print(f"inventory={inv}")
        if args.check and not (args.apply or args.dry_run):
            return 0

        parents = list_parent_ids(
            cur,
            side=args.side,
            max_chars=args.max_chars,
            limit=args.limit,
            parent_id=parent_id,
        )
        print(f"parents_to_process={len(parents)} dry_run={args.dry_run and not args.apply}")
        dry = not args.apply
        n_ok = n_skip = n_fail = 0
        for pid in parents:
            r = apply_parent(
                cur,
                side=args.side,
                parent_id=pid,
                max_chars=args.max_chars,
                dry_run=dry,
                note=args.note,
            )
            if r.get("error"):
                n_fail += 1
                print(f"  FAIL parent={pid} {r}")
            elif r.get("skipped"):
                n_skip += 1
            else:
                n_ok += 1
                if n_ok <= 10 or n_ok % 50 == 0:
                    print(f"  parent={pid} old={r.get('old_n')}→new={r.get('new_n')} "
                          f"max_len={r.get('max_new_len')} dry={r.get('dry_run')}")
        if args.apply:
            conn.commit()
        else:
            conn.rollback()
        print(f"── 完成 ok={n_ok} skip={n_skip} fail={n_fail} apply={args.apply}")
        if args.apply:
            print("inventory_after=", inventory(cur, side=args.side, max_chars=args.max_chars))
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
