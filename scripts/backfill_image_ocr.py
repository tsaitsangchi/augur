#!/usr/bin/env python
"""Image OCR 閉集 backfill：缺 chi_tra 標記之圖檔重跑 Tesseract。

🎯 佇列 title/external 副檔名為 jpg/png/… 且正文無 `via=image_ocr chi_tra`；
   fileparse.extract_text（預設 OCR_LANGS=chi_tra+eng）。增益＝新 CJK > 舊 CJK。
   寫庫蓋 IMAGE_OCR_MARK；禁 ASR／假造；預設 dry-run。
守 #1· #15· IMAGE-OCR65-GO· FZ-keep· ≠整庫 PDF。

執行指令矩陣:
  python scripts/backfill_image_ocr.py --dry-run
  python scripts/backfill_image_ocr.py --dry-run --item-id 277947
  python scripts/backfill_image_ocr.py --apply --limit 65
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys
import time
from urllib.parse import unquote

import _bootstrap  # noqa: F401
from augur.core import db
from augur.knowledge import fileparse, kh4

SEG_CHARS = 8000
_IMG_TITLE_RE = r"\.(jpg|jpeg|png|gif|webp|bmp)$"


def _path_from_url(url: str | None) -> str | None:
    if not url:
        return None
    if url.startswith("file://"):
        return unquote(url[7:])
    return url if os.path.isfile(url) else None


def _cjk_n(text: str | None) -> int:
    return sum(1 for ch in (text or "") if "\u4e00" <= ch <= "\u9fff")


def _detect_lang(text: str) -> str:
    cjk = _cjk_n(text[:2000])
    non_space = sum(1 for ch in text[:2000] if not ch.isspace())
    return "zh" if non_space and cjk > non_space * 0.20 else "en"


def _queue_items(cur, *, item_id: int | None, limit: int, include_marked: bool):
    if item_id is not None:
        cur.execute(
            """
            SELECT i.item_id, coalesce(i.title_zh, i.title),
                   (SELECT string_agg(content, E'\\n' ORDER BY seq)
                      FROM knowledge_item_text x WHERE x.item_id=i.item_id),
                   (SELECT source_url FROM knowledge_item_text x
                      WHERE x.item_id=i.item_id ORDER BY seq LIMIT 1)
            FROM knowledge_item i
            WHERE i.item_id = %s
            """,
            (item_id,),
        )
        return list(cur.fetchall())
    mark_clause = "" if include_marked else (
        "AND coalesce(("
        "  SELECT string_agg(content, E'\\n') FROM knowledge_item_text x "
        "  WHERE x.item_id=i.item_id"
        "), '') NOT LIKE '%%via=image_ocr chi_tra%%'"
    )
    cur.execute(
        f"""
        SELECT i.item_id, coalesce(i.title_zh, i.title),
               (SELECT string_agg(content, E'\\n' ORDER BY seq)
                  FROM knowledge_item_text x WHERE x.item_id=i.item_id),
               (SELECT source_url FROM knowledge_item_text x
                  WHERE x.item_id=i.item_id ORDER BY seq LIMIT 1)
        FROM knowledge_item i
        WHERE (
            coalesce(i.title, '') ~* %s
            OR coalesce(i.title_zh, '') ~* %s
            OR coalesce(i.external_id, '') ~* %s
          )
          {mark_clause}
        ORDER BY i.item_id
        LIMIT %s
        """,
        (_IMG_TITLE_RE, _IMG_TITLE_RE, _IMG_TITLE_RE, limit),
    )
    return list(cur.fetchall())


def _apply_ocr_text(cur, item_id: int, text: str, *, origin_sha: str) -> int:
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
    mark = fileparse.IMAGE_OCR_MARK
    body = text if text.lstrip().startswith("<!-- via=image_ocr") else (mark + text)
    note = f"<!-- origin_media_sha={origin_sha} -->\n"
    if "origin_media_sha=" not in body:
        # 插在 mark 後
        if body.startswith(mark):
            body = mark + note + body[len(mark):]
        else:
            body = mark + note + body
    lang = _detect_lang(body)
    segments = [body[i:i + SEG_CHARS] for i in range(0, len(body), SEG_CHARS)] or [body]

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
    if len(rows) > len(segments):
        drop_ids = itext_ids[len(segments):]
        cur.execute("DELETE FROM knowledge_item_text WHERE itext_id = ANY(%s)", (drop_ids,))
    kh4.refresh_items(cur, item_ids=[item_id])
    return len(segments)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Image OCR backfill (closed set)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--item-id", type=int, default=None)
    ap.add_argument("--limit", type=int, default=100)
    ap.add_argument(
        "--include-marked",
        action="store_true",
        help="含已有 chi_tra 標記者（預設略過）",
    )
    args = ap.parse_args(argv)

    if args.apply and args.dry_run:
        sys.exit("勿同時 --apply 與 --dry-run")
    do_apply = bool(args.apply)
    mode = "APPLY" if do_apply else "dry-run"
    print(
        f"[image-ocr] {mode} langs={fileparse.OCR_LANGS} "
        f"mark=IMAGE_OCR gain=cjk>old no-ASR",
        flush=True,
    )

    with db.connect() as conn, conn.cursor() as cur:
        rows = _queue_items(
            cur,
            item_id=args.item_id,
            limit=args.limit,
            include_marked=bool(args.include_marked),
        )
    if not rows:
        print("[image-ocr] queue empty")
        return 0

    would = 0
    applied = 0
    no_gain = 0
    skip = 0
    applied_ids: list[int] = []
    for item_id, title, old_text, url in rows:
        old_cjk = _cjk_n(old_text)
        old_n = len(old_text or "")
        path = _path_from_url(url)
        print(
            f"\n--- item={item_id} old_chars={old_n} old_cjk={old_cjk} title={title!r}",
            flush=True,
        )
        if not path or not os.path.isfile(path):
            print(f"  SKIP missing_path url={url!r}")
            skip += 1
            continue
        t0 = time.time()
        text, reason = fileparse.extract_text(path)
        elapsed = round(time.time() - t0, 1)
        new_n = len((text or "").strip())
        new_cjk = _cjk_n(text)
        origin_sha = hashlib.sha1(open(path, "rb").read()).hexdigest()
        print(f"  path={path}")
        print(
            f"  ocr reason={reason} chars={new_n} cjk={new_cjk} "
            f"elapsed_s={elapsed} sha16={origin_sha[:16]}"
        )
        if reason != "image_ocr" or not (text or "").strip():
            print("  SKIP extract_fail")
            skip += 1
            continue
        if new_cjk <= old_cjk:
            print("  NO_GAIN (cjk not improved)")
            no_gain += 1
            continue
        head = (fileparse.IMAGE_OCR_MARK + (text or ""))[:160].replace("\n", " / ")
        would += 1
        if not do_apply:
            print(f"  WOULD_APPLY head={head!r}")
            continue
        with db.connect() as conn:
            with db.transaction(conn) as cur:
                nseg = _apply_ocr_text(cur, int(item_id), text or "", origin_sha=origin_sha)
                cur.execute(
                    "SELECT sum(length(content)) FROM knowledge_item_text WHERE item_id=%s",
                    (item_id,),
                )
                new_db = cur.fetchone()[0]
            print(f"  APPLIED segments={nseg} new_chars={new_db} cjk={new_cjk}")
            applied += 1
            applied_ids.append(int(item_id))

    print(
        f"\n[image-ocr] summary mode={mode} queued={len(rows)} "
        f"would_or_ok={would} applied={applied} no_gain={no_gain} skip={skip}"
    )
    if applied_ids:
        print("applied_ids=" + ",".join(str(i) for i in applied_ids))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
