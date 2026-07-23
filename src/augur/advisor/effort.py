"""effort — 前台推理力度檔位(fast/think/ultracode)之 tier 解析+llm 工廠+審議路由(前台檔位計畫 F1)。

🎯 這支在做什麼(白話):把「仿 Claude 前台」的模型×effort 選擇接進 advisor——
   fast/think=參數檔(住 DB config,#29b);**ultracode=審議引擎轉接**:機械可驗宣稱(表/欄/列數/檔案/
   隔離)交 engine.deliberate → 5 oracle 裁決 → verdict_block 機械模板併入回覆(**宣稱原文=LLM 提出、
   非系統背書;系統背書僅及 oracle 證據行**;§1.4 雙標示)。不合格題誠實 fallback 走 advise()。
   **對諮詢資料面唯讀;本檔零資料庫寫入語句**(寫入全在 deliberation 既有寫點;V2 file_grep 可驗)。
   單飛鎖(4GB 現實):同時僅 1 場審議,忙碌即回機械誠實句。config 讀取自管短連線 fresh 讀,翻旗標免重啟。

守 #12(advise 仍唯一諮詢編排出口;config 讀取走 engine_config)· #15(LLM 意見零證據力;誠實 fallback)·
   #26(escalated=進人裁佇列)· #29b(檔位參數/詞表住 DB)。SSOT=augur_frontend_tiers_ultracode_backbone_plan_20260711.md §2/§3。

執行指令矩陣（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.advisor.effort              # 印用途+公開入口（唯讀）
  python -m augur.advisor.effort --selftest   # 純紅綠自測（零 IO）
"""
import sys
import threading
from collections import namedtuple
from pathlib import Path

from augur.core import db
from augur.advisor import ollama
from augur.deliberation import engine_config

REPO = Path(__file__).resolve().parents[3]

Tier = namedtuple("Tier", ["id", "model", "effort"])
UltraResult = namedtuple("UltraResult", ["session_id", "rows", "busy", "fallback_note"])

_ULTRA_LOCK_HOLDER = {}   # config 變更 max_concurrent 時重建;鍵=maxc


class UnknownTierError(ValueError):
    pass


def load_tiers():
    """讀 frontend_tiers config(自管短連線、fresh 讀=翻旗標免重啟);缺列/DB 例外 → {'enabled': False}(fail-safe)。"""
    try:
        with db.connect() as conn, db.transaction(conn) as cur:
            cfg, _sha = engine_config.load_rules(cur, "frontend_tiers", fresh=True)
        return cfg if cfg and cfg.get("enabled") is not None else {"enabled": False}
    except Exception as e:
        print(f"[effort] config 讀取失敗,fail-safe 走 legacy:{type(e).__name__}", file=sys.stderr)
        return {"enabled": False}


def resolve_tier(model_field, cfg):
    """model 欄 → Tier。'augur-advisor'/None/空 → default_tier;未知 → UnknownTierError(handler 轉 400)。"""
    tiers = cfg.get("tiers", {})
    key = (model_field or "").strip()
    if key in ("", "augur-advisor"):
        key = cfg.get("default_tier", "")
    if key not in tiers:
        raise UnknownTierError(f"未知 tier {model_field!r}(可用:{sorted(tiers)})")
    t = tiers[key]
    return Tier(key, t["model"], t["effort"])


def make_tier_llm_fn(tier, cfg):
    """fast/think 檔 llm_fn(參數全出 config);think 檔包截斷偵測(strip_think 後空 → 機械誠實句)。"""
    p = cfg["effort_params"]["think" if tier.effort == "think" else "fast"]
    fn = ollama.make_llm_fn(model=tier.model, think=p["think"], strip_quotes=True,
                            timeout=p["timeout_s"],
                            options={"temperature": p["temperature"], "num_predict": p["num_predict"]})
    if tier.effort != "think":
        return fn

    def wrapped(prompt):
        out = fn(prompt)
        if not (out or "").strip():   # 深思段吃滿 num_predict 截斷 → strip_think fail-closed 全刪=空
            return "(深思輸出因長度上限截斷,無法給出完整回答——請改 fast 檔、或簡化問題再試。)"
        return out
    return wrapped


