#!/usr/bin/env python
"""augur 知識控制台 Admin 後台(P3,計畫 §四)— 登入認證 + 觸發主題抓/資料夾解析 + 狀態監看。

🎯 這支在做什麼(白話):admin 登入後,一頁觸發「主題自動抓」(P2 acquire_topic)、「+資料夾解析」
   (P1 acquire_local_files)、看知識層狀態,並連到「誠實博學的我」對話(:8090)。**只觸發既有本地 script、
   不重造管線、不繞 guard**;綁 127.0.0.1 僅本機。
安全(#5 OWASP):密碼 pbkdf2_hmac 雜湊(env AUGUR_ADMIN_PASSWORD,禁明文禁進 git;--set-password 產)、
   session token(secrets、HttpOnly+SameSite=Strict cookie、逾時)、常數時間比對、`+路徑` realpath 圍欄
   (限 $HOME 下、拒 ../ 逃逸)、subprocess 參數陣列 shell=False(防注入)、審計 log(誰/何時/何動作)。
守 #5(OWASP)· #28(觸發本地引擎零 Claude usage)· #29 · 計畫 §四(admin 操作面、既有管線之 UI)。

執行指令矩陣:
  python scripts/serve_admin_console.py --set-password        # 互動設密碼 → 印 env 該設之 AUGUR_ADMIN_PASSWORD
  AUGUR_ADMIN_PASSWORD='pbkdf2$...' python scripts/serve_admin_console.py --serve   # 起後台(127.0.0.1:8500)
  python scripts/serve_admin_console.py                        # 無參數:印本矩陣+操作值(不起 server)
"""
import argparse
import getpass
import hashlib
import hmac
import html
import json
import os
import secrets
import subprocess
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

import _bootstrap  # noqa: F401
from augur.core import db, config

PORT = 8500
SESSION_TTL = 3600          # session 秒數
_ITER = 240000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIT_LOG = os.path.join(os.path.expanduser("~"), "augur_chat_logs", "admin_audit.log")


def hash_password(pw, salt=None):
    salt = salt or secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", pw.encode(), bytes.fromhex(salt), _ITER).hex()
    return f"pbkdf2${_ITER}${salt}${h}"


def verify_password(pw, stored):
    try:
        _, it, salt, h = stored.split("$")
        calc = hashlib.pbkdf2_hmac("sha256", pw.encode(), bytes.fromhex(salt), int(it)).hex()
        return hmac.compare_digest(calc, h)                # 常數時間比對(防 timing)
    except Exception:
        return False


def _safe_dir(path):
    """`+資料夾` 圍欄:realpath 展開,須在 $HOME 下(拒 ../ 逃逸/絕對路徑逃逸);回 realpath 或 None。"""
    home = os.path.realpath(os.path.expanduser("~"))
    rp = os.path.realpath(os.path.expanduser(path or ""))
    return rp if (rp == home or rp.startswith(home + os.sep)) and os.path.isdir(rp) else None


def _audit(action, detail):
    os.makedirs(os.path.dirname(AUDIT_LOG), exist_ok=True)
    with open(AUDIT_LOG, "a") as f:
        f.write(f"{int(time.time())}\t{action}\t{detail}\n")


_SESSIONS = {}   # token -> expiry


def _new_session():
    t = secrets.token_urlsafe(32)
    _SESSIONS[t] = time.time() + SESSION_TTL
    return t


def _valid(token):
    exp = _SESSIONS.get(token)
    if exp and exp > time.time():
        return True
    _SESSIONS.pop(token, None)
    return False


LOGIN_HTML = """<!doctype html><meta charset=utf-8><title>augur admin</title>
<body style="font-family:system-ui;background:#0d1117;color:#e6edf3;max-width:360px;margin:80px auto">
<h2>augur 知識控制台</h2>{msg}
<form method=post action=/login><input type=password name=pw placeholder=密碼 autofocus
 style="width:100%;padding:10px;margin:8px 0;background:#161b22;border:1px solid #30363d;color:#e6edf3;border-radius:6px">
<button style="width:100%;padding:10px;background:#238636;color:#fff;border:0;border-radius:6px">登入</button></form></body>"""


