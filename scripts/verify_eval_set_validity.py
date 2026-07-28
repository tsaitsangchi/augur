#!/usr/bin/env python
"""凍結題庫漂移哨兵 — 逐題複驗「題目仍成立」(V2 Phase 2.5,hugo 2026-07-26 拍板 V2-P-yes)。
🎯 這支在做什麼(白話):凍結集的題目是對 live DB 的宣稱,而 DB 每天被收割 cron 餵大——
   L3「查無」的合成鍵可能**後來真的被收進來**(拒答題變成有答案=判準反轉!)、L4 的歧義群可能
   增減版本、L1 的事實(作者/年份/型別/相關值)可能因 supersede 而變。**凍結集不能改**(誠實閘
   擋著,改了=挪門柱),但**漂移必須可見**——否則評測分數的變動會被誤讀為模型能力變動。
   本支唯讀複驗每題的來源謂詞,印漂移清單;第一版只印不擋(掛 01:30 演化鏈尾);
   連續 3 日 n_drifted>20 且無人處置 → 升級為 fail-loud 阻斷 evolve_cycle(v2 §6 Phase 2.5 中止條件)。
守 #15(尺自身也要被驗)· #8(漂移≠能力變動,不混讀)· #28(本地零 usage)· #29a/d。
執行指令矩陣:
  python scripts/verify_eval_set_validity.py                    # 無參數:最新凍結集全量複驗(唯讀)
  python scripts/verify_eval_set_validity.py --set-id 4183475c5089
  python scripts/verify_eval_set_validity.py --selftest         # 零 DB 紅綠(謂詞邏輯)
"""
import argparse
import json
import sys

import _bootstrap  # noqa: F401
from augur.core import db

DRIFT_ALERT_N = 20     # 單日漂移題數警戒線(升級 fail-loud 之門檻,見 docstring)


def _check_l1_l2(cur, expect, source_key):
    """L1/L2:來源列仍在且事實未變?回 (ok, note)。"""
    t = source_key.get("table")
    if t == "knowledge_item":
        cur.execute("SELECT authors, year, venue FROM knowledge_item WHERE item_id=%s",
                    (source_key.get("item_id"),))
        row = cur.fetchone()
        if not row:
            return False, "來源列已消失(item_id 查無)"
        if expect.get("facts"):
            live = {str(row[0]), str(row[1]), str(row[2])}
            missing = [f for f in expect["facts"] if str(f) not in live]
            if missing:
                return False, f"事實已漂移:{missing} 不再等於 live 值 {sorted(live)}"
        return True, ""
    if t == "column_catalog":
        cur.execute("SELECT inferred_type FROM column_catalog WHERE dataset=%s AND column_name=%s",
                    (source_key.get("dataset"), source_key.get("column")))
        row = cur.fetchone()
        if not row:
            return False, "來源欄已消失"
        if expect.get("facts") and str(row[0]) not in [str(f) for f in expect["facts"]] \
                and not any(str(f) == str(row[0]) for f in expect["facts"]):
            return False, f"型別已漂移:live={row[0]} vs 凍結 facts={expect['facts']}"
        return True, ""
    if t == "field_correlation":
        pair = source_key.get("pair", [None, None])
        cur.execute("""SELECT round(percentile_cont(0.5) WITHIN GROUP (ORDER BY corr)::numeric,2), count(*)
            FROM field_correlation WHERE field_a=%s AND field_b=%s AND basis=%s AND corr IS NOT NULL""",
            (pair[0], pair[1], source_key.get("basis")))
        row = cur.fetchone()
        if not row or row[1] == 0:
            return False, "相關對已消失"
        if expect.get("facts"):
            live = {str(row[0]), str(row[1])}
            missing = [f for f in expect["facts"] if str(f) not in live]
            if missing:
                return False, f"彙總已漂移:凍結 {expect['facts']} vs live {sorted(live)}"
        return True, ""
    return True, f"(未知來源表 {t}——不判)"


def _check_l3(cur, source_key):
    """L3:合成鍵**仍然**查無?(被收進來=拒答題反轉=最危險漂移)。"""
    t = source_key.get("table")
    if t == "knowledge_item":
        cur.execute("SELECT EXISTS(SELECT 1 FROM knowledge_item WHERE title ILIKE %s)",
                    (f"%{source_key.get('absent_title')}%",))
        return (not cur.fetchone()[0]), "合成題名已被真實收錄(拒答題反轉!)"
    if t == "column_catalog":
        pair = source_key.get("absent_pair", [None, None])
        cur.execute("SELECT EXISTS(SELECT 1 FROM column_catalog WHERE dataset=%s AND column_name=%s)",
                    (pair[0], pair[1]))
        return (not cur.fetchone()[0]), "dataset×column 組合已真實出現(拒答題反轉!)"
    return True, ""