def probe_speed(model_tag):
    """UI 誠實速度顯示:deliberation_model_probe 實測 avg tok/s;無列 → None(顯「未量測」,#9(b) 不寫死)。"""
    try:
        with db.connect() as conn, db.transaction(conn) as cur:
            cur.execute("SELECT round(avg(tok_per_s),1)::float8 FROM deliberation_model_probe "
                        "WHERE model_tag=%s AND tok_per_s IS NOT NULL", (model_tag,))
            row = cur.fetchone()
        return row[0] if row and row[0] else None
    except Exception:
        return None


def route_ultracode(query, cfg, cur):
    """eligibility+標的組法(§2.2/2.2.1;機械規則零 LLM)。回 (eligible, topic, target_block)。"""
    kw = cfg.get("ultra", {}).get("eligibility_keywords", [])
    if not any(k in query for k in kw):
        return False, "", ""
    topic = "[frontend] " + query
    # 檔案標的:token 是 repo 相對路徑且存在
    for tok in query.replace("，", " ").replace(",", " ").split():
        cand = tok.strip("。?？!()「」")
        if "/" in cand and ".." not in cand and (REPO / cand).is_file():
            return True, topic, f"目標檔案 {cand}(內容可經 file_grep 錨定)\n{query}"
    # 表標的:token 對 information_schema 現有表機械比對
    import re
    toks = list({t for t in re.findall(r"[A-Za-z_][A-Za-z0-9_]{3,}", query)})[:12]
    hits = []
    if toks:
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' "
                    "AND table_name = ANY(%s)", (toks,))
        hits = [r[0] for r in cur.fetchall()]
    if hits:
        return True, topic, f"目標=資料庫表 {','.join(sorted(hits)[:4])}(schema/列數可經 information_schema/db_query 錨定)\n{query}"
    return True, topic, f"目標=augur 資料庫與 repo(無單一檔案標的)\n{query}"


def _lock(maxc):
    if maxc not in _ULTRA_LOCK_HOLDER:
        _ULTRA_LOCK_HOLDER[maxc] = threading.Semaphore(maxc)
    return _ULTRA_LOCK_HOLDER[maxc]


BUSY_NOTE = ("審議引擎使用中(單飛):另一場審議進行中,其帳本將完整落庫。"
             "請稍候再送,或改用 fast/think 檔。")
FALLBACK_NOTE = "此題不屬機械可驗域,ultracode 檔改以一般誠實管線作答。"


def run_ultracode(query, cfg, progress_cb=None):
    """單飛鎖 → engine.deliberate → 回讀裁決列。回 UltraResult;不合格 → fallback_note;鎖忙 → busy。
    本函式零直接資料庫寫入(全在 engine/ledger/verifiers 既有寫點)。"""
    from augur.deliberation import engine
    u = cfg.get("ultra", {})
    with db.connect() as conn, db.transaction(conn) as cur:
        eligible, topic, target_block = route_ultracode(query, cfg, cur)
    if not eligible:
        return UltraResult(None, [], False, FALLBACK_NOTE)
    sem = _lock(int(u.get("max_concurrent", 1)))
    if not sem.acquire(blocking=False):
        return UltraResult(None, [], True, BUSY_NOTE)
    try:
        sid, _tally = engine.deliberate(topic, target_block, "skeptic",
                                        u.get("engine_model", "qwen3:4b"),
                                        int(u.get("max_claims", 6)),
                                        float(u.get("engine_timeout_s", 240)),
                                        progress_cb=progress_cb)
    finally:
        sem.release()
    if not sid:
        return UltraResult(None, [], False, FALLBACK_NOTE)
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("""SELECT c.claim_id, c.claim_text, c.assigned_verifier, c.anchor, c.status,
                              COALESCE(c.semantic_bound,false),
                              (SELECT v.evidence FROM deliberation_verdict v WHERE v.claim_id=c.claim_id
                               ORDER BY v.ran_at DESC LIMIT 1),
                              (SELECT e.escalation_id FROM deliberation_escalation e WHERE e.claim_id=c.claim_id
                               ORDER BY e.escalation_id DESC LIMIT 1)
                       FROM deliberation_claim c WHERE c.session_id=%s ORDER BY c.claim_id""", (sid,))
        rows = cur.fetchall()
    return UltraResult(sid, rows, False, None)


