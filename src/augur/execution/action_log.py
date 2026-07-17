"""自動行動六元組 log 寫入 helper — P5.E1 Action 留痕(AUD-10/11)。

🎯 這支在做什麼(白話):把「會改變 Reality 的自動行動」(watchdog/selfheal 的 kill/relaunch、heal 放量重抓…)
   以 P5.E1 **六元組**留痕到 `automation_action_log`,取代家目錄純文字 log——
   六元組:Actor Identity(已解析 agent 身份)、Authorization(FK→authorization_grant)、Knowledge Basis、
   Timestamp(起訖)、Expected Effect、Observed Effect(連結 attestation_result)。
   **本輪僅提供 API**(單一寫入源);watchdog/selfheal/daily_maintenance 之實際改繫列 follow-up Phase 5。

DDL 單一權威=scripts/migrate_automation_action_ddl.py(authorization_grant + automation_action_log)。
守 P5.E1(Action 六元組)· P4.E3/E6(留痕/provenance 延伸至行動記錄)· #12(單一寫入源)· #18。

自測(本檔=library #18;免 DB 免 API 可個別驗證):
  python -m augur.execution.action_log              # 印用途+公開入口(唯讀)
  python -m augur.execution.action_log --selftest   # 純紅綠自測(零 IO)
"""
from __future__ import annotations

import json


def log_action(cur, actor_identity, authorization_ref, knowledge_basis, action_type,
               target=None, expected_effect=None) -> int:
    """寫一列行動起始(六元組之五:Actor/Authorization/Knowledge/Expected/started_at);回 action_id。

    actor_identity / action_type 為硬義務;authorization_ref=FK→authorization_grant(可 None,
    但 P5.E1 精神下自動行動應具已解析授權——None 僅用於過渡期遷移未拍板之舊行動,須另補)。
    knowledge_basis / expected_effect 存為 jsonb。
    """
    if not actor_identity:
        raise ValueError("log_action 須具 actor_identity(P5.E1 Actor Identity)")
    if not action_type:
        raise ValueError("log_action 須具 action_type")
    cur.execute(
        "INSERT INTO automation_action_log (actor_identity, authorization_ref, knowledge_basis, "
        "action_type, target, expected_effect, status) "
        "VALUES (%s, %s, %s, %s, %s, %s, 'started') RETURNING action_id",
        (actor_identity, authorization_ref, json.dumps(knowledge_basis or {}),
         action_type, target, json.dumps(expected_effect or {})))
    return cur.fetchone()[0]


def link_observed_effect(cur, action_id, attestation_result_id, status="completed", ended_at=None):
    """補上 Observed Effect(連結 attestation_result)+ 收尾狀態/ended_at(六元組之六)。

    非 DELETE/非重寫既有欄——僅填 observed_effect_ref/status/ended_at(automation_action_log 之
    permanence:no-DELETE/no-TRUNCATE,允 UPDATE 收尾)。
    """
    cur.execute(
        "UPDATE automation_action_log SET observed_effect_ref=%s, status=%s, "
        "ended_at=COALESCE(%s, now()) WHERE action_id=%s",
        (attestation_result_id, status, ended_at, action_id))


def _selftest():
    """自測(零 DB/零 API;log/link 皆 IO-bound → import-smoke + 參數守衛結構斷言,零 IO)。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    def raises(fn, *args):
        try:
            fn(*args)
            return False
        except ValueError:
            return True
        except Exception:
            return False

    chk("log_action 缺 actor_identity → ValueError",
        raises(log_action, None, "", None, {}, "kill"))
    chk("log_action 缺 action_type → ValueError",
        raises(log_action, None, "watchdog", None, {}, ""))
    chk("公開入口皆存在", all(callable(f) for f in (log_action, link_observed_effect)))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.execution.action_log --selftest;免 DB 免 API)")