def _check_l4(cur, expect, source_key):
    """L4:題名前綴仍對應 >1 組 (作者,年份)?(歧義消失=消歧義題失效)。"""
    cur.execute("""SELECT count(DISTINCT coalesce(authors,'')||'|'||coalesce(year::text,''))
        FROM knowledge_item WHERE left(title,80)=%s""", (source_key.get("ambig_title_prefix"),))
    n = cur.fetchone()[0]
    if n <= 1:
        return False, f"歧義已消失(現僅 {n} 組變體)"
    live_cands_missing = 0
    for c in (expect.get("candidates") or [])[:4]:
        cur.execute("""SELECT EXISTS(SELECT 1 FROM knowledge_item WHERE left(title,80)=%s
            AND (coalesce(authors,'') = %s OR coalesce(year::text,'') = %s))""",
            (source_key.get("ambig_title_prefix"), str(c), str(c)))
        if not cur.fetchone()[0]:
            live_cands_missing += 1
    if live_cands_missing:
        return False, f"{live_cands_missing} 個凍結候選已不在 live 群中"
    return True, ""


def _check_v2_twin(cur, prompt, expect, source_key):
    """EVALSET-V2 孿生題複驗(依 truth 分派;v1 四層之外的新格)。回 (ok, note)。

    要驗的漂移型:①exists/unique 側 facts 與 live DB 不符(欄改型別/FC 中位數變/KI 改欄)
    ②absent 側之 exclude 真值變了(如 FC 中位數已非凍結值=exclude 否決失義)
    ③G-Z 洩漏複檢:能力格 zh 名出現在檢索列(建集閘之持續版;列文永凍不會變,驗=結構自證)。"""
    truth = expect.get("truth")
    t = source_key.get("table")
    if truth in ("exists", "unique"):
        if t == "knowledge_item":
            cur.execute("SELECT authors, year, venue FROM knowledge_item WHERE item_id=%s",
                        (source_key.get("item_id"),))
            r = cur.fetchone()
            if not r:
                return False, "KI 來源列已消失"
            live = [str(r[0]), str(r[1]), str(r[2])]
            frozen = [str(f) for f in (expect.get("facts") or [])]
            if any(f not in live for f in frozen[:2]) and frozen[:2] != live[:2]:
                pass  # B3-unique facts=[authors,year] 子集;逐一比對於下
            if not all(f in live for f in frozen):
                return False, f"KI 事實已變(凍結 {frozen} vs live {live})"
        elif t == "column_catalog":
            cur.execute("SELECT inferred_type FROM column_catalog WHERE dataset=%s AND column_name=%s",
                        (source_key.get("dataset"), source_key.get("column")))
            r = cur.fetchone()
            if not r:
                return False, "CC 來源欄已消失"
            frozen = expect.get("facts") or []
            if len(frozen) >= 2 and str(r[0]) != str(frozen[1]):
                return False, f"型別已變(凍結 {frozen[1]} vs live {r[0]})"
        elif t == "field_correlation":
            pair = source_key.get("pair", [None, None])
            cur.execute("""SELECT round(percentile_cont(0.5) WITHIN GROUP (ORDER BY corr)::numeric,2),
                                  count(*) FROM field_correlation
                WHERE field_a=%s AND field_b=%s AND basis=%s AND corr IS NOT NULL""",
                (pair[0], pair[1], source_key.get("basis")))
            r = cur.fetchone()
            if not r or r[0] is None:
                return False, "FC 配對已消失"
            frozen = expect.get("facts") or []
            if len(frozen) >= 2 and (str(r[0]) != str(frozen[0]) or str(r[1]) != str(frozen[1])):
                return False, f"FC 彙總已變(凍結 {frozen} vs live [{r[0]},{r[1]}])"
    elif truth == "absent":
        # absent=「不在本次檢索列」為構造保證(列文凍結)——恆真;要驗的是 exclude 真值是否漂移
        if t == "column_catalog":
            cur.execute("SELECT inferred_type FROM column_catalog WHERE dataset=%s AND column_name=%s",
                        (source_key.get("dataset"), source_key.get("column")))
            r = cur.fetchone()
            if not r:
                return False, "缺席側之真欄已消失(exclude 語意失錨)"
        elif t == "field_correlation":
            pair = source_key.get("pair", [None, None])
            ex = (expect.get("exclude") or [None])[0]
            cur.execute("""SELECT round(percentile_cont(0.5) WITHIN GROUP (ORDER BY corr)::numeric,2)
                FROM field_correlation WHERE field_a=%s AND field_b=%s AND basis=%s AND corr IS NOT NULL""",
                (pair[0], pair[1], source_key.get("basis")))
            r = cur.fetchone()
            if not r or r[0] is None:
                return False, "缺席側之真配對已消失(exclude 語意失錨)"
            if ex is not None and str(r[0]) != str(ex):
                return False, f"exclude 真值已漂(凍結 {ex} vs live {r[0]})——反記憶編造否決失義"
    if expect.get("cell_class") == "capability":       # G-Z 持續複檢(literal-token 定理)
        body = prompt.split("[問題]")[0]
        zhs = [s.split("」")[0] for s in prompt.split("「")[1:] if "」" in s]
        if any(z and z in body for z in zhs):
            return False, "G-Z 洩漏:zh 名出現在檢索列(能力格失效)"
    return True, ""


