#!/usr/bin/env python
"""augur 誠實博學的我 — 極簡對話 Web UI(stdlib proxy 到 advisor 殼 + 「+」附加入庫)。

🎯 一頁式對話介面:瀏覽器 → 本頁(:8090) → advisor 殼(:8399,advise+guard) → qwen3:8b。
   純 http.server + urllib、無 HuggingFace/無 node/無 Docker(避 Open WebUI 之 HF 嵌入 crash-loop)。
   同源 proxy(頁與 /chat 同埠)故無 CORS;guard verdict 顯示於每則回覆下。
   「+」按鈕(Claude Desktop 式):彈原生視窗選檔案/資料夾,兩種語意——
   · Mode A(入知識庫):/ingest 逐字入庫(webupload 落暫存夾 → acquire_local_files;license 受 DB CHECK
     白名單硬擋、access_scope=local_private),之後可被引經據典;
   · Mode B(只問這次):/attach 抽附加檔逐字文字(不入庫)→ 前端夾帶 augur_attach 轉發 advisor,
     本回合以附加檔為引文語料、guard 對附加檔逐字比對(誠實不變、只換語料與人格框架)。
守 #1(逐字入庫/逐字比對)· #5(上傳 traversal/大小防護)· #28(本地零 usage)· 計畫 §3-S7(對話出口=advise+guard)· #18。

執行指令矩陣:
  python scripts/serve_chat_ui.py                 # 起於 127.0.0.1:8090(預設);瀏覽器開 http://localhost:8090
  python scripts/serve_chat_ui.py --port 8090 --advisor http://127.0.0.1:8399
"""
import argparse
import json
import os
import subprocess
import sys
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

import _bootstrap  # noqa: F401  個別可執行(#29a)
from augur.knowledge import webupload, identity   # identity 匯入鏈載入 .env(取 AUGUR_INTERNAL_SECRET)

ADVISOR = "http://127.0.0.1:8399"
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SECRET = os.environ.get("AUGUR_INTERNAL_SECRET")   # 前台↔殼共享機密(P4;送 X-Augur-Internal)

LOGIN_PAGE = """<!doctype html><html lang=zh-Hant><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1"><title>誠實博學的我 · 登入</title></head>
<body style="margin:0;font-family:system-ui,'Noto Sans TC',sans-serif;background:#0d1117;color:#e6edf3;display:flex;min-height:100vh;align-items:center;justify-content:center">
<div style="width:340px;padding:32px;background:#161b22;border:1px solid #21262d;border-radius:14px">
<h2 style="margin:0 0 4px;font-size:19px">誠實博學的我</h2>
<p style="color:#7d8590;font-size:13px;margin:0 0 18px">登入以依你的權限檢索知識</p>__MSG__
<form method=post action=/login><input name=username placeholder="帳號" autofocus style="width:100%;padding:11px;margin:4px 0 8px;background:#0d1117;border:1px solid #30363d;color:#e6edf3;border-radius:8px;font-size:15px">
<input type=password name=pw placeholder="密碼" style="width:100%;padding:11px;margin:4px 0 12px;background:#0d1117;border:1px solid #30363d;color:#e6edf3;border-radius:8px;font-size:15px">
<button style="width:100%;padding:11px;background:#238636;color:#fff;border:0;border-radius:8px;font-size:15px;cursor:pointer">登入</button></form></div></body></html>"""


def _safe_dir(path):
    """+資料夾圍欄:realpath 須在 $HOME 下(拒 ../ 逃逸);回 realpath 或 None。"""
    home = os.path.realpath(os.path.expanduser("~"))
    rp = os.path.realpath(os.path.expanduser((path or "").strip()))
    return rp if (rp == home or rp.startswith(home + os.sep)) and os.path.isdir(rp) else None

