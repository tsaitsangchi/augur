#!/usr/bin/env python
"""PME-XDOM-SOLAR S1（KH10 橋）— 太陽能供應鏈 investment 假說策展（禁 AI 生成）。

🎯 這支在做什麼（白話）：在既有 investment school `solar_supply_invest` 上追加
   KH10 核准候選（id 2／3／9／18）對應之 principle＋principle_factor_map；
   回寫 governance ledger downstream_ref。不重寫 H1–H6；不灌 ERP／RKI cite 當閘。

守 #1 #15 #29；憲章跨域映射／禁 ai_generated；GATE-keep／FZ-keep／NHC-keep；
計畫 reports/augur_pme_xdom_solar_from_kh10_plan_20260731.md；拍板
audits/PME-XDOM-SOLAR-PLAN-APPROVED-20260731.md。

執行指令矩陣:
  python scripts/curate_pme_xdom_solar_map.py              # dry-run 印將寫列
  python scripts/curate_pme_xdom_solar_map.py --apply      # 寫入 DB＋ledger 回寫
  python scripts/curate_pme_xdom_solar_map.py --selftest   # 免 DB
"""
from __future__ import annotations

import argparse
import json
import sys

import _bootstrap  # noqa: F401

PROVENANCE_BASE = {
    "xdom_loop": "solar",
    "curate": "pme_xdom_solar_kh10_s1",
    "plan": "augur_pme_xdom_solar_from_kh10_plan_20260731",
}

SCHOOL = {
    "name": "solar_supply_invest",
    "name_zh": "太陽能供應鏈投資（概念橋）",
    "core_thesis": (
        "以光電供應鏈／產能週期／成本學習曲線之可證偽概念，橋接為台股可觀測"
        "財務與籌碼假說；市場閘裁決生死，非產業權威說了算。"
    ),
    "proponents": "ITRPV; Fraunhofer ISE; BloombergNEF",
    "domain": "investment",
}

SOURCES = [
    (
        "ITRPV, International Technology Roadmap for Photovoltaic (ITRPV), "
        "14th ed., 2023",
        "report",
    ),
    (
        "Fraunhofer ISE, Photovoltaics Report, "
        "Fraunhofer Institute for Solar Energy Systems, 2024",
        "report",
    ),
    (
        "BloombergNEF, Solar Supply Chain — Module Cost Dynamics and "
        "Manufacturing Capacity, BNEF, 2023",
        "report",
    ),
    (
        "Hastie, Tibshirani & Friedman, The Elements of Statistical Learning, "
        "Springer, 2nd ed., 2009",
        "book",
    ),
    (
        "Marcos López de Prado, Advances in Financial Machine Learning, "
        "Wiley, 2018",
        "book",
    ),
]

