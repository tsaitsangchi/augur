#!/usr/bin/env python
"""PME MAP-E012 S1 — 假說／map 策展（人＋可溯源文獻；禁 AI 生成）。

🎯 這支在做什麼（白話）：把「已有 feature_values 但尚未 principle_factor_map」的特徵，
   對上既有／新增學派原則（真實 citation、source_type≠ai_generated）。冪等 upsert。
   無合格文獻者不 INSERT（本輪 SEED 僅含可核文獻）；不手改 validated_*。

守 #1 #15 #29；憲章 philosophy 禁 ai_generated；MAP §3 S1／§6 A2；FZ-keep。

執行指令矩陣:
  python scripts/curate_pme_map_expand.py              # dry-run 印將寫列
  python scripts/curate_pme_map_expand.py --apply      # 寫入 DB
  python scripts/curate_pme_map_expand.py --selftest   # 免 DB
"""
from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401

# 策展常數：每校含 sources + principles×factors。citation 須可核；禁 ai_generated。
# direction＝文獻預期 IC 方向（假說）；validated_* 僅閘後回填。
MAP_E012_SEED = [
    {
        "name": "wyckoff",
        "principles": [
            {
                "statement": "較短窗量能不均（Gini／最大量占比）亦揭示主力吸籌／出貨階段。",
                "hypothesis": "volume_gini_20d／volume_max_share_{20,60}d／volume_surge_5_60 越高 → 籌碼集中訊號（與 60d Gini 共族）。",
                "factors": [
                    ("volume_gini_20d", 1),
                    ("volume_max_share_20d", 1),
                    ("volume_max_share_60d", 1),
                    ("volume_surge_5_60", 1),
                ],
            }
        ],
        "sources": [
            ("Wyckoff, The Richard D. Wyckoff Method of Trading in Stocks, 1931", "book"),
        ],
    },
    {
        "name": "cycle",
        "principles": [
            {
                "statement": "較短窗法人累計淨流相位同樣標示吸籌／派發位階。",
                "hypothesis": "inst_cumflow_position_60d 之位階預測報酬（與 120d 共族、窗長變體）。",
                "factors": [("inst_cumflow_position_60d", 1)],
            }
        ],
        "sources": [
            ("Marks, The Most Important Thing, 2011", "book"),
        ],
    },
    {
        "name": "smart_money",
        "principles": [
            {
                "statement": "官股／政府銀行與機構動向具資訊優勢。",
                "hypothesis": "gov_bank_net_buy_60d／top_holders_pct 越高 → 未來報酬越高（正向）。",
                "factors": [
                    ("gov_bank_net_buy_60d", 1),
                    ("top_holders_pct", 1),
                ],
            }
        ],
        "sources": [
            ("Gompers & Metrick, Institutional Investors and Equity Prices, QJE, 2001", "paper"),
        ],
    },
    {
        "name": "momentum",
        "principles": [
            {
                "statement": "近月動能（約 20 交易日）為中期動能族之短窗變體。",
                "hypothesis": "momentum_20d 越高 → 未來報酬越高（正向；Jegadeesh–Titman 窗長族）。",
                "factors": [("momentum_20d", 1)],
            }
        ],
        "sources": [
            ("Jegadeesh & Titman, Returns to Buying Winners and Selling Losers, J. Finance, 1993", "paper"),
        ],
    },
    {
        "name": "livermore",
        "principles": [
            {
                "statement": "價格接近年度高點反映趨勢／關鍵點附近之動能。",
                "hypothesis": "price_to_252d_high 越高（近高）→ 順勢報酬假說（正向）。",
                "factors": [("price_to_252d_high", 1)],
            }
        ],
        "sources": [
            ("Lefèvre, Reminiscences of a Stock Operator, 1923", "book"),
        ],
    },
    {
        "name": "low_vol",
        "principles": [
            {
                "statement": "短窗價格振幅（range）為波動代理。",
                "hypothesis": "range_mean_20d 越低 → 風險調整後報酬越高（負向；低波異常族）。",
                "factors": [("range_mean_20d", -1)],
            }
        ],
        "sources": [
            ("Ang, Hodrick, Xing & Zhang, The Cross-Section of Volatility and Expected Returns, J. Finance, 2006", "paper"),
        ],
    },
    {
        "name": "size",
        "principles": [
            {
                "statement": "成交金額／週轉率代理流動性與可交易規模。",
                "hypothesis": "dollar_volume_log_20d／turnover_mean_20d 與規模／流動性溢酬相關（方向待閘；假說＝越高越流動、溢酬偏負向對報酬）。",
                "factors": [
                    ("dollar_volume_log_20d", -1),
                    ("turnover_mean_20d", -1),
                ],
            }
        ],
        "sources": [
            ("Amihud, Illiquidity and stock returns: cross-section and time-series effects, J. Financial Markets, 2002", "paper"),
            ("Fama & French, The Cross-Section of Expected Stock Returns, J. Finance, 1992", "paper"),
        ],
    },
    # 新建學派：短窗反轉（Jegadeesh 1990）
    {
        "name": "short_term_reversal",
        "name_zh": "短窗反轉",
        "proponents": "Narasimhan Jegadeesh",
        "thesis": "極短窗（日／週）報酬傾向反轉——與中期動能正交之可預測性。",
        "principles": [
            {
                "statement": "極短窗報酬反轉（日／週）。",
                "hypothesis": "return_1d／momentum_5d 越高 → 近期末來報酬越低（負向 IC）。",
                "factors": [("return_1d", -1), ("momentum_5d", -1)],
            }
        ],
        "sources": [
            ("Jegadeesh, Evidence of Predictable Behavior of Security Returns, J. Finance, 1990", "paper"),
        ],
    },
    # 新建學派：融券／出借
    {
        "name": "short_interest",
        "name_zh": "融券／出借",
        "proponents": "Asquith, Pathak & Ritter 等",
        "thesis": "高融券餘額／高出借費反映負面資訊或限制套利，與後續報酬相關。",
        "principles": [
            {
                "statement": "融券餘額與出借費率具預測力。",
                "hypothesis": "sbl_short_balance_log／lending_fee_rate_mean_30d 越高 → 未來報酬越低（負向）。",
                "factors": [
                    ("sbl_short_balance_log", -1),
                    ("lending_fee_rate_mean_30d", -1),
                ],
            }
        ],
        "sources": [
            ("Asquith, Pathak & Ritter, Short interest, institutional ownership, and stock returns, J. Financial Economics, 2005", "paper"),
        ],
    },
]

