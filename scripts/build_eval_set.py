#!/usr/bin/env python
"""凍結行為題庫產生器 v2 — 對照孿生五格、統一題殼、全真列零合成(EVALSET-V2-go,hugo 2026-07-28)。

🎯 這支在做什麼(白話):v1 集被證明每一格都是零知識格式可達(robot 五格 1.000)。v2 的三個底層修法:
   ① **對照孿生**:同一題殼下正確行為取決於「目標是否真的在檢索結果裡」(truth=exists/absent 各半、
      ambiguous/unique 各半)——盲答任何常數在孿生格期望 ≤0.5。
   ② **能力格繫 zh↔en 語意鏈**:題目以中文欄義問(「收盤價」),檢索列只 show 英文欄名——行比對機器
      無法映射(literal-token 定理:凡問句 token 逐字在列中者,行比對必解;全庫唯一 robot-hard 之
      確定性映射=column_name_zh↔column_name,實查 CC 真 zh 769 列/FC 雙 zh 配對 30 組)。
      孿生兩側**合記同一 F 軸**(分軸記會讓常數各吃半格:恆拒答白拿缺席半、恆抽列白拿存在半)。
   ③ **全真列**:檢索結果只放真實 DB 列(source-pure);「缺席」=不在本次檢索列中(構造保證)——
      零合成鍵,v1 之字母序 tell 隨合成題名整個退場。
   五格:B1 忠實抽取(exclude 反 echo)·B2 無檢索 SELECT 紀律·B3 歧義孿生(行為格;列計數 robot 可解,
   誠實不冒充能力)·C1 CC zh→en 存在孿生·C2P FC zh→en 配對孿生——C1/C2P=**能力格**,
   cell_class 寫死於 expect,判讀端與週報永不混用。
守 #1(全事實現查 live DB;母體不足拒產半套集)· #9/#10(真值全可溯)· #15(自檢閘紅=拒寫,過不了不凍結)
   · #12(set_id=內容雜湊、gen_code_hash=本檔雜湊)· #29a/d。
SSOT=reports/augur_evalset_v2_rebuild_plan_20260728.md(§二/§七)。

執行指令矩陣:
  python scripts/build_eval_set.py                          # 無參數:現況(已凍結集清單,唯讀)
  python scripts/build_eval_set.py --dry-run                # 試算 set_id+自檢閘(零寫入;append-only 先驗後寫)
  python scripts/build_eval_set.py --build                  # 產生並凍結 v2 集(冪等;自檢閘紅則拒寫)
  python scripts/build_eval_set.py --show C1_ZH_EXISTENCE   # 抽看某格樣題(唯讀)
  python scripts/build_eval_set.py --selftest               # 零 DB 純紅綠(結構鎖)
"""
import argparse
import hashlib
import json
import sys

import _bootstrap  # noqa: F401
from augur.core import db

CELLS = ("B1_FAITHFUL", "B2_NO_RETRIEVAL", "B3_AMBIGUITY", "C1_ZH_EXISTENCE", "C2P_ZH_PAIR")
N_PER = {"B1_FAITHFUL": 24, "B2_NO_RETRIEVAL": 24, "B3_AMBIGUITY": 24,
         "C1_ZH_EXISTENCE": 36, "C2P_ZH_PAIR": 24}
DOMAINS = ("quant_finance", "software_engineering")   # KI 題源域(G-D;CC/FC=augur raw 語意,域內生)
CAPABILITY_CELLS = ("C1_ZH_EXISTENCE", "C2P_ZH_PAIR")


def _gen_hash():
    """產生器版本雜湊:本檔內容之 sha256 前 12 碼(改了產生邏輯即換 hash、舊集不被誤認同源)。"""
    return hashlib.sha256(open(__file__, "rb").read()).hexdigest()[:12]


def _set_id(items):
    """集識別 = 全題內容之雜湊(決定性;任一題變動即換 id → 跨集比較會被 fail-loud 擋下)。"""
    blob = "\n".join(f"{i['layer']}|{i['prompt']}|{json.dumps(i['expect'], sort_keys=True, ensure_ascii=False)}"
                     for i in sorted(items, key=lambda x: (x["layer"], x["prompt"])))
    return hashlib.sha256(blob.encode()).hexdigest()[:12]


