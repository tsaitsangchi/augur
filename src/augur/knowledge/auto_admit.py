"""KH10 漸進自動入庫編排 — admit_depth 0…10 水印（憲章 v1.48.0）。

🎯 這支在做什麼(白話):對已在庫的 knowledge_item（原文已准入）逐層評估／UPDATE
   KH1→KH10 精準度水印；每過一層立刻寫 knowhow_auto_admit_state，深層 fail／未建
   則停在當前 depth、不回滾原文。可選機械 activate 來源（system=True）。
   另供顧問／檢索：依 admit_depth 作答排序（KH9＞KH8＞KH7…；≥7 本地 know-how 優於公版 works）。
守 憲章 v1.48.0(一律准入)· #12· #15(誠實 skip／fail)· FZ-keep· PME-GATE-keep· NHC-keep。

執行指令矩陣(本檔=library #18；免 DB 可個別驗證):
  python -m augur.knowledge.auto_admit
  python -m augur.knowledge.auto_admit --selftest
"""
from __future__ import annotations

import json
from typing import Any

ACTOR = "system:kh10_auto_admit"

LAYER_NAMES = {
    0: "RAW",
    1: "KH1_Qualification",
    2: "KH2_Admission_Assist",
    3: "KH3_Terminal",
    4: "KH4_Retrieval_Answer",
    5: "KH5_Axis",
    6: "KH6_Interaction",
    7: "KH7_Adversarial",
    8: "KH8_Evidence",
    9: "KH9_Synthesis",
    10: "KH10_Governance",
}

# 尚未 LAND 的層：評估為 skipped，不抬 depth（不擋較淺）
# KH8/KH9 min-LAND 2026-07-29 → 可評估；KH10 進化治理仍另層
UNBUILT_LAYERS: set[int] = set()


def _table_exists(cur, name: str) -> bool:
    cur.execute("SELECT to_regclass(%s)", (f"public.{name}",))
    return bool(cur.fetchone()[0])


def _json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, default=str)


def channel_for_adapter(adapter: str | None, protocol: str | None = None) -> str:
    if adapter == "local_files" or protocol == "local_file":
        return "local_files"
    if adapter == "sftp" or protocol == "sftp":
        return "sftp"
    return "topic_harvest"


def load_gate(cur) -> dict:
    if not _table_exists(cur, "knowhow_auto_admit_gate"):
        return {
            "enabled": True,
            "raw_floor_enabled": True,
            "progressive_enabled": True,
            "max_auto_depth": 9,
            "require_kh8": True,
            "require_kh9": True,
        }
    cur.execute(
        """
        SELECT enabled, raw_floor_enabled,
               COALESCE(progressive_enabled, true),
               COALESCE(max_auto_depth, 9),
               require_kh8, require_kh9
        FROM knowhow_auto_admit_gate WHERE gate_id='auto_admit_v1'
        """
    )
    row = cur.fetchone()
    if not row:
        return {
            "enabled": True,
            "raw_floor_enabled": True,
            "progressive_enabled": True,
            "max_auto_depth": 9,
            "require_kh8": True,
            "require_kh9": True,
        }
    return {
        "enabled": bool(row[0]),
        "raw_floor_enabled": bool(row[1]),
        "progressive_enabled": bool(row[2]),
        "max_auto_depth": int(row[3]),
        "require_kh8": bool(row[4]),
        "require_kh9": bool(row[5]),
    }


def get_admit_depth(cur, target_kind: str, target_id: str) -> int:
    if not _table_exists(cur, "knowhow_auto_admit_state"):
        return 0
    cur.execute(
        "SELECT admit_depth FROM knowhow_auto_admit_state "
        "WHERE target_kind=%s AND target_id=%s",
        (target_kind, str(target_id)),
    )
    row = cur.fetchone()
    return int(row[0]) if row else 0


# 作答帶：KH7／8／9 視為「深水印本地 know-how」（KH9-first 計畫）
DEEP_KH_FLOOR = 7


