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
import html
import json
import os
import subprocess
import sys
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

import _bootstrap  # noqa: F401  個別可執行(#29a)
from augur.core import db
from augur.knowledge import webupload, identity   # identity 匯入鏈載入 .env(取 AUGUR_INTERNAL_SECRET)
from augur.advisor import chat_history            # 對話歷史 DB(owner 收窄、住 advisor=FORBIDDEN 前綴)

ADVISOR = "http://127.0.0.1:8399"
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SECRET = os.environ.get("AUGUR_INTERNAL_SECRET")   # 前台↔殼共享機密(P4;送 X-Augur-Internal)

LOGIN_PAGE = """<!doctype html><html lang=zh-Hant><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1"><title>誠實博學的我 · 登入</title>
<style>body{margin:0;font-family:ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans TC",sans-serif;background:#faf9f5;color:#1f1e1d;display:flex;min-height:100vh;align-items:center;justify-content:center}
.card{width:360px;padding:38px 34px;background:#fff;border:1px solid #e9e6dc;border-radius:18px;box-shadow:0 6px 28px rgba(0,0,0,.05)}
.star{color:#d97757;font-size:27px;text-align:center}
h2{margin:10px 0 3px;font-size:20px;text-align:center;font-weight:600}
.sub{color:#73726c;font-size:13px;margin:0 0 22px;text-align:center}
input{width:100%;padding:12px 14px;margin:6px 0;background:#faf9f5;border:1px solid #dcd8cc;color:#1f1e1d;border-radius:10px;font-size:15px}
input:focus{outline:0;border-color:#d97757}
button{width:100%;padding:12px;margin-top:12px;background:#d97757;color:#fff;border:0;border-radius:10px;font-size:15px;cursor:pointer;font-weight:500}
button:hover{background:#c15f3f}</style></head>
<body><div class=card>
<div class=star>✻</div><h2>誠實博學的我</h2>
<p class=sub>登入以依你的權限檢索知識</p>__MSG__
<form method=post action=/login><input name=username placeholder="帳號" autofocus>
<input type=password name=pw placeholder="密碼">
<button>登入</button></form></div></body></html>"""


def _safe_dir(path):
    """+資料夾圍欄:realpath 須在 $HOME 下(拒 ../ 逃逸);回 realpath 或 None。"""
    home = os.path.realpath(os.path.expanduser("~"))
    rp = os.path.realpath(os.path.expanduser((path or "").strip()))
    return rp if (rp == home or rp.startswith(home + os.sep)) and os.path.isdir(rp) else None

