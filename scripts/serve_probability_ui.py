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


# ── 蒙地卡羅模擬情境頁(§3.8 四鎖;逐日價格唯一合法呈現、硬綁「模擬非預測」)──────────
# 鎖①:浮水印/標題文案常數進 code(不從 DB 取、不可被資料竄改)
SIM_WATERMARK = "蒙地卡羅模擬情境 · 模擬非預測"
SIM_DISCLAIMER = ("本頁為歷史日報酬「純重抽」之情境模擬,非模型預測。方向不可預測(六門已判死);"
                  "中位走向僅反映該股歷史報酬分布,長期限尤受歷史漂移放大——切勿讀作漲跌明牌。"
                  "P(終值>0)=歷史重抽之模擬統計,與相對機率/方向機率永不混排。")
# 鎖:與 /(相對機率)零共用視覺——琥珀色系、專屬 class,不用 .prob/.banner
_SIM_CSS = """.simwrap{max-width:1000px;margin:0 auto;padding:16px;font-family:system-ui,sans-serif}
.simband{background:#3a2f14;border:2px solid #b8860b;color:#ffe9b0;padding:12px 16px;font-weight:700;
 border-radius:8px;margin-bottom:12px}.simwm{position:absolute;font-size:.7em;color:#b8860b;opacity:.55;
 transform:rotate(-6deg);pointer-events:none}.simcard{background:#201a10;border:1px solid #6b5416;
 border-radius:10px;padding:14px;margin:10px 0}.simk{display:block;font-size:.8em;color:#c8a95a;margin-top:3px}
.simstat{display:inline-block;min-width:120px;margin:6px 12px 6px 0}.simstat b{font-size:1.5em;color:#ffd873}"""


def _mc_targets(cur):
    cur.execute("SELECT DISTINCT target_id FROM mc_simulation_run ORDER BY target_id")
    return [r[0] for r in cur.fetchall()]


def _mc_run(cur, sid, h, method="block_bootstrap"):
    cur.execute("SELECT summary, n_paths, seed, method, block_len_td, asof_date FROM mc_simulation_run "
                "WHERE target_id=%s AND horizon_td=%s AND method=%s", (sid, h, method))
    return cur.fetchone()


def _mc_horizons(cur, sid):
    cur.execute("SELECT DISTINCT horizon_td FROM mc_simulation_run WHERE target_id=%s ORDER BY horizon_td", (sid,))
    return [r[0] for r in cur.fetchall()]


def _fan_svg(summary):
    """內嵌 SVG 分位錐(p5–p95/p25–p75 帶 + p50 線);琥珀系、浮水印硬綁。無外部依賴。"""
    cone = summary["cone"]
    last = summary["last_close"]
    W, H, ml, mr, mt, mb = 900, 360, 60, 20, 20, 34
    pw, ph = W - ml - mr, H - mt - mb
    n = len(cone)
    lo = min(min(r["px_p5"] for r in cone), last)
    hi = max(max(r["px_p95"] for r in cone), last)
    pad = (hi - lo) * 0.05 or 1
    lo, hi = lo - pad, hi + pad

    def X(i):
        return ml + (i / n) * pw

    def Y(p):
        return mt + (hi - p) / (hi - lo) * ph
    # 帶:右沿上界→左沿下界 polygon(含 td0=last)
    def band(up, dn):
        pts = [f"{X(0):.1f},{Y(last):.1f}"] + [f"{X(i+1):.1f},{Y(r[up]):.1f}" for i, r in enumerate(cone)]
        pts += [f"{X(i+1):.1f},{Y(r[dn]):.1f}" for i, r in reversed(list(enumerate(cone)))] + [f"{X(0):.1f},{Y(last):.1f}"]
        return " ".join(pts)
    p50 = " ".join([f"{X(0):.1f},{Y(last):.1f}"] + [f"{X(i+1):.1f},{Y(r['px_p50']):.1f}" for i, r in enumerate(cone)])
    yticks = "".join(
        f'<line x1="{ml}" y1="{Y(v):.1f}" x2="{W-mr}" y2="{Y(v):.1f}" stroke="#4a3d1a" stroke-width="1"/>'
        f'<text x="{ml-6}" y="{Y(v)+4:.1f}" fill="#c8a95a" font-size="11" text-anchor="end">{v:.0f}</text>'
        for v in [lo + (hi - lo) * k / 4 for k in range(5)])
    return (
        f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" '
        f'aria-label="模擬分位錐:中位由 {last:.0f} 至 {cone[-1]["px_p50"]:.0f},5-95% 末日 {cone[-1]["px_p5"]:.0f}-{cone[-1]["px_p95"]:.0f}">'
        f'{yticks}'
        f'<polygon points="{band("px_p95","px_p5")}" fill="#b8860b" fill-opacity="0.18"/>'
        f'<polygon points="{band("px_p75","px_p25")}" fill="#d9a520" fill-opacity="0.28"/>'
        f'<polyline points="{p50}" fill="none" stroke="#ffd873" stroke-width="2"/>'
        f'<line x1="{ml}" y1="{Y(last):.1f}" x2="{W-mr}" y2="{Y(last):.1f}" stroke="#888" stroke-width="1" stroke-dasharray="4 4"/>'
        f'<text x="{W/2:.0f}" y="{H/2:.0f}" class="simwm" text-anchor="middle" font-size="34">{SIM_WATERMARK}</text>'
        f'<text x="{ml}" y="{H-8}" fill="#c8a95a" font-size="11">交易日(as-of 後) →</text>'
        f'</svg>')