def load_admit_depths(cur, item_ids: list[int] | tuple[int, ...]) -> dict[int, int]:
    """批量讀 item → admit_depth；無列／表缺 → 0。"""
    ids = sorted({int(i) for i in item_ids if i is not None})
    if not ids:
        return {}
    if not _table_exists(cur, "knowhow_auto_admit_state"):
        return {i: 0 for i in ids}
    cur.execute(
        """
        SELECT target_id::bigint, admit_depth
        FROM knowhow_auto_admit_state
        WHERE target_kind='item' AND target_id = ANY(%s::text[])
        """,
        ([str(i) for i in ids],),
    )
    found = {int(tid): int(d) for tid, d in cur.fetchall()}
    return {i: found.get(i, 0) for i in ids}


def rank_item_citations(cites: list, depths: dict[int, int] | None = None,
                        *, deep_floor: int = DEEP_KH_FLOOR) -> list:
    """顧問／檢索排序：KH9＞KH8＞KH7…；depth≥deep_floor 的 items 先於 works／Attached；
    同帶內 -score、-sent_id。不丟引文、不放寬相關度（呼叫端已濾）。"""
    if not cites:
        return []
    depths = depths or {}

    def _item_id(c):
        return getattr(c, "item_id", None)

    def _score(c):
        try:
            return float(getattr(c, "score", 0) or 0)
        except (TypeError, ValueError):
            return 0.0

    def _sent_id(c):
        sid = getattr(c, "sent_id", None)
        return int(sid) if sid is not None else 0

    deep_items, shallow_items, others = [], [], []
    for c in cites:
        iid = _item_id(c)
        if iid is None:
            others.append(c)
            continue
        d = int(depths.get(int(iid), 0))
        bucket = deep_items if d >= deep_floor else shallow_items
        bucket.append(c)

    def _item_key(c):
        iid = int(_item_id(c))
        return (-int(depths.get(iid, 0)), -_score(c), _sent_id(c))

    deep_items.sort(key=_item_key)
    shallow_items.sort(key=_item_key)
    # others（works／Attached）保持相對次序，插在 deep 與 shallow 之間
    return deep_items + others + shallow_items


def rank_citations_kh_first(cites: list, *, deep_floor: int = DEEP_KH_FLOOR) -> list:
    """無 cur 時自連 DB 載 depth 後排序（advise 主路徑用）。"""
    ids = [int(getattr(c, "item_id")) for c in cites if getattr(c, "item_id", None) is not None]
    if not ids:
        return list(cites)
    from augur.core import db

    with db.connect() as conn, db.transaction(conn) as cur:
        depths = load_admit_depths(cur, ids)
    return rank_item_citations(cites, depths, deep_floor=deep_floor)


def upsert_state(cur, *, target_kind, target_id, channel, admit_depth,
                 layer_scores, last_run_id=None):
    cur.execute(
        """
        INSERT INTO knowhow_auto_admit_state
          (target_kind, target_id, channel, admit_depth, layer_scores, updated_at, last_run_id)
        VALUES (%s,%s,%s,%s,%s::jsonb, now(), %s)
        ON CONFLICT (target_kind, target_id) DO UPDATE SET
          channel=EXCLUDED.channel,
          admit_depth=GREATEST(knowhow_auto_admit_state.admit_depth, EXCLUDED.admit_depth),
          layer_scores=EXCLUDED.layer_scores,
          updated_at=now(),
          last_run_id=COALESCE(EXCLUDED.last_run_id, knowhow_auto_admit_state.last_run_id)
        """,
        (target_kind, str(target_id), channel, admit_depth, _json(layer_scores), last_run_id),
    )


