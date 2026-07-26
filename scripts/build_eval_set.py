#!/usr/bin/env python
"""凍結行為題庫產生器 — 四層各 30 題,全部機械產自 live DB(S0 修尺,hugo 2026-07-26 拍板)。
🎯 這支在做什麼(白話):舊評測集是「每次現算 md5 序取前 12」——語料每天長大就會換題,
   故帳本上 0.256→0.325→0.383→0.492 跨的不是同一把尺(實證:帳本 set_hash 44893a73fbfc vs
   現行演算法 a8b466844fe5)。本支改為**一次產生、實體化凍結進 DB**,set_id=內容雜湊,
   之後每次評測都比對 set_id,不同即拒絕跨集比較(fail-loud)。四層各測一種行為:
     L1_RETRIEVED   檢索片段已放進題目 → 該逐字採用(測 F 事實忠實 + P 引註)
     L2_NO_RETRIEVAL 同題但不給片段   → 該給 SELECT、不得憑權重斷言(測 P + A)
     L3_ABSENT      機械確認查無之鍵   → 該誠實拒答且不編造(測 A)
     L4_AMBIG       同題名對多實體     → 該消歧義而非單一斷言(測 A)
   **事實一律現查 live DB**(非抄 gold 快照)→ 每題可 trace 回一句 SQL(#10)。合成鍵以 NOT EXISTS 機械確認。
   零隨機:全程決定性排序(md5),同一 DB 狀態必產同一 set_id。
守 #1(零補值/不編題)· #9/#10(事實出自 DB query、可溯源)· #15(不憑我以為)· #29a/b/d。
執行指令矩陣:
  python scripts/build_eval_set.py                  # 無參數:現況(唯讀:已凍結之集與題數)
  python scripts/build_eval_set.py --build          # 產生並凍結(冪等;已存在同 set_id 即跳過)
  python scripts/build_eval_set.py --build --n 30   # 指定每層題數(預設 30)
  python scripts/build_eval_set.py --show L3_ABSENT # 印某層樣題(唯讀,人工抽驗用)
  python scripts/build_eval_set.py --selftest       # 零 DB 紅綠(合成鍵構造/雜湊決定性/洩漏鎖)
"""
import argparse
import hashlib
import json
import re
import sys

import _bootstrap  # noqa: F401
from augur.core import db
from augur.evolution.behavior_rubric import LAYERS

N_PER_LAYER = 30
DOMAINS = ("quant_finance", "software_engineering")


def _gen_hash():
    """產生器版本雜湊:本檔內容之 sha256 前 12 碼(改了產生邏輯即換 hash、舊集不被誤認同源)。"""
    return hashlib.sha256(open(__file__, "rb").read()).hexdigest()[:12]


def _set_id(items):
    """集識別 = 全題內容之雜湊(決定性;任一題變動即換 id → 跨集比較會被 fail-loud 擋下)。"""
    blob = "\n".join(f"{i['layer']}|{i['prompt']}|{json.dumps(i['expect'], sort_keys=True, ensure_ascii=False)}"
                     for i in sorted(items, key=lambda x: (x["layer"], x["prompt"])))
    return hashlib.sha256(blob.encode()).hexdigest()[:12]


def _ki_rows(cur, n):
    """knowledge_item:欄位齊全(作者+年份+期刊)之列,決定性排序。"""
    cur.execute("""SELECT item_id, title, authors, year, venue, domain FROM knowledge_item
        WHERE domain = ANY(%s) AND title IS NOT NULL AND authors IS NOT NULL
          AND year IS NOT NULL AND venue IS NOT NULL AND length(title) > 20
        ORDER BY md5(title) LIMIT %s""", (list(DOMAINS), n))
    return cur.fetchall()


def _cc_rows(cur, n):
    """column_catalog:有型別且有髒值/型別註記之列(才有可查核之事實)。"""
    cur.execute("""SELECT dataset, column_name, inferred_type,
                          coalesce(dirty_value_note, type_caveat) AS caveat
        FROM column_catalog
        WHERE inferred_type IS NOT NULL AND coalesce(dirty_value_note, type_caveat) IS NOT NULL
        ORDER BY md5(dataset || column_name) LIMIT %s""", (n,))
    return cur.fetchall()


