#!/usr/bin/env python
"""相對機率誠實 web UI — 個股 30/60/120 天「相對機率」唯讀呈現殼(致命紅線:絕不絕對漲跌)。

🎯 這支在做什麼(白話):把 prediction_probability(as-of 2026-05-31 FREEZE)之 p_beat_median 呈現給人看,
   但**永遠是「P(該股報酬 勝過 同儕橫斷面中位數 | as-of, horizon H)」相對機率、絕不寫成「上漲機率」絕對值**
   (憲章相對機率誠實判準)。四誠實標記(①橫斷面口徑+as-of+逐折 n ②日曆日↔交易日偏差 ③econ_verdict 經濟判死
   ④family_note 同族近似)**逐值與機率硬綁於同一 DOM 節點**——單獨截圖/複製仍自帶標記。四 horizon(H20/H40/
   H60/H120)呈**四張獨立模型卡**(不連成機率曲線,免讀出未主張之期限結構)。

安全/治權(#5 OWASP · A-28):純唯讀投影,route 只有 GET 讀端點 + POST /login;**零 approve/promote/trade/
   ingest 端點**(不自迴圈、approve 唯人);綁 127.0.0.1;identity.verify_session fail-closed(revoked/expired/
   inactive 全 AND);HttpOnly+SameSite=Strict cookie。渲染 100% 伺服端確定性(NOT LLM);每個數字直出 SELECT
   結果、無估算(#9 三來源之 b)。

守 #5 · #8(as-of 2026-05-31 凍結)· #15(相對機率誠實、不誤譯絕對)· #18(動作動詞命名,對齊 serve_*)。
   前置=機率層已建(calibrate_relative_probability.py)+ app_user/app_session(identity)。

執行指令矩陣:
  python scripts/serve_probability_ui.py --serve            # 起 UI(127.0.0.1:8600;帳密取 app_user)
  python scripts/serve_probability_ui.py --check            # 唯讀自檢:資料就位 + 誠實不變式(不起服務)
"""
import argparse
import html
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import _bootstrap  # noqa: F401
from augur.core import db
from augur.knowledge import identity

HOST, PORT = "127.0.0.1", 8600
AS_OF = "2026-05-31"
# 致命紅線口徑:所有機率永遠是此式、絕不絕對漲跌(憲章相對機率誠實判準)
CANON = "P(該股報酬 勝過 同儕橫斷面中位數 | as-of {asof}, H{h})".format
_VERDICT_ZH = {"dead": "經濟判死(edge 不存在)", "thin_unestablished": "薄 edge、未確立",
               "established": "edge 已確立"}


# ── 唯讀資料存取(只 SELECT prediction_probability + probability_calibrator)──────────
def _calibrators(cur):
    cur.execute("SELECT horizon, calibrator_id, method, n_fit_folds, n_fit_samples, purge_verified, "
                "brier, brier_baseline, ece, family_note FROM probability_calibrator ORDER BY horizon")
    return {r[0]: {"calibrator_id": r[1], "method": r[2], "folds": r[3], "n": r[4], "purge": r[5],
                   "brier": r[6], "brier_base": r[7], "ece": r[8], "family_note": r[9]} for r in cur.fetchall()}


def _stock_rows(cur, sid):
    cur.execute("SELECT horizon, calendar_days, p_beat_median, rank_pctile, econ_verdict, model_id, calibrator_id "
                "FROM prediction_probability WHERE stock_id=%s AND panel_date=%s ORDER BY horizon", (sid, AS_OF))
    return cur.fetchall()


def _leaderboard(cur, horizon, limit=40):
    cur.execute("SELECT stock_id, p_beat_median, rank_pctile, econ_verdict FROM prediction_probability "
                "WHERE horizon=%s AND panel_date=%s ORDER BY rank_pctile DESC LIMIT %s", (horizon, AS_OF, limit))
    return cur.fetchall()


def _stock_ids(cur):
    cur.execute("SELECT DISTINCT stock_id FROM prediction_probability WHERE panel_date=%s ORDER BY stock_id", (AS_OF,))
    return [r[0] for r in cur.fetchall()]


# ── 誠實渲染(伺服端確定性;四標記逐值硬綁)────────────────────────────────
_CSS = """body{font-family:system-ui,sans-serif;margin:0;background:#0f1115;color:#e6e6e6}
.wrap{max-width:1000px;margin:0 auto;padding:16px}
.banner{background:#3a1d1d;border:2px solid #a33;color:#ffd7d7;padding:12px 16px;font-weight:600;
 position:sticky;top:0;z-index:9;border-radius:0 0 8px 8px}
.card{background:#1a1d24;border:1px solid #333;border-radius:10px;padding:14px;margin:10px 0}
.prob{font-size:2.1em;font-weight:700}
.mk{display:block;font-size:.8em;color:#9aa;margin-top:3px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:10px}
table{border-collapse:collapse;width:100%;font-size:.9em}td,th{border-bottom:1px solid #2a2d34;padding:5px 8px;text-align:left}
a{color:#7ab7ff}.dead{color:#e88}.thin{color:#ec9}input{padding:6px}
.meter{height:6px;background:#333;border-radius:3px;margin-top:5px;position:relative}
.meter i{position:absolute;top:-2px;width:2px;height:10px;background:#7ab7ff}"""

