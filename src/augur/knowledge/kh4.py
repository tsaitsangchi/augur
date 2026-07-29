"""KH4 作答資格狀態聚合器 — qualification→axis→projection→eligibility 的最小 SSOT。

🎯 這支在做什麼(白話):把 knowledge item 依現有帳本/全文/切句/嵌入/blocked 終態，
   聚合成一份最小 KH4 狀態(`knowledge_kh4_state`)；讓匯入/harvest 入口可寫共同狀態，
   並讓 advisor/retrieval 只把 `answer_status='eligible'` 的材料當一般答案材料。
   本版是最小骨架：四層狀態皆有欄位，但 KH-axis 與 interaction projection 先用保守機械衍生，
   **不**宣稱已完成全量語意投影/PME 映射。
守 #12(單一住所)· #15(不讓 provisional 直接進一般回答空間)· KH-XDOM/KH4 最小 slice· FZ-keep。

執行指令矩陣(本檔=library #18;免 DB 免 API 可個別驗證):
  python -m augur.knowledge.kh4
  python -m augur.knowledge.kh4 --selftest
"""
from __future__ import annotations

import json

from augur.knowledge import corpus

QUAL_PENDING = "pending"
QUAL_PASSED = "passed"
QUAL_BLOCKED = "blocked"

AXIS_PENDING = "pending"
AXIS_READY = "ready"
AXIS_BLOCKED = "blocked"

PROJ_PENDING = "pending"
PROJ_READY = "ready"
PROJ_BLOCKED = "blocked"

ANSWER_PROVISIONAL = "provisional"
ANSWER_ELIGIBLE = "eligible"
ANSWER_BLOCKED = "blocked"
ANSWER_INELIGIBLE = "ineligible"

CHANNEL_BY_ADAPTER = {
    "local_files": "local",
    "sftp": "sftp",
}


def _json(data):
    return json.dumps(data, ensure_ascii=False)


def _table_exists(cur, name):
    cur.execute("SELECT to_regclass(%s)", (name,))
    return bool(cur.fetchone()[0])


def semantic_eligible(*, entity_type, license, has_embedding):
    return (
        entity_type in corpus.SEMANTIC_ENTITY_TYPES
        and license in corpus.LICENSE_WHITELIST
        and has_embedding
    )


def derive_answer_status(*, qual_state, axis_state, proj_state, entity_type, license, has_embedding):
    if qual_state == QUAL_BLOCKED or axis_state == AXIS_BLOCKED or proj_state == PROJ_BLOCKED:
        return ANSWER_BLOCKED
    if semantic_eligible(entity_type=entity_type, license=license, has_embedding=has_embedding):
        return ANSWER_ELIGIBLE
    if entity_type not in corpus.SEMANTIC_ENTITY_TYPES:
        return ANSWER_INELIGIBLE
    return ANSWER_PROVISIONAL


def derive_states(row):
    approval = row["approval_status"]
    has_text = row["has_text"]
    has_sentence = row["has_sentence"]
    has_embedding = row["has_embedding"]
    has_terminal_block = row["has_terminal_block"]
    entity_type = row["entity_type"]
    license = row["license"]
    domain = row["domain"]
    adapter = row["adapter"]
    qual_verdict = row["qual_verdict"]

    if qual_verdict in ("reject", "error") or has_terminal_block:
        qual_state = QUAL_BLOCKED
    elif qual_verdict == "pass" or has_text or row["staging_promoted"]:
        qual_state = QUAL_PASSED
    else:
        qual_state = QUAL_PENDING

    if approval != "active":
        axis_state = AXIS_BLOCKED
    elif domain and (adapter in CHANNEL_BY_ADAPTER or row["source_key"]):
        axis_state = AXIS_READY
    else:
        axis_state = AXIS_PENDING

    if has_terminal_block:
        proj_state = PROJ_BLOCKED
    elif has_embedding:
        proj_state = PROJ_READY
    elif has_text or has_sentence:
        proj_state = PROJ_PENDING
    else:
        proj_state = PROJ_PENDING

    answer_status = derive_answer_status(
        qual_state=qual_state,
        axis_state=axis_state,
        proj_state=proj_state,
        entity_type=entity_type,
        license=license,
        has_embedding=has_embedding,
    )
    answer_state = (
        "eligible" if answer_status == ANSWER_ELIGIBLE
        else "blocked" if answer_status == ANSWER_BLOCKED
        else "ineligible" if answer_status == ANSWER_INELIGIBLE
        else "provisional"
    )
    reason = (
        "terminal_blocked" if has_terminal_block else
        "embedded_semantic_material" if answer_status == ANSWER_ELIGIBLE else
        "non_semantic_entity_type" if answer_status == ANSWER_INELIGIBLE else
        "awaiting_projection"
    )
    evidence = {
        "approval_status": approval,
        "adapter": adapter,
        "has_text": has_text,
        "has_sentence": has_sentence,
        "has_embedding": has_embedding,
        "has_terminal_block": has_terminal_block,
        "qual_verdict": qual_verdict,
        "staging_promoted": row["staging_promoted"],
        "license": license,
        "entity_type": entity_type,
    }
    return {
        "qualification_state": qual_state,
        "kh_axis_state": axis_state,
        "interaction_state": proj_state,
        "answer_state": answer_state,
        "answer_status": answer_status,
        "status_reason": reason,
        "evidence": evidence,
    }


