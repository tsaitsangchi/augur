"""匯入檔案合格檢驗帳本 helper — 本機匯入 job/qualification 單一住所。

🎯 這支在做什麼(白話):為本機檔案匯入建立兩層帳本——job 級(`knowledge_import_job`)與檔案級
   qualification(`knowledge_import_qualification`)；writer 只記錄 preflight/入庫真相，**不**做
   approve/activate、**不**改既有 license gate。`acquire_local_files.py` 與其上層 UI 入口共用本模組，
   避免每條匯入路徑各寫一套帳本邏輯而漂移。
守 #12(單一住所)· #6(冪等/前向更新)· #15(無 silent drop；每檔先落 qualification 再處理)。

執行指令矩陣（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.knowledge.import_qualification
  python -m augur.knowledge.import_qualification --selftest
"""
from __future__ import annotations

import hashlib
import json
import os

from augur.knowledge import fileparse

VERDICT_PENDING = "pending"
VERDICT_PASS = "pass"
VERDICT_REJECT = "reject"
VERDICT_ERROR = "error"

REASON_QUEUED = "queued"
REASON_PREFLIGHT_OK = "preflight_ok"
REASON_DUPLICATE_CONTENT = "duplicate_content"
REASON_WRITE_OK = "write_ok"
REASON_INGEST_ERROR = "ingest_error"
REASON_TOO_SHORT = "too_short"
REASON_SKIP_OTHER = "skip_other"

SKIP_REASON_MAP = {
    "oversize": "skip_oversize",
    "symlink": "skip_symlink",
    "empty": "skip_empty",
    "decode_error": "skip_decode_error",
    "parse_error": "skip_parse_error",
    "encrypted": "skip_encrypted",
    "unknown_ext": "skip_unknown_ext",
    "no_text": "skip_no_text",
    "missing_ocr": "skip_missing_ocr",
    "missing_parser": "skip_missing_parser",
}


def _json(data):
    return json.dumps(data, ensure_ascii=False)


def create_job(cur, *, channel, source_key, root_path, license, access_scope,
               domain, owner_user_id, is_dry_run):
    """建立匯入 job 帳本列；回 job_id。"""
    cur.execute(
        """
        INSERT INTO knowledge_import_job
          (channel, source_key, root_path, declared_license, access_scope, domain,
           owner_user_id, is_dry_run, status)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'running')
        RETURNING job_id
        """,
        (channel, source_key, root_path, license, access_scope, domain, owner_user_id, is_dry_run),
    )
    return cur.fetchone()[0]


def set_job_total(cur, job_id, total_files):
    cur.execute(
        "UPDATE knowledge_import_job SET total_files=%s WHERE job_id=%s",
        (total_files, job_id),
    )


def create_qualification(cur, *, job_id, abs_path, rel_path):
    """每檔先落 qualification 初值；杜 silent drop。"""
    try:
        size = os.path.getsize(abs_path)
    except OSError:
        size = None
    cur.execute(
        """
        INSERT INTO knowledge_import_qualification
          (job_id, abs_path, rel_path, size_bytes, verdict, reason_code)
        VALUES (%s,%s,%s,%s,%s,%s)
        RETURNING qualification_id
        """,
        (job_id, abs_path, rel_path, size, VERDICT_PENDING, REASON_QUEUED),
    )
    return cur.fetchone()[0]


def preflight(path, *, min_chars, ocr_pdf=False):
    """回 preflight dict：抽取結果、字數、sha1、建議 verdict/reason。"""
    text, reason = fileparse.extract_text(path, ocr_pdf=bool(ocr_pdf))
    out = {
        "extract_reason": reason,
        "text_chars": 0,
        "sha1": None,
        "verdict": VERDICT_PENDING,
        "reason_code": REASON_QUEUED,
    }
    if text is None:
        out["verdict"] = VERDICT_REJECT
        out["reason_code"] = SKIP_REASON_MAP.get(reason, REASON_SKIP_OTHER)
        return out
    stripped = text.strip()
    if reason == "pdf_ocr":
        stripped = (fileparse.S0_OCR_MARK + stripped).strip()
    elif reason == "image_ocr":
        if not stripped.startswith("<!-- via=image_ocr"):
            stripped = (fileparse.IMAGE_OCR_MARK + stripped).strip()
    out["text_chars"] = len(stripped)
    out["sha1"] = hashlib.sha1(stripped.encode("utf-8", "replace")).hexdigest()
    if len(stripped) < min_chars:
        out["verdict"] = VERDICT_REJECT
        out["reason_code"] = REASON_TOO_SHORT
        return out
    out["verdict"] = VERDICT_PASS
    out["reason_code"] = REASON_PREFLIGHT_OK
    return out


def mark_preflight(cur, qualification_id, pf):
    cur.execute(
        """
        UPDATE knowledge_import_qualification
           SET verdict=%s,
               reason_code=%s,
               preflight=%s::jsonb,
               preflight_at=now()
         WHERE qualification_id=%s
        """,
        (pf["verdict"], pf["reason_code"], _json(pf), qualification_id),
    )


def mark_ingest(cur, qualification_id, *, ingest_status, item_id, segment_rows,
                reason_code=None, error_text=None):
    verdict = VERDICT_ERROR if error_text else VERDICT_PASS
    code = reason_code or REASON_WRITE_OK
    cur.execute(
        """
        UPDATE knowledge_import_qualification
           SET verdict=%s,
               reason_code=%s,
               ingest_status=%s,
               item_id=%s,
               segment_rows=%s,
               error_text=%s,
               ingested_at=now()
         WHERE qualification_id=%s
        """,
        (verdict, code, ingest_status, item_id, segment_rows, error_text, qualification_id),
    )


def mark_dry_run(cur, qualification_id):
    cur.execute(
        """
        UPDATE knowledge_import_qualification
           SET ingest_status='dry_run'
         WHERE qualification_id=%s
        """,
        (qualification_id,),
    )


def finalize_job(cur, job_id, *, status, stats, summary=None):
    cur.execute(
        """
        UPDATE knowledge_import_job
           SET status=%s,
               scanned_files=%s,
               ok_files=%s,
               dup_files=%s,
               short_files=%s,
               skip_files=%s,
               fail_files=%s,
               summary=%s::jsonb,
               finished_at=now()
         WHERE job_id=%s
        """,
        (
            status,
            stats.get("scanned", 0),
            stats.get("ok", 0),
            stats.get("dup", 0),
            stats.get("short", 0),
            sum(stats.get("skips", {}).values()),
            stats.get("fail", 0),
            _json(summary or {}),
            job_id,
        ),
    )


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("VERDICT 集合穩定", {VERDICT_PENDING, VERDICT_PASS, VERDICT_REJECT, VERDICT_ERROR}
        == {"pending", "pass", "reject", "error"})
    chk("SKIP_REASON_MAP 覆蓋 fileparse.SKIP", set(fileparse.SKIP) <= set(SKIP_REASON_MAP))
    chk("queued/reason 常數存在", REASON_QUEUED == "queued" and REASON_PREFLIGHT_OK == "preflight_ok")
    chk("write_ok/reject 分流常數存在", REASON_WRITE_OK == "write_ok" and REASON_TOO_SHORT == "too_short")
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.knowledge.import_qualification --selftest;免 DB 免 API)")