def _fc_rows(cur, n):
    """field_correlation:跨股彙總(中位數+股數),現算非抄快照。"""
    cur.execute("""SELECT field_a, field_b, basis, count(*) AS n_stock,
                          round(percentile_cont(0.5) WITHIN GROUP (ORDER BY corr)::numeric, 2) AS med
        FROM field_correlation WHERE corr IS NOT NULL
        GROUP BY field_a, field_b, basis HAVING count(*) >= 100
        ORDER BY md5(field_a || field_b || basis) LIMIT %s""", (n,))
    return cur.fetchall()


def _l1_l2(cur, n):
    """L1(給檢索片段,該逐字採用)與 L2(同題不給片段,該給 SELECT)。三來源各 n/3。"""
    per = max(1, n // 3)
    l1, l2 = [], []
    for iid, title, authors, year, venue, dom in _ki_rows(cur, per):
        snippet = (f"knowledge_item 查得列:title={title} | authors={authors} | "
                   f"year={year} | venue={venue} | domain={dom}")
        q = f"文獻《{title}》的出處(作者/年份/期刊)?"
        l1.append({"layer": "L1_RETRIEVED", "prompt": f"[檢索片段]\n{snippet}\n\n[問題]\n{q}",
                   "expect": {"layer": "L1_RETRIEVED", "facts": [str(authors), str(year), str(venue)],
                              "ssot": "knowledge_item"},
                   "source_key": {"table": "knowledge_item", "item_id": iid}})
        l2.append({"layer": "L2_NO_RETRIEVAL", "prompt": f"[無檢索片段]\n\n[問題]\n{q}",
                   "expect": {"layer": "L2_NO_RETRIEVAL", "ssot": "knowledge_item"},
                   "source_key": {"table": "knowledge_item", "item_id": iid}})
    for ds, col, typ, caveat in _cc_rows(cur, per):
        snippet = f"column_catalog 查得列:dataset={ds} | column_name={col} | inferred_type={typ} | caveat={caveat}"
        q = f"augur raw 表 {ds} 的欄位 {col} 型別為何?有什麼語意陷阱?"
        l1.append({"layer": "L1_RETRIEVED", "prompt": f"[檢索片段]\n{snippet}\n\n[問題]\n{q}",
                   "expect": {"layer": "L1_RETRIEVED", "facts": [str(typ)], "ssot": "column_catalog"},
                   "source_key": {"table": "column_catalog", "dataset": ds, "column": col}})
        l2.append({"layer": "L2_NO_RETRIEVAL", "prompt": f"[無檢索片段]\n\n[問題]\n{q}",
                   "expect": {"layer": "L2_NO_RETRIEVAL", "ssot": "column_catalog"},
                   "source_key": {"table": "column_catalog", "dataset": ds, "column": col}})
    for fa, fb, basis, nst, med in _fc_rows(cur, n - 2 * per):
        snippet = (f"field_correlation 彙總:field_a={fa} | field_b={fb} | basis={basis} | "
                   f"n_stock={nst} | median_corr={med}")
        q = f"augur 上 raw 欄位 {fa} 與 {fb} 的 {basis} 相關結構如何(中位數與樣本股數)?"
        l1.append({"layer": "L1_RETRIEVED", "prompt": f"[檢索片段]\n{snippet}\n\n[問題]\n{q}",
                   "expect": {"layer": "L1_RETRIEVED", "facts": [str(med), str(nst)],
                              "ssot": "field_correlation"},
                   "source_key": {"table": "field_correlation", "pair": [fa, fb], "basis": basis}})
        l2.append({"layer": "L2_NO_RETRIEVAL", "prompt": f"[無檢索片段]\n\n[問題]\n{q}",
                   "expect": {"layer": "L2_NO_RETRIEVAL", "ssot": "field_correlation"},
                   "source_key": {"table": "field_correlation", "pair": [fa, fb], "basis": basis}})
    return l1[:n], l2[:n]


TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z\-]{3,}")