def verdict_block(result):
    """§1.4 分級機械模板(零-LLM 模板;宣稱原文逐行標「LLM 提出」;背書數字唯 evidence 行)。"""
    if result.busy or result.fallback_note:
        return result.fallback_note or BUSY_NOTE
    lines = ["── 本地審議裁決(模板機械;宣稱原文=LLM 提出、非系統背書;系統背書僅及 oracle 證據行)──"]
    for _cid, txt, ver, anc, st, bound, ev, esc in result.rows:
        claim = f"〔宣稱原文(LLM 提出):{txt[:90]}〕"
        if st == "confirmed" and bound:
            lines.append(f"✓ confirmed·bound {claim}")
            lines.append(f"   oracle 證據:{ver}:{(anc or '')[:60]} → {(ev or '')[:100]}")
        elif st == "confirmed":
            lines.append(f"◐ anchor-only(降格){claim}:錨點成立、語意未綁——僅代表錨點查證通過,不背書宣稱全文")
            lines.append(f"   oracle 證據:{ver}:{(anc or '')[:60]} → {(ev or '')[:100]}")
        elif st == "refuted":
            lines.append(f"✗ 已被 oracle 反證 {claim}")
            lines.append(f"   oracle 證據:{(ev or '')[:110]}")
        else:
            lines.append(f"⚠ 已進人裁佇列 #{esc or '?'} {claim}(誠實「待人裁」非失敗)")
    lines.append("(本檔位僅對機械可驗宣稱給 oracle 裁決;其餘為 LLM 白話+誠實 guard 鏈;LLM 意見零證據力)")
    lines.append("(白話解讀與審議裁決各自獨立產生;兩者不一致時,以上方 oracle 裁決為準)")
    return "\n".join(lines)


def _selftest():
    """純紅綠自測(零 IO):resolve_tier 路由+UnknownTierError、verdict_block 分級模板不變式。"""
    ok = True
    def chk(name, cond):
        nonlocal ok; ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")
    cfg = {"default_tier": "fast",
           "tiers": {"fast": {"model": "m1", "effort": "fast"},
                     "think": {"model": "m2", "effort": "think"}}}
    chk("resolve_tier default(augur-advisor→fast)", resolve_tier("augur-advisor", cfg) == Tier("fast", "m1", "fast"))
    chk("resolve_tier 顯式 think", resolve_tier("think", cfg) == Tier("think", "m2", "think"))
    chk("resolve_tier 空/None→default", resolve_tier("", cfg).id == "fast" and resolve_tier(None, cfg).id == "fast")
    raised = False
    try:
        resolve_tier("zzz", cfg)
    except UnknownTierError:
        raised = True
    chk("resolve_tier 未知→UnknownTierError", raised)
    chk("verdict_block busy→BUSY_NOTE", verdict_block(UltraResult(None, [], True, None)) == BUSY_NOTE)
    chk("verdict_block fallback→原句", verdict_block(UltraResult(None, [], False, "自訂 fallback")) == "自訂 fallback")
    row_cb = (1, "某宣稱", "file_grep", "錨點", "confirmed", True, "證據", None)
    out_cb = verdict_block(UltraResult("s1", [row_cb], False, None))
    chk("verdict_block confirmed·bound 標示+LLM 提出", "confirmed·bound" in out_cb and "LLM 提出" in out_cb)
    row_ref = (2, "壞宣稱", "db_query", "錨", "refuted", False, "反證", None)
    chk("verdict_block refuted 標示", "已被 oracle 反證" in verdict_block(UltraResult("s2", [row_ref], False, None)))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.advisor.effort --selftest;免 DB 免 API)")
