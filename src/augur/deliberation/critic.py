"""完整性 critic + loop-until-dry — 「還缺什麼」枚舉 + 停機判定(P3 完整版;模式 5/6)。

🎯 這支在做什麼(白話):兩件事——
   ① loop-until-dry:多輪審議「連續 K 輪無新確定性發現(confirmed/refuted)才停」(簡單 count<N 會漏長尾);
   ② 完整性枚舉(機械先行):題目提到的真實表,哪些尚未被任何 confirmed/refuted 檢查覆蓋——
      機械查(information_schema)、非 LLM 猜;缺口=下一輪 lens 的提示。
   **只判「有無新確定性訊號」,不自行裁決**(裁決仍在 verifiers;#15)。

守 #15(dry 判定只認 oracle 確定性發現、不認 escalated 湊數)· #12(完整性枚舉走 information_schema 實查)。
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
