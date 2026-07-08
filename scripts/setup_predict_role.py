#!/usr/bin/env python
"""建立受限預測 DB role — A' 隔離雙閘之「DB 層硬保證」(擋 AST 稽核擋不到的動態 SQL 旁路)。

🎯 這支在做什麼(白話):建一個**受限 role `augur_predict`**,對**素養層 62 表**(philosophy_*/knowledge_*/
   chat_*/RBAC)一律 REVOKE、只 GRANT 預測管線表(raw/feature/universe/model/validate/catalog/audit)。
   預測進程改連此 role → 即使有動態 SQL 想撈素養層,DB 層直接拒(擋 anti-leakage #8 之旁路)。
   與 `augur.audit.import_isolation`(靜態 import/字面稽核)成**雙閘**:AST 擋靜態、GRANT 擋動態。
   **冪等**:CREATE ROLE IF NOT EXISTS、REVOKE/GRANT 天然冪等、可重跑(換機 pg_restore 後重跑=一行還原,
   因 role 是 cluster 層不在 pg_dump;寫進 HANDOFF setup 序)。
守 #8(anti-leakage:素養不進預測管線 DB 層硬擋)· #1(隔離)· #6(冪等可重跑、破壞性須 --apply 明示)· #29。

執行指令矩陣:
  python scripts/setup_predict_role.py                    # 無參數=印矩陣 + 分類盤點(唯讀、安全)
  python scripts/setup_predict_role.py --dry-run          # 唯讀:印 forbidden/allowed 分類 + (role 存在則)驗證存取
  python scripts/setup_predict_role.py --apply            # 破壞性:建 role + REVOKE 素養層 + GRANT 預測表(需 --confirm)
  python scripts/setup_predict_role.py --apply --confirm  # 真的執行(role 密碼取 env DB_PREDICT_PASSWORD)

⚠ **破壞性 + 跨機**:建 role 屬 doctrine 級運維(#6),須 --confirm;role 不在 pg_dump,換機還原後重跑本腳本。
   預測 code 連此 role 之接線(config DB_PARAMS_PREDICT)為另一步、本腳本只管 role/GRANT。
"""
import argparse
import os
import sys

import _bootstrap  # noqa: F401
from augur.core import db

PREDICT_ROLE = "augur_predict"

# 素養層(預測 role 一律 REVOKE、零存取)——前綴 + 非前綴之明列
# advisor_distill_*:蒸餾(自問自答訓練)staging,界線-A 蒸餾產物零進預測管線 → DB 層亦硬擋
FORBIDDEN_PREFIXES = ("philosophy_", "knowledge_", "advisor_distill_")
FORBIDDEN_EXPLICIT = {
    "chat_session", "chat_message",                                    # 對話原文
    "app_user", "app_session", "user_group", "group_domain_grant",    # RBAC 身分/授權
    "permission_group", "principle_factor_map", "stock_philosophy_tag", "school_thinker",  # 非前綴素養/映射
}
# 預測 role 需寫入(非只讀)之輸出表(2026-07-08 補 harness 記錄表:revalidate/deflation/判停之落地)
WRITABLE = {"model_registry", "prediction_values", "feature_values",
            "pipeline_execution_log", "data_audit_log",
            "revalidation_ledger", "trial_ledger", "revalidation_baseline",
            "revalidation_verdict", "judgestop_threshold"}


def classify(cur):
    """回 (forbidden[], allowed[]):public 全表依素養層判準分流。"""
    cur.execute("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename")
    forbidden, allowed = [], []
    for (t,) in cur.fetchall():
        if t.startswith(FORBIDDEN_PREFIXES) or t in FORBIDDEN_EXPLICIT:
            forbidden.append(t)
        elif t.startswith("core_universe") or t.startswith("feature_"):
            allowed.append(t)
        else:
            allowed.append(t)
    return forbidden, allowed


def role_exists(cur, role):
    cur.execute("SELECT 1 FROM pg_roles WHERE rolname=%s", (role,))
    return cur.fetchone() is not None


