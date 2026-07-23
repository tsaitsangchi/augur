"""完整性 critic + loop-until-dry — 「還缺什麼」枚舉 + 停機判定(P3 完整版;模式 5/6)。

🎯 這支在做什麼(白話):兩件事——
   ① loop-until-dry:多輪審議「連續 K 輪無新確定性發現(confirmed/refuted)才停」(簡單 count<N 會漏長尾);
   ② 完整性枚舉(機械先行):題目提到的真實表,哪些尚未被任何 confirmed/refuted 檢查覆蓋——
      機械查(information_schema)、非 LLM 猜;缺口=下一輪 lens 的提示。
   **只判「有無新確定性訊號」,不自行裁決**(裁決仍在 verifiers;#15)。

守 #15(dry 判定只認 oracle 確定性發現、不認 escalated 湊數)· #12(完整性枚舉走 information_schema 實查)。

執行指令矩陣（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.deliberation.critic              # 印用途+公開入口（唯讀）
  python -m augur.deliberation.critic --selftest   # 純紅綠自測（零 IO）
"""
import re

from augur.core import db

_DETERMINISTIC = ("confirmed", "refuted")


def new_deterministic_keys(agg, seen_keys):
    """本輪聚合中,尚未見過且有 oracle 確定性定論(confirmed/refuted)之 key 集。"""
    return {a["key"] for a in agg if a["verdict"] in _DETERMINISTIC and a["key"] not in seen_keys}


def is_dry(rounds_without_new, k=2):
    """連續 k 輪無新確定性發現 → dry(停機)。"""
    return rounds_without_new >= k


def uncovered_tables(topic, agg):
    """完整性枚舉:題目 snake_case 詞命中之真實表,哪些未被任何 confirmed/refuted 覆蓋(機械、非 LLM)。
    回 [table]——供下一輪 lens 提示「這些表還沒驗」。"""
    tokens = {t for t in re.findall(r"[a-z][a-z0-9_]{3,}", topic.lower())}
    if not tokens:
        return []
    real = set()
    with db.connect() as conn, db.transaction(conn) as cur:
        for t in list(tokens)[:12]:
            cur.execute("SELECT table_name FROM information_schema.tables "
                        "WHERE table_schema='public' AND table_name LIKE %s LIMIT 6", (f"%{t}%",))
            real.update(r[0] for r in cur.fetchall())
    # 已被確定性檢查觸及之表(從 confirmed/refuted 的 anchor 抽表名)
    covered = set()
    for a in agg:
        if a["verdict"] in _DETERMINISTIC:
            for tbl in re.findall(r"\b([a-z_][a-z0-9_]{3,})\b", a["anchor"] or ""):
                if tbl in real:
                    covered.add(tbl)
    return sorted(real - covered)


def _selftest():
    """自測（零 DB/零 API、可個別驗證 #29a）：合成資料紅綠測 new_deterministic_keys/is_dry——
    核心不變式回歸鎖（只認 confirmed/refuted、排除 escalated 湊數 #15、連續 k 輪才 dry）。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    agg = [{"key": "a", "verdict": "confirmed"}, {"key": "b", "verdict": "refuted"},
           {"key": "c", "verdict": "escalated"}, {"key": "d", "verdict": "confirmed"}]
    chk("new_deterministic_keys 只認 confirmed/refuted(排 escalated 湊數 #15)",
        new_deterministic_keys(agg, set()) == {"a", "b", "d"})
    chk("new_deterministic_keys 排除 seen_keys",
        new_deterministic_keys(agg, {"a", "d"}) == {"b"})
    chk("new_deterministic_keys 空輸入→空集", new_deterministic_keys([], set()) == set())
    chk("is_dry 未達 k→False", is_dry(1, k=2) is False)
    chk("is_dry 達 k→True", is_dry(2, k=2) is True)
    chk("is_dry 自訂 k 邊界", is_dry(2, k=3) is False and is_dry(3, k=3) is True)
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("入口:new_deterministic_keys / is_dry / uncovered_tables")
    print("(自測:python -m augur.deliberation.critic --selftest;免 DB 免 API)")