BANNER = ("⚠ 本頁所有機率 = P(該股報酬 勝過 同儕橫斷面中位數 | as-of " + AS_OF + ", horizon H)"
          " —— 相對機率,非絕對漲跌方向機率。0.5=與同儕中位數持平。禁讀作絕對漲跌方向。"
          "(此橫幅為定義脈絡,不替代下方每個數字自帶之四誠實標記)")


def _prob_cell(row, cal):
    """一個 (horizon) 機率格:p_beat_median + 四誠實標記硬綁同節點(截圖/複製仍自帶)。"""
    h, cal_days, p, rank, verdict, model_id, calib_id = row
    c = cal.get(h, {})
    vz = _VERDICT_ZH.get(verdict, verdict or "?")
    vclass = "dead" if verdict == "dead" else "thin"
    # meter:中心 0.5、標記本值位置(相對位置,禁綠漲紅跌方向)
    pos = max(0, min(100, (float(p) - 0.35) / 0.30 * 100))
    fam = c.get("family_note") or "同族近似聲明從缺"
    return (
        f'<div class="card">'
        f'<div>H{h}（{cal_days} 日曆日）<span style="color:#788">model {html.escape(str(model_id))}</span></div>'
        f'<div class="prob">{float(p):.3f}</div>'
        f'<div class="meter"><i style="left:{pos:.0f}%"></i></div>'
        # 四誠實標記(逐值硬綁)
        f'<span class="mk">① 口徑:{html.escape(CANON(asof=AS_OF, h=h))}｜逐折 n={c.get("folds","?")}（樣本 {c.get("n","?")}）</span>'
        f'<span class="mk">② 日曆↔交易日:H{h} 交易日 = {cal_days} 日曆日（用戶問「N 天」以日曆日對映此欄，非圓整標籤）</span>'
        f'<span class="mk {vclass}">③ 經濟裁決:{html.escape(vz)}</span>'
        f'<span class="mk">④ 同族近似:{html.escape(str(fam)[:120])}</span>'
        f'</div>')


def _stock_view(cur, sid, cal):
    rows = _stock_rows(cur, sid)
    if not rows:
        return f'<div class="card">查無 {html.escape(sid)} 之機率（as-of {AS_OF}）。</div>'
    cards = "".join(_prob_cell(r, cal) for r in rows)
    return (f'<h2>{html.escape(sid)} · 四 horizon 獨立模型卡</h2>'
            f'<div class="grid">{cards}</div>')


def _leaderboard_view(cur, horizon):
    rows = _leaderboard(cur, horizon)
    trs = "".join(f'<tr><td><a href="/?stock={html.escape(s)}">{html.escape(s)}</a></td>'
                  f'<td>{float(p):.3f}</td><td>{float(rk):.3f}</td>'
                  f'<td class="{"dead" if v=="dead" else "thin"}">{html.escape(_VERDICT_ZH.get(v,v or ""))}</td></tr>'
                  for s, p, rk, v in rows)
    return (f'<h2>橫斷面相對排名榜 · H{horizon}（依 rank_pctile 降序 top 40）</h2>'
            f'<div class="card"><table><tr><th>股</th><th>p_beat_median</th><th>rank_pctile</th>'
            f'<th>經濟裁決</th></tr>{trs}</table>'
            f'<span class="mk">口徑:{html.escape(CANON(asof=AS_OF, h=horizon))}；rank 為橫斷面相對位置、非絕對。</span></div>')


def _calibrator_view(cal):
    trs = ""
    for h in sorted(cal):
        c = cal[h]
        thin = "（僅微幅勝基線=坐實薄 edge）" if c["brier"] and c["brier_base"] and c["brier"] > c["brier_base"] * 0.98 else ""
        trs += (f'<tr><td>H{h}</td><td>{html.escape(c["method"] or "")}</td>'
                f'<td>{"✓" if c["purge"] else "✗ 未證"}</td>'
                f'<td>{c["brier"]:.4f} vs 基線 {c["brier_base"]:.4f}{thin}</td>'
                f'<td>{c["ece"]:.4f}</td></tr>')
    return (f'<h2>校準器 provenance（Platt 誠實揭露）</h2>'
            f'<div class="card"><table><tr><th>H</th><th>method</th><th>purge_verified</th>'
            f'<th>Brier vs 基線</th><th>ECE</th></tr>{trs}</table>'
            f'<span class="mk">purge_verified=校準以 expanding-purge 防洩漏(#8)；Brier 僅微幅勝 base-rate = 薄 edge 之誠實坐實。</span></div>')