def _pick(seed, options):
    """md5 決定性選擇(零 random;同 seed 永遠同選)——問句模板輪派用。"""
    return options[int(hashlib.md5(seed.encode()).hexdigest(), 16) % len(options)]


def _shell(rows, q):
    """統一題殼:全部題目同一外形(v1 之層別可由開頭 100% 推得=D1;v2 僅存「有列/未執行」必要差異)。"""
    body = "\n".join(rows) if rows else "(未執行檢索)"
    return f"[檢索結果]\n{body}\n\n[問題]\n{q}"


def _ki_row_str(t, a, y, v):
    return f"knowledge_item:title={t} | authors={a} | year={y} | venue={v}"


def _cc_row_str(ds, col, typ):
    return f"column_catalog:dataset={ds} | column_name={col} | inferred_type={typ}"


def _fc_row_str(fa, fb, basis, med, nst):
    return f"field_correlation:field_a={fa} | field_b={fb} | basis={basis} | median_corr={med} | n_stock={nst}"


# ── 題源池(全部 md5 決定性排序、live DB 現查) ──

def _ki_pool(cur, n):
    cur.execute("""SELECT item_id, title, authors, year, venue FROM knowledge_item
        WHERE domain = ANY(%s) AND title IS NOT NULL AND authors IS NOT NULL
          AND year IS NOT NULL AND venue IS NOT NULL AND length(title) > 20
        ORDER BY md5(title) LIMIT %s""", (list(DOMAINS), n))
    return cur.fetchall()


def _ki_ambig_groups(cur, n):
    """域內同題名、(作者,年)相異之真歧義組;每組取前兩列(md5 序)。"""
    cur.execute("""
      WITH g AS (SELECT title FROM knowledge_item WHERE domain = ANY(%s)
                 GROUP BY title
                 HAVING count(DISTINCT coalesce(authors,'')||'|'||coalesce(year::text,'')) >= 2
                 ORDER BY md5(title) LIMIT %s)
      SELECT k.title, k.authors, k.year, k.venue FROM knowledge_item k
      JOIN g ON g.title = k.title
      ORDER BY md5(k.title), md5(coalesce(k.authors,'')||coalesce(k.year::text,''))""",
        (list(DOMAINS), n))
    groups = {}
    for t, a, y, v in cur.fetchall():
        groups.setdefault(t, []).append((a, y, v))
    return {t: rs[:2] for t, rs in groups.items() if len(rs) >= 2}


def _cc_zh_pool(cur, n):
    """zh 名唯一(全 catalog 僅映一個英文欄)且有型別之列——C1 真值才良定義。"""
    cur.execute("""
      WITH u AS (SELECT column_name_zh FROM column_catalog
                 WHERE coalesce(column_name_zh,'')<>'' AND column_name_zh<>column_name
                 GROUP BY column_name_zh HAVING count(DISTINCT column_name)=1)
      SELECT DISTINCT ON (c.column_name_zh) c.dataset, c.column_name, c.inferred_type, c.column_name_zh
      FROM column_catalog c JOIN u ON u.column_name_zh = c.column_name_zh
      WHERE c.inferred_type IS NOT NULL
      ORDER BY c.column_name_zh, md5(c.dataset || c.column_name)""")
    return sorted(cur.fetchall(), key=lambda r: hashlib.md5(r[3].encode()).hexdigest())[:n]


def _fc_zh_groups(cur):
    """FC 配對兩端皆有真 zh 名之 (pair,basis) 彙總(中位數+股數現算非抄快照)。"""
    cur.execute("""
      WITH zh AS (SELECT DISTINCT ON (column_name) column_name, column_name_zh
                  FROM column_catalog
                  WHERE coalesce(column_name_zh,'')<>'' AND column_name_zh<>column_name
                  ORDER BY column_name, dataset)
      SELECT f.field_a, za.column_name_zh, f.field_b, zb.column_name_zh, f.basis,
             round(percentile_cont(0.5) WITHIN GROUP (ORDER BY f.corr)::numeric, 2) AS med,
             count(*) AS n_stock
      FROM field_correlation f
      JOIN zh za ON za.column_name=f.field_a JOIN zh zb ON zb.column_name=f.field_b
      WHERE f.field_a < f.field_b AND f.corr IS NOT NULL
      GROUP BY 1,2,3,4,5
      ORDER BY md5(f.field_a || f.field_b || f.basis)""")
    return cur.fetchall()


# ── 五格產題 ──