def _select_sql(*, has_fulltext_status, has_import_qualification):
    # terminal_blocked＝有 status 終態帳且仍無全文（FT-COV：有 text≠不可答；
    # 僅因曾 skip_no_oa 等而留 status、後來已有 abstract/全文者不得誤擋 KH4）
    blocked_expr = (
        """(
          EXISTS (SELECT 1 FROM knowledge_fulltext_status f WHERE f.item_id=i.item_id)
          AND NOT EXISTS (SELECT 1 FROM knowledge_item_text x WHERE x.item_id=i.item_id)
        )"""
        if has_fulltext_status else "false"
    )
    qual_expr = (
        """(
          SELECT q.verdict
            FROM knowledge_import_qualification q
           WHERE q.item_id=i.item_id
           ORDER BY q.ingested_at DESC NULLS LAST, q.qualification_id DESC
           LIMIT 1
        )"""
        if has_import_qualification else "NULL::text"
    )
    return f"""
    SELECT
        i.item_id,
        i.source_key,
        i.domain,
        i.entity_type,
        ks.adapter,
        ks.protocol,
        COALESCE(ks.approval_status, 'missing') AS approval_status,
        COALESCE(
          (SELECT x.license
             FROM knowledge_item_text x
            WHERE x.item_id=i.item_id
            ORDER BY x.seq
            LIMIT 1),
          'unknown'
        ) AS license,
        EXISTS (SELECT 1 FROM knowledge_item_text x WHERE x.item_id=i.item_id) AS has_text,
        EXISTS (
          SELECT 1
            FROM knowledge_item_text x
            JOIN knowledge_sentence s ON s.itext_id=x.itext_id
           WHERE x.item_id=i.item_id
        ) AS has_sentence,
        EXISTS (
          SELECT 1
            FROM knowledge_item_text x
            JOIN knowledge_sentence s ON s.itext_id=x.itext_id
            JOIN knowledge_sentence_embedding e ON e.sent_id=s.sent_id
           WHERE x.item_id=i.item_id
        ) AS has_embedding,
        {blocked_expr} AS has_terminal_block,
        EXISTS (
          SELECT 1 FROM knowledge_staging st
           WHERE st.status='promoted' AND st.source_key=i.source_key AND st.staging_id=i.staging_id
        ) AS staging_promoted,
        {qual_expr} AS qual_verdict
    FROM knowledge_item i
    LEFT JOIN knowledge_source ks ON ks.source_key=i.source_key
    """


