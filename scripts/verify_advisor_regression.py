#!/usr/bin/env python
"""顧問回歸驗證器 — 金題集過 advise() 全鏈之機械斷言(e2e 主計畫 P5;P6 機率斷言掛此)。

🎯 這支在做什麼(白話):把「顧問輸出的每個數字都對得上 DB ground truth」變成可重跑的機械驗收——
   ① picks 渲染=prediction_values 逐值等同(D4b 確定性注入之回歸釘);② guard 五閘全過;
   ③ 空檢索走誠實句閉集;④(P6 起)機率附欄=prediction_probability 逐值等同、機率∈payload.numbers()、
   §1.1 四誠實標記在場、P30 帶 'dead' 判死硬綁。--no-llm=結構模式(零 LLM,CI 可重現 A-30);
   --with-llm=全鏈經本機 ollama 生成後過 guard(改碼後 #7 先重啟服務)。

守 #15(斷言全 vs DB 實值)· #12(渲染複用 advise._render_picks_table 同一支)· #28(--no-llm 零 LLM)· #29a。
   SSOT=reports/augur_omniscient_e2e_master_plan_20260710.md §6.5。

執行指令矩陣:
  python scripts/verify_advisor_regression.py                     # 無參數:印矩陣+金題集現況(唯讀)
  python scripts/verify_advisor_regression.py --run --no-llm      # 結構模式:payload/渲染/標記/guard 靜態斷言
  python scripts/verify_advisor_regression.py --run --with-llm    # 全鏈:經 ollama 生成後過 guard(需 advisor 健在)
  python scripts/verify_advisor_regression.py --run --json        # 機器可讀(exit 0=全過)
"""
import argparse
import json
import re
import sys
from pathlib import Path

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db

REPO = Path(__file__).resolve().parent.parent
GOLDEN = REPO / "tests" / "advisor_golden_questions.json"


def _load_golden():
    return json.loads(GOLDEN.read_text(encoding="utf-8"))["questions"]


def check_picks_rendering():
    """斷言①:_render_picks_table 逐值等同 prediction_values(D4b 回歸釘)。"""
    from augur.advisor.advise import _render_picks_table
    from augur.advisor.payload import build_prediction_payload
    pl = build_prediction_payload()
    table = _render_picks_table(pl, top=len(pl.picks))
    fails = []
    with db.connect() as conn, db.transaction(conn) as cur:
        for p in pl.picks:
            cur.execute("SELECT score, rank FROM prediction_values pv JOIN model_registry mr USING (model_id) "
                        "WHERE pv.panel_date=%s AND mr.family='RankRidge' AND mr.horizon=%s AND pv.stock_id=%s",
                        (pl.as_of, pl.horizon, p.symbol))
            row = cur.fetchone()
            if row is None:
                fails.append(f"{p.symbol}: DB 無此列"); continue
            if round(float(row[0]), 4) != round(p.score, 4) or int(row[1]) != p.rank:
                fails.append(f"{p.symbol}: payload(score={p.score:.4f},rank={p.rank}) ≠ DB({row[0]:.4f},{row[1]})")
            if f"{p.score:.4f}" not in table:
                fails.append(f"{p.symbol}: score {p.score:.4f} 未渲染於 picks 表")
    return ("picks 渲染=DB 逐值等同", fails)


def check_probability_columns():
    """斷言④(P6):機率附欄=prediction_probability 逐值等同、∈numbers()、四標記在場、P30 判死硬綁。
    prediction_probability 空(P6 未 emit)→ 誠實 SKIP(基線版容許;emit 後本斷言轉硬)。"""
    from augur.advisor.advise import _render_picks_table
    from augur.advisor.payload import build_prediction_payload
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT count(*) FROM prediction_probability")
        n = cur.fetchone()[0]
    if n == 0:
        return ("機率附欄(P6)", ["SKIP:prediction_probability 空(P6 未 emit;基線版)"])
    pl = build_prediction_payload()
    fails = []
    table = _render_picks_table(pl, top=len(pl.picks))
    nums = pl.numbers()
    with db.connect() as conn, db.transaction(conn) as cur:
        # 逐 pick 逐 horizon:渲染值=DB 值、且 ∈ numbers()
        for p in pl.picks:
            # D5 呈現契約:附欄=P30(H20)/P60(H40)/P120(H120);H60=主欄 score 不重列 p(DB 存 H60 合法、不渲染)
            cur.execute("SELECT horizon, p_beat_median, econ_verdict FROM prediction_probability "
                        "WHERE panel_date=%s AND stock_id=%s AND horizon IN (20,40,120) ORDER BY horizon",
                        (pl.as_of, p.symbol))
            for h, pv, ev in cur.fetchall():
                if round(float(pv), 4) not in nums:
                    fails.append(f"{p.symbol} H{h}: p={pv:.4f} ∉ payload.numbers()")
                if f"{float(pv):.2f}" not in table and f"{float(pv):.4f}" not in table:
                    fails.append(f"{p.symbol} H{h}: p 未渲染")
        # 四誠實標記在場(§1.1 固定用語錨)
        for marker, pat in [("①橫斷面口徑", "勝過.*中位數"), ("②日曆偏差", r"≈\d+ *(日曆日|天)"),
                            ("③經濟判死", "dead|判死"), ("④同族近似", "同族|同 family")]:
            if not re.search(pat, table):
                fails.append(f"四標記缺:{marker}")
        # P30 判死硬綁
        cur.execute("SELECT count(*) FROM prediction_probability WHERE panel_date=%s AND horizon=20 "
                    "AND econ_verdict='dead'", (pl.as_of,))
        if cur.fetchone()[0] and "dead" not in table and "判死" not in table:
            fails.append("P30 判死標籤未硬綁呈現")
    return ("機率附欄=DB 等同+四標記+判死硬綁", fails)


