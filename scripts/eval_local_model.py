#!/usr/bin/env python
"""本地模型行為評測 harness — 多臂對照、三軸 0/1、跨尺 fail-loud(S0/S1,hugo 2026-07-26 拍板)。
🎯 這支在做什麼(白話):在**凍結題庫**上跑多個「臂」並逐軸記帳。舊評測敗因有三,本支逐一封死:
   ①舊尺樣板即得分 → 每輪**強制內建地板臂**(常數樣板,離線零成本);候選未勝地板即無證據力。
   ②舊評測評的是被截斷的思考鏈(實測 100% done_reason=length)→ 本支預設 grammar 強制(format JSON schema),
     並**逐題記 done_reason**;截斷者記 INVALID 不計分(不補假分 #1)。
   ③舊「固定集」隨語料成長漂移 → 本支把 set_id 與 eval_code_hash 寫進帳本,跨集比較時 fail-loud 拒絕。
   另設**上界臂**(用 expect 直接組出理想答案):它若拿不到滿分,代表尺本身壞了 → 先修尺再談模型。
   臂:ceiling(上界,離線) · floor(地板,離線) · shuffled(答非所問,離線) · base(裸模型) ·
      grammar(格式強制) · behavior(格式+行為守則=S1 零訓練上界) · pack:<id>(現行 prompt-pack)
守 #1(逾時/截斷不補分)· #9/#10(分數皆出自實跑、逐題落帳)· #15(地板臂=假兆機械鎖)· #28(全本地零 token)· #29a/d。
執行指令矩陣:
  python scripts/eval_local_model.py                          # 無參數:現況(唯讀:已跑之臂與三軸)
  python scripts/eval_local_model.py --offline-arms           # 只跑三個離線臂(零 LLM、數秒、必跑)
  python scripts/eval_local_model.py --arm grammar            # 跑單一臂
  python scripts/eval_local_model.py --arm behavior --limit 8 # 小樣本煙測
  python scripts/eval_local_model.py --all                    # 離線三臂 + 四個 LLM 臂(耗時)
  python scripts/eval_local_model.py --compare                # 對照表(唯讀帳本,同 set_id 才並排)
  python scripts/eval_local_model.py --selftest               # 零 DB 零 LLM 紅綠
"""
import argparse
import hashlib
import json
import sys
import urllib.error
import urllib.request

import _bootstrap  # noqa: F401
from augur.core import db
from augur.evolution.behavior_rubric import BOILERPLATE_ARM, aggregate, judge

OLLAMA = "http://127.0.0.1:11434/api/generate"
MODEL = "qwen3:4b"
TIMEOUT = 600            # 舊值 150s 造成靜默跳題;拉高並改記 INVALID(#1 不補假分)
NUM_PREDICT = 1200       # 舊值 400 → 實測 100% done_reason=length(評到的是思考鏈非答案)

# grammar 強制:abstain 為布林,攤平時 true→「查無」(behavior_rubric.flatten_response 之約定)
FORMAT_SCHEMA = {
    "type": "object",
    "properties": {"answer": {"type": "string"}, "ssot_table": {"type": "string"},
                   "sql": {"type": "string"}, "abstain": {"type": "boolean"}},
    "required": ["answer", "abstain"],
}

BEHAVIOR_PROMPT = """你是 augur 的資料層助手。回答時**一律**遵守四條守則:
1. 題目若附[檢索片段],**逐字**採用片段中的數值、年份、表名、欄名——不得改寫、不得四捨五入、不得補述片段沒有的內容。
2. 一律指明事實出自哪張 SSOT 表(如 knowledge_item / column_catalog / field_correlation)。
3. 題目若**未附**檢索片段,你**不知道**答案:不要憑記憶回答,改輸出一句可執行的 SELECT 讓人自行查證。
4. 若該鍵在庫中查無,誠實說「查無」並把 abstain 設為 true——**絕不編造**作者、年份或型別;
   若同一題名對應多筆不同紀錄,列出多個候選或明說有多筆、請對方指明,不要只挑一個當答案。"""


