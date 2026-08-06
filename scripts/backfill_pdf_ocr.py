#!/usr/bin/env python
"""PDF-C：弱／掃描 PDF OCR 補抽 backfill。

🎯 佇列 local 標題 .pdf 且字元數 < trigger；fileparse.extract_text(ocr_pdf=True)。
   source_mark=S0（<!-- via=pdf_ocr -->）；禁 ASR／caption；不經 LLM。
   預設 --dry-run；--apply 寫庫（須 apply-go）。

執行指令矩陣:
  python scripts/backfill_pdf_ocr.py --dry-run --queue P0
  python scripts/backfill_pdf_ocr.py --dry-run --item-id 277775
  python scripts/backfill_pdf_ocr.py --apply --queue P0 --trigger-chars 200 --max-pages 40
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys
import time

import _bootstrap  # noqa: F401
from augur.core import db
from augur.knowledge import fileparse, kh4

SEG_CHARS = 8000


def _path_from_url(url: str | None) -> str | None:
    if not url:
        return None
    if url.startswith("file://"):
        return url[7:]
    return url if os.path.isfile(url) else None


def _detect_lang(text: str) -> str:
    cjk = sum(1 for ch in text[:2000] if "\u4e00" <= ch <= "\u9fff")
    non_space = sum(1 for ch in text[:2000] if not ch.isspace())
    return "zh" if non_space and cjk > non_space * 0.30 else "en"


def _queue_items(cur, *, queue: str, trigger: int, item_id: int | None, limit: int):
    if item_id is not None:
        cur.execute(
            """
            SELECT i.item_id, coalesce(i.title_zh, i.title),
                   (SELECT sum(length(content)) FROM knowledge_item_text x WHERE x.item_id=i.item_id),
                   (SELECT source_url FROM knowledge_item_text x WHERE x.item_id=i.item_id ORDER BY seq LIMIT 1)
            FROM knowledge_item i
            WHERE i.item_id = %s
            """,
            (item_id,),
        )
        return list(cur.fetchall())
    if queue == "P0":
        hi = trigger
        lo = 0
    elif queue == "P2":
        lo, hi = trigger, 2000
    else:
        sys.exit(f"未知 --queue={queue}（P0|P2）")
    cur.execute(
        """
        SELECT i.item_id, coalesce(i.title_zh, i.title),
               (SELECT sum(length(content)) FROM knowledge_item_text x WHERE x.item_id=i.item_id) AS nchars,
               (SELECT source_url FROM knowledge_item_text x WHERE x.item_id=i.item_id ORDER BY seq LIMIT 1)
        FROM knowledge_item i
        WHERE i.domain = 'local'
          AND coalesce(i.title_zh, i.title) ILIKE '%%.pdf'
          AND coalesce(
                (SELECT sum(length(content)) FROM knowledge_item_text x WHERE x.item_id=i.item_id), 0
              ) >= %s
          AND coalesce(
                (SELECT sum(length(content)) FROM knowledge_item_text x WHERE x.item_id=i.item_id), 0
              ) < %s
        ORDER BY 3, i.item_id
        LIMIT %s
        """,
        (lo, hi, limit),
    )
    return list(cur.fetchall())


def _apply_ocr_text(cur, item_id: int, text: str, *, origin_sha: str) -> int:
    """以 S0＋OCR 覆寫正文；優先 UPDATE 既有 itext（保留 id／FK），清舊句／chunk 免殘短文。"""
    cur.execute(
        """
        SELECT itext_id, seq, license, access_scope, source_type, owner_user_id, source_url
        FROM knowledge_item_text
        WHERE item_id = %s
        ORDER BY seq
        """,
        (item_id,),
    )
    rows = cur.fetchall()
    if not rows:
        raise RuntimeError(f"item {item_id} 無 item_text")
    itext_ids = [int(r[0]) for r in rows]
    license, access_scope, source_type, owner_user_id, source_url = rows[0][2:]
    body = text if text.startswith(fileparse.S0_OCR_MARK) else (fileparse.S0_OCR_MARK + text)
    note = f"<!-- origin_media_sha={origin_sha} -->\n"
    if "origin_media_sha=" not in body:
        body = fileparse.S0_OCR_MARK + note + body[len(fileparse.S0_OCR_MARK):]
    lang = _detect_lang(body)
    segments = [body[i:i + SEG_CHARS] for i in range(0, len(body), SEG_CHARS)] or [body]

    # 清依附句／chunk（embedding 多 CASCADE）；concordance 若掛句亦先清
    cur.execute(
        """
        DELETE FROM knowledge_concordance
        WHERE sent_id IN (
          SELECT s.sent_id FROM knowledge_sentence s WHERE s.itext_id = ANY(%s)
        )
        """,
        (itext_ids,),
    )
    cur.execute("DELETE FROM knowledge_sentence WHERE itext_id = ANY(%s)", (itext_ids,))
    cur.execute("DELETE FROM philosophy_chunk WHERE itext_id = ANY(%s)", (itext_ids,))

    # 覆寫／補段
    for idx, frag in enumerate(segments):
        seq = idx + 1
        if idx < len(rows):
            cur.execute(
                """
                UPDATE knowledge_item_text
                   SET content=%s, language=%s, seq=%s,
                       source_url=COALESCE(source_url, %s),
                       license=COALESCE(license, %s),
                       source_type=COALESCE(source_type, %s),
                       access_scope=COALESCE(access_scope, %s),
                       owner_user_id=%s
                 WHERE itext_id=%s
                """,
                (
                    frag, lang, seq, source_url, license,
                    source_type or "local_upload", access_scope, owner_user_id,
                    itext_ids[idx],
                ),
            )
        else:
            cur.execute(
                """
                INSERT INTO knowledge_item_text
                  (item_id, seq, content, language, source_url, license, source_type,
                   access_scope, owner_user_id)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    item_id, seq, frag, lang, source_url,
                    license, source_type or "local_upload", access_scope, owner_user_id,
                ),
            )
    # 多餘舊段
    if len(rows) > len(segments):
        drop_ids = itext_ids[len(segments):]
        cur.execute("DELETE FROM knowledge_item_text WHERE itext_id = ANY(%s)", (drop_ids,))
    kh4.refresh_items(cur, item_ids=[item_id])
    return len(segments)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="PDF-C OCR backfill")
    ap.add_argument("--dry-run", action="store_true",
                    help="只報對照、不寫庫")
    ap.add_argument("--apply", action="store_true",
                    help="寫庫（apply-go）")
    ap.add_argument("--queue", default="P0", choices=("P0", "P2"))
    ap.add_argument("--item-id", type=int, default=None)
    ap.add_argument("--trigger-chars", type=int, default=fileparse.OCR_TRIGGER_CHARS_DEFAULT)
    ap.add_argument("--max-pages", type=int, default=fileparse.OCR_MAX_PAGES_DEFAULT)
    ap.add_argument("--limit", type=int, default=20)
    args = ap.parse_args(argv)

    if args.apply and args.dry_run:
        sys.exit("勿同時 --apply 與 --dry-run")
    do_apply = bool(args.apply)
    if not do_apply and not args.dry_run:
        # 無旗標 → dry-run（安全預設）
        do_apply = False

    trigger = int(args.trigger_chars)
    max_pages = int(args.max_pages)
    mode = "APPLY" if do_apply else "dry-run"
    print(
        f"[pdf-c] {mode} queue={args.queue} trigger={trigger} "
        f"max_pages={max_pages} mark=S0 no-ASR no-caption",
        flush=True,
    )

    with db.connect() as conn, conn.cursor() as cur:
        rows = _queue_items(
            cur, queue=args.queue, trigger=trigger,
            item_id=args.item_id, limit=args.limit,
        )
    if not rows:
        print("[pdf-c] queue empty")
        return 0

    ok_n = 0
    applied = 0
    for item_id, title, nchars, url in rows:
        path = _path_from_url(url)
        print(f"\n--- item={item_id} nchars={nchars} title={title!r}", flush=True)
        if not path or not os.path.isfile(path):
            print(f"  SKIP missing_path url={url!r}")
            continue
        t0 = time.time()
        plain, preason = fileparse.extract_text(path, ocr_pdf=False)
        ocr, oreason = fileparse.extract_text(
            path, ocr_pdf=True,
            ocr_trigger_chars=trigger, ocr_max_pages=max_pages,
        )
        elapsed = round(time.time() - t0, 1)
        pc = len((plain or "").strip())
        oc = len((ocr or "").strip())
        origin_sha = hashlib.sha1(open(path, "rb").read()).hexdigest()
        print(f"  path={path}")
        print(f"  pypdf reason={preason} chars={pc}")
        print(f"  ocr   reason={oreason} chars={oc} elapsed_s={elapsed} origin_sha16={origin_sha[:16]}")
        if oreason != "pdf_ocr" or oc <= pc:
            print("  NO_GAIN (keep existing or quality fail)")
            continue
        head = (fileparse.S0_OCR_MARK + (ocr or ""))[:180].replace("\n", " / ")
        ok_n += 1
        if not do_apply:
            print(f"  WOULD_APPLY S0_head={head!r}")
            continue
        with db.connect() as conn:
            with db.transaction(conn) as cur:
                nseg = _apply_ocr_text(cur, int(item_id), ocr or "", origin_sha=origin_sha)
                cur.execute(
                    "SELECT sum(length(content)) FROM knowledge_item_text WHERE item_id=%s",
                    (item_id,),
                )
                new_n = cur.fetchone()[0]
            print(f"  APPLIED segments={nseg} new_chars={new_n}")
            applied += 1

    print(f"\n[pdf-c] {mode} done gain={ok_n}/{len(rows)} applied={applied}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