def _item_snapshot(cur, item_id: int) -> dict | None:
    cur.execute(
        """
        SELECT i.item_id, i.source_key, i.domain, i.entity_type,
               ks.adapter, ks.protocol, COALESCE(ks.approval_status, 'missing'),
               EXISTS (SELECT 1 FROM knowledge_item_text x WHERE x.item_id=i.item_id),
               EXISTS (
                 SELECT 1 FROM knowledge_item_text x
                 JOIN knowledge_sentence s ON s.itext_id=x.itext_id
                 WHERE x.item_id=i.item_id),
               EXISTS (
                 SELECT 1 FROM knowledge_item_text x
                 JOIN knowledge_sentence s ON s.itext_id=x.itext_id
                 JOIN knowledge_sentence_embedding e ON e.sent_id=s.sent_id
                 WHERE x.item_id=i.item_id)
        FROM knowledge_item i
        LEFT JOIN knowledge_source ks ON ks.source_key=i.source_key
        WHERE i.item_id=%s
        """,
        (item_id,),
    )
    row = cur.fetchone()
    if not row:
        return None
    return {
        "item_id": row[0],
        "source_key": row[1],
        "domain": row[2],
        "entity_type": row[3],
        "adapter": row[4],
        "protocol": row[5],
        "approval_status": row[6],
        "has_text": bool(row[7]),
        "has_sentence": bool(row[8]),
        "has_embedding": bool(row[9]),
    }


