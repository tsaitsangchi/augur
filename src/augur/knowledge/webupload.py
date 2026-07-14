"""Web 上傳共用工具(admin 後台 + 對話 UI 共用)— multipart 解析、檔名去逃逸、落暫存夾。

🎯 這支在做什麼(白話):把瀏覽器原生資料夾/檔案選取上傳之 multipart body 解析成(欄位, 檔案),
   逐檔去逃逸(剝 ../、絕對路徑)後落 ~/.augur_uploads/<token>/,供 acquire_local_files 同一入庫引擎解析。
   純 stdlib、binary-safe、免 cgi(Python 3.13 已移除);單檔大小/符號連結防護在 fileparse。
   一處實作、admin 與 chat 共用——安全敏感的 multipart 解析不重複兩份(改一漏一之維護坑)。
守 #1(逐字、不改寫)· #5(path traversal/大小防護)· #18(webupload=領域名詞,免 admin/chat 各寫一份)。

自測（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.knowledge.webupload              # 印用途+公開入口（唯讀）
  python -m augur.knowledge.webupload --selftest   # 純紅綠自測（零 IO）
"""
import os
import secrets

from augur.knowledge import fileparse

UPLOAD_ROOT = os.path.join(os.path.expanduser("~"), ".augur_uploads")
MAX_UPLOAD = 300 * 1024 * 1024        # 單次上傳總量上限(防 OOM;超過=413)
from augur.knowledge import corpus
LICENSES = corpus.LICENSE_WHITELIST      # #12 單一 SSOT=corpus(消副本;對抗審查:license 白名單勿三份漂移)
SCOPES = ("public", "local_private")


def _cd_param(disp, key):
    """從 Content-Disposition 取 key="value";無則 None(免 re)。"""
    tok = key + '="'
    i = disp.find(tok)
    if i < 0:
        return None
    i += len(tok)
    j = disp.find('"', i)
    return disp[i:j] if j >= 0 else None


def parse_multipart(raw, boundary):
    """手寫 multipart/form-data 解析(binary-safe、免 cgi;#5)。回 (fields:dict, files:[(filename, bytes)])。"""
    fields, files = {}, []
    delim = b"--" + boundary.encode()
    for part in raw.split(delim):
        if part.startswith(b"\r\n"):
            part = part[2:]
        if part.endswith(b"\r\n"):
            part = part[:-2]
        if not part or part == b"--":
            continue
        head, sep, body = part.partition(b"\r\n\r\n")
        if not sep:
            continue
        disp = ""
        for line in head.split(b"\r\n"):
            if line.lower().startswith(b"content-disposition:"):
                disp = line.decode("utf-8", "replace")
        name = _cd_param(disp, "name")
        filename = _cd_param(disp, "filename")
        if filename is not None:
            if filename:                              # 空 filename(未選檔)= 略過
                files.append((filename, body))
        elif name:
            fields[name] = body.decode("utf-8", "replace")
    return fields, files


def sanitize_relpath(name):
    """上傳檔相對路徑去逃逸:剝 ..、絕對、空段;回安全相對路徑或 None(#5 防 traversal)。"""
    parts = [p for p in (name or "").replace("\\", "/").split("/") if p not in ("", ".", "..")]
    return os.path.join(*parts) if parts else None


def save_upload(files):
    """落 ~/.augur_uploads/<token>/(保夾結構、去逃逸、per-file 大小上限)。回 {updir, saved, big, bad}。"""
    updir = os.path.join(UPLOAD_ROOT, secrets.token_hex(8))
    os.makedirs(updir, exist_ok=True)
    root_abs = os.path.realpath(UPLOAD_ROOT) + os.sep
    saved = big = bad = 0
    for filename, body in files:
        if len(body) > fileparse.MAX_BYTES:
            big += 1
            continue
        rel = sanitize_relpath(filename)
        if not rel:
            bad += 1
            continue
        dest = os.path.join(updir, rel)
        if not os.path.realpath(dest).startswith(root_abs):   # 再核一次不逃逸
            bad += 1
            continue
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as f:
            f.write(body)
        saved += 1
    return {"updir": updir, "saved": saved, "big": big, "bad": bad}


def extract_texts(files):
    """不落地、直接抽每檔逐字文字(Mode B 暫用場景:附加檔案問答、不入庫)。
    回 (combined_text, meta):meta={parsed, skipped, titles}。逐字、抽不出誠實跳過(fileparse SSOT)。"""
    import tempfile
    parts, titles, parsed, skipped = [], [], 0, 0
    for filename, body in files:
        if len(body) > fileparse.MAX_BYTES:
            skipped += 1
            continue
        base = os.path.basename((filename or "").replace("\\", "/")) or "file"
        ext = os.path.splitext(base)[1] or ".bin"
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tf:
            tf.write(body)
            tmp = tf.name
        try:
            text, _reason = fileparse.extract_text(tmp)
        finally:
            os.unlink(tmp)
        if text and text.strip():
            parts.append(f"── {base} ──\n{text.strip()}")
            titles.append(base)
            parsed += 1
        else:
            skipped += 1
    return "\n\n".join(parts), {"parsed": parsed, "skipped": skipped, "titles": titles}


def _selftest():
    """純紅綠自測(零 IO):鎖 path-traversal 去逃逸、Content-Disposition 取值、multipart 解析不變式。"""
    ok = True
    def chk(name, cond):
        nonlocal ok; ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")
    # sanitize_relpath:剝 ../、絕對、空段(#5 命門——traversal 逃逸須全清)
    chk("relpath 剝 ..", sanitize_relpath("../../etc/passwd") == os.path.join("etc", "passwd"))
    chk("relpath 剝絕對", sanitize_relpath("/abs/x.txt") == os.path.join("abs", "x.txt"))
    chk("relpath 剝 . 空段", sanitize_relpath("a/./b//c") == os.path.join("a", "b", "c"))
    chk("relpath 純 .. → None", sanitize_relpath("../..") is None)
    chk("relpath 空 → None", sanitize_relpath("") is None)
    # _cd_param:取 key="value"、無則 None(免 re)
    disp = 'form-data; name="file"; filename="a.txt"'
    chk("cd_param name", _cd_param(disp, "name") == "file")
    chk("cd_param filename", _cd_param(disp, "filename") == "a.txt")
    chk("cd_param 缺鍵 → None", _cd_param('form-data; name="x"', "filename") is None)
    # parse_multipart:欄位/檔案分流、binary-safe、末尾 -- 不誤收
    raw = (b'--BOUND\r\nContent-Disposition: form-data; name="scope"\r\n\r\npublic\r\n'
           b'--BOUND\r\nContent-Disposition: form-data; name="f"; filename="a.txt"\r\n\r\nhello\r\n'
           b'--BOUND--\r\n')
    fields, files = parse_multipart(raw, "BOUND")
    chk("multipart 欄位", fields == {"scope": "public"})
    chk("multipart 檔案", files == [("a.txt", b"hello")])
    # 空 filename(未選檔)略過、只留真檔
    raw2 = (b'--B\r\nContent-Disposition: form-data; name="f"; filename=""\r\n\r\n\r\n'
            b'--B--\r\n')
    _f2, files2 = parse_multipart(raw2, "B")
    chk("空 filename 略過", files2 == [])
    # 常數結構斷言(SCOPES 對映 access_scope、LICENSES 承 corpus SSOT)
    chk("SCOPES 含 public/local_private", set(SCOPES) == {"public", "local_private"})
    chk("LICENSES 非空", isinstance(LICENSES, (tuple, list)) and len(LICENSES) > 0)
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.knowledge.webupload --selftest;免 DB 免 API)")
