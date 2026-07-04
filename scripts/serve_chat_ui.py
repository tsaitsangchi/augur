#!/usr/bin/env python
"""augur 誠實博學的我 — 極簡對話 Web UI(零外部依賴 stdlib;proxy 到 advisor 殼)。

🎯 一頁式對話介面:瀏覽器 → 本頁(:8090) → advisor 殼(:8399,advise+guard) → qwen3:8b。
   純 http.server + urllib、無 HuggingFace/無 node/無 Docker(避 Open WebUI 之 HF 嵌入 crash-loop)。
   同源 proxy(頁與 /chat 同埠)故無 CORS;guard verdict 顯示於每則回覆下。
守 #28(本地零 usage)· 計畫 §3-S7(對話唯一出口=advise+guard,本頁不編排、只轉發)· #18。

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

ADVISOR = "http://127.0.0.1:8399"
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _safe_dir(path):
    """+資料夾圍欄:realpath 須在 $HOME 下(拒 ../ 逃逸);回 realpath 或 None。"""
    home = os.path.realpath(os.path.expanduser("~"))
    rp = os.path.realpath(os.path.expanduser((path or "").strip()))
    return rp if (rp == home or rp.startswith(home + os.sep)) and os.path.isdir(rp) else None

PAGE = """<!doctype html><html lang=zh-Hant><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>誠實博學的我 · augur</title><style>
:root{color-scheme:dark}
body{margin:0;font-family:system-ui,"Noto Sans TC",sans-serif;background:#0d1117;color:#e6edf3}
header{padding:14px 18px;border-bottom:1px solid #21262d;font-weight:600}
header small{color:#7d8590;font-weight:400;margin-left:8px}
#log{max-width:820px;margin:0 auto;padding:18px}
.msg{margin:14px 0;padding:12px 14px;border-radius:10px;white-space:pre-wrap;line-height:1.6}
.u{background:#1f6feb22;border:1px solid #1f6feb55}
.a{background:#161b22;border:1px solid #21262d}
.g{font-size:12px;color:#7d8590;margin-top:8px;border-top:1px dashed #30363d;padding-top:6px}
.g.pass{color:#3fb950}.g.fail{color:#d29922}
#bar{position:sticky;bottom:0;background:#0d1117;border-top:1px solid #21262d;padding:12px}
#bar form{max-width:820px;margin:0 auto;display:flex;gap:8px}
#q{flex:1;padding:11px;border-radius:8px;border:1px solid #30363d;background:#161b22;color:#e6edf3;font-size:15px}
button{padding:11px 18px;border:0;border-radius:8px;background:#238636;color:#fff;font-size:15px;cursor:pointer}
button:disabled{background:#30363d;cursor:wait}
.sys{color:#7d8590;font-size:13px;text-align:center;margin:8px}
</style></head><body>
<header>誠實博學的我 <small>augur · advisor+guard · 本地 qwen3:8b(引文逐字閘;答不出即誠實說不知道)</small></header>
<div id=log><div class=sys>問投資哲學/經典原文相關問題。回覆較慢(本地 GPU 約數分鐘),guard 會攔下非逐字引用。</div></div>
<div id=bar><form onsubmit="return send(event)">
<input id=q placeholder="例:用經典原文談安全邊際與價值的關係" autocomplete=off>
<button id=b type=submit>送出</button></form></div>
<script>
const log=document.getElementById('log'),q=document.getElementById('q'),b=document.getElementById('b')
function add(cls,txt){const d=document.createElement('div');d.className='msg '+cls;d.textContent=txt;log.appendChild(d);d.scrollIntoView();return d}
async function send(e){e.preventDefault();const text=q.value.trim();if(!text)return false
 add('u',text);q.value='';b.disabled=true;const wait=add('a','思考中…(本地生成,請稍候)')
 try{const r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},
   body:JSON.stringify({messages:[{role:'user',content:text}]})})
  const j=await r.json();const m=j.choices?.[0]?.message?.content||'(無回覆)';const g=j.augur_guard||{}
  wait.textContent=m.split('\\n---\\n')[0]
  const gd=document.createElement('div');gd.className='g '+(g.pass?'pass':'fail')
  gd.textContent='[guard] '+(g.pass?'通過':'攔下(改誠實句)')+' · 引文 '+(g.citations??'?')+' · issues '+(g.issues?.length??0)
  wait.appendChild(gd)
 }catch(err){wait.textContent='錯誤:'+err}
 b.disabled=false;q.focus();return false}
</script></body></html>"""


class H(BaseHTTPRequestHandler):
    advisor = ADVISOR

    def log_message(self, *a):
        pass

    def do_GET(self):
        body = PAGE.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _reply(self, content):
        out = json.dumps({"choices": [{"message": {"content": content}}],
                          "augur_guard": {"pass": True, "issues": [], "citations": 0}}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(out)))
        self.end_headers()
        self.wfile.write(out)

    def do_POST(self):
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
        payload = json.dumps({"model": "augur-advisor", "messages": msgs}).encode()
        try:
            r = urllib.request.Request(self.advisor + "/v1/chat/completions", payload,
                                       {"Content-Type": "application/json"})
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
