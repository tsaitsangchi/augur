"""知識入庫強制管線(KIP)編排 — LSR-INGRESS-S1。

🎯 這支在做什麼(白話):對一批 knowledge_item 依序跑切句→長句重切→嵌→
   （可選）Qdrant→KH4→auto_admit≤9，並寫 knowledge_ingress_kip_run 帳。
   三通道（topic_harvest／local_files／sftp）與 manual_cli／backfill 共用同一入口。
守 #12(單一編排)· #15(誠實 partial／skip)· FZ-keep· LSR-INGRESS-PLAN D8·
   不自動 KH10／PME APPLY。

執行指令矩陣:
  python -m augur.knowledge.ingress_kip
  python -m augur.knowledge.ingress_kip --selftest
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

CHANNELS = (
    "topic_harvest",
    "local_files",
    "sftp",
    "manual_cli",
    "backfill",
)

STAGE_ORDER = (
    "sentences",
    "resplit",
    "embed",
    "qdrant",
    "kh4",
    "admit",
)

DEFAULT_MAX_CHARS = 800
DEFAULT_ADMIT_UP_TO = 9
ACTOR_DEFAULT = "system:ingress_kip"

_ROOT = Path(__file__).resolve().parents[3]
_SCRIPTS = _ROOT / "scripts"
_PY = sys.executable


def _table_exists(cur, name: str) -> bool:
    cur.execute("SELECT to_regclass(%s)", (f"public.{name}",))
    return bool(cur.fetchone()[0])


def _json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, default=str)


def resolve_item_ids(
    cur,
    *,
    item_ids: list[int] | None = None,
    job_id: int | None = None,
    source_key: str | None = None,
    domain: str | None = None,
    needs_kip: bool = False,
    limit: int | None = None,
) -> list[int]:
    """解析本批 item_ids（顯式／job／source_key／domain）。"""
    if item_ids:
        ids = [int(x) for x in item_ids]
        if limit is not None:
            ids = ids[:limit]
        return ids
    if job_id is not None:
        if not _table_exists(cur, "knowledge_import_qualification"):
            return []
        cur.execute(
            """
            SELECT DISTINCT item_id
            FROM knowledge_import_qualification
            WHERE job_id=%s AND item_id IS NOT NULL
              AND ingest_status IN ('inserted','duplicate')
            ORDER BY item_id
            """,
            (int(job_id),),
        )
        ids = [r[0] for r in cur.fetchall()]
        if limit is not None:
            ids = ids[:limit]
        return ids

    where = ["EXISTS (SELECT 1 FROM knowledge_item_text t WHERE t.item_id = i.item_id)"]
    params: list[Any] = []
    if source_key:
        where.append("i.source_key = %s")
        params.append(source_key)
    if domain:
        where.append("i.domain = %s")
        params.append(domain)
    if needs_kip:
        # 缺句／缺嵌／KH4 非 eligible／admit_depth < 9 → 待 KIP
        where.append(
            """(
            NOT EXISTS (
              SELECT 1 FROM knowledge_sentence s
              JOIN knowledge_item_text t ON t.itext_id = s.itext_id
              WHERE t.item_id = i.item_id)
            OR EXISTS (
              SELECT 1 FROM knowledge_sentence s
              JOIN knowledge_item_text t ON t.itext_id = s.itext_id
              WHERE t.item_id = i.item_id
                AND NOT EXISTS (
                  SELECT 1 FROM knowledge_sentence_embedding e WHERE e.sent_id = s.sent_id))
            OR NOT EXISTS (
              SELECT 1 FROM knowledge_kh4_state k
              WHERE k.item_id = i.item_id AND k.answer_status = 'eligible')
            OR NOT EXISTS (
              SELECT 1 FROM knowhow_auto_admit_state a
              WHERE a.target_kind = 'item' AND a.target_id = i.item_id::text
                AND a.admit_depth >= 9)
            )"""
        )
    if not source_key and not domain and not needs_kip:
        return []
    if needs_kip and not source_key and not domain:
        # 全域待補（DAG 無 --domain 時）
        pass
    sql = (
        "SELECT i.item_id FROM knowledge_item i WHERE "
        + " AND ".join(where)
        + " ORDER BY i.item_id"
    )
    if limit is not None:
        sql += " LIMIT %s"
        params.append(int(limit))
    cur.execute(sql, params)
    return [r[0] for r in cur.fetchall()]


def record_kip_skipped_explicit(
    *,
    channel: str,
    trigger_ref: str | None,
    item_ids: list[int],
    actor: str = ACTOR_DEFAULT,
) -> int | None:
    """--no-kip 明示跳過：落 kip_run status=skipped_explicit（D9）。"""
    if channel not in CHANNELS:
        raise ValueError(f"channel 須∈{CHANNELS}")
    from augur.core import db

    with db.connect() as conn, conn.cursor() as cur:
        if not _table_exists(cur, "knowledge_ingress_kip_run"):
            return None
        cur.execute(
            """
            INSERT INTO knowledge_ingress_kip_run
              (channel, trigger_ref, item_ids, status, stages_json, actor, finished_at)
            VALUES (%s,%s,%s,'skipped_explicit',%s::jsonb,%s, now())
            RETURNING kip_run_id
            """,
            (
                channel,
                trigger_ref,
                list(item_ids),
                _json({"skipped": "explicit", "note": "--no-kip"}),
                actor,
            ),
        )
        kid = cur.fetchone()[0]
        conn.commit()
        return kid


def run_kip_hook(
    *,
    channel: str,
    item_ids: list[int] | None = None,
    job_id: int | None = None,
    source_key: str | None = None,
    trigger_ref: str | None = None,
    no_kip: bool = False,
    skip_qdrant: bool = True,
    qdrant_url: str | None = None,
    actor: str = ACTOR_DEFAULT,
) -> dict:
    """acquire／admin 收束鉤子：預設跑 KIP；--no-kip 落 skipped_explicit。"""
    from augur.core import db

    with db.connect() as conn, conn.cursor() as cur:
        ids = list(item_ids or [])
        if not ids:
            ids = resolve_item_ids(
                cur, job_id=job_id, source_key=source_key, item_ids=None
            )
    if not ids:
        print("[kip_done] status=done item_n=0 (no items)", flush=True)
        return {"ok": True, "status": "done", "item_n": 0, "kip_run_id": None}

    trig = trigger_ref
    if trig is None:
        if job_id is not None:
            trig = f"job:{job_id}"
        elif source_key:
            trig = f"source:{source_key}"
        else:
            trig = f"items:{len(ids)}"

    if no_kip:
        kid = record_kip_skipped_explicit(
            channel=channel, trigger_ref=trig, item_ids=ids, actor=actor
        )
        print(
            f"[kip_skip] explicit kip_run_id={kid} item_n={len(ids)} trigger={trig}",
            flush=True,
        )
        return {
            "ok": True,
            "status": "skipped_explicit",
            "kip_run_id": kid,
            "item_n": len(ids),
        }

    print(f"[kip_start] channel={channel} item_n={len(ids)} trigger={trig}", flush=True)
    result = run_kip_for_items(
        ids,
        channel=channel,
        trigger_ref=trig,
        apply=True,
        dry_run=False,
        skip_qdrant=skip_qdrant,
        qdrant_url=qdrant_url,
        actor=actor,
    )
    print(
        f"[kip_done] status={result.get('status')} kip_run_id={result.get('kip_run_id')} "
        f"item_n={result.get('item_n')} ok={result.get('ok')}",
        flush=True,
    )
    return result


def itext_ids_for_items(cur, item_ids: list[int]) -> list[int]:
    if not item_ids:
        return []
    cur.execute(
        """
        SELECT itext_id FROM knowledge_item_text
        WHERE item_id = ANY(%s)
        ORDER BY itext_id
        """,
        (list(item_ids),),
    )
    return [r[0] for r in cur.fetchall()]


def _run_script(args: list[str], *, timeout: int | None = None) -> dict:
    t0 = time.time()
    env = os.environ.copy()
    try:
        proc = subprocess.run(
            [_PY, str(_SCRIPTS / args[0]), *args[1:]],
            cwd=str(_ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
        out = (proc.stdout or "")[-4000:]
        err = (proc.stderr or "")[-2000:]
        return {
            "ok": proc.returncode == 0,
            "rc": proc.returncode,
            "elapsed_s": round(time.time() - t0, 2),
            "stdout_tail": out,
            "stderr_tail": err,
        }
    except subprocess.TimeoutExpired as e:
        return {
            "ok": False,
            "rc": -1,
            "elapsed_s": round(time.time() - t0, 2),
            "error": f"timeout:{e}",
        }
    except Exception as e:
        return {
            "ok": False,
            "rc": -1,
            "elapsed_s": round(time.time() - t0, 2),
            "error": str(e),
        }


def stage_sentences(item_ids: list[int], *, max_chars: int, dry_run: bool) -> dict:
    """KIP-1: build_sentences items（resume=僅缺句段；帶 max_chars）。"""
    info: dict[str, Any] = {
        "stage": "sentences",
        "item_n": len(item_ids),
        "max_chars": max_chars,
    }
    if dry_run:
        info["dry_run"] = True
        info["ok"] = True
        info["cmd"] = (
            f"build_sentences.py --scope items --max-chars {max_chars}"
        )
        return info
    # 全庫 resume：僅尚未有句之 itext；本批入庫後通常恰為本批
    r = _run_script(
        ["build_sentences.py", "--scope", "items", "--max-chars", str(max_chars)],
        timeout=3600,
    )
    info.update(r)
    return info


def stage_resplit(item_ids: list[int], *, max_chars: int, dry_run: bool) -> dict:
    """KIP-2: 本批 itext 若仍有超長句則硬切。"""
    from augur.core import db

    info: dict[str, Any] = {"stage": "resplit", "max_chars": max_chars}
    with db.connect() as conn, conn.cursor() as cur:
        itexts = itext_ids_for_items(cur, item_ids)
        info["itext_n"] = len(itexts)
        if not itexts:
            info["ok"] = True
            info["skipped"] = "no_itext"
            return info
        cur.execute(
            """
            SELECT DISTINCT s.itext_id
            FROM knowledge_sentence s
            WHERE s.itext_id = ANY(%s) AND length(s.sentence) > %s
            """,
            (itexts, max_chars),
        )
        long_parents = [r[0] for r in cur.fetchall()]
    info["long_parents"] = len(long_parents)
    if dry_run:
        info["dry_run"] = True
        info["ok"] = True
        return info
    if not long_parents:
        info["ok"] = True
        info["skipped"] = "no_long"
        return info

    # 逐 parent 呼叫既有 CLI（#12 重切邏輯住 resplit_long_sentences）
    applied = 0
    fails = []
    for pid in long_parents:
        r = _run_script(
            [
                "resplit_long_sentences.py",
                "--apply",
                "--side",
                "items",
                "--max-chars",
                str(max_chars),
                "--itext-id",
                str(pid),
                "--note",
                "LSR-INGRESS-KIP",
            ],
            timeout=600,
        )
        if r.get("ok"):
            applied += 1
        else:
            fails.append({"itext_id": pid, **{k: r[k] for k in ("rc", "error") if k in r}})
    info["applied"] = applied
    info["fail_n"] = len(fails)
    if fails:
        info["fails_sample"] = fails[:5]
    info["ok"] = len(fails) == 0
    return info


def stage_embed(item_ids: list[int], *, dry_run: bool, languages: tuple[str, ...] = ("zh", "en")) -> dict:
    """KIP-3: 本批句 gap-fill 嵌入（scoped；不掃全庫尾債）。"""
    info: dict[str, Any] = {"stage": "embed", "languages": list(languages)}
    if dry_run:
        info["dry_run"] = True
        info["ok"] = True
        info["note"] = "scoped gap-fill for item sentences"
        return info

    from augur.core import db
    from augur.knowledge import corpus, embedspec

    # 延遲載入 scripts/embed_knowledge 之 is_junk／load_model（單一 junk 定義）
    import importlib.util

    scripts_s = str(_SCRIPTS)
    if scripts_s not in sys.path:
        sys.path.insert(0, scripts_s)
    emb_path = _SCRIPTS / "embed_knowledge.py"
    spec = importlib.util.spec_from_file_location("_kip_embed_knowledge", emb_path)
    if spec is None or spec.loader is None:
        return {"stage": "embed", "ok": False, "error": "cannot_load_embed_knowledge"}
    mod = importlib.util.module_from_spec(spec)
    # 避免執行 main：只 exec 模組頂層（會定義函式；main 僅在 __name__）
    spec.loader.exec_module(mod)
    is_junk = mod.is_junk
    load_model = mod.load_model
    PASSAGE_PREFIX = mod.PASSAGE_PREFIX
    resolve_write_target = mod.resolve_write_target
    check_dim = mod.check_dim
    precheck = mod.precheck

    model_tag = embedspec.MODEL_TAG
    dim = embedspec.dim_for(model_tag)
    model = None
    totals = {"processed": 0, "embedded": 0, "junk": 0}

    with db.connect() as conn:
        with db.transaction(conn) as cur:
            precheck(cur, need_ledger=True)
            check_dim(cur, "knowledge_sentence_embedding", dim)
            conflict_cols = resolve_write_target(
                cur, "knowledge_sentence_embedding", "sent_id", model_tag
            )
            item_clean, _ = corpus.clean_item_sql("i", "x", is_super=True)
            cur.execute(
                f"""
                SELECT s.sent_id, s.sentence, s.language
                FROM knowledge_sentence s
                JOIN knowledge_item_text x ON x.itext_id = s.itext_id
                JOIN knowledge_item i ON i.item_id = x.item_id
                WHERE x.item_id = ANY(%s)
                  AND {item_clean}
                  AND NOT EXISTS (
                    SELECT 1 FROM knowledge_sentence_embedding e WHERE e.sent_id = s.sent_id)
                ORDER BY s.sent_id
                """,
                (list(item_ids),),
            )
            rows = cur.fetchall()

        by_lang: dict[str, list] = {lang: [] for lang in languages}
        for sent_id, sentence, lang in rows:
            lang = lang or "en"
            if lang not in by_lang:
                continue
            by_lang[lang].append((sent_id, sentence))

        for lang, batch in by_lang.items():
            if not batch:
                continue
            keep = [(i, tx) for i, tx in batch if not is_junk(tx, lang)]
            junk_n = len(batch) - len(keep)
            totals["processed"] += len(batch)
            totals["junk"] += junk_n
            if not keep:
                continue
            texts = [
                tx if tx.startswith(PASSAGE_PREFIX) else f"{PASSAGE_PREFIX}{tx}"
                for _, tx in keep
            ]
            if model is None:
                model = load_model(model_tag)
            vecs = model.encode(
                texts, batch_size=64, normalize_embeddings=True, show_progress_bar=False
            )
            inserted = 0
            with db.transaction(conn) as cur:
                for (rid, _), v in zip(keep, vecs):
                    cur.execute(
                        f"INSERT INTO knowledge_sentence_embedding "
                        f"(sent_id, embedding, model_tag) VALUES (%s,%s,%s) "
                        f"ON CONFLICT ({conflict_cols}) DO NOTHING",
                        (rid, list(map(float, v)), model_tag),
                    )
                    inserted += cur.rowcount
            totals["embedded"] += inserted

        with db.transaction(conn) as cur:
            cur.execute(
                "INSERT INTO knowledge_embed_ledger "
                "(scope, model_tag, processed, embedded, junk_excluded, note) "
                "VALUES (%s,%s,%s,%s,%s,%s)",
                (
                    "kip_embed_items_scoped",
                    model_tag,
                    totals["processed"],
                    totals["embedded"],
                    totals["junk"],
                    f"LSR-INGRESS items={len(item_ids)}",
                ),
            )

    info["ok"] = True
    info.update(totals)
    return info


def stage_qdrant(
    item_ids: list[int],
    *,
    dry_run: bool,
    qdrant_url: str | None,
    skip_qdrant: bool,
) -> dict:
    """KIP-4: 公開 CLEAN 匯出；無 url／明示 skip／全 private → 誠實跳過。"""
    info: dict[str, Any] = {"stage": "qdrant"}
    if skip_qdrant:
        info["ok"] = True
        info["skipped"] = "explicit"
        return info
    if not qdrant_url:
        info["ok"] = True
        info["skipped"] = "no_url"
        return info

    from augur.core import db

    with db.connect() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT count(*) FILTER (WHERE COALESCE(t.access_scope,'public') = 'local_private'),
                   count(*)
            FROM knowledge_item_text t
            WHERE t.item_id = ANY(%s)
            """,
            (list(item_ids),),
        )
        priv, total = cur.fetchone()
    if total and priv == total:
        info["ok"] = True
        info["skipped"] = "all_local_private"
        return info

    if dry_run:
        info["dry_run"] = True
        info["ok"] = True
        info["url"] = qdrant_url
        return info

    # 增量匯出全側（既有 CLI 無 item 濾；帳內註明 kip batch）
    results = {}
    for lang in ("zh", "en"):
        r = _run_script(
            [
                "export_qdrant_index.py",
                "--side",
                "items",
                "--language",
                lang,
                "--url",
                qdrant_url,
            ],
            timeout=7200,
        )
        results[lang] = {"ok": r.get("ok"), "rc": r.get("rc"), "elapsed_s": r.get("elapsed_s")}
    info["langs"] = results
    info["ok"] = all(v.get("ok") for v in results.values())
    return info