def _code_hash():
    """評測器版本雜湊——**只涵蓋會影響分數的東西**:判準模組全文 + 產答路徑 + 生成參數。
    刻意**不含** compare/status/selftest 等報表層(改報表不等於換尺,否則舊 run 會被無謂作廢)。"""
    import inspect
    from augur.evolution import behavior_rubric
    h = hashlib.sha256(open(behavior_rubric.__file__, "rb").read())
    for fn in (_ideal_answer, _answer_for, _ask, run_arm):
        h.update(inspect.getsource(fn).encode())
    h.update(json.dumps([MODEL, NUM_PREDICT, TIMEOUT, FORMAT_SCHEMA, BEHAVIOR_PROMPT],
                        sort_keys=True, ensure_ascii=False).encode())
    return h.hexdigest()[:12]


def _ideal_answer(expect):
    """由 expect 直接組出理想答案(上界臂用)。它拿不到滿分=尺壞了,不是模型不行。"""
    lay, ssot = expect["layer"], expect.get("ssot", "")
    if lay == "L1_RETRIEVED":
        return f"依 {ssot}:" + "、".join(str(f) for f in expect.get("facts", []))
    if lay == "L2_NO_RETRIEVAL":
        return f"未取得檢索片段,不憑記憶作答。請執行:SELECT * FROM {ssot} WHERE ...;"
    if lay == "L3_ABSENT":
        return f"查無此鍵。{ssot} 中不存在該筆,請以 SELECT 確認。"
    cands = expect.get("candidates", [])[:2]
    return f"此題名對應多筆紀錄(歧義),候選:{'、'.join(str(c) for c in cands)};請指明是哪一筆。"


def _load_set(cur, set_id=None, limit=None):
    if set_id is None:
        cur.execute("SELECT set_id FROM local_model_eval_item ORDER BY created_at DESC LIMIT 1")
        row = cur.fetchone()
        if not row:
            raise RuntimeError("尚無凍結集——先跑 scripts/build_eval_set.py --build")
        set_id = row[0]
    cur.execute("""SELECT item_id, layer, prompt, expect FROM local_model_eval_item
        WHERE set_id=%s ORDER BY layer, item_id""" + (" LIMIT %s" if limit else ""),
        (set_id, limit) if limit else (set_id,))
    return set_id, cur.fetchall()