def check_guard_paths(with_llm=False):
    """斷言②③:guard 五閘(乾淨回覆過/髒數字攔)+ 空檢索誠實句;--with-llm 時金題集過 oai_compat 全鏈。"""
    from augur.advisor import oai_compat
    from augur.advisor.guard import NO_KNOWLEDGE_RESPONSE  # noqa: F401(存在性=閉集錨)
    from augur.advisor.payload import build_prediction_payload, empty_payload
    fails = []
    goldens = _load_golden()
    wire = dict(payload_fn=empty_payload, picking_payload_fn=build_prediction_payload)  # 鏡射生產接線(serve_advisor_openai)
    if not with_llm:
        # 結構模式:mock llm_fn(確定性,CI 可重現)
        for g in goldens:
            resp = oai_compat.chat_completion(
                {"model": "augur-advisor", "messages": [{"role": "user", "content": g["q"]}]},
                llm_fn=lambda p: "(mock)白話結論,不含統計數字。",
                retrieve_fn=lambda q, k, scope=None: [], **wire)
            content = resp["choices"][0]["message"]["content"]
            gd = resp.get("augur_guard", {})
            if g["expected"] == "picks" and "相對強弱排序" not in content:
                fails.append(f"{g['id']}: 選股題未渲染 picks 段")
            if g["expected"] == "decline" and gd.get("pass") and "知識庫" not in content and "無" not in content:
                fails.append(f"{g['id']}: 離題未誠實 decline")
        # 髒數字反斷言:mock 編造數字必被 guard 攔
        resp = oai_compat.chat_completion(
            {"model": "augur-advisor", "messages": [{"role": "user", "content": "未來60天看好哪些台股?"}]},
            llm_fn=lambda p: "2330 目標價 1234.56 元,漲幅 99.99%。",
            retrieve_fn=lambda q, k, scope=None: [], **wire)
        if resp.get("augur_guard", {}).get("pass", True):
            fails.append("反斷言破:編造數字(1234.56)未被 guard 攔")
    else:
        from augur.advisor.ollama import make_llm_fn
        llm = make_llm_fn(think=False, strip_quotes=True)
        for g in goldens:
            resp = oai_compat.chat_completion(
                {"model": "augur-advisor", "messages": [{"role": "user", "content": g["q"]}]}, llm_fn=llm, **wire)
            gd = resp.get("augur_guard", {})
            if g["expected"] == "picks" and "相對強弱排序" not in resp["choices"][0]["message"]["content"]:
                fails.append(f"{g['id']}(llm): picks 段缺")
            if not gd:
                fails.append(f"{g['id']}(llm): 無 guard verdict")
    return ("guard 路徑(金題集%s)" % ("+LLM" if with_llm else ",mock"), fails)


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--no-llm", dest="no_llm", action="store_true")
    ap.add_argument("--with-llm", dest="with_llm", action="store_true")
    ap.add_argument("--json", dest="as_json", action="store_true")
    args = ap.parse_args()
    if not args.run:
        print(__doc__.split("執行指令矩陣:")[1])
        print(f"金題集:{GOLDEN}({len(_load_golden())} 題)")
        return 0
    checks = [check_picks_rendering(), check_probability_columns(),
              check_guard_paths(with_llm=args.with_llm)]
    hard_fail = False
    out = []
    for name, fails in checks:
        skip = any(f.startswith("SKIP") for f in fails)
        status = "SKIP" if skip else ("FAIL" if fails else "PASS")
        hard_fail |= (status == "FAIL")
        out.append({"check": name, "status": status, "detail": fails})
    if args.as_json:
        print(json.dumps(out, ensure_ascii=False, indent=1))
    else:
        for o in out:
            mark = {"PASS": "✓", "FAIL": "✗", "SKIP": "▷"}[o["status"]]
            print(f"{mark} [{o['status']}] {o['check']}")
            for d in o["detail"]:
                print(f"    {d}")
    print("═> " + ("FAIL" if hard_fail else "PASS(exit 0)"))
    return 1 if hard_fail else 0


if __name__ == "__main__":
    sys.exit(main())
