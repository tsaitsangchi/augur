"""KH10 漸進自動入庫編排 — admit_depth 0…10 水印（憲章 v1.48.0）。

🎯 這支在做什麼(白話):對已在庫的 knowledge_item 逐層評估／UPDATE KH0→KH10 精準度水印；
   每過一層立刻寫 knowhow_auto_admit_state，深層 fail／未建則停在當前 depth、不回滾原文。
   KH0（A.1）：有原文 **或** 非空 title/title_zh 即 pass（憲章普遍底線；無內容才 fail）。
   可選機械 activate 來源（system=True）。另供顧問／檢索：依 admit_depth 作答排序
   （KH9＞KH8＞KH7…；≥7 本地 know-how 優於公版 works）。
守 憲章 v1.48.0(一律准入)· v1.53(KH0 普遍)· #12· #15(誠實 skip／fail)· FZ-keep· PME-GATE-keep· NHC-keep。


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


def has_admit_state(cur, target_kind: str, target_id: str) -> bool:
    """是否已有 admit_state 列（≠ depth 值；供 KH0 破口 seeded 計數）。"""
    if not _table_exists(cur, "knowhow_auto_admit_state"):
        return False
    cur.execute(
        "SELECT 1 FROM knowhow_auto_admit_state "
        "WHERE target_kind=%s AND target_id=%s LIMIT 1",
        (target_kind, str(target_id)),
    )
    return bool(cur.fetchone())


def repromotion_locked(cur, item_id: int) -> bool:
    """item 曾被重評降級（knowhow_depth_reevaluation 有 depth_after<depth_before 列）→ D4 再晉升鎖。"""
    if not _table_exists(cur, "knowhow_depth_reevaluation"):
        return False  # 帳表不存在＝從未有降級治權行為；DB trigger 為最終防線
    cur.execute(
        "SELECT EXISTS (SELECT 1 FROM knowhow_depth_reevaluation "
        "WHERE item_id=%s AND depth_after < depth_before)",
        (int(item_id),),
    )
    return bool(cur.fetchone()[0])


# 作答帶：KH7／8／9 視為「深水印本地 know-how」（KH9-first 計畫）
DEEP_KH_FLOOR = 7

# 乙：KH8 證據有效性之進程內快取（由呼叫端以 set_kh_evidence_validity() 灌入；
# 未灌入時預設 None＝未知，深度優先照舊套用以免無 DB 連線時全面退化）。
_kh_evidence_valid_cache: dict[str, Any] = {}
# 判準快取之存活期（D2 2026-08-01 改按**裁決來源**分壽）：資料為據之裁決（ok True/False
# 皆然）＝長 TTL——D2 質量門檻後閘將以資料為據長期 False，若沿用短 TTL＝每 30s 無謂重掃全表；
# 唯 error fail-closed（取不到、error_closed=True）＝極短——否則一次 DB 瞬斷即永久關閘
# （第四次核驗實證：advisor 常駐、無自癒路徑）。
_OK_TTL_SEC = 900.0
_FAIL_TTL_SEC = 30.0


def set_kh_evidence_validity(cur) -> dict[str, Any]:
    """由已有 DB 連線之呼叫端灌入本進程之 KH8 證據有效性（乙之口徑閘）。"""
    from augur.knowledge import evidence as ev

    disc = ev.population_discriminates(cur)
    _kh_evidence_valid_cache.clear()
    _kh_evidence_valid_cache.update(disc)
    return disc


def kh_evidence_valid() -> dict[str, Any]:
    """本進程之 KH8 證據有效性——**自足取得、每進程只算一次、取不到時 fail-closed**。

    三次獨立核驗（2026-07-30）證明前版之兩病：
      (1) 呼叫端須自己正確傳 `cur`，錯了會被 `except: pass` 吞成靜默 fail-open（死碼）；
      (2) `population_discriminates` 為 146k 列全表掃（實測 4.9–7.7s），
          原逐 item／逐問答各呼一次 ⇒ 批次 ~17 天、常駐 advisor 每答 +10s。
    故本函式改為：**呼叫端零配合**（自開唯讀連線）＋**進程級記憶化**（只算一次）
    ＋**fail-closed**（算不出＝視同不具鑑別力、不套深度優先；不確定不得放行）。
    """
    # TTL（第四次獨立核驗 2026-07-30 抓到本函式引入之新洞；D2 2026-08-01 改按裁決來源分壽）：
    # advisor 為**常駐服務**（實測進程存活 1h28m），前版快取永不失效 ⇒ **DB 一次瞬斷即
    # 永久 fail-closed、無自癒**，等於把 fail-open 換成永久關閘。故：
    #   資料為據之裁決（ok True/False 皆然）＝長 TTL——閘因資料而關毋須 30s 重掃；
    #   唯 **error fail-closed（取不到）之快取 TTL 極短**——不確定不得放行，
    #   但也不得讓一次瞬斷永久生效。
    import time as _t

    _now = _t.monotonic()
    _at = _kh_evidence_valid_cache.get("_at")
    if _kh_evidence_valid_cache and _at is not None:
        # 資料為據之裁決（ok True/False 皆然）＝長 TTL；唯 error fail-closed（取不到）＝短 TTL
        _ttl = _FAIL_TTL_SEC if _kh_evidence_valid_cache.get("error_closed") else _OK_TTL_SEC
        if (_now - _at) < _ttl:
            return {k: v for k, v in _kh_evidence_valid_cache.items() if k != "_at"}
    try:
        from augur.core import db
        from augur.knowledge import evidence as ev

        with db.connect() as conn, conn.cursor() as cur:
            disc = ev.population_discriminates(cur)
    except Exception as exc:  # noqa: BLE001 — 任何取不到皆走 fail-closed，不得靜默放行
        disc = {
            "ok": False,
            "error_closed": True,
            "bands": [],
            "n": 0,
            "note": f"fail-closed：無法判定 KH8 母體鑑別力（{type(exc).__name__}）"
                    "——不套深度優先排序",
        }
    _kh_evidence_valid_cache.clear()
    _kh_evidence_valid_cache.update(disc)
    _kh_evidence_valid_cache["_at"] = _now
    return dict(disc)


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
    # ── 乙（hugo 拍板「乙＋丙並行」2026-07-30）：深度須**經有效證據**方得優先。
    # 核驗實證：現存 145,949 件之 depth 9 係以「結構上不可能鑑別」之 band=high 取得
    # （母體選擇效應致三分量恆 1.0）。若逕以 admit_depth 為首要排序鍵，等於讓
    # 橡皮章深度排在公版原典之前。故排序前先驗 KH8 母體鑑別力；不具鑑別力時
    # **一律不套用深度優先**（fail-closed），退回既有相似度序。
    if depths and not kh_evidence_valid().get("ok"):
        return list(cites)  # fail-closed：KH8 母體不具鑑別力／未能判定 ⇒ 不套深度優先
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


def _title_nonzero(snap: dict) -> str | None:
    """回第一個非空白標題欄（title 優先於 title_zh）；皆空→None。"""
    for key in ("title", "title_zh"):
        val = snap.get(key)
        if val is None:
            continue
        s = str(val).strip()
        if s:
            return s
    return None


def _kh0_understandable(snap: dict) -> dict:
    """憲章普遍 KH0：有原文 **或** 有標題語意 → pass；否則 fail-closed。

    A.1（`KH0-UNIVERSAL-A1-go`）：撤回「僅 has_text 才算理解」之 runtime 落差——
    Steward／大憲章 v1.53：標題即有語意；無原文不豁免。
    """
    if snap.get("has_text"):
        return {"verdict": "pass", "note": "item_text 在庫", "action": "raw_present"}
    if _title_nonzero(snap):
        which = "title" if (snap.get("title") or "").strip() else "title_zh"
        return {
            "verdict": "pass",
            "note": f"{which} 可理解（KH0 普遍底線／A.1）",
            "action": "title_understandable",
        }
    return {
        "verdict": "fail",
        "note": "無可理解內容（無原文且無 title/title_zh）",
        "action": "kh0_empty",
    }


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
                 WHERE x.item_id=i.item_id),
               i.title, i.title_zh
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
        "title": row[10],
        "title_zh": row[11],
    }


def evaluate_layer(cur, depth: int, snap: dict) -> dict:
    """回 {verdict: pass|fail|skipped|escalate, note, action?}。"""
    item_id = snap["item_id"]
    source_key = snap["source_key"]

    if depth in UNBUILT_LAYERS:
        return {"verdict": "skipped", "note": f"{LAYER_NAMES[depth]} 未 LAND"}

    if depth == 0:
        return _kh0_understandable(snap)
    if depth == 1:
        # KH1：真路徑＝qualification=pass。
        # 旁路 A：has_text（M-G15 既有）。
        # 旁路 B（2026-08-06 Steward global_title_kh1）：非空 title/title_zh
        #   → 與憲章「標題即語意」上延；≠來源 approve。
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
                if snap["has_text"]:
                    return {"verdict": "pass",
                            "note": f"KH1_BYPASS:qual={q[0]} 原文在庫→准入保留（零變異；存廢待裁）"}
                if _title_nonzero(snap):
                    return {
                        "verdict": "pass",
                        "note": f"KH1_TITLE:qual={q[0]} 標題可理解→KH1（global_title_kh1）",
                        "action": "kh1_title_understandable",
                    }
                return {"verdict": "fail", "note": f"qualification={q[0]}"}
        if snap["has_text"]:
            return {"verdict": "pass",
                    "note": "KH1_BYPASS:既有原文旁路（零變異指標、不得充當獨立證據；存廢待裁）"}
        if _title_nonzero(snap):
            return {
                "verdict": "pass",
                "note": "KH1_TITLE:標題可理解（global_title_kh1／憲章語意上延）",
                "action": "kh1_title_understandable",
            }
        return {"verdict": "fail", "note": "無 qual、無原文、無標題"}

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

    # KH5／KH6 之判準自 2026-07-31 起**一律逐 item**——原有之「庫級」與「粗代理」後路已移除。
    # 移除理由（實證，非設計偏好）：舊碼下 KH2/KH5/KH6/KH7 對**全母體恆 pass**，
    #   · KH5 後路 `if snap["domain"]` ⇒ knowledge_item.domain 零 NULL（285,179/285,179）；
    #   · KH6 後路 `SELECT 1 FROM knowhow_interaction_probe_run LIMIT 1` ⇒ 該表 7 列且
    #     **無任何 item 級欄位**（run_id/started_at/script/git_sha/note/params_json），
    #     即「有人跑過一次探針腳本」就放行全庫二十八萬件，連 interaction_state 標
    #     pending(15,365)／blocked(556) 者亦一併通過。
    # 後果：145,948 件之 depth=7 實際只代表「has_text ∧ KH4 eligible」（對照 KH4
    #   eligible=145,954），KH5/6/7 三層對結果之貢獻為 0，而深度是顧問引文之排序鍵。
    # 現行語義：**無逐 item 證據即 fail**（fail-closed，同 corpus.LICENSE_WHITELIST「未列＝不入」）。
    # 註：KH7 無法比照——`knowhow_kh7_eligibility` 之 schema 無任一 item 級欄位
    #   （eligibility_id/run_id/probe_id/status/reasons/evidence/decided_at/script/note），
    #   逐 item 化須先建其資料模型與評估管線，非本次可為之收緊。
    if depth == 5:
        if not _table_exists(cur, "knowledge_kh4_state"):
            return {"verdict": "fail", "note": "KH5 逐 item 判準之載體表未建"}
        cur.execute(
            "SELECT kh_axis_state FROM knowledge_kh4_state WHERE item_id=%s",
            (item_id,),
        )
        row = cur.fetchone()
        if not row:
            return {"verdict": "fail", "note": "無 kh4_state 列＝無逐 item 軸證據（fail-closed）"}
        if row[0] == "ready":
            return {"verdict": "pass", "note": "kh_axis_state=ready"}
        return {"verdict": "fail", "note": f"kh_axis_state={row[0]}"}

    if depth == 6:
        if not _table_exists(cur, "knowledge_kh4_state"):
            return {"verdict": "fail", "note": "KH6 逐 item 判準之載體表未建"}
        cur.execute(
            "SELECT interaction_state FROM knowledge_kh4_state WHERE item_id=%s",
            (item_id,),
        )
        row = cur.fetchone()
        if not row:
            return {"verdict": "fail", "note": "無 kh4_state 列＝無逐 item 交互證據（fail-closed）"}
        if row[0] == "ready":
            return {"verdict": "pass", "note": "interaction_state=ready"}
        return {"verdict": "fail", "note": f"interaction_state={row[0]}"}

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
    had_state = has_admit_state(cur, "item", str(item_id))
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
            # M-K2：本層本輪**未重評**，只承接既有水印 ⇒ 不得蓋 pass 章（自我背書之綠燈）。
            layer_scores[str(d)] = {
                "verdict": "not_reevaluated",
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

    # D4 再晉升鎖之引擎側配套：曾降級 item 不因 KH8 band=high 自動爬回；
    # 誠實記 held、深度維持原值（無升→trigger 靜默）；再晉升唯 Steward 通行證路徑。
    if depth > before and repromotion_locked(cur, item_id):
        layer_scores["repromote_lock"] = {
            "verdict": "held",
            "note": f"曾重評降級：{before}→{depth} 之再晉升須 Steward 通行證（D4）；本輪維持 {before}",
            "layer": "REPROMOTION_LOCK",
        }
        actions.append({"layer": "repromote", "action": "held_at_floor"})
        depth = before

    # M-K2：層 0 之 not_reevaluated（before>0 之承接）與本輪 pass 同視為 raw 已過 ⇒ 行為不變。
    raw_v = (
        "pass"
        if layer_scores.get("0", {}).get("verdict") in ("pass", "not_reevaluated")
        else "fail"
    )
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
        # BREACH-DRAIN：首評寫入 state 時 after 可能仍=0（標題僅達 KH0）——須計入進度
        "seeded": bool(apply and not had_state),
    }


def list_candidate_item_ids(
    cur,
    *,
    limit: int = 50,
    max_depth_lt: int | None = None,
    min_depth: int | None = None,
) -> list[int]:
    """可理解內容（有原文 **或** 非空 title/title_zh）且 admit_depth ∈ [min_depth, max_depth_lt)。

    預設 ORDER：無 admit_state（KH0 破口）優先，再 depth ASC。  
    A.1／BREACH-DRAIN：若只 JOIN item_text，普遍破口（多為標題件）永遠進不了佇列。
    """
    gate = load_gate(cur)
    cap = gate["max_auto_depth"]
    if max_depth_lt is None:
        max_depth_lt = cap
    lo = int(min_depth) if min_depth is not None else 0
    understand = """(
                EXISTS (SELECT 1 FROM knowledge_item_text x WHERE x.item_id=i.item_id)
                OR NULLIF(BTRIM(i.title), '') IS NOT NULL
                OR NULLIF(BTRIM(i.title_zh), '') IS NOT NULL
              )"""
    if _table_exists(cur, "knowhow_auto_admit_state"):
        cur.execute(
            f"""
            SELECT i.item_id
            FROM knowledge_item i
            LEFT JOIN knowhow_auto_admit_state st
              ON st.target_kind='item' AND st.target_id=i.item_id::text
            WHERE COALESCE(st.admit_depth, 0) >= %s
              AND COALESCE(st.admit_depth, 0) < %s
              AND {understand}
            ORDER BY
              CASE WHEN st.target_id IS NULL THEN 0 ELSE 1 END,
              COALESCE(st.admit_depth, 0) ASC,
              i.item_id
            LIMIT %s
            """,
            (lo, max_depth_lt, limit),
        )
    else:
        if lo > 0:
            return []
        cur.execute(
            f"""
            SELECT i.item_id FROM knowledge_item i
            WHERE {understand}
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
    import inspect as _inspect
    _cand_src = _inspect.getsource(list_candidate_item_ids)
    chk("candidates include title（A.1/BREACH）", "title_zh" in _cand_src)
    chk("candidates prefer no-state breach", "st.target_id IS NULL" in _cand_src)
    chk("candidates not text-only JOIN", "JOIN knowledge_item_text x ON x.item_id=i.item_id\n            LEFT JOIN" not in _cand_src)

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
        "title": None,
        "title_zh": None,
    }
    ev8 = evaluate_layer(_Cur(), 8, snap)
    chk("depth8 表未建→skipped", ev8["verdict"] == "skipped")
    ev9 = evaluate_layer(_Cur(), 9, snap)
    chk("depth9 表未建→skipped", ev9["verdict"] == "skipped")
    ev0 = evaluate_layer(_Cur(), 0, snap)
    chk("depth0 pass with text", ev0["verdict"] == "pass")

    # A.1：憲章普遍 KH0——無原文但有標題／title_zh → pass；皆空 → fail-closed
    ev_title = evaluate_layer(_Cur(), 0, {**snap, "has_text": False, "title": "僅標題亦可理解"})
    chk("depth0 pass with title only (A.1)", ev_title["verdict"] == "pass"
        and ev_title.get("action") == "title_understandable")
    ev_zh = evaluate_layer(_Cur(), 0, {**snap, "has_text": False, "title": "  ", "title_zh": "中文題"})
    chk("depth0 pass with title_zh only (A.1)", ev_zh["verdict"] == "pass")
    ev_empty = evaluate_layer(_Cur(), 0, {**snap, "has_text": False, "title": None, "title_zh": ""})
    chk("depth0 fail when empty (A.1 fail-closed)", ev_empty["verdict"] == "fail"
        and ev_empty.get("action") == "kh0_empty")
    # global_title_kh1：無原文、無 qual 表（_Cur to_regclass→None）時標題仍過 KH1
    ev1_title = evaluate_layer(_Cur(), 1, {**snap, "has_text": False, "title": "僅標題過 KH1"})
    chk("depth1 pass with title only (global_title_kh1)", ev1_title["verdict"] == "pass"
        and ev1_title.get("action") == "kh1_title_understandable")
    ev1_empty = evaluate_layer(_Cur(), 1, {**snap, "has_text": False, "title": None, "title_zh": ""})
    chk("depth1 fail when empty", ev1_empty["verdict"] == "fail")
    chk("_title_nonzero strips", _title_nonzero({"title": "  x  "}) == "x")
    chk("_title_nonzero empty", _title_nonzero({"title": " ", "title_zh": None}) is None)
    from types import SimpleNamespace as S

    cites = [
        S(item_id=1, score=0.9, sent_id=10),   # depth 3 shallow
        S(item_id=2, score=0.5, sent_id=20),   # depth 9 deep
        S(item_id=3, score=0.8, sent_id=30),   # depth 7 deep
        S(work_title="論語", score=0.99),      # works — no item_id
        S(item_id=4, score=0.95, sent_id=40),  # depth 8 deep, high score
    ]
    depths = {1: 3, 2: 9, 3: 7, 4: 8}
    # D2：深度優先繫於 KH8 鑑別力閘（live 現況閘關）——selftest 免 DB，閘裁決以快取顯式灌入
    import time as _t

    _kh_evidence_valid_cache.clear()
    _kh_evidence_valid_cache.update({"ok": True, "_at": _t.monotonic()})
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

    # D2：資料為據之閘關（ok=False）→ 不套深度優先、退回相似度原序（fail-closed）
    _kh_evidence_valid_cache.clear()
    _kh_evidence_valid_cache.update({"ok": False, "_at": _t.monotonic()})
    chk("閘關→退回相似度原序",
        [getattr(c, "item_id", None) for c in rank_item_citations(cites, depths)]
        == [1, 2, 3, None, 4])
    # D2 TTL 政策：資料為據之 fail＝長 TTL（30s<age<900s 仍用快取、不每 30s 重掃全表）
    _kh_evidence_valid_cache.clear()
    _kh_evidence_valid_cache.update(
        {"ok": False, "note": "sentinel-d2-data-fail", "_at": _t.monotonic() - 60.0})
    chk("資料為據之 fail 用長 TTL（60s 仍取快取）",
        kh_evidence_valid().get("note") == "sentinel-d2-data-fail")
    # error fail-closed（error_closed=True）＝短 TTL：60s 已過期、須重取（sentinel 不得沿用）
    _kh_evidence_valid_cache.clear()
    _kh_evidence_valid_cache.update(
        {"ok": False, "error_closed": True, "note": "sentinel-d2-err", "_at": _t.monotonic() - 60.0})
    chk("error fail-closed 用短 TTL（60s 過期重取）",
        kh_evidence_valid().get("note") != "sentinel-d2-err")
    _kh_evidence_valid_cache.clear()

    # ── D4 再晉升鎖（2026-08-01）：謂詞＝sqlite 真表 fixture（真 SQL 打真資料列，
    #    謂詞方向反了會紅）＋ progressive_item wiring 紅綠
    import sqlite3

    class _LedgerCur:
        """sqlite 真表 fixture：repromotion_locked 之真 SQL 對真列執行（#35(1)）；to_regclass 攔截。"""

        def __init__(self, table_in: bool, rows: list[tuple[int, int, int]]):
            self._table_in = table_in
            self._db = sqlite3.connect(":memory:")
            self._db.execute(
                "CREATE TABLE knowhow_depth_reevaluation "
                "(item_id INTEGER, depth_before INTEGER, depth_after INTEGER)")
            self._db.executemany(
                "INSERT INTO knowhow_depth_reevaluation VALUES (?,?,?)", rows)
            self.calls: list = []
            self._last = None

        def execute(self, sql, params=None):
            self.calls.append((str(sql), params))
            if "to_regclass" in str(sql):
                self._last = ("knowhow_depth_reevaluation",) if self._table_in else (None,)
                return
            self._last = self._db.execute(str(sql).replace("%s", "?"), params or ()).fetchone()

        def fetchone(self):
            return self._last

    _rc_absent = _LedgerCur(False, [(277948, 9, 7)])
    chk("D4 謂詞:帳表不存在→False（不掃、trigger 為最終防線）",
        repromotion_locked(_rc_absent, 277948) is False and len(_rc_absent.calls) == 1)
    _rc_demoted = _LedgerCur(True, [(277948, 9, 7)])
    chk("D4 謂詞:降級列（9→7）在帳→True 且收到 item 參數",
        repromotion_locked(_rc_demoted, 277948) is True
        and _rc_demoted.calls[-1][1] == (277948,))
    chk("D4 謂詞:僅再晉升列（7→9）→False（自動留帳不回饋污染謂詞）",
        repromotion_locked(_LedgerCur(True, [(277948, 7, 9)]), 277948) is False)
    chk("D4 謂詞:他 item 之降級不波及→False",
        repromotion_locked(_LedgerCur(True, [(999, 9, 7)]), 277948) is False)

    import augur.knowledge.auto_admit as _self
    _orig = (_self.load_gate, _self._item_snapshot, _self.get_admit_depth,
             _self.has_admit_state, _self.evaluate_layer, _self.repromotion_locked)
    _lock_calls: list = []
    try:
        _self.load_gate = lambda cur: {
            "enabled": True, "raw_floor_enabled": True, "progressive_enabled": True,
            "max_auto_depth": 9, "require_kh8": True, "require_kh9": True}
        _self._item_snapshot = lambda cur, iid: dict(snap, item_id=iid, source_key=None)
        _self.get_admit_depth = lambda cur, k, i: 7
        _self.has_admit_state = lambda cur, k, i: True
        _self.evaluate_layer = lambda cur, d, s: {"verdict": "pass", "note": "fixture"}
        _self.repromotion_locked = lambda cur, iid: _lock_calls.append(iid) or True
        r = _self.progressive_item(None, 277948, up_to=9, apply=False)
        chk("D4 clamp:曾降級 7→9 被壓回 7（dry-run 亦 clamp）",
            r["admit_depth_before"] == 7 and r["admit_depth_after"] == 7)
        chk("D4 clamp:誠實留痕 repromote_lock=held ＋ held_at_floor action",
            r["layer_scores"].get("repromote_lock", {}).get("verdict") == "held"
            and {"layer": "repromote", "action": "held_at_floor"} in r["actions"])
        _self.repromotion_locked = lambda cur, iid: False
        r2 = _self.progressive_item(None, 277948, up_to=9, apply=False)
        chk("D4 clamp:未曾降級照升 7→9、零 held 標記",
            r2["admit_depth_after"] == 9 and "repromote_lock" not in r2["layer_scores"])
        # M-K2：d<before 之承接層一律記 not_reevaluated，絕不得出現 prior_depth×pass
        chk("M-K2:承接層記 not_reevaluated、零 prior_depth 蓋 pass",
            r2["layer_scores"]["0"]["verdict"] == "not_reevaluated"
            and r2["layer_scores"]["6"]["note"] == "prior_depth"
            and all(v.get("verdict") != "pass"
                    for v in r2["layer_scores"].values()
                    if isinstance(v, dict) and v.get("note") == "prior_depth"))
        _lock_calls.clear()
        _self.repromotion_locked = lambda cur, iid: _lock_calls.append(iid) or True
        _self.evaluate_layer = lambda cur, d, s: (
            {"verdict": "pass", "note": "fixture"} if d < 8
            else {"verdict": "fail", "note": "fixture"})
        r3 = _self.progressive_item(None, 277948, up_to=9, apply=False)
        chk("D4 clamp:無升深不觸鎖（謂詞零呼叫＝零成本）",
            r3["admit_depth_after"] == 7 and not _lock_calls
            and "repromote_lock" not in r3["layer_scores"])
        chk("seeded False when had_state", r3.get("seeded") is False)
    finally:
        (_self.load_gate, _self._item_snapshot, _self.get_admit_depth,
         _self.has_admit_state, _self.evaluate_layer, _self.repromotion_locked) = _orig

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