PAGE = """<!doctype html><html lang=zh-Hant><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>誠實博學的我 · augur</title><style>
:root{color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;font-family:system-ui,"Noto Sans TC",-apple-system,sans-serif;background:#0d1117;color:#e6edf3;font-size:15px;line-height:1.65}
header{padding:14px 20px;border-bottom:1px solid #21262d;font-weight:600;position:sticky;top:0;background:#0d1117;z-index:5}
header small{color:#7d8590;font-weight:400;margin-left:8px;font-size:12px}
#log{max-width:800px;margin:0 auto;padding:20px 18px 48px}
.msg{margin:20px 0}
.role{font-size:12px;color:#7d8590;margin-bottom:6px;font-weight:600;letter-spacing:.3px}
.u .bubble{background:#1f6feb1a;border:1px solid #1f6feb44;border-radius:12px;padding:12px 15px;white-space:pre-wrap}
.a .bubble{background:transparent;padding:0 2px}
.bubble{line-height:1.7}
.bubble p{margin:0 0 12px}.bubble p:last-child{margin-bottom:0}
.bubble h2,.bubble h3,.bubble h4{margin:16px 0 8px;line-height:1.3}
.bubble h2{font-size:1.25em}.bubble h3{font-size:1.12em}.bubble h4{font-size:1.02em;color:#c9d1d9}
.bubble ul,.bubble ol{margin:8px 0;padding-left:22px}.bubble li{margin:4px 0}
.bubble code{background:#161b22;border:1px solid #30363d;border-radius:5px;padding:1px 5px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.88em}
.bubble pre.cb{background:#010409;border:1px solid #30363d;border-radius:8px;padding:12px 14px;overflow:auto;font-family:ui-monospace,monospace;font-size:.85em;line-height:1.5;white-space:pre}
.bubble pre.cb code{background:none;border:0;padding:0}
.bubble a{color:#58a6ff}.bubble b{color:#f0f6fc}
.g{font-size:12px;color:#7d8590;margin-top:10px;border-top:1px dashed #30363d;padding-top:6px}
.g.pass{color:#3fb950}.g.fail{color:#d29922}
#bar{position:sticky;bottom:0;background:linear-gradient(180deg,#0d111700,#0d1117 22%);border-top:1px solid #21262d;padding:12px}
#bar form{max-width:800px;margin:0 auto;display:flex;gap:8px;align-items:center}
#q{flex:1;padding:12px 14px;border-radius:12px;border:1px solid #30363d;background:#161b22;color:#e6edf3;font-size:15px}
#q:focus{outline:0;border-color:#1f6feb88}
button{padding:11px 18px;border:0;border-radius:10px;background:#238636;color:#fff;font-size:15px;cursor:pointer}
button:hover{background:#2ea043}
button:disabled{background:#30363d;cursor:wait}
.sys{color:#7d8590;font-size:13px;text-align:center;margin:8px}
#plusbtn{padding:11px 15px;border:1px solid #30363d;border-radius:10px;background:#161b22;color:#e6edf3;font-size:18px;cursor:pointer}
#plusbtn:hover{background:#21262d}
#plusmenu{display:none;max-width:800px;margin:0 auto 8px;background:#161b22;border:1px solid #30363d;border-radius:10px;padding:12px}
#plusmenu button{margin:4px 4px 0 0;background:#21262d;color:#e6edf3;font-size:14px;padding:8px 12px;border:1px solid #30363d;border-radius:6px;cursor:pointer}
#plusmenu select{padding:6px;background:#0d1117;color:#e6edf3;border:1px solid #30363d;border-radius:6px}
#plusmenu .hint{font-size:12px;color:#7d8590;margin-bottom:6px}
#chip{display:none;max-width:800px;margin:0 auto 6px;background:#1f6feb22;border:1px solid #1f6feb55;border-radius:8px;padding:8px;font-size:13px;cursor:pointer;color:#e6edf3}
</style></head><body>
<header>誠實博學的我 <small>augur · advisor+guard · 本地 qwen3:8b(引文逐字閘;答不出即誠實說不知道)</small></header>
<div id=log><div class=sys>問投資哲學/經典原文相關問題。回覆較慢(本地 GPU 約數分鐘),guard 會攔下非逐字引用。</div></div>
<div id=bar>
<div id=chip onclick="clearAttach()"></div>
<div id=plusmenu>
 <div class=hint>A · 入知識庫(永久保存、之後可被引經據典;需公開授權,DB 硬擋只准 public_domain/cc-*)</div>
 授權 <select id=inlic><option>public_domain</option><option>cc-by</option><option>cc-by-sa</option><option>cc0</option></select>
 <button type=button onclick="pick('file')">📎 選檔案入庫</button>
 <button type=button onclick="pick('folder')">📁 選資料夾入庫</button>
 <div class=hint style="margin-top:10px">B · 只問這次(不入庫、只當本次對話的文件助讀;之後提問只根據這份檔回答)</div>
 <button type=button onclick="pickB('file')">📄 選檔案 · 只問這次</button>
 <button type=button onclick="pickB('folder')">📁 選資料夾 · 只問這次</button>
</div>
<form onsubmit="return send(event)">
<button id=plusbtn type=button onclick="togglePlus()" title="附加檔案/資料夾入庫">＋</button>
<input id=q placeholder="例:用經典原文談安全邊際與價值的關係" autocomplete=off>
<button id=b type=submit>送出</button></form></div>
<input type=file id=fpick style="display:none">
<input type=file id=dpick webkitdirectory directory multiple style="display:none">
<script>
const log=document.getElementById('log'),q=document.getElementById('q'),b=document.getElementById('b')
function add(cls,txt){var d=document.createElement('div');d.className='msg '+cls
 var role=document.createElement('div');role.className='role';role.textContent=(cls=='u'?'你':'誠實博學的我')
 var bub=document.createElement('div');bub.className='bubble';bub.textContent=txt
 d.appendChild(role);d.appendChild(bub);log.appendChild(d);d.scrollIntoView();d._bubble=bub;return d}
function esc(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}
function mdToHtml(t){
 var S=String.fromCharCode(1),store=[]
 function stash(h){store.push(h);return S+(store.length-1)+S}
 t=esc(t||'')
 t=t.replace(/```([\\s\\S]*?)```/g,function(_,c){return stash('<pre class=cb><code>'+c.replace(/^\\n/,'').replace(/\\n$/,'')+'</code></pre>')})
 t=t.replace(/`([^`\\n]+)`/g,function(_,c){return stash('<code>'+c+'</code>')})
 t=t.replace(/^#### (.+)$/gm,'<h4>$1</h4>').replace(/^### (.+)$/gm,'<h4>$1</h4>').replace(/^## (.+)$/gm,'<h3>$1</h3>').replace(/^# (.+)$/gm,'<h3>$1</h3>')
 t=t.replace(/\\*\\*([^*]+)\\*\\*/g,'<b>$1</b>')
 t=t.replace(/\\[([^\\]]+)\\]\\((https?:\\/\\/[^)\\s]+)\\)/g,'<a href="$2" target=_blank rel=noopener>$1</a>')
 t=t.replace(/(?:^[-*] .+(?:\\n|$))+/gm,function(bl){return '<ul>'+bl.trim().split(/\\n/).map(function(l){return '<li>'+l.replace(/^[-*] /,'')+'</li>'}).join('')+'</ul>'})
 t=t.replace(/(?:^\\d+\\. .+(?:\\n|$))+/gm,function(bl){return '<ol>'+bl.trim().split(/\\n/).map(function(l){return '<li>'+l.replace(/^\\d+\\. /,'')+'</li>'}).join('')+'</ol>'})
 t=t.split(/\\n{2,}/).map(function(x){x=x.trim();if(!x)return '';if(/^<(h\\d|ul|ol|pre)/.test(x))return x;return '<p>'+x.replace(/\\n/g,'<br>')+'</p>'}).join('')
 return t.replace(/\\x01(\\d+)\\x01/g,function(_,i){return store[+i]})
}
async function send(e){e.preventDefault();const text=q.value.trim();if(!text)return false
 if(text=='/移除'||text=='/remove'){clearAttach();q.value='';return false}
 add('u',text);q.value='';b.disabled=true;const wait=add('a','思考中…(本地生成,請稍候)')
 const payload=attached?{messages:[{role:'user',content:text}],augur_attach:attached}:{messages:[{role:'user',content:text}]}
 try{const r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},
   body:JSON.stringify(payload)})
  const j=await r.json();const m=j.choices?.[0]?.message?.content||'(無回覆)';const g=j.augur_guard||{}
  var parts=m.split('\\n---\\n').map(function(s){return s.trim()}).filter(function(s){return s&&s.indexOf('[augur-guard]')!==0})
  wait._bubble.innerHTML=mdToHtml(parts.join('\\n\\n'))
  const gd=document.createElement('div');gd.className='g '+(g.pass?'pass':'fail')
  gd.textContent='[guard] '+(g.pass?'通過':'攔下(改誠實句)')+' · 引文 '+(g.citations??'?')+' · issues '+(g.issues?.length??0)
  wait.appendChild(gd)
 }catch(err){wait._bubble.textContent='錯誤:'+err}
 b.disabled=false;q.focus();return false}
var attached=null,_pk='A'
function togglePlus(){var m=document.getElementById('plusmenu');m.style.display=m.style.display=='block'?'none':'block'}
function pick(kind){_pk='A';document.getElementById('plusmenu').style.display='none';document.getElementById(kind=='folder'?'dpick':'fpick').click()}
function pickB(kind){_pk='B';document.getElementById('plusmenu').style.display='none';document.getElementById(kind=='folder'?'dpick':'fpick').click()}
document.getElementById('fpick').onchange=function(){handleFiles(this.files);this.value=''}
document.getElementById('dpick').onchange=function(){handleFiles(this.files);this.value=''}
function handleFiles(files){if(_pk=='B')doAttach(files);else doIngest(files)}
function clearAttach(){if(attached){attached=null;updateChip();add('a','已解除附加。')}}
function updateChip(){var c=document.getElementById('chip');if(attached){c.style.display='block';c.textContent='📎 附加中(只問這次):'+attached.title+' — 點此移除'}else{c.style.display='none'}}
async function doIngest(files){
 if(!files||!files.length)return
 var lic=document.getElementById('inlic').value
 add('u','【附加入庫】'+files.length+' 檔 · 授權 '+lic)
 var wait=add('a','解析入庫中…(本地處理,大夾請耐心)')
 var fd=new FormData();fd.append('license',lic);fd.append('access_scope','local_private')
 for(var i=0;i<files.length;i++)fd.append('file',files[i],files[i].webkitRelativePath||files[i].name)
 try{var r=await fetch('/ingest',{method:'POST',body:fd});wait._bubble.textContent=await r.text()}
 catch(e){wait._bubble.textContent='入庫失敗:'+e}
}
async function doAttach(files){
 if(!files||!files.length)return
 var wait=add('a','讀取附加檔案…(本地解析,只問這次、不入庫)')
 var fd=new FormData();for(var i=0;i<files.length;i++)fd.append('file',files[i],files[i].webkitRelativePath||files[i].name)
 try{var r=await fetch('/attach',{method:'POST',body:fd});var j=await r.json()
  if(!j.ok){wait._bubble.textContent='附加失敗:'+(j.error||'無法解析');return}
  attached={title:j.title,text:j.text};updateChip()
  wait._bubble.textContent='📎 已附加:'+j.title+'('+j.chars+' 字'+(j.truncated?'、過長已截斷':'')+',只問這次)。之後提問只根據這份檔回答;點上方標籤或輸入 /移除 可解除。'
 }catch(e){wait._bubble.textContent='附加失敗:'+e}
}
</script></body></html>"""