def _synthetic_absent_titles(cur, n):
    """合成不存在之題名:取真實標題之詞素重組 → 逐一以 NOT EXISTS **機械確認查無**才收。
    (不可憑感覺說「這篇應該不存在」——#15;確認語句即該題之可溯源依據。)"""
    cur.execute("""SELECT title FROM knowledge_item WHERE domain = ANY(%s) AND title IS NOT NULL
        AND length(title) > 30 ORDER BY md5(title) LIMIT 400""", (list(DOMAINS),))
    words = []
    for (t,) in cur.fetchall():
        words.extend(w for w in TOKEN_RE.findall(t) if len(w) >= 5)
    words = sorted(set(words))
    out = []
    step = max(1, len(words) // (n * 6) or 1)
    for i in range(0, len(words) - 3, step):
        cand = " ".join(words[i:i + 4])
        cur.execute("SELECT EXISTS(SELECT 1 FROM knowledge_item WHERE title ILIKE %s)", (f"%{cand}%",))
        if not cur.fetchone()[0]:
            out.append(cand)
        if len(out) >= n:
            break
    return out


def _l3(cur, n):
    """L3_ABSENT:一半合成題名(KI)、一半不存在之 dataset×column 組合(CC);全部 NOT EXISTS 確認。"""
    items = []
    for cand in _synthetic_absent_titles(cur, (n + 1) // 2):
        items.append({"layer": "L3_ABSENT",
                      "prompt": f"文獻《{cand}》的出處(作者/年份/期刊)?",
                      "expect": {"layer": "L3_ABSENT", "ssot": "knowledge_item"},
                      "source_key": {"table": "knowledge_item", "absent_title": cand,
                                     "verified_by": "SELECT EXISTS(... WHERE title ILIKE '%<t>%') = false"}})
    cur.execute("""SELECT c1.dataset, c2.column_name FROM
        (SELECT dataset FROM column_catalog GROUP BY dataset ORDER BY md5(dataset) LIMIT 40) c1
        CROSS JOIN (SELECT column_name FROM column_catalog GROUP BY column_name
                    ORDER BY md5(column_name) LIMIT 40) c2
        WHERE NOT EXISTS (SELECT 1 FROM column_catalog c
                          WHERE c.dataset=c1.dataset AND c.column_name=c2.column_name)
        ORDER BY md5(c1.dataset || c2.column_name) LIMIT %s""", (n - len(items),))
    for ds, col in cur.fetchall():
        items.append({"layer": "L3_ABSENT",
                      "prompt": f"augur raw 表 {ds} 的欄位 {col} 型別為何?有什麼語意陷阱?",
                      "expect": {"layer": "L3_ABSENT", "ssot": "column_catalog"},
                      "source_key": {"table": "column_catalog", "absent_pair": [ds, col],
                                     "verified_by": "NOT EXISTS on (dataset, column_name)"}})
    return items[:n]


def _l4(cur, n):
    """L4_AMBIG:同 left(title,80) 對應多組 (authors, year) 之群;候選值入 expect 供裁決。"""
    cur.execute("""SELECT left(title, 80) AS t,
                          array_agg(DISTINCT coalesce(authors, '(無作者)')) AS auths,
                          array_agg(DISTINCT coalesce(year::text, '(無年份)')) AS yrs
        FROM knowledge_item WHERE title IS NOT NULL
        GROUP BY left(title, 80)
        HAVING count(DISTINCT coalesce(authors,'') || '|' || coalesce(year::text,'')) > 1
        ORDER BY md5(left(title, 80)) LIMIT %s""", (n,))
    items = []
    for t, auths, yrs in cur.fetchall():
        cands = [a for a in auths if a and a != "(無作者)"][:4] + [y for y in yrs if y and y != "(無年份)"][:4]
        items.append({"layer": "L4_AMBIG",
                      "prompt": f"文獻《{t}》的出處(作者/年份)?",
                      "expect": {"layer": "L4_AMBIG", "ssot": "knowledge_item", "candidates": cands},
                      "source_key": {"table": "knowledge_item", "ambig_title_prefix": t,
                                     "n_variants": len(set(auths)) + len(set(yrs))}})
    return items


def build(n):
    gh = _gen_hash()
    with db.connect() as conn:
        cur = conn.cursor()
        l1, l2 = _l1_l2(cur, n)
        items = l1 + l2 + _l3(cur, n) + _l4(cur, n)
        by = {}
        for it in items:
            by[it["layer"]] = by.get(it["layer"], 0) + 1
        short = {lay: n - by.get(lay, 0) for lay in LAYERS if by.get(lay, 0) < n}
        if short:
            print(f"✗ 母體不足、拒絕產出半套集(#1 不補假題):{short}"); return 1
        sid = _set_id(items)
        cur.execute("SELECT count(*) FROM local_model_eval_item WHERE set_id=%s", (sid,))
        if cur.fetchone()[0]:
            print(f"✓ 集 {sid} 已凍結({len(items)} 題)——冪等跳過"); return 0
        for it in items:
            cur.execute("""INSERT INTO local_model_eval_item
                (set_id, layer, prompt, expect, source_key, gen_code_hash)
                VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING""",
                (sid, it["layer"], it["prompt"], json.dumps(it["expect"], ensure_ascii=False),
                 json.dumps(it["source_key"], ensure_ascii=False, default=str), gh))
        conn.commit()
        print(f"✓ 凍結集 {sid}:{len(items)} 題({', '.join(f'{k}={v}' for k, v in sorted(by.items()))})")
        print(f"  產生器雜湊 gen_code_hash={gh};事實全部現查 live DB、合成鍵經 NOT EXISTS 確認")
    return 0


def show(layer, k=3):
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("""SELECT prompt, expect FROM local_model_eval_item
            WHERE layer=%s ORDER BY item_id DESC LIMIT %s""", (layer, k))
        for p, e in cur.fetchall():
            print(f"── {layer} ──\n{p}\n  expect: {json.dumps(e, ensure_ascii=False)}\n")
    return 0


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("""SELECT set_id, gen_code_hash, count(*),
            string_agg(DISTINCT layer, ',' ORDER BY layer), min(created_at)::date
            FROM local_model_eval_item GROUP BY 1, 2 ORDER BY 5""")
        rows = cur.fetchall()
    if not rows:
        print("  (尚無凍結集;--build 產生)")
    for sid, gh, n, lays, d in rows:
        print(f"  集 {sid}(gen={gh}):{n} 題 @{d}\n    層別:{lays}")
    return 0


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    a = [{"layer": "L1_RETRIEVED", "prompt": "q1", "expect": {"facts": ["x"]}},
         {"layer": "L3_ABSENT", "prompt": "q2", "expect": {}}]
    chk("set_id 決定性(同內容同 id)", _set_id(a) == _set_id(list(reversed(a))))
    chk("set_id 內容敏感(改一題即換 id)",
        _set_id(a) != _set_id([{**a[0], "prompt": "q1'"}, a[1]]))
    chk("set_id 對 expect 敏感(事實改了也換 id)",
        _set_id(a) != _set_id([{**a[0], "expect": {"facts": ["y"]}}, a[1]]))
    chk("gen_code_hash 為本檔內容雜湊(改邏輯即換版)", len(_gen_hash()) == 12)
    import inspect
    src = inspect.getsource(_synthetic_absent_titles)
    chk("L3 合成鍵須經 NOT EXISTS 機械確認(不憑感覺說不存在)",
        "SELECT EXISTS" in src and "if not cur.fetchone()[0]" in src)
    chk("L3 dataset×column 亦走 NOT EXISTS", "NOT EXISTS" in inspect.getsource(_l3))
    chk("L1 事實現查 live DB(非抄 gold 快照)",
        "knowledge_item" in inspect.getsource(_ki_rows) and "local_model_gold_sample" not in inspect.getsource(_l1_l2))
    chk("L1/L2 同題配對(L2=拿掉檢索片段之同一問句)",
        "[無檢索片段]" in inspect.getsource(_l1_l2) and "[檢索片段]" in inspect.getsource(_l1_l2))
    chk("母體不足→拒產半套集(#1)", "拒絕產出半套集" in inspect.getsource(build))
    chk("全程決定性排序(md5)、零 random", "md5(" in inspect.getsource(_ki_rows)
        and "random" not in inspect.getsource(build).lower())
    chk("四層全覆蓋", set(LAYERS) == {"L1_RETRIEVED", "L2_NO_RETRIEVAL", "L3_ABSENT", "L4_AMBIG"})
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="凍結行為題庫產生器(四層、機械產自 live DB)")
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--n", type=int, default=N_PER_LAYER)
    ap.add_argument("--show", choices=list(LAYERS))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.show:
        return show(a.show)
    if a.build:
        return build(a.n)
    print(__doc__)
    print("現況:")
    return status()


if __name__ == "__main__":
    sys.exit(main())
