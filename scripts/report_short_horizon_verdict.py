#!/usr/bin/env python
"""🎯 短 horizon 誠實裁決報告 — 把 revalidation_ledger 的 H20/H40/H60/H120 誠實四關結果
   攤成一張對比表(as-of IC + HAC-t、long-only 淨 Sharpe/Calmar/MaxDD vs 基準、deflation DSR),
   每個 horizon 標【確立 / 未確立(薄) / 判死】+ 日曆日對映,寫 reports/ 並印出。
   這是「30/60 天相對強弱」問題的誠實交付:呈現各 horizon 之真實(多半薄)可信度,不偽造絕對機率(靈魂)。

守原則 #12(唯讀讀既有 ledger、零雙軌:數字全出自 revalidate 寫的 revalidation_ledger)· #14(經濟價值=成功
   定義,非 IC)· #15(誠實標可信度、n 小揭露 exploratory、DSR<95%=未確立不粉飾)· #28(本地唯讀零 usage)· #29。

執行指令矩陣:
  python scripts/report_short_horizon_verdict.py                       # 讀最新 as-of、印裁決表 + 寫報告(唯讀安全)
  python scripts/report_short_horizon_verdict.py --as-of 2026-05-31    # 指定 as-of 上界
  python scripts/report_short_horizon_verdict.py --horizons 20,40,60   # 只比這幾個 horizon(預設 20,40,60,120)
  python scripts/report_short_horizon_verdict.py --no-write            # 只印、不寫 reports/ 檔
"""
import _bootstrap  # noqa: F401  (#29a 個別可執行)
import argparse
import datetime as _dt

from augur.core import db

CAL_PER_TD = 1.45          # 1 交易日 ≈ 1.45 日曆日(附錄實查錨)
DEPLOY_MODEL = "ridge"     # 部署口徑 = long-only ridge(既有 H60/H120 registry 模式)
DEPLOY_CONFIG = "LO|since2014"   # full-period long-only(revalidate stage_cd config 格式)
DEFAULT_HORIZONS = (20, 40, 60, 120)


def _latest_asof(conn):
    with db.transaction(conn) as cur:
        cur.execute("SELECT max(as_of_date) FROM revalidation_ledger")
        r = cur.fetchone()
    return r[0] if r and r[0] else None


def _one(conn, as_of, horizon, stage_in, model, config, metric):
    """取單一 metric(as_of、horizon、stage∈stage_in、model、config、metric_name);回 (value, hac_t, n) 或 (None,None,None)。"""
    with db.transaction(conn) as cur:
        cur.execute(
            "SELECT metric_value, hac_t, n_periods FROM revalidation_ledger "
            "WHERE as_of_date=%s AND horizon=%s AND stage = ANY(%s) AND model=%s "
            "AND config=%s AND metric_name=%s ORDER BY run_at DESC LIMIT 1",
            (as_of, horizon, list(stage_in), model, config, metric))
        r = cur.fetchone()
    return (r[0], r[1], r[2]) if r else (None, None, None)


def collect(conn, as_of, horizon):
    """一個 horizon 的誠實四關數字(全出自 ledger、唯讀)。"""
    BCD = ("B", "C", "D")
    ic, hac_t, n_ic = _one(conn, as_of, horizon, ("B",), "B2_ridge", "asof_ic", "mean_ic")
    shuf, _, _ = _one(conn, as_of, horizon, ("B",), "B2_ridge", "shuffle_ic", "mean_ic")
    sharpe, _, n_ec = _one(conn, as_of, horizon, ("C", "D"), DEPLOY_MODEL, DEPLOY_CONFIG, "net_sharpe")
    bench, _, _ = _one(conn, as_of, horizon, ("C", "D"), DEPLOY_MODEL, DEPLOY_CONFIG, "bench_sharpe")
    calmar, _, _ = _one(conn, as_of, horizon, ("C", "D"), DEPLOY_MODEL, DEPLOY_CONFIG, "net_calmar")
    maxdd, _, _ = _one(conn, as_of, horizon, ("C", "D"), DEPLOY_MODEL, DEPLOY_CONFIG, "net_maxdd")
    dsr, _, n_dsr = _one(conn, as_of, horizon, BCD, DEPLOY_MODEL, DEPLOY_CONFIG, "dsr")
    return dict(horizon=horizon, cal_days=round(horizon * CAL_PER_TD), ic=ic, hac_t=hac_t,
                n_ic=n_ic, shuffle_ic=shuf, sharpe=sharpe, bench=bench, alpha=(None if sharpe is None or bench is None else sharpe - bench),
                calmar=calmar, maxdd=maxdd, dsr=dsr, n_dsr=n_dsr)


