#!/usr/bin/env python
"""augur 知識控制台 Admin 後台(P3,計畫 §四)— 登入認證 + 觸發主題抓/資料夾解析 + 狀態監看。

🎯 這支在做什麼(白話):admin 登入後,一頁觸發「主題自動抓」(P2 acquire_topic)、「資料夾解析」
   (P1 acquire_local_files)、看知識層狀態,並連到「誠實博學的我」對話(:8090)。資料夾選取三法並存:
   (A)**頁內瀏覽器**——點目錄樹瀏覽家目錄與 Windows 磁碟(/mnt/c…),選定即解析(引用伺服器路徑、不複製);
   (B)**原生上傳鈕**——webkitdirectory 彈作業系統資料夾視窗,上傳夾內檔案落暫存夾再餵同一入庫引擎;
   (C)打字輸入路徑(power user)。**只觸發既有本地 script、不重造管線、不繞 guard**;綁 127.0.0.1 僅本機。
安全(#5 OWASP):密碼 pbkdf2_hmac 雜湊(env AUGUR_ADMIN_PASSWORD,禁明文禁進 git;--set-password 產)、
   session token(secrets、HttpOnly+SameSite=Strict cookie、逾時)、常數時間比對、路徑 realpath 圍欄
   (限家目錄或 /mnt 下、拒 ../ 逃逸)、上傳大小上限+檔名去逃逸(防 zip bomb/traversal)、手寫 multipart(免 cgi)、
   subprocess 參數陣列 shell=False(防注入)、審計 log(誰/何時/何動作);license 仍受 DB CHECK 白名單硬擋。
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
from urllib.parse import parse_qs, urlparse

import _bootstrap  # noqa: F401
from augur.core import db, config
from augur.knowledge import webupload

PORT = 8500
SESSION_TTL = 3600          # session 秒數
_ITER = 240000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIT_LOG = os.path.join(os.path.expanduser("~"), "augur_chat_logs", "admin_audit.log")
MAX_UPLOAD = webupload.MAX_UPLOAD          # 單次上傳總量上限(SSOT=webupload)
_LICENSES = webupload.LICENSES             # DB CHECK 白名單(#1 版權硬擋;SSOT=webupload)
_SCOPES = webupload.SCOPES


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


def _browse_roots():
    """允許瀏覽/入庫之根:家目錄 + /mnt(Windows 磁碟);其餘系統目錄(/etc /usr…)不得觸及。"""
    home = os.path.realpath(os.path.expanduser("~"))
    return [home] + (["/mnt"] if os.path.isdir("/mnt") else [])


def _under_roots(rp):
    return any(rp == r or rp.startswith(r + os.sep) for r in _browse_roots())


def _safe_dir(path):
    """路徑圍欄:realpath 展開,須在允許根(家目錄/ /mnt)下(拒 ../ 逃逸);回 realpath 或 None。"""
    rp = os.path.realpath(os.path.expanduser(path or ""))
    return rp if (_under_roots(rp) and os.path.isdir(rp)) else None


def _root_list():
    """頁內瀏覽器起點按鈕:家目錄 + 各 Windows 磁碟(/mnt/單字母)。"""
    home = os.path.realpath(os.path.expanduser("~"))
    roots = [{"name": "家目錄 ~", "path": home}]
    try:
        for d in sorted(os.listdir("/mnt")):
            p = "/mnt/" + d
            if len(d) == 1 and d.isalpha() and os.path.isdir(p):
                roots.append({"name": f"Windows {d.upper()}:", "path": p})
    except OSError:
        pass
    return roots


def _list_dir(path):
    """頁內瀏覽器一層列目錄:回 {ok, path, parent, dirs[], file_count, samples[], roots[]}。符號連結不跟。"""
    home = os.path.realpath(os.path.expanduser("~"))
    rp = os.path.realpath(os.path.expanduser(path if path and path != "HOME" else home))
    if not (_under_roots(rp) and os.path.isdir(rp)):
        return {"ok": False, "error": "路徑非法或不在允許根(家目錄/ /mnt)", "roots": _root_list()}
    dirs, nfiles, samples = [], 0, []
    try:
        with os.scandir(rp) as it:
            for e in it:
                try:
                    if e.is_symlink():
                        continue                      # 不跟符號連結(防逃逸/迴圈)
                    if e.is_dir():
                        dirs.append({"name": e.name, "path": os.path.join(rp, e.name)})
                    elif e.is_file():
                        nfiles += 1
                        if len(samples) < 8:
                            samples.append(e.name)
                except OSError:
                    continue
    except (PermissionError, OSError):
        return {"ok": False, "error": "無讀取權限", "roots": _root_list()}
    dirs.sort(key=lambda d: d["name"].lower())
    parent = os.path.dirname(rp)
    parent = parent if (_under_roots(parent) and parent != rp) else None
    return {"ok": True, "path": rp, "parent": parent, "dirs": dirs,
            "file_count": nfiles, "samples": samples, "roots": _root_list()}


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

_LIC_OPTIONS = "".join(f"<option>{v}</option>" for v in _LICENSES)
_SCOPE_OPTIONS = "".join(f"<option>{v}</option>" for v in _SCOPES)

# 資料夾選取兩面板(A 頁內瀏覽器 / B 原生上傳)。純 stdlib、同源 fetch 帶 cookie;非 f-string(JS 大括號免跳脫)。
PANELS = ("""
<div style="background:#161b22;border:1px solid #21262d;border-radius:8px;padding:14px;margin:10px 0">
<b>A · 頁內瀏覽選取資料夾</b>(點資料夾進入,選定即解析;可瀏覽家目錄與 Windows 磁碟,引用路徑不複製)
<div id=rootbar style="margin:6px 0;display:flex;gap:6px;flex-wrap:wrap"></div>
<div id=bcrumb style="font-size:12px;color:#7d8590;margin:4px 0"></div>
<div id=dirlist style="max-height:220px;overflow:auto;border:1px solid #30363d;border-radius:6px;padding:6px;margin:4px 0"></div>
<div id=curinfo style="font-size:12px;color:#7d8590;margin:4px 0"></div>
<form method=post action=/api/folder onsubmit="return document.getElementById('seldir').value!=''">
<input type=hidden name=dir id=seldir>
<select name=license style="padding:8px;background:#0d1117;color:#e6edf3;border:1px solid #30363d;border-radius:6px">"""
+ _LIC_OPTIONS + """</select>
<select name=access_scope style="padding:8px;background:#0d1117;color:#e6edf3;border:1px solid #30363d;border-radius:6px">"""
+ _SCOPE_OPTIONS + """</select>
<button style="padding:8px 14px;background:#1f6feb;color:#fff;border:0;border-radius:6px">選此資料夾解析</button></form></div>

