#!/usr/bin/env python
"""ATA 骨架 — 覆蓋終態推進編排（Auto-Terminal Advance；KH-XDOM-S1b）。

🎯 這支在做什麼(白話):讀 pending／ft_no_sent／sent_no_emb 池，**只** subprocess 既有
   fetch_oa_fulltext／build_sentences／embed_knowledge／promote_knowledge——把 item 推到
   answerable｜terminal_blocked。**自動的是終態推進，不是來源 approve／activate**。
   本支永不 import／呼叫 curation.transition 升級動作；system 觸 HUMAN_ONLY 必須紅。
守 #1/#15（blocked 不洗全文）· 憲章 v1.41.0（approve 唯人）· #28（本地零 usage）·
   #29（個別可執行＋矩陣）· KH-XDOM 計畫 §3.2／§5 S1b。

執行指令矩陣:
  python scripts/advance_knowledge_terminal.py                    # 無參數:印矩陣＋待辦計數（唯讀）
  python scripts/advance_knowledge_terminal.py --dry-run          # 列將執行指令＋池量，零副作用
  python scripts/advance_knowledge_terminal.py --dry-run --limit 50
  python scripts/advance_knowledge_terminal.py --apply --limit 3  # 有界 apply（庫內段；外部 fetch 另碼）
  python scripts/advance_knowledge_terminal.py --selftest         # 純紅綠：禁 HUMAN_ONLY／禁 import 升級
"""
from __future__ import annotations

import argparse
import ast
import subprocess
import sys
from pathlib import Path

import _bootstrap  # noqa: F401

from augur.knowledge import kh4

SCRIPTS = Path(__file__).resolve().parent
PY = sys.executable

# 僅允許編排之既有 CLI（S1b 骨架；外部 OA 放量另拍 KH-ATA-EXEC）
_ALLOWED = {
    "promote": ("promote_knowledge.py", ()),
    "fulltext": ("fetch_oa_fulltext.py", ()),
    "sentences": ("build_sentences.py", ("--scope", "items")),
    "embed": ("embed_knowledge.py", ("--layer", "sentence", "--language", "en", "--scope", "items")),
}


def _pool_counts(cur):
    """FT-COV 三桶＋隱缺（有文未句／有句未嵌）— 唯讀。"""
    cur.execute("""
        SELECT
          count(*) FILTER (
            WHERE NOT EXISTS (SELECT 1 FROM knowledge_item_text t WHERE t.item_id=i.item_id)
              AND NOT EXISTS (SELECT 1 FROM knowledge_fulltext_status f
                              WHERE f.item_id=i.item_id AND f.status <> 'unattempted')
          ) AS pending,
          count(*) FILTER (
            WHERE EXISTS (SELECT 1 FROM knowledge_item_text t WHERE t.item_id=i.item_id)
              AND NOT EXISTS (
                SELECT 1 FROM knowledge_item_text t
                JOIN knowledge_sentence s ON s.itext_id=t.itext_id WHERE t.item_id=i.item_id)
          ) AS ft_no_sent,
          count(*) FILTER (
            WHERE EXISTS (
              SELECT 1 FROM knowledge_item_text t
              JOIN knowledge_sentence s ON s.itext_id=t.itext_id WHERE t.item_id=i.item_id)
              AND NOT EXISTS (
                SELECT 1 FROM knowledge_item_text t
                JOIN knowledge_sentence s ON s.itext_id=t.itext_id
                JOIN knowledge_sentence_embedding e ON e.sent_id=s.sent_id
                WHERE t.item_id=i.item_id)
          ) AS sent_no_emb
        FROM knowledge_item i
    """)
    row = cur.fetchone()
    return {"pending": int(row[0]), "ft_no_sent": int(row[1]), "sent_no_emb": int(row[2])}


def _plan_cmds(limit: int | None):
    """依池產出將跑指令（不執行）。limit 映射各 CLI --limit（promote 無界旗標則略）。"""
    out = []
    for name, (script, base) in _ALLOWED.items():
        cmd = [PY, str(SCRIPTS / script), *base]
        if limit is not None and name != "promote":
            cmd += ["--limit", str(limit)]
        out.append((name, cmd))
    return out