class H(BaseHTTPRequestHandler):
    advisor = ADVISOR

    def log_message(self, *a):
        pass

    def _token(self):
        for kv in self.headers.get("Cookie", "").split(";"):
            if kv.strip().startswith("sid="):
                return kv.strip()[4:]
        return None

    def _html(self, html, code=200, cookie=None):
        body = html.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?")[0].rstrip("/")
        if path == "/logout":
            identity.revoke_session(self._token())
            return self._html(LOGIN_PAGE.replace("__MSG__", "<p style=color:#7d8590>已登出</p>"),
                              cookie="sid=; Max-Age=0; Path=/")
        if identity.verify_session(self._token()) is None:          # 未登入 → 登入頁(RBAC P4)
            return self._html(LOGIN_PAGE.replace("__MSG__", ""))
        self._html(PAGE)

    def _reply(self, content):
        out = json.dumps({"choices": [{"message": {"content": content}}],
                          "augur_guard": {"pass": True, "issues": [], "citations": 0}}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(out)))
        self.end_headers()
        self.wfile.write(out)

    def _plain(self, s):
        out = s.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(out)))
        self.end_headers()
        self.wfile.write(out)

    def _ingest(self):
        """+ 按鈕附加入庫(Mode A):multipart 落暫存夾(webupload)→ acquire_local_files 逐字入庫。
        治權:license 受 DB CHECK 白名單硬擋;access_scope=local_private(不入對外對話池,拍板P2)。"""
        ctype = self.headers.get("Content-Type", "")
        n = int(self.headers.get("Content-Length") or 0)
        if "multipart/form-data" not in ctype or "boundary=" not in ctype:
            return self._plain("需 multipart/form-data")
        if n > webupload.MAX_UPLOAD:
            return self._plain(f"上傳過大(上限 {webupload.MAX_UPLOAD // 1024 // 1024}MB)")
        boundary = ctype.split("boundary=", 1)[1].strip().strip('"')
        fields, files = webupload.parse_multipart(self.rfile.read(n), boundary)
        lic = (fields.get("license") or "").strip()
        scope = (fields.get("access_scope") or "local_private").strip()
        if lic not in webupload.LICENSES:
            return self._plain("license 非白名單(DB 硬擋只准公開授權 public_domain/cc-*)")
        if scope not in webupload.SCOPES:
            scope = "local_private"
        if not files:
            return self._plain("無檔案(請選含檔案的資料夾)")
        r = webupload.save_upload(files)
        if not r["saved"]:
            return self._plain(f"無有效檔案(過大跳 {r['big']}、非法名跳 {r['bad']})")
        cmd = [sys.executable, os.path.join(_ROOT, "scripts", "acquire_local_files.py"),
               "--dir", r["updir"], "--license", lic, "--access-scope", scope, "--domain", "local"]
        out = subprocess.run(cmd, cwd=_ROOT, capture_output=True, text=True, timeout=600).stdout
        return self._plain(f"【附加入庫完成】存檔 {r['saved']}(過大跳 {r['big']}、非法名跳 {r['bad']})、"
                           f"授權 {lic}\n\n{out}")

    def _json(self, obj):
        out = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(out)))
        self.end_headers()
        self.wfile.write(out)

    def _attach(self):
        """Mode B 附加檔:抽逐字文字回傳前端(不入庫、僅本次對話;webupload.extract_texts)。
        治權:不落地不入庫、access 不擴;僅本回合當引文語料交 advisor,guard 對附加檔逐字比對。"""
        ctype = self.headers.get("Content-Type", "")
        n = int(self.headers.get("Content-Length") or 0)
        if "multipart/form-data" not in ctype or "boundary=" not in ctype:
            return self._json({"ok": False, "error": "需 multipart/form-data"})
        if n > webupload.MAX_UPLOAD:
            return self._json({"ok": False, "error": f"上傳過大(上限 {webupload.MAX_UPLOAD // 1024 // 1024}MB)"})
        boundary = ctype.split("boundary=", 1)[1].strip().strip('"')
        _fields, files = webupload.parse_multipart(self.rfile.read(n), boundary)
        if not files:
            return self._json({"ok": False, "error": "無檔案"})
        text, meta = webupload.extract_texts(files)
        if not (text or "").strip():
            return self._json({"ok": False, "error": "無法抽取文字(掃描檔/加密/未支援格式)"})
        cap = 400000
        truncated = len(text) > cap
        text = text[:cap]
        title = (f"資料夾 {meta['parsed']} 檔" if meta["parsed"] > 1
                 else (meta["titles"][0] if meta["titles"] else "附加文件"))
        return self._json({"ok": True, "title": title, "text": text, "chars": len(text),
                           "parsed": meta["parsed"], "skipped": meta["skipped"], "truncated": truncated})

    def do_POST(self):
        path = self.path.rstrip("/")
        if path == "/login":
            n = int(self.headers.get("Content-Length") or 0)
            form = parse_qs(self.rfile.read(n).decode("utf-8", "replace")) if n else {}
            u = identity.authenticate((form.get("username", [""])[0]).strip(), form.get("pw", [""])[0])
            if u:
                tok = identity.issue_session(u["user_id"], client_note="chat")
                self.send_response(303)
                self.send_header("Location", "/")
                self.send_header("Set-Cookie", f"sid={tok}; HttpOnly; SameSite=Strict; Path=/")
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            return self._html(LOGIN_PAGE.replace("__MSG__", "<p style=color:#d29922>帳號或密碼錯誤</p>"))
        if identity.verify_session(self._token()) is None:      # /chat//ingest//attach 皆須登入(RBAC P4;無 public fallback)
            return self._reply("請重新登入(工作階段已失效或未登入;重新整理頁面登入)")
        if path == "/ingest":
            return self._ingest()
        if path == "/attach":
            return self._attach()
        n = int(self.headers.get("Content-Length", 0))
        req = json.loads(self.rfile.read(n) or b"{}")
        msgs = req.get("messages", [])
        last = (msgs[-1].get("content", "") if msgs else "").strip()
        if last.startswith("+"):
            # +資料夾語法(計畫 P4):dry-run 掃描預覽(不寫、不需 license)→ 導向 admin 後台授權入庫。
            # 治權:chat 不逕自入庫版權未明檔;實際入庫走 admin 後台(P3)聲明 license(DB CHECK 硬擋)。
            safe = _safe_dir(last[1:])
            if not safe:
                return self._reply("路徑非法或不存在(限 $HOME 下之現有資料夾、拒 ../ 逃逸)。用法:+/home/hugo/docs")
            cmd = [sys.executable, os.path.join(_ROOT, "scripts", "acquire_local_files.py"),
                   "--dir", safe, "--license", "public_domain", "--dry-run"]
            try:
                sc = subprocess.run(cmd, cwd=_ROOT, capture_output=True, text=True, timeout=120).stdout
            except Exception as e:
                sc = f"掃描失敗:{e}"
            return self._reply(f"【+資料夾 dry-run 掃描】{safe}\n\n{sc}\n"
                               "── 此為預覽(未入庫)。實際入庫請至 admin 後台(:8500)聲明 license(DB CHECK 硬擋只准公開授權檔)。")
        fwd = {"model": "augur-advisor", "messages": msgs}
        att = req.get("augur_attach")
        if isinstance(att, dict) and (att.get("text") or "").strip():
            fwd["augur_attach"] = {"title": att.get("title") or "附加文件", "text": att["text"]}
        payload = json.dumps(fwd).encode()
        headers = {"Content-Type": "application/json"}
        if _SECRET:                                             # P4:傳身分給殼(殼驗機密後自查 session 自 resolve scope,§4.3)
            headers["X-Augur-Internal"] = _SECRET
            headers["X-Augur-Session"] = self._token() or ""
        try:
            r = urllib.request.Request(self.advisor + "/v1/chat/completions", payload, headers)
            out = urllib.request.urlopen(r, timeout=600).read()
        except Exception as e:
            out = json.dumps({"choices": [{"message": {"content": f"advisor 殼錯誤:{e}"}}],
                              "augur_guard": {"pass": False, "issues": [str(e)]}}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(out)))
        self.end_headers()
        self.wfile.write(out)


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--port", type=int, default=8090)
    ap.add_argument("--advisor", default=ADVISOR)
    ap.add_argument("-h", "--help", action="store_true")
    a, _ = ap.parse_known_args()
    if a.help:
        print(__doc__)
        return
    H.advisor = a.advisor
    print(f"誠實博學的我 · 對話 UI 起於 http://127.0.0.1:{a.port}(proxy → {a.advisor};Ctrl-C 停)", flush=True)
    ThreadingHTTPServer(("127.0.0.1", a.port), H).serve_forever()


if __name__ == "__main__":
    main()