def stage_kh4(item_ids: list[int], *, dry_run: bool) -> dict:
    """KIP-5: kh4.refresh_items。"""
    info: dict[str, Any] = {"stage": "kh4", "item_n": len(item_ids)}
    if dry_run:
        info["dry_run"] = True
        info["ok"] = True
        return info
    from augur.core import db
    from augur.knowledge import kh4

    with db.connect() as conn, conn.cursor() as cur:
        n = kh4.refresh_items(cur, item_ids=item_ids)
        conn.commit()
        cur.execute(
            """
            SELECT answer_status, count(*)
            FROM knowledge_kh4_state
            WHERE item_id = ANY(%s)
            GROUP BY 1 ORDER BY 2 DESC
            """,
            (list(item_ids),),
        )
        info["answer_status"] = {r[0]: r[1] for r in cur.fetchall()}
    info["refreshed"] = n
    info["ok"] = True
    return info


def stage_admit(item_ids: list[int], *, dry_run: bool, up_to: int = DEFAULT_ADMIT_UP_TO) -> dict:
    """KIP-6: progressive admit 至 max_auto_depth（預設夾 9；不碰 KH10）。"""
    info: dict[str, Any] = {"stage": "admit", "item_n": len(item_ids), "up_to": up_to}
    if dry_run:
        info["dry_run"] = True
        info["ok"] = True
        return info
    from augur.core import db
    from augur.knowledge import auto_admit as aa

    advanced = 0
    depths: dict[int, int] = {}
    with db.connect() as conn, conn.cursor() as cur:
        gate = aa.load_gate(cur)
        cap = min(int(up_to), int(gate["max_auto_depth"]))
        info["cap"] = cap
        info["gate_enabled"] = gate["enabled"] and gate["progressive_enabled"]
        if not info["gate_enabled"]:
            info["ok"] = True
            info["skipped"] = "gate_disabled"
            return info
        for iid in item_ids:
            r = aa.progressive_item(
                cur, iid, up_to=cap, apply=True, activate_source=True
            )
            if r.get("ok") and r.get("admit_depth_after", -1) > r.get("admit_depth_before", -1):
                advanced += 1
            if r.get("ok"):
                d = int(r.get("admit_depth_after", 0))
                depths[d] = depths.get(d, 0) + 1
        conn.commit()
    info["advanced"] = advanced
    info["depth_hist"] = {str(k): v for k, v in sorted(depths.items())}
    info["ok"] = True
    return info