def _assert_no_human_only_in_source():
    """靜態：本檔執行路徑（排除 selftest）不得呼叫 curation.transition。"""
    src = Path(__file__).read_text(encoding="utf-8")
    tree = ast.parse(src)
    skip_funcs = {"selftest", "_assert_no_human_only_in_source"}

    class _SkipSelftest(ast.NodeVisitor):
        def __init__(self):
            self.bad = []
            self._skip = 0

        def visit_FunctionDef(self, node):
            if node.name in skip_funcs:
                self._skip += 1
                self.generic_visit(node)
                self._skip -= 1
                return
            self.generic_visit(node)

        visit_AsyncFunctionDef = visit_FunctionDef

        def visit_Call(self, node):
            if self._skip == 0:
                fn = node.func
                name = getattr(fn, "attr", None) or getattr(fn, "id", None)
                if name == "transition":
                    self.bad.append(node.lineno)
            self.generic_visit(node)

    v = _SkipSelftest()
    v.visit(tree)
    if v.bad:
        raise AssertionError(f"ATA 禁呼叫 curation.transition（行 {v.bad}）")
    return True


def selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    from augur.knowledge.curation import HUMAN_ONLY, transition

    chk("HUMAN_ONLY 含 approve/activate", {"approve", "activate"} <= HUMAN_ONLY)
    raised = False
    try:
        transition("nonexistent_source_ata_probe", "approve", "ata", system=True)
    except PermissionError:
        raised = True
    except Exception:
        raised = False
    chk("system+approve → PermissionError（V-ATA1）", raised)

    chk("_ALLOWED 僅四段既有 script", set(_ALLOWED) == {"promote", "fulltext", "sentences", "embed"})
    for _, (script, _) in _ALLOWED.items():
        chk(f"script 存在 {script}", (SCRIPTS / script).is_file())
    plan = _plan_cmds(3)
    chk("dry-run 計畫含 --limit 3（非 promote）",
        any("--limit" in c and "3" in c for n, c in plan if n != "promote"))
    chk("計畫字串無 approve/activate",
        all("approve" not in " ".join(c) and "activate" not in " ".join(c) for _, c in plan))
    try:
        _assert_no_human_only_in_source()
        chk("本檔執行路徑無 transition 呼叫", True)
    except AssertionError as e:
        chk(f"本檔執行路徑無 transition 呼叫 ({e})", False)

    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="ATA 覆蓋終態推進骨架（禁來源 approve）")
    ap.add_argument("--dry-run", action="store_true", help="只列指令＋池量，不執行")
    ap.add_argument("--apply", action="store_true", help="依序 subprocess 既有 CLI（有界）")
    ap.add_argument("--limit", type=int, default=None, help="傳給 fetch/sentences/embed 的 --limit")
    ap.add_argument("--selftest", action="store_true", help="純紅綠自測（可觸 DB 僅測 PermissionError 路徑）")
    ap.add_argument("--stages", nargs="+", choices=list(_ALLOWED), default=None,
                    help="只跑指定段（預設全四段；fulltext 需 UNPAYWALL_EMAIL）")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    if not (args.dry_run or args.apply):
        print(__doc__)
        print("預設安全：無 --dry-run／--apply 只印矩陣；來源 approve／activate 永不由此支執行。")
        try:
            from augur.core import db
            with db.connect() as conn:
                cur = conn.cursor()
                pools = _pool_counts(cur)
            print(f"目前池量（唯讀）: pending={pools['pending']} ft_no_sent={pools['ft_no_sent']} "
                  f"sent_no_emb={pools['sent_no_emb']}")
        except Exception as e:
            print(f"(池量暫不可讀: {type(e).__name__}: {e})")
        return 0

    stages = args.stages or list(_ALLOWED)
    plan = [(n, c) for n, c in _plan_cmds(args.limit) if n in stages]

    try:
        from augur.core import db
        with db.connect() as conn:
            pools = _pool_counts(conn.cursor())
        print(f"池量: pending={pools['pending']} ft_no_sent={pools['ft_no_sent']} "
              f"sent_no_emb={pools['sent_no_emb']}")
    except Exception as e:
        print(f"池量暫不可讀: {type(e).__name__}: {e}")

    for name, cmd in plan:
        print(f"[{name}] {' '.join(cmd)}")
        if args.apply:
            # 外部 OA 仍受 UNPAYWALL／節奏約束；本支不解凍 FinMind／FRED
            r = subprocess.run(cmd, check=False)
            if r.returncode != 0:
                print(f"✗ {name} exit={r.returncode}", file=sys.stderr)
                return r.returncode
    if args.apply:
        from augur.core import db
        with db.connect() as conn, db.transaction(conn) as cur:
            n = kh4.refresh_items(cur, limit=args.limit)
        print(f"KH4 refresh → {n} item")
    if args.dry_run:
        print("dry-run 完畢（零執行）。")
    else:
        print("apply 完畢。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