def evaluate_layer(cur, depth: int, snap: dict) -> dict:
    """回 {verdict: pass|fail|skipped|escalate, note, action?}。"""
    item_id = snap["item_id"]
    source_key = snap["source_key"]

    if depth in UNBUILT_LAYERS:
        return {"verdict": "skipped", "note": f"{LAYER_NAMES[depth]} 未 LAND"}

    if depth == 0:
        if snap["has_text"]:
            return {"verdict": "pass", "note": "item_text 在庫", "action": "raw_present"}
        return {"verdict": "fail", "note": "無 item_text"}

    if depth == 1:
        # KH1：有 qual pass，或既有原文（一律准入＝既有庫可視為 qual 已過）
        if _table_exists(cur, "knowledge_import_qualification"):
            cur.execute(
                """
                SELECT verdict FROM knowledge_import_qualification
                WHERE item_id=%s
                ORDER BY ingested_at DESC NULLS LAST, qualification_id DESC
                LIMIT 1
                """,
                (item_id,),
            )
            q = cur.fetchone()
            if q and q[0] == "pass":
                return {"verdict": "pass", "note": "qualification=pass"}
            if q and q[0] in ("reject", "error"):
                # 仍有原文 → 不擋（v1.48 一律准入）；記 escalate 否：pass with note
                if snap["has_text"]:
                    return {"verdict": "pass", "note": f"qual={q[0]} 但原文在庫→准入保留"}
                return {"verdict": "fail", "note": f"qualification={q[0]}"}
        if snap["has_text"]:
            return {"verdict": "pass", "note": "既有原文＝KH1 視同通過"}
        return {"verdict": "fail", "note": "無 qual 且無原文"}

    if depth == 2:
        # KH2：assist 無硬擋，或來源已 active／無 assist 表
        if _table_exists(cur, "knowledge_admission_assist") and source_key:
            cur.execute(
                """
                SELECT flags FROM knowledge_admission_assist
                WHERE (target_kind='source' AND target_id=%s)
                   OR (target_id=%s)
                ORDER BY assist_id DESC
                LIMIT 1
                """,
                (source_key, source_key),
            )
            row = cur.fetchone()
            if row and row[0]:
                flags = row[0] if isinstance(row[0], dict) else json.loads(row[0] or "{}")
                if flags.get("license_risk") or flags.get("block"):
                    return {"verdict": "fail", "note": f"assist 硬擋 flags={flags}"}
        if snap["approval_status"] == "active" or snap["has_text"]:
            return {"verdict": "pass", "note": "KH2／KH×KH 種子可進（來源或原文就緒）"}
        return {"verdict": "fail", "note": "來源未 active 且無原文"}

    if depth == 3:
        if snap["has_sentence"] or snap["has_text"]:
            return {
                "verdict": "pass",
                "note": "terminal 材料就緒（sentence 或 text）",
                "action": "terminal_ready",
            }
        return {"verdict": "fail", "note": "無 text／sentence"}

    if depth == 4:
        # 刷新 KH4 再讀
        from augur.knowledge import kh4

        if _table_exists(cur, "knowledge_kh4_state"):
            kh4.refresh_items(cur, item_ids=[item_id])
            cur.execute(
                "SELECT answer_status FROM knowledge_kh4_state WHERE item_id=%s",
                (item_id,),
            )
            row = cur.fetchone()
            if row and row[0] == "eligible":
                return {"verdict": "pass", "note": "KH4 eligible", "action": "kh4_refresh"}
            if row:
                return {
                    "verdict": "fail",
                    "note": f"KH4 answer_status={row[0]}（進庫≠可答）",
                    "action": "kh4_refresh",
                }
        if snap["has_embedding"]:
            return {"verdict": "pass", "note": "有 embedding、kh4 表缺→暫 pass"}
        return {"verdict": "fail", "note": "未 eligible／無 embedding"}

    if depth == 5:
        if _table_exists(cur, "knowledge_kh4_state"):
            cur.execute(
                "SELECT kh_axis_state FROM knowledge_kh4_state WHERE item_id=%s",
                (item_id,),
            )
            row = cur.fetchone()
            if row and row[0] == "ready":
                return {"verdict": "pass", "note": "kh_axis_state=ready"}
            if row and row[0] == "blocked":
                return {"verdict": "fail", "note": "kh_axis_state=blocked"}
        if snap["domain"]:
            return {"verdict": "pass", "note": "有 domain＝軸起步"}
        return {"verdict": "fail", "note": "無軸／domain"}

    if depth == 6:
        if _table_exists(cur, "knowledge_kh4_state"):
            cur.execute(
                "SELECT interaction_state FROM knowledge_kh4_state WHERE item_id=%s",
                (item_id,),
            )
            row = cur.fetchone()
            if row and row[0] == "ready":
                return {"verdict": "pass", "note": "interaction_state=ready"}
        if _table_exists(cur, "knowhow_interaction_probe_run"):
            cur.execute("SELECT 1 FROM knowhow_interaction_probe_run LIMIT 1")
            if cur.fetchone():
                return {"verdict": "pass", "note": "交互 probe run 帳存在（庫級）"}
        if snap["has_embedding"]:
            return {"verdict": "pass", "note": "embedding 可投影起步"}
        return {"verdict": "fail", "note": "交互投影未就緒"}

    if depth == 7:
        if not _table_exists(cur, "knowhow_kh7_eligibility"):
            return {"verdict": "skipped", "note": "KH7 表未建"}
        # 以「最新 probe run_id」庫級裁決為準（非全域任意一列 decided_at）：
        # decline 探針本應 fail，不得因同批／回放舊列覆蓋掉同 run 已存在的 pass。
        cur.execute("SELECT max(run_id) FROM knowhow_kh7_eligibility")
        mx = cur.fetchone()
        if not mx or mx[0] is None:
            return {"verdict": "fail", "note": "尚 KH7 裁決"}
        run_id = int(mx[0])
        cur.execute(
            """
            SELECT 1 FROM knowhow_kh7_eligibility
             WHERE run_id=%s AND status='eligibility_pass'
             LIMIT 1
            """,
            (run_id,),
        )
        if cur.fetchone():
            return {
                "verdict": "pass",
                "note": f"run_id={run_id} 有 eligibility_pass（庫級；≠approve）",
            }
        cur.execute(
            """
            SELECT status FROM knowhow_kh7_eligibility
             WHERE run_id=%s
             ORDER BY eligibility_id DESC LIMIT 1
            """,
            (run_id,),
        )
        row = cur.fetchone()
        if row:
            return {
                "verdict": "fail",
                "note": f"run_id={run_id} 無 pass；最近={row[0]}（誠實；不擋較淺）",
            }
        return {"verdict": "fail", "note": "尚 KH7 裁決"}

    if depth == 8:
        from augur.knowledge import evidence as kh8

        return kh8.evaluate_item_evidence(cur, snap)

    if depth == 9:
        from augur.knowledge import synthesis as kh9

        return kh9.evaluate_item_synthesis(cur, snap)

    if depth == 10:
        gate = load_gate(cur)
        if gate["enabled"]:
            return {"verdict": "pass", "note": "gate.enabled；治理列帳可", "action": "gov_ok"}
        return {"verdict": "fail", "note": "gate.enabled=false"}

    return {"verdict": "skipped", "note": f"depth {depth} 無評估器"}


