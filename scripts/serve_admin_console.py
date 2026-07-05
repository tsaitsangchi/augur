#!/usr/bin/env python
"""augur 知識控制台 Admin 後台(P3,計畫 §四)— 登入認證 + 觸發主題抓/資料夾解析 + 狀態監看。

🎯 這支在做什麼(白話):admin 登入後,一頁觸發「主題自動抓」(P2 acquire_topic)、「資料夾解析」
   (P1 acquire_local_files)、看知識層狀態,並連到「誠實博學的我」對話(:8090)。資料夾選取三法並存:
   (A)**頁內瀏覽器**——點目錄樹瀏覽家目錄與 Windows 磁碟(/mnt/c…),選定即解析(引用伺服器路徑、不複製);
   (B)**原生上傳鈕**——webkitdirectory 彈作業系統資料夾視窗,上傳夾內檔案落暫存夾再餵同一入庫引擎;
   (C)打字輸入路徑(power user)。**只觸發既有本地 script、不重造管線、不繞 guard**;綁 127.0.0.1 僅本機。
登入(RBAC P1):**DB 群組使用者優先**(填帳號→`identity.authenticate` 查 `app_user` + pbkdf2 240k、
   session 落 `app_session`);**帳號留空＝env 緊急後門**(相容期,`AUGUR_ADMIN_PASSWORD`,防鎖死;計畫 §3.3/§3.6)。
   建帳號/群組/授權走 `scripts/manage_rbac_user.py`(DB 資料驅動、零改碼 #29)。
安全(#5 OWASP):pbkdf2_hmac 240k 雜湊(禁明文禁進 git)、session token(secrets、HttpOnly+SameSite=Strict cookie、
   DB 只存 sha256、fail-closed 每請求 gate)、常數時間比對、路徑 realpath 圍欄
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
from augur.knowledge import webupload, sftpbrowse, identity

PORT = 8500
SESSION_TTL = 3600          # session 秒數
_ITER = 240000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIT_LOG = os.path.join(os.path.expanduser("~"), "augur_chat_logs", "admin_audit.log")
LOG_DIR = os.path.dirname(AUDIT_LOG)       # harvest 背景 log 落此(與 audit 同目錄)
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
_JOBS = {}       # harvest logname -> pid(背景抓取存活判定;admin 重啟後改以 log 尾標記判定)

# harvest 完成標記(acquire_topic/harvest 之終行 sentinel;命中即進度頁標「完成」停輪詢)
_DONE_MARKS = ("harvest 觸發(抓入知識層", "無對應 domain", "排程空(全部已跑")


def _safe_log(name):
    """harvest 進度 log 圍欄:僅 harvest_<hex>.log 且存在於 LOG_DIR;回路徑或 None(#5 拒 traversal)。"""
    name = os.path.basename(name or "")
    if not (name.startswith("harvest_") and name.endswith(".log")):
        return None
    core = name[len("harvest_"):-4]
    if not core or any(c not in "0123456789abcdef" for c in core):
        return None
    fp = os.path.join(LOG_DIR, name)
    return fp if os.path.isfile(fp) else None


def _read_harvest_log(name):
    """回 {ok, log(尾 400 行), done, lines}:done=終行 sentinel 命中,或(pid 已知且進程已歿=崩潰亦收尾)。"""
    fp = _safe_log(name)
    if not fp:
        return {"ok": False, "error": "bad file"}
    try:
        with open(fp, "r", errors="replace") as f:
            data = f.read()
    except OSError:
        data = ""
    sentinel = any(m in data for m in _DONE_MARKS)
    pid = _JOBS.get(os.path.basename((name or "").strip()))
    alive = False
    if pid:
        try:
            os.kill(pid, 0)
            alive = True
        except OSError:
            alive = False
    lines = data.splitlines()
    return {"ok": True, "log": "\n".join(lines[-400:]),
            "done": bool(sentinel or (pid is not None and not alive)), "lines": len(lines)}


def _new_session():
    t = secrets.token_urlsafe(32)
    _SESSIONS[t] = time.time() + SESSION_TTL
    return t


def _valid(token):
    # DB 群組 session(identity/app_session、fail-closed)優先;env 緊急後門用記憶體 _SESSIONS(相容期)
    if token and identity.verify_session(token) is not None:
        return True
    exp = _SESSIONS.get(token)
    if exp and exp > time.time():
        return True
    _SESSIONS.pop(token, None)
    return False


LOGIN_HTML = """<!doctype html><html lang=zh-Hant><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1"><title>augur 知識控制台</title></head>
<body style="margin:0;font-family:ui-sans-serif,-apple-system,'Segoe UI','Noto Sans TC',sans-serif;background:#faf9f5;color:#1f1e1d;display:flex;min-height:100vh;align-items:center;justify-content:center">
<div style="width:360px;padding:38px 34px;background:#fff;border:1px solid #e9e6dc;border-radius:18px;box-shadow:0 6px 28px rgba(0,0,0,.05)">
<div style="color:#d97757;font-size:27px;text-align:center">✻</div>
<h2 style="margin:10px 0 3px;font-size:20px;text-align:center;font-weight:600">augur 知識控制台</h2>
<p style="color:#73726c;font-size:13px;margin:0 0 22px;text-align:center">知識層管理後台</p>{msg}
<form method=post action=/login><input name=username placeholder="帳號(留空＝env 緊急後門)" autofocus
 style="width:100%;padding:12px 14px;margin:6px 0;background:#faf9f5;border:1px solid #dcd8cc;color:#1f1e1d;border-radius:10px;font-size:15px">
<input type=password name=pw placeholder="密碼"
 style="width:100%;padding:12px 14px;margin:6px 0;background:#faf9f5;border:1px solid #dcd8cc;color:#1f1e1d;border-radius:10px;font-size:15px">
<button style="width:100%;padding:12px;margin-top:12px;background:#d97757;color:#fff;border:0;border-radius:10px;font-size:15px;cursor:pointer;font-weight:500">登入</button></form></div></body></html>"""

_LIC_OPTIONS = "".join(f"<option>{v}</option>" for v in _LICENSES)
_SCOPE_OPTIONS = "".join(f"<option>{v}</option>" for v in _SCOPES)

# 資料夾選取兩面板(A 頁內瀏覽器 / B 原生上傳)。純 stdlib、同源 fetch 帶 cookie;非 f-string(JS 大括號免跳脫)。
PANELS = ("""
<div class=card>
<b>選擇檔案或資料夾入庫</b>
<div style="font-size:13px;color:#73726c;margin-bottom:12px">點按鈕開啟檔案管理員選取(Windows 或 WSL 內的檔皆可),逐字入知識庫。license 受 DB CHECK 硬擋只准公開授權。</div>
<div style="margin-bottom:12px">授權 <select id=inlic style="padding:8px;background:#faf9f5;color:#1f1e1d;border:1px solid #dcd8cc;border-radius:6px">"""
+ _LIC_OPTIONS + """</select>
 範圍 <select id=inscope style="padding:8px;background:#faf9f5;color:#1f1e1d;border:1px solid #dcd8cc;border-radius:6px">"""
+ _SCOPE_OPTIONS + """</select></div>
<button type=button onclick="pick('file')" style="padding:9px 16px;background:#d97757;color:#fff;border:0;border-radius:8px;cursor:pointer;margin-right:8px">📄 選檔案</button>
<button type=button onclick="pick('folder')" style="padding:9px 16px;background:#d97757;color:#fff;border:0;border-radius:8px;cursor:pointer">📁 選資料夾</button>
<input type=file id=fpick style="display:none">
<input type=file id=dpick webkitdirectory directory multiple style="display:none">
<pre id=upresult style="white-space:pre-wrap;color:#73726c;font-size:13px;margin-top:12px"></pre>
</div>
<script>
function pick(kind){document.getElementById(kind=='folder'?'dpick':'fpick').click()}
document.getElementById('fpick').onchange=function(){doUpload(this.files);this.value=''}
document.getElementById('dpick').onchange=function(){doUpload(this.files);this.value=''}
async function doUpload(files){
 if(!files||!files.length)return
 var res=document.getElementById('upresult');res.textContent='上傳解析中…('+files.length+' 檔,大夾請耐心)'
 var fd=new FormData();fd.append('license',document.getElementById('inlic').value);fd.append('access_scope',document.getElementById('inscope').value)
 for(var i=0;i<files.length;i++){var f=files[i];fd.append('file',f,f.webkitRelativePath||f.name)}
 try{var r=await fetch('/api/upload',{method:'POST',body:fd});res.textContent=await r.text()}
 catch(e){res.textContent='上傳失敗:'+e}
}
</script>
""")

# D · 遠端 SFTP 瀏覽入庫面板（非 f-string：JS 大括號免跳脫）
SFTP_PANEL = ("""
<div style="background:#ffffff;border:1px solid #e9e6dc;border-radius:8px;padding:14px;margin:10px 0">
<b>D · 遠端 SFTP 瀏覽入庫</b>(SSH 金鑰;連線設定存 ~/.config/augur-sftp.json chmod 600、<b>不存密碼</b>)
<div style="margin:6px 0">連線 <select id=sconn style="padding:6px;background:#faf9f5;color:#1f1e1d;border:1px solid #dcd8cc;border-radius:6px"></select>
 <button type=button onclick="sbrowse('.')" style="padding:6px 10px;background:#e9e6dc;color:#1f1e1d;border:1px solid #dcd8cc;border-radius:6px;cursor:pointer">瀏覽</button>
 <button type=button onclick="var a=document.getElementById('saddc');a.style.display=(a.style.display=='block'?'none':'block')" style="padding:6px 10px;background:#e9e6dc;color:#1f1e1d;border:1px solid #dcd8cc;border-radius:6px;cursor:pointer">＋新增連線</button></div>
<div id=saddc style="display:none;margin:6px 0;font-size:13px">
 <input id=sname placeholder="名稱" style="padding:6px;width:90px;background:#faf9f5;color:#1f1e1d;border:1px solid #dcd8cc;border-radius:6px">
 <input id=shost placeholder="host" style="padding:6px;width:130px;background:#faf9f5;color:#1f1e1d;border:1px solid #dcd8cc;border-radius:6px">
 <input id=sport placeholder="22" value="22" style="padding:6px;width:52px;background:#faf9f5;color:#1f1e1d;border:1px solid #dcd8cc;border-radius:6px">
 <input id=suser placeholder="user" style="padding:6px;width:90px;background:#faf9f5;color:#1f1e1d;border:1px solid #dcd8cc;border-radius:6px">
 <input id=skey placeholder="~/.ssh/id_ed25519" style="padding:6px;width:170px;background:#faf9f5;color:#1f1e1d;border:1px solid #dcd8cc;border-radius:6px">
 <button type=button onclick="saveConn()" style="padding:6px 10px;background:#d97757;color:#fff;border:0;border-radius:6px;cursor:pointer">儲存連線</button></div>
<div id=sbcrumb style="font-size:12px;color:#73726c;margin:4px 0"></div>
<div id=sdirlist style="max-height:220px;overflow:auto;border:1px solid #dcd8cc;border-radius:6px;padding:6px;margin:4px 0"></div>
<div id=scurinfo style="font-size:12px;color:#73726c;margin:4px 0"></div>
<form method=post action=/api/sftp/ingest onsubmit="return document.getElementById('spath').value!=''">
<input type=hidden name=conn id=sconnh><input type=hidden name=path id=spath>
<select name=license style="padding:8px;background:#faf9f5;color:#1f1e1d;border:1px solid #dcd8cc;border-radius:6px">"""
+ _LIC_OPTIONS + """</select>
<select name=access_scope style="padding:8px;background:#faf9f5;color:#1f1e1d;border:1px solid #dcd8cc;border-radius:6px">"""
+ _SCOPE_OPTIONS + """</select>
<button style="padding:8px 14px;background:#d97757;color:#fff;border:0;border-radius:6px">選此遠端資料夾解析</button></form></div>
<script>
(async function(){try{var r=await fetch('/api/sftp/conns');var j=await r.json();var s=document.getElementById('sconn');(j.names||[]).forEach(function(n){var o=document.createElement('option');o.textContent=n;s.appendChild(o)})}catch(e){}})()
async function saveConn(){
 var fd=new URLSearchParams()
 fd.append('name',document.getElementById('sname').value);fd.append('host',document.getElementById('shost').value)
 fd.append('port',document.getElementById('sport').value);fd.append('user',document.getElementById('suser').value)
 fd.append('key_path',document.getElementById('skey').value)
 var r=await fetch('/api/sftp/save',{method:'POST',body:fd});var j=await r.json()
 if(j.ok){var s=document.getElementById('sconn');s.innerHTML='';(j.names||[]).forEach(function(n){var o=document.createElement('option');o.textContent=n;s.appendChild(o)});alert('已儲存連線')}else alert('儲存失敗:'+(j.error||''))
}
async function sbrowse(p){
 var conn=document.getElementById('sconn').value;if(!conn){alert('先選或新增連線');return}
 document.getElementById('sconnh').value=conn
 var list=document.getElementById('sdirlist');list.innerHTML='連線中…'
 var r=await fetch('/api/sftp/list?conn='+encodeURIComponent(conn)+'&path='+encodeURIComponent(p||'.'))
 var j=await r.json();list.innerHTML=''
 if(!j.ok){list.appendChild(document.createTextNode('⚠ '+(j.error||'瀏覽失敗')));document.getElementById('spath').value='';return}
 document.getElementById('spath').value=j.path;document.getElementById('sbcrumb').textContent='遠端:'+j.path
 document.getElementById('scurinfo').textContent='此資料夾檔案 '+j.file_count+' 個'+(j.samples&&j.samples.length?'(例:'+j.samples.join('、')+')':'')+' · 子夾 '+j.dirs.length
 if(j.parent){var up=document.createElement('button');up.type='button';up.textContent='⬆ 上層';up.style.cssText='display:block;width:100%;text-align:left;padding:5px;background:transparent;color:#5f8a5a;border:0;cursor:pointer';up.onclick=function(){sbrowse(j.parent)};list.appendChild(up)}
 j.dirs.forEach(function(d){var btn=document.createElement('button');btn.type='button';btn.textContent='📁 '+d.name;btn.style.cssText='display:block;width:100%;text-align:left;padding:5px;background:transparent;color:#1f1e1d;border:0;cursor:pointer';btn.onclick=function(){sbrowse(d.path)};list.appendChild(btn)})
 if(!j.dirs.length)list.appendChild(document.createTextNode('(無子資料夾;可直接選此資料夾解析)'))
}
</script>
""")


_PROGRESS_TMPL = """<!doctype html><meta charset=utf-8><title>抓取進度 · augur</title>
<body style="font-family:ui-sans-serif,-apple-system,'Segoe UI','Noto Sans TC',sans-serif;background:#faf9f5;color:#1f1e1d;max-width:900px;margin:24px auto;padding:0 16px">
<h3>財經抓取進度 — 主題「__TOPIC__」 <span id=stat style="color:#b5793a">● 執行中…</span></h3>
<div style="color:#73726c;font-size:13px;margin-bottom:8px">batch=__BATCH__ rounds=__ROUNDS__ · 背景執行(關閉此頁不中斷、resume-safe);限速/熔斷/續跑在引擎(#17/#22)。每 2 秒更新。</div>
<div style="margin-bottom:8px"><button id=copybtn onclick="copyLog()" style="padding:6px 12px;background:#fff;color:#1f1e1d;border:1px solid #dcd8cc;border-radius:8px;cursor:pointer;font-size:13px">複製全部</button>
 <span style="color:#73726c;font-size:12px;margin-left:8px">log 可直接選取複製;選取期間暫停自動刷新、不打斷選取</span></div>
<pre id=logbox style="background:#f0eee6;border:1px solid #e9e6dc;border-radius:8px;padding:14px;max-height:70vh;overflow:auto;white-space:pre-wrap;font-size:12.5px;user-select:text;-webkit-user-select:text;cursor:text">(等待引擎輸出…)</pre>
<a href=/ style="color:#5f8a5a">← 返回控制台</a>
<script>
var LF="__LOG__"
function hasSel(box){var s=window.getSelection();if(!s||s.isCollapsed||!s.rangeCount)return false;var n=s.getRangeAt(0).commonAncestorContainer;return box.contains(n.nodeType===1?n:n.parentNode)}
function copyLog(){var t=document.getElementById('logbox').textContent;var b=document.getElementById('copybtn');navigator.clipboard.writeText(t).then(function(){var o=b.textContent;b.textContent='已複製 ✓';setTimeout(function(){b.textContent=o},1500)},function(){b.textContent='複製失敗,請手動選取';setTimeout(function(){b.textContent='複製全部'},2000)})}
async function poll(){
 try{var r=await fetch('/api/topic/log?file='+encodeURIComponent(LF));var j=await r.json()
  if(j.ok){var box=document.getElementById('logbox')
   var nt=j.log||'(等待引擎輸出…)'
   if(nt!==box.textContent&&!hasSel(box)){var atBottom=box.scrollTop+box.clientHeight>=box.scrollHeight-40;box.textContent=nt;if(atBottom)box.scrollTop=box.scrollHeight}
   if(j.done){var s=document.getElementById('stat');s.textContent='✓ 完成(共 '+j.lines+' 行)';s.style.color='#5f8a5a';return}}
 }catch(e){}
 setTimeout(poll,2000)
}
poll()
</script></body>"""


def progress_view_html(topic, logname, batch, rounds):
    return (_PROGRESS_TMPL.replace("__TOPIC__", html.escape(topic)).replace("__LOG__", logname)
            .replace("__BATCH__", str(batch)).replace("__ROUNDS__", str(rounds)))


ADMIN_CSS = """
:root{color-scheme:light;--bg:#faf9f5;--sidebar:#f0eee6;--surface:#fff;--text:#1f1e1d;--muted:#73726c;--border:#e9e6dc;--border-strong:#dcd8cc;--accent:#d97757;--accent-hover:#c15f3f;--hover:#e7e4d8}
*{box-sizing:border-box}
body{margin:0;font-family:ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans TC",sans-serif;background:var(--bg);color:var(--text);font-size:14.5px;line-height:1.6;-webkit-font-smoothing:antialiased}
.app{display:flex;min-height:100vh}
.side{width:230px;flex-shrink:0;background:var(--sidebar);border-right:1px solid var(--border);padding:14px 10px;position:sticky;top:0;height:100vh;overflow:auto;display:flex;flex-direction:column}
.acct-box{margin-top:auto;display:flex;align-items:center;gap:9px;padding:10px 8px 4px;border-top:1px solid var(--border)}
.avatar{width:30px;height:30px;border-radius:50%;background:var(--accent);color:#fff;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:600;flex-shrink:0}
.acct{flex:1;min-width:0}
.acct-name{font-size:13px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.acct-sub{font-size:11px;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.brand{display:flex;align-items:center;gap:8px;font-weight:600;font-size:15px;padding:6px 10px 2px}
.brand .s{color:var(--accent);font-size:18px;line-height:1}
.brand small{display:block;color:var(--muted);font-weight:400;font-size:11px;margin:3px 0 0 26px}
.nav{display:flex;flex-direction:column;gap:2px;margin-top:14px}
.nav button,.nav a{display:block;text-align:left;width:100%;padding:9px 12px;border:0;border-radius:9px;background:transparent;color:#4a4842;font-size:14px;cursor:pointer;text-decoration:none;font-family:inherit}
.nav button:hover,.nav a:hover{background:var(--hover)}
.nav button.active{background:var(--surface);color:var(--text);font-weight:600;box-shadow:0 1px 3px rgba(0,0,0,.05)}
.nav .sep{border-top:1px solid var(--border);margin:10px 6px}
.main{flex:1;padding:30px 40px 60px;max-width:940px}
.sec{display:none}.sec.active{display:block;animation:fade .15s ease}
@keyframes fade{from{opacity:0}to{opacity:1}}
.sec>h1{font-size:22px;margin:0 0 4px;color:var(--text);font-weight:600;letter-spacing:-.01em}
.sec>.desc{color:var(--muted);font-size:13px;margin:0 0 18px}
.card{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:20px;margin:14px 0;box-shadow:0 1px 3px rgba(0,0,0,.03)}
.card>b{color:var(--text);display:block;margin-bottom:10px;font-size:14px;font-weight:600}
pre{white-space:pre-wrap;color:#4a4842;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12.5px;margin:0}
input,select,form button,textarea{font-family:inherit}
input,select{background:var(--bg);border:1px solid var(--border-strong);color:var(--text);border-radius:8px}
input:focus,select:focus{outline:0;border-color:var(--accent)}
.mdbody{line-height:1.7;max-height:72vh;overflow:auto;font-size:14px;color:#2c2b28}
.mdbody h2{font-size:19px;font-weight:600;margin:18px 0 8px}
.mdbody h3{font-size:16px;font-weight:600;margin:16px 0 6px}
.mdbody h4{font-size:14px;font-weight:600;margin:14px 0 6px;color:#4a4842}
.mdbody p{margin:0 0 11px}
.mdbody ul,.mdbody ol{margin:8px 0;padding-left:22px}.mdbody li{margin:4px 0}
.mdbody code{background:#f0eee6;border-radius:4px;padding:1px 5px;font-family:ui-monospace,Menlo,monospace;font-size:.88em}
.mdbody pre.cb{background:#2b2a27;color:#f0eee6;border-radius:8px;padding:12px 14px;overflow:auto;font-size:12.5px;line-height:1.5;white-space:pre}
.mdbody pre.cb code{background:none;padding:0;color:inherit}
.mdbody a{color:var(--accent)}.mdbody b{font-weight:600;color:#1f1e1d}
.mdbody blockquote{border-left:3px solid var(--border-strong);margin:8px 0;padding:2px 0 2px 14px;color:#6a6862}
.mdbody hr{border:0;border-top:1px solid var(--border);margin:16px 0}
.mdbody table.md{border-collapse:collapse;font-size:12.5px;margin:10px 0;width:100%}
.mdbody table.md th,.mdbody table.md td{border:1px solid var(--border-strong);padding:5px 9px;text-align:left;vertical-align:top}
.mdbody table.md th{background:#f0eee6;font-weight:600}
.nav button,.nav a,.card,.mdbody a{transition:background .12s,color .12s,border-color .12s}
button:focus-visible,input:focus-visible,select:focus-visible,.nav button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
"""

NAV_SCRIPT = """</section>
<section id=sec-jobs class=sec>
<h1>背景工作</h1><div class=desc>harvest 抓取工作(背景執行、resume-safe、關頁不中斷);點「檢視」看即時進度。</div>
<div class=card><b>工作清單</b><div id=joblist style="font-size:13px">載入中…</div></div>
</section>
<section id=sec-docs class=sec>
<h1>文件</h1><div class=desc>reports/ 與 docs/ 下的 .md(計畫、報告、治權)。點左側檔名檢視渲染內容。</div>
<div style="display:flex;gap:16px;align-items:flex-start">
<div style="width:270px;flex-shrink:0"><div id=doclist style="font-size:13px">載入中…</div></div>
<div style="flex:1;min-width:0"><div id=docview class=card style="min-height:340px">← 選左側文件檢視</div></div>
</div>
</section>
</main></div>
<script>
function nav(btn,id){document.querySelectorAll('.sec').forEach(function(s){s.classList.remove('active')});document.getElementById('sec-'+id).classList.add('active');document.querySelectorAll('.nav button').forEach(function(b){b.classList.remove('active')});btn.classList.add('active')}
function dot(ok){var s=document.createElement('span');s.style.cssText='display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:7px;background:'+(ok?'#5f8a5a':'#c15f3f');return s}
async function loadHealth(){var el=document.getElementById('health');try{var j=await (await fetch('/api/health')).json();el.textContent='';[['PostgreSQL',j.db],['顧問殼 :8399',j.advisor],['Ollama :11434',j.ollama]].forEach(function(p,ix){el.appendChild(dot(p[1]));el.appendChild(document.createTextNode(p[0]+(ix<2?'　　':'')))})}catch(e){el.textContent='健康檢查失敗'}}
async function loadJobs(){var el=document.getElementById('joblist');el.textContent='載入中…';try{var j=await (await fetch('/api/jobs')).json();var js=j.jobs||[];if(!js.length){el.textContent='(目前無背景工作)';return}el.innerHTML='';js.forEach(function(x){var row=document.createElement('div');row.style.cssText='display:flex;align-items:center;gap:10px;padding:9px 0;border-bottom:1px solid #e9e6dc';var b=document.createElement('span');b.textContent=x.running?'● 執行中':'✓ 完成';b.style.cssText='font-size:11px;padding:2px 9px;border-radius:20px;white-space:nowrap;background:'+(x.running?'#f5e5dd':'#e7ead9')+';color:'+(x.running?'#8a4a30':'#3b6d11');var nm=document.createElement('span');nm.textContent=x.name;nm.style.cssText='flex:1;font-family:ui-monospace,monospace;font-size:12px;word-break:break-all';var ln=document.createElement('span');ln.textContent=x.lines+' 行';ln.style.cssText='color:#73726c;font-size:12px;white-space:nowrap';var a=document.createElement('a');a.textContent='檢視 ↗';a.href='/progress?file='+encodeURIComponent(x.name);a.target='_blank';a.style.cssText='color:#d97757;font-size:12px;white-space:nowrap';row.appendChild(b);row.appendChild(nm);row.appendChild(ln);row.appendChild(a);el.appendChild(row)})}catch(e){el.textContent='載入失敗'}}
async function loadDocs(){var el=document.getElementById('doclist');el.textContent='載入中…';try{var j=await (await fetch('/api/docs')).json();var ds=j.docs||[];if(!ds.length){el.textContent='(無 .md)';return}el.innerHTML='';var cur='';ds.forEach(function(d){if(d.dir!=cur){cur=d.dir;var h=document.createElement('div');h.textContent=d.dir+'/';h.style.cssText='font-size:11px;color:#73726c;margin:12px 0 4px;text-transform:uppercase';el.appendChild(h)}var it=document.createElement('div');it.textContent=d.name;it.style.cssText='padding:7px 9px;border-radius:8px;cursor:pointer;color:#4a4842;word-break:break-all;font-size:13px';it.onmouseover=function(){if(!it.dataset.sel)it.style.background='#f0eee6'};it.onmouseout=function(){if(!it.dataset.sel)it.style.background=''};it.onclick=function(){viewDoc(it,d.path)};el.appendChild(it)})}catch(e){el.textContent='載入失敗'}}
async function viewDoc(node,p){document.querySelectorAll('#doclist div[data-sel]').forEach(function(n){n.removeAttribute('data-sel');n.style.background=''});node.dataset.sel='1';node.style.background='#e7e4d8';var v=document.getElementById('docview');v.textContent='載入中…';try{var j=await (await fetch('/api/doc?path='+encodeURIComponent(p))).json();if(!j.ok){v.textContent=j.error||'載入失敗';return}v.className='card mdbody';v.innerHTML=j.html}catch(e){v.textContent='載入失敗'}}
loadHealth();
</script></body></html>"""


def dashboard_html(status, uname="admin", role=""):
    return (f"""<!doctype html><html lang=zh-Hant><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>augur 知識控制台</title><style>{ADMIN_CSS}</style></head><body>
<div class=app>
<aside class=side>
<div class=brand><span class=s>✻</span>augur 控制台</div><small style="display:block;color:#73726c;font-size:11px;margin:2px 0 0 26px">知識層管理</small>
<nav class=nav>
<button class=active onclick="nav(this,'overview')">總覽</button>
<button onclick="nav(this,'jobs');loadJobs()">背景工作</button>
<button onclick="nav(this,'docs');loadDocs()">文件</button>
<div class=sep></div>
<button onclick="nav(this,'harvest')">主題抓取</button>
<button onclick="nav(this,'local')">本機匯入</button>
<button onclick="nav(this,'remote')">遠端 SFTP</button>
<div class=sep></div>
<a href="http://localhost:8090" target=_blank>誠實博學的我 ↗</a>
<a href=/logout>登出</a>
</nav>
<div class=acct-box>
<div class=avatar>{html.escape((uname[:1] or 'A').upper())}</div>
<div class=acct><div class=acct-name>{html.escape(uname)}</div><div class=acct-sub>{html.escape(role)}</div></div>
</div>
</aside>
<main class=main>
<section id=sec-overview class="sec active">
<h1>總覽</h1><div class=desc>知識層狀態與服務健康</div>
<div class=card><b>服務 running 狀態</b><div id=health style="font-size:13.5px;color:#73726c">檢查中…</div></div>
<div class=card><b>知識層狀態</b><pre>{html.escape(status)}</pre></div>
</section>
<section id=sec-harvest class=sec>
<h1>主題抓取</h1><div class=desc>輸入主題（財經/化學…）→ 展開 registry 域 → 觸發 harvest。放量＝背景執行 + 即時進度頁。</div>
<div class=card>
<form method=post action=/api/topic><input name=topic placeholder="財經" style="padding:8px;background:#faf9f5;border:1px solid #dcd8cc;color:#1f1e1d;border-radius:6px">
batch <input name=batch value=10 type=number min=1 max=2000 style="width:72px;padding:8px;background:#faf9f5;border:1px solid #dcd8cc;color:#1f1e1d;border-radius:6px">
rounds <input name=rounds value=1 type=number min=1 max=20 style="width:60px;padding:8px;background:#faf9f5;border:1px solid #dcd8cc;color:#1f1e1d;border-radius:6px">
<label style=font-size:13px><input type=checkbox name=run> 放量抓取(不勾=只看確認頁)</label>
<button style="padding:8px 14px;background:#d97757;color:#fff;border:0;border-radius:6px">送出</button></form>
<div style="font-size:12px;color:#73726c;margin-top:8px">首次建議 batch 10/rounds 1 小量探(#25);IP 健康再放大。放量後開即時進度頁(每 2 秒更新),關頁不中斷。</div>
</div>
</section>
<section id=sec-local class=sec>
<h1>本機匯入</h1><div class=desc>把本機或已掛載(/mnt、SSHFS)的資料夾/檔案逐字入知識庫。license 受 DB CHECK 硬擋只准公開授權。</div>"""
    + PANELS +
    f"""</section>
<section id=sec-remote class=sec>
<h1>遠端 SFTP</h1><div class=desc>用 SSH 金鑰連遠端主機、瀏覽目錄樹、下載選定資料夾入庫。連線設定存 config（不存密碼）。</div>"""
    + SFTP_PANEL + NAV_SCRIPT)


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


def _list_jobs():
    """背景工作清單:掃 LOG_DIR 之 harvest_*.log,回 [{name,mtime,size,done,lines,running}](新→舊)。"""
    jobs = []
    try:
        for fn in os.listdir(LOG_DIR):
            if fn.startswith("harvest_") and fn.endswith(".log"):
                try:
                    st = os.stat(os.path.join(LOG_DIR, fn))
                except OSError:
                    continue
                r = _read_harvest_log(fn)
                done = r.get("done", True)
                jobs.append({"name": fn, "mtime": int(st.st_mtime), "size": st.st_size,
                             "done": done, "running": not done, "lines": r.get("lines", 0)})
    except OSError:
        pass
    jobs.sort(key=lambda j: -j["mtime"])
    return jobs


_DOC_DIRS = ("reports", "docs")


def _list_docs():
    """文件清單:reports/ ＋ docs/ 下之 *.md,回 [{path,name,dir,size,mtime}](依目錄、名稱)。"""
    out = []
    for d in _DOC_DIRS:
        base = os.path.join(ROOT, d)
        if not os.path.isdir(base):
            continue
        try:
            names = sorted(os.listdir(base))
        except OSError:
            continue
        for fn in names:
            if fn.endswith(".md"):
                try:
                    st = os.stat(os.path.join(base, fn))
                except OSError:
                    continue
                out.append({"path": f"{d}/{fn}", "name": fn, "dir": d,
                            "size": st.st_size, "mtime": int(st.st_mtime)})
    return out


def _read_doc(rel):
    """守衛讀 .md:realpath 須在 ROOT/reports 或 ROOT/docs 下、副檔 .md(#5 拒 traversal);回內容或 None。"""
    if not rel or not rel.endswith(".md"):
        return None
    rp = os.path.realpath(os.path.join(ROOT, rel))
    allowed = [os.path.realpath(os.path.join(ROOT, d)) for d in _DOC_DIRS]
    if not any(rp == a or rp.startswith(a + os.sep) for a in allowed) or not os.path.isfile(rp):
        return None
    try:
        with open(rp, "r", errors="replace") as f:
            return f.read()
    except OSError:
        return None


def _md_to_html(text):
    """精簡 Markdown → HTML(伺服器端、行導向;支援標題/粗體/行內碼/圍欄碼/清單/表格/引言/連結)。
    先 html.escape 全文(防 XSS)再結構化;僅供後台 admin 檢視 reports/docs .md(#5)。"""
    import re
    lines = html.escape(text).split("\n")
    out, i, n = [], 0, 0
    n = len(lines)

    def inline(s):
        s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
        s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)
        s = re.sub(r"\[([^\]]+)\]\((https?:[^)\s]+)\)", r"<a href='\2' target=_blank rel=noopener>\1</a>", s)
        return s

    while i < n:
        line = lines[i]
        if line.startswith("```"):
            buf = []; i += 1
            while i < n and not lines[i].startswith("```"):
                buf.append(lines[i]); i += 1
            i += 1
            out.append("<pre class=cb>" + "\n".join(buf) + "</pre>"); continue
        m = re.match(r"(#{1,6})\s+(.*)", line)
        if m:
            lvl = min(len(m.group(1)) + 1, 4)
            out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>"); i += 1; continue
        if "|" in line and i + 1 < n and "-" in lines[i + 1] and re.match(r"^\s*\|?[\s:|-]+\|?\s*$", lines[i + 1]):
            hdr = [c.strip() for c in line.strip().strip("|").split("|")]
            i += 2; rows = []
            while i < n and "|" in lines[i] and lines[i].strip():
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i += 1
            th = "".join(f"<th>{inline(c)}</th>" for c in hdr)
            tr = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows)
            out.append(f"<table class=md><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>"); continue
        if re.match(r"^\s*[-*]\s+", line):
            items = []
            while i < n and re.match(r"^\s*[-*]\s+", lines[i]):
                items.append("<li>" + inline(re.sub(r"^\s*[-*]\s+", "", lines[i])) + "</li>"); i += 1
            out.append("<ul>" + "".join(items) + "</ul>"); continue
        if re.match(r"^\s*\d+\.\s+", line):
            items = []
            while i < n and re.match(r"^\s*\d+\.\s+", lines[i]):
                items.append("<li>" + inline(re.sub(r"^\s*\d+\.\s+", "", lines[i])) + "</li>"); i += 1
            out.append("<ol>" + "".join(items) + "</ol>"); continue
        if line.startswith("&gt;"):
            out.append("<blockquote>" + inline(re.sub(r"^&gt;\s?", "", line)) + "</blockquote>"); i += 1; continue
        if re.match(r"^\s*(-{3,}|\*{3,})\s*$", line):
            out.append("<hr>"); i += 1; continue
        if not line.strip():
            i += 1; continue
        buf = [line]; i += 1
        while i < n and lines[i].strip() and "|" not in lines[i] and not re.match(r"^(#{1,6}\s|```|\s*[-*]\s|\s*\d+\.\s|&gt;)", lines[i]):
            buf.append(lines[i]); i += 1
        out.append("<p>" + "<br>".join(inline(b) for b in buf) + "</p>")
    return "\n".join(out)


