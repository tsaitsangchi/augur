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
   Runtime 接線(G-ISO-2):`config.DB_PARAMS_PREDICT` + `db.connect_predict()`；`scripts/predict_asof.py` 已走 predict role。
   本腳本只管 role/GRANT provision。
"""
import argparse
import os
import sys

import _bootstrap  # noqa: F401
from augur.core import db

PREDICT_ROLE = "augur_predict"

# 素養層(預測 role 一律 REVOKE、零存取)——前綴 + 非前綴之明列
# advisor_distill_*:蒸餾(自問自答訓練)staging,界線-A 蒸餾產物零進預測管線 → DB 層亦硬擋
# local_model_/local_ai_/raw_evolution_:LAIEVO/RAWEVO 帳本(V2 Phase 2.2/I3,2026-07-26)——
#   三軸隔離 A9:predict 對之零授權;raw_evolution_/local_ai_ 為 Phase 5 未來表、先封前綴
FORBIDDEN_PREFIXES = ("philosophy_", "knowledge_", "advisor_distill_",
                      "local_model_", "local_ai_", "raw_evolution_")
FORBIDDEN_EXPLICIT = {
    "chat_session", "chat_message",                                    # 對話原文
    "app_user", "app_session", "user_group", "group_domain_grant",    # RBAC 身分/授權
    "permission_group", "principle_factor_map", "stock_philosophy_tag", "school_thinker",  # 非前綴素養/映射
    "raw_supersede_log",   # AUD-02:old_row(被取代舊值)+superseded_at(事後修正知識)落入預測回讀=WM.35 消費閘破口→REVOKE
    # 結構補正(步 11):身份側「事後修正知識」表——同 raw_supersede_log 之理(WM.35 消費閘破口)→ REVOKE,
    # 防被預測回讀當特徵(claim 之衝突並存/lifecycle 之 retire/redirect/attribute 之 as-of 修正版本皆屬事後認識,
    # 裸讀=洩漏未來修正)。resolution 解析用途走已解析 augur_id(Phase 2 消費端 SQL)、非直讀本三表。
    "identity_claim", "identity_lifecycle_event", "entity_attribute_version",
    # 自動行動授權/留痕:執行層記錄,與預測管線無涉 → 預測 role 零存取(縱深)。
    "authorization_grant", "automation_action_log",
    # 憲章 v1.47.0 素養層表(前綴 principle_ 非 philosophy_ 而漏網;與 principle_factor_map 同理
    # ——應用注記軸非量化資格 I8,預測 role 零存取;V2 Phase 2.2 補封 2026-07-26)
    "principle_domain_map",
    # NHC-S12:CJK→EN 檢索詞表(顧問 retrieve 用;素養層、預測 role 零存取;V-ISO)
    "retrieve_glossary",
    # RKI-S01:交互探針帳本(顧問／探針用;非特徵權重;預測 role 零存取;V-ISO)
    "knowhow_interaction_probe",
}
# 注:entity_type_catalog / entity_registry / entity_alias 屬 resolution 基礎設施(Phase 2 消費端須 JOIN 已解析
#     augur_id),故不列 forbidden、留 allowed(唯讀);其 append-only/permanence 由 migrate_identity_ddl 硬化。
# ⚠ 過渡期護欄(issue 13/17,誠實揭露):此三表帶 as-of/事後狀態欄(entity_alias.valid_from/valid_to/
#     transaction_time/alias_status〔provisional→adopted→retired〕、entity_registry.status〔active/tombstoned〕/
#     minted_at)。**Layer 4/5 as-of resolver 視圖上線前,預測消費者不得 as-of-blind 直讀現況欄**——裸讀 alias
#     現況(未來重新映射)或 registry status(未來下市)=洩漏未來、違 anti-leakage #8。合規入口=Phase 2 之 as-of
#     resolution 視圖(遮蔽 transaction_time/status 現況、僅暴露 as-of 解析結果);屆時把此三基礎表改回 forbidden、
#     只 GRANT 該視圖(承接 L4/L5)。本步僅留此文件護欄(as-of resolver DEFER L4/L5、過渡期無機械閘)。
# P2H：predict 只讀 prodset 登錄表；其餘 evolution 帳本／promotion_queue 一律拒（禁圖省事整包 evolution）
PRODSET_ALLOW = {"evolution_production_feature_set"}
EVOLUTION_REVOKE_EXPLICIT = {
    "evolution_run", "evolution_coverage_snapshot", "evolution_apply_log",
    "evolution_kill_switch", "promotion_queue",
}
# 預測 role 需寫入(非只讀)之輸出表(2026-07-08 補 harness 記錄表:revalidate/deflation/判停之落地)
WRITABLE = {"model_registry", "prediction_values", "feature_values",
            "pipeline_execution_log", "data_audit_log",
            "revalidation_ledger", "trial_ledger", "revalidation_baseline",
            "revalidation_verdict", "judgestop_threshold",
            "prediction_serving_log"}  # AUD-08:predict 出單伴生 append(Phase 4 改繫);同 prediction_values 為輸出表


# 預測管線 allowed 註冊表(V2 Phase 2.2:fail-loud on unknown——原本的尾 else=fail-open,任何新表
# 靜默 GRANT=無聲放寬;現改「未登錄→第三桶,--apply 拒跑並列名」。新表要授權=來此補登,不改回 fail-open。
# 2026-07-26 以 live DB 157 表 catch-all 實查編錄;raw 層=FinMind 大寫命名以首字母大寫判)
ALLOWED_PREFIXES = (
    "core_universe", "feature_",                                     # 宇宙/特徵
    "daily_direction_", "direction_", "market_", "probability_",     # 方向/機率軸
    "prediction_", "mc_", "risk_", "judgestop",                      # 預測輸出/模擬/風控/判停
    "field_", "fred_", "econ_",                                      # 欄際結構/總經/經濟判準
    "revalidation_", "trial_", "validation_", "score_",              # 驗證帳本
    "dataset_", "column_", "attestation_", "data_audit",             # catalog/對帳
    "freeze_", "full_attest", "restatement_",                        # 凍結/重述
    "deliberation_",                                                 # 審議引擎(既有授權現況、存疑待審)
    "model_registry", "pipeline_execution", "qdrant_",               # 模型登錄/執行紀錄/向量同步
    "governance_", "user_settings", "vectorstore_",                  # 治理佇列(唯讀)/設定(既有現況)
    "arena_admission",                                               # arena 前置 gate
)


def classify(cur):
    """回 (forbidden[], allowed[], unregistered[]):素養層/evolution 拒、註冊表准、**其餘=未登錄第三桶**。"""
    cur.execute("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename")
    forbidden, allowed, unregistered = [], [], []
    for (t,) in cur.fetchall():
        if t.startswith(FORBIDDEN_PREFIXES) or t in FORBIDDEN_EXPLICIT:
            forbidden.append(t)
        elif t in PRODSET_ALLOW:
            allowed.append(t)                          # P2H：熱路徑唯讀 prodset
        elif t in EVOLUTION_REVOKE_EXPLICIT or (
            t.startswith("evolution_") and t not in PRODSET_ALLOW
        ):
            forbidden.append(t)                        # 其餘 evolution 帳本拒(含未來 hint/evidence/deferred)
        elif t[0].isupper() or t.startswith(ALLOWED_PREFIXES):
            allowed.append(t)                          # raw 層(FinMind 大寫)+註冊前綴
        else:
            unregistered.append(t)                     # fail-loud:未登錄不授權、--apply 拒跑
    return forbidden, allowed, unregistered


def role_exists(cur, role):
    cur.execute("SELECT 1 FROM pg_roles WHERE rolname=%s", (role,))
    return cur.fetchone() is not None


def dry_run(cur):
    forbidden, allowed, unregistered = classify(cur)
    if unregistered:
        print(f"  ⚠ 未登錄 {len(unregistered)} 表(不授權;--apply 會拒跑):{', '.join(unregistered)}")
    print(f"  素養層 forbidden(REVOKE 全部)= {len(forbidden)} 表")
    print("    " + ", ".join(forbidden[:12]) + (" …" if len(forbidden) > 12 else ""))
    print(f"  預測 allowed(GRANT)= {len(allowed)} 表;其中可寫 {sorted(WRITABLE & set(allowed))}")
    print("    " + ", ".join(allowed[:12]) + (" …" if len(allowed) > 12 else ""))
    # P2H 明示：prodset 准、其他 evolution 拒
    for t, expect in (
        ("evolution_production_feature_set", "allowed"),
        ("evolution_run", "forbidden"),
        ("promotion_queue", "forbidden"),
    ):
        bucket = "allowed" if t in allowed else ("forbidden" if t in forbidden else "missing")
        mark = "✓" if bucket == expect else f"✗ 不符(期望{expect})!"
        print(f"  P2H classify {t}: {bucket} {mark}")
    if role_exists(cur, PREDICT_ROLE):
        print(f"  role {PREDICT_ROLE} 已存在——抽驗存取:")
        samples = [
            ("evolution_production_feature_set", "准"),
            ("evolution_run", "拒"),
            ("promotion_queue", "拒"),
        ]
        ft = next((t for t in forbidden if t.startswith("philosophy_") or t.startswith("knowledge_")), None)
        if ft:
            samples.append((ft, "拒"))
        at = next((a for a in allowed if a not in WRITABLE and a not in PRODSET_ALLOW), None)
        if at:
            samples.append((at, "准"))
        for t, expect in samples:
            cur.execute("SELECT to_regclass(%s)", (f"public.{t}",))
            if not cur.fetchone()[0]:
                print(f"    {t}: 表不存在(跳過)")
                continue
            cur.execute("SELECT has_table_privilege(%s, %s, 'SELECT')", (PREDICT_ROLE, f'"{t}"'))
            got = "准" if cur.fetchone()[0] else "拒"
            mark = "✓" if got == expect else "✗ 不符!"
            print(f"    {t}: SELECT={got}(應{expect}){mark}")
    else:
        print(f"  role {PREDICT_ROLE} 尚未建(--apply --confirm 建;本腳本 ready、暫緩實建)")


def apply(cur):
    forbidden, allowed, unregistered = classify(cur)
    if unregistered:
        # V2 Phase 2.2:fail-loud——未登錄表出現即拒跑整批;正解=補登 ALLOWED_PREFIXES/FORBIDDEN,
        # 不得改回 fail-open(換機流程因此卡住時亦同:補登該表,見 v2 §6 Phase 2 中止條件)
        sys.exit(f"✗ --apply 拒跑:{len(unregistered)} 張未登錄表(不知該准該拒=不動手):"
                 f"{', '.join(unregistered)}\n  → 補登 ALLOWED_PREFIXES 或 FORBIDDEN_* 後重跑")
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
            print("  完成。Runtime 接線:config.DB_PARAMS_PREDICT + db.connect_predict()（predict_asof 已用）；換機還原後重跑本腳本。")
        else:
            with db.transaction(conn) as cur:
                if not args.dry_run:
                    print(__doc__.split("執行指令矩陣:")[1].split("⚠")[0])
                print("── 預測 role 存取分類盤點(唯讀)──")
                dry_run(cur)


if __name__ == "__main__":
    main()
