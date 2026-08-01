#!/usr/bin/env python
"""PME-XDOM-AI-PREDICT S1 — AI×預測模型進化文獻橋策展（investment 假說鏈；禁 AI 生成）。

🎯 這支在做什麼（白話）：把 AI／統計學習／金融 ML 可證偽方法論概念，人撰成
   investment school `ml_predict_evolution` 的 principle＋principle_factor_map（庫內已有
   feature），可選 principle_domain_map 應用注記（domain＝ai_ml；**非**量化資格）。
   provenance JSONB 標 xdom_loop=ai_predict。冪等；不手改 validated_*；不灌 ERP／RKI／embedding。

守 #1 #15 #29；憲章 v1.47.0 跨域映射／禁 ai_generated；GATE-keep／FZ-keep／NHC-keep；
計畫 PME-XDOM-AI-PREDICT §2 S1。

執行指令矩陣:
  python scripts/curate_pme_xdom_ai_predict_map.py              # dry-run 印將寫列
  python scripts/curate_pme_xdom_ai_predict_map.py --apply      # 寫入 DB
  python scripts/curate_pme_xdom_ai_predict_map.py --selftest   # 免 DB
"""
from __future__ import annotations

import argparse
import json
import sys

import _bootstrap  # noqa: F401

PROVENANCE = {
    "xdom_loop": "ai_predict",
    "curate": "pme_xdom_ai_predict_s1",
    "plan": "augur_pme_xdom_ai_predict_plan_20260728",
}

# 人撰 SEED：citation 須可核；source_type≠ai_generated。禁把 RKI／顧問命中當 citation。
SCHOOL = {
    "name": "ml_predict_evolution",
    "name_zh": "AI／預測模型進化（方法論橋）",
    "core_thesis": (
        "以可證偽之統計學習／金融 ML 方法論概念（OOS、正則、集成、迭代回饋、"
        "第一性拆解）作為投資預測假說骨架；市場閘裁決生死，非權威說了算。"
    ),
    "proponents": (
        "Hastie/Tibshirani/Friedman; López de Prado; Dietterich; Kuhn/Johnson"
    ),
    "domain": "investment",
}

SOURCES = [
    (
        "Hastie, Tibshirani & Friedman, The Elements of Statistical Learning, "
        "Springer, 2nd ed., 2009",
        "book",
    ),
    (
        "Marcos López de Prado, Advances in Financial Machine Learning, Wiley, 2018",
        "book",
    ),
    (
        "Thomas G. Dietterich, Ensemble Methods in Machine Learning, "
        "in Multiple Classifier Systems, Springer, 2000",
        "paper",
    ),
    (
        "Max Kuhn & Kjell Johnson, Applied Predictive Modeling, Springer, 2013",
        "book",
    ),
]

