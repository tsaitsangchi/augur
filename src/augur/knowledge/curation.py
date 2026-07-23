"""來源治理 curation — 審批狀態機/身分閘/DOI 正規化之單一住所(深抓計畫 §4;憲章 v1.41.0 不變式)。

🎯 這支在做什麼(白話):把「哪個來源可以抓」從 psql 手工 UPDATE 升級為**有留痕、有前置檢查的狀態機**——
   `proposed→approved→activate→active`,approve/activate/resume/reopen **唯 superuser 人執行**
   (AI 永不自行呼叫升級動作,同 #14 授權邊界);system:harvest 僅得降級(suspend/cooldown)。
   每一步寫 knowledge_source_review_log(actor/os_user/reason/probe 證據)。
   norm_doi=DOI 正規化 SSOT(自 fetch_oa_fulltext 上移;promote 入庫前一律過此,M4 病灶:
   URL 形 vs 裸形跨形態重複 152 對)。

守 憲章 v1.41.0(審批唯人/三層閘)· #12(norm_doi/狀態機單一住所)· #15(前置=近 30 日 probe 200 證據)。

執行指令矩陣(本檔=library #18；免 DB 免 API 可個別驗證):
  python -m augur.knowledge.curation              # 印用途+公開入口(唯讀)
  python -m augur.knowledge.curation --selftest   # 純紅綠自測(零 IO)
"""
import getpass
import json
import os
import re
import sys

from augur.core import db

# 狀態機轉移表:action → (合法舊態集, 新態);升級動作=唯人(superuser);降級=system:harvest 亦可
TRANSITIONS = {
    "approve":  ({"proposed"}, "approved"),
    "activate": ({"approved", "suspended"}, "active"),
    "suspend":  ({"active"}, "suspended"),
    "resume":   ({"suspended"}, "active"),
    "exhaust":  ({"active"}, "exhausted"),
    "reject":   ({"proposed"}, "rejected"),
    "reopen":   ({"exhausted", "rejected"}, None),   # exhausted→active / rejected→proposed(需 reason)
}
HUMAN_ONLY = {"approve", "activate", "resume", "reopen"}       # 升級=唯人(v1.41.0)
_DOI_PREFIX = re.compile(r"^(?:https?://(?:dx\.)?doi\.org/|doi:)\s*", re.I)


def norm_doi(raw):
    """DOI 正規化 SSOT(M4):剝 URL/doi: 前綴+lowercase+去空白;非 DOI 形回原字串 strip。"""
    s = (raw or "").strip()
    s = _DOI_PREFIX.sub("", s)
    return s.lower().strip() if s.lower().startswith("10.") else s


def cli_identity():
    """CLI 身分閘(§4.1):須 TTY(防被腳本/AI 管道呼叫)+ os user;回 (actor, os_user)。
    升級動作另須 superuser 對映(app_user.is_superuser 以 os user/明示 --as 帳號查)。"""
    if not sys.stdin.isatty():
        raise PermissionError("身分閘:升級動作須互動 TTY 執行(AI/管道呼叫被拒,v1.41.0)")
    u = getpass.getuser()
    return u, u


def _recent_probe_ok(cur, source_key, days=30):
    cur.execute("SELECT 1 FROM knowledge_source_review_log WHERE source_key=%s AND action='probe' "
                "AND (probe_result->>'http_status')='200' AND created_at > now() - interval '%s days' "
                "LIMIT 1", (source_key, days))
    return cur.fetchone() is not None


def transition(source_key, action, actor, *, reason=None, os_user=None, probe_result=None,
               system=False):
    """執行一次狀態機轉移(寫 review_log;失敗 raise)。system=True 限降級動作(harvest 自動 suspend)。"""
    if action not in TRANSITIONS and action not in ("probe", "propose", "edit", "ratify"):
        raise ValueError(f"未知 action {action!r}")
    if system and action in HUMAN_ONLY:
        raise PermissionError(f"v1.41.0:{action} 唯人執行,system 禁升級")
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT approval_status FROM knowledge_source WHERE source_key=%s FOR UPDATE",
                    (source_key,))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"來源 {source_key!r} 不存在")
        old = row[0]
        new = old
        if action in TRANSITIONS:
            legal, target = TRANSITIONS[action]
            if old not in legal:
                raise ValueError(f"{action}: {source_key} 現態 {old!r} 不在合法集 {legal}")
            if action == "reopen":
                if not reason:
                    raise ValueError("reopen 需 reason")
                target = "active" if old == "exhausted" else "proposed"
            if action in ("approve", "activate"):
                # 本機/SFTP 通道(件 A1)無 http probe 概念→豁免 http-200 前置(#18:curation 保純 DB 模組、
                # 不在此建檔案/ssh probe);可用性由 acquirer --dry-run/活化前人工核。API 源前置不變。
                cur.execute("SELECT protocol FROM knowledge_source WHERE source_key=%s", (source_key,))
                proto = (cur.fetchone() or [None])[0]
                if proto not in ("local_file", "sftp") and not _recent_probe_ok(cur, source_key):
                    raise ValueError(f"{action} 前置未滿足:近 30 日無 http_status=200 之 probe 記錄(§3.2)")
            new = target
            if action in ("approve", "activate"):
                cur.execute("UPDATE knowledge_source SET approval_status=%s, approved_by=%s, "
                            "approved_at=now() WHERE source_key=%s", (new, actor, source_key))
            else:
                cur.execute("UPDATE knowledge_source SET approval_status=%s WHERE source_key=%s",
                            (new, source_key))
        cur.execute("INSERT INTO knowledge_source_review_log "
                    "(source_key, action, old_status, new_status, actor, os_user, reason, probe_result) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                    (source_key, action, old, new, actor, os_user or actor, reason,
                     json.dumps(probe_result) if probe_result else None))
        conn.commit()
    return {"source_key": source_key, "action": action, "old": old, "new": new}


def _selftest():
    """純紅綠自測(零 IO):norm_doi 正規化不變式 + 狀態機常數結構斷言。"""
    ok = True

    def chk(name, cond):
        nonlocal ok; ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    # norm_doi:URL/doi: 前綴剝除 + lowercase(DOI 形)
    chk("URL 形剝前綴+小寫", norm_doi("https://doi.org/10.1234/ABC") == "10.1234/abc")
    chk("doi: 前綴+dx 子網", norm_doi("doi:10.1000/XyZ") == "10.1000/xyz"
        and norm_doi("https://dx.doi.org/10.5/A") == "10.5/a")
    # M4 病灶:URL 形 vs 裸形須正規化為同鍵(跨形態去重)
    chk("跨形態去重(M4)", norm_doi("https://doi.org/10.1234/ABC") == norm_doi("10.1234/abc"))
    # 非 DOI 形不 lowercase、僅 strip;None→""
    chk("非 DOI 保原不小寫", norm_doi("  Some Title  ") == "Some Title" and norm_doi(None) == "")
    # 狀態機:升級動作全在 TRANSITIONS 且 reopen 為雙態特例(target=None)
    chk("HUMAN_ONLY ⊆ TRANSITIONS", HUMAN_ONLY <= set(TRANSITIONS))
    chk("reopen 雙態特例", TRANSITIONS["reopen"][1] is None and TRANSITIONS["reopen"][0] == {"exhausted", "rejected"})
    # 降級動作(suspend)非唯人;升級動作(approve/activate)須唯人
    chk("降級非唯人/升級唯人", "suspend" not in HUMAN_ONLY and {"approve", "activate"} <= HUMAN_ONLY)

    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.knowledge.curation --selftest;免 DB 免 API)")