def refresh_items(cur, *, item_ids=None, source_key=None, domain=None, limit=None):
    if not _table_exists(cur, "knowledge_kh4_state"):
        return 0
    sql = _select_sql(
        has_fulltext_status=_table_exists(cur, "knowledge_fulltext_status"),
        has_import_qualification=_table_exists(cur, "knowledge_import_qualification"),
    )
    where = []
    params = []
    if item_ids:
        where.append("i.item_id = ANY(%s)")
        params.append(list(item_ids))
    if source_key:
        where.append("i.source_key = %s")
        params.append(source_key)
    if domain:
        where.append("i.domain = %s")
        params.append(domain)
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY i.item_id"
    if limit is not None:
        sql += " LIMIT %s"
        params.append(limit)
    cur.execute(sql, params)
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]
    n = 0
    for raw in rows:
        row = dict(zip(cols, raw))
        state = derive_states(row)
        source_channel = CHANNEL_BY_ADAPTER.get(row["adapter"], "topic")
        cur.execute(
            """
            INSERT INTO knowledge_kh4_state
              (item_id, source_key, source_channel, domain,
               qualification_state, kh_axis_state, interaction_state,
               answer_state, answer_status, status_reason, evidence, updated_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb, now())
            ON CONFLICT (item_id) DO UPDATE SET
              source_key=EXCLUDED.source_key,
              source_channel=EXCLUDED.source_channel,
              domain=EXCLUDED.domain,
              qualification_state=EXCLUDED.qualification_state,
              kh_axis_state=EXCLUDED.kh_axis_state,
              interaction_state=EXCLUDED.interaction_state,
              answer_state=EXCLUDED.answer_state,
              answer_status=EXCLUDED.answer_status,
              status_reason=EXCLUDED.status_reason,
              evidence=EXCLUDED.evidence,
              updated_at=now()
            """,
            (
                row["item_id"],
                row["source_key"],
                source_channel,
                row["domain"],
                state["qualification_state"],
                state["kh_axis_state"],
                state["interaction_state"],
                state["answer_state"],
                state["answer_status"],
                state["status_reason"],
                _json(state["evidence"]),
            ),
        )
        n += 1
    return n


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("semantic_eligible 需 embedding",
        semantic_eligible(entity_type="paper", license="cc-by", has_embedding=True)
        and not semantic_eligible(entity_type="paper", license="cc-by", has_embedding=False))
    chk("非語意型別 → ineligible",
        derive_answer_status(
            qual_state=QUAL_PASSED, axis_state=AXIS_READY, proj_state=PROJ_READY,
            entity_type="material", license="cc-by", has_embedding=True,
        ) == ANSWER_INELIGIBLE)
    chk("blocked 任一層即 blocked",
        derive_answer_status(
            qual_state=QUAL_BLOCKED, axis_state=AXIS_READY, proj_state=PROJ_READY,
            entity_type="paper", license="cc-by", has_embedding=True,
        ) == ANSWER_BLOCKED)
    sample = derive_states({
        "approval_status": "active",
        "has_text": True,
        "has_sentence": True,
        "has_embedding": True,
        "has_terminal_block": False,
        "entity_type": "paper",
        "license": "cc-by",
        "domain": "finance",
        "adapter": "openalex_works",
        "qual_verdict": None,
        "staging_promoted": True,
        "source_key": "openalex_demo",
    })
    chk("完整語意材料 → eligible", sample["answer_status"] == ANSWER_ELIGIBLE)
    # 有全文時 status 列不得當 terminal block（呼叫端應傳 has_terminal_block=False）
    unblocked = derive_states({**{
        "approval_status": "active",
        "has_text": True,
        "has_sentence": True,
        "has_embedding": True,
        "has_terminal_block": False,
        "entity_type": "paper",
        "license": "cc0",
        "domain": "economics_econometrics_and_finance",
        "adapter": "openalex_works",
        "qual_verdict": None,
        "staging_promoted": True,
        "source_key": "crossref_works",
    }})
    chk("有 text 時不因舊 skip status 擋 eligible", unblocked["answer_status"] == ANSWER_ELIGIBLE)
    still_blocked = derive_states({
        "approval_status": "active",
        "has_text": False,
        "has_sentence": False,
        "has_embedding": False,
        "has_terminal_block": True,
        "entity_type": "paper",
        "license": "unknown",
        "domain": "economics_econometrics_and_finance",
        "adapter": "openalex_works",
        "qual_verdict": None,
        "staging_promoted": False,
        "source_key": "crossref_works",
    })
    chk("無 text＋status → terminal_blocked", still_blocked["status_reason"] == "terminal_blocked")
    chk("本機 channel map 穩定", CHANNEL_BY_ADAPTER["local_files"] == "local" and CHANNEL_BY_ADAPTER["sftp"] == "sftp")
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.knowledge.kh4 --selftest;免 DB 免 API)")