def maybe_activate_source(cur, source_key: str, *, apply: bool) -> list:
    """機械 approve→activate；回 actions 列表。"""
    actions = []
    if not source_key or not apply:
        return actions
    cur.execute(
        "SELECT approval_status FROM knowledge_source WHERE source_key=%s",
        (source_key,),
    )
    row = cur.fetchone()
    if not row:
        return actions
    status = row[0]
    if status == "active":
        return actions
    from augur.knowledge.curation import transition

    try:
        if status == "proposed":
            transition(
                source_key, "approve", ACTOR,
                reason="v1.48.0 auto_admit progressive", system=True,
            )
            actions.append({"action": "approve", "source_key": source_key})
            status = "approved"
        if status in ("approved", "suspended"):
            # suspended→activate 合法；approved→activate
            act = "activate" if status == "approved" else "resume"
            if status == "suspended":
                transition(
                    source_key, "resume", ACTOR,
                    reason="v1.48.0 auto_admit progressive", system=True,
                )
                actions.append({"action": "resume", "source_key": source_key})
            else:
                transition(
                    source_key, "activate", ACTOR,
                    reason="v1.48.0 auto_admit progressive", system=True,
                )
                actions.append({"action": "activate", "source_key": source_key})
    except Exception as e:  # noqa: BLE001 — 記帳不炸整批
        actions.append({"action": "activate_error", "error": str(e), "source_key": source_key})
    return actions


