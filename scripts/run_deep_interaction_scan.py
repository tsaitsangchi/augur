#!/usr/bin/env python
"""augur 深度 raw 交互掃描(as-of 誠實版) — 18 正規化訊號 × 多 horizon × 交互,直接算 HAC-t。

🎯 這支在做什麼(白話):比 run_raw_interaction_ic 更深 + 修方法瑕疵:
- **as-of point-in-time 宇宙**(core_universe_asof、28 panel)→ ICs 從頭就無完整度 look-ahead 灌水(上輪 crude 用全宇宙害 t 虛高)
- **大幅擴欄位**:逐法人別籌碼(外資/投信/自營)、借券/融券、當沖、多 horizon 動能(5/20/60/120)、反轉、波動、流動性——**皆正規化**(/量或/股,避免淪為 size 掃描)
- **多 horizon**(H=5/20/60)× 單欄 + 全對 z-乘積交互
- **直接算 Newey-West HAC Eff-t**(去相關顯著性,審查 G8)——crude 高 t 不採信、只認 HAC
判讀:HAC-t |≥2.5| + 跨 horizon 一致 + 交互>>成分 才標候選(需再過完整提拔關卡才入生產)。本地零 usage(#28)、#8 t+1 還原。
執行指令矩陣:python scripts/run_deep_interaction_scan.py
"""
import itertools

import numpy as np

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db
from augur.evaluation import label as label_mod
from augur.evaluation import metrics

HS = (5, 20, 60)


def _wz(d):
    items = [(k, float(v)) for k, v in d.items() if v is not None and np.isfinite(float(v))]
    if len(items) < 30:
        return {}
    v = np.array([x for _, x in items]); mu, sd = v.mean(), v.std()
    if sd == 0:
        return {}
    return {k: float(z) for (k, _), z in zip(items, np.clip((v - mu) / sd, -3, 3))}


def _ic(sig, lab):
    common = [s for s in sig if s in lab]
    if len(common) < 30:
        return None
    x = np.array([sig[s] for s in common]); y = np.array([lab[s] for s in common])
    xr = np.argsort(np.argsort(x)); yr = np.argsort(np.argsort(y))
    if xr.std() == 0 or yr.std() == 0:
        return None
    return float(np.corrcoef(xr, yr)[0, 1])


def _col(cur, sql, params):
    cur.execute(sql, params)
    return {str(r[0]): float(r[1]) for r in cur.fetchall() if r[1] is not None}


