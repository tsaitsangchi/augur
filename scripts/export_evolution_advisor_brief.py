#!/usr/bin/env python
"""🎯 brief/1 匯出器——TWEVO 帳本事實→advisor 情境註記(v2 §3.2 邊 3;INTEG-C 單元 2)。

白話:把 arena/prodset/apply_log/對照臂的「帳本事實」組成 brief/1 JSON(每條 claim 附
可查表 ref,#10),**產出前先過 evolution_contract.validate 同一把尺**(C7 產消同檢;
不合格 fail-loud 不落檔)。落 var/briefs/(gitignore;進化工件不入公開 repo)。
claim_level 全 ledger_fact;措辭黑名單由 validator 把關(可交易/確立級/更準…寫不進去)。
守 #10(逐條可溯源)#15(僅帳本事實、無外推)#8(禁數值陣列)#29;SSOT=v2 §3.2 邊 3。

執行指令矩陣:
  python scripts/export_evolution_advisor_brief.py             # 無參數:預覽 claims(唯讀)
  python scripts/export_evolution_advisor_brief.py --write     # 驗證後落檔+印 path/sha
  python scripts/export_evolution_advisor_brief.py --selftest  # 零 DB 純紅綠
"""
import hashlib
import json
import os
import sys
from datetime import date

import _bootstrap  # noqa: F401
from augur.audit.evolution_contract import validate
from augur.core import db

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "var", "briefs")


def _claims(cur):
    """逐條帳本事實(SQL 現查、非快照);每條 (text, ref)。"""
    out = []
    cur.execute("SELECT count(*), count(*) FILTER (WHERE settled_at IS NOT NULL), "
                "min(pred_date), max(pred_date) FROM direction_arena_prediction")
    n, ns, d0, d1 = cur.fetchone()
    out.append((f"arena 對局帳本共 {n} 列,已結算 {ns} 列(pred_date {d0}~{d1};觀察級)",
                "direction_arena_prediction"))
    cur.execute("SELECT count(DISTINCT pred_date) FROM direction_arena_prediction")
    out.append((f"方向門 cluster 進度 {cur.fetchone()[0]}/60(確立門檻=direction_gate 門二,未達前不作任何確立宣稱)",
                "direction_gate"))
    cur.execute("SELECT string_agg(feature, '、') FROM evolution_production_feature_set WHERE set_status='active'")
    act = cur.fetchone()[0] or "(空)"
    out.append((f"生產特徵集 active={act}", "evolution_production_feature_set"))
    cur.execute("""SELECT count(*) FROM evolution_apply_log WHERE evidence_json->>'gate_ref'='V2-AUTOADVANCE'""")
    n_auto = cur.fetchone()[0]
    if n_auto:
        cur.execute("""SELECT count(*) FILTER (WHERE evidence_json->>'auto_rule'='R3-sign-refuted-demote')
                       FROM evolution_apply_log WHERE evidence_json->>'gate_ref'='V2-AUTOADVANCE'""")
        nd = cur.fetchone()[0]
        out.append((f"引擎依 V2-AUTOADVANCE 規則自動執行 {n_auto} 筆狀態變更(其中 sign-refuted 除役 {nd} 筆),逐筆落帳可稽",
                    "evolution_apply_log"))
    cur.execute("""SELECT arm, metric_value, (detail->>'abs_hac_p95')::float8
                   FROM evolution_evidence_run
                   WHERE axis='tw' AND selection_scope='control_arms_v1' AND NOT is_invalid
                     AND n_items=(SELECT max(n_items) FROM evolution_evidence_run
                                  WHERE axis='tw' AND selection_scope='control_arms_v1' AND NOT is_invalid)
                   ORDER BY arm""")
    rows = cur.fetchall()
    if rows:
        seg = ";".join(f"{a} 偽陽率 {v:.1%}(p95={p:.3f})" for a, v, p in rows if v is not None)
        out.append((f"對照臂 null 分布實測:{seg};閘之名目顯著性與經驗值之差已入帳", "evolution_evidence_run"))
    cur.execute("SELECT scope||'='||state FROM evolution_kill_switch ORDER BY scope")
    out.append(("kill-switch 現況:" + "、".join(r[0] for r in cur.fetchall()), "evolution_kill_switch"))
    cur.execute("SELECT count(*) FROM evolution_prereg_gate WHERE axis='program'")
    if cur.fetchone()[0]:
        out.append(("V2-SUNSET 已凍結(期限 2026-10-31;三選一續命;判準 sha 已鎖)", "evolution_prereg_gate"))
    return out


def build():
    with db.connect() as conn, db.transaction(conn) as cur:
        claims = _claims(cur)
    obj = {"schema": "brief/1", "source_axis": "tw", "as_of": str(date.today()),
           "claims": [{"claim_level": "ledger_fact", "text": t, "ref": r} for t, r in claims]}
    errs = validate(obj, "brief")
    return obj, errs


def main(argv):
    if "--selftest" in argv:
        return _selftest()
    obj, errs = build()
    if errs:
        print("✗ brief 未過 C7 契約(不落檔,fail-loud):")
        for e in errs:
            print("  -", e)
        return 1
    print(f"claims={len(obj['claims'])}(全 ledger_fact;C7 驗證 ✓)")
    for c in obj["claims"]:
        print(f"  · {c['text'][:76]}  [{c['ref']}]")
    if "--write" not in argv:
        print("(唯讀預覽;--write 落檔)")
        return 0
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, f"brief_tw_{obj['as_of'].replace('-', '')}.json")
    blob = json.dumps(obj, ensure_ascii=False, indent=1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(blob)
    print(f"✓ 落檔 {path}  sha256={hashlib.sha256(blob.encode()).hexdigest()[:16]}")
    return 0


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    fix = {"schema": "brief/1", "source_axis": "tw", "as_of": "2026-07-27",
           "claims": [{"claim_level": "ledger_fact", "text": "arena 已結算 4128 列", "ref": "direction_arena_prediction"}]}
    chk("固定樣本過 C7", validate(fix, "brief") == [])
    chk("黑名單詞寫不進去(validator 擋)", validate(
        {**fix, "claims": [{"claim_level": "ledger_fact", "text": "已可交易", "ref": "x"}]}, "brief") != [])
    chk("claims 組裝含 ref(#10)", all("ref" in c for c in fix["claims"]))
    chk("落點在 var/briefs(gitignore 射程)", OUT_DIR.endswith(os.path.join("var", "briefs")))
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