PRINCIPLES = [
    {
        "statement": (
            "樣本外／偏差—變異數紀律（ESL；AFML purged CV 精神）——"
            "預測模型應偏愛低噪、振幅受控之觀測代理，避免把短窗噪音當訊號。"
        ),
        "hypothesis": (
            "volatility_60d／range_mean_20d 越低 → 未來報酬假說越偏正向"
            "（負向 IC；低噪代理）。"
        ),
        "factors": [
            ("volatility_60d", -1),
            ("range_mean_20d", -1),
        ],
        "domain_notes": [
            {
                "domain": "ai_ml",
                "note_kind": "human_authored",
                "application_note": (
                    "將 OOS／低噪訓練紀律對映為市場振幅與波動代理；"
                    "本注記非 G-PROM 資格憑據。"
                ),
                "citation": (
                    "Hastie et al., ESL, 2009; López de Prado, AFML, 2018"
                ),
                "source_type": "book",
            }
        ],
    },
    {
        "statement": (
            "正則化／奧卡姆剃刀（ESL；Applied Predictive Modeling）——"
            "較簡之財務品質訊號優於過度參數化之投資假說。"
        ),
        "hypothesis": (
            "debt_ratio 越低、roe 越高 → 風險調整後報酬假說（debt−／roe＋）。"
        ),
        "factors": [
            ("debt_ratio", -1),
            ("roe", 1),
        ],
        "domain_notes": [
            {
                "domain": "ai_ml",
                "note_kind": "human_authored",
                "application_note": (
                    "將正則／簡約對映為槓桿與資本報酬品質代理；注記軸＝ai_ml。"
                ),
                "citation": (
                    "Hastie et al., ESL, 2009; Kuhn & Johnson, "
                    "Applied Predictive Modeling, 2013"
                ),
                "source_type": "book",
            }
        ],
    },
    {
        "statement": (
            "集成多樣性（Dietterich 2000）——"
            "多資訊源籌碼代理作為弱學習器多樣之投資假說。"
        ),
        "hypothesis": (
            "institutional_net_buy_ratio_20d／foreign_holding_pct 越高 "
            "→ 未來報酬越高（正向；多源資訊集成）。"
        ),
        "factors": [
            ("institutional_net_buy_ratio_20d", 1),
            ("foreign_holding_pct", 1),
        ],
        "domain_notes": [
            {
                "domain": "ai_ml",
                "note_kind": "human_authored",
                "application_note": (
                    "將 ensemble diversity 對映為機構／外資籌碼多源；非資格捷徑。"
                ),
                "citation": (
                    "Dietterich, Ensemble Methods in Machine Learning, MCS 2000"
                ),
                "source_type": "paper",
            }
        ],
    },
    {
        "statement": (
            "迭代回饋／誤差修正（線上學習精神；AFML 再驗）——"
            "極端位置後之均值回歸代理「錯誤修正」迴路。"
        ),
        "hypothesis": (
            "range_position_120d 越低、days_since_high_252d 越高 "
            "→ 未來報酬假說（位置−／距高＋）。"
        ),
        "factors": [
            ("range_position_120d", -1),
            ("days_since_high_252d", 1),
        ],
        "domain_notes": [],
    },
    {
        "statement": (
            "第一性拆解為可觀測基本面（特徵工程紀律）——"
            "估值與成長基本量為可拆解假說骨架，非黑箱相關。"
        ),
        "hypothesis": (
            "pe_ratio 越低、monthly_revenue_yoy 越高 → 未來報酬假說（pe−／yoy＋）。"
        ),
        "factors": [
            ("pe_ratio", -1),
            ("monthly_revenue_yoy", 1),
        ],
        "domain_notes": [
            {
                "domain": "ai_ml",
                "note_kind": "human_authored",
                "application_note": (
                    "將第一性拆解對映為可觀測估值／營收成長；量化仍經 investment map。"
                ),
                "citation": (
                    "Hastie et al., ESL, 2009; López de Prado, AFML, 2018"
                ),
                "source_type": "book",
            }
        ],
    },
]

REJECTED_UNMAPPABLE = [
    "erp_dump_any",
    "rki_probe_hit_rate",
    "knowledge_embedding_as_feature",
    "ai_generated_principle",
    "solar_slurry_process",
    "model_registry_row_as_feature",
]