def _health():
    """服務 running 狀態:DB / advisor 殼(:8399) / Ollama(:11434) 可達性(各 1.5s timeout)。"""
    import urllib.request
    h = {"db": False, "advisor": False, "ollama": False}
    try:
        with db.connect() as conn, db.transaction(conn) as cur:
            cur.execute("SELECT 1")
            h["db"] = bool(cur.fetchone())
    except Exception:
        pass
    ollama_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/") + "/api/tags"
    for key, url in (("advisor", "http://127.0.0.1:8399/v1/models"), ("ollama", ollama_url)):
        try:
            urllib.request.urlopen(url, timeout=1.5)
            h[key] = True
        except Exception:
            pass
    return h


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
            tok = self._token()
            identity.revoke_session(tok)          # 撤 DB session
            _SESSIONS.pop(tok, None)              # 撤記憶體(env)session
            return self._send(200, LOGIN_HTML.format(msg="<p style=color:#73726c>已登出</p>"),
                              cookie="sid=; Max-Age=0; Path=/")
        if not _valid(self._token()):
            return self._send(200, LOGIN_HTML.format(msg=""))
        if path == "/api/status":
            return self._send(200, json.dumps({"status": _status_text()}), "application/json")
        if path == "/api/browse":
            p = parse_qs(parsed.query).get("path", [""])[0]
            return self._send(200, json.dumps(_list_dir(p)), "application/json")
        if path == "/api/topic/log":
            name = parse_qs(parsed.query).get("file", [""])[0]
            return self._send(200, json.dumps(_read_harvest_log(name)), "application/json")
        if path == "/api/sftp/conns":
            return self._send(200, json.dumps({"names": sftpbrowse.connection_names()}), "application/json")
        if path == "/api/sftp/list":
            qp = parse_qs(parsed.query)
            return self._send(200, json.dumps(sftpbrowse.list_dir(qp.get("conn", [""])[0], qp.get("path", ["."])[0])),
                              "application/json")
        if path == "/api/health":
            return self._send(200, json.dumps(_health()), "application/json")
        if path == "/api/jobs":
            return self._send(200, json.dumps({"jobs": _list_jobs()}), "application/json")
        if path == "/progress":
            logname = parse_qs(parsed.query).get("file", [""])[0]
            if _safe_log(logname):        # 既有背景工作之進度頁(log 可選取複製,§背景工作)
                return self._send(200, progress_view_html("背景工作", logname, "?", "?"))
            return self._send(404, "bad file", ctype="text/plain")
        if path == "/api/docs":
            return self._send(200, json.dumps({"docs": _list_docs()}), "application/json")
        if path == "/api/doc":
            rel = parse_qs(parsed.query).get("path", [""])[0]
            txt = _read_doc(rel)
            if txt is None:
                return self._send(404, json.dumps({"ok": False, "error": "檔案不存在或非法路徑"}), "application/json")
            return self._send(200, json.dumps({"ok": True, "path": rel, "html": _md_to_html(txt)}), "application/json")
        uname, role = self._acct()
        return self._send(200, dashboard_html(_status_text(), uname, role))

    def _acct(self):
        """左下角帳號區:DB session→(username, role);env 緊急後門→('admin','env 後門')。"""
        uid = identity.verify_session(self._token())
        if uid is not None:
            try:
                with db.connect() as conn, db.transaction(conn) as cur:
                    cur.execute("SELECT username, is_superuser FROM app_user WHERE user_id=%s", (uid,))
                    r = cur.fetchone()
                    if r:
                        return (r[0], "superuser" if r[1] else "群組使用者")
            except Exception:
                pass
        return ("admin", "env 後門")

    def do_POST(self):
        path = self.path.split("?")[0].rstrip("/")
        py = sys.executable

        if path == "/login":
            n = int(self.headers.get("Content-Length") or 0)
            form = parse_qs(self.rfile.read(n).decode("utf-8", "replace")) if n else {}
            pw = form.get("pw", [""])[0]
            username = (form.get("username", [""])[0]).strip()
            if username:                          # DB 群組使用者(app_user)優先
                u = identity.authenticate(username, pw)
                if u:
                    tok = identity.issue_session(u["user_id"], client_note="admin")
                    _audit("login", f"ok user={username} super={u['is_superuser']}")
                    return self._send(303, "", cookie=f"sid={tok}; HttpOnly; SameSite=Strict; Path=/",
                                      ctype="text/plain")
                _audit("login", f"fail user={username}")
                return self._send(200, LOGIN_HTML.format(msg="<p style=color:#b5793a>帳號或密碼錯誤</p>"))
            # 帳號留空 ＝ env 緊急後門(相容期;計畫 §3.3/§3.6)——臨時 superuser 等效、記憶體 session
            stored = os.environ.get("AUGUR_ADMIN_PASSWORD", "")
            if stored and verify_password(pw.strip(), stored):
                tok = _new_session()
                _audit("login", "ok emergency(env)")
                return self._send(303, "", cookie=f"sid={tok}; HttpOnly; SameSite=Strict; Path=/",
                                  ctype="text/plain")
            _audit("login", "fail")
            return self._send(200, LOGIN_HTML.format(msg="<p style=color:#b5793a>帳號或密碼錯誤</p>"))

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
            if g("run") != "on":
                # 確認頁(不放量):短跑印域映射(唯讀、不打抓取 API)
                cmd = [py, os.path.join(ROOT, "scripts", "acquire_topic.py"), "--topic", topic]
                out = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=60).stdout
                _audit("topic", f"{topic} confirm")
                return self._send(200, f"<pre style='font-family:system-ui;background:#faf9f5;color:#1f1e1d;padding:20px'>"
                                  f"{html.escape(out)}</pre><a href=/>← 返回</a>")
            # 放量:背景 detached(start_new_session=關頁/請求逾時/admin 重啟不中斷)→ logfile 即時進度(#21/#22)
            try:
                batch = max(1, min(2000, int(g("batch") or 10)))
                rounds = max(1, min(20, int(g("rounds") or 1)))
            except ValueError:
                batch, rounds = 10, 1
            logname = f"harvest_{secrets.token_hex(6)}.log"
            os.makedirs(LOG_DIR, exist_ok=True)
            cmd = [py, "-u", os.path.join(ROOT, "scripts", "acquire_topic.py"),   # -u=acquire_topic 不緩衝(進度即時)
                   "--topic", topic, "--run", "--batch", str(batch), "--rounds", str(rounds)]
            _audit("topic_run", f"{topic} batch={batch} rounds={rounds} log={logname}")
            lf = open(os.path.join(LOG_DIR, logname), "w")
            try:
                proc = subprocess.Popen(cmd, cwd=ROOT, stdout=lf, stderr=subprocess.STDOUT,
                                        stdin=subprocess.DEVNULL, start_new_session=True)
                _JOBS[logname] = proc.pid
            finally:
                lf.close()
            return self._send(200, progress_view_html(topic, logname, batch, rounds))

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
            return self._send(200, f"<pre style='font-family:system-ui;background:#faf9f5;color:#1f1e1d;padding:20px'>"
                              f"{html.escape(out)}</pre><a href=/>← 返回</a>")

        if path == "/api/sftp/save":
            try:
                names = sftpbrowse.save_connection(g("name"), g("host"), g("port"), g("user"), g("key_path"))
                return self._send(200, json.dumps({"ok": True, "names": names}), "application/json")
            except Exception as e:
                return self._send(200, json.dumps({"ok": False, "error": str(e)}), "application/json")

        if path == "/api/sftp/ingest":
            conn, rpath, lic = g("conn"), g("path"), g("license")
            scope = g("access_scope") or "local_private"
            if lic not in _LICENSES:
                return self._send(400, "license 非白名單", ctype="text/plain")
            if scope not in _SCOPES:
                scope = "local_private"
            if not (conn and rpath):
                return self._send(400, "缺 conn/path", ctype="text/plain")
            pre = "<pre style='font-family:system-ui;background:#faf9f5;color:#1f1e1d;padding:20px'>"
            try:
                updir, st = sftpbrowse.fetch_to_upload(conn, rpath)
            except Exception as e:
                return self._send(200, f"{pre}SFTP 下載失敗:{html.escape(str(e))}</pre><a href=/>← 返回</a>")
            _audit("sftp_ingest", f"{conn}:{rpath} saved={st['saved']} license={lic} scope={scope}")
            if not st["saved"]:
                return self._send(200, f"{pre}遠端無可下載檔(過大跳 {st['skipped_big']})</pre><a href=/>← 返回</a>")
            cmd = [py, os.path.join(ROOT, "scripts", "acquire_local_files.py"),
                   "--dir", updir, "--license", lic, "--access-scope", scope, "--domain", "local"]
            out = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=600).stdout
            head = (f"【SFTP 下載+解析】{conn}:{rpath}\n下載 {st['saved']} 檔"
                    f"(過大跳 {st['skipped_big']}{'、截斷' if st['truncated'] else ''})、license={lic} scope={scope}\n\n")
            return self._send(200, f"{pre}{html.escape(head + out)}</pre><a href=/>← 返回</a>")

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