def _open_kip_run(
    cur,
    *,
    channel: str,
    trigger_ref: str | None,
    item_ids: list[int],
    actor: str,
) -> int:
    cur.execute(
        """
        INSERT INTO knowledge_ingress_kip_run
          (channel, trigger_ref, item_ids, status, stages_json, actor)
        VALUES (%s,%s,%s,'running','{}'::jsonb,%s)
        RETURNING kip_run_id
        """,
        (channel, trigger_ref, list(item_ids), actor),
    )
    return cur.fetchone()[0]


def _finish_kip_run(
    cur,
    kip_run_id: int,
    *,
    status: str,
    stages: dict,
    error_text: str | None = None,
) -> None:
    cur.execute(
        """
        UPDATE knowledge_ingress_kip_run
        SET status=%s, stages_json=%s::jsonb, error_text=%s, finished_at=now()
        WHERE kip_run_id=%s
        """,
        (status, _json(stages), error_text, kip_run_id),
    )


def run_kip_for_items(
    item_ids: list[int],
    *,
    channel: str,
    trigger_ref: str | None = None,
    apply: bool = False,
    dry_run: bool = False,
    max_chars: int = DEFAULT_MAX_CHARS,
    admit_up_to: int = DEFAULT_ADMIT_UP_TO,
    qdrant_url: str | None = None,
    skip_qdrant: bool = False,
    skip_stages: set[str] | None = None,
    until_stage: str | None = None,
    actor: str = ACTOR_DEFAULT,
) -> dict:
    """對一批 item 跑 KIP；寫 kip_run（apply／dry_run 皆可開帳，dry_run 標 stages）。"""
    if channel not in CHANNELS:
        raise ValueError(f"channel 須∈{CHANNELS}，得 {channel!r}")
    if max_chars > 1000:
        raise ValueError("max_chars 禁止 >1000（embed en junk 線）")
    skip_stages = set(skip_stages or ())
    item_ids = [int(x) for x in item_ids]
    if not item_ids:
        return {"ok": False, "error": "empty_item_ids", "status": "failed"}

    from augur.core import db

    stages: dict[str, Any] = {}
    kip_run_id = None
    status = "pending"

    with db.connect() as conn, conn.cursor() as cur:
        if not _table_exists(cur, "knowledge_ingress_kip_run"):
            return {
                "ok": False,
                "error": "kip_run 表未建——先 migrate_knowledge_ingress_kip_ddl.py --apply",
                "status": "failed",
            }
        if apply or dry_run:
            kip_run_id = _open_kip_run(
                cur,
                channel=channel,
                trigger_ref=trigger_ref,
                item_ids=item_ids,
                actor=actor + (":dry_run" if dry_run and not apply else ""),
            )
            conn.commit()

    runners = {
        "sentences": lambda: stage_sentences(
            item_ids, max_chars=max_chars, dry_run=dry_run or not apply
        ),
        "resplit": lambda: stage_resplit(
            item_ids, max_chars=max_chars, dry_run=dry_run or not apply
        ),
        "embed": lambda: stage_embed(item_ids, dry_run=dry_run or not apply),
        "qdrant": lambda: stage_qdrant(
            item_ids,
            dry_run=dry_run or not apply,
            qdrant_url=qdrant_url,
            skip_qdrant=skip_qdrant,
        ),
        "kh4": lambda: stage_kh4(item_ids, dry_run=dry_run or not apply),
        "admit": lambda: stage_admit(
            item_ids, dry_run=dry_run or not apply, up_to=admit_up_to
        ),
    }

    hard_fail = False
    error_text = None
    try:
        for name in STAGE_ORDER:
            if name in skip_stages:
                stages[name] = {"ok": True, "skipped": "explicit"}
                continue
            result = runners[name]()
            stages[name] = result
            if not result.get("ok", False) and not result.get("skipped"):
                hard_fail = True
                error_text = f"stage:{name}"
                break
            if until_stage and name == until_stage:
                break
    except Exception as e:
        hard_fail = True
        error_text = str(e)
        stages["exception"] = {"error": str(e)}

    if dry_run and not apply:
        stages["mode"] = "dry_run"

    benign_skip = {
        "no_long",
        "no_url",
        "all_local_private",
        "explicit",
        "gate_disabled",
        "no_itext",
    }
    if hard_fail:
        status = "failed"
    else:
        key_bad = [
            s
            for s in ("sentences", "resplit", "embed", "kh4", "admit")
            if isinstance(stages.get(s), dict)
            and not stages[s].get("ok", False)
            and not stages[s].get("skipped")
        ]
        if key_bad:
            status = "failed"
            error_text = error_text or f"stages:{key_bad}"
        else:
            odd_skips = [
                s
                for s in STAGE_ORDER
                if isinstance(stages.get(s), dict)
                and stages[s].get("skipped")
                and stages[s]["skipped"] not in benign_skip
            ]
            status = "partial" if odd_skips else "done"

    out = {
        "ok": status in ("done", "partial"),
        "status": status,
        "kip_run_id": kip_run_id,
        "channel": channel,
        "trigger_ref": trigger_ref,
        "item_n": len(item_ids),
        "item_ids_sample": item_ids[:20],
        "stages": stages,
        "error_text": error_text,
    }

    if kip_run_id is not None:
        with db.connect() as conn, conn.cursor() as cur:
            _finish_kip_run(
                cur, kip_run_id, status=status, stages=stages, error_text=error_text
            )
            conn.commit()
    return out


def selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("CHANNELS 含三通道", set(["topic_harvest", "local_files", "sftp"]) <= set(CHANNELS))
    chk("STAGE_ORDER 含 LSR→admit", STAGE_ORDER[:3] == ("sentences", "resplit", "embed"))
    chk("STAGE_ORDER 末=admit", STAGE_ORDER[-1] == "admit")
    chk("無 KH10 自動段", "kh10" not in STAGE_ORDER)
    chk("max_chars 預設 800", DEFAULT_MAX_CHARS == 800)
    chk("admit 預設 ≤9", DEFAULT_ADMIT_UP_TO == 9)
    chk("run_kip_for_items 可呼叫", callable(run_kip_for_items))
    chk("resolve_item_ids 可呼叫", callable(resolve_item_ids))
    chk("run_kip_hook 可呼叫", callable(run_kip_hook))
    chk("record_kip_skipped_explicit 可呼叫", callable(record_kip_skipped_explicit))
    # channel 驗證
    try:
        run_kip_for_items([1], channel="not_a_channel", dry_run=True)
        chk("非法 channel 拒", False)
    except ValueError:
        chk("非法 channel 拒", True)
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def main(argv=None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description="ingress_kip library CLI")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    print(__doc__)
    print("用途: run_kip_for_items(...)；CLI 見 scripts/run_knowledge_ingress_kip.py")
    print("公開: CHANNELS / STAGE_ORDER / resolve_item_ids / run_kip_for_items")
    return 0


if __name__ == "__main__":
    sys.exit(main())