def main():
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            cur.execute("SELECT DISTINCT as_of_date FROM core_universe_asof ORDER BY as_of_date")
            panels = [r[0] for r in cur.fetchall()]
        cal = label_mod.full_calendar(conn)
        idx = {str(d): i for i, d in enumerate(cal)}
        print(f"深度 as-of 交互掃描:{len(panels)} panel × H={HS}\n")

        SIGNALS = ["per", "pbr", "divyield", "foreign_net_r", "trust_net_r", "dealer_net_r",
                   "foreign_pct", "foreign_room", "margin_chg_r", "short_chg_r", "sbl_bal_r",
                   "daytrade_r", "turnover", "mom5", "mom20", "mom60", "mom120", "vol20"]
        single = {(s, h): [] for s in SIGNALS for h in HS}
        pair = {(a, b, h): [] for a, b in itertools.combinations(SIGNALS, 2) for h in HS}

        for pi, pd_ in enumerate(panels, 1):
            ps = str(pd_)
            if ps not in idx:
                continue
            i = idx[ps]
            with db.transaction(conn) as cur:
                cur.execute("SELECT stock_id FROM core_universe_asof WHERE as_of_date=%s", (pd_,))
                stk = [str(r[0]) for r in cur.fetchall()]
                if len(stk) < 50:
                    continue
                per = _col(cur, 'SELECT stock_id,"PER" FROM "TaiwanStockPER" WHERE date::text=%s AND stock_id=ANY(%s)', (ps, stk))
                pbr = _col(cur, 'SELECT stock_id,"PBR" FROM "TaiwanStockPER" WHERE date::text=%s AND stock_id=ANY(%s)', (ps, stk))
                dy = _col(cur, 'SELECT stock_id,dividend_yield FROM "TaiwanStockPER" WHERE date::text=%s AND stock_id=ANY(%s)', (ps, stk))
                vol = _col(cur, 'SELECT stock_id,"Trading_Volume" FROM "TaiwanStockPrice" WHERE date::text=%s AND stock_id=ANY(%s)', (ps, stk))
                tno = _col(cur, 'SELECT stock_id,"Trading_turnover" FROM "TaiwanStockPrice" WHERE date::text=%s AND stock_id=ANY(%s)', (ps, stk))
                fpct = _col(cur, 'SELECT stock_id,"ForeignInvestmentSharesRatio" FROM "TaiwanStockShareholding" WHERE date::text=%s AND stock_id=ANY(%s)', (ps, stk))
                fup = _col(cur, 'SELECT stock_id,"ForeignInvestmentUpperLimitRatio" FROM "TaiwanStockShareholding" WHERE date::text=%s AND stock_id=ANY(%s)', (ps, stk))
                shares = _col(cur, 'SELECT stock_id,"NumberOfSharesIssued" FROM "TaiwanStockShareholding" WHERE date::text=%s AND stock_id=ANY(%s)', (ps, stk))
                # 逐法人別 net buy
                cur.execute("SELECT stock_id, name, COALESCE(buy,0)-COALESCE(sell,0) FROM \"TaiwanStockInstitutionalInvestorsBuySell\" WHERE date::text=%s AND stock_id=ANY(%s)", (ps, stk))
                fnet, tnet, dnet = {}, {}, {}
                for sid, nm, net in cur.fetchall():
                    sid = str(sid); net = float(net or 0)
                    if nm == "Foreign_Investor": fnet[sid] = fnet.get(sid, 0) + net
                    elif nm == "Investment_Trust": tnet[sid] = tnet.get(sid, 0) + net
                    elif nm and nm.startswith("Dealer"): dnet[sid] = dnet.get(sid, 0) + net
                # margin/short 今昨 → change
                cur.execute('SELECT stock_id,"MarginPurchaseTodayBalance","MarginPurchaseYesterdayBalance","ShortSaleTodayBalance","ShortSaleYesterdayBalance" FROM "TaiwanStockMarginPurchaseShortSale" WHERE date::text=%s AND stock_id=ANY(%s)', (ps, stk))
                mchg, schg = {}, {}
                for sid, mt, my, st_, sy in cur.fetchall():
                    sid = str(sid)
                    if mt is not None and my is not None: mchg[sid] = float(mt) - float(my)
                    if st_ is not None and sy is not None: schg[sid] = float(st_) - float(sy)
                sbl = _col(cur, 'SELECT stock_id,"SBLShortSalesCurrentDayBalance" FROM "TaiwanDailyShortSaleBalances" WHERE date::text=%s AND stock_id=ANY(%s)', (ps, stk))
                dtv = _col(cur, 'SELECT stock_id,"Volume" FROM "TaiwanStockDayTrading" WHERE date::text=%s AND stock_id=ANY(%s)', (ps, stk))
                # 動能/波動窗:adj close cal[i-120..i]
                wdates = [str(cal[j]) for j in range(max(0, i - 120), i + 1)]
                cur.execute('SELECT stock_id,date,close FROM "TaiwanStockPriceAdj" WHERE date::text=ANY(%s) AND stock_id=ANY(%s) AND close>0', (wdates, stk))
                series = {}
                for sid, d, c in cur.fetchall():
                    series.setdefault(str(sid), {})[str(d)] = float(c)

            def at(j):
                return str(cal[j]) if 0 <= j < len(cal) else None
            raw = {s: {} for s in SIGNALS}
            for sid in stk:
                if sid in per: raw["per"][sid] = per[sid]
                if sid in pbr: raw["pbr"][sid] = pbr[sid]
                if sid in dy: raw["divyield"][sid] = dy[sid]
                v = vol.get(sid)
                if v and v > 0:
                    if sid in fnet: raw["foreign_net_r"][sid] = fnet[sid] / v
                    if sid in tnet: raw["trust_net_r"][sid] = tnet[sid] / v
                    if sid in dnet: raw["dealer_net_r"][sid] = dnet[sid] / v
                    if sid in mchg: raw["margin_chg_r"][sid] = mchg[sid] / v
                    if sid in schg: raw["short_chg_r"][sid] = schg[sid] / v
                    if sid in dtv: raw["daytrade_r"][sid] = dtv[sid] / v
                if sid in fpct: raw["foreign_pct"][sid] = fpct[sid]
                if sid in fpct and sid in fup: raw["foreign_room"][sid] = fup[sid] - fpct[sid]
                if sid in sbl and sid in shares and shares[sid] > 0: raw["sbl_bal_r"][sid] = sbl[sid] * 1000 / shares[sid]
                if sid in tno: raw["turnover"][sid] = tno[sid]
                sc = series.get(sid, {})
                ct = sc.get(ps)
                if ct:
                    for h, nm in ((5, "mom5"), (20, "mom20"), (60, "mom60"), (120, "mom120")):
                        d0 = at(i - h)
                        if d0 and d0 in sc and sc[d0] > 0:
                            raw[nm][sid] = np.log(ct / sc[d0])
                    rets = []
                    for k in range(i - 20, i):
                        a, b = at(k), at(k + 1)
                        if a in sc and b in sc and sc[a] > 0:
                            rets.append(np.log(sc[b] / sc[a]))
                    if len(rets) >= 10:
                        raw["vol20"][sid] = float(np.std(rets))

            z = {s: _wz(raw[s]) for s in SIGNALS}
            for h in HS:
                lab = label_mod.labels(conn, pd_, stk, h, calendar=cal)
                if len(lab) < 30:
                    continue
                for s in SIGNALS:
                    ic = _ic(raw[s], lab)
                    if ic is not None: single[(s, h)].append(ic)
                for a, b in itertools.combinations(SIGNALS, 2):
                    if not z[a] or not z[b]:
                        continue
                    prod = {sid: z[a][sid] * z[b][sid] for sid in z[a] if sid in z[b]}
                    ic = _ic(prod, lab)
                    if ic is not None: pair[(a, b, h)].append(ic)
            print(f"  panel {pi}/{len(panels)} {ps} done", flush=True)

    def hac(arr):
        ser = {i: v for i, v in enumerate(arr)}
        t = metrics.effective_t_hac(ser) if len(arr) > 2 else None
        return (np.mean(arr) if arr else float('nan'), t if t is not None else float('nan'), len(arr))

    print("\n— 單欄 as-of rank IC(IC / HAC-t / n,各 horizon)—")
    print(f"{'signal':14s}" + "".join(f"  H{h}:IC/HAC-t" for h in HS))
    for s in SIGNALS:
        cells = []
        for h in HS:
            m, t, n = hac(single[(s, h)])
            cells.append(f"  {m:+.3f}/{t:+.1f}")
        print(f"{s:14s}" + "".join(cells))

    print("\n— 交互(z-乘積)top 20 by |HAC-t|(任一 horizon)、含成分 max —")
    sic = {(s, h): hac(single[(s, h)])[0] for s in SIGNALS for h in HS}
    rows = []
    for (a, b, h), arr in pair.items():
        m, t, n = hac(arr)
        if n >= 10 and np.isfinite(t):
            comp = max(abs(sic.get((a, h), 0)), abs(sic.get((b, h), 0)))
            rows.append((abs(t), a, b, h, m, t, comp))
    rows.sort(reverse=True)
    print(f"  {'pair':30s} {'H':>3s} {'IC':>8s} {'HAC-t':>6s} {'成分max':>7s} {'判':>8s}")
    for _, a, b, h, m, t, comp in rows[:20]:
        flag = "✅候選" if abs(t) >= 2.5 and abs(m) > comp * 1.3 else "冗餘/弱"
        print(f"  {a+'×'+b:30s} {h:>3d} {m:>+8.4f} {t:>+6.1f} {comp:>7.4f} {flag:>8s}")


if __name__ == "__main__":
    main()