<div style="background:#161b22;border:1px solid #21262d;border-radius:8px;padding:14px;margin:10px 0">
<b>B · 原生視窗上傳資料夾</b>(按下彈作業系統選取視窗→上傳夾內檔案解析;抓瀏覽器所在機器之檔,大夾較重)
<div style="margin:6px 0"><input type=file id=upfiles webkitdirectory directory multiple
 style="color:#e6edf3"></div>
<select id=uplic style="padding:8px;background:#0d1117;color:#e6edf3;border:1px solid #30363d;border-radius:6px">"""
+ _LIC_OPTIONS + """</select>
<select id=upscope style="padding:8px;background:#0d1117;color:#e6edf3;border:1px solid #30363d;border-radius:6px">"""
+ _SCOPE_OPTIONS + """</select>
<button type=button onclick="doUpload()" style="padding:8px 14px;background:#1f6feb;color:#fff;border:0;border-radius:6px">上傳並解析</button>
<pre id=upresult style="white-space:pre-wrap;color:#7d8590;font-size:13px;margin-top:8px"></pre></div>

<script>
function _mk(tag,txt){var e=document.createElement(tag);if(txt!=null)e.textContent=txt;return e}
async function browse(p){
  var r=await fetch('/api/browse?path='+encodeURIComponent(p||'HOME'));var j=await r.json();
  var rb=document.getElementById('rootbar');
  if(!rb.dataset.done && j.roots){rb.dataset.done='1';
    j.roots.forEach(function(rt){var b=_mk('button',rt.name);b.type='button';
      b.style.cssText='padding:5px 10px;background:#21262d;color:#e6edf3;border:1px solid #30363d;border-radius:6px;cursor:pointer';
      b.onclick=function(){browse(rt.path)};rb.appendChild(b)})}
  var list=document.getElementById('dirlist');list.innerHTML='';
  if(!j.ok){list.appendChild(_mk('div','⚠ '+(j.error||'瀏覽失敗')));document.getElementById('seldir').value='';return}
  document.getElementById('seldir').value=j.path;
  document.getElementById('bcrumb').textContent='目前:'+j.path;
  document.getElementById('curinfo').textContent='此資料夾直屬檔案 '+j.file_count+' 個'+(j.samples&&j.samples.length?'(例:'+j.samples.join('、')+')':'')+' · 子資料夾 '+j.dirs.length+' 個';
  if(j.parent){var up=_mk('button','⬆ 上層');up.type='button';up.style.cssText='display:block;width:100%;text-align:left;padding:5px;background:transparent;color:#3fb950;border:0;cursor:pointer';up.onclick=function(){browse(j.parent)};list.appendChild(up)}
  j.dirs.forEach(function(d){var b=_mk('button','📁 '+d.name);b.type='button';
    b.style.cssText='display:block;width:100%;text-align:left;padding:5px;background:transparent;color:#e6edf3;border:0;cursor:pointer';
    b.onclick=function(){browse(d.path)};list.appendChild(b)});
  if(!j.dirs.length)list.appendChild(_mk('div','(無子資料夾;可直接選此資料夾解析)'))
}
async function doUpload(){
  var inp=document.getElementById('upfiles');
  if(!inp.files.length){alert('先選一個資料夾');return}
  var fd=new FormData();
  fd.append('license',document.getElementById('uplic').value);
  fd.append('access_scope',document.getElementById('upscope').value);
  for(var i=0;i<inp.files.length;i++){var f=inp.files[i];fd.append('file',f,f.webkitRelativePath||f.name)}
  var res=document.getElementById('upresult');res.textContent='上傳中…('+inp.files.length+' 檔,大夾請耐心)';
  try{var r=await fetch('/api/upload',{method:'POST',body:fd});res.textContent=await r.text()}
  catch(e){res.textContent='上傳失敗:'+e}
}
browse('HOME');
</script>
""")


def dashboard_html(status):
    return (f"""<!doctype html><meta charset=utf-8><title>augur 知識控制台</title>