def simulate_page(cur, sid, h):
    targets = _mc_targets(cur)
    opts = "".join(f'<option value="{html.escape(s)}"{" selected" if s==sid else ""}>{html.escape(s)}</option>' for s in targets)
    body = ""
    if sid:
        hs = _mc_horizons(cur, sid)
        h = h if h in hs else (hs[0] if hs else None)
        hlinks = " ".join(f'<a href="/simulate?stock={html.escape(sid)}&h={x}">{"[" if x==h else ""}{x}td{"]" if x==h else ""}</a>' for x in hs)
        run = _mc_run(cur, sid, h) if h else None
        if run:
            summ, n_paths, seed, method, blk, asof = run
            t = summ["terminal"]
            body = (
                f'<div class="simcard"><h2 style="color:#ffd873">{html.escape(sid)} · {h} 交易日情境錐（as-of {asof}）</h2>'
                f'<div style="position:relative">{_fan_svg(summ)}</div>'
                f'<div style="margin-top:10px">'
                f'<span class="simstat">as-of 收盤<br><b>{summ["last_close"]:.1f}</b></span>'
                f'<span class="simstat">中位情境<br><b>{t["px_p50"]:.0f}</b></span>'
                f'<span class="simstat">5%–95% 終值報酬<br><b>{t["ret_p5"]:+.1%} ~ {t["ret_p95"]:+.1%}</b></span>'
                f'<span class="simstat">模擬 P(終值&gt;0)<br><b>{summ["sim_stat_p_terminal_up"]:.0%}</b><span class="simk">※歷史統計非預測</span></span>'
                f'</div>'
                f'<span class="simk">horizon:{hlinks}</span>'
                f'<span class="simk">方法:{html.escape(method)}｜區塊 {blk or "-"} td｜n_paths={n_paths}｜seed={seed}(可重現)｜純歷史重抽、零模型 tilt</span>'
                f'</div>')
        else:
            body = f'<div class="simcard">查無 {html.escape(sid)} 之模擬(先跑 simulate_mc_paths.py)。可選 horizon:{hlinks}</div>'
    else:
        body = '<div class="simcard">選一檔看其蒙地卡羅逐日情境錐（模擬非預測）。</div>'
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>蒙地卡羅模擬情境（模擬非預測）</title>'
            f'<style>{_CSS}{_SIM_CSS}</style></head><body><div class="simwrap">'
            f'<div class="simband">⚠ {html.escape(SIM_WATERMARK)}</div>'
            f'<div class="simcard" style="color:#e8d9a8">{html.escape(SIM_DISCLAIMER)}</div>'
            f'<form method="get" action="/simulate"><label>個股 <select name="stock" onchange="this.form.submit()">'
            f'<option value="">—選股—</option>{opts}</select></label> '
            f'<a href="/">← 相對機率頁</a> · <a href="/logout">登出</a></form>'
            f'{body}<p class="simk">資料 as-of {AS_OF} · 唯讀 · is_simulation 硬綁 · 只存分位錐摘要(不存逐路徑)</p>'
            f'</div></body></html>')