# SEED 已簽：plans/PME-XDOM-SOLAR-PLAN-APPROVED；kh10 回寫見 KH10_LEDGER_LINKS
PRINCIPLES = [
    {
        "statement": (
            "第一性拆解 × 可證偽 ML 紀律（ESL／AFML）——"
            "太陽能技術核心假說須落成可觀測估值／成長／低噪代理，禁黑箱專答樹。"
        ),
        "hypothesis": (
            "pe_ratio 越低、monthly_revenue_yoy 越高、volatility_60d 越低 "
            "→ 未來報酬假說（pe−／yoy＋／vol−）。"
        ),
        "factors": [
            ("pe_ratio", -1),
            ("monthly_revenue_yoy", 1),
            ("volatility_60d", -1),
        ],
        "kh10_candidate_ids": [2, 18],
        "domain_notes": [
            {
                "domain": "materials_rd",
                "note_kind": "human_authored",
                "application_note": (
                    "KH10 RKI-FP-AI-SOLAR（id 2／18）橋：第一性＋模型進化→投資代理；"
                    "非 G-PROM 資格憑據。"
                ),
                "citation": (
                    "Hastie et al., ESL, 2009; López de Prado, AFML, 2018; "
                    "ITRPV 2023"
                ),
                "source_type": "book",
            }
        ],
    },
    {
        "statement": (
            "第一性列技術核心 → 品質／財務耐震（ITRPV 良率與成本學習曲線精神）——"
            "核心能力體現於毛利分位與低槓桿。"
        ),
        "hypothesis": (
            "gross_margin_pctile 越高、debt_ratio 越低 "
            "→ 未來報酬假說（margin＋／debt−）。"
        ),
        "factors": [
            ("gross_margin_pctile", 1),
            ("debt_ratio", -1),
        ],
        "kh10_candidate_ids": [3],
        "domain_notes": [
            {
                "domain": "materials_rd",
                "note_kind": "human_authored",
                "application_note": (
                    "KH10 RKI-FP-SOLAR-CORE（id 3）橋：技術核心→毛利／槓桿代理；"
                    "非資格捷徑。"
                ),
                "citation": "ITRPV, 14th ed., 2023; Fraunhofer ISE PV Report, 2024",
                "source_type": "report",
            }
        ],
    },
    {
        "statement": (
            "AI 模型進化強化材料研發 → 供應鏈贏家獲機構／資本效率認可"
            "（BNEF 產業鏈投資流向概念）。"
        ),
        "hypothesis": (
            "institutional_net_buy_ratio_20d 越高、roe 越高 "
            "→ 未來報酬假說（inst＋／roe＋）。"
        ),
        "factors": [
            ("institutional_net_buy_ratio_20d", 1),
            ("roe", 1),
        ],
        "kh10_candidate_ids": [9],
        "domain_notes": [
            {
                "domain": "ai_ml",
                "note_kind": "human_authored",
                "application_note": (
                    "KH10 RKI-AI-SOLAR-RD（id 9）橋：AI×研發→籌碼／ROE；非 cite 率過閘。"
                ),
                "citation": (
                    "BloombergNEF Solar Supply Chain, 2023; "
                    "Dietterich / ESL ensemble spirit via investment proxies"
                ),
                "source_type": "report",
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
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    feats: list[str] = []
    chk("school domain investment", SCHOOL["domain"] == "investment")
    chk("school name solar_supply_invest", SCHOOL["name"] == "solar_supply_invest")
    chk("provenance loop solar", PROVENANCE_BASE.get("xdom_loop") == "solar")
    for cit, st in SOURCES:
        chk(f"no ai_generated src ({cit[:28]})", st != "ai_generated")
        chk("citation non-empty", bool(cit.strip()))
    for pr in PRINCIPLES:
        chk("statement non-empty", bool(pr["statement"].strip()))
        chk("hypothesis non-empty", bool(pr["hypothesis"].strip()))
        chk("kh10 ids list", isinstance(pr.get("kh10_candidate_ids"), list) and pr["kh10_candidate_ids"])
        for f, d in pr["factors"]:
            feats.append(f)
            chk(f"dir±1 {f}", d in (-1, 1))
            chk(f"not rejected token {f}", f not in REJECTED_UNMAPPABLE)
        for note in pr.get("domain_notes") or []:
            chk("note_kind closed", note["note_kind"] in ("verbatim_quote", "human_authored"))
            chk("note no ai_generated", note["source_type"] != "ai_generated")
            chk("note citation", bool(note["citation"].strip()))
    chk("n principles ==3", len(PRINCIPLES) == 3)
    chk("covers kh10 2,3,9,18", set().union(*(pr["kh10_candidate_ids"] for pr in PRINCIPLES)) == {2, 3, 9, 18})
    chk("erp rejected", "erp_dump_any" in REJECTED_UNMAPPABLE)
    chk("rki rejected", "rki_probe_hit_rate" in REJECTED_UNMAPPABLE)
    src = open(__file__, encoding="utf-8").read()
    apply_body = src.split("def apply_seed")[1].split("\ndef main")[0]
    map_loop = apply_body.split('for f, d in pr["factors"]')[1].split("for note in")[0]
    chk("I8 map loop ignores domain_map", "principle_domain_map" not in map_loop)
    chk(
        "I8 notes after maps",
        apply_body.index('for f, d in pr["factors"]') < apply_body.index("for note in"),
    )
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
    n_ledger = 0
    new_maps: list[tuple] = []
    name = SCHOOL["name"]
    pid_by_statement: dict[str, int] = {}

    with db.transaction(conn) as cur:
        cur.execute(
            "SELECT school_id, domain FROM philosophy_school WHERE name=%s",
            (name,),
        )
        row = cur.fetchone()
        if not row:
            if dry_run:
                print(f"  [dry] school ← {name} domain=investment")
                sid = -1
                n_school = 1
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
            for cit, st in SOURCES:
                print(f"  [dry] source ← {cit[:70]}")
                n_src += 1
            for pr in PRINCIPLES:
                print(f"  [dry] principle ← {pr['statement'][:56]}")
                n_pri += 1
                for f, d in pr["factors"]:
                    print(f"  [dry] map ← {f} dir={d:+d}")
                    new_maps.append((name, f, d))
                    n_map += 1
                n_note += len(pr.get("domain_notes") or [])
                for cid in pr["kh10_candidate_ids"]:
                    print(f"  [dry] ledger downstream ← candidate_id={cid}")
                    n_ledger += 1
            return {
                "school": name,
                "school_new": n_school,
                "sources_new": n_src,
                "principles_new": n_pri,
                "maps_new": n_map,
                "domain_notes_new": n_note,
                "ledger_links": n_ledger,
                "new_map_pairs": new_maps,
                "rejected": list(REJECTED_UNMAPPABLE),
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
            kh_ids = list(pr["kh10_candidate_ids"])
            prov = dict(PROVENANCE_BASE)
            prov["kh10_candidate_ids"] = kh_ids
            prov_json = json.dumps(prov, ensure_ascii=False)

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
            if pid > 0:
                pid_by_statement[pr["statement"]] = pid

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
            else:
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
                                "UPDATE principle_domain_map SET note_kind=%s, "
                                "application_note=%s, citation=%s, source_type=%s "
                                "WHERE map_id=%s",
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

            # ledger downstream_ref
            ref = f"principle_id={pid};school={name};kh10={kh_ids}"
            for cid in kh_ids:
                if dry_run or pid < 0:
                    print(f"  [dry] ledger downstream ← candidate_id={cid} → {ref}")
                    n_ledger += 1
                    continue
                cur.execute(
                    """
                    UPDATE knowhow_governance_ledger
                    SET downstream_ref=%s
                    WHERE candidate_id=%s AND decision='approved'
                      AND (downstream_ref IS NULL OR downstream_ref <> %s)
                    """,
                    (ref, cid, ref),
                )
                if cur.rowcount:
                    n_ledger += cur.rowcount
                cur.execute(
                    """
                    UPDATE knowhow_evolution_candidate
                    SET note=COALESCE(note,'') || %s, updated_at=now()
                    WHERE candidate_id=%s
                      AND COALESCE(note,'') NOT LIKE %s
                    """,
                    (f" | PME-SOLAR {ref}", cid, f"%PME-SOLAR principle_id={pid}%"),
                )

    return {
        "school": name,
        "school_new": n_school,
        "sources_new": n_src,
        "principles_new": n_pri,
        "maps_new": n_map,
        "domain_notes_new": n_note,
        "ledger_links": n_ledger,
        "new_map_pairs": new_maps,
        "rejected": list(REJECTED_UNMAPPABLE),
        "dry_run": dry_run,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="PME-XDOM SOLAR KH10 S1 策展")
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