<body style="font-family:system-ui;background:#0d1117;color:#e6edf3;max-width:720px;margin:30px auto">
<h2>augur 知識控制台 <a href=/logout style=font-size:13px>登出</a></h2>
<div style="background:#161b22;border:1px solid #21262d;border-radius:8px;padding:14px;margin:10px 0">
<b>知識層狀態</b><pre>{html.escape(status)}</pre></div>
<div style="background:#161b22;border:1px solid #21262d;border-radius:8px;padding:14px;margin:10px 0">
<b>主題自動抓取</b>(輸入財經/化學…→展開域→觸發 harvest)
<form method=post action=/api/topic><input name=topic placeholder="財經" style="padding:8px;background:#0d1117;border:1px solid #30363d;color:#e6edf3;border-radius:6px">
<label style=font-size:13px><input type=checkbox name=run> 放量抓取(不勾=只看確認頁)</label>
<button style="padding:8px 14px;background:#1f6feb;color:#fff;border:0;border-radius:6px">送出</button></form></div>"""
    + PANELS +
    f"""<div style="background:#161b22;border:1px solid #21262d;border-radius:8px;padding:14px;margin:10px 0">
<b>C · 打字輸入路徑解析</b>(power user;遞迴讀夾內任意副檔名、逐字入庫;路徑限家目錄或 /mnt 下)
<form method=post action=/api/folder><input name=dir placeholder="~/docs" style="padding:8px;width:40%;background:#0d1117;border:1px solid #30363d;color:#e6edf3;border-radius:6px">
<select name=license style="padding:8px;background:#0d1117;color:#e6edf3;border:1px solid #30363d;border-radius:6px">{_LIC_OPTIONS}</select>
<button style="padding:8px 14px;background:#1f6feb;color:#fff;border:0;border-radius:6px">解析(private)</button></form></div>
<p><a href="http://localhost:8090" style=color:#3fb950>→ 開「誠實博學的我」對話(過 guard)</a></p></body>""")


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
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        if path == "/logout":
            _SESSIONS.pop(self._token(), None)
            return self._send(200, LOGIN_HTML.format(msg="<p style=color:#7d8590>已登出</p>"),
                              cookie="sid=; Max-Age=0; Path=/")
        if not _valid(self._token()):
            return self._send(200, LOGIN_HTML.format(msg=""))
        if path == "/api/status":
            return self._send(200, json.dumps({"status": _status_text()}), "application/json")
        if path == "/api/browse":
            p = parse_qs(parsed.query).get("path", [""])[0]
            return self._send(200, json.dumps(_list_dir(p)), "application/json")
        return self._send(200, dashboard_html(_status_text()))

    def do_POST(self):
        path = self.path.split("?")[0].rstrip("/")
        py = sys.executable

        if path == "/login":
            n = int(self.headers.get("Content-Length") or 0)
            form = parse_qs(self.rfile.read(n).decode("utf-8", "replace")) if n else {}
            pw = (form.get("pw", [""])[0]).strip()
            stored = os.environ.get("AUGUR_ADMIN_PASSWORD", "")
            if stored and verify_password(pw, stored):
                tok = _new_session()
                _audit("login", "ok")
                return self._send(303, "", cookie=f"sid={tok}; HttpOnly; SameSite=Strict; Path=/",
                                  ctype="text/plain")  # 303 見下 Location
            _audit("login", "fail")
            return self._send(200, LOGIN_HTML.format(msg="<p style=color:#d29922>密碼錯誤</p>"))

        if not _valid(self._token()):
            return self._send(403, "未授權", ctype="text/plain")

        if path == "/api/upload":
            return self._handle_upload(py)

        # 表單類(urlencoded)
        n = int(self.headers.get("Content-Length") or 0)
        form = parse_qs(self.rfile.read(n).decode("utf-8", "replace")) if n else {}
        g = lambda k: (form.get(k, [""])[0]).strip()

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
            scope = g("access_scope") or "local_private"
            if not safe:
                _audit("folder", f"REJECT {g('dir')}")
                return self._send(400, "路徑非法(限家目錄/ /mnt 下之現有資料夾、拒逃逸)", ctype="text/plain")
            if lic not in _LICENSES:
                return self._send(400, "license 非白名單", ctype="text/plain")
            if scope not in _SCOPES:
                scope = "local_private"
            _audit("folder", f"{safe} license={lic} scope={scope}")
            cmd = [py, os.path.join(ROOT, "scripts", "acquire_local_files.py"),
                   "--dir", safe, "--license", lic, "--access-scope", scope, "--domain", "local"]
            out = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=300).stdout
            return self._send(200, f"<pre style='font-family:system-ui;background:#0d1117;color:#e6edf3;padding:20px'>"
                              f"{html.escape(out)}</pre><a href=/>← 返回</a>")

        return self._send(404, "unknown", ctype="text/plain")

    def _handle_upload(self, py):
        """B · 原生上傳:multipart 落暫存夾(webupload SSOT)→ 餵 acquire_local_files 同一入庫引擎。"""
        ctype = self.headers.get("Content-Type", "")
        n = int(self.headers.get("Content-Length") or 0)
        if "multipart/form-data" not in ctype or "boundary=" not in ctype:
            return self._send(400, "需 multipart/form-data", ctype="text/plain")
        if n > MAX_UPLOAD:
            return self._send(413, f"上傳過大(上限 {MAX_UPLOAD // 1024 // 1024}MB)", ctype="text/plain")
        boundary = ctype.split("boundary=", 1)[1].strip().strip('"')
        fields, files = webupload.parse_multipart(self.rfile.read(n), boundary)
        lic = (fields.get("license") or "").strip()
        scope = (fields.get("access_scope") or "local_private").strip()
        if lic not in _LICENSES:
            return self._send(400, "license 非白名單(DB 硬擋只准公開授權)", ctype="text/plain")
        if scope not in _SCOPES:
            scope = "local_private"
        if not files:
            return self._send(400, "無檔案(請選含檔案的資料夾)", ctype="text/plain")
        r = webupload.save_upload(files)
        _audit("upload", f"{r['updir']} saved={r['saved']} big={r['big']} bad={r['bad']} license={lic} scope={scope}")
        if not r["saved"]:
            return self._send(400, f"無有效檔案(過大跳 {r['big']}、非法名跳 {r['bad']})", ctype="text/plain")
        cmd = [py, os.path.join(ROOT, "scripts", "acquire_local_files.py"),
               "--dir", r["updir"], "--license", lic, "--access-scope", scope, "--domain", "local"]
        out = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=600).stdout
        head = (f"【原生上傳解析】暫存 {r['updir']}\n"
                f"存檔 {r['saved']}(過大跳 {r['big']}、非法名跳 {r['bad']})、license={lic} scope={scope}\n\n")
        return self._send(200, head + out, ctype="text/plain; charset=utf-8")

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
