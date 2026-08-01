#!/usr/bin/env python
"""augur 知識控制台 Admin 後台(P3,計畫 §四)— 登入認證 + 觸發主題抓/資料夾解析 + 狀態監看。

🎯 這支在做什麼(白話):admin 登入後,一頁觸發「主題自動抓」(P2 acquire_topic)、「資料夾解析」
   (P1 acquire_local_files)、看知識層狀態,並連到「誠實博學的我」對話(:8090)。資料夾選取三法並存:
   (A)**頁內瀏覽器**——點目錄樹瀏覽家目錄與 Windows 磁碟(/mnt/c…),選定即解析(引用伺服器路徑、不複製);
   (B)**原生上傳鈕**——webkitdirectory 彈作業系統資料夾視窗,上傳夾內檔案落暫存夾再餵同一入庫引擎;
   (C)打字輸入路徑(power user)。**只觸發既有本地 script、不重造管線、不繞 guard**;綁 127.0.0.1 僅本機。
登入兩路:**(1) env 帳密後門**——帳號留空、或帳號等於 `AUGUR_ADMIN_USER` → 比對 `AUGUR_ADMIN_PASSWORD`
   (**支援 .env 明文**〔本機取捨,與 .env 其餘明文祕密一致〕**或** `pbkdf2$...` 雜湊;臨時 superuser、記憶體 session)。
   **(2) DB 群組使用者**——填其他帳號→`identity.authenticate` 查 `app_user` + pbkdf2 240k、session 落 `app_session`;
   建帳號/群組/授權走 `scripts/manage_rbac_user.py`(DB 資料驅動、零改碼 #29)。
安全(#5 OWASP):env 後門明文限本機(綁 127.0.0.1、.env gitignored)、DB 使用者 pbkdf2_hmac 240k 雜湊、session token(secrets、HttpOnly+SameSite=Strict cookie、
   DB 只存 sha256、fail-closed 每請求 gate)、常數時間比對、路徑 realpath 圍欄
   (限家目錄或 /mnt 下、拒 ../ 逃逸)、上傳大小上限+檔名去逃逸(防 zip bomb/traversal)、手寫 multipart(免 cgi)、
   subprocess 參數陣列 shell=False(防注入)、審計 log(誰/何時/何動作);license 仍受 DB CHECK 白名單硬擋。
守 #5(OWASP)· #28(觸發本地引擎零 Claude usage)· #29 · 計畫 §四(admin 操作面、既有管線之 UI)。

執行指令矩陣:
  # .env 設明文帳密(最簡):AUGUR_ADMIN_USER=admin / AUGUR_ADMIN_PASSWORD=你的密碼(明文即可)
  python scripts/serve_admin_console.py --set-password        # (選)互動產 pbkdf2 雜湊 → 印 env 該設之 AUGUR_ADMIN_PASSWORD
  python scripts/serve_admin_console.py --serve               # 起後台(127.0.0.1:8500;帳密取 env)
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


def _admin_pw_ok(pw, stored):
    """env 後門密碼比對:`pbkdf2$` 開頭走雜湊驗證;否則當 .env 明文、常數時間比對。
    明文為本機後台(綁 127.0.0.1、單一 superuser、.env gitignored)之刻意取捨——與 .env 其餘明文祕密一致(#5)。"""
    if stored.startswith("pbkdf2$"):
        return verify_password(pw, stored)
    return hmac.compare_digest(pw, stored)


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
_JOBS_START = {}  # harvest logname -> 啟動 epoch 秒(進度頁即時計時;same-session 準,重啟後 None fallback)
_UPLOAD_JOBS = {}  # job_id -> {updir, license, scope, total, uploaded, big, bad, phase, logname, pid, t0}

# harvest 完成標記(acquire_topic/harvest 之終行 sentinel;命中即進度頁標「完成」停輪詢)
_DONE_MARKS = ("harvest 觸發(抓入知識層", "無對應 domain", "排程空(全部已跑")
_LOCAL_IMPORT_DONE = "[local_import_done]"


def _upload_job(job_id):
    """取分批上傳 job;job_id 須為 16 hex(#5)。"""
    jid = (job_id or "").strip()
    if len(jid) != 16 or any(c not in "0123456789abcdef" for c in jid):
        return None, None
    job = _UPLOAD_JOBS.get(jid)
    return (jid, job) if job else (None, None)


def _parse_local_import_log(text):
    """從 acquire_local_files 進度 log 抽 {k,n,file,status,ok_n,...,kip_*,done}。"""
    k = n = 0
    cur_file = cur_status = ""
    ok_n = dup_n = short_n = skip_n = fail_n = 0
    summary_lines = []
    kip_status = kip_run_id = ""
    for line in (text or "").splitlines():
        if line.startswith("[progress] "):
            rest = line[len("[progress] "):]
            # 0/541 phase=scan 或 12/541 file=a.txt status=ok
            head, _, tail = rest.partition(" ")
            if "/" in head:
                a, _, b = head.partition("/")
                try:
                    k, n = int(a), int(b)
                except ValueError:
                    pass
            cur_file = cur_status = ""
            for tok in tail.split():
                if tok.startswith("file="):
                    cur_file = tok[5:]
                elif tok.startswith("status="):
                    cur_status = tok[7:]
            if cur_status == "ok":
                ok_n += 1
            elif cur_status == "dup":
                dup_n += 1
            elif cur_status == "short":
                short_n += 1
            elif cur_status.startswith("skip:"):
                skip_n += 1
            elif cur_status:  # 非空且非上述 → 計失敗(勿把 phase=scan 無 status 算入)
                fail_n += 1
        elif line.startswith("[kip_done]") or line.startswith("[kip_skip]"):
            summary_lines.append(line)
            for tok in line.split():
                if tok.startswith("status="):
                    kip_status = tok[7:]
                elif tok.startswith("kip_run_id="):
                    kip_run_id = tok[11:]
        elif line.startswith("[kip_start]") or line.startswith("[kip_warn]"):
            summary_lines.append(line)
        elif line.startswith("[local_import_done]"):
            pass
        elif line.startswith("掃描 ") or line.startswith("[dry-run] 掃描 ") or line.startswith("  "):
            summary_lines.append(line)
        elif line.startswith("須 ") or "admission" in line.lower() or line.startswith("非資料夾"):
            summary_lines.append(line)
    done = _LOCAL_IMPORT_DONE in (text or "")
    summary = "\n".join(summary_lines).strip()
    return {"k": k, "n": n, "file": cur_file, "status": cur_status,
            "ok_n": ok_n, "dup_n": dup_n, "short_n": short_n, "skip_n": skip_n, "fail_n": fail_n,
            "kip_status": kip_status, "kip_run_id": kip_run_id,
            "summary": summary, "done_mark": done}


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
    done = bool(sentinel or (pid is not None and not alive))
    start = _JOBS_START.get(os.path.basename((name or "").strip()))
    elapsed = None
    if start is not None:                       # same-session 啟動可精準計時;done 用 log 末次寫入時間凍結
        try:
            end = os.path.getmtime(fp) if done else time.time()
        except OSError:
            end = time.time()
        elapsed = max(0.0, end - start)
    return {"ok": True, "log": "\n".join(lines[-400:]),
            "done": done, "lines": len(lines), "elapsed": elapsed}


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

# 資料夾選取(原生上傳 webkitdirectory)。分批上傳＋解析輪詢進度。純 stdlib、同源 fetch 帶 cookie;非 f-string(JS 大括號免跳脫)。
PANELS = ("""
<div class=card>
<b>選擇檔案或資料夾入庫</b>
<div style="font-size:13px;color:#73726c;margin-bottom:12px">點按鈕開啟檔案管理員選取(Windows 或 WSL 內的檔皆可),逐字入知識庫。license 白名單：公版／CC／<code>owned_local</code>（自有私有須配 <code>local_private</code>）。同內容再匯＝重複（已在庫、非失敗）。圖檔需 tesseract；舊 .doc/.ppt 需 libreoffice。大夾顯示上傳／解析進度(第 k／N)。</div>
<div style="margin-bottom:12px">授權 <select id=inlic style="padding:8px;background:#faf9f5;color:#1f1e1d;border:1px solid #dcd8cc;border-radius:6px">"""
+ _LIC_OPTIONS + """</select>
 範圍 <select id=inscope style="padding:8px;background:#faf9f5;color:#1f1e1d;border:1px solid #dcd8cc;border-radius:6px">"""
+ _SCOPE_OPTIONS + """</select>
 <label style="font-size:13px;margin-left:8px"><input type=checkbox id=inkip checked> 跑入庫管線 KIP（切句→嵌→KH4→admit；不勾＝--no-kip）</label></div>
<button type=button id=upbtnF onclick="pick('file')" style="padding:9px 16px;background:#d97757;color:#fff;border:0;border-radius:8px;cursor:pointer;margin-right:8px">📄 選檔案</button>
<button type=button id=upbtnD onclick="pick('folder')" style="padding:9px 16px;background:#d97757;color:#fff;border:0;border-radius:8px;cursor:pointer">📁 選資料夾</button>
<input type=file id=fpick style="display:none">
<input type=file id=dpick webkitdirectory directory multiple style="display:none">
<div id=upprog style="display:none;margin-top:14px">
 <div style="display:flex;justify-content:space-between;gap:12px;font-size:12px;color:#73726c;margin-bottom:5px">
  <span id=upphase>準備中…</span><span id=uppct>0%</span>
 </div>
 <div style="height:8px;background:#e9e6dc;border-radius:4px;overflow:hidden">
  <div id=upbar style="height:100%;width:0%;background:#d97757;transition:width .12s ease"></div>
 </div>
 <div id=updetail style="font-size:12px;color:#73726c;margin-top:7px;word-break:break-all"></div>
</div>
<pre id=upresult style="white-space:pre-wrap;color:#73726c;font-size:13px;margin-top:12px"></pre>
</div>
<script>
function pick(kind){document.getElementById(kind=='folder'?'dpick':'fpick').click()}
document.getElementById('fpick').onchange=function(){doUpload(this.files);this.value=''}
document.getElementById('dpick').onchange=function(){doUpload(this.files);this.value=''}
function _setBusy(b){['upbtnF','upbtnD'].forEach(function(id){var el=document.getElementById(id);if(el)el.disabled=!!b})}
function _showProg(phase,k,n,detail){
 var box=document.getElementById('upprog');box.style.display='block'
 document.getElementById('upphase').textContent=phase||''
 var pct=(n>0)?Math.min(100,Math.round(100*k/n)):0
 document.getElementById('uppct').textContent=pct+'%'
 document.getElementById('upbar').style.width=pct+'%'
 document.getElementById('updetail').textContent=detail||''
}
async function doUpload(files){
 if(!files||!files.length)return
 var list=Array.prototype.slice.call(files)
 var total=list.length,res=document.getElementById('upresult')
 res.textContent=''
 _setBusy(true)
 _showProg('準備上傳',0,total,'共 '+total+' 檔')
 try{
  var bd=new URLSearchParams()
  bd.append('license',document.getElementById('inlic').value)
  bd.append('access_scope',document.getElementById('inscope').value)
  bd.append('run_kip', document.getElementById('inkip').checked ? 'on' : '')
  bd.append('total',String(total))
  var br=await fetch('/api/upload/begin',{method:'POST',body:bd,headers:{'Content-Type':'application/x-www-form-urlencoded'}})
  var bj=await br.json()
  if(!bj.ok){res.textContent='無法開始上傳:'+(bj.error||br.status);_setBusy(false);return}
  var job=bj.job_id,uploaded=0,big=0,bad=0,BATCH=6
  for(var i=0;i<list.length;i+=BATCH){
   var chunk=list.slice(i,i+BATCH)
   var cur=chunk[chunk.length-1]
   var curName=(cur.webkitRelativePath||cur.name||'')
   _showProg('上傳中 '+Math.min(i+chunk.length,total)+'／'+total,Math.min(i+chunk.length,total),total,'目前:'+curName)
   var fd=new FormData();fd.append('job_id',job)
   for(var j=0;j<chunk.length;j++){var f=chunk[j];fd.append('file',f,f.webkitRelativePath||f.name)}
   var ur=await fetch('/api/upload/file',{method:'POST',body:fd})
   var uj=await ur.json()
   if(!uj.ok){res.textContent='上傳失敗@'+(i+1)+':'+(uj.error||ur.status);_setBusy(false);return}
   uploaded=uj.uploaded;big=uj.big;bad=uj.bad
  }
  if(!uploaded){res.textContent='無有效檔案(過大跳 '+big+'、非法名跳 '+bad+')';_setBusy(false);_showProg('結束',total,total,'無有效檔');return}
  _showProg('解析入庫 0／'+uploaded,0,uploaded,'上傳完成(存 '+uploaded+'、過大跳 '+big+'、非法名跳 '+bad+')…開始解析')
  var cd=new URLSearchParams();cd.append('job_id',job)
  var cr=await fetch('/api/upload/commit',{method:'POST',body:cd,headers:{'Content-Type':'application/x-www-form-urlencoded'}})
  var cj=await cr.json()
  if(!cj.ok){res.textContent='無法開始解析:'+(cj.error||cr.status);_setBusy(false);return}
  while(true){
   await new Promise(function(r){setTimeout(r,800)})
   var sr=await fetch('/api/upload/status?job='+encodeURIComponent(job))
   var sj=await sr.json()
   if(!sj.ok){res.textContent='進度查詢失敗:'+(sj.error||'');_setBusy(false);return}
   var k=sj.k||0,n=sj.n||uploaded,st=sj.status||'',fn=sj.file||''
   // 重複＝內容 sha1 已在庫（冪等，非失敗）；略過＝無法抽取／缺 OCR／未支援副檔名等
   var counts='成功 '+(sj.ok_n||0)+' · 重複 '+(sj.dup_n||0)+' · 略過 '+((sj.skip_n||0)+(sj.short_n||0))+' · 失敗 '+(sj.fail_n||0)
   if(sj.kip_status){counts+=' · KIP '+sj.kip_status+(sj.kip_run_id?('#'+sj.kip_run_id):'')}
   _showProg('解析入庫 '+k+'／'+n,k,n||1,(fn?('目前:'+fn+' ('+st+') · '):'')+counts)
   if(sj.done){
    _showProg(sj.failed?'解析結束(有錯誤)':'解析完成',n||k,n||k||1,counts)
    res.textContent=sj.summary||sj.log||'(完成)'
    _setBusy(false);return
   }
  }
 }catch(e){res.textContent='上傳失敗:'+e;_setBusy(false)}
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
<label style="font-size:13px;margin-left:6px"><input type=checkbox name=run_kip checked> KIP</label>
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
<h3>知識抓取進度 — 主題「__TOPIC__」 <span id=stat style="color:#b5793a">● 執行中…</span> <span id=elapsed style="color:#73726c;font-family:ui-monospace,monospace;font-size:14px;font-weight:normal"></span></h3>
<div style="color:#73726c;font-size:13px;margin-bottom:8px">batch=__BATCH__ rounds=__ROUNDS__ · 背景執行(關閉此頁不中斷、resume-safe);限速/熔斷/續跑在引擎(#17/#22)。每 2 秒更新。</div>
<div style="margin-bottom:8px"><button id=copybtn onclick="copyLog()" style="padding:6px 12px;background:#fff;color:#1f1e1d;border:1px solid #dcd8cc;border-radius:8px;cursor:pointer;font-size:13px">複製全部</button>
 <span style="color:#73726c;font-size:12px;margin-left:8px">log 可直接選取複製;選取期間暫停自動刷新、不打斷選取</span></div>
<pre id=logbox style="background:#f0eee6;border:1px solid #e9e6dc;border-radius:8px;padding:14px;max-height:70vh;overflow:auto;white-space:pre-wrap;font-size:12.5px;user-select:text;-webkit-user-select:text;cursor:text">(等待引擎輸出…)</pre>
<a href=/ style="color:#5f8a5a">← 返回控制台</a>
<script>
var LF="__LOG__"
var _done=false,_base=0,_baseAt=Date.now(),_have=false
function _fmt(s){s=Math.max(0,Math.floor(s));var m=Math.floor(s/60);return (m>0?m+'m ':'')+(s%60)+'s'}
function _tick(){var el=document.getElementById('elapsed');if(el&&_have){var e=_done?_base:_base+(Date.now()-_baseAt)/1000;el.textContent=(_done?'⏱ 總 ':'⏱ ')+_fmt(e)}if(!_done)setTimeout(_tick,1000)}
_tick()
function hasSel(box){var s=window.getSelection();if(!s||s.isCollapsed||!s.rangeCount)return false;var n=s.getRangeAt(0).commonAncestorContainer;return box.contains(n.nodeType===1?n:n.parentNode)}
function copyLog(){var t=document.getElementById('logbox').textContent;var b=document.getElementById('copybtn');navigator.clipboard.writeText(t).then(function(){var o=b.textContent;b.textContent='已複製 ✓';setTimeout(function(){b.textContent=o},1500)},function(){b.textContent='複製失敗,請手動選取';setTimeout(function(){b.textContent='複製全部'},2000)})}
async function poll(){
 try{var r=await fetch('/api/topic/log?file='+encodeURIComponent(LF));var j=await r.json()
  if(j.ok){var box=document.getElementById('logbox')
   if(typeof j.elapsed==='number'){_base=j.elapsed;_baseAt=Date.now();_have=true}
   var nt=j.log||'(等待引擎輸出…)'
   if(nt!==box.textContent&&!hasSel(box)){var atBottom=box.scrollTop+box.clientHeight>=box.scrollHeight-40;box.textContent=nt;if(atBottom)box.scrollTop=box.scrollHeight}
   if(j.done){var s=document.getElementById('stat');s.textContent='✓ 完成(共 '+j.lines+' 行)';s.style.color='#5f8a5a';_done=true;var el=document.getElementById('elapsed');if(el&&_have)el.textContent='⏱ 總 '+_fmt(_base);return}}
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
.mdbody .codewrap{margin:10px 0}
.mdbody .codebar{display:flex;justify-content:space-between;align-items:center;background:#1f1e1d;color:#8a8a80;padding:5px 12px;font-size:12px;border-radius:8px 8px 0 0}
.mdbody .codecopy{background:transparent;border:0;color:#b8b3a8;font-size:12px;cursor:pointer;font-family:inherit}
.mdbody .codecopy:hover{color:#fff}
.mdbody .codewrap pre.cb{border-radius:0 0 8px 8px;margin:0}
.scrim{position:fixed;inset:0;background:rgba(0,0,0,.4);display:none;z-index:15}
.scrim.show{display:block}
#hb{display:none;position:fixed;left:12px;top:12px;z-index:20;width:34px;height:34px;border:1px solid var(--border);border-radius:8px;background:var(--surface);color:var(--text);font-size:16px;cursor:pointer;align-items:center;justify-content:center}
@media(max-width:768px){.side{position:fixed;left:0;top:0;transform:translateX(-100%);transition:transform .22s ease;z-index:25}.side.open{transform:none}.main{padding:56px 18px 40px}#hb{display:flex}}
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
<button id=hb onclick="toggleSide()" aria-label="選單" title="選單">☰</button>
<div id=scrim class=scrim onclick="toggleSide()"></div>
<script>
function nav(btn,id){document.querySelectorAll('.sec').forEach(function(s){s.classList.remove('active')});document.getElementById('sec-'+id).classList.add('active');document.querySelectorAll('.nav button').forEach(function(b){b.classList.remove('active')});btn.classList.add('active')}
function toggleSide(){var s=document.querySelector('.side'),sc=document.getElementById('scrim');var o=s.classList.toggle('open');if(sc)sc.classList.toggle('show',o)}
document.addEventListener('click',function(e){if(e.target&&e.target.classList&&e.target.classList.contains('codecopy')){var w=e.target.closest('.codewrap');var c=w&&w.querySelector('pre');if(c){navigator.clipboard.writeText(c.textContent||'');e.target.textContent='已複製 ✓';setTimeout(function(){e.target.textContent='複製'},1200)}}})
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
<a href="/gov" style="display:block;padding:8px 12px;color:#8bf;text-decoration:none;font-size:14px">🔐 來源治權 · 匯入合格</a>
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
<h1>主題抓取</h1><div class=desc>輸入主題或 domain 名（如 solar_materials／chemistry／economics_econometrics_and_finance）→ 展開 registry 域 → 觸發 harvest。中文別名（財經/化學/材料…）或英文關鍵詞（solar/perovskite）亦可。放量＝背景執行 + 即時進度頁。</div>
<div class=card>
<form method=post action=/api/topic><input name=topic placeholder="solar_materials 或 太陽能 或 solar" style="padding:8px;background:#faf9f5;border:1px solid #dcd8cc;color:#1f1e1d;border-radius:6px">
batch <input name=batch value=10 type=number min=1 max=2000 style="width:72px;padding:8px;background:#faf9f5;border:1px solid #dcd8cc;color:#1f1e1d;border-radius:6px">
rounds <input name=rounds value=1 type=number min=1 max=20 style="width:60px;padding:8px;background:#faf9f5;border:1px solid #dcd8cc;color:#1f1e1d;border-radius:6px">
<label style=font-size:13px><input type=checkbox name=run> 放量抓取(不勾=只看確認頁)</label>
<button style="padding:8px 14px;background:#d97757;color:#fff;border:0;border-radius:6px">送出</button></form>
<div style="font-size:12px;color:#73726c;margin-top:8px">首次建議 batch 10/rounds 1 小量探(#25);IP 健康再放大。放量後開即時進度頁(每 2 秒更新),關頁不中斷。<b>放量預設接下游至 KIP</b>（切句→嵌→KH4→admit≤9；CLI <code>--no-complete</code> 可只停 metadata）。</div>
</div>
</section>
<section id=sec-local class=sec>
<h1>本機匯入</h1><div class=desc>把本機或已掛載(/mnt、SSHFS)的資料夾/檔案逐字入知識庫。license 白名單含公版／CC／owned_local；同內容再匯記為「重複」（已在庫）。</div>"""
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
            lang = line[3:].strip()
            buf = []; i += 1
            while i < n and not lines[i].startswith("```"):
                buf.append(lines[i]); i += 1
            i += 1
            out.append('<div class="codewrap"><div class="codebar"><span class="lang">' + lang
                       + '</span><button class="codecopy" type="button">複製</button></div><pre class=cb>'
                       + "\n".join(buf) + "</pre></div>"); continue
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


def _gov_data(job_id=None):
    """唯讀:來源治權 + 覆蓋率 + 匯入合格帳本(IMPORT-QUAL-S2)。
    零寫路徑:純 SELECT;升級動作(approve 唯人)不經 web,只印 copy-ready CLI(#14)。
    domain 分桶對齊 FT-COV §3.2：answerable／terminal_blocked／pending（非 length>200 假覆蓋）。
    job_id 可選：篩該 job 之檔案級 qualification（?job=N）。"""
    d = {"filter_job_id": job_id}
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT approval_status, count(*) FROM knowledge_source GROUP BY 1 ORDER BY 2 DESC")
        d["approval"] = cur.fetchall()
        cur.execute("SELECT count(*) FROM knowledge_source WHERE approval_status='active'")
        d["active"] = cur.fetchone()[0]
        cur.execute("SELECT count(DISTINCT source_key) FROM knowledge_source_review_log "
                    "WHERE action IN ('approve','activate','ratify')")
        d["governed"] = cur.fetchone()[0]
        d["fulltext"] = []
        cur.execute("SELECT to_regclass('public.knowledge_fulltext_status')")
        if cur.fetchone()[0]:
            cur.execute("SELECT status, count(*) FROM knowledge_fulltext_status GROUP BY 1 ORDER BY 2 DESC LIMIT 10")
            d["fulltext"] = cur.fetchall()
        # FT-COV-DASH：可答／blocked／pending 四欄（legacy_ft_gt200 僅對照，不作 headline）
        cur.execute("""
            WITH ans AS (
              SELECT DISTINCT t.item_id
              FROM knowledge_item_text t
              JOIN knowledge_sentence s ON s.itext_id = t.itext_id
              JOIN knowledge_sentence_embedding e ON e.sent_id = s.sent_id
            ),
            txt AS (SELECT DISTINCT item_id FROM knowledge_item_text),
            blk AS (SELECT DISTINCT item_id FROM knowledge_fulltext_status WHERE status <> 'unattempted'),
            legacy AS (SELECT DISTINCT item_id FROM knowledge_item_text WHERE length(content) > 200)
            SELECT i.domain,
              count(*)::bigint AS items,
              count(*) FILTER (WHERE a.item_id IS NOT NULL)::bigint AS answerable,
              count(*) FILTER (WHERE b.item_id IS NOT NULL AND t.item_id IS NULL)::bigint AS terminal_blocked,
              count(*) FILTER (WHERE t.item_id IS NULL AND b.item_id IS NULL)::bigint AS pending,
              count(*) FILTER (WHERE l.item_id IS NOT NULL)::bigint AS legacy_ft_gt200
            FROM knowledge_item i
            LEFT JOIN ans a ON a.item_id = i.item_id
            LEFT JOIN txt t ON t.item_id = i.item_id
            LEFT JOIN blk b ON b.item_id = i.item_id
            LEFT JOIN legacy l ON l.item_id = i.item_id
            GROUP BY 1 ORDER BY 2 DESC LIMIT 12""")
        d["coverage"] = cur.fetchall()
        d["assist_summary"] = {"table": False, "latest_targets": 0, "audit_rows": 0}
        d["assist_rows"] = []
        cur.execute("SELECT to_regclass('public.knowledge_admission_assist')")
        if cur.fetchone()[0]:
            d["assist_summary"]["table"] = True
            cur.execute("""
                WITH latest AS (
                  SELECT DISTINCT ON (target_kind, target_id)
                         assist_id, target_kind, target_id, score, reason, flags, model, created_at
                  FROM knowledge_admission_assist
                  ORDER BY target_kind, target_id, created_at DESC, assist_id DESC
                )
                SELECT count(*)::bigint FROM latest""")
            d["assist_summary"]["latest_targets"] = cur.fetchone()[0]
            cur.execute("""
                SELECT count(*)::bigint
                FROM knowledge_source_review_log
                WHERE action='assist'""")
            d["assist_summary"]["audit_rows"] = cur.fetchone()[0]
            cur.execute("""
                WITH latest AS (
                  SELECT DISTINCT ON (a.target_kind, a.target_id)
                         a.assist_id, a.target_kind, a.target_id, a.score, a.reason,
                         a.flags, a.model, a.created_at
                  FROM knowledge_admission_assist a
                  ORDER BY a.target_kind, a.target_id, a.created_at DESC, a.assist_id DESC
                )
                SELECT l.target_kind,
                       l.target_id,
                       CASE WHEN l.target_kind='source' THEN l.target_id ELSE coalesce(st.source_key,'') END AS source_key,
                       CASE WHEN l.target_kind='source' THEN coalesce(src.domain,'') ELSE coalesce(st.domain,'') END AS domain,
                       round(l.score::numeric, 3)::text AS recommend_score,
                       coalesce((l.flags->>'hold_for_human')::boolean, false) AS hold_for_human,
                       coalesce((l.flags->>'license_risk')::boolean, false) AS license_risk,
                       coalesce((l.flags->>'dup_suspect')::boolean, false) AS dup_suspect,
                       coalesce(l.flags->>'suggested_domain', '') AS suggested_domain,
                       left(coalesce(l.reason,''), 140) AS reason,
                       coalesce(l.model,'') AS model,
                       to_char(l.created_at,'MM-DD HH24:MI') AS created_at
                FROM latest l
                LEFT JOIN knowledge_staging st
                  ON l.target_kind='staging' AND st.staging_id::text = l.target_id
                LEFT JOIN knowledge_source src
                  ON l.target_kind='source' AND src.source_key = l.target_id
                ORDER BY l.created_at DESC, l.assist_id DESC
                LIMIT 20""")
            d["assist_rows"] = cur.fetchall()
        cur.execute("SELECT source_key, action, old_status, new_status, actor, os_user, "
                    "to_char(created_at,'MM-DD HH24:MI') FROM knowledge_source_review_log "
                    "ORDER BY review_id DESC LIMIT 15")
        d["reviewlog"] = cur.fetchall()
        # IMPORT-QUAL-S2：本機匯入 job＋檔案級 qualification（唯讀；無 approve/activate）
        d["import_table"] = False
        d["import_jobs"] = []
        d["import_quals"] = []
        d["kip_runs"] = []
        d["import_summary"] = {"jobs": 0, "quals": 0, "by_verdict": [], "by_ingest": []}
        cur.execute("SELECT to_regclass('public.knowledge_import_job')")
        if cur.fetchone()[0]:
            d["import_table"] = True
            cur.execute("SELECT count(*)::bigint FROM knowledge_import_job")
            d["import_summary"]["jobs"] = cur.fetchone()[0]
            cur.execute("SELECT count(*)::bigint FROM knowledge_import_qualification")
            d["import_summary"]["quals"] = cur.fetchone()[0]
            cur.execute("""
                SELECT verdict, count(*)::bigint
                FROM knowledge_import_qualification
                GROUP BY 1 ORDER BY 2 DESC""")
            d["import_summary"]["by_verdict"] = cur.fetchall()
            cur.execute("""
                SELECT coalesce(ingest_status,'(unset)'), count(*)::bigint
                FROM knowledge_import_qualification
                GROUP BY 1 ORDER BY 2 DESC""")
            d["import_summary"]["by_ingest"] = cur.fetchall()
            cur.execute("""
                SELECT j.job_id, j.status, j.is_dry_run, j.source_key, j.domain,
                       j.declared_license, j.access_scope,
                       j.total_files, j.scanned_files, j.ok_files, j.dup_files,
                       j.short_files, j.skip_files, j.fail_files,
                       to_char(j.started_at,'MM-DD HH24:MI') AS started,
                       to_char(j.finished_at,'MM-DD HH24:MI') AS finished,
                       left(coalesce(j.root_path,''), 80) AS root_path
                FROM knowledge_import_job j
                ORDER BY j.job_id DESC
                LIMIT 30""")
            d["import_jobs"] = cur.fetchall()
            if job_id is not None:
                cur.execute("""
                    SELECT q.qualification_id, q.job_id, q.verdict, q.reason_code,
                           coalesce(q.ingest_status,''), coalesce(q.item_id::text,''),
                           q.segment_rows, left(q.rel_path, 100),
                           to_char(coalesce(q.ingested_at, q.preflight_at, q.created_at),'MM-DD HH24:MI')
                    FROM knowledge_import_qualification q
                    WHERE q.job_id = %s
                    ORDER BY q.qualification_id DESC
                    LIMIT 200""", (job_id,))
            else:
                cur.execute("""
                    SELECT q.qualification_id, q.job_id, q.verdict, q.reason_code,
                           coalesce(q.ingest_status,''), coalesce(q.item_id::text,''),
                           q.segment_rows, left(q.rel_path, 100),
                           to_char(coalesce(q.ingested_at, q.preflight_at, q.created_at),'MM-DD HH24:MI')
                    FROM knowledge_import_qualification q
                    ORDER BY q.qualification_id DESC
                    LIMIT 80""")
            d["import_quals"] = cur.fetchall()
        cur.execute("SELECT to_regclass('public.knowledge_ingress_kip_run')")
        if cur.fetchone()[0]:
            cur.execute("""
                SELECT kip_run_id, channel, status, cardinality(item_ids),
                       coalesce(trigger_ref,''),
                       to_char(created_at,'MM-DD HH24:MI'),
                       to_char(finished_at,'MM-DD HH24:MI')
                FROM knowledge_ingress_kip_run
                ORDER BY kip_run_id DESC LIMIT 20""")
            d["kip_runs"] = cur.fetchall()
    return d


def gov_dashboard_html(d):
    """server-render 治權頁(比照 progress 樣式,獨立頁、唯讀)。治理缺口誠實當 headline、不謊稱留痕。
    IMPORT-QUAL-S2：加匯入 job／檔案級 qualification 唯讀表；零 approve／activate 按鈕。"""
    from html import escape as e
    active, governed = d["active"], d["governed"]
    cov = f"{governed}/{active}" + (f"（{100*governed//active}%）" if active else "")
    gap_warn = ("<b style='color:#c33'>⚠ 治理缺口</b>：這些 active 源多為 bulk-seed、"
                "<b>無真人 approve/activate 升級留痕</b>；治權狀態機之升級動作 <b>approve 唯人</b>"
                "（須 TTY+superuser、走 CLI，web/AI 結構上不能觸發）。") if governed < active else "健康"
    ap = " · ".join(f"{e(s)}={n}" for s, n in d["approval"])
    ft = "".join(f"<tr><td>{e(s)}</td><td style=text-align:right>{n}</td></tr>" for s, n in d["fulltext"])
    def _pct(n, den):
        return (100 * n // den) if den else 0
    covr = "".join(
        f"<tr><td>{e(dm or '')}</td>"
        f"<td style=text-align:right>{it}</td>"
        f"<td style=text-align:right>{ans}</td>"
        f"<td style=text-align:right>{blk}</td>"
        f"<td style=text-align:right>{pend}</td>"
        f"<td style=text-align:right>{_pct(ans, it)}%</td>"
        f"<td style=text-align:right>{_pct(ans + blk, it)}%</td>"
        f"<td style=text-align:right;color:#888>{legacy}</td></tr>"
        for dm, it, ans, blk, pend, legacy in d["coverage"])
    assist = d.get("assist_summary", {})
    assist_rows = "".join(
        f"<tr><td>{e(kind)}</td><td><code>{e(tid)}</code></td><td><code>{e(sk or '')}</code></td>"
        f"<td>{e(dom or '')}</td><td style=text-align:right>{e(score)}</td>"
        f"<td>{'hold' if hold else ''}{' license' if lic else ''}{' dup' if dup else ''}"
        f"{(' → ' + e(sdom)) if sdom else ''}</td><td>{e(reason)}</td><td>{e(model or '')}</td><td>{e(ts)}</td></tr>"
        for kind, tid, sk, dom, score, hold, lic, dup, sdom, reason, model, ts in d.get("assist_rows", []))
    rl = "".join(f"<tr><td>{e(k)}</td><td>{e(a)}</td><td>{e(o or '')}→{e(nw or '')}</td>"
                 f"<td>{e(ac or '')}</td><td>{e(ou or '')}</td><td>{e(ts or '')}</td></tr>"
                 for k, a, o, nw, ac, ou, ts in d["reviewlog"])
    isum = d.get("import_summary") or {}
    verdict_s = " · ".join(f"{e(v)}={n}" for v, n in isum.get("by_verdict") or []) or "（無）"
    ingest_s = " · ".join(f"{e(s)}={n}" for s, n in isum.get("by_ingest") or []) or "（無）"
    fj = d.get("filter_job_id")
    job_rows = "".join(
        f"<tr{' style=background:#1e2a1a' if fj == jid else ''}>"
        f"<td><a href='/gov?job={jid}'>#{jid}</a></td>"
        f"<td>{e(st)}</td><td>{'dry' if dry else 'live'}</td>"
        f"<td><code>{e(sk)}</code></td><td>{e(dom)}</td>"
        f"<td style=text-align:right>{tot}</td><td style=text-align:right>{scan}</td>"
        f"<td style=text-align:right>{ok}</td><td style=text-align:right>{dup}</td>"
        f"<td style=text-align:right>{short}</td><td style=text-align:right>{skip}</td>"
        f"<td style=text-align:right>{fail}</td>"
        f"<td>{e(started or '')}</td><td>{e(finished or '')}</td>"
        f"<td style='font-size:.8em;max-width:220px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap'"
        f" title='{e(root)}'>{e(root)}</td></tr>"
        for (jid, st, dry, sk, dom, _lic, _ascope, tot, scan, ok, dup, short, skip, fail,
             started, finished, root) in d.get("import_jobs") or [])
    qual_rows = "".join(
        f"<tr><td>{qid}</td><td><a href='/gov?job={jid}'>#{jid}</a></td>"
        f"<td>{e(vd)}</td><td><code>{e(rc)}</code></td><td>{e(ing or '')}</td>"
        f"<td>{e(iid or '')}</td><td style=text-align:right>{segs}</td>"
        f"<td style='font-size:.85em;max-width:280px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap'"
        f" title='{e(rel)}'>{e(rel)}</td><td>{e(ts or '')}</td></tr>"
        for qid, jid, vd, rc, ing, iid, segs, rel, ts in d.get("import_quals") or [])
    filt_note = (f"目前篩選 job=<b>#{fj}</b> · <a href='/gov'>清除篩選</a>"
                 if fj is not None else "近 80 筆跨 job · 點 job 列可篩該批")
    kip_rows = "".join(
        f"<tr><td>#{kid}</td><td>{e(ch)}</td><td>{e(st)}</td>"
        f"<td style=text-align:right>{n}</td><td><code>{e(trig)}</code></td>"
        f"<td>{e(started or '')}</td><td>{e(finished or '')}</td></tr>"
        for kid, ch, st, n, trig, started, finished in d.get("kip_runs") or [])
    return f"""<!doctype html><html><head><meta charset=utf-8><title>來源治權 · augur admin</title>
<style>body{{font-family:system-ui,sans-serif;background:#14140f;color:#e8e6df;margin:0}}
.w{{max-width:1100px;margin:0 auto;padding:16px}}h2{{border-bottom:1px solid #444;padding-bottom:4px}}
table{{border-collapse:collapse;width:100%;font-size:.9em}}td,th{{border-bottom:1px solid #333;padding:4px 8px;text-align:left}}
.hl{{background:#2a1d1d;border:1px solid #a33;border-radius:8px;padding:12px;margin:10px 0}}
.note{{background:#1a2220;border:1px solid #355;border-radius:8px;padding:10px;margin:10px 0;color:#9ab;font-size:.9em}}
code{{background:#222;padding:2px 5px;border-radius:4px}}a{{color:#8bf}}</style></head><body><div class=w>
<p><a href="/">← 後台首頁</a> · <a href="/gov{'?job='+str(fj) if fj is not None else ''}">⟳ 重新整理</a></p>
<h1>來源治權 + 覆蓋率 + 匯入合格（唯讀）</h1>
<div class=hl><b>治理覆蓋率（governed_active/active）＝ {cov}</b><br>{gap_warn}</div>
<h2 id=import-qual>本機匯入合格帳本（IMPORT-QUAL-S2）</h2>
<div class=note>
<b>唯讀</b>：只列 <code>knowledge_import_job</code>／<code>knowledge_import_qualification</code>。
本頁<strong>無</strong> approve／activate 按鈕——不改 license gate／admission gate。
writer 已由 S1 <code>acquire_local_files</code> 落庫；此處只掃真相。
目前：表={'yes' if d.get('import_table') else 'no'} · jobs={isum.get('jobs', 0)} · quals={isum.get('quals', 0)}
<br>verdict 分佈：{verdict_s}<br>ingest 分佈：{ingest_s}<br>{filt_note}
</div>
<table><tr><th>job</th><th>status</th><th>mode</th><th>source</th><th>domain</th>
<th>total</th><th>scan</th><th>ok</th><th>dup</th><th>short</th><th>skip</th><th>fail</th>
<th>開始</th><th>結束</th><th>root</th></tr>
{job_rows or '<tr><td colspan=15>（尚無匯入 job；跑 acquire_local_files 或後台本機匯入）</td></tr>'}</table>
<h3>KIP 入庫管線帳（knowledge_ingress_kip_run）</h3>
<div class=note>三通道強制收束帳：channel／status／item 數／trigger。skipped_explicit＝後台或 CLI 明示 --no-kip。</div>
<table><tr><th>kip</th><th>channel</th><th>status</th><th>items</th><th>trigger</th><th>開始</th><th>結束</th></tr>
{kip_rows or '<tr><td colspan=7>（尚無 kip_run；先跑 migrate_knowledge_ingress_kip_ddl 或入庫觸發 KIP）</td></tr>'}</table>
<h3>檔案級 qualification</h3>
<table><tr><th>qid</th><th>job</th><th>verdict</th><th>reason</th><th>ingest</th>
<th>item</th><th>segs</th><th>rel_path</th><th>時間</th></tr>
{qual_rows or '<tr><td colspan=9>（尚無 qualification）</td></tr>'}</table>
<h2>審批狀態機分佈</h2><p>{ap}</p>
<p style=color:#999>升級動作一律走 CLI（web 零寫路徑）：<br>
<code>python scripts/review_knowledge_source.py --approve KEY --actor NAME</code>（須互動 TTY + app_user.is_superuser）<br>
<code>python scripts/probe_knowledge_source.py --source KEY</code>（前置最小探測、唯一 web 外之寫 review_log）</p>
<h2>知識終態分桶（per domain；FT-COV-DASH）</h2>
<div class=note>
<b>覆蓋（可答）</b>＝answerable／items（至少一句已 embed）。
<b>終態完成率</b>＝(answerable＋terminal_blocked)／items（含誠實不可答）。
pending＝無全文且無終態列（無 status 或 status='unattempted'＝未嘗試）；blocked＝skip_license／skip_no_oa 等終態帳（<b>非漏做、不得灌成全文</b>）。
「舊 length&gt;200」僅歷史對照——erp 短文會假低，勿當可檢索 headline。
</div>
<table><tr><th>domain</th><th>items</th><th>answerable</th><th>blocked</th><th>pending</th>
<th>可答%</th><th>終態%</th><th>舊&gt;200</th></tr>{covr}</table>
<h2>Fulltext 終態分佈</h2><table><tr><th>status</th><th>數</th></tr>{ft}</table>
<p style=color:#999>skip_license/skip_no_oa = license 阻擋之 metadata-only（終態、非漏做）；skip_fetch_error = 可重試。</p>
<h2>AI 預審建議（ADM-AI-ASSIST；唯讀）</h2>
<div class=note>
<b>recommend_score</b> 只供人排隊與掃視；<b>不是</b> approve／activate 依據。
<code>--apply</code> 只會寫 <code>knowledge_admission_assist</code> 與 source review audit(action=<code>assist</code>)，
<b>不改任何審批終態</b>。
目前：assist 表={'yes' if assist.get('table') else 'no'} · 最新 target={assist.get('latest_targets', 0)} · source audit={assist.get('audit_rows', 0)}
</div>
<table><tr><th>kind</th><th>target</th><th>source</th><th>domain</th><th>score</th><th>風險/提示</th><th>理由</th><th>model</th><th>時間</th></tr>
{assist_rows or '<tr><td colspan=9>（尚無 assist 建議）</td></tr>'}</table>
<h2>審批稽核軌跡（近 15）</h2>
<table><tr><th>source</th><th>action</th><th>轉移</th><th>actor</th><th>os_user</th><th>時間</th></tr>{rl or '<tr><td colspan=6>（無留痕）</td></tr>'}</table>
</div></body></html>"""


def _digest_data():
    """唯讀:R6 digest 資料——本週全部 gate_ref='V2-AUTOADVANCE' 自動決策 + pending hints(H3 佇列)。
    零寫路徑(P-D;整合計畫 §二);hint 批覆走 POST /api/hint/decide(同一 decision 路徑、console 登入=是人證據)。"""
    d = {}
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("""SELECT to_char(a.applied_at,'MM-DD HH24:MI'), q.feature, q.action,
                              a.before_status, a.after_status, a.evidence_json->>'auto_rule'
                       FROM evolution_apply_log a JOIN promotion_queue q USING (queue_id)
                       WHERE a.evidence_json->>'gate_ref'='V2-AUTOADVANCE'
                         AND a.applied_at > now() - interval '7 days'
                       ORDER BY a.applied_at DESC""")
        d["auto"] = cur.fetchall()
        cur.execute("""SELECT hint_id, from_axis, from_iteration_uid, hint_text,
                              coalesce(provenance->>'median_corr',''), coalesce(provenance->>'n_obs',''),
                              to_char(created_at,'MM-DD HH24:MI')
                       FROM evolution_hypothesis_hint WHERE decision='pending'
                       ORDER BY created_at""")
        d["pending"] = cur.fetchall()
        cur.execute("""SELECT decision, count(*) FROM evolution_hypothesis_hint
                       WHERE decided_at > now() - interval '7 days' GROUP BY 1""")
        d["decided_week"] = cur.fetchall()
    return d


def digest_html(d, uname):
    """R6 digest 頁(唯讀渲染;批覆按鈕走同一 decision 路徑)。榮譽制誠實條文照錄,不宣稱機械保證。"""
    from html import escape as e
    auto = "".join(f"<tr><td>{e(ts)}</td><td><code>{e(f)}</code></td><td>{e(ac)}</td>"
                   f"<td>{e(b or '')}→{e(af or '')}</td><td>{e(r or '')}</td></tr>"
                   for ts, f, ac, b, af, r in d["auto"])
    pend = "".join(
        f"<tr id='h_{e(h)}'><td><code>{e(h)}</code></td><td>{e(ax)}/{e(it or '')}</td>"
        f"<td>{e(tx)}</td><td style=text-align:right>{e(mc)}{'（n=' + e(no) + '）' if no else ''}</td>"
        f"<td>{e(ts)}</td>"
        f"<td><button onclick=\"decide('{e(h)}','approved')\">approve</button> "
        f"<button onclick=\"decide('{e(h)}','rejected')\" style='background:#533'>reject</button></td></tr>"
        for h, ax, it, tx, mc, no, ts in d["pending"])
    dw = " · ".join(f"{e(k)}={n}" for k, n in d["decided_week"]) or "（本週無批覆）"
    return f"""<!doctype html><html><head><meta charset=utf-8><title>R6 digest · augur admin</title>
<style>body{{font-family:system-ui,sans-serif;background:#14140f;color:#e8e6df;margin:0}}
.w{{max-width:1150px;margin:0 auto;padding:16px}}h2{{border-bottom:1px solid #444;padding-bottom:4px}}
table{{border-collapse:collapse;width:100%;font-size:.88em}}td,th{{border-bottom:1px solid #333;padding:4px 8px;text-align:left;vertical-align:top}}
.note{{background:#1a2220;border:1px solid #355;border-radius:8px;padding:10px;margin:10px 0;color:#9ab;font-size:.9em}}
button{{background:#2d4a33;color:#dfe;border:1px solid #575;border-radius:5px;padding:3px 10px;cursor:pointer}}
code{{background:#222;padding:2px 5px;border-radius:4px}}a{{color:#8bf}}</style></head><body><div class=w>
<p><a href="/">← 後台首頁</a></p><h1>R6 自動決策 digest ＋ H3 hint 批覆</h1>
<div class=note><b>榮譽制條文照錄（§8.1）</b>：console 密碼登入＝比 CLI 更強的「是人」證據，
但仍為<b>榮譽制＋事後偵測</b>，不宣稱機械保證。批覆寫入 <code>decided_by={e(uname)}</code>；
hint 決定<b>單向不可回改</b>（forward-only 閘），要翻案走新 hint 列＋duplicate_of。
approve＝該假說進量化鏈（H3 判準層）——不確定就先不按。</div>
<h2>本週自動決策（gate_ref=V2-AUTOADVANCE，{len(d['auto'])} 筆；請掃視認領）</h2>
<table><tr><th>時間</th><th>feature</th><th>action</th><th>轉移</th><th>依據規則</th></tr>
{auto or '<tr><td colspan=5>（本週無自動決策）</td></tr>'}</table>
<h2>pending hints（H3 佇列，{len(d['pending'])} 則）</h2>
<table><tr><th>hint</th><th>軸/輪</th><th>內容</th><th>med corr</th><th>時間</th><th>批覆</th></tr>
{pend or '<tr><td colspan=6>（無待批 hint）</td></tr>'}</table>
<p>本週已批覆：{dw}</p>
<script>
async function decide(h, dec) {{
  if (!confirm(dec + ' ' + h + '?（單向不可回改）')) return;
  const r = await fetch('/api/hint/decide', {{method:'POST',
    headers:{{'Content-Type':'application/x-www-form-urlencoded'}},
    body:'hint_id='+encodeURIComponent(h)+'&decision='+encodeURIComponent(dec)}});
  const j = await r.json();
  if (j.ok) {{ document.getElementById('h_'+h).style.opacity=.35; }}
  else alert('未生效:'+(j.err||''));
}}
</script></div></body></html>"""


class AdminHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _token(self):
        c = self.headers.get("Cookie", "")
        for kv in c.split(";"):
            if kv.strip().startswith("sid="):
                return kv.strip()[4:]
        return None

    def _owner_uid(self):
        """受驗 DB session → app_user.user_id;env 後門(記憶體 session)/未登入 → None(件 A 增補#6:
        絕不信任 client 傳入 uid,防越權標他人為 owner #5)。owner=None 時 acquire 端不寫 owner(僅 super 可見私有)。"""
        return identity.verify_session(self._token())

    def _local_source_key(self, domain):
        """本機通道 source_key(件 A1:白名單校驗、防任意 FK)。預設 local_files_<domain 或 local>;
        須為已 active 之本機源(否則 acquire admission 閘拒、回明確訊息)。不信任 client 值。
        不靜默落到無關的 smoke_test 等第一個 active 源——優先同名 key，其次 domain 相符。"""
        sk = "local_files_" + (domain or "local")
        try:
            with db.connect() as conn, db.transaction(conn) as cur:
                cur.execute(
                    "SELECT 1 FROM knowledge_source WHERE source_key=%s "
                    "AND adapter IN ('local_files','manual_file') "
                    "AND approval_status='active'",
                    (sk,),
                )
                if cur.fetchone():
                    return sk
                # 次選：同 domain 的 active local_files（勿 ORDER BY source_key 誤吃 smoke_test）
                cur.execute(
                    "SELECT source_key FROM knowledge_source "
                    "WHERE adapter='local_files' AND approval_status='active' "
                    "AND domain=%s ORDER BY source_key LIMIT 1",
                    (domain or "local",),
                )
                r = cur.fetchone()
                if r:
                    return r[0]
                return sk  # 無 active → 回預設，由 acquire admission 閘擋
        except Exception:
            return sk

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
        if path == "/api/upload/status":
            return self._handle_upload_status(parse_qs(parsed.query).get("job", [""])[0])
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
        if path == "/api/gov":
            jid_raw = parse_qs(parsed.query).get("job", [None])[0]
            jid = int(jid_raw) if jid_raw and str(jid_raw).isdigit() else None
            return self._send(200, json.dumps(_gov_data(job_id=jid), default=str), "application/json")
        if path == "/gov":                          # 來源治權唯讀頁(零寫路徑;升級走 CLI #14)
            jid_raw = parse_qs(parsed.query).get("job", [None])[0]
            jid = int(jid_raw) if jid_raw and str(jid_raw).isdigit() else None
            return self._send(200, gov_dashboard_html(_gov_data(job_id=jid)))
        if path == "/api/digest":
            return self._send(200, json.dumps(_digest_data(), default=str), "application/json")
        if path == "/digest":                       # R6 digest 唯讀頁(P-D;批覆走 POST /api/hint/decide)
            uname, _role = self._acct()
            return self._send(200, digest_html(_digest_data(), uname))
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
            env_user = os.environ.get("AUGUR_ADMIN_USER", "").strip()
            stored = os.environ.get("AUGUR_ADMIN_PASSWORD", "")
            # env 帳密後門(.env 明文或 pbkdf2):帳號留空、或帳號等於 AUGUR_ADMIN_USER → 走此路(臨時 superuser、記憶體 session)
            if stored and (not username or (env_user and username == env_user)):
                if _admin_pw_ok(pw.strip(), stored):
                    tok = _new_session()
                    _audit("login", f"ok env user={username or '(blank)'}")
                    return self._send(303, "", cookie=f"sid={tok}; HttpOnly; SameSite=Strict; Path=/",
                                      ctype="text/plain")
                _audit("login", f"fail env user={username or '(blank)'}")
                return self._send(200, LOGIN_HTML.format(msg="<p style=color:#b5793a>帳號或密碼錯誤</p>"))
            if username:                          # DB 群組使用者(app_user、pbkdf2 240k)
                u = identity.authenticate(username, pw)
                if u:
                    tok = identity.issue_session(u["user_id"], client_note="admin")
                    _audit("login", f"ok user={username} super={u['is_superuser']}")
                    return self._send(303, "", cookie=f"sid={tok}; HttpOnly; SameSite=Strict; Path=/",
                                      ctype="text/plain")
                _audit("login", f"fail user={username}")
            _audit("login", "fail")
            return self._send(200, LOGIN_HTML.format(msg="<p style=color:#b5793a>帳號或密碼錯誤</p>"))

        if not _valid(self._token()):
            return self._send(403, "未授權", ctype="text/plain")

        if path == "/api/hint/decide":
            # H3 hint 批覆(P-D):console 登入=是人證據(§8.1 榮譽制);同一 decision 路徑、
            # forward-only 閘擋回改;decided_by=登入帳號(不由 AI 代打,承 never-type-human-signature)。
            n = int(self.headers.get("Content-Length") or 0)
            form = parse_qs(self.rfile.read(n).decode("utf-8", "replace")) if n else {}
            hid = (form.get("hint_id", [""])[0]).strip()
            dec = (form.get("decision", [""])[0]).strip()
            if dec not in ("approved", "rejected") or not hid:
                return self._send(200, json.dumps({"ok": False, "err": "decision 須 approved|rejected"}),
                                  "application/json")
            uname, _role = self._acct()
            code = f"RAWEVO-HINT-{'approve' if dec == 'approved' else 'reject'}(console)"
            try:
                with db.connect() as conn:
                    cur = conn.cursor()
                    cur.execute("SET LOCAL augur.honesty_write = 'on'")   # 誠實帳本閘通行證(B4-P2a)
                    cur.execute("""UPDATE evolution_hypothesis_hint
                        SET decision=%s, decided_by=%s, decided_at=now(), decision_code=%s,
                            gate_ref='H3-console'
                        WHERE hint_id=%s AND decision='pending'""", (dec, uname, code, hid))
                    changed = cur.rowcount
                    conn.commit()
            except Exception as ex:  # noqa: BLE001  forward-only 閘拒絕等,誠實回錯不吞
                _audit("hint_decide", f"fail {hid} {dec}: {ex}")
                return self._send(200, json.dumps({"ok": False, "err": str(ex)[:200]}), "application/json")
            _audit("hint_decide", f"{dec} {hid} by={uname} changed={changed}")
            return self._send(200, json.dumps(
                {"ok": bool(changed), "hint_id": hid, "decision": dec, "decided_by": uname,
                 **({} if changed else {"err": "無 pending 之該 hint(不存在或已決)"})}), "application/json")

        if path == "/api/upload":
            return self._handle_upload(py)
        if path == "/api/upload/begin":
            return self._handle_upload_begin()
        if path == "/api/upload/file":
            return self._handle_upload_file()
        if path == "/api/upload/commit":
            return self._handle_upload_commit(py)

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
                _JOBS_START[logname] = time.time()
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
            sk, uid = self._local_source_key("local"), self._owner_uid()   # 件 A1:source_key 回填+RBAC owner
            _audit("folder", f"{safe} license={lic} scope={scope} src={sk} owner={uid}")
            cmd = [py, os.path.join(ROOT, "scripts", "acquire_local_files.py"),
                   "--dir", safe, "--source-key", sk, "--license", lic, "--access-scope", scope, "--domain", "local"]
            if uid is not None:
                cmd += ["--owner-user-id", str(uid)]
            r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=300)
            out = r.stdout + (("\n[admission/錯誤]\n" + r.stderr) if r.returncode != 0 else "")   # 顯拒因(不靜默)
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
            run_kip = g("run_kip") == "on"
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
            sk, uid = self._local_source_key("local"), self._owner_uid()
            _audit("sftp_ingest", f"{conn}:{rpath} saved={st['saved']} license={lic} scope={scope} "
                   f"src={sk} owner={uid} run_kip={run_kip}")
            if not st["saved"]:
                return self._send(200, f"{pre}遠端無可下載檔(過大跳 {st['skipped_big']})</pre><a href=/>← 返回</a>")
            cmd = [py, os.path.join(ROOT, "scripts", "acquire_local_files.py"),
                   "--dir", updir, "--source-key", sk, "--license", lic, "--access-scope", scope, "--domain", "local"]
            if uid is not None:
                cmd += ["--owner-user-id", str(uid)]
            if not run_kip:
                cmd.append("--no-kip")
            rr = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=3600)
            out = rr.stdout + (("\n[admission/錯誤]\n" + rr.stderr) if rr.returncode != 0 else "")
            head = (f"【SFTP 下載+解析】{conn}:{rpath}\n下載 {st['saved']} 檔"
                    f"(過大跳 {st['skipped_big']}{'、截斷' if st['truncated'] else ''})、"
                    f"license={lic} scope={scope} KIP={'on' if run_kip else 'off'}\n\n")
            return self._send(200, f"{pre}{html.escape(head + out)}</pre><a href=/>← 返回</a>")

        return self._send(404, "unknown", ctype="text/plain")

    def _handle_upload_begin(self):
        """分批上傳開 job:校驗 license → 建暫存夾 → 回 job_id。"""
        n = int(self.headers.get("Content-Length") or 0)
        form = parse_qs(self.rfile.read(n).decode("utf-8", "replace")) if n else {}
        g = lambda k: (form.get(k, [""])[0]).strip()
        lic, scope = g("license"), g("access_scope") or "local_private"
        run_kip = g("run_kip") == "on"
        if lic not in _LICENSES:
            return self._send(200, json.dumps({"ok": False, "error": "license 非白名單(DB 硬擋只准公開授權)"}),
                              "application/json")
        if scope not in _SCOPES:
            scope = "local_private"
        try:
            total = max(0, min(100000, int(g("total") or 0)))
        except ValueError:
            total = 0
        job_id = secrets.token_hex(8)
        updir = webupload.new_upload_dir()
        _UPLOAD_JOBS[job_id] = {
            "updir": updir, "license": lic, "scope": scope, "total": total,
            "uploaded": 0, "big": 0, "bad": 0, "phase": "upload",
            "logname": None, "pid": None, "t0": time.time(), "failed": False,
            "run_kip": run_kip,
        }
        _audit("upload_begin", f"job={job_id} total={total} license={lic} scope={scope} "
               f"run_kip={run_kip} updir={updir}")
        return self._send(200, json.dumps({"ok": True, "job_id": job_id, "total": total}), "application/json")

    def _handle_upload_file(self):
        """分批上傳一包檔案(multipart)→ append 進 job 暫存夾。"""
        ctype = self.headers.get("Content-Type", "")
        n = int(self.headers.get("Content-Length") or 0)
        if "multipart/form-data" not in ctype or "boundary=" not in ctype:
            return self._send(200, json.dumps({"ok": False, "error": "需 multipart/form-data"}), "application/json")
        if n > MAX_UPLOAD:
            return self._send(200, json.dumps({"ok": False, "error": f"單批過大(上限 {MAX_UPLOAD // 1024 // 1024}MB)"}),
                              "application/json")
        boundary = ctype.split("boundary=", 1)[1].strip().strip('"')
        fields, files = webupload.parse_multipart(self.rfile.read(n), boundary)
        jid, job = _upload_job(fields.get("job_id") or "")
        if not job:
            return self._send(200, json.dumps({"ok": False, "error": "無效或過期 job_id"}), "application/json")
        if job.get("phase") != "upload":
            return self._send(200, json.dumps({"ok": False, "error": "job 已進入解析、不可再上傳"}), "application/json")
        if not files:
            return self._send(200, json.dumps({"ok": False, "error": "本批無檔案"}), "application/json")
        r = webupload.append_upload(job["updir"], files)
        job["uploaded"] = job.get("uploaded", 0) + r["saved"]
        job["big"] = job.get("big", 0) + r["big"]
        job["bad"] = job.get("bad", 0) + r["bad"]
        names = [fn for fn, _ in files[:3]]
        return self._send(200, json.dumps({
            "ok": True, "job_id": jid, "batch_saved": r["saved"], "batch_big": r["big"], "batch_bad": r["bad"],
            "uploaded": job["uploaded"], "big": job["big"], "bad": job["bad"],
            "samples": names,
        }), "application/json")

    def _handle_upload_commit(self, py):
        """上傳完畢→背景跑 acquire_local_files(-u)寫 log,前端輪詢 /api/upload/status。"""
        n = int(self.headers.get("Content-Length") or 0)
        form = parse_qs(self.rfile.read(n).decode("utf-8", "replace")) if n else {}
        jid, job = _upload_job((form.get("job_id", [""])[0]).strip())
        if not job:
            return self._send(200, json.dumps({"ok": False, "error": "無效或過期 job_id"}), "application/json")
        if job.get("phase") == "parse":
            return self._send(200, json.dumps({"ok": True, "job_id": jid, "already": True}), "application/json")
        if not job.get("uploaded"):
            return self._send(200, json.dumps({"ok": False, "error": "無有效檔案可解析"}), "application/json")
        sk, uid = self._local_source_key("local"), self._owner_uid()
        logname = f"local_import_{jid}.log"
        os.makedirs(LOG_DIR, exist_ok=True)
        cmd = [py, "-u", os.path.join(ROOT, "scripts", "acquire_local_files.py"),
               "--dir", job["updir"], "--source-key", sk, "--license", job["license"],
               "--access-scope", job["scope"], "--domain", "local"]
        if uid is not None:
            cmd += ["--owner-user-id", str(uid)]
        if not job.get("run_kip", True):
            cmd.append("--no-kip")
        _audit("upload_commit", f"job={jid} updir={job['updir']} saved={job['uploaded']} "
               f"big={job['big']} bad={job['bad']} license={job['license']} scope={job['scope']} "
               f"src={sk} owner={uid} run_kip={job.get('run_kip', True)}")
        lf = open(os.path.join(LOG_DIR, logname), "w")
        try:
            proc = subprocess.Popen(cmd, cwd=ROOT, stdout=lf, stderr=subprocess.STDOUT,
                                    stdin=subprocess.DEVNULL, start_new_session=True)
            job["phase"] = "parse"
            job["logname"] = logname
            job["pid"] = proc.pid
            job["t0_parse"] = time.time()
            _JOBS[logname] = proc.pid
            _JOBS_START[logname] = time.time()
        finally:
            lf.close()
        return self._send(200, json.dumps({"ok": True, "job_id": jid, "log": logname}), "application/json")

    def _handle_upload_status(self, job_id):
        """輪詢分批上傳／解析進度(JSON)。"""
        jid, job = _upload_job(job_id)
        if not job:
            return self._send(200, json.dumps({"ok": False, "error": "無效或過期 job_id"}), "application/json")
        out = {
            "ok": True, "job_id": jid, "phase": job.get("phase"),
            "uploaded": job.get("uploaded", 0), "big": job.get("big", 0), "bad": job.get("bad", 0),
            "total": job.get("total", 0), "done": False, "failed": False,
            "k": 0, "n": job.get("uploaded", 0) or job.get("total", 0),
            "file": "", "status": "", "ok_n": 0, "dup_n": 0, "short_n": 0, "skip_n": 0, "fail_n": 0,
            "summary": "", "log": "",
        }
        if job.get("phase") != "parse":
            out["k"] = job.get("uploaded", 0)
            return self._send(200, json.dumps(out), "application/json")
        logname = job.get("logname") or ""
        fp = os.path.join(LOG_DIR, os.path.basename(logname)) if logname.startswith("local_import_") else None
        data = ""
        if fp and os.path.isfile(fp):
            try:
                with open(fp, "r", errors="replace") as f:
                    data = f.read()
            except OSError:
                data = ""
        parsed = _parse_local_import_log(data)
        out.update({k: parsed[k] for k in ("k", "n", "file", "status", "ok_n", "dup_n", "short_n",
                                           "skip_n", "fail_n", "summary", "kip_status", "kip_run_id")})
        if not out["n"]:
            out["n"] = job.get("uploaded", 0)
        pid = job.get("pid")
        alive = False
        if pid:
            try:
                os.kill(pid, 0)
                alive = True
            except OSError:
                alive = False
        done = bool(parsed.get("done_mark") or (pid is not None and not alive))
        out["done"] = done
        out["log"] = "\n".join(data.splitlines()[-80:])
        if done and not parsed.get("done_mark"):
            out["failed"] = True
            if not out["summary"]:
                out["summary"] = out["log"] or "(進程結束且無完成標記—可能 admission 拒絕或異常)"
        elif done:
            head = (f"【原生上傳解析】暫存 {job['updir']}\n"
                    f"存檔 {job['uploaded']}(過大跳 {job['big']}、非法名跳 {job['bad']})、"
                    f"license={job['license']} scope={job['scope']}\n\n")
            out["summary"] = head + (out["summary"] or out["log"])
        return self._send(200, json.dumps(out), "application/json")

    def _handle_upload(self, py):
        """B · 原生上傳(相容舊單次 multipart):落暫存夾→同步餵 acquire_local_files。新 UI 走 begin/file/commit。"""
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
        sk, uid = self._local_source_key("local"), self._owner_uid()
        _audit("upload", f"{r['updir']} saved={r['saved']} big={r['big']} bad={r['bad']} license={lic} scope={scope} src={sk} owner={uid}")
        if not r["saved"]:
            return self._send(400, f"無有效檔案(過大跳 {r['big']}、非法名跳 {r['bad']})", ctype="text/plain")
        cmd = [py, os.path.join(ROOT, "scripts", "acquire_local_files.py"),
               "--dir", r["updir"], "--source-key", sk, "--license", lic, "--access-scope", scope, "--domain", "local"]
        if uid is not None:
            cmd += ["--owner-user-id", str(uid)]
        ru = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=600)
        out = ru.stdout + (("\n[admission/錯誤]\n" + ru.stderr) if ru.returncode != 0 else "")
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