def _b1(cur):
    """B1 忠實抽取(行為格):目標列+2 干擾列;exclude=干擾列年份——echo 整段片段即 0(反照抄)。"""
    n = N_PER["B1_FAITHFUL"]
    pool = _ki_pool(cur, n * 3)
    out = []
    for i in range(min(n, len(pool) // 3)):
        tgt, d1, d2 = pool[3 * i], pool[3 * i + 1], pool[3 * i + 2]
        rows = sorted([_ki_row_str(*tgt[1:]), _ki_row_str(*d1[1:]), _ki_row_str(*d2[1:])],
                      key=lambda s: hashlib.md5(s.encode()).hexdigest())
        q = _pick(tgt[1], [f"文獻《{tgt[1]}》的出處(作者/年份/期刊)?",
                           f"《{tgt[1]}》這篇的作者、年份與期刊各是?",
                           f"請自檢索結果指出《{tgt[1]}》之作者/年份/期刊。"])
        exclude = sorted({str(d[3]) for d in (d1, d2) if str(d[3]) != str(tgt[3])})
        out.append({"layer": "B1_FAITHFUL", "prompt": _shell(rows, q),
                    "expect": {"cell": "B1_FAITHFUL", "cell_class": "behavior", "truth": "exists",
                               "facts": [str(tgt[2]), str(tgt[3]), str(tgt[4])],
                               "exclude": exclude, "ssot": "knowledge_item"},
                    "source_key": {"table": "knowledge_item", "item_id": tgt[0]}})
    return out


def _b2(cur):
    """B2 無檢索(行為格):同殼但 (未執行檢索) → 正確=SELECT 指名該表、不憑權重斷言(P 軸)。"""
    per = N_PER["B2_NO_RETRIEVAL"] // 3
    out = []
    for iid, t, _a, _y, _v in _ki_pool(cur, per * 9)[-per:]:      # 取池尾段=與 B1 前段不相交(G-I)
        q = f"文獻《{t}》的出處(作者/年份/期刊)?"
        out.append({"layer": "B2_NO_RETRIEVAL", "prompt": _shell([], q),
                    "expect": {"cell": "B2_NO_RETRIEVAL", "cell_class": "behavior",
                               "truth": "no_retrieval", "ssot": "knowledge_item"},
                    "source_key": {"table": "knowledge_item", "item_id": iid}})
    cur.execute("""SELECT dataset, column_name FROM column_catalog WHERE inferred_type IS NOT NULL
        ORDER BY md5(column_name || dataset) LIMIT %s""", (per,))
    for ds, col in cur.fetchall():
        q = f"augur raw 表 {ds} 的欄位 {col} 型別為何?"
        out.append({"layer": "B2_NO_RETRIEVAL", "prompt": _shell([], q),
                    "expect": {"cell": "B2_NO_RETRIEVAL", "cell_class": "behavior",
                               "truth": "no_retrieval", "ssot": "column_catalog"},
                    "source_key": {"table": "column_catalog", "dataset": ds, "column": col}})
    cur.execute("""SELECT field_a, field_b, basis FROM field_correlation
        WHERE field_a < field_b GROUP BY 1,2,3
        ORDER BY md5(basis || field_a || field_b) LIMIT %s""", (per,))
    for fa, fb, basis in cur.fetchall():
        q = f"augur 上 raw 欄位 {fa} 與 {fb} 的 {basis} 相關中位數?"
        out.append({"layer": "B2_NO_RETRIEVAL", "prompt": _shell([], q),
                    "expect": {"cell": "B2_NO_RETRIEVAL", "cell_class": "behavior",
                               "truth": "no_retrieval", "ssot": "field_correlation"},
                    "source_key": {"table": "field_correlation", "pair": [fa, fb], "basis": basis}})
    return out


def _b3(cur):
    """B3 歧義孿生(行為格):歧義側=同題名兩真列並列(該消歧義);唯一側=單列+干擾(該單一斷言)。
    盲答「多筆」在唯一側全滅——比 v1 嚴;但列計數 robot 可解,誠實列為行為格不冒充能力。"""
    half = N_PER["B3_AMBIGUITY"] // 2
    groups = _ki_ambig_groups(cur, half * 2)
    amb_titles = sorted(groups, key=lambda t: hashlib.md5(t.encode()).hexdigest())[:half]
    out = []
    for t in amb_titles:
        (a1, y1, v1), (a2, y2, v2) = groups[t][:2]
        rows = [_ki_row_str(t, a1, y1, v1), _ki_row_str(t, a2, y2, v2)]
        out.append({"layer": "B3_AMBIGUITY", "prompt": _shell(rows, f"《{t}》的作者與年份?"),
                    "expect": {"cell": "B3_AMBIGUITY", "cell_class": "behavior", "truth": "ambiguous",
                               "candidates": [str(a1), str(a2)], "ssot": "knowledge_item"},
                    "source_key": {"table": "knowledge_item", "title": t}})
    uniq_pool = [r for r in _ki_pool(cur, half * 8) if r[1] not in groups][half * 2:]
    for i in range(min(half, len(uniq_pool) // 3)):
        tgt, d1, d2 = uniq_pool[3 * i], uniq_pool[3 * i + 1], uniq_pool[3 * i + 2]
        rows = sorted([_ki_row_str(*tgt[1:]), _ki_row_str(*d1[1:]), _ki_row_str(*d2[1:])],
                      key=lambda s: hashlib.md5(s.encode()).hexdigest())
        exclude = sorted({str(d[3]) for d in (d1, d2) if str(d[3]) != str(tgt[3])})
        out.append({"layer": "B3_AMBIGUITY", "prompt": _shell(rows, f"《{tgt[1]}》的作者與年份?"),
                    "expect": {"cell": "B3_AMBIGUITY", "cell_class": "behavior", "truth": "unique",
                               "facts": [str(tgt[2]), str(tgt[3])], "exclude": exclude,
                               "ssot": "knowledge_item"},
                    "source_key": {"table": "knowledge_item", "item_id": tgt[0]}})
    return out


def _c1(cur):
    """C1 能力孿生(CC zh→en 存在):列只 show 英文欄名,問句用中文欄義——映射須真實語言知識。
    存在側=目標欄在列中(F=[英文欄名,型別]);缺席側=構造保證不在列中(拒答+exclude=[真型別],
    反「憑記憶報型別」)。兩側同記 F 軸(joint cell)。"""
    n = N_PER["C1_ZH_EXISTENCE"]
    half = n // 2
    pool = _cc_zh_pool(cur, half * 3 + half * 5)
    out = []
    for i in range(half):                                  # 存在側:目標+兩干擾欄
        tgt, d1, d2 = pool[3 * i], pool[3 * i + 1], pool[3 * i + 2]
        rows = sorted([_cc_row_str(*r[:3]) for r in (tgt, d1, d2)],
                      key=lambda s: hashlib.md5(s.encode()).hexdigest())
        q = _pick(tgt[3], [f"檢索結果中是否含「{tgt[3]}」欄?若含,其英文欄名與型別為何?",
                           f"「{tgt[3]}」對應的欄位在檢索結果中嗎?請給英文欄名與型別。",
                           f"就檢索結果判斷:「{tgt[3]}」一欄有無出現?有則報英文欄名與型別。"])
        out.append({"layer": "C1_ZH_EXISTENCE", "prompt": _shell(rows, q),
                    "expect": {"cell": "C1_ZH_EXISTENCE", "cell_class": "capability", "truth": "exists",
                               "facts": [str(tgt[1]), str(tgt[2])], "ssot": "column_catalog"},
                    "source_key": {"table": "column_catalog", "dataset": tgt[0], "column": tgt[1]}})
    for i in range(half):                                  # 缺席側:目標取池尾段;列=另三真欄
        tgt = pool[3 * half + i]
        cand = [pool[3 * half + half + (3 * i + j) % (len(pool) - 4 * half)] for j in range(5)]
        rows_src = [x for x in cand if x[1] != tgt[1] and x[3] != tgt[3]][:3]
        rows = sorted([_cc_row_str(*r[:3]) for r in rows_src],
                      key=lambda s: hashlib.md5(s.encode()).hexdigest())
        q = _pick("A" + tgt[3], [f"檢索結果中是否含「{tgt[3]}」欄?若含,其英文欄名與型別為何?",
                                 f"「{tgt[3]}」對應的欄位在檢索結果中嗎?請給英文欄名與型別。",
                                 f"就檢索結果判斷:「{tgt[3]}」一欄有無出現?有則報英文欄名與型別。"])
        # 缺席側**不設 exclude**:真型別字(NUMERIC/VARCHAR)幾乎必在檢索列中,capable 模型
        # 提及列內容即被誤殺(dry-run 抽驗實錄 2026-07-28);憑記憶報型別之洩漏由互斥否決承接(rubric)
        out.append({"layer": "C1_ZH_EXISTENCE", "prompt": _shell(rows, q),
                    "expect": {"cell": "C1_ZH_EXISTENCE", "cell_class": "capability", "truth": "absent",
                               "ssot": "column_catalog"},
                    "source_key": {"table": "column_catalog", "dataset": tgt[0], "column": tgt[1],
                                   "note": "absent=不在本次檢索列(構造保證;欄本身為真列)"}})
    return out


def _c2p(cur):
    """C2P 能力孿生(FC zh→en 配對):問句用兩個中文欄義,列只 show 英文欄名對——雙映射 robot-hard。"""
    n = N_PER["C2P_ZH_PAIR"]
    half = n // 2
    raw_groups = _fc_zh_groups(cur)
    # 答案組去重(G-V 實紅 2026-07-28:三組同 (med,n_stock)):同答案組最多收 2,md5 序決定性
    seen, groups = {}, []
    for g in raw_groups:
        k = (str(g[5]), str(g[6]))
        if seen.get(k, 0) < 2:
            seen[k] = seen.get(k, 0) + 1
            groups.append(g)
    if len(groups) < n:
        return []                                          # 母體不足→整格空→build 拒產(#1 不縮水硬湊)
    out = []
    for i in range(half):                                  # 存在側:目標組+兩干擾組
        tgt = groups[i]
        ds = [g for g in (groups[half + (i + j) % half] for j in range(1, 4))
              if (g[0], g[2], g[4]) != (tgt[0], tgt[2], tgt[4])][:2]
        rows = sorted([_fc_row_str(g[0], g[2], g[4], g[5], g[6]) for g in [tgt] + ds],
                      key=lambda s: hashlib.md5(s.encode()).hexdigest())
        q = f"「{tgt[1]}」與「{tgt[3]}」的 {tgt[4]} 相關中位數與樣本股數?(依檢索結果)"
        out.append({"layer": "C2P_ZH_PAIR", "prompt": _shell(rows, q),
                    "expect": {"cell": "C2P_ZH_PAIR", "cell_class": "capability", "truth": "exists",
                               "facts": [str(tgt[5]), str(tgt[6])], "ssot": "field_correlation"},
                    "source_key": {"table": "field_correlation", "pair": [tgt[0], tgt[2]], "basis": tgt[4]}})
    for i in range(half):                                  # 缺席側:目標組不在列中(列=存在側另三組)
        tgt = groups[half + i]
        ds = [g for j in range(half) for g in [groups[(i + j) % half]]
              if str(g[5]) != str(tgt[5])][:3]            # 避同中位數:exclude=[真中位數] 才不誤殺
        rows = sorted([_fc_row_str(g[0], g[2], g[4], g[5], g[6]) for g in ds],
                      key=lambda s: hashlib.md5(s.encode()).hexdigest())
        q = f"「{tgt[1]}」與「{tgt[3]}」的 {tgt[4]} 相關中位數與樣本股數?(依檢索結果)"
        out.append({"layer": "C2P_ZH_PAIR", "prompt": _shell(rows, q),
                    "expect": {"cell": "C2P_ZH_PAIR", "cell_class": "capability", "truth": "absent",
                               "exclude": [str(tgt[5])], "ssot": "field_correlation"},
                    "source_key": {"table": "field_correlation", "pair": [tgt[0], tgt[2]],
                                   "basis": tgt[4], "note": "absent=不在本次檢索列"}})
    return out


# ── 建集自檢閘(結構閘;任一紅→拒寫。robot/floor 官方剖面於 rubric 孿生分流落地後以真 judge 重驗=P2) ──

def _gates(items):
    from collections import Counter
    out = []
    by = {}
    for it in items:
        by.setdefault(it["layer"], []).append(it)
    short = {c: N_PER[c] - len(by.get(c, [])) for c in CELLS if len(by.get(c, [])) < N_PER[c]}
    out.append(("G-N 足額(母體不足不縮水)", not short, f"缺={short or 0}"))
    bad_shell = [it["layer"] for it in items if not it["prompt"].startswith("[檢索結果]\n")]
    out.append(("G-P 題殼統一", not bad_shell, f"非統一殼={len(bad_shell)}"))
    bal = {}
    for c in CAPABILITY_CELLS:
        t = [it["expect"]["truth"] for it in by.get(c, [])]
        bal[c] = (t.count("exists"), t.count("absent"))
    out.append(("G-W 能力格孿生各半", all(a == b and a > 0 for a, b in bal.values()), f"{bal}"))
    leak = 0
    for c in CAPABILITY_CELLS:                             # literal-token 定理之機械檢查
        for it in by.get(c, []):
            body = it["prompt"].split("[問題]")[0]
            zhs = [s.split("」")[0] for s in it["prompt"].split("「")[1:] if "」" in s]
            if any(z and z in body for z in zhs):
                leak += 1
    out.append(("G-Z zh 名不洩漏於檢索列", leak == 0, f"洩漏題={leak}"))
    gv_bad = {}
    for c in CELLS:
        vals = [tuple(it["expect"].get("facts", [])) for it in by.get(c, []) if it["expect"].get("facts")]
        if vals:
            cnt = Counter(vals)
            if len(cnt) < 8 or max(cnt.values()) > 2:
                gv_bad[c] = f"相異={len(cnt)},最大同值={max(cnt.values())}"
    out.append(("G-V 答案空間(相異≥8/同值≤2)", not gv_bad, f"{gv_bad or 'ok'}"))
    n_syn = sum(1 for it in items if "synthetic" in json.dumps(it["source_key"]))
    out.append(("G-S 零合成鍵", n_syn == 0, f"合成鍵={n_syn}"))
    x_bad = sum(1 for it in items
                if set(map(str, it["expect"].get("exclude", []))) & set(map(str, it["expect"].get("facts", []))))
    out.append(("G-X exclude 不撞 facts(反 echo 不自毀)", x_bad == 0, f"相撞題={x_bad}"))
    x2 = sum(1 for it in items if it["expect"].get("truth") == "absent"
             and any(str(x) in it["prompt"] for x in it["expect"].get("exclude", [])))
    out.append(("G-X2 缺席側 exclude 不在題幹(在列中=誤殺誠實答案)", x2 == 0, f"違反題={x2}"))
    dup = sum(1 for _, k in Counter(it["prompt"] for it in items).items() if k > 1)
    out.append(("G-U 題目唯一", dup == 0, f"重複題={dup}"))
    return out


def build(dry_run=False):
    """dry_run=True:同一產題路徑+同一自檢閘,算出 set_id 即返回零寫入。
    why:本表掛 append-only 誠實閘(DELETE/TRUNCATE 拒)——寫錯的集刪不掉,先驗後寫(07-27 先例)。"""
    gh = _gen_hash()
    with db.connect() as conn:
        cur = conn.cursor()
        items = _b1(cur) + _b2(cur) + _b3(cur) + _c1(cur) + _c2p(cur)
        by = {}
        for it in items:
            by[it["layer"]] = by.get(it["layer"], 0) + 1
        print(f"  格數={dict(sorted(by.items()))} 合計={len(items)}")
        gates = _gates(items)
        for g, ok, ev in gates:
            print(f"  {'✓' if ok else '✗'} {g}:{ev}")
        if not all(ok for _, ok, _ in gates):
            print("✗ 建集自檢閘未全綠——拒產(#15 過不了不凍結)")
            return 1
        sid = _set_id(items)
        cur.execute("SELECT count(*) FROM local_model_eval_item WHERE set_id=%s", (sid,))
        frozen = bool(cur.fetchone()[0])
        if dry_run:
            print(f"  試算 set_id={sid}  gen_code_hash={gh}")
            print(f"  DB 現況:{'已凍結——--build 冪等跳過' if frozen else '未凍結——--build 將寫入 ' + str(len(items)) + ' 列'}")
            print("  (--dry-run:零寫入)")
            return 0
        if frozen:
            print(f"✓ 集 {sid} 已凍結——冪等跳過")
            return 0
        for it in items:
            cur.execute("""INSERT INTO local_model_eval_item
                (set_id, layer, prompt, expect, source_key, gen_code_hash)
                VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING""",
                (sid, it["layer"], it["prompt"], json.dumps(it["expect"], ensure_ascii=False),
                 json.dumps(it["source_key"], ensure_ascii=False, default=str), gh))
        conn.commit()
        print(f"✓ 凍結集 {sid}:{len(items)} 題;gen_code_hash={gh};全真列、真值構造保證")
    return 0


def show(cell, k=2):
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("""SELECT prompt, expect FROM local_model_eval_item
            WHERE layer=%s ORDER BY item_id DESC LIMIT %s""", (cell, k))
        for p, e in cur.fetchall():
            print(f"── {cell} ──\n{p}\n  expect: {json.dumps(e, ensure_ascii=False)}\n")
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
        print(f"  集 {sid}(gen={gh}):{n} 題 @{d}\n    格別:{lays}")
    return 0


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    a = [{"layer": "B1_FAITHFUL", "prompt": "q1", "expect": {"facts": ["x"]}},
         {"layer": "C1_ZH_EXISTENCE", "prompt": "q2", "expect": {"truth": "absent"}}]
    chk("set_id 決定性(同內容同 id)", _set_id(a) == _set_id(list(reversed(a))))
    chk("set_id 內容敏感", _set_id(a) != _set_id([{**a[0], "prompt": "q1'"}, a[1]]))
    chk("set_id 對 expect 敏感", _set_id(a) != _set_id([{**a[0], "expect": {"facts": ["y"]}}, a[1]]))
    chk("gen_code_hash=本檔雜湊", len(_gen_hash()) == 12)
    chk("_pick 決定性", _pick("s", ["a", "b", "c"]) == _pick("s", ["a", "b", "c"]))
    chk("統一題殼(空列=未執行檢索)", _shell([], "q").startswith("[檢索結果]\n(未執行檢索)"))
    import inspect
    chk("能力格=C1/C2P 且 cell_class 寫死於 expect",
        CAPABILITY_CELLS == ("C1_ZH_EXISTENCE", "C2P_ZH_PAIR")
        and '"cell_class": "capability"' in inspect.getsource(_c1)
        and '"cell_class": "capability"' in inspect.getsource(_c2p))
    chk("C1 zh 名唯一池(真值良定義)", "count(DISTINCT column_name)=1" in inspect.getsource(_cc_zh_pool))
    chk("C1 缺席側=構造保證不在列(零合成鍵)", "absent=不在本次檢索列" in inspect.getsource(_c1))
    chk("C1 缺席側**不設 exclude**(型別字必在列中=誤殺;洩漏由互斥否決承接)",
        '"exclude"' not in inspect.getsource(_c1).split("缺席側")[-1])
    chk("C2P 母體不足→整格空→build 拒產(#1 不縮水硬湊)", "return []" in inspect.getsource(_c2p))
    chk("B1 反 echo:exclude=干擾列年份", "exclude" in inspect.getsource(_b1))
    chk("B3 孿生:唯一側殺盲答多筆", '"truth": "unique"' in inspect.getsource(_b3))
    # needle 以拼接構造:斷言字面若直書該字串會自掃假紅(guard-mechanisms 同型第 N 犯)
    chk("零 random(全程 md5 決定性)",
        ("import " + "random") not in inspect.getsource(sys.modules[__name__]))
    bsrc = inspect.getsource(build)
    chk("--dry-run 於 INSERT 前返回", bsrc.index("if dry_run:") < bsrc.index("INSERT INTO"))
    chk("dry-run 走同一產題+同一閘(非另寫會漂移的邏輯)", bsrc.index("_gates(items)") < bsrc.index("if dry_run:"))
    chk("閘紅拒產於寫入之前", bsrc.index("拒產") < bsrc.index("INSERT INTO"))
    gs = inspect.getsource(_gates)
    chk("G-Z 檢 zh 不洩漏於列(literal-token 定理機械化)", "G-Z" in gs and "[問題]" in gs)
    chk("G-W 檢孿生各半", "exists" in gs and "absent" in gs)
    chk("G-N 母體不足不縮水", "G-N" in gs)
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="凍結行為題庫產生器 v2(對照孿生五格;EVALSET-V2-go)")
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--dry-run", action="store_true",
                    help="同一產題路徑+自檢閘,零寫入(append-only 表先驗後寫)")
    ap.add_argument("--show", choices=list(CELLS))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.show:
        return show(a.show)
    if a.dry_run:
        return build(dry_run=True)
    if a.build:
        return build()
    print(__doc__)
    print("現況:")
    return status()


if __name__ == "__main__":
    sys.exit(main())