def progressive_item(
    cur,
    item_id: int,
    *,
    up_to: int,
    apply: bool,
    activate_source: bool = True,
) -> dict:
    """對單一 item 從當前 depth 推進至 min(up_to, max_auto_depth)。"""
    gate = load_gate(cur)
    if not gate["progressive_enabled"] and up_to > 0:
        return {"ok": False, "error": "progressive_enabled=false"}
    if not gate["raw_floor_enabled"] and up_to >= 0:
        # 仍允許評估既有；僅禁「宣稱 raw 新寫」——既存庫可跑
        pass

    cap = min(int(up_to), int(gate["max_auto_depth"]))
    snap = _item_snapshot(cur, item_id)
    if not snap:
        return {"ok": False, "error": f"item {item_id} 不存在"}

    channel = channel_for_adapter(snap["adapter"], snap["protocol"])
    before = get_admit_depth(cur, "item", str(item_id))
    layer_scores: dict[str, Any] = {}
    actions: list = []
    depth = before

    if activate_source and apply and snap["source_key"] and snap["has_text"]:
        actions.extend(maybe_activate_source(cur, snap["source_key"], apply=True))
        # 刷新 snap approval
        cur.execute(
            "SELECT approval_status FROM knowledge_source WHERE source_key=%s",
            (snap["source_key"],),
        )
        r = cur.fetchone()
        if r:
            snap["approval_status"] = r[0]

    # 逐層：d < before 視為已達（單調不降）；d >= before 重評／推進
    for d in range(0, cap + 1):
        if d < before:
            layer_scores[str(d)] = {
                "verdict": "pass",
                "note": "prior_depth",
                "layer": LAYER_NAMES.get(d),
            }
            continue
        ev = evaluate_layer(cur, d, snap)
        layer_scores[str(d)] = {
            "verdict": ev["verdict"],
            "note": ev.get("note"),
            "layer": LAYER_NAMES.get(d),
        }
        if ev.get("action"):
            actions.append({"layer": d, "action": ev["action"]})
        if ev["verdict"] == "pass":
            depth = max(depth, d)
        elif ev["verdict"] == "skipped":
            # ── C-3 補正（2026-07-30；hugo「甲成立」＋自毀條款當日到期）
            # 病灶：require_kh8／require_kh9 讀入 gate 後**無任何路徑消費**＝空轉閘；
            # 且本迴圈之 skipped 會**繼續往上推**，故 KH8 若因「表未建」回 skipped，
            # depth 9 一過即升至 9＝**證據要件被繞過**（帳面有要件、實際無）。
            # 處置：該層若被 gate 要求，skipped **視同 fail、不得繞過**（fail-closed）。
            if (d == 8 and gate.get("require_kh8")) or (d == 9 and gate.get("require_kh9")):
                layer_scores[str(d)]["note"] = (
                    f"{ev.get('note')}｜require_kh{d}=true：skipped 視同 fail"
                    "（fail-closed；不得以「表未建」繞過證據要件）"
                )
                layer_scores[str(d)]["verdict"] = "fail"
                actions.append({"layer": d, "action": f"require_kh{d}_fail_closed"})
                break
            continue
        else:
            # fail／escalate：不抬本層；較淺 depth 保留
            break

    raw_v = "pass" if layer_scores.get("0", {}).get("verdict") == "pass" else "fail"
    full_v = "pass" if depth >= 10 else ("pending" if depth < cap else "fail")

    run_id = None
    if apply and _table_exists(cur, "knowhow_auto_admit_run"):
        cur.execute(
            """
            INSERT INTO knowhow_auto_admit_run
              (channel, target_kind, target_id, admit_depth_before, admit_depth_after,
               raw_verdict, full_verdict, verdict, layer_scores, actions, actor, note, finished_at)
            VALUES (%s,'item',%s,%s,%s,%s,%s,%s,%s::jsonb,%s::jsonb,%s,%s, now())
            RETURNING run_id
            """,
            (
                channel,
                str(item_id),
                before,
                depth,
                raw_v,
                full_v,
                full_v,
                _json(layer_scores),
                _json(actions),
                ACTOR,
                f"apply-up-to={cap}",
            ),
        )
        run_id = cur.fetchone()[0]
        upsert_state(
            cur,
            target_kind="item",
            target_id=str(item_id),
            channel=channel,
            admit_depth=depth,
            layer_scores=layer_scores,
            last_run_id=run_id,
        )

    return {
        "ok": True,
        "item_id": item_id,
        "channel": channel,
        "admit_depth_before": before,
        "admit_depth_after": depth,
        "layer_scores": layer_scores,
        "actions": actions,
        "run_id": run_id,
        "dry_run": not apply,
    }