def _selftest() -> int:
    ok = True

    def chk(name: str, cond: bool) -> None:
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    feats: list[str] = []
    chk("school domain investment", SCHOOL["domain"] == "investment")
    chk("school name ml_predict_evolution", SCHOOL["name"] == "ml_predict_evolution")
    chk("provenance xdom_loop", PROVENANCE.get("xdom_loop") == "ai_predict")
    for cit, st in SOURCES:
        chk(f"no ai_generated src ({cit[:28]})", st != "ai_generated")
        chk("citation non-empty", bool(cit.strip()))
    for pr in PRINCIPLES:
        chk("statement non-empty", bool(pr["statement"].strip()))
        chk("hypothesis non-empty", bool(pr["hypothesis"].strip()))
        for f, d in pr["factors"]:
            feats.append(f)
            chk(f"dir±1 {f}", d in (-1, 1))
            chk(f"not rejected token {f}", f not in REJECTED_UNMAPPABLE)
        for note in pr.get("domain_notes") or []:
            chk("note_kind closed", note["note_kind"] in ("verbatim_quote", "human_authored"))
            chk("note no ai_generated", note["source_type"] != "ai_generated")
            chk("note citation", bool(note["citation"].strip()))
            chk("domain=ai_ml note axis", note["domain"] == "ai_ml")
    chk("n principles ≥3", len(PRINCIPLES) >= 3)
    chk("n factors ≥5", len(feats) >= 5)
    chk("erp rejected", "erp_dump_any" in REJECTED_UNMAPPABLE)
    chk("rki rejected", "rki_probe_hit_rate" in REJECTED_UNMAPPABLE)
    chk("embedding rejected", "knowledge_embedding_as_feature" in REJECTED_UNMAPPABLE)
    src = open(__file__, encoding="utf-8").read()
    apply_body = src.split("def apply_seed")[1].split("\ndef main")[0]
    map_loop = apply_body.split('for f, d in pr["factors"]')[1].split("for note in")[0]
    chk("I8 map loop ignores domain_map", "principle_domain_map" not in map_loop)
    chk(
        "I8 notes after maps",
        apply_body.index('for f, d in pr["factors"]') < apply_body.index("for note in"),
    )
    # 禁領域專答樹／硬編碼回覆表（字串拆開避免本斷言自撞）
    chk(
        "NHC no hardcode answer tree",
        ("ANSWER" + "_TREE") not in src and ("hardcode" + "_reply") not in src,
    )
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def apply_seed(conn, *, dry_run: bool) -> dict:
    from augur.core import db

    n_src = n_pri = n_map = n_note = 0
    n_school = 0
    new_maps: list[tuple] = []
    prov_json = json.dumps(PROVENANCE, ensure_ascii=False)
    name = SCHOOL["name"]

    with db.transaction(conn) as cur:
        cur.execute("SET LOCAL augur.honesty_write = 'on'")   # 誠實帳本閘通行證(B4)
        cur.execute(
            "SELECT school_id, domain FROM philosophy_school WHERE name=%s",
            (name,),
        )
        row = cur.fetchone()
        if not row:
            if dry_run:
                print(f"  [dry] school ← {name} domain=investment")
                sid = -1
            else:
                cur.execute(
                    "INSERT INTO philosophy_school "
                    "(name, name_zh, core_thesis, proponents, domain) "
                    "VALUES (%s,%s,%s,%s,%s) RETURNING school_id",
                    (
                        name,
                        SCHOOL["name_zh"],
                        SCHOOL["core_thesis"],
                        SCHOOL["proponents"],
                        SCHOOL["domain"],
                    ),
                )
                sid = cur.fetchone()[0]
            n_school = 1
        else:
            sid, domain = row[0], row[1]
            if domain != "investment":
                raise RuntimeError(f"school {name} domain={domain!r} ≠ investment")

        if sid < 0:
            # dry-run without school：仍列印將寫內容
            for cit, st in SOURCES:
                print(f"  [dry] source ← {cit[:70]}")
                n_src += 1
            for pr in PRINCIPLES:
                print(f"  [dry] principle ← {pr['statement'][:56]}")
                n_pri += 1
                for f, d in pr["factors"]:
                    if f in REJECTED_UNMAPPABLE:
                        raise ValueError(f"拒 SEED 不可對映: {f}")
                    print(f"  [dry] map ← {f} dir={d:+d}")
                    new_maps.append((name, f, d))
                    n_map += 1
                n_note += len(pr.get("domain_notes") or [])
            return {
                "school": name,
                "school_new": n_school,
                "sources_new": n_src,
                "principles_new": n_pri,
                "maps_new": n_map,
                "domain_notes_new": n_note,
                "new_map_pairs": new_maps,
                "rejected": list(REJECTED_UNMAPPABLE),
                "provenance": PROVENANCE,
                "dry_run": dry_run,
            }

        for cit, st in SOURCES:
            if st == "ai_generated":
                raise ValueError(f"禁 ai_generated: {cit}")
            cur.execute(
                "SELECT 1 FROM philosophy_source WHERE school_id=%s AND citation=%s",
                (sid, cit),
            )
            if not cur.fetchone():
                if dry_run:
                    print(f"  [dry] source ← {cit[:70]}")
                else:
                    cur.execute(
                        "INSERT INTO philosophy_source (school_id, citation, source_type) "
                        "VALUES (%s,%s,%s)",
                        (sid, cit, st),
                    )
                n_src += 1

        for pr in PRINCIPLES:
            cur.execute(
                "SELECT principle_id FROM philosophy_principle "
                "WHERE school_id=%s AND statement=%s",
                (sid, pr["statement"]),
            )
            prow = cur.fetchone()
            if prow:
                pid = prow[0]
                if not dry_run:
                    cur.execute(
                        "UPDATE philosophy_principle SET hypothesis=%s WHERE principle_id=%s",
                        (pr["hypothesis"], pid),
                    )
            else:
                if dry_run:
                    print(f"  [dry] principle ← {pr['statement'][:56]}")
                    pid = -1
                else:
                    cur.execute(
                        "INSERT INTO philosophy_principle (school_id, statement, hypothesis) "
                        "VALUES (%s,%s,%s) RETURNING principle_id",
                        (sid, pr["statement"], pr["hypothesis"]),
                    )
                    pid = cur.fetchone()[0]
                n_pri += 1

            for f, d in pr["factors"]:
                if f in REJECTED_UNMAPPABLE:
                    raise ValueError(f"拒 SEED 不可對映: {f}")
                if pid < 0:
                    new_maps.append((name, f, d))
                    n_map += 1
                    continue
                cur.execute(
                    "SELECT 1 FROM feature_values WHERE feature=%s LIMIT 1",
                    (f,),
                )
                if not cur.fetchone():
                    raise ValueError(f"feature 庫內無序列，拒 SEED: {f}")
                cur.execute(
                    "SELECT map_id FROM principle_factor_map "
                    "WHERE principle_id=%s AND feature=%s",
                    (pid, f),
                )
                mrow = cur.fetchone()
                if mrow:
                    if not dry_run:
                        cur.execute(
                            "UPDATE principle_factor_map SET direction=%s, "
                            "provenance=COALESCE(provenance,'{}'::jsonb) || %s::jsonb "
                            "WHERE map_id=%s",
                            (d, prov_json, mrow[0]),
                        )
                else:
                    if dry_run:
                        print(f"  [dry] map ← {f} dir={d:+d}")
                    else:
                        cur.execute(
                            "INSERT INTO principle_factor_map "
                            "(principle_id, feature, direction, provenance) "
                            "VALUES (%s,%s,%s,%s::jsonb)",
                            (pid, f, d, prov_json),
                        )
                    new_maps.append((name, f, d))
                    n_map += 1

            if pid < 0:
                n_note += len(pr.get("domain_notes") or [])
                continue
            for note in pr.get("domain_notes") or []:
                if note["source_type"] == "ai_generated":
                    raise ValueError("禁 ai_generated domain note")
                if note["note_kind"] not in ("verbatim_quote", "human_authored"):
                    raise ValueError(f"bad note_kind: {note['note_kind']}")
                cur.execute(
                    "SELECT map_id FROM principle_domain_map "
                    "WHERE principle_id=%s AND domain=%s",
                    (pid, note["domain"]),
                )
                nrow = cur.fetchone()
                if nrow:
                    if not dry_run:
                        cur.execute(
                            "UPDATE principle_domain_map SET note_kind=%s, application_note=%s, "
                            "citation=%s, source_type=%s WHERE map_id=%s",
                            (
                                note["note_kind"],
                                note["application_note"],
                                note["citation"],
                                note["source_type"],
                                nrow[0],
                            ),
                        )
                else:
                    if dry_run:
                        print(
                            f"  [dry] domain_note ← {note['domain']} "
                            f"kind={note['note_kind']}"
                        )
                    else:
                        cur.execute(
                            "INSERT INTO principle_domain_map "
                            "(principle_id, domain, note_kind, application_note, "
                            "citation, source_type) VALUES (%s,%s,%s,%s,%s,%s)",
                            (
                                pid,
                                note["domain"],
                                note["note_kind"],
                                note["application_note"],
                                note["citation"],
                                note["source_type"],
                            ),
                        )
                    n_note += 1

    return {
        "school": name,
        "school_new": n_school,
        "sources_new": n_src,
        "principles_new": n_pri,
        "maps_new": n_map,
        "domain_notes_new": n_note,
        "new_map_pairs": new_maps,
        "rejected": list(REJECTED_UNMAPPABLE),
        "provenance": PROVENANCE,
        "dry_run": dry_run,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="PME-XDOM AI-PREDICT S1 策展")
    ap.add_argument("--apply", action="store_true", help="寫入 DB（預設 dry-run）")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()

    from augur.core import db

    if not db.ping():
        print("SKIP: DB 不可達", file=sys.stderr)
        return 2

    dry = not args.apply
    with db.connect() as conn:
        stats = apply_seed(conn, dry_run=dry)
    print(f"{'DRY-RUN' if dry else 'APPLIED'}: {stats}")
    print(f"rejected (no INSERT): {REJECTED_UNMAPPABLE}")
    if dry:
        print("（加 --apply 才寫入）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