def verdict(d):
    """誠實標籤(#15):經濟 alpha 為成功定義、DSR 為確立門檻。"""
    if d["sharpe"] is None:
        return "資料不足", "此 horizon 無 long-only ridge 經濟 cell(CD 未涵蓋?)"
    if d["sharpe"] <= 0 or (d["alpha"] is not None and d["alpha"] <= 0):
        return "判死", f"淨 Sharpe {d['sharpe']:+.2f} 未勝基準 {d['bench']:+.2f}(無經濟 alpha)"
    if d["dsr"] is not None and d["dsr"] >= 0.95:
        return "確立", f"過 deflation(DSR {d['dsr']:.3f}≥0.95)"
    ds = "n/a" if d["dsr"] is None else f"{d['dsr']:.3f}"
    return "未確立(薄)", f"有正 alpha 但 deflation 未過(DSR {ds}<0.95、樂觀上界)"


def render(rows, as_of):
    L = []
    L.append(f"# 短 horizon 誠實裁決:H20/H40/H60/H120 對比(as-of {as_of})\n")
    L.append("**單位=交易日**;日曆日=交易日×1.45(近似)。**成功定義=經濟價值(long-only 淨 Sharpe 勝基準)、"
             "非 IC**;DSR≥0.95 才算統計確立(#14/#15)。淨 Sharpe 為**樂觀上界**"
             "(survivorship 債未閉環/單 seed/成本平坦/n 小 → 真實更低)。\n")
    L.append("| horizon | ≈日曆日 | as-of IC | HAC-t | shuffle IC | 淨 Sharpe | 基準 | alpha | Calmar | MaxDD | DSR | n | 裁決 |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for d in rows:
        v, _why = verdict(d)
        def f(x, s="{:+.3f}"):
            return "n/a" if x is None else s.format(x)
        L.append("| **H{h}** | ~{c} | {ic} | {ht} | {sh} | {sr} | {bn} | {al} | {ca} | {dd} | {ds} | {n} | **{v}** |".format(
            h=d["horizon"], c=d["cal_days"], ic=f(d["ic"]), ht=f(d["hac_t"], "{:+.2f}"),
            sh=f(d["shuffle_ic"]), sr=f(d["sharpe"], "{:+.2f}"), bn=f(d["bench"], "{:+.2f}"),
            al=f(d["alpha"], "{:+.2f}"), ca=f(d["calmar"], "{:+.2f}"), dd=f(d["maxdd"], "{:+.1%}"),
            ds=("n/a" if d["dsr"] is None else f"{d['dsr']:.3f}"), n=(d["n_dsr"] or d["n_ic"] or "?"), v=v))
    L.append("\n## 逐 horizon 誠實說明\n")
    for d in rows:
        v, why = verdict(d)
        icn = "" if d["n_ic"] is None else f"、n={d['n_ic']}"
        sig = "" if d["hac_t"] is None else ("（IC 顯著 |HAC-t|≥2）" if abs(d["hac_t"]) >= 2 else "（IC 未達顯著 |HAC-t|<2）")
        L.append(f"- **H{d['horizon']}（≈{d['cal_days']} 日曆日）→ {v}**：{why}{icn}{sig}。")
    L.append("\n## 誠實邊界（#15）\n")
    L.append("- 「30/60 天絕對漲跌機率」= 假兆:本表只做**橫斷面相對強弱排序**之可信度,不偽造個股絕對機率(靈魂)。")
    L.append("- n 小者屬 **exploratory**、非定論;DSR<0.95 = edge 多半真但**薄、未達統計確立**(非 edge 不存在)。")
    L.append("- 數字全出自 revalidation_ledger(revalidate.py 寫)、唯讀零繞道(#12/#28);FREEZE 下只用 as-of 凍結快照。")
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description="短 horizon 誠實裁決報告(唯讀 ledger)")
    ap.add_argument("--as-of", dest="as_of", default=None, help="as-of 上界(YYYY-MM-DD;預設=ledger 最新)")
    ap.add_argument("--horizons", default=None, help="逗號分隔 horizon(預設 20,40,60,120)")
    ap.add_argument("--no-write", action="store_true", help="只印、不寫 reports/ 檔")
    a = ap.parse_args(argv)
    horizons = tuple(int(x) for x in a.horizons.split(",")) if a.horizons else DEFAULT_HORIZONS

    with db.connect() as conn:
        as_of = a.as_of or _latest_asof(conn)
        if as_of is None:
            print("revalidation_ledger 無資料 — 先跑 python scripts/revalidate.py --run")
            return
        rows = [collect(conn, as_of, h) for h in horizons]

    text = render(rows, as_of)
    print(text)
    if not a.no_write:
        today = _dt.date.today().strftime("%Y%m%d")
        out = f"reports/augur_short_horizon_verdict_{today}.md"
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
        print(f"\n✓ 寫入 {out}")


if __name__ == "__main__":
    main()