PAGE = """<!doctype html><html lang=zh-Hant><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>誠實博學的我 · augur</title><style>
:root{color-scheme:light;--bg:#faf9f5;--sidebar:#f0eee6;--surface:#fff;--bubble:#f0eee6;--text:#1f1e1d;--muted:#73726c;
 --border:#e9e6dc;--border-strong:#dcd8cc;--accent:#d97757;--accent-hover:#c15f3f;--accent-soft:#f5e5dd;--hover:#e7e4d8;--code:#f0eee6}
*{box-sizing:border-box}
html,body{height:100%}
body{margin:0;font-family:ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans TC",sans-serif;
 background:var(--bg);color:var(--text);font-size:15px;line-height:1.65;-webkit-font-smoothing:antialiased}
.app{display:flex;height:100vh;overflow:hidden}
.sidebar{width:260px;flex-shrink:0;background:var(--sidebar);border-right:1px solid var(--border);display:flex;flex-direction:column;padding:12px}
.brand{display:flex;align-items:center;gap:9px;padding:8px 8px 14px;font-weight:600;font-size:15px}
.brand .s{color:var(--accent);font-size:19px}
.newchat{display:flex;align-items:center;gap:9px;width:100%;padding:10px 12px;border:0;border-radius:10px;background:transparent;color:var(--text);font-size:14px;cursor:pointer;font-family:inherit;text-align:left}
.newchat:hover{background:var(--hover)}
.newchat .p{color:var(--accent);font-size:17px;font-weight:600;line-height:1}
.side-note{padding:14px 12px;font-size:11.5px;color:var(--muted);line-height:1.55}
.spacer{flex:1}
.foot{border-top:1px solid var(--border);padding-top:8px}
.foot a{display:block;padding:9px 12px;border-radius:8px;color:var(--muted);text-decoration:none;font-size:13px}
.foot a:hover{background:var(--hover);color:var(--text)}
.modes{display:flex;flex-direction:column;gap:2px;margin-top:10px}
.mode{width:100%;padding:8px 12px;border:0;border-radius:9px;background:transparent;color:#4a4842;font-size:13.5px;cursor:pointer;font-family:inherit;text-align:left}
.mode:hover{background:var(--hover)}
.mode.active{background:var(--surface);color:var(--text);font-weight:600;box-shadow:0 1px 3px rgba(0,0,0,.05)}
.svc{padding:6px 12px 10px;font-size:11px;color:var(--muted);line-height:1.95}
.svc .d{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:7px;background:#cdc7b8;vertical-align:middle}
.svc .d.on{background:#5f8a5a}.svc .d.off{background:#c15f3f}
.modenote{max-width:740px;margin:0 auto 16px;font-size:12px;color:#8a4a30;background:var(--accent-soft);border:1px solid #eccdc0;border-radius:10px;padding:9px 13px}
.recents{flex:1;min-height:0;overflow-y:auto;margin-top:12px}
.rec-h{font-size:11px;color:var(--muted);padding:6px 12px 2px;text-transform:uppercase;letter-spacing:.03em}
.rec-row{display:flex;align-items:center;border-radius:8px;position:relative}
.rec-row:hover{background:var(--hover)}
.rec-row.active{background:var(--surface);box-shadow:0 1px 3px rgba(0,0,0,.05)}
.rec{flex:1;min-width:0;text-align:left;padding:7px 6px 7px 12px;border:0;border-radius:8px;background:transparent;color:#57554e;font-size:13px;cursor:pointer;font-family:inherit;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.rec-row.active .rec{color:var(--text);font-weight:600}
.kebab{flex-shrink:0;width:26px;height:26px;border:0;border-radius:6px;background:transparent;color:var(--muted);cursor:pointer;font-size:15px;line-height:1;opacity:0;transition:opacity .12s;margin-right:4px}
.rec-row:hover .kebab{opacity:1}
.kebab:hover{background:var(--border-strong);color:var(--text)}
.recmenu{position:fixed;background:var(--surface);border:1px solid var(--border-strong);border-radius:10px;box-shadow:0 6px 22px rgba(0,0,0,.12);padding:5px;z-index:40;min-width:158px}
.recmenu .mi{padding:8px 12px;border-radius:7px;font-size:13px;cursor:pointer;color:var(--text);white-space:nowrap}
.recmenu .mi:hover{background:var(--hover)}
.search{width:100%;margin-top:8px;padding:8px 12px;border:1px solid var(--border-strong);border-radius:9px;background:var(--surface);color:var(--text);font-size:13px;font-family:inherit}
.search:focus{outline:0;border-color:var(--accent)}
.toast{position:fixed;right:20px;bottom:20px;background:var(--surface);border:1px solid var(--border-strong);border-radius:10px;padding:10px 16px;font-size:13px;color:var(--text);box-shadow:0 4px 18px rgba(0,0,0,.1);opacity:0;transform:translateY(8px);transition:.2s;z-index:50}
.toast.show{opacity:1;transform:none}
.actions{display:flex;gap:4px;margin-top:6px;opacity:0;transition:opacity .15s}
.msg:hover .actions{opacity:1}
.msg.u .actions{justify-content:flex-end;padding-right:2px}
.act{background:transparent;border:0;color:var(--muted);font-size:12px;padding:3px 8px;border-radius:6px;cursor:pointer;font-family:inherit}
.act:hover{background:var(--hover);color:var(--text)}
@media(hover:none){.actions{opacity:1}}
.codewrap{margin:0 0 12px}
.codebar{display:flex;justify-content:space-between;align-items:center;background:#1f1e1d;color:#8a8a80;padding:5px 12px;font-size:12px;border-radius:10px 10px 0 0}
.codecopy{background:transparent;border:0;color:#b8b3a8;font-size:12px;cursor:pointer;font-family:inherit}
.codecopy:hover{color:#fff}
.codewrap pre.cb{border-radius:0 0 10px 10px;margin:0}
.chips{margin-top:18px;display:flex;flex-wrap:wrap;justify-content:center;gap:8px}
.chip{padding:8px 14px;border:1px solid var(--border-strong);border-radius:16px;background:var(--surface);font-size:13px;cursor:pointer;color:var(--text);font-family:inherit}
.chip:hover{background:var(--bubble)}
.errcard{background:#fbeaea;border:1px solid #e5c4c0;border-radius:10px;padding:11px 14px;color:#8a3a2f;display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.errcard .retry{background:#fff;border:1px solid #e5c4c0;border-radius:7px;padding:4px 12px;color:#8a3a2f;cursor:pointer;font-size:13px;font-family:inherit}
.dots{display:inline-flex;gap:5px;padding:5px 0}
.dots i{width:7px;height:7px;border-radius:50%;background:var(--muted);display:inline-block;animation:dpulse 1.2s infinite ease-in-out}
.dots i:nth-child(2){animation-delay:.2s}.dots i:nth-child(3){animation-delay:.4s}
@keyframes dpulse{0%,60%,100%{opacity:.3}30%{opacity:1}}
#b.stop{background:#8a8580}#b.stop:hover{background:#736f6a}
.modelpill{flex-shrink:0;font-size:12px;color:var(--muted);padding:4px 6px;white-space:nowrap;align-self:center}
.slashmenu{display:none;max-width:740px;margin:0 auto 8px;background:var(--surface);border:1px solid var(--border-strong);border-radius:14px;padding:8px;box-shadow:0 4px 18px rgba(0,0,0,.06)}
.slashmenu .si{padding:8px 12px;border-radius:8px;font-size:13px;cursor:pointer;color:var(--text)}
.slashmenu .si:hover{background:var(--hover)}
.slashmenu .si b{color:var(--accent);font-weight:600}
.scrim{position:fixed;inset:0;background:rgba(0,0,0,.4);display:none;z-index:15}
.scrim.show{display:block}
#hamburger{display:none;position:absolute;left:12px;top:12px;z-index:10;width:34px;height:34px;border:1px solid var(--border);border-radius:8px;background:var(--surface);color:var(--text);font-size:16px;cursor:pointer;align-items:center;justify-content:center}
.cmdk-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.35);z-index:60;align-items:flex-start;justify-content:center}
.cmdk-box{margin-top:12vh;width:min(560px,92vw);background:var(--surface);border:1px solid var(--border-strong);border-radius:16px;box-shadow:0 12px 40px rgba(0,0,0,.2);overflow:hidden}
#cmdkq{width:100%;padding:16px 18px;border:0;border-bottom:1px solid var(--border);background:transparent;color:var(--text);font-size:15px;font-family:inherit;outline:0}
#cmdklist{max-height:50vh;overflow-y:auto;padding:6px}
.cmdk-item{padding:10px 14px;border-radius:9px;font-size:14px;cursor:pointer;color:var(--text);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.cmdk-item:hover{background:var(--hover)}
@media(max-width:768px){
 .sidebar{position:fixed;left:0;top:0;height:100vh;transform:translateX(-100%);transition:transform .22s ease;z-index:20}
 .sidebar.open{transform:none}
 #hamburger{display:flex}
 #log{padding-top:56px}
}
.account{display:flex;align-items:center;gap:9px;padding:9px 6px 2px;margin-top:6px;border-top:1px solid var(--border)}
.avatar{width:30px;height:30px;border-radius:50%;background:var(--accent);color:#fff;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:600;flex-shrink:0}
.acct{flex:1;min-width:0}
.acct-name{font-size:13px;font-weight:600;color:var(--text);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.acct-sub{font-size:11px;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.logout{color:var(--muted);text-decoration:none;font-size:16px;padding:4px;flex-shrink:0;transition:color .12s}
.logout:hover{color:var(--text)}
.main{flex:1;display:flex;flex-direction:column;min-width:0;min-height:0;position:relative}
#log{flex:1;min-height:0;overflow-y:auto;overscroll-behavior:contain;padding:26px 20px 8px}
#jump{position:absolute;left:50%;bottom:98px;transform:translateX(-50%);width:34px;height:34px;border-radius:50%;background:var(--surface);border:1px solid var(--border-strong);color:var(--muted);box-shadow:0 2px 10px rgba(0,0,0,.1);cursor:pointer;opacity:0;pointer-events:none;transition:opacity .18s;display:flex;align-items:center;justify-content:center;z-index:6;font-size:16px}
#greet{max-width:660px;margin:13vh auto 0;text-align:center;padding:0 20px}
#greet .gs{color:var(--accent);font-size:30px}
#greet h1{font-family:Georgia,"Songti TC","Noto Serif TC",serif;font-weight:500;font-size:29px;margin:14px 0 8px;color:var(--text)}
#greet p{color:var(--muted);font-size:14px;margin:0}
.msg{max-width:740px;margin:0 auto 24px;line-height:1.7}
.msg.u{display:flex;justify-content:flex-end}
.msg.u .bubble{background:var(--bubble);border-radius:16px;padding:11px 16px;max-width:82%;white-space:pre-wrap}
.msg.a{position:relative;padding-left:38px}
.msg.a::before{content:"✻";position:absolute;left:0;top:1px;color:var(--accent);font-size:16px;width:27px;height:27px;display:flex;align-items:center;justify-content:center;background:var(--accent-soft);border-radius:8px}
.role{display:none}
.msg.a .bubble{font-family:"Tiempos Text",Georgia,"Songti TC","Noto Serif TC",serif;font-size:15.5px}
.msg.a .bubble code,.msg.a .bubble pre.cb,.msg.a .bubble pre.cb code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
.bubble p{margin:0 0 12px}.bubble p:last-child{margin-bottom:0}
.bubble h2,.bubble h3,.bubble h4{margin:18px 0 8px;line-height:1.3;font-weight:600}
.bubble h2{font-size:1.3em}.bubble h3{font-size:1.14em}.bubble h4{font-size:1.02em}
.bubble ul,.bubble ol{margin:8px 0;padding-left:24px}.bubble li{margin:5px 0}
.bubble code{background:var(--code);border:1px solid var(--border-strong);border-radius:5px;padding:1px 5px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.88em}
.bubble pre.cb{background:#2b2a27;color:#f0eee6;border-radius:10px;padding:14px 16px;overflow:auto;font-family:ui-monospace,monospace;font-size:.85em;line-height:1.5;white-space:pre}
.bubble pre.cb code{background:none;border:0;padding:0;color:inherit}
.bubble a{color:var(--accent)}.bubble b{color:var(--text);font-weight:600}
.g{font-size:12px;color:var(--muted);margin-top:10px}
.g.pass{color:#5f8a5a}.g.fail{color:#b5793a}
#bar{flex-shrink:0;padding:8px 20px 18px;background:linear-gradient(180deg,rgba(250,249,245,0),var(--bg) 32%)}
#chip{display:none;max-width:740px;margin:0 auto 8px;background:var(--accent-soft);border:1px solid #eccdc0;border-radius:10px;padding:9px 12px;font-size:13px;cursor:pointer;color:#8a4a30}
#plusmenu{display:none;max-width:740px;margin:0 auto 8px;background:var(--surface);border:1px solid var(--border-strong);border-radius:16px;padding:14px;box-shadow:0 4px 18px rgba(0,0,0,.06)}
#plusmenu .hint{font-size:12px;color:var(--muted);margin:2px 0 6px}
#plusmenu button{margin:5px 6px 0 0;background:var(--bg);color:var(--text);font-size:13px;padding:8px 12px;border:1px solid var(--border-strong);border-radius:9px;cursor:pointer}
#plusmenu button:hover{background:var(--bubble)}
#plusmenu select{padding:7px;background:var(--bg);color:var(--text);border:1px solid var(--border-strong);border-radius:8px}
.composer{max-width:740px;margin:0 auto;background:var(--surface);border:1px solid var(--border-strong);border-radius:24px;padding:7px 8px;display:flex;align-items:flex-end;gap:8px;box-shadow:0 2px 14px rgba(0,0,0,.05)}
.composer:focus-within{border-color:#cdc7b8;box-shadow:0 2px 18px rgba(0,0,0,.08)}
#plusbtn{flex-shrink:0;width:36px;height:36px;border:1px solid var(--border-strong);border-radius:50%;background:transparent;color:var(--muted);font-size:19px;cursor:pointer;display:flex;align-items:center;justify-content:center}
#plusbtn:hover{background:var(--bubble);color:var(--text)}
#q{flex:1;border:0;background:transparent;color:var(--text);font-size:15px;padding:8px 4px;resize:none;outline:0;font-family:inherit;max-height:180px;line-height:1.5}
#b{flex-shrink:0;width:36px;height:36px;border:0;border-radius:50%;background:var(--accent);color:#fff;font-size:17px;cursor:pointer;display:flex;align-items:center;justify-content:center}
#b:hover{background:var(--accent-hover)}
#b:disabled{background:#d8d3c6;cursor:default}
.foot-note{max-width:740px;margin:9px auto 0;text-align:center;font-size:11px;color:var(--muted)}
.newchat,.mode,.rec,#plusbtn,#b,.foot a,#plusmenu button{transition:background .12s,color .12s,border-color .12s}
button:focus-visible,#q:focus-visible,.mode:focus-visible,.rec:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
</style></head><body>
<div class=app>
<aside class=sidebar>
 <div class=brand><span class=s>✻</span>augur</div>
 <button class=newchat onclick="newSession()"><span class=p>＋</span>新對話</button>
 <input id=search class=search placeholder="搜尋對話…" oninput="SEARCHQ=this.value;renderRecents()" autocomplete=off>
 <div class=modes>
  <button class="mode active" onclick="setMode('chat',this)">對話</button>
  <button class="mode" onclick="setMode('cowork',this)">協作</button>
  <button class="mode" onclick="setMode('code',this)">程式</button>
 </div>
 <div class=recents id=recents></div>
 <div class=foot>
  <div id=svc class=svc><span class="d"></span>PostgreSQL<br><span class="d"></span>顧問殼<br><span class="d"></span>Ollama</div>
  <a href="http://localhost:8500" target=_blank>知識控制台 ↗</a>
  <div class=account>
   <div class=avatar>__INITIAL__</div>
   <div class=acct><div class=acct-name>__USER__</div><div class=acct-sub>__MODEL__ · __ROLE__</div></div>
   <a href="/logout" class=logout title="登出">⏻</a>
  </div>
 </div>
</aside>
<main class=main>
<button id=hamburger onclick="toggleSide()" aria-label="選單" title="選單">☰</button>
<div id=log><div id=greet><div class=gs>✻</div><h1>今天想聊什麼?</h1><p>問我太陽能材料、能源材料、太陽能產業的 know-how</p></div></div>
<button id=jump title="回到最新" onclick="jumpBottom()">↓</button>
<div id=bar>
<div id=chip onclick="clearAttach()"></div>
<div id=plusmenu>
 <div class=hint>A · 入知識庫(永久保存、之後可被引用;需公開授權,DB 硬擋只准 public_domain/cc-*)</div>
 授權 <select id=inlic><option>public_domain</option><option>cc-by</option><option>cc-by-sa</option><option>cc0</option></select>
 <button type=button onclick="pick('file')">📎 選檔案入庫</button>
 <button type=button onclick="pick('folder')">📁 選資料夾入庫</button>
 <div class=hint style="margin-top:10px">B · 只問這次(不入庫、只當本次對話的文件助讀)</div>
 <button type=button onclick="pickB('file')">📄 選檔案 · 只問這次</button>
 <button type=button onclick="pickB('folder')">📁 選資料夾 · 只問這次</button>
</div>
<div id=slashmenu class=slashmenu>
 <div class=si onclick="slashPick('/移除')"><b>/移除</b> — 解除附加檔</div>
 <div class=si onclick="slashPick('/remove')"><b>/remove</b> — 解除附加檔（英文別名）</div>
 <div class=si onclick="slashPick('+')"><b>+資料夾路徑</b> — 掃描預覽（dry-run、不入庫）</div>
</div>
<form class=composer onsubmit="return send(event)">
<button id=plusbtn type=button onclick="togglePlus()" title="附加檔案/資料夾">＋</button>
<textarea id=q rows=1 placeholder="輸入訊息…" autocomplete=off></textarea>
<span class=modelpill title="目前本地模型">__MODEL__</span>
<button id=b type=submit title="送出">↑</button></form>
<div class=foot-note>誠實博學的我可能會出錯，請查證重要資訊。</div>
</div>
</main>
</div>
<div id=scrim class=scrim onclick="toggleSide()"></div>
<div id=cmdk class=cmdk-overlay onclick="if(event.target===this)closeCmdk()"><div class=cmdk-box><input id=cmdkq placeholder="搜尋對話…" autocomplete=off oninput="cmdkRender(this.value)" onkeydown="if(event.key==='Enter'){var f=document.querySelector('#cmdklist .cmdk-item');if(f)f.click()}"><div id=cmdklist></div></div></div>
<input type=file id=fpick style="display:none">
<input type=file id=dpick webkitdirectory directory multiple style="display:none">
<script>
const log=document.getElementById('log'),q=document.getElementById('q'),b=document.getElementById('b'),jump=document.getElementById('jump')
var pinned=true
function atBottom(){return log.scrollHeight-log.scrollTop-log.clientHeight<100}
function toggleJump(){var on=!atBottom();jump.style.opacity=on?'1':'0';jump.style.pointerEvents=on?'auto':'none'}
function jumpBottom(){log.scrollTo({top:log.scrollHeight,behavior:'smooth'});pinned=true;setTimeout(toggleJump,320)}
log.addEventListener('scroll',function(){pinned=atBottom();toggleJump()})
log.addEventListener('click',function(e){if(e.target&&e.target.classList&&e.target.classList.contains('codecopy')){var w=e.target.closest('.codewrap');var code=w&&w.querySelector('pre code');if(code){navigator.clipboard.writeText(code.textContent||'');e.target.textContent='已複製 ✓';setTimeout(function(){e.target.textContent='複製'},1200)}}})
var MODE='chat'
var GREET={chat:['今天想聊什麼?','問我太陽能材料、能源材料、太陽能產業的 know-how'],
 cowork:['一起完成什麼任務?','協作情境 · 目前沿用顧問後端,專屬協作 agent 建置中'],
 code:['要處理哪段程式?','程式情境 · 目前沿用顧問後端,專屬 code agent 建置中']}
var SESSIONS=[]   // DB session 快取:{id,mode,title,starred,ts}(msgs 按需經 /api/messages 載;歷史存 PostgreSQL、owner 收窄)
var CURid=null
async function fetchSessions(){try{var j=await (await fetch('/api/sessions')).json();SESSIONS=j.sessions||[]}catch(e){SESSIONS=[]}renderRecents()}
async function ensureSession(){if(CURid!=null)return CURid;try{var j=await (await fetch('/api/session/new',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mode:MODE})})).json();if(j.id!=null){CURid=j.id;SESSIONS.unshift({id:CURid,mode:MODE,title:'新對話',starred:false,ts:Date.now()})}return CURid}catch(e){return null}}
async function recordMsg(role,content){var sid=await ensureSession();if(sid==null)return;var dbrole=(role==='u'||role==='user')?'user':'assistant'
 try{await fetch('/api/session/msg',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({sid:sid,role:dbrole,content:content})})}catch(e){}
 var s=SESSIONS.filter(function(x){return x.id===sid})[0]
 if(s){s.ts=Date.now();if(dbrole==='user'&&(!s.title||s.title==='新對話')){s.title=content.slice(0,24);fetch('/api/session/rename',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({sid:sid,title:s.title})}).catch(function(){})}}
 renderRecents()}
var CHIPS={chat:['鈣鈦礦太陽能電池的效率','TOPCon 電池的技術優勢','太陽能電池表面鈍化技術'],cowork:['幫我整理這份資料的重點','列出這個任務的步驟'],code:['解釋這段程式在做什麼','幫我找出可能的 bug']}
function chipClick(b){q.value=b.textContent;q.style.height='auto';q.style.height=Math.min(q.scrollHeight,180)+'px';q.focus()}
function greetHtml(){var g=GREET[MODE];var cs=(CHIPS[MODE]||[]).map(function(c){return '<button class=chip type=button onclick="chipClick(this)">'+c.replace(/&/g,'&amp;').replace(/</g,'&lt;')+'</button>'}).join('');return '<div id=greet><div class=gs>✻</div><h1>'+g[0]+'</h1><p>'+g[1]+'</p><div class=chips>'+cs+'</div></div>'}
function newSession(){CURid=null;log.innerHTML=greetHtml();attached=null;updateChip();q.value='';q.style.height='auto';renderRecents();q.focus()}
function setMode(m,btn){MODE=m;document.querySelectorAll('.mode').forEach(function(b){b.classList.remove('active')});btn.classList.add('active');newSession()}
var SEARCHQ=''
function toast(msg){var t=document.createElement('div');t.className='toast';t.textContent=msg;document.body.appendChild(t);requestAnimationFrame(function(){t.classList.add('show')});setTimeout(function(){t.classList.remove('show');setTimeout(function(){t.remove()},250)},2400)}
function closeMenu(){var m=document.getElementById('recmenu');if(m)m.remove()}
function bucketOf(ts){var t0=new Date();t0.setHours(0,0,0,0);var d=t0.getTime();if(ts>=d)return '今天';if(ts>=d-864e5)return '昨天';if(ts>=d-6048e5)return '過去 7 天';if(ts>=d-2592e6)return '過去 30 天';var dt=new Date(ts);return dt.getFullYear()+' 年 '+(dt.getMonth()+1)+' 月'}
function apiSess(act,body){return fetch('/api/session/'+act,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}).catch(function(){})}
function recMenu(s,anchor){closeMenu();var m=document.createElement('div');m.id='recmenu';m.className='recmenu'
 var acts=[['重新命名',function(){var t=prompt('新標題',s.title);if(t!==null){s.title=t.trim()||s.title;apiSess('rename',{sid:s.id,title:s.title});renderRecents()}}],
  [s.starred?'取消加星':'加星',function(){s.starred=!s.starred;apiSess('star',{sid:s.id,starred:s.starred});renderRecents()}],
  ['複製為 Markdown',function(){fetch('/api/messages?sid='+encodeURIComponent(s.id)).then(function(r){return r.json()}).then(function(j){var md=(j.messages||[]).map(function(x){return (x.role==='user'?'**你**：':'**顧問**：')+'\\n'+x.content}).join('\\n\\n');navigator.clipboard.writeText(md);toast('已複製對話 Markdown')}).catch(function(){toast('複製失敗')})}],
  ['刪除',function(){if(confirm('刪除「'+s.title+'」?')){apiSess('del',{sid:s.id});SESSIONS=SESSIONS.filter(function(x){return x.id!==s.id});if(s.id===CURid){newSession()}else{renderRecents()}}}]]
 acts.forEach(function(p){var it=document.createElement('div');it.className='mi';it.textContent=p[0];it.onclick=function(ev){ev.stopPropagation();closeMenu();p[1]()};m.appendChild(it)})
 var r=anchor.getBoundingClientRect();m.style.left=Math.min(r.left,window.innerWidth-170)+'px';m.style.top=(r.bottom+4)+'px';document.body.appendChild(m)
 setTimeout(function(){document.addEventListener('click',closeMenu,{once:true})},0)}
function makeRec(s){var row=document.createElement('div');row.className='rec-row'+(s.id===CURid?' active':'')
 var btn=document.createElement('button');btn.className='rec';btn.textContent=(s.starred?'★ ':'')+s.title;btn.title=s.title;btn.onclick=function(){loadSession(s.id)}
 var kb=document.createElement('button');kb.className='kebab';kb.textContent='⋯';kb.setAttribute('aria-label','更多');kb.onclick=function(e){e.stopPropagation();recMenu(s,kb)}
 row.appendChild(btn);row.appendChild(kb);return row}
function renderRecents(){var el=document.getElementById('recents');if(!el)return;el.innerHTML=''
 var all=SESSIONS.filter(function(s){return s.mode===MODE})
 if(SEARCHQ){var qq=SEARCHQ.toLowerCase();all=all.filter(function(s){return (s.title||'').toLowerCase().indexOf(qq)>=0})}
 all.sort(function(a,b){return b.ts-a.ts})
 function section(label,list){if(!list.length)return;var h=document.createElement('div');h.className='rec-h';h.textContent=label;el.appendChild(h);list.forEach(function(s){el.appendChild(makeRec(s))})}
 if(SEARCHQ){section('搜尋結果',all);return}
 section('已加星',all.filter(function(s){return s.starred}))
 var buckets={},order=[];all.filter(function(s){return !s.starred}).forEach(function(s){var b=bucketOf(s.ts);if(!buckets[b]){buckets[b]=[];order.push(b)}buckets[b].push(s)})
 order.forEach(function(b){section(b,buckets[b])})}
async function loadSession(id){var s=SESSIONS.filter(function(x){return x.id===id})[0];if(!s)return;CURid=id;pinned=true;log.innerHTML=''
 try{var j=await (await fetch('/api/messages?sid='+encodeURIComponent(id))).json();(j.messages||[]).forEach(function(m){if(m.role==='user'){add('u',m.content)}else{var d=add('a','');d._bubble.innerHTML=mdToHtml(m.content)}})}catch(e){}
 renderRecents();log.scrollTop=log.scrollHeight;toggleJump()}
async function loadHealth(){try{var j=await (await fetch('/health')).json();var ds=document.querySelectorAll('#svc .d');if(ds.length>=3){ds[0].className='d '+(j.db?'on':'off');ds[1].className='d '+(j.advisor?'on':'off');ds[2].className='d '+(j.ollama?'on':'off')}}catch(e){}}
loadHealth();setInterval(loadHealth,15000);fetchSessions();
function toggleSide(){var sb=document.querySelector('.sidebar'),sc=document.getElementById('scrim');var open=sb.classList.toggle('open');if(sc)sc.classList.toggle('show',open)}
function closeCmdk(){document.getElementById('cmdk').style.display='none'}
function openCmdk(){var o=document.getElementById('cmdk');o.style.display='flex';var inp=document.getElementById('cmdkq');inp.value='';cmdkRender('');inp.focus()}
function cmdkRender(qv){var list=document.getElementById('cmdklist');list.innerHTML='';var lq=(qv||'').toLowerCase()
 var na=document.createElement('div');na.className='cmdk-item';na.textContent='＋ 新對話';na.onclick=function(){closeCmdk();newSession()};list.appendChild(na)
 var ss=SESSIONS.filter(function(s){return s.mode===MODE&&(!lq||s.title.toLowerCase().indexOf(lq)>=0)}).sort(function(a,b){return b.ts-a.ts}).slice(0,25)
 ss.forEach(function(s){var it=document.createElement('div');it.className='cmdk-item';it.textContent=(s.starred?'★ ':'')+s.title;it.onclick=function(){closeCmdk();loadSession(s.id)};list.appendChild(it)})}
document.addEventListener('keydown',function(e){
 if((e.metaKey||e.ctrlKey)&&(e.key==='k'||e.key==='K')){e.preventDefault();openCmdk();return}
 if((e.metaKey||e.ctrlKey)&&e.shiftKey&&(e.key==='o'||e.key==='O')){e.preventDefault();newSession();return}
 if(e.key==='Escape'){var o=document.getElementById('cmdk');if(o&&o.style.display==='flex'){closeCmdk();return}closeMenu();var pm=document.getElementById('plusmenu');if(pm)pm.style.display='none';var sm=document.getElementById('slashmenu');if(sm)sm.style.display='none';var sb=document.querySelector('.sidebar');if(sb&&sb.classList.contains('open'))toggleSide()}
})
q.addEventListener('input',function(){q.style.height='auto';q.style.height=Math.min(q.scrollHeight,180)+'px';slashMenu()})
q.addEventListener('keydown',function(e){if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send(e)}})
function add(cls,txt){var d=document.createElement('div');d.className='msg '+cls
 var role=document.createElement('div');role.className='role';role.textContent=(cls=='u'?'你':'誠實博學的我')
 var bub=document.createElement('div');bub.className='bubble';bub.textContent=txt
 var acts=document.createElement('div');acts.className='actions'
 var cp=document.createElement('button');cp.className='act';cp.textContent='複製';cp.setAttribute('aria-label','複製訊息');cp.onclick=function(){navigator.clipboard.writeText(bub.textContent||'').then(function(){cp.textContent='已複製';setTimeout(function(){cp.textContent='複製'},1200)})}
 acts.appendChild(cp)
 d.appendChild(role);d.appendChild(bub);d.appendChild(acts);log.appendChild(d);if(pinned)log.scrollTop=log.scrollHeight;d._bubble=bub;return d}
function esc(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}
function mdToHtml(t){
 var S=String.fromCharCode(1),store=[]
 function stash(h){store.push(h);return S+(store.length-1)+S}
 t=esc(t||'')
 t=t.replace(/```(\\w+)?\\n?([\\s\\S]*?)```/g,function(_,lang,c){return stash('<div class=codewrap><div class=codebar><span class=lang>'+(lang||'')+'</span><button class=codecopy type=button>複製</button></div><pre class=cb><code>'+c.replace(/\\n$/,'')+'</code></pre></div>')})
 t=t.replace(/`([^`\\n]+)`/g,function(_,c){return stash('<code>'+c+'</code>')})
 t=t.replace(/^#### (.+)$/gm,'<h4>$1</h4>').replace(/^### (.+)$/gm,'<h4>$1</h4>').replace(/^## (.+)$/gm,'<h3>$1</h3>').replace(/^# (.+)$/gm,'<h3>$1</h3>')
 t=t.replace(/\\*\\*([^*]+)\\*\\*/g,'<b>$1</b>')
 t=t.replace(/\\[([^\\]]+)\\]\\((https?:\\/\\/[^)\\s]+)\\)/g,'<a href="$2" target=_blank rel=noopener>$1</a>')
 t=t.replace(/(?:^[-*] .+(?:\\n|$))+/gm,function(bl){return '<ul>'+bl.trim().split(/\\n/).map(function(l){return '<li>'+l.replace(/^[-*] /,'')+'</li>'}).join('')+'</ul>'})
 t=t.replace(/(?:^\\d+\\. .+(?:\\n|$))+/gm,function(bl){return '<ol>'+bl.trim().split(/\\n/).map(function(l){return '<li>'+l.replace(/^\\d+\\. /,'')+'</li>'}).join('')+'</ol>'})
 t=t.split(/\\n{2,}/).map(function(x){x=x.trim();if(!x)return '';if(/^<(h\\d|ul|ol|pre)/.test(x))return x;return '<p>'+x.replace(/\\n/g,'<br>')+'</p>'}).join('')
 return t.replace(/\\x01(\\d+)\\x01/g,function(_,i){return store[+i]})
}
function renderStream(wait,full){var parts=full.split('\\n---\\n').map(function(s){return s.trim()}).filter(function(s){return s&&s.indexOf('[augur-guard]')!==0});wait._bubble.innerHTML=mdToHtml(parts.join('\\n\\n'));if(pinned)log.scrollTop=log.scrollHeight}
var CTRL=null
function setGen(on){if(on){b.textContent='■';b.title='停止生成';b.classList.add('stop')}else{b.textContent='↑';b.title='送出';b.classList.remove('stop');b.disabled=false}}
async function runGen(text,wait){
 wait._bubble.innerHTML='<span class=dots><i></i><i></i><i></i></span>'
 var og=wait.querySelector('.g');if(og)og.remove()
 var controller=new AbortController();CTRL=controller;setGen(true)
 const payload=attached?{messages:[{role:'user',content:text}],augur_attach:attached}:{messages:[{role:'user',content:text}]}
 try{const r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload),signal:controller.signal})
  const reader=r.body.getReader(),dec=new TextDecoder();var buf='',full='',first=true
  while(true){const rd=await reader.read();if(rd.done)break
   buf+=dec.decode(rd.value,{stream:true});var lines=buf.split('\\n');buf=lines.pop()
   for(var i=0;i<lines.length;i++){var ln=lines[i];if(ln.indexOf('data:')!==0)continue
    var dt=ln.slice(5).trim();if(!dt||dt==='[DONE]')continue
    try{var pj=JSON.parse(dt),dl=pj.choices&&pj.choices[0]&&pj.choices[0].delta&&pj.choices[0].delta.content
     if(dl){if(first){first=false;wait._bubble.textContent=''}full+=dl;renderStream(wait,full)}}catch(e){}}
  }
  var allp=full.split('\\n---\\n').map(function(s){return s.trim()})
  var gl=allp.filter(function(s){return s.indexOf('[augur-guard]')===0}).join(' ')
  var body=allp.filter(function(s){return s&&s.indexOf('[augur-guard]')!==0}).join('\\n\\n')||'(無回覆)'
  wait._bubble.innerHTML=mdToHtml(body)
  var pass=gl.indexOf('pass=true')>=0
  var gd=document.createElement('div');gd.className='g '+(pass?'pass':'fail');gd.textContent='[guard] '+(pass?'通過':'攔下(改誠實句)');wait.appendChild(gd)
  return body
 }catch(err){
  if(controller.signal.aborted){wait._bubble.innerHTML=full?mdToHtml(full):'(已停止)';return full||''}
  var ec=document.createElement('div');ec.className='errcard';ec.textContent='⚠ 連線或殼錯誤：'+String(err)+'（可重新輸入送出）';wait._bubble.innerHTML='';wait._bubble.appendChild(ec);return null
 }finally{if(CTRL===controller)CTRL=null;setGen(false)}
}
function addRetry(wait,text){var a=wait.querySelector('.actions');if(!a||wait._hasRetry)return;wait._hasRetry=1
 var rb=document.createElement('button');rb.className='act';rb.textContent='重試';rb.setAttribute('aria-label','重新生成')
 rb.onclick=function(){if(CTRL)return;runGen(text,wait)}   // 視覺重生;DB 保留原始訊息(重試不覆寫歷史)
 a.appendChild(rb)}
async function send(e){e.preventDefault()
 if(CTRL){CTRL.abort();return false}
 const text=q.value.trim();if(!text)return false
 var _g=document.getElementById('greet');if(_g)_g.remove();pinned=true
 if(text=='/移除'||text=='/remove'){clearAttach();q.value='';q.style.height='auto';slashMenu();return false}
 add('u',text);recordMsg('u',text);q.value='';q.style.height='auto';slashMenu()
 var wait=add('a','')
 var body=await runGen(text,wait)
 if(body){recordMsg('a',body);addRetry(wait,text)}
 q.focus();return false}
function slashMenu(){var el=document.getElementById('slashmenu');if(!el)return;el.style.display=(q.value.charAt(0)==='/')?'block':'none'}
function slashPick(cmd){q.value=cmd;q.focus();slashMenu()}
var attached=null,_pk='A'
function togglePlus(){var m=document.getElementById('plusmenu');m.style.display=m.style.display=='block'?'none':'block'}
function pick(kind){_pk='A';document.getElementById('plusmenu').style.display='none';document.getElementById(kind=='folder'?'dpick':'fpick').click()}
function pickB(kind){_pk='B';document.getElementById('plusmenu').style.display='none';document.getElementById(kind=='folder'?'dpick':'fpick').click()}
document.getElementById('fpick').onchange=function(){handleFiles(this.files);this.value=''}
document.getElementById('dpick').onchange=function(){handleFiles(this.files);this.value=''}
function handleFiles(files){if(_pk=='B')doAttach(files);else doIngest(files)}
function clearAttach(){if(attached){attached=null;updateChip();toast('已解除附加')}}
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
        uid = identity.verify_session(self._token())
        if uid is None:                                             # 未登入 → 登入頁(RBAC P4)
            return self._html(LOGIN_PAGE.replace("__MSG__", ""))
        if path == "/health":
            return self._health()
        if path == "/api/sessions":                                 # 對話歷史(DB、owner 收窄):列 session
            qs = parse_qs(self.path.split("?", 1)[1]) if "?" in self.path else {}
            return self._json({"sessions": chat_history.list_sessions(uid, qs.get("mode", [None])[0])})
        if path == "/api/messages":                                 # 載入某 session 訊息(owner 驗證於模組層)
            qs = parse_qs(self.path.split("?", 1)[1]) if "?" in self.path else {}
            try:
                sid = int(qs.get("sid", [""])[0])
            except (ValueError, TypeError):
                return self._json({"messages": []})
            return self._json({"messages": chat_history.load_messages(sid, uid)})
        uname, is_super = self._user_info(uid)                      # 左下角帳號區(使用者 + 模型版本)
        model = os.environ.get("OLLAMA_MODEL", "qwen3:8b")
        page = (PAGE.replace("__INITIAL__", html.escape((uname[:1] or "U").upper()))
                    .replace("__USER__", html.escape(uname))
                    .replace("__MODEL__", html.escape(model))
                    .replace("__ROLE__", "superuser" if is_super else "群組使用者"))
        self._html(page)

    def _user_info(self, uid):
        """左下角帳號區資料:回 (username, is_superuser);查無/錯 → 安全預設。"""
        try:
            with db.connect() as conn, db.transaction(conn) as cur:
                cur.execute("SELECT username, is_superuser FROM app_user WHERE user_id=%s", (uid,))
                r = cur.fetchone()
                return (r[0], bool(r[1])) if r else ("使用者", False)
        except Exception:
            return ("使用者", False)

    def _health(self):
        """running 狀態:DB / 顧問殼 / Ollama 可達性(側欄狀態燈;各 1.5s timeout)。"""
        h = {"db": False, "advisor": False, "ollama": False}
        try:
            with db.connect() as conn, db.transaction(conn) as cur:
                cur.execute("SELECT 1")
                h["db"] = bool(cur.fetchone())
        except Exception:
            pass
        ollama = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/") + "/api/tags"
        for k, u in (("advisor", self.advisor + "/v1/models"), ("ollama", ollama)):
            try:
                urllib.request.urlopen(u, timeout=1.5)
                h[k] = True
            except Exception:
                pass
        out = json.dumps(h).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(out)))
        self.end_headers()
        self.wfile.write(out)

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
        uid = identity.verify_session(self._token())            # 上傳者即擁有者(local_private 擁有者收窄,§4.5)
        if scope == "local_private" and uid is not None:
            cmd += ["--owner-user-id", str(uid)]
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

    def _readjson(self):
        try:
            n = int(self.headers.get("Content-Length") or 0)
            return json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            return {}

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
        uid = identity.verify_session(self._token())            # /chat//ingest//attach/session 皆須登入(RBAC P4;無 public fallback)
        if uid is None:
            return self._reply("請重新登入(工作階段已失效或未登入;重新整理頁面登入)")
        if path.startswith("/api/session/"):                    # 對話歷史 DB 寫入(owner 收窄+IDOR 防護於 chat_history 模組)
            bd = self._readjson()
            try:
                sid = int(bd.get("sid")) if bd.get("sid") is not None else None
            except (ValueError, TypeError):
                sid = None
            act = path[len("/api/session/"):]
            if act == "new":
                return self._json({"id": chat_history.create_session(uid, bd.get("mode", "chat"), bd.get("title"))})
            if act == "msg":
                return self._json({"id": chat_history.append_message(sid, uid, bd.get("role"), bd.get("content", ""), bd.get("guard_pass"))})
            if act == "rename":
                return self._json({"ok": chat_history.rename_session(sid, uid, bd.get("title"))})
            if act == "star":
                return self._json({"ok": chat_history.set_starred(sid, uid, bool(bd.get("starred")))})
            if act == "del":
                return self._json({"ok": chat_history.delete_session(sid, uid)})
            return self._json({"ok": False})
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
        fwd = {"model": "augur-advisor", "messages": msgs, "stream": True}
        att = req.get("augur_attach")
        if isinstance(att, dict) and (att.get("text") or "").strip():
            fwd["augur_attach"] = {"title": att.get("title") or "附加文件", "text": att["text"]}
        payload = json.dumps(fwd).encode()
        headers = {"Content-Type": "application/json"}
        if _SECRET:                                             # P4:傳身分給殼(殼驗機密後自查 session 自 resolve scope,§4.3)
            headers["X-Augur-Internal"] = _SECRET
            headers["X-Augur-Session"] = self._token() or ""
        self.send_response(200)                                 # 串流轉發:殼偽 SSE(role keepalive → 全文過閘後分塊)逐行 pipe;guard 尾註夾於文中
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        try:
            r = urllib.request.Request(self.advisor + "/v1/chat/completions", payload, headers)
            with urllib.request.urlopen(r, timeout=1800) as up:
                for line in up:
                    self.wfile.write(line)
                    self.wfile.flush()
        except Exception as e:
            self.wfile.write(("data: " + json.dumps({"choices": [{"delta": {"content": f"advisor 殼錯誤:{e}"}}]}) + "\n\n").encode())
            self.wfile.write(b"data: [DONE]\n\n")


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--port", type=int, default=8090)
    ap.add_argument("--advisor", default=ADVISOR)
    ap.add_argument("-h", "--help", action="store_true")
    a, _ = ap.parse_known_args()
    if a.help:
        print(__doc__)
        return
    if not _SECRET:      # 紅隊 HIGH 2026-07-05:無機密則無法向殼證明身分,拒啟動(不靜默降級成殼端全 deny/或誤當 super)
        sys.exit("✗ 未設 AUGUR_INTERNAL_SECRET:前台無法向殼證明登入者身分 → RBAC 無法生效。\n"
                 "  請於 .env 設 AUGUR_INTERNAL_SECRET(與 advisor 殼同值)再啟動;\n"
                 "  單機免登入測試請改直連殼 :8399 並加 --insecure-loopback-admin。")
    H.advisor = a.advisor
    print(f"誠實博學的我 · 對話 UI 起於 http://127.0.0.1:{a.port}(proxy → {a.advisor};Ctrl-C 停)", flush=True)
    ThreadingHTTPServer(("127.0.0.1", a.port), H).serve_forever()


if __name__ == "__main__":
    main()