def list_candidate_item_ids(
    cur,
    *,
    limit: int = 50,
    max_depth_lt: int | None = None,
    min_depth: int | None = None,
) -> list[int]:
    """有原文且 admit_depth ∈ [min_depth, max_depth_lt) 的 item。

    預設 ORDER BY depth ASC（先抬淺層）。若指定 min_depth（如 4），專掃已達該層、
    要繼續往上衝的佇列（避免 depth 0 海量占滿 limit）。
    """
    gate = load_gate(cur)
    cap = gate["max_auto_depth"]
    if max_depth_lt is None:
        max_depth_lt = cap
    lo = int(min_depth) if min_depth is not None else 0
    if _table_exists(cur, "knowhow_auto_admit_state"):
        cur.execute(
            """
            SELECT i.item_id
            FROM knowledge_item i
            JOIN knowledge_item_text x ON x.item_id=i.item_id
            LEFT JOIN knowhow_auto_admit_state st
              ON st.target_kind='item' AND st.target_id=i.item_id::text
            WHERE COALESCE(st.admit_depth, 0) >= %s
              AND COALESCE(st.admit_depth, 0) < %s
            GROUP BY i.item_id, st.admit_depth
            ORDER BY COALESCE(st.admit_depth, 0) ASC, i.item_id
            LIMIT %s
            """,
            (lo, max_depth_lt, limit),
        )
    else:
        if lo > 0:
            return []
        cur.execute(
            """
            SELECT i.item_id FROM knowledge_item i
            JOIN knowledge_item_text x ON x.item_id=i.item_id
            GROUP BY i.item_id
            ORDER BY i.item_id
            LIMIT %s
            """,
            (limit,),
        )
    return [int(r[0]) for r in cur.fetchall()]


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("LAYER_NAMES 0..10", set(LAYER_NAMES) == set(range(11)))
    chk("UNBUILT 空（8/9 LAND）", UNBUILT_LAYERS == set())
    chk("channel local", channel_for_adapter("local_files") == "local_files")
    chk("channel topic", channel_for_adapter("openalex_works") == "topic_harvest")
    chk("ACTOR", ACTOR == "system:kh10_auto_admit")

    class _Cur:
        """模擬：表未建 → evaluate 8/9 誠實 skipped。"""

        def __init__(self):
            self._last = None

        def execute(self, sql, params=None):
            s = str(sql)
            if "to_regclass" in s:
                self._last = (None,)
            else:
                self._last = None

        def fetchone(self):
            return self._last

    snap = {
        "item_id": 1,
        "source_key": "x",
        "has_text": True,
        "has_sentence": False,
        "has_embedding": False,
        "approval_status": "active",
        "domain": "local",
        "adapter": "local_files",
        "protocol": "local_file",
        "entity_type": "doc",
    }
    ev8 = evaluate_layer(_Cur(), 8, snap)
    chk("depth8 表未建→skipped", ev8["verdict"] == "skipped")
    ev9 = evaluate_layer(_Cur(), 9, snap)
    chk("depth9 表未建→skipped", ev9["verdict"] == "skipped")
    ev0 = evaluate_layer(_Cur(), 0, snap)
    chk("depth0 pass with text", ev0["verdict"] == "pass")

    from types import SimpleNamespace as S

    cites = [
        S(item_id=1, score=0.9, sent_id=10),   # depth 3 shallow
        S(item_id=2, score=0.5, sent_id=20),   # depth 9 deep
        S(item_id=3, score=0.8, sent_id=30),   # depth 7 deep
        S(work_title="論語", score=0.99),      # works — no item_id
        S(item_id=4, score=0.95, sent_id=40),  # depth 8 deep, high score
    ]
    depths = {1: 3, 2: 9, 3: 7, 4: 8}
    ranked = rank_item_citations(cites, depths)
    ids_order = [getattr(c, "item_id", None) for c in ranked]
    chk("KH9-first 序 9→8→7→works→shallow",
        ids_order == [2, 4, 3, None, 1])
    chk("同 depth 較高 score 在前",
        rank_item_citations(
            [S(item_id=9, score=0.1, sent_id=1), S(item_id=9, score=0.9, sent_id=2)],
            {9: 9},
        )[0].sent_id == 2)
    chk("DEEP_KH_FLOOR=7", DEEP_KH_FLOOR == 7)

    from augur.knowledge import evidence as kh8
    from augur.knowledge import synthesis as kh9

    chk("kh8 selftest", kh8._selftest() == 0)
    chk("kh9 selftest", kh9._selftest() == 0)
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or "").split("🎯")[0].strip())
    print("公開: progressive_item / list_candidate_item_ids / load_gate / evaluate_layer / "
          "load_admit_depths / rank_item_citations / rank_citations_kh_first")
    print("(自測: python -m augur.knowledge.auto_admit --selftest)")