def dry_run(cur):
    forbidden, allowed = classify(cur)
    print(f"  素養層 forbidden(REVOKE 全部)= {len(forbidden)} 表")
    print("    " + ", ".join(forbidden[:12]) + (" …" if len(forbidden) > 12 else ""))
    print(f"  預測 allowed(GRANT)= {len(allowed)} 表;其中可寫 {sorted(WRITABLE & set(allowed))}")
    print("    " + ", ".join(allowed[:12]) + (" …" if len(allowed) > 12 else ""))
    if role_exists(cur, PREDICT_ROLE):
        print(f"  role {PREDICT_ROLE} 已存在——抽驗存取:")
        ft = forbidden[0] if forbidden else None
        at = next((a for a in allowed if a not in WRITABLE), None)
        for t, expect in ((ft, "拒"), (at, "准")):
            if not t:
                continue
            cur.execute("SELECT has_table_privilege(%s, %s, 'SELECT')", (PREDICT_ROLE, f'"{t}"'))  # 引號保留大小寫(混大小寫表名如 CnnFearGreedIndex 否則被 lower 化查無)
            got = "准" if cur.fetchone()[0] else "拒"
            mark = "✓" if got == expect else "✗ 不符!"
            print(f"    {t}: SELECT={got}(應{expect}){mark}")
    else:
        print(f"  role {PREDICT_ROLE} 尚未建(--apply --confirm 建;本腳本 ready、暫緩實建)")


def apply(cur):
    forbidden, allowed = classify(cur)
    # 1. 建 role(冪等);已存在則僅 refresh grants(不改密碼——ALTER ROLE 需 superuser/owner,augur 非超級使用者)
    if not role_exists(cur, PREDICT_ROLE):
        pw = os.environ.get("DB_PREDICT_PASSWORD")
        if not pw:
            sys.exit("✗ role 尚未建且未設 DB_PREDICT_PASSWORD env;設後再 --apply(建 role 需 CREATEROLE 權)")
        cur.execute(f"CREATE ROLE {PREDICT_ROLE} LOGIN PASSWORD %s", (pw,))
        print(f"  建 role {PREDICT_ROLE}")
    else:
        print(f"  role {PREDICT_ROLE} 已存在——僅 refresh grants(不改密碼;ALTER ROLE 需 superuser)")
    # 2. 基礎:USAGE on public
    cur.execute(f"GRANT USAGE ON SCHEMA public TO {PREDICT_ROLE}")
    # 3. 素養層 REVOKE ALL
    for t in forbidden:
        cur.execute(f'REVOKE ALL ON public."{t}" FROM {PREDICT_ROLE}')
    # 4. 預測表 GRANT(唯讀 + 可寫者加 INSERT/UPDATE)
    for t in allowed:
        cur.execute(f'GRANT SELECT ON public."{t}" TO {PREDICT_ROLE}')
        if t in WRITABLE:
            cur.execute(f'GRANT INSERT, UPDATE ON public."{t}" TO {PREDICT_ROLE}')
    # 5. default privileges:未來素養表自動對 predict 關(僅 owner=augur 建的)
    cur.execute(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON TABLES FROM {PREDICT_ROLE}")
    # 6. ttai_import(自有 ERP staging)亦不給 predict
    cur.execute("SELECT 1 FROM information_schema.schemata WHERE schema_name='ttai_import'")
    if cur.fetchone():
        cur.execute(f"REVOKE ALL ON ALL TABLES IN SCHEMA ttai_import FROM {PREDICT_ROLE}")
    print(f"  ✓ REVOKE {len(forbidden)} 素養表、GRANT {len(allowed)} 預測表")


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    args, _ = ap.parse_known_args()
    with db.connect() as conn:
        if args.apply:
            if not args.confirm:
                sys.exit("✗ --apply 為破壞性(建 role/改 GRANT),須加 --confirm(#6)")
            with db.transaction(conn) as cur:
                apply(cur)
            print("  完成。下一步:預測入口改連 augur_predict(config DB_PARAMS_PREDICT);換機還原後重跑本腳本。")
        else:
            with db.transaction(conn) as cur:
                if not args.dry_run:
                    print(__doc__.split("執行指令矩陣:")[1].split("⚠")[0])
                print("── 預測 role 存取分類盤點(唯讀)──")
                dry_run(cur)


if __name__ == "__main__":
    main()