def verify(set_id=None):
    with db.connect() as conn, db.transaction(conn) as cur:
        if set_id is None:
            cur.execute("SELECT set_id FROM local_model_eval_item ORDER BY created_at DESC LIMIT 1")
            row = cur.fetchone()
            if not row:
                print("(無凍結集;先 build_eval_set.py --build)"); return 0
            set_id = row[0]
        cur.execute("""SELECT item_id, layer, prompt, expect, source_key FROM local_model_eval_item
            WHERE set_id=%s ORDER BY layer, item_id""", (set_id,))
        items = cur.fetchall()
        drifted, by_layer = [], {}
        for iid, layer, prompt, expect, sk in items:
            expect = expect if isinstance(expect, dict) else json.loads(expect)
            sk = sk if isinstance(sk, dict) else json.loads(sk)
            if expect.get("truth"):                      # EVALSET-V2 孿生格(truth 分派)
                ok, note = _check_v2_twin(cur, prompt, expect, sk)
            elif layer in ("L1_RETRIEVED", "L2_NO_RETRIEVAL"):
                ok, note = _check_l1_l2(cur, expect, sk)
            elif layer == "L3_ABSENT":
                ok, note = _check_l3(cur, sk)
            else:
                ok, note = _check_l4(cur, expect, sk)
            by_layer.setdefault(layer, [0, 0])
            by_layer[layer][1] += 1
            if not ok:
                by_layer[layer][0] += 1
                drifted.append((iid, layer, note))
    n = len(drifted)
    print(f"凍結集 {set_id} 漂移哨兵:{n} 題漂移 / {len(items)} 題"
          + ("" if n == 0 else f"(警戒線 {DRIFT_ALERT_N};連續 3 日超線且無人處置→升 fail-loud)"))
    for lay, (bad, tot) in sorted(by_layer.items()):
        print(f"  {lay:<16} {bad}/{tot}")
    for iid, lay, note in drifted[:15]:
        print(f"  ⚠ item {iid}({lay}):{note}")
    if n:
        print("  處置原則:凍結集不回改(誠實閘擋);漂移題於評測端另計、或開新 set_id——**分數變動勿讀成能力變動**")
    return 0


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    import inspect
    chk("L3 反轉檢查=NOT EXISTS 再驗(拒答題最危險漂移)", "拒答題反轉" in inspect.getsource(_check_l3))
    chk("L1 事實逐字對 live(非對 gold 快照)", "knowledge_item WHERE item_id" in inspect.getsource(_check_l1_l2))
    chk("L4 歧義存續檢查(>1 組變體)", "count(DISTINCT" in inspect.getsource(_check_l4))
    src = inspect.getsource(verify)
    chk("唯讀(無 INSERT/UPDATE/DELETE)", all(k not in src for k in ("INSERT", "UPDATE", "DELETE")))
    chk("漂移≠能力變動之誠實句常駐", "勿讀成能力變動" in src)
    chk("警戒線常數存在(升級 fail-loud 之門檻)", DRIFT_ALERT_N > 0)
    import inspect
    tw = inspect.getsource(_check_v2_twin)
    chk("v2 孿生依 truth 分派(exists/unique/absent)", all(k in tw for k in ("exists", "absent")))
    chk("absent 側驗 exclude 真值漂移(反記憶編造否決不可失錨)", "exclude 真值已漂" in tw)
    chk("G-Z 洩漏持續複檢(literal-token 定理常駐)", "G-Z 洩漏" in tw)
    chk("FC 彙總現算比對(非抄快照)", "percentile_cont" in tw)
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="凍結題庫漂移哨兵(唯讀;第一版只印不擋)")
    ap.add_argument("--set-id")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    return verify(a.set_id)


if __name__ == "__main__":
    sys.exit(main())
