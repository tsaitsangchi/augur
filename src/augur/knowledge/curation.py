"""來源治理 curation — 審批狀態機／DOI 正規化之單一住所(深抓計畫 §4;憲章 v1.48.0 一律准入)。

🎯 這支在做什麼(白話):把「哪個來源可以抓」做成**有留痕的狀態機**——
   `proposed→approved→activate→active`。**v1.48.0 起升級不再唯人**：機械路徑
   (`system=True`，如 `system:kh10_auto_admit`) 得 approve／activate／resume／reopen，
   與人 TTY 路徑並存；一律准入＋原文先入庫、再逐層 KH update 精準（憲章不變式）。
   每一步寫 knowledge_source_review_log。norm_doi=DOI 正規化 SSOT。

守 憲章 v1.48.0(一律准入／漸進 KH)· #12(norm_doi/狀態機單一住所)· #15(前置=近 30 日 probe 200 證據；本機/SFTP 豁免)。

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

# 狀態機轉移表:action → (合法舊態集, 新態)
TRANSITIONS = {
    "approve":  ({"proposed"}, "approved"),
    "activate": ({"approved", "suspended"}, "active"),
    "suspend":  ({"active"}, "suspended"),
    "resume":   ({"suspended"}, "active"),
    "exhaust":  ({"active"}, "exhausted"),
    "reject":   ({"proposed"}, "rejected"),
    "reopen":   ({"exhausted", "rejected"}, None),   # exhausted→active / rejected→proposed(需 reason)
}
# v1.48.0：空集＝無「唯人升級」限制（廢止 v1.41.0 HUMAN_ONLY）
HUMAN_ONLY = set()
_DOI_PREFIX = re.compile(r"^(?:https?://(?:dx\.)?doi\.org/|doi:)\s*", re.I)


def norm_doi(raw):
    """DOI 正規化 SSOT(M4):剝 URL/doi: 前綴+lowercase+去空白;非 DOI 形回原字串 strip。"""
    s = (raw or "").strip()
    s = _DOI_PREFIX.sub("", s)
    return s.lower().strip() if s.lower().startswith("10.") else s


def cli_identity():
    """CLI 身分閘:人路徑建議 TTY+os user;回 (actor, os_user)。
    v1.48.0 起升級亦可走 system=True 機械路徑，不強制本函式。"""
    if not sys.stdin.isatty():
        raise PermissionError("身分閘:人路徑升級建議互動 TTY(管道請改 system=True 機械路徑,v1.48.0)")
    u = getpass.getuser()
    return u, u


def _recent_probe_ok(cur, source_key, days=30):
    cur.execute("SELECT 1 FROM knowledge_source_review_log WHERE source_key=%s AND action='probe' "
                "AND (probe_result->>'http_status')='200' AND created_at > now() - interval '%s days' "
                "LIMIT 1", (source_key, days))
    return cur.fetchone() is not None


def transition(source_key, action, actor, *, reason=None, os_user=None, probe_result=None,
               system=False):
    """執行一次狀態機轉移(寫 review_log;失敗 raise)。
    system=True：機械升級／降級皆可(v1.48.0 一律准入)。"""
    if action not in TRANSITIONS and action not in ("probe", "propose", "edit", "ratify"):
        raise ValueError(f"未知 action {action!r}")
    # v1.48.0：不再因 system∧升級 拒斥（HUMAN_ONLY 空集）
    if system and action in HUMAN_ONLY:
        raise PermissionError(f"v1.48.0:{action} 仍標 HUMAN_ONLY,system 禁")
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

    chk("URL 形剝前綴+小寫", norm_doi("https://doi.org/10.1234/ABC") == "10.1234/abc")
    chk("doi: 前綴+dx 子網", norm_doi("doi:10.1000/XyZ") == "10.1000/xyz"
        and norm_doi("https://dx.doi.org/10.5/A") == "10.5/a")
    chk("跨形態去重(M4)", norm_doi("https://doi.org/10.1234/ABC") == norm_doi("10.1234/abc"))
    chk("非 DOI 保原不小寫", norm_doi("  Some Title  ") == "Some Title" and norm_doi(None) == "")
    chk("HUMAN_ONLY ⊆ TRANSITIONS", HUMAN_ONLY <= set(TRANSITIONS))
    chk("reopen 雙態特例", TRANSITIONS["reopen"][1] is None and TRANSITIONS["reopen"][0] == {"exhausted", "rejected"})
    chk("v1.48 升級非唯人(HUMAN_ONLY 空)", HUMAN_ONLY == set())
    chk("approve/activate 仍在狀態機", {"approve", "activate"} <= set(TRANSITIONS))

    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.knowledge.curation --selftest;免 DB 免 API)")