def _ask(prompt, system=None, grammar=False):
    """回 (text, done_reason, n_tok)。逾時/連線失敗回 (None, 'error:…', 0) → 該題記 INVALID。"""
    body = {"model": MODEL, "prompt": prompt, "stream": False, "think": False,
            "options": {"temperature": 0, "num_predict": NUM_PREDICT}}
    if system:
        body["system"] = system
    if grammar:
        body["format"] = FORMAT_SCHEMA
    req = urllib.request.Request(OLLAMA, json.dumps(body).encode(), {"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            o = json.loads(r.read())
        return o.get("response", ""), o.get("done_reason", "?"), o.get("eval_count", 0)
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as e:
        return None, f"error:{type(e).__name__}", 0


ARMS_OFFLINE = ("ceiling", "floor", "shuffled", "mismatched")
ARMS_LLM = ("base", "grammar", "behavior")


def _answer_for(arm, items, i, pack_text=None):
    """離線臂直接產字串;LLM 臂實呼叫。回 (text, done_reason, n_tok)。"""
    _iid, _lay, prompt, expect = items[i]
    if arm == "ceiling":
        return _ideal_answer(expect), "offline", 0
    if arm == "floor":
        return BOILERPLATE_ARM, "offline", 0
    if arm == "shuffled":                       # 同層鄰題之理想答案:行為類別對、內容錯
        return _ideal_answer(items[(i + 1) % len(items)][3]), "offline", 0
    if arm == "mismatched":                     # **跨層**理想答案:行為類別就選錯(如對 L1 題誠實拒答)
        return _ideal_answer(items[(i + len(items) // 2 + 1) % len(items)][3]), "offline", 0
    if arm == "base":
        return _ask(prompt)
    if arm == "grammar":
        return _ask(prompt, grammar=True)
    if arm == "behavior":
        return _ask(prompt, system=BEHAVIOR_PROMPT, grammar=True)
    if arm.startswith("pack:"):
        return _ask(prompt, system=pack_text, grammar=True)
    raise ValueError(f"未知臂:{arm}")


def _pack_text(cur, version_id):
    cur.execute("SELECT eval_result FROM local_model_version WHERE version_id=%s", (version_id,))
    row = cur.fetchone()
    if not row or not row[0] or "sample_ids" not in row[0]:
        raise RuntimeError(f"{version_id} 無 sample_ids、無法重建 pack 文字")
    cur.execute("""SELECT prompt, gold_answer FROM local_model_gold_sample
        WHERE sample_id = ANY(%s) ORDER BY sample_id""", (row[0]["sample_ids"],))
    return "\n\n".join(f"Q: {q}\nA: {a}" for q, a in cur.fetchall())


def run_arm(arm, set_id=None, limit=None, quiet=False):
    ch = _code_hash()
    with db.connect() as conn:
        cur = conn.cursor()
        set_id, items = _load_set(cur, set_id, limit)
        pack = _pack_text(cur, arm.split(":", 1)[1]) if arm.startswith("pack:") else None
        judgements, detail, n_valid = [], [], 0
        for i, (iid, lay, _p, expect) in enumerate(items):
            text, done, ntok = _answer_for(arm, items, i, pack)
            if text is None or done == "length":       # 逾時或被截斷=沒答完 → 不計分(#1)
                detail.append({"item_id": iid, "layer": lay, "invalid": done, "n_tok": ntok})
                continue
            j = judge(text, expect)
            judgements.append(j); n_valid += 1
            detail.append({"item_id": iid, "layer": lay, "f": j["f"], "p": j["p"], "a": j["a"],
                           "done": done, "n_tok": ntok, "head": j["text"][:200]})
            if not quiet and (i + 1) % 20 == 0:
                print(f"    …{i + 1}/{len(items)}")
        agg = aggregate(judgements)
        invalid = n_valid < len(items)
        run_id = "ev_" + hashlib.sha256(f"{set_id}|{ch}|{arm}|{MODEL}|{len(items)}".encode()).hexdigest()[:14]
        cur.execute("""INSERT INTO local_model_eval_run
            (run_id, set_id, eval_code_hash, arm, model, n_items, n_valid,
             axis_f, axis_p, axis_a, is_invalid, detail)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (run_id) DO NOTHING""",
            (run_id, set_id, ch, arm, MODEL, len(items), n_valid,
             agg["axis_f"], agg["axis_p"], agg["axis_a"], invalid,
             json.dumps({"per_item": detail}, ensure_ascii=False)))
        conn.commit()
    flag = f"  ⚠ {len(items) - n_valid} 題無效(逾時/截斷)、整輪標 INVALID" if invalid else ""
    print(f"  [{arm:<14}] F={_fmt(agg['axis_f'])} P={_fmt(agg['axis_p'])} A={_fmt(agg['axis_a'])} "
          f"(n_valid={n_valid}/{len(items)}){flag}")
    return agg


def _fmt(v):
    return "  n/a" if v is None else f"{v:5.3f}"


def compare(set_id=None):
    with db.connect() as conn, db.transaction(conn) as cur:
        if set_id is None:
            cur.execute("SELECT set_id FROM local_model_eval_run ORDER BY created_at DESC LIMIT 1")
            row = cur.fetchone()
            if not row:
                print("(尚無評測 run)"); return 1
            set_id = row[0]
        cur.execute("""SELECT eval_code_hash, max(created_at) FROM local_model_eval_run
            WHERE set_id=%s GROUP BY 1 ORDER BY 2 DESC""", (set_id,))
        hrows = cur.fetchall()
        cur_hash = hrows[0][0]
        # 只並排**同一把尺**的臂;其他尺之 run 明列為排除、不靜默隱藏(P4.E3 留檔、#8 誠實)
        # 每臂取**最完整**之 run(n_items 大者優先、同大取新);2026-07-26 抓到:--limit 3 探針
        # 因較新而遮蔽了 n=120 全量 run,對照表顯示 3/3=誤導。完整度優先於新鮮度。
        cur.execute("""SELECT DISTINCT ON (arm) arm, axis_f, axis_p, axis_a, n_valid, n_items, is_invalid
            FROM local_model_eval_run WHERE set_id=%s AND eval_code_hash=%s
            ORDER BY arm, n_items DESC, created_at DESC""", (set_id, cur_hash))
        rows = cur.fetchall()
    print(f"凍結集 {set_id} · 評測器 {cur_hash} 之對照(三軸各自成欄、永不平均):")
    print(f"  {'arm':<16}{'F 事實':>9}{'P 出處':>9}{'A 拒答':>9}{'valid':>9}")
    for arm, f, p, a, nv, ni, inv in rows:
        print(f"  {arm:<16}{_fmt(f):>9}{_fmt(p):>9}{_fmt(a):>9}{f'{nv}/{ni}':>9}" + ("  ⚠INVALID" if inv else ""))
    if len(hrows) > 1:
        print(f"  ⓘ 本集另有 {len(hrows) - 1} 把舊尺之 run 已排除不並排(尺不同=分數不可比;留檔未刪):"
              f"{[h for h, _ in hrows[1:]]}")
    _print_layer_matrix(set_id, cur_hash)
    print("  ⚠ 判讀鐵則:任何臂未同時勝過 floor 與 mismatched 即無證據力;"
          "shuffled 高分處表示該軸測的是行為類別而非內容;ceiling 未達 1.000 表示尺本身有問題")
    return 0


def _print_layer_matrix(set_id, cur_hash):
    """layer×axis 拆解——彙總分會把有鑑別力與無鑑別力的格混在一起(V2 Phase 0.5)。
    每格常駐印 shuffled 值:shuffled 高 ⇒ 該格「同層答錯內容」也拿高分 ⇒ 無內容鑑別力,
    該格之進步只能宣稱「更會選對行為」、不得宣稱「答得更準」。"""
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("""SELECT r.arm, d.v->>'layer' AS layer,
                round(avg((d.v->>'f')::numeric), 3), round(avg((d.v->>'p')::numeric), 3),
                round(avg((d.v->>'a')::numeric), 3)
            FROM local_model_eval_run r, jsonb_array_elements(r.detail->'per_item') AS d(v)
            WHERE r.set_id=%s AND r.eval_code_hash=%s
              AND r.n_items = (SELECT max(n_items) FROM local_model_eval_run
                               WHERE set_id=%s AND eval_code_hash=%s)
            GROUP BY r.arm, d.v->>'layer' ORDER BY 2, 1""", (set_id, cur_hash, set_id, cur_hash))
        rows = cur.fetchall()
    if not rows:
        return
    by = {}
    for arm, lay, f, p, a in rows:
        by.setdefault(lay, {})[arm] = (f, p, a)
    print("\n  逐層拆解(彙總分會混淆有/無鑑別力之格):")
    for lay in sorted(by):
        arms = by[lay]
        axis = next((k for k, i in (("F", 0), ("P", 1), ("A", 2))
                     if arms.get("ceiling") and arms["ceiling"][i] is not None), None)
        i = {"F": 0, "P": 1, "A": 2}[axis] if axis else 0
        sh = arms.get("shuffled", (None,) * 3)[i]
        verdict = ("**無內容鑑別力**(同層答錯內容也拿 %.3f)" % sh if sh is not None and sh >= 0.5
                   else "有內容鑑別力(shuffled %.3f)" % sh if sh is not None else "")
        print(f"    {lay:<16} 軸={axis}  {verdict}")
        for arm in sorted(arms):
            v = arms[arm][i]
            print(f"      {arm:<12}{'  n/a' if v is None else f'{float(v):6.3f}'}")
    return


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("""SELECT set_id, arm, axis_f, axis_p, axis_a, n_valid, n_items, created_at::date
            FROM local_model_eval_run ORDER BY created_at DESC LIMIT 12""")
        rows = cur.fetchall()
    if not rows:
        print("  (尚無評測 run;--offline-arms 先跑三個離線臂)")
    for sid, arm, f, p, a, nv, ni, d in rows:
        print(f"  {sid} {arm:<16} F={_fmt(f)} P={_fmt(p)} A={_fmt(a)} ({nv}/{ni}) @{d}")
    return 0


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    import inspect
    for lay, must in (("L1_RETRIEVED", "依"), ("L2_NO_RETRIEVAL", "SELECT"),
                      ("L3_ABSENT", "查無"), ("L4_AMBIG", "歧義")):
        e = {"layer": lay, "ssot": "knowledge_item", "facts": ["A", "2021"], "candidates": ["X", "Y"]}
        chk(f"上界臂 {lay} 自身可滿分", judge(_ideal_answer(e), e) and must in _ideal_answer(e))
    for lay in ("L1_RETRIEVED", "L2_NO_RETRIEVAL", "L3_ABSENT", "L4_AMBIG"):
        e = {"layer": lay, "ssot": "knowledge_item", "facts": ["A", "2021"], "candidates": ["X", "Y"]}
        j = judge(_ideal_answer(e), e)
        chk(f"上界臂 {lay} 三軸皆非 0", all(v in (None, 1) for v in (j["f"], j["p"], j["a"])))
        jf = judge(BOILERPLATE_ARM, e)
        chk(f"地板臂 {lay} 全滅", all(v in (None, 0) for v in (jf["f"], jf["p"], jf["a"])))
    src = inspect.getsource(run_arm)
    chk("截斷/逾時記 INVALID 不計分(#1)", 'done == "length"' in src and "continue" in src)
    chk("整輪 INVALID 旗標入帳", "is_invalid" in src and "n_valid < len(items)" in src)
    chk("set_id 與 eval_code_hash 皆入帳(跨尺可辨)", "eval_code_hash" in src and "set_id" in src)
    csrc = inspect.getsource(compare)
    chk("compare 結構上不可能混尺(查詢綁單一 eval_code_hash)",
        "AND eval_code_hash=%s" in csrc and "cur_hash" in csrc)
    chk("compare 對被排除之舊尺明列不靜默", "已排除不並排" in csrc and "留檔未刪" in csrc)
    chk("compare 常駐印判讀鐵則(不靠人記得)",
        "未同時勝過 floor 與 mismatched" in csrc and "測的是行為類別而非內容" in csrc)
    chk("grammar 強制 schema 含 abstain 布林", FORMAT_SCHEMA["properties"]["abstain"]["type"] == "boolean")
    chk("num_predict 已離開 400 截斷區", NUM_PREDICT >= 1000)
    chk("timeout 已離開 150s", TIMEOUT >= 600)
    chk("行為守則四條齊(逐字/引表/未檢索給SQL/查無拒答)",
        all(k in BEHAVIOR_PROMPT for k in ("逐字", "SSOT", "SELECT", "查無", "絕不編造")))
    chk("離線四臂零 LLM(可零成本必跑;含跨層 mismatched 控制)",
        set(ARMS_OFFLINE) == {"ceiling", "floor", "shuffled", "mismatched"})
    chk("eval_code_hash 涵蓋判準模組(判準改了也換版)", "behavior_rubric" in inspect.getsource(_code_hash))
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="本地模型行為評測 harness(多臂、三軸、跨尺 fail-loud)")
    ap.add_argument("--arm")
    ap.add_argument("--offline-arms", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--set-id")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--compare", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.compare:
        return compare(a.set_id)
    if a.offline_arms or a.all:
        print("離線臂(零 LLM):")
        for arm in ARMS_OFFLINE:
            run_arm(arm, a.set_id, a.limit)
    if a.all:
        print("LLM 臂:")
        for arm in ARMS_LLM:
            print(f"  跑 {arm}…")
            run_arm(arm, a.set_id, a.limit)
    elif a.arm:
        run_arm(a.arm, a.set_id, a.limit)
    if a.arm or a.offline_arms or a.all:
        return 0
    print(__doc__)
    print("現況:")
    return status()


if __name__ == "__main__":
    sys.exit(main())