def dashboard_html(status):
    return f"""<!doctype html><meta charset=utf-8><title>augur 知識控制台</title>
<body style="font-family:system-ui;background:#0d1117;color:#e6edf3;max-width:720px;margin:30px auto">
<h2>augur 知識控制台 <a href=/logout style=font-size:13px>登出</a></h2>
<div style="background:#161b22;border:1px solid #21262d;border-radius:8px;padding:14px;margin:10px 0">
<b>知識層狀態</b><pre>{html.escape(status)}</pre></div>
<div style="background:#161b22;border:1px solid #21262d;border-radius:8px;padding:14px;margin:10px 0">
<b>主題自動抓取</b>(輸入財經/化學…→展開域→觸發 harvest)
<form method=post action=/api/topic><input name=topic placeholder="財經" style="padding:8px;background:#0d1117;border:1px solid #30363d;color:#e6edf3;border-radius:6px">
<label style=font-size:13px><input type=checkbox name=run> 放量抓取(不勾=只看確認頁)</label>
<button style="padding:8px 14px;background:#1f6feb;color:#fff;border:0;border-radius:6px">送出</button></form></div>
<div style="background:#161b22;border:1px solid #21262d;border-radius:8px;padding:14px;margin:10px 0">
<b>+資料夾解析</b>(遞迴讀夾內任意副檔名、逐字入庫;路徑限 $HOME 下、須有公開授權之檔)
<form method=post action=/api/folder><input name=dir placeholder="~/docs" style="padding:8px;width:40%;background:#0d1117;border:1px solid #30363d;color:#e6edf3;border-radius:6px">
<select name=license style="padding:8px;background:#0d1117;color:#e6edf3;border:1px solid #30363d;border-radius:6px">
<option>public_domain</option><option>cc-by</option><option>cc-by-sa</option><option>cc0</option></select>
<button style="padding:8px 14px;background:#1f6feb;color:#fff;border:0;border-radius:6px">解析(private)</button></form></div>
<p><a href="http://localhost:8090" style=color:#3fb950>→ 開「誠實博學的我」對話(過 guard)</a></p></body>"""


def _status_text():
    try:
        with db.connect() as conn, db.transaction(conn) as cur:
            cur.execute("SELECT count(*) FROM knowledge_item")
            it = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM knowledge_item_text WHERE source_type='local_upload'")
            loc = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM knowledge_staging WHERE status='pending'")
            pend = cur.fetchone()[0]
        return f"knowledge_item={it:,}  本機檔 item_text={loc:,}  staging pending={pend:,}"
    except Exception as e:
        return f"(狀態查詢失敗:{e})"


class AdminHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _token(self):
        c = self.headers.get("Cookie", "")
        for kv in c.split(";"):
            if kv.strip().startswith("sid="):
                return kv.strip()[4:]
        return None

    def _send(self, code, body, ctype="text/html; charset=utf-8", cookie=None):
        raw = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(raw)))
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, *a):
        pass

    def do_GET(self):
        path = self.path.split("?")[0].rstrip("/") or "/"
        if path == "/logout":
            _SESSIONS.pop(self._token(), None)
            return self._send(200, LOGIN_HTML.format(msg="<p style=color:#7d8590>已登出</p>"),
                              cookie="sid=; Max-Age=0; Path=/")
        if not _valid(self._token()):
            return self._send(200, LOGIN_HTML.format(msg=""))
        if path == "/api/status":
            return self._send(200, json.dumps({"status": _status_text()}), "application/json")
        return self._send(200, dashboard_html(_status_text()))

    def do_POST(self):
        path = self.path.split("?")[0].rstrip("/")
        n = int(self.headers.get("Content-Length") or 0)
        form = parse_qs(self.rfile.read(n).decode("utf-8", "replace")) if n else {}
        g = lambda k: (form.get(k, [""])[0]).strip()

        if path == "/login":
            stored = os.environ.get("AUGUR_ADMIN_PASSWORD", "")
            if stored and verify_password(g("pw"), stored):
                tok = _new_session()
                _audit("login", "ok")
                return self._send(303, "", cookie=f"sid={tok}; HttpOnly; SameSite=Strict; Path=/",
                                  ctype="text/plain")  # 303 見下 Location
            _audit("login", "fail")
            return self._send(200, LOGIN_HTML.format(msg="<p style=color:#d29922>密碼錯誤</p>"))

        if not _valid(self._token()):
            return self._send(403, "未授權", ctype="text/plain")

        py = sys.executable
        if path == "/api/topic":
            topic = g("topic")[:40]
            run = g("run") == "on"
            _audit("topic", f"{topic} run={run}")
            cmd = [py, os.path.join(ROOT, "scripts", "acquire_topic.py"), "--topic", topic]
            if run:
                cmd += ["--run", "--batch", "10", "--rounds", "1"]   # 首輪最小 #25;放量另由 CLI
            out = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=60).stdout
            return self._send(200, f"<pre style='font-family:system-ui;background:#0d1117;color:#e6edf3;padding:20px'>"
                              f"{html.escape(out)}</pre><a href=/>← 返回</a>")

        if path == "/api/folder":
            safe = _safe_dir(g("dir"))
            lic = g("license")
            if not safe:
                _audit("folder", f"REJECT {g('dir')}")
                return self._send(400, "路徑非法(限 $HOME 下之現有資料夾、拒逃逸)", ctype="text/plain")
            if lic not in ("public_domain", "cc-by", "cc-by-sa", "cc0"):
                return self._send(400, "license 非白名單", ctype="text/plain")
            _audit("folder", f"{safe} license={lic}")
            cmd = [py, os.path.join(ROOT, "scripts", "acquire_local_files.py"),
                   "--dir", safe, "--license", lic, "--access-scope", "local_private", "--domain", "local"]
            out = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=300).stdout
            return self._send(200, f"<pre style='font-family:system-ui;background:#0d1117;color:#e6edf3;padding:20px'>"
                              f"{html.escape(out)}</pre><a href=/>← 返回</a>")

        return self._send(404, "unknown", ctype="text/plain")

    def send_response(self, code, *a):        # 303 需 Location
        super().send_response(code, *a)
        if code == 303:
            self.send_header("Location", "/")


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--serve", action="store_true")
    ap.add_argument("--set-password", action="store_true")
    ap.add_argument("--port", type=int, default=PORT)
    args, _ = ap.parse_known_args()

    if args.set_password:
        pw = getpass.getpass("設定 admin 密碼:")
        if pw != getpass.getpass("再輸入一次:"):
            sys.exit("兩次不符")
        print("\n將下列一行設為環境變數(勿進 git;可入 .env,#5):\n")
        print(f"AUGUR_ADMIN_PASSWORD='{hash_password(pw)}'")
        return
    if not args.serve:
        print(__doc__.split("執行指令矩陣:")[1])
        print(f"  操作值:port={args.port} 綁定=127.0.0.1(僅本機) 密碼設定={'✓' if os.environ.get('AUGUR_ADMIN_PASSWORD') else '✗ 未設(先 --set-password)'}")
        return
    if not os.environ.get("AUGUR_ADMIN_PASSWORD"):
        sys.exit("未設 AUGUR_ADMIN_PASSWORD;先 python scripts/serve_admin_console.py --set-password")
    srv = ThreadingHTTPServer(("127.0.0.1", args.port), AdminHandler)
    print(f"augur 知識控制台後台 http://127.0.0.1:{args.port}(僅本機;Ctrl-C 停;審計 {AUDIT_LOG})", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.server_close()


if __name__ == "__main__":
    main()
