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
    # D3：ready 須逐 item 軸覆蓋證據（axis_domain_mapped＝domain 落於映射工件）；
    # 未映射→pending（誠實「軸證據未落」），**不是** blocked——標籤不作答閘（KH-XDOM-S01），
    # answer_status 之 eligible 路徑不受 pending 影響（derive_answer_status 僅擋 BLOCKED）。
    elif row.get("axis_domain_mapped") and (adapter in CHANNEL_BY_ADAPTER or row["source_key"]):
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
        "axis_domain_mapped": bool(row.get("axis_domain_mapped")),
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


def _select_sql(*, has_fulltext_status, has_import_qualification,
                has_principle_domain_map=False, has_knowledge_domain_map=False):
    # terminal_blocked＝有 status 終態帳且仍無全文（FT-COV：有 text≠不可答；
    # 僅因曾 skip_no_oa 等而留 status、後來已有 abstract/全文者不得誤擋 KH4）。
    # 'unattempted'（D1 回填旗標）＝「還沒試」非終態——不排除則 12 萬件被誤判 terminal_blocked。
    blocked_expr = (
        """(
          EXISTS (SELECT 1 FROM knowledge_fulltext_status f
                  WHERE f.item_id=i.item_id AND f.status <> 'unattempted')
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
    # D3（KH5 恆 ready 收緊）：軸證據＝item.domain 落於決策層映射工件
    #（principle_domain_map.domain ∪ knowledge_domain_map.augur_domain/openalex_field）。
    # 工件表缺 → false（fail-closed：無工件即無軸證據）；納新域＝決策層 INSERT 一列（#29b 零改碼）。
    _axis_parts = []
    if has_principle_domain_map:
        _axis_parts.append(
            "EXISTS (SELECT 1 FROM principle_domain_map pm WHERE pm.domain = i.domain)")
    if has_knowledge_domain_map:
        _axis_parts.append(
            "EXISTS (SELECT 1 FROM knowledge_domain_map km "
            "WHERE km.augur_domain = i.domain OR km.openalex_field = i.domain)")
    axis_map_expr = ("(" + " OR ".join(_axis_parts) + ")") if _axis_parts else "false"
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
        {axis_map_expr} AS axis_domain_mapped,
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
        has_principle_domain_map=_table_exists(cur, "principle_domain_map"),
        has_knowledge_domain_map=_table_exists(cur, "knowledge_domain_map"),
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
    # D3 紅先驗：erp_tiptop 真實形狀 fixture（live 2026-08-01：kh4_state 141,873 列、無任何映射工件列）
    axis_fx = {
        "approval_status": "active", "has_text": True, "has_sentence": True,
        "has_embedding": True, "has_terminal_block": False, "entity_type": "paper",
        "license": "owned_local", "domain": "erp_tiptop", "adapter": "local_files",
        "qual_verdict": None, "staging_promoted": True, "source_key": "local_files_local",
        "axis_domain_mapped": False,
    }
    erp = derive_states(axis_fx)
    chk("未映射域 → axis pending（舊邏輯下本斷言必紅）", erp["kh_axis_state"] == AXIS_PENDING)
    chk("未映射域不動作答閘（KH-XDOM-S01）", erp["answer_status"] == ANSWER_ELIGIBLE)
    mapped = derive_states({**axis_fx, "domain": "quant_finance", "axis_domain_mapped": True})
    chk("映射域 → axis ready", mapped["kh_axis_state"] == AXIS_READY)
    chk("缺映射工件表 → SQL 落 false（fail-closed）",
        "false AS axis_domain_mapped" in _select_sql(has_fulltext_status=False,
                                                     has_import_qualification=False))
    chk("terminal_blocked 仍排除 unattempted（D1 防回退絆線）",
        "f.status <> 'unattempted'" in _select_sql(has_fulltext_status=True,
                                                   has_import_qualification=False))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.knowledge.kh4 --selftest;免 DB 免 API)")