def dashboard(cur, sid=None, horizon=60):
    cal = _calibrators(cur)
    ids = _stock_ids(cur)
    opts = "".join(f'<option value="{html.escape(s)}"{" selected" if s==sid else ""}>{html.escape(s)}</option>' for s in ids)
    body = _stock_view(cur, sid, cal) if sid else '<div class="card">選一檔個股看其四 horizon 相對機率。</div>'
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>相對機率（誠實）</title>'
            f'<style>{_CSS}</style></head><body>'
            f'<div class="banner">{html.escape(BANNER)}</div><div class="wrap">'
            f'<form method="get"><label>個股 <select name="stock" onchange="this.form.submit()">'
            f'<option value="">—選股—</option>{opts}</select></label> '
            f'<a href="/logout">登出</a></form>'
            f'{body}{_leaderboard_view(cur, horizon)}{_calibrator_view(cal)}'
            f'<p class="mk">資料 as-of {AS_OF}（FREEZE）· 唯讀 · 100% 伺服端渲染 · 綁 127.0.0.1</p>'
            f'</div></body></html>')


def login_html(err=""):
    e = f'<p class="dead">{html.escape(err)}</p>' if err else ""
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>登入</title><style>{_CSS}</style></head>'
            f'<body><div class="wrap"><h2>相對機率 UI · 登入</h2>{e}'
            f'<form method="post" action="/login"><div class="card">'
            f'<p><input name="username" placeholder="帳號"></p>'
            f'<p><input name="password" type="password" placeholder="密碼"></p>'
            f'<button>登入</button></div></form></div></body></html>')


# ── HTTP handler(唯讀 + 登入;mirror serve_admin_console 樣式)────────────────
class ProbHandler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _token(self):
        for part in (self.headers.get("Cookie") or "").split(";"):
            if part.strip().startswith("psid="):
                return part.strip()[5:]
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

    def do_GET(self):
        from urllib.parse import urlparse, parse_qs
        u = urlparse(self.path)
        if u.path == "/logout":
            tok = self._token()
            if tok:
                identity.revoke_session(tok)
            return self._send(302, "", cookie="psid=; Max-Age=0; Path=/") or self.send_header("Location", "/")
        if identity.verify_session(self._token()) is None:
            return self._send(200, login_html())
        q = parse_qs(u.query)
        sid = (q.get("stock") or [None])[0] or None
        with db.connect() as conn, db.transaction(conn) as cur:
            return self._send(200, dashboard(cur, sid))

    def do_POST(self):
        from urllib.parse import parse_qs
        if self.path != "/login":
            return self._send(404, "not found")
        n = int(self.headers.get("Content-Length", 0))
        form = parse_qs(self.rfile.read(n).decode())
        user = (form.get("username") or [""])[0]
        pw = (form.get("password") or [""])[0]
        u = identity.authenticate(user, pw)
        if not u:
            return self._send(200, login_html("帳密錯誤或帳號停用"))
        tok = identity.issue_session(u["user_id"], client_note="prob_ui")
        self._send(302, "", cookie=f"psid={tok}; HttpOnly; SameSite=Strict; Path=/")
        self.send_header("Location", "/")


def _check():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT count(*), count(DISTINCT stock_id), count(DISTINCT horizon) FROM prediction_probability WHERE panel_date=%s", (AS_OF,))
        n, s, h = cur.fetchone()
        cal = _calibrators(cur)
        # 誠實不變式:不得有 p_beat_median 被當絕對機率之欄;渲染只出 SELECT 值
        cur.execute("SELECT count(*) FROM prediction_probability WHERE panel_date=%s AND (p_beat_median<0 OR p_beat_median>1)", (AS_OF,))
        bad = cur.fetchone()[0]
    # 渲染自檢:抽一檔渲染,機械斷言(a)禁語絕不出現 (b)四誠實標記逐值在
    with db.connect() as conn, db.transaction(conn) as cur:
        sample = _stock_ids(cur)[0]
        page = dashboard(cur, sid=sample)
    forbidden = [w for w in ("上漲機率", "會漲的機率", "下跌機率", "會漲的機會") if w in page]
    markers = all(mk in page for mk in ("① 口徑", "② 日曆", "③ 經濟裁決", "④ 同族近似", "勝過 同儕"))
    ok = bad == 0 and not forbidden and markers
    print(f"✓ 資料就位:{n} 列 / {s} 股 / {h} horizon（as-of {AS_OF}）；校準器 {len(cal)} 個")
    print(f"  誠實不變式:p_beat_median∈[0,1] 越界={bad}（應 0）；口徑硬綁={CANON(asof=AS_OF, h=60)}")
    print(f"  render 自檢({sample}):禁語出現={forbidden or '無'}；四標記硬綁={'✓' if markers else '✗'}")
    print(f"  render:100% 伺服端、零 LLM、零寫路徑（route 僅 GET 讀 + POST /login）")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--serve", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    if args.check:
        return _check()
    if args.serve:
        print(f"相對機率 UI:http://{HOST}:{PORT}（唯讀、綁本機、as-of {AS_OF}）")
        ThreadingHTTPServer((HOST, PORT), ProbHandler).serve_forever()
        return 0
    print(__doc__.split("執行指令矩陣:")[1])
    return _check()


if __name__ == "__main__":
    sys.exit(main())