# 本輪誠實 deferred（無足夠可核文獻／域特化）→ 不 INSERT
DEFERRED_UNMAPPED = [
    "margin_usage_ratio",  # 台股融資使用率；缺單一經典 citation 本輪不硬灌
]


def _selftest() -> int:
    ok = True

    def chk(name: str, cond: bool) -> None:
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    feats = []
    for sch in MAP_E012_SEED:
        for pr in sch["principles"]:
            for f, d in pr["factors"]:
                feats.append(f)
                chk(f"dir±1 {f}", d in (-1, 1))
        for cit, st in sch["sources"]:
            chk(f"no ai_generated ({cit[:24]})", st != "ai_generated")
            chk(f"citation non-empty", bool(cit.strip()))
    chk("margin deferred", "margin_usage_ratio" in DEFERRED_UNMAPPED)
    chk("margin not in seed factors", "margin_usage_ratio" not in feats)
    # 涵蓋多數 unmapped（除 deferred）
    expected = {
        "dollar_volume_log_20d", "gov_bank_net_buy_60d", "inst_cumflow_position_60d",
        "lending_fee_rate_mean_30d", "momentum_20d", "momentum_5d", "price_to_252d_high",
        "range_mean_20d", "return_1d", "sbl_short_balance_log", "top_holders_pct",
        "turnover_mean_20d", "volume_gini_20d", "volume_max_share_20d",
        "volume_max_share_60d", "volume_surge_5_60",
    }
    chk("seed covers expected unmapped", expected <= set(feats))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def apply_seed(conn, seed, *, dry_run: bool) -> dict:
    from augur.core import db

    n_sch = n_pri = n_map = n_src = 0
    new_maps: list[tuple] = []
    with db.transaction(conn) as cur:
        for sch in seed:
            name = sch["name"]
            cur.execute("SELECT school_id FROM philosophy_school WHERE name=%s", (name,))
            row = cur.fetchone()
            if row:
                sid = row[0]
            else:
                if dry_run:
                    print(f"  [dry] NEW school {name}")
                    sid = -1
                else:
                    cur.execute(
                        "INSERT INTO philosophy_school (name, name_zh, core_thesis, proponents) "
                        "VALUES (%s,%s,%s,%s) RETURNING school_id",
                        (
                            name,
                            sch.get("name_zh") or name,
                            sch.get("thesis") or "",
                            sch.get("proponents") or "",
                        ),
                    )
                    sid = cur.fetchone()[0]
                n_sch += 1
            for cit, st in sch["sources"]:
                if st == "ai_generated":
                    raise ValueError(f"禁 ai_generated: {cit}")
                if sid < 0:
                    n_src += 1
                    continue
                cur.execute(
                    "SELECT 1 FROM philosophy_source WHERE school_id=%s AND citation=%s",
                    (sid, cit),
                )
                if not cur.fetchone():
                    if dry_run:
                        print(f"  [dry] source ← {cit[:60]}")
                    else:
                        cur.execute(
                            "INSERT INTO philosophy_source (school_id, citation, source_type) "
                            "VALUES (%s,%s,%s)",
                            (sid, cit, st),
                        )
                    n_src += 1
            for pr in sch["principles"]:
                if sid < 0:
                    n_pri += 1
                    for f, d in pr["factors"]:
                        new_maps.append((name, f, d))
                        n_map += 1
                    continue
                cur.execute(
                    "SELECT principle_id FROM philosophy_principle "
                    "WHERE school_id=%s AND statement=%s",
                    (sid, pr["statement"]),
                )
                prow = cur.fetchone()
                if prow:
                    pid = prow[0]
                    if not dry_run:
                        cur.execute(
                            "UPDATE philosophy_principle SET hypothesis=%s WHERE principle_id=%s",
                            (pr["hypothesis"], pid),
                        )
                else:
                    if dry_run:
                        print(f"  [dry] principle ← {pr['statement'][:50]}")
                        pid = -1
                    else:
                        cur.execute(
                            "INSERT INTO philosophy_principle (school_id, statement, hypothesis) "
                            "VALUES (%s,%s,%s) RETURNING principle_id",
                            (sid, pr["statement"], pr["hypothesis"]),
                        )
                        pid = cur.fetchone()[0]
                    n_pri += 1
                for f, d in pr["factors"]:
                    if pid < 0:
                        new_maps.append((name, f, d))
                        n_map += 1
                        continue
                    cur.execute(
                        "SELECT map_id FROM principle_factor_map "
                        "WHERE principle_id=%s AND feature=%s",
                        (pid, f),
                    )
                    mrow = cur.fetchone()
                    if mrow:
                        if not dry_run:
                            cur.execute(
                                "UPDATE principle_factor_map SET direction=%s WHERE map_id=%s",
                                (d, mrow[0]),
                            )
                    else:
                        if dry_run:
                            print(f"  [dry] map ← {f} dir={d:+d} school={name}")
                        else:
                            cur.execute(
                                "INSERT INTO principle_factor_map (principle_id, feature, direction) "
                                "VALUES (%s,%s,%s)",
                                (pid, f, d),
                            )
                        new_maps.append((name, f, d))
                        n_map += 1
    return {
        "schools_touched": n_sch,
        "principles_new_or_upd": n_pri,
        "maps_new": n_map,
        "sources_new": n_src,
        "new_map_pairs": new_maps,
        "deferred": list(DEFERRED_UNMAPPED),
        "dry_run": dry_run,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="MAP-E012 S1 策展")
    ap.add_argument("--apply", action="store_true", help="寫入 DB（預設 dry-run）")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()

    from augur.core import db

    if not db.ping():
        print("SKIP: DB 不可達", file=sys.stderr)
        return 2

    dry = not args.apply
    with db.connect() as conn:
        stats = apply_seed(conn, MAP_E012_SEED, dry_run=dry)
    print(f"{'DRY-RUN' if dry else 'APPLIED'}: {stats}")
    print(f"deferred (no INSERT): {DEFERRED_UNMAPPED}")
    if dry:
        print("（加 --apply 才寫入）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
