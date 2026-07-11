#!/usr/bin/env python
"""來源審批 CLI — 審批狀態機之人閘(深抓計畫 §4.1;admin UI 之對偶,共用 curation.py)。

🎯 這支在做什麼(白話):讓 superuser 用命令列推動來源審批狀態機(proposed→approved→activate→active…)——
   **身分閘三件(憲章 v1.41.0「approve 唯人」之機械落地)**:
   ① 升級動作(approve/activate/resume/reopen)檢 sys.stdin.isatty(),**非 TTY fail-closed 拒**
      (自動化腳本/subprocess/AI 管道天然被擋);② --actor 須對映 app_user.is_superuser=true(查表、非自報);
   ③ **approve/activate 屬決策層動作,AI 永不自行執行**(同 #14 commit/push 級授權邊界)。
   每動作寫 knowledge_source_review_log(actor/os_user/reason);approve/activate 前置=近 30 日 probe 200。

守 憲章 v1.41.0(approve 唯人/三件身分閘)· #15(superuser 查表驗證非自報)· CLAUDE #29a。
   前置=migrate_source_governance.py --run。

執行指令矩陣:
  python scripts/review_knowledge_source.py                          # 無參數:印矩陣+待審清單(唯讀)
  python scripts/review_knowledge_source.py --list --status proposed  # 列某狀態之來源
  python scripts/review_knowledge_source.py --approve KEY --actor NAME --reason "..."   # 升級(須 TTY+superuser)
  python scripts/review_knowledge_source.py --activate KEY --actor NAME
  python scripts/review_knowledge_source.py --suspend KEY --actor NAME --reason "..."   # 降級(不需 TTY)
  python scripts/review_knowledge_source.py --resume KEY --actor NAME
  python scripts/review_knowledge_source.py --reject KEY --actor NAME --reason "..."
  python scripts/review_knowledge_source.py --reopen KEY --actor NAME --reason "..."
"""
import argparse
import getpass
import os
import sys

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db
from augur.knowledge import curation

_UPGRADE = {"approve", "activate", "resume", "reopen"}   # 唯人(v1.41.0);升級須 TTY+superuser


def _is_superuser(actor):
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('app_user')")
        if not cur.fetchone()[0]:
            return False
        cur.execute("SELECT is_superuser FROM app_user WHERE username=%s", (actor,))
        r = cur.fetchone()
        return bool(r and r[0])


def _list(status):
    with db.connect() as conn, db.transaction(conn) as cur:
        if status:
            cur.execute("SELECT source_key, adapter, domain, approval_status, license_regime, wave "
                        "FROM knowledge_source WHERE approval_status=%s ORDER BY source_key LIMIT 40", (status,))
        else:
            cur.execute("SELECT approval_status, count(*) FROM knowledge_source GROUP BY 1 ORDER BY 1")
            print("審批分佈:", dict(cur.fetchall()))
            cur.execute("SELECT source_key, adapter, domain, approval_status, license_regime, wave "
                        "FROM knowledge_source WHERE approval_status='approved' ORDER BY source_key LIMIT 20")
        rows = cur.fetchall()
    print(f"{'source_key':<28}{'adapter':<16}{'domain':<20}{'status':<10}{'license':<14}wave")
    for r in rows:
        print(f"{r[0]:<28}{r[1] or '':<16}{(r[2] or ''):<20}{r[3]:<10}{(r[4] or ''):<14}{r[5] if r[5] is not None else ''}")


def _act(action, key, actor, reason):
    if not actor:
        sys.exit(f"✗ {action} 需 --actor(app_user 帳號)")
    if action in _UPGRADE:
        if not sys.stdin.isatty():
            sys.exit(f"✗ 身分閘①:{action}(升級動作)須互動 TTY 執行——非 TTY(腳本/subprocess/AI 管道)fail-closed 拒"
                     "(憲章 v1.41.0 approve 唯人)")
        if not _is_superuser(actor):
            sys.exit(f"✗ 身分閘②:actor {actor!r} 非 app_user.is_superuser=true(查表驗證、非自報)")
    try:
        r = curation.transition(key, action, actor, reason=reason, os_user=getpass.getuser())
    except (ValueError, PermissionError) as e:
        sys.exit(f"✗ {e}")
    print(f"✓ {key}: {r['old']} --{action}--> {r['new']}(actor={actor}, os={getpass.getuser()})")


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--status")
    for a in ("approve", "activate", "suspend", "resume", "reject", "reopen"):
        ap.add_argument(f"--{a}", metavar="KEY")
    ap.add_argument("--actor")
    ap.add_argument("--reason")
    args = ap.parse_args()
    for action in ("approve", "activate", "suspend", "resume", "reject", "reopen"):
        key = getattr(args, action)
        if key:
            _act(action, key, args.actor, args.reason)
            return 0
    if args.list:
        _list(args.status)
        return 0
    print(__doc__.split("執行指令矩陣:")[1])
    _list(None)
    return 0


if __name__ == "__main__":
    sys.exit(main())