# ── 方向 GATE 誠實頁(展示分級:never_shown=不出方向機率、但據實揭露判決;死亡證明研究級呈現)──────
DIR_BANNER = ("⚠ 方向軸(絕對漲跌機率)六門全 evaluated_fail —— 依展示分級,**不輸出任何個股方向機率數字**。"
              "本頁僅據實揭露 GATE 判決(研究級誠實揭露),非可交易訊號。")


def _direction_page(cur):
    cur.execute("SELECT gate_id, track, horizon, status, result_snapshot FROM direction_gate ORDER BY track, horizon")
    rows = cur.fetchall()
    trs = ""
    for gid, tr, h, st, snap in rows:
        s = snap or {}
        i, ii, iii = s.get("i_hitrate", {}), s.get("ii_brier", {}), s.get("iii_calibration", {})
        tier = s.get("display_tier", "?")
        mark = "💀 判死" if st == "evaluated_fail" else ("✓ 過" if st == "evaluated_pass" else st)
        def _pf(x):
            return "✓" if x else "✗"
        trs += (
            f'<tr><td>{html.escape(gid)}</td><td>{tr} h={h}</td>'
            f'<td class="dead">{mark}</td>'
            f'<td>{i.get("overall_hit","-")} vs {s.get("majority_base","-")} '
            f'(Eff-t={i.get("hac_eff_t","-")} p={i.get("p_one_sided","-")}) {_pf(i.get("pass"))}</td>'
            f'<td>{ii.get("model","-")}&lt;{ii.get("base","-")} {_pf(ii.get("pass"))}</td>'
            f'<td>ECE {iii.get("ece","-")} mono={iii.get("spearman_monotone","-")} {_pf(iii.get("pass"))}</td>'
            f'<td>{html.escape(str(tier))}</td></tr>')
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>方向 GATE 判決（死亡證明·誠實揭露）</title>'
            f'<style>{_CSS}</style></head><body>'
            f'<div class="banner">{html.escape(DIR_BANNER)}</div><div class="wrap">'
            f'<p><a href="/">← 相對機率頁</a> · <a href="/simulate">蒙地卡羅情境</a> · <a href="/logout">登出</a></p>'
            f'<h2>方向軸六門機械裁判結果（as-of {AS_OF}、FREEZE 內歷史 walk-forward OOS）</h2>'
            f'<div class="card"><table>'
            f'<tr><th>gate</th><th>軌/H</th><th>判決</th><th>關(i) hit vs 多數類基線</th>'
            f'<th>關(ii) Brier</th><th>關(iii) 校準</th><th>展示層</th></tr>{trs}</table>'
            f'<span class="mk">三關全過才 evaluated_pass;任一不過=判死留檔、never_shown(永不出方向機率)。'
            f'防挪門柱:criteria approve 後 trigger 鎖死、終態不可回改。</span></div>'
            f'<div class="card">結論:此系統<strong>沒有</strong>可信可交易的絕對方向預測。逐日價格路徑需求請見'
            f' <a href="/simulate">蒙地卡羅模擬情境</a>(模擬非預測);相對強弱見 <a href="/">相對機率頁</a>。</div>'
            f'</div></body></html>')


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
            f'<a href="/simulate{"?stock="+html.escape(sid) if sid else ""}">蒙地卡羅情境頁 →</a> · '
            f'<a href="/direction">方向 GATE 判決 →</a> · '
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
            if u.path == "/simulate":
                h = int((q.get("h") or [30])[0])
                return self._send(200, simulate_page(cur, sid, h))
            if u.path == "/direction":
                return self._send(200, _direction_page(cur))
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
